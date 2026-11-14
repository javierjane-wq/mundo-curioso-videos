"""2026-11-14-c2 · El plástico de burbujas se inventó (1957, Fielding y Chavannes) como papel pintado con relieve.

Salón: un rollo de plástico de burbujas con cara entra saltando. Junto a él, una caja de cartón
con un jarrón que el plástico envuelve (su uso de hoy). Tensión: la lámina se suelta del jarrón y
sube flotando hacia la pared. Revelación: destello y la pared se cubre de papel pintado de burbujas
de colores (su idea original); el rollo salta de alegría; zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 5

rng = np.random.default_rng(57)
MOTES = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(3, 7), rng.uniform(15, 40), rng.uniform(0, 6.28)) for _ in range(34)]
SPARK = [(rng.uniform(40, 1040), rng.uniform(1060, 1520), rng.uniform(0, 1.6), rng.uniform(10, 18)) for _ in range(22)]
FLOOR = 1580
BAND_TOP, BAND_BOT = 1040, 1540
PASTEL = ["#9fdcff", "#ffb8d9", "#bff0a8", "#ffe58a", "#d6c2ff"]


def burbuja(x, y, r, fill="#e4f7ff", sw=4, edge="#6fa9c4"):
    return (f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='{fill}' stroke='{edge}' stroke-width='{sw}'/>"
            f"<ellipse cx='{x - r*0.32:.1f}' cy='{y - r*0.34:.1f}' rx='{r*0.32:.1f}' ry='{r*0.2:.1f}' fill='#fff' opacity='0.95' transform='rotate(-30 {x - r*0.32:.1f} {y - r*0.34:.1f})'/>")


def lamina(w, h, r=15, paso=40, fill="#d3f0fb"):
    """Lámina de plástico de burbujas (origen arriba a la izquierda)."""
    g = [f"<rect x='0' y='0' width='{w}' height='{h}' rx='10' fill='{fill}' opacity='0.92' stroke='{INK}' stroke-width='6'/>"]
    fila = 0
    yy = paso * 0.6
    while yy < h - r * 0.6:
        xx = paso * 0.6 + (paso / 2 if fila % 2 else 0)
        while xx < w - r * 0.6:
            g.append(burbuja(xx, yy, r, sw=3))
            xx += paso
        yy += paso * 0.88; fila += 1
    return "".join(g)


def rollo(t):
    """Rollo de plástico de burbujas de pie, con cara."""
    x = lerp(1010, 700, seg(t, 0, 2.1))
    hop = abs(math.sin(t * math.pi * 2.6)) * 70 * (1 - seg(t, 1.6, 2.1))
    sway = 3 * pulso(t, 1.6)
    if t > 5.0 and t < REVELACION:      # tiembla de emoción mirando la pared
        sway += 2.5 * math.sin(t * 40) * seg(t, 5.2, 6.0)
    jump = 0.0
    if t >= REVELACION:
        k = (t - REVELACION) % 0.9
        jump = 90 * math.sin(math.pi * clamp(k / 0.55)) if t < 9.6 else 0
    sq = 1 + 0.05 * pulso(t, 0.9)
    y = FLOOR + 20 - hop - jump
    look = lerp(0, -16, seg(t, 4.9, 5.6))            # mira a la izquierda/arriba
    look_y = lerp(0, -10, seg(t, 4.9, 5.6))
    blink = 0.12 if ((t + 1.3) % 2.9) < 0.12 else 1.0
    happy = seg(t, REVELACION, REVELACION + 0.3)
    g = [f"<ellipse cx='{x:.1f}' cy='{FLOOR + 22}' rx='{150 - 0.4*(hop + jump):.0f}' ry='24' fill='#000' opacity='0.2'/>"]
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({sway:.2f}) scale({1.14/sq:.3f},{1.14*sq:.3f})'>")
    # extremo suelto de la lámina en el suelo
    g.append(f"<g transform='translate(110,-70) rotate(8)'>{lamina(150, 70, r=12, paso=32)}</g>")
    # cuerpo cilíndrico
    g.append(f"<path d='M-135 -370 L-135 -10 Q0 40 135 -10 L135 -370 Z' fill='#bfe8f8' stroke='{INK}' stroke-width='{LW}'/>")
    # capas del rollo (líneas horizontales)
    for ly in (-280, -190, -100):
        g.append(f"<path d='M-135 {ly} Q0 {ly + 34} 135 {ly}' fill='none' stroke='#7fb8d0' stroke-width='5'/>")
    # burbujas en el cuerpo (evitan la cara)
    for row, by in enumerate(range(-336, -20, 56)):
        off = 28 if row % 2 else 0
        for bx in range(-108 + off, 120, 56):
            if -95 < bx < 95 and -300 < by < -130:
                continue
            g.append(burbuja(bx, by + 0.12 * abs(bx) * 0.3, 20, sw=4))
    # tapa superior con espiral
    g.append(f"<ellipse cx='0' cy='-370' rx='135' ry='42' fill='#d9f4ff' stroke='{INK}' stroke-width='{LW}'/>")
    for rr in (105, 78, 54):
        g.append(f"<ellipse cx='0' cy='-370' rx='{rr}' ry='{rr*0.31:.1f}' fill='none' stroke='#7fb8d0' stroke-width='5'/>")
    g.append(f"<ellipse cx='0' cy='-370' rx='34' ry='11' fill='#b07a45' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='0' cy='-368' rx='20' ry='6' fill='#5a3a20'/>")
    # cara
    for ex in (-46, 46):
        er = 36 + 6 * happy
        g.append(f"<ellipse cx='{ex}' cy='-225' rx='{er:.1f}' ry='{er*1.12*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look*0.8:.1f}' cy='{-220 + look_y:.1f}' r='{19 + 3*happy:.1f}' fill='{INK}'/>"
                     f"<circle cx='{ex + look*0.8 - 7:.1f}' cy='{-228 + look_y:.1f}' r='7' fill='#fff'/>")
    for cx in (-86, 86):
        g.append(f"<ellipse cx='{cx}' cy='-172' rx='20' ry='12' fill='#ff8fb1' opacity='0.8'/>")
    mo = lerp(14, 40, happy)
    g.append(f"<path d='M-34 -170 Q0 {-170 + mo:.1f} 34 -170 Z' fill='#c2384f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # bracitos
    wave = 18 * pulso(t, 0.7) if t >= REVELACION else 6 * pulso(t, 1.4)
    ar = lerp(10, -60, happy)
    for side in (-1, 1):
        ang = side * (ar + wave * side)
        g.append(f"<g transform='translate({side*132},-180) rotate({ang:.1f})'>"
                 f"<path d='M0 0 Q{side*50} 30 {side*70} 80' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
                 f"<path d='M0 0 Q{side*50} 30 {side*70} 80' fill='none' stroke='#bfe8f8' stroke-width='11' stroke-linecap='round'/></g>")
    g.append("</g>")
    return "".join(g)


def caja(t):
    """Caja de cartón con un jarrón dentro; la lámina lo envuelve y luego se va."""
    wig = 4 * math.sin(t * 30) * (seg(t, 4.6, 4.75) - seg(t, 5.0, 5.2))
    g = [f"<g transform='translate(300,{FLOOR}) rotate({wig:.2f})'>"]
    g.append(f"<ellipse cx='0' cy='20' rx='190' ry='22' fill='#000' opacity='0.2'/>")
    # jarrón
    g.append(f"<path d='M-55 -150 Q-110 -230 -60 -320 L-40 -370 L40 -370 L60 -320 Q110 -230 55 -150 Z' fill='#3f7fd8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-52' y='-392' width='104' height='28' rx='10' fill='#3f7fd8' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-70 -270 Q0 -245 70 -270' fill='none' stroke='#ffd23f' stroke-width='12'/>")
    g.append(f"<path d='M-40 -330 Q-62 -280 -46 -230' fill='none' stroke='#9cc6ff' stroke-width='9' stroke-linecap='round'/>")
    # flores en el jarrón
    for i, (fx, fy, col) in enumerate(((-40, -470, "#ff6f91"), (10, -500, "#ffd23f"), (55, -455, "#ff8a3d"))):
        sw = 5 * pulso(t, 2.0, i * 0.3)
        g.append(f"<g transform='rotate({sw:.1f} 0 -380)'><path d='M0 -380 Q{fx*0.4:.0f} {fy+60} {fx} {fy}' fill='none' stroke='{INK}' stroke-width='13'/>"
                 f"<path d='M0 -380 Q{fx*0.4:.0f} {fy+60} {fx} {fy}' fill='none' stroke='#4caf3e' stroke-width='6'/>"
                 + "".join(f"<circle cx='{fx + 22*math.cos(a):.1f}' cy='{fy + 22*math.sin(a):.1f}' r='16' fill='{col}' stroke='{INK}' stroke-width='5'/>" for a in np.linspace(0, 6.28, 6)[:-1])
                 + f"<circle cx='{fx}' cy='{fy}' r='14' fill='#fff3b0' stroke='{INK}' stroke-width='5'/></g>")
    # lámina envolviendo el jarrón (sube de 2.4 a 4.6, se suelta desde 5.2)
    wrap = seg(t, 2.4, 4.6) * (1 - seg(t, 5.15, 5.4))
    if wrap > 0.01:
        hgt = 230 * wrap
        g.append(f"<g transform='translate(-118,{-150 - hgt:.1f})'>{lamina(236, max(hgt, 30), r=15, paso=40)}</g>")
    # caja (delante del jarrón)
    g.append(f"<path d='M-170 -200 L-230 -250 L-150 -270 L-110 -205 Z' fill='#d9a15a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M170 -200 L230 -250 L150 -270 L110 -205 Z' fill='#d9a15a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<rect x='-170' y='-205' width='340' height='215' rx='8' fill='#e8b46a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-30' y='-205' width='60' height='215' fill='#c99550' opacity='0.8'/>")
    g.append(f"<path d='M-120 -120 L-70 -120 M-95 -145 L-95 -95' stroke='#b97c3a' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M70 -80 L120 -80' stroke='#b97c3a' stroke-width='10' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def lamina_volando(t):
    """De 5,2 a 7,45 la lámina vuela del jarrón a la pared (esquina izquierda de la franja)."""
    k = seg(t, 5.2, 7.4)
    if t < 5.15 or t >= REVELACION:
        return ""
    x = lerp(182, 40, k) + 60 * math.sin(k * math.pi)
    y = lerp(1200, 1070, k) - 120 * math.sin(k * math.pi)
    rot = lerp(0, -6, k) + 10 * math.sin(t * 5)
    sk = 10 * math.sin(t * 6)
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) skewY({sk:.1f})'>"
            f"{lamina(236, 230, r=15, paso=40)}</g>")


def papel_pintado(t, reveal):
    """Franja de la pared cubierta por papel pintado de burbujas de colores (barrido de izq. a der.)."""
    if reveal <= 0:
        return ""
    wid = W * reveal
    g = [f"<clipPath id='barr'><rect x='0' y='{BAND_TOP}' width='{wid:.1f}' height='{BAND_BOT - BAND_TOP}'/></clipPath>",
         f"<g clip-path='url(#barr)'>",
         f"<rect x='0' y='{BAND_TOP}' width='{W}' height='{BAND_BOT - BAND_TOP}' fill='#e9f7ff'/>"]
    paso = 72; row = 0; yy = BAND_TOP + 46
    while yy < BAND_BOT - 20:
        xx = 40 + (paso / 2 if row % 2 else 0)
        col = 0
        while xx < W + 40:
            c = PASTEL[(row * 2 + col) % len(PASTEL)]
            r = 27 + 2 * math.sin(t * 4 + xx * 0.05 + yy * 0.03)
            g.append(burbuja(xx, yy, r, fill=c, sw=4, edge=mix(c, INK, 0.45)))
            xx += paso; col += 1
        yy += paso * 0.87; row += 1
    g.append("</g>")
    # borde del rollo de papel que va pegándose
    if reveal < 1:
        g.append(f"<rect x='{wid - 16:.1f}' y='{BAND_TOP - 10}' width='32' height='{BAND_BOT - BAND_TOP + 20}' rx='14' fill='#d9f4ff' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='0' y='{BAND_TOP}' width='{wid:.1f}' height='{BAND_BOT - BAND_TOP}' fill='none' stroke='{INK}' stroke-width='6'/>")
    return "".join(g)


def frame(t):
    reveal = seg(t, REVELACION, REVELACION + 0.75)
    dim = seg(t, 5.0, 7.0) * (1 - seg(t, REVELACION, REVELACION + 0.3))
    flash = clamp(1 - (t - REVELACION) / 0.6) if t >= REVELACION else 0
    wall_top = mix(mix("#7fc8c0", "#4d8f99", dim), "#8fe0d4", seg(t, REVELACION, 8.4))
    wall_bot = mix(mix("#b9e3cf", "#7fb0a6", dim), "#d2f5e2", seg(t, REVELACION, 8.4))
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_top}'/>"
            f"<stop offset='1' stop-color='{wall_bot}'/></linearGradient>"
            f"<radialGradient id='luz'><stop offset='0' stop-color='#fff8d8' stop-opacity='{0.55 - 0.3*dim:.2f}'/>"
            f"<stop offset='1' stop-color='#fff8d8' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='suelo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#c98a4b', '#8c5e33', dim)}'/>"
            f"<stop offset='1' stop-color='{mix('#a86a34', '#6e4626', dim)}'/></linearGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    z = 1 + 0.13 * seg(t, REVELACION, 10)
    sc = []
    # rayas suaves en la pared
    for i in range(0, W, 120):
        sc.append(f"<rect x='{i}' y='0' width='60' height='{BAND_TOP}' fill='#ffffff' opacity='0.07'/>")
    # mancha de luz de una ventana (se desliza despacio)
    lx = 700 + 60 * math.sin(t * 0.5)
    sc.append(f"<ellipse cx='{lx:.0f}' cy='620' rx='520' ry='420' fill='url(#luz)'/>")
    # franja baja de la pared (zócalo liso) y moldura
    sc.append(f"<rect x='0' y='{BAND_TOP}' width='{W}' height='{BAND_BOT - BAND_TOP}' fill='{mix(mix('#f3e3c3', '#b8a88a', dim), '#f3e3c3', reveal)}'/>")
    for i in range(60, W, 180):
        sc.append(f"<rect x='{i}' y='{BAND_TOP + 50}' width='120' height='{BAND_BOT - BAND_TOP - 100}' rx='10' fill='none' stroke='{mix('#d8c49c', '#9b8a6d', dim)}' stroke-width='6'/>")
    sc.append(papel_pintado(t, reveal))
    sc.append(f"<rect x='-10' y='{BAND_TOP - 22}' width='{W + 20}' height='30' rx='6' fill='#a8683a' stroke='{INK}' stroke-width='7'/>")
    # suelo de madera
    sc.append(f"<rect x='0' y='{BAND_BOT}' width='{W}' height='44' fill='#fdf6ea' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<rect x='-10' y='{FLOOR}' width='{W + 20}' height='{H - FLOOR + 10}' fill='url(#suelo)' stroke='{INK}' stroke-width='{LW}'/>")
    for k, yy in enumerate((1660, 1760, 1870)):
        sc.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='{INK}' stroke-width='5' opacity='0.45'/>")
        for xx in range(80 + k * 110, W, 330):
            sc.append(f"<line x1='{xx}' y1='{yy - (80 if k else 80)}' x2='{xx}' y2='{yy}' stroke='{INK}' stroke-width='5' opacity='0.45'/>")
    # alfombra
    sc.append(f"<ellipse cx='560' cy='1760' rx='420' ry='90' fill='#ff7a6b' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<ellipse cx='560' cy='1760' rx='330' ry='62' fill='none' stroke='#ffd23f' stroke-width='10'/>")
    # planta en maceta a la derecha (fondo)
    sway = 4 * pulso(t, 2.4)
    sc.append(f"<g transform='translate(1035,{FLOOR - 10}) scale(0.8)'>"
              f"<g transform='rotate({sway:.1f} 0 -150)'>"
              + "".join(f"<path d='M0 -150 Q{dx*0.5:.0f} {-260 + abs(dx)*0.3:.0f} {dx} {-330 + abs(dx)*0.6:.0f} Q{dx*0.2:.0f} -250 0 -150 Z' fill='#4caf3e' stroke='{INK}' stroke-width='6'/>" for dx in (-90, -40, 20, 80))
              + "</g>"
              f"<path d='M-70 -160 L70 -160 L52 0 L-52 0 Z' fill='#e86f3c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
              f"<rect x='-80' y='-182' width='160' height='34' rx='8' fill='#f08a52' stroke='{INK}' stroke-width='{LW}'/></g>")
    sc.append(caja(t))
    sc.append(lamina_volando(t))
    sc.append(rollo(t))
    # chispas sobre el papel pintado
    if t >= REVELACION:
        for sx, sy, ph, sr in SPARK:
            if sx > W * reveal: continue
            a = clamp(math.sin((t - REVELACION) * 4 + ph * 3))
            if a > 0.05:
                r = sr * a
                sc.append(f"<path d='M{sx} {sy - r*1.8:.1f} L{sx + r*0.4:.1f} {sy - r*0.4:.1f} L{sx + r*1.8:.1f} {sy} L{sx + r*0.4:.1f} {sy + r*0.4:.1f} L{sx} {sy + r*1.8:.1f} L{sx - r*0.4:.1f} {sy + r*0.4:.1f} L{sx - r*1.8:.1f} {sy} L{sx - r*0.4:.1f} {sy - r*0.4:.1f} Z' fill='#fff' stroke='#ffd23f' stroke-width='3'/>")
    # motas de polvo en la luz
    for mx, my, mr, sp, ph in MOTES:
        yy = (my - t * sp) % 1900
        sc.append(f"<circle cx='{mx + 18*math.sin(t*0.8 + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#fffbe6' opacity='0.45'/>")
    s.append(zoom(560, 1380, z, "".join(sc)))
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.75*flash:.2f}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
