import sys, os, json, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from playwright.sync_api import sync_playwright
from PIL import Image

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
OUT = os.environ.get('HS_OUT', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'media', 'preview'))
WORK = os.environ.get('HS_WORK', '/tmp/hs-creative-html')
os.makedirs(OUT, exist_ok=True); os.makedirs(WORK, exist_ok=True)

CSS = f'''
@font-face{{font-family:'OST';src:url('file://{FONTS}/OldStandard-Bold.ttf');font-weight:700}}
@font-face{{font-family:'Jost';src:url('file://{FONTS}/Jost.ttf');font-weight:100 900}}
@font-face{{font-family:'SS4';src:url('file://{FONTS}/SourceSerif4.ttf');font-weight:200 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
.page{{position:relative;width:1080px;height:1350px;overflow:hidden}}
.rule{{position:absolute;left:40px;top:40px;width:1000px;height:1270px;border:3px solid {INK}}}
.rule2{{position:absolute;left:50px;top:50px;width:980px;height:1250px;border:1.5px solid {INK}}}
.col{{position:absolute;left:90px;top:90px;width:900px;height:1170px}}
.top{{position:absolute;left:0;top:0;width:900px;display:flex;justify-content:center}}
.stack{{position:absolute;left:0;width:900px;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.h1{{font-family:'OST';font-weight:700;font-size:76px;line-height:1.1;text-align:center;text-wrap:balance;color:{INK};hyphens:none;width:900px}}
.cover .h1{{font-size:100px;line-height:1.06}}
.sub{{font-family:'Jost';font-weight:500;font-size:40px;line-height:1.35;text-align:center;color:{INK};text-wrap:balance;width:900px}}
.lab{{font-family:'Jost';font-weight:600;font-size:32px;letter-spacing:0.16em;text-transform:uppercase;text-align:center}}
.num{{position:absolute;right:0;bottom:0;font-family:'Jost';font-weight:500;font-size:32px;line-height:1.3;color:{INK}}}
.panel{{display:flex;align-items:center;justify-content:center;border:3.5px solid {INK};border-radius:22px}}
.list{{display:grid;grid-template-columns:max-content max-content;justify-content:space-between;row-gap:14px;font-family:'Jost';font-weight:500;font-size:34px;line-height:1.3;color:{INK};width:900px}}
.list div{{white-space:nowrap;display:flex;align-items:center;gap:14px}}
.list i{{display:inline-block;width:12px;height:12px;border-radius:50%;background:{LEAF};flex:none}}
.serif{{font-family:'SS4';font-weight:500;font-variation-settings:'opsz' 40;font-size:40px;line-height:1.4;text-align:center;color:{INK}}}
svg{{display:block}}
'''


def page(bg, body, cls='', rule_color=INK, double=True):
    r2 = f'<div class="rule2" style="border-color:{rule_color}"></div>' if double else ''
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="page {cls}" style="background:{bg}"><div class="rule" style="border-color:{rule_color}"></div>{r2}'
            f'<div class="col">{body}</div></div></body></html>')


def top_wm(w=230, color=KET):
    return f'<div class="top">{wordmark_svg(w, color, cls="a")}</div>'


def num(i, n, color=INK):
    return f'<div class="num t" style="color:{color}">{i}/{n}</div>'


def stack(parts, top, height, gap=40):
    return f'<div class="stack" style="top:{top}px;height:{height}px;gap:{gap}px">{"".join(parts)}</div>'


def h1(text, size=None, color=INK, width=900, raw=False):
    st = f'color:{color};width:{width}px;' + (f'font-size:{size}px;' if size else '') + ('text-wrap:initial;' if raw else '')
    return f'<div class="h1 t" style="{st}">{text if raw else H.escape(text)}</div>'


def sub(text, color=INK, size=40, width=900):
    return f'<div class="sub t" style="color:{color};font-size:{size}px;width:{width}px">{H.escape(text)}</div>'


