from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ML_ARTIFACT_DIR: str

    DATABASE_URL: str = "sqlite:///./churn_dashboard.db"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 12

    # Admin login is checked against the admin_users table in the DB (see app/seed_admin.py).
    # These are only used to seed that table the first time it's empty.
    ADMIN_SEED_USERNAME: str = ""
    ADMIN_SEED_PASSWORD: str = ""

    RISK_THRESHOLD_HIGH: float = 0.6
    RISK_THRESHOLD_MEDIUM: float = 0.35


settings = Settings()


