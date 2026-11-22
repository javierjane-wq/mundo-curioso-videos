"""2026-11-22-c3 · Piel de gallina: con frío, un músculo diminuto en cada pelo se contrae y lo pone de pie.

Escena: un niño original en manga corta llega a un paisaje nevado. Una lupa muestra su piel por dentro:
los pelitos están tumbados y cada uno tiene un musculito. Sopla viento helado, el cielo se oscurece y el
niño tirita. REVELACION: los músculos se contraen, los pelos se ponen DE PIE y salen bultitos
(piel de gallina), destello frío y zoom de cámara hacia la lupa.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.3    # los pelos se ponen de pie: golpe musical
MUSICA = 2

rng = np.random.default_rng(22)
SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 10), rng.uniform(40, 90), rng.uniform(0, 6.28)) for _ in range(85)]
WIND = [(rng.uniform(1050, 1750), rng.uniform(0, 1.0), rng.uniform(160, 300)) for _ in range(9)]
TREES = [(90, 1235, 1.0), (205, 1215, 0.8), (690, 1225, 0.9), (960, 1210, 1.1), (1040, 1250, 0.7)]
LENS_X, LENS_Y, LENS_R = 800, 1300, 212
SURF = 1335                          # superficie de la piel dentro de la lupa
HAIRS = [650, 735, 820, 905, 985]   # raíces de los pelos dentro de la lupa

SKIN = "#f7c29b"
SKIN_D = "#e7a27a"


def frio(t):
    return seg(t, 4.9, 6.6)


def pie(t):
    """0 = pelos tumbados, 1 = de pie (revelación, termina antes de 8,2 s)."""
    return seg(t, REVELACION, REVELACION + 0.45)


def tree(x, y, s, t, cold):
    sw = (2 + 7 * cold) * math.sin(t * (2.2 + 3 * cold) + x)
    g = [f"<g transform='translate({x},{y}) scale({s}) rotate({sw:.1f})'>",
         f"<rect x='-12' y='-10' width='24' height='40' fill='#7a4a2a' stroke='{INK}' stroke-width='6'/>"]
    for i, (w, h, yy) in enumerate(((90, 80, -20), (72, 70, -70), (52, 62, -115))):
        g.append(f"<path d='M{-w} {yy} L0 {yy - h} L{w} {yy} Z' fill='{mix('#2f9e6b', '#2a7a62', cold)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        g.append(f"<path d='M{-w * 0.45:.0f} {yy - h * 0.55:.0f} L0 {yy - h} L{w * 0.45:.0f} {yy - h * 0.55:.0f} Q0 {yy - h * 0.4:.0f} {-w * 0.45:.0f} {yy - h * 0.55:.0f} Z' fill='#ffffff'/>")
    g.append("</g>")
    return "".join(g)


def kid(t):
    """Niño original: cabeza redonda, flequillo castaño, camiseta naranja de manga corta, pantalón azul."""
    x = lerp(10, 300, seg(t, 0, 2.1))
    walking = t < 2.15
    cold = frio(t)
    bob = -10 * abs(math.sin(t * 9)) if walking else 0
    shiver = 5 * math.sin(t * 70) * cold
    x += shiver
    y0 = bob
    step = math.sin(t * 9) if walking else 0
    blink = 0.12 if ((t + 1.3) % 2.7) < 0.12 else 1.0
    g = [f"<g transform='translate({x:.1f},{y0:.1f})'>"]
    g.append("<ellipse cx='0' cy='1768' rx='150' ry='22' fill='#6b8fb3' opacity='0.35'/>")
    # piernas
    for lx, ph in ((-40, 1), (40, -1)):
        dx = 18 * step * ph
        g.append(f"<path d='M{lx} 1585 L{lx + dx:.0f} 1730' stroke='{INK}' stroke-width='52' stroke-linecap='round'/>"
                 f"<path d='M{lx} 1585 L{lx + dx:.0f} 1730' stroke='{SKIN}' stroke-width='36' stroke-linecap='round'/>")
        g.append(f"<ellipse cx='{lx + dx + 12:.0f}' cy='1745' rx='46' ry='26' fill='#c0392b' stroke='{INK}' stroke-width='{LW}'/>")
    # pantalón corto
    g.append(f"<path d='M-92 1500 L92 1500 L98 1600 L8 1600 L0 1565 L-8 1600 L-98 1600 Z' fill='#3d6fd8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brazo izquierdo (colgando, se balancea al andar; con frío se pega al cuerpo)
    sw = 20 * step - 10 * cold
    g.append(f"<g transform='translate(-92,1345) rotate({sw:.1f})'>"
             f"<path d='M0 0 L-28 150' stroke='{INK}' stroke-width='56' stroke-linecap='round'/>"
             f"<path d='M0 0 L-28 150' stroke='{SKIN}' stroke-width='40' stroke-linecap='round'/>"
             f"<circle cx='-30' cy='162' r='26' fill='{SKIN}' stroke='{INK}' stroke-width='7'/></g>")
    # cuerpo (camiseta)
    g.append(f"<path d='M-95 1335 Q0 1305 95 1335 L100 1510 Q0 1525 -100 1510 Z' fill='#ff7a3d' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-95 1430 L100 1430' stroke='#ffd23f' stroke-width='16'/>")
    # mangas cortas
    g.append(f"<path d='M-95 1335 L-140 1395 L-100 1420 Z' fill='#ff7a3d' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>")
    # brazo derecho extendido hacia la lupa
    ax0, ay0, ax1, ay1 = 92, 1352, 245, 1412
    g.append(f"<path d='M{ax0} {ay0} L{ax1} {ay1}' stroke='{INK}' stroke-width='58' stroke-linecap='round'/>"
             f"<path d='M{ax0} {ay0} L{ax1} {ay1}' stroke='{SKIN}' stroke-width='42' stroke-linecap='round'/>")
    g.append(f"<circle cx='{ax1 + 20}' cy='{ay1 + 8}' r='28' fill='{SKIN}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M95 1330 L150 1340 L118 1395 L95 1385 Z' fill='#ff7a3d' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>")
    # pelitos del antebrazo (se levantan en la revelación)
    p = pie(t)
    for i in range(6):
        k = 0.25 + i * 0.12
        hx, hy = lerp(ax0, ax1, k), lerp(ay0, ay1, k) - 18
        a = math.radians(lerp(-8, -78, p))
        g.append(f"<line x1='{hx:.1f}' y1='{hy:.1f}' x2='{hx + 14 * math.cos(a):.1f}' y2='{hy + 14 * math.sin(a):.1f}' stroke='#6b4428' stroke-width='3' stroke-linecap='round'/>")
        if p > 0.05:
            g.append(f"<circle cx='{hx:.1f}' cy='{hy + 6:.1f}' r='{4 * p:.1f}' fill='{SKIN_D}'/>")
    # cuello y cabeza
    g.append(f"<rect x='-22' y='1300' width='44' height='30' fill='{SKIN}' stroke='{INK}' stroke-width='7'/>")
    hy = 1205
    g.append(f"<circle cx='0' cy='{hy}' r='108' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    for ex in (-108, 108):
        g.append(f"<ellipse cx='{ex}' cy='{hy + 10}' rx='20' ry='28' fill='{SKIN}' stroke='{INK}' stroke-width='7'/>")
    # pelo castaño
    g.append(f"<path d='M-104 {hy - 20} Q-110 {hy - 120} 0 {hy - 118} Q110 {hy - 120} 104 {hy - 20} "
             f"Q80 {hy - 70} 40 {hy - 62} Q30 {hy - 90} 0 {hy - 70} Q-30 {hy - 92} -50 {hy - 60} Q-85 {hy - 70} -104 {hy - 20} Z' "
             f"fill='#7a4a24' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # ojos grandes que parpadean (miran a la lupa)
    look = 8 * seg(t, 2.4, 3.0)
    for ex in (-40, 40):
        g.append(f"<g transform='translate({ex},{hy + 5}) scale(1,{blink})'>"
                 f"<ellipse rx='26' ry='32' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='{4 + look:.1f}' cy='4' r='15' fill='#2a1a14'/><circle cx='{look - 2:.1f}' cy='-4' r='6' fill='#fff'/></g>")
    # mofletes: rosas -> azulados con frío; nariz roja
    ch = mix("#ff8c8c", "#9cc8f0", cold)
    for cx in (-66, 66):
        g.append(f"<ellipse cx='{cx}' cy='{hy + 52}' rx='20' ry='12' fill='{ch}' opacity='0.85'/>")
    g.append(f"<circle cx='4' cy='{hy + 42}' r='13' fill='{mix('#f0a07c', '#ff5a5f', cold)}' stroke='{INK}' stroke-width='5'/>")
    # boca: sonrisa -> dientes castañeteando
    if cold < 0.5:
        g.append(f"<path d='M-30 {hy + 70} Q0 {hy + 98} 30 {hy + 70}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        o = 4 * abs(math.sin(t * 40))
        g.append(f"<rect x='-30' y='{hy + 66 - o:.1f}' width='60' height='{24 + 2 * o:.1f}' rx='10' fill='#7a2a2a' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='-24' y='{hy + 70 - o:.1f}' width='48' height='16' rx='4' fill='#fff'/>"
                 f"<line x1='-8' y1='{hy + 70 - o:.1f}' x2='-8' y2='{hy + 86 - o:.1f}' stroke='{INK}' stroke-width='3'/>"
                 f"<line x1='8' y1='{hy + 70 - o:.1f}' x2='8' y2='{hy + 86 - o:.1f}' stroke='{INK}' stroke-width='3'/>")
    # vaho al respirar con frío
    if cold > 0.1:
        for i in range(3):
            ph = (t * 0.9 + i / 3) % 1
            g.append(f"<circle cx='{-40 - 120 * ph:.0f}' cy='{hy + 80 - 40 * ph:.0f}' r='{12 + 26 * ph:.0f}' fill='#ffffff' opacity='{0.75 * cold * (1 - ph):.2f}'/>")
    g.append("</g>")
    return "".join(g), x


def lens(t, kx):
    """Lupa con el corte de la piel: pelo, folículo y musculito (músculo erector del pelo)."""
    s = rebote(t, 2.2, 0.55)
    if s <= 0:
        return ""
    p = pie(t)
    cold = frio(t)
    cx, cy, r = LENS_X, LENS_Y, LENS_R
    g = [f"<g transform='translate({cx},{cy}) scale({s:.3f}) translate({-cx},{-cy})'>"]
    # haz de luz del brazo a la lupa
    axp, ayp = kx + 190, 1385
    g.append(f"<path d='M{axp:.0f} {ayp} L{cx - r * 0.55:.0f} {cy - r * 0.83:.0f} L{cx - r * 0.55:.0f} {cy + r * 0.83:.0f} Z' fill='#ffffff' opacity='0.35'/>")
    g.append(f"<clipPath id='lc'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath>")
    g.append("<g clip-path='url(#lc)'>")
    g.append(f"<rect x='{cx - r}' y='{cy - r}' width='{2 * r}' height='{2 * r}' fill='{mix('#d6efff', '#a9c7e4', cold)}'/>")
    # copitos dentro de la lupa
    for i in range(6):
        fx = cx - r + ((i * 83 + t * 40 * (1 + 2 * cold)) % (2 * r))
        fy = cy - r + ((i * 57 + t * 70) % (r * 0.9))
        g.append(f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='6' fill='#fff' opacity='0.9'/>")
    # superficie con bultitos
    bump = 30 * p
    xs = np.arange(cx - r - 10, cx + r + 12, 8)
    ys = [SURF - sum(bump * math.exp(-((x - hx) / 32) ** 2) for hx in HAIRS) + 3 * math.sin(x / 40 + t) for x in xs]
    pts = " ".join(f"{x:.0f},{y:.1f}" for x, y in zip(xs, ys))
    g.append(f"<polygon points='{pts} {xs[-1]:.0f},{cy + r + 10} {xs[0]:.0f},{cy + r + 10}' fill='{SKIN}'/>")
    g.append(f"<polygon points='{' '.join(f'{x:.0f},{y + 42:.1f}' for x, y in zip(xs, ys))} {xs[-1]:.0f},{cy + r + 10} {xs[0]:.0f},{cy + r + 10}' fill='#f9d3b6'/>")
    g.append(f"<polyline points='{' '.join(f'{x:.0f},{y + 42:.1f}' for x, y in zip(xs, ys))}' fill='none' stroke='{SKIN_D}' stroke-width='5'/>")
    g.append(f"<polyline points='{pts}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # pelos, folículos y músculos
    for i, hx in enumerate(HAIRS):
        root_y = SURF - bump + 3 * math.sin(hx / 40 + t)
        wob = 3 * math.sin(t * 2.5 + i) * (1 - p) + 2 * math.sin(t * 6 + i) * p
        a = math.radians(lerp(-40, -84, p) + wob)
        dx, dy = math.cos(a), math.sin(a)
        fx, fy = -dx, -dy                                   # el folículo continúa hacia dentro
        bx, by = hx + 78 * fx, root_y + 78 * fy             # bulbo del folículo
        # músculo erector: del lateral del folículo a la piel de arriba; se acorta y engorda al contraerse
        mx0, my0 = hx + 52 * fx, root_y + 52 * fy
        mx1, my1 = hx + 62, root_y + 30
        mw = lerp(13, 22, p)
        g.append(f"<path d='M{mx0:.1f} {my0:.1f} Q{(mx0 + mx1) / 2:.1f} {max(my0, my1) + lerp(18, 4, p):.1f} {mx1:.1f} {my1:.1f}' fill='none' stroke='{INK}' stroke-width='{mw + 8:.1f}' stroke-linecap='round'/>")
        g.append(f"<path d='M{mx0:.1f} {my0:.1f} Q{(mx0 + mx1) / 2:.1f} {max(my0, my1) + lerp(18, 4, p):.1f} {mx1:.1f} {my1:.1f}' fill='none' stroke='{mix('#e8707a', '#ff3b4f', p)}' stroke-width='{mw:.1f}' stroke-linecap='round'/>")
        # folículo (vaina) y bulbo
        g.append(f"<line x1='{hx:.1f}' y1='{root_y:.1f}' x2='{bx:.1f}' y2='{by:.1f}' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>"
                 f"<line x1='{hx:.1f}' y1='{root_y:.1f}' x2='{bx:.1f}' y2='{by:.1f}' stroke='#f0b090' stroke-width='14' stroke-linecap='round'/>")
        g.append(f"<circle cx='{bx:.1f}' cy='{by:.1f}' r='14' fill='#c77d55' stroke='{INK}' stroke-width='6'/>")
        # pelo
        L = 135
        tx, ty = hx + L * dx, root_y + L * dy
        qx, qy = hx + L * 0.55 * dx + 10 * dy, root_y + L * 0.55 * dy - 10 * dx
        g.append(f"<path d='M{bx:.1f} {by:.1f} L{hx:.1f} {root_y:.1f} Q{qx:.1f} {qy:.1f} {tx:.1f} {ty:.1f}' fill='none' stroke='#4a2c18' stroke-width='9' stroke-linecap='round'/>")
    # destello frío en la revelación
    fl = seg(t, REVELACION - 0.05, REVELACION + 0.15) * (1 - seg(t, REVELACION + 0.15, 7.75))
    if fl > 0.01:
        g.append(f"<rect x='{cx - r}' y='{cy - r}' width='{2 * r}' height='{2 * r}' fill='#ffffff' opacity='{0.6 * fl:.2f}'/>")
    g.append("</g>")
    # aro de la lupa y mango
    hx0, hy0 = cx + r * 0.72, cy + r * 0.72
    g.append(f"<path d='M{hx0:.0f} {hy0:.0f} L{hx0 + 95:.0f} {hy0 + 95:.0f}' stroke='{INK}' stroke-width='56' stroke-linecap='round'/>"
             f"<path d='M{hx0 + 10:.0f} {hy0 + 10:.0f} L{hx0 + 92:.0f} {hy0 + 92:.0f}' stroke='#8a4fd8' stroke-width='38' stroke-linecap='round'/>")
    ring = mix("#ffd23f", "#bfe8ff", seg(t, REVELACION, REVELACION + 0.4))
    g.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{INK}' stroke-width='34'/>"
             f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{ring}' stroke-width='18'/>")
    g.append(f"<path d='M{cx - r * 0.62:.0f} {cy - r * 0.45:.0f} A{r * 0.78:.0f} {r * 0.78:.0f} 0 0 1 {cx - r * 0.2:.0f} {cy - r * 0.75:.0f}' fill='none' stroke='#ffffff' stroke-width='12' stroke-linecap='round' opacity='0.7'/>")
    # chispas de escarcha que salen en la revelación
    sp = seg(t, REVELACION, REVELACION + 0.8)
    if sp > 0:
        for i in range(12):
            ang = i * math.tau / 12 + 0.2
            rr = r + 20 + 120 * sp
            px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
            sz = 16 * (1 - 0.5 * sp) * (0.8 + 0.3 * math.sin(t * 8 + i))
            g.append(f"<path d='M{px:.0f} {py - sz:.0f} L{px + sz * 0.3:.0f} {py:.0f} L{px:.0f} {py + sz:.0f} L{px - sz * 0.3:.0f} {py:.0f} Z' "
                     f"fill='#ffffff' stroke='#7fc4ff' stroke-width='3' opacity='{1 - 0.4 * sp:.2f}' transform='rotate({math.degrees(ang) + 90:.0f} {px:.0f} {py:.0f})'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    cold = frio(t)
    top = mix("#8fd0ff", "#6f8fb5", cold)
    mid = mix("#c4e8ff", "#a3bdd6", cold)
    low = mix("#eef9ff", "#d5e2ee", cold)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<radialGradient id='sun'><stop offset='0' stop-color='#fff6c8' stop-opacity='0.9'/><stop offset='1' stop-color='#fff6c8' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION - 0.1, 8.1)
    body = []
    # sol pálido que se tapa con el frío
    sa = 1 - 0.8 * cold
    body.append(f"<circle cx='880' cy='880' r='170' fill='url(#sun)' opacity='{sa:.2f}'/>")
    body.append(f"<circle cx='880' cy='880' r='62' fill='#fff3b0' stroke='#ffcf5a' stroke-width='8' opacity='{sa:.2f}'/>")
    # nubes que llegan con el frío
    for i, (cx0, cy0, sc) in enumerate(((180, 760, 1.4), (760, 640, 1.1), (520, 930, 1.6))):
        dx = (t * 12 * (1 + i * 0.4)) + lerp(-500 if i != 1 else 520, 0, seg(t, 4.6, 6.4)) * (1 if i != 1 else 1)
        col = mix("#ffffff", "#c9d6e4", cold)
        body.append(f"<g transform='translate({cx0 + dx:.0f},{cy0}) scale({sc})' opacity='{0.25 + 0.7 * cold:.2f}'>"
                    f"<path d='M0 40 Q15 -15 75 0 Q110 -45 170 -5 Q235 -20 255 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # colinas nevadas y árboles
    body.append(f"<path d='M0 1260 Q180 1150 400 1230 T820 1200 T1080 1220 L1080 1920 L0 1920 Z' fill='{mix('#eaf6ff', '#d6e4f0', cold)}' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, sc in TREES:
        body.append(tree(x, y, sc, t, cold))
    body.append(f"<path d='M0 1560 Q300 1500 600 1550 T1080 1530 L1080 1920 L0 1920 Z' fill='{mix('#ffffff', '#e6eef6', cold)}' stroke='{INK}' stroke-width='{LW}'/>")
    for bx, by, br in ((140, 1700, 50), (880, 1820, 70), (560, 1880, 40)):
        body.append(f"<ellipse cx='{bx}' cy='{by}' rx='{br}' ry='{br * 0.45:.0f}' fill='#ffffff' stroke='{INK}' stroke-width='6'/>")
    # huellas en la nieve
    tr = seg(t, 0, 2.1)
    for i in range(7):
        fx = -120 + i * 70
        if fx < lerp(10, 300, tr) - 40:
            body.append(f"<ellipse cx='{fx}' cy='{1775 + (i % 2) * 22}' rx='22' ry='9' fill='#b9cfe3'/>")
    # ráfagas de viento helado
    if cold > 0.02:
        for wy, ph, ln in WIND:
            prog = ((t * 0.9 + ph) % 1)
            wx = lerp(-400, 1300, prog)
            body.append(f"<path d='M{wx:.0f} {wy:.0f} q{ln * 0.5:.0f} -30 {ln:.0f} 0 q30 20 10 40' fill='none' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='{0.8 * cold:.2f}'/>")
    k, kx = kid(t)
    body.append(k)
    body.append(lens(t, kx))
    # copos de nieve (más rápidos e inclinados con el viento)
    for sx, sy, sr, sp, ph in SNOW:
        yy = (sy + t * sp * (1 + 1.5 * cold)) % (H + 40) - 20
        xx = (sx + 25 * math.sin(t * 1.3 + ph) + t * 180 * cold * cold) % (W + 40) - 20
        op = 0.55 if yy < 1000 else 0.9
        body.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{sr:.1f}' fill='#ffffff' opacity='{op}'/>")
    s.append(zoom(LENS_X - 80, LENS_Y, z, "".join(body)))
    s.append("</svg>")
    return "".join(s)
