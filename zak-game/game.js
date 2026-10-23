// Mini avventura punta-e-clicca in stile SCUMM (grafica originale).
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const VERBS = ['Dai', 'Apri', 'Chiudi', 'Leggi', 'Vai a', 'Prendi', 'Guarda', 'Usa', 'Parla con', 'Accendi', 'Spingi', 'Tira'];
const WALK = 4;
const SCENE_Y = 16, SCENE_H = 136, FLOOR_Y = 140;

ctx.imageSmoothingEnabled = false;
const IMG = {};
for (const [name, src] of Object.entries(ART)) { IMG[name] = new Image(); IMG[name].src = src; }

const state = {
  room: 'casa', verb: 4, sel: null, inv: [], flags: {},
  zak: { x: 200, y: 140, tx: 200, ty: 140, flip: false, frame: 0 }, talker: null, after: null,
  msg: '', msgColor: '#fff', msgT: 0, hover: null, won: false,
};

function say(t, color = '#fff') { state.msg = t; state.msgColor = color; state.msgT = 60 + t.length * 3; state.talker = t.startsWith('CAPO') ? 'boss' : 'zak'; }
function has(i) { return state.inv.includes(i); }
function take(i) { state.inv.push(i); }

// ---------- Stanze ----------
const ROOMS = {
  casa: {
    draw() {
      img('bg_casa', 0, 16, 320, 136);
      if (state.flags.drawerOpen) rect(12, 76, 35, 11, '#1a0c04');
      if (!has('remote')) img('remote', 228, 83);
      if (state.flags.tv) { rect(188, 70, 29, 19, '#3cb4f0'); for (let y = 71; y < 89; y += 2) rect(188, y, 29, 1, (state.t >> 2) % 2 ? '#8ae' : '#6cf'); }
    },
    fg: 'fg_casa', fgY: 148,
    objects: [
      { id: 'porta', name: 'porta', x: 243, y: 35, w: 38, h: 77, wx: 262, wy: 118 },
      { id: 'letto', name: 'letto', x: 0, y: 112, w: 104, h: 36, wx: 116, wy: 140 },
      { id: 'cassetto', name: 'cassetto', x: 8, y: 70, w: 42, h: 46, wx: 62, wy: 118 },
      { id: 'pesce', name: 'pesce rosso', x: 14, y: 50, w: 28, h: 20, wx: 62, wy: 118 },
      { id: 'tv', name: 'televisore', x: 184, y: 56, w: 42, h: 36, wx: 205, wy: 124 },
      { id: 'remote', name: 'telecomando', x: 227, y: 82, w: 9, h: 12, wx: 232, wy: 124, show: () => !has('remote') },
      { id: 'finestra', name: 'finestra', x: 118, y: 28, w: 62, h: 46, wx: 150, wy: 118 },
      { id: 'poster', name: 'poster', x: 58, y: 34, w: 37, h: 35, wx: 76, wy: 118 },
    ],
  },
  ufficio: {
    draw() {
      img('bg_ufficio', 0, 16, 320, 136);
      img('boss', 139, 49 - (state.talker === 'boss' && state.msgT > 0 && (state.t >> 3) % 2));
    },
    fg: 'fg_ufficio', fgY: 121,
    objects: [
      { id: 'capo', name: 'capo', x: 139, y: 49, w: 42, h: 38, wx: 160, wy: 146 },
      { id: 'scrivania', name: 'scrivania', x: 96, y: 86, w: 128, h: 35, wx: 160, wy: 146 },
      { id: 'schedario', name: 'schedario', x: 32, y: 46, w: 31, h: 67, wx: 50, wy: 118 },
      { id: 'giornali', name: 'pila di giornali', x: 2, y: 104, w: 26, h: 36, wx: 40, wy: 136 },
      { id: 'porta2', name: 'porta', x: 259, y: 35, w: 39, h: 77, wx: 276, wy: 118 },
    ],
  },
};

