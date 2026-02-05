import sqlite3
import json
from pathlib import Path
from datetime import datetime
from data.settings import SETTINGS
from src.snapshots import Snapshot

# Full path to sqlite3 file
DB_PATH = SETTINGS.db_path

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables_on_connection(conn: sqlite3.Connection) -> None:
    """
    Skapar tabeller på en redan öppen connection.
    Skapad för pytest med :memory: eftersom databasen lever så länge conn lever.
    """
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE NOT NULL,
            username    TEXT UNIQUE NOT NULL,
            steam_id    TEXT UNIQUE,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            created_at     TEXT NOT NULL,
            snapshot_json  TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS games_cache (
            appid           INTEGER PRIMARY KEY,
            name            TEXT,
            genres_json     TEXT,
            categories_json TEXT,
            last_updated    TEXT
        );
        """
    )
    conn.commit()


def create_tables(db_path: Path) -> None:
    """
    Skapar tabeller i en filbaserad db (normal drift).
    Öppnar conn -> skapar tabeller -> stänger conn.
    """
    conn = sqlite3.connect(db_path)
    try:
        create_tables_on_connection(conn)
    finally:
        conn.close()

#Klass där funktioner för att prata med databasen bor
class UserDB:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert_user(
        self,
        email: str,
        username: str,
        steam_id: str | None = None
    ) -> int:
        try:
            cur = self.conn.execute(
                """
                INSERT INTO users (email, username, steam_id)
                VALUES (?, ?, ?)
                """,
                (email, username, steam_id),
            )
            self.conn.commit()

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

    #Funktion för att hämta användardata med EMAIL och/eller USERNAME.
    def get_user(
        self,
        *,
        email: str | None = None,
        username: str | None = None,
        user_id: int | None = None
    ) -> dict | None:

        if email is None and username is None and user_id is None:
            raise ValueError("Provide at least email, username or user_id")

        query = """
        SELECT user_id, email, username, steam_id, created_at
        FROM users
        WHERE 1=1
        """
        params: list[object] = []

        #För att funktionen ska funka med email, ELLER usernamn, ELLER båda två!
        if email is not None:
            query += " AND email = ?"
            params.append(email)

        if username is not None:
            query += " AND username = ?"
            params.append(username)

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        cur = self.conn.execute(query, tuple(params))
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

#Klass med funktioner för snapshotfunktioner
class SnapshotDB:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert_snapshot(self, snapshot: Snapshot) -> int:
        #sparar snapshot som sträng med to dict
        snapshot_data = json.dumps(snapshot.to_dict(), ensure_ascii=False)

        cur = self.conn.execute(
            """
            INSERT INTO snapshots (user_id, created_at, snapshot_json)
            VALUES (?, ?, ?)
            """,
            (snapshot.user_id, snapshot.created_at.isoformat(), snapshot_data)
        )
        self.conn.commit()

        #returnerar ett snapshot_id (int)
        snapshot_id = int(cur.lastrowid)
        return snapshot_id

    def load_latest_snapshot(self, user_id: int) -> Snapshot | None:
        cur = self.conn.execute(
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

    def load_all_latest_snapshots(self) -> list[Snapshot]:
        cur = self.conn.execute(
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
    
class GameCache:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    #Kolla om spelet finns i databasen redan
    def get_game(self, appid: int) -> dict | None:
        cur = self.conn.execute(
            """
            SELECT appid, name, genres_json, categories_json, last_updated
            FROM games_cache
            WHERE appid = ?
            """,
            (appid,)
        )
        row = cur.fetchone()

        if row is None:
            return None

        return {
            "appid": row[0],
            "name": row[1],
            "genres": json.loads(row[2]),
            "categories": json.loads(row[3]),
            "last_updated": row[4],
        }

    #Om spelet inte fanns, spara det med denna, tillsammans med en lista med genres och categories
    def save_game(
        self,
        appid: int,
        name: str,
        genres: list[str],
        categories: list[str]
    ) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO games_cache
            (appid, name, genres_json, categories_json, last_updated)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                appid,
                name,
                json.dumps(genres, ensure_ascii=False),
                json.dumps(categories, ensure_ascii=False),
                datetime.now().isoformat()
            )
        )
        self.conn.commit()    


if __name__ == "__main__":
    create_tables(DB_PATH)
    print(f"✅ Database ready at {DB_PATH.resolve()}")
