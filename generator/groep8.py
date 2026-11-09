from fractions import Fraction as F
from engine import *
from groep4 import g_tot20, g_over, g_met
from groep6 import (mk_tafel_h, mk_deel_h, g_deelsplits3, g_omtrekF, g_oppF, g_schatten, g_terug_groot,
                    g_tijdwoorden, mk_duur, twoline, _chart_axes)
from groep7 import (D, dfix, rdec, draw_frac, frac_w, with_check, g_kommaplus2, g_kommax10, g_proc_anker,
                    g_proc_1, g_omzetten, g_vereenvoudig, g_breukverg, g_vtabel, g_snelheid, g_samenhang,
                    g_lengte_alle, g_liter_alle, g_gewicht)


# ------------------------------------------------------------------ kommagetallen

def g_kommaxheel(rng):
    """Een kommagetal vermenigvuldigen met een heel getal: 3,5 × 4 / 0,25 × 6"""
    n = rng.randint(2, 9)
    pl = rng.choice([1, 1, 2])
    a = rdec(rng, 0.1, 12, pl)
    if a.denominator == 1: a += F(5, 10 ** pl)
    sa = D(a)
    if rng.random() < 0.3:
        return sum_item(("kh", n, sa), a * n, [f"{n} × {sa} =", WIDE])
    return sum_item(("kh", sa, n), a * n, [f"{sa} × {n} =", WIDE])


def g_kommadeelheel(rng):
    """Een kommagetal delen door een heel getal: 7,2 : 4 = 1,8"""
    n = rng.randint(2, 9)
    while True:
        q = rdec(rng, 0.2, 9.9, rng.choice([1, 1, 2]))
        a = q * n
        if q.denominator != 1 and a.denominator != 1:   # deeltal én uitkomst zijn kommagetallen
            break
    return sum_item(("kd", D(a), n), q, [f"{D(a)} : {n} =", WIDE])


# ------------------------------------------------------------------ procenten

def g_toeafname(rng):
    """Toe- en afname met makkelijke percentages."""
    p = rng.choice([10, 20, 25, 50, 5, 75])
    step = {10: 10, 20: 5, 25: 4, 50: 2, 5: 20, 75: 4}[p]
    v = rng.choice([0, 0, 1, 2])
    if v == 0:      # korting
        prijs = step * rng.randint(3, 30)
        if prijs < 20: prijs *= 5
        new = prijs - prijs * p // 100
        it = twoline(("ta0", p, prijs), new, f"€ {prijs}, {p}% korting", ["nu: €", WIDE if new >= 100 else None], 10)
        return with_check(it, lambda: (F(new) == F(prijs) * (1 - F(p, 100)), "korting"))
    if v == 1:      # duurder
        prijs = step * rng.randint(3, 30)
        if prijs < 20: prijs *= 5
        new = prijs + prijs * p // 100
        it = twoline(("ta1", p, prijs), new, f"€ {prijs}, {p}% duurder", ["nu: €", WIDE if new >= 100 else None], 10)
        return with_check(it, lambda: (F(new) == F(prijs) * (1 + F(p, 100)), "duurder"))
    aantal = step * rng.randint(5, 40)      # aantal neemt toe
    new = aantal + aantal * p // 100
    it = twoline(("ta2", p, aantal), new, f"{aantal} leden, {p}% erbij", ["nu:", WIDE if new >= 100 else None, "leden"], 10)
    return with_check(it, lambda: (F(new) == F(aantal) * (1 + F(p, 100)), "toename"))


# ------------------------------------------------------------------ breuken

def _frac_eq(c, x, y, ch, left_parts, ansbox=True, bw=BW):
    """Rij met breuken/tekst gevolgd door een invulvak, gecentreerd."""
    ws = []
    for p in left_parts:
        ws.append(frac_w(c, p[1], p[2], 12) if isinstance(p, tuple) else c.stringWidth(p, FONT, 13))
    gap = 1.3 * mm
    total = sum(ws) + gap * len(left_parts) + bw
    if total > CELL_W - 1.5 * mm:
        PROBLEMS.append(f"breukrij te breed: {left_parts}")
    cx = x + (CELL_W - total) / 2
    ym = y + ch / 2
    for p, w in zip(left_parts, ws):
        if isinstance(p, tuple):
            draw_frac(c, cx + w / 2, ym, p[1], p[2], 12)
        else:
            c.setFont(FONT, 13); c.setFillColor(black); c.drawString(cx, ym - 1.6 * mm, p)
        cx += w + gap
    box(c, cx, ym - 4.5 * mm, bw)


