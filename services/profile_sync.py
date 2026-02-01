from src.db import get_connection, UserDB, SnapshotDB
from src.snapshots import create_snapshot, Snapshot
from api.steam_webapi import resolve_steam_id, fetch_owned_games
from src.vectors import extract_games
from data.store_cache import get_game

__all__ = ["sync_user_profile"]

# ------------------ Internal helpers ------------------

def enrich_games(games: list[dict], top_n: int = 5) -> list[dict]:
    """
    Sort games by playtime and enrich each with Steam Store metadata (genres, categories).
    Returns a list of enriched game dicts.
    """
    sorted_games = sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)[:top_n]
    enriched: list[dict] = []

    for g in sorted_games:
        appid: int = g["appid"]
        game_data = get_game(appid)

        if not game_data:
            # fallback if fetch failed
            enriched.append({
                "appid": appid,
                "name": "unknown",
                "playtime_forever": g.get("playtime_forever", 0),
                "playtime_2weeks": g.get("playtime_2weeks", 0),
                "genres": [],
                "categories": [],
            })
            continue

        enriched.append({
            "appid": appid,
            "name": game_data.get("name", "unknown"),
            "playtime_forever": g.get("playtime_forever", 0),
            "playtime_2weeks": g.get("playtime_2weeks", 0),
            "genres": game_data.get("genres", []),
            "categories": game_data.get("categories", []),
        })

    return enriched

# ------------------ Public function ------------------

def sync_user_profile(user_id: int, top_n: int = 5) -> Snapshot:
    """
    Full profile sync:
    1. Resolve SteamID
    2. Fetch owned games
    3. Enrich games with store metadata
    4. Create snapshot
    5. Save snapshot to DB
    6. Return snapshot
    """
    conn = get_connection()
    user_db = UserDB(conn)
    user = user_db.get_user(user_id=user_id)
    steam_id = user.get("steam_id")
    conn.close()
    
    steam_id: str = resolve_steam_id(steam_id)
    games: list[dict] = fetch_owned_games(steam_id)
    enriched_games: list[dict] = enrich_games(games, top_n)

    steam_dict: dict = {
        "steam_id": steam_id,
        "game_count": len(enriched_games),
        "games": enriched_games
    }

    extracted: dict = extract_games(steam_dict)
    snapshot: Snapshot = create_snapshot(user_id, extracted)

    conn = get_connection()
    snapshot_db = SnapshotDB(conn)
    snapshot_id: int = snapshot_db.insert_snapshot(snapshot)
    conn.close()

    print(f"user profile: {user_id} synced with snapshot_id: {snapshot_id}")
    return snapshot

# ------------------ Manual testing ------------------

if __name__ == "__main__":
    import json

    print("=== Manual test for profile_sync ===")
    steam_user_input = input("Enter SteamID / vanity / profile URL: ").strip()
    try:
        user_id_input = int(input("Enter SteamTeam user_id (int): ").strip())
    except ValueError:
        print("Invalid user_id, must be an integer")
        exit(1)

    try:
        top_n_input = int(input("Enter number of top games to fetch (int, default 5): ").strip() or 5)
    except ValueError:
        print("Invalid top_n, must be an integer")
        exit(1)

    print(f"\nSyncing profile for user_id={user_id_input}, top_n={top_n_input}...\n")
    snapshot = sync_user_profile(steam_user_input, user_id_input, top_n_input)

    print("\n=== Snapshot object ===")
    print(snapshot)

    print("\n=== Snapshot as dict ===")
    print(json.dumps(snapshot.to_dict(), indent=4, ensure_ascii=False))
