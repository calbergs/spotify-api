"""Unit tests for the pure logic spotify_dag.py delegates to -- split out
into operators/dag_helpers.py specifically so it's testable without an
Airflow install (importing the DAG file itself requires `airflow`)."""
from datetime import datetime

from dag_helpers import is_weekly_summary_window, songs_csv_has_new_rows


class TestSongsCsvHasNewRows:
    def test_missing_file_is_treated_as_empty(self, tmp_path):
        missing = tmp_path / "does_not_exist.csv"
        assert songs_csv_has_new_rows(str(missing)) is False

    def test_completely_empty_file_is_treated_as_empty(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")
        assert songs_csv_has_new_rows(str(csv_path)) is False

    def test_header_only_csv_is_empty(self, tmp_path):
        """The real-world shape when extract_spotify_data fetches zero new
        plays -- pandas' to_csv on an empty DataFrame still writes the
        header row."""
        csv_path = tmp_path / "header_only.csv"
        csv_path.write_text("played_at_utc,song_name,artist_name\n")
        assert songs_csv_has_new_rows(str(csv_path)) is False

    def test_csv_with_one_data_row_has_new_rows(self, tmp_path):
        csv_path = tmp_path / "one_row.csv"
        csv_path.write_text("played_at_utc,song_name,artist_name\n2026-01-01T00:00:00Z,Song,Artist\n")
        assert songs_csv_has_new_rows(str(csv_path)) is True

    def test_csv_with_multiple_data_rows_has_new_rows(self, tmp_path):
        csv_path = tmp_path / "many_rows.csv"
        csv_path.write_text(
            "played_at_utc,song_name,artist_name\n"
            "2026-01-01T00:00:00Z,Song A,Artist A\n"
            "2026-01-01T00:05:00Z,Song B,Artist B\n"
        )
        assert songs_csv_has_new_rows(str(csv_path)) is True


class TestIsWeeklySummaryWindow:
    def test_monday_9am_is_the_window(self):
        assert is_weekly_summary_window(datetime(2026, 1, 5, 9, 0)) is True  # a Monday

    def test_monday_but_wrong_hour_is_not_the_window(self):
        assert is_weekly_summary_window(datetime(2026, 1, 5, 10, 0)) is False

    def test_9am_but_wrong_day_is_not_the_window(self):
        assert is_weekly_summary_window(datetime(2026, 1, 6, 9, 0)) is False  # a Tuesday

    def test_neither_day_nor_hour_matches(self):
        assert is_weekly_summary_window(datetime(2026, 1, 7, 14, 30)) is False
