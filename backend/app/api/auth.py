from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, get_password_hash, verify_password
from app.models.models import Membership, Organization, Role, User, Workspace
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserResponse, WorkspaceResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_in.email.lower().strip()
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(
        id=uuid4(),
        email=email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name.strip(),
    )
    db.add(new_user)
    await db.flush()

    org = Organization(id=uuid4(), name=f"{new_user.full_name}'s Organization")
    db.add(org)
    await db.flush()

    workspace = Workspace(id=uuid4(), org_id=org.id, name="Default Workspace")
    db.add(workspace)
    await db.flush()

    db.add(Membership(user_id=new_user.id, workspace_id=workspace.id, role=Role.OWNER))
    await db.flush()
    return new_user


@router.post("/login", response_model=Token)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": create_access_token(data={"sub": str(user.id)}), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/workspaces", response_model=list[WorkspaceResponse])
async def get_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .join(Membership, Membership.workspace_id == Workspace.id)
        .where(Membership.user_id == current_user.id)
        .order_by(Workspace.created_at.asc())
    )
    return result.scalars().all()
