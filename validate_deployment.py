"""
NexDesk Deployment Validation Script - validates environment is ready for HuggingFace deployment.
Run before submitting: python validate_deployment.py
"""

import ast
import os
import subprocess
import sys
import time
from pathlib import Path

REQUIRED_FILES = [
    "Dockerfile",
    "pyproject.toml",
    "requirements.txt",
    "openenv.yaml",
    "README.md",
    "inference.py",
    "models.py",
    "client.py",
    "server/__init__.py",
    "server/app.py",
    "server/environment.py",
    "server/graders.py",
    "server/metrics.py",
    "server/tickets.py",
]

PYTHON_FILES = [
    "inference.py",
    "models.py",
    "client.py",
    "server/__init__.py",
    "server/app.py",
    "server/environment.py",
    "server/graders.py",
    "server/metrics.py",
    "server/tickets.py",
]

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")


def print_success(text: str):
    print(f"{GREEN}[OK]{RESET} {text}")


def print_error(text: str):
    print(f"{RED}[FAIL]{RESET} {text}")


def print_warning(text: str):
    print(f"{YELLOW}[WARN]{RESET} {text}")


def run_command(cmd: list, cwd: str = ".", timeout: int = 60) -> tuple:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def check_required_files() -> bool:
    """Check that all required files exist."""
    print_header("Checking Required Files")

    all_exist = True
    for file_path in REQUIRED_FILES:
        if Path(file_path).exists():
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_exist = False

    return all_exist


def check_python_syntax() -> bool:
    """Check that all Python files have valid syntax."""
    print_header("Checking Python Syntax")

    all_valid = True
    for file_path in PYTHON_FILES:
        if not Path(file_path).exists():
            print_warning(f"Skipping (not found): {file_path}")
            continue

        try:
            with open(file_path, "r") as f:
                source = f.read()
            ast.parse(source)
            print_success(f"Valid syntax: {file_path}")
        except SyntaxError as e:
            print_error(f"Syntax error in {file_path}: {e}")
            all_valid = False
        except Exception as e:
            print_error(f"Error checking {file_path}: {e}")
            all_valid = False

    return all_valid


def check_imports() -> bool:
    """Check that key imports work."""
    print_header("Checking Imports")

    imports_to_check = [
        ("fastapi", "FastAPI"),
        ("pydantic", "BaseModel"),
        ("requests", None),
        ("openai", "OpenAI"),
    ]

    all_valid = True
    for module, attr in imports_to_check:
        try:
            mod = __import__(module)
            if attr and not hasattr(mod, attr):
                print_error(f"Module {module} missing attribute {attr}")
                all_valid = False
            else:
                print_success(f"Import OK: {module}" + (f".{attr}" if attr else ""))
        except ImportError as e:
            print_error(f"Cannot import {module}: {e}")
            all_valid = False

    return all_valid


def check_docker_build() -> bool:
    """Check that Docker image builds successfully."""
    print_header("Checking Docker Build")

    if not Path("Dockerfile").exists():
        print_error("Dockerfile not found")
        return False

    print("Building Docker image (this may take a few minutes)...")
    success, stdout, stderr = run_command(
        ["docker", "build", "-t", "nexdesk-test", "."], timeout=300
    )

    if success:
        print_success("Docker build successful")
        return True
    else:
        print_error("Docker build failed")
        print(f"\nStdout:\n{stdout}")
        print(f"\nStderr:\n{stderr}")
        return False


