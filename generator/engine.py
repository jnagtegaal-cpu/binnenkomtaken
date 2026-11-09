"""Gedeelde engine voor binnenkomtaken: strookjes van 10 opdrachten, 5 stroken per A4.

Bevat de tekenhulpjes, de algemene opdrachttypen, de controle (validate) en het bouwen per week.
De opdrachten per groep staan in groep3.py t/m groep8.py; bouwen gaat via bouw.py."""
import math, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

W, H = A4
STRIP_H = H / 5
MX = 7 * mm
CELL_W = (W - 2 * MX) / 5
GREY = HexColor("#8c8c8c")
LIGHT = HexColor("#d9d9d9")
ACCENT = HexColor("#1f9bd7")
RED = HexColor("#e2534a")
DAYS = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag"]
FONT, FONTB = "Helvetica", "Helvetica-Bold"
NUM = 15
BW, BH = 9 * mm, 8 * mm

PROBLEMS = []  # verzamelt fouten uit de controle


MAXV = [100]
WIDE = "\x00WIDE"          # invulvak voor grote getallen
WBW = 13.5 * mm
MINSIZE = [11.5]


SUP = {"²": "2", "³": "3"}


def txt_w(c, s, font, size):
    w = 0
    for ch in s:
        w += c.stringWidth(SUP[ch], font, size * 0.6) if ch in SUP else c.stringWidth(ch, font, size)
    return w


def draw_txt(c, x, y, s, font, size):
    """Tekst tekenen; ² en ³ worden als kleine verhoogde cijfers getekend (het lettertype heeft die tekens niet)."""
    buf = ""
    for ch in s:
        if ch in SUP:
            c.setFont(font, size); c.drawString(x, y, buf); x += c.stringWidth(buf, font, size); buf = ""
            c.setFont(font, size * 0.6); c.drawString(x, y + size * 0.4, SUP[ch]); x += c.stringWidth(SUP[ch], font, size * 0.6)
        else:
            buf += ch
    c.setFont(font, size); c.drawString(x, y, buf)


def fmt_dec(v):
    """Fraction/int -> Nederlandse notatie met komma (3,25)."""
    from fractions import Fraction
    v = Fraction(v)
    if v.denominator == 1:
        return fmt(int(v))
    sign = "-" if v < 0 else ""
    v = abs(v)
    ip = int(v); rest = v - ip
    digits = ""
    for _ in range(6):
        rest *= 10; d = int(rest); digits += str(d); rest -= d
        if rest == 0: break
    return f"{sign}{fmt(ip)},{digits}"


def fmt(n):
    """Getallen vanaf 10 000 met een spatie per drie cijfers (zoals in de methode)."""
    return f"{n:,}".replace(",", "\u00a0") if n >= 10000 else str(n)

class Item:
    def __init__(self, key, answer, draw, expr=None, norange=False, ans=None, ans_draw=None, ans_text=None):
        self.key, self.answer, self.draw, self.expr = key, answer, draw, expr
        self.norange = norange
        self.ans = ans              # lijst met teksten, één per invulvak (in tekenvolgorde)
        self.ans_draw = ans_draw    # functie(c, x, y, ch) voor antwoorden zonder invulvak (omcirkelen, wijzers)
        self.ans_text = ans_text    # korte tekst voor het antwoordoverzicht


ANS = {"on": False, "queue": [], "boxes": 0, "rects": []}
ANSCOL = HexColor("#13863b")


# ------------------------------------------------------------------ teken-hulpjes

def box(c, x, y, w=BW, h=BH, ans=True):
    c.setStrokeColor(black); c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 1.2 * mm, stroke=1, fill=0)
    if ans and ANS["on"]:
        ANS["boxes"] += 1
        ANS["rects"].append((x, y, w, h))
        if ANS["queue"]:
            t = ANS["queue"].pop(0)
            size = min(13, h / mm * 1.75)
            while c.stringWidth(t, FONTB, size) > w - 1.2 * mm and size > 5:
                size -= 0.5
            c.saveState(); c.setFillColor(ANSCOL); c.setFont(FONTB, size)
            c.drawCentredString(x + w / 2, y + h / 2 - size * 0.36, t)
            c.restoreState()


