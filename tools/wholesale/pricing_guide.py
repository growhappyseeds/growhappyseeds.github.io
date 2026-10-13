"""Happy Seeds wholesale pricing guide (two pages, US Letter).

Rebuilds the layout of Happy_Seeds_Wholesale_Pricing_Guide.pdf (the Veggie
Garden Kit guide) for any kit. Only the HERB kit content is defined here; the
veggie PDF predates this script and is left as-is.

Usage:  python3 tools/wholesale/pricing_guide.py herb
Output: Happy_Seeds_Herb_Wholesale_Pricing_Guide.pdf at the repo root.
"""
import os, sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader, simpleSplit

HERE = os.path.dirname(os.path.abspath(__file__))
A = HERE + '/assets/'
ROOT = os.path.abspath(HERE + '/../..')
pdfmetrics.registerFont(TTFont('Lilita', A + 'LilitaOne.ttf'))

SUN = HexColor('#F6CC46'); RED = HexColor('#BF3629'); INK = HexColor('#26211A')
MUTED = HexColor('#6B6254'); CREAM = HexColor('#FFF6DB'); LINE = HexColor('#E7D6A6')
BLUE = HexColor('#5CC8EA'); CHIP = HexColor('#E9A93A')
W, H = letter
L, R = 36, W - 36

# Pricing is identical to the veggie kit guide (Jared, Oct 13 2026: "add pricing same as veggie kit").
TIERS = [('10 to 19 units', '$12.50', '50%', '$12.49', '$124.90'),
         ('20 to 49 units', '$11.75', '53%', '$13.24', '$132.40'),
         ('50+ units', '$11.00', '56%', '$13.99', '$139.90')]

KITS = {
    'herb': dict(
        out='Happy_Seeds_Herb_Wholesale_Pricing_Guide.pdf',
        name='Herb Garden Kit',
        season='Coming soon  ·  Stockist terms',
        tagline='Herbs that fit on a shelf.',
        panel_title=['10 CURATED', 'HERB SEED VARIETIES'],
        panel_note='Includes 10 paper seed packets, 1,000+ seeds, and 1 grow guide booklet.',
        body=('Ten culinary herb varieties, 1,000+ seeds lab tested for purity and germination, '
              'and a 24-page grow guide, all in a slide-out keepsake box. Perfect to grow year '
              'round, and easy apartment growing on a sunny windowsill.'),
        body2=('No spinner rack, no wall of packets. A $24.99 ticket in the footprint of a paperback, '
               'on a gift wall, a counter, or an endcap.'),
        chips=['Non-GMO', 'Lab tested', 'All natural'],
        spec=['MSRP $24.99', '6.3 x 3.7 x 2.4 in  ·  Case of 10'],
        why=['Ten units display in under one square foot: two stacks of five, face out. No rack.',
             '$249.90 in revenue per case at full price.',
             'Herbs grow year round on a windowsill, so the kit sells in every season, not just spring.',
             'Opening-order guarantee: unsold units returnable within 60 days.'],
        terms=[('Minimum', '10 units, case pack of 10'),
               ('Payment', 'Opening order prepaid (card or ACH); Net 30 on reorders'),
               ('Delivery', 'Coming soon: reserve your opening order now. Free in NYC; ships nationwide at cost')],
        detail_sub='Herb Garden Kit  ·  what your customers get',
        varieties=['Sweet Basil Genovese', 'Oregano Greek', 'Sage Broadleaf', 'Rosemary Common',
                   'Chives Common', 'Parsley Italian Large Leaf', 'Cilantro Santo', 'Spearmint Curly',
                   'Thyme English (Winter)', 'Dill Bouquet'],
        detail_p1=('1,000+ seeds in total, lab tested for purity and germination. 24-page grow guide with '
                   'the story and step-by-step growing instructions for every variety. Slide-out keepsake '
                   'box with foam insert, 6.3 x 3.7 x 2.4 inches.'),
        detail_p2=('Herbs suit apartment gardeners: a sunny windowsill is enough, '
                   'and they grow year round.'),
        img_box=A + 'herb_box.png', img_guide=A + 'herb_growguide.jpg', img_trust=A + 'herb_trust.jpg',
        cap_box="What's included: box, drawer, 10 packets, 24-page grow guide",
        cap_guide='The grow guide: history and growing instructions for every variety',
        cap_trust='Lab tested for purity and germination. Non-GMO, all natural.',
    ),
}


