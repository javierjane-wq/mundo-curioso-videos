"""La masa de modelar nació como limpiador de papel pintado: en los años 30 se usaba para
quitar el hollín del carbón de las paredes; cuando las casas dejaron el carbón, se vendió
como juguete (Smithsonian Magazine, The Strong National Museum of Play).

Protagonista: una bola de masa original con ojos que rueda junto a la pared y limpia el hollín
(mitad de abajo). Arriba solo la pared con papel pintado tranquilo.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.4   # estallido de colores: la masa se convierte en juguete
MUSICA = 5

rng = np.random.default_rng(1128)
FLOOR = 1770                 # borde superior del suelo
R = 140                      # radio de la bola de masa
CY = FLOOR - R + 6           # centro de la bola apoyada en el suelo
SOOT = [(rng.uniform(40, 1040), rng.uniform(1240, 1730), rng.uniform(40, 110), rng.uniform(25, 70),
         rng.uniform(0.35, 0.7)) for _ in range(34)]
MOTES = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(3, 6), rng.uniform(0, 6.28)) for _ in range(26)]
CONF = [(rng.uniform(0, 6.28), rng.uniform(250, 620), rng.uniform(0.6, 1.3),
         ["#ff4f6d", "#ffd23f", "#3fa7ff", "#4fd17a", "#b36bff"][i % 5]) for i in range(30)]
FLECOS = [(rng.uniform(-1, 1), rng.uniform(0, 1)) for _ in range(10)]


def dough_x(t):
    return lerp(130, 540, seg(t, 0, 4.6))


def pared(t, dim, rev):
    s = []
    base = mix(mix("#f6e7c8", "#d9d3c7", dim), "#fff1d0", rev)
    s.append(f"<rect width='{W}' height='{H}' fill='{base}'/>")
    stripe = mix(mix("#eecfa0", "#c8c0b2", dim), "#ffd9a8", rev)
    for i in range(0, 12):
        x = i * 100 + 20
        s.append(f"<rect x='{x}' y='0' width='44' height='{FLOOR}' fill='{stripe}' opacity='0.55'/>")
    # florecitas del papel pintado (suaves)
    flor = mix(mix("#e7a98a", "#b8aca0", dim), "#f4a07a", rev)
    for row in range(0, 17):
        for col in range(0, 6):
            fx = col * 200 + (100 if row % 2 else 0) - 40
            fy = row * 110 + 60
            if fy > FLOOR - 40:
                continue
            for a in range(0, 360, 72):
                px = fx + 11 * math.cos(math.radians(a)); py = fy + 11 * math.sin(math.radians(a))
                s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='8' fill='{flor}' opacity='0.45'/>")
            s.append(f"<circle cx='{fx}' cy='{fy}' r='6' fill='#f7d36b' opacity='0.6'/>")
    # luz de la lámpara (arriba, tranquila)
    s.append(f"<ellipse cx='540' cy='260' rx='{lerp(520, 700, rev):.0f}' ry='{lerp(420, 560, rev):.0f}' fill='url(#luz)'/>")
    return "".join(s)


def lampara(t, rev):
    sw = 3 * math.sin(t * 1.6)
    on = mix("#ffe9a8", "#fff6d0", rev)
    return (f"<g transform='translate(540,0) rotate({sw:.2f})'>"
            f"<line x1='0' y1='0' x2='0' y2='170' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-90 250 Q-80 170 0 165 Q80 170 90 250 Z' fill='#e85d4f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='252' rx='42' ry='16' fill='{on}' stroke='{INK}' stroke-width='6'/></g>")


def hollin(t):
    """Manchas de hollín en la pared; la masa las borra a su paso (máscara)."""
    x = dough_x(t)
    s = [f"<g mask='url(#limpio)'>"]
    for sx, sy, rx, ry, op in SOOT:
        s.append(f"<ellipse cx='{sx:.0f}' cy='{sy:.0f}' rx='{rx:.0f}' ry='{ry:.0f}' fill='#3a332e' opacity='{min(0.9, op + 0.2):.2f}'/>")
    s.append("</g>")
    return "".join(s), x


def suelo(dim, rev):
    s = []
    rod = mix(mix("#f2efe8", "#cfcac0", dim), "#ffffff", rev)
    s.append(f"<rect x='-10' y='{FLOOR - 46}' width='{W + 20}' height='50' fill='{rod}' stroke='{INK}' stroke-width='{LW}'/>")
    wood = mix(mix("#c9824a", "#9a7458", dim), "#e0985a", rev)
    s.append(f"<rect x='-10' y='{FLOOR}' width='{W + 20}' height='{H - FLOOR + 10}' fill='{wood}' stroke='{INK}' stroke-width='{LW}'/>")
    for i, yy in enumerate((FLOOR + 50, FLOOR + 105)):
        s.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='{INK}' stroke-width='5' opacity='0.5'/>")
        for k in range(6):
            xx = k * 210 + (100 if i % 2 else 0)
            s.append(f"<line x1='{xx}' y1='{yy - 52}' x2='{xx}' y2='{yy}' stroke='{INK}' stroke-width='5' opacity='0.5'/>")
    return "".join(s)


def masa(t, dirt, sad, rev):
    """Bola de masa blandita con ojos, huellas de dedos y aplastamiento al rodar."""
    x = dough_x(t)
    rolling = t < 4.7
    hop = abs(math.sin(t * 6.5)) * 22 if rolling else 0
    sq = 1 + (0.06 * math.sin(t * 13) if rolling else 0.03 * math.sin(t * 3)) - 0.08 * sad + 0.05 * rev
    sx, sy = 1 / sq, sq
    rot = lerp(0, 560, seg(t, 0, 4.6))
    col = mix(mix("#f4ead0", "#d8cfbf", dirt), "#ffd23f", rev)
    sh = mix(mix("#dcc9a2", "#a89f90", dirt), "#f0a91c", rev)
    shake = 4 * math.sin(t * 40) if 5.0 < t < 7.2 else 0
    cy = CY - hop
    g = [f"<ellipse cx='{x:.1f}' cy='{FLOOR + 14}' rx='{R * 1.05:.0f}' ry='22' fill='#000' opacity='0.2'/>"]
    g.append(f"<g transform='translate({x + shake:.1f},{cy + R:.1f}) scale({sx:.3f},{sy:.3f}) translate(0,{-R})'>")
    # cuerpo con borde algo irregular
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        rr = R * (1 + 0.035 * math.sin(3 * a + 1.3) + 0.025 * math.sin(5 * a + t * 2))
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"
    g.append(f"<path d='{d}' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-100 70 Q0 140 100 70 Q60 120 0 125 Q-60 120 -100 70 Z' fill='{sh}' opacity='0.6'/>")
    # huellas de dedos que giran al rodar
    g.append(f"<g transform='rotate({rot:.1f})'>")
    for ax, ay, a0 in ((-70, -60, 20), (75, -40, -30), (20, 75, 60)):
        g.append(f"<path d='M{ax - 22} {ay} Q{ax} {ay - 18} {ax + 22} {ay}' fill='none' stroke='{sh}' stroke-width='6' stroke-linecap='round' transform='rotate({a0} {ax} {ay})'/>"
                 f"<path d='M{ax - 14} {ay + 10} Q{ax} {ay - 2} {ax + 14} {ay + 10}' fill='none' stroke='{sh}' stroke-width='5' stroke-linecap='round' transform='rotate({a0} {ax} {ay})'/>")
    g.append("</g>")
    # manchas de hollín recogidas
    for hx, hy, hr in ((-80, 20, 13), (60, 62, 11), (95, -10, 9)):
        g.append(f"<circle cx='{hx}' cy='{hy}' r='{hr}' fill='#4a4440' opacity='{0.75 * dirt * (1 - rev):.2f}'/>")
    # brillo
    g.append(f"<ellipse cx='-62' cy='-78' rx='34' ry='18' fill='#fff' opacity='{lerp(0.55, 0.25, dirt) + 0.3 * rev:.2f}' transform='rotate(-30 -62 -78)'/>")
    # ojos
    blink = 1.0 if ((t + 0.4) % 2.7) > 0.13 else 0.12
    look = lerp(14, 0, seg(t, 4.2, 5.0))
    for ex in (-46, 46):
        g.append(f"<ellipse cx='{ex}' cy='-12' rx='30' ry='{36 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look:.1f}' cy='-6' r='16' fill='{INK}'/><circle cx='{ex + look - 6:.1f}' cy='-13' r='6' fill='#fff'/>")
    # cejas (tristes en la tensión)
    by = -60
    for ex, sgn in ((-46, 1), (46, -1)):
        tilt = sgn * lerp(0, 16, sad) * (1 - rev)
        g.append(f"<line x1='{ex - 24}' y1='{by + tilt:.1f}' x2='{ex + 24}' y2='{by - tilt:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # boca: sonrisa -> triste -> gran sonrisa
    smile = lerp(lerp(18, -14, sad), 34, rev)
    if rev > 0.5:
        g.append(f"<path d='M-38 40 Q0 {40 + smile * 2:.1f} 38 40 Z' fill='#c2364a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M-30 44 Q0 {44 + smile:.1f} 30 44' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # mofletes
    g.append(f"<ellipse cx='-88' cy='30' rx='18' ry='11' fill='#ff8a8a' opacity='{0.5 * (1 - dirt) + 0.5 * rev:.2f}'/>"
             f"<ellipse cx='88' cy='30' rx='18' ry='11' fill='#ff8a8a' opacity='{0.5 * (1 - dirt) + 0.5 * rev:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def bote(t, dim, rev):
    """Bote de cartón con tapa: de gris (limpiador) a colores (juguete)."""
    bx, top, w = 930, FLOOR - 230, 170
    body = mix(mix("#c8b48a", "#a89c86", dim), "#ff4f6d", rev)
    band = mix(mix("#7d6a4c", "#6e6558", dim), "#ffd23f", rev)
    lid = mix(mix("#d9c9a3", "#b5ab98", dim), "#3fa7ff", rev)
    bob = 6 * math.sin(t * 2.2)
    g = [f"<ellipse cx='{bx}' cy='{FLOOR + 12}' rx='{w * 0.62:.0f}' ry='16' fill='#000' opacity='0.2'/>"]
    g.append(f"<path d='M{bx - w / 2} {top} L{bx - w / 2} {FLOOR} Q{bx} {FLOOR + 30} {bx + w / 2} {FLOOR} L{bx + w / 2} {top} Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M{bx - w / 2} {top + 70} Q{bx} {top + 98} {bx + w / 2} {top + 70} L{bx + w / 2} {top + 130} Q{bx} {top + 158} {bx - w / 2} {top + 130} Z' fill='{band}' stroke='{INK}' stroke-width='6'/>")
    # estrellitas del dibujo del bote (sin texto)
    for k, (sx, sy) in enumerate(((bx - 40, top + 190), (bx + 35, top + 175))):
        g.append(f"<circle cx='{sx}' cy='{sy}' r='14' fill='{mix(band, '#ffffff', 0.4)}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<ellipse cx='{bx}' cy='{top}' rx='{w / 2}' ry='26' fill='{mix(body, '#000000', 0.25)}' stroke='{INK}' stroke-width='{LW}'/>")
    # tapa apoyada inclinada al lado
    g.append(f"<g transform='translate({bx - 10},{top - 40 + bob:.1f}) rotate({-14 + 4 * math.sin(t * 2.2):.1f})'>"
             f"<ellipse cx='0' cy='14' rx='{w / 2 + 10}' ry='28' fill='{mix(lid, '#000000', 0.2)}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<ellipse cx='0' cy='0' rx='{w / 2 + 10}' ry='28' fill='{lid}' stroke='{INK}' stroke-width='{LW}'/></g>")
    return "".join(g)


def bolita(cx, cy, r, col, k, t, ph):
    if k <= 0:
        return ""
    bob = 8 * math.sin(t * 5 + ph)
    sh = mix(col, "#000000", 0.25)
    return (f"<g transform='translate({cx},{cy + bob:.1f}) scale({k:.3f})'>"
            f"<ellipse cx='0' cy='{r + 8}' rx='{r}' ry='10' fill='#000' opacity='0.18'/>"
            f"<circle r='{r}' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M{-r * 0.6:.0f} {r * 0.45:.0f} Q0 {r * 0.95:.0f} {r * 0.6:.0f} {r * 0.45:.0f}' fill='none' stroke='{sh}' stroke-width='6' stroke-linecap='round'/>"
            f"<ellipse cx='{-r * 0.35:.0f}' cy='{-r * 0.4:.0f}' rx='{r * 0.25:.0f}' ry='{r * 0.14:.0f}' fill='#fff' opacity='0.6'/></g>")


def estrella(cx, cy, r, col, k, t):
    if k <= 0:
        return ""
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.48
        pts.append(f"{rr * math.cos(a):.1f} {rr * math.sin(a):.1f}")
    rot = 8 * math.sin(t * 3)
    return (f"<g transform='translate({cx},{cy}) rotate({rot:.1f}) scale({k:.3f})'>"
            f"<path d='M{' L'.join(pts)} Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")


def churro(cx, cy, col, k, t):
    """Tira de masa enrollada en espiral (como un caracol)."""
    if k <= 0:
        return ""
    pts = []
    for i in range(60):
        a = i * 0.22
        rr = 5 + a * 5.2
        pts.append(f"{rr * math.cos(a):.1f} {rr * math.sin(a):.1f}")
    return (f"<g transform='translate({cx},{cy + 4 * math.sin(t * 4):.1f}) scale({k:.3f})'>"
            f"<path d='M{' L'.join(pts)}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
            f"<path d='M{' L'.join(pts)}' fill='none' stroke='{col}' stroke-width='20' stroke-linecap='round'/></g>")


def frame(t):
    dim = 0.6 * seg(t, 4.8, 6.0) * (1 - seg(t, 7.3, 7.6))
    rev = seg(t, 7.35, 7.75)
    dirt = seg(t, 0.6, 4.6)
    sad = seg(t, 5.0, 6.2) * (1 - rev)
    x = dough_x(t)
    defs = (
        "<radialGradient id='luz'><stop offset='0' stop-color='#fff8dc' stop-opacity='0.55'/>"
        "<stop offset='1' stop-color='#fff8dc' stop-opacity='0'/></radialGradient>"
        f"<radialGradient id='arco'><stop offset='0' stop-color='#fff' stop-opacity='{0.95 * rev:.3f}'/>"
        f"<stop offset='0.3' stop-color='#ffe066' stop-opacity='{0.8 * rev:.3f}'/>"
        f"<stop offset='0.55' stop-color='#ff7aa8' stop-opacity='{0.55 * rev:.3f}'/>"
        f"<stop offset='0.8' stop-color='#6ac8ff' stop-opacity='{0.35 * rev:.3f}'/>"
        "<stop offset='1' stop-color='#6ac8ff' stop-opacity='0'/></radialGradient>"
        "<mask id='limpio' maskUnits='userSpaceOnUse' x='0' y='0' width='1080' height='1920'>"
        "<rect width='1080' height='1920' fill='#fff'/>"
        f"<rect x='-200' y='{CY - R + 10}' width='{x + 200:.0f}' height='{FLOOR - (CY - R + 10)}' rx='40' fill='#000'/></mask>"
    )
    s = [pared(t, dim, rev)]
    soot, _ = hollin(t)
    s.append(soot)
    s.append(lampara(t, rev))
    # destellos en la franja recién limpiada
    for i in range(6):
        sx = 60 + i * 85
        if sx < x - 150:
            k = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
            sy = CY - 60 + (i % 3) * 50
            r = 10 + 12 * k
            s.append(f"<path d='M{sx} {sy - r:.0f} L{sx + r * 0.3:.0f} {sy} L{sx} {sy + r:.0f} L{sx - r * 0.3:.0f} {sy} Z M{sx - r:.0f} {sy} L{sx} {sy + r * 0.3:.0f} L{sx + r:.0f} {sy} L{sx} {sy - r * 0.3:.0f} Z' fill='#fff' opacity='{0.5 + 0.5 * k:.2f}'/>")
    # motas de polvo flotando
    for mx, my, mr, ph in MOTES:
        yy = 300 + ((my * 1500 + t * 30) % 1500)
        s.append(f"<circle cx='{mx + 18 * math.sin(t * 0.8 + ph):.0f}' cy='{yy:.0f}' r='{mr:.1f}' fill='#fff' opacity='{0.35 + 0.2 * math.sin(t * 2 + ph):.2f}'/>")
    scene = [suelo(dim, rev)]
    # halo de colores tras la masa en la revelación
    if rev > 0:
        scene.append(f"<circle cx='540' cy='{CY}' r='{lerp(150, 620, rev):.0f}' fill='url(#arco)'/>")
    # copos de hollín que suelta al rodar
    if 0.8 < t < 5.0:
        for fx, fp in FLECOS:
            k = ((t * 1.4 + fp) % 1)
            scene.append(f"<circle cx='{x - 120 - 60 * k + 30 * fx:.0f}' cy='{CY - 40 + 160 * k:.0f}' r='{lerp(9, 3, k):.1f}' fill='#4a4440' opacity='{0.7 * (1 - k):.2f}'/>")
    scene.append(bote(t, dim, rev))
    # confeti
    if rev > 0:
        for a, dist, sp, c in CONF:
            k = clamp((t - 7.4) * sp)
            cx = 540 + math.cos(a) * dist * k
            cy = CY - 40 + math.sin(a) * dist * k * 0.8 + 260 * max(0, t - 7.9) ** 2 * 0.3
            if cy > 1060:
                scene.append(f"<rect x='{cx - 9:.0f}' y='{cy - 5:.0f}' width='18' height='10' rx='3' fill='{c}' stroke='{INK}' stroke-width='3' transform='rotate({(t * 300 + a * 50) % 360:.0f} {cx:.0f} {cy:.0f})'/>")
    scene.append(masa(t, dirt, sad, rev))
    # juguetes de colores que aparecen con rebote
    scene.append(bolita(165, FLOOR + 10, 55, "#3fa7ff", rebote(t, 7.45, 0.45), t, 0))
    scene.append(estrella(330, FLOOR + 50, 62, "#4fd17a", rebote(t, 7.6, 0.45), t))
    scene.append(churro(745, FLOOR + 40, "#b36bff", rebote(t, 7.7, 0.45), t))
    z = 1 + 0.12 * seg(t, 7.3, 8.1)
    s = [zoom(540, CY, z, "".join(s) + "".join(scene))]
    # destello
    fl = clamp(1 - abs(t - 7.42) / 0.18)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff' opacity='{0.7 * fl:.2f}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
