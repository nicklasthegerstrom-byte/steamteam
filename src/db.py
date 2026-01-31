import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # repo root
DB_PATH = BASE_DIR / "data" / "db" / "steamteam.sqlite3"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.executescript(
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
    conn.close()


if __name__ == "__main__":
    create_tables()
    print(f"✅ Database ready at {DB_PATH.resolve()}")