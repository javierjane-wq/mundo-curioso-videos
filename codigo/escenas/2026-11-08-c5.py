"""2026-11-08-c5 · La Gran Pirámide de Guiza no era color arena: estaba recubierta de bloques de
caliza blanca de Tura, pulida, que brillaba al sol (el revestimiento se perdió y se reutilizó).

0-2,5 s  un camello original entra caminando por el desierto con la Gran Pirámide detrás.
2,5-5 s  la pirámide de hoy: escalonada, color arena; nubes, pájaros y palmera moviéndose.
5-7,5 s  "viaje atrás en el tiempo": el Sol retrocede por el cielo y se levanta un remolino de arena.
7,5-10 s REVELACION: destello y zoom: las caras se cubren de caliza blanca pulida que brilla,
         con rayos de sol y destellos; el camello abre mucho los ojos.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 4

rng = np.random.default_rng(58)
A = (560, 1030)            # vértice
L = (70, 1665)             # esquina izquierda
F = (640, 1725)            # esquina delantera
R = (1010, 1650)           # esquina derecha
CURSOS = 16
SAND = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(46)]
GLINTS = [(0.30, 0.45), (0.55, 0.62), (0.18, 0.75), (0.70, 0.35), (0.45, 0.85)]
CLOUDS = [(160, 1130, 1.0), (760, 1210, 0.8), (980, 1090, 0.7)]


def p(a, b, k):
    return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def piramide(t, blanca):
    g = []
    # sombra en el suelo
    g.append(f"<path d='M{F[0]} {F[1]} L{R[0]} {R[1]} L1080 1700 L760 1790 Z' fill='#b9853f' opacity='0.45'/>")
    izq = mix("#e0a85a", "#fbf7ee", blanca)
    der = mix("#b47a3a", "#e3d9c6", blanca)
    g.append(f"<polygon points='{poly([A, L, F])}' fill='{izq}'/>")
    g.append(f"<polygon points='{poly([A, F, R])}' fill='{der}'/>")
    # hiladas de bloques (desaparecen al cubrirse de caliza)
    op = 1 - blanca
    if op > 0.01:
        for k in range(1, CURSOS):
            f = k / CURSOS
            a1, b1, c1 = p(A, L, f), p(A, F, f), p(A, R, f)
            g.append(f"<polyline points='{poly([a1, b1, c1])}' fill='none' stroke='#8a5a2a' stroke-width='5' opacity='{op:.2f}'/>")
            # escalón: borde claro bajo cada hilada
            g.append(f"<polyline points='{poly([(a1[0], a1[1] + 5), (b1[0], b1[1] + 5)])}' fill='none' stroke='#f3c983' stroke-width='3' opacity='{op:.2f}'/>")
            # juntas verticales alternas
            f2 = (k + 1) / CURSOS
            for side, (P0, P1) in enumerate(((A, L), (A, R))):
                n = 2 + k // 2
                for j in range(1, n + 1):
                    m = (j - 0.5 * (k % 2)) / (n + 0.5)
                    if not 0.05 < m < 0.95: continue
                    top = p(p(P0, P1, f), p(A, F, f), m)
                    bot = p(p(P0, P1, f2), p(A, F, f2), m)
                    g.append(f"<line x1='{top[0]:.1f}' y1='{top[1]:.1f}' x2='{bot[0]:.1f}' y2='{bot[1]:.1f}' stroke='#8a5a2a' stroke-width='4' opacity='{op * 0.8:.2f}'/>")
        # algunos bloques rotos en las aristas
        for f in (0.35, 0.6, 0.82):
            q = p(A, L, f)
            g.append(f"<path d='M{q[0]:.0f} {q[1]:.0f} l14 4 l-6 16 Z' fill='#9c6a33' opacity='{op:.2f}'/>")
    # brillo que recorre la caliza pulida
    if blanca > 0.05:
        sx = lerp(-300, 1300, ((t - 7.45) / 1.6) % 1.0)
        g.append(f"<g clip-path='url(#caras)'><polygon points='{sx - 60:.0f},1000 {sx + 40:.0f},1000 {sx - 140:.0f},1800 {sx - 240:.0f},1800' fill='#ffffff' opacity='{0.75 * blanca:.2f}'/>"
                 f"<polygon points='{sx + 80:.0f},1000 {sx + 110:.0f},1000 {sx - 70:.0f},1800 {sx - 100:.0f},1800' fill='#ffffff' opacity='{0.6 * blanca:.2f}'/></g>")
    # contornos gruesos
    g.append(f"<polygon points='{poly([A, L, F, R])}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<line x1='{A[0]}' y1='{A[1]}' x2='{F[0]}' y2='{F[1]}' stroke='{INK}' stroke-width='{LW - 2}'/>")
    # destellos en forma de estrella
    if blanca > 0.05:
        for i, (u, v) in enumerate(GLINTS):
            base = p(L, F, u) if i % 2 == 0 else p(F, R, u)
            q = p(A, base, v)
            s = blanca * (0.6 + 0.4 * math.sin(t * 7 + i * 1.7)) * 50
            g.append(f"<g transform='translate({q[0]:.0f},{q[1]:.0f}) rotate({t * 40 + i * 20:.0f})'>"
                     f"<path d='M0 {-s:.1f} L{s * 0.22:.1f} 0 L0 {s:.1f} L{-s * 0.22:.1f} 0 Z M{-s:.1f} 0 L0 {s * 0.22:.1f} L{s:.1f} 0 L0 {-s * 0.22:.1f} Z' fill='#fffbe0'/></g>")
    return "".join(g)


def camello(t):
    """Camello dromedario original: una joroba, cuello largo curvado, patas largas."""
    walk = t < 6.2
    x = lerp(-70, 300, seg(t, 0, 6.2))
    ph = t * 6.5
    bob = 5 * math.sin(ph * 2) if walk else 2 * math.sin(t * 2.5)
    sorpresa = seg(t, 7.5, 8.0)
    blink = 0.12 if (t % 2.8) < 0.12 and sorpresa < 0.5 else 1.0
    col, col2 = "#d39552", "#b87838"
    g = [f"<g transform='translate({x:.1f},{1700 + bob:.1f})'>"]
    g.append("<ellipse cx='10' cy='175' rx='190' ry='22' fill='#000' opacity='0.18'/>")
    # patas (traseras y delanteras, alternando)
    for i, (lx, fase, c) in enumerate(((-95, 0, col2), (95, math.pi, col2), (-70, math.pi, col), (120, 0, col))):
        a = 18 * math.sin(ph + fase) if walk else 0
        g.append(f"<g transform='translate({lx},30) rotate({a:.1f})'>"
                 f"<path d='M-16 0 L-12 75 Q-14 90 -10 100 L-10 140 L12 140 L10 100 Q14 88 12 75 L16 0 Z' fill='{c}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<ellipse cx='2' cy='143' rx='20' ry='9' fill='#7a4f2a' stroke='{INK}' stroke-width='6'/></g>")
    # cuerpo y joroba
    g.append(f"<path d='M-150 10 Q-160 -40 -110 -55 Q-60 -150 10 -140 Q70 -130 100 -60 Q150 -55 160 -15 Q165 40 110 55 L-110 55 Q-150 50 -150 10 Z' "
             f"fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-60 -100 Q0 -130 50 -110' fill='none' stroke='#e8b373' stroke-width='10' stroke-linecap='round'/>")
    # cola
    sw = 10 * math.sin(t * 3)
    g.append(f"<path d='M-148 0 Q-175 30 {-168 + sw:.0f} 70' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # cuello y cabeza (mira hacia la pirámide al revelar)
    tilt = lerp(0, -14, sorpresa) + 3 * math.sin(t * 2)
    g.append(f"<g transform='translate(140,-20) rotate({tilt:.1f})'>")
    g.append(f"<path d='M-10 10 Q40 -10 55 -110 L95 -120 Q85 -20 30 40 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M50 -160 Q90 -175 140 -150 Q170 -135 165 -110 Q160 -90 120 -92 L95 -95 Q55 -100 45 -125 Q40 -150 50 -160 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M140 -110 Q155 -108 160 -118' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='150' cy='-135' rx='6' ry='4' fill='{INK}'/>")
    g.append(f"<path d='M58 -158 L48 -185 L72 -165 Z' fill='{col2}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    er = lerp(15, 21, sorpresa)
    g.append(f"<circle cx='95' cy='-140' r='{er:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<g transform='translate({99 + 3 * sorpresa:.1f},{-140 - 4 * sorpresa:.1f}) scale(1,{blink})'><circle r='{lerp(8, 10, sorpresa):.1f}' fill='{INK}'/><circle cx='-3' cy='-3' r='3' fill='#fff'/></g>")
    g.append(f"<path d='M78 -{163 + 6 * sorpresa:.0f} Q95 -{170 + 8 * sorpresa:.0f} 112 -{162 + 6 * sorpresa:.0f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g></g>")
    return "".join(g)


def palmera(t):
    sw = 4 * math.sin(t * 1.6)
    g = [f"<g transform='translate(985,1880) rotate({sw:.1f})'>"]
    g.append(f"<path d='M-22 0 Q-40 -250 10 -470 L36 -466 Q0 -250 22 0 Z' fill='#a06a3a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(1, 9):
        y = -k * 52
        g.append(f"<path d='M{-24 + k * 2} {y} Q0 {y - 10} {22 + k * 1.5:.0f} {y}' fill='none' stroke='{INK}' stroke-width='5'/>")
    for a, ln in ((-160, 190), (-125, 170), (-60, 190), (-20, 170), (-95, 150), (10, 140)):
        b = a + 3 * math.sin(t * 2.2 + a)
        g.append(f"<g transform='translate(22,-470) rotate({b:.1f})'><path d='M0 0 Q{ln * 0.5:.0f} -40 {ln} 25 Q{ln * 0.5:.0f} -5 0 12 Z' fill='#4fae4a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    for cx in (10, 34):
        g.append(f"<circle cx='{cx}' cy='-462' r='14' fill='#6b3f1f' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    retro = seg(t, 5.0, 7.3)                       # el tiempo va hacia atrás
    blanca = seg(t, 7.45, 8.2)
    flash = max(0.0, 1 - abs(t - 7.5) / 0.35)
    dim = math.sin(math.pi * retro) * (1 - blanca)  # cielo se oscurece a medio viaje
    top = mix(mix("#3f9fe6", "#2b3f8a", dim), "#55b8ff", blanca)
    low = mix(mix("#ffe2a0", "#f2a36b", dim), "#fff1c4", blanca)
    # el Sol retrocede de derecha a izquierda describiendo un arco
    ang = lerp(0.22, 0.82, retro)
    sun_x = 540 + 420 * math.cos(math.pi * ang); sun_y = 1050 - 330 * math.sin(math.pi * ang)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='#fff8d8' stop-opacity='0.9'/><stop offset='1' stop-color='#ffd27a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='rayos' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#fffbe6' stop-opacity='{0.7 * blanca:.2f}'/><stop offset='1' stop-color='#fff2b0' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='caras'><polygon points='{poly([A, L, F, R])}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.13 * seg(t, 7.45, 10)
    c = []
    # rayos de luz detrás de la pirámide en la revelación
    if blanca > 0.01:
        rays = "".join(f"<path d='M0 0 L-40 -900 L40 -900 Z' fill='url(#rayos)' transform='rotate({k * 22.5 + t * 12:.1f})'/>" for k in range(16))
        c.append(f"<g transform='translate({A[0]},{A[1] + 250})'><circle r='700' fill='url(#rayos)'/>{rays}</g>")
    # Sol
    c.append(f"<circle cx='{sun_x:.0f}' cy='{sun_y:.0f}' r='190' fill='url(#glow)'/>")
    c.append(f"<circle cx='{sun_x:.0f}' cy='{sun_y:.0f}' r='72' fill='#fff3b0' stroke='#ffb347' stroke-width='9'/>")
    # nubes
    for i, (cx, cy, sc) in enumerate(CLOUDS):
        dx = ((t * (14 + 8 * i) - 260 * retro * (1 + i)) % 1500) - 300
        c.append(f"<g transform='translate({(cx + dx) % 1500 - 200:.0f},{cy}) scale({sc})' opacity='0.95'>"
                 f"<path d='M0 50 Q-10 0 50 5 Q70 -40 130 -15 Q180 -40 210 10 Q260 10 250 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # pájaros
    for i in range(3):
        bx = (t * 70 + i * 160) % 1400 - 200 + 40 * i
        by = 1120 + 40 * i + 12 * math.sin(t * 2 + i)
        fl = 18 * math.sin(t * 9 + i)
        c.append(f"<path d='M{bx - 26:.0f} {by - fl:.0f} Q{bx - 12:.0f} {by - 8:.0f} {bx:.0f} {by:.0f} Q{bx + 12:.0f} {by - 8:.0f} {bx + 26:.0f} {by - fl:.0f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # suelo lejano y dunas
    c.append(f"<path d='M0 1560 Q270 1520 540 1555 T1080 1545 L1080 1920 L0 1920 Z' fill='#f2c77d' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(piramide(t, blanca))
    c.append(f"<path d='M0 1740 Q260 1690 560 1760 T1080 1740 L1080 1920 L0 1920 Z' fill='#f6d38f' stroke='{INK}' stroke-width='{LW}'/>")
    for rx, ry in ((420, 1850), (720, 1890), (150, 1900)):
        c.append(f"<ellipse cx='{rx}' cy='{ry}' rx='34' ry='16' fill='#d4a35e' stroke='{INK}' stroke-width='6'/>")
    c.append(palmera(t))
    c.append(camello(t))
    # arena flotando; remolino durante el viaje en el tiempo
    for i, (px, py, pr, ph) in enumerate(SAND):
        swirl = retro * (1 - blanca)
        ax = px + 30 * math.sin(t * 1.3 + ph) + swirl * 260 * math.sin(t * 4 + ph)
        ay = (py - t * 25 - swirl * 300 * ((i % 5) / 5)) % 900 + 1000
        col = "#fff6c8" if blanca > 0.5 else "#e8b56a"
        c.append(f"<circle cx='{ax % W:.0f}' cy='{ay:.0f}' r='{pr * (1 + swirl):.1f}' fill='{col}' opacity='{0.5 + 0.3 * swirl:.2f}'/>")
    # anillos de "viaje en el tiempo"
    if 0 < retro < 1 and blanca < 0.5:
        for k in range(3):
            r = ((t * 380 + k * 220) % 700)
            c.append(f"<circle cx='{A[0]}' cy='1380' r='{r:.0f}' fill='none' stroke='#ffffff' stroke-width='6' opacity='{0.45 * math.sin(math.pi * retro) * (1 - r / 700):.2f}'/>")
    s.append(zoom(560, 1360, z, "".join(c)))
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffdf0' opacity='{0.85 * flash:.2f}'/>")
    from lib import svg
    return svg("".join(s), defs)
