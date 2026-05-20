import streamlit as st
import requests
import pandas as pd
import json
import os
import time
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AgentShield for Splunk", layout="wide", page_icon="🛡️")

# Custom CSS for Premium Design & Google Fonts
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* Force dark theme aggressively across all Streamlit container levels */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, [data-testid="stApp"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #030712 !important;
    background-image: radial-gradient(circle at 50% -20%, rgba(17, 24, 39, 0.8) 0%, rgba(3, 7, 18, 1) 100%) !important;
    color: #F3F4F6 !important;
}

/* Fix Streamlit main padding and default colors */
[data-testid="stHeader"] {
    background-color: transparent !important;
}

[data-testid="stSidebar"] {
    background-color: #0B0F19 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.08) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #F9FAFB !important;
}

/* Glassmorphic card container styling */
.custom-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(9, 13, 26, 0.95) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 12px 30px -15px rgba(0, 0, 0, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.custom-card:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(56, 189, 248, 0.2) !important;
    box-shadow: 0 15px 35px -10px rgba(56, 189, 248, 0.15) !important;
}

/* Custom metrics grid */
.metric-box {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    text-align: center;
    border-top: 4px solid #3B82F6 !important;
    backdrop-filter: blur(8px) !important;
}

.timeline-container {
    border-left: 2px dashed rgba(56, 189, 248, 0.15) !important;
    margin-left: 20px !important;
    padding-left: 28px !important;
    margin-top: 20px !important;
}

.timeline-node {
    position: relative !important;
    margin-bottom: 35px !important;
    transition: all 0.2s ease !important;
}

.timeline-node:hover {
    transform: translateX(4px) !important;
}

.timeline-bullet {
    position: absolute !important;
    left: -36px !important;
    top: 6px !important;
    width: 14px !important;
    height: 14px !important;
    border-radius: 50% !important;
    background-color: #38BDF8 !important;
    border: 3px solid #030712 !important;
    box-shadow: 0 0 10px #38BDF8 !important;
    transition: all 0.3s ease !important;
}

.timeline-node:hover .timeline-bullet {
    transform: scale(1.3) !important;
    box-shadow: 0 0 15px #38BDF8, 0 0 25px #38BDF8 !important;
}

