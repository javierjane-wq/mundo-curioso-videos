"""La campana del Zar: la más grande del mundo (unas 202 t) y nunca ha sonado.

Una campana gigante de bronce (personaje original con ojos) cae en la plaza con un golpe;
un obrero diminuto a su lado da la escala. Llega un incendio (1737), la campana se asusta y,
en la revelación, se agrieta y se le desprende un gran trozo del borde (unas 11,5 t).
Arriba: cielo tranquilo (logo y textos); abajo, la muralla lejana y la plaza empedrada.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.2   # la grieta y el trozo que se cae: golpe musical
MUSICA = 5

rng = np.random.default_rng(1737)
STARS = [(rng.uniform(0, W), rng.uniform(80, 980), rng.uniform(2.5, 5.5), rng.uniform(0, 6.28)) for _ in range(55)]
EMBERS = [(rng.uniform(40, 1040), rng.uniform(0, 1), rng.uniform(4, 9), rng.uniform(0, 6.28)) for _ in range(34)]
COBBLES = []
for fila, y in enumerate(range(1395, 1930, 46)):
    ancho = 60 + fila * 9
    off = (fila % 2) * ancho / 2
    x = -ancho + off
    while x < W + ancho:
        COBBLES.append((x + rng.uniform(-6, 6), y + rng.uniform(-4, 4), ancho * 0.42, 11 + fila * 1.6))
        x += ancho
FLAMES_BACK = [(70, 1.0, 0.0), (190, 1.25, 1.3), (900, 1.3, 0.7), (1020, 1.05, 2.1), (300, 0.8, 2.8), (790, 0.85, 1.9)]
FLAMES_FRONT = [(40, 0.6, 0.4), (1020, 0.8, 1.6)]

BX, BY = 540, 1760
BS = 0.9                   # escala de la campana          # base de la campana (centro del borde)

BELL = ("M -340 0 C -330 -40 -270 -80 -255 -200 C -240 -330 -215 -440 -205 -510 "
        "C -195 -590 -110 -615 0 -615 C 110 -615 195 -590 205 -510 C 215 -440 240 -330 255 -200 "
        "C 270 -80 330 -40 340 0 Q 0 46 -340 0 Z")
# trozo que se desprende (borde inferior derecho)
PIEZA = "M 130 21 L 162 -64 L 208 -96 L 196 -158 L 254 -196 C 266 -110 300 -55 340 0 Q 240 18 130 21 Z"
GRIETA = "M 130 21 L 162 -64 L 208 -96 L 196 -158 L 254 -196"
GRIETA2 = "M 196 -158 L 170 -230 L 186 -290"


def cielo(t, fuego, noche):
    top = mix(mix("#3f7fc6", "#6a2a3c", fuego), "#141c3f", noche)
    mid = mix(mix("#7fb7e6", "#c4523a", fuego), "#2c3770", noche)
    low = mix(mix("#f4c89a", "#ff9a3c", fuego), "#4f4a86", noche)
    return (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>")


def fondo(t, fuego, noche):
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # estrellas de noche
    for sx, sy, sr, ph in STARS:
        a = noche * (0.5 + 0.5 * math.sin(t * 3 + ph))
        if a > 0.03:
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # luna
    if noche > 0.02:
        s.append(f"<g opacity='{noche:.2f}'><circle cx='965' cy='1020' r='52' fill='#fff6d8' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='985' cy='1006' r='42' fill='{mix('#6a2a3c', '#232c5a', noche)}'/></g>")
    # nubes lentas
    for i, (cx, cy, sc) in enumerate([(150, 860, 1.3), (700, 930, 1.6), (420, 720, 1.0)]):
        dx = (t * 16 * (1 + 0.4 * i)) % 1500 - 300
        col = mix(mix("#ffffff", "#ffb08a", fuego), "#5b6399", noche)
        s.append(f"<g transform='translate({cx + dx - 300:.0f},{cy}) scale({sc})' opacity='0.9'>"
                 f"<path d='M0 50 Q10 0 70 12 Q100 -36 160 2 Q220 -18 240 50 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # pájaros
    for i in range(3):
        px = (t * 70 + i * 170) % 1300 - 120
        py = 930 + 26 * i + 10 * math.sin(t * 3 + i)
        ala = 14 * math.sin(t * 12 + i)
        s.append(f"<path d='M{px - 22:.0f} {py - ala:.0f} Q{px - 10:.0f} {py - 8:.0f} {px:.0f} {py:.0f} Q{px + 10:.0f} {py - 8:.0f} {px + 22:.0f} {py - ala:.0f}' "
                 f"fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' opacity='{1 - noche:.2f}'/>")
    # colinas y muralla almenada lejana
    s.append(f"<path d='M0 1180 Q260 1110 540 1160 T1080 1140 L1080 1400 L0 1400 Z' fill='{mix(mix('#7fb36a', '#8a5a3a', fuego), '#2e3d5a', noche)}' stroke='{INK}' stroke-width='{LW}'/>")
    pared = mix(mix("#c8503c", "#a33a2a", fuego), "#5a3346", noche)
    almenas = "M0 1290 " + " ".join(f"L{x} 1290 L{x} 1255 L{x + 20} 1240 L{x + 40} 1255 L{x + 40} 1290 L{x + 70} 1290" for x in range(10, 1080, 70)) + " L1080 1290 L1080 1400 L0 1400 Z"
    s.append(f"<path d='{almenas}' fill='{pared}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for tx in (160, 920):
        s.append(f"<rect x='{tx - 40}' y='1180' width='80' height='140' fill='{pared}' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M{tx - 52} 1185 L{tx} 1110 L{tx + 52} 1185 Z' fill='{mix(mix('#3f8a5a', '#5a3a2a', fuego), '#23304a', noche)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<rect x='{tx - 12}' y='1215' width='24' height='34' rx='10' fill='{mix('#3a2418', '#ffd88a', noche)}' stroke='{INK}' stroke-width='5'/>")
    # plaza empedrada
    suelo = mix(mix("#d8c3a0", "#d79a6a", fuego), "#6f6a8a", noche)
    s.append(f"<rect x='0' y='1370' width='{W}' height='{H - 1370}' fill='{suelo}' stroke='{INK}' stroke-width='{LW}'/>")
    piedra = mix(mix("#c2a983", "#c4835a", fuego), "#5e5a7a", noche)
    for cx, cy, rx, ry in COBBLES:
        s.append(f"<ellipse cx='{cx:.0f}' cy='{cy:.0f}' rx='{rx:.0f}' ry='{ry:.0f}' fill='{piedra}' stroke='{mix('#9c8462', '#4a4664', noche)}' stroke-width='4'/>")
    return "".join(s)


def llama(x, base, h, ph, t, col1="#ff6a2a", col2="#ffd23f"):
    w = 0.45 * h
    sw = 0.12 * h * math.sin(t * 9 + ph)
    tip = (x + sw, base - h)
    p = (f"M{x - w:.0f} {base:.0f} C{x - w:.0f} {base - h * 0.45:.0f} {x - w * 0.2 + sw:.0f} {base - h * 0.6:.0f} {tip[0]:.0f} {tip[1]:.0f} "
         f"C{x + w * 0.3 + sw:.0f} {base - h * 0.6:.0f} {x + w:.0f} {base - h * 0.45:.0f} {x + w:.0f} {base:.0f} Z")
    h2 = h * 0.55; w2 = w * 0.55
    p2 = (f"M{x - w2:.0f} {base:.0f} C{x - w2:.0f} {base - h2 * 0.5:.0f} {x + sw * 0.6:.0f} {base - h2 * 0.7:.0f} {x + sw * 0.8:.0f} {base - h2:.0f} "
          f"C{x + w2 * 0.4:.0f} {base - h2 * 0.6:.0f} {x + w2:.0f} {base - h2 * 0.4:.0f} {x + w2:.0f} {base:.0f} Z")
    return (f"<path d='{p}' fill='{col1}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='{p2}' fill='{col2}'/>")


def campana(t, fuego, rev):
    # caída inicial con golpe y aplastamiento
    caida = seg(t, 0, 0.55) ** 1.6
    dy = lerp(-300, 0, caida)
    imp = clamp((t - 0.55) / 0.5)
    sq = 0.09 * math.sin(math.pi * imp) * (1 - imp) if t > 0.55 else 0
    # pequeño salto "boing" de peso a los 3 s
    hop = clamp((t - 3.0) / 0.5)
    dy -= 60 * math.sin(math.pi * hop) if 3.0 < t < 3.5 else 0
    sq += 0.06 * math.sin(math.pi * clamp((t - 3.5) / 0.35)) if 3.5 < t < 3.85 else 0
    # temblor de miedo con el fuego, sacudida en la revelación
    shake = 5 * fuego * (1 - rev) * math.sin(t * 47) + 14 * math.sin(t * 60) * clamp(1 - (t - REVELACION) / 0.5) * (t > REVELACION)
    sway = 1.5 * math.sin(t * 2.2) * (1 - fuego)
    sx, sy = 1 + sq, 1 - sq
    bronce = mix(mix("#e2a64a", "#ff9a3a", fuego * (1 - rev)), "#9a86b8", seg(t, REVELACION + 0.2, 8.6) * 0.28)
    osc = mix(mix("#b27a2e", "#c4602a", fuego * (1 - rev)), "#6a5a8a", seg(t, REVELACION + 0.2, 8.6) * 0.28)
    g = [f"<g transform='translate({BX + shake:.1f},{BY + dy:.1f}) rotate({sway:.2f}) scale({BS * sx:.3f},{BS * sy:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='22' rx='{370 * (1 + 0.25 * (dy / -300)):.0f}' ry='34' fill='#000' opacity='0.22'/>")
    # corona (asa) y bola de arriba
    g.append(f"<path d='M-80 -612 L-80 -660 Q-80 -700 -40 -700 L40 -700 Q80 -700 80 -660 L80 -612 Z' fill='{osc}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-50 -700 Q-50 -770 0 -770 Q50 -770 50 -700' fill='none' stroke='{INK}' stroke-width='30' stroke-linecap='round'/>"
             f"<path d='M-50 -700 Q-50 -770 0 -770 Q50 -770 50 -700' fill='none' stroke='{osc}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<circle cx='0' cy='-790' r='26' fill='{bronce}' stroke='{INK}' stroke-width='{LW}'/>")
    # cuerpo
    g.append(f"<path d='{BELL}' fill='{bronce}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # sombra lateral
    g.append(f"<path d='M -340 0 C -330 -40 -270 -80 -255 -200 C -240 -330 -215 -440 -205 -510 C -195 -590 -150 -606 -120 -610 "
             f"C -150 -560 -175 -440 -190 -320 C -205 -200 -240 -60 -250 12 Q -300 8 -340 0 Z' fill='{osc}' opacity='0.55'/>")
    # bandas decorativas
    for y0, half in ((-470, 213), (-440, 218), (-118, 268), (-86, 284)):
        g.append(f"<path d='M{-half} {y0} Q0 {y0 + 26} {half} {y0}' fill='none' stroke='{INK}' stroke-width='7'/>")
    for k in range(-3, 4):
        mx = k * 62
        g.append(f"<circle cx='{mx}' cy='{-455 + 13 * (1 - (k / 3.4) ** 2):.0f}' r='10' fill='{osc}' stroke='{INK}' stroke-width='4'/>")
    for k in range(-4, 5):
        mx = k * 58
        g.append(f"<path d='M{mx - 14} {-102 + 14 * (1 - (k / 4.6) ** 2):.0f} l14 -14 l14 14 l-14 14 Z' fill='{osc}' stroke='{INK}' stroke-width='4'/>")
    # brillo que recorre el bronce
    gx = -200 + ((t * 0.45) % 1.0) * 420
    g.append(f"<path d='M{gx - 30:.0f} -560 Q{gx - 40:.0f} -350 {gx - 70:.0f} -160' fill='none' stroke='#fff3c8' stroke-width='16' stroke-linecap='round' opacity='0.55'/>")
    g.append(f"<path d='M-150 -520 Q-165 -420 -175 -330' fill='none' stroke='#fff7dc' stroke-width='12' stroke-linecap='round' opacity='0.7'/>")
    # cara
    blink = 0.12 if (0.5 < t and (t % 2.9) < 0.12) or (2.3 < t < 2.42) else 1.0
    miedo = fuego * (1 - rev)
    sorpresa = seg(t, REVELACION, REVELACION + 0.2)
    eh = 56 * (1 + 0.25 * miedo + 0.3 * sorpresa)
    mirar = lerp(0, -10, miedo) if t < REVELACION else lerp(0, 18, seg(t, REVELACION + 0.4, 8.4))
    mirar_y = 0 if t < REVELACION else lerp(0, 14, seg(t, REVELACION + 0.4, 8.4))
    for ex in (-95, 95):
        g.append(f"<ellipse cx='{ex}' cy='-330' rx='50' ry='{eh:.0f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<g transform='translate({ex + mirar:.1f},{-325 + mirar_y:.1f}) scale(1,{blink})'><circle r='26' fill='#2a1a14'/>"
                 f"<circle cx='-9' cy='-10' r='9' fill='#fff'/></g>")
        # cejas: tranquilas -> preocupadas
        inc = 18 * miedo + 10 * sorpresa
        ey = -330 - eh - 20
        dirc = 1 if ex < 0 else -1
        g.append(f"<path d='M{ex - 40} {ey + inc * dirc * -0.5:.0f} Q{ex} {ey - 14:.0f} {ex + 40} {ey + inc * dirc * 0.5:.0f}' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    # mejillas
    g.append(f"<ellipse cx='-165' cy='-250' rx='32' ry='18' fill='#ff7a6a' opacity='{0.55 * (1 - miedo):.2f}'/>")
    g.append(f"<ellipse cx='165' cy='-250' rx='32' ry='18' fill='#ff7a6a' opacity='{0.55 * (1 - miedo):.2f}'/>")
    # boca: sonrisa -> ondulada de miedo -> "O" de sorpresa
    if t >= REVELACION:
        r = lerp(18, 34, sorpresa)
        g.append(f"<ellipse cx='0' cy='-225' rx='{r * 0.8:.0f}' ry='{r:.0f}' fill='#5a1a1a' stroke='{INK}' stroke-width='7'/>")
    elif miedo > 0.3:
        w = 3 * math.sin(t * 30)
        g.append(f"<path d='M-55 -225 q14 {-14 + w:.0f} 27 0 t27 0 t27 0 t27 0' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    else:
        g.append(f"<path d='M-60 -240 Q0 -180 60 -240 Z' fill='#5a1a1a' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>"
                 f"<path d='M-30 -212 Q0 -196 30 -212' fill='#ff7a7a'/>")
    # gotas de sudor con el fuego
    if miedo > 0.2:
        for k, (dx0, ph) in enumerate(((-250, 0.0), (240, 0.45))):
            f = (t * 1.4 + ph) % 1.0
            yy = -470 + f * 160
            g.append(f"<path d='M{dx0} {yy - 26:.0f} Q{dx0 + 16} {yy:.0f} {dx0} {yy + 10:.0f} Q{dx0 - 16} {yy:.0f} {dx0} {yy - 26:.0f} Z' "
                     f"fill='#bfe8ff' stroke='{INK}' stroke-width='5' opacity='{miedo * (1 - f):.2f}'/>")
    # grieta y trozo que se cae
    if t >= REVELACION:
        g.append(f"<path d='{PIEZA}' fill='#3a2214' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<path d='{GRIETA2}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    elif t > 6.6:
        k = seg(t, 6.6, REVELACION)
        g.append(f"<path d='{GRIETA}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' stroke-dasharray='{400 * k:.0f} 600'/>")
    g.append("</g>")
    return "".join(g)


def pieza_cayendo(t):
    """El trozo de bronce que se desprende y cae rodando junto a la campana."""
    if t < REVELACION:
        return ""
    k = seg(t, REVELACION, REVELACION + 0.55)
    bote = clamp((t - REVELACION - 0.55) / 0.35)
    x = lerp(0, 40, k)
    y = lerp(0, 60, k ** 2) - 30 * math.sin(math.pi * bote) * (t < REVELACION + 0.9)
    rot = lerp(0, 24, k)
    col = mix("#e2a64a", "#9a86b8", seg(t, REVELACION + 0.2, 8.6) * 0.28)
    return (f"<g transform='translate({BX + x:.0f},{BY + y:.0f}) scale({BS}) rotate({rot:.1f},240,-60)'>"
            f"<path d='{PIEZA}' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M215 -10 Q260 -60 268 -150' fill='none' stroke='#fff3c8' stroke-width='10' stroke-linecap='round' opacity='0.6'/></g>")


def obrero(t, fuego, rev):
    """Obrero diminuto (da la escala): entra caminando, saluda y se asusta."""
    x = lerp(-120, 175, seg(t, 0, 2.3))
    paso = math.sin(t * 14) if t < 2.3 else 0
    # salta con el temblor de 3,5 s y con la revelación
    j = 0
    if 3.45 < t < 3.85: j = 45 * math.sin(math.pi * (t - 3.45) / 0.4)
    if 0.55 < t < 0.95: j = 30 * math.sin(math.pi * (t - 0.55) / 0.4)
    if REVELACION < t < REVELACION + 0.5: j = 70 * math.sin(math.pi * (t - REVELACION) / 0.5)
    # con el fuego se aparta un poco
    x += 25 * seg(t, 5.0, 6.0)
    y = 1800 - j
    tiemblo = 3 * math.sin(t * 40) * fuego * (1 - rev)
    saludo = 40 * math.sin(t * 9) if 2.4 < t < 4.8 else 0
    brazo = -150 + saludo if 2.4 < t < 4.8 else (-170 if fuego > 0.3 or t > REVELACION else -20)
    blink = 0.15 if (t % 2.3) < 0.12 else 1
    g = [f"<g transform='translate({x + tiemblo:.0f},{y:.0f}) scale(0.92)'>"]
    g.append(f"<ellipse cx='0' cy='{8 + j:.0f}' rx='50' ry='10' fill='#000' opacity='0.22'/>")
    # piernas
    for s_, ph in ((-1, 0), (1, math.pi)):
        a = 22 * math.sin(t * 14 + ph) if t < 2.3 else 0
        g.append(f"<g transform='rotate({a:.1f},{s_ * 14},-70)'><rect x='{s_ * 14 - 11}' y='-74' width='22' height='72' rx='9' fill='#3a5a9a' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='{s_ * 14 + 6}' cy='-2' rx='18' ry='9' fill='#4a2e1e' stroke='{INK}' stroke-width='5'/></g>")
    # cuerpo
    g.append(f"<rect x='-38' y='-150' width='76' height='88' rx='24' fill='#4f7bd1' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='-24' y='-140' width='48' height='30' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    # brazos (izquierdo quieto, derecho saluda / se tapa)
    g.append(f"<g transform='rotate(18,-34,-136)'><rect x='-46' y='-140' width='20' height='64' rx='10' fill='#4f7bd1' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='-36' cy='-74' r='12' fill='#f5c29a' stroke='{INK}' stroke-width='5'/></g>")
    g.append(f"<g transform='rotate({brazo:.1f},34,-136)'><rect x='26' y='-140' width='20' height='64' rx='10' fill='#4f7bd1' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='36' cy='-74' r='12' fill='#f5c29a' stroke='{INK}' stroke-width='5'/></g>")
    # cabeza con gorra
    g.append(f"<circle cx='0' cy='-196' r='44' fill='#f5c29a' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M-46 -206 Q-44 -252 0 -252 Q44 -252 46 -206 Z' fill='#e2483c' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M-50 -206 L-80 -200' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    for ex in (-16, 16):
        g.append(f"<g transform='translate({ex - 6},-192) scale(1,{blink})'><circle r='6' fill='{INK}'/></g>")
    if fuego > 0.3 or t > REVELACION:
        g.append(f"<ellipse cx='-4' cy='-170' rx='8' ry='10' fill='#5a1a1a' stroke='{INK}' stroke-width='4'/>")
    else:
        g.append(f"<path d='M-18 -174 Q-6 -160 8 -174' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def polvo(t, a, cx, cy, n=9, fuerza=1.0, col="#f0e2c8"):
    k = clamp((t - a) / 0.9)
    if t < a or k >= 1:
        return ""
    s = []
    for i in range(n):
        lado = -1 if i % 2 else 1
        j = i // 2
        d = (250 + 40 * j) * fuerza + 220 * fuerza * ease(k) * (1 + 0.25 * j)
        px = cx + lado * d
        py = cy - 10 - 26 * j * fuerza - 50 * ease(k) * fuerza
        r = (34 + 10 * (j % 3)) * fuerza * (1 + 0.6 * k)
        s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{r:.0f}' fill='{col}' stroke='{INK}' stroke-width='5' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def frame(t):
    fuego = seg(t, 4.9, 5.7) * (1 - seg(t, REVELACION, REVELACION + 0.45))
    noche = seg(t, REVELACION, REVELACION + 0.9)
    rev = seg(t, REVELACION, REVELACION + 0.3)
    defs = (cielo(t, seg(t, 4.9, 5.7) * (1 - noche), noche)
            + f"<radialGradient id='glow'><stop offset='0' stop-color='#ffd060' stop-opacity='{0.75 * fuego:.3f}'/>"
              f"<stop offset='1' stop-color='#ff5a20' stop-opacity='0'/></radialGradient>"
            + "<radialGradient id='luz'><stop offset='0' stop-color='#fff7d6' stop-opacity='0.9'/><stop offset='1' stop-color='#fff7d6' stop-opacity='0'/></radialGradient>")
    # temblor de cámara al caer la campana
    cam = 10 * math.sin(t * 70) * clamp(1 - (t - 0.55) / 0.35) * (t > 0.55)
    s = [f"<g transform='translate(0,{cam:.1f})'>", fondo(t, seg(t, 4.9, 5.7) * (1 - noche), noche)]
    z = 1 + 0.16 * seg(t, REVELACION, 8.2)
    escena = []
    # resplandor y llamas de detrás
    if fuego > 0.01:
        escena.append(f"<ellipse cx='540' cy='1450' rx='700' ry='520' fill='url(#glow)'/>")
        for x, sc, ph in FLAMES_BACK:
            escena.append(llama(x, 1520, 360 * sc * fuego * (0.85 + 0.15 * math.sin(t * 6 + ph)), ph, t))
    # humo que queda tras el fuego
    if t > REVELACION:
        hk = seg(t, REVELACION, 9.8)
        for i, x in enumerate((90, 230, 860, 1000)):
            yy = 1440 - 260 * hk - 30 * i % 60
            escena.append(f"<circle cx='{x + 30 * math.sin(t * 2 + i):.0f}' cy='{yy:.0f}' r='{40 + 40 * hk:.0f}' fill='#8a86a8' opacity='{0.45 * (1 - hk):.2f}'/>")
    escena.append(campana(t, fuego, rev))
    escena.append(pieza_cayendo(t))
    escena.append(obrero(t, fuego, rev))
    # llamas de delante (pequeñas, a los lados)
    if fuego > 0.01:
        for x, sc, ph in FLAMES_FRONT:
            escena.append(llama(x, 1880, 300 * sc * fuego, ph, t))
    # chispas
    if fuego > 0.01:
        for ex, f0, r, ph in EMBERS:
            f = (t * 0.6 + f0) % 1.0
            yy = 1700 - f * 650
            escena.append(f"<circle cx='{ex + 25 * math.sin(t * 3 + ph):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#ffd23f' opacity='{fuego * (1 - f):.2f}'/>")
    # polvo al caer la campana y al caerse el trozo
    escena.append(polvo(t, 0.55, BX, BY + 10, n=11, fuerza=1.0))
    escena.append(polvo(t, REVELACION + 0.5, BX + 150, BY + 30, n=6, fuerza=0.5, col="#d9d2e8"))
    s.append(zoom(640, 1300, z, "".join(escena)))
    s.append("</g>")
    # destello en la revelación
    fl = clamp(1 - (t - REVELACION) / 0.45) if t >= REVELACION else 0
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe8' opacity='{0.75 * fl:.2f}'/>")
    return svg_doc("".join(s), defs)


def svg_doc(cuerpo, defs):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs><rect width='{W}' height='{H}' fill='#3f7fc6'/>{cuerpo}</svg>")
