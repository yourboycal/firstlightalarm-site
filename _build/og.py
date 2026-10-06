"""Generate 1200x630 Open Graph cards and a square logo in the First Step palette.

Headlines are set in New York, the same serif the app uses for its daily
line, because a bold centred sans is what every other productivity app
in the store looks like. A phrase wrapped in *asterisks* takes the clay.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
SF = "/System/Library/Fonts/SFNS.ttf"
NY = "/System/Library/Fonts/NewYork.ttf"
PAPER, INK, CLAY, SUB = (248, 246, 241), (28, 27, 25), (201, 97, 61), (107, 104, 98)
def font(size, weight, optical):
    f = ImageFont.truetype(SF, size); f.set_variation_by_axes([100, optical, 400, weight]); return f
def serif(size, weight=500):
    f = ImageFont.truetype(NY, size); f.set_variation_by_axes([size, weight, 0]); return f
def ground(w, h):
    """Paper with the light coming from the top right, the way a morning does."""
    im = Image.new("RGB", (w, h), PAPER); px = im.load()
    for y in range(h):
        for x in range(0, w, 2):
            dx, dy = (x - w * 0.86) / (w * 0.72), (y + h * 0.04) / (h * 0.95)
            t = max(0.0, 1.0 - (dx * dx + dy * dy) ** 0.5)
            v = t * t * 0.9
            c = (round(248 + (251 - 248) * v), round(246 + (233 - 246) * v), round(241 + (223 - 241) * v))
            px[x, y] = c
            if x + 1 < w: px[x + 1, y] = c
    return im
def mark(d, cx, cy, r, ink=INK):
    # a sun on the first step, ringing: the First Step mark, box of side 2.4r centred on (cx, cy)
    k = r / 100.0; ox, oy = cx - 120 * k, cy - 120 * k
    d.pieslice([ox + 76*k, oy + 74*k, ox + 180*k, oy + 178*k], 180, 360, fill=CLAY)
    d.rounded_rectangle([ox + 90*k, oy + 134*k, ox + 198*k, oy + 154*k], radius=6*k, fill=CLAY)
    d.rounded_rectangle([ox + 44*k, oy + 160*k, ox + 124*k, oy + 180*k], radius=6*k, fill=CLAY)
    R = 52 * 1.34 * k
    for a0, a1 in ((208, 244), (296, 332)):
        d.arc([ox + 128*k - R, oy + 126*k - R, ox + 128*k + R, oy + 126*k + R], a0, a1, fill=CLAY, width=max(2, round(9*k)))

def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], []
    for w in words:
        if d.textlength(" ".join(cur + [w]), font=f) <= max_w: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines
def card(path, title, kicker):
    im = ground(1200, 630); d = ImageDraw.Draw(im)
    mark(d, 96, 96, 44)
    d.text((140, 74), "First Step", font=font(30, 700, 28), fill=INK)
    d.text((80, 168), kicker.upper(), font=font(20, 700, 20), fill=CLAY)
    # Words inside *asterisks* are the accent; the markers never render.
    words = [(w.strip("*"), w.startswith("*") or w.endswith("*")) for w in title.split()]
    size = 70
    while True:
        f = serif(size); lines = wrap_runs(d, words, f, 1040)
        if len(lines) <= 3 or size <= 42: break
        size -= 4
    y = 206
    for ln in lines:
        x = 80
        for word, accent in ln:
            d.text((x, y), word, font=f, fill=CLAY if accent else INK)
            x += d.textlength(word + " ", font=f)
        y += int(size * 1.14)
    d.text((80, 556), "firststepalarm.com", font=font(22, 500, 20), fill=SUB)
    d.rectangle([0, 622, 1200, 630], fill=CLAY)
    im.save(path, optimize=True)

def wrap_runs(d, words, f, max_w):
    lines, cur = [], []
    for word, accent in words:
        trial = " ".join(w for w, _ in cur + [(word, accent)])
        if d.textlength(trial, font=f) <= max_w or not cur: cur.append((word, accent))
        else: lines.append(cur); cur = [(word, accent)]
    if cur: lines.append(cur)
    return lines

def logo(path):
    im = Image.new("RGB", (512, 512), PAPER); d = ImageDraw.Draw(im)
    mark(d, 256, 256, 200)
    im.save(path, optimize=True)
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
    items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "og.json")))
    for it in items: card(it["out"], it["title"], it["kicker"]); print("wrote", it["out"])
    logo("img/logo.png"); print("wrote img/logo.png")
