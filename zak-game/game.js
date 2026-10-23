// Mini avventura punta-e-clicca in stile SCUMM (grafica originale).
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const VERBS = ['Vai a', 'Prendi', 'Usa', 'Apri', 'Guarda', 'Parla con', 'Dai'];
const SCENE_Y = 16, SCENE_H = 136, FLOOR_Y = 140;

// Pre-render degli sprite in canvas offscreen
const IMG = {};
for (const [name, rows] of Object.entries(SPRITES)) {
  const c = document.createElement('canvas');
  c.width = rows[0].length; c.height = rows.length;
  const g = c.getContext('2d');
  rows.forEach((r, y) => [...r].forEach((ch, x) => {
    if (PALETTE[ch]) { g.fillStyle = PALETTE[ch]; g.fillRect(x, y, 1, 1); }
  }));
  IMG[name] = c;
}

const state = {
  room: 'casa', verb: 0, sel: null, inv: [], flags: {},
  zak: { x: 200, tx: 200, flip: false, frame: 0 }, after: null,
  msg: '', msgColor: '#fff', msgT: 0, hover: null, won: false,
};

function say(t, color = '#fff') { state.msg = t; state.msgColor = color; state.msgT = 60 + t.length * 3; }
function has(i) { return state.inv.includes(i); }
function take(i) { state.inv.push(i); }

// ---------- Stanze ----------
const ROOMS = {
  casa: {
    draw() {
      rect(0, 16, 320, 100, '#7a4a2a');            // pareti legno
      for (let x = 0; x < 320; x += 40) rect(x, 16, 3, 100, '#5a3218');
      rect(0, 116, 320, 36, '#3c2a9c');             // moquette viola
      for (let x = 0; x < 320; x += 8) rect(x, 116 + (x % 16 ? 2 : 6), 4, 1, '#5040c0');
      rect(110, 30, 50, 40, '#8ac8f0'); frame(110, 30, 50, 40, '#4a2a10'); // finestra
      rect(118, 50, 10, 4, '#fff'); rect(140, 40, 14, 4, '#fff');
      rect(280, 40, 30, 80, '#6a3a18'); frame(280, 40, 30, 80, '#3a1a08'); rect(303, 80, 3, 3, '#e0c040'); // porta
      rect(10, 110, 80, 22, '#e8e8e8'); rect(10, 104, 20, 8, '#fff'); rect(30, 108, 60, 24, '#2a9a3a'); // letto
      rect(180, 96, 70, 6, '#7a2a1a'); rect(184, 102, 4, 22, '#5a1a0a'); rect(242, 102, 4, 22, '#5a1a0a'); // tavolo
      rect(10, 76, 34, 26, '#8a5a2a'); frame(10, 76, 34, 26, '#4a2a10');  // mobiletto
      if (!state.flags.drawerOpen) rect(14, 86, 26, 6, '#6a3a18'); else rect(14, 86, 26, 6, '#1a0a04');
      spr('fish', 18, 64);
      if (!has('remote')) spr('remote', 230, 88);
      rect(186, 72, 40, 24, '#222'); rect(189, 75, 34, 18, state.flags.tv ? '#40c0ff' : '#334'); // TV
      if (state.flags.tv) for (let y = 76; y < 92; y += 2) rect(189, y, 34, 1, '#80e0ff');
    },
    objects: [
      { id: 'porta', name: 'porta', x: 280, y: 40, w: 30, h: 80, wx: 280 },
      { id: 'letto', name: 'letto', x: 10, y: 104, w: 80, h: 28, wx: 80 },
      { id: 'cassetto', name: 'cassetto', x: 10, y: 76, w: 34, h: 26, wx: 50 },
      { id: 'pesce', name: 'pesce rosso', x: 18, y: 64, w: 12, h: 8, wx: 50 },
      { id: 'tv', name: 'televisore', x: 186, y: 72, w: 40, h: 24, wx: 206 },
      { id: 'remote', name: 'telecomando', x: 230, y: 88, w: 7, h: 10, wx: 232, show: () => !has('remote') },
      { id: 'finestra', name: 'finestra', x: 110, y: 30, w: 50, h: 40, wx: 135 },
    ],
  },
  ufficio: {
    draw() {
      rect(0, 16, 320, 100, '#c8a860');
      for (let x = 0; x < 320; x += 64) rect(x, 16, 6, 100, '#8a6a30');
      rect(0, 116, 320, 36, '#3a8a5a');
      for (let y = 118; y < 152; y += 4) for (let x = (y % 8); x < 320; x += 8) rect(x, y, 2, 1, '#c0e0c0');
      rect(90, 26, 140, 56, '#a8d0f0'); frame(90, 26, 140, 56, '#6a4a20'); // vetrata città
      for (let i = 0; i < 7; i++) rect(96 + i * 19, 40 + (i * 13) % 24, 14, 42 - (i * 13) % 24, '#7890b0');
      text('IL NATIONAL INQUISITOR', 108, 30, '#334', 1);
      rect(10, 60, 26, 56, '#9a9aa8'); for (let y = 66; y < 112; y += 12) rect(13, y, 20, 2, '#556'); // schedario
      rect(4, 20, 4, 96, '#6a4a20'); rect(10, 20, 26, 6, '#6a4a20');
      rect(270, 40, 34, 76, '#6a3a18'); frame(270, 40, 34, 76, '#3a1a08'); // porta
      spr('boss', 148, 70);
      rect(100, 94, 120, 10, '#6a3a18'); rect(104, 104, 112, 20, '#4a2a10'); // scrivania
      rect(120, 90, 20, 4, '#eee'); rect(178, 90, 16, 4, '#eee');
    },
    objects: [
      { id: 'capo', name: 'capo', x: 148, y: 70, w: 24, h: 26, wx: 200 },
      { id: 'scrivania', name: 'scrivania', x: 100, y: 94, w: 120, h: 30, wx: 160 },
      { id: 'schedario', name: 'schedario', x: 10, y: 60, w: 26, h: 56, wx: 40 },
      { id: 'porta2', name: 'porta', x: 270, y: 40, w: 34, h: 76, wx: 280 },
    ],
  },
};

