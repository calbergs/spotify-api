"""
Copies CSV into Postgres
"""

from airflow.hooks.postgres_hook import PostgresHook


def copy_expert_csv(file, columns=None):
    """`columns`, if given, restricts the COPY to those CSV columns (in that
    order) -- needed for any table with a column the CSV doesn't carry (e.g.
    spotify_songs.source, which defaults to 'spotify' for rows loaded here),
    since COPY without an explicit column list matches purely positionally
    against the table and would otherwise error on a column-count mismatch."""
    hook = PostgresHook("postgres_localhost")
    column_list = f"({', '.join(columns)})" if columns else ""
    with hook.get_conn() as connection:
        hook.copy_expert(
            f"""
        COPY {file} {column_list} FROM stdin WITH CSV HEADER DELIMITER as ','
        """,
            f"/opt/airflow/dags/spotify/spotify_data/{file}.csv",
        )
        connection.commit()
