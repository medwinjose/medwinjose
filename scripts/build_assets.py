"""Build every static SVG used by the profile README (dark + light variants).

    python scripts/build_assets.py

The contribution city is built separately by scripts/city.py (hourly action).
"""

from __future__ import annotations

import math
import random

from svgkit import EASE_OUT, THEMES, Doc, arrow, arrow_ne, diamond, fmt, measure, wrap

W = 840  # Matches the README column; images scale down on smaller screens.


# ==========================================================================
# Masthead
# ==========================================================================
TAGLINES = [  # none repeat the About text word for word
    "Quietly obsessed with correctness, latency and good typography.",
    "Every claim backed by a benchmark you can rerun.",
    "Happiest when the proof and the benchmark agree.",
]


def header(t: dict, theme: str) -> None:
    d = Doc(W, 170, "Medwin Jose — building systems that stay correct when participants misbehave")
    cx = W / 2
    n = len(TAGLINES)
    cycle = 4.5 * n
    d.css.append(f"""
.k  {{ animation: fade 1s ease-out 0s both; }}
.nm {{ animation: rise 1.4s {EASE_OUT} .1s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.2s {EASE_OUT} .35s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.2s {EASE_OUT} .35s both; }}
.dm {{ animation: fade .8s ease-out .6s both, breathe 5s ease-in-out 1.6s infinite; }}
.tl {{ opacity: 0; animation: cycle {cycle}s ease-in-out infinite both; }}
.t1 {{ opacity: 1; }}
@keyframes cycle {{ 0% {{ opacity: 0; transform: translateY(5px) }} 5% {{ opacity: 1; transform: none }}
  29% {{ opacity: 1; transform: none }} 33.3% {{ opacity: 0; transform: translateY(-4px) }} 100% {{ opacity: 0 }} }}
@media (prefers-reduced-motion: reduce) {{ .tl:not(.t1) {{ display: none }} }}
.mt {{ animation: fade 1.2s ease-out .9s both; }}
""")
    kick = "HELLO, I AM"
    kw = measure("sans-m", kick, 9, 4.5)
    d.add('<g class="k">',
          d.text(cx, 12, kick, "sans-m", 9, t["accent"], anchor="middle", tracking=4.5),
          diamond(cx - kw / 2 - 16, 9, 2.3, fill=t["accent"]),
          diamond(cx + kw / 2 + 16, 9, 2.3, fill=t["accent"]),
          "</g>")

    # Name with a soft lavender-to-blush sheen drifting across it now and then.
    name = "MEDWIN JOSE"
    d.defs.append(
        f'<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-260" y1="0" x2="-40" y2="0">'
        f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
        f'<stop offset=".35" stop-color="{t["accent"]}" stop-opacity=".9"/>'
        f'<stop offset=".65" stop-color="{t["blush"]}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{t["blush"]}" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1150 0;1150 0" '
        f'keyTimes="0;.24;1" dur="11s" begin="1.6s" repeatCount="indefinite"/></linearGradient>'
    )
    d.add('<g class="nm">',
          d.text(cx, 66, name, "serif", 48, t["ink"], anchor="middle", tracking=11.5),
          d.text(cx, 66, name, "serif", 48, "url(#sheen)", anchor="middle", tracking=11.5),
          "</g>")

    y = 88
    d.add(f'<line class="rl" x1="318" y1="{y}" x2="{cx - 12}" y2="{y}" stroke="{t["accent"]}" stroke-width=".9" opacity=".75"/>',
          f'<line class="rr" x1="{cx + 12}" y1="{y}" x2="{W - 318}" y2="{y}" stroke="{t["accent"]}" stroke-width=".9" opacity=".75"/>',
          f'<g class="dm">{diamond(cx, y, 3.8, stroke=t["blush"], sw=1)}{diamond(cx, y, 1.5, fill=t["blush"])}</g>')

    for i, line in enumerate(TAGLINES):
        d.add(f'<g class="tl t{i + 1}" style="animation-delay:{.55 + i * cycle / n:.2f}s">',
              d.text(cx, 122, line, "serif-i", 19.5, t["soft"], anchor="middle"), "</g>")

    d.add('<g class="mt">',
          d.text(cx, 155, "DISTRIBUTED SYSTEMS  ·  SECURITY  ·  RUST", "sans-m", 8.5, t["muted"], anchor="middle", tracking=3.6),
          "</g>")
    d.save(f"header-{theme}.svg")


