# The profile cards, drawn in the design system of exoxeph.github.io. Every function returns an Svg. Full-width
# boards are 880 wide, half-width project cards and phone boards 440.
import math, os, re
from datetime import date, timedelta

from iso import Camera
from svgkit import C, HERE, M, RADIUS, Svg, data_uri, f1, text_width, wrap

ART = os.path.join(HERE, "art")
ARROW = "↗"  # the north-east arrow the site puts on outbound links


def fmt(n):
    return f"{n:,}"


# ---------------------------------------------------------------- shared pieces
def board(w, h, label):
    s = Svg(w, h, label)
    s.frame()
    return s


def panel(s, x, y, w, h, fill="well", stroke="rule", r=10):
    s.rect(x, y, w, h, fill, stroke, 1, r)


def chip(s, x, y, text, color="muted", size=11.5, h=24):
    """A small tag. Returns its width."""
    w = text_width(text, "mono", size) + 18
    ink = C.get(color, color)
    s.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{h}" rx="6" fill="{ink}" fill-opacity="0.12" '
          f'stroke="{ink}" stroke-opacity="0.45"/>')
    s.text(x + 9, y + h / 2 + size * 0.35, text, "mono", size, "text")
    return w


def chip_flow(s, x, y, items, color, maxw, gap=8, size=11.5, h=24):
    """Chips in rows. Returns the y below the last row."""
    cx = x
    for it in items:
        w = text_width(it, "mono", size) + 18
        if cx > x and cx + w > x + maxw:
            cx, y = x, y + h + gap
        chip(s, cx, y, it, color, size, h)
        cx += w + gap
    return y + h


def open_mark(s, x, y):
    """The square arrow button in a card's corner."""
    s.rect(x, y, 30, 30, "bg", "accent", 1.2, 7)
    s.text(x + 15, y + 21, ARROW, "mono", 16, "accent", "middle")


def hatch(s, color):
    pid = s.uid("hatch")
    s.defs.append(f'<pattern id="{pid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                  f'<rect width="7" height="7" fill="{C[color]}" fill-opacity="0.1"/>'
                  f'<line x1="0" y1="0" x2="0" y2="7" stroke="{C[color]}" stroke-width="2" stroke-opacity="0.5"/></pattern>')
    return f"url(#{pid})"


# ---------------------------------------------------------------- the dev room
# scripts/art/room.svg is the isometric dev room from https://exoxeph.github.io/resume/, captured from the live page
# (XMLSerializer on svg.dr-svg, with only the CSS rules it uses and its images inlined as data URIs). All of the
# lettering was removed afterwards: on the site it spells out the work history, which this profile leaves out. When
# the room changes on the site, capture it again the same way and remove every <text> element.
def place_room(s, x, y, w, h, view):
    """The room as a nested image: its CSS, ids and animations stay sealed inside it."""
    import base64
    src = open(os.path.join(ART, "room.svg"), encoding="utf8").read()
    src = re.sub(r'viewBox="[^"]*"', f'viewBox="{view}"', src, count=1)
    src = re.sub(r'<svg width="\d+" height="\d+"', f'<svg width="{w}" height="{h}"', src, count=1)
    src = src.replace('preserveAspectRatio="xMidYMid meet"', 'preserveAspectRatio="xMidYMid slice"', 1)
    uri = "data:image/svg+xml;base64," + base64.b64encode(src.encode("utf8")).decode()
    s.add(f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')


def fade(s, x, y, w, h, direction):
    """A gradient from the page colour to clear, laid over the room so it melts into the card."""
    gid = s.uid("fade")
    x1, y1, x2, y2 = {"right": (0, 0, 1, 0), "left": (1, 0, 0, 0), "down": (0, 0, 0, 1), "up": (0, 1, 0, 0)}[direction]
    s.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                  f'<stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="{C["bg"]}" stop-opacity="0"/>'
                  f'</linearGradient>')
    s.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="url(#{gid})"/>')


def portrait(s, cx, cy, r):
    cid = s.uid("clip")
    s.defs.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="none" stroke="{C["rule"]}" stroke-width="1.5"/>')
    s.add(f'<line x1="{cx}" y1="{cy - r - 10}" x2="{cx}" y2="{cy - r - 3}" stroke="{C["accent"]}" stroke-width="1.5"/>')
    s.add(f'<image href="{data_uri(os.path.join(ART, "portrait.webp"))}" x="{cx - r}" y="{cy - r}" width="{2 * r}" '
          f'height="{2 * r}" clip-path="url(#{cid})" preserveAspectRatio="xMidYMid slice" style="filter:grayscale(1)"/>')


