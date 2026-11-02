"""Build every static SVG used by the profile README (dark + light variants).

    python scripts/build_assets.py

The contribution city is built separately by scripts/city.py (hourly action).
"""

from __future__ import annotations

import math

from svgkit import EASE_OUT, THEMES, Doc, arrow_ne, diamond, fmt, measure

W = 840  # Matches the README column; images scale down on smaller screens.


# ==========================================================================
# Masthead
# ==========================================================================
TAGLINES = [
    "Building systems that stay correct when participants misbehave.",
    "Quietly obsessed with correctness, latency and good typography.",
    "Every claim backed by a benchmark you can rerun.",
]


def header(t: dict, theme: str) -> None:
    d = Doc(W, 262, "Medwin Jose — building systems that stay correct when participants misbehave")
    cx = W / 2
    n = len(TAGLINES)
    cycle = 4.5 * n
    d.css.append(f"""
.k  {{ animation: fade 1.4s ease-out .1s both; }}
.nm {{ animation: rise 1.8s {EASE_OUT} .25s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.6s {EASE_OUT} 1s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.6s {EASE_OUT} 1s both; }}
.dm {{ animation: fade 1s ease-out 1.5s both, breathe 5s ease-in-out 2.5s infinite; }}
.tl {{ opacity: 0; animation: cycle {cycle}s ease-in-out infinite both; }}
.t1 {{ opacity: 1; }}
@keyframes cycle {{ 0% {{ opacity: 0; transform: translateY(5px) }} 5% {{ opacity: 1; transform: none }}
  29% {{ opacity: 1; transform: none }} 33.3% {{ opacity: 0; transform: translateY(-4px) }} 100% {{ opacity: 0 }} }}
@media (prefers-reduced-motion: reduce) {{ .tl:not(.t1) {{ display: none }} }}
.mt {{ animation: fade 1.6s ease-out 2.3s both; }}
""")
    kick = "HELLO, I AM"
    kw = measure("sans-m", kick, 10.5, 5)
    d.add('<g class="k">',
          d.text(cx, 52, kick, "sans-m", 10.5, t["accent"], anchor="middle", tracking=5),
          diamond(cx - kw / 2 - 18, 48.5, 2.6, fill=t["blush"]),
          diamond(cx + kw / 2 + 18, 48.5, 2.6, fill=t["mint"]),
          "</g>")

    # Name with a soft lavender-to-blush sheen drifting across it now and then.
    name = "MEDWIN JOSE"
    d.defs.append(
        f'<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="-40" y2="0">'
        f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
        f'<stop offset=".35" stop-color="{t["accent"]}" stop-opacity=".9"/>'
        f'<stop offset=".65" stop-color="{t["blush"]}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{t["blush"]}" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1250 0;1250 0" '
        f'keyTimes="0;.24;1" dur="11s" begin="2.6s" repeatCount="indefinite"/></linearGradient>'
    )
    d.add('<g class="nm">',
          d.text(cx, 128, name, "serif", 70, t["ink"], anchor="middle", tracking=17),
          d.text(cx, 128, name, "serif", 70, "url(#sheen)", anchor="middle", tracking=17),
          "</g>")

    y = 158
    d.add(f'<line class="rl" x1="262" y1="{y}" x2="{cx - 14}" y2="{y}" stroke="{t["accent"]}" stroke-width=".9" opacity=".75"/>',
          f'<line class="rr" x1="{cx + 14}" y1="{y}" x2="{W - 262}" y2="{y}" stroke="{t["accent"]}" stroke-width=".9" opacity=".75"/>',
          f'<g class="dm">{diamond(cx, y, 4.4, stroke=t["blush"], sw=1)}{diamond(cx, y, 1.7, fill=t["blush"])}</g>')

    for i, line in enumerate(TAGLINES):
        d.add(f'<g class="tl t{i + 1}" style="animation-delay:{1.9 + i * cycle / n:.2f}s">',
              d.text(cx, 201, line, "serif-i", 23.5, t["soft"], anchor="middle"), "</g>")

    d.add('<g class="mt">',
          d.text(cx, 242, "SYSTEMS  ·  RESEARCH  ·  ENGINEERING", "sans-m", 10, t["muted"], anchor="middle", tracking=4),
          "</g>")
    d.save(f"header-{theme}.svg")


def chip(t: dict, theme: str, key: str, label: str) -> None:
    tw = measure("sans-m", label, 10, 2.2)
    w, h = tw + 58, 36
    d = Doc(int(math.ceil(w)) + 4, h + 4, label.title())
    d.css.append(f"""
.c {{ animation: rise 1.2s {EASE_OUT} 2.6s both; }}
.ar {{ animation: nudge 6s ease-in-out 4s infinite; }}
@keyframes nudge {{ 0%, 86%, 100% {{ transform: none }} 92% {{ transform: translate(2px,-2px) }} }}
""")
    d.add('<g class="c">',
          f'<rect x="2" y="2" width="{fmt(w)}" height="{h}" rx="{h / 2}" fill="none" stroke="{t["border"]}"/>',
          d.text(24, 2 + h / 2 + 3.6, label, "sans-m", 10, t["soft"], tracking=2.2),
          f'<g class="ar">{arrow_ne(24 + tw + 10, 2 + h / 2 - 4, 8, t["accent"], 1.1)}</g>',
          "</g>")
    d.save(f"link-{key}-{theme}.svg")


