"""El primer semáforo (Londres, 1868) funcionaba con gas y explotó en menos de un mes.

Composición: protagonista (semáforo victoriano original: columna verde con bandas doradas, cabeza
con cara, dos brazos rojos de señal y farol de gas encima) sobre una acera adoquinada, con un
policía que lo maneja con una palanca; un coche de caballos cruza la calle. Arriba, cielo tranquilo
de atardecer que se vuelve noche, con luna y estrellas; casas victorianas y una torre al fondo.
Movimiento: el coche de caballos cruza desde el fotograma 0, los brazos suben y bajan, parpadeos,
nubes; al anochecer el farol de gas se enciende (rojo / verde); luego hay fugas de gas (humo), el
farol parpadea y el semáforo tiembla; en la REVELACION estalla: destello, explosión naranja,
trozos volando, cielo iluminado, casco del policía por los aires, humo y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.3   # explota el farol de gas: golpe musical
MUSICA = 2

rng = np.random.default_rng(18113)
STARS = [(rng.uniform(0, W), rng.uniform(60, 1000), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(55)]
COBBLES = [(x + (rng.uniform(-8, 8)), y, rng.uniform(26, 38)) for y in range(1765, 1930, 44)
           for x in range(-20, 1110, 76)]
DEBRIS = [(a, rng.uniform(520, 980), rng.uniform(-400, 400), rng.choice(["#d8322a", "#f6e7a8", "#2e6e4a", "#c9a34a"]),
           rng.uniform(14, 26)) for a in np.linspace(0, 2 * math.pi, 13)[:-1]]
SMOKE = [(rng.uniform(-170, 170), rng.uniform(-120, 60), rng.uniform(60, 110), rng.uniform(0, 6.28)) for _ in range(12)]
SPARKS = [(rng.uniform(0, 2 * math.pi), rng.uniform(250, 700), rng.uniform(0, 1)) for _ in range(26)]
BUILD = [(-10, 1240, 200, "#7d6a8c"), (190, 1180, 170, "#8a6f6a"), (360, 1300, 150, "#6d7a96"),
         (790, 1220, 160, "#8a6f6a"), (950, 1150, 150, "#7d6a8c")]

LX, LY = 640, 1122          # centro del farol de gas (punto de la explosión)
BOOM = REVELACION


def cielo(t, noche, fuego):
    top = mix(mix("#5b6fb5", "#141a3e", noche), "#7a2a1e", 0.55 * fuego)
    mid = mix(mix("#c98fb0", "#2c2a5e", noche), "#d8652a", 0.6 * fuego)
    low = mix(mix("#ffc07a", "#5a3a6a", noche), "#ffb347", 0.7 * fuego)
    return (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>")


def fondo(t, noche, fuego):
    s = []
    # estrellas y luna
    for sx, sy, sr, ph in STARS:
        a = noche * (0.5 + 0.5 * math.sin(t * 3 + ph))
        if a > 0.03:
            s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    my = lerp(900, 760, seg(t, 0, 6))
    s.append(f"<circle cx='880' cy='{my:.0f}' r='58' fill='#fff6d8' stroke='{INK}' stroke-width='6' opacity='{0.35 + 0.65 * noche:.2f}'/>")
    s.append(f"<circle cx='862' cy='{my - 12:.0f}' r='10' fill='#efe2b8' opacity='{0.35 + 0.65 * noche:.2f}'/>")
    # nubes lejanas
    for i, (cy, sc, v) in enumerate(((860, 1.3, 16), (980, 1.0, 24))):
        dx = (t * v + i * 520) % 1500 - 300
        col = mix(mix("#f6d3c8", "#4a4a7a", noche), "#ffb070", fuego)
        s.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})' opacity='0.85'>"
                 f"<path d='M0 40 Q20 -8 80 6 Q112 -36 170 2 Q230 -12 250 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # torre gótica al fondo (genérica)
    tc = mix(mix("#8b7f9e", "#2b2c52", noche), "#a0553a", 0.5 * fuego)
    s.append(f"<path d='M70 1610 L70 1110 L100 1080 L130 1110 L130 1610 Z' fill='{tc}' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<path d='M58 1110 L100 1000 L142 1110 Z' fill='{mix(tc, '#000000', 0.2)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    s.append(f"<circle cx='100' cy='1160' r='22' fill='{mix('#f3e9c8', '#ffe28a', noche)}' stroke='{INK}' stroke-width='5'/>")
    ang = t * 40
    s.append(f"<line x1='100' y1='1160' x2='{100 + 14 * math.sin(math.radians(ang)):.1f}' y2='{1160 - 14 * math.cos(math.radians(ang)):.1f}' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    # casas victorianas
    for bx, by, bw, col in BUILD:
        c = mix(mix(col, "#262a4e", noche * 0.8), "#a0553a", 0.45 * fuego)
        s.append(f"<rect x='{bx}' y='{by}' width='{bw}' height='{1620 - by}' fill='{c}' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<path d='M{bx - 8} {by} L{bx + bw / 2:.0f} {by - 46} L{bx + bw + 8} {by} Z' fill='{mix(c, '#000000', 0.25)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        s.append(f"<rect x='{bx + bw * 0.62:.0f}' y='{by - 70}' width='22' height='50' fill='{mix(c, '#000000', 0.15)}' stroke='{INK}' stroke-width='5'/>")
        for wy in range(by + 30, 1560, 95):
            for wx in (bx + bw * 0.18, bx + bw * 0.58):
                lit = noche * (0.6 + 0.4 * math.sin(wx * 0.37 + wy))
                wc = mix("#cfe0f0", "#ffd86a", clamp(lit))
                s.append(f"<rect x='{wx:.0f}' y='{wy}' width='{bw * 0.24:.0f}' height='52' rx='6' fill='{wc}' stroke='{INK}' stroke-width='5'/>")
    # acera y calle adoquinada
    s.append(f"<rect x='0' y='1600' width='{W}' height='140' fill='{mix(mix('#b8b2a6', '#5c5a6e', noche), '#c08a5a', 0.5 * fuego)}' stroke='{INK}' stroke-width='{LW}'/>")
    for x in range(0, W, 135):
        s.append(f"<line x1='{x}' y1='1604' x2='{x - 30}' y2='1736' stroke='{INK}' stroke-width='4' opacity='0.5'/>")
    s.append(f"<rect x='-10' y='1735' width='{W + 20}' height='24' fill='{mix('#8e887c', '#45434f', noche)}' stroke='{INK}' stroke-width='7'/>")
    road = mix(mix("#7a6e62", "#34303e", noche), "#8a5a3a", 0.5 * fuego)
    s.append(f"<rect x='0' y='1759' width='{W}' height='{H - 1759}' fill='{road}'/>")
    for cx, cy, r in COBBLES:
        s.append(f"<ellipse cx='{cx:.0f}' cy='{cy}' rx='{r:.0f}' ry='{r * 0.48:.0f}' fill='{mix(road, '#ffffff', 0.12)}' stroke='{INK}' stroke-width='4' opacity='0.8'/>")
    return "".join(s)


def caballo(t, x):
    """Coche de caballos (caballo de perfil mirando a la derecha y carruaje de dos ruedas)."""
    paso = t * 9
    y = 1900 + 4 * math.sin(paso * 2)
    g = [f"<g transform='translate({x:.1f},{y:.1f})'>"]
    g.append("<ellipse cx='-150' cy='4' rx='300' ry='20' fill='#000' opacity='0.25'/>")
    # varas del carruaje
    g.append(f"<line x1='-190' y1='-150' x2='-20' y2='-150' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    g.append(f"<line x1='-190' y1='-150' x2='-20' y2='-150' stroke='#a8743e' stroke-width='5' stroke-linecap='round'/>")
    # carruaje
    g.append(f"<path d='M-420 -110 L-420 -300 Q-420 -340 -380 -340 L-230 -340 Q-195 -340 -190 -300 L-180 -110 Z' fill='#8c2f39' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-430 -340 Q-305 -390 -180 -340 Z' fill='#3a2430' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<rect x='-385' y='-300' width='120' height='90' rx='12' fill='#f5d27a' stroke='{INK}' stroke-width='6'/>")
    g.append("<circle cx='-322' cy='-262' r='22' fill='#4a3040'/><path d='M-352 -210 Q-322 -248 -292 -210 Z' fill='#4a3040'/>")
    g.append(f"<line x1='-420' y1='-170' x2='-180' y2='-170' stroke='#e0b24a' stroke-width='6'/>")
    rot = -t * 260
    g.append(f"<g transform='translate(-300,-80) rotate({rot:.1f})'><circle r='78' fill='none' stroke='{INK}' stroke-width='22'/>"
             f"<circle r='78' fill='none' stroke='#d9a440' stroke-width='10'/>"
             + "".join(f"<line x1='0' y1='0' x2='{78 * math.cos(math.radians(a)):.1f}' y2='{78 * math.sin(math.radians(a)):.1f}' stroke='{INK}' stroke-width='6'/>" for a in range(0, 360, 36))
             + f"<circle r='14' fill='#d9a440' stroke='{INK}' stroke-width='5'/></g>")
    # caballo
    body = "#8a5634"
    legs = [(-85, 0.0), (-60, math.pi), (70, math.pi), (95, 0.0)]
    for i, (lx, ph) in enumerate(legs):
        a = 22 * math.sin(paso + ph)
        col = mix(body, "#000000", 0.25) if i in (1, 2) else body
        g.append(f"<g transform='translate({lx},-160) rotate({a:.1f})'><rect x='-11' y='0' width='22' height='150' rx='9' fill='{col}' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='-13' y='138' width='26' height='20' rx='5' fill='#2b1d18' stroke='{INK}' stroke-width='5'/></g>")
    g.append(f"<path d='M-115 -190 Q-170 -170 -165 -95 Q-150 -130 -130 -150 Z' fill='#3a2418' stroke='{INK}' stroke-width='6' stroke-linejoin='round' transform='rotate({6 * math.sin(paso):.1f},-115,-190)'/>")
    g.append(f"<ellipse cx='0' cy='-200' rx='125' ry='58' fill='{body}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M70 -225 L130 -330 L175 -318 L140 -190 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M118 -330 Q85 -280 72 -225 L90 -228 Q100 -280 130 -326 Z' fill='#3a2418' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<g transform='rotate({4 * math.sin(paso * 2):.1f},150,-320)'>"
             f"<path d='M120 -345 Q150 -365 185 -335 L232 -282 Q244 -262 222 -254 L200 -250 Q170 -260 150 -290 Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M140 -350 L148 -390 L162 -352 Z' fill='{body}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<circle cx='172' cy='-322' r='8' fill='{INK}'/><circle cx='170' cy='-325' r='3' fill='#fff'/>"
             f"<circle cx='222' cy='-268' r='4' fill='{INK}'/></g>")
    g.append(f"<path d='M-60 -250 Q0 -265 60 -250 L60 -232 Q0 -246 -60 -232 Z' fill='#5a2a1e' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def policia(t, hollin, casco_y):
    """Policía victoriano con casco alto y palanca del semáforo."""
    x, y = 838, 1722
    blink = 0.12 if ((t + 1.4) % 3.3) < 0.12 else 1.0
    mira_arriba = seg(t, 5.2, 5.8)
    susto = seg(t, 5.6, 6.0)
    g = [f"<g transform='translate({x},{y})'>"]
    g.append("<ellipse cx='0' cy='4' rx='80' ry='14' fill='#000' opacity='0.25'/>")
    # palanca (unida a la base del semáforo)
    tir = 8 * math.sin(t * 2.4) if t < BOOM else 0
    g.append(f"<line x1='-130' y1='-60' x2='{-62 + tir:.1f}' y2='-150' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<line x1='-130' y1='-60' x2='{-62 + tir:.1f}' y2='-150' stroke='#9aa3ad' stroke-width='6' stroke-linecap='round'/>")
    # piernas y cuerpo
    g.append(f"<rect x='-34' y='-110' width='28' height='110' rx='8' fill='#18213f' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='6' y='-110' width='28' height='110' rx='8' fill='#18213f' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-40' y='-8' width='38' height='14' rx='6' fill='#111' /><rect x='4' y='-8' width='38' height='14' rx='6' fill='#111'/>")
    g.append(f"<path d='M-55 -235 Q0 -255 55 -235 L62 -95 L-62 -95 Z' fill='#22305e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-60' y='-140' width='120' height='16' fill='#141a33'/>")
    for by in (-215, -185, -160):
        g.append(f"<circle cx='0' cy='{by}' r='6' fill='#e8c45a' stroke='{INK}' stroke-width='3'/>")
    # brazos: uno a la palanca, otro en la cintura
    g.append(f"<path d='M-48 -225 Q-80 -190 {-62 + tir:.1f} -152' fill='none' stroke='{INK}' stroke-width='30' stroke-linecap='round'/>"
             f"<path d='M-48 -225 Q-80 -190 {-62 + tir:.1f} -152' fill='none' stroke='#22305e' stroke-width='18' stroke-linecap='round'/>")
    g.append(f"<circle cx='{-62 + tir:.1f}' cy='-152' r='13' fill='#f1c7a0' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M48 -225 Q86 -180 50 -140' fill='none' stroke='{INK}' stroke-width='30' stroke-linecap='round'/>"
             f"<path d='M48 -225 Q86 -180 50 -140' fill='none' stroke='#22305e' stroke-width='18' stroke-linecap='round'/>")
    # cabeza
    skin = mix("#f1c7a0", "#4b4440", hollin)
    hy = -285 - 6 * mira_arriba
    g.append(f"<circle cx='0' cy='{hy:.0f}' r='44' fill='{skin}' stroke='{INK}' stroke-width='{LW}'/>")
    er = 9 + 4 * susto
    for ex in (-17, 17):
        g.append(f"<ellipse cx='{ex}' cy='{hy - 6:.0f}' rx='{er:.1f}' ry='{er * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='3'/>")
        g.append(f"<circle cx='{ex - 2 * mira_arriba:.1f}' cy='{hy - 6 - 4 * mira_arriba:.1f}' r='{4.5 * blink:.1f}' fill='{INK}'/>")
    g.append(f"<path d='M-24 {hy + 16:.0f} Q-12 {hy + 6:.0f} 0 {hy + 14:.0f} Q12 {hy + 6:.0f} 24 {hy + 16:.0f} Q12 {hy + 24:.0f} 0 {hy + 18:.0f} Q-12 {hy + 24:.0f} -24 {hy + 16:.0f} Z' fill='#5a3a26' stroke='{INK}' stroke-width='3'/>")
    if susto > 0.5:
        g.append(f"<ellipse cx='0' cy='{hy + 32:.0f}' rx='9' ry='{6 + 4 * susto:.0f}' fill='#5a1e1e' stroke='{INK}' stroke-width='3'/>")
    # casco alto (salta por los aires en la explosión)
    cy = hy - 30 + casco_y
    g.append(f"<g transform='rotate({-0.12 * casco_y:.1f},0,{cy:.0f})'>"
             f"<path d='M-44 {cy:.0f} Q-44 {cy - 110:.0f} 0 {cy - 112:.0f} Q44 {cy - 110:.0f} 44 {cy:.0f} Z' fill='#1a2347' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-52' y='{cy - 6:.0f}' width='104' height='14' rx='6' fill='#1a2347' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='0' cy='{cy - 118:.0f}' r='9' fill='#1a2347' stroke='{INK}' stroke-width='5'/>"
             f"<path d='M0 {cy - 72:.0f} L13 {cy - 52:.0f} L0 {cy - 30:.0f} L-13 {cy - 52:.0f} Z' fill='#e8c45a' stroke='{INK}' stroke-width='4'/></g>")
    g.append("</g>")
    return "".join(g)


def semaforo(t, noche, roto, hollin):
    """Semáforo victoriano original: columna verde y dorada, cabeza con cara, brazos rojos y farol de gas."""
    tension = seg(t, 5.0, BOOM)
    tiembla = (3.5 * tension * math.sin(t * 55)) if t < BOOM else 2.0 * math.sin(t * 30) * (1 - seg(t, BOOM, 8.6))
    verde = mix("#2e8a55", "#2a2a2a", 0.65 * hollin)
    oro = mix("#e3b54a", "#5a4a30", 0.6 * hollin)
    g = [f"<g transform='rotate({tiembla:.2f},640,1720)'>"]
    g.append("<ellipse cx='640' cy='1728' rx='120' ry='16' fill='#000' opacity='0.25'/>")
    # pedestal
    g.append(f"<path d='M545 1725 L575 1640 L705 1640 L735 1725 Z' fill='{verde}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='560' y='1625' width='160' height='26' rx='8' fill='{oro}' stroke='{INK}' stroke-width='6'/>")
    # columna
    g.append(f"<rect x='613' y='1262' width='54' height='370' fill='{verde}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='624' y='1280' width='10' height='330' rx='5' fill='#fff' opacity='0.18'/>")
    for by in (1330, 1460, 1570):
        g.append(f"<rect x='603' y='{by}' width='74' height='20' rx='6' fill='{oro}' stroke='{INK}' stroke-width='6'/>")
    # brazos de señal (horizontal = alto, inclinado 30° = precaución)
    if t < BOOM:
        ciclo = (t % 2.6) / 2.6
        ang = 30 * seg(ciclo, 0.1, 0.25) * (1 - seg(ciclo, 0.6, 0.75)) + (6 * math.sin(t * 40) * tension)
    else:
        k = t - BOOM
        ang = 62 + 14 * math.exp(-k * 1.5) * math.sin(k * 9)
    brazo = mix("#e0342b", "#4a2020", 0.6 * hollin)
    for lado in (-1, 1):
        px = 640 + lado * 58
        rot = ang if lado == 1 else -ang
        g.append(f"<g transform='translate({px},1205) rotate({rot:.1f})'>"
                 f"<path d='M0 -15 L{lado * 175} -18 Q{lado * 190} 0 {lado * 175} 18 L0 15 Z' fill='{brazo}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<rect x='{min(lado * 120, lado * 140)}' y='-15' width='20' height='30' fill='#fff' opacity='{0.9 - 0.6 * hollin:.2f}'/></g>")
    # cabeza con cara
    g.append(f"<rect x='578' y='1172' width='124' height='96' rx='22' fill='{verde}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='578' y='1172' width='124' height='18' rx='9' fill='{oro}' stroke='{INK}' stroke-width='6'/>")
    blink = 0.12 if ((t + 0.6) % 2.9) < 0.12 else 1.0
    susto = tension
    er = 15 + 5 * susto
    for ex in (612, 668):
        if t >= BOOM and roto:
            g.append(f"<ellipse cx='{ex}' cy='1222' rx='{er:.1f}' ry='{er * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
            s = 8 + 2 * math.sin(t * 6)
            g.append(f"<path d='M{ex - s:.1f} 1222 Q{ex} {1222 - s:.1f} {ex + s:.1f} 1222 Q{ex} {1222 + s:.1f} {ex - s * 0.4:.1f} 1222' fill='none' stroke='{INK}' stroke-width='4' opacity='{blink:.2f}'/>")
        else:
            g.append(f"<ellipse cx='{ex}' cy='1222' rx='{er:.1f}' ry='{er * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
            look = 4 * math.sin(t * 1.3) * (1 - susto)
            g.append(f"<circle cx='{ex + look:.1f}' cy='{1224 - 4 * susto:.1f}' r='{(8 - 2 * susto) * blink:.1f}' fill='{INK}'/>")
    if t < 5.0:
        g.append(f"<path d='M622 1248 Q640 1260 658 1248' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='640' cy='1252' rx='{9 + 3 * susto:.1f}' ry='{6 + 4 * susto:.1f}' fill='#5a1e1e' stroke='{INK}' stroke-width='4'/>")
    if hollin > 0.1:
        for hx, hy, hr in ((596, 1240, 12), (690, 1196, 10), (650, 1182, 8)):
            g.append(f"<circle cx='{hx}' cy='{hy}' r='{hr}' fill='#222' opacity='{0.7 * hollin:.2f}'/>")
    # cuello del farol
    g.append(f"<rect x='626' y='1150' width='28' height='24' fill='{oro}' stroke='{INK}' stroke-width='6'/>")
    # farol de gas
    if t < BOOM:
        enc = seg(t, 2.8, 3.3)
        rojo = (int(t / 0.9) % 2 == 0)
        parp = 1.0 if t < 5.3 else (0.35 + 0.65 * (math.sin(t * 37) > -0.2))
        luz = "#ff4b3e" if rojo else "#4ff08a"
        vid = mix("#efe7c8", luz, enc * parp)
        if enc > 0:
            g.append(f"<circle cx='{LX}' cy='{LY}' r='{110 + 8 * math.sin(t * 8):.0f}' fill='url(#glow)' opacity='{enc * parp:.2f}'/>")
        g.append(f"<path d='M604 1150 L594 1092 L686 1092 L676 1150 Z' fill='{vid}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<line x1='640' y1='1094' x2='640' y2='1148' stroke='{INK}' stroke-width='5'/>")
        g.append(f"<path d='M606 1100 L612 1142' stroke='#fff' stroke-width='6' stroke-linecap='round' opacity='0.6'/>")
        g.append(f"<path d='M582 1094 L640 1052 L698 1094 Z' fill='{oro}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<circle cx='640' cy='1044' r='11' fill='{oro}' stroke='{INK}' stroke-width='6'/>")
    else:
        # farol reventado: marco negro y cristal roto
        g.append(f"<path d='M604 1150 L596 1110 L612 1124 L626 1098 L640 1116 L656 1096 L668 1120 L686 1106 L676 1150 Z' fill='#2b2420' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        llama = 0.6 + 0.4 * math.sin(t * 25)
        g.append(f"<path d='M628 1146 Q622 {1120 - 10 * llama:.0f} 640 {1100 - 14 * llama:.0f} Q658 {1120 - 10 * llama:.0f} 652 1146 Z' fill='#ff9a2a' stroke='{INK}' stroke-width='4' opacity='{1 - seg(t, 8.3, 9.6):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def fugas(t):
    """Humo de gas escapando del farol y de la columna antes de la explosión."""
    k = seg(t, 5.0, BOOM)
    if k <= 0 or t >= BOOM:
        return ""
    s = []
    for i in range(9):
        ph = (t * 1.6 + i / 9) % 1
        if ph > k + 0.2:
            continue
        ox = (640 + (i % 3 - 1) * 46) + 40 * math.sin(i * 2.3 + t * 2)
        oy = (1120 if i % 2 else 1300) - ph * 160
        s.append(f"<circle cx='{ox:.0f}' cy='{oy:.0f}' r='{10 + 26 * ph:.0f}' fill='#cfd6c8' stroke='{INK}' stroke-width='4' opacity='{0.75 * (1 - ph) * k:.2f}'/>")
    return "".join(s)


def explosion(t):
    if t < BOOM:
        return ""
    k = t - BOOM
    s = []
    crece = ease(clamp(k / 0.28))
    apaga = 1 - seg(t, BOOM + 0.45, 8.1)
    if apaga > 0:
        for R, col, f in ((300, "#ff5a1f", 1.0), (220, "#ffb02a", 0.8), (130, "#fff3b0", 0.6)):
            r = R * crece * (1 + 0.05 * math.sin(t * 40))
            pts = []
            for j in range(28):
                a = j * math.pi / 14 + k * 0.6
                rr = r if j % 2 == 0 else r * 0.62
                pts.append(f"{LX + rr * math.cos(a):.1f},{LY + rr * math.sin(a):.1f}")
            s.append(f"<polygon points='{' '.join(pts)}' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round' opacity='{apaga:.2f}'/>")
    # humo que se expande y sube
    hum = seg(t, BOOM + 0.15, BOOM + 0.8) * (1 - 0.5 * seg(t, 8.5, 10))
    for sx, sy, sr, ph in SMOKE:
        yy = LY + 40 + sy * 0.6 - 15 * (t - BOOM)
        rr = min(sr * (0.4 + 0.6 * seg(t, BOOM + 0.1, BOOM + 1.5)), yy - 975)
        xx = LX + sx * (0.5 + 0.7 * seg(t, BOOM, BOOM + 1.5)) + 10 * math.sin(t * 1.5 + ph)
        if hum > 0.02 and rr > 12:
            s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{rr:.0f}' fill='#6e6872' stroke='{INK}' stroke-width='6' opacity='{0.8 * hum:.2f}'/>")
            s.append(f"<circle cx='{xx - rr * 0.3:.0f}' cy='{yy - rr * 0.3:.0f}' r='{rr * 0.35:.0f}' fill='#9a94a0' opacity='{0.7 * hum:.2f}'/>")
    # trozos volando con gravedad
    for a, v, spin, col, sz in DEBRIS:
        x = LX + math.cos(a) * v * k
        y = LY + math.sin(a) * v * k - 300 * k + 900 * k * k
        if y < 1880 and y > 760:
            s.append(f"<rect x='{-sz / 2:.0f}' y='{-sz / 3:.0f}' width='{sz:.0f}' height='{sz * 0.66:.0f}' fill='{col}' stroke='{INK}' stroke-width='4' "
                     f"transform='translate({x:.0f},{y:.0f}) rotate({spin * k:.0f})'/>")
    # chispas
    for a, v, ph in SPARKS:
        kk = k - ph * 0.3
        if 0 < kk < 1.4:
            x = LX + math.cos(a) * v * kk
            y = LY + math.sin(a) * v * kk + 500 * kk * kk
            if 780 < y < 1900:
                s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{7 * (1 - kk / 1.4):.1f}' fill='#ffe066' opacity='{1 - kk / 1.4:.2f}'/>")
    return "".join(s)


def frame(t):
    noche = seg(t, 2.0, 4.6)
    fuego = (seg(t, BOOM, BOOM + 0.12) * (1 - 0.55 * seg(t, BOOM + 0.3, 9.5))) if t >= BOOM else 0
    hollin = seg(t, BOOM, BOOM + 0.3)
    casco = 0.0
    if t >= BOOM:
        k = clamp((t - BOOM) / 0.9)
        casco = -260 * math.sin(math.pi * k)
    defs = (cielo(t, noche, fuego)
            + "<radialGradient id='glow'><stop offset='0' stop-color='#fff4c0' stop-opacity='0.9'/>"
              "<stop offset='0.5' stop-color='#ffd27a' stop-opacity='0.35'/><stop offset='1' stop-color='#ffb060' stop-opacity='0'/></radialGradient>"
            + "<radialGradient id='boomglow'><stop offset='0' stop-color='#fff2b0' stop-opacity='0.95'/>"
              "<stop offset='0.4' stop-color='#ff9a3a' stop-opacity='0.55'/><stop offset='1' stop-color='#ff5a1f' stop-opacity='0'/></radialGradient>")
    escena = [fondo(t, noche, fuego)]
    if fuego > 0:
        escena.append(f"<circle cx='{LX}' cy='{LY}' r='{lerp(200, 640, seg(t, BOOM, BOOM + 0.4)):.0f}' fill='url(#boomglow)' opacity='{fuego:.2f}'/>")
    escena.append(semaforo(t, noche, t >= BOOM, hollin))
    escena.append(policia(t, hollin, casco))
    escena.append(fugas(t))
    cx = lerp(180, 1500, seg(t, 0, 4.6) * 0.15 + clamp(t / 4.6) * 0.85)
    if cx < 1500:
        escena.append(caballo(t, cx))
    escena.append(explosion(t))
    z = 1 + 0.15 * seg(t, BOOM, BOOM + 0.7)
    sx = sy = 0.0
    if BOOM <= t < BOOM + 0.6:
        f = 1 - (t - BOOM) / 0.6
        sx, sy = 18 * f * math.sin(t * 97), 14 * f * math.cos(t * 83)
    cuerpo = (f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"
              f"<g transform='translate({sx:.1f},{sy:.1f})'>" + zoom(LX, 1300, z, "".join(escena)) + "</g>")
    flash = 0.85 * (1 - seg(t, BOOM, BOOM + 0.3)) if t >= BOOM else 0
    if flash > 0.01:
        cuerpo += f"<rect width='{W}' height='{H}' fill='#fff8e0' opacity='{flash:.2f}'/>"
    from lib import svg
    return svg(cuerpo, defs)
