import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    DATASET_PROFILE: str = "SMALL"  # SMALL, MEDIUM, LARGE
    GEMINI_API_KEY: str = ""
    GCP_PROJECT_ID: str = ""
    BIGQUERY_DATASET: str = "pulseops_ai"
    TELEMETRY_CSV_PATH: str = "datasets/equipment_telemetry.csv"

    # Support loading from .env file at project root or backend dir
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
