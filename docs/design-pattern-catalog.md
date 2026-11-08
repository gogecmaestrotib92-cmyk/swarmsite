# Katalog dizajnerskih poteza: početna inventura

Radni presek repozitorijuma, 8. novembar 2026. Ovo je inventar dokaza i stvarnih mogućnosti renderera za Butter, Cerebrium i Tengile, namenjen budućem izboru poteza po sadržaju. **Nije garancija sličnosti sa referencom, funkcionalna specifikacija za agenta, niti dokaz da su svi navedeni potezi provereni na mobilnom originalu.** Reference služe za analizu forme; isporuka koristi korisnikov sadržaj i odobrene ili licencirane assete.

## Kako čitati dokaze i statuse

- **Raw** je zapis u `lib/blueprints/raw/`: sadrži izmerene geometrije, CSS vrednosti i medije, ali i ručno dodeljene `role` i `note`. Ne tretirati svaku ulogu, napomenu ili odsustvo elementa kao merenje.
- **BP** je normalizovani `lib/blueprints/*.bp.json`: neki podaci potiču iz raw zapisa, neki su izvedeni ili podrazumevani. **DNA** je zaseban istraživački zapis sa opažanjima; njegove formulacije i mobilna zapažanja nisu isto što i uparena merenja. Tengile nema `dna/tengile/data.json`.
- **Podržano uslovno** znači da postoji putanja kroz današnji renderer; izbor i rezultat zavise od vrste beata, sadržaja, asseta i fallbacka. **Samo opisano** znači da je potez zabeležen, ali ovde nije pronađena odgovarajuća implementacija. **Recipe ne stiže do komponente** znači da je komponenta u kodu i recipe je imenuje, ali trenutni izbor komponente za tu vrstu beata preusmerava poziv. Status se odnosi na opisanu putanju, ne na sve moguće pozive funkcije.
- Browser test generisanog izlaza ne potvrđuje vernost referenci. Raw fajlovi nemaju datum snimanja, mobilni skup merenja ni DPR. Butter i Cerebrium beleže 1440 × 756; Tengile beleži visinu 756, ali ne i širinu — `normalize.py` koristi 1440 kao pretpostavku. Ne zaključivati o stvarnim mobilnim breakpointima izvornika iz tog fajla.

Izvori: [Butter DNA](../dna/butter/data.json), [raw](../lib/blueprints/raw/butter.json), [BP](../lib/blueprints/butter.bp.json); [Cerebrium DNA](../dna/cerebrium/data.json), [raw](../lib/blueprints/raw/cerebrium.json), [BP](../lib/blueprints/cerebrium.bp.json); [Tengile raw](../lib/blueprints/raw/tengile.json), [BP](../lib/blueprints/tengile.bp.json). Zajednički izvor implementacije: [recipes.py](../lib/templates/recipes.py), [render_bp.py](../lib/render/render_bp.py), [agentovi dozvoljeni potezi](../lib/swarm/agents.py). Šira ograničenja kataloga su u [postojećem auditu](blueprint-catalog-audit.md).

## Butter: svetli product editorial

