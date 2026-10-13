"""Build the unlisted review page for a month's claymation statics.

Reads media/YYYY-MM/statics.json (a manifest the Content Run appends to) and
writes media/YYYY-MM/review.html. The page is noindex and linked only from the
approval emails and the Approval Queue's Preview column.

Manifest shape (media/2026-10/statics.json):
  {"generated": "2026-10-12", "design": "DAHX2L1rxg0",
   "statics": [{"key": "glowup", "ct": "CT-20261012-04", "aq": "AQ-20261012-04",
                "angle": "glow_up", "hook": "...", "time": "2026-10-14 11:30",
                "caption": "...", "canva": "MAHX15_JAoM", "note": "reviewer note",
                "url": "https://growhappyseeds.com/media/2026-10/statics/glowup.jpg",
                "status": "Pending"}]}

Usage:  python3 review_page.py 2026-10
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(HERE + '/../..')

CSS = """body{font-family:Jost,-apple-system,Helvetica,Arial,sans-serif;background:#FFFBF2;color:#26211A;margin:0;padding:16px;max-width:860px;margin:0 auto}
h1{font-size:22px;margin:8px 0 4px}h2{font-size:18px;color:#D6362B;margin:28px 0 8px;border-bottom:2px solid #EFE4CC;padding-bottom:4px}
.card{background:#fff;border:1.5px solid #EFE4CC;border-radius:12px;padding:14px;margin:12px 0}
.id{font-size:12px;color:#6B6254;letter-spacing:.08em;text-transform:uppercase}.hook{font-weight:600;font-size:17px;margin:4px 0}
.meta{font-size:13px;color:#6B6254;margin-bottom:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.card img{width:100%;border-radius:8px;border:1px solid #EFE4CC;display:block}
.cap{font-size:14px;white-space:pre-wrap;margin:8px 0 0}.pill{display:inline-block;background:#FFF3D6;border:1.5px solid #F6BE35;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}
.note{font-size:13px;color:#6B6254;margin-top:8px}.sup{font-size:13px;color:#6B6254}
@media(max-width:600px){.grid{grid-template-columns:1fr}}"""


def build(month):
    d = f'{ROOT}/media/{month}'
    m = json.load(open(f'{d}/statics.json'))
    esc = html.escape
    live = [s for s in m['statics'] if s.get('status', 'Pending') not in ('Rejected', 'Superseded')]
    gone = [s for s in m['statics'] if s.get('status') in ('Rejected', 'Superseded')]
    out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>Happy Seeds: statics review, {month}</title><meta name='robots' content='noindex,nofollow'><style>{CSS}</style></head><body>",
           f"<h1>Happy Seeds: claymation statics, {month}</h1><p class='meta'>Single-image Instagram posts (1080x1350, no text on the image; the caption carries the copy). "
           f"Approve or reject each one in the Approval Queue tab of the Growth OS sheet, or reply to the approval email. Canva source: design {esc(m.get('design', ''))} in the Happy Seeds Canva account.</p>",
           f"<h2>For your approval ({len(live)})</h2><div class='grid'>"]
    for s in live:
        out.append(f"<div class='card' id='{s['ct']}'><div class='id'>{s['aq']} · {s['ct']} · instagram · static · {esc(s.get('status', 'Pending'))}</div>"
                   f"<div class='hook'>{esc(s['hook'])}</div><div class='meta'><span class='pill'>{esc(s['angle'])}</span><span class='pill'>{esc(s['time'])} ET</span></div>"
                   f"<a href='{s['url']}'><img src='{s['url']}' alt='{esc(s['hook'])} (claymation scene)'></a><div class='cap'>{esc(s['caption'])}</div>"
                   f"<div class='note'>Reviewer: {esc(s.get('note', ''))}</div></div>")
    out.append("</div>")
    if gone:
        out.append("<h2>Retired</h2><p class='sup'>" + '; '.join(f"{esc(s['aq'])} {esc(s['hook'])}" for s in gone) + ".</p>")
    out.append("<p class='sup'>Video scripts (Reels, TikTok, Shorts) live in the Content tab and need footage before there is anything to approve.</p></body></html>")
    open(f'{d}/review.html', 'w').write(''.join(out))
    return f'{d}/review.html'


if __name__ == '__main__':
    print(build(sys.argv[1] if len(sys.argv) > 1 else '2026-10'))