def answer_hands(c, cx, cy, h, m, r=8.2 * mm):
    """Groene wijzers als antwoord bij 'teken de wijzers'."""
    c.saveState(); c.setStrokeColor(ANSCOL)
    ah = math.radians(90 - ((h % 12) + m / 60) * 30); am = math.radians(90 - m * 6)
    c.setLineWidth(1.8); c.line(cx, cy, cx + math.cos(ah) * r * 0.45, cy + math.sin(ah) * r * 0.45)
    c.setLineWidth(1.1); c.line(cx, cy, cx + math.cos(am) * r * 0.68, cy + math.sin(am) * r * 0.68)
    c.restoreState()


def answer_ring(c, cx, cy, w, h):
    """Groene ring om het goede antwoord (voor 'omcirkel' opdrachten)."""
    c.saveState(); c.setStrokeColor(ANSCOL); c.setLineWidth(1.6)
    c.ellipse(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, stroke=1, fill=0)
    c.restoreState()


def text_with_boxes(c, x, y, parts, size=NUM):
    bw, gap = BW, 1.2 * mm
    while True:
        widths = [bw if p is None else WBW if p == WIDE else txt_w(c, p, FONT, size) for p in parts]
        total = sum(widths) + gap * (len(parts) - 1)
        if total <= CELL_W - 2.5 * mm or size <= MINSIZE[0]:
            break
        size -= 0.5
    if total > CELL_W - 1.5 * mm:
        if len(parts) > 1 and parts[0] not in (None, WIDE) and any(p in (None, WIDE) for p in parts[1:]):
            # twee regels: eerste tekstdeel boven, de rest (met invulvak) eronder
            txt = parts[0]
            sz = 12.5
            while txt_w(c, txt, FONT, sz) > CELL_W - 3 * mm and sz > 9:
                sz -= 0.5
            if txt_w(c, txt, FONT, sz) > CELL_W - 2 * mm:
                PROBLEMS.append(f"te breed: {parts}")
            c.setFillColor(black)
            draw_txt(c, x + (CELL_W - txt_w(c, txt, FONT, sz)) / 2, y + 4.4 * mm, txt, FONT, sz)
            text_with_boxes(c, x, y - 5 * mm, parts[1:], 12)
            return
        PROBLEMS.append(f"te breed: {parts}")
    cx = x + (CELL_W - total) / 2
    c.setFont(FONT, size); c.setFillColor(black)
    for p, wdt in zip(parts, widths):
        if p is None:
            box(c, cx, y - 2.3 * mm)
        elif p == WIDE:
            box(c, cx, y - 2.3 * mm, WBW)
        else:
            draw_txt(c, cx, y, p, FONT, size)
        cx += wdt + gap


def label(c, x, y, s):
    c.setFont(FONT, 6.5); c.setFillColor(GREY)
    c.drawCentredString(x + CELL_W / 2, y, s); c.setFillColor(black)


PIPS = {1: [(0, 0)], 2: [(-1, 1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)],
        4: [(-1, 1), (1, 1), (-1, -1), (1, -1)], 5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
        6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]}


def dice(c, x, y, n, s=11 * mm):
    c.setLineWidth(0.8); c.setStrokeColor(black)
    c.roundRect(x, y, s, s, 1.8 * mm, stroke=1, fill=0)
    cx, cy, d = x + s / 2, y + s / 2, s * 0.28
    c.setFillColor(black)
    for px, py in PIPS[n]:
        c.circle(cx + px * d, cy + py * d, s * 0.085, stroke=0, fill=1)


