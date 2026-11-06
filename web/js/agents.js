/* Swarmsite agents — animated cursors that visibly "work" on a frame (a screenshot of the client's site).
   Original implementation. Usage: const sw = Agents.mount(frameEl, {count:7}); sw.phase('capture'); sw.stop(); */
(function (g) {
  'use strict';
  const ROLES = [
    ['Audit', '#10B981'], ['Concept', '#E63946'], ['Copy', '#1D5CFF'], ['Type', '#FDCB40'],
    ['Photos', '#A8FFCB'], ['Motion', '#FF2E8A'], ['QA', '#F4F4F4'], ['Ending', '#B89B62'],
    ['Reader', '#7C3AED'], ['UX', '#0EA5E9'], ['UI', '#F97316'], ['Visual', '#22C55E'], ['Critic', '#FF6B6B'], ['Render', '#94A3B8']
  ];
  const NAMES = ['atlas', 'birch', 'cobalt', 'dune', 'ember', 'fjord', 'gale', 'halo', 'iris', 'juno', 'kite', 'lumen', 'mica', 'nova', 'onyx', 'pike'];
  // What each role says while a given pipeline step runs. Short, specific, never generic.
  const VOCAB = {
    queued:  { all: ['waking up', 'in the queue'] },
    capture: { Audit: ['reading nav', 'counting links', 'measuring h1'], Photos: ['pulling photo 1', 'photo 2 · 1400px', 'grading hero'], Concept: ['reading the site', 'who is this for?'], Copy: ['collecting text', 'finding the fact'], Type: ['sampling fonts', 'serif? sans?'], Motion: ['watching scroll'], QA: ['390px check', 'tap targets'], Ending: ['finding contact', 'hours · address'] },
    diagnose:{ Audit: ['words per screen', 'sections: 9', 'no headline'], Copy: ['banned words', 'too many CTAs'], Type: ['system font ✗', 'contrast 2.8:1'], Photos: ['hero-grade: 2'], QA: ['overflow at 390', 'footer: 41 links'], Concept: ['category: place'], Motion: ['no motion found'], Ending: ['no ending'] },
    direct:  { Concept: ['concept C8', 'one idea per screen', 'beat 1: hero'], Copy: ['h1 · 6 words', 'the fact: since 1982', 'lede · 22 words'], Type: ['Cormorant + Instrument', 'keep their mark'], Photos: ['hero: long table', 'beat 3: quote + photo'], Motion: ['clip-reveal hero', 'word-blur h1'], Audit: ['5 beats', 'cutting 38 links'], QA: ['reading direction.json'], Ending: ['ending: reservation'] },
    render:  { Type: ['h1 124px', 'tracking −.015em', 'lede 25px'], Photos: ['placing hero', 'tint #648C65', 'band photo'], Motion: ['lenis on', 'masked-line-reveal', 'stagger-in cards'], Copy: ['typing h1', 'typing lede', 'cta: reserve →'], Concept: ['paper #E7F9E8', 'ink #0E1F0F'], Audit: ['nav: 4 links'], QA: ['waiting for build'], Ending: ['wordmark 19vw', 'address · hours'] },
    qa:      { QA: ['1440 · screen 1 ✓', '390 · screen 1 ✓', 'overflow? none', 'h1 length ✓', 'words/screen 71'], Audit: ['buttons: 1 verb', 'links: 4'], Type: ['contrast 7.9:1 ✓'], Motion: ['reduced-motion ✓'], Copy: ['no banned words'], Photos: ['hero fill ✓'], Concept: ['score 94'], Ending: ['ending ✓'] },
    upload:  { all: ['publishing', 'preview ready', 'writing kit'] },
    done:    { all: ['done'] },
    demo:    { Audit: ['58 menu links', 'no headline'], Concept: ['one idea per screen'], Copy: ['h1 · 6 words'], Type: ['Cormorant 124px'], Photos: ['hero: their photo'], Motion: ['clip-reveal'], QA: ['390 ✓'], Ending: ['one action'] }
  };
  const rnd = (a, b) => a + Math.random() * (b - a); const pick = a => a[Math.floor(Math.random() * a.length)];
  const sleep = ms => new Promise(r => setTimeout(r, ms)); const ease = t => 1 - Math.pow(1 - t, 3);
  const CSS = `
  .ag-cur{position:absolute;left:0;top:0;pointer-events:none;z-index:5;will-change:transform;opacity:0;transition:opacity .5s}
  .ag-cur.in{opacity:1}
  .ag-cur .ag-tag{position:absolute;left:16px;top:16px;color:#111;font:600 10.5px/1 system-ui,sans-serif;padding:4px 7px;border-radius:4px;white-space:nowrap;box-shadow:0 1px 3px rgba(0,0,0,.35)}
  .ag-cur .ag-task{position:absolute;left:16px;top:37px;color:#fff;background:rgba(0,0,0,.72);font:500 10.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace;padding:4px 7px;border-radius:4px;white-space:nowrap;backdrop-filter:blur(6px)}
  .ag-cur .ag-task:empty{display:none}
  .ag-sel{position:absolute;border:1.5px solid;pointer-events:none;z-index:4;box-sizing:border-box;background:rgba(255,255,255,.04);transition:opacity .35s}
  .ag-sel i{position:absolute;width:6px;height:6px;background:#fff;border:1.5px solid;border-color:inherit}
  .ag-sel i:nth-child(1){left:-4px;top:-4px}.ag-sel i:nth-child(2){right:-4px;top:-4px}.ag-sel i:nth-child(3){left:-4px;bottom:-4px}.ag-sel i:nth-child(4){right:-4px;bottom:-4px}
  .ag-sel b{position:absolute;left:50%;bottom:-20px;transform:translateX(-50%);color:#111;font:600 9.5px/1 system-ui;padding:3px 6px;border-radius:3px;white-space:nowrap}
  .ag-note{position:absolute;pointer-events:none;z-index:6;color:#fff;font:500 11px/1.2 ui-monospace,Menlo,monospace;background:rgba(0,0,0,.7);padding:5px 7px;border-radius:4px;border-left:2px solid;white-space:nowrap;transition:opacity .35s}
  .ag-line{position:absolute;pointer-events:none;z-index:4;height:0;border-top:1px dashed;transition:opacity .35s}
  @media(prefers-reduced-motion:reduce){.ag-cur,.ag-sel,.ag-note,.ag-line{display:none}}`;
  let cssDone = false;

  class Cursor {
    constructor(frame, role, color, name) {
      this.frame = frame; this.role = role; this.color = color; this.name = name;
      this.x = rnd(.1, .9) * frame.clientWidth; this.y = -40;
      this.el = document.createElement('div'); this.el.className = 'ag-cur';
      this.el.innerHTML = `<svg width="20" height="24" viewBox="0 0 22 26"><path d="M2 2 L2 20 L7 15.5 L10.5 23 L14 21.5 L10.5 14 L17 14 Z" fill="${color}" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg><span class="ag-tag" style="background:${color}">${name} · ${role}</span><span class="ag-task"></span>`;
      frame.appendChild(this.el); this.render(); requestAnimationFrame(() => this.el.classList.add('in'));
    }
    render() { this.el.style.transform = `translate(${this.x}px,${this.y}px)`; }
    task(t) { this.el.querySelector('.ag-task').textContent = t || ''; }
    moveTo(x, y) {
      const sx = this.x, sy = this.y, dx = x - sx, dy = y - sy, dist = Math.hypot(dx, dy); const dur = Math.min(1100, 220 + dist * .9);
      const cx = sx + dx * .5 + rnd(-60, 60), cy = sy + dy * .5 + rnd(-60, 60); const t0 = performance.now();
      return new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = ease(t); this.x = (1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * x; this.y = (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * y; this.render(); t < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
    }
  }

  class Swarm {
    constructor(frame, opts = {}) {
      if (!cssDone) { const s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s); cssDone = true; }
      this.frame = frame; this.opts = opts; this.alive = true; this.ph = opts.phase || 'queued'; this.cursors = []; this.queue = []; this.pan = 0; this.scale = 1; this.pageH = 0;
      if (getComputedStyle(frame).position === 'static') frame.style.position = 'relative';
      const n = Math.min(opts.count || 7, ROLES.length);
      ROLES.slice(0, n).forEach(([role, color], i) => { const c = new Cursor(frame, role, color, NAMES[(i * 3 + Math.floor(rnd(0, 3))) % NAMES.length]); this.cursors.push(c); setTimeout(() => this.loop(c), 300 + i * 420); });
    }
    phase(p) { if (VOCAB[p]) this.ph = p; }
    /* Real page: an <img> of the full page (1440 wide) inside the frame; we pan it to show the rect an agent works on. */
    setPage(img, pageH) { this.page = img; this.pageH = pageH || img.naturalHeight; this.scale = this.frame.clientWidth / 1440; img.style.transition = 'transform 1.1s cubic-bezier(.2,.8,.2,1)'; }
    toLocal(rect) { const s = this.scale; return { x: rect.x * s, y: rect.y * s - this.pan, w: rect.w * s, h: rect.h * s }; }
    panTo(rect) { if (!this.page) return; const s = this.scale, H = this.frame.clientHeight, maxPan = Math.max(0, this.pageH * s - H); const want = Math.min(maxPan, Math.max(0, rect.y * s - H * 0.38)); if (Math.abs(want - this.pan) < 40) return; this.pan = want; this.page.style.transform = `translateY(${-want}px)`; }
    /* Feed real events: {role, text, rect?}. One agent per event; the matching role takes it when free. */
    push(evs) { for (const e of evs) this.queue.push(e); }
    stop() { this.alive = false; this.cursors.forEach(c => c.el.classList.remove('in')); setTimeout(() => this.frame.querySelectorAll('.ag-cur,.ag-sel,.ag-note,.ag-line').forEach(e => e.remove()), 600); }
    say(c) { const v = VOCAB[this.ph] || VOCAB.queued; return pick(v[c.role] || v.all || ['…']); }
    // A plausible region of the page: left/center/right column, hero/mid/low band.
    region() { const W = this.frame.clientWidth, H = this.frame.clientHeight; const w = rnd(.14, .42) * W, h = rnd(.06, .22) * H; return { x: rnd(.04, .96 - w / W) * W, y: rnd(.05, .95 - h / H) * H, w, h }; }
    async loop(c) {
      while (this.alive) {
        const qi = this.queue.findIndex(e => e.role === c.role); const mine = qi >= 0 ? this.queue.splice(qi, 1)[0] : (this.queue.length && Math.random() < .25 ? this.queue.shift() : null);
        try {
          if (mine) await this.real(c, mine);
          else if (this.queue.length) await this.wander(c, this.region());           // others are busy with real work: stay light
          else { const act = Math.random(); const r = this.region(); if (act < .45) await this.select(c, r); else if (act < .75) await this.note(c, r); else if (act < .88) await this.measure(c, r); else await this.wander(c, r); }
        } catch (e) { /* frame may be gone */ }
        await sleep(mine ? rnd(80, 300) : rnd(150, 700));
      }
    }
    async select(c, r) {
      c.task(''); await c.moveTo(r.x, r.y); c.task(this.say(c));
      const s = document.createElement('div'); s.className = 'ag-sel'; s.style.borderColor = c.color; s.style.left = r.x + 'px'; s.style.top = r.y + 'px'; s.style.width = '0px'; s.style.height = '0px';
      s.innerHTML = '<i></i><i></i><i></i><i></i>'; this.frame.appendChild(s);
      const t0 = performance.now(), dur = rnd(380, 700);
      await new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = ease(t); s.style.width = r.w * e + 'px'; s.style.height = r.h * e + 'px'; c.x = r.x + r.w * e; c.y = r.y + r.h * e; c.render(); t < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
      const b = document.createElement('b'); b.style.background = c.color; b.textContent = `${Math.round(r.w * 1.3)} × ${Math.round(r.h * 1.3)}`; s.appendChild(b);
      await sleep(rnd(700, 1400)); s.style.opacity = '0'; setTimeout(() => s.remove(), 400);
    }
    async note(c, r) {
      c.task(''); await c.moveTo(r.x, r.y); const txt = this.say(c);
      const n = document.createElement('div'); n.className = 'ag-note'; n.style.borderColor = c.color; n.style.left = (r.x + 14) + 'px'; n.style.top = (r.y - 8) + 'px'; n.textContent = ''; this.frame.appendChild(n);
      for (let i = 1; i <= txt.length; i++) { n.textContent = txt.slice(0, i); await sleep(rnd(18, 45)); if (!this.alive) break; }
      await sleep(rnd(900, 1600)); n.style.opacity = '0'; setTimeout(() => n.remove(), 400);
    }
    async measure(c, r) {
      c.task('measuring'); await c.moveTo(r.x, r.y + r.h);
      const l = document.createElement('div'); l.className = 'ag-line'; l.style.borderColor = c.color; l.style.left = r.x + 'px'; l.style.top = (r.y + r.h) + 'px'; l.style.width = '0px'; this.frame.appendChild(l);
      const t0 = performance.now(), dur = 500; await new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = ease(t); l.style.width = r.w * e + 'px'; c.x = r.x + r.w * e; c.render(); t < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
      c.task(`${Math.round(r.w * 1.3)}px`); await sleep(rnd(600, 1100)); l.style.opacity = '0'; setTimeout(() => l.remove(), 400); c.task('');
    }
    async real(c, ev) {
      c.task('');
      if (ev.rect && this.page) {
        this.panTo(ev.rect); await sleep(500); const r = this.toLocal(ev.rect);
        await c.moveTo(r.x, r.y);
        const s = document.createElement('div'); s.className = 'ag-sel'; s.style.borderColor = c.color; s.style.left = r.x + 'px'; s.style.top = r.y + 'px'; s.style.width = '0px'; s.style.height = '0px'; s.innerHTML = '<i></i><i></i><i></i><i></i>'; this.frame.appendChild(s);
        const t0 = performance.now(), dur = rnd(350, 600);
        await new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = ease(t); s.style.width = r.w * e + 'px'; s.style.height = r.h * e + 'px'; c.x = r.x + r.w * e; c.y = r.y + r.h * e; c.render(); t < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
        const b = document.createElement('b'); b.style.background = c.color; b.textContent = `${ev.rect.w} × ${ev.rect.h}`; s.appendChild(b);
        const n = document.createElement('div'); n.className = 'ag-note'; n.style.borderColor = c.color; const nx = Math.min(this.frame.clientWidth - 260, r.x + r.w + 10); n.style.left = (nx < r.x + r.w ? Math.max(8, r.x) : nx) + 'px'; n.style.top = (nx < r.x + r.w ? r.y + r.h + 26 : r.y + Math.min(r.h, 28) - 10) + 'px'; n.style.maxWidth = '320px'; n.style.whiteSpace = 'normal'; this.frame.appendChild(n);
        for (let i = 1; i <= ev.text.length; i++) { n.textContent = ev.text.slice(0, i); await sleep(rnd(10, 28)); if (!this.alive) break; }
        await sleep(rnd(900, 1500)); s.style.opacity = n.style.opacity = '0'; setTimeout(() => { s.remove(); n.remove(); }, 400);
      } else {
        const r = this.region(); await c.moveTo(r.x, r.y);
        const n = document.createElement('div'); n.className = 'ag-note'; n.style.borderColor = c.color; n.style.left = (r.x + 14) + 'px'; n.style.top = (r.y - 8) + 'px'; this.frame.appendChild(n);
        for (let i = 1; i <= ev.text.length; i++) { n.textContent = ev.text.slice(0, i); await sleep(rnd(10, 28)); if (!this.alive) break; }
        await sleep(rnd(1100, 1800)); n.style.opacity = '0'; setTimeout(() => n.remove(), 400);
      }
      c.task('');
    }
    async wander(c, r) { c.task(''); await c.moveTo(r.x, r.y); await sleep(rnd(200, 500)); }
  }
  g.Agents = { mount: (frame, opts) => new Swarm(frame, opts), ROLES };
})(window);
