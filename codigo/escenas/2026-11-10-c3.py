"""2026-11-10-c3 · Inventos: el microondas nació de una chocolatina derretida (Percy Spencer, 1945).

Un laboratorio: un aparato de radar (magnetrón) sobre la mesa emite ondas hacia una chocolatina
con cara. La chocolatina suda y se derrite sin fuego; en la REVELACION el aparato se convierte
en un horno de microondas que brilla.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45   # el aparato se convierte en microondas: golpe musical
MUSICA = 2

rng = np.random.default_rng(11)
MOTAS = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.28)) for _ in range(30)]
CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(180, 420), rng.uniform(6, 13)) for _ in range(26)]
BENCH = 1460      # altura del tablero de la mesa
CX = 800          # posición final de la chocolatina


def fondo(t, calido):
    s = []
    top = mix("#7ccfd0", "#ffd98a", calido); low = mix("#4fa6b2", "#ffb35c", calido)
    # azulejos suaves del zócalo
    zc = mix("#3e8f9b", "#e8954a", calido)
    s.append(f"<rect x='-20' y='1120' width='{W + 40}' height='{BENCH - 1120}' fill='{zc}' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(0, W + 1, 135):
        s.append(f"<line x1='{x}' y1='1125' x2='{x}' y2='{BENCH}' stroke='{mix('#357f8a', '#d47f38', calido)}' stroke-width='5'/>")
    s.append(f"<line x1='0' y1='1290' x2='{W}' y2='1290' stroke='{mix('#357f8a', '#d47f38', calido)}' stroke-width='5'/>")
    # cable del aparato hasta la pared
    s.append(f"<path d='M160 1400 C 60 1400 70 1250 -10 1240' fill='none' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>")
    s.append(f"<path d='M160 1400 C 60 1400 70 1250 -10 1240' fill='none' stroke='#3a3a44' stroke-width='9' stroke-linecap='round'/>")
    return "".join(s), top, low


def mesa():
    s = [f"<rect x='-20' y='{BENCH}' width='{W + 40}' height='{H - BENCH + 20}' fill='#b8682f' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='-20' y='{BENCH}' width='{W + 40}' height='46' fill='#d9894a' stroke='{INK}' stroke-width='{LW}'/>"]
    for x0 in (60, 580):
        s.append(f"<rect x='{x0}' y='1580' width='440' height='150' rx='16' fill='#c87638' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<rect x='{x0 + 180}' y='1640' width='80' height='26' rx='13' fill='#f2d16b' stroke='{INK}' stroke-width='6'/>")
        s.append(f"<rect x='{x0}' y='1770' width='440' height='170' rx='16' fill='#c87638' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<rect x='{x0 + 180}' y='1830' width='80' height='26' rx='13' fill='#f2d16b' stroke='{INK}' stroke-width='6'/>")
    # vetas
    for y in (1530, 1555):
        s.append(f"<path d='M20 {y} Q300 {y - 8} 540 {y} T1060 {y}' fill='none' stroke='#a35a26' stroke-width='4' opacity='0.6'/>")
    return "".join(s)


def aparato(t):
    """Generador de radar con magnetrón de cobre y bocina emisora."""
    k = 1 - seg(t, 7.15, 7.45)            # se encoge justo antes de transformarse
    if k <= 0.01:
        return ""
    vib = 2.5 * math.sin(t * 40) * seg(t, 2.2, 3) * k
    luz = "#ff4d4d" if (t % 0.6) < 0.3 else "#ffd23f"
    a1 = -40 + 70 * (0.5 + 0.5 * math.sin(t * 2.3)) * seg(t, 2, 3)
    a2 = 30 - 60 * (0.5 + 0.5 * math.sin(t * 3.1 + 1)) * seg(t, 2, 3)
    g = [f"<g transform='translate({300 + vib:.1f},{BENCH}) scale({k:.3f}) translate(-300,{-BENCH})'>"]
    g.append(f"<ellipse cx='320' cy='{BENCH + 6}' rx='200' ry='16' fill='#000' opacity='0.2'/>")
    # caja
    g.append(f"<rect x='140' y='1290' width='320' height='{BENCH - 1290}' rx='20' fill='#7d8fa3' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='160' y='1312' width='280' height='22' rx='8' fill='#95a7ba' stroke='{INK}' stroke-width='5'/>")
    for dx, ang in ((215, a1), (330, a2)):
        g.append(f"<circle cx='{dx}' cy='1395' r='40' fill='#f4f1e6' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<line x1='{dx}' y1='1395' x2='{dx + 30 * math.sin(math.radians(ang)):.1f}' y2='{1395 - 30 * math.cos(math.radians(ang)):.1f}' stroke='#e2453c' stroke-width='6' stroke-linecap='round'/>")
        g.append(f"<circle cx='{dx}' cy='1395' r='7' fill='{INK}'/>")
    g.append(f"<circle cx='415' cy='1375' r='16' fill='{luz}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='395' y='1412' width='40' height='22' rx='6' fill='#4a5866' stroke='{INK}' stroke-width='5'/>")
    # magnetrón (cilindro de cobre con aletas)
    g.append(f"<rect x='215' y='1175' width='130' height='118' rx='14' fill='#d9823f' stroke='{INK}' stroke-width='{LW}'/>")
    for y in range(1195, 1285, 18):
        g.append(f"<line x1='222' y1='{y}' x2='338' y2='{y}' stroke='#a85a26' stroke-width='6'/>")
    g.append(f"<rect x='245' y='1150' width='70' height='30' rx='8' fill='#5b5f6b' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='280' cy='1140' r='12' fill='#ffcc66' stroke='{INK}' stroke-width='5' opacity='{0.6 + 0.4 * math.sin(t * 9):.2f}'/>")
    # bocina emisora
    g.append(f"<path d='M455 1330 L470 1330 L555 1295 L555 1405 L470 1370 L455 1370 Z' fill='#b9c4cf' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='555' cy='1350' rx='14' ry='55' fill='#5b5f6b' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def ondas(t):
    on = seg(t, 2.2, 3.0) * (1 - seg(t, 7.2, 7.5))
    if on <= 0.01:
        return ""
    s = []
    for i in range(5):
        p = ((t * 0.9 + i / 5) % 1.0)
        r = lerp(20, 230, p)
        op = on * (1 - p) * 0.95
        s.append(f"<path d='M{560 + r * 0.55:.0f} {1350 - r * 0.8:.0f} Q{560 + r * 1.05:.0f} 1350 {560 + r * 0.55:.0f} {1350 + r * 0.8:.0f}' "
                 f"fill='none' stroke='#ff5fa2' stroke-width='12' stroke-linecap='round' opacity='{op:.2f}'/>")
    return "".join(s)


def chocolatina(t):
    m = ease(clamp((t - 5.0) / 3.2))          # derretido 0..1
    x = lerp(930, CX, seg(t, 0, 1.6))
    salto = abs(math.sin(t * 7.5)) * 34 * (1 - seg(t, 1.4, 1.7))
    temblor = 3 * math.sin(t * 50) * seg(t, 5.0, 5.6) * (1 - seg(t, 7.4, 7.6))
    yb = BENCH - salto
    wr_h = 120                                 # envoltorio
    yw = yb - wr_h
    ch = lerp(200, 100, m)                      # alto de la parte de chocolate visible
    wid = lerp(220, 250, m)
    yt = yw - ch
    s = [f"<g transform='translate({x + temblor:.1f},0)'>"]
    # sombra / charco
    s.append(f"<ellipse cx='0' cy='{BENCH + 8}' rx='{150 + 40 * m:.0f}' ry='16' fill='#000' opacity='0.18'/>")
    pr = lerp(0, 230, seg(t, 6.0, 9.0))
    if pr > 2:
        s.append(f"<path d='M{-pr:.0f} {BENCH + 4} Q{-pr * 0.6:.0f} {BENCH - 18} 0 {BENCH - 14} Q{pr * 0.7:.0f} {BENCH - 20} {pr:.0f} {BENCH + 4} "
                 f"Q{pr * 0.5:.0f} {BENCH + 30} 0 {BENCH + 26} Q{-pr * 0.5:.0f} {BENCH + 32} {-pr:.0f} {BENCH + 4} Z' fill='#6b3519' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<ellipse cx='{-pr * 0.35:.0f}' cy='{BENCH - 2}' rx='{pr * 0.18:.0f}' ry='5' fill='#9a5a32'/>")
    # parte de chocolate (borde superior ondulado al derretirse)
    hw = wid / 2
    ond = 18 * m
    ph = t * 3
    top = (f"M{-hw:.0f} {yw} L{-hw:.0f} {yt + 24:.0f} Q{-hw:.0f} {yt:.0f} {-hw + 24:.0f} {yt + ond * math.sin(ph):.0f} "
           f"Q{-hw / 2:.0f} {yt - ond + ond * math.sin(ph + 1):.0f} 0 {yt + ond * math.sin(ph + 2):.0f} "
           f"Q{hw / 2:.0f} {yt + ond * 1.4 + ond * math.sin(ph + 3):.0f} {hw - 24:.0f} {yt + ond * math.sin(ph + 4):.0f} "
           f"Q{hw:.0f} {yt:.0f} {hw:.0f} {yt + 24:.0f} L{hw:.0f} {yw} Z")
    s.append(f"<path d='{top}' fill='#7a3e1d' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # onzas (se borran al derretirse)
    if m < 0.9:
        op = 1 - m / 0.9
        for cx in (-55, 55):
            for i in range(2):
                yy = yt + 18 + i * (ch - 30) / 2
                hh = (ch - 50) / 2
                if hh > 8:
                    s.append(f"<rect x='{cx - 45}' y='{yy:.0f}' width='90' height='{hh:.0f}' rx='10' fill='#8f4c26' stroke='#5a2b12' stroke-width='5' opacity='{op:.2f}'/>")
    # goterones que bajan por el envoltorio
    for dx, d0, ln in ((-80, 5.6, 110), (10, 6.0, 150), (75, 5.8, 90)):
        k = seg(t, d0, d0 + 1.6)
        if k > 0:
            L = ln * k
            s.append(f"<path d='M{dx - 18} {yw - 4} L{dx - 18} {yw + L - 14:.0f} Q{dx - 18} {yw + L + 4:.0f} {dx} {yw + L + 4:.0f} "
                     f"Q{dx + 18} {yw + L + 4:.0f} {dx + 18} {yw + L - 14:.0f} L{dx + 18} {yw - 4} Z' fill='#7a3e1d' stroke='{INK}' stroke-width='6'/>")
    # envoltorio rojo con papel plateado
    s.append(f"<path d='M{-hw - 6:.0f} {yw - 10} L{-hw + 30:.0f} {yw + 4} L{-hw + 70:.0f} {yw - 8} L{-hw + 120:.0f} {yw + 6} L{hw - 70:.0f} {yw - 8} L{hw - 28:.0f} {yw + 5} L{hw + 6:.0f} {yw - 10} L{hw + 6:.0f} {yw + 20} L{-hw - 6:.0f} {yw + 20} Z' fill='#d8dde4' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    s.append(f"<rect x='{-hw - 10:.0f}' y='{yw + 14}' width='{wid + 20:.0f}' height='{wr_h - 14}' rx='12' fill='#e2453c' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{-hw - 10:.0f}' y='{yw + 52}' width='{wid + 20:.0f}' height='26' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    # redibujar los goterones por delante del envoltorio
    for dx, d0, ln in ((-80, 5.6, 110), (10, 6.0, 150), (75, 5.8, 90)):
        k = seg(t, d0, d0 + 1.6)
        if k > 0.05:
            L = ln * k
            s.append(f"<path d='M{dx - 18} {yw + 10} L{dx - 18} {yw + L - 14:.0f} Q{dx - 18} {yw + L + 4:.0f} {dx} {yw + L + 4:.0f} "
                     f"Q{dx + 18} {yw + L + 4:.0f} {dx + 18} {yw + L - 14:.0f} L{dx + 18} {yw + 10} Z' fill='#7a3e1d' stroke='{INK}' stroke-width='6'/>")
            s.append(f"<path d='M{dx - 18} {yw + 6} L{dx + 18} {yw + 6}' stroke='#7a3e1d' stroke-width='10'/>")
    # brazos
    sw = 14 * math.sin(t * 6)
    ay = yw + 50
    if t >= REVELACION:
        s.append(f"<path d='M{-hw - 8:.0f} {ay} Q{-hw - 60:.0f} {ay - 50:.0f} {-hw - 50:.0f} {ay - 110 + sw:.0f}' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
        s.append(f"<path d='M{hw + 8:.0f} {ay} Q{hw + 60:.0f} {ay - 50:.0f} {hw + 50:.0f} {ay - 110 - sw:.0f}' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    else:
        s.append(f"<path d='M{-hw - 8:.0f} {ay} Q{-hw - 50:.0f} {ay + 10:.0f} {-hw - 60:.0f} {ay + 50 + sw:.0f}' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
        s.append(f"<path d='M{hw + 8:.0f} {ay} Q{hw + 50:.0f} {ay + 10:.0f} {hw + 60:.0f} {ay + 50 - sw:.0f}' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    # cara: en el chocolate mientras hay alto; luego sobre el envoltorio
    fy = yt + lerp(ch * 0.45, 38, m)
    blink = 1.0 if (t % 2.7) > 0.13 else 0.15
    mira = lerp(0, -10, seg(t, 2.3, 3.0)) * (1 - seg(t, 7.4, 7.8))
    miedo = seg(t, 5.0, 5.6) * (1 - seg(t, 7.4, 7.7))
    for ex in (-42, 42):
        rw = 26 + 4 * miedo
        s.append(f"<g transform='translate({ex},{fy:.0f}) scale(1,{blink})'><circle r='{rw:.0f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{mira:.1f}' cy='2' r='{13 - 3 * miedo:.1f}' fill='{INK}'/><circle cx='{mira - 5:.1f}' cy='-4' r='5' fill='#fff'/></g>")
        if miedo > 0.05:
            if ex < 0:
                s.append(f"<path d='M{ex - 24} {fy - 40:.0f} L{ex + 20} {fy - 54:.0f}' stroke='{INK}' stroke-width='8' stroke-linecap='round' opacity='{miedo:.2f}'/>")
            else:
                s.append(f"<path d='M{ex - 20} {fy - 54:.0f} L{ex + 24} {fy - 40:.0f}' stroke='{INK}' stroke-width='8' stroke-linecap='round' opacity='{miedo:.2f}'/>")
    my = fy + lerp(42, 40, m)
    if t >= REVELACION:
        s.append(f"<path d='M-30 {my - 6:.0f} Q0 {my + 30:.0f} 30 {my - 6:.0f} Z' fill='#7a1f1f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    elif miedo > 0.3:
        s.append(f"<ellipse cx='0' cy='{my:.0f}' rx='14' ry='{10 + 4 * math.sin(t * 12):.0f}' fill='#7a1f1f' stroke='{INK}' stroke-width='6'/>")
    else:
        s.append(f"<path d='M-22 {my - 4:.0f} Q0 {my + 16:.0f} 22 {my - 4:.0f}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # gotas de sudor
    sud = seg(t, 4.9, 5.4) * (1 - seg(t, 7.3, 7.5))
    for i, (dx, ph) in enumerate(((-hw - 20, 0.0), (hw + 22, 0.45), (hw - 10, 0.8))):
        p = ((t * 1.3 + ph) % 1.0)
        if sud > 0.02:
            yy = yt + 10 + p * 90
            s.append(f"<path d='M{dx:.0f} {yy - 18:.0f} Q{dx + 12:.0f} {yy:.0f} {dx:.0f} {yy + 6:.0f} Q{dx - 12:.0f} {yy:.0f} {dx:.0f} {yy - 18:.0f} Z' fill='#7fd3ff' stroke='{INK}' stroke-width='4' opacity='{sud * (1 - p):.2f}'/>")
    s.append("</g>")
    return "".join(s)


def microondas(t):
    k = rebote(t, REVELACION, 0.55)
    if k <= 0:
        return ""
    gl = 0.75 + 0.25 * math.sin(t * 6)
    rot = (t - REVELACION) * 140
    g = [f"<g transform='translate(330,{BENCH}) scale({k:.3f}) translate(-330,{-BENCH})'>"]
    g.append(f"<ellipse cx='330' cy='{BENCH + 6}' rx='260' ry='18' fill='#000' opacity='0.22'/>")
    g.append(f"<rect x='90' y='1130' width='480' height='{BENCH - 1130 - 18}' rx='34' fill='#f6e7c8' stroke='{INK}' stroke-width='{LW}'/>")
    for fx in (130, 530):
        g.append(f"<rect x='{fx - 22}' y='{BENCH - 26}' width='44' height='26' rx='8' fill='#5b5f6b' stroke='{INK}' stroke-width='6'/>")
    # puerta con ventana iluminada
    g.append(f"<rect x='118' y='1158' width='330' height='254' rx='24' fill='#e9d3a8' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='140' y='1180' width='286' height='210' rx='18' fill='url(#horno)' stroke='{INK}' stroke-width='7' opacity='{gl:.2f}'/>")
    # plato girando con una taza humeante
    g.append(f"<ellipse cx='283' cy='1360' rx='110' ry='18' fill='#ffe9a8' stroke='{INK}' stroke-width='5'/>")
    tx = 283 + 40 * math.sin(math.radians(rot))
    g.append(f"<path d='M{tx - 38:.0f} 1290 L{tx + 38:.0f} 1290 L{tx + 32:.0f} 1355 Q{tx:.0f} 1365 {tx - 32:.0f} 1355 Z' fill='#5ec8ff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M{tx + 36:.0f} 1305 Q{tx + 62:.0f} 1315 {tx + 34:.0f} 1338' fill='none' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='{tx:.0f}' cy='1292' rx='36' ry='8' fill='#7a3e1d' stroke='{INK}' stroke-width='5'/>")
    for i in range(3):
        sy = 1270 - ((t * 60 + i * 25) % 70)
        g.append(f"<path d='M{tx - 18 + i * 18:.0f} {sy:.0f} q8 -12 0 -24' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round' opacity='0.85'/>")
    # panel de mandos
    g.append(f"<rect x='466' y='1158' width='80' height='254' rx='16' fill='#5ec8c0' stroke='{INK}' stroke-width='7'/>")
    for ky, ang in ((1210, rot), (1290, -rot * 0.5)):
        g.append(f"<g transform='translate(506,{ky}) rotate({ang:.0f})'><circle r='26' fill='#f6e7c8' stroke='{INK}' stroke-width='6'/>"
                 f"<line x1='0' y1='0' x2='0' y2='-20' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>")
    g.append(f"<rect x='482' y='1345' width='48' height='34' rx='8' fill='#ff7a45' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    calido = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    fondo_svg, top, low = fondo(t, calido)
    defs = (f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='horno' cx='0.5' cy='0.55' r='0.7'><stop offset='0' stop-color='#fff6c2'/><stop offset='0.6' stop-color='#ffd23f'/><stop offset='1' stop-color='#ff9a3c'/></radialGradient>"
            "<radialGradient id='halo'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.95'/><stop offset='0.5' stop-color='#ffe066' stop-opacity='0.55'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    escena = [fondo_svg]
    # rayos y halo de la revelación
    if calido > 0.01:
        rr = []
        for i in range(14):
            a = math.radians(i * 360 / 14 + t * 18)
            a2 = a + math.radians(9)
            R = 1100
            rr.append(f"M330 1290 L{330 + R * math.cos(a):.0f} {1290 + R * math.sin(a):.0f} L{330 + R * math.cos(a2):.0f} {1290 + R * math.sin(a2):.0f} Z")
        escena.append(f"<path d='{' '.join(rr)}' fill='#fff3b0' opacity='{0.45 * calido:.2f}'/>")
        escena.append(f"<circle cx='330' cy='1290' r='{lerp(150, 520, calido):.0f}' fill='url(#halo)'/>")
    escena.append(mesa())
    escena.append(aparato(t))
    escena.append(microondas(t))
    escena.append(ondas(t))
    escena.append(chocolatina(t))
    # chispas de la revelación
    if t >= REVELACION:
        p = clamp((t - REVELACION) / 1.6)
        for a, d, r in CHISPAS:
            dd = d * ease(p) + 30
            op = 1 - p * 0.7
            escena.append(f"<circle cx='{330 + dd * math.cos(a):.0f}' cy='{1290 + dd * math.sin(a) * 0.8:.0f}' r='{r * (1 - 0.4 * p):.1f}' fill='#fff7c2' stroke='{INK}' stroke-width='3' opacity='{op:.2f}'/>")
    # motas flotando
    for mx, my, mr, sp, ph in MOTAS:
        yy = (my - t * sp - 1000) % 900 + 1000
        escena.append(f"<circle cx='{mx + 18 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#ffffff' opacity='0.35'/>")
    z = 1 + 0.08 * seg(t, REVELACION, 10)
    s.append(zoom(540, 1480, z, f"<g transform='translate(540,1600) scale(1.12) translate(-540,{-BENCH})'>" + "".join(escena) + "</g>"))
    # destello
    fl = clamp(1 - abs(t - REVELACION) / 0.25)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe8' opacity='{0.7 * fl:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
