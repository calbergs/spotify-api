"""
Flask app: Slack slash command /spotify and Events API for DMs/app mentions with conversation history.
"""
import hmac
import hashlib
import logging
import re
import threading
import time
from collections import OrderedDict
from urllib.parse import parse_qs

import requests
from flask import Flask, request

from .config import SLACK_SIGNING_SECRET, SLACK_BOT_TOKEN
from . import claude

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

MAX_HISTORY = 20
_conversations = OrderedDict()


def _conversation_key(channel: str, thread_ts: str = None):
    if thread_ts:
        return f"{channel}:{thread_ts}"
    return channel


def _get_history(key: str):
    return list(_conversations.get(key, []))


def _append_history(key: str, role: str, content: str):
    if key not in _conversations:
        _conversations[key] = []
    _conversations[key].append({"role": role, "content": content})
    _conversations[key] = _conversations[key][-MAX_HISTORY:]
    while len(_conversations) > 500:
        _conversations.popitem(last=False)


def verify_slack_request(body: bytes, timestamp: str, signature: str) -> bool:
    if not timestamp or not signature or not SLACK_SIGNING_SECRET:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
    except ValueError:
        return False
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    expected = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def post_answer(response_url: str, text: str):
    try:
        payload = {"text": text}
        if len(text) > 3900:
            payload["text"] = text[:3900] + "\n… (response truncated)"
        r = requests.post(response_url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        try:
            requests.post(response_url, json={"text": f"Error posting result: {e}"}, timeout=10)
        except Exception:
            pass


def post_message_to_slack(channel: str, text: str, thread_ts: str = None) -> bool:
    if not SLACK_BOT_TOKEN:
        logger.warning("SLACK_BOT_TOKEN not set; cannot post event reply")
        return False
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    if len(text) > 3900:
        payload["text"] = text[:3900] + "\n… (response truncated)"
    try:
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            logger.warning("chat.postMessage not ok: %s", r.text)
            return False
        return True
    except Exception as e:
        logger.exception("post_message_to_slack failed: %s", e)
        return False


@app.route("/slack/spotify", methods=["GET", "POST"])
def slack_spotify():
    if request.method == "GET":
        return {"ok": True, "message": "Use POST from Slack (slash command)."}, 200
    raw_body = request.get_data()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_request(raw_body, timestamp, signature):
        logger.warning("Slack request verification failed")
        return "", 403

    form = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    text = (form.get("text", [""])[0] or "").strip()
    response_url = (form.get("response_url", [""])[0] or "").strip()
    user_id = (form.get("user_id", [""])[0] or "").strip()

    if not response_url:
        logger.warning("Slack request missing response_url")
        return "Missing response_url", 400

    logger.info("Slack /spotify: %s", text[:80] if text else "(empty)")

    if not text:
        return {
            "response_type": "ephemeral",
            "text": "Ask something like: *Who are my top artists this month?* or *What genres did I listen to last week?* or *Recent listens*",
        }, 200

    slash_key = f"slash:{user_id}" if user_id else None

    def run():
        try:
            if slash_key:
                history = _get_history(slash_key)
                history.append({"role": "user", "content": text})
                _append_history(slash_key, "user", text)
                answer = claude.answer_question_with_history(history)
                _append_history(slash_key, "assistant", answer)
            else:
                answer = claude.answer_question(text)
            post_answer(response_url, answer)
        except Exception as e:
            logger.exception("Slack bot error")
            post_answer(response_url, f"Error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return {"response_type": "in_channel", "text": "Thinking…"}, 200


@app.route("/slack/events", methods=["POST"])
def slack_events():
    raw_body = request.get_data()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_request(raw_body, timestamp, signature):
        logger.warning("Slack events verification failed")
        return "", 403

    body = request.get_json(force=True, silent=True) or {}
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge", "")}, 200

    if body.get("type") != "event_callback":
        return "", 200

    event = body.get("event", {})
    if event.get("bot_id"):
        return "", 200

    if event.get("type") == "message" and event.get("channel_type") == "im":
        channel = event.get("channel")
        text = (event.get("text") or "").strip()
        if not text:
            return "", 200
        key = _conversation_key(channel)
        threading.Thread(target=_handle_event_message, args=(channel, None, key, text), daemon=True).start()
        return "", 200

    if event.get("type") == "app_mention":
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")
        text = re.sub(r"<@[A-Z0-9]+>", "", event.get("text") or "").strip()
        if not text:
            return "", 200
        key = _conversation_key(channel, thread_ts)
        threading.Thread(target=_handle_event_message, args=(channel, thread_ts, key, text), daemon=True).start()
        return "", 200

    return "", 200


def _handle_event_message(channel: str, thread_ts: str, key: str, text: str):
    try:
        history = _get_history(key)
        history.append({"role": "user", "content": text})
        _append_history(key, "user", text)
        reply = claude.answer_question_with_history(history)
        _append_history(key, "assistant", reply)
        post_message_to_slack(channel, reply, thread_ts)
    except Exception as e:
        logger.exception("Event message handling failed")
        post_message_to_slack(channel, f"Error: {e}", thread_ts)


if __name__ == "__main__":
    # 5003 to avoid clash with other apps (proxy forwards to this port)
    app.run(host="0.0.0.0", port=5003, debug=False)
