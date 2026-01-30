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
            "playtime_2weeks": g.get("playtime_2weeks", 0),
            "genres": genres,
            "categories": categories,
        })
    return enriched

# ------------------ Public function ------------------

def sync_user_profile(user_string: str, top_n: int = 5, user_id: int = None) -> Snapshot:
    """
    Full profile sync:
    1. Resolve SteamID
    2. Fetch owned games
    3. Enrich games with store metadata
    4. Create snapshot
    5. Return snapshot

    Parameters:
        user_string (str): SteamID64 / vanity / profile URL
        top_n (int): number of top games to include
        user_id (int): internal ID for Snapshot creation
        
    Returns:
        Snapshot:
            A Snapshot object containing:
                - user_id       -> Linked to SteamTeam account
                - created_at    -> timestamp of when the snapshot was created
                - game_vector   -> weighted representation of games
                - genre_vector  -> weighted representation of genres
    """

    # resolve SteamID
    steam_id = resolve_steam_id(user_string)

    # fetch owned games
    games = fetch_owned_games(steam_id)

    # enrich with store metadata
    enriched_games = enrich_games(games, top_n)
    
    # create steam user dict
    steam_dict = {
        "steam_id": steam_id,
        "game_count": len(enriched_games),
        "games": enriched_games
    }

    # create snapshot with vectors
    extracted = extract_games(steam_dict)
    snapshot_user_id = user_id
    if not snapshot_user_id:
        raise ValueError("user_id must be provided to create a snapshot")

    snapshot: Snapshot = create_snapshot(snapshot_user_id, extracted)

    # return snapshot
    return snapshot

