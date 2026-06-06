from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid

import models
from database import get_db
from routers.auth import verify_jwt, verify_gateway, require_role

router = APIRouter(prefix="/tenants", tags=["Tenants"])

class TenantCreate(BaseModel):
    name: str

class TenantResponse(BaseModel):
    id: str
    name: str
    billing_plan: str
    events_this_month: int
    monthly_budget: int
    current_spend: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TenantResponse])
def get_tenants(db: Session = Depends(get_db), jwt_payload: dict = Depends(verify_jwt)):
    return db.query(models.TenantDB).all()

@router.get("/resolve-key")
def resolve_api_key(api_key: str, db: Session = Depends(get_db), gateway: bool = Depends(verify_gateway)):
    tenant = db.query(models.TenantDB).filter(models.TenantDB.api_key == api_key).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return {"tenant_id": tenant.id}

@router.post("/", response_model=TenantResponse)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db), jwt_payload: dict = Depends(verify_jwt)):
    new_tenant_id = f"org_{uuid.uuid4().hex[:8]}"
    new_tenant = models.TenantDB(
        id=new_tenant_id,
        name=tenant.name,
        api_key=f"sk-{uuid.uuid4().hex}",
        billing_plan="enterprise"
    )
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    return new_tenant
class MemberResponse(BaseModel):
    user_id: str
    email: str
    role: str

    class Config:
        from_attributes = True

class MemberAdd(BaseModel):
    email: str
    role: str
    password: str # For MVP, specify password to create the user

@router.get("/{tenant_id}/members", response_model=List[MemberResponse])
def get_tenant_members(tenant_id: str, db: Session = Depends(get_db), role_binding = Depends(require_role("admin"))):
    bindings = db.query(models.RoleBindingDB).filter(models.RoleBindingDB.tenant_id == tenant_id).all()
    results = []
    for b in bindings:
        u = db.query(models.UserDB).filter(models.UserDB.id == b.user_id).first()
        if u:
            results.append({"user_id": u.id, "email": u.email, "role": b.role})
    return results

from routers.auth import hash_password

@router.post("/{tenant_id}/members")
def add_tenant_member(tenant_id: str, payload: MemberAdd, db: Session = Depends(get_db), role_binding = Depends(require_role("admin"))):
    user = db.query(models.UserDB).filter(models.UserDB.email == payload.email).first()
    if not user:
        user = models.UserDB(
            id=f"usr_{uuid.uuid4().hex[:8]}",
            email=payload.email,
            password_hash=hash_password(payload.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    existing = db.query(models.RoleBindingDB).filter(
        models.RoleBindingDB.user_id == user.id,
        models.RoleBindingDB.tenant_id == tenant_id
    ).first()
    
    if existing:
        existing.role = payload.role
    else:
        new_binding = models.RoleBindingDB(user_id=user.id, tenant_id=tenant_id, role=payload.role)
        db.add(new_binding)
    db.commit()
    return {"status": "success"}
