import sys

sys.path.append("/opt/airflow/operators")
from datetime import datetime, timedelta

import copy_to_postgres
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow_dbt.operators.dbt_operator import DbtRunOperator, DbtTestOperator

try:
    from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False


def task_fail_slack_alert(context):
    """Send Slack alert when a task fails. Uses Airflow connection id 'slack' (slackwebhook, Password = webhook URL)."""
    if not SLACK_AVAILABLE:
        return None
    ti = context.get("task_instance")
    exec_date = context.get("logical_date") or context.get("execution_date")
    slack_msg = (
        ":x: Task Failed\n"
        "*Task*: {task}\n"
        "*Dag*: {dag}\n"
        "*Execution Time*: {exec_date}\n"
        "*Log URL*: {log_url}"
    ).format(
        task=ti.task_id,
        dag=ti.dag_id,
        exec_date=exec_date,
        log_url=ti.log_url,
    )
    try:
        hook = SlackWebhookHook(slack_webhook_conn_id="slack")
        hook.send(text=slack_msg)
    except Exception as e:
        # Log only; don't raise or the failure callback itself fails and you get no alert
        print(f"Slack alert failed: {e}")
    return None


args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2022, 12, 21),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "on_success_callback": None,
    "on_failure_callback": task_fail_slack_alert,
}


def should_send_spotify_weekly_summary(**context):
    """Only send the weekly Spotify summary on Monday at 9am Central Time (scheduled or manual)."""
    dt = context.get("data_interval_end") or context.get("logical_date") or context.get("execution_date")
    if not dt:
        return False
    try:
        import pendulum
        central = pendulum.timezone("America/Chicago")
        if hasattr(dt, "in_timezone"):
            ct = dt.in_timezone(central)
        else:
            ct = pendulum.instance(dt).in_timezone(central)
        return ct.weekday() == 0 and ct.hour == 9
    except Exception:
        return False


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

    postgres_port = Variable.get("POSTGRES_HOST_PORT", default_var="5433")

    check_weekly_summary = ShortCircuitOperator(
        task_id="check_weekly_summary_window",
        python_callable=should_send_spotify_weekly_summary,
    )

    spotify_slack_channel = Variable.get("SPOTIFY_SLACK_CHANNEL", default_var="#general")

    weekly_summary = BashOperator(
        task_id="weekly_summary_to_slack",
        bash_command="cd /opt/spotify && python -m slack_bot.weekly_summary",
        env={
            "PYTHONPATH": "/opt/spotify",
            "SPOTIFY_PG_HOST": "host.docker.internal",
            "SPOTIFY_PG_PORT": postgres_port,
            "PG_USER": "airflow",
            "PG_PASSWORD": "airflow",
            "PG_DATABASE": "airflow",
            "SPOTIFY_SLACK_CHANNEL": spotify_slack_channel,
        },
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
        >> check_weekly_summary
        >> weekly_summary
        >> end_task
    )