def T(y):  # top-based y to ReportLab y
    return H - y


def para(c, text, x, y, w, font='Helvetica', size=8.5, lead=11.5, color=INK):
    c.setFont(font, size); c.setFillColor(color)
    for line in simpleSplit(text, font, size, w):
        c.drawString(x, T(y), line); y += lead
    return y


def frame(c, k, title, sub, page):
    c.setFillColor(SUN); c.rect(0, T(72), W, 72, stroke=0, fill=1)
    c.drawImage(ImageReader(A + 'wordmark.png'), L, T(60), width=190, height=190 * 578 / 2487, mask='auto')
    c.setFillColor(RED); c.setFont('Lilita', 14); c.drawRightString(R, T(36), title)
    c.setFont('Helvetica-Bold', 8); c.drawRightString(R, T(52), sub)
    c.setFillColor(SUN); c.rect(0, 0, W, 50, stroke=0, fill=1)
    c.setFillColor(RED); c.setFont('Helvetica-Bold', 8)
    c.drawCentredString(W / 2, 22, 'Orders and questions:  hello@growhappyseeds.com   ·   growhappyseeds.com   ·   @growhappyseeds')
    c.setFillColor(MUTED); c.setFont('Helvetica', 7); c.drawRightString(R, 66, f'Page {page} of 2')


def fit_image(c, path, x, ytop, w, h):
    img = ImageReader(path); iw, ih = img.getSize(); s = min(w / iw, h / ih)
    dw, dh = iw * s, ih * s
    c.drawImage(img, x + (w - dw) / 2, T(ytop + (h - dh) / 2 + dh), width=dw, height=dh, mask='auto')


def blue_panel(c, x, ytop, w, h):
    c.setFillColor(BLUE); c.roundRect(x, T(ytop + h), w, h, 12, stroke=0, fill=1)


def page1(c, k):
    frame(c, k, 'WHOLESALE PRICING GUIDE', k['season'], 1)
    # left art panel
    px, py, pw, ph = L, 96, 300, 276
    blue_panel(c, px, py, pw, ph)
    c.setFillColor(white); c.setFont('Lilita', 18)
    c.drawString(px + 14, T(py + 26), k['panel_title'][0]); c.drawString(px + 14, T(py + 46), k['panel_title'][1])
    fit_image(c, k['img_box'], px + 10, py + 56, pw - 20, 176)
    para(c, k['panel_note'], px + 14, py + 250, pw - 28, 'Helvetica-Bold', 7.5, 10, white)
    # right column
    x, w = 356, R - 356
    c.setFillColor(RED); c.setFont('Lilita', 21); c.drawString(x, T(116), k['name'])
    c.setFont('Lilita', 12.5); c.drawString(x, T(138), k['tagline'])
    y = para(c, k['body'], x, 158, w)
    y = para(c, k['body2'], x, y + 6, w, color=MUTED)
    cx, y = x, y + 8
    c.setFont('Helvetica-Bold', 7.5)
    for chip in k['chips']:
        cw = c.stringWidth(chip, 'Helvetica-Bold', 7.5) + 18
        if cx + cw > R: cx, y = x, y + 20
        c.setFillColor(CREAM); c.setStrokeColor(CHIP); c.setLineWidth(1)
        c.roundRect(cx, T(y + 14), cw, 15, 7.5, stroke=1, fill=1)
        c.setFillColor(RED); c.drawCentredString(cx + cw / 2, T(y + 10), chip); cx += cw + 6
    y += 30
    for s in k['spec']:
        c.setFillColor(MUTED); c.setFont('Helvetica', 7.5); c.drawString(x, T(y), s); y += 11
    # pricing table
    c.setFillColor(RED); c.setFont('Lilita', 14); c.drawString(L, T(404), 'Wholesale pricing')
    c.setFont('Helvetica-Bold', 8); c.drawRightString(R, T(402), 'Minimum order 10 units (one case)')
    cols = [L + 10, 200, 302, 390, 482]
    ty = 412
    c.setFillColor(RED); c.rect(L, T(ty + 20), R - L, 20, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 8)
    for cxx, hd in zip(cols, ['Order size', 'Unit price', 'Your margin', 'Profit per unit', 'Profit per case (10)']):
        c.drawString(cxx, T(ty + 13.5), hd)
    ty += 20
    for i, row in enumerate(TIERS):
        c.setFillColor(CREAM if i % 2 else white); c.rect(L, T(ty + 20), R - L, 20, stroke=0, fill=1)
        for j, (cxx, v) in enumerate(zip(cols, row)):
            c.setFillColor(INK); c.setFont('Helvetica-Bold' if j == 1 else 'Helvetica', 8.5)
            c.drawString(cxx, T(ty + 13.5), v)
        ty += 20
    c.setStrokeColor(LINE); c.setLineWidth(.8); c.rect(L, T(ty), R - L, ty - 412, stroke=1, fill=0)
    para(c, 'Margin shown on a $24.99 retail. MSRP is held everywhere, including Amazon and growhappyseeds.com, '
            'so your shelf is never undercut.', L, ty + 12, R - L, size=7, lead=9, color=MUTED)
    # why + terms boxes
    by, bh = 548, 152
    c.setFillColor(CREAM); c.roundRect(L, T(by + bh), 262, bh, 10, stroke=0, fill=1)
    c.setFillColor(RED); c.setFont('Lilita', 12.5); c.drawString(L + 14, T(by + 22), 'Why it works on your shelf')
    y = by + 40
    for item in k['why']:
        c.setFillColor(RED); c.setFont('Helvetica-Bold', 8); c.drawString(L + 14, T(y), '•')
        y = para(c, item, L + 26, y, 222, size=8, lead=10.5) + 5
    tx = 314
    c.setFillColor(white); c.setStrokeColor(LINE); c.setLineWidth(.8)
    c.roundRect(tx, T(by + bh), R - tx, bh, 10, stroke=1, fill=1)
    c.setFillColor(RED); c.setFont('Lilita', 12.5); c.drawString(tx + 14, T(by + 22), 'Terms')
    y = by + 42
    for label, val in k['terms']:
        c.setFillColor(RED); c.setFont('Helvetica-Bold', 8.5); c.drawString(tx + 14, T(y), label)
        y = para(c, val, tx + 76, y, R - tx - 90, size=8.5, lead=11) + 7


