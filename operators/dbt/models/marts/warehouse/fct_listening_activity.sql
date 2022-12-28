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
		songs.played_at_cst,
		songs.played_date_cst,
		to_char(songs.played_at_cst, 'Day') as played_at_cst_day_of_week,
		extract(year from songs.played_at_cst) as played_at_cst_year,
		extract(month from songs.played_at_cst) as played_at_cst_month,
		extract(day from songs.played_at_cst) as played_at_cst_day,
		DATE_PART('week', songs.played_at_cst) as played_at_cst_week_number,
		extract(hour from songs.played_at_cst) as played_at_cst_hour,
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
		songs.last_updated_datetime_cst

	from songs

	left join genres
        on songs.artist_id = genres.artist_id

)

select * from final