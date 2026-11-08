"""2026-11-08-c4 · El velcro nació de un paseo con perro: los cardos (bardana) se pegaban a su pelo
y al microscopio George de Mestral vio miles de ganchitos que se enganchan en bucles.

0-2,5 s  un perro original entra paseando por un prado de los Alpes.
2,5-5 s  pasa junto a unas plantas de bardana y sus cardos salen volando y se le pegan al pelo.
5-7,5 s  el perro se para y se rasca; una lupa se acerca a un cardo pegado en su lomo.
7,5-10 s REVELACION: la lupa crece hasta llenar la escena, destello y zoom: ganchos curvos
         del cardo enganchados en los bucles del pelo (la idea del velcro).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 9

GROUND = 1330
DOG_Y = 1600
rng = np.random.default_rng(41)
FLOWERS = [(rng.uniform(30, 1050), rng.uniform(1700, 1900), rng.uniform(0.7, 1.1),
            rng.choice(["#ff6b8b", "#ffd23f", "#ffffff", "#b388ff"])) for _ in range(14)]
GRASS = [(rng.uniform(0, W), rng.uniform(1380, 1900), rng.uniform(24, 42), rng.uniform(0, 6.28)) for _ in range(46)]
BUTTER = [(220, 1180, 0.0, "#ff8fb1"), (860, 1240, 2.1, "#7fd4ff")]
# cardos que se pegan: (instante, posición en el perro relativa a su centro, planta de origen)
BURRS = [(2.6, (-70, -62), 0), (3.0, (25, -74), 1), (3.35, (-125, -18), 0),
         (3.7, (95, -38), 1), (4.05, (-25, 22), 0), (4.4, (160, -150), 1)]
PLANTS = [(800, 1475, 1.0), (975, 1520, 0.85)]
HEADS = [[(-40, -235), (35, -265), (-5, -300)], [(-35, -230), (30, -255), (0, -290)]]


def dog_x(t):
    return lerp(-60, 470, seg(t, 0, 4.3))


def burr(r=16, col="#6f7f24"):
    """Cardo de bardana: bola con pinchos de punta curva."""
    g = [f"<circle r='{r}' fill='{col}' stroke='{INK}' stroke-width='5'/>"]
    for k in range(12):
        a = k * 30
        g.append(f"<path d='M0 {-r + 2} L0 {-r - 9} q0 -5 5 -4' fill='none' stroke='{INK}' stroke-width='4' "
                 f"stroke-linecap='round' transform='rotate({a})'/>")
    g.append(f"<circle cx='{-r * 0.3:.1f}' cy='{-r * 0.3:.1f}' r='{r * 0.28:.1f}' fill='#c9a85a'/>")
    return "".join(g)


def plant(x, y, sc, t, idx):
    """Bardana: tallo, hojas grandes y cabezuelas con penacho morado."""
    sway = 3 * math.sin(t * 1.7 + idx)
    g = [f"<g transform='translate({x},{y}) scale({sc}) rotate({sway:.2f})'>"]
    g.append(f"<path d='M0 0 Q-5 -150 0 -290' fill='none' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>")
    g.append(f"<path d='M0 0 Q-5 -150 0 -290' fill='none' stroke='#5c8f2f' stroke-width='8' stroke-linecap='round'/>")
    for hx, hy in HEADS[idx]:
        g.append(f"<path d='M0 {hy + 60} Q{hx * 0.5} {hy + 30} {hx} {hy}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        g.append(f"<path d='M0 {hy + 60} Q{hx * 0.5} {hy + 30} {hx} {hy}' fill='none' stroke='#5c8f2f' stroke-width='6' stroke-linecap='round'/>")
    for side in (-1, 1):
        g.append(f"<path d='M0 -20 C{side * 70} -20 {side * 150} -60 {side * 170} -120 C{side * 110} -130 {side * 40} -90 0 -60 Z' "
                 f"fill='#6fb83f' stroke='{INK}' stroke-width='{LW - 2}' stroke-linejoin='round'/>")
        g.append(f"<path d='M0 -40 Q{side * 80} -70 {side * 150} -112' fill='none' stroke='#3f7a22' stroke-width='5'/>")
    g.append(f"<path d='M0 -110 C-60 -120 -110 -150 -120 -190 C-70 -190 -25 -165 0 -140 Z' fill='#7cc64a' stroke='{INK}' stroke-width='{LW - 2}' stroke-linejoin='round'/>")
    for j, (hx, hy) in enumerate(HEADS[idx]):
        # la cabezuela desaparece cuando su cardo sale volando
        gone = any(b[2] == idx and k % 3 == j and t >= b[0] for k, b in enumerate(BURRS))
        if gone:
            g.append(f"<circle cx='{hx}' cy='{hy}' r='9' fill='#5c8f2f' stroke='{INK}' stroke-width='5'/>")
            continue
        g.append(f"<g transform='translate({hx},{hy})'>{burr(22, '#7f9a3a')}</g>")
        g.append(f"<path d='M{hx - 12} {hy - 18} L{hx - 6} {hy - 38} L{hx} {hy - 20} L{hx + 6} {hy - 40} L{hx + 12} {hy - 18} Z' "
                 f"fill='#b64fd0' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def plant_head_abs(idx, j):
    x, y, sc = PLANTS[idx]
    hx, hy = HEADS[idx][j]
    return x + hx * sc, y + hy * sc


def dog(t, x):
    """Perro original de perfil mirando a la derecha: orejas caídas, collar rojo, cola que se mueve."""
    walking = t < 4.4
    scratch = seg(t, 4.8, 5.2) * (1 - seg(t, 6.6, 7.0))
    ph = t * 9.5
    sw = 24 * math.sin(ph) if walking else 0
    bob = (5 * abs(math.sin(ph)) if walking else 2 * math.sin(t * 3)) - 2
    tail = 20 * math.sin(t * 11) + (10 if t > REVELACION else 0) * math.sin(t * 20)
    blink = 0.12 if (t % 2.7) < 0.12 else 1.0
    head_tilt = lerp(0, -14, seg(t, 5.2, 6.0)) * (1 - seg(t, 7.3, 7.8)) + lerp(0, 6, seg(t, 7.6, 8.2))
    ear = 6 * math.sin(t * 6)
    body, belly, dark = "#d98c45", "#f6d3a0", "#9a5a2a"
    g = [f"<g transform='translate({x:.1f},{DOG_Y - bob:.1f})'>"]
    g.append(f"<ellipse cx='10' cy='{150 + bob:.1f}' rx='210' ry='22' fill='#000' opacity='0.2'/>")

    def leg(lx, ang, col):
        return (f"<g transform='translate({lx},40) rotate({ang:.1f})'>"
                f"<rect x='-20' y='-10' width='40' height='110' rx='18' fill='{col}' stroke='{INK}' stroke-width='{LW - 1}'/>"
                f"<ellipse cx='6' cy='98' rx='28' ry='16' fill='{col}' stroke='{INK}' stroke-width='{LW - 2}'/></g>")
    # patas lejanas (más oscuras)
    g.append(leg(-95, -sw, dark)); g.append(leg(110, sw, dark))
    # cola
    g.append(f"<g transform='translate(-150,-20) rotate({tail - 30:.1f})'>"
             f"<path d='M0 0 Q-40 -50 -20 -110' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
             f"<path d='M0 0 Q-40 -50 -20 -110' fill='none' stroke='{body}' stroke-width='18' stroke-linecap='round'/></g>")
    # cuerpo
    g.append(f"<ellipse cx='0' cy='0' rx='165' ry='78' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-110 40 Q0 85 110 40 Q0 70 -110 40 Z' fill='{belly}'/>")
    g.append(f"<ellipse cx='-60' cy='-30' rx='55' ry='30' fill='{dark}' opacity='0.55'/>")
    # patas cercanas (la trasera se levanta para rascarse)
    back = -sw if walking else lerp(0, -55 + 12 * math.sin(t * 28), scratch)
    g.append(leg(-80, back, body)); g.append(leg(125, -sw * 0.9 if walking else 0, body))
    # cardos pegados al pelo
    for ti, (bx, by), _ in BURRS:
        if t >= ti + 0.38:
            g.append(f"<g transform='translate({bx},{by})'>{burr(19)}</g>")
    # cuello y cabeza
    g.append(f"<g transform='translate(140,-60) rotate({head_tilt:.1f})'>")
    g.append(f"<path d='M-40 40 L-10 -30 L45 -20 L30 55 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-38' y='12' width='78' height='22' rx='10' fill='#e83f4f' stroke='{INK}' stroke-width='6' transform='rotate(12)'/>")
    g.append(f"<circle cx='16' cy='42' r='11' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='35' cy='-70' r='72' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='108' cy='-48' rx='52' ry='36' fill='{belly}' stroke='{INK}' stroke-width='{LW - 1}'/>")
    g.append(f"<ellipse cx='152' cy='-62' rx='17' ry='13' fill='{INK}'/>")
    g.append(f"<path d='M110 -28 Q125 -16 140 -30' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    tongue = 1 if t > REVELACION or walking else 0
    if tongue:
        g.append(f"<path d='M118 -24 Q122 4 134 0 Q140 -14 136 -27 Z' fill='#ff7a8a' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<ellipse cx='60' cy='-92' rx='17' ry='{19 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
    if blink > 0.5:
        g.append(f"<circle cx='66' cy='-90' r='10' fill='{INK}'/><circle cx='70' cy='-95' r='4' fill='#fff'/>")
    g.append(f"<path d='M42 -122 Q60 -132 78 -124' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    # oreja caída
    g.append(f"<g transform='translate(0,-115) rotate({ear:.1f})'>"
             f"<path d='M-10 0 C-60 10 -70 90 -40 120 C-15 110 15 60 20 5 Z' fill='{dark}' stroke='{INK}' stroke-width='{LW - 1}' stroke-linejoin='round'/></g>")
    g.append("</g></g>")
    return "".join(g)


def macro(t, cx, cy, r):
    """Vista de la lupa: ganchos curvos del cardo enganchados en bucles del pelo."""
    k = seg(t, 7.5, 8.4)
    pull = 14 * math.sin(t * 5) * k
    g = [f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{mix('#fbe7c2', '#fff4d0', k)}'/>"]
    sc = r / 340.0
    g.append(f"<g transform='translate({cx},{cy}) scale({sc:.4f})'>")
    xs = [-280, -140, 0, 140]
    # cardo arriba: masa marrón con textura
    g.append(f"<path d='M-360 -360 L360 -360 L360 -215 Q180 -170 0 -200 Q-180 -170 -360 -215 Z' fill='#7a5a22' stroke='{INK}' stroke-width='12'/>")
    for ex, ey in ((-200, -270), (60, -290), (230, -250)):
        g.append(f"<ellipse cx='{ex}' cy='{ey}' rx='60' ry='16' fill='#a07a36'/>")
    # ganchos en forma de J
    for x in xs:
        hook = (f"M{x} -200 L{x} {40 + pull:.0f} Q{x} {120 + pull:.0f} {x + 55} {120 + pull:.0f} "
                f"Q{x + 110} {120 + pull:.0f} {x + 110} {50 + pull:.0f}")
        g.append(f"<path d='{hook}' fill='none' stroke='{INK}' stroke-width='36' stroke-linecap='round'/>")
        g.append(f"<path d='{hook}' fill='none' stroke='#b07a2a' stroke-width='20' stroke-linecap='round'/>")
        g.append(f"<path d='M{x - 4} -180 L{x - 4} {30 + pull:.0f}' stroke='#e2b866' stroke-width='5' stroke-linecap='round'/>")
    # bucles del pelo: suben desde abajo y pasan por encima de cada gancho
    for x in xs:
        cxl = x + 55
        loop = f"M{cxl - 75} 330 C{cxl - 95} {-20 + pull:.0f} {cxl + 95} {-20 + pull:.0f} {cxl + 75} 330"
        g.append(f"<path d='{loop}' fill='none' stroke='{INK}' stroke-width='30' stroke-linecap='round'/>")
        g.append(f"<path d='{loop}' fill='none' stroke='#ff8a3d' stroke-width='16' stroke-linecap='round'/>")
    # base de pelo
    bumps = "".join(f"Q{-360 + 60 * i + 30} 255 {-360 + 60 * (i + 1)} 285 " for i in range(12))
    g.append(f"<path d='M-360 285 {bumps}L360 380 L-360 380 Z' fill='#d98c45' stroke='{INK}' stroke-width='12' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.45, 8.3)
    sky1 = mix("#5fb6f0", "#3d8fe0", rev * 0.4); sky2 = mix("#c9ecff", "#ffe9b0", rev * 0.6)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{sky1}'/>"
            f"<stop offset='1' stop-color='{sky2}'/></linearGradient>"
            f"<radialGradient id='flash'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.9 * rev:.3f}'/>"
            f"<stop offset='0.6' stop-color='#ffd23f' stop-opacity='{0.45 * rev:.3f}'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}"]
    # lupa: posición y tamaño
    x = dog_x(t)
    tx, ty = x + 25, DOG_Y - 74          # cardo del lomo
    lin = seg(t, 5.0, 6.6)
    lx = lerp(1250, tx, lin); ly = lerp(1250, ty, lin)
    lr = 95
    lx = lerp(lx, 540, rev); ly = lerp(ly, 1440, rev); lr = lerp(lr, 360, rev)
    s.append(f"<clipPath id='lens'><circle cx='{lx:.1f}' cy='{ly:.1f}' r='{lr:.1f}'/></clipPath></defs>")
    s.append(f"<rect width='{W}' height='{H}' fill='url(#sky)'/>")
    z = 1 + 0.12 * seg(t, 7.45, 10)
    body = []
    # sol y nubes
    body.append(f"<circle cx='880' cy='330' r='{90 + 6 * math.sin(t * 2):.0f}' fill='#fff2a8' opacity='0.55'/>")
    body.append("<circle cx='880' cy='330' r='70' fill='#ffe066' stroke='#ffd23f' stroke-width='6' opacity='0.9'/>")
    for i, (cx, cy, sc) in enumerate([(160, 620, 1.2), (700, 760, 0.9), (420, 470, 0.8)]):
        dx = (t * 12 * (1 + 0.4 * i)) % 1500 - 300
        body.append(f"<g transform='translate({(cx + dx) % 1500 - 250:.0f},{cy}) scale({sc})' opacity='0.92'>"
                    f"<path d='M0 50 Q10 0 70 10 Q100 -35 160 0 Q220 -10 235 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # montañas con nieve
    for mx, peak, wdt, col in [(150, 1010, 360, "#7f8fc4"), (560, 960, 420, "#6f80b8"), (960, 1040, 340, "#8495c9")]:
        body.append(f"<path d='M{mx - wdt} 1340 L{mx} {peak} L{mx + wdt} 1340 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        sy = peak + 90; sw = wdt * 90 / (1340 - peak)
        body.append(f"<path d='M{mx - sw:.0f} {sy} L{mx} {peak} L{mx + sw:.0f} {sy} L{mx + sw * 0.4:.0f} {sy - 20} L{mx} {sy + 10} L{mx - sw * 0.4:.0f} {sy - 22} Z' "
                    f"fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # prado
    body.append(f"<path d='M0 {GROUND} Q300 1270 600 1320 T1080 1300 L1080 1920 L0 1920 Z' fill='#7ccf52' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M0 1500 Q350 1440 700 1490 T1080 1470 L1080 1920 L0 1920 Z' fill='#66bb3f' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M-20 1640 Q200 1625 420 1650 T900 1660 L1100 1650' fill='none' stroke='#d8b47a' stroke-width='60' stroke-linecap='round' opacity='0.8'/>")
    for gx, gy, gh, ph in GRASS:
        b = 6 * math.sin(t * 2.2 + ph)
        body.append(f"<path d='M{gx:.0f} {gy:.0f} q{b - 6:.1f} {-gh * 0.5:.0f} {b:.1f} {-gh:.0f}' fill='none' stroke='#3f8f2a' stroke-width='5' stroke-linecap='round'/>")
    for fx, fy, sc, col in FLOWERS:
        body.append(f"<g transform='translate({fx:.0f},{fy:.0f}) scale({sc:.2f})'>"
                    + "".join(f"<circle cx='{12 * math.cos(a):.1f}' cy='{12 * math.sin(a):.1f}' r='9' fill='{col}' stroke='{INK}' stroke-width='3'/>" for a in np.linspace(0, 6.28, 5, endpoint=False))
                    + f"<circle r='7' fill='#ffb000' stroke='{INK}' stroke-width='3'/></g>")
    # plantas lejana y perro
    body.append(plant(*PLANTS[1], t, 1))
    body.append(dog(t, x))
    body.append(plant(*PLANTS[0], t, 0))
    # cardos volando hacia el perro
    for i, (ti, (bx, by), p) in enumerate(BURRS):
        k = (t - ti) / 0.38
        if 0 <= k < 1:
            sx, sy = plant_head_abs(p, i % 3)
            ex, ey = x + bx, DOG_Y + by
            px = lerp(sx, ex, k); py = lerp(sy, ey, k) - 120 * math.sin(math.pi * k)
            body.append(f"<g transform='translate({px:.1f},{py:.1f}) rotate({k * 360:.0f})'>{burr(19)}</g>")
        elif 0.38 <= t - ti < 0.7:
            a = 1 - (t - ti - 0.38) / 0.32
            body.append(f"<circle cx='{x + bx:.0f}' cy='{DOG_Y + by:.0f}' r='{lerp(40, 18, a):.0f}' fill='none' stroke='#fff' stroke-width='6' opacity='{a:.2f}'/>")
    # mariposas
    for bx0, by0, ph, col in BUTTER:
        bx = bx0 + 70 * math.sin(t * 0.9 + ph); by = by0 + 30 * math.sin(t * 2.1 + ph)
        f = 0.35 + 0.65 * abs(math.sin(t * 12 + ph))
        body.append(f"<g transform='translate({bx:.0f},{by:.0f})'>"
                    f"<ellipse cx='-14' cy='0' rx='{16 * f:.1f}' ry='13' fill='{col}' stroke='{INK}' stroke-width='4'/>"
                    f"<ellipse cx='14' cy='0' rx='{16 * f:.1f}' ry='13' fill='{col}' stroke='{INK}' stroke-width='4'/>"
                    f"<rect x='-3' y='-12' width='6' height='24' rx='3' fill='{INK}'/></g>")
    # destello de la revelación
    if rev > 0:
        body.append(f"<rect width='{W}' height='{H}' fill='#1d1a3a' opacity='{0.22 * rev:.3f}'/>")
        body.append(f"<circle cx='540' cy='1440' r='{lerp(300, 620, rev):.0f}' fill='url(#flash)'/>")
    # lupa
    if lin > 0:
        if rev < 1:
            ia = 1 - rev
            body.append(f"<g opacity='{ia:.2f}'><line x1='{lx + lr * 0.7:.1f}' y1='{ly + lr * 0.7:.1f}' x2='{lx + lr * 0.7 + 150:.1f}' y2='{ly + lr * 0.7 + 150:.1f}' "
                        f"stroke='{INK}' stroke-width='46' stroke-linecap='round'/>"
                        f"<line x1='{lx + lr * 0.7:.1f}' y1='{ly + lr * 0.7:.1f}' x2='{lx + lr * 0.7 + 150:.1f}' y2='{ly + lr * 0.7 + 150:.1f}' "
                        f"stroke='#8b4a2b' stroke-width='28' stroke-linecap='round'/></g>")
        inner = []
        if rev < 0.5:
            # cardo ampliado x2,6 dentro de la lupa
            inner.append(f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='{lr:.1f}' fill='#d98c45'/>")
            inner.append(f"<g transform='translate({lx:.1f},{ly:.1f}) scale(2.6)' opacity='{1 - 2 * rev:.2f}'>{burr(19)}</g>")
        inner.append(f"<g opacity='{seg(t, 7.3, 7.9):.2f}'>{macro(t, lx, ly, lr)}</g>")
        body.append(f"<g clip-path='url(#lens)'>{''.join(inner)}</g>")
        body.append(f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='{lr:.1f}' fill='#ffffff' opacity='0.12'/>")
        body.append(f"<path d='M{lx - lr * 0.65:.1f} {ly - lr * 0.2:.1f} A{lr * 0.7:.1f} {lr * 0.7:.1f} 0 0 1 {lx - lr * 0.15:.1f} {ly - lr * 0.68:.1f}' "
                    f"fill='none' stroke='#ffffff' stroke-width='{lerp(8, 18, rev):.0f}' stroke-linecap='round' opacity='0.7'/>")
        body.append(f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='{lr:.1f}' fill='none' stroke='{INK}' stroke-width='{lerp(26, 34, rev):.0f}'/>")
        body.append(f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='{lr:.1f}' fill='none' stroke='#c9ced6' stroke-width='{lerp(12, 18, rev):.0f}'/>")
    # chispas en la revelación
    if rev > 0:
        for i in range(10):
            a = i * 36 + t * 40
            rr = 400 + 30 * math.sin(t * 6 + i)
            px = 540 + rr * math.cos(math.radians(a)); py = 1440 + rr * math.sin(math.radians(a)) * 0.9
            if py > 1040:
                sz = 14 + 6 * math.sin(t * 8 + i)
                body.append(f"<path d='M{px:.0f} {py - sz:.0f} L{px + sz * 0.3:.0f} {py:.0f} L{px:.0f} {py + sz:.0f} L{px - sz * 0.3:.0f} {py:.0f} Z' fill='#fff6b0' opacity='{rev:.2f}'/>")
    s.append(zoom(540, 1440, z, "".join(body)))
    s.append("</svg>")
    return "".join(s)