| Potez / dokaz | Putanja i status | Uslovi i ograničenja |
| --- | --- | --- |
| **Tipografija i skala:** raw H1 103 px, 400, `DieGrotesk`, centriran; BP H2 58 px. DNA posebno opisuje regular grotesk i mirnu svetlu podlogu. | **Podržano uslovno:** `head_style`, `hero`, `font_for` i BP type podaci. | Font se mapira na dostupan font ili može biti nadjačan klijentovim izborom; veličina naslova se prilagođava dužini, `clamp`-u i širini. BP boje prolaze kroz paletu i mogu čuvati klijentovu paletu. Ovo nisu fiksne mere izlaza. |
| **Hero sa produktom:** raw hero 1 ekran, H1 centriran; BP navodi veliku medijsku površinu, a recipe `hero: shot`. DNA opisuje i viseće 3D elemente. | **Delimično:** `hero()` ima opšte prikaze medija, centrirani i split hero. `shot` nema zaseban branch; Butter sa izmerenom medijskom površinom ulazi u opštu putanju. | Potreban je upotrebljiv dodeljeni ili izabrani asset. Viseći 3D elementi nisu implementirani kao taj potez; slika izvornika se ne prenosi. |
| **Ticker kratkih poruka:** raw uloga `ticker`, 0,29 ekrana i četiri medijska elementa; DNA opisuje logo-marquee. Recipe predviđa `marquee` za `cells/facts`. | **Podržano uslovno:** `marquee()` pravi tekstualnu traku, ne originalni logo-marquee. | Kratke stavke; dugačak ili detaljan sadržaj prelazi u `cards`. Dupliran animirani sadržaj je `aria-hidden`, postoji statična lista. Ne pretpostaviti da je logo traka podržana samo zato što postoji tekstualni ticker. |
| **Tekst uz produkt vizual / smenjivanje strana:** raw `story` i `story-flip` uz različite položaje naslovnog bloka; recipe dodeljuje `story` za `steps`. | **Podržano uslovno:** `story()` za tekst i vizual; Concept može izabrati `story` za odgovarajuće beatove. | Dodeljeni software screenshot mora imati stvarnu širinu ≥500 px; ostali dodeljeni vizuali ≥640 px, a provere odbacuju prazne/simboličke i rezervisane tuđe assete. Za >4 stavke postoje posebni uslovi i fallback. Mobilni grid prelazi u jednu kolonu; tačna geometrija reference nije garantovana. Recipe poziv ne prenosi eksplicitni `flip=True`, pa se iz `story-flip` ne može obećati automatsko smenjivanje strana. |
| **Velika produkt tabla, blur-in reči, inline ikone u rečenici:** navedeni u DNA; BP beleži više `story`, `tabs-media`, `gallery-marquee` i `story-sticky` uloga. | **Samo opisano kao specifični potezi:** postoji generički reveal, ali nema dokazano ekvivalentnog blur-in-a po reči, inline ikona ni stvarne tabs interakcije. | Ne reklamirati kao dostupne opcije niti kao verno rekonstruisane interakcije. |

## Cerebrium: tamna infrastruktura i proof

| Potez / dokaz | Putanja i status | Uslovi i ograničenja |
| --- | --- | --- |
| **Lagani display i mono label:** raw H1 86 px / 300, body 17 px; BP H2 44 px i label 13 px uppercase. DNA beleži ABC Favorit i Suisse porodice i opisuje akcent na jednoj reči. | **Delimično:** skala i label-stil kroz `head_style` i CSS; fontovi kroz `font_for`. | Fontovi i boje mogu se zameniti odgovarajućim dostupnim mapiranjem ili vlasnikovim izborom. Nema potvrđene zasebne opcije za gradient na jednoj reči. |
| **Hero:** raw H1 levo u bloku širine 663 px, raw anotira WebGL pozadinu; DNA opisuje 3D magenta ribbon i poziv na interakciju. | **Delimično:** recipe bira `hero: centre`, a `hero()` podržava centrirani i split prikaz. | Centrirani recipe se razlikuje od raw leve kompozicije; nema dokaza o implementiranom WebGL ribbon-u / hold interakciji. |
| **Pinovana sekvenca stavki:** raw `feature-cards-sticky`, 4,18 ekrana, media širine 0,46; DNA opisuje pinovanu listu i zasebne interaktivne widgete. Recipe za prvi `features` bira `pinned-sequence`. | **Podržano uslovno:** `pinned_sequence()` prikazuje 2–5 stavki u pinovanom stage-u, uz vidljive sekvencijalne slajdove i pokazivače. | Ovo je komponenta inspirisana ritmom, nije widget po uzoru na original. `features` prihvataju validne pojedinačno dodeljene slike (≥600 px), ne uzimaju jednu generičku sliku za sve; bez slike ostaje tekst. Dodatna napomena, CTA ili source action, kao i neodgovarajući broj stavki, prebacuju u statične kartice/brojeve. U `nomotion` i reduced-motion režimu slajdovi su u normalnom toku; pri širini ≤900 px sekvenca postaje jednokolonska, ali pinovanje samo po sebi nije isključeno osim pri reduced-motion. |
| **Brojevi na tamnom bandu:** BP opisuje `cases-grid`/`cards-row`, recipe dodeljuje `numbers` sa `band: dark` za `facts/cells`. | **Podržano uslovno:** `numbers()` plus band iz recipe-a, ako ga beat nije eksplicitno zadao. | Interpretacija recipe-a, ne dokaz da original ima identičan blok brojeva. |
| **Tamno/svetlo alterniranje, logotipi, carousel, sfera i live widgeti:** DNA ih opisuje; BP sekcije i boje daju delimičnu strukturu, ali `colour.bands` je uglavnom `paper`. | **Delimično / opisano:** renderer poznaje bandove i statične kartice, ali ne postoji dokaz da reprodukuje izvorni redosled alterniranja, widgete, sferu ili case-study carousel. | Ne izmišljati metrike, korisnike, studije slučaja ili slike samo da bi se postigao vizuelni efekat. |

