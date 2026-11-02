"""Build every static SVG used by the profile README (dark + light variants).

    python scripts/build_assets.py

The contribution city is built separately by scripts/city.py (nightly action).
"""

from __future__ import annotations

import math
import random

from svgkit import EASE_OUT, THEMES, Doc, arrow, arrow_ne, diamond, fmt, measure, wrap

W = 840  # Matches the README column; images scale down on smaller screens.


# ==========================================================================
# Masthead
# ==========================================================================
def header(t: dict, theme: str) -> None:
    d = Doc(W, 268, "Medwin Jose — distributed systems research and engineering")
    cx = W / 2
    d.css.append(f"""
.k  {{ animation: fade 1.4s ease-out .1s both; }}
.nm {{ animation: rise 1.8s {EASE_OUT} .25s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.6s {EASE_OUT} 1s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.6s {EASE_OUT} 1s both; }}
.dm {{ transform-box: fill-box; transform-origin: center; animation: fade 1s ease-out 1.5s both, breathe 5s ease-in-out 2.5s infinite; }}
.tl {{ opacity: 0; animation: cycle 13.5s ease-in-out infinite both; }}
.t1 {{ opacity: 1; animation-delay: 1.9s; }} .t2 {{ animation-delay: 6.4s; }} .t3 {{ animation-delay: 10.9s; }}
@keyframes cycle {{ 0% {{ opacity: 0; transform: translateY(5px) }} 5% {{ opacity: 1; transform: none }}
  29% {{ opacity: 1; transform: none }} 33.3% {{ opacity: 0; transform: translateY(-4px) }} 100% {{ opacity: 0 }} }}
@media (prefers-reduced-motion: reduce) {{ .t2, .t3 {{ display: none }} }}
.mt {{ animation: fade 1.6s ease-out 2.3s both; }}
""")
    # Kicker flanked by small diamonds.
    kick = "THE PORTFOLIO OF"
    kw = measure("sans-m", kick, 10.5, 5)
    d.add('<g class="k">',
          d.text(cx, 52, kick, "sans-m", 10.5, t["gold"], anchor="middle", tracking=5),
          diamond(cx - kw / 2 - 18, 48.5, 2.6, fill=t["gold"]),
          diamond(cx + kw / 2 + 18, 48.5, 2.6, fill=t["gold"]),
          "</g>")

    # Name, with an occasional champagne sheen passing across it.
    name = "MEDWIN JOSE"
    d.defs.append(
        f'<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-260" y1="0" x2="-60" y2="0">'
        f'<stop offset="0" stop-color="{t["gold_hi"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["gold_hi"]}" stop-opacity=".75"/>'
        f'<stop offset="1" stop-color="{t["gold_hi"]}" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1250 0;1250 0" '
        f'keyTimes="0;.22;1" dur="11s" begin="2.6s" repeatCount="indefinite"/></linearGradient>'
    )
    d.add('<g class="nm">',
          d.text(cx, 128, name, "serif", 70, t["ink"], anchor="middle", tracking=17),
          d.text(cx, 128, name, "serif", 70, "url(#sheen)", anchor="middle", tracking=17),
          "</g>")

    # Hairline that draws outward from a central diamond.
    y = 158
    d.add(f'<line class="rl" x1="262" y1="{y}" x2="{cx - 14}" y2="{y}" stroke="{t["gold"]}" stroke-width=".8" opacity=".7"/>',
          f'<line class="rr" x1="{cx + 14}" y1="{y}" x2="{W - 262}" y2="{y}" stroke="{t["gold"]}" stroke-width=".8" opacity=".7"/>',
          f'<g class="dm">{diamond(cx, y, 4.2, stroke=t["gold"], sw=.9)}{diamond(cx, y, 1.6, fill=t["gold"])}</g>')

    # Rotating standfirst.
    lines = [
        "Building systems that stay correct when participants misbehave.",
        "Peer-to-peer protocols, adversarial markets, payment networks.",
        "Every claim backed by a benchmark you can rerun.",
    ]
    for i, line in enumerate(lines, 1):
        d.add(f'<g class="tl t{i}">', d.text(cx, 201, line, "serif-i", 23.5, t["soft"], anchor="middle"), "</g>")

    d.add('<g class="mt">',
          d.text(cx, 242, "B.TECH COMPUTER SCIENCE  ·  VIT BHOPAL UNIVERSITY  ·  INDIA", "sans-m", 10, t["muted"],
                 anchor="middle", tracking=3.2),
          "</g>")
    d.save(f"header-{theme}.svg")


