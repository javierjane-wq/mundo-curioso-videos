"""2026-11-23-c2 · Un rayo SÍ cae dos veces en el mismo sitio: el Empire State recibe unos 23 al año.

Rascacielos art déco original con cara (ojos en el tramo central) en una noche de tormenta.
Entra subiendo desde abajo, llueve, las nubes se mueven y le caen rayos cada vez más seguidos
en la aguja. En la REVELACION, un rayo gigante: destello, el edificio se ilumina entero,
halo eléctrico en la aguja y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.0    # rayo gigante: golpe musical
MUSICA = 7

TIP_X, TIP_Y = 540, 1085          # punta de la aguja (con el edificio ya subido)
GOLPES = [2.6, 4.0, 5.1, 5.85, 6.45]   # rayos pequeños; el grande es REVELACION

rng = np.random.default_rng(23)
RAIN = [(rng.uniform(-100, W + 100), rng.uniform(0, 1000), rng.uniform(0.7, 1.3)) for _ in range(110)]
CITY = []
x = -20
while x < W + 20:
    w = rng.uniform(70, 140); h = rng.uniform(180, 420)
    CITY.append((x, w, h)); x += w + rng.uniform(-10, 14)
CITY_WIN = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 6.28)) for _ in range(90)]
BG_CLOUDS = [(rng.uniform(0, W), rng.uniform(140, 700), rng.uniform(0.8, 1.5)) for _ in range(5)]


def jagged(x0, y0, x1, y1, n, amp, seed):
    r = np.random.default_rng(seed)
    pts = []
    for i in range(n + 1):
        k = i / n
        off = 0 if i in (0, n) else r.uniform(-amp, amp)
        pts.append((lerp(x0, x1, k) + off, lerp(y0, y1, k)))
    return pts


def poly(pts):
    return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)


def bolt(pts, grosor=1.0, glow=1.0):
    p = poly(pts)
    return (f"<polyline points='{p}' fill='none' stroke='#9fc6ff' stroke-width='{46*grosor:.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{0.35*glow:.2f}'/>"
            f"<polyline points='{p}' fill='none' stroke='{INK}' stroke-width='{22*grosor:.0f}' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<polyline points='{p}' fill='none' stroke='#fff6a8' stroke-width='{11*grosor:.0f}' stroke-linejoin='round' stroke-linecap='round'/>")


def nube(cx, cy, sc, fill, luz):
    """Nube de tormenta: círculos con el contorno debajo y el relleno encima (silueta limpia)."""
    blobs = [(-230, 30, 95), (-120, -20, 120), (10, -50, 140), (150, -15, 120), (260, 35, 90),
             (-60, 50, 110), (90, 55, 110)]
    s = [f"<g transform='translate({cx:.1f},{cy:.1f}) scale({sc})'>"]
    for bx, by, br in blobs:
        s.append(f"<circle cx='{bx}' cy='{by}' r='{br + LW:.0f}' fill='{INK}'/>")
    for bx, by, br in blobs:
        s.append(f"<circle cx='{bx}' cy='{by}' r='{br}' fill='{fill}'/>")
    s.append("</g>")
    return "".join(s)


def destello(t):
    """Intensidad del destello de los rayos (0-1)."""
    f = 0.0
    for g in GOLPES:
        if g <= t < g + 0.45:
            k = (t - g) / 0.45
            f = max(f, 0.75 * (1 - k) * (0.7 + 0.3 * math.cos(k * 25)))
    if t >= REVELACION:
        k = (t - REVELACION) / 0.7
        f = max(f, clamp(1 - k) * (0.85 + 0.15 * math.cos(k * 30)))
    return clamp(f)


def edificio(t, lit, susto, feliz):
    """Rascacielos art déco escalonado con aguja y cara."""
    sube = lerp(330, 0, seg(t, 0, 1.6))
    bob = 0 if t > 1.9 else -18 * math.sin(math.pi * clamp((t - 1.5) / 0.4))
    squash = 1 - 0.04 * susto
    sway = 1.2 * math.sin(t * 1.7)
    piel = mix("#d9c7a8", "#ffe9a6", lit)
    piel2 = mix("#bfa98a", "#ffd76b", lit)
    win_off = "#33406e"; win_on = "#ffd23f"
    g = [f"<g transform='translate(540,1920) rotate({sway:.2f}) scale(0.9,{0.9*squash:.3f}) translate(-540,{-1920 + sube + bob:.1f})'>"]
    # halo cuando se ilumina
    if lit > 0.02:
        g.append(f"<ellipse cx='540' cy='1450' rx='{330 + 30*lit:.0f}' ry='520' fill='url(#halotorre)' opacity='{lit:.2f}'/>")
    # aguja / pararrayos
    g.append(f"<polygon points='522,1205 558,1205 545,1100 535,1100' fill='#c9ced6' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<line x1='540' y1='1102' x2='540' y2='{TIP_Y}' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<circle cx='540' cy='{TIP_Y}' r='9' fill='{mix('#ff5a5f', '#fff6a8', lit)}' stroke='{INK}' stroke-width='5'/>")
    # corona
    g.append(f"<rect x='495' y='1200' width='90' height='60' rx='6' fill='{piel2}' stroke='{INK}' stroke-width='{LW}'/>")
    for wx in (512, 532, 552):
        g.append(f"<rect x='{wx}' y='1214' width='14' height='32' rx='4' fill='{mix(win_off, win_on, max(lit, 0.35))}'/>")
    # tramo alto
    g.append(f"<rect x='465' y='1255' width='150' height='95' rx='6' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    for row in range(2):
        for col in range(4):
            on = lit > 0.5 or (col + row) % 3 == 0
            g.append(f"<rect x='{480 + col*33}' y='{1270 + row*40}' width='20' height='26' rx='4' fill='{win_on if on else win_off}'/>")
    # tramo central (la cara)
    g.append(f"<rect x='415' y='1345' width='250' height='235' rx='8' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    # franjas verticales art déco
    for fx in (440, 640):
        g.append(f"<rect x='{fx - 6}' y='1355' width='12' height='215' rx='5' fill='{piel2}'/>")
    # ojos
    blink = 1.0 if ((t + 1.2) % 2.7) > 0.13 else 0.12
    if susto > 0.5: blink = 1.0
    look_y = lerp(0, -14, seg(t, 4.1, 4.7)) * (1 - feliz)
    eye_r = 38 + 8 * susto
    for ex in (495, 585):
        g.append(f"<ellipse cx='{ex}' cy='1430' rx='{eye_r:.1f}' ry='{eye_r*blink*1.08:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + 3}' cy='{1432 + look_y:.1f}' r='{18 - 4*susto:.1f}' fill='{INK}'/>")
            g.append(f"<circle cx='{ex - 4}' cy='{1424 + look_y:.1f}' r='6' fill='#fff'/>")
    # cejas
    ceja = lerp(0, -10, susto) + lerp(0, -6, feliz)
    for ex, sgn in ((495, 1), (585, -1)):
        g.append(f"<path d='M{ex - 30} {1380 + ceja + 6*sgn*0:.0f} Q{ex} {1366 + ceja:.0f} {ex + 30} {1380 + ceja:.0f}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # boca: nerviosa (o) con los rayos, sonrisa grande al final
    if feliz > 0.5:
        g.append(f"<path d='M495 1500 Q540 1555 585 1500 Z' fill='#7a2630' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M515 1528 Q540 1545 565 1528 Q540 1520 515 1528 Z' fill='#ff8a8a'/>")
    elif susto > 0.3:
        g.append(f"<ellipse cx='540' cy='1515' rx='{16 + 6*susto:.0f}' ry='{20 + 6*susto:.0f}' fill='#7a2630' stroke='{INK}' stroke-width='7'/>")
    else:
        g.append(f"<path d='M510 1508 Q540 1528 570 1508' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # mejillas
    g.append(f"<circle cx='462' cy='1490' r='16' fill='#ff9d8a' opacity='0.6'/><circle cx='618' cy='1490' r='16' fill='#ff9d8a' opacity='0.6'/>")
    # base ancha
    g.append(f"<rect x='370' y='1575' width='340' height='360' rx='8' fill='{piel2}' stroke='{INK}' stroke-width='{LW}'/>")
    for row in range(6):
        for col in range(6):
            on = lit > 0.5 or (col * 7 + row * 3) % 5 == 0
            g.append(f"<rect x='{392 + col*52}' y='{1595 + row*50}' width='32' height='32' rx='5' fill='{win_on if on else win_off}' stroke='{INK}' stroke-width='3'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    f = destello(t)
    lit = seg(t, REVELACION, REVELACION + 0.5)
    # susto en cada golpe
    susto = 0.0
    for g in GOLPES + [REVELACION]:
        if g <= t < g + 0.6:
            susto = max(susto, 1 - (t - g) / 0.6)
    if t > 4.0 and t < REVELACION:
        susto = max(susto, 0.35)
    feliz = seg(t, REVELACION + 0.35, REVELACION + 0.7)
    if feliz > 0.5: susto = 0

    top = mix("#0d1330", "#7d8fd6", f * 0.8)
    mid = mix("#1d2552", "#a9b8f0", f * 0.8)
    low = mix("#3b3a70", "#d4dcff", f * 0.7)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='halotorre'><stop offset='0' stop-color='#fff3a0' stop-opacity='0.9'/>"
            "<stop offset='0.6' stop-color='#ffcf3f' stop-opacity='0.35'/><stop offset='1' stop-color='#ffb000' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='chispa'><stop offset='0' stop-color='#ffffff' stop-opacity='1'/>"
            "<stop offset='0.4' stop-color='#bfe0ff' stop-opacity='0.8'/><stop offset='1' stop-color='#5ea8ff' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nubes lejanas, muy suaves, en la parte de arriba (fondo tranquilo)
    for i, (cx, cy, sc) in enumerate(BG_CLOUDS):
        dx = ((cx + t * (10 + 4 * i)) % (W + 500)) - 250
        s.append(f"<ellipse cx='{dx:.0f}' cy='{cy:.0f}' rx='{180*sc:.0f}' ry='{50*sc:.0f}' fill='{mix('#2a336a', '#9aa9e6', f*0.6)}' opacity='0.55'/>")

    z = 1 + 0.3 * seg(t, REVELACION, REVELACION + 0.8)
    c = []
    tip_y = 1920 - 0.9 * (1920 - TIP_Y) + 0.9 * lerp(330, 0, seg(t, 0, 1.6))
    # ciudad lejana
    for i, (bx, bw, bh) in enumerate(CITY):
        c.append(f"<rect x='{bx:.0f}' y='{1920 - bh - 120:.0f}' width='{bw:.0f}' height='{bh + 140:.0f}' fill='{mix('#222b5a', '#5d6bb0', f*0.6)}' stroke='{INK}' stroke-width='6'/>")
    for (u, v, ph) in CITY_WIN:
        b = CITY[int(u * (len(CITY) - 1))]
        wx = b[0] + 12 + (b[1] - 30) * ((ph * 7) % 1)
        wy = 1920 - b[2] - 100 + v * (b[2] - 20)
        on = math.sin(t * 1.3 + ph * 5) > -0.3 or lit > 0.5
        if on:
            c.append(f"<rect x='{wx:.0f}' y='{wy:.0f}' width='16' height='20' rx='3' fill='#ffd96a' opacity='0.85'/>")
    # calle
    c.append(f"<rect x='-20' y='1860' width='{W + 40}' height='80' fill='#1b1f3a' stroke='{INK}' stroke-width='{LW}'/>")
    c.append(edificio(t, lit, susto, feliz))
    # chispas en la punta tras cada golpe y halo eléctrico final
    for g in GOLPES:
        if g <= t < g + 0.7:
            k = (t - g) / 0.7
            for a in range(0, 360, 60):
                rr = 20 + 70 * k
                c.append(f"<circle cx='{TIP_X + rr*math.cos(math.radians(a + g*50)):.1f}' cy='{tip_y + rr*math.sin(math.radians(a + g*50)):.1f}' r='{8*(1-k):.1f}' fill='#fff6a8' stroke='{INK}' stroke-width='3'/>")
    if t >= REVELACION:
        e = seg(t, REVELACION, REVELACION + 0.3)
        pul = 1 + 0.08 * math.sin(t * 12)
        c.append(f"<circle cx='{TIP_X}' cy='{tip_y}' r='{110*e*pul:.0f}' fill='url(#chispa)' opacity='0.9'/>")
        for a in range(0, 360, 30):
            ang = math.radians(a + t * 90)
            r1, r2 = 70 * e, (120 + 20 * math.sin(t * 9 + a)) * e
            c.append(f"<line x1='{TIP_X + r1*math.cos(ang):.1f}' y1='{tip_y + r1*math.sin(ang):.1f}' x2='{TIP_X + r2*math.cos(ang):.1f}' y2='{tip_y + r2*math.sin(ang):.1f}' stroke='#fff6a8' stroke-width='7' stroke-linecap='round'/>")
    # lluvia
    for rx, ry, sp in RAIN:
        yy = (ry + t * 1300 * sp) % 1000 + 940
        xx = rx - (yy - 940) * 0.18
        c.append(f"<line x1='{xx:.0f}' y1='{yy:.0f}' x2='{xx - 9:.0f}' y2='{yy + 46:.0f}' stroke='#a9c4ff' stroke-width='4' stroke-linecap='round' opacity='0.55'/>")
    # nubes de tormenta (banda sobre la torre)
    enter = seg(t, 0, 1.4)
    luz = max(f, 0.0)
    c.append(nube(lerp(-120, 180, enter) + 12 * math.sin(t * 0.8), 830, 1.0, mix('#3d4373', '#8f9bd6', f*0.5), luz))
    c.append(nube(lerp(1200, 900, enter) - 12 * math.sin(t * 0.7), 845, 1.0, mix('#353b68', '#8590cc', f*0.5), luz))
    c.append(nube(540 + 8 * math.sin(t * 1.1), 770, 0.85, mix('#454b7e', '#9aa6e0', f*0.5), luz))
    # rayos pequeños (detrás del edificio no: caen en la aguja)
    for j, g in enumerate(GOLPES):
        if g <= t < g + 0.3 and ((t - g) * 30) % 3 < 2.2:
            x0, y0 = ((330, 950) if j % 2 == 0 else (760, 960))
            c.append(bolt(jagged(x0, y0, TIP_X, tip_y - 4, 7, 38, 100 + j), 1.0))
    # rayo gigante
    if REVELACION <= t < REVELACION + 0.75 and ((t - REVELACION) * 30) % 4 < 3.2:
        main = jagged(560, 935, TIP_X, tip_y - 4, 5, 30, 77)
        for k, (x0, y0) in enumerate(((300, 950), (790, 960))):
            c.append(bolt(jagged(x0, y0, TIP_X, tip_y - 4, 7, 40, 200 + k), 1.2, 1.4))
        c.append(bolt(main, 1.5, 1.6))
        for k, (bx, by) in enumerate(main[1:4:2]):
            c.append(bolt(jagged(bx, by, bx + (160 if k % 2 else -170), by + 110, 4, 25, 300 + k), 0.7))
    s.append(zoom(540, 1100, z, "".join(c)))
    # destello blanco general
    if f > 0.02:
        s.append(f"<rect width='{W}' height='{H}' fill='#eef3ff' opacity='{0.45*f:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
