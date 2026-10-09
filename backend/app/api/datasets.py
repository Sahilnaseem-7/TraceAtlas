import os
from pathlib import Path
from uuid import uuid4, UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import AuditEvent, Dataset, DatasetVersion, Membership, User
from app.schemas.schemas import DatasetCreate, DatasetResponse, DatasetUpdate, DatasetVersionResponse
from app.services.profiling import profile_dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])
ALLOWED_EXTENSIONS = {".csv", ".parquet", ".pq"}
CHUNK_SIZE = 1024 * 1024


async def verify_workspace_access(db: AsyncSession, user: User, workspace_id: UUID) -> None:
    result = await db.execute(
        select(Membership.id).where(
            Membership.user_id == user.id,
            Membership.workspace_id == workspace_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not authorized for this workspace")


async def get_accessible_dataset(db: AsyncSession, user: User, dataset_id: UUID) -> Dataset:
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    await verify_workspace_access(db, user, dataset.workspace_id)
    return dataset


def add_audit_event(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    user_id: UUID,
    event_type: str,
    resource_type: str,
    resource_id: UUID,
    details: dict,
) -> None:
    db.add(AuditEvent(
        id=uuid4(),
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    ))


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_in: DatasetCreate,
    workspace_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(db, current_user, workspace_id)
    dataset = Dataset(
        id=uuid4(),
        workspace_id=workspace_id,
        name=dataset_in.name.strip(),
        description=dataset_in.description,
        source=dataset_in.source,
        owner=dataset_in.owner,
        format=dataset_in.format,
        tags=dataset_in.tags,
    )
    db.add(dataset)
    await db.flush()
    add_audit_event(
        db, workspace_id=workspace_id, user_id=current_user.id,
        event_type="dataset_created", resource_type="dataset",
        resource_id=dataset.id, details={"name": dataset.name},
    )
    return dataset


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    workspace_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(db, current_user, workspace_id)
    result = await db.execute(
        select(Dataset).where(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_accessible_dataset(db, current_user, dataset_id)


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: UUID,
    updates: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dataset = await get_accessible_dataset(db, current_user, dataset_id)
    changes = updates.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] is not None:
        changes["name"] = changes["name"].strip()
    for field, value in changes.items():
        setattr(dataset, field, value)
    await db.flush()
    add_audit_event(
        db, workspace_id=dataset.workspace_id, user_id=current_user.id,
        event_type="dataset_updated", resource_type="dataset",
        resource_id=dataset.id, details={"changed_fields": list(changes.keys())},
    )
    return dataset


@router.get("/{dataset_id}/versions", response_model=list[DatasetVersionResponse])
async def list_dataset_versions(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await get_accessible_dataset(db, current_user, dataset_id)
    result = await db.execute(
        select(DatasetVersion)
        .where(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.created_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/{dataset_id}/versions",
    response_model=DatasetVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_and_profile(
    dataset_id: UUID,
    version_tag: str = Query(..., min_length=1, max_length=100),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dataset = await get_accessible_dataset(db, current_user, dataset_id)
    version_tag = version_tag.strip()
    if not version_tag:
        raise HTTPException(status_code=422, detail="Version tag cannot be blank")

    existing = await db.execute(
        select(DatasetVersion.id).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_tag == version_tag,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="This version tag already exists")

    original_name = file.filename or ""
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only CSV and Parquet files are supported")

    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uuid4().hex}{extension}"
    total_bytes = 0

    try:
        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit",
                    )
                destination.write(chunk)

        if total_bytes == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            profile_data = profile_dataset(str(file_path))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not profile the uploaded file: {exc}") from exc

        if not dataset.format:
            dataset.format = extension.lstrip(".").upper()

        version = DatasetVersion(
            id=uuid4(),
            dataset_id=dataset_id,
            version_tag=version_tag,
            record_count=profile_data["record_count"],
            column_count=profile_data["column_count"],
            schema_snapshot=profile_data["schema_snapshot"],
            content_hash=profile_data["content_hash"],
            profile_results=profile_data,
            file_path=str(file_path),
        )
        db.add(version)
        await db.flush()

        add_audit_event(
            db, workspace_id=dataset.workspace_id, user_id=current_user.id,
            event_type="version_created", resource_type="dataset_version",
            resource_id=version.id,
            details={"dataset_id": str(dataset_id), "tag": version_tag, "content_hash": profile_data["content_hash"]},
        )
        return version
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
