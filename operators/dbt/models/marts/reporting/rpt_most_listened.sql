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
        count(track_id) over (partition by artist_name, song_name) as times_song_listened,
        count(artist_id) over (partition by artist_id) as times_artist_listened,
        max(played_date) over (partition by track_id) as song_last_listened_date

    from listening_activity
)

select * from final