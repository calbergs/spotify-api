# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline will call the Spotify API every 30 minutes to retrieve a user's song listening history, load the responses into a database, apply transformation and then visualize the metrics in a dashboard. Since the dataset and listening frequency is small this is all built and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Data Warehouse - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify_architecture](https://user-images.githubusercontent.com/60953643/210158660-a3e0b63b-0e5b-49ff-bdac-298ebcdd0a56.png)

## Dashboard
<img width="1726" alt="Screenshot 2022-12-31 at 7 41 09 PM" src="https://user-images.githubusercontent.com/60953643/210158921-0024a44f-2273-40dd-b974-cede87ef5d69.png">
<img width="1723" alt="Screenshot 2022-12-31 at 7 41 24 PM" src="https://user-images.githubusercontent.com/60953643/210158923-6050b65d-9955-448d-ac52-7556e0900c7d.png">
<img width="1721" alt="Screenshot 2022-12-31 at 7 41 36 PM" src="https://user-images.githubusercontent.com/60953643/210158927-c1f5e65a-e391-4e25-b6cf-7b23362f4439.png">
<img width="1725" alt="Screenshot 2022-12-31 at 7 41 44 PM" src="https://user-images.githubusercontent.com/60953643/210158928-6fc80f5d-8942-462f-846a-e380820aebfd.png">

## Setup



## Further Improvements (Work In Progress)

- Implement data quality checks to catch any errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover more insights
