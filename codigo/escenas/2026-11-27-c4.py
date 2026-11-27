"""2026-11-27-c4 · La bombilla que más tiempo lleva encendida: la Centennial Light (Livermore, California),
encendida desde 1901 en un cuartel de bomberos: 125 años (récord Guinness).

Una bombilla antigua de filamento de carbono (personaje original con cara) baja colgando de su cable en
un cuartel de bomberos (casco, cubo y manguera). Por la ventana pasan los días y las noches cada vez más
deprisa y el reloj gira sin parar, pero ella sigue encendida. Revelación: se hace de noche, la bombilla
brilla con un gran halo, rayos y confeti de cumpleaños, y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso

DUR = 10.0
REVELACION = 6.8   # la bombilla se ilumina a lo grande: golpe musical
MUSICA = 5

PIVOTE = (540, 0)
BX, BY = 540, 1120           # casquillo de la bombilla (posición final)
BS = 1.45                    # escala de la bombilla
SUELO = 1600

rng = np.random.default_rng(1901)
MOTAS = [(rng.uniform(260, 820), rng.uniform(1000, 1600), rng.uniform(3, 6), rng.uniform(0, 6.28)) for _ in range(26)]
CONFETI = [(rng.uniform(40, 1040), rng.uniform(-300, 300), rng.uniform(0, 360), rng.uniform(150, 320),
            ["#ff5a5f", "#ffd23f", "#4cc9f0", "#7bd389", "#c77dff", "#ff9f1c"][i % 6]) for i in range(46)]
ESTRELLAS = [(rng.uniform(745, 985), rng.uniform(1045, 1310), rng.uniform(2, 4)) for _ in range(9)]


def fase(t):
    """Ciclos de día y noche vistos por la ventana (se aceleran a partir de 4,5 s)."""
    if t < 4.5:
        return 0.04 * t
    d = min(t, REVELACION) - 4.5
    p = 0.18 + 0.3 * d + 0.5 * 1.17 * d * d
    return p


def noche(t):
    n = 0.5 - 0.5 * math.cos(2 * math.pi * fase(t))
    return lerp(n, 1.0, seg(t, 6.5, 7.0))


def pared(t, nf):
    s = []
    wall = mix("#f6e6c4", "#efd9ae", 0.3)
    s.append(f"<rect width='{W}' height='{H}' fill='{wall}'/>")
    # papel pintado: rayas verticales muy suaves
    for x in range(0, W, 90):
        s.append(f"<rect x='{x}' y='0' width='40' height='{1380}' fill='#ead6ac' opacity='0.55'/>")
    # moldura del techo
    s.append(f"<rect x='0' y='0' width='{W}' height='46' fill='#c98b55' stroke='{INK}' stroke-width='{LW}'/>")
    # zócalo de ladrillo
    s.append(f"<rect x='-10' y='1380' width='{W + 20}' height='{SUELO - 1380}' fill='#c4553b' stroke='{INK}' stroke-width='{LW}'/>")
    for fila, y in enumerate(range(1380, SUELO, 44)):
        off = 0 if fila % 2 == 0 else 55
        s.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='#8e3524' stroke-width='5'/>")
        for x in range(-55 + off, W, 110):
            s.append(f"<line x1='{x}' y1='{y}' x2='{x}' y2='{y + 44}' stroke='#8e3524' stroke-width='5'/>")
    s.append(f"<rect x='-10' y='1366' width='{W + 20}' height='22' fill='#8a5a33' stroke='{INK}' stroke-width='7'/>")
    # suelo de madera
    s.append(f"<rect x='-10' y='{SUELO}' width='{W + 20}' height='{H - SUELO + 10}' fill='#b9824f' stroke='{INK}' stroke-width='{LW}'/>")
    for i, y in enumerate((1680, 1780, 1880)):
        s.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='#8d5d33' stroke-width='6'/>")
        for x in range(120 + 160 * (i % 2), W, 320):
            s.append(f"<line x1='{x}' y1='{y - 100 + (0 if i else 20)}' x2='{x}' y2='{y}' stroke='#8d5d33' stroke-width='6'/>")
    return "".join(s)


def ventana(t, nf):
    x0, y0, w, h = 730, 1030, 270, 300
    p = fase(t) % 1.0
    sky = mix("#8fd3ff", "#1b2350", nf)
    s = [f"<clipPath id='vent'><rect x='{x0}' y='{y0}' width='{w}' height='{h}'/></clipPath>"]
    s.append(f"<rect x='{x0 - 22}' y='{y0 - 22}' width='{w + 44}' height='{h + 44}' rx='10' fill='#8a5a33' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{x0}' y='{y0}' width='{w}' height='{h}' fill='{sky}' stroke='{INK}' stroke-width='6'/>")
    s.append("<g clip-path='url(#vent)'>")
    for sx, sy, sr in ESTRELLAS:
        a = clamp((nf - 0.5) * 2)
        if a > 0.02:
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # el Sol de día y la Luna de noche cruzan la ventana en arco
    if p < 0.5:
        k = p / 0.5; cx = lerp(x0 - 40, x0 + w + 40, 1 - k); cy = y0 + 210 - 170 * math.sin(math.pi * k)
        s.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='38' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    else:
        k = (p - 0.5) / 0.5; cx = lerp(x0 - 40, x0 + w + 40, 1 - k); cy = y0 + 210 - 170 * math.sin(math.pi * k)
        s.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='32' fill='#f4f1de' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{cx + 14:.0f}' cy='{cy - 8:.0f}' r='26' fill='{sky}'/>")
    # tejados lejanos
    roof = mix("#6d8fb0", "#141a3a", nf)
    s.append(f"<path d='M{x0} {y0 + 260} L{x0 + 60} {y0 + 215} L{x0 + 120} {y0 + 255} L{x0 + 180} {y0 + 205} L{x0 + 270} {y0 + 250} L{x0 + 270} {y0 + h} L{x0} {y0 + h} Z' fill='{roof}' stroke='{INK}' stroke-width='5'/>")
    s.append("</g>")
    # cruceta y alféizar
    s.append(f"<line x1='{x0 + w / 2}' y1='{y0}' x2='{x0 + w / 2}' y2='{y0 + h}' stroke='#8a5a33' stroke-width='16'/>")
    s.append(f"<line x1='{x0}' y1='{y0 + h / 2}' x2='{x0 + w}' y2='{y0 + h / 2}' stroke='#8a5a33' stroke-width='16'/>")
    s.append(f"<rect x='{x0 - 40}' y='{y0 + h + 14}' width='{w + 80}' height='26' rx='8' fill='#a06a3c' stroke='{INK}' stroke-width='7'/>")
    # telaraña que aparece con los años
    tw = seg(t, 4.9, 6.6)
    if tw > 0.02:
        cx, cy = x0 - 22, y0 - 22
        web = [f"<g opacity='{0.85 * tw:.2f}' stroke='#ffffff' stroke-width='3' fill='none'>"]
        for a in (10, 35, 60, 80):
            r = 110 * tw
            web.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + r * math.cos(math.radians(a)):.0f}' y2='{cy + r * math.sin(math.radians(a)):.0f}'/>")
        for r in (35, 65, 95):
            rr = r * tw
            pts = " ".join(f"{cx + rr * math.cos(math.radians(a)):.0f},{cy + rr * math.sin(math.radians(a)):.0f}" for a in (10, 35, 60, 80))
            web.append(f"<polyline points='{pts}'/>")
        web.append("</g>")
        s.append("".join(web))
    return "".join(s)


def reloj(t):
    cx, cy, r = 190, 1075, 88
    # las manecillas giran cada vez más rápido
    vel = 1 + 25 * seg(t, 4.5, REVELACION) ** 1.5
    ang_m = (t * 40 * vel) % 360
    ang_h = ang_m / 12
    swing = 6 * math.sin(t * 2 * math.pi / 1.2)
    s = [f"<circle cx='{cx}' cy='{cy}' r='{r + 14}' fill='#8a5a33' stroke='{INK}' stroke-width='{LW}'/>",
         f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#fffaf0' stroke='{INK}' stroke-width='6'/>"]
    for i in range(12):
        a = math.radians(i * 30)
        l = 16 if i % 3 == 0 else 8
        s.append(f"<line x1='{cx + (r - 8) * math.sin(a):.1f}' y1='{cy - (r - 8) * math.cos(a):.1f}' "
                 f"x2='{cx + (r - 8 - l) * math.sin(a):.1f}' y2='{cy - (r - 8 - l) * math.cos(a):.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + 44 * math.sin(math.radians(ang_h)):.1f}' y2='{cy - 44 * math.cos(math.radians(ang_h)):.1f}' stroke='{INK}' stroke-width='11' stroke-linecap='round'/>")
    s.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + 70 * math.sin(math.radians(ang_m)):.1f}' y2='{cy - 70 * math.cos(math.radians(ang_m)):.1f}' stroke='#d62828' stroke-width='7' stroke-linecap='round'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='10' fill='{INK}'/>")
    # péndulo debajo
    s.append(f"<g transform='translate({cx},{cy + r + 14}) rotate({swing:.1f})'>"
             f"<line x1='0' y1='0' x2='0' y2='90' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='0' cy='100' r='20' fill='#ffd23f' stroke='{INK}' stroke-width='6'/></g>")
    return "".join(s)


def casco(x, y):
    """Casco de bombero clásico colgado de un gancho."""
    return (f"<g transform='translate({x},{y})'>"
            f"<rect x='-8' y='-70' width='16' height='34' rx='5' fill='#6b6b6b' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-150 40 Q-140 10 -95 8 L95 8 Q160 14 175 52 Q100 60 -150 40 Z' fill='#c1121f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-95 12 Q-95 -62 0 -66 Q95 -62 95 12 Z' fill='#e63946' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-40 -60 Q0 -76 40 -60' fill='none' stroke='#ffd23f' stroke-width='8' stroke-linecap='round'/>"
            f"<path d='M-34 -34 L34 -34 L28 10 L0 22 L-28 10 Z' fill='#ffd23f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='-8' r='11' fill='#e63946' stroke='{INK}' stroke-width='5'/>"
            "</g>")


def cubo(x, y):
    return (f"<g transform='translate({x},{y})'>"
            f"<ellipse cx='0' cy='118' rx='95' ry='16' fill='#000' opacity='0.2'/>"
            f"<path d='M-80 0 L80 0 L62 115 L-62 115 Z' fill='#e63946' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='0' rx='80' ry='18' fill='#a4161a' stroke='{INK}' stroke-width='7'/>"
            f"<rect x='-72' y='40' width='144' height='18' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>"
            f"<path d='M-78 2 Q0 -110 78 2' fill='none' stroke='{INK}' stroke-width='8'/></g>")


def manguera(x, y):
    s = [f"<g transform='translate({x},{y})'>",
         f"<ellipse cx='0' cy='92' rx='170' ry='24' fill='#000' opacity='0.2'/>"]
    for i, r in enumerate((150, 118, 86, 54)):
        s.append(f"<ellipse cx='0' cy='{-i * 18}' rx='{r + 10}' ry='{(r + 10) * 0.42:.0f}' fill='{'#e9c46a' if i % 2 == 0 else '#d4a94e'}' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<ellipse cx='0' cy='-72' rx='40' ry='16' fill='#b9824f' stroke='{INK}' stroke-width='6'/>")
    # boquilla de latón
    s.append(f"<path d='M140 10 L215 -20 L222 -6 L150 30 Z' fill='#d4a017' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    s.append("</g>")
    return "".join(s)


def bombilla(t, brillo, reve):
    """Bombilla antigua de filamento de carbono con cara: casquillo de latón arriba, punta abajo."""
    blink = 0.12 if ((t + 1.2) % 2.7) < 0.12 else 1.0
    sq = 1 + 0.05 * reve * math.sin(math.pi * clamp((t - REVELACION) / 0.5))
    glass = mix("#fff3c4", "#fffbe8", reve)
    fil = mix("#ff8c1a", "#fff0a0", reve)
    s = [f"<g transform='scale({sq:.3f})'>"]
    # portalámparas de porcelana y casquillo de latón
    s.append(f"<rect x='-36' y='-74' width='72' height='44' rx='10' fill='#f8f4ea' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M-34 -32 L34 -32 L32 8 L-32 8 Z' fill='#d4a017' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for yy in (-20, -6):
        s.append(f"<line x1='-32' y1='{yy}' x2='32' y2='{yy + 4}' stroke='#8a6a10' stroke-width='5'/>")
    # cristal
    s.append(f"<path d='M-34 6 C-40 46 -100 70 -100 150 C-100 225 -44 258 -12 268 L0 292 L12 268 C44 258 100 225 100 150 C100 70 40 46 34 6 Z' "
             f"fill='{glass}' fill-opacity='0.92' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # filamento de carbono (bucle) que brilla
    path = "M-12 10 L-12 50 C-55 70 -60 118 -28 122 C-4 125 -20 92 0 92 C20 92 4 125 28 122 C60 118 55 70 12 50 L12 10"
    s.append(f"<path d='{path}' fill='none' stroke='{fil}' stroke-width='{14 + 10 * brillo:.1f}' stroke-linecap='round' opacity='{0.35 + 0.3 * brillo:.2f}'/>")
    s.append(f"<path d='{path}' fill='none' stroke='{fil}' stroke-width='6' stroke-linecap='round'/>")
    # cara
    for ex in (-40, 40):
        s.append(f"<g transform='translate({ex},168) scale(1,{blink})'>"
                 f"<ellipse rx='22' ry='26' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='3' cy='4' r='12' fill='{INK}'/><circle cx='-3' cy='-4' r='5' fill='#fff'/></g>")
    s.append(f"<ellipse cx='-66' cy='206' rx='14' ry='9' fill='#ff8fa3' opacity='0.8'/>")
    s.append(f"<ellipse cx='66' cy='206' rx='14' ry='9' fill='#ff8fa3' opacity='0.8'/>")
    if reve > 0.3:
        s.append(f"<path d='M-26 210 Q0 250 26 210 Z' fill='#c1121f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    else:
        s.append(f"<path d='M-22 212 Q0 232 22 212' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # reflejo del cristal
    s.append(f"<path d='M-70 110 Q-78 150 -62 190' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.85'/>")
    s.append("</g>")
    return "".join(s)


def frame(t):
    nf = noche(t)
    reve = seg(t, REVELACION - 0.15, REVELACION + 0.45)
    # bajada inicial con rebote y balanceo suave del cable
    drop = 1 - math.exp(-5 * t) * math.cos(9 * t)
    dy = lerp(-430, 0, clamp(drop, 0, 1.15))
    ang = 2.0 * math.sin(t * 2 * math.pi / 2.6) * (1 - 0.6 * reve) + 4 * math.exp(-2.5 * t) * math.sin(t * 7)
    brillo = 0.55 + 0.1 * pulso(t, 0.9) + 0.45 * reve
    z = 1 + 0.22 * seg(t, REVELACION - 0.1, REVELACION + 0.8) + 0.03 * seg(t, 8.2, 10)

    defs = (f"<radialGradient id='halo'><stop offset='0' stop-color='#fff8d6' stop-opacity='{0.85:.2f}'/>"
            f"<stop offset='0.35' stop-color='#ffd76a' stop-opacity='{0.45 + 0.15 * reve:.2f}'/>"
            f"<stop offset='1' stop-color='#ffb703' stop-opacity='0'/></radialGradient>")
    s = []
    s.append(pared(t, nf))
    s.append(ventana(t, nf))
    s.append(reloj(t))
    s.append(casco(190, 1430))
    s.append(cubo(190, 1660))
    s.append(manguera(840, 1700))
    # la habitación se oscurece de noche (la ventana ya lleva su propio cielo)
    s.append(f"<rect width='{W}' height='{H}' fill='#0e1433' opacity='{0.5 * nf:.3f}'/>")

    # posición de la bombilla (cuelga del pivote y se balancea)
    a = math.radians(ang)
    L = BY + dy - PIVOTE[1]
    bx = PIVOTE[0] + L * math.sin(a); by = PIVOTE[1] + L * math.cos(a)
    cy_glow = by + 150 * BS
    # halo: pequeño y cálido (4 vatios); enorme en la revelación
    hr = lerp(330, 380, brillo) * (1 + 1.1 * reve)
    s.append(f"<circle cx='{bx:.1f}' cy='{cy_glow:.1f}' r='{hr:.0f}' fill='url(#halo)' opacity='{0.35 + 0.35 * nf + 0.1 * reve:.2f}'/>")
    # rayos de luz en la revelación
    if reve > 0.01:
        rays = [f"<g transform='translate({bx:.1f},{cy_glow:.1f}) rotate({t * 18:.1f})' opacity='{0.32 * reve:.2f}'>"]
        for i in range(12):
            rays.append(f"<path d='M0 0 L{-40} {-(700 * reve):.0f} L{40} {-(700 * reve):.0f} Z' fill='#fff3b0' transform='rotate({i * 30})'/>")
        rays.append("</g>")
        s.append("".join(rays))
    # motas de polvo flotando en la luz
    for mx, my, mr, ph in MOTAS:
        yy = (my - t * 25) % 600 + 1000
        op = 0.25 + 0.35 * nf
        s.append(f"<circle cx='{mx + 18 * math.sin(t * 1.3 + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#fff6c8' opacity='{op:.2f}'/>")
    # cable
    s.append(f"<line x1='{PIVOTE[0]}' y1='40' x2='{bx:.1f}' y2='{by - 70 * BS:.1f}' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    s.append(f"<rect x='{PIVOTE[0] - 30}' y='30' width='60' height='26' rx='8' fill='#f8f4ea' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<g transform='translate({bx:.1f},{by:.1f}) rotate({-ang:.2f}) scale({BS})'>{bombilla(t, brillo, reve)}</g>")
    # destellos alrededor
    if reve > 0.01:
        for i in range(8):
            ang2 = i * 45 + 20 * t
            rr = 330 + 30 * math.sin(t * 4 + i)
            sx = bx + rr * math.cos(math.radians(ang2)); sy = cy_glow + rr * math.sin(math.radians(ang2))
            k = 24 * reve * (0.7 + 0.3 * math.sin(t * 9 + i))
            s.append(f"<path d='M{sx:.0f} {sy - k:.0f} Q{sx:.0f} {sy:.0f} {sx + k:.0f} {sy:.0f} Q{sx:.0f} {sy:.0f} {sx:.0f} {sy + k:.0f} "
                     f"Q{sx:.0f} {sy:.0f} {sx - k:.0f} {sy:.0f} Q{sx:.0f} {sy:.0f} {sx:.0f} {sy - k:.0f} Z' fill='#fffbe0' stroke='#ffb703' stroke-width='3'/>")
    # confeti de cumpleaños (cae en la mitad de abajo)
    if t > REVELACION:
        dt = t - REVELACION
        for cx, cy0, rot, vel, col in CONFETI:
            yy = 960 + cy0 + vel * dt * 1.6
            if yy < 960 or yy > 1950:
                continue
            xx = cx + 30 * math.sin(dt * 3 + rot)
            s.append(f"<rect x='{xx - 10:.0f}' y='{yy - 6:.0f}' width='20' height='12' rx='3' fill='{col}' stroke='{INK}' stroke-width='3' "
                     f"transform='rotate({rot + dt * 220:.0f} {xx:.0f} {yy:.0f})'/>")
    cuerpo = f"<g transform='translate({BX},{BY + 220}) scale({z:.4f}) translate({-BX},{-(BY + 220)})'>{''.join(s)}</g>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs><rect width='{W}' height='{H}' fill='#f6e6c4'/>{cuerpo}</svg>")
