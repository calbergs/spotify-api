from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import timedelta, datetime

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 12, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    dag_id='spotify_dag',
    schedule_interval='*/20 * * * *',
    max_active_runs=1,
    catchup=False,
    default_args=args
)

extract_data = BashOperator(
    task_id='make_api_requests_and_download_responses',
    bash_command='python3 /opt/airflow/plugins/main.py',
    dag=dag
)

drop_spotify_genres_table = PostgresOperator(
    task_id="drop_spotify_genres_table",
    postgres_conn_id="postgres_localhost",
    sql="""
    drop table spotify_genres
    """,
    dag=dag
)

create_or_replace_spotify_genres_table = PostgresOperator(
    task_id="create_or_replace_spotify_genres_table",
    postgres_conn_id="postgres_localhost",
    sql="""
    create table spotify_genres (
        artist_id text,
        artist_name text,
        artist_genre text,
        primary key (artist_id)
    )
    """,
    dag=dag
)

create_or_replace_spotify_songs_table = PostgresOperator(
    task_id="create_or_replace_spotify_songs_table",
    postgres_conn_id="postgres_localhost",
    sql="""
    create table if not exists spotify_songs (
        played_at_utc timestamp,
        played_date_utc date,
        song_name text,
        artist_name text,
        song_duration_ms integer,
        song_link text,
        album_art_link text,
        album_name text,
        album_release_date date,
        album_id text,
        artist_id text,
        last_updated_datetime_utc timestamp,
        primary key (played_at_utc)
    )
    """,
    dag=dag
)

start_task = DummyOperator(task_id="start", dag=dag)
end_task = DummyOperator(task_id="end", dag=dag)

start_task >> drop_spotify_genres_table >> create_or_replace_spotify_genres_table >> extract_data >> end_task
start_task >> create_or_replace_spotify_songs_table >> extract_data >> end_task