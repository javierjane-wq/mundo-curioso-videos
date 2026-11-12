"""2026-11-12-c5 · Química: la manzana cortada se pone marrón porque el oxígeno del aire, con una
enzima de la propia fruta (polifenol oxidasa), oxida sus compuestos y forma pigmentos marrones.

Una manzana roja cae y rebota sobre una tabla de cortar en la encimera de una cocina. Un cuchillo
la corta y las dos mitades (con carita) se separan y enseñan su pulpa blanca con las pepitas.
Moléculas de oxígeno (dos bolitas azules unidas) flotan por el aire y se acercan a la pulpa:
salen manchitas marrones. En la revelación hay un destello, el oxígeno las rodea y la pulpa
entera se vuelve marrón; las mitades ponen cara de sorpresa y la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.5    # destello: la pulpa entera se pone marrón
MUSICA = 6

rng = np.random.default_rng(1205)
# moléculas de O2: (x0, y0, velocidad, fase, ángulo)
O2 = [(rng.uniform(40, 1040), rng.uniform(1050, 1880), rng.uniform(25, 55), rng.uniform(0, 6.28),
       rng.uniform(0, 180)) for _ in range(22)]
SPOTS = [(rng.uniform(-0.55, 0.55), rng.uniform(-0.45, 0.6), rng.uniform(14, 30), rng.uniform(5.1, 7.2))
         for _ in range(9)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(260, 420), rng.uniform(0, 0.4), rng.uniform(12, 22)) for _ in range(18)]
JARS = [(110, "#ff9f43", 70, 95), (215, "#6ab04c", 60, 80), (830, "#e056fd", 65, 90), (935, "#f9ca24", 70, 75)]

CX, CY, R = 540, 1450, 215      # manzana entera
TABLE = 1180                    # borde de la encimera


def apple_path(r, sx=1.0):
    """Contorno de manzana (centrado en 0,0, radio r) con el hoyuelo arriba."""
    p = [(0, -0.74), (0.38, -1.05), (1.0, -0.92), (1.0, -0.15), (1.0, 0.55), (0.62, 1.0), (0.3, 0.96),
         (0.16, 0.93), (0.06, 0.88), (0, 0.9), (-0.06, 0.88), (-0.16, 0.93), (-0.3, 0.96),
         (-0.62, 1.0), (-1.0, 0.55), (-1.0, -0.15), (-1.0, -0.92), (-0.38, -1.05), (0, -0.74)]
    q = [(x * r * sx, y * r) for x, y in p]
    d = f"M{q[0][0]:.1f} {q[0][1]:.1f}"
    for i in range(1, len(q), 3):
        a, b, c = q[i], q[i + 1], q[i + 2]
        d += f" C{a[0]:.1f} {a[1]:.1f} {b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}"
    return d + " Z"


def face(t, ox, oy, sc, sorpresa, mira):
    blink = 0.12 if ((t + 1.3 + ox * 0.001) % 2.9) < 0.12 else 1.0
    er = 26 * sc * (1 + 0.35 * sorpresa)
    g = []
    for ex in (-48, 48):
        g.append(f"<ellipse cx='{ox + ex*sc:.1f}' cy='{oy:.1f}' rx='{er:.1f}' ry='{er*1.15*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ox + ex*sc + mira*9:.1f}' cy='{oy + 3:.1f}' r='{er*0.55:.1f}' fill='{INK}'/>"
                     f"<circle cx='{ox + ex*sc + mira*9 - er*0.2:.1f}' cy='{oy - er*0.25:.1f}' r='{er*0.2:.1f}' fill='#fff'/>")
    # mejillas
    for ex in (-80, 80):
        g.append(f"<ellipse cx='{ox + ex*sc:.1f}' cy='{oy + 38*sc:.1f}' rx='{16*sc:.1f}' ry='{9*sc:.1f}' fill='#ff8a8a' opacity='{0.6*(1-sorpresa):.2f}'/>")
    my = oy + 52 * sc
    if sorpresa < 0.5:
        g.append(f"<path d='M{ox-24*sc:.1f} {my:.1f} Q{ox:.1f} {my+22*sc:.1f} {ox+24*sc:.1f} {my:.1f}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='{ox:.1f}' cy='{my+8*sc:.1f}' rx='{17*sc:.1f}' ry='{24*sc:.1f}' fill='#7a2a1e' stroke='{INK}' stroke-width='6'/>")
    return "".join(g)


def whole_apple(t):
    y = lerp(1180, CY, ease(clamp(t / 0.7)))
    if t > 0.7:
        y = CY - 60 * abs(math.sin(math.pi * clamp((t - 0.7) / 0.45))) * (1 - seg(t, 0.7, 1.4))
    sq = 1 + 0.08 * math.exp(-max(0, t - 0.7) * 6) * (t > 0.7)
    rot = 6 * math.sin(t * 5) * (1 - seg(t, 1.2, 2.0))
    g = [f"<g transform='translate({CX},{y:.1f}) rotate({rot:.1f}) scale({sq:.3f},{1/sq:.3f})'>"]
    g.append(f"<path d='M8 -150 Q18 -230 44 -262' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
             f"<path d='M8 -150 Q18 -230 44 -262' fill='none' stroke='#7a4a26' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M30 -228 Q100 -290 170 -240 Q100 -190 30 -228 Z' fill='#5cc45a' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M40 -228 Q100 -238 160 -240' fill='none' stroke='#2f8a3a' stroke-width='5'/>")
    g.append(f"<path d='{apple_path(R)}' fill='#e8322c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='{apple_path(R*0.86)}' fill='none' stroke='#b81e1e' stroke-width='18' opacity='0.35' transform='translate(18,10)'/>")
    g.append(f"<ellipse cx='-95' cy='-80' rx='34' ry='62' fill='#ff8f7a' opacity='0.85' transform='rotate(25 -95 -80)'/>")
    g.append(f"<circle cx='-60' cy='-150' r='13' fill='#ffd2c4'/>")
    g.append(face(t, 0, 10, 1.15, 0, 0))
    g.append("</g>")
    return "".join(g)


def half(t, side, brown, sorpresa):
    """Mitad de manzana vista por el corte: piel roja, pulpa crema, corazón y pepitas."""
    sep = seg(t, 2.25, 3.2)
    x = CX + side * lerp(4, 232, sep)
    rot = side * lerp(0, 9, sep) + 3 * math.sin(t * 2.6 + side)
    bob = 6 * math.sin(t * 3.1 + side * 1.3) * sep
    sq = 1 + 0.10 * sorpresa * math.exp(-max(0, t - REVELACION) * 3) * math.sin((t - REVELACION) * 14) if t > REVELACION else 1
    r = 190
    flesh = mix("#fff6d8", "#b5763a", brown)
    core = mix("#f3e3a8", "#8e5526", brown)
    g = [f"<g transform='translate({x:.1f},{CY + 10 + bob:.1f}) rotate({rot:.1f}) scale({1/sq:.3f},{sq:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='{r*0.98:.0f}' rx='{r*0.9:.0f}' ry='26' fill='#000' opacity='0.18'/>")
    g.append(f"<path d='M6 -{r*0.7:.0f} Q14 -{r*1.1:.0f} 34 -{r*1.25:.0f}' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
             f"<path d='M6 -{r*0.7:.0f} Q14 -{r*1.1:.0f} 34 -{r*1.25:.0f}' fill='none' stroke='#7a4a26' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<path d='{apple_path(r)}' fill='#e8322c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='{apple_path(r*0.88)}' fill='{flesh}' stroke='#f0c8a0' stroke-width='4' transform='translate(0,4)'/>")
    # manchas marrones antes de la revelación
    for sx_, sy_, sr, ta in SPOTS:
        k = seg(t, ta, ta + 1.0) * (1 - brown)
        if k > 0.01:
            g.append(f"<circle cx='{sx_*r*side:.1f}' cy='{sy_*r:.1f}' r='{sr*k:.1f}' fill='#b5763a' opacity='{0.85*k:.2f}'/>")
    # corazón (estrella de semillas)
    g.append(f"<path d='M0 -{r*0.55:.0f} Q{r*0.2:.0f} -{r*0.2:.0f} {r*0.12:.0f} {r*0.25:.0f} Q0 {r*0.42:.0f} -{r*0.12:.0f} {r*0.25:.0f} "
             f"Q-{r*0.2:.0f} -{r*0.2:.0f} 0 -{r*0.55:.0f} Z' fill='{core}' stroke='{mix('#d9b870', '#6e3e1a', brown)}' stroke-width='5'/>")
    for sxs in (-1, 1):
        g.append(f"<ellipse cx='{sxs*r*0.06:.1f}' cy='{r*0.0:.1f}' rx='11' ry='22' fill='#5a3016' stroke='{INK}' stroke-width='4' "
                 f"transform='rotate({sxs*-18} {sxs*r*0.06:.1f} 0)'/>")
    g.append(face(t, 0, r * 0.32, 0.8, sorpresa, -side * 0.6 if t < 5 else side * 0.4))
    g.append("</g>")
    return "".join(g)


def knife(t):
    k_in = seg(t, 1.2, 1.9); k_cut = seg(t, 1.9, 2.25); k_out = seg(t, 2.3, 2.9)
    if k_in <= 0 or k_out >= 1:
        return ""
    y = lerp(620, 820, k_in) + lerp(0, 360, k_cut) - lerp(0, 900, k_out)
    x = CX + lerp(260, 0, k_in) + lerp(0, 400, k_out)
    rot = lerp(-30, 0, k_in) + lerp(0, 25, k_out)
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"
            f"<path d='M-14 -40 L-14 300 Q-14 360 40 380 L40 -40 Z' fill='#dfe6ee' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M14 -30 L14 320' stroke='#ffffff' stroke-width='8' opacity='0.8'/>"
            f"<rect x='-30' y='-230' width='86' height='200' rx='22' fill='#2d3a5a' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='13' cy='-170' r='9' fill='#c9ced6'/><circle cx='13' cy='-90' r='9' fill='#c9ced6'/></g>")


def o2(x, y, a, s=1.0, op=1.0):
    dx = 20 * s * math.cos(math.radians(a)); dy = 20 * s * math.sin(math.radians(a))
    return (f"<g opacity='{op:.2f}'><line x1='{x-dx:.1f}' y1='{y-dy:.1f}' x2='{x+dx:.1f}' y2='{y+dy:.1f}' stroke='{INK}' stroke-width='8'/>"
            f"<circle cx='{x-dx:.1f}' cy='{y-dy:.1f}' r='{17*s:.1f}' fill='#4fb3ff' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='{x+dx:.1f}' cy='{y+dy:.1f}' r='{17*s:.1f}' fill='#4fb3ff' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='{x-dx-5*s:.1f}' cy='{y-dy-6*s:.1f}' r='{5*s:.1f}' fill='#fff'/>"
            f"<circle cx='{x+dx-5*s:.1f}' cy='{y+dy-6*s:.1f}' r='{5*s:.1f}' fill='#fff'/></g>")


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.5)
    brown = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    sorpresa = 1.0 if t >= REVELACION else 0.0
    wall_t = mix("#bfe8e2", "#ffe2b8", rev); wall_b = mix("#e4f6ef", "#fff1d6", rev)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_t}'/>"
            f"<stop offset='1' stop-color='{wall_b}'/></linearGradient>"
            f"<radialGradient id='flash'><stop offset='0' stop-color='#fffbe6' stop-opacity='0.95'/>"
            f"<stop offset='1' stop-color='#ffd27a' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION, 10)
    sc = []
    # azulejos suaves de la pared
    for yy in range(140, TABLE, 120):
        sc.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='#ffffff' stroke-width='5' opacity='0.55'/>")
    for row, yy in enumerate(range(20, TABLE, 120)):
        for xx in range(60 * (row % 2), W, 120):
            sc.append(f"<line x1='{xx}' y1='{yy}' x2='{xx}' y2='{yy+120}' stroke='#ffffff' stroke-width='5' opacity='0.55'/>")
    # repisa con botes a los lados (abajo del todo de la pared)
    sc.append(f"<rect x='40' y='1010' width='300' height='22' rx='6' fill='#c98a52' stroke='{INK}' stroke-width='7'/>")
    sc.append(f"<rect x='740' y='1010' width='300' height='22' rx='6' fill='#c98a52' stroke='{INK}' stroke-width='7'/>")
    for jx, col, jw, jh in JARS:
        sw = 2 * math.sin(t * 1.7 + jx)
        sc.append(f"<g transform='rotate({sw*0.3:.2f} {jx} 1010)'><rect x='{jx-jw/2}' y='{1010-jh}' width='{jw}' height='{jh}' rx='14' fill='{col}' stroke='{INK}' stroke-width='7'/>"
                  f"<rect x='{jx-jw/2-6}' y='{1010-jh-18}' width='{jw+12}' height='22' rx='6' fill='#8a5a3a' stroke='{INK}' stroke-width='6'/>"
                  f"<rect x='{jx-jw/2+10}' y='{1010-jh+14}' width='10' height='{jh-34}' rx='5' fill='#fff' opacity='0.5'/></g>")
    # encimera y frente de muebles
    sc.append(f"<rect x='-20' y='{TABLE}' width='{W+40}' height='60' fill='#f4d29c' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<rect x='-20' y='{TABLE+60}' width='{W+40}' height='{H-TABLE}' fill='#e8a86a' stroke='{INK}' stroke-width='{LW}'/>")
    for dx in (0, 360, 720):
        sc.append(f"<rect x='{dx+30}' y='{TABLE+100}' width='300' height='{H-TABLE-60}' rx='18' fill='#f0b77c' stroke='{INK}' stroke-width='7'/>")
        sc.append(f"<rect x='{dx+150}' y='{TABLE+140}' width='60' height='16' rx='8' fill='#8a5a3a' stroke='{INK}' stroke-width='5'/>")
    # tabla de cortar
    sc.append(f"<rect x='90' y='1600' width='900' height='70' rx='30' fill='#c98a52' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<rect x='90' y='1560' width='900' height='70' rx='30' fill='#e3a865' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<path d='M140 1590 Q400 1580 640 1594 T940 1588' fill='none' stroke='#c98a52' stroke-width='6'/>")
    sc.append(f"<circle cx='960' cy='1595' r='14' fill='#c98a52' stroke='{INK}' stroke-width='5'/>")
    # halo de la revelación detrás de las mitades
    if rev > 0:
        sc.append(f"<circle cx='{CX}' cy='{CY}' r='{lerp(200, 650, rev):.0f}' fill='url(#flash)' opacity='{rev:.2f}'/>")
    # moléculas de oxígeno flotando (se acercan a la pulpa desde 5 s)
    pull = seg(t, 5.0, REVELACION)
    for i, (x0, y0, sp, ph, a) in enumerate(O2):
        x = x0 + 30 * math.sin(t * 0.9 + ph); y = 1060 + (y0 - 1060 - t * sp) % 820
        tx = CX + (232 if x > CX else -232) + 150 * math.cos(ph + t * 1.5)
        ty = CY + 170 * math.sin(ph * 2 + t * 1.5)
        if t > REVELACION:  # giran alrededor de las mitades
            ang = ph + (t - REVELACION) * 2.2
            tx = CX + (232 if i % 2 else -232) + 230 * math.cos(ang); ty = CY + 230 * math.sin(ang)
        k = pull * 0.85 + rev * 0.15
        xx = lerp(x, tx, k); yy = lerp(y, ty, k)
        op = lerp(0.55, 1.0, seg(t, 3.5, 5.5))
        sc.append(o2(xx, yy, a + t * 40, 1.25 + 0.15 * math.sin(t * 3 + ph), op))
    if t < 2.25:
        sc.append(whole_apple(t))
    else:
        sc.append(half(t, -1, brown, sorpresa))
        sc.append(half(t, 1, brown, sorpresa))
    # destellos de la revelación
    if t > REVELACION:
        for ang, dist, dl, sz in SPARK:
            k = clamp((t - REVELACION - dl) / 1.2)
            if 0 < k < 1:
                px = CX + math.cos(ang) * dist * (0.6 + k); py = CY + math.sin(ang) * dist * (0.6 + k) * 0.8
                if py > 1030:
                    sz2 = sz * (1 - k)
                    sc.append(f"<path d='M{px:.0f} {py-sz2*2:.0f} L{px+sz2*0.5:.0f} {py:.0f} L{px:.0f} {py+sz2*2:.0f} L{px-sz2*0.5:.0f} {py:.0f} Z' "
                              f"fill='#fff4b0' stroke='{INK}' stroke-width='4'/>")
    sc.append(knife(t))
    s.append(zoom(CX, CY, z, "".join(sc)))
    # destello blanco del corte y de la revelación
    fl = max(0, 1 - abs(t - REVELACION) / 0.25) * 0.55 + max(0, 1 - abs(t - 2.25) / 0.12) * 0.25
    if fl > 0.01:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{fl:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
