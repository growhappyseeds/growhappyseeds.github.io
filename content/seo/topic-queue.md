# SEO article queue

The SEO Writer agent takes the first unchecked topic, writes it to `content/blog/<slug>.md`, runs `python3 tools/seo/build.py`, opens a pull request, and ticks the box in the same PR. Jared merges. Topics are ordered by how winnable they are for a two-page site; re-order freely. One topic per PR.

Rules for every article: the `answer` field is a two-sentence direct answer; every H2 opens with its answer; product facts only from `content/brand.json`; no competitor prices or specs; planting dates always say "confirm with your county extension office"; 900 to 1,400 words; 4 to 6 FAQ items; link to at least two existing pages.

## Ring 1: kit and buying intent
- [~] `housewarming-gift-for-a-gardener` Housewarming gifts for a new gardener (gift intent, pairs with the gift guide) (drafted 2026-11-02, parked in content/blog/_pending/ awaiting Jared's APPROVED reply)
- [~] `seed-kit-for-kids` The best seed kit for kids: what makes a vegetable kit work for a child (fast crops, big seeds, forgiving varieties) (drafted 2026-11-02, parked in content/blog/_pending/ awaiting Jared's APPROVED reply)
- [ ] `stocking-stuffers-for-gardeners` Stocking stuffers and small gifts for gardeners under $25 (seasonal, publish by mid-November)
- [x] `vegetable-garden-seed-kit-what-to-look-for` What to look for in a vegetable garden seed kit (7 checks: variety count, seed count per packet, germination printed, guide quality, non-GMO/open-pollinated, container-friendly, gift-ready)
- [ ] `how-many-seeds-are-in-a-seed-packet` How many seeds are in a seed packet? (by crop, with a table; why kits with 100 seeds per packet are enough for a home garden)
- [ ] `non-gmo-vs-heirloom-vs-organic-seeds` Non-GMO vs heirloom vs organic seeds: what the labels actually mean (and which matter for a home garden)
- [ ] `apartment-vegetable-garden-from-seed` How to grow vegetables from seed in an apartment (balcony, windowsill, light, containers, the kit's container notes)

## Ring 2: beginner questions
- [ ] `easiest-vegetables-to-grow-from-seed` The 10 easiest vegetables to grow from seed (ranked, with why)
- [ ] `do-seeds-expire` Do seeds expire? How long seeds last by crop and how to store them
- [ ] `how-deep-to-plant-seeds` How deep to plant vegetable seeds (the 2-to-3-times rule, table by crop)
- [ ] `why-are-my-seeds-not-germinating` Why your seeds are not germinating: 9 causes and fixes
- [ ] `direct-sow-vs-transplant` Direct sow vs transplant: which vegetables go straight in the ground
- [ ] `how-to-harden-off-seedlings` How to harden off seedlings in 7 days
- [ ] `how-much-sun-do-vegetables-need` How much sun vegetables need (full sun, part sun, what grows on a north-facing balcony)
- [ ] `how-to-grow-tomatoes-from-seed` How to grow tomatoes from seed (Floradade as the worked example)
- [ ] `how-to-grow-carrots-from-seed` How to grow carrots from seed (why they are slow to germinate, thinning)
- [ ] `how-to-grow-kale-from-seed` How to grow Red Russian kale from seed, spring and fall
- [ ] `how-to-grow-spinach-from-seed` How to grow spinach from seed without it bolting
- [ ] `how-to-grow-cucumbers-from-seed` How to grow cucumbers from seed on a trellis
- [ ] `how-to-grow-beets-from-seed` How to grow Chioggia beets from seed (one seed is a cluster)
- [ ] `how-to-grow-peppers-from-seed` How to grow Anaheim peppers from seed (heat and patience)
- [ ] `how-to-grow-eggplant-from-seed` How to grow Black Beauty eggplant from seed
- [ ] `how-to-grow-melons-from-seed` How to grow honeydew melons from seed in a home garden
- [ ] `how-to-grow-turnips-from-seed` How to grow Purple Top turnips from seed (fast fall crop)
- [ ] `fall-vegetable-garden-from-seed` Planting a fall vegetable garden from seed: the cool-season five
- [ ] `what-to-plant-in-november` What to plant in November by region (refresh monthly: one page per month, `what-to-plant-in-<month>`)
- [ ] `seed-starting-supplies-you-actually-need` Seed starting supplies you actually need (and the ones you don't)
- [ ] `raised-bed-vegetable-garden-from-seed` Planning a first raised-bed garden from seed (4x4 layout using the ten varieties)
- [ ] `companion-planting-for-beginners` Companion planting for the ten most common home vegetables (keep claims conservative)
- [ ] `how-to-save-seeds-from-open-pollinated-vegetables` How to save seeds from open-pollinated vegetables (why open-pollinated matters)

## Ring 3: place and time (beyond the 50 state pages)
- [ ] `when-to-plant-vegetables-by-usda-zone` When to plant vegetables by USDA zone (zones 3 to 10, one table)
- [ ] `last-frost-date-explained` What a last frost date is and how to find yours
- [ ] `vegetable-planting-calendar-northeast` Northeast vegetable planting calendar (NY, NJ, CT, MA, PA)
- [ ] `vegetable-planting-calendar-southeast` Southeast vegetable planting calendar (FL, GA, SC, NC)
- [ ] `vegetable-planting-calendar-texas-and-southwest` Texas and Southwest planting calendar
- [ ] `vegetable-planting-calendar-california` California planting calendar by region
- [ ] `vegetable-planting-calendar-midwest` Midwest planting calendar
- [ ] `vegetable-planting-calendar-pacific-northwest` Pacific Northwest planting calendar

## Ring 4: category and authority
- [ ] `how-to-choose-a-seed-company` How to choose a seed company: 8 questions to ask (germination testing, Safe Seed Pledge, packed-for dates, variety info, support)
- [ ] `seed-packet-anatomy` Anatomy of a seed packet: every line explained
- [ ] `history-of-seed-packets` A short history of the seed packet in America (link-worthy, pitch to garden writers)
- [ ] `germination-rates-by-vegetable` Typical germination rates by vegetable (table with ranges and the federal minimum standards, cite the eCFR)