## Tengile: foto editorial i lodge

| Potez / dokaz | Putanja i status | Uslovi i ograničenja |
| --- | --- | --- |
| **Foto/video hero:** raw anotira full-bleed VIDEO 1425 × 756, H1 120 px uppercase PP Fragment; BP `hero-video`, `video_hero: true`. | **Podržano uslovno:** recipe `hero: photo`, `hero()` može prikazati lokalni `hero.mp4` kao autoplay/muted/loop/playsinline ili odobrenu fotografiju. | Potreban je stvarni video ili pogodan vizual. Video ne treba izmišljati ili preuzimati s reference. Naslov, font i geometrija su adaptivni, a ne replika raw 120 px. |
| **Desno poravnata izjava:** raw `statement-right` H2 32 px sa `x≈0,50` i `wf≈0,48`; recipe prvi `quote` daje `statement` sa `variant: right`. | **Podržano uslovno:** `statement_v()` menja položaj i širinu na osnovu varijante, zatim `statement()`. | Prikazuje klijentov sadržaj; tipografski zaštitni minimumi i responsive layout menjaju izlaz. |
| **Par fotografija / kolaž:** raw `photo-pair` ima dva portretna medija; `collage` tri; recipe imenuje `photo-pair` i `collage` slotove. | **Recipe ne stiže do komponente:** `component_for()` za `type: photo` vraća `photo` ili eksplicitni `story`, čime prepisuje komponentu iz slota. Funkcije `photo_pair()` i `collage()` postoje, ali samo njihovo prisustvo ne dokazuje da ih ovaj recipe trenutno koristi. | Te funkcije zahtevaju najmanje dve odgovarajuće fotografije i imaju fallback. Pre izlaganja agentu potrebna je eksplicitna putanja izbora i browser test očuvanja vlasništva i natpisa. |
| **Full-bleed fotografija i foto-priča:** raw `photo-bleed` beleži `wf≈1,08`; `story-right` kombinuje tekst i medije. | **Podržano uslovno:** `photo_sec()` i `story()` imaju foto prikaz; `photo` beat se bez eksplicitnog `story` usmerava u `photo`. | `photo_sec()` zahteva sopstvenu dodeljenu sliku; za veliki prikaz primenjuje pragove i fallback. Foto-priča traži podobnu fotografiju; pogodna kratka `place` priča može dobiti editorial overlay. Pri ≤900 px ili visini ≤700 px taj editorial prikaz prelazi u redovan vertikalni tok. |
| **Foto marquee, overlay, map pins i spori image reveal:** raw beleži `marquee-photos` i `photo-text-overlay`, BP `motion.idea` ih opisuje. | **Samo opisano kao Tengile potezi:** generički `marquee()` je tekstualni; `overlay()` postoji, ali Tengile recipe nema overlay slot, a foto sekciju `component_for()` preusmerava na `photo/story`. Ne nalazi se implementacija mape sa idle pinovima. | BP motion vrednosti ne dokazuju isti efekat; generički reveal/parallax i reference na GSAP nisu dokaz iste animacije. |

## Šta agent danas zaista može da izabere

Concept schema izlaže `sticky-product`, `pinned-sequence`, `type-wall`, `marquee`, `story`, `cards` i `auto` za beat; za hero samo `default` i `split`. Ovo nije isto što i pun skup komponenti recipe-a: foto-par, kolaž, foto overlay, konkretna nav kompozicija ili izvorne interakcije nisu samostalni agentovi izbori. `component_for()` ima dodatne provere vrste, broja i sadržaja i može preusmeriti traženi potez na fallback. Na primer, ticker za `features` sa detaljima ne postaje skraćena traka; agentova namera nije dokaz izvršenja.

