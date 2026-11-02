"""Build every static SVG used by the profile README (dark + light variants).

    python scripts/build_assets.py

The contribution city is built separately by scripts/city.py (hourly action).
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape
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
    "Curious by nature: I love research, wherever the question leads.",
]


def header(t: dict, theme: str) -> None:
    d = Doc(W, 170, "Medwin Jose — building systems that stay correct when participants misbehave")
    cx = W / 2
    n = len(TAGLINES)
    cycle = 4.5 * n                      # each line owns a 4.5s slot
    slot = 100 / n                       # its share of the cycle, in percent
    fade_in, hold = slot * .17, slot * .83  # ~0.75s in, ~3s hold, ~0.75s out; never overlapping
    d.css.append(f"""
.k  {{ animation: fade 1s ease-out 0s both; }}
.nm {{ animation: rise 1.4s {EASE_OUT} .1s both; }}
.rl {{ transform-box: fill-box; transform-origin: 100% 50%; animation: drawx 1.2s {EASE_OUT} .35s both; }}
.rr {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.2s {EASE_OUT} .35s both; }}
.dm {{ animation: fade .8s ease-out .6s both, breathe 5s ease-in-out 1.6s infinite; }}
.tl {{ opacity: 0; animation: cycle {cycle}s cubic-bezier(.4,0,.2,1) infinite both; }}
.t1 {{ opacity: 1; }}
@keyframes cycle {{ 0% {{ opacity: 0; transform: translateY(6px) }} {fade_in:.2f}% {{ opacity: 1; transform: none }}
  {hold:.2f}% {{ opacity: 1; transform: none }} {slot:.2f}% {{ opacity: 0; transform: translateY(-6px) }} 100% {{ opacity: 0 }} }}
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
def knight_parts(d: Doc) -> str:
    """The knight in its own 300x300 drawing space; returns markup and adds its CSS to ``d``.

    Every 13 seconds it looks left, looks right, tilts its head with a little
    "?", then has an "aha" moment: happy squinting eyes, a tiny hop and two
    sparkles. It blinks on its own rhythm. Pivots use fill-box so the figure
    can be placed and scaled anywhere.
    """
    mask, eye, cloak, rim, line = "#F8F6FF", "#0F0E17", "#363859", "#A79BF5", "#2B2944"
    lav, lav_dk, blush, mint = "#B7AAFF", "#8C7EE6", "#FFB4C8", "#93E6CC"
    d.css.append("""
.kn-all  { animation: bob 2.8s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(0) } to { transform: translateY(-5px) } }
.kn-hop  { animation: hop 13s ease-in-out infinite; }
@keyframes hop { 0%, 66% { transform: none } 69% { transform: translateY(-9px) } 72% { transform: none }
  74.5% { transform: translateY(-4px) } 77%, 100% { transform: none } }
.kn-shadow { transform-box: fill-box; transform-origin: center; animation: shrink 2.8s ease-in-out infinite alternate; }
@keyframes shrink { from { transform: scaleX(1); opacity: .5 } to { transform: scaleX(.86); opacity: .32 } }
.kn-head { transform-box: fill-box; transform-origin: 50% 96%; animation: look 13s ease-in-out infinite; }
@keyframes look {
  0%, 8%    { transform: none }
  12%, 22%  { transform: translateX(-5px) rotate(-3deg) }
  28%, 38%  { transform: translateX(5px) rotate(3deg) }
  44%, 58%  { transform: rotate(-11deg) }
  64%, 80%  { transform: rotate(3deg) }
  86%, 100% { transform: none } }
.kn-eyes { animation: glance 13s ease-in-out infinite; }
@keyframes glance {
  0%, 8%    { transform: none }
  12%, 22%  { transform: translateX(-6px) }
  28%, 38%  { transform: translateX(6px) }
  44%, 58%  { transform: translate(-2px, 1px) }
  64%, 100% { transform: none } }
.kn-open  { animation: open 13s step-end infinite; }
@keyframes open { 0% { opacity: 1 } 65% { opacity: 0 } 81% { opacity: 1 } }
.kn-happy { opacity: 0; animation: happy 13s step-end infinite; }
@keyframes happy { 0% { opacity: 0 } 65% { opacity: 1 } 81% { opacity: 0 } }
@media (prefers-reduced-motion: reduce) { .kn-happy { display: none } }
.kn-blink { transform-box: fill-box; transform-origin: center; animation: blink 4.6s ease-in-out infinite; }
@keyframes blink { 0%, 44%, 52%, 100% { transform: none } 48% { transform: scaleY(.08) } }
.kn-cloak { transform-box: fill-box; transform-origin: 50% 0; animation: sway 2.8s ease-in-out infinite alternate; }
@keyframes sway { from { transform: skewX(1.6deg) } to { transform: skewX(-1.6deg) } }
.kn-tail  { transform-box: fill-box; transform-origin: 0 25%; animation: flutter 2.2s ease-in-out infinite alternate; }
@keyframes flutter { from { transform: rotate(-7deg) } to { transform: rotate(6deg) } }
.kn-q     { transform-box: fill-box; transform-origin: 50% 100%; animation: wonder 13s ease-in-out infinite; }
@keyframes wonder { 0%, 44% { opacity: 0; transform: translateY(6px) scale(.6) }
  48%, 57% { opacity: 1; transform: none } 61%, 100% { opacity: 0; transform: translateY(-4px) } }
.kn-spark { transform-box: fill-box; transform-origin: center; animation: spark 13s ease-out infinite; }
@keyframes spark { 0%, 65% { opacity: 0; transform: scale(.2) rotate(0) } 69% { opacity: 1; transform: scale(1.1) rotate(25deg) }
  76% { opacity: 1; transform: scale(1) rotate(45deg) } 81%, 100% { opacity: 0; transform: scale(.4) rotate(70deg) } }
.kn-mote  { animation: drift linear infinite; }
@keyframes drift { 0% { transform: translateY(0); opacity: 0 } 15% { opacity: .9 } 100% { transform: translateY(-120px); opacity: 0 } }
.kn-glow  { transform-box: fill-box; transform-origin: center; animation: breathe 6s ease-in-out infinite; }
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
        return f'<path class="kn-spark" d="{path}" fill="{color}" style="animation-delay:{delay}s"/>'

    out = [f'<circle class="kn-glow" cx="150" cy="160" r="118" fill="url(#halo)"/>']
    for x, y, r, col, dur, delay in [(78, 250, 2.2, lav, 7, 0), (222, 236, 1.8, blush, 8.5, 2.2), (104, 210, 1.5, mint, 6.5, 4),
                                     (204, 268, 2, lav, 9, 1.1), (60, 190, 1.4, blush, 7.5, 5.4), (238, 200, 1.6, mint, 8, 3.3)]:
        out.append(f'<circle class="kn-mote" cx="{x}" cy="{y}" r="{r}" fill="{col}" '
                   f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>')
    out += [
        f'<ellipse class="kn-shadow" cx="150" cy="271" rx="44" ry="5.5" fill="{lav}" opacity=".45"/>',
        '<g class="kn-all"><g class="kn-hop">',
        f'<rect x="136" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
        f'<rect x="155" y="246" width="9" height="20" rx="4" fill="{cloak}" stroke="{rim}" stroke-width="1.2"/>',
        f'<g class="kn-cloak"><path d="M124 170 C110 198 103 228 98 254 C116 247 133 254 150 248 C167 254 184 247 202 254 '
        f'C197 228 190 198 176 170 Z" fill="{cloak}" stroke="{rim}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<path d="M150 200 V242" stroke="{rim}" stroke-width="1" opacity=".35"/></g>',
        f'<g class="kn-tail"><path d="M168 190 C182 198 198 203 214 199 L211 212 C195 216 179 210 166 200 Z" fill="{lav}" '
        f'stroke="{lav_dk}" stroke-width="1.2" stroke-linejoin="round"/>'
        f'<path d="M205 201 L203 213" stroke="{blush}" stroke-width="3"/></g>',
        f'<path d="M118 180 Q150 198 182 180 L184 191 Q150 211 116 191 Z" fill="{lav}" stroke="{lav_dk}" '
        f'stroke-width="1.2" stroke-linejoin="round"/>',
        f'<path d="M120 187 Q150 204 180 187" fill="none" stroke="{blush}" stroke-width="2.2" stroke-linecap="round"/>',
        '<g class="kn-head">', horn(-1), horn(1),
        f'<path d="M106 136 C106 98 194 98 194 136 C194 170 176 186 150 186 C124 186 106 170 106 136 Z" fill="{mask}" '
        f'stroke="{line}" stroke-width="2.2"/>',
        '<path d="M114 160 C122 176 136 182 150 182" fill="none" stroke="#DCD6F2" stroke-width="2" stroke-linecap="round" opacity=".7"/>',
        '<g class="kn-eyes"><g class="kn-open"><g class="kn-blink">',
        f'<ellipse cx="131" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
        f'<ellipse cx="169" cy="143" rx="10.5" ry="16" fill="{eye}"/>',
        '<circle cx="127" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
        '<circle cx="165" cy="135" r="2.6" fill="#FFFFFF" opacity=".85"/>',
        '</g></g>',
        f'<g class="kn-happy" fill="none" stroke="{eye}" stroke-width="4.5" stroke-linecap="round">'
        '<path d="M121 147 Q131 133 141 147"/><path d="M159 147 Q169 133 179 147"/></g>',
        '</g>',
        f'<ellipse cx="121" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
        f'<ellipse cx="179" cy="164" rx="6" ry="3" fill="{blush}" opacity=".55"/>',
        '</g>',
        '<g class="kn-q">', d.text(212, 92, "?", "serif-bi", 34, blush), "</g>",
        star(214, 84, 9, mint, 0), star(90, 100, 6, blush, .15),
        "</g></g>",
    ]
    return "".join(out)


# ==========================================================================
# About: the knight and the text set together in one image, so the knight
# stays vertically centred beside the text at every window width.
# ==========================================================================
ABOUT = [
    [("I study and build ", "sans"), ("systems that stay correct when some of their participants misbehave", "sans-sb"),
     (": networks where peers lie, markets where traders game the order book, and pipelines where one bad input "
      "should never take everything down. My work sits where distributed systems meet security, mostly in Rust.", "sans")],
    [("I like the unglamorous parts of engineering: specifying behaviour before writing code, testing properties "
      "instead of examples, and publishing every number with the command that produced it.", "sans")],
]
INTERESTS = ["distributed systems", "formal methods", "security"]


def rich_lines(runs: list, size: float, width: float) -> list:
    """Greedy word wrap over runs of (text, face); returns lines of [text, face] segments."""
    words, glue = [], False  # glue: the next word attaches to the previous one without a space
    for text, face in runs:
        parts = text.split(" ")
        for i, w in enumerate(parts):
            if w:
                words.append((w, face, i == 0 and glue))
            glue = False
        glue = not text.endswith(" ")
    lines, line, x = [], [], 0.0
    for w, face, attached in words:
        space = 0.0 if (not line or attached) else measure(face, " ", size)
        ww = measure(face, w, size)
        if line and not attached and x + space + ww > width:
            lines.append(line)
            line, x, space = [], 0.0, 0.0
        piece = (" " if space else "") + w
        if line and line[-1][1] == face:
            line[-1][0] += piece
        else:
            line.append([piece, face])
        x += space + ww
    if line:
        lines.append(line)
    return lines


def about(t: dict, theme: str) -> None:
    size, lead, gap = 15, 25, 15
    tx, tw = 246, W - 246 - 14          # text column
    blocks = [rich_lines(p, size, tw) for p in ABOUT]
    n_lines = sum(len(b) for b in blocks) + 2  # + research label and its line
    text_h = n_lines * lead + gap * len(blocks)
    top = 1                             # first cap-height lands 4px down, like every other block
    H = int(top + text_h + 4)           # bottom padding matched to the Instruments block (measured)

    d = Doc(W, H, "About Medwin Jose: " + " ".join("".join(s for s, _ in p) for p in ABOUT))
    d.css.append(f".ab {{ animation: rise 1.2s {EASE_OUT} both; }}")

    # Knight, scaled to the text block and centred on it.
    s = min(.74, (text_h + 8) / 236)
    kx, ky = 112 - 150 * s, top + text_h / 2 - 160 * s - 4
    d.add(f'<g transform="translate({kx:.1f},{ky:.1f}) scale({s:.3f})">{knight_parts(d)}</g>')

    y = top + 15  # first baseline: cap-height of 15px Inter sits on the block's top edge
    k = 0
    for block in blocks:
        for li, line in enumerate(block):
            words = []  # (text, face, space_before)
            for text, face in line:
                for j, w in enumerate(text.split(" ")):
                    if w:
                        words.append((w, face, j > 0 or (bool(words) and text.startswith(" "))))
            natural = sum(measure(f, w, size) for w, f, _ in words)
            spaces = [i for i, (_, _, sp) in enumerate(words) if sp and i]
            space_w = measure("sans", " ", size)
            last = li == len(block) - 1
            extra = 0 if last or not spaces else (tw - natural - space_w * len(spaces)) / len(spaces)
            x, spans = tx, []
            for i, (w, f, sp) in enumerate(words):
                if i and sp:
                    x += space_w + extra
                d.use_glyphs(f, w)
                spans.append(f'<tspan x="{x:.2f}" class="f-{f}">{escape(w)}</tspan>')
                x += measure(f, w, size)
            d.add(f'<g class="ab" style="animation-delay:{.1 + k * .06:.2f}s">'
                  f'<text y="{y}" font-size="{size}" fill="{t["ink"]}">{"".join(spans)}</text></g>')
            y += lead
            k += 1
        y += gap
    # Research interests: a small-caps label, then the fields spread across the
    # full column width (matching the justified text) with twinkling diamonds.
    d.css.append(".tw { transform-box: fill-box; transform-origin: center; animation: tw 7s ease-in-out infinite; }\n"
                 "@keyframes tw { 0%, 80%, 100% { transform: none; opacity: 1 } 88% { transform: scale(1.8) rotate(45deg); opacity: .5 } }")
    d.add(f'<g class="ab" style="animation-delay:{.1 + k * .06:.2f}s">',
          d.text(tx, y - 4, "RESEARCH INTERESTS", "sans-sb", 8.5, t["accent"], tracking=2.4))
    y += lead - 6
    pieces = [(item, "sans", size, 0) for item in INTERESTS] + [("always open to new ones", "serif-i", size + 2.5, .5)]
    widths = [measure(f, w, sz) for w, f, sz, _ in pieces]
    sep = (tw - sum(widths)) / (len(pieces) - 1)   # equal space around each diamond
    x = tx
    for i, ((w, f, sz, dy), wd) in enumerate(zip(pieces, widths)):
        if i:
            d.add(f'<g class="tw" style="animation-delay:{2 + i * 1.2:.1f}s">'
                  f'{diamond(x - sep / 2, y - 4.6, 2.2, fill=t["accent"])}</g>')
        d.add(d.text(x, y + dy, w, f, sz, t["soft"]))
        x += wd + sep
    d.add("</g>")
    d.save(f"about-{theme}.svg")


# ==========================================================================
# Section openers
# ==========================================================================
SECTIONS = [
    ("about", "I.", "About", "A LITTLE ABOUT ME"),
    ("instruments", "II.", "Instruments", "LANGUAGES, SYSTEMS  &  METHODS"),
    ("work", "III.", "Selected Work", "TWO SYSTEMS, ONE QUESTION"),
    ("city", "IV.", "The City", "MY CONTRIBUTIONS, REBUILT EVERY FEW MINUTES"),
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
.ed {{ animation: fade 1s ease-out 1.6s both, breathe 5s ease-in-out 2.6s infinite; }}
.sb {{ animation: fade 1.4s ease-out .7s both; }}
""")
    # A faint light travels outward along both rules every 10 seconds.
    for gid, x1, x2, vals in (("gl", 0, -80, "0 0;-700 0;-700 0"), ("gr", W, W + 80, "0 0;700 0;700 0")):
        d.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{W / 2 + (x1 - W / 2) * 0}" y1="0" '
                      f'x2="{W / 2 + (x2 - x1)}" y2="0">'
                      f'<stop offset="0" stop-color="{t["accent_hi"]}" stop-opacity="0"/>'
                      f'<stop offset=".5" stop-color="{t["accent_hi"]}" stop-opacity=".9"/>'
                      f'<stop offset="1" stop-color="{t["accent_hi"]}" stop-opacity="0"/>'
                      f'<animateTransform attributeName="gradientTransform" type="translate" values="{vals}" '
                      f'keyTimes="0;.3;1" dur="10s" begin="2.5s" repeatCount="indefinite"/></linearGradient>')
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
          f'<line x1="84" y1="{mid}" x2="{fmt(left_end)}" y2="{mid}" stroke="url(#gl)" stroke-width=".9"/>',
          f'<line x1="{fmt(right_start)}" y1="{mid}" x2="{W - 84}" y2="{mid}" stroke="url(#gr)" stroke-width=".9"/>',
          f'<g class="ed">{diamond(78, mid, 2.6, fill=t["accent"])}{diamond(W - 78, mid, 2.6, fill=t["accent"])}</g>',
          '<g class="sb">', d.text(W / 2, top + 50, sub, "sans-m", 9, t["muted"], anchor="middle", tracking=3.4), "</g>")
    d.save(f"section-{key}-{theme}.svg")


