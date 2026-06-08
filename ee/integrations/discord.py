import requests
import json
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

def send_discord_hitl_message(webhook_url: str, approval_payload: dict):
    """
    Sends an interactive message to Discord using Embeds and Message Components.
    """
    approval_id = approval_payload.get("id")
    agent_id = approval_payload.get("agent_id")
    tool_name = approval_payload.get("tool_name")
    arguments = approval_payload.get("arguments")
    tenant_id = approval_payload.get("tenant_id")
    
    approve_custom_id = f"hitl_approve|{tenant_id}|{approval_id}"
    reject_custom_id = f"hitl_reject|{tenant_id}|{approval_id}"
    
    payload = {
        "embeds": [
            {
                "title": "ZeroTrust Agents: Approval Required",
                "color": 16753920, # Orange
                "fields": [
                    {
                        "name": "Agent ID",
                        "value": f"`{agent_id}`",
                        "inline": True
                    },
                    {
                        "name": "Target Tool",
                        "value": f"`{tool_name}`",
                        "inline": True
                    },
                    {
                        "name": "Arguments",
                        "value": f"```json\n{arguments}\n```",
                        "inline": False
                    }
                ]
            }
        ],
        "components": [
            {
                "type": 1, # Action Row
                "components": [
                    {
                        "type": 2, # Button
                        "label": "Approve",
                        "style": 3, # Success (Green)
                        "custom_id": approve_custom_id
                    },
                    {
                        "type": 2, # Button
                        "label": "Block",
                        "style": 4, # Danger (Red)
                        "custom_id": reject_custom_id
                    }
                ]
            }
        ]
    }
    
    response = requests.post(webhook_url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.status_code
