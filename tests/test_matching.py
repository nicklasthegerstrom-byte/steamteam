import math
import pytest

from src.matching import (
    cosine_similarity_dict,
    match_users,
    find_best_matches,
)

# =========================
# Test cosine similarity
# =========================

def test_cosine_similarity_identical_vectors():
    v = {"Action": 1.0, "RPG": 2.0}
    score = cosine_similarity_dict(v, v)
    assert math.isclose(score, 1.0), "Identiska vektorer ska ge 1.0"


def test_cosine_similarity_no_overlap():
    v1 = {"Action": 1.0}
    v2 = {"Puzzle": 1.0}
    score = cosine_similarity_dict(v1, v2)
    assert score == 0.0, "Vektorer utan gemensamma nycklar ska ge 0.0"


# =========================
# Test match_users
# =========================

def test_match_users_higher_score_for_similar_users():
    user_a = {"Action": 0.7, "RPG": 0.3}
    user_b = {"Action": 0.6, "RPG": 0.4}
    user_c = {"Puzzle": 1.0}

    score_ab = match_users(user_a, user_b)
    score_ac = match_users(user_a, user_c)

    assert score_ab > score_ac, "Mer lika användare ska ha högre poäng"


# =========================
# Test find_best_matches
# =========================

def test_find_best_matches_returns_sorted_results():
    target_user = {"Action": 1.0}

    others = {
        1: {"genre_vector": {"Action": 0.9}, "game_vector": None},
        2: {"genre_vector": {"Puzzle": 1.0}, "game_vector": None},
        3: {"genre_vector": {"Action": 0.5}, "game_vector": None},
    }

    results = find_best_matches(
        target_user_id=0,
        target_genre_vector=target_user,
        target_game_vector=None,
        other_users=others,
        top_n=2,
    )

    # Ska returnera två resultat, sorterade högst poäng först
    assert len(results) == 2
    assert results[0][1] >= results[1][1], "Resultaten ska vara sorterade"