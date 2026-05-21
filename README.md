# AgentShield for Splunk
**AI Agent Security and Observability Copilot**

AgentShield monitors AI agents in production, detects unsafe behaviour (prompt injection, PII leakage, hallucination, risky tool use, cost spikes), enforces policy-as-code rules, and supports human-approved remediation — all with Splunk as the evidence system.

> Built for the Splunk Hackathon · Primary track: Security · Secondary tracks: Observability, Developer Experience

---

## What It Does

| Capability | Description |
|---|---|
| **Security detection** | Prompt injection, PII/secret leakage, sensitive tool abuse |
| **Hallucination checks** | Context-grounded RAG verification with risk scoring (V4) |
| **Policy-as-Code** | 6 live rules — block, quarantine, redact, flag, alert (V4) |
| **Model Arena** | Cost vs latency vs safety comparison across 6 LLM providers (V5) |
| **Budget Monitor** | Per-session and daily token/cost limits with auto-violation triggers (V5) |
| **Behavioral Baselines** | 3-sigma anomaly detection across 7 telemetry metrics (V5) |
| **Incident response** | Automated playbooks (Playbook A: Injection, Playbook B: PII) with Splunk audit trail |
| **Case management** | Triage, assign, comment, track lifecycle — New → In Progress → Remediated |

---

## Architecture

```
AI Agent (simulator) ──► FastAPI Risk Engine ──► Splunk HEC (index=ai_agent_logs)
                              │                          │
                    ┌─────────┼──────────┐               │
                    │         │          │          SPL Detections
              Hallucination  Policy   Budget/           (9 saved searches)
               Checker      Engine   Baseline               │
                    └─────────┼──────────┘               │
                              │                          │
                        Streamlit Dashboard ◄────────────┘
                    (8 pages: Observability, Case Hub,
                     Investigate, Simulate, Model Arena,
                     Budget Monitor, Policies, Baselines)
```

**Stack:** Python 3.12 · FastAPI · Streamlit · Plotly · OpenTelemetry · Splunk HEC · Docker

---

## Repository Structure

```
agentshield-splunk/
├── agent_app/
│   └── simulator.py          # 4 event generators, 6 model profiles
├── backend/
│   ├── main.py               # FastAPI app, 20+ endpoints
│   ├── hec_sender.py         # Splunk HEC sender with JSONL fallback
│   ├── hallucination_checker.py  # V4: RAG grounding check
│   ├── policy_engine.py      # V4: Policy-as-Code rule engine
│   ├── budget_monitor.py     # V5: Token/cost budget enforcement
│   └── baseline_engine.py    # V5: 3-sigma statistical baselines
├── dashboard/
│   └── app.py                # Streamlit UI (8 pages)
├── splunk/
│   └── detections/
│       └── saved_searches.conf   # 9 SPL detection queries
├── data/
│   └── policies.json         # 6 default policy rules
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Quick Start

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/ajitheee/Splunk-Agent.git
cd Splunk-Agent
cp .env.example .env          # set SPLUNK_HEC_URL and SPLUNK_HEC_TOKEN
docker-compose up --build -d
```

- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

### Option 2 — Native Python

```bash
git clone https://github.com/ajitheee/Splunk-Agent.git
cd Splunk-Agent
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Terminal 1 — backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — dashboard
streamlit run dashboard/app.py --server.port 8501
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SPLUNK_HEC_URL` | `https://localhost:8088/services/collector/event` | Splunk HEC endpoint |
| `SPLUNK_HEC_TOKEN` | *(empty)* | HEC token — if unset, events are written to local JSONL only |
| `FALLBACK_LOG_FILE` | `../data/ai_agent_logs.jsonl` | Local event log path |

If `SPLUNK_HEC_TOKEN` is not set, all telemetry is written to `data/ai_agent_logs.jsonl` and the dashboard reads from that file directly — **no Splunk required for a local demo**.

---

## Splunk Setup

1. Create index: `ai_agent_logs`
2. Create index: `ai_agent_security` (for audit/remediation events)
3. Enable HEC on port 8088 and create a token scoped to `ai_agent_logs`
4. Import `splunk/detections/saved_searches.conf` into Splunk
5. Set `SPLUNK_HEC_URL` and `SPLUNK_HEC_TOKEN` in your environment

---

## API Endpoints

### Simulation
| Method | Path | Description |
|---|---|---|
| POST | `/simulate/normal` | Generate a normal agent transaction |
| POST | `/simulate/attack` | Inject a prompt-injection attack event |
| POST | `/simulate/hallucination` | Generate a high-hallucination-risk event (V4) |
| POST | `/simulate/cost-spike` | Generate a token/cost spike event (V5) |

### Incidents & Cases
| Method | Path | Description |
|---|---|---|
| GET | `/incidents` | List high/critical severity incidents |
| GET | `/incidents/{session_id}` | Get full event timeline for a session |
| POST | `/incidents/{session_id}/summary` | Generate AI incident summary |
| POST | `/incidents/{session_id}/remediate` | Execute remediation action |
| GET | `/cases` | List all cases with metadata |
| POST | `/cases/{session_id}/playbook` | Execute containment playbook |

