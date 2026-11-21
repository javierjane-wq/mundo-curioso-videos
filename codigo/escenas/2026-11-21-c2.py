"""2026-11-21-c2 · Las rocas que «se mueven solas» en Racetrack Playa (Valle de la Muerte).

Una roca con ojos se desliza por el lecho seco de un lago dejando un surco larguísimo. Cae la
noche, el suelo se encharca y se hiela; al amanecer (REVELACION) el hielo se rompe en placas,
sopla el viento y las placas empujan a la roca. Zoom sobre la roca sorprendida.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.3    # amanece: el hielo se rompe en placas y el viento empuja la roca
MUSICA = 8

rng = np.random.default_rng(21)
STARS = [(rng.uniform(0, W), rng.uniform(80, 1050), rng.uniform(2.5, 5.5), rng.uniform(0, 6.28)) for _ in range(80)]
HOR = 1190  # horizonte (borde del lago seco)


def trail_y(x):
    """Curva del surco de la roca protagonista."""
    return 1695 + 30 * math.sin((x + 120) / 260)


def _cracks():
    """Grietas del barro seco: filas que se separan con la perspectiva, ladrillos irregulares."""
    out = []
    y = HOR + 22; fila = 0; r = np.random.default_rng(5)
    while y < H + 40:
        paso = 18 + (y - HOR) * 0.11
        ys = y
        pts = []
        for x in range(-40, W + 80, 60):
            pts.append((x, ys + r.uniform(-paso * 0.18, paso * 0.18)))
        out.append(("h", pts, 2 + (y - HOR) / 260))
        ancho = 70 + (y - HOR) * 0.35
        x = r.uniform(-ancho, 0) + (fila % 2) * ancho / 2
        while x < W + 40:
            out.append(("v", [(x, ys), (x + r.uniform(-12, 12), ys + paso)], 2 + (y - HOR) / 260))
            x += ancho * r.uniform(0.75, 1.25)
        y += paso; fila += 1
    return out


CRACKS = _cracks()


def _panels():
    """Placas de hielo rotas (rejilla irregular) alrededor de la roca."""
    r = np.random.default_rng(9)
    cols, rows = 7, 5
    x0, y0, cw, ch = -260, 1330, 230, 130
    P = [[(x0 + i * cw + r.uniform(-60, 60), y0 + j * ch + r.uniform(-30, 30)) for i in range(cols + 1)] for j in range(rows + 1)]
    cells = []
    for j in range(rows):
        for i in range(cols):
            q = [P[j][i], P[j][i + 1], P[j + 1][i + 1], P[j + 1][i]]
            cx = sum(p[0] for p in q) / 4; cy = sum(p[1] for p in q) / 4
            q = [(cx + (px - cx) * 0.9, cy + (py - cy) * 0.86) for px, py in q]
            cells.append((q, r.uniform(0.85, 1.15), r.uniform(-3, 3)))
    return cells


PANELS = _panels()
BG_ROCKS = [(250, 1300, 38, 120), (830, 1255, 26, 220), (960, 1420, 44, 330)]


def rock_x(t):
    x = lerp(170, 600, seg(t, 0, 2.5))
    x += 160 * seg(t, REVELACION, 10.4)          # el hielo y el viento la empujan
    return x


def rock(t, x):
    y = trail_y(x)
    noche = seg(t, 5.0, 6.4) * (1 - seg(t, REVELACION - 0.15, REVELACION + 0.3))
    shiver = 3.5 * math.sin(t * 55) * noche
    sliding = t < 2.55 or t > REVELACION
    tilt = 2.5 * math.sin(t * 9) if sliding else 1.2 * math.sin(t * 2.2)
    sorpresa = seg(t, REVELACION, REVELACION + 0.35)
    blink = 0.12 if ((t + 0.4) % 2.9) < 0.13 and sorpresa < 0.5 else 1.0
    look_back = seg(t, 2.8, 3.4) * (1 - seg(t, 4.6, 5.1))       # mira su huella
    look_up = seg(t, 5.3, 5.9) * (1 - seg(t, REVELACION - 0.1, REVELACION + 0.2))
    lx = lerp(0, -12, look_back) + lerp(0, 8, sorpresa * 0)
    ly = lerp(0, -10, look_up)
    eye_s = 1 + 0.25 * sorpresa
    g = [f"<g transform='translate({x + shiver:.1f},{y:.1f}) rotate({tilt:.2f}) scale(1.32)'>"]
    g.append("<ellipse cx='0' cy='42' rx='175' ry='30' fill='#000' opacity='0.2'/>")
    body = ("M-160 30 C-175 -30 -150 -95 -95 -128 C-40 -160 40 -168 95 -140 "
            "C150 -112 178 -55 168 0 C162 32 120 48 0 48 C-110 48 -152 44 -160 30 Z")
    g.append(f"<path d='{body}' fill='#8e8176' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("<path d='M-120 -95 C-70 -140 30 -150 90 -120 C40 -128 -50 -120 -105 -78 Z' fill='#b1a497'/>")
    g.append(f"<path d='M-150 22 C-90 36 80 38 160 8' fill='none' stroke='#6d6158' stroke-width='10' stroke-linecap='round'/>")
    for sx, sy, sr in ((-110, -10, 9), (120, -40, 7), (60, 15, 6), (-40, -125, 5), (135, 5, 5)):
        g.append(f"<circle cx='{sx}' cy='{sy}' r='{sr}' fill='#6d6158'/>")
    g.append(f"<path d='M95 -100 L118 -70 L105 -40' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    # ojos
    for ex in (-48, 42):
        g.append(f"<g transform='translate({ex},-62) scale({eye_s:.3f},{eye_s * blink:.3f})'>"
                 f"<ellipse rx='30' ry='34' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{lx:.1f}' cy='{ly + 4:.1f}' r='15' fill='{INK}'/>"
                 f"<circle cx='{lx - 5:.1f}' cy='{ly - 3:.1f}' r='5.5' fill='#fff'/></g>")
    # cejas
    cy = lerp(-108, -124, sorpresa) - 6 * noche
    for ex, s in ((-48, 1), (42, -1)):
        g.append(f"<path d='M{ex - 22} {cy + 6 * s * noche:.1f} Q{ex} {cy - 10:.1f} {ex + 22} {cy - 6 * s * noche:.1f}' "
                 f"fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # boca
    if sorpresa > 0.3:
        g.append(f"<ellipse cx='-3' cy='-8' rx='{lerp(6, 16, sorpresa):.1f}' ry='{lerp(6, 20, sorpresa):.1f}' fill='#5a2a22' stroke='{INK}' stroke-width='5'/>")
    elif noche > 0.3:
        g.append(f"<path d='M-24 -10 L-12 -16 L0 -10 L12 -16 L24 -10' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M-22 -14 Q-3 4 18 -14' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # mejillas
    g.append(f"<ellipse cx='-92' cy='-26' rx='16' ry='9' fill='#e98b7a' opacity='{0.55 * (1 - noche):.2f}'/>")
    g.append(f"<ellipse cx='88' cy='-26' rx='16' ry='9' fill='#e98b7a' opacity='{0.55 * (1 - noche):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    noche = seg(t, 4.9, 6.4)                       # 0 día -> 1 noche
    alba = seg(t, REVELACION - 0.15, REVELACION + 0.5)  # amanecer brusco
    hielo = seg(t, 5.8, 7.0)                       # el charco se congela
    roto = seg(t, REVELACION, REVELACION + 0.25)   # el hielo se rompe en placas
    flash = math.exp(-max(0.0, t - REVELACION) * 4) if t >= REVELACION else 0.0

    def tri(dia, nch, amn):
        return mix(mix(dia, nch, noche), amn, alba)
    top = tri("#4fa8f0", "#0d1238", "#5aa9ec"); mid = tri("#9fd2f7", "#25275a", "#ffc4a0"); low = tri("#ffe7bd", "#4a3a70", "#ffd38a")
    x = rock_x(t); ry = trail_y(x)
    z = 1 + 0.24 * seg(t, REVELACION, 8.15)
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d' viewBox='0 0 %d %d'>" % (W, H, W, H), "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
         f"<stop offset='0.62' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='sol'><stop offset='0' stop-color='#fff8e0' stop-opacity='{0.95 * alba:.3f}'/>"
         f"<stop offset='0.4' stop-color='#ffd27a' stop-opacity='{0.6 * alba:.3f}'/><stop offset='1' stop-color='#ffb060' stop-opacity='0'/></radialGradient>",
         "<linearGradient id='ice' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#eafaff'/><stop offset='1' stop-color='#9fdcf5'/></linearGradient>",
         "</defs>", f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    s.append(f"<g transform='translate({x:.1f},{ry - 400:.1f}) scale({z:.4f}) translate({-x:.1f},{-(ry - 400):.1f})'>")
    # estrellas y luna
    st = noche * (1 - alba)
    for sx, sy, sr, ph in STARS:
        a = st * (0.55 + 0.45 * math.sin(t * 3 + ph))
        if a > 0.02:
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    if st > 0.02:
        my = lerp(1080, 960, noche)
        s.append(f"<g opacity='{st:.2f}'><circle cx='870' cy='{my:.0f}' r='52' fill='#fff6d8' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='895' cy='{my - 14:.0f}' r='44' fill='{mid}'/></g>")
    # sol del amanecer tras las montañas
    if alba > 0.01:
        sy = lerp(1230, 1095, alba)
        s.append(f"<circle cx='300' cy='{sy:.0f}' r='{lerp(150, 420, alba):.0f}' fill='url(#sol)'/>")
        s.append(f"<circle cx='300' cy='{sy:.0f}' r='70' fill='#fff1b8' stroke='#ffb347' stroke-width='8'/>")
        for k in range(12):
            a = k * 30 + t * 20
            r1, r2 = 95, 95 + 50 * alba + 18 * math.sin(t * 6 + k)
            s.append(f"<line x1='{300 + r1 * math.cos(math.radians(a)):.0f}' y1='{sy + r1 * math.sin(math.radians(a)):.0f}' "
                     f"x2='{300 + r2 * math.cos(math.radians(a)):.0f}' y2='{sy + r2 * math.sin(math.radians(a)):.0f}' "
                     f"stroke='#ffe08a' stroke-width='10' stroke-linecap='round' opacity='{alba:.2f}'/>")
    # nubes suaves
    for i, (cx, cy, sc) in enumerate([(150, 860, 1.3), (760, 760, 1.0), (520, 980, 0.8)]):
        dx = (t * 16 * (1 + 0.4 * i) + i * 380) % 1500 - 300
        col = tri("#ffffff", "#3c3f75", "#ffe2d0")
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})' opacity='0.9'>"
                 f"<path d='M0 50 Q10 0 70 10 Q100 -35 160 0 Q220 -20 240 50 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # montañas
    m1 = tri("#b06a58", "#2c2550", "#c0706a"); m2 = tri("#8a4f4a", "#211c40", "#9a5560")
    s.append(f"<path d='M-20 {HOR + 10} L60 1070 L170 1120 L300 1010 L430 1100 L520 1060 L640 1130 L760 1040 L880 1110 L1000 1050 L1100 1090 L1100 {HOR + 10} Z' "
             f"fill='{m1}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M-20 {HOR + 10} L100 1140 L220 1165 L360 1120 L500 1160 L700 1110 L840 1155 L980 1125 L1100 1150 L1100 {HOR + 10} Z' "
             f"fill='{m2}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # lago seco
    p1 = tri("#ecd3a2", "#5a5478", "#f3d2a8"); p2 = tri("#e2c38c", "#4c4870", "#eac294")
    s.append(f"<rect x='-20' y='{HOR}' width='{W + 40}' height='{H - HOR + 20}' fill='{p1}'/>")
    s.append(f"<path d='M-20 {HOR + 260} Q540 {HOR + 220} 1100 {HOR + 270} L1100 {H + 20} L-20 {H + 20} Z' fill='{p2}' opacity='0.6'/>")
    s.append(f"<line x1='-20' y1='{HOR}' x2='{W + 20}' y2='{HOR}' stroke='{INK}' stroke-width='{LW}'/>")
    cc = tri("#b99566", "#36325a", "#c39a72")
    for kind, pts, w in CRACKS:
        d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts)
        s.append(f"<path d='{d}' fill='none' stroke='{cc}' stroke-width='{w:.1f}' stroke-linecap='round'/>")
    # rocas lejanas con sus surcos
    for bx, by, br, tl in BG_ROCKS:
        k = br / 40
        s.append(f"<path d='M{bx - tl} {by + 6 * k:.0f} Q{bx - tl / 2} {by - 10 * k:.0f} {bx} {by + 6 * k:.0f}' fill='none' stroke='{tri('#a7865a', '#2e2a50', '#b08860')}' stroke-width='{8 * k:.1f}' stroke-linecap='round'/>")
        s.append(f"<ellipse cx='{bx}' cy='{by}' rx='{br}' ry='{br * 0.65:.0f}' fill='{tri('#8e8176', '#4a4466', '#9a8b7e')}' stroke='{INK}' stroke-width='6'/>")
    # surco de la roca protagonista
    xs = np.linspace(-160, x - 110, 50)
    d = "M" + " L".join(f"{xx:.0f} {trail_y(xx) + 44:.0f}" for xx in xs)
    s.append(f"<path d='{d}' fill='none' stroke='{tri('#7d5a36', '#221f40', '#8a6440')}' stroke-width='60' stroke-linecap='round'/>")
    s.append(f"<path d='{d}' fill='none' stroke='{tri('#b48d5a', '#36325c', '#bf9563')}' stroke-width='26' stroke-linecap='round'/>")
    s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='4' stroke-dasharray='30 26' opacity='0.35'/>")
    # capa de hielo entera (noche) y placas rotas (amanecer)
    if hielo > 0 and roto < 1:
        a = hielo * (1 - roto)
        s.append(f"<rect x='-20' y='{HOR + 60}' width='{W + 40}' height='{H}' fill='#bfe9ff' opacity='{0.42 * a:.3f}'/>")
        for k in range(14):
            fx = (k * 173) % 1080; fy = 1300 + (k * 97) % 560
            s.append(f"<path d='M{fx - 40} {fy} L{fx + 40} {fy - 6}' stroke='#ffffff' stroke-width='5' stroke-linecap='round' opacity='{0.7 * a:.2f}'/>")
    if roto > 0:
        push = 160 * seg(t, REVELACION, 10.4)
        for q, sp, rot in PANELS:
            dx = push * sp
            cx = sum(p[0] for p in q) / 4 + dx; cy = sum(p[1] for p in q) / 4
            d = "M" + " L".join(f"{px + dx:.0f} {py:.0f}" for px, py in q) + " Z"
            g_ = f"<g transform='rotate({rot * roto:.2f},{cx:.0f},{cy:.0f})' opacity='{roto:.2f}'>"
            s.append(g_ + f"<path d='{d}' fill='url(#ice)' fill-opacity='0.5' stroke='#ffffff' stroke-width='7' stroke-linejoin='round'/>"
                     f"<path d='{d}' fill='none' stroke='#5bb8e0' stroke-width='3' stroke-linejoin='round'/></g>")
        s.append(rock(t, x))
        # destellos en el hielo
        for k in range(10):
            fx = (k * 211 + 60) % 1080 + push * 0.5; fy = 1360 + (k * 131) % 520
            tw = 0.5 + 0.5 * math.sin(t * 9 + k)
            r_ = 10 + 10 * tw
            s.append(f"<path d='M{fx:.0f} {fy - r_:.0f} L{fx + 4:.0f} {fy - 4:.0f} L{fx + r_:.0f} {fy:.0f} L{fx + 4:.0f} {fy + 4:.0f} "
                     f"L{fx:.0f} {fy + r_:.0f} L{fx - 4:.0f} {fy + 4:.0f} L{fx - r_:.0f} {fy:.0f} L{fx - 4:.0f} {fy - 4:.0f} Z' fill='#ffffff' opacity='{roto * (0.4 + 0.6 * tw):.2f}'/>")
        # viento
        for k in range(7):
            wy = 1320 + k * 85
            wx = ((t - REVELACION) * 900 + k * 260) % 1500 - 300
            s.append(f"<path d='M{wx:.0f} {wy} q60 -26 120 0 t120 0' fill='none' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='{0.8 * roto:.2f}'/>")
    else:
        s.append(rock(t, x))
    # polvo flotando de día
    for k in range(16):
        px = (k * 137 + t * 30) % 1100; py = 1250 + (k * 89) % 600 + 10 * math.sin(t * 2 + k)
        s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{3 + k % 3}' fill='#fff2d0' opacity='{0.5 * (1 - noche) + 0.3 * alba:.2f}'/>")
    s.append("</g>")
    if flash > 0.02:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.75 * flash:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
