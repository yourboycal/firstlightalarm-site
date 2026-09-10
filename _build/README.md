# Site build

The home page, features page, support, privacy and terms are plain HTML, edited directly.

The product pages (`alarm-that-makes-you-*.html`, `no-snooze-alarm-app.html`, `alarmy-alternative.html`),
the Journal posts and `blog/index.html` are generated from the fragments in `content/`.
Each fragment is one JSON line of metadata followed by the article body.

    python3 _build/build.py      # rebuild generated pages, blog index, sitemap, JSON-LD on home/features
    python3 _build/og.py         # regenerate the Open Graph cards in img/og/ from og.json

To add a post: copy an existing `b*.html` fragment, change the metadata line (path, og, title,
description, h1, published, blurb, faqs, refs, related), add an entry to `og.json`, run both scripts.

Rules for copy: British English, no em dashes, cite the study and link to it, say where the evidence is thin.
