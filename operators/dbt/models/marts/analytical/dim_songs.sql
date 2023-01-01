{{
    config(
        materialized='table'
    )
}}

with songs as (

	select
		played_at_utc at time zone 'utc' at time zone 'cst' as played_at_cst,
		cast(played_at_utc at time zone 'utc' at time zone 'cst' as date) as played_date_cst,
		song_name,
		artist_name,
		song_duration_ms,
		song_link,
		album_art_link,
		album_name,
		album_id,
		artist_id,
		track_id,
		last_updated_datetime_utc at time zone 'utc' at time zone 'cst' as last_updated_datetime_cst

	from {{ ref('stg_songs') }}

)

select * from songs