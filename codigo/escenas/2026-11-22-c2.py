"""2026-11-22-c2 · Un huevo se hunde en agua del grifo, pero flota si disuelves mucha sal:
el agua salada es más densa que el huevo (NOAA, Science Buddies / Scientific American).

Escena: cocina con azulejos. Un vaso grande de agua en la mitad de abajo. Un huevo con cara cae,
salpica y se hunde hasta el fondo. Una cuchara vierte sal, el agua se arremolina y en la
REVELACION el huevo sube de golpe y flota feliz; el agua brilla y la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso

DUR = 10.0
REVELACION = 7.4    # el huevo sube y flota: golpe musical
MUSICA = 4

rng = np.random.default_rng(22)
BURBUJAS = [(rng.uniform(300, 780), rng.uniform(0, 1), rng.uniform(6, 14), rng.uniform(60, 120)) for _ in range(18)]
SAL = [(rng.uniform(-30, 30), rng.uniform(0, 1.6), rng.uniform(8, 12)) for _ in range(80)]
CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(170, 330), rng.uniform(8, 16)) for _ in range(14)]
GOTAS = [(rng.uniform(-1, 1), rng.uniform(0.6, 1.0), rng.uniform(9, 16)) for _ in range(12)]

AGUA_Y = 1130           # nivel del agua
VASO_TOP, VASO_BOT = 1020, 1800
FONDO_Y = 1668          # centro del huevo en el fondo
FLOTA_Y = 1185          # centro del huevo flotando


def huevo_y(t):
    if t < 0.45:
        return lerp(905, AGUA_Y, (t / 0.45) ** 2)
    if t < 6.95:
        y = lerp(AGUA_Y, FONDO_Y, seg(t, 0.45, 2.3))
        # pequeño rebote al tocar el fondo
        y -= 14 * math.sin(math.pi * clamp((t - 2.3) / 0.5)) if 2.3 < t < 2.8 else 0
        # tiembla un poco cuando cae la sal
        if 5.6 < t < 6.95:
            y -= 6 * abs(math.sin(t * 18)) * seg(t, 5.6, 6.4)
        return y
    k = clamp((t - 6.95) / 0.9)
    y = lerp(FONDO_Y, FLOTA_Y, ease(k))
    y -= 40 * math.sin(math.pi * clamp((t - 7.55) / 0.6)) if 7.55 < t < 8.15 else 0
    if t > 8.15:
        y += 6 * math.sin((t - 8.15) * 3.2)
    return y


def huevo(t):
    y = huevo_y(t)
    x = 540 + (20 * math.sin(t * 1.3) if t > 8.1 else 0)
    ang = lerp(0, 16, seg(t, 1.4, 2.5)) * (1 - seg(t, 6.95, 7.6)) + (4 * math.sin(t * 2.6) if t > 8.1 else 0)
    feliz = seg(t, 7.3, 7.7)
    triste = seg(t, 2.6, 3.4) * (1 - feliz)
    blink = 0.12 if ((t + 1.0) % 2.7) < 0.12 else 1.0
    sorpresa = seg(t, 6.6, 7.0) * (1 - feliz)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f})'>"]
    g.append(f"<path d='M0 -128 C62 -128 98 -40 98 30 C98 92 56 124 0 124 C-56 124 -98 92 -98 30 C-98 -40 -62 -128 0 -128 Z' "
             f"fill='#fff4de' stroke='{INK}' stroke-width='{LW}'/>")
    g.append("<path d='M38 -96 C66 -70 78 -30 80 6' fill='none' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='0.9'/>")
    g.append("<path d='M-80 50 C-70 90 -36 110 0 112' fill='none' stroke='#ecd3ae' stroke-width='16' stroke-linecap='round'/>")
    # ojos
    for ex in (-34, 34):
        if feliz > 0.5:
            g.append(f"<path d='M{ex-17} 6 Q{ex} -16 {ex+17} 6' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
        else:
            r = 17 + 5 * sorpresa
            g.append(f"<g transform='translate({ex},0) scale(1,{blink})'><ellipse rx='{r-3:.1f}' ry='{r:.1f}' fill='{INK}'/>"
                     f"<circle cx='-5' cy='-7' r='6' fill='#fff'/></g>")
            if triste > 0.1:
                s = -1 if ex < 0 else 1
                g.append(f"<path d='M{ex-16} {-30 - 6*s*triste:.1f} L{ex+16} {-30 + 6*s*triste:.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # mofletes
    g.append("<ellipse cx='-58' cy='34' rx='15' ry='9' fill='#ff9aa2' opacity='0.8'/><ellipse cx='58' cy='34' rx='15' ry='9' fill='#ff9aa2' opacity='0.8'/>")
    # boca
    if feliz > 0.5:
        g.append(f"<path d='M-26 36 Q0 72 26 36 Z' fill='#c23a4a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    elif sorpresa > 0.3:
        g.append(f"<ellipse cx='0' cy='48' rx='10' ry='{8 + 6*sorpresa:.1f}' fill='#c23a4a' stroke='{INK}' stroke-width='5'/>")
    else:
        curva = lerp(16, -10, triste)
        g.append(f"<path d='M-18 44 Q0 {44 + curva:.1f} 18 44' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def cuchara(t):
    ent = seg(t, 4.3, 5.1) * (1 - seg(t, 7.0, 7.6))
    if ent <= 0:
        return "", 0
    inc = lerp(0, -38, seg(t, 5.2, 5.6))
    sacude = 4 * math.sin(t * 30) if 5.6 < t < 6.9 else 0
    x = lerp(1250, 700, ent); y = lerp(1010, 980, ent)
    vacia = seg(t, 5.5, 6.9)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({inc + sacude:.1f})'>"]
    g.append(f"<rect x='40' y='-14' width='300' height='28' rx='14' fill='#c9ced6' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='0' cy='0' rx='70' ry='44' fill='#dfe3e8' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='-4' cy='-6' rx='{52*(1-vacia*0.8):.1f}' ry='{26*(1-vacia*0.8):.1f}' fill='#ffffff' stroke='#c9cfd8' stroke-width='3'/>")
    g.append("</g>")
    return "".join(g), x - 40


def frame(t):
    rev = seg(t, 7.3, 8.0)
    sal = seg(t, 5.6, 7.0)
    # agua: azul claro -> algo lechosa con la sal -> turquesa brillante en la revelación
    agua_top = mix(mix("#9fe3f7", "#c4e9f0", sal * 0.6), "#7af0e2", rev)
    agua_bot = mix(mix("#4fb6e6", "#7cc4dd", sal * 0.6), "#2fcfc4", rev)
    pared1 = mix("#ffe9c7", "#fff2d9", rev); pared2 = mix("#ffd6a8", "#ffe4bd", rev)
    defs = (f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{pared1}'/><stop offset='1' stop-color='{pared2}'/></linearGradient>"
            f"<linearGradient id='agua' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{agua_top}'/><stop offset='1' stop-color='{agua_bot}'/></linearGradient>"
            f"<radialGradient id='brillo'><stop offset='0' stop-color='#fffbd0' stop-opacity='{0.85*rev:.3f}'/><stop offset='1' stop-color='#fffbd0' stop-opacity='0'/></radialGradient>"
            "<linearGradient id='rayo' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='0.45'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></linearGradient>"
            "<clipPath id='dentro'><path d='M262 1030 L818 1030 L792 1785 Q540 1805 288 1785 Z'/></clipPath>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # azulejos suaves
    for yy in range(0, 1700, 135):
        s.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='#e8c294' stroke-width='4' opacity='0.55'/>")
    for row, yy in enumerate(range(0, 1700, 135)):
        off = 67 if row % 2 else 0
        for xx in range(-off, W + 135, 135):
            s.append(f"<line x1='{xx}' y1='{yy}' x2='{xx}' y2='{yy+135}' stroke='#e8c294' stroke-width='4' opacity='0.55'/>")
    # rayo de luz de una ventana (fuera de plano) que se mueve despacio
    dx = 30 * math.sin(t * 0.6)
    s.append(f"<path d='M{-80+dx:.0f} 0 L{260+dx:.0f} 0 L{820+dx:.0f} 1700 L{420+dx:.0f} 1700 Z' fill='url(#rayo)' opacity='0.55'/>")
    # cámara
    z = 1 + 0.12 * seg(t, 7.3, 8.1)
    cy = 1300
    s.append(f"<g transform='translate(540,{cy}) scale({z:.4f}) translate(-540,{-cy})'>")
    s.append(f"<circle cx='540' cy='1200' r='{lerp(120, 560, rev):.0f}' fill='url(#brillo)'/>")
    # encimera de madera
    s.append(f"<rect x='-40' y='1720' width='1160' height='260' fill='#c98a4e' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='-40' y='1720' width='1160' height='40' fill='#dea366' stroke='{INK}' stroke-width='{LW}'/>")
    for lx, ly, ll in ((80, 1820, 220), (520, 1870, 260), (880, 1810, 170)):
        s.append(f"<path d='M{lx} {ly} q{ll/2} -14 {ll} 0' fill='none' stroke='#a8703c' stroke-width='6' stroke-linecap='round'/>")
    # sombra del vaso
    s.append("<ellipse cx='540' cy='1790' rx='330' ry='30' fill='#000' opacity='0.2'/>")
    # salero al lado (detalle)
    s.append(f"<g transform='translate(910,1600)'><rect x='-55' y='0' width='110' height='160' rx='20' fill='#ffffff' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-55 40 Q-55 -40 0 -46 Q55 -40 55 40 Z' fill='#9aa3ad' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='-16' cy='-14' r='5' fill='{INK}'/><circle cx='0' cy='-22' r='5' fill='{INK}'/><circle cx='16' cy='-14' r='5' fill='{INK}'/>"
             f"<rect x='-30' y='60' width='60' height='60' rx='10' fill='#e8f3ff' stroke='#b7c7d8' stroke-width='4'/></g>")
    # vaso: fondo (parte trasera)
    s.append(f"<path d='M250 {VASO_TOP} L830 {VASO_TOP} L800 1795 Q540 1815 280 1795 Z' fill='#e9f7ff' opacity='0.35' stroke='{INK}' stroke-width='{LW}'/>")
    # agua
    ola = 7 * math.sin(t * 3)
    s.append("<g clip-path='url(#dentro)'>")
    s.append(f"<path d='M200 {AGUA_Y + ola:.1f} Q400 {AGUA_Y - 14 - ola:.1f} 540 {AGUA_Y:.1f} T880 {AGUA_Y + ola:.1f} L880 1820 L200 1820 Z' fill='url(#agua)'/>")
    # remolinos de sal disolviéndose
    rem = seg(t, 5.8, 6.4) * (1 - seg(t, 7.6, 8.4))
    if rem > 0:
        for i in range(4):
            ry = 1250 + i * 120
            rot = (t * 120 + i * 70) % 360
            s.append(f"<ellipse cx='540' cy='{ry}' rx='{170 - i*15}' ry='34' fill='none' stroke='#ffffff' stroke-width='7' "
                     f"stroke-dasharray='60 40' stroke-dashoffset='{rot:.0f}' opacity='{0.6*rem:.2f}'/>")
    # burbujas
    for bx, ph, br, sp in BURBUJAS:
        yy = 1780 - ((t * sp + ph * 650) % 650)
        if yy > AGUA_Y + 12:
            s.append(f"<circle cx='{bx + 10*math.sin(t*2 + bx):.0f}' cy='{yy:.0f}' r='{br:.1f}' fill='#ffffff' opacity='0.35' stroke='#ffffff' stroke-width='3'/>")
    s.append("</g>")
    # granos de sal cayendo de la cuchara
    cu, sx = cuchara(t)
    for gx, ph, gr in SAL:
        tt = t - 5.55 - ph * 0.8
        if 0 < tt < 1.2 and t < 7.0:
            yy = 1010 + tt * 520
            op = 1.0 if yy < AGUA_Y else max(0, 1 - (yy - AGUA_Y) / 220)
            if op > 0:
                s.append(f"<rect x='{sx - 30 + gx:.0f}' y='{yy:.0f}' width='{gr:.0f}' height='{gr:.0f}' fill='#ffffff' stroke='#7f8fa0' stroke-width='3' opacity='{op:.2f}'/>")
    # huevo
    s.append(huevo(t))
    # tinte del agua sobre la parte sumergida del huevo
    s.append("<g clip-path='url(#dentro)'>")
    s.append(f"<path d='M200 {AGUA_Y + ola:.1f} Q400 {AGUA_Y - 14 - ola:.1f} 540 {AGUA_Y:.1f} T880 {AGUA_Y + ola:.1f} L880 1820 L200 1820 Z' fill='{agua_bot}' opacity='0.12'/>")
    s.append(f"<path d='M200 {AGUA_Y + ola:.1f} Q400 {AGUA_Y - 14 - ola:.1f} 540 {AGUA_Y:.1f} T880 {AGUA_Y + ola:.1f}' fill='none' stroke='#ffffff' stroke-width='8' opacity='0.8'/>")
    s.append("</g>")
    # salpicadura al caer el huevo
    sp = clamp((t - 0.45) / 0.7)
    if 0 < sp < 1:
        for gx, gv, gr in GOTAS:
            px = 540 + gx * 260 * sp
            py = AGUA_Y - 330 * gv * sp + 420 * sp * sp
            s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{gr*(1-0.5*sp):.1f}' fill='#bfefff' stroke='{INK}' stroke-width='4'/>")
        s.append(f"<ellipse cx='540' cy='{AGUA_Y}' rx='{lerp(60, 260, sp):.0f}' ry='{lerp(10, 30, sp):.0f}' fill='none' stroke='#ffffff' stroke-width='8' opacity='{1-sp:.2f}'/>")
    # ondas al flotar
    if t > 7.6:
        for i in range(3):
            k = ((t - 7.6) * 0.8 + i / 3) % 1
            s.append(f"<ellipse cx='540' cy='{AGUA_Y + 4}' rx='{lerp(110, 270, k):.0f}' ry='{lerp(14, 32, k):.0f}' fill='none' stroke='#ffffff' stroke-width='6' opacity='{0.8*(1-k):.2f}'/>")
    # vaso: frente (brillos y borde)
    s.append(f"<path d='M250 {VASO_TOP} L830 {VASO_TOP} L800 1795 Q540 1815 280 1795 Z' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<ellipse cx='540' cy='{VASO_TOP}' rx='290' ry='26' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    s.append("<path d='M300 1080 L322 1720' stroke='#ffffff' stroke-width='22' stroke-linecap='round' opacity='0.55'/>")
    s.append("<path d='M350 1090 L362 1300' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.5'/>")
    s.append("<path d='M770 1100 L752 1650' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='0.35'/>")
    # cuchara con sal
    s.append(cu)
    # chispas en la revelación
    if rev > 0:
        ey = huevo_y(t)
        for a, r, cr in CHISPAS:
            aa = a + t * 0.8
            rr = r * (0.6 + 0.4 * rev)
            px = 540 + math.cos(aa) * rr; py = ey + math.sin(aa) * rr * 0.75
            sz = cr * (0.6 + 0.4 * abs(math.sin(t * 5 + a)))
            s.append(f"<path d='M{px:.0f} {py-sz*1.8:.0f} L{px+sz*0.5:.0f} {py:.0f} L{px:.0f} {py+sz*1.8:.0f} L{px-sz*0.5:.0f} {py:.0f} Z' "
                     f"fill='#fff27a' stroke='{INK}' stroke-width='3' opacity='{rev:.2f}'/>")
    s.append("</g></svg>")
    return "".join(s)
