# Inventar referenci — 10 početnih sajtova

Radni pregled, 8. novembar 2026. Cilj je više različitih vizuelnih jezika. Ovo nisu 10 novoizmerenih niti implementiranih blueprintova: prvih devet polazi od postojećih raw fajlova, čiji datum i mobilno merenje nisu zabeleženi. Opisi u raw `note` i `role` su anotacije, ne nužno direktna merenja. Live sadržaj se može promeniti. Potezi nisu automatski dostupni agentima.

## Prioriteti za izradu

1. **CRAV:** plakatni hero, smene crvene/žute, slike sa prozirnom pozadinom i dekorativne trake; fallback bez izrezanog proizvoda mora zadržati sve naslove i CTA.
2. **Units:** mekani obojeni bandovi, veliki pill CTA i foto–tekst–foto raspored; zahtevaju stvarne dodeljene slike.
3. **Aino:** asimetrični portfolio grid i indeksne oznake; ne izmišljati projekte niti skrivati opise.
4. **Halfdays:** urednički foto-par i produktne kartice; ne predstavljati redovne informacije kao e-commerce artikle.
5. **Butter:** priča uz screenshot i promene ritma; dostupnost proveriti kroz stvarni renderer.

Ponavljajući potezi nisu automatski kompatibilni: svaki traži pravilo izbora, proveru vlasništva nad slikama, mobilni fallback, očuvanje svih činjenica i linkova i vizuelnu proveru.

## Crav — loud-brand-poster

- Referenca: https://www.cravburgers.shop/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/crav.json); [normalizovani blueprint](../lib/blueprints/crav.bp.json).
- Primena: Restoran, hrana, događaji i brendovi sa smešnim ili energičnim tonom.
- Zabeležena paleta: #f5e3cd, #ffd750, #f91814, #1b1b1b. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: poster site: condensed display at 216–504px, stickers/cutouts scattered with rotation, colour bands (cream/red/yellow), SVG curved divider, wobbly outline filter on cutouts.
- Zabeleženi potezi po sekcijama:
  - `hero-poster`: 432px condensed headline full width, product cutout 576px over it, 40px chunky labels.
  - `statement-stickers`: 216px centred 3-line headline, cutouts pinned at the left edge.
  - `band-red`: full-bleed red band, headline centred, cutouts at both edges.
  - `photo-bleed`: medija u zapisu: 1.
  - `sticker-row`: row of small contained stickers/badges.
  - `curve-divider`: big SVG path curve separating bands.
  - `statement-left`: naslov 216 px u izvornom zapisu.
  - `band-cream-collage`: cream band, headline left 504 wide, overlapping photo + cutouts.
  - `footer-giant`: 504px wordmark cropped at the bottom, stickers around, 26px columns.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Units — coliving-pastel-cards

- Referenca: https://units.gr/en/homepage/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/units.json); [normalizovani blueprint](../lib/blueprints/units.bp.json).
- Primena: Stanovanje, zajednica, usluge i lifestyle.
- Zabeležena paleta: #f4e9e1, #eef1f5, #0072e3, #ffdb07, #ff5c38. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: page background colour crossfades per section (1.8s), pastel bands, pill buttons, pinned 5-screen feature list with 405px photo cards sliding.
- Zabeleženi potezi po sekcijama:
  - `hero-photo-inset`: inset 16:9 photo card (167 frame), headline + pill over it.
  - `intro-map`: 15px paragraph 446 wide left, map 723x473 right, small coral pill tags.
  - `pinned-cards`: 5-screen pinned: list of amenities left, 405px photo cards slide in from the right.
  - `text-icons-cta`: medija u zapisu: 1.
  - `photo-text-photo`: portrait photo | text column 342 | portrait photo.
  - `cards-3up-contained`: three 342x289 illustration cards with text.
  - `photo-marquee`: marquee of 268x330 photos, big pill.
  - `footer`: detalji u raw zapisu.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Aino — index-grid

