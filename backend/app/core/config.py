from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MOMA_ENDPOINT: str = ""
    MOMA_API_KEY: str = ""
    MOMA_MODEL: str = ""
    MOCK: bool = True


settings = Settings()
