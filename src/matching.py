import math

# =========================
# Cosine similarity (dict)
# =========================
def cosine_similarity_dict(
    v1: dict,
    v2: dict
) -> float:
    common_keys = set(v1.keys()) & set(v2.keys())
    dot_product = sum(v1[k] * v2[k] for k in common_keys)

    norm_v1 = math.sqrt(sum(v ** 2 for v in v1.values()))
    norm_v2 = math.sqrt(sum(v ** 2 for v in v2.values()))

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


# =========================
# Match two users
# =========================
def match_users(
    user_a_genre_vector: dict[str, float],
    user_b_genre_vector: dict[str, float],
    user_a_game_vector: dict[int, float] | None = None,
    user_b_game_vector: dict[int, float] | None = None,
    genre_weight: float = 0.7,
    game_weight: float = 0.3
) -> float:

    genre_score = cosine_similarity_dict(
        user_a_genre_vector,
        user_b_genre_vector
    )

    game_score = 0.0
    if user_a_game_vector and user_b_game_vector:
        game_score = cosine_similarity_dict(
            user_a_game_vector,
            user_b_game_vector
        )

    return (genre_score * genre_weight) + (game_score * game_weight)


# =========================
# Match one user vs many
# =========================
def find_best_matches(
    target_user_id: int,
    target_genre_vector: dict[str, float],
    target_game_vector: dict[int, float],
    other_users: dict[int, dict],
    top_n: int = 5
) -> list[tuple[int, float]]:

    matches = []

    for user_id, data in other_users.items():
        if user_id == target_user_id:
            continue

        score = match_users(
            target_genre_vector,
            data["genre_vector"],
            target_game_vector,
            data["game_vector"]
        )

        matches.append((user_id, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]