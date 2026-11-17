"""Copo de nieve: a simple vista parece una motita blanca, pero de cerca tiene 6 puntas
(el agua, al congelarse, se ordena en hexágonos).

Composición: protagonista (copo con cara) en la mitad de abajo; arriba cielo nocturno tranquilo.
Movimiento: el copo cae balanceándose desde el fotograma 0, nieve, humo de la cabaña, estrellas,
parpadeo; una lupa se acerca y en la REVELACION la motita se convierte en un cristal de 6 puntas
con halo hexagonal, cambio de luz y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.5   # la lupa destella y aparece el cristal de 6 puntas: golpe musical
MUSICA = 6

rng = np.random.default_rng(17)
STARS = [(rng.uniform(0, W), rng.uniform(60, 1150), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(55)]
SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 8), rng.uniform(40, 110), rng.uniform(0, 6.28)) for _ in range(90)]
TREES = [(90, 1560, 1.15), (250, 1600, 0.85), (930, 1580, 1.05), (1020, 1640, 0.8), (780, 1660, 0.7)]


def cara(r, t, blink_fase=0.0):
    """Ojos grandes que parpadean, mofletes y sonrisa (centrada en 0,0; r = tamaño)."""
    blink = 0.12 if 1.5 < ((t + blink_fase) % 2.9) < 1.63 else 1.0
    ex, ey, er = 0.36 * r, -0.12 * r, 0.2 * r
    s = []
    for sx in (-ex, ex):
        s.append(f"<g transform='translate({sx:.1f},{ey:.1f}) scale(1,{blink})'>"
                 f"<ellipse rx='{er*0.85:.1f}' ry='{er:.1f}' fill='{INK}'/>"
                 f"<circle cx='{-er*0.3:.1f}' cy='{-er*0.35:.1f}' r='{er*0.34:.1f}' fill='#fff'/>"
                 f"<circle cx='{er*0.25:.1f}' cy='{er*0.3:.1f}' r='{er*0.14:.1f}' fill='#fff'/></g>")
    for sx in (-0.58 * r, 0.58 * r):
        s.append(f"<ellipse cx='{sx:.1f}' cy='{0.18*r:.1f}' rx='{0.14*r:.1f}' ry='{0.08*r:.1f}' fill='#ff9db8' opacity='0.85'/>")
    s.append(f"<path d='M{-0.17*r:.1f} {0.2*r:.1f} Q0 {0.38*r:.1f} {0.17*r:.1f} {0.2*r:.1f}' fill='#ff6f8e' "
             f"stroke='{INK}' stroke-width='{max(4, 0.045*r):.1f}' stroke-linecap='round' stroke-linejoin='round'/>")
    return "".join(s)


def motita(r, t):
    """El copo visto a simple vista: una bolita blanca esponjosa con cara."""
    bumps = "".join(f"<circle cx='{r*0.78*math.cos(a):.1f}' cy='{r*0.78*math.sin(a):.1f}' r='{r*0.36:.1f}'/>"
                    for a in np.linspace(0, 2 * math.pi, 9, endpoint=False))
    return (f"<g fill='#f4fbff' stroke='{INK}' stroke-width='{LW}'>{bumps}<circle r='{r*0.85:.1f}'/></g>"
            f"<g fill='#f4fbff'>{bumps}<circle r='{r*0.85:.1f}'/></g>"
            f"<ellipse cx='{r*0.2:.1f}' cy='{r*0.45:.1f}' rx='{r*0.7:.1f}' ry='{r*0.32:.1f}' fill='#cfe6fb' opacity='0.7'/>"
            f"<ellipse cx='{-r*0.4:.1f}' cy='{-r*0.55:.1f}' rx='{r*0.22:.1f}' ry='{r*0.12:.1f}' fill='#fff'/>"
            + cara(r * 0.9, t))


def brazo(R):
    """Un brazo del cristal (dendrita) apuntando hacia arriba, con ramitas a ±60°."""
    p = [f"M0 {-0.25*R:.1f} L0 {-R:.1f}"]
    for d, L in ((0.48, 0.30), (0.72, 0.22), (0.9, 0.12)):
        y = -d * R
        for sg in (-1, 1):
            dx = sg * L * R * math.sin(math.radians(60)); dy = -L * R * math.cos(math.radians(60))
            p.append(f"M0 {y:.1f} L{dx:.1f} {y+dy:.1f}")
    d = " ".join(p)
    tip = f"M0 {-R-0.07*R:.1f} L{0.06*R:.1f} {-R+0.02*R:.1f} L0 {-R+0.1*R:.1f} L{-0.06*R:.1f} {-R+0.02*R:.1f} Z"
    return d, tip


def cristal(R, t, brillo):
    d, tip = brazo(R)
    s = []
    for capa, (col, w) in enumerate(((INK, 0.11 * R), ("#e9f7ff", 0.065 * R), ("#8fd8ff", 0.018 * R))):
        for a in range(0, 360, 60):
            s.append(f"<g transform='rotate({a})'><path d='{d}' fill='none' stroke='{col}' stroke-width='{w:.1f}' "
                     f"stroke-linecap='round' stroke-linejoin='round'/>"
                     + (f"<path d='{tip}' fill='#e9f7ff' stroke='{INK}' stroke-width='{0.025*R:.1f}' stroke-linejoin='round'/>" if capa == 1 else "")
                     + "</g>")
    # destellos en las 6 puntas
    for i, a in enumerate(range(0, 360, 60)):
        tw = 0.6 + 0.4 * math.sin(t * 6 + i)
        x = R * 1.02 * math.sin(math.radians(a)); y = -R * 1.02 * math.cos(math.radians(a))
        rr = 0.07 * R * tw * brillo
        s.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({t*90 + i*20:.1f})' opacity='{brillo:.2f}'>"
                 f"<path d='M0 {-rr*2:.1f} L{rr*0.4:.1f} {-rr*0.4:.1f} L{rr*2:.1f} 0 L{rr*0.4:.1f} {rr*0.4:.1f} L0 {rr*2:.1f} "
                 f"L{-rr*0.4:.1f} {rr*0.4:.1f} L{-rr*2:.1f} 0 L{-rr*0.4:.1f} {-rr*0.4:.1f} Z' fill='#fffbe0'/></g>")
    # centro hexagonal con la cara
    hr = 0.34 * R
    hexa = " ".join(f"{hr*math.cos(math.radians(a+30)):.1f},{hr*math.sin(math.radians(a+30)):.1f}" for a in range(0, 360, 60))
    s.append(f"<polygon points='{hexa}' fill='#dff3ff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    hr2 = hr * 0.78
    hexa2 = " ".join(f"{hr2*math.cos(math.radians(a+30)):.1f},{hr2*math.sin(math.radians(a+30)):.1f}" for a in range(0, 360, 60))
    s.append(f"<polygon points='{hexa2}' fill='none' stroke='#9fd9fb' stroke-width='5' stroke-linejoin='round'/>")
    s.append(f"<g transform='scale(0.92)'>{cara(hr*0.95, t)}</g>")
    return "".join(s)


def pino(x, y, sc, t):
    sw = 2.5 * math.sin(t * 1.3 + x)
    g = [f"<g transform='translate({x},{y}) scale({sc}) rotate({sw:.2f})'>",
         f"<rect x='-16' y='-10' width='32' height='70' fill='#7a4a2e' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, (w, yy) in enumerate(((150, 0), (120, -90), (88, -170))):
        g.append(f"<path d='M{-w} {yy} L0 {yy-150} L{w} {yy} Z' fill='#1f7a5a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<path d='M{-w*0.55:.0f} {yy-62} L0 {yy-150} L{w*0.55:.0f} {yy-62} Q{w*0.25:.0f} {yy-45} 0 {yy-62} Q{-w*0.25:.0f} {yy-45} {-w*0.55:.0f} {yy-62} Z' "
                 f"fill='#f4fbff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def cabana(t, luz):
    x, y = 660, 1540
    g = [f"<g transform='translate({x},{y})'>"]
    # humo de la chimenea
    for i in range(4):
        k = ((t * 0.35 + i * 0.25) % 1.0)
        g.append(f"<circle cx='{95 + 30*math.sin(k*5 + i):.1f}' cy='{-190 - k*260:.1f}' r='{16 + k*28:.1f}' fill='#e6eefb' opacity='{0.75*(1-k):.2f}'/>")
    g.append(f"<rect x='75' y='-200' width='40' height='80' fill='#a0523a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-120' y='-90' width='240' height='150' fill='#b8683f' stroke='{INK}' stroke-width='{LW}'/>")
    for yy in (-55, -20, 15):
        g.append(f"<line x1='-120' y1='{yy}' x2='120' y2='{yy}' stroke='#8f4a2c' stroke-width='5'/>")
    g.append(f"<path d='M-150 -80 L0 -190 L150 -80 Z' fill='#f4fbff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-80' y='-55' width='60' height='55' rx='6' fill='{mix('#ffd36b', '#fff2b0', luz)}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<line x1='-50' y1='-55' x2='-50' y2='0' stroke='{INK}' stroke-width='5'/><line x1='-80' y1='-28' x2='-20' y2='-28' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='25' y='-30' width='55' height='90' rx='6' fill='#6e3420' stroke='{INK}' stroke-width='7'/>")
    g.append("</g>")
    return "".join(g)


def lupa(x, y, r, aro_extra, op):
    rr = r + aro_extra
    return (f"<g opacity='{op:.2f}'>"
            f"<g transform='translate({x:.1f},{y:.1f}) rotate(-35)'>"
            f"<rect x='-26' y='{rr+10:.1f}' width='52' height='{rr*1.1:.1f}' rx='20' fill='#c0542f' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-30' y='{rr-6:.1f}' width='60' height='34' rx='8' fill='#c9ced6' stroke='{INK}' stroke-width='{LW}'/></g>"
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{rr:.1f}' fill='#cdeeff' fill-opacity='0.28' stroke='{INK}' stroke-width='{LW*3.2:.1f}'/>"
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{rr:.1f}' fill='none' stroke='#ffcf4a' stroke-width='{LW*1.6:.1f}'/>"
            f"<path d='M{x-rr*0.6:.1f} {y-rr*0.25:.1f} A{rr*0.65:.1f} {rr*0.65:.1f} 0 0 1 {x-rr*0.2:.1f} {y-rr*0.62:.1f}' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.8'/>"
            "</g>")


def frame(t):
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    luz = seg(t, REVELACION - 0.1, REVELACION + 1.2)
    # cielo: noche azul -> azul hielo luminoso en la revelación
    top = mix("#141d4a", "#1b3f8f", luz); mid = mix("#2d3f86", "#3f86d6", luz); low = mix("#6d7fc4", "#9fe0ff", luz)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='0.8' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.9*luz:.3f}'/>"
            f"<stop offset='0.35' stop-color='#9fe6ff' stop-opacity='{0.7*luz:.3f}'/>"
            f"<stop offset='1' stop-color='#3f86d6' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='ventana'><stop offset='0' stop-color='#ffd36b' stop-opacity='0.55'/><stop offset='1' stop-color='#ffd36b' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    esc = []
    # estrellas
    for sx, sy, sr, ph in STARS:
        a = 0.35 + 0.35 * math.sin(t * 2.5 + ph)
        esc.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # luna creciente baja
    esc.append(f"<g transform='translate(190,1160)'><circle r='70' fill='#fff4c9' stroke='{INK}' stroke-width='{LW}'/>"
               f"<circle cx='34' cy='-22' r='62' fill='{mix('#3f4f95', '#5aa0e0', luz)}'/></g>")
    # colinas nevadas
    esc.append(f"<path d='M0 1480 Q270 1380 560 1450 T1080 1420 L1080 1920 L0 1920 Z' fill='{mix('#c9d8f2', '#e4f6ff', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, sc in TREES[:2] + TREES[2:3]:
        esc.append(pino(x, y, sc, t))
    esc.append(f"<circle cx='620' cy='1510' r='160' fill='url(#ventana)'/>")
    esc.append(cabana(t, luz))
    for x, y, sc in TREES[3:]:
        esc.append(pino(x, y, sc, t))
    esc.append(f"<path d='M0 1690 Q300 1610 620 1680 T1080 1660 L1080 1920 L0 1920 Z' fill='{mix('#e3ecfb', '#f6fcff', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(f"<path d='M120 1790 Q320 1760 520 1800' fill='none' stroke='#b9cdee' stroke-width='10' stroke-linecap='round'/>"
               f"<path d='M640 1840 Q820 1810 990 1845' fill='none' stroke='#b9cdee' stroke-width='10' stroke-linecap='round'/>")
    # copo protagonista: cae balanceándose y se queda flotando
    cx = 540 + 70 * math.sin(t * 1.5) * (1 - 0.6 * seg(t, 4.5, 7.4)) * (1 - rev)
    cy = lerp(1060, 1290, seg(t, 0, 4.6)) + 10 * math.sin(t * 2.2)
    rot = 12 * math.sin(t * 1.5) * (1 - rev) + 20 * seg(t, REVELACION, 10)
    # halo de la revelación
    if luz > 0:
        esc.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{lerp(200, 560, luz):.0f}' fill='url(#halo)'/>")
        hr = 430 * rebote(t, REVELACION + 0.1, 0.7)
        if hr > 0:
            for k, (rr, op) in enumerate(((hr, 0.55), (hr * 0.78, 0.35))):
                pts = " ".join(f"{cx + rr*math.cos(math.radians(a + 30 + t*12*(1-2*k))):.1f},{cy + rr*math.sin(math.radians(a + 30 + t*12*(1-2*k))):.1f}" for a in range(0, 360, 60))
                esc.append(f"<polygon points='{pts}' fill='none' stroke='#eaffff' stroke-width='8' stroke-linejoin='round' opacity='{op*luz:.2f}'/>")
    # motita (antes) -> cristal (después)
    mot_esc = 1 - rev
    if mot_esc > 0.01:
        esc.append(f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({mot_esc:.3f})'>{motita(95, t)}</g>")
    cr = rebote(t, REVELACION, 0.6)
    if cr > 0:
        esc.append(f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({cr:.3f})'>{cristal(300, t, luz)}</g>")
    # lupa: entra por la derecha, se coloca sobre el copo y en la revelación se abre y desaparece
    li = seg(t, 4.9, 6.6)
    if li > 0 and t < REVELACION + 0.6:
        lx = lerp(1300, cx, li) + 6 * math.sin(t * 9) * seg(t, 6.6, 7.0)
        ly = lerp(1500, cy, li)
        esc.append(lupa(lx, ly, 150, 700 * seg(t, REVELACION - 0.05, REVELACION + 0.55), 1 - seg(t, REVELACION, REVELACION + 0.55)))
    # nieve cayendo
    for px, py, pr, sp, ph in SNOW:
        yy = (py + t * sp) % (H + 40) - 20
        op = 0.5 if yy < 1000 else 0.85
        esc.append(f"<circle cx='{px + 22*math.sin(t*1.2 + ph):.0f}' cy='{yy:.0f}' r='{pr * (0.7 if yy < 1000 else 1):.1f}' fill='#fff' opacity='{op:.2f}'/>")
    # destello blanco en la revelación
    fl = max(0.0, 1 - abs(t - REVELACION - 0.05) / 0.25)
    z = 1 + 0.12 * seg(t, REVELACION, 10)
    s.append(zoom(cx, cy, z, "".join(esc)))
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.55*fl:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
