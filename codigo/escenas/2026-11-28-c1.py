"""Efecto Leidenfrost: en una sartén muy caliente la gota de agua no hierve al momento,
flota sobre un cojín de su propio vapor y se desliza por la sartén.

Protagonista: una gota de agua original con ojos, en una sartén sobre el fuego (mitad de abajo).
Arriba solo la pared de azulejos de la cocina.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.0   # la gota se levanta sobre el vapor
MUSICA = 2

rng = np.random.default_rng(28)
PCX, PCY = 500, 1335          # centro de la boca de la sartén
RX, RY = 345, 92              # boca de la sartén
SHIM = [(rng.uniform(220, 780), rng.uniform(0, 1), rng.uniform(0.6, 1.2)) for _ in range(9)]
STEAM = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(0.7, 1.3)) for _ in range(14)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(0, 1), rng.uniform(60, 150)) for _ in range(16)]


def pared(t, hot, rev):
    s = []
    base = mix("#f6ecd6", "#ffe4c2", 0.5 * hot + 0.3 * rev)
    s.append(f"<rect width='{W}' height='{H}' fill='{base}'/>")
    # azulejos grandes
    tile = mix("#bfe3dc", "#f8c9a0", 0.35 * hot + 0.25 * rev)
    for row in range(0, 12):
        for col in range(0, 7):
            x = col * 160 - (80 if row % 2 else 0) + 6
            y = row * 120 + 6
            s.append(f"<rect x='{x}' y='{y}' width='148' height='108' rx='14' fill='{tile}' opacity='0.55'/>")
    # luz cálida del fuego que sube por la pared
    s.append(f"<ellipse cx='{PCX}' cy='1420' rx='{lerp(380, 620, rev):.0f}' ry='{lerp(300, 520, rev):.0f}' fill='url(#calor)'/>")
    return "".join(s)


def utensilios(t):
    """Barra con un cucharón y una espumadera que se balancean (fondo, a los lados)."""
    s = [f"<rect x='40' y='1000' width='300' height='16' rx='8' fill='#a7b0ba' stroke='{INK}' stroke-width='6'/>",
         f"<rect x='800' y='1000' width='240' height='16' rx='8' fill='#a7b0ba' stroke='{INK}' stroke-width='6'/>"]
    for i, (x, kind) in enumerate([(110, 0), (250, 1), (900, 1), (1000, 0)]):
        a = 6 * math.sin(t * 2.1 + i * 1.3)
        s.append(f"<g transform='translate({x},1008) rotate({a:.1f})'>")
        s.append(f"<path d='M-8 0 Q0 -22 8 0' fill='none' stroke='{INK}' stroke-width='6'/>")
        s.append(f"<rect x='-9' y='0' width='18' height='120' rx='8' fill='{'#e07a3f' if kind == 0 else '#4f9d8a'}' stroke='{INK}' stroke-width='6'/>")
        if kind == 0:
            s.append(f"<path d='M-36 120 Q-36 175 0 175 Q36 175 36 120 Z' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>")
        else:
            s.append(f"<ellipse cx='0' cy='150' rx='30' ry='34' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>")
            for dx, dy in ((-10, 140), (10, 140), (0, 158), (-12, 160), (12, 160)):
                s.append(f"<circle cx='{dx}' cy='{dy}' r='4' fill='{INK}'/>")
        s.append("</g>")
    return "".join(s)


def cocina(t, hot):
    s = []
    # encimera y placa
    s.append(f"<path d='M0 1470 L1080 1470 L1080 1580 L0 1580 Z' fill='#e9e2d0' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M120 1480 L900 1480 L940 1560 L80 1560 Z' fill='#30343b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # frente del horno
    s.append(f"<rect x='-20' y='1580' width='1120' height='360' fill='#d9d1bd' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='60' y='1600' width='960' height='70' rx='14' fill='#c4bba5' stroke='{INK}' stroke-width='6'/>")
    for i, kx in enumerate((170, 330, 750, 910)):
        rot = 25 * hot if i == 1 else 0
        s.append(f"<g transform='translate({kx},1635) rotate({rot:.1f})'><circle r='26' fill='#f4efe2' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='-4' y='-24' width='8' height='22' rx='3' fill='{INK}'/></g>")
    s.append(f"<rect x='140' y='1700' width='800' height='200' rx='22' fill='#3b3530' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='180' y='1730' width='720' height='140' rx='14' fill='{mix('#4a3f37', '#7a4a2e', hot)}' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<rect x='300' y='1688' width='480' height='22' rx='11' fill='#b8bec6' stroke='{INK}' stroke-width='6'/>")
    # quemador
    s.append(f"<ellipse cx='{PCX}' cy='1500' rx='170' ry='26' fill='#1d2025' stroke='{INK}' stroke-width='6'/>")
    # rejilla de la placa
    for gx in (PCX - 230, PCX - 90, PCX + 90, PCX + 230):
        s.append(f"<path d='M{gx - 14} 1505 L{gx - 6} 1452 L{gx + 6} 1452 L{gx + 14} 1505 Z' fill='#4a4f57' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # llamas azules que crecen con el calor
    fl = lerp(0.35, 1.0, hot)
    for i in range(13):
        fx = PCX - 180 + i * 30
        hgt = (26 + 10 * math.sin(t * 17 + i * 1.7)) * fl
        s.append(f"<path d='M{fx - 11} 1500 Q{fx - 6} {1500 - hgt:.0f} {fx + 2 * math.sin(t * 9 + i):.0f} {1500 - hgt * 1.7:.0f} "
                 f"Q{fx + 7} {1500 - hgt:.0f} {fx + 11} 1500 Z' fill='#3d8cff' stroke='#1d4fa8' stroke-width='3'/>")
        s.append(f"<path d='M{fx - 5} 1500 Q{fx} {1500 - hgt * 1.0:.0f} {fx + 5} 1500 Z' fill='#bfe6ff'/>")
    return "".join(s)


def sarten(t, hot, rev):
    s = []
    # mango
    s.append(f"<g transform='translate({PCX + RX - 20},{PCY - 4}) rotate(-8)'>"
             f"<rect x='0' y='-16' width='110' height='32' rx='10' fill='#9aa3ad' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='90' y='-24' width='190' height='48' rx='22' fill='#2b2d33' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='250' cy='0' r='9' fill='#f6ecd6' stroke='{INK}' stroke-width='5'/></g>")
    # cuerpo exterior
    body = mix("#3a3d44", "#55362b", hot)
    s.append(f"<path d='M{PCX - RX} {PCY} L{PCX - RX + 40} {PCY + 62} Q{PCX} {PCY + 118} {PCX + RX - 40} {PCY + 62} L{PCX + RX} {PCY} Z' "
             f"fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # borde
    s.append(f"<ellipse cx='{PCX}' cy='{PCY}' rx='{RX}' ry='{RY}' fill='#6b7079' stroke='{INK}' stroke-width='{LW}'/>")
    # fondo interior que se pone al rojo
    inner = mix(mix("#2f3238", "#7a3324", hot), "#c4532c", rev * 0.6)
    s.append(f"<ellipse cx='{PCX}' cy='{PCY + 6}' rx='{RX - 28}' ry='{RY - 20}' fill='{inner}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<ellipse cx='{PCX}' cy='{PCY + 8}' rx='{RX - 70}' ry='{RY - 40}' fill='url(#brasa)'/>")
    # brillo metálico del borde
    s.append(f"<path d='M{PCX - RX + 30} {PCY - 30} Q{PCX - 150} {PCY - RY + 4} {PCX + 40} {PCY - RY + 2}' fill='none' stroke='#c9ced6' stroke-width='8' stroke-linecap='round' opacity='0.8'/>")
    return "".join(s)


def gota(t, hot, rev):
    """Gota de agua con cara. Cae (0-1 s), se posa, tiembla con el calor y en la revelación flota."""
    fall = seg(t, 0, 0.95)
    landed = t >= 0.95
    # deslizamiento tras la revelación (de lado a lado de la sartén)
    slide = 120 * math.sin((t - REVELACION) * 3.2) * seg(t, REVELACION, REVELACION + 0.5) if t > REVELACION else 0
    lift = 62 * seg(t, REVELACION, REVELACION + 0.45) + (5 * math.sin(t * 9) if t > REVELACION + 0.45 else 0)
    shake = 5 * math.sin(t * 55) * seg(t, 4.6, 5.4) * (1 - seg(t, REVELACION, REVELACION + 0.3))
    x = PCX + shake + slide
    ybot = PCY + 14 - lift
    s = []
    if not landed:
        y = lerp(1000, ybot - 100, fall * fall)
        st = 1 + 0.25 * fall
        s.append(f"<g transform='translate({x:.1f},{y:.1f}) scale({1/st:.3f},{st:.3f})'>"
                 f"<path d='M0 -120 C30 -70 80 -20 80 25 C80 75 42 100 0 100 C-42 100 -80 75 -80 25 C-80 -20 -30 -70 0 -120 Z' "
                 f"fill='url(#agua)' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<ellipse cx='-34' cy='-4' rx='14' ry='26' fill='#fff' opacity='0.8' transform='rotate(20 -34 -4)'/>"
                 + ojos(t, 0, 20, "sorpresa") + "</g>")
        return "".join(s)
    # aterrizaje: aplastado con rebote
    k = clamp((t - 0.95) / 0.6)
    squash = 1 + 0.35 * math.exp(-k * 5) * math.cos(k * 14)
    breathe = 1 + 0.03 * math.sin(t * 4)
    w = 138 * squash * lerp(1, 0.92, rev)
    h = 132 / squash * breathe * lerp(1, 1.12, rev)
    # sombra / cojín de vapor
    if rev > 0:
        s.append(f"<ellipse cx='{x:.1f}' cy='{PCY + 16:.1f}' rx='{w * 1.6:.0f}' ry='{40 + 14 * rev:.0f}' fill='url(#cojin)'/>")
        s.append(f"<ellipse cx='{x:.1f}' cy='{PCY + 12 - lift * 0.45:.1f}' rx='{w * 0.95:.0f}' ry='{lift * 0.42 + 4:.1f}' "
                 f"fill='#eafaff' stroke='#9ee3ff' stroke-width='5' opacity='{0.9 * rev:.2f}'/>")
        # chispas de vapor que salen a los lados
        for ang, ph, sp in SPARK:
            u = ((t - REVELACION) * 1.5 + ph) % 1
            dx = math.cos(ang) * (w + u * sp)
            dy = -abs(math.sin(ang)) * u * sp * 0.5
            s.append(f"<circle cx='{x + dx:.0f}' cy='{PCY + 10 + dy:.0f}' r='{lerp(9, 2, u):.1f}' fill='#ffffff' opacity='{rev * (1 - u):.2f}'/>")
    else:
        s.append(f"<ellipse cx='{x:.1f}' cy='{PCY + 18:.1f}' rx='{w * 1.05:.0f}' ry='18' fill='#000' opacity='0.25'/>")
    # cuerpo de la gota (cúpula)
    s.append(f"<g transform='translate({x:.1f},{ybot:.1f})'>")
    s.append(f"<path d='M{-w:.1f} 0 C{-w:.1f} {-h * 0.8:.1f} {-w * 0.55:.1f} {-h * 1.15:.1f} 0 {-h * 1.15:.1f} "
             f"C{w * 0.55:.1f} {-h * 1.15:.1f} {w:.1f} {-h * 0.8:.1f} {w:.1f} 0 Q0 {16 + 14 * rev:.1f} {-w:.1f} 0 Z' "
             f"fill='url(#agua)' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<ellipse cx='{-w * 0.5:.1f}' cy='{-h * 0.72:.1f}' rx='16' ry='30' fill='#fff' opacity='0.85' transform='rotate(35 {-w * 0.5:.1f} {-h * 0.72:.1f})'/>")
    s.append(f"<circle cx='{-w * 0.22:.1f}' cy='{-h * 0.98:.1f}' r='8' fill='#fff' opacity='0.85'/>")
    animo = "feliz" if rev > 0.3 else ("susto" if t > 4.6 else "normal")
    s.append(ojos(t, 0, -h * 0.5, animo))
    # gotitas de sudor por el calor
    if 3.4 < t < REVELACION + 0.2:
        u = (t * 1.3) % 1
        s.append(f"<path d='M{w * 0.75:.0f} {-h * 0.85 + u * 40:.0f} q10 18 0 26 q-10 -8 0 -26 Z' fill='#cfefff' stroke='{INK}' stroke-width='4' opacity='{1 - u:.2f}'/>")
    s.append("</g>")
    return "".join(s)


def ojos(t, cx, cy, animo):
    blink = 0.12 if ((t + 1.3) % 2.7) < 0.12 else 1.0
    s = []
    r = 24 if animo != "susto" else 27
    for ex in (-40, 40):
        s.append(f"<ellipse cx='{cx + ex}' cy='{cy:.1f}' rx='{r}' ry='{r * 1.15 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            look = 4 * math.sin(t * 1.3)
            pr = 12 if animo != "susto" else 9
            s.append(f"<circle cx='{cx + ex + look:.1f}' cy='{cy + 3:.1f}' r='{pr}' fill='{INK}'/>"
                     f"<circle cx='{cx + ex + look - 4:.1f}' cy='{cy - 2:.1f}' r='4' fill='#fff'/>")
    # boca
    my = cy + 40
    if animo == "feliz":
        s.append(f"<path d='M{cx - 26} {my:.1f} Q{cx} {my + 34:.1f} {cx + 26} {my:.1f} Z' fill='#e2525c' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    elif animo in ("susto", "sorpresa"):
        s.append(f"<ellipse cx='{cx}' cy='{my + 6:.1f}' rx='13' ry='17' fill='#8a2f3a' stroke='{INK}' stroke-width='6'/>")
    else:
        s.append(f"<path d='M{cx - 20} {my:.1f} Q{cx} {my + 18:.1f} {cx + 20} {my:.1f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # mofletes
    s.append(f"<circle cx='{cx - 64}' cy='{cy + 30:.1f}' r='11' fill='#ff9db0' opacity='0.6'/><circle cx='{cx + 64}' cy='{cy + 30:.1f}' r='11' fill='#ff9db0' opacity='0.6'/>")
    return "".join(s)


def ondas_calor(t, hot, rev):
    s = []
    a = hot * (1 - 0.4 * rev)
    if a < 0.05:
        return ""
    for x, ph, sp in SHIM:
        u = (t * 0.6 * sp + ph) % 1
        y0 = PCY - 10 - u * 260
        op = a * 0.6 * math.sin(math.pi * u)
        s.append(f"<path d='M{x:.0f} {y0:.0f} q14 -22 0 -44 q-14 -22 0 -44' fill='none' stroke='#ffb36b' stroke-width='7' stroke-linecap='round' opacity='{op:.2f}'/>")
    return "".join(s)


def vapor(t, rev):
    s = []
    a = seg(t, 4.8, 5.6)
    if a <= 0:
        return ""
    for dx, ph, sp in STEAM:
        u = (t * 0.55 * sp + ph) % 1
        x = PCX + dx * 260 + 30 * math.sin(t * 2 + ph * 6)
        y = PCY - 20 - u * 330
        r = lerp(18, 54, u) * (1 + 0.4 * rev)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='#ffffff' opacity='{a * 0.5 * (1 - u):.2f}'/>")
    return "".join(s)


def frame(t):
    hot = seg(t, 2.3, 4.8)                 # la sartén se calienta
    rev = seg(t, REVELACION, REVELACION + 0.7)
    defs = (f"<radialGradient id='agua' cx='0.4' cy='0.35' r='0.75'><stop offset='0' stop-color='#d8f4ff'/>"
            f"<stop offset='0.55' stop-color='#6fcaf6'/><stop offset='1' stop-color='#3a98da'/></radialGradient>"
            f"<radialGradient id='calor'><stop offset='0' stop-color='#ff9a3c' stop-opacity='{0.25 * hot + 0.35 * rev:.3f}'/>"
            f"<stop offset='1' stop-color='#ff9a3c' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='brasa'><stop offset='0' stop-color='#ffb347' stop-opacity='{0.55 * hot + 0.3 * rev:.3f}'/>"
            f"<stop offset='1' stop-color='#ff6a2a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='cojin'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.95 * rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#8fe3ff' stop-opacity='{0.6 * rev:.3f}'/><stop offset='1' stop-color='#3dc0ff' stop-opacity='0'/></radialGradient>")
    z = 1 + 0.28 * seg(t, REVELACION, REVELACION + 1.0)
    cuerpo = (pared(t, hot, rev) + utensilios(t) + cocina(t, hot) + sarten(t, hot, rev)
              + ondas_calor(t, hot, rev) + vapor(t, rev) + gota(t, hot, rev))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{zoom(PCX, 1300, z, cuerpo)}</svg>")
