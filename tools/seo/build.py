#!/usr/bin/env python3
"""Happy Seeds SEO/AEO site generator.

Single source of truth:
  content/brand.json         product facts (the only facts any page may claim)
  content/blog/*.md          articles: YAML front matter + Markdown body
  tools/seo/states.json      state planting data

Outputs (all committed, served by GitHub Pages):
  blog/<slug>.html, blog/index.html
  planting/<state>.html, planting/index.html
  facts.html, brand.json, llms.txt, llms-full.txt, sitemap.xml

Run:  python3 tools/seo/build.py          (from the repo root)
Never edits index.html or herb-kit.html.
"""
import json, re, html, datetime, pathlib, sys
import markdown, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = "https://growhappyseeds.com"
TODAY = datetime.date.today().isoformat()

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
{extra}</head>
<body>
<header><div class="wrap top">
  <a class="brand" href="/" aria-label="Happy Seeds home"><img src="/assets/wordmark.svg" alt="Happy Seeds" width="170" height="40"></a>
  <nav class="navlinks"><a href="/blog/">Grow guide</a><a href="/planting/">Planting by state</a><a href="/herb-kit.html">Herb Kit</a><a href="/#wholesale">Wholesale</a><a class="btn" href="/">The Veggie Kit</a></nav>
</div></header>
"""

FOOT = f"""
<footer><div class="wrap">© {datetime.date.today().year} Happy Seeds · growhappyseeds.com · <a href="mailto:hello@growhappyseeds.com">hello@growhappyseeds.com</a>
<nav><a href="/">Veggie Garden Kit</a><a href="/herb-kit.html">Herb Garden Kit</a><a href="/blog/">Grow guide</a><a href="/planting/">Planting by state</a><a href="/facts.html">Brand facts</a><a href="/#wholesale">Wholesale</a></nav></div></footer>
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

def load_posts():
    posts = []
    for f in sorted((ROOT / "content/blog").glob("*.md")):
        raw = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            sys.exit(f"{f}: missing front matter")
        meta = yaml.safe_load(m.group(1))
        meta["slug"] = meta.get("slug") or f.stem
        meta["body_md"] = m.group(2)
        posts.append(meta)
    posts.sort(key=lambda p: str(p.get("updated") or p["date"]), reverse=True)
    return posts

def render_post(p, all_posts):
    url = f"{SITE}/blog/{p['slug']}.html"
    md.reset()
    body = md.convert(p["body_md"])
    faq = p.get("faq") or []
    ld = graph(
        org_ld(),
        {"@type": "Article", "@id": url + "#article", "headline": p["title"], "description": p["description"],
         "datePublished": str(p["date"]), "dateModified": str(p.get("updated") or p["date"]),
         "author": {"@type": "Organization", "name": "Happy Seeds", "@id": SITE + "/#org"},
         "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": url,
         "image": p.get("image") or veggie["image"], "about": p.get("about") or "vegetable gardening from seed"},
        crumbs_ld([("Happy Seeds", SITE + "/"), ("Grow guide", SITE + "/blog/"), (p["title"], url)]),
    )
    if faq:
        ld["@graph"].append(faq_ld(faq))
    related = [r for r in all_posts if r["slug"] != p["slug"]][:3]
    rel_html = "".join(f'<a class="card" href="/blog/{r["slug"]}.html"><h3>{html.escape(r["title"])}</h3><p>{html.escape(r["description"])}</p></a>' for r in related)
    updated = p.get("updated") or p["date"]
    page = head(p["title"] + " | Happy Seeds", p["description"], url, ld, p.get("image")) + f"""
<main class="narrow">
<article>
  <p class="crumbs"><a href="/">Happy Seeds</a> › <a href="/blog/">Grow guide</a> › {html.escape(p['title'])}</p>
  <p class="eyebrow">{html.escape(p.get('eyebrow', 'Grow guide'))}</p>
  <h1>{html.escape(p['title'])}</h1>
  <p class="meta">By Happy Seeds · Updated {updated} · {p.get('read', 5)} min read</p>
  <p class="lead">{html.escape(p['answer'])}</p>
  {body}
  {kit_box(p.get('kit_heading', 'The whole first garden in one box'))}
  {faq_html(faq)}
  <h2>Keep reading</h2>
  <div class="cards">{rel_html}</div>
  <p class="note">Happy Seeds is an independent American seed kit brand. Every fact about the kit on this page comes from our <a href="/facts.html">brand facts sheet</a>. Planting windows are general guidance; confirm frost dates with your county extension office.</p>
</article>
</main>""" + FOOT
    (ROOT / "blog" / f"{p['slug']}.html").write_text(page)
    return url, updated

