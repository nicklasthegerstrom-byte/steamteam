┌──────────────────────────┐
│  Start (CLI)              │
└────────────┬─────────────┘
             │
             v
┌──────────────────────────┐
│  Register user            │
│  - display_name           │
└────────────┬─────────────┘
             │ INSERT
             v
┌──────────────────────────┐
│  Database: users          │
└────────────┬─────────────┘
             │
             v
┌──────────────────────────┐
│  Login (select user)      │
└────────────┬─────────────┘
             │
             v
┌──────────────────────────────────┐
│  Connect / Refresh Spotify        │
│  - PKCE auth                      │
│  - open browser                   │
│  - receive auth code              │
│  - exchange for access_token      │
└────────────┬─────────────────────┘
             │ GET /me/top/artists
             v
┌──────────────────────────┐
│  Spotify JSON             │
│  items[]: artist objects  │
│  - id, name, genres[]     │
└────────────┬─────────────┘
             │
             v
┌──────────────────────────────────┐
│  Parse / Clean data               │
│  - create Artist objects          │
│    (id, name, genres, rank)       │
│  - keep ALL artists               │
│  - normalize strings              │
└────────────┬─────────────────────┘
             │
             v
┌──────────────────────────────────┐
│  Build genre_vector               │
│  - loop through artists           │
│  - weight by artist rank          │
│  - ONLY genres contribute         │
│    (artists w/o genres → 0)       │
│  - sum genre scores               │
│  - normalize to sum = 1.0         │
│  - keep top N genres (optional)   │
└────────────┬─────────────────────┘
             │ INSERT
             v
┌──────────────────────────────────┐
│  Save Snapshot (DB)               │
│  - snapshots (user_id, time)      │
│  - snapshot_genres (genre, weight)│
│  - snapshot_artists (optional)    │
└────────────┬─────────────────────┘
             │
             v
┌──────────────────────────────────┐
│  Match users                      │
│  - genre similarity (cosine)      │
│  - artist overlap (optional)      │
│  - rank matches                   │
└────────────┬─────────────────────┘
             │
             v
┌──────────────────────────┐
│  Display results (CLI)    │
│  - top genres (%)         │
│  - matches + explanation │
└──────────────────────────┘