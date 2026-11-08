"""2026-11-08-c3 · El ojo ve el mundo al revés: la imagen llega invertida a la retina y el cerebro la endereza.

0-2,5 s  un ojo gigante (en corte, con párpado que parpadea) entra flotando y mira un manzano.
2,5-5 s  rayos de luz salen del árbol, entran por la pupila y se cruzan en el cristalino.
5-7,5 s  en el fondo del ojo (la retina) va apareciendo un árbol pequeño... boca abajo.
7,5-10 s REVELACION: la retina se ilumina, zoom de cámara, impulsos por el nervio óptico hasta
         un cerebro con cara que se enciende y muestra el árbol del derecho.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 6

EY = 1390                      # centro vertical del ojo
ER = 210                       # radio del ojo
TREE_X = 205                   # tronco del árbol
TOP_Y, BOT_Y = 1065, 1535      # copa y base del árbol
BRAIN = (905, 1748)

rng = np.random.default_rng(23)
FLOWERS = [(rng.uniform(30, 1050), rng.uniform(1600, 1890), rng.uniform(0.7, 1.2), rng.choice(["#ff6b8b", "#ffd23f", "#ffffff", "#b388ff"])) for _ in range(16)]
GRASS = [(rng.uniform(0, W), rng.uniform(1560, 1900), rng.uniform(26, 46), rng.uniform(0, 6.28)) for _ in range(40)]
SPARK = [(rng.uniform(-300, 300), rng.uniform(-260, 260), rng.uniform(10, 22), rng.uniform(0, 6.28)) for _ in range(14)]
APPLES = [(-70, -40), (55, -70), (85, 25), (-25, 35), (-95, 50), (20, -120)]


def eye_x(t):
    return lerp(1260, 640, seg(t, 0, 2.0))


def tree(sway=0.0, simple=False):
    """Manzano original: tronco marrón, copa de tres círculos verdes y manzanas rojas.
    Coordenadas relativas al pie del tronco (0,0); altura total 470."""
    g = [f"<g transform='rotate({sway:.2f})'>"]
    lw = LW if not simple else 14
    g.append(f"<path d='M-26 0 Q-20 -150 -18 -250 L18 -250 Q20 -150 26 0 Z' fill='#9b5a2f' stroke='{INK}' stroke-width='{lw}' stroke-linejoin='round'/>")
    g.append(f"<path d='M0 -230 L-55 -290 M0 -210 L48 -270' stroke='{INK}' stroke-width='{lw + 10}' stroke-linecap='round'/>")
    g.append(f"<path d='M0 -230 L-55 -290 M0 -210 L48 -270' stroke='#9b5a2f' stroke-width='{lw}' stroke-linecap='round'/>")
    for cx, cy, r in ((-75, -320, 95), (75, -320, 95), (0, -375, 105)):
        g.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#3fae4f' stroke='{INK}' stroke-width='{lw}'/>")
    for cx, cy, r in ((-75, -320, 87), (75, -320, 87), (0, -375, 97)):
        g.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#4cc25c'/>")
    g.append("<path d='M-120 -360 Q-90 -420 -30 -430' stroke='#8ee08f' stroke-width='16' fill='none' stroke-linecap='round'/>")
    for ax, ay in APPLES:
        g.append(f"<circle cx='{ax}' cy='{ay - 330}' r='20' fill='#e8383d' stroke='{INK}' stroke-width='{6 if not simple else 10}'/>")
        if not simple:
            g.append(f"<circle cx='{ax - 6}' cy='{ay - 336}' r='6' fill='#ffb3b3'/>")
    g.append("</g>")
    return "".join(g)


def eye(t, glow, img):
    cx = eye_x(t); cy = EY + 8 * math.sin(t * 2.2)
    g = [f"<g transform='translate({cx:.1f},{cy:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='{ER + 95}' rx='170' ry='18' fill='#000' opacity='0.15'/>")
    # nervio óptico (detrás) hacia el cerebro
    bx, by = BRAIN[0] - cx, BRAIN[1] - cy
    nerve = f"M{ER - 10} 10 C{ER + 120} 40 {bx + 40} {by - 230} {bx + 5} {by - 95}"
    g.append(f"<path d='{nerve}' fill='none' stroke='{INK}' stroke-width='52' stroke-linecap='round'/>")
    g.append(f"<path d='{nerve}' fill='none' stroke='{mix('#f2c46d', '#ffe9a6', glow)}' stroke-width='36' stroke-linecap='round'/>")
    # globo ocular
    g.append(f"<circle r='{ER}' fill='#fbf7f0' stroke='{INK}' stroke-width='{LW}'/>")
    for a, l in ((-35, 70), (20, 60), (55, 50), (-60, 55)):
        x0 = ER * 0.97 * math.cos(math.radians(a)); y0 = ER * 0.97 * math.sin(math.radians(a))
        x1 = x0 - l * math.cos(math.radians(a)); y1 = y0 - l * math.sin(math.radians(a))
        g.append(f"<path d='M{x0:.0f} {y0:.0f} Q{(x0 + x1) / 2 + 12:.0f} {(y0 + y1) / 2 - 10:.0f} {x1:.0f} {y1:.0f}' stroke='#f08a8a' stroke-width='4' fill='none' opacity='0.7'/>")
    # retina (fondo del ojo)
    ret = mix("#ff8fa3", "#ffe14d", glow)
    a0, a1 = math.radians(-62), math.radians(62)
    rr = ER - 22
    g.append(f"<path d='M{rr * math.cos(a0):.1f} {rr * math.sin(a0):.1f} A{rr} {rr} 0 0 1 {rr * math.cos(a1):.1f} {rr * math.sin(a1):.1f}' fill='none' stroke='{ret}' stroke-width='26' stroke-linecap='round'/>")
    if glow > 0:
        g.append(f"<circle cx='{ER - 40}' cy='0' r='{lerp(60, 170, glow):.0f}' fill='url(#retglow)'/>")
    # árbol invertido en la retina
    if img > 0:
        s = 0.31
        g.append(f"<g opacity='{img:.2f}' transform='translate({ER - 70},{0}) scale({s},{-s}) translate(0,{235})'>{tree(0, simple=True)}</g>")
    # córnea
    g.append(f"<path d='M{-ER + 28} -110 Q{-ER - 75} 0 {-ER + 28} 110' fill='#bfe9ff' fill-opacity='0.85' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # iris (dos piezas) y pupila (hueco)
    g.append(f"<rect x='{-ER + 22}' y='-112' width='30' height='82' rx='12' fill='#3d8fe0' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='{-ER + 22}' y='30' width='30' height='82' rx='12' fill='#3d8fe0' stroke='{INK}' stroke-width='6'/>")
    # cristalino
    g.append(f"<ellipse cx='{-ER + 82}' cy='0' rx='30' ry='74' fill='#fff1c9' fill-opacity='0.9' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='{-ER + 74}' cy='-28' rx='8' ry='22' fill='#fff'/>")
    # párpados con pestañas (sector alrededor de la parte delantera): se cierran al parpadear
    bl = (t % 2.9) < 0.18 and t < REVELACION - 0.3
    edge = 183 if bl else 150                 # ángulo del borde del párpado (grados)
    r0, r1 = ER - 8, (ER + 78 if bl else ER + 34)
    for sgn in (-1, 1):
        a_out, a_in = math.radians(sgn * 122), math.radians(sgn * edge)
        def P(r, a): return f"{r * math.cos(a):.1f} {r * math.sin(a):.1f}"
        sweep = 0 if sgn < 0 else 1
        d = (f"M{P(r0, a_out)} L{P(r1, a_out)} A{r1} {r1} 0 0 {sweep} {P(r1, a_in)} "
             f"L{P(r0, a_in)} A{r0} {r0} 0 0 {1 - sweep} {P(r0, a_out)} Z")
        g.append(f"<path d='{d}' fill='#f6b98d' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        for i in range(3):
            aa = math.radians(sgn * (edge - 4 - i * 9))
            x0, y0 = (r1 - 6) * math.cos(aa), (r1 - 6) * math.sin(aa)
            x1, y1 = (r1 + 26) * math.cos(aa) - 6, (r1 + 26) * math.sin(aa)
            g.append(f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{x1:.1f}' y2='{y1:.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g), cx, cy


def rays(t, cx, cy, k, glow):
    """Haz de luz desde la copa y desde la base del árbol; se cruzan en el cristalino."""
    if k <= 0:
        return ""
    lx = cx - ER + 82
    pts_top = [(TREE_X, TOP_Y + 20), (lx, cy - 42), (cx + ER - 40, cy + 60)]
    pts_bot = [(TREE_X, BOT_Y - 10), (lx, cy + 42), (cx + ER - 40, cy - 60)]
    g = []
    for pts, col in ((pts_top, "#ffe14d"), (pts_bot, "#ffb347")):
        d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f} L{pts[1][0]:.0f} {pts[1][1]:.0f} L{pts[2][0]:.0f} {pts[2][1]:.0f}"
        L = 1000
        off = L * (1 - k)
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round' stroke-linejoin='round' stroke-dasharray='{L} {L}' stroke-dashoffset='{off:.0f}' opacity='0.8'/>")
        g.append(f"<path d='{d}' fill='none' stroke='{mix(col, '#fffbe0', glow)}' stroke-width='12' stroke-linecap='round' stroke-linejoin='round' stroke-dasharray='{L} {L}' stroke-dashoffset='{off:.0f}'/>")
        # destellos que viajan por el rayo
        if k >= 1:
            g.append(f"<path d='{d}' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round' stroke-dasharray='14 60' stroke-dashoffset='{-t * 160:.0f}'/>")
    return "".join(g)


def brain(t, glow, show):
    bx, by = BRAIN
    sc = rebote(t, 0.4, 0.6) if t < 1.2 else 1.0
    bob = 4 * math.sin(t * 3.1)
    col = mix("#ff9fb5", "#ffc2d1", glow)
    g = [f"<g transform='translate({bx},{by + bob:.1f}) scale({sc:.3f})'>"]
    if glow > 0:
        g.append(f"<circle r='{lerp(80, 180, glow):.0f}' fill='url(#brglow)'/>")
    g.append(f"<path d='M-95 20 C-120 -40 -80 -95 -30 -88 C-10 -112 40 -110 55 -85 C100 -90 125 -40 105 0 C125 30 95 70 60 62 C40 85 -10 85 -30 66 C-70 80 -105 60 -95 20 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for d in ("M-60 -50 Q-40 -30 -60 -10", "M-10 -80 Q5 -55 -15 -40", "M40 -70 Q60 -50 45 -30", "M75 -20 Q60 0 80 20", "M0 0 L0 0"):
        g.append(f"<path d='{d}' fill='none' stroke='#d9667f' stroke-width='6' stroke-linecap='round'/>")
    blink = 1.0 if ((t + 1.1) % 3.3) > 0.14 else 0.12
    for ex in (-28, 28):
        g.append(f"<g transform='translate({ex},10) scale(1,{blink})'><ellipse rx='13' ry='16' fill='{INK}'/><circle cx='-4' cy='-6' r='5' fill='#fff'/></g>")
    smile = lerp(8, 22, glow)
    g.append(f"<path d='M-16 36 Q0 {36 + smile:.0f} 16 36' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<circle cx='-50' cy='34' r='10' fill='#ff6b8b' opacity='0.6'/><circle cx='50' cy='34' r='10' fill='#ff6b8b' opacity='0.6'/>")
    g.append("</g>")
    # burbuja con el árbol del derecho
    if show > 0:
        s = rebote(t, REVELACION + 1.0, 0.5)
        g.append(f"<g transform='translate(640,1770) scale({s:.3f})'>"
                 f"<circle cx='95' cy='-20' r='12' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle r='80' fill='#fffbe8' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<g transform='translate(0,58) scale(0.24)'>{tree(0, simple=True)}</g></g>")
    return "".join(g)


def frame(t):
    glow = seg(t, REVELACION - 0.1, REVELACION + 0.5)
    k_rays = seg(t, 2.4, 4.4)
    img = seg(t, 5.0, 7.0)
    pulse = seg(t, REVELACION + 0.1, REVELACION + 1.0)
    show = float(t >= REVELACION + 1.0)
    top = mix("#5fb8ff", "#2a3f9e", 0.35 * glow); low = mix("#d6f1ff", "#ffe9b0", glow)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='sun'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.9'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='retglow'><stop offset='0' stop-color='#fff6b0' stop-opacity='0.9'/><stop offset='1' stop-color='#ffe14d' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='brglow'><stop offset='0' stop-color='#fff6b0' stop-opacity='0.9'/><stop offset='1' stop-color='#ffb3c6' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='1'/><stop offset='1' stop-color='#ffffff' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol suave y nubes lentas (fondo tranquilo arriba)
    s.append(f"<circle cx='880' cy='760' r='230' fill='url(#sun)'/>")
    s.append(f"<circle cx='880' cy='760' r='78' fill='#ffe14d' stroke='#ffb347' stroke-width='8'/>")
    for i, (cx, cy, sc) in enumerate([(160, 880, 1.2), (760, 1010, 1.0), (430, 620, 0.9)]):
        dx = (t * 12 * (1 + 0.3 * i)) % 1400 - 250
        s.append(f"<g transform='translate({(cx + dx) % 1400 - 200:.0f},{cy}) scale({sc})' opacity='0.95'>"
                 f"<path d='M0 40 Q15 -15 75 0 Q105 -45 165 -5 Q230 -20 245 40 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    z = 1 + 0.12 * seg(t, REVELACION - 0.1, 9.6)
    w = []
    # colinas y suelo
    w.append(f"<path d='M0 1470 Q260 1400 520 1460 T1080 1440 L1080 1920 L0 1920 Z' fill='#7fd16b' stroke='{INK}' stroke-width='{LW}'/>")
    w.append(f"<path d='M0 1580 Q300 1520 620 1570 T1080 1560 L1080 1920 L0 1920 Z' fill='#5fbf4e' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, gy, gh, ph in GRASS:
        sw = 8 * math.sin(t * 2.4 + ph)
        w.append(f"<path d='M{gx:.0f} {gy:.0f} Q{gx + sw * 0.5:.0f} {gy - gh / 2:.0f} {gx + sw:.0f} {gy - gh:.0f}' stroke='#3a9a3a' stroke-width='6' fill='none' stroke-linecap='round'/>")
    for fx, fy, fs, fc in FLOWERS:
        w.append(f"<g transform='translate({fx:.0f},{fy:.0f}) scale({fs:.2f}) rotate({t * 20:.0f})'>"
                 + "".join(f"<circle cx='{12 * math.cos(a):.1f}' cy='{12 * math.sin(a):.1f}' r='9' fill='{fc}' stroke='{INK}' stroke-width='3'/>" for a in np.linspace(0, 2 * math.pi, 6)[:-1])
                 + f"<circle r='7' fill='#ffb000' stroke='{INK}' stroke-width='3'/></g>")
    # árbol
    w.append(f"<ellipse cx='{TREE_X}' cy='{BOT_Y + 8}' rx='140' ry='20' fill='#000' opacity='0.18'/>")
    w.append(f"<g transform='translate({TREE_X},{BOT_Y})'>{tree(1.6 * math.sin(t * 1.7))}</g>")
    # mariposa
    bxp = 330 + 120 * math.sin(t * 0.9); byp = 1230 + 50 * math.sin(t * 1.7)
    fl = 0.35 + 0.65 * abs(math.sin(t * 12))
    w.append(f"<g transform='translate({bxp:.0f},{byp:.0f})'><g transform='scale({fl:.2f},1)'>"
             f"<path d='M0 0 C-30 -40 -50 -10 -30 8 C-45 25 -20 35 0 8 Z' fill='#ff7ab6' stroke='{INK}' stroke-width='4'/>"
             f"<path d='M0 0 C30 -40 50 -10 30 8 C45 25 20 35 0 8 Z' fill='#ff7ab6' stroke='{INK}' stroke-width='4'/></g>"
             f"<rect x='-3' y='-10' width='6' height='24' rx='3' fill='{INK}'/></g>")
    ex, ecx, ecy = eye(t, glow, img)
    w.append(brain(t, pulse, show))
    w.append(ex)
    w.append(rays(t, ecx, ecy, k_rays, glow))
    # impulsos por el nervio óptico
    if REVELACION < t < REVELACION + 1.3:
        for j in range(3):
            q = clamp((t - REVELACION - 0.12 * j) / 0.9)
            if 0 < q < 1:
                p0 = (ecx + ER - 10, ecy + 10); p3 = (BRAIN[0] + 5, BRAIN[1] - 95)
                p1 = (ecx + ER + 120, ecy + 40); p2 = (BRAIN[0] + 40, BRAIN[1] - 230)
                u = 1 - q
                px = u ** 3 * p0[0] + 3 * u * u * q * p1[0] + 3 * u * q * q * p2[0] + q ** 3 * p3[0]
                py = u ** 3 * p0[1] + 3 * u * u * q * p1[1] + 3 * u * q * q * p2[1] + q ** 3 * p3[1]
                w.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='16' fill='#fffbe0' stroke='#ffb347' stroke-width='5'/>")
    # chispas de la revelación
    if glow > 0:
        for sx, sy, sr, ph in SPARK:
            a = glow * (0.5 + 0.5 * math.sin(t * 6 + ph))
            px, py = ecx + sx, ecy + sy
            w.append(f"<path d='M{px:.0f} {py - sr:.0f} L{px + sr * 0.3:.0f} {py:.0f} L{px:.0f} {py + sr:.0f} L{px - sr * 0.3:.0f} {py:.0f} Z' fill='#fff6b0' opacity='{a:.2f}'/>")
    s.append(zoom(640, 1600, z, "".join(w)))
    fl = clamp(1 - abs(t - REVELACION - 0.05) / 0.35)
    if fl > 0:
        s.append(f"<circle cx='{ecx + ER - 40:.0f}' cy='{ecy:.0f}' r='900' fill='url(#flash)' opacity='{0.75 * fl:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
