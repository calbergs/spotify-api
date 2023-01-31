"""
Generates a new access token on each run
"""

from secrets import base_64, refresh_token

import requests


class RefreshToken:
    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(
            query,
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            headers={"Authorization": "Basic " + base_64},
        )

        response_json = response.json()
        return response_json["access_token"]


if __name__ == "__main__":
    new_token = RefreshToken()
    new_token.refresh()
