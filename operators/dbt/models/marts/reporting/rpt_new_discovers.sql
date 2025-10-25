{{
    config(
        materialized='view'
    )
}}

with listening_activity as (

    select * from {{ ref('fct_listening_activity') }}

),

curr_month as (
    select distinct
        artist_name,
        artist_id,
        count(artist_id) over (partition by artist_id) as times_listened,
        max(played_at) over (partition by artist_id) as last_listened_time
    from listening_activity
    where date_trunc('month', played_date) = date_trunc('month', current_date)
),

prev_month as (
    select distinct
        artist_name,
        artist_id
    from listening_activity
    where date_trunc('month', played_date) < date_trunc('month', current_date)
)

select
	curr_month.artist_name,
	curr_month.artist_id,
	curr_month.times_listened,
	curr_month.last_listened_time,
	case when last_listened_time >= date_trunc('week', current_date) then last_listened_time
		else date_trunc('week', last_listened_time) + interval '6 day'
	end as current_week
from curr_month
left join prev_month using (artist_id)
where prev_month.artist_id is null