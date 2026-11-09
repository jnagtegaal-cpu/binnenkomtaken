from math import gcd
from engine import *
from groep4 import g_tot20, g_over, g_met, mk_tafel
from groep5 import (g_honderd, g_deeltal, g_xsplits, mk_deel, _digital)

# ------------------------------------------------------------------ hulpjes

def draw_sq(c, x, y, base, size, align="left", color=black):
    """Tekst met een zelfgetekende kwadraat-2 (het ²-teken heeft geen glyph in dit lettertype)."""
    w = c.stringWidth(base, FONT, size) + c.stringWidth("2", FONT, size * 0.6)
    if align == "center": x -= w / 2
    c.setFillColor(color); c.setFont(FONT, size); c.drawString(x, y, base)
    c.setFont(FONT, size * 0.6); c.drawString(x + c.stringWidth(base, FONT, size), y + size * 0.4, "2")
    c.setFillColor(black)

def twoline(key, answer, top, bottom, top_size=10.5, norange=False, toplabel=None, ans=None, ans_text=None):
    """Bovenste regel tekst (gecentreerd), onderste regel met invulvak(ken)."""
    def d(c, x, y, ch):
        if toplabel:
            label(c, x, y + ch - 3 * mm, toplabel)
        size = top_size
        while c.stringWidth(top, FONT, size) > CELL_W - 3 * mm and size > 7.5:
            size -= 0.5
        if c.stringWidth(top, FONT, size) > CELL_W - 2 * mm:
            PROBLEMS.append(f"te breed (boven): {top}")
        c.setFont(FONT, size); c.setFillColor(black)
        c.drawCentredString(x + CELL_W / 2, y + ch - (8.6 if toplabel else 7.2) * mm, top)
        text_with_boxes(c, x, y + 3.4 * mm, bottom, 12)
    return Item(key, answer, d, norange=norange, ans=ans, ans_text=ans_text)


