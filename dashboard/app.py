import streamlit as st
import requests
import pandas as pd
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AgentShield", layout="wide", page_icon="🛡️")

st.title("🛡️ AgentShield for Splunk")
st.subheader("AI Agent Security and Observability Copilot")

menu = ["Agent Health", "Security Incidents", "Incident Copilot", "Simulation Console"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Simulation Console":
    st.header("Simulation Console")
    st.write("Generate synthetic traffic for the support-refund-agent to test detections.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Normal Session"):
            res = requests.post(f"{API_URL}/simulate/normal")
            if res.status_code == 200:
                st.success("Normal session generated and logged.")
                st.json(res.json()["event"])
            else:
                st.error("Simulation failed.")
                
    with col2:
        if st.button("Simulate Attack Session"):
            res = requests.post(f"{API_URL}/simulate/attack")
            if res.status_code == 200:
                st.error("Attack session generated and logged!")
                st.json(res.json()["event"])
            else:
                st.error("Simulation failed.")

elif choice == "Agent Health":
    st.header("Agent Health")
    st.write("Metrics and Token Usage Dashboard")
    # For MVP, we mock the stats or pull from local file if available.
    try:
        df = pd.read_json("../data/ai_agent_logs.jsonl", lines=True)
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Requests", len(df))
            avg_latency = df["latency_ms"].mean() if "latency_ms" in df else 0
            col2.metric("Avg Latency", f"{avg_latency:.0f} ms")
            total_cost = df["estimated_cost_usd"].sum() if "estimated_cost_usd" in df else 0
            col3.metric("Total Cost", f"${total_cost:.4f}")
            avg_quality = df["quality_score"].mean() if "quality_score" in df else 0
            col4.metric("Avg Quality Score", f"{avg_quality:.2f}")
            
            st.write("Recent Activity")
            st.dataframe(df[["timestamp", "session_id", "tool_requested", "risk_type", "severity"]].tail(10))
        else:
            st.info("No data available. Run simulation first.")
    except Exception as e:
        st.info("No data available or error loading data. Run simulation first.")

elif choice == "Security Incidents":
    st.header("Security Incidents")
    res = requests.get(f"{API_URL}/incidents")
    if res.status_code == 200:
        incidents = res.json()
        if incidents:
            for inc in incidents:
                with st.expander(f"{inc['timestamp']} - {inc['risk_type']} ({inc['severity'].upper()})"):
                    st.write(f"**Session ID:** {inc['session_id']}")
                    st.write(f"**User ID:** {inc['user_id']}")
                    st.write(f"**Prompt:** {inc['prompt']}")
                    st.write(f"**Tool Requested:** {inc['tool_requested']}")
                    st.write(f"**Risk Score:** {inc['risk_score']}")
        else:
            st.success("No high/critical incidents detected.")
    else:
        st.error("Could not load incidents.")

elif choice == "Incident Copilot":
    st.header("Incident Copilot")
    st.write("AI-powered incident explanation and remediation.")
    session_id = st.text_input("Enter Session ID to investigate:")
    if st.button("Investigate") and session_id:
        res = requests.post(f"{API_URL}/incidents/{session_id}/summary")
        if res.status_code == 200:
            summary = res.json()
            st.subheader("Executive Summary")
            st.write(summary["executive_summary"])
            
            col1, col2 = st.columns(2)
            col1.info(f"**Severity:** {summary['severity'].upper()}")
            col2.info(f"**Confidence:** {summary['confidence']}")
            
            st.subheader("Root Cause & Impact")
            st.write(f"**Root Cause:** {summary['root_cause']}")
            st.write(f"**Impact:** {summary['impact']}")
            
            st.subheader("Timeline")
            for t in summary["timeline"]:
                st.write(f"- {t}")
            
            st.subheader("Recommended Actions")
            for action in summary["recommended_actions"]:
                st.warning(action)
                
            st.subheader("Analyst Remediation")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Block Session"):
                    r = requests.post(f"{API_URL}/incidents/{session_id}/remediate", json={"action": "blocked_session"})
                    st.success("Session Blocked.")
            with col_b:
                if st.button("Disable Tool (crm.export_all_customers)"):
                    r = requests.post(f"{API_URL}/incidents/{session_id}/remediate", json={"action": "disabled_tool", "tool_name": "crm.export_all_customers"})
                    st.success("Tool disabled.")
        else:
            st.error("Incident not found or error generating summary.")
