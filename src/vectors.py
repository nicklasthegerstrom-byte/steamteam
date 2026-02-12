# vectors.py

from services.logger import get_logger

log = get_logger(__name__)


#  Städa Json för att plocka ut nödvändig data till vector
def extract_games(steam_json: dict) -> list[dict]:
    games: list[dict] = []

    for g in steam_json["games"]:
        games.append({
            "game": g["name"],
            "appid": g["appid"],
            "playtime": g["playtime_forever"],
            "genres": g["genres"],
            "categories": g["categories"],
        })

    return games


# Sortera spel efter speltid
def sort_games(games: list[dict]) -> list[dict]:
    games_sorted = sorted(
        games,
        key=lambda g: g["playtime"],
        reverse=True
    )
    return games_sorted


# Vector logik för -> snapshot -> MATCHNING
def build_game_vector(games: list[dict]) -> dict[int, float]:
    total = sum(g["playtime"] for g in games)

    # Kontrollera speltid
    MIN_TOTAL_PLAYTIME = 100

    if total == 0:
        raise ValueError("Total playtime is 0")

    # Byt detta till logger sen för att varna för osäker vector
    if total < MIN_TOTAL_PLAYTIME:
        log.warning("Unstable vector built on total playtime %s minutes", total)

    # Returnerar en vector som dict
    return {g["appid"]: g["playtime"] / total for g in games}


def build_genre_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:
    genre_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        genres = g.get("genres", [])

        if not genres:
            continue

        # Fördela vikter mellan så många genres spelet har
        share = weight / len(genres)

        for genre in genres:
            genre_vector[genre] = genre_vector.get(genre, 0.0) + share

    # Returnerar en vector som dict
    return genre_vector


# Här kommer hantering av categories
# Lista med categories vi bryr oss om:
PLAYSTYLE_WHITELIST = {
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


def build_category_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:
    category_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        categories = g.get("categories", [])

        if not categories:
            continue

        # Ta bort ointressanta kategorier med whitelist
        filtered = [c for c in categories if c in PLAYSTYLE_WHITELIST]
        if not filtered:
            continue

        # Fördela vikten bara över de kategorier vi faktiskt använder
        share = weight / len(filtered)

        for category in filtered:
            category_vector[category] = category_vector.get(category, 0.0) + share

    # Returnerar en vector som dict
    return category_vector


# Grupperade speltyper
COOP = {
    "Co-op",
    "Online Co-op",
    "Local Co-op",
    "Remote Play Together",
}

SOCIAL = {
    "Local Co-op",
    "Shared/Split Screen",
    "Remote Play Together",
}

PVP = {
    "PvP",
    "Online PvP",
}

SOLO = {
    "Single-player",
}

#Funktion för att göra en vektor för grupperade speltyper (ej för matchning, bara för eventuell Gui visning)
def summarize_playstyle(category_vector: dict[str, float]) -> dict[str, float]:

    summary = {
        "coop": 0.0,
        "social": 0.0,
        "pvp": 0.0,
        "solo": 0.0,
    }

    for category, weight in category_vector.items():
        if category in COOP:
            summary["coop"] += weight

        if category in SOCIAL:
            summary["social"] += weight

        if category in PVP:
            summary["pvp"] += weight

        if category in SOLO:
            summary["solo"] += weight

    return summary

