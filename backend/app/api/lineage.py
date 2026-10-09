from uuid import uuid4, UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    AssetType, AuditEvent, Dataset, DatasetVersion, LineageEdge, Membership,
    Model, ModelVersion, User,
)
from app.schemas.schemas import LineageEdgeCreate, LineageEdgeResponse
from app.services.lineage import get_downstream_impact

router = APIRouter(prefix="/api/lineage", tags=["lineage"])


async def verify_workspace_access(db: AsyncSession, user: User, workspace_id: UUID) -> None:
    result = await db.execute(
        select(Membership.id).where(
            Membership.user_id == user.id,
            Membership.workspace_id == workspace_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not authorized for this workspace")


async def verify_asset_in_workspace(
    db: AsyncSession, workspace_id: UUID, asset_type: AssetType, asset_id: UUID
) -> None:
    if asset_type == AssetType.DATASET:
        stmt = select(Dataset.id).where(Dataset.id == asset_id, Dataset.workspace_id == workspace_id)
    elif asset_type == AssetType.DATASET_VERSION:
        stmt = (
            select(DatasetVersion.id)
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .where(DatasetVersion.id == asset_id, Dataset.workspace_id == workspace_id)
        )
    elif asset_type == AssetType.MODEL:
        stmt = select(Model.id).where(Model.id == asset_id, Model.workspace_id == workspace_id)
    elif asset_type == AssetType.MODEL_VERSION:
        stmt = (
            select(ModelVersion.id)
            .join(Model, Model.id == ModelVersion.model_id)
            .where(ModelVersion.id == asset_id, Model.workspace_id == workspace_id)
        )
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Lineage for {asset_type.value} assets is not yet supported by this MVP",
        )

    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f"{asset_type.value} asset not found in this workspace")


@router.post("/edges", response_model=LineageEdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_edge(
    edge_in: LineageEdgeCreate,
    workspace_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(db, current_user, workspace_id)
    if edge_in.source_type == edge_in.target_type and edge_in.source_id == edge_in.target_id:
        raise HTTPException(status_code=422, detail="An asset cannot depend on itself")

    await verify_asset_in_workspace(db, workspace_id, edge_in.source_type, edge_in.source_id)
    await verify_asset_in_workspace(db, workspace_id, edge_in.target_type, edge_in.target_id)

    duplicate = await db.execute(
        select(LineageEdge.id).where(
            LineageEdge.workspace_id == workspace_id,
            LineageEdge.source_type == edge_in.source_type,
            LineageEdge.source_id == edge_in.source_id,
            LineageEdge.target_type == edge_in.target_type,
            LineageEdge.target_id == edge_in.target_id,
            LineageEdge.relationship_type == edge_in.relationship_type,
        )
    )
    if duplicate.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="This lineage edge already exists")

    edge = LineageEdge(
        id=uuid4(),
        workspace_id=workspace_id,
        source_type=edge_in.source_type,
        source_id=edge_in.source_id,
        target_type=edge_in.target_type,
        target_id=edge_in.target_id,
        relationship_type=edge_in.relationship_type,
    )
    db.add(edge)
    await db.flush()
    db.add(AuditEvent(
        id=uuid4(),
        workspace_id=workspace_id,
        user_id=current_user.id,
        event_type="lineage_edge_created",
        resource_type="lineage_edge",
        resource_id=edge.id,
        details={
            "source_type": edge.source_type.value,
            "source_id": str(edge.source_id),
            "target_type": edge.target_type.value,
            "target_id": str(edge.target_id),
            "relationship_type": edge.relationship_type,
        },
    ))
    return edge


@router.get("/graph", response_model=list[LineageEdgeResponse])
async def get_graph(
    workspace_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(db, current_user, workspace_id)
    result = await db.execute(
        select(LineageEdge)
        .where(LineageEdge.workspace_id == workspace_id)
        .order_by(LineageEdge.created_at.asc())
    )
    return result.scalars().all()


@router.get("/impact")
async def impact_analysis(
    workspace_id: UUID = Query(...),
    source_type: AssetType = Query(...),
    source_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(db, current_user, workspace_id)
    await verify_asset_in_workspace(db, workspace_id, source_type, source_id)
    impacts = await get_downstream_impact(db, workspace_id, source_type.value, source_id)
    return {"source": {"type": source_type.value, "id": str(source_id)}, "impacts": impacts}
