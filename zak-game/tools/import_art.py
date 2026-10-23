"""Importa un'immagine qualsiasi (disegno, foto, output di un generatore AI) nel gioco,
convertendola nel formato e nello stile del motore (320x136, max 256 colori, pixel netti).

Esempi:
  python3 tools/import_art.py sfondo mia_camera.png bg_casa
  python3 tools/import_art.py sprite zak_ai.png zak_stand --altezza 55
  python3 tools/import_art.py foglio zak_camminata.png zak_walk --fotogrammi 4 --altezza 55

Per gli sprite lo sfondo viene reso trasparente: usa un fondo verde (#00ff00) o magenta
(#ff00ff) uniforme, oppure un PNG già trasparente.
"""
import argparse, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')

def quantize(im, colors):
    a = im.getchannel('A') if im.mode == 'RGBA' else None
    q = im.convert('RGB').quantize(colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGBA')
    if a: q.putalpha(a.point(lambda v: 255 if v > 128 else 0))
    return q

def key_out(im, tol=60):
    im = im.convert('RGBA'); px = im.load()
    bg = px[0, 0][:3]
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 128 or sum(abs(c - k) for c, k in zip((r, g, b), bg)) < tol: px[x, y] = (0, 0, 0, 0)
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im

def to_height(im, h):
    w = max(1, round(im.width * h / im.height))
    return im.resize((w, h), Image.LANCZOS)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('tipo', choices=['sfondo', 'primopiano', 'sprite', 'foglio'])
    p.add_argument('file'); p.add_argument('nome')
    p.add_argument('--altezza', type=int, default=55)
    p.add_argument('--fotogrammi', type=int, default=4)
    p.add_argument('--colori', type=int, default=0)
    a = p.parse_args()
    src = Image.open(a.file).convert('RGBA')
    out = {}
    if a.tipo in ('sfondo', 'primopiano'):
        im = src if a.tipo == 'sfondo' else key_out(src) if src.getpixel((0, 0))[3] else src
        if a.tipo == 'primopiano': im = src
        out[a.nome] = quantize(im.resize((320, 136), Image.LANCZOS), a.colori or 128)
    elif a.tipo == 'sprite':
        out[a.nome] = quantize(to_height(key_out(src), a.altezza), a.colori or 32)
    else:
        fw = src.width // a.fotogrammi
        frames = [key_out(src.crop((i * fw, 0, (i + 1) * fw, src.height))) for i in range(a.fotogrammi)]
        mh = max(f.height for f in frames)
        for i, f in enumerate(frames):
            h = round(a.altezza * f.height / mh)
            out['%s%d' % (a.nome, i)] = quantize(to_height(f, h), a.colori or 32)
    for n, im in out.items():
        path = os.path.join(ROOT, 'art', n + '.png'); im.save(path); print('salvato', path, im.size)

if __name__ == '__main__':
    main()
