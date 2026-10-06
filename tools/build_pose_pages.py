#!/usr/bin/env python3
"""Build poses/<slug>.html for every tools/poses/<slug>.json, plus the sitemap and llms.txt pose list.

Run from anywhere: python3 tools/build_pose_pages.py
Page style, layout and nav/footer live in tools/partials.html. Copy lives in the JSON files.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SITE = "https://posewise.app"
UPDATED = "2026-10-06"
UPDATED_TEXT = "October 6, 2026"

# Home page grid order, so "More guides" and llms.txt read in the same order as the site.
ORDER = ["downward-dog", "warrior-2", "warrior-1", "upward-dog", "chair", "crescent-lunge",
         "extended-side-angle", "goddess", "triangle", "tree", "cobra", "bridge", "mountain", "childs-pose"]


def partial(name):
    text = (TOOLS / "partials.html").read_text()
    return re.search(rf"<!-- {name} -->\n(.*?)\n(?=<!-- |\Z)", text, re.S).group(1)


def esc(text):
    """Copy may contain <b>/<a> markup on purpose; only escape ampersands that aren't entities."""
    return re.sub(r"&(?!\w+;|#\d+;)", "&amp;", text)


def row(r):
    return (f'      <li><a class="name" href="#{r["fix"]}">{esc(r["name"])}</a>'
            f'<span class="good">{esc(r["good"])}</span>'
            f'<span class="target">{esc(r["target"])}<small>{esc(r["small"])}</small></span></li>\n')


def exercise(e):
    return (f'<li><img src="/assets/ex/{e["id"]}.webp" alt="" width="160" height="160" loading="lazy">'
            f'<div class="cap">{esc(e["name"])}<span>{esc(e["dose"])}</span></div></li>')


def fix(f):
    return f'''  <section class="fix" id="{f["id"]}">
    <p class="say"><b>{esc(f["action"])}</b>, and {esc(f["outcome"])}</p>
    <p class="why">{esc(f["why"])}</p>
    <ul class="try">{"".join(exercise(e) for e in f["exercises"])}</ul>
    <p class="cue">{esc(f["cue"])}</p>
  </section>

'''


def short_question(q, name):
    for suffix in (f" in {name}", f" in a {name}"):
        q = q.replace(suffix, "")
    return q


def page(p, others):
    url = f'{SITE}/poses/{p["slug"]}'
    name = p["name"]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": f'How to Improve Your {name}: {len(p["fixes"])} Fixes',
         "description": p["og_description"], "image": f'{SITE}{p["hero"]}',
         "datePublished": p.get("published", UPDATED), "dateModified": UPDATED,
         "author": {"@type": "Organization", "name": "Posewise", "url": f"{SITE}/"},
         "publisher": {"@type": "Organization", "name": "Posewise", "url": f"{SITE}/"},
         "about": {"@type": "Thing", "name": p["about"]}, "mainEntityOfPage": url},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Posewise", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Poses", "item": f"{SITE}/#poses"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url}]},
        {"@type": "SoftwareApplication", "name": "Posewise", "operatingSystem": "iOS",
         "applicationCategory": "HealthApplication",
         "description": "An iPhone app that uses the camera to check yoga pose alignment, gives live spoken corrections, and builds a six-minute daily workout of the exercises you need.",
         "url": f"{SITE}/"},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", f["a"])}} for f in p["faq"]]},
    ]}
    details = "".join(
        f'  <details>\n    <summary>{esc(short_question(f["q"], name))}</summary>\n    <p>{esc(f["a"])}</p>\n  </details>\n'
        for f in p["faq"])
    more = " · ".join(f'<a href="/poses/{o["slug"]}">{esc(o["name"])}</a>' for o in others)
    cues = f'  <p class="cueonly" id="cues">{esc(p["cues"])}</p>\n\n' if p.get("cues") else ""
    title = f'How to Improve Your {name}: {len(p["fixes"])} Fixes — Posewise'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title, quote=False)}</title>
<meta name="description" content="{html.escape(p["meta_description"])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="How to Improve Your {html.escape(name)}">
<meta property="og:description" content="{html.escape(p["og_description"])}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
{partial("STYLE").replace("{hero}", p["hero"])}
</head>
<body>

{partial("NAV")}

<main class="wrap">
  <header>
    <p class="kicker">Pose guide</p>
    <h1>How to improve your {esc(name)}</h1>
    <p class="lede">{esc(p["lede"])}</p>
    <div class="hero" role="img" aria-label="{html.escape(p["hero_alt"])}"></div>
  </header>

  <h2 id="rubric">The rubric</h2>
  <p class="sub">{esc(p["rubric_intro"])}</p>
  <ul class="rubric">
{"".join(row(r) for r in p["rubric"])}  </ul>

  <h2>What’s holding it back</h2>

{"".join(fix(f) for f in p["fixes"])}{cues}  <section class="app" id="check-your-form">
    <h2>Not sure which one is yours?</h2>
    <p>Posewise watches your {esc(name)} through your iPhone camera, tells you which of these is holding you back, and builds a six-minute daily plan to fix it. Video never leaves your phone.</p>
    <a class="btn" href="/#join">Join the beta</a>
    <p class="small">Free during the beta · iPhone</p>
  </section>

  <h2>Quick answers</h2>
{details}
  <p class="meta">Updated {UPDATED_TEXT} · General information, not medical advice.<br>More pose guides: {more}</p>
</main>

{partial("FOOTER")}

</body>
</html>
'''


def check(p):
    anchors = {f["id"] for f in p["fixes"]} | ({"cues"} if p.get("cues") else set())
    for r in p["rubric"]:
        assert r["fix"] in anchors, f'{p["slug"]}: rubric row {r["name"]} links to missing #{r["fix"]}'
    for f in p["fixes"]:
        assert len(f["exercises"]) == 2, f'{p["slug"]}: {f["id"]} needs exactly two exercises'
        for e in f["exercises"]:
            assert (ROOT / "assets/ex" / f'{e["id"]}.webp').exists(), f'{p["slug"]}: missing assets/ex/{e["id"]}.webp'
    assert (ROOT / p["hero"].lstrip("/")).exists(), f'{p["slug"]}: missing hero {p["hero"]}'


def main():
    poses = {}
    for path in sorted((TOOLS / "poses").glob("*.json")):
        p = json.loads(path.read_text())
        check(p)
        poses[p["slug"]] = p
    ordered = [poses[s] for s in ORDER if s in poses] + [p for s, p in poses.items() if s not in ORDER]
    for p in ordered:
        others = [o for o in ordered if o is not p]
        (ROOT / "poses" / f'{p["slug"]}.html').write_text(page(p, others))

    urls = [f"{SITE}/"] + [f'{SITE}/poses/{p["slug"]}' for p in ordered]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod></url>\n" for u in urls)
        + "</urlset>\n")

    llms = (ROOT / "llms.txt").read_text()
    guides = "".join(
        f'- [How to improve your {p["name"]}]({SITE}/poses/{p["slug"]}): {p["llms_summary"]}\n' for p in ordered)
    llms = re.sub(r"(## Pose guides\n\n)(.*?)(\n## )", lambda m: m.group(1) + guides + m.group(3), llms, flags=re.S)
    (ROOT / "llms.txt").write_text(llms)
    print(f"built {len(ordered)} pose pages")


if __name__ == "__main__":
    main()
