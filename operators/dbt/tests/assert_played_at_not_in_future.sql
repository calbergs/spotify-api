-- Fails if any listen is timestamped in the future, which would indicate a
-- clock-skew or timezone bug in the extraction/load pipeline rather than a
-- real play.
select *
from {{ ref('fct_listening_activity') }}
where played_at > current_timestamp
