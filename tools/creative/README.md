# Creative tooling

Current direction (Jared, Oct 12 2026): **claymation product scenes generated in Canva, single images, no text on the image.**
The flat "Packet Folk" generator (build.py, lib.py) is retired and kept only for reference; do not render new creatives with it.

## How a static is made

1. Canva connector → `generate-image`, aspect `PORTRAIT_4_5`, imageReferences = box front `MAHX10pD-6o` + approved style `MAHX15_JAoM`
   (+ `MAHX2Ad226I` for open-box scenes, `MAHX2DIl7cc` for packet scenes). Props show pictures only — no readable words.
2. Reviewer checks the image at full size (box text right, no invented words, only the ten real varieties).
3. Place it full-bleed on its own page of the month's export design (October: `DAHX2L1rxg0`), commit, `export-design` that page as JPG q92.
4. Host it through the media bridge: push `media/_queue/<name>.json` = `{"items":[{"url":"<canva export url>","path":"media/YYYY-MM/statics/<slug>.jpg"}]}`.
   `.github/workflows/host-media.yml` downloads it on GitHub's runners and commits it (the sandbox cannot reach Canva's CDN; never curl it).
   Live about two minutes later at `https://growhappyseeds.com/media/YYYY-MM/statics/<slug>.jpg`.
5. Append the piece to `media/YYYY-MM/statics.json` and run `python3 tools/creative/review_page.py YYYY-MM` to rebuild the unlisted review page.

`plates.py` (transparent headline plates) is kept but unused: Jared asked for no text on the images.
