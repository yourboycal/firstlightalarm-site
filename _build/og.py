"""Generate 1200x630 Open Graph cards and a square logo in the First Step palette."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
SF = "/System/Library/Fonts/SFNS.ttf"
PAPER, INK, CLAY, SUB = (248, 246, 241), (28, 27, 25), (201, 97, 61), (107, 104, 98)
def font(size, weight, optical):
    f = ImageFont.truetype(SF, size); f.set_variation_by_axes([100, optical, 400, weight]); return f
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
    im = Image.new("RGB", (1200, 630), PAPER); d = ImageDraw.Draw(im)
    mark(d, 96, 96, 44)
    d.text((140, 74), "First Step", font=font(30, 700, 28), fill=INK)
    d.text((80, 168), kicker.upper(), font=font(20, 700, 20), fill=CLAY)
    size = 64
    while True:
        f = font(size, 720, 60); lines = wrap(d, title, f, 1040)
        if len(lines) <= 3 or size <= 44: break
        size -= 4
    y = 212
    for ln in lines:
        d.text((80, y), ln, font=f, fill=INK); y += int(size * 1.18)
    d.text((80, 556), "firststepalarm.com", font=font(22, 500, 20), fill=SUB)
    d.rectangle([0, 622, 1200, 630], fill=CLAY)
    im.save(path, optimize=True)
def logo(path):
    im = Image.new("RGB", (512, 512), PAPER); d = ImageDraw.Draw(im)
    mark(d, 256, 256, 200)
    im.save(path, optimize=True)
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
    items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "og.json")))
    for it in items: card(it["out"], it["title"], it["kicker"]); print("wrote", it["out"])
    logo("img/logo.png"); print("wrote img/logo.png")
