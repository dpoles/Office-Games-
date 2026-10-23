"""Ritaglia un foglio di sprite su sfondo uniforme in singoli PNG trasparenti.
Uso: python3 tools/slice_sheet.py art/src/personaggi.jpg   -> art/src/cut/r<riga>_<n>.png"""
import os, sys
from PIL import Image

def main(path, tol=70):
    im = Image.open(path).convert('RGB'); W, H = im.size; px = im.load()
    bg = px[2, 2]
    mask = [[sum(abs(a - b) for a, b in zip(px[x, y], bg)) > tol for x in range(W)] for y in range(H)]
    seen = [[False] * W for _ in range(H)]; boxes = []
    for y in range(H):
        for x in range(W):
            if mask[y][x] and not seen[y][x]:
                st = [(x, y)]; seen[y][x] = True; x0 = x1 = x; y0 = y1 = y; n = 0
                while st:
                    cx, cy = st.pop(); n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < W and 0 <= ny < H and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True; st.append((nx, ny))
                if n > 400: boxes.append([x0, y0, x1, y1])
    # unisce pezzi che si sovrappongono in orizzontale nella stessa riga (es. capelli staccati)
    boxes.sort(key=lambda b: (b[1] + b[3]) // 2)
    rows = []
    for b in boxes:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - rows[-1][0]) < 90: rows[-1][1].append(b)
        else: rows.append([cy, [b]])
    out = os.path.join(os.path.dirname(path), 'cut'); os.makedirs(out, exist_ok=True)
    for r, (_, bs) in enumerate(rows):
        bs.sort(); merged = []
        for b in bs:
            if merged and b[0] <= merged[-1][2] + 4:
                m = merged[-1]; merged[-1] = [min(m[0], b[0]), min(m[1], b[1]), max(m[2], b[2]), max(m[3], b[3])]
            else: merged.append(b)
        for i, (x0, y0, x1, y1) in enumerate(merged):
            c = im.crop((x0, y0, x1 + 1, y1 + 1)).convert('RGBA'); cp = c.load()
            for yy in range(c.height):
                for xx in range(c.width):
                    if not mask[y0 + yy][x0 + xx]: cp[xx, yy] = (0, 0, 0, 0)
            c.save(os.path.join(out, 'r%d_%d.png' % (r, i)))
            print('r%d_%d' % (r, i), c.size)

if __name__ == '__main__':
    main(sys.argv[1])
