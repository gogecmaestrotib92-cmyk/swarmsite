# DNA — Zaključci posle 2 kruga (16 sajtova, desktop + mobilni)

## 1. Glavni zaključak

**"Wow" nije stil. Wow je KONCEPT + 4 sloja ispod njega.** Svaki dobar sajt koji sam otvorio radi istu stvar: izabere jedan svet, i onda tipografija, boje, pokret, komponente i copy svi služe tom svetu. Prvi demo (SportBot u belo-sivo) nije imao svet — zato je bio reskin.

Sistem koji treba da napravimo ima 5 slojeva, i svaki je bilo moguće izvući iz pobednika:

```
KONCEPT (svet)  →  TIP SISTEM  →  KOMPONENTE  →  MOTION REČNIK  →  KRAJ (footer kao brend momenat)
```

## 2. Biblioteka koncepata (8 svetova koje sam stvarno video, sa dokazima)

| # | Koncept | Dokazi | Za koga | Potpis (šta ga odaje) |
|---|---|---|---|---|
| C1 | **Tehnički crtež / blueprint** | Heron, Illoca, Sharplink, ICOMAT | SaaS, inženjering, fintech, data proizvodi (**SportBot!**) | papir/grid pozadina, mono labele, isprekidane vodilje, kvadratni markeri, kote, hotspot pilule, register marks |
| C2 | **Švajcarski modularni grid** | Aspen Search | B2B usluge, agencije, advokati, konsultanti | sve u ćelijama sa 1px linijama, ćelije kao blokovi boje, halftone tekstura, sat/lokacija, brojači 01–06 |
| C3 | **Ravni svetovi boja** | Maxima, DeepBook | neprofitne org., edukacija, dečji/lifestyle brendovi, consumer apps | 1 neutralna + 3 zasićene, bez senki, 24px radius, kartice koje se ljušte, kosi prelazi, maskote |
| C4 | **Pastel editorial** | Wembi | industrijski AI, wellness, premium consumer | bledo roza/siva baza, lime/lilac akcent, 3D pastel renderi, naslov između hairline linija, highlight-swipe |
| C5 | **Mirni svetli SaaS** | Butter, Cerebrium (svetle sekcije) | product/SaaS, alati | near-white, regular težina 56–64px, blur-in reči, proizvod UI koji izlazi van ivice, pinovana lista feature-a + živi widget |
| C6 | **Crni luksuz** | Moto, Jesper, Gil, Pacôme | luksuz, portfolio, premium usluge | #050505, hrom/bela, 1 proizvod u centru, skoro bez teksta, UI u 4 ugla, pilule |
| C7 | **Tamna infrastruktura + 1 akcenat** | Cerebrium hero/secure, DeepBook | dev tools, infra, crypto | tamno plava/crna, magenta ili električno plava samo na 1 reč + CTA, mono labele, number scramble |
| C8 | **Tematski svet (retro/period)** | Shader (80-te), Santioni (ilustrovani) | brendovi sa pričom, restorani, pića, kreativne agencije | serif + grain + period fotografija + prelazi sa fizičkom metaforom (page curl) |

Pravilo iz dataseta: **koncept se bira po industriji + brend assets-ima klijenta**, a korisniku se ponude 3 (C1/C5/C7 za SportBot, na primer). To je i prvi "wow" momenat proizvoda — pre swarma.

## 3. Tipografski sistem (brojevi, izmereni)

- Display: 56–140px desktop, **line-height 0.8–1.05**, tracking −0.02…−0.05em. Težina: ili vrlo lagana (300, Cerebrium 74px) ili bold uppercase (Maxima 56/0.80) — ne 600 "web bold".
- Body: 16–18px/1.3–1.5; "veliki body" 24–28px (Wembi) kad je teksta malo.
- Labele: **mono 10–13px uppercase** u 9 od 16 sajtova (Heron ×83 instanci, Cerebrium ×25). Ovo je jedan potez koji odmah daje "tech credibility".
- Kontrast display:body ≥ 4×.
- Fontovi viđeni: BT Grotesk, Suisse Intl (+Mono), ABC Favorit, ABC Diatype Rounded, Robuck Rounded, Indivisible, Geist Mono. **Nijedan Inter.**
- Broj reči: 81 (Pacôme) – 846 (Cerebrium). SportBot: ~3.000. Pravilo: ≤ 800 reči, hero ≤ 12.

## 4. Komponente koje se ponavljaju (biblioteka sekcija — ovo su "viralni formati")