# ==========================================================================
# Selected work: two cards, each with a small animated motif
# ==========================================================================
CW, CH = 420, 154


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
    """A living order book: depth breathes, the mid price drifts, and every few
    seconds a spoof order appears on the ask side, is flagged, then cancelled."""
    out, base, x = [], 72, 2
    rng = random.Random(7)
    for h in [50, 43, 35, 28, 20, 12]:
        out.append(_bar(x, base, 6.5, h, t["mint"], rng))
        x += 9.5
    mid = x + 3
    out.append(f'<line x1="{fmt(mid)}" y1="4" x2="{fmt(mid)}" y2="{base}" stroke="{t["accent"]}" stroke-width=".9" '
               f'stroke-dasharray="1.6 2.4" opacity=".9"><animate attributeName="stroke-dashoffset" values="0;-8" '
               f'dur="1.6s" repeatCount="indefinite"/></line>')
    x += 6
    ask0 = x
    for h in [13, 21, 29, 36, 44, 52]:
        out.append(_bar(x, base, 6.5, h, t["blush"], rng))
        x += 9.5
    # The spoof: a tall order stacked on the second ask level, flagged, then pulled.
    sx, sh, dur, kt = ask0 + 9.5, 46, "6s", "0;.18;.26;.62;.72;1"
    out.append(f'<rect x="{fmt(sx)}" y="{base - 21 - sh}" width="6.5" height="{sh}" rx="1" fill="{t["blush"]}" opacity="0">'
               f'<animate attributeName="opacity" values="0;0;.55;.55;0;0" keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/></rect>')
    out.append(f'<rect x="{fmt(sx - 3)}" y="{base - 21 - sh - 3}" width="12.5" height="{sh + 6}" rx="2.5" fill="none" '
               f'stroke="{t["accent"]}" stroke-width=".8" stroke-dasharray="2 2" opacity="0">'
               f'<animate attributeName="opacity" values="0;0;0;.95;0;0" keyTimes="0;.18;.34;.44;.62;1" dur="{dur}" '
               f'repeatCount="indefinite"/></rect>')
    out.append(f'<line x1="0" y1="{base + .5}" x2="{fmt(x)}" y2="{base + .5}" stroke="{t["muted"]}" stroke-width=".6" opacity=".6"/>')
    return "".join(out)


