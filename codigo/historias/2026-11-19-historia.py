"""Episodio de prueba: "Viaje al fondo del mar" con Burbu, un submarino original.

Datos (verificados el 19-11-2026):
- El rojo es el primer color de la luz que absorbe el agua; a gran profundidad los animales rojos
  se ven negros, casi invisibles (NOAA Ocean Exploration «Why are so many deep-sea animals red?»).
- El zifio de Cuvier tiene el récord de buceo de los mamíferos: 2.992 m de profundidad y 222 min
  (3 h 42 min) sin respirar (Guinness World Records 2020; Quick et al., J. Exp. Biol. 2020).
- El 76 % (tres de cada cuatro) de los animales observados en la columna de agua entre la
  superficie y 4.000 m fabrica su propia luz (Martini y Haddock, Scientific Reports 2017, MBARI).
- En algunas especies de rape abisal el macho, diminuto, se fusiona para siempre con la hembra
  (Natural History Museum de Londres; Yale, Current Biology 2024).
- El agua de las fuentes hidrotermales supera los 400 °C pero no hierve por la enorme presión
  (Woods Hole Oceanographic Institution; NOAA Ocean Service).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-19-historia"
TITULO = "Viaje al fondo del mar"
VOZ = "ef_dora"
VELOCIDAD = 0.95
MUSICA = 7

W, H = 1920, 1080
rng = np.random.default_rng(11)
NIEVE = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(8, 25)) for _ in range(70)]
BURB = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(6, 16), rng.uniform(60, 140)) for _ in range(40)]
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, 420), rng.uniform(2, 4)) for _ in range(40)]


# ================= piezas comunes =================
def agua(p, t, rayos=True, suelo=None):
    """Fondo de mar. p = profundidad de 0 (superficie) a 1 (abismo)."""
    top = mix(mix("#5cc9f0", "#0d5a9c", clamp(p * 2)), "#030b1c", clamp((p - 0.5) * 2))
    bot = mix(mix("#1e8fd0", "#073766", clamp(p * 2)), "#01040c", clamp((p - 0.5) * 2))
    s = [f"<defs><linearGradient id='ag' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
         f"<stop offset='1' stop-color='{bot}'/></linearGradient>"
         "<linearGradient id='ray' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='0.35'/>"
         "<stop offset='1' stop-color='#fff' stop-opacity='0'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#ag)'/>"]
    if rayos and p < 0.6:
        a = clamp(1 - p / 0.6)
        for i in range(6):
            x = 150 + i * 330 + 60 * math.sin(t * 0.4 + i)
            s.append(f"<path d='M{x - 40:.0f} 0 L{x + 60:.0f} 0 L{x + 260:.0f} {H} L{x + 60:.0f} {H} Z' fill='url(#ray)' opacity='{a * (0.5 + 0.3 * math.sin(t * 0.7 + i * 2)):.2f}'/>")
    # nieve marina (más visible cuanto más hondo)
    a = 0.15 + 0.45 * p
    for x, y, r, v in NIEVE:
        yy = (y + t * v) % H
        s.append(f"<circle cx='{x + 12 * math.sin(t * 0.5 + x):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#e8f6ff' opacity='{a:.2f}'/>")
    if suelo:
        s.append(suelo)
    return "".join(s)


def burbujas(t, x, y, n=8, sube=320, tam=1.0, fase=0.0):
    s = []
    for i in range(n):
        k = ((t * 0.9 + i / n + fase) % 1)
        bx = x + 22 * math.sin(t * 3 + i * 1.7) - i * 4
        by = y - k * sube
        r = (5 + (i % 4) * 3) * tam * (0.6 + k)
        s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{r:.1f}' fill='#d8f3ff' fill-opacity='0.35' stroke='#ffffff' stroke-width='3' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def submarino(x, y, s, t, luz=0.0, ang=0.0, guino=False):
    """Burbu: submarino naranja con un gran ojo de buey por ojo, periscopio y hélice."""
    parp = 0.12 if (t % 3.7) < 0.13 or guino else 1.0
    helice = abs(math.sin(t * 18))
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if luz > 0.01:
        g.append("<defs><linearGradient id='haz' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#fff6c8' stop-opacity='0.85'/>"
                 "<stop offset='1' stop-color='#fff6c8' stop-opacity='0'/></linearGradient></defs>"
                 f"<path d='M175 22 L760 -170 L760 230 Z' fill='url(#haz)' opacity='{luz:.2f}'/>")
    g.append(f"<ellipse cx='0' cy='95' rx='150' ry='14' fill='#000' opacity='0.12'/>")
    # aletas y hélice
    g.append(f"<path d='M-150 -10 L-215 -62 L-205 0 L-215 62 L-150 10 Z' fill='#f06a28' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-236' y='-6' width='26' height='12' rx='4' fill='#9aa3ad' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<ellipse cx='-240' cy='0' rx='10' ry='{8 + 42 * helice:.0f}' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>")
    # torreta y periscopio
    g.append(f"<path d='M10 -78 L10 -150 L48 -150' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M10 -78 L10 -150 L48 -150' fill='none' stroke='#c9ced6' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<rect x='-70' y='-112' width='110' height='58' rx='20' fill='#ffa95e' stroke='{INK}' stroke-width='{LW}'/>")
    # cuerpo
    g.append(f"<rect x='-170' y='-72' width='350' height='150' rx='75' fill='#ff8a3d' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-150 40 Q10 70 165 40' fill='none' stroke='#e0662a' stroke-width='14' stroke-linecap='round'/>")
    for rx in (-120, -80, -40):
        g.append(f"<circle cx='{rx}' cy='-20' r='13' fill='#cdeeff' stroke='{INK}' stroke-width='5'/>")
    # ojo de buey (el ojo de Burbu)
    g.append(f"<circle cx='88' cy='-6' r='50' fill='#e9f7ff' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<circle cx='88' cy='-6' r='40' fill='none' stroke='#9aa3ad' stroke-width='5'/>")
    g.append(f"<g transform='translate(98,-4) scale(1,{parp})'><circle r='22' fill='#1e2a38'/><circle cx='-7' cy='-8' r='8' fill='#fff'/></g>")
    g.append(f"<path d='M70 48 Q92 62 116 48' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # foco
    g.append(f"<circle cx='172' cy='22' r='15' fill='{mix('#8a8f96', '#fff3a8', luz)}' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def pez(x, y, s, t, color, aleta=None, ojo=True, dirx=1, op=1.0):
    """Pez sencillo con cola que se mueve."""
    aleta = aleta or mix(color, "#000000", 0.25)
    c = 18 * math.sin(t * 9)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})' opacity='{op:.2f}'>"
            f"<path d='M-70 0 L-120 {-40 + c:.0f} L-112 0 L-120 {40 + c:.0f} Z' fill='{aleta}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-20 -38 L5 -62 L25 -36 Z' fill='{aleta}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='0' rx='80' ry='42' fill='{color}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-10 -30 Q8 0 -10 30' fill='none' stroke='{aleta}' stroke-width='7'/>"
            + (f"<circle cx='45' cy='-10' r='13' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='49' cy='-10' r='6' fill='{INK}'/>" if ojo else "")
            + f"<path d='M62 14 Q70 18 76 12' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def destellos(cx, cy, k, n=10, r=220, col="#fff6a8"):
    if k <= 0:
        return ""
    s = []
    for i in range(n):
        a = i / n * 2 * math.pi
        d = r * (0.4 + 0.6 * k)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        e = 18 * (1 - k) + 6
        s.append(f"<path d='M{x:.0f} {y - e:.0f} L{x + e * 0.3:.0f} {y:.0f} L{x:.0f} {y + e:.0f} L{x - e * 0.3:.0f} {y:.0f} Z' fill='{col}' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def suelo_marino(t, color="#3b3550"):
    return (f"<path d='M0 860 Q240 820 480 850 T960 840 T1440 860 T1920 845 L1920 1080 L0 1080 Z' fill='{color}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M0 950 Q300 920 640 945 T1280 935 T1920 950 L1920 1080 L0 1080 Z' fill='{mix(color, '#000000', 0.25)}'/>")


# ================= capítulos =================
def esc_intro(t, dur, m):
    # cielo y superficie
    s = ["<defs><linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#7fd3ff'/>"
         "<stop offset='1' stop-color='#e3f7ff'/></linearGradient>"
         "<linearGradient id='mar' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2aa7e0'/>"
         "<stop offset='1' stop-color='#0b5d9e'/></linearGradient>"
         "<radialGradient id='sol'><stop offset='0' stop-color='#fff8c8'/><stop offset='1' stop-color='#ffd85a' stop-opacity='0'/></radialGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#cielo)'/>",
         "<circle cx='1400' cy='250' r='190' fill='url(#sol)'/>",
         f"<circle cx='1400' cy='250' r='80' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, (cx, cy, sc) in enumerate([(300, 220, 1.3), (900, 160, 1.0), (1700, 320, 0.9)]):
        dx = (t * 18 * (1 + i * 0.3)) % 2300 - 300
        s.append(f"<g transform='translate({(cx + dx) % 2300 - 300:.0f},{cy}) scale({sc})'>"
                 f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    for i in range(3):   # gaviotas
        bx = (t * 60 + i * 400) % 2200 - 200; by = 300 + 40 * i + 10 * math.sin(t * 3 + i)
        w = 18 * math.sin(t * 8 + i)
        s.append(f"<path d='M{bx - 30:.0f} {by + w:.0f} Q{bx - 15:.0f} {by - 15:.0f} {bx:.0f} {by:.0f} Q{bx + 15:.0f} {by - 15:.0f} {bx + 30:.0f} {by + w:.0f}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # submarino: entra, flota, y al final se sumerge
    entra = seg(t, 0, 2.6)
    baja = seg(t, m[3] + 1.2, dur)
    x = lerp(-300, 900, entra) + lerp(0, 120, baja)
    y = 520 + 10 * math.sin(t * 2.2) + lerp(0, 560, baja)
    ang = 5 * math.sin(t * 1.8) + lerp(0, 18, baja)
    sub = submarino(x, y, 0.95, t, ang=ang, guino=(m[2] + 1.6 < t < m[2] + 2.0))
    # mar (el submarino queda medio dentro del agua)
    ola = "".join(f"Q{60 + i * 120:.0f} {540 + 14 * math.sin(t * 2 + i):.0f} {120 + i * 120:.0f} 545 " for i in range(17))
    s.append(sub)
    s.append(f"<path d='M0 545 {ola} L1920 1080 L0 1080 Z' fill='url(#mar)' fill-opacity='0.9' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(8):
        sx = (i * 260 + t * 40) % 2000 - 40
        s.append(f"<path d='M{sx:.0f} {640 + i * 45 % 300:.0f} q30 -12 60 0' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
    if baja > 0:
        s.append(burbujas(t, x - 100, y + 40, 10, 380, 1.3))
    return "".join(s)


def esc_rojo(t, dur, m):
    p = lerp(0.12, 0.5, seg(t, 0, m[3] + 1.5))
    s = [agua(p, t)]
    # haz de sol que se separa en colores: el rojo es el primero en apagarse
    colores = ["#ff3b3b", "#ff9a2e", "#ffe14d", "#4fd36b", "#3a8dff"]
    k = seg(t, m[2], m[2] + 3.5)
    ini = seg(t, m[1] - 0.5, m[2] + 0.2)
    for i, c in enumerate(colores):
        largo = lerp(900, [110, 300, 480, 660, 900][i], k)
        x0 = 1180 + i * 34
        s.append(f"<path d='M{x0} 0 L{x0 + 34} 0 L{x0 + 34 + largo * 0.18:.0f} {largo:.0f} L{x0 + largo * 0.18:.0f} {largo:.0f} Z' "
                 f"fill='{c}' opacity='{0.55 * ini:.2f}'/>")
    # pez rojo que acompaña a Burbu
    oscuro = seg(t, m[3] - 0.3, m[3] + 2.2)
    luz = seg(t, m[5] + 0.3, m[5] + 1.2)
    fondo = mix("#0d5a9c", "#073766", 0.5)
    col = mix(mix("#e8382f", "#1a1f2e", oscuro), "#ff3b2f", luz)
    ale = mix(mix("#b51f1a", "#11141f", oscuro), "#c81e1a", luz)
    fx = lerp(2100, 1180, seg(t, m[1] - 0.8, m[1] + 1.8)) + 30 * math.sin(t * 0.9)
    fy = 600 + 30 * math.sin(t * 1.4)
    sx, sy = 560 + 30 * math.sin(t * 0.6), 500 + 18 * math.sin(t * 1.1)
    s.append(submarino(sx, sy, 0.9, t, luz=luz))
    op = 1 - 0.55 * oscuro * (1 - luz)
    s.append(pez(fx, fy, 1.25, t, col, ale, dirx=-1, op=op))
    if luz > 0:
        s.append(destellos(fx, fy, seg(t, m[5] + 0.6, m[5] + 2.2), 10, 200))
    s.append(burbujas(t, sx - 230, sy, 6, 260, 0.8))
    return "".join(s)


def zifio(x, y, s, t, ang=0.0):
    """Zifio de Cuvier: cuerpo robusto gris pardo, cabeza clara, pico corto, aleta dorsal pequeña atrás."""
    c = 10 * math.sin(t * 2.4)
    parp = 0.15 if (t % 4.1) < 0.14 else 1
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-330 0 L-420 {-70 + c:.0f} Q-400 {0 + c * 0.3:.0f} -420 {70 + c:.0f} Z' fill='#6d6b73' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-150 -70 L-100 -125 L-60 -78 Z' fill='#6d6b73' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-340 0 Q-200 -95 80 -88 Q250 -80 300 -20 Q330 0 300 18 Q230 85 40 88 Q-200 85 -340 0 Z' fill='#8a8790' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M120 -84 Q260 -74 300 -20 Q330 0 300 18 Q250 60 140 70 Q170 -10 120 -84 Z' fill='#d9d4cc'/>"
            f"<path d='M300 -6 Q345 0 360 10 Q340 22 300 18 Z' fill='#d9d4cc' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-340 0 Q-200 -95 80 -88 Q250 -80 300 -20 Q330 0 300 18 Q230 85 40 88 Q-200 85 -340 0 Z' fill='none' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M40 40 Q20 95 -40 110 Q-10 70 0 40 Z' fill='#6d6b73' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            + "".join(f"<path d='M{-200 + i * 70} {-40 + (i % 3) * 25} q40 {10 - i % 2 * 20} 80 {5}' fill='none' stroke='#f2efe8' stroke-width='5' stroke-linecap='round' opacity='0.8'/>" for i in range(5))
            + f"<g transform='translate(225,-14) scale(1,{parp})'><circle r='13' fill='{INK}'/><circle cx='-4' cy='-4' r='4' fill='#fff'/></g>"
            f"<path d='M262 24 Q290 30 318 14' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def cronometro(cx, cy, t, k):
    if k <= 0:
        return ""
    ang = (t * 720) % 360
    s = 0.6 + 0.4 * ease(min(1, k * 2))
    return (f"<g transform='translate({cx},{cy}) scale({s:.2f})' opacity='{min(1, k * 3):.2f}'>"
            f"<rect x='-18' y='-138' width='36' height='30' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
            f"<circle r='112' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle r='92' fill='none' stroke='#ffd23f' stroke-width='10'/>"
            + "".join(f"<line x1='0' y1='-80' x2='0' y2='-66' stroke='{INK}' stroke-width='6' transform='rotate({a})'/>" for a in range(0, 360, 30))
            + f"<line x1='0' y1='0' x2='0' y2='-72' stroke='#e8382f' stroke-width='9' stroke-linecap='round' transform='rotate({ang:.0f})'/>"
            f"<circle r='12' fill='{INK}'/></g>")


def esc_zifio(t, dur, m):
    p = lerp(0.5, 0.62, seg(t, 0, dur))
    s = [agua(p, t)]
    # sombra que pasa (frase 0), luego el zifio se acerca y se ve bien (frase 1)
    sombra = seg(t, 0.2, m[1])
    if t < m[1] + 0.5:
        sx_ = lerp(2300, -600, sombra)
        s.append(f"<g opacity='{0.55 * (1 - seg(t, m[1] - 0.3, m[1] + 0.5)):.2f}'>{zifio(sx_, 330, 1.3, t)}</g>".replace("#8a8790", "#0a2a4a").replace("#6d6b73", "#0a2a4a").replace("#d9d4cc", "#0a2a4a"))
    llega = seg(t, m[1] - 0.2, m[1] + 2.5)
    baja = seg(t, m[2] + 0.5, m[2] + 4)
    vuelve = seg(t, m[4] - 0.4, m[4] + 2.5)
    zx = lerp(2300, 1080, llega) + lerp(0, 120, baja) - lerp(0, 120, vuelve)
    zy = 520 + 15 * math.sin(t * 1.2) + lerp(0, 760, baja) - lerp(0, 760, vuelve)
    za = lerp(0, 52, baja) * (1 - vuelve) - 14 * vuelve * (1 - seg(t, m[4] + 2.5, m[4] + 4))
    sub = submarino(430, 560 + 12 * math.sin(t), 0.75, t, luz=0.6)
    s.append(sub)
    if t > m[1] - 0.3:
        s.append(zifio(zx, zy, 1.1, t, za))
        s.append(burbujas(t, zx - 300, zy - 40, 5, 220, 0.8))
    s.append(cronometro(960, 640, t, seg(t, m[3], m[3] + 0.6) * (1 - seg(t, m[4] - 0.3, m[4] + 0.2))))
    s.append(destellos(zx + 100, zy, seg(t, m[4] + 0.6, m[4] + 2.6), 12, 330))
    return "".join(s)


def medusa(x, y, s, t, brillo, col="#7af0ff"):
    b = 0.85 + 0.15 * math.sin(t * 3 + x)
    cuerpo = mix("#20304a", col, brillo)
    tent = "".join(f"<path d='M{-45 + i * 22} 10 q{12 * math.sin(t * 2 + i)} 50 0 100 q{-12 * math.sin(t * 2 + i)} 50 0 100' fill='none' stroke='{cuerpo}' stroke-width='6' stroke-linecap='round'/>" for i in range(5))
    return (f"<g transform='translate({x:.0f},{y + 14 * math.sin(t * 1.5 + x):.0f}) scale({s:.2f},{s * b:.2f})'>"
            f"<circle r='120' fill='{col}' opacity='{0.25 * brillo:.2f}'/>{tent}"
            f"<path d='M-70 10 Q-70 -80 0 -80 Q70 -80 70 10 Q35 0 0 12 Q-35 0 -70 10 Z' fill='{cuerpo}' fill-opacity='0.85' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='-20' cy='-30' r='8' fill='{INK}'/><circle cx='20' cy='-30' r='8' fill='{INK}'/>"
            f"<path d='M-12 -10 Q0 -2 12 -10' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def pez_linterna(x, y, s, t, brillo):
    puntos = "".join(f"<circle cx='{-50 + i * 24}' cy='{22 - abs(i - 2) * 4}' r='7' fill='{mix('#2a3550', '#7dfcff', brillo)}'/>" for i in range(6))
    halo = "".join(f"<circle cx='{-50 + i * 24}' cy='{22 - abs(i - 2) * 4}' r='20' fill='#7dfcff' opacity='{0.35 * brillo:.2f}'/>" for i in range(6))
    return (f"<g>{pez(x, y, s, t, '#2a3350', '#1d2438')}"
            f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>{halo}{puntos}</g></g>")


def ctenoforo(x, y, s, t, brillo):
    filas = "".join(f"<path d='M{-40 + i * 16} -60 Q{-40 + i * 16 + 6} 0 {-40 + i * 16} 60' fill='none' stroke='{c}' stroke-width='7' opacity='{brillo * (0.5 + 0.5 * math.sin(t * 6 + i)):.2f}'/>"
                    for i, c in enumerate(["#ff5ad8", "#ffd23f", "#5affb4", "#5ac8ff", "#c77dff", "#ff8a3d"]))
    return (f"<g transform='translate({x:.0f},{y + 10 * math.sin(t + x):.0f}) scale({s:.2f})'>"
            f"<ellipse rx='56' ry='76' fill='#cfe8ff' fill-opacity='0.18' stroke='{mix('#3a4a66', '#e8f6ff', brillo)}' stroke-width='6'/>{filas}</g>")


def esc_luces(t, dur, m):
    p = 0.8
    s = [agua(p, t, rayos=False)]
    apaga = seg(t, m[1] + 0.6, m[1] + 1.4)
    luz = 1 - apaga
    s.append(f"<rect width='{W}' height='{H}' fill='#000' opacity='{0.45 * apaga:.2f}'/>")
    enc = [seg(t, m[2] + 0.2 + i * 0.6, m[2] + 1.0 + i * 0.6) for i in range(6)]
    grupo = seg(t, m[-1] - 0.2, m[-1] + 1.6)
    if grupo < 1:
        o = 1 - grupo
        s.append(f"<g opacity='{o:.2f}'>")
        s.append(medusa(1250, 330, 0.9, t, enc[0]))
        s.append(pez_linterna(1600, 560, 0.9, t, enc[1]))
        s.append(ctenoforo(980, 700, 1.0, t, enc[2]))
        s.append(medusa(1600, 790, 0.7, t, enc[3], "#b8ff7a"))
        s.append(pez_linterna(1120, 470, 0.7, t * 1.1, enc[4]))
        s.append(ctenoforo(1460, 300, 0.7, t, enc[5]))
        s.append("</g>")
    if grupo > 0:   # tres de cada cuatro: 4 animales en fila, 3 brillan
        s.append(f"<g opacity='{grupo:.2f}'>")
        xs = [720, 1040, 1360, 1680]
        enc2 = [seg(t, m[-1] + 1.4 + i * 0.6, m[-1] + 1.9 + i * 0.6) for i in range(3)]
        s.append(medusa(xs[0], 560, 1.25, t, enc2[0]))
        s.append(ctenoforo(xs[1], 580, 1.45, t, enc2[1]))
        s.append(f"<circle cx='{xs[2]}' cy='590' r='150' fill='#7dfcff' opacity='{0.15 * enc2[2]:.2f}'/>")
        s.append(pez_linterna(xs[2], 590, 1.3, t, enc2[2]))
        s.append(pez(xs[3], 590, 1.3, t, "#3a3f55", "#262a3a"))
        s.append("</g>")
    s.append(submarino(lerp(380, 250, grupo), 560 + 14 * math.sin(t * 0.9), lerp(0.75, 0.55, grupo), t, luz=0.8 * luz))
    return "".join(s)


def rape(x, y, s, t, revela):
    """Hembra de rape abisal: cuerpo redondo oscuro, boca enorme con dientes, caña con luz en la frente."""
    lure_ang = 12 * math.sin(t * 1.6)
    cuerpo = mix("#120f1c", "#4a3a5c", revela)
    borde = mix("#120f1c", INK, revela)
    dientes = "".join(f"<path d='M{60 + i * 22} -6 l10 {26 + (i % 2) * 8} l10 {-26 - (i % 2) * 8}' fill='#fff' stroke='{borde}' stroke-width='3'/>" for i in range(7))
    dientes2 = "".join(f"<path d='M{70 + i * 22} 74 l10 {-24 - (i % 2) * 8} l10 {24 + (i % 2) * 8}' fill='#fff' stroke='{borde}' stroke-width='3'/>" for i in range(6))
    parp = 0.15 if (t % 3.3) < 0.13 else 1
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
            f"<g opacity='{revela:.2f}'>"
            f"<path d='M-170 0 L-260 -70 L-245 0 L-260 70 Z' fill='{cuerpo}' stroke='{borde}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-180 0 Q-170 -160 20 -150 Q190 -140 230 -10 L230 0 Q200 120 20 140 Q-170 140 -180 0 Z' fill='{cuerpo}' stroke='{borde}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M50 -14 Q160 -40 240 -6 Q220 90 60 82 Q40 34 50 -14 Z' fill='#1a0c14' stroke='{borde}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"{dientes}{dientes2}"
            f"<g transform='translate(0,-70) scale(1,{parp})'><circle r='24' fill='#f2efe8' stroke='{borde}' stroke-width='6'/><circle cx='5' r='11' fill='#111'/><circle cx='1' cy='-5' r='4' fill='#fff'/></g>"
            f"<path d='M-60 60 Q-30 100 10 90' fill='none' stroke='{mix(cuerpo, '#000000', 0.3)}' stroke-width='9' stroke-linecap='round'/></g>"
            f"<g transform='translate(40,-140) rotate({lure_ang:.1f})'>"
            f"<path d='M0 0 Q40 -150 170 -150' fill='none' stroke='{mix('#3a2f4a', '#6a5a7c', revela)}' stroke-width='10' stroke-linecap='round'/>"
            f"<circle cx='175' cy='-140' r='110' fill='#9affd9' opacity='{0.22 + 0.06 * math.sin(t * 5):.2f}'/>"
            f"<circle cx='175' cy='-140' r='50' fill='#c8fff0' opacity='0.45'/>"
            f"<circle cx='175' cy='-140' r='24' fill='#f0fffb' stroke='#9affd9' stroke-width='6'/></g></g>")


def macho(x, y, s, t, op=1.0):
    c = 10 * math.sin(t * 14)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({-s:.3f},{s:.3f})' opacity='{op:.2f}'>"
            f"<path d='M-40 0 L-70 {-22 + c:.0f} L-66 0 L-70 {22 + c:.0f} Z' fill='#6a5a7c' stroke='{INK}' stroke-width='5'/>"
            f"<ellipse rx='46' ry='24' fill='#8a7a9c' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='24' cy='-6' r='9' fill='#fff' stroke='{INK}' stroke-width='3'/><circle cx='26' cy='-6' r='4' fill='{INK}'/></g>")


def corazon(x, y, s, op):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 18 C-30 -6 -22 -30 0 -16 C22 -30 30 -6 0 18 Z' "
            f"fill='#ff5a8a' stroke='{INK}' stroke-width='5' opacity='{op:.2f}'/>")


def esc_rape(t, dur, m):
    s = [agua(0.9, t, rayos=False), f"<rect width='{W}' height='{H}' fill='#000' opacity='0.35'/>"]
    revela = seg(t, m[1], m[1] + 1.6)
    rx, ry = 1060 + 25 * math.sin(t * 0.5), 600 + 18 * math.sin(t * 0.8)
    if revela < 0.05:   # solo se ve la lucecita moviéndose
        lx = lerp(1500, rx + 215, seg(t, 0, m[1])); ly = lerp(300, ry - 290, seg(t, 0, m[1]))
        s.append(f"<circle cx='{lx:.0f}' cy='{ly + 20 * math.sin(t * 2):.0f}' r='80' fill='#9affd9' opacity='0.25'/>"
                 f"<circle cx='{lx:.0f}' cy='{ly + 20 * math.sin(t * 2):.0f}' r='22' fill='#f0fffb' stroke='#9affd9' stroke-width='6'/>")
    else:
        s.append(rape(rx, ry, 1.05, t, revela))
    # el macho llega (frase 2), muerde (frase 3) y se fusiona (frase 4)
    llega = seg(t, m[2] - 0.2, m[2] + 3.0)
    muerde = seg(t, m[3] + 0.5, m[3] + 2.0)
    fusion = seg(t, m[4], m[4] + 3.0)
    if t > m[2] - 0.3:
        mx = lerp(2000, rx + 120, llega) - lerp(0, 60, muerde)
        my = lerp(820, ry + 170, llega) - lerp(0, 20, muerde) + (1 - llega) * 20 * math.sin(t * 4)
        s.append(macho(mx, my, lerp(1.0, 0.75, fusion), t if fusion < 0.5 else 0, op=1 - 0.6 * fusion))
        if muerde > 0.9:
            s.append(f"<circle cx='{mx - 30:.0f}' cy='{my:.0f}' r='{lerp(10, 120, fusion):.0f}' fill='#ff8ac0' opacity='{0.35 * fusion * (1 - seg(t, m[4] + 3, dur)):.2f}'/>")
    if fusion > 0:
        for i in range(5):
            k = ((t - m[4]) * 0.5 + i / 5) % 1
            s.append(corazon(rx + 160 + 60 * math.sin(i * 2 + t), ry + 120 - k * 300, 1.2 + 0.4 * (i % 2), fusion * (1 - k)))
    s.append(submarino(330, 420 + 10 * math.sin(t), 0.62, t, luz=0.0))
    return "".join(s)


def chimenea(x, base, alto, ancho, t, fase):
    s = []
    # humo negro que sube y se expande
    for i in range(9):
        k = ((t * 0.35 + i / 9 + fase) % 1)
        cx = x + 40 * math.sin(k * 5 + fase * 6) + k * 60
        cy = base - alto - k * 520
        r = 30 + k * 110
        s.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r:.0f}' fill='{mix('#2a2a33', '#14141a', k)}' opacity='{0.85 * (1 - k):.2f}'/>")
    pts = f"M{x - ancho} {base} L{x - ancho * 0.6} {base - alto * 0.5} L{x - ancho * 0.45} {base - alto} L{x + ancho * 0.45} {base - alto} L{x + ancho * 0.6} {base - alto * 0.45} L{x + ancho} {base} Z"
    s.append(f"<path d='{pts}' fill='#4a3f3a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M{x - ancho * 0.5} {base - alto * 0.3} l30 -20 M{x + ancho * 0.2} {base - alto * 0.65} l-25 -18' stroke='#2e2622' stroke-width='8' stroke-linecap='round'/>")
    s.append(f"<ellipse cx='{x}' cy='{base - alto}' rx='{ancho * 0.45:.0f}' ry='12' fill='#ff7a2a' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<circle cx='{x}' cy='{base - alto - 10}' r='{ancho * 0.9:.0f}' fill='#ff9a3d' opacity='{0.18 + 0.06 * math.sin(t * 6 + fase):.2f}'/>")
    return "".join(s)


def gusanos(x, base, n, t):
    s = []
    for i in range(n):
        gx = x + i * 34; alto = 90 + (i * 37) % 60
        sw = 8 * math.sin(t * 1.5 + i)
        s.append(f"<path d='M{gx} {base} Q{gx + sw / 2:.0f} {base - alto / 2} {gx + sw:.0f} {base - alto}' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>")
        s.append(f"<path d='M{gx} {base} Q{gx + sw / 2:.0f} {base - alto / 2} {gx + sw:.0f} {base - alto}' fill='none' stroke='#f2efe8' stroke-width='11' stroke-linecap='round'/>")
        s.append(f"<ellipse cx='{gx + sw:.0f}' cy='{base - alto - 14}' rx='16' ry='22' fill='#e8382f' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def termometro(x, y, k, op):
    alto = 300
    return (f"<g transform='translate({x},{y})' opacity='{op:.2f}'>"
            f"<rect x='-26' y='{-alto}' width='52' height='{alto + 10}' rx='26' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-12' y='{-alto * k + 10:.0f}' width='24' height='{alto * k:.0f}' fill='#e8382f'/>"
            f"<circle cy='40' r='50' fill='#e8382f' stroke='{INK}' stroke-width='{LW}'/>"
            + "".join(f"<line x1='26' y1='{-alto + 40 + i * 50}' x2='6' y2='{-alto + 40 + i * 50}' stroke='{INK}' stroke-width='5'/>" for i in range(5))
            + "</g>")


def esc_fuentes(t, dur, m):
    llega = seg(t, 0, 3.0)
    s = [agua(0.95, t, rayos=False, suelo=suelo_marino(t)), f"<rect width='{W}' height='{H}' fill='#000' opacity='0.15'/>"]
    s.append(chimenea(1080, 870, 300, 80, t, 0.0))
    s.append(chimenea(1380, 880, 220, 65, t, 0.37))
    s.append(chimenea(1640, 875, 340, 85, t, 0.71))
    vida = seg(t, m[4] - 0.2, m[4] + 1.8)
    s.append(gusanos(900, 880, 4, t))
    s.append(gusanos(1210, 885, int(2 + 3 * vida), t))
    s.append(gusanos(1480, 885, int(1 + 3 * vida), t))
    for i in range(int(8 * vida)):   # gambas blancas
        gx = 860 + (i * 113 + t * 40 * (1 + i % 3)) % 900; gy = 830 + 20 * math.sin(t * 2 + i)
        s.append(f"<g transform='translate({gx:.0f},{gy:.0f})'><path d='M-18 0 Q0 -16 18 0 Q0 10 -18 0 Z' fill='#f6f0e6' stroke='{INK}' stroke-width='4'/>"
                 f"<path d='M18 0 l14 -10 M18 0 l14 6' stroke='{INK}' stroke-width='3'/></g>")
    # flechas de presión (frase 3)
    pr = seg(t, m[3] - 0.2, m[3] + 0.8) * (1 - seg(t, m[4] - 0.4, m[4] + 0.4))
    if pr > 0:
        for i, ax in enumerate((980, 1240, 1500, 1760)):
            ay = 120 + 40 * ((t * 1.5 + i * 0.3) % 1)
            s.append(f"<g transform='translate({ax},{ay:.0f})' opacity='{pr:.2f}'><rect x='-22' y='0' width='44' height='120' fill='#5ac8ff' stroke='{INK}' stroke-width='7'/>"
                     f"<path d='M-55 115 L55 115 L0 185 Z' fill='#5ac8ff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # termómetro (frase 2)
    tk = seg(t, m[2] + 0.2, m[2] + 3.0)
    s.append(termometro(420, 760, tk, seg(t, m[2], m[2] + 0.5) * (1 - seg(t, m[3] + 2.5, m[3] + 3.2))))
    sx = lerp(-250, 420, llega); sy = lerp(300, 520, llega) + 10 * math.sin(t)
    if tk <= 0 or t > m[3] + 3.0:
        s.append(submarino(sx, sy, 0.7, t, luz=0.7))
    return "".join(s)


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def esc_final(t, dur, m):
    sube = seg(t, 0, 4)
    cielo1 = mix("#0d5a9c", "#ffb38a", sube)
    s = ["<defs><linearGradient id='atar' x1='0' y1='0' x2='0' y2='1'>"
         f"<stop offset='0' stop-color='{mix('#0b3a6e', '#ff8a6b', sube)}'/><stop offset='1' stop-color='{mix('#0d5a9c', '#ffe0a8', sube)}'/></linearGradient>"
         "<linearGradient id='mar2' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a7fc0'/><stop offset='1' stop-color='#0b3d70'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#atar)'/>",
         f"<circle cx='960' cy='{lerp(900, 560, sube):.0f}' r='120' fill='#ffd166' stroke='{INK}' stroke-width='{LW}' opacity='{sube:.2f}'/>"]
    ola = "".join(f"Q{60 + i * 120:.0f} {600 + 12 * math.sin(t * 2 + i):.0f} {120 + i * 120:.0f} 605 " for i in range(17))
    sx = lerp(560, 420, seg(t, m[1] - 0.5, m[1] + 1.0)); sy = lerp(1000, 585, sube) + 10 * math.sin(t * 2)
    s.append(submarino(sx, sy, 0.8, t, ang=6 * math.sin(t * 1.6), guino=(m[3] + 0.4 < t < m[3] + 0.8)))
    s.append(f"<path d='M0 605 {ola} L1920 1080 L0 1080 Z' fill='url(#mar2)' fill-opacity='0.92' stroke='{INK}' stroke-width='{LW}'/>")
    # gran botón de suscripción: aparece (frase 1), el cursor lo pulsa y la campana suena
    ap = seg(t, m[1] - 0.2, m[1] + 0.6)
    pulsa = m[1] + 2.4
    hecho = t > pulsa
    camp = seg(t, m[1] + 3.6, m[1] + 4.1)
    if ap > 0:
        late = 1 + 0.05 * math.sin(t * 6) if not hecho else 1 + 0.12 * math.exp(-(t - pulsa) * 5) * math.sin((t - pulsa) * 30)
        esc_ = (0.5 + 0.5 * ease(ap)) * late
        col = "#e62117" if not hecho else "#8a8f96"
        txt = "SUSCRÍBETE" if not hecho else "SUSCRITO"
        s.append(f"<g transform='translate(1180,330) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        # campana al lado
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='330' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, 330, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, 330, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        # cursor: entra, pulsa el botón y luego la campana
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(900, 345, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 350, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, 330, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


CAPITULOS = [
    {"titulo": "¿Qué hay en el fondo del mar?", "escena": esc_intro, "susc": 2,
     "frases": ["¿Te has preguntado alguna vez qué se esconde en lo más profundo del océano?",
                "Hoy vamos a descubrirlo a bordo de Burbu, nuestro pequeño submarino.",
                "Y si te gustan estas aventuras, suscríbete a Mundo Curioso cinco mil para no perderte ninguna.",
                "¿Preparado? ¡Allá vamos!"]},
    {"titulo": "1. El color que desaparece", "escena": esc_rojo, "tarjeta": "CAPÍTULO 1 · EL COLOR QUE DESAPARECE",
     "frases": ["Empezamos a bajar, y el agua se vuelve cada vez más azul.",
                "Mira a este pez rojo que nos acompaña.",
                "El agua se va tragando los colores de la luz del sol, y el primero en desaparecer es el rojo.",
                "Por eso, a doscientos metros, nuestro amigo ya no se ve rojo… ¡casi no se ve!",
                "Aquí abajo, ser rojo es como llevar una capa de invisibilidad.",
                "Pero si Burbu enciende su luz… ¡ahí está otra vez su color!"],
     "grandes": {4: "¡INVISIBLE!"}},
    {"titulo": "2. El campeón de aguantar la respiración", "escena": esc_zifio, "tarjeta": "CAPÍTULO 2 · EL GRAN BUCEADOR",
     "frases": ["De repente, una sombra enorme pasa a nuestro lado.",
                "Es un zifio de Cuvier, una ballena con el hocico corto, como el pico de un ganso.",
                "Este gran buceador puede bajar hasta casi tres mil metros de profundidad.",
                "Y lo más increíble: un zifio aguantó la respiración durante tres horas y cuarenta y dos minutos.",
                "¡Es el récord de buceo de todos los mamíferos!"],
     "grandes": {2: "3.000 m", 3: "3 h 42 min"}},
    {"titulo": "3. El mar que brilla en la oscuridad", "escena": esc_luces, "tarjeta": "CAPÍTULO 3 · LUCES EN LA OSCURIDAD",
     "frases": ["Seguimos bajando. A mil metros ya no llega ni un solo rayo de sol.",
                "Burbu apaga su luz… y entonces pasa algo mágico.",
                "Medusas, peces y otros animales empiezan a brillar como luces de Navidad.",
                "¡Es como bucear dentro de un cielo lleno de estrellas!",
                "Unos científicos contaron más de trescientos mil animales en estas aguas, y descubrieron que tres de cada cuatro fabrican su propia luz."],
     "grandes": {4: "3 DE CADA 4"}, "extra": 1.5},
    {"titulo": "4. El pez que se pega para siempre", "escena": esc_rape, "tarjeta": "CAPÍTULO 4 · UN AMOR MUY PEGAJOSO",
     "frases": ["En la oscuridad se mueve una lucecita… ¡cuidado!",
                "Es un rape abisal. La hembra lleva en la cabeza una caña de pescar con luz para atraer a sus presas.",
                "Y este pececito diminuto es el macho, muchísimo más pequeño que ella.",
                "En algunas especies, cuando por fin la encuentra, la muerde… y ya no la suelta nunca.",
                "Sus cuerpos se fusionan y comparten hasta la sangre: ¡literalmente se convierten en uno!"],
     "grandes": {3: "¡PARA SIEMPRE!"}},
    {"titulo": "5. Chimeneas en el fondo del mar", "escena": esc_fuentes, "tarjeta": "CAPÍTULO 5 · CHIMENEAS SUBMARINAS",
     "frases": ["Por fin llegamos al fondo. ¡Y mira! Del suelo salen chimeneas que echan humo negro.",
                "Son fuentes hidrotermales: el agua que sale de ellas se ha calentado con el magma de la Tierra.",
                "Puede superar los cuatrocientos grados, cuatro veces más que el agua hirviendo…",
                "Y aun así no hierve, porque el peso de todo el océano la aprieta tanto que no la deja.",
                "Y alrededor, aunque aquí nunca llega el sol, ¡hay vida por todas partes!"],
     "grandes": {2: "400 °C"}},
    {"titulo": "Suscríbete para más aventuras", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje de hoy al fondo del mar.",
                "Si has descubierto algo nuevo, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ninguna aventura: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
