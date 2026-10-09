from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or backend/.env."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./traceatlas.db"
    SECRET_KEY: str = "dev-only-change-this-secret-key-before-deployment"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
