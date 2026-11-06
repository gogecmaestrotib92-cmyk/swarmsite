"""render.py — beats content JSON + concept → page HTML (body + page CSS).
Each concept has its own section renderers; shared components come from components.css.
Usage: from render import render; html = render(content, 'C2')"""
import html as H, json

def e(s): return H.escape(str(s))

def artefact_card(a, cls='card dark'):
    rows = ''.join(f'<div class="row{" best" if len(r) > 2 and r[2] == "best" else ""}"><span>{e(r[0])}</span><b class="num{" accent" if r[0].startswith("Model") else ""}">{e(r[1])}{("<small>" + e(r[2]) + "</small>") if len(r) > 2 and r[2] != "best" else ""}</b></div>' for r in a['rows'])
    teams = f'<div class="teams">{e(a["teams"][0])}<br>{e(a["teams"][1])}</div>' if a.get('teams') else ''
    return f'<div class="{cls}" data-move="fade-rise"><div class="top"><span class="label">{e(a["top"][0])}</span><span class="label">{e(a["top"][1])}</span></div>{teams}{rows}<div class="verdict">{e(a.get("verdict", ""))}<strong>{e(a.get("verdict_strong") or a.get("strong", ""))}</strong></div></div>'

def faq(c):
    return ''.join(f'<details{" open" if i == 0 else ""}><summary><span class="label">■ 0{i+1}</span>{e(q)}<span class="plus">+</span></summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(c['faq']['items']))

def wordmark(c):
    return f'<a class="wordmark" href="#"><img class="mark" src="{{{{LOGO}}}}" alt="{e(c["brand"]["name"])}">{e(c["brand"]["name"])}<em>{e(c["brand"]["badge"])}</em></a>'

# ───────────────────────────── C2 · Swiss modular grid ─────────────────────────────
C2_CSS = """
body{background:var(--paper);color:var(--ink)}
.g{display:grid;border:1px solid var(--line);border-bottom:0}
.g>*{border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:22px;position:relative;min-width:0}
.g>*:last-child,.g.nb>*:nth-child(var(--cols)n){border-right:0}
.g .tag{position:absolute;right:10px;bottom:8px;font-family:var(--font-mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:inherit;opacity:.7}
.fill{background:var(--accent);color:var(--accent-contrast)}.inkc{background:var(--ink);color:var(--paper)}.cell{background:var(--panel)}
.navg{grid-template-columns:auto 1fr auto auto;align-items:center;border-top:0;position:sticky;top:0;background:var(--paper);z-index:50}
.navg>*{padding:14px 20px}.navg .links{display:flex;gap:26px;font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.navg .time{font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.navg .cta{background:var(--ink);color:var(--paper);font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;text-decoration:none;border-right:0}
.herog{grid-template-columns:repeat(5,1fr);grid-auto-rows:minmax(150px,auto)}
.herog .big{grid-column:1/4;grid-row:1/3;padding-bottom:40px;display:flex;flex-direction:column;justify-content:flex-end}
.herog .h1{font-size:clamp(64px,9.5vw,150px);line-height:.85;margin:0}
.herog .art{grid-column:4/6;grid-row:1/4;padding:0;background:var(--panel)}
.herog .art .row{gap:16px}.herog .art .row small{white-space:nowrap}
.herog .art .card{border:0;background:transparent;color:var(--ink);padding:20px;font-size:13px}
.herog .lede{grid-column:1/3;align-self:end}
.herog .n{grid-column:3/4}.herog .num{font-size:52px;line-height:1;display:block;margin-top:14px}
.statg{grid-template-columns:repeat(3,1fr)}.statg>*{min-height:200px}.statg .num{font-size:clamp(48px,5vw,80px);line-height:1;display:block;margin:18px 0 10px}
.band{background:var(--ink);color:var(--paper);padding:clamp(56px,8vw,120px) 0}
.band .g{border-color:rgba(255,255,255,.25)}.band .g>*{border-color:rgba(255,255,255,.25)}
.band .card{background:transparent;border:1px solid rgba(255,255,255,.25);color:var(--paper);font-size:13px}
.band .label{color:rgba(255,255,255,.65)}.band .row{border-color:rgba(255,255,255,.18)}
.svc{grid-template-columns:1fr 1fr}.svc .nlist{display:flex;flex-direction:column;gap:0;padding:0}
.svc .nlist div{display:flex;gap:28px;align-items:baseline;padding:28px 22px;border-bottom:1px solid rgba(255,255,255,.25);font-family:var(--font-display);font-weight:700;font-size:clamp(28px,3.4vw,52px);line-height:1;text-transform:uppercase}
.svc .nlist div:last-of-type{border-bottom:0}.svc .nlist i{font-family:var(--font-mono);font-style:normal;font-size:12px;letter-spacing:.12em}
.listg>*{display:grid;grid-template-columns:60px 1fr auto;gap:24px;align-items:center;font-family:var(--font-display);font-weight:700;font-size:clamp(22px,3vw,44px);text-transform:uppercase;line-height:1}
.listg .num{font-size:inherit}.listg .label{font-size:11px}
.giantq{font-family:var(--font-display);font-weight:700;font-size:clamp(34px,5.2vw,86px);line-height:.95;text-transform:uppercase;letter-spacing:-.02em;padding:clamp(40px,6vw,96px) 0;max-width:22ch}
.plang{grid-template-columns:1fr 1fr 1fr}.plang .tier{min-height:420px;display:flex;flex-direction:column;justify-content:space-between}
.plang .tier .num{font-size:clamp(56px,6vw,96px);line-height:1;display:block;margin:16px 0}
.plang ul{list-style:none;margin:16px 0}.plang li{padding:8px 0;border-top:1px solid var(--line);font-size:14px}
.plang .fill ul li{border-color:rgba(0,0,0,.18)}
.trow{display:grid;grid-template-columns:60px 1fr 2fr;gap:24px;padding:26px 0;border-top:1px solid var(--line)}
.trow .h3{text-transform:uppercase;font-family:var(--font-display);font-weight:700}
.footg{grid-template-columns:2fr 1fr 1fr 1fr}.footg>*{min-height:160px}
.footg h5{font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:12px;color:var(--muted)}
.footg ul{list-style:none;font-size:14px;line-height:1.9}
.clock{font-family:var(--font-display);font-weight:700;font-size:34px;line-height:1;margin-top:8px}
.ending{border-top:0;padding-top:0}.ending .giant{font-size:clamp(90px,19vw,300px)}
@media(max-width:900px){.navg{grid-template-columns:1fr auto}.navg .links,.navg .time{display:none}.herog{grid-template-columns:1fr 1fr}.herog .big{grid-column:1/3;grid-row:auto}.herog .art{grid-column:1/3;grid-row:auto}.herog .lede{grid-column:1/3}.herog .n{grid-column:auto}.statg,.plang,.svc,.footg{grid-template-columns:1fr}.svc .nlist div{font-size:24px}.listg>*{grid-template-columns:40px 1fr auto;font-size:20px}.trow{grid-template-columns:1fr}}
"""

def render_C2(c):
    b, h, r, w, p, t, pl, f, en = c['brand'], c['hero'], c['record'], c['ways'], c['price'], c['trust'], c['plans'], c['faq'], c['ending']
    links = ''.join(f'<a href="{e(u)}">{e(l)}</a>' for u, l in c['nav']['links'])
    cells = ''.join(f'<div{" class=\"fill\"" if cl == "pos" else (" class=\"inkc\"" if cl == "neg" else "")}><span class="label">{e(a)}</span><b class="num" data-move="number-scramble">{e(n)}</b><span class="tag">{e(s)}</span></div>' for a, n, s, cl in r['cells'])
    nlist = ''.join(f'<div><i>0{i+1}</i>{e(s)}</div>' for i, s in enumerate(w['steps']))
    panels = ''.join(f'<div data-panel>{artefact_card(pn, "card")}</div>' for pn in w['panels'])
    plist = ''.join(f'<div><span class="label">0{i+1}</span><span>{e(a)}</span><b class="num" data-move="number-scramble">{e(n)}</b></div>' for i, (a, n, s, cl) in enumerate(p['cells']))
    tiers = ''.join(f'<div class="tier{" fill" if tr["primary"] else ""}"><div><span class="label">{e(tr["name"])}</span><b class="num" data-move="number-scramble">{e(tr["price"])}</b><span class="label">{e(tr["per"])}</span><ul>{"".join("<li>" + e(i) + "</li>" for i in tr["items"])}</ul></div><a class="btn{"" if tr["primary"] else " primary"} arrow" href="#">{e(tr["cta"])}</a></div>' for tr in pl['tiers'])
    life = f'<div class="tier inkc"><div><span class="label" style="color:rgba(255,255,255,.6)">{e(pl["lifetime"]["label"])}</span><p class="h3" style="margin-top:14px;text-transform:uppercase;font-family:var(--font-display)">{e(pl["lifetime"]["h3"])}</p>' + ''.join(f'<b class="num" style="font-size:44px;display:block;margin-top:22px" data-move="number-scramble">{e(n)}</b><span class="label" style="color:rgba(255,255,255,.6)">{e(d)}</span>' for n, d in pl['lifetime']['items']) + '</div></div>'
    trows = ''.join(f'<div class="trow"><span class="label">{e(k)}</span><span class="h3">{e(ti)}</span><p>{e(d)}</p></div>' for k, ti, d in t['rows'])
    fcols = ''.join(f'<div><h5>{e(ti)}</h5><ul>{"".join("<li>" + e(i) + "</li>" for i in items)}</ul></div>' for ti, items in en['cols'])
    return f"""
<nav class="g navg nb" data-agent="Navigation">{wordmark(c)}<span class="time">Belgrade <span class="clock-inline" data-clock>--:--</span> · Madrid · New York</span><div class="links">{links}</div><a class="cta" href="#">{e(c['nav']['cta'])} →</a></nav>

<section class="sec" data-agent="Hero · grid" style="padding-top:28px">
  <div class="wrap">
    <div class="g herog">
      <div class="big"><span class="label"><span class="sq"></span>{e(h['label'])}</span><h1 class="display h1" data-move="masked-line-reveal" style="margin-top:28px">{e(h['h1'][0])}<span class="accent">{e(h['h1'][1])}</span>{e(h['h1'][2])}</h1></div>
      <div class="art"><span class="tag">{e(h['artefact']['tl'])}</span>{artefact_card(h['artefact'], 'card')}</div>
      <div class="lede-cell lede" style="grid-column:1/3"><p class="lede">{e(h['lede'])}</p><div class="ctas" style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn primary arrow" href="#">{e(h['cta'])}</a><a class="btn arrow" href="#record">{e(h['cta2'])}</a></div></div>
      <div class="n fill"><span class="label">{e(h['counter']['t'])}</span><b class="num" data-move="number-scramble">{e(h['counter']['n'])}</b><span class="tag">live</span></div>
    </div>
  </div>
</section>

<div class="marquee" data-move="marquee" data-duration="55" data-agent="Coverage" style="border-top:1px solid var(--line);border-bottom:1px solid var(--line)"><div class="leagues">{''.join('<span>' + e(x) + '</span><span>■</span>' for x in c['marquee'])}</div></div>

<section class="sec" id="record" data-agent="Public record">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(r['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(r['h2'])}</h2></div><p class="lede muted">{e(r['lede'])}</p></div>
    <div class="g statg nb" style="--cols:3">{cells}<div class="inkc"><span class="label" style="color:rgba(255,255,255,.6)">{e(r['ink']['label'])}</span><span class="h3" style="display:block;margin-top:14px">{e(r['ink']['h3'])}</span><a class="link arrow" href="#" style="color:inherit">{e(r['ink']['link'])}</a></div></div>
    <p class="label" style="margin-top:14px">{e(r['foot'])}</p>
  </div>
</section>

<section class="band" id="ways" data-agent="Three ways in">
  <div class="wrap">
    <span class="label"><span class="sq"></span>{e(w['label'])}</span>
    <div class="pinned" data-move="pinned-steps" style="margin-top:28px">
      <div class="steps"><div class="g svc nb" style="grid-template-columns:1fr;border-color:rgba(255,255,255,.25)"><div class="nlist" style="border-right:0">{''.join(f'<div data-step><i>0{i+1}</i>{e(s)}</div>' for i, s in enumerate(w['steps']))}</div></div><p style="margin-top:20px;max-width:44ch;opacity:.7">{e(w['note'])}</p></div>
      <div class="panels">{panels}</div>
    </div>
  </div>
</section>

<section class="sec" id="price" data-agent="Same bet, better price">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(p['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(p['h2'])}</h2></div><p class="big-body" data-move="text-scrub">{e(p['body'])}</p></div>
    <div class="g listg nb" style="grid-template-columns:1fr">{plist}</div>
  </div>
</section>

<section class="sec tight" data-agent="Trust">
  <div class="wrap"><span class="label"><span class="sq"></span>{e(t['label'])}</span>
    <p class="giantq" data-move="word-blur-in">Every pick, every loss, the closing line — on the record.</p>
    {trows}
  </div>
</section>

<section class="sec" id="plans" data-agent="Plans">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(pl['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(pl['h2'])}</h2></div><p class="lede muted">{e(pl['lede'])}</p></div>
    <div class="g plang nb" style="--cols:3">{tiers}{life}</div>
    <p class="label" style="margin-top:14px">{e(pl['foot'])}</p>
    <p class="note-conflict">{e(pl['conflict'])}</p>
  </div>
</section>

<section class="sec tight" data-agent="Questions"><div class="wrap"><span class="label"><span class="sq"></span>{e(f['label'])}</span><div class="faq" style="margin-top:20px">{faq(c)}</div></div></section>

<footer class="ending" data-agent="Ending">
  <div class="wrap">
    <div class="g footg nb" style="--cols:4">
      <div>{wordmark(c)}<p class="muted" style="margin-top:14px;max-width:32ch">{e(en['tag'])}</p><a class="btn primary arrow" href="#" style="margin-top:18px">{e(en['cta'])}</a></div>
      {fcols}
      <div><h5>Belgrade</h5><div class="clock" data-clock>--:--</div></div><div><h5>Madrid</h5><div class="clock" data-clock="Europe/Madrid">--:--</div></div><div><h5>New York</h5><div class="clock" data-clock="America/New_York">--:--</div></div>
      <div class="fill"><h5 style="color:inherit">Next</h5><p style="font-family:var(--font-display);font-weight:700;font-size:22px;text-transform:uppercase;line-height:1">{e(en['next'])}</p></div>
    </div>
    <div class="giant" aria-hidden="true" style="margin-top:40px">{e(b['name'])}<span class="dim" style="left:0;top:-28px;width:38%">w 1,124.00</span></div>
    <div class="legal"><span>{e(en['legal'])}</span><span>{e(en['responsible'])} · Concept C2 · Swiss grid</span></div>
  </div>
</footer>
<script>(function(){{function tick(){{document.querySelectorAll('[data-clock]').forEach(function(el){{var tz=el.getAttribute('data-clock')||'Europe/Belgrade';try{{el.textContent=new Date().toLocaleTimeString('en-GB',{{timeZone:tz,hour:'2-digit',minute:'2-digit'}})}}catch(e){{}}}})}}tick();setInterval(tick,30000)}})();</script>
""", C2_CSS, 'tx-guides'

# ───────────────────────────── C3 · Flat colour worlds ─────────────────────────────
C3_CSS = """
body{background:var(--paper);color:var(--ink)}
.c3nav{position:sticky;top:16px;z-index:50;display:flex;justify-content:center;padding:0 16px}
.c3nav .bar{background:#fff;border-radius:999px;padding:8px 10px 8px 18px;display:flex;align-items:center;gap:26px;box-shadow:0 1px 0 rgba(0,0,0,.06)}
.c3nav .links{display:flex;gap:22px;font-weight:600;font-size:14px}.c3nav .links a{color:var(--ink);text-decoration:none}
.c3nav .cta{background:var(--ink);color:#fff;border-radius:999px;padding:10px 18px;font-weight:700;font-size:14px;text-decoration:none}
.c3nav .wordmark{font-family:var(--font-display);font-weight:800}
.hero3{padding:clamp(40px,6vw,80px) var(--gutter) 0}
.hero3 .cardbig{background:var(--accent);color:var(--accent-contrast);border-radius:var(--radius);padding:clamp(32px,5vw,72px);display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:end;max-width:var(--max);margin:0 auto;position:relative;overflow:hidden}
.hero3 .h1{font-size:clamp(56px,9vw,128px);line-height:.82;margin:20px 0 0;letter-spacing:-.02em}
.hero3 .h1 .accent{color:inherit;text-decoration:underline;text-decoration-thickness:.08em;text-underline-offset:.08em}
.hero3 .lede{max-width:44ch;margin-top:26px;font-size:18px;font-weight:500}
.hero3 .pills{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
.pillb{border-radius:999px;padding:16px 26px;font-weight:700;font-size:15px;text-decoration:none;display:inline-block}
.pillb.ink{background:var(--ink);color:#fff}.pillb.white{background:#fff;color:var(--ink)}
.hero3 .card{background:#fff;color:var(--ink);border:0;border-radius:20px;font-size:13px;padding:22px}
.hero3 .shape{position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;background:rgba(255,255,255,.18)}
.hero3 .counter{position:absolute;left:clamp(32px,5vw,72px);top:clamp(28px,4vw,52px);display:flex;gap:8px;align-items:baseline;font-weight:700}
.hero3 .counter .num{font-size:28px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.tile{border-radius:var(--radius);padding:28px;min-height:200px;display:flex;flex-direction:column;justify-content:space-between}
.tile .num{font-size:clamp(48px,5vw,76px);line-height:1;display:block}
.tile.c1{background:#FDCB40;color:#1A1A1A}.tile.c2{background:#1D5CFF;color:#fff}.tile.c3{background:#10B14B;color:#fff}.tile.c4{background:#FD4401;color:#fff}.tile.white{background:#fff}.tile.inkt{background:var(--ink);color:#fff}
.tile .label{color:inherit;opacity:.75}
.deck{position:relative;min-height:720px}.deck .dcard{background:#fff;border-radius:var(--radius);padding:28px;box-shadow:0 1px 0 rgba(0,0,0,.05)}
.deck .dcard .step{font-family:var(--font-display);font-weight:800;font-size:clamp(28px,4vw,56px);line-height:.9;text-transform:uppercase;margin-bottom:18px}
.deck .dcard .card{background:var(--panel);border:0;border-radius:18px;font-size:13px}
.deck .dcard:nth-child(2) .card{background:#FFF2B7}.deck .dcard:nth-child(3) .card{background:#E8F0FF}
.st2{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
.st2 .big{font-family:var(--font-display);font-weight:800;font-size:clamp(40px,6vw,90px);line-height:.85;text-transform:uppercase;letter-spacing:-.02em}
.rot{display:inline-block}
.angled{height:80px;background:var(--ink);clip-path:polygon(0 60%,100% 0,100% 100%,0 100%)}
.trust3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.trust3 .tile{background:#fff}
.trust3 .h3{font-family:var(--font-display);font-weight:800;text-transform:uppercase;font-size:26px;line-height:.95;margin:40px 0 12px}
.plans3{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.plans3 .tile{min-height:440px}.plans3 .tile .num{font-size:clamp(56px,6vw,96px)}
.plans3 ul{list-style:none;margin:18px 0 26px}.plans3 li{padding:8px 0;font-size:15px;font-weight:500;border-top:1px solid rgba(0,0,0,.12)}
.plans3 .tile.c2 li{border-color:rgba(255,255,255,.25)}
.life3{margin-top:16px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.faq3 .faq details{background:#fff;border:0;border-radius:18px;padding:8px 22px;margin-bottom:10px}
.faq3 .faq summary{font-weight:700}
.end3{background:var(--accent);padding:clamp(40px,6vw,80px) var(--gutter) 24px;margin-top:clamp(40px,6vw,80px)}
.end3 .inner{background:#fff;border-radius:var(--radius);max-width:var(--max);margin:0 auto;padding:clamp(28px,5vw,64px);color:var(--ink)}
.end3 .cols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px}
.end3 h5{font-size:12px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px;opacity:.6}.end3 ul{list-style:none;line-height:1.9;font-size:15px;font-weight:500}
.end3 .giant{font-family:var(--font-display);font-weight:800;font-size:clamp(80px,17vw,260px);line-height:.8;text-transform:uppercase;letter-spacing:-.03em;margin-top:40px;position:relative;color:var(--ink)}
.end3 .giant .dot{position:absolute;width:.22em;height:.22em;border-radius:50%;background:var(--accent);top:-.1em;left:1.9em}
.end3 .next{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:28px;font-weight:700}
.end3 .legal{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:12px;opacity:.6;margin-top:18px}
@media(max-width:900px){.c3nav .links{display:none}.hero3 .cardbig{grid-template-columns:1fr}.tiles,.trust3,.plans3,.life3,.st2{grid-template-columns:1fr}.end3 .cols{grid-template-columns:1fr 1fr}.plans3 .tile{min-height:0}.hero3 .counter{position:static;margin-bottom:12px}}
"""

def render_C3(c):
    b, h, r, w, p, t, pl, f, en = c['brand'], c['hero'], c['record'], c['ways'], c['price'], c['trust'], c['plans'], c['faq'], c['ending']
    links = ''.join(f'<a href="{e(u)}">{e(l)}</a>' for u, l in c['nav']['links'])
    cols = ['c1', 'white', 'c2', 'c4', 'white']
    cells = ''.join(f'<div class="tile {cols[i % 5]}"><span class="label">{e(a)}</span><b class="num" data-move="number-scramble">{e(n)}</b><span class="label">{e(s)}</span></div>' for i, (a, n, s, cl) in enumerate(r['cells']))
    deck = ''.join(f'<div class="dcard"><div class="step">0{i+1} — {e(w["steps"][i])}</div>{artefact_card(pn, "card")}</div>' for i, pn in enumerate(w['panels']))
    pcells = ''.join(f'<div class="tile {["white", "c3", "c4"][i]}"><span class="label">{e(a)}</span><b class="num" data-move="number-scramble">{e(n)}</b><span class="label">{e(s)}</span></div>' for i, (a, n, s, cl) in enumerate(p['cells']))
    trows = ''.join(f'<div class="tile"><span class="label">{e(k)}</span><div><div class="h3">{e(ti)}</div><p>{e(d)}</p></div></div>' for k, ti, d in t['rows'])
    tiers = ''.join(f'<div class="tile {"c2" if tr["primary"] else "white"}"><div><span class="label">{e(tr["name"])}</span><b class="num" data-move="number-scramble">{e(tr["price"])}</b><span class="label">{e(tr["per"])}</span><ul>{"".join("<li>" + e(i) + "</li>" for i in tr["items"])}</ul></div><a class="pillb {"white" if tr["primary"] else "ink"}" href="#">{e(tr["cta"])}</a></div>' for tr in pl['tiers'])
    life = f'<div class="tile inkt"><span class="label">{e(pl["lifetime"]["label"])}</span><div class="h3" style="font-family:var(--font-display);font-weight:800;text-transform:uppercase;font-size:26px;line-height:.95">{e(pl["lifetime"]["h3"])}</div></div>' + ''.join(f'<div class="tile c1"><b class="num" style="font-size:52px" data-move="number-scramble">{e(n)}</b><span class="label">{e(d)}</span></div>' for n, d in pl['lifetime']['items'])
    fcols = ''.join(f'<div><h5>{e(ti)}</h5><ul>{"".join("<li>" + e(i) + "</li>" for i in items)}</ul></div>' for ti, items in en['cols'])
    return f"""
<nav class="c3nav" data-agent="Navigation"><div class="bar">{wordmark(c)}<div class="links">{links}</div><a class="cta" href="#">{e(c['nav']['cta'])}</a></div></nav>

<section class="hero3" data-agent="Hero · colour card">
  <div class="cardbig"><div class="shape"></div>
    <div class="counter"><b class="num" data-move="number-scramble">{e(h['counter']['n'])}</b><span>{e(h['counter']['t'])}</span></div>
    <div style="padding-top:48px"><h1 class="display h1" data-move="masked-line-reveal">{e(h['h1'][0])}<span class="accent">{e(h['h1'][1])}</span>{e(h['h1'][2])}</h1><p class="lede">{e(h['lede'])}</p><div class="pills"><a class="pillb ink" href="#">{e(h['cta'])}</a><a class="pillb white" href="#record">{e(h['cta2'])}</a></div></div>
    <div>{artefact_card(h['artefact'], 'card')}</div>
  </div>
</section>

<div class="marquee" data-move="marquee" data-duration="55" data-agent="Coverage" style="margin-top:24px;border:0"><div class="leagues">{''.join('<span>' + e(x) + '</span><span>●</span>' for x in c['marquee'])}</div></div>

<section class="sec" id="record" data-agent="Public record">
  <div class="wrap">
    <div class="sec-head"><div><span class="label">{e(r['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(r['h2'])}</h2></div><p class="lede muted">{e(r['lede'])}</p></div>
    <div class="tiles">{cells}<div class="tile inkt"><span class="label">{e(r['ink']['label'])}</span><div><div class="h3" style="font-family:var(--font-display);font-weight:800;text-transform:uppercase;font-size:26px;line-height:.95">{e(r['ink']['h3'])}</div><a class="pillb white" href="#" style="margin-top:16px;padding:10px 18px;font-size:13px">{e(r['ink']['link'])}</a></div></div></div>
    <p class="label" style="margin-top:14px">{e(r['foot'])}</p>
  </div>
</section>

<section class="sec" id="ways" data-agent="Three ways in">
  <div class="wrap"><span class="label">{e(w['label'])}</span><h2 class="display h2" data-move="masked-line-reveal" style="margin:16px 0 36px;max-width:16ch">However you play.</h2>
    <div class="deck" data-move="card-deck-peel">{deck}</div>
    <p class="muted" style="margin-top:20px;max-width:44ch">{e(w['note'])}</p>
  </div>
</section>

<div class="angled" data-agent="Divider"></div>
<section class="sec" id="price" data-agent="Same bet, better price" style="background:var(--ink);color:#fff;margin-top:-1px">
  <div class="wrap">
    <div class="st2"><div><span class="label" style="color:rgba(255,255,255,.6)">{e(p['label'])}</span><h2 class="big" style="margin-top:16px">Same bet.<br><span class="rot" data-move="rotating-headline" data-phrases='["Better price.","Better book.","Better number."]'>Better price.</span></h2></div><p class="big-body" data-move="text-scrub" style="color:rgba(255,255,255,.8)">{e(p['body'])}</p></div>
    <div class="tiles" style="margin-top:48px">{pcells}</div>
  </div>
</section>

<section class="sec tight" data-agent="Trust"><div class="wrap"><span class="label">{e(t['label'])}</span><div class="trust3" style="margin-top:20px">{trows}</div></div></section>

<section class="sec" id="plans" data-agent="Plans">
  <div class="wrap">
    <div class="sec-head"><div><span class="label">{e(pl['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(pl['h2'])}</h2></div><p class="lede muted">{e(pl['lede'])}</p></div>
    <div class="plans3">{tiers}</div>
    <div class="life3">{life}</div>
    <p class="label" style="margin-top:14px">{e(pl['foot'])}</p>
    <p class="note-conflict">{e(pl['conflict'])}</p>
  </div>
</section>

<section class="sec tight faq3" data-agent="Questions"><div class="wrap"><span class="label">{e(f['label'])}</span><div class="faq" style="margin-top:20px">{faq(c)}</div></div></section>

<footer class="end3" data-agent="Ending">
  <div class="inner">
    <div class="cols"><div>{wordmark(c)}<p class="muted" style="margin-top:14px;max-width:32ch">{e(en['tag'])}</p><a class="pillb ink" href="#" style="margin-top:18px">{e(en['cta'])}</a></div>{fcols}</div>
    <div class="giant" aria-hidden="true">{e(b['name'])}<span class="dot"></span></div>
    <div class="next"><span>Next stop → {e(en['next'])}</span><span>{e(en['responsible'])}</span></div>
    <div class="legal"><span>{e(en['legal'])}</span><span>Concept C3 · Flat colour</span></div>
  </div>
</footer>
""", C3_CSS, ''


# ───────────────────────────── C1 · Blueprint (section-by-section pass) ─────────────────────────────
C1_CSS = """
body{background:var(--paper);color:var(--ink)}
.guides{position:absolute;inset:0;pointer-events:none}.guides i{position:absolute;top:0;bottom:0;border-left:1px dashed var(--line);opacity:.5}
.hero{min-height:100svh;display:grid;align-content:space-between;padding:calc(72px + 24px) 0 0}
.hero .wrap{align-items:center}
.hero .cat{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:22px}
.hero .h1{font-size:clamp(52px,7.2vw,112px)}
.hero .lede{margin-top:24px;max-width:46ch}
.hero .ctas{margin-top:28px;display:flex;gap:12px;flex-wrap:wrap}
.hero-art{position:relative;padding:28px}.hero-art .card{font-size:14px}
.hero .marquee{margin-top:40px;border-top:1px solid var(--line);border-bottom:0}
.record .cells>div{min-height:170px}.record .cells .num.pos{color:var(--pos,var(--accent))}.record .cells .num.neg{color:var(--neg,#E06A4A)}
.pricegrid{display:grid;grid-template-columns:7fr 5fr;gap:24px;align-items:stretch}.pricegrid .cells>div{min-height:120px;justify-content:center}.pricegrid .af-ladder{gap:14px}.pricegrid .af-ladder .bar{height:18px}.pricegrid .af-ladder .v{font-size:26px}
.audit2 .rows li{display:block}.audit2 .rows li .h3{display:block;margin:8px 0 6px}
.hero .wrap{position:relative;z-index:1}
.ways .panel-card{max-width:560px}.ways{align-content:start}.ways .pinned{min-height:60vh}
.audit2{display:grid;grid-template-columns:5fr 7fr;gap:clamp(32px,5vw,80px);align-items:start}
.audit2 .rows{margin-top:0}.audit2 .rows li{padding:18px 0}
.price .cells>div{min-height:380px}.price .cells .num{font-size:clamp(56px,6vw,88px)}
.price .cells .num small{font-family:var(--font-mono);font-size:12px;letter-spacing:.1em;margin-left:8px;color:var(--muted)}
.price ul{list-style:none;margin:16px 0 24px}.price li{padding:9px 0;border-top:1px solid var(--line);font-size:15px}.price li::before{content:"—";color:var(--accent);margin-right:10px}
.lifetime{margin-top:16px;display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid var(--line)}
.lifetime>div{padding:24px;border-right:1px solid var(--line)}.lifetime>div:last-child{border-right:0}
.ending{min-height:100svh;display:grid;align-content:end}
@media(max-width:900px){.hero{padding-top:88px}.audit2,.lifetime,.pricegrid{grid-template-columns:1fr}.lifetime>div{border-right:0;border-bottom:1px solid var(--line)}.price .cells{grid-template-columns:1fr}.price .cells>div{min-height:0}.hero .marquee{margin-top:28px}}
"""

def render_C1(c):
    b, h, r, w, p, t, pl, f, en = c['brand'], c['hero'], c['record'], c['ways'], c['price'], c['trust'], c['plans'], c['faq'], c['ending']
    links = ''.join(f'<a href="{e(u)}">{e(l)}</a>' for u, l in c['nav']['links'])
    cells = ''.join(f'<div><span class="label">{e(a)}</span><b class="num{" " + cl if cl else ""}" data-move="number-scramble">{e(n)}</b><span class="label">{e(s)}</span></div>' for a, n, s, cl in r['cells'])
    panels = ''.join(f'<div data-panel class="panel-card frame marks" style="padding:20px"><i class="m"></i>{artefact_card(pn)}</div>' for pn in w['panels'])
    pcells = ''.join(f'<div><span class="label">{e(a)}</span><b class="num{" pos accent" if cl == "pos" else ""}"{" style=\"color:var(--neg,#E06A4A)\"" if cl == "neg" else ""} data-move="number-scramble">{e(n)}</b><span class="label">{e(s)}</span></div>' for a, n, s, cl in p['cells'][1:])
    trows = ''.join(f'<li><span class="label">{e(k)}</span><span class="h3">{e(ti)}</span><p>{e(d)}</p></li>' for k, ti, d in t['rows'])
    tiers = ''.join(f'<div><div><span class="label">{e(tr["name"])}</span><b class="num" style="display:block;margin-top:14px" data-move="number-scramble">{e(tr["price"])}<small>{e(tr["per"])}</small></b><ul>{"".join("<li>" + e(i) + "</li>" for i in tr["items"])}</ul></div><a class="btn{" primary" if tr["primary"] else ""} arrow" href="#">{e(tr["cta"])}</a></div>' for tr in pl['tiers'])
    life = f'<div class="lifetime"><div><span class="label">{e(pl["lifetime"]["label"])}</span><p class="h3" style="margin-top:10px">{e(pl["lifetime"]["h3"])}</p></div>' + ''.join(f'<div><b class="num" style="font-size:44px" data-move="number-scramble">{e(n)}</b><p class="muted" style="margin-top:8px;font-size:14px">{e(d)}</p></div>' for n, d in pl['lifetime']['items']) + '</div>'
    fcols = ''.join(f'<div><h5>{e(ti)}</h5><ul>{"".join("<li>" + e(i) + "</li>" for i in items)}</ul></div>' for ti, items in en['cols'])
    a = h['artefact']
    return f"""
<div class="guides" aria-hidden="true"><i style="left:25%"></i><i style="left:50%"></i><i style="left:75%"></i></div>
<nav class="nav" data-agent="Navigation"><div class="wrap">{wordmark(c)}<div class="links">{links}</div><a class="btn primary arrow" href="#">{e(c['nav']['cta'])}</a></div></nav>

<section class="hero" data-agent="Hero · claim + fact + artefact" style="position:relative">
  {("<div class=\"hero-photo\"><img src=\"{{IMG:" + h["img"] + "}}\" alt=\"\"></div>") if h.get("img") and c.get("_images", {}).get(h["img"]) else ""}
  <div class="wrap">
    <div>
      <div class="cat"><span class="label"><span class="sq"></span>{e(h['category'])}</span><span class="label ink"><b class="num" style="font-size:14px" data-move="number-scramble">{e(h['counter']['n'])}</b> {e(h['counter']['t'])}</span></div>
      <h1 class="display h1" data-move="masked-line-reveal">{e(h['h1'][0])}<span class="accent">{e(h['h1'][1])}</span>{e(h['h1'][2])}</h1>
      <p class="lede">{e(h['lede'])}</p>
      <div class="ctas"><a class="btn primary arrow" href="#">{e(h['cta'])}</a><a class="btn arrow" href="#record">{e(h['cta2'])}</a></div>
    </div>
    <div class="artefact frame marks hero-art"><i class="m"></i>
      <span class="corner-meta tl">{e(a['tl'])}</span><span class="corner-meta tr">{e(a['tr'])}</span>
      {artefact_card(a)}
      <span class="corner-meta bl">{e(a['bl'])}</span><span class="corner-meta br">{e(a['br'])}</span>
    </div>
  </div>
  <div class="marquee" data-move="marquee" data-duration="55"><div class="leagues">{''.join('<span>' + e(x) + '</span><span>·</span>' for x in c['marquee'])}</div></div>
</section>

<section class="sec record" id="record" data-agent="The public record" style="--h:1">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(r['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(r['h2'])}</h2></div><p class="lede muted">{e(r['lede'])}</p></div>
    <div class="cells" style="--cols:3">{cells}<div style="padding:18px 20px 14px"><span class="label">{e(r['ink']['label'])} · 664 settled</span><div class="af" data-artefact="ledger-curve" data-curve='{json.dumps(r.get("curve", []))}' data-label="{e(r.get("curve_label", ""))}" style="flex:1;margin:10px 0 6px"></div><a class="link arrow" href="#">{e(r['ink']['link'])}</a></div></div>
    <p class="label" style="margin-top:14px">{e(r['foot'])}</p>
  </div>
</section>

<section class="sec ways" id="ways" data-agent="Three ways in · moment" style="--h:1">
  <div class="wrap">
    <span class="label"><span class="sq"></span>{e(w['label'])}</span><h2 class="display h2" style="margin-top:14px">{e(w['h2'])}</h2>
    <div class="pinned" data-move="pinned-steps" style="margin-top:32px">
      <div class="steps">{''.join(f'<div data-step>{e(s)}</div>' for s in w['steps'])}<p class="muted" style="margin-top:20px;max-width:40ch">{e(w['note'])}</p></div>
      <div class="panels">{panels}</div>
    </div>
  </div>
</section>

<section class="sec" id="price" data-agent="Price check" style="--h:1">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(p['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(p['h2'])}</h2></div><p class="big-body" data-move="text-scrub">{e(p['body'])}</p></div>
    <div class="pricegrid"><div class="frame marks" style="padding:24px"><i class="m"></i><span class="label"><span class="sq"></span>Books that quoted this selection · Brighton · match result</span><div data-artefact="price-ladder" data-ladder='{json.dumps(p["ladder"])}' style="margin-top:18px"></div><p class="label" style="margin-top:12px">{e(p.get("ladder_note", ""))}</p></div><div class="cells" style="--cols:1">{pcells}</div></div>
  </div>
</section>

<div class="band dark" data-agent="Photo band · fact">{("<img src=\"{{IMG:" + c["band"]["img"] + "}}\" alt=\"\">") if c.get("band") and c.get("_images", {}).get(c["band"]["img"]) else ""}<div class="wrap"><div><span class="label">{e(c["band"]["sub"]) if c.get("band") else ""}</span><div class="giant-n" data-move="number-scramble">{e(c["band"]["n"]) if c.get("band") else ""}</div></div><span class="label" style="max-width:22ch;text-align:right">{e(c["band"]["label"]) if c.get("band") else ""}</span></div></div>

<section class="sec" id="audit" data-agent="Method, record, rules + questions" style="--h:1">
  <div class="wrap">
    <span class="label"><span class="sq"></span>{e(t['label'])}</span><h2 class="display h2" style="margin:14px 0 36px">{e(t['h2'])}</h2>
    <div class="audit2"><ul class="rows">{trows}</ul><div class="faq">{faq(c)}</div></div>
  </div>
</section>

<section class="sec price" id="plans" data-agent="Plans" style="--h:1">
  <div class="wrap">
    <div class="sec-head"><div><span class="label"><span class="sq"></span>{e(pl['label'])}</span><h2 class="display h2" data-move="masked-line-reveal">{e(pl['h2'])}</h2></div><p class="lede muted">{e(pl['lede'])}</p></div>
    <div class="cells" style="--cols:2">{tiers}</div>
    {life}
    <p class="label" style="margin-top:14px">{e(pl['foot'])}</p>
  </div>
</section>

<footer class="ending" data-agent="Ending">
  <div class="wrap">
    <div class="cols"><div>{wordmark(c)}<p class="muted" style="margin-top:14px;max-width:32ch">{e(en['tag'])}</p><div class="ctas" style="margin-top:20px"><a class="btn primary arrow" href="#">{e(en['cta'])}</a></div></div>{fcols}</div>
    <div class="giant outline" aria-hidden="true">{e(b['name'])}<span class="dim" style="left:0;top:-28px;width:38%">w 1,124.00</span><span class="dim" style="right:0;top:-28px;width:22%">x 0.78 lh</span></div>
    <div class="next"><span>{e(en['next'])}</span><span>{e(en['responsible'])}</span></div>
    <div class="legal"><span>{e(en['legal'])}</span><span>Concept C1 · Blueprint</span></div>
  </div>
</footer>
""", C1_CSS, 'tx-grid tx-grain'

RENDERERS = {'C1': render_C1, 'C2': render_C2, 'C3': render_C3}

def render(content, concept):
    return RENDERERS[concept](content)
