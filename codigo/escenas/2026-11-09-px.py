"""2026-11-09-px · El pez arquero derriba insectos con un chorro de agua que llega hasta unos 2 m.

Fuentes: Live Science (2014, estudio en Current Biology): dispara a presas "from a distance of up to
6.5 feet (2 meters)"; junta el agua entre la lengua y el paladar y la escupe como un cañón.
Australian Geographic: "shoots a highly targeted jet of water at insects on overhanging branches".
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.45   # el chorro alcanza a la mosca: golpe musical
MUSICA = 6

SURF = 1300                      # nivel del agua
FLY0 = (770, 1046)               # mosca posada en la hoja
S = 1.4                          # escala del pez
MOUTH = (168, -24)               # punta de la mandíbula (coordenadas locales del pez)

rng = np.random.default_rng(23)
BUBBLES = [(rng.uniform(0, W), rng.uniform(SURF + 40, H), rng.uniform(5, 13), rng.uniform(40, 100), rng.uniform(0, 6.28)) for _ in range(26)]
MOTES = [(rng.uniform(0, W), rng.uniform(SURF + 30, H), rng.uniform(2, 4), rng.uniform(0, 6.28)) for _ in range(40)]
DROPS = [(rng.uniform(-1, 1), rng.uniform(-1.2, -0.2), rng.uniform(7, 15)) for _ in range(22)]
SPARK = [(rng.uniform(-260, 260), rng.uniform(-260, 120), rng.uniform(0.6, 1.2), rng.uniform(0, 6.28)) for _ in range(12)]


def fish_state(t):
    """Posición (x, y) y ángulo del pez en el segundo t."""
    fx = lerp(-320, 420, seg(t, 0, 2.4))
    fy = 1620 + 10 * math.sin(t * 2.6) * (1 - seg(t, 2.3, 3))
    ang = 5 * math.sin(t * 3) * (1 - seg(t, 2.3, 3))
    k1 = seg(t, 2.6, 4.8)
    fx, fy, ang = lerp(fx, 432, k1), lerp(fy, 1575, k1), lerp(ang, -30, k1)
    k2 = seg(t, 5.0, 6.5)
    fx, fy, ang = lerp(fx, 437, k2), lerp(fy, 1502, k2), lerp(ang, -50, k2)
    if 5.8 < t < REVELACION:
        ang += 1.5 * math.sin(t * 40) * seg(t, 5.8, 6.4)
    if t >= REVELACION:
        fy += 22 * math.exp(-(t - REVELACION) * 6) * min(1, (t - REVELACION) * 30)
    k3 = seg(t, 7.7, 8.5)
    fx, fy, ang = lerp(fx, 600, k3), lerp(fy, 1500, k3), lerp(ang, -58, k3)
    k4 = seg(t, 8.5, 8.8)
    fy -= 150 * k4
    k5 = seg(t, 8.85, 9.6)
    fx, fy, ang = lerp(fx, 560, k5), lerp(fy, 1610, k5), lerp(ang, -6, k5)
    return fx, fy, ang


def to_world(st, lx, ly):
    fx, fy, ang = st
    a = math.radians(ang)
    return fx + S * (lx * math.cos(a) - ly * math.sin(a)), fy + S * (lx * math.sin(a) + ly * math.cos(a))


def fish(t):
    """Pez arquero original: cuerpo alto y aplanado plateado, 5 manchas negras verticales en el lomo,
    hocico puntiagudo con la mandíbula inferior saliente (boca hacia arriba), ojo grande y aleta
    dorsal muy atrás, frente a la anal."""
    fx, fy, ang = fish_state(t)
    tail = 12 * math.sin(t * (9 if t < 2.5 else 5))
    aim = seg(t, 5.2, 5.6) * (1 - seg(t, 7.0, 7.2))     # entorna el ojo al apuntar
    blink = 0.12 if ((t + 0.7) % 3.2) < 0.12 else 1.0
    wink = 9.3 < t < 9.85
    gulp = seg(t, 8.75, 8.9) * (1 - seg(t, 9.1, 9.5))    # mofletes llenos al tragar
    body = ("M168 -24 L150 -30 Q110 -60 40 -78 Q-40 -86 -120 -50 L-160 -18 L-160 22 "
            "Q-110 62 -40 76 Q60 80 120 40 Q150 16 158 -6 Z")
    g = [f"<g transform='translate({fx:.1f},{fy:.1f}) rotate({ang:.2f}) scale({S})'>",
         "<defs><clipPath id='fb'><path d='" + body + "'/></clipPath></defs>"]
    # cola (ligeramente redondeada)
    g.append(f"<g transform='translate(-156,2) rotate({tail:.1f})'>"
             f"<path d='M0 -18 L-70 -58 Q-92 0 -70 58 L0 18 Z' fill='#d9dee6' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             + "".join(f"<line x1='-6' y1='0' x2='-72' y2='{yy}' stroke='#9aa4b2' stroke-width='4'/>" for yy in (-40, -14, 14, 40))
             + "</g>")
    # aleta dorsal (muy atrás, con radios) y anal enfrente
    g.append(f"<path d='M-40 -82 L-62 -128 L-150 -60 L-120 -50 Z' fill='#cfd5de' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for xx in (-62, -84, -106, -128):
        g.append(f"<line x1='{xx}' y1='{-120 + (xx + 62) * -0.75:.0f}' x2='{xx + 12}' y2='-70' stroke='#8a94a3' stroke-width='4'/>")
    g.append(f"<path d='M-30 76 L-70 116 L-150 52 L-120 44 Z' fill='#cfd5de' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # cuerpo plateado con brillo
    g.append(f"<path d='{body}' fill='#eef2f6' stroke='{INK}' stroke-width='{LW / S:.1f}' stroke-linejoin='round'/>")
    g.append("<g clip-path='url(#fb)'>")
    g.append("<path d='M-160 30 Q0 90 170 10 L170 120 L-160 120 Z' fill='#d6dde6'/>")
    # 5 manchas negras verticales que bajan desde el lomo
    for bx, w, d in ((64, 17, 34), (14, 18, 28), (-36, 18, 20), (-84, 16, 12), (-128, 13, 4)):
        g.append(f"<path d='M{bx - w} -100 L{bx + w} -100 L{bx + w * 0.55:.0f} {d} Q{bx} {d + 16} {bx - w * 0.55:.0f} {d} Z' fill='#1c1f26'/>")
    g.append("<path d='M-120 -40 Q0 -70 120 -36' fill='none' stroke='#ffffff' stroke-width='8' opacity='0.5'/>")
    g.append("</g>")
    g.append(f"<path d='{body}' fill='none' stroke='{INK}' stroke-width='{LW / S:.1f}' stroke-linejoin='round'/>")
    # boca: mandíbula inferior saliente, hendidura hacia arriba
    g.append(f"<path d='M168 -24 Q140 -14 118 -4' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    if gulp > 0:
        g.append(f"<ellipse cx='108' cy='22' rx='{30 * gulp:.0f}' ry='{22 * gulp:.0f}' fill='#ffb3b3' opacity='0.7'/>")
    # aleta pectoral que se agita
    pf = 14 * math.sin(t * 6)
    g.append(f"<g transform='translate(52,26) rotate({pf:.1f})'><path d='M0 0 Q-40 -18 -66 6 Q-40 26 0 0 Z' fill='#d9dee6' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # ojo grande (parpadea, entorna al apuntar, guiña al final)
    g.append(f"<circle cx='92' cy='-30' r='27' fill='#fff' stroke='{INK}' stroke-width='6'/>")
    if wink:
        g.append(f"<path d='M72 -28 Q92 -12 112 -28' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        sy = blink * (1 - 0.45 * aim)
        g.append(f"<g transform='translate(101,-36) scale(1,{sy:.2f})'><circle r='14' fill='{INK}'/><circle cx='-4' cy='-5' r='5' fill='#fff'/></g>")
        if aim > 0.05:
            g.append(f"<path d='M64 {-52 + 6 * aim:.0f} L122 {-46 + 4 * aim:.0f}' stroke='{INK}' stroke-width='7' stroke-linecap='round' opacity='{aim:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def fly_pos(t):
    if t < REVELACION:
        return FLY0[0], FLY0[1], 0.0
    k = clamp((t - REVELACION) / 1.15)
    x = lerp(FLY0[0], 760, k) + 50 * math.sin(k * math.pi)
    y = FLY0[1] - 70 * math.sin(k * math.pi * 0.9) + (SURF - FLY0[1] + 40) * k * k
    return x, y, 540 * k


def fly(t):
    """Mosca original: cuerpo gris azulado, ojos rojos grandes, alas transparentes."""
    if t > 8.82:
        return ""
    x, y, rot = fly_pos(t)
    buzz = 1 if (2.0 < t < 2.6 or t > REVELACION) else 0
    wa = 22 * math.sin(t * 70) * buzz
    rub = 8 * math.sin(t * 14) if 3.2 < t < 6.4 else 0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"]
    for lx, ln in ((-22, 30), (0, 34), (20, 30)):
        g.append(f"<path d='M{lx} 10 L{lx - 10} {10 + ln * 0.6:.0f} L{lx - 4} {10 + ln:.0f}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M30 4 L{48 + rub:.0f} 18' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<g transform='translate(-6,-14) rotate({-30 + wa:.1f})'><ellipse cx='-26' cy='-16' rx='34' ry='16' fill='#dff4ff' fill-opacity='0.75' stroke='{INK}' stroke-width='5'/></g>")
    g.append(f"<ellipse cx='-14' cy='0' rx='34' ry='20' fill='#4f5d73' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-30 -14 Q-36 0 -30 14 M-16 -18 Q-22 0 -16 18' fill='none' stroke='#2d3646' stroke-width='4'/>")
    g.append(f"<g transform='translate(4,-16) rotate({30 - wa:.1f})'><ellipse cx='-22' cy='-18' rx='32' ry='15' fill='#eaf8ff' fill-opacity='0.8' stroke='{INK}' stroke-width='5'/></g>")
    g.append(f"<circle cx='24' cy='-4' r='16' fill='#5c6a80' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='32' cy='-8' r='11' fill='#e2384a' stroke='{INK}' stroke-width='4'/><circle cx='35' cy='-11' r='3.5' fill='#fff'/>")
    if t > REVELACION:   # mareada: estrellitas
        for i in range(3):
            a = t * 6 + i * 2.1
            g.append(f"<circle cx='{20 + 34 * math.cos(a):.0f}' cy='{-44 + 10 * math.sin(a):.0f}' r='5' fill='#fff27a' stroke='{INK}' stroke-width='2'/>")
    g.append("</g>")
    return "".join(g)


def branch(t):
    sw = 4 * math.sin(t * 1.3)
    hit = math.exp(-max(0, t - REVELACION) * 5) * 10 * math.sin((t - REVELACION) * 30) if t > REVELACION else 0
    g = [f"<g transform='rotate({(sw + hit) * 0.3:.2f},1080,960)'>"]
    g.append(f"<path d='M1100 930 Q900 960 760 1010 Q680 1040 620 1030' fill='none' stroke='{INK}' stroke-width='38' stroke-linecap='round'/>")
    g.append(f"<path d='M1100 930 Q900 960 760 1010 Q680 1040 620 1030' fill='none' stroke='#7a4a2a' stroke-width='22' stroke-linecap='round'/>")
    for i, (lx, ly, a, sc) in enumerate(((990, 950, 40, 1.0), (900, 990, 120, 0.9), (840, 985, 30, 1.0), (700, 1030, 150, 0.85), (640, 1030, 20, 0.8), (1040, 930, 150, 0.9))):
        aa = a + 6 * math.sin(t * 2 + i)
        g.append(f"<g transform='translate({lx},{ly}) rotate({aa:.1f}) scale({sc})'><path d='M0 0 Q50 -34 110 0 Q50 34 0 0 Z' fill='{['#3fae4e', '#2f9443'][i % 2]}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M8 0 L96 0' stroke='#8fdc7a' stroke-width='4'/></g>")
    # hoja donde se posa la mosca
    g.append(f"<path d='M700 1060 Q770 1040 850 1062 Q770 1096 700 1060 Z' fill='#56c25a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M744 1020 L760 1058' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def jet(t, mouth):
    """Chorro de agua de la boca a la mosca (6,9-7,45 s) que luego se rompe en gotas."""
    if t < 6.9 or t > 8.3:
        return ""
    mx, my = mouth
    fx, fy = FLY0[0] - 6, FLY0[1] + 6
    cx, cy = (mx + fx) / 2 - 40, (my + fy) / 2 - 60
    grow = seg(t, 6.9, REVELACION)
    pts = []
    for i in range(31):
        u = i / 30 * grow
        pts.append(((1 - u) ** 2 * mx + 2 * (1 - u) * u * cx + u * u * fx, (1 - u) ** 2 * my + 2 * (1 - u) * u * cy + u * u * fy))
    fade = 1 - seg(t, REVELACION + 0.05, REVELACION + 0.4)
    g = []
    if fade > 0.01 and grow > 0.02:
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        g.append(f"<g opacity='{fade:.2f}'><path d='{d}' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>"
                 f"<path d='{d}' fill='none' stroke='#5fd0ff' stroke-width='14' stroke-linecap='round'/>"
                 f"<path d='{d}' fill='none' stroke='#e8fbff' stroke-width='5' stroke-linecap='round'/></g>")
        hx, hy = pts[-1]
        g.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{16 + 3 * math.sin(t * 30):.0f}' fill='#5fd0ff' stroke='{INK}' stroke-width='6' opacity='{fade:.2f}'/>")
    if t > REVELACION:
        k = t - REVELACION
        for dx, dy, r in DROPS:
            x = FLY0[0] + dx * 300 * k
            y = FLY0[1] + dy * 420 * k + 900 * k * k
            if y < SURF:
                g.append(f"<path d='M{x:.0f} {y - r * 1.6:.0f} Q{x + r:.0f} {y:.0f} {x:.0f} {y + r:.0f} Q{x - r:.0f} {y:.0f} {x:.0f} {y - r * 1.6:.0f} Z' fill='#7fdcff' stroke='{INK}' stroke-width='3'/>")
    return "".join(g)


def splash(t, x0, t0):
    if t < t0 or t > t0 + 1.0:
        return ""
    k = (t - t0) / 1.0
    g = [f"<ellipse cx='{x0}' cy='{SURF + 6}' rx='{40 + 160 * k:.0f}' ry='{10 + 30 * k:.0f}' fill='none' stroke='#e8fbff' stroke-width='{8 * (1 - k) + 1:.1f}' opacity='{1 - k:.2f}'/>"]
    for i in range(7):
        a = math.radians(-160 + i * 23)
        r = 140 * k
        x = x0 + r * math.cos(a); y = SURF + r * math.sin(a) * 1.2 + 260 * k * k
        if y < SURF + 10:
            g.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{11 * (1 - k * 0.5):.0f}' fill='#7fdcff' stroke='{INK}' stroke-width='3'/>")
    return "".join(g)


def frame(t):
    flash = seg(t, REVELACION, REVELACION + 0.1) * (1 - seg(t, REVELACION + 0.1, REVELACION + 1.2))
    tense = seg(t, 5.0, 6.8) * (1 - seg(t, REVELACION, REVELACION + 0.5))
    skyt = mix(mix("#6cc8f5", "#4b9fd6", tense), "#fff3c0", 0.6 * flash)
    skyb = mix(mix("#d8f3ff", "#b0dcf2", tense), "#fffbe6", 0.6 * flash)
    wt = mix("#2fb0b4", "#21848c", tense); wb = mix("#0f5a6e", "#0a4252", tense)
    st = fish_state(t)
    mouth = to_world(st, *MOUTH)
    z = 1 + 0.13 * seg(t, REVELACION, 9.6)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{skyt}'/><stop offset='1' stop-color='{skyb}'/></linearGradient>"
            f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wt}'/><stop offset='1' stop-color='{wb}'/></linearGradient>"
            "<linearGradient id='ray' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='0.28'/><stop offset='1' stop-color='#ffffff' stop-opacity='0'/></linearGradient>"
            "<radialGradient id='burst'><stop offset='0' stop-color='#ffffff' stop-opacity='0.9'/><stop offset='0.4' stop-color='#fff1a8' stop-opacity='0.55'/><stop offset='1' stop-color='#fff1a8' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    c = []
    # nubes
    for i, (cx, cy, sc) in enumerate(((180, 420, 1.3), (760, 300, 1.0), (520, 700, 0.9))):
        dx = (t * 16 * (1 + 0.3 * i)) % 1500 - 300
        c.append(f"<g transform='translate({(cx + dx) % 1500 - 250:.0f},{cy}) scale({sc})'><path d='M0 50 Q10 0 70 10 Q100 -40 160 0 Q230 -10 240 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # orilla lejana con manglares
    c.append(f"<path d='M0 1180 Q120 1110 240 1170 Q360 1090 500 1160 Q640 1100 780 1170 Q900 1120 1080 1160 L1080 {SURF} L0 {SURF} Z' fill='#4f9e58' stroke='{INK}' stroke-width='7'/>")
    c.append(f"<path d='M0 1230 Q200 1190 420 1230 Q680 1200 1080 1235 L1080 {SURF} L0 {SURF} Z' fill='#3a8447' stroke='{INK}' stroke-width='7'/>")
    # manglar a la izquierda con raíces
    c.append(f"<path d='M-20 980 Q90 940 130 1040 Q160 1120 120 1200 L-20 1200 Z' fill='#2f8a3e' stroke='{INK}' stroke-width='{LW}'/>")
    for rx in (20, 60, 100):
        c.append(f"<path d='M{rx} 1150 Q{rx + 40} 1240 {rx + 20} 1420' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/><path d='M{rx} 1150 Q{rx + 40} 1240 {rx + 20} 1420' fill='none' stroke='#7a4a2a' stroke-width='10' stroke-linecap='round'/>")
    c.append(branch(t))
    # agua
    wv = " ".join(f"L{x} {SURF + 8 * math.sin(x / 70 + t * 2.4):.1f}" for x in range(0, W + 41, 40))
    c.append(f"<path d='M0 {SURF} {wv} L{W} {H} L0 {H} Z' fill='url(#sea)' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(5):
        x = 80 + i * 230 + 30 * math.sin(t * 0.8 + i)
        c.append(f"<polygon points='{x:.0f},{SURF + 10} {x + 90:.0f},{SURF + 10} {x + 220:.0f},{H} {x + 60:.0f},{H}' fill='url(#ray)'/>")
    for x, y, r, sp, ph in BUBBLES:
        yy = (y - t * sp - SURF - 40) % (H - SURF - 40) + SURF + 40
        c.append(f"<circle cx='{x + 10 * math.sin(t * 2 + ph):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#bff2ff' fill-opacity='0.35' stroke='#e8fbff' stroke-width='3'/>")
    for x, y, r, ph in MOTES:
        c.append(f"<circle cx='{x + 14 * math.sin(t + ph):.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#d9fff5' opacity='0.4'/>")
    # plantas del fondo
    for i, bx in enumerate((200, 820, 980)):
        sw = 20 * math.sin(t * 1.5 + i)
        c.append(f"<path d='M{bx} {H} Q{bx - 30 + sw:.0f} {H - 130} {bx + sw:.0f} {H - 240} Q{bx + 30 + sw:.0f} {H - 120} {bx + 40} {H} Z' fill='#2c8a4e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    if flash > 0:
        c.append(f"<circle cx='{FLY0[0]}' cy='{FLY0[1]}' r='{120 + 380 * seg(t, REVELACION, REVELACION + 0.6):.0f}' fill='url(#burst)' opacity='{flash:.2f}'/>")
    c.append(fish(t))
    c.append(jet(t, mouth))
    c.append(fly(t))
    c.append(splash(t, 760, 8.55))
    c.append(splash(t, int(mouth[0]), 9.0))
    # brillos de felicidad al final
    sp = seg(t, 9.0, 9.4)
    if sp > 0:
        fx, fy, _ = st
        for dx, dy, sc, ph in SPARK:
            a = sp * (0.6 + 0.4 * math.sin(t * 8 + ph))
            c.append(f"<g transform='translate({fx + dx:.0f},{fy + dy:.0f}) rotate({t * 90 + ph * 50:.0f}) scale({sc * a:.2f})'>"
                     f"<path d='M0 -24 L6 -6 L24 0 L6 6 L0 24 L-6 6 L-24 0 L-6 -6 Z' fill='#fff27a' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/></g>")
    s.append(zoom(660, 1280, z, "".join(c)))
    s.append("</svg>")
    return "".join(s)
