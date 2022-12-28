{{
    config(
        materialized='table'
    )
}}

with source_spotify_genres as (
    select * from {{ source('spotify', 'spotify_genres') }}
),

final as (
    select * from source_spotify_genres
)

select * from final