def g_heelxbreuk(rng):
    """Een heel getal vermenigvuldigen met een breuk: ¾ × 12 = 9"""
    from math import gcd
    dd = rng.choice([2, 3, 4, 5, 6, 8, 10])
    nn = rng.choice([v for v in range(1, dd) if gcd(v, dd) == 1])
    k = rng.randint(2, 12)
    whole = dd * k
    ans = nn * k
    if rng.random() < 0.5:
        parts = [("f", str(nn), str(dd)), f"× {whole} ="]
    else:
        parts = [f"{whole} ×", ("f", str(nn), str(dd)), "="]
    def d(c, x, y, ch):
        _frac_eq(c, x, y, ch, parts)
    it = Item(("hxb", nn, dd, whole, len(parts[0]) if isinstance(parts[0], str) else 0), ans, d)
    return with_check(it, lambda: (F(nn, dd) * whole == ans, "heel × breuk"))


def g_heeldeelbreuk(rng):
    """Een heel getal delen door een makkelijke breuk: 3 : ½ = 6"""
    dd = rng.choice([2, 2, 3, 4, 4, 5, 10])
    n = rng.randint(2, 12 if dd <= 4 else 6)
    ans = n * dd
    parts = [f"{n} :", ("f", "1", str(dd)), "="]
    def d(c, x, y, ch):
        _frac_eq(c, x, y, ch, parts, bw=BW if ans < 100 else WBW)
    it = Item(("hdb", n, dd), ans, d)
    return with_check(it, lambda: (F(n) / F(1, dd) == ans, "heel : breuk"))


# ------------------------------------------------------------------ verhoudingen vergelijken

def g_vergverh(rng):
    """Verhoudingen vergelijken: welke is voordeliger / welk deel is groter?"""
    if rng.random() < 0.5:
        while True:
            p1, p2 = F(rng.randint(5, 30), 10), F(rng.randint(5, 30), 10)   # prijs per stuk
            a1, a2 = rng.sample([2, 3, 4, 5, 6], 2)
            if p1 != p2 and abs(p1 - p2) <= F(1, 2) and (p1 * a1).denominator <= 10 and (p2 * a2).denominator <= 10:
                break
        t1, t2 = f"{a1} voor € {dfix(p1 * a1, 2)}", f"{a2} voor € {dfix(p2 * a2, 2)}"
        best = 0 if p1 < p2 else 1
        lab = "omcirkel de voordeligste"
        key = ("vv1", a1, p1, a2, p2)
        chk = lambda: ((p1 < p2) == (best == 0), "voordeligste")
    else:
        while True:
            n1, t1_ = rng.randint(3, 15), rng.choice([20, 25, 30])
            n2, t2_ = rng.randint(3, 15), rng.choice([20, 25, 30])
            f1, f2 = F(n1, t1_), F(n2, t2_)
            if f1 != f2 and t1_ != t2_ and abs(f1 - f2) <= F(1, 5) and f1 < 1 and f2 < 1:
                break
        t1, t2 = f"{n1} van de {t1_}", f"{n2} van de {t2_}"
        best = 0 if f1 > f2 else 1
        lab = "welke klas fietst vaker?"
        key = ("vv2", n1, t1_, n2, t2_)
        chk = lambda: ((f1 > f2) == (best == 0), "grootste deel")
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, lab)
        c.setFont(FONT, 9.5); c.setFillColor(black)
        c.drawString(x + 3 * mm, y + ch - 9.5 * mm, "A")
        c.drawString(x + 3 * mm, y + ch - 16.5 * mm, "B")
        c.drawString(x + 8 * mm, y + ch - 9.5 * mm, t1)
        c.drawString(x + 8 * mm, y + ch - 16.5 * mm, t2)
    def r(c, x, y, ch):
        answer_ring(c, x + 4.1 * mm, y + ch - (8.6 if best == 0 else 15.6) * mm, 5.4 * mm, 5.4 * mm)
    it = Item(key, best, d, ans=[], ans_draw=r, ans_text=("A" if best == 0 else "B") + " omcirkelen")
    return with_check(it, chk)


# ------------------------------------------------------------------ grafieken

