"""2026-11-09-c3 · Récord: el lago de Maracaibo (Venezuela) es el lugar de la Tierra con más rayos,
unos 233 rayos por km² al año según los datos del satélite TRMM de la NASA (relámpago del Catatumbo).

0-2,5 s  noche sobre el lago: una nube de tormenta original con cara entra desde la derecha y se
         coloca sobre el agua; palafitos con luz y una lancha con farol se mecen.
2,5-5 s  empiezan los rayos, uno de vez en cuando; se reflejan en el agua.
5-7,5 s  la nube se carga: chispas, brillo por dentro, rayos cada vez más seguidos.
7,5-10 s REVELACION: muchos rayos a la vez sin parar, destello morado en todo el cielo y el lago,
         la nube sonríe y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 2

rng = np.random.default_rng(41)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1150), rng.uniform(2, 5), rng.uniform(0, 6.28)) for _ in range(80)]
DROPS = [(rng.uniform(-300, 300), rng.uniform(0, 1), rng.uniform(0.6, 1.0)) for _ in range(34)]
RIPPLES = [(rng.uniform(0, W), rng.uniform(1340, 1900), rng.uniform(40, 120), rng.uniform(0, 6.28)) for _ in range(26)]
LAGO = 1330   # horizonte del lago

# círculos que forman la nube (relativos a su centro)
BUMPS = [(-250, 30, 95), (-150, -40, 120), (-20, -95, 140), (120, -55, 125), (240, 10, 100),
         (-90, 40, 110), (90, 40, 110), (0, 30, 120)]


def zigzag(seed, x0, y0, y1):
    r = np.random.default_rng(seed)
    pts = [(x0, y0)]; x = x0; y = y0
    n = 7
    for i in range(1, n + 1):
        y = lerp(y0, y1, i / n)
        x = x + r.uniform(-55, 55)
        pts.append((x, y))
    # ramita
    k = r.integers(2, 5)
    bx, by = pts[k]
    rama = [(bx, by), (bx + r.choice([-1, 1]) * r.uniform(50, 90), by + r.uniform(50, 90)),
            (bx + r.choice([-1, 1]) * r.uniform(70, 130), by + r.uniform(110, 160))]
    return pts, rama


# rayos: (instante, semilla, x de salida, y final)
BOLTS = []
for i, tt in enumerate([1.3, 2.7, 3.6, 4.4, 5.1, 5.6, 6.05, 6.45, 6.8, 7.1, 7.3]):
    BOLTS.append((tt, 100 + i, [380, 620, 470, 700, 420, 560, 660, 450, 600, 500, 400][i],
                  [1560, 1610, 1520, 1640, 1580, 1540, 1620, 1600, 1560, 1650, 1590][i]))
for j in range(30):
    tt = REVELACION + j * 0.085 - (0.0 if j > 2 else 0.0)
    BOLTS.append((tt, 300 + j, 250 + (j * 137) % 580, 1520 + (j * 53) % 180))
PATHS = {s: zigzag(s, x, 1290, y1) for _, s, x, y1 in BOLTS}


def flash_level(t):
    f = 0.0
    for tt, *_ in BOLTS:
        d = t - tt
        if 0 <= d < 0.25: f = max(f, 1 - d / 0.25)
    if t >= REVELACION: f = max(f, 0.45 + 0.25 * math.sin(t * 31))
    return f


def bolt_svg(pts, rama, a):
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    dr = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in rama)
    s = []
    for path, w in ((d, 1.0), (dr, 0.6)):
        s.append(f"<path d='{path}' fill='none' stroke='#c9a6ff' stroke-width='{64*w:.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{0.35*a:.2f}'/>")
        s.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='{32*w:.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{a:.2f}'/>")
        s.append(f"<path d='{path}' fill='none' stroke='#fff27a' stroke-width='{19*w:.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{a:.2f}'/>")
        s.append(f"<path d='{path}' fill='none' stroke='#ffffff' stroke-width='{8*w:.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{a:.2f}'/>")
    return "".join(s)


def nube(t, cx, cy, carga, rev, fl):
    sc = 1 + 0.03 * math.sin(t * 2.4) + 0.03 * rev
    g = [f"<g transform='translate({cx:.1f},{cy:.1f}) scale({sc:.4f})'>"]
    body = mix("#5a5f93", "#7a6bc4", max(carga * 0.4, rev))
    top = mix("#7b81b8", "#a596ec", max(carga * 0.4, rev))
    # contorno: círculos gruesos debajo, relleno encima
    for x, y, r in BUMPS:
        g.append(f"<circle cx='{x}' cy='{y}' r='{r + LW / 2}' fill='{INK}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-300' y='20' width='600' height='120' rx='60' fill='{INK}' stroke='{INK}' stroke-width='{LW * 2}'/>")
    for x, y, r in BUMPS:
        g.append(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{body}'/>")
    g.append(f"<rect x='-300' y='20' width='600' height='120' rx='60' fill='{body}'/>")
    # luces de la parte de arriba
    for x, y, r in BUMPS[:5]:
        g.append(f"<circle cx='{x - r * 0.18:.0f}' cy='{y - r * 0.25:.0f}' r='{r * 0.62:.0f}' fill='{top}'/>")
    # brillo interior (carga)
    glow = clamp(carga * (0.5 + 0.5 * math.sin(t * 19)) + fl * 0.8 + rev * 0.4)
    if glow > 0.02:
        g.append(f"<ellipse cx='{-40 + 40 * math.sin(t * 5):.0f}' cy='-30' rx='220' ry='110' fill='url(#nglow)' opacity='{glow:.2f}'/>")
    # cara
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    eye_r = 40 + 8 * rev
    look = 10 * math.sin(t * 1.3) * (1 - rev)
    for ex in (-95, 95):
        g.append(f"<ellipse cx='{ex}' cy='20' rx='{eye_r:.0f}' ry='{eye_r * blink:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='7'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look:.1f}' cy='{24 - 6 * rev:.1f}' r='{19 + 3 * rev:.0f}' fill='{INK}'/>")
            g.append(f"<circle cx='{ex + look - 7:.1f}' cy='{15 - 6 * rev:.1f}' r='7' fill='#fff'/>")
    # cejas traviesas
    lift = 10 * carga + 8 * rev
    g.append(f"<path d='M-140 {-38 - lift:.0f} Q-95 {-58 - lift:.0f} -55 {-40 - lift:.0f}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<path d='M55 {-40 - lift:.0f} Q95 {-58 - lift:.0f} 140 {-38 - lift:.0f}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    # mofletes
    for ex in (-160, 160):
        g.append(f"<ellipse cx='{ex}' cy='70' rx='30' ry='17' fill='#ff8fb1' opacity='0.75'/>")
    # boca: sonrisa que se abre en la revelación
    op = 10 + 40 * rev + 8 * carga
    g.append(f"<path d='M-55 78 Q0 {98 + op:.0f} 55 78 Q0 {92:.0f} -55 78 Z' fill='#5a1f3a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    if rev > 0.2:
        g.append(f"<path d='M-26 {88 + op * 0.55:.0f} Q0 {78 + op:.0f} 26 {88 + op * 0.55:.0f}' fill='#ff6f8a' opacity='{rev:.2f}'/>")
    # chispitas alrededor cuando se carga
    sp = max(carga, rev)
    if sp > 0.05:
        for k in range(6):
            a = t * 3 + k * 1.047
            rx, ry = 330 * math.cos(a), 160 * math.sin(a) - 20
            on = (math.sin(t * 23 + k * 2) > 0.1)
            if on:
                g.append(f"<path d='M{rx:.0f} {ry - 22:.0f} L{rx + 8:.0f} {ry - 4:.0f} L{rx + 22:.0f} {ry:.0f} L{rx + 8:.0f} {ry + 4:.0f} "
                         f"L{rx:.0f} {ry + 22:.0f} L{rx - 8:.0f} {ry + 4:.0f} L{rx - 22:.0f} {ry:.0f} L{rx - 8:.0f} {ry - 4:.0f} Z' "
                         f"fill='#fff27a' stroke='{INK}' stroke-width='4' opacity='{sp:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def palafito(x, y, s, t, k):
    g = [f"<g transform='translate({x},{y}) scale({s})'>"]
    for px in (-80, -30, 30, 80):
        g.append(f"<rect x='{px - 7}' y='40' width='14' height='120' fill='#6b4a32' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-110' y='30' width='220' height='18' fill='#8a6242' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-95' y='-70' width='190' height='100' fill='#d98c4e' stroke='{INK}' stroke-width='{LW}'/>")
    for px in range(-80, 95, 26):
        g.append(f"<line x1='{px}' y1='-66' x2='{px}' y2='26' stroke='#b46c38' stroke-width='5'/>")
    g.append(f"<path d='M-125 -66 L0 -145 L125 -66 Z' fill='#c9b26a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(-3, 4):
        g.append(f"<line x1='{i * 30}' y1='-130' x2='{i * 38}' y2='-70' stroke='#a8904c' stroke-width='5'/>")
    lit = 0.8 + 0.2 * math.sin(t * 7 + k)
    g.append(f"<rect x='-55' y='-45' width='46' height='46' rx='6' fill='{mix('#7a4a20', '#ffd36b', lit)}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='22' y='-48' width='42' height='78' rx='6' fill='#7a4a2a' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def lancha(t, x, y):
    bob = 7 * math.sin(t * 2.2); rot = 4 * math.sin(t * 1.7)
    g = [f"<g transform='translate({x},{y + bob:.1f}) rotate({rot:.1f})'>"]
    g.append(f"<path d='M-140 -20 L140 -20 Q120 40 60 45 L-90 45 Q-130 35 -140 -20 Z' fill='#e85d4a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-135' y='-28' width='275' height='16' rx='6' fill='#f5e6c8' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<line x1='60' y1='-28' x2='60' y2='-130' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    fl = 0.75 + 0.25 * math.sin(t * 9)
    g.append(f"<circle cx='60' cy='-140' r='{46 * fl:.0f}' fill='#ffd36b' opacity='0.25'/>")
    g.append(f"<rect x='44' y='-158' width='32' height='36' rx='8' fill='#ffe59a' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    carga = seg(t, 4.8, 7.3)
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.4)
    fl = flash_level(t)
    lum = clamp(0.55 * fl + 0.35 * rev)
    sky_top = mix(mix("#0e0d2e", "#2a1f5e", lum), "#3a2a7a", rev * 0.5)
    sky_mid = mix("#26205a", "#6a4fb0", lum)
    sky_low = mix("#3d2f6e", "#a07ce0", lum)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{sky_top}'/>"
            f"<stop offset='0.6' stop-color='{sky_mid}'/><stop offset='1' stop-color='{sky_low}'/></linearGradient>"
            f"<linearGradient id='agua' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#1f3f63', '#5c64b8', lum)}'/>"
            f"<stop offset='1' stop-color='{mix('#0f2340', '#2c2f6e', lum)}'/></linearGradient>"
            "<radialGradient id='nglow'><stop offset='0' stop-color='#fff6a8' stop-opacity='0.95'/>"
            "<stop offset='0.5' stop-color='#d7b8ff' stop-opacity='0.5'/><stop offset='1' stop-color='#d7b8ff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='refl'><stop offset='0' stop-color='#fff3b0' stop-opacity='0.55'/>"
            "<stop offset='0.5' stop-color='#c7a2ff' stop-opacity='0.3'/><stop offset='1' stop-color='#9a6cff' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='halo'><stop offset='0' stop-color='#f3e6ff' stop-opacity='0.9'/>"
            "<stop offset='0.4' stop-color='#b48cff' stop-opacity='0.45'/><stop offset='1' stop-color='#7a4fe0' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # estrellas (se apagan con los destellos)
    for sx, sy, sr, ph in STARS:
        a = (0.5 + 0.5 * math.sin(t * 2.5 + ph)) * (1 - lum)
        if a > 0.05: s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # luna tranquila arriba a la derecha
    s.append(f"<circle cx='880' cy='330' r='70' fill='#fff4cf' stroke='{INK}' stroke-width='7' opacity='{1 - 0.5 * rev:.2f}'/>")
    s.append(f"<circle cx='905' cy='310' r='62' fill='{sky_top}' opacity='{1 - 0.5 * rev:.2f}'/>")

    w = []   # todo lo que se acerca con el zoom
    # halo gigante en la revelación
    if rev > 0:
        w.append(f"<circle cx='540' cy='1300' r='{lerp(300, 900, rev):.0f}' fill='url(#halo)' opacity='{rev * (0.75 + 0.25 * math.sin(t * 17)):.2f}'/>")
    # montañas lejanas (sierra)
    m1 = mix("#2a2350", "#5a45a0", lum); m2 = mix("#1f1b42", "#4a3a8a", lum)
    w.append(f"<path d='M0 {LAGO} L0 1210 Q90 1150 170 1200 Q260 1110 360 1185 L460 1230 L1080 1230 L1080 {LAGO} Z' fill='{m1}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    w.append(f"<path d='M520 {LAGO} L620 1240 Q720 1170 820 1225 Q930 1150 1080 1210 L1080 {LAGO} Z' fill='{m2}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # lago
    w.append(f"<rect x='-20' y='{LAGO}' width='{W + 40}' height='{H - LAGO + 20}' fill='url(#agua)' stroke='{INK}' stroke-width='{LW}'/>")
    cx_r = lerp(980, 540, ease(clamp(t / 2.2)))
    # reflejo de los rayos en el agua
    if fl > 0.02 or rev > 0:
        w.append(f"<ellipse cx='{cx_r:.0f}' cy='1600' rx='{460 + 80 * rev:.0f}' ry='230' fill='url(#refl)' opacity='{max(fl, rev * 0.7):.2f}'/>")
    for rx, ry, rl, ph in RIPPLES:
        dx = 30 * math.sin(t * 0.9 + ph)
        a = 0.35 + 0.25 * math.sin(t * 2 + ph)
        w.append(f"<line x1='{rx + dx - rl / 2:.0f}' y1='{ry:.0f}' x2='{rx + dx + rl / 2:.0f}' y2='{ry:.0f}' stroke='{mix('#6f9ccc', '#ffffff', lum)}' stroke-width='6' stroke-linecap='round' opacity='{a:.2f}'/>")
    # nube: entra desde la derecha
    cx = lerp(980, 540, ease(clamp(t / 2.2))) + 12 * math.sin(t * 1.1)
    cy = 1150 + 10 * math.sin(t * 1.6)
    # lluvia bajo la nube
    for dx, ph, sp in DROPS:
        yy = 1290 + ((t * 1.3 * sp + ph) % 1) * 300
        w.append(f"<line x1='{cx + dx:.0f}' y1='{yy:.0f}' x2='{cx + dx - 8:.0f}' y2='{yy + 34:.0f}' stroke='#a9c4ff' stroke-width='5' stroke-linecap='round' opacity='0.55'/>")
    # rayos
    for tt, sd, x0, y1 in BOLTS:
        d = t - tt
        if 0 <= d < 0.22:
            a = 1 if d < 0.12 else 1 - (d - 0.12) / 0.10
            pts, rama = PATHS[sd]
            off = cx - 540
            pts = [(x + off, y) for x, y in pts]; rama = [(x + off, y) for x, y in rama]
            w.append(bolt_svg(pts, rama, a))
            ex, ey = pts[-1]
            w.append(f"<ellipse cx='{ex:.0f}' cy='{ey:.0f}' rx='70' ry='16' fill='#fff6b0' opacity='{0.7 * a:.2f}'/>")
    w.append(nube(t, cx, cy, carga, rev, fl))
    # palafitos y lancha en primer plano
    w.append(palafito(170, 1600, 1.0, t, 0))
    w.append(palafito(-10, 1720, 0.8, t, 2))
    w.append(lancha(t, 840, 1780))
    z = 1 + 0.10 * seg(t, REVELACION, DUR)
    s.append(zoom(540, 1450, z, "".join(w)))
    # destello general
    if fl > 0.02:
        s.append(f"<rect width='{W}' height='{H}' fill='#e6d4ff' opacity='{0.16 * fl:.2f}'/>")
    from lib import svg
    return svg("".join(s), defs)
