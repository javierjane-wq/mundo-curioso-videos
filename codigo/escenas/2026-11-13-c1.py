"""Mauna Kea: la montaña más alta de la Tierra si se mide desde su base en el fondo del mar.

Arriba del agua solo asoma la cima (unos 4.200 m); un submarino ilumina lo que hay debajo y en la
revelación el mar se aclara: la montaña entera mide más de 10.000 m, más que el Everest (8.849 m).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.5    # el mar se aclara y aparece la montaña entera
MUSICA = 4

SEA = 1370          # nivel del mar
FLOOR = 1885        # fondo marino
PEAK_X, PEAK_Y = 720, 1010

rng = np.random.default_rng(13)
FISH = [(rng.uniform(0, W), rng.uniform(1450, 1820), rng.uniform(0.6, 1.0), rng.uniform(40, 90),
         ["#ff8a3d", "#ffd23f", "#ff5a7a", "#7ee0c3"][i % 4]) for i in range(9)]
BUBBLES = [(rng.uniform(-30, 30), rng.uniform(0, 1), rng.uniform(5, 11)) for _ in range(14)]
SPARK = [(rng.uniform(80, 1000), rng.uniform(1400, 1860), rng.uniform(0, 6.28)) for _ in range(28)]

MOUNT = (f"M60 {FLOOR+40} C230 1760 430 1300 600 1080 Q{PEAK_X} 985 840 1075 "
         f"C1000 1260 1190 1650 1260 {FLOOR+40} Z")
SNOW = (f"M612 1066 Q{PEAK_X} 980 828 1066 Q800 1092 780 1078 Q760 1104 740 1082 "
        f"Q715 1110 690 1084 Q665 1102 645 1080 Q628 1092 612 1066 Z")
EVEREST = (f"M90 {FLOOR} L200 1560 L250 1450 L290 1330 L320 1250 L350 1128 L385 1230 "
           f"L410 1290 L450 1420 L500 1560 L600 {FLOOR} Z")


def mountain(t, rev):
    """Volcán escudo con cara: cumbre nevada, laderas verdes junto a la costa y roca bajo el agua."""
    g = []
    rock = mix("#8b5a43", "#b06a48", rev)
    g.append(f"<path d='{MOUNT}' fill='{rock}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # bandas de roca volcánica (estratos)
    g.append("<clipPath id='mclip'><path d='" + MOUNT + "'/></clipPath>")
    g.append("<g clip-path='url(#mclip)'>")
    for i, yy in enumerate(range(1440, FLOOR + 60, 95)):
        g.append(f"<path d='M0 {yy} Q300 {yy-30} 600 {yy+10} T1200 {yy-10}' fill='none' "
                 f"stroke='{mix('#6e4433', '#93553a', rev)}' stroke-width='14' opacity='0.7'/>")
    # laderas verdes por encima del mar
    g.append(f"<path d='M0 {SEA+10} Q250 1290 470 1250 Q600 1225 640 1170 Q700 1215 760 1180 Q840 1230 900 1210 "
             f"Q1020 1260 1200 {SEA+10} Z' fill='#5fbf5a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M0 {SEA+10} Q300 1330 520 1300 Q760 1280 1200 {SEA+10} Z' fill='#3e9a4a'/>")
    # corales y algas en la base
    for cx, h, col in ((330, 70, "#ff7aa8"), (420, 50, "#ffb347"), (980, 80, "#ff7aa8"), (1050, 55, "#b48cff")):
        sway = 6 * pulso(t, 2.2, cx / 400)
        g.append(f"<path d='M{cx} {FLOOR} q{-10+sway:.1f} {-h/2} {sway:.1f} {-h} M{cx} {FLOOR} q{14+sway:.1f} {-h/2} {18+sway:.1f} {-h*0.8:.0f}' "
                 f"fill='none' stroke='{col}' stroke-width='12' stroke-linecap='round'/>")
    g.append("</g>")
    g.append(f"<path d='{MOUNT}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # nieve en la cima
    g.append(f"<path d='{SNOW}' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cara
    blink = 0.12 if ((t + 1.4) % 2.8) < 0.13 else 1.0
    wide = 1 + 0.35 * seg(t, 7.4, 7.9)
    look_y = lerp(0, 10, seg(t, 4.8, 5.8)) * (1 - seg(t, 7.4, 8.0))
    for ex in (PEAK_X - 62, PEAK_X + 62):
        g.append(f"<ellipse cx='{ex}' cy='1175' rx='{30*wide:.1f}' ry='{36*wide*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex+4:.0f}' cy='{1180+look_y:.0f}' r='{17*wide:.1f}' fill='{INK}'/>"
                     f"<circle cx='{ex-3:.0f}' cy='{1172+look_y:.0f}' r='6' fill='#fff'/>")
    g.append(f"<ellipse cx='{PEAK_X-110}' cy='1228' rx='22' ry='13' fill='#ff8fa3' opacity='0.8'/>"
             f"<ellipse cx='{PEAK_X+110}' cy='1228' rx='22' ry='13' fill='#ff8fa3' opacity='0.8'/>")
    mo = seg(t, 7.4, 7.9)
    if mo > 0.5:
        g.append(f"<ellipse cx='{PEAK_X}' cy='1236' rx='22' ry='26' fill='#7a2a2a' stroke='{INK}' stroke-width='6'/>")
    else:
        g.append(f"<path d='M{PEAK_X-28} 1228 Q{PEAK_X} 1252 {PEAK_X+28} 1228' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # palmera en la costa
    sw = 5 * pulso(t, 2.6)
    g.append(f"<g transform='translate(960,1300)'><path d='M0 30 Q-8 -40 {6+sw:.1f} -110' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
             f"<path d='M0 30 Q-8 -40 {6+sw:.1f} -110' fill='none' stroke='#a8743f' stroke-width='10' stroke-linecap='round'/>")
    for a in (-150, -110, -60, -20, 25):
        g.append(f"<g transform='translate({6+sw:.1f},-110) rotate({a + sw*1.5:.1f})'>"
                 f"<path d='M0 0 Q40 -26 86 6 Q44 -6 0 0 Z' fill='#3fae4f' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/></g>")
    g.append("</g>")
    return "".join(g)


def boat(t):
    x = lerp(-140, 430, seg(t, 0, 9.5))
    bob = 7 * pulso(t, 1.4)
    rot = 3 * pulso(t, 1.4, 0.3)
    return (f"<g transform='translate({x:.1f},{SEA - 8 + bob:.1f}) rotate({rot:.1f})'>"
            f"<path d='M-70 0 L70 0 L48 34 L-48 34 Z' fill='#ff5a5f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<line x1='0' y1='0' x2='0' y2='-120' stroke='{INK}' stroke-width='8'/>"
            f"<path d='M6 -112 L6 -12 L64 -12 Z' fill='#fff7e6' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M-6 -100 L-6 -18 L-50 -18 Z' fill='#ffd23f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def sub_pos(t):
    k = seg(t, 2.6, 7.0)
    return lerp(1180, 900, k), lerp(1470, 1700, k)


def submarine(t):
    x, y = sub_pos(t)
    y += 5 * pulso(t, 1.6)
    prop = (t * 900) % 360
    return (f"<g transform='translate({x:.1f},{y:.1f})'>"
            f"<rect x='-10' y='-78' width='40' height='40' rx='8' fill='#ffc93c' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='0' cy='0' rx='120' ry='56' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='-50' cy='-2' r='24' fill='#8fe3ff' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='-56' cy='-8' r='7' fill='#fff'/>"
            f"<circle cx='16' cy='-2' r='18' fill='#8fe3ff' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-128' y='-16' width='26' height='32' rx='8' fill='#fff2a8' stroke='{INK}' stroke-width='6'/>"
            f"<g transform='translate(132,0) scale(1,{math.cos(math.radians(prop)):.2f})'>"
            f"<ellipse rx='10' ry='34' fill='#9aa3ad' stroke='{INK}' stroke-width='5'/></g></g>")


def beam_poly(t):
    x, y = sub_pos(t)
    x0, y0 = x - 120, y
    return f"M{x0:.0f} {y0-14:.0f} L{x0-520:.0f} {y0-210:.0f} L{x0-470:.0f} {y0+190:.0f} L{x0:.0f} {y0+14:.0f} Z"


def fish(t, rev):
    s = []
    for fx, fy, sc, sp, col in FISH:
        x = (fx + t * sp) % (W + 200) - 100
        y = fy + 10 * pulso(t, 2, fx / 300)
        tail = 10 * pulso(t, 0.4, fx)
        s.append(f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})'>"
                 f"<path d='M-34 0 L-58 {-18+tail:.0f} L-58 {18+tail:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
                 f"<ellipse rx='38' ry='22' fill='{col}' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='18' cy='-5' r='6' fill='{INK}'/></g>")
    return "".join(s)


def frame(t):
    rev = seg(t, 7.35, 8.3)
    # cielo de mañana tropical
    sky = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>"
           f"<stop offset='0' stop-color='#4fb3ff'/><stop offset='0.7' stop-color='#9fdcff'/><stop offset='1' stop-color='#e6f7ff'/></linearGradient>")
    water = (f"<linearGradient id='wat' x1='0' y1='0' x2='0' y2='1'>"
             f"<stop offset='0' stop-color='{mix('#1d6fb8', '#3fd0e6', rev)}'/>"
             f"<stop offset='1' stop-color='{mix('#0b2a5a', '#1878b8', rev)}'/></linearGradient>")
    beamg = ("<linearGradient id='beam' x1='1' y1='0' x2='0' y2='0'>"
             "<stop offset='0' stop-color='#fff7b0' stop-opacity='0.75'/><stop offset='1' stop-color='#fff7b0' stop-opacity='0.05'/></linearGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         f"<defs>{sky}{water}{beamg}<clipPath id='bclip'><path d='{beam_poly(t)}'/></clipPath>"
         f"<clipPath id='under'><rect x='-200' y='{SEA}' width='{W+400}' height='{H}'/></clipPath></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.07 * seg(t, 7.4, 10)
    body = []
    # sol y nubes (arriba, tranquilo)
    body.append(f"<circle cx='985' cy='820' r='{120 + 10*pulso(t, 3):.0f}' fill='#fff3b0' opacity='0.45'/>"
                f"<circle cx='985' cy='820' r='70' fill='#ffe15a' stroke='#ffb347' stroke-width='8'/>")
    for i, (cx, cy, sc) in enumerate(((140, 330, 1.3), (760, 520, 1.0), (330, 860, 0.9))):
        dx = (t * (12 + 6 * i)) % 1400 - 200
        body.append(f"<g transform='translate({(cx + dx) % 1400 - 200:.0f},{cy}) scale({sc})' opacity='0.95'>"
                    f"<path d='M0 40 Q10 0 60 10 Q90 -30 140 5 Q200 -10 210 40 Z' fill='#ffffff' stroke='#bfe3f7' stroke-width='5'/></g>")
    # gaviotas
    for i, (bx, by) in enumerate(((200, 1000), (300, 940))):
        fl = 14 * pulso(t, 0.5, i * 0.3)
        x = (bx + t * 40) % 1200
        body.append(f"<path d='M{x-26:.0f} {by - fl:.0f} Q{x-12:.0f} {by-12:.0f} {x:.0f} {by:.0f} Q{x+12:.0f} {by-12:.0f} {x+26:.0f} {by - fl:.0f}' "
                    f"fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # agua (fondo del mar)
    body.append(f"<rect x='-200' y='{SEA}' width='{W+400}' height='{H-SEA+200}' fill='url(#wat)'/>")
    # montaña (sale con un pequeño rebote al principio)
    rise = lerp(60, 0, ease(clamp(t / 1.2))) - 8 * math.sin(math.pi * clamp(t / 1.2)) * (t < 1.2)
    mtn = mountain(t, rev)
    body.append(f"<g transform='translate(0,{rise:.1f})'>{mtn}</g>")
    # Everest fantasma para comparar (aparece en la revelación, subiendo desde el fondo)
    ev = seg(t, 7.7, 8.7)
    if ev > 0:
        body.append(f"<g transform='translate(0,{lerp(500, 0, ev):.0f})' opacity='{0.75*ev:.2f}'>"
                    f"<path d='{EVEREST}' fill='#e9f4ff' fill-opacity='0.45' stroke='#ffffff' stroke-width='8' stroke-dasharray='26 16' stroke-linejoin='round'/></g>")
    body.append(fish(t, rev))
    # oscuridad del mar profundo: tapa la montaña bajo el agua hasta la revelación
    murk = lerp(0.9, 0.0, rev)
    if murk > 0.01:
        body.append(f"<rect x='-200' y='{SEA}' width='{W+400}' height='{H-SEA+200}' fill='#06183a' opacity='{murk:.3f}'/>")
    # haz del submarino: deja ver la ladera escondida
    bk = seg(t, 4.6, 5.4) * (1 - rev)
    if bk > 0.01:
        body.append(f"<g clip-path='url(#bclip)' opacity='{bk:.2f}'><g clip-path='url(#under)'>"
                    f"<rect x='-200' y='{SEA}' width='{W+400}' height='{H}' fill='url(#wat)'/>"
                    f"<g transform='translate(0,{rise:.1f})'>{mtn}</g>{fish(t, rev)}</g></g>")
        body.append(f"<path d='{beam_poly(t)}' fill='url(#beam)' opacity='{bk:.2f}'/>")
    # burbujas del submarino
    sx, sy = sub_pos(t)
    for bx, ph, br in BUBBLES:
        k = (t * 0.6 + ph) % 1
        by = sy - 60 - k * 260
        if by > SEA + 20:
            body.append(f"<circle cx='{sx + 110 + bx + 10*math.sin(t*3+ph*6):.0f}' cy='{by:.0f}' r='{br:.1f}' fill='none' stroke='#cfefff' stroke-width='4' opacity='{0.8*(1-k):.2f}'/>")
    body.append(submarine(t))
    # olas en la superficie
    off = (t * 60) % 120
    wave = f"M-240 {SEA}" + "".join(f" q30 -16 60 0 t60 0" for _ in range(24))
    body.append(f"<g transform='translate({off - 120:.1f},0)'><path d='{wave} L1400 {SEA+30} L-240 {SEA+30} Z' fill='{mix('#2f8fd8', '#5fe0f0', rev)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    body.append(boat(t))
    # destellos y regla de altura en la revelación
    if rev > 0:
        for px, py, ph in SPARK:
            a = rev * (0.5 + 0.5 * math.sin(t * 6 + ph))
            body.append(f"<path d='M{px:.0f} {py-12:.0f} L{px+4:.0f} {py-4:.0f} L{px+12:.0f} {py:.0f} L{px+4:.0f} {py+4:.0f} L{px:.0f} {py+12:.0f} "
                        f"L{px-4:.0f} {py+4:.0f} L{px-12:.0f} {py:.0f} L{px-4:.0f} {py-4:.0f} Z' fill='#fffbd0' opacity='{a:.2f}'/>")
        rk = seg(t, 7.6, 8.8)
        top = lerp(FLOOR, PEAK_Y - 5, rk)
        body.append(f"<line x1='1000' y1='{FLOOR}' x2='1000' y2='{top:.0f}' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
                    f"<line x1='1000' y1='{FLOOR}' x2='1000' y2='{top:.0f}' stroke='#ffe14a' stroke-width='12' stroke-linecap='round'/>")
        for yy in range(FLOOR - 87, int(top), -87):
            body.append(f"<line x1='982' y1='{yy}' x2='1018' y2='{yy}' stroke='{INK}' stroke-width='6'/>")
        if rk > 0.95:
            body.append(f"<path d='M974 {PEAK_Y+18} L1000 {PEAK_Y-18} L1026 {PEAK_Y+18} Z' fill='#ffe14a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        # destello de luz
        body.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.45*(1-seg(t, 7.5, 8.2))*seg(t, 7.35, 7.5):.2f}'/>")
    s.append(zoom(640, 1450, z, "".join(body)))
    s.append("</svg>")
    return "".join(s)