def _bar(x, base, w, h, color, rng) -> str:
    """One depth bar that breathes from its base (SMIL, so it animates everywhere)."""
    dur = rng.uniform(2.6, 4.4)
    lo = h * rng.uniform(.62, .78)
    begin = rng.uniform(0, 2)
    vals_h = f"{h:.1f};{lo:.1f};{h:.1f}"
    vals_y = f"{base - h:.1f};{base - lo:.1f};{base - h:.1f}"
    anim = (f'<animate attributeName="height" values="{vals_h}" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
            f'<animate attributeName="y" values="{vals_y}" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    return (f'<rect x="{fmt(x)}" y="{fmt(base - h)}" width="{fmt(w)}" height="{fmt(h)}" rx="1" fill="{color}" '
            f'fill-opacity=".8">{anim}</rect>')


PROJECTS = [  # a hook only; the repositories hold the detail
    dict(key="crci", url="crci", kicker="DISTRIBUTED SYSTEMS  ·  PREPRINT", title="CRCI", motif=motif_crci,
         hook="Byzantine-fault-tolerant mesh networking, without consensus.",
         figure=("< 1 ms", "TO ISOLATE A MISBEHAVING PEER")),
    dict(key="sentinel", url="sentinel", kicker="MARKET MICROSTRUCTURE", title="SENTINEL", motif=motif_sentinel,
         hook="Market-making that defends itself against toxic order flow.",
         figure=("+10,843.99", "TICKS SAVED UNDER TOXIC FLOW")),
]