LINKS = [
    ("linkedin", "LINKEDIN"),
    ("orcid", "ORCID"),
    ("scholar", "GOOGLE SCHOLAR"),
    ("email", "EMAIL"),
]


def chip(t: dict, theme: str, key: str, label: str, index: int) -> None:
    tw = measure("sans-m", label, 9.5, 2.1)
    w, h = tw + 54, 34
    d = Doc(int(math.ceil(w)) + 4, h + 4, label.title())
    delay = 1.1 + index * .1
    d.css.append(f"""
.c {{ animation: rise 1.2s {EASE_OUT} {delay:.2f}s both; }}
.ar {{ animation: nudge 7s ease-in-out {delay + 2 + index * .5:.2f}s infinite; }}
@keyframes nudge {{ 0%, 88%, 100% {{ transform: none }} 94% {{ transform: translate(2px,-2px) }} }}
""")
    d.add('<g class="c">',
          f'<rect x="2" y="2" width="{fmt(w)}" height="{h}" rx="{h / 2}" fill="none" stroke="{t["border"]}"/>',
          d.text(22, 2 + h / 2 + 3.4, label, "sans-m", 9.5, t["soft"], tracking=2.1),
          f'<g class="ar">{arrow_ne(22 + tw + 9, 2 + h / 2 - 3.6, 7.2, t["accent"], 1.1)}</g>',
          "</g>")
    d.save(f"link-{key}-{theme}.svg")


