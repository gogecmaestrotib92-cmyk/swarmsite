/* ARTEFACTS — data-driven signature components. Each reads its data from a JSON attribute, draws itself,
   and animates once with GSAP when scrolled into view (ScrollTrigger). Picked by diagnose.py:
     price-ladder   : audit finds ≥4 comparable prices/quotes for one item  (data-ladder='[{"name","v","best"}]')
     ledger-curve   : audit finds results over time (wins/losses, ROI, revenue) (data-curve='[n,n,n…]')
     live-counter   : audit finds a growing count (analyses, orders, users)   (data-counter="28139" data-rate="0.4")
     gap-meter      : two numbers whose difference is the point (your price vs fair price) (data-gap='{"a":1.86,"b":1.96,"la":"…","lb":"…"}')
   Mobile: ladder collapses to top 6 + "and N more", curve keeps full width, counters unchanged. */
(() => {
  const g = () => window.gsap; const ST = () => window.ScrollTrigger;
  const css = `
  .af-ladder{display:grid;gap:6px;font-family:var(--font-mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase}
  .af-ladder .r{display:grid;grid-template-columns:minmax(90px,1fr) 5fr auto;gap:12px;align-items:center;min-height:22px}
  .af-ladder .bar{height:10px;background:var(--line);position:relative;overflow:hidden}
  .af-ladder .bar i{position:absolute;inset:0;width:0;background:var(--muted);transform-origin:left}
  .af-ladder .r.best .bar i{background:var(--accent)}.af-ladder .r.best .v,.af-ladder .r.best .n{color:var(--accent-ink,var(--accent))}
  .af-ladder .r.worst .bar i{background:var(--neg,#E06A4A)}.af-ladder .r.worst .v{color:var(--neg,#E06A4A)}
  .af-ladder .v{font-family:var(--font-display);font-weight:700;font-size:18px;letter-spacing:0;min-width:3.2ch;text-align:right}
  .af-ladder .more{color:var(--muted);padding-top:6px}
  .af-ladder .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .af-curve{position:relative;width:100%;height:100%;min-height:160px}
  .af-curve svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
  .af-curve .p{fill:none;stroke:var(--chart-1,var(--accent));stroke-width:2;vector-effect:non-scaling-stroke}
  .af-curve .z{stroke:var(--line);stroke-width:1;stroke-dasharray:3 4;vector-effect:non-scaling-stroke}
  .af-curve .a{fill:var(--accent);opacity:.12}
  .af-curve .end{position:absolute;right:0;transform:translate(0,-50%);font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;color:var(--accent);background:var(--paper);padding:2px 6px;border:1px solid var(--accent)}
  .af-gap{display:grid;grid-template-columns:1fr auto 1fr;gap:18px;align-items:end}
  .af-gap b{font-family:var(--font-display);font-weight:700;font-size:clamp(40px,5vw,72px);line-height:1;display:block}
  .af-gap .d{font-family:var(--font-mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);border:1px solid var(--accent);padding:8px 10px;align-self:center;white-space:nowrap}
  .af-gap .l{font-family:var(--font-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:10px}
  @media(max-width:700px){.af-ladder .r{grid-template-columns:minmax(70px,1fr) 4fr auto}.af-ladder .v{font-size:15px}.af-gap{grid-template-columns:1fr;gap:12px}.af-gap .d{justify-self:start}}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  const A = {
    'price-ladder'(el) {
      const rows = JSON.parse(el.dataset.ladder); const max = Math.max(...rows.map(r => r.v)), min = Math.min(...rows.map(r => r.v));
      const mobile = innerWidth < 700; const show = mobile ? rows.slice(0, 6) : rows;
      el.classList.add('af-ladder');
      el.innerHTML = show.map(r => `<div class="r${r.v === max ? ' best' : ''}${r.v === min ? ' worst' : ''}"><span class="n">${r.name}</span><span class="bar"><i style="--w:${(r.v - min * .85) / (max - min * .85) * 100}%"></i></span><span class="v" data-v="${r.v}">${r.v.toFixed(2)}</span></div>`).join('') + (rows.length > show.length ? `<div class="more">and ${rows.length - show.length} more books</div>` : '');
      const bars = el.querySelectorAll('.bar i'), vals = el.querySelectorAll('.v');
      if (!g()) { bars.forEach(b => b.style.width = b.style.getPropertyValue('--w')); return; }
      const tl = g().timeline({ scrollTrigger: { trigger: el, start: 'top 80%', once: true } });
      bars.forEach((b, i) => tl.to(b, { width: b.style.getPropertyValue('--w'), duration: .7, ease: 'power3.out' }, i * .04));
      vals.forEach((v, i) => { const t = +v.dataset.v; const o = { x: t * .6 }; tl.to(o, { x: t, duration: .7, ease: 'power3.out', onUpdate: () => v.textContent = o.x.toFixed(2) }, i * .04); });
    },
    'ledger-curve'(el) {
      const d = JSON.parse(el.dataset.curve); const W = 100, H = 100; const mn = Math.min(0, ...d), mx = Math.max(0, ...d);
      const x = i => i / (d.length - 1) * W, y = v => H - (v - mn) / (mx - mn || 1) * H;
      const path = d.map((v, i) => (i ? 'L' : 'M') + x(i).toFixed(2) + ' ' + y(v).toFixed(2)).join(' ');
      el.classList.add('af-curve');
      el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line class="z" x1="0" x2="${W}" y1="${y(0)}" y2="${y(0)}"/><path class="a" d="${path} L${W} ${y(0)} L0 ${y(0)} Z"/><path class="p" d="${path}"/></svg><span class="end" style="top:${y(d[d.length - 1])}%">${el.dataset.label || (d[d.length - 1] > 0 ? '+' : '') + d[d.length - 1]}</span>`;
      const p = el.querySelector('.p'), L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; const a = el.querySelector('.a'); a.style.opacity = 0; const end = el.querySelector('.end'); end.style.opacity = 0;
      if (!g()) { p.style.strokeDashoffset = 0; a.style.opacity = .12; end.style.opacity = 1; return; }
      g().timeline({ scrollTrigger: { trigger: el, start: 'top 75%', once: true } }).to(p, { strokeDashoffset: 0, duration: 1.6, ease: 'power2.inOut' }).to(a, { opacity: .12, duration: .5 }, '-=.4').to(end, { opacity: 1, duration: .3 }, '-=.2');
    },
    'live-counter'(el) {
      const base = +el.dataset.counter, rate = +(el.dataset.rate || 0); const t0 = Date.now(); const fmt = n => Math.round(n).toLocaleString('en-US');
      el.textContent = fmt(base); if (rate) setInterval(() => el.textContent = fmt(base + (Date.now() - t0) / 60000 * rate), 1500);
    },
    'gap-meter'(el) {
      const d = JSON.parse(el.dataset.gap); const pa = 1 / d.a, pb = 1 / d.b; const gap = ((pa - pb) * 100).toFixed(1);
      el.classList.add('af-gap');
      el.innerHTML = `<div><span class="l">${d.la}</span><b>${d.a.toFixed(2)}</b></div><span class="d">${d.verb || 'edge'} ${gap > 0 ? '+' : ''}${gap}pp</span><div><span class="l">${d.lb}</span><b>${d.b.toFixed(2)}</b></div>`;
    }
  };
  window.Artefacts = { init(root = document) { root.querySelectorAll('[data-artefact]').forEach(el => { const k = el.dataset.artefact; if (A[k] && !el.dataset.afDone) { el.dataset.afDone = 1; A[k](el); } }); } };
})();