# ==========================================================================
# Availability pill and link chips
# ==========================================================================
def status(t: dict, theme: str) -> None:
    label = "OPEN TO FULLY FUNDED DIRECT-PHD POSITIONS  ·  RESEARCH INTERNSHIPS"
    tw = measure("sans-m", label, 10.5, 1.9)
    pw, ph = tw + 64, 34
    d = Doc(W, 50, "Open to fully funded direct-PhD positions and research internships")
    x0, y0 = (W - pw) / 2, 8
    d.css.append("""
.pl { animation: fade 1.4s ease-out 2.4s both; }
.ping { transform-box: fill-box; transform-origin: center; animation: ping 2.8s cubic-bezier(0,0,.2,1) 3s infinite both; }
@keyframes ping { 0% { transform: scale(1); opacity: .7 } 75%, 100% { transform: scale(3.4); opacity: 0 } }
""")
    dx, dy = x0 + 24, y0 + ph / 2
    d.add('<g class="pl">',
          f'<rect x="{fmt(x0)}" y="{y0}" width="{fmt(pw)}" height="{ph}" rx="{ph / 2}" fill="{t["surface"]}" stroke="{t["border"]}"/>',
          f'<circle class="ping" cx="{fmt(dx)}" cy="{fmt(dy)}" r="3.2" fill="{t["sage"]}"/>',
          f'<circle cx="{fmt(dx)}" cy="{fmt(dy)}" r="3.2" fill="{t["sage"]}"/>',
          d.text(dx + 16, dy + 3.8, label, "sans-m", 10.5, t["soft"], tracking=1.9),
          "</g>")
    d.save(f"status-{theme}.svg")


CHIPS = [
    ("preprint", "CRCI PREPRINT", .0),
    ("linkedin", "LINKEDIN", .12),
    ("demo", "TRACEFLUX LIVE DEMO", .24),
]


def chip(t: dict, theme: str, key: str, label: str, delay: float) -> None:
    tw = measure("sans-m", label, 10, 2.2)
    w, h = tw + 58, 36
    d = Doc(int(math.ceil(w)) + 4, h + 4, label.title())
    d.css.append(f"""
.c {{ animation: rise 1.2s {EASE_OUT} {2.6 + delay}s both; }}
.ar {{ animation: nudge 6s ease-in-out {4 + delay * 4}s infinite; }}
@keyframes nudge {{ 0%, 86%, 100% {{ transform: none }} 92% {{ transform: translate(2px,-2px) }} }}
""")
    d.add('<g class="c">',
          f'<rect x="2" y="2" width="{fmt(w)}" height="{h}" rx="{h / 2}" fill="none" stroke="{t["border"]}"/>',
          d.text(24, 2 + h / 2 + 3.6, label, "sans-m", 10, t["soft"], tracking=2.2),
          f'<g class="ar">{arrow_ne(24 + tw + 10, 2 + h / 2 - 4, 8, t["gold"], 1.1)}</g>',
          "</g>")
    d.save(f"link-{key}-{theme}.svg")


