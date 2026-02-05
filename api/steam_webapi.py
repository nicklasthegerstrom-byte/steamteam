from time import sleep
from urllib.parse import urlparse
import requests

from data.settings import SETTINGS
from services.logger import get_logger

__all__ = ["resolve_steam_id", "fetch_owned_games"]
log = get_logger(__name__)

# Steam Web API key
STEAM_API_KEY = SETTINGS.steam_api_key

# Fallback base URL
_FB_BASE_URL = "https://api.steampowered.com"

# Base URL, try from config, otherwise use fallback
BASE_URL = (
    SETTINGS.steam_webapi_base_url
    if SETTINGS.steam_webapi_base_url and SETTINGS.steam_webapi_base_url.startswith("http")
    else _FB_BASE_URL
)

TIMEOUT = SETTINGS.http_timeout_s
RETRIES = SETTINGS.http_retries
BACKOFF = SETTINGS.http_backoff_s

HEADERS = {
    "User-Agent": SETTINGS.user_agent,
}

if not STEAM_API_KEY:
    log.warning("STEAM_API_KEY not found. Only mock/local flows will work.")


# ------------------ Internal function ------------------

def _request_with_retry(url: str, params: dict, retries: int = RETRIES, backoff: float = BACKOFF) -> dict:
    """
    Internal helper to perform a GET request with retries/backoff.
    Raises RuntimeError on network failure or ValueError on invalid JSON.
    """
    for attempt in range(retries):
        try:
            log.debug("Steam Web API request url=%s params_keys=%s", url, list(params.keys()))
            r = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            payload = r.json()
            return payload  # return directly
            
        except requests.RequestException as e:
            if attempt < retries - 1:
                log.warning("Steam Web API request failed (attempt %d/%d): %s", attempt + 1, retries, e)
                sleep(backoff)
                
            else:
                log.error("Steam Web API request failed permanently after %d attempts", retries)
                raise RuntimeError(f"Steam API request failed after {retries} attempts: {e}")
                
        except ValueError:
            raise ValueError("Steam API returned invalid JSON")

    # If retries is zero or loop exits without returning, raise to satisfy return contract
    raise RuntimeError(f"Steam API request failed after {retries} attempts")


# ------------------ Web API functions ------------------

def resolve_steam_id(value: str) -> str:
    """
    Resolve SteamID64 from:
    - SteamID64
    - Vanity name
    - Full Steam profile URL (/profiles/ or /id/)
    """
    if not STEAM_API_KEY:
        raise RuntimeError("STEAM_API_KEY is required for real Steam API calls")

    value = value.strip()

    # Full URL
    if value.startswith("http") and "/" in value:
        parsed = urlparse(value)
        parts = parsed.path.strip("/").split("/")

        if len(parts) != 2:
            raise ValueError("Invalid Steam profile URL")

        kind, identifier = parts
        if kind == "profiles":
            return identifier
            
        elif kind == "id":
            vanity = identifier
            
        else:
            raise ValueError("Profile URL must contain /id/ or /profiles/")

    # Raw SteamID64
    elif value.isdigit() and len(value) == 17:
        return value

    # Vanity name
    elif "".join(c for c in value if c not in "-_").isalnum():
        vanity = value

    else:
        raise ValueError("Invalid Steam identifier")

    # Resolve via Steam API
    url = f"{BASE_URL}/ISteamUser/ResolveVanityURL/v0001/"
    params = {"key": STEAM_API_KEY, "vanityurl": vanity}
    payload = _request_with_retry(url, params)

    data = payload.get("response", {})
    if data.get("success") == 1:
        return data.get("steamid")
        
    else:
        raise ValueError("Could not resolve Steam ID: invalid vanity name or SteamID")


def fetch_owned_games(steam_id: str) -> list[dict]:
    """
    Fetch all owned games for a user from Steam Web API.
    """
    if not STEAM_API_KEY:
        raise RuntimeError("STEAM_API_KEY is required for real Steam API calls")

    url = f"{BASE_URL}/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
    }

    payload = _request_with_retry(url, params)    
    data = payload.get("response", {})    
    games = data.get("games", [])
    log.info("Owned games fetched steam_id=%s count=%d", steam_id, len(games))
    return games


