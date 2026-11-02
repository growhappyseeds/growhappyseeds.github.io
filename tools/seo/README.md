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

## Analytics data (Search Console + GA4)

`.github/workflows/seo-data.yml` runs every morning and `tools/seo/pull_data.py` writes:

- `tools/seo/data/gsc/YYYY-MM-DD.json`: Search Console, last 28 days by date, top queries and pages (7 and 28 days), page+query detail for the last 3 days, countries, devices.
- `tools/seo/data/ga4/YYYY-MM-DD.json`: GA4 property 558625133, sessions by date and channel, organic landing pages, key events, sources.
- `tools/seo/data/latest.json`: headline numbers and pointers to today's files.

Agents read these files instead of calling Google. If `latest.json` is older than two days, the workflow failed; the Analyst says so in its email rather than estimating.

One-time setup (Jared, about ten minutes):
1. In Google Cloud (console.cloud.google.com), pick or create a project, enable the **Google Search Console API** and the **Google Analytics Data API**.
2. IAM & Admin → Service Accounts → Create. Name it `seo-data`. No roles needed. Open it → Keys → Add key → JSON. Download the file.
3. Search Console → growhappyseeds.com → Settings → Users and permissions → Add user: the service account's email (ends in `.iam.gserviceaccount.com`), permission **Full**.
4. GA4 → Admin → Property access management → Add: the same email, role **Viewer**.
5. GitHub repo → Settings → Secrets and variables → Actions → New repository secret: name `GOOGLE_SA_JSON`, value = the whole contents of the downloaded JSON file.
6. Actions tab → "SEO data pull" → Run workflow. The first files appear in `tools/seo/data/` within a minute.

The empty GA4 property "Grow Happy Seeds" (558607627) has no data stream and no data; it can be deleted or ignored. The live property is "Happy Seeds" (558625133, tag G-Z51LD2VZH1).

## The agents (all scheduled Claude tasks; nothing goes live without Jared)

| Agent | When (ET) | Reads | Produces | Jared's approval |
| --- | --- | --- | --- | --- |
| SEO data pull (GitHub Action) | daily 05:20/06:20 | Search Console, GA4 | `tools/seo/data/*.json` on main | none needed (read-only data) |
| SEO Analyst | daily 07:10 | data files, yesterday's report | `tools/seo/reports/daily-*.md`, `tools/seo/queue/recommendations.md`, one short email | none needed (reports only) |
| SEO Writer | Mon/Wed/Fri 05:17 | topic queue, brand.json | one article as a `seo/<slug>` pull request | merge the PR |
| SEO Optimizer | Thu 06:33 | recommendations.md, data | one `seo/optimize-<date>` pull request of on-page fixes | merge the PR |
| Mention Builder | Tue 10:47 | latest AEO report, queue | `tools/seo/queue/<date>-offsite.md` + email of texts to paste | Jared posts them himself |
| AI Visibility Monitor | Mon 14:41 | 12 buyer prompts, site health | `tools/seo/reports/aeo-*.md`, `aeo-log.json`, one email | none needed |
| Content Run (social) | weekdays 06:54 | sitemap + llms.txt for live posts, Approval Queue | Instagram statics incl. one blog promo per live post, queued Pending | set the row to Approved |

Coordination is through the repo, not messages between agents: the sitemap says what is live, `recommendations.md` carries findings from the Analyst to the Optimizer, the Approval Queue column N (`BLOG:<slug>`) says which posts already have a social promo, and every report cites the data file it came from.