def sub_nb(text, color=INK, size=40, width=900):
    """Supporting line where only the ' · ' separators may wrap."""
    parts = [H.escape(p).replace(' ', '&nbsp;') for p in text.split(' · ')]
    return f'<div class="sub t" style="color:{color};font-size:{size}px;width:{width}px">{" · ".join(parts)}</div>'


def sub_lines(lines, color=INK, size=40, width=900):
    return (f'<div class="sub t" style="color:{color};font-size:{size}px;width:{width}px;text-wrap:initial">'
            + '<br>'.join(H.escape(l) for l in lines) + '</div>')


def panel(content_svg, w, h, bg=CREAM, border=INK, radius=22):
    return f'<div class="panel a" style="width:{w}px;height:{h}px;background:{bg};border-color:{border};border-radius:{radius}px">{content_svg}</div>'


def art(content, w, h):
    return svg(content, w, h, cls='a')


# ------------------------------------------------------------------ carousel 1 (Sun)
C1_LIST = ["Tomato 'Floradade'", "Carrot 'Danvers 126'", "Cucumber 'Marketmore 76'", "Kale 'Red Russian'",
           "Spinach 'Bloomsdale'", "Beet 'Chioggia'", "Turnip 'Purple Top'", "Eggplant 'Black Beauty'",
           "Pepper 'Anaheim Chili'", "Melon 'Honeydew Orange'"]


def c1(i):
    N = 5
    if i == 1:
        # gift box with ribbon and bow, veg around it, in a cream panel
        a = g(box_flat(ribbon=True, W=440, D=300, H=70), 60, 330, 0.98)
        a += g(carrot(), 80, 196, 0.78, rot=-30)
        a += g(beet_whole(), 668, 300, 0.86)
        a += g(kale_leaf(), 618, 230, 0.56, rot=24)
        body = top_wm(300) + stack([h1('The gift that turns into dinner.', 100), panel(art(a, 760, 440), 800, 480),
                                   sub('Happy Seeds Veggie Garden Kit')], 120, 1000, 44) + num(1, N)
        return page(SUN, body, 'cover')
    if i == 2:
        # ten packets, two rows, each a different window colour rhythm; then the two-column list
        a = ''
        kinds = ['sprig', 'carrot', 'sprig', 'kale', 'spinach', 'beet', 'turnip', 'sprig', 'sprig', 'sprig']
        for k in range(10):
            r, c = divmod(k, 5)
            x = 26 + c*(118+30); y = 20 + r*(160+26)
            a += g(packet(icon=packet_icon(kinds[k]), w=118, h=160, window=(SUN if (k % 2 == 0) else SUNT)), x, y, 1)
        items = ''.join(f'<div><i></i>{H.escape(t)}</div>' for t in C1_LIST)
        lst = f'<div class="list t">{items}</div>'
        body = top_wm() + stack([h1('10 packets. 1,000+ seeds.<br>One box.', raw=True), panel(art(a, 790, 390), 840, 430), lst], 100, 1020, 44) + num(2, N)
        return page(SUN, body)
    if i == 3:
        a = g(book(W=560, H=360), 10, 0, 1.12)
        body = top_wm() + stack([panel(art(a, 650, 405), 760, 460), h1('A 24-page grow guide walks you from packet to plate.'),
                                 sub('Planting depth, spacing, watering, harvest timing for every variety.')], 100, 1020, 40) + num(3, N)
        return page(SUN, body)
    if i == 4:
        a = g(box_flat(tray=0.62, W=420, D=290, H=66), 36, 240, 0.95)
        body = top_wm() + stack([panel(art(a, 760, 360), 800, 400), h1('Wraps like a book.<br>Opens like a treasure box.', raw=True),
                                 sub('Slide-out keepsake box, foam insert, every packet in its place.')], 100, 1020, 40) + num(4, N)
        return page(SUN, body)
    if i == 5:
        a = g(box_flat(tray=0.5, W=420, D=290, H=66), 40, 215, 0.88)
        body = stack([f'<div class="a">{wordmark_svg(720, KET)}</div>', panel(art(a, 700, 320), 760, 370),
                      h1('$24.99 on Amazon. Ships Prime.'), sub('Save this for the holidays.')], 40, 1060, 44) + num(5, N)
        return page(SUN, body)


