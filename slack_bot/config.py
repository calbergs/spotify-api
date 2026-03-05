"""
Load config from environment or operators.app_secrets (for Postgres).
Set SLACK_SIGNING_SECRET, SLACK_BOT_TOKEN, and ANTHROPIC_API_KEY in env or operators.app_secrets.
(Uses app_secrets to avoid shadowing Python's built-in 'secrets' module, which breaks numpy/pandas.)
"""
import os


def _get(name: str, default: str = "") -> str:
    v = os.environ.get(name)
    if v:
        return v
    try:
        from operators.app_secrets import __dict__ as s
        return str(s.get(name, default))
    except ImportError:
        return default


SLACK_SIGNING_SECRET = _get("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = _get("SLACK_BOT_TOKEN")
ANTHROPIC_API_KEY = _get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = _get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def get_pg_config():
    """Postgres config for Spotify DB (airflow DB with spotify_songs / spotify_genres). Env wins when set (e.g. in Docker)."""
    if os.environ.get("SPOTIFY_PG_HOST") or os.environ.get("PG_USER"):
        return {
            "host": os.environ.get("SPOTIFY_PG_HOST", "localhost"),
            "port": int(os.environ.get("SPOTIFY_PG_PORT", "5432")),
            "user": os.environ.get("PG_USER", "airflow"),
            "password": os.environ.get("PG_PASSWORD", "airflow"),
            "dbname": os.environ.get("PG_DATABASE", "airflow"),
        }
    try:
        from operators.app_secrets import host as pg_host, port as pg_port, pg_user, pg_password, dbname
        return {
            "host": pg_host,
            "port": int(pg_port) if isinstance(pg_port, str) else pg_port,
            "user": pg_user,
            "password": pg_password,
            "dbname": dbname,
        }
    except ImportError:
        return {
            "host": os.environ.get("SPOTIFY_PG_HOST", "localhost"),
            "port": int(os.environ.get("SPOTIFY_PG_PORT", "5432")),
            "user": os.environ.get("PG_USER", "airflow"),
            "password": os.environ.get("PG_PASSWORD", "airflow"),
            "dbname": os.environ.get("PG_DATABASE", "airflow"),
        }
