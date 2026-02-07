from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from src.db import get_connection, UserDB, SnapshotDB
from src.snapshots import create_snapshot, Snapshot
from api.steam_webapi import resolve_steam_id, fetch_owned_games
from src.vectors import extract_games, summarize_playstyle
from data.store_cache import get_game
from services.logger import get_logger

__all__ = ["sync_user_profile", "SelfCard", "build_self_card"]

log = get_logger(__name__)


# ------------------ View profile info ------------------

@dataclass(slots=True)
class SelfCard:
    username: str
    steam_id: str | None
    playstyles: dict[str, float]
    top_genres: List[Tuple[str, float]]
    top_games: List[Tuple[str, int]] 


def build_self_card(snapshot: Snapshot, username: str, steam_id: str | None) -> SelfCard:
    playstyles = summarize_playstyle(snapshot.category_vector)

    top_genres = sorted(
        snapshot.genre_vector.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    top_games = [
        (g["name"], round(g["playtime"] / 60))
        for g in (snapshot.top_games or [])[:3]
    ]

    return SelfCard(
        username=username,
        steam_id=steam_id,
        playstyles=playstyles,
        top_genres=top_genres,
        top_games=top_games,
    )


# ------------------ Internal helpers ------------------

def enrich_games(games: list[dict], top_n: int = 5) -> list[dict]:
    """
    Sort games by playtime and enrich each with Steam Store metadata (genres, categories).
    Returns a list of enriched game dicts.
    """
    sorted_games = sorted(
        games,
        key=lambda g: g.get("playtime_forever", 0),
        reverse=True
    )[:top_n]

    enriched: list[dict] = []

    for g in sorted_games:
        appid: int = g["appid"]
        game_data = get_game(appid)

        if not game_data:
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

def sync_user_profile(user_id: int, top_n: int = 5) -> tuple[Snapshot, SelfCard]:
    """
    Full profile sync:
    1. Fetch user from DB
    2. Resolve SteamID
    3. Fetch owned games
    4. Enrich games with store metadata
    5. Create snapshot
    6. Save snapshot to DB
    7. Build selfcard
    8. Return snapshot + selfcard
    """
    log.info("Profile sync started user_id=%s top_n=%s", user_id, top_n)

    try:
        # Fetch user + steam_id from DB
        with get_connection() as conn:
            user_db = UserDB(conn)
            user = user_db.get_user(user_id=user_id)

        if not user:
            log.error("User not found user_id=%s", user_id)
            raise ValueError(f"User {user_id} not found")
    
        steam_id_raw = user.get("steam_id")
        if not isinstance(steam_id_raw, str) or not steam_id_raw.strip():
            log.error("User missing steam_id user_id=%s", user_id)
            raise ValueError(f"User {user_id} has no steam_id")
        steam_id: str = steam_id_raw
        steam_id = resolve_steam_id(steam_id)
    
        if not steam_id:
            log.error("User missing steam_id user_id=%s", user_id)
            raise ValueError(f"User {user_id} has no steam_id")

        # Resolve + fetch games
        steam_id_resolved = resolve_steam_id(steam_id_from_db)
        games = fetch_owned_games(steam_id_resolved)

        log.info(
            "Owned games fetched user_id=%s steam_id=%s count=%d",
            user_id,
            steam_id_resolved,
            len(games),
        )

        enriched_games = enrich_games(games, top_n)

        steam_dict = {
            "steam_id": steam_id_resolved,
            "game_count": len(enriched_games),
            "games": enriched_games,
        }

        extracted: list[dict] = extract_games(steam_dict)
        snapshot: Snapshot = create_snapshot(user_id, extracted)

        log.info("Profile sync complete user_id=%s snapshot_id=%s", user_id, snapshot_id)

        # Build selfcard (username + steam_id from DB)
        selfcard = build_self_card(
            snapshot,
            username=username,
            steam_id=steam_id_from_db,
        )

        return snapshot, selfcard

    except ValueError:
        log.warning("Profile sync validation issue user_id=%s", user_id)
        raise

    except Exception:
        log.exception("Profile sync failed user_id=%s", user_id)
        raise

# ------------------ Manual testing ------------------

if __name__ == "__main__":
    import json

    print("=== Manual test for profile_sync ===")
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
    snapshot = sync_user_profile(user_id_input, top_n_input)

    print("\n=== Snapshot object ===")
    print(snapshot)

    print("\n=== Snapshot as dict ===")
    print(json.dumps(snapshot.to_dict(), indent=4, ensure_ascii=False))
