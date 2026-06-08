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
    dlp_sensitivity = Column(String, default="high") # low, medium, high
    siem_webhook_url = Column(String, nullable=True)
    
    # EE Features (Slack & Budget)
    hitl_webhook_url = Column(String, nullable=True)
    monthly_budget = Column(Integer, default=0) # e.g., budget in cents
    current_spend = Column(Integer, default=0)
    
    mcp_upstream_url = Column(String, default="http://localhost:8080")
    
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

class PermissionDB(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    role = Column(String, index=True)
    permission = Column(String, index=True) # e.g. 'policies:read', 'policies:write'

class AgentDB(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True) # e.g. 'agent_xyz'
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True)
    name = Column(String)
    budget_limit = Column(Integer, default=0) # e.g. 0 means no limit
    current_spend = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminAuditTrailDB(Base):
    __tablename__ = "admin_audit_trails"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True)
    user_id = Column(String, index=True) # ID of the admin who made the change
    action = Column(String) # e.g. 'policy_created', 'config_updated'
    target_resource = Column(String) # e.g. 'policy:agent_x:tool_y'
    before_state = Column(String, nullable=True) # JSON snapshot
    after_state = Column(String, nullable=True) # JSON snapshot
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
