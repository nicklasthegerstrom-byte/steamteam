# users
def insert_user(email: str, username: str, steam_id: str | None = None) -> int:
    ...

def get_user_by_username(username: str) -> dict | None:
    ...

def get_user_by_email(email: str) -> dict | None:
    ...


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