def g_lijngrafiek8(rng):
    """Moeilijkere lijngrafiek: tussen de lijnen aflezen of het verschil uitrekenen."""
    s = rng.choice([10, 20, 50])
    smax = 4 * s
    days = ["ma", "di", "wo", "do", "vr"]
    vals = [rng.randint(0, 8) * s // 2 for _ in range(5)]
    while len(set(vals)) < 4:
        vals = [rng.randint(0, 8) * s // 2 for _ in range(5)]
    if rng.random() < 0.5:
        i = rng.randrange(5)
        if vals[i] % s == 0:
            vals[i] = vals[i] + s // 2 if vals[i] < smax else vals[i] - s // 2
        q, ans, mark = f"{days[i]} =", vals[i], [i]
    else:
        i, j = sorted(rng.sample(range(5), 2))
        if vals[i] == vals[j]:
            vals[j] = (vals[j] + s) % (smax + s // 2)
        q, ans, mark = f"{days[i]}–{days[j]}: verschil", abs(vals[i] - vals[j]), [i, j]
    def d(c, x, y, ch):
        x0, y0, wch, hch = x + 6.5 * mm, y + 3.6 * mm, 17.5 * mm, ch - 6.6 * mm
        _chart_axes(c, x0, y0, wch, hch, smax, s)
        pts = [(x0 + 1.6 * mm + k * 3.6 * mm, y0 + hch * v / smax) for k, v in enumerate(vals)]
        c.setStrokeColor(ACCENT); c.setLineWidth(1)
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            c.line(ax, ay, bx, by)
        for k, (px, py) in enumerate(pts):
            c.setFillColor(RED if k in mark else ACCENT); c.circle(px, py, 0.65 * mm, stroke=0, fill=1)
            c.setFillColor(black); c.setFont(FONT, 4.8); c.drawCentredString(px, y0 - 2.5 * mm, days[k])
        c.setFont(FONT, 7)
        c.drawCentredString(x + 30.5 * mm, y + ch / 2 + 2 * mm, q)
        box(c, x + 25 * mm, y + ch / 2 - 7.5 * mm, 11 * mm, BH)
    return Item(("lg8", s, tuple(vals), q), ans, d)


TYPES = {
    # herhaling
    "tot20": (g_tot20, "6 + 8 / 14 – 8"),
    "over": (g_over, "35 + 8 / 74 – 8"),
    "met": (g_met, "35 + 27 / 73 – 45"),
    "deelsplits3": (g_deelsplits3, "372 : 6 (splitsen)"),
    "alletafels": (mk_tafel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "tall"), "alle tafels door elkaar"),
    "alledeel": (mk_deel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "dall"), "alle deeltafels door elkaar"),
    "kommaplus2": (g_kommaplus2, "komma + en – (verschillend aantal decimalen)"),
    "kommax10": (g_kommax10, "kommagetal × 10, 100, 1000"),
    "proc_anker": (g_proc_anker, "procenten met ankerpunten"),
    "proc_1": (g_proc_1, "procenten met de 1%-regel"),
    "omzetten": (g_omzetten, "breuk, komma, procent omzetten"),
    "vereenvoudig": (g_vereenvoudig, "breuken vereenvoudigen"),
    "breukverg": (g_breukverg, "breuken vergelijken"),
    "vtabel": (g_vtabel, "verhoudingstabel"),
    "snelheid": (g_snelheid, "snelheid"),
    "samenhang": (g_samenhang, "samenhang maten"),
    "lengte_alle": (g_lengte_alle, "alle lengtematen omzetten"),
    "liter_alle": (g_liter_alle, "alle litermaten omzetten"),
    "gewicht": (g_gewicht, "ton, kg, g, mg"),
    "omtrekF": (g_omtrekF, "omtrek rechthoek (formule)"),
    "oppF": (g_oppF, "oppervlakte rechthoek (formule)"),
    "schatten": (g_schatten, "schatten hoeveel iets kost"),
    "terug_groot": (g_terug_groot, "groot bedrag terugkrijgen"),
    "tijdwoorden": (g_tijdwoorden, "kloktijden"),
    "duur1": (mk_duur(1, "du1"), "hoelang duurt het"),
    # groep 8
    "kommaxheel": (g_kommaxheel, "kommagetal × heel getal"),
    "kommadeelheel": (g_kommadeelheel, "kommagetal : heel getal"),
    "toeafname": (g_toeafname, "toe- en afname in procenten"),
    "heelxbreuk": (g_heelxbreuk, "heel getal × breuk"),
    "heeldeelbreuk": (g_heeldeelbreuk, "heel getal : makkelijke breuk"),
    "vergverh": (g_vergverh, "verhoudingen vergelijken"),
    "lijngrafiek8": (g_lijngrafiek8, "moeilijkere lijngrafieken"),
}

PLAN = [
    ((1, 2),   "Opstart: herhaling groep 7",            ["alletafels", "alledeel", "met", "kommaplus2"], ["over", "proc_anker", "omzetten"]),
    ((3, 4),   "Kommagetal × heel getal, 1%-regel",     ["kommaxheel", "proc_1", "alletafels", "alledeel"], ["met", "kommaplus2", "vereenvoudig"]),
    ((5, 6),   "Omzetten, toe- en afname",              ["toeafname", "omzetten", "kommaxheel", "kommaplus2"], ["alletafels", "proc_1", "met"]),
    ((7, 8),   "Herhaling blok 1–2",                    ["toeafname", "kommaxheel", "proc_1", "omzetten", "alledeel"], ["kommaplus2", "met"]),
    ((9, 10),  "Breuken: vergelijken en × breuk",       ["breukverg", "heelxbreuk", "over", "kommadeelheel"], ["toeafname", "alletafels", "met"]),
    ((11, 12), "Kommagetal : heel getal, verhoudingen", ["kommadeelheel", "vergverh", "heelxbreuk", "over"], ["proc_1", "kommaxheel", "omzetten"]),
    ((13, 14), "Omtrek en oppervlakte",                 ["omtrekF", "oppF", "vergverh", "kommadeelheel"], ["breukverg", "met", "toeafname"]),
    ((15, 16), "Herhaling blok 3–4",                    ["heelxbreuk", "kommadeelheel", "vergverh", "oppF", "over"], ["omtrekF", "alledeel"]),
    ((17, 18), "Heel getal : breuk",                    ["heeldeelbreuk", "kommaxheel", "kommadeelheel", "lengte_alle"], ["heelxbreuk", "met", "proc_1"]),
    ((19, 20), "Maten omrekenen",                       ["lengte_alle", "liter_alle", "gewicht", "heeldeelbreuk"], ["kommaxheel", "toeafname", "alletafels"]),
    ((21, 22), "Lijngrafieken",                         ["lijngrafiek8", "gewicht", "heeldeelbreuk", "kommaxheel"], ["liter_alle", "vergverh", "met"]),
    ((23, 24), "Herhaling blok 5–6",                    ["heeldeelbreuk", "kommaxheel", "kommadeelheel", "lengte_alle", "lijngrafiek8"], ["gewicht", "liter_alle"]),
    ((25, 26), "Herhaling: procenten en breuken",       ["proc_1", "toeafname", "omzetten", "heelxbreuk"], ["met", "alletafels", "over"]),
    ((27, 28), "Herhaling: kommagetallen",              ["kommaplus2", "kommaxheel", "kommadeelheel", "kommax10"], ["met", "alledeel", "proc_anker"]),
    ((29, 30), "Herhaling: meten en verhoudingen",      ["vtabel", "vergverh", "snelheid", "samenhang"], ["lengte_alle", "oppF", "met"]),
    ((31, 32), "Herhaling: alles door elkaar",          ["toeafname", "heeldeelbreuk", "kommaxheel", "oppF", "alletafels"], ["met", "lijngrafiek8"]),
    ((33, 34), "Extra: rekenen tot 100 en tafels",      ["met", "alletafels", "alledeel", "deelsplits3"], ["over", "tot20", "kommaplus2"]),
    ((35, 36), "Extra: geld en procenten",              ["toeafname", "schatten", "proc_1", "terug_groot"], ["met", "omzetten", "kommaxheel"]),
    ((37, 38), "Extra: tijd en maten",                  ["duur1", "tijdwoorden", "lengte_alle", "gewicht"], ["met", "alletafels", "snelheid"]),
    ((39, 40), "Afsluiting basisschool",                ["met", "alletafels", "toeafname", "kommaxheel", "heeldeelbreuk"], ["omzetten", "vergverh", "oppF"]),
]

INTRO = (
    "Eén pagina per week: <b>paginanummer = weeknummer</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook: 10 opdrachten (± 5 minuten), "
    "ongeveer 7 focus en 3 herhaling. Rekenmuurtje: blok 2/4/6 = week 8/16/24 (de lijn van groep 8 stopt na blok 6). "
    "Week 25–32 herhalen alle doelen van groep 7 en 8; week 33–40 zijn extra. "
    "<b>Rekenen tot 100 uit het hoofd en de tafels blijven het hele jaar terugkomen.</b>"
)