// ---------- Logica delle azioni ----------
function act(verb, obj, item) {
  const v = VERBS[verb], id = obj.id;
  const F = state.flags;
  if (v === 'Guarda') return say({
    porta: 'La porta di casa. Fuori c\'è San Francisco.', letto: 'Il letto non è rifatto da mesi.',
    cassetto: F.drawerOpen ? 'Il cassetto è aperto.' : 'Un cassetto chiuso.',
    pesce: 'Il mio pesce rosso, Sushi. Mi fissa.', tv: F.tv ? 'Notiziario: "Strani tizi con occhiali e naso finto in città..."' : 'È spenta.',
    remote: 'Il telecomando della TV.', finestra: 'Bel tempo. Pessimo per lavorare.',
    capo: 'Il mio capo. Non sorride dal 1974.', scrivania: 'Pile di articoli sui due-headed squirrel.',
    schedario: 'Archivio di notizie improbabili.', porta2: 'Porta verso casa.',
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
  if (v === 'Usa' && item === 'remote' && id === 'tv' || v === 'Usa' && id === 'remote') {
    F.tv = !F.tv; return say(F.tv ? 'La TV si accende. C\'è una pubblicità di tesserini stampa... ah, il mio è sotto il letto!' : 'Spenta.');
  }
  if (v === 'Usa' && item === 'kazoo' && id === 'pesce') return say('Sushi apprezza la musica. Credo.');
  if (v === 'Usa' && id === 'kazoo') return say('Bzzzzz-bzz-bzzz!', '#ff0');
  if ((v === 'Guarda' || v === 'Prendi') && id === 'letto') {
    if (!F.tv) return say('Solo calzini spaiati.');
    if (has('card')) return say('Nient\'altro sotto il letto.');
    take('card'); return say('Trovato il mio tesserino stampa!');
  }
  if ((v === 'Apri' || v === 'Usa') && (id === 'porta' || id === 'porta2')) {
    if (id === 'porta') { state.room = 'ufficio'; state.zak.x = state.zak.tx = 270; say('Alla redazione del National Inquisitor.'); }
    else { state.room = 'casa'; state.zak.x = state.zak.tx = 270; }
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
function spr(n, x, y, flip) {
  if (!flip) return ctx.drawImage(IMG[n], x, y);
  ctx.save(); ctx.scale(-1, 1); ctx.drawImage(IMG[n], -x - IMG[n].width, y); ctx.restore();
}
function text(t, x, y, c, s = 1) { ctx.fillStyle = c; ctx.font = (8 * s) + 'px monospace'; ctx.textBaseline = 'top'; ctx.fillText(t, x, y); }
function wrap(t, max) {
  const out = []; let line = '';
  for (const w of t.split(' ')) { if ((line + w).length > max) { out.push(line); line = ''; } line += w + ' '; }
  return out.concat(line);
}

function visibleObjs() { return ROOMS[state.room].objects.filter(o => !o.show || o.show()); }

// Inventario in basso a destra, verbi a sinistra
function verbRect(i) { return { x: 4 + (i % 2) * 62, y: 156 + Math.floor(i / 2) * 11, w: 60, h: 10 }; }
function invRect(i) { return { x: 136 + (i % 6) * 30, y: 158 + Math.floor(i / 6) * 20, w: 28, h: 18 }; }
const inside = (p, r) => p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h;

function sentence() {
  let s = VERBS[state.verb];
  if (state.sel) s += ' ' + names[state.sel] + (VERBS[state.verb] === 'Dai' ? ' a' : ' con');
  if (state.hover) s += ' ' + state.hover;
  return s;
}
const names = { card: 'tesserino', kazoo: 'kazoo', remote: 'telecomando' };

function draw() {
  rect(0, 0, 320, 200, '#000');
  ROOMS[state.room].draw();
  const z = state.zak;
  const fr = z.x === z.tx ? 'zak_stand' : (Math.floor(z.frame / 6) % 2 ? 'zak_walk1' : 'zak_walk2');
  spr(fr, Math.round(z.x) - 8, FLOOR_Y - 32, z.flip);
  if (state.msgT > 0) wrap(state.msg, 52).forEach((l, i) => text(l, 2, 1 + i * 8, state.msgColor));
  rect(0, 152, 320, 48, '#000');
  text(sentence(), 4, 146 - 0, '#c0f', 1);
  VERBS.forEach((v, i) => { const r = verbRect(i); text(v, r.x, r.y, i === state.verb ? '#ff0' : '#4f4'); });
  state.inv.forEach((it, i) => { const r = invRect(i); rect(r.x, r.y, r.w, r.h, state.sel === it ? '#446' : '#223'); spr(it, r.x + (r.w - IMG[it].width) / 2, r.y + (r.h - IMG[it].height) / 2); });
  if (state.won) { rect(70, 60, 180, 30, '#000a'); text('*** FINE DELLA DEMO ***', 88, 70, '#ff0'); }
}

function tick() {
  const z = state.zak;
  if (z.x !== z.tx) {
    const d = z.tx - z.x; z.flip = d < 0; z.x += Math.sign(d) * Math.min(1.5, Math.abs(d)); z.frame++;
    if (z.x === z.tx && state.after) { const a = state.after; state.after = null; a(); }
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
    act(state.verb, { id: it }, state.sel); state.sel = null; state.verb = 0; return;
  }
  if (p.y < SCENE_Y || p.y >= 152) return;
  const o = visibleObjs().find(o => inside(p, o));
  const z = state.zak;
  if (!o || VERBS[state.verb] === 'Vai a') { z.tx = Math.max(10, Math.min(310, o ? o.wx : p.x)); state.after = null; return; }
  const verb = state.verb, sel = state.sel;
  state.after = () => { act(verb, o, sel); state.sel = null; state.verb = 0; };
  z.tx = o.wx; if (z.x === z.tx) { const a = state.after; state.after = null; a(); }
});

say('Un\'altra mattina. Dovrei andare in redazione...');
tick();
