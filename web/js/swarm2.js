/* Swarmsite swarm — the agents at work on a page: named cursors that act on REAL events, on a screenshot of the client's
   site. Each agent has one job and one colour; what it does is drawn where it happens — a section is framed and scanned,
   a headline is read line by line, a picture is lifted out, a button is underlined, colours are laid out as swatches, a
   check is stamped. Nothing is shown that the job did not report: an agent with no event of its own goes back over a
   place another event already named and looks at it; it never states a finding of its own.
   API: const sw = Swarm2.mount(frame, {count, roam, busy, demo, roles}); sw.setPage(img, pageH); sw.push(events);
        sw.phase(p); sw.pause(bool); sw.stop();
   An event is {role, text, rect?} with rect in the page's own 1440-wide pixels. Roles of older jobs are kept by ALIAS.
   (`shape` is accepted and ignored: there is one look.) */
(function (g) {
  'use strict';
  const ROLES = [['Reader', '#8A3B46'], ['Layout', '#2C5F8D'], ['Copy', '#A85F12'], ['Photos', '#2E7658'], ['Type', '#6B4C93'], ['Colour', '#C0453F'], ['QA', '#1B1B1B'], ['Render', '#1F6F78']];
  const ALIAS = { Audit: 'Reader', Concept: 'Reader', UX: 'Layout', UI: 'Layout', Motion: 'Layout', Visual: 'Photos', Critic: 'QA', Contract: 'QA', Ending: 'Copy' };
  const rnd = (a, b) => a + Math.random() * (b - a); const sleep = ms => new Promise(r => setTimeout(r, ms));
  const easeInOut = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const onDark = hex => { const n = parseInt(hex.slice(1), 16), r = n >> 16, gg = n >> 8 & 255, b = n & 255; return (r * 299 + gg * 587 + b * 114) / 1000 < 150; };
  const CSS = `
  .s2-cur{position:absolute;left:0;top:0;pointer-events:none;z-index:7;will-change:transform;opacity:0;transition:opacity .5s}
  .s2-cur.in{opacity:1}.s2-cur.off{opacity:0!important;transition:opacity .35s}
  .s2-cur .ptr{display:block;overflow:visible;transform-origin:4px 3px;filter:drop-shadow(0 3px 5px rgba(0,0,0,.28)) drop-shadow(0 1px 1px rgba(0,0,0,.18))}
  .s2-cur .ring{position:absolute;left:-9px;top:-10px;width:26px;height:26px;border-radius:50%;border:2px solid var(--c);opacity:0}
  .s2-cur.on .ring,.s2-cur.look .ring{animation:s2-ring 1.2s ease-out infinite}@keyframes s2-ring{0%{opacity:.7;transform:scale(.35)}100%{opacity:0;transform:scale(1.5)}}
  .s2-cur .tag{position:absolute;left:15px;top:19px;display:flex;align-items:baseline;gap:6px;max-width:300px;padding:5px 10px 5px 9px;border-radius:4px 999px 999px 999px;background:var(--c);color:var(--t);
    font:600 12px/1.15 "Figtree",system-ui,sans-serif;letter-spacing:0;text-transform:none;white-space:nowrap;box-shadow:0 0 0 1.5px rgba(255,255,255,.92),0 6px 16px rgba(0,0,0,.18);transition:transform .25s cubic-bezier(.2,.7,.2,1)}
  .s2-cur .tag b{font-weight:600}.s2-cur .tag s{text-decoration:none;font-weight:500;opacity:.92;overflow:hidden;text-overflow:ellipsis;max-width:0;transition:max-width .35s cubic-bezier(.2,.7,.2,1)}
  .s2-cur.on .tag s{max-width:230px}.s2-cur.on .tag s:not(:empty)::before{content:"· "}.s2-cur.on .tag{transform:translateY(2px)}
  .s2-cur.flip .tag{left:auto;right:6px;border-radius:999px 4px 999px 999px}
  .s2-spot{position:absolute;pointer-events:none;z-index:3;border-radius:10px;box-shadow:0 0 0 9999px rgba(10,10,10,.07);opacity:0;transition:left .9s cubic-bezier(.2,.8,.2,1),top .9s cubic-bezier(.2,.8,.2,1),width .9s cubic-bezier(.2,.8,.2,1),height .9s cubic-bezier(.2,.8,.2,1),opacity .5s}
  .s2-spot.on{opacity:1}
  .s2-x{position:absolute;pointer-events:none;z-index:5;transition:opacity .4s;box-sizing:border-box}
  /* a section framed and scanned: corner marks, a line that travels down it, then it lifts a little — it has been opened */
  .s2-scan{border-radius:8px;border:1.5px solid var(--c);background:color-mix(in srgb,var(--c) 7%,transparent);opacity:0;transform:scale(.985);transition:opacity .35s,transform .5s cubic-bezier(.2,.7,.2,1),box-shadow .5s;overflow:hidden}
  .s2-scan.on{opacity:1;transform:none}.s2-scan.open{transform:scale(1.012);box-shadow:0 18px 44px rgba(0,0,0,.2);background:color-mix(in srgb,var(--c) 3%,transparent)}
  .s2-scan u{position:absolute;left:0;right:0;top:0;height:42%;text-decoration:none;background:linear-gradient(180deg,transparent,color-mix(in srgb,var(--c) 26%,transparent));border-bottom:2px solid var(--c);transform:translateY(-100%)}
  .s2-scan.on u{animation:s2-sweep 1.25s cubic-bezier(.4,0,.3,1) .15s both}@keyframes s2-sweep{0%{transform:translateY(-100%)}100%{transform:translateY(240%);opacity:0}}
  .s2-scan em,.s2-chip{position:absolute;left:8px;top:8px;max-width:calc(100% - 16px);padding:4px 9px;border-radius:999px;background:var(--c);color:var(--t);font:600 11.5px/1.2 "Figtree",system-ui,sans-serif;font-style:normal;letter-spacing:0;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .s2-peek{border-radius:8px;border:1.5px dashed color-mix(in srgb,var(--c) 70%,transparent);opacity:0;transition:opacity .4s}.s2-peek.on{opacity:.9}
  .s2-read{left:0;border-radius:3px;background:color-mix(in srgb,var(--c) 26%,transparent);transform-origin:left;transform:scaleX(0);transition:transform .5s cubic-bezier(.2,.8,.2,1),opacity .4s}
  .s2-under{height:3px;border-radius:2px;background:var(--c);transform-origin:left;transform:scaleX(0);transition:transform .45s cubic-bezier(.2,.8,.2,1),opacity .4s}
  .s2-chip{position:absolute;left:auto;top:auto;opacity:0;transform:translateY(4px);transition:opacity .3s,transform .3s;box-shadow:0 0 0 1.5px rgba(255,255,255,.9),0 6px 16px rgba(0,0,0,.16)}.s2-chip.on{opacity:1;transform:none}
  .s2-crop{border:1.5px solid #fff;outline:1.5px solid var(--c);transform-origin:top left;transform:scale(0);transition:transform .6s cubic-bezier(.2,.8,.2,1),opacity .4s}
  .s2-crop i{position:absolute;width:9px;height:9px;background:#fff;border:1.5px solid var(--c);border-radius:2px}
  .s2-crop i:nth-child(1){left:-6px;top:-6px}.s2-crop i:nth-child(2){right:-6px;top:-6px}.s2-crop i:nth-child(3){left:-6px;bottom:-6px}.s2-crop i:nth-child(4){right:-6px;bottom:-6px}
  .s2-lift{overflow:hidden;border-radius:8px;box-shadow:0 0 0 2px #fff,0 30px 60px rgba(0,0,0,.3);transition:transform 1.1s cubic-bezier(.2,.8,.2,1),opacity .5s;will-change:transform}
  .s2-sw{display:flex;gap:6px;padding:6px;border-radius:12px;background:#fff;box-shadow:0 10px 28px rgba(0,0,0,.2);opacity:0;transform:translateY(6px) scale(.96);transition:opacity .3s,transform .35s cubic-bezier(.2,.7,.2,1)}
  .s2-sw.on{opacity:1;transform:none}.s2-sw i{width:26px;height:26px;border-radius:7px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
  .s2-stamp{padding:6px 12px;border-radius:999px;background:#fff;color:#141414;font:700 12px/1 "Figtree",system-ui,sans-serif;letter-spacing:0;text-transform:none;box-shadow:0 0 0 2px currentColor,0 10px 24px rgba(0,0,0,.18);transform:scale(1.5);opacity:0;transition:transform .35s cubic-bezier(.3,1.6,.4,1),opacity .2s;white-space:nowrap}
  .s2-stamp.on{transform:none;opacity:1}.s2-stamp.no{color:#b3261e}
  .s2-wipe{left:0;right:0;height:0;background:linear-gradient(180deg,color-mix(in srgb,var(--c) 18%,transparent),transparent);border-top:2px solid var(--c)}
  @media(max-width:600px){.s2-cur .tag{font-size:11px;padding:4px 8px}.s2-cur.on .tag s{max-width:130px}}
  @media(prefers-reduced-motion:reduce){.s2-cur,.s2-x,.s2-spot{display:none}}`;
  let cssDone = false;

  class Cursor {
    constructor(frame, role, color) {
      this.frame = frame; this.role = role; this.color = color; this.x = rnd(.15, .85) * frame.clientWidth; this.y = -40; this.ang = 0;
      this.el = document.createElement('div'); this.el.className = 's2-cur'; this.el.style.setProperty('--c', color); this.el.style.setProperty('--t', onDark(color) ? '#fff' : '#141414');
      this.el.innerHTML = '<svg class="ptr" width="22" height="24" viewBox="0 0 22 24" aria-hidden="true"><path d="M3.1 2.7c-.4-1.1.7-2.1 1.8-1.6l14.2 6.2c1.2.5 1.1 2.2-.2 2.6l-5.6 1.6c-.5.1-.8.5-1 .9l-2.3 5.5c-.5 1.2-2.2 1.1-2.6-.1z" fill="var(--c)" stroke="#fff" stroke-width="1.7" stroke-linejoin="round"/></svg><i class="ring"></i><div class="tag"><b></b><s></s></div>';
      this.el.querySelector('.tag b').textContent = role; this.ptr = this.el.querySelector('.ptr'); this.tag = this.el.querySelector('.tag s');
      frame.appendChild(this.el); this.render(); requestAnimationFrame(() => this.el.classList.add('in'));
    }
    render() { this.el.style.transform = `translate(${this.x}px,${this.y}px)`; this.ptr.style.transform = `rotate(${this.ang}deg)`; this.el.classList.toggle('flip', this.x > this.frame.clientWidth - 190); }
    say(t) { this.tag.textContent = t || ''; this.el.classList.toggle('on', !!t); }
    /* mass-based motion: a curved path, eased, the pointer leaning into its turn */
    moveTo(x, y, opts = {}) {
      const sx = this.x, sy = this.y, dx = x - sx, dy = y - sy, dist = Math.hypot(dx, dy); const dur = opts.dur || Math.min(1300, 260 + dist * .85);
      const cx = sx + dx * .55 + rnd(-40, 40) - dy * .12, cy = sy + dy * .55 + rnd(-40, 40) + dx * .12; const t0 = performance.now(); let px = sx;
      return new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur), e = easeInOut(t);
        const nx = (1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * x, ny = (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * y;
        const vx = nx - px; px = nx; this.ang += (Math.max(-16, Math.min(16, vx * .9)) - this.ang) * .18;
        this.x = nx; this.y = ny; this.render(); if (t < 1 && this.frame.isConnected) requestAnimationFrame(step); else { this.ang *= .4; this.render(); res(); } }; requestAnimationFrame(step); });
    }
  }

  class Swarm {
    constructor(frame, opts = {}) {
      if (!cssDone) { const s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s); cssDone = true; }
      this.frame = frame; this.opts = opts; this.alive = true; this.paused = false; this.cursors = []; this.queue = []; this.seen = []; this.pan = 0; this.scale = 1; this.pageH = 0; this.active = 0;
      if (getComputedStyle(frame).position === 'static') frame.style.position = 'relative';
      this.spot = document.createElement('div'); this.spot.className = 's2-spot'; frame.appendChild(this.spot);
      const roles = opts.roles || ROLES, n = Math.min(opts.count || roles.length, roles.length);
      roles.slice(0, n).forEach(([role, color], i) => { const c = new Cursor(frame, role, color); this.cursors.push(c); setTimeout(() => this.loop(c), opts.roam ? 120 + i * 140 : 250 + i * 380); });
    }
    phase() {}
    pause(on) { this.paused = !!on; }
    setPage(img, pageH) { this.page = img; const imageHeight = img.naturalHeight * 1440 / (img.naturalWidth || 1440); this.pageH = Math.min(pageH || imageHeight, imageHeight); this.scale = this.frame.clientWidth / 1440; img.style.transition = 'transform 1.1s cubic-bezier(.2,.8,.2,1)'; }
    toLocal(rect) { const s = this.scale = this.frame.clientWidth / 1440; return { x: rect.x * s, y: rect.y * s - this.pan, w: rect.w * s, h: Math.min(rect.h, 420) * s }; }
    panTo(rect) { if (!this.page) return; const s = this.scale = this.frame.clientWidth / 1440, H = this.frame.clientHeight, maxPan = Math.max(0, this.pageH * s - H); const want = Math.min(maxPan, Math.max(0, rect.y * s - H * .36)); if (this.pan <= maxPan && Math.abs(want - this.pan) < 40) return; this.pan = want; this.page.style.transform = `translateY(${-this.pan}px)`; this.frame.querySelectorAll('.s2-x').forEach(e => e.remove()); }
    inView(rect) { const r = this.toLocal(rect), H = this.frame.clientHeight; return r.y > 8 && r.y + Math.min(r.h, 120) < H - 60; }
    /* places the job has named: where an agent with nothing of its own may go and look */
    know(evs) { for (const e of evs) { const r = e && e.rect; if (r && r.w > 40 && r.h > 16 && this.seen.length < 60 && !this.seen.some(q => q.x === r.x && q.y === r.y)) this.seen.push({ x: r.x, y: r.y, w: r.w, h: r.h }); } }
    push(evs) { this.know(evs); for (const e of evs) this.queue.push(e); }
    stop() { this.alive = false; this.cursors.forEach(c => c.el.classList.remove('in')); this.spot.classList.remove('on'); setTimeout(() => this.frame.querySelectorAll('.s2-cur,.s2-x,.s2-spot').forEach(e => e.remove()), 700); }
    home(c) { const W = this.frame.clientWidth, H = this.frame.clientHeight, n = this.cursors.length, i = this.cursors.indexOf(c), band = W / n; return { x: Math.max(10, Math.min(W - 150, band * (i + .3))), y: H * (.14 + (i % 3) * .1) }; }
    spotlight(r) { if (!r) { this.spot.classList.remove('on'); return; } Object.assign(this.spot.style, { left: (r.x - 14) + 'px', top: (r.y - 14) + 'px', width: (r.w + 28) + 'px', height: (r.h + 28) + 'px' }); this.spot.classList.add('on'); }
    mk(c, cls, r, html) { const d = document.createElement('div'); d.className = 's2-x ' + cls; d.style.setProperty('--c', c.color); d.style.setProperty('--t', onDark(c.color) ? '#fff' : '#141414'); if (r) Object.assign(d.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' }); if (html) d.innerHTML = html; this.frame.appendChild(d); return d; }
    fade(el, ms = 0) { setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 450); }, ms); }
    async loop(c) {
      while (this.alive) {
        if (this.paused || document.hidden) { await sleep(400); continue; }
        const want = ALIAS[c.role] || c.role; const qi = this.queue.findIndex(e => (ALIAS[e.role] || e.role) === want || !this.cursors.some(k => k.role === (ALIAS[e.role] || e.role)) && c === this.cursors[0]);
        const mine = qi >= 0 ? this.queue.splice(qi, 1)[0] : null;
        try {
          if (mine && this.active < (this.opts.busy || 2)) { this.active++; try { await this.real(c, mine); } finally { this.active--; } }
          else if (mine) { this.queue.splice(Math.min(qi, this.queue.length), 0, mine); await this.look(c); }
          else if (this.opts.demo || this.opts.roam) await this.look(c);
          else { c.say(''); c.el.classList.add('off'); await sleep(rnd(400, 900)); }
        } catch (e) { await sleep(300); /* frame gone */ }
      }
    }
    enter(c) { if (!(c.el.classList.contains('off') || c.y < 0)) return; const h = this.home(c); c.x = h.x + rnd(-20, 20); c.y = c.y < 0 ? -50 : this.frame.clientHeight + 20; c.render(); c.el.classList.remove('off'); }
    /* no event of its own: the agent goes back over a place an event has already named and looks at it — a dashed frame,
       no words — or, before anything is known of the page, waits over it in its own band of the width. */
    async look(c) {
      this.enter(c); c.say('');
      const taken = this.cursors.filter(k => k !== c).map(k => k.at), near = this.page ? this.seen.filter(r => r.y < this.pageH && this.inView(r) && !taken.includes(r)) : [];   // each to a place of its own
      c.at = null;
      if (near.length) { const p = c.at = near[Math.floor(rnd(0, near.length))], r = this.toLocal(p);
        await c.moveTo(r.x + rnd(10, Math.max(12, Math.min(r.w - 30, 220))), r.y + rnd(6, Math.max(8, Math.min(r.h - 10, 90))), { dur: rnd(800, 1500) }); if (!this.alive) return;
        const k = this.mk(c, 's2-peek', this.toLocal(p)); requestAnimationFrame(() => k.classList.add('on')); c.el.classList.add('look'); await sleep(rnd(900, 1700)); c.el.classList.remove('look'); this.fade(k); c.at = null; return; }
      const h = this.home(c); await c.moveTo(h.x + rnd(-40, 40), h.y + rnd(-24, 70), { dur: rnd(1100, 1900) }); if (!this.alive) return; await sleep(rnd(300, 900));   // a short rest: a page with nothing to report yet must still look at work
    }
    /* ── one gesture per role, on the real rect, with the real text ── */
    async real(c, ev) {
      const role = ALIAS[ev.role] || ev.role, text = String(ev.text || ''); this.enter(c); c.el.classList.remove('look'); c.at = null;
      if (!(ev.rect && this.page && ev.rect.y < this.pageH)) { const h = this.home(c); await c.moveTo(h.x + rnd(-20, 20), h.y + rnd(-10, 40)); c.say(text);
        if (role === 'Colour') await this.gSwatch(c, text); else if (role === 'QA') await this.gStamp(c, { x: c.x - 40, y: c.y + 46, w: 150, h: 0 }, text);
        await sleep(Math.min(2800, 1000 + text.length * 25)); c.say(''); return; }
      for (let w = 0; !this.inView(ev.rect) && this.active > 1 && w < 4000 && this.alive; w += 200) await sleep(200);   // the page is not pulled away from under another agent's work
      this.panTo(ev.rect); await sleep(450); const r = this.toLocal(ev.rect); this.spotlight(r);
      await c.moveTo(r.x + Math.min(24, r.w * .2), r.y + Math.min(18, r.h * .5)); c.say(text);
      const big = ev.rect.h >= 150 && ev.rect.w >= 500;
      const G = { Reader: big ? this.gScan : this.gRead, Layout: this.gScan, Copy: this.gUnder, Photos: this.gCrop, Type: this.gRead, Colour: this.gScan, QA: this.gStamp, Render: this.gWipe };
      await (G[role] || this.gScan).call(this, c, r, text, ev);
      await sleep(rnd(500, 900)); c.say(''); this.spotlight(null);
    }
    async gScan(c, r) { const b = this.mk(c, 's2-scan', r, '<u></u>'); requestAnimationFrame(() => b.classList.add('on'));
      await c.moveTo(r.x + 14, r.y + r.h - 12, { dur: 1250 }); if (!this.alive) return; b.classList.add('open'); await c.moveTo(r.x + Math.min(r.w - 20, 120), r.y + r.h * .5, { dur: 500 }); await sleep(500); this.fade(b, 300); }
    async gRead(c, r) { const lines = Math.max(1, Math.min(5, Math.round(r.h / (30 * this.scale + 8)))); const lh = r.h / lines;
      for (let i = 0; i < lines; i++) { const b = this.mk(c, 's2-read', { x: r.x, y: r.y + i * lh + lh * .12, w: r.w * (i === lines - 1 && lines > 1 ? rnd(.5, .9) : 1), h: lh * .76 });
        requestAnimationFrame(() => b.style.transform = 'scaleX(1)'); await c.moveTo(r.x + r.w * .92, r.y + i * lh + lh * .55, { dur: 430 }); this.fade(b, 1500); if (!this.alive) return; } }
    async gUnder(c, r, text) { const w = Math.min(r.w, 460), y = r.y + Math.min(r.h, 64 * this.scale + 20); const u = this.mk(c, 's2-under', { x: r.x, y, w, h: 3 }); requestAnimationFrame(() => u.style.transform = 'scaleX(1)');
      await c.moveTo(r.x + w, y + 2, { dur: 480 }); const chip = this.mk(c, 's2-chip', { x: r.x, y: y + 10, w: 0, h: 0 }); chip.style.width = chip.style.height = 'auto'; chip.style.maxWidth = Math.max(140, this.frame.clientWidth - r.x - 16) + 'px'; chip.textContent = text;
      requestAnimationFrame(() => chip.classList.add('on')); await sleep(900); this.fade(u, 900); this.fade(chip, 1100); }
    async gCrop(c, r) { const k = this.mk(c, 's2-crop', r, '<i></i><i></i><i></i><i></i>'); requestAnimationFrame(() => k.style.transform = 'scale(1)');
      await c.moveTo(r.x + r.w, r.y + r.h, { dur: 600 }); await sleep(300);
      if (this.page) { const l = this.mk(c, 's2-lift', r); const img = this.page.cloneNode(); img.removeAttribute('id'); img.style.cssText = `position:absolute;left:${-r.x}px;top:${-(r.y + this.pan)}px;width:${this.frame.clientWidth}px;max-width:none;height:auto;opacity:1;transition:none;transform:none`; l.appendChild(img);
        requestAnimationFrame(() => l.style.transform = 'translate(16px,-20px) scale(1.04)'); this.fade(l, 1500); }
      this.fade(k, 900); }
    async gSwatch(c, text) { const cols = (text.match(/#[0-9a-f]{3,8}\b/gi) || []).slice(0, 5); if (!cols.length) return; const s = this.mk(c, 's2-sw', { x: Math.min(c.x + 4, this.frame.clientWidth - cols.length * 32 - 20), y: c.y + 50, w: 0, h: 0 }); s.style.width = s.style.height = 'auto';
      for (const col of cols) { const i = document.createElement('i'); i.style.background = col; s.appendChild(i); } requestAnimationFrame(() => s.classList.add('on')); this.fade(s, 2600); }
    async gStamp(c, r, text) { const ok = !/✗|fail|broken|missing|empty|repeat|not shown|could not/i.test(text); const s = this.mk(c, 's2-stamp' + (ok ? '' : ' no'), { x: Math.max(8, r.x + r.w - 110), y: r.y + 10, w: 0, h: 0 }); s.style.width = s.style.height = 'auto'; s.textContent = ok ? '✓ passes' : '✗ held back';
      if (r.h) await c.moveTo(r.x + r.w - 60, r.y + 24, { dur: 500 }); s.classList.add('on'); this.fade(s, 1800); }
    async gWipe(c, r) { const w = this.mk(c, 's2-wipe', { x: 0, y: r.y, w: this.frame.clientWidth, h: 0 }); w.style.transition = 'height .9s cubic-bezier(.2,.8,.2,1),opacity .5s'; requestAnimationFrame(() => w.style.height = r.h + 'px'); await c.moveTo(r.x + r.w * .5, r.y + r.h, { dur: 900 }); this.fade(w, 500); }
  }
  g.Swarm2 = { mount: (frame, opts) => new Swarm(frame, opts), ROLES: ROLES.concat(Object.keys(ALIAS).map(k => [k, ROLES.find(r => r[0] === ALIAS[k])[1]])) };
})(window);
