"""2026-11-10-c2 · La Estatua de la Libertad (inaugurada en 1886) era del color del cobre brillante;
el aire y la lluvia oxidaron su piel de cobre y en unos años la cubrieron de una pátina verde que la protege.

0-2,5 s  la cámara se aleja desde la estatua recién estrenada, color cobre, en su isla; entra un remolcador.
2,5-5 s  brilla como una moneda nueva: destellos que recorren el cobre; gaviotas y olas.
5-7,5 s  pasan los años: días y noches a toda velocidad, nubes de lluvia y manchas verdes que aparecen.
7,5-10 s REVELACION: destello, cielo despejado con rayos de sol y zoom: la estatua es VERDE; abre mucho los ojos.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 5

rng = np.random.default_rng(1886)
RAIN = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.8, 1.3)) for _ in range(90)]
SPARK = [(rng.uniform(250, 830), rng.uniform(950, 1600), rng.uniform(0, 6.28)) for _ in range(16)]
CLOUDS = [(150, 560, 1.1), (760, 760, 0.9), (420, 930, 0.7)]
GULLS = [(0, 1080, 1.0, 0.0), (300, 1150, 0.8, 0.4), (-250, 1010, 0.65, 0.8)]
BLOTCH = [(505, 1470, 16), (575, 1540, 20), (490, 1590, 14), (600, 1400, 13), (540, 1360, 15),
          (470, 1180, 10), (520, 1620, 15), (612, 1600, 12), (548, 1460, 11)]

COBRE = ("#d9773f", "#f2a066", "#a8522a")    # base, luz, sombra
VERDE = ("#5fbf9f", "#97dcc4", "#3f927a")


def nube(x, y, sc, col, op=0.95):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 60 Q-10 10 50 15 Q70 -35 130 -10 Q170 -40 215 0 Q275 0 270 60 Z' fill='{col}' "
            f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def gaviota(x, y, sc, t, fase):
    a = 22 * math.sin(t * 9 + fase * 6)
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})'>"
            f"<path d='M-46 {-a*0.6:.1f} Q-22 {-a:.1f} 0 6 Q22 {-a:.1f} 46 {-a*0.6:.1f}' fill='none' stroke='{INK}' "
            f"stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M-46 {-a*0.6:.1f} Q-22 {-a:.1f} 0 6 Q22 {-a:.1f} 46 {-a*0.6:.1f}' fill='none' stroke='#ffffff' "
            f"stroke-width='4' stroke-linecap='round'/></g>")


def remolcador(t):
    x = lerp(-220, 230, seg(t, 0, 6.5)) + 18 * t
    y = 1752 + 5 * math.sin(t * 3)
    g = [f"<g transform='translate({x:.0f},{y:.0f}) rotate({2*math.sin(t*2.5):.1f})'>"]
    for i in range(3):
        k = ((t * 0.9 + i / 3) % 1)
        g.append(f"<circle cx='{20 - 30*k:.0f}' cy='{-70 - 90*k:.0f}' r='{10 + 18*k:.0f}' fill='#eef2f5' "
                 f"stroke='{INK}' stroke-width='4' opacity='{0.9*(1-k):.2f}'/>")
    g.append(f"<rect x='5' y='-72' width='26' height='34' rx='4' fill='#e5484d' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-40' y='-44' width='70' height='28' rx='6' fill='#fff6e0' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-80 -18 L90 -18 L70 14 L-66 14 Z' fill='#2f6db5' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<circle cx='-20' cy='-30' r='6' fill='#5ec8ff' stroke='{INK}' stroke-width='3'/>")
    g.append("</g>")
    return "".join(g)


def estatua(t, k):
    """Estatua: túnica, brazo con antorcha, corona de 7 rayos y tablilla. k = 0 cobre, 1 verde."""
    base, luz, som = (mix(a, b, k) for a, b in zip(COBRE, VERDE))
    blink = 0.12 if (t % 2.9) < 0.12 else 1.0
    wow = seg(t, REVELACION, REVELACION + 0.4)
    eye = 1 + 0.35 * wow
    g = []
    # brazo con antorcha (detrás de la cabeza)
    g.append(f"<path d='M470 1300 L503 1296 L478 1078 L446 1080 Z' fill='{base}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M482 1290 L462 1090' stroke='{luz}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<rect x='450' y='1026' width='22' height='60' rx='6' fill='{som}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='462' cy='1078' r='19' fill='{base}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M424 1008 L500 1008 L486 1032 L438 1032 Z' fill='{base}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    fl = 1 + 0.08 * math.sin(t * 13)
    g.append(f"<g transform='translate(462,1006) scale({fl:.3f},{2-fl:.3f})'>"
             f"<path d='M-30 0 Q-36 -40 -6 -66 Q-4 -40 8 -48 Q12 -70 4 -90 Q40 -60 32 -20 Q30 -6 30 0 Z' fill='#ffc93c' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M-14 -2 Q-16 -28 2 -42 Q6 -24 16 -28 Q20 -10 14 -2 Z' fill='#fff1a8'/></g>")
    # túnica
    g.append(f"<path d='M468 1272 Q452 1460 444 1642 L636 1642 Q628 1460 612 1272 Q540 1252 468 1272 Z' fill='{base}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M478 1300 Q468 1470 462 1638' fill='none' stroke='{luz}' stroke-width='12' stroke-linecap='round'/>")
    for fx, c in ((505, 8), (540, 10), (578, 8), (606, 6)):
        g.append(f"<path d='M{fx} 1440 Q{fx - c} 1540 {fx + 3} 1640' fill='none' stroke='{som}' stroke-width='6' stroke-linecap='round'/>")
    # manto cruzado
    g.append(f"<path d='M600 1276 Q560 1360 470 1440 Q500 1470 520 1468 Q590 1390 616 1300 Z' fill='{luz}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # pie asomando
    g.append(f"<path d='M560 1642 Q566 1624 590 1626 Q606 1630 606 1642 Z' fill='{luz}' stroke='{INK}' stroke-width='6'/>")
    # tablilla y brazo izquierdo
    g.append(f"<g transform='translate(626,1372) rotate(-14)'><rect x='-30' y='-66' width='60' height='132' rx='6' fill='{luz}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<line x1='-18' y1='-40' x2='18' y2='-40' stroke='{som}' stroke-width='5'/></g>")
    g.append(f"<path d='M598 1282 Q636 1316 640 1380 L612 1392 Q606 1330 582 1300 Z' fill='{base}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<circle cx='626' cy='1392' r='15' fill='{base}' stroke='{INK}' stroke-width='6'/>")
    # cuello y cabeza
    g.append(f"<rect x='527' y='1232' width='28' height='44' rx='8' fill='{som}' stroke='{INK}' stroke-width='7'/>")
    # corona: 7 rayos
    for i in range(7):
        a = math.radians(-160 + i * (140 / 6))
        cx, cy = 541, 1196
        x1, y1 = cx + 40 * math.cos(a - 0.12), cy + 40 * math.sin(a - 0.12)
        x2, y2 = cx + 40 * math.cos(a + 0.12), cy + 40 * math.sin(a + 0.12)
        xt, yt = cx + 98 * math.cos(a), cy + 98 * math.sin(a)
        g.append(f"<path d='M{x1:.1f} {y1:.1f} L{xt:.1f} {yt:.1f} L{x2:.1f} {y2:.1f} Z' fill='{luz}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<circle cx='541' cy='1206' r='40' fill='{base}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M501 1188 Q541 1158 581 1188 L578 1172 Q541 1146 504 1172 Z' fill='{luz}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cara
    for ex in (527, 556):
        g.append(f"<g transform='translate({ex},1208) scale({eye:.2f},{eye*blink:.2f})'><ellipse rx='8' ry='10' fill='#fff' stroke='{INK}' stroke-width='3'/>"
                 f"<circle cx='1' cy='1' r='5' fill='{INK}'/><circle cx='3' cy='-2' r='2' fill='#fff'/></g>")
    if wow > 0.5:
        g.append(f"<ellipse cx='541' cy='1230' rx='6' ry='8' fill='{INK}'/>")
    else:
        g.append(f"<path d='M531 1227 Q541 1235 551 1227' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    g.append(f"<circle cx='516' cy='1222' r='6' fill='#ff8a7a' opacity='0.45'/><circle cx='567' cy='1222' r='6' fill='#ff8a7a' opacity='0.45'/>")
    # manchas de pátina que aparecen mientras pasan los años
    mk = seg(t, 5.2, 7.2) * (1 - seg(t, REVELACION, REVELACION + 0.3))
    if mk > 0.01:
        for i, (bx, by, br) in enumerate(BLOTCH):
            o = clamp(mk * 1.6 - i * 0.08)
            if o > 0.01:
                g.append(f"<ellipse cx='{bx}' cy='{by}' rx='{br*1.3:.0f}' ry='{br:.0f}' fill='{VERDE[0]}' opacity='{o:.2f}'/>")
    # destello de cobre nuevo que recorre la estatua
    sh = seg(t, 2.4, 3.6) if t < 4 else seg(t, 3.9, 5.0)
    if 0 < sh < 1 and k < 0.3:
        y0 = lerp(1000, 1700, sh)
        g.append(f"<path d='M420 {y0:.0f} L660 {y0-120:.0f} L660 {y0-80:.0f} L420 {y0+40:.0f} Z' fill='#fff' opacity='0.45'/>")
    return "".join(g)


def pedestal():
    g = []
    g.append(f"<path d='M230 1900 L320 1842 L760 1842 L850 1900 Z' fill='#8fcf6a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M300 1872 L380 1820 L700 1820 L780 1872 Z' fill='#c9b48a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='406' y='1784' width='268' height='40' rx='6' fill='#e3d2a8' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='438' y='1668' width='204' height='120' fill='#e9dab4' stroke='{INK}' stroke-width='{LW}'/>")
    for wx in (468, 540, 612):
        g.append(f"<rect x='{wx-16}' y='1700' width='32' height='58' rx='14' fill='#bfa77a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='424' y='1640' width='232' height='32' rx='6' fill='#f3e6c4' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(g)


def frame(t):
    k = 0.22 * seg(t, 5.2, 7.2) + 0.78 * seg(t, REVELACION, REVELACION + 0.35)
    # días y noches a toda velocidad entre 5 y 7,4 s
    ciclo = seg(t, 5.0, 5.4) * (1 - seg(t, 7.0, 7.4))
    noche = ciclo * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 5.0) * 1.6))
    lluvia = seg(t, 5.3, 5.8) * (1 - seg(t, 7.1, 7.45))
    gris = 0.55 * lluvia
    top = mix(mix("#4fb6f0", "#1b2350", noche), "#6c7a8c", gris)
    low = mix(mix("#bfe8ff", "#3a3f78", noche), "#a9b4c0", gris)
    sea1 = mix(mix("#2f8fd8", "#1a2a5c", noche), "#4f6e86", gris)
    rev = seg(t, REVELACION, REVELACION + 0.5)
    flash = clamp(1 - (t - REVELACION) / 0.6) if t >= REVELACION else 0
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920' viewBox='0 0 1080 1920'><defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff8d0' stop-opacity='{0.9*rev:.2f}'/><stop offset='1' stop-color='#fff8d0' stop-opacity='0'/></radialGradient>",
         "</defs>", "<rect width='1080' height='1920' fill='url(#sky)'/>"]
    # Sol y Luna cruzando el cielo cuando pasan los años
    if ciclo > 0.01:
        ph = ((t - 5.0) * 1.6) % 1
        sx = lerp(-80, 1160, ph)
        s.append(f"<circle cx='{sx:.0f}' cy='{420 + 180*abs(ph-0.5)*2:.0f}' r='60' fill='#ffe066' stroke='{INK}' stroke-width='7' opacity='{ciclo*(1-noche):.2f}'/>")
        mx = lerp(-80, 1160, (ph + 0.5) % 1)
        s.append(f"<circle cx='{mx:.0f}' cy='520' r='46' fill='#f4f1e6' stroke='{INK}' stroke-width='7' opacity='{ciclo*noche:.2f}'/>")
    z = lerp(1.28, 1.0, seg(t, 0, 2.3)) * (1 + 0.13 * seg(t, REVELACION, 10))
    cy = lerp(1380, 1330, seg(t, REVELACION, 10))
    c = []
    # rayos de sol tras la estatua en la revelación
    if rev > 0.01:
        rot = t * 12
        rays = "".join(f"<path d='M0 0 L{900*math.cos(math.radians(a+rot-4)):.0f} {900*math.sin(math.radians(a+rot-4)):.0f} "
                       f"L{900*math.cos(math.radians(a+rot+4)):.0f} {900*math.sin(math.radians(a+rot+4)):.0f} Z' fill='#fff6c8'/>" for a in range(0, 360, 24))
        c.append(f"<g transform='translate(541,1250)' opacity='{0.35*rev:.2f}'>{rays}</g>")
        c.append(f"<circle cx='541' cy='1300' r='520' fill='url(#glow)'/>")
    # nubes
    for i, (nx, ny, sc) in enumerate(CLOUDS):
        dx = (nx + t * (16 + 8 * i)) % 1380 - 300
        c.append(nube(dx, ny, sc, mix("#ffffff", "#8e98a6", gris + 0.4 * noche)))
    # horizonte: ciudad lejana y mar
    sky_line = mix("#8fb4d6", "#2c3566", noche)
    c.append(f"<path d='M0 1700 L0 1640 L60 1640 L60 1600 L110 1600 L110 1650 L170 1650 L170 1580 L200 1560 L230 1580 L230 1660 "
             f"L300 1660 L300 1700 Z' fill='{sky_line}' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    c.append(f"<path d='M780 1700 L780 1650 L840 1650 L840 1590 L880 1590 L880 1630 L940 1630 L940 1560 L975 1540 L1010 1560 "
             f"L1010 1640 L1080 1640 L1080 1700 Z' fill='{sky_line}' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    c.append(f"<rect x='-20' y='1698' width='1120' height='260' fill='{sea1}' stroke='{INK}' stroke-width='{LW}'/>")
    for row, yy in enumerate((1740, 1800, 1860, 1905)):
        off = (t * (40 + 15 * row)) % 160
        for wx in range(-160, 1240, 160):
            c.append(f"<path d='M{wx+off:.0f} {yy} q20 -14 40 0 q20 14 40 0' fill='none' stroke='{mix('#bfe6ff', '#6b78a8', noche)}' stroke-width='6' stroke-linecap='round'/>")
    c.append(remolcador(t))
    c.append("<g transform='translate(0,40)'>" + pedestal()
             + "<g transform='translate(540,1642) scale(1.15) translate(-540,-1642)'>" + estatua(t, k) + "</g></g>")
    # destellos de cobre nuevo / de la revelación
    for sx, sy, ph in SPARK:
        if t < 5:
            a = seg(t, 2.4, 2.9) * max(0, math.sin(t * 5 + ph)) * (1 - seg(t, 4.6, 5.0))
        else:
            a = rev * max(0, math.sin(t * 6 + ph))
        if a > 0.05:
            r = 14 + 10 * a
            col = "#fff3b0" if t < 5 else "#e8fff6"
            c.append(f"<path d='M{sx:.0f} {sy-r:.0f} L{sx+r*0.25:.0f} {sy-r*0.25:.0f} L{sx+r:.0f} {sy:.0f} L{sx+r*0.25:.0f} {sy+r*0.25:.0f} "
                     f"L{sx:.0f} {sy+r:.0f} L{sx-r*0.25:.0f} {sy+r*0.25:.0f} L{sx-r:.0f} {sy:.0f} L{sx-r*0.25:.0f} {sy-r*0.25:.0f} Z' fill='{col}' opacity='{a:.2f}'/>")
    s.append(zoom(541, cy, z, "".join(c)))
    # gaviotas (fuera del zoom para que crucen la pantalla)
    for gx, gy, sc, fase in GULLS:
        x = (gx + t * 120 * sc) % 1400 - 150
        s.append(gaviota(x, gy + 15 * math.sin(t * 2 + fase * 4), sc * 1.4, t, fase))
    # lluvia
    if lluvia > 0.01:
        for rx, ry, sp in RAIN:
            yy = (ry + t * 1700 * sp) % 2000 - 60
            s.append(f"<line x1='{rx:.0f}' y1='{yy:.0f}' x2='{rx-10:.0f}' y2='{yy+46:.0f}' stroke='#dceaff' stroke-width='5' stroke-linecap='round' opacity='{0.45*lluvia:.2f}'/>")
    if flash > 0:
        s.append(f"<rect width='1080' height='1920' fill='#ffffff' opacity='{0.75*flash:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