def tenframe(c, x, y, n, sp=3.3 * mm, r=1.25 * mm):
    c.setLineWidth(0.6); c.setStrokeColor(black)
    c.rect(x, y, 5 * sp, 2 * sp, stroke=1, fill=0)
    c.line(x, y + sp, x + 5 * sp, y + sp)
    for i in range(1, 5):
        c.line(x + i * sp, y, x + i * sp, y + 2 * sp)
    for k in range(n):
        row, col = (0, k) if k < 5 else (1, k - 5)
        c.setFillColor(ACCENT if k < 5 else RED)
        c.circle(x + col * sp + sp / 2, y + 2 * sp - row * sp - sp / 2, r, stroke=0, fill=1)
    c.setFillColor(black)


def clock_face(c, cx, cy, hour_pos, minute_pos, r=8.2 * mm, hands=True, ticks=False):
    """hour_pos in uren (0-12, mag fractie), minute_pos in minuten."""
    c.setLineWidth(0.9); c.setStrokeColor(black)
    c.circle(cx, cy, r, stroke=1, fill=0)
    if ticks:
        for i in range(60):
            a = math.radians(90 - i * 6)
            r0 = r * (0.86 if i % 5 == 0 else 0.92)
            c.setLineWidth(0.6 if i % 5 == 0 else 0.3)
            c.line(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r * 0.98, cy + math.sin(a) * r * 0.98)
        c.setLineWidth(0.9)
    c.setFont(FONT, 5.2); c.setFillColor(black)
    for i in range(1, 13):
        a = math.radians(90 - i * 30)
        rn = 0.70 if ticks else 0.78
        c.drawCentredString(cx + math.cos(a) * r * rn, cy + math.sin(a) * r * rn - 1.8, str(i))
    if not hands:
        c.circle(cx, cy, 0.5 * mm, stroke=0, fill=1); return
    ah = math.radians(90 - hour_pos * 30)
    am = math.radians(90 - minute_pos * 6)
    c.setLineWidth(1.6)
    c.line(cx, cy, cx + math.cos(ah) * r * 0.45, cy + math.sin(ah) * r * 0.45)
    c.setLineWidth(1.0)
    c.line(cx, cy, cx + math.cos(am) * r * 0.68, cy + math.sin(am) * r * 0.68)
    c.circle(cx, cy, 0.5 * mm, stroke=0, fill=1)


def numberline(c, x, y, lo, hi, step, labels, target, bw=BW):
    L = CELL_W - 6 * mm
    x0, yl = x + 3 * mm, y + 4.5 * mm
    c.setLineWidth(0.8); c.setStrokeColor(black)
    c.line(x0, yl, x0 + L, yl)
    n = (hi - lo) // step
    for i in range(n + 1):
        v = lo + i * step
        tx = x0 + L * i / n
        big = v in labels
        c.line(tx, yl - (1.6 if big else 1.0) * mm, tx, yl + (1.6 if big else 1.0) * mm)
    c.setFont(FONT, 6.5)
    for v in labels:
        t_ = fmt(v); w_ = c.stringWidth(t_, FONT, 6.5)
        px = x0 + L * (v - lo) / (hi - lo) - w_ / 2
        px = min(max(px, x + 0.6 * mm), x + CELL_W - 0.6 * mm - w_)
        c.drawString(px, yl - 4 * mm, t_)
    tx = x0 + L * (target - lo) / (hi - lo)
    bx = min(max(tx - bw / 2, x + 1 * mm), x + CELL_W - bw - 1 * mm)
    box(c, bx, yl + 6 * mm, bw)
    c.setLineWidth(0.8); c.line(tx, yl + 6 * mm, tx, yl + 1.8 * mm)
    c.setFillColor(ACCENT); c.circle(tx, yl, 0.9 * mm, stroke=0, fill=1); c.setFillColor(black)


