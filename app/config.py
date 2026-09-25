from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeForge Autonomous Coding Agent"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    workspace_dir: Path = Path("workspace")
    max_iterations: int = 3
    max_file_chars: int = 25_000
    max_workspace_files: int = 80
    command_timeout_seconds: int = 45

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.workspace_dir.mkdir(parents=True, exist_ok=True)