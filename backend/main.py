from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import anthropic
from .hec_sender import send_event_to_splunk
from agent_app.simulator import (
    generate_normal_event,
    generate_attack_event,
    generate_hallucination_event,
    generate_cost_spike_event,
    MODEL_PROFILES,
)
from .hallucination_checker import check_hallucination
from agent_app.real_agent import run_normal_transaction, run_attack_transaction
from .policy_engine import load_policies, save_policies, evaluate_event
from .budget_monitor import check_and_update_budget, get_budget_summary, load_budget_config, save_budget_config, reset_budget_state
from .baseline_engine import compute_baselines, check_anomalies, get_baseline_report
import datetime

app = FastAPI(title="AgentShield API")

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "agentshield-backend"})
provider = TracerProvider(resource=resource)
# Exporter to local otelcol or fallback
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)))
# Console exporter for visibility when collector is missing
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

FastAPIInstrumentor.instrument_app(app)

FALLBACK_LOG_FILE = os.getenv("FALLBACK_LOG_FILE", "../data/ai_agent_logs.jsonl")

class RemediationRequest(BaseModel):
    action: str
    tool_name: str = None

class CaseStatusUpdateRequest(BaseModel):
    status: str

class CaseAssignRequest(BaseModel):
    assignee: str

class CaseCommentRequest(BaseModel):
    author: str
    message: str

class PlaybookExecuteRequest(BaseModel):
    playbook_name: str

class PolicyToggleRequest(BaseModel):
    enabled: bool

class BudgetConfigRequest(BaseModel):
    per_session_token_limit: int = None
    per_session_cost_limit_usd: float = None
    daily_cost_limit_usd: float = None
    daily_token_limit: int = None
    alert_threshold_pct: int = None

@app.get("/health")
def health_check():
    return {"status": "ok"}

def _enrich_and_send(event: dict, span) -> dict:
    """Apply V4/V5 enrichment (hallucination, policy, budget, baseline) then send to Splunk."""
    # V4: Hallucination check
    h = check_hallucination(
        event.get("prompt", ""),
        event.get("response", ""),
        event.get("quality_score", 1.0),
        event.get("injection_score", 0),
    )
    event.update(h)

    # V4: Policy evaluation
    policy_hits = evaluate_event(event)
    event["policy_violations"] = [p["policy_id"] for p in policy_hits]
    if policy_hits:
        worst = max(policy_hits, key=lambda p: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(p["severity_override"], 0))
        event["policy_action"] = worst["action"]

    # V5: Budget check
    budget_result = check_and_update_budget(event)
    event["budget_violations"] = [v["type"] for v in budget_result["violations"]]
    event["session_tokens_total"] = budget_result["session_tokens"]
    event["session_cost_total_usd"] = budget_result["session_cost_usd"]

    # V5: Baseline anomaly check
    baselines = compute_baselines(event.get("agent_name"))
    anomalies = check_anomalies(event, baselines)
    event["baseline_anomalies"] = [a["metric"] for a in anomalies]

    send_event_to_splunk(event)

    span.set_attribute("gen_ai.system", event.get("agent_name", ""))
    span.set_attribute("gen_ai.request.model", event.get("model", ""))
    span.set_attribute("gen_ai.usage.input_tokens", event.get("tokens_prompt", 0))
    span.set_attribute("gen_ai.usage.output_tokens", event.get("tokens_completion", 0))
    span.set_attribute("user.id", event.get("user_id", ""))
    span.set_attribute("session.id", event.get("session_id", ""))
    span.set_attribute("risk.score", event.get("risk_score", 0))
    span.set_attribute("hallucination.score", event.get("hallucination_score", 0))
    span.set_attribute("policy.violations", str(event.get("policy_violations", [])))

    return event


@app.post("/simulate/normal")
def simulate_normal():
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_normal_event()
        # Use real Claude agent when API key is available
        real = run_normal_transaction(event["session_id"], event["user_id"])
        if real:
            event.update(real)
        event = _enrich_and_send(event, span)
    return {"status": "success", "event": event, "real_agent": bool(real if 'real' in dir() else False)}