- Referenca: https://aino.agency/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/aino.json); [normalizovani blueprint](../lib/blueprints/aino.bp.json).
- Primena: Kreativni portfolio i projekti sa snažnom fotografijom.
- Zabeležena paleta: #181818, #f5f5f0. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: almost no motion: hover colour 0.1s, blinking clock; the rhythm IS the motion.
- Zabeleženi potezi po sekcijama:
  - `work-2up`: two 4:5 tiles, index label under each (A002 NAME).
  - `statement`: the only sentence on the page; h1 38px bold 874px + two small pills.
  - `work-asym`: big tile left, small tile top-right (1 col), empty middle.
  - `work-2up`: medija u zapisu: 2.
  - `work-full`: one 16:9 tile full width.
  - `work-3up`: three 1-col tiles, fourth column empty.
  - `work-full`: medija u zapisu: 1.
  - `services-footer`: 4 equal columns of 13px uppercase lists.
  - `footer`: medija u zapisu: 1.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Halfdays — apparel-shop-grid

- Referenca: https://www.halfdays.com/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/halfdays.json); [normalizovani blueprint](../lib/blueprints/halfdays.bp.json).
- Primena: Proizvodi, odeća i katalog sa dobrim fotografijama.
- Zabeležena paleta: #ffffff, #121212, #fff9bb. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: shop: almost no motion, product grids, 20px frame, uppercase 24–26px section titles, white page, black 56px buttons, yellow accent label.
- Zabeleženi potezi po sekcijama:
  - `hero-photo-left`: 16:9 bleed photo, 44px headline top-left (x=20,y=92 under nav) 461 wide, yellow 13px label.
  - `product-row-small`: row of 222x307 product tiles (6 across), 12px gaps.
  - `photo-3up-tall`: three 2:3 editorial photos 587 wide, edge to edge, horizontal scroll.
  - `story-photos-text`: two photos left (square + portrait), 26px uppercase title + 16px paragraph right column 454 wide.
  - `product-row-titled`: title column left (225), product tiles 207x311 with 14px names.
  - `footer-newsletter`: dark footer: 22px line, newsletter field + 56px white button, 10px uppercase meta.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Butter — editorial-product-story

- Referenca: https://www.butter.video/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/butter.json); [normalizovani blueprint](../lib/blueprints/butter.bp.json).
- Primena: Softver sa stvarnim, čitljivim produktnim vizualima.
- Zabeležena paleta: #fafafa, #ededed, #353535, #0a0909, #151515. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: nema objedinjene napomene; proveriti sekcije.
- Zabeleženi potezi po sekcijama:
  - `hero`: naslov 103 px u izvornom zapisu; medija u zapisu: 1.
  - `ticker`: medija u zapisu: 4.
  - `statement`: naslov 58 px u izvornom zapisu; medija u zapisu: 4.
  - `story`: naslov 58 px u izvornom zapisu; medija u zapisu: 3.
  - `story-flip`: naslov 58 px u izvornom zapisu; medija u zapisu: 1.
  - `story-wide`: naslov 58 px u izvornom zapisu; medija u zapisu: 1.
  - `feature-cards`: naslov 44 px u izvornom zapisu; medija u zapisu: 4.
  - `tabs-media`: naslov 58 px u izvornom zapisu; medija u zapisu: 1.
  - `gallery-marquee`: naslov 44 px u izvornom zapisu; medija u zapisu: 1.
  - `story-sticky`: naslov 44 px u izvornom zapisu; medija u zapisu: 1.
  - `double`: naslov 44 px u izvornom zapisu; medija u zapisu: 2.
  - `showcase-list`: naslov 21 px u izvornom zapisu; medija u zapisu: 1.
  - `footer`: medija u zapisu: 1.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Cerebrium — dark-light-bands

