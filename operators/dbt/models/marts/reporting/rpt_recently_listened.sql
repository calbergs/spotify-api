{{
    config(
        materialized='view'
    )
}}

with listening_activity as (

    select * from {{ ref('fct_listening_activity') }}

),

final as (

    select
        played_at,
        song_name,
        artist_name,
        album_name,
        artist_genre,
        song_duration_mins,
        song_link,
        last_updated_datetime

    from listening_activity
)

select * from final