def seq_big(lo, hi, steps, name, start_mult=100):
    """Sprongen met grote getallen: twee getallen gegeven, het volgende invullen."""
    def g(rng):
        step = rng.choice(steps)
        down = rng.random() < 0.4
        st = -step if down else step
        a = rng.randint(lo + (2 * step if down else 0), hi - (0 if down else 2 * step))
        a = max(lo, (a // start_mult) * start_mult)
        if down and a - 2 * step < lo: a += 2 * step
        if not down and a + 2 * step > hi: a -= 2 * step
        seq = [a, a + st, a + 2 * st]
        lab = f"sprongen van {fmt(step)}" + (" terug" if down else "")
        it = twoline((name, a, st), seq[2], f"{fmt(seq[0])},  {fmt(seq[1])},  …", [WIDE], 11, toplabel=lab)
        it.seq = (seq, st)
        return it
    return g


def mk_tafel_h(tables, name):
    """Tafels zonder de makkelijkste sommen (geen × 1)."""
    def g(rng):
        n = rng.choice(tables); a = rng.randint(2, 10)
        if rng.random() < 0.3:
            return sum_item((name, n, a), a * n, [f"{n} × {a} =", None])
        return sum_item((name, a, n), a * n, [f"{a} × {n} =", None])
    return g


def mk_deel_h(tables, name):
    def g(rng):
        n = rng.choice(tables); a = rng.randint(2, 10)
        return sum_item((name, n, a), a, [f"{a * n} : {n} =", None])
    return g


# ------------------------------------------------------------------ getallen tot 10 000 / 100 000

def g_splits10000(rng):
    th, h, t, e = rng.randint(1, 9), rng.randint(0, 9), rng.randint(0, 9), rng.randint(1, 9)
    n = 1000 * th + 100 * h + 10 * t + e
    r = n - 1000 * th
    v = rng.choice([0, 1, 2, 3])
    if v == 0:
        return sum_item(("k0", n), 1000 * th, [f"{n} =", WIDE, f"+ {r}"])
    if v == 1:
        return sum_item(("k1", n), 10 * t + e, [f"{n} = {n - 10 * t - e} +", None])
    if v == 2:
        return sum_item(("k2", n), n, [f"{1000 * th} + {r} =", WIDE])
    left = rng.random() < 0.5
    def d(c, x, y, ch):
        splitsbeen(c, x, y, ch, str(n), str(1000 * th) if left else None, None if left else str(r), bw=12 * mm)
    return Item(("k3", n, left), r if left else 1000 * th, d)


def g_lijn10000(rng):
    if rng.random() < 0.5:
        lo = 1000 * rng.randint(0, 9); hi = lo + 1000
        t = rng.choice([v for v in range(lo + 100, hi, 100) if v != lo + 500])
        def d(c, x, y, ch): numberline(c, x, y, lo, hi, 100, (lo, lo + 500, hi), t, bw=13 * mm)
        return Item(("L1", t), t, d)
    lo = 100 * rng.randint(10, 99); hi = lo + 100
    t = rng.choice([v for v in range(lo + 10, hi, 10) if v != lo + 50])
    def d(c, x, y, ch): numberline(c, x, y, lo, hi, 10, (lo, lo + 50, hi), t, bw=13 * mm)
    return Item(("L2", t), t, d)


def g_lijn100000(rng):
    """Getallen tot 100 000 ongeveer op de getallenlijn."""
    if rng.random() < 0.5:
        t = rng.choice([v for v in range(5000, 100000, 5000) if v != 50000])
        def d(c, x, y, ch):
            label(c, x, y + ch - 3 * mm, "ongeveer")
            numberline(c, x, y, 0, 100000, 10000, (0, 50000, 100000), t, bw=WBW)
        return Item(("L3", t), t, d)
    lo = 10000 * rng.randint(1, 8); hi = lo + 10000
    t = rng.choice([v for v in range(lo + 1000, hi, 1000) if v != lo + 5000])
    def d(c, x, y, ch):
        numberline(c, x, y, lo, hi, 1000, (lo, lo + 5000, hi), t, bw=WBW)
    return Item(("L4", t), t, d)


def g_verg10000(rng):
    """Getallen tot 10 000 ordenen: twee getallen die dicht bij elkaar liggen."""
    a = rng.randint(1000, 9999)
    pos = rng.choice([1, 10, 100])
    b = a + pos * rng.choice([-3, -2, -1, 1, 2, 3])
    if not 1000 <= b <= 9999: b = a - (b - a)
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, "omcirkel de grootste")
        c.setFont(FONTB, 15)
        c.drawCentredString(x + CELL_W * 0.29, y + ch / 2 - 4 * mm, str(a))
        c.drawCentredString(x + CELL_W * 0.71, y + ch / 2 - 4 * mm, str(b))
    def r(c, x, y, ch):
        answer_ring(c, x + CELL_W * (0.29 if a > b else 0.71), y + ch / 2 - 1.8 * mm, 14 * mm, 9 * mm)
    return Item(("vg", a, b), max(a, b), d, ans=[], ans_draw=r, ans_text=f"{max(a, b)} omcirkelen")


def g_cijferwaarde(rng):
    """De waarde van een cijfer in een getal tot 100 000."""
    digits = rng.sample(range(1, 10), 5)
    n = int("".join(map(str, digits)))
    pos = rng.randint(0, 3)              # 0 = tienduizendtal ... 3 = tiental
    dgt = digits[pos]
    val = dgt * 10 ** (4 - pos)
    s = fmt(n)
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, f"wat is de {dgt} waard?")
        c.setFont(FONTB, 13)
        wtot = c.stringWidth(s, FONTB, 13)
        cx = x + (CELL_W - wtot) / 2
        idx = 0
        for chh in s:
            w = c.stringWidth(chh, FONTB, 13)
            if chh.isdigit():
                c.setFillColor(RED if idx == pos else black)
                idx += 1
            c.drawString(cx, y + ch - 10.2 * mm, chh)
            cx += w
        c.setFillColor(black)
        box(c, x + (CELL_W - WBW) / 2, y + 1 * mm, WBW)
    return Item(("cw", n, pos), val, d)


# ------------------------------------------------------------------ vermenigvuldigen en delen

