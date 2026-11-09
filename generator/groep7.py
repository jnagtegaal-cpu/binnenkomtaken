from fractions import Fraction as F
from math import gcd
from engine import *
from groep4 import g_tot20, g_over, g_met
from groep5 import _digital
from groep6 import (mk_tafel_h, mk_deel_h, g_deelsplits3, g_xronde, g_deelronde, g_deelgeheel,
                    g_lijn100000, twoline, _chart_axes)

D = fmt_dec  # korte naam: Fraction/int -> "3,25"

# ------------------------------------------------------------------ hulpjes

def draw_frac(c, cx, ymid, n, d, size=11, bold=True, bw=6 * mm):
    """Breuk gecentreerd op cx. n/d = str of None (= invulvakje)."""
    f = FONTB if bold else FONT
    c.setFillColor(black)
    w = frac_w(c, n, d, size, bw)
    c.setLineWidth(0.9); c.setStrokeColor(black)
    c.line(cx - w / 2, ymid, cx + w / 2, ymid)
    if n is None:
        box(c, cx - bw / 2, ymid + 0.8 * mm, bw, 6.4 * mm)
    else:
        c.setFont(f, size); c.drawCentredString(cx, ymid + 1.0 * mm, n)
    if d is None:
        box(c, cx - bw / 2, ymid - 7.2 * mm, bw, 6.4 * mm)
    else:
        c.setFont(f, size); c.drawCentredString(cx, ymid - 0.9 * mm - size * 0.72, d)
    return w

def frac_w(c, n, d, size=11, bw=6 * mm):
    wn = bw if n is None else c.stringWidth(n, FONTB, size)
    wd = bw if d is None else c.stringWidth(d, FONTB, size)
    return max(wn, wd) + 1.4 * mm


def frac_row(c, x, ymid, parts, size=11):
    """parts: ('f', n, d) breuk, of str tekst. Gecentreerd in de cel."""
    ws = []
    for p in parts:
        ws.append(frac_w(c, p[1], p[2], size) if isinstance(p, tuple) else c.stringWidth(p, FONT, 12))
    gap = 1.3 * mm
    total = sum(ws) + gap * (len(parts) - 1)
    if total > CELL_W - 1.5 * mm:
        PROBLEMS.append(f"breukrij te breed: {parts}")
    cx = x + (CELL_W - total) / 2
    for p, w in zip(parts, ws):
        if isinstance(p, tuple):
            draw_frac(c, cx + w / 2, ymid, p[1], p[2], size)
        else:
            c.setFont(FONT, 12); c.setFillColor(black); c.drawString(cx, ymid - 1.4 * mm, p)
        cx += w + gap


def with_check(it, fn):
    it.check = fn
    return it


# ------------------------------------------------------------------ grote getallen

def g_cijfer1M(rng):
    """De waarde van een cijfer in een getal tot 1 000 000."""
    digits = rng.sample(range(1, 10), 6)
    n = int("".join(map(str, digits)))
    pos = rng.randint(0, 3)
    dgt = digits[pos]; val = dgt * 10 ** (5 - pos)
    s = fmt(n)
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, f"wat is de {dgt} waard?")
        size = 12.5
        cx = x + (CELL_W - c.stringWidth(s, FONTB, size)) / 2
        idx = 0
        for chh in s:
            w = c.stringWidth(chh, FONTB, size)
            if chh.isdigit():
                c.setFillColor(RED if idx == pos else black); idx += 1
            c.setFont(FONTB, size); c.drawString(cx, y + ch - 10.2 * mm, chh); cx += w
        c.setFillColor(black)
        box(c, x + (CELL_W - 17 * mm) / 2, y + 1 * mm, 17 * mm)
    it = Item(("c1m", n, pos), val, d)
    return with_check(it, lambda: (int(str(n)[pos]) == dgt and val == int(str(n)[pos] + "0" * (5 - pos)), "cijferwaarde"))

