"""Franš — master piece build. Hand art-directed; every decision noted inline as a rule candidate for the system."""
import base64, os, json
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
b64 = lambda p, m: f'data:{m};base64,' + base64.b64encode(open(os.path.join(D, p), 'rb').read()).decode()
IMG = {n: b64(f'img-{n}.jpg', 'image/jpeg') for n in ['waiter', 'long-table', 'basta-table', 'octopus', 'reservation-book']}
LOGO = b64('logo-white.png', 'image/png')
VIDEO = b64('hero.mp4', 'video/mp4') if os.path.exists(os.path.join(D, 'hero.mp4')) else ''
moves = open(os.path.join(ROOT, 'lib/motion/moves.js')).read()

# ---- content (all from the site; nothing invented) ----
dishes = [
    ('Biftek u sosu od belih tartufa', '7 400'), ('Guščija džigerica, sos od šljiva i krušaka', '6 800'), ('Čudesni tanjir za dve osobe', '6 000'),
    ('Rižoto sa crnim tartufima', '2 400'), ('Karađorđeva šnicla, teleća', '3 600'), ('Jagnjeći kotleti, grilovani', '4 400'),
    ('Brancin svež, fileti', '3 500'), ('Karpaćo od bifteka, rukola, pinjoli', '3 200'), ('Tatarski biftek, tost, puter', '4 200'), ('Pasta Franš', '2 000'),
]
ledger = ''.join(f'<li><span class="d">{n}</span><span class="dots"></span><span class="p">{p}</span></li>' for n, p in dishes)

