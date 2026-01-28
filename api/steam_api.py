from urllib.parse import urlparse
import os
import requests
import json
import random
import string

from data.settings import env_load

__all__ = ["get_user_top_games", "get_fake_user_top_games"]

# ------------------ Load Steam API key ------------------

STEAM_API_KEY = os.getenv("STEAM_API_KEY")

if not STEAM_API_KEY:
    print("Warning: STEAM_API_KEY not found. Only mock functions will work.")


# ------------------ Internal helper functions ------------------

def _fetch_user_games(steam_id):
    """Fetch all owned games for a user from Steam Web API."""
    
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


def _fetch_store_metadata(appid, cc="us", lang="english"):
    """Fetch genres and categories from Steam Storefront API."""
    
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": cc, "l": lang}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError):
        return [], []  # Fail soft if Storefront API fails

    app_data = data.get(str(appid), {})
    if not app_data.get("success"):
        return [], []

    info = app_data.get("data", {})
    genres = [g.get("description") for g in info.get("genres", []) if "description" in g]
    categories = [c.get("description") for c in info.get("categories", []) if "description" in c]

    return genres, categories


def _enrich_games(games, limit):
    """Sort games by playtime_forever and enrich with store metadata."""
    
    games = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)[:limit]

    enriched = []
    for game in games:
        genres, categories = _fetch_store_metadata(game["appid"])
        enriched.append({
            "appid": game["appid"],
            "name": game.get("name"),
            "playtime_forever": game.get("playtime_forever", 0),
            "playtime_2weeks": game.get("playtime_2weeks"),
            "genres": genres,
            "categories": categories
        })

    return enriched


def _resolve_steam_id(value):
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
        else:
            raise ValueError("Profile URL must contain /id/ or /profiles/")

    # Raw SteamID64
    elif value.isdigit() and len(value) == 17:
        return value

    # Raw vanity name
    elif "".join(c for c in value if c not in "-_").isalnum():
        vanity = value

    else:
        raise ValueError("Invalid Steam identifier")

    # Resolve vanity via Steam API
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


# ------------------ Public function ------------------

def get_user_top_games(user_string, top_n=5):
    """
    Return the user's top N games enriched with genre and category data.

    Parameters:
        user_input (str): SteamID64, vanity name, or full Steam profile URL.
        top_n (int): Number of top games to return.

    Returns:
        dict: {
            "steam_id": <SteamID64>,
            "game_count": <number of games returned>,
            "games": [enriched game dicts]
        }
    """
    
    steam_id = _resolve_steam_id(user_string)
    games = _fetch_user_games(steam_id)
    enriched_games = _enrich_games(games, top_n)

    return {
        "steam_id": steam_id,
        "game_count": len(enriched_games),
        "games": enriched_games
    }

def get_fake_user_top_games(user_string, top_n=5):
    """
    Generate fake enriched game data for testing.
    
    Parameters:
        user_string (str): Any string, just used to simulate a user
        top_n (int): Number of top games to generate
    
    Returns:
        dict: Mock Steam user game data
    """
    
    result = {
        "steam_id": ''.join(str(random.randint(0, 9)) for _ in range(17)),
        "game_count": top_n,
        "games": []
    }

    for _ in range(top_n):
        fake_game = {
            "appid": random.randint(1, 999999),
            "name": ''.join(random.choices(string.ascii_letters + string.digits + " ", k=10)).title(),
            "playtime_forever": random.randint(1, 999999),
            "playtime_2weeks": random.choice([random.randint(1, 1000), None]),
            "genres": random.sample(
                ["RPG", "Shooter", "Adventure", "Simulation", "Racing", "Massively Multiplayer"],
                k=random.randint(0, 5)
            ),
            "categories": random.sample(
                [
                    "Single-player", "Multi-player", "Co-op", "PVP", "Online PVP",
                    "Online Co-op", "Family Sharing", "Steam Cloud", "Steam Achievements",
                    "Stereo Sound", "In-App Purchases", "Camera Comfort"
                ],
                k=random.randint(0, 8)
            )
        }
        result["games"].append(fake_game)

    return result
        

# ------------------ Example ------------------

if __name__ == "__main__":
    user_input = input("Enter SteamID or vanity or profile URL: ")
    result = get_user_top_games(user_input)
    print(json.dumps(result, indent=4))
