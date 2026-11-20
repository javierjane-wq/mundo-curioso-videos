"""2026-11-20-c2 · Química cotidiana: el hielo seco (CO2 sólido, -78,5 °C) no se derrite: pasa de sólido a gas.

Una encimera de cocina con dos cubitos con cara: uno de hielo normal (azul transparente) y un bloque de
hielo seco (blanco escarchado) del que cae niebla. Un termómetro de pared baja hasta el azul. El hielo
normal se derrite y deja un charco; el hielo seco encoge sin dejar ni una gota y en la REVELACION
estalla en una gran nube de niebla con luz fría y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 7.0    # el hielo seco estalla en niebla: golpe musical
MUSICA = 2

rng = np.random.default_rng(20)
BOKEH = [(rng.uniform(0, W), rng.uniform(80, 980), rng.uniform(40, 110), rng.uniform(0, 6.28)) for _ in range(9)]
SPECK = [(rng.uniform(0.08, 0.92), rng.uniform(0.1, 0.9), rng.uniform(3, 7)) for _ in range(26)]
FOG = [(i * 0.17, rng.choice([-1, 1]), rng.uniform(0.7, 1.3)) for i in range(40)]
BURST = [(rng.uniform(-1.0, 1.0), rng.uniform(0.6, 1.0), rng.uniform(80, 150), rng.uniform(0, 0.35)) for _ in range(18)]
SPARK = [(rng.uniform(-200, 200), rng.uniform(-30, 20), rng.uniform(0, 6.28)) for _ in range(8)]

MESA = 1440   # borde superior de la encimera


def cara(cx, cy, s, t, humor, fase=0.0):
    """Ojos grandes que parpadean y boca. humor: 0 normal, 1 preocupado, 2 feliz."""
    blink = 0.12 if ((t + fase) % 3.3) < 0.13 else 1.0
    er = s * 0.12
    g = []
    for dx in (-s * 0.2, s * 0.2):
        g.append(f"<ellipse cx='{cx + dx:.1f}' cy='{cy:.1f}' rx='{er:.1f}' ry='{er * 1.15 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{cx + dx + er * 0.15:.1f}' cy='{cy + er * 0.15:.1f}' r='{er * 0.55:.1f}' fill='{INK}'/>")
            g.append(f"<circle cx='{cx + dx + er * 0.32:.1f}' cy='{cy - er * 0.15:.1f}' r='{er * 0.2:.1f}' fill='#fff'/>")
    my = cy + s * 0.22
    if humor == 1:      # preocupado: boca ondulada y cejas
        g.append(f"<path d='M{cx - s*0.12:.1f} {my:.1f} q{s*0.06:.1f} {-s*0.05:.1f} {s*0.12:.1f} 0 t{s*0.12:.1f} 0' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
        for dx, sg in ((-s * 0.2, 1), (s * 0.2, -1)):
            g.append(f"<line x1='{cx + dx - s*0.08:.1f}' y1='{cy - er*1.6 - sg*s*0.03:.1f}' x2='{cx + dx + s*0.08:.1f}' y2='{cy - er*1.6 + sg*s*0.03:.1f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    elif humor == 2:    # feliz: boca abierta
        g.append(f"<path d='M{cx - s*0.13:.1f} {my - s*0.03:.1f} Q{cx:.1f} {my + s*0.16:.1f} {cx + s*0.13:.1f} {my - s*0.03:.1f} Z' fill='#e2445c' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M{cx - s*0.1:.1f} {my:.1f} Q{cx:.1f} {my + s*0.09:.1f} {cx + s*0.1:.1f} {my:.1f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # mejillas
    for dx in (-s * 0.32, s * 0.32):
        g.append(f"<ellipse cx='{cx + dx:.1f}' cy='{my - s*0.04:.1f}' rx='{s*0.06:.1f}' ry='{s*0.035:.1f}' fill='#ff9aa8' opacity='0.6'/>")
    return "".join(g)


def cubo(cx, by, ancho, alto, front, top, side, extra=""):
    """Cubo en perspectiva sencilla: cara frontal, tapa y lateral derecho."""
    x0, x1 = cx - ancho / 2, cx + ancho / 2
    yt = by - alto
    d = ancho * 0.3; dy = d * 0.6
    g = [f"<path d='M{x1:.1f} {yt:.1f} L{x1 + d:.1f} {yt - dy:.1f} L{x1 + d:.1f} {by - dy:.1f} L{x1:.1f} {by:.1f} Z' fill='{side}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M{x0:.1f} {yt:.1f} L{x1:.1f} {yt:.1f} L{x1 + d:.1f} {yt - dy:.1f} L{x0 + d:.1f} {yt - dy:.1f} Z' fill='{top}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<rect x='{x0:.1f}' y='{yt:.1f}' width='{ancho:.1f}' height='{alto:.1f}' rx='{min(ancho, alto) * 0.08:.1f}' fill='{front}' stroke='{INK}' stroke-width='{LW}'/>",
         extra]
    return "".join(g)


def hielo_normal(t):
    """Cubito de hielo azul: entra por la izquierda, se derrite y deja un charco."""
    x = lerp(90, 280, seg(t, 0, 1.6))
    m = seg(t, 4.5, 8.6)                         # derretido
    s = 215
    alto = s * lerp(1, 0.42, m); ancho = s * lerp(1, 1.12, m)
    bob = 0 if t > 1.6 else -18 * abs(math.sin(t * 7))
    by = MESA + 40 + bob
    g = []
    # charco
    if m > 0:
        rx = lerp(60, 230, m); ry = lerp(10, 34, m)
        g.append(f"<ellipse cx='{x + 20:.1f}' cy='{by + 6:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='#8fd8ff' stroke='{INK}' stroke-width='6' opacity='0.95'/>")
        g.append(f"<ellipse cx='{x - rx*0.3:.1f}' cy='{by + 2:.1f}' rx='{rx*0.25:.1f}' ry='{ry*0.3:.1f}' fill='#e8f8ff'/>")
    else:
        g.append(f"<ellipse cx='{x + 20:.1f}' cy='{by + 8:.1f}' rx='120' ry='16' fill='#000' opacity='0.15'/>")
    brillo = (f"<path d='M{x - ancho*0.36:.1f} {by - alto*0.82:.1f} L{x - ancho*0.36:.1f} {by - alto*0.45:.1f}' stroke='#fff' stroke-width='12' stroke-linecap='round' opacity='0.85'/>"
              f"<circle cx='{x - ancho*0.36:.1f}' cy='{by - alto*0.3:.1f}' r='6' fill='#fff' opacity='0.85'/>")
    humor = 1 if m > 0.05 else 0
    g.append(cubo(x, by, ancho, alto, "#a9e4ff", "#dff6ff", "#7cc8ef",
                  brillo + cara(x, by - alto * 0.52, min(s, alto * 1.6), t, humor, 0.4)))
    # gotas que resbalan
    if 4.5 < t < 9.5:
        for i in range(3):
            k = ((t - 4.5) * 0.9 + i * 0.33) % 1
            gx = x - ancho * 0.25 + i * ancho * 0.25
            gy = by - alto * 0.9 + k * alto * 0.9
            g.append(f"<path d='M{gx:.1f} {gy - 16:.1f} Q{gx + 10:.1f} {gy:.1f} {gx:.1f} {gy + 6:.1f} Q{gx - 10:.1f} {gy:.1f} {gx:.1f} {gy - 16:.1f} Z' fill='#5bbcf2' stroke='{INK}' stroke-width='4'/>")
    # gota de sudor
    if m > 0.05:
        sy = by - alto - 30 + 10 * math.sin(t * 5)
        g.append(f"<path d='M{x + ancho*0.55:.1f} {sy - 22:.1f} Q{x + ancho*0.55 + 14:.1f} {sy:.1f} {x + ancho*0.55:.1f} {sy + 8:.1f} Q{x + ancho*0.55 - 14:.1f} {sy:.1f} {x + ancho*0.55:.1f} {sy - 22:.1f} Z' fill='#8fd8ff' stroke='{INK}' stroke-width='5'/>")
    return "".join(g)


def niebla_baja(t, cx, by, ancho, fuerza):
    """Hilos de niebla que caen del hielo seco y se arrastran por la encimera (el CO2 frío baja)."""
    g = []
    for b, lado, v in FOG:
        a = (t - b) % 2.6
        if t < b * 0.2: continue
        k = a / 2.6
        x = cx + lado * (ancho * 0.45 + k * 260 * v)
        y = by - 30 - 60 * (1 - k) + 25 * k
        r = lerp(18, 70, k) * v
        op = fuerza * 0.75 * math.sin(math.pi * k)
        if op > 0.02:
            g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='#ffffff' stroke='#b9cde3' stroke-width='5' opacity='{op:.2f}'/>")
    return "".join(g)


def hielo_seco(t):
    """Bloque de hielo seco: blanco escarchado con motas, entra por la derecha, encoge sin charco."""
    x = lerp(960, 720, seg(t, 0, 1.9))
    enc = lerp(1, 0.85, seg(t, 4.6, 8.4))
    s = 290 * enc
    bob = 0 if t > 1.9 else -16 * abs(math.sin(t * 7 + 1))
    by = MESA + 60 + bob
    tiembla = 4 * math.sin(t * 40) * seg(t, 6.2, 7.0) * (1 - seg(t, 7.0, 7.3))
    x += tiembla
    g = [f"<ellipse cx='{x + 30:.1f}' cy='{by + 8:.1f}' rx='{s*0.7:.1f}' ry='18' fill='#000' opacity='0.15'/>"]
    motas = "".join(f"<circle cx='{x - s/2 + fx*s:.1f}' cy='{by - s + fy*s:.1f}' r='{r * enc:.1f}' fill='#c8d6e8'/>" for fx, fy, r in SPECK)
    brillo = f"<path d='M{x - s*0.36:.1f} {by - s*0.85:.1f} L{x - s*0.2:.1f} {by - s*0.85:.1f}' stroke='#fff' stroke-width='12' stroke-linecap='round'/>"
    humor = 2 if t > REVELACION else 0
    g.append(cubo(x, by, s, s, "#eef3f9", "#ffffff", "#c9d5e4", motas + brillo + cara(x, by - s * 0.5, s, t, humor, 1.2)))
    return x, by, s, "".join(g)


def termometro(t):
    """Termómetro de pared (sin números): el líquido baja del rojo al azul."""
    x, y0, y1 = 975, 1060, 1360
    k = seg(t, 2.3, 4.4)
    nivel = lerp(y0 + 60, y1 - 40, k)
    col = mix("#ff4d4d", "#3d8fe0", k)
    g = [f"<rect x='{x - 34}' y='{y0 - 20}' width='68' height='{y1 - y0 + 70}' rx='34' fill='#fff7e8' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='{x - 11}' y='{y0}' width='22' height='{y1 - y0}' rx='11' fill='#e8eef5' stroke='{INK}' stroke-width='5'/>",
         f"<rect x='{x - 7}' y='{nivel:.1f}' width='14' height='{y1 - nivel:.1f}' fill='{col}'/>",
         f"<circle cx='{x}' cy='{y1 + 12}' r='24' fill='{col}' stroke='{INK}' stroke-width='6'/>"]
    for i in range(7):
        yy = y0 + 20 + i * 42
        g.append(f"<line x1='{x + 13}' y1='{yy}' x2='{x + 25}' y2='{yy}' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    if k > 0.6:   # copos de frío alrededor
        for i, (dx, dy) in enumerate(((-60, 1120), (55, 1200), (-55, 1290))):
            a = (k - 0.6) / 0.4 * (0.6 + 0.4 * math.sin(t * 5 + i))
            rot = t * 40 + i * 30
            g.append(f"<g transform='translate({x + dx},{dy}) rotate({rot:.0f})' opacity='{a:.2f}'>"
                     + "".join(f"<line x1='0' y1='0' x2='0' y2='-16' stroke='#3d8fe0' stroke-width='5' stroke-linecap='round' transform='rotate({r})'/>" for r in range(0, 360, 60))
                     + "</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.8)
    frio = seg(t, 2.3, 4.4) * 0.35 + rev * 0.65
    pared_a = mix("#ffe3c2", "#cfe9ff", frio); pared_b = mix("#ffd0a6", "#a9d6f7", frio)
    defs = (f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{pared_a}'/><stop offset='1' stop-color='{pared_b}'/></linearGradient>"
            f"<radialGradient id='luz'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.9*rev:.3f}'/><stop offset='0.4' stop-color='#bfe6ff' stop-opacity='{0.7*rev:.3f}'/><stop offset='1' stop-color='#dff1ff' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # bokeh suave en la pared (fondo tranquilo arriba)
    for bx, by, br, ph in BOKEH:
        yy = by + 18 * math.sin(t * 0.6 + ph)
        s.append(f"<circle cx='{bx:.0f}' cy='{yy:.0f}' r='{br:.0f}' fill='#ffffff' opacity='{0.13 + 0.05*math.sin(t + ph):.2f}'/>")
    # azulejos de la cocina (solo abajo)
    azul = mix("#fff4e4", "#e6f4ff", frio); junta = mix("#f0cfa8", "#a8c8e6", frio)
    s.append(f"<rect x='0' y='1030' width='{W}' height='{MESA - 1030}' fill='{azul}'/>")
    for yy in range(1030, MESA, 82):
        s.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='{junta}' stroke-width='5'/>")
    for i, yy in enumerate(range(1030, MESA, 82)):
        off = 0 if i % 2 == 0 else 60
        for xx in range(off, W + 120, 120):
            s.append(f"<line x1='{xx}' y1='{yy}' x2='{xx}' y2='{min(yy + 82, MESA)}' stroke='{junta}' stroke-width='5'/>")
    s.append(f"<line x1='0' y1='1030' x2='{W}' y2='1030' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(termometro(t))
    esc = []
    # encimera de madera
    esc.append(f"<rect x='-20' y='{MESA}' width='{W + 40}' height='70' fill='#d98c4a' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(f"<rect x='-20' y='{MESA + 70}' width='{W + 40}' height='{H - MESA - 70}' fill='#b9693a' stroke='{INK}' stroke-width='{LW}'/>")
    for xx in (60, 600):
        esc.append(f"<rect x='{xx}' y='{MESA + 130}' width='420' height='240' rx='18' fill='#c97a45' stroke='{INK}' stroke-width='7'/>")
        esc.append(f"<rect x='{xx + 170}' y='{MESA + 160}' width='80' height='18' rx='9' fill='#f3d27a' stroke='{INK}' stroke-width='5'/>")
    for xx in range(40, W, 170):
        esc.append(f"<path d='M{xx} {MESA + 22} q40 -8 80 0' fill='none' stroke='#b86e35' stroke-width='5' stroke-linecap='round'/>")
    # protagonistas
    esc.append(hielo_normal(t))
    hx, hby, hs, bloque = hielo_seco(t)
    esc.append(f"<circle cx='{hx:.1f}' cy='{hby - hs*0.5:.1f}' r='{lerp(150, 520, rev):.1f}' fill='url(#luz)'/>")
    # estallido de niebla detrás del bloque
    nube = []
    for dx, dy, r, d in BURST:
        k = seg(t, REVELACION + d * 0.6, REVELACION + 0.7 + d)
        if k <= 0: continue
        px = hx + dx * 380 * k
        py = hby - hs * 0.4 - dy * 300 * k + 40 * (1 - abs(dx))
        rr = r * (0.3 + 0.7 * k) * (1 + 0.05 * math.sin(t * 3 + dx * 5))
        op = 0.92 - 0.25 * seg(t, 8.6, 10)
        nube.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='{rr:.1f}' fill='#ffffff' stroke='#a9c3df' stroke-width='6' opacity='{op:.2f}'/>")
    esc.append("".join(nube))
    fuerza = 0.5 + 0.5 * seg(t, 1.0, 2.5) + 0.4 * rev
    esc.append(niebla_baja(t, hx, hby, hs, fuerza * 0.6))
    esc.append(bloque)
    esc.append(niebla_baja(t + 1.3, hx, hby + 20, hs, fuerza))
    # destellos de escarcha (encimera seca bajo el hielo seco)
    for sx, sy, ph in SPARK:
        a = (0.5 + 0.5 * math.sin(t * 4 + ph)) * (0.4 + 0.6 * rev)
        cx, cy = hx + sx, hby + 18 + sy * 0.3
        esc.append(f"<path d='M{cx:.1f} {cy - 14:.1f} L{cx + 4:.1f} {cy - 4:.1f} L{cx + 14:.1f} {cy:.1f} L{cx + 4:.1f} {cy + 4:.1f} L{cx:.1f} {cy + 14:.1f} L{cx - 4:.1f} {cy + 4:.1f} L{cx - 14:.1f} {cy:.1f} L{cx - 4:.1f} {cy - 4:.1f} Z' fill='#ffffff' opacity='{a:.2f}'/>")
    z = 1 + 0.28 * seg(t, REVELACION, REVELACION + 1.0) + 0.05 * seg(t, 8.0, 10)
    s.append(zoom(hx, hby - hs * 0.5, z, "".join(esc)))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
