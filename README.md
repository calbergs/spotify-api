# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history from the Spotify API using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline calls the Spotify API every hour from hours 0-6 and 14-23 UTC (basically whenever I'm awake) to extract a user's song listening history, load the responses into a database, apply transformations and visualize the metrics in a dashboard. Since the dataset is small and this doesn't need to be running 24/7 this is all built using open source tools and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Database - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify drawio](https://user-images.githubusercontent.com/60953643/210160621-c7213f9d-2b9f-42ad-b8b1-697403bf6497.svg)

#### Data Flow
1. main.py script is triggered every hour (from hours 0-6 and 14-23 UTC) via Airflow to refresh the access token,  make a connection to the Postgres database to check for the latest listened time, and call the Spotify API to retrieve the most recently played songs and corresponding genres.
2. Responses are saved as CSV files in 'YYYY-MM-DD.csv' format. These are saved on the local file system and act as our replayable source since the Spotify API only allows requesting the 50 most recently played songs and not any historical data. These files will keep getting appended with the most recently played songs for the respective date.
3. Data is copied into the Postgres Database into the respective tables, spotify_songs and spotify_genres.
4. dbt run task is triggered to run transformations on top of the staging data to produce analytical and reporting tables/views.
5. dbt test will run after successful completion of dbt run to ensure all tests pass.
6. Tables/views are fed into Metabase and the metrics are visualized through a dashboard.
7. Slack subscription is set up in Metabase to send a weekly summary every Monday.

Throughout this entire process if any Airflow task fails an automatic Slack alert will be sent to a custom Slack channel that was created.

#### DAG
<img width="1170" alt="Screenshot 2023-01-05 at 9 32 42 PM" src="https://user-images.githubusercontent.com/60953643/210924715-f3e75b77-30d9-4bb3-81fa-fe2459355c3b.png">

#### Sample Slack Alert
<img width="696" alt="Screenshot 2023-01-05 at 9 33 09 PM" src="https://user-images.githubusercontent.com/60953643/210924729-6c732f9e-e1de-4cad-9052-9a5db239007d.png">


## Dashboard
<img width="1472" alt="Screenshot 2023-01-31 at 12 02 56 PM" src="https://user-images.githubusercontent.com/60953643/215845338-5e2f7677-8c0b-4e02-af6f-9742dbdb41e7.png">
<img width="1656" alt="Screenshot 2023-01-31 at 1 20 51 PM" src="https://user-images.githubusercontent.com/60953643/215861379-2b0d8498-70ca-4fde-936c-9da3e11ad19c.png">
<img width="1376" alt="Screenshot 2023-01-24 at 10 18 42 PM" src="https://user-images.githubusercontent.com/60953643/215845410-f1a9753f-39aa-4f90-b769-a11104c01962.png">
<img width="1655" alt="Screenshot 2023-01-31 at 12 03 24 PM" src="https://user-images.githubusercontent.com/60953643/215845428-7831d936-bccf-46ea-9848-c527da89a5e9.png">
<img width="1655" alt="Screenshot 2023-01-31 at 12 03 36 PM" src="https://user-images.githubusercontent.com/60953643/215845447-50e5af73-3a41-432f-a5a3-40932b1f153b.png">


## Setup

1. [Get Spotify API Access](https://github.com/calbergs/spotify-api/blob/master/setup/spotify_api_access.md)
2. [Build Docker Containers for Airflow](https://github.com/calbergs/spotify-api/blob/master/setup/airflow_docker.md)
3. [Set Up Airflow Connection to Postgres](https://github.com/calbergs/spotify-api/blob/master/setup/postgres.md)
4. [Install dbt Core](https://github.com/calbergs/spotify-api/blob/master/setup/dbt.md)
5. [Enable Airflow Slack Notifications](https://github.com/calbergs/spotify-api/blob/master/setup/slack_notifications.md)
6. [Install Metabase](https://github.com/calbergs/spotify-api/blob/master/setup/metabase.md)

## Further Improvements (Work In Progress)

- Create a BranchPythonOperator to first check if the API payload is empty. If empty then proceed directly to the end task else continue to the downstream tasks.
- Implement data quality checks to catch any potential errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover further insights once Spotify sends back my entire songs listening history from 10+ years back to the current date (this needed to be requested separately since the current API only allows requesting the 50 most recently played tracks)
- If and whenever Spotify allows requesting historical data implement backfill capability
