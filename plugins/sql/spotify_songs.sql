SELECT
	last_updated_datetime_utc at time zone 'utc' at time zone 'cst' as last_updated_datetime_cst,
	played_at_utc at time zone 'utc' at time zone 'cst' as played_at_cst,
	song_name,
	artist_name,
	song_duration_ms,
	song_link,
	album_art_link,
	album_name,
	album_release_date,
	album_id,
	artist_id
FROM
    public.spotify_songs
ORDER BY
    played_at_utc DESC;