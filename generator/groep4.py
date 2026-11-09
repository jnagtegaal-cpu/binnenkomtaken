from engine import *
from groep3 import g_addsub10, g_aanvul, g_van10, g_teen, g_dubbel
import groep3

# ------------------------------------------------------------------ sommen tot 20 / 100

def g_tot20(rng):
    """6 + 8 & 14 – 8: tot 20, meestal over het tiental."""
    if rng.random() < 0.5:
        a = rng.randint(2, 9); b = rng.randint(max(2, 11 - a), 9)
        return sum_item(("t20+", a, b), a + b, [f"{a} + {b} =", None])
    t = rng.randint(11, 18); b = rng.randint(t - 9, 9)
    return sum_item(("t20-", t, b), t - b, [f"{t} – {b} =", None])

def g_tt(rng):
    """35 + 3 & 38 – 3: binnen het tiental."""
    T = 10 * rng.randint(1, 9)
    if rng.random() < 0.5:
        e = rng.randint(1, 7); b = rng.randint(1, 9 - e)
        return sum_item(("tt+", T, e, b), T + e + b, [f"{T + e} + {b} =", None])
    e = rng.randint(3, 9); b = rng.randint(1, e - 1)
    return sum_item(("tt-", T, e, b), T + e - b, [f"{T + e} – {b} =", None])

def g_tienv(rng):
    """30 + 20 & 70 – 30"""
    if rng.random() < 0.5:
        a = rng.randint(1, 8); b = rng.randint(1, 10 - a)
        return sum_item(("tv+", a, b), 10 * (a + b), [f"{10 * a} + {10 * b} =", None])
    a = rng.randint(2, 10); b = rng.randint(1, a - 1)
    return sum_item(("tv-", a, b), 10 * (a - b), [f"{10 * a} – {10 * b} =", None])

def g_tienvplus(rng):
    """35 + 20 & 78 – 30"""
    e = rng.randint(1, 9)
    if rng.random() < 0.5:
        T = rng.randint(1, 7); b = rng.randint(1, 9 - T)
        n = 10 * T + e
        return sum_item(("tvp+", n, b), n + 10 * b, [f"{n} + {10 * b} =", None])
    T = rng.randint(2, 9); b = rng.randint(1, T - 1)
    n = 10 * T + e
    return sum_item(("tvp-", n, b), n - 10 * b, [f"{n} – {10 * b} =", None])

def g_vanaf(rng):
    """40 + 3 & 74 – ? = 70"""
    T = 10 * rng.randint(2, 9); e = rng.randint(1, 9)
    if rng.random() < 0.5:
        return sum_item(("vf+", T, e), T + e, [f"{T} + {e} =", None])
    return sum_item(("vf-", T, e), e, [f"{T + e} –", None, f"= {T}"])

def g_aanvT(rng):
    """35 + ? = 40 & 70 – 4"""
    T = 10 * rng.randint(2, 10); e = rng.randint(1, 9)
    if rng.random() < 0.5:
        return sum_item(("avT", T, e), e, [f"{T - e} +", None, f"= {T}"])
    return sum_item(("vT", T, e), T - e, [f"{T} – {e} =", None])

def g_over(rng):
    """35 + 8 & 74 – 8: over het tiental"""
    T = 10 * rng.randint(1, 8)
    if rng.random() < 0.5:
        e = rng.randint(2, 9); b = rng.randint(max(2, 11 - e), 9)
        return sum_item(("ov+", T, e, b), T + e + b, [f"{T + e} + {b} =", None])
    T = 10 * rng.randint(2, 9)
    e = rng.randint(1, 7); b = rng.randint(e + 1, 9)
    return sum_item(("ov-", T, e, b), T + e - b, [f"{T + e} – {b} =", None])

def g_zonder(rng):
    """35 + 13 / 35 + 23 & 78 – 13 / 78 – 23: twee tweecijferige getallen, niet over het tiental"""
    if rng.random() < 0.5:
        T1 = rng.randint(1, 7); T2 = rng.randint(1, 8 - T1)
        e1 = rng.randint(1, 8); e2 = rng.randint(1, 9 - e1)
        a, b = 10 * T1 + e1, 10 * T2 + e2
        if rng.random() < 0.3: a, b = b, a
        return sum_item(("zo+", a, b), a + b, [f"{a} + {b} =", None])
    T1 = rng.randint(2, 9); T2 = rng.randint(1, T1 - 1)
    e1 = rng.randint(2, 9); e2 = rng.randint(1, e1)
    a, b = 10 * T1 + e1, 10 * T2 + e2
    return sum_item(("zo-", a, b), a - b, [f"{a} – {b} =", None])

