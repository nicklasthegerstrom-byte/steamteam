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
from time import perf_counter

# ==========================================================
# CONFIG
# ==========================================================

SEED = 42
NUM_USERS = 100
MIN_GAMES_PER_USER = 5
MAX_GAMES_PER_USER = 20

random.seed(SEED)

GAME_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "example_steam_games.json"

# ==========================================================
# APP IMPORTS
# ==========================================================

from src.snapshots import create_snapshot
from src.vectors import extract_games
from src.utils import progress_bar
from src.db import create_tables, get_connection, UserDB, SnapshotDB


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
# FAKE DATA GENERATORS
# ==========================================================

ADJECTIVES = [
    "cool", "sleepy", "angry", "happy", "fast", "epic", "calm", "smart", "slow", "crazy",
    "fierce", "shy", "brave", "bold", "sneaky", "witty", "lucky", "grumpy", "silly", "mighty",
    "fiery", "mysterious", "jolly", "curious", "cheerful", "dark", "bright", "gentle", "proud",
    "wild", "silent", "stormy", "frozen", "fiendish", "playful", "swift", "tiny", "huge", "ancient",
    "vicious", "honest", "lively", "calm", "savage", "sneaky", "daring", "fancy", "zany"
]

NOUNS = [
    "gamer", "wizard", "ninja", "knight", "noob", "pro", "coder", "hunter", "warrior", "mage",
    "archer", "rogue", "assassin", "paladin", "sorcerer", "ranger", "thief", "champion", "samurai", "gladiator",
    "knightmare", "warlock", "guardian", "sentinel", "dragon", "beast", "hero", "villain", "phantom", "cyborg",
    "robot", "pirate", "monk", "jester", "viking", "samurai", "druid", "bard", "swordsman", "goblin",
    "troll", "giant", "elf", "orc", "sprite", "witch", "vampire", "zombie", "shadow", "noble", "hacker"
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
        "steam_id": f"{''.join(str(random.randint(1, 9)) for _ in range(17))}",
        "game_count": len(games),
        "games": games,
    }


# ==========================================================
# MAIN SEED FUNCTION
# ==========================================================

def seed_fake_accounts(num_users: int = NUM_USERS) -> None:
    print("Starting seed script...")
    start = perf_counter()

    print("Setting up database\nCreating tables if not existing...")
    create_tables()
    conn = get_connection()
    user_db = UserDB(conn)
    snapshot_db = SnapshotDB(conn)

    print("Loading Steam example games from json...")
    store_games = load_store_games()
    print(f"Loaded {len(store_games)} Steam store games from: {GAME_DATA_FILE}")


    # Counters
    users_created = 0
    snapshots_created = 0
    failed_users = 0
    print("Seeding fake users now...")
    for i in range(1, num_users + 1):
        bar = progress_bar(i, num_users, 20)
        elapsed = perf_counter() - start
        print(f"\r{bar} ({i}/{num_users}) ({elapsed:.2f}s elapsed)", end="", flush=True)

        username = generate_fake_username(i)
        email = f"{username}@fake.com"
        steam_profile = generate_fake_steam_profile(i, store_games)

        try:
            user_id = user_db.insert_user(
                email=email,
                username=username,
                steam_id=steam_profile["steam_id"]
            )
            users_created += 1

        except ValueError:
            failed_users += 1
            continue

        extracted = extract_games(steam_profile)
        snapshot = create_snapshot(user_id=user_id, games=extracted)
        snapshot_db.insert_snapshot(snapshot)
        snapshots_created += 1

    conn.close()

    elapsed = perf_counter() - start

    # Final summary
    print("")
    print(f"Users created     : {users_created}")
    print(f"Snapshots created : {snapshots_created}")
    print(f"Failed users      : {failed_users}")
    print("\nSeeding completed!")


# ==========================================================
# ENTRYPOINT
# ==========================================================

if __name__ == "__main__":
    raw = input(f"Number of fake users to seed (default {NUM_USERS}) [int]: ").strip()
    try:
        num = NUM_USERS if not raw else int(raw)
        
    except ValueError:
        raise ValueError("Number of users must be an integer")

    seed_fake_accounts(num_users=num)