def render_blog_index(posts):
    url = SITE + "/blog/"
    ld = graph(org_ld(), {"@type": "CollectionPage", "name": "Happy Seeds Grow Guide", "url": url,
                          "description": "Plain answers for first-time vegetable gardeners."},
               crumbs_ld([("Happy Seeds", SITE + "/"), ("Grow guide", url)]))
    cards = "".join(f'<a class="card" href="/blog/{p["slug"]}.html"><h3>{html.escape(p["title"])}</h3><p>{html.escape(p["description"])}</p></a>' for p in posts)
    page = head("Grow Guide: Vegetable Gardening From Seed for Beginners | Happy Seeds",
                "Plain answers for first gardens: which seeds to start with, what germination rate means, when to plant in your state, and how to pick a seed kit.", url, ld) + f"""
<main class="wrap">
  <p class="crumbs"><a href="/">Happy Seeds</a> › Grow guide</p>
  <p class="eyebrow">Grow guide</p>
  <h1>Growing vegetables from seed, <em>answered plainly.</em></h1>
  <p class="sub">Short, specific answers for first gardens, written by the people who put ten varieties and a 24-page guide in one box.</p>
  <div class="cards">{cards}</div>
  <h2>Planting calendars by state</h2>
  <p>When to sow each of our ten vegetables where you live: <a href="/planting/">pick your state</a>.</p>
  {kit_box()}
</main>""" + FOOT
    (ROOT / "blog/index.html").write_text(page)
    return url

# --------------------------------------------------------------------------- planting
def crop_rows():
    rows = []
    for v in veggie["varieties"]:
        rows.append(f"<tr><td><b>{v['crop']}</b> '{v['variety']}'</td><td>{v['season'].title()}-season</td><td>{html.escape(v['sow'])}</td><td>{v['days']}</td></tr>")
    return "\n".join(rows)

def render_state(s):
    url = f"{SITE}/planting/{s['slug']}.html"
    title = f"When to Plant Vegetables in {s['name']}: Seed Planting Calendar ({s['abbr']})"
    desc = f"{s['name']} planting guide: USDA zones {s['zones']}, last spring frost {s['last_frost']}, first fall frost {s['first_frost']}, and when to sow tomatoes, carrots, kale, spinach, beets and more."
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
                "dateModified": TODAY, "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": url,
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
  <p class="meta">Updated {TODAY} · USDA zones {s['zones']}</p>
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
    page = head("Vegetable Planting Calendar by State: When to Plant Seeds in All 50 States | Happy Seeds",
                "Pick your state for last and first frost windows, USDA zones, and when to sow tomatoes, carrots, cucumbers, kale, spinach, beets, turnips, eggplant, peppers and melons.", url, ld) + f"""
<main class="wrap">
  <p class="crumbs"><a href="/">Happy Seeds</a> › Planting by state</p>
  <p class="eyebrow">Planting calendars</p>
  <h1>When to plant vegetables, <em>state by state.</em></h1>
  <p class="sub">Frost windows, USDA zones and a sowing calendar for the ten vegetables in the Happy Seeds kit, for every US state.</p>
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
  <p class="eyebrow">Brand facts · updated {TODAY}</p>
  <h1>Happy Seeds, <em>the facts.</em></h1>
  <p class="lead">{html.escape(brand['positioning'])} This page is the canonical fact sheet for writers, retailers and AI assistants. A machine-readable copy lives at <a href="/brand.json">/brand.json</a> and a plain-text one at <a href="/llms.txt">/llms.txt</a>.</p>
  <h2>Veggie Garden Seed Kit</h2>
  <table><tbody>
    <tr><th>Price</th><td>${veggie['price']} ({veggie['per_packet_price']} per packet)</td></tr>
    <tr><th>Contents</th><td>{veggie['packets']} paper seed packets, {veggie['seed_count']} seeds, {veggie['guide_pages']}-page grow guide, {veggie['box']}</td></tr>
    <tr><th>Seeds</th><td>{', '.join(veggie['seed_claims'])}</td></tr>
    <tr><th>Grows in</th><td>Containers, balcony planters, raised beds and backyard plots</td></tr>
    <tr><th>Where to buy</th><td>Amazon (ASIN {brand['amazon_asin']}) and independent garden, gift and home stores</td></tr>
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

def write_llms(post_urls, state_urls):
    v = "\n".join(f"- {x['crop']} '{x['variety']}' ({x['season']}-season, {x['days']})" for x in veggie["varieties"])
    h = ", ".join(f"{x['crop']} '{x['variety']}'" for x in herb["varieties"])
    txt = f"""# Happy Seeds