def g_met(rng):
    """35 + 28 & 74 – 38: twee tweecijferige getallen, over het tiental"""
    if rng.random() < 0.5:
        T1 = rng.randint(1, 7); T2 = rng.randint(1, 8 - T1)
        e1 = rng.randint(2, 9); e2 = rng.randint(max(1, 11 - e1), 9)
        a, b = 10 * T1 + e1, 10 * T2 + e2
        return sum_item(("me+", a, b), a + b, [f"{a} + {b} =", None])
    T1 = rng.randint(3, 9); T2 = rng.randint(1, T1 - 2)
    e1 = rng.randint(1, 7); e2 = rng.randint(e1 + 1, 9)
    a, b = 10 * T1 + e1, 10 * T2 + e2
    return sum_item(("me-", a, b), a - b, [f"{a} – {b} =", None])

def mk_tafel(tables, name):
    def g(rng):
        n = rng.choice(tables); a = rng.randint(1, 10)
        if rng.random() < 0.25:
            return sum_item((name, n, a), a * n, [f"{n} × {a} =", None])
        return sum_item((name, a, n), a * n, [f"{a} × {n} =", None])
    return g

def g_splits100(rng):
    T = 10 * rng.randint(2, 9); e = rng.randint(1, 9); n = T + e
    v = rng.choice([0, 1, 2, 3])
    if v == 0:
        return sum_item(("sp0", n), e, [f"{n} = {T} +", None])
    if v == 1:
        return sum_item(("sp1", n), T, [f"{n} =", None, f"+ {e}"])
    if v == 2:
        return sum_item(("sp2", n), n, [None, f"= {T} + {e}"])
    left = rng.random() < 0.5
    def d(c, x, y, ch):
        splitsbeen(c, x, y, ch, str(n), str(T) if left else None, None if left else str(e))
    return Item(("sp3", n, left), e if left else T, d)

# ------------------------------------------------------------------ plaatjes

def g_mab(rng):
    """Hoeveelheden tot 100: staven van 10 en losse blokjes."""
    t = rng.randint(1, 5); e = rng.randint(0, 9)
    if t * 10 + e < 11: e = rng.randint(1, 9)
    def d(c, x, y, ch):
        u = 1.3 * mm
        bx, by = x + 2.5 * mm, y + (ch - 10 * u) / 2 - 0.5 * mm
        c.setLineWidth(0.5); c.setStrokeColor(black)
        for i in range(t):
            xx = bx + i * (u * 1.9)
            c.setFillColor(HexColor("#bfe3f5")); c.rect(xx, by, u * 1.4, 10 * u, stroke=1, fill=1)
            for k in range(1, 10):
                c.line(xx, by + k * u, xx + u * 1.4, by + k * u)
        ox = bx + t * (u * 1.9) + 1.2 * mm
        for k in range(e):
            col, row = divmod(k, 5)
            c.setFillColor(HexColor("#f6c7c3"))
            c.rect(ox + col * u * 1.9, by + row * u * 1.9, u * 1.4, u * 1.4, stroke=1, fill=1)
        c.setFillColor(black)
        box(c, x + CELL_W - BW - 1.5 * mm, y + (ch - BH) / 2)
    return Item(("mab", t, e), 10 * t + e, d)


def g_lijnT(rng):
    """Getallen tot 100 tussen tientallen plaatsen (bv. lijn 40–50)."""
    lo = 10 * rng.randint(0, 9); hi = lo + 10
    t = rng.choice([v for v in range(lo + 1, hi) if v != lo + 5])
    def d(c, x, y, ch):
        numberline(c, x, y, lo, hi, 1, (lo, lo + 5, hi), t)
    return Item(("lT", t), t, d)


def g_lijn100(rng):
    """Getallen tot 100 precies op de getallenlijn (streepjes per 5)."""
    t = rng.choice([v for v in range(5, 100, 5) if v != 50])
    def d(c, x, y, ch):
        numberline(c, x, y, 0, 100, 5, (0, 50, 100), t)
    return Item(("l100", t), t, d)


NOTE_W, NOTE_H, COIN_R = 9.5 * mm, 5.5 * mm, 2.9 * mm

