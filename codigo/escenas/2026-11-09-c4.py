"""2026-11-09-c4 · Tierra: el volcán Paricutín (México) nació en 1943 en el maizal de un campesino
(Dionisio Pulido) y en su primer año creció 336 m.

0-2,5 s  un maizal tranquilo por la mañana; un campesino original entra desde la derecha y en el
         suelo se abre una grieta que echa humo.
2,5-5 s  del suelo sale un montículo que humea cada vez más.
5-7,5 s  tensión: tiembla la tierra, el montículo crece, abre los ojos y brilla por dentro.
7,5-10 s REVELACION: el volcán se hace enorme y entra en erupción: cielo rojo, lava, zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 4

VX, BASE = 540, 1500        # centro y base del volcán
rng = np.random.default_rng(23)
CLOUDS = [(120, 560, 1.2, 9), (760, 400, 1.0, 13), (420, 760, 0.8, 7), (980, 680, 0.9, 11)]
SMOKE = [(rng.uniform(-3.0, 0), rng.uniform(-30, 30), rng.uniform(0.7, 1.3)) for _ in range(14)]
LAVA = [(rng.uniform(0, 0.9), rng.uniform(-260, 260), rng.uniform(380, 560), rng.uniform(14, 26)) for _ in range(26)]
DUST = [(rng.uniform(0, W), rng.uniform(1450, 1900), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(30)]
# maíz en el campo (lejos y cerca): x, y, escala, fase
MID_CORN = [(x, 1450 + 18 * (i % 2), 0.42, i * 0.7) for i, x in enumerate(range(40, 1080, 85)) if abs(x - VX) > 150]
ROW2 = [(x, 1560, 0.55, i * 0.9) for i, x in enumerate(range(10, 1080, 120)) if abs(x - VX) > 260]
FRONT = [(70, 1900, 1.15, 0.0), (250, 1940, 1.0, 1.3), (1030, 1930, 1.05, 2.1)]


def altura(t):
    """Altura del volcán en px."""
    h = lerp(0, 70, seg(t, 2.4, 5.0))
    h = lerp(h, 190, seg(t, 5.0, 7.3))
    return lerp(h, 440, seg(t, 7.4, 8.3))


def corn(x, y, s, sway, dark=0.0):
    st = mix("#4caf3e", "#2f5a2a", dark); lf = mix("#6fd04c", "#3c6e30", dark)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f}) rotate({sway:.2f})'>"]
    g.append(f"<path d='M0 0 Q-6 -170 4 -340' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>")
    g.append(f"<path d='M0 0 Q-6 -170 4 -340' fill='none' stroke='{st}' stroke-width='14' stroke-linecap='round'/>")
    for ly, d in ((-70, 1), (-130, -1), (-200, 1), (-260, -1)):
        g.append(f"<path d='M0 {ly} Q{d*70} {ly-60} {d*130} {ly+10} Q{d*70} {ly-25} 0 {ly+12} Z' fill='{lf}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # mazorca
    g.append(f"<g transform='translate(10,-165) rotate(18)'><ellipse cx='16' cy='0' rx='17' ry='42' fill='{mix('#ffd23f', '#a88a2a', dark)}' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M0 40 Q-6 0 10 -38 Q16 0 28 38 Z' fill='{lf}' stroke='{INK}' stroke-width='5'/></g>")
    # penacho
    for a in (-30, -10, 12, 32):
        g.append(f"<line x1='4' y1='-340' x2='{4+60*math.sin(math.radians(a)):.0f}' y2='{-340-55*math.cos(math.radians(a)):.0f}' stroke='{INK}' stroke-width='11' stroke-linecap='round'/>"
                 f"<line x1='4' y1='-340' x2='{4+60*math.sin(math.radians(a)):.0f}' y2='{-340-55*math.cos(math.radians(a)):.0f}' stroke='{mix('#e8c36a', '#8a6a2a', dark)}' stroke-width='5' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def farmer(t, rev):
    """Campesino original: sombrero de paja, sarape rojo con rayas, bigote."""
    x = lerp(1060, 800, seg(t, 0, 1.6))
    walk = t < 1.7
    bob = 7 * abs(math.sin(t * 9)) if walk else 3 * math.sin(t * 2.5)
    jump = -60 * math.sin(math.pi * seg(t, 7.45, 8.0))
    hat = -70 * math.sin(math.pi * seg(t, 7.45, 8.4))
    blink = 1.0 if (t % 2.7) > 0.12 else 0.15
    eye = lerp(1.0, 1.5, rev)
    g = [f"<g transform='translate({x:.1f},{1700 - bob + jump:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='{175 - jump:.0f}' rx='110' ry='18' fill='#000' opacity='0.22'/>")
    # piernas
    sw = 18 * math.sin(t * 9) if walk else 0
    for lx, d in ((-30, 1), (30, -1)):
        g.append(f"<g transform='translate({lx},40) rotate({d*sw:.1f})'><rect x='-20' y='0' width='40' height='120' rx='14' fill='#f4efe2' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<ellipse cx='-8' cy='128' rx='32' ry='14' fill='#8a5a33' stroke='{INK}' stroke-width='7'/></g>")
    # brazos (se levantan en la revelación)
    up = rev
    for d in (-1, 1):
        ang = lerp(d * 14, d * 150, up)
        g.append(f"<g transform='translate({d*62},-70) rotate({ang:.1f})'><rect x='-17' y='-4' width='34' height='110' rx='16' fill='#f4efe2' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='0' cy='112' r='20' fill='#c98a5a' stroke='{INK}' stroke-width='7'/></g>")
    # cuerpo con sarape
    g.append(f"<path d='M-78 -90 Q0 -120 78 -90 L92 50 Q0 70 -92 50 Z' fill='#d8343a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for yy, c in ((-40, '#ffd23f'), (-15, '#2e8b57'), (10, '#ffd23f')):
        g.append(f"<path d='M-86 {yy} Q0 {yy+14} 86 {yy}' fill='none' stroke='{c}' stroke-width='10'/>")
    # cabeza
    g.append(f"<circle cx='0' cy='-150' r='62' fill='#c98a5a' stroke='{INK}' stroke-width='{LW}'/>")
    for ex in (-34, 4):
        g.append(f"<g transform='translate({ex},-162) scale({eye:.2f},{blink*eye:.2f})'><ellipse rx='11' ry='14' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='-3' cy='1' r='6' fill='{INK}'/></g>")
    g.append(f"<path d='M-46 -128 Q-28 -140 -14 -126 Q0 -140 16 -128 Q0 -110 -14 -118 Q-30 -108 -46 -128 Z' fill='#3b2418' stroke='{INK}' stroke-width='4'/>")
    mo = lerp(4, 18, rev)
    g.append(f"<ellipse cx='-15' cy='-106' rx='{lerp(10, 14, rev):.0f}' ry='{mo:.0f}' fill='#6a1f1f' stroke='{INK}' stroke-width='5'/>")
    # sombrero
    g.append(f"<g transform='translate(0,{-200 + hat:.1f}) rotate({lerp(-6, 12, rev):.1f})'>"
             f"<ellipse cx='0' cy='0' rx='130' ry='30' fill='#e8c36a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-55 -4 Q-50 -80 0 -86 Q50 -80 55 -4 Z' fill='#f2d27e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M-54 -18 Q0 -6 54 -18' fill='none' stroke='#d8343a' stroke-width='12'/></g>")
    g.append("</g>")
    return "".join(g)


def volcano(t, h, rev, heat):
    if h < 2:
        return ""
    bw = 60 + h * 1.25; cw = 22 + h * 0.2; top = BASE - h
    body = mix("#7a5442", "#4a2f2a", rev)
    g = []
    g.append(f"<ellipse cx='{VX}' cy='{BASE+10}' rx='{bw+40:.0f}' ry='{18+h*0.05:.0f}' fill='#000' opacity='0.2'/>")
    g.append(f"<path d='M{VX-bw:.0f} {BASE} Q{VX-cw-h*0.25:.0f} {top+h*0.35:.0f} {VX-cw:.0f} {top:.0f} "
             f"Q{VX:.0f} {top+14:.0f} {VX+cw:.0f} {top:.0f} Q{VX+cw+h*0.25:.0f} {top+h*0.35:.0f} {VX+bw:.0f} {BASE} Z' "
             f"fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # vetas de roca
    for k, d in ((0.35, -1), (0.55, 1), (0.75, -1)):
        yy = top + h * k; xx = VX + d * (cw + (bw - cw) * k * 0.55)
        g.append(f"<path d='M{xx:.0f} {yy:.0f} q{-d*30:.0f} {h*0.08:.0f} {-d*10:.0f} {h*0.16:.0f}' fill='none' stroke='{mix('#5e3e30', '#2e1c18', rev)}' stroke-width='8' stroke-linecap='round'/>")
    # brillo del cráter
    if heat > 0:
        g.append(f"<ellipse cx='{VX}' cy='{top+4:.0f}' rx='{cw:.0f}' ry='{6+cw*0.18:.0f}' fill='{mix('#ff7a2a', '#ffe14a', rev)}' opacity='{heat:.2f}' stroke='{INK}' stroke-width='6'/>")
    # ríos de lava
    flow = seg(t, 7.7, 9.6)
    if flow > 0:
        for d, off in ((-1, 0.0), (1, 0.4)):
            L = h * flow * 0.92
            x1 = VX + d * cw * 0.6; y1 = top + 6
            x2 = VX + d * (cw + (bw - cw) * (L / h) * 0.55); y2 = top + L
            w = 22 + 4 * math.sin(t * 6 + off * 10)
            path = f"M{x1:.0f} {y1:.0f} Q{x1+d*h*0.12 + 18*math.sin(t*3+off):.0f} {(y1+y2)/2:.0f} {x2:.0f} {y2:.0f}"
            g.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='{w+14:.0f}' stroke-linecap='round'/>")
            g.append(f"<path d='{path}' fill='none' stroke='#ff6a1a' stroke-width='{w:.0f}' stroke-linecap='round'/>")
            g.append(f"<path d='{path}' fill='none' stroke='#ffd23f' stroke-width='{w*0.4:.0f}' stroke-linecap='round'/>")
    # cara
    if h > 110:
        op = seg(h, 110, 150)
        blink = 1.0 if (t % 2.3) > 0.12 else 0.12
        ey = top + h * 0.42; sep = 28 + h * 0.13; er = 12 + h * 0.05
        awake = seg(t, 5.8, 6.4); big = lerp(1, 1.25, rev)
        for d in (-1, 1):
            ex = VX + d * sep
            g.append(f"<g transform='translate({ex:.0f},{ey:.0f}) scale({big:.2f},{blink*lerp(0.25, 1, awake)*big:.2f})' opacity='{op:.2f}'>"
                     f"<ellipse rx='{er:.0f}' ry='{er*1.2:.0f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='{-d*er*0.15:.0f}' cy='{er*0.15:.0f}' r='{er*0.55:.0f}' fill='{INK}'/>"
                     f"<circle cx='{-d*er*0.15 - er*0.2:.0f}' cy='{-er*0.15:.0f}' r='{er*0.2:.0f}' fill='#fff'/></g>")
        my = ey + er * 2.2
        mw = lerp(14, 34, rev) * (h / 300)
        g.append(f"<ellipse cx='{VX}' cy='{my:.0f}' rx='{mw+6:.0f}' ry='{lerp(4, mw*0.9, rev)+2:.0f}' fill='#6a1f1f' stroke='{INK}' stroke-width='6' opacity='{op:.2f}'/>")
        for d in (-1, 1):
            g.append(f"<ellipse cx='{VX + d*(sep+er*1.6):.0f}' cy='{my-er*0.4:.0f}' rx='{er*0.8:.0f}' ry='{er*0.45:.0f}' fill='#ff7a6a' opacity='{0.55*op:.2f}'/>")
    return "".join(g)


def puff(cx, cy, r, col, op):
    return (f"<g opacity='{op:.2f}'><circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r:.0f}' fill='{col}' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='{cx-r*0.6:.0f}' cy='{cy+r*0.25:.0f}' r='{r*0.7:.0f}' fill='{col}' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='{cx+r*0.6:.0f}' cy='{cy+r*0.3:.0f}' r='{r*0.65:.0f}' fill='{col}' stroke='{INK}' stroke-width='6'/></g>")


def frame(t):
    h = altura(t)
    rev = seg(t, 7.45, 8.2)
    heat = seg(t, 5.2, 7.2)
    top = BASE - h
    shake = 7 * math.sin(t * 57) * (seg(t, 5.0, 6.0) - seg(t, 8.6, 9.6)) + 3 * math.sin(t * 43) * seg(t, 7.4, 7.8)
    s = ["<defs>"]
    s.append(f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>"
             f"<stop offset='0' stop-color='{mix('#6fc3ef', '#3a1d3a', rev)}'/>"
             f"<stop offset='0.55' stop-color='{mix('#a9def5', '#b8402b', rev)}'/>"
             f"<stop offset='1' stop-color='{mix('#fdf3cf', '#ff9a3c', rev)}'/></linearGradient>")
    s.append(f"<radialGradient id='glow'><stop offset='0' stop-color='#fff1a0' stop-opacity='{0.9*rev:.2f}'/>"
             f"<stop offset='0.4' stop-color='#ff8a2a' stop-opacity='{0.6*rev:.2f}'/><stop offset='1' stop-color='#ff4a1a' stop-opacity='0'/></radialGradient>")
    s.append("</defs>")
    s.append(f"<rect width='{W}' height='{H}' fill='url(#sky)'/>")
    z = 1 + 0.12 * seg(t, 7.45, 10)
    w = [f"<g transform='translate({shake:.1f},0)'>"]
    # sol de la mañana
    sa = 1 - rev
    if sa > 0.02:
        w.append(f"<circle cx='880' cy='{lerp(1080, 1040, seg(t, 0, 7)):.0f}' r='70' fill='#fff1a6' stroke='#ffc94a' stroke-width='8' opacity='{sa:.2f}'/>")
    # nubes tranquilas arriba
    for cx, cy, sc, sp in CLOUDS:
        dx = (cx + t * sp) % 1300 - 110
        col = mix("#ffffff", "#7a4a5a", rev)
        w.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})' opacity='0.9'>"
                 f"<path d='M0 40 Q10 -10 70 0 Q100 -50 160 -10 Q220 -25 240 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # montañas lejanas
    w.append(f"<path d='M-20 1330 L150 1170 L300 1290 L430 1200 L560 1320 L720 1180 L880 1290 L1000 1210 L1100 1300 L1100 1500 L-20 1500 Z' "
             f"fill='{mix('#7fa8c9', '#5a2f3e', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    w.append(f"<path d='M-20 1380 Q250 1310 540 1370 T1100 1360 L1100 1500 L-20 1500 Z' fill='{mix('#8cc56a', '#5e4a2a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    # campo arado
    w.append(f"<rect x='-20' y='1430' width='1120' height='520' fill='{mix('#b9773f', '#6e3a24', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for i, yy in enumerate((1475, 1530, 1600, 1690, 1800)):
        w.append(f"<path d='M-20 {yy} Q540 {yy - 18 - i*4} 1100 {yy}' fill='none' stroke='{mix('#93592c', '#4e2818', rev)}' stroke-width='{8+i*2}'/>")
    # brillo de la erupción detrás
    w.append(f"<circle cx='{VX}' cy='{top:.0f}' r='{lerp(100, 620, rev):.0f}' fill='url(#glow)'/>")
    # humo / ceniza
    if True:
        for t0, dx, sc in SMOKE:
            per = 3.0 if t < REVELACION else 1.6
            age = ((t - t0) % per) / per
            amt = lerp(0.35, 1.0, seg(t, 2.5, 7)) * sc + 1.1 * rev
            yy = top - 20 - age * lerp(180, 420, seg(t, 3, 8.3))
            r = (20 + age * 50) * amt
            col = mix(mix("#e8e8e8", "#9a9a9a", seg(t, 5, 7.5)), "#4a3a3a", rev)
            w.append(puff(VX + dx * (1 + age * 2) + 20 * math.sin(t * 2 + t0), max(yy, 860 + r), r, col, 0.9 * (1 - age * 0.6)))
    # grieta antes de que crezca
    cr = lerp(0.35, 1, seg(t, 0, 1.4)) * (1 - seg(t, 3.0, 3.8))
    if cr > 0:
        w.append(f"<path d='M{VX-110*cr:.0f} 1500 L{VX-60*cr:.0f} 1490 L{VX-30*cr:.0f} 1506 L{VX+10*cr:.0f} 1488 L{VX+50*cr:.0f} 1504 L{VX+110*cr:.0f} 1494' "
                 f"fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>")
        w.append(f"<path d='M{VX-90*cr:.0f} 1497 L{VX-60*cr:.0f} 1492 L{VX-30*cr:.0f} 1502 L{VX+10*cr:.0f} 1492 L{VX+50*cr:.0f} 1500 L{VX+90*cr:.0f} 1495' "
                 f"fill='none' stroke='#ff7a2a' stroke-width='4' stroke-linecap='round' opacity='{0.4 + 0.4*math.sin(t*8):.2f}'/>")
    # maíz lejano (detrás del volcán)
    for x, y, sc, ph in MID_CORN:
        w.append(corn(x, y, sc, 4 * math.sin(t * 2.2 + ph) + 3 * shake, rev * 0.6))
    w.append(volcano(t, h, rev, heat))
    # fuente de lava
    if t >= REVELACION:
        for t0, vx, vy, r in LAVA:
            age = ((t - REVELACION - t0) % 1.1)
            if t - REVELACION - t0 < 0: continue
            px = VX + vx * age * 0.9
            py = top - vy * age + 520 * age * age
            if py > top + 30: continue
            py = max(py, 870)
            w.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{r:.0f}' fill='#ff6a1a' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='{px - r*0.3:.0f}' cy='{py - r*0.3:.0f}' r='{r*0.4:.0f}' fill='#ffe14a'/>")
    # segunda fila de maíz
    for x, y, sc, ph in ROW2:
        w.append(corn(x, y, sc, 5 * math.sin(t * 2.0 + ph) + 3 * shake, rev * 0.5))
    # polvo que salta con el temblor
    jig = seg(t, 5, 6) * (1 - seg(t, 9, 10))
    for px, py, pr, ph in DUST:
        hop = abs(math.sin(t * 7 + ph)) * 26 * jig
        w.append(f"<circle cx='{px:.0f}' cy='{py - hop:.0f}' r='{pr:.1f}' fill='{mix('#e2a86a', '#ff9a4a', rev)}' opacity='0.7'/>")
    w.append(farmer(t, rev))
    for x, y, sc, ph in FRONT:
        w.append(corn(x, y, sc, 5 * math.sin(t * 1.8 + ph) + 2 * shake, rev * 0.4))
    w.append("</g>")
    s.append(zoom(VX, 1420, z, "".join(w)))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>" + "".join(s) + "</svg>"
