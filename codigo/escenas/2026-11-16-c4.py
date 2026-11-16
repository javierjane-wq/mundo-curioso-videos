"""2026-11-16-c4 · Los aztecas usaban los granos de cacao como dinero (1 grano = 1 tamal).

Una mazorca de cacao con cara entra saltando en un mercado mesoamericano, suelta sus granos
sobre un petate y, en la revelación, los granos se vuelven dorados como monedas: uno vuela al
cesto de tamales y un tamal salta hacia la mazorca (el trueque). Rayos dorados y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.5    # los granos se vuelven dorados: golpe musical
MUSICA = 2

rng = np.random.default_rng(16)
MOTAS = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 7), rng.uniform(25, 60)) for _ in range(30)]
CHISPAS = [(rng.uniform(80, 1000), rng.uniform(1150, 1800), rng.uniform(14, 30), rng.uniform(0, 6.28)) for _ in range(22)]

# granos: (x final sobre el petate, y final, segundo de salida, giro final)
GRANOS = [(470, 1700, 2.6, -20), (560, 1720, 2.9, 15), (650, 1695, 3.2, -8),
          (520, 1770, 3.5, 30), (610, 1785, 3.8, -25), (700, 1760, 4.1, 10)]
BOCA = (330, 1150)   # por donde salen los granos (parte de arriba de la mazorca)


def grano(x, y, rot, s=1.0, oro=0.0):
    base = mix("#7a3b22", "#f2b632", oro); claro = mix("#a85a36", "#ffe680", oro)
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({s:.3f})'>"
            f"<ellipse rx='34' ry='22' fill='{base}' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-26 0 Q0 -6 26 0' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>"
            f"<ellipse cx='-10' cy='-9' rx='10' ry='4' fill='{claro}' opacity='0.8'/></g>")


def tamal(x, y, rot=0.0, s=1.0):
    """Tamal envuelto en hoja de maíz, atado por arriba."""
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({s:.3f})'>"
            f"<path d='M-46 40 Q-56 -10 -20 -52 L0 -78 L20 -52 Q56 -10 46 40 Q0 58 -46 40 Z' fill='#c9cf6a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-28 34 Q-30 -10 -6 -50' fill='none' stroke='#8f9a3a' stroke-width='5'/>"
            f"<path d='M26 34 Q30 -10 6 -50' fill='none' stroke='#8f9a3a' stroke-width='5'/>"
            f"<path d='M-30 14 Q0 30 30 14 Q20 -20 0 -24 Q-20 -20 -30 14 Z' fill='#f39c32' stroke='{INK}' stroke-width='5'/>"
            f"<path d='M-14 -58 L14 -58' stroke='#7a9a3a' stroke-width='8' stroke-linecap='round'/></g>")


def mazorca(t, oro):
    """Mazorca de cacao original: alargada, con surcos, punta abajo, rabito y hoja arriba."""
    x = lerp(980, 330, seg(t, 0, 2.0))
    salto = abs(math.sin(t * 7.5)) * 70 * (1 - seg(t, 1.6, 2.1))
    resp = 1 + 0.02 * math.sin(t * 3.2)
    lanza = sum(max(0.0, math.sin(math.pi * clamp((t - t0 + 0.12) / 0.25))) for _, _, t0, _ in GRANOS)
    # tras soltar los granos sigue con un balanceo; en la revelación da un saltito de alegría
    bal = 5 * math.sin(t * 2.4) + (-8 * seg(t, 5.0, 5.8) + 8 * seg(t, 7.3, 7.8))
    alegria = 40 * max(0.0, math.sin(math.pi * clamp((t - 7.5) / 0.6))) + 18 * max(0.0, math.sin(math.pi * clamp((t - 8.6) / 0.5)))
    y = 1390 - salto - alegria
    sacude = 0.0
    parp = 0.12 if (((t + 1.2) % 2.9) < 0.13 or abs(t - 6.2) < 0.07) else 1.0
    mira = lerp(0, 16, seg(t, 2.6, 3.2)) - lerp(0, 16, seg(t, 5.0, 5.4)) + lerp(0, 18, seg(t, 6.6, 7.2))
    piel = mix("#e8892c", "#f3a83a", 0.5 + 0.5 * math.sin(t * 2)); piel = mix(piel, "#ffc23d", oro * 0.6)
    oscuro = mix("#b8561d", "#d98a20", oro * 0.6)
    g = [f"<ellipse cx='{x:.1f}' cy='1608' rx='{150 - salto*0.6:.0f}' ry='24' fill='#000' opacity='0.22'/>",
         f"<g transform='translate({x + sacude:.1f},{y:.1f}) rotate({bal:.1f}) scale({resp + 0.05*lanza:.4f},{resp - 0.07*lanza:.4f})'>"]
    # rabito y hoja
    g.append(f"<path d='M0 -225 Q6 -265 -10 -295' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
             f"<path d='M0 -225 Q6 -265 -10 -295' fill='none' stroke='#6b4a2a' stroke-width='11' stroke-linecap='round'/>")
    hoja = 8 * math.sin(t * 3.1)
    g.append(f"<g transform='translate(-8,-285) rotate({-30 + hoja:.1f})'><path d='M0 0 Q60 -60 150 -30 Q80 30 0 0 Z' fill='#4fb24a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M8 -2 Q70 -30 140 -30' fill='none' stroke='#2e7d32' stroke-width='5'/></g>")
    # cuerpo: mazorca alargada con surcos (gajos alternos claros/oscuros) y punta abajo
    cuerpo = "M0 -230 C95 -226 142 -110 140 20 C138 140 84 222 12 262 C-66 226 -138 140 -140 20 C-142 -110 -95 -226 0 -230 Z"
    claro = mix(piel, "#ffd27a", 0.35)
    g.append(f"<defs><clipPath id='cmz'><path d='{cuerpo}'/></clipPath></defs>")
    g.append(f"<path d='{cuerpo}' fill='{piel}'/>")
    gaj = []
    for k in range(-4, 5):
        if k % 2 == 0:
            gaj.append(f"<ellipse cx='{k*31}' cy='15' rx='16' ry='250' fill='{claro}'/>")
        gaj.append(f"<path d='M{k*31 + 15} -235 Q{k*40 + 15} 15 {k*14 + 15} 265' fill='none' stroke='{oscuro}' stroke-width='6'/>")
    g.append(f"<g clip-path='url(#cmz)'>{''.join(gaj)}"
             f"<path d='M-120 -20 Q-100 -170 -30 -210' fill='none' stroke='#fff0b8' stroke-width='12' stroke-linecap='round' opacity='0.6'/></g>")
    g.append(f"<path d='{cuerpo}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # cara
    g.append(f"<ellipse cx='-95' cy='40' rx='26' ry='16' fill='#ff7f6e' opacity='0.6'/><ellipse cx='95' cy='40' rx='26' ry='16' fill='#ff7f6e' opacity='0.6'/>")
    for ex in (-55, 55):
        g.append(f"<ellipse cx='{ex}' cy='-30' rx='34' ry='{40*parp:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        if parp > 0.5:
            g.append(f"<circle cx='{ex + mira*0.6:.1f}' cy='-24' r='19' fill='{INK}'/><circle cx='{ex + mira*0.6 - 7:.1f}' cy='-32' r='7' fill='#fff'/>")
    boca_ab = 14 + 22 * seg(t, 7.4, 7.8)
    g.append(f"<path d='M-34 50 Q0 {50 + boca_ab*2:.0f} 34 50 Z' fill='#7a1f1f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # bracitos
    br = 20 * math.sin(t * 4) + 40 * seg(t, 7.4, 7.9)
    g.append(f"<path d='M-150 60 Q-205 {40 - br:.0f} -220 {0 - br:.0f}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<path d='M150 60 Q205 {40 - br:.0f} 220 {0 - br:.0f}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def cesto(t):
    """Cesto de mimbre con tamales, a la derecha."""
    x, y = 860, 1620
    s = [f"<ellipse cx='{x}' cy='{y + 115}' rx='170' ry='24' fill='#000' opacity='0.2'/>"]
    s.append(tamal(x - 70, y - 40, -18) + tamal(x + 5, y - 60, 4) + tamal(x + 80, y - 38, 20))
    s.append(f"<path d='M{x-160} {y-20} L{x+160} {y-20} L{x+125} {y+110} L{x-125} {y+110} Z' fill='#d9a35a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(1, 4):
        yy = y - 20 + k * 32
        s.append(f"<path d='M{x-160 + k*9} {yy} L{x+160 - k*9} {yy}' stroke='#a8743a' stroke-width='6'/>")
    for k in range(-3, 4):
        s.append(f"<path d='M{x + k*42} {y-20} L{x + k*34} {y+110}' stroke='#a8743a' stroke-width='5'/>")
    s.append(f"<rect x='{x-172}' y='{y-36}' width='344' height='28' rx='14' fill='#c58a45' stroke='{INK}' stroke-width='7'/>")
    return "".join(s)


def piramide(col, borde):
    """Templo escalonado lejano (genérico)."""
    p = []
    for i in range(5):
        w = 420 - i * 70; y = 1210 - i * 46
        p.append(f"<rect x='{800 - w/2:.0f}' y='{y}' width='{w}' height='48' fill='{col}' stroke='{borde}' stroke-width='6'/>")
    p.append(f"<rect x='{800 - 60}' y='{1210 - 5*46 - 50}' width='120' height='52' fill='{col}' stroke='{borde}' stroke-width='6'/>")
    p.append(f"<rect x='{800 - 22}' y='{1210 - 5*46 - 34}' width='44' height='36' fill='{borde}'/>")
    p.append(f"<rect x='{800 - 30}' y='{1010}' width='60' height='248' fill='{mix(col, '#ffffff', 0.15)}' stroke='{borde}' stroke-width='5'/>")
    return "".join(p)


def frame(t):
    oro = seg(t, 7.35, 7.9)
    tension = seg(t, 5.0, 6.8) * (1 - oro)
    top = mix(mix("#4fc3f7", "#3f7fb8", tension), "#ffb74d", oro * 0.55)
    mid = mix(mix("#a5e4ff", "#86b6d6", tension), "#ffe08a", oro * 0.7)
    low = mix(mix("#fff1c9", "#e6d2a8", tension), "#fff3c4", oro)
    defs = (f"<linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff8d0' stop-opacity='{0.95*oro:.3f}'/>"
            f"<stop offset='0.4' stop-color='#ffd54f' stop-opacity='{0.6*oro:.3f}'/><stop offset='1' stop-color='#ffb300' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#cielo)'/>"]
    # sol y nubes (arriba, tranquilos)
    s.append(f"<circle cx='880' cy='{560 + 10*math.sin(t):.0f}' r='{90 + 6*math.sin(t*2):.0f}' fill='#fff3b0' opacity='0.85'/>")
    for i, (cx, cy, sc) in enumerate([(150, 420, 1.2), (700, 760, 1.0), (400, 920, 0.8)]):
        dx = ((t * (16 + 6 * i) + cx) % 1500) - 250
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})' opacity='0.92'><path d='M0 40 Q15 -15 75 0 Q105 -45 165 -5 Q225 -20 245 40 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    z = 1 + 0.14 * seg(t, 7.4, 10)
    esc = []
    # rayos dorados en la revelación
    if oro > 0.01:
        rot = t * 12
        rayos = "".join(f"<path d='M0 0 L{1500*math.cos(math.radians(a - 5)):.0f} {1500*math.sin(math.radians(a - 5)):.0f} L{1500*math.cos(math.radians(a + 5)):.0f} {1500*math.sin(math.radians(a + 5)):.0f} Z' fill='#fff1a8'/>" for a in range(0, 360, 24))
        esc.append(f"<g transform='translate(600,1680) rotate({rot:.1f})' opacity='{0.45*oro:.2f}'>{rayos}</g>")
    # colinas de selva y templo lejano
    esc.append(f"<path d='M0 1180 Q140 1080 300 1150 T620 1120 T1080 1140 L1080 1920 L0 1920 Z' fill='{mix('#3f9d4a', '#2f7a3d', tension)}' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(piramide(mix("#c9a27a", "#a98b6c", tension), INK))
    for i, (px, py, r) in enumerate([(90, 1190, 90), (230, 1215, 70), (1010, 1210, 85), (560, 1230, 60)]):
        sway = 4 * math.sin(t * 1.5 + i)
        esc.append(f"<circle cx='{px + sway:.0f}' cy='{py}' r='{r}' fill='{mix('#56b85a', '#3e8e46', tension)}' stroke='{INK}' stroke-width='7'/>")
    # suelo de tierra y petate
    esc.append(f"<path d='M0 1290 Q300 1250 560 1285 T1080 1275 L1080 1920 L0 1920 Z' fill='{mix('#e0a868', '#c48f5a', tension)}' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(f"<path d='M380 1640 L960 1640 L1040 1860 L300 1860 Z' fill='#e8c27a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(1, 7):
        yy = 1640 + k * 31; xa = lerp(380, 300, k / 7); xb = lerp(960, 1040, k / 7)
        esc.append(f"<line x1='{xa:.0f}' y1='{yy}' x2='{xb:.0f}' y2='{yy}' stroke='#c79a4e' stroke-width='5'/>")
    for k in range(1, 12):
        xa = lerp(380, 960, k / 12); xb = lerp(300, 1040, k / 12)
        esc.append(f"<line x1='{xa:.0f}' y1='1640' x2='{xb:.0f}' y2='1860' stroke='#c79a4e' stroke-width='4' opacity='0.8'/>")
    esc.append(cesto(t))
    # media mazorca abierta en el suelo: pulpa blanca con semillas en hileras
    hp = ["<g transform='translate(165,1790) rotate(-8)'>",
          "<ellipse cx='0' cy='40' rx='140' ry='20' fill='#000' opacity='0.18'/>",
          f"<ellipse rx='138' ry='62' fill='#d9762a' stroke='{INK}' stroke-width='{LW}'/>",
          f"<ellipse cy='-6' rx='116' ry='42' fill='#fff7e8' stroke='{INK}' stroke-width='6'/>"]
    for fila in (-1, 0, 1):
        for c in range(-3, 4):
            hp.append(f"<ellipse cx='{c*28 + fila*6}' cy='{-6 + fila*20}' rx='12' ry='8' fill='#efd9b8' stroke='#b89a78' stroke-width='3'/>")
    hp.append("</g>")
    esc.append("".join(hp))
    # halo dorado sobre el petate
    esc.append(f"<ellipse cx='600' cy='1730' rx='{lerp(150, 520, oro):.0f}' ry='{lerp(80, 260, oro):.0f}' fill='url(#halo)'/>")
    # granos: salen de la mazorca en arco y caen al petate; tiemblan en la tensión
    for i, (gx, gy, t0, gr) in enumerate(GRANOS):
        if t < t0: continue
        k = seg(t, t0, t0 + 0.7)
        bx, by = BOCA
        x = lerp(bx, gx, k); y = lerp(by, gy, k) - 260 * math.sin(math.pi * k)
        rot = lerp(0, 360 + gr, k)
        tiembla = 5 * math.sin(t * 30 + i) * tension
        if i == 3 and t > 7.6:   # este grano vuela hasta el cesto
            v = seg(t, 7.7, 8.5)
            x = lerp(gx, 860, v); y = lerp(gy, 1560, v) - 300 * math.sin(math.pi * v); rot += 540 * v
            if v >= 1: continue
        brillo = 1 + 0.08 * math.sin(t * 8 + i) * oro
        esc.append(grano(x + tiembla, y, rot, brillo * (1 + 0.15 * oro), oro))
    # el tamal salta del cesto hacia la mazorca (el pago)
    if t > 8.3:
        v = seg(t, 8.3, 9.1)
        tx = lerp(860, 520, v); ty = lerp(1560, 1690, v) - 260 * math.sin(math.pi * v)
        esc.append(tamal(tx, ty, lerp(10, -15, v) + 6 * math.sin(t * 6), 1.45))
    esc.append(mazorca(t, oro))
    # chispas doradas tipo moneda
    for cx, cy, r, ph in CHISPAS:
        a = oro * (0.5 + 0.5 * math.sin(t * 6 + ph))
        if a > 0.05:
            rr = r * (0.7 + 0.3 * math.sin(t * 5 + ph))
            esc.append(f"<path d='M{cx} {cy - rr:.1f} Q{cx} {cy} {cx + rr:.1f} {cy} Q{cx} {cy} {cx} {cy + rr:.1f} Q{cx} {cy} {cx - rr:.1f} {cy} Q{cx} {cy} {cx} {cy - rr:.1f} Z' fill='#fff59d' stroke='#f9a825' stroke-width='3' opacity='{a:.2f}'/>")
    # motas de polvo / polen flotando
    for px, py, pr, sp in MOTAS:
        yy = (py - t * sp) % 900 + 1000
        esc.append(f"<circle cx='{px + 18*math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fff3d0' opacity='0.5'/>")
    s.append(zoom(600, 1600, z, "".join(esc)))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
