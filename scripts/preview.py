# Renders cards into dev/ and writes dev/preview.html, which shows them on GitHub's dark page.
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "dev")
os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.join(HERE, "profile.json"), encoding="utf8"))
ST = json.load(open(os.path.join(HERE, "state.json"), encoding="utf8"))
DATA = {"calendar": ST["calendar"]["value"], "repos": ST["repos"]["value"]}
names = sys.argv[1:] or ["hero"]
html = ['<body style="margin:0;background:#0d1117;padding:24px;display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start">']
for n in names:
    jobs = []
    if n == "project":
        jobs = [(f"project{i}", (lambda i: lambda ph: cards.project(P, i, ph))(i)) for i in range(len(P["projects"]))]
    elif n == "github":
        jobs = [("github", lambda ph: cards.github(P, DATA, ph))]
    elif n == "button":
        jobs = [("button", lambda ph: cards.button(cards.site_host(P), "accent"))]
    else:
        jobs = [(n, lambda ph, n=n: getattr(cards, n)(P, phone=ph))]
    for name, fn in jobs:
        for phone in (False, True):
            s = fn(phone)
            f = f"{name}{'-phone' if phone else ''}.svg"
            open(os.path.join(OUT, f), "w", encoding="utf8").write(s.render())
            print(f, s.w, s.h, "min font", s.min_size, "overflow", s.overflow)
            html.append(f'<img src="{f}" width="{s.w if not (phone and name.startswith("project")) else 220}">')
open(os.path.join(OUT, "preview.html"), "w", encoding="utf8").write("".join(html))