# ==========================================================================
# The Knight: a small companion who looks around, tilts its head and blinks.
# One file; the white mask and outlined cloak read on both themes.
# ==========================================================================
def knight() -> None:
    """A small horned knight in a lavender scarf.

    Every 13 seconds it looks left, looks right, tilts its head with a little
    "?", then has an "aha" moment: happy squinting eyes, a tiny hop and two
    sparkles. It blinks on its own rhythm. One file; the outlined white mask
    and cloak read on both themes.
    """
    # The canvas is as tall as the About text beside it (so text never wraps
    # underneath) and the figure is vertically centred inside it.
    KH = KNIGHT_CANVAS_H
    dy = KH / 2 - 158
    d = Doc(320, KH, "A small horned knight in a lavender scarf, looking around curiously")
    mask, eye, cloak, rim, line = "#F8F6FF", "#0F0E17", "#363859", "#A79BF5", "#2B2944"
    lav, lav_dk, blush, mint = "#B7AAFF", "#8C7EE6", "#FFB4C8", "#93E6CC"
    neck_y, scarf_x = 182 + dy, 168  # pivot points (neck, scarf knot) in canvas coordinates
    d.css.append(f"""
.all   {{ animation: bob 2.8s ease-in-out infinite alternate; }}
@keyframes bob {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-5px) }} }}
.hop   {{ animation: hop 13s ease-in-out infinite; }}
@keyframes hop {{ 0%, 66% {{ transform: none }} 69% {{ transform: translateY(-9px) }} 72% {{ transform: none }}
  74.5% {{ transform: translateY(-4px) }} 77%, 100% {{ transform: none }} }}
.shadow {{ transform-box: fill-box; transform-origin: center; animation: shrink 2.8s ease-in-out infinite alternate; }}
@keyframes shrink {{ from {{ transform: scaleX(1); opacity: .5 }} to {{ transform: scaleX(.86); opacity: .32 }} }}
.head  {{ transform-box: view-box; transform-origin: 150px {neck_y:.0f}px; animation: look 13s ease-in-out infinite; }}
@keyframes look {{
  0%, 8%    {{ transform: none }}
  12%, 22%  {{ transform: translateX(-5px) rotate(-3deg) }}
  28%, 38%  {{ transform: translateX(5px) rotate(3deg) }}
  44%, 58%  {{ transform: rotate(-11deg) }}
  64%, 80%  {{ transform: rotate(3deg) }}
  86%, 100% {{ transform: none }} }}
.eyes  {{ animation: glance 13s ease-in-out infinite; }}
@keyframes glance {{
  0%, 8%    {{ transform: none }}
  12%, 22%  {{ transform: translateX(-6px) }}
  28%, 38%  {{ transform: translateX(6px) }}
  44%, 58%  {{ transform: translate(-2px, 1px) }}
  64%, 100% {{ transform: none }} }}
.open  {{ animation: open 13s step-end infinite; }}
@keyframes open {{ 0% {{ opacity: 1 }} 65% {{ opacity: 0 }} 81% {{ opacity: 1 }} }}
.happy {{ opacity: 0; animation: happy 13s step-end infinite; }}
@keyframes happy {{ 0% {{ opacity: 0 }} 65% {{ opacity: 1 }} 81% {{ opacity: 0 }} }}
@media (prefers-reduced-motion: reduce) {{ .happy {{ display: none }} }}
.blink {{ transform-box: fill-box; transform-origin: center; animation: blink 4.6s ease-in-out infinite; }}
@keyframes blink {{ 0%, 44%, 52%, 100% {{ transform: none }} 48% {{ transform: scaleY(.08) }} }}
.cloak {{ transform-box: view-box; transform-origin: 150px {neck_y - 6:.0f}px; animation: sway 2.8s ease-in-out infinite alternate; }}
@keyframes sway {{ from {{ transform: skewX(1.6deg) }} to {{ transform: skewX(-1.6deg) }} }}
.tail  {{ transform-box: view-box; transform-origin: {scarf_x}px {neck_y + 13:.0f}px; animation: flutter 2.2s ease-in-out infinite alternate; }}
@keyframes flutter {{ from {{ transform: rotate(-7deg) }} to {{ transform: rotate(6deg) }} }}
.q     {{ transform-box: fill-box; transform-origin: 50% 100%; animation: wonder 13s ease-in-out infinite; }}
@keyframes wonder {{ 0%, 44% {{ opacity: 0; transform: translateY(6px) scale(.6) }}
  48%, 57% {{ opacity: 1; transform: none }} 61%, 100% {{ opacity: 0; transform: translateY(-4px) }} }}
.spark {{ transform-box: fill-box; transform-origin: center; animation: spark 13s ease-out infinite; }}
@keyframes spark {{ 0%, 65% {{ opacity: 0; transform: scale(.2) rotate(0) }} 69% {{ opacity: 1; transform: scale(1.1) rotate(25deg) }}
  76% {{ opacity: 1; transform: scale(1) rotate(45deg) }} 81%, 100% {{ opacity: 0; transform: scale(.4) rotate(70deg) }} }}
.mote  {{ animation: drift linear infinite; }}
@keyframes drift {{ 0% {{ transform: translateY(0); opacity: 0 }} 15% {{ opacity: .9 }} 100% {{ transform: translateY(-120px); opacity: 0 }} }}
.glow  {{ transform-box: fill-box; transform-origin: center; animation: breathe 6s ease-in-out infinite; }}
""")
    d.defs.append(f'<radialGradient id="halo"><stop offset="0" stop-color="{lav}" stop-opacity=".32"/>'
                  f'<stop offset="1" stop-color="{lav}" stop-opacity="0"/></radialGradient>')

    def horn(sign: int) -> str:
        m = (lambda x: x) if sign < 0 else (lambda x: 300 - x)
        return (f'<path d="M{m(115)} 116 C{m(106)} 98 {m(100)} 78 {m(106)} 52 C{m(114)} 72 {m(124)} 90 {m(138)} 106 Z" '
                f'fill="{mask}" stroke="{line}" stroke-width="2.2" stroke-linejoin="round"/>')

    def star(cx, cy, r, color, delay) -> str:
        k = r * .16
        path = (f"M{cx} {cy - r} Q{cx + k} {cy - k} {cx + r} {cy} Q{cx + k} {cy + k} {cx} {cy + r} "
                f"Q{cx - k} {cy + k} {cx - r} {cy} Q{cx - k} {cy - k} {cx} {cy - r} Z")
        return f'<path class="spark" d="{path}" fill="{color}" style="animation-delay:{delay}s"/>'

    d.add(f'<g transform="translate(0,{dy:.1f})">')
    # Soft halo and drifting motes behind the knight.
    d.add(f'<circle class="glow" cx="150" cy="160" r="118" fill="url(#halo)"/>')
    for x, y, r, col, dur, delay in [(78, 250, 2.2, lav, 7, 0), (222, 236, 1.8, blush, 8.5, 2.2), (104, 210, 1.5, mint, 6.5, 4),
                                     (204, 268, 2, lav, 9, 1.1), (60, 190, 1.4, blush, 7.5, 5.4), (238, 200, 1.6, mint, 8, 3.3)]:
        d.add(f'<circle class="mote" cx="{x}" cy="{y}" r="{r}" fill="{col}" style="animation-duration:{dur}s;animation-delay:{delay}s"/>')

    d.add(f'<ellipse class="shadow" cx="150" cy="271" rx="44" ry="5.5" fill="{lav}" opacity=".45"/>',
          '<g class="all"><g class="hop">',
          # legs
          f'<rect x="136" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
          f'<rect x="155" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
          # cloak
          f'<g class="cloak"><path d="M124 170 C110 198 103 228 98 254 C116 247 133 254 150 248 C167 254 184 247 202 254 '
          f'C197 228 190 198 176 170 Z" fill="{cloak}" stroke="{rim}" stroke-width="1.4" stroke-linejoin="round"/>'
          f'<path d="M150 200 V242" stroke="{rim}" stroke-width="1" opacity=".35"/></g>',
          # scarf: tail first (behind the knot), then the wrap around the neck
          f'<g class="tail"><path d="M168 190 C182 198 198 203 214 199 L211 212 C195 216 179 210 166 200 Z" fill="{lav}" '
          f'stroke="{lav_dk}" stroke-width="1.2" stroke-linejoin="round"/>'
          f'<path d="M205 201 L203 213" stroke="{blush}" stroke-width="3"/></g>',
          f'<path d="M118 180 Q150 198 182 180 L184 191 Q150 211 116 191 Z" fill="{lav}" stroke="{lav_dk}" '
          f'stroke-width="1.2" stroke-linejoin="round"/>',
          f'<path d="M120 187 Q150 204 180 187" fill="none" stroke="{blush}" stroke-width="2.2" stroke-linecap="round"/>',
          # head: horns, mask, eyes
          '<g class="head">', horn(-1), horn(1),
          f'<path d="M106 136 C106 98 194 98 194 136 C194 170 176 186 150 186 C124 186 106 170 106 136 Z" fill="{mask}" stroke="{line}" stroke-width="2.2"/>',
          f'<path d="M114 160 C122 176 136 182 150 182" fill="none" stroke="#DCD6F2" stroke-width="2" stroke-linecap="round" opacity=".7"/>',
          '<g class="eyes"><g class="open"><g class="blink">',
          f'<ellipse cx="131" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
          f'<ellipse cx="169" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
          '<circle cx="127" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
          '<circle cx="165" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
          '</g></g>',
          # happy, squinting eyes for the "aha" moment
          f'<g class="happy" fill="none" stroke="{eye}" stroke-width="4.5" stroke-linecap="round">'
          '<path d="M121 147 Q131 133 141 147"/><path d="M159 147 Q169 133 179 147"/></g>',
          '</g>',
          f'<ellipse cx="121" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
          f'<ellipse cx="179" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
          '</g>',
          # a curious "?" during the tilt, sparkles during the "aha"
          '<g class="q">', d.text(212, 92, "?", "serif-bi", 34, blush), "</g>",
          star(214, 84, 9, mint, 0), star(90, 100, 6, blush, .15),
          "</g></g>")
    d.add("</g>")
    d.save("knight.svg")


