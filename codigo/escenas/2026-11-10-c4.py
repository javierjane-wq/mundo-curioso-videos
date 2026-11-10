"""2026-11-10-c4 · La Torre de Pisa empezó a inclinarse en 1178, con solo 3 pisos construidos.

0-2,5 s: la torre (piso 1) en una pradera toscana; cae el piso 2 desde arriba.
2,5-5 s: cae el piso 3; la torre sonríe, recta.
5-7,4 s: el suelo blando de la derecha se agrieta y la torre tiembla, preocupada.
7,45 s (REVELACION): se hunde y se inclina de golpe, polvo, halo cálido y zoom; línea vertical de referencia.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 6

rng = np.random.default_rng(11)
BX, BY = 540, 1720           # centro de la base de la torre
MARBLE = "#f6f1e4"
SHADE = "#ddd1b6"
BAND = "#c9c3b6"
CYPRESS = [(70, 1440, 1.2), (165, 1420, 0.9), (890, 1430, 1.1), (985, 1445, 1.35), (300, 1410, 0.7)]
HOUSES = [(215, 1400, 1.0), (780, 1395, 0.9), (690, 1410, 0.75)]
FLOWERS = [(rng.uniform(20, 1060), rng.uniform(1560, 1900), rng.choice(["#ff6b8a", "#ffd23f", "#ffffff", "#b07cff"]),
            rng.uniform(0, 6.28)) for _ in range(46)]
DUSTP = [(rng.uniform(-1, 1), rng.uniform(0.4, 1.0), rng.uniform(18, 40)) for _ in range(16)]


def cloud(x, y, s, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s})'>"
            f"<path d='M0 50 Q-10 0 45 5 Q70 -40 125 -10 Q170 -35 200 15 Q250 15 240 50 Z' fill='{col}' "
            f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def bird(x, y, t, ph):
    f = 14 * math.sin(t * 9 + ph)
    return (f"<path d='M{x-26:.0f} {y-f:.0f} Q{x-12:.0f} {y-8:.0f} {x:.0f} {y:.0f} Q{x+12:.0f} {y-8:.0f} {x+26:.0f} {y-f:.0f}' "
            f"fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")


def ledge(y, hw):
    return (f"<rect x='{-hw}' y='{y - 11}' width='{2*hw}' height='22' rx='6' fill='{MARBLE}' stroke='{INK}' stroke-width='7'/>"
            f"<line x1='{-hw+8}' y1='{y+4}' x2='{hw-8}' y2='{y+4}' stroke='{BAND}' stroke-width='4'/>")


def gallery(y0, h):
    """Piso con galería de columnas y arcos (local: base en y0, altura h)."""
    hw = 150
    top = y0 - h
    g = [f"<rect x='{-hw}' y='{top}' width='{2*hw}' height='{h}' fill='{MARBLE}' stroke='{INK}' stroke-width='{LW}'/>"]
    # bandas grises del mármol
    for yy in (top + 22, y0 - 26):
        g.append(f"<line x1='{-hw+6}' y1='{yy}' x2='{hw-6}' y2='{yy}' stroke='{BAND}' stroke-width='5'/>")
    # arcos abiertos (interior en sombra)
    n = 5; cw = 2 * hw / n
    for i in range(n):
        ax = -hw + i * cw + 9; aw = cw - 18; ab = y0 - 34; at = top + 40 + aw / 2
        g.append(f"<path d='M{ax:.1f} {ab} L{ax:.1f} {at:.1f} A{aw/2:.1f} {aw/2:.1f} 0 0 1 {ax+aw:.1f} {at:.1f} L{ax+aw:.1f} {ab} Z' "
                 f"fill='#8c7a63' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<path d='M{ax+aw*0.55:.1f} {ab} L{ax+aw*0.55:.1f} {at:.1f} A{aw*0.45:.1f} {aw*0.45:.1f} 0 0 1 {ax+aw:.1f} {at-aw*0.25:.1f} L{ax+aw:.1f} {ab} Z' "
                 f"fill='#6d5d4a' opacity='0.6'/>")
    # columnas delanteras
    for i in range(n + 1):
        cx = -hw + i * cw
        if i in (0, n): continue
        g.append(f"<rect x='{cx-7:.1f}' y='{top+34}' width='14' height='{h-68}' fill='{MARBLE}' stroke='{INK}' stroke-width='5'/>")
        g.append(f"<rect x='{cx-12:.1f}' y='{top+30}' width='24' height='10' rx='3' fill='{MARBLE}' stroke='{INK}' stroke-width='4'/>")
    # sombra lateral para dar volumen de cilindro
    g.append(f"<rect x='{hw-38}' y='{top+4}' width='34' height='{h-8}' fill='#000' opacity='0.08'/>")
    g.append(ledge(y0, hw + 14))
    g.append(ledge(top, hw + 18))
    return "".join(g)


def ground_floor(t, worry, shock):
    """Piso 1 con cara (local: base y=0, alto 220)."""
    hw = 160; h = 220
    g = [f"<rect x='{-hw}' y='{-h}' width='{2*hw}' height='{h}' fill='{MARBLE}' stroke='{INK}' stroke-width='{LW}'/>"]
    g.append(f"<line x1='{-hw+6}' y1='{-h+24}' x2='{hw-6}' y2='{-h+24}' stroke='{BAND}' stroke-width='5'/>")
    # arcos ciegos y puerta
    for ax, aw, col in ((-148, 50, SHADE), (-90, 50, SHADE), (40, 50, SHADE), (98, 50, SHADE)):
        g.append(f"<path d='M{ax} 0 L{ax} -60 A{aw/2} {aw/2} 0 0 1 {ax+aw} -60 L{ax+aw} 0' fill='{col}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-34 0 L-34 -62 A34 34 0 0 1 34 -62 L34 0 Z' fill='#5b4636' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<line x1='0' y1='-94' x2='0' y2='0' stroke='{INK}' stroke-width='5'/>")
    # cara
    blink = 0.12 if (((t + 1.3) % 2.9) < 0.12 and not 7.2 < t < 8.2) or abs(t - 4.2) < 0.06 else 1.0
    er = 30 + 10 * shock
    look_x = lerp(0, 9, worry) - 4 * shock
    look_y = lerp(0, 8, worry) + 2 * shock
    for ex in (-56, 56):
        g.append(f"<g transform='translate({ex},-158) scale(1,{blink})'>"
                 f"<ellipse rx='{er*0.85:.1f}' ry='{er:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='{look_x:.1f}' cy='{look_y:.1f}' r='{15 - 3*shock:.1f}' fill='{INK}'/>"
                 f"<circle cx='{look_x-5:.1f}' cy='{look_y-6:.1f}' r='5' fill='#fff'/></g>")
    # cejas (preocupación)
    tilt = 16 * worry
    for ex, sg in ((-56, 1), (56, -1)):
        g.append(f"<line x1='{ex-24}' y1='{-200 - 6*shock + sg*tilt*0.6:.1f}' x2='{ex+24}' y2='{-200 - 6*shock - sg*tilt*0.6:.1f}' "
                 f"stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # mejillas
    for ex in (-104, 104):
        g.append(f"<ellipse cx='{ex}' cy='-124' rx='18' ry='10' fill='#ff9aa8' opacity='{0.7*(1-worry*0.6):.2f}'/>")
    # boca: sonrisa -> línea ondulada -> "O"
    if shock > 0.05:
        g.append(f"<ellipse cx='0' cy='-114' rx='{12+8*shock:.1f}' ry='{10+14*shock:.1f}' fill='#7a2e2e' stroke='{INK}' stroke-width='6'/>")
    elif worry > 0.3:
        g.append(f"<path d='M-26 -112 Q-13 -122 0 -112 Q13 -102 26 -112' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        g.append(f"<path d='M-28 -120 Q0 -92 28 -120' fill='#7a2e2e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<rect x='{hw-40}' y='{-h+4}' width='36' height='{h-8}' fill='#000' opacity='0.08'/>")
    g.append(ledge(-h, hw + 18))
    return "".join(g)


def tower(t):
    worry = seg(t, 5.0, 5.8)
    shock = seg(t, 7.45, 7.75)
    # caída de los pisos 2 y 3 (con pequeño aplastamiento al llegar)
    d2 = (1 - seg(t, 0, 1.15) ** 2) * -620 if t < 1.15 else 0
    d3 = (1 - clamp(t - 2.6) ** 2) * -900 if t < 3.6 else 0
    sq = 0
    for land in (1.15, 3.6):
        if land <= t < land + 0.35: sq = max(sq, math.sin(math.pi * (t - land) / 0.35))
    # inclinación: temblor 5-7,4 s y caída a 8,5° en la revelación
    tremble = 1.8 * math.sin(t * 38) * seg(t, 5.2, 5.6) * (1 - seg(t, 7.3, 7.45))
    ang = lerp(0, 2.2, seg(t, 5.4, 7.3)) + tremble + lerp(0, 6.3, seg(t, 7.45, 8.1))
    ang += 0.8 * math.sin((t - 8.1) * 9) * math.exp(-(t - 8.1) * 3) if t > 8.1 else 0
    sink = lerp(0, 10, seg(t, 5.4, 7.3)) + lerp(0, 22, seg(t, 7.45, 8.1))
    g = [f"<g transform='translate({BX},{BY + sink*0.3:.1f}) translate(-160,0) rotate({ang:.2f}) translate(160,0) scale({1+0.03*sq:.3f},{1-0.04*sq:.3f})'>"]
    g.append(ground_floor(t, worry, shock))
    if t >= 2.6:
        g.append(f"<g transform='translate(0,{d3:.1f})'>{gallery(-380, 160)}</g>")
    g.append(f"<g transform='translate(0,{d2:.1f})'>{gallery(-220, 160)}</g>")
    # piedras sin terminar arriba del piso 3
    if t > 3.6:
        k = seg(t, 3.7, 4.2)
        for i, (sx, sw) in enumerate(((-120, 70), (-30, 60), (60, 75))):
            g.append(f"<rect x='{sx}' y='{-572 - 26*k:.1f}' width='{sw}' height='{26*k:.1f}' rx='4' fill='#e8e1cf' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g), ang


def frame(t):
    rev = seg(t, 7.45, 8.3)
    top = mix("#58b8f5", "#ffb45e", rev * 0.85); low = mix("#c4ecff", "#ffe6a8", rev)
    shake = 7 * math.sin(t * 70) * math.exp(-(t - 7.45) * 6) if t > 7.45 else 0
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#fff6c8' stop-opacity='{0.95*rev:.3f}'/>"
         f"<stop offset='0.45' stop-color='#ffd36b' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ff9a3c' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, 7.45, 9.6)
    body = []
    # sol suave y nubes
    body.append(f"<circle cx='965' cy='930' r='{58 + 4*math.sin(t*2):.1f}' fill='#fff4b0' stroke='#ffc94a' stroke-width='8' opacity='0.95'/>")
    for i, (cx, cy, sc) in enumerate([(120, 520, 1.1), (700, 850, 0.9), (400, 330, 0.8), (980, 1040, 0.7)]):
        dx = (t * 18 * (1 + 0.35 * i)) % 1500 - 300
        body.append(cloud((cx + dx) % 1500 - 260, cy, sc, mix("#ffffff", "#fff0d6", rev)))
    # halo de la revelación detrás de la torre
    body.append(f"<circle cx='{BX+60}' cy='1350' r='{lerp(150, 720, rev):.0f}' fill='url(#halo)'/>")
    # colinas lejanas, casitas y cipreses
    body.append(f"<path d='M0 1330 Q180 1250 380 1310 Q600 1230 820 1300 Q960 1260 1080 1290 L1080 1500 L0 1500 Z' fill='{mix('#8fc97a', '#b8c96a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M0 1420 Q240 1350 520 1410 Q800 1360 1080 1400 L1080 1520 L0 1520 Z' fill='{mix('#6fb85c', '#98b84f', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for hx, hy, sc in HOUSES:
        body.append(f"<g transform='translate({hx},{hy}) scale({sc})'><rect x='-40' y='-50' width='80' height='50' fill='#f3d9a6' stroke='{INK}' stroke-width='6'/>"
                    f"<path d='M-50 -48 L0 -82 L50 -48 Z' fill='#d9603b' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                    f"<rect x='-12' y='-34' width='20' height='20' fill='#7a5a3a'/></g>")
    for cx, cy, sc in CYPRESS:
        sw = 3 * math.sin(t * 1.6 + cx)
        body.append(f"<g transform='translate({cx},{cy}) scale({sc}) rotate({sw:.1f})'>"
                    f"<rect x='-6' y='-14' width='12' height='18' fill='#6b4a2e' stroke='{INK}' stroke-width='5'/>"
                    f"<path d='M0 -190 Q34 -100 26 -14 L-26 -14 Q-34 -100 0 -190 Z' fill='#2f7a45' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # pradera y plaza
    body.append(f"<path d='M0 1500 Q300 1470 540 1490 Q800 1505 1080 1480 L1080 1920 L0 1920 Z' fill='{mix('#82d06a', '#a6cf5e', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<ellipse cx='{BX}' cy='{BY}' rx='330' ry='74' fill='#e9dcc0' stroke='{INK}' stroke-width='{LW}'/>")
    # suelo blando que se agrieta y se hunde (derecha)
    mud = seg(t, 5.2, 7.3) * 0.6 + 0.4 * rev
    if mud > 0:
        body.append(f"<ellipse cx='{BX+150}' cy='{BY+6}' rx='{lerp(30, 170, mud):.0f}' ry='{lerp(10, 44, mud):.0f}' fill='#8a6a48' opacity='{min(1, mud*1.4):.2f}'/>")
        cr = seg(t, 5.3, 6.6)
        body.append(f"<path d='M{BX+120} {BY+30} L{BX+150} {BY+50} L{BX+140} {BY+64} L{BX+175} {BY+80}' fill='none' stroke='{INK}' stroke-width='6' "
                    f"stroke-dasharray='{120*cr:.0f} 400' stroke-linecap='round'/>")
        body.append(f"<path d='M{BX+200} {BY+20} L{BX+240} {BY+38} L{BX+262} {BY+30}' fill='none' stroke='{INK}' stroke-width='6' "
                    f"stroke-dasharray='{90*cr:.0f} 400' stroke-linecap='round'/>")
    # sombra de la torre
    body.append(f"<ellipse cx='{BX+30 + 60*rev:.0f}' cy='{BY+8}' rx='200' ry='24' fill='#000' opacity='0.18'/>")
    # línea vertical de referencia (lo recta que debería estar)
    tw, ang = tower(t)
    body.append(tw)
    if rev > 0:
        lx = BX - 178
        body.append(f"<line x1='{lx}' y1='{BY-10}' x2='{lx}' y2='{BY - 10 - 640*rev:.0f}' stroke='{INK}' stroke-width='15' "
                    f"stroke-dasharray='30 22' stroke-linecap='round' opacity='0.8'/>")
        body.append(f"<line x1='{lx}' y1='{BY-10}' x2='{lx}' y2='{BY - 10 - 640*rev:.0f}' stroke='#ffffff' stroke-width='8' "
                    f"stroke-dasharray='30 22' stroke-linecap='round'/>")
    # borde delantero de la plaza (tapa la base que se hunde)
    body.append(f"<path d='M{BX-330} {BY} A330 74 0 0 0 {BX+330} {BY} L{BX+330} {BY+4} Q{BX+300} {BY+92} {BX} {BY+96} Q{BX-300} {BY+92} {BX-330} {BY+4} Z' "
                f"fill='#ddcda9' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M{BX-330} {BY} A330 74 0 0 0 {BX+330} {BY}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # polvo de la revelación
    if t > 7.45:
        k = clamp((t - 7.45) / 1.6)
        for dx, dy, r in DUSTP:
            px = BX + 170 + dx * 260 * k; py = BY - 10 - dy * 160 * k
            body.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{r*(0.6+k):.0f}' fill='#f1e2c2' stroke='{INK}' stroke-width='4' opacity='{(1-k)*0.9:.2f}'/>")
    # flores que se mecen
    for fx, fy, col, ph in FLOWERS:
        if abs(fx - BX) < 350 and fy < BY + 110: continue
        sw = 6 * math.sin(t * 2.4 + ph)
        body.append(f"<line x1='{fx:.0f}' y1='{fy:.0f}' x2='{fx+sw:.0f}' y2='{fy-26:.0f}' stroke='#3f8a35' stroke-width='5'/>"
                    f"<circle cx='{fx+sw:.0f}' cy='{fy-30:.0f}' r='11' fill='{col}' stroke='{INK}' stroke-width='4'/>"
                    f"<circle cx='{fx+sw:.0f}' cy='{fy-30:.0f}' r='4' fill='#ffb000'/>")
    # pájaros cruzando
    for i, (by, sp, ph) in enumerate(((1090, 95, 0), (1150, 80, 1.7), (1040, 110, 3.1))):
        bx = (t * sp + i * 380) % 1300 - 110
        body.append(bird(bx, by + 10 * math.sin(t * 2 + ph), t, ph))
    s.append(f"<g transform='translate({shake:.1f},0)'>" + zoom(BX, 1450, z, "".join(body)) + "</g>")
    s.append("</svg>")
    return "".join(s)
