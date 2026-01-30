import json
from pathlib import Path

CACHE_FILE = Path(__file__).parent / "store_cache.json"

# ------------------ Internal helpers ------------------

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open(encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: store cache corrupted, starting fresh")
    return {}

def _save_cache(cache: dict) -> None:
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

# ------------------ Public API ------------------

def store_cache_get(appid: int):
    """
    Returns (genres, categories) for appid if cached.
    Returns ([], []) if not found.
    """
    cache = _load_cache()
    entry = cache.get(str(appid))
    if not entry:
        return [], []

    return entry.get("genres", []), entry.get("categories", [])

def store_cache_set(appid: int, name: str, genres: list[str], categories: list[str]) -> None:
    """
    Store Steam Store metadata for an appid.
    """
    cache = _load_cache()
    cache[str(appid)] = {
        "appid": appid,
        "name": name,
        "genres": genres,
        "categories": categories,
    }
    _save_cache(cache)