Na širini ≤900 px renderer za više komponenti koristi jednu kolonu i skriva nav linkove; `nomotion` i `prefers-reduced-motion` daju statični prikaz pinovane sekvence. To su ponašanja izlaza, ne merenja mobilne reference. Učitavanje GSAP/ScrollTrigger-a zavisi od spoljnog skripta, pa interakcije zahtevaju posebnu proveru dostupnosti i tastature. Generisani prikaz treba testirati i kad biblioteka nije dostupna.

## Predlog mašinski čitljive sheme

Predlog za budući katalog, ne postojeći format ili implementacija. Jedan zapis treba da razdvaja referentni dokaz od izvršive sposobnosti, sa stabilnim ID-jem i verzijom. Na primer:

```json
{
  "id": "text-ticker",
  "version": 1,
  "reference": {
    "blueprint": "butter",
    "evidence": [{"file": "lib/blueprints/raw/butter.json", "pointer": "/sections/1", "kind": "measurement_and_annotation"}],
    "viewport": {"width": 1440, "height": 756, "dpr": null},
    "capture_date": null,
    "limitations": ["no structured mobile measurement", "role is annotated"]
  },
  "implementation": {
    "status": "conditional",
    "renderer": "marquee",
    "agent_move": "marquee",
    "accepted_beat_types": ["cells", "facts"],
    "fallback": "cards",
    "asset_requirements": "text only",
    "responsive": "static list available; verify reduced motion",
    "content_constraints": "short items; never discard descriptions"
  },
  "verification": {"browser_fixtures": [], "desktop": "not_recorded", "mobile": "not_recorded", "reduced_motion": "not_recorded"}
}
```

Kod validacije treba proveriti obavezna polja i verziju, postojanje fajla i JSON pointera, konzistentnost statusa sa stvarnim enumom agenta i putanjom `component_for`/recipe, kao i uslove asseta i fallbacka. Za svaki `conditional` potez zahtevati pozitivni i negativni fixture, očuvanje svih činjenica, CTA-ova i source linkova, bez krađe dodeljenih slika; browser proveru desktop + mobile + reduced motion i bez eksternog JS-a kada je animacija bitna. Beležiti stvarne viewport/DPR, datum, verziju koda i rezultate umesto praznih tvrdnji o podršci. Potez `described_only` ne treba nuditi agentu kao izvršivu opciju dok se ne implementira i ne prođe vizuelni i funkcionalni pregled.

### Reference candidate: Neutra VDL (editorial typography)

- Source: Awwwards, *Hot Right Now 2023*, p. 115: https://assets.awwwards.com/awards/gallery/2023/07/HOT-RIGHT-NOW-BOOK-2023.pdf
- Observed in the published screenshots: oversized stacked type, a restrained top navigation, a smaller vertical group of contextual links and a carefully organized editorial grid; the menu is rendered as a full-page contents list.
- Transferable candidates: large responsive typographic hero; compact contextual link rail; editorial contents/menu. These are design observations, not implemented components or verified production patterns.
- Scope: based on Awwwards screenshots only. The live site, scroll behavior, mobile experience and presence or absence of 3D elsewhere have not been verified. No parity or production suitability is claimed.

## Pangram Pangram — tipografski katalog i serija postera

Referenca koju je korisnik izabrao: https://pangrampangram.com/ . Pregled početne stranice u browseru 8. novembra 2026, desktop; ovo nisu mobilna merenja niti validacija renderer komponente.

