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
# Match two users
# ==================================================

def match_users(
    user_a_genre_vector: Dict[str, float],
    user_b_genre_vector: Dict[str, float],
    user_a_category_vector: Dict[str, float],
    user_b_category_vector: Dict[str, float],
    user_a_game_vector: Dict[int, float],
    user_b_game_vector: Dict[int, float],
    genre_weight: float = 0.5,
    category_weight: float = 0.3,
    game_weight: float = 0.2
) -> float:
    """
    Matchar två users baserat på deras vectors
    """

    genre_score = cosine_similarity_dict(
        user_a_genre_vector,
        user_b_genre_vector
    )

    category_score = cosine_similarity_dict(
        user_a_category_vector,
        user_b_category_vector
    )

    game_score = cosine_similarity_dict(
        user_a_game_vector,
        user_b_game_vector
    )

    return (
        genre_score * genre_weight +
        category_score * category_weight +
        game_score * game_weight
    )


# ==================================================
# Match one user vs many
# ==================================================

def find_best_matches(
    target_user_id: int,
    target_vectors: Dict,
    other_users: Dict[int, Dict],
    top_n: int = 5
) -> List[Tuple[int, float]]:
    """
    Returnerar top N matchningar för en user
    """

    matches: List[Tuple[int, float]] = []

    for user_id, vectors in other_users.items():
        if user_id == target_user_id:
            continue

        score = match_users(
            target_vectors["genre_vector"],
            vectors["genre_vector"],
            target_vectors["category_vector"],
            vectors["category_vector"],
            target_vectors["game_vector"],
            vectors["game_vector"],
        )

        matches.append((user_id, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]