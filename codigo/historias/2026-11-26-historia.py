"""Episodio: "Viaje por el tiempo más salvaje de la Tierra" con Zumbi, un dron cazatormentas (original).

Datos (verificados el 26-11-2026):
- La piedra de granizo más grande de EE. UU. cayó en Vivian (Dakota del Sur) el 23 de julio de 2010:
  8,0 pulgadas (20 cm) de diámetro, 18,6 pulgadas de circunferencia y 1,9375 libras (0,88 kg), récord
  de diámetro y de peso del país (NWS Aberdeen «Record Setting Hail Event in Vivian, South Dakota»;
  NOAA NCEI). Un balón de voleibol mide unos 21 cm de diámetro. El granizo crece porque las corrientes
  ascendentes de la tormenta lo suben y bajan y cada vez se cubre de otra capa de hielo (NOAA NSSL).
- La racha de viento más fuerte medida en superficie (excluidos los tornados): 113,2 m/s (408 km/h) en
  la isla Barrow (Australia) el 10 de abril de 1996, durante el ciclón tropical Olivia (OMM, Archivo de
  Fenómenos Meteorológicos y Climáticos Extremos; Bureau of Meteorology).
- El desierto de Lut (Irán) dio la temperatura de superficie más alta registrada por el satélite
  MODIS: 70,7 °C en 2005 (temperatura del suelo, no del aire) (NASA Earth Observatory «The Hottest Spot
  on Earth», 2012). Estudios posteriores también sitúan en Lut el punto más caliente.
- Los pelos de Pele son hilos de vidrio volcánico, dorados, que se forman cuando el viento estira la
  lava de las fuentes y lagos de lava de Hawái: a menudo de menos de 1 mm de grosor y a veces de más de
  1 m de largo; llevan el nombre de Pele, diosa hawaiana de los volcanes (USGS HVO «Volcano Watch —
  Pele's hairs: a beautiful hazard», 2023; NPS Hawaiʻi Volcanoes).
- La erupción del Hunga Tonga-Hunga Haʻapai (15 de enero de 2022) lanzó su nube hasta 58 km, hasta la
  mesosfera: probablemente la más alta del registro por satélite (NASA Earth Observatory «Tonga Volcano
  Plume Reached the Mesosphere», 2022). Produjo la tormenta eléctrica más intensa jamás registrada: más
  de 192.000 rayos, con un máximo de 2.615 por minuto (USGS / AGU, 2023). Un avión comercial vuela a
  unos 10-11 km.
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-26-historia"
TITULO = "Viaje por el tiempo más salvaje de la Tierra"
VOZ = "em_alex"
VELOCIDAD = 1.0
MUSICA = 16

W, H = 1920, 1080
rng = np.random.default_rng(26)
LLUVIA = [(rng.uniform(0, W + 400), rng.uniform(0, H + 200), rng.uniform(30, 70), rng.uniform(900, 1400)) for _ in range(90)]
VIENTO = [(rng.uniform(0, W + 600), rng.uniform(120, 980), rng.uniform(120, 320), rng.uniform(1200, 2200)) for _ in range(28)]
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, 520), rng.uniform(2, 4.5)) for _ in range(60)]
PIEDRAS = [(rng.uniform(0, W), rng.uniform(905, 1070), rng.uniform(8, 22)) for _ in range(40)]
HILOS = [(rng.uniform(0, 1), rng.uniform(-60, 80), rng.uniform(90, 170), rng.uniform(0.6, 1.3), rng.uniform(0, 6.3)) for _ in range(34)]
RAYOS_T = [(rng.uniform(-1, 1), rng.uniform(0, 1), int(rng.integers(0, 1000))) for _ in range(16)]


# ================= piezas comunes =================
def cielo(top, bot, id_):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def bolas(circulos, relleno, borde=INK, lw=LW, op=1.0):
    """Varios círculos con un solo contorno exterior (nubes, humo)."""
    a = "".join(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r + lw / 2:.0f}' fill='{borde}'/>" for x, y, r in circulos)
    b = "".join(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='{relleno}'/>" for x, y, r in circulos)
    return f"<g opacity='{op:.2f}'>{a}{b}</g>"


def nube(x, y, sc, col="#fff", op=1.0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def nubarron(x, y, sc, col, t, fase=0.0):
    cs = [(x + dx * sc + 6 * math.sin(t * 0.8 + i + fase), y + dy * sc, r * sc) for i, (dx, dy, r) in
          enumerate([(-150, 20, 70), (-70, -25, 90), (30, -45, 105), (130, -10, 85), (200, 25, 60), (40, 30, 80), (-60, 35, 70)])]
    return bolas(cs, col, lw=7)


def lluvia(t, dx, dy, op, col="#cfe3ff", vel=1.0, n=90, grosor=4):
    s = []
    nrm = math.hypot(dx, dy)
    ux, uy = dx / nrm, dy / nrm
    for x0, y0, ln, v in LLUVIA[:n]:
        x = (x0 + t * v * vel * ux) % (W + 400) - 200
        y = (y0 + t * v * vel * uy) % (H + 200) - 100
        s.append(f"<line x1='{x:.0f}' y1='{y:.0f}' x2='{x + ux * ln:.0f}' y2='{y + uy * ln:.0f}' stroke='{col}' stroke-width='{grosor}' stroke-linecap='round'/>")
    return f"<g opacity='{op:.2f}'>{''.join(s)}</g>"


def rayo(x0, y0, x1, y1, semilla, ancho=1.0, op=1.0):
    r = np.random.default_rng(semilla)
    n = 7
    pts = []
    for i in range(n + 1):
        k = i / n
        jit = r.uniform(-45, 45) * ancho if 0 < i < n else 0
        pts.append((lerp(x0, x1, k) + jit, lerp(y0, y1, k)))
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f"<g opacity='{op:.2f}'><path d='{d}' fill='none' stroke='#fff6a8' stroke-width='{34 * ancho:.0f}' stroke-opacity='0.3' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{15 * ancho:.0f}' stroke-linejoin='round' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='#fffbe0' stroke-width='{7 * ancho:.0f}' stroke-linejoin='round' stroke-linecap='round'/></g>")


def destellos(cx, cy, k, n=10, r=220, col="#fff6a8"):
    if k <= 0 or k >= 1:
        return ""
    s = []
    for i in range(n):
        a = i / n * 2 * math.pi
        d = r * (0.4 + 0.6 * k)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        e = 18 * (1 - k) + 6
        s.append(f"<path d='M{x:.0f} {y - e:.0f} L{x + e * 0.3:.0f} {y:.0f} L{x:.0f} {y + e:.0f} L{x - e * 0.3:.0f} {y:.0f} Z' fill='{col}' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def zumbi(x, y, s, t, ang=0.0, guino=False, calor=0.0, sudor=0.0, pelo=0.0, viento=1.0, susto=0.0):
    """Zumbi: dron cazatormentas amarillo con visor, dos ojos luminosos, 2 hélices y un anemómetro en la cabeza."""
    parp = 0.12 if (t % 3.4) < 0.13 or guino else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    # brazos y hélices
    for sx in (-1, 1):
        g.append(f"<path d='M{sx * 80} -34 L{sx * 165} -80' stroke='{INK}' stroke-width='24' stroke-linecap='round'/>")
        g.append(f"<path d='M{sx * 80} -34 L{sx * 165} -80' stroke='#8d99a6' stroke-width='11' stroke-linecap='round'/>")
        w = 62 + 26 * abs(math.sin(t * 23 + sx))
        g.append(f"<ellipse cx='{sx * 165}' cy='-98' rx='{w:.0f}' ry='10' fill='#e6eef6' fill-opacity='0.6' stroke='{INK}' stroke-width='5'/>")
        g.append(f"<rect x='{sx * 165 - 13}' y='-106' width='26' height='30' rx='7' fill='#3a4656' stroke='{INK}' stroke-width='5'/>")
    # patas
    g.append(f"<path d='M-52 62 L-74 114 M52 62 L74 114' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>")
    g.append(f"<path d='M-108 116 L-42 116 M42 116 L108 116' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>")
    # anemómetro
    g.append(f"<line x1='0' y1='-80' x2='0' y2='-150' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
             f"<line x1='0' y1='-80' x2='0' y2='-150' stroke='#c9ced6' stroke-width='5' stroke-linecap='round'/>")
    a = t * 6 * viento
    copas = sorted([(math.sin(a + k * 2.094), a + k * 2.094) for k in range(3)])
    for prof, th in copas:
        cx, cy = 50 * math.cos(th), -152 + 9 * prof
        g.append(f"<line x1='0' y1='-152' x2='{cx:.1f}' y2='{cy:.1f}' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='14' fill='{mix('#c23a22', '#ff5a3c', (prof + 1) / 2)}' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='0' cy='-152' r='9' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    # cuerpo
    cuerpo = mix("#ffcc33", "#ff7a3d", calor)
    g.append(f"<ellipse cx='0' cy='0' rx='118' ry='86' fill='{cuerpo}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-104 36 Q0 92 104 36' fill='none' stroke='{mix('#f0a020', '#d85a2a', calor)}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<circle cx='-92' cy='-34' r='9' fill='{'#ff3b3b' if (t % 1.2) < 0.6 else '#7a2020'}' stroke='{INK}' stroke-width='4'/>")
    # melena de pelos de Pele (por encima del cuerpo, por debajo del visor)
    if pelo > 0:
        for i in range(12):
            lado = -1 if i < 6 else 1
            j = i % 6
            bx = lado * (14 + j * 16)
            by = -84 + (j * j) * 1.6
            L = (70 + (i * 37) % 50) * pelo
            sw = 8 * math.sin(t * 3 + i)
            d = f"M{bx} {by:.0f} q{lado * (40 + j * 8) + sw:.0f} {L * 0.15:.0f} {lado * (70 + j * 10) + sw:.0f} {L:.0f}"
            g.append(f"<path d='{d}' fill='none' stroke='#7a5320' stroke-width='7' stroke-linecap='round'/>"
                     f"<path d='{d}' fill='none' stroke='#f6cf62' stroke-width='3.5' stroke-linecap='round'/>")
    # visor con ojos
    g.append(f"<rect x='-80' y='-48' width='160' height='84' rx='40' fill='#1e2a38' stroke='{INK}' stroke-width='7'/>")
    ojo = 1 + 0.35 * susto
    for ex in (-34, 34):
        g.append(f"<g transform='translate({ex},-8) scale({ojo:.2f},{parp * ojo:.2f})'><ellipse rx='17' ry='21' fill='#7af0ff'/>"
                 f"<circle cx='-5' cy='-8' r='6' fill='#fff'/></g>")
    if susto > 0.5:
        g.append(f"<ellipse cx='0' cy='22' rx='12' ry='9' fill='none' stroke='#7af0ff' stroke-width='6'/>")
    else:
        g.append(f"<path d='M-22 18 Q0 32 22 18' fill='none' stroke='#7af0ff' stroke-width='6' stroke-linecap='round'/>")
    # gotas de sudor
    if sudor > 0:
        for i, (gx, gy) in enumerate(((112, -50), (-118, -10), (96, 20))):
            k = (t * 0.9 + i * 0.33) % 1
            g.append(f"<path d='M{gx} {gy + k * 40:.0f} q-11 18 0 24 q11 -6 0 -24 Z' fill='#9be3ff' stroke='{INK}' stroke-width='4' opacity='{sudor * (1 - k):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def granizo(x, y, r, capas=1, ang=0.0, semilla=0):
    """Piedra de granizo: bola irregular blanco-azulada con capas como una cebolla."""
    def contorno(rr, sem):
        pts = []
        for i in range(18):
            a = i / 18 * 2 * math.pi
            k = 1 + 0.07 * math.sin(5 * a + sem) + 0.05 * math.sin(3 * a + sem * 2)
            pts.append((rr * k * math.cos(a), rr * k * math.sin(a)))
        return "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"
    s = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f})'>",
         f"<path d='{contorno(r, semilla)}' fill='#e4f3ff' stroke='{INK}' stroke-width='{max(4, min(LW, r * 0.18)):.0f}' stroke-linejoin='round'/>"]
    for c in range(1, capas):
        rr = r * (1 - c / (capas + 0.6))
        s.append(f"<path d='{contorno(rr, semilla + c)}' fill='{mix('#e4f3ff', '#b8dcf5', c / capas)}' stroke='#8cbde0' stroke-width='{max(2, r * 0.05):.0f}'/>")
    s.append(f"<ellipse cx='{-r * 0.35:.1f}' cy='{-r * 0.4:.1f}' rx='{r * 0.22:.1f}' ry='{r * 0.13:.1f}' fill='#fff' transform='rotate(-30 {-r * 0.35:.1f} {-r * 0.4:.1f})'/></g>")
    return "".join(s)


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


def destello_pantalla(t, tiempos, col="#ffffff", fuerza=0.45):
    k = max([math.exp(-(t - tf) * 7) for tf in tiempos if t >= tf] or [0])
    return (f"<rect width='{W}' height='{H}' fill='{col}' opacity='{fuerza * k:.2f}'/>" if k > 0.02 else ""), k


# ================= capítulo 0: gancho =================
def esc_intro(t, dur, m):
    s = [cielo("#25264f", "#5d6596", "cie0")]
    # mar lejano y volcán en el horizonte
    s.append(f"<rect x='0' y='730' width='{W}' height='200' fill='#2e4f6e'/>")
    erupcion = seg(t, m[1] + 3.0, m[1] + 5.4)
    vx, vy = 1610, 740
    if erupcion > 0:
        cs = [(vx + 18 * math.sin(i * 1.3 + t), vy - 40 - i * 34 * erupcion, 22 + i * 9 * erupcion) for i in range(9)]
        s.append(bolas(cs, "#8f8794", lw=5))
        if (t * 3) % 1 < 0.25:
            s.append(rayo(vx - 20, vy - 260 * erupcion, vx + 30, vy - 120 * erupcion, int(t * 3), 0.45))
    s.append(f"<path d='M{vx - 170} 742 L{vx - 34} 690 L{vx + 34} 690 L{vx + 170} 742 Z' fill='#3b3346' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    s.append(f"<ellipse cx='{vx}' cy='692' rx='34' ry='7' fill='{mix('#3b3346', '#ff7a2a', erupcion)}'/>")
    # nubarrones
    for i, (cx, cy, sc) in enumerate([(220, 150, 1.2), (760, 110, 1.4), (1300, 170, 1.15), (1800, 120, 1.3)]):
        dx = (t * 22 * (1 + 0.25 * i)) % 2400
        s.append(nubarron((cx + dx) % 2400 - 250, cy, sc, ["#3d3f6e", "#474a7a", "#3a3c68", "#444777"][i], t, i))
    # destellos de rayos
    TF = [0.05, 4.2, m[1] + 2.0, m[2] + 0.3]
    fl, k = destello_pantalla(t, TF)
    if k > 0.3:
        bx = [1380, 900, 1180, 860][sum(1 for tf in TF if t >= tf) - 1]
        s.append(rayo(bx, 160, bx + 60, 760, int(bx), 1.1, min(1, k * 1.5)))
    s.append(lluvia(t, 0.25, 1, 0.55))
    # colinas
    s.append(f"<path d='M0 860 Q300 800 640 845 T1280 830 T1920 850 L1920 1080 L0 1080 Z' fill='#2f6b3a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 960 Q400 925 900 955 T1920 945 L1920 1080 L0 1080 Z' fill='#255a30'/>")
    # granizos pequeños que rebotan
    for i in range(7):
        p = (t * 0.7 + i / 7) % 1
        gx = 200 + i * 250 + 40 * math.sin(i)
        gy = lerp(-40, 870, min(1, p * 1.25)) - (80 * math.sin(math.pi * (p - 0.8) / 0.2) if p > 0.8 else 0)
        s.append(granizo(gx, gy, 12, 1, t * 200 + i * 40, i))
    # el granizo gigante cae a su lado
    caida = seg(t, m[0] + 0.6, m[0] + 1.5)
    if caida > 0:
        gy = lerp(-120, 852, caida * caida) if caida < 1 else 852
        rebote = math.exp(-(t - m[0] - 1.5) * 5) * abs(math.sin((t - m[0] - 1.5) * 12)) * 60 if t > m[0] + 1.5 else 0
        s.append(granizo(1060, gy - rebote - 20, 80, 4, 10, 3))
        if caida >= 1:
            pk = seg(t, m[0] + 1.5, m[0] + 2.6)
            for i in range(8):
                a = math.pi + i / 7 * math.pi
                s.append(f"<circle cx='{1060 + math.cos(a) * 160 * pk:.0f}' cy='{905 + math.sin(a) * 60 * pk:.0f}' r='{14 * (1 - pk) + 3:.0f}' fill='#cfe8ff' opacity='{1 - pk:.2f}'/>")
    # Zumbi
    entra = seg(t, 0, 1.4)
    vete = seg(t, dur - 1.6, dur)
    susto = seg(t, m[0] + 1.45, m[0] + 1.6) * (1 - seg(t, m[0] + 2.6, m[0] + 3.0))
    zx = lerp(140, 560, entra) + lerp(0, 1700, vete)
    zy = 470 + 16 * math.sin(t * 2.3) - lerp(0, 220, vete)
    s.append(zumbi(zx, zy, 0.95, t, ang=lerp(-8, 0, entra) + 4 * math.sin(t * 1.7) + 14 * vete, susto=susto,
                   guino=(m[1] + 1.0 < t < m[1] + 1.35)))
    s.append(fl)
    return "".join(s)


# ================= capítulo 1: granizo =================
def esc_granizo(t, dur, m):
    s = [cielo("#6f8fb8", "#d3dfea", "cie1")]
    # pradera de Dakota del Sur con granero y valla
    s.append(f"<path d='M0 840 Q480 815 960 835 T1920 830 L1920 1500 L0 1500 Z' fill='#b4c46a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 930 Q500 905 1000 925 T1920 915 L1920 1500 L0 1500 Z' fill='#9bb052'/>")
    s.append(f"<g transform='translate(1640,760)'><rect x='0' y='0' width='170' height='110' fill='#c8402f' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M-14 4 L85 -70 L184 4 Z' fill='#9e2f24' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='60' y='40' width='50' height='70' fill='#f6efe6' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M60 40 L110 110 M110 40 L60 110' stroke='{INK}' stroke-width='5'/></g>")
    for i in range(9):
        fx = 60 + i * 120
        s.append(f"<rect x='{fx}' y='880' width='12' height='50' fill='#8a5a34' stroke='{INK}' stroke-width='4'/>")
    s.append(f"<path d='M60 895 L1030 895 M60 915 L1030 915' stroke='{INK}' stroke-width='4'/>")
    # cortina de lluvia y granizo bajo la nube
    s.append(f"<g opacity='0.5'>" + "".join(f"<line x1='{720 + i * 38 + (t * 260 + i * 53) % 30:.0f}' y1='{690 + (t * 900 + i * 97) % 160:.0f}' x2='{712 + i * 38 + (t * 260 + i * 53) % 30:.0f}' y2='{735 + (t * 900 + i * 97) % 160:.0f}' stroke='#7f8fa6' stroke-width='5' stroke-linecap='round'/>" for i in range(16)) + "</g>")
    # cumulonimbo con yunque
    cx = 1000
    s.append("<g transform='translate(0,45)'>")
    s.append(f"<path d='M500 230 Q560 150 760 160 L1260 160 Q1460 150 1520 230 Q1380 250 1250 270 L760 270 Q620 250 500 230 Z' fill='#eef2f7' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    torre = [(cx + dx + 5 * math.sin(t + i), cy, r) for i, (dx, cy, r) in enumerate(
        [(-200, 620, 130), (-60, 640, 150), (110, 630, 140), (230, 600, 110), (-260, 520, 100), (-130, 470, 140),
         (40, 430, 160), (190, 470, 120), (-90, 330, 120), (80, 320, 130), (0, 260, 110)])]
    s.append(bolas(torre, "#e6ebf2"))
    s.append(f"<path d='M770 680 Q1000 745 1250 680 L1250 700 Q1000 770 770 700 Z' fill='#9aa6b8'/>")
    for x0, y0, r0 in [(-120, 520, 60), (90, 560, 70), (-30, 390, 55)]:
        s.append(f"<circle cx='{cx + x0}' cy='{y0}' r='{r0}' fill='#cdd5e0'/>")
    s.append("</g>")
    # corrientes que suben (frase 1)
    sube = seg(t, m[1] - 0.2, m[1] + 0.8) * (1 - seg(t, m[3] - 0.5, m[3]))
    if sube > 0:
        for i in range(3):
            ay = 695 - ((t * 0.8 + i / 3) % 1) * 330
            ax = cx - 70 + i * 70
            s.append(f"<g transform='translate({ax},{ay:.0f})' opacity='{sube * 0.9:.2f}'><rect x='-14' y='0' width='28' height='70' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>"
                     f"<path d='M-36 4 L36 4 L0 -44 Z' fill='#ffd23f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # la bolita sube y baja y crece por capas (frase 2)
    ciclo = (t - m[1]) * 0.42
    if m[1] < t < m[3]:
        p = max(0.0, ciclo)
        vueltas = min(4.0, p)
        gx = cx + 210 * math.sin(2 * math.pi * p)
        gy = 515 + 190 * math.cos(2 * math.pi * p)
        s.append(granizo(gx, gy, 16 + 10 * vueltas, 1 + int(vueltas), t * 90, 2))
    # cae la piedra gigante (frase 3)
    cae = seg(t, m[3] + 0.2, m[3] + 1.0)
    suelo_y = 838
    choque = t > m[3] + 1.0
    tem = (math.exp(-(t - m[3] - 1.0) * 6) if choque else 0)
    zk = seg(t, m[3] + 1.6, m[3] + 3.2)
    z = lerp(1.0, 1.75, zk)
    zx_, zy_ = lerp(1200, 1110, zk), lerp(838, 640, zk)
    escena = "".join(s)
    s = [f"<g transform='translate({12 * tem * math.sin(t * 80):.1f},{8 * tem * math.cos(t * 70):.1f})'>",
         f"<g transform='translate({zx_:.1f},{zy_:.1f}) scale({z:.3f}) translate(-1200,-838)'>", escena]
    if t > m[3]:
        gy = lerp(745, suelo_y, cae * cae)
        gx = lerp(1040, 1200, cae)
        s.append(f"<ellipse cx='1200' cy='{suelo_y + 46}' rx='{70 * cae:.0f}' ry='12' fill='#000' opacity='{0.2 * cae:.2f}'/>")
        s.append(granizo(gx, gy, 58, 5, 20 * (1 - cae), 5))
        if choque:
            pk = seg(t, m[3] + 1.0, m[3] + 2.0)
            for i in range(9):
                a = math.pi + i / 8 * math.pi
                s.append(f"<circle cx='{1200 + math.cos(a) * 150 * pk:.0f}' cy='{suelo_y + 40 + math.sin(a) * 70 * pk:.0f}' r='{16 * (1 - pk) + 3:.0f}' fill='#d9c79a' opacity='{1 - pk:.2f}'/>")
    # balón de voleibol al lado (frase 4)
    bal = seg(t, m[4] - 0.1, m[4] + 0.6)
    if bal > 0:
        bx, by, br = 1345, suelo_y + 2, 62 * (0.6 + 0.4 * ease(bal))
        s.append(f"<g transform='translate({bx},{by:.0f})' opacity='{min(1, bal * 2):.2f}'>"
                 f"<circle r='{br:.0f}' fill='#ffffff' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M{-br:.0f} 0 Q0 {-br * 0.5:.0f} {br:.0f} 0' fill='none' stroke='#2f6fd8' stroke-width='9'/>"
                 f"<path d='M{-br * 0.5:.0f} {-br * 0.86:.0f} Q{br * 0.2:.0f} 0 {-br * 0.3:.0f} {br * 0.95:.0f}' fill='none' stroke='#ffd23f' stroke-width='9'/>"
                 f"<path d='M{br * 0.45:.0f} {-br * 0.88:.0f} Q{br * 0.1:.0f} {-br * 0.2:.0f} {br * 0.85:.0f} {br * 0.5:.0f}' fill='none' stroke='#2f6fd8' stroke-width='9'/>"
                 f"<circle r='{br:.0f}' fill='none' stroke='{INK}' stroke-width='7'/></g>")
        s.append(destellos(1270, suelo_y, seg(t, m[4] + 0.2, m[4] + 1.8), 12, 240))
    s.append("</g>")
    # Zumbi mira desde la izquierda (fuera del zoom)
    mira = seg(t, m[3] + 0.9, m[3] + 1.2) * (1 - seg(t, m[3] + 2.2, m[3] + 2.8))
    s.append(zumbi(330 + 15 * math.sin(t * 0.7), 500 + 18 * math.sin(t * 1.9), 0.8, t, ang=4 * math.sin(t * 1.3), susto=mira,
                   guino=(m[4] + 1.6 < t < m[4] + 2.0)))
    s.append("</g>")
    return "".join(s)


# ================= capítulo 2: viento =================
def palmera(x, base, alto, b, t, fase):
    wob = 0.06 * math.sin(t * (5 + 4 * b) + fase) * (0.3 + b)
    bb = clamp(b + wob, 0, 1.2)
    tx, ty = x + bb * alto * 0.75, base - alto * (1 - 0.32 * bb)
    cx, cy = x + bb * alto * 0.1, base - alto * 0.6
    s = [f"<path d='M{x} {base} Q{cx:.0f} {cy:.0f} {tx:.0f} {ty:.0f}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>",
         f"<path d='M{x} {base} Q{cx:.0f} {cy:.0f} {tx:.0f} {ty:.0f}' fill='none' stroke='#a8743e' stroke-width='22' stroke-linecap='round'/>"]
    for i in range(4):
        k = 0.2 + i * 0.2
        px = (1 - k) ** 2 * x + 2 * (1 - k) * k * cx + k * k * tx
        py = (1 - k) ** 2 * base + 2 * (1 - k) * k * cy + k * k * ty
        s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='5' fill='#7a5228'/>")
    for j, a0 in enumerate([-160, -125, -80, -35, 5, 40]):
        a = lerp(a0, 10 + (j - 2.5) * 8, clamp(bb * 0.85)) + 6 * math.sin(t * 9 + j + fase) * b
        L = 175
        s.append(f"<g transform='translate({tx:.0f},{ty:.0f}) rotate({a:.1f})'>"
                 f"<path d='M0 0 Q{L * 0.5:.0f} -34 {L} 6 Q{L * 0.5:.0f} 18 0 0 Z' fill='#3fa84a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M8 0 Q{L * 0.5:.0f} -12 {L - 10} 6' fill='none' stroke='#2a7a34' stroke-width='4'/></g>")
    s.append(f"<circle cx='{tx - 12:.0f}' cy='{ty + 14:.0f}' r='17' fill='#7a5228' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='{tx + 12:.0f}' cy='{ty + 18:.0f}' r='17' fill='#6a4520' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def velocimetro(cx, cy, r, k, op, t):
    if op <= 0:
        return ""
    s = [f"<g opacity='{op:.2f}' transform='translate({cx},{cy}) scale({0.7 + 0.3 * ease(op):.2f})'>",
         f"<path d='M{-r - 22} 30 L{-r - 22} 0 A{r + 22} {r + 22} 0 0 1 {r + 22} 0 L{r + 22} 30 Z' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    cols = ["#4fd36b", "#ffe14d", "#ff9a2e", "#ff3b3b"]
    for i, c in enumerate(cols):
        a0, a1 = math.pi + i * math.pi / 4, math.pi + (i + 1) * math.pi / 4
        rr = r - 18
        s.append(f"<path d='M{rr * math.cos(a0):.1f} {rr * math.sin(a0):.1f} A{rr} {rr} 0 0 1 {rr * math.cos(a1):.1f} {rr * math.sin(a1):.1f}' fill='none' stroke='{c}' stroke-width='30'/>")
    for i in range(9):
        a = math.pi + i * math.pi / 8
        s.append(f"<line x1='{(r - 46) * math.cos(a):.1f}' y1='{(r - 46) * math.sin(a):.1f}' x2='{(r - 64) * math.cos(a):.1f}' y2='{(r - 64) * math.sin(a):.1f}' stroke='{INK}' stroke-width='6'/>")
    temb = 0.04 * math.sin(t * 40) * (k > 0.95)
    a = math.pi + math.pi * clamp(k + temb, 0, 1.02)
    s.append(f"<line x1='0' y1='0' x2='{(r - 30) * math.cos(a):.1f}' y2='{(r - 30) * math.sin(a):.1f}' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
             f"<line x1='0' y1='0' x2='{(r - 30) * math.cos(a):.1f}' y2='{(r - 30) * math.sin(a):.1f}' stroke='#e8382f' stroke-width='8' stroke-linecap='round'/>"
             f"<circle r='18' fill='{INK}'/></g>")
    return "".join(s)


def esc_viento(t, dur, m):
    k = seg(t, 0, m[3]) * 0.55 + seg(t, m[3], m[3] + 1.2) * 0.45      # fuerza del viento
    calma = seg(t, m[5] - 0.3, dur)
    k *= 1 - 0.7 * calma
    s = [cielo(mix("#48656a", "#f0b866", calma), mix("#9fb5a8", "#ffe3a8", calma), "cie2")]
    for i, (cx, cy, sc) in enumerate([(200, 170, 1.0), (900, 120, 1.3), (1500, 200, 1.1)]):
        dx = (t * (60 + 400 * k) + i * 700) % 2500
        s.append(nubarron(dx - 300, cy, sc, mix("#5e7377", "#ffd9a0", calma), t, i))
    # mar con olas
    s.append(f"<rect x='0' y='640' width='{W}' height='{H}' fill='{mix('#2c6e8a', '#3f8fb0', calma)}'/>")
    for fila in range(4):
        y0 = 660 + fila * 70
        amp = 10 + 26 * k
        d = f"M0 {y0} " + " ".join(f"Q{x + 60:.0f} {y0 - amp * math.sin(t * 4 + x * 0.01 + fila):.0f} {x + 120:.0f} {y0}" for x in range(0, W, 120))
        s.append(f"<path d='{d}' fill='none' stroke='#d8f3ff' stroke-width='7' stroke-linecap='round' opacity='0.75'/>")
    # isla
    s.append(f"<path d='M560 770 Q700 690 1000 685 Q1300 690 1440 770 Z' fill='#f2d48a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for x, al, f in ((720, 330, 0.0), (990, 390, 1.7), (1240, 300, 3.1)):
        s.append(palmera(x, 735, al, 0.15 + 0.85 * k, t, f))
    # rachas de viento
    for x0, y0, ln, v in VIENTO:
        x = (x0 + t * v * (0.3 + k)) % (W + 600) - 300
        y = y0 + 20 * math.sin(t * 3 + x0)
        s.append(f"<path d='M{x:.0f} {y:.0f} q{ln * 0.5:.0f} {-18:.0f} {ln:.0f} 0' fill='none' stroke='#ffffff' stroke-width='6' stroke-linecap='round' opacity='{0.25 + 0.55 * k:.2f}'/>")
    s.append(lluvia(t, 1, 0.18 + 0.6 * (1 - k), 0.25 + 0.4 * k * (1 - calma), vel=0.6 + k))
    # hojas y cocos que salen volando (frase 4)
    vuela = seg(t, m[4] - 0.3, m[4] + 0.2) * (1 - calma)
    if vuela > 0:
        for i in range(6):
            p = ((t - m[4]) * 0.7 + i / 6) % 1
            hx, hy = 900 + p * 1200, 420 + 160 * math.sin(i * 2.1) - 60 * math.sin(p * 6)
            s.append(f"<g transform='translate({hx:.0f},{hy:.0f}) rotate({t * 400 + i * 60:.0f})' opacity='{vuela:.2f}'>"
                     + (f"<path d='M-40 0 Q0 -18 40 0 Q0 12 -40 0 Z' fill='#3fa84a' stroke='{INK}' stroke-width='5'/>" if i % 2 else
                        f"<circle r='16' fill='#7a5228' stroke='{INK}' stroke-width='5'/>") + "</g>")
    # velocímetro (sin números): aparece con el anemómetro y se dispara en la frase 3
    vk = lerp(0.18, 0.5, seg(t, m[1], m[2])) + 0.5 * seg(t, m[3] + 0.3, m[3] + 1.8)
    vk *= 1 - 0.6 * calma
    s.append(velocimetro(1640, 560, 170, vk, seg(t, m[1] + 0.3, m[1] + 0.9), t))
    if t > m[3] + 1.6:
        s.append(destellos(1640, 470, seg(t, m[3] + 1.6, m[3] + 3.2), 12, 260, "#ffffff"))
    # Zumbi aguantando el viento; el anemómetro gira cada vez más deprisa
    temb = 6 * k * math.sin(t * 31)
    zx = 400 + 40 * k * math.sin(t * 2.2) + temb
    zy = 440 + 20 * math.sin(t * 1.7) + temb * 0.6
    zoomk = seg(t, m[1] - 0.2, m[1] + 0.8) * (1 - seg(t, m[2] - 0.6, m[2] + 0.2))
    s.append(zumbi(zx + 90 * zoomk, zy + 40 * zoomk, 0.85 + 0.35 * zoomk, t, ang=-6 + 26 * k, viento=1 + 5 * k,
                   susto=seg(t, m[4] - 0.2, m[4]) * (1 - calma)))
    return "".join(s)


# ================= capítulo 3: desierto de Lut =================
def termometro(x, y, k, op):
    alto = 300
    return (f"<g transform='translate({x},{y})' opacity='{op:.2f}'>"
            f"<rect x='-26' y='{-alto}' width='52' height='{alto + 10}' rx='26' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-12' y='{-alto * k + 10:.0f}' width='24' height='{alto * k:.0f}' fill='#e8382f'/>"
            f"<circle cy='40' r='50' fill='#e8382f' stroke='{INK}' stroke-width='{LW}'/>"
            + "".join(f"<line x1='26' y1='{-alto + 40 + i * 50}' x2='6' y2='{-alto + 40 + i * 50}' stroke='{INK}' stroke-width='5'/>" for i in range(5))
            + "</g>")


def satelite(x, y, s, ang=0.0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.1f}) scale({s:.2f})'>"
            f"<rect x='-150' y='-24' width='100' height='48' fill='#3a6fd8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-125 -24 L-125 24 M-100 -24 L-100 24 M-75 -24 L-75 24' stroke='#9cc2ff' stroke-width='3'/>"
            f"<rect x='50' y='-24' width='100' height='48' fill='#3a6fd8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M75 -24 L75 24 M100 -24 L100 24 M125 -24 L125 24' stroke='#9cc2ff' stroke-width='3'/>"
            f"<line x1='-50' y1='0' x2='50' y2='0' stroke='{INK}' stroke-width='8'/>"
            f"<rect x='-42' y='-42' width='84' height='84' rx='10' fill='#e8c25a' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='0' cy='42' r='14' fill='#2a3550' stroke='{INK}' stroke-width='5'/></g>")


def esc_lut(t, dur, m):
    s = [cielo("#ffc96b", "#fff3cf", "cie3")]
    # sol abrasador
    gir = t * 12
    s.append(f"<g transform='translate(1480,250) rotate({gir:.1f})'>" + "".join(
        f"<path d='M-14 -150 L14 -150 L0 -200 Z' fill='#ffb030' transform='rotate({a})' opacity='0.8'/>" for a in range(0, 360, 30)) + "</g>")
    s.append(f"<circle cx='1480' cy='250' r='{112 + 4 * math.sin(t * 3):.0f}' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>")
    # dunas lejanas y kaluts (crestas alargadas que talla el viento)
    s.append(f"<path d='M0 640 Q240 560 520 625 Q760 540 1060 620 Q1360 560 1640 615 Q1800 580 1920 610 L1920 760 L0 760 Z' fill='#f0a85a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for i, (x, w, h) in enumerate([(120, 330, 120), (560, 280, 95), (980, 360, 130), (1450, 300, 110)]):
        s.append(f"<path d='M{x} 760 Q{x + 20} {760 - h} {x + w * 0.35:.0f} {760 - h} L{x + w * 0.8:.0f} {760 - h * 0.85:.0f} Q{x + w} {760 - h * 0.6:.0f} {x + w + 40} 760 Z' fill='#c98a4e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M{x + w * 0.45:.0f} {760 - h + 6} Q{x + w * 0.6:.0f} {760 - h * 0.4:.0f} {x + w * 0.55:.0f} 760' fill='none' stroke='#a86d3a' stroke-width='6'/>")
    s.append(f"<rect x='0' y='750' width='{W}' height='120' fill='#d9995a'/>")
    # meseta de piedras volcánicas oscuras
    s.append(f"<path d='M0 850 Q500 820 960 840 T1920 835 L1920 1080 L0 1080 Z' fill='#4a3b34' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, r in PIEDRAS:
        s.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{r:.0f}' ry='{r * 0.55:.0f}' fill='#2f2622'/>")
    # aire que tiembla por el calor
    for i in range(10):
        hx = 100 + i * 190
        k = (t * 0.5 + i * 0.17) % 1
        y0 = 830 - k * 300
        s.append(f"<path d='M{hx} {y0:.0f} q15 -20 0 -40 q-15 -20 0 -40' fill='none' stroke='#ffffff' stroke-width='5' stroke-linecap='round' opacity='{0.45 * math.sin(math.pi * k):.2f}'/>")
    # satélite que mide desde el espacio (frase 2)
    sat = seg(t, m[2] - 0.8, m[2] + 1.0)
    sale = seg(t, m[3] + 1.0, m[3] + 3.0)
    if sat > 0 and sale < 1:
        sx = lerp(-200, 1120, sat) + lerp(0, 1100, sale)
        haz = seg(t, m[2] + 0.4, m[2] + 1.0) * (1 - seg(t, m[3] + 0.6, m[3] + 1.2))
        if haz > 0:
            s.append(f"<path d='M{sx - 14:.0f} 460 L{sx + 14:.0f} 460 L{sx + 160:.0f} 860 L{sx - 160:.0f} 860 Z' fill='#ff6a3d' opacity='{0.28 * haz:.2f}'/>")
            s.append(f"<ellipse cx='{sx:.0f}' cy='860' rx='160' ry='22' fill='#ff3b1f' opacity='{0.4 * haz:.2f}'/>")
        s.append(satelite(sx, 430, 0.75, 4 * math.sin(t)))
    # termómetro que sube hasta arriba
    tk = lerp(0.35, 1.0, seg(t, m[2] + 1.0, m[2] + 3.2))
    top = seg(t, m[1] - 0.2, m[1] + 0.4)
    s.append(termometro(1700, 780, tk, top))
    if tk > 0.98:
        s.append(destellos(1700, 480, seg(t, m[2] + 3.2, m[2] + 4.8), 12, 200, "#ff6a3d"))
    # el huevo (frase 4)
    zx, zy = 640 + 20 * math.sin(t * 0.8), 480 + 16 * math.sin(t * 1.6)
    suelta = m[4] + 0.6
    if t < suelta:
        s.append(f"<ellipse cx='{zx:.0f}' cy='{zy + 150:.0f}' rx='30' ry='38' fill='#fff6e8' stroke='{INK}' stroke-width='6'/>")
    else:
        cae = seg(t, suelta, suelta + 0.5)
        if cae < 1:
            ey = lerp(zy + 150, 880, cae * cae)
            s.append(f"<ellipse cx='{zx:.0f}' cy='{ey:.0f}' rx='30' ry='38' fill='#fff6e8' stroke='{INK}' stroke-width='6'/>")
        else:
            ex = 640
            s.append(f"<g transform='translate({ex},870) scale({1 + 0.45 * seg(t, suelta + 0.5, suelta + 0.9):.2f}) translate({-ex},-870)'>")
            fr = seg(t, suelta + 0.5, suelta + 2.5)
            clara = mix("#e8f0e0", "#ffffff", fr)
            s.append(f"<path d='M{ex - 95:.0f} 885 Q{ex - 100:.0f} 850 {ex - 40:.0f} 852 Q{ex:.0f} 830 {ex + 50:.0f} 850 Q{ex + 110:.0f} 852 {ex + 95:.0f} 885 Q{ex + 40:.0f} 905 {ex - 95:.0f} 885 Z' "
                     f"fill='{clara}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
            s.append(f"<circle cx='{ex + 8:.0f}' cy='868' r='26' fill='#ffb020' stroke='{INK}' stroke-width='6'/><circle cx='{ex:.0f}' cy='860' r='7' fill='#fff2c0'/>")
            for i in range(6):
                bk = (t * 2.2 + i / 6) % 1
                s.append(f"<circle cx='{ex - 70 + i * 28:.0f}' cy='{880 - bk * 30:.0f}' r='{4 + 4 * bk:.0f}' fill='none' stroke='#ffffff' stroke-width='3' opacity='{1 - bk:.2f}'/>")
            for i in range(3):
                vk = (t * 0.6 + i / 3) % 1
                s.append(f"<path d='M{ex - 40 + i * 40:.0f} {840 - vk * 150:.0f} q14 -20 0 -40 q-14 -20 0 -40' fill='none' stroke='#ffffff' stroke-width='7' stroke-linecap='round' opacity='{0.7 * math.sin(math.pi * vk):.2f}'/>")
            s.append("</g>")
    calor = seg(t, m[1], m[3] + 1)
    s.append(zumbi(zx, zy, 0.9, t, ang=3 * math.sin(t * 1.4), calor=0.6 * calor, sudor=calor,
                   guino=(m[4] + 3.2 < t < m[4] + 3.6)))
    return "".join(s)


# ================= capítulo 4: pelos de Pele =================
def fuente_lava(cx, cy, t, alto, k):
    if k <= 0:
        return ""
    s = [f"<circle cx='{cx}' cy='{cy - alto * 0.4:.0f}' r='{alto * 0.75:.0f}' fill='#ff9a3d' opacity='{0.16 * k:.2f}'/>"]
    for i in range(30):
        p = (t * 0.75 + i / 30) % 1
        vx = (((i * 37) % 21) / 20 - 0.5) * 380
        hh = alto * k * (0.55 + 0.45 * ((i * 53) % 11) / 10)
        x = cx + vx * p
        y = cy - 4 * hh * p * (1 - p)
        r = 7 + (i % 4) * 3
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r}' fill='{mix('#fff27a', '#ff4a1f', p)}' stroke='{INK}' stroke-width='4'/>")
    h = alto * k * (0.85 + 0.15 * math.sin(t * 7))
    pts = []
    for i in range(9):
        a = i / 8
        pts.append((cx + (a - 0.5) * 110 + 14 * math.sin(t * 9 + i), cy - h * (0.35 + 0.65 * math.sin(math.pi * a)) + 10 * math.sin(t * 11 + i * 2)))
    d = f"M{cx - 70} {cy} " + " ".join(f"L{x:.0f} {y:.0f}" for x, y in pts) + f" L{cx + 70} {cy} Z"
    s.append(f"<path d='{d}' fill='#ff7a1f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    s.append(f"<path d='M{cx - 36} {cy} Q{cx} {cy - h * 0.75:.0f} {cx + 36} {cy} Z' fill='#ffd84a'/>")
    return "".join(s)


def hilo(x, y, L, ang, t, fase, op):
    d = f"M{x:.0f} {y:.0f} q{L * 0.25:.0f} {-14 * math.sin(t * 3 + fase):.0f} {L * 0.5:.0f} 0 t{L * 0.5:.0f} 0"
    return (f"<g transform='rotate({ang:.0f} {x:.0f} {y:.0f})' opacity='{op:.2f}'>"
            f"<path d='{d}' fill='none' stroke='#7a5320' stroke-width='6' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='#f6cf62' stroke-width='3' stroke-linecap='round'/></g>")


def esc_pele(t, dur, m):
    s = [cielo("#2b1f4d", "#ef8a52", "cie4")]
    for x, y, r in ESTRELLAS[:25]:
        s.append(f"<circle cx='{x:.0f}' cy='{y * 0.6:.0f}' r='{r * 0.7:.1f}' fill='#fff' opacity='{0.4 + 0.3 * math.sin(t * 2 + x):.2f}'/>")
    # mar al fondo
    s.append(f"<rect x='0' y='700' width='{W}' height='200' fill='#3c4f86'/>")
    for i in range(6):
        s.append(f"<path d='M{(i * 340 + t * 30) % 2100 - 100:.0f} {730 + (i * 23) % 60} q30 -10 60 0' fill='none' stroke='#ffb27a' stroke-width='5' stroke-linecap='round' opacity='0.6'/>")
    # volcán con ríos de lava
    vx, vy = 1300, 560
    s.append(f"<path d='M760 900 Q980 700 {vx - 90} {vy} L{vx + 90} {vy} Q1640 700 1880 900 Z' fill='#3b2f33' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i, (x1, y1) in enumerate([(1080, 880), (1460, 890), (1290, 900)]):
        brillo = 0.75 + 0.25 * math.sin(t * 3 + i)
        s.append(f"<path d='M{vx - 30 + i * 30} {vy + 10} Q{(vx + x1) / 2 + 40 * math.sin(i):.0f} {(vy + y1) / 2:.0f} {x1} {y1}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
                 f"<path d='M{vx - 30 + i * 30} {vy + 10} Q{(vx + x1) / 2 + 40 * math.sin(i):.0f} {(vy + y1) / 2:.0f} {x1} {y1}' fill='none' stroke='{mix('#ff4a1f', '#ffd84a', brillo)}' stroke-width='12' stroke-linecap='round'/>")
    s.append(f"<ellipse cx='{vx}' cy='{vy}' rx='92' ry='18' fill='#ff7a1f' stroke='{INK}' stroke-width='7'/>")
    fk = seg(t, 0, 1.0) * 0.6 + seg(t, m[1] - 0.2, m[1] + 0.8) * 0.4
    s.append(fuente_lava(vx, vy, t, 300, fk))
    # hilos de cristal dorado que el viento arrastra hacia la izquierda (frase 2)
    hil = seg(t, m[2] - 0.2, m[2] + 1.5)
    if hil > 0:
        n = int(len(HILOS) * hil)
        for i, (ph, dy, L, v, f) in enumerate(HILOS[:n]):
            p = (t * 0.16 * v + ph) % 1
            hx = lerp(vx - 60, -200, p)
            hy = lerp(vy - 220 + dy, 560 + dy * 2, p) + 40 * math.sin(p * 9 + f)
            s.append(hilo(hx, hy, L * (0.4 + 0.6 * min(1, p * 4)), -10 + 20 * math.sin(f + t), t, f, min(1, p * 6) * (1 - seg(p, 0.85, 1))))
    s.append(f"<path d='M0 885 L{W} 885 L{W} {H} L0 {H} Z' fill='#2c2226'/>")
    # primer plano: hierba con hilos dorados posados
    s.append(f"<path d='M0 860 Q300 820 620 850 Q760 860 820 900 L820 1080 L0 1080 Z' fill='#3f8f4a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(9):
        hx0 = 40 + i * 85
        s.append(f"<path d='M{hx0} 900 q10 -50 -6 -80 M{hx0 + 20} 900 q-4 -40 14 -66' fill='none' stroke='#2a6b34' stroke-width='7' stroke-linecap='round'/>")
    posados = seg(t, m[3] - 0.3, m[3] + 1.5)
    for i in range(int(14 * posados)):
        s.append(hilo(30 + i * 52, 880 + (i * 17) % 30, 90 + (i * 29) % 60, -6 + (i * 13) % 12, 0, i, 1))
    # Zumbi atrapa los hilos: le sale una melena dorada (frase 4)
    pelo = seg(t, m[4] + 0.6, m[4] + 2.0)
    zx, zy = 470 + 25 * math.sin(t * 0.7), 470 + 18 * math.sin(t * 1.5)
    s.append(zumbi(zx, zy, 0.92, t, ang=-4 + 4 * math.sin(t * 1.2), pelo=pelo, calor=0.15,
                   guino=(m[4] + 2.4 < t < m[4] + 2.8)))
    s.append(destellos(zx, zy - 60, seg(t, m[4] + 1.0, m[4] + 2.6), 12, 230, "#ffe08a"))
    return "".join(s)


# ================= capítulo 5: Hunga Tonga =================
def avion(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-90 0 Q-90 -16 -60 -16 L70 -16 Q100 -14 110 0 Q100 14 70 14 L-60 14 Q-90 14 -90 0 Z' fill='#ffffff' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-70 -14 L-96 -56 L-66 -56 L-40 -14 Z' fill='#e8382f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M-10 4 L-50 50 L-24 50 L30 4 Z' fill='#c9d6e6' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            + "".join(f"<circle cx='{-40 + i * 20}' cy='-4' r='4' fill='#2a3550'/>" for i in range(6)) + "</g>")


def esc_tonga(t, dur, m):
    t_ex = m[1] + 2.2                       # "...explotó"
    sube = seg(t, t_ex, m[2] + 2.6)         # la nube sube hasta 58 km
    alt = 58 * sube
    ppk = lerp(40, (860 - 470) / 58, seg(t, t_ex + 1.0, m[2] + 2.8))   # píxeles por km: la cámara se aleja
    alto = seg(t, t_ex + 1.0, m[2] + 2.8)
    # cielo: más oscuro arriba cuanto más alto miramos
    s = [cielo(mix("#4ea8e8", "#140f3a", alto), mix("#bfe6ff", "#7cc4f0", alto), "cie5")]
    for x, y, r in ESTRELLAS:
        s.append(f"<circle cx='{x:.0f}' cy='{y * 0.7:.0f}' r='{r * 0.8:.1f}' fill='#fff' opacity='{alto * (0.5 + 0.3 * math.sin(t * 2 + x)):.2f}'/>")
    # línea de la mesosfera (frase 3)
    mes = seg(t, m[3] - 0.2, m[3] + 0.8)
    if mes > 0:
        ym = 860 - 50 * ppk
        s.append(f"<rect x='0' y='{ym - 60:.0f}' width='{W}' height='60' fill='#c77dff' opacity='{0.18 * mes:.2f}'/>")
        s.append(f"<path d='M0 {ym:.0f} L{W} {ym:.0f}' stroke='#e2b8ff' stroke-width='6' stroke-dasharray='28 18' opacity='{mes:.2f}'/>")
    # avión a 10 km
    ya = 860 - 10 * ppk
    ax = (180 + t * 70) % 2300 - 200
    s.append(avion(ax, ya, 0.55 + 0.45 * ppk / 40))
    vx = 1180
    # nube volcánica
    if alt > 0.3:
        cs = []
        n = 16
        for i in range(n + 1):
            a = alt * i / n
            r_km = 1.8 + 0.22 * a
            cs.append((vx + 30 * math.sin(i * 1.7 + t * 0.8) * min(1, ppk / 20), 860 - a * ppk, max(18, r_km * ppk)))
        if alt > 22:   # paraguas en la estratosfera
            ua = min(1, (alt - 22) / 20)
            for j in range(-4, 5):
                cs.append((vx + j * 95 * ua, 860 - 30 * ppk + 15 * math.sin(j + t), (55 + 10 * (j % 2)) * (0.4 + 0.6 * ua)))
        s.append(bolas(cs, "#b4a898"))
        s.append(bolas([(x - r * 0.25, y + r * 0.2, r * 0.6) for x, y, r in cs[::2]], "#988c7e", lw=0, op=0.6))
    # rayos dentro de la nube (frase 4)
    ry = seg(t, m[4] - 0.1, m[4] + 0.4)
    if ry > 0 and alt > 20:
        paso = int(t * 14)
        for i, (fx, fy, sem) in enumerate(RAYOS_T):
            if (paso + i * 7) % 2 == 0:
                a0 = 20 + 10 * fy
                y0 = 860 - a0 * ppk
                ancho = (1.8 + 0.22 * a0) * ppk
                x0 = vx + fx * max(ancho * 0.7, 230)
                s.append(f"<circle cx='{x0:.0f}' cy='{y0 + 50:.0f}' r='90' fill='#fff6a8' opacity='{0.4 * ry:.2f}'/>")
                s.append(rayo(x0, y0 - 40, x0 + 60 * math.sin(sem), y0 + 130, sem + paso, 0.6, ry))
    # mar
    s.append(f"<rect x='0' y='860' width='{W}' height='220' fill='#1f5f9e'/>")
    for fila in range(3):
        y0 = 880 + fila * 55
        d = f"M0 {y0} " + " ".join(f"Q{x + 60:.0f} {y0 - 10 * math.sin(t * 2 + x * 0.02 + fila):.0f} {x + 120:.0f} {y0}" for x in range(0, W, 120))
        s.append(f"<path d='{d}' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
    s.append(f"<path d='M0 860 L{W} 860' stroke='{INK}' stroke-width='{LW}'/>")
    # islita antes de la explosión
    isla = 1 - seg(t, t_ex - 0.1, t_ex + 0.3)
    if isla > 0:
        s.append(f"<path d='M{vx - 150} 862 Q{vx - 60} 790 {vx} 792 Q{vx + 60} 790 {vx + 150} 862 Z' fill='#7a6a4a' stroke='{INK}' stroke-width='7' opacity='{isla:.2f}'/>"
                 f"<path d='M{vx - 100} 840 Q{vx} 800 {vx + 100} 840' fill='none' stroke='#5a9a4a' stroke-width='10' opacity='{isla:.2f}'/>")
        if t < t_ex:
            for i in range(4):
                k = (t * 0.5 + i / 4) % 1
                s.append(f"<circle cx='{vx + 20 * math.sin(i):.0f}' cy='{800 - k * 120:.0f}' r='{16 + 30 * k:.0f}' fill='#ffffff' opacity='{0.5 * (1 - k):.2f}'/>")
    # onda expansiva
    onda = seg(t, t_ex, t_ex + 2.2)
    if 0 < onda < 1:
        s.append(f"<circle cx='{vx}' cy='860' r='{40 + 1800 * onda:.0f}' fill='none' stroke='#ffffff' stroke-width='{24 * (1 - onda) + 4:.0f}' opacity='{0.8 * (1 - onda):.2f}'/>")
    # Zumbi lo mira todo desde lejos
    temb = 8 * math.exp(-(t - t_ex) * 2.5) * math.sin(t * 60) if t > t_ex else 0
    zx = lerp(-150, 330, seg(t, 0, 2.2)) + temb
    s.append(zumbi(zx, 640 + 14 * math.sin(t * 1.8) + temb * 0.5, 0.6, t, ang=5 * math.sin(t * 1.3),
                   susto=min(1.0, seg(t, t_ex, t_ex + 0.3) * (1 - seg(t, m[2] + 3.0, m[2] + 3.6)) + 0.9 * ry * seg(t, m[4], m[4] + 0.2))))
    fl, _ = destello_pantalla(t, [t_ex], "#fff3c0", 0.7)
    s.append(fl)
    return "".join(s)


# ================= despedida =================
def esc_final(t, dur, m):
    sube = seg(t, 0, 3.5)
    s = ["<defs><linearGradient id='atar' x1='0' y1='0' x2='0' y2='1'>"
         f"<stop offset='0' stop-color='{mix('#3a4a7a', '#ff8a6b', sube)}'/><stop offset='1' stop-color='{mix('#6a7aa0', '#ffe0a8', sube)}'/></linearGradient>"
         "<linearGradient id='mar6' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a7fc0'/><stop offset='1' stop-color='#0b3d70'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#atar)'/>",
         f"<circle cx='960' cy='{lerp(800, 520, sube):.0f}' r='120' fill='#ffd166' stroke='{INK}' stroke-width='{LW}' opacity='{sube:.2f}'/>"]
    # arcoíris después de la tormenta
    arc = seg(t, 1.0, 3.5)
    for i, c in enumerate(["#ff3b3b", "#ff9a2e", "#ffe14d", "#4fd36b", "#3a8dff", "#8a5cff"]):
        r = 620 - i * 30
        s.append(f"<path d='M{560 - r} 605 A{r} {r} 0 0 1 {560 + r} 605' fill='none' stroke='{c}' stroke-width='30' opacity='{0.75 * arc:.2f}'/>")
    for i, (cx, cy, sc) in enumerate([(200, 200, 1.0), (1500, 150, 0.9), (1100, 260, 0.7)]):
        dx = (t * 16 * (1 + i * 0.3)) % 2300
        s.append(nube((cx + dx) % 2300 - 300, cy, sc, "#fff4ea"))
    ola = "".join(f"Q{60 + i * 120:.0f} {600 + 12 * math.sin(t * 2 + i):.0f} {120 + i * 120:.0f} 605 " for i in range(17))
    s.append(f"<path d='M0 605 {ola} L1920 1080 L0 1080 Z' fill='url(#mar6)' fill-opacity='0.95' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(8):
        sx = (i * 260 + t * 40) % 2000 - 40
        s.append(f"<path d='M{sx:.0f} {680 + i * 45 % 280:.0f} q30 -12 60 0' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
    zx = lerp(560, 430, seg(t, m[1] - 0.5, m[1] + 1.0))
    zy = lerp(1150, 430, sube) + 14 * math.sin(t * 2)
    s.append(zumbi(zx, zy, 0.9, t, ang=6 * math.sin(t * 1.6), guino=(m[4] + 0.3 < t < m[4] + 0.7)))
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
        s.append(f"<g transform='translate(1180,400) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='400' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, 400, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, 400, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(950, 415, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 420, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, 400, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Una bola de hielo del tamaño de un balón?", "escena": esc_intro, "susc": 2,
     "frases": ["¿Te imaginas una bola de hielo tan grande como un balón cayendo del cielo?",
                "Hoy la verás con Zumbi, nuestro dron cazatormentas… y al final, un volcán que te dejará con la boca abierta.",
                "Suscríbete a Mundo Curioso cinco mil y… ¡despegamos!"]},
    {"titulo": "1. El granizo gigante", "escena": esc_granizo, "tarjeta": "CAPÍTULO 1 · GRANIZO GIGANTE",
     "frases": ["Primera parada: una tormenta enorme sobre Dakota del Sur, en Estados Unidos.",
                "Dentro de la nube, el viento sopla hacia arriba con tanta fuerza que sube las gotas de agua hasta donde se congelan.",
                "La bolita cae, vuelve a subir, y en cada viaje se cubre con otra capa de hielo, como una cebolla.",
                "Aquí, en julio de dos mil diez, cayó la piedra de granizo más grande de Estados Unidos: ¡veinte centímetros de ancho!",
                "Era como un balón de voleibol… ¡y pesaba casi un kilo!"],
     "grandes": {3: "20 cm", 4: "¡CASI 1 KG!"}},
    {"titulo": "2. El viento más fuerte jamás medido", "escena": esc_viento, "tarjeta": "CAPÍTULO 2 · EL VIENTO RÉCORD",
     "frases": ["Seguimos hasta una isla de Australia llamada Barrow.",
                "Zumbi lleva en la cabeza un anemómetro: unas cucharitas que giran con el viento y miden su velocidad.",
                "En mil novecientos noventa y seis, por aquí pasó el ciclón Olivia.",
                "Y un aparato como este midió la racha de viento más fuerte jamás registrada fuera de un tornado: ¡cuatrocientos ocho kilómetros por hora!",
                "¡Agárrate fuerte, Zumbi!",
                "Pero después de tanto viento, nos espera un lugar donde el suelo quema como una sartén…"],
     "grandes": {3: "408 km/h"}},
    {"titulo": "3. El suelo más caliente del planeta", "escena": esc_lut, "tarjeta": "CAPÍTULO 3 · EL SUELO QUE QUEMA",
     "frases": ["Tercera parada: el desierto de Lut, en Irán.",
                "Casi no hay plantas ni agua: solo dunas, rocas oscuras y un sol abrasador.",
                "Un satélite de la NASA midió desde el espacio la temperatura del suelo… y marcó setenta coma siete grados.",
                "¡Es el lugar más caliente que han encontrado los satélites en toda la Tierra!",
                "A esa temperatura, un huevo empezaría a cocinarse directamente sobre las piedras."],
     "grandes": {2: "70,7 °C"}, "extra": 1.0},
    {"titulo": "4. Los pelos de cristal de un volcán", "escena": esc_pele, "tarjeta": "CAPÍTULO 4 · PELOS DE CRISTAL",
     "frases": ["Cruzamos el océano Pacífico hasta Hawái, la tierra de los volcanes.",
                "Delante de nosotros, una fuente de lava lanza chorros de roca fundida hacia el cielo.",
                "El viento estira las gotas de lava, que se enfrían al momento y se convierten en hilos de cristal dorado.",
                "Los llaman pelos de Pele, por la diosa hawaiana de los volcanes.",
                "Son más finos que un milímetro… ¡y algunos miden más de un metro de largo!",
                "Pero el volcán de nuestra última parada es muchísimo más bestia…"],
     "grandes": {4: "+ DE 1 METRO"}},
    {"titulo": "5. La nube volcánica más alta", "escena": esc_tonga, "tarjeta": "CAPÍTULO 5 · EL VOLCÁN QUE TOCÓ EL CIELO",
     "frases": ["Última parada: Tonga, en el sur del océano Pacífico. Bajo estas olas se esconde un volcán.",
                "El quince de enero de dos mil veintidós, el volcán Hunga Tonga explotó.",
                "Su nube de ceniza y vapor subió cincuenta y ocho kilómetros: ¡más de cinco veces la altura a la que vuelan los aviones!",
                "Llegó hasta la mesosfera. Seguramente es la nube volcánica más alta que han visto nunca los satélites.",
                "Y dentro de ella estalló la tormenta de rayos más intensa jamás registrada: ¡más de dos mil seiscientos rayos por minuto!"],
     "grandes": {2: "58 km", 4: "2.600 POR MINUTO"}, "extra": 1.5},
    {"titulo": "Suscríbete para más aventuras", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje por el tiempo más salvaje de la Tierra.",
                "Si has aprendido algo nuevo, ayúdanos con un gesto muy pequeño: suscríbete al canal y activa la campanita.",
                "Así no te perderás ninguna aventura: cada día, una historia nueva llena de curiosidades.",
                "Y cuéntanos en los comentarios cuál de estas paradas te ha sorprendido más.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
