from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "RT"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    GROQ_API_KEY: str
    DATABASE_URL: str
    SECRET_KEY: str
    SESSION_MAX_AGE: int

    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()