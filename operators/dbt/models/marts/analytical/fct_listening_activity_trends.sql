{{ 
    config(
        materialized='table'
    )
}}

-- Source: fct_listening_activity
-- Goal: Calculate day-over-day and week-over-week change in total listening time (song_duration_mins)

with daily_activity as (

    select
        played_date,
        sum(song_duration_mins) as total_listening_mins
    from {{ ref('fct_listening_activity') }}
    group by played_date

),

daily_change as (

    select
        played_date,
        total_listening_mins,
        lag(total_listening_mins) over (order by played_date) as prev_day_listening_mins,
        total_listening_mins - lag(total_listening_mins) over (order by played_date) as day_over_day_change,
        case 
            when lag(total_listening_mins) over (order by played_date) = 0 then null
            else round(
                (total_listening_mins - lag(total_listening_mins) over (order by played_date))
                / lag(total_listening_mins) over (order by played_date) * 100, 2
            )
        end as day_over_day_pct_change
    from daily_activity

),

weekly_activity as (

    select
        date_trunc('week', played_date)::date as week_start_date,
        sum(song_duration_mins) as total_listening_mins
    from {{ ref('fct_listening_activity') }}
    group by 1

),

weekly_change as (

    select
        week_start_date,
        total_listening_mins,
        lag(total_listening_mins) over (order by week_start_date) as prev_week_listening_mins,
        total_listening_mins - lag(total_listening_mins) over (order by week_start_date) as week_over_week_change,
        case 
            when lag(total_listening_mins) over (order by week_start_date) = 0 then null
            else round(
                (total_listening_mins - lag(total_listening_mins) over (order by week_start_date))
                / lag(total_listening_mins) over (order by week_start_date) * 100, 2
            )
        end as week_over_week_pct_change
    from weekly_activity

),

final as (

    select
        'daily' as granularity,
        played_date as period_start_date,
        total_listening_mins,
        day_over_day_change as change_in_mins,
        day_over_day_pct_change as pct_change
    from daily_change

    union all

    select
        'weekly' as granularity,
        week_start_date as period_start_date,
        total_listening_mins,
        week_over_week_change as change_in_mins,
        week_over_week_pct_change as pct_change
    from weekly_change

)

select * from final
order by granularity, period_start_date
