

#Städa Json för att plocka ut nödvändig data till vector
def extract_games(steam_json: dict) -> list[dict]:
    games = []

    for g in steam_json["games"]:
        games.append({
            "game": g["name"],
            "appid": g["appid"],
            "playtime": g["playtime_forever"],
            "genres": g["genres"]
        })

    return games

#Sortera spel efter speltid
def sort_games(games: list):

    games_sorted = sorted(
        games,
        key=lambda g: g["playtime"],
        reverse=True
    )

    return games_sorted


#Vector logik för -> snapshot -> MATCHNING

def build_game_vector(games: list[dict]) -> dict[int, float]:
    total = sum(g["playtime"] for g in games)

    #Kontrollera speltid
    MIN_TOTAL_PLAYTIME = 100

    if total == 0:
        raise ValueError("Total playtime is 0")
    #Byt detta till logger sen för att varna för osäker vector
    if total < MIN_TOTAL_PLAYTIME:
        print("Low playtime - results may be unreliable")
    #Returnerar en vector som dict
    return {g["appid"]: g["playtime"] / total for g in games}


def build_genre_vector(
    games: list[dict],
    game_vector: dict[int, float]
) -> dict[str, float]:

    genre_vector: dict[str, float] = {}

    for g in games:
        appid = g["appid"]
        weight = game_vector[appid]
        genres = g["genres"]

    
        if not genres:
            continue
        #Fördela vikter mellan så många genres spelet har
        share = weight / len(genres)

        for genre in genres:
            genre_vector[genre] = genre_vector.get(genre, 0.0) + share
    #Returnerar en vector som dict
    return genre_vector


