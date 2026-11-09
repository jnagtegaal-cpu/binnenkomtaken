from engine import *


def g_add10(rng):
    a = rng.randint(1, 9); b = rng.randint(1, 10 - a)
    return sum_item(("a10", a, b), a + b, [f"{a} + {b} =", None])

def g_sub10(rng):
    a = rng.randint(2, 10); b = rng.randint(1, a - 1)
    return sum_item(("s10", a, b), a - b, [f"{a} – {b} =", None])

def g_addsub10(rng):
    return (g_add10 if rng.random() < 0.5 else g_sub10)(rng)

def g_tienplus(rng):
    e = rng.randint(1, 9); v = rng.choice([0, 1, 2])
    if v == 0:
        return sum_item(("tp0", e), 10 + e, ["10 + " + str(e) + " =", None])
    if v == 1:
        return sum_item(("tp1", e), e, [f"{10 + e} = 10 +", None])
    return sum_item(("tp2", e), e, [f"{10 + e} –", None, "= 10"])

def g_teen(rng):
    if rng.random() < 0.5:
        e = rng.randint(1, 8); b = rng.randint(1, 9 - e)
        return sum_item(("tn+", e, b), 10 + e + b, [f"{10 + e} + {b} =", None])
    e = rng.randint(2, 9); b = rng.randint(1, e)
    return sum_item(("tn-", e, b), 10 + e - b, [f"{10 + e} – {b} =", None])

def g_aanvul(rng):
    a = rng.randint(1, 9)
    return sum_item(("av", a), 10 - a, [f"{a} +", None, "= 10"])

def g_van10(rng):
    b = rng.randint(1, 9)
    return sum_item(("v10", b), 10 - b, [f"10 – {b} =", None])

def g_dubbel(rng):
    a = rng.randint(1, 10)
    return sum_item(("du", a), 2 * a, [f"{a} + {a} =", None])

def g_over10(rng):
    a = rng.randint(5, 9); b = rng.randint(11 - a, 9)
    if rng.random() < 0.5: a, b = b, a
    return sum_item(("o10", a, b), a + b, [f"{a} + {b} =", None])

def g_over10min(rng):
    t = rng.randint(11, 17); b = rng.randint(t - 9, 9)
    return sum_item(("o10m", t, b), t - b, [f"{t} – {b} =", None])


TYPES = {
    "dobbel": (g_dobbel, "dobbelsteenbeelden"),
    "2dob": (g_twodice, "twee dobbelstenen"),
    "tien10": (g_tien10, "tienbeeld tot 10"),
    "tien20": (g_tien20, "tienbeelden tot 20"),
    "dubbelbeeld": (g_dubbelbeeld, "dubbelbeelden"),
    "tel10": (mk_seq(0, 10, 1, "tel10"), "telrij tot 10"),
    "tel20": (mk_seq(0, 20, 1, "tel20"), "telrij tot 20"),
    "terug10": (mk_seq(0, 10, -1, "terug10", "terugtellen"), "terugtellen tot 10"),
    "terug20": (mk_seq(0, 20, -1, "terug20", "terugtellen"), "terugtellen tot 20"),
    "verg10": (mk_cmp(0, 10, "verg10"), "vergelijken tot 10"),
    "verg20": (mk_cmp(0, 20, "verg20"), "vergelijken tot 20"),
    "lijn10": (mk_lijn(0, 10, "lijn10"), "getallenlijn 0–10"),
    "lijn20": (mk_lijn(0, 20, "lijn20"), "getallenlijn 0–20"),
    "lijn1020": (mk_lijn(10, 20, "lijn1020"), "getallenlijn 10–20"),
    "spl10": (mk_splits([10], "spl10"), "splitsen van 10"),
    "splN": (mk_splits(list(range(4, 10)), "splN"), "splitsen tot 10"),
    "plus10": (g_add10, "optellen tot 10"),
    "min10": (g_sub10, "aftrekken tot 10"),
    "plusmin10": (g_addsub10, "+ en – tot 10"),
    "tienplus": (g_tienplus, "10 + 4 / 14 – ? = 10"),
    "teen": (g_teen, "15 + 3 / 18 – 3"),
    "aanvul": (g_aanvul, "aanvullen tot 10"),
    "van10": (g_van10, "10 – 4"),
    "dubbel": (g_dubbel, "dubbelsommen"),
    "over10": (g_over10, "+ over het tiental"),
    "over10min": (g_over10min, "– over het tiental"),
    "uur": (mk_clock("hour"), "hele uren"),
    "half": (mk_clock("half"), "halve uren"),
    "klokmix": (mk_clock("mix"), "hele en halve uren"),
}