- Referenca: https://cerebrium.ai/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/cerebrium.json); [normalizovani blueprint](../lib/blueprints/cerebrium.bp.json).
- Primena: Tehnološke usluge i softver sa konkretnim dokazima.
- Zabeležena paleta: #101421, #ffffff, #eef2f5, #dbe5ed, #172b76. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: nema objedinjene napomene; proveriti sekcije.
- Zabeleženi potezi po sekcijama:
  - `hero`: full-bleed webgl canvas behind; h1 left 663px; logo ticker at bottom; CLICK AND HOLD affordance.
  - `feature-cards-sticky`: 2-col: left sticky copy stack, right tall cards 663x775 scrolling; mono labels with data (CAPACITY : 2500+).
  - `statement`: dark band: mono label, 57px light display line, 27px body, pink button.
  - `logo-grid`: 20-col strip of partner marks.
  - `cases-grid`: container-sm 1240; centered h2; 2x2 list rows with 47px icon + h3 21px + 17px body.
  - `cards-row`: 3 cards 453px wide, image 199x165 contained, h3 27px; horizontal carousel with arrows.
  - `features-list`: label left (435px col), content right from x=500.
  - `blog-cards`: 3 portrait cards 435x560, title inside card bottom.
  - `footer`: dark footer: 36px statement left 663px + CTA, link columns right at 723/1064.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Lpas — studio-grid-26

- Referenca: https://lpas.com/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/lpas.json); [normalizovani blueprint](../lib/blueprints/lpas.bp.json).
- Primena: Arhitektura i portfolio sa stvarnim projektima.
- Zabeležena paleta: #ffffff, #262626, #111111, #e3c1aa, #707569. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: 26-column grid; one sans at 9 sizes; pinned 6.7-screen hero where project cards slide in from the right over a dimmed video (brightness .5); sticky work section.
- Zabeleženi potezi po sekcijama:
  - `pinned-hero-rail`: dimmed bleed video, 75px sans h1 900 wide at x=50; on scroll, 800x582 project cards with 56px titles slide in from the right (x=1162, 1802…) — the hero is a horizontal rail.
  - `manifesto`: 56px four-sentence manifesto 658 wide; 14px stacked verbs; 16px paragraph 791 wide.
  - `work-grid-sticky`: 38px title; one big 16:10 image left (671), two small 16:10 right (330) — 2:1:1 split, sticky title.
  - `updates-list`: 28px title, dated rows (16px source/date + 14px text 457 wide).
  - `footer-photo-offices`: 2-screen footer: oversized bleed photo, office columns 171 wide at 267px pitch.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Tengile — editorial-lodge

- Referenca: https://tengilemalamala.com/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/tengile.json); [normalizovani blueprint](../lib/blueprints/tengile.bp.json).
- Primena: Ugostiteljstvo i putovanja sa kvalitetnim fotografijama.
- Zabeležena paleta: #f5eee9, #e3e1d4, #373f1d, #5c6e21. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: slow expo easings 1.6–2s on image reveal (blur+scale), image marquee band, map with idle pins.
- Zabeleženi potezi po sekcijama:
  - `hero-video`: full-bleed video, giant uppercase light serif h1 top-left at y=166, 18px serif lede 336px wide.
  - `statement-right`: 32px serif paragraph in right half (x=721, 689 wide); small Inter 14 label left.
  - `photo-pair`: two portrait photos offset (left bleeds edge, right larger), 16px Inter caption 343px.
  - `statement-full`: 48px light serif across full container.
  - `cards-3up`: uppercase 14 label, 3 portrait cards 508x619 with 20px serif title + 16px text under.
  - `cards-3up`: same as 5 (CAMPS).
  - `quote-band`: 48px serif quote indented to x=140, 1158 wide, 80px pads.
  - `photo-bleed`: full-bleed 16:9 photo, slight overscan (parallax).
  - `story-right`: 32px serif in right half + two small photos (portrait + square) under it.
  - `collage`: small scattered photos around a centered 32px heading.
  - `marquee-photos`: 32px serif left half, then horizontal photo marquee of 520px-wide mixed-aspect images.
  - `photo-text-overlay`: tall bleed photo with 32px serif paragraph bottom-right (x=728, 459 wide).
  - `footer`: olive footer, 219px link columns from x=16.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## White-Desert — cinematic-travel

