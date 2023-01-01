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