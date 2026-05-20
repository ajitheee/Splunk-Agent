from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from .hec_sender import send_event_to_splunk
from agent_app.simulator import generate_normal_event, generate_attack_event
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/simulate/normal")
def simulate_normal():
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_normal_event()
        send_event_to_splunk(event)
        
        span.set_attribute("gen_ai.system", event.get("agent_name", ""))
        span.set_attribute("gen_ai.request.model", event.get("model", ""))
        span.set_attribute("gen_ai.usage.input_tokens", event.get("tokens_prompt", 0))
        span.set_attribute("gen_ai.usage.output_tokens", event.get("tokens_completion", 0))
        span.set_attribute("user.id", event.get("user_id", ""))
        span.set_attribute("session.id", event.get("session_id", ""))
        span.set_attribute("gen_ai.prompt", event.get("prompt", ""))
        span.set_attribute("gen_ai.completion", event.get("response", ""))
        span.set_attribute("tool.requested", event.get("tool_requested", ""))
        span.set_attribute("risk.score", event.get("risk_score", 0))
        
    return {"status": "success", "event": event}

@app.post("/simulate/attack")
def simulate_attack():
    with tracer.start_as_current_span("agent_session") as span:
        event = generate_attack_event()
        send_event_to_splunk(event)

        span.set_attribute("gen_ai.system", event.get("agent_name", ""))
        span.set_attribute("gen_ai.request.model", event.get("model", ""))
        span.set_attribute("gen_ai.usage.input_tokens", event.get("tokens_prompt", 0))
        span.set_attribute("gen_ai.usage.output_tokens", event.get("tokens_completion", 0))
        span.set_attribute("user.id", event.get("user_id", ""))
        span.set_attribute("session.id", event.get("session_id", ""))
        span.set_attribute("gen_ai.prompt", event.get("prompt", ""))
        span.set_attribute("gen_ai.completion", event.get("response", ""))
        span.set_attribute("tool.requested", event.get("tool_requested", ""))
        span.set_attribute("risk.score", event.get("risk_score", 0))
        
    return {"status": "success", "event": event}

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
    # Mock AI Summary Generation
    timeline = []
    for e in events:
        timeline.append(f"{e.get('timestamp')} - Prompt received: [REDACTED]")
        timeline.append(f"{e.get('timestamp')} - Tool {e.get('tool_requested')} requested")
        timeline.append(f"{e.get('timestamp')} - Incident flagged as {e.get('risk_type')}")
    summary = {
        "executive_summary": "An unauthenticated user attempted a prompt injection to export VIP customer emails.",
        "severity": events[0].get("severity", "unknown"),
        "confidence": "High (92%)",
        "timeline": timeline,
        "root_cause": "Missing authorization guardrail on tool execution.",
        "impact": "Potential PII leakage prevented by tool disallow policy.",
        "recommended_actions": ["Block session", "Disable crm.export_all_customers tool"]
    }
    return summary

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
