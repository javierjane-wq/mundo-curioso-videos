"""2026-11-15-c5 · Récords: el huevo de avestruz es el más grande de un ave viva; su volumen
equivale al de unos 24 huevos de gallina (dos docenas) (Guinness World Records).

Un huevito de gallina entra rodando en la sabana y se queda tan contento en su nido. Al fondo
pasea un avestruz. Tiembla el suelo, una sombra enorme llega por la derecha… y entra rodando un
huevo de avestruz gigante. En la REVELACION el huevo grande brilla, la cámara se acerca y a su
alrededor aparecen, uno a uno, 24 huevitos de gallina en corro.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, svg, zoom, rebote

DUR = 10.0
REVELACION = 7.45   # el huevo de avestruz brilla y salen los 24 huevitos: golpe musical
MUSICA = 4

rng = np.random.default_rng(55)
GRASS = [(rng.uniform(0, W), rng.uniform(1300, 1900), rng.uniform(0.7, 1.35), rng.uniform(0, 6.28)) for _ in range(40)]
PORES = [(rng.uniform(-0.8, 0.8), rng.uniform(-0.85, 0.85), rng.uniform(2.5, 4.5)) for _ in range(60)]
DUST = [(rng.uniform(0, W), rng.uniform(1150, 1900), rng.uniform(3, 7), rng.uniform(15, 45)) for _ in range(30)]
CLOUDS = [(150, 380, 1.2, 9), (720, 250, 1.0, 13), (980, 640, 0.9, 7), (420, 760, 0.75, 11)]

HEN = (60, 78)       # semiejes del huevo de gallina
BIG = (173, 225)     # huevo de avestruz (~2,9 veces más largo: 24 veces el volumen)
CX, CY = 640, 1556   # centro del huevo de avestruz ya colocado


def egg_path(rx, ry):
    """Contorno de huevo (más estrecho arriba), centrado en 0,0."""
    pts = []
    for i in range(73):
        a = 2 * math.pi * i / 72
        x = math.sin(a); y = -math.cos(a)
        k = 1 - 0.13 * (-y)           # arriba (y<0) más estrecho
        pts.append((rx * x * k, ry * y))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def face(t, rx, ry, surprise, happy, look, blink_off=0.0, s=1.0):
    blink = 0.12 if ((t + blink_off) % 2.8) < 0.13 else 1.0
    g = []
    ex = rx * 0.36; ey = -ry * 0.05; er = rx * 0.26 * (1 + 0.25 * surprise)
    for sx in (-1, 1):
        x = sx * ex
        if happy > 0.5:
            g.append(f"<path d='M{x - er:.1f} {ey + 4:.1f} Q{x:.1f} {ey - er * 1.3:.1f} {x + er:.1f} {ey + 4:.1f}' fill='none' stroke='{INK}' stroke-width='{8*s:.1f}' stroke-linecap='round'/>")
        else:
            g.append(f"<g transform='translate({x:.1f},{ey:.1f}) scale(1,{blink})'>"
                     f"<ellipse rx='{er:.1f}' ry='{er * 1.15:.1f}' fill='#fff' stroke='{INK}' stroke-width='{6*s:.1f}'/>"
                     f"<circle cx='{look * er * 0.35:.1f}' cy='{er * 0.1 - surprise * er * 0.2:.1f}' r='{er * 0.55:.1f}' fill='{INK}'/>"
                     f"<circle cx='{look * er * 0.35 - er * 0.2:.1f}' cy='{-er * 0.2 - surprise * er * 0.2:.1f}' r='{er * 0.2:.1f}' fill='#fff'/></g>")
    # mejillas
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{sx * rx * 0.62:.1f}' cy='{ry * 0.22:.1f}' rx='{rx * 0.15:.1f}' ry='{rx * 0.09:.1f}' fill='#ff8f8f' opacity='0.7'/>")
    # boca
    my = ry * 0.28
    if surprise > 0.5:
        g.append(f"<ellipse cx='0' cy='{my + 4:.1f}' rx='{rx * 0.11:.1f}' ry='{rx * 0.15:.1f}' fill='#7a2a2a' stroke='{INK}' stroke-width='{5*s:.1f}'/>")
    else:
        w = rx * (0.18 + 0.1 * happy)
        g.append(f"<path d='M{-w:.1f} {my:.1f} Q0 {my + w * 0.9:.1f} {w:.1f} {my:.1f}' fill='{'#7a2a2a' if happy > 0.5 else 'none'}' stroke='{INK}' stroke-width='{6*s:.1f}' stroke-linecap='round' stroke-linejoin='round'/>")
    return "".join(g)


def hen_egg(t, x, y, rot, surprise, happy, look, sq=1.0):
    rx, ry = HEN
    g = [f"<ellipse cx='{x:.1f}' cy='{y + ry + 6:.1f}' rx='{rx * 1.2:.1f}' ry='12' fill='#000' opacity='0.2'/>",
         f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({1/sq:.3f},{sq:.3f})'>",
         f"<path d='{egg_path(rx, ry)}' fill='#e8b07a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M{-rx*0.55:.1f} {-ry*0.45:.1f} Q{-rx*0.35:.1f} {-ry*0.75:.1f} {-rx*0.05:.1f} {-ry*0.8:.1f}' fill='none' stroke='#fff3df' stroke-width='9' stroke-linecap='round' opacity='0.8'/>",
         f"<g transform='rotate({-rot:.1f})'>{face(t, rx, ry, surprise, happy, look, 0.6, 0.8)}</g>",
         "</g>"]
    return "".join(g)


def big_egg(t, x, y, rot, glow, look, happy):
    rx, ry = BIG
    g = [f"<ellipse cx='{x:.1f}' cy='{y + ry + 8:.1f}' rx='{rx * 1.15:.1f}' ry='22' fill='#000' opacity='0.22'/>",
         f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>",
         f"<path d='{egg_path(rx, ry)}' fill='{mix('#f3e6c4', '#fff6dc', glow)}' stroke='{INK}' stroke-width='{LW + 2}' stroke-linejoin='round'/>"]
    # poros del cascarón de avestruz
    for px, py, pr in PORES:
        if px * px + py * py < 0.62:
            g.append(f"<circle cx='{px * rx:.1f}' cy='{py * ry:.1f}' r='{pr:.1f}' fill='#d8c49a' opacity='0.75'/>")
    g.append(f"<path d='M{-rx*0.6:.1f} {-ry*0.38:.1f} Q{-rx*0.42:.1f} {-ry*0.72:.1f} {-rx*0.05:.1f} {-ry*0.82:.1f}' fill='none' stroke='#ffffff' stroke-width='16' stroke-linecap='round' opacity='0.85'/>")
    g.append(f"<g transform='rotate({-rot:.1f})'>{face(t, rx, ry, 0, happy, look, 1.3, 1.4)}</g>")
    g.append("</g>")
    return "".join(g)


def ostrich(t, x, y):
    """Avestruz pequeño al fondo (adulto: cuerpo negro, alas con puntas blancas, cuello y patas rosadas)."""
    st = t * 3.2
    l1 = 22 * math.sin(st); l2 = -l1
    g = [f"<g transform='translate({x:.1f},{y:.1f})'>"]
    for ang in (l1, l2):
        g.append(f"<g transform='translate(0,-70) rotate({ang:.1f})'>"
                 f"<path d='M0 0 L8 38 L-2 70 L14 72' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='M0 0 L8 38 L-2 70 L14 72' fill='none' stroke='#e7a7a0' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/></g>")
    bob = 3 * math.sin(st * 2)
    g.append(f"<g transform='translate(0,{bob:.1f})'>")
    g.append(f"<path d='M-55 -82 Q-60 -122 -10 -128 Q40 -130 50 -96 Q40 -66 -10 -64 Q-48 -64 -55 -82 Z' fill='#2b2422' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-58 -92 Q-80 -100 -78 -80 Q-66 -78 -56 -82 Z' fill='#fff' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<path d='M-20 -96 Q10 -88 30 -100' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<path d='M38 -108 Q52 -150 46 -196' fill='none' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>"
             f"<path d='M38 -108 Q52 -150 46 -196' fill='none' stroke='#e7a7a0' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='52' cy='-202' rx='15' ry='11' fill='#e7a7a0' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M64 -206 L82 -200 L64 -196 Z' fill='#f0c060' stroke='{INK}' stroke-width='3'/>")
    g.append(f"<circle cx='56' cy='-205' r='3.5' fill='{INK}'/>")
    g.append("</g></g>")
    return "".join(g)


def acacia(x, y, s, sway):
    return (f"<g transform='translate({x},{y}) scale({s})'>"
            f"<path d='M-8 0 L-6 -90 L-40 -140 M-6 -90 L30 -150 M-6 -60 L-6 -90' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
            f"<path d='M-8 0 L-6 -90 L-40 -140 M-6 -90 L30 -150' fill='none' stroke='#7a5236' stroke-width='9' stroke-linecap='round'/>"
            f"<g transform='rotate({sway:.2f},0,-150)'><path d='M-150 -140 Q-120 -195 -40 -185 Q0 -215 60 -190 Q140 -195 160 -145 Q100 -128 0 -132 Q-90 -128 -150 -140 Z' fill='#5f8a33' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/></g></g>")


def cloud(x, y, s, col):
    return (f"<g transform='translate({x:.0f},{y}) scale({s})'><path d='M0 60 Q-10 10 50 15 Q70 -30 130 -5 Q170 -35 210 10 Q270 10 260 60 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='0.95'/></g>")


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)
    tension = seg(t, 5.0, 7.3)
    # temblor del suelo mientras llega el huevo gigante
    shake = (6 * math.sin(t * 47) * tension * (1 - seg(t, 7.2, 7.5)))
    # cielo de la sabana: de mañana dorada a atardecer más cálido en la revelación
    top = mix("#7cc6ee", "#ffb36b", rev * 0.55); low = mix("#ffe3a3", "#ffd27a", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff7c8' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffd23f' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ffb020' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sun'><stop offset='0' stop-color='#fffbe0'/><stop offset='0.6' stop-color='#fff0a8' stop-opacity='0.7'/><stop offset='1' stop-color='#ffe08a' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol y nubes (arriba, fondo tranquilo)
    s.append(f"<circle cx='860' cy='{1060 - 20 * seg(t, 0, 10):.0f}' r='220' fill='url(#sun)'/>")
    s.append(f"<circle cx='860' cy='{1060 - 20 * seg(t, 0, 10):.0f}' r='85' fill='#fff2b0' stroke='#ffc94a' stroke-width='8'/>")
    for i, (cx, cy, sc, sp) in enumerate(CLOUDS):
        x = (cx + t * sp) % 1400 - 200
        s.append(cloud(x, cy, sc, mix("#ffffff", "#ffe6c8", rev)))
    cam = 1 + 0.12 * seg(t, REVELACION, 10)
    scene = []
    # colinas lejanas y horizonte
    scene.append(f"<path d='M0 1150 Q180 1090 380 1130 T780 1110 T1080 1130 L1080 1920 L0 1920 Z' fill='{mix('#d9a85a', '#e3a24e', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(acacia(170, 1150, 1.0, 1.5 * math.sin(t * 1.3)))
    scene.append(acacia(1000, 1140, 0.7, 1.5 * math.sin(t * 1.1 + 1)))
    # avestruz paseando al fondo
    ox = lerp(1180, 520, seg(t, 0, 10))
    scene.append(f"<g transform='translate({ox:.1f},1168) scale(-1,1) translate({-ox:.1f},-1168)'>{ostrich(t, ox, 1168)}</g>")
    # pradera
    scene.append(f"<path d='M0 1230 Q300 1180 620 1220 T1080 1210 L1080 1920 L0 1920 Z' fill='{mix('#e8c06a', '#f0bc5c', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(f"<path d='M0 1420 Q320 1360 640 1400 T1080 1390 L1080 1920 L0 1920 Z' fill='{mix('#c9a24f', '#d79f45', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, gy, gs, ph in GRASS:
        if gy < 1380: continue
        sw = 6 * math.sin(t * 2.2 + ph)
        scene.append(f"<g transform='translate({gx:.0f},{gy:.0f}) scale({gs:.2f})'><path d='M-14 0 Q-16 -30 {-22 + sw:.1f} -48 M0 0 Q2 -40 {4 + sw:.1f} -62 M14 0 Q18 -28 {26 + sw:.1f} -44' "
                     f"fill='none' stroke='#6f8a2c' stroke-width='7' stroke-linecap='round'/></g>")
    # nido de arena
    scene.append(f"<ellipse cx='{CX}' cy='1790' rx='330' ry='62' fill='#b98c45' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(f"<ellipse cx='{CX}' cy='1782' rx='270' ry='38' fill='#a37838'/>")
    # halo de la revelación + rayos
    if rev > 0:
        scene.append(f"<circle cx='{CX}' cy='{CY}' r='{lerp(200, 520, rev):.0f}' fill='url(#halo)'/>")
        for k in range(14):
            a = k * 2 * math.pi / 14 + t * 0.4
            r1, r2 = 240, lerp(240, 470, rev)
            scene.append(f"<path d='M{CX + r1*math.cos(a-0.07):.0f} {CY + r1*math.sin(a-0.07):.0f} L{CX + r2*math.cos(a):.0f} {CY + r2*math.sin(a):.0f} "
                         f"L{CX + r1*math.cos(a+0.07):.0f} {CY + r1*math.sin(a+0.07):.0f} Z' fill='#fff3b0' opacity='{0.55*rev:.2f}'/>")
    # sombra gigante que llega por la derecha (tensión)
    if 5.0 < t < 7.6:
        sx = lerp(1250, CX, seg(t, 5.0, 7.2))
        scene.append(f"<ellipse cx='{sx:.0f}' cy='1785' rx='{lerp(80, 180, tension):.0f}' ry='26' fill='#000' opacity='{0.25*tension:.2f}'/>")
    # huevo de avestruz: entra rodando de 6,0 a 7,3
    k = seg(t, 6.0, 7.3)
    if t >= 6.0:
        bx = lerp(1300, CX, k)
        brot = lerp(220, 0, k) + (2 * math.sin(t * 2) if k >= 1 else 0)
        by = CY - 14 * abs(math.sin(k * math.pi * 3)) * (1 - k)
        scene.append(big_egg(t, bx, by, brot, rev, lerp(-1, -0.6, rev), 1.0 if t > REVELACION + 0.3 else 0.0))
    # huevo de gallina: entra rodando desde la izquierda
    hk = seg(t, 0, 2.0)
    hx = lerp(70, 470, hk) - 250 * seg(t, 5.6, 6.6)
    rolling = hk < 1
    hrot = lerp(-360, 0, hk) + (8 * math.sin(t * 3) if not rolling else 0)
    hop = 30 * abs(math.sin(t * 4.5)) * seg(t, 2.6, 3.0) * (1 - seg(t, 4.4, 4.8))
    jump = 60 * math.sin(math.pi * clamp((t - 5.3) / 0.45))     # salto del susto
    hy = 1690 - hop - jump + shake
    surprise = 1.0 if 5.2 < t < REVELACION + 0.2 else 0.0
    happy = 1.0 if (2.2 < t < 3.4) or t > REVELACION + 0.6 else 0.0
    look = 1.0 if t > 4.8 else lerp(-0.5, 0.5, 0.5 + 0.5 * math.sin(t * 1.5))
    sq = 1 + 0.08 * math.sin(t * 9) * seg(t, 2.6, 3.0) * (1 - seg(t, 4.4, 4.8))
    scene.append(hen_egg(t, hx, hy, hrot, surprise, happy, look, sq))
    # los 24 huevitos de gallina en corro alrededor del huevo grande
    if t >= REVELACION:
        for i in range(24):
            a = -math.pi / 2 + i * 2 * math.pi / 24
            at = REVELACION + 0.05 + i * 0.05
            sc = rebote(t, at, 0.35)
            if sc <= 0: continue
            R = 300 + 6 * math.sin(t * 3 + i)
            ex, ey = CX + R * math.cos(a), CY + R * 1.02 * math.sin(a)
            scene.append(f"<g transform='translate({ex:.1f},{ey:.1f}) scale({sc * 0.40:.3f}) rotate({8 * math.sin(t * 4 + i):.1f})'>"
                         f"<path d='{egg_path(*HEN)}' fill='#e8b07a' stroke='{INK}' stroke-width='12' stroke-linejoin='round'/>"
                         f"<path d='M-26 -34 Q-16 -52 0 -54' fill='none' stroke='#fff3df' stroke-width='12' stroke-linecap='round'/></g>")
    # polvo / chispas flotando
    for px, py, pr, sp in DUST:
        yy = (py - t * sp) % 800 + 1150
        col = mix("#fff4cf", "#fff0a0", rev)
        scene.append(f"<circle cx='{px + 18 * math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr * (1 + rev * 0.4):.1f}' fill='{col}' opacity='0.5'/>")
    s.append(f"<g transform='translate({shake * 0.5:.1f},0)'>" + zoom(CX, CY, cam, "".join(scene)) + "</g>")
    # destello de la revelación
    fl = clamp(1 - abs(t - REVELACION - 0.05) / 0.25)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.6 * fl:.2f}'/>")
    return svg("".join(s), defs)
