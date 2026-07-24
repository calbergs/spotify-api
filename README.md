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

### Metabase
<img width="1472" alt="Screenshot 2023-01-31 at 12 02 56 PM" src="https://user-images.githubusercontent.com/60953643/215845338-5e2f7677-8c0b-4e02-af6f-9742dbdb41e7.png">
<img width="1656" alt="Screenshot 2023-01-31 at 1 20 51 PM" src="https://user-images.githubusercontent.com/60953643/215861379-2b0d8498-70ca-4fde-936c-9da3e11ad19c.png">
<img width="1376" alt="Screenshot 2023-01-24 at 10 18 42 PM" src="https://user-images.githubusercontent.com/60953643/215845410-f1a9753f-39aa-4f90-b769-a11104c01962.png">
<img width="1655" alt="Screenshot 2023-01-31 at 12 03 24 PM" src="https://user-images.githubusercontent.com/60953643/215845428-7831d936-bccf-46ea-9848-c527da89a5e9.png">
<img width="1655" alt="Screenshot 2023-01-31 at 12 03 36 PM" src="https://user-images.githubusercontent.com/60953643/215845447-50e5af73-3a41-432f-a5a3-40932b1f153b.png">

#### As of October 2025 I've migrated to using Apache Superset for visualization

### Superset
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_main.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_top_metrics.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_quarterly_trend.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_listening_history.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_all_time_top_songs.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_all_time_metrics.png">
<img width="1472" alt="image" src="https://raw.githubusercontent.com/calbergs/spotify-api/refs/heads/master/images/superset_heatmap.png">


## Slack Bot

Beyond the scheduled weekly summary, there's an on-demand `/spotify` Slack slash command that lets you ask Claude questions about your listening history in plain English — it queries the `spotify_songs`/`spotify_genres` Postgres tables via Claude tool-calling and answers directly in Slack:

```
/spotify Who are my top artists this month?
/spotify What genres did I listen to last week?
/spotify Recent listens
```

You'll see an immediate "Thinking…" reply, then the real answer once Claude and the DB respond. You can also DM the bot or @mention it in a channel for multi-turn follow-up questions (e.g. ask a question, then "what about last year?") — it keeps the last 20 messages of context per conversation.

Full setup (Slack app, Slash Command, ngrok/ngrok-proxy wiring, optional DM/@mention support) is in [`slack_bot/README.md`](slack_bot/README.md).

## Setup

Current setup (everything runs inside the shared `data-platform` Airflow/Postgres stack):

1. [Get Spotify API Access](https://github.com/calbergs/spotify-api/blob/master/setup/spotify_api_access.md) — includes what to do when your refresh token expires (Spotify tokens now expire after 6 months of inactivity; see `operators/reauth.py`).
2. Use the shared Airflow stack in the `data-platform` repo (see its `README.md` for `docker compose` instructions). This provisions Postgres, runs the DAG (which handles `dbt build` internally — no standalone dbt install needed), and starts Superset.
3. [Enable Airflow Slack Notifications](https://github.com/calbergs/spotify-api/blob/master/setup/slack_notifications.md) for task-failure alerts.
4. (Optional) [`/spotify` Slack bot](slack_bot/README.md) — ask questions about your listening history on demand, separate from the scheduled weekly summary.

Dashboarding is via **Apache Superset**, shared with the `ynab-api` Superset instance (both read from the same `airflow` Postgres database — see `ynab-api/README.md`'s Superset section). Metabase is no longer used.

`setup/postgres.md`, `setup/dbt.md`, and `setup/metabase.md` describe an older, standalone setup (before this moved into the shared `data-platform` stack) and are kept only for historical reference — don't follow them for a fresh setup.

## Testing

Unit tests cover the pure logic behind the DAG's retry/branching behavior
(`operators/main.py`'s `request_with_retry`, `operators/dag_helpers.py`'s
payload-emptiness check and weekly-summary-window check) -- split into a
plain module specifically so they're runnable without an Airflow install,
unlike the DAG file itself.

```bash
pip install -r requirements.txt
pytest
```

Data quality (beyond the primary-key `unique`/`not_null` tests every dbt
model already has) is checked by `dbt test`: `not_null` on `song_name`/
`artist_name`/`song_duration_mins`, plus two singular tests
(`operators/dbt/tests/`) asserting no non-positive song durations and no
listens timestamped in the future.