# ==========================================================================
# Monogram seal (one file; mid-tone gold reads on both themes)
# ==========================================================================
def seal() -> None:
    gold = "#B8975A"
    S = 300
    d = Doc(S + 26, S, "MJ monogram")  # right padding keeps text off the seal
    c = S / 2
    d.css.append("""
.spin { transform-box: view-box; transform-origin: 150px 150px; animation: spin 80s linear infinite; }
.orb  { transform-box: view-box; transform-origin: 150px 150px; animation: spin 24s linear infinite reverse; }
@keyframes spin { to { transform: rotate(360deg) } }
.mono { animation: fade 2s ease-out .4s both; }
""")
    ring_text = "DISTRIBUTED SYSTEMS  ·  FORMAL METHODS  ·  ADVERSARIAL ROBUSTNESS  ·  "
    r = 116
    circ = 2 * math.pi * r
    base = measure("sans-m", ring_text, 12.5)
    tracking = (circ - base) / len(ring_text)
    d.defs.append(f'<path id="ring" d="M{c} {c - r} a{r} {r} 0 1 1 -.01 0"/>')
    d.use_glyphs("sans-m", ring_text)
    d.add(f'<circle cx="{c}" cy="{c}" r="141" fill="none" stroke="{gold}" stroke-width=".8" opacity=".55"/>',
          f'<circle cx="{c}" cy="{c}" r="134" fill="none" stroke="{gold}" stroke-width=".5" opacity=".35"/>',
          f'<g class="spin"><text class="f-sans-m" font-size="12.5" fill="{gold}" letter-spacing="{fmt(tracking)}">'
          f'<textPath href="#ring">{ring_text}</textPath></text></g>',
          f'<circle cx="{c}" cy="{c}" r="97" fill="none" stroke="{gold}" stroke-width=".8" opacity=".6"/>',
          f'<g class="orb"><circle cx="{c}" cy="{c - 97}" r="2.4" fill="{gold}"/></g>',
          '<g class="mono">',
          d.text(c - 4, c + 25, "MJ", "serif-bi", 84, gold, anchor="middle", tracking=-2),
          diamond(c, c + 52, 2.4, fill=gold),
          "</g>")
    d.save("seal.svg")


# ==========================================================================
# Section openers
# ==========================================================================
SECTIONS = [
    ("about", "I.", "About", "RESEARCH INTERESTS  &  BACKGROUND"),
    ("work", "II.", "Selected Work", "FOUR SYSTEMS, ONE QUESTION"),
    ("instruments", "III.", "Instruments", "LANGUAGES, SYSTEMS  &  METHODS"),
    ("record", "IV.", "Record", "MILESTONES  &  CREDENTIALS"),
    ("city", "V.", "The City", "A YEAR OF CONTRIBUTIONS, REBUILT EVERY NIGHT"),
]


def section(t: dict, theme: str, key: str, num: str, title: str, sub: str) -> None:
    d = Doc(W, 108, f"{num} {title}")
    d.css.append(f"""
.st {{ animation: rise 1.4s {EASE_OUT} .1s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.5s {EASE_OUT} .45s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.5s {EASE_OUT} .45s both; }}
.ed {{ animation: fade 1s ease-out 1.6s both; }}
.sb {{ animation: fade 1.4s ease-out .7s both; }}
""")
    ns, ts, gap = 30, 36, 12
    wn, wt = measure("serif-bi", num, ns), measure("serif", title, ts)
    x = W / 2 - (wn + gap + wt) / 2
    base, mid = 60, 50
    left_end, right_start = x - 30, x + wn + gap + wt + 30
    d.add('<g class="st">',
          d.text(x, base, num, "serif-bi", ns, t["gold"]),
          d.text(x + wn + gap, base, title, "serif", ts, t["ink"]),
          "</g>",
          f'<line class="rl" x1="78" y1="{mid}" x2="{fmt(left_end)}" y2="{mid}" stroke="{t["gold"]}" stroke-width=".7" opacity=".55"/>',
          f'<line class="rr" x1="{fmt(right_start)}" y1="{mid}" x2="{W - 78}" y2="{mid}" stroke="{t["gold"]}" stroke-width=".7" opacity=".55"/>',
          f'<g class="ed">{diamond(72, mid, 2.6, fill=t["gold"])}{diamond(W - 72, mid, 2.6, fill=t["gold"])}</g>',
          '<g class="sb">', d.text(W / 2, 92, sub, "sans-m", 9.5, t["muted"], anchor="middle", tracking=3.4), "</g>")
    d.save(f"section-{key}-{theme}.svg")


# ==========================================================================
# Project cards (two per row) with a small animated motif each
# ==========================================================================
CW, CH = 420, 300