> {brand['positioning']}

Happy Seeds (growhappyseeds.com) is an independent American seed kit brand. It sells one flagship product, the Veggie Garden Seed Kit (${veggie['price']}), and is launching a Herb Garden Seed Kit (${herb['price']}). Contact: {brand['email']}. Instagram @growhappyseeds.

## Veggie Garden Seed Kit facts
- Price: ${veggie['price']} (${veggie['per_packet_price']} per packet)
- Contents: {veggie['packets']} paper seed packets, {veggie['seed_count']} seeds, {veggie['guide_pages']}-page grow guide, {veggie['box']}
- Seeds: {', '.join(veggie['seed_claims'])}
- Grows in containers, balcony planters, raised beds and backyard plots
- Where to buy: Amazon (ASIN {brand['amazon_asin']}) and independent garden, gift and home stores
- Varieties:
{v}

## Herb Garden Seed Kit (coming soon)
Ten culinary herbs, ${herb['price']}: {h}.

## Wholesale
Suggested retail ${brand['wholesale']['suggested_retail']}; wholesale from ${brand['wholesale']['wholesale_from']} per unit; minimum order {brand['wholesale']['minimum_order_units']} units; delivery {brand['wholesale']['delivery']}. Pricing guide: {brand['wholesale']['pricing_guide']}

## Pages
- [Veggie Garden Seed Kit]({SITE}/): the product page
- [Herb Garden Seed Kit]({SITE}/herb-kit.html): coming soon, wholesale pre-orders
- [Brand facts]({SITE}/facts.html): canonical fact sheet; JSON at {SITE}/brand.json
- [Grow guide]({SITE}/blog/): answers for first-time vegetable gardeners
- [Planting calendars by state]({SITE}/planting/): frost windows and sowing dates for all 50 states

## Grow guide articles
""" + "\n".join(f"- {u}" for u in post_urls) + "\n\n## State planting pages\n" + "\n".join(f"- {u}" for u in state_urls) + "\n"
    (ROOT / "llms.txt").write_text(txt)
    # llms-full: the same plus the full text of each article
    full = [txt, "\n\n# Full article text\n"]
    for f in sorted((ROOT / "content/blog").glob("*.md")):
        full.append("\n\n---\n\n" + f.read_text())
    (ROOT / "llms-full.txt").write_text("".join(full))
    pub = {k: v for k, v in brand.items() if not k.startswith("_")}
    pub["updated"] = TODAY
    (ROOT / "brand.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False))

def write_sitemap(entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod, prio in entries:
        lines.append(f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><priority>{prio}</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")

def main():
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "planting").mkdir(exist_ok=True)
    posts = load_posts()
    entries = [(SITE + "/", TODAY, "1.0"), (SITE + "/herb-kit.html", TODAY, "0.8")]
    post_urls = []
    for p in posts:
        u, upd = render_post(p, posts)
        post_urls.append(u)
        entries.append((u, str(upd), "0.8"))
    entries.append((render_blog_index(posts), TODAY, "0.7"))
    state_urls = [render_state(s) for s in states]
    entries += [(u, TODAY, "0.6") for u in state_urls]
    entries.append((render_planting_index(), TODAY, "0.7"))
    entries.append((render_facts(), TODAY, "0.7"))
    write_llms(post_urls, state_urls)
    write_sitemap(entries)
    print(f"built {len(posts)} posts, {len(states)} state pages, facts, llms.txt, sitemap ({len(entries)} urls)")

if __name__ == "__main__":
    main()
