#!/usr/bin/env python3
"""
One-off script: create a private Spotify playlist for each year, containing
every unique track played that year (per analytical.fct_listening_activity),
ordered by when it was first played that year.

Run once from this directory:
    python3 create_year_playlists.py

Requires the account's Spotify token to include the playlist-modify-private
scope (see operators/reauth.py -- SCOPE must include it, and you must have
re-authorized after adding it).
"""
import sys
import time

import psycopg2
import requests
from psycopg2.extras import RealDictCursor

from refresh import RefreshToken
from spotify_secrets import host, port, dbname, pg_user, pg_password

YEARS = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2022]

API_BASE = "https://api.spotify.com/v1"
BATCH_SIZE = 100  # Spotify's max URIs per add-tracks call


def get_access_token() -> str:
    return RefreshToken().refresh()


def get_current_user_id(access_token: str) -> str:
    """Fetch the authenticated account's actual Spotify user ID live rather
    than trusting spotify_secrets.py's spotify_user_id, which was stale
    (still an old username) when this script was first written."""
    resp = requests.get(f"{API_BASE}/me", headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.json()["id"]


def get_unique_tracks_for_year(conn, year: int):
    """Unique track_ids played in `year`, ordered by first play that year."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT track_id, MIN(played_at) AS first_played_at,
                   MAX(song_name) AS song_name, MAX(artist_name) AS artist_name
            FROM analytical.fct_listening_activity
            WHERE played_at_year = %s AND track_id IS NOT NULL
            GROUP BY track_id
            ORDER BY first_played_at
            """,
            (year,),
        )
        return cur.fetchall()


def _request_with_retry(method: str, url: str, headers: dict, **kwargs) -> requests.Response:
    """Spotify's API rate-limits with 429 + Retry-After; honor it rather
    than failing a batch job partway through."""
    while True:
        resp = requests.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", "1"))
            print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        return resp


def create_playlist(access_token: str, user_id: str, name: str) -> str:
    resp = _request_with_retry(
        "POST",
        f"{API_BASE}/users/{user_id}/playlists",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={
            "name": name,
            "public": False,
            "description": f"Every unique song played in {name}, generated from listening history.",
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def add_tracks(access_token: str, playlist_id: str, track_ids: list) -> None:
    for i in range(0, len(track_ids), BATCH_SIZE):
        batch = track_ids[i : i + BATCH_SIZE]
        uris = [f"spotify:track:{t}" for t in batch]
        resp = _request_with_retry(
            "POST",
            f"{API_BASE}/playlists/{playlist_id}/tracks",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={"uris": uris},
        )
        if resp.status_code >= 400:
            print(f"  batch {i}-{i+len(batch)}: {resp.status_code} {resp.text[:500]}", file=sys.stderr)
        resp.raise_for_status()


def main():
    access_token = get_access_token()
    user_id = get_current_user_id(access_token)
    print(f"Creating playlists for Spotify user: {user_id}")
    conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=pg_user, password=pg_password)

    try:
        for year in YEARS:
            tracks = get_unique_tracks_for_year(conn, year)
            if not tracks:
                print(f"{year}: no tracks, skipping")
                continue

            playlist_id = create_playlist(access_token, user_id, str(year))
            track_ids = [t["track_id"] for t in tracks]
            add_tracks(access_token, playlist_id, track_ids)
            print(f"{year}: created playlist {playlist_id} with {len(track_ids)} unique tracks")
    finally:
        conn.close()

    print("Done.")


if __name__ == "__main__":
    main()