def motif_crci(t: dict) -> str:
    n = [(8, 44), (34, 14), (36, 68), (62, 41), (92, 12), (94, 68), (114, 40)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4), (3, 5), (2, 5), (4, 6), (5, 6), (3, 6)]
    bad = 4
    out = []
    dur, kt = "9s", "0;.38;.5;.86;1"
    for a, b in edges:
        (x1, y1), (x2, y2) = n[a], n[b]
        dim = bad in (a, b)
        anim = (f'<animate attributeName="stroke-opacity" values=".45;.45;.07;.07;.45" keyTimes="{kt}" dur="{dur}" '
                f'repeatCount="indefinite"/>') if dim else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["gold"]}" stroke-width=".8" '
                   f'stroke-opacity=".45">{anim}</line>')
    for path, begin in (("M8 44 L34 14 L62 41 L94 68 L114 40", "0s"), ("M8 44 L36 68 L62 41 L114 40", "1.7s"),
                        ("M114 40 L94 68 L36 68 L8 44", "3.1s")):
        out.append(f'<circle r="1.9" fill="{t["gold"]}" opacity="0">'
                   f'<animateMotion path="{path}" dur="3.2s" begin="{begin}" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3.2s" begin="{begin}" '
                   f'repeatCount="indefinite"/></circle>')
    for i, (x, y) in enumerate(n):
        if i == bad:
            out.append(f'<circle cx="{x}" cy="{y}" r="7.5" fill="none" stroke="{t["rose"]}" stroke-width=".8" '
                       f'stroke-dasharray="2 2.2" opacity="0"><animate attributeName="opacity" values="0;0;.9;.9;0" '
                       f'keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/></circle>')
            out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{t["soft"]}"><animate attributeName="fill" '
                       f'values="{t["soft"]};{t["rose"]};{t["rose"]};{t["rose"]};{t["soft"]}" keyTimes="0;.3;.5;.86;1" '
                       f'dur="{dur}" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{t["soft"]}"/>')
    return "".join(out)


def motif_sentinel(t: dict) -> str:
    out = []
    base = 72
    bids = [50, 43, 35, 28, 20, 12]
    asks = [13, 21, 29, 36, 44, 52]
    rng = random.Random(7)
    x = 2
    for h in bids:
        out.append(_bar(x, base, 6.5, h, t["sage"], rng))
        x += 9.5
    mid = x + 3
    out.append(f'<line x1="{fmt(mid)}" y1="4" x2="{fmt(mid)}" y2="{base}" stroke="{t["gold"]}" stroke-width=".8" '
               f'stroke-dasharray="1.6 2.4" opacity=".8"/>')
    x += 6
    for h in asks:
        out.append(_bar(x, base, 6.5, h, t["rose"], rng))
        x += 9.5
    out.append(f'<line x1="0" y1="{base + .5}" x2="{fmt(x)}" y2="{base + .5}" stroke="{t["muted"]}" stroke-width=".6" opacity=".6"/>')
    return "".join(out)


def _bar(x, base, w, h, color, rng) -> str:
    dur = rng.uniform(2.8, 5.2)
    variant = rng.choice("abc")
    return (f'<rect class="fb" x="{fmt(x)}" y="{fmt(base - h)}" width="{fmt(w)}" height="{fmt(h)}" rx="1" fill="{color}" '
            f'fill-opacity=".75" style="transform-origin:50% 100%;animation:depth-{variant} {dur:.2f}s ease-in-out '
            f'{rng.uniform(0, 2):.2f}s infinite alternate"/>')