// ---------- Logica delle azioni ----------
function act(verb, obj, item) {
  const v = VERBS[verb], id = obj.id;
  const F = state.flags;
  if (v === 'Chiudi') return say(id === 'cassetto' && F.drawerOpen ? (F.drawerOpen = false, 'Chiuso.') : 'Non è aperto.');
  if (v === 'Leggi') return say(id === 'giornali' ? '"SCOIATTOLO A DUE TESTE TERRORIZZA LA CITTÀ". Il mio capolavoro.' : 'Non c\'è niente da leggere.');
  if (v === 'Guarda') return say({
    porta: 'La porta di casa. Fuori c\'è San Francisco.', letto: 'Il letto non è rifatto da mesi.',
    cassetto: F.drawerOpen ? 'Il cassetto è aperto.' : 'Un cassetto chiuso.',
    pesce: 'Il mio pesce rosso, Sushi. Mi fissa.', tv: F.tv ? 'Notiziario: "Strani tizi con occhiali e naso finto in città..."' : 'È spenta.',
    remote: 'Il telecomando della TV.', finestra: 'Bel tempo. Pessimo per lavorare.',
    capo: 'Il mio capo. Non sorride dal 1974.', scrivania: 'Bozze sullo scoiattolo a due teste.',
    schedario: 'Archivio di notizie improbabili.', poster: 'Un poster di Marte. Chissà com\'è lassù.', giornali: 'Le copie invendute della settimana. Tutte.', porta2: 'Porta verso casa.',
    card: 'Il mio tesserino da giornalista.', kazoo: 'Un kazoo. Strumento nobile.',
  }[id] || 'Niente di speciale.');

  if (v === 'Apri' && id === 'cassetto') {
    if (F.drawerOpen) return say('È già aperto.');
    F.drawerOpen = true; return say('Dentro c\'è un kazoo!');
  }
  if (v === 'Prendi' && id === 'cassetto') {
    if (!F.drawerOpen) return say('Prima dovrei aprirlo.');
    if (has('kazoo')) return say('Il cassetto è vuoto.');
    take('kazoo'); return say('Ho preso il kazoo.');
  }
  if (v === 'Prendi' && id === 'remote') { take('remote'); return say('Preso il telecomando.'); }
  if (v === 'Prendi' && id === 'pesce') return say('Sushi resta dov\'è.');
  if (v === 'Usa' && item === 'remote' && id === 'tv' || v === 'Usa' && id === 'remote' || v === 'Accendi' && id === 'tv') {
    if (v === 'Accendi' && !has('remote')) return say('Il tasto è rotto. Mi serve il telecomando.');
    F.tv = !F.tv; return say(F.tv ? 'La TV si accende. C\'è una pubblicità di tesserini stampa... ah, il mio è sotto il letto!' : 'Spenta.');
  }
  if (v === 'Usa' && item === 'kazoo' && id === 'pesce') return say('Sushi apprezza la musica. Credo.');
  if (v === 'Usa' && id === 'kazoo') return say('Bzzzzz-bzz-bzzz!', '#ff0');
  if ((v === 'Guarda' || v === 'Prendi') && id === 'letto') {
    if (!F.tv) return say('Solo calzini spaiati.');
    if (has('card')) return say('Nient\'altro sotto il letto.');
    take('card'); return say('Trovato il mio tesserino stampa!');
  }
  if ((v === 'Apri' || v === 'Usa' || v === 'Spingi') && (id === 'porta' || id === 'porta2')) {
    if (id === 'porta') { state.room = 'ufficio'; state.zak.x = state.zak.tx = 276; state.zak.y = state.zak.ty = 118; say('Eccomi alla redazione del National Inquisitor.'); }
    else { state.room = 'casa'; state.zak.x = state.zak.tx = 262; state.zak.y = state.zak.ty = 118; }
    return;
  }
  if (v === 'Parla con' && id === 'capo') {
    if (!F.talked) { F.talked = true; return say('CAPO: Zak, Zak, Zak. Mi serve un pezzo sugli alieni. E portami il tuo tesserino!', '#8f8'); }
    return say('CAPO: Senza tesserino non vai da nessuna parte!', '#8f8');
  }
  if (v === 'Dai' && id === 'capo') {
    if (item === 'card') { state.won = true; return say('CAPO: Bene! Parti subito per Seattle. Fine della demo!', '#8f8'); }
    if (item === 'kazoo') return say('CAPO: Che dovrei farci con un kazoo?!', '#8f8');
    return say('Non credo lo voglia.');
  }
  if (v === 'Parla con') return say('Non risponde.');
  say('Non posso farlo.');
}