# ==========================================================================
# The Knight: a small companion who looks around, tilts its head and blinks.
# One file; the white mask and outlined cloak read on both themes.
# ==========================================================================
def knight() -> None:
    S = 300
    d = Doc(S + 20, S, "A small horned knight looking around curiously")
    mask, eye, cloak, rim, line = "#F8F6FF", "#0F0E17", "#363859", "#A79BF5", "#2B2944"
    lav, blush, mint = "#B7AAFF", "#FFB4C8", "#93E6CC"
    d.css.append("""
.all   { animation: bob 2.8s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(0) } to { transform: translateY(-5px) } }
.shadow { transform-box: fill-box; transform-origin: center; animation: shrink 2.8s ease-in-out infinite alternate; }
@keyframes shrink { from { transform: scaleX(1); opacity: .5 } to { transform: scaleX(.86); opacity: .32 } }
.head  { transform-box: view-box; transform-origin: 150px 182px; animation: look 11s ease-in-out infinite; }
@keyframes look {
  0%, 10%   { transform: none }
  15%, 30%  { transform: translateX(-5px) rotate(-3deg) }
  36%, 52%  { transform: translateX(5px) rotate(3deg) }
  58%, 76%  { transform: rotate(-11deg) }
  82%, 100% { transform: none } }
.eyes  { animation: glance 11s ease-in-out infinite; }
@keyframes glance {
  0%, 10%   { transform: none }
  15%, 30%  { transform: translateX(-6px) }
  36%, 52%  { transform: translateX(6px) }
  58%, 76%  { transform: translate(-2px, 1px) }
  82%, 100% { transform: none } }
.blink { transform-box: fill-box; transform-origin: center; animation: blink 4.6s ease-in-out infinite; }
@keyframes blink { 0%, 44%, 52%, 100% { transform: none } 48% { transform: scaleY(.08) } }
.cloak { transform-box: view-box; transform-origin: 150px 176px; animation: sway 2.8s ease-in-out infinite alternate; }
@keyframes sway { from { transform: skewX(1.6deg) } to { transform: skewX(-1.6deg) } }
.q     { transform-box: fill-box; transform-origin: 50% 100%; animation: wonder 11s ease-in-out infinite; }
@keyframes wonder { 0%, 58% { opacity: 0; transform: translateY(6px) scale(.6) }
  63%, 74% { opacity: 1; transform: none } 79%, 100% { opacity: 0; transform: translateY(-4px) } }
.mote  { animation: drift linear infinite; }
@keyframes drift { 0% { transform: translateY(0); opacity: 0 } 15% { opacity: .9 } 100% { transform: translateY(-120px); opacity: 0 } }
.glow  { transform-box: fill-box; transform-origin: center; animation: breathe 6s ease-in-out infinite; }
""")
    d.defs.append(f'<radialGradient id="halo"><stop offset="0" stop-color="{lav}" stop-opacity=".32"/>'
                  f'<stop offset="1" stop-color="{lav}" stop-opacity="0"/></radialGradient>')

    def horn(sign: int) -> str:
        m = (lambda x: x) if sign < 0 else (lambda x: 300 - x)
        return (f'<path d="M{m(115)} 116 C{m(106)} 98 {m(100)} 78 {m(106)} 52 C{m(114)} 72 {m(124)} 90 {m(138)} 106 Z" '
                f'fill="{mask}" stroke="{line}" stroke-width="2.2" stroke-linejoin="round"/>')

    # Soft halo and drifting motes behind the knight.
    d.add(f'<circle class="glow" cx="150" cy="160" r="118" fill="url(#halo)"/>')
    for x, y, r, col, dur, delay in [(78, 250, 2.2, lav, 7, 0), (222, 236, 1.8, blush, 8.5, 2.2), (104, 210, 1.5, mint, 6.5, 4),
                                     (204, 268, 2, lav, 9, 1.1), (60, 190, 1.4, blush, 7.5, 5.4), (238, 200, 1.6, mint, 8, 3.3)]:
        d.add(f'<circle class="mote" cx="{x}" cy="{y}" r="{r}" fill="{col}" style="animation-duration:{dur}s;animation-delay:{delay}s"/>')

    d.add(f'<ellipse class="shadow" cx="150" cy="271" rx="44" ry="5.5" fill="{lav}" opacity=".45"/>',
          '<g class="all">',
          # legs
          f'<rect x="136" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
          f'<rect x="155" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
          # cloak
          f'<g class="cloak"><path d="M124 170 C110 198 103 228 98 254 C116 247 133 254 150 248 C167 254 184 247 202 254 '
          f'C197 228 190 198 176 170 Z" fill="{cloak}" stroke="{rim}" stroke-width="1.4" stroke-linejoin="round"/>'
          f'<path d="M150 186 V242" stroke="{rim}" stroke-width="1" opacity=".35"/></g>',
          # head: horns, mask, eyes
          '<g class="head">', horn(-1), horn(1),
          f'<path d="M106 136 C106 98 194 98 194 136 C194 170 176 186 150 186 C124 186 106 170 106 136 Z" fill="{mask}" stroke="{line}" stroke-width="2.2"/>',
          f'<path d="M114 160 C122 176 136 182 150 182" fill="none" stroke="#DCD6F2" stroke-width="2" stroke-linecap="round" opacity=".7"/>',
          '<g class="eyes"><g class="blink">',
          f'<ellipse cx="131" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
          f'<ellipse cx="169" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
          f'<circle cx="127" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
          f'<circle cx="165" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
          '</g></g>',
          f'<ellipse cx="121" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
          f'<ellipse cx="179" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
          '</g>',
          # a curious little question mark during the head tilt
          '<g class="q">', d.text(212, 92, "?", "serif-bi", 34, blush), "</g>",
          "</g>")
    d.save("knight.svg")


