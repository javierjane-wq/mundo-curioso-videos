"""2026-11-08-c2 · El grafito del lápiz y el diamante son el mismo elemento: carbono.

0-2,5 s  un lápiz con cara escribe un garabato sobre el papel.
2,5-5 s  una lupa muestra las capas de átomos del grafito, que se deslizan (por eso escribe).
5-7,5 s  las capas tiemblan, se aprietan y se calientan.
7,5-10 s REVELACION: destello y aparece un gran diamante brillante; la habitación se vuelve
         azul noche con rayos de luz y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 2

ANG = 55.0                     # inclinación del lápiz (grados sobre la horizontal)
CA, SA = math.cos(math.radians(ANG)), math.sin(math.radians(ANG))
LENS = (300, 1215, 190)        # lupa: centro y radio
DIA = (300, 1215)              # centro del diamante

rng = np.random.default_rng(11)
MOTES = [(rng.uniform(0, W), rng.uniform(0, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.28)) for _ in range(34)]
SPARK = [(rng.uniform(-420, 420), rng.uniform(-330, 330), rng.uniform(18, 38), rng.uniform(0, 6.28)) for _ in range(16)]
CRUMBS = [(rng.uniform(-30, 30), rng.uniform(0, 1), rng.uniform(4, 8)) for _ in range(10)]


def tip_pos(t):
    """Punta del lápiz: escribe un garabato de izquierda a derecha hasta los 5 s."""
    k = clamp(t / 5.0)
    x = lerp(110, 520, k)
    y = 1700 + 32 * math.sin(min(t, 5.0) * 7.5)
    if t > 5.0:                       # tensión: tiembla
        sh = seg(t, 5.0, 7.4)
        x += 5 * sh * math.sin(t * 61); y += 4 * sh * math.sin(t * 47)
    if t > REVELACION:                # salta hacia atrás del susto
        j = seg(t, REVELACION, REVELACION + 0.5)
        x += 40 * j; y -= 40 * math.sin(math.pi * clamp((t - REVELACION) / 0.6)) + 10 * j
    return x, y


def pencil(t, night):
    tx, ty = tip_pos(t)
    rise = lerp(420, 0, seg(t, 0, 0.8))          # entra desde abajo
    ty += rise
    tilt = -ANG + (6 * seg(t, REVELACION, REVELACION + 0.5)) + 2 * math.sin(t * 2.3)
    L = 740
    g = [f"<g transform='translate({tx:.1f},{ty:.1f}) rotate({tilt:.2f})'>"]
    # sombra sobre la mesa (no rotada aproximada)
    g.append(f"<path d='M8 10 L{L} 30 L{L} 70 L8 22 Z' fill='#000' opacity='0.12'/>")
    # cono de madera y mina
    g.append(f"<path d='M0 0 L120 -66 L120 66 Z' fill='#f4cf98' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M0 0 L42 -23 Q50 0 42 23 Z' fill='#3a3f47' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cuerpo hexagonal amarillo (tres caras)
    g.append(f"<rect x='118' y='-68' width='500' height='136' fill='#ffc93c' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='118' y='-68' width='500' height='34' fill='#ffe07a'/>")
    g.append(f"<rect x='118' y='34' width='500' height='34' fill='#f0a92a'/>")
    g.append(f"<line x1='118' y1='-34' x2='618' y2='-34' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<line x1='118' y1='34' x2='618' y2='34' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<rect x='118' y='-68' width='500' height='136' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # dientes de la madera en la unión
    g.append(f"<path d='M120 -66 Q140 -40 128 -20 Q148 0 128 20 Q140 40 120 66' fill='none' stroke='{INK}' stroke-width='6'/>")
    # virola metálica
    g.append(f"<rect x='618' y='-72' width='62' height='144' rx='8' fill='#c8ced8' stroke='{INK}' stroke-width='{LW}'/>")
    for vx in (634, 650, 666):
        g.append(f"<line x1='{vx}' y1='-68' x2='{vx}' y2='68' stroke='#8a93a3' stroke-width='5'/>")
    # goma rosa
    g.append(f"<path d='M680 -66 L{L - 30} -66 Q{L} -66 {L} -36 L{L} 36 Q{L} 66 {L - 30} 66 L680 66 Z' fill='#ff8fb1' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='690' y='-52' width='30' height='16' rx='8' fill='#ffc3d6'/>")
    g.append("</g>")
    # cara (vertical, sobre el cuerpo)
    fx = tx + 330 * math.cos(math.radians(tilt)); fy = ty + 330 * math.sin(math.radians(tilt))
    blink = 1.0 if (t % 2.7) > 0.13 else 0.12
    wow = seg(t, REVELACION, REVELACION + 0.4)
    er = 26 + 8 * wow
    look_x = lerp(4, -12, seg(t, 2.4, 3.0)) if t < REVELACION else -14
    look_y = lerp(6, 4, seg(t, 2.4, 3.0)) if t < REVELACION else -6
    g.append(f"<g transform='translate({fx:.1f},{fy:.1f})'>")
    for ex in (-30, 30):
        g.append(f"<g transform='translate({ex},-14) scale(1,{blink})'>"
                 f"<ellipse rx='{er:.1f}' ry='{er * 1.15:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{look_x:.1f}' cy='{look_y:.1f}' r='{12 + 2 * wow:.1f}' fill='{INK}'/>"
                 f"<circle cx='{look_x - 4:.1f}' cy='{look_y - 5:.1f}' r='4.5' fill='#fff'/></g>")
    # mejillas
    g.append(f"<ellipse cx='-46' cy='26' rx='12' ry='7' fill='#ff8a5c' opacity='0.7'/>"
             f"<ellipse cx='46' cy='26' rx='12' ry='7' fill='#ff8a5c' opacity='0.7'/>")
    if wow > 0.05:
        g.append(f"<ellipse cx='0' cy='38' rx='{10 + 6 * wow:.1f}' ry='{12 + 8 * wow:.1f}' fill='#7a2a2a' stroke='{INK}' stroke-width='5'/>")
    else:
        worry = seg(t, 5.0, 6.0)
        g.append(f"<path d='M-18 30 Q0 {lerp(48, 34, worry):.1f} 18 30' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def scribble(t, night):
    if t < 0.75:
        return ""
    pts = []
    tt = 0.75
    while tt <= min(t, 5.0):
        x, y = tip_pos(tt); pts.append(f"{x:.1f},{y:.1f}"); tt += 0.04
    x, y = tip_pos(min(t, 5.0)); pts.append(f"{x:.1f},{y:.1f}")
    col = mix("#3a3f47", "#6a7a9a", night)
    return f"<polyline points='{' '.join(pts)}' fill='none' stroke='{col}' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/>"


def lens(t):
    a = rebote(t, 2.45, 0.6)
    gone = seg(t, REVELACION - 0.05, REVELACION + 0.35)
    if a <= 0 or gone >= 1:
        return ""
    cx, cy, r = LENS
    sc = a * (1 + 0.5 * gone)
    heat = seg(t, 5.0, 7.3)
    squeeze = lerp(1.0, 0.62, heat)
    out = [f"<g opacity='{1 - gone:.2f}' transform='translate({cx},{cy}) scale({sc:.3f})'>"]
    # mango
    out.append(f"<line x1='-120' y1='-120' x2='-215' y2='-215' stroke='{INK}' stroke-width='42' stroke-linecap='round'/>"
               f"<line x1='-120' y1='-120' x2='-215' y2='-215' stroke='#8b4a2b' stroke-width='26' stroke-linecap='round'/>")
    out.append(f"<clipPath id='lc'><circle r='{r - 6}'/></clipPath>")
    out.append(f"<circle r='{r}' fill='{mix('#eef6ff', '#ffe2b8', heat)}'/>")
    out.append("<g clip-path='url(#lc)'>")
    # capas de grafito: filas de hexágonos (átomos de carbono) que se deslizan
    shake = 6 * heat
    for row in range(-3, 4):
        ry = row * 62 * squeeze + shake * math.sin(t * 53 + row)
        slide = 22 * math.sin(t * 2.2 + row * 1.3) * (1 - heat)
        col_line = mix("#4b5563", "#c2410c", heat)
        pts = []
        for i in range(-8, 9):
            x = i * 36 + slide + (18 if row % 2 else 0)
            y = ry + (-10 if i % 2 else 10)
            pts.append((x, y))
        out.append("<polyline points='" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
                   f"' fill='none' stroke='{col_line}' stroke-width='6'/>")
        for x, y in pts:
            out.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='9' fill='{mix('#2f343b', '#ff7a1a', heat)}' stroke='{INK}' stroke-width='3'/>")
    out.append("</g>")
    if heat > 0:
        out.append(f"<circle r='{r}' fill='#ff9a3c' opacity='{0.25 * heat * (0.6 + 0.4 * math.sin(t * 20)):.2f}'/>")
    out.append(f"<ellipse cx='-60' cy='-80' rx='50' ry='24' fill='#fff' opacity='0.6' transform='rotate(-35 -60 -80)'/>")
    out.append(f"<circle r='{r}' fill='none' stroke='{INK}' stroke-width='{LW + 4}'/>"
               f"<circle r='{r - 10}' fill='none' stroke='#9aa6b8' stroke-width='10'/>")
    out.append("</g>")
    return "".join(out)


def diamond(t):
    a = rebote(t, REVELACION, 0.6)
    if a <= 0:
        return ""
    cx, cy = DIA
    w, h = 210, 230
    rot = 4 * math.sin(t * 2.5)
    bob = 10 * math.sin(t * 3.1)
    sp = (t * 0.8) % 1.0
    o = [f"<g transform='translate({cx},{cy + bob:.1f}) rotate({rot:.2f}) scale({a:.3f})'>"]
    # halo
    o.append(f"<circle r='330' fill='url(#dh)'/>")
    T = -0.62 * h; G = -0.18 * h; tw = 0.52 * w
    # corona
    o.append(f"<path d='M{-tw} {T} L{tw} {T} L{w} {G} L{-w} {G} Z' fill='#9ff3ff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    o.append(f"<path d='M{-tw} {T} L{-w * 0.35:.0f} {G} L{-w} {G} Z' fill='#6fdcf5'/>")
    o.append(f"<path d='M{tw} {T} L{w * 0.35:.0f} {G} L{w} {G} Z' fill='#d8fbff'/>")
    o.append(f"<path d='M{-tw * 0.35:.0f} {T} L0 {G} L{tw * 0.35:.0f} {T} Z' fill='#e9fdff'/>")
    # pabellón
    o.append(f"<path d='M{-w} {G} L{w} {G} L0 {h} Z' fill='#5fd0ee' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    o.append(f"<path d='M{-w * 0.35:.0f} {G} L0 {h} L{-w} {G} Z' fill='#3fb4dc'/>")
    o.append(f"<path d='M{w * 0.35:.0f} {G} L0 {h} L{w} {G} Z' fill='#a8f0ff'/>")
    # aristas
    for x1, y1, x2, y2 in ((-tw, T, -w * 0.35, G), (tw, T, w * 0.35, G), (-tw * 0.35, T, 0, G), (tw * 0.35, T, 0, G),
                           (-w * 0.35, G, 0, h), (w * 0.35, G, 0, h), (-w, G, 0, h), (w, G, 0, h)):
        o.append(f"<line x1='{x1:.0f}' y1='{y1:.0f}' x2='{x2:.0f}' y2='{y2:.0f}' stroke='{INK}' stroke-width='5'/>")
    o.append(f"<path d='M{-w} {G} L{w} {G}' stroke='{INK}' stroke-width='{LW}'/>")
    o.append(f"<path d='M{-w} {G} L{-tw} {T} L{tw} {T} L{w} {G} L0 {h} Z' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brillo que recorre la piedra
    bx = lerp(-w, w, sp)
    o.append(f"<clipPath id='dc'><path d='M{-w} {G} L{-tw} {T} L{tw} {T} L{w} {G} L0 {h} Z'/></clipPath>"
             f"<g clip-path='url(#dc)'><rect x='{bx - 30:.0f}' y='-300' width='40' height='600' fill='#fff' opacity='0.55' transform='rotate(20 {bx:.0f} 0)'/></g>")
    o.append("</g>")
    return "".join(o)


def star4(x, y, r, col="#fff", op=1.0):
    k = r * 0.22
    return (f"<path d='M{x} {y - r} Q{x + k} {y - k} {x + r} {y} Q{x + k} {y + k} {x} {y + r} "
            f"Q{x - k} {y + k} {x - r} {y} Q{x - k} {y - k} {x} {y - r} Z' fill='{col}' opacity='{op:.2f}'/>")


def frame(t):
    night = seg(t, REVELACION - 0.2, REVELACION + 0.8)
    heat = seg(t, 5.0, 7.3)
    wall_top = mix(mix("#a8e0d8", "#f6c48e", heat * 0.6), "#1d1650", night)
    wall_low = mix(mix("#d4f1ea", "#ffe0b0", heat * 0.6), "#3b2a8a", night)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_top}'/>"
            f"<stop offset='1' stop-color='{wall_low}'/></linearGradient>"
            "<radialGradient id='dh'><stop offset='0' stop-color='#ffffff' stop-opacity='0.95'/>"
            "<stop offset='0.35' stop-color='#9ff3ff' stop-opacity='0.6'/><stop offset='1' stop-color='#5fd0ee' stop-opacity='0'/></radialGradient>"
            "<linearGradient id='wood' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{mix('#d9985a', '#6a4a8a', night * 0.7)}'/><stop offset='1' stop-color='{mix('#b8743c', '#4a3070', night * 0.7)}'/></linearGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    sc = []
    # papel pintado: rombos suaves
    pat = mix(mix("#c2ebe3", "#ffd9a8", heat * 0.6), "#2a2068", night)
    for row in range(0, 15):
        for col in range(0, 9):
            x = col * 135 + (67 if row % 2 else 0); y = row * 100 + 40
            sc.append(f"<path d='M{x} {y - 22} L{x + 16} {y} L{x} {y + 22} L{x - 16} {y} Z' fill='{pat}'/>")
    # rayos de luz en la revelación
    if night > 0:
        cx, cy = DIA
        for i in range(14):
            a0 = math.radians(i * 360 / 14 + t * 14); a1 = a0 + math.radians(9)
            R = 1800
            sc.append(f"<path d='M{cx} {cy} L{cx + R * math.cos(a0):.0f} {cy + R * math.sin(a0):.0f} "
                      f"L{cx + R * math.cos(a1):.0f} {cy + R * math.sin(a1):.0f} Z' fill='#9ff3ff' opacity='{0.16 * night:.2f}'/>")
    # mesa
    sc.append(f"<rect x='-20' y='1390' width='{W + 40}' height='560' fill='url(#wood)' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<rect x='-20' y='1378' width='{W + 40}' height='26' fill='{mix('#e8b07a', '#7a5aa0', night * 0.7)}' stroke='{INK}' stroke-width='{LW}'/>")
    for py, x0, x1 in ((1500, 40, 380), (1610, 600, 1040), (1760, 80, 460), (1850, 640, 1000)):
        sc.append(f"<path d='M{x0} {py} Q{(x0 + x1) / 2} {py - 14} {x1} {py}' fill='none' stroke='{mix('#a5652f', '#3a2560', night * 0.7)}' stroke-width='6' stroke-linecap='round'/>")
    # papel
    sc.append(f"<g transform='rotate(-4 400 1660)'><rect x='30' y='1470' width='760' height='400' rx='10' fill='#000' opacity='0.15' transform='translate(12,12)'/>"
              f"<rect x='30' y='1470' width='760' height='400' rx='10' fill='{mix('#fffdf6', '#d9dcff', night * 0.6)}' stroke='{INK}' stroke-width='{LW}'/>")
    for ly in range(1540, 1860, 55):
        sc.append(f"<line x1='50' y1='{ly}' x2='770' y2='{ly}' stroke='#8fc3ea' stroke-width='4'/>")
    sc.append(f"<line x1='120' y1='1475' x2='120' y2='1865' stroke='#ff8a8a' stroke-width='4'/></g>")
    sc.append(scribble(t, night))
    # polvo de grafito que cae de la punta
    if t < 5.0:
        tx, ty = tip_pos(t)
        for dx, ph, r in CRUMBS:
            k = (t * 1.7 + ph) % 1.0
            sc.append(f"<circle cx='{tx - 20 + dx - 40 * k:.0f}' cy='{ty + 20 + 30 * k:.0f}' r='{r * (1 - k):.1f}' fill='#4b5563' opacity='{0.7 * (1 - k):.2f}'/>")
    sc.append(pencil(t, night))
    sc.append(lens(t))
    # líneas de presión/calor alrededor de la lupa
    if 5.0 < t < REVELACION:
        cx, cy, r = LENS
        for i in range(8):
            a = math.radians(i * 45 + 20)
            d = r + 30 + 14 * math.sin(t * 18 + i)
            sc.append(f"<line x1='{cx + d * math.cos(a):.0f}' y1='{cy + d * math.sin(a):.0f}' x2='{cx + (d + 50) * math.cos(a):.0f}' "
                      f"y2='{cy + (d + 50) * math.sin(a):.0f}' stroke='#ff7a1a' stroke-width='10' stroke-linecap='round' opacity='{heat:.2f}'/>")
    sc.append(diamond(t))
    # destellos alrededor del diamante
    if night > 0:
        cx, cy = DIA
        for dx, dy, r, ph in SPARK:
            tw = max(0.0, math.sin(t * 5 + ph))
            sc.append(star4(cx + dx, cy + dy, r * (0.5 + 0.5 * tw), "#ffffff", night * tw))
    # motas flotando en el aire
    for mx, my, mr, sp, ph in MOTES:
        yy = (my - t * sp) % 1900
        col = mix("#ffffff", "#bff6ff", night)
        sc.append(f"<circle cx='{mx + 18 * math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='{col}' opacity='{0.35 + 0.3 * night:.2f}'/>")
    # destello blanco en el instante de la revelación
    fl = clamp(1 - abs(t - REVELACION - 0.05) / 0.25)
    z = 1 + 0.03 * seg(t, 0, REVELACION) + 0.10 * seg(t, REVELACION, 10)
    s.append(zoom(480, 1380, z, "".join(sc)))
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff' opacity='{0.85 * fl:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