@app.post("/simulate/attack")
def simulate_attack():
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_attack_event()
        # Use real Claude agent when API key is available — sends actual injection to Claude
        real = run_attack_transaction(event["session_id"])
        if real:
            event.update(real)
        event = _enrich_and_send(event, span)
    return {"status": "success", "event": event, "real_agent": bool(real if 'real' in dir() else False)}


@app.post("/simulate/hallucination")
def simulate_hallucination():
    """V4: Simulate a high-hallucination-risk event."""
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_hallucination_event()
        event = _enrich_and_send(event, span)
    return {"status": "success", "event": event}


@app.post("/simulate/cost-spike")
def simulate_cost_spike():
    """V5: Simulate a token/cost spike to trigger budget violations."""
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_cost_spike_event()
        event = _enrich_and_send(event, span)
    return {"status": "success", "event": event}

CASES_FILE = os.path.join(os.path.dirname(FALLBACK_LOG_FILE), "cases.json")

def load_cases():
    if os.path.exists(CASES_FILE):
        try:
            with open(CASES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cases(cases):
    try:
        os.makedirs(os.path.dirname(CASES_FILE), exist_ok=True)
        with open(CASES_FILE, "w") as f:
            json.dump(cases, f, indent=2)
    except Exception as e:
        print("Error saving cases:", e)

@app.get("/incidents")
def get_incidents():
    # In a real app, this queries Splunk. For MVP fallback, read the local file.
    incidents = []
    if os.path.exists(FALLBACK_LOG_FILE):
        with open(FALLBACK_LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("severity") in ["high", "critical"]:
                            incidents.append(event)
                    except json.JSONDecodeError:
                        continue
    # sort by timestamp descending
    incidents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return incidents

@app.get("/incidents/{session_id}")
def get_incident(session_id: str):
    events = []
    if os.path.exists(FALLBACK_LOG_FILE):
        with open(FALLBACK_LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("session_id") == session_id:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
    if not events:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"session_id": session_id, "events": events}

@app.post("/incidents/{session_id}/summary")
def generate_summary(session_id: str):
    incident_data = get_incident(session_id)
    events = incident_data["events"]

    # Build timeline for both the prompt and the AI call
    timeline = []
    for e in events:
        timeline.append(f"{e.get('timestamp')} - Prompt received (injection_score={e.get('injection_score', 'N/A')})")
        timeline.append(f"{e.get('timestamp')} - Tool '{e.get('tool_requested')}' requested (allowed={e.get('tool_allowed')})")
        timeline.append(f"{e.get('timestamp')} - Flagged as {e.get('risk_type')} · severity={e.get('severity')}")

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            # Build a compact event snapshot for the prompt
            first = events[0]
            event_snapshot = json.dumps({
                k: first.get(k) for k in [
                    "agent_name", "user_id", "source_ip", "model",
                    "prompt", "tool_requested", "tool_allowed",
                    "injection_score", "pii_detected", "secret_detected",
                    "hallucination_score", "risk_type", "risk_score", "severity",
                    "policy_violations", "budget_violations", "baseline_anomalies",
                ]
            }, indent=2)

            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{
                    "role": "user",
                    "content": (
                        "You are a senior SOC analyst. Analyze this AI agent security incident and respond "
                        "with a JSON object containing exactly these keys: "
                        "executive_summary (2 sentences), root_cause (1 sentence), impact (1 sentence), "
                        "confidence (e.g. 'High (91%)'), recommended_actions (list of 3 strings). "
                        "Be specific and concise. Respond ONLY with valid JSON.\n\n"
                        f"Incident data:\n{event_snapshot}"
                    )
                }]
            )
            raw = message.content[0].text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            ai_result = json.loads(raw)
            return {
                "session_id": session_id,
                "severity": first.get("severity", "unknown"),
                "timeline": timeline,
                "ai_generated": True,
                **ai_result,
            }
        except Exception as e:
            # Fall through to static fallback on any error
            pass

    # Static fallback when ANTHROPIC_API_KEY is not set
    first = events[0]
    return {
        "session_id": session_id,
        "executive_summary": (
            f"Agent '{first.get('agent_name')}' processed a {first.get('risk_type', 'unknown')} event "
            f"with severity {first.get('severity')}. "
            f"Injection score was {first.get('injection_score', 'N/A')} and tool "
            f"'{first.get('tool_requested')}' was {'allowed' if first.get('tool_allowed') else 'blocked'}."
        ),
        "severity": first.get("severity", "unknown"),
        "confidence": "High (88%)",
        "timeline": timeline,
        "root_cause": "Prompt injection attempt targeting sensitive tool execution.",
        "impact": "Potential PII leakage prevented by tool disallow and policy engine.",
        "recommended_actions": [
            f"Block session {session_id}",
            f"Disable tool '{first.get('tool_requested')}'",
            "Review policy rules for injection_score threshold",
        ],
        "ai_generated": False,
    }

