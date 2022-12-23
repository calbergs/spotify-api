from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
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
    schedule_interval='0 * * * *',
    max_active_runs=1,
    catchup=False,
    default_args=args
)

extract_data = BashOperator(
    task_id='make_api_requests_and_download_responses',
    bash_command='python3 /opt/airflow/plugins/main.py',
    dag=dag
)

start_task = DummyOperator(task_id="start", dag=dag)
end_task = DummyOperator(task_id="end", dag=dag)

start_task >> extract_data >> end_task