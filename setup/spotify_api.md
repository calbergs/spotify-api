1. Ensure you have a Spotify account created
2. Register Your Application
    -Go to the [Dashboard] (https://developer.spotify.com/dashboard/applications) page on the Spotify Developer site
    -Click on **CREATE AN APP**. Provide your app name and app description and then click create.
    -Click on **EDIT SETTINGS** and provide a redirect URI and then click save
    -Copy and save your Client ID and Client Secret
3. Define your query parameters for the GET request
    https://accounts.spotify.com/authorize?client_id=<your_client_id>&response_type=code&redirect_uri=<your_redirect_uri>&scope=<your_scope>
    -<your_client_id> = The Client ID saved from step 2 above
    -<your_redirect_uri> = The redirect URI you provided in step 2 above. This needs to be the ENCODED redirect URI. You can encode the redirect URI by going to [urlencoder.org] (https://www.urlencoder.org/), pasting in the redirect URI, and then clicking encode. Ensure encode is selected and not decode.
    -<your_scope> = Scope(s) needed for your requests. In this case we are using user-read-recently-played.
4. Make the GET request using the link in step 3 to obtain your authorization code
    -Paste the link from step 3 into a browser and hit enter
    -Click Agree
    -Copy the new URL and save the authorization code (value after 'code=')
5. Define your curl command
    -Ensure you have curl by opening up command prompt/terminal and typing curl.
    -Convert Client ID and Client Secret to a base 64 encoded string
        -<your_client_id>:<your_client_secret>
        -You can convert this by going to [base64encode.org] (https://www.base64encode.org/), pasting in the string like in the example above, and then clicking encode. Ensure encode is selected and not decode.
    -curl -d client_id=<your_client_id> -d client_secret=<your_client_secret> -d grant_type=authorization_code -d code=<authorization_code_obtained_from_step_4> -d redirect_uri=<your_redirect_uri> https://accounts.spotify.com/api/token
6. Run curl command to obtain access token and refresh token
    -Paste in the curl command from step 5 into command prompt/terminal and run
    -Save your access token and refresh token
    -Access token is what we define as spotify_token in our code
    -Refresh token will be used to generate a new access token on each run