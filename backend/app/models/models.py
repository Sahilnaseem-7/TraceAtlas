import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Enum as SAEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import datetime

class Role(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DATA_ENGINEER = "data_engineer"
    DATA_SCIENTIST = "data_scientist"
    AUDITOR = "auditor"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Membership(Base):
    __tablename__ = "memberships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    role = Column(SAEnum(Role), nullable=False, default=Role.DATA_SCIENTIST)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    source = Column(String)
    owner = Column(String)
    format = Column(String)
    tags = Column(JSON, default=list)
    governance_status = Column(String, default="not_reviewed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    version_tag = Column(String, nullable=False)
    record_count = Column(Integer)
    column_count = Column(Integer)
    schema_snapshot = Column(JSON)
    content_hash = Column(String)
    profile_results = Column(JSON)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dataset = relationship("Dataset", back_populates="versions")

class AssetType(str, enum.Enum):
    DATASET = "dataset"
    DATASET_VERSION = "dataset_version"
    MODEL = "model"
    MODEL_VERSION = "model_version"
    EXPERIMENT = "experiment"
    DEPLOYMENT = "deployment"
    TRANSFORMATION = "transformation"

class LineageEdge(Base):
    __tablename__ = "lineage_edges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    source_type = Column(SAEnum(AssetType), nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False)
    target_type = Column(SAEnum(AssetType), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    relationship_type = Column(String, nullable=False)
    edge_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Model(Base):
    __tablename__ = "models"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    version_tag = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))
    doc_type = Column(String)
    name = Column(String, nullable=False)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GovernanceReview(Base):
    __tablename__ = "governance_reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    status = Column(String, default="pending")
    findings = Column(Text)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)