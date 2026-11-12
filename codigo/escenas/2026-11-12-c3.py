"""2026-11-12-c3 · Inventos: el polo (helado de palo) lo inventó un niño de 11 años en 1905.

Un vaso de refresco de naranja con un palito de remover dentro entra deslizándose sobre una
mesita del porche al atardecer. Anochece, sale la luna, se encienden las ventanas del barrio.
Empieza a nevar, la escarcha cubre el vaso y el refresco (con carita) tirita y se congela.
En la revelación amanece de golpe: el bloque helado salta del vaso, da media vuelta y queda
convertido en un POLO con su palo, entre destellos.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45   # amanece y el bloque helado salta del vaso convertido en polo
MUSICA = 7

rng = np.random.default_rng(1905)
STARS = [(rng.uniform(0, W), rng.uniform(40, 1000), rng.uniform(2.5, 5.5), rng.uniform(0, 6.28)) for _ in range(60)]
SNOW = [(rng.uniform(0, W), rng.uniform(0, 1920), rng.uniform(4, 9), rng.uniform(70, 140), rng.uniform(0, 6.28)) for _ in range(55)]
BUBBLES = [(rng.uniform(-90, 90), rng.uniform(0, 1), rng.uniform(5, 11), rng.uniform(0.6, 1.2)) for _ in range(14)]
CRYST = [(rng.uniform(-0.8, 0.8), rng.uniform(-0.85, 0.85), rng.uniform(8, 16), rng.uniform(0, 90)) for _ in range(16)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(190, 330), rng.uniform(0, 0.5), rng.uniform(14, 26)) for _ in range(16)]
CLOUDS = [(150, 620, 1.2, 10), (780, 300, 0.9, 14), (980, 760, 0.7, 8)]
HOUSES = [(40, 1150, 120, 90), (190, 1120, 110, 120), (330, 1165, 130, 80), (720, 1140, 120, 100),
          (860, 1110, 100, 130), (990, 1155, 120, 85)]

GT, GB = 1150, 1560          # borde superior e inferior del vaso
ST, SB = 1240, 1545          # superficie y fondo del refresco
CY0 = (ST + SB) / 2          # centro del bloque de refresco
HB = (SB - ST) / 2           # media altura del bloque


def hw(y):
    """Media anchura interior del vaso a la altura y."""
    return lerp(150, 120, (y - GT) / (GB - GT)) - 14


def sky(t, n, d):
    top = mix(mix("#4c5fb8", "#0c1536", n), "#4fc0ff", d)
    mid = mix(mix("#c86fa0", "#1c2a62", n), "#9ee0ff", d)
    low = mix(mix("#ffb47a", "#33427e", n), "#fff1a8", d)
    return (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>")


def cloud(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y}) scale({sc})' opacity='0.9'>"
            f"<path d='M0 50 Q10 0 70 10 Q100 -35 160 0 Q220 -20 240 50 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def barrio(t, n, d):
    """Colinas lejanas con casitas cuyas ventanas se encienden de noche."""
    hill1 = mix(mix("#7a6aa8", "#1d2650", n), "#7cc97a", d)
    hill2 = mix(mix("#8f7bb5", "#253063", n), "#95d98a", d)
    g = [f"<path d='M0 1150 Q200 1050 420 1110 T860 1080 T1080 1110 L1080 1400 L0 1400 Z' fill='{hill1}' stroke='{INK}' stroke-width='{LW}'/>"]
    win = mix("#3b3355", "#ffd45c", n * (1 - d))
    for i, (x, y, w, h) in enumerate(HOUSES):
        wall = mix(mix("#e6b9a0", "#4a4a78", n), ["#ffd9b0", "#ffe9a8", "#ffc8c8"][i % 3], d)
        roof = mix(mix("#b6545a", "#5a2f4a", n), "#e8584f", d)
        g.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{wall}' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<path d='M{x - 12} {y} L{x + w / 2} {y - 50} L{x + w + 12} {y} Z' fill='{roof}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<rect x='{x + w * 0.2:.0f}' y='{y + 20}' width='{w * 0.25:.0f}' height='26' fill='{win}' stroke='{INK}' stroke-width='4'/>")
        g.append(f"<rect x='{x + w * 0.55:.0f}' y='{y + 20}' width='{w * 0.25:.0f}' height='26' fill='{win}' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<path d='M0 1250 Q300 1170 600 1230 T1080 1210 L1080 1400 L0 1400 Z' fill='{hill2}' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(g)


def porche(t, n, d, f):
    """Barandilla de madera, suelo de tablas y mesita redonda."""
    wood = mix(mix("#c9824a", "#5b4064", n), "#d98d4f", d)
    dark = mix(mix("#9a5f33", "#3d2c4a", n), "#a9662f", d)
    frost = f * (1 - d)
    g = [f"<rect x='0' y='1700' width='{W}' height='220' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>"]
    for yy in (1760, 1830, 1900):
        g.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='{INK}' stroke-width='5'/>")
    for x in range(30, W, 96):
        g.append(f"<rect x='{x}' y='1330' width='38' height='370' rx='8' fill='{wood}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='-20' y='1300' width='{W + 40}' height='46' rx='10' fill='{wood}' stroke='{INK}' stroke-width='{LW}'/>")
    if frost > 0.01:
        g.append(f"<rect x='-20' y='1296' width='{W + 40}' height='16' rx='8' fill='#ffffff' opacity='{0.85 * frost:.2f}'/>")
    # mesita
    g.append(f"<rect x='510' y='1570' width='60' height='300' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='540' cy='1875' rx='150' ry='28' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='540' cy='1582' rx='330' ry='44' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='540' cy='1562' rx='330' ry='44' fill='{wood}' stroke='{INK}' stroke-width='{LW}'/>")
    if frost > 0.01:
        g.append(f"<ellipse cx='540' cy='1556' rx='300' ry='32' fill='#ffffff' opacity='{0.6 * frost:.2f}'/>")
    return "".join(g)


def glass_back(cx):
    d = f"M{cx - 150} {GT} L{cx + 150} {GT} L{cx + 120} {GB} Q{cx} {GB + 14} {cx - 120} {GB} Z"
    return f"<path d='{d}' fill='#dff4ff' opacity='0.55'/>"


def glass_front(cx, f):
    d = f"M{cx - 150} {GT} L{cx + 150} {GT} L{cx + 120} {GB} Q{cx} {GB + 14} {cx - 120} {GB} Z"
    g = [f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<ellipse cx='{cx}' cy='{GT}' rx='150' ry='16' fill='none' stroke='{INK}' stroke-width='6'/>",
         f"<path d='M{cx - 112} {GT + 40} L{cx - 92} {GB - 50}' stroke='#ffffff' stroke-width='16' stroke-linecap='round' opacity='0.75'/>",
         f"<path d='M{cx + 108} {GT + 50} L{cx + 100} {GT + 140}' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.6'/>"]
    if f > 0.01:   # escarcha que sube desde el fondo y baja desde el borde
        for i in range(9):
            yy = GB - 20 - i * 22 * f
            g.append(f"<ellipse cx='{cx - 124 + (i % 3) * 10:.0f}' cy='{yy:.0f}' rx='{18 + 5 * (i % 2)}' ry='16' fill='#ffffff' opacity='{0.75 * f:.2f}'/>")
            g.append(f"<ellipse cx='{cx + 112 - (i % 3) * 10:.0f}' cy='{yy - 8:.0f}' rx='{17 + 5 * ((i + 1) % 2)}' ry='15' fill='#ffffff' opacity='{0.75 * f:.2f}'/>")
        g.append(f"<path d='M{cx - 150} {GT} Q{cx - 110} {GT + 30 * f + 10:.0f} {cx - 70} {GT + 8} Q{cx - 20} {GT + 40 * f + 10:.0f} {cx + 30} {GT + 8} "
                 f"Q{cx + 90} {GT + 34 * f + 10:.0f} {cx + 150} {GT}' fill='#ffffff' stroke='{INK}' stroke-width='4' opacity='{f:.2f}'/>")
    return "".join(g)


def bloque(t, f, d, pop):
    """El refresco (o el bloque helado) en coordenadas locales centradas en (0,0)."""
    col = mix("#ff8a24", "#ffad5c", f)
    col = mix(col, "#ff9a2e", d)
    wt, wb = hw(ST), hw(SB)
    # al convertirse en polo, la parte de abajo (lejos del palo) se redondea
    rnd = pop
    wb2 = lerp(wb, wt * 0.96, rnd)
    k = lerp(0, 1, rnd)
    d_ = (f"M{-wt:.0f} {-HB:.0f} L{wt:.0f} {-HB:.0f} L{wb2:.0f} {HB - 60 * k:.0f} "
          f"Q{wb2:.0f} {HB + 40 * k:.0f} 0 {HB + 40 * k:.0f} Q{-wb2:.0f} {HB + 40 * k:.0f} {-wb2:.0f} {HB - 60 * k:.0f} Z")
    g = []
    # palito
    ang = 0 if pop > 0 else (10 * math.sin(t * 6) * (1 - seg(t, 2.2, 3.0)))
    g.append(f"<g transform='rotate({ang:.1f} 0 {-HB:.0f})'><rect x='-22' y='{-HB - 270:.0f}' width='44' height='{300 + HB * 0.5:.0f}' rx='22' "
             f"fill='#f1d199' stroke='{INK}' stroke-width='{LW}'/>"
             f"<line x1='-6' y1='{-HB - 240:.0f}' x2='-6' y2='{-HB - 40:.0f}' stroke='#d8ae6a' stroke-width='6' stroke-linecap='round'/></g>")
    g.append(f"<path d='{d_}' fill='{col}' stroke='{INK}' stroke-width='{LW if pop > 0 else 0}' stroke-linejoin='round'/>")
    # superficie del refresco (líquido) con ondas al entrar
    if pop == 0:
        wave = 10 * math.sin(t * 9) * (1 - seg(t, 1.4, 2.6))
        g.append(f"<path d='M{-wt:.0f} {-HB:.0f} Q{-wt / 2:.0f} {-HB - wave:.0f} 0 {-HB:.0f} T{wt:.0f} {-HB:.0f}' fill='none' stroke='#ffd08a' stroke-width='10' stroke-linecap='round'/>")
        # burbujas (desaparecen al congelarse)
        for bx, ph, br, sp in BUBBLES:
            yy = HB - ((t * sp + ph) % 1) * 2 * HB
            a = (1 - f) * 0.85
            if a > 0.03:
                g.append(f"<circle cx='{bx:.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='#ffe2b0' stroke='#e06a10' stroke-width='3' opacity='{a:.2f}'/>")
    # cristales de hielo
    ice = max(f, d)
    if ice > 0.02:
        for cxr, cyr, cr, rot in CRYST:
            x = cxr * wt * 0.85; y = cyr * HB
            g.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({rot:.0f})' opacity='{0.8 * ice:.2f}'>"
                     f"<path d='M{-cr:.0f} 0 L{cr:.0f} 0 M0 {-cr:.0f} L0 {cr:.0f} M{-cr * 0.7:.0f} {-cr * 0.7:.0f} L{cr * 0.7:.0f} {cr * 0.7:.0f}' stroke='#fff6e8' stroke-width='4' stroke-linecap='round'/></g>")
        g.append(f"<path d='M{-wt + 26:.0f} {-HB + 40:.0f} L{-wt + 40:.0f} {HB - 50:.0f}' stroke='#fff3dd' stroke-width='18' stroke-linecap='round' opacity='{0.7 * ice:.2f}'/>")
    return "".join(g)


def cara(t, f, d, pop):
    blink = 0.12 if ((t + 1.0) % 2.9) < 0.12 or abs(t - 5.6) < 0.06 else 1.0
    shiver = 4 * math.sin(t * 60) * f * (1 - d)
    big = 1 + 0.2 * seg(t, REVELACION + 0.3, REVELACION + 0.7)
    look = lerp(0, -12, seg(t, 3.0, 3.6)) * (1 - seg(t, 5.0, 5.4))     # mira la luna (arriba)
    g = []
    for ex in (-50, 50):
        g.append(f"<g transform='translate({ex + shiver:.1f},-20) scale({big:.3f},{big * blink:.3f})'>"
                 f"<ellipse rx='27' ry='32' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{4 if ex < 0 else -4}' cy='{look + 4:.1f}' r='15' fill='{INK}'/>"
                 f"<circle cx='{-1 if ex < 0 else -9}' cy='{look - 3:.1f}' r='6' fill='#fff'/></g>")
    for cx in (-86, 86):
        g.append(f"<ellipse cx='{cx}' cy='22' rx='18' ry='10' fill='#ff5a6e' opacity='{0.6 * (1 - f) + 0.6 * d:.2f}'/>")
    if d > 0.05:
        g.append(f"<path d='M-36 32 Q0 {32 + 44 * d:.0f} 36 32 Z' fill='#7a2a2a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    elif f > 0.3:   # tiritando: boca en zigzag
        g.append(f"<path d='M-34 40 L-20 30 L-6 40 L8 30 L22 40 L34 32' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round' transform='translate({shiver:.1f},0)'/>")
    else:
        g.append(f"<path d='M-28 34 Q0 58 28 34' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    return "".join(g)


def frame(t):
    n = seg(t, 2.2, 4.8)                 # anochece
    f = seg(t, 5.0, 7.3)                 # se congela
    d = seg(t, REVELACION - 0.15, REVELACION + 0.45)    # amanece de golpe
    pop = seg(t, REVELACION, REVELACION + 0.55)

    defs = sky(t, n, d)
    defs += ("<radialGradient id='glow'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.95'/>"
             "<stop offset='0.5' stop-color='#ffe27a' stop-opacity='0.5'/><stop offset='1' stop-color='#ffd04a' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]

    # estrellas
    for sx, sy, sr, ph in STARS:
        a = n * (1 - d) * (0.55 + 0.45 * math.sin(t * 3 + ph))
        if a > 0.03:
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # nubes
    for i, (cx, cy, sc, sp) in enumerate(CLOUDS):
        x = (cx + t * sp * 3) % 1400 - 200
        s.append(cloud(x, cy, sc, mix(mix("#ffd2c0", "#4a5590", n), "#ffffff", d)))
    # luna
    my = lerp(1180, 870, seg(t, 2.4, 5.0))
    ma = seg(t, 2.4, 3.4) * (1 - d)
    if ma > 0.02:
        s.append(f"<g opacity='{ma:.2f}'><circle cx='880' cy='{my:.0f}' r='70' fill='#fff6cf' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='860' cy='{my - 18:.0f}' r='14' fill='#eadfae'/><circle cx='905' cy='{my + 20:.0f}' r='10' fill='#eadfae'/></g>")
    # sol de la mañana
    if d > 0.01:
        sy = lerp(1250, 1030, d)
        s.append(f"<circle cx='540' cy='{sy:.0f}' r='{lerp(120, 330, d):.0f}' fill='url(#glow)'/>")
        s.append(f"<circle cx='540' cy='{sy:.0f}' r='95' fill='#fff2a0' stroke='#ffb43a' stroke-width='9'/>")

    escena = [barrio(t, n, d), porche(t, n, d, f)]

    # vaso: entra deslizándose y en la revelación se aparta a la derecha
    cx = lerp(350, 540, seg(t, 0, 1.4)) + lerp(0, 270, seg(t, REVELACION, REVELACION + 0.6))
    tilt = 5 * math.sin(t * 8) * (1 - seg(t, 1.2, 2.0))
    shake = 4 * math.sin(t * 55) * f * (1 - d)
    gx = cx + shake
    escena.append(f"<ellipse cx='{gx:.0f}' cy='{GB + 6}' rx='140' ry='18' fill='#000' opacity='0.22'/>")
    escena.append(f"<g transform='rotate({tilt:.2f} {gx:.0f} {GB})'>")
    escena.append(glass_back(gx))

    # bloque de refresco / polo
    bx = lerp(gx, 430, pop)
    by = lerp(CY0, 1170, pop) - 120 * math.sin(math.pi * pop) + (6 * math.sin(t * 3) if pop >= 1 else 0)
    rot = 180 * seg(t, REVELACION + 0.05, REVELACION + 0.55)
    sc = 1 + 0.12 * pop
    blk = bloque(t, f, d, pop)
    if pop <= 0:
        escena.append(f"<g transform='translate({bx:.1f},{by:.1f})'>{blk}{cara(t, f, d, pop)}</g>")
        escena.append(glass_front(gx, f))
        escena.append("</g>")
    else:
        escena.append(glass_front(gx, f * (1 - 0.5 * d)))
        escena.append("</g>")
        # rayos de luz detrás del polo
        ra = d * (0.35 + 0.1 * math.sin(t * 4))
        rays = "".join(f"<path d='M0 0 L{520 * math.cos(math.radians(a - 6)):.0f} {520 * math.sin(math.radians(a - 6)):.0f} "
                       f"L{520 * math.cos(math.radians(a + 6)):.0f} {520 * math.sin(math.radians(a + 6)):.0f} Z' fill='#fff6b0'/>"
                       for a in range(int(t * 20) % 30, 360, 30))
        escena.append(f"<g transform='translate({bx:.0f},{by:.0f})' opacity='{ra:.2f}'>{rays}</g>")
        escena.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='300' fill='url(#glow)' opacity='{0.8 * d:.2f}'/>")
        escena.append(f"<ellipse cx='{bx:.0f}' cy='1560' rx='{110 * pop:.0f}' ry='16' fill='#000' opacity='0.2'/>")
        escena.append(f"<g transform='translate({bx:.1f},{by:.1f}) scale({sc:.3f}) rotate({rot:.1f})'>{blk}</g>")
        escena.append(f"<g transform='translate({bx:.1f},{by + 10 * (1 - pop):.1f}) scale({sc:.3f})'>{cara(t, f, d, pop)}</g>")
        # gota que cae del polo
        dt = (t - (REVELACION + 0.9)) % 1.1
        if t > REVELACION + 0.9:
            dy = by + (HB + 40) * sc + 10 + 240 * (dt / 1.1) ** 2
            escena.append(f"<path d='M{bx + 60:.0f} {dy - 22:.0f} Q{bx + 74:.0f} {dy:.0f} {bx + 60:.0f} {dy + 8:.0f} Q{bx + 46:.0f} {dy:.0f} {bx + 60:.0f} {dy - 22:.0f} Z' "
                          f"fill='#ff9a2e' stroke='{INK}' stroke-width='4'/>")
        # destellos
        for a, rr, dl, sz in SPARK:
            k = clamp((t - REVELACION - dl) / 1.2)
            if 0 < k < 1:
                r2 = rr + 120 * k
                x = bx + r2 * math.cos(a); y = by + r2 * math.sin(a) * 0.9
                z = sz * math.sin(math.pi * k)
                escena.append(f"<path d='M{x:.0f} {y - z:.0f} L{x + z * 0.3:.0f} {y - z * 0.3:.0f} L{x + z:.0f} {y:.0f} L{x + z * 0.3:.0f} {y + z * 0.3:.0f} "
                              f"L{x:.0f} {y + z:.0f} L{x - z * 0.3:.0f} {y + z * 0.3:.0f} L{x - z:.0f} {y:.0f} L{x - z * 0.3:.0f} {y - z * 0.3:.0f} Z' fill='#fffbe0' stroke='{INK}' stroke-width='3'/>")

    # nieve
    sn = seg(t, 4.6, 5.4) * (1 - d)
    if sn > 0.02:
        for x0, y0, r, sp, ph in SNOW:
            y = (y0 + t * sp) % 1920
            x = x0 + 18 * math.sin(t * 1.5 + ph)
            s_op = sn * (0.5 if y < 1000 else 0.9)
            escena.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#ffffff' opacity='{s_op:.2f}'/>")

    z = 1 + 0.12 * seg(t, REVELACION, DUR)
    s.append(zoom(480, 1300, z, "".join(escena)))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
