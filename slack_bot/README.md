# Spotify Slack bot

Ask questions about your Spotify listening history in Slack. The bot queries your Postgres `spotify_songs` and `spotify_genres` data and uses Claude to answer in plain language.

Example: `/spotify Who are my top artists this month?`

**Conversation history:** You can also DM the app or @mention it in a channel; the bot keeps the last 20 messages per conversation for follow-ups (e.g. "What about last year?"). See **Optional: Events API** below.

---

## 1. Prerequisites

- PostgreSQL with `spotify_songs` and `spotify_genres` populated (your Airflow Spotify DAG running).
- Python 3.9+ with dependencies below.

---

## 2. Install dependencies

From the **Spotify repo root**, with your virtualenv activated:

```bash
pip install flask anthropic requests psycopg2-binary
```

---

## 3. Slack app setup

1. Go to [Slack API – Your Apps](https://api.slack.com/apps) → **Create New App** → **From scratch**.
2. Name it (e.g. "Spotify") and pick your workspace.
3. **Slash Commands** → **Create New Command**:
   - Command: `/spotify`
   - Request URL: your public URL (see step 5) + `/slack/spotify`, e.g. `https://your-domain.com/slack/spotify`
   - Short description: `Ask questions about your Spotify listening history`
   - Usage hint: `Who are my top artists this month?`
4. **Basic Information** → **App Credentials**: copy **Signing Secret**.
5. **Install App** → Install to workspace. For **slash only** you don’t need a Bot token. For **DMs / @mentions**, copy the **Bot User OAuth Token** (`xoxb-...`).

---

## 4. Environment / config

The bot needs:

- **SLACK_SIGNING_SECRET** – From Slack app → Basic Information → App Credentials.
- **ANTHROPIC_API_KEY** – From [Anthropic Console](https://console.anthropic.com/).
- **SLACK_BOT_TOKEN** – (Optional, for DMs/@mentions.) Bot User OAuth Token after Install App.
- **Postgres** – Same as your Spotify pipeline. Either:
  - Use `operators/secrets.py` (with `host`, `port`, `pg_user`, `pg_password`, `dbname`), or
  - Set env: `SPOTIFY_PG_HOST`, `SPOTIFY_PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` (default `airflow`).

**Option A** – add to `operators/secrets.py` (gitignored):

```python
SLACK_SIGNING_SECRET = "your_signing_secret_here"
ANTHROPIC_API_KEY = "sk-ant-..."
SLACK_BOT_TOKEN = "xoxb-..."   # optional, for DMs / @mentions
# pg_* already there
```

**Option B** – export in the shell:

```bash
export SLACK_SIGNING_SECRET="..."
export ANTHROPIC_API_KEY="sk-ant-..."
export SPOTIFY_PG_HOST=localhost   # when running on your Mac
```

---

## 5. Expose your server to the internet

Slack must POST to your app. For local dev use [ngrok](https://ngrok.com/): `ngrok http 5050` and set the Slash Command Request URL to `https://xxxx.ngrok.io/slack/spotify`. For production, run on a server with HTTPS and set the URL to `https://your-domain.com/slack/spotify`.

---

## 6. Run the app

From the **Spotify repo root** (so `operators` and `slack_bot` are importable):

```bash
python -m slack_bot.app
```

Server listens on `http://0.0.0.0:5003` (port 5003; use the proxy + ngrok 5050 for one tunnel). In Slack:

```
/spotify Who are my top artists this month?
/spotify What genres did I listen to last week?
/spotify Recent listens
```

You’ll get “Thinking…” then the answer when Claude and the DB respond.

---

## Summary checklist

- [ ] Postgres has `spotify_songs` and `spotify_genres` (Airflow Spotify DAG).
- [ ] Dependencies installed (`flask`, `anthropic`, `requests`, `psycopg2-binary`).
- [ ] Slack app created; Slash Command `/spotify` with Request URL = `https://<your-public-host>/slack/spotify`.
- [ ] Signing Secret and Anthropic API key set (in `operators/secrets.py` or env).
- [ ] App running and reachable (ngrok or production).
- [ ] Test with `/spotify top artists this month`.

---

## Optional: Events API (conversation history)

To have the bot remember context when you **DM it** or **@mention it**:

1. **OAuth & Permissions** → add scopes **`chat:write`** and **`app_mentions:read`**. Reinstall and set **SLACK_BOT_TOKEN**.
2. **Event Subscriptions** → On → Request URL = `https://<your-public-host>/slack/events`.
3. **Subscribe to bot events**: **`message.im`**, **`app_mention`**.
4. Restart the app. DM or @mention the app and ask follow-ups; history is kept per conversation (last 20 messages).
