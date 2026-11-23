"""2026-11-23-c3 · En el polo norte de Saturno hay una tormenta con forma de HEXÁGONO.

Una sonda original llega volando hasta Saturno (personaje con cara, inclinado para que se vea su
polo norte). El polo está cubierto de bruma; la bruma se aparta y en la REVELACION aparece el
hexágono, un chorro de viento de unos 30.000 km (más de 2 veces la Tierra) que brilla en cian,
con zoom de cámara hacia el polo. Fuentes: NASA JPL (2013), NASA Science «Hexagon in motion».
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.2   # aparece el hexágono: golpe musical
MUSICA = 5

CX, CY, R = 540.0, 1460.0, 270.0
INC = math.radians(45)        # cuánto se inclina el polo hacia nosotros
CE, SE = math.cos(INC), math.sin(INC)

rng = np.random.default_rng(23)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.8, 5), rng.uniform(0, 6.28)) for _ in range(110)]

# bandas: (latitud desde la que empieza, color)
BANDAS = [(-40, "#e3b86e"), (-22, "#f2d79a"), (-6, "#f8e7b8"), (9, "#e6be76"), (20, "#f3daa2"),
          (32, "#dcab60"), (45, "#efd296"), (57, "#cfa868"), (66, "#bdb39a")]
HEX_LAT = 75.5


def P(lat, th, r=R):
    """Punto de la esfera (lat en grados, th en radianes) -> (x, y en pantalla, z hacia nosotros)."""
    la = math.radians(lat); sl, cl = math.sin(la), math.cos(la)
    x = r * cl * math.cos(th)
    yup = r * sl * CE - r * cl * math.sin(th) * SE
    z = r * sl * SE + r * cl * math.sin(th) * CE
    return CX + x, CY - yup, z


def pts(lista):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in lista)


def casquete(lat, color, op=1.0):
    """Zona visible al norte de la latitud lat (recortada al disco del planeta)."""
    la = math.radians(lat)
    A = math.sin(la) * SE; B = math.cos(la) * CE
    if B <= 1e-6 or -A / B < -1:   # todo el círculo visible: elipse
        p = [P(lat, 2 * math.pi * k / 90)[:2] for k in range(90)]
        return f"<polygon points='{pts(p)}' fill='{color}' opacity='{op:.3f}'/>"
    th0 = math.asin(clamp(-A / B, -1, 1))
    th = np.linspace(th0, math.pi - th0, 70)
    p = [P(lat, a)[:2] for a in th]
    lx = p[-1][0]; fx = p[0][0]
    far_l = CX + 3 * R * (1 if lx > CX else -1); far_f = CX + 3 * R * (1 if fx > CX else -1)
    p += [(far_l, p[-1][1]), (far_l, CY - 2 * R), (far_f, CY - 2 * R), (far_f, p[0][1])]
    return f"<polygon points='{pts(p)}' fill='{color}' opacity='{op:.3f}'/>"


def anillo_path(r1, r2):
    e = lambda r: (f"M{CX - r:.1f} {CY:.1f} A{r:.1f} {r*SE:.1f} 0 1 0 {CX + r:.1f} {CY:.1f} "
                   f"A{r:.1f} {r*SE:.1f} 0 1 0 {CX - r:.1f} {CY:.1f} Z")
    return e(r2) + " " + e(r1)


ANILLOS = [(1.22, 1.42, "#c79f63"), (1.47, 1.74, "#efd6a4"), (1.78, 1.9, "#d2ad74")]


def anillos(t, mitad):
    clip = "ringback" if mitad == "atras" else "ringfront"
    g = [f"<g clip-path='url(#{clip})'>"]
    for r1, r2, col in ANILLOS:
        g.append(f"<path d='{anillo_path(r1 * R, r2 * R)}' fill='{col}' fill-rule='evenodd' stroke='{INK}' stroke-width='6'/>")
    # brillo de partículas que giran
    for i, rr in enumerate((1.33, 1.6, 1.68, 1.84)):
        r = rr * R
        g.append(f"<ellipse cx='{CX}' cy='{CY}' rx='{r:.1f}' ry='{r*SE:.1f}' fill='none' stroke='#fff6dc' "
                 f"stroke-width='3' stroke-dasharray='6 {22 + 9*i}' stroke-dashoffset='{-t*(40 + 12*i):.1f}' opacity='0.7'/>")
    g.append("</g>")
    return "".join(g)


def hexagono(t, rev):
    rot = 0.25 * t
    vert = []
    for k in range(6):
        for s in range(8):   # lados un pelín ondulados, como un chorro de viento
            a = rot + (k + s / 8) * math.pi / 3
            lat = HEX_LAT + 0.0
            # lado recto: interpola entre vértices en el plano tangente
            a0 = rot + k * math.pi / 3; a1 = rot + (k + 1) * math.pi / 3
            x0, y0, _ = P(HEX_LAT, a0); x1, y1, _ = P(HEX_LAT, a1)
            f = s / 8
            w = 3 * math.sin(f * math.pi) * math.sin(t * 5 + k)
            vert.append((lerp(x0, x1, f), lerp(y0, y1, f) + w))
    hx, hy, _ = P(90, 0)
    glow = mix("#9a9a8a", "#62d8ff", rev)
    g = []
    inner = mix("#a9a491", "#2f5fae", rev)
    g.append(f"<polygon points='{pts(vert)}' fill='{inner}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    if rev > 0:
        g.append(f"<polygon points='{pts(vert)}' fill='none' stroke='#bff2ff' stroke-width='{22*rev:.1f}' opacity='{0.35*rev:.3f}' stroke-linejoin='round'/>")
    g.append(f"<polygon points='{pts(vert)}' fill='none' stroke='{glow}' stroke-width='9' stroke-linejoin='round'/>")
    # remolino del centro (ojo del vórtice)
    sw = []
    for k in range(40):
        a = -t * 2.2 + k * 0.32; rr = 4 + k * 1.15
        sw.append((hx + rr * math.cos(a), hy + rr * math.sin(a) * SE))
    g.append(f"<polyline points='{pts(sw)}' fill='none' stroke='{mix('#8d8877', '#9fe8ff', rev)}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='{hx:.1f}' cy='{hy:.1f}' rx='9' ry='{9*SE:.1f}' fill='{mix('#6d6858', '#123a7a', rev)}' stroke='{INK}' stroke-width='4'/>")
    return "".join(g)


def cara(t, rev):
    blink = 1.0 if (((t + 1.2) % 2.9) > 0.13 or 6.9 < t < 9.3) else 0.12
    up = lerp(0, -12, seg(t, 4.8, 6.0)) + lerp(0, -6, rev)
    big = 1 + 0.15 * rev
    g = []
    ey = CY + 35
    for ex in (CX - 80, CX + 80):
        g.append(f"<g transform='translate({ex},{ey}) scale({big:.3f},{big*blink:.3f})'>"
                 f"<ellipse rx='38' ry='42' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='0' cy='{6 + up:.1f}' r='19' fill='#2b1d3d'/>"
                 f"<circle cx='-6' cy='{-1 + up:.1f}' r='7' fill='#fff'/></g>")
        g.append(f"<path d='M{ex - 34} {ey - 58 - 8*rev:.1f} Q{ex} {ey - 74 - 10*rev:.1f} {ex + 34} {ey - 58 - 8*rev:.1f}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    for ex in (CX - 135, CX + 135):
        g.append(f"<ellipse cx='{ex}' cy='{ey + 52}' rx='22' ry='12' fill='#ff8f6b' opacity='0.55'/>")
    my = ey + 92
    if rev < 0.5:
        g.append(f"<path d='M{CX - 34} {my} Q{CX} {my + 26 + 4*pulso(t, 1.5):.1f} {CX + 34} {my}' fill='#9c3b33' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    else:
        g.append(f"<ellipse cx='{CX}' cy='{my + 8}' rx='22' ry='28' fill='#9c3b33' stroke='{INK}' stroke-width='7'/>")
    return "".join(g)


def sonda(t, rev):
    k = seg(t, 0, 4.4)
    x = lerp(-140, 800, k); y = lerp(1180, 1090, k) + 10 * math.sin(t * 2.6)
    ang = lerp(-8, 6, k) + 3 * math.sin(t * 1.9)
    luz = 0.5 + 0.5 * math.sin(t * 9)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale(0.95)'>"]
    if t < 4.6:   # estela del motor
        g.append(f"<path d='M-70 0 L-{140 + 30*luz:.0f} -10 L-{140 + 30*luz:.0f} 10 Z' fill='#ffb347' opacity='0.85'/>")
    g.append(f"<line x1='-10' y1='0' x2='-10' y2='70' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='-10' cy='76' r='9' fill='#ff5a5f' stroke='{INK}' stroke-width='4' opacity='{0.5 + 0.5*luz:.2f}'/>")
    g.append(f"<rect x='-66' y='-30' width='96' height='62' rx='10' fill='#f2b33d' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-56 -18 L20 -18 M-56 0 L20 0 M-56 18 L20 18' stroke='#c98a1f' stroke-width='4'/>")
    # antena parabólica
    g.append(f"<path d='M30 -62 Q78 0 30 62 Q52 0 30 -62 Z' fill='#f4f1ea' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<line x1='40' y1='0' x2='86' y2='0' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='88' cy='0' r='7' fill='#5ec8ff' stroke='{INK}' stroke-width='4'/>")
    # ojito-cámara
    g.append(f"<circle cx='-22' cy='-2' r='16' fill='#1e2a38' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='-22' cy='-2' r='8' fill='{mix('#5ec8ff', '#bff2ff', rev)}'/>")
    if rev > 0:
        fl = clamp(1 - (t - REVELACION) / 0.5)
        g.append(f"<circle cx='-22' cy='-2' r='{20 + 40*(1-fl):.1f}' fill='#ffffff' opacity='{0.8*fl:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.5)
    hz = 1 - seg(t, 4.8, 7.0)           # bruma del polo
    hx, hy, _ = P(90, 0)
    defs = (
        "<linearGradient id='space' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#090d2a'/><stop offset='0.6' stop-color='#151a48'/><stop offset='1' stop-color='#261754'/></linearGradient>"
        f"<radialGradient id='neb' cx='0.8' cy='0.75' r='0.6'><stop offset='0' stop-color='#7b3fa8' stop-opacity='0.45'/><stop offset='1' stop-color='#7b3fa8' stop-opacity='0'/></radialGradient>"
        f"<radialGradient id='pglow'><stop offset='0' stop-color='#8fe6ff' stop-opacity='{0.75*rev:.3f}'/><stop offset='0.5' stop-color='#3d8fe0' stop-opacity='{0.35*rev:.3f}'/><stop offset='1' stop-color='#3d8fe0' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='shade' cx='0.35' cy='0.3' r='0.75'><stop offset='0' stop-color='#fff8e0' stop-opacity='0.35'/>"
        "<stop offset='0.55' stop-color='#fff8e0' stop-opacity='0'/><stop offset='0.85' stop-color='#3a2410' stop-opacity='0.25'/><stop offset='1' stop-color='#2a1608' stop-opacity='0.55'/></radialGradient>"
        f"<clipPath id='disk'><circle cx='{CX}' cy='{CY}' r='{R}'/></clipPath>"
        f"<clipPath id='ringback'><rect x='0' y='0' width='{W}' height='{CY}'/></clipPath>"
        f"<clipPath id='ringfront'><rect x='0' y='{CY}' width='{W}' height='{H - CY}'/></clipPath>"
    )
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#space)'/><rect width='{W}' height='{H}' fill='url(#neb)'/>"]
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.4 * math.sin(t * 2.5 + ph) + 0.15 * rev
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{clamp(a):.2f}'/>")
    z = 1 + 1.0 * seg(t, REVELACION - 0.1, REVELACION + 0.9) + 0.04 * seg(t, 0, 7)
    c = [f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{lerp(120, 330, rev):.0f}' fill='url(#pglow)'/>"]
    c.append(anillos(t, "atras"))
    # sombra del planeta sobre el fondo de los anillos y planeta
    c.append(f"<g clip-path='url(#disk)'><circle cx='{CX}' cy='{CY}' r='{R}' fill='#d6a253'/>")
    for lat, col in BANDAS:
        c.append(casquete(lat, col))
    # manchas de nubes que giran con el planeta
    for lat, ph, rx in ((27, 0.0, 26), (27, 2.6, 18), (-12, 1.2, 30), (52, 3.8, 18), (52, 0.9, 14), (-30, 4.4, 22)):
        x, y, zz = P(lat, ph + 0.45 * t)
        if zz > 40:
            c.append(f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{rx * zz / R:.1f}' ry='{rx*0.45:.1f}' fill='#fff7dd' opacity='0.75'/>")
    c.append(hexagono(t, rev))
    # bruma que tapa el polo y se aparta
    if hz > 0:
        c.append(casquete(68, "#ece3c8", 0.92 * hz))
        for k in range(5):
            x, y, _ = P(78, k * 1.25 + t * 0.6)
            c.append(f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{40 + 8*k}' ry='18' fill='#fbf6e6' opacity='{0.8*hz:.2f}'/>")
    c.append(f"<circle cx='{CX}' cy='{CY}' r='{R}' fill='url(#shade)'/>")
    c.append(cara(t, rev))
    c.append("</g>")
    c.append(f"<circle cx='{CX}' cy='{CY}' r='{R}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(anillos(t, "delante"))
    # destello de la revelación
    if t >= REVELACION:
        k = clamp((t - REVELACION) / 0.9)
        c.append(f"<ellipse cx='{hx:.1f}' cy='{hy:.1f}' rx='{70 + 260*k:.1f}' ry='{(70 + 260*k)*SE:.1f}' fill='none' stroke='#c9f6ff' stroke-width='{14*(1-k):.1f}' opacity='{0.9*(1-k):.2f}'/>")
    sube = 90 * seg(t, REVELACION - 0.1, REVELACION + 0.9)   # deja el hexágono por encima del cierre
    s.append(f"<g transform='translate(0,{-sube:.1f})'>" + zoom(CX, hy - 20, z, "".join(c)) + "</g>")
    s.append(sonda(t, rev))
    s.append("</svg>")
    return "".join(s)
