"""2026-11-21-c1 · El colibrí puede volar hacia atrás.

0-2,3 s: el colibrí entra volando desde la izquierda hacia una flor roja.
2,3-5 s: se queda suspendido en el aire bebiendo néctar (alas a toda velocidad).
5-7,4 s: saca el pico poco a poco…
7,4 s (REVELACION): ¡sale disparado MARCHA ATRÁS! sin darse la vuelta: halo dorado,
líneas de velocidad, flecha curva y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.4
MUSICA = 6

rng = np.random.default_rng(21)
POLEN = [(rng.uniform(600, 1050), rng.uniform(1050, 1500), rng.uniform(4, 8), rng.uniform(0, 6.28)) for _ in range(26)]
CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(140, 330), rng.uniform(6, 13)) for _ in range(22)]
HIERBA = [(x, rng.uniform(40, 90), rng.uniform(0, 6.28)) for x in range(0, 1100, 34)]
FLORES = [(90, 1700, "#b07cff"), (300, 1790, "#ffd23f"), (980, 1730, "#ff8fc8"), (640, 1830, "#ffffff"), (840, 1860, "#b07cff")]


def bird_x(t):
    x = lerp(20, 514, seg(t, 0, 2.3))
    x -= 40 * seg(t, 5.2, 7.2)                  # saca el pico despacio
    x -= 180 * seg(t, 7.4, 8.1)                 # ¡marcha atrás!
    return x


def colibri(t):
    """Colibrí original mirando a la derecha: pico largo, garganta roja, lomo verde."""
    x = bird_x(t)
    y = 1310 + 12 * pulso(t, 0.9) + (-8 * seg(t, 7.4, 7.8) + 8 * seg(t, 7.8, 8.3))
    tilt = lerp(18, 0, seg(t, 1.6, 2.4)) - 8 * seg(t, 7.4, 7.7) + 8 * seg(t, 7.7, 8.4)
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    flap = math.sin(t * 2 * math.pi * 7.5)      # 4 fotogramas por aleteo
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({tilt:.1f}) scale(1.15)'>"]
    # sombra difusa de alas (borrón de velocidad)
    g.append(f"<path d='M-10 -30 Q-120 -230 30 -250 Q90 -170 -10 -30 Z' fill='#e9fbff' opacity='0.45'/>")
    g.append(f"<path d='M-10 -30 Q-170 -60 -150 80 Q-60 40 -10 -30 Z' fill='#e9fbff' opacity='0.30'/>")
    # cola en abanico
    g.append(f"<path d='M-70 20 L-200 40 L-205 75 L-195 105 L-70 50 Z' fill='#1f7a55' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-150 38 L-200 58 M-150 58 L-198 88' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    # ala trasera (más oscura)
    a2 = -60 + 55 * flap
    g.append(f"<g transform='translate(-5,-30) rotate({a2 + 10:.1f})'><path d='M0 0 Q-40 -110 -20 -205 Q30 -110 22 0 Z' fill='#7fd6b0' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # cuerpo
    g.append(f"<ellipse cx='0' cy='0' rx='100' ry='62' transform='rotate(-22)' fill='#2fbf71' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-60 30 Q0 75 70 20 Q40 0 -10 10 Z' fill='#f4f1e6'/>")
    # patitas recogidas
    g.append(f"<path d='M-5 58 l-8 20 M20 55 l-4 20' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # cabeza
    g.append(f"<circle cx='88' cy='-58' r='56' fill='#2fbf71' stroke='{INK}' stroke-width='{LW}'/>")
    # garganta roja iridiscente
    brillo = mix("#e8213f", "#ff6a3d", 0.5 + 0.5 * pulso(t, 0.8))
    g.append(f"<path d='M48 -20 Q95 10 138 -30 Q120 -5 100 -8 Q75 0 48 -20 Z' fill='{brillo}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # pico largo y fino
    g.append(f"<path d='M136 -66 L318 -54 L136 -46 Z' fill='#3a2a22' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # ojo
    g.append(f"<g transform='translate(100,-70) scale(1,{blink})'><circle r='22' fill='#fff' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='6' cy='1' r='12' fill='{INK}'/><circle cx='10' cy='-4' r='4.5' fill='#fff'/></g>")
    # ala delantera
    a1 = -55 + 60 * flap
    g.append(f"<g transform='translate(-15,-25) rotate({a1:.1f})'><path d='M0 0 Q-45 -120 -18 -225 Q36 -120 26 0 Z' fill='#a6f0cf' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M8 -20 Q-10 -110 -10 -180' stroke='#5fbf98' stroke-width='5' fill='none' stroke-linecap='round'/></g>")
    g.append("</g>")
    return "".join(g), x, y


def flor(t):
    """Flor roja en forma de trompeta, abierta hacia la izquierda, sobre un tallo."""
    sw = 2.5 * pulso(t, 2.6) + 4 * seg(t, 7.4, 7.7) * (1 - seg(t, 7.7, 8.6)) * pulso(t, 0.25)
    g = [f"<g transform='translate(90,35) rotate({sw:.2f},900,1800)'>"]
    g.append(f"<path d='M900 1800 Q930 1500 880 1300 Q860 1240 890 1200' fill='none' stroke='{INK}' stroke-width='24' stroke-linecap='round'/>")
    g.append(f"<path d='M900 1800 Q930 1500 880 1300 Q860 1240 890 1200' fill='none' stroke='#3fae4a' stroke-width='12' stroke-linecap='round'/>")
    for lx, ly, s in ((905, 1520, 1), (890, 1380, -1)):
        g.append(f"<path d='M{lx} {ly} q{110*s} -70 {170*s} -20 q-{60*s} 70 -{170*s} 20 Z' fill='#56c95f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # trompeta
    g.append(f"<path d='M900 1215 L795 1170 Q770 1210 798 1258 Z' fill='#ff3b4e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M806 1160 Q760 1145 760 1180 Q740 1215 765 1245 Q770 1285 812 1268 Q790 1215 806 1160 Z' fill='#ff6b78' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='790' cy='1214' rx='16' ry='40' fill='#8a1022'/>")
    g.append(f"<path d='M900 1215 q25 -20 40 -5 q-15 25 -40 5' fill='#2f8f3a' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.4, 8.1)
    top = mix("#6cc8ff", "#ffc46e", rev); mid = mix("#b8ecff", "#ffe7a8", rev); low = mix("#e8fbff", "#fff6dc", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff6c8' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffd24a' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ffb000' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sol'><stop offset='0' stop-color='#fffbe0'/><stop offset='1' stop-color='#ffe98a' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # Sol suave arriba a la derecha y nubes que pasan
    s.append(f"<circle cx='900' cy='360' r='230' fill='url(#sol)' opacity='0.8'/>")
    s.append(f"<circle cx='900' cy='360' r='80' fill='#fff3a8' stroke='#ffd04a' stroke-width='8'/>")
    for i, (cx, cy, sc, sp) in enumerate([(150, 620, 1.3, 18), (700, 820, 1.0, 12), (380, 300, 0.9, 9)]):
        dx = ((cx + t * sp) % 1400) - 200
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})'><path d='M0 50 Q10 0 70 10 Q100 -35 160 0 Q220 -10 235 50 Z' "
                 f"fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='0.95'/></g>")
    z = 1 + 0.10 * seg(t, 7.4, 8.2) + 0.03 * seg(t, 8.2, 10)
    w = []
    # colinas
    w.append(f"<path d='M0 1360 Q250 1270 520 1340 T1080 1310 L1080 1920 L0 1920 Z' fill='#8fd86b' stroke='{INK}' stroke-width='{LW}'/>")
    w.append(f"<path d='M0 1500 Q300 1430 620 1490 T1080 1470 L1080 1920 L0 1920 Z' fill='#63c255' stroke='{INK}' stroke-width='{LW}'/>")
    # arbustos al fondo
    for bx, by, br in ((120, 1400, 90), (250, 1420, 70), (1010, 1380, 85)):
        w.append(f"<circle cx='{bx}' cy='{by}' r='{br}' fill='#3f9e4a' stroke='{INK}' stroke-width='7'/>")
    w.append(f"<path d='M0 1660 Q300 1610 640 1650 T1080 1640 L1080 1920 L0 1920 Z' fill='#4aa84a' stroke='{INK}' stroke-width='{LW}'/>")
    # flores pequeñas del prado
    for fx, fy, c in FLORES:
        bal = 6 * pulso(t, 2.0, fx / 300)
        w.append(f"<g transform='translate({fx},{fy}) rotate({bal:.1f})'><line x1='0' y1='0' x2='0' y2='90' stroke='{INK}' stroke-width='8'/>"
                 + "".join(f"<circle cx='{28*math.cos(a):.0f}' cy='{28*math.sin(a):.0f}' r='20' fill='{c}' stroke='{INK}' stroke-width='5'/>" for a in np.linspace(0, 6.28, 6, endpoint=False))
                 + f"<circle r='16' fill='#ffb000' stroke='{INK}' stroke-width='5'/></g>")
    w.append(flor(t))
    # hierba que se mece
    for hx, hh, ph in HIERBA:
        b = 10 * math.sin(t * 2.2 + ph)
        w.append(f"<path d='M{hx} 1920 Q{hx + b/2:.0f} {1920 - hh/2:.0f} {hx + b:.0f} {1920 - hh:.0f}' stroke='#2f8a3a' stroke-width='10' fill='none' stroke-linecap='round'/>")
    # polen flotando cerca de la flor
    for px, py, pr, ph in POLEN:
        yy = py - (t * 25) % 200 + 20 * math.sin(t + ph)
        w.append(f"<circle cx='{px + 15*math.sin(t*1.3 + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fff2a0' opacity='{0.4 + 0.3*math.sin(t*3+ph):.2f}'/>")
    ave, bx, by = colibri(t)
    # halo dorado detrás del colibrí en la revelación
    if rev > 0:
        w.append(f"<circle cx='{bx + 70:.0f}' cy='{by - 70:.0f}' r='{lerp(120, 420, rev):.0f}' fill='url(#halo)'/>")
    # líneas de velocidad (quedan a la derecha: se mueve hacia la izquierda)
    vel = seg(t, 7.4, 7.6) * (1 - seg(t, 8.2, 8.8))
    if vel > 0:
        for i, (dy, ln) in enumerate(((-150, 220), (-80, 300), (-10, 260), (60, 200))):
            x0 = bx + 390 + 20 * i
            w.append(f"<line x1='{x0:.0f}' y1='{by + dy:.0f}' x2='{x0 + ln*vel:.0f}' y2='{by + dy:.0f}' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='{0.9*vel:.2f}'/>")
            w.append(f"<line x1='{x0:.0f}' y1='{by + dy:.0f}' x2='{x0 + ln*vel:.0f}' y2='{by + dy:.0f}' stroke='{INK}' stroke-width='4' stroke-linecap='round' opacity='{0.5*vel:.2f}'/>")
    w.append(ave)
    # flecha curva que señala "hacia atrás" (por debajo del colibrí)
    fa = seg(t, 7.5, 8.0)
    if fa > 0:
        sc = 0.6 + 0.4 * fa
        w.append(f"<g transform='translate({bx + 150:.0f},{by + 190:.0f}) scale({sc:.3f})' opacity='{fa:.2f}'>"
                 f"<path d='M230 -20 Q120 70 -90 20' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
                 f"<path d='M230 -20 Q120 70 -90 20' fill='none' stroke='#ffd23f' stroke-width='20' stroke-linecap='round'/>"
                 f"<path d='M-140 5 L-60 -40 L-70 60 Z' fill='#ffd23f' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/></g>")
    # chispas de la revelación
    ch = seg(t, 7.4, 7.9)
    if ch > 0:
        for ang, rr, cr in CHISPAS:
            r2 = rr * (0.6 + 0.6 * ch) + 20 * math.sin(t * 4 + ang)
            op = ch * (0.6 + 0.4 * math.sin(t * 6 + ang))
            w.append(f"<circle cx='{bx + 60 + r2*math.cos(ang):.0f}' cy='{by - 60 + r2*math.sin(ang)*0.8:.0f}' r='{cr:.1f}' fill='#fff7c0' stroke='#ffb000' stroke-width='3' opacity='{op:.2f}'/>")
    s.append(zoom(260, 1300, z, "".join(w)))
    s.append("</svg>")
    return "".join(s)
