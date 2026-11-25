"""La mimosa púdica (planta sensible): si la tocan, pliega sus hojitas y deja caer las hojas;
lo hace soltando agua de unas «bisagras» (pulvínulos) en la base de las hojas, y se cree que es
una defensa contra los insectos que se la comen (Britannica; Nature Communications 2022).

Jardín tropical: una mimosa con hojas de 4 «dedos» llenos de hojitas y pompones rosas en la mitad
de abajo. Una oruga original (naranja con anillos) llega reptando, se yergue para morder la hoja
más baja y, en la REVELACION, todas las hojitas se cierran en ola, las hojas caen, destello verde
y zoom; la oruga se queda boquiabierta.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.5    # toda la planta se cierra: golpe musical
MUSICA = 5

rng = np.random.default_rng(31)
MOTES = [(rng.uniform(0, W), rng.uniform(1050, 1900), rng.uniform(3, 6.5), rng.uniform(12, 40), rng.uniform(0, 6.28))
         for _ in range(30)]
TUFTS = [(x, 1700 + rng.uniform(-10, 60), rng.uniform(0.8, 1.3), rng.uniform(0, 6.28))
         for x in (40, 150, 260, 420, 700, 820, 960, 1050)]
PEBBLES = [(120, 1860, 30), (880, 1840, 24), (1000, 1890, 36), (640, 1890, 20)]

BASE_X, BASE_Y = 560, 1770
# hojas: (y del nudo, ángulo base, lado: -1 izquierda / +1 derecha, largo pecíolo, largo pinna, retardo de cierre)
LEAVES = [(1600, 186, -1, 110, 175, 0.00),
          (1490, -12, 1, 115, 175, 0.12),
          (1380, 200, -1, 100, 160, 0.24),
          (1280, -30, 1, 95, 150, 0.36),
          (1200, 235, -1, 80, 130, 0.46)]
FLOWERS = [(600, 1150, 34, 0.0), (680, 1395, 30, 1.3), (455, 1290, 28, 2.1)]


def fold_leaf(t, delay):
    """0 = abierta, 1 = cerrada. La hoja tocada (delay 0) empieza antes y se cierra desde la punta."""
    return seg(t, 7.45 + delay, 7.75 + delay * 0.75)


def leaf(t, nx, ny, ang, side, lp, lr, delay):
    f = fold_leaf(t, delay)
    droop = side * 38 * seg(t, 7.5 + delay * 0.6, 8.05)
    sway = 3 * math.sin(t * 1.7 + ny * 0.01)
    a = ang + droop + sway
    g = [f"<g transform='translate({nx},{ny}) rotate({a:.2f})'>",
         f"<line x1='0' y1='0' x2='{lp}' y2='0' stroke='{INK}' stroke-width='15' stroke-linecap='round'/>",
         f"<line x1='0' y1='0' x2='{lp}' y2='0' stroke='#7aa83c' stroke-width='7' stroke-linecap='round'/>"]
    fill = mix("#74d94f", "#3f9a3e", f)
    under = mix("#5cc24a", "#2f7d34", f)
    spreads = [lerp(-40, -9, f), lerp(-13, -3, f), lerp(13, 3, f), lerp(40, 9, f)]
    for k, sp in enumerate(spreads):
        g.append(f"<g transform='translate({lp},0) rotate({sp:.2f})'>")
        g.append(f"<line x1='0' y1='0' x2='{lr}' y2='0' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
        n = 9
        for j in range(n):
            s = lr * (0.16 + 0.84 * j / (n - 1))
            # la hoja tocada se cierra como una ola desde la punta
            if delay == 0:
                fj = seg(t, 7.2 + (n - 1 - j) * 0.04, 7.45 + (n - 1 - j) * 0.04)
            else:
                fj = clamp(f * 1.15 - (n - 1 - j) * 0.015)
            la = lerp(72, 10, fj)
            ln = lerp(25, 21, fj) * (0.75 + 0.25 * math.sin(math.pi * (0.25 + 0.75 * j / (n - 1))))
            wd = lerp(9, 6, fj)
            col = mix("#74d94f", "#3f9a3e", fj)
            for sgn in (-1, 1):
                g.append(f"<g transform='translate({s:.1f},0) rotate({sgn * la:.1f})'>"
                         f"<ellipse cx='{ln:.1f}' cy='0' rx='{ln:.1f}' ry='{wd:.1f}' fill='{col}' stroke='{INK}' stroke-width='4'/></g>")
        g.append(f"<line x1='0' y1='0' x2='{lr}' y2='0' stroke='#4f8f2e' stroke-width='4' stroke-linecap='round'/>")
        g.append("</g>")
    g.append(f"<circle cx='{lp}' cy='0' r='9' fill='#9bbf4a' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<ellipse cx='4' cy='0' rx='12' ry='9' fill='#9bbf4a' stroke='{INK}' stroke-width='4'/>")
    g.append("</g>")
    return "".join(g)


def pompon(x, y, r, t, ph):
    bob = 4 * math.sin(t * 2.2 + ph)
    g = [f"<g transform='translate({x},{y + bob:.1f})'>"]
    n = 26
    for i in range(n):
        a = 2 * math.pi * i / n + ph
        x2, y2 = (r + 20) * math.cos(a), (r + 20) * math.sin(a)
        g.append(f"<line x1='0' y1='0' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    for i in range(n):
        a = 2 * math.pi * i / n + ph
        x2, y2 = (r + 20) * math.cos(a), (r + 20) * math.sin(a)
        g.append(f"<line x1='0' y1='0' x2='{x2:.1f}' y2='{y2:.1f}' stroke='#f07fcf' stroke-width='3.5' stroke-linecap='round'/>"
                 f"<circle cx='{x2:.1f}' cy='{y2:.1f}' r='5' fill='#ffe46b' stroke='{INK}' stroke-width='2.5'/>")
    g.append(f"<circle r='{r}' fill='#f8a5de' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='{-r*0.3:.1f}' cy='{-r*0.3:.1f}' r='{r*0.35:.1f}' fill='#ffd6f2'/>")
    g.append("</g>")
    return "".join(g)


def plant(t):
    sway = 1.4 * math.sin(t * 1.3)
    g = [f"<g transform='rotate({sway:.2f},{BASE_X},{BASE_Y}) translate({BASE_X},{BASE_Y}) scale(1.1) translate({-BASE_X},{-BASE_Y})'>"]
    # tallos de las flores
    for fx, fy, fr, ph in FLOWERS:
        sx, sy = BASE_X, fy + 90
        g.append(f"<path d='M{sx} {sy} Q{(sx + fx) / 2:.0f} {sy - 10} {fx} {fy}' fill='none' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>"
                 f"<path d='M{sx} {sy} Q{(sx + fx) / 2:.0f} {sy - 10} {fx} {fy}' fill='none' stroke='#9c5a3c' stroke-width='5' stroke-linecap='round'/>")
    # tallo principal (rojizo, con pinchitos)
    d = f"M{BASE_X} {BASE_Y} C{BASE_X - 25} 1600 {BASE_X + 30} 1400 {BASE_X} 1170"
    g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>")
    g.append(f"<path d='{d}' fill='none' stroke='#a85a3e' stroke-width='14' stroke-linecap='round'/>")
    for py in range(1230, 1740, 70):
        side = 1 if (py // 70) % 2 else -1
        g.append(f"<path d='M{BASE_X + side * 8} {py} l{side * 14} -10' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    for ny, ang, side, lp, lr, dl in LEAVES:
        g.append(leaf(t, BASE_X + (4 if side > 0 else -4), ny, ang, side, lp, lr, dl))
    for fx, fy, fr, ph in FLOWERS:
        g.append(pompon(fx, fy, fr, t, ph))
    g.append("</g>")
    return "".join(g)


def caterpillar(t):
    """Oruga original: anillos naranjas con rayas, cabeza amarilla, antenas cortas y ojos grandes."""
    hx = lerp(110, 290, seg(t, 0, 4.6))
    moving = t < 4.7
    rear = seg(t, 4.9, 6.4) + 0.12 * seg(t, 6.6, 7.2)          # se yergue para morder
    recoil = seg(t, 7.5, 8.0)
    rear = rear * (1 - 0.15 * recoil)
    hx -= 35 * recoil
    n = 8
    pts = []
    for i in range(n):
        x = hx - i * 48
        hump = 20 * max(0.0, math.sin(t * 9 - i * 0.9)) if moving else 4 * max(0.0, math.sin(t * 3 - i * 0.6))
        lift = 0.0
        if i < 4:
            lift = rear * 175 * ((4 - i) / 4) ** 1.3
        x += rear * (i < 4) * (4 - i) * 6
        pts.append((x, 1740 - hump - lift))
    g = [f"<ellipse cx='{hx - 170:.0f}' cy='1782' rx='230' ry='18' fill='#000' opacity='0.18'/>"]
    for i in range(n - 1, 0, -1):
        x, y = pts[i]
        r = 34 - i * 1.4
        g.append(f"<line x1='{x - 10:.1f}' y1='{y + r - 4:.1f}' x2='{x - 14:.1f}' y2='{y + r + 12:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>"
                 f"<line x1='{x + 10:.1f}' y1='{y + r - 4:.1f}' x2='{x + 14:.1f}' y2='{y + r + 12:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
        g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='#ff9d3a' stroke='{INK}' stroke-width='{LW - 2}'/>")
        g.append(f"<path d='M{x - r * 0.55:.1f} {y - r * 0.6:.1f} Q{x:.1f} {y + r * 0.2:.1f} {x + r * 0.55:.1f} {y - r * 0.6:.1f}' fill='none' stroke='#7b4bd6' stroke-width='7' stroke-linecap='round'/>")
        g.append(f"<circle cx='{x:.1f}' cy='{y + r * 0.45:.1f}' r='6' fill='#ffe16b'/>")
    # cabeza
    x, y = pts[0]
    tilt = lerp(0, -18, rear) + 12 * recoil
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({tilt:.1f})'>")
    ant = 6 * math.sin(t * 5)
    up = 14 * recoil
    for ax in (-16, 16):
        g.append(f"<path d='M{ax} -36 Q{ax * 1.6 + ant:.1f} {-70 - up:.1f} {ax * 1.9 + ant:.1f} {-78 - up:.1f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
                 f"<circle cx='{ax * 1.9 + ant:.1f}' cy='{-80 - up:.1f}' r='8' fill='#7b4bd6' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<circle r='44' fill='#ffcf55' stroke='{INK}' stroke-width='{LW}'/>")
    blink = 0.12 if (t % 2.7) < 0.12 and recoil < 0.1 else 1.0
    er = lerp(13, 19, recoil)
    for ex in (-2, 24):
        g.append(f"<ellipse cx='{ex}' cy='-8' rx='{er:.1f}' ry='{er * 1.2 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        if blink > 0.5:
            px = ex + lerp(4, 1, recoil)
            g.append(f"<circle cx='{px:.1f}' cy='-8' r='{lerp(7, 6, recoil):.1f}' fill='{INK}'/><circle cx='{px - 2:.1f}' cy='-11' r='2.5' fill='#fff'/>")
    g.append("<circle cx='-26' cy='14' r='8' fill='#ff7f8a' opacity='0.7'/><circle cx='36' cy='14' r='8' fill='#ff7f8a' opacity='0.7'/>")
    mouth = rear * (1 - recoil)
    if recoil > 0.05:
        g.append(f"<ellipse cx='14' cy='22' rx='{6 + 4 * recoil:.1f}' ry='{6 + 8 * recoil:.1f}' fill='#8a2c2c' stroke='{INK}' stroke-width='4'/>")
    elif mouth > 0.3:
        g.append(f"<path d='M2 18 Q14 {18 + 18 * mouth:.1f} 30 18 Z' fill='#8a2c2c' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
                 "<rect x='9' y='17' width='7' height='6' fill='#fff'/><rect x='17' y='17' width='7' height='6' fill='#fff'/>")
    else:
        g.append(f"<path d='M4 18 Q14 28 26 18' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append("</g>")
    # rayitas de sorpresa
    if recoil > 0:
        a = seg(t, 7.5, 7.8) * (1 - seg(t, 9.3, 9.9))
        for k, dx, dy in ((0, -40, -100), (1, 0, -115), (2, 40, -100)):
            g.append(f"<line x1='{x + dx * 0.6:.1f}' y1='{y + dy * 0.75:.1f}' x2='{x + dx:.1f}' y2='{y + dy:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round' opacity='{a:.2f}'/>")
    return "".join(g)


def frame(t):
    rv = seg(t, 7.5, 8.1)
    top = mix("#7fd0ff", "#86c9f0", rv); low = mix("#e3f7ff", "#f3ffe0", rv)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<radialGradient id='sun'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.9'/><stop offset='1' stop-color='#fff3b0' stop-opacity='0'/></radialGradient>",
         "<radialGradient id='flash'><stop offset='0' stop-color='#f4ffd0' stop-opacity='0.95'/><stop offset='0.5' stop-color='#b8f26a' stop-opacity='0.5'/><stop offset='1' stop-color='#7ee04a' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>",
         "<circle cx='900' cy='420' r='260' fill='url(#sun)'/>"]
    # nubes tranquilas
    for i, (cx, cy, sc) in enumerate([(250, 520, 1.3), (820, 760, 1.0), (520, 300, 0.9)]):
        dx = (cx + t * 16 * (1 + 0.3 * i)) % 1500 - 250
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})'>"
                 f"<path d='M-110 30 Q-120 -20 -60 -20 Q-40 -70 20 -55 Q60 -90 100 -40 Q150 -40 140 30 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    z = 1 + 0.18 * seg(t, 7.5, 9.2)
    body = []
    # colinas lejanas con selva
    body.append(f"<path d='M0 1230 Q180 1150 360 1210 T720 1190 T1080 1180 L1080 1920 L0 1920 Z' fill='#8fd27a' stroke='{INK}' stroke-width='{LW}'/>")
    for bx, by, br in ((90, 1185, 70), (250, 1170, 55), (840, 1150, 75), (1000, 1160, 60), (640, 1190, 45)):
        body.append(f"<circle cx='{bx}' cy='{by}' r='{br}' fill='#5fb85a' stroke='{INK}' stroke-width='7'/>"
                    f"<circle cx='{bx + br * 0.6:.0f}' cy='{by + 15}' r='{br * 0.7:.0f}' fill='#55ad52' stroke='{INK}' stroke-width='7'/>")
    body.append(f"<path d='M0 1330 Q260 1270 540 1320 T1080 1300 L1080 1920 L0 1920 Z' fill='#76c457' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M0 1700 Q280 1660 560 1690 T1080 1680 L1080 1920 L0 1920 Z' fill='#5fae3f' stroke='{INK}' stroke-width='{LW}'/>")
    # tierra alrededor de la planta
    body.append(f"<ellipse cx='{BASE_X}' cy='1785' rx='150' ry='38' fill='#9a6a43' stroke='{INK}' stroke-width='7'/>")
    for px, py, pr in PEBBLES:
        body.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr}' ry='{pr * 0.6:.0f}' fill='#c9c0b0' stroke='{INK}' stroke-width='6'/>")
    for gx, gy, sc, ph in TUFTS:
        w = 6 * math.sin(t * 2 + ph)
        body.append(f"<g transform='translate({gx},{gy:.0f}) scale({sc:.2f})'>"
                    f"<path d='M-24 10 Q-20 -30 {-30 + w:.1f} -55 M0 10 Q2 -40 {6 + w:.1f} -70 M22 10 Q24 -26 {34 + w:.1f} -48' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
                    f"<path d='M-24 10 Q-20 -30 {-30 + w:.1f} -55 M0 10 Q2 -40 {6 + w:.1f} -70 M22 10 Q24 -26 {34 + w:.1f} -48' fill='none' stroke='#8bd65a' stroke-width='5' stroke-linecap='round'/></g>")
    # destello verde de la revelación
    fl = seg(t, 7.45, 7.75) * (1 - seg(t, 8.0, 9.6))
    if fl > 0.01:
        body.append(f"<circle cx='470' cy='1480' r='{lerp(150, 620, seg(t, 7.45, 8.4)):.0f}' fill='url(#flash)' opacity='{fl:.2f}'/>")
        ring = seg(t, 7.45, 8.2)
        body.append(f"<circle cx='330' cy='1590' r='{lerp(20, 520, ring):.0f}' fill='none' stroke='#ffffff' stroke-width='{lerp(18, 2, ring):.1f}' opacity='{(1 - ring) * 0.9:.2f}'/>")
    body.append(plant(t))
    body.append(caterpillar(t))
    # motitas de luz
    for mx, my, mr, sp, ph in MOTES:
        yy = (my - t * sp - 1050) % 850 + 1050
        a = 0.35 + 0.35 * math.sin(t * 3 + ph)
        body.append(f"<circle cx='{mx + 18 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#fffbd0' opacity='{a:.2f}'/>")
    s.append(zoom(470, 1520, z, "".join(body)))
    s.append("</svg>")
    return "".join(s)
