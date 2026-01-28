import json
from src.vectors import (
    extract_games,
    sort_games,
    build_game_vector,
    build_genre_vector,
)


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

def print_games(games: list):
    for g in games:
        hours = round(g['playtime'] / 60, 2)
        print(f"Game: {g['game']}, spelat i {hours} timmar")

def main() -> None:
    games = extract_games(steam_json)
    games_sorted = sort_games(games)

    print_games(games_sorted)

    game_vector = build_game_vector(games_sorted)
    genre_vector = build_genre_vector(games_sorted, game_vector)

    print("\nSum weights:", round(sum(game_vector.values()), 6))
    print("\nGame vector (percent):")
    for g in games_sorted:
        appid = g["appid"]
        print(f"  {g['game']}: {round(game_vector[appid] * 100, 2)} %")

    print("\nGenre vector (percent):")
    for genre, weight in sorted(genre_vector.items(), key=lambda x: x[1], reverse=True):
        print(f"  {genre}: {round(weight * 100, 2)} %")


if __name__ == "__main__":
    main()