import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(__file__)
BUDGET_CONFIG_FILE = os.path.join(_BASE, "..", "data", "budget_config.json")
BUDGET_STATE_FILE = os.path.join(_BASE, "..", "data", "budget_state.json")

DEFAULT_CONFIG = {
    "budgets": {
        "per_session_token_limit": 5000,
        "per_session_cost_limit_usd": 1.00,
        "daily_cost_limit_usd": 50.00,
        "daily_token_limit": 500000,
        "alert_threshold_pct": 80
    },
    "actions": {
        "on_session_exceed": "block_session",
        "on_daily_exceed": "alert_and_throttle"
    }
}


def _today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_budget_config() -> dict:
    if os.path.exists(BUDGET_CONFIG_FILE):
        try:
            with open(BUDGET_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG


def save_budget_config(config: dict):
    os.makedirs(os.path.dirname(BUDGET_CONFIG_FILE), exist_ok=True)
    with open(BUDGET_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _load_state() -> dict:
    if os.path.exists(BUDGET_STATE_FILE):
        try:
            with open(BUDGET_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": {}, "daily": {"date": _today_str(), "tokens": 0, "cost_usd": 0.0}}


def _save_state(state: dict):
    os.makedirs(os.path.dirname(BUDGET_STATE_FILE), exist_ok=True)
    with open(BUDGET_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_and_update_budget(event: dict) -> dict:
    """
    Accumulate token/cost usage for a session and globally for today.
    Returns a dict with any budget violations and current usage totals.
    """
    config = load_budget_config()
    state = _load_state()
    budgets = config.get("budgets", DEFAULT_CONFIG["budgets"])
    actions = config.get("actions", DEFAULT_CONFIG["actions"])

    session_id = event.get("session_id", "unknown")
    tokens_used = (event.get("tokens_prompt") or 0) + (event.get("tokens_completion") or 0)
    cost_usd = event.get("estimated_cost_usd") or 0.0

    # Per-session accumulation
    if session_id not in state["sessions"]:
        state["sessions"][session_id] = {"tokens": 0, "cost_usd": 0.0}
    state["sessions"][session_id]["tokens"] += tokens_used
    state["sessions"][session_id]["cost_usd"] = round(
        state["sessions"][session_id]["cost_usd"] + cost_usd, 6
    )

    # Daily accumulation — reset if date rolled over
    if state["daily"].get("date") != _today_str():
        state["daily"] = {"date": _today_str(), "tokens": 0, "cost_usd": 0.0}
    state["daily"]["tokens"] += tokens_used
    state["daily"]["cost_usd"] = round(state["daily"]["cost_usd"] + cost_usd, 6)

    violations = []
    sess = state["sessions"][session_id]
    token_limit = budgets["per_session_token_limit"]
    cost_limit = budgets["per_session_cost_limit_usd"]
    alert_pct = budgets["alert_threshold_pct"] / 100

    if sess["tokens"] > token_limit:
        violations.append({
            "type": "session_token_exceeded",
            "value": sess["tokens"],
            "limit": token_limit,
            "action": actions.get("on_session_exceed", "block_session"),
            "severity": "critical"
        })
    elif sess["tokens"] > token_limit * alert_pct:
        violations.append({
            "type": "session_token_warning",
            "value": sess["tokens"],
            "limit": token_limit,
            "action": "alert",
            "severity": "medium"
        })

    if sess["cost_usd"] > cost_limit:
        violations.append({
            "type": "session_cost_exceeded",
            "value": round(sess["cost_usd"], 4),
            "limit": cost_limit,
            "action": "block_session",
            "severity": "high"
        })

    daily_token_limit = budgets["daily_token_limit"]
    daily_cost_limit = budgets["daily_cost_limit_usd"]

    if state["daily"]["tokens"] > daily_token_limit:
        violations.append({
            "type": "daily_token_exceeded",
            "value": state["daily"]["tokens"],
            "limit": daily_token_limit,
            "action": actions.get("on_daily_exceed", "alert_and_throttle"),
            "severity": "high"
        })

    if state["daily"]["cost_usd"] > daily_cost_limit:
        violations.append({
            "type": "daily_cost_exceeded",
            "value": round(state["daily"]["cost_usd"], 4),
            "limit": daily_cost_limit,
            "action": "alert_and_throttle",
            "severity": "high"
        })

    _save_state(state)

    return {
        "violations": violations,
        "session_tokens": sess["tokens"],
        "session_cost_usd": round(sess["cost_usd"], 4),
        "daily_tokens": state["daily"]["tokens"],
        "daily_cost_usd": round(state["daily"]["cost_usd"], 4)
    }


def get_budget_summary() -> dict:
    config = load_budget_config()
    state = _load_state()
    budgets = config.get("budgets", DEFAULT_CONFIG["budgets"])

    if state["daily"].get("date") != _today_str():
        state["daily"] = {"date": _today_str(), "tokens": 0, "cost_usd": 0.0}

    daily_tokens = state["daily"]["tokens"]
    daily_cost = state["daily"]["cost_usd"]
    daily_token_limit = max(budgets["daily_token_limit"], 1)
    daily_cost_limit = max(budgets["daily_cost_limit_usd"], 0.01)

    return {
        "config": budgets,
        "daily": state["daily"],
        "sessions_tracked": len(state["sessions"]),
        "daily_token_pct": round(daily_tokens / daily_token_limit * 100, 1),
        "daily_cost_pct": round(daily_cost / daily_cost_limit * 100, 1),
        "session_details": [
            {
                "session_id": sid,
                "tokens": data["tokens"],
                "cost_usd": round(data["cost_usd"], 4),
                "token_pct": round(data["tokens"] / max(budgets["per_session_token_limit"], 1) * 100, 1)
            }
            for sid, data in list(state["sessions"].items())[-20:]
        ]
    }


def reset_budget_state():
    state = {"sessions": {}, "daily": {"date": _today_str(), "tokens": 0, "cost_usd": 0.0}}
    _save_state(state)
    return {"status": "reset"}
