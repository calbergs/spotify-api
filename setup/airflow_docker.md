# Build Docker Containers for Airflow

- Check if you have enough memory (need at least 4GB)
  ```
  docker run --rm "debian:bullseye-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'
  ```
- Fetch docker-compose.yaml
  ```
  curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.5.0/docker-compose.yaml'
  ```
- Make the directories and set the user
  ```
  mkdir -p ./dags ./logs ./plugins
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  ```
- Initialize the database
  ```
  docker compose up airflow-init
  ```
- Start all services
  ```
  docker-compose up
  ```
- Airflow is now available on http://localhost:8080/home
- Depending on where your dbt project is installed a new volume will need to be added in the docker-compose.yaml file in order for dbt to run in Airflow
  ```
  - ./operators/dbt:/opt/airflow/operators/dbt
  ```