KNIGHT_CANVAS_H = 392  # tuned so the image matches the About text height at GitHub's width


# ==========================================================================
# Section openers
# ==========================================================================
SECTIONS = [
    ("about", "I.", "About", "A LITTLE ABOUT ME"),
    ("instruments", "II.", "Instruments", "LANGUAGES, SYSTEMS  &  METHODS"),
    ("work", "III.", "Selected Work", "TWO SYSTEMS, ONE QUESTION"),
    # +8: follows a caption ending in a code snippet, whose grey box sits lower than text
    ("city", "IV.", "The City", "MY CONTRIBUTIONS, REBUILT EVERY FEW MINUTES", 8),
]


SECTION_TOP = 22     # space above a section title; with the previous block it renders as about 44px
SECTION_BOTTOM = 34  # space below the subtitle; also renders as about 44px, so each title sits centred


def section(t: dict, theme: str, key: str, num: str, title: str, sub: str, extra_top: int = 0) -> None:
    top = SECTION_TOP + extra_top
    d = Doc(W, top + 54 + SECTION_BOTTOM, f"{num} {title}")
    d.css.append(f"""
.st {{ animation: rise 1.4s {EASE_OUT} .1s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.5s {EASE_OUT} .45s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.5s {EASE_OUT} .45s both; }}
.ed {{ animation: fade 1s ease-out 1.6s both; }}
.sb {{ animation: fade 1.4s ease-out .7s both; }}
""")
    ns, ts, gap = 28, 33, 11
    wn, wt = measure("serif-bi", num, ns), measure("serif", title, ts)
    x = W / 2 - (wn + gap + wt) / 2
    base, mid = top + 24, top + 15
    left_end, right_start = x - 28, x + wn + gap + wt + 28
    d.add('<g class="st">',
          d.text(x, base, num, "serif-bi", ns, t["accent"]),
          d.text(x + wn + gap, base, title, "serif", ts, t["ink"]),
          "</g>",
          f'<line class="rl" x1="84" y1="{mid}" x2="{fmt(left_end)}" y2="{mid}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<line class="rr" x1="{fmt(right_start)}" y1="{mid}" x2="{W - 84}" y2="{mid}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<g class="ed">{diamond(78, mid, 2.6, fill=t["accent"])}{diamond(W - 78, mid, 2.6, fill=t["accent"])}</g>',
          '<g class="sb">', d.text(W / 2, top + 50, sub, "sans-m", 9, t["muted"], anchor="middle", tracking=3.4), "</g>")
    d.save(f"section-{key}-{theme}.svg")


