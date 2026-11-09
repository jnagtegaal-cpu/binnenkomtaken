"""Bouwt de binnenkomtaken en de gegevens voor de site.

Gebruik (vanuit de hoofdmap van de repository):

  python generator/bouw.py --controle
      Controleert alle groepen en alle weken (sommen narekenen, opmaak, antwoordvakjes) zonder iets te schrijven.

  python generator/bouw.py
      Bouwt weken die nog niet bestaan, vernieuwt de kalender, de jaar-PDF's en de gegevens voor de site.
      Bestaande weken blijven ongewijzigd.

  python generator/bouw.py --groep 5 --vanaf 48
      Bouwt groep 5 opnieuw vanaf week 48 (weeknummer van de kalender); eerdere weken blijven zoals ze zijn.

  python generator/bouw.py --groep 5 --week 48
      Bouwt alleen groep 5 week 48 opnieuw.

  python generator/bouw.py --groep alle --vanaf volgende
      Bouwt alle groepen opnieuw vanaf de volgende lesweek (de veilige standaard na een aanpassing).

  python generator/bouw.py --kalender
      Vernieuwt alleen de kalender (na het wijzigen van instellingen.json).

Weken die al geweest zijn of deze week aan de beurt zijn, kunnen al geprint zijn. Die worden alleen
opnieuw gebouwd met --forceer. Zo kloppen de antwoorden op het digibord altijd met de geprinte bladen.
"""
import argparse, datetime as dt, importlib, json, os, shutil, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HIER)
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, HIER)

import engine  # noqa: E402

GROEPEN = {
    3: dict(maxv=100, minsize=11.5),
    4: dict(maxv=100, minsize=11.5),
    5: dict(maxv=1000, minsize=11.5),
    6: dict(maxv=100000, minsize=10.5),
    7: dict(maxv=1000000, minsize=10.5),
    8: dict(maxv=1000000, minsize=10.5),
}


def lees_instellingen():
    with open(os.path.join(ROOT, "instellingen.json"), encoding="utf-8") as f:
        return json.load(f)


def d(s):
    return dt.date.fromisoformat(s)


# ------------------------------------------------------------------ kalender

def maak_kalender(inst):
    """Alle schoolweken met hun lesweeknummer, vakanties en vrije dagen."""
    start, eind = d(inst["eerste_schooldag"]), d(inst["laatste_schooldag"])
    vak = [(d(v["van"]), d(v["tot"]), v["naam"]) for v in inst["vakanties"]]
    vrij = [(d(v["datum"]), v["naam"]) for v in inst.get("vrije_dagen", [])]
    zonder = {d(s) for s in inst.get("weken_zonder_blad", [])}
    maandag = start - dt.timedelta(days=start.weekday())
    weken, lw = [], 0
    while maandag <= eind:
        vrijdag = maandag + dt.timedelta(days=4)
        lesdagen = [maandag + dt.timedelta(days=i) for i in range(5)
                    if start <= maandag + dt.timedelta(days=i) <= eind
                    and not any(a <= maandag + dt.timedelta(days=i) <= b for a, b, _ in vak)]
        vakantie = next((n for a, b, n in vak if a <= maandag and vrijdag <= b), None)
        w = {"maandag": maandag.isoformat(), "vrijdag": vrijdag.isoformat(), "kw": maandag.isocalendar()[1]}
        if vakantie or not lesdagen:
            w.update(soort="vakantie", naam=vakantie or "Geen lesdagen")
        elif maandag in zonder:
            w.update(soort="geen blad", naam="Geen binnenkomtaak deze week")
        else:
            lw += 1
            w.update(soort="les", lesweek=lw)
        vd = [{"datum": x.isoformat(), "naam": n} for x, n in vrij if maandag <= x <= vrijdag]
        if vd:
            w["vrije_dagen"] = vd
        weken.append(w)
        maandag += dt.timedelta(days=7)
    if lw != 40:
        raise SystemExit(f"Let op: de kalender heeft {lw} lesweken met een blad, maar er zijn 40 weekbladen. "
                         f"Pas 'weken_zonder_blad' in instellingen.json aan.")
    return {"school": inst.get("schoolnaam", ""), "schooljaar": inst["schooljaar"], "regio": inst["regio"], "weken": weken}


def labels_van(kal):
    """lesweek -> kalenderweek (het nummer dat op de bladen en de site staat)."""
    return {w["lesweek"]: w["kw"] for w in kal["weken"] if w.get("lesweek")}


