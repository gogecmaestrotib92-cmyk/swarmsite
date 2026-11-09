/* Swarm Rebuild engine — original implementation (c) 2026, written from scratch for the live-redesign demo.
   Snapshots the page into "layers" (boxes + text), blanks it, then animated agent cursors rebuild it
   section by section while the viewport tours along. No external deps. */
(function (global) {
  'use strict';

  const ROLES = [
    { name: 'Layout',     color: '#3B82F6' },
    { name: 'Typography', color: '#A855F7' },
    { name: 'Copy',       color: '#F59E0B' },
    { name: 'Color',      color: '#EF4444' },
    { name: 'Motion',     color: '#10B981' },
    { name: 'QA',         color: '#06B6D4' },
    { name: 'Layout',     color: '#2563EB' },
    { name: 'Copy',       color: '#D97706' },
  ];
  const NAMES = ['atlas','birch','cobalt','dune','ember','fjord','gale','halo','iris','juno','kite','lumen','mica','nova','onyx','pike','quill','reed','sol','tide','umber','vale','wren','xeno','yarrow','zinc','arc','bloom','crest'];

  const TEXT_TAGS = new Set(['H1','H2','H3','H4','H5','P','A','SPAN','B','SMALL','LI','SUMMARY','EM','I','STRONG','DIV','LABEL']);
  const BOX_SEL = '.card, .record, .rows li, .ways > div, .plans > div, .lifetime, .faq details, .rg, .stores a, .pricelist li, .stats .grid div, .btn, nav';

  // A shared family of agents, with a distinct silhouette and palette per role.
  const AGENT_STYLES = {
    Layout: {light:'#8fa7b1', mid:'#445a65', dark:'#1c282d', edge:'#9cb6c1', accent:'#8fc3d4', mark:'M15 36h12v5H15z', head:'M8 6l5-3h16l5 3 2 12-3 10-4 3H13l-4-3-3-10z', crest:'M16 4V1.8h10V4'},
    Typography: {light:'#b895a2', mid:'#674b58', dark:'#291e25', edge:'#c9a5b3', accent:'#e8a9c4', mark:'M16 36h10M21 36v5', head:'M8 9Q8 3 14 3h14Q34 3 34 9l1 10q0 12-9 12H16Q7 31 7 19z', crest:'M18 4V1h6v3'},
    Copy: {light:'#b4a08a', mid:'#665548', dark:'#28221d', edge:'#ceb69d', accent:'#e2bc8c', mark:'M16 36h10M16 39h7', head:'M9 5Q12 3 15 3h12q7 0 8 7v12q0 9-8 9H15Q7 31 7 22V11z', crest:'M14 4V2h14v2'},
    Color: {light:'#ba908c', mid:'#714b49', dark:'#2b1e1e', edge:'#cfaaa5', accent:'#e7a19d', mark:'M16 37h10M16 40h10', head:'M7 9l6-6h16l6 6v13l-6 9H13l-6-9z', crest:'M16 4V2l5-1 5 1v2'},
    Motion: {light:'#8fac9c', mid:'#46665a', dark:'#1c2923', edge:'#9dbfae', accent:'#9dd4b6', mark:'M16 40l3-3 3 3 3-3', head:'M6 10l9-7h12l9 7-2 13-6 8H14l-6-8z', crest:'M16 4l5-3 5 3'},
    QA: {light:'#a79bb9', mid:'#5c526c', dark:'#231f2b', edge:'#b9aac8', accent:'#c8b0e2', mark:'M16 38l3 2 6-5', head:'M11 4h20l5 8-2 11-5 8H13l-5-8-2-11z', crest:'M16 4V2h10v2'},
  };
  function agentStyle(role) { return AGENT_STYLES[role] || AGENT_STYLES[{Reader:'Typography',Concept:'Color',UX:'Layout',UI:'Motion',Visual:'Copy',Critic:'Color',Contract:'QA',Render:'Layout'}[role]] || AGENT_STYLES.Layout; }
  const AGENT_ART = { Layout:'blue', Typography:'rose', Copy:'ivory', Color:'rose', Motion:'sage', QA:'blue', Reader:'rose', Concept:'rose', UX:'blue', UI:'sage', Visual:'ivory', Critic:'rose', Contract:'blue', Render:'blue', Audit:'rose', Type:'ivory', Photos:'ivory', Ending:'blue' };
  function addAgentArt(el, role) {
    const img = document.createElement('img');
    img.className = 'agent-photo'; img.alt = ''; img.setAttribute('aria-hidden', 'true');
    img.onerror = () => { el.classList.remove('photo-agent'); img.remove(); };
    img.src = '/agents/' + (AGENT_ART[role] || 'blue') + '.webp';
    el.classList.add('photo-agent'); el.appendChild(img);
  }
  const rnd = (a, b) => a + Math.random() * (b - a);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const easeOut = t => 1 - Math.pow(1 - t, 3);

  function isLeafText(el) {
    if (!TEXT_TAGS.has(el.tagName)) return false;
    // element carries its own text node(s) (children may also carry text; those become their own layers)
    for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) return true;
    return false;
  }

  class Cursor {
    constructor(role, idx, layer) {
      this.role = role; this.name = NAMES[idx % NAMES.length];
      this.x = rnd(100, innerWidth - 100); this.y = rnd(-80, -20);
      this.el = document.createElement('div');
      this.el.className = 'sw-cursor' + (Swarm.skin === 'firefly' ? ' fly' : Swarm.skin === 'character' ? ' character' : ''); this.el.style.setProperty('--c', role.color); this.hist = [];
      if (Swarm.skin === 'firefly') { this.trail = document.createElement('div'); this.trail.className = 'sw-trail'; this.trail.style.setProperty('--c', role.color); this.trail.innerHTML = '<i></i>'.repeat(12); this.dots = [...this.trail.children]; layer.appendChild(this.trail); }
      const variant = agentStyle(role.name);
      if (Swarm.skin === 'character') { this.el.style.setProperty('--c', variant.accent); this.el.style.setProperty('--agent-delay', `${-(idx % 7) * .13}s`); }
      const avatar = Swarm.skin === 'character' ? `<svg width="42" height="48" viewBox="0 0 42 48" aria-hidden="true"><defs><linearGradient id="sw-agent-${idx}-shell" x1="0" x2="1" y1="0" y2="1"><stop stop-color="${variant.light}"/><stop offset=".3" stop-color="${variant.mid}"/><stop offset=".7" stop-color="${variant.dark}"/><stop offset="1" stop-color="${variant.mid}"/></linearGradient><linearGradient id="sw-agent-${idx}-glass" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#405257"/><stop offset=".45" stop-color="#17282d"/><stop offset="1" stop-color="#0d1417"/></linearGradient></defs><path d="${variant.crest}" fill="none" stroke="#b7bfc1" stroke-width="1.2"/><path d="${variant.head}" fill="url(#sw-agent-${idx}-shell)" stroke="${variant.edge}" stroke-width="1"/><path d="M10 9l4-2h14l4 2 1 9-3 6H12l-3-6z" fill="#111719" stroke="#818f91" stroke-width=".7"/><path d="M12 11l3-1h12l3 1 .5 6.5-2 3h-15l-2-3z" fill="url(#sw-agent-${idx}-glass)" stroke="#6d8081" stroke-width=".55"/><path d="M14 12.3h12" stroke="#d4e4df" stroke-opacity=".4" stroke-width=".7"/><path d="M14 17h9" stroke="#9eb0ac" stroke-opacity=".6" stroke-width=".7"/><circle cx="27" cy="16.6" r="1.5" fill="${variant.accent}"/><circle cx="27" cy="16.6" r=".55" fill="#fff"/><path d="M7.6 13H5.4v8h2.2M34.4 13h2.2v8h-2.2" fill="#30393b" stroke="#8b9696" stroke-width=".8"/><path d="M15 26.5h12M18 28.5h6" stroke="#a7b1b0" stroke-opacity=".8" stroke-width=".7"/><path d="M16 31v2l-6 2.5-2 7 4 2.5h18l4-2.5-2-7-6-2.5v-2" fill="url(#sw-agent-${idx}-shell)" stroke="#c2cbca" stroke-width=".8"/><path d="M15 35h12l2 4-2 3H15l-2-3z" fill="#171e20" stroke="#7c8988" stroke-width=".6"/><path d="${variant.mark}" fill="none" stroke="${variant.accent}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 36l-2 5M32 36l2 5" stroke="#a3afac" stroke-opacity=".7" stroke-width=".7"/><g class="agent-work" aria-hidden="true"><g class="agent-tool"><path d="M13 32L7 34 2 40" fill="none" stroke="#a8b5b6" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="7" cy="34" r="1.5" fill="#e5ecea"/><path d="M2 40l-2 2" stroke="#e9f3ef" stroke-width="2" stroke-linecap="round"/></g><g class="agent-spark" fill="none" stroke="#d8761e" stroke-width="2" stroke-linecap="round"><path d="M0 42l-6-2M0 42l-5 4M1 43l-1 6M2 42l4 5M2 40l5-3M-1 40l-2-5"/><circle cx="0" cy="42" r="2.4" fill="#fff1b0" stroke="#ec993e"/><circle cx="-7" cy="45" r="1.1" fill="#eea43e" stroke="none"/><circle cx="7" cy="43" r=".9" fill="#f4b85e" stroke="none"/></g></g></svg>` : null;
      this.el.innerHTML = `${avatar || `<svg width="22" height="26" viewBox="0 0 22 26"><path d="M2 2 L2 20 L7 15.5 L10.5 23 L14 21.5 L10.5 14 L17 14 Z" fill="${role.color}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>`}<span class="sw-tag" style="background:${role.color}">${this.name} · ${role.name}</span><span class="sw-task"></span>`;
      if (Swarm.skin === 'character') addAgentArt(this.el, role.name);
        layer.appendChild(this.el);
      this.busy = false; this.render();
    }
    show(on) { if (this.on === on) return; this.on = on; this.el.classList.toggle('off', !on); if (this.trail) this.trail.classList.toggle('off', !on); if (on) { this.hist = []; const sx = this.x, sy = this.y; this.x = sx + rnd(-30, 30); this.y = sy + rnd(-30, 30); } }
    render() { this.el.style.transform = `translate(${this.x}px,${this.y}px)`;
      if (this.dots) { this.hist.unshift([this.x, this.y]); if (this.hist.length > 70) this.hist.pop(); const h1 = this.hist[6]; const sp = h1 ? Math.hypot(this.x - h1[0], this.y - h1[1]) : 0; const vis = Math.min(1, sp / 28);
        this.dots.forEach((d, i) => { const h = this.hist[(i + 1) * 5]; if (!h || !vis) { d.style.opacity = 0; return; } d.style.transform = `translate(${h[0]}px,${h[1]}px) scale(${1 - i * .07})`; d.style.opacity = vis * (this.busy ? .7 : .45) * (1 - i / 12); }); } }
    setTask(t) { this.el.querySelector('.sw-task').textContent = t || ''; this.el.classList.toggle('busy', !!t); }
    async moveTo(x, y, speed) {
      const sx = this.x, sy = this.y, dx = x - sx, dy = y - sy;
      const dist = Math.hypot(dx, dy); const dur = Math.min(900, 180 + dist * 0.55) / speed;
      // slight curve: control point offset
      const cx = sx + dx * 0.5 + rnd(-40, 40), cy = sy + dy * 0.5 + rnd(-40, 40);
      const t0 = performance.now();
      return new Promise(res => {
        const step = now => {
          let t = Math.min(1, (now - t0) / dur); const e = easeOut(t);
          this.x = (1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * x;
          this.y = (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * y;
          this.render();
          if (t < 1) requestAnimationFrame(step); else res();
        };
        requestAnimationFrame(step);
      });
    }
    async idle() {
      if (this.busy) return;
      await this.moveTo(this.x + rnd(-30, 30), this.y + rnd(-20, 20), 0.6);
    }
  }

  class Swarm {
    constructor(opts) {
      this.opts = Object.assign({ agents: 24, speed: 1, sectionSelector: '[data-agent]', onProgress: null, onDone: null, hud: true, skin: 'arrow' }, opts); Swarm.skin = this.opts.skin;
      this.layers = []; this.done = 0; this.agentsUsed = new Set();
    }

    snapshot() {
      const sections = [...document.querySelectorAll(this.opts.sectionSelector)];
      this.sections = sections.map(sec => {
        const BS = this.opts.boxSel || BOX_SEL; const boxes = [...sec.querySelectorAll(BS)].concat(sec.matches(BS) ? [sec] : []);
        const texts = [...sec.querySelectorAll('*')].filter(isLeafText);
        const layers = [];
        boxes.forEach(el => layers.push({ kind: 'box', el, sec }));
        texts.forEach(el => layers.push({ kind: 'text', el, sec, html: el.innerHTML, text: el.textContent }));
        // visual-only elements (svg/img/decorative divs with background)
        [...sec.querySelectorAll('img, svg, i')].filter(el => !el.closest('.hero-crew, .peek')).forEach(el => layers.push({ kind: 'img', el, sec }));
        const lab = sec.querySelector('.lab, h2, h1'); const nm = sec.getAttribute('data-agent') || (lab && lab.textContent.trim().slice(0, 24)) || sec.id || sec.tagName.toLowerCase(); return { el: sec, name: nm, layers };
      });
      this.total = this.sections.reduce((n, s) => n + s.layers.length, 0);
    }

    blank() {
      document.documentElement.classList.add('sw-building');
      this.sections.forEach(s => {
        s.layers.forEach(L => {
          L.el.classList.add('sw-hidden-' + L.kind);
          if (L.kind === 'text') { L.el.setAttribute('data-sw-text', '1'); }
        });
        s.el.classList.add('sw-sec-pending');
      });
    }

    mountUI() {
      this.layer = document.createElement('div'); this.layer.className = 'sw-layer'; document.body.appendChild(this.layer);
      if (this.opts.hud) {
        this.hud = document.createElement('div'); this.hud.className = 'sw-hud';
        this.hud.innerHTML = `<div class="sw-dots"></div><span class="sw-k"><b class="sw-agents">0</b> agents</span><i class="sw-sep"></i><span class="sw-k hide-m"><b class="sw-count">0</b> / ${this.total} layers</span><div class="sw-bar"><i></i></div><span class="sw-sec">Touring</span><i class="sw-sep"></i><button class="sw-speed">1×</button><button class="sw-skip">Skip</button>`;
        document.body.appendChild(this.hud);
        this.hud.querySelector('.sw-speed').onclick = () => { this.opts.speed = this.opts.speed >= 4 ? 1 : this.opts.speed * 2; this.hud.querySelector('.sw-speed').textContent = this.opts.speed + '×'; };
        this.hud.querySelector('.sw-skip').onclick = () => { this.skip = true; };
      }
      const n = this.opts.agents;
      this.cursors = Array.from({ length: n }, (_, i) => new Cursor(ROLES[i % ROLES.length], i, this.layer));
      if (this.hud) this.hud.querySelector('.sw-dots').innerHTML = ROLES.slice(0, 6).map(r => `<i style="background:${r.color};color:${r.color}"></i>`).join('');
    }

    progress(secName) {
      if (!this.hud) return;
      this.hud.querySelector('.sw-count').textContent = this.done;
      this.hud.querySelector('.sw-agents').textContent = this.agentsUsed.size;
      this.hud.querySelector('.sw-bar i').style.width = (100 * this.done / this.total) + '%';
      if (secName) this.hud.querySelector('.sw-sec').textContent = secName;
      this.opts.onProgress && this.opts.onProgress(this.done, this.total, secName);
    }

    pageXY(el) { const r = el.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; }

    async tour(secEl) {
      const r = secEl.getBoundingClientRect(); const target = scrollY + r.top - Math.max(40, (innerHeight - Math.min(r.height, innerHeight)) / 2);
      const start = scrollY, dist = target - start; const dur = Math.min(1100, 300 + Math.abs(dist) * 0.5) / this.opts.speed; const t0 = performance.now();
      await new Promise(res => { const step = now => { const t = Math.min(1, (now - t0) / dur); scrollTo(0, start + dist * easeOut(t)); if (t < 1) requestAnimationFrame(step); else res(); }; requestAnimationFrame(step); });
    }

    async buildBox(c, L) {
      const p = this.pageXY(L.el); const sp = this.opts.speed;
      c.setTask('placing block');
      await c.moveTo(p.x - scrollX + 4, p.y - scrollY + 4, sp);
      // selection outline grows from the corner
      const sel = document.createElement('div'); sel.className = 'sw-sel'; sel.style.borderColor = c.role.color;
      sel.style.left = p.x + 'px'; sel.style.top = p.y + 'px'; sel.style.width = '0px'; sel.style.height = '0px';
      const dim = document.createElement('span'); dim.className = 'sw-dim'; dim.style.background = c.role.color; dim.textContent = `${Math.round(p.w)} × ${Math.round(p.h)}`; sel.appendChild(dim);
      this.layer.appendChild(sel);
      await c.moveTo(p.x - scrollX + p.w - 4, p.y - scrollY + p.h - 4, sp * 1.4);
      sel.style.transition = `width ${260 / sp}ms ease-out, height ${260 / sp}ms ease-out`;
      sel.style.width = p.w + 'px'; sel.style.height = p.h + 'px';
      await sleep(300 / sp);
      L.el.classList.remove('sw-hidden-box'); L.el.classList.add('sw-pop');
      sel.style.opacity = '0'; await sleep(220 / sp); sel.remove();
    }

    async buildText(c, L) {
      const p = this.pageXY(L.el); const sp = this.opts.speed;
      const len = L.text.length;
      c.setTask(len > 80 ? 'writing paragraph' : len > 20 ? 'setting heading' : 'labelling');
      await c.moveTo(p.x - scrollX - 6, p.y - scrollY + Math.min(p.h, 28) / 2, sp);
      L.el.classList.remove('sw-hidden-text');
      const simple = L.el.children.length === 0;
      if (simple && len <= 220) {
        // type it out
        const caret = document.createElement('i'); caret.className = 'sw-caret'; caret.style.background = c.role.color;
        L.el.textContent = ''; L.el.appendChild(caret);
        const perChar = Math.max(6, Math.min(28, 900 / len)) / sp;
        for (let i = 1; i <= len; i++) {
          L.el.textContent = L.text.slice(0, i); L.el.appendChild(caret);
          if (i % 2 === 0) await sleep(perChar);
          if (i % 12 === 0) { const q = this.pageXY(L.el); c.x = Math.min(q.x + q.w, q.x + i * (q.w / len)) - scrollX; c.y = q.y - scrollY + Math.min(q.h, 28) / 2; c.render(); }
        }
        caret.remove(); L.el.innerHTML = L.html;
      } else {
        L.el.classList.add('sw-fade');
        await sleep(240 / sp);
      }
    }

    async buildImg(c, L) {
      const p = this.pageXY(L.el); const sp = this.opts.speed;
      c.setTask('placing asset');
      await c.moveTo(p.x - scrollX + p.w / 2, p.y - scrollY + p.h / 2, sp);
      L.el.classList.remove('sw-hidden-img'); L.el.classList.add('sw-pop');
      await sleep(160 / sp);
    }

    async run() {
      this.t0 = performance.now();
      this.snapshot(); this.blank(); this.mountUI(); this.progress('Touring');
      if (!this.opts.noScroll) scrollTo(0, 0);
      await sleep(600);
      for (const sec of this.sections) {
        if (this.skip) break;
        sec.el.classList.remove('sw-sec-pending');
        if (!this.opts.noScroll) await this.tour(sec.el);
        this.progress(sec.name);
        // order: boxes → text (top to bottom) → imgs ; run with a pool of cursors
        const queue = [...sec.layers.filter(l => l.kind === 'box'), ...sec.layers.filter(l => l.kind === 'text').sort((a, b) => this.pageXY(a.el).y - this.pageXY(b.el).y), ...sec.layers.filter(l => l.kind === 'img')];
        const pool = Math.min(this.cursors.length, Math.max(3, Math.ceil(queue.length / 3)), innerWidth < 700 ? 4 : 7);
        const free = this.cursors.slice().sort(() => Math.random() - 0.5).slice(0, pool);
        const worker = async c => {
          while (queue.length && !this.skip) {
            const L = queue.shift(); c.busy = true; this.agentsUsed.add(c.name);
            try { if (L.kind === 'box') await this.buildBox(c, L); else if (L.kind === 'text') await this.buildText(c, L); else await this.buildImg(c, L); } catch (e) { console.warn(e); }
            this.done++; this.progress();
            c.setTask(''); c.busy = false;
          }
        };
        // only the agents with work are on screen; the rest are simply not there until they are needed
        free.forEach(c => c.show(true)); this.cursors.filter(c => !free.includes(c)).forEach(c => c.show(false));
        await Promise.all(free.map(worker));
      }
      if (this.skip) this.finishInstant();
      this.finish();
    }

    finishInstant() {
      this.sections.forEach(s => s.layers.forEach(L => { L.el.classList.remove('sw-hidden-' + L.kind); if (L.kind === 'text') L.el.innerHTML = L.html; }));
      this.done = this.total; this.progress();
    }

    async finish() {
      const secs = ((performance.now() - this.t0) / 1000).toFixed(1);
      // cursors fly off
      this.cursors.forEach(c => c.setTask(''));
      await Promise.all(this.cursors.map(c => c.moveTo(rnd(-200, innerWidth + 200), rnd(-300, -100), 0.8)));
      this.layer.remove();
      document.documentElement.classList.remove('sw-building');
      document.querySelectorAll('[data-sw-text]').forEach(e => e.removeAttribute('data-sw-text'));
      document.querySelectorAll('.rv').forEach(e => e.classList.add('in'));
      if (this.hud) {
        this.hud.innerHTML = `<div class="sw-dots">${ROLES.slice(0, 6).map(r => `<i style="background:${r.color};color:${r.color}"></i>`).join('')}</div><span class="sw-k">Rebuilt by <b>${this.agentsUsed.size}</b> agents in <b>${secs}s</b></span><i class="sw-sep"></i><button class="sw-replay">Replay</button><button class="sw-close">×</button>`;
        this.hud.querySelector('.sw-replay').onclick = () => { this.hud.remove(); scrollTo(0, 0); new Swarm(this.opts).run(); };
        this.hud.querySelector('.sw-close').onclick = () => this.hud.remove();
      }
      this.opts.onDone && this.opts.onDone({ agents: this.agentsUsed.size, seconds: secs, layers: this.total });
    }
  }

  const CSS = `
  .sw-layer{position:absolute;inset:0 auto auto 0;width:100%;height:0;pointer-events:none;z-index:9000}
  .sw-cursor{position:fixed;left:0;top:0;pointer-events:none;z-index:9001;will-change:transform;transition:opacity .5s}
  .sw-cursor.off,.sw-trail.off{opacity:0!important;transition:opacity .35s}
  .sw-cursor.fly svg{display:none}.sw-cursor.fly::before{content:"";position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 28%,transparent),0 0 18px 4px color-mix(in srgb,var(--c) 55%,transparent),0 0 44px 10px color-mix(in srgb,var(--c) 25%,transparent)}
  .sw-cursor.fly::after{content:"";position:absolute;left:-3px;top:-4px;width:4px;height:4px;border-radius:50%;background:#fff;opacity:.9}
  .sw-cursor.fly.busy::before{animation:swpulse 1.1s ease-in-out infinite}@keyframes swpulse{50%{transform:scale(1.25)}}
  .sw-cursor.fly .sw-tag{margin-left:12px}
  .sw-trail{position:fixed;left:0;top:0;pointer-events:none;z-index:9000}.sw-trail i{position:absolute;left:-4px;top:-4px;width:8px;height:8px;border-radius:50%;background:var(--c);opacity:0;filter:blur(.6px)}
  .sw-cursor:not(.busy) .sw-tag{opacity:0;transform:translateY(-3px)}
  .sw-cursor .sw-tag{transition:opacity .25s,transform .25s;position:absolute;left:18px;top:18px;color:#fff;font:600 11px/1 system-ui,sans-serif;padding:4px 7px;border-radius:4px;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.2)}
  .sw-cursor .sw-task{position:absolute;left:18px;top:40px;color:#111;background:#fff;font:500 10.5px/1 system-ui,sans-serif;padding:3px 6px;border-radius:3px;white-space:nowrap;opacity:.9;border:1px solid rgba(0,0,0,.08)}
  .sw-cursor .sw-task:empty{display:none}
  .sw-cursor.character svg{overflow:visible}
  .sw-cursor.character .agent-work{opacity:0}
  .sw-cursor.character.busy .agent-work{opacity:1}
  .sw-cursor.character.busy svg{transform-origin:50% 85%;animation:agent-lean .9s ease-in-out infinite alternate;animation-delay:var(--agent-delay,0s)}
  .sw-cursor.character.busy .agent-tool{transform-origin:13px 32px;animation:agent-weld .45s ease-in-out infinite alternate;animation-delay:var(--agent-delay,0s)}
  .sw-cursor.character.busy .agent-spark{filter:drop-shadow(0 0 2px #f4aa36);transform-origin:0px 42px;animation:agent-sparks .8s ease-in-out infinite;animation-delay:var(--agent-delay,0s)}
  @keyframes agent-lean{0%{transform:rotate(-7deg) translateY(0)}100%{transform:rotate(8deg) translateY(2px)}}
  @keyframes agent-weld{from{transform:rotate(-10deg)}to{transform:rotate(17deg)}}
  @keyframes agent-sparks{0%,100%{opacity:.55;transform:scale(1)}35%{opacity:1;transform:scale(1.8)}65%{opacity:.8;transform:scale(1.3)}}
  .sw-cursor.photo-agent svg{position:relative;z-index:2;pointer-events:none}
  .sw-cursor.photo-agent svg > :not(defs):not(.agent-work){display:none}
  .sw-cursor.photo-agent .agent-tool{display:none}
  .sw-cursor.photo-agent .agent-work{transform:translate(38px,-20px)}
  .sw-cursor.photo-agent .agent-photo{position:absolute;z-index:1;left:-5px;top:-4px;width:56px;height:56px;object-fit:contain;pointer-events:none;filter:drop-shadow(0 3px 5px #0004);transform-origin:50% 85%}
  .sw-cursor.photo-agent.busy .agent-photo{animation:agent-lean .9s ease-in-out infinite alternate;animation-delay:var(--agent-delay,0s)}
  .sw-cursor.photo-agent .sw-tag{z-index:3;left:51px}
  @media(prefers-reduced-motion:reduce){.sw-cursor.photo-agent .agent-photo{animation:none!important}}
  @media(prefers-reduced-motion:reduce){.sw-cursor.character .agent-work{display:none}.sw-cursor.character.busy svg{animation:none}}
  .sw-cursor.character svg{filter:drop-shadow(0 3px 5px rgba(0,0,0,.24))}
  .sw-cursor.character .sw-tag{left:39px;top:14px;background:#242729!important;color:#f8f8f6;border:1px solid #ffffff38;border-radius:5px;font:500 10px/1.2 ui-monospace,monospace;letter-spacing:.01em;padding:6px 8px;box-shadow:0 4px 14px #0003}
  .sw-cursor.character .sw-tag::before{content:"";display:inline-block;width:5px;height:5px;margin-right:6px;vertical-align:1px;border-radius:50%;background:var(--c)}
  .sw-cursor.character .sw-task{left:39px;top:37px;border-radius:4px;font:400 10px/1.2 ui-monospace,monospace;color:#444;padding:4px 6px}
  .sw-sel{position:absolute;border:1.5px solid;box-sizing:border-box;z-index:8999;pointer-events:none;transition:opacity .2s;background:rgba(59,130,246,.04)}
  .sw-sel::before,.sw-sel::after{content:"";position:absolute;width:6px;height:6px;background:#fff;border:1.5px solid inherit;border-color:inherit}
  .sw-sel::before{left:-4px;top:-4px}.sw-sel::after{right:-4px;bottom:-4px}
  .sw-dim{position:absolute;left:50%;bottom:-22px;transform:translateX(-50%);color:#fff;font:600 10px/1 system-ui;padding:3px 6px;border-radius:3px;white-space:nowrap}
  .sw-hidden-box{border-color:transparent!important;background:transparent!important;box-shadow:none!important}
  .sw-hidden-box::before,.sw-hidden-box::after{opacity:0}
  .sw-hidden-box *{border-color:transparent!important}
  .sw-hidden-text{visibility:hidden}
  .sw-hidden-img{opacity:0}
  .sw-pop{animation:sw-pop .35s ease-out}
  @keyframes sw-pop{from{opacity:.2;transform:scale(.985)}to{opacity:1;transform:none}}
  .sw-fade{animation:sw-fade .4s ease-out}
  @keyframes sw-fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  .sw-caret{display:inline-block;width:2px;height:.9em;vertical-align:-.1em;margin-left:1px;animation:sw-blink .7s steps(1) infinite}
  @keyframes sw-blink{50%{opacity:0}}
  .sw-building .rv{opacity:1!important;transform:none!important;transition:none!important}
  .sw-hud{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:9500;background:rgba(250,250,249,.86);color:#111;border:1px solid rgba(17,17,17,.12);border-radius:999px;padding:9px 10px 9px 14px;display:flex;align-items:center;gap:14px;font:500 12.5px/1 'Instrument Sans',system-ui,sans-serif;box-shadow:0 18px 50px rgba(0,0,0,.14),0 1px 0 rgba(255,255,255,.6) inset;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);white-space:nowrap;letter-spacing:.005em}
  .sw-hud b{font-weight:500;font-variant-numeric:tabular-nums}
  .sw-hud span{color:#6B6B68}
  .sw-hud .sw-k{font:400 10.5px/1 'JetBrains Mono',ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:#6B6B68}
  .sw-hud .sw-dots{display:flex;align-items:center}
  .sw-hud .sw-dots i{width:9px;height:9px;border-radius:50%;margin-right:-3px;box-shadow:0 0 0 2px rgba(250,250,249,.9),0 0 10px 1px color-mix(in srgb,currentColor 60%,transparent);color:inherit;animation:swglow 2.4s ease-in-out infinite}
  .sw-hud .sw-dots i:nth-child(2){animation-delay:.4s}.sw-hud .sw-dots i:nth-child(3){animation-delay:.8s}.sw-hud .sw-dots i:nth-child(4){animation-delay:1.2s}.sw-hud .sw-dots i:nth-child(5){animation-delay:1.6s}.sw-hud .sw-dots i:nth-child(6){animation-delay:2s}
  @keyframes swglow{50%{transform:scale(1.18)}}
  .sw-hud .sw-sep{width:1px;height:16px;background:rgba(17,17,17,.12)}
  .sw-hud .sw-bar{width:140px;height:1px;background:rgba(17,17,17,.14);position:relative;overflow:visible}
  .sw-hud .sw-bar i{display:block;height:100%;width:0;background:#111;transition:width .3s cubic-bezier(.2,.8,.2,1)}
  .sw-hud .sw-bar i::after{content:"";position:absolute;right:-3px;top:-3px;width:7px;height:7px;border-radius:50%;background:#111;box-shadow:0 0 10px 2px rgba(17,17,17,.25)}
  .sw-hud .sw-sec{font:400 10.5px/1 'JetBrains Mono',ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:#111;background:transparent;padding:0;border-radius:0;opacity:1}
  .sw-hud .sw-sec::before{content:"→ ";color:#6B6B68}
  .sw-hud button{background:transparent;color:#111;border:1px solid rgba(17,17,17,.18);border-radius:999px;padding:7px 11px;font:500 12px 'Instrument Sans',system-ui,sans-serif;cursor:pointer;transition:background .15s,transform .15s}
  .sw-hud button:hover{background:#111;color:#fff;border-color:#111}.sw-hud button:active{transform:scale(.97)}
  .sw-hud .sw-close{padding:7px 9px}
  @media(max-width:700px){.sw-hud{gap:10px;padding:8px 8px 8px 12px;bottom:14px}.sw-hud .sw-bar{width:70px}.sw-hud .sw-k.hide-m,.sw-hud .sw-sec{display:none}}
  `;
  const style = document.createElement('style'); style.textContent = CSS; document.head.appendChild(style);

  global.Swarm = Swarm;
})(window);
