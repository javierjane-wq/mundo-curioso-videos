"""2026-11-11-c4 · Récords: el tren maglev japonés L0 alcanzó 603 km/h (2015), el tren más rápido.

Un tren bala de morro largo arranca sobre su vía elevada con ruedas, como cualquier tren.
Luego guarda las ruedas, flota sobre imanes (brillo azul) y en la revelación sale disparado:
el cielo cambia, líneas de velocidad, halo bajo el tren y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.45   # el tren flota y sale disparado
MUSICA = 4

DECK = 1585         # parte de arriba de la vía elevada
rng = np.random.default_rng(23)
CLOUDS = [(rng.uniform(0, W), rng.uniform(250, 820), rng.uniform(0.8, 1.4), rng.uniform(8, 20)) for _ in range(5)]
STREAKS = [(rng.uniform(0, 1), rng.uniform(1050, 1900), rng.uniform(120, 420), rng.uniform(4, 10)) for _ in range(40)]
SPARK = [(rng.uniform(0, 1), rng.uniform(0, 6.28), rng.uniform(4, 9)) for _ in range(26)]


def velocidad(t):
    """Velocidad del paisaje (px/s)."""
    if t < 2.2: return lerp(120, 360, t / 2.2)
    if t < 5.0: return lerp(360, 1100, (t - 2.2) / 2.8)
    if t < 7.45: return lerp(1100, 2200, (t - 5.0) / 2.45)
    return lerp(2200, 6500, seg(t, 7.45, 8.3))


def recorrido(t, paso=1 / 120):
    n = int(t / paso); s = 0.0
    for i in range(n): s += velocidad(i * paso) * paso
    return s + velocidad(n * paso) * (t - n * paso)


def tren(t, nose_x, lift, rev, glow):
    """Tren maglev original: morro muy largo y aplanado, franja azul, ventanillas."""
    y = DECK - 56 - lift
    shake = 3 * math.sin(t * 47) * (1 - seg(t, 5.2, 6.0)) if t < 6 else 1.5 * math.sin(t * 61)
    g = [f"<g transform='translate({nose_x:.1f},{y + shake:.1f})'>"]
    cuerpo = ("M-2600 0 L-2600 -232 Q-2600 -250 -2582 -250 L-640 -250 "
              "C-380 -250 -170 -150 -40 -62 Q4 -32 -6 -10 Q-12 0 -40 0 Z")
    g.append(f"<clipPath id='ctren'><path d='{cuerpo}'/></clipPath>")
    # halo azul de los imanes
    if glow > 0.01:
        g.append(f"<ellipse cx='-900' cy='{lift/2+20:.1f}' rx='1300' ry='{40+lift*0.6:.1f}' fill='url(#mag)' opacity='{glow:.2f}'/>")
    # ruedas (se esconden al flotar)
    hide = seg(t, 5.0, 5.9)
    rot = recorrido(t) / 26 * 57.3
    for wx in (-430, -720, -1240, -1560, -2080):
        if hide < 0.98:
            wy = 30 - 24 * hide
            g.append(f"<g transform='translate({wx},{wy:.1f}) scale({1 - hide:.3f}) rotate({rot % 360:.1f})'>"
                     f"<circle r='26' fill='#3a3f47' stroke='{INK}' stroke-width='6'/>"
                     f"<line x1='-18' y1='0' x2='18' y2='0' stroke='#c7ccd4' stroke-width='6'/>"
                     f"<line x1='0' y1='-18' x2='0' y2='18' stroke='#c7ccd4' stroke-width='6'/></g>")
    # carrocería
    g.append(f"<path d='{cuerpo}' fill='{mix('#f7f9fc', '#ffffff', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("<g clip-path='url(#ctren)'>")
    g.append(f"<rect x='-2600' y='-250' width='2700' height='60' fill='#e3e9f1'/>")
    g.append(f"<rect x='-2600' y='-74' width='2700' height='30' fill='{mix('#1f64c8', '#21b8ff', rev)}'/>")
    g.append(f"<rect x='-2600' y='-40' width='2700' height='12' fill='{mix('#1f64c8', '#21b8ff', rev)}'/>")
    g.append(f"<rect x='-2600' y='-16' width='2700' height='20' fill='#c9d1dc'/>")
    g.append("</g>")
    g.append(f"<path d='{cuerpo}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cabina
    g.append(f"<path d='M-560 -238 C-430 -232 -330 -192 -262 -150 L-300 -138 C-380 -168 -470 -190 -600 -196 Z' "
             f"fill='#1c2c44' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M-540 -222 C-470 -216 -420 -200 -380 -184' stroke='#8fd3ff' stroke-width='6' fill='none' stroke-linecap='round'/>")
    # faro
    g.append(f"<ellipse cx='-120' cy='-58' rx='26' ry='11' fill='{mix('#fff6c8', '#ffffff', rev)}' stroke='{INK}' stroke-width='5'/>")
    # ventanillas y puertas
    for wx in range(-1340, -700, 92):
        g.append(f"<rect x='{wx}' y='-188' width='58' height='50' rx='14' fill='#2a3f5e' stroke='{INK}' stroke-width='5'/>"
                 f"<rect x='{wx + 8}' y='-180' width='16' height='22' rx='6' fill='#6fb6ff' opacity='0.7'/>")
    g.append(f"<rect x='-1460' y='-210' width='70' height='166' rx='10' fill='#e9eef5' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<line x1='-1425' y1='-206' x2='-1425' y2='-48' stroke='{INK}' stroke-width='4'/>")
    # unión entre vagones
    g.append(f"<rect x='-1640' y='-240' width='34' height='236' fill='#3a3f47' stroke='{INK}' stroke-width='6'/>")
    for wx in range(-2560, -1680, 92):
        g.append(f"<rect x='{wx}' y='-188' width='58' height='50' rx='14' fill='#2a3f5e' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def pajaro(t, rev):
    """Pajarito original que vuela junto al tren y se queda atrás en la revelación."""
    x = lerp(-80, 520, seg(t, 0, 2.6)) - 1400 * seg(t, 7.3, 8.6) ** 1.6
    y = 1170 + 22 * math.sin(t * 2.2) - 60 * seg(t, 7.3, 8.2)
    rot = -25 * seg(t, 7.3, 7.8)
    f = 24 * math.sin(t * 13)
    blink = 0.12 if (t % 2.6) < 0.12 else 1.0
    wide = 1 + 0.4 * seg(t, 7.3, 7.7)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale(1.35)'>"]
    g.append(f"<path d='M-40 0 L-78 -14 L-74 14 Z' fill='#ff8a3d' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M-20 -6 Q-30 {-50 - f:.1f} 10 {-40 - f:.1f} Q14 -18 0 -6 Z' fill='#ffb13d' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<ellipse rx='46' ry='34' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='8' cy='12' rx='26' ry='16' fill='#fff1b8'/>")
    g.append(f"<path d='M42 -6 L66 2 L42 10 Z' fill='#ff7a45' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<g transform='translate(22,-10) scale({wide:.2f},{wide * blink:.2f})'><circle r='12' fill='#fff' stroke='{INK}' stroke-width='4'/>"
             f"<circle cx='3' cy='0' r='6' fill='{INK}'/><circle cx='1' cy='-3' r='2.2' fill='#fff'/></g>")
    g.append(f"<path d='M-20 -6 Q-30 {-50 - f:.1f} 10 {-40 - f:.1f}' fill='none' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.45, 8.1)
    s = recorrido(t)
    nose_x = lerp(330, 930, seg(t, 0, 2.4)) + 40 * seg(t, 7.45, 8.0)
    lift = 58 * seg(t, 5.6, 6.9) + 6 * math.sin(t * 5) * seg(t, 6.0, 7.0)
    glow = seg(t, 5.4, 6.6) * (0.55 + 0.15 * pulso(t, 0.4)) + 0.4 * rev
    top = mix("#3f8ee8", "#2a1d6e", rev); mid = mix("#8cc8ff", "#c23fa8", rev); low = mix("#d8f1ff", "#ff9a5a", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='mag'><stop offset='0' stop-color='#e9fbff' stop-opacity='1'/>"
            "<stop offset='0.4' stop-color='#5fe0ff' stop-opacity='0.85'/><stop offset='1' stop-color='#2a7dff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='1'/><stop offset='1' stop-color='#ffffff' stop-opacity='0'/></radialGradient>")
    c = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nubes (lentas, arriba)
    for i, (cx, cy, sc, sp) in enumerate(CLOUDS):
        x = (cx - t * sp * (1 + 3 * rev) - s * 0.01) % 1500 - 250
        col = mix("#ffffff", "#ffd0e8", rev)
        c.append(f"<g transform='translate({x:.0f},{cy:.0f}) scale({sc:.2f})' opacity='0.9'>"
                 f"<path d='M0 40 Q10 -10 70 0 Q100 -45 160 -5 Q220 -20 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # montaña nevada lejana
    mx = 760 - s * 0.02
    c.append(f"<path d='M{mx-520:.0f} 1330 L{mx-90:.0f} 1030 Q{mx:.0f} 975 {mx+90:.0f} 1030 L{mx+520:.0f} 1330 Z' "
             f"fill='{mix('#6f86b8', '#5a3a8a', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    c.append(f"<path d='M{mx-90:.0f} 1030 Q{mx:.0f} 975 {mx+90:.0f} 1030 L{mx+150:.0f} 1072 L{mx+80:.0f} 1060 L{mx+30:.0f} 1088 "
             f"L{mx-30:.0f} 1058 L{mx-90:.0f} 1086 L{mx-150:.0f} 1072 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # colinas con árboles (paralaje)
    hc = mix("#7cc96a", "#4b3b8e", rev); hc2 = mix("#5fb35a", "#3d2f7a", rev)
    off = (s * 0.15) % 540
    c.append(f"<path d='M{-off:.0f} 1360 " + " ".join(f"Q{-off + 135 + 540 * k:.0f} 1270 {-off + 270 + 540 * k:.0f} 1340 T{-off + 540 * (k + 1):.0f} 1350" for k in range(4))
             + f" L1700 1920 L{-off:.0f} 1920 Z' fill='{hc}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    toff = (s * 0.35) % 300
    for k in range(6):
        tx = k * 300 - toff - 60
        c.append(f"<rect x='{tx - 9:.0f}' y='1370' width='18' height='50' fill='#8a5a3a' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse cx='{tx:.0f}' cy='1345' rx='44' ry='52' fill='{hc2}' stroke='{INK}' stroke-width='7'/>")
    c.append(f"<rect x='0' y='1440' width='{W}' height='480' fill='{mix('#9fdc7a', '#5a4a9e', rev)}'/>")
    c.append(f"<line x1='0' y1='1440' x2='{W}' y2='1440' stroke='{INK}' stroke-width='{LW}'/>")
    # pilares de la vía (se mueven con la velocidad real)
    poff = s % 380
    for k in range(5):
        px = k * 380 - poff
        c.append(f"<rect x='{px:.0f}' y='{DECK + 90}' width='70' height='{H - DECK - 60}' fill='{mix('#c9ccd3', '#8d86b8', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    # estelas de velocidad en el suelo
    vk = clamp((velocidad(t) - 700) / 2500)
    for fx, fy, fl, fw in STREAKS:
        if fy < DECK - 330 or vk < 0.02: continue
        x = (fx * 2000 - s * 1.3) % 1600 - 260
        c.append(f"<line x1='{x:.0f}' y1='{fy:.0f}' x2='{x + fl * (0.5 + vk):.0f}' y2='{fy:.0f}' stroke='#ffffff' stroke-width='{fw:.0f}' "
                 f"stroke-linecap='round' opacity='{0.55 * vk:.2f}'/>")
    # vía elevada con bobinas
    c.append(f"<rect x='-20' y='{DECK}' width='{W + 40}' height='100' fill='{mix('#dfe2e8', '#b9b3dc', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    boff = s % 120
    for k in range(11):
        bx = k * 120 - boff
        on = glow * (0.6 + 0.4 * math.sin(k * 1.7 + t * 9))
        c.append(f"<rect x='{bx:.0f}' y='{DECK + 22}' width='70' height='34' rx='8' fill='{mix('#7f8896', '#6ff0ff', on)}' stroke='{INK}' stroke-width='5'/>")
    c.append(f"<rect x='-20' y='{DECK + 74}' width='{W + 40}' height='18' fill='{mix('#b4b9c2', '#8d86b8', rev)}'/>")
    # pajarito y tren
    c.append(pajaro(t, rev))
    c.append(tren(t, nose_x, lift, rev, glow))
    # chispas mágicas bajo el tren al flotar
    if glow > 0.05:
        for fx, ph, r in SPARK:
            x = (fx * 1400 - t * (300 + 1500 * rev)) % 1300 - 120
            yy = DECK - 20 - lift * (0.2 + 0.6 * abs(math.sin(ph + t * 3)))
            c.append(f"<circle cx='{x:.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#bff6ff' opacity='{0.8 * glow:.2f}'/>")
    # líneas de velocidad en la revelación (por todo el ancho bajo los textos)
    if rev > 0:
        for fx, fy, fl, fw in STREAKS:
            if fy > DECK - 290: continue
            x = (fx * 2400 - t * 5200) % 1700 - 300
            c.append(f"<line x1='{x:.0f}' y1='{fy:.0f}' x2='{x + fl * 1.6:.0f}' y2='{fy:.0f}' stroke='#fff6c8' stroke-width='{fw:.0f}' "
                     f"stroke-linecap='round' opacity='{0.7 * rev:.2f}'/>")
    z = 1 + 0.13 * seg(t, 7.45, 10)
    cuerpo = zoom(820, 1450, z, "".join(c))
    fl = clamp(1 - abs(t - 7.5) / 0.35)
    if fl > 0:
        cuerpo += f"<circle cx='930' cy='1520' r='{lerp(200, 1300, fl):.0f}' fill='url(#flash)' opacity='{0.85 * fl:.2f}'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")
