# tests/test_db.py
import sqlite3
from datetime import datetime

import pytest

from src.db import (
    UserDB,
    SnapshotDB,
    GameCache,
    create_tables_on_connection, 
)
from src.snapshots import Snapshot


# ==========================================================
# Fixture: isolerad in-memory DB per test
# ==========================================================

@pytest.fixture
def conn() -> sqlite3.Connection:
    """Skapa en isolerad test-databas i minnet (per test)."""
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON;")
    create_tables_on_connection(c)
    try:
        yield c
    finally:
        c.close()


#Testa användare

def test_insert_and_get_user_by_username(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)

    user_id = users.insert_user(
        email="test@example.com",
        username="nicklas",
        steam_id="steam_123",
    )

    user = users.get_user(username="nicklas")
    assert user is not None
    assert user["user_id"] == user_id
    assert user["email"] == "test@example.com"
    assert user["username"] == "nicklas"
    assert user["steam_id"] == "steam_123"
    assert user["created_at"]  # DEFAULT datetime('now') ska finnas


def test_get_user_by_email_and_username_together_must_match_same_row(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)

    users.insert_user(email="a@a.com", username="userA", steam_id="sA")
    users.insert_user(email="b@b.com", username="userB", steam_id="sB")

    # rätt kombination
    ok = users.get_user(email="a@a.com", username="userA")
    assert ok is not None
    assert ok["username"] == "userA"

    # fel kombination ska ge None (AND-logik)
    nope = users.get_user(email="a@a.com", username="userB")
    assert nope is None


def test_insert_user_unique_constraints_email(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)

    users.insert_user(email="dup@example.com", username="u1", steam_id="s1")

    with pytest.raises(ValueError):
        users.insert_user(email="dup@example.com", username="u2", steam_id="s2")


def test_insert_user_unique_constraints_username(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)

    users.insert_user(email="a@x.com", username="same", steam_id="s1")

    with pytest.raises(ValueError):
        users.insert_user(email="b@x.com", username="same", steam_id="s2")


def test_insert_user_unique_constraints_steam_id(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)

    users.insert_user(email="a@x.com", username="u1", steam_id="steam_same")

    with pytest.raises(ValueError):
        users.insert_user(email="b@x.com", username="u2", steam_id="steam_same")


#Testa snapshots

def test_insert_and_load_latest_snapshot(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)
    snaps = SnapshotDB(conn)

    user_id = users.insert_user(
        email="snap@example.com",
        username="snapuser",
        steam_id="s99",
    )

    snapshot = Snapshot(
        user_id=user_id,
        created_at=datetime.now(),
        game_vector={570: 0.6, 730: 0.4},
        genre_vector={"Action": 1.0},
        category_vector={"Co-op": 0.5, "PvP": 0.5},
        top_games=[],
    )

    snap_id = snaps.insert_snapshot(snapshot)
    assert isinstance(snap_id, int)

    loaded = snaps.load_latest_snapshot(user_id=user_id)
    assert loaded is not None
    assert loaded.user_id == user_id
    assert loaded.game_vector == snapshot.game_vector
    assert loaded.genre_vector == snapshot.genre_vector
    assert loaded.category_vector == snapshot.category_vector
    assert loaded.top_games == snapshot.top_games


def test_load_latest_snapshot_returns_none_if_missing(conn: sqlite3.Connection) -> None:
    snaps = SnapshotDB(conn)
    loaded = snaps.load_latest_snapshot(user_id=999)
    assert loaded is None


def test_load_all_latest_snapshots_returns_one_per_user(conn: sqlite3.Connection) -> None:
    users = UserDB(conn)
    snaps = SnapshotDB(conn)

    u1 = users.insert_user(email="u1@x.com", username="u1", steam_id="s1")
    u2 = users.insert_user(email="u2@x.com", username="u2", steam_id="s2")

    # två snapshots för user1 (senaste ska väljas)
    s1_old = Snapshot(
        user_id=u1,
        created_at=datetime.fromisoformat("2026-01-01T10:00:00"),
        game_vector={1: 1.0},
        genre_vector={"Action": 1.0},
        category_vector={"Co-op": 1.0},
        top_games=[],
    )
    s1_new = Snapshot(
        user_id=u1,
        created_at=datetime.fromisoformat("2026-01-02T10:00:00"),
        game_vector={2: 1.0},
        genre_vector={"RPG": 1.0},
        category_vector={"PvP": 1.0},
        top_games=[],
    )

    s2 = Snapshot(
        user_id=u2,
        created_at=datetime.fromisoformat("2026-01-03T10:00:00"),
        game_vector={3: 1.0},
        genre_vector={"Indie": 1.0},
        category_vector={"Solo": 1.0},
        top_games=[],
    )

    snaps.insert_snapshot(s1_old)
    snaps.insert_snapshot(s1_new)
    snaps.insert_snapshot(s2)

    latest = snaps.load_all_latest_snapshots()
    assert len(latest) == 2

    # hitta user1 i listan och se att den är "new"
    latest_u1 = next(s for s in latest if s.user_id == u1)
    assert latest_u1.game_vector == {2: 1.0}


#Testa Game cache

def test_game_cache_save_and_get(conn: sqlite3.Connection) -> None:
    cache = GameCache(conn)

    appid = 570
    cache.save_game(
        appid=appid,
        name="Dota 2",
        genres=["Action", "Strategy"],
        categories=["Multi-player", "Online PvP"],
    )

    game = cache.get_game(appid)
    assert game is not None
    assert game["appid"] == appid
    assert game["name"] == "Dota 2"
    assert game["genres"] == ["Action", "Strategy"]
    assert game["categories"] == ["Multi-player", "Online PvP"]
    assert game["last_updated"]