def draw_money(c, x, y, vals):
    cx = x
    for v in vals:
        if v >= 5:
            c.setFillColor({5: HexColor("#d9dde3"), 10: HexColor("#f4c9c4"), 20: HexColor("#c9daf4"), 50: HexColor("#f7d9a8")}[v])
            c.setStrokeColor(black); c.setLineWidth(0.6)
            c.roundRect(cx, y, NOTE_W, NOTE_H, 0.8 * mm, stroke=1, fill=1)
            c.setFillColor(black); c.setFont(FONTB, 7.5)
            c.drawCentredString(cx + NOTE_W / 2, y + 1.8 * mm, f"€ {v}")
            cx += NOTE_W + 1 * mm
        else:
            c.setFillColor(HexColor("#f1dc8f") if v == 2 else HexColor("#e6e6e6"))
            c.setStrokeColor(black); c.setLineWidth(0.6)
            c.circle(cx + COIN_R, y + NOTE_H / 2, COIN_R, stroke=1, fill=1)
            c.setFillColor(black); c.setFont(FONTB, 6.5)
            c.drawCentredString(cx + COIN_R, y + NOTE_H / 2 - 0.9 * mm, f"€{v}")
            cx += 2 * COIN_R + 1 * mm
    return cx - x


def g_geld(rng):
    """Briefjes en munten tellen (hele euro's)."""
    for _ in range(100):
        k = rng.randint(2, 4)
        vals = sorted((rng.choice([1, 2, 2, 5, 10, 10, 20]) for _ in range(k)), reverse=True)
        notes = sum(1 for v in vals if v >= 5)
        width = notes * (NOTE_W + 1 * mm) + (k - notes) * (2 * COIN_R + 1 * mm)
        if width < CELL_W - 3 * mm and sum(vals) <= 50:
            break
    def d(c, x, y, ch):
        wtot = width - 1 * mm
        draw_money(c, x + (CELL_W - wtot) / 2, y + ch - NOTE_H - 4 * mm, vals)
        c.setFont(FONT, 12)
        c.drawString(x + CELL_W / 2 - 7.5 * mm, y + 3.5 * mm, "€")
        box(c, x + CELL_W / 2 - 3.5 * mm, y + 1.2 * mm)
    return Item(("geld", tuple(vals)), sum(vals), d)