PLAN = [
    ((1, 2),  "Aantallen en telrij tot 10",        ["dobbel", "tien10", "tel10", "verg10"], []),
    ((3, 4),  "Tellen tot 10 en verder",            ["dobbel", "tien10", "tel20", "terug10"], ["verg10"]),
    ((5, 6),  "Telrij tot 20, terugtellen",         ["tel20", "terug20", "verg20", "lijn10"], ["dobbel", "tien10"]),
    ((7, 8),  "Getallenlijn tot 20, vergelijken",   ["lijn20", "verg20", "terug20", "2dob"], ["dobbel", "tien10", "tel20"]),
    ((9, 10), "Tienbeelden en dubbelbeelden",       ["tien20", "dubbelbeeld", "lijn1020", "spl10"], ["tel20", "terug20", "dobbel"]),
    ((11, 12), "Splitsen van 10, hele uren",        ["spl10", "tien20", "uur", "dubbelbeeld"], ["lijn20", "verg20", "terug20"]),
    ((13, 14), "Splitsen van 10, klok",             ["spl10", "uur", "tien20", "lijn1020"], ["dubbelbeeld", "terug20", "verg20"]),
    ((15, 16), "Herhaling blok 3–4",                ["spl10", "uur", "tien20", "dubbelbeeld", "lijn20"], ["terug20", "2dob"]),
    ((17, 18), "Splitsen tot 10, optellen tot 10",  ["splN", "plus10", "spl10", "tienplus"], ["tien20", "uur", "lijn20"]),
    ((19, 20), "Optellen en aftrekken tot 10",      ["plus10", "min10", "splN", "tienplus"], ["spl10", "tien20", "uur"]),
    ((21, 22), "Tot 10 en tussen 10 en 20",         ["plusmin10", "teen", "tienplus", "half"], ["splN", "spl10", "lijn20"]),
    ((23, 24), "Herhaling blok 5–6",                ["plusmin10", "teen", "splN", "spl10", "klokmix"], ["tienplus", "dubbelbeeld"]),
    ((25, 26), "Aanvullen tot 10, aftrekken van 10", ["aanvul", "van10", "plus10", "min10"], ["teen", "splN", "klokmix"]),
    ((27, 28), "Aanvullen en splitsen vlot",        ["aanvul", "van10", "splN", "teen"], ["plusmin10", "spl10", "tienplus"]),
    ((29, 30), "Sommen tot 10 vlot",                ["plus10", "min10", "aanvul", "van10"], ["teen", "splN", "klokmix"]),
    ((31, 32), "Herhaling blok 7–8",                ["plusmin10", "aanvul", "van10", "splN", "spl10"], ["teen", "klokmix"]),
    ((33, 34), "Dubbelsommen (op weg naar groep 4)", ["dubbel", "plusmin10", "aanvul", "teen"], ["tienplus", "van10", "dubbelbeeld"]),
    ((35, 36), "Optellen over het tiental",         ["over10", "dubbel", "plusmin10", "aanvul"], ["teen", "splN", "klokmix"]),
    ((37, 38), "Over het tiental + herhaling",      ["over10", "over10min", "plusmin10", "teen"], ["dubbel", "aanvul", "van10"]),
    ((39, 40), "Jaarafsluiting: alles door elkaar", ["plusmin10", "aanvul", "van10", "teen", "over10"], ["dubbel", "splN"]),
]

INTRO = (
    "Eén pagina per schoolweek; bovenaan staat het <b>weeknummer van de kalender</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook heeft 10 opdrachten (± 5 minuten): "
    "ongeveer 7 over de focus van de week en 3 herhalingsopdrachten uit eerdere weken.<br/>"
    "Aansluiting op het Rekenmuurtje: blok 2 = {w:8}, blok 4 = {w:16}, blok 6 = {w:24}, blok 8 = {w:32}. "
    "{W:33-40} gaan verder dan de lijn: dubbelsommen en optellen/aftrekken over het tiental als opstap naar "
    "groep 4 blok 2 (6 + 8 en 14 – 8), steeds gemengd met herhaling. "
    "Bij de klok schrijven kinderen het uur in het vakje (bijv. <i>half</i> [4])."
)