# ==========================================================================
# Selected work: two cards, each with a small animated motif
# ==========================================================================
CW, CH = 420, 300


def motif_crci(t: dict) -> str:
    """A gossip mesh in which one peer misbehaves and its neighbours cut it off."""
    n = [(8, 44), (34, 14), (36, 68), (62, 41), (92, 12), (94, 68), (114, 40)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4), (3, 5), (2, 5), (4, 6), (5, 6), (3, 6)]
    bad, dur, kt = 4, "9s", "0;.38;.5;.86;1"
    out = []
    for a, b in edges:
        (x1, y1), (x2, y2) = n[a], n[b]
        anim = (f'<animate attributeName="stroke-opacity" values=".5;.5;.07;.07;.5" keyTimes="{kt}" dur="{dur}" '
                f'repeatCount="indefinite"/>') if bad in (a, b) else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["accent"]}" stroke-width=".8" '
                   f'stroke-opacity=".5">{anim}</line>')
    for path, begin in (("M8 44 L34 14 L62 41 L94 68 L114 40", "0s"), ("M8 44 L36 68 L62 41 L114 40", "1.7s"),
                        ("M114 40 L94 68 L36 68 L8 44", "3.1s")):
        out.append(f'<circle r="1.9" fill="{t["mint"]}" opacity="0">'
                   f'<animateMotion path="{path}" dur="3.2s" begin="{begin}" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3.2s" begin="{begin}" '
                   f'repeatCount="indefinite"/></circle>')
    for i, (x, y) in enumerate(n):
        if i == bad:
            out.append(f'<circle cx="{x}" cy="{y}" r="7.5" fill="none" stroke="{t["blush"]}" stroke-width=".8" '
                       f'stroke-dasharray="2 2.2" opacity="0"><animate attributeName="opacity" values="0;0;.9;.9;0" '
                       f'keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/></circle>')
            out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{t["soft"]}"><animate attributeName="fill" '
                       f'values="{t["soft"]};{t["blush"]};{t["blush"]};{t["blush"]};{t["soft"]}" keyTimes="0;.3;.5;.86;1" '
                       f'dur="{dur}" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{t["soft"]}"/>')
    return "".join(out)


def motif_sentinel(t: dict) -> str:
    """A breathing order book: bids in mint, asks in blush, the mid price dashed."""
    out, base, x = [], 72, 2
    rng = random.Random(7)
    for h in [50, 43, 35, 28, 20, 12]:
        out.append(_bar(x, base, 6.5, h, t["mint"], rng))
        x += 9.5
    mid = x + 3
    out.append(f'<line x1="{fmt(mid)}" y1="4" x2="{fmt(mid)}" y2="{base}" stroke="{t["accent"]}" stroke-width=".8" '
               f'stroke-dasharray="1.6 2.4" opacity=".9"/>')
    x += 6
    for h in [13, 21, 29, 36, 44, 52]:
        out.append(_bar(x, base, 6.5, h, t["blush"], rng))
        x += 9.5
    out.append(f'<line x1="0" y1="{base + .5}" x2="{fmt(x)}" y2="{base + .5}" stroke="{t["muted"]}" stroke-width=".6" opacity=".6"/>')
    return "".join(out)