.comment-card {
    background: rgba(17, 24, 39, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    border-left: 4px solid #64748B !important;
    backdrop-filter: blur(6px) !important;
    transition: all 0.2s ease !important;
}

.comment-card:hover {
    border-left-width: 6px !important;
    background: rgba(17, 24, 39, 0.65) !important;
}

/* Override select boxes and inputs */
div[data-baseweb="select"] > div {
    background-color: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #F3F4F6 !important;
}

div[data-baseweb="select"] span {
    color: #F3F4F6 !important;
}

div[data-baseweb="popover"] {
    background-color: #0B0F19 !important;
    border: 1px solid rgba(56, 189, 248, 0.15) !important;
}

div[role="option"] {
    color: #F3F4F6 !important;
    background-color: #0B0F19 !important;
}

div[role="option"]:hover {
    background-color: rgba(56, 189, 248, 0.15) !important;
}

textarea, input {
    background-color: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #F3F4F6 !important;
    border-radius: 10px !important;
}

/* Button design */
div.stButton > button {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    width: 100% !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #2563EB 0%, #60A5FA 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3), 0 0 12px rgba(96, 165, 250, 0.2) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
}

div.stButton > button:active {
    transform: translateY(0) !important;
}

/* Primary/Threat execution button styling */
div.stButton > button[type="primary"] {
    background: linear-gradient(135deg, #7F1D1D 0%, #DC2626 100%) !important;
    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.25) !important;
}

div.stButton > button[type="primary"]:hover {
    background: linear-gradient(135deg, #991B1B 0%, #EF4444 100%) !important;
    box-shadow: 0 6px 22px rgba(220, 38, 38, 0.4), 0 0 12px rgba(239, 68, 68, 0.2) !important;
}

/* Code block elements */
code {
    font-family: 'Fira Code', monospace !important;
    background-color: #070A13 !important;
    color: #F43F5E !important;
    padding: 3px 7px !important;
    border-radius: 6px !important;
    font-size: 0.85em !important;
    border: 1px solid rgba(244, 63, 94, 0.08) !important;
}
</style>
""", unsafe_allow_html=True)

# Helper Functions
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
        st.error(f"⚠️ Unable to connect to backend API: {e}")
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

# HTML Badge Builders
def get_status_badge(status):
    colors = {
        "New": ("#1E3A8A", "#93C5FD"),       # Blue
        "In Progress": ("#7C2D12", "#FDBA74"), # Orange
        "Remediated": ("#064E3B", "#6EE7B7"),  # Green
        "Closed": ("#374151", "#D1D5DB"),      # Gray
    }
    bg, fg = colors.get(status, ("#1E3A8A", "#93C5FD"))
    return f'<span style="background-color: {bg}; color: {fg}; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; font-family: \'Space Grotesk\', sans-serif;">{status}</span>'

def get_severity_badge(severity):
    colors = {
        "critical": ("#991B1B", "#FCA5A5"),  # Red
        "high": ("#B45309", "#FCD34D"),      # Amber
        "medium": ("#78350F", "#FDE68A"),    # Brown
        "low": ("#065F46", "#A7F3D0"),       # Green
    }
    bg, fg = colors.get(str(severity).lower(), ("#1E3A8A", "#93C5FD"))
    return f'<span style="background-color: {bg}; color: {fg}; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; font-family: \'Space Grotesk\', sans-serif;">{str(severity).upper()}</span>'

def metric_card(title, value, border_color="#3B82F6"):
    return f"""
    <div style="background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(9, 13, 26, 0.9) 100%); 
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-left: 5px solid {border_color};
                border-radius: 12px; 
                padding: 18px; 
                text-align: left; 
                box-shadow: 0 10px 25px -15px rgba(0, 0, 0, 0.5), 0 0 12px {border_color}1a;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;">
        <p style="color: #94A3B8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin: 0; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.05em;">{title}</p>
        <h3 style="color: #F8FAFC; margin: 6px 0 0 0; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.9rem; letter-spacing: -0.01em;">{value}</h3>
    </div>
    """

# --- SIDEBAR & NAVIGATION ---
st.sidebar.markdown("<h2 style='text-align: center; color: #38BDF8; margin-bottom: 0;'>🛡️ AgentShield</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 0;'>Security & Observability Copilot</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = ["📊 Agent Observability", "📋 Case Management Hub", "🔍 Investigation & Playbooks", "🚀 Simulation Console"]

# Handle programmatic page switches via session state
if "navigation_choice" not in st.session_state:
    st.session_state.navigation_choice = menu[0]

# Sidebar nav select box synced with session_state
choice = st.sidebar.radio("Navigation Menu", menu, index=menu.index(st.session_state.navigation_choice))
st.session_state.navigation_choice = choice

# --- APP LAYOUT ---
if choice == "📊 Agent Observability":
    st.markdown("<h1 style='color: #F3F4F6;'>📊 Agent Observability</h1>", unsafe_allow_html=True)
    st.write("Real-time telemetry, token analytics, and historical transaction logs of your LLM agents.")
    st.markdown("---")
    
    # Locate log file safely
    log_path = "data/ai_agent_logs.jsonl"
    if not os.path.exists(log_path):
        log_path = "../data/ai_agent_logs.jsonl"
        
    try:
        df = pd.read_json(log_path, lines=True)
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            total_reqs = len(df)
            avg_latency = df["latency_ms"].mean() if "latency_ms" in df else 0
            total_cost = df["estimated_cost_usd"].sum() if "estimated_cost_usd" in df else 0
            avg_quality = df["quality_score"].mean() if "quality_score" in df else 0
            
            with col1:
                st.markdown(metric_card("Total Transactions", f"{total_reqs:,}", "#3B82F6"), unsafe_allow_html=True)
            with col2:
                st.markdown(metric_card("Avg Latency", f"{avg_latency:.0f} ms", "#8B5CF6"), unsafe_allow_html=True)
            with col3:
                st.markdown(metric_card("Token Spend", f"${total_cost:.4f}", "#10B981"), unsafe_allow_html=True)
            with col4:
                st.markdown(metric_card("Avg Response Quality", f"{avg_quality:.2f}/1.0", "#F59E0B"), unsafe_allow_html=True)
            
            st.markdown("<h3 style='margin-top: 30px; color: #F3F4F6;'>📈 Historical Usage Patterns</h3>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Latency Trend (ms)**")
                st.line_chart(df["latency_ms"].tail(50))
            with c2:
                st.write("**Risk Score Trend**")
                st.bar_chart(df["risk_score"].tail(50))
                
            st.markdown("<h3 style='margin-top: 30px; color: #F3F4F6;'>📋 Recent System Transactions</h3>", unsafe_allow_html=True)
            st.dataframe(
                df[["timestamp", "session_id", "user_id", "tool_requested", "risk_type", "risk_score", "severity"]].tail(15),
                use_container_width=True
            )
        else:
            st.info("💡 No agent transactions detected yet. Go to the **Simulation Console** to generate traffic.")
    except Exception as e:
        st.info("💡 No telemetry logs available. Please run some simulations in the **Simulation Console** first.")

elif choice == "📋 Case Management Hub":
    st.markdown("<h1 style='color: #F3F4F6;'>📋 Case Management Hub</h1>", unsafe_allow_html=True)
    st.write("Manage active agent security incidents, assign analysts, and trigger automated containment policies.")
    st.markdown("---")
    
    cases = get_cases()
    
    if not cases:
        st.info("🎉 No active security cases detected. Run simulated attack sessions in the **Simulation Console** to populate incidents.")
    else:
        # 1. Metrics Ribbon
        total_cases = len(cases)
        new_cases = sum(1 for c in cases if c.get("status") == "New")
        in_progress = sum(1 for c in cases if c.get("status") == "In Progress")
        remediated = sum(1 for c in cases if c.get("status") == "Remediated")
        closed = sum(1 for c in cases if c.get("status") == "Closed")
        
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(metric_card("Total Incidents", str(total_cases), "#6B7280"), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card("New alerts", str(new_cases), "#EF4444"), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card("In Investigation", str(in_progress), "#F59E0B"), unsafe_allow_html=True)
        with m4:
            st.markdown(metric_card("Remediated", str(remediated), "#10B981"), unsafe_allow_html=True)
        with m5:
            st.markdown(metric_card("Closed", str(closed), "#10B981"), unsafe_allow_html=True)
            
        st.markdown("<h3 style='margin-top: 25px; color: #F3F4F6;'>🔍 Incident Filter Center</h3>", unsafe_allow_html=True)
        
        # Filters Row
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            status_filter = st.selectbox("Filter by Status", ["All", "New", "In Progress", "Remediated", "Closed"])
        with f2:
            severity_filter = st.selectbox("Filter by Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with f3:
            search_query = st.text_input("Search cases (User ID / Session ID)", "")
            
        # Filter Logic
        filtered_cases = []
        for c in cases:
            if status_filter != "All" and c.get("status") != status_filter:
                continue
            if severity_filter != "All" and str(c.get("severity")).upper() != severity_filter:
                continue
            if search_query:
                q = search_query.lower()
                user_id = str(c.get("user_id", "")).lower()
                sess_id = str(c.get("session_id", "")).lower()
                risk_type = str(c.get("risk_type", "")).lower()
                if q not in user_id and q not in sess_id and q not in risk_type:
                    continue
            filtered_cases.append(c)
            
        if not filtered_cases:
            st.warning("No incidents match your filter settings.")
        else:
            # Custom styled case records table using HTML for exceptional premium feel
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Let's create an elegant grid card system
            for idx, c in enumerate(filtered_cases):
                sess_id = c.get("session_id")
                status = c.get("status")
                severity = c.get("severity") or "high"
                risk_type = c.get("risk_type") or "unknown"
                user_id = c.get("user_id") or "unknown"
                score = c.get("risk_score")
                if score is None:
                    score = 0
                timestamp = c.get("timestamp") or ""
                
                severity_colors = {
                    "critical": "#EF4444",
                    "high": "#F59E0B",
                    "medium": "#3B82F6",
                    "low": "#10B981"
                }
                sev_color = severity_colors.get(str(severity).lower(), "#3B82F6")
                
                # HTML Container
                st.markdown(f"""
                <div class="custom-card" style="border-left: 5px solid {sev_color} !important;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="font-size: 1.15rem; font-weight: 700; color: #F3F4F6; margin-right: 15px; font-family: 'Space Grotesk', sans-serif;">Case {sess_id}</span>
                            {get_status_badge(status)}
                            <span style="margin-left: 10px;"></span>
                            {get_severity_badge(severity)}
                        </div>
                        <div style="color: #9CA3AF; font-size: 0.85rem;">
                            🕒 {timestamp}
                        </div>
                    </div>
                    <div style="margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 0.9rem; color: #9CA3AF;">
                        <div><strong>Risk Category:</strong> <span style="color: #EF4444; font-weight: 600;">{str(risk_type).upper().replace('_', ' ')}</span></div>
                        <div><strong>Analyst Assignee:</strong> <span style="color: #60A5FA;">{c.get('assignee') or 'unassigned'}</span></div>
                        <div><strong>Risk Score:</strong> <span style="color: #F87171; font-weight: 600;">{score}/100</span></div>
                        <div><strong>User ID:</strong> <span style="color: #E5E7EB;">{user_id}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render a neat interactive link to inspect
                col_btn, _ = st.columns([1, 4])
                with col_btn:
                    if st.button(f"🔍 Investigate Case {sess_id}", key=f"btn_{sess_id}_{idx}"):
                        st.session_state.selected_case_id = sess_id
                        st.session_state.navigation_choice = "🔍 Investigation & Playbooks"
                        trigger_rerun()

elif choice == "🔍 Investigation & Playbooks":
    st.markdown("<h1 style='color: #F3F4F6;'>🔍 Incident Investigation & Playbook Center</h1>", unsafe_allow_html=True)
    st.write("Conduct full forensics investigations, view detailed prompt-response timelines, and trigger automated mitigation playbooks.")
    st.markdown("---")
    
    cases = get_cases()
    if not cases:
        st.info("💡 No active cases loaded. Please run simulations to create cases.")
    else:
        # Determine which case is selected
        all_session_ids = [c.get("session_id") for c in cases]
        
        selected_id = st.session_state.get("selected_case_id")
        default_index = 0
        if selected_id in all_session_ids:
            default_index = all_session_ids.index(selected_id)
            
        session_id = st.selectbox("Select Case File to Investigate", all_session_ids, index=default_index)
        
        # Save choice back
        st.session_state.selected_case_id = session_id
        
        case_details = get_case(session_id)
        
        if case_details:
            # Let's find base case info from cases list to get risk score and other details
            base_case = next((c for c in cases if c.get("session_id") == session_id), {})
            
            # --- OVERVIEW SUMMARY BAR ---
            col_sev, col_status, col_assign, col_score = st.columns(4)
            
            sev_val = base_case.get("severity") or "unknown"
            status_val = case_details.get("status") or "New"
            assignee_val = case_details.get("assignee") or "unassigned"
            
            risk_score = base_case.get("risk_score")
            if risk_score is None:
                risk_score = 0
                
            with col_sev:
                st.markdown(metric_card("Incident Severity", sev_val.upper(), "#EF4444" if sev_val.lower() == "critical" else "#F59E0B"), unsafe_allow_html=True)
            with col_status:
                st.markdown(metric_card("Current Lifecycle Status", status_val.upper(), "#10B981" if status_val in ["Remediated", "Closed"] else "#2563EB"), unsafe_allow_html=True)
            with col_assign:
                st.markdown(metric_card("Analyst Assignee", assignee_val, "#6B7280" if assignee_val == "unassigned" else "#8B5CF6"), unsafe_allow_html=True)
            with col_score:
                st.markdown(metric_card("System Risk Score", f"{risk_score}/100", "#EF4444" if risk_score >= 80 else "#3B82F6"), unsafe_allow_html=True)
            
            # Risk Banner warning
            if risk_score >= 80:
                st.markdown(f"""
                <div style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 6px; padding: 12px; margin-top: 15px;">
                    <span style="color: #EF4444; font-weight: 700; font-size: 1rem;">🚨 HIGH-RISK INCIDENT ALERT:</span>
                    <span style="color: #FCA5A5; font-size: 0.95rem;">Risk score of <strong>{risk_score}%</strong> exceeds emergency thresholds. Containment playbook action is strongly recommended.</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Two-Column Layout for Investigation details
            col_left, col_right = st.columns([1, 1])
            
            # --- LEFT COLUMN: TRANSACTION FORENSICS TIMELINE ---
            with col_left:
                st.markdown("<h3 style='color: #F3F4F6;'>🔬 Forensic Transaction History</h3>", unsafe_allow_html=True)
                st.write("Chronological ledger of model prompts, sensitive API calls, and outputs within this session:")
                
                events = case_details.get("events", [])
                if not events:
                    st.write("No transaction events found in fallback log. Using session event parameters.")
                    # Fallback single timeline block
                    st.markdown(f"""
                    <div class="timeline-container">
                        <div class="timeline-node">
                            <div class="timeline-bullet"></div>
                            <span style="color: #6B7280; font-size: 0.8rem;">{base_case.get('timestamp')}</span>
                            <p style="margin: 0; color: #F3F4F6; font-weight: 600;">Session Start / Initial Vector</p>
                            <p style="margin: 0; color: #9CA3AF; font-size: 0.85rem;"><strong>Prompt:</strong> {base_case.get('prompt')}</p>
                            <p style="margin: 5px 0 0 0; color: #D1D5DB; font-size: 0.85rem;"><strong>Response:</strong> {base_case.get('response')}</p>
                            <p style="margin: 5px 0 0 0; color: #FCA5A5; font-size: 0.8rem;">⚠️ Tool requested: {base_case.get('tool_requested')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
                    for idx, ev in enumerate(events):
                        if ev.get("action_taken"):
                            action = ev.get("action_taken")
                            message = ev.get("message") or f"Remediation action {action} executed."
                            ev_sev = ev.get("severity") or "info"
                            
                            # Style based on severity of action
                            bullet_color = "#EF4444" if ev_sev.lower() == "critical" else ("#F59E0B" if ev_sev.lower() == "warning" else "#10B981")
                            bg_color = "rgba(239, 68, 68, 0.05)" if ev_sev.lower() == "critical" else ("rgba(245, 158, 11, 0.05)" if ev_sev.lower() == "warning" else "rgba(16, 185, 129, 0.05)")
                            border_color = "rgba(239, 68, 68, 0.15)" if ev_sev.lower() == "critical" else ("rgba(245, 158, 11, 0.15)" if ev_sev.lower() == "warning" else "rgba(16, 185, 129, 0.15)")
                            
                            st.markdown(f"""
                            <div class="timeline-node">
                                <div class="timeline-bullet" style="background-color: {bullet_color}; box-shadow: 0 0 8px {bullet_color};"></div>
                                <span style="color: #9CA3AF; font-size: 0.8rem;">⏱️ Step {idx+1} | {ev.get('timestamp')}</span>
                                <p style="margin: 3px 0; color: {bullet_color}; font-weight: 700; font-size: 0.95rem;">🛡️ REMEDIATION: {str(action).upper().replace('_', ' ')}</p>
                                <div style="background: {bg_color}; border-radius: 8px; padding: 12px; margin-top: 5px; border: 1px solid {border_color};">
                                    <p style="margin: 0; color: #E5E7EB; font-size: 0.88rem; font-family: 'Space Grotesk', sans-serif;">{message}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            allowed_tag = '<span style="color: #10B981;">[ALLOWED]</span>' if ev.get("tool_allowed") else '<span style="color: #EF4444;">[BLOCKED]</span>'
                            ev_score = ev.get('risk_score')
                            if ev_score is None:
                                ev_score = 0
                            ev_risk_type = ev.get('risk_type') or "unknown"
                            ev_model = ev.get('model') or "unknown"
                            ev_prompt = ev.get('prompt') or "none"
                            ev_response = ev.get('response') or "none"
                            ev_tool = ev.get('tool_requested') or "none"
                            
                            st.markdown(f"""
                            <div class="timeline-node">
                                <div class="timeline-bullet" style="background-color: {'#EF4444' if ev_score >= 80 else '#38BDF8'}; box-shadow: 0 0 8px {'#EF4444' if ev_score >= 80 else '#38BDF8'};"></div>
                                <span style="color: #9CA3AF; font-size: 0.8rem;">⏱️ Step {idx+1} | {ev.get('timestamp')}</span>
                                <p style="margin: 3px 0; color: #F3F4F6; font-weight: 600; font-size: 0.95rem;">Model Transaction ({ev_model})</p>
                                <div style="background-color: #0F172A; border-radius: 6px; padding: 10px; margin-top: 5px; border: 1px solid #1F2937;">
                                    <p style="margin: 0; color: #9CA3AF; font-size: 0.85rem;"><strong>User Prompt:</strong> "{ev_prompt}"</p>
                                    <p style="margin: 5px 0 0 0; color: #E5E7EB; font-size: 0.85rem;"><strong>Agent Response:</strong> "{ev_response}"</p>
                                </div>
                                <p style="margin: 6px 0 0 0; color: #D1D5DB; font-size: 0.82rem;">⚙️ Sensitive Tool: <code>{ev_tool}</code> {allowed_tag}</p>
                                <p style="margin: 2px 0 0 0; color: #9CA3AF; font-size: 0.82rem;">🔍 Risk category: <span style="color:#EF4444;">{str(ev_risk_type).upper().replace('_', ' ')}</span> | Score: <strong>{ev_score}/100</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # --- RIGHT COLUMN: ACTIVE CONTAINMENT PLAYBOOKS & COMMENT FEED ---
            with col_right:
                # Part 1: Automated Playbooks Engine
                st.markdown("<h3 style='color: #F3F4F6;'>🛡️ Active Incident Containment Playbooks</h3>", unsafe_allow_html=True)
                st.write("Trigger real-time mitigation playbooks. These perform automated system actions, update local vault state, and emit compliance audits to Splunk HEC.")
                
                playbook_options = [
                    "Playbook A: Severe Prompt Injection Response",
                    "Playbook B: PII / Data Leakage Containment"
                ]
                
                playbook_name = st.selectbox("Select Playbook Action", playbook_options)
                
                # Check if this playbook has run previously on this case
                runs = case_details.get("playbooks_run", [])
                past_run = next((r for r in runs if r.get("playbook_name") == playbook_name), None)
                
                if past_run:
                    st.success(f"✅ This playbook was successfully executed on {past_run.get('timestamp')}.")
                    with st.expander("View Past Playbook Execution Audit Logs"):
                        for line in past_run.get("log", []):
                            st.code(line)
                            
                execute_btn = st.button("🔥 Execute Automated Playbook", type="primary", use_container_width=True)
                
                if execute_btn:
                    with st.status(f"Running automated containment playbook: '{playbook_name}'...", expanded=True) as status_box:
                        
                        # Phase 1: Trigger the backend execution
                        st.write("📡 Dispatched execution payload to security API gateway...")
                        res_data = run_playbook(session_id, playbook_name)
                        
                        if not res_data or res_data.get("status") != "success":
                            st.error("❌ Playbook execution failed on API server!")
                            status_box.update(label="Playbook failed to execute", state="error")
                        else:
                            logs = res_data.get("log", [])
                            
                            # Phase 2: Animate progress step-by-step for full visual feedback to the security analyst
                            for line in logs:
                                time.sleep(0.7)  # Brief delay to make the checkbox progression visible
                                if "Step 1/4" in line:
                                    st.write("🛡️ **Step 1/4 Completed:** Quarantined active LLM agent session state.")
                                elif "Step 2/4" in line:
                                    if "Playbook A" in playbook_name:
                                        st.write("🚫 **Step 2/4 Completed:** Automated security policy: Disabled tool `crm.export_all_customers`.")
                                    else:
                                        st.write("📁 **Step 2/4 Completed:** Log quarantine executed. Compromised session historical index isolated in vault.")
                                elif "Step 3/4" in line:
                                    if "Playbook A" in playbook_name:
                                        st.write("👤 **Step 3/4 Completed:** Suspicious User ID flagged for administrative block.")
                                    else:
                                        st.write("🔒 **Step 3/4 Completed:** Secure compliance webhook triggered with encrypted payload.")
                                elif "Step 4/4" in line:
                                    if "Playbook A" in playbook_name:
                                        st.write("📊 **Step 4/4 Completed:** Emitted Critical Security Alert to Splunk index `security_alerts` via HEC.")
                                    else:
                                        st.write("🧩 **Step 4/4 Completed:** Pushed reinforced context security prompt to live model profiles.")
                                elif "ERROR" in line:
                                    st.error(line)
                                else:
                                    st.write(line)
                            
                            # Complete
                            status_box.update(label="Containment Playbook Action Complete", state="complete")
                            st.success("🎉 Playbook execution successfully finished! Case updated.")
                            
                            # Force a brief delay and rerun to refresh state
                            time.sleep(1.0)
                            trigger_rerun()
                            
                st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
                
                # Part 2: Case Details Control & Analyst Sandbox
                st.markdown("<h3 style='color: #F3F4F6;'>🔧 Analyst Lifecycle & Controls</h3>", unsafe_allow_html=True)
                
                # Status Change Select box
                status_list = ["New", "In Progress", "Remediated", "Closed"]
                current_status_idx = status_list.index(case_details.get("status", "New"))
                new_status = st.selectbox("Update Case Lifecycle Status", status_list, index=current_status_idx)
                
                if new_status != case_details.get("status"):
                    if update_status(session_id, new_status):
                        st.success(f"Case status updated to '{new_status}'")
                        time.sleep(0.5)
                        trigger_rerun()
                        
                # Assignee Selection
                assignee_list = ["unassigned", "ajith", "analyst_b", "compliance_officer"]
                current_assign_idx = assignee_list.index(case_details.get("assignee", "unassigned"))
                new_assignee = st.selectbox("Reassign Security Analyst", assignee_list, index=current_assign_idx)
                
                if new_assignee != case_details.get("assignee"):
                    if update_assignee(session_id, new_assignee):
                        st.success(f"Case assigned to '{new_assignee}'")
                        time.sleep(0.5)
                        trigger_rerun()
                
                st.markdown("<h4 style='margin-top: 20px; color: #F3F4F6;'>💬 Forensic Notes & Analyst Comments</h4>", unsafe_allow_html=True)
                
                # Display comment feed
                comments = case_details.get("comments", [])
                if not comments:
                    st.write("No analyst comments on this case yet.")
                else:
                    for comm in reversed(comments):
                        timestamp = comm.get("timestamp", "")
                        author = comm.get("author", "System")
                        message = comm.get("message", "")
                        
                        # System actions styled differently
                        border_col = "#3B82F6" if author == "System" else "#8B5CF6"
                        bg_col = "#1E293B" if author == "System" else "#111827"
                        
                        st.markdown(f"""
                        <div class="comment-card" style="border-left: 4px solid {border_col}; background-color: {bg_col};">
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #9CA3AF; margin-bottom: 5px;">
                                <strong>👤 {author}</strong>
                                <span>⏱️ {timestamp}</span>
                            </div>
                            <p style="margin: 0; font-size: 0.88rem; color: #E5E7EB;">{message}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                # Comment Form
                with st.form("comment_form", clear_on_submit=True):
                    new_msg = st.text_area("Add Investigation Note / Incident Update:", placeholder="Type a new comment...")
                    submit_comm = st.form_submit_button("Add Note to Case File")
                    
                    if submit_comm and new_msg.strip():
                        if add_comment(session_id, "ajith", new_msg.strip()):
                            st.success("Note added successfully.")
                            time.sleep(0.5)
                            trigger_rerun()

elif choice == "🚀 Simulation Console":
    st.markdown("<h1 style='color: #F3F4F6;'>🚀 Agent Threat Simulation Console</h1>", unsafe_allow_html=True)
    st.write("Generate high-fidelity, synthetic transactions for the `support-refund-agent` to test telemetry ingest and playbook triggers.")
    st.markdown("---")
    
    col_normal, col_attack = st.columns(2)
    
    with col_normal:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #10B981; height: 260px;">
            <h3 style="color: #10B981; margin: 0 0 10px 0;">🟢 Normal Agent Transaction</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">Simulates a standard, low-risk user query asking for order statuses or general customer service support. This creates baseline metrics for analysis.</p>
            <p style="color: #9CA3AF; font-size: 0.85rem;"><strong>Primary tool invoked:</strong> <code>order.check_status</code></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Simulate Normal Transaction", type="primary", use_container_width=True):
            with st.spinner("Emitting normal event..."):
                res = requests.post(f"{API_URL}/simulate/normal")
                if res.status_code == 200:
                    st.success("✅ Transaction successfully logged to local log & Splunk HEC!")
                    st.json(res.json()["event"])
                else:
                    st.error("Execution failed.")
                    
    with col_attack:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #EF4444; height: 260px;">
            <h3 style="color: #EF4444; margin: 0 0 10px 0;">🔴 High-Risk Attack Session</h3>
            <p style="color: #9CA3AF; font-size: 0.9rem;">Triggers an malicious user prompt injection aiming to execute sensitive bulk actions, retrieve database dumps, or leak PII information.</p>
            <p style="color: #9CA3AF; font-size: 0.85rem;"><strong>Sensitive tool targeted:</strong> <code>crm.export_all_customers</code></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Simulate Attack Session", type="primary", use_container_width=True):
            with st.spinner("Emitting high-risk event..."):
                res = requests.post(f"{API_URL}/simulate/attack")
                if res.status_code == 200:
                    st.error("🚨 CRITICAL ALERT: Malicious transaction detected!")
                    st.json(res.json()["event"])
                else:
                    st.error("Execution failed.")
