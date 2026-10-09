import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.models import Membership, Organization, Role, User, Workspace
from app.core.config import settings

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    # Reset data between tests while reusing the in-memory test engine.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.flush()

    org = Organization(id=uuid.uuid4(), name="Test Org")
    db_session.add(org)
    await db_session.flush()

    workspace = Workspace(id=uuid.uuid4(), org_id=org.id, name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    db_session.add(Membership(user_id=user.id, workspace_id=workspace.id, role=Role.OWNER))
    await db_session.commit()
    return {"user": user, "workspace": workspace}


@pytest_asyncio.fixture
async def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user["user"].id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(autouse=True)
async def isolated_upload_directory(tmp_path, monkeypatch):
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_path))
    yield
