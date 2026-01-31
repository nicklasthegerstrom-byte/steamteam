import sqlite3
import json
from src.snapshots import Snapshot

# users
def insert_user(
    conn: sqlite3.Connection,
    email: str,
    username: str,
    steam_id: str | None = None
) -> int:
    try:
        cur = conn.execute(
            """
            INSERT INTO users (email, username, steam_id)
            VALUES (?, ?, ?)
            """,
            (email, username, steam_id),
        )
        
        user_id = int(cur.lastrowid)
        #returnerar ett user_id (int)
        return user_id

    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if "users.email" in msg:
            raise ValueError("Email already exists") from e
        if "users.username" in msg:
            raise ValueError("Username already exists") from e
        if "users.steam_id" in msg:
            raise ValueError("Steam ID already exists") from e
        raise ValueError("User violates database constraints") from e
    
    #Funktion för att hämta användardata antingen med EMAIL eller USERNAME, inte båda samtidigt.
def get_user(
    conn: sqlite3.Connection,
    *,
    email: str | None = None,
    username: str | None = None,
) -> dict | None:

    if email is None and username is None:
        raise ValueError("Provide at least email or username")

    query = """
    SELECT user_id, email, username, steam_id, created_at
    FROM users
    WHERE 1=1
    """
    params = []

    #För att funktionen ska funka med email, ELLER usernamn, ELLER båda två!
    if email is not None:
        query += " AND email = ?"
        params.append(email)

    if username is not None:
        query += " AND username = ?"
        params.append(username)

    cur = conn.execute(query, tuple(params))
    row = cur.fetchone()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "email": row[1],
        "username": row[2],
        "steam_id": row[3],
        "created_at": row[4],
    }
#Förslag? update_user_steam_id(user_id: int)


# snapshots


def insert_snapshot(conn: sqlite3.Connection, snapshot: Snapshot) -> int:

    #sparar snapshot som sträng med to dict
    snapshot_data = json.dumps(snapshot.to_dict(), ensure_ascii=False)

    cur = conn.execute(
        """
        INSERT INTO snapshots (user_id, created_at, snapshot_json)
        VALUES (?, ?, ?)
        """,
        (snapshot.user_id, snapshot.created_at.isoformat(), snapshot_data)
    )
    #returnerar ett snapshot_id (int)
    snapshot_id = int(cur.lastrowid)
    return snapshot_id

def load_latest_snapshot(conn: sqlite3.Connection, user_id: int) -> Snapshot | None:
    cur = conn.execute(
        """
        SELECT snapshot_json
        FROM snapshots
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id,)
    )
    row = cur.fetchone()

    if row is None:
        return None

    data = json.loads(row[0])          # text -> dict (keys är strings här)

    return Snapshot.from_dict(data)     # dict -> Snapshot (appid-keys tillbaka till int)

def load_all_latest_snapshots(conn: sqlite3.Connection) -> list[Snapshot]:
    cur = conn.execute(
        """
        SELECT s.snapshot_json
        FROM snapshots s
        JOIN (
            SELECT user_id, MAX(created_at) AS max_created
            FROM snapshots
            GROUP BY user_id
        ) latest
        ON latest.user_id = s.user_id AND latest.max_created = s.created_at
        """
    )

    snaps: list[Snapshot] = []
    for (snapshot_json,) in cur.fetchall():
        data = json.loads(snapshot_json)
        snaps.append(Snapshot.from_dict(data))
        #returnerar en lista med alla användars snapshots i rätt format (keys som int)
    return snaps


# games cache
def load_game_cache(appid: int) -> dict | None:
    ...

def save_game_cache(appid: int, name: str | None, genres: list[str], categories: list[str]) -> None:
    ...