def note(s, x, y, text, size=15, anchor="start", rotate=-3):
    """A hand note, in the site's marker ink."""
    s.text(x, y, text, "note", size, "note", anchor, extra=f'transform="rotate({rotate} {f1(x)} {f1(y)})"')


def arrow(s, d, head):
    """A hand-drawn arrow: a curved stroke and an open head, both in note ink."""
    s.add(f'<path d="{d}" fill="none" stroke="{C["note"]}" stroke-width="1.8" stroke-linecap="round"/>')
    s.add(f'<path d="{head}" fill="none" stroke="{C["note"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- hero
def hero_label(P):
    return f"{P['name']}, {P['role']}. {P['lede']} Portfolio: exoxeph.github.io."


def _clip_board(s):
    cid = s.uid("board")
    s.defs.append(f'<clipPath id="{cid}"><rect x="{M + 1}" y="{M + 1}" width="{s.w - 2 * M - 2}" '
                  f'height="{s.h - 2 * M - 2}" rx="{RADIUS - 1}"/></clipPath>')
    return cid


def _site_chip(s, x, y):
    """The tilted address sticker: the portfolio, printed on the profile."""
    text = f"exoxeph.github.io {ARROW}"
    w = text_width(text, "mono5", 15) + 28
    s.add(f'<g transform="rotate(3 {f1(x + w / 2)} {y + 19})">')
    s.rect(x + 3, y + 4, w, 38, "well", None, 1, 9)
    s.rect(x, y, w, 38, "accent", None, 1, 9)
    s.text(x + w / 2, y + 24.5, text, "mono5", 15, "bg", "middle")
    s.add("</g>")


def hero(P, phone=False):
    s = board(440 if phone else 880, 700 if phone else 440, hero_label(P))
    cid = _clip_board(s)
    s.add(f'<g clip-path="url(#{cid})">')
    if phone:
        place_room(s, M, M, 428, 340, "150 170 700 556")
        fade(s, 0, 256, 440, 92, "up")
    else:
        place_room(s, 300, M, 574, 428, "40 40 900 671")
        fade(s, 299, 0, 200, 440, "right")
        fade(s, 300, 356, 580, 80, "up")
    s.add("</g>")
    if phone:
        _site_chip(s, 214, 24)
        portrait(s, 68, 392, 36)
        s.lines(126, 386, P["meta"], "mono", 12.5, 1.7, "muted")
        s.text(28, 500, "Imtiaz", "serif", 54, "text")
        s.text(28, 554, "Mashrafee", "serif", 54, "text")
        s.text(26, 608, P["role"], "serif", 42, "accent", italic=True)
        s.lines(28, 644, wrap(P["lede"], "serif", 17, 384), "serif", 17, 1.4, "muted")
        return s
    portrait(s, 94, 96, 44)
    s.lines(164, 92, P["meta"], "mono", 12.5, 1.7, "muted")
    s.text(44, 218, "Imtiaz", "serif", 62, "text")
    s.text(44, 280, "Mashrafee", "serif", 62, "text")
    s.text(42, 338, P["role"], "serif", 48, "accent", italic=True)
    s.lines(44, 378, wrap(P["lede"], "serif", 18, 300), "serif", 18, 1.4, "muted")
    _site_chip(s, 662, 28)
    note(s, 690, 304, "that's me, in my dev room", 15, rotate=-3)
    arrow(s, "M716 314 C 712 340, 700 354, 682 363", "M686 351 L681 364 L695 362")
    return s


# ---------------------------------------------------------------- link buttons
def button(label, tint):
    w = round(text_width(label, "sans5", 15) + text_width(" " + ARROW, "mono", 14) + 44)
    s = Svg(w, 50, label)
    ink = C.get(tint, tint)
    s.rect(3, 6, w - 6, 40, "well", None, 1, 10)
    s.rect(2, 3, w - 6, 40, "bg", None, 1, 10)
    s.add(f'<rect x="2" y="3" width="{w - 6}" height="40" rx="10" fill="{ink}" fill-opacity="0.2" stroke="{ink}" stroke-width="1.4"/>')
    tw = s.text(20, 28.5, label, "sans5", 15, "text")
    s.text(20 + tw + 4, 28.5, " " + ARROW, "mono", 14, "accent")
    return s


# ---------------------------------------------------------------- the idea
def _idea_diagram(s, ox, oy):
    s.rect(ox, oy + 50, 100, 40, "well", "muted", 1, 7)
    s.text(ox + 50, oy + 75, "a request", "mono", 13, "text", "middle")
    s.line(ox + 100, oy + 70, ox + 140, oy + 70, "muted")
    cx, cy, d = ox + 168, oy + 70, 28
    s.add(f'<polygon points="{cx},{cy - d} {cx + d},{cy} {cx},{cy + d} {cx - d},{cy}" fill="{C["well"]}" stroke="{C["accent"]}" stroke-width="1.4"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{C["accent"]}"/>')
    s.text(cx, cy + d + 20, "CHECK", "mono5", 12, "accent", "middle", tracking=0.08)
    jx = cx + d + 14
    s.line(cx + d, cy, jx, cy, "muted")
    s.add(f'<path d="M{jx} {cy} V{oy + 20} H{jx + 48}" fill="none" stroke="{C["verified"]}" stroke-width="1.4"/>')
    s.add(f'<path d="M{jx} {cy} V{oy + 120} H{jx + 48}" fill="none" stroke="{C["invalid"]}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    s.rect(jx + 48, oy, 172, 40, "well", "verified", 1.2, 7)
    s.text(jx + 134, oy + 25, "the system acts", "mono", 13, "text", "middle")
    s.text(jx + 6, oy + 13, "PASS", "mono5", 11, "verified")
    s.rect(jx + 48, oy + 100, 172, 40, "well", "invalid", 1.2, 7, extra='stroke-dasharray="4 3"')
    s.text(jx + 134, oy + 125, "ask, refuse, leave out", "mono", 12, "text", "middle")
    s.text(jx + 6, oy + 136, "FAIL", "mono5", 11, "invalid")


def idea(P, phone=False):
    label = ("What I build: check before acting. A request comes in, a check sits in its path, and the system acts "
             "only if the check passes. Four systems below.")
    sub = "Four systems. Each one breaks somewhere. Here's where, and what catches it."
    if phone:
        s = board(440, 400, label)
        s.label_text(28, 46, "What I build")
        s.text(28, 90, "Check before acting.", "serif", 34, "text")
        s.lines(28, 124, wrap(sub, "serif", 17, 380), "serif", 17, 1.4, "muted")
        s.add('<g transform="translate(24 196) scale(0.89)">')
        _idea_diagram(s, 0, 0)
        s.add("</g>")
        note(s, 70, 366, "the check sits in its path", 15, rotate=-2)
        return s
    s = board(880, 262, label)
    s.label_text(40, 54, "What I build")
    s.text(40, 108, "Check before acting.", "serif", 38, "text")
    s.lines(40, 148, wrap(sub, "serif", 18, 318), "serif", 18, 1.45, "muted")
    panel(s, 388, 24, 468, 214)
    _idea_diagram(s, 414, 66)
    note(s, 414, 54, "a request comes in", 14)
    arrow(s, "M452 64 C 456 80, 458 92, 460 106", "M453 99 L460 108 L465 98")
    note(s, 582, 222, "the check sits in its path", 14, "middle", rotate=-2)
    return s


# ---------------------------------------------------------------- isometric project icons
PAPER = ("#ece9e1", "#bdb9af", "#8f8c84")
WARM = (C["warm-top"], C["warm-front"], C["warm-end"])
DARK = ("#3b3e44", "#2a2c31", "#202226")
GLASS = ("#c5cdff", C["accent"], "#6c78c9")


def iso_icon(kind, ox, oy, s=11):
    cam = Camera(ox, oy, s)
    p = []
    if kind == "car":
        for wx, wy in ((3.4, 0), (3.4, 2.2), (0.6, 0), (0.6, 2.2)):
            p.append(cam.prism(wx - 0.4, wy - 0.15, 0, wx + 0.4, wy + 0.15, 0.7, *DARK))
        p.append(cam.prism(0, 0.05, 0.35, 4, 2.15, 1.25, *WARM))
        p.append(cam.prism(1, 0.3, 1.25, 3.1, 1.9, 2.05, *GLASS))
    elif kind == "envelope":
        p.append(cam.prism(0, 0, 0, 4, 2.8, 0.35, *PAPER))
        t = lambda x, y: (x, y, 0.36)
        p.append(f'<polyline points="{cam.pts([t(0, 0), t(2, 1.5), t(4, 0)])}" fill="none" stroke="#8f8c84" stroke-width="1.2"/>')
        p.append(cam.prism(1.6, 1.9, 0.35, 2.4, 2.4, 0.5, *WARM))
    elif kind == "papers":
        for i, (dx, dy) in enumerate(((0.3, 0.2), (0.15, 0.1), (0, 0))):
            z = i * 0.45
            p.append(cam.prism(dx, dy, z, dx + 3, dy + 3.6, z + 0.3, *PAPER))
        t = lambda x, y: (x, y, 1.21)
        for k in range(4):
            y = 0.7 + k * 0.6
            p.append(f'<polyline points="{cam.pts([t(0.5, y), t(2.5 - (k % 2) * 0.8, y)])}" stroke="#8f8c84" stroke-width="1.1" fill="none"/>')
        p.append(cam.prism(2.2, 2.6, 1.2, 2.7, 3.1, 1.9, *GLASS))
    elif kind == "report":
        p.append(cam.prism(0, 0, 0, 3.2, 4, 0.3, *PAPER))
        t = lambda x, y: (x, y, 0.31)
        for k, ok in enumerate((True, True, False, True)):
            y = 0.7 + k * 0.85
            p.append(f'<polyline points="{cam.pts([t(0.4, y), t(1.9, y)])}" stroke="#8f8c84" stroke-width="1.2" fill="none"/>')
            col = C["verified"] if ok else C["invalid"]
            p.append(cam.prism(2.3, y - 0.22, 0.3, 2.75, y + 0.22, 0.55, col, col, col))
    return "".join(p)


# ---------------------------------------------------------------- the four diagrams
# Each one redraws the live stage of its system on the home page of exoxeph.github.io, with the same recorded data.
# Each is drawn in a 392 x 250 box whose top left corner is (x, y).
def dia_pool(s, x, y):
    u, x0 = 56, x + 20
    red = hatch(s, "invalid")

    def row(yy, title, result, rcol, blocks):
        s.text(x0, yy - 10, title, "mono", 11, "muted")
        s.text(x0 + 6 * u, yy - 10, result, "mono5", 14, rcol, "end")
        s.rect(x0, yy, 6 * u, 44, "bg", "rule", 1, 4)
        for a, b, name, kind in blocks:
            if kind == "ok":
                s.rect(x0 + a * u + 1.5, yy + 1.5, (b - a) * u - 3, 41, "#2c3350", "accent", 1, 3)
            elif kind == "bad":
                s.add(f'<rect x="{x0 + a * u + 1.5}" y="{yy + 1.5}" width="{(b - a) * u - 3}" height="41" rx="3" fill="{red}" stroke="{C["invalid"]}"/>')
            else:
                s.rect(x0 + a * u + 1.5, yy + 1.5, (b - a) * u - 3, 41, "bg", "verified", 1.2, 3, extra='stroke-dasharray="4 3"')
            s.text(x0 + (a + b) / 2 * u, yy + 27, name, "mono5", 12.5, "text", "middle")

    row(y + 60, "without the check", "5 of 3", "invalid", [(0, 1, "A", "ok"), (1, 3, "B", "ok"), (3, 5, "C", "bad")])
    row(y + 150, "with the check", "3 of 3", "verified", [(0, 1, "A", "ok"), (1, 3, "B", "ok"), (3, 5, "C refused", "no")])
    cx = x0 + 3 * u
    s.line(cx, y + 28, cx, y + 204, "accent", 2.5)
    s.add(f'<circle cx="{cx}" cy="{y + 24}" r="6" fill="{C["accent"]}"/>')
    s.add(f'<circle cx="{cx}" cy="{y + 24}" r="11" fill="none" stroke="{C["accent"]}" stroke-opacity="0.4"/>')
    s.text(cx + 18, y + 28, "capacity 3", "mono", 11.5, "accent")
    for i in range(7):
        s.line(x0 + i * u, y + 204, x0 + i * u, y + 210, "muted")
        s.text(x0 + i * u, y + 224, str(i), "mono", 11, "muted", "middle")
    s.text(x0, y + 242, "seats taken · recorded on a mock database", "mono", 11, "muted")


def dia_email(s, x, y):
    for i, name in enumerate(("intent", "key facts", "tone")):
        yy = y + 26 + i * 38
        s.rect(x + 16, yy, 86, 28, "bg", "muted", 1, 6)
        s.text(x + 59, yy + 18, name, "mono", 11.5, "text", "middle")
        s.add(f'<path d="M{x + 102} {yy + 14} C {x + 118} {yy + 14}, {x + 118} {y + 78}, {x + 132} {y + 78}" fill="none" stroke="{C["rule"]}" stroke-width="1.4"/>')
    cx, cy = x + 160, y + 78
    s.add(f'<polygon points="{cx},{cy - 28} {cx + 28},{cy} {cx},{cy + 28} {cx - 28},{cy}" fill="{C["bg"]}" stroke="{C["text"]}" stroke-width="1.3"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{C["verified"]}"/>')
    s.text(cx, cy + 46, "code checks", "mono", 11, "muted", "middle")
    s.line(cx + 28, cy, x + 214, cy, "muted")
    s.rect(x + 214, y + 24, 162, 108, "bg", "muted", 1, 8, extra='stroke-dasharray="4 3"')
    s.text(x + 295, y + 46, "model: enough", "mono", 11.5, "text", "middle")
    s.text(x + 295, y + 62, "to write from?", "mono", 11.5, "text", "middle")
    for yy, txt, col in ((y + 74, "yes: writes it", "verified"), (y + 101, "no: asks first", "partial")):
        s.rect(x + 228, yy, 134, 22, "well", col, 1, 5)
        s.text(x + 295, yy + 15, txt, "mono", 11, col, "middle")
    s.line(x + 16, y + 148, x + 376, y + 148, "rule")
    s.text(x + 16, y + 170, "10 recorded scenarios, 9 as expected", "mono", 11, "muted")
    red = hatch(s, "invalid")
    for i in range(10):
        bx = x + 16 + i * 36.3
        if i == 3:
            s.add(f'<rect x="{f1(bx)}" y="{y + 180}" width="30" height="28" rx="4" fill="{red}" stroke="{C["invalid"]}"/>')
        else:
            s.rect(bx, y + 180, 30, 28, "#26413a", "verified", 1, 4)
        s.text(bx + 15, y + 198, str(i + 1), "mono", 11, "text", "middle")
    tw = s.text(x + 16, y + 238, "4.7", "serif", 26, "verified")
    s.text(x + 24 + tw, y + 237, "vs 4.2 for a single prompt, of 5", "mono", 11, "muted")


def dia_rag(s, x, y):
    s.text(x + 18, y + 48, "0.66", "serif", 40, "partial")
    s.text(x + 18, y + 68, "still below 0.72", "mono", 11, "muted")
    s.text(x + 18, y + 83, "after one repair", "mono", 11, "muted")
    cam = Camera(x + 38, y + 128, 33, -17)
    s.add(cam.prism(0, 0, 0, 10, 1.5, 0.32, "#34373d", "#272a2f", "#1f2125", "#50545c"))
    s.add(cam.quad([(0, 0, 0.33), (6.55, 0, 0.33), (6.55, 1.5, 0.33), (0, 1.5, 0.33)], hatch(s, "partial")))
    s.add(cam.prism(6.2, 0.35, 0.33, 6.75, 1.15, 1.25, "#e8e5dc", "#b9b6ae", "#8f8c84"))
    s.add(f'<g fill-opacity="0.82">{cam.prism(7.2, -0.1, 0, 7.45, 1.6, 2.3, "#c5cdff", C["accent"], "#6c78c9")}</g>')
    px, py = cam.at(7.32, -0.1, 2.3)
    s.add(f'<circle cx="{f1(px)}" cy="{f1(py - 8)}" r="5" fill="{C["accent"]}"/>')
    s.text(px - 12, py - 6, "needs 0.72", "mono", 11, "accent", "end")
    s.line(x + 16, y + 152, x + 376, y + 152, "rule")
    bx, bw = x + 88, 190
    for i, (q, v, ok) in enumerate((("q1", 0.82, True), ("q5", 0.72, True), ("q3", 0.67, False), ("q4", 0.655, False))):
        yy = y + 174 + i * 22
        s.text(x + 18, yy + 4, f"{q}  {v:g}", "mono", 11, "muted")
        s.rect(bx, yy - 4, bw * v, 8, "verified" if ok else "partial", None, 1, 3)
        s.text(x + 376, yy + 4, "accepted" if ok else "still below", "mono", 11, "text", "end")
    s.line(bx + bw * 0.72, y + 164, bx + bw * 0.72, y + 248, "accent", 2)


def dia_speech(s, x, y):
    s.text(x + 16, y + 24, "ocr line", "mono", 11, "muted")
    s.rect(x + 16, y + 32, 360, 30, "bg", "rule", 1, 5)
    cols = (("test", "Albumin", 30), ("value", "3.7", 130), ("unit", "g/dL", 196), ("range", "3.5 - 5.0", 272))
    for name, val, dx in cols:
        w = text_width(val, "mono", 12)
        s.text(x + dx, y + 52, val, "mono", 12, "text")
        s.add(f'<path d="M{x + dx} {y + 68} v5 h{f1(max(w, 28))} v-5" fill="none" stroke="{C["verified"]}"/>')
        s.text(x + dx, y + 88, name, "mono", 11, "verified")
    rows = (("Hemoglobin", "10.5", "g/dL", "12.0 - 16.0"), ("Glucose", "180", "mg/dL", "70 - 100"),
            ("Albumin", "3.7", "g/dL", "3.5 - 5.0"))
    for i, row in enumerate(rows):
        yy = y + 106 + i * 24
        s.rect(x + 16, yy, 360, 21, "#233029" if i == 2 else "bg", None, 1, 4)
        for val, (_, _, dx) in zip(row, cols):
            s.text(x + dx, yy + 15, val, "mono", 11.5, "text")
    red = hatch(s, "invalid")
    for i, (val, why, verdict, col) in enumerate((("1.2 x 1043", "not a number", "row left out", "invalid"),
                                                  ("<8.5", "looks valid", "row kept", "partial"))):
        yy = y + 192 + i * 31
        s.line(x + 16, yy - 5, x + 376, yy - 5, "rule")
        s.text(x + 18, yy + 16, val, "mono5", 12, "text")
        s.text(x + 130, yy + 16, why, "mono", 11, "muted")
        s.add(f'<rect x="{x + 264}" y="{yy + 1}" width="112" height="22" rx="5" fill="{red if i == 0 else C["bg"]}" stroke="{C[col]}"/>')
        s.text(x + 320, yy + 16, verdict, "mono", 11, "text", "middle")


DIAGRAMS = {"car": (dia_pool, "pool"), "envelope": (dia_email, "email"), "papers": (dia_rag, "rag"),
            "report": (dia_speech, "speech")}


# ---------------------------------------------------------------- projects
def project_label(pr):
    return f"{pr['question']} It fails: {pr['fails']} It catches: {pr['catches']} Limit: {pr['limit']}"


def project(P, i, phone=False):
    pr = P["projects"][i]
    draw, tint = DIAGRAMS[pr["icon"]]
    n = f"{i + 1:02d} / {len(P['projects']):02d}"
    s = board(440, 336 if phone else 548, project_label(pr))
    s.rect(M + 1, M + 1, 440 - 2 * M - 2, s.h - 2 * M - 2, tint, None, 1, RADIUS - 1, extra='fill-opacity="0.78"')
    if phone:
        s.add(iso_icon(pr["icon"], 322, 70, 15))
        s.label_text(30, 52, f"{n}", "accent", 17)
        s.label_text(30, 82, pr["domain"], "muted", 16)
        s.lines(30, 154, wrap(pr["question"], "serif", 37, 376), "serif", 37, 1.16, "text")
        chip_flow(s, 30, 264, pr["tech"][:2], "accent", 340, 10, 15, 34)
        return s
    s.add(iso_icon(pr["icon"], 28, 38, 7))
    s.label_text(72, 46, f"{n} · {pr['domain']}")
    open_mark(s, 384, 26)
    s.lines(28, 94, wrap(pr["question"], "serif", 24, 384), "serif", 24, 1.22, "text")
    panel(s, 24, 144, 392, 256)
    draw(s, 24, 146)
    s.label_text(28, 428, "Where it still fails", "partial", 11)
    s.lines(28, 450, wrap(pr["limit"], "sans", 13.5, 384)[:2], "sans", 13.5, 1.45, "text")
    tech = list(pr["tech"])
    while len(tech) > 1 and sum(text_width(t, "mono", 11.5) + 26 for t in tech) > 392:
        tech.pop()
    chip_flow(s, 28, 496, tech, "accent", 392)
    return s


def weeks_of(cal, n_weeks):
    """The last n_weeks calendar weeks (Sunday first, as GitHub draws them): a list of 7-slot lists."""
    days = sorted(cal)
    last = date.fromisoformat(days[-1])
    start = last - timedelta(days=(last.weekday() + 1) % 7) - timedelta(weeks=n_weeks - 1)
    out = []
    for w in range(n_weeks):
        week = []
        for d in range(7):
            day = start + timedelta(weeks=w, days=d)
            week.append((day, cal.get(day.isoformat())))
        out.append(week)
    return out


def skyline(s, cal, ox, oy, scale, n_weeks, max_z=5.2, az=-30):
    """The contribution calendar as an isometric city in the dev room's warm materials: one block per day,
    as tall as that day's contributions (square-root scale, so one busy day does not flatten the rest)."""
    weeks = weeks_of(cal, n_weeks)
    counts = sorted(c for wk in weeks for _, c in wk if c)
    top = counts[int(len(counts) * 0.97) - 1] if counts else 1
    cam = Camera(ox, oy, scale, az)
    W = len(weeks)
    s.add(cam.prism(-0.5, -0.5, -0.7, W + 0.3, 7.5, 0, "#24262a", "#1c1e21", "#18191b"))
    hi = ("#ffe2a8", "#f0a050", "#b8642f")
    for x in range(W - 1, -1, -1):
        for y in range(7):
            day, c = weeks[x][y]
            if c is None:
                continue
            if not c:
                s.add(cam.prism(x + 0.12, y + 0.12, 0, x + 0.88, y + 0.88, 0.06, "#2e3135", "#26282c", "#222427"))
                continue
            z = 0.25 + max_z * math.sqrt(min(c, top) / top)
            tones = hi if c >= top * 0.6 else WARM
            s.add(cam.prism(x + 0.12, y + 0.12, 0, x + 0.88, y + 0.88, z, *tones))
    # month ticks along the front edge
    seen = None
    for x, wk in enumerate(weeks):
        m = wk[0][0].strftime("%b")
        if m != seen and wk[0][0].day <= 7:
            px, py = cam.at(x, 8.2, 0)
            s.text(px, py + 10, m.upper(), "mono", 11, "muted", tracking=0.08)
        seen = m
    return weeks


def github_label(data):
    from fetch import streaks
    cal = data["calendar"]
    active = sum(1 for c in cal.values() if c)
    return (f"On GitHub: {fmt(sum(cal.values()))} contributions in the last year, drawn as an isometric city with one "
            f"block per day. {active} active days, longest streak {streaks(cal)[1]} days, "
            f"{data['repos']['public_repos']} public repositories.")


def stat_tile(s, x, y, w, value, label, tint, color):
    s.rect(x + 3, y + 4, w, 96, "well", None, 1, 11)
    s.rect(x, y, w, 96, tint, color, 1.2, 11, extra='stroke-opacity="0.45"')
    s.text(x + 16, y + 52, value, "serif5", 40, "text")
    s.text(x + 16, y + 77, label, "mono", 11, "muted")


def github(P, data=None, phone=False):
    from fetch import streaks
    cal = data["calendar"]
    active = sum(1 for c in cal.values() if c)
    stats = ((fmt(sum(cal.values())), "contributions this year", "pool", "accent"),
             (str(active), "active days", "email", "verified"),
             (str(streaks(cal)[1]), "day longest streak", "rag", "invalid"),
             (str(data["repos"]["public_repos"]), "public repos", "speech", "partial"))
    s = board(440 if phone else 880, 624 if phone else 552, github_label(data))
    s.text(28, 56, "On GitHub", "serif5", 28, "text")
    if phone:
        for i, (v, lab, tint, col) in enumerate(stats):
            stat_tile(s, 28 + (i % 2) * 196, 80 + (i // 2) * 112, 184, v, lab, tint, col)
        panel(s, 24, 314, 392, 284)
        skyline(s, cal, 46, 506, 13.4, 26, 9.0, -18)
        s.text(40, 586, "last 26 weeks · redrawn nightly", "mono", 11, "muted")
        return s
    s.text(852, 54, "redrawn every night", "mono", 12, "muted", "end")
    for i, (v, lab, tint, col) in enumerate(stats):
        stat_tile(s, 28 + i * 208, 78, 197, v, lab, tint, col)
    panel(s, 28, 196, 824, 328)
    skyline(s, cal, 68, 444, 14, 53, 10, -18)
    s.text(834, 506, "one block per day, last 12 months", "mono", 11, "muted", "end")
    return s


# ---------------------------------------------------------------- whoami
def whoami_label(P):
    w = P["whoami"]
    return " ".join([w["who"], w["line"]] + w["now"])


def whoami(P, phone=False):
    w = P["whoami"]
    W = 440 if phone else 880
    size = 13.5 if phone else 15
    width = W - 110
    rows = [("cmd", "whoami")] + [("text", t) for t in wrap(w["who"], "mono", size, width + 20)]
    rows += [("dim", t) for t in wrap(w["line"], "mono", size, width + 20)]
    rows += [("gap", ""), ("cmd", "cat interests.txt")]
    for item in w["now"]:
        for k, t in enumerate(wrap(item, "mono", size, width)):
            rows.append(("item" if k == 0 else "cont", t))
    rows.append(("cursor", ""))
    step = size * 1.75
    h = round(112 + step * len(rows))
    s = board(W, h, whoami_label(P))
    panel(s, 24, 24, W - 48, h - 48)
    s.line(24, 60, W - 24, 60, "rule")
    for i, col in enumerate(("invalid", "partial", "verified")):
        s.add(f'<circle cx="{46 + i * 19}" cy="42" r="5" fill="{C[col]}"/>')
    s.text(W / 2 + 14, 46.5, "imtiaz@dhaka: ~", "mono", 12, "muted", "middle")
    y = 94
    for kind, t in rows:
        if kind == "cmd":
            s.text(48, y, "$", "mono5", size, "partial")
            s.text(70, y, t, "mono5", size, "text")
        elif kind in ("text", "dim"):
            s.text(48, y, t, "mono", size, "text" if kind == "text" else "muted")
        elif kind in ("item", "cont"):
            if kind == "item":
                s.text(48, y, "→", "mono", size, "verified")
            s.text(70, y, t, "mono", size, "muted")
        elif kind == "cursor":
            s.text(48, y, "$", "mono5", size, "partial")
            s.add(f'<rect class="cursor" x="70" y="{f1(y - size * 0.85)}" width="9" height="{f1(size * 1.05)}" fill="{C["text"]}"/>')
        y += step * (0.6 if kind == "gap" else 1)
    s.css.append("@keyframes blink{50%{opacity:0}}.cursor{animation:blink 1.1s steps(1) infinite}")
    return s


# ---------------------------------------------------------------- research and certifications
def creds_label(P):
    e = P["education"]
    return (f"Research: {e['thesis']}. {e['course']}, {e['school']}. Certifications: "
            + ", ".join(c["name"] for c in P["certs"]) + ".")


def creds(P, phone=False):
    e = P["education"]
    tints = (("pool", "accent"), ("email", "verified"), ("rag", "invalid"), ("speech", "partial"))
    tw = 184 if phone else 197
    s = board(440 if phone else 880, 726 if phone else 452, creds_label(P))
    s.text(28, 56, "Research and certifications", "serif5", 24 if phone else 28, "text")
    pw = 392 if phone else 824
    panel(s, 24 if phone else 28, 78, pw, 190 if phone else 138)
    x = 44 if phone else 52
    s.label_text(x, 110, "Thesis", "accent", 11)
    ty = s.lines(x, 144, wrap(e["thesis"], "serif", 23, pw - 52), "serif", 23, 1.3, "text", italic=True)
    s.lines(x, ty + 6, wrap(f"{e['course']}, {e['school']} · {e['dates']}", "mono", 11.5, pw - 52), "mono", 11.5, 1.6, "muted")
    for i, c in enumerate(P["certs"]):
        tint, col = tints[i]
        if phone:
            cx, cy = 28 + (i % 2) * 196, 288 + (i // 2) * 208
        else:
            cx, cy = 28 + i * 208, 234
        s.rect(cx + 3, cy + 4, tw, 188, "well", None, 1, 11)
        s.rect(cx, cy, tw, 188, tint, col, 1.2, 11, extra='stroke-opacity="0.45"')
        s.add(f'<image href="{data_uri(os.path.join(ART, "certs", c["file"]))}" x="{cx + tw / 2 - 36}" y="{cy + 18}" width="72" height="72"/>')
        s.lines(cx + tw / 2, cy + 116, wrap(c["name"], "sans5", 13.5, tw - 24), "sans5", 13.5, 1.38, "text", anchor="middle")
        s.text(cx + tw / 2, cy + 172, c["date"], "mono", 11, "muted", "middle")
    return s


# ---------------------------------------------------------------- tools
def stack(P, phone=False):
    groups = P["stack"]
    label = "Tools: " + "; ".join(f"{g}: {', '.join(items)}" for g, items in groups) + "."
    cols = ("accent", "verified", "invalid", "partial")
    W = 440 if phone else 880

    def layout(s):
        y = 98
        for (g, items), col in zip(groups, cols):
            if phone:
                s.label_text(28, y + 4, g, col, 11)
                y = chip_flow(s, 28, y + 18, items, col, 384, 9, 13, 30) + 28
            else:
                for k, ln in enumerate(wrap(g, "sans5", 13.5, 170)):
                    s.text(28, y + 20 + k * 18, ln, "sans5", 13.5, col)
                y = chip_flow(s, 218, y, items, col, 634, 9, 13, 32) + 22
        return y

    h = layout(Svg(W, 10, label))
    s = board(W, h + (6 if phone else 12), label)
    s.text(28, 58, "Tools I reach for", "serif5", 28, "text")
    layout(s)
    return s
