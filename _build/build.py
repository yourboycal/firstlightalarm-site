"""Assemble First Light pages from content fragments.

Run from anywhere:  python3 _build/build.py

Each fragment in content/ starts with a JSON line of metadata, then the HTML body.
Product pages get the site nav, a page header, the long-form body, related links,
the sign-up block and the footer. Journal posts get the narrow reading layout.
Both get canonical/OG tags and JSON-LD. Also rebuilds blog/index.html and
sitemap.xml, and injects structured data into index.html and features.html.
"""
import json, os, re, glob, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)  # repo root
BASE = "https://firstlightalarm.com/"
TODAY = datetime.date.today().isoformat()
ORG_ID = BASE + "#org"

src_index = open(f"{SITE}/index.html", encoding="utf-8").read()
NAV = re.search(r"<nav>.*?</nav>", src_index, re.S).group(0)
FOOTER = re.search(r"<footer.*?</footer>", src_index, re.S).group(0)
FAVICON = re.search(r'<link rel="icon"[^>]*>', src_index).group(0)
NOTIFY = re.search(r'<section id="notify".*?</section>', src_index, re.S).group(0)

def nav_for(depth, current=None):
    n = NAV
    if depth:  # pages in /blog/
        n = n.replace('href="/"', 'href="../index.html"')
        n = re.sub(r'href="(?!https?:|mailto:|\.\./|/)', 'href="../', n)
    else:
        n = n.replace('href="#', 'href="index.html#')
    if current:
        n = n.replace(f'>{current}<', f' aria-current="page">{current}<')
    return n

def footer_for(depth):
    f = FOOTER
    if depth:
        f = re.sub(r'href="(?!https?:|mailto:|\.\./|/)', 'href="../', f)
    return f

def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"

ORG = {"@type": "Organization", "@id": ORG_ID, "name": "Calco Studios Ltd", "alternateName": "First Light",
       "url": BASE, "logo": BASE + "img/logo.png", "email": "hello@firstlightalarm.com",
       "address": {"@type": "PostalAddress", "addressCountry": "GB"}}
AUTHOR_ID = BASE + "#callum"
AUTHOR = {"@type": "Person", "@id": AUTHOR_ID, "name": "Callum Matthews", "jobTitle": "Founder",
          "worksFor": {"@id": ORG_ID}, "url": BASE + "blog/index.html",
          "description": "Founder of Calco Studios Ltd and maker of First Light, an iPhone alarm that won't stop until a morning mission is done."}
AUTHOR_BIO = """<div class="author">
    <div class="mono">CM</div>
    <div>
      <b>Callum Matthews</b>
      <p>Founder of Calco Studios and maker of <a href="../index.html">First Light</a>, an iPhone alarm that won't stop until a morning mission is done. He writes The Morning Journal from the research he had to read to build it. <a href="mailto:hello@firstlightalarm.com">Email him</a> if a study is misread; it will be corrected.</p>
    </div>
  </div>"""
WEBSITE = {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": "First Light", "publisher": {"@id": ORG_ID}}

def head(meta, depth, extra_ld):
    rel = "../" if depth else ""
    url = BASE + meta["path"]
    og_img = BASE + meta["og"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta["title"])}</title>