def g_deelsplits(rng):
    """52 : 4 door te splitsen"""
    n = rng.randint(2, 9)
    q = rng.choice([v for v in range(11, 99 // n + 1) if v % 10])
    return sum_item(("ds", n, q), q, [f"{n * q} : {n} =", None])


def g_deelsplits3(rng):
    """372 : 6 door te splitsen"""
    n = rng.randint(3, 9)
    q = rng.choice([v for v in range(21, 999 // n + 1) if v % 10 and n * v >= 100])
    return sum_item(("ds3", n, q), q, [f"{n * q} : {n} =", None])


def g_x10_100_1000(rng):
    f = rng.choice([10, 100, 1000])
    a = rng.randint(2, 99 if f < 1000 else 99)
    if a % 10 == 0: a += rng.randint(1, 9)
    box_ = WIDE if a * f >= 1000 else None
    return sum_item(("xf", a, f), a * f, [f"{a} × {fmt(f)} =", box_])


def g_delen10_100_1000(rng):
    f = rng.choice([10, 100, 1000])
    q = rng.randint(2, 99)
    n = q * f
    return sum_item(("df", q, f), q, [f"{fmt(n)} : {fmt(f)} =", None])


def g_xronde(rng):
    """3 × 400 / 6 × 2000"""
    a, b, k = rng.randint(2, 9), rng.randint(2, 9), rng.choice([1, 2, 2, 3])
    m = b * 10 ** k
    return sum_item(("xr", a, m), a * m, [f"{a} × {fmt(m)} =", WIDE if a * m >= 1000 else None])


def g_deelronde(rng):
    """2400 : 6 / 350 : 7"""
    n, q, k = rng.randint(2, 9), rng.randint(2, 9), rng.choice([1, 2, 2, 3])
    qq = q * 10 ** k
    return sum_item(("dr", n, qq), qq, [f"{fmt(n * qq)} : {n} =", WIDE if qq >= 1000 else None])


def g_deelgeheel(rng):
    """Een deel van een geheel: ¾ van 24"""
    d_ = rng.choice([2, 3, 4, 5, 6, 8, 10])
    nn = rng.choice([v for v in range(1, d_) if gcd(v, d_) == 1])
    k = rng.randint(2, 10)
    whole = d_ * k
    def d(c, x, y, ch):
        mid = y + ch / 2 - 1 * mm
        fx = x + 6 * mm
        c.setFont(FONTB, 11)
        c.drawCentredString(fx, mid + 1.4 * mm, str(nn))
        c.setLineWidth(0.9); c.line(fx - 2.4 * mm, mid + 0.6 * mm, fx + 2.4 * mm, mid + 0.6 * mm)
        c.drawCentredString(fx, mid - 3.6 * mm, str(d_))
        c.setFont(FONT, 13)
        c.drawString(x + 9.5 * mm, mid - 1.5 * mm, f"van {whole} =")
        box(c, x + CELL_W - BW - 1.5 * mm, mid - 3.9 * mm)
    return Item(("dg", nn, d_, whole), nn * k, d)


# ------------------------------------------------------------------ meten

UNITS = {"m": 1000, "dm": 100, "cm": 10, "mm": 1}

def g_lengte_omzet(rng):
    """Lengtematen omzetten: m, dm, cm, mm"""
    big, small = rng.choice([("m", "cm"), ("m", "dm"), ("dm", "cm"), ("cm", "mm"), ("m", "mm"), ("dm", "mm")])
    ratio = UNITS[big] // UNITS[small]
    a = rng.randint(1, 9) if ratio < 1000 else rng.randint(1, 5)
    if rng.random() < 0.6:
        return text_item(("lo", a, big, small), a * ratio, [f"{a} {big} =", None if a * ratio < 1000 else WIDE, small])
    return text_item(("lo2", a, big, small), a, [f"{a * ratio} {small} =", None, big])


def g_kg(rng):
    v = rng.choice([0, 1, 2, 3, 4])
    a = rng.randint(1, 9)
    if v == 0: return text_item(("kg0", a), 1000 * a, [f"{a} kg =", WIDE, "g"], norange=True)
    if v == 1: return text_item(("kg1", a), 1000 * a + 500, [f"{a},5 kg =", WIDE, "g"], norange=True)
    if v == 2: return text_item(("kg2", a), a, [f"{1000 * a} g =", None, "kg"])
    if v == 3:
        q = rng.choice([25, 75])
        return text_item(("kg3", a, q), 1000 * a + 10 * q, [f"{a},{q} kg =", WIDE, "g"], norange=True)
    fr, val = rng.choice([("½", 500), ("¼", 250), ("¾", 750)])
    return text_item(("kg4", fr), val, [f"{fr} kg =", None, "g"])


def g_liter(rng):
    v = rng.choice([0, 1, 2, 3])
    a = rng.randint(1, 9)
    if v == 0: return text_item(("l0", a), 1000 * a, [f"{a} l =", WIDE, "ml"], norange=True)
    if v == 1: return text_item(("l1", a), 1000 * a + 500, [f"{a},5 l =", WIDE, "ml"], norange=True)
    if v == 2: return text_item(("l2", a), a, [f"{1000 * a} ml =", None, "l"])
    fr, val = rng.choice([("½", 500), ("¼", 250), ("¾", 750)])
    return text_item(("l3", fr), val, [f"{fr} l =", None, "ml"])


def g_opp_ruitjes(rng):
    """Oppervlakte in cm² met ruitjes (1 hokje = 1 cm²)."""
    w, h = rng.randint(3, 7), rng.randint(2, 4)
    cells = {(i, j) for i in range(w) for j in range(h)}
    if rng.random() < 0.55:      # L-vorm: hoek eraf
        cw, chh = rng.randint(1, w - 2), rng.randint(1, h - 1)
        corner = rng.choice(["tl", "tr", "bl", "br"])
        for i in range(cw):
            for j in range(chh):
                ii = i if corner in ("tl", "bl") else w - 1 - i
                jj = j if corner in ("bl", "br") else h - 1 - j
                cells.discard((ii, jj))
    area = len(cells)
    def d(c, x, y, ch):
        u = 2.3 * mm
        gx, gy = x + 2.5 * mm, y + (ch - 5 * u) / 2 - 1 * mm
        c.setLineWidth(0.25); c.setStrokeColor(HexColor("#b5b5b5"))
        for i in range(9):
            c.line(gx + i * u, gy, gx + i * u, gy + 5 * u)
        for j in range(6):
            c.line(gx, gy + j * u, gx + 8 * u, gy + j * u)
        ox, oy = (8 - w) // 2, (5 - h) // 2
        c.setFillColor(HexColor("#9ed3ef")); c.setStrokeColor(black); c.setLineWidth(0.4)
        for (i, j) in cells:
            c.rect(gx + (ox + i) * u, gy + (oy + j) * u, u, u, stroke=0, fill=1)
        c.setFillColor(black)
        draw_sq(c, x + 7 * mm + CELL_W / 2, y + ch - 3 * mm, "1 hokje = 1 cm", 6.5, "center", GREY)
        box(c, x + 22.5 * mm, y + ch / 2 - 5 * mm, 8.5 * mm, BH)
        draw_sq(c, x + 31.6 * mm, y + ch / 2 - 2.6 * mm, "cm", 9)
    return Item(("or", tuple(sorted(cells))), area, d)


def _rect_item(key, a, b, unit, kind):
    ans = 2 * (a + b) if kind == "omtrek" else a * b
    sq = kind != "omtrek"
    def d(c, x, y, ch):
        rw = 6 * mm + min(a, 20) * 0.62 * mm
        rh = 3.5 * mm + min(b, 12) * 0.55 * mm
        rx, ry = x + 4.5 * mm, y + 3 * mm
        c.setLineWidth(0.9); c.setStrokeColor(black)
        c.setFillColor(HexColor("#e8f4fb")); c.rect(rx, ry, rw, rh, stroke=1, fill=1)
        c.setFillColor(black); c.setFont(FONT, 7)
        c.drawCentredString(rx + rw / 2, ry + rh + 1 * mm, f"{a} {unit}")
        c.saveState(); c.translate(rx - 1 * mm, ry + rh / 2); c.rotate(90)
        c.drawCentredString(0, 0, f"{b} {unit}"); c.restoreState()
        c.setFont(FONT, 7.5)
        c.drawCentredString(x + 30 * mm, y + ch - 6 * mm, kind)
        box(c, x + 24.5 * mm, y + ch / 2 - 6 * mm, 11 * mm, BH)
        if sq:
            draw_sq(c, x + 30 * mm, y + 1.2 * mm, unit, 7.5, "center")
        else:
            c.setFont(FONT, 7.5); c.drawCentredString(x + 30 * mm, y + 1.2 * mm, unit)
    return Item(key, ans, d)


def g_omtrekF(rng):
    a, b = rng.randint(6, 25), rng.randint(3, 14)
    if a == b: a += 1
    return _rect_item(("of", a, b), a, b, "cm", "omtrek")


def g_oppF(rng):
    a, b = rng.randint(4, 15), rng.randint(2, 9)
    if a == b: a += 1
    unit = "m" if rng.random() < 0.3 else "cm"
    return _rect_item(("af", a, b, unit), a, b, unit, "oppervlakte")


# ------------------------------------------------------------------ geld

def g_terug_groot(rng):
    pay = rng.choice([50, 100, 100, 200, 500])
    cost = rng.randint(pay // 5, pay - 1)
    def d(c, x, y, ch):
        c.setFont(FONT, 8.5); c.setFillColor(black)
        c.drawString(x + 3 * mm, y + ch - 6.5 * mm, f"Het kost € {cost}.")
        c.drawString(x + 3 * mm, y + ch - 10.5 * mm, f"Je betaalt € {pay}.")
        c.setFont(FONT, 9)
        c.drawString(x + 3 * mm, y + 3.6 * mm, "Terug: €")
        box(c, x + 17.5 * mm, y + 1.2 * mm, 11 * mm)
    return Item(("tg", pay, cost), pay - cost, d)


def g_schatten(rng):
    """Schatten hoeveel iets kost: bedragen dicht bij hele euro's."""
    def price():
        e = rng.randint(1, 12)
        c_ = rng.choice([95, 98, 99, 90, 5, 10, 2])
        if c_ >= 90:
            return e, c_, e + 1
        return e, c_, e
    if rng.random() < 0.7:
        (e1, c1, r1), (e2, c2, r2) = price(), price()
        top = f"€ {e1},{c1:02d} + € {e2},{c2:02d}"
        ans = r1 + r2; key = ("sc", e1, c1, e2, c2)
    else:
        k = rng.randint(2, 5); e1, c1, r1 = price()
        top = f"{k} × € {e1},{c1:02d}"
        ans = k * r1; key = ("sck", k, e1, c1)
    return twoline(key, ans, top, ["ongeveer €", None], 10)


# ------------------------------------------------------------------ tijd

NUMW = ["twaalf", "een", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen", "tien", "elf", "twaalf"]

def time_words(h, m):
    """h 1-12, m veelvoud van 5 -> Nederlandse kloktijd in woorden."""
    nxt = NUMW[h % 12 + 1]
    cur = NUMW[h]
    table = {0: f"{cur} uur", 5: f"vijf over {cur}", 10: f"tien over {cur}", 15: f"kwart over {cur}",
             20: f"tien voor half {nxt}", 25: f"vijf voor half {nxt}", 30: f"half {nxt}",
             35: f"vijf over half {nxt}", 40: f"tien over half {nxt}", 45: f"kwart voor {nxt}",
             50: f"tien voor {nxt}", 55: f"vijf voor {nxt}"}
    return table[m]


def _hm_boxes(c, bx, by):
    box(c, bx, by, 7 * mm, BH)
    c.setFont(FONTB, 13); c.drawCentredString(bx + 8.2 * mm, by + 2.2 * mm, ":")
    box(c, bx + 9.4 * mm, by, 7 * mm, BH)


def g_minuten(rng):
    """Minuten op een klok met wijzers -> digitale tijd."""
    h = rng.randint(1, 12); m = rng.choice([v for v in range(1, 60) if v % 5])
    def d(c, x, y, ch):
        clock_face(c, x + 10.5 * mm, y + ch / 2, (h % 12) + m / 60, m, ticks=True)
        _hm_boxes(c, x + 20.5 * mm, y + ch / 2 - 4 * mm)
    return Item(("mi", h, m), h * 100 + m, d, norange=True, ans=[str(h), f"{m:02d}"], ans_text=f"{h}:{m:02d}")


def g_wijzers_min(rng):
    """Minuten op een digitale klok -> wijzers tekenen."""
    h = rng.randint(1, 12); m = rng.choice([v for v in range(1, 60) if v % 5])
    def d(c, x, y, ch):
        label(c, x + 5 * mm, y + ch - 3 * mm, "teken de wijzers")
        clock_face(c, x + 10.5 * mm, y + ch / 2 - 1 * mm, 0, 0, hands=False, ticks=True)
        _digital(c, x + 21.5 * mm, y + ch / 2 - 5 * mm, f"{h}:{m:02d}")
    def r(c, x, y, ch):
        answer_hands(c, x + 10.5 * mm, y + ch / 2 - 1 * mm, h, m)
    return Item(("wm", h, m), h * 100 + m, d, norange=True, ans=[], ans_draw=r, ans_text=f"wijzers op {h}:{m:02d}")


def g_tijdwoorden(rng):
    """Kloktijden bij elkaar zoeken: woorden -> digitaal (soms 24-uurs)."""
    h = rng.randint(1, 12); m = rng.choice(range(0, 60, 5))
    words = time_words(h, m)
    if rng.random() < 0.35 and h <= 5:
        top = words + " 's middags"
        hh = h + 12
    else:
        top = words; hh = h
    def d(c, x, y, ch):
        size = 8.5
        while c.stringWidth(top, FONT, size) > CELL_W - 3 * mm: size -= 0.5
        c.setFont(FONT, size); c.drawCentredString(x + CELL_W / 2, y + ch - 7 * mm, top)
        _hm_boxes(c, x + (CELL_W - 16.4 * mm) / 2, y + 1.5 * mm)
    return Item(("tw", hh, m), hh * 100 + m, d, norange=True, ans=[str(hh), f"{m:02d}"], ans_text=f"{hh}:{m:02d}")


def _hm(t):
    return f"{t // 60}:{t % 60:02d}"


def mk_duur(step, name):
    """Uitrekenen hoelang iets duurt (stap 5 of 1 minuut), of hoe laat het dan is."""
    def g(rng):
        start = rng.randint(7 * 60, 16 * 60) // step * step
        dur = rng.randint(max(2, 10 // step), 95 // step) * step
        end = start + dur
        if rng.random() < 0.65:
            return twoline((name, start, dur), dur, f"van {_hm(start)} tot {_hm(end)}", [None, "minuten"], 10)
        it = twoline((name + "e", start, dur), (end // 60) * 100 + end % 60,
                     f"{_hm(start)} + {dur} minuten", ["", None, ":", None], 10, norange=True,
                     ans=[str(end // 60), f"{end % 60:02d}"], ans_text=_hm(end))
        return it
    return g


# ------------------------------------------------------------------ grafieken

def _chart_axes(c, x0, y0, wch, hch, smax, s):
    c.setFont(FONT, 5.2); c.setLineWidth(0.25); c.setStrokeColor(HexColor("#bdbdbd"))
    n = smax // s
    for i in range(n + 1):
        yy = y0 + hch * i / n
        c.line(x0, yy, x0 + wch, yy)
        c.setFillColor(black); c.drawRightString(x0 - 0.7 * mm, yy - 0.6 * mm, str(i * s))
    c.setStrokeColor(black); c.setLineWidth(0.6)
    c.line(x0, y0, x0, y0 + hch); c.line(x0, y0, x0 + wch, y0)


def g_staaf(rng):
    """Moeilijke staafgrafiek: schaal in stappen, waarde tussen de lijnen."""
    s = rng.choice([10, 20, 50, 100])
    smax = 4 * s
    vals = [rng.randint(1, 8) * s // 2 for _ in range(3)]
    ask = rng.randrange(3)
    if vals[ask] % s == 0:
        vals[ask] = vals[ask] - s // 2 if vals[ask] > s // 2 else vals[ask] + s // 2
    names = "ABC"
    def d(c, x, y, ch):
        x0, y0, wch, hch = x + 7.5 * mm, y + 3.6 * mm, 15 * mm, ch - 6.6 * mm
        _chart_axes(c, x0, y0, wch, hch, smax, s)
        bw = 3 * mm
        for i, v in enumerate(vals):
            bx = x0 + 1.5 * mm + i * 4.6 * mm
            c.setFillColor(RED if i == ask else ACCENT)
            c.rect(bx, y0, bw, hch * v / smax, stroke=0, fill=1)
            c.setFillColor(black); c.setFont(FONT, 5.5)
            c.drawCentredString(bx + bw / 2, y0 - 2.5 * mm, names[i])
        c.setFont(FONT, 8.5)
        c.drawString(x + 25.5 * mm, y + ch / 2 + 2 * mm, f"{names[ask]} =")
        box(c, x + 25 * mm, y + ch / 2 - 7.5 * mm, 11 * mm, BH)
    return Item(("st", s, tuple(vals), ask), vals[ask], d)


def g_lijngrafiek(rng):
    """Een lijngrafiek aflezen (temperatuur door de week)."""
    s = rng.choice([2, 10, 20])
    smax = 4 * s
    vals = [rng.randint(0, 8) * s // 2 for _ in range(4)]
    days = ["ma", "di", "wo", "do"]
    ask = rng.randrange(4)
    def d(c, x, y, ch):
        x0, y0, wch, hch = x + 6.5 * mm, y + 3.6 * mm, 16.5 * mm, ch - 6.6 * mm
        _chart_axes(c, x0, y0, wch, hch, smax, s)
        pts = [(x0 + 1.8 * mm + i * 4.3 * mm, y0 + hch * v / smax) for i, v in enumerate(vals)]
        c.setStrokeColor(ACCENT); c.setLineWidth(1)
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            c.line(ax, ay, bx, by)
        for i, (px, py) in enumerate(pts):
            c.setFillColor(RED if i == ask else ACCENT); c.circle(px, py, 0.7 * mm, stroke=0, fill=1)
            c.setFillColor(black); c.setFont(FONT, 5)
            c.drawCentredString(px, y0 - 2.5 * mm, days[i])
        c.setFont(FONT, 8.5)
        c.drawString(x + 25.5 * mm, y + ch / 2 + 2 * mm, f"{days[ask]} =")
        box(c, x + 25 * mm, y + ch / 2 - 7.5 * mm, 11 * mm, BH)
    return Item(("lg", s, tuple(vals), ask), vals[ask], d)


TYPES = {
    # herhaling
    "tot20": (g_tot20, "6 + 8 / 14 – 8"),
    "over": (g_over, "35 + 8 / 74 – 8"),
    "met": (g_met, "35 + 27 / 73 – 45"),
    "honderd": (g_honderd, "152 + 230 / 763 – 340"),
    "deeltal": (g_deeltal, "120 : 3 / 250 : 5"),
    "xsplits": (g_xsplits, "6 × 32"),
    # tafels
    "tafel6789": (mk_tafel_h([6, 7, 8, 9], "t69"), "tafels 6–9 door elkaar"),
    "alletafels": (mk_tafel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "tall"), "alle tafels door elkaar"),
    "deel6789": (mk_deel_h([6, 7, 8, 9], "d69"), "deeltafels 6–9 door elkaar"),
    "alledeel": (mk_deel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "dall"), "alle deeltafels door elkaar"),
    # getalbegrip
    "sprong1000": (seq_big(0, 10000, [1000, 100], "sb1"), "sprongen van 1000 en 100"),
    "splits10000": (g_splits10000, "getallen tot 10 000 splitsen"),
    "lijn10000": (g_lijn10000, "getallenlijn tot 10 000"),
    "verg10000": (g_verg10000, "getallen tot 10 000 ordenen"),
    "sprong_groot": (seq_big(10000, 100000, [10000, 1000, 500], "sb2", 500), "sprongen van 10 000, 1000 en 500"),
    "lijn100000": (g_lijn100000, "getallenlijn tot 100 000"),
    "cijferwaarde": (g_cijferwaarde, "waarde van een cijfer"),
    # bewerkingen
    "deelsplits": (g_deelsplits, "52 : 4 (splitsen)"),
    "deelsplits3": (g_deelsplits3, "372 : 6 (splitsen)"),
    "x10_100_1000": (g_x10_100_1000, "× 10, 100 en 1000"),
    "delen10_100_1000": (g_delen10_100_1000, ": 10, 100 en 1000"),
    "xronde": (g_xronde, "3 × 400 / 6 × 2000"),
    "deelronde": (g_deelronde, "2400 : 6 / 350 : 7"),
    "deelgeheel": (g_deelgeheel, "deel van een geheel (¾ van 24)"),
    # meten
    "lengte": (g_lengte_omzet, "lengtematen m, dm, cm, mm"),
    "kg": (g_kg, "kg en g"),
    "liter": (g_liter, "l en ml"),
    "opp_ruitjes": (g_opp_ruitjes, "oppervlakte met ruitjes"),
    "omtrekF": (g_omtrekF, "omtrek rechthoek (formule)"),
    "oppF": (g_oppF, "oppervlakte rechthoek (formule)"),
    # geld
    "terug_groot": (g_terug_groot, "groot bedrag terugkrijgen"),
    "schatten": (g_schatten, "schatten hoeveel iets kost"),
    # tijd
    "minuten": (g_minuten, "minuten (wijzers)"),
    "wijzers_min": (g_wijzers_min, "wijzers tekenen (minuten)"),
    "tijdwoorden": (g_tijdwoorden, "kloktijden bij elkaar zoeken"),
    "duur5": (mk_duur(5, "du5"), "hoelang duurt het (5 min.)"),
    "duur1": (mk_duur(1, "du1"), "hoelang duurt het (1 min.)"),
    # grafieken
    "staaf": (g_staaf, "staafgrafiek aflezen"),
    "lijngrafiek": (g_lijngrafiek, "lijngrafiek aflezen"),
}

PLAN = [
    ((1, 2),   "Opstart: herhaling groep 5",            ["alletafels", "alledeel", "met", "honderd"], ["tot20", "over", "deeltal"]),
    ((3, 4),   "Tafels 6–9 vlot, tot 10 000",           ["tafel6789", "deel6789", "sprong1000", "splits10000"], ["met", "honderd", "alletafels"]),
    ((5, 6),   "Getallen tot 10 000, 52 : 4",           ["lijn10000", "splits10000", "deelsplits", "alletafels"], ["met", "alledeel", "xsplits"]),
    ((7, 8),   "Lengtematen en kloktijden",             ["lengte", "minuten", "tijdwoorden", "deelsplits"], ["alletafels", "alledeel", "met"]),
    ((9, 10),  "Ordenen, × en : 10, 100, 1000",         ["verg10000", "x10_100_1000", "delen10_100_1000", "tot20"], ["lijn10000", "met", "lengte"]),
    ((11, 12), "3 × 400 en 2400 : 6",                   ["xronde", "deelronde", "x10_100_1000", "deelsplits3"], ["alletafels", "alledeel", "tot20"]),
    ((13, 14), "Geld terug en tijdsduur",               ["terug_groot", "duur5", "deelsplits3", "xronde"], ["delen10_100_1000", "verg10000", "met"]),
    ((15, 16), "Herhaling blok 3–4",                    ["staaf", "deelronde", "xronde", "duur5", "terug_groot"], ["tot20", "deelsplits3"]),
    ((17, 18), "Over het tiental vlot, kg en liter",    ["over", "kg", "liter", "met"], ["deelsplits3", "xronde", "alletafels"]),
    ((19, 20), "Oppervlakte, tijdsduur op de minuut",   ["opp_ruitjes", "duur1", "kg", "liter"], ["over", "deelronde", "met"]),
    ((21, 22), "Lijngrafiek, wijzers op de minuut",     ["lijngrafiek", "opp_ruitjes", "duur1", "wijzers_min"], ["kg", "liter", "staaf"]),
    ((23, 24), "Herhaling blok 5–6",                    ["over", "kg", "liter", "opp_ruitjes", "duur1"], ["lijngrafiek", "met"]),
    ((25, 26), "Getallen tot 100 000",                  ["sprong_groot", "cijferwaarde", "alletafels", "alledeel"], ["over", "xronde", "deelronde"]),
    ((27, 28), "Deel van een geheel",                   ["deelgeheel", "lijn100000", "cijferwaarde", "alledeel"], ["met", "kg", "duur1"]),
    ((29, 30), "Omtrek en oppervlakte (formule)",       ["omtrekF", "oppF", "deelgeheel", "alletafels"], ["sprong_groot", "liter", "deelsplits3"]),
    ((31, 32), "Herhaling blok 7–8, schatten",          ["schatten", "oppF", "deelgeheel", "alletafels", "alledeel"], ["cijferwaarde", "omtrekF"]),
    ((33, 34), "Extra: rekenen tot 100 en 1000",        ["met", "honderd", "deelsplits3", "xsplits"], ["tot20", "over", "lengte"]),
    ((35, 36), "Extra: getallen tot 100 000",           ["lijn100000", "cijferwaarde", "sprong_groot", "xronde"], ["deelronde", "met", "schatten"]),
    ((37, 38), "Extra: tafels en deeltafels vlot",      ["alletafels", "alledeel", "met", "deelgeheel"], ["over", "opp_ruitjes", "tijdwoorden"]),
    ((39, 40), "Jaarafsluiting: alles door elkaar",     ["met", "alletafels", "alledeel", "deelsplits3", "deelgeheel"], ["omtrekF", "kg", "schatten"]),
]

INTRO = (
    "Eén pagina per week: <b>paginanummer = weeknummer</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook: 10 opdrachten (± 5 minuten), "
    "ongeveer 7 focus en 3 herhaling. Rekenmuurtje: blok 2/4/6/8 = week 8/16/24/32. Week 1–2: herhaling groep 5. "
    "<b>Rekenen tot 100 uit het hoofd (35 + 27 / 73 – 45) blijft het hele jaar terugkomen.</b> "
    "Week 33–40 zijn extra. Tijden schrijven kinderen digitaal op (uur : minuten); bij <i>'s middags</i> in 24-uursnotatie. "
    "Grote getallen staan met een spatie (45 000), zoals in de methode."
)
