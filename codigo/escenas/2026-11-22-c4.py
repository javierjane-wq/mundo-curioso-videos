"""2026-11-22-c4 · Púrpura de Tiro: el morado de los emperadores romanos salía de un caracol marino; su jugo
no es morado, pero con el aire y el sol se vuelve púrpura.

Escena: playa del Mediterráneo antiguo con un templo de columnas a lo lejos. Un caracol marino original
(cañadilla/múrex, concha con pinchos y canal largo) entra reptando sobre una tela blanca tendida en la
arena y deja una mancha de jugo amarillo pálido. Una nube tapa el Sol; la nube se aparta, los rayos
caen sobre la tela y la mancha pasa a verde. REVELACION: la mancha estalla en MORADO intenso y se
extiende por toda la tela, destellos, rayos dorados y zoom de cámara hacia la tela.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.3    # la tela se vuelve morada: golpe musical
MUSICA = 6

rng = np.random.default_rng(1122)
SPARK = [(rng.uniform(80, 1000), rng.uniform(1250, 1850), rng.uniform(8, 18), rng.uniform(0, 6.28)) for _ in range(26)]
PEBBLES = [(60, 1840, 26), (980, 1880, 34), (1010, 1420, 22), (300, 1890, 18), (880, 1830, 16), (40, 1440, 18)]
GULLS = [(140, 690, 1.0, 0.0), (330, 610, 0.7, 1.3), (900, 560, 0.8, 2.1)]

SUN_X, SUN_Y = 790, 720
# tela tendida en la arena (en perspectiva)
CLOTH = "M120 1440 Q300 1418 470 1436 Q640 1452 830 1432 L905 1770 Q690 1792 480 1772 Q270 1752 60 1778 Z"
BLOT_X, BLOT_Y = 660, 1590
STOP_X = 330            # donde se para el caracol (centro de la concha)
PURPLE = "#7b2391"
PURPLE_D = "#57166a"


def sol(t):
    """0 = nublado, 1 = el Sol ya brilla sobre la tela."""
    return seg(t, 5.0, 6.6)


def morado(t):
    """0 = mancha pálida, 1 = morado total (revelación, termina antes de 8,2 s)."""
    return seg(t, REVELACION, REVELACION + 0.6)


def snail_x(t):
    return lerp(1010, STOP_X, seg(t, 0, 4.2))


def snail(t):
    """Caracol marino original (tipo cañadilla): pie rosado, concha crema con pinchos y canal largo, ojos en antenas."""
    x = snail_x(t)
    y = 1640
    moving = t < 4.3
    crawl = math.sin(t * 9) if moving else 0
    m = morado(t)
    joy = seg(t, REVELACION + 0.1, REVELACION + 0.5)
    hop = -26 * abs(math.sin((t - REVELACION) * 6)) * joy if t > REVELACION else 0
    blink = 0.12 if ((t + 0.7) % 2.9) < 0.12 else 1.0
    g = [f"<g transform='translate({x:.1f},{y + hop:.1f})'>"]
    g.append("<ellipse cx='10' cy='12' rx='230' ry='22' fill='#000' opacity='0.18'/>")
    # pie (se estira y encoge al reptar)
    st = 8 * crawl
    g.append(f"<path d='M-185 6 Q-200 -40 -150 -48 L120 -48 Q{175 + st:.0f} -40 {178 + st:.0f} 6 "
             f"Q{120:.0f} 16 0 12 Q-100 16 -185 6 Z' fill='#f4b3a0' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(5):
        wx = -140 + i * 60 + 10 * crawl
        g.append(f"<path d='M{wx:.0f} 0 q12 -10 24 0' fill='none' stroke='#d98a78' stroke-width='5' stroke-linecap='round'/>")
    # concha: canal largo hacia delante
    g.append(f"<path d='M-60 -92 Q-170 -70 -258 -40' fill='none' stroke='{INK}' stroke-width='42' stroke-linecap='round'/>"
             f"<path d='M-60 -92 Q-170 -70 -258 -40' fill='none' stroke='#efd6a8' stroke-width='26' stroke-linecap='round'/>")
    for k in (0.45, 0.75):
        cx, cy = lerp(-60, -258, k), lerp(-92, -40, k) - 10 * math.sin(math.pi * k)
        g.append(f"<path d='M{cx - 10:.0f} {cy - 10:.0f} L{cx - 4:.0f} {cy - 46:.0f} L{cx + 10:.0f} {cy - 12:.0f} Z' fill='#e2bf86' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # aguja (espira) hacia atrás y arriba
    g.append(f"<path d='M40 -170 L150 -250 L120 -150 Z' fill='#e9cd98' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M70 -186 L124 -170 M95 -205 L134 -198 M118 -224 L142 -224' stroke='#b9864e' stroke-width='6' stroke-linecap='round'/>")
    # pinchos de la vuelta grande
    for a in range(190, 355, 24):
        r = math.radians(a)
        bx, by = 10 + 118 * math.cos(r), -110 + 88 * math.sin(r)
        tx, ty = 10 + 178 * math.cos(r), -110 + 140 * math.sin(r)
        nx, ny = -math.sin(r) * 16, math.cos(r) * 16
        g.append(f"<path d='M{bx - nx:.0f} {by - ny:.0f} L{tx:.0f} {ty:.0f} L{bx + nx:.0f} {by + ny:.0f} Z' fill='#e2bf86' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # vuelta grande de la concha
    g.append(f"<ellipse cx='10' cy='-110' rx='125' ry='92' fill='#f2dcae' stroke='{INK}' stroke-width='{LW}'/>")
    for k, c in ((0.55, '#c9935a'), (0.8, '#d9a96c')):
        g.append(f"<path d='M{10 - 118 * k:.0f} {-110 + 30 * (1 - k):.0f} Q10 {-110 - 92 * k:.0f} {10 + 118 * k:.0f} {-110 + 30 * (1 - k):.0f}' fill='none' stroke='{c}' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M-70 -60 Q-30 -20 60 -32' fill='none' stroke='#c9935a' stroke-width='9' stroke-linecap='round'/>")
    # abertura rosada
    g.append(f"<ellipse cx='-62' cy='-62' rx='46' ry='28' fill='#ff9d84' stroke='{INK}' stroke-width='7' transform='rotate(-14 -62 -62)'/>")
    # cabeza y antenas con ojos
    hx, hy = -170, -40
    g.append(f"<circle cx='{hx}' cy='{hy}' r='36' fill='#f4b3a0' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (ex, ey) in enumerate(((-232, -150), (-176, -168))):
        sw = 7 * math.sin(t * 3.4 + i * 1.7) + 10 * joy * math.sin(t * 8 + i)
        ex2 = ex + sw
        g.append(f"<path d='M{hx + 10 * i - 6} {hy - 20} Q{(hx + ex2) / 2 - 10:.0f} {(hy + ey) / 2:.0f} {ex2:.0f} {ey:.0f}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
                 f"<path d='M{hx + 10 * i - 6} {hy - 20} Q{(hx + ex2) / 2 - 10:.0f} {(hy + ey) / 2:.0f} {ex2:.0f} {ey:.0f}' fill='none' stroke='#f4b3a0' stroke-width='10' stroke-linecap='round'/>")
        er = 26 + 6 * joy
        g.append(f"<g transform='translate({ex2:.1f},{ey}) scale(1,{blink})'>"
                 f"<circle r='{er:.0f}' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='-5' cy='3' r='{13 + 2 * joy:.0f}' fill='{INK}'/><circle cx='-9' cy='-4' r='5' fill='#fff'/></g>")
    # boca: sonrisa (más grande al final) y mofletes
    if joy > 0.5:
        g.append(f"<path d='M{hx - 22} {hy + 2} Q{hx - 4} {hy + 30} {hx + 16} {hy + 4} Z' fill='#7a2a2a' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M{hx - 20} {hy + 6} Q{hx - 4} {hy + 22} {hx + 14} {hy + 6}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='{hx + 20}' cy='{hy - 2}' rx='9' ry='6' fill='#ff7f8f' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g)


def cloud(x, y, s, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s})'>"
            f"<path d='M-150 50 Q-170 -10 -100 -15 Q-90 -80 -10 -70 Q40 -120 100 -60 Q170 -60 160 10 Q200 40 150 60 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def temple(x, y, col):
    """Templo de columnas lejano sobre un cabo."""
    g = [f"<g transform='translate({x},{y})'>"]
    g.append(f"<path d='M-60 140 Q-40 30 40 20 L260 18 Q330 40 360 140 Z' fill='{mix('#b98a5a', '#c99c6a', 1)}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='30' y='0' width='210' height='18' fill='{col}' stroke='{INK}' stroke-width='5'/>")
    for cx in range(48, 240, 36):
        g.append(f"<rect x='{cx}' y='-78' width='16' height='80' fill='{col}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='30' y='-96' width='210' height='20' fill='{col}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M24 -96 L135 -146 L246 -96 Z' fill='{col}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    s_on = sol(t)
    m = morado(t)
    glow = seg(t, REVELACION, REVELACION + 0.3) * (1 - 0.6 * seg(t, REVELACION + 0.4, 9.5))
    top = mix(mix("#7c9bbf", "#4fa8ec", s_on), "#ff9f6b", 0.35 * m)
    mid = mix(mix("#b4c6d8", "#9fd6f7", s_on), "#ffc98a", 0.45 * m)
    low = mix(mix("#dfe6ea", "#fff1c9", s_on), "#ffe3a8", 0.5 * m)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='sunglow'><stop offset='0' stop-color='#fff8d0' stop-opacity='{0.25 + 0.6 * s_on:.2f}'/>"
            f"<stop offset='1' stop-color='#ffd36b' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='flash'><stop offset='0' stop-color='#ffe7ff' stop-opacity='{0.85 * glow:.2f}'/>"
            f"<stop offset='0.5' stop-color='#d78cff' stop-opacity='{0.45 * glow:.2f}'/><stop offset='1' stop-color='#a040d0' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='cl'><path d='{CLOTH}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # Sol con halo
    s.append(f"<circle cx='{SUN_X}' cy='{SUN_Y}' r='{300 + 80 * m:.0f}' fill='url(#sunglow)'/>")
    s.append(f"<circle cx='{SUN_X}' cy='{SUN_Y}' r='86' fill='#ffe066' stroke='#f0a020' stroke-width='9'/>")
    # nubes lejanas que pasan
    for i, (cx, cy, sc) in enumerate(((150, 430, 0.9), (620, 300, 0.7), (1000, 520, 0.6))):
        dx = (t * (12 + 5 * i)) % 1400 - 150
        s.append(cloud((cx + dx) % 1400 - 150, cy, sc, mix("#e4e9ef", "#ffffff", s_on)))
    # nube grande que tapa el Sol y se aparta
    s.append(cloud(lerp(SUN_X + 10 + 14 * math.sin(t * 0.8), 1400, seg(t, 4.9, 6.6)), SUN_Y + 5, 1.55, mix("#cfd6de", "#ffffff", s_on)))
    # gaviotas lejanas
    for gx, gy, gs, ph in GULLS:
        xx = (gx + t * 40 * gs) % 1200 - 60
        fl = 14 * math.sin(t * 6 + ph)
        s.append(f"<path d='M{xx - 30 * gs:.0f} {gy + fl * gs:.0f} Q{xx - 15 * gs:.0f} {gy - 16 * gs:.0f} {xx:.0f} {gy:.0f} "
                 f"Q{xx + 15 * gs:.0f} {gy - 16 * gs:.0f} {xx + 30 * gs:.0f} {gy + fl * gs:.0f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # rayos de sol hacia la tela (aparecen al irse la nube, más fuertes en la revelación)
    ra = 0.18 * s_on + 0.3 * glow
    if ra > 0.01:
        for i in range(7):
            a = math.radians(-35 + i * 14 + 3 * math.sin(t * 1.5 + i))
            s.append(f"<path d='M{SUN_X} {SUN_Y} L{SUN_X - 1400 * math.sin(a + 0.04):.0f} {SUN_Y + 1400 * math.cos(a + 0.04):.0f} "
                     f"L{SUN_X - 1400 * math.sin(a - 0.04):.0f} {SUN_Y + 1400 * math.cos(a - 0.04):.0f} Z' fill='#fff6c0' opacity='{ra:.2f}'/>")
    # mar
    sea = mix("#4a86b0", "#1f9fd6", s_on)
    s.append(f"<rect x='0' y='1080' width='{W}' height='300' fill='{sea}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(temple(40, 960, mix("#e9e1d2", "#fff7e8", s_on)))
    for i in range(4):
        yy = 1130 + i * 45
        off = (t * (30 + 12 * i)) % 160
        d = "M-160 %d " % yy + " ".join(f"q40 -14 80 0 q40 14 80 0" for _ in range(9))
        s.append(f"<path d='{d}' transform='translate({off:.0f},0)' fill='none' stroke='#bfe9ff' stroke-width='6' opacity='0.8' stroke-linecap='round'/>")
    # destellos del sol en el agua
    for i in range(6):
        a = 0.5 + 0.5 * math.sin(t * 4 + i * 1.3)
        s.append(f"<path d='M{560 + i * 70 - 18} {1100 + (i % 3) * 40} h36' stroke='#ffffff' stroke-width='6' opacity='{a * s_on:.2f}' stroke-linecap='round'/>")
    # orilla con espuma que va y viene
    fo = 14 * math.sin(t * 2.2)
    s.append(f"<path d='M0 {1330 + fo:.0f} Q270 {1300 + fo:.0f} 540 {1325 + fo:.0f} T1080 {1315 + fo:.0f} L1080 1920 L0 1920 Z' fill='#ffffff' stroke='{INK}' stroke-width='7'/>")
    sand = mix("#e3c48c", "#f6d58f", s_on)
    s.append(f"<path d='M0 {1355 + fo * 0.6:.0f} Q270 {1330 + fo * 0.6:.0f} 540 {1350 + fo * 0.6:.0f} T1080 {1342 + fo * 0.6:.0f} L1080 1920 L0 1920 Z' fill='{sand}' stroke='{INK}' stroke-width='{LW}'/>")
    for px, py, pr in PEBBLES:
        s.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr}' ry='{pr * 0.62:.0f}' fill='#c9a46e' stroke='{INK}' stroke-width='6'/>")
    # pequeña concha de vieira en la arena
    s.append(f"<path d='M980 1720 l-38 -52 q38 -26 76 0 z' fill='#ffb6a3' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")

    # ---- tela con la mancha ----
    c = []
    wave = 6 * math.sin(t * 2.5)
    c.append(f"<g transform='translate(0,{wave:.1f})'>")
    c.append(f"<path d='{CLOTH}' fill='{mix('#fbf8f0', PURPLE, m)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    c.append("<g clip-path='url(#cl)'>")
    # pliegues de la tela
    for i in range(4):
        fx = 220 + i * 170 + 10 * math.sin(t * 2 + i)
        c.append(f"<path d='M{fx:.0f} 1440 Q{fx + 30:.0f} 1600 {fx - 10:.0f} 1780' fill='none' stroke='{mix('#e4ddcc', PURPLE_D, m)}' stroke-width='12' stroke-linecap='round'/>")
    # rastro y mancha del jugo: amarillo pálido -> verde (sol) -> morado (revelación)
    green = seg(t, 5.6, REVELACION)
    jc = mix(mix("#e8d86a", "#93c25a", green), PURPLE_D, m)
    sx = snail_x(t)
    tr0 = min(sx + 150, 930)
    if tr0 < 930:
        c.append(f"<path d='M{tr0:.0f} 1636 Q{(tr0 + 930) / 2:.0f} 1626 930 1640' fill='none' stroke='{jc}' stroke-width='34' stroke-linecap='round' opacity='0.9'/>")
    blot = 135 * seg(t, 2.4, 4.6)
    if blot > 1:
        c.append(f"<path d='M{BLOT_X - blot:.0f} {BLOT_Y + 40} Q{BLOT_X - blot * 1.1:.0f} {BLOT_Y - blot * 0.6 + 40:.0f} {BLOT_X - blot * 0.2:.0f} {BLOT_Y - blot * 0.7 + 40:.0f} "
                 f"Q{BLOT_X + blot * 0.6:.0f} {BLOT_Y - blot * 0.9 + 40:.0f} {BLOT_X + blot * 1.05:.0f} {BLOT_Y - blot * 0.2 + 40:.0f} "
                 f"Q{BLOT_X + blot * 1.2:.0f} {BLOT_Y + blot * 0.5 + 40:.0f} {BLOT_X + blot * 0.2:.0f} {BLOT_Y + blot * 0.55 + 40:.0f} "
                 f"Q{BLOT_X - blot * 0.9:.0f} {BLOT_Y + blot * 0.6 + 40:.0f} {BLOT_X - blot:.0f} {BLOT_Y + 40} Z' fill='{jc}' opacity='0.92'/>")
    # la mancha morada se extiende por toda la tela
    if m > 0:
        c.append(f"<circle cx='{BLOT_X}' cy='{BLOT_Y + 40}' r='{lerp(110, 620, m):.0f}' fill='{PURPLE}'/>")
        for i in range(4):
            fx = 220 + i * 170 + 10 * math.sin(t * 2 + i)
            c.append(f"<path d='M{fx:.0f} 1440 Q{fx + 30:.0f} 1600 {fx - 10:.0f} 1780' fill='none' stroke='{PURPLE_D}' stroke-width='12' stroke-linecap='round' opacity='{m:.2f}'/>")
        # brillo de seda
        c.append(f"<path d='M140 1470 Q480 1440 820 1462' fill='none' stroke='#c77de0' stroke-width='14' opacity='{0.7 * m:.2f}' stroke-linecap='round'/>")
    c.append("</g>")
    c.append(f"<path d='{CLOTH}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    c.append("</g>")
    s.append("".join(c))
    # destello morado en la revelación
    if glow > 0.01:
        s.append(f"<circle cx='{BLOT_X}' cy='{BLOT_Y}' r='{lerp(200, 700, seg(t, REVELACION, REVELACION + 0.6)):.0f}' fill='url(#flash)'/>")
    s.append(snail(t))
    # chispitas sobre la tela morada
    sp = seg(t, REVELACION + 0.15, REVELACION + 0.6)
    if sp > 0:
        for px, py, pr, ph in SPARK:
            a = sp * (0.5 + 0.5 * math.sin(t * 6 + ph))
            r = pr * (0.7 + 0.3 * math.sin(t * 5 + ph))
            s.append(f"<path d='M{px:.0f} {py - r:.0f} L{px + r * 0.25:.0f} {py:.0f} L{px:.0f} {py + r:.0f} L{px - r * 0.25:.0f} {py:.0f} Z "
                     f"M{px - r:.0f} {py:.0f} L{px:.0f} {py + r * 0.25:.0f} L{px + r:.0f} {py:.0f} L{px:.0f} {py - r * 0.25:.0f} Z' fill='#fff3a8' opacity='{a:.2f}'/>")
    z = 1 + 0.12 * seg(t, REVELACION, 9.8)
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>" \
           + zoom(380, 1620, z, "".join(s)) + "</svg>"
