"""2026-11-26-c2 · Física: un imán suelta el clavo de hierro cuando este se pone al rojo (770 °C, punto de Curie).

Un imán de herradura (con cara) atrae un clavo de hierro que cuelga de un hilo; un mechero lo calienta,
el clavo se pone al rojo y, en la REVELACION, deja de ser magnético: el imán lo suelta y el clavo se
balancea lejos. Todo en la mitad de abajo; arriba, pared tranquila del laboratorio.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 6.9    # el imán suelta el clavo
MUSICA = 7

rng = np.random.default_rng(26)
MOTES = [(rng.uniform(0, W), rng.uniform(80, 1000), rng.uniform(2, 5), rng.uniform(0, 6.28)) for _ in range(30)]
SPARKS = [(rng.uniform(-1, 1), rng.uniform(0.4, 1.0), rng.uniform(0, 1)) for _ in range(26)]
BURST = [(rng.uniform(0, 6.28), rng.uniform(250, 520), rng.uniform(8, 15)) for _ in range(40)]

PIV = (700, 1040)       # punto del que cuelga el hilo
WIRE = 165              # largo del hilo
NAIL = 215              # largo del clavo
TH_MAX = 36.0           # ángulo (grados) hacia el imán cuando está atraído


def angulo(t):
    if t < REVELACION:
        k = clamp(t / 1.1)
        a = TH_MAX * (1 - math.cos(k * math.pi * 1.0)) / 2
        if t > 1.1:  # pequeño rebote al pegarse
            a = TH_MAX - 3 * math.exp(-(t - 1.1) * 6) * math.cos((t - 1.1) * 25)
        return a + 0.6 * math.sin(t * 9)  # tiembla un poco: el imán tira
    u = t - REVELACION
    return TH_MAX * math.cos(2 * math.pi * u / 1.35) * math.exp(-u * 0.75)


def punto(theta, d):
    r = math.radians(theta)
    return PIV[0] - d * math.sin(r), PIV[1] + d * math.cos(r)


def color_clavo(h):
    if h < 0.5:
        return mix("#8d97a3", "#a3321c", h / 0.5)
    return mix("#a3321c", "#ff9a2e", (h - 0.5) / 0.5)


def iman(t, rev):
    """Imán de herradura rojo abierto a la derecha, con polos plateados y cara."""
    x0 = lerp(-260, 0, seg(t, 0, 0.9))
    bob = 4 * math.sin(t * 3.2)
    cx, cy, R, r, xe = 280, 1430, 170, 70, 470
    g = [f"<g transform='translate({x0:.1f},{bob:.1f})'>"]
    g.append(f"<ellipse cx='300' cy='1606' rx='210' ry='16' fill='#000' opacity='0.2'/>")
    body = (f"M{xe} {cy - R} L{cx} {cy - R} A{R} {R} 0 0 0 {cx} {cy + R} L{xe} {cy + R} "
            f"L{xe} {cy + r} L{cx} {cy + r} A{r} {r} 0 0 1 {cx} {cy - r} L{xe} {cy - r} Z")
    g.append(f"<path d='{body}' fill='#e5392c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brillo
    g.append(f"<path d='M{cx} {cy - R + 22} A{R - 22} {R - 22} 0 0 0 {cx - 120} {cy - 70}' fill='none' stroke='#ff8a7a' stroke-width='14' stroke-linecap='round' opacity='0.8'/>")
    # polos
    for y0 in (cy - R, cy + r):
        g.append(f"<rect x='{xe - 62}' y='{y0}' width='62' height='{R - r}' fill='#d9dee5' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<rect x='{xe - 50}' y='{y0 + 14}' width='12' height='{R - r - 28}' rx='5' fill='#ffffff' opacity='0.8'/>")
    # cara en la pata de arriba
    worry = seg(t, 4.2, 5.2) * (1 - rev)
    blink = 0.12 if ((t + 1.3) % 2.7) < 0.12 and rev < 0.5 else 1.0
    eye_r = lerp(17, 22, rev)
    for ex in (322, 382):
        g.append(f"<ellipse cx='{ex}' cy='1296' rx='{eye_r:.1f}' ry='{eye_r * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        look = lerp(6, 2, rev)
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look:.1f}' cy='1298' r='{lerp(9, 8, rev):.1f}' fill='{INK}'/>")
            g.append(f"<circle cx='{ex + look - 3:.1f}' cy='1294' r='3' fill='#fff'/>")
    # cejas preocupadas
    if worry > 0.02:
        g.append(f"<path d='M304 {1268 - 4 * worry:.1f} L338 {1272 - 10 * worry:.1f} M366 {1272 - 10 * worry:.1f} L400 {1268 - 4 * worry:.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round' fill='none'/>")
        # gota de sudor
        g.append(f"<path d='M418 {1262 + 30 * ((t * 0.8) % 1):.0f} q8 14 0 20 q-8 -6 0 -20 Z' fill='#8fd8ff' stroke='{INK}' stroke-width='3' opacity='{worry:.2f}'/>")
    if rev > 0.3:
        g.append(f"<ellipse cx='352' cy='1336' rx='12' ry='{lerp(4, 14, rev):.1f}' fill='#7a1410' stroke='{INK}' stroke-width='5'/>")
    else:
        g.append(f"<path d='M334 1330 Q352 {1346 - 14 * worry:.1f} 370 1330' stroke='{INK}' stroke-width='6' fill='none' stroke-linecap='round'/>")
    g.append(f"<circle cx='306' cy='1326' r='9' fill='#ff9a8f' opacity='0.8'/><circle cx='398' cy='1326' r='9' fill='#ff9a8f' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g)


def mechero(t):
    """Mechero de laboratorio (tubo metálico) con llama azul que se enciende a 2,3 s."""
    x, top = 540, 1470
    g = [f"<ellipse cx='{x}' cy='1606' rx='70' ry='10' fill='#000' opacity='0.2'/>",
         f"<path d='M{x - 66} 1606 L{x - 52} 1570 L{x + 52} 1570 L{x + 66} 1606 Z' fill='#5b6470' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<rect x='{x - 20}' y='{top}' width='40' height='104' rx='6' fill='#b8c0ca' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='{x - 26}' y='1520' width='52' height='20' rx='5' fill='#7c8794' stroke='{INK}' stroke-width='5'/>",
         f"<rect x='{x - 10}' y='{top + 8}' width='7' height='86' rx='3' fill='#fff' opacity='0.6'/>",
         # tubo de gas
         f"<path d='M{x + 52} 1590 Q{x + 120} 1600 {x + 140} 1640' stroke='{INK}' stroke-width='16' fill='none' stroke-linecap='round'/>",
         f"<path d='M{x + 52} 1590 Q{x + 120} 1600 {x + 140} 1640' stroke='#f0a63a' stroke-width='8' fill='none' stroke-linecap='round'/>"]
    on = seg(t, 2.3, 2.7)
    if on > 0:
        hgt = 215 * on * (1 + 0.06 * math.sin(t * 31) + 0.04 * math.sin(t * 17))
        wd = 34 * (1 + 0.08 * math.sin(t * 23))
        sway = 6 * math.sin(t * 13)
        ty = top - hgt
        g.append(f"<path d='M{x - wd} {top} Q{x - wd * 0.9} {top - hgt * 0.5} {x + sway} {ty} Q{x + wd * 0.9} {top - hgt * 0.5} {x + wd} {top} Z' fill='#3e8dff' opacity='0.85' stroke='{INK}' stroke-width='5'/>")
        h2 = hgt * 0.55
        g.append(f"<path d='M{x - wd * 0.5} {top} Q{x - wd * 0.4} {top - h2 * 0.5} {x + sway * 0.5} {top - h2} Q{x + wd * 0.4} {top - h2 * 0.5} {x + wd * 0.5} {top} Z' fill='#bfe3ff'/>")
        # chispitas
        for sx, sp, ph in SPARKS[:12]:
            u = (t * sp * 1.4 + ph) % 1
            g.append(f"<circle cx='{x + sx * 40 + sway:.0f}' cy='{top - 80 - u * 220:.0f}' r='{4 * (1 - u) + 1:.1f}' fill='#ffd166' opacity='{(1 - u) * on:.2f}'/>")
    elif t > 2.05:
        g.append(f"<circle cx='{x}' cy='{top - 12}' r='14' fill='#ffd166' stroke='{INK}' stroke-width='4'/>")
    return "".join(g)


def soporte():
    return (f"<ellipse cx='850' cy='1606' rx='120' ry='12' fill='#000' opacity='0.2'/>"
            f"<rect x='760' y='1580' width='180' height='28' rx='8' fill='#4a5560' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='868' y='1020' width='24' height='566' rx='8' fill='#b8c0ca' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='684' y='1020' width='206' height='22' rx='8' fill='#b8c0ca' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='860' y='1012' width='40' height='38' rx='6' fill='#5b6470' stroke='{INK}' stroke-width='6'/>")


def clavo(t, theta, h):
    col = color_clavo(h)
    hx, hy = punto(theta, WIRE)
    tx, ty = punto(theta, WIRE + NAIL)
    mx, my = punto(theta, WIRE + NAIL * 0.5)
    g = [f"<line x1='{PIV[0]}' y1='{PIV[1]}' x2='{hx:.1f}' y2='{hy:.1f}' stroke='{INK}' stroke-width='5'/>",
         f"<circle cx='{PIV[0]}' cy='{PIV[1]}' r='8' fill='#5b6470' stroke='{INK}' stroke-width='4'/>"]
    if h > 0.05:
        g.append(f"<circle cx='{mx:.1f}' cy='{my:.1f}' r='{lerp(60, 200, h):.0f}' fill='url(#heat)'/>")
    g.append(f"<g transform='translate({hx:.1f},{hy:.1f}) rotate({theta:.2f})'>")
    g.append(f"<path d='M-14 12 L14 12 L14 {NAIL - 42} L0 {NAIL} L-14 {NAIL - 42} Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<rect x='-30' y='-2' width='60' height='19' rx='6' fill='{col}' stroke='{INK}' stroke-width='6'/>")
    hl = mix("#e8edf2", "#fff2b0", h)
    g.append(f"<rect x='-6' y='18' width='5' height='{NAIL - 60}' rx='2' fill='{hl}' opacity='0.75'/>")
    g.append("</g>")
    return "".join(g)


def campo(t, theta, h):
    """Líneas de fuerza azules entre los polos y la punta del clavo; se apagan con el calor."""
    vis = seg(t, 0.6, 1.3) * (1 - seg(t, 5.0, 6.7))
    if vis < 0.02:
        return ""
    tx, ty = punto(theta, WIRE + NAIL)
    x0 = lerp(-260, 0, seg(t, 0, 0.9))
    g = []
    for i, (py, bend) in enumerate([(1310, -60), (1330, -20), (1550, 60), (1530, 110)]):
        sx = 470 + x0
        c = f"M{sx} {py} Q{(sx + tx) / 2 + 40:.0f} {(py + ty) / 2 + bend:.0f} {tx:.0f} {ty:.0f}"
        g.append(f"<path d='{c}' fill='none' stroke='#7fe0ff' stroke-width='6' stroke-dasharray='16 14' "
                 f"stroke-dashoffset='{-t * 60 + i * 9:.0f}' stroke-linecap='round' opacity='{0.85 * vis:.2f}'/>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.35)
    flash = clamp(1 - (t - REVELACION) / 0.9) if t >= REVELACION else 0
    h = seg(t, 2.6, 6.6)                     # calor del clavo
    theta = angulo(t)
    warm = 0.35 * h + 0.25 * rev
    wall_top = mix("#1f5a73", "#5a3550", warm)
    wall_low = mix("#3f8fa8", "#c9714a", warm)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_top}'/><stop offset='1' stop-color='{wall_low}'/></linearGradient>",
         "<radialGradient id='heat'><stop offset='0' stop-color='#fff1a8' stop-opacity='0.9'/>"
         "<stop offset='0.35' stop-color='#ff8c2e' stop-opacity='0.55'/><stop offset='1' stop-color='#ff4d1a' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.95 * flash:.3f}'/>"
         f"<stop offset='0.4' stop-color='#ffe27a' stop-opacity='{0.6 * flash:.3f}'/><stop offset='1' stop-color='#ffb03a' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    # azulejos suaves en la pared
    for yy in range(140, 1600, 150):
        s.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='#ffffff' stroke-width='3' opacity='0.07'/>")
    for xx in range(90, W, 180):
        s.append(f"<line x1='{xx}' y1='0' x2='{xx}' y2='1600' stroke='#ffffff' stroke-width='3' opacity='0.05'/>")
    for mx, my, mr, ph in MOTES:
        yy = (my - t * 18) % 940 + 60
        s.append(f"<circle cx='{mx + 14 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#ffffff' opacity='{0.25 + 0.15 * math.sin(t * 2 + ph):.2f}'/>")

    z = 1 + 0.16 * seg(t, REVELACION, 8.0)
    cx, cy = 560, 1360
    s.append(f"<g transform='translate({cx},{cy}) scale({z:.4f}) translate({-cx},{-cy})'>")
    # estantería baja con frascos (fondo, mitad de abajo)
    s.append(f"<rect x='620' y='1150' width='420' height='16' rx='5' fill='#8a5a36' stroke='{INK}' stroke-width='6' opacity='0.0'/>")
    # mesa
    s.append(f"<rect x='-40' y='1600' width='{W + 80}' height='40' fill='#b8743f' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='-40' y='1640' width='{W + 80}' height='300' fill='#8e5530' stroke='{INK}' stroke-width='{LW}'/>")
    for px in range(60, W, 240):
        s.append(f"<line x1='{px}' y1='1652' x2='{px}' y2='1920' stroke='#6e3f22' stroke-width='6'/>")
    s.append(f"<line x1='-40' y1='1612' x2='{W + 40}' y2='1612' stroke='#d79a62' stroke-width='5'/>")
    s.append("<g transform='translate(480,1605) scale(1.12) translate(-480,-1605)'>")
    s.append(soporte())
    s.append(mechero(t))
    s.append(campo(t, theta, h))
    s.append(clavo(t, theta, h))
    s.append(iman(t, rev))
    # destello y chispas de la revelación
    if t >= REVELACION:
        tx, ty = punto(TH_MAX, WIRE + NAIL)
        s.append(f"<circle cx='{tx:.0f}' cy='{ty:.0f}' r='{lerp(120, 780, ease(clamp((t - REVELACION) / 0.7))):.0f}' fill='url(#flash)'/>")
        u = clamp((t - REVELACION) / 1.1)
        if u < 1:
            for ang, dist, rr in BURST:
                bx = tx + math.cos(ang) * dist * ease(u)
                by = ty + math.sin(ang) * dist * ease(u)
                s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{rr * (1 - u) + 1:.1f}' fill='#ffd84a' stroke='{INK}' stroke-width='2' opacity='{1 - u:.2f}'/>")
        # ondas de calor que suben del clavo
    if h > 0.2:
        mx, my = punto(theta, WIRE + NAIL * 0.5)
        for i in range(3):
            u = (t * 0.7 + i / 3) % 1
            yy = my - 40 - u * 180
            s.append(f"<path d='M{mx - 30:.0f} {yy:.0f} q15 -18 30 0 t30 0' fill='none' stroke='#ffd9a0' stroke-width='5' stroke-linecap='round' opacity='{(1 - u) * 0.7 * h:.2f}'/>")
    s.append("</g></g></svg>")
    return "".join(s)
