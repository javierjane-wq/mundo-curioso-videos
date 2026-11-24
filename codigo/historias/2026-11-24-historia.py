"""Episodio: "Viaje al mundo de los insectos" con Bellotín, una bellota voladora con hélice (original).

Datos (verificados el 24-11-2026):
- Las libélulas cazan al vuelo interceptando a su presa (calculan hacia dónde va) y en los
  experimentos atrapan hasta el 90-95 % de las presas que persiguen; mueven cada una de sus cuatro
  alas por separado y pueden quedarse quietas en el aire y volar hacia atrás (Combes et al. 2013,
  Integrative and Comparative Biology / J. Exp. Biol., Harvard-UC Davis; National Wildlife Federation).
- La abeja de la miel comunica dónde hay flores con la danza del meneo (waggle dance): el ángulo de
  la carrera respecto a la vertical del panal es el ángulo de las flores respecto al sol, y la
  duración del meneo indica la distancia. Karl von Frisch lo descubrió y ganó el Premio Nobel de
  Medicina en 1973 (Conferencia Nobel de von Frisch; NC State Extension «Honey Bee Dance Language»).
- El escarabajo bombardero mezcla en su abdomen dos sustancias (hidroquinonas y agua oxigenada) con
  enzimas y dispara un chorro irritante a unos 100 °C, en pulsos: unas 500 explosiones por segundo
  (Arndt et al., Science 2015; MIT News; National Geographic; Natural History Museum de Londres).
- Las cigarras periódicas (Magicicada, este de EE. UU.) pasan 13 o 17 años bajo tierra como ninfas
  chupando savia de las raíces y salen todas a la vez: hasta 1,5 millones por acre (unos 4.000 m²,
  más o menos medio campo de fútbol) (Purdue Extension Entomology; University of Arkansas;
  UConn «Periodical cicadas»; USDA Forest Service).
- El escarabajo pelotero africano (Scarabaeus satyrus) rueda su bola en línea recta de noche
  guiándose por la franja de luz de la Vía Láctea; se comprobó en el planetario de Johannesburgo y es
  el primer animal conocido que usa la galaxia para orientarse (Dacke et al., Current Biology 2013;
  National Geographic; Science News).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-24-historia"
TITULO = "Viaje al mundo de los insectos"
VOZ = "em_santa"
VELOCIDAD = 0.95
MUSICA = 78

W, H = 1920, 1080
rng = np.random.default_rng(24)
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, 760), rng.uniform(1.5, 4.0), rng.uniform(0, 6)) for _ in range(150)]
# estrellas concentradas en la franja de la Vía Láctea (de abajo a la izquierda a arriba a la derecha)
VIA = []
for _ in range(260):
    u = rng.uniform(0, 1); d = rng.normal(0, 55)
    x0, y0 = lerp(-100, 2020, u), lerp(720, 60, u)
    VIA.append((x0 + d * 0.3, y0 + d, rng.uniform(1.2, 3.2), rng.uniform(0, 6)))
HOJAS = [(rng.uniform(0, W), rng.uniform(800, 1060), rng.uniform(0, 180), rng.uniform(0.7, 1.3),
          ["#c0702f", "#d9a03f", "#8a5a2b", "#a8452a", "#6f8a3a"][i % 5]) for i in range(46)]
PIEDRAS = [(rng.uniform(80, 1840), rng.uniform(470, 1040), rng.uniform(18, 46)) for _ in range(22)]


# ================= piezas comunes =================
def cielo(top, bot, id_="cie"):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def nube(x, y, sc, col="#fff"):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def nubes(t, cols="#fff"):
    s = []
    for i, (cx, cy, sc) in enumerate([(300, 150, 1.2), (950, 110, 0.9), (1650, 190, 1.0)]):
        dx = (cx + t * 14 * (1 + i * 0.3)) % 2300 - 300
        s.append(nube(dx, cy, sc, cols))
    return "".join(s)


def sol(cx, cy, r, op=1.0):
    return (f"<g opacity='{op:.2f}'><circle cx='{cx}' cy='{cy}' r='{r * 2.1:.0f}' fill='#fff3b0' opacity='0.35'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/></g>")


def hierba(y0, t, col="#5fb84a", col2="#3f9a3a", alto=90, paso=26, fase=0.0):
    s = [f"<rect x='0' y='{y0}' width='{W}' height='{H - y0}' fill='{col2}'/>"]
    d = []
    for i in range(int(W / paso) + 2):
        x = i * paso - 10
        h = alto * (0.6 + 0.4 * abs(math.sin(i * 1.7 + fase)))
        sw = 10 * math.sin(t * 1.6 + i * 0.5 + fase)
        d.append(f"M{x - 12} {y0 + 4} Q{x + sw * 0.4:.0f} {y0 - h * 0.5:.0f} {x + sw:.0f} {y0 - h:.0f} Q{x + 4 + sw * 0.4:.0f} {y0 - h * 0.5:.0f} {x + 14} {y0 + 4} Z")
    s.append(f"<path d='{' '.join(d)}' fill='{col}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return "".join(s)


def flor(x, y, s, t, col="#ff6fa5", centro="#ffd23f", tallo=180, fase=0.0):
    sw = 6 * math.sin(t * 1.4 + fase)
    p = "".join(f"<ellipse cx='{36 * math.cos(a):.1f}' cy='{36 * math.sin(a):.1f}' rx='30' ry='20' transform='rotate({math.degrees(a):.0f} {36 * math.cos(a):.1f} {36 * math.sin(a):.1f})' "
                f"fill='{col}' stroke='{INK}' stroke-width='6'/>" for a in [i * 2 * math.pi / 6 for i in range(6)])
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M0 0 Q{sw * 2:.0f} {-tallo / 2} {sw * 3:.0f} {-tallo}' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
            f"<path d='M0 0 Q{sw * 2:.0f} {-tallo / 2} {sw * 3:.0f} {-tallo}' fill='none' stroke='#4caf50' stroke-width='8' stroke-linecap='round'/>"
            f"<path d='M{sw:.0f} {-tallo * 0.4:.0f} q40 -30 70 -10 q-30 30 -70 10 Z' fill='#5fbf4a' stroke='{INK}' stroke-width='5'/>"
            f"<g transform='translate({sw * 3:.0f},{-tallo}) rotate({t * 10 + fase * 30:.0f})'>{p}"
            f"<circle r='24' fill='{centro}' stroke='{INK}' stroke-width='6'/></g></g>")


def destellos(cx, cy, k, n=10, r=220, col="#fff6a8"):
    if k <= 0 or k >= 1:
        return ""
    s = []
    for i in range(n):
        a = i / n * 2 * math.pi
        d = r * (0.4 + 0.6 * k)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        e = 18 * (1 - k) + 6
        s.append(f"<path d='M{x:.0f} {y - e:.0f} L{x + e * 0.3:.0f} {y:.0f} L{x:.0f} {y + e:.0f} L{x - e * 0.3:.0f} {y:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='2' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def bellotin(x, y, s, t, ang=0.0, guino=False, luz=0.0, mira=(0.0, 0.0), susto=0.0):
    """Bellotín: una bellota voladora con hélice de hoja en el capuchón, dos ojos grandes y un foco."""
    parp = 0.12 if (t % 3.9) < 0.13 or guino else 1.0
    prop = abs(math.sin(t * 22))
    mx, my = mira
    g = [f"<g transform='translate({x:.1f},{y + 8 * math.sin(t * 2.3):.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if luz > 0.01:
        g.append("<defs><linearGradient id='hazb' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#fff6c8' stop-opacity='0.85'/>"
                 "<stop offset='1' stop-color='#fff6c8' stop-opacity='0'/></linearGradient></defs>"
                 f"<path d='M100 -20 L700 -210 L700 230 Z' fill='url(#hazb)' opacity='{luz:.2f}'/>")
    # hélice de hoja
    g.append(f"<rect x='-7' y='-170' width='14' height='52' rx='6' fill='#7a4a22' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='{-50 * prop:.1f}' cy='-172' rx='{8 + 52 * prop:.1f}' ry='14' fill='#7fd14a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='{50 * prop:.1f}' cy='-172' rx='{8 + 52 * prop:.1f}' ry='14' fill='#6cc03c' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='0' cy='-172' r='10' fill='#a0682e' stroke='{INK}' stroke-width='5'/>")
    # fruto (la nuez de la bellota)
    g.append(f"<path d='M-92 -50 Q-104 50 -30 112 Q0 136 30 112 Q104 50 92 -50 Z' fill='#e3a24f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-62 -30 Q-74 40 -30 90' fill='none' stroke='#f6c97f' stroke-width='14' stroke-linecap='round' opacity='0.8'/>")
    g.append(f"<path d='M0 128 L0 146' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    # ojos
    for ex in (-34, 34):
        g.append(f"<g transform='translate({ex},4) scale(1,{parp})'><ellipse rx='26' ry='{30 + 6 * susto:.0f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{4 + 8 * mx:.1f}' cy='{4 + 8 * my:.1f}' r='13' fill='{INK}'/><circle cx='{-1 + 8 * mx:.1f}' cy='{-2 + 8 * my:.1f}' r='5' fill='#fff'/></g>")
    g.append(f"<ellipse cx='-60' cy='46' rx='14' ry='9' fill='#ff8f7a' opacity='0.7'/><ellipse cx='60' cy='46' rx='14' ry='9' fill='#ff8f7a' opacity='0.7'/>")
    if susto > 0.5:
        g.append(f"<ellipse cx='0' cy='62' rx='14' ry='16' fill='#7a2a1a' stroke='{INK}' stroke-width='5'/>")
    else:
        g.append(f"<path d='M-22 54 Q0 74 22 54' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # capuchón con escamas
    g.append(f"<path d='M-112 -40 Q-118 -128 0 -132 Q118 -128 112 -40 Q60 -26 0 -28 Q-60 -26 -112 -40 Z' fill='#9a6430' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for fila, yy in enumerate((-108, -84, -58)):
        n = 5 + fila
        for i in range(n):
            xx = -88 + fila * -6 + i * (176 + fila * 12) / (n - 1)
            g.append(f"<path d='M{xx - 13:.0f} {yy} Q{xx:.0f} {yy + 14} {xx + 13:.0f} {yy}' fill='none' stroke='#6e4420' stroke-width='5' stroke-linecap='round'/>")
    # foco
    g.append(f"<circle cx='100' cy='-40' r='16' fill='{mix('#8a8f96', '#fff3a8', luz)}' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def via_lactea(t, op=1.0, brillo=0.0):
    a = op * (0.55 + 0.45 * brillo)
    s = [f"<g opacity='{a:.2f}'>"]
    for wdt, o in ((330, 0.07), (210, 0.09), (110, 0.12), (40, 0.16)):
        s.append(f"<path d='M-100 720 Q900 420 2020 60' fill='none' stroke='#d9d2ff' stroke-width='{wdt}' stroke-linecap='round' opacity='{o + 0.06 * brillo:.2f}'/>")
    s.append(f"<path d='M-100 740 Q900 450 2020 90' fill='none' stroke='#1a1440' stroke-width='18' opacity='0.35'/>")
    for x, y, r, f in VIA:
        tw = 0.55 + 0.45 * math.sin(t * 3 + f)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * (1 + 0.4 * brillo):.1f}' fill='#fff' opacity='{tw:.2f}'/>")
    s.append("</g>")
    return "".join(s)


def estrellas(t, op=1.0):
    return "".join(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{op * (0.5 + 0.5 * math.sin(t * 2.2 + f)):.2f}'/>" for x, y, r, f in ESTRELLAS)


def noche_sabana(t, brillo=0.0, op_via=1.0):
    s = [cielo("#070a2a", "#2a2560", "noc"), estrellas(t), via_lactea(t, op_via, brillo)]
    # luna creciente
    s.append(f"<circle cx='1700' cy='170' r='50' fill='#fff4c8' stroke='{INK}' stroke-width='6'/><circle cx='1722' cy='155' r='46' fill='#141440'/>")
    # acacia
    s.append(f"<path d='M1480 860 L1500 640 Q1470 600 1400 590 M1500 650 Q1540 600 1620 585' fill='none' stroke='#0c0a1a' stroke-width='26' stroke-linecap='round'/>")
    s.append(f"<path d='M1290 600 Q1350 520 1520 530 Q1700 515 1760 590 Q1600 620 1520 610 Q1400 625 1290 600 Z' fill='#0c0a1a'/>")
    # suelo (dunas de arena de noche)
    s.append(f"<path d='M0 840 Q300 800 640 830 T1280 820 T1920 835 L1920 1080 L0 1080 Z' fill='#4a3a5a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 930 Q400 900 900 925 T1920 920 L1920 1080 L0 1080 Z' fill='#3a2c48'/>")
    for i in range(14):
        gx = i * 145 + 30
        s.append(f"<path d='M{gx} 838 l-10 -34 M{gx + 8} 838 l4 -42 M{gx + 16} 838 l14 -30' stroke='#2a2038' stroke-width='6' stroke-linecap='round'/>")
    return "".join(s)


def pelotero(x, y, s, t, rueda=1.0, encima=0.0, gira=0.0, ojo=1.0):
    """Escarabajo pelotero empujando su bola con las patas traseras, cabeza abajo (va hacia la derecha).
    encima > 0.5: subido sobre la bola mirando al cielo; gira = ángulo de giro (cambio de sentido)."""
    rb = 62
    halo = f"<ellipse cx='{x + 30:.0f}' cy='{y - 90:.0f}' rx='190' ry='150' fill='#b8a8ff' opacity='0.16'/>"
    ang_bola = (x * 1.4) % 360
    bola = (f"<g transform='translate({x + 70:.1f},{y - rb:.1f}) rotate({ang_bola:.0f})'>"
            f"<circle r='{rb}' fill='#7a5230' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-40 -20 q20 -14 40 0 M5 22 q18 -10 34 4 M-30 30 q10 -8 20 0 M10 -40 q12 6 18 18' fill='none' stroke='#5a3a20' stroke-width='7' stroke-linecap='round'/></g>")
    parp = 0.15 if (t % 3.4) < 0.13 else 1

    def cuerpo(patas):
        return (f"{patas}"
                f"<path d='M-70 -6 Q-60 -62 10 -64 Q78 -62 80 -10 Q70 20 0 22 Q-60 20 -70 -6 Z' fill='#2a2440' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                f"<path d='M-40 -40 Q0 -58 40 -44' fill='none' stroke='#8a8ad0' stroke-width='9' stroke-linecap='round' opacity='{0.6 * ojo:.2f}'/>"
                f"<path d='M5 -62 L5 18' stroke='#3a3550' stroke-width='5'/>"
                f"<path d='M-70 -6 Q-100 -28 -112 -6 Q-118 12 -92 18 Q-76 18 -70 -6 Z' fill='#2a2638' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                f"<path d='M-112 -6 l-14 -8 M-114 4 l-16 2 M-108 14 l-12 10' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
                f"<g transform='translate(-88,-8) scale(1,{parp})'><circle r='8' fill='#cfd6ff'/><circle cx='-2' r='4' fill='{INK}'/></g>")

    if encima > 0.5:
        sx = math.cos(gira)
        patas = "".join(f"<path d='M{px} 10 l{dx} 36' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>" for px, dx in ((-40, -14), (0, 0), (40, 14)))
        b = (f"<g transform='translate({x + 70:.1f},{y - 2 * rb - 30:.1f}) scale({0.75 * sx:.3f},0.75) rotate(-12)'>"
             + cuerpo(patas) + "</g>")
        return f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f}) translate({-x:.1f},{-y:.1f})'>{halo}{bola}{b}</g>"
    w = 14 * math.sin(t * 10) * rueda
    patas = (f"<path d='M-60 10 L{-90 + w:.0f} 60' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
             f"<path d='M-10 16 L{-20 - w:.0f} 66' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
             f"<path d='M40 -10 L{88 + w * 0.5:.0f} {-30 - w:.0f}' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
             f"<path d='M60 10 L{100 - w * 0.5:.0f} {20 + w:.0f}' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    b = f"<g transform='translate({x - 20:.1f},{y - 66:.1f}) rotate(-38)'>{cuerpo(patas)}</g>"
    return f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f}) translate({-x:.1f},{-y:.1f})'>{halo}{bola}{b}</g>"


def termometro(x, y, k, op):
    if op <= 0:
        return ""
    alto = 300
    return (f"<g transform='translate({x},{y})' opacity='{op:.2f}'>"
            f"<rect x='-26' y='{-alto}' width='52' height='{alto + 10}' rx='26' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-12' y='{-alto * k + 10:.0f}' width='24' height='{alto * k:.0f}' fill='#e8382f'/>"
            f"<circle cy='40' r='50' fill='#e8382f' stroke='{INK}' stroke-width='{LW}'/>"
            + "".join(f"<line x1='26' y1='{-alto + 40 + i * 50}' x2='6' y2='{-alto + 40 + i * 50}' stroke='{INK}' stroke-width='5'/>" for i in range(5))
            + "</g>")


# ================= capítulo 0: gancho =================
def jardin(t, fase=0.0):
    s = [cielo("#7fd3ff", "#e3f7ff", "jar"), sol(1650, 170, 70), nubes(t)]
    s.append(f"<path d='M0 760 Q400 700 900 740 T1920 720 L1920 1080 L0 1080 Z' fill='#8fd36a' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (fx, fy, sc, col) in enumerate([(220, 900, 1.1, "#ff6fa5"), (520, 880, 0.9, "#ffd23f"), (1380, 900, 1.2, "#b98cff"),
                                          (1640, 880, 0.95, "#ff8a3d"), (1840, 910, 1.0, "#ff6fa5"), (80, 930, 0.8, "#b98cff")]):
        s.append(flor(fx, fy, sc, t, col, "#ffd23f" if col != "#ffd23f" else "#ff8a3d", 230, i * 1.3 + fase))
    s.append(hierba(960, t, alto=110, fase=fase))
    return "".join(s)


def esc_intro(t, dur, m):
    noche = 1 - seg(t, m[1] - 0.4, m[1] + 0.2)
    s = []
    if noche > 0:
        s.append(f"<g opacity='{1:.2f}'>" + noche_sabana(t, brillo=0.5 + 0.5 * math.sin(t * 1.5)) + "</g>")
        s.append(pelotero(lerp(450, 1150, seg(t, 0, m[1])), 860, 1.6, t))
        # estrella fugaz
        k = seg(t, 0.8, 2.0)
        if 0 < k < 1:
            fx, fy = lerp(600, 1300, k), lerp(120, 330, k)
            s.append(f"<path d='M{fx:.0f} {fy:.0f} L{fx - 220:.0f} {fy - 66:.0f}' stroke='#fff' stroke-width='6' stroke-linecap='round' opacity='{1 - k:.2f}'/>"
                     f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='9' fill='#fff'/>")
    if noche < 1:
        enc = seg(t, m[2] - 0.2, m[2] + 1.6)          # nos hacemos diminutos: la cámara se acerca a la hierba
        z = lerp(1.0, 1.7, enc)
        cuerpo = jardin(t)
        s.append(f"<g opacity='{1 - noche:.2f}'><g transform='translate(960,1000) scale({z:.3f}) translate(-960,-1000)'>{cuerpo}</g></g>")
        llega = seg(t, m[1] - 0.2, m[1] + 2.2)
        sale = seg(t, dur - 1.6, dur)
        bx = lerp(-250, 820, llega) + lerp(0, 1400, sale)
        by = 520 + lerp(0, -40, sale)
        sc = lerp(1.05, 0.72, enc)
        s.append(destellos(bx, by, seg(t, m[2] + 0.2, m[2] + 1.8), 12, 260))
        s.append(bellotin(bx, by, sc, t, ang=lerp(-10, 6, llega) + 10 * sale, guino=(m[3] + 0.3 < t < m[3] + 0.7), mira=(0.4, -0.2)))
        # mariposa que revolotea
        mx = (t * 140) % 2300 - 200; my = 420 + 60 * math.sin(t * 1.3)
        a = abs(math.sin(t * 12))
        s.append(f"<g transform='translate({mx:.0f},{my:.0f})'><g transform='scale({0.3 + 0.7 * a:.2f},1)'>"
                 f"<path d='M0 0 Q-60 -70 -70 -10 Q-60 30 0 0 Q60 30 70 -10 Q60 -70 0 0 Z' fill='#ffb347' stroke='{INK}' stroke-width='5'/></g>"
                 f"<rect x='-5' y='-20' width='10' height='40' rx='5' fill='{INK}'/></g>")
    return "".join(s)


# ================= capítulo 1: la libélula =================
def junco(x, base, alto, t, fase):
    sw = 14 * math.sin(t * 1.2 + fase)
    tx, ty = x + sw, base - alto
    return (f"<path d='M{x} {base} Q{x + sw * 0.5:.0f} {base - alto / 2} {tx:.0f} {ty:.0f}' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
            f"<path d='M{x} {base} Q{x + sw * 0.5:.0f} {base - alto / 2} {tx:.0f} {ty:.0f}' fill='none' stroke='#6aa83a' stroke-width='7' stroke-linecap='round'/>"
            f"<rect x='{tx - 15:.0f}' y='{ty + 10:.0f}' width='30' height='90' rx='15' fill='#8a5a2b' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M{tx:.0f} {ty + 10:.0f} L{tx + sw * 0.2:.0f} {ty - 30:.0f}' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")


def nenufar(x, y, s, flor_=False):
    g = (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f},{s * 0.42:.2f})'>"
         f"<path d='M0 0 L80 -30 A85 85 0 1 1 80 30 Z' fill='#4caf50' stroke='{INK}' stroke-width='12'/>"
         f"<path d='M0 0 L-60 -40 M0 0 L-70 20 M0 0 L10 70' stroke='#2e8b3a' stroke-width='8'/></g>")
    if flor_:
        g += (f"<g transform='translate({x - 10:.0f},{y - 22:.0f}) scale({s:.2f})'>"
              + "".join(f"<path d='M0 0 Q{-16 + 32 * (i / 4):.0f} -60 {-34 + 68 * (i / 4):.0f} -6 Z' fill='#ff9ac2' stroke='{INK}' stroke-width='5'/>" for i in range(5))
              + f"<circle cx='0' cy='-12' r='12' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")
    return g


def libelula(x, y, s, t, ang=0.0, aleteo=1.0):
    """Libélula vista desde arriba: dos grandes ojos, tórax, abdomen largo y 4 alas que se mueven por separado."""
    a1 = 0.35 + 0.65 * abs(math.sin(t * 26))
    a2 = 0.35 + 0.65 * abs(math.sin(t * 26 + 1.4))
    if aleteo < 0.5:
        a1 = a2 = 1.0

    def ala(cx, cy, rot, largo, k):
        return (f"<g transform='translate({cx},{cy}) rotate({rot}) scale(1,{k:.2f})'>"
                f"<path d='M0 0 Q30 -{largo * 0.25:.0f} 26 -{largo:.0f} Q6 -{largo + 20:.0f} -14 -{largo * 0.8:.0f} Q-18 -{largo * 0.3:.0f} 0 0 Z' fill='#e6f7ff' fill-opacity='0.55' stroke='{INK}' stroke-width='5'/>"
                f"<path d='M4 -10 L12 -{largo * 0.85:.0f} M-6 -{largo * 0.3:.0f} L18 -{largo * 0.5:.0f}' stroke='#7fb7d6' stroke-width='3'/></g>")
    seg_ = "".join(f"<line x1='{-60 - i * 34}' y1='-11' x2='{-60 - i * 34}' y2='11' stroke='{INK}' stroke-width='4'/>" for i in range(7))
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            + ala(20, -12, -8, 190, a1) + ala(-14, -12, -22, 175, a2)
            + f"<g transform='scale(1,-1)'>" + ala(20, -12, -8, 190, a1) + ala(-14, -12, -22, 175, a2) + "</g>"
            + f"<path d='M-30 -12 L-300 -8 Q-318 0 -300 8 L-30 12 Z' fill='#2f8fe0' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>{seg_}"
            f"<ellipse cx='0' cy='0' rx='44' ry='26' fill='#2b7fd0' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-20 -8 L20 -8 M-20 8 L20 8' stroke='#5ab4ff' stroke-width='5'/>"
            f"<circle cx='56' cy='-20' r='24' fill='#4fd36b' stroke='{INK}' stroke-width='6'/><circle cx='56' cy='20' r='24' fill='#4fd36b' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='62' cy='-26' r='7' fill='#e9fff0'/><circle cx='62' cy='14' r='7' fill='#e9fff0'/>"
            f"<path d='M78 -8 Q88 0 78 8' fill='none' stroke='{INK}' stroke-width='5'/></g>")


def mosquito(x, y, s, t, op=1.0):
    a = abs(math.sin(t * 40))
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})' opacity='{op:.2f}'>"
            f"<ellipse cx='-6' cy='-26' rx='{10 + 8 * a:.0f}' ry='26' fill='#eef8ff' fill-opacity='0.7' stroke='{INK}' stroke-width='4' transform='rotate(-30 -6 -26)'/>"
            f"<path d='M-10 0 L-60 6 M-4 4 L-30 44 M4 4 L10 46 M10 2 L44 40' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>"
            f"<ellipse cx='-30' cy='4' rx='30' ry='7' fill='#6a6a72' stroke='{INK}' stroke-width='4'/>"
            f"<ellipse cx='6' cy='0' rx='12' ry='10' fill='#55555e' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='22' cy='-2' r='8' fill='#44444c' stroke='{INK}' stroke-width='4'/>"
            f"<path d='M28 0 L56 8' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")


def esc_libelula(t, dur, m):
    s = [cielo("#8fd8ff", "#e8f8ff", "lib"), sol(1700, 150, 60), nubes(t * 0.6)]
    s.append(f"<path d='M0 560 Q200 470 420 520 Q650 450 900 520 Q1150 460 1400 515 Q1650 470 1920 520 L1920 640 L0 640 Z' fill='#5aa84a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='0' y='620' width='{W}' height='{H - 620}' fill='#3aa0c8' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='0' y='760' width='{W}' height='{H - 760}' fill='#2f8ab4'/>")
    for i in range(12):
        rx = (i * 173 + t * 30) % 2000 - 40; ry = 680 + (i * 61) % 340
        s.append(f"<path d='M{rx:.0f} {ry} q40 -12 80 0' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
    s.append(nenufar(560, 860, 1.0, True)); s.append(nenufar(1320, 960, 1.2)); s.append(nenufar(980, 720, 0.7))
    for i, (jx, al) in enumerate([(70, 620), (130, 520), (190, 680), (1720, 560), (1790, 660), (1860, 500)]):
        s.append(junco(jx, 1080, al, t, i * 1.1))
    # Bellotín observa
    s.append(bellotin(330 + 15 * math.sin(t * 0.7), 470, 0.62, t, mira=(1, 0.2)))
    # la libélula: llega, vuela adelante y atrás, se queda quieta, intercepta
    llega = seg(t, 0.3, 2.6)
    lx = lerp(2200, 1150, llega); ly = 470
    adel = seg(t, m[2] - 0.2, m[2] + 1.0) - seg(t, m[2] + 1.0, m[2] + 2.4)    # adelante y atrás
    lx += 220 * adel * math.sin((t - m[2]) * 2.6)
    ly += 14 * math.sin(t * 2)
    # el mosquito cruza y la libélula le corta el paso
    mq = seg(t, m[3] + 0.2, m[4] + 1.0)
    caza = seg(t, m[3] + 1.6, m[4] + 0.8)
    pre = seg(t, m[3] + 0.6, m[3] + 1.4)
    mx_, my_ = lerp(700, 1500, mq), lerp(320, 640, mq)
    ix, iy = 1300, 560          # punto de intercepción calculado
    if t > m[3]:
        lx = lerp(lx, ix, caza); ly = lerp(ly, iy, caza)
    ang = 22 * caza * (1 - seg(t, m[4] + 0.8, m[4] + 2.0)) + 8 * math.sin(t * 1.5) * (1 - caza)
    if pre > 0 and t < m[4] + 1.5:
        op = pre * (1 - seg(t, m[4] + 0.6, m[4] + 1.5))
        s.append(f"<path d='M700 320 L{ix} {iy}' stroke='#ffffff' stroke-width='8' stroke-dasharray='4 22' stroke-linecap='round' opacity='{op:.2f}'/>")
        s.append(f"<circle cx='{ix}' cy='{iy}' r='{38 + 6 * math.sin(t * 8):.0f}' fill='none' stroke='#ffe14d' stroke-width='8' stroke-dasharray='18 12' opacity='{op:.2f}'/>")
    atrapado = t > m[4] + 0.75
    if m[3] + 0.2 < t and not atrapado:
        s.append(mosquito(mx_, my_, 0.9, t))
    s.append(libelula(lx, ly, 1.2, t, ang=180 + ang))
    s.append(destellos(ix + 60, iy, seg(t, m[4] + 0.7, m[4] + 2.2), 12, 230))
    return "".join(s)


# ================= capítulo 2: la abeja que baila =================
def panal(t, oscuro=0.0):
    s = [f"<rect width='{W}' height='{H}' fill='{mix('#e7a12a', '#6a3f12', oscuro)}'/>"]
    r = 58; dx = r * 1.732; d = []; miel = []; tapa = []
    for fila in range(-1, 14):
        for col in range(-1, 21):
            cx = col * dx + (dx / 2 if fila % 2 else 0); cy = fila * r * 1.5
            pts = " ".join(f"{cx + r * math.cos(math.radians(60 * k + 30)):.0f},{cy + r * math.sin(math.radians(60 * k + 30)):.0f}" for k in range(6))
            h = (fila * 7 + col * 13) % 9
            if h in (0, 4):
                miel.append(f"<polygon points='{pts}' fill='#c97a10'/>")
            elif h == 6:
                tapa.append(f"<polygon points='{pts}' fill='#f6d27a'/>")
            d.append(f"<polygon points='{pts}' fill='none' stroke='#8a5208' stroke-width='9'/>")
    s += miel + tapa + d
    s.append(f"<rect width='{W}' height='{H}' fill='#000' opacity='{0.12 + 0.3 * oscuro:.2f}'/>")
    return "".join(s)


def abeja(x, y, s, t, ang=0.0, menea=0.0, op=1.0):
    """Abeja de la miel vista desde arriba (cabeza hacia arriba en ang=0)."""
    a = 0.6 + 0.4 * abs(math.sin(t * 30))
    w = menea * 14 * math.sin(t * 40)
    patas = "".join(f"<path d='M{sx * 14} {py} l{sx * 34} {py * 0.4 + 10}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>" for sx in (-1, 1) for py in (-14, 0, 14))
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})' opacity='{op:.2f}'>{patas}"
            f"<g transform='rotate({w:.1f} 0 10)'>"
            f"<ellipse cx='0' cy='52' rx='30' ry='44' fill='#ffc93c' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-29 40 Q0 50 29 40 M-27 62 Q0 72 27 62 M-18 82 Q0 90 18 82' fill='none' stroke='{INK}' stroke-width='10'/>"
            f"<path d='M0 96 L0 108' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>"
            f"<ellipse cx='-34' cy='8' rx='{32 * a:.0f}' ry='18' fill='#eaf7ff' fill-opacity='0.75' stroke='{INK}' stroke-width='5' transform='rotate(25 -34 8)'/>"
            f"<ellipse cx='34' cy='8' rx='{32 * a:.0f}' ry='18' fill='#eaf7ff' fill-opacity='0.75' stroke='{INK}' stroke-width='5' transform='rotate(-25 34 8)'/>"
            f"<ellipse cx='0' cy='0' rx='24' ry='22' fill='#a8742c' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='0' cy='-34' r='17' fill='#3a2a1a' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='-11' cy='-36' rx='6' ry='9' fill='#1a1010'/><ellipse cx='11' cy='-36' rx='6' ry='9' fill='#1a1010'/>"
            f"<path d='M-6 -48 Q-14 -70 -26 -76 M6 -48 Q14 -70 26 -76' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def ventana_afuera(cx, cy, r, k, theta):
    """Ventana redonda al exterior: sol arriba, colmena abajo y las flores en el ángulo del baile."""
    if k <= 0:
        return ""
    sc = 0.6 + 0.4 * ease(k)
    hx, hy = 0, r * 0.55
    fx, fy = hx + 250 * math.sin(math.radians(theta)), hy - 250 * math.cos(math.radians(theta))
    flores = "".join(f"<g transform='translate({fx + ox:.0f},{fy + oy:.0f})'>"
                     + "".join(f"<circle cx='{11 * math.cos(a * 1.257):.0f}' cy='{11 * math.sin(a * 1.257):.0f}' r='9' fill='{c}' stroke='{INK}' stroke-width='3'/>" for a in range(5))
                     + f"<circle r='6' fill='#ffd23f'/></g>" for ox, oy, c in ((-26, 6, "#ff6fa5"), (10, -10, "#b98cff"), (30, 16, "#ff6fa5"), (-4, 22, "#ffffff")))
    return (f"<g transform='translate({cx},{cy}) scale({sc:.3f})' opacity='{min(1, k * 2):.2f}'>"
            f"<defs><clipPath id='ven'><circle r='{r}'/></clipPath></defs>"
            f"<g clip-path='url(#ven)'><rect x='{-r}' y='{-r}' width='{2 * r}' height='{2 * r}' fill='#9fe0ff'/>"
            f"<rect x='{-r}' y='{r * 0.3:.0f}' width='{2 * r}' height='{r}' fill='#8fd36a'/>"
            f"<circle cx='0' cy='{-r * 0.62:.0f}' r='34' fill='#ffe066' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M{hx} {hy} L0 {-r * 0.62 + 40:.0f}' stroke='#e8382f' stroke-width='7' stroke-dasharray='14 10'/>"
            f"<path d='M{hx} {hy} L{fx:.0f} {fy:.0f}' stroke='#ffffff' stroke-width='8' stroke-dasharray='14 10'/>"
            f"<path d='M{hx} {hy - 80} A80 80 0 0 1 {hx + 80 * math.sin(math.radians(theta)):.0f} {hy - 80 * math.cos(math.radians(theta)):.0f}' fill='none' stroke='#ffe14d' stroke-width='8'/>"
            f"{flores}"
            f"<path d='M-34 {hy + 30:.0f} Q-40 {hy - 30:.0f} 0 {hy - 40:.0f} Q40 {hy - 30:.0f} 34 {hy + 30:.0f} Z' fill='#f2c14e' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-36 {hy:.0f} L36 {hy:.0f} M-30 {hy - 20:.0f} L30 {hy - 20:.0f}' stroke='#b07d1c' stroke-width='5'/>"
            f"<circle cx='0' cy='{hy + 12:.0f}' r='8' fill='{INK}'/></g>"
            f"<circle r='{r}' fill='none' stroke='#8a5a2b' stroke-width='26'/><circle r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle r='{r + 13}' fill='none' stroke='{INK}' stroke-width='6'/></g>")


def medalla(cx, cy, k, t):
    if k <= 0:
        return ""
    sc = (0.4 + 0.6 * ease(k)) * (1 + 0.03 * math.sin(t * 4))
    return (f"<g transform='translate({cx},{cy}) scale({sc:.3f})' opacity='{min(1, k * 2):.2f}'>"
            f"<path d='M-60 -170 L-20 -40 L20 -40 L60 -170 Z' fill='#3a7bd5' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>"
            f"<path d='M-20 -170 L0 -60 L20 -170 Z' fill='#e8382f'/>"
            f"<circle r='120' fill='#ffcf3a' stroke='{INK}' stroke-width='{LW}'/><circle r='90' fill='none' stroke='#d99a10' stroke-width='10'/>"
            + "".join(f"<ellipse cx='{-62 * math.cos(a):.0f}' cy='{62 * math.sin(a) - 10:.0f}' rx='16' ry='8' fill='#7ac04a' stroke='{INK}' stroke-width='4' transform='rotate({math.degrees(a) + 90:.0f} {-62 * math.cos(a):.0f} {62 * math.sin(a) - 10:.0f})'/>" for a in [i * 0.33 - 0.6 for i in range(6)])
            + "".join(f"<ellipse cx='{62 * math.cos(a):.0f}' cy='{62 * math.sin(a) - 10:.0f}' rx='16' ry='8' fill='#7ac04a' stroke='{INK}' stroke-width='4' transform='rotate({-math.degrees(a) - 90:.0f} {62 * math.cos(a):.0f} {62 * math.sin(a) - 10:.0f})'/>" for a in [i * 0.33 - 0.6 for i in range(6)])
            + f"<path d='M0 -40 L12 -12 L42 -10 L18 8 L26 38 L0 22 L-26 38 L-18 8 L-42 -10 L-12 -12 Z' fill='#fff3a8' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<path d='M-60 -60 Q-40 -90 -10 -96' fill='none' stroke='#fff' stroke-width='10' stroke-linecap='round' opacity='0.6'/></g>")


THETA = 35   # ángulo del baile respecto a la vertical (= ángulo de las flores respecto al sol)


def esc_abeja(t, dur, m):
    s = [panal(t)]
    # obreras que caminan por el panal
    for i, (bx, by, va) in enumerate([(260, 820, 0.6), (1700, 300, -0.5), (1450, 880, 0.4), (520, 260, -0.3), (1200, 180, 0.5)]):
        a = (t * 20 * va + i * 70)
        px = bx + 40 * math.sin(t * va + i); py = by + 30 * math.cos(t * va * 1.3 + i)
        s.append(abeja(px, py, 0.7, t + i, ang=a))
    cx, cy = 880, 600
    L = 260
    th = math.radians(THETA)
    # el baile empieza en la frase 1 y se dibuja su recorrido en la frase 2
    baila = t > m[1] + 1.2
    if t > m[2] - 0.3:
        op = seg(t, m[2] - 0.3, m[2] + 0.6)
        ax, ay = cx - L / 2 * math.sin(th), cy + L / 2 * math.cos(th)
        bx_, by_ = cx + L / 2 * math.sin(th), cy - L / 2 * math.cos(th)
        s.append(f"<g opacity='{op * 0.85:.2f}'><path d='M{ax:.0f} {ay:.0f} L{bx_:.0f} {by_:.0f}' stroke='#fff' stroke-width='10' stroke-dasharray='6 20' stroke-linecap='round'/>"
                 f"<path d='M{bx_:.0f} {by_:.0f} A{L / 2} {L / 2} 0 0 1 {ax:.0f} {ay:.0f} M{bx_:.0f} {by_:.0f} A{L / 2} {L / 2} 0 0 0 {ax:.0f} {ay:.0f}' fill='none' stroke='#fff' stroke-width='7' stroke-dasharray='6 20' stroke-linecap='round' opacity='0.6'/></g>")
    if t > m[3] - 0.3:   # la vertical del panal = el sol; el ángulo = la dirección de las flores
        op = seg(t, m[3] - 0.3, m[3] + 0.6)
        s.append(f"<g opacity='{op:.2f}'><path d='M{cx} {cy + 160} L{cx} {cy - 230}' stroke='#e8382f' stroke-width='8' stroke-dasharray='16 12'/>"
                 f"<path d='M{cx} {cy - 120} A120 120 0 0 1 {cx + 120 * math.sin(th):.0f} {cy - 120 * math.cos(th):.0f}' fill='none' stroke='#ffe14d' stroke-width='10'/>"
                 f"<circle cx='{cx}' cy='{cy - 262}' r='30' fill='#ffe066' stroke='{INK}' stroke-width='6'/></g>")
    # posición de la bailarina en el ocho
    if baila:
        per = 3.2
        f = ((t - m[1] - 1.2) % (2 * per)) / per
        lado = 1 if f < 1 else -1
        f = f % 1
        if f < 0.45:     # carrera recta con meneo
            k = f / 0.45
            px = cx + lerp(-L / 2, L / 2, k) * math.sin(th); py = cy - lerp(-L / 2, L / 2, k) * math.cos(th)
            ang = THETA; men = 1.0
        else:            # vuelta en semicírculo hasta el inicio
            k = (f - 0.45) / 0.55
            phi = math.pi * k * lado
            rr = L / 2
            vx, vy = math.sin(th), -math.cos(th)
            px = cx + rr * (vx * math.cos(phi) + lado * 0 - vy * math.sin(phi) * 1)
            py = cy + rr * (vy * math.cos(phi) + vx * math.sin(phi))
            ang = THETA + math.degrees(phi) + 90 * lado; men = 0.0
    else:
        px, py = lerp(1400, cx, seg(t, 0.3, m[1] + 1.0)), lerp(950, cy, seg(t, 0.3, m[1] + 1.0)); ang = -40; men = 0
    for i, (ox, oy) in enumerate([(-210, -40), (200, 110), (-150, 210), (190, -170)]):   # compañeras que miran
        s.append(abeja(cx + ox, cy + oy, 1.05, t + i * 0.7, ang=math.degrees(math.atan2(px - (cx + ox), -(py - (cy + oy)))), op=0.95))
    s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{120 + 10 * math.sin(t * 6):.0f}' fill='#fff6a8' opacity='{0.25 * float(baila):.2f}'/>")
    s.append(abeja(px, py, 1.5, t, ang=ang, menea=men))
    s.append(ventana_afuera(1500, 600, 230, seg(t, m[3] + 0.2, m[3] + 1.0) * (1 - seg(t, m[4] - 0.2, m[4] + 0.4)), THETA))
    s.append(medalla(1500, 640, seg(t, m[4] + 0.2, m[4] + 1.0), t))
    s.append(destellos(1500, 640, seg(t, m[4] + 0.6, m[4] + 2.2), 12, 250))
    s.append(bellotin(300, 470 + 10 * math.sin(t * 0.9), 0.62, t, mira=(1, 0.3)))
    return "".join(s)


# ================= capítulo 3: el escarabajo bombardero =================
def suelo_bosque(t):
    s = [cielo("#2f6b3a", "#8fbf6a", "bos")]
    for i, (tx, tw) in enumerate([(120, 120), (520, 80), (980, 140), (1460, 100), (1800, 130)]):
        s.append(f"<rect x='{tx}' y='-20' width='{tw}' height='820' fill='#6b4a2e' stroke='{INK}' stroke-width='{LW}' opacity='0.85'/>"
                 f"<path d='M{tx + tw * 0.3:.0f} 100 l0 120 M{tx + tw * 0.6:.0f} 300 l0 160' stroke='#4a3220' stroke-width='8' stroke-linecap='round'/>")
    for i in range(8):   # rayos de luz
        x = 100 + i * 250 + 30 * math.sin(t * 0.3 + i)
        s.append(f"<path d='M{x:.0f} 0 L{x + 70:.0f} 0 L{x + 230:.0f} 800 L{x + 120:.0f} 800 Z' fill='#fffbd0' opacity='{0.10 + 0.05 * math.sin(t * 0.8 + i):.2f}'/>")
    s.append(f"<path d='M0 790 Q480 760 960 790 T1920 780 L1920 1080 L0 1080 Z' fill='#7a5233' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, a, sc, c in HOJAS:
        s.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({a:.0f}) scale({sc:.2f})'><path d='M-40 0 Q0 -24 40 0 Q0 24 -40 0 Z' fill='{c}' stroke='{INK}' stroke-width='5'/>"
                 f"<path d='M-36 0 L36 0' stroke='{mix(c, '#000000', 0.3)}' stroke-width='4'/></g>")
    # setas
    for mx, my, sc in ((1720, 800, 1.1), (1600, 815, 0.7)):
        s.append(f"<g transform='translate({mx},{my}) scale({sc})'><rect x='-24' y='-110' width='48' height='110' rx='20' fill='#f6efe0' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M-110 -100 Q-100 -200 0 -205 Q100 -200 110 -100 Z' fill='#e8382f' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='-50' cy='-140' r='14' fill='#fff'/><circle cx='20' cy='-170' r='12' fill='#fff'/><circle cx='60' cy='-125' r='10' fill='#fff'/></g>")
    return "".join(s)


def bombardero(x, y, s, t, apunta=0.0, anda=0.0):
    """Escarabajo bombardero de perfil (mira a la derecha): cabeza y tórax naranjas, élitros azul oscuro."""
    w = 10 * math.sin(t * 12) * anda
    patas = "".join(f"<path d='M{px} 8 L{px + 22 + (w if i % 2 else -w):.0f} 32 L{px + 8 + (w if i % 2 else -w):.0f} 62' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>"
                    f"<path d='M{px} 8 L{px + 22 + (w if i % 2 else -w):.0f} 32 L{px + 8 + (w if i % 2 else -w):.0f} 62' fill='none' stroke='#e8862f' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>"
                    for i, px in enumerate((-80, 0, 70)))
    ant = "".join(f"<circle cx='{196 + i * 12 + 4 * math.sin(t * 3 + i * 0.4):.0f}' cy='{-40 - i * 11:.0f}' r='7' fill='#e8862f' stroke='{INK}' stroke-width='3'/>" for i in range(7))
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
            f"<ellipse cx='0' cy='66' rx='170' ry='12' fill='#000' opacity='0.2'/>{patas}"
            f"<g transform='rotate({-apunta * 12:.1f} -130 0)'>"
            f"<path d='M-150 4 Q-150 -96 -20 -98 Q86 -96 96 -26 L96 10 Q0 30 -150 4 Z' fill='#1f3a8a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-120 -40 Q-40 -86 60 -64 M-130 -12 Q-40 -50 80 -30' fill='none' stroke='#14286a' stroke-width='6'/>"
            f"<path d='M-90 -70 Q-30 -94 30 -84' fill='none' stroke='#7fa8ff' stroke-width='12' stroke-linecap='round' opacity='0.7'/>"
            f"<path d='M-150 4 Q-170 10 -168 -10 Q-162 -22 -150 -20' fill='#e8862f' stroke='{INK}' stroke-width='6'/></g>"
            f"<path d='M90 -44 Q150 -56 160 -14 Q160 14 90 14 Z' fill='#e8862f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M150 -30 Q206 -40 214 0 Q210 22 156 16 Z' fill='#f09a3a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<circle cx='190' cy='-12' r='11' fill='{INK}'/><circle cx='186' cy='-16' r='4' fill='#fff'/>"
            f"<path d='M212 8 l18 6 M210 14 l14 14' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>{ant}</g>")


def hormiga(x, y, s, t, anda=1.0, dirx=1, susto=0.0):
    """Hormiga de perfil (cabeza a la derecha si dirx=1): cabeza con mandíbulas y antenas acodadas,
    tórax con 6 patas, cintura estrecha y gáster."""
    w = 12 * math.sin(t * 16) * anda
    patas = "".join(f"<path d='M{px} 0 L{px + 20 + (w if i % 2 else -w):.0f} 26 L{px + 10 + (w if i % 2 else -w):.0f} 56' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>" for i, px in enumerate((-20, 0, 20)))
    gotas = "".join(f"<path d='M{60 + i * 22} {-70 - i * 8} q-8 14 0 20 q8 -6 0 -20 Z' fill='#9fe0ff' stroke='{INK}' stroke-width='3'/>" for i in range(3)) if susto > 0.5 else ""
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>{patas}"
            f"<ellipse cx='-90' cy='-6' rx='52' ry='36' fill='#a8321e' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-90 -30 Q-80 -20 -100 -4' fill='none' stroke='#d85a3a' stroke-width='6' stroke-linecap='round'/>"
            f"<circle cx='-34' cy='-6' r='12' fill='#8a2616' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='0' cy='-8' rx='32' ry='18' fill='#a8321e' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='56' cy='-20' r='26' fill='#a8321e' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='64' cy='-26' r='{6 + 3 * susto:.0f}' fill='{INK}'/>"
            f"<path d='M78 -8 Q96 -4 92 10 M76 -2 Q88 8 80 16' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M58 -44 L66 -86 L104 -100' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>{gotas}</g>")


def chorro(x0, y0, x1, y1, t, k, pulsos=False):
    if k <= 0:
        return ""
    s = []
    n = 10
    for i in range(n):
        f = ((t * (3.5 if pulsos else 1.6) + i / n) % 1)
        if f > k:
            continue
        cx, cy = lerp(x0, x1, f), lerp(y0, y1, f) - 40 * math.sin(f * math.pi)
        r = 18 + 50 * f
        on = 1.0 if not pulsos else (0.55 + 0.45 * math.sin(t * 60 + i * 2))
        s.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r:.0f}' fill='{mix('#fff8d0', '#ffd23f', f)}' stroke='{INK}' stroke-width='4' opacity='{0.85 * (1 - f * 0.7) * on:.2f}'/>")
    return "".join(s)


def esc_bombardero(t, dur, m):
    s = [suelo_bosque(t)]
    bx, by = 1180, 760
    dispara = seg(t, m[2] + 1.4, m[2] + 1.8)
    pul = t > m[3]
    huye = seg(t, m[4] - 0.4, m[4] + 2.0)
    hx = lerp(-200, 620, seg(t, 0.3, m[2] + 1.0)) - lerp(0, 1100, huye)
    s.append(hormiga(hx, 782, 1.25, t, anda=1.0 if (t < m[2] + 1.0 or huye > 0) else 0.2, dirx=1 if huye == 0 else -1,
                     susto=float(t > m[2] + 1.6)))
    s.append(bombardero(bx, by, 1.15, t, apunta=seg(t, m[2] + 0.8, m[2] + 1.4) * (1 - seg(t, m[4] + 1.0, m[4] + 2.0)), anda=0.0))
    activo = dispara * (1 - seg(t, m[4] + 0.6, m[4] + 1.6))
    s.append(chorro(bx - 195, by - 40, 760, 690, t, activo, pulsos=pul))
    if dispara > 0 and t < m[2] + 2.6:   # ¡pum!
        k = seg(t, m[2] + 1.4, m[2] + 2.6)
        s.append(f"<path transform='translate({bx - 200},{by - 40}) scale({0.6 + 0.8 * k:.2f})' d='M0 -70 L18 -22 L66 -36 L32 4 L64 44 L14 30 L0 76 L-14 30 L-64 44 L-32 4 L-66 -36 L-18 -22 Z' "
                 f"fill='#ffe14d' stroke='{INK}' stroke-width='6' opacity='{1 - k:.2f}'/>")
    if pul:   # pequeñas explosiones seguidas
        for i in range(5):
            f = ((t * 7 + i / 5) % 1)
            s.append(f"<circle cx='{bx - 200:.0f}' cy='{by - 40:.0f}' r='{20 + 60 * f:.0f}' fill='none' stroke='#fff3a8' stroke-width='6' opacity='{(1 - f) * activo:.2f}'/>")
    s.append(termometro(1500, 640, seg(t, m[2] + 1.6, m[2] + 3.6), seg(t, m[2] + 1.4, m[2] + 2.0) * (1 - seg(t, m[3] + 2.5, m[3] + 3.2))))
    s.append(bellotin(360, 440 + 10 * math.sin(t), 0.6, t, mira=(1, 0.5), susto=float(m[2] + 1.5 < t < m[3] + 1.0)))
    return "".join(s)


# ================= capítulo 4: la cigarra bajo tierra =================
SUP = 400   # línea del suelo


def ninfa(x, y, s, t, ang=0.0, op=1.0, piel=False):
    """Ninfa de cigarra de perfil (cabeza a la derecha): cuerpo pardo jorobado, patas delanteras excavadoras."""
    w = 6 * math.sin(t * 3)
    col = "#c89a5a" if not piel else "#e3c28a"
    st = "stroke-dasharray='1 0'" if not piel else "stroke-dasharray='10 6'"
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})' opacity='{op:.2f}'>"
            f"<path d='M-20 20 L-40 56 M10 24 L0 60' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
            f"<path d='M-110 0 Q-110 -40 -40 -44 L20 -40 Q30 30 -40 34 Q-100 34 -110 0 Z' fill='{col}' stroke='{INK}' stroke-width='7' {st}/>"
            + "".join(f"<path d='M{-90 + i * 22} -36 Q{-84 + i * 22} 0 {-90 + i * 22} 30' fill='none' stroke='#8a6430' stroke-width='4'/>" for i in range(4))
            + f"<path d='M10 -44 Q60 -80 90 -30 Q96 10 20 24 Z' fill='{mix(col, '#a07438', 0.4)}' stroke='{INK}' stroke-width='7' {st}/>"
            f"<path d='M40 -60 Q60 -60 70 -44' fill='none' stroke='#6e4a20' stroke-width='6'/>"
            f"<circle cx='96' cy='-8' r='22' fill='{col}' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='104' cy='-16' r='7' fill='{INK}'/>"
            f"<path d='M70 18 L{100 + w:.0f} 40 L{122 + w:.0f} 26 M{100 + w:.0f} 40 L{110 + w:.0f} 58' fill='none' stroke='{INK}' stroke-width='11' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M70 18 L{100 + w:.0f} 40 L{122 + w:.0f} 26' fill='none' stroke='{col}' stroke-width='5' stroke-linecap='round'/></g>")


def cigarra(x, y, s, t, ang=0.0, canta=0.0):
    """Cigarra periódica adulta: cuerpo negro, ojos rojos y alas transparentes con venas naranjas."""
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-10 10 L-30 34 M20 12 L14 36' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
            f"<ellipse cx='-10' cy='0' rx='60' ry='22' fill='#1c1c22' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M40 -10 Q-40 -50 -120 -20 Q-60 4 40 6 Z' fill='#f3f8ff' fill-opacity='0.6' stroke='#e8862f' stroke-width='5'/>"
            f"<path d='M30 -6 Q-30 -30 -100 -18' fill='none' stroke='#e8862f' stroke-width='3'/>"
            f"<ellipse cx='44' cy='-2' rx='22' ry='18' fill='#1c1c22' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='58' cy='-10' r='10' fill='#e8382f' stroke='{INK}' stroke-width='4'/>"
            + (f"<path d='M74 -30 q14 20 0 40 M88 -42 q22 32 0 64' fill='none' stroke='#fff' stroke-width='5' stroke-linecap='round' opacity='{canta * (0.5 + 0.5 * math.sin(t * 20)):.2f}'/>" if canta > 0 else "")
            + "</g>")


def arbol_estacion(t, f):
    """Árbol en la superficie; f = fase del año (0 primavera, 0.25 verano, 0.5 otoño, 0.75 invierno)."""
    verde = mix("#5fbf4a", "#3f9a3a", clamp((f - 0.1) * 4))
    if f < 0.45:
        copa = verde; op = 1.0
    elif f < 0.62:
        copa = mix("#3f9a3a", "#ff9a2e", (f - 0.45) / 0.17); op = 1.0
    elif f < 0.72:
        copa = "#ff9a2e"; op = 1 - (f - 0.62) / 0.1
    else:
        copa = "#ffffff"; op = 0.0
    nieve_ = clamp((f - 0.74) * 8) * (1 - clamp((f - 0.95) * 20))
    s = [f"<path d='M1420 {SUP + 10} L1440 200 L1500 200 L1520 {SUP + 10} Z' fill='#7a4f2c' stroke='{INK}' stroke-width='{LW}'/>",
         f"<path d='M1460 290 L1370 220 M1490 260 L1560 200' stroke='{INK}' stroke-width='24' stroke-linecap='round'/>",
         f"<path d='M1460 290 L1370 220 M1490 260 L1560 200' stroke='#7a4f2c' stroke-width='12' stroke-linecap='round'/>"]
    if op > 0:
        for cx, cy, r in ((1350, 210, 95), (1460, 150, 105), (1560, 220, 88), (1460, 250, 95)):
            s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{copa}' stroke='{INK}' stroke-width='{LW}' opacity='{op:.2f}'/>")
    if nieve_ > 0:
        s.append(f"<path d='M1360 216 l40 -8 M1530 196 l30 -6 M1442 202 l56 0' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='{nieve_:.2f}'/>")
        s.append(f"<rect x='0' y='{SUP - 16}' width='{W}' height='22' fill='#ffffff' opacity='{nieve_:.2f}'/>")
    return "".join(s)


def esc_cigarra(t, dur, m):
    corre = seg(t, m[2] - 0.2, m[2] + 0.4) * (1 - seg(t, m[3] - 0.4, m[3]))
    k17 = clamp((t - m[2]) / max(0.1, (m[3] - 0.3) - m[2]))
    f = (k17 * 17) % 1 if 0 < k17 < 1 else 0.3
    cielo_c = mix("#8fd8ff", "#c8dcef", 1 if 0.72 < f < 0.97 else 0)
    s = [f"<rect width='{W}' height='{SUP}' fill='{cielo_c}'/>", nubes(t * 0.5)]
    s.append(arbol_estacion(t, f))
    s.append(f"<rect x='0' y='{SUP}' width='{W}' height='{H - SUP}' fill='#7a5233'/>")
    s.append(f"<path d='M0 {SUP + 210} Q500 {SUP + 180} 960 {SUP + 215} T1920 {SUP + 200} L1920 1080 L0 1080 Z' fill='#6a4529'/>")
    s.append(f"<path d='M0 {SUP + 430} Q500 {SUP + 400} 960 {SUP + 440} T1920 {SUP + 420} L1920 1080 L0 1080 Z' fill='#5a3a22'/>")
    for x, y, r in PIEDRAS:
        s.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{r:.0f}' ry='{r * 0.7:.0f}' fill='#9a8a7a' stroke='{INK}' stroke-width='5'/>")
    # raíces del árbol
    for d in ("M1450 410 Q1380 560 1220 640 Q1100 700 1000 820", "M1480 410 Q1520 600 1700 700 Q1800 760 1900 900",
              "M1465 410 Q1450 650 1380 860 Q1340 960 1300 1080", "M1220 640 Q1180 760 1120 800"):
        s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
                 f"<path d='{d}' fill='none' stroke='#a87a4a' stroke-width='20' stroke-linecap='round'/>")
    s.append(hierba(SUP, t, alto=46, paso=22).replace(f"<rect x='0' y='{SUP}' width='{W}' height='{H - SUP}' fill='#3f9a3a'/>", ""))
    # túnel iluminado alrededor de Bellotín y de la ninfa
    s.append(f"<ellipse cx='900' cy='690' rx='520' ry='190' fill='#4a2e18' opacity='0.5'/>")
    sale = seg(t, m[3] - 0.2, m[3] + 2.0)
    # la ninfa principal chupa savia de la raíz y después sube a la superficie
    nx = lerp(1150, 1300, sale); ny = lerp(700, SUP - 10, sale)
    s.append(ninfa(nx, ny, 1.1, t, ang=lerp(-20, -70, sale) * (1 - seg(t, m[3] + 1.8, m[3] + 2.4))))
    # muchas ninfas suben a la vez y salen convertidas en cigarras
    if t > m[3] - 0.3:
        r_ = np.random.default_rng(5)
        for i in range(16):
            x0 = r_.uniform(80, 1850); y0 = r_.uniform(820, 1060); dl = r_.uniform(0, 1.2)
            k = seg(t, m[3] - 0.2 + dl, m[3] + 1.8 + dl)
            if k < 1:
                s.append(ninfa(x0, lerp(y0, SUP + 20, k), 0.55, t + i, ang=-80, op=min(1, k * 4)))
            else:
                s.append(f"<ellipse cx='{x0:.0f}' cy='{SUP + 4}' rx='16' ry='7' fill='#3a2412'/>")
                s.append(ninfa(x0, SUP - 20, 0.42, 0, ang=-80, piel=True, op=0.8))
                vuela = seg(t, m[3] + 1.8 + dl, m[3] + 3.6 + dl)
                tx_ = 1400 + (i % 4) * 30 if i % 2 else x0 + 120 * math.sin(i + t)
                ty_ = 210 + (i * 37) % 170 if i % 2 else SUP - 90 - 80 * vuela - 30 * math.sin(t * 3 + i)
                s.append(cigarra(lerp(x0, tx_, vuela), lerp(SUP - 50, ty_, vuela), 0.6, t, ang=-90 * (i % 2) * vuela,
                                 canta=seg(t, m[4], m[4] + 0.5)))
    s.append(f"<path d='M{W} 0 L{W} 0' />")
    s.append(bellotin(640, 640, 0.6, t, luz=0.8, mira=(1, 0.3 - sale)))
    if corre > 0:   # el tiempo vuela: un reloj de arena que da vueltas
        s.append(f"<g transform='translate(330,{SUP + 210}) rotate({(t * 300) % 360:.0f}) scale({corre:.2f})' opacity='{corre:.2f}'>"
                 f"<path d='M-46 -70 L46 -70 L4 0 L46 70 L-46 70 L-4 0 Z' fill='#fff3d0' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>"
                 f"<path d='M-26 -54 L26 -54 L2 -14 Z M-30 58 L30 58 L0 30 Z' fill='#e8c15a'/></g>")
    return "".join(s)


# ================= capítulo 5: el pelotero y la Vía Láctea =================
def esc_pelotero(t, dur, m):
    oscuro = seg(t, m[2] - 0.3, m[2] + 0.8)
    brilla = seg(t, m[3] - 0.1, m[3] + 1.2)
    s = [noche_sabana(t, brillo=brilla, op_via=lerp(0.7, 0.35, oscuro) + 0.65 * brilla)]
    s.append(f"<rect width='{W}' height='{H}' fill='#000' opacity='{0.35 * oscuro * (1 - brilla):.2f}'/>")
    # camino recto que deja detrás
    x0 = 420
    avance = seg(t, 1.0, m[2] - 0.2) * 0.45 + seg(t, m[4] - 0.4, dur) * 0.55
    px = lerp(x0, 1450, avance)
    encima = 1.0 if (m[2] + 0.3 < t < m[4] - 0.4) else 0.0
    gira = (t - m[2]) * 3.0 if t < m[3] + 0.8 else 0.0
    if avance > 0.02:
        s.append(f"<path d='M{x0} 868 L{px:.0f} 868' stroke='#a88ac8' stroke-width='10' stroke-dasharray='10 18' stroke-linecap='round' opacity='0.8'/>")
    s.append(pelotero(px, 860, 1.4, t, rueda=0.0 if encima else 1.0, encima=encima, gira=gira))
    if brilla > 0:   # mira al cielo: la franja de luz le marca el camino
        bx, by = px + 98, 860 - 210
        s.append(f"<path d='M{bx:.0f} {by:.0f} L1150 330' stroke='#fff3a8' stroke-width='12' stroke-dasharray='6 20' stroke-linecap='round' opacity='{brilla * (1 - seg(t, m[4] - 0.4, m[4] + 0.6)):.2f}'/>")
        s.append(destellos(1150, 330, seg(t, m[3] + 0.2, m[3] + 2.0), 14, 300, "#ffffff"))
    s.append(destellos(px + 70, 800, seg(t, m[4] + 1.5, m[4] + 3.2), 12, 220))
    s.append(bellotin(300, 500 + 12 * math.sin(t * 0.8), 0.58, t, luz=0.0, mira=(0.6, -0.6 if brilla > 0 else 0.6)))
    return "".join(s)


# ================= despedida =================
def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


def esc_final(t, dur, m):
    s = [cielo("#ff9a76", "#ffe3a8", "atar"), sol(960, 760, 110), nubes(t * 0.5, "#fff2e6")]
    s.append(f"<path d='M0 760 Q400 700 900 740 T1920 720 L1920 1080 L0 1080 Z' fill='#7cc25a' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (fx, fy, sc, col) in enumerate([(160, 930, 1.0, "#ff6fa5"), (1780, 930, 1.1, "#b98cff"), (1620, 950, 0.8, "#ffd23f")]):
        s.append(flor(fx, fy, sc, t, col, "#ff8a3d", 230, i * 1.7))
    s.append(hierba(960, t, alto=100))
    # luciérnagas al atardecer
    for i in range(10):
        lx = 200 + (i * 173) % 1600 + 30 * math.sin(t * 0.8 + i); ly = 620 + 120 * math.sin(t * 0.6 + i * 1.3)
        s.append(f"<circle cx='{lx:.0f}' cy='{ly:.0f}' r='14' fill='#fff7a0' opacity='{0.3 + 0.3 * math.sin(t * 4 + i):.2f}'/><circle cx='{lx:.0f}' cy='{ly:.0f}' r='5' fill='#fffbe0'/>")
    llega = seg(t, 0, 2.4)
    nx = lerp(-300, 470, llega) + lerp(0, -40, seg(t, m[1] - 0.5, m[1] + 1.0)); ny = 540
    s.append(destellos(nx, ny, seg(t, 1.8, 3.2), 12, 260))
    s.append(bellotin(nx, ny, 0.85, t, ang=4 * math.sin(t * 1.6), guino=(m[3] + 0.4 < t < m[3] + 0.8), mira=(0.6, 0)))
    ap = seg(t, m[1] - 0.2, m[1] + 0.6)
    pulsa = m[1] + 2.4
    hecho = t > pulsa
    camp = seg(t, m[1] + 3.6, m[1] + 4.1)
    by = 470
    if ap > 0:
        late = 1 + 0.05 * math.sin(t * 6) if not hecho else 1 + 0.12 * math.exp(-(t - pulsa) * 5) * math.sin((t - pulsa) * 30)
        esc_ = (0.5 + 0.5 * ease(ap)) * late
        col = "#e62117" if not hecho else "#8a8f96"
        txt = "SUSCRÍBETE" if not hecho else "SUSCRITO"
        s.append(f"<g transform='translate(1180,{by}) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='{by}' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, by, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, by, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(1000, by + 15, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, by + 20, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, by, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Un escarabajo que mira las estrellas?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que hay un escarabajo que se guía por la Vía Láctea?",
                "Hoy viajamos al mundo de los insectos, y la última parada te dejará con la boca abierta.",
                "Nos hacemos diminutos y subimos a Bellotín, nuestra bellota voladora.",
                "Suscríbete y… ¡despegamos!"]},
    {"titulo": "1. La cazadora perfecta", "escena": esc_libelula, "tarjeta": "CAPÍTULO 1 · LA CAZADORA PERFECTA",
     "frases": ["Primera parada: un estanque lleno de juncos. ¡Mira qué helicóptero tan elegante!",
                "Es una libélula, y puede mover cada una de sus cuatro alas por separado.",
                "Vuela hacia delante, hacia atrás… y se queda quieta en el aire.",
                "Cuando ve un mosquito no lo persigue sin más: calcula hacia dónde va y le corta el paso.",
                "En los experimentos atrapa hasta noventa y cinco de cada cien presas: ¡una de las mejores cazadoras del planeta!"],
     "grandes": {4: "95 DE 100"}},
    {"titulo": "2. El baile de las abejas", "escena": esc_abeja, "tarjeta": "CAPÍTULO 2 · EL BAILE SECRETO",
     "frases": ["Ahora volamos hasta una colmena, donde miles de abejas trabajan sin parar.",
                "Esta abeja acaba de encontrar un campo lleno de flores… y para contarlo, ¡se pone a bailar!",
                "Camina en línea recta meneando el cuerpo, da una vuelta y vuelve a empezar.",
                "La dirección del baile indica hacia dónde están las flores, tomando el sol como referencia, y lo que dura el meneo dice lo lejos que están.",
                "Lo descubrió el científico Karl von Frisch, y ganó el Premio Nobel en mil novecientos setenta y tres."],
     "grandes": {3: "¡UN MAPA BAILADO!", 4: "NOBEL 1973"}},
    {"titulo": "3. El escarabajo cañón", "escena": esc_bombardero, "tarjeta": "CAPÍTULO 3 · EL ESCARABAJO CAÑÓN",
     "frases": ["Bajamos al suelo del bosque. Una hormiga hambrienta se acerca a un escarabajo…",
                "Pero este no es un escarabajo cualquiera: es el escarabajo bombardero.",
                "Dentro de su cuerpo mezcla dos sustancias y, ¡pum!, dispara un chorro a unos cien grados, tan caliente como el agua hirviendo.",
                "Y no es un solo disparo: son unas quinientas explosiones diminutas por segundo.",
                "La hormiga sale corriendo. Pero lo que nos espera bajo tierra es todavía más raro…"],
     "grandes": {2: "100 °C", 3: "500 POR SEGUNDO"}},
    {"titulo": "4. Diecisiete años bajo tierra", "escena": esc_cigarra, "tarjeta": "CAPÍTULO 4 · 17 AÑOS BAJO TIERRA",
     "frases": ["Bellotín enciende su foco y se mete bajo tierra, entre las raíces de un árbol.",
                "Aquí abajo vive una cría de cigarra, chupando la savia de las raíces.",
                "Y en algunas especies de América del Norte, se queda aquí abajo diecisiete años.",
                "Cuando llega el momento, salen todas a la vez: ¡hasta un millón y medio en un terreno como medio campo de fútbol!",
                "Trepan a los árboles, cambian de piel y llenan el bosque con un canto ensordecedor."],
     "grandes": {2: "17 AÑOS", 3: "1.500.000"}, "extra": 0.8},
    {"titulo": "5. Guiado por las estrellas", "escena": esc_pelotero, "tarjeta": "CAPÍTULO 5 · GUIADO POR LAS ESTRELLAS",
     "frases": ["Última parada: la sabana africana, de noche. ¡Mira qué cielo!",
                "Aquí, un escarabajo pelotero hace una bola de caca y se la lleva rodando, para que nadie se la robe.",
                "Tiene que ir en línea recta, pero está oscurísimo… ¿cómo lo consigue?",
                "Se sube a su bola, mira hacia arriba… ¡y se guía por la franja de luz de la Vía Láctea!",
                "Los científicos lo comprobaron en un planetario: es el primer animal conocido que se orienta con nuestra galaxia."],
     "grandes": {3: "¡LA VÍA LÁCTEA!"}, "extra": 1.2},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje por el mundo de los insectos.",
                "Si te ha gustado, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
