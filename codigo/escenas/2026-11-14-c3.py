"""2026-11-14-c3 · La miel de las tumbas egipcias, intacta tras miles de años.

Tumba egipcia iluminada por antorchas. Un tarro de barro con miel (personaje original con cara)
está cubierto de polvo y telarañas; un reloj de arena marca el paso del tiempo. El tarro tiembla,
la tapa salta y la miel dorada brilla intacta (REVELACION), con chispas, goteo y una abeja.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.5
MUSICA = 7

rng = np.random.default_rng(14)
DUST = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.28)) for _ in range(45)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(260, 620), rng.uniform(8, 18), rng.uniform(0.6, 1.4)) for _ in range(26)]
BLOCKS = []
for row, y in enumerate(range(0, 1700, 150)):
    off = 0 if row % 2 == 0 else 135
    for x in range(-270 + off, W + 270, 270):
        BLOCKS.append((x, y))

PX, PY = 540, 1450   # centro del tarro


def fondo(t, luz, oro):
    s = []
    wall = mix("#c98d4e", "#e6ad5a", luz)
    wall = mix(wall, "#f2c46a", 0.35 * oro)
    s.append(f"<rect width='{W}' height='{H}' fill='{wall}'/>")
    # bloques de piedra
    for x, y in BLOCKS:
        s.append(f"<rect x='{x}' y='{y}' width='270' height='150' fill='none' stroke='{mix('#8a5a2e', '#a8703a', luz)}' stroke-width='5' opacity='0.55'/>")
    # cenefas decorativas (franjas de colores, sin escritura)
    for yb in (330, 760):
        s.append(f"<rect x='0' y='{yb}' width='{W}' height='70' fill='#1f6f8b' stroke='{INK}' stroke-width='6'/>")
        for i in range(12):
            cx = 45 + i * 90
            col = ("#e9b23c", "#c9463d", "#f4ead2")[i % 3]
            s.append(f"<path d='M{cx-30} {yb+60} L{cx} {yb+10} L{cx+30} {yb+60} Z' fill='{col}' stroke='{INK}' stroke-width='4'/>")
        s.append(f"<rect x='0' y='{yb+70}' width='{W}' height='18' fill='#c9463d' stroke='{INK}' stroke-width='5'/>")
    # puerta / nicho al fondo
    s.append(f"<path d='M300 1650 L300 1080 Q540 960 780 1080 L780 1650 Z' fill='{mix('#5a3418', '#7a4a22', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M340 1650 L340 1100 Q540 1005 740 1100 L740 1650 Z' fill='{mix('#3a200e', '#56321a', luz)}' opacity='0.9'/>")
    # suelo
    s.append(f"<rect x='0' y='1650' width='{W}' height='270' fill='{mix('#9a6434', '#b87a40', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(0, W, 180):
        s.append(f"<line x1='{x}' y1='1650' x2='{x - 60}' y2='1920' stroke='#7a4c24' stroke-width='5' opacity='0.6'/>")
    return "".join(s)


def antorcha(x, y, t, fase):
    f = 1 + 0.12 * math.sin(t * 13 + fase) + 0.06 * math.sin(t * 29 + fase)
    sw = 6 * math.sin(t * 7 + fase)
    g = [f"<circle cx='{x}' cy='{y-70}' r='{150*f:.0f}' fill='url(#torchglow)'/>",
         f"<path d='M{x-28} {y-20} L{x+28} {y-20} L{x+12} {y+120} L{x-12} {y+120} Z' fill='#7a4a22' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>",
         f"<rect x='{x-36}' y='{y-38}' width='72' height='26' rx='6' fill='#c9a24a' stroke='{INK}' stroke-width='6'/>",
         f"<g transform='translate({x},{y-40}) scale({f:.3f},{f:.3f})'>"
         f"<path d='M-30 0 Q-38 -50 {sw:.1f} -110 Q38 -50 30 0 Z' fill='#ff8a2a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
         f"<path d='M-15 0 Q-18 -30 {sw*0.6:.1f} -66 Q18 -30 15 0 Z' fill='#ffe066'/></g>"]
    return "".join(g)


def reloj(t):
    """Reloj de arena sobre el suelo: la arena cae y en 3,6 s se le da la vuelta."""
    x, y = 875, 1640
    flip = seg(t, 3.4, 4.1)
    rot = 180 * flip
    lift = -40 * math.sin(math.pi * flip)
    # arena: antes del giro baja de arriba a abajo; después vuelve a empezar
    if t < 3.4:
        k = clamp(0.35 + t / 3.4 * 0.6)
    else:
        k = clamp((t - 4.1) / 6.0)
    top = 1 - k
    g = [f"<ellipse cx='{x}' cy='{y+8}' rx='95' ry='16' fill='#000' opacity='0.22'/>",
         f"<g transform='translate({x},{y - 110 + lift:.1f}) rotate({rot:.1f})'>"]
    # arena dentro (antes de girar, la ampolla "de arriba" es la superior)
    if t >= 3.4 and t < 4.1:
        top, bot = 0.0, 1.0
    else:
        bot = k
    sand = "#f2c15a"
    g.append(f"<path d='M-62 -98 L62 -98 L8 -4 L-8 -4 Z' fill='#dff3ff' opacity='0.55'/>")
    g.append(f"<path d='M-62 98 L62 98 L8 4 L-8 4 Z' fill='#dff3ff' opacity='0.55'/>")
    if top > 0.02:
        hy = -4 - 88 * top
        hw = lerp(8, 62, (hy + 4) / -94)
        g.append(f"<path d='M{-hw:.1f} {hy:.1f} L{hw:.1f} {hy:.1f} L8 -4 L-8 -4 Z' fill='{sand}'/>")
    if bot > 0.02:
        g.append(f"<path d='M-58 96 Q0 {96 - 80*bot:.1f} 58 96 Z' fill='{sand}'/>")
    if 0.03 < top and not (3.4 <= t < 4.1):
        g.append(f"<line x1='0' y1='-4' x2='0' y2='94' stroke='{sand}' stroke-width='5'/>")
    g.append(f"<path d='M-62 -98 L62 -98 L8 -4 L8 4 L62 98 L-62 98 L-8 4 L-8 -4 Z' fill='none' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<rect x='-82' y='-122' width='164' height='26' rx='8' fill='#8a5228' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='-82' y='96' width='164' height='26' rx='8' fill='#8a5228' stroke='{INK}' stroke-width='7'/>")
    for sx in (-70, 70):
        g.append(f"<rect x='{sx-7}' y='-98' width='14' height='196' fill='#a8683a' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def tarro(t, rev):
    """Tarro de barro con miel. Tiembla antes de la revelación; la tapa sale volando."""
    temblor = seg(t, 5.0, 7.4) * (1 - rev)
    sx = 7 * temblor * math.sin(t * 55)
    despierta = math.exp(-((t - 1.4) / 0.35) ** 2)      # sacude el polvo al despertar
    sx += 10 * despierta * math.sin(t * 40)
    squash = 1 + 0.06 * math.sin(math.pi * clamp((t - REVELACION) / 0.5)) if t > REVELACION else 1
    polvo = 1 - seg(t, REVELACION, REVELACION + 0.5)
    blink = 0.12 if ((t + 1.0) % 2.9) < 0.13 or abs(t - 1.2) < 0.08 else 1.0
    clay = mix("#b5652f", "#d97a35", rev)
    g = [f"<ellipse cx='{PX}' cy='{1690}' rx='250' ry='30' fill='#000' opacity='0.25'/>",
         f"<g transform='translate({PX + sx:.1f},{1680}) scale({1/squash:.3f},{squash:.3f}) translate({-PX},{-1680})'>"]
    body = (f"M{PX-110} 1250 Q{PX-120} 1300 {PX-190} 1350 Q{PX-250} 1430 {PX-215} 1550 "
            f"Q{PX-185} 1650 {PX-120} 1680 L{PX+120} 1680 Q{PX+185} 1650 {PX+215} 1550 "
            f"Q{PX+250} 1430 {PX+190} 1350 Q{PX+120} 1300 {PX+110} 1250 Z")
    g.append(f"<path d='{body}' fill='{clay}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brillo y banda decorativa
    g.append(f"<path d='M{PX-170} 1400 Q{PX-200} 1470 {PX-175} 1560' fill='none' stroke='#f3b27a' stroke-width='16' stroke-linecap='round' opacity='{0.5 + 0.4*rev:.2f}'/>")
    g.append(f"<path d='M{PX-226} 1520 Q{PX} 1560 {PX+226} 1520' fill='none' stroke='#1f6f8b' stroke-width='18'/>")
    g.append(f"<path d='M{PX-226} 1520 Q{PX} 1560 {PX+226} 1520' fill='none' stroke='{INK}' stroke-width='4' transform='translate(0,-11)'/>")
    g.append(f"<path d='M{PX-224} 1540 Q{PX} 1580 {PX+224} 1540' fill='none' stroke='{INK}' stroke-width='4'/>")
    # boca del tarro y miel
    g.append(f"<ellipse cx='{PX}' cy='1250' rx='118' ry='26' fill='{mix('#c07a2a', '#ffb81c', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    if rev > 0:
        g.append(f"<ellipse cx='{PX}' cy='1252' rx='92' ry='15' fill='#ffd84a' opacity='{rev:.2f}'/>")
        # goteo de miel por el borde
        for dx, d0, ln in ((-80, 0.0, 90), (35, 0.25, 140), (95, 0.45, 70)):
            k = seg(t, REVELACION + 0.2 + d0, REVELACION + 1.6 + d0)
            if k > 0:
                yy = 1262 + ln * k
                xx = PX + dx * (1 + 0.25 * k)
                g.append(f"<path d='M{xx-14:.0f} 1258 L{xx-14:.0f} {yy:.0f} Q{xx:.0f} {yy+26:.0f} {xx+14:.0f} {yy:.0f} L{xx+14:.0f} 1258 Z' "
                         f"fill='#ffb81c' stroke='{INK}' stroke-width='5'/>")
    # cara
    for ex in (-70, 70):
        g.append(f"<ellipse cx='{PX+ex}' cy='1420' rx='34' ry='{40*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            look = 6 * math.sin(t * 1.3)
            g.append(f"<circle cx='{PX+ex+look:.1f}' cy='1426' r='18' fill='{INK}'/>")
            g.append(f"<circle cx='{PX+ex+look-6:.1f}' cy='1418' r='6' fill='#fff'/>")
    for ex in (-110, 110):
        g.append(f"<ellipse cx='{PX+ex}' cy='1478' rx='26' ry='14' fill='#ff8f80' opacity='0.7'/>")
    boca = lerp(14, 46, rev) + 10 * temblor
    if rev > 0.3:
        g.append(f"<path d='M{PX-45} 1470 Q{PX} {1470 + boca:.0f} {PX+45} 1470 Z' fill='#7a1f1f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M{PX-38} 1474 Q{PX} {1474 + boca:.0f} {PX+38} 1474' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # polvo y telarañas (desaparecen en la revelación)
    if polvo > 0.01:
        g.append(f"<path d='{body}' fill='#8f8577' opacity='{0.42*polvo:.2f}'/>")
        sway = 4 * math.sin(t * 2.2)
        g.append(f"<g opacity='{polvo:.2f}' stroke='#f4f0e6' stroke-width='3' fill='none'>"
                 f"<path d='M{PX+120} 1255 L{PX+235} {1340+sway:.1f} M{PX+120} 1255 L{PX+205} {1420+sway:.1f} M{PX+120} 1255 L{PX+160} {1440+sway:.1f}'/>"
                 f"<path d='M{PX+160} {1300+sway*0.5:.1f} Q{PX+185} {1320:.0f} {PX+205} {1330+sway*0.7:.1f} M{PX+145} {1350+sway*0.6:.1f} Q{PX+175} 1370 {PX+215} {1385+sway:.1f}'/></g>")
    g.append("</g>")
    return "".join(g)


def tapa(t, rev):
    """Tapa de barro: tiembla y en la revelación sale volando girando hacia arriba."""
    temblor = seg(t, 5.0, 7.4)
    k = seg(t, REVELACION - 0.1, REVELACION + 0.9)
    y = 1225 - 16 * temblor * abs(math.sin(t * 24)) * (1 - k) - 260 * k + 90 * seg(t, REVELACION + 1.2, 10) * 0
    x = PX - 300 * k
    rot = 25 * math.sin(t * 24) * temblor * (1 - k) - 200 * k
    if k >= 1:
        # la tapa cae y queda apoyada en el suelo a la derecha
        q = seg(t, REVELACION + 0.9, REVELACION + 1.45)
        y = lerp(965, 1640, q)
        rot = -200 - 160 * q
        x = PX - 300 + 50 * q
    col = "#a85a28"
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"
            f"<path d='M-128 10 Q-120 -46 0 -54 Q120 -46 128 10 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<rect x='-134' y='4' width='268' height='22' rx='10' fill='#8f4a20' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='0' cy='-62' r='22' fill='#c06a30' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-70 -30 Q-40 -44 -10 -46' stroke='#e39a62' stroke-width='9' fill='none' stroke-linecap='round'/></g>")


def abeja(t):
    k = seg(t, REVELACION + 0.4, REVELACION + 1.8)
    if k <= 0:
        return ""
    x = lerp(-80, 330, k) + 30 * math.sin(t * 4)
    y = lerp(1180, 1120, k) + 25 * math.sin(t * 6.5)
    ala = 0.55 + 0.45 * abs(math.sin(t * 60))
    return (f"<g transform='translate({x:.1f},{y:.1f})'>"
            f"<ellipse cx='-8' cy='-38' rx='22' ry='{30*ala:.1f}' fill='#e8f7ff' stroke='{INK}' stroke-width='5' opacity='0.9' transform='rotate(-20 -8 -38)'/>"
            f"<ellipse cx='16' cy='-36' rx='20' ry='{26*ala:.1f}' fill='#e8f7ff' stroke='{INK}' stroke-width='5' opacity='0.9' transform='rotate(20 16 -36)'/>"
            f"<ellipse cx='0' cy='0' rx='48' ry='34' fill='#ffcf26' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-14 -32 Q-20 0 -14 32 M10 -33 Q4 0 10 33' stroke='{INK}' stroke-width='11' fill='none'/>"
            f"<path d='M-48 0 L-64 4 L-48 9' fill='{INK}'/>"
            f"<circle cx='44' cy='-6' r='24' fill='#2a1a14'/>"
            f"<circle cx='50' cy='-12' r='9' fill='#fff'/><circle cx='52' cy='-12' r='4' fill='{INK}'/>"
            f"<path d='M50 -28 Q58 -52 70 -54 M40 -28 Q40 -52 50 -58' stroke='{INK}' stroke-width='4' fill='none'/></g>")


def frame(t):
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.3)
    luz = seg(t, 0, 1.5) * 0.6 + 0.4 * rev
    oro = rev
    defs = ("<radialGradient id='torchglow'><stop offset='0' stop-color='#ffd27a' stop-opacity='0.55'/>"
            "<stop offset='1' stop-color='#ff9a3a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='honeyglow'><stop offset='0' stop-color='#fff6c2' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.35' stop-color='#ffd23f' stop-opacity='{0.8*rev:.3f}'/>"
            f"<stop offset='1' stop-color='#ff9f1c' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='beam'><stop offset='0' stop-color='#fff3c8' stop-opacity='0.35'/>"
            "<stop offset='1' stop-color='#fff3c8' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='vig'><stop offset='0.45' stop-color='#000' stop-opacity='0'/>"
            "<stop offset='1' stop-color='#1a0a02' stop-opacity='0.55'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>"]
    # cámara: se aleja al principio y acerca en la revelación
    z = lerp(1.18, 1.0, seg(t, 0, 2.6)) + 0.16 * seg(t, REVELACION, 10)
    c = [fondo(t, luz, oro)]
    c.append(antorcha(120, 1130, t, 0.0))
    c.append(antorcha(960, 1130, t, 2.1))
    # haz de la linterna del explorador que barre la tumba al inicio
    bx = lerp(150, PX, seg(t, 0, 2.2))
    c.append(f"<ellipse cx='{bx:.0f}' cy='1450' rx='{lerp(240, 380, seg(t, 0, 2.2)):.0f}' ry='330' fill='url(#beam)'/>")
    # resplandor dorado de la miel
    if rev > 0:
        pr = lerp(150, 760, rev) * (1 + 0.04 * pulso(t, 0.8))
        c.append(f"<circle cx='{PX}' cy='1260' r='{pr:.0f}' fill='url(#honeyglow)'/>")
        for i in range(12):
            a = i * 30 + t * 18
            l = lerp(120, 520, rev)
            x2 = PX + l * math.cos(math.radians(a)); y2 = 1260 + l * math.sin(math.radians(a)) * 0.8
            c.append(f"<path d='M{PX} 1260 L{x2:.0f} {y2:.0f}' stroke='#fff2a8' stroke-width='{lerp(4, 26, rev):.0f}' opacity='{0.35*rev:.2f}' stroke-linecap='round'/>")
    c.append(reloj(t))
    c.append(tarro(t, rev))
    c.append(tapa(t, rev))
    # rayitos de luz que escapan bajo la tapa durante la tensión
    ten = seg(t, 5.4, 7.4) * (1 - rev)
    if ten > 0.01:
        for i, a in enumerate((-160, -130, -50, -20)):
            l = 70 + 40 * ten + 10 * math.sin(t * 20 + i)
            x2 = PX + (130 + l) * math.cos(math.radians(a)); y2 = 1240 + (40 + l) * math.sin(math.radians(a))
            c.append(f"<path d='M{PX + 120*math.cos(math.radians(a)):.0f} {1245 + 20*math.sin(math.radians(a)):.0f} L{x2:.0f} {y2:.0f}' stroke='#ffe066' stroke-width='12' stroke-linecap='round' opacity='{ten:.2f}'/>")
    # nube de polvo que sale al sacudirse y al abrirse
    for k0, amp in ((1.4, 0.8), (REVELACION, 1.2)):
        k = clamp((t - k0) / 1.1)
        if 0 < k < 1:
            for i in range(9):
                a = math.radians(i * 40 + 10)
                r = (290 + 200 * k) * amp
                c.append(f"<circle cx='{PX + r*math.cos(a):.0f}' cy='{1460 + r*0.75*math.sin(a):.0f}' r='{(30 + 30*k)*amp:.0f}' fill='#e8dcc0' opacity='{0.4*(1-k):.2f}'/>")
    # chispas doradas
    if rev > 0:
        for a, rr, sz, sp in SPARK:
            k = ((t - REVELACION) * sp * 0.6) % 1
            r = rr * (0.4 + k)
            x = PX + r * math.cos(a); y = 1260 + r * 0.75 * math.sin(a) - 80 * k
            sc = sz * (1 - k) * rev
            if sc > 1:
                c.append(f"<path d='M{x:.0f} {y-sc*2:.0f} L{x+sc*0.6:.0f} {y-sc*0.6:.0f} L{x+sc*2:.0f} {y:.0f} L{x+sc*0.6:.0f} {y+sc*0.6:.0f} L{x:.0f} {y+sc*2:.0f} L{x-sc*0.6:.0f} {y+sc*0.6:.0f} L{x-sc*2:.0f} {y:.0f} L{x-sc*0.6:.0f} {y-sc*0.6:.0f} Z' fill='#fff7c0' stroke='#ffb81c' stroke-width='3'/>")
    c.append(abeja(t))
    # motas de polvo flotando
    for px, py, pr, sp, ph in DUST:
        yy = (py - t * sp) % 900 + 1000
        c.append(f"<circle cx='{px + 18*math.sin(t*0.8 + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='{mix('#f2dcb0', '#fff2a8', rev)}' opacity='0.5'/>")
    s.append(zoom(PX, 1380, z, "".join(c)))
    s.append(f"<rect width='{W}' height='{H}' fill='url(#vig)' opacity='{1 - 0.6*rev:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
