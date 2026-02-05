# ----------------------------------------------------------------------
# Patch SETTINGS and DB_PATH for testing
# ----------------------------------------------------------------------
# We patch the global SETTINGS object and src.db.DB_PATH to point to
# a separate test database. This is necessary because:
# 1. The original SETTINGS and DB_PATH are loaded at import time in modules
#    like src.db and services, so changing environment variables alone
#    won’t affect already imported modules.
# 2. We cannot modify settings.py directly because it’s shared among the team.
# 3. By creating a new Settings instance with only the required fields
#    overridden (db_path, steam_api_key) and reloading src.db,
#    all database operations within this test module will use an
#    isolated test database.
# This ensures:
# - Tests in this module are deterministic and do not affect the real database.
# - Each test module gets its own isolated database (no cross-test contamination).
# - The patch works even if other tests have already imported SETTINGS.
# - No manual duplication of all settings fields is required.

import os
import sys
from pathlib import Path
import pytest

@pytest.fixture(scope="module", autouse=True)
def test_environment(tmp_path_factory):
    import data.settings as settings_module
    import src.db as db_module
    import importlib
    from data.settings import Settings
    from pathlib import Path

    # --- Save original objects ---
    original_settings = getattr(settings_module, "SETTINGS", None)
    original_db_path = getattr(db_module, "DB_PATH", None)

    # --- Patch SETTINGS ---
    test_db_path = tmp_path_factory.mktemp("db") / "test.sqlite3"
    fields = {f: getattr(original_settings, f) for f in Settings.__dataclass_fields__}
    fields.update({"db_path": test_db_path, "steam_api_key": "TEST_KEY"})
    settings_module.SETTINGS = Settings(**fields)

    # --- Patch DB_PATH ---
    db_module.DB_PATH = test_db_path

    # --- Reload db module to pick up new DB_PATH ---
    importlib.reload(db_module)

    # --- Create tables in test DB ---
    db_module.create_tables(test_db_path)

    yield test_db_path

    # --- Teardown ---
    if test_db_path.exists():
        test_db_path.unlink()
    if original_settings:
        settings_module.SETTINGS = original_settings
    if original_db_path:
        db_module.DB_PATH = original_db_path
    
    # reload original DB_PATH
    importlib.reload(db_module)


# =========================================================
# Mock Steam API
# =========================================================

@pytest.fixture(autouse=True)
def mock_steam(monkeypatch):
    """
    Automatically patches Steam API calls for tests, including signup and profile sync.
    """
    id_map = {}
    counter = 10000000000000000

    # ------------------------
    # Signup always generates new unique SteamID
    # ------------------------
    def resolve_for_signup(steam_input):
        nonlocal counter
        counter += 1
        steam_id = str(counter)
        id_map[steam_id] = steam_id
        return steam_id

    # ------------------------
    # Sync reuses SteamID if known, handles vanity/manual input
    # ------------------------
    def resolve_for_sync(steam_input):
        if steam_input.isdigit() and len(steam_input) == 17:
            return steam_input
        return id_map[steam_input]

    # ------------------------
    # Patch the functions
    # ------------------------
    monkeypatch.setattr(
        "services.auth_service.resolve_steam_id",
        resolve_for_signup
    )
    
    monkeypatch.setattr(
        "services.profile_sync.resolve_steam_id",
        resolve_for_sync
    )

    # ------------------------
    # Patch fetch_owned_games
    # ------------------------
    monkeypatch.setattr(
        "services.profile_sync.fetch_owned_games",
        lambda steam_id: [
            {"appid": 1, "playtime_forever": 100},
            {"appid": 2, "playtime_forever": 200, "playtime_2weeks": 100},
            {"appid": 1337, "name": "Name That Will Be Replaced", "playtime_forever": 600, "playtime_2weeks": 100},
        ]
    )

@pytest.fixture(autouse=True)
def mock_store_cache(monkeypatch):
    """
    Automatically patches store_cache.py for tests.
    store_cache.py either returns gamedata from database if appid exists there
    or by returning gamedata that has been fetched if appid did not exist in database
    """
    
    def fetch_game_data(appid):
        fake_data = {
            "appid": appid,
            "name": f"Monkeypatch {str(appid)}",
            "genres": ["Hacking"],
            "categories": ["Monkeypatching", "PvP", "Co-op", "Something"]
            }
            
        return fake_data
        
    monkeypatch.setattr(
        "data.store_cache._fetch_game_data",
        fetch_game_data
    )
    

# =========================================================
# Integration test
# =========================================================

def test_full_flow(test_environment):
    """
    Full end-to-end flow test:
    1. Signup two users
    2. Sync their profiles while checking gamecache before and after to verify it works
    3. Perform matching
    4. Check both users matchcards to verify various data
    """
    # Import services AFTER test_environment patched SETTINGS
    from services.auth_service import signup, get_user_by_id
    from services.profile_sync import sync_user_profile
    from services.matching_service import match_user_id
    from src.db import get_connection, GameCache
    
    # Add user accounts
    user_id_1 = signup(username="username_1", email="email_1", steam_id="steam_1")
    user_id_2 = signup(username="username_2", email="email_2", steam_id="steam_2")
    
    assert user_id_1 == 1 and user_id_2 == 2
    
    # Check user accounts
    user_1 = get_user_by_id(user_id_1)
    user_2 = get_user_by_id(user_id_2)
    
    assert user_1.get("user_id") == user_id_1 == 1
    assert user_2.get("user_id") == user_id_2 == 2
    assert user_1.get("username") == "username_1" and user_1.get("email") == "email_1" and user_1.get("steam_id") == "10000000000000001"
    assert user_2.get("username") == "username_2" and user_2.get("email") == "email_2" and user_2.get("steam_id") == "10000000000000002"
    
    # Game should not be in cache
    conn = get_connection()
    cache = GameCache(conn)
    assert cache.get_game(1337) is None
    
    # Sync user accounts
    snapshot_1 = sync_user_profile(user_id=user_id_1)
    snapshot_2 = sync_user_profile(user_id=user_id_2)
    
    # Game should be in cache because we synced users
    cached_game = cache.get_game(1337)
    assert cached_game is not None
    assert cached_game["name"] == "Monkeypatch 1337"
    
    # Verify snapshots
    assert snapshot_1.user_id == user_id_1 and snapshot_2.user_id == user_id_2
    
    # Perform matching
    matches_1 = match_user_id(snapshot_1.user_id)
    matches_2 = match_user_id(snapshot_2.user_id)
    
    # Both users matched with 1 user each, they matched with eachother
    assert len(matches_1) == len(matches_2) == 1
    
    # Check matches
    assert matches_1[0].username == "username_2" and matches_2[0].username == "username_1"
    assert int(matches_1[0].steam_id) > int(matches_2[0].steam_id)
    assert matches_1[0].top_games[0] == matches_2[0].top_games[0] == ("Monkeypatch 1337", 10)
    assert matches_1[0].top_genres[0] == matches_2[0].top_genres[0] == ("Hacking", 1.0)
    assert matches_1[0].playstyles == matches_2[0].playstyles
    
    
