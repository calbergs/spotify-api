"""
Makes requests to the Spotify API to retrieve recently played songs and the corresponding genres
"""

import datetime as dt
import json
import os.path
import pandas as pd
import psycopg2
import requests
from datetime import datetime
from io import StringIO
from pathlib import Path
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

        if max_played_at_utc == None:
            today = dt.datetime.now()
            yesterday = today - dt.timedelta(days=1)
            yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
            latest_timestamp = yesterday_unix_timestamp
        else:
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

        # Download all songs listened to since the last run
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
        # album_release_dates = []
        album_ids = []
        artist_ids = []
        track_ids = []

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
            # album_release_dates.append(song["track"]["album"]["release_date"])
            album_ids.append(song["track"]["album"]["id"])
            artist_ids.append(song["track"]["artists"][0]["id"])
            track_ids.append(song["track"]["id"])

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
            "album_id": album_ids,
            "artist_id": artist_ids,
            "track_id": track_ids
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
            "album_id",
            "artist_id",
            "track_id"
        ])

        last_updated_datetime_utc = dt.datetime.utcnow()
        # last_updated_date_utc = dt.datetime.strftime(last_updated_datetime_utc, '%Y-%m-%d')
        song_df['last_updated_datetime_utc'] = last_updated_datetime_utc
        song_df = song_df.sort_values('played_at_utc', ascending=True)

        # Remove latest song since last run since this will be a duplicate
        song_df = song_df.iloc[1: , :]
        song_df.to_csv('/opt/airflow/dags/spotify_data/spotify_songs.csv', index=False)

        for date in set(song_df['played_date_utc']):
            played_dt = datetime.strptime(date, '%Y-%m-%d')
            date_year = played_dt.year
            date_month = played_dt.month
            output_song_dir = Path(f'/opt/airflow/dags/spotify_data/spotify_songs/{date_year}/{date_month}')
            output_song_file = f'{date}.csv'
            path_to_songs_file = f'{output_song_dir}/{output_song_file}'
            songs_file_exists = os.path.exists(path_to_songs_file)
            print(songs_file_exists)
            # Check to see if file exists. If not create a new file, else append to existing file.
            if songs_file_exists:
                curr_song_df = pd.read_csv(path_to_songs_file)
                curr_song_df = curr_song_df.append(song_df)
                curr_song_df.to_csv(path_to_songs_file, index=False)
            else:
                output_song_dir.mkdir(parents=True, exist_ok=True)
                song_df.loc[song_df['played_date_utc'] == date].to_csv(f'{output_song_dir}/{date}.csv', index=False)

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

        artist_genre_df.to_csv('/opt/airflow/dags/spotify_data/spotify_genres_tmp.csv', index=False)
        artist_genre_df_nh = pd.read_csv('/opt/airflow/dags/spotify_data/spotify_genres_tmp.csv', sep=',')
        try:
            curr_artist_genre_df = pd.read_csv('/opt/airflow/dags/spotify_data/spotify_genres.csv', sep=',')
            curr_artist_genre_df = curr_artist_genre_df.append(artist_genre_df_nh)
            curr_artist_genre_df.drop_duplicates(subset="artist_id", keep="first", inplace=True)
            curr_artist_genre_df['last_updated_datetime_utc'] = last_updated_datetime_utc
            curr_artist_genre_df.to_csv('/opt/airflow/dags/spotify_data/spotify_genres.csv', index=False)
        except:
            artist_genre_df_nh['last_updated_datetime_utc'] = last_updated_datetime_utc
            artist_genre_df_nh.to_csv('/opt/airflow/dags/spotify_data/spotify_genres.csv', index=False)
        os.remove('/opt/airflow/dags/spotify_data/spotify_genres_tmp.csv')

    def load_to_postgres(self):
        conn = psycopg2.connect(f"host='{host}' port='{port}' dbname='{dbname}' user='{pg_user}' password='{pg_password}'")
        cur = conn.cursor()

        datasets = [
            'spotify_songs',
            'spotify_genres'
        ]

        # for dataset in datasets:
        #     f = open(f'/opt/airflow/dags/spotify_data/{dataset}.csv', 'r')
        #     cur.copy_from(f, dataset, sep=',')
        #     conn.commit()
        #     f.close()
        #     print(f'Loaded {dataset}')

        query ="""
        copy spotify_genres
        from '/opt/airflow/dags/spotify_data/spotify_genres.csv'
        delimiter ',' csv;
        """
        cur.execute(query)

    def call_refresh(self):
        print("Refreshing token...")
        refreshCaller= Refresh()
        self.spotify_token = refreshCaller.refresh()
        print("Getting songs...")
        self.get_songs()
        # print("Loading to postgres...")
        # self.load_to_postgres()

if __name__ == "__main__":
    tracks = RetrieveSongs()
    tracks.call_refresh()