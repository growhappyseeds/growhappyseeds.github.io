# Blog tooling

Posts live at `/blog/<slug>/index.html` and share `/blog/blog.css`.

New posts are written as Markdown in `content/blog/<slug>.md` (front matter documented in `tools/seo/README.md`) and rendered
through `_template.html` by `python3 tools/seo/build.py`, which also rebuilds the cards on `/blog/index.html`, `/sitemap.xml`,
`/llms.txt` and `/llms-full.txt`. The seven original posts are hand-built from the same template and are left untouched by the build.
