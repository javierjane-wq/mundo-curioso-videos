"""2026-11-27-c3 · En la Luna saltarías unas 6 veces más alto que en la Tierra (gravedad ~1/6).

Un astronauta (diseño original) da saltitos en un prado de la Tierra; el cielo se vuelve negro,
el suelo gris con cráteres y aparece la Tierra en el cielo: está en la Luna. Se agacha, salta… y
sube seis veces más alto (y tarda seis veces más en caer). Revelación: destello, polvo y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.3   # el astronauta sale disparado hacia arriba en la Luna: golpe musical
MUSICA = 2

SUELO = 1700          # y de los pies
X0 = 470              # x final del astronauta
H_TIERRA = 62         # altura de un saltito en la Tierra
H_LUNA = H_TIERRA * 6 - 10   # ~6 veces más (algo menos para no tapar el cielo de arriba)
HOP = 0.47            # duración de un saltito en la Tierra
PERIODO = 0.62
T_SALTO = 6.6         # despegue en la Luna
VUELO = HOP * 6       # en la Luna está 6 veces más tiempo en el aire

rng = np.random.default_rng(23)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1420), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(90)]
CRATERS = [(150, 1790, 90), (860, 1760, 70), (640, 1880, 55), (330, 1600, 40), (980, 1880, 60), (760, 1610, 34)]
FLORES = [(110, 1760, "#ff6b8a"), (300, 1850, "#ffd23f"), (720, 1800, "#ff8c42"), (930, 1730, "#ffffff"),
          (560, 1880, "#c77dff"), (1010, 1860, "#ff6b8a"), (200, 1660, "#ffd23f")]
NUBES = [(180, 1120, 1.3), (760, 1230, 1.0), (520, 1010, 0.8)]


def salto(t):
    """Devuelve (x, altura sobre el suelo, aplastamiento, brazos 0..1)."""
    if t < 4.6:
        n = int(t // PERIODO); p = (t - n * PERIODO) / HOP
        x = lerp(140, X0, seg(t, 0, 2.4))
        if p < 1:
            h = 4 * H_TIERRA * p * (1 - p); sq = 1.0; arms = 0.35 * math.sin(math.pi * p)
        else:
            q = (p - 1) * HOP / (PERIODO - HOP); h = 0; sq = 1 - 0.1 * math.sin(math.pi * q); arms = 0
        return x, h, sq, arms
    if t < T_SALTO:
        crouch = seg(t, 6.05, 6.5) * (1 - seg(t, 6.5, T_SALTO))
        return X0, 0, 1 - 0.16 * crouch, -0.15 * crouch
    p = (t - T_SALTO) / VUELO
    if p < 1:
        h = 4 * H_LUNA * p * (1 - p)
        arms = min(1, (t - T_SALTO) / 0.4)
        return X0, h, 1.0, arms
    return X0, 0, 1.0, 0.6


def astronauta(t, x, h, sq, arms):
    blink = 0.12 if (t % 2.7) < 0.12 or 5.15 < t < 5.27 else 1.0
    look = 10 * math.sin(t * 1.3) if t < 6.6 else -8   # en el gran salto mira hacia arriba
    look_y = -10 if t >= 6.6 else 0
    ant = 9 * math.sin(t * 5)
    sc = 0.86
    y = SUELO - h
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({sc * (2 - sq):.4f},{sc * sq:.4f})'>"]
    # mochila con antena
    g.append(f"<g transform='translate(-60,-210) rotate({ant:.1f})'><line x1='0' y1='0' x2='0' y2='-95' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>"
             f"<circle cx='0' cy='-102' r='13' fill='#ff5a5f' stroke='{INK}' stroke-width='6'/></g>")
    g.append(f"<rect x='-98' y='-235' width='196' height='150' rx='26' fill='#c9ced6' stroke='{INK}' stroke-width='{LW}'/>")
    # piernas y botas
    for s in (-1, 1):
        g.append(f"<rect x='{-62 if s < 0 else 8}' y='-118' width='54' height='92' rx='20' fill='#f4f4f0' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<rect x='{-74 if s < 0 else 4}' y='-42' width='72' height='42' rx='16' fill='#7d8592' stroke='{INK}' stroke-width='{LW}'/>")
    # brazos (suben al saltar)
    for s in (-1, 1):
        ang = -s * lerp(22, 150, arms)
        g.append(f"<g transform='translate({s * 70},-200) rotate({ang:.1f})'>"
                 f"<rect x='-22' y='-8' width='44' height='108' rx='22' fill='#f4f4f0' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='0' cy='104' r='25' fill='#7d8592' stroke='{INK}' stroke-width='{LW}'/></g>")
    # cuerpo
    g.append(f"<rect x='-80' y='-232' width='160' height='130' rx='34' fill='#f4f4f0' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-42' y='-200' width='84' height='60' rx='12' fill='#ff8c42' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='-16' cy='-170' r='11' fill='#ff3d5a' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='17' cy='-170' r='11' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='-80' y='-128' width='160' height='20' rx='8' fill='#7d8592' stroke='{INK}' stroke-width='6'/>")
    # casco
    g.append(f"<circle cx='0' cy='-318' r='96' fill='#f4f4f0' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-50' y='-236' width='100' height='22' rx='10' fill='#c9ced6' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='0' cy='-312' rx='72' ry='60' fill='url(#visor)' stroke='{INK}' stroke-width='8'/>")
    for ex in (-28, 28):
        g.append(f"<ellipse cx='{ex}' cy='-314' rx='19' ry='{23 * blink:.1f}' fill='#ffffff'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look * 0.6:.1f}' cy='{-312 + look_y:.1f}' r='11' fill='{INK}'/>"
                     f"<circle cx='{ex + look * 0.6 - 4:.1f}' cy='{-317 + look_y:.1f}' r='4' fill='#fff'/>")
    mouth = "M-16 -280 Q0 -262 16 -280" if t < 6.6 else "M-18 -282 Q0 -252 18 -282 Z"
    fill = "none" if t < 6.6 else "#ff7a8a"
    g.append(f"<path d='{mouth}' fill='{fill}' stroke='#ffffff' stroke-width='6' stroke-linecap='round'/>")
    g.append("<path d='M-50 -348 Q-36 -366 -14 -366' fill='none' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g)


def tierra_globo(cx, cy, r, t):
    rot = (t * 18) % 200
    return (f"<g><circle cx='{cx}' cy='{cy}' r='{r * 1.5:.0f}' fill='url(#eglow)'/>"
            f"<clipPath id='ec'><circle cx='{cx}' cy='{cy}' r='{r:.1f}'/></clipPath>"
            f"<circle cx='{cx}' cy='{cy}' r='{r:.1f}' fill='#2f8fe8'/>"
            f"<g clip-path='url(#ec)'>"
            f"<path transform='translate({cx - r - rot + 100:.1f},{cy})' d='M0 -40 Q30 -70 70 -45 Q90 -10 60 10 Q30 30 10 5 Z M120 -60 Q160 -50 150 -10 Q140 30 110 50 Q90 10 120 -60 Z M210 -40 Q240 -70 270 -45 Q290 -10 260 10 Q230 30 210 5 Z' fill='#4cc46a' stroke='{INK}' stroke-width='5'/>"
            f"<ellipse cx='{cx - r * 0.2:.0f}' cy='{cy - r * 0.75:.0f}' rx='{r * 0.6:.0f}' ry='{r * 0.18:.0f}' fill='#ffffff' opacity='0.85'/>"
            f"<circle cx='{cx + r * 0.35:.0f}' cy='{cy + r * 0.3:.0f}' r='{r * 1.05:.0f}' fill='#0a1030' opacity='0.28'/>"
            f"</g><circle cx='{cx}' cy='{cy}' r='{r:.1f}' fill='none' stroke='{INK}' stroke-width='7'/></g>")


def frame(t):
    k = seg(t, 4.6, 5.6)            # 0 = Tierra, 1 = Luna
    flash = seg(t, 7.2, 7.5) * (1 - 0.6 * seg(t, 7.7, 9.0))
    x, h, sq, arms = salto(t)
    top = mix("#3aa0ff", "#04040e", k); mid = mix("#7cc6ff", "#0d0f26", k); low = mix("#c9ecff", "#1c1f3e", k)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='visor' cx='0.4' cy='0.35' r='0.75'><stop offset='0' stop-color='#4a6fb0'/>"
            "<stop offset='1' stop-color='#141c3a'/></radialGradient>"
            f"<radialGradient id='eglow'><stop offset='0.6' stop-color='#7fd0ff' stop-opacity='{0.35 + 0.4 * flash:.2f}'/>"
            "<stop offset='1' stop-color='#7fd0ff' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='burst'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95 * flash:.3f}'/>"
            f"<stop offset='0.35' stop-color='#ffd23f' stop-opacity='{0.6 * flash:.3f}'/>"
            "<stop offset='1' stop-color='#ff8c42' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='sun'><stop offset='0' stop-color='#fffbe8'/><stop offset='0.5' stop-color='#ffe066' stop-opacity='0.6'/>"
            "<stop offset='1' stop-color='#ffe066' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.15 * seg(t, 7.1, 8.3)
    s.append(f"<g transform='translate({X0},1330) scale({z:.4f}) translate({-X0},-1330)'>")
    # estrellas (Luna)
    for sx, sy, sr, ph in STARS:
        a = k * (0.5 + 0.5 * math.sin(t * 3.2 + ph))
        if a > 0.03:
            rr = sr * (1 + 0.6 * flash)
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{rr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # sol y nubes (Tierra)
    if k < 1:
        o = 1 - k
        s.append(f"<g opacity='{o:.2f}'><circle cx='860' cy='1080' r='150' fill='url(#sun)'/>"
                 f"<circle cx='860' cy='1080' r='62' fill='#fff3a8' stroke='#ffb347' stroke-width='8'/></g>")
        for i, (cx, cy, sc) in enumerate(NUBES):
            dx = (t * (16 + 6 * i)) % 1400 - 300
            s.append(f"<g transform='translate({(cx + dx) % 1400 - 200:.0f},{cy}) scale({sc})' opacity='{0.95 * o:.2f}'>"
                     f"<path d='M0 50 Q-10 0 45 5 Q65 -40 120 -15 Q170 -45 205 5 Q260 5 250 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # la Tierra en el cielo lunar
    if k > 0:
        r = 80 * (0.6 + 0.4 * k) * (1 + 0.08 * flash)
        s.append(f"<g opacity='{k:.2f}'>{tierra_globo(860, 1130, r, t)}</g>")
    # colinas del fondo
    c1 = mix("#7fd36b", "#8d919d", k); c2 = mix("#5fbf4f", "#aeb2bc", k); c3 = mix("#4caf3f", "#c4c7cf", k)
    s.append(f"<path d='M0 1470 Q180 1390 380 1450 T780 1420 T1080 1440 L1080 1920 L0 1920 Z' fill='{c1}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1560 Q260 1500 540 1550 T1080 1530 L1080 1920 L0 1920 Z' fill='{c2}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1660 Q300 1620 600 1660 T1080 1650 L1080 1920 L0 1920 Z' fill='{c3}' stroke='{INK}' stroke-width='{LW}'/>")
    # cráteres (Luna)
    if k > 0:
        for cx, cy, cr in CRATERS:
            s.append(f"<g opacity='{k:.2f}'><ellipse cx='{cx}' cy='{cy}' rx='{cr}' ry='{cr * 0.38:.0f}' fill='#8f939f' stroke='{INK}' stroke-width='7'/>"
                     f"<ellipse cx='{cx}' cy='{cy + cr * 0.06:.0f}' rx='{cr * 0.72:.0f}' ry='{cr * 0.24:.0f}' fill='#767a86'/></g>")
    # hierba y flores (Tierra)
    if k < 1:
        o = 1 - k
        for i in range(0, 1100, 46):
            yb = 1665 + 8 * math.sin(i * 0.05)
            sw = 6 * math.sin(t * 3 + i * 0.1)
            s.append(f"<path d='M{i} {yb:.0f} q{6 + sw:.1f} -34 {14 + sw:.1f} -40 q-2 20 6 40' fill='#3d9a32' stroke='{INK}' stroke-width='5' opacity='{o:.2f}'/>")
        for fx, fy, col in FLORES:
            bob = 4 * math.sin(t * 2.5 + fx)
            s.append(f"<g transform='translate({fx},{fy + bob:.1f})' opacity='{o:.2f}'>"
                     + "".join(f"<circle cx='{14 * math.cos(a):.1f}' cy='{14 * math.sin(a):.1f}' r='11' fill='{col}' stroke='{INK}' stroke-width='4'/>" for a in np.linspace(0, 2 * math.pi, 6)[:-1])
                     + f"<circle r='9' fill='#ffb300' stroke='{INK}' stroke-width='4'/></g>")
    # marcas de altura en la Luna: saltito de la Tierra (abajo) frente al salto lunar (arriba)
    m1 = seg(t, 6.0, 6.5); m2 = seg(t, 7.3, 7.8)
    if m1 > 0:
        y1 = SUELO - H_TIERRA * 0.86 - 5
        s.append(f"<g opacity='{m1:.2f}'><line x1='640' y1='{y1:.0f}' x2='800' y2='{y1:.0f}' stroke='#7fd0ff' stroke-width='8' stroke-dasharray='18 12' stroke-linecap='round'/>"
                 f"<circle cx='828' cy='{y1:.0f}' r='18' fill='#2f8fe8' stroke='{INK}' stroke-width='5'/>"
                 f"<path d='M818 {y1 - 6:.0f} q8 -8 16 -2 q-2 10 -12 10 z' fill='#4cc46a'/></g>")
    if m2 > 0:
        y2 = SUELO - H_LUNA * 0.86 - 5
        s.append(f"<g opacity='{m2:.2f}'><line x1='640' y1='{y2:.0f}' x2='800' y2='{y2:.0f}' stroke='#ffd23f' stroke-width='9' stroke-dasharray='18 12' stroke-linecap='round'/>"
                 f"<circle cx='828' cy='{y2:.0f}' r='18' fill='#d9dbe2' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='823' cy='{y2 - 4:.0f}' r='5' fill='#9a9ea8'/>"
                 f"<line x1='720' y1='{y1 - 14:.0f}' x2='720' y2='{y2 + 16:.0f}' stroke='#ffd23f' stroke-width='7' stroke-dasharray='4 14' stroke-linecap='round'/>"
                 f"<path d='M706 {y2 + 30:.0f} L720 {y2 + 12:.0f} L734 {y2 + 30:.0f}' fill='none' stroke='#ffd23f' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/></g>")
    # sombra
    sh = 1 / (1 + h / 160)
    s.append(f"<ellipse cx='{x:.1f}' cy='{SUELO + 8}' rx='{95 * sh:.0f}' ry='{18 * sh:.0f}' fill='#000' opacity='{0.25 * sh:.2f}'/>")
    # destello de la revelación detrás del astronauta
    if flash > 0:
        s.append(f"<circle cx='{x:.0f}' cy='{SUELO - h - 140:.0f}' r='{lerp(150, 430, seg(t, 7.2, 8.0)):.0f}' fill='url(#burst)'/>")
    # polvo: aterrizajes en la Tierra, despegue en la Luna
    if t >= T_SALTO:
        d = t - T_SALTO
        for i in range(14):
            a = math.pi * (0.05 + 0.9 * i / 13)
            rr = 40 + 260 * (1 - math.exp(-d * 1.6))
            px = x + rr * math.cos(a) * (1 if i % 2 else -1)
            py = SUELO - 20 - 60 * (1 - math.exp(-d * 1.2)) * math.sin(a) + 30 * d * d * 0.16
            op = max(0, 0.8 - d * 0.28)
            if op > 0:
                s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{14 + 6 * (i % 3)}' fill='#d9dbe2' stroke='{INK}' stroke-width='4' opacity='{op:.2f}'/>")
    elif t < 4.6:
        n = int(t // PERIODO); d = t - n * PERIODO - HOP
        if n > 0 and -0.5 < d < 0.35:
            d = (t - n * PERIODO) if t - n * PERIODO < 0.3 else None
            if d is not None:
                for sgn in (-1, 1):
                    s.append(f"<circle cx='{x + sgn * (60 + 120 * d):.0f}' cy='{SUELO - 12 - 40 * d:.0f}' r='{12 - 20 * d:.1f}' fill='#e8f5d0' opacity='{0.7 - 2 * d:.2f}'/>")
    s.append(astronauta(t, x, h, sq, arms))
    # chispas en lo alto del salto
    if t > 7.3:
        for i in range(8):
            a = i * math.pi / 4 + t * 0.8
            rr = 170 + 20 * math.sin(t * 6 + i)
            cx = x + rr * math.cos(a); cy = SUELO - h - 150 + rr * math.sin(a)
            sz = 14 * clamp((t - 7.3) / 0.4) * (0.7 + 0.3 * math.sin(t * 8 + i))
            s.append(f"<path transform='translate({cx:.0f},{cy:.0f})' d='M0 {-sz:.1f} L{sz * 0.3:.1f} {-sz * 0.3:.1f} L{sz:.1f} 0 L{sz * 0.3:.1f} {sz * 0.3:.1f} L0 {sz:.1f} L{-sz * 0.3:.1f} {sz * 0.3:.1f} L{-sz:.1f} 0 L{-sz * 0.3:.1f} {-sz * 0.3:.1f} Z' fill='#ffe066' stroke='{INK}' stroke-width='3'/>")
    s.append("</g>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
