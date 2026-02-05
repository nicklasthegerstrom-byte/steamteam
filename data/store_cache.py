from src.db import get_connection, GameCache
from api.steam_store import fetch_store_metadata

__all__ = ["get_game"]

def _fetch_game_data(appid: int) -> dict | None:
    """Fetch game metadata from Steam Store API"""
    return fetch_store_metadata(appid)

def get_game(appid: int) -> dict | None:
    """
    Return cached game metadata from DB, fetch if not cached.
    Returns dict with keys: appid, name, genres, categories or None if failed.
    """
    conn = get_connection()
    game_cache = GameCache(conn)

    cached: dict | None = game_cache.get_game(appid)

    if cached:
        return cached

    # fetch if not cached
    game_data: dict | None = _fetch_game_data(appid)
    if not game_data:
        print(f"Warning: Could not fetch store metadata for appid {appid}")
        return None

    game_cache.save_game(
        appid=appid,
        name=game_data["name"],
        genres=game_data["genres"],
        categories=game_data["categories"]
    )

    return game_data
