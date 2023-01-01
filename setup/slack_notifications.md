### Enable Slack notifications for any Airflow task failures

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
- Implement the code into the DAG script to enable alerts