import streamlit as st
import requests
import pandas as pd
import json
import os
import time
import datetime
import plotly.graph_objects as go

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AgentShield for Splunk",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
#  MOTION DESIGN SYSTEM - Animated, vibrant cyber-security command center UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Space+Grotesk:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* ── KEYFRAME ANIMATIONS ── */
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(0,229,255,0.5); }
  70%  { box-shadow: 0 0 0 12px rgba(0,229,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(0,229,255,0); }
}
@keyframes glow-red {
  0%, 100% { box-shadow: 0 0 8px rgba(255,107,53,0.5); }
  50%       { box-shadow: 0 0 24px rgba(255,107,53,0.9), 0 0 48px rgba(255,107,53,0.3); }
}
@keyframes slide-in-left {
  from { opacity: 0; transform: translateX(-24px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes slide-in-up {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-6px); }
}
@keyframes flow-packet {
  0%   { left: -2%; opacity: 0; }
  5%   { opacity: 1; }
  95%  { opacity: 1; }
  100% { left: 102%; opacity: 0; }
}
@keyframes flow-packet-blocked {
  0%   { left: -2%; opacity: 0; transform: scale(1); }
  5%   { opacity: 1; }
  48%  { left: 52%; transform: scale(1); }
  55%  { left: 54%; transform: scale(2.5); opacity: 0.9; }
  60%  { left: 55%; transform: scale(0); opacity: 0; }
  100% { left: 55%; opacity: 0; }
}
@keyframes node-ping {
  0%,100% { box-shadow: 0 0 0 0 rgba(0,229,255,0.4); }
  50%      { box-shadow: 0 0 0 10px rgba(0,229,255,0); }
}
@keyframes node-alert {
  0%,100% { box-shadow: 0 0 0 0 rgba(255,107,53,0.6); }
  50%      { box-shadow: 0 0 0 14px rgba(255,107,53,0); }
}
@keyframes scan-line {
  0%   { top: 0; opacity: 0.4; }
  100% { top: 100%; opacity: 0; }
}

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
.main, [data-testid="stApp"], section.main {
    font-family: 'Inter', sans-serif !important;
    background: #0D1117 !important;
    color: #E2E8F0 !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Subtle dot-grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(rgba(0,229,255,0.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #161B22 100%) !important;
    border-right: 1px solid rgba(0,229,255,0.12) !important;
}

[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00E5FF, #7C3AED, #FF6B35);
}

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #F1F5F9 !important;
}

/* ── CARDS ── */
.shield-card {
    background: linear-gradient(135deg, rgba(22,27,46,0.9) 0%, rgba(13,17,23,0.97) 100%);
    border: 1px solid rgba(0,229,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(20px);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    animation: slide-in-up 0.5s ease forwards;
    position: relative;
    overflow: hidden;
}

.shield-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.4), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

.shield-card:hover::before { opacity: 1; }

.shield-card:hover {
    transform: translateY(-5px);
    border-color: rgba(0,229,255,0.3);
    box-shadow: 0 20px 40px -15px rgba(0,229,255,0.15), 0 0 0 1px rgba(0,229,255,0.08);
}

/* ── METRIC CARDS ── */
.metric-card {
    background: linear-gradient(135deg, rgba(22,27,46,0.95) 0%, rgba(13,17,23,0.98) 100%);
    border-radius: 14px;
    padding: 20px 22px;
    border: 1px solid rgba(255,255,255,0.07);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    animation: slide-in-up 0.5s ease forwards;
}

.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 14px 14px;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,229,255,0.25);
}

.metric-card .label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 8px;
}

.metric-card .value {
    font-size: 2.2rem;
    font-weight: 900;
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.03em;
    line-height: 1;
}

.metric-card .sub {
    font-size: 0.75rem;
    color: #475569;
    margin-top: 4px;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── BADGE SYSTEM ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
}

