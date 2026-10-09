from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime

# Auth & Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Workspaces
class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    org_id: UUID
    class Config:
        from_attributes = True

# Datasets
class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source: Optional[str] = None
    owner: Optional[str] = None
    format: Optional[str] = None
    tags: List[str] = []

class DatasetResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: Optional[str]
    source: Optional[str]
    owner: Optional[str]
    format: Optional[str]
    tags: List[str]
    governance_status: str
    created_at: datetime
    class Config:
        from_attributes = True

class DatasetVersionResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    version_tag: str
    record_count: Optional[int]
    column_count: Optional[int]
    schema_snapshot: Optional[Dict[str, Any]]
    content_hash: Optional[str]
    profile_results: Optional[Dict[str, Any]]
    created_at: datetime
    class Config:
        from_attributes = True

# Lineage
class LineageEdgeCreate(BaseModel):
    source_type: str
    source_id: UUID
    target_type: str
    target_id: UUID
    relationship_type: str

class LineageEdgeResponse(BaseModel):
    id: UUID
    source_type: str
    source_id: UUID
    target_type: str
    target_id: UUID
    relationship_type: str
    class Config:
        from_attributes = True

# Models
class ModelCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ModelResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# Governance
class GovernanceReviewCreate(BaseModel):
    dataset_id: UUID
    findings: Optional[str] = None

class GovernanceReviewResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    status: str
    findings: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# Audit
class AuditEventResponse(BaseModel):
    id: UUID
    event_type: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    class Config:
        from_attributes = True