from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from database import get_db
import models
import json

router = APIRouter(prefix="/integrations", tags=["Integrations"])

@router.post("/slack/action")
async def slack_interaction(request: Request, db: Session = Depends(get_db)):
    """
    Receives interactive callbacks from Slack Block Kit (e.g. when an admin clicks Approve/Block).
    """
    form_data = await request.form()
    payload_str = form_data.get("payload")
    if not payload_str:
        raise HTTPException(status_code=400, detail="Missing payload")
        
    payload = json.loads(payload_str)
    
    # Check if it's an interactive message action
    if payload.get("type") == "block_actions":
        actions = payload.get("actions", [])
        for action in actions:
            action_id = action.get("action_id", "")
            
            # action_id format: hitl_approve|tenant_id|approval_id
            if action_id.startswith("hitl_approve|") or action_id.startswith("hitl_reject|"):
                parts = action_id.split("|")
                if len(parts) == 3:
                    action_type = "approved" if "approve" in parts[0] else "rejected"
                    tenant_id = parts[1]
                    approval_id = int(parts[2])
                    
                    # Resolve the approval in the DB
                    approval = db.query(models.PendingApprovalDB).filter(
                        models.PendingApprovalDB.id == approval_id,
                        models.PendingApprovalDB.tenant_id == tenant_id,
                        models.PendingApprovalDB.status == "pending"
                    ).first()
                    
                    if approval:
                        approval.status = action_type
                        db.commit()
                        
                        # In a real app we'd also update the Slack message to say "Approved by X", 
                        # but returning 200 is sufficient to acknowledge the click.
                        return Response(status_code=200)

    return Response(status_code=200)


@router.post("/discord/action")
async def discord_interaction(request: Request, db: Session = Depends(get_db)):
    """
    Receives interactive callbacks from Discord Message Components (Buttons).
    """
    # Discord sends interactions as JSON
    payload = await request.json()
    
    # Handle Discord Ping/Pong verification
    if payload.get("type") == 1:
        return {"type": 1}
        
    # Handle Message Component interaction
    if payload.get("type") == 3:
        data = payload.get("data", {})
        custom_id = data.get("custom_id", "")
        
        # custom_id format: hitl_approve|tenant_id|approval_id
        if custom_id.startswith("hitl_approve|") or custom_id.startswith("hitl_reject|"):
            parts = custom_id.split("|")
            if len(parts) == 3:
                action_type = "approved" if "approve" in parts[0] else "rejected"
                tenant_id = parts[1]
                approval_id = int(parts[2])
                
                # Resolve the approval in the DB
                approval = db.query(models.PendingApprovalDB).filter(
                    models.PendingApprovalDB.id == approval_id,
                    models.PendingApprovalDB.tenant_id == tenant_id,
                    models.PendingApprovalDB.status == "pending"
                ).first()
                
                if approval:
                    approval.status = action_type
                    db.commit()
                    
                    # Discord requires a specific response format to update the message
                    # Type 7: UPDATE_MESSAGE
                    return {
                        "type": 7,
                        "data": {
                            "content": f"✅ This request was {action_type.upper()}.",
                            "components": [] # Remove the buttons
                        }
                    }

    return Response(status_code=200)
