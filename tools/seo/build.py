#!/usr/bin/env python3
"""Happy Seeds SEO/AEO site generator.

Single source of truth:
  content/brand.json         product facts (the only facts any page may claim)
  content/blog/*.md          articles: YAML front matter + Markdown body
  tools/seo/states.json      state planting data

Outputs (all committed, served by GitHub Pages):
  blog/<slug>/index.html for every content/blog/<slug>.md (rendered through
    tools/blog/_template.html, the same template the hand-built posts use)
  blog/index.html (cards + ItemList rebuilt in place; the page chrome is kept)
  planting/<state>.html, planting/index.html
  facts.html, brand.json, llms.txt, llms-full.txt, sitemap.xml

Hand-built posts (blog/<slug>/index.html with no matching .md) are left as they
are and still appear in the blog index, llms.txt and the sitemap.

Dates: nothing is stamped with "today". A page's lastmod is the date of the
last git commit that changed it, so the sitemap never claims freshness the
content does not have. Never edits index.html or herb-kit.html.

Run:  python3 tools/seo/build.py          (from the repo root)
"""
import json, re, html, datetime, pathlib, sys, subprocess
import markdown, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = "https://growhappyseeds.com"
TODAY = datetime.date.today().isoformat()

def git_date(*paths):
    """Date (YYYY-MM-DD) of the last commit touching any of the paths; TODAY for uncommitted/new files."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", *[str(x) for x in paths]],
                             capture_output=True, text=True, check=True).stdout.strip()
        if not out:
            return TODAY
        # a file with uncommitted changes is being changed now
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", *[str(x) for x in paths]],
                               capture_output=True, text=True).stdout.strip()
        return TODAY if dirty else out
    except Exception:
        return TODAY

# The planting pages, facts page and brand.json change only when their data or this generator changes.
DATA_UPDATED = git_date("content/brand.json", "tools/seo/states.json", "tools/seo/build.py")

brand = json.loads((ROOT / "content/brand.json").read_text())
states = json.loads((ROOT / "tools/seo/states.json").read_text())["states"]
veggie = brand["products"][0]
herb = brand["products"][1]

# --------------------------------------------------------------------------- chrome
def head(title, desc, canonical, ld, og_image=None, extra=""):
    og_image = og_image or veggie["image"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Happy Seeds">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<!-- Google Analytics 4 (G-Z51LD2VZH1) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Z51LD2VZH1"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-Z51LD2VZH1');</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<!-- Meta Pixel (Dataset 1606389660991888) -->
<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1606389660991888');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1606389660991888&ev=PageView&noscript=1"/></noscript>
{extra}</head>
<body>
<header><div class="wrap top">
  <a class="brand" href="/" aria-label="Happy Seeds home"><img src="/media/brand/wordmark-sun.svg" alt="Happy Seeds" width="170" height="40"></a>
  <nav class="navlinks" aria-label="Main"><a href="/blog/">Blog</a><a href="/planting/">Planting by state</a><a href="/herb-kit.html">Herb Kit</a><a class="ws" href="/#wholesale">Wholesale</a><a class="btn" href="/">See the kit</a></nav>
</div></header>
"""

