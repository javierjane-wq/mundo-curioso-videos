"""2026-11-11-c3 · Tierra: alrededor del 90 % de un iceberg está bajo el agua.

Un iceberg simpático llega flotando; solo vemos su punta. En la revelación el agua
se aclara, entran rayos de luz y la cámara se aleja: debajo hay un bloque enorme.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.45   # el agua se aclara y aparece la parte sumergida
MUSICA = 8

WL = 1240           # línea de flotación
rng = np.random.default_rng(11)
SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 7), rng.uniform(30, 70), rng.uniform(0, 6.28)) for _ in range(55)]
BUBBLES = [(rng.uniform(80, 1000), rng.uniform(0, 1), rng.uniform(6, 16), rng.uniform(60, 130)) for _ in range(22)]

TIP = [(-215, 20), (-185, -95), (-120, -155), (-65, -160), (-20, -250), (50, -210), (100, -232), (165, -125), (200, -55), (220, 20)]
UNDER = [(220, 0), (350, 80), (430, 230), (415, 400), (330, 530), (190, 620), (20, 650), (-160, 620),
         (-310, 520), (-415, 360), (-425, 190), (-345, 70), (-215, 0)]


def pts(lista, cx, cy):
    return " ".join(f"{cx + x:.1f},{cy + y:.1f}" for x, y in lista)


def tip(t, cx, cy, rev):
    blink = 0.12 if 2.0 < (t % 2.9) < 2.12 else 1.0
    look_y = lerp(0, 9, seg(t, 5.0, 6.0))
    wide = 1 + 0.35 * seg(t, 7.45, 7.9)
    g = [f"<polygon points='{pts(TIP, cx, cy)}' fill='#f6fcff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    # facetas de hielo
    g.append(f"<polygon points='{pts([(50, -210), (100, -232), (165, -125), (200, -55), (220, 20), (95, 20), (75, -80)], cx, cy)}' fill='#c3e9f8'/>")
    g.append(f"<polygon points='{pts([(-215, 20), (-185, -95), (-130, -50), (-150, 20)], cx, cy)}' fill='#d9f2fc'/>")
    g.append(f"<polyline points='{pts([(-20, -250), (5, -160), (75, -80)], cx, cy)}' fill='none' stroke='#9fd6ee' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<polygon points='{pts(TIP, cx, cy)}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brillo
    g.append(f"<path d='M{cx-135:.1f} {cy-118:.1f} Q{cx-110:.1f} {cy-145:.1f} {cx-80:.1f} {cy-142:.1f}' stroke='#fff' stroke-width='10' fill='none' stroke-linecap='round'/>")
    # cara
    for ex in (-62, 38):
        g.append(f"<g transform='translate({cx+ex:.1f},{cy-118:.1f}) scale({wide:.3f},{wide*blink:.3f})'>"
                 f"<ellipse rx='26' ry='30' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='3' cy='{4+look_y:.1f}' r='14' fill='{INK}'/><circle cx='-2' cy='{-1+look_y:.1f}' r='5' fill='#fff'/></g>")
    for ex in (-100, 78):
        g.append(f"<ellipse cx='{cx+ex:.1f}' cy='{cy-78:.1f}' rx='17' ry='9' fill='#ff9db5' opacity='0.8'/>")
    if rev < 0.5:
        g.append(f"<path d='M{cx-32:.1f} {cy-74:.1f} Q{cx-12:.1f} {cy-52:.1f} {cx+8:.1f} {cy-74:.1f}' stroke='{INK}' stroke-width='6' fill='none' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='{cx-12:.1f}' cy='{cy-62:.1f}' rx='14' ry='18' fill='#7a2e3a' stroke='{INK}' stroke-width='6'/>")
    return "".join(g)


def under(cx, cy, rev):
    g = [f"<polygon points='{pts(UNDER, cx, cy)}' fill='{mix('#5d8fb0', '#a8e6f4', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    g.append(f"<polygon points='{pts([(220, 0), (350, 80), (430, 230), (415, 400), (330, 530), (205, 420), (240, 200), (125, 60)], cx, cy)}' fill='{mix('#4a7aa0', '#79cde6', rev)}'/>")
    g.append(f"<polygon points='{pts([(-310, 520), (-415, 360), (-425, 190), (-290, 260), (-240, 430)], cx, cy)}' fill='{mix('#6b9cbc', '#c4f0fa', rev)}'/>")
    g.append(f"<polyline points='{pts([(-120, 80), (-40, 260), (60, 330), (110, 520)], cx, cy)}' fill='none' stroke='{mix('#4a7aa0', '#7cc6df', rev)}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<polygon points='{pts(UNDER, cx, cy)}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    return "".join(g)


def fish(t):
    x = lerp(-120, 1220, seg(t, 1.0, 9.5)); y = 1560 + 30 * math.sin(t * 2.4)
    tail = 12 * math.sin(t * 14)
    return (f"<g transform='translate({x:.1f},{y:.1f})'>"
            f"<path d='M-52 0 L-86 {-26+tail:.1f} L-86 {26+tail:.1f} Z' fill='#ff8a3d' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<ellipse rx='58' ry='34' fill='#ffb13d' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-8 -32 Q4 -6 -8 30' stroke='#ff8a3d' stroke-width='8' fill='none'/>"
            f"<circle cx='28' cy='-8' r='10' fill='#fff' stroke='{INK}' stroke-width='4'/><circle cx='31' cy='-8' r='5' fill='{INK}'/></g>")


def gull(t):
    x = lerp(1180, -150, seg(t, 0.0, 6.5)); y = 1020 + 18 * math.sin(t * 1.7)
    f = 22 * math.sin(t * 9)
    return (f"<g transform='translate({x:.1f},{y:.1f})'>"
            f"<path d='M-60 {-f:.1f} Q-30 -14 0 0 Q30 -14 60 {-f:.1f}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M-60 {-f:.1f} Q-30 -14 0 0 Q30 -14 60 {-f:.1f}' fill='none' stroke='#ffffff' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='2' r='9' fill='#fff' stroke='{INK}' stroke-width='5'/></g>")


def frame(t):
    rev = seg(t, 7.45, 8.2)
    cx = lerp(800, 540, seg(t, 0, 2.6)); bob = 6 * math.sin(t * 2.2)
    tilt = 2.0 * math.sin(t * 1.6)
    cy = WL + bob
    s = ["<defs>",
         "<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#5fb4ea'/><stop offset='0.6' stop-color='#a9dcf7'/><stop offset='1' stop-color='#e6f6ff'/></linearGradient>",
         f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#1f5d98', '#3fb6d9', rev)}'/>"
         f"<stop offset='1' stop-color='{mix('#0b2348', '#1a6aa8', rev)}'/></linearGradient>",
         f"<linearGradient id='deep' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#1f5d98', '#2b8fc4', rev)}'/><stop offset='1' stop-color='{mix('#0b2348', '#0f3f78', rev)}'/></linearGradient>",
         "<radialGradient id='sun'><stop offset='0' stop-color='#fffbe6' stop-opacity='0.95'/><stop offset='1' stop-color='#fff2b0' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.8*rev*(1-seg(t, 8.0, 9.6)):.3f}'/><stop offset='1' stop-color='#bff4ff' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    body = []
    # sol suave y nubes
    body.append("<circle cx='880' cy='640' r='240' fill='url(#sun)'/>")
    body.append(f"<circle cx='880' cy='640' r='70' fill='#fff8d8' stroke='#ffe08a' stroke-width='8'/>")
    for i, (x0, y0, sc) in enumerate([(120, 760, 1.4), (700, 880, 1.1), (360, 560, 0.9)]):
        dx = (t * (10 + 6 * i)) % 1500 - 250
        body.append(f"<g transform='translate({(x0 + dx) % 1500 - 250:.0f},{y0}) scale({sc})'>"
                    f"<path d='M0 50 Q10 0 60 10 Q90 -30 140 5 Q190 -10 200 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # glaciares lejanos en el horizonte
    body.append(f"<path d='M-20 {WL+10} L60 1150 L130 1175 L210 1120 L300 {WL+10} Z' fill='#e9f7fd' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    body.append(f"<path d='M760 {WL+10} L840 1165 L910 1135 L990 1180 L1100 {WL+10} Z' fill='#d6eff9' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    body.append(gull(t))
    # fondo marino (detrás del hielo)
    body.append(f"<rect x='-400' y='{WL}' width='{W+800}' height='{H}' fill='url(#deep)'/>")
    # parte sumergida (debajo del agua) y punta
    ice = f"<g transform='rotate({tilt:.2f},{cx:.1f},{cy:.1f})'>" + under(cx, cy, rev) + tip(t, cx, cy, rev) + "</g>"
    body.append(ice)
    # agua por encima de la parte sumergida: muy opaca al principio, transparente al revelar
    op = lerp(lerp(1.0, 0.82, seg(t, 5.0, 7.3)), 0.3, rev)
    wave = " ".join(f"L{x} {WL + 9 * math.sin(x / 70 + t * 3):.1f}" for x in range(0, W + 41, 40))
    body.append(f"<path d='M0 {WL} {wave} L{W} {H} L0 {H} Z' fill='url(#sea)' opacity='{op:.3f}'/>")
    # rayos de luz y destellos tras la revelación
    if rev > 0:
        for i, x0 in enumerate((180, 420, 680, 900)):
            sw = 20 * math.sin(t * 1.3 + i)
            body.append(f"<polygon points='{x0-40+sw:.0f},{WL} {x0+40+sw:.0f},{WL} {x0+150:.0f},{H} {x0-10:.0f},{H}' fill='#ffffff' opacity='{0.16*rev:.3f}'/>")
        for i, (dx, dy) in enumerate([(-330, 150), (300, 120), (-250, 480), (260, 460), (0, 600), (380, 300), (-400, 320)]):
            a = rev * (0.5 + 0.5 * math.sin(t * 6 + i * 1.7))
            r = 12 + 6 * a
            px, py = cx + dx, cy + dy
            body.append(f"<path d='M{px:.0f} {py-r*2:.0f} L{px+r*0.5:.0f} {py-r*0.5:.0f} L{px+r*2:.0f} {py:.0f} L{px+r*0.5:.0f} {py+r*0.5:.0f} "
                        f"L{px:.0f} {py+r*2:.0f} L{px-r*0.5:.0f} {py+r*0.5:.0f} L{px-r*2:.0f} {py:.0f} L{px-r*0.5:.0f} {py-r*0.5:.0f} Z' fill='#ffffff' opacity='{a:.2f}'/>")
        body.append(f"<circle cx='{cx:.0f}' cy='{cy+300:.0f}' r='{lerp(200, 700, rev):.0f}' fill='url(#flash)'/>")
    # línea de superficie y espuma
    surf = " ".join(f"{x},{WL + 9 * math.sin(x / 70 + t * 3):.1f}" for x in range(0, W + 41, 40))
    body.append(f"<polyline points='{surf}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    body.append(f"<polyline points='{surf}' fill='none' stroke='#e8fbff' stroke-width='4' stroke-linejoin='round' transform='translate(0,8)'/>")
    for k in range(3):
        fx = cx + (-210 if k % 2 == 0 else 215) + 10 * math.sin(t * 3 + k)
        body.append(f"<ellipse cx='{fx:.0f}' cy='{WL + 14 + k * 6:.0f}' rx='{26 - k * 6}' ry='8' fill='#ffffff' opacity='0.85'/>")
    # burbujas y pez
    for bx, ph, br, sp in BUBBLES:
        yy = H + 40 - ((ph * 700 + t * sp) % 700)
        if yy > WL + 30:
            body.append(f"<circle cx='{bx + 12 * math.sin(t * 2 + bx):.0f}' cy='{yy:.0f}' r='{br:.0f}' fill='none' stroke='#dff7ff' stroke-width='4' opacity='0.75'/>")
    body.append(fish(t))
    # nieve suave
    for x0, y0, r, sp, ph in SNOW:
        yy = (y0 + t * sp) % H
        body.append(f"<circle cx='{x0 + 18 * math.sin(t * 1.2 + ph):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#ffffff' opacity='0.8'/>")
    # cámara: empieza cerca de la punta y se aleja en la revelación
    z = lerp(lerp(1.28, 1.34, seg(t, 0, 7.3)), 1.0, seg(t, 7.35, 8.3)) + 0.025 * seg(t, 8.3, 10)
    s.append(zoom(540, 1180, z, "".join(body)))
    s.append("</svg>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>" + "".join(s)
