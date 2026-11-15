"""2026-11-15-c4 · Física: un pájaro posado en un cable eléctrico no se electrocuta porque sus
dos patas están al mismo voltaje (sin diferencia de potencial no pasa corriente por su cuerpo).

Un pajarito entra volando y se posa en un cable de la luz. La corriente (pulsos amarillos) recorre
el cable, cada vez más fuerte; el pájaro mira hacia abajo, nervioso… y en la REVELACION la corriente
pasa a toda velocidad bajo sus patas, sus dos patas brillan igual y él sigue tan tranquilo (zoom + halo).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, svg, zoom

DUR = 10.0
REVELACION = 7.5   # la corriente pasa bajo sus patas y él, feliz: golpe musical
MUSICA = 9

rng = np.random.default_rng(15)
CLOUDS = [(180, 520, 1.25, 10), (760, 360, 1.0, 14), (600, 820, 0.85, 8), (1000, 700, 1.1, 12)]
GRASS = [(rng.uniform(0, W), rng.uniform(1640, 1900), rng.uniform(0.7, 1.3)) for _ in range(46)]
FLOWERS = [(rng.uniform(40, W - 40), rng.uniform(1700, 1880), ["#ff6b8b", "#ffffff", "#ffd23f"][i % 3]) for i in range(14)]
SPARKS = [(rng.uniform(0, 6.28), rng.uniform(60, 200), rng.uniform(0, 1)) for _ in range(16)]

POLE_X = 960
WIRES = [(1180, 125), (1345, 105)]   # (altura en el poste, comba)
BIRD_X = 430


def wire_y(x, k):
    """Altura del cable k en x: parábola entre dos postes (x=-100 y x=960), y otro tramo a la derecha."""
    y0, sag = WIRES[k]
    if x <= POLE_X:
        a, b = -1100 + POLE_X, POLE_X     # el poste de la izquierda queda fuera de cuadro
    else:
        a, b = POLE_X, POLE_X + 1060
    u = (x - a) / (b - a)
    return y0 + sag * 4 * u * (1 - u)


def wire_path(k):
    pts = " ".join(f"L{x:.0f} {wire_y(x, k):.1f}" for x in range(-40, W + 60, 20))
    return "M" + pts[1:]


def bird(t, flying, flap, look_down, happy, ruffle):
    """Pajarito original (gorrión anaranjado) mirando a la derecha. Origen = punto entre las patas, sobre el cable."""
    blink = 0.12 if (t % 2.9) < 0.12 or 4.1 < t < 4.22 else 1.0
    g = []
    sh = ruffle * 3 * math.sin(t * 55)
    tail = -6 + 10 * math.sin(t * 3.1) if not flying else 8 * math.sin(t * 20)
    # cola
    g.append(f"<g transform='translate(-70,-120) rotate({tail:.1f})'>"
             f"<path d='M0 -10 L-110 -55 Q-118 -20 -104 8 L0 28 Z' fill='#9a4a22' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M-20 -6 L-96 -36 M-22 14 L-98 -6' stroke='{INK}' stroke-width='4' stroke-linecap='round' opacity='0.5'/></g>")
    # patas (solo posado)
    if not flying:
        for fx in (-22, 26):
            g.append(f"<path d='M{fx} -40 L{fx} -6' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>"
                     f"<path d='M{fx} -40 L{fx} -6' stroke='#ff9d2e' stroke-width='6' stroke-linecap='round'/>")
            g.append(f"<path d='M{fx-18} -4 Q{fx} -16 {fx+20} -4 Q{fx+24} 8 {fx+14} 12' fill='none' stroke='{INK}' stroke-width='11' stroke-linecap='round'/>"
                     f"<path d='M{fx-18} -4 Q{fx} -16 {fx+20} -4 Q{fx+24} 8 {fx+14} 12' fill='none' stroke='#ff9d2e' stroke-width='5' stroke-linecap='round'/>")
    else:
        for fx in (-30, 0):
            g.append(f"<path d='M{fx} -50 L{fx-28} -22' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
                     f"<path d='M{fx} -50 L{fx-28} -22' stroke='#ff9d2e' stroke-width='5' stroke-linecap='round'/>")
    # cuerpo
    g.append(f"<g transform='translate({sh:.1f},0)'>")
    g.append(f"<ellipse cx='0' cy='-120' rx='100' ry='84' fill='#e8853f' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='22' cy='-92' rx='64' ry='50' fill='#ffe2b4'/>")
    # cabeza
    g.append(f"<circle cx='62' cy='-205' r='62' fill='#e8853f' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M8 -236 Q50 -286 112 -240 Q80 -258 50 -252 Q24 -248 8 -236 Z' fill='#9a4a22'/>")
    g.append(f"<ellipse cx='78' cy='-172' rx='22' ry='14' fill='#ffd0b0'/>")
    g.append(f"<ellipse cx='100' cy='-178' rx='14' ry='9' fill='#ff8a8a' opacity='0.8'/>")
    # pico
    g.append(f"<path d='M116 -212 L166 -198 L116 -182 Z' fill='#ffb020' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # ojo
    if happy > 0.5:
        g.append(f"<path d='M66 -214 Q84 -238 102 -214' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    else:
        py = lerp(0, 8, look_down); px = lerp(4, 0, look_down)
        g.append(f"<g transform='translate(84,-214) scale(1,{blink})'>"
                 f"<circle r='21' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{px:.1f}' cy='{py:.1f}' r='12' fill='{INK}'/>"
                 f"<circle cx='{px-4:.1f}' cy='{py-5:.1f}' r='4.5' fill='#fff'/></g>")
    # ala
    if flying:
        g.append(f"<g transform='translate(-10,-150) rotate({flap:.1f})'>"
                 f"<path d='M0 0 Q-40 -150 -150 -170 Q-110 -110 -120 -60 Q-70 -10 0 20 Z' fill='#b85e2a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M-40 -40 L-118 -150 M-30 -10 L-110 -90' stroke='{INK}' stroke-width='4' opacity='0.45'/></g>")
    else:
        wf = 3 * math.sin(t * 2.4) + ruffle * 6 * math.sin(t * 40)
        g.append(f"<g transform='translate(-20,-140) rotate({wf:.1f})'>"
                 f"<path d='M40 -20 Q-30 -40 -100 0 Q-60 50 30 40 Q60 10 40 -20 Z' fill='#b85e2a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M-70 4 Q-20 10 20 2 M-50 24 Q-10 28 22 22' fill='none' stroke='{INK}' stroke-width='4' opacity='0.45'/></g>")
    g.append("</g>")
    return "".join(g)


def pulses(t, k, power, speed, n):
    """Pulsos de corriente recorriendo el cable k de izquierda a derecha."""
    out = []
    if power <= 0.01: return ""
    span = W + 200
    for i in range(n):
        x = (t * speed + i * span / n + k * 90) % span - 100
        y = wire_y(x, k)
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{34 * (0.6 + 0.4 * power):.0f}' fill='#ffd400' opacity='{0.45 * power:.2f}'/>"
                   f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='26' ry='11' fill='#fff6a8' stroke='#ff9d00' stroke-width='4' opacity='{power:.2f}'/>")
    return "".join(out)


def frame(t):
    rev = seg(t, 7.5, 8.1)
    tense = seg(t, 5.0, 7.0) * (1 - rev)
    power = seg(t, 2.2, 3.2) * (0.6 + 0.4 * seg(t, 5.0, 7.3))
    # cielo: azul de tarde, se vuelve dorado y luminoso en la revelación
    top = mix(mix("#4aa8ec", "#3b86c9", tense), "#ff9f5a", rev)
    mid = mix(mix("#8fd2ff", "#7ab8e8", tense), "#ffc77a", rev)
    low = mix(mix("#d8f1ff", "#c3dff3", tense), "#fff0b8", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95*rev:.2f}'/>"
            f"<stop offset='0.45' stop-color='#ffe066' stop-opacity='{0.6*rev:.2f}'/><stop offset='1' stop-color='#ffb000' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sun'><stop offset='0' stop-color='#fffbe8'/><stop offset='0.5' stop-color='#fff3b0' stop-opacity='0.6'/>"
            f"<stop offset='1' stop-color='#fff3b0' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol suave arriba a la derecha (detrás de los textos, tranquilo)
    s.append(f"<circle cx='880' cy='{lerp(260, 300, seg(t, 0, 10)):.0f}' r='210' fill='url(#sun)'/>")
    s.append(f"<circle cx='880' cy='{lerp(260, 300, seg(t, 0, 10)):.0f}' r='72' fill='#fff6c8' stroke='#ffd35a' stroke-width='7'/>")
    # nubes
    for cx, cy, sc, sp in CLOUDS:
        x = (cx + t * sp + 200) % (W + 500) - 250
        col = mix("#ffffff", "#ffe9d0", rev)
        s.append(f"<g transform='translate({x:.0f},{cy}) scale({sc})' opacity='0.92'>"
                 f"<path d='M-120 30 Q-120 -20 -70 -18 Q-60 -70 0 -62 Q50 -95 90 -40 Q140 -40 140 30 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    cam = []
    # colinas y prado
    h1 = mix("#7fcf6a", "#a8d35a", rev); h2 = mix("#5bb84f", "#8cc94a", rev); h3 = mix("#49a743", "#7dbb3c", rev)
    cam.append(f"<path d='M0 1450 Q180 1370 380 1430 T760 1400 T1080 1420 L1080 1920 L0 1920 Z' fill='{h1}' stroke='{INK}' stroke-width='{LW}'/>")
    # casita lejana
    cam.append(f"<g transform='translate(170,1395)'><rect x='-50' y='-60' width='100' height='70' fill='#fff3dc' stroke='{INK}' stroke-width='6'/>"
               f"<path d='M-64 -56 L0 -112 L64 -56 Z' fill='#e0533d' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
               f"<rect x='-14' y='-30' width='28' height='40' fill='#8a5a3a' stroke='{INK}' stroke-width='5'/>"
               f"<rect x='18' y='-46' width='22' height='22' fill='{mix('#9fd8ff', '#ffe27a', rev)}' stroke='{INK}' stroke-width='5'/></g>")
    cam.append(f"<path d='M0 1560 Q260 1500 560 1560 T1080 1540 L1080 1920 L0 1920 Z' fill='{h2}' stroke='{INK}' stroke-width='{LW}'/>")
    cam.append(f"<path d='M0 1680 Q320 1620 640 1670 T1080 1660 L1080 1920 L0 1920 Z' fill='{h3}' stroke='{INK}' stroke-width='{LW}'/>")
    for gx, gy, gs in GRASS:
        sw = 6 * math.sin(t * 2 + gx * 0.02)
        cam.append(f"<path d='M{gx:.0f} {gy:.0f} q{sw - 6:.1f} {-24*gs:.1f} {sw - 2:.1f} {-36*gs:.1f} M{gx:.0f} {gy:.0f} q{sw + 6:.1f} {-20*gs:.1f} {sw + 12:.1f} {-30*gs:.1f}' "
                   f"fill='none' stroke='#2f7d34' stroke-width='5' stroke-linecap='round'/>")
    for fx, fy, fc in FLOWERS:
        cam.append(f"<g transform='translate({fx:.0f},{fy:.0f})'>" + "".join(
            f"<circle cx='{12*math.cos(a):.1f}' cy='{12*math.sin(a):.1f}' r='9' fill='{fc}' stroke='{INK}' stroke-width='3'/>" for a in np.linspace(0, 6.28, 5, endpoint=False))
            + f"<circle r='7' fill='#ffb020' stroke='{INK}' stroke-width='3'/></g>")
    # poste de madera
    cam.append(f"<rect x='{POLE_X-26}' y='1060' width='52' height='760' rx='8' fill='#9b6a3f' stroke='{INK}' stroke-width='{LW}'/>")
    for yy in (1160, 1300, 1460, 1620):
        cam.append(f"<path d='M{POLE_X-14} {yy} q14 10 28 0' fill='none' stroke='{INK}' stroke-width='4' opacity='0.5'/>")
    cam.append(f"<rect x='{POLE_X-40}' y='1048' width='80' height='26' rx='8' fill='#7d5230' stroke='{INK}' stroke-width='7'/>")
    # cables (con brillo cuando sube la corriente)
    glow = 0.25 * tense + 0.75 * rev
    for k in range(2):
        cam.append(f"<path d='{wire_path(k)}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        cam.append(f"<path d='{wire_path(k)}' fill='none' stroke='{mix('#5a5f66', '#ffcf3a', glow if k == 0 else glow * 0.5)}' stroke-width='6' stroke-linecap='round'/>")
        if glow > 0.02:
            cam.append(f"<path d='{wire_path(k)}' fill='none' stroke='#fff27a' stroke-width='34' opacity='{0.3*glow if k == 0 else 0.15*glow:.2f}' stroke-linecap='round'/>")
    # aisladores del poste
    for k in range(2):
        y = WIRES[k][0]
        cam.append(f"<rect x='{POLE_X-18}' y='{y-30}' width='36' height='34' rx='8' fill='#7ed0c8' stroke='{INK}' stroke-width='6'/>")
        cam.append(f"<line x1='{POLE_X-18}' y1='{y-14}' x2='{POLE_X+18}' y2='{y-14}' stroke='{INK}' stroke-width='4'/>")
    # corriente: pulsos que corren por los cables
    speed = lerp(260, 520, seg(t, 5.0, 7.3)) + 500 * rev
    cam.append(pulses(t, 0, power, speed, int(round(lerp(5, 9, seg(t, 5, 7.3))))))
    cam.append(pulses(t, 1, power * 0.7, speed * 0.9, 5))
    # chispitas en el aislador durante la tensión
    if tense > 0.05:
        for a, r, ph in SPARKS[:8]:
            k = (t * 3 + ph) % 1
            x = POLE_X - 30 + math.cos(a) * r * 0.4 * k; y = WIRES[0][0] - 10 + math.sin(a) * r * 0.4 * k
            cam.append(f"<path d='M{x:.0f} {y:.0f} l8 -14 l-4 12 l10 -2' fill='none' stroke='#ffe14a' stroke-width='5' opacity='{tense*(1-k):.2f}' stroke-linecap='round'/>")
    # pájaro
    fly = seg(t, 0, 2.2)
    perch_y = wire_y(BIRD_X, 0)
    flying = t < 2.15
    if flying:
        bx = lerp(40, BIRD_X, fly)
        by = lerp(1230, perch_y, fly) - 120 * math.sin(math.pi * fly) * (1 - fly)
        flap = -40 + 55 * math.sin(t * 26)
        rot = lerp(-12, 0, fly)
    else:
        land = clamp((t - 2.15) / 0.35)
        bx = BIRD_X
        by = perch_y - 12 * math.sin(math.pi * land) + 3 * math.sin(t * 2.5)
        flap = 0; rot = 3 * math.sin(t * 1.7)
    look_down = seg(t, 5.2, 5.8) * (1 - rev)
    happy = 1.0 if t > 7.7 else 0.0
    ruffle = tense
    # halo de la revelación y patas brillando igual
    if rev > 0.01:
        cam.append(f"<circle cx='{BIRD_X}' cy='{perch_y-130:.0f}' r='{lerp(150, 460, rev):.0f}' fill='url(#halo)'/>")
    hop = 14 * abs(math.sin(math.pi * (t - 8.2) / 0.6)) if 8.2 < t < 9.4 else 0
    cam.append(f"<g transform='translate({bx:.1f},{by - hop:.1f}) rotate({rot:.1f}) scale(1.35)'>{bird(t, flying, flap, look_down, happy, ruffle)}</g>")
    if rev > 0.01:
        for fx in (-22, 26):
            pr = 1 + 0.15 * math.sin(t * 9)
            cam.append(f"<circle cx='{BIRD_X+fx*1.35:.0f}' cy='{perch_y - hop:.0f}' r='{34*pr*rev:.0f}' fill='none' stroke='#fff27a' stroke-width='7' opacity='{0.9*rev:.2f}'/>")
        # estrellitas alrededor del pájaro
        for i, (a, r, ph) in enumerate(SPARKS):
            aa = a + t * 0.8
            rr = 230 + 60 * math.sin(t * 2 + ph * 6)
            x = BIRD_X + math.cos(aa) * rr; y = perch_y - 180 + math.sin(aa) * rr * 0.8
            sc = rev * (0.6 + 0.4 * math.sin(t * 6 + i))
            cam.append(f"<path transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' d='M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5 Z' fill='#fffbe0' stroke='#ffb000' stroke-width='3'/>")
    z = 1 + 0.32 * seg(t, 7.4, 9.6)
    s.append(zoom(BIRD_X, perch_y - 160, z, "".join(cam)))
    return svg("".join(s), defs)
