import requests
import json
import time

def send_siem_event(webhook_url: str, event_type: str, payload: dict):
    """
    Sends a structured JSON event to a SIEM webhook (e.g. Datadog, Splunk HEC, or generic HTTPS endpoint).
    """
    # Wrap in a standard schema
    siem_payload = {
        "timestamp": int(time.time()),
        "event_source": "zerotrust-agents",
        "event_type": event_type,
        "data": payload
    }
    
    try:
        # If it's a Splunk HEC endpoint, it might expect {"event": {...}}
        if "splunk" in webhook_url.lower():
            requests.post(webhook_url, json={"event": siem_payload}, timeout=2.0)
        else:
            # Datadog or Generic webhook
            requests.post(webhook_url, json=siem_payload, timeout=2.0)
    except Exception as e:
        print(f"SIEM Forwarding failed: {e}")