def splitsbeen(c, x, y, ch, top, left, right, bw=BW):
    """top/left/right: str of None (= invulvakje)."""
    cx = x + CELL_W / 2
    top_y = y + ch - 9 * mm
    c.setLineWidth(0.8); c.setStrokeColor(black)
    lx, rx, by = cx - bw - 1.5 * mm, cx + 1.5 * mm, y + 1.2 * mm
    c.line(cx - 1.5 * mm, top_y, lx + bw / 2, by + BH)
    c.line(cx + 1.5 * mm, top_y, rx + bw / 2, by + BH)
    for bx, byy, val, bold in ((cx - bw / 2, top_y, top, True), (lx, by, left, False), (rx, by, right, False)):
        box(c, bx, byy, bw, ans=(val is None))
        if val is not None:
            c.setFont(FONTB if bold else FONT, 13 if len(val) < 3 else 11)
            c.drawCentredString(bx + bw / 2, byy + 2.2 * mm, val)


# ------------------------------------------------------------------ algemene generatoren

def sum_item(key, answer, parts):
    def d(c, x, y, ch):
        text_with_boxes(c, x, y + ch / 2 - 2.5 * mm, parts)
    return Item(key, answer, d, expr=parts)


def g_dobbel(rng):
    n = rng.randint(1, 6)
    def d(c, x, y, ch):
        dice(c, x + 6 * mm, y + (ch - 11 * mm) / 2, n)
        box(c, x + 22 * mm, y + (ch - BH) / 2)
    return Item(("dob", n), n, d)


def g_twodice(rng):
    a, b = rng.randint(1, 6), rng.randint(1, 6)
    def d(c, x, y, ch):
        s = 9.5 * mm
        dice(c, x + 2.5 * mm, y + (ch - s) / 2, a, s)
        dice(c, x + 13 * mm, y + (ch - s) / 2, b, s)
        box(c, x + 25.5 * mm, y + (ch - BH) / 2)
    return Item(("2d", a, b), a + b, d)


def g_tien10(rng):
    n = rng.randint(1, 10)
    def d(c, x, y, ch):
        tenframe(c, x + 3.5 * mm, y + (ch - 6.6 * mm) / 2, n)
        box(c, x + 24 * mm, y + (ch - BH) / 2)
    return Item(("t10", n), n, d)


def _two_frames(a, b):
    def d(c, x, y, ch):
        sp = 3.1 * mm
        tenframe(c, x + 2.5 * mm, y + ch - 10 * mm, a, sp, 1.15 * mm)
        tenframe(c, x + 2.5 * mm + 5 * sp + 1.5 * mm, y + ch - 10 * mm, b, sp, 1.15 * mm)
        box(c, x + (CELL_W - BW) / 2, y + 0.8 * mm)
    return d


def g_tien20(rng):
    n = rng.randint(11, 20)
    return Item(("t20", n), n, _two_frames(10, n - 10))


def g_dubbelbeeld(rng):
    a = rng.randint(2, 10)
    return Item(("db", a), 2 * a, _two_frames(a, a))


def mk_seq(lo, hi, step, name, lab=None):
    """Rijtje van 3 getallen met 1 open plek. step mag negatief zijn."""
    def g(rng):
        span = 2 * abs(step)
        if step > 0:
            s = rng.randint(lo, hi - span)
        else:
            s = rng.randint(lo + span, hi)
        seq = [s, s + step, s + 2 * step]
        blank = rng.choice([0, 1, 2])
        parts = []
        for i, v in enumerate(seq):
            parts.append(None if i == blank else str(v))
            if i < 2:
                parts.append(",")
        def d(c, x, y, ch):
            if lab:
                label(c, x, y + ch - 3 * mm, lab)
            text_with_boxes(c, x, y + ch / 2 - 2.5 * mm, parts, 14)
        it = Item((name, s, blank), seq[blank], d)
        it.seq = (seq, step)
        return it
    return g


def text_item(key, answer, parts, norange=False):
    def d(c, x, y, ch):
        text_with_boxes(c, x, y + ch / 2 - 2.5 * mm, parts)
    return Item(key, answer, d, norange=norange)


