"""Wisp: the mascot, drawn as code.

Structure (all in a 1000x1000 drawing space, ground at y=900, Wisp centred on x=512):

  WORLD (background, theme-aware)       WISP (the character, identical everywhere)
  - halo behind Wisp                    - feet
  - ground glow + contact shadow        - cloak (with hem)
  - orbit ring, back half               - scarf tail, scarf wrap
  - crescent moon                       - head: shading, gloss, blush, eyes
  - stars and drifting specks
                                        FOREGROUND (world elements that pass in front)
                                        - orbit ring, front half, and its gliding light
                                        - expression effects: "?", thinking dots, sparkles

One light source (upper left) shades everything; one outline weight (8 units) is used
for every part of Wisp.

One 18-second expression loop:
  0-6 %   neutral          9-16 %  looks left        20-27 % looks right
  31-43 % curious tilt, a "?" springs up and settles
  47-58 % thinking: eyes up, three dots pop in one by one
  62-72 % "aha": happy eyes, a crouch, a double hop with squash and stretch, sparkles
  76-84 % a wink           88-100 % back to neutral
Independent rhythms layered on top: breathing (3.2 s), idle head drift (7.4 s), blinks
with an occasional double blink (7.6 s), two-layer scarf flutter (2.6 s + 1.7 s),
moon float, star drift and twinkle, a light gliding along the orbit ring.
"""

from __future__ import annotations

LOOP = 18  # seconds

# --- Silhouette (from Medwin's draft) ---------------------------------------------
HEAD = ("M618.4 154.7 C603.6 162.1 577.7 175.05 568.45 202.8 C562.9 226.85 588.8 243.5 620.25 256.45 "
        "C662.8 273.1 692.4 317.5 699.8 373 C705.35 422.95 681.3 474.75 644.3 515.45 "
        "C592.5 559.85 481.5 585.75 398.25 578.35 C324.25 567.25 272.45 493.25 266.9 422.95 "
        "C259.5 317.5 333.5 206.5 426 163.95 C481.5 138.05 555.5 132.5 618.4 154.7 Z")
CLOAK = ("M426 637.55 C398.25 687.5 361.25 770.75 337.2 826.25 C379.75 848.45 435.25 859.55 500 859.55 "
         "C570.3 859.55 644.3 848.45 694.25 828.1 C670.2 780 629.5 706 577.7 630.15 Z")
CLOAK_SHEEN = ("M418 660 C396 712 370 772 350 818 L366 823 C381 780 403 726 428 672 Z")
HEM = ("M339.05 824.4 C389 844.75 444.5 842.9 509.25 844.75 C574 844.75 638.75 833.65 692.4 815.15 "
       "L694.25 828.1 C644.3 850.3 570.3 861.4 500 861.4 C431.55 861.4 379.75 850.3 337.2 828.1 Z")
WRAP = ("M405.65 578.35 C453.75 570.95 546.25 550.6 638.75 532.1 L644.3 559.85 L629.5 576.5 L642.45 591.3 "
        "C611 615.35 537 637.55 466.7 643.1 C440.8 644.95 414.9 641.25 401.95 626.45 "
        "C392.7 611.65 396.4 589.45 405.65 578.35 Z")
WRAP_FOLD = ("M405.65 580.2 C426 576.5 448.2 578.35 459.3 585.75 C448.2 596.85 444.5 615.35 451.9 637.55 "
             "C429.7 641.25 407.5 633.85 400.1 619.05 C394.55 604.25 396.4 589.45 405.65 580.2 Z")
TAIL = ("M633.2 589.45 C685 600.55 731.25 585.75 773.8 556.15 C818.2 526.55 866.3 519.15 910.7 517.3 "
        "C907 558 901.45 604.25 895.9 652.35 C860.75 641.25 833 641.25 799.7 656.05 "
        "C768.25 669 731.25 674.55 703.5 663.45 C675.75 652.35 651.7 637.55 633.2 626.45 Z")
EYES = ((376.98, 482.15), (569.38, 434.05))  # left, right centres; both tilted -7.5deg with the head

# --- Palette (one hue family per material; one light source, upper left) ------------
OUTLINE, OUTLINE_W = "#1C1336", 8
INK = "#160E2C"            # closed / happy eye strokes
CX = 512                   # Wisp's centre line (between the feet)

# Orbit ring: one perfect ellipse, tilted, centred on Wisp at scarf height.
RING = dict(cx=CX, cy=655, rx=318, ry=70, tilt=-7)

# Horizontal / vertical extent of everything drawn, for layouts that fit Wisp to a column.
EXTENT_X = (190, 912)
EXTENT_Y = (64, 912)


