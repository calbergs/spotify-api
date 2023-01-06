# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history from the Spotify API using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline calls the Spotify API every 30 minutes from hours 0-6 and 14-23 UTC (basically whenever I'm awake) to extract a user's song listening history, load the responses into a database, apply transformations and visualize the metrics in a dashboard. Since the dataset is small and this doesn't need to be running 24/7 this is all built using open source tools and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Data Warehouse - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify drawio](https://user-images.githubusercontent.com/60953643/210160621-c7213f9d-2b9f-42ad-b8b1-697403bf6497.svg)

#### Process
1. main.py script is triggered every 30 minutes via Airflow to refresh the access token,  make a connection to the Postgres database to check for the latest listened time, and call the Spotify API to retrieve the most recently played songs and corresponding genres.
2. Responses are saved as CSV files in 'YYYY-MM-DD.csv' format. These files will keep getting appended with the most recently played songs for the respective date.
3. Data is copied into the Postgres Database into the respective tables, spotify_songs and spotify_genres.
4. dbt run task is triggered to run transformations on top of the staging data to produce analytical and reporting tables/views.
5. dbt test will run after successful completion of dbt run to ensure all tests pass.
6. Tables/views are fed into Metabase and the metrics are visualized through a dashboard.

Throughout this entire process if any Airflow task fails an automatic Slack alert will be sent to a custom Slack channel that was created.

#### DAG
<img width="1170" alt="Screenshot 2023-01-05 at 9 32 42 PM" src="https://user-images.githubusercontent.com/60953643/210924715-f3e75b77-30d9-4bb3-81fa-fe2459355c3b.png">

#### Sample Slack Alert
<img width="696" alt="Screenshot 2023-01-05 at 9 33 09 PM" src="https://user-images.githubusercontent.com/60953643/210924729-6c732f9e-e1de-4cad-9052-9a5db239007d.png">


## Dashboard
<img width="1728" alt="Screenshot 2023-01-05 at 4 55 48 PM" src="https://user-images.githubusercontent.com/60953643/210896053-c92c565d-c46d-427f-8eac-5acebdcfe253.png">
<img width="1728" alt="Screenshot 2023-01-05 at 4 56 03 PM" src="https://user-images.githubusercontent.com/60953643/210896070-3ccb3f78-38d0-4111-96fc-6b1a47986ec1.png">
<img width="1728" alt="Screenshot 2023-01-05 at 4 56 19 PM" src="https://user-images.githubusercontent.com/60953643/210896074-764892ad-c515-47dc-b48b-c7b79d4656c1.png">
<img width="1728" alt="Screenshot 2023-01-05 at 4 56 34 PM" src="https://user-images.githubusercontent.com/60953643/210896088-39449b09-ea0e-4ca6-8169-3077c2d5a50d.png">


## Setup

- [Get Spotify API Access](https://github.com/calbergs/spotify-api/blob/master/setup/spotify_api_access.md)
- [Build Docker Containers for Airflow](https://github.com/calbergs/spotify-api/blob/master/setup/airflow_docker.md)
- [Set Up Airflow Connection to Postgres](https://github.com/calbergs/spotify-api/blob/master/setup/postgres.md)
- [Install dbt Core](https://github.com/calbergs/spotify-api/blob/master/setup/dbt.md)
- [Enable Airflow Slack Notifications](https://github.com/calbergs/spotify-api/blob/master/setup/slack_notifications.md)
- [Install Metabase](https://github.com/calbergs/spotify-api/blob/master/setup/metabase.md)

## Further Improvements (Work In Progress)

- Create a BranchPythonOperator to first check if the API payload is empty. If empty then proceed directly to the end task else continue to the downstream tasks.
- Implement data quality checks to catch any potential errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover further insights once Spotify sends back my entire songs listening history from 10+ years back to the current date (this needed to be requested separately since the current API only allows requesting the 50 most recently played tracks)
- If and whenever Spotify allows requesting historical data implement backfill capability
