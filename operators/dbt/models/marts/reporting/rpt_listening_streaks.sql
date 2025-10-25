{{
    config(
        materialized='view'
    )
}}

WITH listening_activity AS (
    SELECT * 
    FROM {{ ref('fct_listening_activity') }}
),

listened_dates AS (
    SELECT DISTINCT played_date
    FROM listening_activity
),

date_diffs AS (
    SELECT
        played_date,
        LAG(played_date) OVER (ORDER BY played_date) AS prev_date,
        played_date - LAG(played_date) OVER (ORDER BY played_date) AS date_diff
    FROM listened_dates
),

streak_groups AS (
    SELECT
        played_date,
        SUM(CASE WHEN date_diff > 1 OR date_diff IS NULL THEN 1 ELSE 0 END)
            OVER (ORDER BY played_date ROWS UNBOUNDED PRECEDING) AS streak_group
    FROM date_diffs
),

streak_lengths AS (
    SELECT
        streak_group,
        MIN(played_date) AS streak_start,
        MAX(played_date) AS streak_end,
        COUNT(*) AS streak_length
    FROM streak_groups
    GROUP BY streak_group
),

latest_streak AS (
    SELECT *
    FROM streak_lengths
    WHERE streak_end = (SELECT MAX(played_date) FROM listened_dates)
)

SELECT *
FROM latest_streak