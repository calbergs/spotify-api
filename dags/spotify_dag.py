from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime
from airflow.hooks.postgres_hook import PostgresHook

def failure_email_function(context):
    dag_run = context.get('dag_run')
    msg = "Your Dag has failed"
    subject = f"DAG {dag_run} has failed"
    send_email(to='albert.rich.cheng@gmail.com', subject=subject, html_content=msg)

args = {
    'owner': 'airflow',
    'email': ['albert.rich.cheng@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'on_failure_callback': failure_email_function,
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
    email_on_failure=failure_email_function,
    dag=dag
)

drop_spotify_genres_table = PostgresOperator(
    task_id="drop_spotify_genres_table",
    postgres_conn_id="postgres_localhost",
    sql="""
    drop table spotify_genres
    """,
    email_on_failure=failure_email_function,
    dag=dag
)

create_if_not_exists_spotify_genres_table = PostgresOperator(
    task_id="create_if_not_exists_spotify_genres_table",
    postgres_conn_id="postgres_localhost",
    sql="""
    create table spotify_genres (
        artist_id text,
        artist_name text,
        artist_genre text,
        last_updated_datetime_utc timestamp,
        primary key (artist_id)
    )
    """,
    email_on_failure=failure_email_function,
    dag=dag
)

create_if_not_exists_spotify_songs_table = PostgresOperator(
    task_id="create_if_not_exists_spotify_songs_table",
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
        album_id text,
        artist_id text,
        last_updated_datetime_utc timestamp,
        primary key (played_at_utc)
    )
    """,
    email_on_failure=failure_email_function,
    dag=dag
)

def copy_expert_genres_csv():
    hook = PostgresHook(
        postgres_conn_id='postgres_localhost',
        host='host.docker.internal',
        database='spotify',
        user='airflow',
        password='airflow',
        port=5432
    )
    with hook.get_conn() as connection:
            hook.copy_expert("""COPY spotify_genres FROM stdin WITH CSV HEADER
                        DELIMITER as ',' """,
                        '/opt/airflow/dags/spotify_data/spotify_genres.csv')
            connection.commit()

def copy_expert_songs_csv():
    hook = PostgresHook(
        postgres_conn_id='postgres_localhost',
        host='host.docker.internal',
        database='spotify',
        user='airflow',
        password='airflow',
        port=5432
    )
    with hook.get_conn() as connection:
            hook.copy_expert("""COPY spotify_songs FROM stdin WITH CSV HEADER
                        DELIMITER as ',' """,
                        '/opt/airflow/dags/spotify_data/spotify_songs.csv')
            connection.commit()

load_genres = PythonOperator(
    task_id="load_genres",
    python_callable=copy_expert_genres_csv,
    email_on_failure=failure_email_function,
    dag=dag
)

load_songs = PythonOperator(
    task_id="load_songs",
    python_callable=copy_expert_songs_csv,
    email_on_failure=failure_email_function,
    dag=dag
)

start_task = DummyOperator(task_id="start", dag=dag)
end_task = DummyOperator(task_id="end", dag=dag)

start_task >> drop_spotify_genres_table >> create_if_not_exists_spotify_genres_table >> extract_data >> [load_songs,load_genres] >> end_task
start_task >> create_if_not_exists_spotify_songs_table >> extract_data