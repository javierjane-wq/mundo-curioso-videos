"""2026-11-11-c1 · El caballito de mar macho es quien se queda embarazado y da a luz.

0-2,5 s  un caballito de mar entra nadando en un arrecife
2,5-5 s  su bolsa de la barriga se va hinchando (lleva los huevos)
5-7,5 s  tiembla, la bolsa late...
7,45 s   REVELACION: destello y de la bolsa salen cientos de crías diminutas; zoom
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 6

rng = np.random.default_rng(11)
BUBBLES = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(6, 16), rng.uniform(60, 140), rng.uniform(0, 6.28)) for _ in range(34)]
SPECKS = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(60)]
# crías: tiempo de salida, ángulo, velocidad, tamaño, fase
BABIES = []
for i in range(55):
    BABIES.append((REVELACION + rng.uniform(0, 1.5), rng.uniform(-1.3, 1.1), rng.uniform(260, 700),
                   rng.uniform(1.0, 1.6), rng.uniform(0, 6.28)))
WEEDS = [(70, 1.0, "#3fbf6a", 0.0), (190, 0.75, "#2ea85a", 1.3), (900, 0.95, "#3fbf6a", 2.1),
         (1010, 0.7, "#2ea85a", 0.6), (820, 0.55, "#55d27c", 3.0)]
SX, SY, SC = 0, 0, 1.2   # escala del protagonista


def weed(x0, h, col, ph, t):
    pts = []
    n = 9
    for i in range(n + 1):
        k = i / n
        y = 1900 - k * 620 * h
        x = x0 + 38 * k * k * math.sin(t * 1.6 + ph + k * 2.2)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='42' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='{d}' fill='none' stroke='{col}' stroke-width='26' stroke-linecap='round' stroke-linejoin='round'/>")


def coral(x, y, s, col):
    d = ("M0 0 L-8 -60 Q-30 -80 -40 -120 Q-30 -130 -20 -118 Q-10 -90 0 -80 L4 -150 Q14 -160 22 -150 "
         "L20 -90 Q34 -110 46 -140 Q58 -142 58 -128 Q46 -90 24 -50 L20 0 Z")
    return (f"<g transform='translate({x},{y}) scale({s})'><path d='{d}' fill='{col}' stroke='{INK}' "
            f"stroke-width='{LW / s:.1f}' stroke-linejoin='round'/></g>")


BODY = ("M-62 -282 Q-40 -330 6 -322 Q36 -316 44 -284 L148 -270 Q164 -266 164 -250 Q164 -234 148 -232 "
        "L46 -224 Q30 -200 34 -182 Q80 -150 BELLYTOP BELLYMID BELLYLOW Q40 140 28 170 L22 250 "
        "L-30 250 Q-44 170 -64 120 Q-104 40 -104 -60 Q-102 -150 -74 -196 Q-80 -240 -62 -282 Z")


def body_path(p):
    """p = hinchazón de la bolsa (0 normal, 1 muy llena)."""
    bx = lerp(92, 150, p)
    top = f"{lerp(84, 110, p):.0f} -110"
    mid = f"Q{bx + 18:.0f} -10 {bx:.0f} 50"
    low = f"Q{lerp(90, 120, p):.0f} 110 54 116"
    return BODY.replace("BELLYTOP", top).replace("BELLYMID", mid).replace("BELLYLOW", low)


def seahorse(t, x, y, rot, p, blink, fin, shake, pouch_open):
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.2f}) scale({SC})'>"]
    # aleta dorsal (en la espalda, aletea muy rápido)
    g.append(f"<g transform='translate(-98,-10) scale({fin:.3f},1)'>"
             f"<path d='M0 -70 Q-70 -60 -78 0 Q-70 60 0 70 Z' fill='#ffe9a8' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             + "".join(f"<line x1='0' y1='{yy * 0.9:.0f}' x2='-62' y2='{yy * 1.05:.0f}' stroke='#e7a940' stroke-width='5'/>" for yy in (-48, -24, 0, 24, 48))
             + "</g>")
    # cola enroscada
    tail = "M-4 236 C-6 330 70 372 96 318 C116 276 66 250 52 286 C44 306 66 316 74 300"
    g.append(f"<path d='{tail}' fill='none' stroke='{INK}' stroke-width='62' stroke-linecap='round'/>")
    g.append(f"<path d='{tail}' fill='none' stroke='#ffa53a' stroke-width='44' stroke-linecap='round'/>")
    for k, (tx, ty) in enumerate([(-6, 270), (8, 314), (40, 340), (78, 330), (96, 300)]):
        g.append(f"<circle cx='{tx}' cy='{ty}' r='4' fill='#d9771f'/>")
    # cuerpo
    g.append(f"<path d='{body_path(p)}' fill='#ffb547' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # bolsa incubadora (más clara)
    pr = lerp(46, 86, p)
    pcx = lerp(52, 82, p)
    g.append(f"<ellipse cx='{pcx:.0f}' cy='40' rx='{pr:.0f}' ry='{pr * 1.15:.0f}' fill='#ffe08a' stroke='#e89a33' stroke-width='5'/>")
    # huevitos dentro de la bolsa (se transparentan)
    if p > 0.15:
        for i in range(9):
            a = i * 2.4
            rr = (i % 3 + 1) / 3 * pr * 0.6
            ex = pcx + rr * math.cos(a) + 3 * math.sin(t * 6 + i)
            ey = 40 + rr * math.sin(a) * 1.1
            g.append(f"<circle cx='{ex:.0f}' cy='{ey:.0f}' r='{lerp(4, 11, p):.1f}' fill='#ff8a5c' opacity='{min(1, (p - 0.15) * 2):.2f}'/>")
    # abertura de la bolsa
    op = lerp(6, 26, pouch_open)
    g.append(f"<ellipse cx='{pcx + pr * 0.55:.0f}' cy='{40 - pr * 0.75:.0f}' rx='{op:.0f}' ry='{op * 0.55:.0f}' fill='#c2581f' stroke='{INK}' stroke-width='5'/>")
    # anillos del cuerpo
    for yy, w in ((-150, 60), (-90, 80), (-30, 86), (30, 80), (90, 66), (150, 48), (205, 40)):
        cx = -40 if yy < 100 else -14
        g.append(f"<path d='M{cx - w:.0f} {yy} Q{cx:.0f} {yy + 14} {cx + w * 0.4:.0f} {yy - 2}' fill='none' stroke='#d9771f' stroke-width='6' stroke-linecap='round'/>")
    # espinitas de la espalda
    for yy in (-150, -90, -30, 30, 90):
        g.append(f"<path d='M-100 {yy - 8} L-122 {yy} L-100 {yy + 8}' fill='#ffb547' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # corona
    g.append(f"<path d='M-34 -318 L-30 -352 L-14 -324 L0 -360 L12 -322 L28 -344 L28 -312' fill='#ffc861' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # aleta pectoral
    pf = 1 + 0.25 * math.sin(t * 14)
    g.append(f"<g transform='translate(-34,-200) scale({pf:.2f},1)'><path d='M0 0 Q-40 -26 -40 0 Q-40 26 0 0 Z' fill='#ffe9a8' stroke='{INK}' stroke-width='5'/></g>")
    # mejilla y ojo
    g.append(f"<ellipse cx='46' cy='-246' rx='18' ry='11' fill='#ff7b7b' opacity='0.75'/>")
    g.append(f"<circle cx='4' cy='-268' r='30' fill='#fff' stroke='{INK}' stroke-width='6'/>")
    look = 6 + 4 * shake
    g.append(f"<g transform='translate({look:.1f},-268) scale(1,{blink:.2f})'><circle r='17' fill='{INK}'/><circle cx='-6' cy='-7' r='6' fill='#fff'/></g>")
    # párpado preocupado en la tensión
    if shake > 0.05:
        g.append(f"<path d='M-26 -300 Q4 {-306 + 10 * shake:.0f} 34 -296' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # punta del hocico
    g.append(f"<ellipse cx='160' cy='-251' rx='6' ry='14' fill='#e8892b' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def pouch_world(t, x, y, rot, p):
    """Posición en el mundo de la abertura de la bolsa."""
    pr = lerp(46, 86, p); pcx = lerp(52, 82, p)
    lx, ly = (pcx + pr * 0.55) * SC, (40 - pr * 0.75) * SC
    a = math.radians(rot)
    return x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)


def baby(x, y, s, rot, blink):
    d = ("M-6 -30 Q4 -36 10 -28 L30 -26 Q34 -22 30 -18 L10 -16 Q8 -8 14 0 Q22 14 10 26 "
         "Q8 40 22 44 Q30 40 26 34 M10 26 Q-4 30 -6 20 Q-14 4 -14 -8 Q-14 -24 -6 -30 Z")
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({s:.3f})'>"
            f"<path d='{d}' fill='#ffcf6b' stroke='{INK}' stroke-width='5' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<circle cx='0' cy='-22' r='{3.5 * blink:.1f}' fill='{INK}'/></g>")


def frame(t):
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    p = seg(t, 2.4, 5.2) * 0.85 + 0.15 * seg(t, 5.0, 7.3)
    p = p * (1 - 0.75 * seg(t, REVELACION + 0.2, 9.6))
    shake = seg(t, 5.0, 6.0) * (1 - seg(t, REVELACION, REVELACION + 0.4))
    pouch_open = seg(t, REVELACION - 0.3, REVELACION + 0.1) * (1 - 0.6 * seg(t, 9.2, 9.9))
    # nado de entrada y balanceo
    x = lerp(150, 520, seg(t, 0, 2.4)) + 10 * math.sin(t * 1.3)
    y = 1400 + 22 * math.sin(t * 2.2) + shake * 6 * math.sin(t * 45)
    rot = -6 * (1 - seg(t, 0, 2.4)) + 3 * math.sin(t * 1.7) + shake * 2.5 * math.sin(t * 38)
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    if t > REVELACION and t < REVELACION + 0.25:
        blink = 0.12
    fin = 0.55 + 0.45 * abs(math.sin(t * 18))

    top = mix("#1e6fb8", "#38a8e8", rev); mid = mix("#2b8fd0", "#5cc8f0", rev); low = mix("#1b5d9a", "#2f9fd8", rev)
    defs = (f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='flash'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.85 * rev * (1 - 0.5 * seg(t, 8.2, 10)):.3f}'/>"
            f"<stop offset='0.4' stop-color='#ffe48a' stop-opacity='{0.45 * rev:.3f}'/><stop offset='1' stop-color='#ffe48a' stop-opacity='0'/></radialGradient>"
            "<linearGradient id='ray' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='0.28'/>"
            "<stop offset='1' stop-color='#ffffff' stop-opacity='0'/></linearGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sea)'/>"]
    # rayos de luz tranquilos
    for i, rx in enumerate((120, 420, 700, 960)):
        sw = 20 * math.sin(t * 0.7 + i)
        s.append(f"<path d='M{rx - 40 + sw:.0f} 0 L{rx + 60 + sw:.0f} 0 L{rx + 260:.0f} 1500 L{rx + 80:.0f} 1500 Z' fill='url(#ray)' opacity='{0.7 + 0.3 * math.sin(t * 1.1 + i):.2f}'/>")
    for sx, sy, sr, ph in SPECKS:
        yy = (sy - t * 12) % 1900
        s.append(f"<circle cx='{sx + 8 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{sr:.1f}' fill='#e8fbff' opacity='0.35'/>")

    scene = []
    # rocas y arena del fondo
    scene.append(f"<path d='M0 1560 Q180 1500 360 1560 Q520 1610 700 1550 Q900 1490 1080 1560 L1080 1920 L0 1920 Z' fill='{mix('#2a6e8f', '#3d8fb0', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    scene.append(coral(140, 1720, 1.5, "#ff6f91"))
    scene.append(coral(960, 1700, 1.3, "#b07cff"))
    scene.append(coral(800, 1760, 1.0, "#ff9a4d"))
    for wx, wh, wc, wp in WEEDS:
        scene.append(weed(wx, wh, wc, wp, t))
    scene.append(f"<path d='M0 1760 Q240 1710 520 1750 Q800 1790 1080 1740 L1080 1920 L0 1920 Z' fill='#f5d58a' stroke='{INK}' stroke-width='{LW}'/>")
    for px, py, r in ((90, 1840, 12), (330, 1800, 9), (610, 1850, 14), (880, 1820, 10), (1000, 1880, 8)):
        scene.append(f"<ellipse cx='{px}' cy='{py}' rx='{r * 2}' ry='{r}' fill='#e2b866' stroke='{INK}' stroke-width='5'/>")
    # estrella de mar
    scene.append("<g transform='translate(470,1840) rotate(%.1f)'>" % (8 * math.sin(t * 0.8)) +
                 "<path d='M0 -44 L12 -14 L44 -12 L18 8 L28 40 L0 22 L-28 40 L-18 8 L-44 -12 L-12 -14 Z' "
                 f"fill='#ff7a45' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # destello de la revelación detrás del caballito
    ox, oy = pouch_world(t, x, y, rot, p)
    if rev > 0:
        scene.append(f"<circle cx='{ox:.0f}' cy='{oy:.0f}' r='{lerp(120, 620, rev):.0f}' fill='url(#flash)'/>")
    scene.append(seahorse(t, x, y, rot, p, blink, fin, shake, pouch_open))
    # crías saliendo de la bolsa
    for t0, ang, sp, sz, ph in BABIES:
        if t < t0:
            continue
        dt = t - t0
        dist = sp * (1 - math.exp(-dt * 1.6)) / 1.6 * 1.6
        bx = ox + math.cos(ang) * dist + 14 * math.sin(t * 3 + ph)
        by = oy + math.sin(ang) * dist * 0.85 - 30 * dt + 10 * math.cos(t * 2.5 + ph)
        by = max(by, 1010)
        sc = sz * min(1, dt * 4) * 0.95
        bl = 0.2 if ((t + ph) % 2.3) < 0.1 else 1.0
        scene.append(baby(bx, by, sc, 12 * math.sin(t * 4 + ph), bl))
    # burbujas
    for bx, by, br, sp, ph in BUBBLES:
        yy = (by - t * sp) % 1950
        if yy < 980:
            continue
        scene.append(f"<circle cx='{bx + 12 * math.sin(t * 2 + ph):.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='#cdf3ff' fill-opacity='0.35' stroke='#e8fbff' stroke-width='3'/>")
    # burbujitas que suelta por el hocico
    for k in range(4):
        bt = (t * 0.9 + k * 0.25) % 1.0
        hx = x + 170 * SC + 20 * bt
        hy = y - 260 * SC - 140 * bt
        scene.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{6 + 8 * bt:.1f}' fill='none' stroke='#e8fbff' stroke-width='4' opacity='{1 - bt:.2f}'/>")

    z = 1 + 0.16 * seg(t, REVELACION, 9.8)
    s.append(zoom(ox, oy, z, "".join(scene)))
    s.append("</svg>")
    return "".join(s)
