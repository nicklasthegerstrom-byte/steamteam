from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from .vectors import build_game_vector, build_genre_vector


@dataclass
class Snapshot:
    user_id: int
    created_at: datetime
    game_vector: dict[int, float]
    genre_vector: dict[str, float]

    # Metod för att spara snapshot till en dict -> JSON/Databas
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            # JSON kräver str-keys, så vi gör det tydligt här
            "game_vector": {str(k): float(v) for k, v in self.game_vector.items()},
            "genre_vector": {str(k): float(v) for k, v in self.genre_vector.items()},
        }

    # Metod för att läsa in en snapshot från JSON/Databas -> Pythonobjekt (appid-key: int)
    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            user_id=int(data["user_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            game_vector={int(k): float(v) for k, v in data["game_vector"].items()},
            genre_vector={str(k): float(v) for k, v in data["genre_vector"].items()},
        )

    # __str__ för att kunna printa snapshotten snyggt om man vill
    def __str__(self) -> str:
        lines = [
            f"Snapshot for user {self.user_id}",
            f"Created at: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Game vector:",
        ]

        for appid, weight in self.game_vector.items():
            lines.append(f"  {appid}: {round(weight * 100, 2)} %")

        lines.append("")
        lines.append("Genre vector:")

        for genre, weight in self.genre_vector.items():
            lines.append(f"  {genre}: {round(weight * 100, 2)} %")

        return "\n".join(lines)

# Bygger och returnerar ett Snapshot-objekt (user-id + vektorer + timestamp)
def create_snapshot(user_id: int, games: list[dict]) -> Snapshot:
    if not games:
        raise ValueError("No games provided")

    games_sorted = sorted(games, key=lambda g: g["playtime"], reverse=True)

    game_vector = build_game_vector(games_sorted)
    genre_vector = build_genre_vector(games_sorted, game_vector)

    return Snapshot(
        user_id=user_id,
        created_at=datetime.now(),
        game_vector=game_vector,
        genre_vector=genre_vector,
    )


# Hjälpfunktion för att läsa in en Snapshot från JSON (och få ett matchningsklart objekt)
def load_snapshot_from_json(path: Path) -> Snapshot:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return Snapshot.from_dict(data)