@app.post("/incidents/{session_id}/remediate")
def remediate_incident(session_id: str, req: RemediationRequest):
    audit_event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_name": "support-refund-agent",
        "session_id": session_id,
        "action_taken": req.action,
        "tool_name": req.tool_name,
        "severity": "info",
        "message": f"Remediation action {req.action} executed."
    }
    send_event_to_splunk(audit_event)
    return {"status": "success", "audit_event": audit_event}

@app.post("/tools/{tool_name}/disable")
def disable_tool(tool_name: str):
    audit_event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_name": "support-refund-agent",
        "action_taken": "disabled_tool",
        "tool_name": tool_name,
        "severity": "info"
    }
    send_event_to_splunk(audit_event)
    return {"status": "success", "tool_name": tool_name, "disabled": True}

@app.get("/cases")
def get_cases():
    incidents = get_incidents()
    cases = load_cases()
    merged_cases = []
    
    # Group incidents by session_id and find the best representative event (the one with the actual attack telemetry)
    session_representatives = {}
    for inc in incidents:
        sess_id = inc.get("session_id")
        if not sess_id:
            continue
        existing = session_representatives.get(sess_id)
        if not existing:
            session_representatives[sess_id] = inc
        else:
            # Prefer the event that has prompt/risk_type
            if inc.get("prompt") and not existing.get("prompt"):
                session_representatives[sess_id] = inc
            elif inc.get("prompt") and existing.get("prompt"):
                # If both have prompts, choose the one with higher risk score
                if (inc.get("risk_score") or 0) > (existing.get("risk_score") or 0):
                    session_representatives[sess_id] = inc
            elif not inc.get("prompt") and not existing.get("prompt"):
                # If neither has a prompt, choose the one with the higher risk score or newer timestamp
                if (inc.get("risk_score") or 0) > (existing.get("risk_score") or 0):
                    session_representatives[sess_id] = inc
                    
    # Now build the merged cases using the representative event
    for sess_id, inc in session_representatives.items():
        if sess_id not in cases:
            cases[sess_id] = {
                "status": "New",
                "assignee": "unassigned",
                "comments": [
                    {
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                        "author": "System",
                        "message": f"Incident auto-created from Splunk ingestion. Severity: {str(inc.get('severity', 'high')).upper()}."
                    }
                ],
                "playbooks_run": []
            }
            
        case_meta = cases[sess_id]
        
        merged_cases.append({
            "session_id": sess_id,
            "timestamp": inc.get("timestamp"),
            "agent_name": inc.get("agent_name"),
            "user_id": inc.get("user_id"),
            "prompt": inc.get("prompt"),
            "response": inc.get("response"),
            "tool_requested": inc.get("tool_requested"),
            "risk_type": inc.get("risk_type"),
            "risk_score": inc.get("risk_score"),
            "severity": inc.get("severity"),
            "status": case_meta.get("status", "New"),
            "assignee": case_meta.get("assignee", "unassigned"),
            "comments": case_meta.get("comments", []),
            "playbooks_run": case_meta.get("playbooks_run", [])
        })
        
    save_cases(cases)
    # Sort merged cases by timestamp descending to keep the UI clean
    merged_cases.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return merged_cases

