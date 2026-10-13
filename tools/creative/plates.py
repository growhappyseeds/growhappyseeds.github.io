"""Transparent text plates for the claymation statics.

Each plate is a 1080x1350 PNG with a transparent background: a cream label
(headline in Jost 600, tomato red; sub-line in Jost 400, ink) in the top
third, and a small red price pill at the bottom. The plate is layered over a
Canva-generated claymation scene (insert_fill at 0,0 1080x1350), so the
typography stays exactly on brand no matter what Canva's text tools offer.

Usage:  python3 plates.py            # renders every plate in PLATES
        python3 plates.py gift city  # only these keys
Output: $HS_OUT (default media/2026-10/plates next to the repo root).
"""
import os, sys, json
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = HERE + '/fonts'
ROOT = os.path.abspath(HERE + '/../..')
OUT = os.environ.get('HS_OUT', ROOT + '/media/2026-10/plates')

KET = '#D6362B'; CREAM = '#FFFBF2'; INK = '#26211A'

PLATES = {
    # key: (headline, sub-line, pill, label position)
    'glowup': ("Seed packets just<br>got a glow up.",
               "Ten named varieties in a box that wraps like a book.",
               "$24.99 on Amazon", 'top'),
    'gift':   ("The gift that<br>turns into dinner.",
               "Ten seed packets. One keepsake box. Their first garden.",
               "$24.99 on Amazon", 'top'),
    'city':   ("No yard? Start here.",
               "Five of the ten packets grow on a sunny windowsill<br>or a balcony planter.",
               "$24.99 on Amazon", 'top'),
    'inside': ("What's actually<br>in the box.",
               "Ten packets, 1,000+ seeds, a 24-page guide, one keepsake box.",
               "$24.99 on Amazon", 'top'),
    'beet':   ("Beet 'Chioggia':<br>the candy-striped one.",
               "Cool-season, so it works on a windowsill or balcony.",
               "$24.99 on Amazon", 'top'),
    'winter': ("Your spring garden<br>starts on paper.",
               "Five packets for the windowsill now. Five that wait for spring.",
               "$24.99 on Amazon", 'top'),
}

CSS = f"""
@font-face{{font-family:'Jost';src:url('file://{FONTS}/Jost.ttf');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;background:transparent;overflow:hidden}}
body{{position:relative;font-family:'Jost',sans-serif}}
.label{{position:absolute;left:62px;top:58px;max-width:900px;background:{CREAM};
  border-radius:28px;padding:36px 46px 34px;transform:rotate(-1.6deg);transform-origin:left top;
  box-shadow:0 14px 34px rgba(38,33,26,.28),0 2px 0 rgba(38,33,26,.12)}}
.label.bottom{{top:auto;bottom:150px}}
h1{{font-weight:600;font-size:70px;line-height:1.04;letter-spacing:-.01em;color:{KET}}}
h1.long{{font-size:62px}}
p{{margin-top:14px;font-weight:400;font-size:30px;line-height:1.25;color:{INK}}}
.pill{{position:absolute;left:50%;bottom:66px;transform:translateX(-50%) rotate(1.5deg);
  background:{KET};color:{CREAM};font-weight:600;font-size:31px;letter-spacing:.02em;
  padding:16px 34px;border-radius:999px;white-space:nowrap;
  box-shadow:0 10px 24px rgba(38,33,26,.28)}}
"""


def html(head, sub, pill, pos):
    cls = 'long' if len(head.replace('<br>', ' ')) > 34 else ''
    lab = 'label bottom' if pos == 'bottom' else 'label'
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='{lab}'><h1 class='{cls}'>{head}</h1><p>{sub}</p></div>"
            f"<div class='pill'>{pill}</div></body></html>")


def render(keys):
    os.makedirs(OUT, exist_ok=True)
    made = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        for k in keys:
            head, sub, pill, pos = PLATES[k]
            work = os.environ.get('HS_WORK', '/tmp/hs-plates-html')
            os.makedirs(work, exist_ok=True)
            hp = f'{work}/{k}.html'
            open(hp, 'w').write(html(head, sub, pill, pos))
            pg.goto('file://' + hp)          # file:// origin so the @font-face files load
            pg.wait_for_timeout(300)
            path = f'{OUT}/{k}.png'
            pg.screenshot(path=path, omit_background=True, full_page=False)
            made.append(path)
        b.close()
    return made


if __name__ == '__main__':
    keys = sys.argv[1:] or list(PLATES)
    for m in render(keys):
        print(m)
