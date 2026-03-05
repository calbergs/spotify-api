"""
Postgres queries for Spotify listening data (spotify_songs, spotify_genres).
"""
import json
from contextlib import contextmanager
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import get_pg_config

SONGS_TABLE = "spotify_songs"
GENRES_TABLE = "spotify_genres"


@contextmanager
def get_conn():
    cfg = get_pg_config()
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
    )
    try:
        yield conn
    finally:
        conn.close()


def _run_query(sql: str, params: tuple = ()):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def date_range_available():
    """Earliest and latest played_at_utc in spotify_songs."""
    sql = f"SELECT MIN(played_at_utc) AS min_date, MAX(played_at_utc) AS max_date FROM {SONGS_TABLE}"
    rows = _run_query(sql)
    return dict(rows[0]) if rows else {}


def top_artists(start_date: str, end_date: str, limit: int = 20):
    """Most played artists by play count in the date range."""
    sql = f"""
        SELECT artist_name, artist_id,
               COUNT(*) AS play_count,
               COUNT(DISTINCT played_date_utc) AS days_played
        FROM {SONGS_TABLE}
        WHERE played_date_utc BETWEEN %s AND %s
        GROUP BY artist_name, artist_id
        ORDER BY play_count DESC
        LIMIT %s
    """
    rows = _run_query(sql, (start_date, end_date, limit))
    return [dict(r) for r in rows]


def top_songs(start_date: str, end_date: str, limit: int = 20):
    """Most played tracks (song_name + artist) by play count."""
    sql = f"""
        SELECT song_name, artist_name, track_id,
               COUNT(*) AS play_count
        FROM {SONGS_TABLE}
        WHERE played_date_utc BETWEEN %s AND %s
        GROUP BY song_name, artist_name, track_id
        ORDER BY play_count DESC
        LIMIT %s
    """
    rows = _run_query(sql, (start_date, end_date, limit))
    return [dict(r) for r in rows]


def top_genres(start_date: str, end_date: str, limit: int = 20):
    """Most listened genres in the date range (via artist genre from spotify_genres)."""
    sql = f"""
        SELECT g.artist_genre AS genre,
               COUNT(*) AS play_count
        FROM {SONGS_TABLE} s
        JOIN {GENRES_TABLE} g ON s.artist_id = g.artist_id
        WHERE s.played_date_utc BETWEEN %s AND %s
          AND g.artist_genre IS NOT NULL AND g.artist_genre != ''
        GROUP BY g.artist_genre
        ORDER BY play_count DESC
        LIMIT %s
    """
    rows = _run_query(sql, (start_date, end_date, limit))
    return [dict(r) for r in rows]


def listening_activity_by_date(start_date: str, end_date: str):
    """Plays per day in the date range."""
    sql = f"""
        SELECT played_date_utc AS date, COUNT(*) AS play_count
        FROM {SONGS_TABLE}
        WHERE played_date_utc BETWEEN %s AND %s
        GROUP BY played_date_utc
        ORDER BY played_date_utc
    """
    rows = _run_query(sql, (start_date, end_date))
    return [dict(r) for r in rows]


def recent_tracks(start_date: str, end_date: str, limit: int = 20, artist_filter: Optional[str] = None):
    """Recent listens with played_at, song, artist."""
    sql = f"""
        SELECT played_at_utc, played_date_utc, song_name, artist_name
        FROM {SONGS_TABLE}
        WHERE played_date_utc BETWEEN %s AND %s
    """
    params = [start_date, end_date]
    if artist_filter:
        sql += " AND artist_name ILIKE %s"
        params.append(f"%{artist_filter}%")
    sql += " ORDER BY played_at_utc DESC LIMIT %s"
    params.append(limit)
    rows = _run_query(sql, tuple(params))
    return [dict(r) for r in rows]


def artist_genres(artist_name_or_id: str):
    """Look up genre(s) for an artist by name or artist_id."""
    sql = f"""
        SELECT artist_id, artist_name, artist_genre
        FROM {GENRES_TABLE}
        WHERE artist_name ILIKE %s OR artist_id = %s
    """
    rows = _run_query(sql, (f"%{artist_name_or_id}%", artist_name_or_id))
    return [dict(r) for r in rows]


def total_listens(start_date: str, end_date: str):
    """Total play count and distinct days in the date range."""
    sql = f"""
        SELECT COUNT(*) AS total_plays,
               COUNT(DISTINCT played_date_utc) AS days_listened
        FROM {SONGS_TABLE}
        WHERE played_date_utc BETWEEN %s AND %s
    """
    rows = _run_query(sql, (start_date, end_date))
    return dict(rows[0]) if rows else {"total_plays": 0, "days_listened": 0}


def run_tool(name: str, **kwargs) -> str:
    """Execute a named query tool and return JSON string for Claude."""
    try:
        if name == "date_range_available":
            out = date_range_available()
        elif name == "top_artists":
            out = top_artists(
                kwargs["start_date"],
                kwargs["end_date"],
                kwargs.get("limit", 20),
            )
        elif name == "top_songs":
            out = top_songs(
                kwargs["start_date"],
                kwargs["end_date"],
                kwargs.get("limit", 20),
            )
        elif name == "top_genres":
            out = top_genres(
                kwargs["start_date"],
                kwargs["end_date"],
                kwargs.get("limit", 20),
            )
        elif name == "listening_activity_by_date":
            out = listening_activity_by_date(kwargs["start_date"], kwargs["end_date"])
        elif name == "recent_tracks":
            out = recent_tracks(
                kwargs["start_date"],
                kwargs["end_date"],
                kwargs.get("limit", 20),
                kwargs.get("artist_filter"),
            )
        elif name == "artist_genres":
            out = artist_genres(kwargs["artist_name_or_id"])
        elif name == "total_listens":
            out = total_listens(kwargs["start_date"], kwargs["end_date"])
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