html = f'''<!DOCTYPE html>
<html lang="sr" data-nav-light>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Restoran Franš — Bašta u kojoj Beograd slavi od 1982.</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Instrument+Sans:wght@400;500;600&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..600,0..100,0..1;1,9..144,300..600,0..100,0..1&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
/* RULE: colour as a world — cream paper + deep garden green, both from the client's own palette; no third colour. */
:root{{--paper:#F4EFE3;--paper-2:#EAE3D2;--ink:#0F2A14;--ink-2:#1E3F25;--muted:#6E7A62;--line:rgba(15,42,20,.18);--gold:#B89B62;
--on-photo:#F4EFE3;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Instrument Sans',system-ui,sans-serif;--gutter:clamp(20px,4.5vw,72px);--max:1440px}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:auto}}
html,body{{overflow-x:hidden}}
body{{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased}}
img,video{{display:block;max-width:100%}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:var(--max);margin:0 auto;padding:0 var(--gutter);width:100%}}
/* RULE: labels are small caps serif with wide tracking, never mono — the register of a place, not a product. */
.lab{{font-family:var(--serif);font-weight:500;font-size:13px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted)}}
.lab.light{{color:rgba(244,239,227,.7)}}
.ser{{font-family:var(--serif);font-weight:400;letter-spacing:-.01em}}
.it{{font-style:italic}}
h1,h2,h3{{font-family:var(--serif);font-weight:400;line-height:1.02;letter-spacing:-.015em}}
.h1{{font-size:clamp(52px,7.4vw,124px)}}
.h2{{font-size:clamp(40px,5.2vw,84px)}}
.lede{{font-family:var(--serif);font-size:clamp(20px,1.6vw,26px);line-height:1.35;max-width:38ch}}
.btn{{display:inline-flex;align-items:center;gap:14px;font-family:var(--serif);font-size:18px;letter-spacing:.04em;padding:16px 26px;border:1px solid currentColor;border-radius:999px;transition:background .3s,color .3s,transform .35s cubic-bezier(.2,.8,.2,1)}}
.btn.solid{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}
.btn.light{{color:var(--on-photo)}}.btn.light.solid{{background:var(--on-photo);color:#0F2A14;border-color:var(--on-photo)}}
.btn:hover{{transform:translateY(-2px)}}.btn .ar{{transition:transform .35s}}.btn:hover .ar{{transform:translateX(4px)}}
/* nav */
.nav{{position:fixed;inset:0 0 auto 0;z-index:50;padding:22px 0;color:var(--on-photo);transition:background .4s,color .4s,padding .4s}}
.nav .wrap{{display:flex;align-items:center;justify-content:space-between;gap:24px}}
.nav .mark{{display:block;width:44px;height:62px;background:currentColor;-webkit-mask:url("{LOGO}") center/contain no-repeat;mask:url("{LOGO}") center/contain no-repeat}}
.nav .links{{display:flex;gap:34px;font-family:var(--serif);font-size:17px;letter-spacing:.06em}}
.nav .links a{{position:relative}}.nav .links a::after{{content:"";position:absolute;left:0;right:100%;bottom:-4px;border-bottom:1px solid currentColor;transition:right .4s cubic-bezier(.2,.8,.2,1)}}.nav .links a:hover::after{{right:0}}
.nav.solid{{background:var(--paper);color:var(--ink);padding:14px 0;box-shadow:0 1px 0 var(--line)}}
.nav.solid .mark{{width:34px;height:48px}}.nav.solid .btn{{color:var(--ink);border-color:var(--ink)}}
/* hero */
.hero{{position:relative;min-height:100svh;display:grid;align-content:end;color:var(--on-photo);overflow:hidden}}
.hero .media{{position:absolute;inset:0;z-index:0;background:#0F2A14}}
.hero .media video,.hero .media img{{width:100%;height:100%;object-fit:cover;object-position:center 30%;transform:scale(1.04)}}
.hero .media::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--ink) 55%,transparent) 0%,color-mix(in srgb,var(--ink) 15%,transparent) 35%,color-mix(in srgb,var(--ink) 35%,transparent) 65%,color-mix(in srgb,var(--ink) 92%,transparent) 100%)}}
.hero .wrap{{position:relative;z-index:1;padding-top:140px;padding-bottom:clamp(40px,6vw,72px);display:grid;grid-template-columns:1fr auto;gap:40px;align-items:end}}
.hero .cat{{display:flex;gap:28px;flex-wrap:wrap;margin-bottom:26px}}
.hero .h1{{max-width:11ch}}
.hero .lede{{margin-top:26px;color:var(--on-photo);opacity:.85}}
.hero .ctas{{display:flex;gap:14px;margin-top:34px;flex-wrap:wrap}}
.hero .side{{display:grid;gap:10px;text-align:right}}
.hero .side .big{{font-family:var(--serif);font-size:clamp(48px,6vw,96px);line-height:.9}}
.hero .strip{{position:relative;z-index:1;border-top:1px solid rgba(244,239,227,.25)}}
.hero .strip .wrap{{display:flex;justify-content:space-between;gap:24px;padding:16px var(--gutter);flex-wrap:wrap;align-items:center}}
/* sections */
.sec{{padding:clamp(80px,10vw,150px) 0}}
.sec.tight{{padding:clamp(48px,6vw,88px) 0}}
/* 2 · type moment */
.quote{{text-align:center}}
.quote .big{{font-family:var(--serif);font-style:italic;font-size:clamp(56px,9vw,150px);line-height:.95;letter-spacing:-.02em;max-width:14ch;margin:24px auto 0}}
.quote p.body{{font-family:var(--serif);font-size:clamp(20px,1.7vw,27px);line-height:1.4;max-width:46ch;margin:40px auto 0}}
.quote .who{{margin-top:22px}}
.num44{{font-family:var(--serif);font-size:clamp(120px,22vw,340px);line-height:.8;letter-spacing:-.04em;color:var(--ink)}}
/* 3 · garden editorial */
.garden{{display:grid;grid-template-columns:7fr 5fr;gap:clamp(20px,3vw,48px);align-items:end}}
.garden.one{{grid-template-columns:1fr}}.garden .big{{aspect-ratio:21/10;overflow:hidden}}
.garden .small{{aspect-ratio:4/5;overflow:hidden;margin-bottom:clamp(40px,8vw,120px)}}
.garden img{{width:100%;height:100%;object-fit:cover}}
.garden .cap{{display:flex;justify-content:space-between;gap:16px;margin-top:14px;flex-wrap:wrap}}
.gh{{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:end;margin-bottom:clamp(32px,4vw,64px)}}
/* 4 · ledger */
.menu{{display:grid;grid-template-columns:5fr 7fr;gap:clamp(32px,5vw,96px);align-items:start}}
.ledger{{list-style:none;columns:1}}
.ledger li{{display:flex;align-items:baseline;gap:10px;padding:16px 0;border-bottom:1px solid var(--line);font-family:var(--serif);font-size:clamp(19px,1.5vw,24px)}}
.ledger .dots{{flex:1;border-bottom:1px dotted var(--line);transform:translateY(-6px)}}
.ledger .p{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.menu .photo{{aspect-ratio:1;overflow:hidden;margin-top:12px}}.menu .photo img{{width:100%;height:100%;object-fit:cover}}
/* 5 · band */
.band{{position:relative;min-height:78vh;display:grid;align-items:end;overflow:hidden;color:var(--on-photo)}}
.band img{{position:absolute;inset:0;width:100%;height:112%;object-fit:cover}}
.band::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--ink) 5%,transparent),color-mix(in srgb,var(--ink) 85%,transparent))}}
.band .wrap{{position:relative;z-index:1;padding-bottom:clamp(40px,6vw,72px);display:grid;grid-template-columns:repeat(3,1fr);gap:24px;align-items:end}}
.band .f b{{display:block;font-family:var(--serif);font-size:clamp(48px,6vw,104px);line-height:.9;letter-spacing:-.02em;margin-bottom:10px}}
/* 6 · reservation */
.res{{background:var(--ink);color:var(--paper)}}html[data-world="ink"] .hero .media::after{{background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.15) 35%,rgba(0,0,0,.35) 65%,#0F2A14 100%)}}
.res .grid{{display:grid;grid-template-columns:5fr 7fr;gap:clamp(32px,5vw,96px);align-items:center}}
.res .photo{{aspect-ratio:4/5;overflow:hidden}}.res .photo img{{width:100%;height:100%;object-fit:cover}}
.form{{display:grid;grid-template-columns:1fr 1fr;gap:18px 28px;margin-top:36px}}
.form label{{display:grid;gap:8px}}
.form input,.form select{{background:transparent;border:0;border-bottom:1px solid rgba(244,239,227,.35);color:var(--paper);font-family:var(--serif);font-size:22px;padding:10px 0;outline:0;border-radius:0}}
.form input::placeholder{{color:rgba(244,239,227,.4)}}
.form .full{{grid-column:1/3}}
.res .alt{{margin-top:28px;display:flex;gap:28px;flex-wrap:wrap;color:rgba(244,239,227,.75);font-family:var(--serif);font-size:18px}}
/* 7 · ending */
.end{{padding:clamp(72px,9vw,130px) 0 28px;overflow:hidden}}
.end .cols{{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;padding-bottom:48px;border-bottom:1px solid var(--line)}}
.end h5{{font-family:var(--serif);font-weight:500;font-size:13px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}}
.end ul{{list-style:none;font-family:var(--serif);font-size:19px;line-height:1.7}}
.giant{{font-family:var(--serif);font-style:italic;font-size:clamp(120px,24vw,380px);line-height:.78;letter-spacing:-.03em;margin:40px 0 0;color:var(--ink)}}
.end .legal{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:22px;font-size:12.5px;color:var(--muted)}}

/* ── colour worlds (palette.py, C8 light) — the whole page re-dyes: paper, ink, lines, muted, photo gradients use var(--ink) ── */
html[data-world="terracotta"]{{--paper:#FBEFE9;--paper-2:#F3E2D8;--ink:#2A130D;--ink-2:#4A2A20;--muted:#8A6A5C;--line:rgba(42,19,13,.18)}}
html[data-world="navy"]{{--paper:#EEF2F8;--paper-2:#DFE6F0;--ink:#0E1B2D;--ink-2:#22344E;--muted:#5F6E85;--line:rgba(14,27,45,.18)}}
html[data-world="plum"]{{--paper:#F8EEF1;--paper-2:#EEDCE2;--ink:#29121B;--ink-2:#4A2A36;--muted:#866673;--line:rgba(41,18,27,.18)}}
html[data-world="ink"]{{--paper:#0F2A14;--paper-2:#143319;--ink:#F4EFE3;--ink-2:#E2DBC9;--muted:#9AA88F;--line:rgba(244,239,227,.18)}}
html[data-world="ink"] .res{{background:#F4EFE3;color:#0F2A14}}html[data-world="ink"] .res .lab.light{{color:rgba(15,42,20,.7)}}html[data-world="ink"] .form input{{color:#0F2A14;border-color:rgba(15,42,20,.35)}}html[data-world="ink"] .form input::placeholder{{color:rgba(15,42,20,.4)}}html[data-world="ink"] .res .alt{{color:rgba(15,42,20,.75)}}html[data-world="ink"] .res .btn.light.solid{{background:#0F2A14;color:#F4EFE3;border-color:#0F2A14}}
/* ── font worlds ── */
html[data-font="fraunces"]{{--serif:'Fraunces',Georgia,serif}}html[data-font="fraunces"] .h1,html[data-font="fraunces"] .h2,html[data-font="fraunces"] .quote .big,html[data-font="fraunces"] .giant{{font-variation-settings:"WONK" 1,"SOFT" 40;letter-spacing:-.03em}}
html[data-font="instrument"]{{--serif:'Instrument Serif',Georgia,serif}}html[data-font="instrument"] .lab,html[data-font="instrument"] .end h5{{font-family:var(--sans);font-weight:600;font-size:11px;letter-spacing:.2em}}
/* ── brand panel ── */
.bp{{position:fixed;left:16px;bottom:16px;z-index:60;background:rgba(15,42,20,.92);color:#F4EFE3;backdrop-filter:blur(10px);border-radius:14px;padding:12px 14px;font:500 12px/1.3 var(--sans);display:grid;gap:10px;box-shadow:0 20px 50px rgba(0,0,0,.35);max-width:min(92vw,420px)}}
.bp .row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.bp .t{{opacity:.6;letter-spacing:.14em;text-transform:uppercase;font-size:10px;min-width:52px}}
.bp label{{display:inline-flex;gap:6px;align-items:center;padding:6px 10px;border:1px solid rgba(244,239,227,.25);border-radius:999px;cursor:pointer}}.bp label:has(input:checked){{background:#F4EFE3;color:#0F2A14;border-color:#F4EFE3}}
.bp input{{position:absolute;opacity:0;width:0;height:0}}.bp i{{width:12px;height:12px;border-radius:50%;display:inline-block;outline:2px solid rgba(255,255,255,.35)}}
.bp .x{{position:absolute;right:8px;top:6px;background:none;border:0;color:inherit;opacity:.6;cursor:pointer;font-size:16px}}

/* mobile — RULE: photographs stay full-bleed, type scales to 11vw, everything one column */
@media(max-width:900px){{
.nav .links{{display:none}}.hero .wrap{{grid-template-columns:1fr}}.hero .side{{text-align:left}}.hero .h1{{font-size:clamp(44px,12vw,72px)}}
.garden,.menu,.res .grid,.gh{{grid-template-columns:1fr}}.garden .small{{margin:0;aspect-ratio:4/3}}.band .wrap{{grid-template-columns:1fr;gap:18px}}
.form{{grid-template-columns:1fr}}.form .full{{grid-column:auto}}.end .cols{{grid-template-columns:1fr 1fr}}.quote .big{{font-size:13vw}}.num44{{font-size:34vw}}
}}
</style>
</head>
<body>
<nav class="nav" id="nav"><div class="wrap"><a href="#" aria-label="Restoran Franš"><span class="mark"></span></a><div class="links"><a href="#basta">Bašta</a><a href="#jelovnik">Jelovnik</a><a href="#proslave">Proslave</a><a href="#kontakt">Kontakt</a></div><a class="btn light" href="#rezervacija">Rezervišite sto <span class="ar">→</span></a></div></nav>

<section class="hero" data-move="hero-intro">
  <div class="media">{('<video autoplay muted loop playsinline poster="' + IMG['waiter'] + '"><source src="' + VIDEO + '" type="video/mp4"></video>') if VIDEO else ('<img src="' + IMG['waiter'] + '" alt="">')}</div>
  <div class="wrap">
    <div>
      <div class="cat"><span class="lab light">Restoran Franš · Bulevar oslobođenja, Beograd</span><span class="lab light">Pon–Sub · 9–00h</span></div>
      <h1 class="h1">Bašta u kojoj Beograd <em class="it">slavi</em> od 1982.</h1>
      <p class="lede">Tradicija i elegancija pod starim stablima: jelovnik koji se ne menja po modi, sto koji vas čeka i konobar koji zna šta pijete.</p>
      <div class="ctas"><a class="btn light solid" href="#rezervacija">Rezervišite sto <span class="ar">→</span></a><a class="btn light" href="#jelovnik">Jelovnik</a></div>
    </div>
    <div class="side"><span class="lab light">Godina sa vama</span><span class="big" data-move="number-scramble">44</span></div>
  </div>
  <div class="strip"><div class="wrap"><span class="lab light">Since 1982</span><span class="lab light">Bašta · Restoran · Proslave</span><span class="lab light">Nedeljom ne radimo</span></div></div>
</section>

<section class="sec quote" id="o-nama">
  <div class="wrap">
    <span class="lab">Iz Beograda, za Beograd</span>
    <h2 class="big" data-move="scale-settle">Franš je izlazak.</h2>
    <p class="body" data-move="word-blur-in">Idemo, lutamo, istražujemo novitete, ali mu se ipak uvek vraćamo. I on nas čeka, na starom mestu — uvek bolji, svežiji, lepši. Kad je bilo najgore, u Franšu nam je bilo bolje. A kad nam je bilo dobro, gde smo to slavili, ako ne u Franšu?</p>
    <p class="who lab">Mirjana Bobić Mojsilović</p>
  </div>
</section>

<section class="sec tight" id="basta">
  <div class="wrap">
    <div class="gh"><div><span class="lab">Bašta i restoran</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">Hlad, beli stolnjaci i dug sto za sve vas.</h2></div><p class="lede">Bašta pod starim stablima leti, restoran zimi. Isti stolnjaci, iste čaše, isti ljudi koji vas dočekuju.</p></div>
    <div class="garden one">
      <div><div class="big" data-move="clip-reveal"><img src="{IMG['long-table']}" alt=""></div><div class="cap"><span class="lab">Bašta · dugi sto pod stablima</span><span class="lab">Proslave · rođendani · večere do ponoći</span></div></div>
    </div>
  </div>
</section>

<section class="sec" id="jelovnik">
  <div class="wrap">
    <div class="menu">
      <div><span class="lab">Jelovnik</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">Tartufi, biftek i ono što se ne menja.</h2><p class="lede" style="margin-top:22px">Pola porcije se naplaćuje 65% od cene. Cene su sa porezom, u dinarima.</p><div class="photo" data-move="clip-reveal"><img src="{IMG['octopus']}" alt=""></div></div>
      <div><ul class="ledger" data-move="stagger-in">{ledger}</ul><div style="margin-top:28px;display:flex;gap:14px;flex-wrap:wrap"><a class="btn solid" href="https://frans.rs/menu/jelovnik/">Ceo jelovnik <span class="ar">→</span></a><a class="btn" href="https://frans.rs/bela-vina/">Vinska karta</a></div></div>
    </div>
  </div>
</section>

<div class="band" id="proslave" data-move="parallax" data-parallax="8">
  <img src="{IMG['basta-table']}" alt="">
  <div class="wrap">
    <div class="f"><b data-move="number-scramble">1982</b><span class="lab light">Otvoren na Bulevaru oslobođenja</span></div>
    <div class="f"><b data-move="number-scramble">44</b><span class="lab light">Godine sa vama · rasli smo zajedno</span></div>
    <div class="f"><b>9–00</b><span class="lab light">Ponedeljak – subota · parking čuvan</span></div>
  </div>
</div>

<section class="sec res" id="rezervacija">
  <div class="wrap">
    <div class="grid">
      <div class="photo" data-move="clip-reveal"><img src="{IMG['reservation-book']}" alt=""></div>
      <div>
        <span class="lab light">Rezervacija</span>
        <h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">Vaš sto, upisan.</h2>
        <form class="form" onsubmit="return false">
          <label><span class="lab light">Ime i prezime</span><input placeholder="Ime i prezime"></label>
          <label><span class="lab light">Telefon</span><input placeholder="+381"></label>
          <label><span class="lab light">Broj gostiju</span><input placeholder="2"></label>
          <label><span class="lab light">Datum</span><input placeholder="DD/MM"></label>
          <label><span class="lab light">Vreme</span><input placeholder="20:00"></label>
          <label><span class="lab light">Napomena</span><input placeholder="Bašta, rođendan…"></label>
          <div class="full"><a class="btn light solid" href="#">Pošaljite rezervaciju <span class="ar">→</span></a></div>
        </form>
        <div class="alt"><span>SMS · WhatsApp · Viber: +381 65 26 41 944</span><span>Fiksni: +381 11 26 41 944</span></div>
      </div>
    </div>
  </div>
</section>

<footer class="end" id="kontakt">
  <div class="wrap">
    <div class="cols">
      <div><h5>Restoran Franš</h5><ul><li>Bulevar oslobođenja 18G, Beograd</li><li>Ponedeljak – subota, 9–00h</li><li>Nedeljom ne radimo</li></ul></div>
      <div><h5>Jelovnik</h5><ul><li><a href="https://frans.rs/menu/jelovnik/">Jelovnik</a></li><li><a href="https://frans.rs/menu/deserti/">Deserti</a></li><li><a href="https://frans.rs/bela-vina/">Vina</a></li></ul></div>
      <div><h5>Proslave</h5><ul><li><a href="https://frans.rs/event/proslave/">Proslave</a></li><li><a href="https://frans.rs/frans-torte/">Torte</a></li><li><a href="https://frans.rs/360-tura/">360° tura</a></li></ul></div>
      <div><h5>Kontakt</h5><ul><li>pr@frans.rs</li><li>+381 11 26 41 944</li><li><a href="https://frans.rs/rezervacije/">Rezervacije</a></li></ul></div>
    </div>
    <div class="giant" data-move="giant-scrub" aria-hidden="true">Franš</div>
    <div class="legal"><span>© 2026 Restoran Franš · Beograd</span><span>Sledeće: rezervišite sto →</span></div>
  </div>
</footer>


<div class="bp" id="bp"><button class="x" id="bpx" aria-label="close">×</button>
  <div class="row"><span class="t">Font</span>
    <label><input type="radio" name="bf" value="brand" checked><span>Njihov · Cormorant</span></label>
    <label><input type="radio" name="bf" value="fraunces"><span>Fraunces</span></label>
    <label><input type="radio" name="bf" value="instrument"><span>Instrument Serif</span></label></div>
  <div class="row"><span class="t">Boje</span>
    <label><input type="radio" name="bw" value="brand" checked><i style="background:#0F2A14;outline-color:#F4EFE3"></i><span>Njihove</span></label>
    <label><input type="radio" name="bw" value="ink"><i style="background:#F4EFE3;outline-color:#0F2A14"></i><span>Tamno</span></label>
    <label><input type="radio" name="bw" value="terracotta"><i style="background:#2A130D;outline-color:#FBEFE9"></i><span>Terakota</span></label>
    <label><input type="radio" name="bw" value="navy"><i style="background:#0E1B2D;outline-color:#EEF2F8"></i><span>Navy</span></label>
    <label><input type="radio" name="bw" value="plum"><i style="background:#29121B;outline-color:#F8EEF1"></i><span>Šljiva</span></label></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
<script>{moves}</script>
<script>
addEventListener('load',()=>{{ Moves.init();
  document.querySelectorAll('#bp input').forEach(i=>i.addEventListener('change',e=>{{const h=document.documentElement; if(e.target.name==='bf') h.dataset.font=e.target.value; else h.dataset.world=e.target.value; h.dataset.font==='brand'&&delete h.dataset.font; h.dataset.world==='brand'&&delete h.dataset.world;}})); document.getElementById('bpx').onclick=()=>document.getElementById('bp').remove();
  const nav=document.getElementById('nav'); const onS=()=>nav.classList.toggle('solid', scrollY>innerHeight*.75); onS(); addEventListener('scroll',onS,{{passive:true}});
}});
</script>
</body></html>'''
out = os.path.join(D, 'index.html'); open(out, 'w').write(html); print(out, len(html) // 1024, 'KB', 'video' if VIDEO else 'no video')
