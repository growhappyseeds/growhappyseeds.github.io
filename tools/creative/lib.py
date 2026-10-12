"""Packet Folk illustration library: flat fills, one even Ink line, brand palette only."""
import math, re

SUN = '#F6BE35'; SUNT = '#FFF3D6'; KET = '#D6362B'; KETD = '#B72A20'; LEAF = '#2E6B34'
CREAM = '#FFFBF2'; INK = '#26211A'; MUTED = '#6B6254'; LINE = '#EFE4CC'
SW = 3.5  # ink line at final scale (non-scaling stroke)

import os
BATCH = os.path.dirname(os.path.abspath(__file__))
_wm = open(BATCH + '/wordmark.svg').read()
WM_D = re.search(r'<path d="([^"]+)"', _wm).group(1)
WM_W, WM_H = 2496, 587


def el(tag, fill='none', stroke=INK, sw=SW, **attrs):
    a = {'fill': fill, 'stroke': stroke if stroke else 'none', 'stroke-width': sw,
         'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'vector-effect': 'non-scaling-stroke'}
    for k, v in attrs.items():
        a[k.replace('_', '-')] = v
    return '<' + tag + ' ' + ' '.join(f'{k}="{v}"' for k, v in a.items()) + '/>'


def g(content, x=0, y=0, s=1, rot=0, extra=''):
    t = f'translate({x},{y})'
    if rot:
        t += f' rotate({rot})'
    if s != 1:
        t += f' scale({s})'
    return f'<g transform="{t}" {extra}>{content}</g>'


def wordmark_svg(width, color=KET, cls='', style=''):
    h = width * WM_H / WM_W
    return (f'<svg class="{cls}" style="{style}" width="{width:.1f}" height="{h:.1f}" viewBox="0 0 {WM_W} {WM_H}">'
            f'<g transform="translate(0,{WM_H}) scale(0.1,-0.1)" fill="{color}"><path d="{WM_D}"/></g></svg>')


def wordmark_in(x, y, width, color=KET):
    """Nested svg for use inside an illustration (local coords)."""
    h = width * WM_H / WM_W
    return (f'<svg x="{x}" y="{y}" width="{width}" height="{h:.2f}" viewBox="0 0 {WM_W} {WM_H}" overflow="visible">'
            f'<g transform="translate(0,{WM_H}) scale(0.1,-0.1)" fill="{color}"><path d="{WM_D}"/></g></svg>')


# ---------- primitives ----------

def leaf(L, w, fill=LEAF, vein=CREAM, stroke=INK):
    """Almond leaf from (0,0) to (L,0), half-width w. Midrib in vein colour."""
    c = 0.55
    p = f'M0,0 C{L*0.25},{-w*1.5} {L*0.75},{-w*1.4} {L},0 C{L*0.75},{w*1.4} {L*0.25},{w*1.5} 0,0 Z'
    out = el('path', fill=fill, stroke=stroke, d=p)
    if vein:
        out += el('line', stroke=vein, sw=2.5, x1=L*0.08, y1=0, x2=L*0.86, y2=0)
    return out


def sprig(h=120, fill=LEAF):
    """A stem with three leaves, base at (0,0), growing up to (0,-h)."""
    out = el('path', stroke=LEAF, d=f'M0,0 C 4,{-h*0.4} -4,{-h*0.7} 0,{-h}')
    out += g(leaf(h*0.42, h*0.11, fill), 0, -h*0.42, rot=-150)
    out += g(leaf(h*0.42, h*0.11, fill), 0, -h*0.62, rot=-35)
    out += g(leaf(h*0.40, h*0.11, fill), 0, -h*0.98, rot=-95)
    return out


def packet(paper=CREAM, window=SUN, band=KET, icon=None, w=200, h=270):
    """Seed packet, local box (0,0)-(w,h). Icon is an svg string centred in the window."""
    s = w / 200
    out = el('rect', fill=paper, x=0, y=0, width=w, height=h, rx=10*s)
    out += el('line', x1=0, y1=44*s, x2=w, y2=44*s)
    out += el('rect', fill=window, x=22*s, y=66*s, width=w-44*s, height=h-130*s, rx=6*s)
    if icon:
        out += g(icon, w/2, 66*s + (h-130*s)/2, s)
    out += el('rect', fill=band, x=22*s, y=h-48*s, width=w-44*s, height=26*s, rx=4*s)
    return out


def carrot(fill=SUN):
    """Carrot, local approx x -60..60, y -100..230 (body from y=0 down, leaves up)."""
    body = 'M-34,0 C-40,80 -24,170 0,230 C24,170 40,80 34,0 C20,-10 -20,-10 -34,0 Z'
    out = el('path', fill=fill, d=body)
    for yy, hw in ((50, 26), (100, 21), (150, 14)):
        out += el('path', sw=2.5, d=f'M{-hw},{yy} q{hw},8 {2*hw},0')
    out += g(leaf(82, 10), -8, -8, rot=-128)
    out += g(leaf(90, 10), 0, -14, rot=-90)
    out += g(leaf(82, 10), 8, -8, rot=-52)
    return out


def beet_whole(fill=KET):
    """Whole beet with leaves; local x -90..90, y -150..140."""
    out = ''
    stems = [(-20, -140, -40), (0, -150, 0), (20, -140, 40)]
    for dx, ty, rot in stems:
        out += el('path', stroke=KETD, sw=4, d=f'M{dx*0.3},-70 Q{dx},{ty*0.5} {dx*1.3},{ty+30}')
        out += g(leaf(76, 16, LEAF, KETD), dx*1.3, ty+30, rot=-90+rot)
    bulb = 'M0,120 C-45,120 -82,85 -82,30 C-82,-35 -45,-78 0,-78 C45,-78 82,-35 82,30 C82,85 45,120 0,120 Z'
    out += el('path', fill=fill, d=bulb)
    out += el('path', sw=2.5, d='M-40,60 Q0,74 40,60')
    out += el('path', sw=2.5, d='M-52,20 Q0,34 52,20')
    out += el('path', d='M0,120 Q-4,132 2,142')
    return out


def beet_cut(r=100, a=KET, b=CREAM):
    """Cross-section with concentric candy stripes and a thin skin ring."""
    out = el('circle', fill=KETD, cx=0, cy=0, r=r)
    rings = [0.93, 0.80, 0.68, 0.56, 0.45, 0.34, 0.24, 0.14]
    for i, f in enumerate(rings):
        out += el('circle', fill=(b if i % 2 == 0 else a), stroke=None, cx=0, cy=0, r=r*f)
    return out


_kale_id = 0


def kale_leaf(L=300, W=150, fill=LEAF, rib=KETD):
    """Frilly kale leaf standing up: base at (0,0), tip at (0,-L)."""
    pts = []
    N = 160
    for i in range(N):
        t = i / N * 2 * math.pi
        # ellipse centred at (0,-L/2), frill modulation stronger at the sides
        base_x = (W/2) * math.sin(t)
        base_y = -L/2 - (L/2) * math.cos(t)
        frill = 1 + 0.10 * math.sin(11*t) * abs(math.sin(t)) ** 0.5
        pts.append((base_x*frill, -L/2 + (base_y + L/2)*(1 + 0.03*math.sin(11*t))))
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'
    global _kale_id
    _kale_id += 1
    cid = f'kale{_kale_id}'
    out = f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
    out += el('path', fill=fill, d=d)
    veins = el('path', stroke=rib, sw=4, d=f'M0,0 L0,{-L*0.88}')
    for k in range(1, 5):
        yy = -L * (0.18 + 0.16*k)
        veins += el('path', stroke=rib, sw=2.5, d=f'M0,{yy} Q{W*0.22},{yy-12} {W*0.36},{yy-30}')
        veins += el('path', stroke=rib, sw=2.5, d=f'M0,{yy} Q{-W*0.22},{yy-12} {-W*0.36},{yy-30}')
    out += f'<g clip-path="url(#{cid})">{veins}</g>'
    out += el('path', fill='none', d=d)
    return out


def spinach_leaf(L=240, W=150, fill=LEAF):
    """Rounded spinach leaf, base at (0,0), tip at (0,-L)."""
    d = (f'M0,0 C{-W*0.55},{-L*0.05} {-W*0.62},{-L*0.55} {-W*0.3},{-L*0.8} '
         f'C{-W*0.15},{-L*0.95} {-W*0.05},{-L} 0,{-L} '
         f'C{W*0.05},{-L} {W*0.15},{-L*0.95} {W*0.3},{-L*0.8} '
         f'C{W*0.62},{-L*0.55} {W*0.55},{-L*0.05} 0,0 Z')
    out = el('path', fill=fill, d=d)
    out += el('line', stroke=CREAM, sw=2.5, x1=0, y1=-L*0.06, x2=0, y2=-L*0.9)
    for k in range(1, 4):
        yy = -L*(0.15 + 0.2*k)
        out += el('path', stroke=CREAM, sw=2, d=f'M0,{yy} Q{W*0.15},{yy-10} {W*0.3},{yy-40}')
        out += el('path', stroke=CREAM, sw=2, d=f'M0,{yy} Q{-W*0.15},{yy-10} {-W*0.3},{yy-40}')
    out += el('path', stroke=LEAF, d=f'M0,0 L0,{L*0.18}')
    return out


def turnip():
    """Purple-top turnip: cream bulb with a deep-red cap; local x -90..90, y -150..120."""
    out = ''
    for dx, ty, rot in ((-18, -140, -35), (0, -150, 0), (18, -140, 35)):
        out += el('path', stroke=LEAF, sw=4, d=f'M{dx*0.3},-60 Q{dx},{ty*0.5} {dx*1.2},{ty+34}')
        out += g(leaf(70, 15), dx*1.2, ty+34, rot=-90+rot)
    bulb = 'M0,100 C-50,100 -86,70 -86,20 C-86,-30 -50,-64 0,-64 C50,-64 86,-30 86,20 C86,70 50,100 0,100 Z'
    out += el('path', fill=CREAM, stroke=None, d=bulb)
    cap = 'M-84,8 C-60,0 -30,16 0,10 C30,4 60,18 84,8 C80,-30 50,-64 0,-64 C-50,-64 -80,-30 -84,8 Z'
    out += el('path', fill=KETD, stroke=None, d=cap)
    out += el('path', fill='none', d=bulb)
    out += el('path', sw=2.5, d='M-84,8 C-60,0 -30,16 0,10 C30,4 60,18 84,8')
    out += el('path', d='M0,100 Q-3,112 2,124')
    return out


def box(W=420, H=270, dx=80, dy=56, tray=0.0, mark=True, mark_w=None, mark_x=None, front=SUN, top=SUNT, packets=2):
    """Oblique slide-out box. Front face (0,0)-(W,H); top face rises by dy and shifts dx.
    tray in 0..1 slides the inner tray out to the right. Bounds: x 0..W+dx+tray*W, y -dy..H
    (standing packets rise to about y = -H*0.55 when tray > 0)."""
    out = ''
    if tray > 0:
        tl = tray * W
        ins = 12
        sx, sy = dx * (1 - 2*ins/H), dy * (1 - 2*ins/H)
        x0, y0, hh = W, ins, H - 2*ins
        # foam top of the tray, with slot outlines
        out += el('polygon', fill=LINE, points=f'{x0},{y0} {x0+tl},{y0} {x0+tl+sx},{y0-sy} {x0+sx},{y0-sy}')
        # packets standing in the tray (their lower part hidden by the tray front)
        pw = min(150, tl*0.46); ph = pw*1.35
        xs = [x0 + tl*0.30, x0 + tl*0.70][:packets]
        for i, cx in enumerate(xs):
            rot = -5 if i == 0 else 4
            icon = sprig(pw*0.42) if i == 0 else g(carrot(), 0, -pw*0.33, pw*0.0036)
            out += g(packet(icon=icon, w=pw, h=ph), cx - pw/2 + sx*0.4, y0 - sy*0.4 + hh*0.5 - ph, 1, rot=rot)
        out += el('rect', fill=CREAM, x=x0, y=y0, width=tl, height=hh)
        out += el('path', fill=LINE, d=f'M{x0+tl*0.5-24},{y0} a24,24 0 0 0 48,0 Z')
        out += el('polygon', fill=SUNT, points=f'{x0+tl},{y0} {x0+tl+sx},{y0-sy} {x0+tl+sx},{y0+hh-sy} {x0+tl},{y0+hh}')
    out += el('polygon', fill=top, points=f'0,0 {W},0 {W+dx},{-dy} {dx},{-dy}')
    out += el('polygon', fill=front, points=f'{W},0 {W+dx},{-dy} {W+dx},{H-dy} {W},{H}')
    for i in range(1, 6):
        yy = H*i/6
        out += el('line', sw=1.5, x1=W+5, y1=yy, x2=W+dx-5, y2=yy-dy)
    out += el('rect', fill=front, x=0, y=0, width=W, height=H)
    if mark:
        mw = mark_w or W*0.66
        mx = mark_x if mark_x is not None else (W-mw)/2
        mh = mw*WM_H/WM_W
        out += wordmark_in(mx, (H-mh)/2, mw, KET)
    return out


def tray_top(W=640, H=440, kinds=None):
    """Top-down view of the open tray with ten packets and the guide."""
    out = el('rect', fill=SUN, x=0, y=0, width=W, height=H, rx=14)
    out += el('rect', fill=LINE, x=24, y=24, width=W-48, height=H-48, rx=8)
    pw, ph, gap = 92, 122, 18
    cols = 5
    x0 = (W - (cols*pw + (cols-1)*gap)) / 2
    y0 = 46
    for r in range(2):
        for c in range(cols):
            x = x0 + c*(pw+gap); y = y0 + r*(ph+gap)
            out += el('rect', fill=CREAM, x=x, y=y, width=pw, height=ph, rx=5)
            out += el('line', x1=x, y1=y+20, x2=x+pw, y2=y+20)
            out += el('rect', fill=SUN, stroke=None, x=x+12, y=y+32, width=pw-24, height=ph-62, rx=3)
            kind = kinds[r*cols+c] if kinds else 'sprig'
            out += g(packet_icon(kind), x+pw/2, y+32+(ph-62)/2, 0.46)
            out += el('rect', fill=KET, stroke=None, x=x+12, y=y+ph-24, width=pw-24, height=12, rx=2)
    gy = y0 + 2*ph + gap + 10
    gh = H - 24 - 22 - gy
    gx = x0; gw = cols*pw + (cols-1)*gap
    out += el('rect', fill=CREAM, x=gx, y=gy, width=gw, height=gh, rx=5)
    out += el('line', stroke=MUTED, sw=3, x1=gx+24, y1=gy+gh/2-14, x2=gx+gw*0.45, y2=gy+gh/2-14)
    out += el('line', stroke=MUTED, sw=3, x1=gx+24, y1=gy+gh/2+2, x2=gx+gw*0.36, y2=gy+gh/2+2)
    out += el('line', stroke=MUTED, sw=3, x1=gx+24, y1=gy+gh/2+18, x2=gx+gw*0.41, y2=gy+gh/2+18)
    out += g(sprig(gh*0.7), gx+gw-70, gy+gh-16, 1)
    return out


def book(W=480, H=320):
    """Open grow guide. Local (0,0)-(W,H)."""
    m = W/2
    left = f'M{m},34 L24,52 Q14,53 14,63 L14,{H-30} Q14,{H-20} 24,{H-21} L{m},{H-8} Z'
    right = f'M{m},34 L{W-24},52 Q{W-14},53 {W-14},63 L{W-14},{H-30} Q{W-14},{H-20} {W-24},{H-21} L{m},{H-8} Z'
    out = el('path', fill=CREAM, d=left) + el('path', fill=CREAM, d=right)
    out += el('line', x1=m, y1=34, x2=m, y2=H-8)
    # text lines on the left page (follow the slight page slant)
    for i, frac in enumerate((0.9, 0.75, 0.85, 0.6, 0.8, 0.5)):
        y = 92 + i*28
        x1, x2 = 40, 40 + (m-70)*frac
        out += el('line', stroke=MUTED, sw=3, x1=x1, y1=y-4, x2=x2, y2=y-4+(x2-x1)*0.02)
    # diagram on the right page: soil line, seedling, depth marker, sun
    sx = m + 40
    soil_y = H - 92
    out += el('line', x1=sx, y1=soil_y, x2=W-50, y2=soil_y)
    for k in range(5):
        xx = sx + 14 + k*38
        out += el('line', sw=2.5, x1=xx, y1=soil_y+10, x2=xx+8, y2=soil_y+10)
    out += el('circle', fill=INK, stroke=None, cx=sx+112, cy=soil_y+36, r=5)
    out += el('line', sw=2.5, x1=sx+80, y1=soil_y, x2=sx+80, y2=soil_y+36)
    out += el('line', sw=2.5, x1=sx+72, y1=soil_y, x2=sx+88, y2=soil_y)
    out += el('line', sw=2.5, x1=sx+72, y1=soil_y+36, x2=sx+88, y2=soil_y+36)
    out += g(sprig(110), sx+112, soil_y, 1)
    out += el('circle', fill=SUN, cx=W-62, cy=78, r=18)
    for k in range(8):
        a = k*math.pi/4
        out += el('line', sw=2.5, x1=W-62+26*math.cos(a), y1=78+26*math.sin(a), x2=W-62+34*math.cos(a), y2=78+34*math.sin(a))
    return out


def window_sill(W=520, H=580):
    """Window with a planter on the sill. Local (0,0)-(W,H)."""
    fx, fy, fw, fh = 30, 10, W-60, 400
    out = el('rect', fill=SUNT, x=fx, y=fy, width=fw, height=fh)
    # sun in the top-right pane
    cx, cy = fx+fw*0.74, fy+fh*0.26
    out += el('circle', fill=SUN, cx=cx, cy=cy, r=44)
    for k in range(8):
        a = k*math.pi/4 + math.pi/8
        out += el('line', sw=2.5, x1=cx+56*math.cos(a), y1=cy+56*math.sin(a), x2=cx+70*math.cos(a), y2=cy+70*math.sin(a))
    # mullions (cream bars with ink edges)
    out += el('rect', fill=CREAM, x=fx+fw/2-9, y=fy, width=18, height=fh)
    out += el('rect', fill=CREAM, x=fx, y=fy+fh/2-9, width=fw, height=18)
    out += el('rect', fill='none', x=fx, y=fy, width=fw, height=fh)
    # outer casing
    out += el('rect', fill='none', x=fx-16, y=fy-16, width=fw+32, height=fh+32)
    # sill
    out += el('rect', fill=CREAM, x=0, y=fy+fh+16, width=W, height=30, rx=3)
    # planter
    py = fy+fh+16
    out += el('polygon', fill=KET, points=f'140,{py-6} {W-140},{py-6} {W-160},{py+120} 160,{py+120}')
    out += el('rect', fill=KETD, x=126, y=py-34, width=W-252, height=30, rx=4)
    for i, (px, hh) in enumerate(((190, 120), (W/2, 150), (W-190, 120))):
        out += g(sprig(hh), px, py-34, 1)
    return out


def pots(W=760):
    """Sow / water / watch: three pots in a row. Local x 0..W, y -200..130."""
    out = ''
    cxs = [W/6, W/2, 5*W/6]
    for i, cx in enumerate(cxs):
        # pot
        out += el('polygon', fill=KET, points=f'{cx-70},0 {cx+70},0 {cx+56},120 {cx-56},120')
        out += el('rect', fill=KETD, x=cx-78, y=-26, width=156, height=28, rx=4)
        if i == 0:
            out += el('ellipse', fill=MUTED, cx=cx, cy=-26, rx=62, ry=10)
            out += el('ellipse', fill=INK, stroke=None, cx=cx, cy=-96, rx=9, ry=13)
            out += el('line', sw=2.5, x1=cx-22, y1=-150, x2=cx-16, y2=-128)
            out += el('line', sw=2.5, x1=cx+22, y1=-150, x2=cx+16, y2=-128)
            out += el('line', sw=2.5, x1=cx, y1=-166, x2=cx, y2=-142)
        elif i == 1:
            out += el('ellipse', fill=MUTED, cx=cx, cy=-26, rx=62, ry=10)
            # watering can, tilted, top-right
            can = el('rect', fill=LEAF, x=0, y=0, width=90, height=70, rx=8)
            can += el('path', fill='none', d='M10,0 Q45,-40 80,0')
            can += el('path', fill=LEAF, d='M0,18 L-60,-10 L-66,2 L0,38 Z')
            can += el('circle', fill=LEAF, cx=-64, cy=-4, r=14)
            out += g(can, cx+30, -176, 1, rot=24)
            for k, (dx, dy) in enumerate(((-40, -120), (-52, -90), (-38, -62))):
                out += el('path', fill=SUNT, d=f'M{cx+dx},{dy-14} q-9,12 -9,18 a9,9 0 0 0 18,0 q0,-6 -9,-18 Z')
        else:
            # cutaway soil with a young carrot
            out += el('polygon', fill=MUTED, stroke=None, points=f'{cx-62},0 {cx+62},0 {cx+50},112 {cx-50},112')
            out += el('ellipse', fill=MUTED, cx=cx, cy=-26, rx=62, ry=10)
            out += g(carrot(), cx, -14, 0.42)
    return out


def stamp(r=74):
    out = el('circle', fill='none', stroke=LEAF, sw=7, cx=0, cy=0, r=r)
    out += el('circle', fill='none', stroke=LEAF, sw=3, cx=0, cy=0, r=r-14)
    out += el('path', fill='none', stroke=LEAF, sw=11, d=f'M{-r*0.36},{2} L{-r*0.08},{r*0.3} L{r*0.42},{-r*0.3}')
    return out


def sun_disc(r=60):
    out = el('circle', fill=SUN, cx=0, cy=0, r=r)
    for k in range(12):
        a = k*math.pi/6
        out += el('line', x1=(r+14)*math.cos(a), y1=(r+14)*math.sin(a), x2=(r+30)*math.cos(a), y2=(r+30)*math.sin(a))
    return out


def ribbon_bow(w=120):
    """Bow centred at (0,0)."""
    out = el('path', fill=KET, d=f'M0,0 C{-w*0.2},{-w*0.5} {-w*0.75},{-w*0.45} {-w*0.6},{-w*0.1} C{-w*0.5},{w*0.15} {-w*0.2},{w*0.12} 0,0 Z')
    out += el('path', fill=KET, d=f'M0,0 C{w*0.2},{-w*0.5} {w*0.75},{-w*0.45} {w*0.6},{-w*0.1} C{w*0.5},{w*0.15} {w*0.2},{w*0.12} 0,0 Z')
    out += el('path', fill=KET, d=f'M-6,6 L{-w*0.3},{w*0.5} L{-w*0.12},{w*0.46} L0,{w*0.2} L{w*0.12},{w*0.46} L{w*0.3},{w*0.5} L6,6 Z')
    out += el('circle', fill=KETD, cx=0, cy=0, r=w*0.1)
    return out


def svg(content, w, h, cls='a', style=''):
    return f'<svg class="{cls}" style="{style}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="visible">{content}</svg>'


def topg(content, D, kx, ky, z=0):
    """Map content drawn in lid-page coordinates (u right, w down-toward-viewer, page D tall) onto the oblique top face."""
    return f'<g transform="matrix(1 0 {-kx} {ky} {D*kx:.3f} {-D*ky+z:.3f})">{content}</g>'


def flat_packet(w, h, icon=None, paper=CREAM, window=SUN, band=KET):
    return packet(paper=paper, window=window, band=band, icon=icon, w=w, h=h)


def packet_icon(kind):
    """Vegetable icon sized for the packet window (200-unit packet space, centred at 0,0)."""
    if kind == 'sprig':
        return g(sprig(104), 0, 52)
    if kind == 'carrot':
        return g(carrot(), 0, -26, 0.36)
    if kind == 'beet':
        return g(beet_whole(), 0, 2, 0.36)
    if kind == 'kale':
        return g(kale_leaf(), 0, 51, 0.34)
    if kind == 'spinach':
        return g(spinach_leaf(), 0, 42, 0.38)
    if kind == 'turnip':
        return g(turnip(), 0, 5, 0.36)
    return ''


def box_flat(W=440, D=300, H=72, kx=0.42, ky=0.66, tray=0.0, ribbon=False, mark=True, mark_w=None, mark_u=None, packets=None):
    """Book-shaped slide-out box lying flat, oblique view. Front edge (0,0)-(W,H); lid rises back by D*ky and shifts D*kx.
    tray slides the inner tray out of the right end by tray*W. Bounds: x 0..W+D*kx+tray*W, y -D*ky..H."""
    P = lambda u, v, z=0: (u + v*kx, -v*ky + z)
    pts = lambda *ps: ' '.join(f'{x:.2f},{y:.2f}' for x, y in ps)
    out = ''
    if tray > 0:
        tl = tray*W; ins = 14; zt = 8; rim = 10
        # tray outer top (rim) and foam
        out += el('polygon', fill=CREAM, points=pts(P(W, ins-rim, zt), P(W+tl, ins-rim, zt), P(W+tl, D-ins+rim, zt), P(W, D-ins+rim, zt)))
        out += el('polygon', fill=LINE, points=pts(P(W, ins, zt), P(W+tl, ins, zt), P(W+tl, D-ins, zt), P(W, D-ins, zt)))
        # packets lying flat in the foam, drawn in page coordinates (u right, w toward viewer)
        pd = (D - 2*ins - 3*18) / 2      # two rows
        pw = pd * 0.78
        content = ''
        slots = packets if packets is not None else [('sprig', 0, 0), ('carrot', 0, 1), ('beet', 1, 0), ('kale', 1, 1)]
        ncol = max(1, int((tl - 18) // (pw + 18)))
        for kind, col, row in slots:
            if col >= ncol:
                continue
            u0 = W + 18 + col*(pw+18) + 6
            w0 = ins + 18 + row*(pd+18)
            icon = packet_icon(kind)
            content += el('rect', fill='none', stroke=MUTED, sw=2, x=u0-6, y=w0-6, width=pw+12, height=pd+12, rx=6)
            content += g(flat_packet(pw, pd, icon), u0, w0, 1)
        out += topg(content, D, kx, ky, zt)
        # tray front face and right end
        out += el('polygon', fill=CREAM, points=pts(P(W, ins-rim, zt), P(W+tl, ins-rim, zt), P(W+tl, ins-rim, H-4), P(W, ins-rim, H-4)))
        out += el('polygon', fill=SUNT, points=pts(P(W+tl, ins-rim, zt), P(W+tl, D-ins+rim, zt), P(W+tl, D-ins+rim, H-4), P(W+tl, ins-rim, H-4)))
        # thumb notch on the tray end
        nx, ny = P(W+tl + (D*kx)*0.5, 0)
        mid = P(W+tl, D/2, zt)
        out += el('path', fill=LINE, d=f'M{mid[0]-10*kx:.2f},{mid[1]+10*ky:.2f} a16,16 0 0 0 {20*kx:.2f},{-20*ky:.2f} Z')
    # sleeve: lid, front, right end
    out += el('polygon', fill=SUN, points=pts(P(0, 0), P(W, 0), P(W, D), P(0, D)))
    out += el('rect', fill=SUN, x=0, y=0, width=W, height=H)
    out += el('polygon', fill=SUNT, points=pts(P(W, 0), P(W, D), P(W, D, H), P(W, 0, H)))
    for i in range(1, 4):
        zz = H*i/4
        out += el('line', sw=1.5, x1=W+4*kx, y1=-4*ky+zz, x2=W+(D-4)*kx, y2=-(D-4)*ky+zz)
    # lid label: thin inner rule and wordmark
    lid = el('rect', fill='none', sw=2.5, x=18, y=18, width=W-36, height=D-36, rx=4)
    if mark:
        mw = mark_w or (W*0.56 if ribbon else W*0.62)
        mu = mark_u if mark_u is not None else (W*0.11 if ribbon else (W-mw)/2)
        mh = mw*WM_H/WM_W
        lid += wordmark_in(mu, (D-mh)/2, mw, KET)
    if ribbon:
        ru = W*0.80; rw = 34
        lid += el('rect', fill=KET, x=ru, y=-2, width=rw, height=D+4)
    out += topg(lid, D, kx, ky, 0)
    if ribbon:
        out += el('rect', fill=KET, x=ru, y=-1, width=rw, height=H+2)
        bx, by = P(ru + rw/2, D*0.5)
        out += g(ribbon_bow(118), bx, by, 1)
    return out


def carrot_tops(h=150):
    """Feathery carrot foliage rising from (0,0)."""
    out = ''
    for rot, L in ((-118, h*0.8), (-96, h), (-74, h*0.8)):
        out += el('path', stroke=LEAF, d=f'M0,0 L{L*math.cos(math.radians(rot)):.1f},{L*math.sin(math.radians(rot)):.1f}')
        for k in range(1, 5):
            f = k/5
            px, py = L*f*math.cos(math.radians(rot)), L*f*math.sin(math.radians(rot))
            out += g(leaf(h*0.16, h*0.03), px, py, rot=rot-48)
            out += g(leaf(h*0.16, h*0.03), px, py, rot=rot+48)
    return out
