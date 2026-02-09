from __future__ import annotations

import sqlite3
from pathlib import Path

from data.settings import SETTINGS
from services.logger import setup_logging, get_logger
from src.db import create_tables
from scripts.seed_fake_accounts import seed_fake_accounts


def _needs_seed(db_path: Path) -> bool:
    """
    True if DB should be seeded:
    - file missing
    - users table missing
    - users table exists but empty
    - db unreadable/corrupt
    """
    if not db_path.exists():
        return True

    try:
        conn = sqlite3.connect(db_path)
        try:
            # table exists?
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
            ).fetchone()
            if row is None:
                return True

            # has any users?
            count = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
            return int(count) == 0
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        # corrupt/unreadable
        return True


def bootstrap() -> None:
    setup_logging(SETTINGS.log_dir)
    log = get_logger(__name__)

    db_path = SETTINGS.db_path

    try:
        # Always ensure schema exists (safe no-op if already there)
        create_tables(db_path)
    except Exception:
        log.exception("Database table initialization failed.")
        raise

    if _needs_seed(db_path):
        log.info("Database missing/empty/invalid at %s. Seeding fake accounts...", db_path)

        # If file is corrupt, remove it first so seeding can recreate clean DB
        if db_path.exists():
            try:
                # quick corruption probe
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA quick_check;").fetchone()
                conn.close()
            except sqlite3.DatabaseError:
                log.warning("Database appears corrupt. Recreating: %s", db_path)
                db_path.unlink(missing_ok=True)

        try:
            seed_fake_accounts()
            log.info("Fake account seeding completed.")
        except Exception:
            log.exception("Failed to seed fake accounts.")
            raise
    else:
        log.info("Database exists and has data. Skipping seed.")

    if not SETTINGS.steam_api_key:
        log.warning("STEAM_API_KEY is not set. Live Steam sync will be unavailable.")

    log.info("Bootstrap complete")
