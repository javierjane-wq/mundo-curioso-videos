"""2026-11-14-c1 · Las primeras zanahorias cultivadas eran moradas (o amarillas); las naranjas llegaron después, en Europa.

Huerto con corte del suelo: una zanahoria naranja con cara asoma bajo tierra (hojas arriba).
Tensión: el suelo tiembla y el tiempo "rebobina" (anillos girando). Revelación: destello,
la zanahoria se vuelve MORADA y a su lado brota una zanahoria AMARILLA; zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.5
MUSICA = 8

rng = np.random.default_rng(14)
PEBBLES = [(rng.uniform(40, 1040), rng.uniform(1300, 1880), rng.uniform(10, 24)) for _ in range(26)]
PEBBLES = [p for p in PEBBLES if not (380 < p[0] < 700 and p[1] < 1820)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(180, 420), rng.uniform(6, 14), rng.uniform(0, 1)) for _ in range(28)]
GROUND = 1180

NARANJA = ("#ff8a1f", "#d9640a")
MORADA = ("#7b2fa8", "#4f1a73")
AMARILLA = ("#ffd23a", "#e0a915")


def hojas(x, y, t, s=1.0, fase=0.0):
    """Penacho de hojas de zanahoria: tallos finos con hojitas."""
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"]
    for i, ang in enumerate((-38, -18, 0, 18, 38)):
        a = ang + 6 * pulso(t, 2.2, fase + i * 0.17)
        L = 230 - abs(ang) * 1.6
        rad = math.radians(a)
        ex, ey = L * math.sin(rad), -L * math.cos(rad)
        cx, cy = ex * 0.4, ey * 0.6
        g.append(f"<path d='M0 0 Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f}' fill='none' stroke='{INK}' stroke-width='15' stroke-linecap='round'/>"
                 f"<path d='M0 0 Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f}' fill='none' stroke='#4caf3e' stroke-width='7' stroke-linecap='round'/>")
        for k in (0.45, 0.7, 0.92):
            px, py = ex * k, ey * k
            for side in (-1, 1):
                rot = a + side * 50
                g.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='15' ry='34' fill='#5cc94a' stroke='{INK}' stroke-width='5' "
                         f"transform='rotate({rot:.0f} {px:.0f} {py:.0f}) translate(0,-22)'/>")
    g.append("</g>")
    return "".join(g)


def zanahoria(x, y, t, col, s=1.0, mirada=0.0, cara=True, fase=0.0):
    """Raíz de zanahoria original con cara. (x, y) = cuello de la raíz a ras de suelo."""
    c1, c2 = col
    g = [hojas(x, y + 6 * s, t, s, fase)]
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>")
    body = "M-95 0 Q-110 120 -70 300 Q-35 460 0 560 Q35 460 70 300 Q110 120 95 0 Q0 -26 -95 0 Z"
    g.append(f"<path d='{body}' fill='{c1}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # sombra lateral
    g.append(f"<path d='M50 20 Q78 140 52 300 Q30 420 6 520 Q40 440 68 300 Q100 140 88 14 Z' fill='{c2}' opacity='0.8'/>")
    # anillos (arrugas de la raíz)
    for yy, w in ((95, 58), (175, 54), (255, 46), (345, 36), (430, 24)):
        side = 1 if yy % 2 else -1
        g.append(f"<path d='M{side*w:.0f} {yy} q{-side*26} 6 {-side*44} 2' fill='none' stroke='{c2}' stroke-width='7' stroke-linecap='round'/>")
    # raicillas
    g.append(f"<path d='M-78 230 l-34 10 M74 360 l32 6 M-40 440 l-26 12' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    if cara:
        blink = 1.0 if ((t + fase) % 2.9) > 0.13 else 0.12
        for ex in (-36, 36):
            g.append(f"<ellipse cx='{ex}' cy='95' rx='25' ry='30' fill='#fff' stroke='{INK}' stroke-width='6'/>")
            g.append(f"<g transform='translate({ex + mirada:.1f},100) scale(1,{blink})'><circle r='14' fill='{INK}'/>"
                     f"<circle cx='-5' cy='-6' r='5' fill='#fff'/></g>")
        g.append(f"<path d='M-26 150 Q0 178 26 150' fill='{INK}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<ellipse cx='-62' cy='140' rx='14' ry='9' fill='#ff5a7a' opacity='0.55'/>"
                 f"<ellipse cx='62' cy='140' rx='14' ry='9' fill='#ff5a7a' opacity='0.55'/>")
    g.append("</g>")
    return "".join(g)


def gusano(t):
    x = (120 + t * 38) % 1300 - 120
    y = 1760
    g = [f"<g transform='translate({x:.0f},{y})'>"]
    for i in range(5):
        dy = 10 * math.sin(t * 8 - i * 0.9)
        g.append(f"<circle cx='{-i*26}' cy='{dy:.1f}' r='20' fill='#f4a0a8' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='6' cy='{10*math.sin(t*8)-4:.1f}' r='4' fill='{INK}'/></g>")
    return "".join(g)


def frame(t):
    sube = seg(t, 0, 2.0)                       # la zanahoria asoma desde abajo
    tiembla = seg(t, 5.0, 7.4)                  # tensión
    rev = seg(t, 7.5, 8.1)                      # cambio de color
    flash = clamp(1 - abs(t - 7.55) / 0.35) if t > 7.2 else 0
    shake = 10 * tiembla * math.sin(t * 55) if t < 7.5 else 0

    sky_top = mix("#5ab8f0", "#3b2f7a", rev * 0.35)
    sky_low = mix("#bfe9ff", "#f3d9ff", rev * 0.6)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{sky_top}'/>"
            f"<stop offset='1' stop-color='{sky_low}'/></linearGradient>"
            f"<linearGradient id='soil' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#9a5b32'/>"
            f"<stop offset='1' stop-color='#5e3419'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff6ff' stop-opacity='{0.9*rev:.3f}'/>"
            f"<stop offset='0.4' stop-color='#d69cff' stop-opacity='{0.6*rev:.3f}'/>"
            f"<stop offset='1' stop-color='#9a4dff' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol y nubes
    s.append(f"<circle cx='880' cy='260' r='{95 + 6*pulso(t, 2):.0f}' fill='#fff3a8' opacity='0.5'/>"
             f"<circle cx='880' cy='260' r='72' fill='#ffe066' stroke='{INK}' stroke-width='7'/>")
    for i, (cx, cy, sc) in enumerate(((150, 700, 1.2), (700, 560, 0.9), (420, 860, 1.0))):
        dx = (t * (16 + 6 * i)) % 1400 - 250
        s.append(f"<g transform='translate({(cx + dx) % 1400 - 200:.0f},{cy}) scale({sc})'>"
                 f"<path d='M0 50 Q0 0 50 8 Q80 -36 130 0 Q185 -14 190 40 Q215 60 180 72 L20 72 Q-20 70 0 50 Z' "
                 f"fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")

    sc = []  # contenido con zoom
    # colinas lejanas y huerto
    sc.append(f"<path d='M0 1080 Q220 990 460 1060 T900 1040 T1080 1060 L1080 {GROUND} L0 {GROUND} Z' fill='#7fd16a' stroke='{INK}' stroke-width='{LW}'/>")
    # valla de madera al fondo
    for vx in range(-20, 1100, 120):
        sc.append(f"<path d='M{vx} 1150 L{vx} 1060 L{vx+22} 1040 L{vx+44} 1060 L{vx+44} 1150 Z' fill='#e8c48a' stroke='{INK}' stroke-width='6'/>")
    sc.append(f"<rect x='-10' y='1085' width='1100' height='18' fill='#d8ad6c' stroke='{INK}' stroke-width='6'/>")
    # suelo en corte
    sc.append(f"<rect x='-10' y='{GROUND}' width='1100' height='{H-GROUND+10}' fill='url(#soil)' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<path d='M-10 {GROUND} Q120 {GROUND-24} 260 {GROUND} T540 {GROUND} T820 {GROUND} T1090 {GROUND} L1090 {GROUND+30} L-10 {GROUND+30} Z' fill='#5fbf4b' stroke='{INK}' stroke-width='7'/>")
    sc.append(f"<path d='M-10 1500 Q270 1470 540 1505 T1090 1490' fill='none' stroke='#4e2a13' stroke-width='6' opacity='0.6'/>")
    for px, py, pr in PEBBLES:
        sc.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='{pr:.0f}' ry='{pr*0.65:.0f}' fill='#b98b62' stroke='{INK}' stroke-width='5'/>")
    sc.append(gusano(t))
    # anillos del "tiempo" que giran en la tensión
    if 5.0 < t < 8.2:
        a = tiembla * (1 - rev)
        for k, r in enumerate((300, 380, 460)):
            rot = -t * (120 + 40 * k)
            sc.append(f"<circle cx='540' cy='1470' r='{r}' fill='none' stroke='#fff3c4' stroke-width='10' "
                      f"stroke-dasharray='40 60' opacity='{0.55*a:.2f}' transform='rotate({rot:.0f} 540 1470)'/>")
    # halo morado
    if rev > 0:
        sc.append(f"<circle cx='540' cy='1450' r='{lerp(200, 620, rev):.0f}' fill='url(#halo)'/>")
    # zanahoria amarilla que brota a la izquierda en la revelación
    pop = rebote(t, 7.7, 0.6)
    if pop > 0:
        ya = GROUND + 8 + (1 - min(1, pop)) * 300
        sc.append(f"<g transform='translate(195,{ya:.0f}) scale({0.62*min(pop,1.1):.3f}) translate(-195,{-ya:.0f})'>"
                  + zanahoria(190, ya, t, AMARILLA, 1.0, mirada=8, fase=1.1) + "</g>")
    # zanahoria protagonista
    col = (mix(NARANJA[0], MORADA[0], rev), mix(NARANJA[1], MORADA[1], rev))
    y0 = GROUND + 12 + lerp(320, 0, sube) + 4 * pulso(t, 1.3)
    mir = lerp(0, -10, seg(t, 7.8, 8.4))
    sc.append(f"<g transform='translate({shake:.1f},0)'>" + zanahoria(560, y0, t, col, 1.15, mirada=mir) + "</g>")
    # tierra que salta al asomar
    if t < 2.4:
        for i in range(8):
            k = seg(t, 0.1 + i * 0.05, 1.6 + i * 0.05)
            ang = math.radians(-160 + i * 20)
            px = 560 + math.cos(ang) * 260 * k
            py = GROUND - math.sin(-ang) * 0 - 220 * math.sin(math.pi * k)
            if 0 < k < 1:
                sc.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='14' fill='#8a4f2a' stroke='{INK}' stroke-width='5'/>")
    # chispas de la revelación
    if t > 7.5:
        for ang, rad, r, ph in SPARK:
            k = ((t - 7.5) * 0.7 + ph) % 1
            px = 560 + math.cos(ang) * rad * (0.6 + k)
            py = 1420 + math.sin(ang) * rad * (0.6 + k) * 0.9
            sc.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{r*(1-k):.1f}' fill='#fff4ff' opacity='{0.9*(1-k):.2f}'/>")
    # mariposa
    bx = 140 + (t * 70) % 900; by = 1010 + 40 * math.sin(t * 2.3)
    fl = 0.35 + 0.65 * abs(math.sin(t * 14))
    sc.append(f"<g transform='translate({bx:.0f},{by:.0f})'><g transform='scale({fl:.2f},1)'>"
              f"<ellipse cx='-20' cy='-8' rx='22' ry='16' fill='#ff7ab8' stroke='{INK}' stroke-width='5'/>"
              f"<ellipse cx='20' cy='-8' rx='22' ry='16' fill='#ff7ab8' stroke='{INK}' stroke-width='5'/></g>"
              f"<rect x='-4' y='-22' width='8' height='30' rx='4' fill='{INK}'/></g>")

    z = 1 + 0.16 * seg(t, 7.5, 10)
    s.append(zoom(560, 1450, z, "".join(sc)))
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.75*flash:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