1. **Hero sa pravim artefaktom** (proizvod UI / 3D objekat / fotografija proizvoda), ne mockup u telefonu — 14/16.
2. **Pinovana lista + živi widget** (Cerebrium) — aktivna stavka se boji dok skroluješ, desno se menja demo.
3. **Big-number ćelije** (Aspen "500+", Sharplink "895,117", DeepBook stat tiles sa scramble).
4. **Hotspot pilule na slici** (ICOMAT "10× FASTER ⊕", Moto "Jet Booked ✓").
5. **Pre/posle paneli** sa mono labelom i corner markerima (ICOMAT).
6. **Horizontalni numerisani proces 01–07** (ICOMAT) / numerisana poglavlja (Wembi, Aspen).
7. **Ledger / tabela kao dizajn** (Aspen klijenti, Sharplink FAQ redovi sa ■ 05 i + kvadratom).
8. **Card-deck peel** (Maxima) i **kosi prelazi sekcija**.
9. **Logo marquee** pod hairline-om (Cerebrium, Butter).
10. **Nav**: ili 4 ugla (Jesper/Gil), ili plutajuća pilula (Butter, DeepBook), ili **pilule na dnu** (Wembi) — nikad klasičan meni sa 8 linkova.
11. **Footer = brend momenat**: džinovski wordmark odsečen na dnu (DeepBook, Aspen, Sharplink sa kotama, Heron outline, Maxima sa maskotama) + jedan pokazivač napred ("Next stop").
12. **Data kartica**: tamni panel, mono labele, grafik, full-width dugme sa odvojenom strelicom (Sharplink, DeepBook mobile).

## 5. Motion rečnik (15 poteza, svi viđeni, svi izvodljivi u GSAP + Lenis)

1. masked line reveal (Aspen) 2. word blur-in (Butter) 3. letter-by-letter (Sharplink) 4. highlight swipe (Wembi) 5. text scrub — boja prati scroll (Wembi, ICOMAT) 6. number scramble/count (DeepBook) 7. pinned step story (Heron, Cerebrium) 8. pinned image zoom/dolly (Illoca) 9. card-deck peel (Maxima) 10. draw-on-scroll SVG (Heron tlocrt) 11. marquee 12. page-curl / circular mask prelaz (Shader, Moto) 13. rotating headline carousel (DeepBook) 14. hover scramble / cursor tooltip (Signal-A, Pacôme) 15. split headline koji propušta UI (Santioni).

Tehnički stack u 12/16: **GSAP + ScrollTrigger + Lenis**, često Webflow ili Next/Nuxt. Nema magije — isti alati.

## 6. Mobilni (nije naknadna misao)

- Grid koncepti kolabiraju u **jednu kolonu ćelija** (Aspen) — koncept preživi.
- Pinovane liste postaju običan stack, widgeti full-width (Cerebrium).
- Hero naslov se pomera: ICOMAT ga diže na vrh, tvrdnja ide dole.
- Nav → logo | CTA | Menu, ili pilule na dnu (Wembi) — to je **mobile-first obrazac koji i na desktopu izgleda moderno**.
- Motion ostaje (blur-in, scrub), 3D se zamenjuje statikom ili ostaje kao pozadina.
- Dugme full-width sa odvojenom ćelijom za strelicu (DeepBook).
→ Pravilo za engine: svaki koncept ima mobilnu varijantu definisanu unapred, ne "responsive fallback".

## 7. Šta ovo znači za SportBot (test slučaj)

Najbolji fit je **C1 Tehnički crtež** (data/ledger proizvod, "source-labelled", "public record" — to je jezik preciznosti) sa elementima C7 (tamna infrastruktura, zelena samo na 1 reč + CTA). Hero artefakt: pravi ledger / price-compare tabela kao data kartica. Beats: 6 sekcija umesto 15. Motion: number scramble na rekordu, text scrub na manifestu, pinovana lista "Three ways in" sa živim widgetom. Kraj: džinovski SPORTBOT wordmark sa kotama + "Next: today's picks".

## 8. Šta sistem NE može (iskreno)

- Custom 3D (Spyker, Cerebrium sfera, Moto kartica) i ručnu ilustraciju (Illoca, Santioni). Zamena: 2-bojna generisana ilustracija + grain (Illoca princip) ili klijentove fotografije sa tretmanom (halftone, duotone).
- Sajt bez sadržaja: ako klijent nema pravi proizvod/fotografije/brojeve, nema hero artefakta → sistem mora to da traži od korisnika u onboardingu (upload 3 fotke + logo + 3 broja).

## 9. Sledeći korak koji ima smisla

Ne još ekstrakcije. **Kodirati biblioteku**: 8 koncepata kao design tokens (boje, fontovi, spacing, tekstura) + 12 komponenti kao HTML/CSS šabloni sa koncept-varijantama + 15 motion poteza u GSAP-u. Onda SportBot v2 po C1 — i tek tada poređenje sa prvim demom pokazuje da li sistem radi.
