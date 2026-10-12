# Happy Seeds creative generator

Renders branded 1080x1350 Instagram carousels and statics as PNG (Packet Folk system: Sun #F6BE35, Cream #FFFBF2, Ketchup #D6362B, Leaf #2E6B34, Ink #26211A; headlines Old Standard TT Bold, labels Jost, body Source Serif 4; the real wordmark SVG).

- `lib.py`: brand tokens, the wordmark, and flat SVG illustration helpers (packet, box, tray, book, beet, carrot, kale, spinach, turnip, windowsill, pots, stamp, ribbon).
- `build.py`: the slide definitions and the Playwright/Chromium renderer. Edit the slide content lists in `build.py` (or import `lib` and write your own page specs), then run:

```
pip install playwright pillow --break-system-packages   # if missing
HS_OUT=/path/to/repo/media/2026-11 python3 build.py
```

Chromium: set `executablePath` to `/opt/pw-browsers/chromium` when running in the cloud workspace. Fonts are in `fonts/` (OFL). Keep every PNG under 1.5 MB and all text inside the 90 px safe area; look at each rendered PNG before committing it.
