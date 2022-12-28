{{
    config(
        materialized='table'
    )
}}

with source_spotify_songs as (
    select * from {{ source('spotify', 'spotify_songs') }}
),

final as (
    select * from source_spotify_songs
)

select * from final