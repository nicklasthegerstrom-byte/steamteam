import json
from dataclasses import dataclass
from datetime import datetime

#Bara jsondata för att testa funktionerna
steam_json_raw = """
{
    "steam_id": "12345678912345678",
    "game_count": 5,
    "games": [
        {
            "appid": 306130,
            "name": "The Elder Scrolls Online",
            "playtime_forever": 408543,
            "playtime_2weeks": null,
            "genres": [
                "Action",
                "Adventure",
                "Massively Multiplayer",
                "RPG"
            ],
            "categories": [
                "Multi-player",
                "MMO",
                "PvP",
                "Online PvP",
                "Co-op",
                "Online Co-op",
                "Steam Trading Cards",
                "Captions available",
                "In-App Purchases",
                "Camera Comfort",
                "Custom Volume Controls",
                "Playable without Timed Input",
                "Stereo Sound",
                "Surround Sound",
                "Partial Controller Support",
                "HDR available",
                "Family Sharing"
            ]
        },
        {
            "appid": 730,
            "name": "Counter-Strike 2",
            "playtime_forever": 146920,
            "playtime_2weeks": 61,
            "genres": [
                "Action",
                "Free To Play"
            ],
            "categories": [
                "Multi-player",
                "Cross-Platform Multiplayer",
                "Steam Trading Cards",
                "Steam Workshop",
                "In-App Purchases",
                "Adjustable Text Size",
                "Camera Comfort",
                "Color Alternatives",
                "Custom Volume Controls",
                "Playable without Timed Input",
                "Stereo Sound",
                "Surround Sound",
                "Valve Anti-Cheat enabled",
                "Stats",
                "Remote Play on Phone",
                "Remote Play on Tablet",
                "Remote Play on TV",
                "Steam Timeline"
            ]
        },
        {
            "appid": 1282100,
            "name": "Remnant II",
            "playtime_forever": 50755,
            "playtime_2weeks": 1162,
            "genres": [
                "Action",
                "Adventure",
                "RPG"
            ],
            "categories": [
                "Single-player",
                "Multi-player",
                "Co-op",
                "Online Co-op",
                "Steam Achievements",
                "Full controller support",
                "Steam Cloud",
                "Family Sharing"
            ]
        },
        {
            "appid": 386180,
            "name": "Crossout",
            "playtime_forever": 36713,
            "playtime_2weeks": null,
            "genres": [
                "Action",
                "Adventure",
                "Massively Multiplayer",
                "Racing",
                "Free To Play"
            ],
            "categories": [
                "Multi-player",
                "MMO",
                "PvP",
                "Online PvP",
                "Co-op",
                "Online Co-op",
                "Steam Achievements",
                "Full controller support",
                "Steam Trading Cards",
                "In-App Purchases",
                "Camera Comfort",
                "Color Alternatives",
                "Custom Volume Controls",
                "Playable without Timed Input",
                "Stereo Sound",
                "Subtitle Options",
                "Remote Play on Tablet",
                "Remote Play on TV"
            ]
        },
        {
            "appid": 1501750,
            "name": "Lords of the Fallen",
            "playtime_forever": 17211,
            "playtime_2weeks": 1981,
            "genres": [
                "Action",
                "Adventure",
                "RPG"
            ],
            "categories": [
                "Single-player",
                "Multi-player",
                "PvP",
                "Online PvP",
                "Co-op",
                "Online Co-op",
                "Cross-Platform Multiplayer",
                "Steam Achievements",
                "Full controller support",
                "Steam Cloud",
                "Family Sharing"
            ]
        }
    ]
}

"""
#skapar en dict från json-sträng för testning
steam_json = json.loads(steam_json_raw)

#Städa Json för att plocka ut nödvändig data till vector
def extract_games(steam_json: dict) -> list[dict]:
    games = []

    for g in steam_json["games"]:
        games.append({
            "game": g["name"],
            "appid": g["appid"],
            "playtime": g["playtime_forever"],
            "genres": g["genres"]
        })

    return games

#Lista med spel för testning
games = extract_games(steam_json)

#Sortera spel efter speltid
def sort_games(games: list):

    games_sorted = sorted(
        games,
        key=lambda g: g["playtime"],
        reverse=True
    )

    return games_sorted


def print_games(games: list):
    for g in games:
        hours = round(g['playtime'] / 60, 2)
        print(f"Game: {g['game']}, spelat i {hours} timmar")

#Stoppa detta i egen snapshot modul senare
@dataclass
class Snapshot:
    user_id: int
    created_at: datetime
    games: list[dict]

def create_snapshot(user_id: int, games: list[dict]) -> Snapshot:
    games_sorted = sorted(games, key=lambda g: g["playtime"], reverse=True)
    return Snapshot(
        user_id=user_id,
        created_at=datetime.now(),
        games=games_sorted
    )

#Vector logik för -> snapshot -> MATCHNING

def build_game_vector(games: list[dict]) -> dict[int, float]:
    total = sum(g["playtime"] for g in games)

    #Kontrollera speltid
    MIN_TOTAL_PLAYTIME = 100

    if total == 0:
        raise ValueError("Total playtime is 0")
    #Byt detta till logger sen för att varna för osäker vector
    if total < MIN_TOTAL_PLAYTIME:
        print("Low playtime - results may be unreliable")
    #Returnerar en vector som dict
    return {g["appid"]: g["playtime"] / total for g in games}


def build_genre_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:

    genre_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        genres = g["genres"]

    
        if not genres:
            continue
        #Fördela vikter mellan så många genres spelet har
        share = weight / len(genres)

        for genre in genres:
            genre_vector[genre] = genre_vector.get(genre, 0.0) + share
    #Returnerar en vector som dict
    return genre_vector

games_sorted = sort_games(games)
game_vector = build_game_vector(games_sorted)
genre_vector = build_genre_vector(games, game_vector)

print("Sum weights:", sum(game_vector.values()))
for g in games_sorted:
    print(g["game"], round(game_vector[g["appid"]] * 100, 2), "%")

print()
print()
print("Genre vector:")
for genre, weight in sorted(
    genre_vector.items(),
    key=lambda x: x[1],
    reverse=True):
        print(genre, round(weight * 100, 2), "%")