def mk_cmp(lo, hi, name):
    def g(rng):
        a, b = rng.sample(range(lo, hi + 1), 2)
        def d(c, x, y, ch):
            label(c, x, y + ch - 3 * mm, "omcirkel de grootste")
            c.setFont(FONTB, 16)
            c.drawCentredString(x + CELL_W * 0.32, y + ch / 2 - 4 * mm, str(a))
            c.drawCentredString(x + CELL_W * 0.68, y + ch / 2 - 4 * mm, str(b))
        def r(c, x, y, ch):
            answer_ring(c, x + CELL_W * (0.32 if a > b else 0.68), y + ch / 2 - 1.8 * mm, 11 * mm, 9 * mm)
        return Item((name, a, b), max(a, b), d, ans=[], ans_draw=r, ans_text=f"{max(a, b)} omcirkelen")
    return g


def mk_lijn(lo, hi, name):
    mid = (lo + hi) // 2
    def g(rng):
        t = rng.choice([v for v in range(lo + 1, hi) if v != mid])
        def d(c, x, y, ch):
            numberline(c, x, y, lo, hi, 1, (lo, mid, hi), t)
        return Item((name, t), t, d)
    return g


def mk_splits(totals, name):
    def g(rng):
        t = rng.choice(totals)
        a = rng.randint(1, t - 1)
        left_known = rng.random() < 0.5
        def d(c, x, y, ch):
            splitsbeen(c, x, y, ch, str(t), str(a) if left_known else None,
                       None if left_known else str(t - a))
        return Item((name, t, a, left_known), t - a if left_known else a, d)
    return g


def mk_clock(mode):
    """mode: hour | half | mix (analoog)"""
    def g(rng):
        h = rng.randint(1, 12)
        half = mode == "half" or (mode == "mix" and rng.random() < 0.5)
        # tijd h:00 of h:30 ; half -> "half (h+1)"
        ans = h if not half else (h % 12) + 1
        def d(c, x, y, ch):
            clock_face(c, x + 10.5 * mm, y + ch / 2, (h % 12) + (0.5 if half else 0), 30 if half else 0)
            c.setFont(FONT, 11)
            if half:
                c.drawString(x + 20.5 * mm, y + ch / 2 - 1.3 * mm, "half")
                box(c, x + 29 * mm, y + ch / 2 - 4 * mm, 8.5 * mm, BH)
            else:
                box(c, x + 20 * mm, y + ch / 2 - 4 * mm, 8.5 * mm, BH)
                c.drawString(x + 30.3 * mm, y + ch / 2 - 1.3 * mm, "uur")
        return Item(("cl", h, half), ans, d)
    return g


# ------------------------------------------------------------------ pagina-opbouw

def _ev(expr):
    import re
    from fractions import Fraction
    expr = expr.replace("\u00a0", "").replace("–", "-").replace("×", "*").replace(":", "/")
    expr = re.sub(r"\d+(?:,\d+)?", lambda m: f"Fraction('{m.group(0).replace(',', '.')}')", expr)
    return eval(expr, {"Fraction": Fraction})


def validate(it, typename):
    from fractions import Fraction
    a = it.answer
    if isinstance(a, bool) or not isinstance(a, (int, Fraction)) or a < 0 or (a > MAXV[0] and not it.norange):
        PROBLEMS.append(f"{typename}: antwoord buiten bereik {it.key} -> {a}")
        return
    if isinstance(a, Fraction) and a.denominator == 1:
        a = int(a)
    if it.expr:
        ans = fmt_dec(a).replace("\u00a0", "")
        s = " ".join(ans if (p is None or p == WIDE) else p for p in it.expr)
        if "=" not in s:
            PROBLEMS.append(f"{typename}: geen = in {s}"); return
        lhs, rhs = s.split("=")
        try:
            L, R = _ev(lhs), _ev(rhs)
        except Exception as e:
            PROBLEMS.append(f"{typename}: niet te rekenen {s} ({e})"); return
        if L != R:
            PROBLEMS.append(f"{typename}: klopt niet {s}")
        import re
        for tok in re.findall(r"\d+(?:,\d+)?", s.replace("\u00a0", "")):
            if Fraction(tok.replace(",", ".")) > MAXV[0]:
                PROBLEMS.append(f"{typename}: getal buiten bereik {s}")
    if hasattr(it, "seq"):
        seq, step = it.seq
        if any(v < 0 or v > MAXV[0] for v in seq):
            PROBLEMS.append(f"{typename}: rij buiten bereik {seq}")
    if hasattr(it, "check"):
        ok, msg = it.check()
        if not ok:
            PROBLEMS.append(f"{typename}: {msg}")


