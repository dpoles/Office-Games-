"""Genera gli sprite originali (pixel art) del gioco.
Output: sprites/*.png (ingranditi x4 e 1:1) e sprites.js usato dal gioco."""
import json, os
from PIL import Image

PAL = {
    'k': (20, 16, 24), 's': (240, 184, 140), 'S': (200, 136, 100), 'h': (110, 60, 30),
    'H': (70, 36, 16), 'e': (30, 30, 60), 'b': (40, 90, 210), 'B': (24, 50, 140),
    'w': (240, 240, 240), 'p': (60, 60, 70), 'P': (36, 36, 44), 'o': (90, 50, 30),
    'g': (40, 40, 48), 'G': (80, 80, 96), 'r': (200, 30, 40), 'y': (240, 210, 60),
    'c': (120, 200, 230), 'n': (230, 120, 40), 'm': (150, 150, 160),
}

ZAK_TOP = [
    "....kkkkkk......",
    "...khhhhhhk.....",
    "..khhhhhhhhk....",
    "..khhHsssshk....",
    "..khHsesseshk...",
    "..khHssssssk....",
    "...kHssSssk.....",
    "....kssrssk.....",
    ".....kssssk.....",
    "....kkwwwwkk....",
    "...kbbwwwwbbk...",
    "..kbbbwrrwbbbk..",
    "..kbBbwrrwbBbk..",
    "..kbBbwrrwbBbk..",
    "..kbBbwwwwbBbk..",
    "..ksBbbbbbbBsk..",
    "..kskbbbbbbksk..",
    "...k.kBBBBk.k...",
    ".....kpppppk....",
    ".....kppkppk....",
]
ZAK_LEGS = {
    'stand': ["....kppkppk.....", "....kppkppk.....", "....kppkppk.....", "....kppkppk.....",
              "....kppkppk.....", "....kPpkPpk.....", "....kPpkPpk.....", "....kPpkPpk.....",
              "....kooko ok....".replace(' ', 'o'), "...kooookoook...", "...kkkkkkkkkk...", "................"],
    'walk1': ["....kppkkppk....", "...kppk..kppk...", "...kppk..kppk...", "..kppk....kppk..",
              "..kppk....kPpk..", "..kPpk....kPpk..", ".kPpk......kPpk.", ".kPpk......kPpk.",
              ".kook......kook.", "kooook....kooook", "kkkkkk....kkkkkk", "................"],
    'walk2': ["....kppkppk.....", "....kppkppk.....", "....kppkkpk.....", "....kppk.kpk....",
              "....kppk.kPpk...", "....kPpk..kPk...", "....kPpk..kPk...", "....kPpk..kPk...",
              "....kook..kook..", "...kooook.kooook", "...kkkkkk.kkkkkk", "................"],
}

BOSS = [
    ".......kkkkkkkk.........",
    "......kssssssssk........",
    ".....kssssssssssk.......",
    ".....ksSssssssSsk.......",
    "....ksseesssseessk......",
    "....kssssssssssssk......",
    "....kSsssSSSSsssSk......",
    ".....ksssrrrrsssk.......",
    "......kSssssssSk........",
    ".....kkkkswwskkkk.......",
    "...kkggggwwwwggggkk.....",
    "..kgggggGwrrwGgggggk....",
    ".kggggggGwrrwGggggggk...",
    ".kgggGggGwrrwGggGgggk...",
    "kggggGgggwrrwgggGggggk..",
    "kggggGgggwwwwgggGggggk..",
    "kggggGggggggggggGggggk..",
    "kssggGggggggggggGggssk..",
    "kssggGggggyggggggGgssk..",
    ".kk.kggggggggggggk.kk...",
    "....kggggggggggggk......",
    "....kgggggkkggggggk.....",
    "....kgggggk.kgggggk.....",
    "....kgggggk.kgggggk.....",
    "....kgggggk.kgggggk.....",
    "....kPPPPPk.kPPPPPk.....",
    "...kkkkkkkk.kkkkkkkk....",
]

ITEMS = {
    'card': ["kkkkkkkkkkkk", "kwwwwwwwwwwk", "kwssk.wrrrwk".replace('.', 'w'), "kwhhkwwwwwwk",
             "kwbbkwkkkkwk", "kwwwwwwwwwwk", "kwkkkkkkkkwk", "kkkkkkkkkkkk"],
    'kazoo': ["..........kk", "......kkkkyk", "..kkkkyyyyyk", "kkyyyyyyyykk",
              "kyyyyyyykk..", "kkkkkkkkk..."],
    'remote': [".kkkkk.", "kgggggk", "kgrgggk", "kgggggk", "kgmgmgk", "kgggggk",
               "kgmgmgk", "kgggggk", "kgmgmgk", ".kkkkk."],
    'fish': ["...kkkkkk...", "..kccccccck.".replace('ck.', 'k.'), ".kcccccccck.", "kcccnnccccck",
             "kccnnnnckcck", "kcccnnccccck", ".kcccccccck.", "..kkkkkkkk.."],
}

def norm(rows, w=None):
    w = w or max(len(r) for r in rows)
    return [r.ljust(w, '.')[:w] for r in rows]

def build():
    sprites = {}
    for name, legs in ZAK_LEGS.items():
        sprites['zak_' + name] = norm(ZAK_TOP + legs, 16)
    sprites['boss'] = norm(BOSS, 24)
    for k, v in ITEMS.items():
        sprites[k] = norm(v)
    return sprites

def to_img(rows, scale=1):
    im = Image.new('RGBA', (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                im.putpixel((x, y), PAL[ch] + (255,))
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST) if scale > 1 else im

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(__file__), '..')
    sp = build()
    for n, rows in sp.items():
        to_img(rows).save(os.path.join(root, 'sprites', n + '.png'))
        to_img(rows, 4).save(os.path.join(root, 'sprites', n + '@4x.png'))
    with open(os.path.join(root, 'sprites.js'), 'w') as f:
        f.write('// Generato da tools/make_sprites.py - non modificare a mano\n')
        f.write('window.PALETTE = ' + json.dumps({k: '#%02x%02x%02x' % v for k, v in PAL.items()}) + ';\n')
        f.write('window.SPRITES = ' + json.dumps(sp, indent=0) + ';\n')
    print('ok', list(sp))
