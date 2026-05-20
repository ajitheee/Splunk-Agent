# AgentShield for Splunk

AgentShield is an AI Agent Security and Observability Copilot. It monitors AI agents in production, detects unsafe behavior such as prompt injection, PII leakage, risky tool use, hallucination risk, and token-cost spikes, then explains incidents in Splunk and supports human-approved remediation.

## Architecture

* **Backend**: FastAPI
* **Frontend**: Streamlit
* **Telemetry**: JSON logs ready for Splunk HEC

## Setup

You can run AgentShield either natively using Python or via Docker.

### Running Natively
1. Install dependencies: `pip install -r requirements.txt`
2. Start Backend: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
3. Start Dashboard: `streamlit run dashboard/app.py`

### Running via Docker
`docker-compose up --build -d`

## Splunk Integration
The `splunk/detections/saved_searches.conf` contains the SPL queries for detecting AI-agent risks.

## Demo Walkthrough
1. Open the Streamlit Dashboard.
2. Navigate to **Simulation Console** and simulate an attack session.
3. Check the **Security Incidents** page to view the flagged incident.
4. Go to **Incident Copilot**, enter the session ID, and run an AI investigation.
5. Apply the recommended remediation (e.g. Block Session, Disable Tool).
