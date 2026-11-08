"""2026-11-08-c1 · El camarón pistola: al cerrar su pinza crea una burbuja que alcanza unos 4.700 °C.

Fuente: Lohse et al., Nature 413, 477 (2001) "Snapping shrimp make flashing bubbles": al colapsar,
la burbuja de cavitación alcanza al menos 5.000 K (unos 4.700 °C) y emite un destello de luz.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.45   # la pinza se cierra: destello de la burbuja
MUSICA = 5

rng = np.random.default_rng(11)
BUBBLES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(5, 14), rng.uniform(40, 110), rng.uniform(0, 6.28)) for _ in range(34)]
MOTES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(45)]
SAND_DOTS = [(rng.uniform(0, W), rng.uniform(1640, 1900), rng.uniform(3, 7)) for _ in range(60)]

SX, SY, SS = 300, 1452, 1.08          # posición y escala del camarón
TIP = (SX + 455 * SS, SY + 22 * SS)   # punta de la pinza: allí nace la burbuja


def weed(x, base, h, col, ph, t):
    """Alga ondulante."""
    pts = []
    for i in range(9):
        k = i / 8
        sw = 38 * k * math.sin(t * 1.6 + ph + k * 2.5)
        pts.append((x + sw, base - h * k))
    left = " ".join(f"{px - 22 * (1 - k * 0.8):.0f},{py:.0f}" for (px, py), k in zip(pts, [i / 8 for i in range(9)]))
    right = " ".join(f"{px + 22 * (1 - k * 0.8):.0f},{py:.0f}" for (px, py), k in reversed(list(zip(pts, [i / 8 for i in range(9)]))))
    return f"<polygon points='{left} {right}' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"


def shrimp(t):
    """Camarón pistola original: cuerpo segmentado naranja con bandas, una pinza enorme con 'martillo'."""
    walk = seg(t, 0, 2.4)
    x = lerp(-80, SX, walk)
    walking = t < 2.45
    bob = 5 * math.sin(t * 18) if walking else 3 * math.sin(t * 2.4)
    # apertura del dedo móvil de la pinza (grados): se abre, tiembla y se cierra de golpe
    opn = 62 * seg(t, 2.7, 4.6)
    if 5.0 < t < REVELACION - 0.1:
        opn += 3 * math.sin(t * 38) * seg(t, 5.0, 6.0)
    if t >= REVELACION - 0.1:
        opn = 62 * (1 - clamp((t - (REVELACION - 0.1)) / 0.1))
    recoil = -14 * math.exp(-max(0, t - REVELACION) * 6) if t >= REVELACION else 0
    blink = 0.12 if ((t + 1.3) % 2.9) < 0.12 or abs(t - REVELACION - 0.15) < 0.12 else 1.0
    body = "#f26b3a"; band = "#ffd0a8"; dark = "#c84a22"
    g = [f"<g transform='translate({x + recoil:.1f},{SY + bob:.1f}) scale({SS})'>"]
    g.append(f"<ellipse cx='60' cy='128' rx='330' ry='22' fill='#0a2a3a' opacity='0.25'/>")
    # antenas (dos pares) ondulando
    for i, (ln, ph, w) in enumerate(((430, 0, 6), (330, 1.4, 5))):
        a1 = 18 * math.sin(t * 2.2 + ph); a2 = 26 * math.sin(t * 2.2 + ph + 1)
        g.append(f"<path d='M160 -38 Q{250 + i * 30} {-150 + a1:.0f} {ln} {-250 + a2 - i * 40:.0f}' fill='none' stroke='{INK}' stroke-width='{w + 6}' stroke-linecap='round'/>"
                 f"<path d='M160 -38 Q{250 + i * 30} {-150 + a1:.0f} {ln} {-250 + a2 - i * 40:.0f}' fill='none' stroke='#ff9a6a' stroke-width='{w}' stroke-linecap='round'/>")
    # patas (caminan)
    for i, lx in enumerate((10, 50, 90, 125)):
        st = 14 * math.sin(t * 18 + i * 1.7) if walking else 0
        g.append(f"<path d='M{lx} 30 L{lx - 18 + st:.0f} 82 L{lx - 4 + st:.0f} 120' fill='none' stroke='{INK}' stroke-width='13' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='M{lx} 30 L{lx - 18 + st:.0f} 82 L{lx - 4 + st:.0f} 120' fill='none' stroke='{dark}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")
    # pleópodos (bajo el abdomen)
    for i, px in enumerate((-50, -100, -148)):
        sw = 8 * math.sin(t * 7 + i)
        g.append(f"<path d='M{px} 40 L{px - 10 + sw:.0f} 78' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    # cola en abanico
    flick = 6 * math.sin(t * 3)
    g.append(f"<g transform='translate(-262,52) rotate({flick:.1f})'>"
             f"<path d='M0 0 L-70 -30 Q-95 10 -70 45 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M0 0 L-80 20 Q-90 60 -50 75 Z' fill='{dark}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M0 0 L-30 70 Q10 90 25 60 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # abdomen segmentado (curvado hacia abajo)
    segs = [(-232, 36, 60, 58), (-190, 22, 66, 70), (-145, 11, 70, 82), (-95, 4, 72, 90), (-42, 0, 74, 96)]
    for cx, cy, w, h in segs:
        g.append(f"<rect x='{cx - w / 2:.0f}' y='{cy - h / 2:.0f}' width='{w}' height='{h}' rx='{w * 0.45:.0f}' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M{cx - w / 2 + 8:.0f} {cy - h / 2 + 14:.0f} Q{cx:.0f} {cy - h / 2 + 2:.0f} {cx + w / 2 - 8:.0f} {cy - h / 2 + 14:.0f}' fill='none' stroke='{band}' stroke-width='8' stroke-linecap='round'/>")
    # caparazón
    g.append(f"<path d='M-10 -52 Q70 -82 150 -60 L196 -44 L150 -28 Q170 20 140 45 Q60 62 -10 48 Q-30 0 -10 -52 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M10 -30 Q70 -52 130 -38' fill='none' stroke='{band}' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<path d='M20 20 Q70 34 120 22' fill='none' stroke='{dark}' stroke-width='7' stroke-linecap='round'/>")
    # ojo grande (parpadea)
    g.append(f"<circle cx='132' cy='-64' r='30' fill='#fff' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<g transform='translate(140,-64) scale(1,{blink})'><circle r='15' fill='{INK}'/><circle cx='-5' cy='-6' r='5' fill='#fff'/></g>")
    # pinza pequeña
    g.append(f"<path d='M140 40 L200 72' stroke='{INK}' stroke-width='18' stroke-linecap='round'/><path d='M140 40 L200 72' stroke='{body}' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<path d='M196 64 Q238 58 246 76 Q232 88 198 82 Z' fill='{body}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # brazo de la pinza grande
    g.append(f"<path d='M120 10 L220 26' stroke='{INK}' stroke-width='40' stroke-linecap='round'/><path d='M120 10 L220 26' stroke='{dark}' stroke-width='24' stroke-linecap='round'/>")
    # pinza grande: palma + dedo fijo
    claw = "#ff5a2e"
    g.append(f"<path d='M210 -18 Q300 -50 372 -8 L462 18 Q470 34 452 40 L372 46 Q300 88 214 64 Q186 24 210 -18 Z' fill='{claw}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M236 2 Q296 -22 346 4' fill='none' stroke='#ffb08a' stroke-width='10' stroke-linecap='round'/>")
    for bx in (260, 300, 336):
        g.append(f"<circle cx='{bx}' cy='34' r='7' fill='#ffd23f' stroke='{INK}' stroke-width='4'/>")
    # dedo móvil (martillo) que gira sobre su articulación
    g.append(f"<g transform='translate(368,-6) rotate({-opn:.1f})'>"
             f"<path d='M-6 -18 Q50 -34 104 -4 Q112 10 98 16 Q50 8 -4 16 Z' fill='#ff7b3d' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<circle cx='22' cy='4' r='9' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")
    g.append(f"<circle cx='368' cy='-6' r='10' fill='{dark}' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def fish(t):
    """Pececillo presa: entra por la derecha y queda aturdido tras el destello."""
    stun = seg(t, REVELACION, REVELACION + 0.4)
    x = lerp(1090, 905, seg(t, 0, 3.2)) + 10 * math.sin(t * 2.1) * (1 - stun) - 40 * seg(t, REVELACION, 9.5)
    y = 1380 + 14 * math.sin(t * 2.7) - 90 * seg(t, REVELACION + 0.2, 10)
    rot = 160 * stun + 20 * math.sin(t * 3) * stun
    tail = 14 * math.sin(t * 12) * (1 - stun)
    blink = 0.12 if ((t + 2.0) % 3.4) < 0.12 else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"]
    g.append(f"<path d='M70 0 L128 -38 L{124 + tail:.0f} 0 L128 38 Z' fill='#2fb3e8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-10 -52 Q20 -86 52 -50' fill='#2fb3e8' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='0' cy='0' rx='86' ry='58' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M10 -54 Q-6 0 10 54' fill='none' stroke='#2fb3e8' stroke-width='16'/>")
    g.append(f"<path d='M40 -48 Q28 0 40 48' fill='none' stroke='#2fb3e8' stroke-width='12'/>")
    g.append(f"<ellipse cx='0' cy='0' rx='86' ry='58' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    if stun > 0.5:
        # ojos en espiral de aturdido
        g.append(f"<circle cx='-44' cy='-14' r='20' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M-44 -14 m-10 0 a10 10 0 1 1 10 10 a6 6 0 1 1 -6 -6' fill='none' stroke='{INK}' stroke-width='4'/>")
    else:
        g.append(f"<circle cx='-44' cy='-14' r='20' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<g transform='translate(-50,-14) scale(1,{blink})'><circle r='10' fill='{INK}'/><circle cx='-3' cy='-4' r='3.5' fill='#fff'/></g>")
    g.append(f"<path d='M-78 14 Q-66 22 -58 14' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append("</g>")
    if stun > 0:
        # estrellitas girando sobre el pez aturdido
        for i in range(3):
            a = t * 4 + i * 2.09
            sx, sy = x + 95 * math.cos(a), y - 90 + 28 * math.sin(a)
            g.append(f"<g transform='translate({sx:.0f},{sy:.0f}) rotate({a * 40:.0f}) scale({0.9 * stun:.2f})'>"
                     f"<path d='M0 -22 L6 -6 L22 0 L6 6 L0 22 L-6 6 L-22 0 L-6 -6 Z' fill='#fff27a' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/></g>")
    return "".join(g)


def frame(t):
    flash = seg(t, REVELACION, REVELACION + 0.12) * (1 - 0.75 * seg(t, REVELACION + 0.12, REVELACION + 1.4))
    heat = seg(t, REVELACION, REVELACION + 0.3)
    dim = seg(t, 4.8, 7.3) * (1 - heat)          # el agua se oscurece en la tensión
    top = mix(mix("#5fd0f0", "#2a7fb8", dim), "#ffe7a8", 0.55 * flash)
    mid = mix(mix("#1f9fd2", "#155e96", dim), "#ffb85a", 0.45 * flash)
    low = mix(mix("#0f6fa8", "#0b3f70", dim), "#d86a3a", 0.35 * flash)
    bx, by = TIP
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<linearGradient id='ray' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='0.35'/><stop offset='1' stop-color='#ffffff' stop-opacity='0'/></linearGradient>",
         "<radialGradient id='hot'><stop offset='0' stop-color='#ffffff' stop-opacity='1'/><stop offset='0.25' stop-color='#fff6b0' stop-opacity='0.95'/>"
         "<stop offset='0.55' stop-color='#ffb03a' stop-opacity='0.6'/><stop offset='1' stop-color='#ff6a1a' stop-opacity='0'/></radialGradient>",
         "<radialGradient id='sand' cx='0.5' cy='0' r='1'><stop offset='0' stop-color='#f6dc9a'/><stop offset='1' stop-color='#d9b46a'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sea)'/>"]
    z = 1 + 0.22 * seg(t, REVELACION, REVELACION + 1.2)
    sh_x = 7 * math.sin(t * 90) * math.exp(-max(0, t - REVELACION) * 5) if t >= REVELACION else 0
    s.append(f"<g transform='translate({sh_x:.1f},0)'>")
    s.append(zoom(bx - 160, by - 40, z, scene(t, flash, heat, dim)))
    s.append("</g>")
    # destello general
    if flash > 0.01:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe0' opacity='{0.55 * flash * (1 - seg(t, REVELACION + 0.12, REVELACION + 0.6)):.3f}'/>")
    s.append("</svg>")
    return "".join(s)


def scene(t, flash, heat, dim):
    s = []
    # superficie con ondas, arriba del todo
    wave = " ".join(f"{x},{40 + 14 * math.sin(x / 70 + t * 2):.0f}" for x in range(0, W + 40, 40))
    s.append(f"<polyline points='{wave}' fill='none' stroke='#e9fbff' stroke-width='8' opacity='0.6'/>")
    # rayos de luz
    for i, rx in enumerate((120, 380, 640, 900)):
        sw = 40 * math.sin(t * 0.7 + i)
        s.append(f"<polygon points='{rx + sw:.0f},0 {rx + 90 + sw:.0f},0 {rx + 260:.0f},1500 {rx + 60:.0f},1500' fill='url(#ray)' opacity='{0.8 - 0.5 * dim:.2f}'/>")
    # motas suspendidas
    for mx, my, mr, ph in MOTES:
        s.append(f"<circle cx='{mx + 12 * math.sin(t + ph):.0f}' cy='{(my - t * 8) % H:.0f}' r='{mr:.1f}' fill='#e9fbff' opacity='0.4'/>")
    # rocas lejanas
    far = mix("#2a6f8e", "#1b4a6a", dim)
    s.append(f"<path d='M0 1500 Q120 1380 260 1430 Q360 1330 480 1440 L480 1700 L0 1700 Z' fill='{far}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M700 1470 Q820 1360 940 1410 Q1020 1350 1080 1400 L1080 1700 L700 1700 Z' fill='{far}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # algas al fondo
    s.append(weed(60, 1700, 420, "#3fbf6a", 0, t))
    s.append(weed(140, 1700, 300, "#2e9e55", 1.2, t))
    s.append(weed(1010, 1700, 460, "#3fbf6a", 2.1, t))
    # coral
    cc = "#ff6fa8"
    s.append(f"<g transform='translate(620,1640)'><path d='M0 0 L0 -80 M0 -50 L-40 -110 M0 -60 L36 -120 M-20 -78 L-50 -82' stroke='{INK}' stroke-width='32' stroke-linecap='round' fill='none'/>"
             f"<path d='M0 0 L0 -80 M0 -50 L-40 -110 M0 -60 L36 -120 M-20 -78 L-50 -82' stroke='{cc}' stroke-width='18' stroke-linecap='round' fill='none'/></g>")
    # fondo de arena
    s.append(f"<path d='M0 1600 Q270 1560 540 1590 T1080 1580 L1080 1920 L0 1920 Z' fill='url(#sand)' stroke='{INK}' stroke-width='{LW}'/>")
    for dx, dy, dr in SAND_DOTS:
        s.append(f"<circle cx='{dx:.0f}' cy='{dy:.0f}' r='{dr:.1f}' fill='#c99a50' opacity='0.7'/>")
    for px, py, pr, col in ((180, 1700, 30, "#8c6a8f"), (930, 1720, 40, "#6f8ca0"), (500, 1800, 26, "#a07a5a")):
        s.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr * 1.4:.0f}' ry='{pr}' fill='{col}' stroke='{INK}' stroke-width='7'/>")
    # concha
    s.append(f"<g transform='translate(820,1820)'><path d='M-40 0 Q0 -60 40 0 Z' fill='#ffd7c2' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M0 0 L0 -30 M-18 0 L-10 -24 M18 0 L10 -24' stroke='{INK}' stroke-width='4'/></g>")
    # protagonistas
    s.append(fish(t))
    s.append(shrimp(t))
    # burbujas que suben
    for ux, uy, ur, sp, ph in BUBBLES:
        yy = (uy - t * sp) % (H + 100) - 50
        s.append(f"<circle cx='{ux + 14 * math.sin(t * 1.5 + ph):.0f}' cy='{yy:.0f}' r='{ur:.1f}' fill='#bdf2ff' fill-opacity='0.25' stroke='#e9fbff' stroke-width='3' opacity='0.7'/>")
    # burbuja caliente de la revelación
    bx, by = TIP
    if t >= REVELACION:
        k = t - REVELACION
        glow = 1 - 0.35 * seg(t, REVELACION + 0.6, DUR)
        r_hot = lerp(40, 300, seg(t, REVELACION, REVELACION + 0.25)) * (0.92 + 0.08 * pulso(t, 0.35))
        s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{r_hot:.0f}' fill='url(#hot)' opacity='{glow:.2f}'/>")
        # rayos de luz del destello
        for i in range(12):
            a = i * math.pi / 6 + t * 0.6
            l1, l2 = 70, lerp(90, 210, seg(t, REVELACION, REVELACION + 0.3)) + 20 * math.sin(t * 6 + i)
            s.append(f"<line x1='{bx + l1 * math.cos(a):.0f}' y1='{by + l1 * math.sin(a):.0f}' x2='{bx + l2 * math.cos(a):.0f}' y2='{by + l2 * math.sin(a):.0f}' "
                     f"stroke='#fff6b0' stroke-width='10' stroke-linecap='round' opacity='{0.85 * glow:.2f}'/>")
        core = lerp(10, 54, seg(t, REVELACION, REVELACION + 0.2)) * (0.9 + 0.1 * pulso(t, 0.25))
        s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{core:.0f}' fill='#ffffff' stroke='#ffd23f' stroke-width='8'/>")
        # ondas de choque
        for j in range(3):
            kk = (k - j * 0.35)
            if 0 < kk < 1.6:
                rr = 60 + kk * 520
                s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{rr:.0f}' fill='none' stroke='#ffffff' stroke-width='{lerp(14, 2, kk / 1.6):.1f}' opacity='{0.8 * (1 - kk / 1.6):.2f}'/>")
    return "".join(s)
