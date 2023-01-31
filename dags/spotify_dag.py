import sys

sys.path.append("/opt/airflow/operators")
from datetime import datetime, timedelta

import copy_to_postgres
from airflow import DAG
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow_dbt.operators.dbt_operator import DbtRunOperator, DbtTestOperator


def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection("slack").password
    slack_msg = """
        :x: Task Failed
        *Task*: {task}
        *Dag*: {dag}
        *Execution Time*: {exec_date}
        *Log URL*: {log_url}
        """.format(
        task=context.get("task_instance").task_id,
        dag=context.get("task_instance").dag_id,
        ti=context.get("task_instance"),
        exec_date=context.get("execution_date"),
        log_url=context.get("task_instance").log_url,
    )
    failed_alert = SlackWebhookOperator(
        task_id="slack_alert",
        http_conn_id="slack",
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username="airflow",
        dag=dag,
    )
    return failed_alert.execute(context=context)


args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2022, 12, 21),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "on_success_callback": None,
    "on_failure_callback": task_fail_slack_alert,
}

with DAG(
    dag_id="spotify_dag",
    schedule_interval="0 0-6,14-23 * * *",
    max_active_runs=1,
    catchup=False,
    default_args=args,
) as dag:

    TASK_DEFS = {
        "songs": {"path": "sql/create_spotify_songs.sql"},
        "genres": {"path": "sql/create_spotify_genres.sql"},
    }

    create_tables_if_not_exists = {
        k: PostgresOperator(
            task_id=f"create_if_not_exists_spotify_{k}_table",
            postgres_conn_id="postgres_localhost",
            sql=v["path"],
        )
        for k, v in TASK_DEFS.items()
    }

    extract_spotify_data = BashOperator(
        task_id="extract_spotify_data",
        bash_command="python3 /opt/airflow/operators/main.py",
    )

    load_tables = {
        k: PythonOperator(
            task_id=f"load_{k}",
            python_callable=copy_to_postgres.copy_expert_csv,
            op_kwargs={"file": f"spotify_{k}"},
        )
        for k, v in TASK_DEFS.items()
    }

    dbt_run = DbtRunOperator(
        task_id="dbt_run",
        dir="/opt/airflow/operators/dbt/",
        profiles_dir="/opt/airflow/operators/dbt/",
    )

    dbt_test = DbtTestOperator(
        task_id="dbt_test",
        dir="/opt/airflow/operators/dbt/",
        profiles_dir="/opt/airflow/operators/dbt/",
    )

    continue_task = DummyOperator(task_id="continue")

    start_task = DummyOperator(task_id="start")

    end_task = DummyOperator(task_id="end")

    (
        start_task
        >> extract_spotify_data
        >> list(create_tables_if_not_exists.values())
        >> continue_task
        >> list(load_tables.values())
        >> dbt_run
        >> dbt_test
        >> end_task
    )
