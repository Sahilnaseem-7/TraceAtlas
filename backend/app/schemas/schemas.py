from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.models import AssetType


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    org_id: UUID


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=500)
    owner: str | None = Field(default=None, max_length=200)
    format: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list, max_length=50)


class DatasetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=500)
    owner: str | None = Field(default=None, max_length=200)
    format: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = Field(default=None, max_length=50)
    governance_status: str | None = Field(default=None, max_length=50)


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    source: str | None
    owner: str | None
    format: str | None
    tags: list[str]
    governance_status: str
    created_at: datetime


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    dataset_id: UUID
    version_tag: str
    record_count: int | None
    column_count: int | None
    schema_snapshot: dict[str, Any] | None
    content_hash: str | None
    profile_results: dict[str, Any] | None
    created_at: datetime


class LineageEdgeCreate(BaseModel):
    source_type: AssetType
    source_id: UUID
    target_type: AssetType
    target_id: UUID
    relationship_type: str = Field(min_length=1, max_length=100)


class LineageEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_type: AssetType
    source_id: UUID
    target_type: AssetType
    target_id: UUID
    relationship_type: str


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None
    created_at: datetime


class GovernanceReviewCreate(BaseModel):
    dataset_id: UUID
    findings: str | None = None


class GovernanceReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    dataset_id: UUID
    status: str
    findings: str | None
    created_at: datetime
    updated_at: datetime


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_type: str
    resource_type: str | None
    resource_id: UUID | None
    details: dict[str, Any] | None
    created_at: datetime
