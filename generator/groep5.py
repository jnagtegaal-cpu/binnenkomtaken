from engine import *
from groep4 import (g_tot20, g_over, g_zonder, g_met, g_aanvT, mk_tafel, draw_money,
                    NOTE_W, NOTE_H, COIN_R, g_kwartier)

# ------------------------------------------------------------------ getallen tot 1000

def g_rondom(rng):
    """Tellen en terugtellen rondom een honderdtal (298, 299, 300)."""
    Hh = 100 * rng.randint(1, 9)
    down = rng.random() < 0.4
    step = -1 if down else 1
    s = Hh + rng.randint(0, 2) if down else Hh - rng.randint(0, 2)
    seq = [s, s + step, s + 2 * step]
    blank = rng.choice([0, 1, 2])
    parts = []
    for i, v in enumerate(seq):
        parts.append(None if i == blank else str(v))
        if i < 2: parts.append(",")
    def d(c, x, y, ch):
        if down: label(c, x, y + ch - 3 * mm, "terugtellen")
        text_with_boxes(c, x, y + ch / 2 - 2.5 * mm, parts, 14)
    it = Item(("rd", s, down, blank), seq[blank], d); it.seq = (seq, step)
    return it


def mk_sprong(step, name, start_mult=1):
    def g(rng):
        down = rng.random() < 0.4
        st = -step if down else step
        lo, hi = (2 * step, 1000) if down else (1, 1000 - 2 * step)
        s = rng.randint(lo, hi)
        s = (s // start_mult) * start_mult or start_mult
        seq = [s, s + st, s + 2 * st]
        blank = rng.choice([0, 1, 2])
        parts = []
        for i, v in enumerate(seq):
            parts.append(None if i == blank else str(v))
            if i < 2: parts.append(",")
        lab = f"sprongen van {step}" + (" terug" if down else "")
        def d(c, x, y, ch):
            label(c, x, y + ch - 3 * mm, lab)
            text_with_boxes(c, x, y + ch / 2 - 2.5 * mm, parts, 14)
        it = Item((name, s, down, blank), seq[blank], d); it.seq = (seq, st)
        return it
    return g


def g_sprong100_50(rng):
    return (mk_sprong(100, "s100") if rng.random() < 0.5 else mk_sprong(50, "s50", 50))(rng)


def g_mab1000(rng):
    """Handig tellen tot 1000 met een structuur: honderdplaten, staven, blokjes."""
    P, B, U = 6.6 * mm, 1.6 * mm, 1.1 * mm
    for _ in range(100):
        h = rng.randint(1, 4); t = rng.randint(0, 6); e = rng.randint(0, 9)
        width = h * (P + 0.8 * mm) + t * (B + 0.7 * mm) + (math.ceil(e / 5)) * (U + 0.6 * mm)
        if width < CELL_W - 4 * mm:
            break
    def d(c, x, y, ch):
        cx = x + (CELL_W - width) / 2
        by = y + ch - P - 3.6 * mm
        c.setLineWidth(0.5); c.setStrokeColor(black)
        for i in range(h):
            c.setFillColor(HexColor("#fde3a7")); c.rect(cx, by, P, P, stroke=1, fill=1)
            c.setStrokeColor(HexColor("#c9a85a")); c.setLineWidth(0.25)
            for k in range(1, 10):
                c.line(cx + k * P / 10, by, cx + k * P / 10, by + P)
                c.line(cx, by + k * P / 10, cx + P, by + k * P / 10)
            c.setStrokeColor(black); c.setLineWidth(0.5)
            c.rect(cx, by, P, P, stroke=1, fill=0)
            cx += P + 0.8 * mm
        for i in range(t):
            c.setFillColor(HexColor("#bfe3f5")); c.rect(cx, by, B, P, stroke=1, fill=1)
            cx += B + 0.7 * mm
        for k in range(e):
            col, row = divmod(k, 5)
            c.setFillColor(HexColor("#f6c7c3"))
            c.rect(cx + col * (U + 0.6 * mm), by + row * (U + 0.22 * mm), U, U, stroke=1, fill=1)
        c.setFillColor(black)
        box(c, x + (CELL_W - BW) / 2, y + 0.8 * mm)
    return Item(("m1000", h, t, e), 100 * h + 10 * t + e, d)


def g_splits1000(rng):
    h, t, e = rng.randint(1, 9), rng.randint(0, 9), rng.randint(1, 9)
    n = 100 * h + 10 * t + e
    v = rng.choice([0, 1, 2])
    if v == 0:
        return sum_item(("sk0", n), 100 * h, [f"{n} =", None, f"+ {10 * t + e}"])
    if v == 1:
        return sum_item(("sk1", n), n, [None, f"= {100 * h} + {10 * t} + {e}"])
    return sum_item(("sk2", n), e, [f"{n} = {100 * h + 10 * t} +", None])


def g_lijn1000(rng):
    if rng.random() < 0.5:
        lo = 100 * rng.randint(0, 9); hi = lo + 100
        t = rng.choice([v for v in range(lo + 10, hi, 10) if v != lo + 50])
        def d(c, x, y, ch): numberline(c, x, y, lo, hi, 10, (lo, lo + 50, hi), t)
        return Item(("l1000h", t), t, d)
    lo = 10 * rng.randint(10, 99); hi = lo + 10
    t = rng.choice([v for v in range(lo + 1, hi) if v != lo + 5])
    def d(c, x, y, ch): numberline(c, x, y, lo, hi, 1, (lo, lo + 5, hi), t)
    return Item(("l1000t", t), t, d)


def g_nullen(rng):
    v = rng.choice([0, 1, 2, 3])
    if v == 0:
        a = rng.randint(1, 8); b = rng.randint(1, 9 - a)
        return sum_item(("n0", a, b), 100 * (a + b), [f"{100 * a} + {100 * b} =", None])
    if v == 1:
        a = rng.randint(2, 9); b = rng.randint(1, a - 1)
        return sum_item(("n1", a, b), 100 * (a - b), [f"{100 * a} – {100 * b} =", None])
    if v == 2:
        a = rng.randint(2, 9); b = rng.randint(2, 9)
        return sum_item(("n2", a, b), 10 * (a + b), [f"{10 * a} + {10 * b} =", None])
    a = rng.randint(11, 18); b = rng.randint(a - 9, 9)
    return sum_item(("n3", a, b), 10 * (a - b), [f"{10 * a} – {10 * b} =", None])


def g_delen10(rng):
    q = rng.randint(2, 99) * 10 // 10
    n = 10 * q
    return sum_item(("d10", n), q, [f"{n} : 10 =", None])


def g_honderd(rng):
    """152 + 230 & 763 – 340: zonder overschrijding."""
    if rng.random() < 0.5:
        h1, t1, e1 = rng.randint(1, 7), rng.randint(0, 8), rng.randint(0, 9)
        h2 = rng.randint(1, 8 - h1); t2 = rng.randint(1, 9 - t1)
        a, b = 100 * h1 + 10 * t1 + e1, 100 * h2 + 10 * t2
        return sum_item(("h+", a, b), a + b, [f"{a} + {b} =", None])
    h1, t1, e1 = rng.randint(2, 9), rng.randint(1, 9), rng.randint(0, 9)
    h2 = rng.randint(1, h1 - 1); t2 = rng.randint(1, t1)
    a, b = 100 * h1 + 10 * t1 + e1, 100 * h2 + 10 * t2
    return sum_item(("h-", a, b), a - b, [f"{a} – {b} =", None])


# ------------------------------------------------------------------ deeltafels en vermenigvuldigen

def mk_deel(tables, name):
    def g(rng):
        n = rng.choice(tables); a = rng.randint(1, 10)
        return sum_item((name, n, a), a, [f"{a * n} : {n} =", None])
    return g


def g_x10tal(rng):
    """4 × 30 & 7 × 60"""
    a = rng.randint(2, 9); b = rng.randint(2, 9)
    if rng.random() < 0.3:
        return sum_item(("xt1", a, b), a * b * 10, [f"{10 * b} × {a} =", None])
    return sum_item(("xt0", a, b), a * b * 10, [f"{a} × {10 * b} =", None])


def g_deeltal(rng):
    """120 : 3 & 250 : 5"""
    n = rng.randint(2, 9); q = rng.randint(2, 9)
    return sum_item(("dt", n, q), 10 * q, [f"{n * q * 10} : {n} =", None])


def g_xsplits(rng):
    """6 × 32 via splitsen"""
    a = rng.randint(2, 6); b = rng.choice([v for v in range(11, 40) if v % 10])
    if a * b > 200: b = rng.randint(11, 19)
    return sum_item(("xs", a, b), a * b, [f"{a} × {b} =", None])


# ------------------------------------------------------------------ meten, tijd, geld

def g_kg(rng):
    v = rng.choice([0, 0, 1, 2])
    if v == 0:
        k = rng.randint(1, 9)
        return text_item(("kg0", k), 1000 * k, [f"{k} kg =", None, "g"], norange=True)
    if v == 1:
        k = rng.randint(1, 9)
        return text_item(("kg1", k), k, [f"{1000 * k} g =", None, "kg"])
    return text_item(("kg2",), 500, ["½ kg =", None, "g"])


def g_lengte(rng):
    """De betekenis van kommagetallen in lengtematen."""
    v = rng.choice([0, 1, 2])
    m = rng.randint(0, 5)
    if v == 0:
        return text_item(("le0", m), 100 * m + 50, [f"{m},5 m =", None, "cm"])
    if v == 1:
        d = rng.choice([25, 75])
        return text_item(("le1", m, d), 100 * m + d, [f"{m},{d} m =", None, "cm"])
    cm = rng.randint(1, 9)
    return text_item(("le2", m, cm), 100 * m + 10 * cm, [f"{m},{cm} m =", None, "cm"])


def g_omtrek(rng):
    a, b = rng.randint(3, 9), rng.randint(2, 6)
    if a == b: a += 1
    def d(c, x, y, ch):
        rw, rh = 4 * mm + a * 1.6 * mm, 2.5 * mm + b * 1.1 * mm
        rx, ry = x + 3.5 * mm, y + (ch - rh) / 2 - 1 * mm
        c.setLineWidth(0.9); c.setStrokeColor(black)
        c.setFillColor(HexColor("#e8f4fb")); c.rect(rx, ry, rw, rh, stroke=1, fill=1)
        c.setFillColor(black); c.setFont(FONT, 7.5)
        c.drawCentredString(rx + rw / 2, ry + rh + 1 * mm, f"{a} cm")
        c.drawRightString(rx - 0.6 * mm, ry + rh / 2 - 1, f"{b}")
        c.setFont(FONT, 7.5)
        c.drawString(x + 25 * mm, y + ch - 7.5 * mm, "omtrek")
        box(c, x + 24.5 * mm, y + ch / 2 - 6 * mm, 8.5 * mm, BH)
        c.drawString(x + 33.6 * mm, y + ch / 2 - 3.6 * mm, "cm")
    return Item(("om", a, b), 2 * (a + b), d)


def g_geldgroot(rng):
    """Grotere bedragen tellen en betalen."""
    for _ in range(200):
        k = rng.randint(3, 4)
        vals = sorted((rng.choice([50, 20, 20, 10, 10, 5, 2, 1]) for _ in range(k)), reverse=True)
        notes = sum(1 for v in vals if v >= 5)
        width = notes * (NOTE_W + 1 * mm) + (k - notes) * (2 * COIN_R + 1 * mm)
        if width < CELL_W - 3 * mm:
            break
    def d(c, x, y, ch):
        draw_money(c, x + (CELL_W - width + 1 * mm) / 2, y + ch - NOTE_H - 4 * mm, vals)
        c.setFont(FONT, 12)
        c.drawString(x + CELL_W / 2 - 7.5 * mm, y + 3.5 * mm, "€")
        box(c, x + CELL_W / 2 - 3.5 * mm, y + 1.2 * mm)
    return Item(("gg", tuple(vals)), sum(vals), d)


def _digital(c, bx, by, txt, bw=15.5 * mm, bh=8 * mm):
    c.setFillColor(HexColor("#26323a")); c.roundRect(bx, by, bw, bh, 1.5 * mm, stroke=0, fill=1)
    c.setFillColor(HexColor("#7ee08a")); c.setFont("Courier-Bold", 12)
    c.drawCentredString(bx + bw / 2, by + 2.4 * mm, txt)
    c.setFillColor(black)


def g_vijfmin(rng):
    """Vijf minuten op een klok met wijzers -> digitale tijd opschrijven."""
    h = rng.randint(1, 12); m = 5 * rng.choice([1, 2, 4, 5, 7, 8, 10, 11])
    def d(c, x, y, ch):
        clock_face(c, x + 10.5 * mm, y + ch / 2, (h % 12) + m / 60, m)
        bx = x + 20.5 * mm; by = y + ch / 2 - 4 * mm
        box(c, bx, by, 7 * mm, BH)
        c.setFont(FONTB, 13); c.drawCentredString(bx + 8.2 * mm, by + 2.2 * mm, ":")
        box(c, bx + 9.4 * mm, by, 7 * mm, BH)
    return Item(("vm", h, m), h * 100 + m, d, norange=True, ans=[str(h), f"{m:02d}"], ans_text=f"{h}:{m:02d}")


def g_wijzers(rng):
    """Vijf minuten op een digitale klok -> wijzers tekenen."""
    h = rng.randint(1, 12); m = 5 * rng.choice([1, 2, 3, 4, 5, 7, 8, 9, 10, 11])
    def d(c, x, y, ch):
        label(c, x + 5 * mm, y + ch - 3 * mm, "teken de wijzers")
        clock_face(c, x + 10.5 * mm, y + ch / 2 - 1 * mm, 0, 0, hands=False)
        _digital(c, x + 21.5 * mm, y + ch / 2 - 5 * mm, f"{h}:{m:02d}")
    def r(c, x, y, ch):
        answer_hands(c, x + 10.5 * mm, y + ch / 2 - 1 * mm, h, m)
    return Item(("wz", h, m), h * 100 + m, d, norange=True, ans=[], ans_draw=r, ans_text=f"wijzers op {h}:{m:02d}")


def g_kwartdig(rng):
    """Kwartieren op een digitale klok."""
    h = rng.randint(1, 12); over = rng.random() < 0.5
    shown = f"{h}:15" if over else f"{(h - 2) % 12 + 1}:45"
    def d(c, x, y, ch):
        _digital(c, x + 2.5 * mm, y + ch / 2 - 4 * mm, shown)
        c.setFont(FONT, 8.5)
        c.drawCentredString(x + 27.5 * mm, y + ch / 2 + 3.2 * mm, "kwart " + ("over" if over else "voor"))
        box(c, x + 23.2 * mm, y + ch / 2 - 7 * mm, 8.5 * mm, BH)
    return Item(("kd", h, over), h, d)


def g_klokmix5(rng):
    r = rng.random()
    if r < 0.35: return g_vijfmin(rng)
    if r < 0.6: return g_wijzers(rng)
    if r < 0.8: return g_kwartdig(rng)
    return g_kwartier(rng)


TYPES = {
    # herhaling groep 4
    "tot20": (g_tot20, "6 + 8 / 14 – 8"),
    "over": (g_over, "35 + 8 / 74 – 8"),
    "zonder": (g_zonder, "35 + 23 / 78 – 23"),
    "met": (g_met, "35 + 27 / 73 – 45"),
    "aanvT": (g_aanvT, "35 + ? = 40 / 70 – 4"),
    "kwartier": (g_kwartier, "kwartieren (wijzers)"),
    "tafel15": (mk_tafel([1, 2, 3, 4, 5, 10], "t15"), "tafels 1–5 en 10 door elkaar"),
    "tafel34": (mk_tafel([3, 4], "t34"), "tafels van 3 en 4"),
    # groep 5
    "tel1000": (mk_seq(0, 1000, 1, "tel1000"), "telrij tot 1000"),
    "rondom": (g_rondom, "tellen rondom een honderdtal"),
    "sprong100_50": (g_sprong100_50, "sprongen van 100 en 50"),
    "sprong10": (mk_sprong(10, "s10"), "sprongen van 10 tot 1000"),
    "mab1000": (g_mab1000, "handig tellen tot 1000 (structuur)"),
    "splits1000": (g_splits1000, "getallen tot 1000 splitsen"),
    "lijn1000": (g_lijn1000, "getallenlijn tot 1000"),
    "verg1000": (mk_cmp(100, 999, "v1000"), "vergelijken tot 1000"),
    "nullen": (g_nullen, "optellen/aftrekken met nullen"),
    "delen10": (g_delen10, "grote getallen delen door 10"),
    "honderd": (g_honderd, "152 + 230 / 763 – 340"),
    "tafel6": (mk_tafel([6], "t6"), "tafel van 6"),
    "tafel8": (mk_tafel([8], "t8"), "tafel van 8"),
    "tafel68": (mk_tafel([6, 8], "t68"), "tafels van 6 en 8"),
    "tafel9": (mk_tafel([9], "t9"), "tafel van 9"),
    "tafel7": (mk_tafel([7], "t7"), "tafel van 7"),
    "tafel6789": (mk_tafel([6, 7, 8, 9], "t69"), "tafels 6–9 door elkaar"),
    "alletafels": (mk_tafel(list(range(1, 11)), "tall"), "alle tafels door elkaar"),
    "deel2510": (mk_deel([2, 5, 10], "d2510"), "deeltafels 2, 5, 10"),
    "deel34": (mk_deel([3, 4], "d34"), "deeltafels 3 en 4"),
    "deelmix5": (mk_deel([2, 3, 4, 5, 10], "d5"), "deeltafels 2, 3, 4, 5, 10 door elkaar"),
    "deel6789": (mk_deel([6, 7, 8, 9], "d69"), "deeltafels 6–9"),
    "alledeel": (mk_deel(list(range(1, 11)), "dall"), "alle deeltafels door elkaar"),
    "x10tal": (g_x10tal, "4 × 30 / 7 × 60"),
    "deeltal": (g_deeltal, "120 : 3 / 250 : 5"),
    "xsplits": (g_xsplits, "6 × 32 (splitsen)"),
    "kg": (g_kg, "1 kg = 1000 g"),
    "lengte": (g_lengte, "kommagetallen in lengtematen"),
    "omtrek": (g_omtrek, "omtrek berekenen"),
    "geld": (g_geldgroot, "grotere bedragen tellen"),
    "vijfmin": (g_vijfmin, "vijf minuten (wijzers)"),
    "wijzers": (g_wijzers, "wijzers tekenen (5 min.)"),
    "kwartdig": (g_kwartdig, "kwartieren (digitaal)"),
    "klokmix": (g_klokmix5, "klok door elkaar"),
}

PLAN = [
    ((1, 2),   "Opstart: herhaling groep 4",          ["tafel15", "met", "over", "tot20"], ["zonder", "aanvT", "kwartier"]),
    ((3, 4),   "Tellen tot 1000, tafels 3 en 4",      ["tel1000", "rondom", "sprong100_50", "tafel34"], ["met", "tot20", "tafel15"]),
    ((5, 6),   "Getallen tot 1000, tafel van 6",      ["mab1000", "splits1000", "sprong10", "tafel6"], ["met", "tot20", "tafel34"]),
    ((7, 8),   "Rekenen met nullen, tafel van 8",     ["nullen", "tafel68", "vijfmin", "delen10"], ["met", "tafel15", "mab1000"]),
    ((9, 10),  "Getallenlijn tot 1000",               ["lijn1000", "verg1000", "tafel8", "honderd"], ["tot20", "nullen", "met"]),
    ((11, 12), "Tafel van 9, 152 + 230",              ["tafel9", "honderd", "lijn1000", "kwartdig"], ["tafel68", "tot20", "met"]),
    ((13, 14), "Tafel van 7, digitale klok",          ["tafel7", "honderd", "wijzers", "tafel9"], ["tot20", "nullen", "lijn1000"]),
    ((15, 16), "Herhaling blok 3–4",                  ["tafel6789", "honderd", "lijn1000", "tot20", "wijzers"], ["met", "nullen"]),
    ((17, 18), "Deeltafels van 2, 5 en 10",           ["deel2510", "tafel15", "over", "tafel7"], ["honderd", "met", "tot20"]),
    ((19, 20), "Deeltafels van 3 en 4, kg en g",      ["deel34", "deel2510", "tafel7", "kg"], ["over", "tafel15", "honderd"]),
    ((21, 22), "Alle tafels door elkaar",             ["alletafels", "deelmix5", "kg", "over"], ["met", "honderd", "vijfmin"]),
    ((23, 24), "Herhaling blok 5–6",                  ["alletafels", "deelmix5", "over", "kg", "tafel6789"], ["met", "honderd"]),
    ((25, 26), "4 × 30 en 120 : 3",                   ["x10tal", "deeltal", "deelmix5", "alletafels"], ["met", "honderd", "tot20"]),
    ((27, 28), "Deeltafels 6–9, lengte en omtrek",    ["deel6789", "x10tal", "lengte", "omtrek"], ["deelmix5", "met", "nullen"]),
    ((29, 30), "6 × 32, geld",                        ["xsplits", "deeltal", "geld", "deel6789"], ["alletafels", "met", "lengte"]),
    ((31, 32), "Herhaling blok 7–8",                  ["alledeel", "alletafels", "x10tal", "deeltal", "omtrek"], ["met", "honderd"]),
    ((33, 34), "Extra: rekenen tot 100",              ["met", "zonder", "alledeel", "alletafels"], ["over", "tot20", "lengte"]),
    ((35, 36), "Extra: rekenen tot 1000",             ["honderd", "nullen", "met", "xsplits"], ["deeltal", "geld", "kg"]),
    ((37, 38), "Extra: tafels en deeltafels vlot",    ["alletafels", "alledeel", "met", "x10tal"], ["over", "omtrek", "klokmix"]),
    ((39, 40), "Jaarafsluiting: alles door elkaar",   ["met", "alletafels", "alledeel", "honderd", "deeltal"], ["lengte", "kg", "klokmix"]),
]

INTRO = (
    "Eén pagina per week: <b>paginanummer = weeknummer</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook heeft 10 opdrachten (± 5 minuten): "
    "ongeveer 7 over de focus van de week en 3 herhalingsopdrachten.<br/>"
    "Rekenmuurtje: blok 2/4/6/8 = week 8/16/24/32. Week 1–2: herhaling groep 4. <b>Rekenen tot 100 uit het hoofd (35 + 27 / 73 – 45) komt het hele "
    "jaar terug</b> (in de lijn alleen in blok 2). Week 33–40 zijn extra: tot 100 en 1000, alle (deel)tafels vlot. "
    "Bij de klok met wijzers schrijven kinderen de digitale tijd op (uur : minuten); bij <i>teken de wijzers</i> "
    "tekenen ze de wijzers in de lege klok. Het beelddiagram zit er niet in (past niet op een strook)."
)
