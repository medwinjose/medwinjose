"""Live contribution city, rendered on request (Vercel serverless function).

GET /api/city?theme=dark|light  ->  image/svg+xml

Reads the contribution calendar at request time, so a new commit shows up in
the city within about a minute instead of waiting for the hourly Action.
Responses are cached at the edge for 30 seconds to stay well inside GitHub's
API rate limits. Environment variables:

    GITHUB_TOKEN  a personal access token (no scopes needed; add `read:user`
                  to include private contributions you've chosen to show)
    CITY_LOGIN    GitHub username to draw (default: medwinjose)
"""

from __future__ import annotations

import os
import sys
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import city  # noqa: E402

_cache: dict = {}
FRESH_FOR = 30  # seconds a warm instance reuses the last calendar it fetched


def contribution_days() -> list:
    now = time.time()
    if _cache.get("days") and now - _cache["at"] < FRESH_FOR:
        return _cache["days"]
    login = os.environ.get("CITY_LOGIN", "medwinjose")
    token = os.environ.get("GITHUB_TOKEN")
    try:
        days = city.fetch_graphql(login, token) if token else city.fetch_html(login)
    except Exception:  # noqa: BLE001 - keep serving the last good city if GitHub hiccups
        if _cache.get("days"):
            return _cache["days"]
        days = city.fetch_html(login)
    _cache.update(days=sorted(days)[-371:], at=now)
    return _cache["days"]


class handler(BaseHTTPRequestHandler):  # noqa: N801 - name required by Vercel
    def do_GET(self) -> None:  # noqa: N802
        theme = parse_qs(urlparse(self.path).query).get("theme", ["dark"])[0]
        if theme not in city.THEMES:
            theme = "dark"
        try:
            body = city.render(contribution_days(), theme, True).render().encode()
            status = 200
        except Exception as exc:  # noqa: BLE001
            body = f"city unavailable: {exc}".encode()
            status = 503
        self.send_response(status)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8" if status == 200 else "text/plain")
        self.send_header("Cache-Control", "public, max-age=0, s-maxage=30, stale-while-revalidate=60")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
