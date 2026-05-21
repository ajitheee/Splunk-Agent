import json
import math
import os
import logging

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(__file__)
FALLBACK_LOG_FILE = os.getenv("FALLBACK_LOG_FILE", os.path.join(_BASE, "..", "data", "ai_agent_logs.jsonl"))

BASELINE_METRICS = [
    "latency_ms",
    "tokens_prompt",
    "tokens_completion",
    "risk_score",
    "injection_score",
    "estimated_cost_usd",
    "hallucination_score",
]


def _load_events(log_file: str = None) -> list:
    path = log_file or FALLBACK_LOG_FILE
    events = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
    # Only transaction events (have a prompt field)
    return [e for e in events if e.get("prompt")]


def compute_baselines(agent_name: str = None) -> dict:
    """
    Compute per-metric mean, stdev, and 3-sigma upper threshold.
    Requires at least 5 events; returns {} if insufficient data.
    """
    events = _load_events()
    if agent_name:
        events = [e for e in events if e.get("agent_name") == agent_name]

    if len(events) < 5:
        return {}

    baselines = {}
    for metric in BASELINE_METRICS:
        values = [e[metric] for e in events if e.get(metric) is not None]
        if len(values) < 3:
            continue
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stdev = math.sqrt(variance)
        baselines[metric] = {
            "mean": round(mean, 4),
            "stdev": round(stdev, 4),
            "threshold_3sigma": round(mean + 3 * stdev, 4),
            "sample_count": len(values),
        }
    return baselines


def check_anomalies(event: dict, baselines: dict = None) -> list:
    """
    Compare event metrics against precomputed 3-sigma baselines.
    Returns a list of anomaly dicts for any metric exceeding the threshold.
    """
    if baselines is None:
        baselines = compute_baselines(event.get("agent_name"))

    anomalies = []
    for metric in BASELINE_METRICS:
        value = event.get(metric)
        if value is None or metric not in baselines:
            continue

        b = baselines[metric]
        mean, stdev = b["mean"], b["stdev"]
        if stdev == 0:
            continue

        z_score = (value - mean) / stdev
        if abs(z_score) > 3:
            anomalies.append({
                "metric": metric,
                "value": value,
                "mean": mean,
                "stdev": round(stdev, 4),
                "z_score": round(z_score, 2),
                "direction": "high" if z_score > 0 else "low",
                "severity": "critical" if abs(z_score) > 5 else "high",
            })

    return anomalies


def get_baseline_report() -> dict:
    """Full report: computed baselines + anomalies in the most recent 20 events."""
    baselines = compute_baselines()
    events = _load_events()

    recent_anomalies = []
    for event in events[-20:]:
        anomalies = check_anomalies(event, baselines)
        if anomalies:
            recent_anomalies.append({
                "session_id": event.get("session_id"),
                "timestamp": event.get("timestamp"),
                "agent_name": event.get("agent_name"),
                "anomalies": anomalies,
            })

    return {
        "baselines": baselines,
        "total_events_analyzed": len(events),
        "recent_anomalies": recent_anomalies[-10:],
        "anomaly_count": len(recent_anomalies),
    }
