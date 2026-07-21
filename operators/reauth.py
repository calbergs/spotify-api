#!/usr/bin/env python3
"""
Re-authorize with Spotify after the refresh token expires or is revoked.

Spotify refresh tokens now expire after 6 months of inactivity (policy
change effective July 2026, see api.spotify.com token refresh docs). When
that happens, refresh.py's error tells you to run this script.

Walks through the OAuth authorization-code flow interactively and writes
the new access_token/refresh_token back into spotify_secrets.py.
"""
import base64
import re
import sys
from urllib.parse import urlencode, urlparse, parse_qs

import requests

from spotify_secrets import base_64

SCOPE = "user-read-recently-played user-library-read"
SECRETS_FILE = "spotify_secrets.py"  # run from operators/


def client_id_from_base64(b64: str) -> str:
    return base64.b64decode(b64).decode().split(":", 1)[0]


def build_authorize_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPE,
    }
    return "https://accounts.spotify.com/authorize?" + urlencode(params)


def extract_code(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("http"):
        qs = parse_qs(urlparse(raw).query)
        if "code" not in qs:
            print("ERROR: no 'code' param found in that URL.", file=sys.stderr)
            sys.exit(1)
        return qs["code"][0]
    return raw  # assume they pasted the bare code value


def exchange_code(code: str, redirect_uri: str) -> dict:
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={"Authorization": "Basic " + base_64},
    )
    if resp.status_code != 200:
        print(f"ERROR: token exchange failed {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json()


def write_secrets(access_token: str, refresh_token: str) -> None:
    with open(SECRETS_FILE) as f:
        content = f.read()
    content, n1 = re.subn(r"spotify_token = '.*?'", f"spotify_token = '{access_token}'", content)
    content, n2 = re.subn(r"refresh_token = '.*?'", f"refresh_token = '{refresh_token}'", content)
    if n1 != 1 or n2 != 1:
        print(
            f"ERROR: expected exactly one spotify_token/refresh_token literal in {SECRETS_FILE}, "
            f"found {n1}/{n2}. Not overwriting — update it manually with the values below:",
            file=sys.stderr,
        )
        print(f"spotify_token = '{access_token}'")
        print(f"refresh_token = '{refresh_token}'")
        sys.exit(1)
    with open(SECRETS_FILE, "w") as f:
        f.write(content)
    print(f"Wrote new access_token and refresh_token into {SECRETS_FILE}")


def main():
    redirect_uri = input(
        "Redirect URI registered for this app (Spotify dashboard > your app > "
        "Settings > Redirect URIs): "
    ).strip()
    client_id = client_id_from_base64(base_64)
    url = build_authorize_url(client_id, redirect_uri)

    print("\nOpen this URL in a browser logged into the Spotify account to authorize, then click Agree:\n")
    print(url)

    raw = input(
        "\nAfter approving, the browser will redirect (the page may fail to "
        "load — that's fine). Paste the FULL URL from the address bar here "
        "(or just the 'code=' value): "
    ).strip()
    code = extract_code(raw)

    tokens = exchange_code(code, redirect_uri)
    write_secrets(tokens["access_token"], tokens["refresh_token"])
    print("\nDone. Re-run the pipeline (python3 main.py) to confirm it works.")


if __name__ == "__main__":
    main()