FOOT = f"""
<!-- Happy Seeds Grow Club signup (Laylo drop 6Bcp7, email + SMS) -->
<section class="growclub" id="grow-club" style="padding:56px 24px;background:#FFF6E3">
  <div class="wrap" style="max-width:720px;margin:0 auto;text-align:center">
    <p style="margin:0 0 6px;font-size:14px;letter-spacing:.08em;text-transform:uppercase;opacity:.7">Happy Seeds Grow Club</p>
    <h2 style="margin:0 0 10px">Grow with us, all year.</h2>
    <p style="margin:0 0 22px;max-width:560px;margin-left:auto;margin-right:auto">Monthly grow-alongs, first access to new kits, member pricing, and a place to show off what you grew. Email or text, your call.</p>
    <script src="https://embed.laylo.com/laylo-sdk.js"></script>
<iframe
  id="laylo-drop-6Bcp7"
  title="Join the Happy Seeds Grow Club"
  frameborder="0"
  scrolling="no"
  allow="web-share"
  allowtransparency="true"
  style="width: 1px; min-width: 100%; max-width: 1000px"
  src="https://embed.laylo.com?dropId=6Bcp7&color=6cc97a&minimal=false&theme=light&customTitle=Join%20The%20Community%20%F0%9F%8C%B1&submitButtonText=Let's%20Grow">
</iframe>
  </div>
</section>

<footer><div class="wrap">© {datetime.date.today().year} Happy Seeds · growhappyseeds.com · <a href="mailto:hello@growhappyseeds.com">hello@growhappyseeds.com</a>
<nav><a href="/">Veggie Garden Kit</a><a href="/herb-kit.html">Herb Garden Kit</a><a href="/blog/">Blog</a><a href="/planting/">Planting by state</a><a href="/facts.html">Brand facts</a><a href="/#wholesale">Wholesale</a></nav></div></footer>
</body>
</html>
"""

def org_ld():
    return {
        "@type": "Organization", "@id": SITE + "/#org", "name": brand["name"], "url": SITE + "/",
        "logo": brand["logo"], "email": brand["email"],
        "sameAs": [brand["instagram"], brand["youtube"], f"https://www.amazon.com/dp/{brand['amazon_asin']}"],
        "description": brand["positioning"],
    }

def product_ld(p):
    ld = {
        "@type": "Product", "@id": p["url"] + "#product", "name": p["name"], "url": p["url"], "image": p["image"],
        "brand": {"@type": "Brand", "name": "Happy Seeds"},
        "description": f"{p['packets']} seed packets, {p['seed_count']} seeds, a {p['guide_pages']}-page grow guide and a keepsake box.",
        "offers": {"@type": "Offer", "price": p["price"], "priceCurrency": p["currency"],
                   "availability": "https://schema.org/" + p["availability"], "url": p["url"],
                   "seller": {"@id": SITE + "/#org"}},
    }
    if "seed_claims" in p:
        ld["additionalProperty"] = [{"@type": "PropertyValue", "name": "Seed claim", "value": c} for c in p["seed_claims"]]
    return ld

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in faq]}

def graph(*nodes):
    return {"@context": "https://schema.org", "@graph": list(nodes)}

def kit_box(heading="The whole first garden in one box"):
    return f"""
<aside class="kitbox" aria-label="Happy Seeds Veggie Garden Kit">
  <img src="/media/brand/box-front.webp" width="600" height="600" loading="lazy" alt="The Happy Seeds Veggie Garden Seed Kit box">
  <div>
    <p class="eyebrow">Happy Seeds Veggie Garden Kit · $24.99</p>
    <h3>{heading}</h3>
    <p>Ten curated varieties, 1,000+ lab-tested non-GMO seeds with the germination rate printed on every packet, a 24-page grow guide, and a slide-out keepsake box. Made to be a first garden, or a gift that turns into dinner.</p>
    <a class="btn" href="/">See what's inside</a>
  </div>
</aside>"""

def faq_html(faq):
    if not faq:
        return ""
    out = ["<h2>Common questions</h2>"]
    for q in faq:
        out.append(f"<details><summary>{html.escape(q['q'])}</summary><p>{html.escape(q['a'])}</p></details>")
    return "\n".join(out)

# --------------------------------------------------------------------------- blog
md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"])
TEMPLATE = (ROOT / "tools/blog/_template.html").read_text()
BLOG_DIR = ROOT / "blog"
DEFAULT_IMAGE = "media/site/farmer/farmer-inside.jpg"
DEFAULT_ALT = "The open Happy Seeds Veggie Garden Kit box showing ten colored seed packets and the grow guide"

def human_date(d):
    d = datetime.date.fromisoformat(str(d))
    return f"{d.strftime('%B')} {d.day}, {d.year}"