# ------------------------------------------------------------------ carousel 2 (Cream, Leaf accents)
def leaf_rule(w=220):
    c = el('line', stroke=LEAF, sw=3, x1=0, y1=16, x2=w/2-26, y2=16) + el('line', stroke=LEAF, sw=3, x1=w/2+26, y1=16, x2=w, y2=16)
    c += g(leaf(36, 8, LEAF, CREAM, LEAF), w/2-18, 16, rot=0)
    return f'<div class="a">{svg(c, w, 32)}</div>'


def c2(i):
    N = 6
    numc = LEAF
    if i == 1:
        a = g(window_sill(W=520, H=580), 0, 0, 1.0)
        body = top_wm(300) + stack([h1('No yard? Start here.', 104), art(a, 520, 560), leaf_rule(), sub('A windowsill is enough to begin.')], 120, 1000, 36) + num(1, N, numc)
        return page(CREAM, body, 'cover')
    if i == 2:
        a = g(kale_leaf(L=260, W=130), 90, 350, 1) + g(spinach_leaf(L=220, W=140), 262, 330, 1)
        a += g(carrot(), 450, 110, 0.9) + g(beet_whole(), 630, 230, 0.9) + g(turnip(), 800, 250, 0.9)
        body = top_wm() + stack([h1('Five of the ten grow in cool weather.'), art(a, 900, 400), leaf_rule(),
                                 sub_lines(["Kale 'Red Russian' · Spinach 'Bloomsdale' ·", "Carrot 'Danvers 126' · Beet 'Chioggia' ·", "Turnip 'Purple Top'"], size=36)], 100, 1020, 36) + num(2, N, numc)
        return page(CREAM, body)
    if i == 3:
        # balcony railing planter, sun off to the upper left
        a = g(sun_disc(64), 150, 110, 1)
        rail = ''
        for k in range(10):
            x = 92 + k*80
            rail += el('line', x1=x, y1=258, x2=x, y2=420)
        rail += el('rect', fill=CREAM, x=70, y=240, width=760, height=20, rx=4)
        a += rail
        a += el('polygon', fill=KET, points='250,270 650,270 628,408 272,408')
        a += el('rect', fill=KETD, x=232, y=242, width=436, height=32, rx=4)
        a += g(kale_leaf(L=170, W=90), 318, 244, 1, rot=-8)
        a += g(sprig(150), 400, 244, 1)
        a += g(carrot_tops(), 470, 244, 1)
        a += g(sprig(135), 540, 244, 1)
        a += g(spinach_leaf(L=150, W=100), 600, 244, 1, rot=8)
        body = top_wm() + stack([h1('A sunny windowsill or a balcony planter.'), art(a, 900, 430), leaf_rule(),
                                 sub('The grow guide covers spacing and light for each one.')], 100, 1020, 36) + num(3, N, numc)
        return page(CREAM, body)
    if i == 4:
        a = g(packet(icon=packet_icon('beet'), w=320, h=432), 290, 0, 1) + g(stamp(84), 606, 92, 1, rot=-14)
        body = top_wm() + stack([h1('The germination rate is printed on every packet.'), art(a, 900, 440), leaf_rule(),
                                 sub('Every lot is lab tested, so you know what to expect.')], 100, 1020, 36) + num(4, N, numc)
        return page(CREAM, body)
    if i == 5:
        a = g(pots(W=680), 8, 270, 1.3)
        body = top_wm() + stack([h1('Sow. Water. Watch.', 84), art(a, 900, 440), leaf_rule(),
                                 sub("Carrots are slow. That's normal.")], 100, 1020, 46) + num(5, N, numc)
        return page(CREAM, body)
    if i == 6:
        a = g(box_flat(tray=0.5, W=420, D=290, H=66), 40, 185, 0.88)
        body = stack([f'<div class="a">{wordmark_svg(720, KET)}</div>', art(a, 700, 260),
                      h1("Kit's on Amazon. $24.99."), leaf_rule(), sub('Save this for your first garden.')], 40, 1060, 40) + num(6, N, numc)
        return page(CREAM, body)


