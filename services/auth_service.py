from __future__ import annotations

from api.steam_webapi import resolve_steam_id
from src.db import get_connection, UserDB
from typing import Any
from src.db import get_connection, UserDB

# =========================
# Auth / Identity
# =========================
def login(identifier: str) -> dict | None:
    if not identifier or not identifier.strip():
        return None

    identifier = identifier.strip()

    with get_connection() as conn:
        user_db = UserDB(conn)

        # If it looks like an email
        if "@" in identifier:
            return user_db.get_user(email=identifier)

        # Otherwise treat as username
        return user_db.get_user(username=identifier)



def signup(username: str, email: str, steam_id: str) -> int:
    if not username or not email:
        raise ValueError("Username and email are required")

    steam_id = (steam_id or "").strip()

    if steam_id:
        try:
            steam_id = resolve_steam_id(steam_id)
        except Exception:
            pass

    with get_connection() as conn:
        user_db = UserDB(conn)
        return user_db.insert_user(username=username, email=email, steam_id=steam_id or None)

# =========================
# Profile updates
# =========================
def get_user_by_id(user_id: int) -> dict[str, Any]:
    with get_connection() as conn:
        user_db = UserDB(conn)
        user = user_db.get_user(user_id=user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        return user


def update_email(user_id: int, new_email: str) -> None:
    if not new_email or not new_email.strip():
        raise ValueError("Email cannot be empty")
    with get_connection() as conn:
        user_db = UserDB(conn)
        user_db.update_email(user_id, new_email.strip())


def update_username(user_id: int, new_username: str) -> None:
    if not new_username or not new_username.strip():
        raise ValueError("Username cannot be empty")
    with get_connection() as conn:
        user_db = UserDB(conn)
        user_db.update_username(user_id, new_username.strip())


def update_steam_id(user_id: int, new_steam_id: str) -> None:
    if not new_steam_id or not new_steam_id.strip():
        raise ValueError("SteamID cannot be empty")
    with get_connection() as conn:
        user_db = UserDB(conn)
        user_db.update_steam_id(user_id, new_steam_id.strip())
