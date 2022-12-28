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
        artist_genre,
        song_link,
        count(track_id) over (partition by artist_name, song_name) as track_times_listened,
        max(played_at_cst) over (partition by track_id) as last_listened_time_cst,
        count(artist_id) over (partition by artist_id) as artist_times_listened,
        track_id

    from listening_activity
)

select * from final