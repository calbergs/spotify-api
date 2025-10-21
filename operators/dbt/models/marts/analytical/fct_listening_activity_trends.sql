{{
    config(
        materialized='table'
    )
}}

-- Source: fct_listening_activity
-- Goal: Calculate day-over-day change and 7-day rolling average in total listening time (song_duration_mins)

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

rolling_7day as (

    select
        played_date,
        total_listening_mins,
        -- 7-day rolling average (includes current day)
        round(
            avg(total_listening_mins) over (
                order by played_date
                rows between 6 preceding and current row
            ),
            2
        ) as rolling_7day_avg_listening_mins
    from daily_activity

),

rolling_change as (

    select
        played_date,
        rolling_7day_avg_listening_mins,
        lag(rolling_7day_avg_listening_mins) over (order by played_date) as prev_rolling_avg,
        round(
            rolling_7day_avg_listening_mins - lag(rolling_7day_avg_listening_mins) over (order by played_date),
            2
        ) as rolling_avg_change,
        case
            when lag(rolling_7day_avg_listening_mins) over (order by played_date) = 0 then null
            else round(
                (rolling_7day_avg_listening_mins - lag(rolling_7day_avg_listening_mins) over (order by played_date))
                / lag(rolling_7day_avg_listening_mins) over (order by played_date) * 100,
                2
            )
        end as rolling_avg_pct_change
    from rolling_7day

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
        'rolling_7day' as granularity,
        played_date as period_start_date,
        rolling_7day_avg_listening_mins as total_listening_mins,
        rolling_avg_change as change_in_mins,
        rolling_avg_pct_change as pct_change
    from rolling_change

)

select * from final
order by granularity, period_start_date