// ---------- Rendering helpers ----------
function rect(x, y, w, h, c) { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); }
function frame(x, y, w, h, c) { rect(x, y, w, 2, c); rect(x, y + h - 2, w, 2, c); rect(x, y, 2, h, c); rect(x + w - 2, y, 2, h, c); }
function img(n, x, y, w, h) { w ? ctx.drawImage(IMG[n], x, y, w, h) : ctx.drawImage(IMG[n], x, y); }
function spr(n, x, y, flip, sc = 1) {
  const i = IMG[n], k = n.startsWith('zak') ? 55 / i.height : 1, w = Math.round(i.width * sc * k), h = Math.round(i.height * sc * k);
  if (!flip) return ctx.drawImage(i, x, y, w, h);
  ctx.save(); ctx.scale(-1, 1); ctx.drawImage(i, -x - w, y, w, h); ctx.restore();
}
function text(t, x, y, c, s = 1, sh = false) { ctx.font = (10 * s) + "px VT323, monospace"; ctx.textBaseline = 'top';
  if (sh) { ctx.fillStyle = '#000'; for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1]]) ctx.fillText(t, x + dx, y + dy); }
  ctx.fillStyle = c; ctx.font = (10 * s) + "px VT323, monospace"; ctx.textBaseline = 'top'; ctx.fillText(t, x, y); }
function wrap(t, max) {
  const out = []; let line = '';
  for (const w of t.split(' ')) { if ((line + w).length > max) { out.push(line); line = ''; } line += w + ' '; }
  return out.concat(line);
}

function visibleObjs() { return ROOMS[state.room].objects.filter(o => !o.show || o.show()); }

// Inventario in basso a destra, verbi a sinistra
function verbRect(i) { return { x: 4 + (i % 3) * 52, y: 163 + Math.floor(i / 3) * 9, w: 50, h: 9 }; }
function invRect(i) { return { x: 162 + (i % 5) * 31, y: 163 + Math.floor(i / 5) * 18, w: 29, h: 16 }; }
const inside = (p, r) => p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h;

function sentence() {
  let s = VERBS[state.verb];
  if (state.sel) s += ' ' + names[state.sel] + (VERBS[state.verb] === 'Dai' ? ' a' : ' con');
  if (state.hover) s += ' ' + state.hover;
  return s;
}
const names = { card: 'tesserino', kazoo: 'kazoo', remote: 'telecomando' };

