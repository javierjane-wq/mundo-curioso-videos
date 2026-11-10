"""2026-11-10-c5 · El Sol es blanco: desde el espacio, sin atmósfera, se ve blanco.

0-2,5 s  un Sol simpático sale tras las colinas, amarillo.
2,5-5 s  día normal: nubes, pájaros, un cohete espera en su plataforma.
5-7,5 s  el cohete despega y la cámara sube con él: el cielo se oscurece y la Tierra se curva.
7,45 s   REVELACION: en el espacio negro el Sol se vuelve BLANCO con un gran halo + zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45   # el Sol se vuelve blanco en el espacio: golpe musical
MUSICA = 4

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(2.5, 6.5), rng.uniform(0, 6.28)) for _ in range(90)]
CLOUDS = [(150, 1040, 1.25, 16), (760, 930, 1.0, 11), (560, 1240, 0.85, 20), (980, 1150, 0.7, 14), (-80, 780, 0.9, 9)]
TREES = [(90, 1700, 1.0), (250, 1735, 0.8), (560, 1720, 1.1), (700, 1760, 0.75), (1010, 1735, 0.9)]

SX, SY = 420, 1320          # posición final del Sol
SR = 165                    # radio del Sol


def sun(t, cx, cy, w):
    """Sol original con cara. w: 0 = amarillo (visto desde la Tierra), 1 = blanco (espacio)."""
    r = SR
    g = []
    rot = t * 18
    ray = mix("#ff9f1c", "#dfe9ff", w)
    body = mix("#ffd23f", "#ffffff", w)
    shade = mix("#ffb627", "#e6eeff", w)
    g.append(f"<g transform='translate({cx:.1f},{cy:.1f})'>")
    # rayos (triángulos redondeados que giran y laten)
    pl = 1 + 0.06 * math.sin(t * 5)
    for i in range(12):
        a = rot + i * 30
        L = (r + 70 * pl) if i % 2 == 0 else (r + 48 * pl)
        g.append(f"<path d='M-26 {-r + 12} L0 {-L:.1f} L26 {-r + 12} Z' fill='{ray}' stroke='{INK}' stroke-width='7' "
                 f"stroke-linejoin='round' transform='rotate({a:.1f})'/>")
    # cuerpo
    g.append(f"<circle r='{r}' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M{-r*0.62:.0f} {r*0.55:.0f} A{r*0.85:.0f} {r*0.85:.0f} 0 0 0 {r*0.72:.0f} {r*0.42:.0f}' fill='none' stroke='{shade}' stroke-width='22' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='{-r*0.45:.0f}' cy='{-r*0.5:.0f}' rx='28' ry='16' fill='#fff' opacity='0.8' transform='rotate(-35 {-r*0.45:.0f} {-r*0.5:.0f})'/>")
    # mejillas
    cheek = mix("#ff7a6b", "#ffb3c0", w)
    for ex in (-92, 92):
        g.append(f"<ellipse cx='{ex}' cy='38' rx='26' ry='16' fill='{cheek}' opacity='0.75'/>")
    # ojos: parpadean; en la revelación se abren de sorpresa
    sorpresa = seg(t, 7.45, 7.75) * (1 - seg(t, 8.6, 9.1))
    blink = 0.12 if ((t % 2.9) < 0.13 and not (7.3 < t < 8.8)) else 1.0
    esc = 1 + 0.28 * sorpresa
    look = lerp(0, 10, seg(t, 4.9, 5.6)) * (1 - seg(t, 7.4, 7.9))   # mira al cohete
    for ex in (-55, 55):
        g.append(f"<g transform='translate({ex},-22) scale({esc:.3f},{esc*blink:.3f})'>"
                 f"<ellipse rx='27' ry='33' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{4 + look:.1f}' cy='4' r='15' fill='{INK}'/>"
                 f"<circle cx='{-2 + look:.1f}' cy='-4' r='6' fill='#fff'/></g>")
    # boca: sonrisa -> "¡oh!" en la revelación -> gran sonrisa
    if sorpresa > 0.5:
        g.append(f"<ellipse cx='0' cy='62' rx='{20 + 6*sorpresa:.1f}' ry='{26 + 6*sorpresa:.1f}' fill='#8a2b2b' stroke='{INK}' stroke-width='6'/>")
    else:
        big = seg(t, 8.8, 9.3)
        h = lerp(28, 46, big)
        g.append(f"<path d='M-48 46 Q0 {46 + h*1.6:.1f} 48 46 Z' fill='#8a2b2b' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<path d='M-22 {58 + h*0.55:.1f} Q0 {48 + h*0.6:.1f} 22 {58 + h*0.55:.1f}' fill='none' stroke='#ff7f8a' stroke-width='9' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def rocket(t, x, y, flame):
    """Cohete original: cuerpo blanco, punta y aletas rojas, ventanilla azul. (x, y) = base."""
    sway = 2.5 * math.sin(t * 7) if flame > 0 else 0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({sway:.1f})'>"]
    if flame > 0:
        fl = flame * (1 + 0.18 * math.sin(t * 40))
        g.append(f"<path d='M-30 0 Q-34 {60*fl:.0f} 0 {150*fl:.0f} Q34 {60*fl:.0f} 30 0 Z' fill='#ff7a2f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<path d='M-16 0 Q-18 {40*fl:.0f} 0 {95*fl:.0f} Q18 {40*fl:.0f} 16 0 Z' fill='#ffe066'/>")
    # aletas
    g.append(f"<path d='M-42 -20 L-80 12 L-80 -70 L-42 -110 Z' fill='#e63946' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M42 -20 L80 12 L80 -70 L42 -110 Z' fill='#e63946' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # tobera
    g.append(f"<path d='M-30 -14 L-36 6 L36 6 L30 -14 Z' fill='#6c757d' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cuerpo
    g.append(f"<path d='M-46 -14 L-46 -190 Q-46 -260 0 -300 Q46 -260 46 -190 L46 -14 Z' fill='#f7f7f2' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-40 -232 Q-30 -268 0 -296 Q30 -268 40 -232 Z' fill='#e63946' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<line x1='-46' y1='-60' x2='46' y2='-60' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='0' cy='-150' r='27' fill='#4cc9f0' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='-8' cy='-158' r='8' fill='#fff' opacity='0.9'/>")
    g.append(f"<path d='M28 -200 L28 -90' stroke='#d9d9cf' stroke-width='9' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def cloud(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M0 60 Q-10 10 45 14 Q60 -34 115 -14 Q150 -46 195 -6 Q250 -6 248 60 Z' fill='{col}' "
            f"stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def frame(t):
    sube = seg(t, 4.9, 7.5)               # la cámara sube con el cohete
    cam = 700 * sube                      # desplazamiento hacia abajo del paisaje
    esp = seg(t, 5.3, 7.4)                # 0 = cielo de día, 1 = espacio
    blanco = seg(t, 7.3, 7.75)            # el Sol se vuelve blanco
    top = mix("#4fb3ff", "#04061a", esp); mid = mix("#8fd6ff", "#0a0f33", esp); low = mix("#ffe8a8", mix("#1b3a8a", "#0a0f33", seg(t, 7.0, 8.5)), esp)
    sun_y = lerp(1540, SY, seg(t, 0, 2.4)) + 10 * math.sin(t * 2.2)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='{mix('#fff3b0', '#ffffff', blanco)}' stop-opacity='{lerp(0.75, 0.95, blanco):.2f}'/>"
            f"<stop offset='0.45' stop-color='{mix('#ffd166', '#dce8ff', blanco)}' stop-opacity='{lerp(0.35, 0.55, blanco):.2f}'/>"
            f"<stop offset='1' stop-color='{mix('#ffd166', '#9fbfff', blanco)}' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='atm' cx='0.5' cy='0.5' r='0.5'><stop offset='0.93' stop-color='#6fd0ff' stop-opacity='0'/>"
            "<stop offset='0.975' stop-color='#7fdcff' stop-opacity='0.85'/><stop offset='1' stop-color='#bff0ff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='flash'><stop offset='0' stop-color='#fff' stop-opacity='1'/><stop offset='0.5' stop-color='#fff' stop-opacity='0.6'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, 7.35, 10)
    c = []
    # estrellas en el espacio
    if esp > 0.4:
        a0 = seg(t, 6.2, 7.6)
        for sx, sy, sr, ph in STARS:
            a = a0 * (0.5 + 0.5 * math.sin(t * 3.3 + ph))
            if a > 0.03:
                c.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # la Tierra curvada aparece abajo
    limb = 2560 - cam * 1.2
    if limb < H + 40:
        R = 2700; ey = limb + R
        c.append(f"<circle cx='540' cy='{ey:.0f}' r='{R + 70}' fill='url(#atm)'/>")
        c.append(f"<circle cx='540' cy='{ey:.0f}' r='{R}' fill='#2f7fd8' stroke='{INK}' stroke-width='{LW}'/>")
        c.append(f"<path d='M120 {limb + 70:.0f} Q260 {limb + 20:.0f} 420 {limb + 60:.0f} Q500 {limb + 130:.0f} 360 {limb + 180:.0f} Q200 {limb + 200:.0f} 120 {limb + 70:.0f} Z' fill='#52b788' stroke='{INK}' stroke-width='6'/>")
        c.append(f"<path d='M700 {limb + 40:.0f} Q860 {limb + 30:.0f} 960 {limb + 90:.0f} Q900 {limb + 160:.0f} 760 {limb + 140:.0f} Z' fill='#52b788' stroke='{INK}' stroke-width='6'/>")
        c.append(f"<path d='M480 {limb + 150:.0f} Q560 {limb + 120:.0f} 640 {limb + 160:.0f}' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.8'/>")
    # nubes: se deslizan y, al subir, pasan hacia abajo
    ncol = mix("#ffffff", "#c9d6ff", esp)
    for i, (cx, cy, sc, sp) in enumerate(CLOUDS):
        x = (cx + t * sp + 200) % 1400 - 260
        y = cy + cam * (1.5 + 0.2 * i)
        if y < H + 100:
            c.append(cloud(x, y, sc, ncol))
    # halo y Sol (lejos: no se mueve con la cámara)
    halo_r = lerp(380, 720, blanco) * (1 + 0.04 * math.sin(t * 3))
    c.append(f"<circle cx='{SX}' cy='{sun_y:.0f}' r='{halo_r:.0f}' fill='url(#glow)'/>")
    c.append(sun(t, SX, sun_y, blanco))
    # pájaros
    if cam < 600:
        for i in range(3):
            bx = (t * 90 + 120 + i * 70) % 1300 - 100; by = 1130 + i * 34 + 8 * math.sin(t * 6 + i) + cam * 1.6
            fl = 14 * math.sin(t * 12 + i)
            c.append(f"<path d='M{bx - 26:.0f} {by - fl:.0f} Q{bx - 12:.0f} {by - 10:.0f} {bx:.0f} {by:.0f} Q{bx + 12:.0f} {by - 10:.0f} {bx + 26:.0f} {by - fl:.0f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # paisaje (baja cuando la cámara sube)
    if cam < 560:
        g = [f"<g transform='translate(0,{cam:.1f})'>"]
        g.append(f"<path d='M0 1560 Q270 1470 540 1545 T1080 1520 L1080 2700 L0 2700 Z' fill='#3fa34d' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M0 1690 Q300 1610 620 1670 T1080 1650 L1080 2700 L0 2700 Z' fill='#6cc551' stroke='{INK}' stroke-width='{LW}'/>")
        for tx, ty, ts in TREES:
            sw = 4 * math.sin(t * 2 + tx)
            g.append(f"<g transform='translate({tx},{ty}) scale({ts}) rotate({sw:.1f})'>"
                     f"<rect x='-11' y='-10' width='22' height='60' rx='6' fill='#8d5a3b' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='0' cy='-48' r='50' fill='#2d8f3c' stroke='{INK}' stroke-width='{LW}'/>"
                     f"<circle cx='-16' cy='-62' r='14' fill='#4fbf5c'/></g>")
        # flores
        for fx in (170, 420, 640, 930):
            g.append(f"<circle cx='{fx}' cy='1800' r='11' fill='#ff6b9a' stroke='{INK}' stroke-width='4'/>")
        # plataforma de lanzamiento
        g.append(f"<rect x='770' y='1648' width='180' height='26' rx='8' fill='#adb5bd' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<rect x='930' y='1380' width='22' height='270' fill='#e9c46a' stroke='{INK}' stroke-width='6'/>")
        for yy in range(1410, 1650, 50):
            g.append(f"<line x1='930' y1='{yy}' x2='952' y2='{yy + 40}' stroke='{INK}' stroke-width='4'/>")
        g.append("</g>")
        c.append("".join(g))
    # humo del despegue
    lift = seg(t, 4.8, 6.9)
    if t > 4.8:
        for k in range(9):
            pk = ((t - 4.8) * 1.2 + k * 0.11)
            if pk < 0: continue
            px = 860 + (k - 4) * 34 * (1 + pk) ; py = 1690 + cam - 10 * k
            pr = 30 + 30 * pk
            op = clamp(0.9 - pk * 0.35)
            if op > 0.02:
                c.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{pr:.0f}' fill='#f1f1f1' stroke='{INK}' stroke-width='5' opacity='{op:.2f}'/>")
    # cohete
    ry = lerp(1648, 1500, lift) + (0 if t < 7.5 else 10 * math.sin((t - 7.5) * 2.5))
    shake = 3 * math.sin(t * 60) * (seg(t, 4.5, 4.8) * (1 - seg(t, 5.2, 5.6)))
    flame = seg(t, 4.5, 4.9) * (1 - 0.5 * seg(t, 7.6, 8.4))
    c.append(rocket(t, 860 + shake, ry, flame))
    # destello de la revelación
    fl = clamp(1 - abs(t - 7.5) / 0.35)
    if fl > 0:
        c.append(f"<circle cx='{SX}' cy='{sun_y:.0f}' r='{lerp(200, 1300, seg(t, 7.3, 7.9)):.0f}' fill='url(#flash)' opacity='{0.8 * fl:.2f}'/>")
    # brillitos alrededor del Sol blanco
    if blanco > 0.5:
        for i in range(8):
            a = i * 45 + t * 25
            d = 300 + 30 * math.sin(t * 4 + i)
            px = SX + d * math.cos(math.radians(a)); py = sun_y + d * math.sin(math.radians(a))
            sc = 0.6 + 0.4 * math.sin(t * 6 + i)
            c.append(f"<path d='M{px:.0f} {py - 22*sc:.0f} L{px + 6*sc:.0f} {py:.0f} L{px:.0f} {py + 22*sc:.0f} L{px - 6*sc:.0f} {py:.0f} Z' fill='#fff' opacity='{0.9*blanco:.2f}'/>")
    s.append(zoom(SX, SY, z, "".join(c)))
    s.append("</svg>")
    return "".join(s)
