"""
Script to generate credentials to be authenticated on Youtube API
as the owner of a Youtube channel.

Follow these instructions:

1. Go to https://console.cloud.google.com/apis/credentials

    a. Enable access to Youtube API
        (only if you never used the Youtube API on this Google Cloud project)

        * In the left menu, go to "Enabled APIs and Services"
        * Search for "Youtube Data API v3"
        * "Enable" the Youtube API on your project

    b. Configure OAuth consent screen
        (only if this is not yet configured on your current Google Cloud project,
        or if you need to edit its scope to include Youtube access)

        * In the left menu, go to "OAuth consent screen"
        * Select "External" user type
        * Configure the minimal required fields: app name (e.g "Tournesol") and email address
        * On "Scopes", add scope "https://www.googleapis.com/auth/youtube" ("Manage your
        YouTube account")
        * No test user is required
        * "Back to dashboard"
        * At the top of the page in Publishing status, click on "Publish App"
        As the app will only be used by your own user, you won't need to submit the app
        for verification by Google.

    c. Create a new Oauth application and get client secret

        * In the left menu, go to "Credentials"
        * "Create credentials" -> "OAuth client ID" -> "Web application"
        * Choose a name for the application, such as "Tournesol jobs on Youtube channel"
        * In the last section, add `http://localhost:8080/` as a Redirect URI (note the
        trailing slash)
        You can also use any port available locally, as configured below in LOCALHOST_PORT.
        * Download json file that contains your client secret for your new app.
        Configure its path below as CLIENT_SECRET_FILE_PATH.

2. Run the present script on your machine: `python3 ./youtube_channel_oauth_flow.py`
    (You may need to install "google-auth-oauthlib" via pip)

    * A browser window should open automatically to log into your Google account,
      and select the Youtube channel you want to authenticate with.
    * Once the authentication flow has completed, you may close the browser.
    * The credentials are visible in the console.
      The json string can be used as YOUTUBE_CHANNEL_CREDENTIALS_JSON in backend settings.
"""

import google_auth_oauthlib.flow
import json

LOCALHOST_PORT = 8080
CLIENT_SECRET_FILE_PATH = "path/to/your/client_secret.json"  # nosec B105


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def auth_flow():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE_PATH,
        scopes=["https://www.googleapis.com/auth/youtube"],
    )
    credentials = flow.run_local_server(port=LOCALHOST_PORT)
    return credentials


if __name__ == "__main__":
    creds = auth_flow()
    creds_dict = credentials_to_dict(creds)
    print()
    print("The authentication flow has completed!")
    print("Find your JSON credentials below:\n")
    print(json.dumps(creds_dict))