def card(t: dict, theme: str, p: dict, index: int) -> None:
    """A compact card on a strict 26px inner margin; type scaled down so it breathes."""
    d = Doc(CW, CH, f"{p['title']}: {p['hook']} {p['figure'][0]} {p['figure'][1].lower()}")
    delay = .15 + index * .12
    d.css.append(f"""
.cd {{ animation: rise 1.3s {EASE_OUT} {delay:.2f}s both; }}
.ac {{ transform-box: fill-box; transform-origin: 0 50%; animation: drawx 1.4s {EASE_OUT} {delay + .5:.2f}s both; }}
.ar {{ animation: nudge 6s ease-in-out {3 + index * .7:.1f}s infinite; }}
@keyframes nudge {{ 0%, 86%, 100% {{ transform: none }} 92% {{ transform: translateX(3px) }} }}
""")
    # A soft light that glides along the card's top accent every few seconds.
    d.defs.append(f'<linearGradient id="glint" gradientUnits="userSpaceOnUse" x1="-60" y1="0" x2="0" y2="0">'
                  f'<stop offset="0" stop-color="{t["accent_hi"]}" stop-opacity="0"/>'
                  f'<stop offset=".5" stop-color="{t["accent_hi"]}" stop-opacity=".9"/>'
                  f'<stop offset="1" stop-color="{t["accent_hi"]}" stop-opacity="0"/>'
                  f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;160 0;160 0" '
                  f'keyTimes="0;.25;1" dur="8s" begin="{3 + index * 1.5:.1f}s" repeatCount="indefinite"/></linearGradient>')
    top, pad, side = 4, 30, 14          # side: margin outside the card, so the pair has a 28px gutter
    x0, L, R = side, side + pad, CW - side - pad
    value, label = p["figure"]
    kicker_base = top + pad + 6          # cap-height of 8px Inter sits on the inner margin
    title_base = kicker_base + 26
    hook_base = title_base + 22
    fig_base = hook_base + 28
    rect_h = fig_base + 4 + pad - top    # same 26px margin below the figure's descenders
    d.add('<g class="cd">',
          f'<rect x="{x0}" y="{top}" width="{CW - 2 * side}" height="{rect_h}" rx="12" fill="{t["surface"]}" stroke="{t["border"]}"/>',
          f'<line class="ac" x1="{L}" y1="{top + .5}" x2="{L + 40}" y2="{top + .5}" stroke="{t["accent"]}" stroke-width="1.2"/>',
          f'<line x1="{L}" y1="{top + .5}" x2="{L + 40}" y2="{top + .5}" stroke="url(#glint)" stroke-width="1.2"/>',
          d.text(L, kicker_base, p["kicker"], "sans-m", 8, t["accent"], tracking=2.2),
          d.text(L, title_base, p["title"], "serif-b", 22, t["ink"]))
    # Motif: right-aligned to the inner margin, top-aligned with the kicker's cap-height.
    ms = .46
    d.add(f'<g transform="translate({R - 118 * ms:.1f},{top + pad:.1f}) scale({ms})">{p["motif"](t)}</g>')
    size = 13.5
    while measure("serif-i", p["hook"], size) > R - L:
        size -= .25
    d.add(d.text(L, hook_base, p["hook"], "serif-i", size, t["soft"]))
    d.add(d.text(L, fig_base, value, "serif-b", 16.5, t["ink"]),
          d.text(L + measure("serif-b", value, 16.5) + 8, fig_base, label, "sans-m", 7.5, t["muted"], tracking=1.3),
          f'<g class="ar">{arrow(R - 12, fig_base - 3.5, 12, t["accent"], 1.1)}</g>',
          "</g>")
    assert CH == top + rect_h + top, (CH, top + rect_h + top)
    d.save(f"card-{p['key']}-{theme}.svg")


