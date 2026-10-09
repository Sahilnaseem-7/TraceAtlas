from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, LineageEdge, Membership, AuditEvent
from app.schemas.schemas import LineageEdgeCreate, LineageEdgeResponse
from app.services.lineage import get_downstream_impact
import uuid

router = APIRouter(prefix="/api/lineage", tags=["lineage"])

@router.post("/edges", response_model=LineageEdgeResponse)
async def create_edge(
    edge_in: LineageEdgeCreate,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Verify workspace access
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id, Membership.workspace_id == workspace_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")

    edge = LineageEdge(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        source_type=edge_in.source_type,
        source_id=edge_in.source_id,
        target_type=edge_in.target_type,
        target_id=edge_in.target_id,
        relationship_type=edge_in.relationship_type
    )
    db.add(edge)
    return edge

@router.get("/graph", response_model=list[LineageEdgeResponse])
async def get_graph(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LineageEdge).where(LineageEdge.workspace_id == workspace_id))
    return result.scalars().all()

@router.get("/impact")
async def impact_analysis(
    workspace_id: uuid.UUID = Query(...),
    source_type: str = Query(...),
    source_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    impacts = await get_downstream_impact(db, workspace_id, source_type, source_id)
    return {"source": {"type": source_type, "id": source_id}, "impacts": impacts}