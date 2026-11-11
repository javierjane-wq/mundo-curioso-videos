"""2026-11-11-c2 · El arcoíris es en realidad un círculo completo: desde el suelo el horizonte tapa la mitad.

0-2,5 s  tras la lluvia aparece un arcoíris sobre las colinas; entra una avioneta
2,5-5 s  desde el suelo solo se ve medio arco (el resto queda bajo el horizonte)
5-7,5 s  la avioneta sube: las colinas bajan y desaparecen, nubes que pasan
7,45 s   REVELACION: el arcoíris se completa en un CÍRCULO brillante; destello y zoom
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 4

rng = np.random.default_rng(23)
RAIN = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(40, 80), rng.uniform(900, 1300)) for _ in range(70)]
SPARK = [(rng.uniform(0, 6.283), rng.uniform(0.85, 1.25), rng.uniform(5, 12), rng.uniform(0, 6.28)) for _ in range(36)]
FLY = [(rng.uniform(-100, W + 100), rng.uniform(0, 1), rng.uniform(1.0, 1.8)) for _ in range(5)]
CX, CY, R = 540, 1470, 395          # centro y radio del arcoíris (centro = horizonte)
BAND = 17
COLS = ["#ff3d3d", "#ff8c1a", "#ffd60a", "#3fcf4e", "#2f8cff", "#4a4fd6", "#9b4dff"]
TREES = [(140, 1500, 1.0), (230, 1520, 0.8), (860, 1560, 1.1), (960, 1540, 0.85)]


def nube(x, y, s, col="#ffffff", sw=7, op=1.0):
    d = "M-120 30 Q-150 -10 -100 -30 Q-90 -90 -20 -70 Q20 -120 80 -70 Q150 -80 140 -10 Q180 20 120 40 Z"
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})' opacity='{op:.2f}'>"
            f"<path d='{d}' fill='{col}' stroke='{INK}' stroke-width='{sw / s:.1f}' stroke-linejoin='round'/></g>")


def _dash(t, circ):
    """Parte visible del circulo: primero se dibuja el arco de izquierda a derecha (0-1,6 s);
    al subir la avioneta (4,9 s - revelacion) los dos extremos bajan hasta cerrarse abajo."""
    if t < 1.6:
        L = circ * 0.5 * (0.2 + 0.8 * seg(t, 0.0, 1.6))
        return f"transform='rotate(180 {CX} {CY})' stroke-dasharray='{L:.1f} {circ:.1f}'"
    f = seg(t, 4.9, REVELACION)
    if f >= 0.999:
        return ""
    L = circ * (0.5 + 0.5 * f)
    return (f"transform='rotate(-90 {CX} {CY})' stroke-dasharray='{L:.1f} {circ - L:.1f}' "
            f"stroke-dashoffset='{L / 2:.1f}'")


def arcoiris(t, brillo):
    """Circulo de 7 bandas con contorno."""
    s = []
    op = lerp(0.72, 1.0, brillo)
    for i, c in enumerate(COLS):
        r = R - i * BAND - BAND / 2
        s.append(f"<circle cx='{CX}' cy='{CY}' r='{r:.1f}' fill='none' stroke='{c}' stroke-width='{BAND + 1}' "
                 f"opacity='{op:.2f}' {_dash(t, 2 * math.pi * r)}/>")
    for r in (R, R - 7 * BAND):
        s.append(f"<circle cx='{CX}' cy='{CY}' r='{r}' fill='none' stroke='{INK}' stroke-width='6' "
                 f"opacity='{op:.2f}' {_dash(t, 2 * math.pi * r)}/>")
    return "".join(s)


def colinas(t, d):
    """Paisaje del suelo; d = cuánto ha bajado (la cámara sube)."""
    g = [f"<g transform='translate(0,{d:.1f})'>"]
    g.append(f"<path d='M-20 1490 Q160 1420 360 1470 Q560 1520 760 1450 Q930 1400 1100 1470 L1100 2600 L-20 2600 Z' "
             f"fill='#69c26a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-20 1620 Q240 1540 520 1600 Q800 1660 1100 1580 L1100 2600 L-20 2600 Z' "
             f"fill='#4fae55' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-20 1780 Q300 1700 640 1760 Q880 1800 1100 1740 L1100 2600 L-20 2600 Z' "
             f"fill='#3e9a47' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for x, y, s in TREES:
        sway = 3 * math.sin(t * 2.2 + x)
        g.append(f"<g transform='translate({x},{y}) scale({s}) rotate({sway:.1f})'>"
                 f"<rect x='-11' y='-10' width='22' height='60' rx='6' fill='#8a5a36' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='0' cy='-50' r='52' fill='#2f8f3e' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='-16' cy='-66' r='14' fill='#55b85f'/></g>")
    # charquitos que brillan
    for px, py in ((330, 1700), (820, 1680)):
        g.append(f"<ellipse cx='{px}' cy='{py}' rx='55' ry='14' fill='#9fd8ff' stroke='{INK}' stroke-width='5'/>")
    # florecillas
    for i, (fx, fy) in enumerate(((90, 1860), (260, 1800), (800, 1870), (1000, 1820), (380, 1640))):
        b = 1 + 0.08 * math.sin(t * 3 + i)
        g.append(f"<g transform='translate({fx},{fy}) scale({b:.3f})'>"
                 + "".join(f"<circle cx='{14*math.cos(a):.1f}' cy='{14*math.sin(a):.1f}' r='10' fill='#fff' stroke='{INK}' stroke-width='3'/>"
                           for a in [k * 1.2566 for k in range(5)])
                 + f"<circle r='8' fill='#ffd23f' stroke='{INK}' stroke-width='3'/></g>")
    g.append("</g>")
    return "".join(g)


def avioneta(t, asombro):
    """Avioneta original de hélice con un pasajero en la ventanilla."""
    x = lerp(-40, 300, seg(t, 0, 2.6)) + 30 * seg(t, 2.6, 10)
    y = 1030 + 70 * seg(t, REVELACION - 0.2, 8.4) + 9 * math.sin(t * 2.4)
    climb = seg(t, 4.9, 5.6) - seg(t, 7.0, 7.7)
    ang = -9 * climb + 2 * math.sin(t * 1.7)
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    eye = lerp(13, 17, asombro)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.2f})'>"]
    # estela
    g.append(f"<path d='M-190 6 L-330 0 M-190 28 L-300 30' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.7'/>")
    # ala trasera (al fondo)
    g.append(f"<path d='M-10 10 L-60 -48 L-20 -48 L50 8 Z' fill='#c93d3d' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # cola
    g.append(f"<path d='M-150 -10 L-195 -92 L-150 -92 L-100 -14 Z' fill='#e04848' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-160 6 L-215 -6 L-208 18 L-150 22 Z' fill='#e04848' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # fuselaje
    g.append(f"<path d='M-180 -4 Q-170 -40 -60 -44 L110 -42 Q170 -40 182 4 Q172 44 110 46 L-60 44 Q-150 40 -180 10 Z' "
             f"fill='#f6f2ea' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-170 14 Q-120 26 -60 26 L176 24' fill='none' stroke='#e04848' stroke-width='12'/>")
    # ventanillas pequeñas
    for wx in (-110, -70):
        g.append(f"<rect x='{wx}' y='-26' width='26' height='26' rx='9' fill='#9fd8ff' stroke='{INK}' stroke-width='5'/>")
    # ventanilla grande con el pasajero
    g.append(f"<rect x='-28' y='-38' width='92' height='60' rx='22' fill='#bfe7ff' stroke='{INK}' stroke-width='6'/>")
    g.append("<clipPath id='win'><rect x='-25' y='-35' width='86' height='54' rx='20'/></clipPath>")
    g.append("<g clip-path='url(#win)'>")
    g.append(f"<circle cx='18' cy='0' r='30' fill='#f5c9a0' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M-14 -10 Q-6 -34 18 -32 Q44 -32 50 -8 Q30 -22 -14 -10 Z' fill='#5a3a22'/>")
    for ex in (8, 30):
        g.append(f"<g transform='translate({ex},-4) scale(1,{blink})'><circle r='{eye*0.55:.1f}' fill='#fff' stroke='{INK}' stroke-width='3'/>"
                 f"<circle cx='{lerp(1, 2, asombro):.1f}' cy='{lerp(2, 1, asombro):.1f}' r='{eye*0.3:.1f}' fill='{INK}'/></g>")
    if asombro > 0.3:
        g.append(f"<ellipse cx='20' cy='14' rx='{4 + 3*asombro:.1f}' ry='{4 + 5*asombro:.1f}' fill='#8a2a2a'/>")
    else:
        g.append(f"<path d='M12 12 Q20 18 28 12' fill='none' stroke='{INK}' stroke-width='3' stroke-linecap='round'/>")
    g.append("</g>")
    # morro y hélice
    g.append(f"<path d='M170 -20 Q200 0 170 22 Z' fill='#e04848' stroke='{INK}' stroke-width='7'/>")
    sp = abs(math.sin(t * 40))
    g.append(f"<ellipse cx='198' cy='0' rx='9' ry='{lerp(16, 70, sp):.1f}' fill='#d9d2c4' stroke='{INK}' stroke-width='5' opacity='0.85'/>")
    g.append(f"<circle cx='196' cy='0' r='10' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    # ala delantera
    g.append(f"<path d='M-30 6 L-90 78 L-40 82 L60 12 Z' fill='#e04848' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rise = seg(t, 4.9, 7.4)                     # la cámara sube
    d = 435 * seg(t, 4.9, REVELACION) + 700 * seg(t, REVELACION, 8.3)   # el suelo baja: el circulo se cierra justo en la revelacion
    rev = seg(t, REVELACION, REVELACION + 0.6)  # brillo final
    flash = clamp(1 - abs(t - REVELACION - 0.08) / 0.35)
    asombro = seg(t, 7.0, 7.7)
    top = mix("#7cc6f4", "#4fa9ee", rise); low = mix("#cfeeff", "#bfe4ff", rise)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='halo'><stop offset='0.55' stop-color='#ffffff' stop-opacity='0'/>"
            f"<stop offset='0.8' stop-color='#fff6d0' stop-opacity='{0.75*rev:.3f}'/>"
            "<stop offset='1' stop-color='#ffffff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='sunlight' cx='0' cy='0' r='1'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.9'/>"
            "<stop offset='1' stop-color='#fffbe0' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>",
         f"<rect width='{W}' height='{H}' fill='url(#sunlight)' opacity='0.5'/>"]
    # nubes altas tranquilas (zona de textos)
    for i, (cx, cy, sc) in enumerate(((180, 300, 0.9), (860, 200, 1.1), (620, 760, 0.8))):
        dx = (t * (10 + 4 * i)) % 1500 - 300
        s.append(nube((cx + dx) % 1500 - 200, cy, sc, "#ffffff", 6, 0.8))
    body = []
    # mar de nubes al fondo (se descubre al subir)
    for i, (nx, ny, ns) in enumerate(((120, 1800, 1.6), (430, 1860, 1.9), (760, 1810, 1.7), (1000, 1870, 1.5),
                                      (280, 1700, 1.2), (900, 1720, 1.2))):
        bob = 6 * math.sin(t * 1.3 + i)
        body.append(nube(nx, ny + bob + lerp(220, 0, rise), ns, "#f4f9ff", 7))
    # cortina de lluvia
    for x, ph, ln, sp in RAIN:
        yy = 1000 + ((ph * 900 + t * sp) % 900)
        body.append(f"<line x1='{x:.0f}' y1='{yy:.0f}' x2='{x - 10:.0f}' y2='{yy + ln:.0f}' stroke='#7fa9d6' stroke-width='5' "
                    f"stroke-linecap='round' opacity='0.45'/>")
    # halo y arcoíris
    if rev > 0:
        body.append(f"<circle cx='{CX}' cy='{CY}' r='{R + 140}' fill='url(#halo)'/>")
    body.append(arcoiris(t, rev))
    # destellos alrededor del círculo
    if rev > 0:
        for a, k, sz, ph in SPARK:
            rr = (R - 3.5 * BAND) + (k - 1) * 260
            px, py = CX + rr * math.cos(a + t * 0.3), CY + rr * math.sin(a + t * 0.3)
            tw = rev * (0.5 + 0.5 * math.sin(t * 7 + ph))
            sz2 = sz * (0.6 + tw)
            body.append(f"<path d='M{px:.0f} {py - sz2*2:.0f} L{px + sz2*0.5:.0f} {py:.0f} L{px:.0f} {py + sz2*2:.0f} "
                        f"L{px - sz2*0.5:.0f} {py:.0f} Z M{px - sz2*2:.0f} {py:.0f} L{px:.0f} {py - sz2*0.5:.0f} "
                        f"L{px + sz2*2:.0f} {py:.0f} L{px:.0f} {py + sz2*0.5:.0f} Z' fill='#fffbe6' opacity='{tw:.2f}'/>")
    # el suelo (tapa la mitad de abajo hasta que la cámara sube)
    if d < 1100:
        body.append(colinas(t, d))
    # nubes que pasan de largo mientras se sube
    for x0, ph, sc in FLY:
        k = clamp((t - 4.9 - ph * 1.6) / 1.2)
        if 0 < k < 1:
            body.append(nube(x0, lerp(900, 2300, k), sc, "#ffffff", 8, 0.95))
    body.append(avioneta(t, asombro))
    z = 1 + 0.12 * seg(t, REVELACION - 0.1, 10)
    s.append(zoom(CX, CY - 60, z, "".join(body)))
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.55*flash:.2f}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
