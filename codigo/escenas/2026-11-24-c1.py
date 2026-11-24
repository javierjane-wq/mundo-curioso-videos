"""2026-11-24-c1 · El sismoscopio de Zhang Heng (China, año 132).

Una gran vasija de bronce con dragones; cada dragón sujeta una bola en la boca y debajo
espera un sapo con la boca abierta. La tierra empieza a temblar, una bola cae en la boca del
sapo (REVELACION): destello dorado y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.45   # la bola cae en la boca del sapo
MUSICA = 6

rng = np.random.default_rng(24)
PETALOS = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(10, 17), rng.uniform(0, 6.28), rng.uniform(60, 110)) for _ in range(16)]
POLVO = [(rng.uniform(80, 1000), rng.uniform(1640, 1880), rng.uniform(8, 18), rng.uniform(0, 6.28)) for _ in range(26)]
NUBES = [(160, 520, 1.0), (760, 360, 1.25), (520, 760, 0.8)]

DRAGON_Y = 1300
RX, LX = 760, 320          # dragones de perfil (derecha/izquierda)
BALL_LOCAL = (150, 32)
TOAD_Y = 1790


def parpadeo(t, periodo, fase):
    return 0.12 if ((t + fase) % periodo) < 0.12 else 1.0


def bola(x, y, r=26):
    return (f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='{x - r*0.35:.1f}' cy='{y - r*0.35:.1f}' r='{r*0.28:.1f}' fill='#fff6c8'/>")


def dragon_perfil(x, y, flip, t, con_bola=True, temblor=0.0):
    """Cabeza de dragón de jade de perfil (mira hacia +x en coordenadas locales)."""
    b = parpadeo(t, 3.3, 0.7 if flip > 0 else 2.1)
    wv = 10 * math.sin(t * 3.2 + (0 if flip > 0 else 1.5))
    jaw = 3 * math.sin(t * 2) + 6 * temblor * math.sin(t * 40)
    g = [f"<g transform='translate({x},{y}) scale({flip},1)'>"]
    # cuerpo serpenteante que baja por la vasija
    body = "M -10 20 C -90 60 -30 150 -110 210 S -170 330 -95 400"
    g.append(f"<path d='{body}' fill='none' stroke='{INK}' stroke-width='52' stroke-linecap='round'/>")
    g.append(f"<path d='{body}' fill='none' stroke='#3fae8c' stroke-width='36' stroke-linecap='round'/>")
    g.append(f"<path d='{body}' fill='none' stroke='#8fe0c2' stroke-width='8' stroke-linecap='round' stroke-dasharray='14 18'/>")
    # cresta del lomo
    for i, (px, py) in enumerate([(-60, 70), (-80, 150), (-125, 235), (-150, 310)]):
        g.append(f"<path d='M {px} {py} l -30 -14 l 14 26 Z' fill='#ff7a45' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # cuernos
    g.append(f"<path d='M -10 -48 Q -50 -90 -100 -110' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>")
    g.append(f"<path d='M -10 -48 Q -50 -90 -100 -110' fill='none' stroke='#f2ead8' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M 15 -55 Q -10 -105 -50 -128' fill='none' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>")
    g.append(f"<path d='M 15 -55 Q -10 -105 -50 -128' fill='none' stroke='#f2ead8' stroke-width='8' stroke-linecap='round'/>")
    # melena
    for i in range(4):
        a = -30 + i * 22
        g.append(f"<path d='M -35 {a} l -48 {6 + 4*math.sin(t*3+i):.1f} l 40 22 Z' fill='#ff7a45' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # mandíbula inferior
    g.append(f"<g transform='rotate({jaw:.1f} 20 30)'>"
             f"<path d='M 20 22 L 150 58 Q 166 66 150 76 L 60 74 Q 18 64 8 40 Z' fill='#36997b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M 60 50 l 10 -14 l 8 15 Z M 95 58 l 9 -13 l 8 14 Z' fill='#fff'/></g>")
    # bola en la boca
    if con_bola:
        g.append(bola(*BALL_LOCAL))
    # cabeza (mandíbula superior)
    g.append(f"<path d='M -45 -28 Q 0 -72 70 -44 L 158 -22 Q 180 -10 168 6 L 100 10 Q 60 12 40 24 Q -5 44 -45 30 Z' fill='#3fae8c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M 110 10 l 8 14 l 8 -13 Z M 140 8 l 8 13 l 7 -14 Z' fill='#fff' stroke='{INK}' stroke-width='3'/>")
    g.append(f"<circle cx='152' cy='-10' r='6' fill='{INK}'/>")
    # ceja y ojo
    g.append(f"<path d='M 10 -58 Q 45 -72 75 -50' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='42' cy='-30' rx='20' ry='{20*b:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
    if b > 0.5:
        g.append(f"<circle cx='48' cy='-30' r='9' fill='{INK}'/><circle cx='51' cy='-34' r='3.5' fill='#fff'/>")
    # bigote ondulante
    g.append(f"<path d='M 150 0 Q 190 {-20 + wv:.1f} 215 {-60 + wv:.1f} T 250 {-110 - wv:.1f}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<path d='M 150 0 Q 190 {-20 + wv:.1f} 215 {-60 + wv:.1f} T 250 {-110 - wv:.1f}' fill='none' stroke='#ffd23f' stroke-width='4' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def dragon_frente(x, y, t, temblor=0.0):
    b = parpadeo(t, 2.9, 1.4)
    wv = 8 * math.sin(t * 3)
    g = [f"<g transform='translate({x},{y})'>"]
    for s in (-1, 1):
        g.append(f"<path d='M {30*s} -60 Q {70*s} -120 {110*s} -135' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
                 f"<path d='M {30*s} -60 Q {70*s} -120 {110*s} -135' fill='none' stroke='#f2ead8' stroke-width='10' stroke-linecap='round'/>")
        g.append(f"<path d='M {70*s} -20 l {50*s} -20 l {-20*s} 40 Z' fill='#ff7a45' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
        g.append(f"<path d='M {40*s} 55 Q {95*s} {70 + wv:.1f} {120*s} {120 - wv:.1f}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # cabeza
    g.append(f"<path d='M -75 -40 Q 0 -95 75 -40 L 70 30 Q 0 50 -70 30 Z' fill='#3fae8c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for s in (-1, 1):
        g.append(f"<ellipse cx='{32*s}' cy='-30' rx='17' ry='{17*b:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if b > 0.5:
            g.append(f"<circle cx='{32*s}' cy='-27' r='8' fill='{INK}'/><circle cx='{32*s + 3}' cy='-31' r='3' fill='#fff'/>")
    # hocico y boca con bola
    g.append(f"<path d='M -55 25 Q 0 0 55 25 L 50 95 Q 0 112 -50 95 Z' fill='#36997b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='0' cy='72' rx='38' ry='28' fill='#5a1e1e' stroke='{INK}' stroke-width='6'/>")
    g.append(bola(0, 72, 24))
    g.append(f"<circle cx='-16' cy='30' r='6' fill='{INK}'/><circle cx='16' cy='30' r='6' fill='{INK}'/>")
    g.append("</g>")
    return "".join(g)


def vasija_path():
    return ("M 410 1180 L 670 1180 Q 690 1220 700 1250 Q 790 1300 790 1450 Q 790 1600 700 1660 "
            "L 690 1700 L 390 1700 L 380 1660 Q 290 1600 290 1450 Q 290 1300 380 1250 Q 390 1220 410 1180 Z")


def vasija(t):
    g = []
    g.append(f"<path d='{vasija_path()}' fill='url(#bronce)' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # bandas decorativas
    g.append(f"<path d='M 330 1340 Q 540 1385 750 1340 L 765 1380 Q 540 1428 315 1380 Z' fill='#8a5a22' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M 315 1560 Q 540 1605 765 1560 L 745 1600 Q 540 1642 335 1600 Z' fill='#8a5a22' stroke='{INK}' stroke-width='6'/>")
    for i in range(7):
        px = 370 + i * 57
        g.append(f"<path d='M {px} {1462 + 10*math.sin(i)} q 20 -26 40 0 q -20 26 -40 0 Z' fill='#5fb3a0' stroke='{INK}' stroke-width='4'/>")
    # pie
    g.append(f"<rect x='370' y='1690' width='340' height='42' rx='12' fill='#8a5a22' stroke='{INK}' stroke-width='{LW}'/>")
    # tapa
    g.append(f"<path d='M 390 1190 Q 540 1060 690 1190 Z' fill='#b9772c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='375' y='1180' width='330' height='30' rx='12' fill='#8a5a22' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<circle cx='540' cy='1100' r='26' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>")
    # brillo que recorre el bronce al principio
    gx = lerp(150, 1000, seg(t, 0.3, 2.2))
    g.append(f"<g clip-path='url(#cvas)'><path d='M {gx-60:.0f} 1100 L {gx:.0f} 1100 L {gx-160:.0f} 1760 L {gx-220:.0f} 1760 Z' fill='#fff8e0' opacity='0.45'/></g>")
    return "".join(g)


def sapo(x, y, t, fase, mira, con_bola=False, golpe=0.0):
    b = parpadeo(t, 3.7, fase)
    gl = 1 + 0.08 * math.sin(t * 5 + fase) + 0.25 * golpe
    sq = 1 - 0.12 * golpe
    g = [f"<g transform='translate({x},{y}) scale({1/sq:.3f},{sq:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='8' rx='120' ry='20' fill='#000' opacity='0.2'/>")
    # patas traseras
    for s in (-1, 1):
        g.append(f"<ellipse cx='{88*s}' cy='-30' rx='48' ry='38' fill='#5f9e3a' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M {100*s} 0 l {30*s} 4 l {-6*s} -14 Z' fill='#5f9e3a' stroke='{INK}' stroke-width='5'/>")
    # cuerpo
    g.append(f"<ellipse cx='0' cy='-62' rx='96' ry='70' fill='#7cbf4a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='0' cy='-45' rx='{58*gl:.1f}' ry='{42*gl:.1f}' fill='#f3e3a6' stroke='{INK}' stroke-width='5'/>")
    for sx, sy in ((-60, -95), (55, -88), (-40, -30), (70, -45)):
        g.append(f"<circle cx='{sx}' cy='{sy}' r='9' fill='#5f9e3a'/>")
    # patas delanteras
    for s in (-1, 1):
        g.append(f"<path d='M {40*s} -20 Q {48*s} 0 {58*s} 4 L {30*s} 6 Z' fill='#5f9e3a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # cabeza mirando arriba con la boca abierta
    g.append(f"<ellipse cx='0' cy='-128' rx='84' ry='50' fill='#7cbf4a' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='0' cy='-140' rx='54' ry='30' fill='#7a2230' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='0' cy='-132' rx='30' ry='12' fill='#ff8fa0'/>")
    if con_bola:
        g.append(bola(0, -160, 26))
        g.append(f"<path d='M -54 -140 Q 0 -112 54 -140' fill='#7cbf4a' stroke='{INK}' stroke-width='7'/>")
    for s in (-1, 1):
        g.append(f"<circle cx='{66*s}' cy='-168' r='27' fill='#7cbf4a' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<ellipse cx='{66*s}' cy='-170' rx='17' ry='{17*b:.1f}' fill='#fff' stroke='{INK}' stroke-width='4'/>")
        if b > 0.5:
            g.append(f"<circle cx='{66*s + mira:.1f}' cy='-176' r='8' fill='{INK}'/><circle cx='{66*s + mira + 3:.1f}' cy='-179' r='3' fill='#fff'/>")
    g.append("</g>")
    return "".join(g)


def templo(t, day):
    g = []
    g.append(f"<path d='M 0 1020 Q 180 930 360 990 Q 540 900 760 980 Q 920 930 1080 990 L 1080 1100 L 0 1100 Z' fill='{mix('#9bc7b0', '#ffcf8a', day)}' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    # muro rojo
    g.append(f"<rect x='-20' y='1090' width='1120' height='190' fill='#c8443a' stroke='{INK}' stroke-width='{LW}'/>")
    for px in (60, 300, 780, 1020):
        g.append(f"<rect x='{px-22}' y='1090' width='44' height='190' fill='#a8332c' stroke='{INK}' stroke-width='6'/>")
    for wx in (180, 900):
        g.append(f"<rect x='{wx-70}' y='1135' width='140' height='100' rx='8' fill='#f6d37a' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<path d='M {wx-70} 1185 H {wx+70} M {wx} 1135 V 1235 M {wx-35} 1135 V 1235 M {wx+35} 1135 V 1235' stroke='#a8332c' stroke-width='5'/>")
    # tejado con aleros curvos
    g.append(f"<path d='M -40 1040 Q 120 1075 300 1060 L 780 1060 Q 960 1075 1120 1040 L 1100 1100 L -20 1100 Z' fill='#2f6f73' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for px in range(20, 1080, 46):
        g.append(f"<line x1='{px}' y1='1068' x2='{px}' y2='1096' stroke='#1f4f52' stroke-width='5'/>")
    # farolillos que se balancean
    for lx, ph in ((150, 0.0), (930, 1.3)):
        ang = 5 * math.sin(t * 2.2 + ph) + 12 * day * 0
        g.append(f"<g transform='rotate({ang:.1f} {lx} 1098)'><line x1='{lx}' y1='1098' x2='{lx}' y2='1125' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse cx='{lx}' cy='1160' rx='36' ry='40' fill='#ff5a4a' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='{lx-18}' y='1196' width='36' height='10' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")
    return "".join(g)


def suelo():
    g = [f"<rect x='0' y='1275' width='{W}' height='{H-1275}' fill='#e9cf9d'/>",
         f"<line x1='0' y1='1278' x2='{W}' y2='1278' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, yy in enumerate((1340, 1430, 1550, 1700, 1880)):
        g.append(f"<line x1='0' y1='{yy}' x2='{W}' y2='{yy}' stroke='#c9ad7a' stroke-width='5'/>")
    for k in range(-6, 7):
        g.append(f"<line x1='{540 + k*70}' y1='1278' x2='{540 + k*260}' y2='1920' stroke='#c9ad7a' stroke-width='5'/>")
    # alfombra bajo la vasija
    g.append(f"<ellipse cx='540' cy='1770' rx='500' ry='105' fill='#b8473d' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='540' cy='1770' rx='450' ry='80' fill='none' stroke='#ffd23f' stroke-width='6' stroke-dasharray='20 14'/>")
    return "".join(g)


def frame(t):
    shake = seg(t, 5.0, 6.6) * (1 - seg(t, 7.55, 8.0))
    dx = 14 * shake * math.sin(t * 47) + 6 * shake * math.sin(t * 83)
    dy = 5 * shake * math.sin(t * 61)
    rev = seg(t, REVELACION, REVELACION + 0.45)
    glow = seg(t, REVELACION - 0.05, REVELACION + 0.6)
    day = glow
    # cámara: entra acercándose y en la revelación se acerca al sapo de la derecha
    z0 = lerp(1.18, 1.0, seg(t, 0, 2.2))
    zr = 1 + 0.28 * seg(t, REVELACION, 8.15)

    top = mix("#7fc8e6", "#ffb85c", glow * 0.8); low = mix("#fde9c4", "#ffe6a8", glow)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<linearGradient id='bronce' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#a8692a'/><stop offset='0.45' stop-color='#e0a24a'/><stop offset='1' stop-color='#9a5e24'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95*glow:.3f}'/><stop offset='0.4' stop-color='#ffd23f' stop-opacity='{0.6*glow:.3f}'/><stop offset='1' stop-color='#ff9a3c' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='cvas'><path d='{vasija_path()}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol suave y nubes arriba (fondo tranquilo)
    s.append(f"<circle cx='880' cy='600' r='70' fill='#fff3c4' stroke='#ffd48a' stroke-width='8' opacity='0.9'/>")
    for i, (cx, cy, sc) in enumerate(NUBES):
        ddx = (t * (10 + 4 * i)) % 1400 - 300
        s.append(f"<g transform='translate({(cx + ddx) % 1400 - 200:.0f},{cy}) scale({sc})' opacity='0.85'>"
                 f"<path d='M0 40 Q15 0 60 10 Q85 -30 135 0 Q185 -10 200 40 Z' fill='#fffaf0' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")

    w = []
    w.append(templo(t, glow))
    w.append(suelo())
    # halo de la revelación
    tx, ty = LX if False else 900, TOAD_Y
    if glow > 0.01:
        w.append(f"<circle cx='{tx}' cy='{ty-150}' r='{lerp(120, 620, rev):.0f}' fill='url(#halo)'/>")
        for k in range(12):
            a = k * 30 + t * 25
            ra = math.radians(a); rb = math.radians(a + 9)
            L = lerp(150, 700, rev)
            w.append(f"<path d='M {tx} {ty-150} L {tx + L*math.cos(ra):.0f} {ty-150 + L*math.sin(ra):.0f} L {tx + L*math.cos(rb):.0f} {ty-150 + L*math.sin(rb):.0f} Z' fill='#fff3b0' opacity='{0.35*glow:.2f}'/>")

    # polvo del temblor
    for px, py, pr, ph in POLVO:
        a = shake * (0.5 + 0.5 * math.sin(t * 9 + ph))
        if a > 0.05:
            w.append(f"<circle cx='{px + 10*math.sin(t*6+ph):.0f}' cy='{py - 40*((t*1.3+ph) % 1):.0f}' r='{pr:.0f}' fill='#c9ad7a' opacity='{0.7*a:.2f}'/>")

    # sapos (no tiemblan tanto)
    cayendo = t >= 7.0
    landed = t >= REVELACION
    golpe = seg(t, REVELACION, REVELACION + 0.12) * (1 - seg(t, REVELACION + 0.12, REVELACION + 0.45))
    w.append(sapo(180 + dx * 0.4, TOAD_Y, t, 0.3, 4))
    w.append(sapo(900 + dx * 0.4, TOAD_Y, t, 2.0, lerp(-4, 0, seg(t, 6.6, 7.0)), con_bola=landed, golpe=golpe))

    # vasija + dragones (tiemblan)
    rot = 1.2 * shake * math.sin(t * 39)
    v = [f"<g transform='translate({dx:.1f},{dy:.1f}) rotate({rot:.2f} 540 1700)'>"]
    v.append(f"<ellipse cx='540' cy='1735' rx='240' ry='26' fill='#000' opacity='0.22'/>")
    v.append(vasija(t))
    v.append(dragon_perfil(LX, DRAGON_Y, -1, t, True, shake))
    v.append(dragon_perfil(RX, DRAGON_Y, 1, t, not cayendo, shake))
    v.append(dragon_frente(540, 1300, t, shake))
    v.append("</g>")
    w.append("".join(v))
    w.append(sapo(540 + dx * 0.4, TOAD_Y + 90, t, 1.1, 0))

    # bola que cae (bamboleo antes)
    if cayendo and not landed:
        k = clamp((t - 7.0) / (REVELACION - 7.0))
        bx0, by0 = RX + BALL_LOCAL[0] + dx, DRAGON_Y + BALL_LOCAL[1] + dy
        bx1, by1 = 900, TOAD_Y - 148
        bx = lerp(bx0, bx1, k); by = lerp(by0, by1, k * k)
        w.append(f"<path d='M {bx:.0f} {by-40:.0f} L {bx:.0f} {by-120:.0f} M {bx-18:.0f} {by-35:.0f} L {bx-18:.0f} {by-90:.0f} M {bx+18:.0f} {by-35:.0f} L {bx+18:.0f} {by-90:.0f}' stroke='#fff' stroke-width='7' stroke-linecap='round' opacity='0.8'/>")
        w.append(bola(bx, by))
    # aro de impacto
    if landed:
        k = seg(t, REVELACION, REVELACION + 0.6)
        if k < 1:
            w.append(f"<circle cx='900' cy='{TOAD_Y-150}' r='{lerp(30, 260, k):.0f}' fill='none' stroke='#fff8d0' stroke-width='{lerp(22, 2, k):.1f}' opacity='{1-k:.2f}'/>")
        for i in range(8):
            a = math.radians(i * 45 + 20)
            r1 = lerp(60, 170, k); r2 = r1 + 40
            if k < 1:
                w.append(f"<line x1='{900 + r1*math.cos(a):.0f}' y1='{TOAD_Y-150 + r1*math.sin(a):.0f}' x2='{900 + r2*math.cos(a):.0f}' y2='{TOAD_Y-150 + r2*math.sin(a):.0f}' stroke='#ffd23f' stroke-width='10' stroke-linecap='round' opacity='{1-k:.2f}'/>")
        # destellos que flotan
        for i in range(10):
            ph = i * 0.63
            yy = TOAD_Y - 200 - ((t - REVELACION) * 120 + i * 40) % 380
            xx = 900 + 150 * math.sin(i * 2.1 + t)
            a = 0.8 * (0.5 + 0.5 * math.sin(t * 6 + ph))
            w.append(f"<path d='M {xx:.0f} {yy-14:.0f} L {xx+5:.0f} {yy-4:.0f} L {xx+14:.0f} {yy:.0f} L {xx+5:.0f} {yy+4:.0f} L {xx:.0f} {yy+14:.0f} L {xx-5:.0f} {yy+4:.0f} L {xx-14:.0f} {yy:.0f} L {xx-5:.0f} {yy-4:.0f} Z' fill='#fff6b0' opacity='{a:.2f}'/>")

    # pétalos que caen (siempre)
    for px, py0, pr, ph, sp in PETALOS:
        yy = 1000 + ((py0 * 920 + t * sp) % 920)
        xx = (px + 40 * math.sin(t * 1.3 + ph) - t * 20) % W
        w.append(f"<ellipse cx='{xx:.0f}' cy='{yy:.0f}' rx='{pr:.0f}' ry='{pr*0.55:.0f}' fill='#ffb3c7' stroke='{INK}' stroke-width='3' transform='rotate({(t*90 + ph*57) % 360:.0f} {xx:.0f} {yy:.0f})'/>")

    cont = "".join(w)
    cont = f"<g transform='translate(900,1640) scale({zr:.4f}) translate(-900,-1640)'>{cont}</g>"
    cont = f"<g transform='translate(540,1500) scale({z0:.4f}) translate(-540,-1500)'>{cont}</g>"
    s.append(cont)
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
