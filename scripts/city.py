"""Render the last year of GitHub contributions as a small isometric city.

    python scripts/city.py --login medwinjose          # live data (GITHUB_TOKEN optional)
    python scripts/city.py --demo                      # synthetic placeholder

Each day is a city block; the taller the building, the more was committed that day.
Writes assets/city-dark.svg and assets/city-light.svg. Rebuilt every few minutes by
.github/workflows/city.yml.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import re
import sys
import urllib.request

from svgkit import EASE_OUT, THEMES, Doc, diamond, fmt

W, SCENE_H = 840, 416
CAPTION_H = 31     # caption line set inside the image, so it never reflows with the window
H = SCENE_H + CAPTION_H
CAPTION = ("Each building is one day; its height is that day's contributions. "
           "Rebuilt every few minutes from my GitHub activity.")
U = (12.2, 3.55)    # screen offset of one week step
V = (-10.4, 5.25)   # screen offset of one weekday step
MAX_H = 112
LOOP = 7            # seconds per rebuild cycle of the skyline
GAP = 0.13          # inset of each building inside its block

# restrictedContributionsCount = private contributions the token cannot see in
# detail; they are still included in the calendar counts when the profile shows
# private contributions, or fully visible when the token belongs to the user.
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  restrictedContributionsCount contributionCalendar {
  totalContributions weeks { contributionDays { date contributionCount weekday } } } } } }"""


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def fetch_graphql(login: str, token: str) -> list[tuple[dt.date, int]]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "city"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GraphQL error"))
    coll = payload["data"]["user"]["contributionsCollection"]
    cal = coll["contributionCalendar"]
    print(f"calendar: {cal['totalContributions']} contributions in the last year "
          f"(of which private/restricted: {coll['restrictedContributionsCount']})", file=sys.stderr)
    weeks = cal["weeks"]
    return [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def fetch_html(login: str) -> list[tuple[dt.date, int]]:
    """Fallback: the public contributions fragment (levels + tooltip counts)."""
    req = urllib.request.Request(f"https://github.com/users/{login}/contributions", headers={"User-Agent": "city"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode()
    days = {}
    for cell in re.finditer(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"[^>]*data-level="(\d)"', html):
        days[cell.group(2)] = (dt.date.fromisoformat(cell.group(1)), int(cell.group(3)))
    counts = {}
    for tip in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"(\d+|No) contribution", tip.group(2).strip())
        if m:
            counts[tip.group(1)] = 0 if m.group(1) == "No" else int(m.group(1))
    out = [(d, counts.get(k, lvl * 3)) for k, (d, lvl) in days.items()]
    if not out:
        raise RuntimeError("could not parse contributions page")
    return sorted(out)


def demo_data() -> list[tuple[dt.date, int]]:
    rng = random.Random(42)
    end = dt.date.today()
    start = end - dt.timedelta(days=end.weekday() + 1 + 52 * 7)  # a Sunday
    out = []
    for i in range((end - start).days + 1):
        d = start + dt.timedelta(days=i)
        season = .55 + .45 * math.sin(i / 365 * 2 * math.pi * 1.6 + 1)
        busy = rng.random() < (.32 + .5 * season) * (.55 if d.weekday() >= 5 else 1)
        out.append((d, int(rng.expovariate(1 / (2 + 9 * season))) + 1 if busy else 0))
    return out


# --------------------------------------------------------------------------
# Statistics for the captions
# --------------------------------------------------------------------------
def stats(days: list[tuple[dt.date, int]]) -> dict:
    total = sum(c for _, c in days)
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    best_day, best = max(days, key=lambda x: x[1])
    by_wd = [0] * 7
    for d, c in days:
        by_wd[d.weekday()] += c
    weekday = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"][by_wd.index(max(by_wd))]
    active = sum(1 for _, c in days if c)
    return dict(total=total, longest=longest, best_day=best_day, best=best, weekday=weekday, active=active)


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def shade(hex_color: str, k: float) -> str:
    """k < 0 darkens towards black, k > 0 lightens towards white."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if k < 0:
        r, g, b = (int(c * (1 + k)) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * k) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def poly(points, fill, extra="") -> str:
    pts = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" {extra}/>'


PALETTE = {
    # tiers 1..4 (top-face colours); sides are derived by shading
    "dark": ["#4D4A7E", "#7C78D8", "#ADA6FF", "#FFB4C8"],
    "light": ["#DEDBF8", "#BBB5F3", "#8F86E8", "#EE8CAC"],
}


def stars(t: dict, mx: float, my: float, count: int = 30) -> list:
    """A sky of faint stars, each blinking on its own slow rhythm. Seeded, so the
    sky stays the same between rebuilds; kept clear of the moon, the figures
    block (top right) and the skyline (which slopes down to the right)."""
    rng, out, tries, placed = random.Random(2026), [], 0, []
    while len(out) < count and tries < 4000:
        tries += 1
        x, y = rng.uniform(16, W - 16), rng.uniform(6, 150)
        if x > W - 300 and y < 172:                 # figures block
            continue
        if (x - mx) ** 2 + (y - my) ** 2 < 46 ** 2:  # moon and halo
            continue
        if y > 40 + max(0.0, x - 120) * .3:          # stay above the tallest possible rooftops
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 38 ** 2 for px, py in placed):  # even spacing, no clumps
            continue
        placed.append((x, y))
        r = rng.choice([.6, .7, .8, .9, 1.1, 1.3])
        dur, delay = rng.uniform(4.5, 9), rng.uniform(0, 8)
        out.append(f'<circle class="star" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{t["butter"]}" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>')
    return out


def render(days: list[tuple[dt.date, int]], theme: str, live: bool) -> Doc:
    t = THEMES[theme]
    tiers = PALETTE[theme]
    first = days[0][0]
    first_sunday = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    cells = []
    for d, c in days:
        offset = (d - first_sunday).days
        cells.append((offset // 7, offset % 7, d, c))
    weeks = max(w for w, *_ in cells) + 1

    counts = sorted(c for *_, c in cells if c)
    cap = counts[int(len(counts) * .96) - 1] if counts else 1
    q = [counts[int(len(counts) * f)] if counts else 1 for f in (.3, .62, .92)]

    def height(c):
        return 0 if c == 0 else 7 + (MAX_H - 7) * min(1, c / max(cap, 1)) ** .62

    def tier(c):
        return sum(c > x for x in q)

    span_x = weeks * U[0] - 7 * V[0]
    ox = (W - span_x) / 2 - 7 * V[0] + 6
    oy = SCENE_H - (weeks * U[1] + 7 * V[1]) - 25

    def P(a, b, z=0.0):
        return ox + a * U[0] + b * V[0], oy + a * U[1] + b * V[1] - z

    s = stats(days)
    title = (f"Contribution city: {s['total']:,} contributions in the last year, one building per day"
             if live else "Contribution city: one building per day of the last year")
    doc = Doc(W, H, title)
    doc.css.append(f"""
/* An image can't tell when it is scrolled into view, so the city rebuilds on a
   slow loop: every {LOOP}s the buildings settle and rise again, one by one,
   left to right, and a visitor always catches it building within seconds. */
.b   {{ transform-box: fill-box; transform-origin: 50% 100%; animation: build {LOOP}s linear infinite both; }}
@keyframes build {{
  0%   {{ transform: scaleY(0); opacity: 0; animation-timing-function: cubic-bezier(.2,.8,.25,1) }}
  3%   {{ opacity: 1 }}
  11%  {{ transform: scaleY(1); opacity: 1 }}
  88%  {{ transform: scaleY(1); opacity: 1; animation-timing-function: cubic-bezier(.5,0,.75,0) }}
  96%, 100% {{ transform: scaleY(0); opacity: 0 }} }}
.g   {{ animation: fade 1.4s ease-out both; }}
.tw  {{ animation: twinkle ease-in-out infinite; }}
@keyframes twinkle {{ 0%, 100% {{ opacity: .15 }} 45%, 60% {{ opacity: .95 }} }}
.cap {{ animation: rise 1.4s {EASE_OUT} 2.4s both; }}
.moon {{ animation: fade 2s ease-out 2s both; }}
.halo {{ transform-box: fill-box; transform-origin: center; animation: fade 2s ease-out 1s both, halo 6s ease-in-out 3s infinite; }}
@keyframes halo {{ 0%, 100% {{ opacity: .45; transform: scale(1) }} 50% {{ opacity: .85; transform: scale(1.12) }} }}
.star {{ animation: twinkle ease-in-out infinite; }}
""")
    rng = random.Random(7)

    # Moon (dark) or a faint sun (light), top-left above the oldest weeks.
    mx, my = 74, 38  # halo (r 30, breathing to x1.12) clears the top edge
    if theme == "dark":
        doc.defs.append(f'<radialGradient id="glow"><stop offset="0" stop-color="{t["butter"]}" stop-opacity=".35"/>'
                        f'<stop offset="1" stop-color="{t["butter"]}" stop-opacity="0"/></radialGradient>'
                        f'<mask id="cres"><rect width="{W}" height="{H}" fill="#fff"/>'
                        f'<circle cx="{mx + 7}" cy="{my - 5}" r="12.5" fill="#000"/></mask>')
        doc.add(*stars(t, mx, my))
        doc.add(f'<circle class="halo" cx="{mx}" cy="{my}" r="30" fill="url(#glow)"/>',
                f'<circle class="moon" cx="{mx}" cy="{my}" r="13" fill="{t["butter"]}" mask="url(#cres)" opacity=".9"/>')
    else:
        doc.defs.append(f'<radialGradient id="glow"><stop offset="0" stop-color="{t["butter"]}" stop-opacity=".55"/>'
                        f'<stop offset="1" stop-color="{t["butter"]}" stop-opacity="0"/></radialGradient>')
        doc.add(f'<circle class="halo" cx="{mx}" cy="{my}" r="30" fill="url(#glow)"/>',
                f'<circle class="moon" cx="{mx}" cy="{my}" r="12" fill="{t["butter"]}" opacity=".5"/>')

    # Ground: every day is a block, drawn once as a faint tile.
    ground = []
    for w, wd, _, _ in cells:
        a0, b0, a1, b1 = w + GAP, wd + GAP, w + 1 - GAP, wd + 1 - GAP
        ground.append(poly([P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)], t["ink"], 'fill-opacity=".055"'))
    doc.add(f'<g class="g">{"".join(ground)}</g>')

    # Month names along the front edge.
    seen = set()
    for w, wd, d, _ in cells:
        if wd == 0 and d.day <= 7 and d.month not in seen and 0 < w < weeks - 1:
            seen.add(d.month)
            x, y = P(w + .5, 7.9)
            doc.add(doc.text(x, y + 10, d.strftime("%b").upper(), "sans-m", 7.5, t["muted"], anchor="middle",
                             tracking=1.6, cls="g", style="animation-delay:.6s"))

    # Buildings, painted back to front.
    for w, wd, d, c in sorted(cells, key=lambda x: (x[0] + x[1], x[0])):
        h = height(c)
        if not h:
            continue
        base = tiers[tier(c)]
        top_c = base
        right_c = shade(base, -.38 if theme == "dark" else -.22)
        left_c = shade(base, -.2 if theme == "dark" else -.1)
        a0, b0, a1, b1 = w + GAP, wd + GAP, w + 1 - GAP, wd + 1 - GAP
        faces = [
            poly([P(a0, b1), P(a1, b1), P(a1, b1, h), P(a0, b1, h)], left_c),    # faces +weekday (front-left)
            poly([P(a1, b0), P(a1, b1), P(a1, b1, h), P(a1, b0, h)], right_c),   # faces +week (front-right)
            poly([P(a0, b0, h), P(a1, b0, h), P(a1, b1, h), P(a0, b1, h)], top_c),
        ]
        windows = []
        if h > 24:
            for z in range(10, int(h) - 6, 8):
                for frac in (.3, .68):
                    bb = b0 + (b1 - b0) * frac
                    quad = [P(a1, bb - .1, z), P(a1, bb + .1, z), P(a1, bb + .1, z + 3.2), P(a1, bb - .1, z + 3.2)]
                    lit = rng.random()
                    if lit < .5:
                        continue
                    cls, sty = "", ""
                    if lit > .9:
                        cls = ' class="tw"'
                        sty = f' style="animation-duration:{rng.uniform(5, 11):.1f}s;animation-delay:{rng.uniform(3, 12):.1f}s"'
                    windows.append(poly(quad, t["window"], f'fill-opacity="{.75 if theme == "dark" else .9}"{cls}{sty}'))
        delay = .3 + w * .036 + wd * .012  # sweeps left to right, one building after another
        doc.add(f'<g class="b" style="animation-delay:{delay:.2f}s">{"".join(faces)}{"".join(windows)}</g>')

    # Captions: headline figure top-right, small ledger beneath it.
    rx = W - 40
    doc.add('<g class="cap">')
    if live:
        doc.add(doc.text(rx, 32, f"{s['total']:,}", "serif-b", 44, t["ink"], anchor="end"),
                doc.text(rx, 54, "contributions in the last year", "serif-i", 16.5, t["soft"], anchor="end"))
        ledger = [("LONGEST STREAK", f"{s['longest']} days"),
                  ("BUSIEST DAY", f"{s['best_day'].strftime('%-d %b')} · {s['best']}"),
                  ("MOST ACTIVE ON", s["weekday"])]
        for i, (k, v) in enumerate(ledger):
            y = 88 + i * 22
            doc.add(doc.text(rx - 112, y, k, "sans-m", 8, t["muted"], anchor="end", tracking=1.8),
                    diamond(rx - 100, y - 3, 1.6, fill=t["blush"]),
                    doc.text(rx, y, v, "serif", 15.5, t["ink"], anchor="end"))
    else:
        doc.add(doc.text(rx, 26, "One building for every day.", "serif-i", 19, t["soft"], anchor="end"),
                doc.text(rx, 50, "REBUILT FROM THE CONTRIBUTION GRAPH", "sans-m", 8, t["muted"], anchor="end",
                         tracking=1.8))
    doc.add("</g>")

    # Legend, bottom-left.
    lx, ly = 40, SCENE_H - 6
    doc.add('<g class="cap">', doc.text(lx, ly, "QUIET", "sans-m", 7.5, t["muted"], tracking=1.6))
    x = lx + 42
    for i, col in enumerate(tiers):
        hh = 5 + i * 3.5
        doc.add(f'<rect x="{fmt(x)}" y="{fmt(ly - hh + 1)}" width="7" height="{fmt(hh)}" rx="1" fill="{col}"/>')
        x += 11
    doc.add(doc.text(x + 6, ly, "BUSY", "sans-m", 7.5, t["muted"], tracking=1.6), "</g>")
    doc.add('<g class="cap">', doc.text(W / 2, SCENE_H + 22, CAPTION, "serif-i", 15.5, t["soft"], anchor="middle"), "</g>")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "medwinjose"))
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default=None, help="output directory (default: assets/)")
    args = ap.parse_args()

    live = not args.demo
    if args.demo:
        days = demo_data()
    else:
        token = os.environ.get("GITHUB_TOKEN")
        try:
            if not token:
                raise RuntimeError("GITHUB_TOKEN not set")
            days = fetch_graphql(args.login, token)
        except Exception as exc:  # noqa: BLE001 - fall back to the public page
            print(f"GraphQL unavailable ({exc}); falling back to HTML", file=sys.stderr)
            days = fetch_html(args.login)
    days = sorted(days)[-371:]
    for theme in THEMES:
        doc = render(days, theme, live)
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, f"city-{theme}.svg"), "w", encoding="utf-8") as fh:
                fh.write(doc.render())
        else:
            doc.save(f"city-{theme}.svg")
    print(f"rendered {len(days)} days, {sum(c for _, c in days)} contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
