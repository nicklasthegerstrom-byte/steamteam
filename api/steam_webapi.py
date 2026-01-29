from urllib.parse import urlparse
import requests

from data.settings import SETTINGS

STEAM_API_KEY = SETTINGS.steam_api_key

if not STEAM_API_KEY:
    print("Warning: STEAM_API_KEY not found. Only mock functions will work.")

__all__ = ["resolve_steam_id", "fetch_owned_games"]

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
        if kind == "id":
            vanity = identifier
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

    # Resolve vanity via API
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {"key": STEAM_API_KEY, "vanityurl": vanity}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        payload = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Vanity URL request failed: {e}")
    except ValueError:
        raise RuntimeError("Vanity URL API returned invalid JSON")

    data = payload.get("response", {})
    if data.get("success") == 1:
        return data.get("steamid")

    raise ValueError("Could not resolve Steam ID")


def fetch_owned_games(steam_id: str) -> list[dict]:
    """
    Fetch all owned games for a user from Steam Web API.
    """
    if not STEAM_API_KEY:
        raise RuntimeError("STEAM_API_KEY is required for real Steam API calls")

    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Steam API request failed: {e}")
    except ValueError:
        raise RuntimeError("Steam API returned invalid JSON")

    return data.get("response", {}).get("games", [])
