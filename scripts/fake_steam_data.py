import random

# ------------------ Static reference data ------------------

# Real popular Steam games (subset, easy to expand)
STEAM_GAMES = [
    (570, "Dota 2"),
    (730, "Counter-Strike 2"),
    (440, "Team Fortress 2"),
    (945360, "Among Us"),
    (1091500, "Cyberpunk 2077"),
    (620, "Portal 2"),
    (271590, "Grand Theft Auto V"),
    (1085660, "Destiny 2"),
    (381210, "Dead by Daylight"),
    (892970, "Valheim"),
    (578080, "PUBG: Battlegrounds"),
    (1172470, "Apex Legends"),
    (413150, "Stardew Valley"),
    (252490, "Rust"),
    (1245620, "Elden Ring"),
]


GENRES = [
    "Action",
    "Adventure",
    "RPG",
    "Shooter",
    "Strategy",
    "Simulation",
    "Indie",
    "Racing",
    "Sports",
    "Casual",
    "Massively Multiplayer",
    "Puzzle",
    "Horror",
    "Survival",
    "Open World",
]

CATEGORIES = [
    "Single-player",
    "Multi-player",
    "Online PvP",
    "Online Co-op",
    "Local Co-op",
    "Shared/Split Screen",
    "Steam Achievements",
    "Steam Cloud",
    "Full Controller Support",
    "Controller",
    "Steam Trading Cards",
    "Workshop",
    "VR Supported",
    "Family Sharing",
    "In-App Purchases",
]

# ------------------ Public API ------------------

def generate_fake_steam_data(min_games: int = 5, max_games: int = 30) -> dict:
    """
    Generate realistic fake Steam profile data.

    Returns:
        dict:
            {
                "steam_id": <SteamID64>,
                "game_count": <number of games returned>,
                "games": [
                    {
                        "appid": int,
                        "name": str,
                        "playtime_forever": int,
                        "playtime_2weeks": int,
                        "genres": list[str],
                        "categories": list[str],
                    }
                ]
            }
    """
    
    steam_id = ''.join(str(random.randint(0, 9)) for _ in range(17))
    game_count = random.randint(min_games, max_games)
    games = []

    for _ in range(game_count):
        appid, name = random.choice(STEAM_GAMES)

        playtime_forever = random.randint(60, 300_000)

        # playtime_2weeks is often 0 in real data
        playtime_2weeks = (
            random.randint(30, 6_000)
            if random.random() < 0.35
            else 0
        )

        games.append({
            "appid": appid,
            "name": name,
            "playtime_forever": playtime_forever,
            "playtime_2weeks": playtime_2weeks,
            "genres": random.sample(GENRES, k=random.randint(1, 10)),
            "categories": random.sample(CATEGORIES, k=random.randint(2, 10)),
        })
        
    user = {
        "steam_id": steam_id,
        "game_count": game_count,
        "games": games
    }
    
    return user

if __name__ == "__main__":
    import json
    user = generate_fake_steam_data()
    print(json.dumps(user, indent=4))
