"""Lágrimas en el espacio: no caen, se quedan pegadas al ojo y crecen como una bola de agua.

Una astronauta (personaje original) flota dentro de la estación espacial, mira la Tierra por la
ventana y se emociona. La lágrima no cae: crece y crece sobre el ojo hasta ser una bola de agua.
Arriba: ventana redonda con estrellas y la Tierra asomando (fondo tranquilo para logo y textos).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.4   # la lágrima se convierte en una gran bola de agua: golpe musical
MUSICA = 2

rng = np.random.default_rng(21)
STARS = [(rng.uniform(220, 860), rng.uniform(300, 900), rng.uniform(2.5, 5.5), rng.uniform(0, 6.28)) for _ in range(45)]
GOTITAS = [(rng.uniform(-1, 1), rng.uniform(0, 6.28), rng.uniform(6, 13)) for _ in range(9)]

EYE_L = (-78, -10)   # ojo con la lágrima (izquierda en pantalla), relativo a la cabeza
EYE_R = (78, -10)
HEAD = (540, 1240)
HR = 190


def fondo(t, rev):
    s = []
    # pared del módulo
    wall = mix("#c9d6e6", "#d9ecff", rev)
    s.append(f"<rect width='{W}' height='{H}' fill='{wall}'/>")
    # paneles acolchados
    for i, x in enumerate(range(-40, W + 40, 230)):
        s.append(f"<rect x='{x}' y='-20' width='210' height='{H + 40}' rx='26' fill='{mix('#b9c8db', '#cfe4fb', rev)}' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    # franja inferior con cables y pasamanos
    s.append(f"<rect x='0' y='1010' width='{W}' height='70' fill='{mix('#8ea3bd', '#a9c3e2', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(30, W, 140):
        s.append(f"<circle cx='{x}' cy='1045' r='10' fill='#e9eef5' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<rect x='60' y='1100' width='26' height='420' rx='13' fill='#f2b33d' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<rect x='994' y='1100' width='26' height='420' rx='13' fill='#f2b33d' stroke='{INK}' stroke-width='7'/>")
    # luces de panel parpadeando
    for k, (lx, ly) in enumerate([(150, 1600), (150, 1660), (930, 1600), (930, 1660), (150, 1720)]):
        on = 0.5 + 0.5 * math.sin(t * 5 + k * 1.7)
        col = ["#ff5a5f", "#4cd964", "#ffd23f", "#5ec8ff", "#4cd964"][k]
        s.append(f"<rect x='{lx - 30}' y='{ly - 16}' width='60' height='32' rx='8' fill='#33465e' stroke='{INK}' stroke-width='5'/>")
        s.append(f"<circle cx='{lx}' cy='{ly}' r='9' fill='{col}' opacity='{0.35 + 0.65 * on:.2f}'/>")
    # ventana redonda
    cx, cy, r = 540, 600, 330
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 46}' fill='#e9eef5' stroke='{INK}' stroke-width='{LW}'/>")
    for a in range(0, 360, 30):
        bx = cx + (r + 23) * math.cos(math.radians(a)); by = cy + (r + 23) * math.sin(math.radians(a))
        s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='8' fill='#9aa7b8' stroke='{INK}' stroke-width='4'/>")
    s.append("<clipPath id='win'><circle cx='540' cy='600' r='330'/></clipPath>")
    s.append("<g clip-path='url(#win)'>")
    s.append(f"<rect x='200' y='260' width='680' height='680' fill='url(#space)'/>")
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.6 + ph))
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # la Tierra asomando por abajo
    ex, ey, er = 540, 1240, 560
    s.append(f"<circle cx='{ex}' cy='{ey}' r='{er + 30}' fill='#7fd0ff' opacity='0.35'/>")
    s.append(f"<circle cx='{ex}' cy='{ey}' r='{er}' fill='#2f7fd6' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<clipPath id='tierra'><circle cx='{ex}' cy='{ey}' r='{er - 4}'/></clipPath><g clip-path='url(#tierra)'>")
    off = (t * 22) % 900
    for k in range(3):
        bx = 120 + k * 900 - off
        s.append(f"<path d='M{bx:.0f} 760 q60 -40 140 -10 q70 30 150 -5 q40 40 -20 80 q-90 30 -170 10 q-90 -20 -100 -75 z' fill='#57b85a' stroke='{INK}' stroke-width='6'/>")
        s.append(f"<path d='M{bx + 520:.0f} 720 q50 -30 120 0 q30 40 -30 60 q-70 10 -90 -60 z' fill='#57b85a' stroke='{INK}' stroke-width='6'/>")
    coff = (t * 38) % 900
    for k in range(3):
        bx = 60 + k * 900 - coff
        s.append(f"<path d='M{bx:.0f} 720 q30 -26 70 -8 q30 -24 66 0 q30 4 20 26 l-150 0 q-22 -6 -6 -18 z' fill='#fff' opacity='0.9'/>")
        s.append(f"<path d='M{bx + 420:.0f} 820 q30 -26 70 -8 q30 -24 66 0 q30 4 20 26 l-150 0 q-22 -6 -6 -18 z' fill='#fff' opacity='0.9'/>")
    s.append("</g></g>")
    # reflejo del cristal
    s.append(f"<path d='M330 420 Q400 330 500 300' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.25'/>")
    return "".join(s)


def flotantes(t):
    """Objetos sueltos que flotan y giran: un bolígrafo, una bolsita de zumo y un tornillo."""
    s = []
    px, py = 190 + 40 * math.sin(t * 0.7), 1230 + 30 * math.sin(t * 0.9 + 1)
    s.append(f"<g transform='translate({px:.0f},{py:.0f}) rotate({t * 40:.0f})'>"
             f"<rect x='-70' y='-11' width='140' height='22' rx='10' fill='#ff7a45' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M70 -11 L96 0 L70 11 Z' fill='#f2ead8' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
             f"<rect x='-80' y='-13' width='22' height='26' rx='6' fill='#2e5c9a' stroke='{INK}' stroke-width='5'/></g>")
    jx, jy = 900 + 30 * math.sin(t * 0.8 + 2), 1260 + 35 * math.sin(t * 0.6)
    s.append(f"<g transform='translate({jx:.0f},{jy:.0f}) rotate({-15 + 25 * math.sin(t * 0.9):.0f})'>"
             f"<rect x='-48' y='-62' width='96' height='124' rx='18' fill='#7ed957' stroke='{INK}' stroke-width='7'/>"
             f"<rect x='-30' y='-20' width='60' height='44' rx='10' fill='#fff7d6' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='0' cy='2' r='12' fill='#ff5a5f'/>"
             f"<line x1='20' y1='-62' x2='34' y2='-104' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
             f"<line x1='20' y1='-62' x2='34' y2='-104' stroke='#fff' stroke-width='4' stroke-linecap='round'/></g>")
    sx, sy = 860 + 50 * math.sin(t * 0.5 + 4), 1820 - 40 * math.sin(t * 0.7)
    s.append(f"<g transform='translate({sx:.0f},{sy:.0f}) rotate({t * -70:.0f})'>"
             f"<polygon points='-22,-13 0,-26 22,-13 22,13 0,26 -22,13' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>"
             f"<circle r='8' fill='#8a939e' stroke='{INK}' stroke-width='4'/></g>")
    return "".join(s)


def astronauta(t, crece, rev):
    """Astronauta original con polo azul, pelo que flota hacia arriba y ojos que parpadean."""
    hx, hy = HEAD
    # entra flotando desde abajo a la derecha y luego se mece
    ent = seg(t, 0, 1.9)
    dx = lerp(260, 0, ent) + 10 * math.sin(t * 1.3)
    dy = lerp(380, 0, ent) + 14 * math.sin(t * 1.7)
    rot = lerp(14, 0, ent) + 2.5 * math.sin(t * 1.1)
    g = [f"<g transform='translate({hx + dx:.1f},{hy + dy:.1f}) rotate({rot:.2f})'>"]
    # brazos flotando
    wave = 8 * math.sin(t * 1.6)
    for sgn in (-1, 1):
        ang = -sgn * (50 + wave * sgn)
        g.append(f"<g transform='translate({sgn * 150},300) rotate({ang:.1f})'>"
                 f"<rect x='-45' y='-10' width='90' height='300' rx='44' fill='#2f6fd1' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='0' cy='310' r='46' fill='#f4c09a' stroke='{INK}' stroke-width='{LW}'/></g>")
    # cuerpo (polo azul con parche redondo)
    g.append(f"<path d='M-210 300 Q-200 210 -80 190 L80 190 Q200 210 210 300 L230 720 L-230 720 Z' fill='#2f6fd1' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-70 192 L0 260 L70 192' fill='#f2ead8' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<circle cx='-110' cy='330' r='38' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-128 340 L-110 304 L-92 340 Z' fill='#ff5a5f' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>")
    g.append(f"<rect x='70' y='300' width='80' height='50' rx='8' fill='#ffffff' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='70' y='300' width='80' height='16' fill='#ff5a5f' stroke='{INK}' stroke-width='5'/>")
    # cuello
    g.append(f"<rect x='-50' y='140' width='100' height='70' fill='#f4c09a' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo flotando hacia arriba (detrás de la cabeza)
    hair = []
    for k in range(9):
        a = -150 + k * 15
        ax = HR * 0.92 * math.cos(math.radians(a)); ay = HR * 0.92 * math.sin(math.radians(a))
        sway = 18 * math.sin(t * 2.1 + k * 0.8)
        tipx = ax * 1.35 + sway; tipy = ay * 1.25 - 120 - 20 * math.sin(t * 1.7 + k)
        hair.append(f"<path d='M{ax - 40:.0f} {ay + 20:.0f} Q{ax * 1.2 + sway * 0.5:.0f} {ay - 40:.0f} {tipx:.0f} {tipy:.0f} "
                    f"Q{ax * 1.05 + sway * 0.4 + 20:.0f} {ay - 20:.0f} {ax + 40:.0f} {ay + 20:.0f} Z' fill='#5a3524' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append("".join(hair))
    g.append(f"<ellipse cx='0' cy='-60' rx='{HR + 8}' ry='{HR * 0.75:.0f}' fill='#5a3524' stroke='{INK}' stroke-width='{LW}'/>")
    # orejas y cabeza
    for sgn in (-1, 1):
        g.append(f"<ellipse cx='{sgn * (HR - 6)}' cy='20' rx='34' ry='46' fill='#f4c09a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='0' cy='10' rx='{HR}' ry='{HR + 6}' fill='#f4c09a' stroke='{INK}' stroke-width='{LW}'/>")
    # flequillo
    g.append(f"<path d='M-170 -60 Q-120 -170 0 -175 Q130 -175 175 -50 Q120 -110 40 -100 Q-40 -130 -170 -60 Z' fill='#5a3524' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # cejas: se ponen tristes / emocionadas
    sad = seg(t, 3.0, 3.8)
    for (ex, ey), sgn in ((EYE_L, -1), (EYE_R, 1)):
        lift = lerp(0, 16, sad)
        g.append(f"<path d='M{ex - 40} {ey - 70 + (lift if sgn < 0 else -lift) * 0:.0f} Q{ex} {ey - 88} {ex + 40} {ey - 70}' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round' "
                 f"transform='rotate({sgn * lerp(0, 14, sad):.1f} {ex} {ey - 75})'/>")
    # ojos (miran a la ventana de 2 a 3,4 s)
    look = seg(t, 1.9, 2.6) * (1 - seg(t, 3.4, 4.0))
    blink = 1.0 if ((t + 1.2) % 2.7) > 0.13 or t > 7.0 else 0.12
    for (ex, ey) in (EYE_L, EYE_R):
        g.append(f"<ellipse cx='{ex}' cy='{ey}' rx='42' ry='50' fill='#ffffff' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<g transform='translate({ex + 4:.1f},{ey + lerp(6, -16, look):.1f}) scale(1,{blink})'>"
                 f"<circle r='24' fill='#4a2c1a'/><circle r='13' fill='#1a0f08'/>"
                 f"<circle cx='-8' cy='-9' r='8' fill='#fff'/><circle cx='9' cy='8' r='4' fill='#fff'/></g>")
        if blink < 1:
            g.append(f"<ellipse cx='{ex}' cy='{ey}' rx='44' ry='52' fill='#f4c09a' stroke='{INK}' stroke-width='7'/>"
                     f"<path d='M{ex - 38} {ey} Q{ex} {ey + 14} {ex + 38} {ey}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
        # brillo húmedo en el ojo emocionado
        if sad > 0:
            g.append(f"<path d='M{ex - 34} {ey + 30} Q{ex} {ey + 48} {ex + 34} {ey + 30}' fill='none' stroke='#8fd8ff' stroke-width='8' stroke-linecap='round' opacity='{0.9 * sad:.2f}'/>")
    # mofletes y nariz
    for sgn in (-1, 1):
        g.append(f"<ellipse cx='{sgn * 120}' cy='70' rx='30' ry='18' fill='#ff8f8f' opacity='0.55'/>")
    g.append(f"<path d='M-6 30 Q-22 70 4 76' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # boca: sonrisa -> temblorosa -> "o" de sorpresa en la revelación
    if t < 3.2:
        g.append(f"<path d='M-50 110 Q0 150 50 110' fill='#c2413b' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    elif rev < 0.3:
        wob = 5 * math.sin(t * 18)
        g.append(f"<path d='M-46 128 Q-23 {110 + wob:.0f} 0 126 Q23 {110 - wob:.0f} 46 128' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='125' rx='26' ry='{lerp(14, 32, rev):.0f}' fill='#c2413b' stroke='{INK}' stroke-width='7'/>")
    # LA LÁGRIMA: se queda pegada al ojo y crece
    if crece > 0:
        ex, ey = EYE_L
        r = crece
        cy = ey + lerp(46, 10, clamp((r - 14) / 70))   # nace en el párpado de abajo y sube sobre el ojo
        wob = 1 + (0.05 * math.sin(t * 9) if r > 40 else 0.02 * math.sin(t * 12))
        g.append(f"<g transform='translate({ex},{cy:.1f}) scale({wob:.3f},{2 - wob:.3f})'>")
        if rev > 0:
            g.append(f"<circle r='{r * 1.5:.1f}' fill='url(#brillo)' opacity='{rev:.2f}'/>")
        g.append(f"<circle r='{r:.1f}' fill='#7fd6ff' fill-opacity='0.55' stroke='#1f7fb8' stroke-width='6'/>")
        # el ojo se ve agrandado dentro de la bola (efecto lupa)
        if r > 36:
            k = clamp((r - 36) / 40)
            g.append(f"<g opacity='{0.75 * k:.2f}' transform='translate(0,{ey - cy + 4:.1f}) scale(1.18)'>"
                     f"<circle r='26' fill='#4a2c1a'/><circle r='14' fill='#1a0f08'/><circle cx='-8' cy='-9' r='8' fill='#fff'/></g>")
        g.append(f"<ellipse cx='{-r * 0.38:.1f}' cy='{-r * 0.42:.1f}' rx='{r * 0.26:.1f}' ry='{r * 0.15:.1f}' fill='#fff' opacity='0.9' transform='rotate(-35 {-r * 0.38:.1f} {-r * 0.42:.1f})'/>")
        g.append(f"<circle cx='{r * 0.42:.1f}' cy='{r * 0.36:.1f}' r='{r * 0.08:.1f}' fill='#fff' opacity='0.8'/>")
        g.append("</g>")
    # una lagrimilla más pequeña en el otro ojo a partir de 5,5 s
    k2 = seg(t, 5.4, 7.6)
    if k2 > 0:
        ex, ey = EYE_R
        r2 = lerp(6, 26, k2)
        g.append(f"<circle cx='{ex + 6}' cy='{ey + 46 - 8 * k2:.1f}' r='{r2:.1f}' fill='#7fd6ff' fill-opacity='0.6' stroke='#1f7fb8' stroke-width='5'/>"
                 f"<circle cx='{ex + 6 - r2 * 0.35:.1f}' cy='{ey + 46 - 8 * k2 - r2 * 0.4:.1f}' r='{r2 * 0.22:.1f}' fill='#fff' opacity='0.9'/>")
    g.append("</g>")
    return "".join(g), (hx + dx, hy + dy)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)
    # radio de la lágrima: aparece a 3,6 s, crece despacio y en la revelación se hace una gran bola
    crece = 0.0
    if t >= 3.6:
        crece = lerp(8, 22, seg(t, 3.6, 5.0)) + lerp(0, 30, seg(t, 5.0, 7.3)) + lerp(0, 40, seg(t, 7.25, 7.9))
        crece += 6 * math.sin(math.pi * clamp((t - 7.25) / 0.7)) if t > 7.25 else 0
    defs = ("<radialGradient id='space' cx='0.5' cy='0.3' r='0.8'><stop offset='0' stop-color='#1d2a5a'/>"
            "<stop offset='1' stop-color='#070b1f'/></radialGradient>"
            "<radialGradient id='brillo'><stop offset='0' stop-color='#eaffff' stop-opacity='0.9'/>"
            "<stop offset='0.6' stop-color='#8fe3ff' stop-opacity='0.45'/><stop offset='1' stop-color='#5ec8ff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='0.85'/><stop offset='1' stop-color='#bfefff' stop-opacity='0'/></radialGradient>")
    astro, (ax, ay) = astronauta(t, crece, rev)
    ex, ey = ax + EYE_L[0], ay + EYE_L[1]
    cuerpo = [fondo(t, rev), flotantes(t), astro]
    # gotitas que flotan alrededor tras la revelación
    if rev > 0:
        for dxn, ph, rr in GOTITAS:
            a = ph + t * 0.8
            dist = lerp(60, 170 + 40 * dxn, rev)
            gx = ex + dist * math.cos(a); gy = ey + dist * math.sin(a) * 0.8
            cuerpo.append(f"<circle cx='{gx:.0f}' cy='{gy:.0f}' r='{rr * rev:.1f}' fill='#9fe2ff' fill-opacity='0.7' stroke='#1f7fb8' stroke-width='4'/>")
        # destellos
        for k in range(6):
            a = k * 60 + t * 50
            d = 150 + 15 * math.sin(t * 6 + k)
            sx = ex + d * math.cos(math.radians(a)); sy = ey + d * math.sin(math.radians(a))
            sc = rev * (0.6 + 0.4 * math.sin(t * 8 + k))
            cuerpo.append(f"<path transform='translate({sx:.0f},{sy:.0f}) scale({sc:.2f})' d='M0 -22 L6 -6 L22 0 L6 6 L0 22 L-6 6 L-22 0 L-6 -6 Z' fill='#fff7c2' stroke='{INK}' stroke-width='3'/>")
    # destello de luz en la revelación
    fl = clamp(1 - abs(t - REVELACION - 0.15) / 0.45)
    if fl > 0:
        cuerpo.append(f"<circle cx='{ex:.0f}' cy='{ey:.0f}' r='{lerp(200, 700, fl):.0f}' fill='url(#flash)' opacity='{fl:.2f}'/>")
    z = 1 + 0.22 * seg(t, REVELACION - 0.1, REVELACION + 1.2)
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{zoom(ex, ey, z, ''.join(cuerpo))}</svg>")
