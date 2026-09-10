"""Generate 1200x630 Open Graph cards and a square logo in the First Light palette."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
SF = "/System/Library/Fonts/SFNS.ttf"
PAPER, INK, CLAY, SUB = (248, 246, 241), (28, 27, 25), (201, 97, 61), (107, 104, 98)
def font(size, weight, optical):
    f = ImageFont.truetype(SF, size); f.set_variation_by_axes([100, optical, 400, weight]); return f
def mark(d, cx, cy, r, ink=INK):
    # half sun on a horizon line with three rays, same as the favicon
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=CLAY)
    d.line([cx - r * 1.5, cy, cx + r * 1.5, cy], fill=ink, width=max(3, r // 6))
    for dx, dy in ((0, -1), (-0.7, -0.7), (0.7, -0.7)):
        d.line([cx + dx * r * 1.25, cy + dy * r * 1.25, cx + dx * r * 1.6, cy + dy * r * 1.6], fill=CLAY, width=max(3, r // 5))
def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], []
    for w in words:
        if d.textlength(" ".join(cur + [w]), font=f) <= max_w: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines
def card(path, title, kicker):
    im = Image.new("RGB", (1200, 630), PAPER); d = ImageDraw.Draw(im)
    mark(d, 96, 96, 26)
    d.text((140, 74), "First Light", font=font(30, 700, 28), fill=INK)
    d.text((80, 168), kicker.upper(), font=font(20, 700, 20), fill=CLAY)
    size = 64
    while True:
        f = font(size, 720, 60); lines = wrap(d, title, f, 1040)
        if len(lines) <= 3 or size <= 44: break
        size -= 4
    y = 212
    for ln in lines:
        d.text((80, y), ln, font=f, fill=INK); y += int(size * 1.18)
    d.text((80, 556), "firstlightalarm.com", font=font(22, 500, 20), fill=SUB)
    d.rectangle([0, 622, 1200, 630], fill=CLAY)
    im.save(path, optimize=True)
def logo(path):
    im = Image.new("RGB", (512, 512), PAPER); d = ImageDraw.Draw(im)
    mark(d, 256, 300, 120)
    im.save(path, optimize=True)
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
    items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "og.json")))
    for it in items: card(it["out"], it["title"], it["kicker"]); print("wrote", it["out"])
    logo("img/logo.png"); print("wrote img/logo.png")