def _star(cx: float, cy: float, r: float) -> str:
    k = r * .14
    return (f"M{cx:.1f} {cy - r:.1f} Q{cx + k:.1f} {cy - k:.1f} {cx + r:.1f} {cy:.1f} "
            f"Q{cx + k:.1f} {cy + k:.1f} {cx:.1f} {cy + r:.1f} Q{cx - k:.1f} {cy + k:.1f} {cx - r:.1f} {cy:.1f} "
            f"Q{cx - k:.1f} {cy - k:.1f} {cx:.1f} {cy - r:.1f} Z")


SINE = "cubic-bezier(.37,0,.63,1)"   # ease-in-out sine: the smoothest loop easing
GLIDE = "cubic-bezier(.45,0,.2,1)"   # for glances and turns


def _css() -> str:
    L = LOOP
    return f"""
/* ---------- Wisp: body ---------- */
.wp-bob    {{ animation: wpBob 3.2s {SINE} infinite alternate; }}
@keyframes wpBob {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-11px) }} }}
.wp-hop    {{ animation: wpHop {L}s linear infinite; }}
@keyframes wpHop {{
  0%, 61.6% {{ transform: none }}
  62.6%     {{ transform: translateY(5px); animation-timing-function: cubic-bezier(.2,.7,.4,1) }}
  63.6%     {{ transform: translateY(-30px); animation-timing-function: cubic-bezier(.6,0,.8,.4) }}
  64.8%     {{ transform: translateY(2px); animation-timing-function: cubic-bezier(.2,.7,.4,1) }}
  65.8%     {{ transform: translateY(-11px); animation-timing-function: cubic-bezier(.6,0,.8,.4) }}
  66.8%     {{ transform: translateY(1px) }}
  67.6%, 100% {{ transform: none }} }}
.wp-squash {{ transform-box: fill-box; transform-origin: 50% 100%; animation: wpSquash {L}s linear infinite; }}
@keyframes wpSquash {{
  0%, 61.6% {{ transform: none }}
  62.6%     {{ transform: scale(1.035, .955) }}
  63.6%     {{ transform: scale(.975, 1.035) }}
  64.8%     {{ transform: scale(1.03, .96) }}
  65.8%     {{ transform: scale(.99, 1.015) }}
  66.8%     {{ transform: scale(1.012, .985) }}
  67.6%, 100% {{ transform: none }} }}
.wp-breath {{ transform-box: fill-box; transform-origin: 50% 100%; animation: wpBreath 3.2s {SINE} infinite alternate; }}
@keyframes wpBreath {{ from {{ transform: scale(1, 1) }} to {{ transform: scale(1.008, 1.016) }} }}
.wp-cloak  {{ transform-box: fill-box; transform-origin: 50% 0; animation: wpSway 3.6s {SINE} infinite alternate; }}
@keyframes wpSway {{ from {{ transform: skewX(1.1deg) }} to {{ transform: skewX(-1.1deg) }} }}
.wp-tail   {{ transform-box: fill-box; transform-origin: 0 22%; animation: wpTail 2.6s {SINE} infinite alternate; }}
@keyframes wpTail {{ from {{ transform: rotate(-3.5deg) }} to {{ transform: rotate(4.5deg) }} }}
.wp-tail2  {{ transform-box: fill-box; transform-origin: 0 30%; animation: wpTail2 1.7s {SINE} infinite alternate; }}
@keyframes wpTail2 {{ from {{ transform: skewY(-1.4deg) scaleX(.99) }} to {{ transform: skewY(1.8deg) scaleX(1.01) }} }}
/* ---------- Wisp: head ---------- */
.wp-idle   {{ transform-box: fill-box; transform-origin: 47% 98%; animation: wpIdle 7.4s {SINE} infinite alternate; }}
@keyframes wpIdle {{ from {{ transform: rotate(-.8deg) }} to {{ transform: rotate(.9deg) }} }}
.wp-head   {{ transform-box: fill-box; transform-origin: 47% 98%; animation: wpLook {L}s {GLIDE} infinite; }}
@keyframes wpLook {{
  0%, 6%    {{ transform: none }}
  9.5%, 16% {{ transform: translateX(-13px) rotate(-3deg) }}
  20.5%, 27% {{ transform: translateX(13px) rotate(3deg) }}
  31.5%, 43% {{ transform: rotate(-9deg) }}
  47.5%, 58% {{ transform: translate(4px, -4px) rotate(4deg) }}
  62%, 72%  {{ transform: rotate(2deg) }}
  76%, 84%  {{ transform: rotate(5deg) }}
  89%       {{ transform: none }}
  91.2%     {{ transform: translateY(5px) rotate(-1.5deg) }}
  93.6%, 100% {{ transform: none }} }}
.wp-eyes   {{ animation: wpGlance {L}s {GLIDE} infinite; }}
@keyframes wpGlance {{
  0%, 5.6%  {{ transform: none }}
  8.6%, 16% {{ transform: translate(-22px, 2px) }}
  19.6%, 27% {{ transform: translate(22px, 0) }}
  31%, 43%  {{ transform: translate(-6px, 5px) }}
  47%, 58%  {{ transform: translate(12px, -20px) }}
  61%, 100% {{ transform: none }} }}
.wp-blink  {{ transform-box: fill-box; transform-origin: center; animation: wpBlink 7.6s ease-in-out infinite; }}
@keyframes wpBlink {{
  0%, 26%, 30%, 72%, 75.5%, 77%, 80.5%, 100% {{ transform: none }}
  28%, 73.8%, 78.8% {{ transform: scaleY(.06) }} }}
.wp-openl  {{ animation: wpOpenL {L}s step-end infinite; }}
@keyframes wpOpenL {{ 0% {{ opacity: 1 }} 61.5% {{ opacity: 0 }} 72.5% {{ opacity: 1 }} }}
.wp-openr  {{ animation: wpOpenR {L}s step-end infinite; }}
@keyframes wpOpenR {{ 0% {{ opacity: 1 }} 61.5% {{ opacity: 0 }} 72.5% {{ opacity: 1 }} 75.5% {{ opacity: 0 }} 84.5% {{ opacity: 1 }} }}
.wp-happy  {{ opacity: 0; animation: wpHappy {L}s step-end infinite; }}
@keyframes wpHappy {{ 0% {{ opacity: 0 }} 61.5% {{ opacity: 1 }} 72.5% {{ opacity: 0 }} }}
.wp-wink   {{ opacity: 0; animation: wpWink {L}s step-end infinite; }}
@keyframes wpWink {{ 0% {{ opacity: 0 }} 75.5% {{ opacity: 1 }} 84.5% {{ opacity: 0 }} }}
.wp-blush  {{ animation: wpBlush {L}s {SINE} infinite; }}
@keyframes wpBlush {{ 0%, 59% {{ opacity: .7 }} 64%, 71% {{ opacity: 1 }} 76%, 100% {{ opacity: .7 }} }}
.wp-gloss  {{ animation: wpGloss 9s {SINE} infinite alternate; }}
@keyframes wpGloss {{ from {{ opacity: .55 }} to {{ opacity: .85 }} }}
/* ---------- expression effects ---------- */
.wp-q      {{ transform-box: fill-box; transform-origin: 50% 100%; animation: wpQ {L}s linear infinite; }}
@keyframes wpQ {{
  0%, 31%   {{ opacity: 0; transform: translateY(16px) scale(.4) rotate(-18deg); animation-timing-function: cubic-bezier(.2,.8,.3,1) }}
  33.2%     {{ opacity: 1; transform: translateY(-5px) scale(1.1) rotate(7deg); animation-timing-function: {SINE} }}
  35%       {{ transform: translateY(1px) scale(.97) rotate(-3deg); animation-timing-function: {SINE} }}
  36.6%     {{ transform: none; animation-timing-function: {SINE} }}
  39%       {{ transform: translateY(-3px) rotate(2deg); animation-timing-function: {SINE} }}
  41.5%     {{ opacity: 1; transform: none; animation-timing-function: cubic-bezier(.4,0,.8,.6) }}
  44.5%, 100% {{ opacity: 0; transform: translateY(-18px) scale(.9) }} }}
.wp-dot    {{ transform-box: fill-box; transform-origin: center; animation: wpDot {L}s ease-out infinite; opacity: 0; }}
@keyframes wpDot {{ 0%, 47.5% {{ opacity: 0; transform: scale(.2) }} 48.8% {{ opacity: 1; transform: scale(1.25) }}
  49.8% {{ opacity: 1; transform: none }} 53% {{ transform: translateY(-3px) }} 56.5% {{ opacity: 1; transform: none }}
  58.5%, 100% {{ opacity: 0; transform: translateY(-6px) scale(.6) }} }}
.wp-burst  {{ transform-box: fill-box; transform-origin: center; animation: wpBurst {L}s ease-out infinite; opacity: 0; }}
@keyframes wpBurst {{ 0%, 62.6% {{ opacity: 0; transform: scale(.2) rotate(0) }} 64.8% {{ opacity: 1; transform: scale(1.15) rotate(30deg) }}
  69% {{ opacity: 1; transform: scale(1) rotate(45deg) }} 73%, 100% {{ opacity: 0; transform: scale(.4) rotate(70deg) }} }}
.wp-glint  {{ transform-box: fill-box; transform-origin: center; animation: wpGlint {L}s ease-out infinite; opacity: 0; }}
@keyframes wpGlint {{ 0%, 76% {{ opacity: 0; transform: scale(.2) }} 78% {{ opacity: 1; transform: scale(1.1) rotate(20deg) }}
  82% {{ opacity: 1; transform: scale(1) rotate(45deg) }} 85%, 100% {{ opacity: 0; transform: scale(.3) }} }}
@media (prefers-reduced-motion: reduce) {{ .wp-happy, .wp-wink, .wp-q {{ display: none }} }}
/* ---------- level-up: personality and secondary motion ---------- */
/* blinks that happen with a turn of the head, the way people blink when they look away */
.wp-tblink {{ transform-box: fill-box; transform-origin: center; animation: wpTBlink {L}s linear infinite; }}
@keyframes wpTBlink {{
  0%, 7.9%, 9.1%, 18.9%, 20.1%, 45.9%, 47.1%, 100% {{ transform: none }}
  8.5%, 19.5%, 46.5% {{ transform: scaleY(.06) }} }}
/* a small foot tap while glancing right */
.wp-footr  {{ transform-box: fill-box; transform-origin: 15% 100%; animation: wpTap {L}s ease-in-out infinite; }}
@keyframes wpTap {{ 0%, 21.5%, 23%, 24%, 25.5%, 100% {{ transform: none }} 22.25%, 24.75% {{ transform: translateY(-6px) rotate(-7deg) }} }}
/* catchlights shimmer softly */
.wp-catch  {{ transform-box: fill-box; transform-origin: center; animation: wpCatch 4.2s {SINE} infinite alternate; }}
@keyframes wpCatch {{ from {{ opacity: .82; transform: scale(.94) }} to {{ opacity: 1; transform: scale(1.06) }} }}
/* the scarf wrap swells a touch with each breath */
.wp-wrap   {{ transform-box: fill-box; transform-origin: 50% 60%; animation: wpWrap 3.2s {SINE} infinite alternate; }}
@keyframes wpWrap {{ from {{ transform: scale(1, 1) }} to {{ transform: scale(1.01, 1.03) }} }}
/* the hem follows the cloak a beat late */
.wp-hem    {{ transform-box: fill-box; transform-origin: 50% 0; animation: wpHem 3.6s {SINE} -.6s infinite alternate; }}
@keyframes wpHem {{ from {{ transform: skewX(1.6deg) }} to {{ transform: skewX(-1.6deg) }} }}
/* once per loop, a shooting star crosses the upper sky */
.wp-shoot  {{ animation: wpShoot {L}s linear infinite; opacity: 0; }}
@keyframes wpShoot {{ 0%, 86% {{ opacity: 0; transform: translate(0, 0) }} 86.6% {{ opacity: 1 }}
  89% {{ opacity: 0; transform: translate(-230px, 64px) }} 100% {{ opacity: 0; transform: translate(-230px, 64px) }} }}
@media (prefers-reduced-motion: reduce) {{ .wp-shoot {{ display: none }} }}
/* ---------- world ---------- */
.wp-shadow {{ transform-box: fill-box; transform-origin: center; animation: wpShadow 3.2s {SINE} infinite alternate; }}
@keyframes wpShadow {{ from {{ transform: scaleX(1); opacity: 1 }} to {{ transform: scaleX(.9); opacity: .72 }} }}
.wp-halo   {{ transform-box: fill-box; transform-origin: center; animation: wpHalo 8s {SINE} infinite alternate; }}
@keyframes wpHalo {{ from {{ opacity: .78; transform: scale(1) }} to {{ opacity: 1; transform: scale(1.035) }} }}
.wp-moon   {{ animation: wpMoon 8.5s {SINE} infinite alternate; }}
@keyframes wpMoon {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-7px) }} }}
.wp-moonglow {{ transform-box: fill-box; transform-origin: center; animation: wpMoonGlow 6s {SINE} infinite alternate; }}
@keyframes wpMoonGlow {{ from {{ opacity: .6; transform: scale(.94) }} to {{ opacity: 1; transform: scale(1.04) }} }}
.wp-sky    {{ animation: wpSky 22s {SINE} infinite alternate; }}
@keyframes wpSky {{ from {{ transform: translate(0, 0) }} to {{ transform: translate(5px, -4px) }} }}
.wp-tw     {{ transform-box: fill-box; transform-origin: center; animation: wpTw {SINE} infinite; }}
@keyframes wpTw {{ 0%, 100% {{ opacity: .35; transform: scale(.8) rotate(0) }} 50% {{ opacity: 1; transform: scale(1) rotate(12deg) }} }}
.wp-speck  {{ animation: wpSpeck linear infinite; }}
@keyframes wpSpeck {{ 0% {{ transform: translate(0, 0); opacity: 0 }} 18% {{ opacity: .85 }}
  60% {{ transform: translate(6px, -100px) }} 100% {{ transform: translate(-4px, -165px); opacity: 0 }} }}
"""


