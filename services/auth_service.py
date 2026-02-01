from src.db import get_connection, UserDB


# =========================
# Auth / Identity
# =========================
def login(username: str, email: str) -> dict | None:
    if not username or not email:
        return None

    conn = get_connection()
    try:
        user_db = UserDB(conn)
        return user_db.get_user(username=username, email=email)
        
    finally:
        conn.close()


def signup(username: str, email: str, steam_id: str) -> int:
    if not username or not email:
        raise ValueError("Username and email are required")

    conn = get_connection()
    try:
        user_db = UserDB(conn)
        return user_db.insert_user(username=username, email=email, steam_id=steam_id)
    finally:
        conn.close()


# =========================
# Profile updates
# =========================
def update_email(user_id: int, new_email: str) -> None:
    if not new_email or not new_email.strip():
        raise ValueError("Email cannot be empty")

    conn = get_connection()
    try:
        user_db = UserDB(conn)
        user_db.update_email(user_id, new_email.strip())
        
    finally:
        conn.close()


def update_username(user_id: int, new_username: str) -> None:
    if not new_username or not new_username.strip():
        raise ValueError("Username cannot be empty")

    conn = get_connection()
    try:
        user_db = UserDB(conn)
        user_db.update_username(user_id, new_username.strip())
        
    finally:
        conn.close()


def update_steam_id(user_id: int, new_steam_id: str) -> None:
    if not new_steam_id or not new_steam_id.strip():
        raise ValueError("SteamID cannot be empty")

    conn = get_connection()
    try:
        user_db = UserDB(conn)
        user_db.update_steam_id(user_id, new_steam_id.strip())
        
    finally:
        conn.close()
