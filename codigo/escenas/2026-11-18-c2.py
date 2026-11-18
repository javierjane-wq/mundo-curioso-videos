"""El mapa de los sabores de la lengua es un mito: toda la lengua nota todos los sabores.

Composición: protagonista (niña/niño original de cabeza redonda que saca la lengua, detrás de una
mesa) en la mitad de abajo; arriba solo la pared tranquila de una cocina con degradado suave.
Movimiento: la cabeza sube con rebote desde el fotograma 0 y saca la lengua; parpadea y balancea
la cabeza; caramelo, limón, salero y taza flotan a los lados; burbujitas en el fondo. En la lengua
se pinta el "mapa" clásico zona a zona (amargo atrás, ácido y salado a los lados, dulce en la punta),
las zonas tiemblan en la tensión y en la REVELACION se rompen: toda la lengua se llena de papilas
de los 5 colores, halo, rayos, ojos felices, los alimentos brillan y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.3   # el mapa se rompe y toda la lengua se ilumina: golpe musical
MUSICA = 7

rng = np.random.default_rng(1182)
BUBBLES = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(6, 16), rng.uniform(30, 70)) for _ in range(26)]

DULCE, SALADO, ACIDO, AMARGO, UMAMI = "#ff6fb1", "#4fa8ff", "#a8e04a", "#9b5de5", "#ff9f40"
COLORES = [DULCE, SALADO, ACIDO, AMARGO, UMAMI]

# lengua (coordenadas de pantalla, antes de la animación)
TX = 540
TONGUE = "M412 1508 C396 1620 404 1730 466 1790 C508 1830 572 1830 614 1790 C676 1730 684 1620 668 1508 Z"


def _dentro(x, y):
    """¿Punto aproximadamente dentro de la lengua? (para repartir papilas)."""
    if y < 1525 or y > 1810: return False
    if y < 1700: half = 132
    else: half = 132 * math.sqrt(max(0.0, 1 - ((y - 1700) / 112) ** 2))
    return abs(x - TX) < half - 16


PAPILAS = []
while len(PAPILAS) < 70:
    x, y = rng.uniform(410, 670), rng.uniform(1525, 1805)
    if _dentro(x, y):
        PAPILAS.append((x, y, rng.uniform(8, 13), COLORES[len(PAPILAS) % 5], rng.uniform(0, 0.55)))

CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(200, 420), rng.uniform(10, 18), COLORES[i % 5]) for i in range(22)]


def caramelo(c):
    return (f"<path d='M-70 -26 L-40 0 L-70 26 Z' fill='{c}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M70 -26 L40 0 L70 26 Z' fill='{c}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<ellipse rx='46' ry='36' fill='{c}' stroke='{INK}' stroke-width='7'/>"
            "<path d='M-26 -22 Q0 0 -10 30' stroke='#fff' stroke-width='9' fill='none' opacity='0.8' stroke-linecap='round'/>"
            "<path d='M8 -30 Q30 -6 22 26' stroke='#ffd1e8' stroke-width='8' fill='none' opacity='0.8' stroke-linecap='round'/>")


def limon():
    s = [f"<circle r='54' fill='#ffe14d' stroke='{INK}' stroke-width='7'/>",
         "<circle r='42' fill='#fff7b0'/>"]
    for a in range(0, 360, 60):
        r = math.radians(a + 30)
        s.append(f"<path d='M0 0 L{38*math.cos(r - 0.42):.1f} {38*math.sin(r - 0.42):.1f} "
                 f"A38 38 0 0 1 {38*math.cos(r + 0.42):.1f} {38*math.sin(r + 0.42):.1f} Z' fill='#ffd31a'/>")
    s.append(f"<circle r='6' fill='#fff7b0'/>")
    return "".join(s)


def salero():
    return (f"<path d='M-34 -40 L34 -40 L44 52 Q44 62 34 62 L-34 62 Q-44 62 -44 52 Z' fill='#eef6ff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-34 -40 Q-34 -78 0 -80 Q34 -78 34 -40 Z' fill='#b8c4d6' stroke='{INK}' stroke-width='7'/>"
            + "".join(f"<circle cx='{dx}' cy='-62' r='4' fill='{INK}'/>" for dx in (-12, 0, 12))
            + "<rect x='-24' y='-20' width='12' height='66' rx='6' fill='#fff' opacity='0.9'/>"
            + f"<rect x='-30' y='4' width='60' height='40' rx='6' fill='{SALADO}' stroke='{INK}' stroke-width='5'/>")


def taza(t):
    vapor = "".join(f"<path d='M{dx} -60 q-12 -18 0 -36 q12 -18 0 -36' fill='none' stroke='#fff' stroke-width='7' "
                    f"stroke-linecap='round' opacity='{0.4 + 0.3 * math.sin(t * 4 + dx):.2f}' "
                    f"transform='translate(0,{-6 * math.sin(t * 3 + dx):.1f})'/>" for dx in (-16, 16))
    return (vapor +
            f"<path d='M44 -20 Q80 -20 78 8 Q76 34 42 34' fill='none' stroke='{INK}' stroke-width='16'/>"
            f"<path d='M44 -20 Q80 -20 78 8 Q76 34 42 34' fill='none' stroke='#8f5bd6' stroke-width='7'/>"
            f"<path d='M-52 -48 L52 -48 L44 46 Q42 60 28 60 L-28 60 Q-42 60 -44 46 Z' fill='#8f5bd6' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='-48' rx='52' ry='12' fill='#5a3220' stroke='{INK}' stroke-width='6'/>"
            "<rect x='-36' y='-32' width='12' height='70' rx='6' fill='#c4a3f2' opacity='0.8'/>")


def cabeza(t, rev):
    """Cabeza redonda original con flequillo, orejas, ojos grandes, mejillas y boca abierta."""
    feliz = seg(t, REVELACION, REVELACION + 0.25)
    blink = 0.12 if (t % 2.9) > 2.75 and feliz < 0.5 else 1.0
    duda = seg(t, 5.0, 5.6) * (1 - feliz)
    # mirada: al frente, abajo a la lengua (2,4-5), a los lados en la tensión
    lx = (-12 * math.sin((t - 5.0) * 4.2)) * seg(t, 5.0, 5.4) * (1 - feliz)
    ly = 12 * seg(t, 2.3, 2.8) * (1 - seg(t, 5.0, 5.4)) + 4
    s = []
    skin, skin_d = "#ffd2a6", "#f2b07e"
    # orejas
    for ex in (178, 902):
        s.append(f"<ellipse cx='{ex}' cy='1390' rx='58' ry='74' fill='{skin}' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(f"<ellipse cx='{ex}' cy='1392' rx='26' ry='38' fill='{skin_d}'/>")
    # cara
    s.append(f"<ellipse cx='540' cy='1385' rx='368' ry='380' fill='{skin}' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo: casquete con flequillo en picos
    s.append(f"<path d='M196 1290 Q190 1040 540 1010 Q890 1040 884 1290 Q860 1200 790 1170 L760 1232 L700 1150 "
             f"L640 1222 L590 1140 L520 1220 L460 1142 L400 1224 L350 1158 L300 1236 Q240 1220 196 1290 Z' "
             f"fill='#5a3426' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append("<path d='M330 1070 Q420 1036 520 1032' stroke='#8a5a44' stroke-width='12' fill='none' stroke-linecap='round'/>")
    # remolino del pelo (se mueve)
    sw = 10 * math.sin(t * 3.2)
    s.append(f"<path d='M540 1014 Q{560 + sw:.0f} 960 {600 + sw:.0f} 968' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
             f"<path d='M540 1014 Q{560 + sw:.0f} 960 {600 + sw:.0f} 968' fill='none' stroke='#5a3426' stroke-width='7' stroke-linecap='round'/>")
    # cejas
    for ex, sg in ((395, -1), (685, 1)):
        up = 22 * duda + 14 * feliz
        s.append(f"<path d='M{ex - 50} {1262 - up + sg * 6 * duda:.0f} Q{ex} {1240 - up:.0f} {ex + 50} {1262 - up - sg * 6 * duda:.0f}' "
                 f"fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    # ojos
    for ex in (395, 685):
        if feliz > 0.5:
            s.append(f"<path d='M{ex - 46} 1340 Q{ex} 1280 {ex + 46} 1340' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        else:
            s.append(f"<g transform='translate({ex},1330) scale(1,{blink})'>"
                     f"<ellipse rx='58' ry='64' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
                     f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='30' fill='#3a2418'/>"
                     f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='17' fill='#1a0f0a'/>"
                     f"<circle cx='{lx - 10:.1f}' cy='{ly - 12:.1f}' r='10' fill='#fff'/></g>")
    # mejillas
    for ex in (300, 780):
        s.append(f"<ellipse cx='{ex}' cy='1460' rx='54' ry='32' fill='#ff8a8a' opacity='{0.55 + 0.25 * feliz:.2f}'/>")
    # nariz
    s.append(f"<path d='M520 1410 Q540 1440 560 1410' fill='none' stroke='{skin_d}' stroke-width='10' stroke-linecap='round'/>")
    # boca abierta
    abre = seg(t, 0.5, 1.0)
    mh = lerp(20, 1, abre)
    s.append(f"<path d='M352 1470 Q540 {1448 - 4 * feliz:.0f} 728 1470 Q716 {1470 + 130 * abre:.0f} 540 {1470 + 150 * abre:.0f} "
             f"Q364 {1470 + 130 * abre:.0f} 352 1470 Z' fill='#7a1f2b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if abre > 0.2:
        s.append(f"<path d='M392 1466 Q540 1452 688 1466 L682 1496 Q540 1486 398 1496 Z' fill='#fff' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def lengua(t, rev):
    """Lengua que sale de la boca con el 'mapa' de sabores y, en la revelación, papilas de colores."""
    k = seg(t, 0.7, 1.3)
    sy = (1 + 0.1 * math.sin(math.pi * seg(t, 1.0, 1.6))) * k if k > 0 else 0
    if t >= 1.6: sy = 1 + 0.025 * math.sin(t * 3.4)
    if sy <= 0.01: return ""
    wob = 2.5 * math.sin(t * 2.7)
    s = [f"<g transform='translate({TX},1508) rotate({wob:.2f}) scale(1,{sy:.3f}) translate({-TX},-1508)'>"]
    # halo de la revelación
    if rev > 0:
        s.append(f"<ellipse cx='{TX}' cy='1660' rx='{lerp(150, 330, rev):.0f}' ry='{lerp(180, 300, rev):.0f}' fill='url(#halo)'/>")
    s.append(f"<path d='{TONGUE}' fill='{mix('#ff7f8e', '#ff93a0', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append("<g clip-path='url(#clipT)'>")
    # zonas del mapa clásico (aparecen una a una y se rompen en la revelación)
    fade = 1 - seg(t, REVELACION, REVELACION + 0.35)
    temb = 5 * seg(t, 5.0, 6.0) * math.sin(t * 38) * fade
    zonas = [(2.5, AMARGO, f"<ellipse cx='{TX}' cy='1515' rx='160' ry='70'/>"),
             (3.1, ACIDO, "<rect x='380' y='1570' width='58' height='100'/><rect x='642' y='1570' width='58' height='100'/>"),
             (3.7, SALADO, "<rect x='380' y='1670' width='70' height='70'/><rect x='630' y='1670' width='70' height='70'/>"),
             (4.3, DULCE, f"<ellipse cx='{TX}' cy='1800' rx='110' ry='66'/>")]
    for a, col, forma in zonas:
        z = seg(t, a, a + 0.35) * fade
        if z > 0.01:
            dx = temb * (1 if col in (ACIDO, DULCE) else -1)
            s.append(f"<g transform='translate({dx:.1f},0)' fill='{col}' opacity='{0.92 * z:.2f}'>{forma}</g>")
            s.append(f"<g transform='translate({dx:.1f},0)' fill='none' stroke='#fff' stroke-width='5' stroke-dasharray='14 10' "
                     f"opacity='{0.9 * z:.2f}'>{forma}</g>")
    # surco central
    s.append(f"<path d='M{TX} 1530 Q{TX + 6} 1640 {TX} 1730' fill='none' stroke='#d9505f' stroke-width='9' stroke-linecap='round' opacity='{0.9 - 0.5 * rev:.2f}'/>")
    # papilas de todos los colores por toda la lengua
    for x, y, r, col, d in PAPILAS:
        e = rebote(t, REVELACION + d, 0.35)
        if e > 0:
            rr = r * e * (1 + 0.15 * math.sin(t * 6 + x))
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{rr:.1f}' fill='{col}' stroke='{INK}' stroke-width='3'/>")
    s.append("</g>")
    s.append(f"<path d='{TONGUE}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    s.append("</g>")
    return "".join(s)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.5)
    pared_a = mix("#7fd3e6", "#ffe08a", rev); pared_b = mix("#c8f1e9", "#ffb8d0", rev)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{pared_a}'/>"
            f"<stop offset='1' stop-color='{pared_b}'/></linearGradient>"
            "<radialGradient id='halo'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.95'/>"
            "<stop offset='0.5' stop-color='#ffe066' stop-opacity='0.6'/><stop offset='1' stop-color='#ffe066' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='burst'><stop offset='0' stop-color='#fff' stop-opacity='0.9'/>"
            "<stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='clipT'><path d='{TONGUE}'/></clipPath>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         f"<defs>{defs}</defs>", f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    # azulejos suaves en la parte baja de la pared
    s.append(f"<g opacity='0.18' stroke='#fff' stroke-width='4'>"
             + "".join(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}'/>" for y in range(1100, 1860, 110))
             + "".join(f"<line x1='{x}' y1='1100' x2='{x}' y2='1860'/>" for x in range(0, W + 1, 110)) + "</g>")
    # rayos de la revelación (giran)
    if rev > 0:
        rot = t * 18
        rays = "".join(f"<path d='M0 0 L{1500*math.cos(math.radians(a - 6)):.0f} {1500*math.sin(math.radians(a - 6)):.0f} "
                       f"L{1500*math.cos(math.radians(a + 6)):.0f} {1500*math.sin(math.radians(a + 6)):.0f} Z'/>" for a in range(0, 360, 30))
        s.append(f"<g transform='translate(540,1620) rotate({rot:.1f})' fill='#fff' opacity='{0.28 * rev:.2f}'>{rays}</g>")
    # burbujitas que suben
    for bx, by, br, sp in BUBBLES:
        yy = (by - t * sp) % 1950 - 20
        s.append(f"<circle cx='{bx + 14 * math.sin(t * 1.3 + bx):.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='#fff' opacity='0.25'/>")

    escena = []
    # entrada de la cabeza con rebote
    k = seg(t, 0, 0.9)
    dy = 560 * (1 - k) - 34 * math.sin(math.pi * clamp((t - 0.7) / 0.5)) * (t < 1.2)
    tilt = 2.2 * math.sin(t * 1.9)
    escena.append(f"<g transform='translate(0,{dy:.1f}) rotate({tilt:.2f} 540 1760)'>")
    escena.append(f"<ellipse cx='540' cy='1770' rx='360' ry='40' fill='#000' opacity='0.15'/>")
    escena.append(cabeza(t, rev))
    escena.append(lengua(t, rev))
    escena.append("</g>")
    # mesa
    escena.append(f"<rect x='-20' y='1830' width='1120' height='120' fill='#e0a05e' stroke='{INK}' stroke-width='{LW}'/>")
    escena.append("<rect x='-20' y='1846' width='1120' height='14' fill='#f2c088'/>")
    # alimentos flotando a los lados (entran deslizándose)
    ent = seg(t, 0.2, 1.4)
    shake = 4 * seg(t, 5.0, 5.8) * math.sin(t * 30) * (1 - rev)
    items = [(118, 1190, -1, caramelo(DULCE), 0.0), (112, 1610, -1, limon(), 1.1),
             (962, 1170, 1, salero(), 2.2), (958, 1600, 1, taza(t), 3.3)]
    for x, y, lado, dib, fase in items:
        xx = x + lado * 320 * (1 - ent) + shake
        yy = y + 16 * math.sin(t * 2.4 + fase)
        rot = 8 * math.sin(t * 1.8 + fase)
        sc = 1 + 0.22 * rebote(t, REVELACION + 0.05, 0.5) * (t < REVELACION + 0.6) + 0.04 * math.sin(t * 5 + fase) * rev
        if rev > 0:
            escena.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{lerp(60, 110, rev):.0f}' fill='url(#burst)' opacity='{rev:.2f}'/>")
        escena.append(f"<g transform='translate({xx:.1f},{yy:.1f}) rotate({rot:.1f}) scale({sc:.3f})'>{dib}</g>")
    # chispas de colores que salen de la lengua en la revelación
    if t > REVELACION:
        for a, dist, r, col in CHISPAS:
            p = clamp((t - REVELACION) / 1.2)
            if p >= 1: continue
            cx = 540 + math.cos(a) * dist * ease(p)
            cy = 1640 + math.sin(a) * dist * ease(p) * 0.8
            rr = r * (1 - p)
            escena.append(f"<path d='M{cx:.0f} {cy - rr * 1.8:.0f} L{cx + rr * 0.5:.0f} {cy:.0f} L{cx:.0f} {cy + rr * 1.8:.0f} "
                          f"L{cx - rr * 0.5:.0f} {cy:.0f} Z M{cx - rr * 1.8:.0f} {cy:.0f} L{cx:.0f} {cy - rr * 0.5:.0f} "
                          f"L{cx + rr * 1.8:.0f} {cy:.0f} L{cx:.0f} {cy + rr * 0.5:.0f} Z' fill='{col}'/>")
    z = 1 + 0.16 * seg(t, REVELACION - 0.1, 8.0)
    s.append(zoom(540, 1640, z, "".join(escena)))
    s.append("</svg>")
    return "".join(s)
