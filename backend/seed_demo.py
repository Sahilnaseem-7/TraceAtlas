import asyncio
import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models.models import User, Organization, Workspace, Membership, Role, Dataset, DatasetVersion, LineageEdge, AssetType
from app.core.security import get_password_hash

async def seed():
    async with async_session() as db:
        user = User(id=uuid.uuid4(), email="demo@traceatlas.com", hashed_password=get_password_hash("demo123"), full_name="Demo User")
        db.add(user)
        await db.flush()
        
        org = Organization(id=uuid.uuid4(), name="Demo Corp")
        db.add(org)
        await db.flush()
        
        ws = Workspace(id=uuid.uuid4(), org_id=org.id, name="Demo Workspace")
        db.add(ws)
        await db.flush()
        
        mem = Membership(user_id=user.id, workspace_id=ws.id, role=Role.OWNER)
        db.add(mem)
        
        ds1 = Dataset(id=uuid.uuid4(), workspace_id=ws.id, name="Raw Customer Data", source="Internal CRM", owner="Data Team", governance_status="approved")
        ds2 = Dataset(id=uuid.uuid4(), workspace_id=ws.id, name="Cleaned Training Set", source="Data Pipeline", owner="ML Team", governance_status="pending")
        db.add_all([ds1, ds2])
        await db.flush()
        
        v1 = DatasetVersion(
            id=uuid.uuid4(), dataset_id=ds1.id, version_tag="v1.0", 
            record_count=10000, column_count=15, 
            schema_snapshot={"id": "int64", "name": "object", "email": "object"},
            profile_results={"missing_values": {"email": 150}, "duplicate_rows": 12}
        )
        v2 = DatasetVersion(
            id=uuid.uuid4(), dataset_id=ds2.id, version_tag="v1.0", 
            record_count=8500, column_count=12, 
            schema_snapshot={"id": "int64", "feature_1": "float64", "feature_2": "float64"},
            profile_results={"missing_values": {}, "duplicate_rows": 0}
        )
        db.add_all([v1, v2])
        
        edge = LineageEdge(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            source_type=AssetType.DATASET,
            source_id=ds1.id,
            target_type=AssetType.DATASET,
            target_id=ds2.id,
            relationship_type="cleaned_and_filtered"
        )
        db.add(edge)
        
        await db.commit()
        print("✅ Demo data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
