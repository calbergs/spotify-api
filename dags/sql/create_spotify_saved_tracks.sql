--hacky way to do a create or replace
--full refresh each run since the Spotify saved-tracks endpoint has no incremental cursor
--(unlike recently-played) and needs to reflect unlikes too, not just new likes
create table if not exists spotify_saved_tracks (
    track_id text,
    song_name text,
    artist_name text,
    album_name text,
    added_at_utc timestamp,
    last_updated_datetime_utc timestamp,
    primary key (track_id)
);
drop table spotify_saved_tracks;
create table if not exists spotify_saved_tracks (
    track_id text,
    song_name text,
    artist_name text,
    album_name text,
    added_at_utc timestamp,
    last_updated_datetime_utc timestamp,
    primary key (track_id)
);
