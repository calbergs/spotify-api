# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline will call the Spotify API every 30 minutes to retrieve a user's song listening history, load the responses into a database, apply transformation and then visualized in a dashboard.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Data Warehouse - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify_architecture](https://user-images.githubusercontent.com/60953643/210158660-a3e0b63b-0e5b-49ff-bdac-298ebcdd0a56.png)
