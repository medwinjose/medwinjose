"""Small toolkit for hand-built, self-contained SVGs.

Every SVG embeds only the glyphs it uses (subsetted WOFF2, base64), so the
typography renders identically for every visitor without any web requests.
"""

from __future__ import annotations

import base64
import functools
import io
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
OUT_DIR = ROOT / "assets"

# --------------------------------------------------------------------------
# Palette: soft but bright pastels (lavender, mint, blush, butter) on
# GitHub dark; deeper versions of the same hues on GitHub light. Backgrounds
# stay transparent so every piece sits directly on the page.
# --------------------------------------------------------------------------
THEMES = {
    "dark": {
        "ink": "#F4F1FB",
        "soft": "#CBC6DC",
        "muted": "#9893AD",
        "faint": "#615C74",
        "rule": "#2F2C3D",
        "accent": "#B7AAFF",     # lavender
        "accent_hi": "#E6E0FF",
        "mint": "#93E6CC",
        "blush": "#FFB4C8",
        "butter": "#FFE29A",
        "surface": "#15141D",
        "border": "#2B2938",
        "window": "#FFE8AE",
    },
    "light": {
        "ink": "#1E1A2D",
        "soft": "#4A4561",
        "muted": "#7D7795",
        "faint": "#B7B1C9",
        "rule": "#E7E3F1",
        "accent": "#6D5BDB",
        "accent_hi": "#D9D1FF",
        "mint": "#2E9C7E",
        "blush": "#D8698C",
        "butter": "#D9A23A",
        "surface": "#FBFAFF",
        "border": "#EAE6F5",
        "window": "#FFFDF4",
    },
}

FACES = {
    "serif": ("Cormorant Garamond", 500, "normal", "cormorant-garamond-latin-500-normal.woff2"),
    "serif-i": ("Cormorant Garamond", 500, "italic", "cormorant-garamond-latin-500-italic.woff2"),
    "serif-b": ("Cormorant Garamond", 600, "normal", "cormorant-garamond-latin-600-normal.woff2"),
    "serif-bi": ("Cormorant Garamond", 600, "italic", "cormorant-garamond-latin-600-italic.woff2"),
    "sans": ("Inter", 400, "normal", "inter-latin-400-normal.woff2"),
    "sans-m": ("Inter", 500, "normal", "inter-latin-500-normal.woff2"),
    "sans-sb": ("Inter", 600, "normal", "inter-latin-600-normal.woff2"),
}

FALLBACK = {"serif": "Georgia, 'Times New Roman', serif", "sans": "system-ui, -apple-system, 'Segoe UI', sans-serif"}

EASE_OUT = "cubic-bezier(.16,1,.3,1)"


@functools.lru_cache(maxsize=None)
def _font(face: str) -> TTFont:
    return TTFont(FONT_DIR / FACES[face][3])


def measure(face: str, text: str, size: float, tracking: float = 0.0) -> float:
    """Visible advance width of ``text`` in px (kerning ignored, trailing tracking excluded)."""
    font = _font(face)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    width = 0
    for ch in text:
        glyph = cmap.get(ord(ch))
        if glyph is None:
            raise ValueError(f"glyph {ch!r} missing from {face}")
        width += hmtx[glyph][0]
    return width * size / upm + tracking * max(len(text) - 1, 0)


