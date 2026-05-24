import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FALLBACK_LOG_FILE = os.getenv("FALLBACK_LOG_FILE", "../data/ai_agent_logs.jsonl")

def send_event_to_splunk(event_data: dict):
    SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL", "")
    SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN", "")

    # Always write to fallback log file first
    try:
        os.makedirs(os.path.dirname(FALLBACK_LOG_FILE), exist_ok=True)
        with open(FALLBACK_LOG_FILE, "a") as f:
            f.write(json.dumps(event_data) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to fallback log: {e}")

    if not SPLUNK_HEC_TOKEN:
        logger.info("SPLUNK_HEC_TOKEN not set. Skipping HEC send.")
        return

    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "event": event_data,
        "sourcetype": "_json",
        "index": "ai_agent_logs"
    }

    try:
        response = requests.post(
            SPLUNK_HEC_URL, 
            json=payload, 
            headers=headers, 
            verify=False # In a demo environment, ignore self-signed certs
        )
        if response.status_code != 200:
            logger.error(f"Splunk HEC Error: {response.text}")
    except Exception as e:
        logger.error(f"Exception sending to Splunk HEC: {e}")