def motif_traceflux(t: dict) -> str:
    nodes = {"s": (6, 40), "a": (38, 16), "b": (38, 64), "c": (74, 6), "d": (74, 40), "e": (74, 72),
             "f": (112, 22), "g": (112, 58)}
    # (from, to, start, end) as fractions of the cycle; None = edge predates the report, never tainted.
    edges = [("s", "a", .06, .16), ("s", "b", .08, .18), ("a", "c", .20, .30), ("a", "d", .22, .32),
             ("b", "e", None, None), ("d", "f", .36, .46), ("d", "g", .38, .48), ("c", "f", .34, .44)]
    reach = {"s": .0, "a": .16, "b": .18, "c": .30, "d": .32, "f": .44, "g": .48}
    dur = "8s"
    out = []
    for u, v, t0, t1 in edges:
        (x1, y1), (x2, y2) = nodes[u], nodes[v]
        dash = ' stroke-dasharray="2 2.4"' if t0 is None else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["muted"]}" stroke-width=".7" '
                   f'opacity=".45"{dash}/>')
        if t0 is None:
            continue
        L = math.hypot(x2 - x1, y2 - y1)
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["gold"]}" stroke-width="1.1" '
                   f'stroke-dasharray="{L:.1f}" stroke-dashoffset="{L:.1f}"><animate attributeName="stroke-dashoffset" '
                   f'values="{L:.1f};{L:.1f};0;0;{L:.1f}" keyTimes="0;{t0};{t1};.9;1" dur="{dur}" repeatCount="indefinite"/></line>')
    for k, (x, y) in nodes.items():
        r = 3.6 if k == "s" else 3.1
        if k in reach:
            t0 = reach[k]
            vals = f"{t['faint']};{t['faint']};{t['gold']};{t['gold']};{t['faint']}"
            kts = f"0;{max(t0 - .001, 0):.3f};{t0 + .02:.3f};.9;1" if t0 else "0;0;.02;.9;1"
            out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{t["faint"]}"><animate attributeName="fill" values="{vals}" '
                       f'keyTimes="{kts}" dur="{dur}" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{t["faint"]}" stroke-width="1"/>')
    return "".join(out)


def motif_inkgauge(t: dict) -> str:
    rng = random.Random(11)
    heights = [rng.uniform(10, 40) for _ in range(30)]
    top = sorted(range(30), key=lambda i: heights[i])[-5:]
    for i in top:
        heights[i] = rng.uniform(52, 62)
    base, out = 70, []
    for i, h in enumerate(heights):
        x = 2 + i * 3.9
        hot = i in top
        out.append(f'<rect x="{fmt(x)}" y="{fmt(base - h)}" width="2.5" height="{fmt(h)}" rx=".8" '
                   f'fill="{t["gold"] if hot else t["soft"]}" fill-opacity="{1 if hot else .32}"/>')
    for n, i in enumerate(sorted(top)):
        x = 2 + i * 3.9 + 1.25
        out.append(f'<circle cx="{fmt(x)}" cy="{fmt(base - heights[i] - 6)}" r="1.5" fill="{t["gold"]}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{.1 + n * .12:.2f};{.14 + n * .12:.2f};.92;1" '
                   f'dur="7s" repeatCount="indefinite"/></circle>')
    out.append(f'<line x1="0" y1="2" x2="0" y2="{base}" stroke="{t["gold"]}" stroke-width=".9" opacity=".55">'
               f'<animateTransform attributeName="transform" type="translate" values="0 0;118 0" dur="7s" '
               f'repeatCount="indefinite"/></line>')
    out.append(f'<line x1="0" y1="{base + .5}" x2="118" y2="{base + .5}" stroke="{t["muted"]}" stroke-width=".6" opacity=".6"/>')
    return "".join(out)


