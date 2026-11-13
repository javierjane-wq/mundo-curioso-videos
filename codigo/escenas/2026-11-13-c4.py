"""Oso polar: su piel es negra y su pelo no es blanco, es transparente.

Un oso polar camina por el hielo del Ártico y lo vemos blanco como la nieve. Una lupa gigante pasa
por encima y deja ver lo que hay debajo; en la revelación todo el oso cambia: piel negra y un
pelaje translúcido que solo parece blanco porque refleja la luz.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.5    # el oso entero muestra su piel negra y el pelo transparente
MUSICA = 5

ICE = 1560          # borde del hielo donde camina el oso
rng = np.random.default_rng(29)
SNOWF = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 10), rng.uniform(50, 120), rng.uniform(0, 6.28))
         for _ in range(70)]
STARS = [(rng.uniform(0, W), rng.uniform(0, 1000), rng.uniform(2, 5), rng.uniform(0, 6.28)) for _ in range(45)]
SPARK = [(rng.uniform(-330, 560), rng.uniform(-380, 0), rng.uniform(0, 6.28)) for _ in range(26)]

# ---- piezas del oso (coordenadas locales: pies en y=0, mira a la derecha) ----
TORSO = ("M-275 -175 C-290 -330 -120 -385 40 -340 C140 -315 215 -300 255 -255 "
         "C285 -215 270 -150 230 -120 C150 -95 -20 -100 -150 -105 C-230 -110 -268 -130 -275 -175 Z")
NECK = "M170 -300 C240 -330 300 -300 345 -270 L360 -195 C300 -170 240 -150 200 -140 Z"
HEAD = ("M300 -262 C320 -305 380 -312 420 -285 C450 -268 480 -262 505 -250 "
        "C525 -240 522 -212 500 -205 C460 -195 420 -190 385 -188 C340 -186 300 -215 300 -262 Z")
EAR = "M318 -285 C305 -318 335 -330 350 -305 Z"


def leg(x, top, ang, near, fill):
    """Pata gruesa con zarpa ancha; gira desde la cadera/hombro."""
    sh = mix(fill, "#9fb4c8", 0.35) if not near else fill
    return (f"<g transform='translate({x},{top}) rotate({ang:.1f})'>"
            f"<path d='M-42 0 L-40 {-top-38} Q-44 {-top-6} -8 {-top} L52 {-top} Q62 {-top-20} 40 {-top-40} L40 0 Z' "
            f"fill='{sh}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")


def bear(t, k, x, y, legs_ang, head_ang, tail, eyes_wide, clip_id=None):
    """k = 0 oso blanco; k = 1 piel negra y pelo transparente."""
    fur = mix("#f6f8fb", "#1f2129", k)
    shade = mix("#d5e1ec", "#121318", k)
    g = [f"<g transform='translate({x:.1f},{y:.1f})'>"]
    if clip_id is None:
        g.append(f"<ellipse cx='60' cy='6' rx='330' ry='30' fill='#3d6a90' opacity='0.25'/>")
    a1, a2 = legs_ang
    # patas del fondo
    g.append(leg(-150, -150, a2, False, fur))
    g.append(leg(175, -150, a1, False, fur))
    # cuerpo: primero con contorno doble, luego relleno encima (silueta limpia)
    hg = f"rotate({head_ang:.1f} 300 -230)"
    parts = [f"<path d='{TORSO}'/>", f"<g transform='{hg}'><path d='{NECK}'/><path d='{HEAD}'/><path d='{EAR}'/></g>",
             f"<ellipse cx='-280' cy='-200' rx='26' ry='20' transform='rotate({tail:.1f} -270 -200)'/>"]
    if k > 0.02:   # pelos transparentes que asoman por fuera de la silueta
        g.append(f"<g fill='none' stroke='#f2fbff' stroke-width='60' stroke-dasharray='3 8' opacity='{0.9*k:.2f}' "
                 f"stroke-linejoin='round'>{''.join(parts[:2])}</g>")
    g.append(f"<g fill='{fur}' stroke='{INK}' stroke-width='{2*LW}' stroke-linejoin='round'>{''.join(parts)}</g>")
    g.append(f"<g fill='{fur}'>{''.join(parts)}</g>")
    # sombra de la tripa
    g.append(f"<path d='M-230 -125 C-120 -150 60 -150 220 -130 C150 -100 -40 -100 -150 -105 Z' fill='{shade}'/>")
    # patas de delante (cerca)
    g.append(leg(-215, -150, a1, True, fur))
    g.append(leg(110, -150, a2, True, fur))
    for px, ang in ((-215, a1), (110, a2)):
        g.append(f"<g transform='translate({px},-150) rotate({ang:.1f})'>"
                 + "".join(f"<line x1='{dx}' y1='136' x2='{dx}' y2='150' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
                           for dx in (-5, 15, 35)) + "</g>")
    # pelaje transparente (aparece con k)
    if k > 0.02:
        hair = mix("#ffffff", "#dff4ff", 0.5)
        g.append(f"<g fill='#e8f7ff' opacity='{0.10*k:.2f}'>{''.join(parts[:2])}</g>")
        for i in range(16):
            hx = -230 + i * 30; hy = -300 + 110 * (i % 3) / 2 + 20 * math.sin(i)
            if hx > 200: hy = -230 + 25 * (i % 2)
            g.append(f"<path d='M{hx:.0f} {hy:.0f} q8 -14 4 -30' fill='none' stroke='#eaf8ff' stroke-width='5' "
                     f"stroke-linecap='round' opacity='{0.65*k:.2f}'/>")
    # cara
    g.append(f"<g transform='{hg}'>")
    g.append(f"<path d='M326 -296 C322 -310 334 -314 340 -302' fill='none' stroke='{mix('#b9c7d6', '#55586a', k)}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='512' cy='-238' rx='18' ry='14' fill='#15161b' stroke='{INK}' stroke-width='5'/>"
             f"<ellipse cx='507' cy='-243' rx='6' ry='4' fill='#fff' opacity='0.8'/>")
    g.append(f"<path d='M470 -206 Q485 -198 500 -206' fill='none' stroke='{mix(INK, '#8a8fa8', k)}' stroke-width='6' stroke-linecap='round'/>")
    blink = 0.12 if ((t + 0.6) % 2.9) < 0.13 else 1.0
    wd = 1 + 0.35 * eyes_wide
    g.append(f"<ellipse cx='410' cy='-262' rx='{15*wd:.1f}' ry='{17*wd*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
    if blink > 0.5:
        g.append(f"<circle cx='{415:.0f}' cy='-260' r='{9*wd:.1f}' fill='{INK}'/><circle cx='411' cy='-265' r='3.5' fill='#fff'/>")
    g.append(f"<ellipse cx='430' cy='-222' rx='16' ry='9' fill='#ff9fb2' opacity='{0.75*(1-k):.2f}'/>")
    g.append("</g></g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.35, 8.0)
    # ---- movimiento del oso ----
    walk = 1 - seg(t, 2.3, 2.8)
    x = lerp(-120, 420, seg(t, 0, 2.7))
    ph = t * 2 * math.pi * 1.5
    a1 = 16 * math.sin(ph) * walk; a2 = -a1
    y = ICE + 40 - 7 * abs(math.sin(ph)) * walk - 3 * seg(t, 2.8, 3.2) * pulso(t, 2.0)
    sniff = 0
    if 2.8 < t < 5.0: sniff = 6 * math.sin((t - 2.8) * 5) * seg(t, 2.8, 3.2) * (1 - seg(t, 4.6, 5.0))
    look = -10 * seg(t, 5.0, 5.6) * (1 - seg(t, 7.3, 7.8))      # mira la lupa
    up = -8 * seg(t, 7.4, 7.9)                                     # sorpresa
    head = sniff + look + up + 2 * pulso(t, 1.1) * walk
    tail = 18 * pulso(t, 0.9)
    k = rev

    # ---- cielo: día ártico -> crepúsculo con aurora ----
    top = mix("#7fc4f0", "#16234d", rev); mid = mix("#bfe4fa", "#2d5f8a", rev); low = mix("#eaf7ff", "#7fd1d8", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.9*rev:.2f}'/>"
            f"<stop offset='0.4' stop-color='#bff3ff' stop-opacity='{0.55*rev:.2f}'/><stop offset='1' stop-color='#7fd1ff' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#2f7fc0', '#1d4f86', rev)}'/>"
            f"<stop offset='1' stop-color='{mix('#1f5f9a', '#123766', rev)}'/></linearGradient>"
            f"<clipPath id='lens'><circle cx='0' cy='0' r='165'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    for sx, sy, sr, sp in STARS:
        a = rev * (0.5 + 0.5 * math.sin(t * 4 + sp))
        if a > 0.03: s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    if rev > 0.01:
        for i, (yy, col) in enumerate(((560, "#6dffb0"), (690, "#5be0ff"), (820, "#b38cff"))):
            w = 60 * math.sin(t * 1.3 + i)
            s.append(f"<path d='M-60 {yy} C200 {yy-120+w:.0f} 420 {yy+90-w:.0f} 640 {yy-30:.0f} S960 {yy-140+w:.0f} 1160 {yy-40}' "
                     f"fill='none' stroke='{col}' stroke-width='70' stroke-linecap='round' opacity='{0.32*rev:.2f}'/>")
    # sol bajo del Ártico (se oculta en la revelación)
    sun_y = lerp(980, 1180, seg(t, 0, 8))
    s.append(f"<circle cx='860' cy='{sun_y:.0f}' r='70' fill='#fff6c9' stroke='#ffd36b' stroke-width='8' opacity='{1-rev:.2f}'/>")
    # nubes
    for i, (cx, cy, sc) in enumerate(((150, 840, 1.3), (760, 700, 1.0), (460, 950, 0.8))):
        dx = (t * 16 * (1 + 0.4 * i)) % 1500 - 300
        s.append(f"<g transform='translate({cx + dx - 400:.0f},{cy}) scale({sc})' opacity='{0.9 - 0.5*rev:.2f}'>"
                 f"<path d='M0 40 Q15 -15 75 5 Q105 -40 165 -5 Q225 -20 245 40 Z' fill='#ffffff' stroke='{INK}' "
                 f"stroke-width='6' stroke-linejoin='round'/></g>")
    z = 1 + 0.17 * seg(t, 7.4, 10)
    w = []
    # montañas de hielo lejanas
    w.append(f"<path d='M0 1300 L120 1170 L210 1240 L330 1110 L460 1250 L560 1190 L700 1270 L820 1150 L950 1240 L1080 1180 L1080 1340 L0 1340 Z' "
             f"fill='{mix('#d9eefc', '#6f97c0', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    w.append(f"<path d='M330 1110 L300 1150 L345 1140 L360 1165 L390 1150 Z M820 1150 L795 1185 L835 1175 L850 1195 L870 1180 Z' fill='#ffffff'/>")
    # mar con olas
    w.append(f"<rect x='0' y='1330' width='{W}' height='300' fill='url(#sea)' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(7):
        wy = 1370 + i * 30; off = (t * 40 * (1 + 0.15 * i) + i * 90) % 160
        w.append(f"<path d='M{-160+off:.0f} {wy} " + " ".join(f"q40 -12 80 0 t80 0" for _ in range(9)) +
                 f"' fill='none' stroke='#9fd6ff' stroke-width='5' opacity='0.5'/>")
    # iceberg que flota
    bob = 6 * pulso(t, 2.4)
    w.append(f"<g transform='translate(860,{1360 + bob:.1f})'><path d='M-90 30 L-60 -50 L-20 -30 L20 -90 L70 -20 L100 30 Z' "
             f"fill='#f2fbff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M20 -90 L70 -20 L100 30 L40 30 Z' fill='#bfe1f5'/></g>")
    # placa de hielo donde camina el oso
    w.append(f"<path d='M-20 {ICE-20} Q260 {ICE-60} 560 {ICE-40} T1100 {ICE-30} L1100 1940 L-20 1940 Z' fill='{mix('#f4fbff', '#cfe9f5', rev)}' "
             f"stroke='{INK}' stroke-width='{LW}'/>")
    w.append(f"<path d='M-20 {ICE+10} Q300 {ICE-20} 600 {ICE} T1100 {ICE}' fill='none' stroke='#bfe1f5' stroke-width='16'/>")
    for cx, cy, rx in ((160, 1820, 90), (900, 1760, 70), (560, 1880, 120)):
        w.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{rx*0.22:.0f}' fill='#d6ecf8'/>")
    # huellas
    for i in range(6):
        fx = -60 + i * 85
        if fx < x - 200:
            w.append(f"<ellipse cx='{fx}' cy='{1660 + 18*(i%2)}' rx='20' ry='9' fill='#bcd6e8'/>")
    # brillo detrás del oso en la revelación
    if rev > 0.01:
        w.append(f"<circle cx='{x+90:.0f}' cy='{y-230:.0f}' r='{lerp(200, 620, rev):.0f}' fill='url(#glow)'/>")
        for i in range(12):
            a = i * 30 + t * 12
            w.append(f"<path d='M{x+90:.0f} {y-230:.0f} l{700*math.cos(math.radians(a)):.0f} {700*math.sin(math.radians(a)):.0f} "
                     f"l{90*math.cos(math.radians(a+90)):.0f} {90*math.sin(math.radians(a+90)):.0f} Z' fill='#e9fbff' opacity='{0.16*rev:.2f}'/>")
    w.append(bear(t, k, x, y, (a1, a2), head, tail, seg(t, 7.4, 7.9)))
    # aliento (vaho)
    for i in range(3):
        p = ((t + i * 0.55) % 1.65) / 1.65
        hx = x + 520 + 70 * p; hy = y - 210 - 40 * p - head * 2
        w.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{8 + 22*p:.0f}' fill='#ffffff' opacity='{0.6*(1-p):.2f}'/>")
    # destellos del pelo en la revelación
    for sx, sy, sp in SPARK:
        a = rev * max(0, math.sin(t * 6 + sp))
        if a > 0.05:
            px, py = x + sx, y + sy; r = 10 + 8 * a
            w.append(f"<path d='M{px:.0f} {py-r:.0f} L{px+r*0.3:.0f} {py:.0f} L{px:.0f} {py+r:.0f} L{px-r*0.3:.0f} {py:.0f} Z "
                     f"M{px-r:.0f} {py:.0f} L{px:.0f} {py+r*0.3:.0f} L{px+r:.0f} {py:.0f} L{px:.0f} {py-r*0.3:.0f} Z' fill='#ffffff' opacity='{a:.2f}'/>")
    # lupa (5,0 - 7,5 s): dentro se ve la piel negra
    lens_in = seg(t, 4.8, 5.4) * (1 - seg(t, 7.3, 7.6))
    if lens_in > 0.01:
        lx = lerp(x - 60, x + 330, seg(t, 5.2, 7.2)) + 1200 * (1 - seg(t, 4.8, 5.4))
        ly = y - 230 + 40 * math.sin(t * 2.5)
        w.append(f"<g transform='translate({lx:.1f},{ly:.1f})'>")
        w.append(f"<rect x='95' y='95' width='46' height='190' rx='20' transform='rotate(-45 0 0)' fill='#b5652e' stroke='{INK}' stroke-width='{LW}'/>")
        w.append(f"<circle r='165' fill='#e6f6ff' stroke='none'/>")
        w.append(f"<g clip-path='url(#lens)'><g transform='translate({-lx:.1f},{-ly:.1f})'>"
                 f"<rect x='{lx-200:.0f}' y='{ly-200:.0f}' width='400' height='400' fill='#d6efff'/>"
                 + bear(t, 1.0, x, y, (a1, a2), head, tail, 0, clip_id="lens") + "</g></g>")
        w.append(f"<circle r='165' fill='none' stroke='#c9d3dd' stroke-width='22'/><circle r='165' fill='none' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle r='187' fill='none' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M-110 -60 Q-95 -110 -45 -128' fill='none' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='0.8'/>")
        w.append("</g>")
    s.append(zoom(x + 90, y - 200, z, "".join(w)))
    # copos de nieve por delante
    for sx, sy, sr, sp, ph2 in SNOWF:
        yy = (sy + t * sp) % (H + 40) - 20
        xx = sx + 25 * math.sin(t * 1.5 + ph2)
        s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{sr:.1f}' fill='#ffffff' opacity='0.85'/>")
    # destello de la revelación
    fl = clamp(1 - abs(t - 7.5) / 0.35)
    if fl > 0: s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.75*fl:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
