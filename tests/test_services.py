# ----------------------------------------------------------------------
# Patch SETTINGS and DB_PATH for testing
# ----------------------------------------------------------------------
# We patch the global SETTINGS object and src.db.DB_PATH to point to
# a separate test database. This is necessary because:
# 1. The original SETTINGS and DB_PATH are loaded at import time in modules
#    like src.db and services, so changing environment variables alone
#    won’t affect already imported modules.
# 2. We cannot modify settings.py directly because it’s shared among the team.
# 3. By creating a new Settings instance with only the fields we need
#    overridden (db_path, steam_api_key), and reloading src.db,
#    all database operations in tests will use an isolated test DB.
# This ensures:
# - Tests are deterministic and do not affect the real database.
# - The patch works even if other tests have already imported SETTINGS.
# - No manual duplication of all settings fields is required.

import os
import sys
from pathlib import Path
import pytest

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    import data.settings as settings_module
    import src.db as db_module
    import importlib
    from data.settings import Settings
    from pathlib import Path

    # --- Save original objects ---
    original_settings = getattr(settings_module, "SETTINGS", None)
    original_db_path = getattr(db_module, "DB_PATH", None)

    # --- Patch SETTINGS ---
    test_db_path = Path(__file__).parent / "test.sqlite3"
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
            {"appid": 570, "playtime_forever": 5000, "playtime_2weeks": 120},
            {"appid": 730, "playtime_forever": 3000, "playtime_2weeks": 80},
            {"appid": 440, "playtime_forever": 2000, "playtime_2weeks": 20},
        ]
    )


# =========================================================
# Integration test
# =========================================================

def test_full_flow(test_environment):
    """
    Full end-to-end flow test:
    1. Signup two users
    2. Sync their profiles
    3. Perform matching
    4. Check that both users matched with 1 user each (eachother)
    """
    # Import services AFTER test_environment patched SETTINGS
    from services.auth_service import signup, get_user_by_id
    from services.profile_sync import sync_user_profile
    from services.matching_service import match_user_id
    
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
    
    # Sync user accounts
    snapshot_1 = sync_user_profile(user_id=user_id_1)
    snapshot_2 = sync_user_profile(user_id=user_id_2)
    
    assert snapshot_1.user_id == user_id_1 and snapshot_2.user_id == user_id_2
    
    # Perform matching
    matches_1 = match_user_id(snapshot_1.user_id)
    matches_2 = match_user_id(snapshot_2.user_id)
    
    assert len(matches_1) == len(matches_2) == 1
