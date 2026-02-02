from src.db import get_connection, UserDB, SnapshotDB
from src.matching import match_users, find_best_matches
from src.snapshots import Snapshot

def match_snapshot_to_all(target_snapshot: Snapshot, top_n: int = 5) -> list[dict]:
    """
    Match a single snapshot against all other snapshots in the DB.

    Returns a list of dicts
    """
    conn = get_connection()
    snapshot_db = SnapshotDB(conn)

    all_snapshots = snapshot_db.load_all_latest_snapshots()
    conn.close()
    
    matches = find_best_matches(
        target_snapshot=target_snapshot,
        other_snapshots=[snap for snap in all_snapshots if snap.user_id != target_snapshot.user_id],
        top_n=top_n
    )
    
    conn = get_connection()
    user_db = UserDB(conn)
    
    result = []
    
    try:
        for match in matches:
            uid, score = match
            user = user_db.get_user(user_id=uid)
            
            match_info = {
                "user_id": uid,
                "username": user.get("username", "Unknown"),
                "steam_id": user.get("steam_id", "Unknown"),
                "score": score
            }
            
            result.append(match_info)
        
    finally:
        conn.close()
    
    return result
    

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