def answer_list(it):
    if it.ans is not None:
        return list(it.ans)
    return [fmt_dec(it.answer)]


def answer_text(it):
    if it.ans_text:
        return it.ans_text
    return " / ".join(answer_list(it)) or fmt_dec(it.answer)


def plan_for(plan, week):
    for (a, b), title, focus, herh in plan:
        if a <= week <= b:
            return title, focus, herh
    raise ValueError(week)


def strip_items(rng, plan, types, week):
    _, focus, herh = plan_for(plan, week)
    nh = min(3, len(herh))
    nf = 10 - nh
    tlist = [focus[i % len(focus)] for i in range(nf)]
    pool = herh[:]; rng.shuffle(pool)
    tlist += pool[:nh]
    order = focus + herh
    tlist.sort(key=lambda t: order.index(t))
    items, seen = [], set()
    for t in tlist:
        for _ in range(200):
            it = types[t][0](rng)
            if it.key not in seen:
                break
        else:
            PROBLEMS.append(f"week {week}: geen unieke opdracht voor {t}")
        seen.add(it.key)
        validate(it, t)
        items.append(it)
    if len(items) != 10:
        PROBLEMS.append(f"week {week}: {len(items)} opdrachten")
    return items


def draw_strip(c, y0, week, day, group, title, items, answers=False):
    top = y0 + STRIP_H
    c.setFont(FONTB, 9); c.setFillColor(ACCENT)
    c.drawString(MX, top - 7.5 * mm, f"Week {week}  ·  {day}")
    c.setFont(FONT, 7.5); c.setFillColor(GREY)
    ht = f"{group}  ·  {title}"
    draw_txt(c, W / 2 - txt_w(c, ht, FONT, 7.5) / 2, top - 7.5 * mm, ht, FONT, 7.5)
    if answers:
        c.setFillColor(ANSCOL); c.setFont(FONTB, 9)
        c.drawRightString(W - MX, top - 7.5 * mm, "ANTWOORDEN")
    else:
        c.setFillColor(black); c.setFont(FONT, 8.5)
        c.drawString(W - MX - 52 * mm, top - 7.5 * mm, "Naam:")
        c.setLineWidth(0.5); c.setStrokeColor(GREY)
        c.line(W - MX - 42 * mm, top - 8 * mm, W - MX, top - 8 * mm)
    area_top, area_bot = top - 11 * mm, y0 + 4 * mm
    ch = (area_top - area_bot) / 2
    for i, it in enumerate(items):
        r, col = divmod(i, 5)
        x = MX + col * CELL_W
        y = area_top - (r + 1) * ch
        c.setFont(FONT, 6); c.setFillColor(GREY)
        c.drawString(x + 0.8 * mm, y + ch - 2.6 * mm, str(i + 1))
        c.setFillColor(black); c.setStrokeColor(black)
        if answers:
            ANS["on"] = True; ANS["queue"] = answer_list(it); ANS["boxes"] = 0; ANS["rects"] = []
            want = len(ANS["queue"])
            it.draw(c, x, y, ch)
            if it.ans_draw:
                it.ans_draw(c, x, y, ch)
            if ANS["boxes"] != want or ANS["queue"]:
                PROBLEMS.append(f"week {week} {day} opdracht {i + 1}: {ANS['boxes']} invulvakken, {want} antwoorden ({it.key})")
            ANS["on"] = False
            # plek van de antwoordvakjes binnen de strook (fracties; y vanaf de bovenkant) voor het digibord
            it.rects = [[round(bx / W, 4), round((top - (by + bh)) / STRIP_H, 4), round(bw / W, 4), round(bh / STRIP_H, 4)]
                        for bx, by, bw, bh in ANS["rects"]]
            it.cell = [round(x / W, 4), round((top - (y + ch)) / STRIP_H, 4), round(CELL_W / W, 4), round(ch / STRIP_H, 4)]
        else:
            it.draw(c, x, y, ch)
    c.setStrokeColor(LIGHT); c.setLineWidth(0.4)
    for col in range(1, 5):
        xx = MX + col * CELL_W
        c.line(xx, area_bot + 1 * mm, xx, area_top - 1 * mm)
    c.line(MX, area_bot + ch, W - MX, area_bot + ch)


