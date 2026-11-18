"""Build every page of the site from tools/pages/*.html.

Each page source starts with a JSON front-matter block between <!--meta and -->:
  {"path": "about/index.html", "url": "/about/", "nav": "/about/", "crumb": "...",
   "title": "...", "description": "...", "jsonld": [...], "extra_head": "..."}
Page bodies can pull shared blocks with <!--@include NAME-->:
  - a file tools/partials/NAME.html, or
  - a block generated from tools/data.json (ingredients, certificates, news, gallery, gallery-preview).
Run:  python tools/build_pages.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SITE = "https://www.panarint.com"
IMG = "/assets/img/site"

data = json.loads((TOOLS / "data.json").read_text(encoding="utf-8"))
header = (TOOLS / "partials" / "header.html").read_text(encoding="utf-8")
footer = (TOOLS / "partials" / "footer.html").read_text(encoding="utf-8")

HEAD = """<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#003078">
  <meta property="og:type" content="{og_type}">
  <meta property="og:locale" content="th_TH">
  <meta property="og:site_name" content="PANARIN ตรา พนารินทร์">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{site}/assets/img/og-panarin.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Kanit:wght@600;700;800&family=Prompt:wght@400;600&display=swap">
  <link rel="stylesheet" href="/assets/css/site.css">
{extra_head}  <script type="application/ld+json">
{jsonld}
  </script>
</head>
<body>
"""

esc = html.escape


def ingredients():
    items = "\n".join(
        f'          <li><img src="{IMG}/{i["img"]}" width="320" height="320" loading="lazy" alt="{esc(i["name"])}"><span>{esc(i["name"])}</span></li>'
        for i in data["ingredients"]
    )
    return f'        <ul class="ing-grid">\n{items}\n        </ul>'


def certificates():
    items = "\n".join(
        f'          <li><a href="{IMG}/{c["img"]}" target="_blank" rel="noopener"><img src="{IMG}/{c["img"]}" width="{c["w"]}" height="{c["h"]}" loading="lazy" alt="{esc(c["alt"])}"></a><span>{esc(c["title"])}</span></li>'
        for c in data["certificates"]
    )
    return f'        <ul class="cert-grid">\n{items}\n        </ul>'


def news(limit=None):
    rows = data["news"][:limit] if limit else data["news"]
    items = "\n".join(
        f'          <article class="news-card"><img src="{IMG}/{n["img"]}" width="{n["w"]}" height="{n["h"]}" loading="lazy" alt="{esc(n["alt"])}">'
        f'<div class="news-card__body"><time datetime="{n["date"]}">{esc(n["date_th"])}</time><h3>{esc(n["title"])}</h3></div></article>'
        for n in rows
    )
    return f'        <div class="news-grid">\n{items}\n        </div>'


def gallery(limit=None):
    rows = data["gallery"][:limit] if limit else data["gallery"]
    items = "\n".join(
        f'          <li><img src="{IMG}/{g}" width="400" height="284" loading="lazy" alt="ลูกค้าและร้านค้าตัวแทนจำหน่ายถือน้ำมังคุด ตรา พนารินทร์ ภาพที่ {n}"></li>'
        for n, g in enumerate(rows, 1)
    )
    return f'        <ul class="gallery">\n{items}\n        </ul>'


BLOCKS = {
    "ingredients": ingredients,
    "certificates": certificates,
    "news": news,
    "news-preview": lambda: news(3),
    "gallery": gallery,
    "gallery-preview": lambda: gallery(12),
}


def include(m):
    name = m.group(1)
    if name in BLOCKS:
        return BLOCKS[name]()
    return (TOOLS / "partials" / f"{name}.html").read_text(encoding="utf-8").rstrip()


def breadcrumb(name, url):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "หน้าแรก", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": SITE + url},
        ],
    }


for src in sorted((TOOLS / "pages").glob("*.html")):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", text, re.S)
    meta = json.loads(m.group(1))
    body = re.sub(r"[ \t]*<!--@include ([\w-]+)-->", include, text[m.end():])
    graph = ([breadcrumb(meta["crumb"], meta["url"])] if meta.get("crumb") else []) + meta.get("jsonld", [])
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    page_header = header
    if meta.get("nav"):
        page_header = page_header.replace(f'<a href="{meta["nav"]}">', f'<a href="{meta["nav"]}" aria-current="page">', 1)
    extra = meta.get("extra_head", "")
    html_out = HEAD.format(
        title=meta["title"],
        description=meta["description"],
        canonical=SITE + meta["url"],
        og_type=meta.get("og_type", "website"),
        og_title=meta.get("og_title", meta["title"]),
        site=SITE,
        extra_head=extra + "\n" if extra else "",
        jsonld=jsonld,
    ) + page_header + "\n" + body.rstrip() + "\n\n" + footer + "</body>\n</html>\n"
    if meta.get("noindex"):
        html_out = html_out.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
        html_out = re.sub(r'  <link rel="canonical"[^>]*>\n', "", html_out)
    out = ROOT / meta["path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8", newline="\n")
    print("built", meta["path"])
