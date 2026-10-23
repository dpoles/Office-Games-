"""Genera tutta la grafica originale del gioco (sfondi, primi piani, personaggi, oggetti).
Uso: python3 tools/make_art.py  ->  art/*.png e art.js"""
import json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'art')
W, H = 320, 136
OUTLINE = (22, 14, 26, 255)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
random.seed(7)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def dgrad(im, box, c1, c2, vertical=True, steps=6):
    """Sfumatura a bande con retinatura ordinata (look VGA/FM-Towns)."""
    x0, y0, x1, y1 = box
    px = im.load()
    n = (y1 - y0) if vertical else (x1 - x0)
    for y in range(y0, y1):
        for x in range(x0, x1):
            t = ((y - y0) if vertical else (x - x0)) / max(1, n - 1) * steps
            b = int(t); f = t - b
            if BAYER[y % 4][x % 4] / 16 < f: b += 1
            px[x, y] = lerp(c1, c2, min(b, steps) / steps) + (255,)

def shade_box(d, box, base, hi, lo, edge=2):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=base)
    d.rectangle((x0, y0, x1, y0 + edge - 1), fill=hi)
    d.rectangle((x0, y0, x0 + edge - 1, y1), fill=hi)
    d.rectangle((x0, y1 - edge + 1, x1, y1), fill=lo)
    d.rectangle((x1 - edge + 1, y0, x1, y1), fill=lo)

def wood(im, box, c, dark):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=c)
    for y in range(y0, y1 + 1, 3):
        off = random.randint(0, 20)
        for x in range(x0 + off, x1, random.randint(18, 40)):
            d.line((x, y, min(x1, x + random.randint(4, 14)), y), fill=dark)

def outline(im):
    px = im.load(); w, h = im.size
    pts = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] == 0 and any(
        0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] and px[x + dx, y + dy] != OUTLINE
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in pts: px[p] = OUTLINE
    return im

def room_shell(im, wall1, wall2, floorfn):
    """Parete di fondo, pareti laterali in prospettiva, pavimento."""
    d = ImageDraw.Draw(im)
    dgrad(im, (0, 0, W, 96), wall1, wall2)
    floorfn(im)
    d.polygon([(0, 0), (26, 0), (26, 96), (0, 120)], fill=lerp(wall2, (0, 0, 0), .35))
    d.polygon([(W, 0), (W - 26, 0), (W - 26, 96), (W, 120)], fill=lerp(wall2, (0, 0, 0), .35))
    d.line((26, 0, 26, 96), fill=lerp(wall2, (0, 0, 0), .55)); d.line((W - 27, 0, W - 27, 96), fill=lerp(wall2, (0, 0, 0), .55))
    d.line((26, 96, 0, 120), fill=(0, 0, 0)); d.line((W - 27, 96, W, 120), fill=(0, 0, 0))
    d.rectangle((26, 90, W - 27, 96), fill=lerp(wall2, (0, 0, 0), .5))  # battiscopa
    d.line((26, 90, W - 27, 90), fill=lerp(wall1, (255, 255, 255), .2))
    return d

