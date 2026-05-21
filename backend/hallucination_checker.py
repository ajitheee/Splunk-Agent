import random

# Simulated context documents — in production these come from a RAG retrieval step
_CONTEXT_DOCS = [
    "Order #12345 status: processing, estimated delivery tomorrow.",
    "Refund policy: 30-day return window for all products.",
    "Customer support hours: 9am-5pm EST, Monday to Friday.",
    "VIP customers receive priority queue routing.",
    "Payment methods accepted: Visa, Mastercard, PayPal.",
]

_GROUNDED_KEYWORDS = ["order", "status", "refund", "support", "shipping", "policy", "delivery", "return"]
_RISKY_KEYWORDS = ["export", "secret", "token", "password", "bypass", "ignore", "override", "credentials", "dump"]
_INJECTION_PHRASES = ["ignore previous", "reveal", "bypass policy", "export all", "developer mode", "override instructions"]


def check_hallucination(prompt: str, response: str, quality_score: float, injection_score: int) -> dict:
    """
    Simulated context-grounded hallucination check.

    Produces a hallucination_score (0–1), grounding status, and risk tier.
    High injection score or low quality correlates with higher hallucination risk.
    """
    response_lower = (response or "").lower()
    prompt_lower = (prompt or "").lower()

    has_grounded = any(kw in response_lower for kw in _GROUNDED_KEYWORDS)
    has_risky = any(kw in response_lower for kw in _RISKY_KEYWORDS)
    has_injection = any(phrase in prompt_lower for phrase in _INJECTION_PHRASES)

    # Base score inverts quality — poor quality signals likely hallucination
    score = round(1.0 - max(0.0, min(1.0, quality_score)), 3)

    if has_injection:
        score = min(1.0, score + 0.35)
    if has_risky:
        score = min(1.0, score + 0.20)
    if has_grounded:
        score = max(0.0, score - 0.15)
    if injection_score and injection_score >= 70:
        score = min(1.0, score + 0.10)

    # Small noise for realism
    score = round(min(1.0, max(0.0, score + random.uniform(-0.04, 0.04))), 3)

    context_grounded = has_grounded and not has_injection and quality_score >= 0.6

    if score >= 0.7:
        risk = "high"
    elif score >= 0.4:
        risk = "medium"
    else:
        risk = "low"

    return {
        "hallucination_score": score,
        "context_grounded": context_grounded,
        "context_docs_checked": len(_CONTEXT_DOCS),
        "hallucination_risk": risk,
    }