# ==========================================================================
# Instruments
# ==========================================================================
INSTRUMENTS = [
    ("LANGUAGES", "accent", ["Rust", "Python", "Kotlin", "SQL", "JavaScript"]),
    ("SYSTEMS", "mint", ["Async I/O", "Applied cryptography", "Peer-to-peer networks", "APIs · WebSockets",
                         "Observability"]),
    ("METHODS", "blush", ["TLA+ specification", "Property-based testing", "Statistical modelling",
                          "Graph algorithms", "Reproducible benchmarks"]),
    ("INFRASTRUCTURE", "butter", ["Docker", "GitHub Actions", "AWS (certified)", "Linux", "ARM cross-builds"]),
]
RULE_L, RULE_R = 78, W - 78  # the end diamonds of every section rule


def instruments(t: dict, theme: str) -> None:
    d = Doc(W, 212, "Languages, systems, methods and infrastructure")  # bottom pad matches a paragraph margin
    d.css.append(f"""
.col {{ animation: rise 1.3s {EASE_OUT} both; }}
.sep {{ transform-box: fill-box; transform-origin: 50% 0; animation: drawy 1.6s {EASE_OUT} .3s both; }}
.ul  {{ transform-box: fill-box; transform-origin: center; animation: pulse 8s ease-in-out infinite; }}
@keyframes pulse {{ 0%, 70%, 100% {{ transform: scaleX(1); opacity: 1 }} 80% {{ transform: scaleX(1.9); opacity: .55 }} }}
""")
    size, hsize, htrack = 17, 9, 3
    widths = [max([measure("sans-sb", h, hsize, htrack)] + [measure("serif", it, size) for it in items])
              for h, _, items in INSTRUMENTS]
    gap = (RULE_R - RULE_L - sum(widths)) / (len(widths) - 1)
    x, centres = RULE_L, []
    for w in widths:
        centres.append(x + w / 2)
        x += w + gap
    for i in range(1, len(widths)):  # separators sit exactly halfway between neighbouring columns
        sx = (centres[i - 1] + widths[i - 1] / 2 + centres[i] - widths[i] / 2) / 2
        d.add(f'<line class="sep" x1="{sx:.1f}" y1="4" x2="{sx:.1f}" y2="196" stroke="{t["rule"]}" stroke-width=".8"/>')
    for i, ((head, color, items), cx) in enumerate(zip(INSTRUMENTS, centres)):
        c = t[color]
        d.add(f'<g class="col" style="animation-delay:{.15 + i * .14:.2f}s">',
              d.text(cx, 16, head, "sans-sb", hsize, c, anchor="middle", tracking=htrack),
              f'<line class="ul" x1="{cx - 11:.1f}" y1="29" x2="{cx + 11:.1f}" y2="29" stroke="{c}" stroke-width="1.2" '
              f'stroke-linecap="round" style="animation-delay:{3 + i * 2:.1f}s"/>')
        for k, item in enumerate(items):
            d.add(d.text(cx, 64 + k * 30, item, "serif", size, t["ink"], anchor="middle"))
        d.add("</g>")
    d.save(f"instruments-{theme}.svg")


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
    for theme, t in THEMES.items():
        header(t, theme)
        about(t, theme)
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