<meta name="description" content="{html.escape(meta["description"])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(meta.get("og_title", meta["h1"]))}">
<meta property="og:description" content="{html.escape(meta["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{"article" if meta["kind"] == "post" else "website"}">
<meta property="og:site_name" content="First Light">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{FAVICON}
<meta name="theme-color" content="#F8F6F1">
<link rel="stylesheet" href="{"style.css" if meta["kind"] == "post" else "site.css"}">
{extra_ld}
</head>
<body>
'''

def faq_ld(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def faq_html(faqs):
    return '<div class="faq">\n' + "\n".join(
        f"  <details>\n    <summary>{q}</summary>\n    <p>{a}</p>\n  </details>" for q, a in faqs) + "\n</div>"

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate(items)]}

def related_html(items, depth):
    rel = "../" if depth else ""
    lis = "\n".join(f'    <li><a href="{rel + p if not p.startswith("http") else p}">{n}</a>{(" <span>" + d + "</span>") if d else ""}</li>' for n, p, d in items)
    return f'<div class="related">\n  <h2>Read next</h2>\n  <ul>\n{lis}\n  </ul>\n</div>'

def hero_art(slug):
    f = f"{SITE}/blog/{slug}.html"
    if not os.path.exists(f): return ""
    m = re.search(r'<div class="hero-art">.*?</div>', open(f, encoding="utf-8").read(), re.S)
    return m.group(0) if m else ""

def load_fragments():
    out = []
    for f in sorted(glob.glob(f"{HERE}/content/*.html")):
        text = open(f, encoding="utf-8").read()
        first, body = text.split("\n", 1)
        meta = json.loads(first)
        meta["body"] = re.sub(r"\{\{HERO:([\w-]+)\}\}", lambda m: hero_art(m.group(1)), body.strip("\n"))
        out.append(meta)
    return out

def build_product(meta):
    faqs = meta.get("faqs", [])
    graph = [ORG, WEBSITE,
             {"@type": "WebPage", "@id": BASE + meta["path"], "url": BASE + meta["path"], "name": meta["h1"],
              "description": meta["description"], "isPartOf": {"@id": BASE + "#website"},
              "about": {"@type": "SoftwareApplication", "name": "First Light", "operatingSystem": "iOS 26",
                        "applicationCategory": "LifestyleApplication"},
              "dateModified": meta.get("modified", TODAY), "datePublished": meta.get("published", TODAY)},
             crumbs_ld([("First Light", ""), (meta["crumb"], meta["path"])])]
    if faqs: graph.append(faq_ld(faqs))
    doc = head(meta, 0, ld({"@context": "https://schema.org", "@graph": graph}))
    doc += nav_for(0) + "\n\n"
    doc += f'''<header class="page-head">
  <div class="wrap longform">
    <p class="crumbs"><a href="index.html">First Light</a> &rsaquo; {meta["crumb"]}</p>
    <div class="eyebrow">{meta["eyebrow"]}</div>
    <h1>{meta["h1"]}</h1>
    <p class="lede">{meta["lede"]}</p>
  </div>
</header>

<section class="tight">
  <div class="wrap longform">
{meta["body"]}
'''
    if faqs:
        doc += f'\n    <h2>Questions people ask</h2>\n{faq_html(faqs)}\n'
    if meta.get("related"):
        doc += "\n" + related_html(meta["related"], 0) + "\n"
    doc += "  </div>\n</section>\n\n" + NOTIFY + "\n\n" + footer_for(0) + "\n\n</body>\n</html>\n"
    open(f"{SITE}/{meta['path']}", "w", encoding="utf-8").write(doc)

def build_post(meta):
    faqs = meta.get("faqs", [])
    post_ld = {"@type": "BlogPosting", "@id": BASE + meta["path"], "mainEntityOfPage": BASE + meta["path"],
               "headline": meta["h1"], "description": meta["description"], "image": BASE + meta["og"],
               "datePublished": meta["published"], "dateModified": meta.get("modified", TODAY),
               "author": {"@id": AUTHOR_ID},
               "publisher": {"@id": ORG_ID}, "isPartOf": {"@type": "Blog", "@id": BASE + "blog/#blog", "name": "The Morning Journal"},
               "wordCount": len(re.sub(r"<[^>]+>", " ", meta["body"] + " " + " ".join(q + " " + a for q, a in faqs)).split()),
               "inLanguage": "en-GB"}
    graph = [ORG, AUTHOR, post_ld, crumbs_ld([("First Light", ""), ("The Morning Journal", "blog/index.html"), (meta["crumb"], meta["path"])])]
    if faqs: graph.append(faq_ld(faqs))
    doc = head(meta, 1, ld({"@context": "https://schema.org", "@graph": graph}))
    when = datetime.date.fromisoformat(meta["published"]).strftime("%-d %B %Y")
    upd = "" if meta.get("modified", TODAY) == meta["published"] else f' · Updated {datetime.date.fromisoformat(meta.get("modified", TODAY)).strftime("%-d %B %Y")}'
    words = post_ld["wordCount"]
    doc += f'''<div class="wrap">
  <a class="home" href="index.html">&larr; The Morning Journal</a>
  <h1>{meta["h1"]}</h1>
  <p class="meta">By <a href="index.html#author">Callum Matthews</a> · <time datetime="{meta["published"]}">{when}</time>{upd} · {max(3, round(words / 220))} min read</p>

