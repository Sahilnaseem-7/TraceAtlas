from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import LineageEdge, AssetType
from uuid import UUID
from typing import List, Dict, Set, Tuple

async def get_downstream_impact(db: AsyncSession, workspace_id: UUID, source_type: str, source_id: UUID) -> List[Dict]:
    """
    BFS to find all downstream dependencies.
    Returns a list of affected assets with their paths.
    """
    visited: Set[Tuple[str, UUID]] = set()
    queue: List[Tuple[str, UUID, List[UUID]]] = [(source_type, source_id, [])]
    impacts = []

    while queue:
        curr_type, curr_id, path = queue.pop(0)
        
        if (curr_type, curr_id) in visited:
            continue
        visited.add((curr_type, curr_id))

        if curr_type != source_type or curr_id != source_id:
            impacts.append({
                "type": curr_type,
                "id": curr_id,
                "path": path
            })

        # Find edges where current node is the source
        stmt = select(LineageEdge).where(
            LineageEdge.workspace_id == workspace_id,
            LineageEdge.source_type == curr_type,
            LineageEdge.source_id == curr_id
        )
        result = await db.execute(stmt)
        edges = result.scalars().all()

        for edge in edges:
            next_path = path + [edge.target_id]
            queue.append((edge.target_type.value, edge.target_id, next_path))

    return impacts