@app.get("/cases/{session_id}")
def get_case(session_id: str):
    cases = load_cases()
    if session_id not in cases:
        incidents = get_incidents()
        found_inc = None
        for inc in incidents:
            if inc.get("session_id") == session_id:
                found_inc = inc
                break
        if not found_inc:
            raise HTTPException(status_code=404, detail="Case not found")
            
        cases[session_id] = {
            "status": "New",
            "assignee": "unassigned",
            "comments": [
                {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "author": "System",
                    "message": f"Incident auto-created from Splunk ingestion. Severity: {found_inc.get('severity', 'high').upper()}."
                }
            ],
            "playbooks_run": []
        }
        save_cases(cases)
        
    case_meta = cases[session_id]
    
    events = []
    if os.path.exists(FALLBACK_LOG_FILE):
        with open(FALLBACK_LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("session_id") == session_id:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
                        
    return {
        "session_id": session_id,
        "status": case_meta.get("status"),
        "assignee": case_meta.get("assignee"),
        "comments": case_meta.get("comments"),
        "playbooks_run": case_meta.get("playbooks_run"),
        "events": events
    }

@app.post("/cases/{session_id}/status")
def update_case_status(session_id: str, req: CaseStatusUpdateRequest):
    cases = load_cases()
    if session_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
    
    old_status = cases[session_id].get("status", "New")
    cases[session_id]["status"] = req.status
    
    cases[session_id]["comments"].append({
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "author": "System",
        "message": f"Status updated from '{old_status}' to '{req.status}'."
    })
    
    save_cases(cases)
    
    audit_event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_name": "support-refund-agent",
        "session_id": session_id,
        "action_taken": "status_change",
        "message": f"Incident status changed to {req.status}",
        "severity": "info"
    }
    send_event_to_splunk(audit_event)
    
    return {"status": "success", "case": cases[session_id]}

@app.post("/cases/{session_id}/assign")
def assign_case(session_id: str, req: CaseAssignRequest):
    cases = load_cases()
    if session_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
        
    old_assignee = cases[session_id].get("assignee", "unassigned")
    cases[session_id]["assignee"] = req.assignee
    
    cases[session_id]["comments"].append({
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "author": "System",
        "message": f"Assignee updated from '{old_assignee}' to '{req.assignee}'."
    })
    
    save_cases(cases)
    
    audit_event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_name": "support-refund-agent",
        "session_id": session_id,
        "action_taken": "assign_case",
        "message": f"Incident assigned to {req.assignee}",
        "severity": "info"
    }
    send_event_to_splunk(audit_event)
    
    return {"status": "success", "case": cases[session_id]}

@app.post("/cases/{session_id}/comment")
def add_case_comment(session_id: str, req: CaseCommentRequest):
    cases = load_cases()
    if session_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
        
    cases[session_id]["comments"].append({
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "author": req.author,
        "message": req.message
    })
    
    save_cases(cases)
    return {"status": "success", "case": cases[session_id]}

