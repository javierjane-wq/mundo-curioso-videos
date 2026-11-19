"""2026-11-19-c2 · Cataratas de Sangre (Blood Falls), glaciar Taylor, Antártida.

Un pingüino llega andando por un lago helado frente a un glaciar blanco. De una grieta del hielo
empieza a salir agua transparente que cae hasta el lago; al tocar el aire empieza a teñirse y en
la REVELACION toda la cascada y la mancha del lago se vuelven ROJAS (el hierro del agua se oxida):
destello, zoom de cámara y el pingüino aletea asombrado.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso

DUR = 10.0
REVELACION = 7.4   # la cascada se vuelve roja: golpe musical
MUSICA = 4

rng = np.random.default_rng(1911)
SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 8), rng.uniform(40, 110), rng.uniform(0, 6.28))
        for _ in range(70)]
SPARK = [(rng.uniform(60, 1020), rng.uniform(1640, 1880), rng.uniform(0, 6.28)) for _ in range(14)]
DROPS = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(5, 11)) for _ in range(16)]

CX, TOP = 700, 1215          # grieta de la que sale el agua
BOT = 1640                   # donde cae al lago
CLEAR = "#9fdcff"
RED = "#c3161c"
RED_D = "#86100f"


def cielo(t):
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol pálido polar
    s.append("<circle cx='840' cy='640' r='190' fill='url(#sun)'/>")
    s.append(f"<circle cx='840' cy='640' r='62' fill='#fffbe9' stroke='#ffe6a6' stroke-width='8'/>")
    # nubes suaves que se desplazan
    for i, (cx, cy, sc, sp) in enumerate([(150, 760, 1.25, 10), (700, 880, 1.0, 14), (980, 520, 0.8, 8)]):
        x = (cx + t * sp + 200) % 1400 - 200
        s.append(f"<g transform='translate({x:.0f},{cy}) scale({sc})' opacity='0.95'>"
                 f"<path d='M-110 30 Q-110 -10 -70 -8 Q-60 -55 -10 -45 Q20 -80 65 -45 Q115 -50 115 0 Q140 10 125 30 Z' "
                 f"fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    return "".join(s)


def montanas():
    s = []
    s.append(f"<path d='M-20 1140 L120 1010 L230 1080 L380 960 L520 1070 L640 990 L780 1060 L920 975 L1100 1090 L1100 1200 L-20 1200 Z' "
             f"fill='#a9c6e4' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # nieve en las cumbres
    for (px, py, w) in ((120, 1010, 55), (380, 960, 70), (640, 990, 55), (920, 975, 65)):
        s.append(f"<path d='M{px - w} {py + w*0.85:.0f} L{px} {py} L{px + w} {py + w*0.85:.0f} "
                 f"L{px + w*0.45:.0f} {py + w*0.6:.0f} L{px + w*0.1:.0f} {py + w*0.9:.0f} L{px - w*0.4:.0f} {py + w*0.6:.0f} Z' "
                 f"fill='#ffffff' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return "".join(s)


def glaciar(t, rojo, tinte):
    s = []
    # superficie superior del glaciar
    s.append(f"<path d='M-30 1190 Q200 1150 420 1170 Q640 1140 860 1165 Q980 1150 1110 1175 L1110 1240 L-30 1240 Z' "
             f"fill='#ffffff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # frente del glaciar (pared de hielo con facetas)
    s.append(f"<path d='M-30 1225 L1110 1225 L1110 1660 Q900 1640 700 1655 Q450 1640 260 1660 Q100 1650 -30 1665 Z' "
             f"fill='#e9f7ff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for (x1, x2, x3, col) in ((40, 150, 110, "#c7e8fb"), (300, 420, 350, "#bfe3f8"), (520, 600, 560, "#d3eefc"),
                              (860, 980, 930, "#c3e6fa"), (1000, 1100, 1040, "#d6effc")):
        s.append(f"<path d='M{x1} 1230 L{x2} 1230 L{x3} 1650 L{x1 + 10} 1650 Z' fill='{col}'/>")
    for x in (150, 330, 470, 610, 820, 960):
        s.append(f"<path d='M{x} 1240 L{x + 18} 1380 L{x - 6} 1500' fill='none' stroke='#7fb7dc' stroke-width='6' stroke-linecap='round'/>")
    # mancha rojiza en la pared alrededor de la cascada (el hierro la tiñe)
    a = max(0.18 * tinte, rojo)
    if a > 0.01:
        s.append(f"<path d='M{CX - 40} {TOP} Q{CX - 150} 1420 {CX - 230} 1652 L{CX + 230} 1652 Q{CX + 150} 1420 {CX + 40} {TOP} Z' "
                 f"fill='{mix('#e9a27a', '#b5301f', rojo)}' opacity='{0.85*a:.2f}'/>")
    # grieta
    g = seg(t, 2.6, 3.3)
    if g > 0:
        w = 16 + 20 * seg(t, 5, 7)
        s.append(f"<path d='M{CX - w*g:.0f} {TOP + 8} Q{CX} {TOP - 20*g:.0f} {CX + w*g:.0f} {TOP + 8} Q{CX} {TOP + 30*g:.0f} {CX - w*g:.0f} {TOP + 8} Z' "
                 f"fill='#2c5f86' stroke='{INK}' stroke-width='6'/>")
    return "".join(s)


def lago(t):
    s = [f"<rect x='0' y='1640' width='{W}' height='{H - 1640}' fill='url(#lake)'/>",
         f"<path d='M-20 1650 Q300 1630 540 1655 Q800 1635 1100 1650' fill='none' stroke='{INK}' stroke-width='{LW}'/>"]
    for d in ("M60 1760 L200 1800 L260 1880", "M880 1720 L960 1790 L1060 1800", "M420 1860 L520 1830 L600 1900"):
        s.append(f"<path d='{d}' fill='none' stroke='#8fc2e2' stroke-width='6' stroke-linecap='round'/>")
    # rocas oscuras del valle
    for (x, y, rx) in ((40, 1690, 70), (1040, 1700, 60), (980, 1880, 80), (120, 1900, 70)):
        s.append(f"<ellipse cx='{x}' cy='{y}' rx='{rx}' ry='{rx*0.55:.0f}' fill='#8a6a55' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<ellipse cx='{x - rx*0.25:.0f}' cy='{y - rx*0.18:.0f}' rx='{rx*0.35:.0f}' ry='{rx*0.15:.0f}' fill='#a88a72'/>")
    # brillos del hielo
    for (x, y, ph) in SPARK:
        a = 0.5 + 0.5 * math.sin(t * 3 + ph)
        if a > 0.6:
            r = 10 * a
            s.append(f"<path d='M{x:.0f} {y - r:.0f} L{x + r*0.25:.0f} {y:.0f} L{x:.0f} {y + r:.0f} L{x - r*0.25:.0f} {y:.0f} Z' fill='#fff' opacity='{a:.2f}'/>"
                     f"<path d='M{x - r:.0f} {y:.0f} L{x:.0f} {y + r*0.25:.0f} L{x + r:.0f} {y:.0f} L{x:.0f} {y - r*0.25:.0f} Z' fill='#fff' opacity='{a:.2f}'/>")
    return "".join(s)


def cascada(t, rojo, tinte):
    s = []
    caida = seg(t, 3.1, 4.6)
    if caida <= 0:
        return ""
    yb = lerp(TOP + 10, BOT, caida)
    ancho = 1 + 0.6 * seg(t, 5, 7.2)
    # charco / mancha en el lago
    charco = seg(t, 4.4, 5.6)
    if charco > 0:
        rx = lerp(30, 150, charco) * (1 + 0.25 * seg(t, 5.5, 7.2)) + 160 * seg(t, REVELACION, REVELACION + 0.8)
        rx *= 1 + 0.02 * pulso(t, 1.4) * rojo
        ry = rx * 0.3
        col = mix(mix(CLEAR, "#f3b08a", tinte), RED, rojo)
        pts = []
        for i in range(24):
            ang = 2 * math.pi * i / 24
            k = 1 + 0.12 * math.sin(ang * 5 + 1.3) + 0.06 * math.sin(ang * 3)
            pts.append(f"{CX + rx * k * math.cos(ang):.0f},{BOT + 40 + ry * k * math.sin(ang):.0f}")
        s.append(f"<polygon points='{' '.join(pts)}' fill='{col}' stroke='{mix('#7fb7dc', RED_D, rojo)}' stroke-width='7' stroke-linejoin='round' opacity='{0.85 + 0.15*rojo:.2f}'/>")
        s.append(f"<ellipse cx='{CX - rx*0.3:.0f}' cy='{BOT + 30:.0f}' rx='{rx*0.25:.0f}' ry='{ry*0.22:.0f}' fill='#fff' opacity='{0.55 - 0.25*rojo:.2f}'/>")
    # chorro que se ensancha al bajar
    wt, wb = 22 * ancho, 70 * ancho
    wy = lambda y: lerp(wt, wb, (y - TOP) / (BOT - TOP))
    izq, der = [], []
    for i in range(13):
        y = lerp(TOP + 10, yb, i / 12)
        o = 10 * math.sin(y * 0.035 - t * 9) * (y - TOP) / (BOT - TOP)
        izq.append(f"{CX - wy(y) + o:.0f},{y:.0f}"); der.append(f"{CX + wy(y) + o:.0f},{y:.0f}")
    pts = " ".join(izq + der[::-1])
    s.append(f"<polygon points='{pts}' fill='url(#agua)' stroke='{mix('#5aa4d0', RED_D, rojo)}' stroke-width='7' stroke-linejoin='round'/>")
    # rayas de corriente que bajan
    for j in range(5):
        x = CX + (j - 2) * 0.32 * wt
        dx = (j - 2) * 0.32 * (wb - wt)
        col = mix("#ffffff", "#ff8a7a", rojo)
        s.append(f"<path d='M{x:.0f} {TOP + 20} L{x + dx * (yb - TOP) / (BOT - TOP):.0f} {yb - 10:.0f}' stroke='{col}' stroke-width='6' "
                 f"stroke-linecap='round' stroke-dasharray='34 46' stroke-dashoffset='{-t * 260 + j * 23:.0f}' opacity='0.85'/>")
    # salpicaduras al caer
    if caida >= 1:
        for (dx, ph, r) in DROPS:
            k = (t * 1.6 + ph) % 1
            x = CX + dx * (70 + 80 * k) * ancho
            y = BOT + 30 - 120 * k * (1 - k) * 2.2
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * (1 - 0.5*k):.1f}' fill='{mix(CLEAR, RED, rojo)}' "
                     f"stroke='{mix('#5aa4d0', RED_D, rojo)}' stroke-width='3' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def pinguino(t, susto):
    x = lerp(-30, 270, seg(t, 0, 2.3))
    andando = t < 2.35
    paso = math.sin(t * 13) if andando else 0
    y = 1815 - (abs(paso) * 10 if andando else 0)
    rot = 8 * paso if andando else lerp(0, 6, susto) + 2 * math.sin(t * 2.2)
    aleteo = 0
    if t > REVELACION:
        aleteo = 38 * abs(math.sin((t - REVELACION) * 10))
    elif not andando:
        aleteo = 6 * math.sin(t * 3)
    blink = 0.12 if (t % 2.9) < 0.12 and susto < 0.5 else 1.0
    ojo = 1 + 0.35 * susto
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"]
    g.append("<ellipse cx='0' cy='4' rx='105' ry='18' fill='#2a5a80' opacity='0.25'/>")
    # patas
    for fx in (-38, 38):
        g.append(f"<path d='M{fx - 30} 4 Q{fx} -22 {fx + 30} 4 Z' fill='#ff9a2e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # aletas
    g.append(f"<g transform='translate(-78,-150) rotate({20 + aleteo:.1f})'><path d='M0 0 Q-40 50 -22 120 Q5 70 16 10 Z' fill='#1c2436' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    g.append(f"<g transform='translate(78,-150) rotate({-20 - aleteo:.1f})'><path d='M0 0 Q40 50 22 120 Q-5 70 -16 10 Z' fill='#1c2436' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # cuerpo
    g.append(f"<path d='M0 -250 Q-95 -245 -92 -110 Q-95 -10 0 -6 Q95 -10 92 -110 Q95 -245 0 -250 Z' fill='#1c2436' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("<path d='M0 -190 Q-66 -170 -64 -90 Q-62 -20 0 -18 Q62 -20 64 -90 Q66 -170 0 -190 Z' fill='#fbfbf7'/>")
    # cara
    for ex in (-30, 30):
        g.append(f"<g transform='translate({ex},-200) scale({ojo:.3f},{ojo * blink:.3f})'>"
                 f"<ellipse rx='22' ry='25' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{6 + 4*susto:.1f}' cy='2' r='{11 - 2*susto:.1f}' fill='{INK}'/>"
                 f"<circle cx='{2 + 4*susto:.1f}' cy='-4' r='4' fill='#fff'/></g>")
    g.append(f"<ellipse cx='-52' cy='-168' rx='14' ry='8' fill='#ff8fa0' opacity='0.8'/><ellipse cx='52' cy='-168' rx='14' ry='8' fill='#ff8fa0' opacity='0.8'/>")
    boca = 10 * susto
    g.append(f"<path d='M-22 -170 L22 -170 L0 {-148 + boca:.0f} Z' fill='#ff9a2e' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def nieve(t, sobre_abajo):
    s = []
    for (x, y, r, sp, ph) in SNOW:
        yy = (y + t * sp) % H
        if (yy > 1100) != sobre_abajo:
            continue
        xx = x + 18 * math.sin(t * 1.3 + ph)
        s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#fff' opacity='0.85'/>")
    return "".join(s)


def frame(t):
    tinte = seg(t, 5.6, 7.3) * 0.45            # el agua empieza a teñirse al tocar el aire
    rojo = seg(t, REVELACION, REVELACION + 0.55)
    susto = seg(t, 5.2, 6.2)
    top_col = mix(CLEAR, mix("#f6c9a4", RED, rojo), max(tinte * 0.2, rojo))
    bot_col = mix(CLEAR, mix("#f0a47c", RED, rojo), max(tinte, rojo))
    defs = (
        "<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#6fb6ec'/>"
        "<stop offset='0.55' stop-color='#bfe3fb'/><stop offset='1' stop-color='#eef9ff'/></linearGradient>"
        "<radialGradient id='sun'><stop offset='0' stop-color='#fff6d8' stop-opacity='0.9'/><stop offset='1' stop-color='#fff6d8' stop-opacity='0'/></radialGradient>"
        "<linearGradient id='lake' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#bfe6fb'/><stop offset='1' stop-color='#e6f6ff'/></linearGradient>"
        f"<linearGradient id='agua' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top_col}'/>"
        f"<stop offset='1' stop-color='{bot_col}'/></linearGradient>"
    )
    z = 1 + 0.03 * seg(t, 0, 7) + 0.14 * seg(t, REVELACION, REVELACION + 0.8)
    escena = [montanas(), glaciar(t, rojo, tinte), lago(t), cascada(t, rojo, tinte), pinguino(t, susto)]
    # destello en la revelación
    f = clamp((t - REVELACION) / 0.7)
    if 0 < f < 1:
        escena.append(f"<circle cx='{CX}' cy='{BOT}' r='{lerp(40, 520, f):.0f}' fill='none' stroke='#fff' stroke-width='{lerp(30, 4, f):.0f}' opacity='{1 - f:.2f}'/>")
        escena.append(f"<circle cx='{CX}' cy='{BOT}' r='{lerp(20, 380, f):.0f}' fill='none' stroke='#ff5a4e' stroke-width='{lerp(18, 3, f):.0f}' opacity='{1 - f:.2f}'/>")
    cuerpo = cielo(t) + nieve(t, False) + \
        f"<g transform='translate({CX},1500) scale({z:.4f}) translate({-CX},-1500)'>{''.join(escena)}</g>" + nieve(t, True)
    fl = clamp(1 - (t - REVELACION) / 0.35) if t >= REVELACION else 0
    if fl > 0:
        cuerpo += f"<rect width='{W}' height='{H}' fill='#fff' opacity='{0.45*fl:.2f}'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")
