"""The only place devour talks to treg.to, the paid fallback when yt-dlp is blocked.
The token goes only to endpoint ids on the allow-list below, because treg's /call/ route
forwards headers to whatever it is pointed at. Redirects are refused for the same reason.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://treg.to/call/"
WORKSPACE_ENV = Path.home() / "Documents" / "Projects" / ".env"

# id -> (HTTP method, price per call in USD), checked against the treg catalog on 2026-11-07.
ENDPOINTS = {
    "scrapecreators.x.v1-youtube-channel-videos": ("GET", 0.00188),
    "crawl4ai.youtube.channel.videos": ("POST", 0.0009),
    "scrapecreators.x.v1-youtube-video-transcript": ("GET", 0.00188),
    "anyapi.youtube.video_transcript_full": ("POST", 0.00308),
    "tikhub.x.youtube-web-v2-get-video-captions": ("GET", 0.008),
}


class TregError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.out_of_funds = status == 402


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise TregError("treg answered with a redirect; refusing to follow it with the token attached")


def find_token():
    """TREG_TOKEN wins; otherwise use TREG_API_KEY from the environment or the workspace .env."""
    token = os.environ.get("TREG_TOKEN") or os.environ.get("TREG_API_KEY")
    if token or not WORKSPACE_ENV.exists():
        return token
    for line in WORKSPACE_ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("TREG_API_KEY="):
            return line.split("=", 1)[1].strip().strip("\"'")
    return None


def available():
    return bool(find_token())


def build_url(endpoint_id, params, method):
    if endpoint_id not in ENDPOINTS or not re.fullmatch(r"[a-z0-9_.-]+", endpoint_id):
        raise TregError(f"Refusing to send the treg token to non-catalog endpoint: {endpoint_id!r}")
    url = BASE + endpoint_id
    if method == "GET" and params:
        url += "?" + urllib.parse.urlencode(params)
    return url


def call(endpoint_id, params):
    if endpoint_id not in ENDPOINTS:
        raise TregError(f"Refusing to send the treg token to non-catalog endpoint: {endpoint_id!r}")
    method = ENDPOINTS[endpoint_id][0]
    token = find_token()
    if not token:
        raise TregError("no treg key found (TREG_TOKEN, or TREG_API_KEY in the workspace .env)")
    url = build_url(endpoint_id, params, method)
    headers = {"X-Treg-Token": token, "Accept": "application/json", "User-Agent": "devour-skill"}
    body = None
    if method == "POST":
        body = json.dumps(params).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        raise TregError(f"{endpoint_id} answered HTTP {error.code}: {detail}", status=error.code) from error
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise TregError(f"{endpoint_id} failed: {error}") from error