def page2(c, k):
    frame(c, k, 'PRODUCT DETAIL', k['detail_sub'], 2)
    gw, gh = 262, 236
    # top-left: what's included
    blue_panel(c, L, 96, gw, gh)
    c.setFillColor(white); c.setFont('Lilita', 15); c.drawCentredString(L + gw / 2, T(118), "WHAT'S INCLUDED")
    fit_image(c, k['img_box'], L + 12, 126, gw - 24, gh - 40)
    para(c, k['cap_box'], L, 96 + gh + 14, gw, size=7.5, lead=9.5, color=MUTED)
    # top-right: grow guide
    rx = R - gw
    fit_image(c, k['img_guide'], rx, 96, gw, gh)
    para(c, k['cap_guide'], rx, 96 + gh + 14, gw, size=7.5, lead=9.5, color=MUTED)
    # bottom-left: trust panel
    fit_image(c, k['img_trust'], L, 366, gw, gh)
    para(c, k['cap_trust'], L, 366 + gh + 14, gw, size=7.5, lead=9.5, color=MUTED)
    # bottom-right: in every kit
    c.setFillColor(RED); c.setFont('Lilita', 14); c.drawString(rx, T(384), 'In every kit')
    y = 402
    for v in k['varieties']:
        c.setFillColor(RED); c.setFont('Helvetica-Bold', 8.5); c.drawString(rx + 2, T(y), '•')
        c.setFillColor(INK); c.setFont('Helvetica', 9); c.drawString(rx + 14, T(y), v); y += 13.5
    y = para(c, k['detail_p1'], rx, y + 8, gw, size=8.5, lead=11.5)
    para(c, k['detail_p2'], rx, y + 6, gw, size=8.5, lead=11.5)


def build(key):
    k = KITS[key]
    out = f"{ROOT}/{k['out']}"
    c = canvas.Canvas(out, pagesize=letter)
    c.setTitle(f"Happy Seeds {k['name']} Wholesale Pricing Guide"); c.setAuthor('Happy Seeds')
    page1(c, k); c.showPage(); page2(c, k); c.showPage(); c.save()
    return out


if __name__ == '__main__':
    print(build(sys.argv[1] if len(sys.argv) > 1 else 'herb'))
