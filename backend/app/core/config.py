import secrets
from string import digits, punctuation, ascii_letters
from typing import Any, Dict, List, Union, Optional

from dotenv import load_dotenv
from pydantic import EmailStr, AnyHttpUrl, BaseSettings, validator
from databases import DatabaseURL

load_dotenv(".env")


class Settings(BaseSettings):
    API_STR: str = "/api"
    PROJECT_NAME: str = "example_application"
    FRONTEND_URL: str = "localhost:5173"
    SERVER_HOST: str = "http://localhost:8000/"

    # JWT token
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24  # one day
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # one week
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"

    # BACKEND CORS ORIGINS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Mongodb settings
    MONGODB_URL: str = ""
    MONGO_HOST: str = "localhost"
    MONGO_PORT: str = "27017"
    MONGO_USER: str = "root"
    MONGO_PASS: str = "root"
    MONGO_DB: str = "realDB"

    if not MONGODB_URL:
        MONGODB_URL = DatabaseURL(
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
        )

    database_name: str = MONGO_DB

    # SMTP
    SMTP_TLS: bool = False
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    PASSWORD_MIN_LENGTH: int = 6
    PASSWORD_MAX_LENGTH: int = 32
    PASSWORD_CHARS = "".join([ascii_letters, digits, punctuation])

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
