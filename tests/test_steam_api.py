"""
Tests for api.steam_api
"""

import random
import api.steam_api as steam_api  # Import the module under test


# -------------------------
# Basic sanity test
# -------------------------

def test_fake_user_top_games_basic_structure():
    """
    Verify that the fake function returns the expected top-level structure.
    """
    result = steam_api.get_fake_user_top_games("any-user", top_n=3)

    # Top-level keys
    assert isinstance(result, dict)
    assert "steam_id" in result
    assert "game_count" in result
    assert "games" in result

    # steam_id should look like a SteamID64 (17 digits)
    assert isinstance(result["steam_id"], str)
    assert result["steam_id"].isdigit()
    assert len(result["steam_id"]) == 17

    # game_count should match top_n
    assert result["game_count"] == 3

    # games should be a list of length top_n
    assert isinstance(result["games"], list)
    assert len(result["games"]) == 3


# -------------------------
# Game object structure
# -------------------------

def test_fake_game_object_shape():
    """
    Check that each fake game contains the expected fields and types.
    """
    result = steam_api.get_fake_user_top_games("user", top_n=1)
    game = result["games"][0]

    # Required keys
    assert "appid" in game
    assert "name" in game
    assert "playtime_forever" in game
    assert "playtime_2weeks" in game
    assert "genres" in game
    assert "categories" in game

    # Check types
    assert isinstance(game["appid"], int)
    assert isinstance(game["name"], str)
    assert isinstance(game["playtime_forever"], int)
    assert game["playtime_2weeks"] is None or isinstance(game["playtime_2weeks"], int)
    assert isinstance(game["genres"], list)
    assert isinstance(game["categories"], list)


# -------------------------
# Controlled randomness
# -------------------------

def test_fake_user_top_games_is_deterministic_with_seed():
    """
    By seeding random, the output becomes predictable.
    Useful for asserting specific values.
    """
    random.seed(42)
    result_1 = steam_api.get_fake_user_top_games("user", top_n=2)

    random.seed(42)
    result_2 = steam_api.get_fake_user_top_games("user", top_n=2)

    # Entire output should now be identical
    assert result_1 == result_2


# -------------------------
# Edge cases
# -------------------------

def test_zero_games_requested():
    """
    Requesting zero games should return an empty list and not crash.
    """
    result = steam_api.get_fake_user_top_games("user", top_n=0)
    assert result["game_count"] == 0
    assert result["games"] == []


def test_genres_and_categories_can_be_empty():
    """
    Genres and categories can be empty lists in realistic Steam data.
    """
    result = steam_api.get_fake_user_top_games("user", top_n=5)
    for game in result["games"]:
        assert isinstance(game["genres"], list)
        assert isinstance(game["categories"], list)


# -------------------------
# get_user_top_games with mocked HTTP
# -------------------------

def test_get_user_top_games_happy_path(monkeypatch):
    """
    Test get_user_top_games with mocked internal functions.
    Avoid real HTTP requests.
    """
    monkeypatch.setenv("STEAM_API_KEY", "fake-key-for-tests")

    # Mock internal helpers
    monkeypatch.setattr(steam_api, "_resolve_steam_id", lambda user_string: "12345678901234567")
    monkeypatch.setattr(
        steam_api,
        "_fetch_user_games",
        lambda steam_id: [
            {"appid": 1, "name": "Game A", "playtime_forever": 100},
            {"appid": 2, "name": "Game B", "playtime_forever": 50},
        ]
    )
    monkeypatch.setattr(
        steam_api,
        "_enrich_games",
        lambda games, top_n: [
            {
                "appid": 1,
                "name": "Game A",
                "playtime_forever": 100,
                "playtime_2weeks": None,
                "genres": ["RPG"],
                "categories": ["Single-player"]
            }
        ]
    )

    # Call the function under test
    result = steam_api.get_user_top_games("some-user", top_n=1)

    assert result["steam_id"] == "12345678901234567"
    assert result["game_count"] == 1
    assert len(result["games"]) == 1
    assert result["games"][0]["name"] == "Game A"


def test_get_user_top_games_no_games(monkeypatch):
    """
    Test get_user_top_games when the user owns no games.
    """
    monkeypatch.setenv("STEAM_API_KEY", "fake-key-for-tests")

    monkeypatch.setattr(steam_api, "_resolve_steam_id", lambda user_string: "99999999999999999")
    monkeypatch.setattr(steam_api, "_fetch_user_games", lambda steam_id: [])
    monkeypatch.setattr(steam_api, "_enrich_games", lambda games, top_n: [])

    result = steam_api.get_user_top_games("empty-user", top_n=5)

    assert result["steam_id"] == "99999999999999999"
    assert result["game_count"] == 0
    assert result["games"] == []
