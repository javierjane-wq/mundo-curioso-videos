"""Rafflesia arnoldii: la flor más grande del mundo (Guinness: 111 cm, hasta 11 kg).

Selva de Sumatra. Una liana gruesa recorre el suelo; de ella sale un capullo granate que se va
hinchando mientras una mosca simpática (ojos que parpadean, alas que zumban) da vueltas a su
alrededor. Entre 5 y 6,6 s el capullo tiembla y se agrieta; en la REVELACION estalla: destello,
cinco pétalos enormes rojo-anaranjados con verrugas blancas se despliegan con rebote, aparece el
disco central, la cámara se acerca, suben ondas verdes de mal olor y llegan más moscas.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 6.6    # el capullo estalla y se abre la flor: golpe musical
MUSICA = 5

CX, CY = 540, 1490   # centro de la flor (sobre la liana)
SQ = 0.55            # aplastamiento vertical (la flor está tumbada en el suelo)

rng = np.random.default_rng(11)
MOTAS = [(rng.uniform(0, W), rng.uniform(300, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.28)) for _ in range(38)]
HOJARASCA = [(rng.uniform(-20, W + 20), rng.uniform(1330, 1900), rng.uniform(26, 52), rng.uniform(0, 180),
              ["#6b5a2e", "#8a6d34", "#4f6b2a", "#7a4f2a"][int(rng.integers(0, 4))]) for _ in range(46)]
TRONCOS = [(70, 92, "#9cc49a"), (300, 60, "#a9cfa5"), (820, 78, "#9cc49a"), (1010, 54, "#a9cfa5"), (600, 40, "#b5d8b0")]
# verrugas de los pétalos: (u relativo 0-1, v relativo -1..1, radio)
VERRUGAS = [(float(rng.uniform(0.3, 0.92)), float(rng.uniform(-0.75, 0.75)), float(rng.uniform(9, 17))) for _ in range(10)]
TROZOS = [(a, float(rng.uniform(380, 620)), float(rng.uniform(-300, 300))) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]


def P(ang, u, v):
    """Punto de un pétalo (coordenadas polares del suelo) -> pantalla."""
    ca, sa = math.cos(ang), math.sin(ang)
    return CX + u * ca - v * sa, CY + (u * sa + v * ca) * SQ


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def fondo(t, luz):
    s = []
    # cielo de selva entre las copas (arriba tranquilo)
    s.append(f"<rect width='{W}' height='{H}' fill='url(#cielo)'/>")
    # rayos de sol diagonales
    for i, x0 in enumerate((120, 430, 760)):
        op = (0.10 + 0.05 * pulso(t, 3.0, i * 0.7)) * (1 + 1.4 * luz)
        s.append(f"<path d='M{x0} -40 L{x0 + 170} -40 L{x0 + 520} 1500 L{x0 + 250} 1500 Z' fill='#fffbd0' opacity='{op:.3f}'/>")
    # copas lejanas (siluetas suaves)
    s.append("<path d='M-40 820 Q60 700 170 780 Q260 660 380 760 Q500 690 600 770 Q720 650 830 760 Q940 690 1120 790 L1120 1400 L-40 1400 Z' fill='#8dbb86'/>")
    # troncos lejanos
    for x, w, c in TRONCOS:
        s.append(f"<rect x='{x - w / 2}' y='560' width='{w}' height='800' fill='{c}'/>")
    s.append("<path d='M-40 1010 Q120 930 260 990 Q420 910 560 985 Q700 920 860 990 Q980 940 1120 1000 L1120 1400 L-40 1400 Z' fill='#6fa865' stroke='" + INK + "' stroke-width='6'/>")
    # arbustos del medio
    for i, (bx, by, sc) in enumerate(((90, 1250, 1.2), (330, 1235, 0.9), (760, 1240, 1.0), (1000, 1255, 1.25))):
        sw = 4 * pulso(t, 2.6, i * 0.4)
        s.append(f"<g transform='translate({bx},{by}) scale({sc}) rotate({sw:.1f})'>"
                 f"<path d='M-150 60 Q-170 -40 -90 -60 Q-60 -130 10 -100 Q80 -140 120 -60 Q190 -40 160 60 Z' fill='#3f8a3c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M-60 30 Q-40 -30 0 -50 M50 30 Q70 -20 90 -40' fill='none' stroke='#2c6a2c' stroke-width='7' stroke-linecap='round'/></g>")
    # suelo de la selva
    s.append(f"<path d='M-20 1320 Q260 1280 540 1310 Q820 1290 1100 1320 L1100 1940 L-20 1940 Z' fill='#4b4a26' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, r, rot, c in HOJARASCA:
        s.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{r:.0f}' ry='{r * 0.38:.0f}' fill='{c}' stroke='{INK}' stroke-width='4' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>")
    # la liana sobre la que vive la flor
    d = f"M-60 1590 C200 1470 380 1560 {CX} {CY + 8} S880 1420 1140 1540"
    s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='64' stroke-linecap='round'/>")
    s.append(f"<path d='{d}' fill='none' stroke='#7a4d2c' stroke-width='46' stroke-linecap='round'/>")
    s.append(f"<path d='{d}' fill='none' stroke='#a06a3e' stroke-width='12' stroke-dasharray='60 40' stroke-linecap='round' transform='translate(0,-10)'/>")
    return "".join(s)


def hojas_delante(t):
    """Hojas grandes en las esquinas de abajo que se balancean."""
    s = []
    for lado, x, y, base_rot in ((-1, -30, 1930, 28), (1, 1110, 1930, -28)):
        rot = base_rot + 5 * pulso(t, 2.8, 0.3 if lado > 0 else 0)
        s.append(f"<g transform='translate({x},{y}) rotate({rot:.1f}) scale({-lado},1)'>"
                 f"<path d='M0 0 Q-40 -260 60 -470 Q200 -300 140 -60 Q90 10 0 0 Z' fill='#2f7d32' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M10 -10 Q40 -220 60 -440' fill='none' stroke='#1f5c24' stroke-width='8' stroke-linecap='round'/>"
                 + "".join(f"<path d='M{25 + k * 6} {-80 - k * 85} Q{70 + k * 5} {-120 - k * 85} {110 - k * 8} {-110 - k * 80}' fill='none' stroke='#1f5c24' stroke-width='5' stroke-linecap='round'/>" for k in range(4))
                 + "</g>")
    return "".join(s)


def capullo(t):
    """Capullo granate con brácteas, que crece, respira y tiembla antes de abrirse."""
    if t >= REVELACION:
        return ""
    r = lerp(62, 150, ease(seg(t, 0, 6.0))) * (1 + 0.03 * pulso(t, 1.1))
    tens = seg(t, 4.8, REVELACION)
    dx = 9 * tens * math.sin(t * 47)
    cx, cy = CX + dx, CY - r * 0.72
    s = [f"<ellipse cx='{CX}' cy='{CY + 18}' rx='{r * 1.15:.0f}' ry='{r * 0.3:.0f}' fill='#000' opacity='0.28'/>",
         f"<g transform='translate({cx:.1f},{cy:.1f})'>"]
    # brácteas de atrás, cuerpo y brácteas de delante
    s.append(f"<circle r='{r:.1f}' fill='#5e2620' stroke='{INK}' stroke-width='{LW}'/>")
    # grietas naranjas que se abren arriba
    if tens > 0:
        for a in (-60, -90, -120):
            ra = math.radians(a); L = r * (0.3 + 0.6 * tens)
            s.append(f"<path d='M0 {-r * 0.2:.1f} L{L * math.cos(ra):.1f} {L * math.sin(ra) - r * 0.2:.1f}' stroke='#ff9a3c' stroke-width='{6 + 6 * tens:.1f}' stroke-linecap='round'/>")
    for rot, sx, col in ((-38, -0.42, "#7b3326"), (38, 0.42, "#7b3326"), (0, 0, "#8e3d2b")):
        s.append(f"<g transform='translate({sx * r:.1f},{r * 0.25:.1f}) rotate({rot})'>"
                 f"<path d='M0 {r * 0.75:.1f} Q{-r * 0.62:.1f} {r * 0.2:.1f} 0 {-r * 0.72:.1f} Q{r * 0.62:.1f} {r * 0.2:.1f} 0 {r * 0.75:.1f} Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M0 {r * 0.55:.1f} L0 {-r * 0.45:.1f}' stroke='#5e2620' stroke-width='5' stroke-linecap='round'/></g>")
    # brillo
    s.append(f"<ellipse cx='{-r * 0.45:.1f}' cy='{-r * 0.5:.1f}' rx='{r * 0.16:.1f}' ry='{r * 0.09:.1f}' fill='#d98a6a' opacity='0.8' transform='rotate(-35 {-r * 0.45:.1f} {-r * 0.5:.1f})'/>")
    # copa donde se une a la liana
    s.append(f"<path d='M{-r * 0.55:.1f} {r * 0.78:.1f} Q0 {r * 1.05:.1f} {r * 0.55:.1f} {r * 0.78:.1f}' fill='#7a4d2c' stroke='{INK}' stroke-width='7'/>")
    s.append("</g>")
    return "".join(s)


def flor(t):
    """Rafflesia abierta: 5 pétalos carnosos con verrugas y disco central con abertura."""
    if t < REVELACION:
        return ""
    o = seg(t, REVELACION, REVELACION + 0.7)
    rb = 1 + 0.07 * math.sin(math.pi * seg(t, REVELACION + 0.45, REVELACION + 1.2))
    R = lerp(150, 430, o) * rb
    anchura = lerp(0.45, 1.0, o)
    r0 = 60
    s = [f"<ellipse cx='{CX}' cy='{CY + 20}' rx='{R * 1.05:.0f}' ry='{R * SQ * 1.0:.0f}' fill='#000' opacity='0.3'/>"]
    angs = sorted((math.radians(-90 + 72 * i) for i in range(5)), key=lambda a: math.sin(a))
    for i, a in enumerate(angs):
        uc, au, bv = (r0 + R) / 2, (R - r0) / 2, 165 * anchura * rb
        pts = [P(a, uc + au * math.cos(th), bv * math.sin(th)) for th in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
        s.append(f"<path d='{poly(pts)}' fill='#c9542e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        # borde interior algo más oscuro hacia el centro
        pts2 = [P(a, uc - au * 0.25 + au * 0.55 * math.cos(th), bv * 0.55 * math.sin(th)) for th in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
        s.append(f"<path d='{poly(pts2)}' fill='#b23c25' opacity='0.55'/>")
        for uu, vv, rr in VERRUGAS:
            x, y = P(a, r0 + (R - r0) * uu, vv * bv * math.sqrt(max(0, 1 - ((uu * 2 - 1.05) ** 2))))
            rr2 = rr * lerp(0.5, 1, o) * rb
            s.append(f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{rr2:.1f}' ry='{rr2 * 0.68:.1f}' fill='#f5e4cc' stroke='#8f3a22' stroke-width='3'/>")
    # disco central (diafragma) elevado
    k = rb * lerp(0.6, 1, o)
    rx, ry, h = 155 * k, 92 * k, 46 * k
    s.append(f"<ellipse cx='{CX}' cy='{CY:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='#9c3422' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{CX - rx:.1f}' y='{CY - h:.1f}' width='{2 * rx:.1f}' height='{h:.1f}' fill='#9c3422'/>")
    s.append(f"<line x1='{CX - rx:.1f}' y1='{CY - h:.1f}' x2='{CX - rx:.1f}' y2='{CY:.1f}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<line x1='{CX + rx:.1f}' y1='{CY - h:.1f}' x2='{CX + rx:.1f}' y2='{CY:.1f}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='{CX}' cy='{CY - h:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='#d65a36' stroke='{INK}' stroke-width='{LW}'/>")
    for j in range(10):
        a = 2 * math.pi * j / 10 + 0.3
        x, y = CX + rx * 0.8 * math.cos(a), CY - h + ry * 0.8 * math.sin(a)
        s.append(f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{11 * k:.1f}' ry='{7 * k:.1f}' fill='#f5e4cc' stroke='#8f3a22' stroke-width='2.5'/>")
    # abertura oscura con el disco de pinchitos dentro
    s.append(f"<ellipse cx='{CX}' cy='{CY - h:.1f}' rx='{rx * 0.6:.1f}' ry='{ry * 0.55:.1f}' fill='#3a1410' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<ellipse cx='{CX}' cy='{CY - h + ry * 0.1:.1f}' rx='{rx * 0.42:.1f}' ry='{ry * 0.34:.1f}' fill='#e9cfb2'/>")
    for j in range(9):
        a = 2 * math.pi * j / 9
        x, y = CX + rx * 0.28 * math.cos(a), CY - h + ry * 0.1 + ry * 0.22 * math.sin(a)
        s.append(f"<path d='M{x - 6 * k:.1f} {y:.1f} L{x:.1f} {y - 16 * k:.1f} L{x + 6 * k:.1f} {y:.1f} Z' fill='#fff7ea' stroke='#8f3a22' stroke-width='2'/>")
    return "".join(s)


def trozos(t):
    """Brácteas del capullo que salen despedidas al abrirse."""
    k = seg(t, REVELACION, REVELACION + 1.0)
    if k <= 0 or k >= 1:
        return ""
    s = []
    for a, dist, giro in TROZOS:
        x = CX + math.cos(a) * dist * k
        y = CY - 110 + math.sin(a) * dist * k * 0.6 + 500 * k * k - 200 * k
        s.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({giro * k:.1f})' opacity='{1 - k:.2f}'>"
                 f"<path d='M0 -34 Q26 0 0 34 Q-26 0 0 -34 Z' fill='#7b3326' stroke='{INK}' stroke-width='6'/></g>")
    return "".join(s)


def olor(t):
    """Ondas verdes de mal olor que suben de la flor."""
    k = seg(t, REVELACION + 0.4, REVELACION + 1.2)
    if k <= 0:
        return ""
    s = []
    for i, x0 in enumerate((CX - 190, CX - 40, CX + 110, CX + 240)):
        fase = (t * 0.55 + i * 0.27) % 1.0
        y0 = CY - 80 - fase * 360
        op = k * (1 - fase) * 0.9
        wv = 30
        d = f"M{x0} {y0 + 120:.0f} q{wv} -30 0 -60 q{-wv} -30 0 -60"
        s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='24' stroke-linecap='round' opacity='{op:.2f}'/>"
                 f"<path d='{d}' fill='none' stroke='#c6f57e' stroke-width='13' stroke-linecap='round' opacity='{op:.2f}'/>")
    return "".join(s)


def mosca(t, x, y, sc, mira, fase=0.0):
    """Mosca original y simpática: cuerpo verde metálico, ojos grandes que parpadean, alas que zumban."""
    blink = 0.12 if ((t + fase) % 2.7) < 0.12 else 1.0
    ala = 0.35 + 0.65 * abs(math.sin((t + fase) * 55))
    s = [f"<g transform='translate({x:.1f},{y:.1f}) scale({sc * mira:.3f},{sc:.3f})'>"]
    # sombra en el suelo no (vuela); patitas
    for lx in (-14, 0, 14):
        s.append(f"<path d='M{lx} 18 L{lx - 6} 38 L{lx - 12} 42' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")
    # alas
    for rot in (-28, 18):
        s.append(f"<g transform='translate(-6,-16) rotate({rot}) scale(1,{ala:.2f})'>"
                 f"<ellipse cx='-6' cy='-34' rx='22' ry='38' fill='#e6f6ff' fill-opacity='0.75' stroke='{INK}' stroke-width='5'/></g>")
    # abdomen y tórax
    s.append(f"<ellipse cx='-26' cy='6' rx='34' ry='24' fill='#2f7f6a' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<path d='M-44 -4 Q-38 6 -44 18 M-30 -14 Q-22 6 -30 26' fill='none' stroke='#1d5546' stroke-width='5'/>")
    s.append(f"<ellipse cx='-26' cy='-2' rx='12' ry='6' fill='#7fd1b6' opacity='0.8'/>")
    s.append(f"<circle cx='8' cy='0' r='22' fill='#3a9a80' stroke='{INK}' stroke-width='6'/>")
    # cabeza con ojos grandes
    s.append(f"<circle cx='34' cy='-4' r='20' fill='#2f7f6a' stroke='{INK}' stroke-width='6'/>")
    for ex, ey in ((30, -16), (48, -10)):
        s.append(f"<ellipse cx='{ex}' cy='{ey}' rx='14' ry='{14 * blink:.1f}' fill='#c8312b' stroke='{INK}' stroke-width='5'/>")
        if blink > 0.5:
            s.append(f"<circle cx='{ex + 3}' cy='{ey - 2}' r='6' fill='#fff'/><circle cx='{ex + 4}' cy='{ey - 1}' r='3' fill='{INK}'/>")
    s.append(f"<path d='M44 6 Q52 14 46 22' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    s.append("</g>")
    return "".join(s)


def moscas(t):
    s = []
    # la protagonista: entra por la izquierda desde el fotograma 0 y orbita el capullo
    e = seg(t, 0, 1.6)
    w = 1.35
    ox = CX + 300 * math.cos(w * t + 2.6)
    oy = 1180 + 55 * math.sin(2 * w * t) + 18 * math.sin(t * 9)
    x = lerp(70, ox, e); y = lerp(1120, oy, e)
    vx = -300 * w * math.sin(w * t + 2.6) if e >= 1 else 1
    s.append(mosca(t, x, y, 1.15, 1 if vx >= 0 else -1))
    # tras la revelación llegan más moscas atraídas por el olor
    for i, (x0, y0, x1, y1, ph) in enumerate(((1180, 1080, 820, 1150, 0.8), (-120, 1260, 250, 1210, 1.7))):
        k = seg(t, REVELACION + 0.5 + i * 0.4, REVELACION + 1.8 + i * 0.4)
        if k > 0:
            xx = lerp(x0, x1, k) + 30 * math.sin(t * 3 + ph)
            yy = lerp(y0, y1, k) + 20 * math.sin(t * 7 + ph)
            s.append(mosca(t, xx, yy, 0.9, -1 if x0 > W else 1, ph))
    return "".join(s)


def frame(t):
    luz = seg(t, REVELACION, REVELACION + 0.8)
    flash = clamp(1 - (t - REVELACION) / 0.6) if t >= REVELACION else 0
    top = mix("#d9efb8", "#fff3c2", luz); mid = mix("#a9d79a", "#d8ecaa", luz)
    defs = (f"<linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='#6fa865'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff2b0' stop-opacity='{0.85 * luz:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffd36b' stop-opacity='{0.4 * luz:.3f}'/><stop offset='1' stop-color='#ffd36b' stop-opacity='0'/></radialGradient>")
    escena = [fondo(t, luz)]
    if luz > 0:
        escena.append(f"<ellipse cx='{CX}' cy='{CY - 60}' rx='620' ry='460' fill='url(#halo)'/>")
    escena += [capullo(t), flor(t), trozos(t), olor(t), moscas(t)]
    # motas de polen flotando
    for px, py, pr, sp, ph in MOTAS:
        yy = (py - t * sp) % 1600 + 300
        escena.append(f"<circle cx='{px + 18 * math.sin(t * 0.9 + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fffbe0' opacity='0.55'/>")
    escena.append(hojas_delante(t))
    z = 1 + 0.13 * seg(t, REVELACION, REVELACION + 1.4)
    cuerpo = zoom(CX, 1420, z, "".join(escena))
    if flash > 0:
        cuerpo += f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.85 * flash:.2f}'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")
