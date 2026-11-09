"""2026-11-09-c1 · En el espacio, la llama de una vela es una ESFERA azulada: sin gravedad el aire
caliente no sube (no hay convección), así que la llama no se estira hacia arriba.

0-2,5 s  una vela original con cara se enciende sobre una mesa, en una habitación de noche.
2,5-5 s  la llama normal: alargada, amarilla, parpadeando hacia arriba.
5-7,5 s  la habitación se convierte en una estación espacial: la mesa se va, la vela flota
         y la llama tiembla y se va redondeando.
7,5-10 s REVELACION: destello azul y zoom: la llama es una esfera azul con halo; la vela abre
         mucho los ojos.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 7

rng = np.random.default_rng(91)
STARS = [(rng.uniform(300, 780), rng.uniform(260, 860), rng.uniform(2.5, 5.5), rng.uniform(0, 6.28)) for _ in range(40)]
MOTAS = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.28)) for _ in range(34)]
WIN = (540, 560, 250)      # ventana redonda (centro y radio), arriba: fondo tranquilo
CX = 540                   # eje de la vela
ESC = 1.3                  # tamaño de la vela


def ventana(t, esp):
    """Ojo de buey: de noche con Luna (Tierra) -> espacio con la Tierra (estación)."""
    cx, cy, r = WIN
    g = [f"<clipPath id='vent'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath>"]
    g.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 34}' fill='{mix('#b07a4a', '#9aa6b4', esp)}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<g clip-path='url(#vent)'>")
    g.append(f"<rect x='{cx - r}' y='{cy - r}' width='{2 * r}' height='{2 * r}' fill='{mix('#1d2a5a', '#070a1c', esp)}'/>")
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 3 + ph)
        g.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # Luna (se desvanece)
    if esp < 0.99:
        g.append(f"<g opacity='{1 - esp:.2f}'><circle cx='640' cy='450' r='60' fill='#fff4c8' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='620' cy='435' r='12' fill='#e8dba8'/><circle cx='660' cy='475' r='8' fill='#e8dba8'/></g>")
        # tejados de la ciudad en la ventana
        g.append(f"<path d='M290 820 L290 740 L360 700 L430 740 L430 690 L520 690 L520 760 L600 720 L690 760 L690 700 L790 700 L790 820 Z' "
                 f"fill='#141b3a' opacity='{1 - esp:.2f}'/>")
        for wx, wy in ((330, 760), (470, 720), (740, 730), (640, 780)):
            g.append(f"<rect x='{wx}' y='{wy}' width='18' height='22' fill='#ffd36b' opacity='{(1 - esp) * (0.6 + 0.4 * math.sin(t * 2 + wx)):.2f}'/>")
    # Tierra (aparece y gira)
    if esp > 0.01:
        ey = lerp(1000, 820, esp)
        g.append(f"<g opacity='{esp:.2f}'><circle cx='540' cy='{ey:.0f}' r='300' fill='#2f7fd6' stroke='{INK}' stroke-width='{LW}'/>")
        off = (t * 30) % 600
        for i in range(3):
            x0 = 300 + i * 220 - off + 300
            g.append(f"<path d='M{x0:.0f} {ey - 200:.0f} q60 -30 110 10 q40 40 0 90 q-60 30 -110 -20 z' fill='#5cbf6a' stroke='{INK}' stroke-width='6'/>")
            g.append(f"<path d='M{x0 - 300:.0f} {ey - 200:.0f} q60 -30 110 10 q40 40 0 90 q-60 30 -110 -20 z' fill='#5cbf6a' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<circle cx='540' cy='{ey:.0f}' r='308' fill='none' stroke='#8fd3ff' stroke-width='16' opacity='0.6'/></g>")
    g.append("</g>")
    g.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # tornillos del marco
    for a in range(0, 360, 45):
        bx = cx + (r + 17) * math.cos(math.radians(a)); by = cy + (r + 17) * math.sin(math.radians(a))
        g.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='6' fill='{mix('#6e4a2a', '#5d6875', esp)}'/>")
    # reflejo
    g.append(f"<path d='M{cx - 170} {cy - 120} Q{cx - 150} {cy - 190} {cx - 80} {cy - 210}' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.35'/>")
    return "".join(g)


def fondo(t, esp):
    g = []
    pared = mix("#d98a5a", "#b9c3cf", esp)
    g.append(f"<rect width='{W}' height='{H}' fill='{pared}'/>")
    # papel pintado (habitación) -> paneles con remaches (estación)
    if esp < 0.99:
        for x in range(0, W + 1, 120):
            g.append(f"<rect x='{x}' y='0' width='50' height='{H}' fill='#e7a070' opacity='{1 - esp:.2f}'/>")
    if esp > 0.01:
        for y in (0, 1080):
            for x in range(0, W, 360):
                g.append(f"<rect x='{x + 14}' y='{y + 14}' width='332' height='{1052 if y == 0 else 900}' rx='26' fill='#c9d2dc' stroke='{INK}' stroke-width='6' opacity='{esp:.2f}'/>")
                for bx, by in ((x + 40, y + 40), (x + 320, y + 40)):
                    g.append(f"<circle cx='{bx}' cy='{by}' r='7' fill='#8793a1' opacity='{esp:.2f}'/>")
        # pasamanos amarillos y cable
        for hx in (90, 990):
            g.append(f"<rect x='{hx - 20}' y='1060' width='40' height='300' rx='20' fill='#ffcc33' stroke='{INK}' stroke-width='{LW}' opacity='{esp:.2f}'/>")
        g.append(f"<path d='M0 1000 Q270 {1060 + 20 * math.sin(t * 1.5):.0f} 540 1000 T1080 1000' fill='none' stroke='#e2533c' stroke-width='14' opacity='{esp:.2f}'/>")
    g.append(ventana(t, esp))
    # cuadro (habitación): marco con paisaje, se va
    if esp < 0.99:
        g.append(f"<g opacity='{1 - esp:.2f}'><rect x='60' y='1050' width='170' height='130' fill='#f6e3b4' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M70 1170 L120 1100 L160 1140 L190 1110 L220 1170 Z' fill='#6fb86a' stroke='{INK}' stroke-width='5'/></g>")
    # suelo
    g.append(f"<rect x='0' y='1700' width='{W}' height='220' fill='{mix('#8a5434', '#7d8896', esp)}' stroke='{INK}' stroke-width='{LW}'/>")
    if esp > 0.01:
        for x in range(0, W, 140):
            g.append(f"<rect x='{x + 10}' y='1730' width='120' height='40' rx='10' fill='#69737f' opacity='{esp:.2f}'/>")
    return "".join(g)


def mesa(t, esp):
    dy = 600 * seg(t, 5.0, 6.6)
    if dy >= 600: return ""
    y = 1560 + dy
    return (f"<g transform='translate(0,{dy:.1f})'>"
            f"<rect x='300' y='1600' width='34' height='240' fill='#7a4524' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='746' y='1600' width='34' height='240' fill='#7a4524' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='220' y='1560' width='640' height='56' rx='12' fill='#a8643a' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M250 1560 L830 1560 L800 1640 Q540 1680 280 1640 Z' fill='#f2f2f2' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M300 1600 L320 1640 M400 1610 L410 1655 M520 1612 L520 1660 M640 1610 L630 1655 M760 1600 L740 1640' stroke='#d33c3c' stroke-width='8'/>"
            "</g>")


def llama_path(r, h, k):
    """Llama: gota alargada (k=0, punta a altura h) -> esfera de radio r (k=1). Origen en el centro de la base redonda."""
    hh = lerp(h, r, k)
    c1y = lerp(-0.55 * h, -0.552 * r, k)
    c2x = lerp(0.22 * r, 0.552 * r, k); c2y = lerp(-0.8 * h, -r, k)
    return (f"M{-r:.1f} 0 A{r:.1f} {r:.1f} 0 0 0 {r:.1f} 0 "
            f"C{r:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} 0 {-hh:.1f} "
            f"C{-c2x:.1f} {c2y:.1f} {-r:.1f} {c1y:.1f} {-r:.1f} 0 Z")


def vela(t, esp, k):
    """Vela original con cara, en candelero; flota en la estación."""
    flota = seg(t, 5.2, 6.6)
    y = lerp(1560, 1640, flota) + flota * 14 * math.sin(t * 1.8)
    ang = flota * 6 * math.sin(t * 1.3)
    enc = seg(t, 0.15, 0.9)            # se enciende al principio
    blink = 0.12 if ((t + 1.2) % 2.7) < 0.13 else 1.0
    sorpresa = seg(t, 7.45, 7.9)
    g = [f"<g transform='translate({CX},{y:.1f}) rotate({ang:.2f}) scale({ESC})'>"]
    # sombra (solo sobre la mesa)
    if flota < 1:
        g.append(f"<ellipse cx='0' cy='6' rx='150' ry='16' fill='#000' opacity='{0.22 * (1 - flota):.2f}'/>")
    # candelero
    g.append(f"<ellipse cx='0' cy='-6' rx='130' ry='28' fill='#e3b341' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-90' y='-50' width='180' height='44' rx='10' fill='#f0c55a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M120 -16 Q190 -30 175 -80 Q160 -110 130 -86' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
             f"<path d='M120 -16 Q190 -30 175 -80 Q160 -110 130 -86' fill='none' stroke='#f0c55a' stroke-width='10' stroke-linecap='round'/>")
    # cuerpo de cera
    g.append(f"<path d='M-75 -50 L-75 -330 Q0 -350 75 -330 L75 -50 Z' fill='#fbe9f0' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M40 -320 L40 -100' stroke='#ffffff' stroke-width='16' stroke-linecap='round' opacity='0.7'/>")
    # gotas de cera
    g.append(f"<path d='M-75 -330 Q-40 -350 -20 -336 L-20 -290 Q-28 -270 -36 -290 L-36 -320 Q-56 -318 -60 -280 Q-68 -262 -75 -282 Z' fill='#f7d3e0' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M30 -337 Q55 -340 75 -330 L75 -300 Q66 -284 60 -302 Q58 -320 30 -330 Z' fill='#f7d3e0' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='0' cy='-336' rx='75' ry='14' fill='#f7d3e0' stroke='{INK}' stroke-width='6'/>")
    # cara
    eye_r = lerp(26, 33, sorpresa)
    look = lerp(0, -8, seg(t, 2.5, 3.2)) + lerp(0, 8, sorpresa)
    for ex in (-30, 30):
        g.append(f"<g transform='translate({ex},-220) scale(1,{blink})'><ellipse rx='{eye_r - 6:.1f}' ry='{eye_r:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='0' cy='{look:.1f}' r='{lerp(12, 14, sorpresa):.1f}' fill='{INK}'/><circle cx='-5' cy='{look - 6:.1f}' r='5' fill='#fff'/></g>")
    g.append(f"<ellipse cx='-55' cy='-180' rx='14' ry='9' fill='#ff8fa8' opacity='0.7'/><ellipse cx='55' cy='-180' rx='14' ry='9' fill='#ff8fa8' opacity='0.7'/>")
    if sorpresa < 0.5:
        g.append(f"<path d='M-22 -170 Q0 -150 22 -170' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='-160' rx='14' ry='{lerp(10, 18, sorpresa):.1f}' fill='#7a2a2a' stroke='{INK}' stroke-width='6'/>")
    # mecha
    g.append(f"<path d='M0 -340 Q4 -360 0 -378' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    # llama (contrarresta el giro para seguir apuntando arriba en la Tierra)
    if enc > 0:
        fl = 1 - k
        flick = 1 + fl * (0.06 * math.sin(t * 17) + 0.04 * math.sin(t * 29 + 1))
        sway = fl * 7 * math.sin(t * 9)
        temblor = 6 * math.sin(t * 40) * seg(t, 5.6, 6.5) * (1 - seg(t, 7.3, 7.6))
        r = lerp(30, 78, k) * enc
        h = 190 * enc * flick
        cy = lerp(-368, -400, k)
        g.append(f"<g transform='translate({sway + temblor:.1f},{cy:.1f}) rotate({-ang:.2f})'>")
        # halo
        hc = mix("#ffb347", "#5ab4ff", seg(t, 7.05, 7.5))
        g.append(f"<circle cx='0' cy='{lerp(-70, 0, k):.1f}' r='{lerp(150, 190, k) * enc:.1f}' fill='url(#halo)'/>")
        kc = seg(t, 7.05, 7.5)          # el color cambia de golpe, tapado por el destello
        out_c = mix("#ff8a1e", "#2f7fe8", kc); mid_c = mix("#ffd23f", "#6fc3ff", kc); in_c = mix("#fff6c2", "#d6f1ff", kc)
        g.append(f"<path d='{llama_path(r, h, k)}' fill='{out_c}' stroke='{mix(INK, '#1a4fa0', k)}' stroke-width='7' stroke-linejoin='round'/>")
        g.append(f"<g transform='translate(0,{lerp(4, 0, k):.1f}) scale(0.68)'><path d='{llama_path(r, h * lerp(0.92, 1, k), k)}' fill='{mid_c}'/></g>")
        g.append(f"<g transform='translate(0,{lerp(6, 0, k):.1f}) scale(0.38)'><path d='{llama_path(r, h * lerp(0.8, 1, k), k)}' fill='{in_c}'/></g>")
        # base azul (Tierra)
        if k < 0.9:
            g.append(f"<ellipse cx='0' cy='{-r * 0.2:.1f}' rx='{r * 0.55:.1f}' ry='{r * 0.35:.1f}' fill='#4aa0ff' opacity='{0.8 * (1 - k):.2f}'/>")
        if k < 0.5:
            g.append(f"<path d='M0 {r * 0.2 + 6:.1f} L0 {-r * 0.1:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round' opacity='{1 - 2 * k:.2f}'/>")
        # borde que chisporrotea en la esfera azul
        if k > 0.3:
            for i in range(14):
                a = math.radians(i * 360 / 14 + t * 60)
                rr = r * (1.02 + 0.07 * math.sin(t * 13 + i * 2.1))
                g.append(f"<circle cx='{rr * math.cos(a):.1f}' cy='{rr * math.sin(a):.1f}' r='{r * 0.13:.1f}' fill='#9ad6ff' opacity='{0.55 * kc:.2f}'/>")
        g.append("</g>")
    g.append("</g>")
    return "".join(g), y


def frame(t):
    esp = seg(t, 4.9, 6.6)                 # habitación -> estación espacial
    k = seg(t, 6.0, 7.6)                   # llama alargada -> esfera
    rev = seg(t, 7.45, 8.0)
    flash = clamp(1 - abs(t - 7.5) / 0.35)
    k = seg(t, 6.0, 7.6); kc = seg(t, 7.05, 7.5)
    hc = mix("#ffb347", "#5ab4ff", kc)
    defs = (f"<radialGradient id='halo'><stop offset='0' stop-color='{mix('#fff1c2', '#e2f4ff', kc)}' stop-opacity='{lerp(0.75, 0.95, rev):.2f}'/>"
            f"<stop offset='0.5' stop-color='{hc}' stop-opacity='{lerp(0.35, 0.55, rev):.2f}'/><stop offset='1' stop-color='{hc}' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='luz' cx='0.5' cy='0.62' r='0.6'><stop offset='0' stop-color='#9fd8ff' stop-opacity='0'/>"
            f"<stop offset='1' stop-color='#0b1e4a' stop-opacity='0.55'/></radialGradient>")
    s = [fondo(t, esp), mesa(t, esp)]
    v, vy = vela(t, esp, k)
    s.append(v)
    # motas de polvo que flotan (más en la estación)
    for px, py, pr, sp, ph in MOTAS:
        yy = (py - t * sp) % 900 + 1000
        s.append(f"<circle cx='{px + 25 * math.sin(t * 0.8 + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fff' opacity='{0.25 + 0.3 * esp:.2f}'/>")
    # objeto flotando en la estación: un tornillo y un lápiz
    if esp > 0.05:
        bx = lerp(-80, 260, seg(t, 5.4, 10)); by = 1250 + 30 * math.sin(t * 1.4)
        s.append(f"<g transform='translate({bx:.0f},{by:.0f}) rotate({t * 40:.0f})' opacity='{esp:.2f}'>"
                 f"<rect x='-60' y='-10' width='120' height='20' rx='4' fill='#ffcf3a' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M60 -10 L88 0 L60 10 Z' fill='#f4d2a8' stroke='{INK}' stroke-width='5'/><rect x='-72' y='-10' width='14' height='20' fill='#ff8fa8' stroke='{INK}' stroke-width='5'/></g>")
        ox = lerp(1160, 820, seg(t, 5.6, 10)); oy = 1180 + 25 * math.sin(t * 1.1 + 2)
        s.append(f"<g transform='translate({ox:.0f},{oy:.0f}) rotate({-t * 55:.0f})' opacity='{esp:.2f}'>"
                 f"<polygon points='-28,-16 0,-32 28,-16 28,16 0,32 -28,16' fill='#aab4c0' stroke='{INK}' stroke-width='6'/><circle r='10' fill='#6c7683' stroke='{INK}' stroke-width='4'/></g>")
    # tinte azul en la revelación + destellos alrededor de la esfera
    s.append(f"<rect width='{W}' height='{H}' fill='url(#luz)' opacity='{rev:.2f}'/>")
    fx, fy = CX, vy - 400 * ESC
    if rev > 0:
        for i in range(10):
            a = i * 36 + t * 30
            d = lerp(140, 185, (math.sin(t * 4 + i) + 1) / 2)
            x = fx + d * math.cos(math.radians(a)); y = fy + d * math.sin(math.radians(a))
            s.append(f"<path d='M{x:.0f} {y - 14:.0f} L{x + 4:.0f} {y - 4:.0f} L{x + 14:.0f} {y:.0f} L{x + 4:.0f} {y + 4:.0f} L{x:.0f} {y + 14:.0f} "
                     f"L{x - 4:.0f} {y + 4:.0f} L{x - 14:.0f} {y:.0f} L{x - 4:.0f} {y - 4:.0f} Z' fill='#e6f6ff' opacity='{rev * 0.9:.2f}'/>")
    z = 1 + 0.28 * seg(t, 7.4, 9.6)
    cuerpo = zoom(CX, 1115, z, "".join(s))
    if flash > 0:
        cuerpo += f"<rect width='{W}' height='{H}' fill='#d8f0ff' opacity='{0.6 * flash:.2f}'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")
