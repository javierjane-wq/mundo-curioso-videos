"""Big Ben no es la torre: es la campana de 13,7 toneladas que suena dentro (la torre es la Torre Elizabeth).

Composición: torre del reloj (dibujo propio) en la mitad de abajo, palacio a los lados, río con barco,
paloma que llega volando. En la REVELACION: martillazo a la campana, luz dorada y zoom al campanario,
donde la campana (con ojos) se ve en grande.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso

DUR = 10.0
REVELACION = 7.5   # martillazo: ¡BONG!
MUSICA = 2

rng = np.random.default_rng(14)
CLOUDS = [(150, 360, 1.3, 9), (760, 220, 1.0, 6), (520, 620, 1.5, 11), (980, 520, 0.9, 7), (60, 820, 1.1, 8)]
SPARK = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28)) for _ in range(26)]

STONE = "#ecc77f"; STONE_D = "#c99f57"; STONE_L = "#f7dea6"
SLATE = "#3d4a72"; GOLD = "#ffcf3f"; GOLD_D = "#d79a1d"
BELL_C = (540, 1186)  # centro de la campana


def nube(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M-110 30 Q-120 -10 -70 -12 Q-60 -55 -10 -45 Q20 -80 65 -45 Q115 -50 110 0 Q140 15 115 30 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def ventana_gotica(x, y, w, h, col="#4a3d5e"):
    r = w / 2
    return (f"<path d='M{x:.0f} {y + h:.0f} L{x:.0f} {y + r:.0f} Q{x:.0f} {y:.0f} {x + r:.0f} {y - r * 0.4:.0f} "
            f"Q{x + w:.0f} {y:.0f} {x + w:.0f} {y + r:.0f} L{x + w:.0f} {y + h:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='5'/>")


def palacio(x0, x1, top, glow):
    g = []
    wall = mix(STONE, "#ffc978", glow * 0.5)
    g.append(f"<rect x='{x0}' y='{top}' width='{x1 - x0}' height='{1830 - top}' fill='{wall}' stroke='{INK}' stroke-width='{LW}'/>")
    # tejado
    g.append(f"<path d='M{x0 - 10} {top} L{x0 + 20} {top - 40} L{x1 - 20} {top - 40} L{x1 + 10} {top} Z' fill='{SLATE}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # pináculos
    for px in range(x0 + 30, x1, 70):
        g.append(f"<path d='M{px - 12} {top - 40} L{px} {top - 92} L{px + 12} {top - 40} Z' fill='{STONE_D}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # ventanas
    for fila, wy in enumerate((top + 40, top + 135)):
        for wx in range(x0 + 28, x1 - 40, 70):
            col = mix("#4a3d5e", "#ffd86b", glow * 0.8)
            g.append(ventana_gotica(wx, wy, 34, 62, col))
    return "".join(g)


def campana(t, rev):
    """Campana original con ojos. rev: 0..1 (sorpresa en la revelación)."""
    cx, cy = BELL_C
    ts = [REVELACION, REVELACION + 1.3]
    wob = 0.0
    for s0 in ts:
        if t >= s0:
            wob += 0.06 * math.exp(-(t - s0) * 3.5) * math.sin((t - s0) * 40)
    g = [f"<g transform='translate({cx},{cy}) scale({1 + wob:.4f},{1 - wob * 0.6:.4f})'>"]
    body = mix("#c4863a", "#ffb948", rev * 0.6)
    g.append(f"<rect x='-10' y='-62' width='20' height='14' rx='4' fill='{GOLD_D}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M-16 -50 Q0 -60 16 -50 L32 -44 Q46 -38 47 -8 Q49 28 64 40 Q66 48 56 50 L-56 50 Q-66 48 -64 40 "
             f"Q-49 28 -47 -8 Q-46 -38 -32 -44 Z' fill='{body}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M-30 -34 Q-38 -10 -36 18' fill='none' stroke='#ffe1a0' stroke-width='6' stroke-linecap='round' opacity='0.85'/>")
    g.append(f"<path d='M-56 38 Q0 46 56 38' fill='none' stroke='{INK}' stroke-width='4'/>")
    # ojos
    blink = 0.12 if (t % 2.7) < 0.13 else 1.0
    es = 1 + 0.35 * rev
    for ex in (-17, 17):
        g.append(f"<g transform='translate({ex},-6) scale({es:.3f},{es * blink:.3f})'>"
                 f"<ellipse rx='10' ry='12' fill='#fff' stroke='{INK}' stroke-width='4'/>"
                 f"<circle cx='1' cy='2' r='5.5' fill='{INK}'/><circle cx='-1.5' cy='-1' r='2' fill='#fff'/></g>")
    # boca: sonrisa -> "¡O!"
    if rev < 0.5:
        g.append(f"<path d='M-9 16 Q0 23 9 16' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='20' rx='{6 + 3 * rev:.1f}' ry='{7 + 4 * rev:.1f}' fill='#7a2a2a' stroke='{INK}' stroke-width='4'/>")
    # mejillas
    g.append(f"<circle cx='-31' cy='12' r='6' fill='#ff8a7a' opacity='0.7'/><circle cx='31' cy='12' r='6' fill='#ff8a7a' opacity='0.7'/>")
    g.append("</g>")
    # martillo (golpea por fuera, a la derecha)
    ang = 0.0
    for s0 in ts:
        ang = max(ang, 0)
    k1 = seg(t, REVELACION - 0.8, REVELACION - 0.05)
    hit1 = t >= REVELACION - 0.05
    ang = lerp(0, -38, k1) if not hit1 else lerp(-38, 0, seg(t, REVELACION - 0.05, REVELACION))
    if t > REVELACION + 0.4:
        ang = lerp(0, -38, seg(t, REVELACION + 0.4, REVELACION + 1.2)) if t < REVELACION + 1.25 else lerp(-38, 0, seg(t, REVELACION + 1.25, REVELACION + 1.3))
    g.append(f"<g transform='translate({cx + 92},{cy - 40}) rotate({ang:.1f})'>"
             f"<line x1='0' y1='0' x2='-22' y2='62' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
             f"<rect x='-38' y='54' width='26' height='22' rx='5' fill='#6b6f7a' stroke='{INK}' stroke-width='5'/>"
             f"<circle r='6' fill='{INK}'/></g>")
    return "".join(g)


def torre(t, glow, rev):
    g = []
    st = mix(STONE, "#ffd88a", glow * 0.5); sd = mix(STONE_D, "#e0a24a", glow * 0.4)
    # fuste
    g.append(f"<rect x='432' y='1440' width='216' height='400' fill='{st}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='600' y='1445' width='44' height='390' fill='{sd}'/>")
    for px in (470, 510, 550, 590):
        g.append(f"<line x1='{px}' y1='1460' x2='{px}' y2='1830' stroke='{sd}' stroke-width='6'/>")
    for wy in (1500, 1620, 1740):
        for wx in (478, 556):
            g.append(ventana_gotica(wx, wy, 26, 52, mix("#4a3d5e", "#ffd86b", glow * 0.7)))
    g.append(f"<rect x='432' y='1440' width='216' height='400' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # cuerpo del reloj
    g.append(f"<rect x='405' y='1236' width='270' height='214' fill='{st}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='428' y='1252' width='224' height='184' rx='6' fill='{SLATE}' stroke='{INK}' stroke-width='6'/>")
    for (qx, qy) in ((440, 1264), (640, 1264), (440, 1424), (640, 1424)):
        g.append(f"<circle cx='{qx}' cy='{qy}' r='7' fill='{GOLD}' stroke='{INK}' stroke-width='3'/>")
    cx, cy, r = 540, 1344, 86
    face = mix("#fffbe9", "#fff1b8", glow)
    g.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 8}' fill='{GOLD}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<circle cx='{cx}' cy='{cy}' r='{r - 4}' fill='{face}' stroke='{INK}' stroke-width='5'/>")
    for i in range(12):
        a = math.radians(i * 30)
        r1 = r - 16 if i % 3 else r - 26
        g.append(f"<line x1='{cx + (r - 8) * math.sin(a):.1f}' y1='{cy - (r - 8) * math.cos(a):.1f}' "
                 f"x2='{cx + r1 * math.sin(a):.1f}' y2='{cy - r1 * math.cos(a):.1f}' stroke='{INK}' stroke-width='{6 if i % 3 == 0 else 4}' stroke-linecap='round'/>")
    mins = lerp(300, 360, clamp(t / REVELACION)) + (t - REVELACION) * 6 * (t > REVELACION)
    hrs = -5 + mins / 72
    for ang, ln, wd in ((hrs, 46, 10), (mins, 70, 7)):
        a = math.radians(ang)
        g.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + ln * math.sin(a):.1f}' y2='{cy - ln * math.cos(a):.1f}' stroke='{INK}' stroke-width='{wd}' stroke-linecap='round'/>")
    g.append(f"<circle cx='{cx}' cy='{cy}' r='9' fill='{GOLD}' stroke='{INK}' stroke-width='4'/>")
    # cornisa
    g.append(f"<rect x='395' y='1226' width='290' height='20' rx='4' fill='{sd}' stroke='{INK}' stroke-width='6'/>")
    # campanario: interior oscuro con la campana
    g.append(f"<rect x='420' y='1110' width='240' height='120' fill='{st}' stroke='{INK}' stroke-width='{LW}'/>")
    inner = mix("#2c2340", "#5a3a2a", glow)
    g.append(f"<path d='M438 1226 L438 1150 Q438 1124 540 1122 Q642 1124 642 1150 L642 1226 Z' fill='{inner}' stroke='{INK}' stroke-width='6'/>")
    if glow > 0.01:
        g.append(f"<circle cx='{BELL_C[0]}' cy='{BELL_C[1]}' r='{90 + 20 * glow:.0f}' fill='url(#bellglow)'/>")
    g.append(campana(t, rev))
    # parteluces (se apartan en la revelación)
    mo = 1 - seg(t, REVELACION - 0.4, REVELACION + 0.1)
    if mo > 0.01:
        for mx in (492, 576):
            g.append(f"<rect x='{mx}' y='1128' width='12' height='98' fill='{st}' stroke='{INK}' stroke-width='4' opacity='{mo:.2f}'/>")
    # tejado y aguja
    g.append(f"<rect x='410' y='1094' width='260' height='20' rx='4' fill='{sd}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M420 1094 L478 1032 L602 1032 L660 1094 Z' fill='{SLATE}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for lx in (470, 540, 610):
        g.append(f"<path d='M{lx - 10} 1090 L{lx} 1060 L{lx + 10} 1090 Z' fill='{GOLD}' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<rect x='494' y='1004' width='92' height='30' fill='{SLATE}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M500 1006 L540 958 L580 1006 Z' fill='{SLATE}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<line x1='540' y1='962' x2='540' y2='930' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    g.append(f"<circle cx='540' cy='926' r='9' fill='{GOLD}' stroke='{INK}' stroke-width='5'/>")
    # pináculos de las esquinas
    for px in (418, 662):
        g.append(f"<path d='M{px - 14} 1096 L{px} 1040 L{px + 14} 1096 Z' fill='{GOLD}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    return "".join(g)


def paloma(t):
    # vuela desde la izquierda (fotograma 0) y se posa en el tejado del palacio derecho; huye al sonar
    if t < 2.6:
        k = seg(t, 0, 2.6)
        x = lerp(-90, 830, k); y = lerp(1060, 1556, k) - 160 * math.sin(math.pi * k)
        flap = math.sin(t * 26); fly = True
    elif t < REVELACION + 0.15:
        x, y = 830, 1556 + 2 * math.sin(t * 5); flap = 0; fly = False
    else:
        k = seg(t, REVELACION + 0.15, REVELACION + 1.6)
        x = lerp(830, 1250, k); y = lerp(1556, 1200, k); flap = math.sin(t * 30); fly = True
    look = -1 if (REVELACION - 2.2 < t < REVELACION + 0.15) else 1   # mira hacia la torre antes del golpe
    peck = 10 * max(0, math.sin(t * 4)) if (3.0 < t < 5.0) else 0
    blink = 0.15 if (t % 2.3) < 0.12 else 1
    sc = -1 if look < 0 else 1
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({sc},1)'>"]
    if not fly:
        g.append(f"<path d='M-6 26 L-8 40 M8 26 L10 40' stroke='#ff8a6a' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<path d='M-40 4 L-62 -4 L-58 16 Z' fill='#8a93a8' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='0' cy='6' rx='40' ry='26' fill='#b4bccd' stroke='{INK}' stroke-width='6'/>")
    wy = -26 * flap if fly else 0
    g.append(f"<path d='M-18 0 Q0 {-14 + wy:.0f} 26 {-4 + wy * 1.3:.0f} Q10 14 -18 10 Z' fill='#9099ad' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<g transform='translate(30,{-22 + peck:.0f})'>"
             f"<circle r='20' fill='#b4bccd' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M-14 12 Q0 22 14 12' fill='none' stroke='#6bc79a' stroke-width='6'/>"
             f"<path d='M17 -2 L32 3 L17 8 Z' fill='#ffb347' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
             f"<g transform='translate(6,-5) scale(1,{blink})'><circle r='7' fill='#fff' stroke='{INK}' stroke-width='3'/><circle cx='2' r='3.5' fill='{INK}'/></g></g>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    glow = seg(t, REVELACION - 0.15, REVELACION + 0.6)
    rev = seg(t, REVELACION, REVELACION + 0.35)
    top = mix("#5fb2ff", "#ff9a6a", glow); mid = mix("#9fd3ff", "#ffc77a", glow); low = mix("#dff2ff", "#ffe9b0", glow)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='bellglow'><stop offset='0' stop-color='#fff6c8' stop-opacity='{0.95 * glow:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffd24a' stop-opacity='{0.7 * glow:.3f}'/><stop offset='1' stop-color='#ff9a2a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sunburst'><stop offset='0' stop-color='#fff3b0' stop-opacity='{0.75 * glow:.3f}'/>"
            f"<stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nubes tranquilas arriba
    for cx, cy, sc, sp in CLOUDS:
        x = (cx + t * sp * 3) % 1400 - 160
        s.append(nube(x, cy, sc, mix("#ffffff", "#fff0d8", glow)))
    # cámara: entra subiendo (0-2,5 s) y en la revelación hace zoom al campanario
    k = seg(t, REVELACION - 0.1, REVELACION + 0.8)
    z = lerp(1.0, 2.3, k) * (1 + 0.04 * seg(t, REVELACION + 0.8, DUR))
    pan = lerp(90, 0, seg(t, 0, 2.6))
    tx = BELL_C[0]; ty = lerp(BELL_C[1] + pan, 1420, k)
    shake = 0
    for s0 in (REVELACION, REVELACION + 1.3):
        if t >= s0: shake += 7 * math.exp(-(t - s0) * 6) * math.sin((t - s0) * 70)
    s.append(f"<g transform='translate({tx + shake:.1f},{ty:.1f}) scale({z:.4f}) translate({-BELL_C[0]},{-BELL_C[1]})'>")
    s.append(f"<circle cx='{BELL_C[0]}' cy='{BELL_C[1]}' r='520' fill='url(#sunburst)'/>")
    # árboles al fondo
    for i, tx_ in enumerate(range(-40, 1140, 120)):
        sw = 4 * math.sin(t * 1.6 + i)
        s.append(f"<circle cx='{tx_ + sw:.0f}' cy='{1660 + (i % 2) * 20}' r='{70 + (i % 3) * 10}' fill='{mix('#5fb35a', '#8fbf4a', glow)}' stroke='{INK}' stroke-width='6'/>")
    s.append(palacio(-30, 390, 1560, glow))
    s.append(palacio(690, 1110, 1600, glow))
    s.append(torre(t, glow, rev))
    # muro del río
    s.append(f"<rect x='-20' y='1800' width='1120' height='50' fill='{mix('#b0905e', '#d8a868', glow)}' stroke='{INK}' stroke-width='{LW}'/>")
    for lx in range(30, 1080, 110):
        s.append(f"<rect x='{lx}' y='1770' width='12' height='34' fill='{INK}'/><circle cx='{lx + 6}' cy='1764' r='12' fill='{mix('#fff6c0', '#ffe27a', glow)}' stroke='{INK}' stroke-width='5'/>")
    # río
    s.append(f"<rect x='-20' y='1848' width='1120' height='120' fill='{mix('#3a86d4', '#e0925a', glow * 0.6)}' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(9):
        wx = (i * 140 + t * 60) % 1240 - 80
        s.append(f"<path d='M{wx:.0f} {1884 + (i % 2) * 18} q18 -10 36 0 q18 10 36 0' fill='none' stroke='#cfe9ff' stroke-width='5' stroke-linecap='round'/>")
    # barco turístico cruzando
    bx = lerp(1180, -260, t / DUR); by = 1850 + 4 * math.sin(t * 3)
    s.append(f"<g transform='translate({bx:.0f},{by:.0f})'>"
             f"<path d='M-110 -10 L110 -10 L90 22 L-96 22 Z' fill='#ff5a4f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='-80' y='-48' width='150' height='40' rx='8' fill='#fff7e8' stroke='{INK}' stroke-width='7'/>"
             + "".join(f"<rect x='{wx}' y='-40' width='22' height='18' rx='4' fill='#7fc8ff' stroke='{INK}' stroke-width='3'/>" for wx in (-66, -32, 2, 36))
             + "</g>")
    s.append(paloma(t))
    s.append("</g>")
    # ondas de sonido (en pantalla) desde la campana
    for s0 in (REVELACION, REVELACION + 0.45, REVELACION + 1.3, REVELACION + 1.75):
        if t >= s0:
            d = t - s0
            rr = 170 + d * 380
            op = clamp(1 - d / 1.5)
            if op > 0.01:
                s.append(f"<circle cx='540' cy='{ty:.0f}' r='{rr * z / 2.3:.0f}' fill='none' stroke='#fff3b0' stroke-width='{14 * op + 3:.1f}' opacity='{op * 0.9:.2f}'/>")
    # chispas doradas
    if t > REVELACION:
        d = t - REVELACION
        for dx, dy, ph in SPARK:
            px = 540 + dx * (200 + d * 260); py = ty + dy * (180 + d * 200)
            a = clamp(1 - d / 2.4) * (0.6 + 0.4 * math.sin(t * 8 + ph))
            if py > 980 and a > 0.02:
                s.append(f"<path d='M{px:.0f} {py - 14:.0f} L{px + 5:.0f} {py:.0f} L{px:.0f} {py + 14:.0f} L{px - 5:.0f} {py:.0f} Z' fill='#fff3a0' stroke='{INK}' stroke-width='2' opacity='{a:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
