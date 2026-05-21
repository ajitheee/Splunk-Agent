"""
Seed script — generates pre-built sample events into data/ai_agent_logs.jsonl
so the dashboard has data on first load without needing live simulation.

Usage:  python scripts/seed_data.py
"""

import json
import os
import random
import datetime
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_app.simulator import (
    generate_normal_event,
    generate_attack_event,
    generate_hallucination_event,
    generate_cost_spike_event,
    MODEL_PROFILES,
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "ai_agent_logs.jsonl")

AGENTS = [
    "support-refund-agent",
    "billing-query-agent",
    "inventory-lookup-agent",
    "onboarding-agent",
]

MODELS = list(MODEL_PROFILES.keys())


def backdate(hours_ago: float) -> str:
    dt = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_ago)
    return dt.isoformat() + "Z"


def seed():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    events = []

    # ── 60 normal events spread over last 24 h, all 4 agents, all 6 models ──
    for i in range(60):
        ev = generate_normal_event(model=MODELS[i % len(MODELS)])
        ev["agent_name"] = AGENTS[i % len(AGENTS)]
        ev["timestamp"] = backdate(random.uniform(0.5, 24))
        ev["session_id"] = f"sess_{8000 + i}"
        ev["user_id"] = f"user_{100 + i}"
        events.append(ev)

    # ── 10 attack events (critical) ──
    for i in range(10):
        ev = generate_attack_event()
        ev["agent_name"] = random.choice(AGENTS)
        ev["timestamp"] = backdate(random.uniform(1, 20))
        ev["session_id"] = f"sess_{9000 + i}"
        events.append(ev)

    # ── 8 hallucination events (medium/high) ──
    for i in range(8):
        ev = generate_hallucination_event()
        ev["agent_name"] = random.choice(AGENTS)
        ev["timestamp"] = backdate(random.uniform(0.5, 18))
        ev["session_id"] = f"sess_{9100 + i}"
        events.append(ev)

    # ── 4 cost-spike events ──
    for i in range(4):
        ev = generate_cost_spike_event()
        ev["agent_name"] = random.choice(AGENTS)
        ev["timestamp"] = backdate(random.uniform(2, 12))
        ev["session_id"] = f"sess_{9200 + i}"
        events.append(ev)

    # Shuffle so timeline looks natural
    events.sort(key=lambda e: e["timestamp"])

    # Write (append if file exists so live data is preserved)
    existing_ids = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            for line in f:
                try:
                    existing_ids.add(json.loads(line)["session_id"])
                except Exception:
                    pass

    new_count = 0
    with open(OUTPUT_FILE, "a") as f:
        for ev in events:
            if ev["session_id"] not in existing_ids:
                f.write(json.dumps(ev) + "\n")
                new_count += 1

    print(f"Seeded {new_count} new events → {OUTPUT_FILE}")
    print(f"  Normal: 60 | Attack: 10 | Hallucination: 8 | Cost-spike: 4")


if __name__ == "__main__":
    seed()
