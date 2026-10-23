# Zak: Avventura in Redazione

Mini avventura punta-e-clicca ispirata allo stile SCUMM di *Zak McKracken*.
Tutta la grafica è **originale** (sfondi in prospettiva con retinatura, sprite ombreggiati, generati da `tools/make_art.py`):
nessun asset del gioco LucasArts è incluso.

- Gioca: apri `index.html` nel browser.
- Rigenera la grafica: `python3 tools/make_art.py` → `art/*.png` e `art.js`.
- Anteprima sprite: `art/preview_sprites.png`.

Soluzione: accendi la TV con il telecomando, guarda sotto il letto, vai in
redazione, parla col capo e dagli il tesserino.

## Usare grafica tua o generata con AI

Il motore carica le immagini da `art/` per nome. Per sostituirne una, crea l'immagine
e convertila con `tools/import_art.py`: la ridimensiona, riduce i colori e rende
trasparente lo sfondo degli sprite.

| File | Cosa | Formato da generare |
|---|---|---|
| `bg_casa`, `bg_ufficio` | sfondo stanza | orizzontale, circa 2.35:1 (es. 1600x680), pavimento nel terzo inferiore |
| `fg_casa`, `fg_ufficio` | oggetti in primo piano (letto, scrivania) | stessa misura dello sfondo, PNG trasparente |
| `zak_stand` | Zak fermo | figura intera su fondo verde #00ff00 |
| `zak_walk0..3` | camminata | 4 pose affiancate in un'unica immagine (`foglio`) |
| `boss`, `boss_talk` | capo a bocca chiusa / aperta | busto su fondo verde |
| `card`, `kazoo`, `remote` | icone inventario | oggetto su fondo verde |

Comandi:

```
python3 tools/import_art.py sfondo  camera.png        bg_casa
python3 tools/import_art.py sprite  zak.png           zak_stand --altezza 55
python3 tools/import_art.py foglio  zak_cammina.png   zak_walk  --fotogrammi 4
python3 tools/import_art.py sprite  capo.png          boss      --altezza 46
```

Prompt d'esempio per un generatore di immagini:

- *Sfondo:* "1990 point-and-click adventure game background, FM Towns 256-color pixel art,
  hand-painted look, side view of a messy 1990s apartment bedroom in San Francisco: wooden
  wall panels, window with blue sky, purple carpet, unmade bed with green blanket, small CRT
  TV on a wooden table, dresser with goldfish bowl, door on the right, no characters,
  wide 2.35:1"
- *Personaggio:* "full body pixel art sprite of a young tabloid reporter, brown messy hair,
  blue jacket, white shirt, red tie, grey trousers, 3/4 front view standing, 1990 LucasArts
  adventure style, 256 colors, plain #00ff00 background"
- *Camminata:* stesso prompt + "walk cycle, 4 frames side by side, side view, same size".

Usa uno stile ispirato, non immagini del gioco originale: la grafica di Zak McKracken è
protetta da copyright.
