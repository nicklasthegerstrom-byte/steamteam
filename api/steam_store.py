from time import sleep
import requests
from data.settings import SETTINGS
from services.logger import get_logger


__all__ = ["fetch_store_metadata"]
log = get_logger(__name__)


# ---------- Settings ----------

_FB_BASE_URL = "https://store.steampowered.com"
BASE_URL = (
    SETTINGS.steam_store_base_url
    if SETTINGS.steam_store_base_url and SETTINGS.steam_store_base_url.startswith("http")
    else _FB_BASE_URL
    )

TIMEOUT = SETTINGS.http_timeout_s
HEADERS = {"User-Agent": SETTINGS.user_agent}
RETRIES = SETTINGS.http_retries
BACKOFF = SETTINGS.http_backoff_s
STORE_DELAY = SETTINGS.store_request_delay_s


# ---------- Internal functions ----------

def _store_request_with_retry(url: str, params: dict, retries: int = RETRIES, backoff: float = BACKOFF) -> dict | None:
    """
    Helper for store requests with retry and backoff.
    Returns JSON dict if successful, None on permanent failure.
    """
    for attempt in range(retries):
        try:
            # Respect store request delay
            sleep(STORE_DELAY)
            log.debug("Steam Store request url=%s params=%s", url, params)
            r = requests.get(url=url, params=params, timeout=TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            
            payload = r.json()
            return payload # Return directly
        
        except requests.RequestException:
            log.warning("Steam Store request failed (attempt %d/%d) url=%s", attempt + 1, retries, url)
            if attempt < retries - 1:
                sleep(backoff)
            
            else:
                log.error("Steam Store request failed permanently url=%s params=%s", url, params)
                return None
        
        except ValueError:
            # Invalid JSON
            log.error("Steam Store returned invalid JSON url=%s params=%s", url, params)
            return None
    
    return None

def fetch_store_metadata(appid: int, cc: str = "us", lang: str = "english") -> dict | None:
    """
    Fetch genres and categories from Steam Storefront API.
    Returns a dict with keys: appid, name, genres, categories or None if failed.
    """
    url = f"{BASE_URL}/api/appdetails"
    params = {"appids": appid, "cc": cc, "l": lang}
    data = _store_request_with_retry(url=url, params=params)
    
    if not data:
        return None
    
    app_data = data.get(str(appid), {})
    if not app_data.get("success"):
        log.debug("Store metadata success=false appid=%s", appid)
        return None
    
    info = app_data.get("data", {})
    name: str = info.get("name", "unknown")
    genres: list[str] = [g.get("description") for g in info.get("genres", []) if "description" in g]
    categories: list[str] = [c.get("description") for c in info.get("categories", []) if "description" in c]
    log.info("Store metadata fetched appid=%s", appid)
    return {"appid": appid, "name": name, "genres": genres, "categories": categories}
    
