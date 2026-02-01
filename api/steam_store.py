import requests

__all__ = ["fetch_store_metadata"]

def fetch_store_metadata(appid: int, cc: str = "us", lang: str = "english") -> dict | None:
    """
    Fetch genres and categories from Steam Storefront API.
    Returns a dict with keys: appid, name, genres, categories or None if failed.
    """
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": cc, "l": lang}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data: dict = r.json()
    except (requests.RequestException, ValueError):
        return None

    app_data = data.get(str(appid), {})
    if not app_data.get("success"):
        return None

    info = app_data.get("data", {})
    name: str = info.get("name", "unknown")
    genres: list[str] = [g.get("description") for g in info.get("genres", []) if "description" in g]
    categories: list[str] = [c.get("description") for c in info.get("categories", []) if "description" in c]

    return {"appid": appid, "name": name, "genres": genres, "categories": categories}
