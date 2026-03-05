import os
import psycopg2

# Postgres connection info.
# Defaults match the shared Airflow Postgres, but can be overridden via env vars
# when running from the host (e.g. host=localhost).
POSTGRES_CONFIG = {
    "host": os.getenv("SPOTIFY_PG_HOST", "host.docker.internal"),
    "port": int(os.getenv("SPOTIFY_PG_PORT", "5432")),
    "user": os.getenv("SPOTIFY_PG_USER", "airflow"),
    "password": os.getenv("SPOTIFY_PG_PASSWORD", "airflow"),
    "dbname": os.getenv("SPOTIFY_DB_NAME", "airflow"),
}

def copy_csv_to_postgres(table_name, csv_path):
    """
    Load a single CSV into the target table, de-duplicating on primary key.

    We COPY into a temp table first, then INSERT .. ON CONFLICT DO NOTHING
    into the real table so re-running the backfill is idempotent.
    """
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    # Temp table to stage raw CSV rows.
    # We load the CSV's 12 columns, but keep the last one as text so we can ignore it.
    cur.execute(
        f"""
        CREATE TEMP TABLE tmp_{table_name} (
            played_at_utc timestamp,
            played_date_utc date,
            song_name text,
            artist_name text,
            song_duration_ms_raw text,
            song_link text,
            album_art_link text,
            album_name text,
            album_id text,
            artist_id text,
            track_id text,
            last_updated_raw text
        )
        """
    )

    # Older CSVs may contain non-timestamp values in the last column.
    # We COPY all CSV columns into the temp table, then drop the last one
    # when inserting into the real table so last_updated_datetime_utc remains NULL.
    with open(csv_path, "r") as f:
        cur.copy_expert(
            f"""
            COPY tmp_{table_name} (
                played_at_utc,
                played_date_utc,
                song_name,
                artist_name,
                song_duration_ms_raw,
                song_link,
                album_art_link,
                album_name,
                album_id,
                artist_id,
                track_id,
                last_updated_raw
            )
            FROM STDIN WITH CSV HEADER DELIMITER ','
            """,
            f,
        )

    # Insert into the real table, skipping any existing primary keys
    cur.execute(
        f"""
        INSERT INTO {table_name} (
            played_at_utc,
            played_date_utc,
            song_name,
            artist_name,
            song_duration_ms,
            song_link,
            album_art_link,
            album_name,
            album_id,
            artist_id,
            track_id,
            last_updated_datetime_utc
        )
        SELECT
            played_at_utc,
            played_date_utc,
            song_name,
            artist_name,
            -- Cast raw duration (which may be a float string like '161584.0') to integer milliseconds
            NULLIF(song_duration_ms_raw, '')::numeric::integer AS song_duration_ms,
            song_link,
            album_art_link,
            album_name,
            album_id,
            artist_id,
            track_id,
            NULL::timestamp
        FROM tmp_{table_name}
        ON CONFLICT (played_at_utc) DO NOTHING
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Copied {csv_path} into {table_name} (duplicates skipped)")

def backfill_csv_folder(base_folder, table_name):
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                copy_csv_to_postgres(table_name, full_path)

if __name__ == "__main__":
    # Path to your folder containing the CSV files
    spotify_songs_folder = "/Users/albertcheng/Documents/GitHub/spotify/dags/spotify_data/spotify_songs"
    backfill_csv_folder(spotify_songs_folder, "spotify_songs")
