{{
    config(
        materialized='view'
    )
}}

select
    played_at_day_of_week,
    case when played_at_day_of_week like '%Sunday%' then '0_Sun'
     when played_at_day_of_week like '%Monday%' then '1_Mon'
     when played_at_day_of_week like '%Tuesday%' then '2_Tue'
     when played_at_day_of_week like '%Wednesday%' then '3_Wed'
     when played_at_day_of_week like '%Thursday%' then '4_Thu'
     when played_at_day_of_week like '%Friday%' then '5_Fri'
     when played_at_day_of_week like '%Saturday%' then '6_Sat'
     end as day_num,
    played_at_hour,
    sum(song_duration_mins) as song_duration_mins

from {{ ref('fct_listening_activity') }}

group by
    played_at_day_of_week,
    played_at_hour