# ==========================================================================
# Section openers
# ==========================================================================
SECTIONS = [
    ("about", "I.", "About", "A LITTLE ABOUT ME"),
    ("instruments", "II.", "Instruments", "LANGUAGES, SYSTEMS  &  METHODS"),
    ("city", "III.", "The City", "MY CONTRIBUTIONS, REBUILT EVERY HOUR"),
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
          d.text(x, base, num, "serif-bi", ns, t["accent"]),
          d.text(x + wn + gap, base, title, "serif", ts, t["ink"]),
          "</g>",
          f'<line class="rl" x1="78" y1="{mid}" x2="{fmt(left_end)}" y2="{mid}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<line class="rr" x1="{fmt(right_start)}" y1="{mid}" x2="{W - 78}" y2="{mid}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<g class="ed">{diamond(72, mid, 2.8, fill=t["blush"])}{diamond(W - 72, mid, 2.8, fill=t["mint"])}</g>',
          '<g class="sb">', d.text(W / 2, 92, sub, "sans-m", 9.5, t["muted"], anchor="middle", tracking=3.4), "</g>")
    d.save(f"section-{key}-{theme}.svg")


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
    d = Doc(W, 246, "Languages, systems, methods and infrastructure")
    d.css.append(f"""
.col {{ animation: rise 1.3s {EASE_OUT} both; }}
.sep {{ transform-box: fill-box; transform-origin: 50% 0; animation: drawy 1.6s {EASE_OUT} .3s both; }}
""")
    cw = W / 4
    for i in range(1, 4):
        d.add(f'<line class="sep" x1="{i * cw}" y1="26" x2="{i * cw}" y2="222" stroke="{t["rule"]}" stroke-width=".8"/>')
    for i, (head, color, items) in enumerate(INSTRUMENTS):
        cx = cw * i + cw / 2
        c = t[color]
        d.add(f'<g class="col" style="animation-delay:{.15 + i * .14:.2f}s">',
              d.text(cx, 42, head, "sans-sb", 9.5, c, anchor="middle", tracking=3),
              f'<line x1="{cx - 11}" y1="56" x2="{cx + 11}" y2="56" stroke="{c}" stroke-width="1.2" stroke-linecap="round"/>')
        for k, item in enumerate(items):
            size = 18.5
            while measure("serif", item, size) > cw - 20:
                size -= .5
            d.add(d.text(cx, 92 + k * 30, item, "serif", size, t["ink"], anchor="middle"))
        d.add("</g>")
    d.save(f"instruments-{theme}.svg")


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
    d.add(f'<line class="rl" x1="{cx - 210}" y1="{y}" x2="{cx - 14}" y2="{y}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<line class="rr" x1="{cx + 14}" y1="{y}" x2="{cx + 210}" y2="{y}" stroke="{t["accent"]}" stroke-width=".8" opacity=".6"/>',
          f'<g class="dm">{diamond(cx, y, 4.4, stroke=t["blush"], sw=1)}{diamond(cx, y, 1.7, fill=t["blush"])}</g>',
          '<g class="tx">', d.text(cx, 88, "Thank you for reading.", "serif-i", 22, t["soft"], anchor="middle"), "</g>",
          '<g class="cl">',
          d.text(cx, 124, "MEDWIN JOSE  ·  MMXXVI", "sans-m", 9.5, t["muted"], anchor="middle", tracking=4),
          d.text(cx, 146, "SET IN CORMORANT GARAMOND & INTER", "sans", 8, t["faint"], anchor="middle", tracking=3.2),
          "</g>")
    d.save(f"footer-{theme}.svg")


def main() -> None:
    knight()
    for theme, t in THEMES.items():
        header(t, theme)
        chip(t, theme, "linkedin", "LINKEDIN")
        for s in SECTIONS:
            section(t, theme, *s)
        instruments(t, theme)
        footer(t, theme)


if __name__ == "__main__":
    main()
