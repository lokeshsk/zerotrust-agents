from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class TenantDB(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, index=True) # e.g., 'org_123'
    name = Column(String)
    billing_plan = Column(String, default="open_core") # open_core, startup, enterprise
    api_key = Column(String, unique=True, index=True)
    events_this_month = Column(Integer, default=0)
    
    # Semantic DLP Configuration
    dlp_model = Column(String, nullable=True) # e.g., 'ollama/llama3'
    dlp_api_base = Column(String, nullable=True) # e.g., 'http://localhost:11434'
    dlp_api_key = Column(String, nullable=True)
    
    # SIEM / Logging
    siem_webhook_url = Column(String, nullable=True)
    
    # EE Features (Slack & Budget)
    hitl_webhook_url = Column(String, nullable=True)
    monthly_budget = Column(Integer, default=0) # e.g., budget in cents
    current_spend = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PolicyDB(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True, default="default")
    agent_id = Column(String, index=True)
    tool_name = Column(String, index=True)
    action = Column(String, default="deny") # allow, deny, require_approval
    dsl_rules = Column(String, nullable=True) # JSON rules payload

class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True, default="default")
    agent_id = Column(String, index=True)
    tool_name = Column(String, index=True)
    arguments = Column(String)
    allowed = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class PendingApprovalDB(Base):
    __tablename__ = "pending_approvals"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True, default="default")
    agent_id = Column(String, index=True)
    tool_name = Column(String, index=True)
    arguments = Column(String)
    status = Column(String, default="pending") # pending, approved, rejected
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AdminDB(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, default="admin")
    password_hash = Column(String)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True) # e.g. 'usr_abc'
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RoleBindingDB(Base):
    __tablename__ = "role_bindings"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True)
    role = Column(String) # 'owner', 'admin', 'auditor', 'developer'
