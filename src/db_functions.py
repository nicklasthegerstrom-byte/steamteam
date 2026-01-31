import sqlite3


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
        conn.commit()
        return int(cur.lastrowid)

    except sqlite3.IntegrityError as e:
        # Triggas av UNIQUE / NOT NULL constraints
        raise ValueError("User already exists (email/username/steam_id must be unique)") from e
    
def get_user_by_username(
    conn: sqlite3.Connection,
    username: str
) -> dict | None:
    
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id, email, username, steam_id, created_at
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

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

def get_user_by_email(
    conn: sqlite3.Connection,
    email: str
) -> dict | None:
    
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id, email, username, steam_id, created_at
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

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
def insert_snapshot(snapshot: Snapshot) -> int:
    ...

def load_latest_snapshot(user_id: int) -> Snapshot | None:
    ...

def load_all_latest_snapshots() -> list[Snapshot]:
    ...


# games cache
def load_game_cache(appid: int) -> dict | None:
    ...

def save_game_cache(appid: int, name: str | None, genres: list[str], categories: list[str]) -> None:
    ...