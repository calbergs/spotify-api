"""
Makes requests to the Spotify API to retrieve recently played songs and the corresponding genres
"""

import datetime
import json
import pandas as pd
import requests
from refresh import Refresh
from secrets import spotify_user_id

class RetrieveSongs:
    def __init__(self):
        self.user_id = spotify_user_id # Spotify username
        self.spotify_token = "" # Spotify access token
        self.artists_id_dedup = "" # Deduped list of artist ids

    # Extract recently played songs from Spotify API
    def get_songs(self):
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : "Bearer {}".format(self.spotify_token)
        }

        # Convert time to Unix timestamp in miliseconds
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

        # Download all songs listened to in the past 24 hours
        song_response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&after={time}".format(time=yesterday_unix_timestamp), headers = headers)

        song_data = song_response.json()

        played_at_utc = []
        played_date_utc = []
        song_names = []
        artist_names = []
        song_durations_ms = []
        song_links = []
        album_art_links = []
        album_names = []
        album_release_dates = []
        album_ids = []
        artist_ids = []

        # Extract only the necessary data from the json object
        for song in song_data["items"]:
            played_at_utc.append(song["played_at"])
            played_date_utc.append(song["played_at"][0:10])
            song_names.append(song["track"]["name"])
            artist_names.append(song["track"]["album"]["artists"][0]["name"])
            song_durations_ms.append(song["track"]["duration_ms"])
            song_links.append(song["track"]["external_urls"]["spotify"])
            album_art_links.append(song["track"]["album"]["images"][1]["url"])
            album_names.append(song["track"]["album"]["name"])
            album_release_dates.append(song["track"]["album"]["release_date"])
            album_ids.append(song["track"]["album"]["id"])
            artist_ids.append(song["track"]["artists"][0]["id"])

        # Prepare a dictionary in order to turn it into a pandas dataframe
        song_dict = {
            "played_at_utc" : played_at_utc,
            "played_date_utc" : played_date_utc,
            "song_name" : song_names,
            "artist_name": artist_names,
            "song_duration_ms": song_durations_ms,
            "song_link": song_links,
            "album_art_link": album_art_links,
            "album_name": album_names,
            "album_release_date": album_release_dates,
            "album_id": album_ids,
            "artist_id": artist_ids
        }

        song_df = pd.DataFrame(song_dict, columns = [
            "played_at_utc",
            "played_date_utc",
            "song_name",
            "artist_name",
            "song_duration_ms",
            "song_link",
            "album_art_link",
            "album_name",
            "album_release_date",
            "album_id",
            "artist_id"
        ])

        song_df.to_csv('spotify_data/spotify_songs.csv', index=False)

        # Retrieve the corresponding genres for the artists in the artist_ids list
        artist_ids_genres = []
        artist_names = []
        artist_genres = []

        artist_ids_dedup = set(artist_ids)

        for id in artist_ids_dedup:
            artist_response = requests.get("https://api.spotify.com/v1/artists/{id}".format(id=id), headers = headers)

            artist_data = artist_response.json()

            artist_ids_genres.append(artist_data["id"])
            artist_names.append(artist_data["name"])

            if len(artist_data["genres"]) == 0:
                artist_genres.append(None)
            else:
                artist_genres.append(artist_data["genres"][0])

        artist_dict = {
            "artist_id": artist_ids_genres,
            "artist_name": artist_names,
            "artist_genre": artist_genres
        }

        artist_genre_df = pd.DataFrame(artist_dict, columns = [
            "artist_id",
            "artist_name",
            "artist_genre"
        ])

        artist_genre_df.to_csv('spotify_data/spotify_genres.csv', index=False)

    def call_refresh(self):
        print("Refreshing token...")
        refreshCaller= Refresh()
        self.spotify_token = refreshCaller.refresh()
        print("Getting songs...")
        self.get_songs()

if __name__ == "__main__":
    tracks = RetrieveSongs()
    tracks.call_refresh()