### Obtaining access to the Spotify API

1. Ensure you have a Spotify account created
2. Register Your Application
    <p>- Go to the [Dashboard] (https://developer.spotify.com/dashboard/applications) page on the Spotify Developer site<br>
    - Click on **CREATE AN APP**. Provide your app name and app description and then click create.<br>
    - Click on **EDIT SETTINGS** and provide a redirect URI and then click save<br>
    - Copy and save your Client ID and Client Secret<br>
3. Define your query parameters for the GET request
    <p>https://accounts.spotify.com/authorize?client_id=your_client_id&response_type=code&redirect_uri=your_redirect_uri&scope=your_scope<br>
    - your_client_id = The Client ID saved from step 2 above<br>
    - your_redirect_uri = The redirect URI you provided in step 2 above. This needs to be the ENCODED redirect URI. You can encode the redirect URI by going to [urlencoder.org] (https://www.urlencoder.org/), pasting in the redirect URI, and then clicking encode. Ensure encode is selected and not decode.<br>
    - your_scope = Scope(s) needed for your requests. In this case we are using user-read-recently-played.<br>
4. Make the GET request using the link in step 3 to obtain your authorization code
    <p>- Paste the link from step 3 into a browser and hit enter<br>
    - Click Agree<br>
    - Copy the new URL and save the authorization code (value after 'code=')<br>
5. Define your curl command
    <p>- Ensure you have curl by opening up command prompt/terminal and typing curl.<br>
    - Convert Client ID and Client Secret to a base 64 encoded string<br>
        - your_client_id:your_client_secret<br>
        - You can convert this by going to [base64encode.org] (https://www.base64encode.org/), pasting in the string like in the example above, and then clicking encode. Ensure encode is selected and not decode.<br>
        -curl -d client_id=<your_client_id> -d client_secret=<your_client_secret> -d grant_type=authorization_code -d code=<authorization_code_obtained_from_step_4> -d redirect_uri=<your_redirect_uri> https://accounts.spotify.com/api/token<br>
6. Run curl command to obtain access token and refresh token
    <p>- Paste in the curl command from step 5 into command prompt/terminal and run<br>
    - Save your access token and refresh token<br>
    - Access token is what we define as spotify_token in our code<br>
    - Refresh token will be used to generate a new access token on each run<br>