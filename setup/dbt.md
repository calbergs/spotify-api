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