def _ring_d(half: str) -> str:
    """Front (lower) or back (upper) half of the orbit ellipse, before tilting."""
    cx, cy, rx, ry = RING["cx"], RING["cy"], RING["rx"], RING["ry"]
    sweep = 0 if half == "front" else 1
    return f"M{cx - rx} {cy} A{rx} {ry} 0 0 {sweep} {cx + rx} {cy}"


def wisp_background(d, t: dict, dark: bool) -> str:
    acc, hi, butter, blush, mint = t["accent"], t["accent_hi"], t["butter"], t["blush"], t["mint"]
    d.defs.append(
        f'<radialGradient id="wp-halo"><stop offset="0" stop-color="{acc}" stop-opacity="{.3 if dark else .16}"/>'
        f'<stop offset=".55" stop-color="{acc}" stop-opacity="{.09 if dark else .045}"/>'
        f'<stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="wp-ground"><stop offset="0" stop-color="{acc}" stop-opacity="{.36 if dark else .26}"/>'
        f'<stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="wp-moonglow"><stop offset="0" stop-color="{butter}" stop-opacity="{.42 if dark else .28}"/>'
        f'<stop offset="1" stop-color="{butter}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="wp-moonfill" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#FFF6DA"/>'
        f'<stop offset="1" stop-color="{butter}"/></radialGradient>'
        f'<linearGradient id="wp-streak" x1="880" y1="92" x2="838" y2="104" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{hi}" stop-opacity="0"/><stop offset="1" stop-color="{hi}" stop-opacity=".95"/>'
        f'</linearGradient>'
        f'<mask id="wp-crescent"><rect x="150" y="80" width="200" height="200" fill="#fff"/>'
        f'<circle cx="266" cy="160" r="30" fill="#000"/></mask>'
    )
    tilt = f'rotate({RING["tilt"]} {RING["cx"]} {RING["cy"]})'
    out = [
        f'<ellipse class="wp-halo" cx="{CX}" cy="470" rx="330" ry="330" fill="url(#wp-halo)"/>',
        # ground: one even, symmetric glow and a soft contact shadow, both on Wisp's centre line
        f'<ellipse cx="{CX}" cy="902" rx="290" ry="32" fill="url(#wp-ground)"/>',
        f'<ellipse class="wp-shadow" cx="{CX}" cy="899" rx="140" ry="12" fill="{"#05030C" if dark else "#3B2F6E"}" '
        f'opacity="{.55 if dark else .16}"/>',
        # back half of the orbit ring (behind the body)
        f'<path d="{_ring_d("back")}" transform="{tilt}" fill="none" stroke="{acc}" stroke-width="4" '
        f'stroke-opacity="{.34 if dark else .3}" stroke-linecap="round"/>',
        # crescent moon, floating gently, with a breathing glow
        '<g class="wp-moon">',
        f'<circle class="wp-moonglow" cx="248" cy="172" r="64" fill="url(#wp-moonglow)"/>',
        f'<circle cx="248" cy="172" r="30" fill="url(#wp-moonfill)" mask="url(#wp-crescent)"/>',
        '</g>',
        # a shooting star, once per loop
        f'<g class="wp-shoot"><path d="M880 92 L838 104" stroke="url(#wp-streak)" stroke-width="3.2" stroke-linecap="round"/>'
        f'<circle cx="838" cy="104" r="3.2" fill="{hi}"/></g>',
        '<g class="wp-sky">',
    ]
    for (x, y, r, dur, delay, col) in [(214, 318, 22, 4.6, 0, butter), (842, 270, 18, 5.4, 1.3, butter),
                                       (206, 700, 13, 5.0, 2.2, butter), (852, 772, 19, 5.8, .7, butter),
                                       (735, 116, 11, 5.2, 3.1, hi), (382, 96, 9, 5.6, 1.9, hi),
                                       (905, 420, 7, 6.2, 4.0, hi), (312, 860, 7, 6.6, 2.7, hi)]:
        out.append(f'<path class="wp-tw" d="{_star(x, y, r)}" fill="{col}" '
                   f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>')
    out.append('</g>')
    for (x, y, r, dur, delay, col) in [(262, 820, 4, 9.5, 0, acc), (770, 840, 3.5, 11, 3.5, blush),
                                       (338, 724, 3, 10.5, 6, mint), (700, 760, 3, 12, 1.8, acc),
                                       (610, 870, 2.5, 13, 8.2, hi)]:
        out.append(f'<circle class="wp-speck" cx="{x}" cy="{y}" r="{r}" fill="{col}" '
                   f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>')
    return "".join(out)


def wisp_character(d, dark: bool) -> str:
    d.defs.append(
        # head: warm porcelain in the light (upper left), cool lavender in the shade (lower right)
        '<linearGradient id="wp-head" x1="330" y1="170" x2="660" y2="570" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#FFFDFC"/><stop offset=".5" stop-color="#FAF3F8"/>'
        '<stop offset="1" stop-color="#EFE4F3"/></linearGradient>'
        '<radialGradient id="wp-headform" cx="400" cy="300" r="380" gradientUnits="userSpaceOnUse">'
        '<stop offset=".55" stop-color="#C9B6EC" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#B9A2E6" stop-opacity=".55"/></radialGradient>'
        '<radialGradient id="wp-gloss"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        # cloak: deep indigo, lifting slightly toward the hem
        '<linearGradient id="wp-cloak" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#21184A"/><stop offset=".6" stop-color="#2C2268"/>'
        '<stop offset="1" stop-color="#372B7C"/></linearGradient>'
        '<linearGradient id="wp-cloaksheen" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#D9CCFA" stop-opacity=".5"/><stop offset="1" stop-color="#D9CCFA" stop-opacity="0"/>'
        '</linearGradient>'
        '<linearGradient id="wp-hem" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#6650BF"/><stop offset="1" stop-color="#4A3A9A"/></linearGradient>'
        # scarf: one lavender ramp shared by wrap and tail
        '<linearGradient id="wp-scarf" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#C3B4FA"/><stop offset=".5" stop-color="#9A85E8"/>'
        '<stop offset="1" stop-color="#7158CB"/></linearGradient>'
        '<linearGradient id="wp-tailsheen" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#F1E9FF" stop-opacity=".85"/><stop offset="1" stop-color="#F1E9FF" stop-opacity="0"/>'
        '</linearGradient>'
        '<linearGradient id="wp-fold" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#DCD1FC" stop-opacity=".9"/><stop offset="1" stop-color="#DCD1FC" stop-opacity=".25"/>'
        '</linearGradient>'
        '<linearGradient id="wp-feet" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#2E2356"/><stop offset="1" stop-color="#170F2E"/></linearGradient>'
        # eyes: deep ink with a faint violet depth
        '<radialGradient id="wp-eye" cx=".42" cy=".32" r=".82">'
        '<stop offset="0" stop-color="#271A4E"/><stop offset=".62" stop-color="#110A26"/>'
        '<stop offset="1" stop-color="#2B1D52"/></radialGradient>'
        '<radialGradient id="wp-iris" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#8B74E0" stop-opacity=".55"/><stop offset="1" stop-color="#8B74E0" stop-opacity="0"/>'
        '</radialGradient>'
        '<radialGradient id="wp-cheek"><stop offset="0" stop-color="#F7B4D1" stop-opacity=".8"/>'
        '<stop offset="1" stop-color="#F7B4D1" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="wp-headclip"><path d="{HEAD}"/></clipPath>'
        f'<clipPath id="wp-cloakclip"><path d="{CLOAK}"/></clipPath>'
        f'<clipPath id="wp-wrapclip"><path d="{WRAP}"/></clipPath>'
        # warm moonlight rim on the head's upper-left edge (dark pages)
        '<linearGradient id="wp-moonrim" x1="300" y1="160" x2="520" y2="420" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#FFE7B8" stop-opacity=".75"/><stop offset="1" stop-color="#FFE7B8" stop-opacity="0"/>'
        '</linearGradient>'
        # lavender light bounced up from the scarf onto the underside of the head
        '<radialGradient id="wp-bounce" cx="490" cy="600" r="190" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#A994F0" stop-opacity=".34"/><stop offset=".6" stop-color="#A994F0" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#A994F0" stop-opacity="0"/>'
        '</radialGradient>'
        # contact shadows: under the scarf on the cloak, under the head on the scarf
        '<linearGradient id="wp-undercast" x1="0" y1="630" x2="0" y2="700" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#0B0620" stop-opacity=".55"/><stop offset="1" stop-color="#0B0620" stop-opacity="0"/>'
        '</linearGradient>'
        '<linearGradient id="wp-headcast" x1="0" y1="540" x2="0" y2="600" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#3A2A7C" stop-opacity=".45"/><stop offset="1" stop-color="#3A2A7C" stop-opacity="0"/>'
        '</linearGradient>'
        f'<clipPath id="wp-tailclip"><path d="{TAIL}"/></clipPath>'
    )
    rim = (f'<path d="{HEAD}" fill="none" stroke="#B7AAFF" stroke-opacity=".24" stroke-width="22" '
           f'stroke-linejoin="round"/>') if dark else ""

    def eye(i: int, side: str):
        cx, cy = EYES[i]
        rot = f'rotate(-7.5 {cx} {cy})'
        opened = (f'<g class="wp-open{side}"><g class="wp-blink"><g class="wp-tblink"><g transform="{rot}">'
                  f'<ellipse cx="{cx}" cy="{cy}" rx="46" ry="63.5" fill="url(#wp-eye)"/>'
                  f'<ellipse cx="{cx + 2}" cy="{cy + 30}" rx="32" ry="20" fill="url(#wp-iris)"/>'
                  f'<g class="wp-catch"><ellipse cx="{cx - 20}" cy="{cy - 24}" rx="9.5" ry="14" fill="#FFFFFF" '
                  f'transform="rotate(-10 {cx - 20} {cy - 24})"/></g>'
                  f'<circle cx="{cx + 16}" cy="{cy + 24}" r="4.6" fill="#FFFFFF" opacity=".72"/>'
                  f'</g></g></g></g>')
        happy = (f'<path d="M{cx - 38} {cy + 14} Q{cx} {cy - 38} {cx + 38} {cy + 14}" transform="{rot}" '
                 f'fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round"/>')
        return opened, happy

    lo, lh = eye(0, "l")
    ro, rh = eye(1, "r")
    rx_, ry_ = EYES[1]
    wink = (f'<path d="M{rx_ - 38} {ry_ - 4} Q{rx_} {ry_ + 28} {rx_ + 38} {ry_ - 4}" '
            f'transform="rotate(-7.5 {rx_} {ry_})" fill="none" stroke="{INK}" stroke-width="12.5" stroke-linecap="round"/>')
    line = f'stroke="{OUTLINE}" stroke-width="{OUTLINE_W}" stroke-linejoin="round"'

    return "".join([
        '<g class="wp-bob"><g class="wp-hop"><g class="wp-squash">',
        # feet: same outline as everything else, a faint top light so they read on dark pages
        f'<rect x="428" y="852" width="66" height="42" rx="20" fill="url(#wp-feet)" {line}/>',
        '<path d="M442 862 H478" stroke="#5A4A96" stroke-width="4" stroke-linecap="round" opacity=".7"/>',
        '<g class="wp-footr">',
        f'<rect x="530" y="852" width="66" height="42" rx="20" fill="url(#wp-feet)" {line}/>',
        '<path d="M544 862 H580" stroke="#5A4A96" stroke-width="4" stroke-linecap="round" opacity=".7"/>',
        '</g>',
        # cloak: breathes from the feet, sways from the shoulders
        '<g class="wp-breath"><g class="wp-cloak">',
        (f'<path d="{CLOAK}" fill="none" stroke="#B7AAFF" stroke-opacity=".2" stroke-width="18" '
         f'stroke-linejoin="round"/>') if dark else "",
        f'<path d="{CLOAK}" fill="url(#wp-cloak)" {line}/>',
        f'<path d="{CLOAK_SHEEN}" fill="url(#wp-cloaksheen)"/>',
        # cloth folds: a soft shadow crease with a faint lit edge beside it
        '<g clip-path="url(#wp-cloakclip)" fill="none" stroke-linecap="round">',
        '<path d="M470 668 C463 728 455 786 447 846" stroke="#120B30" stroke-opacity=".42" stroke-width="7"/>',
        '<path d="M480 672 C474 730 467 788 460 846" stroke="#5E4CB0" stroke-opacity=".2" stroke-width="3"/>',
        '<path d="M560 664 C571 724 585 782 598 842" stroke="#120B30" stroke-opacity=".38" stroke-width="6"/>',
        '<path d="M550 668 C560 726 572 784 584 842" stroke="#5E4CB0" stroke-opacity=".18" stroke-width="2.6"/>',
        '<rect x="330" y="625" width="380" height="80" fill="url(#wp-undercast)" stroke="none"/>',
        '</g>',
        '<g class="wp-hem">',
        f'<path d="{HEM}" fill="url(#wp-hem)" stroke="{OUTLINE}" stroke-width="3" stroke-linejoin="round"/>',
        '<path d="M352 829 C410 846 470 850 512 850 C570 850 630 842 680 826" fill="none" stroke="#9C88EC" '
        'stroke-opacity=".45" stroke-width="2.4" stroke-linecap="round"/>',
        '</g>',
        '</g></g>',
        # scarf tail: flutters from the knot; a second, faster layer makes the end lag
        '<g class="wp-tail"><g class="wp-tail2">',
        f'<path d="{TAIL}" fill="url(#wp-scarf)" {line}/>',
        '<path d="M650 600 C700 606 742 592 778 568 C820 540 864 528 906 525" fill="none" '
        'stroke="url(#wp-tailsheen)" stroke-width="16" stroke-linecap="round" clip-path="url(#wp-tailclip)"/>',
        '<g clip-path="url(#wp-tailclip)" fill="none" stroke="#4E37A0" stroke-linecap="round">',
        '<path d="M700 640 C742 634 776 612 806 592 C836 574 866 566 900 566" stroke-opacity=".32" stroke-width="5"/>',
        '<path d="M760 655 C790 646 820 628 852 616 C870 610 886 608 898 608" stroke-opacity=".22" stroke-width="4"/>',
        '</g>',
        '</g></g>',
        # head: idle drift wraps the expression turns
        '<g class="wp-idle"><g class="wp-head">',
        rim,
        f'<path d="{HEAD}" fill="url(#wp-head)" {line}/>',
        f'<path d="{HEAD}" fill="url(#wp-headform)"/>',
        '<g clip-path="url(#wp-headclip)">',
        '<circle cx="490" cy="600" r="190" fill="url(#wp-bounce)"/>',  # shape = full gradient: fades to nothing
        (f'<path d="{HEAD}" fill="none" stroke="url(#wp-moonrim)" stroke-width="16"/>' if dark else ""),
        '<ellipse class="wp-gloss" cx="395" cy="255" rx="95" ry="52" fill="url(#wp-gloss)" transform="rotate(-32 395 255)"/>',
        '<g class="wp-blush">',
        # cheeks sit just below and outside each eye, well inside the outline
        '<ellipse cx="338" cy="548" rx="42" ry="22" fill="url(#wp-cheek)" transform="rotate(-7.5 338 548)"/>',
        '<ellipse cx="618" cy="502" rx="40" ry="21" fill="url(#wp-cheek)" transform="rotate(-7.5 618 502)"/>',
        '</g></g>',
        f'<g class="wp-eyes">{lo}{ro}</g>',
        f'<g class="wp-happy">{lh}{rh}</g>',
        f'<g class="wp-wink">{wink}</g>',
        '</g></g>',
        # scarf wrap (over the neck)
        '<g class="wp-wrap">',
        f'<path d="{WRAP}" fill="url(#wp-scarf)" {line}/>',
        f'<rect x="395" y="530" width="255" height="80" fill="url(#wp-headcast)" clip-path="url(#wp-wrapclip)"/>',
        f'<path d="{WRAP_FOLD}" fill="url(#wp-fold)"/>',
        '<path d="M466 590 C522 582 580 568 628 555" fill="none" stroke="#EEE7FF" stroke-opacity=".45" '
        'stroke-width="6" stroke-linecap="round"/>',
        '<path d="M470 628 C530 620 590 602 632 586" fill="none" stroke="#4E37A0" stroke-opacity=".3" '
        'stroke-width="4" stroke-linecap="round"/>',
        '</g>',
        '</g></g></g>',
    ])


def wisp_foreground(d, t: dict, dark: bool) -> str:
    """Front half of the orbit ring with its gliding light, and the expression effects."""
    acc, blush, mint, butter = t["accent"], t["blush"], t["mint"], t["butter"]
    tilt = f'rotate({RING["tilt"]} {RING["cx"]} {RING["cy"]})'
    front = _ring_d("front")
    return "".join([
        f'<g transform="{tilt}">',
        f'<path d="{front}" fill="none" stroke="{acc}" stroke-width="4.5" stroke-opacity="{.58 if dark else .48}" '
        f'stroke-linecap="round"/>',
        f'<radialGradient id="wp-comet" cx=".8" cy=".5" r=".8"><stop offset="0" stop-color="{t["accent_hi"]}"/>'
        f'<stop offset="1" stop-color="{t["accent_hi"]}" stop-opacity="0"/></radialGradient>'
        f'<ellipse rx="20" ry="5" fill="url(#wp-comet)" opacity="0">'
        f'<animateMotion path="{front}" dur="9s" rotate="auto" keyPoints="0;1;1" keyTimes="0;.6;1" calcMode="spline" '
        f'keySplines=".37 0 .63 1;0 0 1 1" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.1;.5;.6;1" dur="9s" repeatCount="indefinite"/>'
        f'</ellipse>',
        '</g>',
        '<g class="wp-q">', d.text(722, 252, "?", "serif-bi", 170, blush), '</g>',
        f'<circle class="wp-dot" cx="712" cy="268" r="11" fill="{acc}"/>',
        f'<circle class="wp-dot" cx="752" cy="236" r="13" fill="{acc}" style="animation-delay:.27s"/>',
        f'<circle class="wp-dot" cx="798" cy="198" r="15" fill="{acc}" style="animation-delay:.54s"/>',
        f'<path class="wp-burst" d="{_star(745, 230, 30)}" fill="{mint}"/>',
        f'<path class="wp-burst" d="{_star(300, 190, 20)}" fill="{blush}" style="animation-delay:.15s"/>',
        f'<path class="wp-glint" d="{_star(690, 330, 18)}" fill="{butter}"/>',
    ])


def wisp_parts(d, t: dict, dark: bool) -> str:
    """World, Wisp and foreground, in a 1000x1000 space."""
    d.css.append(_css())
    return wisp_background(d, t, dark) + wisp_character(d, dark) + wisp_foreground(d, t, dark)
