"""2026-11-26-c4 · Las estatuas griegas no eran blancas: estaban pintadas de colores vivos.

Historia: una estatua griega de mármol (original) entra deslizándose en un templo junto al mar.
Brilla blanca; una lupa encuentra diminutos restos de pintura azul y roja; en la REVELACION
el color sube desde los pies hasta la cabeza (túnica azul, manto rojo con cenefa dorada, pelo
castaño con cinta de oro), estalla una lluvia de gotas de pintura y la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.0    # el color sube por la estatua
MUSICA = 6
SC = 1.12          # escala de estatua + pedestal

rng = np.random.default_rng(26114)
CLOUDS = [(160, 380, 1.3, 9), (760, 260, 1.0, 6), (520, 620, 0.8, 11), (930, 760, 1.1, 8)]
SPARK = [(-60, 1240), (55, 1380), (-30, 1520), (90, 1560), (-110, 1460), (20, 1090), (-70, 1330)]
DROPS = [(rng.uniform(0, 6.283), rng.uniform(380, 820), rng.uniform(10, 22),
          ["#2f6fd6", "#e0363c", "#ffc81e", "#2bb673", "#ff8a1e"][i % 5]) for i in range(34)]
# restos de pintura que ve la lupa (coordenadas locales de la estatua)
TRAZAS = [(30, 1470, 7, "#2f6fd6"), (62, 1495, 6, "#2f6fd6"), (40, 1515, 5, "#2f6fd6"),
          (70, 1462, 6, "#e0363c"), (22, 1500, 5, "#e0363c"), (55, 1525, 4, "#ffc81e"),
          (80, 1510, 4, "#e0363c"), (45, 1450, 4, "#2f6fd6")]


def colores(p):
    if p:
        return dict(skin="#f2c39c", skin2="#d99a74", hair="#7a3b1e", hair2="#5a2a14", band="#ffc81e",
                    chiton="#2f6fd6", chiton2="#1f4fa8", him="#e0363c", him2="#b0242b", trim="#ffc81e",
                    lips="#d23a48", iris="#4a2a18", flower="#ff4f7a", leaf="#2bb673")
    return dict(skin="#f6f2ea", skin2="#d8d1c4", hair="#ece6da", hair2="#cfc7b8", band="#e4ddd0",
                chiton="#f3eee5", chiton2="#d4ccbe", him="#ebe5da", him2="#cdc5b6", trim="#e0d9cc",
                lips="#d9d1c4", iris="#bdb5a8", flower="#efe9df", leaf="#ddd6c9")


def brazo(d, ancho, col):
    return (f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{ancho + 18}' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='{d}' fill='none' stroke='{col}' stroke-width='{ancho}' stroke-linecap='round' stroke-linejoin='round'/>")


def estatua(t, p, look=0.0, smile=0.0):
    """Figura en coordenadas locales (x centrada en 0, y absolutas). p=1 pintada, p=0 mármol."""
    c = colores(p)
    g = []
    # brazo de atrás (izquierda del espectador), cuelga junto al cuerpo
    g.append(brazo("M-82 1200 Q-112 1300 -116 1410", 34, c["skin"]))
    # falda de la túnica (chiton)
    g.append(f"<path d='M-92 1325 Q-118 1480 -150 1622 L150 1622 Q118 1480 92 1325 Z' fill='{c['chiton']}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for fx in (-100, -62, -24, 14, 52, 90):
        g.append(f"<path d='M{fx * 0.62:.0f} 1350 Q{fx * 0.85:.0f} 1490 {fx * 1.1:.0f} 1612' fill='none' stroke='{c['chiton2']}' stroke-width='7' stroke-linecap='round'/>")
    # cenefa de la falda
    g.append(f"<path d='M-146 1586 L146 1586 L150 1622 L-150 1622 Z' fill='{c['trim']}' stroke='{INK}' stroke-width='6'/>")
    if p:
        for i in range(-6, 7):
            g.append(f"<rect x='{i * 22 - 6}' y='1597' width='12' height='12' fill='{c['him']}'/>")
        for sx, sy in ((-60, 1420), (40, 1480), (-30, 1530), (80, 1550), (-95, 1540), (10, 1390)):
            g.append(f"<circle cx='{sx}' cy='{sy}' r='6' fill='{c['trim']}' stroke='{INK}' stroke-width='3'/>")
    # pies
    for fx in (-50, 50):
        g.append(f"<ellipse cx='{fx}' cy='1626' rx='34' ry='14' fill='{c['skin']}' stroke='{INK}' stroke-width='6'/>")
    # torso
    g.append(f"<path d='M-84 1185 Q-100 1260 -94 1340 L94 1340 Q100 1260 84 1185 Q0 1168 -84 1185 Z' fill='{c['chiton']}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for fx in (-40, 0, 40):
        g.append(f"<path d='M{fx} 1200 Q{fx * 1.1:.0f} 1260 {fx * 1.15:.0f} 1330' fill='none' stroke='{c['chiton2']}' stroke-width='6' stroke-linecap='round'/>")
    # manto (himation) en diagonal
    g.append(f"<path d='M-90 1192 Q-40 1172 -6 1192 Q66 1300 124 1430 Q74 1474 6 1458 Q-66 1424 -100 1352 Z' fill='{c['him']}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-6 1192 Q66 1300 124 1430' fill='none' stroke='{c['trim']}' stroke-width='12' stroke-linecap='round'/>")
    for k in (0.3, 0.55, 0.8):
        g.append(f"<path d='M{lerp(-80, 10, k):.0f} {lerp(1210, 1450, k):.0f} Q{lerp(-30, 60, k):.0f} {lerp(1250, 1400, k):.0f} {lerp(-10, 100, k):.0f} {lerp(1200, 1420, k):.0f}' fill='none' stroke='{c['him2']}' stroke-width='6' stroke-linecap='round'/>")
    # brazo de delante doblado, sujeta una flor junto al pecho
    g.append(brazo("M84 1200 Q122 1290 96 1330 Q66 1300 40 1268", 32, c["skin"]))
    g.append(f"<path d='M40 1268 L30 1200' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>"
             f"<path d='M40 1268 L30 1200' stroke='{c['leaf']}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='42' cy='1228' rx='16' ry='9' fill='{c['leaf']}' stroke='{INK}' stroke-width='5' transform='rotate(-30 42 1228)'/>")
    for a in range(0, 360, 72):
        g.append(f"<circle cx='{30 + 13 * math.cos(math.radians(a)):.1f}' cy='{1194 + 13 * math.sin(math.radians(a)):.1f}' r='11' fill='{c['flower']}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='30' cy='1194' r='7' fill='{c['trim']}' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<circle cx='40' cy='1270' r='17' fill='{c['skin']}' stroke='{INK}' stroke-width='6'/>")
    # cuello
    g.append(f"<path d='M-22 1130 L-22 1182 Q0 1192 22 1182 L22 1130 Z' fill='{c['skin']}' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo de detrás (melena ondulada hasta los hombros)
    g.append(f"<path d='M-78 1060 Q-96 1130 -84 1176 Q-60 1188 -48 1160 L48 1160 Q60 1188 84 1176 Q96 1130 78 1060 Z' fill='{c['hair']}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cabeza
    g.append(f"<ellipse cx='0' cy='1085' rx='70' ry='80' fill='{c['skin']}' stroke='{INK}' stroke-width='{LW}'/>")
    # moño y flequillo ondulado
    g.append(f"<circle cx='0' cy='990' r='34' fill='{c['hair']}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-74 1080 Q-80 1010 -30 998 Q0 990 30 998 Q80 1010 74 1080 Q60 1040 40 1050 Q26 1026 8 1046 Q-8 1024 -26 1046 Q-44 1028 -56 1052 Q-66 1046 -74 1080 Z' fill='{c['hair']}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-70 1040 Q0 1000 70 1040' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
             f"<path d='M-70 1040 Q0 1000 70 1040' fill='none' stroke='{c['band']}' stroke-width='10' stroke-linecap='round'/>")
    for hx in (-30, 0, 30):
        g.append(f"<path d='M{hx - 8} 1000 Q{hx} 990 {hx + 8} 1000' fill='none' stroke='{c['hair2']}' stroke-width='5' stroke-linecap='round'/>")
    # ojos (parpadean y miran)
    blink = 0.12 if (t % 3.3) < 0.13 or abs(t - 6.1) < 0.06 else 1.0
    for ex in (-26, 26):
        g.append(f"<g transform='translate({ex},1088) scale(1,{blink})'>"
                 f"<ellipse rx='17' ry='19' fill='#ffffff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{look * 7:.1f}' cy='{3 + abs(look) * 3:.1f}' r='10' fill='{c['iris']}'/>"
                 f"<circle cx='{look * 7 - 4:.1f}' cy='{-1 + abs(look) * 3:.1f}' r='4' fill='#fff'/></g>")
        g.append(f"<path d='M{ex - 16} 1062 Q{ex} 1054 {ex + 16} 1062' fill='none' stroke='{c['hair2'] if p else '#bfb7a9'}' stroke-width='6' stroke-linecap='round'/>")
    # nariz recta griega, mejillas y boca
    g.append(f"<path d='M0 1080 L-6 1112 Q0 1116 6 1112' fill='none' stroke='{c['skin2']}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")
    if p:
        for cx in (-44, 44):
            g.append(f"<ellipse cx='{cx}' cy='1118' rx='14' ry='8' fill='#ff8a8a' opacity='0.55'/>")
    sm = 6 + 8 * smile
    g.append(f"<path d='M-18 1130 Q0 {1130 + sm:.1f} 18 1130' fill='{c['lips']}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return "".join(g)


def pedestal():
    return (f"<rect x='-212' y='1622' width='424' height='30' rx='6' fill='#efe9de' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-188' y='1652' width='376' height='132' fill='#e4ddd0' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-150' y='1676' width='300' height='84' rx='6' fill='#d9d1c3' stroke='{INK}' stroke-width='5'/>"
            f"<rect x='-224' y='1784' width='448' height='34' rx='6' fill='#efe9de' stroke='{INK}' stroke-width='{LW}'/>")


def columna(x):
    s = [f"<rect x='{x - 62}' y='1000' width='124' height='716' fill='#f1e6cf' stroke='{INK}' stroke-width='{LW}'/>"]
    for fx in (-36, -12, 12, 36):
        s.append(f"<line x1='{x + fx}' y1='1012' x2='{x + fx}' y2='1704' stroke='#d8c8a8' stroke-width='7'/>")
    s.append(f"<path d='M{x - 92} 1000 L{x + 92} 1000 L{x + 70} 966 L{x - 70} 966 Z' fill='#f1e6cf' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<rect x='{x - 100}' y='930' width='200' height='36' fill='#e8dbc0' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{x - 84}' y='1716' width='168' height='30' fill='#e8dbc0' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(s)


def nube(cx, cy, sc):
    return (f"<g transform='translate({cx:.0f},{cy:.0f}) scale({sc})'>"
            f"<path d='M0 50 Q-10 10 40 12 Q60 -30 110 -6 Q150 -30 180 10 Q230 12 220 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def destello(x, y, r, a, col="#ffffff"):
    return (f"<path d='M{x} {y - r} Q{x + r * 0.18:.1f} {y - r * 0.18:.1f} {x + r} {y} Q{x + r * 0.18:.1f} {y + r * 0.18:.1f} {x} {y + r} "
            f"Q{x - r * 0.18:.1f} {y + r * 0.18:.1f} {x - r} {y} Q{x - r * 0.18:.1f} {y - r * 0.18:.1f} {x} {y - r} Z' fill='{col}' opacity='{a:.2f}'/>")


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)          # subida del color
    after = seg(t, REVELACION, REVELACION + 1.0)
    # entrada de la estatua: se desliza desde la derecha y se tambalea al pararse
    ent = seg(t, 0, 1.6)
    sx = 540 + lerp(620, 0, ent)
    wob = 4 * math.sin((t - 1.6) * 9) * math.exp(-(t - 1.6) * 2.2) if t > 1.6 else -3
    breath = 1 + 0.006 * math.sin(t * 2.6)
    # mirada: al frente, a la lupa (abajo a la derecha) y luego al espectador
    look = lerp(0, 0.9, seg(t, 5.0, 5.5)) * (1 - seg(t, 6.7, 7.0))
    smile = seg(t, REVELACION, REVELACION + 0.5)
    # cielo y luz cálida en la revelación
    top = mix("#5fb6ec", "#ffb86b", 0.35 * after); low = mix("#c9ecff", "#ffe8b0", 0.5 * after)
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920' viewBox='0 0 1080 1920'><defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<radialGradient id='halo'><stop offset='0' stop-color='#fff6c8' stop-opacity='0.95'/>"
         "<stop offset='0.5' stop-color='#ffd05a' stop-opacity='0.55'/><stop offset='1' stop-color='#ffb02e' stop-opacity='0'/></radialGradient>",
         "<linearGradient id='mar' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2c8fd4'/><stop offset='1' stop-color='#5cc0ee'/></linearGradient>",
         f"<clipPath id='pinta'><rect x='-400' y='{lerp(1830, 940, rev):.1f}' width='800' height='1000'/></clipPath>",
         "<clipPath id='lente'><circle cx='0' cy='0' r='104'/></clipPath>",
         "</defs>",
         "<rect width='1080' height='1920' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION, REVELACION + 1.1)
    scene = []
    # nubes que pasan despacio
    for cx, cy, sc, sp in CLOUDS:
        scene.append(nube((cx + t * sp * 3) % 1300 - 160, cy, sc))
    # mar lejano y colinas con olivos
    scene.append("<rect x='0' y='1060' width='1080' height='200' fill='url(#mar)'/>")
    for i in range(6):
        wx = (i * 200 + t * 30) % 1200 - 100
        scene.append(f"<path d='M{wx:.0f} {1100 + (i % 3) * 34} q20 -10 40 0 q20 10 40 0' fill='none' stroke='#bfe8ff' stroke-width='5' stroke-linecap='round'/>")
    scene.append(f"<path d='M0 1170 Q200 1110 420 1160 T820 1150 T1080 1140 L1080 1320 L0 1320 Z' fill='#8cc05a' stroke='{INK}' stroke-width='{LW}'/>")
    for ox, oy in ((300, 1150), (700, 1140), (860, 1150)):
        sway = 3 * math.sin(t * 1.5 + ox)
        scene.append(f"<rect x='{ox - 6}' y='{oy}' width='12' height='34' fill='#7a5230' stroke='{INK}' stroke-width='5'/>"
                     f"<ellipse cx='{ox + sway:.1f}' cy='{oy - 10}' rx='38' ry='26' fill='#5f9a3e' stroke='{INK}' stroke-width='6'/>")
    # suelo del templo (losas)
    scene.append(f"<rect x='0' y='1300' width='1080' height='620' fill='#e9d6ae' stroke='{INK}' stroke-width='{LW}'/>")
    for yy in (1420, 1560, 1730):
        scene.append(f"<line x1='0' y1='{yy}' x2='1080' y2='{yy}' stroke='#d2bb8c' stroke-width='6'/>")
    for k in range(-4, 5):
        scene.append(f"<line x1='{540 + k * 90}' y1='1300' x2='{540 + k * 260}' y2='1920' stroke='#d2bb8c' stroke-width='6'/>")
    scene.append(columna(96)); scene.append(columna(984))
    # halo dorado detrás de la estatua en la revelación
    if after > 0:
        scene.append(f"<circle cx='540' cy='1340' r='{lerp(120, 560, after):.0f}' fill='url(#halo)' opacity='{after:.2f}'/>")
        for i in range(12):
            a = math.radians(i * 30 + t * 18)
            r1, r2 = 200, lerp(240, 620, after)
            scene.append(f"<line x1='{540 + r1 * math.cos(a):.0f}' y1='{1340 + r1 * math.sin(a):.0f}' x2='{540 + r2 * math.cos(a):.0f}' y2='{1340 + r2 * math.sin(a):.0f}' stroke='#fff1a8' stroke-width='16' stroke-linecap='round' opacity='{0.6 * after:.2f}'/>")
    # sombra, pedestal y estatua
    scene.append(f"<ellipse cx='{sx:.1f}' cy='1880' rx='280' ry='26' fill='#000' opacity='0.18'/>")
    if 0 < t < 1.9:
        for i in range(5):
            pa = clamp((t - i * 0.25) / 0.8)
            if 0 < pa < 1:
                scene.append(f"<circle cx='{sx + 230 + i * 18 + pa * 60:.0f}' cy='{1866 - pa * 40:.0f}' r='{14 + 20 * pa:.0f}' fill='#f5e8cc' opacity='{0.7 * (1 - pa):.2f}'/>")
    body = [f"<g transform='translate({sx:.1f},60) translate(0,1818) scale({SC}) translate(0,-1818) rotate({wob:.2f} 0 1818)'>", pedestal(),
            f"<g transform='translate(0,1622) scale(1,{breath:.4f}) translate(0,-1622)'>",
            estatua(t, 0, look, 0)]
    if rev > 0:
        body.append(f"<g clip-path='url(#pinta)'>{estatua(t, 1, look, smile)}</g>")
        if rev < 1:
            ly = lerp(1830, 940, rev)
            for i in range(9):
                body.append(destello(-160 + i * 40, ly + 8 * math.sin(i * 2 + t * 20), 16, 0.95, "#fff7c2"))
    body.append("</g>")
    # destellos del mármol (situación normal)
    for i, (px, py) in enumerate(SPARK):
        a = max(0.0, math.sin(t * 2.4 + i * 1.7)) * seg(t, 1.6, 2.2) * (1 - seg(t, 4.8, 5.2))
        if a > 0.05:
            body.append(destello(px, py, 12 + 10 * a, a))
    body.append("</g>")
    scene.append("".join(body))
    # gotas de pintura que salen disparadas en la revelación
    if t >= REVELACION:
        k = clamp((t - REVELACION) / 1.6)
        for ang, dist, r, col in DROPS:
            dd = dist * ease(k)
            x = 540 + dd * math.cos(ang); y = 1340 + dd * math.sin(ang) * 0.8 + 260 * k * k
            if y > 1000:
                scene.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * (1 - 0.4 * k):.1f}' fill='{col}' stroke='{INK}' stroke-width='4' opacity='{1 - 0.6 * k:.2f}'/>")
    # la lupa encuentra restos de pintura (4,9 - 7,0)
    lin, lout = seg(t, 4.7, 5.3), seg(t, 6.6, 6.95)
    if lin > 0 and lout < 1:
        lx = lerp(1250, 600, lin) + lerp(0, 700, lout) + 18 * math.sin(t * 2.2)
        ly = lerp(1700, 1500, lin) - lerp(0, 300, lout) + 10 * math.cos(t * 2.8)
        tx, ty = (lx - sx) / SC, (ly - 60 - 1818) / SC + 1818   # punto observado (local de la estatua)
        found = seg(t, 5.4, 6.0)
        inner = [f"<g transform='translate({lx:.1f},{ly:.1f})'>",
                 f"<line x1='70' y1='70' x2='190' y2='200' stroke='{INK}' stroke-width='44' stroke-linecap='round'/>",
                 "<line x1='70' y1='70' x2='190' y2='200' stroke='#9b5a2c' stroke-width='28' stroke-linecap='round'/>",
                 "<g clip-path='url(#lente)'><rect x='-120' y='-120' width='240' height='240' fill='#e9d6ae'/>",
                 f"<g transform='scale(2.1) translate({-tx:.1f},{-ty:.1f})'>{estatua(t, 0)}"]
        for px, py, r, col in TRAZAS:
            inner.append(f"<circle cx='{px}' cy='{py}' r='{1.7 * r * found:.1f}' fill='{col}' stroke='{INK}' stroke-width='2' opacity='0.9'/>")
        inner.append("</g>")
        inner.append("<path d='M-70 -40 Q-50 -80 -10 -88' fill='none' stroke='#ffffff' stroke-width='12' stroke-linecap='round' opacity='0.8'/></g>")
        inner.append(f"<circle r='104' fill='#bfe6ff' opacity='0.12'/><circle r='108' fill='none' stroke='{INK}' stroke-width='24'/>"
                     "<circle r='108' fill='none' stroke='#c9a040' stroke-width='12'/></g>")
        scene.append("".join(inner))
    s.append(zoom(540, 1340, z, "".join(scene)))
    # destello blanco del golpe
    if REVELACION <= t < REVELACION + 0.6:
        s.append(f"<rect width='1080' height='1920' fill='#fffbe6' opacity='{0.55 * (1 - (t - REVELACION) / 0.6):.2f}'/>")
    s.append("</svg>")
    return "".join(s)
