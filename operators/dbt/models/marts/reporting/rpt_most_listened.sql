{{
    config(
        materialized='view'
    )
}}

with listening as (

    select * from {{ ref('fct_listening_activity') }}

),

song_stats as (

    select
        song_name,
        artist_name,
        song_link,
        min(album_name) as album_name,
        min(artist_genre) as artist_genre,
        count(*) as times_song_listened,
        max(played_date) as song_last_listened_date,
        max(artist_id) as artist_id
    from listening
    group by song_name, artist_name, song_link

),

artist_stats as (

    select
        artist_id,
        count(*) as times_artist_listened
    from listening
    group by artist_id

)

select
    s.song_name,
    s.artist_name,
    s.album_name,
    s.artist_genre,
    s.song_link,
    s.times_song_listened,
    a.times_artist_listened,
    s.song_last_listened_date
from song_stats s
join artist_stats a
    on s.artist_id = a.artist_id