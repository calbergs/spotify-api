{{
    config(
        materialized='table'
    )
}}

with genres as (

    select
        artist_id,
        artist_name,
        artist_genre,
        last_updated_datetime_utc at time zone 'utc' at time zone 'America/Chicago' as last_updated_datetime_ct

    from {{ ref('stg_genres') }}

)

select * from genres