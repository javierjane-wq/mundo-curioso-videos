"""El búho gira la cabeza hasta 270 grados: sus ojos son tubulares y no se mueven (National Geographic, Johns Hopkins 2013).

0-2,5 s  un búho entra volando de noche y se posa en una rama
2,5-5 s  mira a un lado y a otro (sus ojos no se mueven: gira la cabeza)
5-7,5 s  empieza a girar la cabeza por detrás… y sigue
7,5 s    REVELACIÓN: llega a 270° (tres cuartos de vuelta); la luna se enciende, halo y zoom
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.5   # la cabeza llega a 270°: golpe musical
MUSICA = 7

rng = np.random.default_rng(23)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1150), rng.uniform(2.5, 6), rng.uniform(0, 6.28)) for _ in range(75)]
FLIES = [(rng.uniform(40, W - 40), rng.uniform(1150, 1880), rng.uniform(5, 8), rng.uniform(0, 6.28)) for _ in range(18)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(260, 420), rng.uniform(5, 10), rng.uniform(0, 6.28)) for _ in range(24)]
LEAVES = [(170, 1745, -30), (300, 1770, 25), (760, 1735, -20), (880, 1760, 35), (980, 1725, -10)]

PLUMA = "#b06a36"; PLUMA_OSC = "#8a4f26"; PECHO = "#f2d6a2"; DISCO = "#f6e5c4"
HX, HY, R = 540, 1265, 158    # cabeza (sobre el cuerpo posado)


def angulo(t):
    """Ángulo de la cabeza en grados (positivo = gira hacia la derecha de la pantalla)."""
    a = 4 * math.sin(t * 2.1)
    a += -35 * (seg(t, 2.7, 3.3) - seg(t, 3.6, 4.2)) + 35 * (seg(t, 3.6, 4.2) - seg(t, 4.4, 4.9))
    a += 270 * seg(t, 5.0, 7.5)
    return a


def ala(lado, flap, fold):
    """Ala: abierta y batiendo al volar, plegada sobre el cuerpo al posarse."""
    s = 1 if lado > 0 else -1
    ang = lerp(-70 + 55 * flap, 12, fold) * s
    cx = lerp(150, 130, fold) * s
    return (f"<g transform='translate({cx:.1f},-40) rotate({ang:.1f})'>"
            f"<path d='M0 -30 Q{95*s} -10 {80*s} 150 Q{40*s} 230 {-10*s} 200 Q{-30*s} 60 0 -30 Z' "
            f"fill='{PLUMA_OSC}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            + "".join(f"<path d='M{(-5 + 18*k)*s} {120 + 22*k} q{12*s} 22 {26*s} 18' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>" for k in range(3))
            + "</g>")


def cabeza(t, rev):
    a = math.radians(angulo(t))
    blink = 0.12 if ((t + 1.2) % 2.7) < 0.14 else 1.0
    g = [f"<g transform='translate({HX},{HY})'>"]
    # penachos (orejas) detrás de la cabeza
    for d in (-0.72, 0.72):
        ph = a + d
        x = 0.72 * R * math.sin(ph)
        g.append(f"<path d='M{x - 38:.1f} {-R*0.62:.1f} L{x + (18 if d > 0 else -18):.1f} {-R - 62:.1f} "
                 f"L{x + 40:.1f} {-R*0.55:.1f} Z' fill='{PLUMA_OSC}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cabeza
    g.append(f"<circle r='{R}' fill='{PLUMA}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<clipPath id='hc'><circle r='{R - LW/2}'/></clipPath><g clip-path='url(#hc)'>")
    # nuca: plumas en V cuando mira hacia atrás
    b = a + math.pi
    cb = math.cos(b)
    if cb > 0:
        xb = 0.8 * R * math.sin(b)
        for k, yy in enumerate((-70, -20, 30, 80)):
            for dx in (-45, 0, 45):
                xx = xb + dx * cb
                g.append(f"<path d='M{xx - 16*cb:.1f} {yy} L{xx:.1f} {yy + 16} L{xx + 16*cb:.1f} {yy}' fill='none' "
                         f"stroke='{PLUMA_OSC}' stroke-width='7' stroke-linecap='round' opacity='{min(1, cb*1.6):.2f}'/>")
    # disco facial y ojos
    for d in (-0.45, 0.45):
        ph = a + d
        c = math.cos(ph)
        if c > 0.02:
            x = 0.86 * R * math.sin(ph)
            g.append(f"<ellipse cx='{x:.1f}' cy='-8' rx='{76*c:.1f}' ry='86' fill='{DISCO}' stroke='{mix(PLUMA_OSC, PLUMA, 0.3)}' stroke-width='6'/>")
    for d in (-0.45, 0.45):
        ph = a + d
        c = math.cos(ph)
        if c > 0.02:
            x = 0.86 * R * math.sin(ph)
            iris = mix("#ffb21f", "#ffd84a", rev)
            g.append(f"<g transform='translate({x:.1f},-12) scale({c:.3f},{blink})'>"
                     f"<circle r='50' fill='{iris}' stroke='{INK}' stroke-width='{LW}'/>"
                     f"<circle r='27' fill='{INK}'/><circle cx='-10' cy='-11' r='10' fill='#fff'/>"
                     f"<circle cx='11' cy='10' r='4.5' fill='#fff'/></g>")
            if blink < 0.5:
                g.append(f"<path d='M{x - 48*c:.1f} -12 Q{x:.1f} 2 {x + 48*c:.1f} -12' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # pico
    c = math.cos(a)
    if c > -0.05:
        x = 0.95 * R * math.sin(a)
        hw = 17 * max(c, 0.25)
        tip = x + 22 * math.sin(a)
        g.append(f"<path d='M{x - hw:.1f} 40 L{x + hw:.1f} 40 L{tip:.1f} 86 Z' fill='#f0a63a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append("</g></g>")
    return "".join(g)


def anillo(t, rev, delante):
    """Flecha que rodea la cabeza en horizontal y muestra cuánto ha girado."""
    a = angulo(t) - 4 * math.sin(t * 2.1)
    k = seg(t, 5.0, 5.3)
    if a < 6 or k <= 0:
        return ""
    rx, ry, cy = 250, 66, HY + 55
    pts = []
    n = 60
    for i in range(n + 1):
        ps = math.radians(a) * i / n
        if (math.cos(ps) > 0) == delante:
            pts.append((HX + rx * math.sin(ps), cy + ry * math.cos(ps)))
        else:
            pts.append(None)
    col = mix("#ffe066", "#fff3a8", rev)
    out, run = [], []
    for p in pts + [None]:
        if p is None:
            if len(run) > 1:
                d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in run)
                out.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{24 + 6*rev:.0f}' stroke-linecap='round' stroke-linejoin='round' opacity='{k:.2f}'/>")
                out.append(f"<path d='{d}' fill='none' stroke='{col}' stroke-width='{12 + 6*rev:.0f}' stroke-linecap='round' stroke-linejoin='round' opacity='{k:.2f}'/>")
            run = []
        else:
            run.append(p)
    # punta de flecha al final del recorrido
    ps = math.radians(a)
    if (math.cos(ps) > 0) == delante:
        x, y = HX + rx * math.sin(ps), cy + ry * math.cos(ps)
        dx, dy = rx * math.cos(ps), -ry * math.sin(ps)
        L = math.hypot(dx, dy) or 1; dx, dy = dx / L, dy / L
        s = 34 + 8 * rev
        p1 = (x + dx * s, y + dy * s); p2 = (x - dy * s * 0.75, y + dx * s * 0.75); p3 = (x + dy * s * 0.75, y - dx * s * 0.75)
        out.append(f"<path d='M{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} L{p3[0]:.1f} {p3[1]:.1f} Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round' opacity='{k:.2f}'/>")
    return "".join(out)


def buho(t, rev):
    land = seg(t, 0, 1.7)
    x = lerp(880, HX, land)
    fold = seg(t, 1.5, 2.2)
    flap = math.sin(t * 16)
    breathe = 1 + 0.015 * math.sin(t * 3)
    bob = -25 * math.sin(math.pi * seg(t, 1.6, 2.1))   # pequeño botecito al posarse
    g = [f"<g transform='translate({x - HX:.1f},{(lerp(-200, 0, land) + bob):.1f})'>"]
    g.append(anillo(t, rev, False))
    g.append(f"<g transform='translate({HX},1520) scale({breathe:.4f},1)'>")
    g.append(ala(-1, flap, fold)); g.append(ala(1, flap, fold))
    g.append(f"<ellipse rx='178' ry='215' fill='{PLUMA}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cy='30' rx='122' ry='165' fill='{PECHO}'/>")
    for yy, xs in ((-60, (-50, 0, 50)), (0, (-75, -25, 25, 75)), (60, (-60, -10, 40)), (120, (-35, 15))):
        for xx in xs:
            g.append(f"<path d='M{xx - 13} {yy} L{xx} {yy + 13} L{xx + 13} {yy}' fill='none' stroke='{PLUMA}' stroke-width='6' stroke-linecap='round'/>")
    # patas con garras agarradas a la rama
    for fx in (-55, 55):
        g.append(f"<g transform='translate({fx},{lerp(250, 205, fold):.0f})'>"
                 + "".join(f"<path d='M{dx} 0 q{dx*0.2} 20 {dx*0.6} 32' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
                           f"<path d='M{dx} 0 q{dx*0.2} 20 {dx*0.6} 32' fill='none' stroke='#f0a63a' stroke-width='8' stroke-linecap='round'/>" for dx in (-22, 0, 22))
                 + "</g>")
    g.append("</g>")
    g.append(cabeza(t, rev))
    g.append(anillo(t, rev, True))
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.3, 8.1)
    top = mix("#141a4a", "#1f3f8f", rev); mid = mix("#2b2f78", "#3f6cc2", rev); low = mix("#4a3a8c", "#6b8fd8", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='moon'><stop offset='0' stop-color='#fff8d8' stop-opacity='{0.55 + 0.4*rev:.2f}'/>"
            f"<stop offset='1' stop-color='#fff2b0' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff3b0' stop-opacity='{0.85*rev:.2f}'/>"
            f"<stop offset='0.5' stop-color='#ffd447' stop-opacity='{0.45*rev:.2f}'/><stop offset='1' stop-color='#ffb000' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='fly'><stop offset='0' stop-color='#fffbb0'/><stop offset='1' stop-color='#d7ff5a' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, 7.3, 10)
    s.append(f"<g transform='translate({HX},{HY}) scale({z:.4f}) translate({-HX},{-HY})'>")
    for sx, sy, sr, ph in STARS:
        a = 0.5 + 0.5 * math.sin(t * 3 + ph)
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr * (1 + 0.3*rev):.1f}' fill='#fff' opacity='{0.35 + 0.6*a:.2f}'/>")
    # luna creciente
    mx, my = 935, 330
    mr = 95 + 12 * rev
    s.append(f"<circle cx='{mx}' cy='{my}' r='{mr*3.2:.0f}' fill='url(#moon)'/>")
    s.append(f"<circle cx='{mx}' cy='{my}' r='{mr:.0f}' fill='{mix('#fff1b8', '#fffbe6', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for cx, cy, cr in ((-30, -20, 18), (25, 30, 12), (35, -35, 9)):
        s.append(f"<circle cx='{mx + cx}' cy='{my + cy}' r='{cr}' fill='#ecd893'/>")
    # nubecillas que pasan
    for i, (cx, cy, sc) in enumerate(((150, 700, 1.1), (700, 860, 0.9))):
        dx = (t * 18 * (1 + 0.4 * i)) % 1500 - 300
        s.append(f"<g transform='translate({cx + dx - 300:.0f},{cy}) scale({sc})' opacity='0.85'>"
                 f"<path d='M0 40 Q20 -10 80 5 Q110 -40 170 0 Q230 -15 250 40 Z' fill='{mix('#5a5fa8', '#9ab4ea', rev)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # bosque lejano (siluetas de abetos)
    for layer, (base, col, sc, off) in enumerate(((1250, mix('#232a63', '#34539a', rev), 1.0, 0), (1360, mix('#1b2150', '#2a4280', rev), 1.25, 60))):
        trees = []
        x = -60 + off
        while x < W + 120:
            hgt = 230 * sc * (0.8 + 0.3 * math.sin(x * 0.03 + layer))
            trees.append(f"M{x - 70*sc:.0f} {base + 40} L{x:.0f} {base - hgt:.0f} L{x + 70*sc:.0f} {base + 40} Z")
            x += 115 * sc
        s.append(f"<path d='{' '.join(trees)}' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        s.append(f"<rect x='0' y='{base + 30}' width='{W}' height='{H - base}' fill='{col}'/>")
    # suelo del bosque
    s.append(f"<path d='M0 1800 Q300 1760 560 1790 T1080 1780 L1080 1920 L0 1920 Z' fill='{mix('#1e3b3a', '#2f5d55', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    # tronco y rama
    s.append(f"<path d='M-20 1100 L130 1100 L150 1920 L-20 1920 Z' fill='#5b3a24' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M40 1300 Q20 1500 60 1700' fill='none' stroke='#4a2e1b' stroke-width='8' stroke-linecap='round'/>")
    s.append(f"<path d='M120 1700 Q500 1690 1100 1735 L1100 1790 Q500 1760 130 1785 Z' fill='#7a4e2e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M300 1735 Q500 1728 700 1745' fill='none' stroke='#5b3a24' stroke-width='6' stroke-linecap='round'/>")
    for lx, ly, la in LEAVES:
        sw = 8 * math.sin(t * 2.4 + lx)
        s.append(f"<g transform='translate({lx},{ly}) rotate({la + sw:.1f})'><path d='M0 0 Q30 -40 0 -80 Q-30 -40 0 0 Z' fill='#4fae5a' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M0 -5 L0 -70' stroke='#2f7a3b' stroke-width='4'/></g>")
    # halo de la revelación
    if rev > 0:
        s.append(f"<circle cx='{HX}' cy='{HY}' r='{lerp(200, 470, rev):.0f}' fill='url(#halo)'/>")
    s.append(buho(t, rev))
    # chispas de la revelación
    if rev > 0:
        for ang, dist, rr, ph in SPARK:
            d = dist * (0.6 + 0.4 * rev) + 15 * math.sin(t * 4 + ph)
            x, y = HX + d * math.cos(ang + t * 0.4), HY + d * math.sin(ang + t * 0.4) * 0.9
            s.append(f"<path d='M{x:.0f} {y - rr*2:.0f} L{x + rr*0.6:.0f} {y:.0f} L{x:.0f} {y + rr*2:.0f} L{x - rr*0.6:.0f} {y:.0f} Z' fill='#fff6b8' opacity='{rev * (0.6 + 0.4*math.sin(t*6+ph)):.2f}'/>")
    # luciérnagas
    for fx, fy, fr, ph in FLIES:
        x = fx + 30 * math.sin(t * 0.9 + ph); y = fy + 20 * math.cos(t * 1.3 + ph)
        a = 0.5 + 0.5 * math.sin(t * 4 + ph)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{fr*3:.0f}' fill='url(#fly)' opacity='{a:.2f}'/>")
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{fr*0.6:.1f}' fill='#fffbd0' opacity='{0.4 + 0.6*a:.2f}'/>")
    s.append("</g>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
