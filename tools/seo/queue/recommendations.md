# SEO recommendations queue

Written by the SEO Analyst (daily); the SEO Optimizer ticks a line when it acts on it in a `seo/optimize-<date>` pull request. One line per open recommendation: `- [ ] YYYY-MM-DD [type] <page or query>: <proposed change> (<numbers>)`. Do not add a line whose page and type are already here.

- [ ] 2026-11-02 [technical] tools/seo/data (Jared): add the GOOGLE_SA_JSON secret and run the "SEO data pull" workflow once; see tools/seo/README.md, Analytics data (latest.json pulled = null, seo-data.yml 0 runs)
- [ ] 2026-11-02 [internal link] index.html: add a "From the blog" block with three post cards (best-seed-gifts, gifts-for-new-gardeners, how-to-start-a-vegetable-garden-for-beginners); only best-seed-gifts is linked today (0 of 113 sessions in 28 days landed on a blog post)
- [ ] 2026-11-02 [internal link] blog/index.html: add "Planting by state" (/planting/) to the blog index nav, and a "When to plant in your state" link in the 7 posts that have none (/planting/ 2 landing sessions in 28 days, state pages 0)
- [ ] 2026-11-02 [technical] herb-kit.html: confirm the 2 herb_kit_wholesale generate_lead submissions of Oct 26-Nov 1 are real, then check why those sessions are Unassigned with 0 engagement (2 events, 2 Unassigned sessions)
- [ ] 2026-11-02 [technical] tools/seo/pull_data.py: also pull the landingPage dimension so fbclid variants roll up per page (16 of 26 landing rows are ?fbclid= variants)
- [ ] 2026-11-02 [new content] content/seo/topic-queue.md: move stocking-stuffers-for-gardeners to the top of Ring 1 so it publishes before mid-November (6 topics ahead of it; Writer runs Mon/Wed/Fri)
- [ ] 2026-11-02 [technical] sitemap.xml: decide whether herb-kit.html should be listed now that it is live (13 landing sessions and 2 key events in 28 days; not in the 65-URL sitemap)
