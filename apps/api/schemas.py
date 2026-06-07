from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TenantConfigUpdate(BaseModel):
    dlp_model: Optional[str] = None
    dlp_api_base: Optional[str] = None
    dlp_api_key: Optional[str] = None
    dlp_sensitivity: Optional[str] = None
    monthly_budget: Optional[int] = None
    siem_webhook_url: Optional[str] = None
    hitl_webhook_url: Optional[str] = None
    mcp_upstream_url: Optional[str] = None

# Policy Schemas
class PolicyBase(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    tool_name: str
    action: str
    dsl_rules: Optional[str] = None

class PolicyCreate(PolicyBase):
    pass

class PolicyResponse(PolicyBase):
    id: int
    class Config:
        from_attributes = True

class RegisterToolsRequest(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    tools: List[str]

# Log Schemas
class LogCreate(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    tool_name: str
    arguments: str
    allowed: bool

class LogResponse(LogCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# Approval Schemas
class PendingApprovalBase(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    tool_name: str
    arguments: str

class PendingApproval(PendingApprovalBase):
    id: int
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True
