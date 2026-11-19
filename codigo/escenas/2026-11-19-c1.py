"""2026-11-19-c1 · El pez globo se infla tragando agua cuando lo amenazan.

Un pez globo nada tranquilo entre corales; se acerca un pez grande con la boca abierta,
el pez globo se asusta y en la REVELACION se infla de golpe (traga agua) y se convierte
en una bola de pinchos: destello de luz, burbujas y zoom. El depredador huye.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.4   # el pez globo se infla: golpe musical
MUSICA = 8

rng = np.random.default_rng(19)
BUBBLES = [(rng.uniform(40, W - 40), rng.uniform(0, 1), rng.uniform(6, 16), rng.uniform(60, 140), rng.uniform(0, 6.28))
           for _ in range(34)]
MOTES = [(rng.uniform(0, W), rng.uniform(0, 1000), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(45)]
SPOTS = [(-0.45, -0.35, 0.09), (-0.15, -0.55, 0.08), (0.12, -0.42, 0.07), (-0.62, -0.05, 0.07),
         (-0.3, -0.12, 0.06), (0.02, -0.2, 0.05), (-0.75, -0.38, 0.05)]
WEEDS = [(70, 1760, 1.15, 0.0, "#3fae5a"), (190, 1760, 0.85, 1.3, "#58c46c"), (960, 1760, 1.25, 2.1, "#3fae5a"),
         (1040, 1760, 0.8, 0.7, "#2f9a4c"), (860, 1760, 0.7, 3.0, "#58c46c")]


def burbuja(x, y, r, a=0.75):
    return (f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='#dff6ff' fill-opacity='{0.35*a:.2f}' "
            f"stroke='#ffffff' stroke-opacity='{a:.2f}' stroke-width='3.5'/>"
            f"<circle cx='{x - r*0.35:.1f}' cy='{y - r*0.35:.1f}' r='{r*0.25:.1f}' fill='#fff' opacity='{a:.2f}'/>")


def alga(x, y, sc, ph, col, t):
    sw = 26 * math.sin(t * 1.6 + ph)
    d = (f"M{x - 18} {y} C{x - 40 + sw*0.3:.0f} {y - 150*sc:.0f} {x + 30 + sw*0.7:.0f} {y - 250*sc:.0f} "
         f"{x + sw:.0f} {y - 380*sc:.0f} C{x + 30 + sw*0.8:.0f} {y - 260*sc:.0f} {x + 20 + sw*0.3:.0f} {y - 140*sc:.0f} {x + 18} {y} Z")
    return f"<path d='{d}' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"


def coral(x, y, sc, col):
    """Coral ramificado (forma de cuerno de ciervo) con contorno grueso."""
    g = [f"<g transform='translate({x},{y}) scale({sc})'>"]
    ramas = [(-5, 0, -10, -150), (-10, -90, -70, -170), (-8, -60, 60, -150), (-40, -140, -60, -210),
             (40, -120, 75, -200), (-10, -150, 10, -230)]
    for x1, y1, x2, y2 in ramas:
        g.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{INK}' stroke-width='38' stroke-linecap='round'/>")
    for x1, y1, x2, y2 in ramas:
        g.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{col}' stroke-width='22' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def pez_globo(t, cx, cy, p, susto):
    """Pez globo original (mira a la derecha). p: 0 = normal, 1 = inflado. susto: ojos muy abiertos."""
    rx = lerp(150, 285, p); ry = lerp(100, 275, p)
    wag = 18 * math.sin(t * 9) * (1 - 0.6 * p)
    fin = 22 * math.sin(t * 11)
    blink = 1.0 if (t % 2.7) > 0.12 or susto > 0.5 else 0.12
    body, belly, spot = "#f4c542", "#fff3c9", "#9a6a2a"
    g = [f"<g transform='translate({cx:.1f},{cy:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='{1745 - cy:.0f}' rx='{rx*0.9:.0f}' ry='22' fill='#0b3b55' opacity='0.18'/>")
    # cola (a la izquierda)
    tx = -rx + 18
    g.append(f"<g transform='translate({tx:.1f},0) rotate({wag:.1f})'>"
             f"<path d='M0 0 L-95 -62 Q-80 0 -95 62 Z' fill='#e9a52a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M-20 -6 L-70 -36 M-20 6 L-70 36' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")
    # aleta dorsal y anal (pequeñas, atrás)
    g.append(f"<path d='M{-rx*0.55:.1f} {-ry*0.82:.1f} Q{-rx*0.7:.1f} {-ry*0.82 - 70:.1f} {-rx*0.9:.1f} {-ry*0.62 - 40:.1f} "
             f"L{-rx*0.82:.1f} {-ry*0.5:.1f} Z' fill='#e9a52a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M{-rx*0.55:.1f} {ry*0.82:.1f} Q{-rx*0.7:.1f} {ry*0.82 + 60:.1f} {-rx*0.9:.1f} {ry*0.62 + 35:.1f} "
             f"L{-rx*0.82:.1f} {ry*0.5:.1f} Z' fill='#e9a52a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # pinchos (salen al inflarse)
    if p > 0.02:
        n = 30
        for i in range(n):
            a = 2 * math.pi * i / n + 0.1
            if math.cos(a) < -0.88:
                continue   # sin pinchos donde está la cola
            L = lerp(0, 46, ease(p))
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            nx, ny = math.cos(a), math.sin(a)
            px, py = -ny, nx
            b = 13
            g.append(f"<path d='M{ex + px*b - nx*6:.1f} {ey + py*b - ny*6:.1f} L{ex + nx*L:.1f} {ey + ny*L:.1f} "
                     f"L{ex - px*b - nx*6:.1f} {ey - py*b - ny*6:.1f} Z' fill='#fff1c2' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cuerpo
    g.append(f"<ellipse cx='0' cy='0' rx='{rx:.1f}' ry='{ry:.1f}' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<clipPath id='cb'><ellipse cx='0' cy='0' rx='{rx - 4:.1f}' ry='{ry - 4:.1f}'/></clipPath>")
    g.append(f"<g clip-path='url(#cb)'><ellipse cx='{rx*0.05:.1f}' cy='{ry*0.62:.1f}' rx='{rx*0.95:.1f}' ry='{ry*0.55:.1f}' fill='{belly}'/></g>")
    for sx, sy, sr in SPOTS:
        g.append(f"<circle cx='{sx*rx:.1f}' cy='{sy*ry:.1f}' r='{sr*(rx+ry)*0.5:.1f}' fill='{spot}' opacity='0.85'/>")
    # puntitos de pinchos plegados (cuando no está inflado)
    if p < 0.6:
        for i in range(10):
            a = 0.6 + i * 0.22
            g.append(f"<circle cx='{rx*0.75*math.cos(a+1.6):.1f}' cy='{ry*0.75*math.sin(a+1.6):.1f}' r='3.5' fill='{INK}' opacity='{0.5*(1-p/0.6):.2f}'/>")
    # aleta pectoral
    g.append(f"<g transform='translate({rx*0.12:.1f},{ry*0.15:.1f}) rotate({fin:.1f})'>"
             f"<path d='M0 0 Q-60 -40 -78 8 Q-50 40 0 0 Z' fill='#e9a52a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # ojo grande (lado derecho, arriba)
    ex, ey = rx * 0.5, -ry * 0.28
    er = lerp(40, 52, p) + 6 * susto
    g.append(f"<circle cx='{ex:.1f}' cy='{ey:.1f}' r='{er:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
    pr = er * lerp(0.55, 0.38, susto)
    look = er * 0.22
    g.append(f"<g transform='translate({ex + look:.1f},{ey:.1f}) scale(1,{blink})'>"
             f"<circle r='{pr:.1f}' fill='#1b2a3a'/><circle cx='{-pr*0.35:.1f}' cy='{-pr*0.4:.1f}' r='{pr*0.35:.1f}' fill='#fff'/></g>")
    # párpado al parpadear
    if blink < 1:
        g.append(f"<path d='M{ex - er:.1f} {ey:.1f} Q{ex:.1f} {ey - er*0.2:.1f} {ex + er:.1f} {ey:.1f}' stroke='{INK}' stroke-width='6' fill='none'/>")
    # boca (pequeña, al frente); al inflarse, mejillas llenas y boca en "o"
    mx = rx * 0.93; my = ry * 0.12
    if p < 0.5:
        g.append(f"<path d='M{mx - 30:.1f} {my:.1f} Q{mx - 10:.1f} {my + 16:.1f} {mx + 6:.1f} {my - 2:.1f}' stroke='{INK}' stroke-width='7' fill='none' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='{mx - 12:.1f}' cy='{my:.1f}' rx='14' ry='17' fill='#c2463a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='{rx*0.6:.1f}' cy='{ry*0.22:.1f}' rx='{18 + 8*p:.1f}' ry='{11 + 5*p:.1f}' fill='#ff8a6b' opacity='0.55'/>")
    g.append("</g>")
    return "".join(g)


def depredador(t, x, y, flip):
    """Pez grande original con la boca abierta (mira a la izquierda; flip=-1 lo gira al huir)."""
    jaw = 18 + 10 * math.sin(t * 6)
    blink = 1.0 if (t % 3.3) > 0.12 else 0.15
    wag = 14 * math.sin(t * 7)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({flip},1)'>"]
    g.append(f"<g transform='translate(250,0) rotate({wag:.1f})'><path d='M0 0 L120 -95 Q95 0 120 95 Z' fill='#3d5f8c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    g.append(f"<path d='M-40 -150 Q60 -250 170 -135 Z' fill='#3d5f8c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='20' cy='0' rx='260' ry='155' fill='#5b80b0' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<clipPath id='cp'><ellipse cx='20' cy='0' rx='255' ry='150'/></clipPath>")
    g.append(f"<g clip-path='url(#cp)'><ellipse cx='0' cy='120' rx='300' ry='90' fill='#c9dcef'/>"
             + "".join(f"<path d='M{sx} -60 q20 30 0 60' stroke='#3d5f8c' stroke-width='6' fill='none'/>" for sx in (60, 110, 160)) + "</g>")
    # boca abierta con dientes
    g.append(f"<path d='M-245 {-10 - jaw:.1f} L-130 0 L-245 {10 + jaw:.1f} Z' fill='#7a1f2b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(3):
        tx = -232 + k * 34
        g.append(f"<path d='M{tx} {-8 - jaw*(1 - k*0.3):.1f} l10 18 l10 -18 Z' fill='#fff' stroke='{INK}' stroke-width='4'/>")
        g.append(f"<path d='M{tx} {8 + jaw*(1 - k*0.3):.1f} l10 -18 l10 18 Z' fill='#fff' stroke='{INK}' stroke-width='4'/>")
    # ojo con ceja
    g.append(f"<circle cx='-120' cy='-60' r='36' fill='#fff' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<g transform='translate(-132,-56) scale(1,{blink})'><circle r='17' fill='#1b2a3a'/><circle cx='-6' cy='-6' r='6' fill='#fff'/></g>")
    g.append(f"<path d='M-165 -110 L-80 -90' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    g.append(f"<path d='M-40 40 Q-10 80 30 50' fill='#3d5f8c' stroke='{INK}' stroke-width='7'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    infl = seg(t, REVELACION - 0.05, REVELACION + 0.5)
    pop = rebote(t, REVELACION - 0.05, 0.75)
    p = clamp(infl * (pop if pop > 0 else 0))
    p = clamp(p if t < REVELACION + 0.75 else 1.0, 0, 1.08)
    susto = seg(t, 5.6, 6.3)
    flash = clamp(1 - abs(t - (REVELACION + 0.15)) / 0.55) if t > REVELACION - 0.4 else 0
    light = seg(t, REVELACION, REVELACION + 0.6)

    top = mix("#0b4f7a", "#1a77a8", light); mid = mix("#1384b4", "#2aa6d4", light); low = mix("#0d5f86", "#1789b6", light)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>", "<defs>",
         f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#5fd0f0', '#8fe6ff', light)}'/>"
         f"<stop offset='0.25' stop-color='{mid}'/><stop offset='0.7' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<linearGradient id='ray' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='0.35'/>"
         "<stop offset='1' stop-color='#ffffff' stop-opacity='0'/></linearGradient>",
         f"<radialGradient id='burst'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.9*flash:.3f}'/>"
         f"<stop offset='0.4' stop-color='#ffe680' stop-opacity='{0.55*flash:.3f}'/><stop offset='1' stop-color='#ffe680' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#bff4ff' stop-opacity='{0.45*light:.3f}'/><stop offset='1' stop-color='#bff4ff' stop-opacity='0'/></radialGradient>",
         "</defs>", f"<rect width='{W}' height='{H}' fill='url(#sea)'/>"]
    # superficie ondulada arriba
    wv = "".join(f" Q{x + 45} {40 + 14*math.sin(t*2 + x*0.02):.0f} {x + 90} 40" for x in range(-90, W + 90, 90))
    s.append(f"<path d='M-90 0 L{W + 90} 0 L{W + 90} 40 L-90 40 Z' fill='#a6ecff' opacity='0.5'/>"
             f"<path d='M-90 40{wv}' fill='none' stroke='#e8fbff' stroke-width='6' opacity='0.7'/>")
    # rayos de luz (fondo tranquilo)
    for i, (x0, w0) in enumerate([(120, 120), (380, 90), (640, 140), (900, 100)]):
        sh = 30 * math.sin(t * 0.8 + i)
        s.append(f"<path d='M{x0 + sh:.0f} 0 L{x0 + w0 + sh:.0f} 0 L{x0 + w0*2.2 + sh:.0f} 1300 L{x0 + w0*0.6 + sh:.0f} 1300 Z' fill='url(#ray)' opacity='{0.55 + 0.25*math.sin(t*1.3 + i):.2f}'/>")
    for mx, my, mr, ph in MOTES:
        s.append(f"<circle cx='{mx + 10*math.sin(t + ph):.0f}' cy='{(my - t*8) % 1000:.0f}' r='{mr:.1f}' fill='#e6fbff' opacity='{0.35 + 0.2*math.sin(t*2 + ph):.2f}'/>")
    # bancos de peces lejanos (siluetas suaves)
    for k in range(6):
        fx = (t * 60 + k * 70) % 1500 - 200; fy = 860 + 18 * math.sin(k * 1.7 + t * 2)
        s.append(f"<g transform='translate({fx:.0f},{fy + k*14:.0f})' opacity='0.35'><ellipse rx='26' ry='11' fill='#0b3b55'/>"
                 f"<path d='M-24 0 L-42 -12 L-42 12 Z' fill='#0b3b55'/></g>")
    cam_cx, cam_cy = 520, 1380
    z = 1 + 0.13 * seg(t, REVELACION, REVELACION + 1.4)
    s.append(f"<g transform='translate({cam_cx},{cam_cy}) scale({z:.4f}) translate({-cam_cx},{-cam_cy})'>")
    # rocas lejanas y fondo marino
    s.append(f"<path d='M0 1500 Q150 1400 320 1460 Q520 1380 700 1450 Q900 1390 1080 1440 L1080 1920 L0 1920 Z' fill='#2b7f8f' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(coral(150, 1700, 1.15, "#ff6f91"))
    s.append(coral(930, 1660, 0.95, "#ff9f43"))
    for wx, wy, sc, ph, col in WEEDS:
        s.append(alga(wx, wy, sc, ph, col, t))
    s.append(f"<path d='M0 1700 Q270 1640 540 1690 Q810 1740 1080 1680 L1080 1920 L0 1920 Z' fill='#f2d49b' stroke='{INK}' stroke-width='{LW}'/>")
    for rx_, ry_, rr in [(300, 1800, 40), (700, 1830, 30), (520, 1760, 22), (880, 1820, 48)]:
        s.append(f"<ellipse cx='{rx_}' cy='{ry_}' rx='{rr}' ry='{rr*0.6:.0f}' fill='#c99b5e' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<g transform='translate(620,1795)'><path d='M0 -40 L10 -12 L40 -12 L16 6 L26 36 L0 18 L-26 36 L-16 6 L-40 -12 L-10 -12 Z' fill='#ff7a45' stroke='{INK}' stroke-width='6' stroke-linejoin='round' transform='rotate({8*math.sin(t*1.5):.1f})'/></g>")
    # depredador: entra desde la derecha 4,6-7,2 s; huye tras la revelación
    if t < REVELACION + 0.3:
        px_ = lerp(1330, 950, seg(t, 3.9, 7.1)) + 8 * math.sin(t * 5)
        s.append(depredador(t, px_, 1150 + 10 * math.sin(t * 2), 1))
    else:
        k = seg(t, REVELACION + 0.3, REVELACION + 1.6)
        px_ = lerp(950, 1600, k)
        s.append(depredador(t, px_, 1150 - 60 * k, -1))
    # pez globo: entra desde la izquierda 0-2,2 s
    fx = lerp(110, 460, seg(t, 0, 2.3)) + 10 * math.sin(t * 1.7)
    fy = 1390 + 14 * math.sin(t * 2.2)
    if 5.6 < t < REVELACION:
        fx += 5 * math.sin(t * 60) * susto; fx -= 40 * seg(t, 5.6, 6.6)
    if t >= REVELACION:
        fx = lerp(fx - 40, 500, seg(t, REVELACION, REVELACION + 0.6))
        fy -= 40 * seg(t, REVELACION, REVELACION + 0.6)
    s.append(f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='{lerp(300, 520, light):.0f}' fill='url(#glow)'/>")
    s.append(f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='{lerp(200, 700, light):.0f}' fill='url(#burst)'/>")
    # anillos de choque en la revelación
    if REVELACION <= t < REVELACION + 1.0:
        k = (t - REVELACION) / 1.0
        for j in range(2):
            kk = clamp(k - j * 0.2)
            if kk > 0:
                s.append(f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='{lerp(280, 620, kk):.0f}' fill='none' stroke='#ffffff' stroke-width='{lerp(14, 2, kk):.1f}' opacity='{0.8*(1-kk):.2f}'/>")
    # burbujas de agua tragada (entran hacia la boca justo antes) y salen al inflarse
    if REVELACION - 0.6 < t < REVELACION + 0.2:
        for j in range(6):
            k = clamp((t - (REVELACION - 0.6) - j * 0.06) / 0.4)
            if 0 < k < 1:
                bx = lerp(fx + 330, fx + 150, k); by = fy + 15 + 30 * math.sin(j * 2.3) * (1 - k)
                s.append(burbuja(bx, by, 12 - j, 0.9))
    s.append(pez_globo(t, fx, fy, p, susto))
    # burbujas que suben
    for bx, b0, br, sp, ph in BUBBLES:
        yy = 1950 - ((b0 * 1000 + t * sp) % 1000) - 0
        if yy > 1020:
            s.append(burbuja(bx + 14 * math.sin(t * 2 + ph), yy, br, 0.7))
    if t >= REVELACION:
        for j in range(14):
            a = j * 2 * math.pi / 14
            k = clamp((t - REVELACION) / 1.6)
            d = lerp(300, 560, k)
            s.append(burbuja(fx + d * math.cos(a), fy + d * math.sin(a) - 120 * k, 12 + 5 * (j % 3), 0.85 * (1 - k)))
    s.append("</g></svg>")
    return "".join(s)