- Referenca: https://white-desert.com/
- Dokazi: [raw merenja i anotacije](../lib/blueprints/raw/white-desert.json); [normalizovani blueprint](../lib/blueprints/white-desert.bp.json).
- Primena: Putovanja i iskustva sa stvarnim širokim vizualima.
- Zabeležena paleta: #ffffff, #090b10, #1f2a44, #e9e7e1. Ovo nisu automatski boje izlaza.
- Pokret / napomena iz raw zapisa: page transitions, reveal keyframes, a long pinned camps sequence (11.8 screens), giant condensed wordmarks.
- Zabeleženi potezi po sekcijama:
  - `hero-video-giant`: 2-screen hero: full-bleed video, 256px condensed uppercase wordmark centered, 18px serif lede 294 wide, small inset photo.
  - `statement-uppercase`: 42px uppercase serif, 708 wide, offset right of centre (x=484), a full screen for one sentence.
  - `photo-bleed-tall`: tall bleed photo with caption words in Oswald 18.
  - `section-title`: white band, 320px top pad, centred 60px uppercase serif title.
  - `cards-2up-wide`: two half-width trip cards 720x643, italic serif 42 title top-left inside, 16px body; carousel continues (third at x=897).
  - `quote-centre`: 22px serif paragraph 472 wide, 320px pads.
  - `pinned-sequence`: pinned 11.8-screen sequence: bleed photos swap behind, camp cards slide horizontally from right (x=1460), 140px uppercase serif title.
  - `giant-wordmark`: 320px condensed route code as a section divider.
  - `itinerary-overlay`: tall bleed photo with time-stamped itinerary rows (42px times left) and small video thumb right.
  - `cta-photo`: full-screen photo, centred uppercase serif + outlined button.
  - `footer-sand`: sand footer with a quote, 10px uppercase attribution, badges.
- Status: **istraživačka referenca**; sekcije, animacije i mobilni raspored nisu u ovom pregledu dokazano preneti u renderer.

## Neutra VDL — urednička tipografija

- Referenca: https://neutra-vdl.org/; Awwwards opis i snimci: https://assets.awwwards.com/awards/gallery/2023/07/HOT-RIGHT-NOW-BOOK-2023.pdf, str. 115.
- Potezi vidljivi na objavljenim snimcima: veliki složeni naslov, suzdržana navigacija, vertikalni skup kontekstnih linkova, editorial grid, meni kao sadržaj stranice.
- Primena: arhitektura, institucije, kultura, editorial.
- Status: kandidat iz snimaka; nije potvrđen čitav živi sajt, mobilna verzija ili odsustvo 3D.

## Šta još nedostaje

Za ove reference treba proveriti desktop i mobilne originalne stranice, identifikovati dozvoljene/korisnikove assete i uneti tačne uslove i fallback za svaku komponentu. Tek zatim ih povezati sa izborom kreativnog agenta i uporediti stvarne generisane primere sa referencama. Postojeći eksperimentalni katalog i renderer ne pokrivaju čitav ovaj inventar.

## Provera dostupnosti u postojećem engine-u

- **Units / Aino foto-par:** recipe ga navodi, ali `component_for()` za `photo` bira `photo` ili `story`; sam recept nije dokaz da se foto-par izvršava.
- **CRAV kolaž:** recipe ga navodi, ali isti izbor za `photo` ga može preusmeriti. `stickers` i `product-row` postoje kao komponente, no potrebno je zasebno proveriti dostupne ulaze, fallback i stvarni render pre ponude agentu.
- **Halfdays kolaž:** recipe ga navodi, ali ga izbor za `photo` može preusmeriti; kartica i foto raspored nisu automatski verni originalu.
- **Butter story:** eksperimentalni katalog ima ograničene proverljive story/marquee predloge, ali nije povezan sa produkcijskim agentima.
- **Cerebrium, Butter i White Desert:** u raw zapisima postoje i 3D, canvas ili video elementi; ova inventura ih ne svrstava u potvrđene reference bez 3D. Prednost za jednostavnije ponovno izvođenje treba dati CRAV/Aino/Halfdays/Units, uz pregled živih sajtova pre zaključka o njihovim animacijama.

