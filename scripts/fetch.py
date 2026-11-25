# Fetches the numbers that change by themselves: the contribution calendar (from the public profile page, the
# same count a visitor sees) and the public repositories and their stars (GitHub REST API). Each source falls
# back to its last good copy in state.json, so one failed request never blanks a card.
import json, os, re, urllib.request
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
UA = "exoxeph-profile-readme"


def _get(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if accept:
        req.add_header("Accept", accept)
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf8")


def parse_calendar(html):
    """{iso date: count} from the profile's contribution calendar HTML."""
    ids = {m.group(2): m.group(1) for m in re.finditer(r'data-date="([\d-]+)"[^>]*?id="([^"]+)"', html)}
    days = {d: 0 for d in ids.values()}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        d = ids.get(m.group(1))
        n = re.match(r"\s*([\d,]+) contributions?", m.group(2))
        if d and n:
            days[d] = int(n.group(1).replace(",", ""))
    if len(days) < 300:
        raise ValueError(f"calendar has {len(days)} days; the page layout may have changed")
    return dict(sorted(days.items()))


def fetch_calendar(user):
    return parse_calendar(_get(f"https://github.com/users/{user}/contributions"))


def fetch_repos(user):
    repos, page = [], 1
    while True:
        batch = json.loads(_get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner&page={page}",
                                "application/vnd.github+json"))
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]
    return {"public_repos": len(own), "stars": sum(r.get("stargazers_count", 0) for r in own)}


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf8") as fh:
            return json.load(fh)
    return {}


def fetch_all(user):
    """Returns (data, problems). data holds every source, fresh or from the saved copy."""
    state, problems = load_state(), []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    for key, fn in (("calendar", fetch_calendar), ("repos", fetch_repos)):
        try:
            state[key] = {"value": fn(user), "fetched": now}
        except Exception as e:  # keep the last good copy
            problems.append(f"{key}: {e}")
            if key not in state:
                raise
    with open(STATE, "w", encoding="utf8") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
        fh.write("\n")
    cal = state["calendar"]["value"]
    return {"calendar": cal, "repos": state["repos"]["value"], "today": max(cal)}, problems


def streaks(cal, today=None):
    """(current, longest) in days. Today without a contribution does not break the current streak yet."""
    ds = sorted(cal)
    longest = run = 0
    for d in ds:
        run = run + 1 if cal[d] else 0
        longest = max(longest, run)
    cur = 0
    for i, d in enumerate(reversed(ds)):
        if cal[d]:
            cur += 1
        elif i == 0:
            continue
        else:
            break
    return cur, longest
