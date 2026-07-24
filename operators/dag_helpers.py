"""Pure logic used by spotify_dag.py, split out into a plain module so it's
unit-testable without an Airflow install (importing the DAG file itself
pulls in `airflow`, which isn't available outside the Airflow containers)."""
from datetime import datetime

SPOTIFY_SONGS_CSV_PATH = "/opt/airflow/dags/spotify/spotify_data/spotify_songs.csv"


def songs_csv_has_new_rows(csv_path: str = SPOTIFY_SONGS_CSV_PATH) -> bool:
    """True if the CSV has at least one data row beyond the header.
    extract_spotify_data always writes a header row even with zero new
    plays (pandas' to_csv on an empty DataFrame), so this -- not the
    task's exit code, which is 0 either way -- is the reliable "was the
    payload empty" signal."""
    try:
        with open(csv_path) as f:
            next(f)  # header row
            return next(f, None) is not None
    except (FileNotFoundError, StopIteration):
        return False


def is_weekly_summary_window(dt: datetime) -> bool:
    """True only for Monday at 9am (in whatever timezone `dt` is already
    expressed in -- the caller is responsible for converting to Central)."""
    return dt.weekday() == 0 and dt.hour == 9
