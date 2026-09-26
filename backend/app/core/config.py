from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MOMA_ENDPOINT: str = ""
    MOMA_API_KEY: str = ""
    MOMA_MODEL: str = ""
    REDIS_URL: str = ""
    MINIO_ENDPOINT: str = ""
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "galaxy-files"
    MOCK: bool = True
    SANDBOX_MODE: str = "subprocess"


settings = Settings()
