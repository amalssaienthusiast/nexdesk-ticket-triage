import json
from server.environment import NexDeskEnv

def extract_floats(obj, path=""):
    floats = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            floats.extend(extract_floats(v, path=f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            floats.extend(extract_floats(v, path=f"{path}[{i}]"))
    elif isinstance(obj, float):
        floats.append((path, obj))
    return floats

actions_to_test = [
    {
        "priority": "critical",
        "category": "network",
        "team": "network-ops",
        "affected_system": "vpn",
        "first_response": "We are looking into the VPN issue right now.",
        "resolution_steps": ["Restarted VPN server", "Fixed it"],
        "sla_hours": 1,
        "confidence": 1.0
    },
    {
        "priority": "low",
        "category": "software",
        "team": "dev",
        "affected_system": "nothing",
        "first_response": "bad",
        "resolution_steps": [],
        "sla_hours": 999,
        "confidence": 0.0
    },
    {}
]

tasks = ["ticket_classify", "ticket_route", "ticket_resolve", "crisis_surge"]
env = NexDeskEnv()

failures = []

for task in tasks:
    for action_idx, action in enumerate(actions_to_test):
        res = env.reset(task)
        session_id = res["session_id"]
        obs = res["observation"]
        
        all_floats = extract_floats(res, path="RESET")
        for path, val in all_floats:
            if not (0.0 < val < 1.0):
                failures.append(f"{task} Action={action_idx} {path}: {val}")
                
        for step in range(1, obs["max_steps"] + 1):
            step_res = env.step(session_id, action)
            
            all_floats = extract_floats(step_res, path=f"STEP_{step}")
            for path, val in all_floats:
                if not (0.0 < val < 1.0):
                    failures.append(f"{task} Action={action_idx} {path}: {val}")

if not failures:
    print("SUCCESS: 100% of generated floats are strictly between 0 and 1.")
else:
    print("FAILURES FOUND:")
    for f in failures:
        print(f)
