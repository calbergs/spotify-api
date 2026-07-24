"""
Copies CSV into Postgres
"""

from airflow.hooks.postgres_hook import PostgresHook

# Matches the CSV column order main.py writes (played_at_utc..track_id) plus
# the last_updated_datetime_utc column appended after extraction. Excludes
# spotify_songs.source (added for lastfm-api's historical backfill into this
# same table), which main.py's CSV doesn't carry -- it gets its table
# default ('spotify') instead, since it's left out of the INSERT below too.
SONGS_COLUMNS = [
    "played_at_utc", "played_date_utc", "song_name", "artist_name",
    "song_duration_ms", "song_link", "album_art_link", "album_name",
    "album_id", "artist_id", "track_id", "last_updated_datetime_utc",
]


def copy_expert_csv(file):
    hook = PostgresHook("postgres_localhost")
    csv_path = f"/opt/airflow/dags/spotify/spotify_data/{file}.csv"

    if file == "spotify_songs":
        _upsert_songs_csv(hook, csv_path)
        return

    with hook.get_conn() as connection:
        hook.copy_expert(
            f"""
        COPY {file} FROM stdin WITH CSV HEADER DELIMITER as ','
        """,
            csv_path,
        )
        connection.commit()


def _upsert_songs_csv(hook, csv_path):
    """spotify_songs specifically upserts via a staging table, since COPY
    itself has no ON CONFLICT support -- a retried or overlapping run
    refreshes an already-loaded row's metadata instead of erroring on the
    played_at_utc primary key, matching the refresh-on-rerun behavior every
    other pipeline in this codebase already has. Left out of the UPDATE
    clause: `source`, so this (spotify-only) load never overwrites a
    differently-sourced row (e.g. lastfm-api's historical backfill) --
    not that the two could realistically collide anyway, since this only
    ever loads newly-played tracks going forward.

    genres/saved_tracks don't need this: their own tables get dropped and
    recreated empty right before this runs (see their create_if_not_exists
    SQL), so a plain COPY there can never hit a conflict."""
    conn = hook.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TEMP TABLE tmp_spotify_songs (
                    played_at_utc timestamp,
                    played_date_utc date,
                    song_name text,
                    artist_name text,
                    song_duration_ms integer,
                    song_link text,
                    album_art_link text,
                    album_name text,
                    album_id text,
                    artist_id text,
                    track_id text,
                    last_updated_datetime_utc timestamp
                ) ON COMMIT DROP
            """)
            with open(csv_path) as f:
                cur.copy_expert(
                    "COPY tmp_spotify_songs FROM STDIN WITH CSV HEADER DELIMITER ','",
                    f,
                )
            cur.execute(f"""
                INSERT INTO spotify_songs ({', '.join(SONGS_COLUMNS)})
                SELECT {', '.join(SONGS_COLUMNS)} FROM tmp_spotify_songs
                ON CONFLICT (played_at_utc) DO UPDATE SET
                    song_name = EXCLUDED.song_name,
                    artist_name = EXCLUDED.artist_name,
                    song_duration_ms = EXCLUDED.song_duration_ms,
                    song_link = EXCLUDED.song_link,
                    album_art_link = EXCLUDED.album_art_link,
                    album_name = EXCLUDED.album_name,
                    album_id = EXCLUDED.album_id,
                    artist_id = EXCLUDED.artist_id,
                    track_id = EXCLUDED.track_id,
                    last_updated_datetime_utc = EXCLUDED.last_updated_datetime_utc
            """)
        conn.commit()
    finally:
        conn.close()