def check_server_start() -> bool:
    """Check that server starts and responds to health check."""
    print_header("Checking Server Startup")

    # Start server in background
    print("Starting server...")
    try:
        proc = subprocess.Popen(
            ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        time.sleep(3)

        # Check health endpoint
        import requests

        try:
            response = requests.get("http://localhost:7860/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print_success("Server started and health check passed")
                    return True
                else:
                    print_error(f"Health check returned unexpected status: {data}")
                    return False
            else:
                print_error(f"Health check returned status {response.status_code}")
                return False
        except requests.RequestException as e:
            print_error(f"Health check request failed: {e}")
            return False
        finally:
            proc.terminate()
            proc.wait(timeout=5)

    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return False


def check_reset_endpoint() -> bool:
    """Check that /reset endpoint works."""
    print_header("Checking /reset Endpoint")

    import requests

    try:
        response = requests.post(
            "http://localhost:7860/reset", json={"task": "ticket_classify"}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "observation" in data and "session_id" in data:
                print_success("/reset endpoint working")
                return True
            else:
                print_error("/reset response missing required fields")
                return False
        else:
            print_error(f"/reset returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"/reset request failed: {e}")
        return False


def check_step_endpoint() -> bool:
    """Check that /step endpoint works."""
    print_header("Checking /step Endpoint")

    import requests

    # First get a session
    try:
        reset_response = requests.post(
            "http://localhost:7860/reset", json={"task": "ticket_classify"}, timeout=10
        )
        session_id = reset_response.json()["session_id"]

        # Now take a step
        step_response = requests.post(
            "http://localhost:7860/step",
            json={
                "session_id": session_id,
                "priority": "high",
                "category": "network",
                "confidence": 0.8,
            },
            timeout=10,
        )

        if step_response.status_code == 200:
            data = step_response.json()
            if all(k in data for k in ["observation", "reward", "done", "info"]):
                print_success("/step endpoint working")
                return True
            else:
                print_error("/step response missing required fields")
                return False
        else:
            print_error(f"/step returned status {step_response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"/step request failed: {e}")
        return False


def check_openenv_yaml() -> bool:
    """Check that openenv.yaml is valid."""
    print_header("Checking openenv.yaml")

    try:
        import yaml

        with open("openenv.yaml", "r") as f:
            data = yaml.safe_load(f)

        required_keys = ["name", "version", "description", "tasks"]
        for key in required_keys:
            if key not in data:
                print_error(f"openenv.yaml missing required key: {key}")
                return False

        # Check tasks
        tasks = data.get("tasks", [])
        if len(tasks) < 3:
            print_error(f"Need at least 3 tasks, found {len(tasks)}")
            return False

        print_success("openenv.yaml is valid")
        return True
    except ImportError:
        print_warning("PyYAML not installed, skipping YAML validation")
        return True
    except Exception as e:
        print_error(f"Error validating openenv.yaml: {e}")
        return False


def check_graders() -> bool:
    """Check that graders return valid scores."""
    print_header("Checking Graders")

    try:
        from server.graders import grade_classify

        # Test with sample data
        test_action = {"priority": "high", "category": "network"}
        test_ticket = {
            "gt_priority": "high",
            "gt_priority_ok": [],
            "gt_category": "network",
            "gt_category_ok": [],
        }

        score = grade_classify(test_action, test_ticket)

        if 0.0 <= score <= 1.0:
            print_success(f"Grader returns valid score: {score}")
            return True
        else:
            print_error(f"Grader returned invalid score: {score}")
            return False
    except Exception as e:
        print_error(f"Error testing graders: {e}")
        return False


def main():
    """Run all validation checks."""
    print(f"{BLUE}NexDesk Deployment Validation{RESET}")
    print(f"{BLUE}============================={RESET}\n")

    results = {}

    # Run checks
    results["files"] = check_required_files()
    results["syntax"] = check_python_syntax()
    results["imports"] = check_imports()
    results["yaml"] = check_openenv_yaml()
    results["graders"] = check_graders()

    # Docker and server checks (optional, may not work in all environments)
    if (
        os.path.exists("/var/run/docker.sock")
        or subprocess.run(["which", "docker"], capture_output=True).returncode == 0
    ):
        results["docker"] = check_docker_build()
        # Only check server if Docker build succeeded
        if results.get("docker"):
            results["server"] = check_server_start()
            if results.get("server"):
                results["reset"] = check_reset_endpoint()
                results["step"] = check_step_endpoint()
    else:
        print_warning("Docker not available, skipping container checks")

    # Summary
    print_header("Validation Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {check:15} {status}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print(f"\n{GREEN}All checks passed! Ready for deployment.{RESET}")
        return 0
    else:
        print(f"\n{RED}Some checks failed. Please fix the issues above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