def _bar(x, base, w, h, color, rng) -> str:
    dur = rng.uniform(2.8, 5.2)
    variant = rng.choice("abc")
    return (f'<rect class="fb" x="{fmt(x)}" y="{fmt(base - h)}" width="{fmt(w)}" height="{fmt(h)}" rx="1" fill="{color}" '
            f'fill-opacity=".8" style="transform-origin:50% 100%;animation:depth-{variant} {dur:.2f}s ease-in-out '
            f'{rng.uniform(0, 2):.2f}s infinite alternate"/>')


PROJECTS = [
    dict(key="crci", no="Nº 01 — DISTRIBUTED SYSTEMS", title="CRCI", tag="PREPRINT", motif=motif_crci,
         sub="Byzantine-fault-tolerant gossip for mesh networks: every node isolates misbehaving peers on its own, "
             "with no servers and no consensus.",
         stats=[("< 1 ms", "REPLAY ISOLATION"), ("0 / 50", "HONEST PEERS BANNED"), ("O(n)", "COST PER MESSAGE")],
         tools="RUST  ·  ED25519  ·  TLA+  ·  PROPTEST"),
    dict(key="sentinel", no="Nº 02 — MARKET MICROSTRUCTURE", title="SENTINEL", tag=None, motif=motif_sentinel,
         sub="Trust and toxicity detection for limit-order-book market-making: under extreme toxicity, the "
             "trust-aware maker cuts its adverse-selection cost.",
         stats=[("+10,843.99", "TICKS SAVED"), ("t = 3.50", "WELCH, N = 500"), ("p = 4.9e-4", "TWO-SIDED")],
         tools="RUST  ·  HAWKES PROCESSES  ·  AVELLANEDA–STOIKOV"),
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
          # 4px above the card (aligns with other blocks), 8px on the sides (gap between the two cards)
          f'<rect x="{x0}" y="4" width="{CW - 16}" height="{CH - 16}" rx="14" fill="{t["surface"]}" stroke="{t["border"]}"/>',
          f'<line class="ac" x1="{L}" y1="4.5" x2="{L + 56}" y2="4.5" stroke="{t["accent"]}" stroke-width="1.4"/>',
          d.text(L, 40, p["no"], "sans-m", 9.5, t["accent"], tracking=2.4),
          d.text(L, 88, p["title"], "serif-b", 38, t["ink"]))
    if p["tag"]:
        tx = L + measure("serif-b", p["title"], 38) + 14
        tw = measure("sans-sb", p["tag"], 8, 1.8) + 16
        d.add(f'<rect x="{fmt(tx)}" y="68" width="{fmt(tw)}" height="17" rx="8.5" fill="none" stroke="{t["accent"]}" '
              f'stroke-opacity=".7" stroke-width=".8"/>',
              d.text(tx + 8, 79.6, p["tag"], "sans-sb", 8, t["accent"], tracking=1.8))
    d.add(f'<g transform="translate({R - 118},24)">{p["motif"](t)}</g>')
    for i, line in enumerate(wrap("serif-i", p["sub"], 16.5, R - L)):
        d.add(d.text(L, 120 + i * 21, line, "serif-i", 16.5, t["soft"]))
    d.add(f'<line x1="{L}" y1="182" x2="{R}" y2="182" stroke="{t["rule"]}" stroke-width=".8"/>')
    col = (R - L) / 3
    for i, (value, label) in enumerate(p["stats"]):
        x = L + i * col
        size = 25.0
        while measure("serif-b", value, size) > col - 12:
            size -= .5
        tracking = 1.5
        while measure("sans-m", label, 8.5, tracking) > col - 10 and tracking > .4:
            tracking -= .1
        d.add(d.text(x, 216, value, "serif-b", size, t["ink"]),
              d.text(x, 236, label, "sans-m", 8.5, t["muted"], tracking=tracking))
    d.add(diamond(L + 2.4, 260.5, 2.2, fill=t["accent"]),
          d.text(L + 12, 264, p["tools"], "sans-m", 8.5, t["muted"], tracking=1.4),
          f'<g class="ar">{arrow(R - 16, 261, 16, t["accent"], 1.1)}</g>',
          "</g>")
    d.save(f"card-{p['key']}-{theme}.svg")


