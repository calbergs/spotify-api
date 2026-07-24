{{
    config(
        materialized='table'
    )
}}

with source_spotify_songs as (
    select * from {{ source('spotify', 'spotify_songs') }}
),

excluded_plays as (
    select * from {{ source('spotify', 'spotify_excluded_plays') }}
),

final as (
    select source_spotify_songs.*
    from source_spotify_songs
    left join excluded_plays
        on source_spotify_songs.played_at_utc = excluded_plays.played_at_utc
    where excluded_plays.played_at_utc is null
)

select * from final