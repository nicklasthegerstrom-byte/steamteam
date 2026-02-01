from src.db import get_connection, SnapshotDB
from src.matching import match_users, find_best_matches
from src.snapshots import Snapshot

def match_snapshot_to_all(target_snapshot: Snapshot, top_n: int = 5) -> list:
    """
    Match a single snapshot against all other snapshots in the DB.

    Returns a list of tuples: (user_id, score)
    """
    conn = get_connection()
    snapshot_db = SnapshotDB(conn)

    all_snapshots = snapshot_db.load_all_latest_snapshots()
    conn.close()

    # Convert to dict {user_id: {"genre_vector":..., "game_vector":...}}
    other_users = {
        s.user_id: {
            "genre_vector": s.genre_vector,
            "game_vector": s.game_vector
        }
        for s in all_snapshots
        if s.user_id != target_snapshot.user_id
    }

    return find_best_matches(
        target_user_id=target_snapshot.user_id,
        target_genre_vector=target_snapshot.genre_vector,
        target_game_vector=target_snapshot.game_vector,
        other_users=other_users,
        top_n=top_n
    )


def match_user_id(user_id: int, top_n: int = 5) -> list:
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
