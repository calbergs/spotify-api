{{
    config(
        materialized='view'
    )
}}

with listening_activity as (

    select * from {{ ref('fct_listening_activity') }}

),

curr as (

	select distinct
		artist_name,
		artist_id,
		count(artist_id) over(partition by artist_id) as times_listened,
		max(played_at) over (partition by artist_id) as last_listened_time

	from analytical.fct_listening_activity

	where cast(date_trunc('week', played_date + interval '1 day') - interval '1 day' as date) = cast(date_trunc('week', current_date + interval '1 day') - interval '1 day' as date)
)

,prev as (

	select distinct
		artist_name,
		artist_id

	from analytical.fct_listening_activity

	where cast(date_trunc('week', played_date + interval '1 day') - interval '1 day' as date) < cast(date_trunc('week', current_date + interval '1 day') - interval '1 day' as date) 
)

,final as (

	select
		curr.artist_name,
		times_listened,
		row_number() over (order by times_listened desc, last_listened_time desc) as rnk

	from curr

	left join prev
        on curr.artist_id = prev.artist_id

	where prev.artist_id is null
)

select
	artist_name,
	times_listened

from final

order by rnk
