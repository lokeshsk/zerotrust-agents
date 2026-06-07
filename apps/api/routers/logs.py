from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import verify_jwt, verify_gateway, require_role
from fastapi import Header

router = APIRouter(prefix="/logs", tags=["Audit Logs"])

import requests
from fastapi import BackgroundTasks
from routers.ws import manager

async def broadcast_log(log_data: dict):
    await manager.broadcast({"type": "NEW_LOG", "data": log_data})

def send_siem_webhook(url: str, payload: dict):
    try:
        requests.post(url, json=payload, timeout=2.0)
    except Exception as e:
        print(f"SIEM Webhook failed: {e}")

@router.post("/", response_model=schemas.LogResponse)
def create_log(log: schemas.LogCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    db_log = models.AuditLogDB(**log.model_dump())
    db.add(db_log)
    
    # Increment tenant billing event count and check webhooks
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == log.tenant_id).first()
    if tenant:
        tenant.events_this_month += 1
        if tenant.siem_webhook_url:
            payload = log.model_dump()
            payload["event_type"] = "audit_log"
            background_tasks.add_task(send_siem_webhook, tenant.siem_webhook_url, payload)
        
    db.commit()
    db.refresh(db_log)
    
    # Broadcast to dashboard
    background_tasks.add_task(broadcast_log, schemas.LogResponse.model_validate(db_log).model_dump(mode="json"))
    
    return db_log

@router.get("/", response_model=List[schemas.LogResponse])
def get_logs(x_tenant_id: str = Header(default="default", alias="x-tenant-id"), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), role_binding = Depends(require_role("auditor"))):
    tenant_id = x_tenant_id
    return db.query(models.AuditLogDB).filter(models.AuditLogDB.tenant_id == tenant_id).order_by(models.AuditLogDB.timestamp.desc()).offset(skip).limit(limit).all()
