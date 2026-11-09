# Binnenkomtaken rekenen – instructies voor Claude

Deze repository maakt dagelijkse rekenstrookjes ("binnenkomtaken") voor groep 3 t/m 8 en publiceert ze op een
site (GitHub Pages, map `docs/`). Eigenaar: Joep, rekencoördinator. Collega's gebruiken de site om per week een
werkblad te printen en op het digibord na te kijken. Schrijf en antwoord in het Nederlands.

## Weeknummers
Op de bladen, in de bestandsnamen en op de site staan de **weeknummers van de kalender** (bijv. week 46), zoals in de
agenda van school. Intern telt de generator **lesweken 1–40** (die bepalen het jaarplan en de willekeur). De koppeling
lesweek → kalenderweek komt uit `instellingen.json` (eerste schooldag, vakanties, week zonder blad). In `PLAN` en in
`INTRO` gaat het dus over lesweken; in `INTRO` schrijf je weken als `{w:8}` of `{W:33-40}`, die worden ingevuld als
"week 44" / "Week 20–27". Gebruikt Joep een weeknummer ("week 48"), dan bedoelt hij de kalenderweek.

## Opbouw
- `instellingen.json` – schooljaar, vakanties (regio Midden), vrije dagen, week zonder blad, versies per week.
- `generator/engine.py` – tekenhulpjes, algemene opdrachttypen, controle (`validate`), antwoordweergave, bouwen per week.
- `generator/groep3.py` … `groep8.py` – per groep: opdrachttypen (`TYPES`), jaarplan (`PLAN`) en uitleg (`INTRO`).
  - `PLAN`: 20 regels van 2 weken: `((van, tot), "thema", [focus-typen], [herhaling-typen])`.
  - Elke strook = 10 opdrachten: 7 verdeeld over de focus-typen, 3 uit de herhaling (bij minder herhaling-typen meer focus).
  - Een opdrachttype is een functie `g(rng) -> Item`. Gebruik `sum_item` voor sommen (wordt automatisch nagerekend),
    `text_item` voor opdrachten met eenheden, of een eigen `Item(key, answer, draw, ...)`.
- `generator/bouw.py` – bouwt PDF's, antwoordstroken (PNG) en de gegevens voor de site.
- `docs/` – de site: `index.html`, `app.js`, `style.css`, `data/` (kalender en groepsgegevens) en `groepN/` (per week
  `weekNN.pdf`, `weekNN-antwoorden.pdf`, `weekNN-dag1..5.png`, `weekNN.json` met NN = kalenderweek, plus jaar-PDF's).

## Gouden regels
1. **Verander nooit weken die al geweest zijn of deze week aan de beurt zijn.** Die kunnen al geprint zijn; de
   antwoorden op het digibord moeten blijven kloppen. `bouw.py` beschermt die weken; gebruik `--forceer` alleen als
   Joep daar uitdrukkelijk om vraagt.
2. Elke week heeft eigen, vaste willekeur (`week_rng(groep, week, versie)`). Aanpassingen aan de ene week veranderen
   andere weken dus niet. Wil Joep voor één week nieuwe getallen: hoog `versies` in `instellingen.json` op.
3. **Altijd controleren:** `python generator/bouw.py --controle` moet voor alle groepen "in orde" geven (narekenen,
   bereik, opmaak, aantal antwoordvakjes). Bij problemen: oplossen, niet negeren.
4. **Altijd kijken:** render na een wijziging een paar pagina's (`pdftoppm -r 70 -png -f 1 -l 1 docs/groep5/week48.pdf /tmp/x`)
   en de bijbehorende antwoorden, en bekijk ze. Let op tekst die buiten vakjes valt en op onlogische sommen.
5. Ontbrekende tekens: het standaardlettertype heeft geen ² en ³ en geen pijlen. Gebruik `draw_txt` (zet ² ³ goed)
   en vermijd →, ↔, ⅓ enz. Breuken teken je met `draw_frac`.
6. Elke opdracht met meerdere invulvakjes krijgt `ans=[...]` (één tekst per vakje, in tekenvolgorde). Opdrachten
   zonder invulvak (omcirkelen, wijzers tekenen) krijgen `ans=[]` en een `ans_draw`. De controle meldt het als het
   aantal vakjes en antwoorden niet klopt.

## Veelvoorkomende verzoeken
- **"Alle bladen iets makkelijker" (of moeilijker):** pas de getalbereiken in de generatoren aan (bijv. kleinere
  getallen, geen overschrijding) of verschuif focus naar eenvoudigere typen in `PLAN`. Bouw daarna vanaf de volgende
  lesweek: `python generator/bouw.py --groep alle --vanaf volgende`.
- **"Meer tafels":** voeg het tafeltype (`alletafels`, `tafel6789`, …) toe aan de herhaling (of focus) in `PLAN` van
  de betreffende weken, of maak een nieuw type met `mk_tafel_h([...])`.
- **"Groep 5 week 48 vond ik te moeilijk":** pas alleen die week aan (eigen PLAN-regel, of de versie van die lesweek
  ophogen in `instellingen.json`) en bouw `--groep 5 --week 48` (als die week nog niet geweest is).
  `--week` en `--vanaf` gebruiken het weeknummer van de kalender; `versies` en `PLAN` gebruiken de lesweek.
- **Studiedag of andere vakantie:** pas `instellingen.json` aan en draai `python generator/bouw.py --kalender`.
  Er moeten precies 40 lesweken met blad overblijven (pas `weken_zonder_blad` aan). Verschuift daardoor het
  weeknummer van toekomstige weken, dan bouwt `python generator/bouw.py` die vanzelf opnieuw.
- **Nieuw schooljaar:** nieuwe vakanties in `instellingen.json`, versies leegmaken, dan alles opnieuw bouwen met
  `python generator/bouw.py --vanaf 1 --forceer` (alleen vóór de start van het schooljaar).

## Werkwijze bij een aanpassing
1. Lees wat Joep wil en vat in één zin samen welke weken en groepen veranderen (alleen toekomstige weken).
2. Pas de code/het plan aan.
3. `python generator/bouw.py --controle` → moet in orde zijn.
4. Bouw: `python generator/bouw.py --groep … --vanaf volgende` (of specifieker).
5. Bekijk een paar gerenderde pagina's, ook de antwoorden.
6. Noteer de wijziging kort in `WIJZIGINGEN.md` (datum, wat, welke weken).
7. Commit met een duidelijke Nederlandse boodschap en push naar `main`. De site werkt zich binnen een paar minuten bij.

## Benodigd
Python 3 met `reportlab`, `pypdf`, `Pillow`; `pdftoppm` (poppler-utils). Installeren: `pip install reportlab pypdf pillow`.
