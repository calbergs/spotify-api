# Spotify API Access

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
    - Using the format above convert to a base 64 encoded string by going to [base64encode.org](https://www.base64encode.org/), pasting in the string, and then clicking encode. Ensure encode is selected and not decode.<br>
    - This will be defined as base_64 in our code and will be used when we generate a new access token on each run<br>

References:
https://developer.spotify.com/console/get-recently-played/?limit=&after=&before=