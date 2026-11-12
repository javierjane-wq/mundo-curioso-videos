"""2026-11-12-c1 · Cuerpo humano: los dedos no tienen músculos.

Una mano dibujada sale desde abajo y mueve los dedos sin parar. Un escáner de rayos X sube
por el brazo y, en la revelación, se ve por dentro: huesos, tendones como hilos y los músculos
que tiran de ellos... en el antebrazo, no en los dedos.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45   # el escáner termina: rayos X a pantalla completa
MUSICA = 2

rng = np.random.default_rng(12)
SPARK = [(rng.uniform(40, W - 40), rng.uniform(150, 1000), rng.uniform(5, 11), rng.uniform(0, 6.28)) for _ in range(22)]
BUBBLES = [(rng.uniform(0, W), rng.uniform(0, 1920), rng.uniform(6, 16), rng.uniform(30, 70)) for _ in range(26)]

SKIN = "#f6c29b"; SKIN_D = "#e39a72"; SKIN_L = "#ffd9bb"
WX, WY = 540, 1570          # muñeca (centro de giro de la mano)
# dedos: (x de la base, y de la base, largo, ancho, inclinación, fase)
FINGERS = [(412, 1290, 175, 66, -9, 0.0),    # meñique
           (490, 1268, 232, 72, -3, 0.18),   # anular
           (570, 1262, 258, 74, 1, 0.36),    # corazón
           (650, 1278, 232, 72, 6, 0.54)]    # índice
THUMB = (700, 1470, 190, 80, 38, 0.72)

PALM = "M372 1300 Q372 1250 430 1252 L660 1256 Q716 1262 712 1320 L708 1470 Q700 1560 620 1585 L470 1585 Q385 1560 378 1470 Z"


def flex(t, fase):
    """0 = dedo estirado, 1 = doblado."""
    if t < 2.5:      # saluda moviendo los dedos en ola
        return 0.5 + 0.5 * math.sin(2 * math.pi * (t * 1.6 - fase))
    if t < 5.0:      # cuenta: se doblan uno tras otro y se abren
        k = (t - 2.5) / 2.5
        return 0.5 - 0.5 * math.cos(2 * math.pi * clamp((k - fase * 0.6) * 1.6))
    if t < REVELACION:   # se quedan medio doblados, tensos, temblando
        return 0.35 + 0.06 * math.sin(t * 18 + fase * 6)
    return 0.5 + 0.5 * math.sin(2 * math.pi * (t * 1.2 - fase))   # con rayos X: abre y cierra


def rot(px, py, ang):
    a = math.radians(ang); dx, dy = px - WX, py - WY
    return WX + dx * math.cos(a) - dy * math.sin(a), WY + dx * math.sin(a) + dy * math.cos(a)


def finger(f, t, xray):
    x, y, L, w, ang, fase = f
    fl = flex(t, fase)
    s = 1 - 0.5 * fl                    # al doblarse se ve más corto (se dobla hacia nosotros)
    ang2 = ang + (8 * fl if ang > 20 else 0)
    l = L * s
    g = [f"<g transform='translate({x},{y}) rotate({ang2:.1f})'>"]
    if not xray:
        g.append(f"<rect x='{-w/2:.0f}' y='{-l:.1f}' width='{w}' height='{l + 60:.1f}' rx='{w/2:.0f}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
        for kk in (0.36, 0.68):           # pliegues de las articulaciones
            cy = -l * kk
            g.append(f"<path d='M{-w*0.28:.0f} {cy:.1f} Q0 {cy + 7:.1f} {w*0.28:.0f} {cy:.1f}' fill='none' stroke='{SKIN_D}' stroke-width='5' stroke-linecap='round'/>")
        # yema: al doblarse asoma la punta del dedo
        g.append(f"<ellipse cx='0' cy='{-l + w*0.42:.1f}' rx='{w*0.3:.1f}' ry='{w*0.22*(0.6+fl):.1f}' fill='{SKIN_L}' opacity='{0.4 + 0.5*fl:.2f}'/>")
    else:
        g.append(f"<rect x='{-w/2:.0f}' y='{-l:.1f}' width='{w}' height='{l + 60:.1f}' rx='{w/2:.0f}' fill='#2c6fa8' fill-opacity='0.45' stroke='#9fe7ff' stroke-width='6'/>")
        # tres falanges
        parts = [(0, 0.38), (0.41, 0.70), (0.73, 0.96)]
        for a, b in parts:
            y1, y2 = -l * b, -l * a
            g.append(f"<rect x='-13' y='{y1:.1f}' width='26' height='{max(4, y2 - y1 - 4):.1f}' rx='12' fill='#eef8ff' stroke='#6fb6e0' stroke-width='4'/>")
        # tendón (hilo amarillo) por el centro del dedo hasta la punta
        g.append(f"<line x1='0' y1='{-l*0.9:.1f}' x2='0' y2='40' stroke='#ffd23f' stroke-opacity='0.35' stroke-width='22' stroke-linecap='round'/>")
        g.append(f"<line x1='0' y1='{-l*0.9:.1f}' x2='0' y2='40' stroke='#ffe98a' stroke-width='8' stroke-linecap='round' stroke-dasharray='18 12' stroke-dashoffset='{-t*80:.0f}'/>")
    g.append("</g>")
    return "".join(g)


def thumb(t, xray):
    x, y, L, w, ang, fase = THUMB
    fl = flex(t, fase); a = ang - 22 * fl
    g = [f"<g transform='translate({x},{y}) rotate({a:.1f})'>"]
    if not xray:
        g.append(f"<rect x='{-w/2:.0f}' y='{-L:.0f}' width='{w}' height='{L + 70}' rx='{w/2:.0f}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M{-w*0.28:.0f} {-L*0.5:.0f} Q0 {-L*0.5 + 7:.0f} {w*0.28:.0f} {-L*0.5:.0f}' fill='none' stroke='{SKIN_D}' stroke-width='5' stroke-linecap='round'/>")
    else:
        g.append(f"<rect x='{-w/2:.0f}' y='{-L:.0f}' width='{w}' height='{L + 70}' rx='{w/2:.0f}' fill='#2c6fa8' fill-opacity='0.45' stroke='#9fe7ff' stroke-width='6'/>")
        for a1, b1 in [(0, 0.45), (0.5, 0.95)]:
            g.append(f"<rect x='-14' y='{-L*b1:.0f}' width='28' height='{L*(b1-a1) - 4:.0f}' rx='12' fill='#eef8ff' stroke='#6fb6e0' stroke-width='4'/>")
        g.append(f"<line x1='0' y1='{-L*0.88:.0f}' x2='0' y2='60' stroke='#ffd23f' stroke-opacity='0.35' stroke-width='22' stroke-linecap='round'/>")
        g.append(f"<line x1='0' y1='{-L*0.88:.0f}' x2='0' y2='60' stroke='#ffe98a' stroke-width='8' stroke-linecap='round' stroke-dasharray='18 12' stroke-dashoffset='{-t*80:.0f}'/>")
    g.append("</g>")
    return "".join(g)


def wave(t):
    return 6 * math.sin(t * 2.4) if t < REVELACION else 3 * math.sin(t * 2.4)


def hand_normal(t):
    a = wave(t)
    s = []
    # antebrazo y manga (no giran)
    s.append(f"<path d='M425 1560 L655 1560 L700 1940 L380 1940 Z' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M355 1770 Q540 1730 725 1770 L760 1960 L320 1960 Z' fill='#7b5cff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M350 1775 Q540 1735 730 1775 L736 1815 Q540 1775 344 1815 Z' fill='#ffd23f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for sx in (430, 540, 650):
        s.append(f"<circle cx='{sx}' cy='{1870 + (sx-540)**2/9000:.0f}' r='14' fill='#ff7ab6' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<g transform='rotate({a:.2f},{WX},{WY})'>")
    s.append(thumb(t, False))
    s.append(f"<path d='{PALM}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for f in FINGERS: s.append(finger(f, t, False))
    s.append(f"<path d='{PALM}' fill='{SKIN}' clip-path='url(#palmtop)'/>")
    # líneas de la palma
    s.append(f"<path d='M400 1350 Q520 1335 640 1300' fill='none' stroke='{SKIN_D}' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<path d='M395 1420 Q500 1400 600 1420' fill='none' stroke='{SKIN_D}' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<path d='M640 1440 Q590 1500 600 1560' fill='none' stroke='{SKIN_D}' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<ellipse cx='470' cy='1480' rx='48' ry='30' fill='{SKIN_L}' opacity='0.6'/>")
    s.append("</g>")
    return "".join(s)


def hand_xray(t):
    a = wave(t)
    fl_avg = sum(flex(t, f[5]) for f in FINGERS) / 4
    s = []
    # antebrazo transparente con sus dos huesos
    s.append(f"<path d='M425 1560 L655 1560 L700 1940 L380 1940 Z' fill='#2c6fa8' fill-opacity='0.4' stroke='#9fe7ff' stroke-width='6'/>")
    for bx1, bx2 in ((488, 468), (594, 616)):
        s.append(f"<path d='M{bx1} 1600 L{bx2} 1940' stroke='#6fb6e0' stroke-width='46' stroke-linecap='round'/>")
        s.append(f"<path d='M{bx1} 1600 L{bx2} 1940' stroke='#eef8ff' stroke-width='36' stroke-linecap='round'/>")
    # músculos del antebrazo: se hinchan al tirar
    for i, (mx, my) in enumerate(((470, 1785), (540, 1765), (612, 1785))):
        k = 1 + 0.16 * flex(t, i * 0.2)
        s.append(f"<g transform='translate({mx},{my}) scale({1 + 0.1*(k-1)*3:.3f},{k:.3f})'>"
                 f"<ellipse rx='46' ry='120' fill='#ff4f6d' stroke='#ffd0d8' stroke-width='6'/>"
                 f"<path d='M-20 -90 Q-28 0 -20 90 M0 -105 L0 105 M20 -90 Q28 0 20 90' fill='none' stroke='#ff9aae' stroke-width='5'/></g>")
    # tendones: de cada dedo, por la muñeca, hasta los músculos
    pts = [(f[0], f[1]) for f in FINGERS] + [(THUMB[0], THUMB[1])]
    for i, (px, py) in enumerate(pts):
        gx, gy = rot(px, py + 30, a)
        mid = rot(500 + i * 22, 1540, a)
        end = (470 + i * 35, 1700)
        d = f"M{gx:.0f} {gy:.0f} Q{mid[0]:.0f} {mid[1]:.0f} {end[0]:.0f} {end[1]:.0f}"
        s.append(f"<path d='{d}' fill='none' stroke='#ffd23f' stroke-opacity='0.35' stroke-width='22' stroke-linecap='round'/>")
        s.append(f"<path d='{d}' fill='none' stroke='#ffe98a' stroke-width='8' stroke-linecap='round' stroke-dasharray='18 12' stroke-dashoffset='{-t*80:.0f}'/>")
    s.append(f"<g transform='rotate({a:.2f},{WX},{WY})'>")
    s.append(thumb(t, True))
    s.append(f"<path d='{PALM}' fill='#2c6fa8' fill-opacity='0.45' stroke='#9fe7ff' stroke-width='6'/>")
    # huesos de la palma (metacarpianos) y de la muñeca (carpo)
    for f in FINGERS:
        s.append(f"<path d='M{f[0]} {f[1] + 30} L{lerp(f[0], 540, 0.55):.0f} 1500' stroke='#6fb6e0' stroke-width='34' stroke-linecap='round'/>")
        s.append(f"<path d='M{f[0]} {f[1] + 30} L{lerp(f[0], 540, 0.55):.0f} 1500' stroke='#eef8ff' stroke-width='24' stroke-linecap='round'/>")
    for cx, cy, r in ((480, 1525, 22), (520, 1540, 24), (565, 1535, 22), (605, 1520, 20), (500, 1565, 18), (585, 1565, 18)):
        s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#eef8ff' stroke='#6fb6e0' stroke-width='4'/>")
    for f in FINGERS: s.append(finger(f, t, True))
    s.append("</g>")
    return "".join(s)


def frame(t):
    rise = lerp(520, 0, ease(clamp(t / 1.3))) + (0 if t > 1.3 else 0) - 25 * math.sin(math.pi * clamp((t - 1.0) / 0.5))
    bounce = 4 * math.sin(t * 3.1)
    dy = rise + bounce
    # escáner: sube de 5,0 a REVELACION, luego los rayos X ocupan toda la pantalla
    scan_y = lerp(1990, 940, seg(t, 5.0, REVELACION)) if t < REVELACION else lerp(940, -60, seg(t, REVELACION, REVELACION + 0.45))
    scanning = 5.0 <= t
    flash = clamp(1 - (t - REVELACION) / 0.5) if t >= REVELACION else 0
    defs = ("<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#6cc8ff'/>"
            "<stop offset='0.6' stop-color='#bfeaff'/><stop offset='1' stop-color='#e9f8ff'/></linearGradient>"
            "<radialGradient id='lab' cx='0.5' cy='0.78' r='0.8'><stop offset='0' stop-color='#1f5b8f'/>"
            "<stop offset='0.6' stop-color='#0f2c52'/><stop offset='1' stop-color='#081a33'/></radialGradient>"
            "<radialGradient id='sun'><stop offset='0' stop-color='#fff6c8'/><stop offset='1' stop-color='#fff6c8' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='palmtop'><rect x='0' y='1296' width='{W}' height='400'/></clipPath>"
            f"<clipPath id='scan'><rect x='0' y='{max(0, scan_y):.1f}' width='{W}' height='{H}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol y nubes (arriba, tranquilo)
    s.append("<circle cx='930' cy='880' r='230' fill='url(#sun)' opacity='0.8'/>")
    s.append(f"<circle cx='930' cy='880' r='{88 + 4*math.sin(t*2):.0f}' fill='#ffe35a' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (cx, cy, sc) in enumerate(((120, 760, 1.4), (700, 930, 1.1), (380, 520, 0.9))):
        dx = (t * (16 + 7 * i)) % 1500 - 300
        s.append(f"<g transform='translate({cx + dx - 300:.0f},{cy}) scale({sc})'>"
                 f"<path d='M0 60 Q0 10 50 18 Q70 -30 130 -5 Q175 -35 215 15 Q265 15 260 60 Z' fill='#ffffff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    for sx, sy, sr, ph in SPARK:
        a = 0.35 + 0.35 * math.sin(t * 3 + ph)
        s.append(f"<path d='M{sx:.0f} {sy-sr*1.6:.0f} L{sx+sr*0.4:.0f} {sy:.0f} L{sx:.0f} {sy+sr*1.6:.0f} L{sx-sr*0.4:.0f} {sy:.0f} Z' fill='#ffffff' opacity='{a:.2f}'/>")
    # colinas abajo
    s.append(f"<path d='M0 1660 Q200 1590 420 1650 T840 1630 T1080 1650 L1080 1920 L0 1920 Z' fill='#8fdc6a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1780 Q260 1720 540 1780 T1080 1770 L1080 1920 L0 1920 Z' fill='#5fc24f' stroke='{INK}' stroke-width='{LW}'/>")
    for fx, fy, col in ((110, 1760, '#ff7ab6'), (220, 1830, '#ffd23f'), (900, 1750, '#ffffff'), (1000, 1840, '#ff7ab6'), (820, 1860, '#ffd23f')):
        sw = 6 * math.sin(t * 2.5 + fx)
        s.append(f"<g transform='translate({fx},{fy}) rotate({sw:.1f})'><line x1='0' y1='0' x2='0' y2='40' stroke='#2f8a3a' stroke-width='6'/>"
                 + "".join(f"<circle cx='{12*math.cos(k*1.2566):.1f}' cy='{12*math.sin(k*1.2566):.1f}' r='10' fill='{col}' stroke='{INK}' stroke-width='4'/>" for k in range(5))
                 + f"<circle r='8' fill='#ff9f1c' stroke='{INK}' stroke-width='4'/></g>")
    # líneas de movimiento junto a los dedos (antes del escáner)
    mv = 1 - seg(t, 4.6, 5.2)
    if mv > 0.02:
        for i, (lx, ly) in enumerate(((330, 1150), (760, 1120), (300, 1300), (790, 1290))):
            o = (0.5 + 0.5 * math.sin(t * 8 + i)) * mv
            s.append(f"<path d='M{lx} {ly + dy:.0f} q{-14 if lx < 540 else 14} 20 0 40' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' opacity='{o:.2f}'/>")
    hand = f"<g transform='translate(0,{dy:.1f})'>" + hand_normal(t) + "</g>"
    scene = "".join(s) + hand
    # capa de rayos X (por debajo de la línea del escáner)
    if scanning:
        xr = [f"<g clip-path='url(#scan)'>", f"<rect width='{W}' height='{H}' fill='url(#lab)'/>"]
        for gx in range(0, W + 1, 90):
            xr.append(f"<line x1='{gx}' y1='0' x2='{gx}' y2='{H}' stroke='#3f86c4' stroke-opacity='0.25' stroke-width='3'/>")
        for gy in range(0, H + 1, 90):
            xr.append(f"<line x1='0' y1='{gy}' x2='{W}' y2='{gy}' stroke='#3f86c4' stroke-opacity='0.25' stroke-width='3'/>")
        for bx, by, br, sp in BUBBLES:
            yy = (by - t * sp) % 1920
            xr.append(f"<circle cx='{bx:.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='none' stroke='#9fe7ff' stroke-opacity='0.35' stroke-width='3'/>")
        xr.append(f"<g transform='translate(0,{dy:.1f})'>" + hand_xray(t) + "</g>")
        # halo rojo en los músculos tras la revelación
        glow = seg(t, REVELACION, REVELACION + 0.6)
        if glow > 0:
            xr.append(f"<ellipse cx='540' cy='{1780 + dy:.0f}' rx='{170 + 15*math.sin(t*6):.0f}' ry='230' fill='#ff4f6d' opacity='{0.18*glow:.2f}'/>")
        xr.append("</g>")
        scene += "".join(xr)
        if scan_y > 0:
            scene += (f"<rect x='0' y='{scan_y - 18:.1f}' width='{W}' height='36' fill='#7ff3ff' opacity='0.35'/>"
                      f"<rect x='0' y='{scan_y - 5:.1f}' width='{W}' height='10' fill='#e8ffff' stroke='{INK}' stroke-width='4'/>")
    z = 1 + 0.13 * seg(t, REVELACION, 10)
    out = zoom(540, 1560, z, scene)
    if flash > 0:
        out += f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.85*flash:.2f}'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{out}</svg>")