{meta["body"]}
'''
    if faqs:
        doc += f'\n  <h2>Questions people ask</h2>\n{faq_html(faqs)}\n'
    if meta.get("refs"):
        doc += '\n  <div class="refs">\n    <h2>References</h2>\n    <ol>\n' + "\n".join(f"      <li>{r}</li>" for r in meta["refs"]) + "\n    </ol>\n  </div>\n"
    doc += "\n  " + AUTHOR_BIO + "\n"
    if meta.get("related"):
        doc += "\n" + related_html([(n, p.replace("blog/", "") if p.startswith("blog/") else "../" + p, d) for n, p, d in meta["related"]], 0) + "\n"
    doc += f'''
  <div class="cta-box">
    <b>{meta["cta_b"]}</b>
    <span>{meta["cta"]} <a href="../index.html">Meet First Light &rarr;</a></span>
  </div>
</div>
</body>
</html>
'''
    open(f"{SITE}/{meta['path']}", "w", encoding="utf-8").write(doc)

def build_blog_index(posts):
    posts = sorted(posts, key=lambda m: m["published"], reverse=True)
    items = "\n".join(f'''    <li>
      <a href="{m["path"].replace("blog/", "")}">{m["h1"]}</a>
      <p>{m["blurb"]}</p>
    </li>''' for m in posts)
    graph = [ORG, AUTHOR, {"@type": "Blog", "@id": BASE + "blog/#blog", "name": "The Morning Journal", "url": BASE + "blog/index.html",
                   "description": "Research-backed writing on habits, snoozing, sleep inertia and morning routines.",
                   "publisher": {"@id": ORG_ID}, "author": {"@id": AUTHOR_ID},
                   "blogPost": [{"@type": "BlogPosting", "@id": BASE + m["path"], "headline": m["h1"], "datePublished": m["published"], "url": BASE + m["path"]} for m in posts]},
             crumbs_ld([("First Light", ""), ("The Morning Journal", "blog/index.html")])]
    meta = {"path": "blog/index.html", "og": "img/og/journal.png", "kind": "post",
            "title": "The Morning Journal: habit science for better mornings | First Light",
            "description": "Research-backed writing on habits, snoozing, sleep inertia, exercise timing and morning routines from the team behind First Light, the no-snooze alarm.",
            "h1": "The Morning Journal", "og_title": "The Morning Journal: habit science for better mornings"}
    doc = head(meta, 1, ld({"@context": "https://schema.org", "@graph": graph})).replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
    doc += f'''<div class="wrap">
  <a class="home" href="../index.html">&larr; First Light</a>
  <h1>The Morning Journal</h1>
  <p class="meta">Habit science, honestly told. No 21-day myths.</p>
  <p class="intro">Most advice about mornings is either a motivational poster or a product pitch. This is neither. Every post here starts from published research on sleep, habit formation and behaviour change, names the study, links to it, and says plainly where the evidence is thin. We write it because we built <a href="../index.html">an alarm</a> around this research and had to read it properly first.</p>
  <p class="intro">Start with <a href="why-you-cant-stop-hitting-snooze.html">why you can't stop hitting snooze</a> if you want the problem, or <a href="how-to-wake-up-without-hitting-snooze.html">how to wake up without hitting snooze</a> if you want the fix.</p>

  <ul class="post-list">
    <li class="kicker">All posts, newest first</li>
{items}
  </ul>

  <div id="author">
  {AUTHOR_BIO.replace("../index.html", "../index.html")}
  </div>
