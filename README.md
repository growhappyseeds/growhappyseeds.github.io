# growhappyseeds.com

GitHub Pages site for Happy Seeds. `main` is live.

## HAPPY SEEDS FINAL WEBSITE (restore point)
Jared, Nov 2 2026: the branch **`happy-seeds-final-website`** (commit 5d21ad6) is the exact live site as published at 11:48 ET on Nov 2 2026 (white background, Happy Farmer images, clay herb lineup, clean wholesale boxes). Nobody commits to that branch. To put it back live, exactly:

    git checkout main && git pull
    git checkout happy-seeds-final-website -- .
    git commit -m "Restore HAPPY SEEDS FINAL WEBSITE"
    git push origin main

That restores every file (pages, CSS, media) to the snapshot while keeping history. Agents: never delete or move this branch.

## Agents
See `tools/seo/README.md` for the SEO agents and `media/brand/clay/README.md` for the Happy Farmer brand rules.
