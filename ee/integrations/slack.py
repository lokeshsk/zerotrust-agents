import requests
import json
import os

# Base URL to generate callback URLs. In production this should be the public SaaS domain.
# For local dev, we fall back to localhost (though interactive buttons won't work locally without Ngrok).
BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

def send_slack_hitl_message(webhook_url: str, approval_payload: dict):
    """
    Sends an interactive message to Slack using Block Kit.
    """
    approval_id = approval_payload.get("id")
    agent_id = approval_payload.get("agent_id")
    tool_name = approval_payload.get("tool_name")
    arguments = approval_payload.get("arguments")
    tenant_id = approval_payload.get("tenant_id")
    
    # We embed the tenant_id and approval_id in the action_id so we can extract it on callback
    approve_action = f"hitl_approve|{tenant_id}|{approval_id}"
    reject_action = f"hitl_reject|{tenant_id}|{approval_id}"
    
    block_kit_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "ZeroTrust Agents: Approval Required",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Agent ID:*\n`{agent_id}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Target Tool:*\n`{tool_name}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Arguments:*\n```\n{arguments}\n```"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": "approved",
                        "action_id": approve_action
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Block",
                            "emoji": True
                        },
                        "style": "danger",
                        "value": "rejected",
                        "action_id": reject_action
                    }
                ]
            }
        ]
    }
    
    response = requests.post(webhook_url, json=block_kit_payload, timeout=5.0)
    response.raise_for_status()
    return response.status_code
