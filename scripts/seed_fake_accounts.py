"""
Seed database with deterministic fake SteamTeam users and snapshots.
Uses real Steam Store metadata from JSON (no API calls).

This script is meant to be:
- deterministic (same output every run)
- independent of Steam Web API
- safe to run locally by all team members
"""

import json
import random
from pathlib import Path

# ==========================================================
# CONFIG
# ==========================================================

SEED = 42
NUM_USERS = 10
MIN_GAMES_PER_USER = 3
MAX_GAMES_PER_USER = 20

random.seed(SEED)

GAME_DATA_FILE = Path(__file__).parent / "example_steam_games.json"

# ==========================================================
# APP IMPORTS
# ==========================================================

from src.snapshots import create_snapshot
from src.vectors import extract_games

# DB functions
from src.db_functions import insert_user, insert_snapshot


# ==========================================================
# LOAD STEAM STORE DATA
# ==========================================================

def load_store_games() -> list[dict]:
    if not GAME_DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {GAME_DATA_FILE}")

    with GAME_DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{GAME_DATA_FILE} must contain a list of games")

    return data


# ==========================================================
# FAKE DATA GENERATORS
# ==========================================================

ADJECTIVES = [
    "cool", "sleepy", "angry", "happy", "fast",
    "epic", "calm", "smart", "slow", "crazy"
]

NOUNS = [
    "gamer", "wizard", "ninja", "knight",
    "noob", "pro", "coder"
]


def generate_fake_username(user_index: int) -> str:
    return f"fake_{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}_{user_index}"


def generate_playtime_minutes() -> int:
    # up to 10k hours
    return random.randint(0, 600_000)


def generate_playtime_2weeks() -> int:
    # sometimes zero
    return random.choice([0, random.randint(60, 10_000)])


def generate_fake_owned_games(store_games: list[dict]) -> list[dict]:
    game_count = random.randint(MIN_GAMES_PER_USER, min(MAX_GAMES_PER_USER, len(store_games)))
    chosen_games = random.sample(store_games, game_count)

    games = []
    for g in chosen_games:
        games.append({
            "appid": g["appid"],
            "name": g["name"],
            "playtime_forever": generate_playtime_minutes(),
            "playtime_2weeks": generate_playtime_2weeks(),
            "genres": g["genres"],
            "categories": g["categories"],
        })

    return games


def generate_fake_steam_profile(user_index: int, store_games: list[dict]) -> dict:
    games = generate_fake_owned_games(store_games)

    return {
        "steam_id": f"fake_{user_index}",
        "game_count": len(games),
        "games": games,
    }


# ==========================================================
# MAIN SEED FUNCTION
# ==========================================================

def seed_fake_accounts() -> None:
    store_games = load_store_games()
    print(f"Loaded {len(store_games)} Steam store games from: {GAME_DATA_FILE}")

    for i in range(1, NUM_USERS + 1):
        print("-" * 50)
        print(f"Creating fake user {i} out of {NUM_USERS}")

        # Fake SteamTeam credentials
        username = generate_fake_username(i)
        email = f"fake_user{i}@fake.com"

        print(f"username: {username}")
        print(f"email: {email}")

        # Fake Steam profile
        steam_profile = generate_fake_steam_profile(i, store_games)

        # --------------------------------------------
        # DB: create user
        # --------------------------------------------
        
        user_id = insert_user(
            email=email,
            username=username,
            steam_id=steam_profile["steam_id"]
        )

        print(f"user saved to database with user_id: {user_id}")

        # Create snapshot
        print(f"creating snapshot...")
        extracted = extract_games(steam_profile)
        snapshot = create_snapshot(user_id=user_id, extracted=extracted)
        print(snapshot)
        print("snapshot created")

        # --------------------------------------------
        # DB: save snapshot
        # --------------------------------------------
        
        snapshot_id = insert_snapshot(snapshot)
        print(f"snapshot saved to database with id: {snapshot_id}")
        
        print("account created")

    print("-" * 50)
    print("Seeding complete!")


# ==========================================================
# ENTRYPOINT
# ==========================================================

if __name__ == "__main__":
    seed_fake_accounts()
