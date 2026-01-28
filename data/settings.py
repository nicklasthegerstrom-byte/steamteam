from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional
import os

# Helper to read env vars with optional default
def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return v

# Helper to read int/float env vars with default and error handling 
def _env_int(name: str, default: int) -> int:
    v = _env(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError as e:
        raise ValueError(f"Invalid int for env {name}={v!r}") from e

# Helper to read int/float env vars with default and error handling
def _env_float(name: str, default: float) -> float:
    v = _env(name)
    if v is None:
        return default
    try:
        return float(v)
    except ValueError as e:
        raise ValueError(f"Invalid float for env {name}={v!r}") from e

# Settings dataclass, one typed object passed around instead of many loose parameters.
@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str

    # Paths
    data_dir: Path
    db_path: Path
    cache_dir: Path
    export_dir: Path
    log_dir: Path

    # Steam endpoints + credentials
    steam_api_key: Optional[str]
    steam_webapi_base_url: str
    steam_store_base_url: str

    # HTTP behavior
    http_timeout_s: float
    http_retries: int
    http_backoff_s: float
    user_agent: str

    # Rate limiting / caching
    store_request_delay_s: float
    store_cache_ttl_s: int


def _default_data_dir(app_name: str) -> Path:
    # Windows: %LOCALAPPDATA%\steamteam
    # Fallback: ~/.steamteam
    localappdata = os.getenv("LOCALAPPDATA")
    if localappdata and localappdata.strip():
        return Path(localappdata) / app_name
    return Path.home() / f".{app_name}"

# Load settings from environment variables with defaults
def load_settings(create_dirs: bool = True) -> Settings:
    app_name: Final[str] = "steamteam"

    data_dir = Path(_env("STEAMTEAM_DATA_DIR") or _default_data_dir(app_name)).expanduser()
    db_path = Path(_env("STEAMTEAM_DB_PATH") or (data_dir / "steamteam.sqlite3")).expanduser()
    cache_dir = Path(_env("STEAMTEAM_CACHE_DIR") or (data_dir / "cache")).expanduser()
    export_dir = Path(_env("STEAMTEAM_EXPORT_DIR") or (data_dir / "exports")).expanduser()
    log_dir = Path(_env("STEAMTEAM_LOG_DIR") or (data_dir / "logs")).expanduser()

    if create_dirs:
        for d in (data_dir, cache_dir, export_dir, log_dir):
            d.mkdir(parents=True, exist_ok=True)

    steam_api_key = _env("STEAM_API_KEY")  # optional in tests/demo

    steam_webapi_base_url = _env("STEAM_WEBAPI_BASE_URL", "https://api.steampowered.com")
    steam_store_base_url = _env("STEAM_STORE_BASE_URL", "https://store.steampowered.com")

    http_timeout_s = _env_float("STEAMTEAM_HTTP_TIMEOUT_S", 10.0)
    http_retries = _env_int("STEAMTEAM_HTTP_RETRIES", 3)
    http_backoff_s = _env_float("STEAMTEAM_HTTP_BACKOFF_S", 0.5)

    user_agent = _env("STEAMTEAM_USER_AGENT", f"{app_name}/1.0 (+school project)") or f"{app_name}/1.0"

    store_request_delay_s = _env_float("STEAMTEAM_STORE_DELAY_S", 0.20)
    store_cache_ttl_s = _env_int("STEAMTEAM_STORE_CACHE_TTL_S", 60 * 60 * 24 * 7)  # 7 days

    return Settings(
        app_name=app_name,
        data_dir=data_dir,
        db_path=db_path,
        cache_dir=cache_dir,
        export_dir=export_dir,
        log_dir=log_dir,
        steam_api_key=steam_api_key,
        steam_webapi_base_url=steam_webapi_base_url,
        steam_store_base_url=steam_store_base_url,
        http_timeout_s=http_timeout_s,
        http_retries=http_retries,
        http_backoff_s=http_backoff_s,
        user_agent=user_agent,
        store_request_delay_s=store_request_delay_s,
        store_cache_ttl_s=store_cache_ttl_s,
    )

# Global settings instance
SETTINGS: Final[Settings] = load_settings()
