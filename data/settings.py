from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional
import os

from dotenv import load_dotenv


# ----------------------------------------------------------------------
# Env helpers
# ----------------------------------------------------------------------

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
        
    return v


def _env_int(name: str, default: int) -> int:
    v = _env(name)
    if v is None:
        return default
        
    try:
        return int(v)
        
    except ValueError as e:
        raise ValueError(f"Invalid int for env {name}={v!r}") from e


def _env_float(name: str, default: float) -> float:
    v = _env(name)
    if v is None:
        return default
        
    try:
        return float(v)
        
    except ValueError as e:
        raise ValueError(f"Invalid float for env {name}={v!r}") from e


# ----------------------------------------------------------------------
# Settings dataclass
# ----------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str

    base_dir: Path
    data_dir: Path
    src_dir: Path
    gui_dir: Path
    scripts_dir: Path
    services_dir: Path
    tests_dir: Path
    db_dir: Path
    db_path: Path
    log_dir: Path
    
    example_steam_games_path: Path

    steam_api_key: Optional[str]
    steam_webapi_base_url: str
    steam_store_base_url: str

    http_timeout_s: float
    http_retries: int
    http_backoff_s: float
    user_agent: str

    store_request_delay_s: float
    store_cache_ttl_s: int


# ----------------------------------------------------------------------
# Project base dir (repo root)
# ----------------------------------------------------------------------

def _default_base_dir(app_name: str) -> Path:
    # Project root (…/steamteam)
    return Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# Load settings
# ----------------------------------------------------------------------

def load_settings() -> Settings:
    app_name: Final[str] = "steamteam"

    # Load .env file early so everything below sees it
    load_dotenv(_default_base_dir(app_name) / ".env")

    base_dir = Path(_env("STEAMTEAM_BASE_DIR") or _default_base_dir(app_name)).expanduser()

    data_dir = Path(_env("STEAMTEAM_DATA_DIR") or (base_dir / "data")).expanduser()
    src_dir = Path(_env("STEAMTEAM_SRC_DIR") or (base_dir / "src")).expanduser()
    gui_dir = Path(_env("STEAMTEAM_GUI_DIR") or (base_dir / "gui")).expanduser()
    scripts_dir = Path(_env("STEAMTEAM_SCRIPTS_DIR") or (base_dir / "scripts")).expanduser()
    services_dir = Path(_env("STEAMTEAM_SERVICES_DIR") or (base_dir / "services")).expanduser()
    tests_dir = Path(_env("STEAMTEAM_TESTS_DIR") or (base_dir / "tests")).expanduser()

    db_dir = Path(_env("STEAMTEAM_DB_DIR") or (data_dir / "db")).expanduser()
    db_path = Path(_env("STEAMTEAM_DB_PATH") or (db_dir / "steamteam.sqlite3")).expanduser()

    log_dir = Path(_env("STEAMTEAM_LOG_DIR") or (base_dir / "logs")).expanduser()
    
    example_steam_games_path = Path(_env("STEAMTEAM_EXAMPLE_STEAM_GAMES_PATH") or (data_dir / "example_steam_games.json")).expanduser() 

    steam_api_key = _env("STEAM_API_KEY")

    steam_webapi_base_url = _env("STEAM_WEBAPI_BASE_URL", "https://api.steampowered.com") or "https://api.steampowered.com"
    steam_store_base_url  = _env("STEAM_STORE_BASE_URL",  "https://store.steampowered.com/api") or "https://store.steampowered.com/api"

    http_timeout_s = _env_float("STEAMTEAM_HTTP_TIMEOUT_S", 10.0)
    http_retries = _env_int("STEAMTEAM_HTTP_RETRIES", 3)
    http_backoff_s = _env_float("STEAMTEAM_HTTP_BACKOFF_S", 0.5)

    user_agent = _env("USER_AGENT", "SteamTeam/1.0") or "SteamTeam/1.0"

    store_request_delay_s = _env_float("STEAMTEAM_STORE_DELAY_S", 0.20)
    store_cache_ttl_s = _env_int("STEAMTEAM_STORE_CACHE_TTL_S", 60 * 60 * 24 * 7) # 7 days
    
    for d in [data_dir, db_dir, log_dir, src_dir, gui_dir, scripts_dir, services_dir, tests_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    settings = Settings(
        app_name=app_name,
        base_dir=base_dir,
        data_dir=data_dir,
        src_dir=src_dir,
        gui_dir=gui_dir,
        scripts_dir=scripts_dir,
        services_dir=services_dir,
        tests_dir=tests_dir,
        db_dir=db_dir,
        db_path=db_path,
        log_dir=log_dir,
        example_steam_games_path=example_steam_games_path,
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


    return settings


# Global settings instance
SETTINGS: Final[Settings] = load_settings()
