# tests/test_snapshots.py
from datetime import datetime
import pytest

from src.snapshots import Snapshot, create_snapshot


# Testa att ett snapshot ser ut som den ska (inkl categories + top_games)
def test_create_snapshot_basic():
    games = [
        {
            "appid": 10,
            "playtime": 100,
            "genres": ["Action", "RPG"],
            "categories": ["Single-player", "Co-op"],
            "game": "Game A",
        },
        {
            "appid": 20,
            "playtime": 50,
            "genres": ["Action"],
            "categories": ["Multi-player"],
            "game": "Game B",
        },
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    assert isinstance(snapshot, Snapshot)
    assert snapshot.user_id == 1
    assert isinstance(snapshot.created_at, datetime)

    assert isinstance(snapshot.game_vector, dict)
    assert isinstance(snapshot.genre_vector, dict)
    assert isinstance(snapshot.category_vector, dict)

    # top_games ska finnas och vara en lista
    assert hasattr(snapshot, "top_games")
    assert isinstance(snapshot.top_games, list)


# Testa att game_vector blir normaliserad till 1
def test_game_vector_normalized():
    games = [
        {"appid": 1, "playtime": 100, "genres": ["Action"], "categories": ["Co-op"], "game": "A"},
        {"appid": 2, "playtime": 100, "genres": ["Action"], "categories": ["PvP"], "game": "B"},
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    total = sum(snapshot.game_vector.values())
    assert round(total, 6) == 1.0


# Testa att category_vector aldrig innehåller kategorier utanför whitelist
# (om du kör whitelist-filtrering i build_category_vector)
def test_category_vector_only_contains_whitelisted_categories():
    games = [
        {
            "appid": 1,
            "playtime": 100,
            "genres": ["Action"],
            "categories": ["Co-op", "Steam Cloud", "Family Sharing"],  # två ska filtreras bort
            "game": "A",
        },
        {
            "appid": 2,
            "playtime": 100,
            "genres": ["RPG"],
            "categories": ["Single-player", "Remote Play Together"],
            "game": "B",
        },
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    # whitelist som du har i vectors.py (spelet kan ha fler men de ska filtreras)
    allowed = {
        "Co-op",
        "Online Co-op",
        "Local Co-op",
        "PvP",
        "Online PvP",
        "Multi-player",
        "Single-player",
        "Shared/Split Screen",
        "Remote Play Together",
    }

    assert set(snapshot.category_vector.keys()).issubset(allowed)


# Testa top_games-strukturen (format + rätt ordning)
def test_top_games_structure_and_order():
    games = [
        {"appid": 1, "playtime": 300, "genres": ["Action"], "categories": ["Co-op"], "game": "Big"},
        {"appid": 2, "playtime": 200, "genres": ["RPG"], "categories": ["Single-player"], "game": "Mid"},
        {"appid": 3, "playtime": 100, "genres": ["Indie"], "categories": ["Multi-player"], "game": "Small"},
        {"appid": 4, "playtime": 50, "genres": ["Casual"], "categories": ["Single-player"], "game": "Tiny"},
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    assert len(snapshot.top_games) == 3  # om du tar top 3
    assert snapshot.top_games[0]["name"] == "Big"
    assert snapshot.top_games[1]["name"] == "Mid"
    assert snapshot.top_games[2]["name"] == "Small"

    # format
    for tg in snapshot.top_games:
        assert set(tg.keys()) == {"appid", "name", "playtime", "share"}
        assert isinstance(tg["appid"], int)
        assert isinstance(tg["name"], str)
        assert isinstance(tg["playtime"], int)
        assert isinstance(tg["share"], float)

    # shares borde finnas i game_vector-n (samma vikt)
    # (du kan välja om du vill ha exakt match eller bara typ checka 0-1)
    assert 0.0 <= snapshot.top_games[0]["share"] <= 1.0


# Testa roundtrip: to_dict -> from_dict (inkl category_vector + top_games)
def test_snapshot_to_dict_and_back():
    games = [
        {"appid": 1, "playtime": 100, "genres": ["Action"], "categories": ["Co-op"], "game": "A"},
        {"appid": 2, "playtime": 50, "genres": ["RPG"], "categories": ["Single-player"], "game": "B"},
    ]

    snapshot = create_snapshot(user_id=42, games=games)
    data = snapshot.to_dict()
    loaded = Snapshot.from_dict(data)

    assert loaded.user_id == snapshot.user_id
    assert loaded.game_vector == snapshot.game_vector
    assert loaded.genre_vector == snapshot.genre_vector
    assert loaded.category_vector == snapshot.category_vector
    assert loaded.top_games == snapshot.top_games


# Testa att det crashar att göra en snapshot utan speldata
def test_create_snapshot_with_no_games_raises():
    with pytest.raises(ValueError):
        create_snapshot(user_id=1, games=[])