PROJECTS = [
    dict(key="crci", no="Nº 01 — DISTRIBUTED SYSTEMS", title="CRCI", tag="PREPRINT", motif=motif_crci,
         sub="Signed gossip for disaster-zone mesh networks: every node isolates misbehaving peers on its own, "
             "with no servers and no voting.",
         stats=[("< 1 ms", "REPLAY ISOLATION"), ("0 / 50", "HONEST PEERS BANNED"), ("O(n)", "COST PER MESSAGE")],
         tools="RUST  ·  ED25519  ·  TLA+  ·  PROPTEST  ·  UNIFFI"),
    dict(key="sentinel", no="Nº 02 — MARKET MICROSTRUCTURE", title="SENTINEL", tag=None, motif=motif_sentinel,
         sub="An adversarial limit-order-book simulator in which a trust-aware market maker learns to defend "
             "itself against spoofers.",
         stats=[("sub-µs", "MATCHING LATENCY"), ("zero", "HOT-PATH ALLOCS"), ("N = 30", "SEEDED ABLATIONS")],
         tools="RUST  ·  PYTHON  ·  HAWKES MLE  ·  AVELLANEDA–STOIKOV"),
    dict(key="traceflux", no="Nº 03 — FINANCIAL NETWORKS", title="TraceFlux", tag="LIVE", motif=motif_traceflux,
         sub="Causal, time-bounded taint propagation that freezes mule-account chains across banks, backed by a "
             "tamper-evident audit log.",
         stats=[("3.8 µs", "CAUSAL BFS · P50"), ("15.4 µs", "P99 · 509 NODES"), ("HMAC", "HASH-CHAINED AUDIT")],
         tools="PYTHON  ·  FASTAPI  ·  REACT  ·  WEBSOCKETS"),
    dict(key="inkgauge", no="Nº 04 — TOOLS FOR WRITERS", title="Inkgauge", tag=None, motif=motif_inkgauge,
         sub="A copyeditor's proof sheet: readability, style flags and the five hardest sentences in a chapter, "
             "analysed privately.",
         stats=[("150k", "CHARACTERS PER PASS"), ("0 bytes", "OF TEXT STORED"), ("4", "AI ENGINES · 1 OFFLINE")],
         tools="PYTHON  ·  FASTAPI  ·  NLP  ·  LOCAL-FIRST"),
]


def card(t: dict, theme: str, p: dict, index: int) -> None:
    d = Doc(CW, CH, f"{p['title']} — {p['sub']}")
    delay = .15 + index * .12
    d.css.append(f"""
.cd {{ animation: rise 1.3s {EASE_OUT} {delay:.2f}s both; }}
.ac {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.4s {EASE_OUT} {delay + .5:.2f}s both; }}
.ar {{ animation: nudge 6s ease-in-out {3 + index * .7:.1f}s infinite; }}
@keyframes nudge {{ 0%, 86%, 100% {{ transform: none }} 92% {{ transform: translateX(3px) }} }}
@keyframes depth-a {{ from {{ transform: scaleY(1) }} to {{ transform: scaleY(.74) }} }}
@keyframes depth-b {{ from {{ transform: scaleY(1) }} to {{ transform: scaleY(.82) }} }}
@keyframes depth-c {{ from {{ transform: scaleY(.9) }} to {{ transform: scaleY(1) }} }}
""")
    x0, L, R = 8, 32, CW - 32
    d.add('<g class="cd">',
          f'<rect x="{x0}" y="8" width="{CW - 16}" height="{CH - 16}" rx="14" fill="{t["surface"]}" stroke="{t["border"]}"/>',
          f'<line class="ac" x1="{L}" y1="8.5" x2="{L + 56}" y2="8.5" stroke="{t["gold"]}" stroke-width="1.4"/>',
          d.text(L, 44, p["no"], "sans-m", 9.5, t["gold"], tracking=2.4),
          d.text(L, 92, p["title"], "serif-b", 38, t["ink"]))
    if p["tag"]:
        tx = L + measure("serif-b", p["title"], 38) + 14
        tw = measure("sans-sb", p["tag"], 8, 1.8) + 16
        d.add(f'<rect x="{fmt(tx)}" y="72" width="{fmt(tw)}" height="17" rx="8.5" fill="none" stroke="{t["gold"]}" '
              f'stroke-opacity=".6" stroke-width=".8"/>',
              d.text(tx + 8, 83.6, p["tag"], "sans-sb", 8, t["gold"], tracking=1.8))
    d.add(f'<g transform="translate({R - 118},28)">{p["motif"](t)}</g>')

    for i, line in enumerate(wrap("serif-i", p["sub"], 16.5, R - L)):
        d.add(d.text(L, 124 + i * 21, line, "serif-i", 16.5, t["soft"]))
    d.add(f'<line x1="{L}" y1="186" x2="{R}" y2="186" stroke="{t["rule"]}" stroke-width=".8"/>')
    col = (R - L) / 3
    for i, (value, label) in enumerate(p["stats"]):
        x = L + i * col
        tracking = 1.5
        while measure("sans-m", label, 8.5, tracking) > col - 10 and tracking > .4:
            tracking -= .1
        d.add(d.text(x, 220, value, "serif-b", 25, t["ink"]),
              d.text(x, 240, label, "sans-m", 8.5, t["muted"], tracking=tracking))
    d.add(diamond(L + 2.4, 264.5, 2.2, fill=t["gold"]),
          d.text(L + 12, 268, p["tools"], "sans-m", 8.5, t["muted"], tracking=1.4),
          f'<g class="ar">{arrow(R - 16, 265, 16, t["gold"], 1.1)}</g>',
          "</g>")
    d.save(f"card-{p['key']}-{theme}.svg")


