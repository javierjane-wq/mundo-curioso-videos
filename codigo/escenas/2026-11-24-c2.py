"""Pajita "rota" en un vaso de agua: la luz va ~25 % más lenta en el agua y se dobla (refracción).

Protagonista: un vaso de agua con cara (original) y una pajita de rayas que entra desde arriba.
Bajo el agua la pajita se ve desplazada (rota). Tensión: se levanta la pajita y la "rotura" sigue en
la superficie. Revelación: la cocina se oscurece, rayos de luz amarillos se doblan al salir del agua,
el agua brilla y zoom a la superficie.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.4    # rayos de luz que se doblan: golpe musical
MUSICA = 2

rng = np.random.default_rng(24)
BUBBLES = [(rng.uniform(395, 685), rng.uniform(0, 1), rng.uniform(5, 11), rng.uniform(40, 90)) for _ in range(16)]
DOTS = [(x, y) for y in range(140, 1060, 150) for x in range((y // 150 % 2) * 75 + 40, W, 150)]
SPARKS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28)) for _ in range(14)]

# vaso
GX, TOP, BOT = 540, 1150, 1750
TW, BW = 215, 170          # semiancho arriba / abajo
SURF = 1370                # nivel del agua


def half_w(y):
    return lerp(TW, BW, (y - TOP) / (BOT - TOP))


def straw_shape(color_a, color_b):
    """Pajita en coordenadas locales: eje vertical, de y=-640 (arriba) a y=0 (punta de abajo)."""
    s = [f"<rect x='-17' y='-640' width='34' height='640' rx='14' fill='{color_a}' stroke='{INK}' stroke-width='{LW}'/>"]
    for k in range(0, 590, 70):
        s.append(f"<path d='M-13 {-620 + k} L13 {-640 + k + 34} L13 {-640 + k + 58} L-13 {-620 + k + 24} Z' fill='{color_b}'/>")
    s.append(f"<rect x='-17' y='-640' width='34' height='640' rx='14' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='0' cy='-640' rx='17' ry='6' fill='#fff7f0' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def frame(t):
    night = seg(t, 6.6, 7.9)                     # la cocina se oscurece en la revelación
    rev = seg(t, 7.3, 8.1)                       # rayos de luz y brillo del agua
    # --- fondo: pared de la cocina ---
    top = mix("#ffe9c7", "#26306a", night); low = mix("#ffd6a5", "#3b4b8f", night)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<linearGradient id='water' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{mix('#8fdcff', '#7ff6ff', rev)}' stop-opacity='0.85'/>"
            f"<stop offset='1' stop-color='{mix('#3fa3e8', '#19c7ff', rev)}' stop-opacity='0.92'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='#fff6b0' stop-opacity='{0.85*rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#7ff6ff' stop-opacity='{0.35*rev:.3f}'/>"
            f"<stop offset='1' stop-color='#7ff6ff' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sun'><stop offset='0' stop-color='#fff8dc' stop-opacity='{0.55*(1-night):.3f}'/>"
            f"<stop offset='1' stop-color='#fff8dc' stop-opacity='0'/></radialGradient>")
    # trapecio del vaso (interior) para recortar
    hwS = half_w(SURF); hwB = half_w(BOT - 18)
    glass_in = f"M{GX - TW + 8} {TOP} L{GX + TW - 8} {TOP} L{GX + BW - 8} {BOT - 18} L{GX - BW + 8} {BOT - 18} Z"
    water_path = f"M{GX - hwS + 8:.0f} {SURF} L{GX + hwS - 8:.0f} {SURF} L{GX + hwB - 8:.0f} {BOT - 18} L{GX - hwB + 8:.0f} {BOT - 18} Z"
    defs += (f"<clipPath id='above'><rect x='0' y='0' width='{W}' height='{SURF}'/></clipPath>"
             f"<clipPath id='below'><path d='{water_path}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    for i, (x, y) in enumerate(DOTS):
        s.append(f"<circle cx='{x}' cy='{y}' r='10' fill='{mix('#ffc98a', '#33407e', night)}' opacity='0.55'/>")
    # rayo de sol suave por la izquierda
    s.append(f"<ellipse cx='{150 + 30 * pulso(t, 6):.0f}' cy='700' rx='520' ry='620' fill='url(#sun)'/>")
    # estrellitas de noche (en la pared, tenues)
    for i, (x, y) in enumerate(DOTS[::3]):
        a = night * (0.45 + 0.45 * math.sin(t * 4 + i))
        if a > 0.03:
            s.append(f"<circle cx='{x + 40}' cy='{y + 30}' r='4' fill='#fff' opacity='{a:.2f}'/>")
    # azulejos de la cocina detrás de la mesa
    tile = mix("#bfe8e0", "#2f4a80", night)
    s.append(f"<rect x='0' y='1080' width='{W}' height='700' fill='{tile}'/>")
    for x in range(0, W + 1, 135):
        s.append(f"<line x1='{x}' y1='1080' x2='{x}' y2='1780' stroke='{mix('#9fd3c9', '#253c6b', night)}' stroke-width='6'/>")
    for y in range(1080, 1780, 135):
        s.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='{mix('#9fd3c9', '#253c6b', night)}' stroke-width='6'/>")
    s.append(f"<line x1='0' y1='1080' x2='{W}' y2='1080' stroke='{INK}' stroke-width='{LW}'/>")

    scene = []
    # mesa de madera
    wood = mix("#d98b4a", "#6a4a52", night); wood2 = mix("#b86d35", "#523847", night)
    scene.append(f"<rect x='-20' y='1720' width='{W + 40}' height='240' fill='{wood}' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(f"<rect x='-20' y='1720' width='{W + 40}' height='40' fill='{wood2}' stroke='{INK}' stroke-width='{LW}'/>")
    for y in (1810, 1870):
        scene.append(f"<path d='M0 {y} Q270 {y - 18} 540 {y} T1080 {y}' fill='none' stroke='{wood2}' stroke-width='7'/>")
    # limón en la mesa (detalle secundario)
    lx = 900
    scene.append(f"<g transform='translate({lx},1700) rotate({4 * pulso(t, 2.2):.1f})'>"
                 f"<path d='M-70 20 A70 70 0 0 1 70 20 Z' fill='{mix('#ffe14d', '#a9a050', night)}' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M-50 20 A50 50 0 0 1 50 20 Z' fill='{mix('#fff6a8', '#c9c58a', night)}' stroke='{INK}' stroke-width='5'/>"
                 + "".join(f"<line x1='0' y1='20' x2='{50*math.cos(math.radians(a)):.0f}' y2='{20-50*math.sin(math.radians(a)):.0f}' stroke='{INK}' stroke-width='4'/>" for a in (30, 70, 110, 150))
                 + "</g>")
    # sombra del vaso
    scene.append(f"<ellipse cx='{GX}' cy='1752' rx='230' ry='22' fill='#000' opacity='0.22'/>")

    # --- pajita ---
    enter = seg(t, 0, 2.0)
    lift = seg(t, 5.0, 6.6) - seg(t, 6.6, 7.5)    # se levanta un poco y vuelve
    ang = 22 + 3 * math.sin(t * 2.1) * (1 - seg(t, 6.8, 7.4))
    slide = 350 * (1 - enter)                 # baja a lo largo de su eje
    tipx = 470 + slide * math.sin(math.radians(22))
    tipy = 1680 - slide * math.cos(math.radians(22)) - 170 * lift
    straw_col = (mix("#ffffff", "#e8ecff", night), mix("#ff4d5e", "#ff6b9a", night))
    straw = straw_shape(*straw_col)
    # parte de arriba (real)
    st_above = f"<g transform='translate({tipx:.1f},{tipy:.1f}) rotate({ang:.1f})'>{straw}</g>"
    # parte de abajo: se ve desplazada y más inclinada (refracción)
    shift = 105 * seg(t, 0.9, 1.8)
    # el punto donde la pajita cruza la superficie (para pivotar la parte sumergida)
    ra = math.radians(ang)
    dy = tipy - SURF
    cx = tipx + dy * math.tan(ra)            # x en la superficie
    st_below = (f"<g transform='translate({shift:.1f},0) translate({cx:.1f},{SURF}) rotate({-12 * seg(t, 0.9, 1.8):.1f}) translate({-cx:.1f},{-SURF})'>"
                f"<g transform='translate({tipx:.1f},{tipy:.1f}) rotate({ang:.1f})'>{straw}</g></g>")

    # vaso: cuerpo de cristal detrás
    glass_col = mix("#e9fbff", "#6f86c8", night)
    scene.append(f"<path d='{glass_in}' fill='{glass_col}' opacity='0.45'/>")
    # agua
    wob = 6 * math.sin(t * 3.2)
    scene.append(f"<path d='M{GX - hwS + 8:.0f} {SURF} Q{GX - 80} {SURF - wob:.1f} {GX} {SURF} T{GX + hwS - 8:.0f} {SURF} "
                 f"L{GX + hwB - 8:.0f} {BOT - 18} L{GX - hwB + 8:.0f} {BOT - 18} Z' fill='url(#water)'/>")
    # pajita (parte sumergida, desplazada) recortada al agua
    scene.append(f"<g clip-path='url(#below)' opacity='0.92'>{st_below}</g>")
    # burbujas
    for bx, ph, br, sp in BUBBLES:
        yy = BOT - 40 - ((t * sp + ph * 380) % 370)
        if SURF + 12 < yy < BOT - 30:
            hw = half_w(yy) - 30
            xx = clamp(bx + 8 * math.sin(t * 3 + ph * 6), GX - hw, GX + hw)
            scene.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='#ffffff' opacity='0.6' stroke='{INK}' stroke-width='3'/>")
    # línea de la superficie
    scene.append(f"<path d='M{GX - hwS + 8:.0f} {SURF} Q{GX - 80} {SURF - wob:.1f} {GX} {SURF} T{GX + hwS - 8:.0f} {SURF}' "
                 f"fill='none' stroke='{mix('#ffffff', '#fff6b0', rev)}' stroke-width='{lerp(6, 12, rev):.1f}' opacity='0.95'/>")
    # pajita parte de arriba (real), recortada sobre el agua
    scene.append(f"<g clip-path='url(#above)'>{st_above}</g>")

    # --- rayos de luz en la revelación ---
    if rev > 0.01:
        L = lerp(0, 1, rev)
        for k, off in enumerate((-45, 45)):
            x0, y0 = cx + 20 + off, 1640                   # sale de la pajita sumergida
            x1, y1 = cx + 110 + off, SURF                  # llega a la superficie
            x2, y2 = x1 + 300, SURF - 290                  # sale doblado (se aleja de la vertical)
            d_in = f"M{x0:.0f} {y0} L{x1:.0f} {y1}"
            d_out = f"M{x1:.0f} {y1} L{lerp(x1, x2, L):.0f} {lerp(y1, y2, L):.0f}"
            for d in (d_in, d_out):
                scene.append(f"<path d='{d}' stroke='{INK}' stroke-width='26' stroke-linecap='round' opacity='{0.8*rev:.2f}'/>")
                scene.append(f"<path d='{d}' stroke='#ffe14d' stroke-width='14' stroke-linecap='round' opacity='{rev:.2f}'/>")
            # punta de flecha al final
            ex, ey = lerp(x1, x2, L), lerp(y1, y2, L)
            scene.append(f"<circle cx='{ex:.0f}' cy='{ey:.0f}' r='{12 + 3*math.sin(t*9+k):.0f}' fill='#fff6b0' stroke='{INK}' stroke-width='5' opacity='{rev:.2f}'/>")
        # brillo en el punto donde se dobla
        scene.append(f"<circle cx='{cx + 110:.0f}' cy='{SURF}' r='{lerp(60, 320, rev):.0f}' fill='url(#glow)'/>")
        for sx, sy, ph in SPARKS:
            a = rev * (0.5 + 0.5 * math.sin(t * 7 + ph))
            px, py = cx + 110 + sx * 300, SURF + sy * 200
            scene.append(f"<path d='M{px:.0f} {py - 16:.0f} L{px + 5:.0f} {py - 5:.0f} L{px + 16:.0f} {py:.0f} L{px + 5:.0f} {py + 5:.0f} "
                         f"L{px:.0f} {py + 16:.0f} L{px - 5:.0f} {py + 5:.0f} L{px - 16:.0f} {py:.0f} L{px - 5:.0f} {py - 5:.0f} Z' fill='#fff8c8' opacity='{a:.2f}'/>")

    # contorno del vaso, reflejos y borde
    scene.append(f"<path d='M{GX - TW} {TOP} L{GX - BW} {BOT} L{GX + BW} {BOT} L{GX + TW} {TOP}' fill='none' stroke='{INK}' stroke-width='{LW + 2}' stroke-linejoin='round'/>")
    scene.append(f"<rect x='{GX - BW + 4}' y='{BOT - 26}' width='{2*BW - 8}' height='26' rx='6' fill='{mix('#d9f4ff', '#8aa3e0', night)}' stroke='{INK}' stroke-width='6'/>")
    scene.append(f"<ellipse cx='{GX}' cy='{TOP}' rx='{TW}' ry='22' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(f"<path d='M{GX - TW + 40} {TOP + 50} L{GX - BW + 40} {BOT - 60}' stroke='#ffffff' stroke-width='16' stroke-linecap='round' opacity='0.65'/>")
    scene.append(f"<path d='M{GX - TW + 78} {TOP + 60} L{GX - TW + 70} {TOP + 140}' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='0.6'/>")

    # cara del vaso (encima del agua, a la izquierda de la pajita)
    blink = 1.0 if (t % 2.7) > 0.13 else 0.12
    surprise = seg(t, 5.2, 6.0)
    er = lerp(24, 30, surprise)
    look_x = lerp(-4, 8, seg(t, 2.4, 3.2)) - 10 * seg(t, 7.3, 7.9)
    look_y = lerp(6, 10, seg(t, 2.4, 3.2)) - 16 * seg(t, 7.3, 7.9)
    fy = 1228 + 4 * math.sin(t * 2.6)
    for ex in (GX - 130, GX - 40):
        scene.append(f"<ellipse cx='{ex}' cy='{fy:.1f}' rx='{er + 4:.1f}' ry='{(er + 8) * blink:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            scene.append(f"<circle cx='{ex + look_x:.1f}' cy='{fy + look_y:.1f}' r='{er * 0.55:.1f}' fill='{INK}'/>"
                         f"<circle cx='{ex + look_x - 5:.1f}' cy='{fy + look_y - 6:.1f}' r='5' fill='#fff'/>")
    # mejillas y boca
    scene.append(f"<ellipse cx='{GX - 175}' cy='{fy + 50:.1f}' rx='20' ry='11' fill='#ff9db0' opacity='0.8'/>")
    scene.append(f"<ellipse cx='{GX + 5}' cy='{fy + 50:.1f}' rx='20' ry='11' fill='#ff9db0' opacity='0.8'/>")
    mo = lerp(6, 22, surprise) + 10 * rev
    scene.append(f"<ellipse cx='{GX - 85}' cy='{fy + 62:.1f}' rx='{lerp(26, 18, surprise):.1f}' ry='{mo / 2 + 4:.1f}' fill='#7a2730' stroke='{INK}' stroke-width='6'/>")

    z = 1 + 0.16 * seg(t, 7.3, 8.1)
    s.append(zoom(cx + 60, SURF, z, "".join(scene)))
    # viñeta nocturna suave
    if night > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#0a0f2a' opacity='{0.12*night:.3f}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
