"""
Generates a new access token on each run
"""

import sys

import requests
from spotify_secrets import base_64, refresh_token


class RefreshToken:
    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(
            query,
            data={"grant_type": "refresh_token", "refresh_token": self.refresh_token},
            headers={"Authorization": "Basic " + self.base_64},
        )
        if response.status_code != 200:
            print(
                "ERROR: Spotify token refresh failed with "
                f"{response.status_code}: {response.text[:200]}",
                file=sys.stderr,
            )
            response.raise_for_status()
        try:
            response_json = response.json()
        except ValueError:
            print(
                "ERROR: Failed to parse Spotify token refresh response as JSON. "
                f"Status {response.status_code}, body starts with: {response.text[:200]}",
                file=sys.stderr,
            )
            raise
        return response_json["access_token"]


if __name__ == "__main__":
    new_token = RefreshToken()
    new_token.refresh()
