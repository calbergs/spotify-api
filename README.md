# Spotify Data Pipeline

Data pipeline that extracts a user's song listening history using Python, PostgreSQL, dbt, Metabase, Airflow, and Docker

## Objective

Deep dive into a user's song listening history to retrieve information about top artists, top tracks, top genres, and more. This is a personal side project for fun to recreate Spotify Wrapped but at a more frequent cadence to get quicker and more detailed insights. This pipeline will call the Spotify API every 30 minutes to retrieve a user's song listening history, load the responses into a database, apply transformation and then visualize the metrics in a dashboard. Since the dataset and listening frequency is small this is all built and hosted locally to avoid any cost.

## Tools & Technologies

- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Airflow**](https://airflow.apache.org)
- Database - [**PostgreSQL**](https://www.postgresql.org/)
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

### Spotify API Access
- Ensure you have a Spotify account created
- Register Your Application
  - Go to the [**Dashboard**](https://developer.spotify.com/dashboard/applications) page on the Spotify Developer site
  - Click on **CREATE AN APP**. Provide your app name and app description and then click create.
  - Click on **EDIT SETTINGS** and provide a redirect URI and then click save
  - Copy and save your Client ID and Client Secret
- Define the query parameters in your custom link
  - Link: https://accounts.spotify.com/authorize?client_id=<your_client_id>&response_type=code&redirect_uri=<your_redirect_uri>&scope=<your_scope>
  - <your_client_id> = The Client ID saved from step 2 above
  - <your_redirect_uri> = The redirect URI you provided in step 2 above. This needs to be the ENCODED redirect URI. You can encode the redirect URI by going to [**urlencoder.org**](https://www.urlencoder.org/), pasting in the redirect URI, and then clicking encode. Ensure encode is selected and not decode.
  - <your_scope> = Scope(s) needed for your requests. In this case we are using user-read-recently-played.
- Go to the link created in the step above to obtain your authorization code
  - Paste the link from step 3 into a browser and hit enter
  - Click Agree
  - Copy the new URL and save the authorization code (value after 'code=' parameter)
- Define your curl command
  - Ensure you have curl by opening up command prompt/terminal and typing curl.
  - Curl command:
  ```
    -curl -d client_id=your_client_id -d client_secret=your_client_secret -d grant_type=authorization_code -d code=your_authorization_code_obtained_from_step_4 -d redirect_uri=your_redirect_uri https://accounts.spotify.com/api/token
  ```
- Run curl command to obtain access token and refresh token
  - Paste in the curl command from step 5 into command prompt/terminal and run
  - Save your access token and refresh token
  - Access token is what we define as spotify_token in our code
  - Refresh token will be used to generate a new access token on each run as the access token expires after one hour
- Convert Client ID and Client Secret to a base 64 encoded string
  - <your_client_id>:<your_client_secret>
  - Using the format above convert to a base 64 encoded string by going to [**base64encode.org**](https://www.base64encode.org/), pasting in the string, and then clicking encode. Ensure encode is selected and not decode.
  - This will be defined as base_64 in our code and will be used when we generate a new access token on each run

## Further Improvements (Work In Progress)

- Implement data quality checks to catch any errors in the dataset
- Create unit tests to ensure pipeline is running as intended
- Include CI/CD
- Create more visualizations to uncover more insights
