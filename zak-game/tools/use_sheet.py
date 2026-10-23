"""Converte gli sprite ritagliati dal foglio personaggi nei file usati dal gioco
e rigenera art.js con tutte le immagini in art/."""
import json, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
CUT = os.path.join(ROOT, 'art', 'src', 'cut')
SCALE = 55 / 205  # Zak alto 55 px nel gioco; tutti i personaggi alla stessa scala
MAP = {
    'zak_stand': 'r0_0', 'zak_walk0': 'r0_1', 'zak_walk1': 'r0_2', 'zak_back': 'r0_3', 'zak_talk': 'r0_5',
    'annie_stand': 'r1_0', 'annie_walk0': 'r1_1', 'annie_walk1': 'r1_2', 'annie_back': 'r1_3',
    'agente_stand': 'r2_0', 'agente_walk0': 'r2_1', 'agente_back': 'r2_4',
    'scienziato_stand': 'r3_0', 'scienziato_side': 'r3_1',
    'boss': 'r4_0', 'boss_talk': 'r4_1', 'alieno_verde': 'r4_2', 'alieno_blu': 'r4_3',
}

def convert(src):
    im = Image.open(src).convert('RGBA')
    w, h = round(im.width * SCALE), round(im.height * SCALE)
    a = im.getchannel('A').resize((w, h), Image.BOX).point(lambda v: 255 if v > 110 else 0)
    rgb = im.convert('RGB').resize((w, h), Image.BOX).quantize(24, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGBA')
    rgb.putalpha(a)
    return rgb

def write_art_js():
    files = {f[:-4]: 'art/' + f for f in sorted(os.listdir(os.path.join(ROOT, 'art'))) if f.endswith('.png') and not f.startswith('preview')}
    with open(os.path.join(ROOT, 'art.js'), 'w') as f:
        f.write('// Generato da tools/use_sheet.py / make_art.py\nwindow.ART = ' + json.dumps(files) + ';\n')

if __name__ == '__main__':
    for name, cut in MAP.items():
        convert(os.path.join(CUT, cut + '.png')).save(os.path.join(ROOT, 'art', name + '.png'))
    for f in ('zak_walk2', 'zak_walk3'):
        p = os.path.join(ROOT, 'art', f + '.png')
        if os.path.exists(p): os.remove(p)
    write_art_js()
    names = list(MAP)
    ims = [Image.open(os.path.join(ROOT, 'art', n + '.png')) for n in names]
    sheet = Image.new('RGBA', (sum(i.width + 3 for i in ims), 56), (40, 40, 80, 255)); x = 0
    for i in ims: sheet.paste(i, (x, 56 - i.height), i); x += i.width + 3
    sheet.resize((sheet.width * 3, 168), Image.NEAREST).save(os.path.join(ROOT, 'art', 'preview_sprites.png'))
    print('ok')
