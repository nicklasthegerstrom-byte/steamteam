from dataclasses import dataclass
from datetime import datetime
from vectors import build_game_vector, build_genre_vector


@dataclass
class Snapshot:
    user_id: int
    created_at: datetime
    game_vector: dict[int, float]
    genre_vector: dict[str, float]

    #Funktion för att spara snapshot till en dict
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "game_vector": self.game_vector,
            "genre_vector": self.genre_vector,
        }

    #__str__ För att kunna printa snapshotten snyggt om man vill
    def __str__(self) -> str:
        lines = [
            f"Snapshot for user {self.user_id}",
            f"Created at: {self.created_at}",
            "",
            "Game vector:"
        ]

        for appid, weight in self.game_vector.items():
            lines.append(f"  {appid}: {round(weight * 100, 2)} %")

        lines.append("")
        lines.append("Genre vector:")

        for genre, weight in self.genre_vector.items():
            lines.append(f"  {genre}: {round(weight * 100, 2)} %")

        return "\n".join(lines)

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
        genre_vector=genre_vector
    )