### Units: dodatna vizuelna provera

Pregledan živi desktop prikaz 8. novembra 2026: uz levi rub stoji uska vertikalna navigacija sa velikim numerisanim karticama u plavoj, žutoj, narandžastoj, zelenoj i ljubičastoj; uz nju je velika zaobljena fotografija s centriranim naslovom i pill CTA. Naredna sekcija su dve zaobljene površine — tekst i mapa — praćene crvenom horizontalnom trakom. Ovo su opažene desktop forme, ne potvrda mobilnog ponašanja ili prava na slike. Za naš renderer: napraviti verziju sa korisnikovim stvarnim linkovima i sadržajem; mapa samo ako postoji stvarna lokacija; izbor boja i kontrast moraju poštovati korisničke postavke. Nijedna od ovih posebnih kompozicija nije ovim pregledom proglašena implementiranom.

### Aino: odstupanje od arhiviranih podataka

Pri desktop pregledu živog `https://aino.agency/` 8. novembra 2026 početni prikaz je pokazao tamnu pozadinu i animiranu ilustraciju od monospace znakova, uz jednostavnu navigaciju; to ne potvrđuje ranije zabeleženi foto-grid iz raw datoteke. U trenutnom browser prikazu ASCII animacija se nastavila i tokom pokušaja skrola, pa ostatak sajta i mobilni raspored nisu uspešno provereni. Stari `aino.json` tretirati kao prethodno snimljenu referencu, ne kao dokaz sadašnje naslovne strane.

### Halfdays: dodatna vizuelna provera

Desktop, 8. novembar 2026, EU verzija: puna fotografija kao hero sa velikim nazivom i kratkim linkom u jednoj strani, a ispod pravilna traka šest portretnih fotografija sa nazivima kategorija i strelicama. Zatim slede veće fotografske kartice. Primena zahteva odgovarajuće stvarne fotografije, kategorije i odredišta; nije dokaz da su postojeće `product-row` ili karusel identični originalu. Mobilni prikaz nije posmatran.

### Tengile: dodatna vizuelna provera

Desktop, 8. novembar 2026: kadar prirode preko celog ekrana, dugačak naslov podeljen u dve horizontalno pomerene linije, kratki tekst i CTA na desnoj polovini, zatim svetla sekcija sa sitnom oznakom levo i velikim serifnim pasusom desno. Uočeni raspored je jak zbog fotografije/video-materijala i tipografije, pa renderer ne treba da pozajmljuje tuđi vizual ili izmišlja lokaciju. Prikaz na telefonu i efekti smanjenog pokreta nisu ovim pregledom potvrđeni.

### Butter: dodatna vizuelna provera

Desktop, 8. novembar 2026: odvojeni zaobljeni navigacioni paneli, centriran veliki naslov, kratak podnaslov i jedno primarno dugme, uz prepoznatljiv slojeviti vizual iznad. Pri skrolu se pojavljuju animirani tipografski i slikovni elementi; uhvaćeni kadar tokom prelaza nije dokaz konačnog stanja sekcije. Naša postojeća `story` forma nije isto što i čitav ovaj hero ili 3D vizual; mobilni prikaz i motion fallback ovim pregledom nisu provereni.

### White Desert: dodatna vizuelna provera

Desktop, 8. novembar 2026: kadar životinje ispunjava hero, preko donjeg dela je širok veliki naziv, uz sitan serifni tekst i kontrolu za film sa strane. Pri skrolu je viđen svetli prelaz koji u posmatranom trenutku još nije završio; ne koristiti taj poluprazni kadar kao specifikaciju sekcije. Pokret i uski ekran nisu detaljno testirani. Kompozicija zavisi od stvarnog kvalitetnog vizuala korisnika.
