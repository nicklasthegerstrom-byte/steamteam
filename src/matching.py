import math
from typing import Dict, List, Tuple

# ==================================================
# Cosine similarity
# ==================================================

def cosine_similarity_dict(v1: Dict, v2: Dict) -> float:
    """
    Räknar cosine similarity mellan två vectors (dicts)
    """
    common_keys = set(v1.keys()) & set(v2.keys())
    dot_product = sum(v1[k] * v2[k] for k in common_keys)

    norm_v1 = math.sqrt(sum(v ** 2 for v in v1.values()))
    norm_v2 = math.sqrt(sum(v ** 2 for v in v2.values()))

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


# ==================================================
# Match two users (snapshot-version)
# ==================================================

def match_users(
    snapshot_a: Dict,
    snapshot_b: Dict,
    genre_weight: float = 0.2,
    category_weight: float = 0.3,
    game_weight: float = 0.5
) -> float:
    """
    Matchar två users baserat på deras snapshots
    """

    genre_score = cosine_similarity_dict(
        snapshot_a.get("genre_vector", {}),
        snapshot_b.get("genre_vector", {})
    )

    category_score = cosine_similarity_dict(
        snapshot_a.get("category_vector", {}),
        snapshot_b.get("category_vector", {})
    )

    game_score = cosine_similarity_dict(
        snapshot_a.get("game_vector", {}),
        snapshot_b.get("game_vector", {})
    )

    return (
        genre_score * genre_weight +
        category_score * category_weight +
        game_score * game_weight
    )


# ==================================================
# Match one user vs many (snapshot-version)
# ==================================================

def find_best_matches(
    target_user_id: int,
    target_snapshot: Dict,
    other_users: Dict[int, Dict],
    top_n: int = 5
) -> List[Tuple[int, float]]:
    """
    Returnerar top N matchningar för en user
    """

    matches: List[Tuple[int, float]] = []

    for user_id, snapshot in other_users.items():
        if user_id == target_user_id:
            continue

        score = match_users(
            target_snapshot,
            snapshot
        )

        matches.append((user_id, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]
