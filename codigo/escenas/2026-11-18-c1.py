"""Fuegos artificiales: sus colores salen de metales (cobre = azul, estroncio = rojo, bario = verde).

Composición: protagonista (cohete de fuegos artificiales con cara, clavado en una botella sobre la
hierba) en la mitad de abajo; arriba cielo nocturno tranquilo con luna y estrellas.
Movimiento: el cohete cae en la botella desde el fotograma 0, parpadea y mira; la mecha se enciende
y chisporrotea, el cohete tiembla y despega con estela y humo; en la REVELACION estalla en anillos
rojo, verde y azul con destello, cielo y casas iluminados, mini-estallidos laterales y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.2   # estallido de colores: golpe musical
MUSICA = 4

rng = np.random.default_rng(1118)
STARS = [(rng.uniform(0, W), rng.uniform(60, 1250), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(60)]
GRASS = [(x, rng.uniform(0, 6.28), rng.uniform(26, 46)) for x in np.linspace(10, 1070, 46)]
HOUSES = [(60, 1555, 150, 120), (215, 1585, 120, 95), (720, 1570, 135, 110), (870, 1545, 170, 135)]
WIN = [(hx + dx, hy + dy, rng.uniform(0, 6.28)) for hx, hy, hw, hh in HOUSES
       for dx, dy in ((hw * 0.25, hh * 0.35), (hw * 0.62, hh * 0.35))]

BX, BY = 540, 1270          # punto del estallido
RX, RY = 540, 1410          # centro del cuerpo del cohete en la botella
ROJO, VERDE, AZUL = "#ff3b4e", "#3ee07a", "#3fa9ff"
BOOM = REVELACION


def rocket(t):
    """Cohete original: tubo rojo con franjas crema, cono amarillo, palo de madera, mecha y cara."""
    caer = seg(t, 0, 0.9)
    y0 = lerp(-420, 0, caer)
    squash = 1 - 0.1 * math.sin(math.pi * seg(t, 0.85, 1.25))
    vuelo = seg(t, 5.0, BOOM)                  # 0 en la botella, 1 en el punto del estallido
    y = RY + y0 + (BY - RY) * vuelo
    sc = lerp(1.2, 0.3, vuelo)
    temblor = 6 * seg(t, 3.6, 5.0) * math.sin(t * 70) * (1 - vuelo)
    x = RX + temblor + 18 * math.sin(t * 9) * vuelo * (1 - vuelo) * 2
    tilt = (3 * math.sin(t * 2.2) if t < 3.6 else 0) + 4 * math.sin(t * 11) * vuelo
    blink = 0.12 if 1.6 < (t % 2.7) < 1.73 else 1.0
    look = lerp(0, -1, seg(t, 1.3, 1.8)) + lerp(0, 2, seg(t, 2.0, 2.5)) - lerp(0, 1, seg(t, 2.8, 3.2))
    asusto = seg(t, 3.0, 3.4)                  # ojos grandes cuando se enciende la mecha
    eye_r = 17 + 5 * asusto
    look_up = -6 * seg(t, 4.2, 4.8)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({sc:.3f}) rotate({tilt:.2f}) scale(1,{squash:.3f})'>"]
    # palo
    g.append(f"<rect x='-8' y='100' width='16' height='240' rx='6' fill='#d39a5a' stroke='{INK}' stroke-width='6'/>")
    # mecha (se va quemando de 3,0 a 5,0 s)
    quema = seg(t, 3.0, 5.0)
    if quema < 1:
        g.append(f"<path d='M38 108 Q78 128 70 160 Q62 188 84 205' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
        g.append(f"<path d='M38 108 Q78 128 70 160 Q62 188 84 205' fill='none' stroke='#8a5a32' stroke-width='6' stroke-linecap='round' "
                 f"stroke-dasharray='{lerp(130, 0, quema):.1f} 400'/>")
    # cuerpo
    g.append(f"<rect x='-58' y='-112' width='116' height='224' rx='16' fill='#e63946' stroke='{INK}' stroke-width='{LW}'/>")
    for sy in (-92, 62):
        g.append(f"<rect x='-58' y='{sy}' width='116' height='26' fill='#fff1d6' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='-44' y='-100' width='14' height='190' rx='7' fill='#ff7f88' opacity='0.8'/>")
    # cono
    g.append(f"<path d='M-66 -110 L0 -210 L66 -110 Z' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-30 -128 L-6 -176' stroke='#fff6c2' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<circle cx='0' cy='-214' r='12' fill='#ff7a45' stroke='{INK}' stroke-width='6'/>")
    # cara
    for ex in (-24, 24):
        g.append(f"<g transform='translate({ex + look * 4:.1f},-28) scale(1,{blink})'>"
                 f"<ellipse rx='{eye_r:.1f}' ry='{eye_r * 1.15:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{look * 3:.1f}' cy='{look_up + 2:.1f}' r='{9 - 2 * asusto:.1f}' fill='{INK}'/>"
                 f"<circle cx='{look * 3 - 3:.1f}' cy='{look_up - 2:.1f}' r='3.5' fill='#fff'/></g>")
    for ex in (-40, 40):
        g.append(f"<ellipse cx='{ex}' cy='8' rx='11' ry='6' fill='#ffb3c0' opacity='0.9'/>")
    if asusto < 0.5:
        g.append(f"<path d='M-14 18 Q0 32 14 18' fill='#a01d2b' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='26' rx='9' ry='{8 + 3 * math.sin(t * 20):.1f}' fill='#7a1020' stroke='{INK}' stroke-width='5'/>")
    # chispa de la mecha
    if 2.95 < t < 5.05:
        k = quema
        px, py = lerp(84, 40, k), lerp(205, 110, k)
        rr = 16 + 5 * math.sin(t * 40)
        rays = "".join(f"<line x1='{px:.1f}' y1='{py:.1f}' x2='{px + (rr + 14) * math.cos(a + t * 9):.1f}' "
                       f"y2='{py + (rr + 14) * math.sin(a + t * 9):.1f}' stroke='#ffe36b' stroke-width='5' stroke-linecap='round'/>"
                       for a in np.linspace(0, 2 * math.pi, 8, endpoint=False))
        g.append(rays + f"<circle cx='{px:.1f}' cy='{py:.1f}' r='{rr * 0.6:.1f}' fill='#fff7c0' stroke='#ff9f1c' stroke-width='5'/>")
    # llama del despegue
    if vuelo > 0:
        fl = 70 + 25 * math.sin(t * 45)
        g.append(f"<path d='M-40 112 Q-30 {112 + fl * 0.6:.1f} 0 {112 + fl:.1f} Q30 {112 + fl * 0.6:.1f} 40 112 Z' fill='#ffb020' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M-20 112 Q-14 {112 + fl * 0.4:.1f} 0 {112 + fl * 0.65:.1f} Q14 {112 + fl * 0.4:.1f} 20 112 Z' fill='#fff3a0'/>")
    g.append("</g>")
    return "".join(g), x, y, sc


def bottle():
    s = [f"<ellipse cx='{RX}' cy='1838' rx='110' ry='18' fill='#000' opacity='0.25'/>"]
    s.append(f"<path d='M{RX-70} 1700 Q{RX-70} 1660 {RX-30} 1650 L{RX-26} 1590 L{RX+26} 1590 L{RX+30} 1650 "
             f"Q{RX+70} 1660 {RX+70} 1700 L{RX+70} 1815 Q{RX+70} 1835 {RX+50} 1835 L{RX-50} 1835 Q{RX-70} 1835 {RX-70} 1815 Z' "
             f"fill='#3fa36f' fill-opacity='0.88' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<rect x='{RX-34}' y='1576' width='68' height='22' rx='8' fill='#5cc48d' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<path d='M{RX-46} 1690 L{RX-46} 1800' stroke='#c8f5dc' stroke-width='12' stroke-linecap='round' opacity='0.7'/>")
    s.append(f"<rect x='{RX-48}' y='1720' width='96' height='54' rx='10' fill='#fff1d6' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='{RX}' cy='1747' r='14' fill='#ff7a45' stroke='{INK}' stroke-width='4'/>")
    return "".join(s)


def burst(t, cx, cy, t0, rings, escala=1.0, cara=False):
    """Estallido: anillos de chispas con estela que se abren, caen un poco y titilan."""
    if t < t0:
        return ""
    k = 1 - (1 - clamp((t - t0) / 0.8)) ** 3
    caida = 45 * max(0.0, t - t0 - 0.6) ** 1.6 * escala
    s = []
    for j, (col, n, R) in enumerate(rings):
        R *= escala
        for i in range(n):
            a = 2 * math.pi * i / n + j * 0.21
            r1, r0 = R * k, R * k * 0.62
            dy = caida * (0.6 + 0.4 * j / max(1, len(rings) - 1))
            x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a) + dy
            x0, y0 = cx + r0 * math.cos(a), cy + r0 * math.sin(a) + dy * 0.5
            op = 0.75 + 0.25 * math.sin(t * 14 + i * 1.7 + j)
            s.append(f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{x1:.1f}' y2='{y1:.1f}' stroke='{INK}' stroke-width='{16*escala:.1f}' stroke-linecap='round' opacity='{op:.2f}'/>"
                     f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{x1:.1f}' y2='{y1:.1f}' stroke='{col}' stroke-width='{9*escala:.1f}' stroke-linecap='round' opacity='{op:.2f}'/>"
                     f"<circle cx='{x1:.1f}' cy='{y1:.1f}' r='{11*escala:.1f}' fill='{mix(col, '#ffffff', 0.45)}' stroke='{INK}' stroke-width='{4*escala:.1f}' opacity='{op:.2f}'/>")
    if cara:
        r = 46 * rebote(t, t0, 0.5)
        if r > 0:
            s.append(f"<circle cx='{cx}' cy='{cy}' r='{r*2.2:.1f}' fill='url(#core)'/>")
            s.append(f"<g transform='translate({cx},{cy}) scale({r/46:.3f})'>"
                     f"<circle r='46' fill='#fff3a0' stroke='{INK}' stroke-width='7'/>"
                     f"<path d='M-26 -6 Q-17 -18 -8 -6 M8 -6 Q17 -18 26 -6' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
                     f"<path d='M-16 10 Q0 30 16 10 Z' fill='#ff6f8e' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
                     f"<ellipse cx='-30' cy='10' rx='8' ry='5' fill='#ff9db8'/><ellipse cx='30' cy='10' rx='8' ry='5' fill='#ff9db8'/></g>")
    return "".join(s)


def frame(t):
    luz = seg(t, BOOM, BOOM + 0.4) * (1 - 0.35 * seg(t, BOOM + 0.8, 10))   # iluminación del estallido
    top = mix("#0b0d2e", "#2a1452", luz); mid = mix("#1d2163", "#4a2a86", luz); low = mix("#3a2f7e", "#8a4a9e", luz)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='#ffe9ff' stop-opacity='{0.75*luz:.3f}'/>"
            f"<stop offset='0.4' stop-color='#b06bff' stop-opacity='{0.35*luz:.3f}'/><stop offset='1' stop-color='#6b3bd0' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='core'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.9'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='moon'><stop offset='0' stop-color='#fff8d8' stop-opacity='0.5'/><stop offset='1' stop-color='#fff8d8' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    c = []
    # estrellas
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 2.6 + ph)
        c.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a * (1 - 0.5 * luz):.2f}'/>")
    # luna
    c.append("<circle cx='900' cy='300' r='150' fill='url(#moon)'/>"
             f"<circle cx='900' cy='300' r='62' fill='#fff2c4' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='880' cy='285' r='12' fill='#f0dca0'/><circle cx='922' cy='322' r='8' fill='#f0dca0'/>")
    # brillo del estallido
    if luz > 0:
        c.append(f"<circle cx='{BX}' cy='{BY}' r='{lerp(300, 820, seg(t, BOOM, BOOM + 0.6)):.0f}' fill='url(#glow)'/>")
    # colinas lejanas
    c.append(f"<path d='M0 1560 Q180 1470 380 1530 T760 1500 T1080 1520 L1080 1920 L0 1920 Z' fill='{mix('#1f2a5c', '#4a3a8a', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    # casitas con ventanas
    for hx, hy, hw, hh in HOUSES:
        c.append(f"<rect x='{hx}' y='{hy}' width='{hw}' height='{hh}' fill='{mix('#2b3570', '#5a4aa0', luz)}' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M{hx-14} {hy} L{hx + hw/2:.0f} {hy - hh*0.55:.0f} L{hx + hw + 14} {hy} Z' fill='{mix('#7a2f45', '#c04a6a', luz)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for wx, wy, ph in WIN:
        col = mix("#ffd36b", "#fff2b0", 0.5 + 0.5 * math.sin(t * 3 + ph))
        c.append(f"<rect x='{wx:.0f}' y='{wy:.0f}' width='26' height='28' rx='3' fill='{mix(col, '#ff9cf0', 0.5*luz)}' stroke='{INK}' stroke-width='5'/>")
    # colina delantera con hierba
    c.append(f"<path d='M0 1700 Q270 1640 540 1690 T1080 1680 L1080 1920 L0 1920 Z' fill='{mix('#2d6b4a', '#3f8a66', luz)}' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, ph, gl in GRASS:
        gy = 1700 - 18 * math.sin(gx / 1080 * math.pi) + (gx > 540) * 0
        sw = 7 * math.sin(t * 2.4 + ph)
        c.append(f"<path d='M{gx:.0f} {gy + 34:.0f} Q{gx + sw/2:.0f} {gy + 34 - gl/2:.0f} {gx + sw:.0f} {gy + 34 - gl:.0f}' "
                 f"stroke='{mix('#4fae72', '#6fd08f', luz)}' stroke-width='7' stroke-linecap='round' fill='none'/>")
    # estela y humo del despegue
    vuelo = seg(t, 5.0, BOOM)
    r_svg, rx, ry, rsc = rocket(t)
    if 5.0 < t < BOOM + 0.3:
        fade = 1 - seg(t, BOOM, BOOM + 0.3)
        c.append(f"<path d='M{RX} 1580 Q{RX + 20 * math.sin(t * 6):.1f} {(1580 + ry) / 2:.1f} {rx:.1f} {ry + 110 * rsc:.1f}' "
                 f"stroke='#ffe9a8' stroke-width='{lerp(14, 6, vuelo):.1f}' stroke-dasharray='18 16' stroke-dashoffset='{t * 300:.0f}' "
                 f"stroke-linecap='round' fill='none' opacity='{0.9 * fade:.2f}'/>")
    for i in range(6):
        t0 = 5.0 + i * 0.18
        if t > t0:
            k = seg(t, t0, t0 + 2.2)
            px = RX + (i - 2.5) * 34 + (i - 2.5) * 50 * k
            py = 1590 - 60 * k - 10 * i
            c.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{lerp(18, 58, k):.0f}' fill='#cbbfe6' stroke='{INK}' stroke-width='6' opacity='{0.9 * (1 - k):.2f}'/>")
    c.append(bottle())
    if t < BOOM:
        c.append(r_svg)
    # estallidos
    c.append(burst(t, BX, BY, BOOM, [(ROJO, 22, 235), (VERDE, 16, 165), (AZUL, 12, 98)], 1.0, cara=True))
    c.append(burst(t, 185, 1150, BOOM + 0.45, [(AZUL, 12, 120), (ROJO, 8, 70)], 0.75))
    c.append(burst(t, 895, 1120, BOOM + 0.75, [(VERDE, 12, 120), ("#ffd23f", 8, 70)], 0.75))
    z = 1 + 0.12 * seg(t, BOOM, 9.6)
    s.append(zoom(BX, BY, z, "".join(c)))
    # destello
    if BOOM <= t < BOOM + 0.6:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff6e8' opacity='{0.6 * (1 - seg(t, BOOM, BOOM + 0.6)):.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
