"""
Makes requests to the Spotify API to retrieve recently played songs and the corresponding genres
"""

import datetime
import json
import pandas as pd
import psycopg2
import requests
from refresh import Refresh
from secrets import spotify_user_id, pg_user, pg_password, host, port, dbname

class RetrieveSongs:
    def __init__(self):
        self.user_id = spotify_user_id # Spotify username
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.spotify_token = "" # Spotify access token
        self.artists_id_dedup = "" # Deduped list of artist ids

    # Query the postgres database to get the latest played timestamp
    def get_latest_listened_timestamp(self):
        conn = psycopg2.connect(f"host='{host}' port='{port}' dbname='{dbname}' user='{pg_user}' password='{pg_password}'")
        cur = conn.cursor()

        query = "SELECT MAX(played_at_utc) FROM public.spotify_songs"

        cur.execute(query)
        total_records = cur.rowcount

        max_played_at_utc = cur.fetchall()[0][0]
        latest_timestamp = int(max_played_at_utc.timestamp()) * 1000
        return latest_timestamp

    # Extract recently played songs from Spotify API
    def get_songs(self):
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : "Bearer {}".format(self.spotify_token)
        }

        latest_timestamp = RetrieveSongs().get_latest_listened_timestamp()

        # Download all songs listened to in the past 24 hours
        song_response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&after={time}".format(time=latest_timestamp), headers = headers)

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

        last_updated_datetime_utc = datetime.datetime.utcnow()
        song_df['last_updated_datetime_utc'] = last_updated_datetime_utc
        song_df = song_df.sort_values('played_at_utc', ascending=True)
        song_df = song_df.iloc[1: , :]
        song_df.to_csv('/opt/airflow/dags/spotify_data/spotify_songs.csv', index=False, header=False)

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

        artist_genre_df.to_csv('/opt/airflow/dags/spotify_data/spotify_genres.csv', index=False, header=False)

    def load_to_postgres(self):
        conn = psycopg2.connect(f"host='{host}' port='{port}' dbname='{dbname}' user='{pg_user}' password='{pg_password}'")
        cur = conn.cursor()

        datasets = [
            'spotify_songs'
        ]

        for dataset in datasets:
            f = open(f'/opt/airflow/dags/spotify_data/{dataset}.csv', 'r')
            # print(f.read())
            cur.copy_from(f, dataset, sep=',')
            conn.commit()
            f.close()
            print(f'Loaded {dataset}')

    def call_refresh(self):
        print("Refreshing token...")
        refreshCaller= Refresh()
        self.spotify_token = refreshCaller.refresh()
        print("Getting songs...")
        self.get_songs()
        print("Loading to postgres...")
        self.load_to_postgres()

if __name__ == "__main__":
    tracks = RetrieveSongs()
    tracks.call_refresh()