# ==========================================================================
# Instruments
# ==========================================================================
INSTRUMENTS = [
    ("LANGUAGES", ["Rust", "Python", "Kotlin", "SQL", "JavaScript"]),
    ("SYSTEMS", ["Tokio async I/O", "Ed25519 · AES-GCM", "UniFFI bindings", "FastAPI · WebSockets", "Prometheus · Grafana"]),
    ("METHODS", ["TLA+ specification", "Property-based testing", "Hawkes-process MLE", "Temporal graph search",
                 "Seeded ablations"]),
    ("INFRASTRUCTURE", ["Docker · Compose", "GitHub Actions CI", "AWS Solutions Architect", "Linux netns · netem",
                        "ARM cross-builds"]),
]


def instruments(t: dict, theme: str) -> None:
    d = Doc(W, 246, "Languages, systems, methods and infrastructure")
    d.css.append(f"""
.col {{ animation: rise 1.3s {EASE_OUT} both; }}
.sep {{ transform-box: fill-box; transform-origin: 50% 0; animation: drawy 1.6s {EASE_OUT} .3s both; }}
""")
    cw = W / 4
    for i in range(1, 4):
        d.add(f'<line class="sep" x1="{i * cw}" y1="26" x2="{i * cw}" y2="222" stroke="{t["rule"]}" stroke-width=".8"/>')
    for i, (head, items) in enumerate(INSTRUMENTS):
        cx = cw * i + cw / 2
        d.add(f'<g class="col" style="animation-delay:{.15 + i * .14:.2f}s">',
              d.text(cx, 42, head, "sans-sb", 9.5, t["gold"], anchor="middle", tracking=3),
              f'<line x1="{cx - 11}" y1="56" x2="{cx + 11}" y2="56" stroke="{t["gold"]}" stroke-width=".8" opacity=".7"/>')
        for k, item in enumerate(items):
            d.add(d.text(cx, 92 + k * 30, item, "serif", 18.5, t["ink"], anchor="middle"))
        d.add("</g>")
    d.save(f"instruments-{theme}.svg")


# ==========================================================================
# Record: a timeline that draws itself
# ==========================================================================
RECORD = [
    ("2024", "VIT BHOPAL", ["B.Tech, Computer", "Science & Engineering"]),
    ("2025", "TEAM VORTEX", ["Founding member", "& team manager"]),
    ("2025", "AWS CERTIFIED", ["Solutions Architect", "— Associate"]),
    ("2026", "SAE AERO DESIGN", ["World rank 16", "Fort Worth, Texas"]),
    ("2026", "CRCI PREPRINT", ["Published with a", "software archive"]),
    ("2028", "NEXT", ["Direct PhD in", "distributed systems"]),
]


