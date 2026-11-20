"""2026-11-20-c1 · Inventos: ENIAC, uno de los primeros ordenadores, pesaba unas 27 toneladas.

Una sala con una fila enorme de armarios llenos de válvulas y luces (el ordenador, con cara en el
armario central). La cámara se aleja para mostrar que ocupa la sala entera; un móvil pequeño entra
andando y lo mira. Todo está sobre una báscula gigante: la aguja sube y, en la REVELACION, llega al
tope, todas las luces se encienden en amarillo, la sala tiembla y la cámara se acerca a la esfera.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 6.7   # la aguja de la báscula llega al tope: golpe musical
MUSICA = 5

rng = np.random.default_rng(20)
CAB_W = 190
CABS = list(range(-505, 1500, CAB_W))          # x izquierda de cada armario
LUCES = {x: [(rng.uniform(0, 6.28), rng.uniform(1.2, 3.5), rng.integers(0, 3)) for _ in range(18)] for x in CABS}
MOTAS = [(rng.uniform(0, W), rng.uniform(950, 1900), rng.uniform(2.5, 5), rng.uniform(15, 40)) for _ in range(30)]
CABLES = [(CABS[i] + CAB_W - 20, CABS[i + 1] + 20, c) for i, c in
          zip(range(0, len(CABS) - 1), ["#ff5a5f", "#3fa7ff", "#ffd23f", "#5fd068"] * 4)]
LUZ_COL = ["#ff9a3c", "#ffd23f", "#ff5a5f"]


def armario(x, t, brillo, cara=False):
    """Un armario del ordenador: cuerpo oscuro, rejilla de válvulas que se encienden y diales."""
    s = []
    y0, y1 = 1040, 1585
    body = mix("#3b4554", "#5a5030", brillo)
    s.append(f"<rect x='{x}' y='{y0}' width='{CAB_W}' height='{y1 - y0}' rx='10' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{x - 6}' y='{y0 - 26}' width='{CAB_W + 12}' height='34' rx='8' fill='#2a303a' stroke='{INK}' stroke-width='{LW}'/>")
    # zócalo
    s.append(f"<rect x='{x + 10}' y='{y1 - 60}' width='{CAB_W - 20}' height='44' rx='6' fill='#2a303a' stroke='{INK}' stroke-width='6'/>")
    if cara:
        # dos grandes indicadores redondos que son los ojos, con párpados que parpadean
        blink = 1.0 if ((t + 1.0) % 2.9) > 0.14 else 0.1
        wide = 1 + 0.25 * seg(t, REVELACION - 0.1, REVELACION + 0.2)
        look = lerp(0, 14, seg(t, 2.0, 3.0)) - lerp(0, 14, seg(t, 5.0, 5.6))
        lookdown = lerp(0, 14, seg(t, 5.0, 5.8)) * (1 - seg(t, REVELACION, REVELACION + 0.3))
        for ex in (x + 52, x + 138):
            s.append(f"<circle cx='{ex}' cy='1150' r='{40 * wide:.1f}' fill='#fffaf0' stroke='{INK}' stroke-width='{LW}'/>")
            s.append(f"<g transform='translate({ex + look:.1f},{1150 + lookdown:.1f}) scale(1,{blink})'>"
                     f"<circle r='{19 * wide:.1f}' fill='#1e2a38'/><circle cx='-7' cy='-8' r='7' fill='#fff'/></g>")
        # boca: rejilla que se abre en una "O" de sorpresa
        o = seg(t, REVELACION - 0.05, REVELACION + 0.25)
        s.append(f"<rect x='{x + 60}' y='{1232 - 22 * o:.1f}' width='70' height='{18 + 44 * o:.1f}' rx='{9 + 22 * o:.1f}' fill='#1e1416' stroke='{INK}' stroke-width='7'/>")
        if o < 0.5:
            for gx in range(x + 72, x + 130, 14):
                s.append(f"<line x1='{gx}' y1='1236' x2='{gx}' y2='1246' stroke='#6b7484' stroke-width='4'/>")
        # mejillas
        s.append(f"<ellipse cx='{x + 30}' cy='1225' rx='16' ry='10' fill='#ff7a8a' opacity='0.55'/>")
        s.append(f"<ellipse cx='{x + 160}' cy='1225' rx='16' ry='10' fill='#ff7a8a' opacity='0.55'/>")
        fila0 = 1300
    else:
        # dos diales con aguja que oscila
        for i, dx in enumerate((50, 140)):
            a = 40 * math.sin(t * (2.2 + i) + x * 0.01)
            s.append(f"<circle cx='{x + dx}' cy='1110' r='30' fill='#f2ead8' stroke='{INK}' stroke-width='6'/>")
            s.append(f"<line x1='{x + dx}' y1='1110' x2='{x + dx + 22 * math.sin(math.radians(a)):.1f}' y2='{1110 - 22 * math.cos(math.radians(a)):.1f}' stroke='#d33' stroke-width='5' stroke-linecap='round'/>")
        fila0 = 1175
    # rejilla de válvulas (luces)
    filas = 4 if cara else 6
    for i, (ph, sp, ci) in enumerate(LUCES[x][:filas * 3]):
        cx = x + 42 + (i % 3) * 53; cy = fila0 + (i // 3) * 56
        on = 0.5 + 0.5 * math.sin(t * sp * 2 + ph) > 0.45
        lit = max(brillo, 1.0 if on else 0.0)
        col = mix("#4a3a30", LUZ_COL[ci], lit) if brillo < 0.5 else mix(LUZ_COL[ci], "#fff3a0", brillo)
        s.append(f"<circle cx='{cx}' cy='{cy}' r='17' fill='#20252d' stroke='{INK}' stroke-width='5'/>")
        s.append(f"<circle cx='{cx}' cy='{cy}' r='11' fill='{col}'/>")
        if lit > 0.5:
            s.append(f"<circle cx='{cx - 4}' cy='{cy - 4}' r='4' fill='#fff' opacity='0.8'/>")
    return "".join(s)


def movil(t):
    """Un móvil pequeño con cara que entra andando desde la derecha y mira el ordenador."""
    x = lerp(1180, 900, seg(t, 0, 2.4))
    walking = t < 2.5
    hop = -abs(math.sin(t * 9)) * 14 if walking else 0
    sorpresa = seg(t, REVELACION, REVELACION + 0.25) * (1 - 0.6 * seg(t, REVELACION + 0.6, REVELACION + 1.2))
    hop -= 60 * sorpresa
    tilt = (5 * math.sin(t * 9) if walking else 2 * math.sin(t * 2)) - 8 * seg(t, 2.6, 3.4)
    blink = 1.0 if ((t + 1.3) % 3.3) > 0.13 else 0.1
    y = 1880 + hop
    g = [f"<ellipse cx='{x:.1f}' cy='1885' rx='{70 - 0.3 * abs(hop):.1f}' ry='12' fill='#000' opacity='0.22'/>"]
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({tilt:.1f})'>")
    # piernas y brazos
    st = 18 * math.sin(t * 9) if walking else 0
    g.append(f"<path d='M-24 -8 L{-24 + st:.1f} 0 M24 -8 L{24 - st:.1f} 0' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    arm = -50 * sorpresa
    g.append(f"<path d='M-58 -110 Q-90 {-90 + arm:.1f} -84 {-60 + 2 * arm:.1f}' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M58 -110 Q90 {-90 + arm:.1f} 84 {-60 + 2 * arm:.1f}' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    # cuerpo del móvil
    g.append(f"<rect x='-60' y='-200' width='120' height='196' rx='22' fill='#30363f' stroke='{INK}' stroke-width='{LW}'/>")
    pant = mix("#5ec8ff", "#bff0ff", sorpresa)
    g.append(f"<rect x='-48' y='-186' width='96' height='166' rx='12' fill='{pant}'/>")
    g.append(f"<rect x='-14' y='-196' width='28' height='7' rx='3' fill='#1b1f25'/>")
    # cara en la pantalla
    ey = 1 + 0.35 * sorpresa
    for ex in (-20, 20):
        g.append(f"<g transform='translate({ex},-120) scale({ey:.2f},{blink * ey:.2f})'><ellipse rx='11' ry='14' fill='#1e2a38'/>"
                 f"<circle cx='-3' cy='-5' r='4' fill='#fff'/></g>")
    if sorpresa > 0.3:
        g.append(f"<ellipse cx='0' cy='-74' rx='11' ry='{8 + 8 * sorpresa:.1f}' fill='#1e2a38'/>")
    else:
        g.append("<path d='M-14 -80 Q0 -68 14 -80' fill='none' stroke='#1e2a38' stroke-width='6' stroke-linecap='round'/>")
    g.append("<ellipse cx='-32' cy='-90' rx='8' ry='5' fill='#ff7a8a' opacity='0.6'/><ellipse cx='32' cy='-90' rx='8' ry='5' fill='#ff7a8a' opacity='0.6'/>")
    g.append("</g>")
    return "".join(g)


def bascula(t):
    """Esfera de báscula gigante delante del ordenador; la aguja sube y llega al tope."""
    cx, cy, r = 540, 1745, 135
    sube = 0.15 * seg(t, 1.0, 3.0) + 0.45 * seg(t, 4.5, 6.2) + 0.4 * seg(t, 6.3, REVELACION)
    tiembla = 4 * math.sin(t * 40) * seg(t, 4.5, 5.3) * (1 - seg(t, 5.8, 6.3))
    rebote = 6 * math.sin((t - REVELACION) * 18) * math.exp(-(t - REVELACION) * 3) if t > REVELACION else 0
    ang = -130 + 260 * sube + tiembla + rebote
    flash = seg(t, REVELACION - 0.05, REVELACION + 0.2)
    s = [f"<rect x='{cx - 60}' y='1600' width='120' height='40' fill='#8d98a6' stroke='{INK}' stroke-width='{LW}'/>"]
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 22}' fill='#c94a3a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{mix('#fffaf0', '#fff0a0', flash)}' stroke='{INK}' stroke-width='6'/>")
    # zona roja del final de la escala
    a0, a1 = math.radians(80 - 90), math.radians(130 - 90)
    rr = r - 18
    s.append(f"<path d='M{cx + rr * math.cos(a0):.1f} {cy + rr * math.sin(a0):.1f} A{rr} {rr} 0 0 1 {cx + rr * math.cos(a1):.1f} {cy + rr * math.sin(a1):.1f}' "
             f"fill='none' stroke='#ff5a5f' stroke-width='16'/>")
    for i in range(14):
        a = math.radians(-130 + i * 20 - 90)
        l = 26 if i % 2 == 0 else 14
        s.append(f"<line x1='{cx + (r - 8) * math.cos(a):.1f}' y1='{cy + (r - 8) * math.sin(a):.1f}' "
                 f"x2='{cx + (r - 8 - l) * math.cos(a):.1f}' y2='{cy + (r - 8 - l) * math.sin(a):.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    a = math.radians(ang - 90)
    s.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + (r - 30) * math.cos(a):.1f}' y2='{cy + (r - 30) * math.sin(a):.1f}' stroke='#d22' stroke-width='12' stroke-linecap='round'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='18' fill='{INK}'/>")
    return "".join(s)


def frame(t):
    brillo = seg(t, REVELACION - 0.05, REVELACION + 0.25) * (1 - 0.35 * seg(t, REVELACION + 0.8, 9.5))
    # cámara: empieza cerca y se aleja (sala entera); en la revelación se acerca a la báscula
    z = lerp(1.35, 1.0, seg(t, 0, 4.6)) + 0.13 * seg(t, REVELACION - 0.1, REVELACION + 0.6)
    zx, zy = 540, lerp(1350, 1450, seg(t, 0, 4.6))
    if t > REVELACION - 0.1:
        zy = lerp(zy, 1560, seg(t, REVELACION - 0.1, REVELACION + 0.6))
    sh = 10 * math.sin(t * 47) * math.exp(-max(0, t - REVELACION) * 4) if t > REVELACION else 0
    top = mix("#bcd9ea", "#ffe6a8", brillo * 0.8); low = mix("#8fb4cc", "#ffc970", brillo * 0.8)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#fff6c0' stop-opacity='{0.85 * brillo:.3f}'/>"
         f"<stop offset='1' stop-color='#ffb040' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # paneles suaves de la pared (fondo tranquilo arriba)
    for px in range(-60, W + 60, 270):
        s.append(f"<rect x='{px}' y='120' width='230' height='760' rx='18' fill='#ffffff' opacity='0.10'/>")
    s.append(f"<g transform='translate({sh:.1f},0)'>")
    s.append(f"<g transform='translate({zx:.1f},{zy:.1f}) scale({z:.4f}) translate({-zx:.1f},{-zy:.1f})'>")
    # zócalo de la pared y suelo de baldosas
    s.append(f"<rect x='-500' y='960' width='2080' height='40' fill='#6f8ea3' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<rect x='-500' y='1000' width='2080' height='640' fill='{mix('#9fbfd2', '#ffd890', brillo * 0.6)}'/>")
    s.append(f"<rect x='-500' y='1630' width='2080' height='400' fill='#e8d9b8' stroke='{INK}' stroke-width='{LW}'/>")
    for row, yy in enumerate(range(1630, 1940, 75)):
        for i, xx in enumerate(range(-500, 1600, 120)):
            if (i + row) % 2 == 0:
                s.append(f"<rect x='{xx}' y='{yy}' width='120' height='75' fill='#d2bd94'/>")
    s.append(f"<line x1='-500' y1='1630' x2='1580' y2='1630' stroke='{INK}' stroke-width='{LW}'/>")
    # halo de la revelación
    if brillo > 0.01:
        s.append(f"<circle cx='540' cy='1300' r='{lerp(300, 900, brillo):.0f}' fill='url(#halo)'/>")
    # plataforma de la báscula bajo todo el ordenador
    s.append(f"<rect x='-480' y='1580' width='2040' height='34' rx='8' fill='#8d98a6' stroke='{INK}' stroke-width='{LW}'/>")
    # armarios
    for x in CABS:
        s.append(armario(x, t, brillo, cara=(x == 445)))
    # cables entre armarios, balanceándose
    for i, (xa, xb, c) in enumerate(CABLES):
        sag = 1490 + 22 * math.sin(t * 2.4 + i)
        s.append(f"<path d='M{xa} 1440 Q{(xa + xb) / 2:.0f} {sag + 60:.0f} {xb} 1440' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        s.append(f"<path d='M{xa} 1440 Q{(xa + xb) / 2:.0f} {sag + 60:.0f} {xb} 1440' fill='none' stroke='{c}' stroke-width='7' stroke-linecap='round'/>")
    # grietas en el suelo por el peso (revelación)
    gk = seg(t, REVELACION, REVELACION + 0.35)
    if gk > 0:
        for gx, sg in ((300, -1), (780, 1), (140, -1), (960, 1)):
            pts = [(gx, 1632), (gx + sg * 30, 1680), (gx + sg * 5, 1730), (gx + sg * 45, 1790), (gx + sg * 20, 1850)]
            n = max(2, int(round(len(pts) * gk)))
            d = "M" + " L".join(f"{a} {b}" for a, b in pts[:n])
            s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/>")
    s.append(bascula(t))
    # chispas en la revelación
    if t > REVELACION:
        k = clamp((t - REVELACION) / 1.4)
        for i in range(14):
            a = i * 2 * math.pi / 14 + 0.3
            d = lerp(150, 420, ease(k))
            px = 540 + d * math.cos(a); py = 1745 + d * math.sin(a) * 0.7
            op = 1 - k
            s.append(f"<path d='M{px:.0f} {py - 16:.0f} L{px + 6:.0f} {py:.0f} L{px:.0f} {py + 16:.0f} L{px - 6:.0f} {py:.0f} Z' fill='#ffd23f' stroke='{INK}' stroke-width='4' opacity='{op:.2f}'/>")
    s.append(movil(t))
    s.append("</g></g>")
    # motas de polvo flotando en la luz
    for px, py, pr, sp in MOTAS:
        yy = (py - t * sp) % 950 + 1000
        s.append(f"<circle cx='{px + 15 * math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#ffffff' opacity='0.35'/>")
    s.append("</svg>")
    return "".join(s)
