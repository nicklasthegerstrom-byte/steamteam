import json
from pathlib import Path
from time import perf_counter


# ==========================================================
# CONFIG
# ==========================================================

from data.settings import SETTINGS
GAME_DATA_FILE = SETTINGS.example_steam_games_path
DB_PATH = SETTINGS.db_path

# ==========================================================
# APP IMPORTS
# ==========================================================

from src.utils import progress_bar
from src.db import create_tables, get_connection, GameCache

# ==========================================================
# LOAD STEAM STORE DATA
# ==========================================================

def load_store_games() -> list[dict]:
    if not GAME_DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {GAME_DATA_FILE}")

    with GAME_DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)

    return list(data.values())


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def main():
    example_games = load_store_games()
    total = len(example_games)
    print(f"Loaded: '{GAME_DATA_FILE}'")
    print(f"This script will store loaded game data to disk (sqlite3)")
    print("The data is real and fetched from the Steam Store API")
    print("Project will always attempt to get gamedata from disk before fetching")
    print(f"Storing these games might help increase performance later on")
    print(f"DB_PATH: '{DB_PATH}'")
    print(f"Number of games to store: {total}")
    
    answer = input("Continue? (y/n):").strip().lower()
    if not answer.startswith("y"):
        print("Aborting, no changes has been made")
        return
    
    start = perf_counter()
    conn = get_connection()
    create_tables(db_path=DB_PATH)  # Ensure tables exist
    game_cache = GameCache(conn)

    print(f"Adding example games to GameCache...")

    for i, g in enumerate(example_games, 1):
        game_cache.save_game(
            appid=g["appid"],
            name=g.get("name", "unknown"),
            genres=g.get("genres", []),
            categories=g.get("categories", [])
        )

        bar = progress_bar(i, total, width=20)
        elapsed = perf_counter() - start
        print(f"\r{bar} ({i}/{total}) ({elapsed:.2f}s elapsed)", end="", flush=True)

    conn.close()
    elapsed = perf_counter() - start
    print("")
    print(f"\nDone! {total} games cached in {elapsed:.2f}s")


# ==========================================================
# ENTRYPOINT
# ==========================================================

if __name__ == "__main__":
    main()
