from datetime import datetime
import pytest
from src.snapshots import Snapshot, create_snapshot

#Testa att ett snapshot ser ut som den ska
def test_create_snapshot_basic():
    games = [
        {
            "appid": 10,
            "playtime": 100,
            "genres": ["Action", "RPG"],
        },
        {
            "appid": 20,
            "playtime": 50,
            "genres": ["Action"],
        },
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    assert isinstance(snapshot, Snapshot)
    assert snapshot.user_id == 1
    assert isinstance(snapshot.created_at, datetime)

    assert isinstance(snapshot.game_vector, dict)
    assert isinstance(snapshot.genre_vector, dict)

#Testa att en vektors summerade värden blir 1
def test_game_vector_normalized():
    games = [
        {"appid": 1, "playtime": 100, "genres": ["Action"]},
        {"appid": 2, "playtime": 100, "genres": ["Action"]},
    ]

    snapshot = create_snapshot(user_id=1, games=games)

    total = sum(snapshot.game_vector.values())
    assert round(total, 6) == 1.0

#Testa att det funkar läsa till json och från json
def test_snapshot_to_dict_and_back():
    games = [
        {"appid": 1, "playtime": 100, "genres": ["Action"]},
        {"appid": 2, "playtime": 50, "genres": ["RPG"]},
    ]

    snapshot = create_snapshot(user_id=42, games=games)
    data = snapshot.to_dict()

    loaded = Snapshot.from_dict(data)

    assert loaded.user_id == snapshot.user_id
    assert loaded.game_vector == snapshot.game_vector
    assert loaded.genre_vector == snapshot.genre_vector    

#Testa att det crashar att göra en snapshot utan speldata
def test_create_snapshot_with_no_games_raises():
    with pytest.raises(ValueError):
        create_snapshot(user_id=1, games=[])