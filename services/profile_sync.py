# services/profile_sync.py

from datetime import datetime
from api.steam_webapi import resolve_steam_id, fetch_owned_games
from api.steam_store import fetch_store_metadata
from src.snapshots import create_snapshot, Snapshot
from src.vectors import extract_games

__all__ = ["sync_user_profile"]

# ------------------ Internal helpers ------------------

def enrich_games(games: list[dict], top_n: int = 5) -> list[dict]:
    """
    Sort games by playtime and enrich each with Steam Store metadata (genres, categories).
    """
    # Sort by playtime
    sorted_games = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)[:top_n]

    enriched = []
    for g in sorted_games:
        genres, categories = fetch_store_metadata(g["appid"])
        enriched.append({
            "appid": g["appid"],
            "name": g.get("name"),
            "playtime_forever": g.get("playtime_forever", 0),
            "playtime_2weeks": g.get("playtime_2weeks"),
            "genres": genres,
            "categories": categories,
        })
    return enriched

# ------------------ Public function ------------------

def sync_user_profile(user_string: str, top_n: int = 5, user_id: int = None) -> dict:
    """
    Full profile sync:
    1. Resolve SteamID
    2. Fetch owned games
    3. Enrich games with store metadata
    4. Build snapshot (vector) via Nicklas logic
    5. Return both raw_profile and vector snapshot

    Parameters:
        user_string (str): SteamID64 / vanity / profile URL
        top_n (int): number of top games to include
        user_id (int, optional): internal ID for Snapshot creation

    Returns:
        dict: {
            "steam_id": str,
            "raw_profile": { "games": [...], "game_count": int },
            "vector": Snapshot object
        }
    """
    # resolve SteamID
    steam_id = resolve_steam_id(user_string)

    # fetch owned games
    games = fetch_owned_games(steam_id)

    # enrich med store metadata
    enriched_games = enrich_games(games, top_n)

    # create snapshot with vectors
    extracted = extract_games({"games": enriched_games})
    snapshot_user_id = user_id if user_id is not None else int(steam_id[-6:])  # fallback
    snapshot: Snapshot = create_snapshot(snapshot_user_id, extracted)

    # return profile dict
    return {
        "steam_id": steam_id,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_profile": {
            "games": enriched_games,
            "game_count": len(enriched_games)
        },
        "vector": snapshot
    }

# ------------------ Example CLI ------------------

if __name__ == "__main__":
    user_input = input("Enter SteamID, vanity, or profile URL: ")
    result = sync_user_profile(user_input, top_n=5)
    print("Steam ID:", result["steam_id"])
    print("Raw games:", result["raw_profile"])
    print("Vector snapshot:\n", result["vector"])
