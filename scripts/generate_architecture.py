"""
Generates architecture.png in the repo root.
Run: python scripts/generate_architecture.py
Requires: pip install matplotlib
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "architecture.png")

BG      = "#04051A"
CARD    = "#0E0E2C"
BORDER  = "#8B5CF6"
CYAN    = "#06B6D4"
PINK    = "#EC4899"
GREEN   = "#34D399"
ORANGE  = "#F97316"
RED     = "#EF4444"
TEXT    = "#E2E8F0"
MUTED   = "#64748B"
YELLOW  = "#EAB308"

fig, ax = plt.subplots(figsize=(18, 11))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis("off")


def box(x, y, w, h, color=BORDER, label="", sublabel="", icon=""):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.08",
                          linewidth=1.5,
                          edgecolor=color,
                          facecolor=CARD)
    ax.add_patch(rect)
    # Top accent bar
    bar = FancyBboxPatch((x, y + h - 0.12), w, 0.12,
                         boxstyle="round,pad=0.02",
                         linewidth=0,
                         edgecolor="none",
                         facecolor=color,
                         alpha=0.7)
    ax.add_patch(bar)
    full_label = f"{icon} {label}".strip() if icon else label
    ax.text(x + w/2, y + h/2 + 0.12, full_label,
            ha="center", va="center", fontsize=9.5, fontweight="bold",
            color=TEXT, fontfamily="monospace")
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22, sublabel,
                ha="center", va="center", fontsize=7.2,
                color=MUTED, fontfamily="monospace")


def arrow(x1, y1, x2, y2, color=MUTED, label="", lw=1.4):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=14))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.14, label, ha="center", va="bottom",
                fontsize=6.8, color=color, fontfamily="monospace")


def section_label(x, y, text, color=MUTED):
    ax.text(x, y, text, ha="left", va="center",
            fontsize=7.5, color=color, fontfamily="monospace",
            style="italic")


# ── Title ──────────────────────────────────────────────────────────────────
ax.text(9, 10.55, "AgentShield for Splunk — Architecture",
        ha="center", va="center", fontsize=16, fontweight="bold",
        color=TEXT, fontfamily="monospace")
ax.text(9, 10.2, "AI Agent Security & Observability Copilot  ·  FastAPI · Streamlit · Splunk HEC · Docker",
        ha="center", va="center", fontsize=8, color=MUTED, fontfamily="monospace")

# ── Row 1: Inputs ───────────────────────────────────────────────────────────
section_label(0.3, 9.55, "INPUTS / SOURCES")
box(0.4, 8.8,  2.4, 0.9, CYAN,   "AI Agent Simulator", "4 event types · 6 LLM models", "🤖")
box(3.2, 8.8,  2.4, 0.9, CYAN,   "Real AI Agents",     "Any LLM-powered app / bot",    "🔗")
box(6.0, 8.8,  2.4, 0.9, CYAN,   "OpenTelemetry",      "GenAI semantic conventions",   "📡")

# ── Row 2: FastAPI Risk Engine ───────────────────────────────────────────────
section_label(0.3, 7.85, "RISK ENGINE  (FastAPI · Port 8000)")
box(0.4, 6.9,  3.8, 1.2, BORDER, "FastAPI Risk Engine", "20+ REST endpoints · /simulate · /incidents", "⚙️")

# V4/V5 sub-engines inside risk engine row
box(4.6, 6.9,  2.5, 1.2, PINK,   "Hallucination Checker", "RAG grounding · score 0–1", "🧠")
box(7.5, 6.9,  2.5, 1.2, ORANGE, "Policy Engine",         "6 rules · block/quarantine/redact", "📜")
box(10.4, 6.9, 2.5, 1.2, YELLOW, "Budget Monitor",        "Token/cost limits · violations", "💰")
box(13.3, 6.9, 2.5, 1.2, GREEN,  "Baseline Engine",       "3-sigma anomaly · 7 metrics", "📈")

# ── Row 3: Splunk HEC ────────────────────────────────────────────────────────
section_label(0.3, 6.05, "SPLUNK  (index=ai_agent_logs)")
box(3.5, 5.1,  4.0, 1.2, RED,    "Splunk HEC",            "HTTP Event Collector · Port 8088", "🔴")
box(8.0, 5.1,  4.0, 1.2, RED,    "SPL Saved Searches",    "9 detections · real-time scheduled", "🔍")
box(12.5, 5.1, 3.8, 1.2, RED,    "JSONL Fallback",        "data/ai_agent_logs.jsonl · no-Splunk mode", "📄")

# ── Row 4: Streamlit Dashboard ───────────────────────────────────────────────
section_label(0.3, 4.25, "DASHBOARD  (Streamlit · Port 8501)")
pages = [
    ("📊", "Observability", BORDER),
    ("📋", "Case Hub",      PINK),
    ("🔍", "Investigate",   CYAN),
    ("🚀", "Simulate",      GREEN),
    ("🧪", "Model Arena",   ORANGE),
    ("💰", "Budget Mon.",   YELLOW),
    ("📜", "Policies",      RED),
    ("📈", "Baselines",     "#A78BFA"),
]
pw = 2.1
for i, (icon, name, col) in enumerate(pages):
    bx = 0.4 + i * (pw + 0.06)
    box(bx, 3.1, pw, 1.1, col, name, "", icon)

# ── Arrows: Simulator → FastAPI ─────────────────────────────────────────────
arrow(1.6,  8.8, 1.6,  8.15, CYAN,  "events")
arrow(4.4,  8.8, 3.0,  8.15, CYAN,  "events")
arrow(7.2,  8.8, 2.5,  8.15, CYAN,  "OTLP")

# ── Arrows: FastAPI → sub-engines ───────────────────────────────────────────
arrow(4.2,  7.5, 5.0,  7.5, PINK)
arrow(4.2,  7.5, 7.8,  7.5, ORANGE)
arrow(4.2,  7.5, 10.7, 7.5, YELLOW)
arrow(4.2,  7.5, 13.6, 7.5, GREEN)

# ── Arrows: FastAPI → Splunk HEC ────────────────────────────────────────────
arrow(2.3,  6.9, 5.5,  6.35, RED,   "HEC POST")
arrow(2.3,  6.9, 14.4, 6.35, MUTED, "JSONL fallback")

# ── Arrows: Splunk HEC → SPL ────────────────────────────────────────────────
arrow(7.5,  5.7, 8.0,  5.7, RED)

# ── Arrows: Splunk / JSONL → Dashboard ─────────────────────────────────────
arrow(5.5,  5.1, 5.5,  4.25, RED,   "query")
arrow(14.4, 5.1, 14.4, 4.25, MUTED, "read")
arrow(8.5,  6.9, 8.5,  4.25, CYAN,  "API calls")

# ── Claude AI box ────────────────────────────────────────────────────────────
box(15.5, 8.0, 2.1, 1.2, "#A78BFA", "Claude API", "AI incident summaries", "✨")
arrow(15.5, 8.6, 4.2, 8.1, "#A78BFA", "LLM summary")

# ── Legend ───────────────────────────────────────────────────────────────────
legend_items = [
    (CYAN,   "Data Ingestion"),
    (BORDER, "Core Engine"),
    (PINK,   "V4: Hallucination"),
    (ORANGE, "V4: Policy-as-Code"),
    (YELLOW, "V5: Budget"),
    (GREEN,  "V5: Baselines"),
    (RED,    "Splunk Layer"),
    ("#A78BFA", "Claude AI"),
]
for i, (c, lbl) in enumerate(legend_items):
    lx = 0.5 + i * 2.2
    ax.add_patch(mpatches.Rectangle((lx, 0.25), 0.3, 0.25, color=c, alpha=0.85))
    ax.text(lx + 0.4, 0.37, lbl, va="center", fontsize=7, color=MUTED, fontfamily="monospace")

plt.tight_layout(pad=0.2)
plt.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"Saved -> {OUT}")
