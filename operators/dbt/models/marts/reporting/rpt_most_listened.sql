{{
    config(
        materialized='view'
    )
}}

with listening_activity as (

    select * from {{ ref('fct_listening_activity') }}

),

final as (

    select distinct
        song_name,
        artist_name,
        album_name,
        artist_genre,
        song_link,
        count(track_id) over (partition by played_at_week_number, artist_name, song_name) as times_song_listened_this_week,
        count(track_id) over (partition by played_at_month, artist_name, song_name) as times_song_listened_this_month,
        count(track_id) over (partition by played_at_year, artist_name, song_name) as times_song_listened_this_year,
        count(artist_id) over (partition by played_at_week_number, artist_id) as times_artist_listened_this_week,
        count(artist_id) over (partition by played_at_month, artist_id) as times_artist_listened_this_month,
        count(artist_id) over (partition by played_at_year, artist_id) as times_artist_listened_this_year,
        max(played_date) over (partition by track_id) as song_last_listened_date

    from listening_activity
)

select * from final