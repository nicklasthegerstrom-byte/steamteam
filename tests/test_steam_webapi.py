import pytest
from types import SimpleNamespace
from api import steam_webapi

# ------------------- Setup monkeypatch -------------------
@pytest.fixture(autouse=True)
def fake_steam_key(monkeypatch):
    # set fake STEAM_API_KEY before every test
    monkeypatch.setattr(steam_webapi, "STEAM_API_KEY", "fake-key")

# ------------------- Tests -------------------
def test_resolve_steam_id(monkeypatch):
    # Fake HTTP response
    def fake_get(url, params, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"response": {"steamid": "76561198000000001", "success": 1}}
        )

    monkeypatch.setattr(steam_webapi.requests, "get", fake_get)

    steam_id = steam_webapi.resolve_steam_id("somevanity")
    assert steam_id == "76561198000000001"

def test_fetch_owned_games(monkeypatch):
    fake_games = [{"appid": 1, "name": "Game A", "playtime_forever": 100}]

    def fake_get(url, params, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"response": {"games": fake_games}}
        )

    monkeypatch.setattr(steam_webapi.requests, "get", fake_get)

    games = steam_webapi.fetch_owned_games("12345678901234567")
    assert games == fake_games
