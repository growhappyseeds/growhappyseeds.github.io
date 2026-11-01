"""Stop-motion style Reels from approved Happy Seeds claymation statics.

Each reel: a sequence of scenes. Each scene = one hosted static (1080x1350), shown with a slow
Ken Burns move that is stepped at 8 states per second (held 3 frames at 24 fps) with a tiny
random jitter and rotation per step, so the image breathes like a stop-motion set. Captions are
Jost SemiBold, cream on a solid ketchup block or ink on a sun block (brand rule), in the upper
third so Instagram's UI never covers them. Silent (music is added in-app).
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.environ.get("REELS_OUT", "/tmp/reels")
FONT = os.environ.get("JOST_TTF", "/tmp/fonts/Jost.ttf")
W, H = 1080, 1920
FPS = 24
HOLD = 3            # frames per stop-motion step (8 steps per second)
SUN = (246, 190, 53); CREAM = (255, 246, 227); KETCHUP = (214, 54, 43); INK = (38, 33, 26); LEAF = (46, 107, 52)

def font(size):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name("SemiBold")
    return f

CARD_W, CARD_H, CARD_Y = 980, 1225, 330
WORDMARK = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordmark.png")).convert("RGBA")
WORDMARK = WORDMARK.resize((420, round(WORDMARK.height * 420 / WORDMARK.width)), Image.LANCZOS)

def load(path):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    # background: cover-fit, blurred, tinted toward cream
    scale = max(W / im.width, H / im.height)
    bg = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
    l, t = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(36))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (255, 251, 242)), 0.55)
    # card source at 1.12x the card size so zoom has room
    cs = max(CARD_W / im.width, CARD_H / im.height) * 1.12
    card = im.resize((round(im.width * cs), round(im.height * cs)), Image.LANCZOS)
    return bg, card

def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=255)
    out = img.convert("RGBA"); out.putalpha(m)
    return out

def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def caption(frame, text, style, pop):
    """Draw a caption block. style: 'ketchup' (cream text) or 'sun' (ink text). pop: 0..1 scale-in."""
    if not text: return frame
    f = font(58)
    d = ImageDraw.Draw(frame)
    lines = wrap(d, text, f, 900 - 2 * 34)
    lh = 70
    bw = max(d.textlength(l, font=f) for l in lines) + 2 * 34
    bh = lh * len(lines) + 2 * 22
    s = 0.86 + 0.14 * pop
    block = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(block)
    bg, fg = (KETCHUP + (255,), CREAM) if style == "ketchup" else (SUN + (255,), INK)
    bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=28, fill=bg)
    y = 22
    for l in lines:
        bd.text((34, y - 4), l, font=f, fill=fg)
        y += lh
    # soft drop shadow like a clay prop
    shadow = Image.new("RGBA", block.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=28, fill=(38, 33, 26, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    if s != 1:
        block = block.resize((max(1, int(bw * s)), max(1, int(bh * s))), Image.LANCZOS)
        shadow = shadow.resize(block.size, Image.LANCZOS)
    x = 72; y0 = 300 - block.height
    frame.paste(shadow, (x + 4, y0 + 14), shadow)
    frame.paste(block, (x, y0), block)
    return frame

def render(reel):
    random.seed(reel["slug"])
    os.makedirs(os.path.join(OUT, reel["slug"]), exist_ok=True)
    n = 0
    for sc in reel["scenes"]:
        bg, im = load(sc["image"])
        steps = int(sc["seconds"] * FPS / HOLD)
        z0, z1 = sc.get("zoom", (1.0, 1.08))
        px0, px1 = sc.get("panx", (0.5, 0.5))
        py0, py1 = sc.get("pany", (0.5, 0.5))
        for st in range(steps):
            t = st / max(1, steps - 1)
            e = t * t * (3 - 2 * t)  # smoothstep
            z = z0 + (z1 - z0) * e
            cw, ch = CARD_W / z, CARD_H / z
            cx = (px0 + (px1 - px0) * e) * im.width
            cy = (py0 + (py1 - py0) * e) * im.height
            left = min(max(cx - cw / 2, 0), im.width - cw)
            top = min(max(cy - ch / 2, 0), im.height - ch)
            crop = im.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((CARD_W, CARD_H), Image.BILINEAR)
            card = rounded(crop, 40).rotate(random.uniform(-0.45, 0.45), resample=Image.BICUBIC, expand=True)
            frame = bg.copy()
            sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([6, 6, card.width - 7, card.height - 7], radius=40, fill=(38, 33, 26, 110))
            sh = sh.filter(ImageFilter.GaussianBlur(18))
            jx, jy = random.randint(-4, 4), random.randint(-4, 4)
            px, py = (W - card.width) // 2 + jx, CARD_Y + (CARD_H - card.height) // 2 + jy
            frame.paste(sh, (px + 2, py + 22), sh)
            frame.paste(card, (px, py), card)
            frame.paste(WORDMARK, ((W - WORDMARK.width) // 2, 1650 + random.randint(-1, 1)), WORDMARK)
            # caption with a 3-step pop-in at scene start
            pop = min(1.0, st / 3) if sc.get("text") else 0
            frame = caption(frame, sc.get("text"), sc.get("style", "ketchup"), pop)
            for _ in range(HOLD):
                frame.save(os.path.join(OUT, reel["slug"], f"f{n:05d}.jpg"), quality=92)
                n += 1
    # cover frame = first frame
    mp4 = os.path.join(OUT, f"{reel['slug']}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i",
                    os.path.join(OUT, reel["slug"], "f%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-profile:v", "high", "-level", "4.0", "-crf", "20", "-preset", "slow",
                    "-movflags", "+faststart", "-r", str(FPS), mp4], check=True)
    cover = os.path.join(OUT, f"{reel['slug']}-cover.jpg")
    Image.open(os.path.join(OUT, reel["slug"], "f00006.jpg")).save(cover, quality=90)
    return mp4, n / FPS

if __name__ == "__main__":
    reels = json.load(open(sys.argv[1]))
    for r in reels:
        mp4, secs = render(r)
        print(r["slug"], f"{secs:.1f}s", os.path.getsize(mp4) // 1024, "KB")
