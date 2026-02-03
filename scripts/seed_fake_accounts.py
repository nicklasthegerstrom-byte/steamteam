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
PT_LOW = 0
PT_HIGH = 600_000
PT2_LOW = 60
PT2_HIGH = 10_000

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
    "vicious", "honest", "lively", "savage", "daring", "fancy", "zany"
]

NOUNS = [
    "gamer", "wizard", "ninja", "knight", "noob", "pro", "coder", "hunter", "warrior", "mage",
    "archer", "rogue", "assassin", "paladin", "sorcerer", "ranger", "thief", "champion", "samurai", "gladiator",
    "knightmare", "warlock", "guardian", "sentinel", "dragon", "beast", "hero", "villain", "phantom", "cyborg",
    "robot", "pirate", "monk", "jester", "viking", "druid", "bard", "swordsman", "goblin",
    "troll", "giant", "elf", "orc", "sprite", "witch", "vampire", "zombie", "shadow", "noble", "hacker"
]

def generate_fake_username(user_index: int) -> str:
    return f"fake_{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}_{user_index}"

def generate_fake_steam_profile(user_index: int, store_games: list[dict],
                                min_games: int, max_games: int,
                                pt_low: int, pt_high: int, pt2_low: int, pt2_high: int) -> dict:
                                    
    game_count = random.randint(min_games, min(max_games, len(store_games)))
    chosen_games = random.sample(store_games, game_count)
    
    games = [
        {
            "appid": g["appid"],
            "name": g["name"],
            "playtime_forever": random.randint(pt_low, pt_high),
            "playtime_2weeks": random.choice([0, random.randint(pt2_low, pt2_high)]),
            "genres": g["genres"],
            "categories": g["categories"],
        }
        for g in chosen_games
    ]
    
    return {
        "steam_id": f"{''.join(str(random.randint(1, 9)) for _ in range(17))}",
        "game_count": len(games),
        "games": games,
    }

# ==========================================================
# MAIN SEED FUNCTION
# ==========================================================

def seed_fake_accounts(
        num_users: int = NUM_USERS,
        min_games_per_user: int = MIN_GAMES_PER_USER,
        max_games_per_user: int = MAX_GAMES_PER_USER,
        seed: int = SEED,
        pt_low: int = PT_LOW,
        pt_high: int = PT_HIGH,
        pt2_low: int = PT2_LOW,
        pt2_high: int = PT2_HIGH
    ) -> None:
    
    random.seed(seed)
    start = perf_counter()
    print("Starting seed script...")

    print("Setting up database\nCreating tables if not existing...")
    create_tables()
    conn = get_connection()
    user_db = UserDB(conn)
    snapshot_db = SnapshotDB(conn)

    print("Loading Steam example games from json (RAM)...")
    store_games = load_store_games()
    print(f"Loaded {len(store_games)} Steam store games from: {GAME_DATA_FILE}")

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
        steam_profile = generate_fake_steam_profile(
            i, store_games, min_games_per_user, max_games_per_user,
            pt_low, pt_high, pt2_low, pt2_high
        )

        try:
            user_id = user_db.insert_user(email=email, username=username, steam_id=steam_profile["steam_id"])
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

    print("")
    print(f"Users created     : {users_created}")
    print(f"Snapshots created : {snapshots_created}")
    print(f"Failed users      : {failed_users}")
    print(f"Time elapsed      : {elapsed:.2f}s")
    print("\nSeeding completed!")

# ==========================================================
# ENTRYPOINT
# ==========================================================

if __name__ == "__main__":
    print("You can press ENTER to select default values")
    raw_users = input(f"Number of fake users to seed (default {NUM_USERS}) [int]: ").strip()
    raw_min = input(f"Minimum games per user (default {MIN_GAMES_PER_USER}) [int]: ").strip()
    raw_max = input(f"Maximum games per user (default {MAX_GAMES_PER_USER}) [int]: ").strip()
    raw_seed = input(f"Random seed (default {SEED}) [int]: ").strip()
    raw_pt_low = input(f"Playtime total low (default {PT_LOW}) [int]: ").strip()
    raw_pt_high = input(f"Playtime total high (default {PT_HIGH}) [int]: ").strip()
    raw_pt2_low = input(f"Playtime last 2 weeks low (default {PT2_LOW}) [int]: ").strip()
    raw_pt2_high = input(f"Playtime last 2 weeks high (default {PT2_HIGH}) [int]: ").strip()

    try:
        num = NUM_USERS if not raw_users else int(raw_users)
        min_games = MIN_GAMES_PER_USER if not raw_min else int(raw_min)
        max_games = MAX_GAMES_PER_USER if not raw_max else int(raw_max)
        seed = SEED if not raw_seed else int(raw_seed)
        pt_low = PT_LOW if not raw_pt_low else int(raw_pt_low)
        pt_high = PT_HIGH if not raw_pt_high else int(raw_pt_high)
        pt2_low = PT2_LOW if not raw_pt2_low else int(raw_pt2_low)
        pt2_high = PT2_HIGH if not raw_pt2_high else int(raw_pt2_high)

    except ValueError:
        raise ValueError("All inputs must be integers")

    seed_fake_accounts(
        num_users=num,
        min_games_per_user=min_games,
        max_games_per_user=max_games,
        seed=seed,
        pt_low=pt_low,
        pt_high=pt_high,
        pt2_low=pt2_low,
        pt2_high=pt2_high
    )
