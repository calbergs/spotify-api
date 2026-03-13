"""
Send a weekly Spotify listening summary to Slack.

Intended to be called from Airflow (or manually):

    cd /path/to/spotify-api && PYTHONPATH=/path/to/spotify-api python -m slack_bot.weekly_summary

Uses the same Claude + Postgres logic as the Slack bot and posts to a configured channel.
"""
import os
import sys
from datetime import datetime

from .claude import answer_question
from .app import post_message_to_slack
from .config import SLACK_BOT_TOKEN


def _as_central(dt: datetime) -> datetime:
    """Convert a naive/UTC datetime to America/Chicago for gating."""
    try:
        import pendulum

        central = pendulum.timezone("America/Chicago")
        if getattr(dt, "tzinfo", None):
            return dt.astimezone(central)
        return pendulum.instance(dt).in_timezone(central)
    except Exception:
        return dt


def should_send_now(dt: datetime) -> bool:
    """
    Gate sending to Monday morning in Central time.

    - Only send on Monday (weekday() == 0).
    - Only send before 12:00 *Central* so we don't send twice if the DAG runs multiple times.
    """
    ct = _as_central(dt)
    return ct.weekday() == 0 and ct.hour < 12


def send_weekly_summary() -> None:
    """
    Ask Claude for the previous week's listening summary and post it to Slack.

    Channel is controlled via SPOTIFY_SLACK_CHANNEL (e.g. "#general" or a channel ID).
    """
    channel = os.environ.get("SPOTIFY_SLACK_CHANNEL", "#general")

    if not SLACK_BOT_TOKEN:
        print("ERROR: SLACK_BOT_TOKEN is not set. Set it in operators/app_secrets or env.", file=sys.stderr)
        sys.exit(1)

    print(f"Sending weekly Spotify summary to channel: {channel}", flush=True)
    question = (
        "Give me my Spotify listening summary for the previous week (Monday through Sunday). "
        "Include: total listens, top artists, top songs, top genres, and any notable trends. "
        "Use clear headings and plain text tables (code blocks) with aligned columns."
    )

    answer = answer_question(question)
    ok = post_message_to_slack(channel, answer)
    if not ok:
        print("ERROR: Failed to post message to Slack.", file=sys.stderr)
        sys.exit(1)
    print("Weekly Spotify summary sent successfully.", flush=True)


if __name__ == "__main__":
    send_weekly_summary()
