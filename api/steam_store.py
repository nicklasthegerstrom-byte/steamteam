from time import sleep
import requests
from data.settings import SETTINGS


__all__ = ["fetch_store_metadata"]


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
            
            r = requests.get(url=url, params=params, timeout=TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            
            payload = r.json()
            return payload # Return directly
        
        except requests.RequestException:
            if attempt < retries - 1:
                sleep(backoff)
            
            else:
                return None
        
        except ValueError:
            # Invalid JSON
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
        return None
    
    info = app_data.get("data", {})
    name: str = info.get("name", "unknown")
    genres: list[str] = [g.get("description") for g in info.get("genres", []) if "description" in g]
    categories: list[str] = [c.get("description") for c in info.get("categories", []) if "description" in c]
    
    return {"appid": appid, "name": name, "genres": genres, "categories": categories}
    
