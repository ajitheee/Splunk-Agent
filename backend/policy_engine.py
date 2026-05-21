import json
import os
import logging

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(__file__)
POLICIES_FILE = os.path.join(_BASE, "..", "data", "policies.json")

DEFAULT_POLICIES = {
    "version": "1.0",
    "policies": [
        {
            "id": "pol_001",
            "name": "Block CRM Bulk Export",
            "description": "Block any tool call to CRM bulk-export endpoint.",
            "enabled": True,
            "conditions": {"tool_requested": ["crm.export_all_customers", "crm.export_users"]},
            "action": "block",
            "severity_override": "critical"
        },
        {
            "id": "pol_002",
            "name": "High Injection Score Quarantine",
            "description": "Quarantine sessions where injection score >= 80.",
            "enabled": True,
            "conditions": {"injection_score_min": 80},
            "action": "quarantine",
            "severity_override": "high"
        },
        {
            "id": "pol_003",
            "name": "PII + Secret Leakage Redact",
            "description": "Redact and alert when both PII and secrets are detected.",
            "enabled": True,
            "conditions": {"pii_detected": True, "secret_detected": True},
            "action": "redact_alert",
            "severity_override": "high"
        },
        {
            "id": "pol_004",
            "name": "Hallucination Risk Threshold",
            "description": "Flag responses with hallucination score >= 0.7.",
            "enabled": True,
            "conditions": {"hallucination_score_min": 0.7},
            "action": "flag",
            "severity_override": "medium"
        },
        {
            "id": "pol_005",
            "name": "Low Quality Score Alert",
            "description": "Alert when response quality score drops below 0.4.",
            "enabled": True,
            "conditions": {"quality_score_max": 0.4},
            "action": "alert",
            "severity_override": "medium"
        },
        {
            "id": "pol_006",
            "name": "Dangerous Tool Read Secrets",
            "description": "Block attempts to read secrets or credentials.",
            "enabled": True,
            "conditions": {"tool_requested": ["read_secrets", "get_credentials", "dump_env"]},
            "action": "block",
            "severity_override": "critical"
        }
    ]
}


def _ensure_policies_file():
    if not os.path.exists(POLICIES_FILE):
        os.makedirs(os.path.dirname(POLICIES_FILE), exist_ok=True)
        with open(POLICIES_FILE, "w") as f:
            json.dump(DEFAULT_POLICIES, f, indent=2)


def load_policies() -> list:
    _ensure_policies_file()
    try:
        with open(POLICIES_FILE, "r") as f:
            data = json.load(f)
        return data.get("policies", [])
    except Exception as e:
        logger.error(f"Failed to load policies: {e}")
        return DEFAULT_POLICIES["policies"]


def save_policies(policies: list):
    _ensure_policies_file()
    try:
        with open(POLICIES_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {"version": "1.0"}
    data["policies"] = policies
    with open(POLICIES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def evaluate_event(event: dict) -> list:
    """Evaluate event against all enabled policies. Returns list of triggered policy results."""
    policies = load_policies()
    triggered = []

    for policy in policies:
        if not policy.get("enabled", True):
            continue

        conditions = policy.get("conditions", {})
        matched = True

        # tool_requested: list match
        if "tool_requested" in conditions:
            if event.get("tool_requested") not in conditions["tool_requested"]:
                matched = False

        # injection_score_min
        if matched and "injection_score_min" in conditions:
            if (event.get("injection_score") or 0) < conditions["injection_score_min"]:
                matched = False

        # pii_detected
        if matched and "pii_detected" in conditions:
            if bool(event.get("pii_detected")) != bool(conditions["pii_detected"]):
                matched = False

        # secret_detected
        if matched and "secret_detected" in conditions:
            if bool(event.get("secret_detected")) != bool(conditions["secret_detected"]):
                matched = False

        # hallucination_score_min
        if matched and "hallucination_score_min" in conditions:
            if (event.get("hallucination_score") or 0) < conditions["hallucination_score_min"]:
                matched = False

        # quality_score_max
        if matched and "quality_score_max" in conditions:
            if (event.get("quality_score") or 1.0) > conditions["quality_score_max"]:
                matched = False

        if matched:
            triggered.append({
                "policy_id": policy["id"],
                "policy_name": policy["name"],
                "action": policy["action"],
                "severity_override": policy.get("severity_override", "medium")
            })

    return triggered
