"""2026-11-16-c3 · Ni los gemelos idénticos tienen las mismas huellas dactilares.

Dos gemelos idénticos (mismo pelo, misma ropa, misma cara) llegan saltando a un parque y levantan
una mano para saludar. Entre ellos gira una doble hélice de ADN (el mismo ADN). Una lupa gigante
entra y pasa sobre sus manos; en la REVELACION aparecen dos burbujas enormes con la yema de un dedo
de cada uno: una huella en espiral y otra en lazo, distintas. El cielo se vuelve dorado, destellos
y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.5    # aparecen las dos huellas distintas: golpe musical
MUSICA = 5

rng = np.random.default_rng(1116)
POLEN = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(15, 45)) for _ in range(30)]
FLORES = [(70, 1790, "#ff5d8f"), (190, 1870, "#ffd23f"), (460, 1880, "#ffffff"), (640, 1860, "#ff8a3d"),
          (900, 1800, "#ff5d8f"), (1010, 1880, "#ffd23f"), (560, 1760, "#b07cff")]
CHISPAS = [(rng.uniform(0, 6.283), rng.uniform(0.6, 1.0)) for _ in range(26)]

PIEL = "#f6c39a"
PELO = "#6b3b1f"
CAMISA = "#2fa7e0"
FRANJA = "#ffd23f"
PANT = "#3b4a8c"

# posiciones de los gemelos y de sus manos levantadas
KIDS = [(330, -1), (750, 1)]        # (x, lado hacia el que levanta la mano)
HEAD_Y = 1430
BURBUJAS = [(245, 1120), (835, 1120)]


def nino(x, lado, t, idx):
    """Niño original: cabeza redonda, flequillo, camiseta a rayas. Levanta una mano hacia fuera."""
    # entrada saltando desde el borde (0-1,6 s)
    ent = seg(t, 0, 1.6)
    x0 = x + lado * 300
    xx = lerp(x0, x, ent)
    salto = abs(math.sin(t * 8)) * 60 * (1 - ent)
    resp = 4 * math.sin(t * 3 + idx)
    rev = seg(t, REVELACION, REVELACION + 0.4)
    brinco = abs(math.sin((t - REVELACION) * 9)) * 26 * (1 - seg(t, REVELACION + 0.9, REVELACION + 1.6)) if t > REVELACION else 0
    y = -salto - brinco + resp * 0.3
    g = [f"<g transform='translate({xx:.1f},{y:.1f})'>"]
    # sombra
    g.append(f"<ellipse cx='0' cy='1835' rx='{120 + salto*0.3:.0f}' ry='20' fill='#1d5a1a' opacity='0.3'/>")
    # piernas y zapatos
    for sx in (-1, 1):
        g.append(f"<rect x='{sx*38 - 26}' y='1660' width='52' height='150' rx='18' fill='{PANT}' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M{sx*38 - 34} 1830 Q{sx*38 - 34} 1790 {sx*38} 1790 Q{sx*38 + 44} 1790 {sx*38 + 44} 1830 Z' fill='#e8463c' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # brazo bajado (lado contrario)
    ob = -lado
    swing = 8 * math.sin(t * 3.2 + idx)
    g.append(f"<g transform='translate({ob*88},1560) rotate({-ob*(12 + swing):.1f})'>"
             f"<rect x='-22' y='-10' width='44' height='150' rx='22' fill='{CAMISA}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='0' cy='150' r='28' fill='{PIEL}' stroke='{INK}' stroke-width='7'/></g>")
    # cuerpo (camiseta a rayas)
    g.append(f"<path d='M-100 1700 L-100 1590 Q-100 1530 -40 1525 L40 1525 Q100 1530 100 1590 L100 1700 Z' fill='{CAMISA}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-96' y='1600' width='192' height='26' fill='{FRANJA}'/>")
    g.append(f"<rect x='-96' y='1650' width='192' height='20' fill='{FRANJA}'/>")
    g.append(f"<path d='M-100 1700 L-100 1590 Q-100 1530 -40 1525 L40 1525 Q100 1530 100 1590 L100 1700 Z' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brazo levantado (saluda)
    up = seg(t, 1.2, 2.0)
    ola = 14 * math.sin(t * 7) * (1 - seg(t, 4.8, 5.4)) * up
    ang = -lado * lerp(20, 155, up) + ola
    g.append(f"<g transform='translate({lado*88},1560) rotate({ang:.1f})'>"
             f"<rect x='-22' y='-10' width='44' height='150' rx='22' fill='{CAMISA}' stroke='{INK}' stroke-width='{LW}'/>"
             # mano abierta: palma y dedos
             f"<g transform='translate(0,170)'>"
             + "".join(f"<rect x='{fx-9}' y='12' width='18' height='46' rx='9' fill='{PIEL}' stroke='{INK}' stroke-width='6'/>" for fx in (-21, -7, 7, 21))
             + f"<rect x='-40' y='-14' width='18' height='40' rx='9' fill='{PIEL}' stroke='{INK}' stroke-width='6' transform='rotate(-35 -31 6)'/>"
             f"<rect x='-30' y='-20' width='60' height='52' rx='22' fill='{PIEL}' stroke='{INK}' stroke-width='7'/></g></g>")
    # cuello y cabeza
    hy = HEAD_Y - 1430 + 1430
    tilt = 4 * math.sin(t * 2.1 + idx * 1.3) + (lado * -6 * rev)
    g.append(f"<g transform='translate(0,{hy}) rotate({tilt:.1f})'>")
    g.append(f"<rect x='-20' y='70' width='40' height='40' fill='{PIEL}' stroke='{INK}' stroke-width='7'/>")
    for sx in (-1, 1):
        g.append(f"<circle cx='{sx*92}' cy='5' r='22' fill='{PIEL}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='0' cy='0' r='96' fill='{PIEL}' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo con flequillo
    g.append(f"<path d='M-98 -5 Q-104 -104 0 -106 Q104 -104 98 -5 Q80 -48 46 -52 Q30 -30 0 -40 Q-20 -58 -46 -50 Q-78 -44 -98 -5 Z' fill='{PELO}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # mechón que se balancea
    m = 10 * math.sin(t * 5 + idx)
    g.append(f"<path d='M0 -104 Q{8 + m:.1f} -146 {30 + m:.1f} -136' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
             f"<path d='M0 -104 Q{8 + m:.1f} -146 {30 + m:.1f} -136' fill='none' stroke='{PELO}' stroke-width='7' stroke-linecap='round'/>")
    # ojos (parpadean; en la revelación se abren mucho)
    blink = 0.12 if ((t + idx * 0.07 + 1.0) % 2.9) < 0.12 else 1.0
    er = lerp(21, 27, rev)
    mira = lado * -6 * (1 - rev) + lado * 8 * rev
    for ex in (-36, 36):
        g.append(f"<g transform='translate({ex},10) scale(1,{blink})'>"
                 f"<ellipse rx='{er:.1f}' ry='{er*1.15:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{mira:.1f}' cy='-{4*rev:.1f}' r='{lerp(12, 14, rev):.1f}' fill='{INK}'/>"
                 f"<circle cx='{mira - 4:.1f}' cy='-{5 + 4*rev:.1f}' r='5' fill='#fff'/></g>")
    # mofletes y boca
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{sx*60}' cy='48' rx='16' ry='10' fill='#ff8a8a' opacity='0.7'/>")
    if rev > 0.5:
        g.append(f"<ellipse cx='0' cy='58' rx='18' ry='22' fill='#7a2a1e' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='0' cy='68' rx='10' ry='7' fill='#ff7a7a'/>")
    else:
        g.append(f"<path d='M-26 50 Q0 78 26 50' fill='#7a2a1e' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append("</g></g>")
    return "".join(g)


def adn(t):
    """Doble hélice girando entre los dos gemelos (2-5,6 s)."""
    a = seg(t, 2.2, 2.8) * (1 - seg(t, 5.0, 5.6))
    if a <= 0.01:
        return ""
    cx, y0, y1 = 540, 1150, 1450
    g = [f"<g opacity='{a:.2f}' transform='translate(0,{-10*math.sin(t*2):.1f})'>"]
    n = 9
    pts1, pts2 = [], []
    for i in range(n + 1):
        y = lerp(y0, y1, i / n)
        ph = i * 0.75 + t * 3.2
        x1 = cx + 62 * math.sin(ph); x2 = cx - 62 * math.sin(ph)
        pts1.append((x1, y)); pts2.append((x2, y))
        col = ["#ff5d8f", "#ffd23f", "#7ce06a", "#b07cff"][i % 4]
        g.append(f"<line x1='{x1:.1f}' y1='{y:.1f}' x2='{x2:.1f}' y2='{y:.1f}' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
                 f"<line x1='{x1:.1f}' y1='{y:.1f}' x2='{x2:.1f}' y2='{y:.1f}' stroke='{col}' stroke-width='7' stroke-linecap='round'/>")
    for pts, col in ((pts1, "#ff7a45"), (pts2, "#2fa7e0")):
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='{d}' fill='none' stroke='{col}' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def lupa(t):
    """Lupa gigante que entra y pasa sobre las manos (5-7,5 s)."""
    if t < 4.9 or t > REVELACION + 0.4:
        return ""
    k = seg(t, 4.9, 7.2)
    x = lerp(1250, 300, k) + 40 * math.sin(t * 4)
    y = 1180 + 25 * math.sin(t * 5)
    a = 1 - seg(t, REVELACION, REVELACION + 0.3)
    return (f"<g opacity='{a:.2f}' transform='translate({x:.1f},{y:.1f}) rotate(-25)'>"
            f"<rect x='-26' y='120' width='52' height='190' rx='20' fill='#a0522d' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle r='130' fill='#d8f3ff' fill-opacity='0.45' stroke='{INK}' stroke-width='{LW + 4}'/>"
            f"<circle r='120' fill='none' stroke='#ffb52e' stroke-width='14'/>"
            f"<path d='M-70 -50 Q-50 -85 -10 -92' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.85'/></g>")


def espiral(cx, cy, vueltas=6.5, paso=11.5):
    pts = []
    th = 0.0
    while th < vueltas * 2 * math.pi:
        r = 8 + paso * th / (2 * math.pi)
        pts.append((cx + r * math.cos(th), cy + r * 1.18 * math.sin(th)))
        th += 0.18
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def huella(cx, cy, tipo, t, k):
    """Yema del dedo dentro de una burbuja con su huella: 'espiral' o 'lazo'."""
    if k <= 0:
        return ""
    s = rebote(t, REVELACION, 0.55)
    gira = 3 * math.sin(t * 2.5 + cx)
    g = [f"<g transform='translate({cx},{cy}) scale({s:.3f}) rotate({gira:.1f})'>"]
    g.append(f"<circle r='190' fill='url(#brillo)'/>")
    g.append(f"<circle r='150' fill='#fff7e0' stroke='{INK}' stroke-width='{LW + 2}'/>")
    cid = f"yema{tipo}"
    g.append(f"<clipPath id='{cid}'><ellipse cx='0' cy='6' rx='96' ry='122'/></clipPath>")
    g.append(f"<ellipse cx='0' cy='6' rx='96' ry='122' fill='{PIEL}' stroke='{INK}' stroke-width='7'/>")
    rid = "#b5683e"
    g.append(f"<g clip-path='url(#{cid})' fill='none' stroke='{rid}' stroke-width='7' stroke-linecap='round'>")
    if tipo == "espiral":
        g.append(f"<path d='{espiral(0, 4)}'/>")
    else:
        # lazo: curvas en U que entran por la izquierda y vuelven a salir
        for i in range(9):
            w = 10 + i * 13
            top = -40 - i * 13
            g.append(f"<path d='M{-w-20} 160 Q{-w-20} {top+40} {-w+10} {top+12} Q{10} {top-8} {w-6} {top+30} Q{w+12} {top+60} {w-10} 160'/>")
        for i in range(3):
            r = 150 + i * 14
            g.append(f"<path d='M-120 {-40 + i*-10} Q0 {-140 - i*16} 120 {-40 + i*-10}'/>")
    g.append("</g>")
    g.append(f"<ellipse cx='0' cy='6' rx='96' ry='122' fill='none' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M-110 -75 Q-80 -125 -30 -138' fill='none' stroke='#fff' stroke-width='12' stroke-linecap='round' opacity='0.9'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.6)
    top = mix("#5ab8f2", "#ff9f5a", rev)
    mid = mix("#9fdcff", "#ffd27a", rev)
    low = mix("#e3f6ff", "#fff1c4", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='brillo'><stop offset='0.6' stop-color='#fff6a8' stop-opacity='0.9'/>"
            "<stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='sol'><stop offset='0' stop-color='#fff9d6' stop-opacity='0.9'/>"
            "<stop offset='1' stop-color='#ffe27a' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.12 * seg(t, REVELACION, DUR)
    zx, zy = 540, 1300
    s.append(f"<g transform='translate({zx},{zy}) scale({z:.4f}) translate({-zx},{-zy})'>")
    # sol suave arriba a la derecha
    s.append(f"<circle cx='900' cy='330' r='{230 + 8*math.sin(t*2):.0f}' fill='url(#sol)'/>")
    s.append(f"<circle cx='900' cy='330' r='80' fill='#fff2a8' stroke='#ffc93a' stroke-width='8'/>")
    # nubes que pasan despacio
    for i, (cx, cy, sc) in enumerate([(120, 560, 1.3), (700, 760, 1.0), (380, 900, 0.8)]):
        dx = ((cx + t * 18 * (1 + i * 0.4)) % 1500) - 250
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})'>"
                 f"<path d='M0 60 Q-10 10 45 15 Q60 -30 115 -10 Q160 -40 200 5 Q250 5 245 60 Z' fill='#ffffff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # colinas y árboles
    s.append(f"<path d='M0 1320 Q240 1240 520 1300 T1080 1280 L1080 1920 L0 1920 Z' fill='{mix('#8fd16a', '#a8d65a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for tx, ts in ((110, 1.0), (980, 0.85)):
        sw = 3 * math.sin(t * 1.8 + tx)
        s.append(f"<g transform='translate({tx},1300) scale({ts}) rotate({sw:.1f})'>"
                 f"<rect x='-16' y='-20' width='32' height='110' rx='8' fill='#8a5a33' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='0' cy='-70' r='80' fill='#3fa34d' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='-30' cy='-95' r='22' fill='#5cc266'/></g>")
    s.append(f"<path d='M0 1480 Q300 1420 600 1470 T1080 1450 L1080 1920 L0 1920 Z' fill='{mix('#5cbf4a', '#77c94a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    # flores que se balancean
    for fx, fy, fc in FLORES:
        sw = 6 * math.sin(t * 2.4 + fx)
        s.append(f"<g transform='translate({fx},{fy}) rotate({sw:.1f})'>"
                 f"<line x1='0' y1='0' x2='0' y2='45' stroke='#2f7a2a' stroke-width='7'/>"
                 + "".join(f"<circle cx='{14*math.cos(a):.1f}' cy='{14*math.sin(a):.1f}' r='11' fill='{fc}' stroke='{INK}' stroke-width='4'/>" for a in np.linspace(0, 6.28, 6)[:-1])
                 + f"<circle r='8' fill='#ffb52e' stroke='{INK}' stroke-width='4'/></g>")
    # destellos de la revelación detrás de las burbujas
    if t > REVELACION:
        k = seg(t, REVELACION, REVELACION + 0.8)
        for bx, by in BURBUJAS:
            for ang, ln in CHISPAS[:13] if bx < 540 else CHISPAS[13:]:
                a2 = ang + t * 0.4
                r1 = 170 + 30 * k; r2 = r1 + 90 * ln * k
                s.append(f"<line x1='{bx + r1*math.cos(a2):.1f}' y1='{by + r1*math.sin(a2):.1f}' x2='{bx + r2*math.cos(a2):.1f}' y2='{by + r2*math.sin(a2):.1f}' "
                         f"stroke='#fff3a0' stroke-width='10' stroke-linecap='round' opacity='{0.9*(1-0.4*seg(t, 8.5, 10)):.2f}'/>")
    s.append(adn(t))
    for i, (kx, lado) in enumerate(KIDS):
        s.append(nino(kx, lado, t, i))
    # mariposa
    bx = 100 + (t * 90) % 1000; by = 1240 + 50 * math.sin(t * 2.2)
    ala = abs(math.sin(t * 16))
    s.append(f"<g transform='translate({bx:.0f},{by:.0f})'>"
             f"<ellipse cx='-16' cy='0' rx='{20*ala + 4:.1f}' ry='18' fill='#ff7ac2' stroke='{INK}' stroke-width='5'/>"
             f"<ellipse cx='16' cy='0' rx='{20*ala + 4:.1f}' ry='18' fill='#ff7ac2' stroke='{INK}' stroke-width='5'/>"
             f"<rect x='-4' y='-16' width='8' height='32' rx='4' fill='{INK}'/></g>")
    s.append(lupa(t))
    if t >= REVELACION:
        s.append(huella(BURBUJAS[0][0], BURBUJAS[0][1], "espiral", t, 1))
        s.append(huella(BURBUJAS[1][0], BURBUJAS[1][1], "lazo", t, 1))
    # polen flotando
    for px, py, pr, sp in POLEN:
        yy = (py - t * sp) % 950 + 980
        s.append(f"<circle cx='{px + 18*math.sin(t*1.3 + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fffbe0' opacity='0.7'/>")
    s.append("</g></svg>")
    return "".join(s)
