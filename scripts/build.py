# Builds every card and README.md. Run: python scripts/build.py
# Fetches the live numbers first (falling back to the saved copy in state.json); exits non-zero when a source
# could not be fetched for more than three days, after still writing everything from the saved copy.
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards
import readme
from fetch import fetch_all, load_state

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")


def write_svg(name, svg):
    os.makedirs(ASSETS, exist_ok=True)
    problems = []
    if svg.overflow:
        problems.append(f"{name}: text runs past the edge: {svg.overflow}")
    if svg.min_size < 11:
        problems.append(f"{name}: text smaller than 11px")
    with open(os.path.join(ASSETS, f"{name}.svg"), "w", encoding="utf8", newline="\n") as fh:
        fh.write(svg.render())
    return problems


def main():
    P = json.load(open(os.path.join(HERE, "profile.json"), encoding="utf8"))
    data, fetch_problems = fetch_all(P["user"])
    problems = []
    labels = {}

    def both(name, fn):
        d = fn(False)
        labels[name] = d.label
        problems.extend(write_svg(name, d))
        problems.extend(write_svg(f"{name}-phone", fn(True)))

    both("hero", lambda ph: cards.hero(P, ph))
    both("idea", lambda ph: cards.idea(P, ph))
    for i, pr in enumerate(P["projects"]):
        both(f"project-{pr['id']}", lambda ph, i=i: cards.project(P, i, ph))
    both("github", lambda ph: cards.github(P, data, ph))
    both("whoami", lambda ph: cards.whoami(P, ph))
    both("creds", lambda ph: cards.creds(P, ph))
    both("stack", lambda ph: cards.stack(P, ph))
    for name, text, tint in (("site", "exoxeph.github.io", "accent"), ("resume", "Résumé", "partial"),
                             ("linkedin", "LinkedIn", "#4d8fd6"), ("email", "Email", "invalid")):
        problems.extend(write_svg(f"btn-{name}", cards.button(text, tint)))

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf8", newline="\n") as fh:
        fh.write(readme.render(P, labels))

    if problems:
        print("layout problems:\n  " + "\n  ".join(problems))
        sys.exit(2)
    stale = []
    state = load_state()
    now = datetime.now(timezone.utc)
    for key in ("calendar", "repos"):
        fetched = datetime.strptime(state[key]["fetched"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        if (now - fetched).days > 3:
            stale.append(f"{key} last fetched {state[key]['fetched']}")
    for p in fetch_problems:
        print("fetch problem:", p)
    if stale:
        print("stale sources:", "; ".join(stale))
        sys.exit(1)
    print("built", len(os.listdir(ASSETS)), "files in assets/")


if __name__ == "__main__":
    main()
