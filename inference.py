"""
NexDesk Baseline Inference Script
Runs an LLM agent against all NexDesk tasks with retry logic and OpenEnv output format.

Environment variables:
  API_BASE_URL, MODEL_NAME, HF_TOKEN, ENV_BASE_URL, MAX_RETRIES, TIMEOUT
"""

import json
import os
import sys
import textwrap
import time
from typing import Any, Dict, List, Optional, Callable

import requests
from openai import OpenAI, APIError, RateLimitError

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860").rstrip("/")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

BENCHMARK = "nexdesk-ticket-triage"
TEMPERATURE = 0.2
MAX_TOKENS = 512
SUCCESS_THRESHOLD = 0.5
TASKS = ["ticket_classify", "ticket_route", "ticket_resolve", "crisis_surge"]


# OpenEnv mandatory log format
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_display = action[:200] + "..." if len(action) > 200 else action
    print(
        f"[STEP] step={step} action={action_display} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# Retry decorator with exponential backoff
def with_retry(max_retries: int = MAX_RETRIES, backoff: float = 1.0):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, APIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff * (2**attempt)
                        print(
                            f"[DEBUG] Retry {attempt + 1}/{max_retries} after {wait_time}s: {str(e)}",
                            flush=True,
                        )
                        time.sleep(wait_time)
                    else:
                        raise last_exception
            return None

        return wrapper

    return decorator


# Environment API calls
@with_retry(max_retries=MAX_RETRIES)
def env_reset(task: str) -> Dict[str, Any]:
    r = requests.post(f"{ENV_BASE_URL}/reset", json={"task": task}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


@with_retry(max_retries=MAX_RETRIES)
def env_step(session_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
    payload = {"session_id": session_id, **action}
    r = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


@with_retry(max_retries=2)
def env_health_check() -> bool:
    try:
        r = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False


# System prompt for LLM
SYSTEM_BASE = textwrap.dedent("""
    You are an expert IT helpdesk manager. Analyze the support ticket and respond
    with a JSON object containing only the fields specified in the instructions.
    Return ONLY valid JSON. No markdown, no explanation, no preamble.
    
    For the confidence field (0.0-1.0), provide your honest confidence in your answer:
    - 0.9-1.0: Very confident, clear-cut case
    - 0.7-0.9: Confident, but some ambiguity
    - 0.5-0.7: Uncertain, could go either way
    - 0.0-0.5: Low confidence, guessing
""").strip()


def build_prompt(obs: Dict[str, Any], step: int) -> str:
    """Build task-specific prompt from observation."""
    task = obs["task"]
    ticket_block = (
        f"Ticket ID: {obs['ticket_id']}\n"
        f"Subject: {obs['subject']}\n"
        f"Description: {obs['description']}\n"
        f"Submitter: {obs['submitter']} ({obs['department']})\n"
        f"Submitted: {obs['submitted_at']}"
    )

    context_block = ""
    if obs.get("stress_level") is not None:
        context_block += f"\nStress Level: {obs['stress_level']:.2f}"
    if obs.get("sla_deadline_minutes"):
        context_block += f"\nSLA Deadline: {obs['sla_deadline_minutes']} minutes"
    if obs.get("queue_depth"):
        context_block += f"\nQueue Depth: {obs['queue_depth']} tickets"

    similar = obs.get("similar_tickets", [])
    if similar:
        context_block += "\n\nSimilar Past Tickets:"
        for t in similar[:2]:
            context_block += f"\n- {t.get('subject', 'N/A')} -> Team: {t.get('team', 'N/A')}"

    if task == "crisis_surge" and obs.get("batch_info"):
        batch = obs["batch_info"]
        context_block += f"\n\nBatch Progress: {batch.get('current_index', 0) + 1}/{batch.get('total_tickets', 10)}"

    if task == "ticket_classify":
        instructions = textwrap.dedent("""
            Return JSON with exactly these fields:
            {"priority": "<low|medium|high|critical>", "category": "<network|hardware|software|access|security|other>", "confidence": <0.0-1.0>}
        """).strip()

    elif task == "ticket_route":
        if step == 1:
            instructions = textwrap.dedent("""
                Return JSON: {"priority": "<low|medium|high|critical>", "category": "<network|hardware|software|access|security|other>", "team": "<helpdesk|network-ops|sysadmin|security|dev>", "confidence": <0.0-1.0>}
            """).strip()
        else:
            instructions = 'Return JSON: {"affected_system": "<name of affected system>", "confidence": <0.0-1.0>}'

    elif task == "ticket_resolve":
        if step == 1:
            instructions = 'Step 1/3. Return JSON: {"priority": "...", "category": "...", "team": "...", "confidence": <0.0-1.0>}'
        elif step == 2:
            instructions = 'Step 2/3. Return JSON: {"affected_system": "...", "first_response": "<professional response to user>", "confidence": <0.0-1.0>}'
        else:
            instructions = 'Step 3/3. Return JSON: {"resolution_steps": ["step1", "step2", ...], "sla_hours": <integer>, "confidence": <0.0-1.0>}'

    elif task == "crisis_surge":
        instructions = 'CRISIS MODE! Return JSON: {"priority": "...", "category": "...", "team": "...", "confidence": <0.0-1.0>}'

    else:
        instructions = '{"priority": "medium", "category": "other", "confidence": 0.5}'

    return f"{ticket_block}{context_block}\n\n{instructions}"


def get_action(client: OpenAI, obs: Dict[str, Any], step: int) -> Dict[str, Any]:
    """Get action from LLM with retries and fallback."""
    prompt = build_prompt(obs, step)

    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_BASE},
                    {"role": "user", "content": prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            raw = (completion.choices[0].message.content or "{}").strip()

            if raw.startswith("```"):
                parts = raw.split("```")
                if len(parts) >= 2:
                    raw = parts[1]
                    if raw.startswith("json"):
                        raw = raw[4:]

            parsed = json.loads(raw.strip())
            if "priority" not in parsed:
                parsed["priority"] = "medium"
            if "category" not in parsed:
                parsed["category"] = "other"
            if "confidence" not in parsed:
                parsed["confidence"] = 0.5
            return parsed

        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parse error (attempt {attempt + 1}): {e}", flush=True)
            if attempt == MAX_RETRIES - 1:
                return {"priority": "medium", "category": "other", "confidence": 0.5}
            time.sleep(0.5 * (2**attempt))

        except (APIError, RateLimitError) as e:
            print(f"[DEBUG] API error (attempt {attempt + 1}): {e}", flush=True)
            if attempt == MAX_RETRIES - 1:
                return {"priority": "medium", "category": "other", "confidence": 0.5}
            time.sleep(1.0 * (2**attempt))

        except Exception as e:
            print(f"[DEBUG] LLM error at step {step}: {e}", flush=True)
            return {"priority": "medium", "category": "other", "confidence": 0.5}

    return {"priority": "medium", "category": "other", "confidence": 0.5}


def run_task(client: OpenAI, task: str) -> Dict[str, Any]:
    """Run a single task episode."""
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    error_msg = None

    log_start(task=task, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_result = env_reset(task)
        obs = reset_result["observation"]
        session_id = reset_result["session_id"]
        max_steps = obs["max_steps"]
    except Exception as e:
        print(f"[DEBUG] Reset failed for task {task}: {e}", flush=True)
        log_end(success=False, steps=0, score=0.0, rewards=[0.0])
        return {
            "task": task,
            "success": False,
            "score": 0.0,
            "steps": 0,
            "rewards": [0.0],
            "error": str(e),
        }

    for step in range(1, max_steps + 1):
        try:
            action = get_action(client, obs, step)
            action_str = json.dumps(action, separators=(",", ":"))
        except Exception as e:
            print(f"[DEBUG] Action generation failed: {e}", flush=True)
            action = {"priority": "medium", "category": "other", "confidence": 0.5}
            action_str = json.dumps(action)

        try:
            result = env_step(session_id, action)
            obs = result["observation"]
            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            error_msg = None

            info = result.get("info", {})
            if info.get("score_breakdown"):
                print(f"[DEBUG] breakdown: {json.dumps(info['score_breakdown'])}", flush=True)

        except requests.HTTPError as e:
            reward, done = 0.0, True
            error_msg = f"HTTP {e.response.status_code}: {str(e)[:80]}"
            print(f"[DEBUG] HTTP error: {error_msg}", flush=True)

        except requests.RequestException as e:
            reward, done = 0.0, True
            error_msg = f"Request failed: {str(e)[:80]}"
            print(f"[DEBUG] Request error: {error_msg}", flush=True)

        except Exception as e:
            reward, done = 0.0, True
            error_msg = str(e)[:100]
            print(f"[DEBUG] Step error: {error_msg}", flush=True)

        rewards.append(reward)
        steps_taken = step
        log_step(step=step, action=action_str, reward=reward, done=done, error=error_msg)

        if done:
            break

    raw_score = sum(rewards)
    if task == "crisis_surge":
        score = round(min(max(raw_score / 1.2, 0.0), 1.0), 4)
    else:
        score = round(min(max(raw_score, 0.0), 1.0), 4)
    success = score >= SUCCESS_THRESHOLD

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {
        "task": task,
        "success": success,
        "score": score,
        "steps": steps_taken,
        "rewards": rewards,
        "error": error_msg,
    }


def main():
    print("Checking environment health...", flush=True)
    if not env_health_check():
        print(f"ERROR: Environment at {ENV_BASE_URL} is not responding", flush=True)
        print("  Start server: uvicorn server.app:app --host 0.0.0.0 --port 7860", flush=True)
        sys.exit(1)
    print("Environment is healthy!\n", flush=True)

    if not HF_TOKEN:
        print("WARNING: HF_TOKEN not set. LLM calls may fail.\n", flush=True)

    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}", flush=True)
        sys.exit(1)

    results = []
    for task in TASKS:
        result = run_task(client, task)
        results.append(result)
        print("", flush=True)

    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    total_score = sum(r["score"] for r in results)
    avg_score = total_score / len(results) if results else 0
    successes = sum(1 for r in results if r["success"])
    errors = sum(1 for r in results if r.get("error"))

    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        error_note = f" [ERROR: {r.get('error', 'N/A')[:30]}...]" if r.get("error") else ""
        print(f"  {r['task']}: {r['score']:.2f} [{status}]{error_note}")

    print(f"\nTotal: {total_score:.2f} / {len(results):.0f}")
    print(f"Average: {avg_score:.2f}")
    print(f"Success rate: {successes}/{len(results)}")
    if errors > 0:
        print(f"Errors: {errors}/{len(results)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
