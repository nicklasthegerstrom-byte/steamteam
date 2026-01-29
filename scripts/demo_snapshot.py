import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import json

OUT_DIR = BASE_DIR / "data" / "demo"

from src.vectors import extract_games, sort_games
from src.snapshots import create_snapshot

# Rå Steam-data för demo
steam_json_raw = """
{
  "steam_id": "12345678912345678",
  "game_count": 5,
  "games": [
    {
      "appid": 306130,
      "name": "The Elder Scrolls Online",
      "playtime_forever": 408543,
      "genres": ["Action", "Adventure", "Massively Multiplayer", "RPG"]
    },
    {
      "appid": 730,
      "name": "Counter-Strike 2",
      "playtime_forever": 146920,
      "genres": ["Action", "Free To Play"]
    },
    {
      "appid": 1282100,
      "name": "Remnant II",
      "playtime_forever": 50755,
      "genres": ["Action", "Adventure", "RPG"]
    },
    {
      "appid": 386180,
      "name": "Crossout",
      "playtime_forever": 36713,
      "genres": ["Action", "Adventure", "Massively Multiplayer", "Racing", "Free To Play"]
    },
    {
      "appid": 1501750,
      "name": "Lords of the Fallen",
      "playtime_forever": 17211,
      "genres": ["Action", "Adventure", "RPG"]
    }
  ]
}
"""

#Funktion som sparar en snapshot i data/demo/snapshot_user1.json
#OCH printar en snapshot som den ser ut för matchningen när man gör ett snapshot objekt
def main() -> None:
    steam_payload = json.loads(steam_json_raw)

    games = extract_games(steam_payload)
    games_sorted = sort_games(games)

    snapshot = create_snapshot(user_id=1, games=games_sorted)

    print("\n=== SNAPSHOT (MATCHNINGSKLAR PYTHON-DATA) ===\n")

    snapshot_data = {
        "user_id": snapshot.user_id,
        "created_at": snapshot.created_at,
        "game_vector": snapshot.game_vector,     # dict[int, float]
        "genre_vector": snapshot.genre_vector,   # dict[str, float]
    }

    print(snapshot_data)

    # === SPARA SNAPSHOT SOM JSON (DB / demo) ===
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "snapshot_user1.json"

    out_path.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\nSaved demo snapshot as JSON to: {out_path}")


if __name__ == "__main__":
    main()