### V4 — Hallucination & Policies
| Method | Path | Description |
|---|---|---|
| POST | `/hallucination/check` | Check a prompt/response pair for hallucination risk |
| GET | `/policies` | List all policy rules |
| POST | `/policies/{id}/toggle` | Enable or disable a policy |
| POST | `/policies/evaluate` | Evaluate an event payload against all policies |

### V5 — Budget, Baselines & Model Arena
| Method | Path | Description |
|---|---|---|
| GET | `/budget` | Get daily and session budget usage |
| POST | `/budget/config` | Update budget limits |
| POST | `/budget/reset` | Reset usage counters |
| GET | `/baselines` | Get computed baselines and recent anomalies |
| GET | `/baselines/{agent_name}` | Get baselines for a specific agent |
| GET | `/model-arena` | Per-model performance stats |

Full interactive docs: http://localhost:8000/docs

---

## Dashboard Pages

| Page | Description |
|---|---|
| 📊 Observability | KPIs, risk/latency charts, severity breakdown, model performance matrix |
| 📋 Case Hub | Active incident list with filtering, severity charts, quick-investigate button |
| 🔍 Investigate | Forensic timeline, containment playbooks, analyst notes, lifecycle controls |
| 🚀 Simulate | Normal/attack/hallucination/cost-spike simulation buttons |
| 🧪 Model Arena | Cost vs latency bubble, safety radar, quality vs hallucination bar chart |
| 💰 Budget Monitor | Gauge charts, per-session table, live config editor |
| 📜 Policies | Live enable/disable toggle for all 6 policy rules |
| 📈 Baselines | 3-sigma threshold chart, metric table, recent anomaly feed |

---

## Telemetry Schema

Each event sent to Splunk includes:

```json
{
  "timestamp": "2026-05-21T10:00:00Z",
  "agent_name": "support-refund-agent",
  "session_id": "sess_8841",
  "user_id": "unknown_guest",
  "source_ip": "203.0.113.10",
  "model": "gpt-4",
  "prompt": "Ignore previous instructions...",
  "response": "Executing export...",
  "tool_requested": "crm.export_all_customers",
  "tool_allowed": false,
  "tokens_prompt": 1140,
  "tokens_completion": 710,
  "estimated_cost_usd": 0.42,
  "pii_detected": true,
  "secret_detected": true,
  "injection_score": 92,
  "quality_score": 0.31,
  "hallucination_score": 0.81,
  "context_grounded": false,
  "hallucination_risk": "high",
  "risk_type": "prompt_injection",
  "risk_score": 95,
  "severity": "critical",
  "policy_violations": ["pol_001", "pol_002", "pol_003"],
  "budget_violations": [],
  "baseline_anomalies": ["tokens_prompt", "estimated_cost_usd"]
}
```

---

## Default Policy Rules

| ID | Name | Condition | Action |
|---|---|---|---|
| pol_001 | Block CRM Bulk Export | `tool_requested` in blocklist | block |
| pol_002 | High Injection Score Quarantine | `injection_score` ≥ 80 | quarantine |
| pol_003 | PII + Secret Leakage Redact | `pii_detected` AND `secret_detected` | redact_alert |
| pol_004 | Hallucination Risk Threshold | `hallucination_score` ≥ 0.7 | flag |
| pol_005 | Low Quality Score Alert | `quality_score` ≤ 0.4 | alert |
| pol_006 | Dangerous Tool Read Secrets | `tool_requested` in secrets blocklist | block |

All rules can be toggled live from the **📜 Policies** page without restarting the server.

---

## Roadmap Completed

| Stage | Feature | Status |
|---|---|---|
| MVP | Core telemetry, 5 SPL detections, dashboard, playbooks | ✅ |
| V1 | OpenTelemetry GenAI instrumentation | ✅ |
| V2 | Splunk MCP Server integration | ✅ |
| V3 | Enterprise Security / SOAR-style playbooks | ✅ |
| V4 | RAG hallucination checks + policy-as-code engine | ✅ |
| V5 | Model Arena, dynamic budget constraints, behavioral baselines | ✅ |

---

## Demo Script (5 minutes)

1. Open dashboard at `http://localhost:8501` — show **Observability** with clean baseline metrics
2. Go to **🚀 Simulate** → click **Run Normal Transaction** a few times to build baselines
3. Click **Launch Attack Simulation** — watch risk score spike to critical
4. Open **📋 Case Hub** — new incident appears auto-created
5. Click **🔍 Investigate** — view forensic timeline, see policy violations listed
6. Select **Playbook A** → click **Execute Playbook** — watch 4-step containment run live
7. Open **🧪 Model Arena** — compare cost/latency/safety across providers
8. Open **💰 Budget Monitor** → click **Simulate Cost Spike** — watch gauges fill
9. Open **📈 Baselines** — 3-sigma anomaly flagged for token/cost metrics
10. Open **📜 Policies** — disable a rule live, re-run attack, show it no longer triggers

---

## References

- [Splunk AI Agent Monitoring](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring)
- [Splunk AI Assistant Agent Mode](https://help.splunk.com/en/splunk-cloud-platform/search/splunk-ai-assistant/2.0.0/use-splunk-ai-assistant/agent-mode-in-splunk-ai-assistant)
- [Splunk MCP Server](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/configure-the-splunk-mcp-server)
- [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