def g_nullen10000(rng):
    """Optel- en aftreksommen met nullen tot 10 000: 4700 + 2800 / 8300 – 4600"""
    if rng.random() < 0.5:
        a = rng.randint(11, 79) * 100; b = rng.randint(11, 99 - a // 100) * 100
        if a % 1000 == 0: a += 100
        return sum_item(("n+", a, b), a + b, [f"{a} + {b} =", WIDE])
    a = rng.randint(30, 99) * 100; b = rng.randint(11, a // 100 - 5) * 100
    return sum_item(("n-", a, b), a - b, [f"{a} – {b} =", WIDE])


def g_groot(rng):
    """Sommen met grote getallen: 35 000 + 48 000 / 120 000 – 45 000 / 45 300 + 6800"""
    v = rng.choice([0, 1, 2, 3])
    if v == 0:
        a, b = rng.randint(12, 95) * 1000, rng.randint(12, 95) * 1000
        return sum_item(("g0", a, b), a + b, [f"{fmt(a)} + {fmt(b)} =", WIDE])
    if v == 1:
        a = rng.randint(100, 950) * 1000; b = rng.randint(11, a // 1000 - 10) * 1000
        return sum_item(("g1", a, b), a - b, [f"{fmt(a)} – {fmt(b)} =", WIDE])
    if v == 2:
        a = rng.randint(10, 89) * 1000 + rng.randint(1, 9) * 100; b = rng.randint(1, 9) * 1000 + rng.randint(1, 9) * 100
        return sum_item(("g2", a, b), a + b, [f"{fmt(a)} + {fmt(b)} =", WIDE])
    a = rng.randint(20, 99) * 1000 + rng.randint(1, 9) * 100; b = rng.randint(1, 9) * 1000 + rng.randint(1, 9) * 100
    return sum_item(("g3", a, b), a - b, [f"{fmt(a)} – {fmt(b)} =", WIDE])

def _conv(rng, units, key, span=3):
    """units: dict naam -> factor t.o.v. kleinste eenheid; geordend van groot naar klein."""
    names = list(units)
    i = rng.randrange(len(names) - 1)
    j = rng.randint(i + 1, min(len(names) - 1, i + span))
    big, small = names[i], names[j]
    ratio = units[big] // units[small]
    mode = rng.choice([0, 0, 1, 2])
    if mode == 0:      # groot -> klein, heel getal
        num = F(rng.randint(1, 9)); lu, ru = big, small
    elif mode == 1:    # groot -> klein, kommagetal
        num = F(rng.randint(11, 95), 10)
        if num.denominator == 1: num += F(1, 2)
        lu, ru = big, small
    else:              # klein -> groot
        num = F(rng.randint(2, 95) * max(1, ratio // 10))
        if num % ratio == 0: num += max(1, ratio // 2)
        lu, ru = small, big
    ans = num * units[lu] / units[ru]
    top = f"{D(num)} {lu} ="
    it = text_item((key, top, ru), ans, [top, WIDE if (ans >= 100 or ans.denominator != 1) else None, ru])
    return with_check(it, lambda: (F(top.split(" ")[0].replace("\u00a0", "").replace(",", ".")) * units[lu] == ans * units[ru], f"omrekenen {top} {ans} {ru}"))

LENGTE = {"km": 1000000, "hm": 100000, "dam": 10000, "m": 1000, "dm": 100, "cm": 10, "mm": 1}
LITER = {"hl": 100000, "l": 1000, "dl": 100, "cl": 10, "ml": 1}
GEWICHT = {"ton": 1000000000, "kg": 1000000, "g": 1000, "mg": 1}

def g_lengte_alle(rng): return _conv(rng, LENGTE, "len", 3)
def g_liter_alle(rng): return _conv(rng, LITER, "lit", 2)


def g_gewicht(rng):
    # ton -> kg, kg -> g, g -> mg (en terug); geen ton -> mg
    pairs = [("ton", "kg"), ("kg", "g"), ("g", "mg"), ("kg", "g"), ("ton", "kg")]
    big, small = rng.choice(pairs)
    sub = {big: GEWICHT[big], small: GEWICHT[small]}
    return _conv(rng, sub, "gew")


def g_dm3(rng):
    """1 liter = 1 dm³ ; 1 ml = 1 cm³"""
    v = rng.choice(range(6))
    a = rng.randint(2, 9)
    opts = [
        (["1 dm³ =", None, "l"], 1),
        ([f"{a} l =", None, "dm³"], a),
        ([f"{a} dm³ =", WIDE, "cm³"], 1000 * a),
        ([f"{a * 50} cm³ =", WIDE, "ml"], a * 50),
        ([f"{a * 500} ml =", WIDE, "cm³"], a * 500),
        ([f"{a} dm³ =", WIDE, "ml"], 1000 * a),
    ]
    parts, ans = opts[v]
    return text_item(("dm3", v, a), ans, parts)


def g_samenhang(rng):
    """De samenhang tussen lengte-, inhouds- en gewichtsmaten (water)."""
    a = rng.randint(2, 9)
    opts = [
        ("1 liter water weegt", ["", None, "kg"], 1),
        (f"{a} liter water weegt", ["", None, "kg"], a),
        (f"{a * 100} ml water weegt", ["", WIDE, "g"], a * 100),
        (f"{a} dm³ water weegt", ["", None, "kg"], a),
        (f"{a * 250} cm³ water weegt", ["", WIDE, "g"], a * 250),
        (f"{a} kg water is", ["", None, "liter"], a),
    ]
    top, bottom, ans = rng.choice(opts)
    def d(c, x, y, ch):
        c.setFillColor(black)
        w = txt_w(c, top, FONT, 9.5)
        draw_txt(c, x + (CELL_W - w) / 2, y + ch - 7.2 * mm, top, FONT, 9.5)
        text_with_boxes(c, x, y + 3.4 * mm, bottom, 12)
    return Item(("sh", top), ans, d)


# ------------------------------------------------------------------ breuken

def g_breukverg(rng):
    """Breuken vergelijken door ze gelijknamig te maken."""
    while True:
        d1, d2 = rng.sample([2, 3, 4, 5, 6, 8, 10, 12], 2)
        n1 = rng.randint(1, d1 - 1); n2 = rng.randint(1, d2 - 1)
        f1, f2 = F(n1, d1), F(n2, d2)
        if gcd(n1, d1) == 1 and gcd(n2, d2) == 1 and f1 != f2 and abs(f1 - f2) <= F(1, 3):
            break
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, "omcirkel de grootste")
        ym = y + ch / 2 - 1 * mm
        draw_frac(c, x + CELL_W * 0.32, ym, str(n1), str(d1), 13)
        draw_frac(c, x + CELL_W * 0.68, ym, str(n2), str(d2), 13)
    def r(c, x, y, ch):
        answer_ring(c, x + CELL_W * (0.32 if f1 > f2 else 0.68), y + ch / 2 - 1 * mm, 10 * mm, 13 * mm)
    big = (n1, d1) if f1 > f2 else (n2, d2)
    return Item(("bv", n1, d1, n2, d2), max(f1, f2), d, ans=[], ans_draw=r, ans_text=f"{big[0]}/{big[1]} omcirkelen")


def g_vereenvoudig(rng):
    """Kale breuken vereenvoudigen: 6/8 = 3/4"""
    dd = rng.choice([3, 4, 5, 6, 7, 8, 9, 10])
    nn = rng.choice([v for v in range(1, dd) if gcd(v, dd) == 1])
    k = rng.choice([2, 3, 4, 5])
    if dd * k > 60: k = 2
    def d(c, x, y, ch):
        frac_row(c, x, y + ch / 2 - 0.5 * mm, [("f", str(nn * k), str(dd * k)), "=", ("f", None, None)], 12)
    it = Item(("vv", nn, dd, k), F(nn, dd), d, ans=[str(nn), str(dd)], ans_text=f"{nn}/{dd}")
    return with_check(it, lambda: (F(nn * k, dd * k) == F(nn, dd) and gcd(nn, dd) == 1, "vereenvoudigen"))


def g_breukplus(rng):
    """Gelijknamige breuken optellen en aftrekken."""
    dd = rng.randint(3, 12)
    if rng.random() < 0.5:
        a = rng.randint(1, dd - 2); b = rng.randint(1, dd - 1 - a)
        op, res = "+", F(a + b, 1)
    else:
        a = rng.randint(2, dd - 1); b = rng.randint(1, a - 1)
        op, res = "–", F(a - b, 1)
    def d(c, x, y, ch):
        frac_row(c, x, y + ch / 2 - 0.5 * mm, [("f", str(a), str(dd)), op, ("f", str(b), str(dd)), "=", ("f", None, str(dd))], 11)
    it = Item(("bp", a, b, dd, op), res, d, ans_text=f"{int(res)}/{dd}")
    return with_check(it, lambda: ((F(a, dd) + F(b, dd) if op == "+" else F(a, dd) - F(b, dd)) == F(int(res), dd), "breuksom"))


# ------------------------------------------------------------------ kommagetallen

def dfix(v, pl):
    """Kommagetal met precies pl decimalen (3,50)."""
    v = F(v)
    if pl == 0:
        return fmt(int(v))
    ip = int(v); frac_ = v - ip
    digits = str(int(frac_ * 10 ** pl)).rjust(pl, "0")
    assert F(int(frac_ * 10 ** pl), 10 ** pl) == frac_, "te veel decimalen"
    return f"{fmt(ip)},{digits}"


def rdec(rng, lo, hi, places):
    v = F(rng.randint(int(lo * 10 ** places), int(hi * 10 ** places)), 10 ** places)
    return v


def g_kommaverg(rng):
    """Kommagetallen op volgorde: verschillend aantal decimalen."""
    while True:
        ip = rng.randint(0, 9)
        a = ip + F(rng.randint(1, 9), 10)
        b = ip + F(rng.randint(1, 99), 100)
        if a != b and abs(a - b) < F(1, 5) and b.denominator == 100:
            break
    if rng.random() < 0.5: a, b = b, a
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, "omcirkel de grootste")
        c.setFont(FONTB, 15)
        c.drawCentredString(x + CELL_W * 0.29, y + ch / 2 - 4 * mm, D(a))
        c.drawCentredString(x + CELL_W * 0.71, y + ch / 2 - 4 * mm, D(b))
    def r(c, x, y, ch):
        answer_ring(c, x + CELL_W * (0.29 if a > b else 0.71), y + ch / 2 - 1.8 * mm, 13 * mm, 9 * mm)
    return Item(("kv", a, b), max(a, b), d, ans=[], ans_draw=r, ans_text=f"{D(max(a, b))} omcirkelen")


def g_kommaplus(rng):
    """Gelijk aantal cijfers achter de komma optellen en aftrekken."""
    pl = rng.choice([1, 2])
    a, b = rdec(rng, 1, 9, pl), rdec(rng, 1, 9, pl)
    if a.denominator == 1: a += F(1, 10 ** pl) * 3
    if b.denominator == 1: b += F(1, 10 ** pl) * 7
    sa, sb = dfix(a, pl), dfix(b, pl)
    if rng.random() < 0.5:
        return sum_item(("k+", a, b), a + b, [f"{sa} + {sb} =", WIDE])
    if a < b: a, b, sa, sb = b, a, sb, sa
    if a == b: a += 1; sa = dfix(a, pl)
    return sum_item(("k-", a, b), a - b, [f"{sa} – {sb} =", WIDE])


def g_kommaplus2(rng):
    """Verschillend aantal cijfers achter de komma: 3,5 + 2,75 / 6 – 1,25"""
    p1, p2 = rng.choice([(1, 2), (2, 1), (0, 2), (0, 1), (2, 3)])
    a = rdec(rng, 1, 9, p1) if p1 else F(rng.randint(2, 12))
    b = rdec(rng, 0.1, 6, p2)
    sa = D(a)
    sb = D(b)
    if rng.random() < 0.5:
        return sum_item(("kk+", sa, sb), a + b, [f"{sa} + {sb} =", WIDE])
    if a <= b:
        a = a + 6; sa = D(a)
    return sum_item(("kk-", sa, sb), a - b, [f"{sa} – {sb} =", WIDE])


def g_kommawaarde(rng):
    """De waarde van een cijfer in een kommagetal."""
    digs = rng.sample(range(1, 10), 4)
    s = f"{digs[0]},{digs[1]}{digs[2]}{digs[3]}"
    pos = rng.randint(1, 3)
    dgt = digs[pos]
    val = F(dgt, 10 ** pos)
    def d(c, x, y, ch):
        label(c, x, y + ch - 3 * mm, f"wat is de {dgt} waard?")
        size = 14
        cx = x + (CELL_W - c.stringWidth(s, FONTB, size)) / 2
        idx = 0
        for chh in s:
            w = c.stringWidth(chh, FONTB, size)
            if chh.isdigit():
                c.setFillColor(RED if idx == pos else black); idx += 1
            c.setFont(FONTB, size); c.drawString(cx, y + ch - 10.4 * mm, chh); cx += w
        c.setFillColor(black)
        box(c, x + (CELL_W - 17 * mm) / 2, y + 1 * mm, 17 * mm)
    it = Item(("kw", s, pos), val, d)
    return with_check(it, lambda: (int(s.replace(",", "")[pos]) == dgt and val * 10 ** pos == dgt, "kommawaarde"))

def g_kommax10(rng):
    """Een kommagetal vermenigvuldigen met 10, 100 en 1000"""
    f = rng.choice([10, 100, 1000])
    pl = rng.choice([1, 2, 2, 3])
    a = rdec(rng, 0.1, 99, pl)
    if a.denominator == 1: a += F(1, 10 ** pl)
    sa = D(a)
    return sum_item(("kx", sa, f), a * f, [f"{sa} × {f} =", WIDE])


def g_kommadeel10(rng):
    """Een kommagetal delen door 10, 100 en 1000"""
    f = rng.choice([10, 100, 1000])
    pl = rng.choice([0, 1, 1, 2])
    a = rdec(rng, 1, 999, pl) if pl else F(rng.randint(2, 999))
    sa = D(a)
    return sum_item(("kd", sa, f), a / f, [f"{sa} : {f} =", WIDE])


# ------------------------------------------------------------------ verhoudingen

CTX = [("pakken", "€"), ("liter", "km"), ("uur", "€"), ("kg", "€"), ("dozen", "eieren"), ("min.", "km")]

def g_vtabel(rng):
    """Zelf een verhoudingstabel invullen."""
    top_l, bot_l = rng.choice(CTX)
    r = rng.randint(2, 9)
    tops = sorted(rng.sample(range(1, 13), 3))
    bots = [t * r for t in tops]
    miss = rng.randint(1, 2); row = rng.choice([0, 1])
    ans = tops[miss] if row == 0 else bots[miss]
    def d(c, x, y, ch):
        lw, cw, rh = 9.5 * mm, 8.6 * mm, 6.6 * mm
        tx = x + (CELL_W - lw - 3 * cw) / 2
        ty = y + (ch - 2 * rh) / 2
        c.setLineWidth(0.6); c.setStrokeColor(black)
        for i, (lab, vals) in enumerate(((top_l, tops), (bot_l, bots))):
            yy = ty + (1 - i) * rh
            c.setFillColor(HexColor("#eaf5fb")); c.rect(tx, yy, lw, rh, stroke=1, fill=1)
            c.setFillColor(black); c.setFont(FONT, 6.5); c.drawCentredString(tx + lw / 2, yy + 2.2 * mm, lab)
            for j, v in enumerate(vals):
                cx_ = tx + lw + j * cw
                c.rect(cx_, yy, cw, rh, stroke=1, fill=0)
                if not (j == miss and i == row):
                    c.setFont(FONT, 11); c.drawCentredString(cx_ + cw / 2, yy + 2 * mm, str(v))
                else:
                    c.setLineWidth(1.4); c.roundRect(cx_ + 0.6 * mm, yy + 0.6 * mm, cw - 1.2 * mm, rh - 1.2 * mm, 1 * mm, stroke=1, fill=0); c.setLineWidth(0.6)
    def ad(c, x, y, ch):
        lw, cw, rh = 9.5 * mm, 8.6 * mm, 6.6 * mm
        tx = x + (CELL_W - lw - 3 * cw) / 2
        ty = y + (ch - 2 * rh) / 2
        yy = ty + (1 - row) * rh
        c.saveState(); c.setFillColor(ANSCOL); c.setFont(FONTB, 11)
        c.drawCentredString(tx + lw + miss * cw + cw / 2, yy + 2 * mm, str(ans)); c.restoreState()
    it = Item(("vt", r, tuple(tops), miss, row), ans, d, ans=[], ans_draw=ad)
    return with_check(it, lambda: (all(b == t * r for t, b in zip(tops, bots)), "verhoudingstabel"))


def g_vtaal(rng):
    """Verhoudingentaal gebruiken."""
    v = rng.choice([0, 1, 2])
    def three(l1, l2, bottom, ans, key, chk):
        def d(c, x, y, ch):
            c.setFont(FONT, 8.3); c.setFillColor(black)
            for k_, t_ in enumerate((l1, l2)):
                sz = 8.3
                while c.stringWidth(t_, FONT, sz) > CELL_W - 2.5 * mm: sz -= 0.3
                c.setFont(FONT, sz); c.drawCentredString(x + CELL_W / 2, y + ch - (5 + 4 * k_) * mm, t_)
            text_with_boxes(c, x, y + 3.4 * mm, bottom, 11)
        return with_check(Item(key, ans, d), chk)
    if v == 0:
        k = rng.randint(3, 6); tot = k * rng.randint(4, 10)
        return three(f"1 op de {k} snoepjes is rood.", f"Er zijn {tot} snoepjes.", ["rood:", None], tot // k,
                     ("vt0", k, tot), lambda: (F(tot // k, tot) == F(1, k), "verhoudingentaal"))
    if v == 1:
        a, b = rng.choice([(2, 3), (1, 2), (3, 4), (2, 5), (3, 5)])
        m = rng.randint(2, 8)
        return three(f"jongens : meisjes = {a} : {b}", f"Er zijn {a * m} jongens.", ["meisjes:", None], b * m,
                     ("vt1", a, b, m), lambda: (F(a * m, b * m) == F(a, b), "verhouding"))
    a, b = rng.choice([(1, 3), (2, 3), (1, 4), (3, 4), (2, 5)])
    m = rng.randint(2, 8)
    return three(f"{a} van de {b} kinderen fietst.", f"Er zijn {b * m} kinderen.", ["fietsers:", None], a * m,
                 ("vt2", a, b, m), lambda: (F(a * m, b * m) == F(a, b), "verhoudingentaal"))


def g_grafiekreken(rng):
    """Berekeningen maken op basis van een staafgrafiek."""
    s = rng.choice([10, 20, 50, 100])
    smax = 4 * s
    vals = [rng.randint(1, 8) * s // 2 for _ in range(3)]
    while len(set(vals)) < 3:
        vals = [rng.randint(1, 8) * s // 2 for _ in range(3)]
    i, j = rng.sample(range(3), 2)
    if rng.random() < 0.5:
        q, ans = f"{'ABC'[i]} + {'ABC'[j]} =", vals[i] + vals[j]
    else:
        if vals[i] < vals[j]: i, j = j, i
        q, ans = f"{'ABC'[i]} – {'ABC'[j]} =", vals[i] - vals[j]
    def d(c, x, y, ch):
        x0, y0, wch, hch = x + 7.5 * mm, y + 3.6 * mm, 13.5 * mm, ch - 6.6 * mm
        _chart_axes(c, x0, y0, wch, hch, smax, s)
        for k, v in enumerate(vals):
            bx = x0 + 1.2 * mm + k * 4.2 * mm
            c.setFillColor(ACCENT); c.rect(bx, y0, 2.8 * mm, hch * v / smax, stroke=0, fill=1)
            c.setFillColor(black); c.setFont(FONT, 5.5); c.drawCentredString(bx + 1.4 * mm, y0 - 2.5 * mm, "ABC"[k])
        c.setFont(FONT, 8.5); c.drawCentredString(x + 30 * mm, y + ch / 2 + 2 * mm, q)
        box(c, x + 24 * mm, y + ch / 2 - 7.5 * mm, 12 * mm, BH)
    return Item(("gr", s, tuple(vals), q), ans, d)


# ------------------------------------------------------------------ procenten

def g_proc_anker(rng):
    """Percentages berekenen met ankerpunten: 50%, 25%, 10%, 20%, 75%, 5%"""
    p = rng.choice([50, 25, 10, 20, 75, 5])
    base = {50: 2, 25: 4, 10: 10, 20: 5, 75: 4, 5: 20}[p]
    n = base * rng.randint(2, 40 if p in (10, 5) else 25)
    ans = F(p * n, 100)
    it = text_item(("pa", p, n), ans, [f"{p}% van {n} =", WIDE if ans >= 100 else None])
    return with_check(it, lambda: (ans.denominator == 1 and ans * 100 == p * n, "procent"))

def g_proc_1(rng):
    """Percentages berekenen met de 1%-regel: 3% van 400"""
    p = rng.choice([1, 2, 3, 4, 6, 7, 8, 9, 12, 15, 30, 40, 60])
    n = 100 * rng.randint(2, 9) if rng.random() < 0.7 else 50 * rng.randint(3, 19)
    if (p * n) % 100: n = 100 * rng.randint(2, 9)
    ans = F(p * n, 100)
    return with_check(text_item(("p1", p, n), ans, [f"{p}% van {n} =", WIDE if ans >= 100 else None]),
                      lambda: (ans.denominator == 1 and ans == F(p, 100) * n, "1%-regel"))


def g_proc_komma(rng):
    """Percentages omzetten in een kommagetal (en terug)."""
    p = rng.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 65, 70, 75, 80, 90, 12, 8])
    if rng.random() < 0.6:
        it = text_item(("pk", p), F(p, 100), [f"{p}% =", WIDE])
        return with_check(it, lambda: (F(p, 100) * 100 == p, "procent-komma"))
    it = text_item(("kp", p), p, [f"{D(F(p, 100))} =", None, "%"])
    return with_check(it, lambda: (F(D(F(p, 100)).replace(",", ".")) * 100 == p, "komma-procent"))

def g_omzetten(rng):
    """Breuken, kommagetallen en percentages in elkaar omzetten."""
    n, dd = rng.choice([(1, 2), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (1, 10), (3, 10), (7, 10), (1, 20), (1, 8)])
    fr = F(n, dd)
    v = rng.choice([0, 1, 2])
    if (fr * 100).denominator != 1:
        v = 1
    if v == 0:                                      # breuk -> %
        def d(c, x, y, ch):
            fw = frac_w(c, str(n), str(dd), 12)
            total = fw + 4.5 * mm + BW + 4.5 * mm
            cx = x + (CELL_W - total) / 2
            draw_frac(c, cx + fw / 2, y + ch / 2, str(n), str(dd), 12)
            c.setFont(FONT, 13); c.drawString(cx + fw + 1.2 * mm, y + ch / 2 - 1.6 * mm, "=")
            box(c, cx + fw + 5 * mm, y + ch / 2 - 4.5 * mm)
            c.drawString(cx + fw + 5 * mm + BW + 1 * mm, y + ch / 2 - 1.6 * mm, "%")
        it = Item(("oz0", n, dd), int(fr * 100), d)
        return with_check(it, lambda: (F(int(fr * 100), 100) == fr, "breuk-procent"))
    if v == 1:                                      # breuk -> kommagetal
        def d(c, x, y, ch):
            fw = frac_w(c, str(n), str(dd), 12)
            total = fw + 5 * mm + WBW
            cx = x + (CELL_W - total) / 2
            draw_frac(c, cx + fw / 2, y + ch / 2, str(n), str(dd), 12)
            c.setFont(FONT, 13); c.drawString(cx + fw + 1.2 * mm, y + ch / 2 - 1.6 * mm, "=")
            box(c, cx + fw + 5 * mm, y + ch / 2 - 4.5 * mm, WBW)
        it = Item(("oz1", n, dd), fr, d)
        return with_check(it, lambda: (F(D(fr).replace(",", ".")) == fr, "breuk-komma"))
    p = int(fr * 100)                               # % -> breuk (vereenvoudigd)
    def d(c, x, y, ch):
        s_ = f"{p}% ="
        w = c.stringWidth(s_, FONT, 13)
        total = w + 1.5 * mm + 7.4 * mm
        cx = x + (CELL_W - total) / 2
        c.setFont(FONT, 13); c.drawString(cx, y + ch / 2 - 1.6 * mm, s_)
        draw_frac(c, cx + w + 1.5 * mm + 3.7 * mm, y + ch / 2, None, None, 12)
    it = Item(("oz2", n, dd), fr, d, ans=[str(n), str(dd)], ans_text=f"{n}/{dd}")
    return with_check(it, lambda: (F(p, 100) == fr, "procent-breuk"))

def g_snelheid(rng):
    """Rekenen met snelheid in km/u en m/s."""
    v = rng.choice([0, 1, 2, 3])
    if v == 0:
        s = rng.choice([4, 5, 15, 20, 30, 40, 50, 60, 80, 90, 100, 120]); t = rng.randint(2, 5)
        return twoline(("sn0", s, t), s * t, f"{s} km/u, {t} uur rijden", ["afstand:", WIDE if s * t >= 100 else None, "km"], 9.5)
    if v == 1:
        s = rng.choice([30, 60, 90, 120]); m = rng.choice([10, 20, 30, 40])
        if (s * m) % 60: m = 30
        return twoline(("sn1", s, m), s * m // 60, f"{s} km/u, {m} minuten", ["afstand:", None, "km"], 9.5)
    if v == 2:
        s = rng.choice([40, 50, 60, 80, 90, 100]); t = rng.randint(2, 4)
        return twoline(("sn2", s, t), s, f"{s * t} km in {t} uur", ["snelheid:", None, "km/u"], 9.5)
    s = rng.choice([2, 3, 4, 5, 10, 12, 15, 20])
    return twoline(("sn3", s), s * 60, f"{s} m/s, 1 minuut lang", ["afstand:", WIDE, "m"], 9.5)


TYPES = {
    # herhaling
    "tot20": (g_tot20, "6 + 8 / 14 – 8"),
    "over": (g_over, "35 + 8 / 74 – 8"),
    "met": (g_met, "35 + 27 / 73 – 45"),
    "deelsplits3": (g_deelsplits3, "372 : 6 (splitsen)"),
    "xronde": (g_xronde, "3 × 400 / 6 × 2000"),
    "deelronde": (g_deelronde, "2400 : 6"),
    "deelgeheel": (g_deelgeheel, "deel van een geheel"),
    "lijn100000": (g_lijn100000, "getallenlijn tot 100 000"),
    "alletafels": (mk_tafel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "tall"), "alle tafels door elkaar"),
    "alledeel": (mk_deel_h([2, 3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9], "dall"), "alle deeltafels door elkaar"),
    # groep 7
    "cijfer1M": (g_cijfer1M, "cijferwaarde tot 1 000 000"),
    "nullen10000": (g_nullen10000, "4700 + 2800 / 8300 – 4600"),
    "groot": (g_groot, "sommen met grote getallen"),
    "lengte_alle": (g_lengte_alle, "alle lengtematen omzetten"),
    "liter_alle": (g_liter_alle, "alle litermaten omzetten"),
    "breukverg": (g_breukverg, "breuken vergelijken"),
    "vereenvoudig": (g_vereenvoudig, "breuken vereenvoudigen"),
    "kommaverg": (g_kommaverg, "kommagetallen ordenen"),
    "kommaplus": (g_kommaplus, "komma + en – (gelijk aantal decimalen)"),
    "kommawaarde": (g_kommawaarde, "cijferwaarde in kommagetal"),
    "vtabel": (g_vtabel, "verhoudingstabel"),
    "vtaal": (g_vtaal, "verhoudingentaal"),
    "grafiekreken": (g_grafiekreken, "rekenen met een grafiek"),
    "breukplus": (g_breukplus, "gelijknamige breuken + en –"),
    "kommax10": (g_kommax10, "kommagetal × 10, 100, 1000"),
    "kommadeel10": (g_kommadeel10, "kommagetal : 10, 100, 1000"),
    "gewicht": (g_gewicht, "ton, kg, g, mg"),
    "dm3": (g_dm3, "1 liter = 1 dm³"),
    "proc_anker": (g_proc_anker, "procenten met ankerpunten"),
    "proc_1": (g_proc_1, "procenten met de 1%-regel"),
    "proc_komma": (g_proc_komma, "procent en kommagetal"),
    "omzetten": (g_omzetten, "breuk, komma, procent omzetten"),
    "kommaplus2": (g_kommaplus2, "komma + en – (verschillend aantal decimalen)"),
    "snelheid": (g_snelheid, "snelheid (km/u en m/s)"),
    "samenhang": (g_samenhang, "samenhang lengte, inhoud en gewicht"),
}

PLAN = [
    ((1, 2),   "Opstart: herhaling groep 6",            ["alletafels", "alledeel", "met", "deelsplits3"], ["tot20", "xronde", "deelgeheel"]),
    ((3, 4),   "Tot 1 000 000, rekenen met nullen",     ["cijfer1M", "nullen10000", "tot20", "alletafels"], ["met", "deelronde", "lijn100000"]),
    ((5, 6),   "Sommen met grote getallen",             ["groot", "nullen10000", "lengte_alle", "cijfer1M"], ["tot20", "met", "alledeel"]),
    ((7, 8),   "Lengtematen en litermaten",             ["lengte_alle", "liter_alle", "groot", "tot20"], ["met", "cijfer1M", "deelsplits3"]),
    ((9, 10),  "Breuken vergelijken en vereenvoudigen", ["breukverg", "vereenvoudig", "alletafels", "alledeel"], ["met", "lengte_alle", "liter_alle"]),
    ((11, 12), "Kommagetallen",                         ["kommaverg", "kommaplus", "kommawaarde", "vereenvoudig"], ["alletafels", "groot", "tot20"]),
    ((13, 14), "Verhoudingen",                          ["vtabel", "vtaal", "kommaplus", "breukverg"], ["alledeel", "met", "kommawaarde"]),
    ((15, 16), "Herhaling blok 3–4",                    ["grafiekreken", "vtabel", "kommaplus", "vereenvoudig", "alletafels"], ["kommaverg", "alledeel"]),
    ((17, 18), "Breuken +/–, kommagetal × en : 10",     ["breukplus", "over", "kommax10", "kommadeel10"], ["vtabel", "kommaplus", "met"]),
    ((19, 20), "Gewichten: ton, kg, g, mg",             ["gewicht", "kommax10", "kommadeel10", "breukplus"], ["over", "vtaal", "liter_alle"]),
    ((21, 22), "1 liter = 1 dm³",                       ["dm3", "gewicht", "breukplus", "over"], ["kommax10", "vtabel", "met"]),
    ((23, 24), "Herhaling blok 5–6",                    ["kommax10", "kommadeel10", "breukplus", "gewicht", "dm3"], ["over", "kommaverg"]),
    ((25, 26), "Procenten met ankerpunten",             ["proc_anker", "proc_komma", "kommaplus2", "alletafels"], ["breukplus", "gewicht", "met"]),
    ((27, 28), "De 1%-regel, omzetten",                 ["proc_1", "proc_anker", "omzetten", "kommaplus2"], ["alledeel", "vtabel", "dm3"]),
    ((29, 30), "Snelheid",                              ["snelheid", "omzetten", "proc_1", "kommaplus2"], ["met", "kommax10", "grafiekreken"]),
    ((31, 32), "Herhaling blok 7–8, samenhang maten",   ["samenhang", "snelheid", "proc_anker", "omzetten", "kommaplus2"], ["proc_1", "vereenvoudig"]),
    ((33, 34), "Extra: rekenen tot 100 en tafels",      ["met", "alletafels", "alledeel", "deelsplits3"], ["tot20", "over", "kommaplus"]),
    ((35, 36), "Extra: kommagetallen",                  ["kommaplus2", "kommax10", "kommadeel10", "kommaverg"], ["met", "proc_anker", "lengte_alle"]),
    ((37, 38), "Extra: breuken en procenten",           ["omzetten", "proc_1", "breukplus", "vereenvoudig"], ["met", "gewicht", "snelheid"]),
    ((39, 40), "Jaarafsluiting: alles door elkaar",     ["met", "alletafels", "kommaplus2", "proc_anker", "omzetten"], ["snelheid", "breukverg", "dm3"]),
]

INTRO = (
    "Eén pagina per schoolweek; bovenaan staat het <b>weeknummer van de kalender</b>. Print per week zoveel pagina's als er leerlingen zijn, "
    "snijd langs de stippellijnen en leg per dag een stapeltje klaar. Elke strook: 10 opdrachten (± 5 minuten), "
    "ongeveer 7 focus en 3 herhaling. Rekenmuurtje: blok 2/4/6/8 = {w:8}, {w:16}, {w:24} en {w:32}. {W:1-2}: herhaling groep 6. "
    "<b>Rekenen tot 100 uit het hoofd en de tafels blijven het hele jaar terugkomen.</b> {W:33-40} zijn extra. "
    "Bij breuken vullen kinderen teller en noemer in (vereenvoudigd)."
)
