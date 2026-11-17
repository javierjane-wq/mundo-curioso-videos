"""La Torre Eiffel cambia de altura: con el calor del verano su hierro se dilata y la torre crece unos
centímetros (y en invierno, con el frío, encoge). Dilatación térmica (toureiffel.paris).

Composición: torre de hierro (dibujo propio, con cara) en la mitad de abajo sobre el césped, tejados de
París detrás, poste de medir a la izquierda con una línea discontinua a la altura de invierno y un
termómetro a la derecha. 0-2,5 s invierno con nieve; 2,5-5 s sale el Sol y se derrite la nieve;
5-7,5 s calor (ondas, sudor, el termómetro sube); en la REVELACION la torre se estira por encima de la
línea, brilla y la cámara se acerca a la punta.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso

DUR = 10.0
REVELACION = 7.5   # la torre se estira: golpe musical
MUSICA = 2

rng = np.random.default_rng(1117)
SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(5, 11), rng.uniform(60, 140), rng.uniform(0, 6.28)) for _ in range(90)]
CLOUDS = [(160, 330, 1.2, 10), (820, 190, 0.9, 7), (560, 640, 1.4, 12), (980, 520, 0.8, 8), (60, 850, 1.0, 9)]
SPARK = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28)) for _ in range(24)]
HEAT = [(rng.uniform(80, 1000), rng.uniform(0, 1), rng.uniform(0.6, 1.2)) for _ in range(14)]

TX, TY = 560, 1795          # base de la torre
TH = 760                    # altura del cuerpo de la torre (sin antena)
TS = 0.92                   # escala general de la torre
TIP = 843                   # de la base a la bola de la antena
REF_Y = TY - TIP * TS * 0.985   # punta en invierno (línea discontinua)


def nube(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M-110 30 Q-120 -10 -70 -12 Q-60 -55 -10 -45 Q20 -80 65 -45 Q115 -50 110 0 Q140 15 115 30 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


# --- silueta de la torre (coordenadas locales: base en 0,0; arriba y negativa) ---
SEC1 = "M-250 0 Q-150 -105 -128 -230 L128 -230 Q150 -105 250 0 L150 0 C140 -150 -140 -150 -150 0 Z"
SEC2 = "M-112 -250 Q-80 -340 -60 -420 L60 -420 Q80 -340 112 -250 L50 -250 Q0 -305 -50 -250 Z"
SEC3 = "M-50 -436 Q-26 -590 -13 -722 L13 -722 Q26 -590 50 -436 Z"


def torre(t, stretch, heat, rev):
    col = mix(mix("#7b6f86", "#a8643c", seg(t, 2.6, 5.0)), "#e07434", heat * 0.6 + rev * 0.3)
    dark = mix(col, "#2a1a14", 0.35)
    light = mix(col, "#ffffff", 0.25)
    # escalón de entrada desde el fotograma 0 y temblor de frío
    ent = ease(t / 0.8)
    sc = lerp(0.75, 1.0, ent) + 0.07 * math.sin(math.pi * clamp(t / 0.8)) * (1 - clamp((t - 0.8) / 0.4))
    shiver = 3.5 * math.sin(t * 55) * (1 - seg(t, 2.0, 3.2))
    sway = 1.2 * math.sin(t * 1.7)
    g = [f"<g transform='translate({TX + shiver:.1f},{TY}) rotate({sway:.2f}) scale({sc * TS:.4f},{sc * TS * stretch:.4f})'>"]
    g.append("<defs><clipPath id='tc'>" + f"<path d='{SEC1}'/><path d='{SEC2}'/><path d='{SEC3}'/>" + "</clipPath></defs>")
    for d in (SEC1, SEC2, SEC3):
        g.append(f"<path d='{d}' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # celosía de hierro (recortada por la silueta)
    lat = ["<g clip-path='url(#tc)'>"]
    for k in range(-30, 30):
        x = k * 38
        lat.append(f"<line x1='{x}' y1='0' x2='{x + 800}' y2='-800' stroke='{dark}' stroke-width='3.5' opacity='0.55'/>")
        lat.append(f"<line x1='{x}' y1='0' x2='{x - 800}' y2='-800' stroke='{dark}' stroke-width='3.5' opacity='0.55'/>")
    for yy in range(-40, -720, -60):
        lat.append(f"<line x1='-300' y1='{yy}' x2='300' y2='{yy}' stroke='{dark}' stroke-width='5' opacity='0.6'/>")
    lat.append("</g>")
    g.append("".join(lat))
    # brillo en el borde izquierdo
    g.append(f"<path d='M-228 -12 Q-148 -110 -122 -222' fill='none' stroke='{light}' stroke-width='7' stroke-linecap='round' opacity='0.8'/>")
    g.append(f"<path d='M-100 -262 Q-74 -340 -56 -410' fill='none' stroke='{light}' stroke-width='6' stroke-linecap='round' opacity='0.8'/>")
    # redibujar contornos encima de la celosía
    for d in (SEC1, SEC2, SEC3):
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # plataformas
    g.append(f"<rect x='-162' y='-254' width='324' height='28' rx='6' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>")
    for px in range(-150, 160, 30):
        g.append(f"<line x1='{px}' y1='-252' x2='{px}' y2='-230' stroke='{light}' stroke-width='4' opacity='0.7'/>")
    g.append(f"<rect x='-78' y='-440' width='156' height='22' rx='5' fill='{dark}' stroke='{INK}' stroke-width='{LW}'/>")
    # cabina de la cima y antena
    g.append(f"<rect x='-22' y='-752' width='44' height='34' rx='8' fill='{dark}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<line x1='0' y1='-752' x2='0' y2='-828' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<circle cx='0' cy='-834' r='9' fill='{mix('#ff6b5a', '#fff27a', rev)}' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    # cara (sin estirar, siguiendo la altura de la sección 2)
    fy = TY + (-338) * sc * TS * stretch
    fx = TX + shiver
    blink = 0.12 if (t % 2.9) < 0.13 else 1.0
    es = (1 + 0.3 * rev) * sc
    f = [f"<g transform='translate({fx:.1f},{fy:.1f}) scale({sc * TS:.4f})'>"]
    f.append(f"<ellipse cx='0' cy='4' rx='84' ry='62' fill='{col}' opacity='0.9'/>")
    for ex in (-34, 34):
        f.append(f"<g transform='translate({ex},-10) scale({1 + 0.3 * rev:.3f},{(1 + 0.3 * rev) * blink:.3f})'>"
                 f"<ellipse rx='22' ry='26' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='2' cy='{4 - 6 * rev:.1f}' r='11' fill='{INK}'/><circle cx='-3' cy='{-1 - 6 * rev:.1f}' r='4' fill='#fff'/></g>")
    # cejas: preocupadas con frío, relajadas con calor
    cej = lerp(8, -4, seg(t, 2.6, 4.5)) - 6 * rev
    f.append(f"<path d='M-54 {-44 + cej:.0f} L-18 {-48:.0f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    f.append(f"<path d='M54 {-44 + cej:.0f} L18 {-48:.0f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # boca: tiritando (ondulada) -> sonrisa -> "¡oh!" de sorpresa
    if t < 2.6:
        f.append(f"<path d='M-20 28 Q-13 22 -6 28 Q1 34 8 28 Q15 22 22 28' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    elif rev < 0.3:
        f.append(f"<path d='M-20 24 Q0 40 20 24' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    else:
        f.append(f"<ellipse cx='0' cy='32' rx='{10 + 6 * rev:.1f}' ry='{11 + 7 * rev:.1f}' fill='#7a2a2a' stroke='{INK}' stroke-width='5'/>")
    # mejillas: azules con frío, rosas con calor
    ch = mix("#8fc3ff", "#ff7f7f", seg(t, 2.6, 4.5))
    for cx in (-58, 58):
        f.append(f"<ellipse cx='{cx}' cy='18' rx='13' ry='8' fill='{ch}' opacity='0.8'/>")
    # gotas de sudor con el calor
    if heat > 0.05:
        for i, (dx, ph) in enumerate(((72, 0.0), (-76, 0.5))):
            k = ((t * 0.9 + ph) % 1.0)
            f.append(f"<path d='M{dx} {-30 + 50 * k:.0f} q-9 14 0 20 q9 -6 0 -20 Z' fill='#9fe0ff' stroke='{INK}' stroke-width='3.5' opacity='{heat * (1 - k):.2f}'/>")
    f.append("</g>")
    return "".join(g) + "".join(f)


def poste(t, rev):
    """Poste de medir a rayas (sin números) y línea discontinua a la altura de invierno."""
    x = 150
    g = [f"<rect x='{x - 22}' y='{REF_Y - 120}' width='44' height='{TY - REF_Y + 120}' rx='10' fill='#ffffff' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, yy in enumerate(range(int(REF_Y - 120), TY, 60)):
        if i % 2 == 0:
            g.append(f"<rect x='{x - 18}' y='{yy + 4}' width='36' height='56' fill='#ff5a5f'/>")
    for yy in range(int(REF_Y - 120), TY, 30):
        g.append(f"<line x1='{x - 22}' y1='{yy}' x2='{x - 6}' y2='{yy}' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<rect x='{x - 22}' y='{REF_Y - 120}' width='44' height='{TY - REF_Y + 120}' rx='10' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # línea de invierno
    lc = mix("#5aa9ff", "#ffffff", 0.2)
    g.append(f"<line x1='{x + 22}' y1='{REF_Y}' x2='{TX - 16}' y2='{REF_Y}' stroke='{INK}' stroke-width='11' stroke-dasharray='26 16' stroke-linecap='round'/>")
    g.append(f"<line x1='{x + 22}' y1='{REF_Y}' x2='{TX - 16}' y2='{REF_Y}' stroke='{lc}' stroke-width='5' stroke-dasharray='26 16' stroke-linecap='round'/>")
    g.append(f"<path d='M{x + 22} {REF_Y - 16} l-28 16 l28 16 Z' fill='{lc}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return "".join(g)


def flecha(t, top_y):
    """Flecha amarilla que aparece en la revelación entre la línea y la nueva punta."""
    a = seg(t, REVELACION, REVELACION + 0.4)
    if a <= 0:
        return ""
    bob = 8 * math.sin(t * 8)
    x = TX + 105
    y0, y1 = REF_Y + 60, top_y - 4 + bob
    sc = 1 + 0.25 * math.sin(math.pi * clamp((t - REVELACION) / 0.4))
    return (f"<g opacity='{a:.2f}' transform='translate({x},{(y0 + y1) / 2:.0f}) scale({sc:.3f}) translate({-x},{-(y0 + y1) / 2:.0f})'>"
            f"<path d='M{x - 16} {y0} L{x - 16} {y1 + 40} L{x - 40} {y1 + 40} L{x} {y1} L{x + 40} {y1 + 40} L{x + 16} {y1 + 40} L{x + 16} {y0} Z' "
            f"fill='#ffd23f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def termometro(t, heat):
    x, yb = 960, 1700
    lvl = lerp(0.12, 0.92, seg(t, 2.4, 7.6))
    top, bot = 1380, yb - 40
    hy = lerp(bot, top + 20, lvl)
    rojo = mix("#5aa9ff", "#ff3b30", seg(t, 2.4, 5.5))
    wob = 2 * math.sin(t * 3)
    return (f"<g transform='rotate({wob:.2f},{x},{yb})'>"
            f"<rect x='{x - 26}' y='{top}' width='52' height='{bot - top + 20}' rx='26' fill='#ffffff' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='{x - 11}' y='{hy:.0f}' width='22' height='{bot - hy + 20:.0f}' rx='8' fill='{rojo}'/>"
            + "".join(f"<line x1='{x + 26}' y1='{yy}' x2='{x + 42}' y2='{yy}' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>" for yy in range(top + 40, bot, 50))
            + f"<circle cx='{x}' cy='{yb}' r='44' fill='{rojo}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='{x - 14}' cy='{yb - 14}' r='10' fill='#ffffff' opacity='0.6'/>"
            f"<rect x='{x - 66}' y='{yb + 36}' width='132' height='22' rx='8' fill='#8d6e63' stroke='{INK}' stroke-width='6'/></g>")


def tejados(day):
    g = []
    wall = mix("#9aa6c4", "#f3dcb4", day); roof = mix("#56617f", "#6d7ea3", day); win = mix("#cfe0f5", "#ffe9a8", day)
    xs = [(-20, 150, 1505), (125, 140, 1540), (255, 160, 1490), (400, 130, 1530), (520, 150, 1500),
          (660, 140, 1525), (790, 150, 1495), (930, 170, 1520)]
    for x, w, top in xs:
        g.append(f"<rect x='{x}' y='{top}' width='{w}' height='{1720 - top}' fill='{wall}' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<path d='M{x - 6} {top} L{x + 18} {top - 46} L{x + w - 18} {top - 46} L{x + w + 6} {top} Z' fill='{roof}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        g.append(f"<rect x='{x + w * 0.62:.0f}' y='{top - 72}' width='20' height='30' fill='#c0705a' stroke='{INK}' stroke-width='5'/>")
        for wx in range(x + 18, x + w - 30, 42):
            g.append(f"<rect x='{wx}' y='{top + 22}' width='22' height='34' rx='4' fill='{win}' stroke='{INK}' stroke-width='4'/>")
            g.append(f"<rect x='{wx}' y='{top + 80}' width='22' height='34' rx='4' fill='{win}' stroke='{INK}' stroke-width='4'/>")
    return "".join(g)


def arbol(x, y, sc, day, snow):
    leaf = mix("#3f7f5a", "#4fbf5a", day); leaf2 = mix("#356b4d", "#3ea24c", day)
    s = (f"<g transform='translate({x},{y}) scale({sc})'>"
         f"<rect x='-14' y='-60' width='28' height='80' fill='#8a5a3b' stroke='{INK}' stroke-width='6'/>"
         f"<circle cx='0' cy='-110' r='72' fill='{leaf}' stroke='{INK}' stroke-width='7'/>"
         f"<circle cx='-38' cy='-80' r='44' fill='{leaf2}' stroke='{INK}' stroke-width='6'/>"
         f"<circle cx='40' cy='-84' r='40' fill='{leaf2}' stroke='{INK}' stroke-width='6'/>")
    if snow > 0.02:
        s += f"<path d='M-62 -140 Q-40 -190 0 -184 Q44 -190 62 -140 Q30 -158 0 -150 Q-30 -160 -62 -140 Z' fill='#ffffff' stroke='{INK}' stroke-width='5' opacity='{snow:.2f}'/>"
    return s + "</g>"


def frame(t):
    day = seg(t, 2.5, 5.0)                  # invierno -> verano
    heat = seg(t, 4.8, 7.4)                 # calor creciente
    rev = seg(t, REVELACION, REVELACION + 0.5)
    snow = 1 - seg(t, 2.6, 4.6)
    # estiramiento: un poco encogida en invierno, crece despacio con calor y salta en la revelación
    k = clamp((t - REVELACION) / 0.6)
    spring = 0.025 * math.sin(math.pi * k) * (1 - k) * 2 if t >= REVELACION else 0
    stretch = 0.985 + 0.02 * heat + 0.10 * ease(k) + spring

    top = mix("#7fa3cf", "#3fa3ff", day); mid = mix("#b8cfe8", "#8fd1ff", day); low = mix("#e6eef8", "#ffe7a8", day)
    low = mix(low, "#ffd27a", rev * 0.7)
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920' viewBox='0 0 1080 1920'>", "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff6c8' stop-opacity='{0.85 * day:.3f}'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#fff27a' stop-opacity='{0.8 * rev:.3f}'/><stop offset='0.5' stop-color='#ffb347' stop-opacity='{0.45 * rev:.3f}'/><stop offset='1' stop-color='#ff7a45' stop-opacity='0'/></radialGradient>",
         "</defs>", "<rect width='1080' height='1920' fill='url(#sky)'/>"]
    z = 1 + 0.13 * seg(t, REVELACION, 10)
    s.append(f"<g transform='translate({TX},{1500}) scale({z:.4f}) translate({-TX},{-1500})'>")
    # nubes
    for i, (cx, cy, sc, sp) in enumerate(CLOUDS):
        x = (cx + t * sp * 3) % 1400 - 160
        s.append(nube(x, cy, sc, mix("#eef3fa", "#ffffff", day)))
    # Sol que sale por la derecha
    sx, sy = 860, lerp(1580, 1060, seg(t, 2.3, 5.2))
    sr = lerp(70, 92, heat) + 6 * rev * math.sin(t * 6)
    s.append(f"<circle cx='{sx}' cy='{sy:.0f}' r='{sr * 3.4:.0f}' fill='url(#glow)'/>")
    s.append(f"<g transform='translate({sx},{sy:.0f}) rotate({t * 20:.1f})' opacity='{day:.2f}'>"
             + "".join(f"<path d='M{sr + 14:.0f} -12 L{sr + 48:.0f} 0 L{sr + 14:.0f} 12 Z' fill='#ffd23f' stroke='{INK}' stroke-width='5' stroke-linejoin='round' transform='rotate({a})'/>" for a in range(0, 360, 30))
             + "</g>")
    s.append(f"<circle cx='{sx}' cy='{sy:.0f}' r='{sr:.0f}' fill='{mix('#fff4c2', '#ffd23f', heat)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(tejados(day))
    # césped y camino
    s.append(f"<path d='M0 1700 Q540 1660 1080 1700 L1080 1920 L0 1920 Z' fill='{mix('#7cae8a', '#6ccf55', day)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M420 1920 L490 1760 L630 1760 L700 1920 Z' fill='{mix('#c9c1b6', '#f1d49a', day)}' stroke='{INK}' stroke-width='7'/>")
    # nieve en el suelo
    if snow > 0.02:
        s.append(f"<path d='M0 1702 Q540 1662 1080 1702 L1080 {1740 + 30 * (1 - snow):.0f} Q800 {1760:.0f} 540 1735 Q260 1760 0 {1745:.0f} Z' fill='#ffffff' stroke='{INK}' stroke-width='6' opacity='{snow:.2f}'/>")
    s.append(arbol(330, 1760, 0.95, day, snow))
    s.append(arbol(800, 1770, 1.0, day, snow))
    # halo de calor detrás de la torre
    s.append(f"<circle cx='{TX}' cy='{TY - 420}' r='{lerp(300, 620, rev):.0f}' fill='url(#halo)'/>")
    s.append(poste(t, rev))
    s.append(termometro(t, heat))
    s.append(torre(t, stretch, heat, rev))
    top_y = TY - TIP * TS * stretch
    s.append(flecha(t, top_y))
    # destellos en la punta
    if rev > 0:
        for dx, dy, ph in SPARK:
            r = 90 + 140 * clamp((t - REVELACION) / 1.2)
            a = rev * (0.5 + 0.5 * math.sin(t * 6 + ph))
            px, py = TX + dx * r, top_y - 60 + dy * r * 0.7
            s.append(f"<path d='M{px:.0f} {py - 16:.0f} L{px + 5:.0f} {py - 5:.0f} L{px + 16:.0f} {py:.0f} L{px + 5:.0f} {py + 5:.0f} L{px:.0f} {py + 16:.0f} "
                     f"L{px - 5:.0f} {py + 5:.0f} L{px - 16:.0f} {py:.0f} L{px - 5:.0f} {py - 5:.0f} Z' fill='#fff27a' stroke='{INK}' stroke-width='3' opacity='{a:.2f}'/>")
    # ondas de calor
    if heat > 0.02:
        for hx, ph, sp in HEAT:
            k = (t * sp * 0.5 + ph) % 1.0
            y = 1760 - k * 480
            if y < 1080:
                continue
            a = heat * math.sin(math.pi * k) * 0.8
            s.append(f"<path d='M{hx:.0f} {y:.0f} q12 -18 0 -36 q-12 -18 0 -36' fill='none' stroke='#ffffff' stroke-width='6' stroke-linecap='round' opacity='{a:.2f}'/>")
    # copos de nieve
    if snow > 0.02:
        for x, y0, r, sp, ph in SNOW:
            yy = (y0 + t * sp * 2.2) % H
            xx = x + 25 * math.sin(t * 1.5 + ph)
            s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='2.5' opacity='{snow * 0.95:.2f}'/>")
    s.append("</g></svg>")
    return "".join(s)
