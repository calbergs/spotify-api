{{
    config(
        materialized='table'
    )
}}

with source_spotify_saved_tracks as (
    select * from {{ source('spotify', 'spotify_saved_tracks') }}
),

final as (
    select * from source_spotify_saved_tracks
)

select * from final
