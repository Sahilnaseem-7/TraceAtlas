import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.models import User, Organization, Workspace, Membership, Role
import uuid

# Using aiosqlite for isolated, fast local testing without needing a separate Postgres container
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(id=uuid.uuid4(), email="test@example.com", hashed_password=get_password_hash("password"), full_name="Test User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    org = Organization(id=uuid.uuid4(), name="Test Org")
    db_session.add(org)
    await db_session.commit()
    
    ws = Workspace(id=uuid.uuid4(), org_id=org.id, name="Test WS")
    db_session.add(ws)
    await db_session.commit()
    
    mem = Membership(user_id=user.id, workspace_id=ws.id, role=Role.OWNER)
    db_session.add(mem)
    await db_session.commit()
    
    return {"user": user, "workspace": ws}

@pytest_asyncio.fixture
async def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user["user"].id)})
    return {"Authorization": f"Bearer {token}"}