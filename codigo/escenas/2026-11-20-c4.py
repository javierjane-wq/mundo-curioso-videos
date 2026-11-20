"""2026-11-20-c4 · Historia: en los años 1830 el ketchup se vendía como medicina (y hasta en pastillas de tomate).

Un bote de ketchup original con cara llega dando saltitos a la encimera y le echa un chorro a un plato
de patatas fritas, con un tomate amigo al lado. El reloj de la pared gira hacia atrás y la cocina se
vuelve de color sepia (viaje al pasado): el tapón se convierte en corcho, la etiqueta en un pergamino
y una cuchara de jarabe se acerca. En la REVELACION estalla un halo dorado, el bote crece, la cámara
se acerca y salen disparadas pastillas rojas de tomate que rebotan por la encimera.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 7.2    # halo dorado + pastillas + zoom: golpe musical
MUSICA = 4

rng = np.random.default_rng(1830)
MOTAS = [(rng.uniform(40, W - 40), rng.uniform(150, 1400), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(30)]
PASTILLAS = [(rng.uniform(-1, 1), rng.uniform(0.7, 1.25), rng.uniform(0, 0.35), rng.uniform(-180, 180)) for _ in range(14)]
CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(260, 420), rng.uniform(0, 1)) for _ in range(18)]

BX, BASE = 560, 1470     # centro y base del bote
MESA = 1470              # altura de la encimera


def sep(c, k):
    """Color hacia sepia (viaje al pasado)."""
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    y = 0.3 * r + 0.59 * g + 0.11 * b
    s = "#%02x%02x%02x" % (int(min(255, y * 1.07 + 30)), int(min(255, y * 0.9 + 18)), int(min(255, y * 0.68)))
    return mix(c, s, k * 0.75)


def estrella(x, y, r, col, op):
    p = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        p.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return f"<polygon points='{' '.join(p)}' fill='{col}' opacity='{op:.2f}' stroke='{INK}' stroke-width='4'/>"


def pastilla(x, y, rot, k):
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"
            f"<ellipse cx='0' cy='0' rx='34' ry='30' fill='{sep('#e8322b', k)}' stroke='{INK}' stroke-width='6'/>"
            f"<line x1='-22' y1='0' x2='22' y2='0' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
            f"<ellipse cx='-12' cy='-13' rx='9' ry='5' fill='#fff' opacity='0.75'/></g>")


def bote(t, k):
    """Bote de ketchup de cristal: cuerpo ancho, hombros, cuello estrecho, tapón (que pasa a corcho)."""
    # cae desde arriba con rebote (visible desde el fotograma 0)
    x = BX
    if t < 0.55:
        salto = 280 * (1 - (t / 0.55) ** 2)
    elif t < 1.0:
        salto = 70 * math.sin(math.pi * (t - 0.55) / 0.45)
    else:
        salto = 0
    # inclinación para echar ketchup (1,1-2,1 s) y bamboleo nervioso en la tensión
    incl = -28 * (seg(t, 1.1, 1.4) - seg(t, 1.9, 2.2))
    incl += 4 * math.sin(t * 13) * (seg(t, 4.8, 5.3) - seg(t, 7.0, 7.3))
    incl += 3 * math.sin(t * 3)
    esc = 1 + 0.14 * seg(t, REVELACION, REVELACION + 0.5) + 0.05 * rebote(t, REVELACION, 0.6) * (t < REVELACION + 0.6)
    resp = 1 + 0.012 * math.sin(t * 4)
    rojo = sep("#d8261e", k * 0.6); rojo2 = sep("#a5140f", k * 0.6)
    g = [f"<g transform='translate({x:.1f},{BASE - salto:.1f}) rotate({incl:.1f}) scale({esc * resp:.4f},{esc / resp:.4f})'>"]
    g.append("<ellipse cx='0' cy='4' rx='150' ry='18' fill='#000' opacity='0.2'/>")
    cuerpo = ("M-120 0 Q-128 -60 -126 -200 Q-124 -250 -86 -290 Q-50 -325 -46 -360 L-44 -410 "
              "L44 -410 L46 -360 Q50 -325 86 -290 Q124 -250 126 -200 Q128 -60 120 0 Z")
    g.append(f"<path d='{cuerpo}' fill='{rojo}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-96 -30 Q-104 -120 -100 -220' fill='none' stroke='{rojo2}' stroke-width='16' stroke-linecap='round' opacity='0.6'/>")
    g.append(f"<path d='M86 -40 Q96 -130 92 -215' fill='none' stroke='#ffffff' stroke-width='12' stroke-linecap='round' opacity='0.35'/>")
    g.append(f"<path d='M-30 -395 L-30 -330' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='0.4'/>")
    # tapón moderno (blanco) -> corcho
    tapa = seg(t, 4.7, 5.4)
    if tapa < 1:
        g.append(f"<g opacity='{1 - tapa:.2f}'><rect x='-54' y='-462' width='108' height='60' rx='14' fill='#f4f1ea' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<line x1='-40' y1='-440' x2='40' y2='-440' stroke='#c9c3b6' stroke-width='6'/></g>")
    if tapa > 0:
        g.append(f"<g opacity='{tapa:.2f}'><path d='M-40 -404 L-48 -470 Q0 -484 48 -470 L40 -404 Z' fill='#c58a52' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 + "".join(f"<circle cx='{cx}' cy='{cy}' r='5' fill='#8a5a30'/>" for cx, cy in ((-20, -448), (14, -432), (24, -458), (-8, -420)))
                 + "</g>")
    # etiqueta: blanca moderna -> pergamino con lazo
    lab = sep(mix("#fbf6ea", "#efd9a6", tapa), k * 0.3)
    g.append(f"<rect x='-112' y='-250' width='224' height='190' rx='26' fill='{lab}' stroke='{INK}' stroke-width='7'/>")
    if tapa > 0:
        g.append(f"<path d='M-112 -82 L-140 -60 L-112 -60 Z M112 -82 L140 -60 L112 -60 Z' fill='#7a3d1c' stroke='{INK}' stroke-width='5' opacity='{tapa:.2f}'/>"
                 f"<rect x='-112' y='-88' width='224' height='26' fill='#b3542a' stroke='{INK}' stroke-width='5' opacity='{tapa:.2f}'/>")
    # cara sobre la etiqueta
    rev = seg(t, REVELACION, REVELACION + 0.3)
    blink = 0.12 if ((t + 0.4) % 2.9) < 0.13 else 1.0
    sorpresa = seg(t, 4.6, 5.2)
    mira = lerp(0, 10, seg(t, 4.8, 5.4)) - lerp(0, 10, rev)
    for ex in (-48, 48):
        ry = (30 + 6 * sorpresa + 6 * rev) * blink
        g.append(f"<ellipse cx='{ex}' cy='-180' rx='27' ry='{ry:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            pr = 15 - 4 * sorpresa + 4 * rev
            g.append(f"<circle cx='{ex + mira:.1f}' cy='-176' r='{pr:.1f}' fill='{INK}'/>"
                     f"<circle cx='{ex + mira - 5:.1f}' cy='-183' r='6' fill='#fff'/>")
    g.append(f"<ellipse cx='-80' cy='-130' rx='16' ry='9' fill='#ff8f8a' opacity='0.7'/><ellipse cx='80' cy='-130' rx='16' ry='9' fill='#ff8f8a' opacity='0.7'/>")
    if t < 4.6 or rev > 0:
        boca = 22 + 18 * rev
        g.append(f"<path d='M-30 -132 Q0 {-132 + boca:.1f} 30 -132 Z' fill='#8b1f1a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='-118' rx='14' ry='{12 + 3 * math.sin(t * 8):.1f}' fill='#8b1f1a' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def patatas(t, k):
    x, y = 215, MESA - 4
    g = [f"<ellipse cx='{x}' cy='{y}' rx='165' ry='34' fill='{sep('#ffffff', k)}' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, (dx, h, a) in enumerate(((-90, 150, -14), (-55, 175, -6), (-20, 160, 4), (15, 185, -3), (50, 150, 10), (85, 140, 18), (-5, 120, 0))):
        g.append(f"<rect x='{x + dx - 16}' y='{y - h}' width='32' height='{h + 10}' rx='6' fill='{sep('#ffcf3f', k)}' stroke='{INK}' stroke-width='6' transform='rotate({a} {x + dx} {y})'/>")
    g.append(f"<path d='M{x - 150} {y - 6} Q{x} {y + 55} {x + 150} {y - 6} Q{x} {y + 40} {x - 150} {y - 6} Z' fill='{sep('#e9e4dc', k)}' stroke='{INK}' stroke-width='6'/>")
    # chorro de ketchup encima
    c = seg(t, 1.35, 2.0)
    if c > 0:
        g.append(f"<path d='M{x - 70} {y - 140} Q{x - 30} {y - 175} {x + 10} {y - 150} Q{x + 50} {y - 175} {x + 75} {y - 135} Q{x + 20} {y - 110} {x - 70} {y - 140} Z' "
                 f"fill='{sep('#c81e17', k * 0.6)}' stroke='{INK}' stroke-width='6' transform='translate({x} {y - 145}) scale({c:.3f}) translate({-x} {-(y - 145)})'/>")
    chorro = seg(t, 1.3, 1.45) - seg(t, 1.85, 2.0)
    if chorro > 0.02:
        g.append(f"<path d='M362 1092 Q300 1080 {x + 10} {y - 160}' fill='none' stroke='{INK}' stroke-width='28' stroke-linecap='round' opacity='{chorro:.2f}'/>"
                 f"<path d='M362 1092 Q300 1080 {x + 10} {y - 160}' fill='none' stroke='#d8261e' stroke-width='16' stroke-linecap='round' opacity='{chorro:.2f}'/>")
    return "".join(g)


def tomate(t, k):
    salta = abs(math.sin(t * 3.2)) * 30
    x, y = 905, MESA - 90 - salta
    sq = 1 + 0.06 * math.sin(t * 6.4)
    rev = seg(t, REVELACION, REVELACION + 0.3)
    blink = 0.12 if ((t + 1.3) % 3.3) < 0.13 else 1.0
    g = [f"<ellipse cx='905' cy='{MESA + 2}' rx='{80 - salta * 0.6:.1f}' ry='14' fill='#000' opacity='0.2'/>",
         f"<g transform='translate({x:.1f},{y:.1f}) scale({sq:.3f},{1 / sq:.3f})'>",
         f"<path d='M0 -82 Q60 -92 88 -40 Q108 10 80 52 Q44 92 0 90 Q-44 92 -80 52 Q-108 10 -88 -40 Q-60 -92 0 -82 Z' fill='{sep('#ef3b2c', k * 0.6)}' stroke='{INK}' stroke-width='{LW}'/>",
         "<ellipse cx='-44' cy='-36' rx='18' ry='11' fill='#fff' opacity='0.55'/>",
         f"<path d='M0 -80 L-34 -104 L-12 -86 L-20 -116 L0 -92 L20 -116 L12 -86 L34 -104 Z' fill='{sep('#3fae4a', k)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>",
         f"<path d='M0 -96 Q4 -124 16 -132' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>"]
    for ex in (-30, 30):
        g.append(f"<ellipse cx='{ex}' cy='0' rx='17' ry='{(21 + 5 * rev) * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex - 5}' cy='2' r='9' fill='{INK}'/><circle cx='{ex - 8}' cy='-3' r='3.5' fill='#fff'/>")
    g.append(f"<path d='M-18 34 Q0 {50 + 12 * rev:.1f} 18 34' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def reloj(t, k):
    x, y = 880, 1105
    atras = seg(t, 2.3, 4.6)
    min_a = 360 * 3 * (t / 10) - 360 * 9 * atras
    hor_a = 60 + min_a / 12
    g = [f"<g transform='translate({x},{y}) rotate({2 * math.sin(t * 2):.1f})'>",
         f"<circle r='86' fill='{sep('#a5683a', k)}' stroke='{INK}' stroke-width='{LW}'/>",
         f"<circle r='66' fill='{sep('#fff8e6', k)}' stroke='{INK}' stroke-width='6'/>"]
    for i in range(12):
        a = i * math.pi / 6
        g.append(f"<circle cx='{52 * math.cos(a):.1f}' cy='{52 * math.sin(a):.1f}' r='4.5' fill='{INK}'/>")
    g.append(f"<line x1='0' y1='0' x2='0' y2='-30' stroke='{INK}' stroke-width='9' stroke-linecap='round' transform='rotate({hor_a:.1f})'/>")
    g.append(f"<line x1='0' y1='0' x2='0' y2='-50' stroke='#c0392b' stroke-width='6' stroke-linecap='round' transform='rotate({min_a:.1f})'/>")
    g.append(f"<circle r='8' fill='{INK}'/></g>")
    # flechitas curvas de "hacia atrás" mientras gira
    op = seg(t, 2.3, 2.6) * (1 - seg(t, 4.4, 4.8))
    if op > 0.02:
        g.append(f"<g transform='translate({x},{y}) rotate({-t * 160:.1f})' opacity='{op:.2f}'>"
                 f"<path d='M0 -112 A112 112 0 0 0 -97 -56' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round'/>"
                 f"<path d='M-112 -40 L-97 -56 L-78 -44' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='M0 112 A112 112 0 0 0 97 56' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round'/>"
                 f"<path d='M112 40 L97 56 L78 44' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round' stroke-linejoin='round'/></g>")
    return "".join(g)


def estante(t, k):
    """Estante con tarros de botica que aparecen al viajar al pasado."""
    a = seg(t, 3.8, 4.8)
    g = [f"<rect x='40' y='1210' width='420' height='26' rx='6' fill='{sep('#9a5b30', k)}' stroke='{INK}' stroke-width='7'/>"]
    tarros = [(95, 92, '#5d8fbf'), (190, 118, '#7fae5a'), (290, 100, '#c9893b'), (385, 84, '#8f6bb3')]
    for i, (tx, h, c) in enumerate(tarros):
        s = rebote(t, 3.9 + i * 0.18, 0.5)
        if s <= 0: continue
        g.append(f"<g transform='translate({tx},1212) scale({s:.3f})'>"
                 f"<rect x='-34' y='{-h}' width='68' height='{h}' rx='14' fill='{sep(c, k * 0.5)}' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='-40' y='{-h - 20}' width='80' height='22' rx='6' fill='{sep('#6b4a2e', k * 0.5)}' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='-22' y='{-h * 0.65:.0f}' width='44' height='{h * 0.35:.0f}' rx='5' fill='#f3e3bd' stroke='{INK}' stroke-width='4'/></g>")
    return "".join(g) if a > 0 else g[0]


def cuchara(t, k):
    e = seg(t, 5.0, 6.0) - seg(t, 7.0, 7.4)
    if e <= 0.01: return ""
    x = lerp(1250, 790, e); y = 1205 + 10 * math.sin(t * 5)
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate(-8)'>"
            f"<rect x='40' y='-14' width='300' height='28' rx='14' fill='{sep('#cfd6de', k * 0.5)}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<ellipse cx='0' cy='0' rx='62' ry='38' fill='{sep('#cfd6de', k * 0.5)}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<ellipse cx='0' cy='2' rx='44' ry='22' fill='{sep('#c81e17', k * 0.5)}'/>"
            f"<ellipse cx='-14' cy='-6' rx='12' ry='6' fill='#fff' opacity='0.6'/></g>")


def frame(t):
    k = seg(t, 2.5, 4.6)                       # 0 = hoy, 1 = años 1830 (sepia)
    rev = seg(t, REVELACION, REVELACION + 0.5)
    pared1 = mix(sep("#ffe7a8", k), "#ffd56b", rev * 0.5); pared2 = mix(sep("#ffd27a", k), "#ffb84a", rev * 0.5)
    s = ["<defs>",
         f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{sep('#bfe7ff', k)}'/><stop offset='0.42' stop-color='{pared1}'/><stop offset='1' stop-color='{pared2}'/></linearGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95 * rev:.3f}'/><stop offset='0.4' stop-color='#ffd84a' stop-opacity='{0.75 * rev:.3f}'/><stop offset='1' stop-color='#ff9f1a' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # rayas suaves del papel pintado (fondo tranquilo)
    for i in range(0, W + 120, 120):
        s.append(f"<rect x='{i}' y='0' width='44' height='{MESA}' fill='#ffffff' opacity='{0.10 + 0.04 * k:.2f}'/>")
    # motas de polvo flotando
    for mx, my, mr, ph in MOTAS:
        yy = (my - t * 22) % 1400 + 60
        s.append(f"<circle cx='{mx + 14 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#fff' opacity='{0.25 + 0.2 * k:.2f}'/>")
    z = 1 + 0.16 * seg(t, REVELACION, REVELACION + 1.4)
    esc = []
    # halo y rayos
    if rev > 0:
        esc.append(f"<g transform='translate({BX},{BASE - 230}) rotate({t * 25:.1f})' opacity='{0.5 * rev:.2f}'>"
                   + "".join(f"<path d='M0 0 L{560 * math.cos(a - 0.09):.0f} {560 * math.sin(a - 0.09):.0f} L{560 * math.cos(a + 0.09):.0f} {560 * math.sin(a + 0.09):.0f} Z' fill='#fff4b8'/>"
                             for a in [i * math.pi / 7 for i in range(14)]) + "</g>")
        esc.append(f"<circle cx='{BX}' cy='{BASE - 230}' r='{lerp(150, 560, rev):.0f}' fill='url(#halo)'/>")
    esc.append(reloj(t, k))
    esc.append(estante(t, k))
    # encimera de madera
    esc.append(f"<rect x='-40' y='{MESA}' width='{W + 80}' height='{H - MESA + 40}' fill='{sep('#c9814a', k)}' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(f"<rect x='-40' y='{MESA}' width='{W + 80}' height='40' fill='{sep('#e39a5c', k)}' stroke='{INK}' stroke-width='{LW}'/>")
    for yy in (1580, 1690, 1800):
        esc.append(f"<path d='M-20 {yy} Q300 {yy - 14} 560 {yy} T1100 {yy}' fill='none' stroke='{sep('#a9643a', k)}' stroke-width='7'/>")
    esc.append(patatas(t, k))
    esc.append(tomate(t, k))
    esc.append(cuchara(t, k))
    esc.append(bote(t, k))
    # pastillas que salen disparadas y rebotan
    if t >= REVELACION:
        for dx, v, dl, r0 in PASTILLAS:
            tt = t - REVELACION - dl * 0.6
            if tt < 0: continue
            vx = dx * 520; vy = -1250 * v
            px = BX + vx * tt
            py = BASE - 300 + vy * tt + 2200 * tt * tt
            suelo = MESA + 30 + 120 * abs(dx)
            if py > suelo:
                py = suelo - abs(math.sin(tt * 7)) * 60 * math.exp(-tt * 2)
            esc.append(pastilla(px, py, r0 + tt * 260 * dx, 0))
        for a, r, ph in CHISPAS:
            op = rev * (0.5 + 0.5 * math.sin(t * 7 + ph * 6.28))
            esc.append(estrella(BX + r * math.cos(a + t * 0.3), BASE - 230 + r * 0.9 * math.sin(a + t * 0.3), 16, '#fff6a8', op))
    s.append(zoom(BX, BASE - 220, z, "".join(esc)))
    return ("<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d' viewBox='0 0 %d %d'>" % (W, H, W, H)) + "".join(s) + "</svg>"
