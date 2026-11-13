"""Versión por código de 2026-11-13-px: en el espacio los astronautas crecen hasta un 3 % (unos 5 cm).

Astronauta original (mono azul con un parche redondo sin letras, sin casco) entra flotando en un
módulo de una estación espacial y se pone junto a una regla de colores con una línea roja a la altura
de su cabeza. Su torso se vuelve transparente (rayos X): columna de vértebras blancas con discos
rosas. Sin gravedad los discos se hinchan, la espalda se estira y en la REVELACION su cabeza sobrepasa
la línea roja (nueva línea amarilla con flecha), con destellos y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.5    # la cabeza sobrepasa la línea roja
MUSICA = 4

rng = np.random.default_rng(13)
STARS = [(rng.uniform(380, 1020), rng.uniform(280, 900), rng.uniform(2, 5), rng.uniform(0, 6.28)) for _ in range(45)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(150, 330), rng.uniform(12, 22)) for _ in range(14)]

FEET = 1840          # pies del astronauta (flotando un poco sobre el suelo)
LEGS, TORSO, HEADR = 330, 270, 72
EXTRA = 95           # estiramiento exagerado para que se vea (en la realidad ~5 cm)
X0 = 560             # x final del astronauta
STRIP_X = 120
LINE_Y = FEET - (LEGS + TORSO + 40 + 2 * HEADR)   # altura inicial de la cabeza


def stretch(t):
    return 0.18 * seg(t, 5.6, 7.2) + 0.82 * seg(t, 7.2, 7.8)


def fondo(t):
    s = []
    s.append(f"<rect width='{W}' height='{H}' fill='#cfe3ef'/>")
    # paneles de la pared
    for y in (180, 560, 940, 1320):
        s.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='#a9c6d8' stroke-width='6'/>")
    for x, y in ((60, 240), (1000, 240), (60, 620), (1000, 620), (1000, 1000), (1000, 1380)):
        s.append(f"<circle cx='{x}' cy='{y}' r='9' fill='#a9c6d8'/>")
    # ventana redonda con la Tierra
    cx, cy, r = 700, 590, 300
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 38}' fill='#e9f2f8' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<clipPath id='win'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#0d1430'/>")
    s.append("<g clip-path='url(#win)'>")
    for sx, sy, sr, ph in STARS:
        a = 0.5 + 0.5 * math.sin(t * 3 + ph)
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    ex = cx + 120 - t * 6
    s.append(f"<circle cx='{ex:.0f}' cy='{cy + 560}' r='420' fill='#2f8fe0' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, gy, gr in ((-120, -380, 70), (60, -400, 50), (180, -340, 60)):
        s.append(f"<ellipse cx='{ex + gx:.0f}' cy='{cy + 560 + gy}' rx='{gr}' ry='{gr * 0.55:.0f}' fill='#4cc27a'/>")
    s.append(f"<circle cx='{ex:.0f}' cy='{cy + 560}' r='440' fill='none' stroke='#9fd8ff' stroke-width='16' opacity='0.6'/>")
    s.append("</g>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 38}' fill='none' stroke='#8fb2c8' stroke-width='10'/>")
    # suelo/rejilla de la estación
    s.append(f"<rect x='-10' y='1870' width='{W + 20}' height='80' fill='#9fb7c7' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(40, W, 120):
        s.append(f"<rect x='{x}' y='1888' width='70' height='16' rx='6' fill='#6fe0ff' opacity='{0.6 + 0.4 * math.sin(t * 4 + x):.2f}'/>")
    # barandilla
    s.append(f"<rect x='300' y='1500' width='60' height='300' rx='14' fill='#f1c232' stroke='{INK}' stroke-width='7' opacity='0'/>")
    return "".join(s)


def flotantes(t):
    """Objetos flotando sin gravedad: taza rosa, lápiz y gota de agua."""
    s = []
    x, y, a = 300 + 30 * math.sin(t * 0.7), 1180 + 25 * math.sin(t * 0.9), 20 * math.sin(t * 0.8)
    s.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({a:.1f})'>"
             f"<path d='M-34 -36 L34 -36 L28 34 Q0 44 -28 34 Z' fill='#ff8fb1' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M34 -20 Q62 -16 58 6 Q54 22 30 18' fill='none' stroke='{INK}' stroke-width='7'/></g>")
    x, y, a = 930 + 20 * math.sin(t * 0.6 + 1), 1250 + 30 * math.sin(t * 0.75 + 2), 40 + 30 * t
    s.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({a:.1f})'>"
             f"<rect x='-60' y='-11' width='100' height='22' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M40 -11 L68 0 L40 11 Z' fill='#f5d6a8' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<rect x='-74' y='-11' width='16' height='22' fill='#ff7a8a' stroke='{INK}' stroke-width='6'/></g>")
    x, y = 860 + 25 * math.sin(t * 1.1), 1560 + 20 * math.cos(t * 0.9)
    s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{22 + 3 * math.sin(t * 5):.1f}' fill='#7fd4ff' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='{x - 7:.0f}' cy='{y - 8:.0f}' r='6' fill='#fff'/>")
    return "".join(s)


def regla(t, s_):
    """Regla de colores en la pared con la línea roja (altura inicial) y la nueva línea amarilla."""
    g = []
    g.append(f"<rect x='{STRIP_X - 50}' y='880' width='130' height='{FEET - 880 + 20}' rx='14' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>")
    for i, c in enumerate(("#ff5a5f", "#ffb347", "#ffd23f", "#4cc27a", "#3d8fe0", "#8f6bff")):
        g.append(f"<rect x='{STRIP_X - 38 + i * 18}' y='895' width='12' height='{FEET - 895}' fill='{c}'/>")
    for y in range(920, FEET, 40):
        w = 34 if (y // 40) % 5 == 0 else 18
        g.append(f"<line x1='{STRIP_X + 80 - w}' y1='{y}' x2='{STRIP_X + 80}' y2='{y}' stroke='{INK}' stroke-width='5'/>")
    # línea roja: altura de la cabeza al principio
    lr = seg(t, 2.6, 3.2)
    if lr > 0:
        x2 = lerp(STRIP_X - 50, X0 + 110, lr)
        g.append(f"<line x1='{STRIP_X - 60}' y1='{LINE_Y}' x2='{x2:.0f}' y2='{LINE_Y}' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
                 f"<line x1='{STRIP_X - 60}' y1='{LINE_Y}' x2='{x2:.0f}' y2='{LINE_Y}' stroke='#ff3b3b' stroke-width='9' stroke-linecap='round'/>")
    # nueva línea amarilla y flecha de diferencia
    ny = LINE_Y - EXTRA
    ly = seg(t, 7.7, 8.3)
    if ly > 0:
        x2 = lerp(STRIP_X - 50, X0 + 110, ly)
        g.append(f"<line x1='{STRIP_X - 60}' y1='{ny}' x2='{x2:.0f}' y2='{ny}' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
                 f"<line x1='{STRIP_X - 60}' y1='{ny}' x2='{x2:.0f}' y2='{ny}' stroke='#ffe14a' stroke-width='11' stroke-linecap='round'/>")
    ar = seg(t, 8.2, 8.7)
    if ar > 0:
        ax = STRIP_X + 150
        top, bot = LINE_Y - 8 - (EXTRA - 16) * ar, LINE_Y - 8
        g.append(f"<g transform='translate({ax},0)'><line x1='0' y1='{bot}' x2='0' y2='{top:.0f}' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
                 f"<line x1='0' y1='{bot}' x2='0' y2='{top:.0f}' stroke='#ffe14a' stroke-width='7' stroke-linecap='round'/>"
                 f"<path d='M-20 {top + 24:.0f} L0 {top:.0f} L20 {top + 24:.0f}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/></g>")
    return "".join(g)


def astronauta(t):
    s_ = stretch(t)
    L = EXTRA * s_
    x = lerp(1300, X0, seg(t, 0, 2.3))
    bob = 6 * math.sin(t * 2.2) * (1 - seg(t, 2.3, 2.8)) + (0 if t > 2.8 else 0)
    tilt = lerp(-14, 0, seg(t, 0, 2.4))
    xr = seg(t, 4.8, 5.6)                       # torso transparente (rayos X)
    hip = -LEGS
    sh = hip - TORSO - L                         # hombros
    head_c = sh - 40 - HEADR
    blink = 0.12 if (t % 2.9) < 0.12 else 1.0
    happy = seg(t, 7.6, 8.1)
    g = [f"<g transform='translate({x:.1f},{FEET + bob:.1f}) rotate({tilt:.1f})'>"]
    # piernas (pantalón que se queda corto al estirarse: se ven calcetines)
    sock = 26 * seg(t, 8.0, 8.6)
    for lx in (-50, 50):
        g.append(f"<rect x='{lx - 42}' y='{hip - 10}' width='84' height='{LEGS - 40 - sock:.0f}' rx='26' fill='#2f6fd6' stroke='{INK}' stroke-width='{LW}'/>")
        if sock > 1:
            g.append(f"<rect x='{lx - 30}' y='{-50 - sock:.0f}' width='60' height='{sock + 14:.0f}' fill='#ffffff' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<path d='M{lx - 46} -54 L{lx + 40} -54 Q{lx + 70} -40 {lx + 64} -8 L{lx - 46} -8 Z' fill='#3b3f46' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brazo izquierdo (lado del espectador derecho), suelto
    sw = 6 * math.sin(t * 2)
    g.append(f"<g transform='translate(118,{sh + 30:.0f}) rotate({-12 + sw - 30 * happy:.1f})'>"
             f"<rect x='-28' y='-10' width='56' height='230' rx='26' fill='#2f6fd6' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='0' cy='238' r='30' fill='#f5c9a0' stroke='{INK}' stroke-width='7'/></g>")
    # brazo derecho: señala hacia la línea roja (2,5-6 s), luego se abre de alegría
    up = seg(t, 2.4, 3.0) * (1 - seg(t, 7.4, 7.9))
    ang = lerp(12, 150, up) + lerp(0, -40, happy)
    g.append(f"<g transform='translate(-118,{sh + 30:.0f}) rotate({ang:.1f})'>"
             f"<rect x='-28' y='-10' width='56' height='230' rx='26' fill='#2f6fd6' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='0' cy='238' r='30' fill='#f5c9a0' stroke='{INK}' stroke-width='7'/></g>")
    # torso
    g.append(f"<rect x='-125' y='{sh:.0f}' width='250' height='{TORSO + L + 10:.0f}' rx='50' fill='#2f6fd6' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-125' y='{hip - 30}' width='250' height='34' fill='#24509c' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-26' y='{hip - 30}' width='52' height='34' rx='6' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>")
    # cremallera y parche (se ocultan en rayos X)
    if xr < 1:
        g.append(f"<g opacity='{1 - xr:.2f}'><line x1='0' y1='{sh + 20:.0f}' x2='0' y2='{hip - 34}' stroke='#24509c' stroke-width='6'/>"
                 f"<circle cx='-62' cy='{sh + 70:.0f}' r='26' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M-62 {sh + 52:.0f} L-56 {sh + 66:.0f} L-44 {sh + 70:.0f} L-56 {sh + 76:.0f} L-62 {sh + 90:.0f} L-68 {sh + 76:.0f} L-80 {sh + 70:.0f} L-68 {sh + 66:.0f} Z' fill='#ff7a45'/></g>")
    # rayos X: ventana oscura con la columna
    if xr > 0:
        top, bot = sh + 22, hip - 36
        g.append(f"<rect x='-88' y='{top:.0f}' width='176' height='{bot - top:.0f}' rx='34' fill='#16325e' stroke='#7fd4ff' stroke-width='6' opacity='{xr:.2f}'/>")
        n = 7
        h = (bot - top - 20) / n
        disc = lerp(10, 26, s_) + (2 * math.sin(t * 12) if 5.5 < t < 7.6 else 0)
        glow = seg(t, 5.6, 6.2) * (1 - 0.5 * seg(t, 8.5, 9.5))
        for i in range(n):
            yc = top + 10 + h * (i + 0.5)
            vh = max(8, h - disc)
            g.append(f"<g opacity='{xr:.2f}'><rect x='-38' y='{yc - vh / 2:.1f}' width='76' height='{vh:.1f}' rx='12' fill='#fbf6ea' stroke='{INK}' stroke-width='5'/>"
                     f"<rect x='-62' y='{yc - 6:.1f}' width='124' height='12' rx='6' fill='#e8e0cc' stroke='{INK}' stroke-width='4'/></g>")
            if i < n - 1:
                yd = yc + h / 2
                g.append(f"<ellipse cx='0' cy='{yd:.1f}' rx='{44 + 6 * glow:.1f}' ry='{disc / 2:.1f}' fill='{mix('#ffb3c7', '#ff6f9a', glow)}' stroke='{INK}' stroke-width='4' opacity='{xr:.2f}'/>")
    # cuello y cabeza
    g.append(f"<rect x='-30' y='{sh - 46:.0f}' width='60' height='56' fill='#f5c9a0' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M-70 {sh + 4:.0f} Q0 {sh - 30:.0f} 70 {sh + 4:.0f}' fill='#24509c' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<g transform='translate(0,{head_c:.0f})'>")
    g.append(f"<circle cx='-70' cy='8' r='16' fill='#f5c9a0' stroke='{INK}' stroke-width='6'/><circle cx='70' cy='8' r='16' fill='#f5c9a0' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle r='{HEADR}' fill='#f5c9a0' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-70 -10 Q-78 -78 -10 -80 Q60 -88 72 -14 Q50 -46 20 -40 Q-10 -60 -40 -36 Q-56 -30 -70 -10 Z' fill='#6b3d22' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    eye_r = lerp(13, 18, happy)
    look = lerp(-6, 0, seg(t, 7.3, 7.6)) if t > 2.6 else 0
    lift = -8 * up * (1 - happy)
    for exx in (-28, 28):
        g.append(f"<g transform='translate({exx + look:.1f},{-2 + lift:.1f}) scale(1,{blink})'><ellipse rx='{eye_r:.1f}' ry='{eye_r * 1.2:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='0' cy='2' r='{eye_r * 0.6:.1f}' fill='{INK}'/><circle cx='-3' cy='-3' r='3.5' fill='#fff'/></g>")
    g.append(f"<circle cx='-46' cy='26' r='10' fill='#ff9aa2' opacity='0.7'/><circle cx='46' cy='26' r='10' fill='#ff9aa2' opacity='0.7'/>")
    if happy > 0.5:
        g.append(f"<path d='M-22 30 Q0 66 22 30 Z' fill='#9b2a3a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M-20 32 Q0 46 20 32' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g></g>")
    return "".join(g), x, FEET + bob + head_c - HEADR


def frame(t):
    cuerpo, ax, ytop = astronauta(t)
    s = [fondo(t), regla(t, stretch(t)), flotantes(t), cuerpo]
    # destellos en la revelación
    k = seg(t, REVELACION, REVELACION + 1.0)
    if k > 0:
        for ang, rad, sz in SPARK:
            rr = rad * (0.4 + 0.6 * k)
            px, py = ax + rr * math.cos(ang), ytop + 40 + rr * math.sin(ang) * 0.8
            if py > 960:
                sc = sz * (1 - 0.5 * k) * (0.8 + 0.2 * math.sin(t * 10 + ang))
                s.append(f"<path d='M{px:.0f} {py - sc:.0f} L{px + sc * 0.3:.0f} {py - sc * 0.3:.0f} L{px + sc:.0f} {py:.0f} L{px + sc * 0.3:.0f} {py + sc * 0.3:.0f} "
                         f"L{px:.0f} {py + sc:.0f} L{px - sc * 0.3:.0f} {py + sc * 0.3:.0f} L{px - sc:.0f} {py:.0f} L{px - sc * 0.3:.0f} {py - sc * 0.3:.0f} Z' fill='#ffe14a' stroke='{INK}' stroke-width='4'/>")
        # destello de luz
        s.append(f"<circle cx='{ax:.0f}' cy='{ytop + 60:.0f}' r='{lerp(60, 380, k):.0f}' fill='#fff7c2' opacity='{0.45 * (1 - k):.2f}'/>")
    z = 1 + 0.1 * seg(t, REVELACION, 9.6)
    contenido = "".join(s)
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            + zoom(380, 1300, z, contenido) + "</svg>")
