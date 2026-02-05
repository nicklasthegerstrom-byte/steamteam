from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple


# -----------------------------
# Basic helpers / validation
# -----------------------------
def _require_nonempty(s: str, field_name: str) -> str:
    if not isinstance(s, str) or not s.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return s.strip()


def _require_nonneg_int(n: int, field_name: str) -> int:
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"{field_name} must be a non-negative int")
    return n


def _require_nonneg_float(x: float, field_name: str) -> float:
    if not isinstance(x, (int, float)) or float(x) < 0:
        raise ValueError(f"{field_name} must be a non-negative number")
    return float(x)


# -----------------------------
# App/User models (DB-level)
# -----------------------------
@dataclass(frozen=True, slots=True)
class User:
    id: int
    username: str
    created_at: str  # ISO string for simplicity

    def __post_init__(self) -> None:
        _require_nonneg_int(self.id, "User.id")
        _require_nonempty(self.username, "User.username")
        _require_nonempty(self.created_at, "User.created_at")


@dataclass(frozen=True, slots=True)
class SteamIdentity:
    steamid64: str  # store as string to avoid int overflow/format issues
    persona_name: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.steamid64, "SteamIdentity.steamid64")


# -----------------------------
# Steam data models
# -----------------------------
@dataclass(frozen=True, slots=True)
class OwnedGame:
    appid: int
    playtime_forever_min: int = 0
    playtime_2weeks_min: int = 0

    def __post_init__(self) -> None:
        _require_nonneg_int(self.appid, "OwnedGame.appid")
        _require_nonneg_int(self.playtime_forever_min, "OwnedGame.playtime_forever_min")
        _require_nonneg_int(self.playtime_2weeks_min, "OwnedGame.playtime_2weeks_min")


@dataclass(frozen=True, slots=True)
class GameMeta:
    appid: int
    name: str
    genres: Tuple[str, ...] = ()
    categories: Tuple[str, ...] = ()
    # "tags" are not reliably available via official store appdetails.
    # Keep optional in case you add another source later.
    tags: Tuple[str, ...] = ()
    is_free: Optional[bool] = None
    release_date: Optional[str] = None  # keep as string from API; parse later if needed

    def __post_init__(self) -> None:
        _require_nonneg_int(self.appid, "GameMeta.appid")
        _require_nonempty(self.name, "GameMeta.name")


# -----------------------------
# Derived profile used for matching
# -----------------------------
Vector = Dict[str, float]


@dataclass(frozen=True, slots=True)
class UserGameProfile:
    """
    This is the normalized “matching input” for one user.
    It can be stored as JSON in DB (vectors + summary stats).
    """
    user_id: int
    steam: Optional[SteamIdentity]
    owned_games: Tuple[OwnedGame, ...] = ()

    # Feature vectors for matching
    genre_vector: Vector = field(default_factory=dict)        # e.g. {"Action": 1.2, "RPG": 0.7}
    category_vector: Vector = field(default_factory=dict)     # e.g. {"Co-op": 0.9, "PvP": 0.3}
    tag_vector: Vector = field(default_factory=dict)          # optional

    # Metadata to help UI / debugging
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        _require_nonneg_int(self.user_id, "UserGameProfile.user_id")
        _require_nonempty(self.updated_at, "UserGameProfile.updated_at")


@dataclass(frozen=True, slots=True)
class MatchBreakdown:
    genre_similarity: float
    category_similarity: float
    tag_similarity: float
    overall_score: float

    def __post_init__(self) -> None:
        # similarities are typically [0,1], but keep lenient in case you re-scale later
        _require_nonneg_float(self.genre_similarity, "MatchBreakdown.genre_similarity")
        _require_nonneg_float(self.category_similarity, "MatchBreakdown.category_similarity")
        _require_nonneg_float(self.tag_similarity, "MatchBreakdown.tag_similarity")
        _require_nonneg_float(self.overall_score, "MatchBreakdown.overall_score")


@dataclass(frozen=True, slots=True)
class MatchResult:
    user_a_id: int
    user_b_id: int
    breakdown: MatchBreakdown
    top_shared_genres: Tuple[str, ...] = ()
    top_shared_categories: Tuple[str, ...] = ()
    top_shared_games: Tuple[int, ...] = ()  # appids; resolve names via GameMeta cache/DB

    def __post_init__(self) -> None:
        _require_nonneg_int(self.user_a_id, "MatchResult.user_a_id")
        _require_nonneg_int(self.user_b_id, "MatchResult.user_b_id")


# -----------------------------
# Lightweight parsing helpers (optional)
# Keep in models.py only if you want simple conversion;
# otherwise move to api/*.
# -----------------------------
def parse_owned_games_from_webapi(payload: Dict[str, Any]) -> List[OwnedGame]:
    """
    Expected shape (Steam Web API GetOwnedGames):
      {"response":{"games":[{"appid":..., "playtime_forever":..., "playtime_2weeks":...}, ...]}}
    """
    resp = payload.get("response") or {}
    games = resp.get("games") or []
    out: List[OwnedGame] = []
    for g in games:
        out.append(
            OwnedGame(
                appid=int(g.get("appid")),
                playtime_forever_min=int(g.get("playtime_forever") or 0),
                playtime_2weeks_min=int(g.get("playtime_2weeks") or 0),
            )
        )
    return out


def parse_game_meta_from_store_appdetails(appid: int, payload: Dict[str, Any]) -> Optional[GameMeta]:
    """
    Store appdetails is typically keyed by appid: { "<appid>": {"success": true, "data": {...}} }
    Returns None if not successful / no data.
    """
    entry = payload.get(str(appid)) or {}
    if not entry.get("success"):
        return None
    data = entry.get("data") or {}

    name = data.get("name") or ""
    genres = tuple((x.get("description") or "").strip() for x in (data.get("genres") or []) if x.get("description"))
    categories = tuple((x.get("description") or "").strip() for x in (data.get("categories") or []) if x.get("description"))

    is_free = data.get("is_free")
    release_date = None
    rd = data.get("release_date") or {}
    if isinstance(rd, dict):
        release_date = rd.get("date")

    return GameMeta(
        appid=appid,
        name=name,
        genres=genres,
        categories=categories,
        tags=(),  # not from appdetails by default
        is_free=bool(is_free) if isinstance(is_free, bool) else None,
        release_date=release_date if isinstance(release_date, str) else None,
    )