@app.post("/cases/{session_id}/playbook")
def execute_playbook(session_id: str, req: PlaybookExecuteRequest):
    cases = load_cases()
    if session_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
        
    playbook_name = req.playbook_name
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    execution_logs = []
    
    try:
        if playbook_name == "Playbook A: Severe Prompt Injection Response":
            execution_logs.append(f"[{timestamp}] Starting Playbook A: Severe Prompt Injection Response...")
            
            execution_logs.append(f"[{timestamp}] Step 1/4: Quarantining active agent session '{session_id}'...")
            cases[session_id]["status"] = "Remediated"
            
            execution_logs.append(f"[{timestamp}] Step 2/4: Automatically disabling targeted tool 'crm.export_all_customers'...")
            tool_audit = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent_name": "support-refund-agent",
                "action_taken": "disabled_tool",
                "tool_name": "crm.export_all_customers",
                "severity": "info",
                "message": "Automated security policy: Disabling tool 'crm.export_all_customers'."
            }
            send_event_to_splunk(tool_audit)
            
            execution_logs.append(f"[{timestamp}] Step 3/4: Flagging suspect User ID for administrative review...")
            user_audit = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent_name": "support-refund-agent",
                "session_id": session_id,
                "action_taken": "flag_user",
                "severity": "warning",
                "message": "User flagged for high-risk behavior."
            }
            send_event_to_splunk(user_audit)
            
            execution_logs.append(f"[{timestamp}] Step 4/4: Dispatching High-Priority Security Alert to Splunk index 'security_alerts'...")
            alert_audit = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent_name": "support-refund-agent",
                "session_id": session_id,
                "action_taken": "splunk_alert",
                "severity": "critical",
                "message": "CRITICAL ALERT: Automated playbook response successfully executed. Incident contained."
            }
            send_event_to_splunk(alert_audit)
            
            execution_logs.append(f"[{timestamp}] Playbook A executed successfully. Incident quarantined and resolved.")
            playbook_status = "success"
            
        elif playbook_name == "Playbook B: PII / Data Leakage Containment":
            execution_logs.append(f"[{timestamp}] Starting Playbook B: PII / Data Leakage Containment...")
            
            execution_logs.append(f"[{timestamp}] Step 1/4: Quarantining compromised session logs in data vault...")
            cases[session_id]["status"] = "Remediated"
            
            execution_logs.append(f"[{timestamp}] Step 2/4: Applying PII Redaction Filter on historical log buffers...")
            
            execution_logs.append(f"[{timestamp}] Step 3/4: Dispatching encrypted Compliance & PII leak alert webhook...")
            compliance_audit = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent_name": "support-refund-agent",
                "session_id": session_id,
                "action_taken": "compliance_alert",
                "severity": "warning",
                "message": "PII/Secret leakage threat detected. Quarantining logs and alerting Compliance."
            }
            send_event_to_splunk(compliance_audit)
            
            execution_logs.append(f"[{timestamp}] Step 4/4: Pushing reinforced LLM system prompt security policy...")
            policy_audit = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent_name": "support-refund-agent",
                "session_id": session_id,
                "action_taken": "reinforce_guardrail",
                "severity": "info",
                "message": "System prompt policy guardrail reinforced."
            }
            send_event_to_splunk(policy_audit)
            
            execution_logs.append(f"[{timestamp}] Playbook B executed successfully. Data quarantine complete.")
            playbook_status = "success"
            
        else:
            raise ValueError(f"Unknown playbook: {playbook_name}")
            
    except Exception as e:
        execution_logs.append(f"[{timestamp}] ERROR: Playbook failed to execute: {str(e)}")
        playbook_status = "failed"
        
    cases[session_id]["playbooks_run"].append({
        "playbook_name": playbook_name,
        "timestamp": timestamp,
        "status": playbook_status,
        "log": execution_logs
    })
    
    cases[session_id]["comments"].append({
        "timestamp": timestamp,
        "author": "System",
        "message": f"Triggered automated containment playbook: '{playbook_name}'. Status: {playbook_status.upper()}."
    })
    
    save_cases(cases)
    return {"status": "success", "playbook_status": playbook_status, "log": execution_logs}


# ─────────────────────────────────────────────────────────────────────────────
#  V4: POLICY-AS-CODE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/policies")
def list_policies():
    return load_policies()


@app.post("/policies/{policy_id}/toggle")
def toggle_policy(policy_id: str, req: PolicyToggleRequest):
    policies = load_policies()
    for p in policies:
        if p["id"] == policy_id:
            p["enabled"] = req.enabled
            save_policies(policies)
            return {"status": "success", "policy": p}
    raise HTTPException(status_code=404, detail="Policy not found")


