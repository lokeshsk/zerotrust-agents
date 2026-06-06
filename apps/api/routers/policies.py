from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import verify_jwt, verify_gateway, require_role
from fastapi import Header

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("/", response_model=List[schemas.PolicyResponse])
def list_policies(x_tenant_id: str = Header(default="default", alias="x-tenant-id"), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), jwt_payload: dict = Depends(verify_jwt)):
    tenant_id = x_tenant_id
    return db.query(models.PolicyDB).filter(models.PolicyDB.tenant_id == tenant_id).offset(skip).limit(limit).all()

@router.get("/{tenant_id}/{agent_id}/{tool_name}", response_model=schemas.PolicyResponse)
def get_policy(tenant_id: str, agent_id: str, tool_name: str, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    policy = db.query(models.PolicyDB).filter(
        models.PolicyDB.tenant_id == tenant_id,
        models.PolicyDB.agent_id == agent_id,
        models.PolicyDB.tool_name == tool_name
    ).first()
    
    if not policy:
        # Return a mock deny policy if not explicitly defined
        return {"id": 0, "tenant_id": tenant_id, "agent_id": agent_id, "tool_name": tool_name, "action": "deny", "dsl_rules": None}
    return policy

@router.get("/{tenant_id}/config")
def get_tenant_config(tenant_id: str, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "api_key": tenant.api_key,
        "dlp_model": tenant.dlp_model,
        "dlp_api_base": tenant.dlp_api_base,
        "dlp_api_key": tenant.dlp_api_key,
        "monthly_budget": tenant.monthly_budget,
        "current_spend": tenant.current_spend,
        "siem_webhook_url": tenant.siem_webhook_url,
        "hitl_webhook_url": tenant.hitl_webhook_url
    }

@router.post("/{tenant_id}/config")
def update_tenant_config(tenant_id: str, config: schemas.TenantConfigUpdate, db: Session = Depends(get_db), role_binding: models.RoleBindingDB = Depends(require_role("admin"))):
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    if config.dlp_model is not None: tenant.dlp_model = config.dlp_model
    if config.dlp_api_base is not None: tenant.dlp_api_base = config.dlp_api_base
    if config.dlp_api_key is not None: tenant.dlp_api_key = config.dlp_api_key
    if config.monthly_budget is not None: tenant.monthly_budget = config.monthly_budget
    if config.siem_webhook_url is not None: tenant.siem_webhook_url = config.siem_webhook_url
    if config.hitl_webhook_url is not None: tenant.hitl_webhook_url = config.hitl_webhook_url
    
    db.commit()
    return {"status": "ok"}

class UsageReport(schemas.BaseModel):
    tokens: int
    cost: float

@router.post("/{tenant_id}/usage")
def report_usage(tenant_id: str, usage: UsageReport, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    tenant.current_spend += int(usage.cost * 100) # Assuming cost is reported in dollars and stored in cents
    db.commit()
    
    return {"status": "ok", "current_spend": tenant.current_spend}

@router.post("/", response_model=schemas.PolicyResponse)
def create_policy(policy: schemas.PolicyCreate, db: Session = Depends(get_db), role_binding: models.RoleBindingDB = Depends(require_role("admin"))):
    # Check if exists to perform an upsert
    existing = db.query(models.PolicyDB).filter(
        models.PolicyDB.tenant_id == policy.tenant_id,
        models.PolicyDB.agent_id == policy.agent_id,
        models.PolicyDB.tool_name == policy.tool_name
    ).first()
    
    if existing:
        existing.action = policy.action
        db.commit()
        db.refresh(existing)
        return existing
    
    db_policy = models.PolicyDB(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.delete("/{tenant_id}/{agent_id}/{tool_name}")
def delete_policy(tenant_id: str, agent_id: str, tool_name: str, db: Session = Depends(get_db), role_binding: models.RoleBindingDB = Depends(require_role("admin"))):
    policy = db.query(models.PolicyDB).filter(
        models.PolicyDB.tenant_id == tenant_id,
        models.PolicyDB.agent_id == agent_id,
        models.PolicyDB.tool_name == tool_name
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"status": "deleted"}

@router.post("/register")
def register_tools(request: schemas.RegisterToolsRequest, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    for tool in request.tools:
        exists = db.query(models.PolicyDB).filter(
            models.PolicyDB.tenant_id == request.tenant_id,
            models.PolicyDB.agent_id == request.agent_id,
            models.PolicyDB.tool_name == tool
        ).first()
        if not exists:
            new_policy = models.PolicyDB(tenant_id=request.tenant_id, agent_id=request.agent_id, tool_name=tool, action="deny")
            db.add(new_policy)
    db.commit()
    return {"status": "auto-discovered"}

from fastapi import UploadFile, File
import yaml

@router.post("/sync-yaml")
async def sync_yaml_policies(
    file: UploadFile = File(...), 
    x_tenant_id: str = Header(default="default", alias="x-tenant-id"), 
    db: Session = Depends(get_db), 
    role_binding: models.RoleBindingDB = Depends(require_role("admin"))
):
    try:
        content = await file.read()
        parsed = yaml.safe_load(content)
        
        if not isinstance(parsed, dict) or "policies" not in parsed:
            raise HTTPException(status_code=400, detail="Invalid YAML: Must contain a top-level 'policies' list.")
            
        synced_count = 0
        for p in parsed["policies"]:
            agent_id = p.get("agent_id")
            tool_name = p.get("tool_name")
            action = p.get("action", "deny")
            
            if not agent_id or not tool_name:
                continue
                
            existing = db.query(models.PolicyDB).filter(
                models.PolicyDB.tenant_id == x_tenant_id,
                models.PolicyDB.agent_id == agent_id,
                models.PolicyDB.tool_name == tool_name
            ).first()
            
            if existing:
                existing.action = action
            else:
                new_policy = models.PolicyDB(tenant_id=x_tenant_id, agent_id=agent_id, tool_name=tool_name, action=action)
                db.add(new_policy)
            synced_count += 1
            
        db.commit()
        return {"status": "success", "synced": synced_count}
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format.")

# --- Pending Approvals ---
@router.get("/approvals", response_model=List[schemas.PendingApproval])
def list_approvals(x_tenant_id: str = Header(default="default", alias="x-tenant-id"), db: Session = Depends(get_db), jwt_payload: dict = Depends(verify_jwt)):
    tenant_id = x_tenant_id
    return db.query(models.PendingApprovalDB).filter(
        models.PendingApprovalDB.tenant_id == tenant_id,
        models.PendingApprovalDB.status == "pending"
    ).all()

import requests
from fastapi import BackgroundTasks

def send_hitl_webhook(url: str, payload: dict):
    try:
        # Format for generic webhook, but could be adapted for Slack Block Kit
        message = {
            "text": f"*HITL Approval Required*\nAgent `{payload['agent_id']}` wants to use `{payload['tool_name']}`.\n*Arguments:* `{payload['arguments']}`\n*Approval ID:* `{payload['id']}`"
        }
        requests.post(url, json=message, timeout=2.0)
    except Exception as e:
        print(f"HITL Webhook failed: {e}")

@router.post("/approvals", response_model=schemas.PendingApproval)
def create_approval(approval: schemas.PendingApprovalBase, background_tasks: BackgroundTasks, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    db_approval = models.PendingApprovalDB(**approval.model_dump())
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == approval.tenant_id).first()
    if tenant and tenant.hitl_webhook_url:
        background_tasks.add_task(send_hitl_webhook, tenant.hitl_webhook_url, db_approval.__dict__)
        
    return db_approval

@router.get("/approvals/{approval_id}", response_model=schemas.PendingApproval)
def get_approval(approval_id: int, x_tenant_id: str = Header(default="default", alias="x-tenant-id"), db: Session = Depends(get_db), jwt_payload: dict = Depends(verify_jwt)):
    tenant_id = x_tenant_id
    approval = db.query(models.PendingApprovalDB).filter(
        models.PendingApprovalDB.id == approval_id,
        models.PendingApprovalDB.tenant_id == tenant_id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval

@router.post("/approvals/{approval_id}/resolve")
def resolve_approval(approval_id: int, action: str, x_tenant_id: str = Header(default="default", alias="x-tenant-id"), db: Session = Depends(get_db), role_binding: models.RoleBindingDB = Depends(require_role("admin"))):
    tenant_id = x_tenant_id
    if action not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    approval = db.query(models.PendingApprovalDB).filter(
        models.PendingApprovalDB.id == approval_id,
        models.PendingApprovalDB.tenant_id == tenant_id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = action
    db.commit()
    return {"status": action}
