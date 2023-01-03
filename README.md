# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history from the Spotify API using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline calls the Spotify API every 30 minutes from hours 0-6 and 14-23 UTC (basically whenever I'm awake) to extract a user's song listening history, load the responses into a database, apply transformations and visualize the metrics in a dashboard. Since the dataset is small and this doesn't need to be running 24/7 this is all built using open source tools and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Database - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify drawio](https://user-images.githubusercontent.com/60953643/210160621-c7213f9d-2b9f-42ad-b8b1-697403bf6497.svg)

- main.py script is triggered every 30 minutes via Airflow to call the Spotify API and retrieve the most recently listened songs. The script will first make a connection to the Postgres database to check for the latest listened time. This will then be passed as a parameter when we call the Spotify API to only pull back data from after our last listened track time. The script will pull back recently listened songs as well as the corresponding genres
- The responses are then saved as CSV files in 'YYYY-MM-DD.csv' format. This file we keep getting appended with the most recently played songs for the respective date. The folder structure is partitioned by year and month (YYYY/MM/YYYY-MM-DD.csv)
- The incremental data is then copied into the Postgres Database into the respective tables, spotify_songs and spotify_genres.
- dbt run task is then triggered to run transformations on top of our staging data to produce analytical and reporting tables/views.
- dbt test will run after successful completion of dbt run to ensure all tests pass.
- The tables/views are then fed into Metabase and the metrics are visualized through a dashboard.
- Throughout this entire process if any Airflow task fails an automatic Slack alert will be sent to a custom Slack channel that was created

## Dashboard
<img width="1726" alt="Screenshot 2022-12-31 at 7 41 09 PM" src="https://user-images.githubusercontent.com/60953643/210158921-0024a44f-2273-40dd-b974-cede87ef5d69.png">
<img width="1723" alt="Screenshot 2022-12-31 at 7 41 24 PM" src="https://user-images.githubusercontent.com/60953643/210158923-6050b65d-9955-448d-ac52-7556e0900c7d.png">
<img width="1721" alt="Screenshot 2022-12-31 at 7 41 36 PM" src="https://user-images.githubusercontent.com/60953643/210158927-c1f5e65a-e391-4e25-b6cf-7b23362f4439.png">
<img width="1725" alt="Screenshot 2022-12-31 at 7 41 44 PM" src="https://user-images.githubusercontent.com/60953643/210158928-6fc80f5d-8942-462f-846a-e380820aebfd.png">

## Setup

- [Get Spotify API Access](https://github.com/calbergs/spotify-api/blob/master/setup/spotify_api_access.md)
- [Build Docker Containers for Airflow](https://github.com/calbergs/spotify-api/blob/master/setup/airflow_docker.md)
- [Set Up Airflow Connection to Postgres](https://github.com/calbergs/spotify-api/blob/master/setup/postgres.md)
- [Install dbt Core](https://github.com/calbergs/spotify-api/blob/master/setup/dbt.md)
- [Enable Airflow Slack Notifications](https://github.com/calbergs/spotify-api/blob/master/setup/slack_notifications.md)
- [Install Metabase](https://github.com/calbergs/spotify-api/blob/master/setup/metabase.md)

## Further Improvements (Work In Progress)

- Create a BranchPythonOperator to check for any new data from the API first before continuing with the other downstream tasks. If the payload is empty then proceed diretly to the end task.
- Implement data quality checks to catch any potential errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover further insights once Spotify sends back my entire songs listening history from 10+ years back to the current date (this needed to be requested seprately since the current API only allows requesting the 50 most recently played tracks)
- If and whenever Spotify allows requesting historical data implement backfill capability