# ------------------------------------------------------------------ carousel 3 (Sun tint, Ketchup accents)
def c3(i):
    N = 5
    rc = KET
    if i == 1:
        a = g(tray_top(W=720, H=480, kinds=['sprig','carrot','sprig','kale','spinach','beet','turnip','sprig','sprig','sprig']), 0, 0, 1)
        body = top_wm(300) + stack([h1("What's actually in the box", 100), art(a, 720, 480), sub('No filler. No gimmicks.', color=KET)], 120, 1000, 48) + num(1, N, KET)
        return page(SUNT, body, 'cover', rule_color=rc)
    if i == 2:
        a = ''
        kinds = ['sprig', 'carrot', 'sprig', 'kale', 'spinach', 'beet', 'turnip', 'sprig', 'sprig', 'sprig']
        for k in range(10):
            r, c = divmod(k, 5)
            x = 15 + c*(150+30); y = r*(203+30)
            a += g(packet(icon=packet_icon(kinds[k]), w=150, h=203, window=(SUN if k % 2 == 0 else SUNT)), x, y, 1)
        body = top_wm() + stack([h1('10 paper seed packets'), art(a, 900, 436), sub('Non-GMO, open-pollinated, 1,000+ seeds.', color=KET)], 100, 1020, 48) + num(2, N, KET)
        return page(SUNT, body, rule_color=rc)
    if i == 3:
        a = g(packet(icon=packet_icon('carrot'), w=320, h=432), 290, 0, 1) + g(stamp(84), 606, 62, 1, rot=-14)
        body = top_wm() + stack([h1('Lab-tested seed'), art(a, 900, 440), sub('The germination rate is printed right on the packet.', color=KET)], 100, 1020, 48) + num(3, N, KET)
        return page(SUNT, body, rule_color=rc)
    if i == 4:
        a = g(book(W=600, H=380), 0, 0, 1.2)
        body = top_wm() + stack([h1('A 24-page grow guide'), art(a, 720, 460), sub('Depth, spacing, watering and harvest for every variety.', color=KET)], 100, 1020, 48) + num(4, N, KET)
        return page(SUNT, body, rule_color=rc)
    if i == 5:
        a = g(box_flat(tray=0.5, W=420, D=290, H=66), 40, 185, 0.88)
        body = stack([f'<div class="a">{wordmark_svg(720, KET)}</div>', art(a, 700, 260),
                      h1('A slide-out keepsake box'), sub('$24.99 on Amazon · Packed in the USA', color=KET)], 40, 1060, 44) + num(5, N, KET)
        return page(SUNT, body, rule_color=rc)


# ------------------------------------------------------------------ statics
def s1():
    # plain old-fashioned packets receding (progressively fainter) into one bright Happy Seeds packet
    a = ''
    for k in range(4):
        x = 0 + k*132; y = 150 - k*24; op = (0.32, 0.5, 0.7, 0.9)[k]
        plain = el('rect', fill=CREAM, stroke=MUTED, x=0, y=0, width=150, height=203, rx=8)
        plain += el('line', stroke=MUTED, x1=0, y1=34, x2=150, y2=34)
        plain += el('rect', fill=LINE, stroke=MUTED, x=17, y=50, width=116, height=104, rx=4)
        for yy, ln in ((176, 64), (189, 96)):
            plain += el('line', stroke=MUTED, sw=2.5, x1=20, y1=yy, x2=20+ln, y2=yy)
        a += g(plain, x, y, 1, extra=f'opacity="{op}"')
    a += g(packet(icon=packet_icon('beet'), w=290, h=392), 600, 0, 1)
    body = top_wm(300) + stack([h1('Seed packets just got a glow up.', 100), art(a, 900, 400),
                                sub('Happy Seeds Veggie Garden Kit · $24.99 on Amazon', size=36)], 120, 1000, 52)
    return page(CREAM, body, 'cover')


