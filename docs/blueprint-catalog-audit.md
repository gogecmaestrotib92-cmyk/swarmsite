# Audit blueprint kataloga i postupak za nove reference

Stanje zatečeno 8. novembra 2026. Ovaj dokument je inventar i predlog postupka, a ne potvrda da svaki blueprint verno reprodukuje referencu ili da su svi testirani na mobilnom uređaju.

## Šta je trenutno aktivno

`lib/blueprints/*.bp.json` sadrži 12 blueprinta koje direktor može da odabere. Kategorije u tabeli su interne klase aplikacije, ne nužno kategorije koje je originalnom sajtu dodelio Awwwards. Izvorni URL pokazuje odakle potiče postojeći zapis; nije dokaz da je sajt trenutno dostupan, da je nagrađen ili da su njegova sredstva licencirana za isporuku.

| Blueprint | Klasa / arhetip u fajlu | Izvor naveden u katalogu | Raw zapis |
| --- | --- | --- | --- |
| aino | service / index-grid | [aino.agency](https://aino.agency/) | Da |
| atelier | service / studio-grid-26 | Originalni interni koncept, bez navedenog sajta | Ne |
| belgrade-arbor | place / real-estate-cinematic | [Belgrade Arbor](https://belgradearbor.rs/en) | Da |
| butter | software / editorial-product-story | [Butter](https://www.butter.video/) | Da |
| cerebrium | software / dark-light-bands | [Cerebrium](https://cerebrium.ai/) | Da |
| crav | product / loud-brand-poster | [Crav](https://www.cravburgers.shop/) | Da |
| deepbook | software / dark-mono-sans | [DeepBook](https://deepbook.tech/) | Da |
| halfdays | product / apparel-shop-grid | [Halfdays](https://www.halfdays.com/) | Da |
| lpas | service / studio-grid-26 | [LPAS](https://lpas.com/) | Da |
| tengile | place / editorial-lodge | [Tengile](https://tengilemalamala.com/) | Da |
| units | place / coliving-pastel-cards | [Units](https://units.gr/en/homepage/) | Da |
| white-desert | place / cinematic-travel | [White Desert](https://white-desert.com/) | Da |

Raspodela je 4 `place`, 3 `service`, 3 `software` i 2 `product`. To ne obezbeđuje ravnomernu pokrivenost restorana, klinika, advokata, hotela, e-commerce-a, SaaS-a ili drugih podindustrija; nekoliko veoma različitih delatnosti trenutno deli istu internu klasu. Sam broj blueprinta nije dokaz dobrog izbora za svaku delatnost.

## Kvalitet postojećih merenja

- Za 11 od 12 blueprinta postoji `lib/blueprints/raw/<id>.json`; `atelier` je autorski interni koncept bez raw merenja. To što raw fajl postoji ne potvrđuje da su svaka vrednost i svaka sekcija izmerene, potpune ili i danas tačne: pojedina polja i uloge su naknadno anotirana.
- `aino`, `butter` i `cerebrium` u raw zapisu eksplicitno imaju `vw: 1440`; ostalih osam raw fajlova ne beleži širinu viewporta. Svi raw zapisi navode `vh: 756`. `normalize.py` za nedostajući `vw` pretpostavlja 1440, što nije dokaz originalne širine. Novija izmena extractora ne dopunjava retroaktivno te postojeće fajlove.
- U postojećim raw JSON-ovima ne postoji poseban strukturisani skup mobilnih merenja. DNA izveštaji opisuju i mobilna opažanja, ali se iz raw blueprint formata ne može dokazati upareno merenje desktop/mobilni ni da je renderer proverio sve reference na oba formata.
- Trenutni `extract.js` obrađuje maksimalno prvih 16 pronađenih blokova, uz ograničen broj naslova, medija i drugih elemenata po bloku. Rezultat zavisi od vidljivosti, učitavanja, animacija, strukture DOM-a i aktivnog viewporta; custom canvas/WebGL i interakcije ne mogu se pouzdano rekonstruisati samo iz DOM merenja. Izmena extractora koja je trenutno u radu zapisuje i `vw` i `vh`, a `pageH` ponovo meri nakon prolaska kroz stranicu. To ne garantuje da je scroll pass obuhvatio sav naknadno učitan sadržaj, niti menja stare raw fajlove.
- `normalize.py` pored merenja koristi heuristike i podrazumevane vrednosti: npr. bira najveći naslov za display, izvodi ostale tipografske uloge i upisuje podrazumevano dugme ili motion vrednosti kad nema odgovarajućih podataka. Takve vrednosti treba označiti kao izvedene/pretpostavljene, ne kao direktno izmerene.
- `render_bp.py` koristi normalizovane vrednosti, ali bira postojeće komponente i recipe slotove prema vrsti sadržaja, slikama i ograničenjima komponente. Nije opšti rekonstruktor izvornog sajta: redosled, oblici, sekcije, fontovi i pokret mogu se razlikovati. Zbog toga je potreban pregled stvarnog izlaza, a ne samo validacija JSON-a.

## DNA je zasebna istraživačka kolekcija

`dna/` sadrži 16 direktorijuma sa `data.json` profilima i 211 JPG fajlova koji su trenutno praćeni u Gitu. Tri imena — Butter, Cerebrium i DeepBook — preklapaju se sa aktivnim blueprintima. Ostali profili predstavljaju odvojena istraživačka opažanja; nisu automatski aktivni blueprinti. Izveštaji u `dna/` daju korisne hipoteze o kompoziciji i pokretu, ali opšta pravila poput ograničavanja celog landinga na određeni broj reči ili sekcija ne smeju izazvati gubitak važnog sadržaja klijenta.

Normalizovani `.bp.json` uglavnom čuva strukturu i vizuelne parametre. Međutim, raw JSON-ovi sadrže i isečke originalnih naslova i oznaka dugmadi, a `dna/` sadrži slike referenci. Dakle, nije tačno da u celom repozitorijumu nema originalnog sadržaja. Ovaj audit ne utvrđuje da li su ti fajlovi dostupni preko javnog servera niti rešava pravo njihovog čuvanja; pre daljeg deljenja treba proveriti uslove i dozvole.

## Gde tražiti nove kandidate

Awwwards ima odvojene filtere za kategoriju, nagradu, oznake i tehnologiju; kandidata treba proveriti na njegovoj pojedinačnoj stranici. Uvrštenje u galeriju nije samo po sebi dokaz da je sajt dobio Site of the Day. Posebno voditi računa o promovisanom sadržaju i o dostupnosti originalnog sajta.

- **SaaS, alati i B2B:** [Technology](https://www.awwwards.com/websites/technology/), [Startups](https://www.awwwards.com/websites/startups/), [Mobile & Apps](https://www.awwwards.com/websites/mobile-apps/) i [SaaS rezultati](https://www.awwwards.com/websites/saas/).
- **Restorani, kafići i hoteli:** [Hotel / Restaurant](https://www.awwwards.com/websites/restaurant/) i [Food & Drink](https://www.awwwards.com/websites/food-drink/).
- **Agencije i profesionalne usluge:** [Design Agencies](https://www.awwwards.com/websites/design-agencies/) i [Business & Corporate](https://www.awwwards.com/websites/business-corporate/).
- **Trgovina i arhitektura:** [E-Commerce](https://www.awwwards.com/websites/e-commerce/) i [Architecture](https://www.awwwards.com/websites/architecture/).

Kao prvi krug birati funkcionalne landing stranice koje imaju stvarni sadržaj, jasne CTA-ove i upotrebljivu mobilnu verziju, umesto oslanjanja samo na atraktivan hero ili nagradu. U svakoj ciljnoj kategoriji treba više različitih pristupa, npr. tipografski, foto i product-led, ali tek posle stvarne provere. Za klinike i druge specifične usluge pretražiti relevantne projekte i izvan širokih kategorija; ne pretpostavljati da u katalogu već postoji namenska kategorija.

## Provereni kandidati po kategoriji

Pregled u Chrome-u 8. novembra 2026: svih 12 stranica vratilo je HTTP 200, a svaka navedena Awwwards stranica sadrži direktan link ka odgovarajućem originalu. Kategorije ispod su radna klasifikacija za SwarmSite. Ovo su kandidati za istraživanje, ne aktivni blueprinti.

| Kategorija | Kandidat | Original | Awwwards |
| --- | --- | --- | --- |
| Software / SaaS | GrowthBook | [growthbook.io](https://www.growthbook.io/) | [GrowthBook](https://www.awwwards.com/sites/growthbook) |
| Software / AI | Wafer | [wafer.ai](https://www.wafer.ai/) | [Wafer.ai](https://www.awwwards.com/sites/wafer-ai) |
| Restoran | Délice | [delice.ca](https://delice.ca/) | [Délice](https://www.awwwards.com/sites/delice) |
| Restoran | Qissa | [qissa.co.uk](https://www.qissa.co.uk/) | [Qissa](https://www.awwwards.com/sites/qissa-a-tale-of-food) |
| Hotel / resort | Velaa | [velaaprivateisland.com](https://www.velaaprivateisland.com/) | [Velaa Private Island](https://www.awwwards.com/sites/velaa-private-island) |
| Kreativne usluge | Extrafazant | [extrafazant.nl](https://www.extrafazant.nl/) | [Extrafazant](https://www.awwwards.com/sites/extrafazant) |

Ovim su provereni dostupnost i veza između navedenih stranica, ne puna upotrebljivost, pristupačnost, kvalitet mobilnog prikaza, licence asseta, održivost animacija ili podobnost za renderer. Osim niže opisanih preliminarnih merenja GrowthBooka, dizajni nisu izmereni niti je proveren generisani izlaz; status nagrada nije predmet ove provere. Kandidati zahtevaju postupak promocije iz ovog dokumenta.

## Prvi kandidat: GrowthBook

[GrowthBook na Awwwards](https://www.awwwards.com/sites/growthbook) · [Originalni sajt](https://www.growthbook.io/) · predložena interna klasa: `software`. Ovo je kandidat za dalje istraživanje, ne aktivni blueprint. U nezavisnoj preliminarnoj browser proveri vidljivi H1 je 68 px na širini 1440 i 44 px na širini 390; jedan sadržajni H2 je 56 px odnosno 36 px. To nisu univerzalne veličine svih H2 na stranici: među vidljivim naslovima postoje i druge veličine, pa u budućem merenju treba beležiti konkretan element i ulogu.

Ova provera nije kompletan audit sekcija, interakcija ili mobilnog ponašanja. Pri ekstrakciji je zabeležen zaseban problem: prazan blok iz DOM-a preklapa drugu detektovanu sekciju, pa automatsku segmentaciju treba proveriti i ispraviti pre normalizacije. To nije `bpout`: on je pomoćni element koji extractor ubacuje u stranicu za prikaz JSON rezultata i može pomeriti ili zakloniti sadržaj pri naknadnom vizuelnom pregledu; ukloniti ga pre referentnih snimaka. Novija izmena extractora zapisuje `vw` i ponovo meri `pageH` posle scroll prolaska, ali sama po sebi ne rešava preklapanje blokova niti potvrđuje potpunost merenja. Kandidat ostaje u istraživanju i nije spreman za produkciju do postupka promocije ispod.

## Postupak od kandidata do aktivnog blueprinta

1. **Kandidat:** zabeležiti originalni URL, Awwwards URL ako postoji, vrstu sajta, stvarni status nagrade, datum pregleda, dostupnost i razlog izbora. Proveriti uslove korišćenja i poštovati ograničenja pristupa, `robots.txt` za automatizovani pristup i razumnu učestalost zahteva; ne zaobilaziti zaštitu, prijavu ni paywall. `robots.txt` sam po sebi nije licenca za sadržaj.
2. **Provera originala:** pregledati desktop i mobilni prikaz u stvarnom browseru, više sekcija i stanja, osnovne linkove i ključne interakcije. Posebno zabeležiti šta se menja pod `prefers-reduced-motion`, da li je bitan sadržaj čitljiv i kada nedostaju animacije, i da li je sajt previše zavisan od nedostupnog WebGL/canvas sadržaja.
3. **Merenje:** za svaku širinu posebno zabeležiti stvarnu širinu/visinu viewporta i DPR, datum, alat i verziju, sekcije i položaje, tipografiju, grid, boje, oblik medija, nav i dostupne interakcije. Razdvojiti izmerene vrednosti, ručne anotacije, pretpostavke i nepouzdana merenja. Ako alat ili animacija izostavi sekciju, sačuvati ograničenje umesto popunjavanja izmišljotinom.
4. **Prava i privatnost:** u korisničku isporuku ne unositi tuđe fotografije, ilustracije, logotipe, tekst, font-fajlove, video ni kod bez odgovarajuće dozvole/licence. Kao input koristiti klijentov sadržaj ili zasebno licencirane/originalno kreirane assete. Za reference po potrebi čuvati samo odobrene metapodatke i link; screenshot-ove i sirovi izvod držati prema utvrđenim pravima, ograničenjima pristupa i roku čuvanja, ne automatski javno. To je praktičan kontrolni postupak, ne pravni zaključak za sve jurisdikcije.
5. **Implementacija:** uvesti normalizovanu formu i eksplicitne recipe/komponente koje renderer zaista podržava, sa fallback-om za nedostajuće slike i duži sadržaj. Nijedna referenca ne daje dozvolu za gubitak korisnikovih tekstova, CTA-ova ili podstranica.
6. **Promocija tek nakon render provere:** izgenerisati najmanje dva različita realna ili reprezentativna sadržajna primera, uključujući jedan dugačak i jedan sa ograničenim assetima. Pregledati rezultat u Chrome-u na desktopu i telefonu, uz normalan i smanjeni pokret; proveriti sadržaj, akcije, kontrast, tastaturu, responsive overflow, neodsecanje slika i konzistentnost ritma. Mehanički contract je potreban, ali ne dokazuje estetsku sličnost. Sačuvati datum, uslove i rezultat poređenja sa referencom, zajedno sa poznatim ograničenjima; pre toga kandidat ostaje eksperiment, ne aktivni blueprint.

Orijentir za pristupačnost: [WCAG 2.2](https://www.w3.org/TR/WCAG22/) pokriva, između ostalog, kontrast, fokus, alternativne načine korišćenja i kretanje. Uspešan audit jedne verzije ne garantuje pristupačnost svih budućih generisanih stranica.