def maak_intro(intro, labels):
    """Vult {w:8} / {W:33-40} in met kalenderweken: 'week 44' / 'Week 20–27'."""
    import re
    def rep(m):
        a = int(m.group(2)); b = int(m.group(3)) if m.group(3) else None
        tekst = ("week " if m.group(1) == "w" else "Week ") + (str(labels[a]) if b is None else f"{labels[a]}–{labels[b]}")
        return tekst
    return re.sub(r"\{([wW]):(\d+)(?:-(\d+))?\}", rep, intro)


def huidige_lesweek(kal, vandaag=None):
    """De lesweek van vandaag; in een vakantie of weekend daarna: de eerstvolgende lesweek."""
    vandaag = vandaag or dt.date.today()
    for w in kal["weken"]:
        zondag = d(w["maandag"]) + dt.timedelta(days=6)
        if w.get("lesweek") and vandaag <= zondag:
            return w["lesweek"]
    return 41


# ------------------------------------------------------------------ bouwen

def laad_groep(g):
    m = importlib.import_module(f"groep{g}")
    return m.PLAN, m.TYPES, m.INTRO


def stel_in(g):
    engine.MAXV[0] = GROEPEN[g]["maxv"]
    engine.MINSIZE[0] = GROEPEN[g]["minsize"]


def controleer(groepen):
    """Genereert alles in het geheugen en tekent zowel leerling- als antwoordversie; schrijft niets weg."""
    from reportlab.pdfgen import canvas
    inst = lees_instellingen()
    labels = labels_van(maak_kalender(inst))
    totaal = 0
    for g in groepen:
        stel_in(g)
        plan, types, intro = laad_groep(g)
        start = len(engine.PROBLEMS)
        c = canvas.Canvas(os.devnull)
        for week in range(1, 41):
            versie = int(inst.get("versies", {}).get(str(g), {}).get(str(week), 1))
            rng = engine.week_rng(f"Groep {g}", week, versie)
            for dag in range(5):
                items = engine.strip_items(rng, plan, types, week)
                engine.draw_strip(c, 0, labels[week], engine.DAYS[dag], f"Groep {g}", plan_titel(plan, week), items, answers=False)
                engine.draw_strip(c, 0, labels[week], engine.DAYS[dag], f"Groep {g}", plan_titel(plan, week), items, answers=True)
                totaal += len(items)
        try:
            engine.overview(c, f"Groep {g}", plan, types, maak_intro(intro, labels), labels)
        except KeyError as e:
            engine.PROBLEMS.append(f"groep {g}: onbekende week in INTRO: {e}")
        nieuw = engine.PROBLEMS[start:]
        print(f"groep {g}: {'in orde' if not nieuw else f'{len(nieuw)} problemen'}")
        for p in nieuw[:20]:
            print("   ", p)
    print(f"{totaal} opdrachten gecontroleerd.")
    return not engine.PROBLEMS


def plan_titel(plan, week):
    return engine.plan_for(plan, week)[0]


def bestaande_weken(g):
    """lesweek -> kalenderweek van de weken die al gebouwd zijn (uit de weekNN.json-bestanden)."""
    map_ = os.path.join(DOCS, f"groep{g}")
    uit = {}
    if os.path.isdir(map_):
        for f in os.listdir(map_):
            if f.startswith("week") and f.endswith(".json"):
                with open(os.path.join(map_, f), encoding="utf-8") as fh:
                    m = json.load(fh)
                if f == f"week{m.get('kalenderweek', m['week']):02d}.json":
                    uit[m["week"]] = m.get("kalenderweek", m["week"])
    return uit


def ruim_op(g, labels):
    """Verwijdert weekbestanden waarvan het nummer niet (meer) bij een lesweek hoort."""
    import re
    map_ = os.path.join(DOCS, f"groep{g}")
    geldig = {f"{kw:02d}" for kw in labels.values()}
    for f in os.listdir(map_):
        m = re.match(r"week(\d\d)", f)
        if m and m.group(1) not in geldig:
            os.remove(os.path.join(map_, f))


def bouw_groep(g, weken, inst, labels):
    """Bouwt de opgegeven weken in een tijdelijke map; pas als alles klopt, worden de bestanden overgezet."""
    stel_in(g)
    plan, types, intro = laad_groep(g)
    intro = maak_intro(intro, labels)
    doel = os.path.join(DOCS, f"groep{g}")
    os.makedirs(doel, exist_ok=True)
    start = len(engine.PROBLEMS)
    with tempfile.TemporaryDirectory() as tmp:
        for week in weken:
            versie = int(inst.get("versies", {}).get(str(g), {}).get(str(week), 1))
            engine.build_week(tmp, f"Groep {g}", plan, types, week, versie, labels[week])
        if len(engine.PROBLEMS) > start:
            print(f"groep {g}: NIET opgeslagen, er zijn problemen:")
            for p in engine.PROBLEMS[start:start + 20]:
                print("   ", p)
            return False
        for f in os.listdir(tmp):
            shutil.copy(os.path.join(tmp, f), os.path.join(doel, f))
    ruim_op(g, labels)
    engine.build_year_pdfs(doel, f"Groep {g}", plan, types, intro, f"groep{g}", labels)
    if weken:
        print(f"groep {g}: {len(weken)} weken gebouwd (week {labels[weken[0]]} t/m {labels[weken[-1]]})")
    return True


