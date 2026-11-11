"""Versión por código de 2026-11-11-px: en la Luna un martillo y una pluma caen a la vez (Apolo 15, 1971).

Astronauta original (traje blanco, visera dorada, sin banderas ni logotipos) llega dando saltitos,
levanta un martillo y una pluma, los suelta a la vez y ambos tocan el suelo en el mismo instante:
nube de polvo doble, destello y salto de alegría a cámara lenta.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.6    # martillo y pluma tocan el suelo a la vez
MUSICA = 6

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1350), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(90)]
CRATERS = [(150, 1500, 70), (900, 1470, 55), (760, 1860, 90), (230, 1840, 60), (1000, 1700, 45), (480, 1440, 30)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(140, 320), rng.uniform(10, 20)) for _ in range(16)]

GROUND = 1800          # donde caen martillo y pluma
T_DROP, T_HIT = 6.8, REVELACION
X_HAM, X_FEA = 300, 780


def hops(t):
    """Posición del astronauta: llega dando saltos lentos (gravedad lunar) y luego salta de alegría."""
    x = lerp(150, 540, seg(t, 0, 2.4))
    y = 0
    if t < 2.4:
        k = (t / 0.8) % 1
        y = -90 * math.sin(math.pi * k)
    jump = seg(t, 8.0, 8.0001) * clamp((t - 8.0) / 1.7)
    if 8.0 < t < 9.7:
        y = -170 * math.sin(math.pi * jump)
    return x, y


def hammer(x, yb, ang=0):
    """Martillo: mango de madera vertical, cabeza de metal arriba. (x, yb) = extremo de abajo del mango."""
    return (f"<g transform='translate({x:.1f},{yb:.1f}) rotate({ang:.1f})'>"
            f"<rect x='-13' y='-190' width='26' height='190' rx='9' fill='#b9773f' stroke='{INK}' stroke-width='7'/>"
            f"<line x1='-4' y1='-170' x2='-4' y2='-20' stroke='#d99a5c' stroke-width='5' stroke-linecap='round'/>"
            f"<rect x='-62' y='-245' width='124' height='64' rx='10' fill='#8d96a3' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-50' y='-236' width='60' height='14' rx='6' fill='#c9d0da'/>"
            f"</g>")


def feather(x, yb, ang=0):
    """Pluma de halcón: cañón blanco, barbas marrones con bandas claras. (x, yb) = punta del cañón."""
    bands = "".join(
        f"<path d='M{-30 + i*2} {-60 - i*32} Q0 {-70 - i*32} {30 - i*2} {-52 - i*32}' fill='none' stroke='#f3e3c4' stroke-width='6' stroke-linecap='round'/>"
        for i in range(5))
    return (f"<g transform='translate({x:.1f},{yb:.1f}) rotate({ang:.1f})'>"
            f"<path d='M0 -40 C-48 -70 -50 -190 -6 -250 C40 -190 46 -80 0 -40 Z' fill='#8a5a34' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"{bands}"
            f"<path d='M0 -250 C-18 -215 -26 -180 -28 -150 L-6 -160 Z' fill='#5c3a20'/>"
            f"<line x1='0' y1='0' x2='0' y2='-240' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
            f"<line x1='0' y1='0' x2='0' y2='-238' stroke='#fbf6ea' stroke-width='4' stroke-linecap='round'/>"
            f"</g>")


def limb(x1, y1, x2, y2, w=44):
    return (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{INK}' stroke-width='{w + 2*LW}' stroke-linecap='round'/>"
            f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='#f4f6fa' stroke-width='{w}' stroke-linecap='round'/>")


def astronaut(t):
    x, dy = hops(t)
    base = 1785 + dy            # pies
    hip = base - 200
    sh_y = hip - 230            # hombros
    head_y = sh_y - 95
    g = [f"<ellipse cx='{x:.1f}' cy='1795' rx='{lerp(130, 70, clamp(-dy/170)):.0f}' ry='20' fill='#000' opacity='0.3'/>"]
    # brazos: a los lados mientras llega, arriba entre 2,6 y 4,6 s; tras soltar, saludan en el salto
    up = seg(t, 2.6, 4.4)
    wave = 0.0 if t < 8.0 else 22 * math.sin((t - 8.0) * 9)
    hands = []
    for side in (-1, 1):
        sx = x + side * 92
        hx = lerp(sx + side * 40, x + side * 240, up) + (side * wave if t > 8 else 0)
        hy = lerp(sh_y + 200, sh_y - 170, up) - (abs(wave) * 0.6 if t > 8 else 0)
        if t < 2.4:
            hy += 25 * math.sin(t * 7.8 + side)
        hands.append((sx, sh_y + 20, hx, hy))
    # mochila
    g.append(f"<rect x='{x-150:.1f}' y='{sh_y-40:.1f}' width='300' height='250' rx='34' fill='#d7dce5' stroke='{INK}' stroke-width='{LW}'/>")
    # piernas
    spread = 10 * math.sin(t * 7.8) if t < 2.4 else 0
    for side in (-1, 1):
        g.append(limb(x + side * 52, hip, x + side * (70 + spread), base - 30, 66))
        g.append(f"<rect x='{x + side*(70+spread) - 50:.1f}' y='{base-60:.1f}' width='100' height='60' rx='22' fill='#e9ecf2' stroke='{INK}' stroke-width='{LW}'/>")
    # brazos (detrás del torso arriba se ven por encima de los hombros)
    for sx, sy, hx, hy in hands:
        g.append(limb(sx, sy, hx, hy, 48))
    # torso
    g.append(f"<rect x='{x-120:.1f}' y='{sh_y-30:.1f}' width='240' height='{hip - sh_y + 60:.1f}' rx='60' fill='#f4f6fa' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='{x-62:.1f}' y='{sh_y+40:.1f}' width='124' height='92' rx='14' fill='#dfe4ec' stroke='{INK}' stroke-width='6'/>")
    lamp = '#ff5a5f' if (t % 1.0) < 0.5 else '#ffd23f'
    g.append(f"<circle cx='{x-30:.1f}' cy='{sh_y+70:.1f}' r='14' fill='#3a7bd5' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='{x+22:.1f}' cy='{sh_y+66:.1f}' r='9' fill='{lamp}' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<rect x='{x+6:.1f}' y='{sh_y+90:.1f}' width='38' height='14' rx='5' fill='#7ee081' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<rect x='{x-112:.1f}' y='{hip-20:.1f}' width='224' height='34' rx='12' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>")
    # guantes
    for sx, sy, hx, hy in hands:
        g.append(f"<circle cx='{hx:.1f}' cy='{hy:.1f}' r='32' fill='#e9ecf2' stroke='{INK}' stroke-width='{LW}'/>")
    # casco
    g.append(f"<circle cx='{x:.1f}' cy='{head_y:.1f}' r='112' fill='#f4f6fa' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='{x:.1f}' cy='{head_y+8:.1f}' rx='84' ry='70' fill='url(#visor)' stroke='{INK}' stroke-width='7'/>")
    shine = 18 * math.sin(t * 1.3)
    g.append(f"<ellipse cx='{x-34+shine:.1f}' cy='{head_y-22:.1f}' rx='26' ry='14' fill='#fff6d0' opacity='0.85' transform='rotate(-25 {x-34+shine:.1f} {head_y-22:.1f})'/>")
    g.append(f"<circle cx='{x+38+shine*0.5:.1f}' cy='{head_y+30:.1f}' r='7' fill='#fff6d0' opacity='0.7'/>")
    return "".join(g), hands


def lander(t):
    """Módulo de aterrizaje genérico, lejos a la izquierda."""
    x, y = 150, 1330
    light = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 5))
    return (f"<g transform='translate({x},{y}) scale(0.8)'>"
            f"<path d='M-90 60 L-130 150 M90 60 L130 150 M-40 70 L-55 150 M40 70 L55 150' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>"
            f"<path d='M-90 60 L-130 150 M90 60 L130 150' stroke='#c9ced6' stroke-width='4'/>"
            f"<rect x='-100' y='0' width='200' height='80' rx='10' fill='#f2b632' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-70 0 L-60 -90 L60 -90 L70 0 Z' fill='#d7dce5' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='-48' r='20' fill='#1e2a38' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='0' cy='-108' r='10' fill='#ff5a5f' opacity='{light:.2f}' stroke='{INK}' stroke-width='4'/>"
            f"</g>")


def frame(t):
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         "<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#05061a'/><stop offset='1' stop-color='#1b1f45'/></linearGradient>",
         "<linearGradient id='visor' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffd54a'/><stop offset='1' stop-color='#e08a12'/></linearGradient>",
         "<linearGradient id='moon' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b9bcc4'/><stop offset='1' stop-color='#8e929c'/></linearGradient>",
         "<radialGradient id='flash'><stop offset='0' stop-color='#fff8d6' stop-opacity='0.95'/><stop offset='0.5' stop-color='#ffd23f' stop-opacity='0.45'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # estrellas (fuera del zoom: fondo lejano)
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.6 + ph))
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # la Tierra (gira despacio)
    ex, ey, er = 860, 790, 100
    rot = (t * 9) % 120
    s.append(f"<circle cx='{ex}' cy='{ey}' r='{er+26}' fill='#5ec8ff' opacity='0.18'/>")
    s.append(f"<clipPath id='ec'><circle cx='{ex}' cy='{ey}' r='{er}'/></clipPath>")
    s.append(f"<circle cx='{ex}' cy='{ey}' r='{er}' fill='#2f7fe0'/>")
    s.append(f"<g clip-path='url(#ec)'>")
    for dx in (-240, -120, 0, 120):
        cx = ex - 60 + dx + rot
        s.append(f"<path d='M{cx:.0f} {ey-60} q40 -10 55 25 q-10 40 -45 45 q-30 -20 -10 -70 Z' fill='#4fbf5a'/>")
        s.append(f"<path d='M{cx+50:.0f} {ey+20} q30 5 30 40 q-30 15 -45 -10 Z' fill='#4fbf5a'/>")
        s.append(f"<path d='M{cx-20:.0f} {ey-15} q60 -20 110 0' stroke='#fff' stroke-width='12' fill='none' stroke-linecap='round' opacity='0.85'/>")
    s.append(f"<ellipse cx='{ex+38}' cy='{ey}' rx='{er}' ry='{er+10}' fill='#000' opacity='0.28'/>")
    s.append("</g>")
    s.append(f"<circle cx='{ex}' cy='{ey}' r='{er}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")

    # escena con zoom de cámara hacia el suelo en la revelación
    z = 1 + 0.10 * seg(t, 5.0, 6.8) + 0.16 * seg(t, 7.5, 8.6) - 0.12 * seg(t, 8.8, 10)
    cx, cy = 540, 1640
    s.append(f"<g transform='translate({cx},{cy}) scale({z:.4f}) translate({-cx},{-cy})'>")
    # suelo lunar
    s.append(f"<path d='M0 1360 Q270 1320 540 1350 T1080 1340 L1080 1920 L0 1920 Z' fill='url(#moon)' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1560 Q300 1520 620 1555 T1080 1540 L1080 1920 L0 1920 Z' fill='#a3a7b0' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    for rx, ry, rr in CRATERS:
        s.append(f"<ellipse cx='{rx}' cy='{ry}' rx='{rr}' ry='{rr*0.38:.0f}' fill='#7c808a' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='{rx}' cy='{ry + rr*0.08:.0f}' rx='{rr*0.75:.0f}' ry='{rr*0.24:.0f}' fill='#6a6e78'/>")
    s.append(lander(t))
    # huellas de los saltos
    for i, fx in enumerate((210, 330, 450)):
        if t > 0.8 * (i + 1) - 0.4:
            s.append(f"<ellipse cx='{fx}' cy='1800' rx='26' ry='9' fill='#6a6e78'/>")

    body, hands = astronaut(t)
    # posiciones de martillo y pluma
    (lsx, lsy, lhx, lhy), (rsx, rsy, rhx, rhy) = hands
    shake = 4 * math.sin(t * 40) * seg(t, 5.6, 6.6) * (1 - seg(t, 6.75, 6.8))
    if t < T_DROP:
        hb = (lhx, lhy + 70 + shake)
        fb = (rhx, rhy + 70 - shake)
        ham_ang = lerp(-60, 0, seg(t, 2.6, 4.4)); fea_ang = lerp(60, 0, seg(t, 2.6, 4.4))
    else:
        # caída libre (misma aceleración para los dos): y = y0 + d * k²
        x_up, _ = hops(T_DROP)
        y_rel = (1785 - 200 - 230) - 170 + 70     # altura de la mano al soltar
        k = clamp((t - T_DROP) / (T_HIT - T_DROP))
        y = lerp(y_rel, GROUND, k * k)
        hb = (x_up - 240, y); fb = (x_up + 240, y)
        ham_ang = fea_ang = 0
    s.append(body)
    s.append(hammer(hb[0], hb[1], ham_ang))
    s.append(feather(fb[0], fb[1], fea_ang))
    if t < T_DROP:   # dedos del guante por delante del mango
        for hx, hy in ((lhx, lhy), (rhx, rhy)):
            s.append(f"<path d='M{hx-26:.1f} {hy-6:.1f} q26 22 52 0' fill='#e9ecf2' stroke='{INK}' stroke-width='6'/>")
    # líneas de velocidad durante la caída
    if T_DROP < t < T_HIT + 0.1:
        for bx in (hb[0], fb[0]):
            for j in (-24, 0, 24):
                s.append(f"<line x1='{bx + j:.0f}' y1='{hb[1]-330:.0f}' x2='{bx + j:.0f}' y2='{hb[1]-260:.0f}' stroke='#ffffff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")

    # revelación: polvo doble, destello y chispas
    r = seg(t, T_HIT, T_HIT + 1.4)
    if t >= T_HIT:
        s.append(f"<circle cx='540' cy='{GROUND}' r='{lerp(80, 620, r):.0f}' fill='url(#flash)' opacity='{1 - seg(t, T_HIT + 0.2, T_HIT + 1.1):.2f}'/>")
        for bx in (hb[0], fb[0]):
            for j, (dxp, rr) in enumerate([(-70, 46), (-30, 62), (25, 58), (70, 44)]):
                px = bx + dxp * lerp(0.5, 1.8, r); py = GROUND - 20 - 60 * r * (1 if j % 2 else 0.6)
                s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{rr * lerp(0.4, 1.3, r):.0f}' fill='#c9ccd3' stroke='{INK}' stroke-width='6' opacity='{1 - 0.75*seg(t, 8.6, 10):.2f}'/>")
        for ang, dist, sz in SPARK:
            d = dist * seg(t, T_HIT, T_HIT + 0.9)
            px = 540 + math.cos(ang) * d * 1.6; py = GROUND - 150 + math.sin(ang) * d
            a = 1 - seg(t, 9.0, 10)
            col = '#ffd23f' if sz > 15 else '#ffffff'
            s.append(f"<path d='M{px:.0f} {py-sz:.0f} L{px+sz*0.35:.0f} {py:.0f} L{px:.0f} {py+sz:.0f} L{px-sz*0.35:.0f} {py:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='3' opacity='{a:.2f}'/>")
    # polvo fino que flota
    for i in range(14):
        px = (i * 83 + t * 18) % W; py = 1700 + 60 * math.sin(t * 0.8 + i)
        s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='4' fill='#e3e5ea' opacity='0.5'/>")
    s.append("</g></svg>")
    return "".join(s)
