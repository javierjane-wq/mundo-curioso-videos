"""2026-11-12-c2 · Naturaleza/Química: el color de las hortensias depende del suelo.

Una hortensia de flores rosas crece en un jardín (vista con el suelo en corte). Una regadera
moja la tierra, la tierra se vuelve ácida y unas chispitas azules (el aluminio) suben por las
raíces y el tallo. En la revelación todas las flores se vuelven AZULES con un golpe de luz.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45   # las flores cambian de rosa a azul
MUSICA = 5

rng = np.random.default_rng(23)
BX, BY = 500, 1520          # base de la mata
# cabezuelas: (x, y, radio, fase, retraso de cambio)
HEADS = [(330, 1150, 98, 0.0, 0.10), (690, 1140, 98, 1.3, 0.18), (205, 1295, 86, 2.1, 0.0),
         (800, 1290, 86, 0.7, 0.26), (500, 1235, 132, 1.7, 0.05)]


def _florets(R, seed):
    """Posiciones de las florecillas (espiral de girasol) dentro de una cabezuela."""
    r = np.random.default_rng(seed); out = []
    n = int(R * R / 520)
    for i in range(n):
        rr = R * 0.8 * math.sqrt((i + 0.5) / n); a = i * 2.39996
        out.append((rr * math.cos(a), rr * math.sin(a) * 0.92, r.uniform(0.85, 1.1) * R * 0.3,
                    r.uniform(0, 90), r.random() < 0.5))
    out.sort(key=lambda f: f[1])
    return out


FLORETS = [_florets(h[2], 40 + i) for i, h in enumerate(HEADS)]
# hojas: (x base, y base, ángulo, largo, ancho)
LEAVES = [(470, 1500, -168, 230, 120), (530, 1500, -12, 230, 120), (480, 1470, -140, 200, 110),
          (520, 1470, -40, 200, 110), (420, 1390, -175, 170, 95), (580, 1385, -5, 170, 95),
          (300, 1360, -120, 140, 80), (700, 1355, -60, 140, 80), (500, 1460, -95, 150, 90)]
CLOUDS = [(160, 560, 1.3, 9), (760, 330, 1.0, 13), (980, 760, 0.8, 7), (420, 180, 0.7, 11)]
PEBBLES = [(rng.uniform(30, W - 30), rng.uniform(1600, 1900), rng.uniform(10, 24)) for _ in range(16)]
SPARKS = [(rng.uniform(820, 1020), rng.uniform(1600, 1820), rng.uniform(0, 0.9), int(rng.integers(0, 5)),
           rng.uniform(13, 19)) for _ in range(26)]
GLINTS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28), int(rng.integers(0, 5))) for _ in range(30)]
FENCE = list(range(-20, W + 80, 92))

PINK = ("#ffb0d4", "#ff79b4", "#e3558f")
BLUE = ("#a9c8ff", "#5f8dff", "#3a5ed6")


def colores(k):
    return tuple(mix(p, b, k) for p, b in zip(PINK, BLUE))


def leaf(x, y, ang, L, Wd, sway):
    """Hoja grande de hortensia: ovalada, punta aguda, borde dentado y nervio central."""
    top, bot = [], []
    N = 14
    for i in range(N + 1):
        s = i / N
        w = Wd * 0.5 * math.sin(math.pi * s) ** 0.75 * (1 - 0.25 * s)
        tooth = 6 if (i % 2 and 0 < i < N) else 0
        top.append((s * L, -(w + tooth))); bot.append((s * L, w + tooth))
    pts = top + bot[::-1]
    d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + " Z"
    return (f"<g transform='translate({x},{y}) rotate({ang + sway:.1f})'>"
            f"<path d='{d}' fill='#3fa34d' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M8 0 Q{L*0.5:.0f} {-Wd*0.06:.0f} {L*0.92:.0f} 0' fill='none' stroke='#2c7a39' stroke-width='6' stroke-linecap='round'/>"
            + "".join(f"<path d='M{L*s:.0f} 0 L{L*(s+0.12):.0f} {sg*Wd*0.28:.0f}' stroke='#2c7a39' stroke-width='4' stroke-linecap='round'/>"
                      for s in (0.25, 0.45, 0.65) for sg in (-1, 1))
            + f"<path d='M{L*0.2:.0f} {-Wd*0.2:.0f} Q{L*0.4:.0f} {-Wd*0.32:.0f} {L*0.6:.0f} {-Wd*0.24:.0f}' fill='none' stroke='#7fd36b' stroke-width='5' stroke-linecap='round' opacity='0.8'/>"
            "</g>")


def floret(fx, fy, r, rot, light, cols):
    c = cols[0] if light else cols[1]
    g = [f"<g transform='translate({fx:.1f},{fy:.1f}) rotate({rot:.0f})'>"]
    for a in (0, 90, 180, 270):
        g.append(f"<ellipse cx='{r*0.55:.1f}' cy='0' rx='{r*0.58:.1f}' ry='{r*0.46:.1f}' fill='{c}' stroke='{INK}' stroke-width='4' transform='rotate({a})'/>")
    g.append(f"<circle r='{r*0.2:.1f}' fill='{cols[2]}' stroke='{INK}' stroke-width='3'/></g>")
    return "".join(g)


def head(i, t, k):
    x, y, R, ph, _ = HEADS[i]
    cols = colores(k)
    sc = 0.45 + 0.55 * seg(t, 0.1 + i * 0.12, 1.3 + i * 0.12)
    sc *= 1 + 0.06 * math.sin(math.pi * clamp((t - REVELACION) / 0.5)) if t > REVELACION else 1
    bob = 5 * math.sin(t * 2.1 + ph)
    g = [f"<g transform='translate({x},{y + bob:.1f}) scale({sc:.3f})'>",
         f"<circle r='{R}' fill='{cols[2]}' stroke='{INK}' stroke-width='{LW}'/>"]
    for fx, fy, r, rot, light in FLORETS[i]:
        g.append(floret(fx, fy, r, rot + 8 * math.sin(t * 1.5 + fx), light, cols))
    if i == 4:   # carita en la cabezuela del centro
        blink = 0.12 if (t % 3.3) < 0.13 or abs(t - 6.2) < 0.06 else 1.0
        look_y = 10 * seg(t, 5.0, 5.6) * (1 - seg(t, 7.3, 7.6))
        look_x = 9 * seg(t, 5.0, 5.6) * (1 - seg(t, 7.3, 7.6))
        big = 1 + 0.18 * seg(t, REVELACION, REVELACION + 0.4)
        for ex in (-40, 40):
            g.append(f"<g transform='translate({ex},-14) scale({big:.3f},{big*blink:.3f})'>"
                     f"<ellipse rx='24' ry='29' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='{look_x:.1f}' cy='{look_y:.1f}' r='14' fill='{INK}'/>"
                     f"<circle cx='{look_x - 5:.1f}' cy='{look_y - 6:.1f}' r='5' fill='#fff'/></g>")
        sm = lerp(16, 34, seg(t, REVELACION, REVELACION + 0.4))
        if t > REVELACION:
            g.append(f"<path d='M-30 30 Q0 {30 + sm:.0f} 30 30 Z' fill='#7a2a3a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        else:
            g.append(f"<path d='M-26 32 Q0 {32 + sm:.0f} 26 32' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
        for cx in (-70, 70):
            g.append(f"<ellipse cx='{cx}' cy='22' rx='16' ry='9' fill='{mix(cols[2], '#ff3d6e', 0.5)}' opacity='0.7'/>")
    g.append("</g>")
    return "".join(g)


def bush(t):
    rot = 1.6 * math.sin(t * 1.4)
    grow = lerp(0.82, 1.0, seg(t, 0, 1.4))
    ks = [seg(t, 7.3 + h[4], 7.9 + h[4]) for h in HEADS]
    g = [f"<g transform='translate({BX},{BY}) rotate({rot:.2f}) scale({grow:.3f}) translate({-BX},{-BY})'>"]
    # tallos
    for x, y, R, ph, _ in HEADS:
        d = f"M{BX} {BY} Q{(BX + x) / 2:.0f} {BY - 60} {x} {y + 20}"
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='24' stroke-linecap='round'/>")
        g.append(f"<path d='{d}' fill='none' stroke='#5a8f3a' stroke-width='11' stroke-linecap='round'/>")
    for j, (x, y, a, L, Wd) in enumerate(LEAVES):
        g.append(leaf(x, y, a, L, Wd, 4 * math.sin(t * 2.3 + j)))
    for i in (0, 1, 2, 3, 4):
        g.append(head(i, t, ks[i]))
    g.append("</g>")
    return "".join(g)


def can(t):
    """Regadera metálica: entra por la derecha, se inclina y riega la tierra."""
    x = lerp(1320, 990, seg(t, 4.6, 5.4)) + lerp(0, 380, seg(t, 7.6, 8.5))
    tilt = -32 * seg(t, 5.4, 5.8) * (1 - seg(t, 7.2, 7.6))
    y = 1120 + 6 * math.sin(t * 5)
    if x > 1300: return ""
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({tilt:.1f})'>"
            f"<path d='M-70 -10 L-180 -70 L-168 -86 L-56 -40 Z' fill='#4fb6c8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<ellipse cx='-180' cy='-80' rx='16' ry='26' transform='rotate(-30 -180 -80)' fill='#8fe0ec' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M70 -60 Q150 -60 140 20 Q130 70 80 60' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>"
            f"<path d='M70 -60 Q150 -60 140 20 Q130 70 80 60' fill='none' stroke='#3a95a8' stroke-width='12' stroke-linecap='round'/>"
            f"<path d='M-85 -70 L85 -70 L95 90 Q0 110 -95 90 Z' fill='#5fc6d8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<rect x='-90' y='-30' width='182' height='26' fill='#3a95a8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-60 -50 L-55 70' stroke='#b9f0f7' stroke-width='12' stroke-linecap='round' opacity='0.8'/>"
            f"<path d='M-60 -70 Q0 -120 60 -70' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
            f"<path d='M-60 -70 Q0 -120 60 -70' fill='none' stroke='#3a95a8' stroke-width='9' stroke-linecap='round'/>"
            "</g>")


def drops(t):
    if not (5.75 < t < 7.5): return ""
    s = []
    for i in range(14):
        ph = (t * 1.8 + i / 14) % 1
        st = 5.75 + i / 14 / 1.8
        if t - ph / 1.8 < 5.75 or t - ph / 1.8 > 7.25: continue
        x0, y0 = 862 + (i % 3) * 14, 1250
        yy = y0 + ph * 290; xx = x0 - 18 * ph + (i % 2) * 8
        s.append(f"<path d='M{xx:.0f} {yy - 18:.0f} Q{xx + 11:.0f} {yy + 2:.0f} {xx:.0f} {yy + 8:.0f} Q{xx - 11:.0f} {yy + 2:.0f} {xx:.0f} {yy - 18:.0f} Z' fill='#7fd8ff' stroke='{INK}' stroke-width='4'/>")
    return "".join(s)


def star(x, y, r, col):
    p = " ".join(f"{x + (r if j % 2 == 0 else r * 0.4) * math.cos(j * math.pi / 4 - math.pi / 2):.1f},"
                 f"{y + (r if j % 2 == 0 else r * 0.4) * math.sin(j * math.pi / 4 - math.pi / 2):.1f}" for j in range(8))
    return f"<polygon points='{p}' fill='{col}' stroke='{INK}' stroke-width='3' stroke-linejoin='round'/>"


def sparks(t):
    """Chispitas azules (aluminio) que viajan por la tierra, las raíces y el tallo hasta las flores."""
    s = []
    for sx, sy, dl, hi, r in SPARKS:
        u = seg(t, 6.0 + dl, 7.55 + dl * 0.15)
        if u <= 0 or u >= 1: continue
        hx, hy = HEADS[hi][0], HEADS[hi][1]
        pts = [(sx, sy), (BX + (sx - BX) * 0.25, 1700), (BX, BY), (hx, hy)]
        q = u * 3; k = min(2, int(q)); f = q - k
        x = lerp(pts[k][0], pts[k + 1][0], f); y = lerp(pts[k][1], pts[k + 1][1], f)
        s.append(star(x, y, r * (1 + 0.3 * math.sin(t * 20 + sx)), "#8fe3ff"))
    return "".join(s)


def butterfly(t):
    x = 190 + 130 * math.sin(t * 0.7); y = 1060 + 35 * math.sin(t * 1.9)
    fl = 0.25 + 0.75 * abs(math.sin(t * 9))
    wing = "M0 0 Q-60 -70 -90 -30 Q-80 10 0 0 Z M0 0 Q-55 50 -40 60 Q-10 50 0 0 Z"
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({10 * math.sin(t * 2):.1f})'>"
            f"<g transform='scale({fl:.2f},1)'><path d='{wing}' fill='#ffcf3f' stroke='{INK}' stroke-width='5'/></g>"
            f"<g transform='scale({-fl:.2f},1)'><path d='{wing}' fill='#ffa32b' stroke='{INK}' stroke-width='5'/></g>"
            f"<ellipse rx='8' ry='26' fill='{INK}'/>"
            f"<path d='M-3 -24 Q-12 -44 -20 -48 M3 -24 Q12 -44 20 -48' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")


def frame(t):
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.5)
    acid = seg(t, 6.0, 7.4)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#5fb4f2', '#4b8ff0', rev)}'/>"
            f"<stop offset='1' stop-color='{mix('#cdeeff', '#e3f2ff', rev)}'/></linearGradient>"
            "<radialGradient id='sun'><stop offset='0' stop-color='#fff8d0' stop-opacity='0.9'/><stop offset='1' stop-color='#fff2a0' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='acid' cx='0.82' cy='0.2' r='{lerp(0.05, 1.1, acid):.3f}'><stop offset='0' stop-color='#6a5bd8' stop-opacity='0.55'/>"
            "<stop offset='0.7' stop-color='#6a5bd8' stop-opacity='0.3'/><stop offset='1' stop-color='#6a5bd8' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='halo'><stop offset='0' stop-color='#ffffff' stop-opacity='0.9'/><stop offset='0.5' stop-color='#bcd6ff' stop-opacity='0.5'/>"
            "<stop offset='1' stop-color='#bcd6ff' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION - 0.1, 10)
    c = []
    # sol suave y nubes
    c.append(f"<circle cx='930' cy='170' r='260' fill='url(#sun)'/>")
    c.append(f"<circle cx='930' cy='170' r='80' fill='#fff1a6' stroke='#ffd35a' stroke-width='8'/>")
    for cx, cy, sc, sp in CLOUDS:
        dx = (cx + t * sp) % 1400 - 200
        c.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})'><path d='M0 50 Q-10 0 50 5 Q80 -40 140 -5 Q200 -30 220 25 Q260 30 250 60 Z' "
                 f"fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='0.95'/></g>")
    # colinas y valla
    c.append(f"<path d='M0 1080 Q250 990 520 1060 T1080 1040 L1080 1600 L0 1600 Z' fill='#9ad86a' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(f"<path d='M0 1180 Q300 1120 620 1170 T1080 1150 L1080 1600 L0 1600 Z' fill='#7cc456' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(f"<rect x='-20' y='1300' width='1120' height='22' fill='#fff6e6' stroke='{INK}' stroke-width='6'/>")
    c.append(f"<rect x='-20' y='1400' width='1120' height='22' fill='#fff6e6' stroke='{INK}' stroke-width='6'/>")
    for fx in FENCE:
        c.append(f"<path d='M{fx} 1500 L{fx} 1270 L{fx + 28} 1240 L{fx + 56} 1270 L{fx + 56} 1500 Z' fill='#fffaf0' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # halo de la revelación detrás de la mata
    if rev > 0:
        c.append(f"<g transform='translate({BX},1240) rotate({t * 18:.1f})' opacity='{0.75 * rev:.2f}'>"
                 + "".join(f"<path d='M0 0 L{900 * math.cos(math.radians(a - 5)):.0f} {900 * math.sin(math.radians(a - 5)):.0f} "
                           f"L{900 * math.cos(math.radians(a + 5)):.0f} {900 * math.sin(math.radians(a + 5)):.0f} Z' fill='#d9e8ff'/>" for a in range(0, 360, 30))
                 + "</g>")
        c.append(f"<circle cx='{BX}' cy='1240' r='{lerp(200, 520, rev):.0f}' fill='url(#halo)' opacity='{rev:.2f}'/>")
    # tierra en corte
    soil = "M0 1545 Q270 1525 540 1545 T1080 1540 L1080 1920 L0 1920 Z"
    c.append(f"<path d='{soil}' fill='#8a5634' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(f"<path d='M0 1680 Q300 1660 560 1690 T1080 1675 L1080 1920 L0 1920 Z' fill='#77462a'/>")
    for px, py, pr in PEBBLES:
        c.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='{pr:.0f}' ry='{pr * 0.65:.0f}' fill='#a87450' stroke='{INK}' stroke-width='5'/>")
    # raíces
    roots = [f"M{BX} 1530 Q{BX - 20} 1640 {BX - 120} 1760 Q{BX - 160} 1820 {BX - 230} 1840",
             f"M{BX} 1530 Q{BX + 20} 1650 {BX + 140} 1740 Q{BX + 200} 1790 {BX + 300} 1800",
             f"M{BX} 1540 L{BX + 5} 1860", f"M{BX - 60} 1700 Q{BX - 140} 1690 {BX - 200} 1650",
             f"M{BX + 90} 1700 Q{BX + 170} 1660 {BX + 230} 1640"]
    for d in roots:
        c.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>")
        c.append(f"<path d='{d}' fill='none' stroke='#e2bf8e' stroke-width='9' stroke-linecap='round'/>")
    if acid > 0:
        c.append(f"<path d='{soil}' fill='url(#acid)'/>")
    # césped
    c.append(f"<path d='M0 1500 Q270 1480 540 1500 T1080 1495 L1080 1555 Q800 1540 540 1552 T0 1550 Z' fill='#5fb948' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for gx in range(20, W, 70):
        sw = 6 * math.sin(t * 3 + gx)
        c.append(f"<path d='M{gx} 1505 L{gx + 8 + sw:.0f} 1465 L{gx + 18} 1505 L{gx + 30 + sw:.0f} 1475 L{gx + 38} 1505' fill='#5fb948' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # charquito donde cae el agua
    wet = seg(t, 5.9, 6.6)
    if wet > 0:
        c.append(f"<ellipse cx='875' cy='1540' rx='{80 * wet:.0f}' ry='{16 * wet:.0f}' fill='#4e7fb8' stroke='{INK}' stroke-width='5' opacity='0.9'/>")
    c.append(bush(t))
    c.append(sparks(t))
    c.append(drops(t))
    c.append(can(t))
    c.append(butterfly(t))
    # destellos alrededor de las flores tras la revelación
    if t > REVELACION:
        for gx, gy, ph, hi in GLINTS:
            hx, hy, R = HEADS[hi][0], HEADS[hi][1], HEADS[hi][2]
            a = clamp((t - REVELACION) * 3) * (0.5 + 0.5 * math.sin(t * 7 + ph))
            if a > 0.1:
                c.append(f"<g opacity='{a:.2f}'>{star(hx + gx * R * 1.4, hy + gy * R * 1.3, 12 + 6 * a, '#ffffff')}</g>")
    s.append(zoom(BX, 1250, z, "".join(c)))
    flash = clamp(1 - abs(t - REVELACION) / 0.35)
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.55 * flash:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