def cutlines(c):
    c.setStrokeColor(GREY); c.setLineWidth(0.5); c.setDash(3, 2)
    for i in range(1, 5):
        c.line(0, i * STRIP_H, W, i * STRIP_H)
    c.setDash()
    c.setFillColor(black)


def week_label(labels, a, b=None):
    """Kalenderweek(en) voor lesweek a (t/m b): '46', '45–46' of '50, 1' (met vakantie ertussen)."""
    if not labels:
        return f"{a}" if b is None else f"{a}–{b}"
    la = labels[a]
    if b is None or b == a:
        return str(la)
    lb = labels[b]
    if b - a == 1:
        return f"{la}–{lb}" if lb == la + 1 else f"{la}, {lb}"
    return f"{la}–{lb}"


def overview(c, group, plan, types, intro, labels=None):
    c.setFont(FONTB, 18); c.setFillColor(ACCENT)
    c.drawString(20 * mm, H - 25 * mm, f"Binnenkomtaken {group.lower()} – jaaroverzicht")
    c.setFillColor(black)
    st = ParagraphStyle("i", fontName=FONT, fontSize=9, leading=12)
    p = Paragraph(intro, st); _, h = p.wrap(175 * mm, 100 * mm)
    y = H - 31 * mm - h
    p.drawOn(c, 20 * mm, y)
    y -= 8 * mm
    c.setFont(FONTB, 9)
    for xmm, t in ((20, "Week"), (33, "Thema"), (73, "Focus"), (148, "Herhaling")):
        c.drawString(xmm * mm, y, t)
    y -= 2 * mm; c.setStrokeColor(GREY); c.setLineWidth(0.6); c.line(20 * mm, y, 195 * mm, y)
    st2 = ParagraphStyle("s", fontName=FONT, fontSize=7.4, leading=8.6)
    y -= 2 * mm
    for (a, b), title, focus, herh in plan:
        sup = lambda t_: t_.replace("³", "<super>3</super>").replace("²", "<super>2</super>")
        cells = [(20, 12, week_label(labels, a, b)), (33, 38, sup(title)),
                 (73, 73, sup(", ".join(types[t][1] for t in focus))),
                 (148, 47, sup(", ".join(types[t][1] for t in herh)) or "–")]
        ps = []
        for xmm, wmm, txt in cells:
            pp = Paragraph(txt, st2); _, hh = pp.wrap(wmm * mm, 60 * mm); ps.append((xmm, pp, hh))
        hmax = max(hh for _, _, hh in ps)
        for xmm, pp, hh in ps:
            pp.drawOn(c, xmm * mm, y - hh - 1.5 * mm)
        y -= hmax + 2.4 * mm
        c.setStrokeColor(LIGHT); c.setLineWidth(0.4); c.line(20 * mm, y, 195 * mm, y)
        y -= 0.5 * mm
    if y < 15 * mm:
        PROBLEMS.append("overzicht loopt van de pagina")


