# api/steam_store.py

import requests

__all__ = ["fetch_store_metadata"]

def fetch_store_metadata(appid: int, cc="us", lang="english") -> tuple[list[str], list[str]]:
    """
    Fetch genres and categories from Steam Storefront API.
    """
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": cc, "l": lang}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError):
        return [], []  # Fail soft if Storefront API fails

    app_data = data.get(str(appid), {})
    if not app_data.get("success"):
        return [], []

    info = app_data.get("data", {})
    genres = [g.get("description") for g in info.get("genres", []) if "description" in g]
    categories = [c.get("description") for c in info.get("categories", []) if "description" in c]

    return genres, categories