function draw() {
  if (!Object.values(IMG).every(i => i.complete)) return;
  rect(0, 0, 320, 200, '#000');
  const R = ROOMS[state.room]; R.draw();
  const z = state.zak, moving = z.x !== z.tx || z.y !== z.ty;
  const talking = state.talker === 'zak' && state.msgT > 0 && !moving;
  const fr = moving ? (z.up ? 'zak_back' : 'zak_walk' + (Math.floor(z.frame / 8) % 2))
    : talking && (state.t >> 4) % 2 ? 'zak_talk' : 'zak_stand';
  const sc = 0.78 + (z.y - 112) / 38 * 0.22;
  if (z.y >= R.fgY) img(R.fg, 0, 16, 320, 136);
  ctx.fillStyle = '#0005'; ctx.beginPath(); ctx.ellipse(z.x, z.y, 9 * sc, 2.5 * sc, 0, 0, 7); ctx.fill();
  spr(fr, Math.round(z.x - IMG[fr].width * 55 / IMG[fr].height * sc / 2), Math.round(z.y - 55 * sc), z.flip && fr !== 'zak_back' && fr !== 'zak_stand', sc);
  if (z.y < R.fgY) img(R.fg, 0, 16, 320, 136);
  if (state.msgT > 0) {
    const lines = wrap(state.msg, 52), cx = state.talker === 'boss' ? 160 : z.x;
    const ty = state.talker === 'boss' ? 20 : Math.max(2, z.y - 55 * sc - lines.length * 9 - 2);
    ctx.font = '10px VT323, monospace'; lines.forEach((l, i) => { const w = ctx.measureText(l).width; text(l, Math.max(2, Math.min(318 - w, cx - w / 2)), ty + i * 10, state.msgColor, 1, true); });
  }
  rect(0, 152, 320, 48, '#000');
  ctx.font = '10px VT323, monospace'; text(sentence(), 160 - ctx.measureText(sentence()).width / 2, 152, '#c8f', 1);
  VERBS.forEach((v, i) => { const r = verbRect(i); text(v, r.x, r.y, i === state.verb ? '#ff4' : '#5d5'); });
  rect(160, 161, 158, 38, '#101018');
  state.inv.forEach((it, i) => { const r = invRect(i); rect(r.x, r.y, r.w, r.h, state.sel === it ? '#557' : '#223'); img(it, r.x + ((r.w - IMG[it].width) >> 1), r.y + ((r.h - IMG[it].height) >> 1)); });
  if (state.won) { rect(70, 64, 180, 24, '#000c'); text('*** FINE DELLA DEMO ***', 104, 72, '#ff0'); }
}

function tick() {
  const z = state.zak; state.t = (state.t || 0) + 1;
  if (z.x !== z.tx || z.y !== z.ty) {
    const dx = z.tx - z.x, dy = z.ty - z.y, d = Math.hypot(dx, dy), v = 1.3;
    if (Math.abs(dx) > 0.5) z.flip = dx < 0;
    z.up = dy < 0 && Math.abs(dy) * 1.5 > Math.abs(dx);
    if (d <= v) { z.x = z.tx; z.y = z.ty; } else { z.x += dx / d * v; z.y += dy / d * v * 0.6; }
    z.frame++;
    if (z.x === z.tx && z.y === z.ty && state.after) { const a = state.after; state.after = null; a(); }
  }
  if (state.msgT > 0) state.msgT--;
  draw(); requestAnimationFrame(tick);
}

function pt(e) { const b = cv.getBoundingClientRect(); return { x: (e.clientX - b.left) * 320 / b.width, y: (e.clientY - b.top) * 200 / b.height }; }
cv.addEventListener('mousemove', e => {
  const p = pt(e); state.hover = null;
  const o = visibleObjs().find(o => inside(p, o)); if (o) state.hover = o.name;
  state.inv.forEach((it, i) => { if (inside(p, invRect(i))) state.hover = names[it]; });
});
cv.addEventListener('click', e => {
  const p = pt(e);
  for (let i = 0; i < VERBS.length; i++) if (inside(p, verbRect(i))) { state.verb = i; state.sel = null; return; }
  for (let i = 0; i < state.inv.length; i++) if (inside(p, invRect(i))) {
    const it = state.inv[i], v = VERBS[state.verb];
    if ((v === 'Usa' || v === 'Dai') && !state.sel) { state.sel = it; return; }
    act(state.verb, { id: it }, state.sel); state.sel = null; state.verb = WALK; return;
  }
  if (p.y < SCENE_Y || p.y >= 152) return;
  const o = visibleObjs().find(o => inside(p, o));
  const z = state.zak;
  if (!o || VERBS[state.verb] === 'Vai a') {
    z.tx = Math.max(12, Math.min(308, o ? o.wx : p.x)); z.ty = Math.max(114, Math.min(150, o ? o.wy : p.y)); state.after = null; return;
  }
  const verb = state.verb, sel = state.sel;
  state.after = () => { act(verb, o, sel); state.sel = null; state.verb = WALK; };
  z.tx = o.wx; z.ty = o.wy; if (z.x === z.tx && z.y === z.ty) { const a = state.after; state.after = null; a(); }
});

say('Un\'altra mattina. Dovrei andare in redazione...');
tick();
