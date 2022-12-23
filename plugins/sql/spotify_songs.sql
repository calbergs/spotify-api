SELECT
	last_updated_datetime_utc at time zone 'utc' at time zone 'cst' as last_updated_datetime_cst,
	played_at_utc at time zone 'utc' at time zone 'cst' as played_at_cst,
	cast(played_date_utc at time zone 'utc' at time zone 'cst' as date) as played_date_cst,
	to_char(played_at_utc at time zone 'utc' at time zone 'cst', 'Day') as played_at_cst_day_of_week,
	extract(year from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_year,
	extract(month from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_month,
	extract(day from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_day,
	extract(hour from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_hour,
	song_name,
	artist_name,
	song_duration_ms,
	cast(song_duration_ms as decimal)/60000 as song_duration_mins,
	song_link,
	album_art_link,
	album_name,
	album_release_date,
	album_id,
	artist_id
FROM
    public.spotify_songs