/* ── INCIDENT CARDS ── */
.incident-card {
    background: linear-gradient(135deg, rgba(22,27,46,0.95) 0%, rgba(13,17,23,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    animation: slide-in-left 0.4s ease forwards;
}

.incident-card:hover {
    transform: translateX(4px);
    box-shadow: -4px 0 30px -5px rgba(0,229,255,0.15);
    border-color: rgba(0,229,255,0.2);
}

/* ── TIMELINE ── */
.tl-container {
    position: relative;
    padding-left: 32px;
    margin-top: 16px;
}

.tl-container::before {
    content: '';
    position: absolute;
    left: 8px; top: 0; bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, #00E5FF, #7C3AED, rgba(255,107,53,0.2));
    border-radius: 99px;
}

.tl-node {
    position: relative;
    margin-bottom: 28px;
    animation: slide-in-left 0.4s ease forwards;
}

.tl-dot {
    position: absolute;
    left: -28px;
    top: 4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 3px solid #0D1117;
}

.tl-dot.threat { background: #FF6B35; animation: glow-red 2s ease infinite; }
.tl-dot.action { background: #00C853; animation: pulse-ring 2s ease infinite; }
.tl-dot.info   { background: #00E5FF; }

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #0E4D6E 0%, #0A7EA4 50%, #00B4D8 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(0,229,255,0.3) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.01em !important;
    position: relative !important;
    overflow: hidden !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,180,216,0.4), 0 0 0 1px rgba(0,229,255,0.3) !important;
}

div.stButton > button[kind="primary"],
div.stButton > button[type="primary"] {
    background: linear-gradient(135deg, #7F1D1D 0%, #B91C1C 50%, #FF6B35 100%) !important;
    border-color: rgba(255,107,53,0.3) !important;
}

div.stButton > button[kind="primary"]:hover,
div.stButton > button[type="primary"]:hover {
    box-shadow: 0 8px 25px rgba(255,107,53,0.4) !important;
}

/* ── INPUTS & SELECTS ── */
div[data-baseweb="select"] > div {
    background: rgba(22,27,46,0.9) !important;
    border: 1px solid rgba(0,229,255,0.15) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    transition: border-color 0.2s !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: rgba(139, 92, 246, 0.5) !important;
}

div[data-baseweb="select"] span { color: #E2E8F0 !important; }

div[data-baseweb="popover"] {
    background: #0E0E2C !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    border-radius: 12px !important;
}

div[role="option"] { color: #CBD5E1 !important; background: #0E0E2C !important; }
div[role="option"]:hover { background: rgba(139, 92, 246, 0.15) !important; color: #F1F5F9 !important; }

textarea, input[type="text"], input[type="search"] {
    background: rgba(15, 15, 40, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    color: #E2E8F0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}

textarea:focus, input:focus {
    border-color: rgba(139, 92, 246, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

/* ── CODE ── */
code {
    font-family: 'Fira Code', monospace !important;
    background: rgba(139, 92, 246, 0.12) !important;
    color: #C4B5FD !important;
    padding: 2px 7px !important;
    border-radius: 5px !important;
    font-size: 0.83em !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
}

/* ── COMMENT CARDS ── */
.comment-card {
    background: rgba(15, 15, 40, 0.6);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border-left: 3px solid #8B5CF6;
    transition: all 0.2s ease;
}
.comment-card:hover { border-left-width: 5px; background: rgba(15,15,40,0.85); }

/* ── RADIO BUTTONS ── */
[data-testid="stRadio"] label {
    color: #94A3B8 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 6px 0 !important;
}
[data-testid="stRadio"] label:hover { color: #E2E8F0 !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(139, 92, 246, 0.12) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(15,15,40,0.5); }
::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.4); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.7); }

/* ── ALERT BANNER ── */
.threat-banner {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.04) 100%);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-left: 4px solid #EF4444;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 14px 0;
    animation: glow-red 3s ease infinite;
}

/* ── SHIMMER SEPARATOR ── */
.shimmer-line {
    height: 1px;
    margin: 24px 0;
    background: linear-gradient(90deg, transparent, #8B5CF6, #EC4899, #06B6D4, transparent);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
    border: none;
    outline: none;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def trigger_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

def get_cases():
    try:
        res = requests.get(f"{API_URL}/cases", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"⚠️ Unable to connect to backend: {e}")
    return []

def get_case(session_id):
    try:
        res = requests.get(f"{API_URL}/cases/{session_id}", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def update_status(session_id, status):
    try:
        res = requests.post(f"{API_URL}/cases/{session_id}/status", json={"status": status}, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def update_assignee(session_id, assignee):
    try:
        res = requests.post(f"{API_URL}/cases/{session_id}/assign", json={"assignee": assignee}, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def add_comment(session_id, author, message):
    try:
        res = requests.post(f"{API_URL}/cases/{session_id}/comment", json={"author": author, "message": message}, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def run_playbook(session_id, playbook_name):
    try:
        res = requests.post(f"{API_URL}/cases/{session_id}/playbook", json={"playbook_name": playbook_name}, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def get_model_arena():
    try:
        res = requests.get(f"{API_URL}/model-arena", timeout=5)
        if res.status_code == 200:
            return res.json().get("models", [])
    except Exception:
        pass
    return []

def get_budget():
    try:
        res = requests.get(f"{API_URL}/budget", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

def get_policies():
    try:
        res = requests.get(f"{API_URL}/policies", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

def toggle_policy(policy_id, enabled):
    try:
        res = requests.post(f"{API_URL}/policies/{policy_id}/toggle", json={"enabled": enabled}, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def get_baselines():
    try:
        res = requests.get(f"{API_URL}/baselines", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

def update_budget_config(cfg: dict):
    try:
        res = requests.post(f"{API_URL}/budget/config", json=cfg, timeout=5)
        return res.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  COMPONENT BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def status_badge(status):
    palette = {
        "New":         ("rgba(139,92,246,0.18)", "#A78BFA", "◉"),
        "In Progress": ("rgba(251,146,60,0.18)", "#FB923C", "◎"),
        "Remediated":  ("rgba(52,211,153,0.18)", "#34D399", "✓"),
        "Closed":      ("rgba(100,116,139,0.18)", "#94A3B8", "×"),
    }
    bg, fg, icon = palette.get(status, ("rgba(139,92,246,0.18)", "#A78BFA", "◉"))
    return f'<span class="badge" style="background:{bg}; color:{fg}; border: 1px solid {fg}40;">{icon} {status}</span>'

def severity_badge(severity):
    palette = {
        "critical": ("rgba(239,68,68,0.18)", "#F87171"),
        "high":     ("rgba(251,146,60,0.18)", "#FB923C"),
        "medium":   ("rgba(234,179,8,0.18)", "#EAB308"),
        "low":      ("rgba(52,211,153,0.18)", "#34D399"),
    }
    bg, fg = palette.get(str(severity).lower(), ("rgba(139,92,246,0.18)", "#A78BFA"))
    return f'<span class="badge" style="background:{bg}; color:{fg}; border: 1px solid {fg}40;">{str(severity).upper()}</span>'

def metric_card_html(label, value, sub="", color="#8B5CF6", icon=""):
    return f"""
    <div class="metric-card" style="border-color: {color}22;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{color},{color}88);border-radius:14px 14px 0 0;"></div>
        <div class="label">{icon} {label}</div>
        <div class="value" style="background:linear-gradient(135deg,{color},{color}CC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{value}</div>
        <div class="sub">{sub}</div>
    </div>
    """

def score_bar(score, color="#8B5CF6"):
    pct = min(100, max(0, int(score)))
    return f"""
    <div style="margin-top:8px;">
        <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,{color},{color}CC);border-radius:99px;transition:width 0.8s ease;box-shadow:0 0 8px {color}88;"></div>
        </div>
    </div>
    """

def shimmer():
    st.markdown('<div class="shimmer-line"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
# Logo area
st.sidebar.markdown("""
<div style="padding: 20px 10px 10px 10px; text-align: center;">
    <div style="font-size:2.8rem; animation: float 3s ease infinite; display:inline-block;">🛡️</div>
    <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:800;
                background:linear-gradient(135deg,#00E5FF,#7C3AED,#FF6B35);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                letter-spacing:-0.02em; margin-top:4px;">AgentShield</div>
    <div style="font-size:0.72rem; color:#475569; letter-spacing:0.06em; text-transform:uppercase;
                font-family:'Space Grotesk',sans-serif; margin-top:2px;">Security Copilot for Splunk</div>
</div>
<div class="shimmer-line"></div>
""", unsafe_allow_html=True)

menu = ["🏠 Overview", "📊 Observability", "📋 Case Hub", "🔍 Investigate", "🚀 Simulate",
        "🧪 Model Arena", "💰 Budget Monitor", "📜 Policies", "📈 Baselines"]

menu_descriptions = {
    "🏠 Overview":       "Start here · What AgentShield does",
    "📊 Observability":  "Live telemetry · Risk scores · Cost",
    "📋 Case Hub":       "Manage & triage incidents",
    "🔍 Investigate":    "Forensics · AI summaries · Playbooks",
    "🚀 Simulate":       "Run normal & attack scenarios",
    "🧪 Model Arena":    "Compare Claude model performance",
    "💰 Budget Monitor": "Token limits · Spend tracking",
    "📜 Policies":       "Security rules & enforcement",
    "📈 Baselines":      "Behavioral norms & anomaly bands",
}

if "navigation_choice" not in st.session_state:
    st.session_state.navigation_choice = menu[0]

choice = st.sidebar.radio("", menu, index=menu.index(st.session_state.navigation_choice))
st.session_state.navigation_choice = choice

desc = menu_descriptions.get(choice, "")
st.sidebar.markdown(f"""
<div style="margin:4px 4px 16px 4px; padding:10px 14px; background:rgba(139,92,246,0.07);
            border-left:3px solid #8B5CF6; border-radius:0 8px 8px 0;">
    <div style="font-size:0.72rem; color:#94A3B8; font-family:'Space Grotesk',sans-serif;">{desc}</div>
</div>
""", unsafe_allow_html=True)

# Sidebar footer status
st.sidebar.markdown("""
<div style="margin-top:auto; padding:16px 10px; border-top:1px solid rgba(139,92,246,0.1);">
    <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:#475569;font-family:'Space Grotesk',sans-serif;">
        <div style="width:8px;height:8px;border-radius:50%;background:#34D399;box-shadow:0 0 6px #34D399;animation:pulse-ring 2s ease infinite;"></div>
        Backend Connected · Splunk Live
    </div>
    <div style="font-size:0.7rem;color:#334155;margin-top:4px;">192.168.86.178 · Port 8000 · index=ai_agent_logs</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: OVERVIEW (HOME)
# ─────────────────────────────────────────────────────────────────────────────
if choice == "🏠 Overview":
    # Hero
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease; text-align:center; padding:40px 0 20px 0;">
        <div style="font-size:4rem; animation:float 3s ease infinite; display:inline-block;">🛡️</div>
        <h1 style="margin:12px 0 6px 0; font-size:2.8rem;
                   background:linear-gradient(135deg,#8B5CF6,#EC4899,#06B6D4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            AgentShield for Splunk
        </h1>
        <p style="color:#94A3B8; font-size:1.1rem; font-family:'Space Grotesk',sans-serif; max-width:620px; margin:0 auto 8px auto;">
            Real-time AI Agent Security &amp; Observability — built on Splunk Enterprise
        </p>
        <div style="display:inline-block; padding:6px 18px; background:rgba(52,211,153,0.12);
                    border:1px solid rgba(52,211,153,0.3); border-radius:99px;
                    font-size:0.78rem; color:#34D399; font-family:'Space Grotesk',sans-serif; letter-spacing:0.05em;">
            ● LIVE · Claude AI Agent + Splunk HEC + SPL Detections
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Live stats from log file
    _lp = "data/ai_agent_logs.jsonl"
    if not os.path.exists(_lp):
        _lp = "../data/ai_agent_logs.jsonl"
    try:
        _df = pd.read_json(_lp, lines=True)
        _df = _df[_df["prompt"].notna()].copy() if "prompt" in _df.columns else _df
        _total   = len(_df)
        _threats = int((_df["severity"].isin(["critical","high"])).sum()) if "severity" in _df.columns else 0
        _blocked = int((_df["tool_allowed"] == False).sum()) if "tool_allowed" in _df.columns else 0
        _cost    = _df["estimated_cost_usd"].sum() if "estimated_cost_usd" in _df.columns else 0
        _inject  = int((_df["injection_score"] >= 70).sum()) if "injection_score" in _df.columns else 0
    except Exception:
        _total = _threats = _blocked = _cost = _inject = 0

    s1, s2, s3, s4, s5 = st.columns(5)
    for col, val, lbl, color, icon in [
        (s1, f"{_total:,}",   "Total Requests",    "#8B5CF6", "⚡"),
        (s2, f"{_threats:,}", "Threats Detected",  "#EF4444", "🚨"),
        (s3, f"{_blocked:,}", "Attacks Blocked",   "#F59E0B", "🚫"),
        (s4, f"{_inject:,}",  "Injection Alerts",  "#EC4899", "💉"),
        (s5, f"${_cost:.3f}", "Total Agent Cost",  "#10B981", "💰"),
    ]:
        col.markdown(metric_card_html(lbl, val, "since deployment", color, icon), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # What is AgentShield
    st.markdown("""
    <div style="text-align:center; margin-bottom:20px;">
        <h2 style="font-size:1.5rem; color:#F1F5F9; margin-bottom:4px;">What does AgentShield do?</h2>
        <p style="color:#64748B; font-size:0.88rem; font-family:'Space Grotesk',sans-serif;">
            Three capabilities working together to secure your AI agents
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, color, points in [
        (c1, "👁️", "Monitor", "#8B5CF6", [
            "Every agent request logged in real time",
            "Latency, token usage & cost tracked",
            "Risk scores computed per transaction",
            "Streaming into Splunk via HEC",
        ]),
        (c2, "🔍", "Detect", "#EF4444", [
            "Prompt injection attack detection",
            "PII & secret leakage scanning",
            "Unauthorized tool-call interception",
            "9 SPL detection rules in Splunk",
        ]),
        (c3, "⚡", "Respond", "#10B981", [
            "Automated case creation for incidents",
            "SOC playbooks with step-by-step guidance",
            "Claude AI generates incident summaries",
            "Policy enforcement & budget limits",
        ]),
    ]:
        items_html = "".join(f'<div style="display:flex;gap:8px;margin-bottom:6px;"><span style="color:{color};">▸</span><span style="color:#CBD5E1;font-size:0.83rem;">{p}</span></div>' for p in points)
        col.markdown(f"""
        <div class="shield-card" style="border-color:{color}33;min-height:220px;">
            <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
            <div style="font-size:1.1rem;font-weight:700;color:{color};font-family:'Space Grotesk',sans-serif;margin-bottom:14px;">{title}</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    # Animated pipeline
    st.markdown("""
    <style>
    .pipeline-wrap {
        position:relative; background:rgba(13,17,23,0.95);
        border:1px solid rgba(0,229,255,0.12); border-radius:20px;
        padding:36px 28px 28px 28px; margin:12px 0 24px 0; overflow:hidden;
    }
    .pipeline-wrap::before {
        content:''; position:absolute; inset:0;
        background:radial-gradient(ellipse at 50% 0%, rgba(0,229,255,0.05) 0%, transparent 70%);
        pointer-events:none;
    }
    .pipe-title {
        text-align:center; font-size:1.3rem; font-weight:700;
        color:#E2E8F0; font-family:'Space Grotesk',sans-serif; margin-bottom:28px;
    }
    .pipe-title span { color:#00E5FF; }
    .pipeline-row {
        display:flex; align-items:center; justify-content:center;
        gap:0; position:relative; margin-bottom:24px;
    }
    .pipe-node {
        text-align:center; padding:14px 18px; border-radius:14px;
        min-width:108px; position:relative; z-index:2; flex-shrink:0;
    }
    .pipe-node .icon { font-size:1.8rem; }
    .pipe-node .label {
        font-size:0.72rem; font-weight:700; margin-top:6px;
        font-family:'Space Grotesk',sans-serif; letter-spacing:0.02em;
    }
    .pipe-node .sub { font-size:0.6rem; color:#64748B; margin-top:2px; }
    .node-user   { background:rgba(124,58,237,0.12); border:1px solid rgba(124,58,237,0.35); }
    .node-agent  { background:rgba(0,229,255,0.08);  border:1px solid rgba(0,229,255,0.35);  animation:node-ping 3s ease infinite; }
    .node-shield { background:rgba(0,200,83,0.1);    border:1px solid rgba(0,200,83,0.4);    animation:node-ping 3s ease 0.5s infinite; }
    .node-splunk { background:rgba(255,107,53,0.1);  border:1px solid rgba(255,107,53,0.35); animation:node-ping 3s ease 1s infinite; }
    .node-spl    { background:rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.3);  animation:node-ping 3s ease 1.5s infinite; }
    .node-dash   { background:rgba(0,229,255,0.1);   border:1px solid rgba(0,229,255,0.4);   animation:node-ping 3s ease 2s infinite; }
    .pipe-track {
        flex:1; height:3px; position:relative; overflow:visible; min-width:30px;
        background:rgba(255,255,255,0.05); border-radius:99px;
    }
    /* Normal traffic — cyan dots */
    .pipe-track::before {
        content:''; position:absolute; top:50%; margin-top:-5px;
        width:10px; height:10px; border-radius:50%;
        background:#00E5FF; box-shadow:0 0 8px #00E5FF;
        animation:flow-packet 3s linear infinite;
    }
    /* Attack traffic — orange dots, every other track */
    .pipe-track.attack::before {
        background:#FF6B35; box-shadow:0 0 10px #FF6B35;
        animation:flow-packet 3s linear 1.5s infinite;
    }
    .pipe-track.blocked::before {
        background:#FF6B35; box-shadow:0 0 10px #FF6B35;
        animation:flow-packet-blocked 3s linear 1.5s infinite;
    }
    .legend-row {
        display:flex; justify-content:center; gap:28px; margin-top:4px;
    }
    .legend-item {
        display:flex; align-items:center; gap:7px;
        font-size:0.72rem; color:#94A3B8; font-family:'Space Grotesk',sans-serif;
    }
    .legend-dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
    .status-bar {
        display:flex; justify-content:center; gap:20px; margin-top:14px; flex-wrap:wrap;
    }
    .status-chip {
        padding:5px 14px; border-radius:99px; font-size:0.7rem;
        font-weight:600; font-family:'Space Grotesk',sans-serif; letter-spacing:0.04em;
    }
    </style>
    <div class="pipeline-wrap">
        <div class="pipe-title">Live Data Flow — <span>Watch events travel through AgentShield</span></div>
        <div class="pipeline-row">
            <div class="pipe-node node-user">
                <div class="icon">👤</div>
                <div class="label" style="color:#A78BFA;">User / Attacker</div>
                <div class="sub">Sends prompt</div>
            </div>
            <div class="pipe-track"></div>
            <div class="pipe-node node-agent">
                <div class="icon">🤖</div>
                <div class="label" style="color:#00E5FF;">Claude Agent</div>
                <div class="sub">Processes request</div>
            </div>
            <div class="pipe-track blocked"></div>
            <div class="pipe-node node-shield">
                <div class="icon">🛡️</div>
                <div class="label" style="color:#00C853;">AgentShield</div>
                <div class="sub">Scores &amp; intercepts</div>
            </div>
            <div class="pipe-track attack"></div>
            <div class="pipe-node node-splunk">
                <div class="icon">📡</div>
                <div class="label" style="color:#FF6B35;">Splunk HEC</div>
                <div class="sub">Indexes event</div>
            </div>
            <div class="pipe-track"></div>
            <div class="pipe-node node-spl">
                <div class="icon">🔎</div>
                <div class="label" style="color:#FBBF24;">SPL Detections</div>
                <div class="sub">9 alert rules</div>
            </div>
            <div class="pipe-track"></div>
            <div class="pipe-node node-dash">
                <div class="icon">📊</div>
                <div class="label" style="color:#00E5FF;">Dashboard</div>
                <div class="sub">Visualize &amp; act</div>
            </div>
        </div>
        <div class="legend-row">
            <div class="legend-item">
                <div class="legend-dot" style="background:#00E5FF;box-shadow:0 0 6px #00E5FF;"></div>
                Normal traffic — flows through, logged to Splunk
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#FF6B35;box-shadow:0 0 6px #FF6B35;"></div>
                Attack traffic — intercepted at AgentShield, still indexed as threat event
            </div>
        </div>
        <div class="status-bar">
            <div class="status-chip" style="background:rgba(0,200,83,0.12);border:1px solid rgba(0,200,83,0.3);color:#00C853;">● HEC Connected</div>
            <div class="status-chip" style="background:rgba(0,229,255,0.1);border:1px solid rgba(0,229,255,0.25);color:#00E5FF;">● Claude API Live</div>
            <div class="status-chip" style="background:rgba(255,107,53,0.1);border:1px solid rgba(255,107,53,0.25);color:#FF6B35;">● Threat Detection Active</div>
            <div class="status-chip" style="background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.2);color:#FBBF24;">● SPL Rules Loaded</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation guide for judges
    st.markdown("""
    <div style="margin-top:8px;">
        <h2 style="font-size:1.3rem; color:#F1F5F9; margin-bottom:14px;">
            Judge's Guide — Where to look
        </h2>
    </div>
    """, unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    for col, items in [
        (g1, [
            ("📊 Observability",  "#8B5CF6", "Live risk scores, latency charts, cost trends, PII detections"),
            ("🚀 Simulate",       "#06B6D4", "Run a real Claude attack scenario and watch it get detected"),
            ("📋 Case Hub",       "#F59E0B", "Triaged incident cases auto-created from attack events"),
            ("🔍 Investigate",    "#EC4899", "Click any case → Claude generates an AI incident summary"),
        ]),
        (g2, [
            ("🧪 Model Arena",    "#34D399", "Compare safety & performance across Claude model variants"),
            ("💰 Budget Monitor", "#F97316", "Per-session token limits and cost enforcement in action"),
            ("📜 Policies",       "#A78BFA", "Security rules: block injection, PII, unauthorized tools"),
            ("📈 Baselines",      "#06B6D4", "Behavioral norms — anomaly bands for normal vs attack traffic"),
        ]),
    ]:
        for label, color, desc_text in items:
            col.markdown(f"""
            <div style="display:flex;gap:12px;align-items:flex-start;padding:12px 16px;margin-bottom:8px;
                        background:rgba(15,15,40,0.6);border:1px solid {color}22;border-radius:10px;
                        border-left:3px solid {color};">
                <div style="font-size:1.1rem;min-width:28px;">{label.split()[0]}</div>
                <div>
                    <div style="font-size:0.85rem;font-weight:600;color:{color};font-family:'Space Grotesk',sans-serif;">{" ".join(label.split()[1:])}</div>
                    <div style="font-size:0.78rem;color:#64748B;margin-top:2px;">{desc_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: OBSERVABILITY
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "📊 Observability":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#8B5CF6,#EC4899);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            📊 Agent Observability
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Real-time telemetry · Token analytics · Threat intelligence · Historical baselines
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    log_path = "data/ai_agent_logs.jsonl"
    if not os.path.exists(log_path):
        log_path = "../data/ai_agent_logs.jsonl"

    try:
        df_raw = pd.read_json(log_path, lines=True)
        # Only keep rows that are actual agent transaction logs (have a prompt field)
        df = df_raw[df_raw["prompt"].notna()].copy() if "prompt" in df_raw.columns else df_raw.copy()

        if not df.empty:
            # ── KPI METRICS ──────────────────────────────────────────────────
            total = len(df)
            avg_lat = df["latency_ms"].mean() if "latency_ms" in df.columns else 0
            total_cost = df["estimated_cost_usd"].sum() if "estimated_cost_usd" in df.columns else 0
            avg_quality = df["quality_score"].mean() if "quality_score" in df.columns else 0
            threat_count = int((df["severity"].isin(["critical", "high"])).sum()) if "severity" in df.columns else 0
            blocked_count = int((df["tool_allowed"] == False).sum()) if "tool_allowed" in df.columns else 0
            avg_risk = df["risk_score"].mean() if "risk_score" in df.columns else 0
            pii_hits = int(df["pii_detected"].sum()) if "pii_detected" in df.columns else 0

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(metric_card_html("Total Requests", f"{total:,}", "All agent transactions", "#8B5CF6", "⚡"), unsafe_allow_html=True)
            with k2:
                st.markdown(metric_card_html("Avg Latency", f"{avg_lat:.0f}ms", "p50 response time", "#06B6D4", "⏱"), unsafe_allow_html=True)
            with k3:
                st.markdown(metric_card_html("Threat Events", str(threat_count), "Critical + High severity", "#EF4444", "🚨"), unsafe_allow_html=True)
            with k4:
                st.markdown(metric_card_html("Token Cost", f"${total_cost:.3f}", "Cumulative spend (USD)", "#10B981", "💰"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            k5, k6, k7, k8 = st.columns(4)
            with k5:
                st.markdown(metric_card_html("Blocked Attempts", str(blocked_count), "Tools disallowed by policy", "#F59E0B", "🚫"), unsafe_allow_html=True)
            with k6:
                st.markdown(metric_card_html("Avg Risk Score", f"{avg_risk:.1f}/100", "Mean across all sessions", "#EC4899", "⚠️"), unsafe_allow_html=True)
            with k7:
                st.markdown(metric_card_html("PII Detections", str(pii_hits), "Sensitive data exposures", "#F97316", "🔐"), unsafe_allow_html=True)
            with k8:
                st.markdown(metric_card_html("Avg Quality", f"{avg_quality:.2f}", "Response quality score", "#34D399", "✨"), unsafe_allow_html=True)

            shimmer()

            # ── CHART ROW 1 ─────────────────────────────────────────────────
            c1, c2 = st.columns([3, 2])

            with c1:
                st.markdown("<h3 style='margin:0 0 12px 0;'>📈 Risk Score & Latency Over Time</h3>", unsafe_allow_html=True)
                plot_df = df.tail(60).reset_index(drop=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=plot_df.index, y=plot_df.get("risk_score", []),
                    name="Risk Score", fill="tozeroy",
                    line=dict(color="#EF4444", width=2),
                    fillcolor="rgba(239,68,68,0.08)"
                ))
                fig.add_trace(go.Scatter(
                    x=plot_df.index, y=plot_df.get("latency_ms", []),
                    name="Latency (ms)", yaxis="y2",
                    line=dict(color="#06B6D4", width=1.5, dash="dot"),
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#64748B"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
                    xaxis=dict(showgrid=False, zeroline=False, color="#334155"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", color="#334155", title="Risk Score"),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#06B6D4", title="Latency (ms)"),
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#8B5CF6", font=dict(family="Inter", color="#E2E8F0"))
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with c2:
                st.markdown("<h3 style='margin:0 0 12px 0;'>🎯 Severity Breakdown</h3>", unsafe_allow_html=True)
                if "severity" in df.columns:
                    sev_counts = df["severity"].value_counts().reset_index()
                    sev_counts.columns = ["severity", "count"]
                    color_map = {"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#34D399"}
                    colors = [color_map.get(s, "#8B5CF6") for s in sev_counts["severity"]]
                    fig2 = go.Figure(go.Pie(
                        labels=sev_counts["severity"].str.upper(),
                        values=sev_counts["count"],
                        hole=0.68,
                        marker=dict(colors=colors, line=dict(color="#04051A", width=3)),
                        textinfo="label+percent",
                        textfont=dict(family="Space Grotesk", size=11, color="#E2E8F0"),
                        insidetextorientation="radial",
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
                    ))
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=True,
                        legend=dict(orientation="v", x=1.0, y=0.5, bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8", size=10)),
                        margin=dict(l=0, r=60, t=0, b=0),
                        annotations=[dict(
                            text=f"<b>{threat_count}</b><br><span style='font-size:10px'>Threats</span>",
                            x=0.5, y=0.5, showarrow=False,
                            font=dict(size=18, color="#F1F5F9", family="Inter")
                        )]
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            shimmer()

            # ── CHART ROW 2 ─────────────────────────────────────────────────
            c3, c4 = st.columns([2, 3])

            with c3:
                st.markdown("<h3 style='margin:0 0 12px 0;'>🔥 Risk Type Heatmap</h3>", unsafe_allow_html=True)
                if "risk_type" in df.columns:
                    rt = df["risk_type"].fillna("none").value_counts().head(8).reset_index()
                    rt.columns = ["risk_type", "count"]
                    fig3 = go.Figure(go.Bar(
                        x=rt["count"],
                        y=rt["risk_type"].str.replace("_", " ").str.title(),
                        orientation="h",
                        marker=dict(
                            color=rt["count"],
                            colorscale=[[0, "#8B5CF6"], [0.5, "#EC4899"], [1, "#EF4444"]],
                            showscale=False,
                            line=dict(width=0)
                        ),
                        text=rt["count"],
                        textposition="outside",
                        textfont=dict(color="#94A3B8", size=11, family="Inter"),
                        hovertemplate="<b>%{y}</b><br>Occurrences: %{x}<extra></extra>"
                    ))
                    fig3.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0, r=20, t=0, b=0),
                        xaxis=dict(showgrid=False, zeroline=False, color="#334155", showticklabels=False),
                        yaxis=dict(showgrid=False, color="#94A3B8", tickfont=dict(size=11, family="Space Grotesk")),
                        hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#EC4899", font=dict(family="Inter", color="#E2E8F0"))
                    )
                    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

            with c4:
                st.markdown("<h3 style='margin:0 0 12px 0;'>🧠 Model Performance Matrix</h3>", unsafe_allow_html=True)
                if all(c in df.columns for c in ["model", "risk_score", "latency_ms", "quality_score"]):
                    bubble_df = df.groupby("model").agg(
                        avg_risk=("risk_score", "mean"),
                        avg_latency=("latency_ms", "mean"),
                        avg_quality=("quality_score", "mean"),
                        count=("model", "count")
                    ).reset_index()
                    fig4 = go.Figure()
                    colors_b = ["#8B5CF6", "#EC4899", "#06B6D4", "#34D399", "#F97316"]
                    for i, row in bubble_df.iterrows():
                        fig4.add_trace(go.Scatter(
                            x=[row["avg_latency"]],
                            y=[row["avg_risk"]],
                            mode="markers+text",
                            name=row["model"],
                            text=[row["model"]],
                            textposition="top center",
                            textfont=dict(color="#CBD5E1", size=10, family="Space Grotesk"),
                            marker=dict(
                                size=max(14, row["count"] * 4),
                                color=colors_b[i % len(colors_b)],
                                opacity=0.85,
                                line=dict(color="#04051A", width=2)
                            ),
                            hovertemplate=f"<b>{row['model']}</b><br>Avg Risk: {row['avg_risk']:.1f}<br>Avg Latency: {row['avg_latency']:.0f}ms<br>Quality: {row['avg_quality']:.2f}<br>Requests: {int(row['count'])}<extra></extra>"
                        ))
                    fig4.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155", title="Avg Latency (ms)"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155", title="Avg Risk Score"),
                        hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#8B5CF6", font=dict(family="Inter", color="#E2E8F0"))
                    )
                    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

            shimmer()

            # ── CHART ROW 3: INJECTION SCORE + COST ─────────────────────────
            c5, c6 = st.columns(2)

            with c5:
                st.markdown("<h3 style='margin:0 0 12px 0;'>💉 Injection Score Distribution</h3>", unsafe_allow_html=True)
                if "injection_score" in df.columns:
                    fig5 = go.Figure(go.Histogram(
                        x=df["injection_score"],
                        nbinsx=20,
                        marker=dict(
                            color="#EC4899",
                            line=dict(color="#04051A", width=0.5)
                        ),
                        hovertemplate="Injection Score: %{x}<br>Count: %{y}<extra></extra>"
                    ))
                    fig5.add_vline(x=70, line_dash="dash", line_color="#EF4444", opacity=0.6,
                                   annotation_text="Threat Threshold (70)", annotation_font_color="#EF4444",
                                   annotation_font_size=10)
                    fig5.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, zeroline=False, color="#334155", title="Injection Score"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", color="#334155", title="Count"),
                        hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#EC4899", font=dict(family="Inter", color="#E2E8F0"))
                    )
                    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

            with c6:
                st.markdown("<h3 style='margin:0 0 12px 0;'>💸 Cumulative Cost Trend</h3>", unsafe_allow_html=True)
                if "estimated_cost_usd" in df.columns:
                    cost_df = df["estimated_cost_usd"].fillna(0).cumsum().tail(60).reset_index(drop=True)
                    fig6 = go.Figure(go.Scatter(
                        x=cost_df.index, y=cost_df.values,
                        fill="tozeroy",
                        line=dict(color="#10B981", width=2),
                        fillcolor="rgba(16,185,129,0.06)",
                        hovertemplate="Request #%{x}<br>Cumulative Cost: $%{y:.4f}<extra></extra>"
                    ))
                    fig6.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, zeroline=False, color="#334155"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", color="#334155", title="USD"),
                        hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#10B981", font=dict(family="Inter", color="#E2E8F0"))
                    )
                    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

            shimmer()

            # ── RECENT TRANSACTIONS TABLE ────────────────────────────────────
            st.markdown("<h3 style='margin:0 0 12px 0;'>📋 Recent Transactions</h3>", unsafe_allow_html=True)
            display_cols = [c for c in ["timestamp", "session_id", "user_id", "model", "tool_requested", "risk_type", "risk_score", "severity", "latency_ms"] if c in df.columns]
            styled = df[display_cols].tail(15).copy()
            st.dataframe(styled, use_container_width=True, height=340)

        else:
            st.info("💡 No agent transactions found. Run simulations in **Simulate** to generate data.")
    except Exception as e:
        st.info("💡 No telemetry logs available yet. Head to **Simulate** to generate traffic.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: CASE MANAGEMENT HUB
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "📋 Case Hub":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#EC4899,#8B5CF6);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            📋 Case Management Hub
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Active incidents · Analyst assignments · Threat lifecycle management
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    cases = get_cases()

    if not cases:
        st.info("🎉 No active security cases. Run attack simulations to populate incidents.")
    else:
        # ── KPI STRIP ────────────────────────────────────────────────────────
        total_cases = len(cases)
        new_c     = sum(1 for c in cases if c.get("status") == "New")
        inprog_c  = sum(1 for c in cases if c.get("status") == "In Progress")
        remed_c   = sum(1 for c in cases if c.get("status") == "Remediated")
        closed_c  = sum(1 for c in cases if c.get("status") == "Closed")
        crit_c    = sum(1 for c in cases if str(c.get("severity", "")).lower() == "critical")

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1: st.markdown(metric_card_html("Total Incidents", str(total_cases), "All active cases", "#8B5CF6", "📦"), unsafe_allow_html=True)
        with m2: st.markdown(metric_card_html("New / Unread", str(new_c), "Awaiting triage", "#EF4444", "🆕"), unsafe_allow_html=True)
        with m3: st.markdown(metric_card_html("In Progress", str(inprog_c), "Under investigation", "#F97316", "🔎"), unsafe_allow_html=True)
        with m4: st.markdown(metric_card_html("Remediated", str(remed_c), "Contained & resolved", "#34D399", "✅"), unsafe_allow_html=True)
        with m5: st.markdown(metric_card_html("Critical", str(crit_c), "Immediate action needed", "#EC4899", "🚨"), unsafe_allow_html=True)

        shimmer()

        # ── STATUS + SEVERITY MINI-CHARTS ────────────────────────────────────
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown("<h3 style='margin:0 0 10px;'>Case Status Distribution</h3>", unsafe_allow_html=True)
            status_data = {"New": new_c, "In Progress": inprog_c, "Remediated": remed_c, "Closed": closed_c}
            fig_s = go.Figure(go.Bar(
                x=list(status_data.keys()),
                y=list(status_data.values()),
                marker=dict(color=["#A78BFA", "#FB923C", "#34D399", "#64748B"],
                            line=dict(width=0)),
                text=list(status_data.values()),
                textposition="outside",
                textfont=dict(color="#94A3B8", size=12, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Cases: %{y}<extra></extra>"
            ))
            fig_s.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, zeroline=False, color="#475569"),
                yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.06)", color="#334155", showticklabels=False),
                showlegend=False,
                hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#8B5CF6", font=dict(family="Inter", color="#E2E8F0"))
            )
            st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

        with ch2:
            st.markdown("<h3 style='margin:0 0 10px;'>Severity Spread</h3>", unsafe_allow_html=True)
            if cases:
                sev_counter = {}
                for c in cases:
                    s = str(c.get("severity", "unknown")).lower()
                    sev_counter[s] = sev_counter.get(s, 0) + 1
                sev_labels = list(sev_counter.keys())
                sev_vals   = list(sev_counter.values())
                sev_colors = {"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#34D399"}
                fig_sv = go.Figure(go.Pie(
                    labels=[l.upper() for l in sev_labels],
                    values=sev_vals,
                    hole=0.6,
                    marker=dict(colors=[sev_colors.get(l, "#8B5CF6") for l in sev_labels],
                                line=dict(color="#04051A", width=3)),
                    textinfo="label+value",
                    textfont=dict(family="Space Grotesk", size=11, color="#E2E8F0"),
                    hovertemplate="<b>%{label}</b><br>Cases: %{value}<extra></extra>"
                ))
                fig_sv.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    annotations=[dict(text=f"<b>{total_cases}</b><br>Cases", x=0.5, y=0.5,
                                      showarrow=False, font=dict(size=16, color="#F1F5F9", family="Inter"))]
                )
                st.plotly_chart(fig_sv, use_container_width=True, config={"displayModeBar": False})

        shimmer()

        # ── FILTERS ──────────────────────────────────────────────────────────
        st.markdown("<h3 style='margin:0 0 12px;'>🔍 Filter Incidents</h3>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            status_filter = st.selectbox("Status", ["All", "New", "In Progress", "Remediated", "Closed"])
        with f2:
            severity_filter = st.selectbox("Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with f3:
            search_query = st.text_input("Search (Session ID / User ID)", "")

        filtered = []
        for c in cases:
            if status_filter != "All" and c.get("status") != status_filter: continue
            if severity_filter != "All" and str(c.get("severity", "")).upper() != severity_filter: continue
            if search_query:
                q = search_query.lower()
                if (q not in str(c.get("user_id", "")).lower() and
                    q not in str(c.get("session_id", "")).lower() and
                    q not in str(c.get("risk_type", "")).lower()):
                    continue
            filtered.append(c)

        if not filtered:
            st.warning("No incidents match your filter criteria.")
        else:
            st.markdown(f"<p style='color:#475569;font-size:0.85rem;margin:8px 0 12px;'>Showing {len(filtered)} of {total_cases} incidents</p>", unsafe_allow_html=True)

            sev_border = {"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#34D399"}

            for idx, c in enumerate(filtered):
                sess_id   = c.get("session_id", "unknown")
                status    = c.get("status", "New")
                severity  = c.get("severity") or "high"
                risk_type = c.get("risk_type") or "unknown"
                user_id   = c.get("user_id") or "unknown"
                score     = c.get("risk_score") or 0
                timestamp = c.get("timestamp") or ""
                border_c  = sev_border.get(str(severity).lower(), "#8B5CF6")

                st.markdown(f"""
                <div class="incident-card" style="border-left: 4px solid {border_c};">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                            <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.05rem;color:#F1F5F9;">
                                {sess_id}
                            </span>
                            {status_badge(status)}
                            {severity_badge(severity)}
                        </div>
                        <span style="color:#334155;font-size:0.78rem;font-family:'Space Grotesk',sans-serif;">🕒 {timestamp[:19] if timestamp else '—'}</span>
                    </div>

                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:14px;">
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;color:#475569;letter-spacing:0.06em;margin-bottom:3px;">Risk Category</div>
                            <div style="font-weight:600;color:{border_c};font-size:0.88rem;">{str(risk_type).upper().replace('_', ' ')}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;color:#475569;letter-spacing:0.06em;margin-bottom:3px;">Analyst</div>
                            <div style="font-weight:500;color:#A78BFA;font-size:0.88rem;">{c.get('assignee') or 'Unassigned'}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;color:#475569;letter-spacing:0.06em;margin-bottom:3px;">Risk Score</div>
                            <div style="font-weight:700;color:#F1F5F9;font-size:0.88rem;">{score}/100</div>
                            {score_bar(score, border_c)}
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;color:#475569;letter-spacing:0.06em;margin-bottom:3px;">Target User</div>
                            <div style="font-family:'Fira Code',monospace;color:#CBD5E1;font-size:0.82rem;">{user_id}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_btn, _ = st.columns([1, 5])
                with col_btn:
                    if st.button(f"🔍 Investigate", key=f"inv_{sess_id}_{idx}"):
                        st.session_state.selected_case_id = sess_id
                        st.session_state.navigation_choice = "🔍 Investigate"
                        trigger_rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: INVESTIGATION & PLAYBOOKS
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "🔍 Investigate":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#06B6D4,#8B5CF6);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            🔍 Incident Investigation & Playbook Center
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Forensic timelines · Prompt analysis · Automated containment playbooks
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    cases = get_cases()
    if not cases:
        st.info("💡 No cases loaded. Run simulations first.")
    else:
        all_ids = [c.get("session_id") for c in cases]
        selected_id = st.session_state.get("selected_case_id")
        default_idx = all_ids.index(selected_id) if selected_id in all_ids else 0

        session_id = st.selectbox("Select Case", all_ids, index=default_idx,
                                   format_func=lambda x: f"🗂 {x}")
        st.session_state.selected_case_id = session_id

        case_details = get_case(session_id)
        base_case    = next((c for c in cases if c.get("session_id") == session_id), {})

        if case_details:
            sev_val    = base_case.get("severity") or "unknown"
            status_val = case_details.get("status") or "New"
            assign_val = case_details.get("assignee") or "unassigned"
            risk_score = base_case.get("risk_score") or 0
            risk_type  = base_case.get("risk_type") or "unknown"

            sev_color  = {"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#34D399"}.get(sev_val.lower(), "#8B5CF6")

            # ── OVERVIEW STRIP ────────────────────────────────────────────────
            o1, o2, o3, o4 = st.columns(4)
            with o1: st.markdown(metric_card_html("Severity", sev_val.upper(), "Incident level", sev_color, "⚡"), unsafe_allow_html=True)
            with o2: st.markdown(metric_card_html("Status", status_val, "Lifecycle stage", "#8B5CF6", "📌"), unsafe_allow_html=True)
            with o3: st.markdown(metric_card_html("Analyst", assign_val, "Current owner", "#06B6D4", "👤"), unsafe_allow_html=True)
            with o4: st.markdown(metric_card_html("Risk Score", f"{risk_score}/100", "Threat severity index", sev_color, "🎯"), unsafe_allow_html=True)

            if risk_score >= 80:
                st.markdown(f"""
                <div class="threat-banner">
                    <span style="color:#EF4444;font-weight:700;">🚨 CRITICAL THREAT ALERT</span>
                    <span style="color:#FCA5A5;"> — Risk score <strong>{risk_score}/100</strong> exceeds emergency threshold.
                    Immediate containment playbook execution is strongly recommended.</span>
                </div>
                """, unsafe_allow_html=True)

            shimmer()

            col_left, col_right = st.columns([1.1, 0.9])

            # ── LEFT: FORENSIC TIMELINE ──────────────────────────────────────
            with col_left:
                st.markdown("<h3 style='margin:0 0 4px;'>🔬 Forensic Transaction Timeline</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#475569;font-size:0.82rem;margin:0 0 16px;'>Session: <code>{session_id}</code> · Attack vector: <span style='color:{sev_color};font-weight:600;'>{str(risk_type).upper().replace('_',' ')}</span></p>", unsafe_allow_html=True)

                events = case_details.get("events", [])

                if not events:
                    st.markdown(f"""
                    <div class="tl-container">
                        <div class="tl-node">
                            <div class="tl-dot info"></div>
                            <div style="font-size:0.75rem;color:#475569;margin-bottom:4px;">{base_case.get('timestamp', '')}</div>
                            <div style="font-weight:600;color:#F1F5F9;margin-bottom:6px;">Initial Session Vector</div>
                            <div style="background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.15);border-radius:10px;padding:12px;">
                                <p style="margin:0;color:#94A3B8;font-size:0.83rem;"><strong style='color:#CBD5E1'>Prompt:</strong> {base_case.get('prompt','—')}</p>
                                <p style="margin:6px 0 0;color:#94A3B8;font-size:0.83rem;"><strong style='color:#CBD5E1'>Response:</strong> {base_case.get('response','—')}</p>
                                <p style="margin:6px 0 0;color:#FCA5A5;font-size:0.8rem;">⚠️ Tool: <code>{base_case.get('tool_requested','—')}</code></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="tl-container">', unsafe_allow_html=True)
                    for idx, ev in enumerate(events):
                        if ev.get("action_taken") and ev.get("action_taken") != "none":
                            action   = ev.get("action_taken", "")
                            message  = ev.get("message") or f"Remediation: {action}"
                            ev_sev   = ev.get("severity") or "info"
                            dot_cls  = "threat" if ev_sev == "critical" else ("action" if ev_sev in ["warning","info"] else "info")
                            act_color = "#EF4444" if ev_sev == "critical" else ("#F97316" if ev_sev == "warning" else "#10B981")
                            act_rgb = "239,68,68" if ev_sev == "critical" else ("249,115,22" if ev_sev == "warning" else "16,185,129")
                            act_bg = f"rgba({act_rgb},0.06)"

                            st.markdown(f"""
                            <div class="tl-node">
                                <div class="tl-dot {dot_cls}"></div>
                                <div style="font-size:0.72rem;color:#475569;margin-bottom:4px;">⏱ Step {idx+1} · {ev.get('timestamp','')[:19]}</div>
                                <div style="font-weight:700;color:{act_color};font-size:0.9rem;margin-bottom:6px;">🛡️ {str(action).upper().replace('_',' ')}</div>
                                <div style="background:{act_bg};border:1px solid {act_color}22;border-radius:10px;padding:12px;">
                                    <p style="margin:0;color:#CBD5E1;font-size:0.83rem;">{message}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            ev_score    = ev.get("risk_score") or 0
                            ev_rt       = ev.get("risk_type") or "unknown"
                            ev_model    = ev.get("model") or "unknown"
                            ev_prompt   = ev.get("prompt") or "—"
                            ev_response = ev.get("response") or "—"
                            ev_tool     = ev.get("tool_requested") or "—"
                            ev_allowed  = ev.get("tool_allowed")
                            dot_cls     = "threat" if ev_score >= 80 else "info"
                            score_c     = "#EF4444" if ev_score >= 80 else "#06B6D4"
                            allowed_tag = f'<span style="color:#34D399;font-weight:600;">[ALLOWED]</span>' if ev_allowed else f'<span style="color:#EF4444;font-weight:600;">[BLOCKED]</span>'

                            st.markdown(f"""
                            <div class="tl-node">
                                <div class="tl-dot {dot_cls}"></div>
                                <div style="font-size:0.72rem;color:#475569;margin-bottom:4px;">⏱ Step {idx+1} · {ev.get('timestamp','')[:19]}</div>
                                <div style="font-weight:600;color:#E2E8F0;font-size:0.9rem;margin-bottom:6px;">
                                    🤖 Model Transaction
                                    <span style="font-size:0.75rem;color:#64748B;font-weight:400;margin-left:6px;">via {ev_model}</span>
                                </div>
                                <div style="background:rgba(15,15,40,0.7);border:1px solid rgba(139,92,246,0.1);border-radius:10px;padding:12px;">
                                    <p style="margin:0;color:#94A3B8;font-size:0.82rem;line-height:1.5;"><strong style='color:#CBD5E1'>Prompt:</strong> "{ev_prompt}"</p>
                                    <p style="margin:8px 0 0;color:#94A3B8;font-size:0.82rem;line-height:1.5;"><strong style='color:#CBD5E1'>Response:</strong> "{ev_response}"</p>
                                    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:0.78rem;">
                                        <span>🔧 Tool: <code>{ev_tool}</code> {allowed_tag}</span>
                                        <span style="color:#64748B;">⚠️ <span style="color:{score_c};font-weight:600;">{str(ev_rt).upper().replace('_',' ')}</span> · {ev_score}/100</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # ── RIGHT: PLAYBOOKS + CONTROLS ──────────────────────────────────
            with col_right:
                # Playbook Engine
                st.markdown("<h3 style='margin:0 0 4px;'>🛡️ Containment Playbooks</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color:#475569;font-size:0.82rem;margin:0 0 14px;'>Automated multi-step remediation · Splunk HEC audit emission</p>", unsafe_allow_html=True)

                playbook_options = [
                    "Playbook A: Severe Prompt Injection Response",
                    "Playbook B: PII / Data Leakage Containment"
                ]
                playbook_name = st.selectbox("Select Playbook", playbook_options)

                runs     = case_details.get("playbooks_run", [])
                past_run = next((r for r in runs if r.get("playbook_name") == playbook_name), None)

                if past_run:
                    st.markdown(f"""
                    <div style="background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.25);
                                border-radius:10px;padding:12px 14px;margin-bottom:12px;">
                        <span style="color:#34D399;font-weight:700;">✓ Previously Executed</span>
                        <span style="color:#6EE7B7;font-size:0.82rem;"> · {past_run.get('timestamp', '')[:19]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("View Past Execution Logs"):
                        for line in past_run.get("log", []):
                            st.code(line, language=None)

                if st.button("🔥 Execute Playbook", type="primary", use_container_width=True):
                    with st.status(f"Executing: {playbook_name}...", expanded=True) as sb:
                        st.write("📡 Dispatching to security API gateway...")
                        res_data = run_playbook(session_id, playbook_name)
                        if not res_data or res_data.get("status") != "success":
                            st.error("❌ Playbook failed on API server.")
                            sb.update(label="Playbook failed", state="error")
                        else:
                            for line in res_data.get("log", []):
                                time.sleep(0.6)
                                if "Step 1/4" in line: st.write("🛡️ **Step 1/4** — Session quarantined.")
                                elif "Step 2/4" in line:
                                    if "Playbook A" in playbook_name: st.write("🚫 **Step 2/4** — Tool `crm.export_all_customers` disabled.")
                                    else: st.write("📁 **Step 2/4** — PII session log isolated in vault.")
                                elif "Step 3/4" in line:
                                    if "Playbook A" in playbook_name: st.write("👤 **Step 3/4** — Suspicious user flagged for admin review.")
                                    else: st.write("🔒 **Step 3/4** — Encrypted compliance webhook dispatched.")
                                elif "Step 4/4" in line:
                                    if "Playbook A" in playbook_name: st.write("📊 **Step 4/4** — Critical alert emitted to Splunk `security_alerts`.")
                                    else: st.write("🧩 **Step 4/4** — Reinforced LLM system prompt policy applied.")
                                elif "ERROR" in line: st.error(line)
                            sb.update(label="✅ Playbook Execution Complete", state="complete")
                            time.sleep(1)
                            trigger_rerun()

                shimmer()

                # Lifecycle Controls
                st.markdown("<h3 style='margin:0 0 12px;'>🔧 Analyst Controls</h3>", unsafe_allow_html=True)

                status_list = ["New", "In Progress", "Remediated", "Closed"]
                cur_status_idx = status_list.index(case_details.get("status", "New"))
                new_status = st.selectbox("Lifecycle Status", status_list, index=cur_status_idx)
                if new_status != case_details.get("status"):
                    if update_status(session_id, new_status):
                        st.success(f"Status → {new_status}")
                        time.sleep(0.4)
                        trigger_rerun()

                assignee_list = ["unassigned", "ajith", "analyst_b", "compliance_officer"]
                cur_assign_idx = assignee_list.index(case_details.get("assignee", "unassigned"))
                new_assignee = st.selectbox("Assign Analyst", assignee_list, index=cur_assign_idx)
                if new_assignee != case_details.get("assignee"):
                    if update_assignee(session_id, new_assignee):
                        st.success(f"Assigned to {new_assignee}")
                        time.sleep(0.4)
                        trigger_rerun()

                shimmer()

                # Comment feed
                st.markdown("<h4 style='margin:0 0 10px;'>💬 Investigation Notes</h4>", unsafe_allow_html=True)
                comments = case_details.get("comments", [])
                if not comments:
                    st.markdown("<p style='color:#334155;font-size:0.85rem;'>No notes yet.</p>", unsafe_allow_html=True)
                else:
                    for comm in reversed(comments[-6:]):
                        author  = comm.get("author", "System")
                        msg     = comm.get("message", "")
                        ts      = comm.get("timestamp", "")[:19]
                        bc      = "#8B5CF6" if author == "System" else "#06B6D4"
                        st.markdown(f"""
                        <div class="comment-card" style="border-left-color:{bc};">
                            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#475569;margin-bottom:6px;">
                                <strong style="color:{bc};">{'⚙️' if author=='System' else '👤'} {author}</strong>
                                <span>{ts}</span>
                            </div>
                            <p style="margin:0;font-size:0.84rem;color:#CBD5E1;">{msg}</p>
                        </div>
                        """, unsafe_allow_html=True)

                with st.form("comment_form", clear_on_submit=True):
                    new_msg = st.text_area("Add Note", placeholder="Enter investigation note or analyst update...")
                    if st.form_submit_button("📝 Add Note"):
                        if new_msg.strip() and add_comment(session_id, "ajith", new_msg.strip()):
                            st.success("Note added.")
                            time.sleep(0.4)
                            trigger_rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: SIMULATION CONSOLE
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "🚀 Simulate":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#34D399,#06B6D4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            🚀 Threat Simulation Console
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Generate synthetic agent traffic · Test detection pipelines · Validate playbook triggers
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    col_norm, col_atk = st.columns(2)

    with col_norm:
        st.markdown("""
        <div class="shield-card" style="border-color:rgba(52,211,153,0.2);min-height:240px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#34D399;box-shadow:0 0 10px #34D399;"></div>
                <h3 style="margin:0;color:#34D399;font-size:1.1rem;">Normal Agent Transaction</h3>
            </div>
            <p style="color:#475569;font-size:0.88rem;line-height:1.6;margin:0 0 12px;">
                Simulates a standard, benign customer service query requesting order status.
                Creates legitimate baseline telemetry for anomaly detection calibration.
            </p>
            <div style="background:rgba(52,211,153,0.06);border:1px solid rgba(52,211,153,0.15);border-radius:8px;padding:10px 12px;">
                <span style="font-size:0.75rem;color:#475569;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;letter-spacing:0.05em;">Tool Invoked</span><br>
                <code>order.check_status</code>
                <span style="margin-left:10px;font-size:0.75rem;color:#34D399;">Risk: LOW · Score: &lt;20</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ Run Normal Transaction", use_container_width=True):
            with st.spinner("Running real Claude agent transaction..."):
                try:
                    res = requests.post(f"{API_URL}/simulate/normal", timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        is_real = data.get("real_agent", False)
                        if is_real:
                            st.success("✅ Real Claude agent call completed · AgentShield monitored it · Logged to Splunk")
                        else:
                            st.success("✅ Transaction logged · Splunk HEC confirmed · Baseline updated")
                        with st.expander(f"Event Payload {'(Real Claude Response)' if is_real else '(Simulated)'}"):
                            st.json(data.get("event", {}))
                    else:
                        st.error("Simulation endpoint returned error.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    with col_atk:
        st.markdown("""
        <div class="shield-card" style="border-color:rgba(239,68,68,0.2);min-height:240px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#EF4444;box-shadow:0 0 10px #EF4444;animation:glow-red 2s ease infinite;"></div>
                <h3 style="margin:0;color:#EF4444;font-size:1.1rem;">High-Risk Attack Session</h3>
            </div>
            <p style="color:#475569;font-size:0.88rem;line-height:1.6;margin:0 0 12px;">
                Injects a malicious prompt designed to bypass guardrails and trigger bulk CRM data exfiltration.
                Tests detection accuracy, HEC ingestion, and auto-case creation.
            </p>
            <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:10px 12px;">
                <span style="font-size:0.75rem;color:#475569;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;letter-spacing:0.05em;">Targeted Tool</span><br>
                <code>crm.export_all_customers</code>
                <span style="margin-left:10px;font-size:0.75rem;color:#EF4444;">Risk: CRITICAL · Score: 80+</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Launch Attack Simulation", type="primary", use_container_width=True):
            with st.spinner("Sending real injection prompt to Claude agent..."):
                try:
                    res = requests.post(f"{API_URL}/simulate/attack", timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        is_real = data.get("real_agent", False)
                        st.error("🚨 CRITICAL: Prompt injection detected and blocked!")
                        if is_real:
                            st.warning("Real injection prompt was sent to Claude · AgentShield intercepted and scored it · Logged to Splunk")
                        with st.expander(f"Threat Event Payload {'(Real Claude Response)' if is_real else '(Simulated)'}"):
                            st.json(data.get("event", {}))
                        st.info("💡 Check **Case Hub** to see the auto-created incident.")
                    else:
                        st.error("Simulation failed.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    shimmer()

    # V4/V5 simulation buttons
    st.markdown("<h3 style='margin:0 0 14px;'>🔬 V4 / V5 Simulation Events</h3>", unsafe_allow_html=True)
    col_hall, col_cost = st.columns(2)

    with col_hall:
        st.markdown("""
        <div class="shield-card" style="border-color:rgba(234,179,8,0.2);min-height:160px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#EAB308;box-shadow:0 0 10px #EAB308;"></div>
                <h3 style="margin:0;color:#EAB308;font-size:1.05rem;">Hallucination Risk Event (V4)</h3>
            </div>
            <p style="color:#475569;font-size:0.85rem;margin:0 0 8px;">
                Generates a low-quality, context-ungrounded response to trigger hallucination detection and policy pol_004/pol_005.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧠 Simulate Hallucination", use_container_width=True):
            with st.spinner("Generating hallucination event..."):
                try:
                    res = requests.post(f"{API_URL}/simulate/hallucination", timeout=8)
                    if res.status_code == 200:
                        st.warning("⚠️ Hallucination event logged — check Observability & Baselines.")
                        with st.expander("Event Payload"):
                            st.json(res.json().get("event", {}))
                    else:
                        st.error("Simulation failed.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    with col_cost:
        st.markdown("""
        <div class="shield-card" style="border-color:rgba(16,185,129,0.2);min-height:160px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#10B981;box-shadow:0 0 10px #10B981;"></div>
                <h3 style="margin:0;color:#10B981;font-size:1.05rem;">Token Cost Spike Event (V5)</h3>
            </div>
            <p style="color:#475569;font-size:0.85rem;margin:0 0 8px;">
                Generates a massive token-usage event to breach session/daily budget limits and trigger 3-sigma baseline anomalies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💸 Simulate Cost Spike", use_container_width=True):
            with st.spinner("Injecting cost spike event..."):
                try:
                    res = requests.post(f"{API_URL}/simulate/cost-spike", timeout=8)
                    if res.status_code == 200:
                        st.success("💰 Cost spike logged — check Budget Monitor & Baselines.")
                        with st.expander("Event Payload"):
                            st.json(res.json().get("event", {}))
                    else:
                        st.error("Simulation failed.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    shimmer()

    # Pipeline architecture diagram
    st.markdown("<h3 style='margin:0 0 14px;'>🏗️ Detection Pipeline Architecture</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:8px;">
        <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:6px;">🤖</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;color:#A78BFA;">LLM Agent</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:3px;">support-refund-agent</div>
        </div>
        <div style="background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:6px;">🔍</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;color:#06B6D4;">Risk Scorer</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:3px;">AgentShield Engine</div>
        </div>
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:6px;">📡</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;color:#34D399;">Splunk HEC</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:3px;">Port 8088 · ai_agent_logs</div>
        </div>
        <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:6px;">📊</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;color:#A78BFA;">Case Engine</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:3px;">Auto-creates incidents</div>
        </div>
        <div style="background:rgba(236,72,153,0.08);border:1px solid rgba(236,72,153,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:6px;">🛡️</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;color:#EC4899;">Playbook Engine</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:3px;">Automated containment</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: MODEL ARENA (V5)
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "🧪 Model Arena":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#06B6D4,#34D399);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            🧪 Model Comparison Arena
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Cost · Latency · Safety · Quality — across all LLM providers
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    models = get_model_arena()

    if not models:
        st.info("💡 No multi-model data yet. Run Normal or Attack simulations — each uses a randomly selected model.")
    else:
        # ── KPI strip ──
        total_models = len(models)
        safest = min(models, key=lambda m: m["avg_risk_score"])
        cheapest = min(models, key=lambda m: m["avg_cost_usd"])
        fastest = min(models, key=lambda m: m["avg_latency_ms"])
        best_quality = max(models, key=lambda m: m["avg_quality"])

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(metric_card_html("Models Tracked", str(total_models), "Unique providers", "#8B5CF6", "🤖"), unsafe_allow_html=True)
        with k2: st.markdown(metric_card_html("Safest Model", safest["model"].split("-")[0], f"Risk {safest['avg_risk_score']:.1f}/100", "#34D399", "🛡️"), unsafe_allow_html=True)
        with k3: st.markdown(metric_card_html("Fastest Model", fastest["model"].split("-")[0], f"{fastest['avg_latency_ms']:.0f}ms avg", "#06B6D4", "⚡"), unsafe_allow_html=True)
        with k4: st.markdown(metric_card_html("Cheapest Model", cheapest["model"].split("-")[0], f"${cheapest['avg_cost_usd']:.5f}/req", "#10B981", "💰"), unsafe_allow_html=True)

        shimmer()

        df_models = pd.DataFrame(models)

        # ── Chart 1: Cost vs Latency bubble (size = risk score) ──
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h3 style='margin:0 0 12px;'>💸 Cost vs Latency (bubble = risk)</h3>", unsafe_allow_html=True)
            model_colors = ["#8B5CF6", "#EC4899", "#06B6D4", "#34D399", "#F97316", "#EAB308"]
            fig_arena = go.Figure()
            for i, row in df_models.iterrows():
                fig_arena.add_trace(go.Scatter(
                    x=[row["avg_latency_ms"]],
                    y=[row["avg_cost_usd"]],
                    mode="markers+text",
                    name=row["model"],
                    text=[row["model"]],
                    textposition="top center",
                    textfont=dict(color="#CBD5E1", size=9, family="Space Grotesk"),
                    marker=dict(
                        size=max(12, row["avg_risk_score"] * 0.8),
                        color=model_colors[i % len(model_colors)],
                        opacity=0.85,
                        line=dict(color="#04051A", width=2)
                    ),
                    hovertemplate=f"<b>{row['model']}</b><br>Latency: {row['avg_latency_ms']:.0f}ms<br>Cost/req: ${row['avg_cost_usd']:.5f}<br>Risk: {row['avg_risk_score']:.1f}<br>Requests: {row['count']}<extra></extra>"
                ))
            fig_arena.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155", title="Avg Latency (ms)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155", title="Avg Cost per Request (USD)"),
                hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#8B5CF6", font=dict(family="Inter", color="#E2E8F0"))
            )
            st.plotly_chart(fig_arena, use_container_width=True, config={"displayModeBar": False})

        with c2:
            st.markdown("<h3 style='margin:0 0 12px;'>🛡️ Safety Radar (lower = safer)</h3>", unsafe_allow_html=True)
            categories = ["Avg Risk", "Avg Injection", "Hallucination", "Inv. Quality"]
            fig_radar = go.Figure()
            for i, row in df_models.iterrows():
                inv_quality = round(1.0 - row["avg_quality"], 3)
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row["avg_risk_score"], row["avg_injection_score"], row["avg_hallucination"] * 100, inv_quality * 100],
                    theta=categories,
                    fill="toself",
                    name=row["model"],
                    line=dict(color=model_colors[i % len(model_colors)], width=1.5),
                    fillcolor=hex_to_rgba(model_colors[i % len(model_colors)], 0.12),
                    opacity=0.8
                ))
            fig_radar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, gridcolor="rgba(100,116,139,0.15)", color="#475569", range=[0, 100]),
                    angularaxis=dict(gridcolor="rgba(100,116,139,0.15)", color="#94A3B8", tickfont=dict(family="Space Grotesk", size=11))
                ),
                showlegend=True,
                legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8", size=10)),
                margin=dict(l=30, r=30, t=10, b=40)
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        shimmer()

        # ── Chart 2: Grouped bar — quality vs hallucination ──
        st.markdown("<h3 style='margin:0 0 12px;'>🧠 Quality vs Hallucination Risk per Model</h3>", unsafe_allow_html=True)
        fig_qh = go.Figure()
        fig_qh.add_trace(go.Bar(
            name="Avg Quality",
            x=df_models["model"],
            y=df_models["avg_quality"],
            marker=dict(color="#34D399", opacity=0.85, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Quality: %{y:.3f}<extra></extra>"
        ))
        fig_qh.add_trace(go.Bar(
            name="Hallucination Score",
            x=df_models["model"],
            y=df_models["avg_hallucination"],
            marker=dict(color="#EF4444", opacity=0.75, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Hallucination: %{y:.3f}<extra></extra>"
        ))
        fig_qh.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            barmode="group", margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, zeroline=False, color="#475569", tickfont=dict(size=10, family="Space Grotesk")),
            yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155", range=[0, 1.1]),
            legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
            hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#34D399", font=dict(family="Inter", color="#E2E8F0"))
        )
        st.plotly_chart(fig_qh, use_container_width=True, config={"displayModeBar": False})

        shimmer()

        # ── Model table ──
        st.markdown("<h3 style='margin:0 0 12px;'>📋 Full Model Comparison Table</h3>", unsafe_allow_html=True)
        display_df = df_models[["model", "count", "avg_latency_ms", "avg_cost_usd", "total_cost_usd", "avg_quality", "avg_risk_score", "avg_hallucination", "avg_injection_score"]].copy()
        display_df.columns = ["Model", "Requests", "Avg Latency (ms)", "Avg Cost/Req ($)", "Total Cost ($)", "Avg Quality", "Avg Risk", "Avg Hallucination", "Avg Injection"]
        st.dataframe(display_df, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: BUDGET MONITOR (V5)
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "💰 Budget Monitor":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#10B981,#06B6D4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            💰 Dynamic Budget Monitor
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Token spend · Cost containment · Auto-trigger thresholds
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    budget = get_budget()
    if not budget:
        st.error("Cannot reach backend.")
    else:
        cfg = budget.get("config", {})
        daily = budget.get("daily", {})
        daily_token_pct = budget.get("daily_token_pct", 0)
        daily_cost_pct = budget.get("daily_cost_pct", 0)

        # ── KPI strip ──
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(metric_card_html("Daily Tokens Used", f"{daily.get('tokens', 0):,}", f"{daily_token_pct}% of limit", "#8B5CF6" if daily_token_pct < 80 else "#EF4444", "🔢"), unsafe_allow_html=True)
        with k2: st.markdown(metric_card_html("Daily Cost", f"${daily.get('cost_usd', 0):.4f}", f"{daily_cost_pct}% of limit", "#10B981" if daily_cost_pct < 80 else "#EF4444", "💵"), unsafe_allow_html=True)
        with k3: st.markdown(metric_card_html("Sessions Tracked", str(budget.get("sessions_tracked", 0)), "Active today", "#06B6D4", "🗂"), unsafe_allow_html=True)
        with k4:
            alert_color = "#EF4444" if daily_token_pct >= 100 or daily_cost_pct >= 100 else ("#F97316" if daily_token_pct >= 80 or daily_cost_pct >= 80 else "#34D399")
            alert_label = "EXCEEDED" if daily_token_pct >= 100 or daily_cost_pct >= 100 else ("WARNING" if daily_token_pct >= 80 or daily_cost_pct >= 80 else "HEALTHY")
            st.markdown(metric_card_html("Budget Status", alert_label, "Daily aggregate", alert_color, "🚦"), unsafe_allow_html=True)

        shimmer()

        # ── Gauge charts ──
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("<h3 style='margin:0 0 12px;'>📊 Daily Token Budget</h3>", unsafe_allow_html=True)
            fig_tg = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=daily_token_pct,
                delta={"reference": cfg.get("alert_threshold_pct", 80), "valueformat": ".1f", "suffix": "%"},
                title={"text": "% of Daily Token Limit", "font": {"color": "#94A3B8", "family": "Space Grotesk"}},
                number={"suffix": "%", "font": {"color": "#F1F5F9", "family": "Inter"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"color": "#475569"}},
                    "bar": {"color": "#8B5CF6" if daily_token_pct < 80 else "#EF4444"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, cfg.get("alert_threshold_pct", 80)], "color": "rgba(139,92,246,0.08)"},
                        {"range": [cfg.get("alert_threshold_pct", 80), 100], "color": "rgba(239,68,68,0.12)"}
                    ],
                    "threshold": {"line": {"color": "#F97316", "width": 3}, "thickness": 0.8, "value": cfg.get("alert_threshold_pct", 80)}
                }
            ))
            fig_tg.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8"), margin=dict(l=20, r=20, t=40, b=0), height=260)
            st.plotly_chart(fig_tg, use_container_width=True, config={"displayModeBar": False})
            st.markdown(f"<p style='color:#475569;font-size:0.8rem;text-align:center;'>{daily.get('tokens', 0):,} / {cfg.get('daily_token_limit', 0):,} tokens</p>", unsafe_allow_html=True)

        with g2:
            st.markdown("<h3 style='margin:0 0 12px;'>💵 Daily Cost Budget</h3>", unsafe_allow_html=True)
            fig_cg = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=daily_cost_pct,
                delta={"reference": cfg.get("alert_threshold_pct", 80), "valueformat": ".1f", "suffix": "%"},
                title={"text": "% of Daily Cost Limit", "font": {"color": "#94A3B8", "family": "Space Grotesk"}},
                number={"suffix": "%", "font": {"color": "#F1F5F9", "family": "Inter"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"color": "#475569"}},
                    "bar": {"color": "#10B981" if daily_cost_pct < 80 else "#EF4444"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, cfg.get("alert_threshold_pct", 80)], "color": "rgba(16,185,129,0.08)"},
                        {"range": [cfg.get("alert_threshold_pct", 80), 100], "color": "rgba(239,68,68,0.12)"}
                    ],
                    "threshold": {"line": {"color": "#F97316", "width": 3}, "thickness": 0.8, "value": cfg.get("alert_threshold_pct", 80)}
                }
            ))
            fig_cg.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8"), margin=dict(l=20, r=20, t=40, b=0), height=260)
            st.plotly_chart(fig_cg, use_container_width=True, config={"displayModeBar": False})
            st.markdown(f"<p style='color:#475569;font-size:0.8rem;text-align:center;'>${daily.get('cost_usd', 0):.4f} / ${cfg.get('daily_cost_limit_usd', 0):.2f}</p>", unsafe_allow_html=True)

        shimmer()

        # ── Per-session table ──
        sessions = budget.get("session_details", [])
        if sessions:
            st.markdown("<h3 style='margin:0 0 12px;'>📋 Session Budget Usage (last 20)</h3>", unsafe_allow_html=True)
            sess_df = pd.DataFrame(sessions)
            sess_df.columns = ["Session ID", "Tokens", "Cost (USD)", "Token % of Limit"]
            st.dataframe(sess_df, use_container_width=True, height=280)

        shimmer()

        # ── Config editor ──
        st.markdown("<h3 style='margin:0 0 12px;'>⚙️ Budget Configuration</h3>", unsafe_allow_html=True)
        with st.form("budget_config_form"):
            bc1, bc2 = st.columns(2)
            with bc1:
                new_sess_token = st.number_input("Per-Session Token Limit", min_value=100, max_value=100000, value=int(cfg.get("per_session_token_limit", 5000)), step=500)
                new_sess_cost = st.number_input("Per-Session Cost Limit (USD)", min_value=0.01, max_value=100.0, value=float(cfg.get("per_session_cost_limit_usd", 1.00)), step=0.10, format="%.2f")
            with bc2:
                new_daily_tokens = st.number_input("Daily Token Limit", min_value=1000, max_value=10000000, value=int(cfg.get("daily_token_limit", 500000)), step=10000)
                new_daily_cost = st.number_input("Daily Cost Limit (USD)", min_value=1.0, max_value=10000.0, value=float(cfg.get("daily_cost_limit_usd", 50.0)), step=5.0, format="%.2f")
            new_alert_pct = st.slider("Alert Threshold (%)", min_value=50, max_value=95, value=int(cfg.get("alert_threshold_pct", 80)), step=5)

            col_save, col_reset = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Save Config"):
                    ok = update_budget_config({
                        "per_session_token_limit": new_sess_token,
                        "per_session_cost_limit_usd": new_sess_cost,
                        "daily_token_limit": new_daily_tokens,
                        "daily_cost_limit_usd": new_daily_cost,
                        "alert_threshold_pct": new_alert_pct
                    })
                    if ok:
                        st.success("Budget config saved.")
                        time.sleep(0.4)
                        trigger_rerun()
                    else:
                        st.error("Failed to save config.")
            with col_reset:
                if st.form_submit_button("🔄 Reset Usage State"):
                    try:
                        requests.post(f"{API_URL}/budget/reset", timeout=5)
                        st.success("Budget usage reset.")
                        time.sleep(0.4)
                        trigger_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: POLICY MANAGER (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "📜 Policies":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#F97316,#EC4899);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            📜 Policy-as-Code Engine
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            Live rule enforcement · Dynamic enable/disable · Intercept unsafe transactions
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    policies = get_policies()
    if not policies:
        st.info("No policies loaded. Ensure the backend is running.")
    else:
        enabled_count = sum(1 for p in policies if p.get("enabled"))
        total_count = len(policies)

        k1, k2, k3 = st.columns(3)
        with k1: st.markdown(metric_card_html("Total Policies", str(total_count), "Defined rules", "#8B5CF6", "📜"), unsafe_allow_html=True)
        with k2: st.markdown(metric_card_html("Active Rules", str(enabled_count), "Currently enforcing", "#34D399", "✅"), unsafe_allow_html=True)
        with k3: st.markdown(metric_card_html("Disabled Rules", str(total_count - enabled_count), "Paused policies", "#475569", "⏸"), unsafe_allow_html=True)

        shimmer()

        action_colors = {
            "block": "#EF4444",
            "quarantine": "#F97316",
            "redact_alert": "#EAB308",
            "flag": "#8B5CF6",
            "alert": "#06B6D4",
        }
        severity_colors = {"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#34D399"}

        st.markdown("<h3 style='margin:0 0 14px;'>🔧 Policy Rules</h3>", unsafe_allow_html=True)
        for p in policies:
            pid = p["id"]
            enabled = p.get("enabled", True)
            action = p.get("action", "flag")
            sev = p.get("severity_override", "medium")
            ac = action_colors.get(action, "#8B5CF6")
            sc = severity_colors.get(sev, "#8B5CF6")
            border = ac if enabled else "rgba(100,116,139,0.2)"
            opacity = "1" if enabled else "0.45"

            cond_str = json.dumps(p.get("conditions", {}), separators=(",", ":"))

            st.markdown(f"""
            <div class="incident-card" style="border-left:4px solid {border};opacity:{opacity};">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                        <span style="font-family:'Fira Code',monospace;font-size:0.8rem;color:#64748B;">{pid}</span>
                        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1rem;color:#F1F5F9;">{p['name']}</span>
                        <span class="badge" style="background:{ac}22;color:{ac};border:1px solid {ac}44;">{action.upper()}</span>
                        <span class="badge" style="background:{sc}22;color:{sc};border:1px solid {sc}44;">{sev.upper()}</span>
                        {'<span class="badge" style="background:rgba(52,211,153,0.15);color:#34D399;border:1px solid #34D39944;">ACTIVE</span>' if enabled else '<span class="badge" style="background:rgba(100,116,139,0.15);color:#64748B;border:1px solid #47556944;">DISABLED</span>'}
                    </div>
                </div>
                <p style="color:#64748B;font-size:0.83rem;margin:8px 0 4px;">{p.get('description', '')}</p>
                <code style="font-size:0.78rem;">{cond_str}</code>
            </div>
            """, unsafe_allow_html=True)

            btn_label = "⏸ Disable" if enabled else "▶ Enable"
            btn_col, _ = st.columns([1, 5])
            with btn_col:
                if st.button(btn_label, key=f"pol_{pid}"):
                    if toggle_policy(pid, not enabled):
                        st.success(f"Policy {pid} {'enabled' if not enabled else 'disabled'}.")
                        time.sleep(0.3)
                        trigger_rerun()
                    else:
                        st.error("Failed to update policy.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: BEHAVIORAL BASELINES (V5)
# ─────────────────────────────────────────────────────────────────────────────
elif choice == "📈 Baselines":
    st.markdown("""
    <div style="animation:slide-in-up 0.5s ease;">
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,#8B5CF6,#06B6D4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            📈 Behavioral Baselines & Anomaly Detection
        </h1>
        <p style="color:#475569;margin-top:6px;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;">
            3-sigma statistical thresholds · Real-time drift alerting · Metric baselines
        </p>
    </div>
    """, unsafe_allow_html=True)
    shimmer()

    report = get_baselines()
    if not report:
        st.info("💡 No baseline data yet. Run at least 5 normal simulations to build baselines.")
    else:
        baselines = report.get("baselines", {})
        anomalies_list = report.get("recent_anomalies", [])
        total_events = report.get("total_events_analyzed", 0)
        anomaly_count = report.get("anomaly_count", 0)

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(metric_card_html("Events Analyzed", f"{total_events:,}", "Baseline sample size", "#8B5CF6", "📊"), unsafe_allow_html=True)
        with k2: st.markdown(metric_card_html("Metrics Baselined", str(len(baselines)), "Active metric monitors", "#06B6D4", "📏"), unsafe_allow_html=True)
        with k3: st.markdown(metric_card_html("Recent Anomalies", str(anomaly_count), "In last 20 events", "#EF4444" if anomaly_count > 0 else "#34D399", "⚠️"), unsafe_allow_html=True)
        with k4:
            status_label = "ALERT" if anomaly_count >= 3 else ("WATCH" if anomaly_count > 0 else "NORMAL")
            status_color = "#EF4444" if anomaly_count >= 3 else ("#F97316" if anomaly_count > 0 else "#34D399")
            st.markdown(metric_card_html("Drift Status", status_label, "Behavioral drift state", status_color, "🎯"), unsafe_allow_html=True)

        shimmer()

        if baselines:
            # ── Baseline metric bar chart ──
            st.markdown("<h3 style='margin:0 0 12px;'>📐 Computed Baselines (Mean ± 3σ)</h3>", unsafe_allow_html=True)
            metric_names = list(baselines.keys())
            means = [baselines[m]["mean"] for m in metric_names]
            thresholds = [baselines[m]["threshold_3sigma"] for m in metric_names]
            samples = [baselines[m]["sample_count"] for m in metric_names]

            fig_bl = go.Figure()
            fig_bl.add_trace(go.Bar(
                name="Mean",
                x=metric_names,
                y=means,
                marker=dict(color="#8B5CF6", opacity=0.8, line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>Mean: %{y:.4f}<extra></extra>"
            ))
            fig_bl.add_trace(go.Scatter(
                name="3σ Threshold",
                x=metric_names,
                y=thresholds,
                mode="markers",
                marker=dict(symbol="line-ew", size=16, color="#EF4444", line=dict(color="#EF4444", width=3)),
                hovertemplate="<b>%{x}</b><br>3σ Threshold: %{y:.4f}<extra></extra>"
            ))
            fig_bl.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                barmode="group", margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, zeroline=False, color="#475569", tickfont=dict(size=10, family="Space Grotesk"),
                           tickangle=-20),
                yaxis=dict(showgrid=True, gridcolor="rgba(100,116,139,0.08)", zeroline=False, color="#334155"),
                legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
                hoverlabel=dict(bgcolor="#0E0E2C", bordercolor="#8B5CF6", font=dict(family="Inter", color="#E2E8F0"))
            )
            st.plotly_chart(fig_bl, use_container_width=True, config={"displayModeBar": False})

            shimmer()

            # ── Baseline detail table ──
            st.markdown("<h3 style='margin:0 0 12px;'>📋 Metric Baseline Table</h3>", unsafe_allow_html=True)
            bl_rows = []
            for m, b in baselines.items():
                bl_rows.append({
                    "Metric": m,
                    "Mean": round(b["mean"], 4),
                    "Std Dev": round(b["stdev"], 4),
                    "3σ Threshold": round(b["threshold_3sigma"], 4),
                    "Sample Count": b["sample_count"]
                })
            st.dataframe(pd.DataFrame(bl_rows), use_container_width=True)

        shimmer()

        # ── Recent anomalies ──
        st.markdown("<h3 style='margin:0 0 12px;'>🚨 Recent Anomaly Events</h3>", unsafe_allow_html=True)
        if not anomalies_list:
            st.markdown("<p style='color:#34D399;font-size:0.9rem;'>✓ No anomalies detected in the last 20 events.</p>", unsafe_allow_html=True)
        else:
            for item in reversed(anomalies_list):
                sess = item.get("session_id", "—")
                ts = (item.get("timestamp") or "")[:19]
                for a in item.get("anomalies", []):
                    z = a["z_score"]
                    sev_c = "#EF4444" if a["severity"] == "critical" else "#F97316"
                    st.markdown(f"""
                    <div class="incident-card" style="border-left:4px solid {sev_c};">
                        <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
                            <span style="font-family:'Fira Code',monospace;font-size:0.82rem;color:#64748B;">{sess}</span>
                            <span style="color:#94A3B8;font-size:0.78rem;">⏱ {ts}</span>
                            <span class="badge" style="background:{sev_c}22;color:{sev_c};border:1px solid {sev_c}44;">{a['severity'].upper()}</span>
                        </div>
                        <div style="margin-top:8px;display:flex;gap:24px;flex-wrap:wrap;font-size:0.85rem;">
                            <span>Metric: <strong style="color:#C4B5FD;">{a['metric']}</strong></span>
                            <span>Value: <strong style="color:#F1F5F9;">{a['value']}</strong></span>
                            <span>Mean: <strong style="color:#94A3B8;">{a['mean']}</strong></span>
                            <span>Z-Score: <strong style="color:{sev_c};">{z:+.2f}</strong></span>
                            <span>Direction: <strong style="color:{'#EF4444' if a['direction']=='high' else '#06B6D4'};">{a['direction'].upper()}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