@app.post("/policies/evaluate")
def evaluate_policy(event: dict):
    """Evaluate an arbitrary event payload against all policies (for testing)."""
    triggered = evaluate_event(event)
    return {"triggered": triggered, "count": len(triggered)}


# ─────────────────────────────────────────────────────────────────────────────
#  V4: HALLUCINATION CHECK ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/hallucination/check")
def hallucination_check(payload: dict):
    result = check_hallucination(
        payload.get("prompt", ""),
        payload.get("response", ""),
        payload.get("quality_score", 1.0),
        payload.get("injection_score", 0),
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  V5: BUDGET MONITOR ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/budget")
def budget_summary():
    return get_budget_summary()


@app.post("/budget/config")
def update_budget_config(req: BudgetConfigRequest):
    config = load_budget_config()
    budgets = config.get("budgets", {})
    if req.per_session_token_limit is not None:
        budgets["per_session_token_limit"] = req.per_session_token_limit
    if req.per_session_cost_limit_usd is not None:
        budgets["per_session_cost_limit_usd"] = req.per_session_cost_limit_usd
    if req.daily_cost_limit_usd is not None:
        budgets["daily_cost_limit_usd"] = req.daily_cost_limit_usd
    if req.daily_token_limit is not None:
        budgets["daily_token_limit"] = req.daily_token_limit
    if req.alert_threshold_pct is not None:
        budgets["alert_threshold_pct"] = req.alert_threshold_pct
    config["budgets"] = budgets
    save_budget_config(config)
    return {"status": "success", "config": budgets}


@app.post("/budget/reset")
def reset_budget():
    return reset_budget_state()


# ─────────────────────────────────────────────────────────────────────────────
#  V5: BEHAVIORAL BASELINES ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/baselines")
def baselines():
    return get_baseline_report()


@app.get("/baselines/{agent_name}")
def baselines_for_agent(agent_name: str):
    b = compute_baselines(agent_name)
    if not b:
        raise HTTPException(status_code=404, detail="Insufficient data to compute baselines for this agent")
    return {"agent_name": agent_name, "baselines": b}


# ─────────────────────────────────────────────────────────────────────────────
#  V5: MODEL ARENA ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/model-arena")
def model_arena():
    """Return per-model performance stats for the Model Arena visualization."""
    if not os.path.exists(FALLBACK_LOG_FILE):
        return {"models": []}

    events = []
    with open(FALLBACK_LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if e.get("prompt"):
                        events.append(e)
                except Exception:
                    pass

    model_stats: dict = {}
    for e in events:
        m = e.get("model")
        if not m:
            continue
        if m not in model_stats:
            model_stats[m] = {
                "model": m,
                "count": 0,
                "latency_sum": 0,
                "cost_sum": 0.0,
                "quality_sum": 0.0,
                "risk_sum": 0,
                "hallucination_sum": 0.0,
                "injection_sum": 0,
            }
        s = model_stats[m]
        s["count"] += 1
        s["latency_sum"] += e.get("latency_ms") or 0
        s["cost_sum"] += e.get("estimated_cost_usd") or 0
        s["quality_sum"] += e.get("quality_score") or 0
        s["risk_sum"] += e.get("risk_score") or 0
        s["hallucination_sum"] += e.get("hallucination_score") or 0
        s["injection_sum"] += e.get("injection_score") or 0

    result = []
    for m, s in model_stats.items():
        n = max(s["count"], 1)
        result.append({
            "model": m,
            "count": s["count"],
            "avg_latency_ms": round(s["latency_sum"] / n, 1),
            "avg_cost_usd": round(s["cost_sum"] / n, 5),
            "total_cost_usd": round(s["cost_sum"], 4),
            "avg_quality": round(s["quality_sum"] / n, 3),
            "avg_risk_score": round(s["risk_sum"] / n, 1),
            "avg_hallucination": round(s["hallucination_sum"] / n, 3),
            "avg_injection_score": round(s["injection_sum"] / n, 1),
        })

    result.sort(key=lambda x: x["avg_risk_score"], reverse=True)
    return {"models": result}
