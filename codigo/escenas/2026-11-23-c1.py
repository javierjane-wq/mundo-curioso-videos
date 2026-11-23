"""2026-11-23-c1 · La anguila eléctrica (Electrophorus voltai) suelta descargas de hasta 860 voltios.

Una anguila eléctrica original entra nadando en un río amazónico (agua verde azulada, fondo de
arena, plantas y una raíz sumergida). Unos pececillos curiosos se le acercan; empiezan a saltar
chispitas por su cuerpo y en la REVELACION suelta una gran descarga: destello amarillo en toda el
agua, rayos que salen del cuerpo, halo y zoom. Los pececillos salen disparados.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 6.8   # gran descarga: golpe musical
MUSICA = 4

rng = np.random.default_rng(23)
MOTES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(0, 6.28), rng.uniform(8, 22))
         for _ in range(60)]
BUBBLES = [(rng.uniform(0, 1), rng.uniform(5, 13), rng.uniform(70, 130), rng.uniform(0, 6.28)) for _ in range(14)]
PEBBLES = [(60, 1800, 34, "#8d7a5c"), (250, 1860, 26, "#a08a66"), (470, 1830, 40, "#7f6d52"),
           (700, 1880, 30, "#9c8662"), (900, 1815, 44, "#86734f"), (1040, 1880, 28, "#a08a66"),
           (380, 1760, 18, "#9c8662"), (820, 1750, 16, "#8d7a5c")]
GRASS = [(40, 1.1, 0.0, "#3f9a52"), (110, 0.8, 1.1, "#56b566"), (180, 0.95, 2.3, "#3f9a52"),
         (900, 0.9, 0.6, "#56b566"), (975, 1.2, 1.7, "#3f9a52"), (1050, 0.85, 2.9, "#2f8545"),
         (560, 0.6, 2.0, "#56b566"), (620, 0.75, 0.4, "#3f9a52")]
# pececillos: (desfase x, y, escala, color, fase)
FISH = [(0, 1170, 1.25, "#ffb347", 0.0), (-170, 1250, 1.05, "#ff7a6b", 1.7), (-90, 1080, 1.0, "#ffd84a", 3.1)]

L = 820          # largo de la anguila (px)
NS = 70          # puntos del espinazo


def radio(s):
    """Medio grosor del cuerpo a lo largo del espinazo (s=0 hocico, s=1 cola)."""
    if s < 0.09:
        return 80 * math.sqrt(max(s, 0.0005) / 0.09)
    if s < 0.35:
        return 80
    return lerp(80, 7, ((s - 0.35) / 0.65) ** 0.9)


def espinazo(t, hx, hy, amp_k):
    pts = []
    for i in range(NS + 1):
        s = i / NS
        a = (14 + 70 * s ** 1.4) * amp_k
        y = hy + a * math.sin(9.0 * s - t * 6.0) - 14 * amp_k * math.sin(-t * 6.0)
        pts.append((hx - s * L, y, s))
    return pts


def bordes(pts, extra=0.0, f=1.0):
    """Devuelve (arriba, abajo, normales hacia abajo) del cuerpo."""
    up, dn, nd = [], [], []
    for i, (x, y, s) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n          # normal
        if ny < 0: nx, ny = -nx, -ny      # que apunte hacia abajo
        r = radio(s) * f + extra
        up.append((x - nx * r, y - ny * r)); dn.append((x + nx * r, y + ny * r)); nd.append((nx, ny))
    return up, dn, nd


def poly(p):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p) + " Z"


def rayo(x0, y0, ang, largo, semilla, ancho=14, col="#ffe03a"):
    r = np.random.default_rng(semilla)
    pts = [(x0, y0)]; n = 7
    for i in range(1, n + 1):
        d = largo * i / n
        j = r.uniform(-1, 1) * largo * 0.09 if i < n else 0
        pts.append((x0 + math.cos(ang) * d - math.sin(ang) * j, y0 + math.sin(ang) * d + math.cos(ang) * j))
    p = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f"<path d='{p}' fill='none' stroke='{INK}' stroke-width='{ancho + 10}' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<path d='{p}' fill='none' stroke='{col}' stroke-width='{ancho}' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<path d='{p}' fill='none' stroke='#ffffff' stroke-width='{ancho * 0.35:.1f}' stroke-linejoin='round' stroke-linecap='round'/>")


def chispa(x, y, sz, semilla):
    r = np.random.default_rng(semilla)
    ang = r.uniform(0, 6.28)
    pts = [(x, y)]
    for i in range(3):
        ang += r.uniform(-0.9, 0.9)
        x += math.cos(ang) * sz; y += math.sin(ang) * sz
        pts.append((x, y))
    p = "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in pts)
    return (f"<path d='{p}' fill='none' stroke='{INK}' stroke-width='11' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='{p}' fill='none' stroke='#fff36b' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")


def anguila(t, hx, hy, glow):
    amp_k = 1.0 if t < 2.6 else 0.75
    pts = espinazo(t, hx, hy, amp_k)
    up, dn, nd = bordes(pts)
    g = []
    # aleta anal: cinta ondulante a lo largo de la panza
    fin_out, fin_in = [], []
    for i, (x, y, s) in enumerate(pts):
        if 0.16 <= s <= 0.99:
            h = (30 + 10 * math.sin(s * 46 - t * 14)) * (1 - (s - 0.16) * 0.55)
            nx, ny = nd[i]
            bx, by = dn[i]
            fin_in.append((bx - nx * 10, by - ny * 10)); fin_out.append((bx + nx * h, by + ny * h))
    g.append(f"<path d='{poly(fin_in + fin_out[::-1])}' fill='{mix('#c99a5e', '#ffe9a0', glow)}' fill-opacity='0.9' "
             f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    for k in range(0, len(fin_out), 3):
        g.append(f"<line x1='{fin_in[k][0]:.0f}' y1='{fin_in[k][1]:.0f}' x2='{fin_out[k][0]:.0f}' y2='{fin_out[k][1]:.0f}' "
                 f"stroke='#8a6436' stroke-width='3' opacity='0.6'/>")
    # aletas pectorales pequeñas
    px, py, _ = pts[8]
    flap = 10 * math.sin(t * 9)
    g.append(f"<g transform='translate({px:.1f},{py + 30:.1f}) rotate({20 + flap:.1f})'>"
             f"<ellipse cx='-6' cy='26' rx='17' ry='30' fill='{mix('#d9a868', '#fff0b0', glow)}' stroke='{INK}' stroke-width='6'/></g>")
    # cuerpo
    body = poly(up + dn[::-1])
    g.append(f"<path d='{body}' fill='{mix('#4f5b3c', '#9fa860', glow * 0.6)}' stroke='none'/>")
    # panza naranja (E. voltai tiene la garganta y la panza anaranjadas)
    _, b1, _ = bordes(pts, 0, 0.18)
    belly = [b1[i] for i in range(1, int(NS * 0.62))] + [dn[i] for i in range(int(NS * 0.62) - 1, 0, -1)]
    g.append(f"<path d='{poly(belly)}' fill='{mix('#ef8a3a', '#ffd15a', glow)}' stroke='none'/>")
    # lomo más oscuro
    u2, _, _ = bordes(pts, 0, 0.55)
    back = [up[i] for i in range(1, NS)] + [u2[i] for i in range(NS - 1, 0, -1)]
    g.append(f"<path d='{poly(back)}' fill='{mix('#39432b', '#7f8a48', glow * 0.6)}' stroke='none' opacity='0.85'/>")
    # puntitos de la línea lateral
    for i in range(10, int(NS * 0.85), 5):
        x, y, s = pts[i]
        g.append(f"<circle cx='{x:.0f}' cy='{y - radio(s) * 0.2:.0f}' r='{max(2.5, radio(s) * 0.1):.1f}' fill='{mix('#c9cf9a', '#fffbd0', glow)}'/>")
    g.append(f"<path d='{body}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cabeza: boca, ojo, fosas
    hx0, hy0, _ = pts[0]
    x3, y3, _ = pts[3]
    ang = math.degrees(math.atan2(hy0 - y3, hx0 - x3))
    blink = 1.0 if ((t + 1.0) % 2.9) > 0.13 else 0.12
    wide = seg(t, REVELACION - 0.1, REVELACION + 0.2)
    g.append(f"<g transform='translate({hx0:.1f},{hy0:.1f}) rotate({ang:.1f})'>")
    g.append(f"<path d='M-4 14 Q-30 30 -62 22' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<path d='M-62 22 Q-68 18 -66 12' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<circle cx='-14' cy='-6' r='4' fill='{INK}'/>")
    er = lerp(17, 21, wide)
    g.append(f"<circle cx='-50' cy='-24' r='{er + 5:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<g transform='translate(-47,-24) scale(1,{blink})'><circle r='{er * 0.62:.1f}' fill='#1b1f24'/>"
             f"<circle cx='-4' cy='-5' r='{er * 0.25:.1f}' fill='#fff'/></g>")
    g.append("</g>")
    return "".join(g), pts


def pececillo(x, y, sc, col, t, ph, flip=False):
    tail = 14 * math.sin(t * 12 + ph)
    blink = 1.0 if ((t + ph) % 2.4) > 0.12 else 0.15
    sx = -sc if flip else sc
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({sx:.3f},{sc:.3f})'>"
            f"<path d='M-46 0 L-86 {-30 + tail:.1f} L-80 {30 + tail:.1f} Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='0' rx='56' ry='36' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-8 -34 Q8 -56 26 -32' fill='{col}' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-14 -26 Q-22 0 -14 26' fill='none' stroke='{INK}' stroke-width='4' opacity='0.5'/>"
            f"<circle cx='24' cy='-8' r='13' fill='#fff' stroke='{INK}' stroke-width='5'/>"
            f"<g transform='translate(27,-8) scale(1,{blink})'><circle r='7' fill='#1b1f24'/><circle cx='-2' cy='-3' r='2.5' fill='#fff'/></g>"
            f"<path d='M44 8 Q50 12 46 16' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")


def frame(t):
    flash = 0.0 if t < REVELACION else math.exp(-(t - REVELACION) * 5.0)   # destello
    glow = seg(t, 4.6, REVELACION) * 0.35 + seg(t, REVELACION, REVELACION + 0.25) * 0.65
    lit = seg(t, REVELACION, REVELACION + 0.3)                            # agua iluminada tras la descarga
    crack = 0.85 + 0.15 * math.sin(t * 40)
    top = mix(mix("#2c8c8a", "#3fb7b0", lit * 0.6), "#fffbe0", flash * 0.85)
    mid = mix(mix("#1c6366", "#2f8f7c", lit * 0.6), "#fff3a8", flash * 0.8)
    low = mix(mix("#123f44", "#2a6a52", lit * 0.6), "#ffe46b", flash * 0.75)
    defs = (f"<linearGradient id='agua' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<linearGradient id='rayo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#eafff5' stop-opacity='0.32'/>"
            "<stop offset='1' stop-color='#eafff5' stop-opacity='0'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fffbd0' stop-opacity='{0.9 * lit * crack:.3f}'/>"
            f"<stop offset='0.45' stop-color='#ffe85a' stop-opacity='{0.55 * lit * crack:.3f}'/>"
            "<stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='pre'><stop offset='0' stop-color='#fff59a' stop-opacity='{0.45 * seg(t, 4.8, REVELACION):.3f}'/>"
            "<stop offset='1' stop-color='#fff59a' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#agua)'/>"]
    # rayos de luz desde la superficie (arriba, tranquilos)
    for i, (x, w) in enumerate([(120, 120), (380, 90), (640, 140), (900, 100)]):
        sw = 40 * math.sin(t * 0.7 + i * 1.3)
        s.append(f"<path d='M{x:.0f} 0 L{x + w:.0f} 0 L{x + w + 220 + sw:.0f} 1500 L{x + 120 + sw:.0f} 1500 Z' fill='url(#rayo)'/>")
    # partículas flotando
    for mx, my, mr, ph, sp in MOTES:
        yy = (my - t * sp) % H
        s.append(f"<circle cx='{mx + 14 * math.sin(t * 0.8 + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#e9fff4' opacity='0.35'/>")
    # cámara
    hx = lerp(330, 930, seg(t, 0, 2.4)) + 18 * math.sin(t * 1.1) * seg(t, 2.4, 3.2)
    hy = 1420 + 10 * math.sin(t * 1.4)
    z = 1 + 0.16 * seg(t, REVELACION, REVELACION + 0.75)
    shake = 7 * flash * math.sin(t * 90)
    scene = []
    # raíz sumergida a la derecha (bosque inundado)
    scene.append(f"<path d='M1080 1000 Q980 1080 1000 1240 Q1010 1380 940 1520 L980 1540 Q1060 1400 1080 1300 Z' "
                 f"fill='{mix('#5a3d2a', '#8a6238', lit * 0.5)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    scene.append(f"<path d='M1080 1150 Q1030 1230 1050 1330 L1080 1340 Z' fill='{mix('#6e4b33', '#9a7040', lit * 0.5)}' stroke='{INK}' stroke-width='6'/>")
    scene.append(f"<path d='M0 1080 Q70 1130 60 1260 Q55 1330 90 1400 L50 1410 Q10 1330 0 1300 Z' "
                 f"fill='{mix('#5a3d2a', '#8a6238', lit * 0.5)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # fondo del río
    s_col = mix(mix("#b39a6c", "#d8bd80", lit * 0.6), "#fff2b0", flash * 0.6)
    scene.append(f"<path d='M0 1700 Q270 1650 540 1690 T1080 1680 L1080 1920 L0 1920 Z' fill='{s_col}' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, sc, ph, col in GRASS:
        sw = 22 * math.sin(t * 1.5 + ph)
        y0 = 1712
        d = (f"M{gx - 14} {y0} C{gx - 26 + sw * 0.3:.0f} {y0 - 120 * sc:.0f} {gx + 16 + sw * 0.7:.0f} {y0 - 210 * sc:.0f} "
             f"{gx + sw:.0f} {y0 - 300 * sc:.0f} C{gx + 22 + sw * 0.6:.0f} {y0 - 200 * sc:.0f} {gx + 16 + sw * 0.2:.0f} {y0 - 110 * sc:.0f} {gx + 14} {y0} Z")
        scene.append(f"<path d='{d}' fill='{mix(col, '#a6e36a', lit * 0.4)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    for px, py, pr, col in PEBBLES:
        scene.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr}' ry='{pr * 0.62:.0f}' fill='{mix(col, '#e6cf96', lit * 0.4)}' stroke='{INK}' stroke-width='6'/>")
    # brillo previo (tensión)
    scene.append(f"<ellipse cx='{hx - 380:.0f}' cy='{hy:.0f}' rx='600' ry='260' fill='url(#pre)'/>")
    scene.append(f"<ellipse cx='{hx - 380:.0f}' cy='{hy:.0f}' rx='{lerp(560, 760, lit):.0f}' ry='{lerp(260, 420, lit):.0f}' fill='url(#halo)'/>")
    # pececillos: llegan, se acercan curiosos y salen disparados en la descarga
    run = seg(t, REVELACION, REVELACION + 0.9)
    for dx, fy, sc, col, ph in FISH:
        fx = lerp(1320, 960, seg(t, 1.4, 4.0)) + dx - lerp(0, 60, seg(t, 4.3, 6.6)) + 8 * math.sin(t * 2 + ph)
        fy2 = fy + 14 * math.sin(t * 1.8 + ph)
        if run > 0:
            fx += run * 700; fy2 -= run * 160 * (1 if dx else -0.3)
        jit = 9 * flash * math.sin(t * 70 + ph)
        scene.append(pececillo(fx + jit, fy2 + jit, sc, col, t, ph, flip=run == 0))
    # rayos de la descarga
    if t >= REVELACION:
        semilla = int(t * 15)
        amp = lerp(1.0, 0.55, seg(t, REVELACION, REVELACION + 0.7)) * crack
        for k, (ang, lg) in enumerate([(-2.5, 470), (-1.75, 400), (-1.1, 420), (-0.35, 460),
                                        (2.75, 420), (1.9, 300), (0.7, 380)]):
            sx0 = hx - 360 + math.cos(ang) * 300; sy0 = hy + math.sin(ang) * 90
            scene.append(rayo(sx0, sy0, ang, lg * amp, semilla * 31 + k, ancho=lerp(12, 22, amp)))
    eel, pts = anguila(t, hx, hy, glow)
    scene.append(eel)
    # chispitas sobre el cuerpo (desde 5 s, cada vez más)
    if t > 4.6:
        nchis = int(lerp(1, 5, seg(t, 4.6, REVELACION))) + (2 if t >= REVELACION else 0)
        r = np.random.default_rng(int(t * 12) + 5)
        for k in range(nchis):
            i = int(r.uniform(4, NS * 0.85))
            x, y, sss = pts[i]
            scene.append(chispa(x + r.uniform(-30, 30), y + r.uniform(-80, 80), r.uniform(16, 30), int(t * 12) * 50 + k))
    # burbujas de la boca
    for bx, br, sp, ph in BUBBLES:
        cyc = (t * 0.45 + bx) % 1.0
        x = hx + 10 + 30 * math.sin(t * 2 + ph) + cyc * 60
        y = hy - 30 - cyc * 650
        a = 0.8 * (1 - cyc)
        if y > 960:
            scene.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{br:.1f}' fill='#e9fff8' fill-opacity='0.3' stroke='#fff' "
                         f"stroke-opacity='{a:.2f}' stroke-width='3.5'/>")
    cx, cy = hx - 380, hy
    s.append(f"<g transform='translate({shake:.1f},{shake * 0.6:.1f})'>"
             f"<g transform='translate({cx:.1f},{cy:.1f}) scale({z:.4f}) translate({-cx:.1f},{-cy:.1f})'>{''.join(scene)}</g></g>")
    # destello blanco sobre todo
    if flash > 0.02:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.55 * flash:.3f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
