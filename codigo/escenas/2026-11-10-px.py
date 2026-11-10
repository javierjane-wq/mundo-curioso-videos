"""2026-11-10-px · No puedes hacerte cosquillas a ti mismo: el cerebelo predice la sensación.

Fuentes: Scientific American ("Why can't a person tickle himself?", S.-J. Blakemore): el cerebelo
predice las consecuencias sensoriales de nuestros propios movimientos y esa predicción atenúa
la sensación; las cosquillas de otra persona no se pueden predecir (Blakemore, Wolpert y Frith,
Nature Neuroscience 1998 / NeuroReport 2000).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.5    # el niño estalla de risa: golpe musical
MUSICA = 5

SKIN = "#f6c89a"
SKIN_D = "#e3a877"
SKIN2 = "#8a5a3c"     # piel de la amiga
FOOT = (800, 1395)    # centro de la planta del pie levantado
HEAD = (330, 1150)

rng = np.random.default_rng(11)
DUST = [(rng.uniform(0, W), rng.uniform(150, 1900), rng.uniform(3, 6), rng.uniform(10, 30), rng.uniform(0, 6.28)) for _ in range(26)]
TEARS = [(rng.uniform(0.6, 1.2), rng.uniform(-1, -0.3), rng.uniform(0, 0.6)) for _ in range(8)]
SPARKS = [(rng.uniform(0, 6.28), rng.uniform(90, 170), rng.uniform(0, 1)) for _ in range(10)]
CONFETTI = [(rng.uniform(0, W), rng.uniform(-400, 900), rng.uniform(0, 6.28), rng.choice(["#ffd23f", "#ff6b6b", "#5ec8ff", "#7ee081", "#c58cff"])) for _ in range(34)]


def laugh(t):
    return seg(t, REVELACION, REVELACION + 0.25)


def jitter(t):
    """Sacudida de la risa."""
    k = laugh(t)
    return 10 * k * math.sin(t * 38), 14 * k * abs(math.sin(t * 19))


def background(t):
    s = []
    s.append(f"<rect width='{W}' height='{H}' fill='#8fd0d9'/>")
    # papel pintado a rayas
    for x in range(0, W + 120, 120):
        s.append(f"<rect x='{x}' y='0' width='60' height='1700' fill='#7fc3cd'/>")
    # ventana con cielo y nubes
    s.append("<clipPath id='win'><rect x='600' y='200' width='380' height='520' rx='14'/></clipPath>")
    s.append(f"<rect x='600' y='200' width='380' height='520' rx='14' fill='#bfe9ff'/>")
    s.append("<g clip-path='url(#win)'>")
    for i, (cy, sc) in enumerate([(330, 1.0), (520, 0.8)]):
        cx = 420 + ((t * (22 + 10 * i) + 160 * i) % 620)
        s.append(f"<g transform='translate({cx:.0f},{cy}) scale({sc})'><path d='M0 40 Q15 0 60 10 Q85 -25 130 5 Q170 -5 175 40 Z' "
                 f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    s.append("</g>")
    s.append(f"<rect x='600' y='200' width='380' height='520' rx='14' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<line x1='790' y1='200' x2='790' y2='720' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<line x1='600' y1='460' x2='980' y2='460' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='580' y='715' width='420' height='34' rx='8' fill='#f2ead8' stroke='{INK}' stroke-width='{LW}'/>")
    # planta en el alféizar
    sw = 4 * math.sin(t * 2)
    s.append(f"<g transform='translate(900,715) rotate({sw:.1f})'>"
             f"<path d='M0 0 Q-40 -70 -10 -120 Q0 -60 0 0' fill='#5cb85c' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M0 0 Q40 -80 20 -130 Q5 -60 0 0' fill='#4caf50' stroke='{INK}' stroke-width='6'/></g>")
    s.append(f"<path d='M870 715 L930 715 L922 690 L878 690 Z' fill='#e07a4a' stroke='{INK}' stroke-width='6'/>")
    # cuadro
    s.append(f"<rect x='110' y='420' width='260' height='200' rx='10' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='135' y='445' width='210' height='150' fill='#7ee081' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<circle cx='300' cy='480' r='22' fill='#fff3a0' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<path d='M135 595 L200 515 L250 565 L290 530 L345 595 Z' fill='#4a9a5a' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # suelo y alfombra
    s.append(f"<rect x='0' y='1700' width='{W}' height='220' fill='#d9a066' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(-40, W, 160):
        s.append(f"<line x1='{x}' y1='1700' x2='{x + 60}' y2='1920' stroke='#c08a52' stroke-width='6'/>")
    s.append(f"<ellipse cx='540' cy='1830' rx='470' ry='60' fill='#ff8fa3' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='540' cy='1830' rx='380' ry='40' fill='none' stroke='#ffd1da' stroke-width='8' stroke-dasharray='20 14'/>")
    return "".join(s)


def burst(t):
    k = laugh(t)
    if k <= 0:
        return ""
    s = []
    rot = (t - REVELACION) * 25
    cx, cy = 450, 1250
    for i in range(16):
        a = math.radians(i * 22.5 + rot)
        a2 = a + math.radians(9)
        r = 1400
        s.append(f"<path d='M{cx} {cy} L{cx + r*math.cos(a):.0f} {cy + r*math.sin(a):.0f} L{cx + r*math.cos(a2):.0f} {cy + r*math.sin(a2):.0f} Z' "
                 f"fill='{'#fff07a' if i % 2 else '#ffd23f'}' opacity='{0.55*k:.2f}'/>")
    return "".join(s)


def sofa(t, part):
    """part='back' (respaldo y cojines) o 'front' (asiento y brazos)."""
    s = []
    if part == "back":
        s.append(f"<rect x='60' y='1180' width='960' height='360' rx='60' fill='#e8743b' stroke='{INK}' stroke-width='{LW}'/>")
        # cojines que saltan en la revelación
        for i, (cx, col) in enumerate([(170, "#3d8fe0"), (930, "#ffd23f")]):
            k = laugh(t)
            up = k * (220 + 60 * i) * abs(math.sin((t - REVELACION) * 3.2 + i)) if k > 0 else 0
            rot = k * 40 * math.sin((t - REVELACION) * 4 + i) if k > 0 else -8 + 16 * i
            s.append(f"<g transform='translate({cx},{1340 - up:.0f}) rotate({rot:.1f})'>"
                     f"<rect x='-80' y='-80' width='160' height='160' rx='34' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
                     f"<circle r='10' fill='{INK}' opacity='0.5'/></g>")
    else:
        s.append(f"<rect x='90' y='1500' width='900' height='150' rx='36' fill='#f08a4f' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(f"<line x1='540' y1='1510' x2='540' y2='1640' stroke='{INK}' stroke-width='6'/>")
        for x in (20, 960):
            s.append(f"<rect x='{x}' y='1330' width='100' height='330' rx='40' fill='#d9652f' stroke='{INK}' stroke-width='{LW}'/>")
        for x in (110, 950):
            s.append(f"<rect x='{x}' y='1650' width='30' height='60' rx='6' fill='#7a4a2a' stroke='{INK}' stroke-width='6'/>")
    return "".join(s)


def feather(x, y, ang, sc=1.0):
    """Pluma blanca grande: raquis curvo y barbas esponjosas."""
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({sc})'>"
            f"<path d='M0 0 Q60 -40 150 -30 Q200 -20 215 0 Q200 25 150 30 Q60 40 0 0 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M70 -22 L60 -6 M110 -27 L100 -8 M150 -28 L140 -8 M70 22 L60 6 M110 27 L100 8 M150 28 L140 8' stroke='#cfd8e0' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M-30 4 Q80 2 205 0' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>")


def limb(x1, y1, x2, y2, col, w):
    return (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{INK}' stroke-width='{w + 2*LW}' stroke-linecap='round'/>"
            f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{col}' stroke-width='{w}' stroke-linecap='round'/>")


def foot_pos(t):
    k = laugh(t)
    if k <= 0:
        wig = 4 * math.sin(t * 3)
        return FOOT[0], FOOT[1] + wig, 0
    kick = (t - REVELACION) * 9
    return FOOT[0] + 20 * math.sin(kick), FOOT[1] - 60 * k * abs(math.sin(kick)), 18 * math.sin(kick)


def boy(t):
    jx, jy = jitter(t)
    k = laugh(t)
    s = [f"<g transform='translate({jx:.1f},{-jy:.1f})'>"]
    fx, fy, frot = foot_pos(t)
    # pierna de abajo (doblada, pie en el suelo)
    s.append(limb(300, 1520, 300, 1690, "#2f5fa8", 86))
    s.append(f"<ellipse cx='320' cy='1712' rx='62' ry='24' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    # pierna estirada hacia el pie levantado
    s.append(limb(360, 1500, fx - 70, fy + 95, "#2f5fa8", 90))
    s.append(f"<rect x='{fx - 125:.0f}' y='{fy + 55:.0f}' width='70' height='80' rx='12' fill='#3c74c4' stroke='{INK}' stroke-width='7' transform='rotate(-15 {fx - 90:.0f} {fy + 95:.0f})'/>")
    # pie con la planta hacia la cámara y cinco dedos
    s.append(f"<g transform='rotate({frot:.1f} {fx:.0f} {fy + 60:.0f})'>")
    s.append(f"<ellipse cx='{fx:.0f}' cy='{fy:.0f}' rx='66' ry='100' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='{fx:.0f}' cy='{fy + 50:.0f}' rx='40' ry='34' fill='{SKIN_D}' opacity='0.6'/>")
    s.append(f"<ellipse cx='{fx + 4:.0f}' cy='{fy - 40:.0f}' rx='42' ry='30' fill='{SKIN_D}' opacity='0.45'/>")
    curl = 0
    for i, (dx, dy, r) in enumerate([(-44, -98, 24), (-18, -112, 20), (6, -116, 18), (28, -110, 16), (48, -96, 14)]):
        wig = 4 * math.sin(t * 6 + i) + (10 * math.sin(t * 30 + i) if 6.6 < t < REVELACION else 0)
        s.append(f"<circle cx='{fx + dx:.0f}' cy='{fy + dy + wig + curl:.0f}' r='{r}' fill='{SKIN}' stroke='{INK}' stroke-width='7'/>")
    s.append("</g>")
    # cuerpo
    s.append(f"<path d='M220 1300 Q330 1250 440 1300 L460 1520 L205 1520 Z' fill='#3fae5a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M290 1290 Q330 1320 370 1290' fill='none' stroke='{INK}' stroke-width='6'/>")
    # brazo izquierdo apoyado
    s.append(limb(230, 1330, 160, 1470, SKIN, 40))
    # brazo con la pluma
    self_t = seg(t, 0.3, 1.0) * (1 - seg(t, 5.2, 5.8))
    if k > 0:
        hx, hy = 470 + 40 * math.sin(t * 20), 1180 + 30 * math.sin(t * 17)
    else:
        rub = math.sin(t * 9) * self_t
        hx = lerp(470, fx - 150, self_t) + 20 * rub
        hy = lerp(1480, fy - 10, self_t) + 50 * rub
    s.append(limb(425, 1330, hx, hy, SKIN, 40))
    s.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='30' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    if self_t > 0.05 and k <= 0:
        s.append(feather(hx, hy, -8 + 10 * math.sin(t * 9), 0.85))
    # cabeza
    hx0, hy0 = HEAD
    tilt = -12 * k + 4 * math.sin(t * 1.3) * (1 - k)
    s.append(f"<g transform='rotate({tilt:.1f} {hx0} {hy0 + 100})'>")
    s.append(f"<circle cx='{hx0 - 112}' cy='{hy0 + 10}' r='28' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{hx0 + 112}' cy='{hy0 + 10}' r='28' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{hx0}' cy='{hy0}' r='118' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo despeinado
    s.append(f"<path d='M{hx0-122} {hy0-5} Q{hx0-140} {hy0-110} {hx0-70} {hy0-130} L{hx0-80} {hy0-170} L{hx0-30} {hy0-140} L{hx0-10} {hy0-185} "
             f"L{hx0+25} {hy0-140} L{hx0+70} {hy0-170} L{hx0+70} {hy0-120} Q{hx0+140} {hy0-100} {hx0+122} {hy0-5} "
             f"Q{hx0+90} {hy0-70} {hx0+30} {hy0-70} Q{hx0-10} {hy0-40} {hx0-30} {hy0-75} Q{hx0-90} {hy0-60} {hx0-122} {hy0-5} Z' "
             f"fill='#6b3a1f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cerebro y cerebelo (transparencia "rayos X") mientras predice
    g = seg(t, 3.7, 4.2) * (1 - seg(t, 5.9, 6.4))
    if g > 0:
        s.append(f"<g opacity='{0.92*g:.2f}'>")
        s.append(f"<circle cx='{hx0}' cy='{hy0-80}' r='0' fill='none'/>")
        s.append(f"<path d='M{hx0-85} {hy0-45} Q{hx0-95} {hy0-120} {hx0-20} {hy0-128} Q{hx0+50} {hy0-140} {hx0+88} {hy0-85} Q{hx0+100} {hy0-40} {hx0+55} {hy0-38} L{hx0-55} {hy0-38} Q{hx0-90} {hy0-35} {hx0-85} {hy0-45} Z' "
                 f"fill='#ff9fb6' stroke='{INK}' stroke-width='6'/>")
        s.append(f"<path d='M{hx0-50} {hy0-105} Q{hx0-20} {hy0-85} {hx0-40} {hy0-55} M{hx0} {hy0-120} Q{hx0+20} {hy0-90} {hx0+5} {hy0-60} M{hx0+45} {hy0-110} Q{hx0+60} {hy0-75} {hx0+40} {hy0-50}' "
                 f"fill='none' stroke='#e0607e' stroke-width='5' stroke-linecap='round'/>")
        glow = 0.6 + 0.4 * pulso(t, 0.5)
        cbx, cby = hx0 - 70, hy0 - 25
        s.append(f"<circle cx='{cbx}' cy='{cby}' r='{60 + 12*glow:.0f}' fill='#5ec8ff' opacity='{0.35*glow:.2f}'/>")
        s.append(f"<ellipse cx='{cbx}' cy='{cby}' rx='40' ry='26' fill='#5ec8ff' stroke='{INK}' stroke-width='6'/>")
        s.append(f"<path d='M{cbx-28} {cby-6} Q{cbx} {cby-14} {cbx+28} {cby-6} M{cbx-30} {cby+8} Q{cbx} {cby} {cbx+30} {cby+8}' fill='none' stroke='#2a7fc0' stroke-width='4'/>")
        s.append("</g>")
    # cara
    blink = 1.0 if ((t + 1.2) % 2.7) > 0.13 else 0.12
    look = 14 if k <= 0 else 0
    if k > 0.5:
        for ex in (-42, 42):
            s.append(f"<path d='M{hx0+ex-24} {hy0+5} Q{hx0+ex} {hy0-28} {hx0+ex+24} {hy0+5}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
        op = 1 + 0.25 * math.sin(t * 22)
        s.append(f"<path d='M{hx0-55} {hy0+35} Q{hx0} {hy0+35} {hx0+55} {hy0+35} Q{hx0+50} {hy0+35+75*op:.0f} {hx0} {hy0+38+80*op:.0f} Q{hx0-50} {hy0+35+75*op:.0f} {hx0-55} {hy0+35} Z' "
                 f"fill='#a8283a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        s.append(f"<path d='M{hx0-45} {hy0+38} L{hx0+45} {hy0+38} L{hx0+40} {hy0+55} L{hx0-40} {hy0+55} Z' fill='#fff'/>")
        s.append(f"<ellipse cx='{hx0}' cy='{hy0+38+62*op:.0f}' rx='26' ry='14' fill='#ff7a8a'/>")
        s.append(f"<circle cx='{hx0-75}' cy='{hy0+40}' r='20' fill='#ff8a8a' opacity='0.6'/><circle cx='{hx0+75}' cy='{hy0+40}' r='20' fill='#ff8a8a' opacity='0.6'/>")
        # lágrimas de risa
        for i, (vx, vy, d) in enumerate(TEARS):
            tt = ((t - REVELACION - d) % 0.9)
            side = -1 if i % 2 else 1
            x = hx0 + side * (70 + 380 * vx * tt)
            y = hy0 - 5 + 420 * vy * tt + 900 * tt * tt
            s.append(f"<path d='M{x:.0f} {y - 16:.0f} Q{x + 12:.0f} {y + 2:.0f} {x:.0f} {y + 10:.0f} Q{x - 12:.0f} {y + 2:.0f} {x:.0f} {y - 16:.0f} Z' fill='#7fd4ff' stroke='{INK}' stroke-width='4'/>")
    else:
        for ex in (-42, 42):
            s.append(f"<ellipse cx='{hx0+ex}' cy='{hy0-5}' rx='30' ry='{34*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
            if blink > 0.5:
                s.append(f"<circle cx='{hx0+ex+look:.0f}' cy='{hy0+5}' r='14' fill='{INK}'/><circle cx='{hx0+ex+look-5:.0f}' cy='{hy0}' r='5' fill='#fff'/>")
        if t < 1.6:   # sonrisa traviesa al empezar
            s.append(f"<path d='M{hx0-40} {hy0+50} Q{hx0+5} {hy0+90} {hx0+50} {hy0+45}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
        elif t < 6.6:  # aburrido: boca plana, cejas desconcertadas
            s.append(f"<path d='M{hx0-30} {hy0+65} Q{hx0} {hy0+58} {hx0+30} {hy0+65}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
            s.append(f"<path d='M{hx0-68} {hy0-55} L{hx0-20} {hy0-48} M{hx0+20} {hy0-52} L{hx0+68} {hy0-62}' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
        else:          # sorpresa: boca en O
            s.append(f"<ellipse cx='{hx0}' cy='{hy0+65}' rx='18' ry='22' fill='#a8283a' stroke='{INK}' stroke-width='7'/>")
    s.append("</g></g>")
    return "".join(s)


def friend_hand(t):
    """Brazo de la amiga (manga amarilla) que entra por la derecha con otra pluma."""
    k = seg(t, 5.8, 6.6)
    if k <= 0:
        return ""
    fx, fy, _ = foot_pos(t)
    rub = math.sin(t * 14) * seg(t, 6.5, 6.8)
    hx = lerp(1250, fx + 160, k) + 15 * rub
    hy = lerp(1300, fy - 20, k) + 45 * rub
    if t > REVELACION:
        hx = fx + 170 + 30 * seg(t, REVELACION, REVELACION + 0.6)
    s = [f"<path d='M1140 {hy - 40:.0f} L{hx + 40:.0f} {hy - 32:.0f} L{hx + 40:.0f} {hy + 32:.0f} L1140 {hy + 40:.0f} Z' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>",
         f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='34' fill='{SKIN2}' stroke='{INK}' stroke-width='{LW}'/>",
         feather(hx - 10, hy, 180 + 12 * math.sin(t * 14), 0.9)]
    return "".join(s)


def tickles(t):
    """Chispas de cosquillas alrededor del pie: apagadas por el escudo azul o enormes y amarillas."""
    s = []
    fx, fy, _ = foot_pos(t)
    # escudo de predicción
    sh = seg(t, 4.0, 4.5) * (1 - seg(t, 5.9, 6.4))
    if sh > 0:
        r = 150 + 8 * pulso(t, 0.6)
        s.append(f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='{r:.0f}' fill='#5ec8ff' opacity='{0.22*sh:.2f}' stroke='#2a9be0' stroke-width='8' stroke-opacity='{0.8*sh:.2f}' stroke-dasharray='26 16'/>")
        # señal del cerebelo al pie
        hx0, hy0 = HEAD
        x0, y0 = hx0 - 70, hy0 - 25
        off = -(t * 120) % 60
        s.append(f"<path d='M{x0} {y0} Q{(x0 + fx)/2:.0f} {y0 - 220} {fx - 60:.0f} {fy - 110:.0f}' fill='none' stroke='#2a9be0' stroke-width='10' "
                 f"stroke-dasharray='30 30' stroke-dashoffset='{off:.0f}' stroke-linecap='round' opacity='{0.9*sh:.2f}'/>")
    self_tk = seg(t, 1.0, 1.4) * (1 - seg(t, 5.3, 5.7))
    other = seg(t, 6.6, 6.9)
    for i, (a, r, ph) in enumerate(SPARKS):
        if other > 0:
            amp = other * (1.3 + 0.6 * laugh(t))
            col = "#ffd23f"
            op = 1
        elif self_tk > 0:
            amp = 0.55 * self_tk * (1 - 0.7 * sh)
            col = "#b8c4cc"
            op = 0.8
        else:
            continue
        p = (t * 2.2 + ph) % 1
        rr = r * amp * (0.6 + 0.6 * p)
        x, y = fx + rr * math.cos(a), fy + rr * math.sin(a)
        sz = 26 * amp * (1 - p * 0.5)
        ang = math.degrees(a)
        s.append(f"<path d='M{-sz:.0f} 0 L{-sz/3:.0f} {-sz/2:.0f} L{sz/3:.0f} {sz/2:.0f} L{sz:.0f} 0' transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f})' "
                 f"fill='none' stroke='{col}' stroke-width='{max(3, 9*amp):.0f}' stroke-linecap='round' stroke-linejoin='round' opacity='{op:.2f}'/>")
    return "".join(s)


def confetti(t):
    k = laugh(t)
    if k <= 0:
        return ""
    s = []
    dt = t - REVELACION
    for x, y0, ph, col in CONFETTI:
        y = y0 * 0.5 + 900 + 420 * dt
        if y > 1950:
            continue
        xx = x + 30 * math.sin(dt * 4 + ph)
        s.append(f"<rect x='{xx:.0f}' y='{y:.0f}' width='22' height='12' rx='3' fill='{col}' stroke='{INK}' stroke-width='3' "
                 f"transform='rotate({(dt * 200 + ph * 57) % 360:.0f} {xx:.0f} {y:.0f})'/>")
    return "".join(s)


def frame(t):
    z = 1 + 0.10 * seg(t, REVELACION, REVELACION + 1.0) + 0.04 * seg(t, 3.6, 4.4) * (1 - seg(t, 5.8, 6.4))
    cuerpo = [background(t), burst(t), sofa(t, "back"), sofa(t, "front"), boy(t), tickles(t), friend_hand(t)]
    for px, py, pr, sp, ph in DUST:
        yy = (py - t * sp) % 1800 + 120
        cuerpo.append(f"<circle cx='{px + 15*math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#ffffff' opacity='0.35'/>")
    cuerpo.append(confetti(t))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            + zoom(540, 1400, z, "".join(cuerpo)) + "</svg>")
