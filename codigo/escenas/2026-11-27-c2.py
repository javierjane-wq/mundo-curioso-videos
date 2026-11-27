"""El cactus saguaro se hincha como un acordeón cuando llueve.

0-2,5 s: desierto al sol, el saguaro (delgado, sediento) entra con un rebote y una planta rodadora cruza.
2,5-5 s: calor: ondas de calor, el Sol aprieta, el cactus se encoge un poco.
5-7 s: llegan las nubes y empieza a llover; el cactus abre la boca y bebe.
7-8 s (REVELACION): sus pliegues se abren, engorda, se vuelve verde intenso, destello y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, pulso, zoom

DUR = 10.0
REVELACION = 7.1   # el cactus se hincha: golpe musical
MUSICA = 5

rng = np.random.default_rng(42)
RAIN = [(rng.uniform(-100, W + 100), rng.uniform(0, 1), rng.uniform(0.55, 0.85), rng.uniform(26, 44)) for _ in range(110)]
PEBBLES = [(110, 1800, 22), (300, 1870, 16), (860, 1835, 26), (990, 1760, 14), (700, 1890, 18)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(260, 470), rng.uniform(6, 13)) for _ in range(22)]

BASE_Y = 1760   # pie del cactus
CX = 540


def tubo(d, ancho, color, sombra=None):
    """Tubo con contorno grueso a partir de un trazo (punta redondeada)."""
    s = (f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{ancho + 2 * LW:.1f}' stroke-linecap='round' stroke-linejoin='round'/>"
         f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{ancho:.1f}' stroke-linecap='round' stroke-linejoin='round'/>")
    if sombra:
        s += f"<path d='{d}' fill='none' stroke='{sombra}' stroke-width='{ancho * 0.22:.1f}' stroke-linecap='round' stroke-linejoin='round' opacity='0.8'/>"
    return s


def saguaro(t):
    hin = seg(t, 7.0, 7.9)                      # hinchado
    seco = seg(t, 2.5, 4.8) * (1 - seg(t, 5.6, 6.8))
    w = lerp(150, 236, hin) * (1 - 0.06 * seco)  # ancho del tronco
    aw = w * 0.62                                # ancho de los brazos
    col = mix(mix("#7da24a", "#93a25a", seco), "#2fb24a", hin)
    dark = mix(mix("#557a2e", "#6b7a3a", seco), "#17853a", hin)
    light = mix("#a9c86c", "#7fe07a", hin)
    sway = 2.2 * math.sin(t * 2.1) * (1 - hin * 0.6)
    sc = 0.88 + 0.12 * min(1, rebote(t + 0.05, 0, 0.9)) if t < 1.0 else 1.0
    wob = 1 + 0.05 * math.sin(clamp((t - 7.0) / 0.9) * math.pi * 3) * (1 - seg(t, 7.9, 8.6))
    top = 1060
    g = [f"<g transform='translate({CX},{BASE_Y}) rotate({sway:.2f}) scale({sc * wob:.4f},{sc:.4f}) translate({-CX},{-BASE_Y})'>"]
    # sombra en el suelo
    g.append(f"<ellipse cx='{CX}' cy='{BASE_Y + 8}' rx='{w * 1.5:.0f}' ry='26' fill='#000' opacity='0.18'/>")
    # brazos (izquierdo más bajo, derecho más alto)
    off = w / 2 - 8
    la = f"M{CX - off:.0f} 1430 L{CX - off - 120 - aw * 0.3:.0f} 1430 Q{CX - off - 150 - aw * 0.3:.0f} 1430 {CX - off - 150 - aw * 0.3:.0f} 1390 L{CX - off - 150 - aw * 0.3:.0f} 1230"
    ra = f"M{CX + off:.0f} 1330 L{CX + off + 110 + aw * 0.3:.0f} 1330 Q{CX + off + 140 + aw * 0.3:.0f} 1330 {CX + off + 140 + aw * 0.3:.0f} 1290 L{CX + off + 140 + aw * 0.3:.0f} 1150"
    g.append(tubo(la, aw, col, dark))
    g.append(tubo(ra, aw, col, dark))
    # espinas de los brazos
    for x0, y0, y1 in ((CX - off - 150 - aw * 0.3, 1390, 1240), (CX + off + 140 + aw * 0.3, 1290, 1160)):
        for yy in range(int(y1), int(y0), 34):
            for sx in (-aw * 0.32, aw * 0.32):
                g.append(f"<circle cx='{x0 + sx:.0f}' cy='{yy}' r='4' fill='#fff6d0'/>")
    # tronco
    r = w / 2
    g.append(f"<path d='M{CX - r:.1f} {BASE_Y + 20} L{CX - r:.1f} {top + r:.1f} A{r:.1f} {r:.1f} 0 0 1 {CX + r:.1f} {top + r:.1f} L{CX + r:.1f} {BASE_Y + 20} Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # pliegues (costillas): se separan al hincharse
    n = 5
    for k in range(n):
        f = (k - (n - 1) / 2) / ((n - 1) / 2)          # -1..1
        x = CX + f * (w / 2) * lerp(0.62, 0.78, hin)
        ytop = top + w / 2 - math.sqrt(max(0, 1 - f * f * 0.5)) * w * 0.38
        g.append(f"<path d='M{x:.1f} {BASE_Y + 10} L{x:.1f} {ytop:.0f}' stroke='{dark}' stroke-width='{lerp(7, 5, hin):.1f}' stroke-linecap='round'/>")
        if k < n - 1:
            xm = CX + (f + 1 / ((n - 1) / 2) * 0.5) * (w / 2) * lerp(0.62, 0.78, hin)
            g.append(f"<path d='M{xm:.1f} {BASE_Y + 10} L{xm:.1f} {top + w * 0.35:.0f}' stroke='{light}' stroke-width='{lerp(6, 12, hin):.1f}' stroke-linecap='round' opacity='0.55'/>")
        for yy in range(int(top + w * 0.5), BASE_Y - 20, 40):
            if 1180 < yy < 1330 and abs(f) < 0.8:
                continue   # sin espinas sobre la cara
            g.append(f"<circle cx='{x:.1f}' cy='{yy + (k % 2) * 20}' r='4.5' fill='#fff6d0' stroke='{INK}' stroke-width='1.5'/>")
    # flores blancas en la punta al hincharse
    fl = rebote(t, 7.6, 0.6)
    if fl > 0:
        for dx, dy, r in ((-36, top + 12, 26), (8, top - 4, 30), (44, top + 18, 24)):
            g.append(f"<g transform='translate({CX + dx},{dy}) scale({fl:.3f})'>"
                     + "".join(f"<ellipse cx='0' cy='{-r * 0.55:.0f}' rx='{r * 0.42:.0f}' ry='{r * 0.62:.0f}' fill='#fffdf4' stroke='{INK}' stroke-width='4' transform='rotate({a})'/>" for a in range(0, 360, 60))
                     + f"<circle r='{r * 0.34:.0f}' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")
    # cara
    blink = 0.12 if ((t + 1.0) % 2.7) < 0.12 or 6.95 < t < 7.05 else 1.0
    ey = 1235
    eye_r = lerp(25, 30, hin)
    for ex in (-38, 38):
        exx = CX + ex * lerp(1, 1.35, hin)
        g.append(f"<ellipse cx='{exx:.0f}' cy='{ey}' rx='{eye_r:.0f}' ry='{eye_r * 1.15 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            look_y = lerp(0, -10, seg(t, 5.0, 5.6)) * (1 - seg(t, 7.0, 7.4))
            g.append(f"<circle cx='{exx + 3:.0f}' cy='{ey + 4 + look_y:.0f}' r='{eye_r * 0.52:.0f}' fill='{INK}'/>"
                     f"<circle cx='{exx - 4:.0f}' cy='{ey - 4 + look_y:.0f}' r='{eye_r * 0.2:.0f}' fill='#fff'/>")
    # cejas: preocupadas con el calor
    bw = seco * 10
    for s_ in (-1, 1):
        exx = CX + s_ * 38 * lerp(1, 1.35, hin)
        g.append(f"<path d='M{exx - 22 * s_:.0f} {ey - 44 + bw * 0.2:.0f} L{exx + 16 * s_:.0f} {ey - 44 - bw:.0f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # mejillas
    g.append(f"<ellipse cx='{CX - 62 * lerp(1, 1.35, hin):.0f}' cy='{ey + 40}' rx='18' ry='10' fill='#ff7aa0' opacity='{lerp(0.35, 0.8, hin):.2f}'/>")
    g.append(f"<ellipse cx='{CX + 62 * lerp(1, 1.35, hin):.0f}' cy='{ey + 40}' rx='18' ry='10' fill='#ff7aa0' opacity='{lerp(0.35, 0.8, hin):.2f}'/>")
    # boca: sedienta (lengua fuera) -> bebe (abierta hacia arriba) -> sonrisa grande
    my = ey + 62
    beber = seg(t, 5.3, 5.8) * (1 - seg(t, 7.0, 7.3))
    if hin > 0.3:
        g.append(f"<path d='M{CX - 46} {my - 6} Q{CX} {my + 52} {CX + 46} {my - 6} Z' fill='#7a2230' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M{CX - 22} {my + 22} Q{CX} {my + 8} {CX + 22} {my + 22} Q{CX} {my + 40} {CX - 22} {my + 22}' fill='#ff6f86'/>")
    elif beber > 0.2:
        rr = 20 + 4 * math.sin(t * 12)
        g.append(f"<ellipse cx='{CX}' cy='{my + 6}' rx='{rr:.0f}' ry='{rr * 1.1:.0f}' fill='#7a2230' stroke='{INK}' stroke-width='6'/>")
    else:
        tg = 0.4 + 0.6 * seco
        g.append(f"<path d='M{CX - 28} {my + 10} Q{CX} {my - 4} {CX + 28} {my + 10}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
        if tg > 0.5:
            g.append(f"<path d='M{CX - 4} {my + 4} Q{CX - 2} {my + 32 * tg} {CX + 14} {my + 30 * tg} Q{CX + 22} {my + 14} {CX + 14} {my + 4}' fill='#ff6f86' stroke='{INK}' stroke-width='5'/>")
    # gota de sudor con el calor
    if 2.8 < t < 5.4:
        k = ((t - 2.8) % 1.3) / 1.3
        g.append(f"<path d='M{CX + 78} {1180 + k * 60:.0f} q-12 22 0 30 q12 -8 0 -30 Z' fill='#9fdcff' stroke='{INK}' stroke-width='4' opacity='{1 - k * 0.6:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def rodadora(t):
    """Planta rodadora que cruza el desierto."""
    x = lerp(-140, 1240, clamp(t / 4.6))
    if x > 1220:
        return ""
    y = 1690 - abs(math.sin(t * 4.2)) * 60
    rot = t * 400
    s = [f"<g transform='translate({x:.0f},{y:.0f}) rotate({rot:.0f})'>"]
    s.append(f"<circle r='58' fill='#c9a46a' stroke='{INK}' stroke-width='7' opacity='0.95'/>")
    for a in range(0, 360, 30):
        s.append(f"<path d='M0 0 Q{30 * math.cos(math.radians(a + 40)):.0f} {30 * math.sin(math.radians(a + 40)):.0f} {54 * math.cos(math.radians(a)):.0f} {54 * math.sin(math.radians(a)):.0f}' fill='none' stroke='#8a6a3a' stroke-width='5'/>")
    s.append("</g>")
    return "".join(s)


def frame(t):
    nub = seg(t, 4.6, 5.8) * (1 - 0.5 * seg(t, 8.6, 10))   # nubes de tormenta
    lluvia = seg(t, 5.2, 5.6) * (1 - 0.7 * seg(t, 7.8, 9.0))
    hin = seg(t, 7.0, 7.9)
    calor = seg(t, 1.5, 3.5) * (1 - nub)
    top = mix(mix("#3a9be0", "#ffb14e", calor * 0.35), "#5a6a8a", nub)
    mid = mix(mix("#8fd0f4", "#ffd27a", calor * 0.5), "#8a96a8", nub)
    low = mix(mix("#ffe3a6", "#ffc06a", calor * 0.6), "#c0b49a", nub)
    s = ["<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='sun'><stop offset='0' stop-color='#fff6c0' stop-opacity='{0.9 * (1 - nub):.2f}'/><stop offset='1' stop-color='#ffb040' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#eaffd8' stop-opacity='{0.85 * hin * (1 - 0.5 * seg(t, 8.2, 10)):.2f}'/><stop offset='0.5' stop-color='#9dff8a' stop-opacity='{0.45 * hin:.2f}'/><stop offset='1' stop-color='#4fd06a' stop-opacity='0'/></radialGradient>",
         "</defs>"]
    defs = "".join(s)
    b = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # Sol
    sx, sy = 820, 1000
    b.append(f"<circle cx='{sx}' cy='{sy}' r='{230 + 15 * pulso(t, 1.6):.0f}' fill='url(#sun)'/>")
    b.append(f"<g opacity='{1 - nub:.2f}'><circle cx='{sx}' cy='{sy}' r='{lerp(78, 92, calor):.0f}' fill='#ffe46b' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(10):
        a = math.radians(i * 36 + t * 20)
        b.append(f"<line x1='{sx + 110 * math.cos(a):.0f}' y1='{sy + 110 * math.sin(a):.0f}' x2='{sx + 150 * math.cos(a):.0f}' y2='{sy + 150 * math.sin(a):.0f}' stroke='#ffd23f' stroke-width='12' stroke-linecap='round'/>")
    b.append("</g>")
    # mesetas lejanas
    mes = mix("#d9875a", "#8a7a78", nub)
    b.append(f"<path d='M0 1330 L70 1330 L100 1250 L300 1250 L330 1330 L700 1330 L730 1270 L860 1270 L890 1330 L1080 1330 L1080 1500 L0 1500 Z' fill='{mes}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # nubes de lluvia
    if nub > 0.01:
        for i, (cx, cy, sc) in enumerate(((180, 900, 1.5), (620, 860, 1.8), (980, 930, 1.3))):
            dx = lerp(-700 if i % 2 == 0 else 700, 0, nub) + 12 * math.sin(t * 0.8 + i)
            col = mix("#b8c0cc", "#7c8798", 0.6)
            b.append(f"<g transform='translate({cx + dx:.0f},{cy}) scale({sc})'>"
                     f"<path d='M-120 40 Q-130 -10 -80 -14 Q-70 -60 -20 -54 Q10 -90 60 -60 Q110 -66 115 -20 Q150 -10 135 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # suelo (dunas)
    d1 = mix("#f0b86a", "#c9a070", nub); d2 = mix("#e8a456", "#b98e5e", nub)
    b.append(f"<path d='M0 1470 Q270 1420 540 1460 T1080 1450 L1080 1920 L0 1920 Z' fill='{d1}' stroke='{INK}' stroke-width='{LW}'/>")
    # cactus pequeños de fondo
    for x0, h0 in ((150, 120), (930, 95)):
        b.append(tubo(f"M{x0} 1500 L{x0} {1500 - h0}", 34, mix("#6e9a48", "#3aa24a", hin)))
    # charcos
    ch = seg(t, 5.8, 7.2)
    if ch > 0:
        for px, py, pr in ((280, 1790, 110), (820, 1800, 90)):
            b.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr * ch:.0f}' ry='{pr * 0.22 * ch:.0f}' fill='#7cc6f0' stroke='{INK}' stroke-width='6'/>")
    # ondas de calor
    if calor * (1 - nub) > 0.05:
        a = calor * (1 - nub)
        for i in range(4):
            yy = 1600 - ((t * 80 + i * 70) % 280)
            b.append(f"<path d='M{180 + i * 220} {yy:.0f} q20 -20 0 -40 q-20 -20 0 -40' fill='none' stroke='#fff3d0' stroke-width='6' stroke-linecap='round' opacity='{0.6 * a:.2f}'/>")
    b.append(rodadora(t))
    # halo detrás del cactus en la revelación
    if hin > 0:
        b.append(f"<circle cx='{CX}' cy='1380' r='{lerp(200, 560, hin):.0f}' fill='url(#halo)'/>")
    b.append(saguaro(t))
    # montículo de arena delante del pie
    b.append(f"<path d='M{CX - 260} 1790 Q{CX} 1700 {CX + 260} 1790 Z' fill='{d2}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for px, py, pr in PEBBLES:
        b.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr}' ry='{pr * 0.6:.0f}' fill='{mix('#b0784a', '#8a6a52', nub)}' stroke='{INK}' stroke-width='6'/>")
    # lluvia
    if lluvia > 0.01:
        for x0, ph, sp, ln in RAIN:
            k = ((t * sp * 1.6) + ph) % 1
            y = lerp(1000, 1940, k)
            x = x0 - k * 60
            b.append(f"<line x1='{x:.0f}' y1='{y:.0f}' x2='{x - 8:.0f}' y2='{y + ln:.0f}' stroke='#d8f0ff' stroke-width='6' stroke-linecap='round' opacity='{0.85 * lluvia:.2f}'/>")
        # salpicaduras en los charcos
        for i in range(6):
            k = ((t * 2.2) + i * 0.17) % 1
            px = (280, 820)[i % 2] + (i * 37 % 120) - 60
            b.append(f"<ellipse cx='{px}' cy='{1790 + (i % 2) * 10}' rx='{8 + 26 * k:.0f}' ry='{3 + 7 * k:.0f}' fill='none' stroke='#eaf8ff' stroke-width='4' opacity='{lluvia * (1 - k):.2f}'/>")
    # chispas de la revelación
    if hin > 0:
        for a0, r0, sz in SPARK:
            rr = r0 * lerp(0.6, 1.1, seg(t, 7.0, 8.4))
            a = a0 + t * 0.6
            op = hin * (0.5 + 0.5 * math.sin(t * 6 + a0 * 3)) * (1 - 0.4 * seg(t, 8.6, 10))
            x = CX + rr * math.cos(a); y = 1380 + rr * 1.3 * math.sin(a)
            b.append(f"<path d='M{x:.0f} {y - sz * 2:.0f} L{x + sz * 0.5:.0f} {y - sz * 0.5:.0f} L{x + sz * 2:.0f} {y:.0f} L{x + sz * 0.5:.0f} {y + sz * 0.5:.0f} L{x:.0f} {y + sz * 2:.0f} L{x - sz * 0.5:.0f} {y + sz * 0.5:.0f} L{x - sz * 2:.0f} {y:.0f} L{x - sz * 0.5:.0f} {y - sz * 0.5:.0f} Z' fill='#fffbd0' opacity='{op:.2f}'/>")
    z = 1 + 0.13 * seg(t, 6.9, 8.0) + 0.02 * seg(t, 8.0, 10)
    cuerpo = zoom(CX, 1400, z, "".join(b))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"{defs}{cuerpo}</svg>")
