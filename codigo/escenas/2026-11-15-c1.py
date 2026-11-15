"""Una nube de algodón pesa como 100 elefantes (cúmulo: unas 500 toneladas, USGS / NCAR).

0-2,5 s  una nube sonriente entra flotando sobre la sabana
2,5-5 s  flota ligera, pájaros y nubecillas pasan
5-7,5 s  entran tres elefantes caminando por debajo
7,5 s    REVELACIÓN: la nube se hincha y brilla, aparece una manada entera de elefantes (zoom)
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.5   # aparece la manada: golpe musical
MUSICA = 4

rng = np.random.default_rng(15)
GRASS = [(rng.uniform(0, W), rng.uniform(1420, 1910), rng.uniform(0.7, 1.3), rng.uniform(0, 6.28)) for _ in range(55)]
DROPS = [(rng.uniform(-230, 230), rng.uniform(0, 1), rng.uniform(7, 12)) for _ in range(22)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(330, 470), rng.uniform(4, 9), rng.uniform(0, 6.28)) for _ in range(26)]

# bolas que forman la nube (cx, cy, r) alrededor de (0,0)
PUFFS = [(-250, 40, 95), (-150, -30, 125), (-20, -85, 150), (130, -40, 130), (250, 30, 100),
         (-120, 60, 110), (60, 60, 120), (180, 70, 95), (-230, 80, 70), (0, 40, 130)]

PIEL = "#8f96a3"; PIEL_OSC = "#737a88"; OREJA = "#7b8291"


def nube(t, cx, cy, sc, rev):
    blink = 0.12 if (t % 2.9) < 0.13 else 1.0
    body = mix("#ffffff", "#e9f1ff", rev)
    shade = mix("#d7e6f7", "#b9cbe6", rev)
    g = [f"<g transform='translate({cx:.1f},{cy:.1f}) scale({sc:.4f})'>"]
    g.append("<ellipse cx='0' cy='190' rx='300' ry='22' fill='#000' opacity='0.0'/>")
    for x, y, r in PUFFS:                      # contorno exterior único
        g.append(f"<circle cx='{x}' cy='{y}' r='{r + LW / 2:.1f}' fill='{INK}'/>")
    g.append(f"<rect x='-262' y='60' width='524' height='{110 + LW / 2:.0f}' rx='55' fill='{INK}'/>")
    for x, y, r in PUFFS:
        g.append(f"<circle cx='{x}' cy='{y}' r='{r - LW / 2:.1f}' fill='{body}'/>")
    g.append(f"<rect x='-257' y='60' width='514' height='{110 - LW / 2:.0f}' rx='50' fill='{body}'/>")
    # sombra inferior suave
    g.append(f"<path d='M-240 120 Q0 175 240 120 L240 140 Q238 160 205 163 L-205 163 Q-238 160 -240 140 Z' fill='{shade}'/>")
    # brillo
    g.append("<ellipse cx='-60' cy='-150' rx='60' ry='26' fill='#fff' opacity='0.9' transform='rotate(-15 -60 -150)'/>")
    # cara
    eye_r = lerp(26, 33, rev)
    look = 10 * math.sin(t * 0.9) if rev < 0.5 else lerp(0, 0, rev)
    for ex in (-70, 70):
        g.append(f"<g transform='translate({ex},20) scale(1,{blink})'>"
                 f"<ellipse rx='{eye_r:.1f}' ry='{eye_r * 1.18:.1f}' fill='{INK}'/>"
                 f"<circle cx='{look - 8:.1f}' cy='{-eye_r * 0.45:.1f}' r='{eye_r * 0.38:.1f}' fill='#fff'/>"
                 f"<circle cx='{look + 9:.1f}' cy='{eye_r * 0.35:.1f}' r='{eye_r * 0.16:.1f}' fill='#fff'/></g>")
    # mofletes
    for ex in (-130, 130):
        g.append(f"<ellipse cx='{ex}' cy='75' rx='30' ry='17' fill='#ff9db3' opacity='0.75'/>")
    # boca: sonrisa -> "¡oh!" en la revelación
    if rev < 0.5:
        g.append(f"<path d='M-38 78 Q0 118 38 78' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='98' rx='22' ry='{lerp(10, 28, rev):.1f}' fill='#7a2a3a' stroke='{INK}' stroke-width='7'/>")
    g.append("</g>")
    return "".join(g)


def elefante(x, y, s, t, fase, andando=True, op=1.0):
    """Elefante original de perfil mirando a la derecha. (x,y) = punto de las patas en el suelo."""
    sw = 16 * math.sin(t * 7 + fase) if andando else 3 * math.sin(t * 2 + fase)
    bob = (4 * abs(math.sin(t * 7 + fase))) if andando else 0
    oreja = 6 * math.sin(t * 3.1 + fase)
    trompa = 10 * math.sin(t * 2.3 + fase)
    blink = 0.15 if ((t + fase) % 3.3) < 0.13 else 1.0
    g = [f"<g transform='translate({x:.1f},{y - bob * s:.1f}) scale({s:.4f})' opacity='{op:.3f}'>"]
    g.append("<ellipse cx='20' cy='4' rx='170' ry='16' fill='#000' opacity='0.18'/>")
    # patas (las del fondo más oscuras)
    for lx, ang, col in ((-80, -sw, PIEL_OSC), (70, sw, PIEL_OSC), (-40, sw, PIEL), (110, -sw, PIEL)):
        g.append(f"<g transform='translate({lx},-110) rotate({ang:.1f})'>"
                 f"<rect x='-24' y='0' width='48' height='112' rx='14' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M-16 104 L-16 96 M0 104 L0 96 M16 104 L16 96' stroke='#e9e2d0' stroke-width='7' stroke-linecap='round'/></g>")
    # cola
    g.append(f"<path d='M-128 -165 Q-160 -130 -150 -85' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>"
             f"<path d='M-150 -92 L-160 -70 L-140 -74 Z' fill='{INK}'/>")
    # cuerpo
    g.append(f"<ellipse cx='10' cy='-165' rx='145' ry='92' fill='{PIEL}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append("<path d='M-70 -230 Q10 -262 90 -232' fill='none' stroke='#a8afba' stroke-width='10' stroke-linecap='round'/>")
    # trompa (detrás de la cabeza para que salga de ella)
    tx, ty = 215 + trompa * 0.5, -45
    g.append(f"<path d='M165 -175 Q222 -150 {tx:.1f} {ty + 40:.1f} Q{tx + 4:.1f} {ty + 62:.1f} {tx + 22:.1f} {ty + 52:.1f}' "
             f"fill='none' stroke='{INK}' stroke-width='{38 + 2 * LW}' stroke-linecap='round'/>")
    g.append(f"<path d='M165 -175 Q222 -150 {tx:.1f} {ty + 40:.1f} Q{tx + 4:.1f} {ty + 62:.1f} {tx + 22:.1f} {ty + 52:.1f}' "
             f"fill='none' stroke='{PIEL}' stroke-width='38' stroke-linecap='round'/>")
    # cabeza
    g.append(f"<circle cx='150' cy='-205' r='68' fill='{PIEL}' stroke='{INK}' stroke-width='{LW}'/>")
    # colmillo
    g.append(f"<path d='M178 -150 Q205 -128 228 -140' fill='none' stroke='{INK}' stroke-width='{18 + 2 * 6}' stroke-linecap='round'/>"
             f"<path d='M178 -150 Q205 -128 228 -140' fill='none' stroke='#fbf6e8' stroke-width='18' stroke-linecap='round'/>")
    # oreja
    g.append(f"<g transform='translate(112,-205) rotate({oreja:.1f})'>"
             f"<path d='M0 -62 Q-70 -70 -72 0 Q-70 70 -5 72 Q20 40 10 0 Q20 -40 0 -62 Z' fill='{OREJA}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             "<path d='M-12 -40 Q-50 -40 -50 0 Q-50 40 -14 48' fill='none' stroke='#c99aa8' stroke-width='10' stroke-linecap='round'/></g>")
    # ojo
    g.append(f"<g transform='translate(175,-222) scale(1,{blink})'><ellipse rx='11' ry='14' fill='{INK}'/>"
             "<circle cx='-3' cy='-5' r='4.5' fill='#fff'/></g>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    # cielo
    top = mix("#5fb4ff", "#4aa3ff", rev); mid = mix("#9fd6ff", "#a8dcff", rev); low = mix("#dff4ff", "#fff1c9", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff8d6' stop-opacity='{0.95 * rev:.3f}'/>"
            f"<stop offset='0.45' stop-color='#ffe07a' stop-opacity='{0.55 * rev:.3f}'/>"
            "<stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    c = []
    # nubecillas lejanas (lentas, arriba poco contraste)
    for i, (y0, sc, v) in enumerate(((620, 0.6, 18), (860, 0.45, 26), (380, 0.5, 12))):
        x0 = (150 + i * 380 - t * v) % 1400 - 200
        c.append(f"<g transform='translate({x0:.0f},{y0}) scale({sc})' opacity='0.55'>"
                 "<path d='M0 60 Q0 10 50 18 Q70 -30 130 -10 Q170 -40 210 5 Q260 10 255 60 Z' fill='#ffffff'/></g>")
    cx = lerp(1100, 540, seg(t, 0, 2.3)) + 14 * math.sin(t * 0.8)
    cy = 1120 + 14 * math.sin(t * 1.6)
    c.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{lerp(300, 560, rev):.0f}' fill='url(#halo)'/>")
    # colinas y suelo
    h1 = mix("#8fd06b", "#9bd86f", rev); h2 = mix("#6fbf4f", "#7ccb55", rev); g3 = mix("#5fae3f", "#6aba46", rev)
    c.append(f"<path d='M0 1330 Q180 1250 380 1310 T760 1290 T1080 1300 L1080 1920 L0 1920 Z' fill='{h1}' stroke='{INK}' stroke-width='{LW}'/>")
    # acacia lejana
    c.append(f"<g transform='translate(890,1310)'><path d='M0 0 L6 -110 M6 -90 L-40 -140 M6 -95 L50 -150' stroke='{INK}' stroke-width='12' stroke-linecap='round' fill='none'/>"
             f"<path d='M-110 -140 Q-90 -200 0 -190 Q90 -210 120 -150 Q60 -125 0 -132 Q-60 -122 -110 -140 Z' fill='#4e9a3a' stroke='{INK}' stroke-width='7'/></g>")
    c.append(f"<path d='M0 1440 Q270 1380 560 1430 T1080 1420 L1080 1920 L0 1920 Z' fill='{h2}' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(f"<path d='M0 1600 Q300 1550 640 1590 T1080 1580 L1080 1920 L0 1920 Z' fill='{g3}' stroke='{INK}' stroke-width='{LW}'/>")
    # hierba que se mece
    for gx, gy, gs, ph in GRASS:
        b = 8 * math.sin(t * 2.2 + ph)
        c.append(f"<path d='M{gx:.0f} {gy:.0f} q{-6 + b:.1f} {-26 * gs:.1f} {-10 + b:.1f} {-40 * gs:.1f} M{gx:.0f} {gy:.0f} q{6 + b:.1f} {-24 * gs:.1f} {14 + b:.1f} {-34 * gs:.1f}' "
                 "stroke='#3f8a2e' stroke-width='6' stroke-linecap='round' fill='none'/>")
    # manada que aparece en la revelación (filas del fondo)
    for i, x in enumerate((110, 290, 470, 650, 830, 1010)):
        k = rebote(t, REVELACION + 0.05 * i, 0.45)
        if k > 0: c.append(elefante(x - 40, 1455, 0.36 * k, t, i * 0.9, andando=False))
    for i, x in enumerate((60, 300, 540, 780, 1020)):
        k = rebote(t, REVELACION + 0.12 + 0.06 * i, 0.45)
        if k > 0: c.append(elefante(x - 50, 1575, 0.52 * k, t, i * 1.3 + 0.4, andando=False))
    # tres elefantes que entran caminando
    for i, (xf, a) in enumerate(((150, 4.3), (480, 4.7), (810, 5.1))):
        k = seg(t, a, a + 1.6)
        if t > a - 0.05:
            walk = t < a + 1.65
            c.append(elefante(lerp(-330, xf, k), 1830, 0.82, t, i * 1.7, andando=walk))
    # pájaros
    for i in range(3):
        bx = (t * 120 + i * 90) % 1500 - 250
        by = 1010 + i * 34 + 10 * math.sin(t * 3 + i)
        fl = 14 * math.sin(t * 12 + i)
        c.append(f"<path d='M{bx:.0f} {by:.0f} q14 {-12 - fl:.1f} 28 0 q14 {-12 - fl:.1f} 28 0' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # nube protagonista: entra desde la derecha, flota
    sc = lerp(1.05, 1.16, rev) * (1 + 0.03 * math.sin(t * 2.4))
    # destellos alrededor en la revelación
    if rev > 0:
        for a, r, sr, ph in SPARK:
            al = rev * (0.5 + 0.5 * math.sin(t * 6 + ph))
            px, py = cx + r * math.cos(a + t * 0.3), cy + 0.6 * r * math.sin(a + t * 0.3)
            c.append(f"<path d='M{px:.0f} {py - sr * 2:.0f} L{px + sr * 0.5:.0f} {py:.0f} L{px:.0f} {py + sr * 2:.0f} L{px - sr * 0.5:.0f} {py:.0f} Z' fill='#fff7c2' opacity='{al:.2f}'/>")
    # gotitas que caen (la nube es agua)
    if t > REVELACION:
        for dx, ph, dr in DROPS:
            p = ((t - REVELACION) * 0.9 + ph) % 1.0
            yy = cy + 150 + p * 260
            c.append(f"<path d='M{cx + dx:.0f} {yy - dr * 1.6:.0f} Q{cx + dx + dr:.0f} {yy:.0f} {cx + dx:.0f} {yy + dr:.0f} Q{cx + dx - dr:.0f} {yy:.0f} {cx + dx:.0f} {yy - dr * 1.6:.0f} Z' "
                     f"fill='#5ec8ff' stroke='{INK}' stroke-width='3' opacity='{(1 - p) * rev:.2f}'/>")
    c.append(nube(t, cx, cy, sc, rev))
    z = 1 + 0.10 * seg(t, REVELACION - 0.1, DUR)
    s.append(zoom(540, 1080, z, "".join(c)))
    s.append("</svg>")
    return "".join(s)