@functools.lru_cache(maxsize=None)
def _subset_b64(face: str, chars: str) -> str:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "lnum", "pnum"]
    opts.name_IDs = []
    opts.notdef_outline = True
    font = TTFont(FONT_DIR / FACES[face][3])
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Doc:
    """Collects markup, CSS and glyph usage for a single SVG file."""

    BASE_CSS = """
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }
@keyframes fade { from { opacity: 0 } to { opacity: 1 } }
@keyframes rise { from { opacity: 0; transform: translateY(10px) } to { opacity: 1; transform: none } }
@keyframes drawx { from { transform: scaleX(0) } to { transform: scaleX(1) } }
@keyframes drawy { from { transform: scaleY(0) } to { transform: scaleY(1) } }
@keyframes breathe { 0%, 100% { opacity: .55 } 50% { opacity: 1 } }
.fb { transform-box: fill-box; }
"""

    def __init__(self, width: int, height: int, title: str):
        self.width, self.height, self.title = width, height, title
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.css: list[str] = []
        self.used: dict[str, set[str]] = defaultdict(set)

    def add(self, *markup: str) -> None:
        self.parts.extend(markup)

    def text(self, x, y, s, face, size, fill, *, anchor="start", tracking=0.0, cls="", style="", attrs="") -> str:
        self.used[face].update(s)
        if anchor == "middle" and tracking:
            x += tracking / 2  # SVG adds trailing letter-spacing; keep optical centre.
        klass = f"f-{face} {cls}".strip()
        a = [f'x="{fmt(x)}"', f'y="{fmt(y)}"', f'class="{klass}"', f'font-size="{fmt(size)}"', f'fill="{fill}"']
        if anchor != "start":
            a.append(f'text-anchor="{anchor}"')
        if tracking:
            a.append(f'letter-spacing="{fmt(tracking)}"')
        if style:
            a.append(f'style="{style}"')
        if attrs:
            a.append(attrs)
        return f"<text {' '.join(a)}>{escape(s)}</text>"

    def use_glyphs(self, face: str, s: str) -> None:
        self.used[face].update(s)

    def render(self) -> str:
        fonts, classes = [], []
        for face, chars in sorted(self.used.items()):
            family, weight, style, _ = FACES[face]
            fid = f"MJ-{face}"
            data = _subset_b64(face, "".join(sorted(chars | {" "})))
            fonts.append(
                f"@font-face {{ font-family: '{fid}'; src: url(data:font/woff2;base64,{data}) format('woff2'); "
                f"font-weight: {weight}; font-style: {style}; }}"
            )
            fallback = FALLBACK["serif" if face.startswith("serif") else "sans"]
            feats = " font-feature-settings: 'lnum' 1, 'kern' 1;" if face.startswith("serif") else ""
            classes.append(f".f-{face} {{ font-family: '{fid}', {fallback}; font-weight: {weight}; font-style: {style};{feats} }}")
        css = "\n".join(fonts + classes) + self.BASE_CSS + "\n".join(self.css)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-label="{escape(self.title)}">'
            f"<title>{escape(self.title)}</title><style>{css}</style>{defs}{''.join(self.parts)}</svg>\n"
        )

    def save(self, name: str) -> Path:
        path = OUT_DIR / name
        path.write_text(self.render(), encoding="utf-8")
        return path


def diamond(cx: float, cy: float, r: float, fill: str = "none", stroke: str = "none", sw: float = 1, attrs: str = "") -> str:
    pts = f"{fmt(cx)},{fmt(cy - r)} {fmt(cx + r)},{fmt(cy)} {fmt(cx)},{fmt(cy + r)} {fmt(cx - r)},{fmt(cy)}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{fmt(sw)}" {attrs}/>'


def arrow_ne(x: float, y: float, size: float, stroke: str, sw: float = 1.2, attrs: str = "") -> str:
    """A thin north-east arrow whose bounding box starts at (x, y) top-left."""
    s = size
    return (
        f'<path d="M{fmt(x)} {fmt(y + s)} L{fmt(x + s)} {fmt(y)} M{fmt(x + s * .3)} {fmt(y)} H{fmt(x + s)} V{fmt(y + s * .7)}" '
        f'fill="none" stroke="{stroke}" stroke-width="{fmt(sw)}" stroke-linecap="round" stroke-linejoin="round" {attrs}/>'
    )


def wrap(face: str, text: str, size: float, max_width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and measure(face, trial, size) > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def arrow(x: float, y: float, size: float, stroke: str, sw: float = 1.2, attrs: str = "") -> str:
    """A thin north-east or east arrow drawn as a path (glyph-free)."""
    s = size
    return (
        f'<path d="M{fmt(x)} {fmt(y)} H{fmt(x + s)} M{fmt(x + s - s * .38)} {fmt(y - s * .38)} L{fmt(x + s)} {fmt(y)} '
        f'L{fmt(x + s - s * .38)} {fmt(y + s * .38)}" fill="none" stroke="{stroke}" stroke-width="{fmt(sw)}" '
        f'stroke-linecap="round" stroke-linejoin="round" {attrs}/>'
    )
