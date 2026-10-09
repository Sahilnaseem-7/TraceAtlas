from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, datasets, lineage
from app.core.config import settings
from app.core.database import Base, engine

app = FastAPI(
    title="TraceAtlas API",
    description="Dataset provenance, profiling, and lineage API.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(lineage.router)


@app.on_event("startup")
async def startup() -> None:
    # Convenient for local MVP use. Production deployments should run Alembic migrations.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown() -> None:
    await engine.dispose()


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "healthy"}
