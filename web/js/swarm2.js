/* Swarmsite swarm v2 — the same principle as v1 (cursors that act on REAL events, on a screenshot of the client's site),
   at a premium visual level: restrained cursor, glass name tag, one gesture per role, mass-based motion, a spotlight that
   follows the work, and nothing fake while real events are flowing.
   API (same as v1): const sw = Swarm2.mount(frame, {count, demo}); sw.setPage(img, pageH); sw.push(events); sw.phase(p); sw.stop(); */
(function (g) {
  'use strict';
  const ROLES = [['Reader', '#7C3AED'], ['Concept', '#E63946'], ['UX', '#0EA5E9'], ['Copy', '#1D5CFF'], ['UI', '#F97316'], ['Visual', '#22C55E'], ['Critic', '#FF4D4D'], ['Contract', '#9BE94B'], ['Render', '#B9B9B9'],
    ['Audit', '#10B981'], ['Type', '#FDCB40'], ['Photos', '#A8FFCB'], ['Motion', '#FF2E8A'], ['QA', '#E8E8E8'], ['Ending', '#B89B62']];
  const ALIAS = { Audit: 'Reader', Type: 'Copy', Photos: 'Visual', Motion: 'UI', QA: 'Contract', Ending: 'UX' };
  const rnd = (a, b) => a + Math.random() * (b - a); const sleep = ms => new Promise(r => setTimeout(r, ms));
  const easeOut = t => 1 - Math.pow(1 - t, 3); const easeInOut = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const CSS = `
  .s2-cur{position:absolute;left:0;top:0;pointer-events:none;z-index:7;will-change:transform;opacity:0;transition:opacity .6s}
  .s2-cur.in{opacity:1}.s2-cur.off,.s2-ghost.off,.s2-trail.off{opacity:0!important;transition:opacity .35s}.s2-cur svg{display:block;filter:drop-shadow(0 4px 6px rgba(0,0,0,.28)) drop-shadow(0 1px 1px rgba(0,0,0,.2))}
  .s2-cur .tag{position:absolute;left:14px;top:18px;display:flex;align-items:center;gap:7px;padding:5px 8px 5px 6px;border-radius:999px;background:rgba(255,255,255,.78);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(0,0,0,.08);box-shadow:0 6px 18px rgba(0,0,0,.12);white-space:nowrap;opacity:0;transform:translateY(-4px);transition:opacity .25s,transform .25s}
  .s2-cur.on .tag{opacity:1;transform:none}.s2-cur .tag i{width:7px;height:7px;border-radius:50%;display:block}.s2-cur .tag b{font:500 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:#111}
  .s2-cur .tag s{text-decoration:none;font:400 10.5px/1 Inter,system-ui,sans-serif;color:#555;max-width:220px;overflow:hidden;text-overflow:ellipsis}
  .s2-ghost{position:absolute;left:0;top:0;pointer-events:none;z-index:6;opacity:.22;will-change:transform}
  .s2-cur.fly svg{display:none}.s2-cur.fly .orb{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 28%,transparent),0 0 18px 4px color-mix(in srgb,var(--c) 55%,transparent),0 0 44px 10px color-mix(in srgb,var(--c) 25%,transparent)}
  .s2-cur.fly .orb::after{content:"";position:absolute;left:4px;top:3px;width:4px;height:4px;border-radius:50%;background:#fff;opacity:.9}
  .s2-cur.fly.on .orb{animation:s2pulse 1.1s ease-in-out infinite}@keyframes s2pulse{50%{transform:scale(1.25)}}
  .s2-cur.fly .tag{left:12px;top:10px}
  .s2-trail{position:absolute;left:0;top:0;pointer-events:none;z-index:6}.s2-trail i{position:absolute;left:-4px;top:-4px;width:8px;height:8px;border-radius:50%;background:var(--c);opacity:0;filter:blur(.5px)}
  .s2-spot{position:absolute;pointer-events:none;z-index:3;border-radius:10px;box-shadow:0 0 0 9999px rgba(10,10,10,.10);opacity:0;transition:left .9s cubic-bezier(.2,.8,.2,1),top .9s cubic-bezier(.2,.8,.2,1),width .9s cubic-bezier(.2,.8,.2,1),height .9s cubic-bezier(.2,.8,.2,1),opacity .5s}
  .s2-spot.on{opacity:1}
  .s2-x{position:absolute;pointer-events:none;z-index:5;transition:opacity .4s}
  .s2-read{position:absolute;left:0;height:1.25em;background:rgba(124,58,237,.22);border-radius:2px;transform-origin:left;transform:scaleX(0)}
  .s2-strike{position:absolute;height:1.5px;background:#111;transform-origin:left;transform:scaleX(0);transition:transform .45s cubic-bezier(.2,.8,.2,1)}
  .s2-type{position:absolute;font:500 15px/1.3 Inter,system-ui,sans-serif;color:#0b0b0b;background:rgba(255,255,255,.92);padding:6px 9px;border-radius:6px;box-shadow:0 10px 30px rgba(0,0,0,.14);border:1px solid rgba(0,0,0,.06);white-space:nowrap;max-width:420px;overflow:hidden;text-overflow:ellipsis}
  .s2-type::after{content:"";display:inline-block;width:1.5px;height:1em;background:#111;margin-left:2px;vertical-align:-2px;animation:s2blink .9s steps(2) infinite}
  @keyframes s2blink{to{opacity:0}}
  .s2-crop{position:absolute;border:1.5px solid rgba(255,255,255,.95);outline:1px solid rgba(0,0,0,.35);box-sizing:border-box;box-shadow:0 0 0 9999px rgba(0,0,0,.18) inset;transform-origin:top left;transform:scale(0)}
  .s2-crop i{position:absolute;width:8px;height:8px;background:#fff;border:1px solid rgba(0,0,0,.5);border-radius:1px}
  .s2-crop i:nth-child(1){left:-5px;top:-5px}.s2-crop i:nth-child(2){right:-5px;top:-5px}.s2-crop i:nth-child(3){left:-5px;bottom:-5px}.s2-crop i:nth-child(4){right:-5px;bottom:-5px}
  .s2-lift{position:absolute;overflow:hidden;border-radius:8px;box-shadow:0 30px 60px rgba(0,0,0,.28);transition:transform 1.1s cubic-bezier(.2,.8,.2,1),opacity .5s;will-change:transform}
  .s2-ghost-sec{position:absolute;background:rgba(255,255,255,.55);border:1px dashed rgba(0,0,0,.45);border-radius:6px;box-sizing:border-box;transition:transform 1s cubic-bezier(.2,.8,.2,1);will-change:transform;backdrop-filter:blur(2px)}
  .s2-guide{position:absolute;top:0;width:0;border-left:1px solid rgba(249,115,22,.95);transform:scaleY(0);transform-origin:top;transition:transform .5s cubic-bezier(.2,.8,.2,1)}
  .s2-guide b{position:absolute;top:8px;left:6px;font:500 10px/1 ui-monospace,Menlo,monospace;color:#9a3d00;background:rgba(255,255,255,.85);padding:3px 5px;border-radius:3px}
  .s2-ink{position:absolute;overflow:visible}.s2-ink path{fill:none;stroke:#FF3B3B;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  .s2-inknote{position:absolute;font:500 12px/1.3 "Caveat",Inter,system-ui,sans-serif;color:#d41d1d;background:rgba(255,255,255,.9);padding:4px 8px;border-radius:4px;white-space:nowrap;max-width:300px;overflow:hidden;text-overflow:ellipsis;transform:rotate(-1.5deg)}
  .s2-stamp{position:absolute;font:600 13px/1 ui-monospace,Menlo,monospace;letter-spacing:.14em;padding:6px 10px;border:2px solid;border-radius:4px;transform:rotate(-7deg) scale(1.6);opacity:0;transition:transform .35s cubic-bezier(.3,1.6,.4,1),opacity .2s;background:rgba(255,255,255,.75)}
  .s2-stamp.on{transform:rotate(-7deg) scale(1);opacity:1}
  .s2-sticky{position:absolute;width:190px;padding:12px 13px;background:#FFF7C2;color:#2b2200;font:400 12.5px/1.35 "Caveat",Inter,system-ui,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.18);transform:rotate(1.5deg) scale(.9);opacity:0;transition:transform .35s cubic-bezier(.3,1.5,.4,1),opacity .25s}
  .s2-sticky.on{transform:rotate(1.5deg) scale(1);opacity:1}
  .s2-wipe{position:absolute;left:0;right:0;background:#fff;border-bottom:1px solid rgba(0,0,0,.12);box-shadow:0 10px 30px rgba(0,0,0,.08);height:0}
  @media(prefers-reduced-motion:reduce){.s2-cur,.s2-ghost,.s2-x,.s2-spot{display:none}}`;
  let cssDone = false;

  class Cursor {
    constructor(frame, role, color, shape) {
      this.frame = frame; this.role = role; this.color = color; this.shape = shape || 'arrow'; this.x = rnd(.15, .85) * frame.clientWidth; this.y = -40; this.vx = 0; this.vy = 0; this.ang = 0; this.hist = [];
      this.el = document.createElement('div'); this.el.className = 's2-cur' + (this.shape === 'firefly' ? ' fly' : ''); this.el.style.setProperty('--c', color);
      this.el.innerHTML = `<svg width="18" height="22" viewBox="0 0 18 22"><path d="M1.5 1.5 L1.5 17 L5.6 13.2 L8.4 20 L11.4 18.7 L8.6 12 L14.5 12 Z" fill="#0b0b0b" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/></svg><div class="orb"></div><div class="tag"><i style="background:${color}"></i><b>${role}</b><s></s></div>`;
      if (this.shape === 'firefly') { this.ghost = document.createElement('div'); this.ghost.className = 's2-trail'; this.ghost.style.setProperty('--c', color); this.ghost.innerHTML = '<i></i>'.repeat(14); this.dots = [...this.ghost.children]; }
      else { this.ghost = document.createElement('div'); this.ghost.className = 's2-ghost'; this.ghost.innerHTML = this.el.querySelector('svg').outerHTML; }
      frame.appendChild(this.ghost); frame.appendChild(this.el); this.render(); requestAnimationFrame(() => this.el.classList.add('in'));
    }
    render(gx, gy) {
      if (this.shape === 'firefly') { this.el.style.transform = `translate(${this.x}px,${this.y}px)`; this.hist.unshift([this.x, this.y]); if (this.hist.length > 80) this.hist.pop();
        const on = this.el.classList.contains('on'); const h1 = this.hist[6]; const sp = h1 ? Math.hypot(this.x - h1[0], this.y - h1[1]) : 0; const vis = Math.min(1, sp / 28);
        this.dots.forEach((d, i) => { const h = this.hist[(i + 1) * 5]; if (!h || !vis) { d.style.opacity = 0; return; } d.style.transform = `translate(${h[0]}px,${h[1]}px) scale(${1 - i * .06})`; d.style.opacity = vis * (on ? .75 : .45) * (1 - i / 14); }); return; }
      this.el.style.transform = `translate(${this.x}px,${this.y}px) rotate(${this.ang}deg)`; if (gx !== undefined) this.ghost.style.transform = `translate(${gx}px,${gy}px) rotate(${this.ang}deg)`; }
    say(t) { this.el.querySelector('.tag s').textContent = t || ''; this.el.classList.toggle('on', !!t); }
    moveTo(x, y, opts = {}) {
      const sx = this.x, sy = this.y, dx = x - sx, dy = y - sy, dist = Math.hypot(dx, dy); const dur = opts.dur || Math.min(1300, 260 + dist * .85);
      const cx = sx + dx * .55 + rnd(-40, 40) - dy * .12, cy = sy + dy * .55 + rnd(-40, 40) + dx * .12; const t0 = performance.now(); let px = sx, py = sy;
      return new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = easeInOut(t);
        const nx = (1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * x, ny = (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * y;
        const vx = nx - px, vy = ny - py; px = nx; py = ny; const sp = Math.hypot(vx, vy); this.ang += ((sp > .5 ? Math.max(-14, Math.min(14, vx * .9)) : 0) - this.ang) * .18;
        this.x = nx; this.y = ny; this.render(nx - vx * 2.2, ny - vy * 2.2); if (t < 1) requestAnimationFrame(step); else { this.ang *= .5; this.render(nx, ny); res(); } }; requestAnimationFrame(step); });
    }
  }

  class Swarm {
    constructor(frame, opts = {}) {
      if (!cssDone) { const s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s); cssDone = true; }
      this.frame = frame; this.opts = opts; this.alive = true; this.cursors = []; this.queue = []; this.pan = 0; this.scale = 1; this.pageH = 0; this.active = 0;
      if (getComputedStyle(frame).position === 'static') frame.style.position = 'relative';
      this.spot = document.createElement('div'); this.spot.className = 's2-spot'; frame.appendChild(this.spot);
      const n = Math.min(opts.count || 9, ROLES.length);
      ROLES.slice(0, n).forEach(([role, color], i) => { const c = new Cursor(frame, role, color, opts.shape); this.cursors.push(c); setTimeout(() => this.loop(c), 250 + i * 380); });
    }
    phase() {}
    setPage(img, pageH) { this.page = img; this.pageH = pageH || img.naturalHeight; this.scale = this.frame.clientWidth / 1440; img.style.transition = 'transform 1.1s cubic-bezier(.2,.8,.2,1)'; }
    toLocal(rect) { const s = this.scale; return { x: rect.x * s, y: rect.y * s - this.pan, w: rect.w * s, h: Math.min(rect.h, 420) * s }; }
    panTo(rect) { if (!this.page) return; const s = this.scale, H = this.frame.clientHeight, maxPan = Math.max(0, this.pageH * s - H); const want = Math.min(maxPan, Math.max(0, rect.y * s - H * .36)); if (Math.abs(want - this.pan) < 40) return; this.pan = want; this.page.style.transform = `translateY(${-this.pan}px)`; this.frame.querySelectorAll('.s2-x').forEach(e => e.remove()); }
    push(evs) { for (const e of evs) this.queue.push(e); }
    stop() { this.alive = false; this.cursors.forEach(c => c.el.classList.remove('in')); this.spot.classList.remove('on'); setTimeout(() => this.frame.querySelectorAll('.s2-cur,.s2-ghost,.s2-trail,.s2-x,.s2-spot').forEach(e => e.remove()), 700); }
    park(c) { const i = this.cursors.indexOf(c); return { x: 24 + i * 34 + rnd(-3, 3), y: this.frame.clientHeight - 30 + rnd(-3, 3) }; }
    spotlight(r) { if (!r) { this.spot.classList.remove('on'); return; } Object.assign(this.spot.style, { left: (r.x - 14) + 'px', top: (r.y - 14) + 'px', width: (r.w + 28) + 'px', height: (r.h + 28) + 'px' }); this.spot.classList.add('on'); }
    mk(cls, r, html) { const d = document.createElement('div'); d.className = 's2-x ' + cls; if (r) Object.assign(d.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' }); if (html) d.innerHTML = html; this.frame.appendChild(d); return d; }
    fade(el, ms = 0) { setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 450); }, ms); }
    async loop(c) {
      while (this.alive) {
        const want = ALIAS[c.role] || c.role; const qi = this.queue.findIndex(e => (ALIAS[e.role] || e.role) === want);
        const mine = qi >= 0 ? this.queue.splice(qi, 1)[0] : null;
        try {
          if (mine && this.active < 2) { this.active++; try { await this.real(c, mine); } finally { this.active--; } }
          else if (mine) { this.queue.unshift(mine); await sleep(300); }
          else if (this.opts.demo && !this.queue.length && Math.random() < .5) await this.demo(c);
          else { c.say(''); c.el.classList.add('off'); c.ghost.classList.add('off'); await sleep(rnd(400, 900)); }
        } catch (e) { /* frame gone */ }
      }
    }
    /* ── one gesture per role, on the real rect, with the real text ── */
    async real(c, ev) {
      const role = ALIAS[c.role] || c.role; const text = ev.text || '';
      if (c.el.classList.contains('off')) { const r0 = ev.rect && this.page ? this.toLocal(ev.rect) : null; c.x = (r0 ? r0.x : this.frame.clientWidth * .5) + rnd(-160, 160); c.y = (r0 ? r0.y : this.frame.clientHeight * .5) + rnd(-120, 120); c.hist = []; c.render(); c.el.classList.remove('off'); c.ghost.classList.remove('off'); await sleep(250); }
      if (!(ev.rect && this.page)) { const p = this.park(c); await c.moveTo(p.x + rnd(-20, 20), p.y - rnd(40, 120)); c.say(text); await sleep(Math.min(2600, 900 + text.length * 25)); c.say(''); return; }
      this.panTo(ev.rect); await sleep(450); const r = this.toLocal(ev.rect); this.spotlight(r);
      await c.moveTo(r.x + Math.min(24, r.w * .2), r.y + Math.min(18, r.h * .5)); c.say(text);
      const G = { Reader: this.gRead, Copy: this.gCopy, Visual: this.gCrop, UX: this.gDrag, UI: this.gGuides, Critic: this.gInk, Contract: this.gStamp, Concept: this.gSticky, Render: this.gWipe };
      await (G[role] || this.gRead).call(this, c, r, text, ev);
      await sleep(rnd(500, 900)); c.say(''); this.spotlight(null);
    }
    async gRead(c, r, text) { const lines = Math.max(1, Math.min(6, Math.round(r.h / 26))); const lh = r.h / lines;
      for (let i = 0; i < lines; i++) { const b = this.mk('s2-read', { x: r.x, y: r.y + i * lh + lh * .15, w: r.w * (i === lines - 1 ? rnd(.4, .9) : 1), h: lh * .7 }); b.style.transition = 'transform .5s cubic-bezier(.2,.8,.2,1)';
        requestAnimationFrame(() => b.style.transform = 'scaleX(1)'); await c.moveTo(r.x + r.w * .9, r.y + i * lh + lh * .5, { dur: 420 }); this.fade(b, 1400); if (!this.alive) return; } }
    async gCopy(c, r, text) { const s = this.mk('s2-strike', { x: r.x, y: r.y + Math.min(r.h, 40) * .5, w: Math.min(r.w, 420), h: 1.5 }); requestAnimationFrame(() => s.style.transform = 'scaleX(1)');
      await c.moveTo(r.x + Math.min(r.w, 420), r.y + Math.min(r.h, 40) * .5, { dur: 450 });
      const t = this.mk('s2-type', { x: r.x, y: r.y + Math.min(r.h, 40) + 8, w: 0, h: 0 }); t.style.width = t.style.height = 'auto';
      for (let i = 1; i <= text.length; i++) { t.textContent = text.slice(0, i); await sleep(rnd(14, 34)); if (!this.alive) return; }
      this.fade(s, 1200); this.fade(t, 1600); }
    async gCrop(c, r, text) { const k = this.mk('s2-crop', r, '<i></i><i></i><i></i><i></i>'); k.style.transition = 'transform .6s cubic-bezier(.2,.8,.2,1)'; requestAnimationFrame(() => k.style.transform = 'scale(1)');
      await c.moveTo(r.x + r.w, r.y + r.h, { dur: 600 }); await sleep(350);
      if (this.page) { const l = this.mk('s2-lift', r); const img = this.page.cloneNode(); img.style.cssText = `position:absolute;left:${-r.x}px;top:${-(r.y + this.pan)}px;width:${this.frame.clientWidth}px;transition:none;transform:none`; l.appendChild(img);
        requestAnimationFrame(() => l.style.transform = 'translate(14px,-18px) scale(1.03)'); this.fade(l, 1500); }
      this.fade(k, 900); }
    async gDrag(c, r, text) { const gh = this.mk('s2-ghost-sec', r); const dy = Math.min(120, this.frame.clientHeight - r.y - r.h - 20);
      await c.moveTo(r.x + r.w / 2, r.y + r.h / 2, { dur: 400 }); gh.style.transform = `translateY(${dy}px)`; await c.moveTo(r.x + r.w / 2, r.y + r.h / 2 + dy, { dur: 950 }); await sleep(400); gh.style.transform = 'translateY(0)'; await c.moveTo(r.x + r.w / 2, r.y + r.h / 2, { dur: 800 }); this.fade(gh, 500); }
    async gGuides(c, r, text) { const a = this.mk('s2-guide', { x: r.x, y: 0, w: 0, h: this.frame.clientHeight }, `<b>${Math.round(r.x / this.scale)}</b>`), b = this.mk('s2-guide', { x: r.x + r.w, y: 0, w: 0, h: this.frame.clientHeight }, `<b>${Math.round(r.w / this.scale)}px</b>`);
      requestAnimationFrame(() => { a.style.transform = b.style.transform = 'scaleY(1)'; }); await c.moveTo(r.x + r.w, r.y + r.h * .5, { dur: 600 }); const nudge = rnd(-18, 18); b.style.transition += ',left .5s cubic-bezier(.2,.8,.2,1)'; b.style.left = (r.x + r.w + nudge) + 'px'; await c.moveTo(r.x + r.w + nudge, r.y + r.h * .5, { dur: 500 }); this.fade(a, 1200); this.fade(b, 1200); }
    async gInk(c, r, text) { const pad = 10, w = r.w + pad * 2, h = Math.min(r.h, 160) + pad * 2; const svg = this.mk('s2-ink', { x: r.x - pad, y: r.y - pad, w, h });
      const cx = w / 2, cy = h / 2, rx = w / 2 - 3, ry = h / 2 - 3; const d = `M${cx + rx} ${cy} A${rx} ${ry} 0 1 1 ${cx + rx * .98} ${cy - ry * .12}`;
      svg.innerHTML = `<svg width="${w}" height="${h}" style="overflow:visible"><path d="${d}" stroke-dasharray="2000" stroke-dashoffset="2000" style="transition:stroke-dashoffset 1.1s cubic-bezier(.4,0,.2,1)"/></svg>`;
      requestAnimationFrame(() => svg.querySelector('path').style.strokeDashoffset = '0');
      const t0 = performance.now(); await new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / 1100), a = -Math.PI * .5 + t * Math.PI * 2; c.x = r.x - pad + cx + Math.cos(a) * rx; c.y = r.y - pad + cy + Math.sin(a) * ry; c.render(); t < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
      const n = this.mk('s2-inknote', { x: Math.min(this.frame.clientWidth - 320, r.x + r.w + 16), y: r.y - 6, w: 0, h: 0 }); n.style.width = n.style.height = 'auto'; n.textContent = text; this.fade(svg, 1800); this.fade(n, 1800); }
    async gStamp(c, r, text) { const ok = !/✗|fail|broken|missing|empty|repeat/i.test(text); const s = this.mk('s2-stamp', { x: r.x + r.w - 110, y: r.y + 10, w: 0, h: 0 }); s.style.width = s.style.height = 'auto'; s.style.color = s.style.borderColor = ok ? '#1f7a2e' : '#c81e1e'; s.textContent = ok ? '✓ PASS' : '✗ FAIL';
      await c.moveTo(r.x + r.w - 60, r.y + 24, { dur: 500 }); s.classList.add('on'); this.fade(s, 1600); }
    async gSticky(c, r, text) { const s = this.mk('s2-sticky', { x: Math.min(this.frame.clientWidth - 210, r.x + 20), y: r.y + 16, w: 190, h: 0 }); s.style.height = 'auto'; s.textContent = text; await c.moveTo(r.x + 40, r.y + 30, { dur: 500 }); s.classList.add('on'); this.fade(s, 2600); }
    async gWipe(c, r, text) { const w = this.mk('s2-wipe', { x: 0, y: r.y, w: this.frame.clientWidth, h: 0 }); w.style.transition = 'height .9s cubic-bezier(.2,.8,.2,1),opacity .5s'; requestAnimationFrame(() => w.style.height = r.h + 'px'); await c.moveTo(r.x + r.w * .5, r.y + r.h, { dur: 900 }); this.fade(w, 500); }
    /* landing demo (no real events): a few quiet, plausible gestures on the frame's own blocks */
    async demo(c) { if (c.el.classList.contains('off')) { c.el.classList.remove('off'); c.ghost.classList.remove('off'); } let blocks = [...this.frame.querySelectorAll('[data-agent]')]; if (!blocks.length) blocks = [...this.frame.querySelectorAll('.row > div, figure, img, h1, h2, h3, p')].filter(b => b.getBoundingClientRect().width > 120); if (!blocks.length) return; const el = blocks[Math.floor(rnd(0, blocks.length))]; const fr = this.frame.getBoundingClientRect(), b = el.getBoundingClientRect(); const r = { x: b.left - fr.left, y: b.top - fr.top, w: b.width, h: Math.min(b.height, 240) };
      const role = ALIAS[c.role] || c.role; const say = { Reader: 'reading', Copy: 'h1 · 6 words', Visual: 'hero · 1440px', UX: 'one action', UI: '3 columns', Critic: 'empty screen', Contract: 'promise kept', Concept: 'one idea', Render: 'rendering' }[role] || 'working';
      await c.moveTo(r.x + 20, r.y + 16); c.say(say); const G = { Reader: this.gRead, Copy: this.gCopy, Visual: this.gCrop, UX: this.gDrag, UI: this.gGuides, Critic: this.gInk, Contract: this.gStamp, Concept: this.gSticky, Render: this.gWipe };
      await (G[role] || this.gRead).call(this, c, r, say); await sleep(600); c.say(''); }
  }
  g.Swarm2 = { mount: (frame, opts) => new Swarm(frame, opts), ROLES };
})(window);
