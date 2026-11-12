"""Versión por código de 2026-11-12-px: el lagarto basilisco corre sobre el agua a dos patas (unos 4,5 m).

Basilisco original (verde, cresta en la cabeza, vela en el lomo, cola larga, patas traseras largas con
dedos largos) descansa en una rama sobre un río de la selva. Llega una serpiente de dibujos por la rama,
el lagarto salta al agua, se levanta sobre las patas traseras y CORRE por la superficie dejando
salpicaduras y anillos. En la revelación: zoom, corona de agua y las "bolsas de aire" bajo sus pies;
al final salta a la otra orilla y posa.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.5    # zoom + bolsas de aire bajo los pies
MUSICA = 8

G = "#5cc94a"        # verde del lagarto
G_DARK = "#3c9a34"
G_LIGHT = "#c9f27a"
CREST = "#8ee36a"

WATER_Y = 1640       # línea donde pisan los pies al correr
BRANCH_Y = 1100
S_BRANCH, S_RUN = 1.05, 1.15
T_JUMP0, T_JUMP1 = 4.35, 5.0
T_RUN1 = 9.0
T_HOP1 = 9.4
X_RUN0, X_RUN1, X_END = 360, 620, 765
BANK_Y = 1560

rng = np.random.default_rng(12)
LEAVES_BG = [(rng.uniform(-60, W + 60), rng.uniform(980, 1180), rng.uniform(90, 160)) for _ in range(14)]
SPARK = [(rng.uniform(0, W), rng.uniform(1300, 1900), rng.uniform(0, 6.28)) for _ in range(26)]
DROPS = [(rng.uniform(-1, 1), rng.uniform(0.6, 1.0), rng.uniform(5, 10)) for _ in range(6)]
MOTES = [(rng.uniform(0, W), rng.uniform(0, 1100), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(24)]


# ---------- trayectoria del lagarto ----------
def pose(t):
    """Devuelve X, Y (cadera), escala, 'up' (0 tumbado, 1 de pie) y si está corriendo."""
    if t < T_JUMP0:
        return 330, BRANCH_Y - 50 * S_BRANCH, S_BRANCH, 0.0, False
    if t < T_JUMP1:
        k = (t - T_JUMP0) / (T_JUMP1 - T_JUMP0)
        s = lerp(S_BRANCH, S_RUN, k)
        y0 = BRANCH_Y - 50 * S_BRANCH
        y1 = WATER_Y - 125 * S_RUN
        y = lerp(y0, y1, k * k) - 160 * math.sin(math.pi * k) * (1 - k)
        return lerp(330, X_RUN0, k), y, s, ease(k), False
    if t < T_RUN1:
        k = (t - T_JUMP1) / (T_RUN1 - T_JUMP1)
        return lerp(X_RUN0, X_RUN1, k), WATER_Y - 125 * S_RUN + 4 * math.sin(t * 44), S_RUN, 1.0, True
    k = seg(t, T_RUN1, T_HOP1)
    x = lerp(X_RUN1, X_END, k)
    y = lerp(WATER_Y, BANK_Y, k) - 125 * S_RUN - 120 * math.sin(math.pi * min(1, (t - T_RUN1) / (T_HOP1 - T_RUN1)))
    return x, y, S_RUN, 1.0, False


def step_phase(t):
    return (t - T_JUMP1) * 2 * math.pi * 6.5


def foot_pos(ph, up, running):
    """Pie respecto a la cadera (sin escala)."""
    if running:
        fx, fy = 80 * math.cos(ph), 125 - 50 * max(0.0, math.sin(ph))
    else:
        fx, fy = lerp(-15, 10, up), lerp(50, 125, up)
    return fx, fy


def hind_leg(ph, up, running, col):
    fx, fy = foot_pos(ph, up, running)
    kx, ky = fx / 2 + lerp(55, 45, up), fy / 2 - lerp(15, 8, up)
    d = f"M0 0 L{kx:.1f} {ky:.1f} L{fx:.1f} {fy:.1f}"
    s = [f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round' stroke-linejoin='round'/>",
         f"<path d='{d}' fill='none' stroke='{col}' stroke-width='19' stroke-linecap='round' stroke-linejoin='round'/>"]
    # dedos largos con flecos
    for ang, ln in ((-14, 62), (4, 70), (20, 54)):
        a = math.radians(ang)
        tx, ty = fx + ln * math.cos(a), fy + ln * math.sin(a) * 0.5 + 2
        s.append(f"<line x1='{fx:.1f}' y1='{fy:.1f}' x2='{tx:.1f}' y2='{ty:.1f}' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>")
        s.append(f"<line x1='{fx:.1f}' y1='{fy:.1f}' x2='{tx:.1f}' y2='{ty:.1f}' stroke='{col}' stroke-width='5' stroke-linecap='round'/>")
    return "".join(s)


def lizard(t):
    X, Y, S, up, running = pose(t)
    ph = step_phase(t) if running else 0.0
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    scared = seg(t, 3.6, 4.0) * (1 - seg(t, 5.2, 5.8))
    g = [f"<g transform='translate({X:.1f},{Y:.1f}) scale({S:.3f})'>"]
    # pata trasera lejana
    g.append(hind_leg(ph + math.pi, up, running, G_DARK))
    # cola (se ondula)
    wave = 14 * math.sin(t * 5) * (1 - up) + 10 * math.sin(t * 20) * up
    g.append(f"<g transform='rotate({-28 * up:.1f})'>")
    tail = f"M10 -5 Q-160 {25 + wave:.1f} -300 {-5 - wave:.1f} Q-380 {-25 + wave:.1f} -430 {10 + wave:.1f}"
    g.append(f"<path d='{tail}' fill='none' stroke='{INK}' stroke-width='36' stroke-linecap='round'/>")
    g.append(f"<path d='{tail}' fill='none' stroke='{G}' stroke-width='21' stroke-linecap='round'/>")
    for i in range(5):  # bandas oscuras en la cola
        x = -90 - i * 65
        g.append(f"<circle cx='{x}' cy='{12 + wave * (0.3 + i * 0.12) - i * 4:.1f}' r='6' fill='{G_DARK}'/>")
    g.append("</g>")
    # cuerpo (gira al ponerse de pie)
    g.append(f"<g transform='rotate({-55 * up:.1f})'>")
    # vela del lomo
    sail = "M5 -45 L22 -118 L48 -60 L72 -132 L98 -62 L122 -118 L148 -52 Z"
    g.append(f"<path d='{sail}' fill='{CREST}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for x0, x1 in ((22, 30), (72, 74), (122, 120)):
        g.append(f"<line x1='{x0}' y1='-112' x2='{x1}' y2='-55' stroke='{G_DARK}' stroke-width='5'/>")
    g.append(f"<ellipse cx='85' cy='-12' rx='118' ry='50' fill='{G}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M10 12 Q85 42 170 14 Q120 30 85 32 Q40 30 10 12 Z' fill='{G_LIGHT}'/>")
    for x in (40, 85, 130):
        g.append(f"<path d='M{x} -50 Q{x + 12} -25 {x} -2' fill='none' stroke='{G_DARK}' stroke-width='7' stroke-linecap='round'/>")
    # pata delantera (pegada al pecho al correr, agarrada a la rama tumbado)
    ex, ey = lerp(175, 195, up), lerp(50, 40, up)
    hx, hy = lerp(185, 230, up), lerp(62, 20, up)
    arm = f"M160 8 L{ex:.0f} {ey:.0f} L{hx:.0f} {hy:.0f}"
    g.append(f"<path d='{arm}' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='{arm}' fill='none' stroke='{G}' stroke-width='13' stroke-linecap='round' stroke-linejoin='round'/>")
    # cabeza (se endereza para mirar al frente)
    g.append(f"<g transform='translate(222,-42) rotate({45 * up:.1f})'>")
    g.append(f"<path d='M-45 -22 Q-70 -120 -12 -128 Q12 -70 22 -36 Z' fill='{CREST}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<line x1='-28' y1='-90' x2='-6' y2='-42' stroke='{G_DARK}' stroke-width='5'/>")
    g.append(f"<path d='M-55 0 Q-50 -48 5 -50 Q60 -50 88 -12 Q98 8 80 22 Q30 40 -25 34 Q-58 28 -55 0 Z' fill='{G}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-20 30 Q30 38 82 18' fill='none' stroke='{G_LIGHT}' stroke-width='9' stroke-linecap='round'/>")
    mouth_open = 10 * seg(t, 7.4, 7.9)
    g.append(f"<path d='M28 16 Q55 {24 + mouth_open:.1f} 80 12' fill='{'#7a2b2b' if mouth_open > 1 else 'none'}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<circle cx='72' cy='-14' r='4' fill='{INK}'/>")
    er = 26 + 6 * scared
    g.append(f"<g transform='translate(14,-14) scale(1,{blink})'>"
             f"<circle r='{er:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='6' r='{15 - 3 * scared:.1f}' fill='#e8a317'/><circle cx='7' r='{9 - 3 * scared:.1f}' fill='{INK}'/>"
             f"<circle cx='1' cy='-8' r='6' fill='#fff'/><circle cx='12' cy='5' r='3' fill='#fff'/></g>")
    g.append(f"<path d='M-14 {-44 - 8 * scared:.1f} Q14 {-56 - 8 * scared:.1f} 40 -42' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    g.append("</g></g>")
    # pata trasera cercana
    g.append(hind_leg(ph, up, running, G))
    g.append("</g>")
    return "".join(g), X, Y, S, running, ph


# ---------- serpiente de dibujos ----------
def snake(t):
    hx = lerp(-200, 170, seg(t, 2.4, 4.1)) + lerp(0, 90, seg(t, 4.6, 6.0))
    if hx < -200:
        return ""
    sur = seg(t, 4.5, 5.0)
    pts = []
    for i in range(14):
        x = hx - i * 42
        y = BRANCH_Y - 22 + 10 * math.sin(i * 0.9 - t * 6)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    s = [f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='52' stroke-linecap='round' stroke-linejoin='round'/>",
         f"<path d='{d}' fill='none' stroke='#e08a3c' stroke-width='36' stroke-linecap='round' stroke-linejoin='round'/>",
         f"<path d='{d}' fill='none' stroke='#8a4a24' stroke-width='36' stroke-dasharray='14 40' stroke-linejoin='round'/>"]
    lift = -40 * sur
    s.append(f"<g transform='translate({hx + 30:.0f},{BRANCH_Y - 40 + lift:.0f})'>")
    s.append(f"<ellipse rx='48' ry='34' fill='#e08a3c' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='18' cy='14' rx='26' ry='{8 + 10 * sur:.1f}' fill='#7a2b2b' stroke='{INK}' stroke-width='5'/>")
    for ex in (-8, 20):
        s.append(f"<circle cx='{ex}' cy='-14' r='{12 + 5 * sur:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{ex + 3}' cy='-13' r='5' fill='{INK}'/>")
    s.append("</g>")
    return "".join(s)


# ---------- escenario ----------
def leaf(x, y, sc, rot, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({rot:.1f}) scale({sc:.2f})'>"
            f"<path d='M0 0 Q60 -70 160 -20 Q80 40 0 0 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M8 -2 Q80 -30 150 -20' fill='none' stroke='{INK}' stroke-width='4'/></g>")


def background(t):
    s = []
    s.append(f"<rect width='{W}' height='{H}' fill='url(#sky)'/>")
    # rayos de sol
    for i in range(5):
        a = 0.10 + 0.05 * math.sin(t * 1.5 + i)
        x = 150 + i * 200
        s.append(f"<path d='M{x} -50 L{x + 120} -50 L{x + 380} 1250 L{x + 200} 1250 Z' fill='#fffbd0' opacity='{a:.2f}'/>")
    # árboles lejanos
    s.append(f"<path d='M0 1030 Q90 920 190 990 Q280 880 400 970 Q500 890 610 980 Q720 870 830 960 Q950 890 1080 970 L1080 1300 L0 1300 Z' fill='#4fa86a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1120 Q120 1040 240 1100 Q370 1020 500 1090 Q640 1020 760 1095 Q900 1030 1080 1090 L1080 1300 L0 1300 Z' fill='#3f9156' stroke='{INK}' stroke-width='{LW}'/>")
    for x in (120, 470, 860):
        s.append(f"<rect x='{x}' y='1080' width='34' height='200' fill='#7a5233' stroke='{INK}' stroke-width='7'/>")
    # orilla lejana
    s.append(f"<path d='M0 1250 Q270 1225 540 1245 T1080 1240 L1080 1300 L0 1300 Z' fill='#7cc35a' stroke='{INK}' stroke-width='{LW}'/>")
    # río
    s.append(f"<rect x='0' y='1275' width='{W}' height='{H - 1275}' fill='url(#water)'/>")
    s.append(f"<line x1='0' y1='1275' x2='{W}' y2='1275' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(9):
        y = 1330 + i * 68
        dx = (t * (30 + i * 4) + i * 170) % 1300 - 200
        s.append(f"<path d='M{dx:.0f} {y} q40 -12 80 0 t80 0' fill='none' stroke='#bff6f2' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
    for x, y, p in SPARK:
        a = max(0.0, math.sin(t * 4 + p))
        if a > 0.3:
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{4 + 3 * a:.1f}' fill='#fff' opacity='{a * 0.8:.2f}'/>")
    # rama (desde la izquierda)
    s.append(f"<path d='M-40 {BRANCH_Y - 30} Q250 {BRANCH_Y - 45} 560 {BRANCH_Y - 10} L565 {BRANCH_Y + 18} Q250 {BRANCH_Y - 8} -40 {BRANCH_Y + 25} Z' fill='#8a5a33' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(leaf(470, BRANCH_Y - 20, 0.7, -30 + 4 * math.sin(t * 2), '#5fbf45'))
    s.append(leaf(540, BRANCH_Y, 0.6, 20 + 4 * math.sin(t * 2.3), '#4fae3c'))
    return "".join(s)


def bank(t):
    s = []
    s.append(f"<path d='M720 1920 L705 1640 Q740 {BANK_Y - 20} 860 {BANK_Y - 6} Q980 {BANK_Y - 10} 1080 {BANK_Y - 30} L1080 1920 Z' fill='#d9b072' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M712 1660 Q740 {BANK_Y - 18} 860 {BANK_Y - 4} Q980 {BANK_Y - 8} 1080 {BANK_Y - 28} L1080 {BANK_Y + 30} Q900 {BANK_Y + 40} 712 1700 Z' fill='#7cc35a' stroke='{INK}' stroke-width='7'/>")
    for gx in (760, 840, 950, 1030):
        sway = 6 * math.sin(t * 3 + gx)
        s.append(f"<path d='M{gx} {BANK_Y + 5} q{-10 + sway:.0f} -50 {-20 + sway:.0f} -70 M{gx + 10} {BANK_Y + 5} q{8 + sway:.0f} -60 {18 + sway:.0f} -80' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
        s.append(f"<path d='M{gx} {BANK_Y + 5} q{-10 + sway:.0f} -50 {-20 + sway:.0f} -70 M{gx + 10} {BANK_Y + 5} q{8 + sway:.0f} -60 {18 + sway:.0f} -80' fill='none' stroke='#5fbf45' stroke-width='3' stroke-linecap='round'/>")
    return "".join(s)


def front_leaves(t):
    s = []
    s.append(leaf(-30, 260, 1.5, 20 + 3 * math.sin(t * 1.3), '#3f9a3a'))
    s.append(leaf(-40, 120, 1.2, 50 + 3 * math.sin(t * 1.1), '#4fae3c'))
    s.append(leaf(1110, 220, 1.5, 160 - 3 * math.sin(t * 1.2), '#3f9a3a'))
    s.append(leaf(1110, 380, 1.1, 190 - 3 * math.sin(t * 1.5), '#4fae3c'))
    return "".join(s)


def splashes(t, reveal):
    """Salpicaduras y anillos de cada pisada mientras corre."""
    s = []
    if t < T_JUMP1 - 0.05:
        return ""
    # salpicón al caer al agua
    k = (t - T_JUMP1) / 0.6
    if 0 <= k <= 1:
        x0 = X_RUN0
        for i in range(10):
            a = math.pi * (0.1 + 0.8 * i / 9)
            r = 150 * k
            x = x0 + r * math.cos(a) * 1.3
            y = WATER_Y - r * math.sin(a) * 1.6 + 300 * k * k
            if y > WATER_Y + 8:
                continue
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{12 * (1 - k) + 3:.1f}' fill='#e9fdff' stroke='{INK}' stroke-width='4'/>")
    # pisadas: una cada medio ciclo de cada pata
    period = 1 / 6.5
    n = int((min(t, T_RUN1) - T_JUMP1) / (period / 2)) + 1
    for i in range(max(0, n - 26), n):
        ts = T_JUMP1 + i * period / 2
        if ts > min(t, T_RUN1):
            continue
        age = t - ts
        xs = lerp(X_RUN0, X_RUN1, (ts - T_JUMP1) / (T_RUN1 - T_JUMP1)) + (25 if i % 2 else -10)
        # anillo que se abre y se desvanece
        if age < 2.0:
            a = 1 - age / 2.0
            s.append(f"<ellipse cx='{xs:.0f}' cy='{WATER_Y + 12}' rx='{30 + 70 * age:.0f}' ry='{8 + 18 * age:.0f}' fill='none' stroke='#e9fdff' stroke-width='{6 * a + 1:.1f}' opacity='{a:.2f}'/>")
        # gotitas
        if age < 0.45:
            for dxr, up, rr in DROPS:
                x = xs + dxr * 90 * age / 0.45
                y = WATER_Y - 260 * up * age + 900 * age * age
                if y > WATER_Y + 8:
                    continue
                s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{rr * (1 + 0.6 * reveal):.1f}' fill='#e9fdff' stroke='{INK}' stroke-width='3'/>")
    return "".join(s)


def air_pockets(t, X, S, ph, reveal):
    """Bolsas de aire bajo los pies (revelación)."""
    if reveal <= 0:
        return ""
    s = []
    for off in (0, math.pi):
        fx, fy = foot_pos(ph + off, 1, True)
        depth = max(0.0, -math.sin(ph + off)) + 0.25
        x = X + fx * S + 20
        s.append(f"<path d='M{x - 60:.0f} {WATER_Y + 2} Q{x:.0f} {WATER_Y + 30 + 130 * depth * reveal:.0f} {x + 60:.0f} {WATER_Y + 2} Z' "
                 f"fill='#ffffff' opacity='{0.9 * reveal:.2f}' stroke='{INK}' stroke-width='5'/>")
    # corona de agua alrededor
    for i in range(8):
        a = math.pi * (0.12 + 0.76 * i / 7)
        h = (110 + 35 * math.sin(t * 30 + i)) * reveal
        x = X + 30 + 170 * math.cos(a)
        s.append(f"<path d='M{x - 12:.0f} {WATER_Y + 4} Q{x:.0f} {WATER_Y - h:.0f} {x + 12:.0f} {WATER_Y + 4} Z' fill='#e9fdff' stroke='{INK}' stroke-width='4'/>")
    return "".join(s)


def frame(t):
    reveal = seg(t, REVELACION, REVELACION + 0.5) * (1 - seg(t, T_RUN1, T_RUN1 + 0.2))
    liz, X, Y, S, running, ph = lizard(t)
    defs = ("<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d9f7b8'/>"
            "<stop offset='0.6' stop-color='#9fe0a8'/><stop offset='1' stop-color='#6cc58c'/></linearGradient>"
            "<linearGradient id='water' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#5fd6cf'/>"
            "<stop offset='1' stop-color='#1f8f9a'/></linearGradient>"
            f"<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.35 * reveal:.2f}'/>"
            "<stop offset='1' stop-color='#ffffff' stop-opacity='0'/></radialGradient>")
    body = [background(t), snake(t)]
    # reflejo del lagarto en el agua al correr
    if t < T_JUMP1:
        body.append(bank(t))
    if t >= T_JUMP1:
        body.append(f"<g opacity='0.25' transform='translate(0,{2 * WATER_Y + 30}) scale(1,-1)'>{liz}</g>"
                    f"<rect x='0' y='{WATER_Y + 15}' width='{W}' height='{H - WATER_Y}' fill='#1f8f9a' opacity='0.35'/>")
    body.append(bank(t))
    body.append(splashes(t, reveal))
    if running:
        body.append(air_pockets(t, X, S, ph, reveal))
    body.append(liz)
    # destello de la revelación
    body.append(f"<circle cx='{X:.0f}' cy='{WATER_Y - 100}' r='{lerp(100, 520, reveal):.0f}' fill='url(#flash)'/>")
    z = 1 + 0.22 * seg(t, REVELACION, 8.4) - 0.08 * seg(t, 9.2, 10)
    cx = lerp(X_RUN0, X_END, seg(t, 6.5, 9.4))
    scene = f"<g transform='translate({cx:.1f},1560) scale({z:.4f}) translate({-cx:.1f},-1560)'>{''.join(body)}</g>"
    motes = "".join(f"<circle cx='{x + 15 * math.sin(t + p):.0f}' cy='{(y + t * 25) % 1100:.0f}' r='{r:.1f}' fill='#fffbd0' opacity='0.6'/>"
                    for x, y, r, p in MOTES)
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{scene}{motes}{front_leaves(t)}</svg>")
