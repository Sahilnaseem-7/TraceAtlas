from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.models.models import User, Organization, Workspace, Membership, Role
from app.schemas.schemas import UserCreate, UserResponse, Token, WorkspaceCreate, WorkspaceResponse
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    await db.flush()

    # Create default org and workspace
    org = Organization(id=uuid.uuid4(), name=f"{user_in.full_name}'s Org")
    db.add(org)
    await db.flush()

    ws = Workspace(id=uuid.uuid4(), org_id=org.id, name="Default Workspace")
    db.add(ws)
    await db.flush()

    membership = Membership(user_id=new_user.id, workspace_id=ws.id, role=Role.OWNER)
    db.add(membership)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    # Note: FastAPI OAuth2PasswordRequestForm is usually used, but for simplicity:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/workspaces", response_model=list[WorkspaceResponse])
async def get_workspaces(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Workspace).join(Membership).where(Membership.user_id == current_user.id)
    )
    return result.scalars().all()