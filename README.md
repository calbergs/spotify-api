# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline will call the Spotify API every 30 minutes to retrieve a user's song listening history, load the responses into a database, apply transformations and visualize the metrics in a dashboard. Since the dataset and listening frequency is small this is all built and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Database - [**PostgreSQL**](https://www.postgresql.org/)
- Transformation - [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Metabase**](https://www.metabase.com/)
- Language - [**Python**](https://www.python.org)

## Architecture

![spotify_architecture drawio](https://user-images.githubusercontent.com/60953643/210160261-98c3ff9e-3c54-4407-b758-828322fbc2ad.png)

## Dashboard
<img width="1726" alt="Screenshot 2022-12-31 at 7 41 09 PM" src="https://user-images.githubusercontent.com/60953643/210158921-0024a44f-2273-40dd-b974-cede87ef5d69.png">
<img width="1723" alt="Screenshot 2022-12-31 at 7 41 24 PM" src="https://user-images.githubusercontent.com/60953643/210158923-6050b65d-9955-448d-ac52-7556e0900c7d.png">
<img width="1721" alt="Screenshot 2022-12-31 at 7 41 36 PM" src="https://user-images.githubusercontent.com/60953643/210158927-c1f5e65a-e391-4e25-b6cf-7b23362f4439.png">
<img width="1725" alt="Screenshot 2022-12-31 at 7 41 44 PM" src="https://user-images.githubusercontent.com/60953643/210158928-6fc80f5d-8942-462f-846a-e380820aebfd.png">

## Setup

### Spotify API Access
- Ensure you have a Spotify account created
- Register Your Application
  - Go to the [**Dashboard**](https://developer.spotify.com/dashboard/applications) page on the Spotify Developer site
  - Click on **CREATE AN APP**. Provide your app name and app description and then click create.
  - Click on **EDIT SETTINGS** and provide a redirect URI and then click save
  - Copy and save your Client ID and Client Secret
- Define the query parameters in your custom link
  - Link: https://accounts.spotify.com/authorize?client_id=<your_client_id>&response_type=code&redirect_uri=<your_redirect_uri>&scope=<your_scope>
  - <your_client_id> = The Client ID saved from the step above
  - <your_redirect_uri> = The redirect URI you provided in the step above. This needs to be the ENCODED redirect URI. You can encode the redirect URI by going to [**urlencoder.org**](https://www.urlencoder.org/), pasting in the redirect URI, and then clicking encode. Ensure encode is selected and not decode.
  - <your_scope> = Scope(s) needed for your requests. In this case we are using user-read-recently-played.
- Go to the link created in the step above to obtain your authorization code
  - Paste the link from the step above into a browser and hit enter
  - Click Agree
  - Copy the new URL and save the authorization code (value after 'code=' parameter)
- Define your curl command
  - Ensure you have curl by opening up command prompt/terminal and typing curl
  - Curl command:
  ```
    -curl -d client_id=<your_client_id> -d client_secret=<your_client_secret> -d grant_type=authorization_code -d code=<your_authorization_code> -d redirect_uri=<your_redirect_uri> https://accounts.spotify.com/api/token
  ```
- Run curl command to obtain access token and refresh token
  - Paste in the curl command from the step above into command prompt/terminal and run
  - Save your access token and refresh token
  - Access token is what we define as spotify_token in our code
  - Refresh token will be used to generate a new access token on each run as the access token expires after one hour
- Convert Client ID and Client Secret to a base 64 encoded string
  - <your_client_id>:<your_client_secret>
  - Using the format above convert to a base 64 encoded string by going to [**base64encode.org**](https://www.base64encode.org/), pasting in the string, and then clicking encode. Ensure encode is selected and not decode.
  - This will be defined as base_64 in our code and will be used when we generate a new access token on each run
  
### Build Docker Containers for Airflow

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

### Set up Airflow connection to Postgres

- Add ports to the section under services and Postgres in the docker-compose.yaml file like below:
  ```
  ports:
      - 5432:5432
  ```
- Download DBeaver (or your tool of choice)
    - Create a new Postgres connection and add the username and password
    - Test the connection, it may ask you to download the Postgres JDBC driver if you don't have it. Download and test again.
    - Once connection is successful create a new database named 'spotify'
- Go to the Airflow UI and click on Admin>Connections then click on the + sign
- Fill in the connection with the below details and click save:
  - Conn Id: postgres_localhost
  - Conn Type: Postgres
  - Host: host.docker.internal
  - Schema: spotify
  - Login:
  - Password:
  - Port: 5432

### Install dbt Core with Homebrew (or your method of choice)

- Run the below commands:
  ```
  brew update
  brew install git
  brew tap dbt-labs/dbt
  ```
- Identify your [**adapter**](https://docs.getdbt.com/docs/supported-data-platforms) (in this case Postgres is used) and install:
  ```
  brew install dbt-postgres
  ```
- cd to the directory where you want to have dbt installed and initialize the project
  ```
  dbt init <your-folder-path>
  ```
- Update the profiles.yml file found in Users/<your-username>/.dbt/
  - Update all the appropriate configurations based on the [**dbt setup guide**](https://docs.getdbt.com/reference/warehouse-setups/postgres-setup)
- Go to the dbt_project.yml file and make sure the profile configuration matches with the one in the profiles.yml file
- Ensure the database setup was done correctly
  ```
  dbt debug
  ```
- Test that dbt is building the models correctly. If successful you can verify the new tables/views in the database.
  ```
  dbt run
  ```
- Generate the docs for the dbt project
  ```
  dbt docs generate
  ```
- Serve the docs on a webserver using port 8001
  ```
  dbt docs serve --port 8001
  ```

### Set up Slack notifications for any Airflow task failures

- Create a channel in your workspace where the alerts will be sent
- Go to api.slack.com/apps and click on "Create New App" then click on "From scratch"
- Give your app a name and select your workspace where the alerts will be sent then click "Create App"
- Enable incoming webhooks for your Slack workspace app
- You can test your webhook from the command line by running the code below (replace with your own key):
  ```
  -curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/00000000000/00000000000/000000000000000000000000
  ```
- Go to the Airflow UI and click on Admin>Connections then click on the + sign
- Fill in the connection with the below details and click save (replace password with your credentials):
  - Connection Id: slack
  - Connection Type: HTTP
  - Host: https://hooks.slack.com/services/
  - Password: /T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
 
### Set up Metabase

- Download the Metabase [**JAR file**](https://www.metabase.com/start/oss/) (or your method of choice)
- Create a new directory and move the Metabase JAR file into it
- Ensure the [**latest Java version**](https://www.oracle.com/java/technologies/downloads/#jdk19-mac) is downloaded
- Change into your new Metabase directory and run the JAR
  ```
  java -jar metabase.jar
  ```
- Metabase is now available on http://localhost:3000/setup
- Set up the connection and use host: localhost
  
## Further Improvements (Work In Progress)

- Implement data quality checks to catch any errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover more insights
