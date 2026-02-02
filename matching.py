import math
from dataclasses import dataclass
from datetime import datetime

# ==================================================
# Vector builders
# ==================================================

def build_game_vector(games: list[dict]) -> dict[int, float]:
    total = sum(g["playtime"] for g in games)

    if total == 0:
        raise ValueError("Total playtime is 0")

    return {
        g["appid"]: g["playtime"] / total
        for g in games
    }


def build_genre_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:

    genre_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        genres = g.get("genres", [])

        if not genres:
            continue

        share = weight / len(genres)

        for genre in genres:
            genre_vector[genre] = genre_vector.get(genre, 0.0) + share

    return genre_vector


def build_category_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:

    category_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        categories = g.get("categories", [])

        if not categories:
            continue

        share = weight / len(categories)

        for cat in categories:
            category_vector[cat] = category_vector.get(cat, 0.0) + share

    return category_vector


# ==================================================
# Snapshot
# ==================================================

@dataclass
class Snapshot:
    user_id: int
    created_at: datetime
    game_vector: dict[int, float]
    genre_vector: dict[str, float]
    category_vector: dict[str, float]


def create_snapshot(user_id: int, games: list[dict]) -> Snapshot:
    game_vector = build_game_vector(games)
    genre_vector = build_genre_vector(games, game_vector)
    category_vector = build_category_vector(games, game_vector)

    return Snapshot(
        user_id=user_id,
        created_at=datetime.now(),
        game_vector=game_vector,
        genre_vector=genre_vector,
        category_vector=category_vector
    )


# ==================================================
# Cosine similarity
# ==================================================

def cosine_similarity_dict(v1: dict, v2: dict) -> float:
    common_keys = set(v1.keys()) & set(v2.keys())
    dot_product = sum(v1[k] * v2[k] for k in common_keys)

    norm_v1 = math.sqrt(sum(v ** 2 for v in v1.values()))
    norm_v2 = math.sqrt(sum(v ** 2 for v in v2.values()))

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


# ==================================================
# Matchmaking
# ==================================================

def match_users(
    a: Snapshot,
    b: Snapshot,
    genre_weight: float = 0.5,
    category_weight: float = 0.3,
    game_weight: float = 0.2
) -> float:

    genre_score = cosine_similarity_dict(
        a.genre_vector,
        b.genre_vector
    )

    category_score = cosine_similarity_dict(
        a.category_vector,
        b.category_vector
    )

    game_score = cosine_similarity_dict(
        a.game_vector,
        b.game_vector
    )

    return (
        genre_score * genre_weight +
        category_score * category_weight +
        game_score * game_weight
    )


def find_best_matches(
    target_snapshot: Snapshot,
    other_snapshots: list[Snapshot],
    top_n: int = 5
) -> list[tuple[int, float]]:

    matches = []

    for snap in other_snapshots:
        if snap.user_id == target_snapshot.user_id:
            continue

        score = match_users(target_snapshot, snap)
        matches.append((snap.user_id, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]