</div>
</body>
</html>
'''
    open(f"{SITE}/blog/index.html", "w", encoding="utf-8").write(doc)

def inject_home(fragments):
    p = f"{SITE}/index.html"; s = open(p, encoding="utf-8").read()
    faqs = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", s, re.S)
    faqs = [(html.unescape(re.sub(r"<[^>]+>", "", q)), html.unescape(re.sub(r"<[^>]+>", "", a)).strip()) for q, a in faqs]
    app = {"@type": "SoftwareApplication", "@id": BASE + "#app", "name": "First Light", "operatingSystem": "iOS 26",
           "applicationCategory": "LifestyleApplication", "applicationSubCategory": "Alarm clock",
           "description": "An iPhone alarm that keeps coming back until you have finished a morning mission: push-ups, squats, a walk, meditation, journaling, reading or prayer. Movement is verified by the camera on the phone; nothing is recorded or uploaded.",
           "url": BASE, "image": BASE + "img/og.png", "screenshot": [BASE + f"img/store-0{i}.jpg" for i in range(1, 9)],
           "featureList": "No snooze; mission-based dismissal; camera-verified push-ups and squats; pedometer-counted morning steps; timed missions with photo proof; habit stacking; streaks, levels and progress charts; multiple alarms; rings through Silent mode and Focus; everything stored on the phone",
           "offers": [{"@type": "Offer", "name": "Yearly", "price": "39.99", "priceCurrency": "GBP", "category": "subscription", "description": "One week free, then £39.99 a year"},
                      {"@type": "Offer", "name": "Monthly", "price": "5.99", "priceCurrency": "GBP", "category": "subscription", "description": "One week free, then £5.99 a month"}],
           "publisher": {"@id": ORG_ID}, "author": {"@id": ORG_ID}, "isAccessibleForFree": False, "countryOfOrigin": "GB"}
    graph = [ORG, WEBSITE, app, faq_ld(faqs)]
    block = ld({"@context": "https://schema.org", "@graph": graph})
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, flags=re.S)
    s = s.replace('<link rel="stylesheet" href="site.css">', '<link rel="stylesheet" href="site.css">\n' + block)
    open(p, "w", encoding="utf-8").write(s)

def inject_features():
    p = f"{SITE}/features.html"; s = open(p, encoding="utf-8").read()
    graph = [ORG, WEBSITE, {"@type": "WebPage", "@id": BASE + "features.html", "url": BASE + "features.html",
             "name": "First Light features", "isPartOf": {"@id": BASE + "#website"}, "about": {"@id": BASE + "#app"}},
             crumbs_ld([("First Light", ""), ("Features", "features.html")])]
    block = ld({"@context": "https://schema.org", "@graph": graph})
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, flags=re.S)
    s = s.replace('<link rel="stylesheet" href="site.css">', '<link rel="stylesheet" href="site.css">\n' + block)
    if 'property="og:image"' not in s:
        s = s.replace('<meta name="twitter:card" content="summary_large_image">', f'<meta property="og:image" content="{BASE}img/og/features.png">\n<meta name="twitter:card" content="summary_large_image">')
    open(p, "w", encoding="utf-8").write(s)

def build_sitemap(fragments):
    def lastmod(path):
        out = os.popen(f'cd "{SITE}" && git log -1 --format=%as -- "{path}"').read().strip()
        return out or TODAY
    rows = [("", "1.0"), ("features.html", "0.9")]
    rows += [(m["path"], "0.8") for m in fragments if m["kind"] == "product"]
    rows += [("blog/index.html", "0.8")]
    rows += [(m["path"], "0.7") for m in sorted(fragments, key=lambda m: m["published"], reverse=True) if m["kind"] == "post"]
    rows += [("support.html", "0.5"), ("privacy.html", "0.3"), ("terms.html", "0.3")]
    changed = set(os.popen(f'cd "{SITE}" && git status --porcelain').read().split())
    def when(p):
        f = p or "index.html"
        return TODAY if f in changed or not os.path.exists(f"{SITE}/{f}") else lastmod(f)
    body = "\n".join(f'  <url><loc>{BASE}{p}</loc><lastmod>{when(p)}</lastmod><priority>{pr}</priority></url>' for p, pr in rows)
    open(f"{SITE}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")

if __name__ == "__main__":
    frags = load_fragments()
    for m in frags:
        (build_product if m["kind"] == "product" else build_post)(m); print("built", m["path"])
    build_blog_index([m for m in frags if m["kind"] == "post"])
    inject_home(frags); inject_features(); build_sitemap(frags)
    print("blog index, home/features JSON-LD, sitemap done")