def persp_floor(im, c1, c2, tile, line):
    dgrad(im, (0, 96, W, H), c1, c2, steps=4)
    d = ImageDraw.Draw(im)
    for i in range(-12, 13):
        d.line((160 + i * 14, 96, 160 + i * 26, H), fill=line)
    y = 96.0; k = 4.0
    while y < H:
        d.line((0, int(y), W, int(y)), fill=line); y += k; k *= 1.35
    if tile:
        px = im.load()
        for y in range(97, H, 2):
            for x in range((y // 2) % 2 * 3, W, 6): px[x, y] = tile + (255,)

def window(d, im, box, sky1, sky2, city=False):
    x0, y0, x1, y1 = box
    shade_box(d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), (120, 72, 36), (168, 112, 60), (70, 38, 16))
    dgrad(im, (x0, y0, x1, y1), sky1, sky2)
    d = ImageDraw.Draw(im)
    if city:
        random.seed(3)
        x = x0
        while x < x1:
            bw = random.randint(10, 20); bh = random.randint(14, y1 - y0 - 8)
            col = random.choice([(96, 118, 156), (120, 140, 176), (80, 98, 136)])
            d.rectangle((x, y1 - bh, min(x1, x + bw), y1), fill=col)
            d.line((x, y1 - bh, x, y1), fill=lerp(col, (255, 255, 255), .3))
            for wy in range(y1 - bh + 3, y1 - 2, 4):
                for wx in range(x + 2, min(x1, x + bw) - 1, 3): d.point((wx, wy), fill=(220, 230, 170))
            x += bw + 1
    else:
        for cx, cy in ((x0 + 10, y0 + 12), (x0 + 30, y0 + 8)):
            d.ellipse((cx, cy, cx + 14, cy + 5), fill=(250, 250, 255)); d.ellipse((cx + 5, cy - 3, cx + 13, cy + 3), fill=(250, 250, 255))
        d.rectangle((x0, y1 - 8, x1, y1), fill=(70, 120, 60))
        d.rectangle((x0 + 8, y1 - 16, x0 + 16, y1 - 8), fill=(170, 110, 90))
    mx = (x0 + x1) // 2
    d.rectangle((mx - 1, y0, mx + 1, y1), fill=(120, 72, 36)); d.rectangle((x0, (y0 + y1) // 2 - 1, x1, (y0 + y1) // 2), fill=(120, 72, 36))
    d.rectangle((x0 - 6, y1 + 4, x1 + 6, y1 + 7), fill=(150, 96, 50))

def door(d, box):
    x0, y0, x1, y1 = box
    shade_box(d, (x0 - 3, y0 - 3, x1 + 3, y1), (100, 60, 30), (150, 100, 56), (56, 30, 12))
    shade_box(d, box, (132, 78, 38), (170, 110, 60), (86, 46, 20))
    for py in (y0 + 6, y0 + 40):
        shade_box(d, (x0 + 5, py, x1 - 5, py + 28), (120, 70, 34), (86, 46, 20), (168, 108, 58), 1)
    d.ellipse((x1 - 9, y0 + 36, x1 - 5, y0 + 40), fill=(240, 200, 70), outline=(120, 90, 20))

# ---------------- CASA DI ZAK ----------------
def casa():
    im = Image.new('RGBA', (W, H))
    room_shell(im, (196, 128, 84), (150, 90, 54),
               lambda im: persp_floor(im, (70, 54, 170), (42, 30, 120), (96, 80, 200), (52, 40, 140)))
    d = ImageDraw.Draw(im)
    for x in range(40, W - 30, 22): d.line((x, 0, x, 89), fill=(176, 112, 70))  # carta da parati
    window(d, im, (122, 16, 176, 54), (110, 170, 240), (190, 220, 250))
    door(d, (246, 22, 278, 95))
    # poster
    shade_box(d, (58, 18, 94, 52), (30, 20, 60), (60, 40, 110), (10, 6, 20), 1)
    d.ellipse((66, 24, 86, 44), fill=(230, 120, 40)); d.ellipse((70, 28, 78, 34), fill=(250, 180, 90))
    d.line((60, 48, 92, 48), fill=(250, 230, 120))
    # orologio
    d.ellipse((196, 14, 210, 28), fill=(240, 236, 220), outline=(60, 40, 20)); d.line((203, 21, 203, 16), fill=(0, 0, 0)); d.line((203, 21, 207, 21), fill=(0, 0, 0))
    # cassettiera + boccia
    wood(im, (8, 54, 50, 100), (150, 92, 46), (124, 72, 34)); d = ImageDraw.Draw(im)
    shade_box(d, (8, 52, 50, 56), (180, 120, 70), (210, 150, 100), (120, 72, 34), 1)
    for i, y in enumerate((60, 74, 88)):
        shade_box(d, (12, y, 46, y + 10), (136, 82, 40), (176, 116, 66), (90, 50, 22), 1)
        d.rectangle((26, y + 4, 32, y + 5), fill=(230, 200, 90))
    d.ellipse((14, 34, 42, 54), fill=(150, 210, 240), outline=(80, 140, 180))
    d.rectangle((14, 34, 42, 38), fill=(0, 0, 0, 0)); d.line((17, 38, 39, 38), fill=(200, 240, 255))
    d.ellipse((24, 42, 32, 48), fill=(250, 130, 30)); d.polygon([(32, 45), (36, 42), (36, 48)], fill=(250, 130, 30)); d.point((26, 44), fill=(0, 0, 0))
    d.arc((18, 38, 30, 52), 160, 220, fill=(255, 255, 255))
    # tavolo + TV
    wood(im, (176, 76, 240, 80), (140, 60, 36), (110, 44, 26)); d = ImageDraw.Draw(im)
    d.line((176, 76, 240, 76), fill=(190, 100, 60))
    for lx in (180, 234): shade_box(d, (lx, 81, lx + 3, 104), (110, 44, 26), (150, 70, 40), (70, 26, 14), 1)
    shade_box(d, (184, 50, 226, 76), (70, 70, 78), (120, 120, 132), (34, 34, 40))
    d.rectangle((188, 54, 216, 72), fill=(30, 40, 50)); d.line((190, 56, 196, 56), fill=(90, 110, 130))
    for ky in (56, 62, 68): d.ellipse((219, ky, 223, ky + 4), fill=(170, 170, 180))
    d.line((196, 50, 188, 40), fill=(150, 150, 160)); d.line((214, 50, 222, 40), fill=(150, 150, 160))
    # pianta
    shade_box(d, (150, 84, 166, 100), (190, 90, 50), (230, 130, 80), (130, 56, 30), 1)
    for a in range(-70, 80, 25):
        r = math.radians(a - 90); d.line((158, 84, 158 + 16 * math.cos(r), 84 + 18 * math.sin(r)), fill=(40, 130, 50), width=2)
    # letto (primo piano, va sopra Zak) -> livello separato
    fg = Image.new('RGBA', (W, H)); f = ImageDraw.Draw(fg)
    shade_box(f, (0, 96, 104, 132), (120, 70, 36), (170, 110, 60), (70, 36, 14))
    shade_box(f, (2, 98, 30, 112), (240, 240, 245), (255, 255, 255), (190, 190, 210))
    f.rectangle((28, 98, 102, 120), fill=(50, 160, 70))
    for x in range(30, 102, 6): f.line((x, 98, x + 2, 120), fill=(40, 130, 56))
    f.line((28, 98, 102, 98), fill=(110, 210, 120)); f.rectangle((28, 118, 102, 121), fill=(30, 100, 44))
    f.rectangle((0, 96, 4, 132), fill=(86, 46, 20))
    return im, fg

# ---------------- REDAZIONE ----------------
def ufficio():
    im = Image.new('RGBA', (W, H))
    room_shell(im, (226, 196, 120), (176, 140, 74),
               lambda im: persp_floor(im, (70, 150, 96), (34, 100, 60), (200, 230, 200), (40, 110, 66)))
    d = ImageDraw.Draw(im)
    # boiserie
    wood(im, (26, 64, W - 27, 89), (150, 100, 50), (126, 80, 36)); d = ImageDraw.Draw(im)
    d.line((26, 64, W - 27, 64), fill=(200, 150, 90))
    for x in range(36, W - 30, 36): shade_box(d, (x, 68, x + 28, 86), (140, 92, 44), (110, 70, 30), (180, 130, 76), 1)
    window(d, im, (94, 12, 226, 56), (150, 190, 240), (230, 236, 250), city=True)
    d.rectangle((104, 14, 216, 22), fill=(240, 240, 250)); 
    door(d, (262, 22, 294, 95))
    # schedario metallico
    dgrad(im, (32, 30, 62, 96), (190, 190, 205), (120, 120, 140), vertical=False, steps=5); d = ImageDraw.Draw(im)
    d.rectangle((32, 30, 62, 96), outline=(60, 60, 76))
    for y in (34, 54, 74):
        shade_box(d, (35, y, 59, y + 17), (170, 170, 184), (220, 220, 230), (100, 100, 116), 1)
        d.rectangle((43, y + 7, 51, y + 9), fill=(80, 80, 90))
    # pile di giornali
    for i in range(8): shade_box(d, (4 + i % 2, 120 - i * 4, 26, 123 - i * 4), (236, 232, 214), (255, 255, 250), (180, 176, 160), 1)
    # vaso
    d.ellipse((236, 72, 256, 96), fill=(236, 236, 240), outline=(140, 140, 160)); d.arc((240, 76, 252, 92), 200, 280, fill=(255, 255, 255))
    # quadro
    shade_box(d, (56, 10, 82, 32), (200, 160, 50), (250, 210, 90), (140, 100, 20), 2)
    d.rectangle((60, 14, 78, 28), fill=(90, 140, 90)); d.ellipse((65, 16, 73, 24), fill=(240, 190, 150))
    # scrivania (primo piano: davanti al capo)
    fg = Image.new('RGBA', (W, H))
    wood(fg, (96, 70, 224, 76), (130, 74, 36), (104, 56, 26)); f = ImageDraw.Draw(fg)
    f.line((96, 70, 224, 70), fill=(190, 120, 70))
    wood(fg, (100, 77, 220, 104), (110, 60, 28), (88, 46, 20)); f = ImageDraw.Draw(fg)
    for x in (100, 196): shade_box(f, (x, 78, x + 24, 104), (120, 66, 30), (160, 100, 56), (70, 36, 14), 1)
    shade_box(f, (114, 64, 138, 70), (246, 246, 236), (255, 255, 255), (190, 190, 180), 1)
    f.rectangle((176, 60, 190, 70), fill=(40, 40, 44)); f.ellipse((178, 58, 188, 63), fill=(70, 70, 76))
    f.rectangle((152, 66, 168, 70), fill=(60, 120, 200))
    return im, fg

SK = (246, 196, 156)

# ---------------- OGGETTI (icone inventario) ----------------
PAL = {'k': (20, 16, 24), 's': SK, 'h': (124, 66, 30), 'b': (56, 110, 226), 'w': (245, 245, 245),
       'g': (60, 60, 70), 'r': (210, 30, 40), 'y': (240, 210, 60), 'Y': (190, 150, 30), 'm': (170, 170, 180)}
ITEMS = {
    'card': ["kkkkkkkkkkkkkk", "kwwwwwwwwwwwwk", "kwhhhwwrrrrrwk", "kwsssswwwwwwwk", "kwbbbbwkkkkkwk",
             "kwbbbbwwwwwwwk", "kwwwwwwkkkkkwk", "kkkkkkkkkkkkkk"],
    'kazoo': ["............kk", "........kkkkYk", "...kkkkkyyyyyk", ".kkyyyyyyyyykk", "kyyyyyyyykkk..",
              "kYYYYYYkk.....", "kkkkkkk......."],
    'remote': [".kkkkk.", "kgggggk", "kgrgggk", "kgggggk", "kgmgmgk", "kgggggk", "kgmgmgk", "kgggggk",
               "kgmgmgk", "kgggggk", ".kkkkk."],
}
def item(rows):
    im = Image.new('RGBA', (len(rows[0]), len(rows)))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL: im.putpixel((x, y), PAL[ch] + (255,))
    return im

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    files = {}
    def save(name, im): im.save(os.path.join(OUT, name + '.png')); files[name] = 'art/' + name + '.png'
    for n, fn in (('casa', casa), ('ufficio', ufficio)):
        bg, fg = fn(); save('bg_' + n, bg); save('fg_' + n, fg)
    for k, v in ITEMS.items(): save(k, item(v))
    # i personaggi vengono dal foglio in art/src (vedi tools/use_sheet.py)
    import use_sheet; use_sheet.write_art_js()
    print('ok')
