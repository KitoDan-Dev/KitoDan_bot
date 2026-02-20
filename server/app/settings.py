from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APPDATA_ROOT = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "KitoDan"
DEFAULT_SERVER_ENV = APPDATA_ROOT / "server.env"


def ensure_server_env() -> Path:
    APPDATA_ROOT.mkdir(parents=True, exist_ok=True)
    (APPDATA_ROOT / "data").mkdir(parents=True, exist_ok=True)
    (APPDATA_ROOT / "logs").mkdir(parents=True, exist_ok=True)

    if not DEFAULT_SERVER_ENV.exists():
        DEFAULT_SERVER_ENV.write_text(
            "\n".join(
                [
                    "PORT=4891",
                    "OLLAMA_MODEL=llama3.1:8b",
                    "OLLAMA_BASE_URL=http://localhost:11434",
                    "SYSTEM_PROFILE_PATH=profiles/KitoDan.md",
                    f"DB_PATH={str(APPDATA_ROOT / 'data' / 'kitodan.db')}",
                    f"LOG_PATH={str(APPDATA_ROOT / 'logs' / 'server.log')}",
                    "CONTEXT_TURNS=20",
                    "ALLOWED_ORIGIN=http://localhost:5173",
                ]
            ),
            encoding="utf-8",
        )
    return DEFAULT_SERVER_ENV


class Settings(BaseSettings):
    port: int = 4891
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    system_profile_path: str = "profiles/KitoDan.md"
    db_path: str = str(APPDATA_ROOT / "data" / "kitodan.db")
    log_path: str = str(APPDATA_ROOT / "logs" / "server.log")
    context_turns: int = 20
    allowed_origin: str = "http://localhost:5173"
    server_version: str = "0.3.0"

    model_config = SettingsConfigDict(
        env_file=str(ensure_server_env()),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
