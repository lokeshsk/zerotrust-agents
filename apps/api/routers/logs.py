from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import verify_jwt, verify_gateway, require_permission
from fastapi import Header

router = APIRouter(prefix="/logs", tags=["Audit Logs"])

import requests
from fastapi import BackgroundTasks
from routers.ws import manager
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
try:
    from ee.integrations.siem import send_siem_event
except ImportError:
    send_siem_event = None

async def broadcast_log(log_data: dict):
    await manager.broadcast({"type": "NEW_LOG", "data": log_data})

@router.post("/", response_model=schemas.LogResponse)
def create_log(log: schemas.LogCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    db_log = models.AuditLogDB(**log.model_dump())
    db.add(db_log)
    
    # Increment tenant billing event count and check webhooks
    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == log.tenant_id).first()
    if tenant:
        tenant.events_this_month += 1
        if tenant.siem_webhook_url and send_siem_event:
            payload = log.model_dump()
            background_tasks.add_task(send_siem_event, tenant.siem_webhook_url, "audit_log", payload)
        
    db.commit()
    db.refresh(db_log)
    
    # Broadcast to dashboard
    background_tasks.add_task(broadcast_log, schemas.LogResponse.model_validate(db_log).model_dump(mode="json"))
    
    return db_log

@router.get("/", response_model=List[schemas.LogResponse])
def get_logs(x_tenant_id: str = Header(default="default", alias="x-tenant-id"), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), role_binding = Depends(require_permission("logs:read"))):
    tenant_id = x_tenant_id
    return db.query(models.AuditLogDB).filter(models.AuditLogDB.tenant_id == tenant_id).order_by(models.AuditLogDB.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/audit-trail")
def get_audit_trail(x_tenant_id: str = Header(default="default", alias="x-tenant-id"), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), role_binding = Depends(require_permission("logs:read"))):
    tenant_id = x_tenant_id
    trails = db.query(models.AdminAuditTrailDB).filter(models.AdminAuditTrailDB.tenant_id == tenant_id).order_by(models.AdminAuditTrailDB.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "tenant_id": t.tenant_id,
            "user_id": t.user_id,
            "action": t.action,
            "target_resource": t.target_resource,
            "before_state": t.before_state,
            "after_state": t.after_state,
            "timestamp": t.timestamp
        } for t in trails
    ]