def load_md_posts():
    posts = []
    for f in sorted((ROOT / "content/blog").glob("*.md")):
        raw = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            sys.exit(f"{f}: missing front matter")
        meta = yaml.safe_load(m.group(1))
        meta["slug"] = meta.get("slug") or f.stem
        meta["body_md"] = m.group(2)
        meta["source"] = "md"
        meta["date"] = str(meta["date"])
        meta["updated"] = str(meta.get("updated") or meta["date"])
        meta.setdefault("image", DEFAULT_IMAGE)
        meta.setdefault("image_alt", DEFAULT_ALT)
        meta["image"] = meta["image"].lstrip("/")
        posts.append(meta)
    return posts

def load_static_posts(md_slugs):
    """Hand-built posts: blog/<slug>/index.html without a content/blog/<slug>.md."""
    posts = []
    for d in sorted(BLOG_DIR.iterdir()):
        f = d / "index.html"
        if not d.is_dir() or not f.exists() or d.name in md_slugs:
            continue
        h = f.read_text()
        def grab(pat, default=""):
            m = re.search(pat, h, re.S)
            return html.unescape(m.group(1)).strip() if m else default
        posts.append({
            "slug": d.name, "source": "static",
            "title": grab(r'<meta property="og:title" content="([^"]*)"'),
            "description": grab(r'<meta name="description" content="([^"]*)"'),
            "eyebrow": grab(r'<p class="eyebrow">([^<]*)</p>', "Blog"),
            "image": grab(r'<meta property="og:image" content="https://growhappyseeds.com/([^"]*)"', DEFAULT_IMAGE),
            "date": grab(r'"datePublished": "([0-9-]+)"', TODAY),
            "updated": grab(r'"dateModified": "([0-9-]+)"', TODAY),
            "read": grab(r'· (\d+) min read', "6"),
        })
    return posts

