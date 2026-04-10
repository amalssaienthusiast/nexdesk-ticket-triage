"""
Exhaustively check every float in every API response the Hackathon validator could hit.
Covers: /reset, /step (all tasks, all steps), /metrics, /state
"""
import json
import sys
sys.path.insert(0, '.')

from server.environment import NexDeskEnv
from server.metrics import BusinessMetrics

FAILURES = []

def check_floats(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_floats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_floats(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        if obj <= 0.0 or obj >= 1.0:
            FAILURES.append(f"OUT OF RANGE  {path} = {obj}")

env = NexDeskEnv()

tasks = ["ticket_classify", "ticket_route", "ticket_resolve", "crisis_surge"]

perfect_actions = {
    "ticket_classify": [{"priority":"low","category":"software","confidence":0.9}],
    "ticket_route": [
        {"priority":"high","category":"network","team":"network-ops","confidence":0.9},
        {"affected_system":"vpn","confidence":0.9},
    ],
    "ticket_resolve": [
        {"priority":"critical","category":"security","team":"security","confidence":0.9},
        {"affected_system":"email","first_response":"We are urgently looking into your security issue and have escalated it immediately.","confidence":0.9},
        {"resolution_steps":["Block the IP","Reset passwords","Enable MFA","Audit logs"],"sla_hours":1,"confidence":0.9},
    ],
    "crisis_surge": [{"priority":"critical","category":"network","team":"network-ops","confidence":0.9}]*10,
}

wrong_actions = {
    "ticket_classify": [{"priority":"low","category":"hardware","confidence":0.1}],
    "ticket_route": [
        {"priority":"low","category":"hardware","team":"helpdesk","confidence":0.1},
        {"affected_system":"keyboard","confidence":0.1},
    ],
    "ticket_resolve": [
        {"priority":"low","category":"hardware","team":"helpdesk","confidence":0.1},
        {"affected_system":"keyboard","first_response":"ok","confidence":0.1},
        {"resolution_steps":[],"sla_hours":999,"confidence":0.1},
    ],
    "crisis_surge": [{"priority":"low","category":"hardware","team":"helpdesk","confidence":0.1}]*10,
}

empty_actions = {t: [{}]*10 for t in tasks}

for label, action_sets in [("PERFECT", perfect_actions), ("WRONG", wrong_actions), ("EMPTY", empty_actions)]:
    for task in tasks:
        res = env.reset(task)
        check_floats(res, f"[{label}][{task}] RESET")
        session_id = res["session_id"]
        obs = res["observation"]
        max_steps = obs["max_steps"]
        actions = action_sets[task]
        for step in range(max_steps):
            action = actions[step] if step < len(actions) else {}
            step_res = env.step(session_id, action)
            check_floats(step_res, f"[{label}][{task}] STEP_{step+1}")
            if step_res.get("done"):
                break

# Check metrics with no episodes
m = BusinessMetrics()
summary = m.get_summary()
check_floats(summary, "[METRICS] empty")

# Record a perfect episode and check
m.record_episode("ticket_classify", total_reward=0.99, tickets_resolved=1, sla_breaches=0, confidence_calibration=0.99)
summary2 = m.get_summary()
check_floats(summary2, "[METRICS] perfect_episode")

# Record a zero episode 
m2 = BusinessMetrics()
m2.record_episode("ticket_classify", total_reward=0.01, tickets_resolved=1, sla_breaches=10, confidence_calibration=0.01)
summary3 = m2.get_summary()
check_floats(summary3, "[METRICS] bad_episode")

# Check state endpoint (env._sessions structure)
# Check /state for all sessions
for session in list(env._sessions.keys()):
    state = env.state(session_id=session)
    check_floats(state, f"[STATE] {session}")

print()
if not FAILURES:
    print("✅ ALL CLEAR: Zero floats at 0.0 or 1.0 across all endpoints.")
else:
    print(f"❌ {len(FAILURES)} FAILURES FOUND:")
    for f in FAILURES:
        print(f"  {f}")
