from data.settings import SETTINGS
from services.logger import setup_logging, get_logger
from src.db import create_tables

def bootstrap() -> None:
    setup_logging(SETTINGS.log_dir)
    log = get_logger(__name__)

    create_tables(SETTINGS.db_path)

    if not SETTINGS.steam_api_key:
        log.warning("STEAM_API_KEY is not set. Live Steam sync will be unavailable.")

    log.info("Bootstrap complete")
