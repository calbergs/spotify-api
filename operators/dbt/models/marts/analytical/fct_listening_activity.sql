{{
    config(
        materialized='table'
    )
}}

with songs as (

    select * from {{ ref('dim_songs') }}

),

genres as (

    select * from {{ ref('dim_genres') }}

),

final as (

	select
		songs.played_at_cst as played_at,
		songs.played_date_cst as played_date,
		to_char(songs.played_at_cst, 'Day') as played_at_day_of_week,
		extract(year from songs.played_at_cst) as played_at_year,
		extract(month from songs.played_at_cst) as played_at_month,
		extract(day from songs.played_at_cst) as played_at_day,
		DATE_PART('week', cast(date_trunc('week', songs.played_at_cst + interval '1 day') - interval '1 day' as date)) as played_at_week_number,
		extract(hour from songs.played_at_cst) as played_at_hour,
		songs.song_name,
		songs.artist_name,
		genres.artist_genre,
		songs.song_duration_ms,
		cast(songs.song_duration_ms as decimal)/60000 as song_duration_mins,
		songs.song_link,
		songs.album_art_link,
		songs.album_name,
		songs.album_id,
		songs.artist_id,
		songs.track_id,
		songs.last_updated_datetime_cst as last_updated_datetime

	from songs

	left join genres
        on songs.artist_id = genres.artist_id

)

select * from final