# README.md from the cards. Every image is a <picture>: a phone source for narrow screens (GitHub's mobile web),
# then the desktop <img>. The cards are dark on purpose: exoxeph.github.io is dark only, so they look the same on
# GitHub's light and dark themes.
from html import escape

from cards import site_host


def picture(name, alt, width="100%"):
    return (f'<picture><source media="(max-width: 600px)" srcset="assets/{name}-phone.svg">'
            f'<img src="assets/{name}.svg" width="{width}" alt="{escape(alt, quote=True)}"></picture>')


def button(name, alt):
    return f'<img src="assets/btn-{name}.svg" height="46" alt="{escape(alt, quote=True)}">'


def link(url, inner):
    return f'<a href="{url}">{inner}</a>'


def render(P, labels):
    L, site = P["links"], P["links"]["site"]
    host = site_host(P)
    out = [link(site, picture("hero", labels["hero"])), ""]
    out += ['<p align="center">',
            link(site, button("site", f"Portfolio: {host}")),
            link(L["resume"], button("resume", "Résumé")),
            link(L["linkedin"], button("linkedin", "LinkedIn")),
            link(L["email"], button("email", "Email")),
            "</p>", ""]
    out += [picture("github", labels["github"]), ""]
    out += [picture("whoami", labels["whoami"]), ""]
    out += [link(site, picture("idea", labels["idea"])), ""]
    cells = [link(f"{L['work']}{pr['id']}/", picture(f"project-{pr['id']}", labels[f"project-{pr['id']}"], "49%"))
             for pr in P["projects"]]
    out += ['<p align="center">', *cells, "</p>", ""]
    code = " · ".join(link(pr["repo"], pr["repo"].rsplit("/", 1)[1]) for pr in P["projects"])
    out += [f'<p align="center"><sub>Each card opens its case study. The code: {code}</sub></p>', ""]
    out += [picture("creds", labels["creds"]), ""]
    creds = " · ".join(link(c["url"], c["name"]) for c in P["certs"])
    out += [f'<p align="center"><sub>Verify: {creds}</sub></p>', ""]
    out += [picture("stack", labels["stack"]), ""]
    out += [f'<p align="center"><sub>Drawn in the design system of {link(site, host)}'
            f' · GitHub numbers redrawn every night by a GitHub Action</sub></p>', ""]
    return "\n".join(out)
