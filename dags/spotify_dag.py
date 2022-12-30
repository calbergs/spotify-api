from airflow import DAG
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow_dbt.operators.dbt_operator import (
    DbtSeedOperator,
    DbtSnapshotOperator,
    DbtRunOperator,
    DbtTestOperator
)
from datetime import timedelta, datetime

slack_conn_id = 'slack'

def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(slack_conn_id).password
    slack_msg = """
        :x: Task Failed
        *Task*: {task}
        *Dag*: {dag}
        *Execution Time*: {exec_date}
        *Log URL*: {log_url}
        """.format(
        task=context.get('task_instance').task_id,
        dag=context.get('task_instance').dag_id,
        ti=context.get('task_instance'),
        exec_date=context.get('execution_date'),
        log_url=context.get('task_instance').log_url,
    )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow',
        dag=dag
    )
    return failed_alert.execute(context=context)

def task_success_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(slack_conn_id).password
    slack_msg = """
        :white_check_mark: Task Succeeded
        *Task*: {task}
        *Dag*: {dag}
        *Execution Time*: {exec_date}
        *Log URL*: {log_url}
        """.format(
        task=context.get('task_instance').task_id,
        dag=context.get('task_instance').dag_id,
        ti=context.get('task_instance'),
        exec_date=context.get('execution_date'),
        log_url=context.get('task_instance').log_url,
    )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow',
        dag=dag
    )
    return failed_alert.execute(context=context)

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 12, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'on_success_callback': None,
    'on_failure_callback': task_fail_slack_alert
}

dag = DAG(
    dag_id='spotify_dag',
    schedule_interval='*/30 0-6,14-23 * * *',
    max_active_runs=1,
    catchup=False,
    default_args=args
)

extract_spotify_data = BashOperator(
    task_id='extract_spotify_data',
    bash_command='python3 /opt/airflow/operators/main.py',
    dag=dag
)

create_if_not_exists_spotify_genres_table = PostgresOperator(
    task_id="create_if_not_exists_spotify_genres_table",
    postgres_conn_id="postgres_localhost",
    sql="sql/create_spotify_genres.sql",
    dag=dag
)

create_if_not_exists_spotify_songs_table = PostgresOperator(
    task_id="create_if_not_exists_spotify_songs_table",
    postgres_conn_id="postgres_localhost",
    sql="sql/create_spotify_songs.sql",
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
    dag=dag
)

load_songs = PythonOperator(
    task_id="load_songs",
    python_callable=copy_expert_songs_csv,
    dag=dag
)

dbt_run = DbtRunOperator(
    task_id="dbt_run",
    dir="/opt/airflow/operators/dbt/",
    profiles_dir="/opt/airflow/operators/dbt/",
    dag=dag
)

dbt_test = DbtTestOperator(
    task_id="dbt_test",
    dir="/opt/airflow/operators/dbt/",
    profiles_dir="/opt/airflow/operators/dbt/",
    dag=dag
)

start_task = DummyOperator(
    task_id="start",
    dag=dag
)

end_task = DummyOperator(
    task_id="end",
    dag=dag
)

start_task >> [create_if_not_exists_spotify_genres_table, create_if_not_exists_spotify_songs_table] >> extract_spotify_data >> [load_genres, load_songs] >> dbt_run >> dbt_test >> end_task