- **Uvučeni široki poster:** uz belu stranicu pojavljuje se širok zaobljeni pravougaonik sa pozadinom, centriranim ogromnim naslovom, kratkim tekstom i dva pill dugmeta; mali bedž daje kontekst. Ispod sledi drugi takav poster drugačije vizuelne atmosfere. Za našu primenu: jasno dodeljeni vizual, tekst i stvarni CTA; proveriti kontrast, bezbedno prelamanje i mobilni raspored. Status: zabeleženo, nije implementirano kao ovaj potez.
- **Serija različitih vizuelnih poglavlja:** više samostalnih plakata sa istom geometrijom ali različitom tipografijom, bojom i slikom daje ritam bez potrebe za 3D scenom. Potrebni su različiti relevantni vizuali; bez njih ne ponavljati istu sliku niti izmišljati sadržaj. Status: koncept, nije implementirano kao takav sistem.
- **Prebacivanje grid/list view:** vidljiv izbor Card view / List view iznad kataloga. Prenosivo za duge liste stvarnih proizvoda/projekata; mora čuvati podatke, pristup tastaturom i oznaku izabranog prikaza. Status: zabeleženo, nije potvrđeno u našem rendereru.
- **Kartica kao mali tipografski poster:** grid uključuje naziv, opis i demonstraciju tipa. Za druge biznise koristiti stvarne proizvode/primere, bez izmišljenih kataloga. Status: zabeleženo, nije potvrđeno u našem rendereru.
- **Fontovi i licence:** FAQ navodi da su trial fontovi za lične/nekomercijalne projekte i probe; web licenciranje zavisi od upotrebe i pageview-a. EULA zabranjuje deljenje font fajlova neovlašćenima. Za komercijalni SaaS, preview i distribuirani kit ne pretpostavljati da standardna ili starter-pack licenca pokriva sve klijente i isporuku; proveriti konkretne uslove ili tražiti odgovarajuću licencu od izdavača. Izvori: https://pangrampangram.com/pages/faq ; https://pangrampangram.com/pages/eula ; https://pangrampangram.com/products/fsp . Alternativa su odgovarajuće licencirani otvoreni fontovi; potrebno je proveriti karaktere za korisnikov jezik i vizuelni rezultat.

Lokalni prototip `billboard`: renderer može prikazati jednu dodeljenu hero fotografiju u zaobljenom panelu sa centriranim postojećim naslovom, tekstom i CTA-ovima; tamna podloga osigurava čitljivost teksta. Concept schema lokalno nudi potez samo kada postoji dodeljena slika, dok renderer dodatno odbija screenshot i neupotrebljive slike. Ovaj prototip još nije testiran kroz novi produkcijski posao niti objavljen; ne tvrdi identičnost Pangram sajtu i ne koristi njihove fontove ili vizuale.

## Synchronized Studio — eksperimentalni tipografski portfolio

Korisnikova referenca: https://synchronized.studio/ . Posmatrano u browseru 8. novembra 2026. na desktopu: početni ekran posle učitavanja i deo stranice pri skrolu. Mobilna verzija, interakcije tastaturom i ponašanje sa smanjenim pokretom nisu ovde provereni.

- **Rasuti ogromni serifni naslov:** više velikih delova reči na različitim pozicijama preko tamne podloge i mali sekundarni tekst. Za našu varijantu očuvati stvarni smisleni H1, čitljivost i selektabilni tekst; posebnu pažnju posvetiti dugim rečima i uskim ekranima. Status: opaženo; ovo nije isto što i postojeći `type-wall` i nije implementirano kao hero.
- **Sitna ugaona navigacija nasuprot velikom naslovu:** logo/identitet levo, lista navigacije desno. Za našu varijantu koristiti stvarne linkove, vidljiv fokus i mobilni meni. Status: koncept; nije potvrđena ekvivalentna komponenta.
- **Grafički akcenti tokom skrola:** tanke geometrijske forme i kružni natpis između sadržaja. Pravljenje varijante zahteva sopstveni dekorativni oblik, koji ne sme nositi ključnu informaciju; obezbediti mirnu varijantu bez pokreta. Status: opaženo, nije implementirano kao ovaj efekat.
- **Kontrast svetlih portfolio-kartica i crne pozadine:** veliki svetli paneli s fotografijom, naslovom, opisom i rednim brojem. Primena samo kada korisnik zaista ima projekte, njihove opise i dodeljene vizuale; ne izmišljati primere ni nagrade. Status: opaženo, nije potvrđen ekvivalentan renderer.
- Ovaj primer je pogodan za izražajan studio/portfolio, a njegovo razlamanje teksta možda nije dobar izbor za svaku vrstu sajta. Opažanja ne potvrđuju odsustvo 3D niti celokupnu funkcionalnost originala.

Lokalni prototip `editorial-type`: jedan čitljiv veliki naslov na kontrastnoj podlozi, stvarni CTA i opcioni vizual. Concept schema ga ograničava na service sajtove; na sintetičkom primeru kreativnog studija stvarni model ga je izabrao. Prototip nije rekonstrukcija originalnog razlomljenog sloga, animacije ili portfolio-kartica, i nije objavljen. Bez slike automatski contract trenutno prijavljuje odsustvo vizuala u prvom ekranu; sa testnom slikom contract je 100/100. Potrebno je proveriti takav namerno tipografski hero i kriterijum contracta na stvarnim primerima pre produkcije.
