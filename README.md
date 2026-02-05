![SteamTeam](steamteam-logo.png)

Find your dreamteam (on Steam)

---

## 🎮 What is Steamteam?

Steamteam is an application that helps players discover other users with similar gaming preferences.

Instead of relying on friend lists or manual searching, Steamteam analyzes:
- played games
- genres
- playtime distribution

and matches users using **vector-based similarity**.

The goal is to make it easier to find like-minded gamers and potential gaming partners in a data-driven way.

---

## 🧠 How it works (high level)

1. A user connects their Steam account  
2. Steam game data is fetched via the Steam Web API  
3. The data is transformed into **weighted vectors**  
4. A **snapshot** of the user profile is created  
5. Users are matched by comparing snapshots using similarity algorithms  

The matching logic does **not** use raw Steam data directly – it only works on snapshots.

---

## 📸 What is a Snapshot?

A **snapshot** is a compact, comparable representation of a user’s gaming profile at a specific moment in time.

Each snapshot contains:
- `user_id` – internal Steamteam user ID  
- `created_at` – timestamp  
- `game_vector` – weighted game IDs  
- `genre_vector` – weighted genres  

Snapshots can be:
- printed (for debugging and testing)  
- saved as JSON  
- stored in the database  
- compared efficiently during matching  

This separation keeps matching fast, stable, and reproducible.

---

## 🧮 Matching logic

Users are matched using **cosine similarity** on vectors.

Three signals are combined:
- **Genre similarity** (primary signal)  
- **Game similarity** (secondary signal)  
- **Category similarity** (third playstyle signal) 

Each user is compared against others, producing a match score between `0.0` and `1.0`.

Higher score = more similar gaming preferences.

---

## 🗄️ Database design

Steamteam uses **SQLite** for simplicity and portability.

The database contains three main tables:

### users
Stores Steamteam users (not Steam accounts).

### snapshots
Stores serialized snapshot data used for matching.

### games_cache
Caches Steam Store metadata (genres, categories) to reduce API calls and support future GUI features.

Snapshots are stored as JSON blobs to keep the vector format flexible and version-safe.

---

## 🖥️ Features

- User account system  
- Steam Web API integration  
- Snapshot-based matching  
- Vector similarity algorithms  
- SQLite database persistence  
- Graphical user interface (WIP)  

---

## ⚙️ Requirements

- Python 3  
- Steam account  
- Steam Web API key  
- Internet connection  

---

## 🚀 Running the application

1. Clone the repository  