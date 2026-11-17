"""2026-11-17-c1 · La rana de bosque se congela en invierno (hasta 2/3 de su agua se vuelve hielo,
el corazón se para) y en primavera se descongela y revive.

Una rana de bosque original (marrón, con antifaz oscuro) llega saltando a un bosque boreal en otoño.
Empieza a nevar, la rana se vuelve azul de hielo y queda dentro de un bloque de hielo; su corazón
late cada vez más despacio hasta pararse. En la revelación sale el sol de primavera: el hielo estalla,
la nieve se derrite, brotan flores, la rana recupera el color, abre los ojos y da un gran salto. Zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45   # el hielo estalla y la rana revive: golpe musical
MUSICA = 5

rng = np.random.default_rng(1117)
HOJAS = [(rng.uniform(0, W), rng.uniform(-200, 900), rng.uniform(0.7, 1.2), rng.uniform(0, 6.28),
          ["#e8742c", "#f2b134", "#c8452a"][i % 3]) for i in range(16)]
COPOS = [(rng.uniform(0, W), rng.uniform(0, 1920), rng.uniform(5, 12), rng.uniform(90, 170), rng.uniform(0, 6.28)) for _ in range(90)]
ESQUIRLAS = [(rng.uniform(-1, 1), rng.uniform(-1.1, 0.2), rng.uniform(18, 34), rng.uniform(0, 360)) for _ in range(18)]
FLORES = [(110, 1585, "#ff6fa8"), (250, 1700, "#ffd23f"), (860, 1610, "#ff6fa8"), (980, 1730, "#9b7bff"),
          (700, 1840, "#ffd23f"), (380, 1860, "#9b7bff"), (60, 1800, "#ffd23f"), (1020, 1520, "#ffd23f")]
PINOS = [(40, 1150, 1.0), (170, 1120, 1.25), (300, 1160, 0.9), (780, 1140, 1.1), (900, 1110, 1.35), (1040, 1150, 1.0)]
PIEDRAS = [(150, 1480, 50), (930, 1470, 44), (980, 1860, 58)]


def rana(t, hielo, viva):
    """Rana de bosque original vista de frente, sentada. Origen = centro de la base."""
    piel = mix("#c9874a", "#a9d4ee", hielo)
    piel_osc = mix("#9a6232", "#7fb0d6", hielo)
    vientre = mix("#f4e2bd", "#e8f6fd", hielo)
    antifaz = mix("#4e2c18", "#3f6688", hielo)
    # ojos: abiertos al principio, se cierran al congelarse, se abren de golpe al revivir
    cerrado = seg(t, 4.0, 5.2) * (1 - seg(t, 7.55, 7.8))
    parpadeo = 0.12 if (((t + 1.0) % 2.7) < 0.12 and t < 4.0) or (7.9 < t < 8.0) else 1.0
    ab = max(0.06, (1 - cerrado)) * parpadeo
    # respiración del buche (se para al congelarse)
    resp = (1 - seg(t, 3.6, 5.0)) + seg(t, 7.6, 8.0)
    buche = 1 + 0.06 * resp * max(0, math.sin(t * 7))
    g = []
    # patas traseras (muslos plegados) y pies palmeados
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{150*sx}' cy='-70' rx='100' ry='74' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
        for dx, dy in ((40, -55), (95, -40), (60, -95)):
            g.append(f"<ellipse cx='{(150+dx-60)*sx}' cy='{-70+dy+40}' rx='16' ry='10' fill='{piel_osc}'/>")
        g.append(f"<path d='M{150*sx} -8 L{250*sx} 4 Q{262*sx} 14 {246*sx} 18 L{140*sx} 16 Z' fill='{piel_osc}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        for k in range(3):
            tx = (205 + k * 24) * sx
            g.append(f"<circle cx='{tx}' cy='{14 + k*2}' r='9' fill='{piel}' stroke='{INK}' stroke-width='5'/>")
    # cuerpo
    g.append(f"<ellipse cx='0' cy='-150' rx='160' ry='150' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='0' cy='-115' rx='{100*buche:.1f}' ry='{105*buche:.1f}' fill='{vientre}' stroke='{INK}' stroke-width='5'/>")
    # brazos
    for sx in (-1, 1):
        d = f"M{70*sx} -150 Q{110*sx} -80 {95*sx} -5"
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='46' stroke-linecap='round'/>")
        g.append(f"<path d='{d}' fill='none' stroke='{piel}' stroke-width='30' stroke-linecap='round'/>")
        for k in (-1, 0, 1):
            g.append(f"<circle cx='{95*sx + k*20}' cy='6' r='9' fill='{piel}' stroke='{INK}' stroke-width='5'/>")
    # cabeza
    g.append(f"<ellipse cx='0' cy='-300' rx='178' ry='100' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    # antifaz oscuro típico de la rana de bosque (del hocico al tímpano, pasando por el ojo)
    for sx in (-1, 1):
        g.append(f"<path d='M{40*sx} -318 Q{120*sx} -330 {176*sx} -292 Q{172*sx} -250 {140*sx} -238 Q{100*sx} -270 {40*sx} -300 Z' fill='{antifaz}'/>")
        g.append(f"<circle cx='{140*sx}' cy='-262' r='16' fill='{piel_osc}' stroke='{antifaz}' stroke-width='4'/>")
    # boca y fosas nasales
    g.append(f"<path d='M-128 -262 Q0 -212 128 -262' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<circle cx='-22' cy='-322' r='6' fill='{INK}'/><circle cx='22' cy='-322' r='6' fill='{INK}'/>")
    # ojos saltones con pupila horizontal
    mira = 8 * math.sin(t * 1.3) * (1 - seg(t, 3.5, 4.5))
    for sx in (-1, 1):
        ex, ey = 92 * sx, -372
        g.append(f"<circle cx='{ex}' cy='{ey}' r='60' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
        iris = mix("#e9b740", "#bfe3f7", hielo)
        g.append(f"<g transform='translate({ex},{ey + 6}) scale(1,{ab:.3f})'>"
                 f"<circle r='44' fill='{iris}' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='{mira:.1f}' cy='0' rx='27' ry='15' fill='{mix(INK, '#2b4a66', hielo)}'/>"
                 f"<circle cx='{mira - 14:.1f}' cy='-14' r='9' fill='#fff'/></g>")
        if ab < 0.5:
            g.append(f"<path d='M{ex - 42} {ey + 6} Q{ex} {ey + 24} {ex + 42} {ey + 6}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # escarcha sobre la piel
    if hielo > 0.05:
        for fx, fy in ((-120, -160), (110, -190), (-60, -330), (140, -90), (-150, -60), (40, -200)):
            r = 14 * hielo
            g.append(f"<g transform='translate({fx},{fy})' opacity='{hielo:.2f}' stroke='#ffffff' stroke-width='4' stroke-linecap='round'>"
                     f"<line x1='{-r:.1f}' y1='0' x2='{r:.1f}' y2='0'/><line x1='0' y1='{-r:.1f}' x2='0' y2='{r:.1f}'/>"
                     f"<line x1='{-r*0.7:.1f}' y1='{-r*0.7:.1f}' x2='{r*0.7:.1f}' y2='{r*0.7:.1f}'/></g>")
    return "".join(g)


def corazon(x, y, s, col):
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
            f"<path d='M0 34 C-60 -6 -46 -52 -14 -46 C-4 -44 0 -36 0 -30 C0 -36 4 -44 14 -46 C46 -52 60 -6 0 34 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<ellipse cx='-20' cy='-26' rx='9' ry='6' fill='#fff' opacity='0.6'/></g>")


def frame(t):
    inv = seg(t, 2.5, 5.0) * (1 - seg(t, REVELACION, 8.3))     # invierno
    pri = seg(t, REVELACION, 8.3)                                # primavera
    hielo = seg(t, 3.4, 5.6) * (1 - seg(t, REVELACION, 8.0))
    bloque = seg(t, 4.8, 5.8) * (1 - seg(t, REVELACION, 7.7))
    top = mix(mix("#8fcdf0", "#7d8fa8", inv), "#4fb8f2", pri)
    low = mix(mix("#fde0b0", "#d2dde8", inv), "#d9f6ff", pri)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='luz'><stop offset='0' stop-color='#fff7c2' stop-opacity='{0.9*pri:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffe066' stop-opacity='{0.45*pri:.3f}'/>"
            f"<stop offset='1' stop-color='#ffe066' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nubes suaves arriba (fondo tranquilo)
    for i, (cx, cy, sc) in enumerate([(220, 300, 1.3), (820, 520, 1.1), (480, 760, 0.9)]):
        dx = (t * 16 * (1 + 0.3 * i)) % 1500 - 250
        col = mix(mix("#ffffff", "#e3e9f0", inv), "#ffffff", pri)
        s.append(f"<g transform='translate({(cx + dx) % 1500 - 250:.0f},{cy}) scale({sc})' opacity='0.9'>"
                 f"<path d='M0 40 Q15 -15 75 0 Q105 -45 165 -5 Q230 -20 245 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # sol de primavera (esquina derecha, detrás de las colinas)
    sy = lerp(1120, 860, pri)
    if pri > 0:
        rot = t * 25
        rayos = "".join(f"<rect x='-10' y='-200' width='20' height='70' rx='10' fill='#ffd84d' transform='rotate({a + rot:.1f})'/>" for a in range(0, 360, 30))
        s.append(f"<g transform='translate(900,{sy:.0f})' opacity='{pri:.2f}'>{rayos}"
                 f"<circle r='110' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/></g>")
    cuerpo = []
    # colinas lejanas
    c1 = mix(mix("#d79a52", "#9fb2c4", inv), "#7cc96a", pri)
    c2 = mix(mix("#c47e3c", "#b9c8d6", inv), "#5fb556", pri)
    cuerpo.append(f"<path d='M0 1150 Q260 1060 540 1120 T1080 1090 L1080 1920 L0 1920 Z' fill='{c1}' stroke='{INK}' stroke-width='{LW}'/>")
    # abetos del bosque boreal
    pino = mix(mix("#2f6b45", "#4f6f78", inv), "#2f8a4c", pri)
    nieve_p = inv
    for px, py, sc in PINOS:
        sw = 3 * math.sin(t * 1.5 + px)
        cuerpo.append(f"<g transform='translate({px},{py}) scale({sc}) rotate({sw:.1f})'>"
                      f"<rect x='-10' y='-10' width='20' height='40' fill='#6b4428' stroke='{INK}' stroke-width='6'/>"
                      f"<path d='M0 -190 L60 -60 L35 -60 L80 0 L-80 0 L-35 -60 L-60 -60 Z' fill='{pino}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                      f"<path d='M0 -190 L30 -125 L-30 -125 Z' fill='#ffffff' opacity='{nieve_p:.2f}'/></g>")
    cuerpo.append(f"<path d='M0 1300 Q300 1230 600 1290 T1080 1270 L1080 1920 L0 1920 Z' fill='{c2}' stroke='{INK}' stroke-width='{LW}'/>")
    # suelo del bosque
    suelo = mix(mix("#9a6436", "#8a6a52", inv), "#5aa84a", pri)
    cuerpo.append(f"<path d='M0 1420 Q270 1370 540 1410 T1080 1400 L1080 1920 L0 1920 Z' fill='{suelo}' stroke='{INK}' stroke-width='{LW}'/>")
    # hojas secas en el suelo (otoño)
    hoja_a = 1 - pri
    for i in range(14):
        hx = 40 + i * 76; hy = 1480 + (i * 137) % 400
        cuerpo.append(f"<ellipse cx='{hx}' cy='{hy}' rx='24' ry='11' fill='{['#e8742c', '#f2b134', '#c8452a'][i % 3]}' "
                      f"stroke='{INK}' stroke-width='4' transform='rotate({(i*47) % 180} {hx} {hy})' opacity='{hoja_a:.2f}'/>")
    for px, py, pr in PIEDRAS:
        cuerpo.append(f"<ellipse cx='{px}' cy='{py}' rx='{pr}' ry='{pr*0.62:.0f}' fill='#8d8f99' stroke='{INK}' stroke-width='7'/>")
        if inv > 0.02:
            cuerpo.append(f"<ellipse cx='{px}' cy='{py - pr*0.42:.0f}' rx='{pr*0.85:.0f}' ry='{pr*0.25:.0f}' fill='#fff' opacity='{inv:.2f}'/>")
    # manto de nieve que crece y se derrite
    if inv > 0.01:
        cuerpo.append(f"<path d='M0 1415 Q270 1365 540 1405 T1080 1395 L1080 1920 L0 1920 Z' fill='#f4f9ff' stroke='{INK}' stroke-width='{LW}' opacity='{inv:.2f}'/>")
        for i in range(8):
            cuerpo.append(f"<ellipse cx='{70 + i*135}' cy='{1560 + (i*97) % 300}' rx='70' ry='14' fill='#cfe2f3' opacity='{0.8*inv:.2f}'/>")
    # flores y hierba de primavera
    if pri > 0.01:
        for i, (fx, fy, fc) in enumerate(FLORES):
            k = clamp((t - REVELACION - 0.1 * i) / 0.5)
            if k <= 0: continue
            sc = (1 + 0.15 * math.sin(math.pi * k)) * ease(k)
            sw = 5 * math.sin(t * 3 + i)
            pet = "".join(f"<ellipse cx='0' cy='-22' rx='13' ry='20' fill='{fc}' stroke='{INK}' stroke-width='5' transform='rotate({a})'/>" for a in range(0, 360, 72))
            cuerpo.append(f"<g transform='translate({fx},{fy}) scale({sc:.3f}) rotate({sw:.1f})'>"
                          f"<path d='M0 0 L0 70' stroke='{INK}' stroke-width='12'/><path d='M0 0 L0 70' stroke='#3f9a3a' stroke-width='6'/>"
                          f"<g transform='translate(0,-10)'>{pet}<circle r='14' fill='#fff3a0' stroke='{INK}' stroke-width='5'/></g></g>")
    # luz cálida detrás de la rana en la revelación
    cuerpo.append(f"<circle cx='540' cy='1430' r='{lerp(200, 640, pri):.0f}' fill='url(#luz)'/>")

    # ---- la rana ----
    fx, fy, esc_y = 540.0, 1640.0, 1.0
    if t < 2.4:   # tres saltos desde la izquierda
        k = clamp(t / 2.4)
        fx = lerp(150, 540, ease(k) * 0.3 + k * 0.7)
        ph = (k * 3) % 1
        fy -= 170 * math.sin(math.pi * ph)
        esc_y = 1.08 if ph < 0.5 else 0.96
    elif t >= REVELACION + 0.15:   # gran salto de alegría al revivir
        k = clamp((t - REVELACION - 0.15) / 0.9)
        fy -= 300 * math.sin(math.pi * k)
        esc_y = 1 + 0.12 * math.sin(math.pi * k)
        if k >= 1:
            fy -= 14 * abs(math.sin((t - REVELACION) * 6))
    # sombra
    sh = 1 - 0.4 * clamp((1640 - fy) / 300)
    cuerpo.append(f"<ellipse cx='{fx:.1f}' cy='1662' rx='{270*sh:.0f}' ry='30' fill='#000' opacity='0.22'/>")
    # temblor de frío justo antes de congelarse
    tiembla = 5 * math.sin(t * 60) * seg(t, 3.0, 3.6) * (1 - seg(t, 4.6, 5.0))
    cuerpo.append(f"<g transform='translate({fx + tiembla:.1f},{fy:.1f}) scale(1,{esc_y:.3f})'>{rana(t, hielo, pri)}")
    # bloque de hielo
    if bloque > 0.01:
        cuerpo.append(f"<g opacity='{bloque:.2f}'>"
                      f"<rect x='-285' y='-500' width='570' height='540' rx='46' fill='#a9dcff' fill-opacity='0.62' stroke='{INK}' stroke-width='{LW}'/>"
                      f"<rect x='-255' y='-470' width='510' height='480' rx='34' fill='none' stroke='#ffffff' stroke-width='6' opacity='0.8'/>"
                      f"<path d='M-220 -420 L-120 -470 M-230 -330 L-60 -460 M150 -60 L240 -150' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='0.75'/></g>")
    # esquirlas de hielo al estallar
    ke = clamp((t - REVELACION) / 0.9)
    if 0 < ke < 1:
        for dx, dy, r, a in ESQUIRLAS:
            ex = dx * 520 * ease(ke); ey = -250 + dy * 520 * ease(ke) + 400 * ke * ke
            cuerpo.append(f"<path d='M0 {-r} L{r*0.7:.0f} 0 L0 {r} L{-r*0.7:.0f} 0 Z' fill='#d8f2ff' stroke='{INK}' stroke-width='5' "
                          f"transform='translate({ex:.0f},{ey:.0f}) rotate({a + ke*300:.0f})' opacity='{1 - ke:.2f}'/>")
    cuerpo.append("</g>")
    # corazón: late normal, cada vez más lento, se para (gris) y vuelve a latir rojo
    if t < REVELACION:
        periodo = lerp(0.55, 1.6, seg(t, 3.0, 6.0))
        fase = (t / periodo) % 1
        amp = 1 - seg(t, 5.8, 6.6)
        lat = 1 + 0.22 * amp * max(0, math.sin(2 * math.pi * fase)) ** 3
        col = mix("#ff3b5c", "#8a96a6", seg(t, 5.6, 6.8))
    else:
        lat = 1.15 + 0.25 * max(0, math.sin((t - REVELACION) * 2 * math.pi * 2.2)) ** 3
        col = "#ff3b5c"
    hx, hy = 860.0, 1180.0
    cuerpo.append(corazon(hx, hy + 6 * math.sin(t * 2), 1.35 * lat, col))
    if t >= REVELACION:
        for i in range(8):
            a = i * 45 + 10; rr = lerp(80, 150, clamp((t - REVELACION) / 0.6))
            cuerpo.append(f"<line x1='{hx + math.cos(math.radians(a))*rr*0.75:.0f}' y1='{hy + math.sin(math.radians(a))*rr*0.75:.0f}' "
                          f"x2='{hx + math.cos(math.radians(a))*rr:.0f}' y2='{hy + math.sin(math.radians(a))*rr:.0f}' stroke='#ffd23f' "
                          f"stroke-width='8' stroke-linecap='round' opacity='{1 - seg(t, 8.6, 9.6):.2f}'/>")
    # hojas de otoño cayendo
    for hx0, hy0, sc, ph, hc in HOJAS:
        if t > 3.2: break
        y = hy0 + t * 260
        x = hx0 + 40 * math.sin(t * 2 + ph)
        if y < 1000 or y > 1900: continue
        cuerpo.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{22*sc:.0f}' ry='{10*sc:.0f}' fill='{hc}' stroke='{INK}' stroke-width='4' "
                      f"transform='rotate({t*120 + ph*50:.0f} {x:.0f} {y:.0f})' opacity='{1 - seg(t, 2.6, 3.2):.2f}'/>")
    # copos de nieve
    nv = seg(t, 2.5, 3.3) * (1 - seg(t, REVELACION, 7.8))
    if nv > 0.01:
        for cx, cy, r, sp, ph in COPOS:
            y = (cy + t * sp) % 1920
            x = cx + 25 * math.sin(t * 1.5 + ph)
            cuerpo.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#ffffff' opacity='{0.9*nv:.2f}'/>")
    # destellos de primavera
    if pri > 0.01:
        for cx, cy, r, sp, ph in COPOS[:24]:
            y = 1900 - ((cy + (t - REVELACION) * sp * 2) % 900)
            a = pri * (0.5 + 0.5 * math.sin(t * 6 + ph))
            cuerpo.append(f"<circle cx='{cx:.0f}' cy='{y:.0f}' r='{r*0.8:.1f}' fill='#fff6b0' opacity='{a:.2f}'/>")
    z = 1 + 0.16 * seg(t, REVELACION, 9.6) + 0.04 * seg(t, 5.0, 7.4)
    s.append(zoom(540, 1450, z, "".join(cuerpo)))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
