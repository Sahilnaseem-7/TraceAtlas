from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Dataset, DatasetVersion, AuditEvent, Membership
from app.schemas.schemas import DatasetCreate, DatasetResponse, DatasetVersionResponse
from app.services.profiling import profile_dataset
from app.core.config import settings
import uuid
import os
import datetime

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

async def verify_workspace_access(db: AsyncSession, user: User, workspace_id: uuid.UUID):
    result = await db.execute(
        select(Membership).where(Membership.user_id == user.id, Membership.workspace_id == workspace_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized for this workspace")

@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    dataset_in: DatasetCreate, 
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    await verify_workspace_access(db, current_user, workspace_id)
    
    dataset = Dataset(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name=dataset_in.name,
        description=dataset_in.description,
        source=dataset_in.source,
        owner=dataset_in.owner,
        format=dataset_in.format,
        tags=dataset_in.tags
    )
    db.add(dataset)
    
    audit = AuditEvent(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        user_id=current_user.id,
        event_type="dataset_created",
        resource_type="dataset",
        resource_id=dataset.id,
        details={"name": dataset.name}
    )
    db.add(audit)
    
    return dataset

@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    await verify_workspace_access(db, current_user, workspace_id)
    result = await db.execute(select(Dataset).where(Dataset.workspace_id == workspace_id))
    return result.scalars().all()

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    await verify_workspace_access(db, current_user, dataset.workspace_id)
    return dataset

@router.post("/{dataset_id}/versions", response_model=DatasetVersionResponse)
async def upload_and_profile(
    dataset_id: uuid.UUID,
    version_tag: str = Query(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    await verify_workspace_access(db, current_user, dataset.workspace_id)

    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Profile
    try:
        profile_data = profile_dataset(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Profiling failed: {str(e)}")

    version = DatasetVersion(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        version_tag=version_tag,
        record_count=profile_data["record_count"],
        column_count=profile_data["column_count"],
        schema_snapshot=profile_data["schema_snapshot"],
        content_hash=profile_data["content_hash"],
        profile_results=profile_data,
        file_path=file_path
    )
    db.add(version)

    audit = AuditEvent(
        id=uuid.uuid4(),
        workspace_id=dataset.workspace_id,
        user_id=current_user.id,
        event_type="version_created",
        resource_type="dataset_version",
        resource_id=version.id,
        details={"dataset_id": str(dataset_id), "tag": version_tag}
    )
    db.add(audit)

    return version