def schrijf_sitegegevens(groepen_alle, labels):
    """docs/data/groepN.json: per week thema, bestanden en antwoorden; plus raster van de antwoordstroken."""
    from reportlab.lib.units import mm
    raster = {  # positie van het 2×5-raster binnen een strook (fracties van breedte/hoogte)
        "links": engine.MX / engine.W, "rechts": 1 - engine.MX / engine.W,
        "boven": 11 * mm / engine.STRIP_H, "onder": 1 - 4 * mm / engine.STRIP_H,
    }
    overzicht = []
    for g in groepen_alle:
        plan, types, intro = laad_groep(g)
        weken = []
        for week in range(1, 41):
            p = os.path.join(DOCS, f"groep{g}", f"week{labels[week]:02d}.json")
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                meta = json.load(f)
            if meta["week"] != week:
                continue
            weken.append({
                "week": week, "kw": labels[week], "thema": meta["thema"],
                "focus": [types[t][1] for t in engine.plan_for(plan, week)[1]],
                "dagen": [x["antwoorden"] for x in meta["dagen"]],
            })
        data = {"groep": g, "raster": raster, "weken": weken}
        with open(os.path.join(DOCS, "data", f"groep{g}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        overzicht.append({"groep": g, "weken": len(weken)})
    return overzicht


def lesweek_van(n, labels):
    """--week en --vanaf gaan over het weeknummer van de kalender (bijv. 46)."""
    for lw, kw in labels.items():
        if kw == n:
            return lw
    raise SystemExit(f"Week {n} is geen schoolweek met een blad. Kies een weeknummer uit de kalender.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groep", default="alle", help="3 t/m 8, of 'alle'")
    ap.add_argument("--vanaf", help="weeknummer van de kalender (bijv. 48) of 'volgende'")
    ap.add_argument("--week", type=int, help="alleen deze week (weeknummer van de kalender, bijv. 48)")
    ap.add_argument("--forceer", action="store_true", help="ook weken bouwen die al geweest zijn of nu aan de beurt zijn")
    ap.add_argument("--controle", action="store_true", help="alleen controleren, niets schrijven")
    ap.add_argument("--kalender", action="store_true", help="alleen de kalender vernieuwen")
    a = ap.parse_args()

    groepen = list(GROEPEN) if a.groep == "alle" else [int(a.groep)]
    if a.controle:
        sys.exit(0 if controleer(groepen) else 1)

    inst = lees_instellingen()
    kal = maak_kalender(inst)
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    with open(os.path.join(DOCS, "data", "kalender.json"), "w", encoding="utf-8") as f:
        json.dump(kal, f, ensure_ascii=False, indent=1)
    if a.kalender:
        print("kalender bijgewerkt"); return

    nu = huidige_lesweek(kal)
    labels = labels_van(kal)
    beschermd_tot = nu  # weken t/m deze week kunnen al geprint zijn
    ok = True
    for g in groepen:
        oud = bestaande_weken(g)
        # bestaand = gebouwd én nog met het juiste kalenderweeknummer
        bestaand = {w for w, kw in oud.items() if labels.get(w) == kw}
        verschoven = sorted(w for w, kw in oud.items() if labels.get(w) != kw)
        if a.week:
            weken = [lesweek_van(a.week, labels)]
        elif a.vanaf:
            v = nu + 1 if a.vanaf == "volgende" else lesweek_van(int(a.vanaf), labels)
            weken = list(range(v, 41))
        else:
            weken = [w for w in range(1, 41) if w not in bestaand]
        if verschoven:
            print(f"groep {g}: kalender veranderd, weeknummer opnieuw voor lesweek {', '.join(map(str, verschoven))}")
        geblokt = [w for w in weken if w in bestaand and w <= beschermd_tot and not a.forceer]
        if geblokt:
            print(f"groep {g}: week {', '.join(map(str, geblokt))} overgeslagen (al geweest of deze week; "
                  f"gebruik --forceer als je zeker weet dat die nog niet geprint is)")
        weken = [w for w in weken if w not in geblokt]
        weken = sorted(set(weken))
        if weken or not bestaand:
            ok &= bouw_groep(g, weken, inst, labels)
    schrijf_sitegegevens(list(GROEPEN), labels)
    print(f"deze week: week {labels.get(nu, '?')} (lesweek {nu})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
