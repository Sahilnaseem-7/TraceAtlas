from collections import deque
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AssetType, LineageEdge


async def get_downstream_impact(
    db: AsyncSession, workspace_id: UUID, source_type: AssetType | str, source_id: UUID
) -> list[dict[str, Any]]:
    """Return each reachable downstream asset once, preserving a shortest discovered path."""
    if not isinstance(source_type, AssetType):
        source_type = AssetType(source_type)

    queue = deque([(source_type, source_id, [])])
    visited: set[tuple[AssetType, UUID]] = set()
    impacts: list[dict[str, Any]] = []

    while queue:
        current_type, current_id, path = queue.popleft()
        key = (current_type, current_id)
        if key in visited:
            continue
        visited.add(key)

        if key != (source_type, source_id):
            impacts.append({
                "type": current_type.value,
                "id": str(current_id),
                "path": path,
            })

        result = await db.execute(
            select(LineageEdge).where(
                LineageEdge.workspace_id == workspace_id,
                LineageEdge.source_type == current_type,
                LineageEdge.source_id == current_id,
            )
        )
        for edge in result.scalars().all():
            queue.append((edge.target_type, edge.target_id, path + [str(edge.target_id)]))

    return impacts