# ------------------------------------------------------------------ per week bouwen (voor de site)

def week_rng(group, week, versie=1):
    """Vaste willekeur per groep en week: een week verandert alleen als je die week zelf opnieuw bouwt
    of de versie ophoogt. Aanpassingen aan andere weken hebben er geen invloed op."""
    return random.Random(f"binnenkomtaken|{group}|week{week}|v{versie}")


def build_week(outdir, group, plan, types, week, versie=1, label=None):
    """Bouwt voor één week: leerlingblad (PDF), antwoordblad (PDF), antwoordstroken per dag (PNG) en week.json.
    week = lesweek (1-40; bepaalt plan en willekeur), label = kalenderweek (staat op het blad en in de bestandsnaam)."""
    label = label or week
    import os, json, subprocess, tempfile
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    rng = week_rng(group, week, versie)
    title = plan_for(plan, week)[0]
    days = [strip_items(rng, plan, types, week) for _ in range(5)]
    base = os.path.join(outdir, f"week{label:02d}")
    for answers, path in ((False, base + ".pdf"), (True, base + "-antwoorden.pdf")):
        c = canvas.Canvas(path, pagesize=A4)
        c.setTitle(f"Binnenkomtaken {group.lower()} week {label}" + (" – antwoorden" if answers else ""))
        cutlines(c)
        for d in range(5):
            draw_strip(c, H - (d + 1) * STRIP_H, label, DAYS[d], group, title, days[d], answers=answers)
        c.showPage(); c.save()
    # antwoordstroken als afbeelding (voor het digibord)
    dpi = 170
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", base + "-antwoorden.pdf", os.path.join(td, "p")], check=True)
        png = [f for f in os.listdir(td) if f.endswith(".png")][0]
        img = Image.open(os.path.join(td, png)).convert("RGB")
    sh = img.height / 5
    for d in range(5):
        strip = img.crop((0, round(d * sh), img.width, round((d + 1) * sh)))
        strip = strip.quantize(colors=48, method=Image.Quantize.MEDIANCUT)
        strip.save(f"{base}-dag{d + 1}.png", optimize=True)
    meta = {
        "week": week, "kalenderweek": label, "thema": title, "versie": versie,
        "dagen": [{"dag": DAYS[d], "antwoorden": [answer_text(it) for it in days[d]],
                   "vakjes": [(it.rects if (it.rects and not it.ans_draw) else [it.cell]) for it in days[d]]}
                  for d in range(5)],
    }
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta


def build_year_pdfs(outdir, group, plan, types, intro, slug, labels=None):
    """Plakt de weekbladen samen tot één jaar-PDF (met jaaroverzicht) en één antwoorden-PDF."""
    import os, tempfile
    from pypdf import PdfWriter, PdfReader
    with tempfile.TemporaryDirectory() as td:
        ov = os.path.join(td, "overzicht.pdf")
        c = canvas.Canvas(ov, pagesize=A4); overview(c, group, plan, types, intro, labels); c.showPage(); c.save()
        for suffix, out in (("", f"{slug}-heel-jaar.pdf"), ("-antwoorden", f"{slug}-antwoorden-heel-jaar.pdf")):
            w = PdfWriter()
            for week in range(1, 41):
                lab = labels[week] if labels else week
                for p in PdfReader(os.path.join(outdir, f"week{lab:02d}{suffix}.pdf")).pages:
                    w.add_page(p)
            for p in PdfReader(ov).pages:
                w.add_page(p)
            w.add_metadata({"/Title": f"Binnenkomtaken {group.lower()}" + (" – antwoorden" if suffix else "")})
            with open(os.path.join(outdir, out), "wb") as f:
                w.write(f)
        # los jaaroverzicht
        import shutil
        shutil.copy(ov, os.path.join(outdir, f"{slug}-jaaroverzicht.pdf"))
