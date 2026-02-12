from src.db import get_connection, UserDB, SnapshotDB
from src.matching import match_users, find_best_matches
from src.snapshots import Snapshot
from dataclasses import dataclass
from typing import List, Tuple
from src.vectors import summarize_playstyle
from services.logger import get_logger

log = get_logger(__name__)


#Matchcard för trevlig presentation av matchningarna

@dataclass(slots=True)
class MatchCard:
    username: str
    steam_id: str | None
    score: float

    # Presentation-data
    playstyles: dict[str, float]              # coop / social / pvp / solo
    top_genres: List[Tuple[str, float]]       # ("Action", 0.48)
    top_games: List[Tuple[str, int]]           # ("CS2", 1200 timmar)


def build_match_card(
    snapshot: Snapshot,
    *,
    username: str,
    steam_id: str | None,
    score: float,
) -> MatchCard:
    """
    Bygger ett MatchCard från en snapshot + redan uträknad match score.
    """

    # 1. Spelstil (grupperad via categories)
    playstyles = summarize_playstyle(snapshot.category_vector)

    # 2. Top 3 genres
    top_genres = sorted(
        snapshot.genre_vector.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    # 3. Top 3 spel (från snapshot, minuter -> timmar)
    top_games = [
        (g["name"], round(g["playtime"] / 60))
        for g in snapshot.top_games[:3]
    ]

    return MatchCard(
        username=username,
        steam_id=steam_id,
        score=score,
        playstyles=playstyles,
        top_genres=top_genres,
        top_games=top_games,
    )


def match_snapshot_to_all(target_snapshot: Snapshot, top_n: int = 5) -> list[MatchCard]:
    """
    Match a single snapshot against all other snapshots in the DB.
    Returns a list of MatchCard objects.
    """
    log.info("Matching started target_user_id=%s top_n=%s", target_snapshot.user_id, top_n)

    try:
        conn = get_connection()
        snapshot_db = SnapshotDB(conn)
        all_snapshots = snapshot_db.load_all_latest_snapshots()
        log.debug("Matching pool size=%d", len(all_snapshots))
        conn.close()

        # Adapter: Snapshot -> vectors (INGET räknas om)
        other_users_snapshots = {
            s.user_id: s
            for s in all_snapshots
            if s.user_id != target_snapshot.user_id
        }

        matches = find_best_matches(
            target_user_id=target_snapshot.user_id,
            target_snapshot=target_snapshot,
            other_users=other_users_snapshots,
            top_n=top_n,
        )

    except Exception:
        log.exception("Matching failed target_user_id=%s", target_snapshot.user_id)
        raise

    conn = get_connection()
    user_db = UserDB(conn)
    snapshot_db = SnapshotDB(conn)

    match_cards: list[MatchCard] = []

    try:
        for uid, score in matches:
            user = user_db.get_user(user_id=uid)
            snapshot = snapshot_db.load_latest_snapshot(uid)

            if not user or not snapshot:
                continue

            card = build_match_card(
                snapshot=snapshot,
                username=user["username"],
                steam_id=user.get("steam_id"),
                score=score,
            )
            match_cards.append(card)

    finally:
        conn.close()

    log.info("Matching complete target_user_id=%s results=%d", target_snapshot.user_id, len(match_cards))
    return match_cards


def match_user_id(user_id: int, top_n: int = 5) -> list[MatchCard]:
    """
    Fetch a snapshot by user_id and match it against all other users.
    """
    conn = get_connection()
    snapshot_db = SnapshotDB(conn)
    target_snapshot = snapshot_db.load_latest_snapshot(user_id)
    conn.close()

    if not target_snapshot:
        raise ValueError(f"No snapshot found for user_id={user_id}")

    return match_snapshot_to_all(target_snapshot, top_n=top_n)
