"""La penicilina (1928): un moho que se coló en una placa de bacterias las mató a su alrededor.

Placa de Petri sobre la mesa de un laboratorio, llena de colonias de bacterias (personajes originales
redonditos con ojos). Se retira la tapa de cristal; una espora de moho verde (personaje original) entra
flotando, aterriza en la placa y crece; a su alrededor las bacterias se asustan y desaparecen, y se abre
un círculo limpio. En la revelación, la luz del laboratorio baja, la placa brilla dorada y la cámara se acerca.
Arriba: pared tranquila del laboratorio (logo y textos); abajo, la mesa, la placa y el estante.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.2   # el círculo limpio brilla: golpe musical
MUSICA = 7

PX, PY = 540, 1450            # centro de la placa (cara del agar)
PRX, PRY = 370, 175           # radios del agar
MX, MY = 440, 1455            # donde aterriza el moho
K = 0.47                      # aplastamiento de la perspectiva

rng = np.random.default_rng(1928)
BACT = []
while len(BACT) < 15:
    u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
    if u * u + v * v > 0.78: continue
    x, y = PX + u * PRX, PY + v * PRY
    if math.hypot(x - MX, (y - MY) / K) < 120: continue
    if any(math.hypot(x - bx, (y - by) / 0.6) < 118 for bx, by, *_ in BACT): continue
    BACT.append((x, y, rng.uniform(1.15, 1.4), rng.uniform(0, 6.28), rng.uniform(0, 1.5)))
DUST = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 6), rng.uniform(15, 40)) for _ in range(28)]

ZONA_MAX = 330


def zona(t):
    """Radio (en x) del círculo limpio alrededor del moho."""
    return ZONA_MAX * seg(t, 5.0, 7.1)


def t_muerte(d):
    if d >= ZONA_MAX * 0.995: return None
    lo, hi = 5.0, 7.1
    for _ in range(30):
        m = (lo + hi) / 2
        if zona(m) < d: lo = m
        else: hi = m
    return hi


BACT = [b + (t_muerte(math.hypot(b[0] - MX, (b[1] - MY) / K)),) for b in BACT]


def ojos(cx, cy, s, t, fase, susto=0.0, mira=0.0):
    blink = 0.12 if ((t + fase) % 2.7) < 0.12 else 1.0
    er = 9 * s * (1 + 0.45 * susto)
    g = []
    for ex in (-11, 11):
        x = cx + ex * s
        g.append(f"<ellipse cx='{x:.1f}' cy='{cy:.1f}' rx='{er:.1f}' ry='{er * 1.15 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='3.5'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{x + mira * 3 * s:.1f}' cy='{cy + 1.5 * s:.1f}' r='{er * (0.55 - 0.2 * susto):.1f}' fill='{INK}'/>")
            g.append(f"<circle cx='{x + mira * 3 * s - 2 * s:.1f}' cy='{cy - 1.5 * s:.1f}' r='{1.8 * s:.1f}' fill='#fff'/>")
    return "".join(g)


def bacteria(x, y, s, fase, t, td):
    """Colonia redondita (racimo de bolitas, como los estafilococos) con cara."""
    pop = rebote(t, 0.05 + fase * 0.25, 0.45)
    if pop <= 0: return ""
    susto, esc, alfa = 0.0, 1.0, 1.0
    if td is not None:
        susto = seg(t, td - 0.35, td - 0.1)
        esc = 1 - seg(t, td, td + 0.32)
        if esc <= 0.01:
            k = seg(t, td, td + 0.9)
            if k >= 1: return ""
            out = []
            for a in range(0, 360, 60):
                r = 20 + 45 * k
                out.append(f"<circle cx='{x + r * math.cos(math.radians(a)):.1f}' cy='{y - 10 + r * 0.6 * math.sin(math.radians(a)):.1f}' "
                           f"r='{5 * (1 - k):.1f}' fill='#fffbe6' opacity='{1 - k:.2f}'/>")
            return "".join(out)
    tiembla = 3 * math.sin(t * 40) * susto
    bob = 3 * math.sin(t * 4 + fase * 5)
    sq = 1 + 0.05 * math.sin(t * 4 + fase * 5)
    sc = s * pop * esc
    g = [f"<g transform='translate({x + tiembla:.1f},{y + bob:.1f}) scale({sc * sq:.3f},{sc / sq:.3f})'>",
         "<ellipse cx='0' cy='22' rx='34' ry='9' fill='#7a4d10' opacity='0.25'/>"]
    col = mix("#fff0b0", "#fff7d6", susto)
    for bx, by, br in ((-24, 6, 15), (24, 4, 14), (-12, -24, 13), (16, -22, 12)):
        g.append(f"<circle cx='{bx}' cy='{by}' r='{br}' fill='{mix('#ffe48a', '#fff3c4', susto)}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='0' cy='0' r='26' fill='{col}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='-9' cy='-12' rx='8' ry='5' fill='#fff' opacity='0.8'/>")
    g.append(ojos(0, -2, 1.0, t, fase, susto, mira=-1 if x > MX else 1))
    if susto > 0.3:
        g.append(f"<ellipse cx='0' cy='14' rx='5' ry='6' fill='{INK}'/>")
    else:
        g.append(f"<path d='M -7 12 Q 0 18 7 12' fill='none' stroke='{INK}' stroke-width='3.5' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def borla(r, t, n=14, amp=0.09):
    """Contorno peludo (moho) de radio r."""
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r * (1 + (amp if i % 2 == 0 else -amp * 0.3) + 0.03 * math.sin(t * 3 + i))
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(1, len(pts) + 1, 2):
        c = pts[i % len(pts)]; p = pts[(i + 1) % len(pts)]
        d += f"Q {c[0]:.1f} {c[1]:.1f} {p[0]:.1f} {p[1]:.1f} "
    return d + "Z"


def moho(t):
    """Espora de moho verde: entra flotando, aterriza (4,6 s) y crece como una colonia peluda."""
    if t < 2.0: return ""
    k = seg(t, 2.0, 4.6)
    if t < 4.6:
        x = lerp(1120, MX, k) + 60 * math.sin(k * 5.5) * (1 - k)
        y = lerp(860, MY - 30, k ** 1.4) + 25 * math.sin(k * 9) * (1 - k)
        r, sq, rot = 55, 1.0, 25 * math.sin(t * 3)
    else:
        x, y = MX, MY - 30
        land = clamp((t - 4.6) / 0.35)
        sq = 1 + 0.25 * math.sin(math.pi * land) * (1 - land)
        r = lerp(55, 112, seg(t, 4.7, 7.0)) + 18 * rebote(t, 7.2, 0.5) * (1 - seg(t, 8.2, 9.0)) + 10 * seg(t, 7.2, 7.8)
        rot = 0
        y = MY - r * 0.42
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({sq:.3f},{1 / sq:.3f})'>"]
    if t >= 4.6:
        g.append(f"<ellipse cx='0' cy='{r * 0.42:.1f}' rx='{r * 1.2:.1f}' ry='{r * 0.32:.1f}' fill='#3d6b1f' opacity='0.3'/>")
    g.append(f"<path d='{borla(r * 1.08, t)}' fill='#eef8e4' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='{borla(r * 0.92, t + 1, 11, 0.07)}' fill='#4fa86a' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<circle cx='0' cy='{r * 0.05:.1f}' r='{r * 0.6:.1f}' fill='#2f8a63'/>")
    for i, (a, d) in enumerate(((30, 0.55), (150, 0.6), (260, 0.5), (330, 0.65), (200, 0.3))):
        g.append(f"<circle cx='{r * d * math.cos(math.radians(a)):.1f}' cy='{r * d * math.sin(math.radians(a)) * 0.8:.1f}' r='{r * 0.1:.1f}' fill='#bfe8a0' opacity='0.8'/>")
    s = r / 34
    g.append(ojos(0, -r * 0.12, s, t, 0.9, mira=0))
    feliz = seg(t, 7.2, 7.5)
    g.append(f"<path d='M {-9 * s:.1f} {r * 0.2:.1f} Q 0 {r * 0.2 + (7 + 8 * feliz) * s:.1f} {9 * s:.1f} {r * 0.2:.1f}' "
             f"fill='{mix('#2f8a63', '#c94b4b', feliz)}' stroke='{INK}' stroke-width='{3.5 * min(s, 1.6):.1f}' stroke-linecap='round'/>")
    for ex in (-18, 18):
        g.append(f"<ellipse cx='{ex * s:.1f}' cy='{r * 0.12:.1f}' rx='{5 * s:.1f}' ry='{3 * s:.1f}' fill='#ff8fa3' opacity='0.6'/>")
    g.append("</g>")
    return "".join(g)


def matraz(x, y, s, col, t, fase):
    g = [f"<g transform='translate({x},{y}) scale({s})'>"]
    g.append(f"<path d='M -14 -110 L -14 -50 L -55 20 Q -62 34 -46 34 L 46 34 Q 62 34 55 20 L 14 -50 L 14 -110 Z' fill='#e6f6ff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M -34 -10 L -55 20 Q -62 34 -46 34 L 46 34 Q 62 34 55 20 L 34 -10 Z' fill='{col}'/>")
    g.append(f"<path d='M -14 -110 L -14 -50 L -55 20 Q -62 34 -46 34 L 46 34 Q 62 34 55 20 L 14 -50 L 14 -110' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-22' y='-122' width='44' height='16' rx='6' fill='#c9a27a' stroke='{INK}' stroke-width='6'/>")
    for i in range(3):
        k = ((t * 0.7 + fase + i / 3) % 1)
        g.append(f"<circle cx='{8 * math.sin(k * 9 + i):.1f}' cy='{lerp(20, -100, k):.1f}' r='{lerp(7, 3, k):.1f}' fill='#fff' opacity='{0.9 * (1 - k):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.2, 7.9)
    # pared del laboratorio: verde menta suave; en la revelación baja la luz
    top = mix("#bfe3dc", "#1f3b4d", rev * 0.85); low = mix("#e3f3ec", "#2c5466", rev * 0.85)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='brillo'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95 * rev:.3f}'/>"
         f"<stop offset='0.45' stop-color='#ffe27a' stop-opacity='{0.6 * rev:.3f}'/><stop offset='1' stop-color='#ffb84d' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='luz'><stop offset='0' stop-color='#fff8d8' stop-opacity='0.55'/><stop offset='1' stop-color='#fff8d8' stop-opacity='0'/></radialGradient>",
         f"<clipPath id='agar'><ellipse cx='{PX}' cy='{PY}' rx='{PRX}' ry='{PRY}'/></clipPath>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # azulejos muy suaves en la parte baja de la pared
    for yy in range(1000, 1300, 70):
        s.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='{mix('#a9d3ca', '#2a4a5c', rev * 0.85)}' stroke-width='4'/>")
    z = 1 + 0.2 * seg(t, 7.2, 8.2) + 0.03 * seg(t, 0, 7.2)
    c = [f"<circle cx='540' cy='1250' r='700' fill='url(#luz)' opacity='{1 - rev:.2f}'/>"]
    # estante con matraces
    c.append(f"<rect x='-20' y='1160' width='1120' height='26' rx='6' fill='#b9824e' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(matraz(110, 1126, 0.95, '#ff7aa8', t, 0.0))
    c.append(matraz(245, 1126, 0.7, '#7ac8ff', t, 0.4))
    c.append(matraz(850, 1126, 0.75, '#ffd23f', t, 0.7))
    c.append(matraz(975, 1126, 0.95, '#9be37a', t, 0.2))
    # mesa de madera
    c.append(f"<path d='M -20 1300 L 1100 1300 L 1100 1800 L -20 1800 Z' fill='{mix('#d9a066', '#8a6a4a', rev * 0.6)}' stroke='{INK}' stroke-width='{LW}'/>")
    for yy in (1390, 1520, 1660):
        c.append(f"<path d='M 0 {yy} Q 300 {yy - 12} 600 {yy} T 1080 {yy}' fill='none' stroke='{mix('#c08750', '#76583a', rev * 0.6)}' stroke-width='6'/>")
    c.append(f"<rect x='-20' y='1800' width='1120' height='140' fill='{mix('#a8693a', '#6a4a30', rev * 0.6)}' stroke='{INK}' stroke-width='{LW}'/>")
    # placa de Petri: sombra, pared de cristal, agar
    c.append(f"<ellipse cx='{PX}' cy='{PY + 70}' rx='{PRX + 60}' ry='{PRY + 40}' fill='#5a3414' opacity='0.28'/>")
    c.append(f"<path d='M {PX - PRX - 22} {PY} L {PX - PRX - 22} {PY + 42} A {PRX + 22} {PRY + 14} 0 0 0 {PX + PRX + 22} {PY + 42} L {PX + PRX + 22} {PY} Z' fill='#cfeefc' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    c.append(f"<ellipse cx='{PX}' cy='{PY}' rx='{PRX + 22}' ry='{PRY + 14}' fill='#e8f8ff' stroke='{INK}' stroke-width='{LW}'/>")
    agar = mix('#f4c95d', '#ffd86b', rev)
    c.append(f"<ellipse cx='{PX}' cy='{PY}' rx='{PRX}' ry='{PRY}' fill='{agar}' stroke='{INK}' stroke-width='5'/>")
    # círculo limpio alrededor del moho
    R = zona(t)
    if R > 2:
        c.append(f"<g clip-path='url(#agar)'>"
                 f"<ellipse cx='{MX}' cy='{MY}' rx='{R:.1f}' ry='{R * K:.1f}' fill='{mix('#fbe7a8', '#fff6cf', rev)}' "
                 f"stroke='{mix('#e0a93a', '#ffffff', rev)}' stroke-width='5' stroke-dasharray='14 10'/>"
                 f"<ellipse cx='{MX}' cy='{MY}' rx='{R * 1.25 + 40 * pulso(t, 0.8) * rev:.1f}' ry='{(R * 1.25 + 40 * pulso(t, 0.8) * rev) * K:.1f}' fill='url(#brillo)'/></g>")
    # brillo del cristal
    c.append(f"<path d='M {PX - PRX + 40} {PY - PRY + 50} Q {PX - PRX + 120} {PY - PRY - 5} {PX - 120} {PY - PRY - 4}' fill='none' stroke='#fff' stroke-width='10' stroke-linecap='round' opacity='0.8'/>")
    # bacterias (ordenadas por profundidad)
    for x, y, sc, fase, _, td in sorted(BACT, key=lambda b: b[1]):
        c.append(bacteria(x, y, sc, fase, t, td))
    # rayos de luz en la revelación
    if rev > 0:
        for i in range(12):
            a = math.radians(i * 30 + t * 25)
            r1, r2 = 150, 150 + 320 * rev
            c.append(f"<path d='M {MX + r1 * math.cos(a):.1f} {MY - 40 + r1 * math.sin(a) * 0.7:.1f} "
                     f"L {MX + r2 * math.cos(a - 0.06):.1f} {MY - 40 + r2 * math.sin(a - 0.06) * 0.7:.1f} "
                     f"L {MX + r2 * math.cos(a + 0.06):.1f} {MY - 40 + r2 * math.sin(a + 0.06) * 0.7:.1f} Z' fill='#fff3b0' opacity='{0.5 * rev:.2f}'/>")
    c.append(moho(t))
    # destellos alrededor del moho
    if rev > 0:
        for i in range(8):
            a = i * 0.785 + t * 1.5
            rr = 245 + 20 * math.sin(t * 5 + i)
            x, y = MX + rr * math.cos(a), MY - 50 + rr * 0.6 * math.sin(a)
            sz = 16 * rev * (0.7 + 0.3 * math.sin(t * 8 + i))
            c.append(f"<path d='M {x:.1f} {y - sz:.1f} L {x + sz * 0.3:.1f} {y - sz * 0.3:.1f} L {x + sz:.1f} {y:.1f} L {x + sz * 0.3:.1f} {y + sz * 0.3:.1f} "
                     f"L {x:.1f} {y + sz:.1f} L {x - sz * 0.3:.1f} {y + sz * 0.3:.1f} L {x - sz:.1f} {y:.1f} L {x - sz * 0.3:.1f} {y - sz * 0.3:.1f} Z' fill='#fff' stroke='{INK}' stroke-width='3'/>")
    # tapa de cristal que se retira hacia la derecha (0-1,8 s)
    lk = seg(t, 0, 1.8)
    if lk < 1:
        lx, ly = PX + 900 * lk, PY - 60 - 50 * math.sin(math.pi * lk)
        c.append(f"<g opacity='0.85'><path d='M {lx - PRX - 32} {ly} L {lx - PRX - 32} {ly + 34} A {PRX + 32} {PRY + 20} 0 0 0 {lx + PRX + 32} {ly + 34} L {lx + PRX + 32} {ly} Z' fill='#d8f2ff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<ellipse cx='{lx}' cy='{ly}' rx='{PRX + 32}' ry='{PRY + 20}' fill='#eefaff' fill-opacity='0.55' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M {lx - 250} {ly - 110} Q {lx - 120} {ly - 175} {lx + 60} {ly - 180}' fill='none' stroke='#fff' stroke-width='12' stroke-linecap='round'/></g>")
    # polvo flotando en la luz
    for px, py, pr, sp in DUST:
        yy = (py - t * sp) % 950 + 980
        c.append(f"<circle cx='{px + 18 * math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='{mix('#ffffff', '#ffe9a0', rev)}' opacity='0.5'/>")
    s.append(zoom(MX, 1420, z, "".join(c)))
    s.append("</svg>")
    return "".join(s)
