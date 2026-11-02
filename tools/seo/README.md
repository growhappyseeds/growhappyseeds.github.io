# Happy Seeds SEO / AEO system

Everything an agent (or a person) needs to grow growhappyseeds.com in Google and in AI answers, with nothing going live until Jared merges a pull request.

## Layout

| Path | What it is | Who edits it |
| --- | --- | --- |
| `content/brand.json` | The only source of product facts. Every page, llms.txt and brand.json are generated from it. | Jared, or an agent in a PR Jared approves |
| `content/blog/*.md` | Articles: YAML front matter + Markdown. Rendered through `tools/blog/_template.html` to `blog/<slug>/index.html`, so they look exactly like the seven hand-built posts, which stay as they are. | SEO Writer agent (PR) |
| `content/seo/topic-queue.md` | Backlog of article topics in priority order. | Anyone |
| `tools/seo/states.json` | State planting data (zones, frost windows, extension links). | Agent in a PR |
| `tools/seo/build.py` | Generates `blog/<slug>/index.html` for markdown posts, `blog/index.html` cards, `planting/`, `facts.html`, `brand.json`, `llms.txt`, `llms-full.txt`, `sitemap.xml`. Never touches `index.html` or `herb-kit.html`. | Run after any content change |
| `tools/seo/reports/` | Weekly AI-visibility and SERP reports (`aeo-YYYY-MM-DD.md`) and `aeo-log.json` (share of voice over time). | AI Visibility Monitor agent (commits to main; these are not site pages) |
| `tools/seo/queue/` | Ready-to-paste off-site drafts (Reddit answers, list-inclusion pitches, Pinterest descriptions) that Jared posts himself. | Mention Builder agent |
| `robots.txt` | Allows every major search and AI crawler; points at the sitemap. | Rarely |
| `assets/site.css`, `assets/wordmark.svg` | Shared chrome for generated pages. | Rarely |

## Build

```
python3 tools/seo/build.py
```

Needs `markdown` and `pyyaml` (`pip install markdown pyyaml --break-system-packages`). Commit the generated files together with the source change.

## Rules every agent follows

1. Nothing goes live without Jared: site changes travel as a pull request from a branch named `seo/<slug>`; Jared merges. Reports and off-site drafts under `tools/seo/` may be committed to `main` because GitHub Pages does not link to them.
2. Product facts only from `content/brand.json`. No invented numbers, reviews, awards or quotes. No competitor prices or specs.
3. Planting advice always tells the reader to confirm frost dates with their county extension office.
4. Answer first: the `answer` field and the first sentence of every H2 answer the question outright.
5. Never fake freshness: `updated` changes only when the content changed. The build takes every other page's lastmod from git, never from today's date, and never puts a future date anywhere.
6. One positioning phrase everywhere: "the complete first vegetable garden in one box: ten varieties, 1,000+ lab-tested non-GMO seeds, germination rate printed on every packet, a 24-page grow guide, $24.99."
7. Email Jared from his own Gmail connector (`mcp__Gmail__send_message`, to glassman.ja@gmail.com) with the PR link; never WhatsApp; never email anyone else.

## Article front matter

```
---
title: "..."          # 50-65 chars
slug: "..."
description: "..."    # 140-160 chars
date: 2026-10-31
updated: 2026-10-31
eyebrow: "..."
read: 6
answer: "..."         # two sentences, max 60 words; shown as "The short answer"
image: "media/2026-10/statics/inside.jpg"   # hero, 1080x1350, an approved claymation static from media/*/statics/
image_alt: "..."      # describe what is actually in the picture
image_caption: "..."  # optional, one line under the hero
subtitle: "..."       # optional, one sentence under the H1; defaults to description
kit_heading: "..."
about: "..."
faq:
  - q: "..."
    a: "..."
---
```

## Blog URLs

Every post lives at `/blog/<slug>/` (a folder with `index.html`), never `/blog/<slug>.html`. Link posts that way in Markdown: `[title](/blog/<slug>/)`. The seven posts written before this system (best-seed-gifts, best-vegetables-to-grow-on-a-balcony, fall-vegetables-to-plant-in-late-summer, gifts-for-new-gardeners, how-to-read-a-seed-packet, how-to-start-a-vegetable-garden-for-beginners, when-to-start-seeds-indoors) are hand-built HTML; do not write a `.md` with one of those slugs, and do not write an article on a topic one of them already covers.
