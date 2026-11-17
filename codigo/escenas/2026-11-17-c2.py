"""Gran Mancha Roja de Júpiter: una tormenta en la que cabe la Tierra entera (NASA/JPL, Juno 2017:
unos 16.350 km de ancho, 1,3 veces el diámetro de la Tierra).

- 0-2,5 s: Júpiter sube desde abajo, sus bandas se deslizan y la Gran Mancha Roja gira.
- 2,5-5 s: una pequeña Tierra con cara entra volando por la izquierda y mira la mancha.
- 5-7,5 s: la tormenta gira más rápido y se agita; la Tierra se acerca, nerviosa.
- 7,5 s (REVELACION): la Tierra salta dentro de la mancha a su tamaño real y cabe entera;
  destello naranja, halo y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.5
MUSICA = 8

rng = np.random.default_rng(23)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1500), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(90)]
SWIRL = [(rng.uniform(0, 6.28), rng.uniform(0.35, 1.0), rng.uniform(5, 10)) for _ in range(22)]

JX, JY, JR = 540, 1640, 640          # Júpiter (centro y radio)
SX, SY = 610, 1370                   # Gran Mancha Roja (centro)
SRX, SRY = 205, 150                  # semiejes de la mancha

BANDS = [  # (y relativa al centro del planeta, grosor, color)
    (-640, 70, "#e9d3b0"), (-570, 55, "#c98b5a"), (-515, 50, "#f2e2c4"), (-465, 70, "#b8714a"),
    (-395, 60, "#f3dfbd"), (-335, 85, "#d49a66"), (-250, 70, "#f6e7cc"), (-180, 95, "#c27b4f"),
    (-85, 80, "#efd8b3"), (-5, 90, "#a9653f"), (85, 80, "#f1dcba"), (165, 120, "#cf9262"),
    (285, 120, "#ecd2ab"), (405, 240, "#be7c52"),
]


def band_path(y0, h, ph, amp=10):
    pts = [(x, y0 + amp * math.sin(x / 95 + ph)) for x in range(-160, W + 200, 40)]
    d = f"M{pts[0][0]} {pts[0][1]:.1f} " + " ".join(f"L{x} {y:.1f}" for x, y in pts[1:])
    d += f" L{W + 200} {y0 + h + 60} L-160 {y0 + h + 60} Z"
    return d


def jupiter(t, rise, agit):
    oy = lerp(420, 0, rise)
    cy = JY + oy
    g = [f"<g>"]
    # halo suave del planeta
    g.append(f"<circle cx='{JX}' cy='{cy:.1f}' r='{JR + 60}' fill='url(#jglow)'/>")
    g.append(f"<clipPath id='jclip'><circle cx='{JX}' cy='{cy:.1f}' r='{JR}'/></clipPath>")
    g.append(f"<circle cx='{JX}' cy='{cy:.1f}' r='{JR}' fill='#f0dcb8'/>")
    g.append("<g clip-path='url(#jclip)'>")
    for i, (yy, hh, col) in enumerate(BANDS):
        ph = t * (0.9 + 0.25 * (i % 3)) * (1 if i % 2 else -1) + i
        g.append(f"<path d='{band_path(cy + yy, hh, ph, 8 + (i % 3) * 3)}' fill='{col}' stroke='{INK}' stroke-width='4' stroke-opacity='0.35'/>")
    # pequeños remolinos blancos en las bandas
    for k, (bx, by) in enumerate([(160, -300), (880, -120), (300, 60), (820, 220), (120, -460)]):
        x = (bx + t * 40 * (1 if k % 2 else -1)) % (W + 200) - 100
        g.append(f"<ellipse cx='{x:.0f}' cy='{cy + by:.0f}' rx='46' ry='18' fill='#fff7e8' stroke='{INK}' stroke-width='4' stroke-opacity='0.5'/>")
    # sombra lateral para dar volumen
    g.append(f"<circle cx='{JX}' cy='{cy:.1f}' r='{JR}' fill='url(#jshade)'/>")
    g.append("</g>")
    g.append(f"<circle cx='{JX}' cy='{cy:.1f}' r='{JR}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    g.append("</g>")
    return "".join(g), oy


def spot(t, oy, agit, rev):
    cx, cy = SX, SY + oy
    sc = 1 + 0.04 * agit * math.sin(t * 9) + 0.05 * rev
    rx, ry = SRX * sc, SRY * sc
    ang = (t * 60 + 180 * seg(t, 5, 7.5) * (t - 5)) % 360    # gira más rápido en la tensión
    g = []
    # halo de la revelación
    if rev > 0:
        g.append(f"<ellipse cx='{cx}' cy='{cy:.1f}' rx='{rx * lerp(1.2, 1.9, rev):.1f}' ry='{ry * lerp(1.2, 1.9, rev):.1f}' fill='url(#shalo)' opacity='{rev:.2f}'/>")
    g.append(f"<ellipse cx='{cx}' cy='{cy:.1f}' rx='{rx + 26:.1f}' ry='{ry + 20:.1f}' fill='#f6e2bf' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<clipPath id='sclip'><ellipse cx='{cx}' cy='{cy:.1f}' rx='{rx:.1f}' ry='{ry:.1f}'/></clipPath>")
    g.append(f"<ellipse cx='{cx}' cy='{cy:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='{mix('#d4512c', '#ff7a2e', rev)}'/>")
    g.append("<g clip-path='url(#sclip)'>")
    g.append(f"<g transform='translate({cx},{cy:.1f}) scale(1,{ry / rx:.3f}) rotate({ang:.1f})'>")
    cols = ["#b73a22", "#ef7a45", "#9e2f1c", "#f59a5c"]
    for i in range(4):
        r0 = rx * (0.95 - i * 0.2)
        g.append(f"<path d='M{r0:.0f} 0 A{r0:.0f} {r0:.0f} 0 0 1 {-r0 * 0.6:.0f} {r0 * 0.8:.0f}' fill='none' stroke='{cols[i]}' stroke-width='{26 - i * 4}' stroke-linecap='round'/>")
        g.append(f"<path d='M{-r0:.0f} 0 A{r0:.0f} {r0:.0f} 0 0 1 {r0 * 0.6:.0f} {-r0 * 0.8:.0f}' fill='none' stroke='{cols[(i + 2) % 4]}' stroke-width='{22 - i * 4}' stroke-linecap='round'/>")
    g.append(f"<circle r='{rx * 0.18:.0f}' fill='#c4442a' stroke='{mix('#8a2a18', '#ffd08a', rev)}' stroke-width='8'/>")
    g.append("</g></g>")
    g.append(f"<ellipse cx='{cx}' cy='{cy:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # nubecillas que giran alrededor de la tormenta
    for a0, rr, sz in SWIRL:
        a = a0 + t * (1.2 + 2.5 * agit)
        px = cx + math.cos(a) * (rx + 40) * (0.85 + 0.25 * rr)
        py = cy + math.sin(a) * (ry + 32) * (0.85 + 0.25 * rr)
        g.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{sz:.1f}' fill='#fff3dc' opacity='{0.55 + 0.3 * agit:.2f}'/>")
    return "".join(g), (cx, cy)


def earth(t, x, y, r, worry, wow):
    blink = 1.0 if (t % 2.7) > 0.13 else 0.12
    g = [f"<g transform='translate({x:.1f},{y:.1f})'>"]
    g.append(f"<circle r='{r * 1.35:.1f}' fill='url(#eglow)'/>")
    g.append(f"<clipPath id='eclip'><circle r='{r:.1f}'/></clipPath>")
    g.append(f"<circle r='{r:.1f}' fill='#2f8fe0'/>")
    g.append("<g clip-path='url(#eclip)'>")
    off = (t * 0.25 * r) % (2.4 * r)
    for dx in (-off, -off + 2.4 * r):
        s = r / 100
        g.append(f"<g transform='translate({dx:.1f},0) scale({s:.3f})'>"
                 "<path d='M-90 -60 Q-60 -95 -20 -80 Q10 -60 -5 -30 Q-30 -10 -55 -25 Q-85 -20 -90 -60 Z' fill='#54c26b'/>"
                 "<path d='M20 10 Q55 -10 85 15 Q95 50 60 70 Q35 85 25 55 Q10 35 20 10 Z' fill='#54c26b'/>"
                 "<path d='M-150 30 Q-120 15 -100 40 Q-105 75 -135 70 Z' fill='#54c26b'/>"
                 "<path d='M110 -70 Q140 -85 165 -60 Q150 -35 120 -45 Z' fill='#54c26b'/></g>")
    # casquetes polares y nube
    g.append(f"<ellipse cx='0' cy='{-r * 0.98:.1f}' rx='{r * 0.55:.1f}' ry='{r * 0.2:.1f}' fill='#ffffff'/>")
    g.append(f"<ellipse cx='0' cy='{r * 0.98:.1f}' rx='{r * 0.5:.1f}' ry='{r * 0.18:.1f}' fill='#ffffff'/>")
    g.append(f"<circle cx='{r * 0.28:.1f}' cy='{-r * 0.28:.1f}' r='{r * 0.9:.1f}' fill='#ffffff' opacity='0.12'/>")
    g.append("</g>")
    g.append(f"<circle r='{r:.1f}' fill='none' stroke='{INK}' stroke-width='{max(6, LW * r / 110):.1f}'/>")
    # cara
    s = r / 100
    look = lerp(0, 9, worry)
    g.append(f"<g transform='scale({s:.3f})'>")
    for ex in (-32, 32):
        er = 20 + 6 * wow
        g.append(f"<ellipse cx='{ex}' cy='-8' rx='{er:.1f}' ry='{er * 1.15 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look:.1f}' cy='{-6 + look * 0.6:.1f}' r='{11:.1f}' fill='{INK}'/>"
                     f"<circle cx='{ex + look - 4:.1f}' cy='{-11 + look * 0.6:.1f}' r='4' fill='#fff'/>")
    g.append("<circle cx='-55' cy='22' r='11' fill='#ff8fa3' opacity='0.8'/><circle cx='55' cy='22' r='11' fill='#ff8fa3' opacity='0.8'/>")
    if wow > 0.5:
        g.append(f"<ellipse cx='0' cy='34' rx='14' ry='17' fill='#7a1f2b' stroke='{INK}' stroke-width='6'/>")
    elif worry > 0.5:
        g.append(f"<path d='M-16 38 Q0 30 16 38' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    else:
        g.append(f"<path d='M-20 28 Q0 46 20 28' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g></g>")
    return "".join(g)


def frame(t):
    rise = seg(t, 0, 2.2)
    agit = seg(t, 5, 6.5) * (1 - seg(t, 7.5, 8.2))
    rev = seg(t, REVELACION, REVELACION + 0.5)
    defs = (
        "<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>"
        f"<stop offset='0' stop-color='{mix('#0b0f2e', '#1a1240', rev)}'/><stop offset='0.6' stop-color='{mix('#1b1f52', '#3a1d5c', rev)}'/>"
        f"<stop offset='1' stop-color='{mix('#2a2366', '#6a2a5a', rev)}'/></linearGradient>"
        "<radialGradient id='neb' cx='0.3' cy='0.3' r='0.6'><stop offset='0' stop-color='#6a4fd1' stop-opacity='0.35'/>"
        "<stop offset='1' stop-color='#6a4fd1' stop-opacity='0'/></radialGradient>"
        f"<radialGradient id='jglow'><stop offset='0.9' stop-color='#ffcf8a' stop-opacity='{0.35 + 0.35 * rev:.2f}'/>"
        "<stop offset='1' stop-color='#ffcf8a' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='jshade' cx='0.35' cy='0.3' r='0.75'><stop offset='0.6' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='1' stop-color='#2a1030' stop-opacity='0.45'/></radialGradient>"
        "<radialGradient id='shalo'><stop offset='0.45' stop-color='#ffd36b' stop-opacity='0.9'/>"
        "<stop offset='1' stop-color='#ff7a2e' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='eglow'><stop offset='0.7' stop-color='#9fe0ff' stop-opacity='0.5'/>"
        "<stop offset='1' stop-color='#9fe0ff' stop-opacity='0'/></radialGradient>"
    )
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>",
         f"<rect width='{W}' height='1200' fill='url(#neb)'/>"]
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 2.6 + ph) + 0.1 * rev
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{clamp(a):.2f}'/>")
    z = 1 + 0.28 * seg(t, REVELACION, 9.6)
    body = []
    # pequeña luna que cruza a lo lejos
    mx = lerp(-60, 1140, t / DUR)
    body.append(f"<circle cx='{mx:.0f}' cy='{1010 - 30 * math.sin(t / DUR * 3.14):.0f}' r='26' fill='#cfc6b8' stroke='{INK}' stroke-width='6'/>"
                f"<circle cx='{mx - 8:.0f}' cy='{1004 - 30 * math.sin(t / DUR * 3.14):.0f}' r='7' fill='#a99f90'/>")
    jup, oy = jupiter(t, rise, agit)
    body.append(jup)
    sp, (scx, scy) = spot(t, oy, agit, rev)
    body.append(sp)
    # la Tierra: entra por la izquierda, se acerca y salta dentro de la mancha
    enter = seg(t, 2.2, 3.8)
    ex = lerp(-120, 230, enter); ey = 1120 + 12 * math.sin(t * 3)
    approach = seg(t, 5.2, 7.0)
    ex = lerp(ex, 330, approach); ey = lerp(ey, 1150, approach)
    shake = 5 * agit * math.sin(t * 40)
    jump = seg(t, 7.0, REVELACION + 0.1)
    arc = -90 * math.sin(math.pi * jump)
    fx = lerp(ex + shake, scx, jump); fy = lerp(ey, scy, jump) + arc
    er = lerp(68, 132, seg(t, 7.2, REVELACION + 0.35))
    er *= 1 + 0.06 * math.sin(math.pi * seg(t, REVELACION + 0.2, REVELACION + 0.7))
    if t > 2.2:
        body.append(earth(t, fx, fy, er, worry=seg(t, 5, 5.5) * (1 - rev), wow=rev))
    # destello en la revelación
    fl = seg(t, REVELACION - 0.05, REVELACION + 0.1) * (1 - seg(t, REVELACION + 0.1, REVELACION + 0.7))
    if fl > 0:
        body.append(f"<circle cx='{scx}' cy='{scy:.0f}' r='{lerp(150, 520, seg(t, REVELACION, REVELACION + 0.7)):.0f}' fill='none' stroke='#ffe9a8' stroke-width='{30 * fl:.1f}' opacity='{fl:.2f}'/>")
    s.append(zoom(scx, scy, z, "".join(body)))
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff3d0' opacity='{0.35 * fl:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
