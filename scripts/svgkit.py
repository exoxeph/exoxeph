# A small SVG kit for the profile cards, drawn in the design system of exoxeph.github.io:
# its colour roles, its three type families (Newsreader, IBM Plex Sans, IBM Plex Mono) and its hand-note font
# (Comic Neue). Fonts are subset to the characters each card uses and embedded as WOFF2, because GitHub shows
# README images through <img>, which cannot load outside files.
import base64, io, os
from collections import defaultdict
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))

# The colour roles of exoxeph.github.io (src/styles/tokens.css). The site is dark only, so the cards are too.
C = {
    "bg": "#131416",
    "surface": "#1b1d20",
    "text": "#ece9e1",
    "muted": "#a5a49e",
    "rule": "#2e3033",
    "accent": "#9ca9ff",
    "verified": "#7acf9f",
    "partial": "#e2b35c",
    "invalid": "#f28d7b",
    "note": "#f4d58d",  # the hand notes (src/styles/notes.css)
    "well": "#0f1012",  # the inset that holds a diagram
    # the chapter tints of the home page, one per system
    "pool": "#222838",
    "email": "#1f3030",
    "rag": "#302530",
    "speech": "#273027",
    # the warm materials of the isometric dev room (src/lib/resume/room.ts)
    "warm-top": "#ffc867",
    "warm-front": "#d9793a",
    "warm-end": "#9c4f27",
}

# Every board keeps this much clear space inside its own image, so blocks in the README never touch.
M = 6
RADIUS = 16

# key: (css family, weight, file, variable-font weight to pin or None)
FONTS = {
    "serif": ("Newsreader", 400, "newsreader-latin-wght-normal.woff2", 400),
    "serif5": ("Newsreader", 500, "newsreader-latin-wght-normal.woff2", 500),
    "sans": ("IBM Plex Sans", 400, "ibm-plex-sans-latin-400-normal.woff2", None),
    "sans5": ("IBM Plex Sans", 500, "ibm-plex-sans-latin-500-normal.woff2", None),
    "mono": ("IBM Plex Mono", 400, "ibm-plex-mono-latin-400-normal.woff2", None),
    "mono5": ("IBM Plex Mono", 500, "ibm-plex-mono-latin-500-normal.woff2", None),
    "note": ("Comic Neue", 700, "comic-neue-latin-700-normal.woff2", None),
}

_tt = {}


def _font(key):
    if key not in _tt:
        fam, wt, fname, pin = FONTS[key]
        f = TTFont(os.path.join(HERE, "fonts", fname), recalcTimestamp=False)
        if pin is not None:
            f = instancer.instantiateVariableFont(f, {"wght": pin})
            f.recalcTimestamp = False  # the same input must give the same bytes, or every night commits noise
        _tt[key] = f
    return _tt[key]


def text_width(s, font, size, tracking=0.0):
    tt = _font(font)
    cmap, hmtx, upm = tt.getBestCmap(), tt["hmtx"], tt["head"].unitsPerEm
    w = sum(hmtx[cmap[ord(ch)]][0] if ord(ch) in cmap else upm * 0.55 for ch in s)
    return w * size / upm + tracking * size * max(len(s) - 1, 0)


def wrap(s, font, size, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if text_width(t, font, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _subset_b64(key, chars):
    f = _font(key)
    buf = io.BytesIO()
    f.save(buf)  # a fresh copy, so subsetting never touches the cached font used for measuring
    buf.seek(0)
    g = TTFont(buf, recalcTimestamp=False)
    g.recalcTimestamp = False
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(g)
    out = io.BytesIO()
    g.flavor = "woff2"
    g.save(out)
    return base64.b64encode(out.getvalue()).decode()


def data_uri(path):
    ext = path.rsplit(".", 1)[1]
    mime = {"png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}[ext]
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


def f1(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.parts, self.defs, self.css = [], [], []
        self.used = defaultdict(set)
        self.min_size = 999
        self.overflow = []
        self._id = 0
        self.framed = False

    def uid(self, p="u"):
        self._id += 1
        return f"{p}{self._id}"

    def add(self, s):
        self.parts.append(s)

    def use_font(self, key, chars):
        """For text drawn by something else (the captured room), so its font still gets embedded."""
        self.used[key].update(chars)

    def _check(self, s, x, font, size, anchor, tracking):
        w = text_width(s, font, size, tracking)
        left = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
        if left < -0.5 or left + w > self.w + 0.5:
            self.overflow.append(s)
        self.min_size = min(self.min_size, size)
        return w

    def text(self, x, y, s, font="sans", size=15, fill="text", anchor="start", tracking=0.0, italic=False, extra=""):
        self.used[font].update(s)
        w = self._check(s, x, font, size, anchor, tracking)
        fam, wt, _, _ = FONTS[font]
        ls = f' letter-spacing="{f1(tracking * size)}"' if tracking else ""
        it = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{f1(x)}" y="{f1(y)}" font-family="{fam}" font-weight="{wt}" font-size="{size}" '
                 f'fill="{C.get(fill, fill)}" text-anchor="{anchor}"{ls}{it} {extra}>{escape(s)}</text>')
        return w

    def label_text(self, x, y, s, fill="accent", size=11.5, anchor="start", font="mono5"):
        """The site's technical labels: mono, upper case, tracked out."""
        return self.text(x, y, s.upper(), font, size, fill, anchor, tracking=0.12)

    def lines(self, x, y, lines, font="sans", size=15, lh=1.5, fill="muted", **kw):
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * lh, ln, font, size, fill, **kw)
        return y + len(lines) * size * lh

    def rect(self, x, y, w, h, fill="surface", stroke=None, sw=1, r=0, extra=""):
        s = f' stroke="{C.get(stroke, stroke)}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" rx="{r}" fill="{C.get(fill, fill)}"{s} {extra}/>')

    def line(self, x1, y1, x2, y2, stroke="rule", sw=1, extra=""):
        self.add(f'<line x1="{f1(x1)}" y1="{f1(y1)}" x2="{f1(x2)}" y2="{f1(y2)}" stroke="{C.get(stroke, stroke)}" stroke-width="{sw}" {extra}/>')

    def frame(self):
        """The card itself: the page colour with a hairline rule, square corners as on the site. Drawn at render
        time, under everything, so a card may still change its height after calling this."""
        self.framed = True

    def render(self):
        faces = []
        for key, chars in sorted(self.used.items()):
            if not chars:
                continue
            fam, wt, _, _ = FONTS[key]
            faces.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};"
                         f"src:url(data:font/woff2;base64,{_subset_b64(key, chars)}) format('woff2')}}")
        style = "".join(faces) + "".join(self.css)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        self.h = round(self.h)
        bg = ""
        if self.framed:
            x, y, w, h = M, M, self.w - 2 * M, self.h - 2 * M
            box = f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{RADIUS}"'
            bg = (f'<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
                  f'<circle cx="9" cy="9" r="0.9" fill="{C["text"]}" fill-opacity="0.07"/></pattern></defs>'
                  f'<rect {box} fill="{C["bg"]}" stroke="{C["rule"]}" stroke-width="1.5"/><rect {box} fill="url(#dots)"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-label="{escape(self.label, {chr(34): "&quot;"})}">'
                f"<title>{escape(self.label)}</title><style><![CDATA[{style}]]></style>{defs}{bg}"
                f"{''.join(self.parts)}</svg>")
