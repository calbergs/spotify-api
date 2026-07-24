-- Fails if any listen has a non-positive duration, which indicates a
-- malformed extraction (e.g. a bad Spotify API response) rather than a
-- real song -- not_null alone wouldn't catch a bad zero/negative value.
select *
from {{ ref('fct_listening_activity') }}
where song_duration_mins <= 0
