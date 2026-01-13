from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "UrbanVibe API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    SUPABASE_JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:19006",
        "http://localhost:8081",
        "http://localhost:8000",
        "*",
    ]

    # App Mode
    DEMO_MODE: bool = False

    # Supabase Client (for authentication)
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # QR System
    QR_JWT_SECRET: str = "change-me-in-prod-qr-secret"
    QR_JWT_ISSUER: str = "urbanvibe-qr"
    QR_JWT_AUDIENCE: str = "urbanvibe-app"
    QR_TOKEN_DEFAULT_TTL_SECONDS: int = 120

    # SMTP Configuration
    MAIL_USERNAME: str = "contacto@urbanvibe.cl"
    MAIL_PASSWORD: str
    MAIL_FROM: str = "contacto@urbanvibe.cl"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "mail.urbanvibe.cl"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    
    # Notifications
    SUPER_ADMIN_EMAIL: str = "admin@urbanvibe.cl"

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()
