"""2026-11-13-c3 · Récords: la bicicleta más rápida, 296 km/h pedaleando tras un coche (Guinness, 2018).

Una ciclista original entra pedaleando pegada a la parte trasera de un coche con un gran carenado
que le corta el aire sobre un lago de sal. El coche acelera, el suelo corre cada vez más… y en la
revelación todo estalla en velocidad: rayos de luz, estelas, polvo de sal, cielo encendido y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.5   # la bici alcanza la velocidad récord: estallido de velocidad
MUSICA = 2

rng = np.random.default_rng(20261113)
CLOUDS = [(rng.uniform(0, 1300), rng.uniform(300, 900), rng.uniform(0.8, 1.4), rng.uniform(6, 14)) for _ in range(6)]
DUST = [(rng.uniform(0, 1), rng.uniform(1560, 1720), rng.uniform(6, 16), rng.uniform(0, 1)) for _ in range(40)]
LINES = [(rng.uniform(0, 1), rng.uniform(1280, 1900), rng.uniform(80, 260), rng.uniform(0, 1)) for _ in range(34)]
CRACKS = [(rng.uniform(0, 2400), rng.uniform(1290, 1900)) for _ in range(46)]

GROUND = 1702   # línea de contacto de las ruedas


def velocidad(t):
    return 260 + 900 * seg(t, 2.0, 7.4) + 2200 * seg(t, 7.3, 8.1)


def recorrido(t):
    """Distancia recorrida por el suelo (integral de la velocidad)."""
    n = 120; dt = t / n
    return sum(velocidad((i + 0.5) * dt) for i in range(n)) * dt if t > 0 else 0.0


def ik(hx, hy, px, py, l1=98, l2=98):
    """Rodilla para una pierna de cadera (hx,hy) a pedal (px,py), rodilla hacia delante."""
    dx, dy = px - hx, py - hy
    d = min(math.hypot(dx, dy), l1 + l2 - 1)
    a = math.atan2(dy, dx)
    b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    ang = a - b
    return hx + l1 * math.cos(ang), hy + l1 * math.sin(ang)


def rueda(cx, cy, r, rot, aro="#2d3038"):
    g = [f"<g transform='translate({cx},{cy}) rotate({rot:.1f})'>",
         f"<circle r='{r}' fill='#eaf2f8' fill-opacity='0.35' stroke='{INK}' stroke-width='{LW}'/>",
         f"<circle r='{r-7}' fill='none' stroke='{aro}' stroke-width='7'/>"]
    for a in range(0, 360, 30):
        g.append(f"<line x1='0' y1='0' x2='{(r-9)*math.cos(math.radians(a)):.1f}' y2='{(r-9)*math.sin(math.radians(a)):.1f}' stroke='#9aa3ad' stroke-width='3'/>")
    g.append(f"<circle r='9' fill='#c9ced6' stroke='{INK}' stroke-width='5'/></g>")
    return "".join(g)


def coche(t, rot, rev):
    """Coche de arrastre original con un gran carenado trasero que corta el aire."""
    vib = 2.5 * math.sin(t * 40) * (0.3 + rev)
    g = [f"<g transform='translate(0,{vib:.1f})'>"]
    g.append(f"<ellipse cx='820' cy='{GROUND+4}' rx='300' ry='22' fill='#000' opacity='0.18'/>")
    # carenado trasero (caja alta)
    g.append(f"<path d='M560 1330 L700 1330 Q730 1330 730 1360 L730 1600 L560 1600 Z' fill='#f2ead8' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='575' y='1350' width='22' height='230' rx='8' fill='#e0d4bb'/>")
    # cuerpo
    g.append(f"<path d='M600 1470 L1020 1500 Q1110 1520 1110 1570 L1110 1610 L600 1610 Z' fill='#e8483b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M730 1530 L1080 1548' stroke='#ffd23f' stroke-width='16' stroke-linecap='round'/>")
    # cabina con piloto
    g.append(f"<path d='M820 1484 Q860 1415 930 1430 Q965 1440 975 1494 Z' fill='#7fd0ff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<circle cx='885' cy='1460' r='24' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M885 1450 L909 1450' stroke='#2e5c9a' stroke-width='9' stroke-linecap='round'/>")
    # alerón y escape
    g.append(f"<rect x='740' y='1440' width='60' height='22' rx='6' fill='#3b3f46' stroke='{INK}' stroke-width='6'/>")
    flame = 0.6 + 0.4 * math.sin(t * 30)
    g.append(f"<path d='M742 1452 Q{742 - 40 - 50*rev*flame:.0f} 1440 {742-20-70*rev*flame:.0f} 1452 Q{742-40-50*rev*flame:.0f} 1464 742 1452 Z' fill='#ffb347' opacity='{0.4+0.6*rev:.2f}'/>")
    for wx in (745, 1010):
        g.append(rueda(wx, 1640, 62, rot * 0.8, "#1e2126").replace("fill='#eaf2f8' fill-opacity='0.35'", "fill='#3b3f46'"))
    g.append("</g>")
    return "".join(g)


def ciclista(t, rot, rev):
    """Ciclista original agachada, con casco y gafas; pedalea pegada al carenado."""
    crank = math.radians(rot * 0.55)
    bx, by = 362, 1648
    sway = 3 * math.sin(t * 9)
    g = [f"<g transform='translate(0,{sway:.1f})'>"]
    g.append(f"<ellipse cx='365' cy='{GROUND+4}' rx='170' ry='16' fill='#000' opacity='0.18'/>")
    hip = (318, 1478); sh = (440, 1446)
    # pierna lejana (más oscura)
    pf = (bx - 44 * math.cos(crank), by - 44 * math.sin(crank))
    kf = ik(*hip, *pf)
    g.append(f"<path d='M{hip[0]} {hip[1]} L{kf[0]:.1f} {kf[1]:.1f} L{pf[0]:.1f} {pf[1]:.1f}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M{hip[0]} {hip[1]} L{kf[0]:.1f} {kf[1]:.1f} L{pf[0]:.1f} {pf[1]:.1f}' fill='none' stroke='#1d3f73' stroke-width='18' stroke-linecap='round' stroke-linejoin='round'/>")
    # ruedas
    g.append(rueda(258, 1640, 62, rot))
    g.append(rueda(470, 1640, 62, rot))
    # cuadro
    R, BB, S, HT, F = (258, 1640), (bx, by), (330, 1505), (448, 1505), (470, 1640)
    for a, b in ((R, BB), (R, S), (S, BB), (S, HT), (HT, BB), (HT, F)):
        g.append(f"<line x1='{a[0]}' y1='{a[1]}' x2='{b[0]}' y2='{b[1]}' stroke='{INK}' stroke-width='17' stroke-linecap='round'/>")
    for a, b in ((R, BB), (R, S), (S, BB), (S, HT), (HT, BB), (HT, F)):
        g.append(f"<line x1='{a[0]}' y1='{a[1]}' x2='{b[0]}' y2='{b[1]}' stroke='#ffd23f' stroke-width='8' stroke-linecap='round'/>")
    # sillín y manillar
    g.append(f"<path d='M300 1494 L348 1490' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<path d='M448 1505 L478 1500 Q500 1505 492 1530' fill='none' stroke='{INK}' stroke-width='11' stroke-linecap='round'/>")
    # plato grande
    g.append(f"<circle cx='{bx}' cy='{by}' r='34' fill='#c9ced6' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='{bx}' cy='{by}' r='12' fill='#6b7280' stroke='{INK}' stroke-width='5'/>")
    # pierna cercana
    pn = (bx + 44 * math.cos(crank), by + 44 * math.sin(crank))
    kn = ik(*hip, *pn)
    g.append(f"<line x1='{bx}' y1='{by}' x2='{pn[0]:.1f}' y2='{pn[1]:.1f}' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M{hip[0]} {hip[1]} L{kn[0]:.1f} {kn[1]:.1f} L{pn[0]:.1f} {pn[1]:.1f}' fill='none' stroke='{INK}' stroke-width='36' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M{hip[0]} {hip[1]} L{kn[0]:.1f} {kn[1]:.1f}' fill='none' stroke='#2e5c9a' stroke-width='20' stroke-linecap='round'/>")
    g.append(f"<path d='M{kn[0]:.1f} {kn[1]:.1f} L{pn[0]:.1f} {pn[1]:.1f}' fill='none' stroke='#f2b58c' stroke-width='20' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='{pn[0]+8:.1f}' cy='{pn[1]+2:.1f}' rx='22' ry='11' fill='#ff5a5f' stroke='{INK}' stroke-width='5'/>")
    # torso agachado
    g.append(f"<path d='M300 1490 Q330 1420 445 1425 Q470 1440 450 1470 Q380 1478 335 1505 Z' fill='#3a7bd5' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M330 1452 Q380 1432 440 1436' fill='none' stroke='#ffd23f' stroke-width='10' stroke-linecap='round'/>")
    # brazo
    g.append(f"<path d='M432 1446 L470 1490 L492 1522' fill='none' stroke='{INK}' stroke-width='28' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M432 1446 L470 1490 L492 1522' fill='none' stroke='#3a7bd5' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<circle cx='494' cy='1524' r='12' fill='#f2b58c' stroke='{INK}' stroke-width='5'/>")
    # cabeza con casco aerodinámico
    hx, hy = 488, 1418
    g.append(f"<circle cx='{hx}' cy='{hy}' r='38' fill='#f2b58c' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M{hx-48} {hy-6} Q{hx-30} {hy-62} {hx+18} {hy-50} Q{hx+48} {hy-38} {hx+44} {hy-12} L{hx-20} {hy-10} Q{hx-70} {hy+4} {hx-110} {hy+10} Z' fill='#ffffff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M{hx-30} {hy-40} Q{hx} {hy-58} {hx+30} {hy-40}' fill='none' stroke='#ff5a5f' stroke-width='9' stroke-linecap='round'/>")
    blink = 0.15 if (t % 2.7) < 0.12 else 1.0
    look = 4 * math.sin(t * 1.3)
    g.append(f"<rect x='{hx-6}' y='{hy-18}' width='50' height='30' rx='13' fill='#7fd0ff' fill-opacity='0.55' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<g transform='translate({hx+20+look:.1f},{hy-3}) scale(1,{blink})'><ellipse rx='9' ry='12' fill='{INK}'/><circle cx='-3' cy='-4' r='4' fill='#fff'/></g>")
    # boca: sonrisa que se vuelve grito de emoción en la revelación
    if rev < 0.3:
        g.append(f"<path d='M{hx+8} {hy+20} Q{hx+20} {hy+28} {hx+30} {hy+18}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='{hx+20}' cy='{hy+22}' rx='10' ry='{4+7*rev:.1f}' fill='#7a1f2b' stroke='{INK}' stroke-width='5'/>")
    # gotas de esfuerzo en la tensión
    tens = seg(t, 5.0, 6.0)
    if tens > 0:
        for i, (dx, ph) in enumerate(((-30, 0.0), (-55, 0.4))):
            k = ((t + ph) % 0.8) / 0.8
            g.append(f"<path d='M{hx+dx-10*k:.0f} {hy-58+30*k:.0f} q-7 12 0 16 q7 -4 0 -16 Z' fill='#8fd3ff' stroke='{INK}' stroke-width='4' opacity='{tens*(1-k):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, 7.4, 8.1)
    tens = seg(t, 4.8, 7.4)
    dist = recorrido(t)
    rot = dist * 0.9
    # cielo: azul de día -> más intenso en la tensión -> encendido en la revelación
    top = mix(mix("#3d8fe8", "#2f6fd6", tens), "#ff5f8f", rev)
    mid = mix(mix("#7cc0f5", "#6ab0f0", tens), "#ff9d4d", rev)
    low = mix("#d6f0ff", "#ffe08a", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='burst'><stop offset='0' stop-color='#fffbe8' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.4' stop-color='#ffe08a' stop-opacity='{0.6*rev:.3f}'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='salt' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#e9f3f8', '#fff3d6', rev)}'/>"
            f"<stop offset='1' stop-color='{mix('#fbfcf7', '#fffaf0', rev)}'/></linearGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    c = []
    # nubes lejanas (arriba, tranquilas)
    for cx, cy, sc, sp in CLOUDS:
        x = (cx - t * sp * (1 + 3 * rev)) % 1400 - 200
        c.append(f"<g transform='translate({x:.0f},{cy:.0f}) scale({sc:.2f})' opacity='0.92'>"
                 f"<path d='M-110 30 Q-100 -20 -50 -10 Q-30 -55 20 -35 Q60 -60 95 -15 Q130 -10 125 30 Z' fill='{mix('#ffffff', '#fff0e0', rev)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # montañas lejanas en el horizonte
    m = mix("#8a86d6", "#c46a9a", rev); m2 = mix("#a7a3e6", "#e08aa8", rev)
    off = (dist * 0.03) % 540
    c.append(f"<g transform='translate({-off:.1f},0)'>")
    for k in range(3):
        bx = k * 540
        c.append(f"<path d='M{bx-20} 1270 L{bx+60} 1180 L{bx+130} 1215 L{bx+230} 1130 L{bx+320} 1210 L{bx+400} 1165 L{bx+480} 1225 L{bx+560} 1190 L{bx+560} 1280 L{bx-20} 1280 Z' fill='{m}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        c.append(f"<path d='M{bx+200} 1158 L{bx+230} 1130 L{bx+262} 1160 L{bx+246} 1152 L{bx+230} 1166 L{bx+214} 1152 Z' fill='{m2}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    c.append("</g>")
    # destello detrás de la ciclista en la revelación
    if rev > 0:
        c.append(f"<circle cx='420' cy='1500' r='{lerp(200, 900, rev):.0f}' fill='url(#burst)'/>")
        for i in range(16):
            a = i * 22.5 + t * 25
            c.append(f"<path d='M420 1520 L{420+1400*math.cos(math.radians(a-4)):.0f} {1520+1400*math.sin(math.radians(a-4)):.0f} L{420+1400*math.cos(math.radians(a+4)):.0f} {1520+1400*math.sin(math.radians(a+4)):.0f} Z' fill='#fff6c8' opacity='{0.22*rev:.2f}'/>")
    # lago de sal
    c.append(f"<path d='M0 1268 L1080 1268 L1080 1920 L0 1920 Z' fill='url(#salt)' stroke='{INK}' stroke-width='{LW}'/>")
    if rev > 0:
        c.append(f"<rect x='0' y='1272' width='1080' height='648' fill='#ffe9a8' opacity='{0.35*rev:.2f}'/>")
    # grietas hexagonales de la sal que corren hacia atrás (más rápido cuanto más cerca)
    for cx, cy in CRACKS:
        depth = (cy - 1268) / 650
        sc = 0.35 + depth * 1.1
        x = (cx - dist * (0.25 + depth * 1.1)) % 2400 - 300
        pts = " ".join(f"{x + 60*sc*math.cos(math.radians(a)):.0f},{cy + 16*sc*math.sin(math.radians(a)):.0f}" for a in range(0, 360, 60))
        c.append(f"<polygon points='{pts}' fill='none' stroke='{mix('#b9cfdc', '#e6c58a', rev)}' stroke-width='{2+4*depth:.1f}' stroke-linejoin='round'/>")
    # pista marcada
    lane = (dist * 1.2) % 160
    for k in range(10):
        x = k * 160 - lane - 160
        c.append(f"<rect x='{x:.0f}' y='1760' width='90' height='14' rx='7' fill='{mix('#7aa6c2', '#f08a3c', rev)}'/>")
    # estelas de velocidad
    sp = clamp(0.6 * tens + rev)
    if sp > 0.02:
        for u, y, ln, ph in LINES:
            x = (u * 1600 - t * 2600 * (0.4 + rev)) % 1600 - 260
            c.append(f"<line x1='{x:.0f}' y1='{y:.0f}' x2='{x + ln*(1+rev):.0f}' y2='{y:.0f}' stroke='{mix("#8fbcd8", "#ffffff", rev)}' stroke-width='{5+5*rev:.0f}' stroke-linecap='round' opacity='{0.8*sp:.2f}'/>")
    # grupo coche + ciclista: entra desde la izquierda y luego tiembla con la velocidad
    gx = lerp(-380, 0, seg(t, 0, 2.2)) + lerp(0, 20, rev) + 6 * math.sin(t * 2.1) * (1 - rev)
    # polvo de sal que levantan
    for u, y, r, ph in DUST:
        k = (u + t * (0.8 + 2.5 * rev)) % 1.0
        x = 600 - k * (700 + 600 * rev)
        c.append(f"<circle cx='{x + gx:.0f}' cy='{y - 40*k:.0f}' r='{r*(1+1.6*k)*(0.6+0.8*rev):.1f}' fill='#ffffff' stroke='{mix('#b9cfdc', '#e6c58a', rev)}' stroke-width='3' opacity='{(1-k)*(0.45+0.5*rev):.2f}'/>")
    c.append(f"<g transform='translate({gx - 20:.1f},0) translate(360,{GROUND}) scale(1.12) translate(-360,{-GROUND})'>")
    c.append(coche(t, rot, rev))
    c.append(ciclista(t, rot, rev))
    c.append("</g>")
    z = 1 + 0.17 * seg(t, 7.4, 9.6)
    s.append(zoom(420, 1540, z, "".join(c)))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
