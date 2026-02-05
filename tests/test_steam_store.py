import pytest
from types import SimpleNamespace
from api import steam_store
import requests

# ------------------- Fixtures -------------------

@pytest.fixture
def fake_store_response():
    return {
        "123": {
            "success": True,
            "data": {
                "name": "examplename",
                "genres": [{"description": "RPG"}, {"description": "Adventure"}],
                "categories": [{"description": "Single-player"}, {"description": "Co-op"}]
            }
        }
    }

@pytest.fixture
def fake_store_failure():
    return {"123": {"success": False}}

# ------------------- Tests -------------------

def test_fetch_store_metadata_happy(monkeypatch, fake_store_response):
    # Mock requests.get for “happy path”
    def fake_get(url, params, timeout, headers):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: fake_store_response
        )

    monkeypatch.setattr(steam_store.requests, "get", fake_get)

    data = steam_store.fetch_store_metadata(123)
    name = data["name"]
    genres = data["genres"]
    categories = data["categories"]
    
    assert name == "examplename"
    assert genres == ["RPG", "Adventure"]
    assert categories == ["Single-player", "Co-op"]

def test_fetch_store_metadata_fail(monkeypatch, fake_store_failure):
    # Mock requests.get when success=False
    def fake_get(url, params, timeout, headers):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: fake_store_failure
        )

    monkeypatch.setattr(steam_store.requests, "get", fake_get)

    data = steam_store.fetch_store_metadata(123)
    
    assert data is None

def test_fetch_store_metadata_request_exception(monkeypatch):
    # Mock requests.get that raises RequestException
    def fake_get(url, params, timeout, headers):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(steam_store.requests, "get", fake_get)

    data = steam_store.fetch_store_metadata(123)
    
    assert data is None