def g_terug(rng):
    """Een bedrag in hele euro's betalen en uitrekenen hoeveel je terugkrijgt."""
    pay = rng.choice([5, 10, 10, 20, 20, 50])
    cost = rng.randint(max(1, pay // 4), pay - 1)
    def d(c, x, y, ch):
        c.setFont(FONT, 8.5); c.setFillColor(black)
        c.drawString(x + 3 * mm, y + ch - 6.5 * mm, f"Het kost € {cost}.")
        c.drawString(x + 3 * mm, y + ch - 10.5 * mm, f"Je betaalt € {pay}.")
        c.setFont(FONT, 9)
        c.drawString(x + 3 * mm, y + 3.6 * mm, "Terug: €")
        box(c, x + 17.5 * mm, y + 1.2 * mm)
    return Item(("terug", pay, cost), pay - cost, d)


def g_digitaal(rng):
    """Hele en halve uren op een digitale klok."""
    h = rng.randint(1, 12); half = rng.random() < 0.5
    ans = (h % 12) + 1 if half else h
    def d(c, x, y, ch):
        bx, by, bw, bh = x + 2.5 * mm, y + ch / 2 - 4.5 * mm, 17 * mm, 9 * mm
        c.setFillColor(HexColor("#26323a")); c.roundRect(bx, by, bw, bh, 1.5 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor("#7ee08a")); c.setFont("Courier-Bold", 13)
        c.drawCentredString(bx + bw / 2, by + 2.6 * mm, f"{h}:{'30' if half else '00'}")
        c.setFillColor(black); c.setFont(FONT, 10.5)
        if half:
            c.drawString(x + 21 * mm, y + ch / 2 - 1.3 * mm, "half")
            box(c, x + 29.2 * mm, y + ch / 2 - 4 * mm, 8.5 * mm, BH)
        else:
            box(c, x + 21 * mm, y + ch / 2 - 4 * mm, 8.5 * mm, BH)
            c.drawString(x + 30.6 * mm, y + ch / 2 - 1.3 * mm, "uur")
    return Item(("dig", h, half), ans, d)


def g_kwartier(rng):
    """Kwartieren op een klok met wijzers."""
    h = rng.randint(1, 12); over = rng.random() < 0.5
    # kwart over h = h:15 ; kwart voor h = (h-1):45
    if over:
        hp, mp = (h % 12) + 0.25, 15
    else:
        hp, mp = ((h - 1) % 12) + 0.75, 45
    def d(c, x, y, ch):
        clock_face(c, x + 10.5 * mm, y + ch / 2, hp, mp)
        c.setFont(FONT, 8.5)
        c.drawCentredString(x + 29 * mm, y + ch / 2 + 3.2 * mm, "kwart " + ("over" if over else "voor"))
        box(c, x + 24.5 * mm, y + ch / 2 - 7 * mm, 8.5 * mm, BH)
    return Item(("kw", h, over), h, d)


def g_klokmix4(rng):
    r = rng.random()
    if r < 0.4: return g_kwartier(rng)
    if r < 0.7: return g_digitaal(rng)
    return mk_clock("mix")(rng)


TYPES = {
    # herhaling groep 3
    "plusmin10": (g_addsub10, "+ en – tot 10"),
    "aanvul": (g_aanvul, "aanvullen tot 10"),
    "van10": (g_van10, "10 – 4"),
    "teen": (g_teen, "15 + 3 / 18 – 3"),
    "spl10": (mk_splits([10], "spl10"), "splitsen van 10"),
    "splN": (mk_splits(list(range(4, 10)), "splN"), "splitsen tot 10"),
    "dubbel": (g_dubbel, "dubbelsommen"),
    # groep 4
    "tot20": (g_tot20, "6 + 8 / 14 – 8"),
    "tel100": (mk_seq(0, 100, 1, "tel100"), "telrij tot 100"),
    "terug100": (mk_seq(0, 100, -1, "terug100", "terugtellen"), "terugtellen tot 100"),
    "sprong10": (mk_seq(1, 99, 10, "sp10", "sprongen van 10"), "sprongen van 10 vooruit"),
    "sprong10t": (mk_seq(1, 99, -10, "sp10t", "sprongen van 10 terug"), "sprongen van 10 terug"),
    "verg100": (mk_cmp(10, 99, "verg100"), "vergelijken tot 100"),
    "mab": (g_mab, "hoeveelheden tot 100 (tientallen en losse)"),
    "splits100": (g_splits100, "getallen tot 100 splitsen"),
    "lijnT": (g_lijnT, "getallenlijn tussen tientallen"),
    "lijn100": (g_lijn100, "getallenlijn 0–100 precies"),
    "tt": (g_tt, "35 + 3 / 38 – 3"),
    "tienv": (g_tienv, "30 + 20 / 70 – 30"),
    "tienvplus": (g_tienvplus, "35 + 20 / 78 – 30"),
    "vanaf": (g_vanaf, "40 + 3 / 74 – ? = 70"),
    "aanvT": (g_aanvT, "35 + ? = 40 / 70 – 4"),
    "over": (g_over, "35 + 8 / 74 – 8"),
    "zonder": (g_zonder, "35 + 23 / 78 – 23"),
    "met": (g_met, "35 + 28 / 74 – 38"),
    "tafel10": (mk_tafel([10], "x10"), "tafel van 10"),
    "tafel2": (mk_tafel([2], "x2"), "tafel van 2"),
    "tafel2_10": (mk_tafel([2, 10], "x210"), "tafels van 2 en 10"),
    "tafel5": (mk_tafel([5], "x5"), "tafel van 5"),
    "tafel3": (mk_tafel([3], "x3"), "tafel van 3"),
    "tafel4": (mk_tafel([4], "x4"), "tafel van 4"),
    "tafel34": (mk_tafel([3, 4], "x34"), "tafels van 3 en 4"),
    "tafelmix": (mk_tafel([1, 2, 3, 4, 5, 10], "xmix"), "tafels 1, 2, 3, 4, 5, 10 door elkaar"),
    "geld": (g_geld, "geld tellen"),
    "terug": (g_terug, "terugkrijgen (hele euro's)"),
    "digitaal": (g_digitaal, "digitale klok hele/halve uren"),
    "kwartier": (g_kwartier, "kwartieren (wijzers)"),
    "klokmix": (g_klokmix4, "klok door elkaar"),
}

PLAN = [
    ((1, 2),   "Opstart: herhaling groep 3",            ["plusmin10", "aanvul", "teen", "tel100"], ["spl10", "splN", "van10"]),
    ((3, 4),   "Telrij tot 100, tot 20",                ["tel100", "terug100", "tot20", "sprong10"], ["plusmin10", "aanvul", "teen"]),
    ((5, 6),   "Getallen tot 100 maken en splitsen",    ["mab", "splits100", "lijnT", "tot20"], ["tel100", "terug100", "spl10"]),
    ((7, 8),   "Tussen tientallen: 35 + 3",             ["tt", "tot20", "lijnT", "sprong10t"], ["mab", "splits100", "aanvul"]),
    ((9, 10),  "Tienvouden: 30 + 20",                   ["tienv", "tot20", "lijn100", "tt"], ["sprong10", "splits100", "van10"]),
    ((11, 12), "35 + 20 en 40 + 3",                     ["tienvplus", "vanaf", "tot20", "tienv"], ["tt", "lijnT", "verg100"]),
    ((13, 14), "Naar het tiental en over het tiental",  ["aanvT", "over", "geld", "tienvplus"], ["tot20", "vanaf", "lijn100"]),
    ((15, 16), "Herhaling blok 3–4",                    ["over", "aanvT", "tienvplus", "geld", "tot20"], ["tienv", "vanaf"]),
    ((17, 18), "Tafel van 10, 35 + 13",                 ["tafel10", "zonder", "tienvplus", "digitaal"], ["over", "tot20", "aanvT"]),
    ((19, 20), "Tafel van 2, 35 + 23",                  ["tafel2", "zonder", "terug", "kwartier"], ["over", "tot20", "tafel10"]),
    ((21, 22), "Tafels 2 en 10, geld terug",            ["zonder", "tafel2_10", "terug", "kwartier"], ["over", "aanvT", "tot20"]),
    ((23, 24), "Herhaling blok 5–6",                    ["zonder", "tot20", "tafel2_10", "klokmix", "terug"], ["over", "tienvplus"]),
    ((25, 26), "Tafel van 5, over het tiental vlot",    ["tafel5", "over", "tot20", "tafel2_10"], ["zonder", "aanvT", "kwartier"]),
    ((27, 28), "Tafel van 3, 35 + 28",                  ["tafel3", "met", "over", "tafel5"], ["zonder", "tot20", "geld"]),
    ((29, 30), "Tafel van 4, 74 – 38",                  ["tafel4", "met", "tafel3", "over"], ["zonder", "tot20", "tafel2_10"]),
    ((31, 32), "Herhaling blok 7–8",                    ["tafelmix", "met", "over", "tot20", "zonder"], ["aanvT", "klokmix"]),
    ((33, 34), "Extra: rekenen tot 100",                ["met", "zonder", "tafelmix", "tienvplus"], ["over", "tot20", "kwartier"]),
    ((35, 36), "Extra: tot 100 en geld",                ["met", "tafelmix", "aanvT", "terug"], ["over", "tot20", "lijn100"]),
    ((37, 38), "Extra: tafels 3 en 4 vlot",             ["tafel34", "met", "tafelmix", "over"], ["zonder", "tot20", "sprong10t"]),
    ((39, 40), "Jaarafsluiting: alles door elkaar",     ["met", "tafelmix", "over", "tot20", "zonder"], ["aanvT", "klokmix", "terug"]),
]

INTRO = (
    "Eén pagina per schoolweek; bovenaan staat het <b>weeknummer van de kalender</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook heeft 10 opdrachten (± 5 minuten): "
    "ongeveer 7 over de focus van de week en 3 herhalingsopdrachten.<br/>"
    "Aansluiting op het Rekenmuurtje: blok 2 = {w:8}, blok 4 = {w:16}, blok 6 = {w:24}, blok 8 = {w:32}. "
    "{W:1-2} starten met herhaling van groep 3. Sommen tot 20 (6 + 8 / 14 – 8) komen het hele jaar terug. "
    "{W:33-40} zijn extra: veel oefening met rekenen tot 100 (35 + 28 en 74 – 38) en de tafels door elkaar, "
    "zodat dit stevig staat vóór groep 5. "
    "De lege getallenlijn en staafgrafieken uit de lijn zitten er niet in; die passen niet op een smalle strook. "
    "Mag een kind bij de sommen tot 100 een kladje gebruiken, leg dat dan klaar."
)