def record(t: dict, theme: str) -> None:
    d = Doc(W, 222, "Milestones: VIT Bhopal 2024, Team Vortex 2025, AWS Solutions Architect 2025, "
                    "SAE Aero Design West world rank 16 in 2026, CRCI preprint 2026, direct PhD from 2028")
    n = len(RECORD)
    x0, x1, y = 82, W - 82, 84
    step = (x1 - x0) / (n - 1)
    d.css.append(f"""
.ln {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 2.6s {EASE_OUT} .2s both; }}
.ms {{ animation: rise 1.1s {EASE_OUT} both; }}
.ping {{ transform-box: fill-box; transform-origin: center; animation: ping 3s cubic-bezier(0,0,.2,1) 3.6s infinite both; }}
@keyframes ping {{ 0% {{ transform: scale(1); opacity: .8 }} 75%, 100% {{ transform: scale(2.6); opacity: 0 }} }}
""")
    d.add(f'<line class="ln" x1="{x0}" y1="{y}" x2="{x1 - step}" y2="{y}" stroke="{t["gold"]}" stroke-width=".9" opacity=".6"/>',
          f'<line class="ln" x1="{x1 - step}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["gold"]}" stroke-width=".9" '
          f'stroke-dasharray="2 3" opacity=".6" style="animation-delay:2s"/>')
    for i, (year, head, desc) in enumerate(RECORD):
        cx = x0 + i * step
        future = i == n - 1
        tracking = 2
        while measure("sans-sb", head, 9, tracking) > step - 14 and tracking > .6:
            tracking -= .1
        d.add(f'<g class="ms" style="animation-delay:{.35 + i * .32:.2f}s">',
              d.text(cx, y - 22, year, "serif-b", 26, t["gold"] if not future else t["muted"], anchor="middle"))
        if future:
            d.add(f'<circle class="ping" cx="{fmt(cx)}" cy="{y}" r="5" fill="none" stroke="{t["gold"]}" stroke-width="1"/>',
                  f'<circle cx="{fmt(cx)}" cy="{y}" r="5" fill="{t["surface"]}" stroke="{t["gold"]}" stroke-width="1.1"/>')
        else:
            d.add(f'<circle cx="{fmt(cx)}" cy="{y}" r="8.5" fill="{t["gold"]}" opacity=".14"/>',
                  f'<circle cx="{fmt(cx)}" cy="{y}" r="4.2" fill="{t["gold"]}"/>')
        d.add(d.text(cx, y + 42, head, "sans-sb", 9, t["ink"], anchor="middle", tracking=tracking))
        for k, line in enumerate(desc):
            d.add(d.text(cx, y + 66 + k * 20, line, "serif-i", 16, t["soft"], anchor="middle"))
        d.add("</g>")
    d.save(f"record-{theme}.svg")


# ==========================================================================
# Colophon
# ==========================================================================
def footer(t: dict, theme: str) -> None:
    d = Doc(W, 170, "Thank you for reading")
    cx, y = W / 2, 40
    d.css.append(f"""
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.8s {EASE_OUT} .2s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.8s {EASE_OUT} .2s both; }}
.dm {{ animation: fade 1s ease-out .8s both, breathe 5s ease-in-out 2s infinite; }}
.tx {{ animation: rise 1.4s {EASE_OUT} .6s both; }}
.cl {{ animation: fade 1.6s ease-out 1.1s both; }}
""")
    d.add(f'<line class="rl" x1="{cx - 210}" y1="{y}" x2="{cx - 14}" y2="{y}" stroke="{t["gold"]}" stroke-width=".7" opacity=".6"/>',
          f'<line class="rr" x1="{cx + 14}" y1="{y}" x2="{cx + 210}" y2="{y}" stroke="{t["gold"]}" stroke-width=".7" opacity=".6"/>',
          f'<g class="dm">{diamond(cx, y, 4.2, stroke=t["gold"], sw=.9)}{diamond(cx, y, 1.6, fill=t["gold"])}</g>',
          '<g class="tx">', d.text(cx, 88, "Thank you for reading.", "serif-i", 22, t["soft"], anchor="middle"), "</g>",
          '<g class="cl">',
          d.text(cx, 124, "MEDWIN JOSE  ·  BHOPAL, INDIA  ·  MMXXVI", "sans-m", 9.5, t["muted"], anchor="middle", tracking=4),
          d.text(cx, 146, "SET IN CORMORANT GARAMOND & INTER", "sans", 8, t["faint"], anchor="middle", tracking=3.2),
          "</g>")
    d.save(f"footer-{theme}.svg")


def main() -> None:
    seal()
    for theme, t in THEMES.items():
        header(t, theme)
        status(t, theme)
        for key, label, delay in CHIPS:
            chip(t, theme, key, label, delay)
        for s in SECTIONS:
            section(t, theme, *s)
        for i, p in enumerate(PROJECTS):
            card(t, theme, p, i % 2)
        instruments(t, theme)
        record(t, theme)
        footer(t, theme)


if __name__ == "__main__":
    main()