def s2():
    a = g(beet_cut(r=170), 300, 230, 1)
    a += g(beet_whole(), 620, 250, 1.1)
    body = top_wm(300) + stack([h1("Beet 'Chioggia': the candy-striped one.", 96), panel(art(a, 800, 470), 840, 510),
                                sub('One of ten in the Happy Seeds kit')], 120, 1000, 48)
    return page(SUN, body, 'cover')


SLIDES = []
for i in range(1, 6):
    SLIDES.append((f'c1-{i}', 'carousel-1', i, c1(i)))
for i in range(1, 7):
    SLIDES.append((f'c2-{i}', 'carousel-2', i, c2(i)))
for i in range(1, 6):
    SLIDES.append((f'c3-{i}', 'carousel-3', i, c3(i)))
SLIDES.append(('s1', 'static', 1, s1()))
SLIDES.append(('s2', 'static', 2, s2()))

CHECK_JS = '''
() => {
  const safe = {l:90, t:90, r:990, b:1260};
  const probs = [];
  const els = [...document.querySelectorAll('.t, .a')];
  const boxes = els.map(e => { const r = e.getBoundingClientRect(); return {e, cls:e.className.baseVal||e.className, l:r.left, t:r.top, r:r.right, b:r.bottom}; });
  for (const b of boxes) {
    if (b.l < safe.l-0.5 || b.t < safe.t-0.5 || b.r > safe.r+0.5 || b.b > safe.b+0.5) probs.push('outside safe: ' + b.cls + ' ' + [b.l,b.t,b.r,b.b].map(Math.round).join(','));
    if (b.e.classList.contains('t') && (b.e.scrollWidth > b.e.clientWidth + 1 || b.e.scrollHeight > b.e.clientHeight + 4)) probs.push('overflow: ' + b.e.textContent.slice(0,40));
  }
  for (let i = 0; i < boxes.length; i++) for (let j = i+1; j < boxes.length; j++) {
    const a = boxes[i], c = boxes[j];
    if (a.e.contains(c.e) || c.e.contains(a.e)) continue;
    const ov = Math.min(a.r, c.r) - Math.max(a.l, c.l) > 0.5 && Math.min(a.b, c.b) - Math.max(a.t, c.t) > 0.5;
    if (ov) probs.push('overlap: ' + a.cls + ' x ' + c.cls + ' (' + (a.e.textContent||'').slice(0,30) + ' / ' + (c.e.textContent||'').slice(0,30) + ')');
  }
  // text metrics for review
  const lines = [...document.querySelectorAll('.h1, .sub')].map(e => { const r = e.getBoundingClientRect(); return e.className + ' h=' + Math.round(r.height) + ' fs=' + getComputedStyle(e).fontSize; });
  return {probs, lines, fonts: [...document.fonts].map(f => f.family + ':' + f.status)};
}
'''


def render(only=None):
    report = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        for name, sset, idx, html_src in SLIDES:
            if only and name not in only:
                continue
            path = f'{WORK}/{name}.html'
            open(path, 'w').write(html_src)
            pg.goto('file://' + path)
            pg.evaluate('document.fonts.ready.then(()=>true)')
            pg.wait_for_timeout(150)
            res = pg.evaluate(CHECK_JS)
            tmp = f'{WORK}/{name}.raw.png'
            pg.screenshot(path=tmp, full_page=False)
            im = Image.open(tmp).convert('RGB')
            assert im.size == (1080, 1350), im.size
            q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            q.save(f'{OUT}/{name}.png', optimize=True)
            size = os.path.getsize(f'{OUT}/{name}.png')
            report.append((name, res['probs'], res['lines'], size))
        b.close()
    for name, probs, lines, size in report:
        print(f'{name}: {size//1024} KB | ' + ('OK' if not probs else ' ; '.join(probs)))
        for l in lines:
            print('    ', l)


if __name__ == '__main__':
    render(sys.argv[1:] or None)
