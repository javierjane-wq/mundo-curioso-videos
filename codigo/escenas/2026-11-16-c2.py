"""2026-11-16-c2 · El despertador de 1787 que solo sonaba a las 4 de la madrugada (Levi Hutchins).

Un despertador de campanas con cara llega a la mesilla de noche, junto a una vela y bajo una
ventana con la Luna. Intentan mover sus agujas, pero vuelven a su sitio; el minutero se acerca a
las 4:00 y, en la REVELACION, el reloj suena: campanas temblando, ondas de sonido, la habitación
se ilumina y la cámara se acerca a la esfera.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.45   # el minutero llega a las 4:00 y el despertador suena: golpe musical
MUSICA = 2

rng = np.random.default_rng(16)
STARS = [(rng.uniform(150, 930), rng.uniform(180, 820), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(34)]
MOTAS = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 6), rng.uniform(15, 40)) for _ in range(26)]

CX, CY = 540, 1390      # centro de la esfera del reloj


def ang_agujas(t):
    """Ángulos (grados desde las 12, sentido horario) de minutero y horario."""
    base_min = 300.0                     # 3:50
    # 2,6-4,9 s: alguien gira la llave, las agujas avanzan deprisa... y vuelven solas a su sitio
    ida = seg(t, 2.7, 3.7); vuelta = seg(t, 4.0, 4.7)
    extra = 900 * ida * (1 - vuelta)
    wob = 10 * math.sin((t - 4.7) * 18) * math.exp(-(t - 4.7) * 5) if t > 4.7 else 0
    # 5-7,45 s: el minutero avanza de las 3:50 a las 4:00
    avance = 60 * seg(t, 5.0, REVELACION)
    m = base_min + extra + avance + wob
    h = 90 + m / 12.0                    # el horario avanza 1/12 de lo que avanza el minutero
    return m, h


def despertador(t):
    ring = t >= REVELACION
    # entrada desde la derecha con saltitos (0-1,8 s)
    ent = seg(t, 0, 1.8)
    x = lerp(980, CX, ent)
    salto = abs(math.sin(t * 7)) * 46 * (1 - ent) if t < 1.8 else 0
    temblor = 0.0
    if 5.0 < t < REVELACION:
        temblor = 4 * seg(t, 5.0, REVELACION) * math.sin(t * 60)
    if ring:
        temblor = 10 * math.sin(t * 90)
        salto = abs(math.sin(t * 24)) * 22
    sacude = 0.0
    if 4.7 < t < 5.6:                     # "no" con la cabeza tras volver las agujas
        sacude = 7 * math.sin((t - 4.7) * 16) * (1 - seg(t, 4.7, 5.6))
    inclin = lerp(-10, 0, ent) + sacude + (3 * math.sin(t * 70) if ring else 0)
    g = [f"<g transform='translate({x + temblor:.1f},{CY - salto:.1f}) rotate({inclin:.2f})'>"]
    # patas
    for sx in (-1, 1):
        g.append(f"<path d='M{sx*110} 150 L{sx*150} 250' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
                 f"<path d='M{sx*110} 150 L{sx*150} 250' stroke='#ffcc3a' stroke-width='18' stroke-linecap='round'/>")
    # campanas y martillo
    camp = 9 * math.sin(t * 95) if ring else 1.5 * math.sin(t * 2.5)
    for sx in (-1, 1):
        rot = sx * 32 + (camp if sx < 0 else -camp)
        g.append(f"<g transform='translate({sx*118},-150) rotate({rot:.1f})'>"
                 f"<path d='M-78 18 Q-80 -72 0 -78 Q80 -72 78 18 Z' fill='#ffcc3a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M-50 -10 Q-46 -52 -8 -58' fill='none' stroke='#fff3b0' stroke-width='12' stroke-linecap='round'/>"
                 f"<rect x='-90' y='12' width='180' height='18' rx='9' fill='#e0a91c' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='0' cy='-86' r='12' fill='#e0a91c' stroke='{INK}' stroke-width='6'/></g>")
    mart = 26 * math.sin(t * 95) if ring else 0
    g.append(f"<g transform='translate(0,-178) rotate({mart:.1f})'>"
             f"<line x1='0' y1='0' x2='0' y2='-70' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
             f"<circle cx='0' cy='-76' r='16' fill='#ffcc3a' stroke='{INK}' stroke-width='6'/></g>")
    # asa de arriba
    g.append(f"<path d='M-70 -196 Q0 -262 70 -196' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>"
             f"<path d='M-70 -196 Q0 -262 70 -196' fill='none' stroke='#ffcc3a' stroke-width='12' stroke-linecap='round'/>")
    # llave de cuerda (lado izquierdo), gira cuando intentan cambiar la hora
    llave = lerp(0, 540, seg(t, 2.6, 3.8))
    g.append(f"<g transform='translate(-212,30)'><rect x='-30' y='-9' width='34' height='18' fill='#e0a91c' stroke='{INK}' stroke-width='6'/>"
             f"<g transform='translate(-36,0) scale(1,{math.cos(math.radians(llave)):.3f})'>"
             f"<path d='M0 0 L-28 -36 Q-46 -50 -54 -30 L-44 0 L-54 30 Q-46 50 -28 36 Z' fill='#ffcc3a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g></g>")
    # caja (cuerpo rojo)
    g.append(f"<circle r='210' fill='#e8463c' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-150 -120 A190 190 0 0 1 60 -190' fill='none' stroke='#ff8a73' stroke-width='16' stroke-linecap='round'/>")
    # esfera
    brillo = seg(t, REVELACION, REVELACION + 0.4)
    g.append(f"<circle r='168' fill='{mix('#fff6e0', '#fffbd0', brillo)}' stroke='{INK}' stroke-width='8'/>")
    for i in range(12):
        a = math.radians(i * 30)
        r1 = 132 if i % 3 else 120
        g.append(f"<line x1='{150*math.sin(a):.1f}' y1='{-150*math.cos(a):.1f}' x2='{r1*math.sin(a):.1f}' y2='{-r1*math.cos(a):.1f}' "
                 f"stroke='{INK}' stroke-width='{10 if i % 3 == 0 else 6}' stroke-linecap='round'/>")
    # ojos (arriba de la esfera) con parpadeo; se abren mucho al acercarse las 4
    asombro = seg(t, 5.6, 7.0)
    abre = 1.0 if (t % 2.7) > 0.13 else 0.12
    if t < 0.4: abre = 0.12          # se despierta al llegar
    if ring: abre = 1.0
    rojo = 1 + 0.25 * asombro + 0.15 * brillo
    for ex in (-62, 62):
        g.append(f"<g transform='translate({ex},-58) scale(1,{abre:.2f})'>"
                 f"<ellipse rx='{28*rojo:.1f}' ry='{32*rojo:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{4 if ex < 0 else -4}' cy='4' r='{15*rojo:.1f}' fill='{INK}'/>"
                 f"<circle cx='{-2 if ex < 0 else -10}' cy='-4' r='6' fill='#fff'/></g>")
    # boca: sonrisa -> "o" de asombro -> grito abierto al sonar
    if ring:
        g.append(f"<ellipse cx='0' cy='88' rx='38' ry='30' fill='#7a1f1a' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='0' cy='100' rx='20' ry='10' fill='#ff7a7a'/>")
    elif asombro > 0.2:
        rr = lerp(10, 18, asombro)
        g.append(f"<ellipse cx='0' cy='90' rx='{rr:.1f}' ry='{rr*1.2:.1f}' fill='#7a1f1a' stroke='{INK}' stroke-width='6'/>")
    else:
        g.append(f"<path d='M-30 82 Q0 108 30 82' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # mofletes
    for ex in (-108, 108):
        g.append(f"<ellipse cx='{ex}' cy='40' rx='20' ry='12' fill='#ff9aa0' opacity='0.8'/>")
    # agujas
    m, h = ang_agujas(t)
    g.append(f"<g transform='rotate({h:.2f})'><path d='M-9 12 L-7 -82 L0 -96 L7 -82 L9 12 Z' fill='{INK}'/></g>")
    g.append(f"<g transform='rotate({m:.2f})'><path d='M-6 14 L-5 -122 L0 -138 L5 -122 L6 14 Z' fill='{INK}'/></g>")
    g.append(f"<circle r='14' fill='#ffcc3a' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def ondas(t):
    """Ondas de sonido saliendo de las campanas al sonar."""
    if t < REVELACION: return ""
    s = []
    for k in range(5):
        p = ((t - REVELACION) * 1.6 + k / 5) % 1.0
        r = lerp(250, 560, p); op = (1 - p) * 0.9
        for sx in (-1, 1):
            a0, a1 = (math.radians(-150), math.radians(-100)) if sx < 0 else (math.radians(-80), math.radians(-30))
            x0, y0 = CX + r * math.cos(a0), CY - 150 + r * math.sin(a0)
            x1, y1 = CX + r * math.cos(a1), CY - 150 + r * math.sin(a1)
            s.append(f"<path d='M{x0:.0f} {y0:.0f} A{r:.0f} {r:.0f} 0 0 1 {x1:.0f} {y1:.0f}' fill='none' stroke='#fff3a0' "
                     f"stroke-width='16' stroke-linecap='round' opacity='{op:.2f}'/>")
    return "".join(s)


def frame(t):
    rv = seg(t, REVELACION, REVELACION + 0.5)
    pared = mix("#2f3a6b", "#f0a94a", rv)
    pared2 = mix("#28325e", "#e2913a", rv)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         "<linearGradient id='noche' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0d1640'/><stop offset='1' stop-color='#2b3f8a'/></linearGradient>",
         f"<radialGradient id='vela'><stop offset='0' stop-color='#ffdf8a' stop-opacity='0.55'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='estallido'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95*rv:.3f}'/>"
         f"<stop offset='0.45' stop-color='#ffd95a' stop-opacity='{0.75*rv:.3f}'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='{pared}'/>"]
    z = 1 + 0.22 * seg(t, REVELACION, REVELACION + 1.6)
    s.append(f"<g transform='translate({CX},{CY}) scale({z:.4f}) translate({-CX},{-CY})'>")
    # papel pintado: rayas verticales suaves
    for xx in range(0, W + 1, 120):
        s.append(f"<rect x='{xx}' y='0' width='60' height='1640' fill='{pared2}'/>")
    # ventana con la noche, la Luna y estrellas
    s.append(f"<rect x='130' y='160' width='820' height='690' rx='30' fill='url(#noche)' stroke='{INK}' stroke-width='{LW}'/>")
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.55 * abs(math.sin(t * 2.2 + ph))
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff8d8' opacity='{a:.2f}'/>")
    mx = 760 - 12 * t
    s.append(f"<circle cx='{mx:.0f}' cy='330' r='78' fill='#fff1b8' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='{mx+30:.0f}' cy='305' r='60' fill='#1a2a6a'/>")
    for i, (nx, ny) in enumerate([(260, 560), (640, 690)]):
        dx = (t * 18 * (1 + 0.4 * i)) % 240 - 60
        s.append(f"<path d='M{nx+dx:.0f} {ny} q30 -40 75 -10 q35 -30 70 5 q30 0 30 30 h-175 z' fill='#4a5aa0' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='0.9'/>")
    s.append(f"<line x1='540' y1='160' x2='540' y2='850' stroke='{INK}' stroke-width='{LW}'/>"
             f"<line x1='130' y1='505' x2='950' y2='505' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='110' y='840' width='860' height='34' rx='10' fill='#c98a4b' stroke='{INK}' stroke-width='{LW}'/>")
    # cortinas que se mecen
    for sx in (-1, 1):
        bx = 130 if sx < 0 else 950
        sw = 14 * math.sin(t * 1.6 + (0 if sx < 0 else 1.3))
        tip = bx - sx * 120 + sw
        s.append(f"<path d='M{bx - sx*30} 120 L{bx + sx*95} 120 L{bx + sx*95 + sw*0.4:.0f} 960 Q{bx + sx*20} 990 {tip:.0f} 950 Q{bx - sx*60 + sw:.0f} 560 {bx - sx*30} 120 Z' "
                 f"fill='#b84a7a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<rect x='60' y='104' width='960' height='30' rx='15' fill='#8a5530' stroke='{INK}' stroke-width='{LW}'/>")
    # cuadro de un barco no; zócalo y suelo
    s.append(f"<rect x='0' y='1640' width='{W}' height='280' fill='{mix('#3d2a3e', '#a8653a', rv)}'/>")
    # brillo del estallido detrás del reloj y rayos
    if rv > 0:
        s.append(f"<circle cx='{CX}' cy='{CY}' r='{lerp(200, 760, rv):.0f}' fill='url(#estallido)'/>")
        for i in range(14):
            a = math.radians(i * 360 / 14 + (t - REVELACION) * 30)
            r0, r1 = 260, 260 + 420 * rv
            a2 = a + math.radians(7)
            s.append(f"<path d='M{CX + r0*math.cos(a):.0f} {CY + r0*math.sin(a):.0f} L{CX + r1*math.cos(a):.0f} {CY + r1*math.sin(a):.0f} "
                     f"L{CX + r1*math.cos(a2):.0f} {CY + r1*math.sin(a2):.0f} Z' fill='#fff6b0' opacity='{0.5*rv:.2f}'/>")
    # mesilla de noche
    s.append(f"<rect x='90' y='1640' width='900' height='300' rx='18' fill='#a0623a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='60' y='1610' width='960' height='54' rx='16' fill='#c27a48' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='170' y='1720' width='740' height='160' rx='14' fill='#b06e42' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='540' cy='1800' r='20' fill='#ffcc3a' stroke='{INK}' stroke-width='6'/>")
    # vela con llama que tiembla
    vx, vy = 175, 1610
    fl = 1 + 0.12 * math.sin(t * 13) + 0.06 * math.sin(t * 31)
    s.append(f"<circle cx='{vx}' cy='{vy-190}' r='{150*fl:.0f}' fill='url(#vela)'/>")
    s.append(f"<ellipse cx='{vx}' cy='{vy-6}' rx='70' ry='18' fill='#d9c3a0' stroke='{INK}' stroke-width='7'/>"
             f"<rect x='{vx-32}' y='{vy-150}' width='64' height='140' rx='10' fill='#fff4dc' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M{vx-32} {vy-130} q16 22 30 0' fill='none' stroke='#e8d6b0' stroke-width='8'/>"
             f"<line x1='{vx}' y1='{vy-150}' x2='{vx}' y2='{vy-170}' stroke='{INK}' stroke-width='6'/>"
             f"<g transform='translate({vx},{vy-172}) scale({fl:.3f},{fl:.3f}) rotate({6*math.sin(t*5):.1f})'>"
             f"<path d='M0 0 Q-22 -26 0 -70 Q22 -26 0 0 Z' fill='#ffb52e' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M0 -6 Q-9 -22 0 -40 Q9 -22 0 -6 Z' fill='#fff3a0'/></g>")
    # sombra del reloj
    s.append(f"<ellipse cx='{CX}' cy='1630' rx='190' ry='18' fill='#000' opacity='0.25'/>")
    s.append(ondas(t))
    s.append(despertador(t))
    # motas de polvo que flotan a la luz de la vela
    for px, py, pr, sp in MOTAS:
        yy = (py - t * sp) % 900 + 1000
        s.append(f"<circle cx='{px + 15*math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#ffe9b0' opacity='0.45'/>")
    s.append("</g></svg>")
    return "".join(s)
