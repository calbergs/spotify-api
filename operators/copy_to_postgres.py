from airflow.hooks.postgres_hook import PostgresHook

def copy_expert_csv(file):
    hook = PostgresHook('postgres_localhost')
    with hook.get_conn() as connection:
        hook.copy_expert(f"""
        COPY {file} FROM stdin WITH CSV HEADER DELIMITER as ','
        """,
        f'/opt/airflow/dags/spotify_data/{file}.csv'
        )
        connection.commit()