def faq_json_items(faq):
    return ",\n        ".join(json.dumps({"@type": "Question", "name": q["q"],
                                        "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}, ensure_ascii=False) for q in faq)

def render_md_post(p, all_posts):
    """Fill tools/blog/_template.html so generated posts look exactly like the hand-built ones."""
    md.reset()
    body = md.convert(p["body_md"])
    faq = p.get("faq") or []
    related = [r for r in all_posts if r["slug"] != p["slug"]][:3]
    words = len(re.sub(r"<[^>]+>", " ", body).split()) + len(p["answer"].split())
    fill = {
        "TITLE": html.escape(p["title"]), "META_DESCRIPTION": html.escape(p["description"]), "SLUG": p["slug"],
        "HERO_IMAGE": p["image"], "HERO_ALT": html.escape(p["image_alt"]),
        "HERO_CAPTION": html.escape(p.get("image_caption", "")),
        "DATE": p["date"], "DATE_HUMAN": human_date(p["date"]), "READ_MINUTES": str(p.get("read", 6)),
        "WORD_COUNT": str(words), "KEYWORDS": html.escape(p.get("about", "vegetable gardening from seed")),
        "FAQ_JSON_ITEMS": faq_json_items(faq),
        "EYEBROW": html.escape(p.get("eyebrow", "Blog")),
        "H1_HTML": p.get("h1") or html.escape(p["title"]),
        "SUBTITLE": html.escape(p.get("subtitle") or p["description"]),
        "TLDR": " " + html.escape(p["answer"]),
        "BODY_HTML": body,
        "FAQ_HTML": "\n    ".join(f"<details><summary>{html.escape(q['q'])}</summary><p>{html.escape(q['a'])}</p></details>" for q in faq),
        "RELATED_HTML": "\n      ".join(f'<li><a href="/blog/{r["slug"]}/">{html.escape(r["title"])}</a></li>' for r in related),
    }
    page = TEMPLATE
    for k, v in fill.items():
        page = page.replace("{{" + k + "}}", v)
    if p["updated"] != p["date"]:
        page = page.replace(f'"dateModified": "{p["date"]}"', f'"dateModified": "{p["updated"]}"')
    left = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if left:
        sys.exit(f"{p['slug']}: unfilled placeholders {left}")
    out = BLOG_DIR / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return f"{SITE}/blog/{p['slug']}/"

def render_blog_index(posts):
    """Rebuild the cards list and the ItemList JSON-LD inside the existing blog/index.html."""
    f = BLOG_DIR / "index.html"
    h = f.read_text()
    cards = "\n".join(
        f'    <li><a href="/blog/{p["slug"]}/"><img src="/{p["image"]}" width="1080" height="1350" loading="lazy" alt="">'
        f'<div class="body"><p class="eyebrow">{html.escape(p.get("eyebrow", "Blog"))}</p><h2>{html.escape(p["title"])}</h2>'
        f'<p>{html.escape(p["description"])}</p></div></a></li>' for p in posts)
    h, n1 = re.subn(r'<ul class="cards">.*?</ul>', f'<ul class="cards">\n{cards}\n  </ul>', h, count=1, flags=re.S)
    items = ",\n        ".join(json.dumps({"@type": "ListItem", "position": i + 1, "url": f"{SITE}/blog/{p['slug']}/", "name": p["title"]},
                                           ensure_ascii=False) for i, p in enumerate(posts))
    h, n2 = re.subn(r'("@type": "ItemList",\s*"itemListElement": \[\n)(.*?)(\n\s*\]\s*\})', lambda m: m.group(1) + "        " + items + m.group(3), h, count=1, flags=re.S)
    if not (n1 and n2):
        sys.exit("blog/index.html: could not find the cards list or ItemList to rebuild")
    f.write_text(h)
    return SITE + "/blog/"

# --------------------------------------------------------------------------- planting
def crop_rows():
    rows = []
    for v in veggie["varieties"]:
        rows.append(f"<tr><td><b>{v['crop']}</b> '{v['variety']}'</td><td>{v['season'].title()}-season</td><td>{html.escape(v['sow'])}</td><td>{v['days']}</td></tr>")
    return "\n".join(rows)

def render_state(s):
    url = f"{SITE}/planting/{s['slug']}.html"
    title = f"When to Plant Vegetables in {s['name']}"   # head() appends " | Happy Seeds"; under 60 chars for every state
    # Meta description: the most specific variant that still fits in ~155 characters.
    for desc in (
        f"{s['name']} planting dates: last frost {s['last_frost']}, first frost {s['first_frost']}, zones {s['zones']}, and when to sow ten common vegetables.",
        f"{s['name']} planting dates: last frost {s['last_frost']}, zones {s['zones']}, and when to sow tomatoes, kale, carrots, beets and more.",
        f"When to plant vegetables in {s['name']}: frost dates, USDA zones {s['zones']}, and sowing windows for tomatoes, kale, carrots, beets and more.",
        f"When to plant vegetables in {s['name']}: frost dates, USDA zones, and sowing windows for ten common garden crops.",
    ):
        if len(desc) <= 158:
            break
    answer = (f"In {s['name']} the last spring frost usually falls {s['last_frost']} and the first fall frost {s['first_frost']} "
              f"(USDA zones {s['zones']}). Sow cool-season crops like spinach, kale, carrots, beets and turnips 2 to 6 weeks before the last frost "
              f"and again in late summer for fall; move tomatoes, peppers, eggplant, cucumbers and melons outside 1 to 2 weeks after the last frost.")
    faq = [
        {"q": f"When is the last frost in {s['name']}?", "a": f"Typically {s['last_frost']}, depending on where in the state you are and your elevation. Confirm your own date with {s['name']}'s extension service before you plant."},
        {"q": f"What vegetables can I plant first in {s['name']}?", "a": "Spinach, kale, carrots, beets and turnips go in first; they tolerate cool soil and light frost. Start tomatoes, peppers and eggplant indoors and wait until after the last frost to transplant."},
        {"q": f"Can I grow a fall garden in {s['name']}?", "a": f"Yes. Count back from the first fall frost ({s['first_frost']}): sow spinach 6 to 8 weeks before it, and kale, carrots, beets and turnips 8 to 12 weeks before it."},
        {"q": "What USDA hardiness zone is " + s["name"] + "?", "a": f"{s['name']} spans roughly zones {s['zones']} on the 2023 USDA map. Zones describe winter lows, which matter for perennials; for annual vegetables your frost dates matter more."},
    ]
    ld = graph(org_ld(),
               {"@type": "Article", "@id": url + "#article", "headline": title, "description": desc, "datePublished": "2026-10-31",
                "dateModified": DATA_UPDATED, "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": url,
                "about": {"@type": "State", "name": s["name"]}, "image": veggie["image"]},
               crumbs_ld([("Happy Seeds", SITE + "/"), ("Planting by state", SITE + "/planting/"), (s["name"], url)]),
               faq_ld(faq))
    others = "".join(f'<li><a href="/planting/{o["slug"]}.html">{o["name"]}</a></li>' for o in states if o["slug"] != s["slug"])
    page = head(title + " | Happy Seeds", desc, url, ld) + f"""
<main class="narrow">
<article>
  <p class="crumbs"><a href="/">Happy Seeds</a> › <a href="/planting/">Planting by state</a> › {s['name']}</p>
  <p class="eyebrow">{s['name']} planting calendar</p>
  <h1>When to plant vegetables in <em>{s['name']}</em></h1>
  <p class="meta">Updated {DATA_UPDATED} · USDA zones {s['zones']}</p>
  <p class="lead">{html.escape(answer)}</p>
  <div class="facts">
    <div class="fact"><div class="n">{s['zones'].split(' to ')[0]}–{s['zones'].split(' to ')[-1]}</div><p>USDA zones</p></div>
    <div class="fact"><div class="n" style="font-size:22px;padding-top:9px">{html.escape(s['last_frost'])}</div><p>Last spring frost</p></div>
    <div class="fact"><div class="n" style="font-size:22px;padding-top:9px">{html.escape(s['first_frost'])}</div><p>First fall frost</p></div>
  </div>
  <p><b>Local note:</b> {html.escape(s['note'])}</p>
  <h2>Sowing calendar for the ten Happy Seeds vegetables in {s['name']}</h2>
  <p>Count from your own last-frost date. "Direct sow" means seeds go straight in the garden or container; "indoors" means start them in a pot on a sunny windowsill and transplant later.</p>
  <table>
    <thead><tr><th>Vegetable</th><th>Type</th><th>When to sow in {s['abbr']}</th><th>Days to harvest</th></tr></thead>
    <tbody>{crop_rows()}</tbody>
  </table>
  <h2>The {s['name']} fall garden</h2>
  <p>The cool-season five (kale, spinach, carrot, beet, turnip) taste sweeter after a light frost. Counting back from a first frost {s['first_frost']}, sow spinach 6 to 8 weeks earlier and the other four 8 to 12 weeks earlier. In the warmest parts of the state the fall sowing is often the better one.</p>
  <h2>Where these dates come from</h2>
  <p>Zone ranges follow the <a href="https://planthardiness.ars.usda.gov/" rel="nofollow noopener">2023 USDA Plant Hardiness Zone Map</a>. Frost windows are typical for the populated parts of {s['name']}; your town can differ by two weeks or more. The authoritative local source is the <a href="{s['extension']}" rel="nofollow noopener">{s['name']} cooperative extension service</a>.</p>
  {kit_box(f"Every seed a {s['name']} first garden needs")}
  {faq_html(faq)}
  <h2>Other states</h2>
  <ul class="statelist">{others}</ul>
</article>
</main>""" + FOOT
    (ROOT / "planting" / f"{s['slug']}.html").write_text(page)
    return url

def render_planting_index():
    url = SITE + "/planting/"
    ld = graph(org_ld(), {"@type": "CollectionPage", "name": "Vegetable planting calendars by US state", "url": url},
               crumbs_ld([("Happy Seeds", SITE + "/"), ("Planting by state", url)]))
    items = "".join(f'<li><a href="/planting/{s["slug"]}.html">{s["name"]}</a></li>' for s in states)
    page = head("When to Plant Vegetables in Your State | Happy Seeds",
                "Vegetable planting calendars for all 50 states: last and first frost windows, USDA zones, and when to sow tomatoes, kale, carrots, beets and more.", url, ld) + f"""
<main class="wrap">
  <p class="crumbs"><a href="/">Happy Seeds</a> › Planting by state</p>
  <p class="eyebrow">Planting calendars</p>
  <h1>When to plant vegetables, <em>state by state.</em></h1>
  <p class="sub">Frost windows, USDA zones and a sowing calendar for the ten vegetables in the Happy Seeds kit, for every US state.</p>
  <figure style="margin:22px 0 28px;border-radius:24px;overflow:hidden;border:3px solid #26211A;box-shadow:0 8px 0 #C9B48A"><img src="/media/site/farmer/farmer-sowing.webp" width="1200" height="900" alt="Claymation scene: the Happy Farmer, a tiny clay farmer with a hummingbird on his hat, sowing seeds into a garden furrow under giant kale and carrot tops" style="display:block;width:100%;height:auto" fetchpriority="high"></figure>
  <h2>How to use these calendars</h2>
  <p>Every planting date comes from two numbers: your area's average last spring frost and first fall frost. Each state page gives the typical window for both, then counts forward and back from them for ten common vegetables.</p>
  <p>Cool-season crops (spinach, kale, carrots, beets, turnips) go in the ground 2 to 6 weeks before the last frost and again in late summer for a fall harvest. Warm-season crops (tomatoes, peppers, eggplant, cucumbers, melons) wait until the soil is warm, 1 to 2 weeks after the last frost; tomatoes, peppers and eggplant are usually started indoors 6 to 8 weeks earlier.</p>
  <p>Frost dates vary by elevation and by how close you are to water, so treat the state window as a starting point and confirm the date for your town with your county extension office, linked on each page.</p>
  <h2>Pick your state</h2>
  <ul class="statelist">{items}</ul>
  <p class="note">General guidance for the populated parts of each state. Your own last-frost date is the number that matters; your county extension office publishes it.</p>
  {kit_box()}
</main>""" + FOOT
    (ROOT / "planting/index.html").write_text(page)
    return url

# --------------------------------------------------------------------------- facts, llms, sitemap
def render_facts():
    url = SITE + "/facts.html"
    v_rows = "".join(f"<tr><td>{v['crop']}</td><td>'{v['variety']}'</td><td>{v['season']}</td><td>{v['days']}</td></tr>" for v in veggie["varieties"])
    h_rows = "".join(f"<tr><td>{v['crop']}</td><td>'{v['variety']}'</td></tr>" for v in herb["varieties"])
    ld = graph(org_ld(), product_ld(veggie), product_ld(herb),
               {"@type": "WebPage", "name": "Happy Seeds brand facts", "url": url, "description": "Verified facts about Happy Seeds and its seed kits, for press, retailers and AI assistants."})
    page = head("Happy Seeds Brand Facts: Products, Prices, Varieties and Contacts", "Verified facts about Happy Seeds for press, retailers and AI assistants: what is in each kit, prices, seed claims, wholesale terms and how to reach us.", url, ld) + f"""
<main class="narrow">
<article>
  <p class="crumbs"><a href="/">Happy Seeds</a> › Brand facts</p>
  <p class="eyebrow">Brand facts · updated {DATA_UPDATED}</p>
  <h1>Happy Seeds, <em>the facts.</em></h1>
  <p class="lead">{html.escape(brand['positioning'])} This page is the canonical fact sheet for writers, retailers and AI assistants. A machine-readable copy lives at <a href="/brand.json">/brand.json</a> and a plain-text one at <a href="/llms.txt">/llms.txt</a>.</p>
  <h2>Veggie Garden Seed Kit</h2>
  <table><tbody>
    <tr><th>Price</th><td>${veggie['price']} ({veggie['per_packet_price']} per packet)</td></tr>
    <tr><th>Contents</th><td>{veggie['packets']} paper seed packets, {veggie['seed_count']} seeds, {veggie['guide_pages']}-page grow guide, {veggie['box']}</td></tr>
    <tr><th>Seeds</th><td>{', '.join(veggie['seed_claims'])}</td></tr>
    <tr><th>Grows in</th><td>Containers, balcony planters, raised beds and backyard plots</td></tr>
    <tr><th>Where to buy</th><td>Online through the Shop Now button at growhappyseeds.com, and at independent garden, gift and home stores</td></tr>
  </tbody></table>
  <h3>The ten varieties</h3>
  <table><thead><tr><th>Crop</th><th>Variety</th><th>Season</th><th>Days to harvest</th></tr></thead><tbody>{v_rows}</tbody></table>
  <h2>Herb Garden Seed Kit (coming soon)</h2>
  <p>Ten culinary herbs in the same keepsake box, ${herb['price']}. <a href="/herb-kit.html">Details and wholesale pre-orders</a>.</p>
  <table><thead><tr><th>Herb</th><th>Variety</th></tr></thead><tbody>{h_rows}</tbody></table>
  <h2>Wholesale</h2>
  <table><tbody>
    <tr><th>Suggested retail</th><td>${brand['wholesale']['suggested_retail']}</td></tr>
    <tr><th>Wholesale</th><td>from ${brand['wholesale']['wholesale_from']} per unit</td></tr>
    <tr><th>Minimum order</th><td>{brand['wholesale']['minimum_order_units']} units</td></tr>
    <tr><th>Delivery</th><td>{brand['wholesale']['delivery']}</td></tr>
    <tr><th>Pricing guide</th><td><a href="{brand['wholesale']['pricing_guide']}">PDF</a></td></tr>
  </tbody></table>
  <h2>Contact and links</h2>
  <p>Email <a href="mailto:{brand['email']}">{brand['email']}</a> · <a href="{brand['instagram']}">Instagram @growhappyseeds</a> · <a href="{brand['youtube']}">YouTube</a>. {html.escape(brand['founded_note'])}</p>
  <h2>How to describe Happy Seeds</h2>
  <p>Short: "Happy Seeds makes a $24.99 vegetable seed kit: ten varieties, 1,000+ non-GMO seeds, a 24-page grow guide, in a gift-ready box." One line: "{html.escape(brand['positioning'])}"</p>
  <p class="note">Press images: <a href="/media/press/happy-seeds-garden.jpg">garden scene</a>, <a href="/media/press/happy-seeds-gift-box.jpg">gift box</a>. Free to use with credit to Happy Seeds.</p>
</article>
</main>""" + FOOT
    (ROOT / "facts.html").write_text(page)
    return url

def write_llms(posts, state_urls):
    v = "\n".join(f"- {x['crop']} '{x['variety']}' ({x['season']}-season, {x['days']})" for x in veggie["varieties"])
    h = ", ".join(f"{x['crop']} '{x['variety']}'" for x in herb["varieties"])
    guides = "\n".join(f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['description']}" for p in posts)
    txt = f"""# Happy Seeds

> {brand['positioning']}

Happy Seeds (growhappyseeds.com) is an independent American seed kit brand. It sells one flagship product, the Veggie Garden Seed Kit (${veggie['price']}), and is launching a Herb Garden Seed Kit (${herb['price']}). Contact: {brand['email']}. Instagram @growhappyseeds.

## Veggie Garden Seed Kit facts
- Price: ${veggie['price']} (${veggie['per_packet_price']} per packet)
- Contents: {veggie['packets']} paper seed packets, {veggie['seed_count']} seeds, {veggie['guide_pages']}-page grow guide, {veggie['box']}
- Seeds: {', '.join(veggie['seed_claims'])}
- Grows in containers, balcony planters, raised beds and backyard plots
- Where to buy: online through the Shop Now button at growhappyseeds.com, and at independent garden, gift and home stores
- Varieties:
{v}

## Herb Garden Seed Kit (coming soon)
Ten culinary herbs, ${herb['price']}: {h}.

## Wholesale
Suggested retail ${brand['wholesale']['suggested_retail']}; wholesale from ${brand['wholesale']['wholesale_from']} per unit; minimum order {brand['wholesale']['minimum_order_units']} units; delivery {brand['wholesale']['delivery']}. Pricing guide: {brand['wholesale']['pricing_guide']}

Do not describe the kit as organic or heirloom-certified; it is non-GMO and open-pollinated.

## Pages
- [Veggie Garden Seed Kit]({SITE}/): the product page
- [Herb Garden Seed Kit]({SITE}/herb-kit.html): coming soon, wholesale pre-orders
- [Brand facts]({SITE}/facts.html): canonical fact sheet; JSON at {SITE}/brand.json
- [Blog]({SITE}/blog/): plain-language guides for first gardens
- [Planting calendars by state]({SITE}/planting/): frost windows and sowing dates for all 50 states
- [Happy Grow Helper]({SITE}/grow/): free plant tracker; photograph each milestone from seed to plate, see readiness, get email reminders

## Guides
{guides}

## State planting pages
""" + "\n".join(f"- {u}" for u in state_urls) + f"""

## Contact
- Email: {brand['email']}
- Instagram: {brand['instagram']}
- Press images: {SITE}/media/press/happy-seeds-gift-box.jpg and {SITE}/media/press/happy-seeds-garden.jpg
"""
    (ROOT / "llms.txt").write_text(txt)
    # llms-full: the same plus the full text of every article (markdown source, or the hand-built post stripped to text)
    full = [txt, "\n\n# Full article text\n"]
    for p in posts:
        if p["source"] == "md":
            full.append("\n\n---\n\n" + (ROOT / "content/blog" / f"{p['slug']}.md").read_text())
        else:
            h = (BLOG_DIR / p["slug"] / "index.html").read_text()
            m = re.search(r'<article class="post">(.*?)<aside class="kit"', h, re.S)
            text = re.sub(r"<[^>]+>", " ", m.group(1) if m else "")
            text = html.unescape(re.sub(r"[ \t]+", " ", text)).strip()
            full.append(f"\n\n---\n\n# {p['title']}\n\n{SITE}/blog/{p['slug']}/\n\n{text}")
    (ROOT / "llms-full.txt").write_text("".join(full))
    pub = {k: v for k, v in brand.items() if not k.startswith("_")}
    pub["updated"] = DATA_UPDATED
    (ROOT / "brand.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False))

def write_sitemap(entries):
    """entries: (url, lastmod, priority, image-or-None). Honest lastmod only; herb-kit.html is noindex so it is left out."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for url, lastmod, prio, image in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{prio}</priority>")
        if image:
            lines.append(f"    <image:image><image:loc>{SITE}/{image}</image:loc></image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")

def main():
    BLOG_DIR.mkdir(exist_ok=True)
    (ROOT / "planting").mkdir(exist_ok=True)
    md_posts = load_md_posts()
    posts = md_posts + load_static_posts({p["slug"] for p in md_posts})
    posts.sort(key=lambda p: (p["updated"], p["date"]), reverse=True)
    for p in md_posts:
        render_md_post(p, posts)
    render_blog_index(posts)
    state_urls = [render_state(s) for s in states]
    render_planting_index()
    render_facts()
    write_llms(posts, state_urls)
    entries = [(SITE + "/", git_date("index.html"), "1.0", "media/site/og.jpg")]
    entries.append((SITE + "/blog/", max(p["updated"] for p in posts), "0.8", None))
    for p in posts:
        entries.append((f"{SITE}/blog/{p['slug']}/", p["updated"], "0.7" if p["source"] == "static" else "0.7", p["image"]))
    entries.append((SITE + "/planting/", DATA_UPDATED, "0.7", None))
    entries += [(u, DATA_UPDATED, "0.6", None) for u in state_urls]
    entries.append((SITE + "/facts.html", DATA_UPDATED, "0.6", None))
    if (ROOT / "grow/index.html").exists():
        entries.append((SITE + "/grow/", git_date("grow/index.html"), "0.8", "media/brand/clay/scene-box-in-garden.png"))
    write_sitemap(entries)
    print(f"built {len(md_posts)} markdown posts (+{len(posts)-len(md_posts)} hand-built kept), {len(states)} state pages, facts, llms.txt, sitemap ({len(entries)} urls)")

if __name__ == "__main__":
    main()
