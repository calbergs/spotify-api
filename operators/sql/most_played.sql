with listening_history as (
	SELECT
		songs.last_updated_datetime_utc at time zone 'utc' at time zone 'cst' as last_updated_datetime_cst,
		played_at_utc at time zone 'utc' at time zone 'cst' as played_at_cst,
		cast(played_date_utc at time zone 'utc' at time zone 'cst' as date) as played_date_cst,
		to_char(played_at_utc at time zone 'utc' at time zone 'cst', 'Day') as played_at_cst_day_of_week,
		extract(year from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_year,
		extract(month from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_month,
		extract(day from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_day,
		DATE_PART('week',played_at_utc) as played_at_cst_week_number,
		extract(hour from played_at_utc at time zone 'utc' at time zone 'cst') as played_at_cst_hour,
		song_name,
		songs.artist_name,
		genres.artist_genre,
		song_duration_ms,
		cast(song_duration_ms as decimal)/60000 as song_duration_mins,
		song_link,
		album_art_link,
		album_name,
		album_id,
		songs.artist_id,
		track_id
	FROM
	    public.spotify_songs songs
	left join
		public.spotify_genres genres
		on songs.artist_id = genres.artist_id
--	order by
--		played_at_utc desc
)
select distinct
	song_name,
	artist_name,
	artist_genre,
	song_link,
	count(track_id) over (partition by artist_name, song_name) as track_times_listened,
	max(played_at_cst) over (partition by track_id) as last_listened_time_cst,
	sum(song_duration_ms) over (partition by artist_name) as artist_minutes_listened,
	track_id
from listening_history
order by
	track_times_listened desc