# ==========================================================================
# Instruments
# ==========================================================================
INSTRUMENTS = [
    ("LANGUAGES", "accent", ["Rust", "Python", "Kotlin", "SQL", "JavaScript"]),
    ("SYSTEMS", "mint", ["Async I/O", "Applied cryptography", "Peer-to-peer networking", "APIs · WebSockets",
                         "Observability"]),
    ("METHODS", "blush", ["Formal specification · TLA+", "Property-based testing", "Statistical modelling",
                          "Graph algorithms", "Reproducible benchmarks"]),
    ("INFRASTRUCTURE", "butter", ["Docker", "GitHub Actions", "AWS · certified architect", "Linux", "ARM cross-builds"]),
]


def instruments(t: dict, theme: str) -> None:
    d = Doc(W, 212, "Languages, systems, methods and infrastructure")  # matches a paragraph margin below
    d.css.append(f"""
.col {{ animation: rise 1.3s {EASE_OUT} both; }}
.sep {{ transform-box: fill-box; transform-origin: 50% 0; animation: drawy 1.6s {EASE_OUT} .3s both; }}
""")
    cw = W / 4
    for i in range(1, 4):
        d.add(f'<line class="sep" x1="{i * cw}" y1="4" x2="{i * cw}" y2="196" stroke="{t["rule"]}" stroke-width=".8"/>')
    for i, (head, color, items) in enumerate(INSTRUMENTS):
        cx = cw * i + cw / 2
        c = t[color]
        d.add(f'<g class="col" style="animation-delay:{.15 + i * .14:.2f}s">',
              d.text(cx, 16, head, "sans-sb", 9, c, anchor="middle", tracking=3),
              f'<line x1="{cx - 11}" y1="29" x2="{cx + 11}" y2="29" stroke="{c}" stroke-width="1.2" stroke-linecap="round"/>')
        for k, item in enumerate(items):
            size = 18
            while measure("serif", item, size) > cw - 22:
                size -= .5
            d.add(d.text(cx, 64 + k * 30, item, "serif", size, t["ink"], anchor="middle"))
        d.add("</g>")
    d.save(f"instruments-{theme}.svg")


# ==========================================================================
# Colophon
# ==========================================================================
def footer(t: dict, theme: str) -> None:
    top = SECTION_TOP + 6  # follows a caption line, which sits slightly lower than an image
    d = Doc(W, top + 82, "Thank you for reading")
    cx, y = W / 2, top + 4
    d.css.append(f"""
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.8s {EASE_OUT} .2s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.8s {EASE_OUT} .2s both; }}
.dm {{ animation: fade 1s ease-out .8s both, breathe 5s ease-in-out 2s infinite; }}
.tx {{ animation: rise 1.4s {EASE_OUT} .6s both; }}
.cl {{ animation: fade 1.6s ease-out 1.1s both; }}
""")
    d.add(f'<line class="rl" x1="{cx - 190}" y1="{y}" x2="{cx - 12}" y2="{y}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<line class="rr" x1="{cx + 12}" y1="{y}" x2="{cx + 190}" y2="{y}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<g class="dm">{diamond(cx, y, 3.8, stroke=t["blush"], sw=1)}{diamond(cx, y, 1.5, fill=t["blush"])}</g>',
          '<g class="tx">', d.text(cx, top + 46, "Thank you for reading.", "serif-i", 20, t["soft"], anchor="middle"), "</g>",
          '<g class="cl">', d.text(cx, top + 76, "MEDWIN JOSE", "sans-m", 9, t["muted"], anchor="middle", tracking=4.5), "</g>")
    d.save(f"footer-{theme}.svg")


def main() -> None:
    knight()
    for theme, t in THEMES.items():
        header(t, theme)
        for i, (key, label) in enumerate(LINKS):
            chip(t, theme, key, label, i)
        for s in SECTIONS:
            section(t, theme, *s)
        instruments(t, theme)
        for i, p in enumerate(PROJECTS):
            card(t, theme, p, i)
        footer(t, theme)


if __name__ == "__main__":
    main()
