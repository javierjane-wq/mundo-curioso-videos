"""Episodio: "Viaje por el mundo antiguo" con Arenillo, un reloj de arena volador original.

Datos (verificados el 27-11-2026):
- La hoja de hierro del puñal de Tutankamón (reinó c. 1332-1323 a. C.; el puñal, con mango de oro, se halló
  en 1925) es de hierro de meteorito: tiene un 11 % de níquel y un 0,6 % de cobalto (fluorescencia de rayos X,
  Comelli et al., Meteoritics & Planetary Science 2016). En Egipto no hay pruebas de fundición de hierro hasta
  el siglo VI a. C. (Eos/AGU «Pharaoh's iron dagger made from a meteorite, study confirms»; Wikipedia
  «Tutankhamun's meteoric iron dagger»).
- La tablilla de queja a Ea-nasir (Ur, Mesopotamia, c. 1750 a. C., arcilla con escritura cuneiforme acadia):
  Nanni se queja de que le entregaron cobre de mala calidad y de que lo trataron con desprecio; Guinness la
  reconoce como la reclamación de cliente escrita más antigua (National Geographic «Think customer service is
  bad now?»; Wikipedia «Complaint tablet to Ea-nāṣir»; Guinness World Records «Oldest written customer complaint»).
- En Pompeya (erupción del 79 d. C.) había puestos de comida callejera, los termopolios (unos 150, según
  Archaeology); en el de la Regio V, excavado entero en 2020, aparecieron restos de pato, cerdo, cabra, pescado
  y caracoles, y el mostrador estaba pintado con dos patos, un gallo y un perro (The Art Newspaper, 27-12-2020;
  Archaeology Magazine, 29-03-2019).
- El hormigón romano se cura solo: sus grumos de cal (mezclada en caliente con cal viva) reaccionan con el agua
  que entra por una grieta y la rellenan de carbonato cálcico; en la prueba del MIT las grietas se cerraron solas
  en dos semanas. La cúpula del Panteón (dedicado en el 128 d. C.) es la mayor de hormigón sin armar del mundo y
  sigue intacta (MIT News, 06-01-2023; Seymour, Masic et al., Science Advances 2023).
- El mecanismo de Anticitera lo encontraron en 1901 unos buceadores de esponjas en un barco hundido de época
  romana; tiene unos 2.000 años, quedan 82 fragmentos y 30 engranajes de bronce, y mostraba las posiciones del
  Sol, la Luna y los planetas, los eclipses y las fechas de los Juegos Olímpicos: «el primer ordenador
  analógico del mundo» (UCL News, 12-03-2021; Freeth et al., Scientific Reports 2021).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-27-historia"
TITULO = "Viaje por el mundo antiguo"
VOZ = "em_santa"
VELOCIDAD = 0.95
MUSICA = 92

W, H = 1920, 1080
rng = np.random.default_rng(27)
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(0, 6.3)) for _ in range(80)]
ARENA = [(rng.uniform(0, 1), rng.uniform(0, 6.3), rng.uniform(4, 10), rng.uniform(0.5, 1.5)) for _ in range(60)]
PIEDRAS = [(rng.uniform(640, 1280), rng.uniform(400, 740), rng.uniform(14, 34), rng.uniform(0, 6.3), int(rng.integers(5, 8))) for _ in range(46)]
CAL = [(745, 470, 30), (880, 640, 26), (1020, 445, 24), (1150, 690, 30), (1210, 520, 22), (700, 690, 20), (960, 560, 34)]
NIEVE = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(8, 25)) for _ in range(60)]


# ================= piezas comunes =================
def cielo(id_, top, bot):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def nube(x, y, sc, col="#fff", op=1.0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


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


def brillo(x, y, r, op=1.0, col="#fff6a8"):
    """Estrellita de cuatro puntas."""
    return (f"<path d='M{x:.0f} {y - r:.0f} Q{x + r * 0.15:.0f} {y - r * 0.15:.0f} {x + r:.0f} {y:.0f} Q{x + r * 0.15:.0f} {y + r * 0.15:.0f} {x:.0f} {y + r:.0f} "
            f"Q{x - r * 0.15:.0f} {y + r * 0.15:.0f} {x - r:.0f} {y:.0f} Q{x - r * 0.15:.0f} {y - r * 0.15:.0f} {x:.0f} {y - r:.0f} Z' fill='{col}' opacity='{op:.2f}'/>")


def remolino_arena(cx, cy, t, k, r=260):
    """Torbellino de arena dorada (viaje en el tiempo)."""
    if k <= 0:
        return ""
    s = []
    for a0, fase, tam, v in ARENA:
        a = fase + t * 4 * v
        rr = r * (0.3 + 0.7 * a0) * (0.6 + 0.4 * k)
        x, y = cx + rr * math.cos(a), cy + rr * 0.55 * math.sin(a)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{tam * (0.5 + k):.1f}' fill='#ffd36b' stroke='#c98a2a' stroke-width='2' opacity='{k * (0.6 + 0.4 * math.sin(a)):.2f}'/>")
    return "".join(s)


def arenillo(x, y, s, t, arena=0.55, guino=False, ang=0.0, susto=0.0, alas=1.0, mira=0.0, brilla=0.0):
    """Arenillo: reloj de arena volador con marco de madera, alitas blancas y ojos en la ampolla de arriba."""
    parp = 0.12 if (t % 3.6) < 0.13 or guino else 1.0
    a = math.sin(t * 13) * alas
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if brilla > 0:
        g.append(f"<circle r='260' fill='#ffe9a0' opacity='{0.35 * brilla:.2f}'/>")
    g.append("<ellipse cx='0' cy='215' rx='120' ry='14' fill='#000' opacity='0.10'/>")
    for sx in (-1, 1):
        rot = sx * (-12 - 26 * a)
        g.append(f"<g transform='translate({sx * 96},-60) rotate({rot:.1f}) scale({sx},1)'>"
                 f"<path d='M0 0 Q50 -95 160 -88 Q128 -60 150 -38 Q108 -30 120 -8 Q70 0 0 26 Z' fill='#ffffff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 "<path d='M28 -6 Q78 -48 132 -58 M30 10 Q72 -14 108 -20' fill='none' stroke='#cfd8e3' stroke-width='5' stroke-linecap='round'/></g>")
    vidrio = "M-82 -138 C-82 -64 -14 -34 -14 0 C-14 34 -82 64 -82 138 L82 138 C82 64 14 34 14 0 C14 -34 82 -64 82 -138 Z"
    g.append(f"<defs><clipPath id='vidrio'><path d='{vidrio}'/></clipPath></defs>")
    g.append(f"<path d='{vidrio}' fill='#e6f7ff' fill-opacity='0.9'/>")
    yt = lerp(-6, -96, clamp(arena))
    yb = lerp(128, 46, clamp(1 - arena))
    g.append("<g clip-path='url(#vidrio)'>"
             f"<path d='M-90 0 L-90 {yt + 8:.0f} Q0 {yt + 22:.0f} 90 {yt + 8:.0f} L90 0 Z' fill='#f4c25a'/>"
             f"<path d='M-90 140 L-90 {yb + 34:.0f} Q0 {yb - 26:.0f} 90 {yb + 34:.0f} L90 140 Z' fill='#f4c25a'/>"
             f"<path d='M-90 140 L-90 {yb + 50:.0f} Q0 {yb - 6:.0f} 90 {yb + 50:.0f} L90 140 Z' fill='#e0a540'/></g>")
    if 0.02 < arena < 0.98:
        g.append(f"<line x1='0' y1='-4' x2='0' y2='{yb:.0f}' stroke='#e9ad45' stroke-width='6'/>")
        for i in range(3):
            k = (t * 2.2 + i / 3) % 1
            g.append(f"<circle cx='{2 * math.sin(i + t * 9):.1f}' cy='{lerp(0, yb, k):.0f}' r='4' fill='#c98a2a'/>")
    g.append(f"<path d='M-60 -120 Q-56 -80 -30 -58' fill='none' stroke='#ffffff' stroke-width='9' stroke-linecap='round' opacity='0.85'/>")
    g.append(f"<path d='{vidrio}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cara (en la ampolla de arriba)
    for ex in (-32, 32):
        g.append(f"<ellipse cx='{ex}' cy='-104' rx='21' ry='{24 * parp:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        if parp > 0.5:
            g.append(f"<circle cx='{ex + 5 + 6 * mira:.1f}' cy='-100' r='11' fill='{INK}'/><circle cx='{ex + 1 + 6 * mira:.1f}' cy='-105' r='4' fill='#fff'/>")
    g.append("<ellipse cx='-56' cy='-78' rx='11' ry='7' fill='#ff8fa8' opacity='0.8'/><ellipse cx='56' cy='-78' rx='11' ry='7' fill='#ff8fa8' opacity='0.8'/>")
    if susto > 0.5:
        g.append(f"<ellipse cx='0' cy='-70' rx='11' ry='14' fill='#6a2a2a' stroke='{INK}' stroke-width='5'/>")
    else:
        g.append(f"<path d='M-17 -76 Q0 -58 17 -76' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # marco de madera
    for px in (-104, 86):
        g.append(f"<rect x='{px}' y='-142' width='18' height='284' rx='6' fill='#c98a4b' stroke='{INK}' stroke-width='6'/>")
    for cy in (-176, 138):
        g.append(f"<rect x='-118' y='{cy}' width='236' height='38' rx='14' fill='#b5713a' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M-100 {cy + 19} L100 {cy + 19}' stroke='#8a5226' stroke-width='6' stroke-linecap='round'/>")
        for bx in (-88, 0, 88):
            g.append(f"<circle cx='{bx}' cy='{cy + 19}' r='6' fill='#ffd23f' stroke='{INK}' stroke-width='3'/>")
    g.append(f"<circle cx='0' cy='-190' r='13' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def engranaje(cx, cy, r, n, ang, col="#d9a441", oscuro="#a8742a", lw=6, op=1.0):
    """Rueda dentada de bronce."""
    pts = []
    paso = 2 * math.pi / n
    ri, ro = r, r + max(10, r * 0.16)
    for i in range(n):
        a0 = i * paso + math.radians(ang)
        for k, rr in ((0.0, ri), (0.2, ro), (0.5, ro), (0.7, ri)):
            a = a0 + k * paso
            pts.append(f"{cx + rr * math.cos(a):.1f} {cy + rr * math.sin(a):.1f}")
    d = "M" + " L".join(pts) + " Z"
    s = [f"<g opacity='{op:.2f}'><path d='{d}' fill='{col}' stroke='{INK}' stroke-width='{lw}' stroke-linejoin='round'/>",
         f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r * 0.78:.1f}' fill='{oscuro}' stroke='{INK}' stroke-width='{lw * 0.7:.1f}'/>"]
    for k in range(4):
        a = math.radians(ang) + k * math.pi / 2
        s.append(f"<line x1='{cx:.1f}' y1='{cy:.1f}' x2='{cx + r * 0.78 * math.cos(a):.1f}' y2='{cy + r * 0.78 * math.sin(a):.1f}' stroke='{col}' stroke-width='{max(6, r * 0.16):.1f}'/>")
    s.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{max(6, r * 0.2):.1f}' fill='{col}' stroke='{INK}' stroke-width='{lw * 0.7:.1f}'/></g>")
    return "".join(s)


def palmera(x, y, s, t, fase=0.0):
    sw = 4 * math.sin(t * 1.2 + fase)
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>",
         f"<path d='M-14 0 Q-4 -120 {10 + sw:.0f} -250 L{30 + sw:.0f} -250 Q16 -120 14 0 Z' fill='#a8743c' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"]
    for i in range(5):
        g.append(f"<path d='M{6 + sw * 2:.0f} {-80 - i * 36} l22 -8' stroke='#7a5028' stroke-width='5' stroke-linecap='round'/>")
    for i, a in enumerate((-160, -120, -60, -20, -95)):
        aa = math.radians(a + 6 * math.sin(t * 1.5 + i + fase))
        ex, ey = 20 + sw + 150 * math.cos(aa), -255 + 110 * math.sin(aa) + 40
        g.append(f"<path d='M{20 + sw:.0f} -255 Q{20 + sw + 90 * math.cos(aa):.0f} {-255 + 90 * math.sin(aa) - 30:.0f} {ex:.0f} {ey:.0f} "
                 f"Q{20 + sw + 60 * math.cos(aa):.0f} {-255 + 60 * math.sin(aa) + 10:.0f} {20 + sw:.0f} -250 Z' fill='#4caf50' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<circle cx='{14 + sw:.0f}' cy='-245' r='12' fill='#8a5226' stroke='{INK}' stroke-width='4'/><circle cx='{32 + sw:.0f}' cy='-240' r='12' fill='#8a5226' stroke='{INK}' stroke-width='4'/></g>")
    return "".join(g)


def persona(x, y, s, t, piel="#e0a878", ropa="#f2e6cf", pelo="#2a1a14", barba=False, enfado=0.0, brazo=0.0,
            brazo2=0.0, gorro=None, flecos=False, cinturon=None, boca=0.0, dirx=1, alegre=0.0):
    """Persona sencilla de frente (y = pies). brazo/brazo2: ángulo de los brazos (0 = abajo, 1 = arriba)."""
    parp = 0.12 if (t % 4.0 + x * 0.001) % 4.0 < 0.13 else 1.0
    cara = mix(piel, "#e2553a", 0.5 * enfado)
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s * dirx:.3f},{s:.3f})'>"]
    g.append("<ellipse cx='0' cy='4' rx='90' ry='14' fill='#000' opacity='0.15'/>")
    # brazos (detrás del cuerpo)
    for lado, b in ((-1, brazo), (1, brazo2)):
        a = math.radians(lado * (12 + 150 * b))
        hx, hy = lado * 62 + 150 * math.sin(a) * 1.0, -240 + 150 * math.cos(a)
        g.append(f"<path d='M{lado * 50} -240 L{hx:.0f} {hy:.0f}' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
                 f"<path d='M{lado * 50} -240 L{hx:.0f} {hy:.0f}' stroke='{ropa}' stroke-width='22' stroke-linecap='round'/>"
                 f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='17' fill='{piel}' stroke='{INK}' stroke-width='6'/>")
    # cuerpo (túnica)
    g.append(f"<path d='M-62 -250 Q0 -272 62 -250 L84 -10 Q0 6 -84 -10 Z' fill='{ropa}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if flecos:
        for i in range(9):
            fx = -76 + i * 19
            g.append(f"<path d='M{fx} -16 l3 22' stroke='{mix(ropa, INK, 0.4)}' stroke-width='6' stroke-linecap='round'/>")
        g.append(f"<path d='M-70 -150 Q0 -130 72 -170' fill='none' stroke='{mix(ropa, INK, 0.3)}' stroke-width='8'/>")
    if cinturon:
        g.append(f"<path d='M-70 -140 Q0 -126 70 -140' fill='none' stroke='{cinturon}' stroke-width='14'/>")
    g.append(f"<path d='M-30 -10 L-30 4 M30 -10 L30 4' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
    # cabeza
    g.append(f"<rect x='-16' y='-276' width='32' height='30' fill='{piel}' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<circle cx='0' cy='-318' r='52' fill='{cara}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-52 -322 Q-50 -378 0 -376 Q50 -378 52 -322 Q40 -350 0 -350 Q-40 -350 -52 -322 Z' fill='{pelo}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    if gorro:
        g.append(f"<path d='M-54 -340 Q0 -400 54 -340 Z' fill='{gorro}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    if barba:
        g.append(f"<path d='M-48 -312 Q-50 -250 0 -238 Q50 -250 48 -312 Q30 -290 0 -292 Q-30 -290 -48 -312 Z' fill='{pelo}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        for i in range(4):
            g.append(f"<path d='M{-30 + i * 20} -282 q4 12 0 24' fill='none' stroke='{mix(pelo, '#ffffff', 0.25)}' stroke-width='4'/>")
    for ex in (-19, 19):
        g.append(f"<g transform='translate({ex},-322) scale(1,{parp})'><circle r='8' fill='{INK}'/><circle cx='-2' cy='-3' r='3' fill='#fff'/></g>")
    ce = 10 * enfado
    g.append(f"<path d='M-34 {-342 - ce:.0f} L-8 {-338 + ce:.0f} M34 {-342 - ce:.0f} L8 {-338 + ce:.0f}' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    my = -296 if barba else -292
    if boca > 0.3:
        g.append(f"<ellipse cx='0' cy='{my}' rx='13' ry='{8 + 8 * boca:.0f}' fill='#6a2a2a' stroke='{INK}' stroke-width='5'/>")
    elif enfado > 0.4:
        g.append(f"<path d='M-14 {my + 4} Q0 {my - 8} 14 {my + 4}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    else:
        g.append(f"<path d='M-14 {my - 4} Q0 {my + 8 + 6 * alegre:.0f} 14 {my - 4}' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def vapor(x, y, t, n=4, alto=160, op=0.7, col="#ffffff", fase=0.0):
    s = []
    for i in range(n):
        k = (t * 0.6 + i / n + fase) % 1
        cx = x + 18 * math.sin(k * 7 + i + fase * 5)
        s.append(f"<circle cx='{cx:.0f}' cy='{y - k * alto:.0f}' r='{10 + 22 * k:.0f}' fill='{col}' opacity='{op * (1 - k):.2f}'/>")
    return "".join(s)


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


# ================= iconos del viaje (intro) =================
def icono_piramide(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-80 50 L0 -60 L80 50 Z' fill='#f0c060' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M0 -60 L22 50 L80 50 Z' fill='#d49a3a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def icono_tablilla(x, y, s, ang=0):
    cuñas = "".join(f"<path d='M{-30 + c * 22} {-40 + f * 22} l12 4 l-12 4 Z' fill='#7a4a26'/>" for f in range(4) for c in range(3))
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang}) scale({s:.2f})'>"
            f"<rect x='-48' y='-62' width='96' height='124' rx='16' fill='#c98d55' stroke='{INK}' stroke-width='7'/>{cuñas}</g>")


def icono_olla(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-50 -30 Q-70 40 0 50 Q70 40 50 -30 Z' fill='#c0643a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<rect x='-56' y='-44' width='112' height='18' rx='8' fill='#d9804a' stroke='{INK}' stroke-width='6'/></g>")


def icono_columna(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<rect x='-50' y='-62' width='100' height='18' rx='4' fill='#f4efe4' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-32' y='-44' width='64' height='88' fill='#f4efe4' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-14 -40 L-14 40 M0 -40 L0 40 M14 -40 L14 40' stroke='#cfc6b4' stroke-width='5'/>"
            f"<rect x='-50' y='44' width='100' height='18' rx='4' fill='#f4efe4' stroke='{INK}' stroke-width='6'/></g>")


def esc_intro(t, dur, m):
    s = [cielo("noche0", "#2a1650", "#6a2a7a")]
    for x, y, r, f in ESTRELLAS:
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * 0.7:.1f}' fill='#fff6d8' opacity='{0.5 + 0.5 * math.sin(t * 2 + f):.2f}'/>")
    # túnel del tiempo: brazos en espiral que giran
    cx, cy = 960, 590
    for brazo, col in enumerate(["#ffb347", "#ff6fae", "#7ad7ff", "#ffe066"]):
        pts = []
        for i in range(60):
            th = i * 0.16
            rr = 20 + i * 13
            a = th + brazo * math.pi / 2 - t * 1.6
            pts.append(f"{cx + rr * math.cos(a):.0f} {cy + rr * 0.62 * math.sin(a):.0f}")
        s.append(f"<path d='M{' L'.join(pts)}' fill='none' stroke='{col}' stroke-width='34' stroke-linecap='round' opacity='0.35'/>")
        s.append(f"<path d='M{' L'.join(pts)}' fill='none' stroke='{col}' stroke-width='10' stroke-linecap='round' opacity='0.8'/>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{70 + 10 * math.sin(t * 4):.0f}' fill='#fff3c4' opacity='0.85'/>")
    # engranajes de bronce que giran (pista del final)
    s.append(engranaje(250, 760, 120, 18, t * 30, op=0.9))
    s.append(engranaje(420, 900, 70, 11, -t * 30 * 120 / 70 + 8, op=0.9))
    s.append(engranaje(1690, 760, 110, 16, -t * 34, op=0.9))
    s.append(engranaje(1560, 920, 60, 10, t * 34 * 110 / 60, op=0.9))
    # iconos de las cinco paradas que giran alrededor (desde la frase 1)
    ic = seg(t, m[1] + 0.8, m[1] + 2.0) * (1 - seg(t, m[2] + 1.2, m[2] + 2.2))
    if ic > 0:
        iconos = [icono_piramide, icono_tablilla, icono_olla, icono_columna, None]
        for i, f in enumerate(iconos):
            a = t * 0.9 + i * 2 * math.pi / 5
            ix, iy = cx + 560 * math.cos(a), cy + 250 * math.sin(a)
            sc = 0.9 * ease(ic) * (0.8 + 0.2 * math.sin(a))
            if f is None:
                s.append(engranaje(ix, iy, 46 * sc, 10, t * 90, op=ic))
            else:
                s.append(f"<g opacity='{ic:.2f}'>{f(ix, iy, sc)}</g>")
    # Arenillo: sale del túnel desde el fotograma 0, saluda y al final se lanza dentro
    sale = seg(t, 0, 1.6)
    entra = seg(t, m[2] + 1.6, dur)
    x = lerp(960, 960, sale) + 60 * math.sin(t * 1.3) * (1 - entra)
    y = lerp(590, 560, sale) + 16 * math.sin(t * 2.4) * (1 - entra)
    sc = lerp(0.15, 1.0, ease(sale)) * lerp(1, 0.1, entra)
    s.append(remolino_arena(x, y, t, 0.6 + 0.4 * math.sin(t * 2), 330 * sc))
    s.append(arenillo(x, y, sc, t, arena=0.95, ang=8 * math.sin(t * 1.7) + 200 * entra,
                      guino=(m[1] + 0.3 < t < m[1] + 0.7), susto=1.0 if t < m[0] + 1.5 else 0.0))
    s.append(destellos(x, y, seg(t, 0.4, 1.8), 12, 300))
    return "".join(s)


# ================= 1 · Egipto =================
def antorcha(x, y, t, fase=0.0):
    f = 1 + 0.12 * math.sin(t * 17 + fase) + 0.08 * math.sin(t * 29 + fase)
    return (f"<circle cx='{x}' cy='{y - 40}' r='{150 * f:.0f}' fill='#ffcf6a' opacity='0.18'/>"
            f"<path d='M{x - 12} {y + 70} L{x - 18} {y} L{x + 18} {y} L{x + 12} {y + 70} Z' fill='#7a4a26' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M{x - 26} {y} Q{x - 30} {y - 50 * f:.0f} {x} {y - 95 * f:.0f} Q{x + 30} {y - 50 * f:.0f} {x + 26} {y} Z' fill='#ff8a2a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M{x - 12} {y} Q{x - 12} {y - 30 * f:.0f} {x} {y - 55 * f:.0f} Q{x + 12} {y - 30 * f:.0f} {x + 12} {y} Z' fill='#ffe066'/>")


def sarcofago(x, y, s, t):
    """Ataúd egipcio dorado de pie (genérico), con tocado a rayas."""
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-110 -250 Q-120 -330 0 -340 Q120 -330 110 -250 L130 -150 Q120 120 80 230 L-80 230 Q-120 120 -130 -150 Z' fill='#e8b830' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            + "".join(f"<path d='M{-118 + i * 4} {-230 + i * 34} L{-60} {-230 + i * 34}' stroke='#2a5aa8' stroke-width='14'/>" for i in range(4))
            + "".join(f"<path d='M{118 - i * 4} {-230 + i * 34} L{60} {-230 + i * 34}' stroke='#2a5aa8' stroke-width='14'/>" for i in range(4))
            + f"<ellipse cx='0' cy='-235' rx='58' ry='72' fill='#f2cf6a' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-34 -250 q10 -8 20 0 M14 -250 q10 -8 20 0' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
            f"<path d='M-34 -250 L-48 -244 M34 -250 L48 -244' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-12 -206 Q0 -198 12 -206' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
            f"<rect x='-12' y='-172' width='24' height='40' rx='6' fill='#2a5aa8' stroke='{INK}' stroke-width='5'/>"
            f"<path d='M-100 -110 Q0 -60 100 -110 L96 -70 Q0 -20 -96 -70 Z' fill='#2a5aa8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-96 -70 Q0 -20 96 -70 L92 -40 Q0 10 -92 -40 Z' fill='#c0392b' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-70 -10 L70 -10 M-60 40 L60 40 M-50 90 L50 90 M-40 140 L40 140' stroke='#b88a20' stroke-width='8'/>"
            f"<path d='M-60 -20 L60 60 M60 -20 L-60 60' stroke='#c99a24' stroke-width='12' stroke-linecap='round'/>"
            "</g>")


def cofre(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<rect x='-140' y='-100' width='280' height='120' rx='8' fill='#e8b830' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-150 -100 Q0 -170 150 -100 Z' fill='#f2cf6a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<rect x='-110' y='-80' width='220' height='80' rx='6' fill='#2a5aa8' stroke='{INK}' stroke-width='6'/>"
            + "".join(f"<circle cx='{-80 + i * 40}' cy='-40' r='12' fill='#e8b830' stroke='{INK}' stroke-width='4'/>" for i in range(5))
            + f"<path d='M-130 20 L-130 50 M130 20 L130 50' stroke='{INK}' stroke-width='16' stroke-linecap='round'/></g>")


def jarron(x, y, s, col="#e8b830"):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-26 -120 L26 -120 L22 -96 Q64 -70 50 -10 Q40 20 0 22 Q-40 20 -50 -10 Q-64 -70 -22 -96 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-46 -50 Q0 -36 46 -50' fill='none' stroke='#2a5aa8' stroke-width='10'/></g>")


def punal(x, y, s, t, estrellas=0.0, ang=0.0):
    """Puñal: mango de oro con bandas y pomo de cristal, hoja de hierro gris con nervio central."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if estrellas > 0:
        g.append(f"<ellipse cx='110' cy='0' rx='{240 + 20 * math.sin(t * 5):.0f}' ry='90' fill='#bfe6ff' opacity='{0.35 * estrellas:.2f}'/>")
    hoja = mix("#9aa4ad", "#c8e4ff", 0.6 * estrellas)
    g.append(f"<path d='M-20 -34 L300 -22 L380 0 L300 22 L-20 34 Z' fill='{hoja}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-10 0 L360 0' stroke='{mix('#6e7882', '#ffffff', 0.5 * estrellas)}' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<path d='M10 -20 L280 -12' stroke='#e8eef3' stroke-width='5' stroke-linecap='round' opacity='0.8'/>")
    if estrellas > 0:
        for i in range(7):
            bx = 20 + i * 48; by = (-12 if i % 2 else 12)
            g.append(brillo(bx, by, 10 + 4 * math.sin(t * 6 + i), estrellas, "#ffffff"))
    # guarda y mango
    g.append(f"<path d='M-34 -54 Q-20 0 -34 54 L-6 54 Q4 0 -6 -54 Z' fill='#f2cf6a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<rect x='-200' y='-24' width='168' height='48' rx='12' fill='#e8b830' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(5):
        g.append(f"<path d='M{-180 + i * 32} -22 L{-180 + i * 32} 22' stroke='{['#2a5aa8', '#c0392b'][i % 2]}' stroke-width='10'/>")
    g.append(f"<ellipse cx='-218' cy='0' rx='30' ry='40' fill='#e8b830' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='-218' cy='0' rx='17' ry='24' fill='#cfefff' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def esc_egipto(t, dur, m):
    s = [cielo("tumba", "#b57a3a", "#d9a65a"),
         f"<rect x='0' y='780' width='{W}' height='300' fill='#9a6a34' stroke='{INK}' stroke-width='{LW}'/>",
         "<rect x='0' y='860' width='1920' height='220' fill='#86592a'/>"]
    # friso pintado en la pared
    s.append(f"<rect x='0' y='300' width='{W}' height='46' fill='#2a5aa8' stroke='{INK}' stroke-width='6'/>")
    for i in range(24):
        s.append(f"<path d='M{i * 80 + 10} 346 L{i * 80 + 40} 304 L{i * 80 + 70} 346 Z' fill='{['#e8b830', '#c0392b', '#3aa07a'][i % 3]}' stroke='{INK}' stroke-width='4'/>")
    for i in range(12):
        s.append(f"<rect x='{i * 160 + 30}' y='430' width='100' height='300' rx='10' fill='#c99050' opacity='0.35'/>")
    # columnas con capitel de papiro
    for cx in (110, 1810):
        s.append(f"<rect x='{cx - 50}' y='240' width='100' height='560' fill='#e9c48a' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M{cx - 80} 240 Q{cx} 180 {cx + 80} 240 Z' fill='#3aa07a' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M{cx - 50} 600 L{cx + 50} 600 M{cx - 50} 630 L{cx + 50} 630' stroke='#c0392b' stroke-width='10'/>")
    luz = 1 + 0.05 * math.sin(t * 9)
    s.append(antorcha(300, 500, t))
    s.append(antorcha(1620, 500, t, 2.0))
    # tesoros
    s.append(sarcofago(440, 560, 0.95, t))
    s.append(cofre(1430, 790, 0.95))
    s.append(jarron(1240, 800, 0.9))
    s.append(jarron(1640, 820, 0.75, "#3aa07a"))
    for i in range(10):   # brillos del oro
        k = (t * 0.7 + i * 0.37) % 1
        bx = [420, 520, 470, 1400, 1480, 1300, 1240, 560, 1560, 380][i]; by = [400, 450, 620, 690, 720, 740, 730, 300, 700, 520][i]
        s.append(brillo(bx, by, 16 * math.sin(math.pi * k), 0.9))
    # pedestal y puñal
    s.append(f"<path d='M800 800 L1120 800 L1090 730 L830 730 Z' fill='#e9c48a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<rect x='850' y='690' width='220' height='40' rx='8' fill='#c0392b' stroke='{INK}' stroke-width='7'/>")
    aparece = seg(t, m[2] - 0.3, m[2] + 1.2)
    estr = seg(t, m[4] + 1.6, m[4] + 2.6)
    flota = 14 * math.sin(t * 2)
    pz = lerp(0.7, 1.0, aparece)
    px = 960 - 80 * pz
    py = lerp(660, 560, aparece) + flota * aparece
    s.append(f"<ellipse cx='960' cy='600' rx='{300 * aparece:.0f}' ry='{110 * aparece:.0f}' fill='#fff2b0' opacity='{0.35 * aparece:.2f}'/>")
    s.append(punal(px, py, pz, t, estrellas=estr))
    # Arenillo mira los tesoros
    ax, ay = 1460 + 30 * math.sin(t * 0.8), 470 + 16 * math.sin(t * 1.6)
    # bocadillo: un yunque tachado (frase 3)
    bo = seg(t, m[3], m[3] + 0.5) * (1 - seg(t, m[4] - 0.2, m[4] + 0.3))
    if bo > 0:
        bx, by = 1180, 420
        s.append(f"<g opacity='{bo:.2f}' transform='translate({bx},{by}) scale({0.6 + 0.4 * ease(bo):.2f})'>"
                 f"<circle cx='150' cy='90' r='12' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='120' cy='70' r='18' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse cx='0' cy='0' rx='120' ry='90' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<path d='M-60 -20 L60 -20 L40 0 L20 0 L30 40 L-30 40 L-20 0 L-60 0 Z' fill='#5a6470' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M-30 -60 L10 -30' stroke='#8a5226' stroke-width='12' stroke-linecap='round'/><rect x='-52' y='-78' width='34' height='22' rx='4' fill='#5a6470' stroke='{INK}' stroke-width='5' transform='rotate(35 -35 -67)'/>"
                 f"<path d='M-70 -60 L70 60 M70 -60 L-70 60' stroke='#e62117' stroke-width='16' stroke-linecap='round'/></g>")
    s.append(arenillo(ax, ay, 0.72, t, arena=0.8, mira=-1.0, susto=1.0 if m[4] + 0.8 < t < m[4] + 2.4 else 0.0))
    # meteorito que cruza la tumba y cae sobre el puñal (frase 4)
    k = seg(t, m[4] + 0.4, m[4] + 1.6)
    if 0 < k < 1:
        mx, my = lerp(1750, 1060, k), lerp(330, 560, k)
        s.append(f"<rect width='{W}' height='{H}' fill='#1a0c30' opacity='{0.6 * math.sin(math.pi * min(1, k * 1.4)):.2f}'/>")
        for i in range(10):
            q = i / 10
            s.append(f"<circle cx='{mx + 700 * q * 0.95:.0f}' cy='{my - 700 * q * 0.32:.0f}' r='{105 * (1 - q * 0.8):.0f}' fill='{mix('#fff3a0', '#ff5a2a', q)}' opacity='{0.9 * (1 - q):.2f}'/>")
        s.append(f"<circle cx='{mx:.0f}' cy='{my:.0f}' r='82' fill='#6e5a4a' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='{mx - 26:.0f}' cy='{my - 18:.0f}' r='20' fill='#54443a'/><circle cx='{mx + 28:.0f}' cy='{my + 22:.0f}' r='14' fill='#54443a'/>"
                 f"<circle cx='{mx + 22:.0f}' cy='{my - 30:.0f}' r='9' fill='#54443a'/>")
    fl = seg(t, m[4] + 1.5, m[4] + 1.7) * (1 - seg(t, m[4] + 1.7, m[4] + 2.6))
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.7 * fl:.2f}'/>")
    s.append(destellos(1060, 560, seg(t, m[4] + 1.6, m[4] + 3.2), 14, 380, "#ffffff"))
    return "".join(s)


# ================= 2 · Mesopotamia =================
def zigurat(x, y, s):
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"]
    for i, (w, h) in enumerate([(720, 150), (520, 120), (340, 100)]):
        y0 = -sum(hh for _, hh in [(720, 150), (520, 120), (340, 100)][:i + 1])
        g.append(f"<rect x='{-w / 2:.0f}' y='{y0}' width='{w}' height='{h}' fill='{['#c98d55', '#d49a60', '#dea86c'][i]}' stroke='{INK}' stroke-width='{LW}'/>")
        for j in range(int(w / 60)):
            g.append(f"<line x1='{-w / 2 + 30 + j * 60:.0f}' y1='{y0 + 14}' x2='{-w / 2 + 30 + j * 60:.0f}' y2='{y0 + h - 14}' stroke='#a8703e' stroke-width='6'/>")
    g.append(f"<rect x='-90' y='-450' width='180' height='80' fill='#e8b87c' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-30' y='-420' width='60' height='50' rx='26' fill='#5a3a22' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-60 0 L-36 -370 L36 -370 L60 0 Z' fill='#b87a44' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for j in range(12):
        yy = -20 - j * 30
        g.append(f"<line x1='{-58 + j * 2}' y1='{yy}' x2='{58 - j * 2}' y2='{yy}' stroke='#8a5a30' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def casa_barro(x, y, w, h, col="#d9a86c"):
    return (f"<rect x='{x}' y='{y - h}' width='{w}' height='{h}' fill='{col}' stroke='{INK}' stroke-width='7'/>"
            f"<rect x='{x - 8}' y='{y - h - 14}' width='{w + 16}' height='18' fill='{mix(col, '#000000', 0.15)}' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='{x + w / 2 - 22:.0f}' y='{y - 80}' width='44' height='80' rx='20' fill='#5a3a22' stroke='{INK}' stroke-width='6'/>")


def lingote(x, y, s, malo=0.0, ang=0.0):
    """Lingote de cobre (forma de piel de buey); malo -> mate, verdoso y agrietado."""
    col = mix("#e07a3a", "#7a8a66", malo)
    bri = mix("#ffb07a", "#8a9a76", malo)
    g = (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.1f}) scale({s:.2f})'>"
         f"<path d='M-80 -40 Q-60 -26 0 -30 Q60 -26 80 -40 Q66 0 80 40 Q60 26 0 30 Q-60 26 -80 40 Q-66 0 -80 -40 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
         f"<path d='M-50 -14 Q0 -20 50 -14' fill='none' stroke='{bri}' stroke-width='7' stroke-linecap='round'/>")
    if malo > 0.3:
        g += (f"<path d='M-20 -28 L-8 -6 L-24 10 L-10 28' fill='none' stroke='{INK}' stroke-width='5' opacity='{malo:.2f}'/>"
              f"<circle cx='34' cy='8' r='8' fill='#4a5a3a' opacity='{malo:.2f}'/><circle cx='-44' cy='12' r='6' fill='#4a5a3a' opacity='{malo:.2f}'/>")
    return g + "</g>"


def tablilla(x, y, s, t, marcas=1.0, ang=0.0, enfado=0.0):
    """Tablilla de barro con filas de cuñas (escritura cuneiforme, sin letras reales)."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if enfado > 0:
        for i in range(6):
            a = i / 6 * 2 * math.pi + t
            r1, r2 = 230, 270 + 20 * math.sin(t * 10 + i)
            g.append(f"<path d='M{r1 * math.cos(a):.0f} {r1 * math.sin(a):.0f} L{r2 * math.cos(a + 0.05):.0f} {r2 * math.sin(a + 0.05):.0f}' stroke='#e62117' stroke-width='12' stroke-linecap='round' opacity='{enfado:.2f}'/>")
    g.append(f"<rect x='-130' y='-190' width='260' height='380' rx='34' fill='#c98d55' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-112' y='-172' width='224' height='344' rx='26' fill='#d9a06a'/>")
    total = 9 * 7
    n = int(total * clamp(marcas))
    for i in range(n):
        f, c = divmod(i, 7)
        cx, cy = -92 + c * 30 + (6 if f % 2 else 0), -150 + f * 36
        if (i * 7) % 5 == 0:
            g.append(f"<path d='M{cx} {cy} l18 0 l-9 22 Z' fill='#7a4a26'/>")
        else:
            g.append(f"<path d='M{cx} {cy} l22 7 l-22 7 Z' fill='#7a4a26'/>")
    g.append("</g>")
    return "".join(g)


def esc_ur(t, dur, m):
    s = [cielo("tarde", "#ff9a6a", "#ffe3a8"),
         f"<circle cx='1500' cy='330' r='90' fill='#ffd166' stroke='{INK}' stroke-width='{LW}'/>"]
    for i, (cx, cy, sc) in enumerate([(200, 210, 0.9), (1100, 160, 0.8)]):
        s.append(nube((cx + t * 14) % 2300 - 300, cy, sc, "#fff1e0"))
    s.append(zigurat(960, 760, 0.95))
    s.append(casa_barro(60, 770, 200, 160))
    s.append(casa_barro(1640, 770, 230, 180, "#cf9c62"))
    s.append(palmera(320, 790, 1.1, t))
    s.append(palmera(1560, 790, 0.95, t, 1.3))
    s.append(f"<path d='M0 760 Q480 740 960 760 T1920 760 L1920 1080 L0 1080 Z' fill='#e8c48a' stroke='{INK}' stroke-width='{LW}'/>"
             "<path d='M0 900 Q500 880 960 900 T1920 900 L1920 1080 L0 1080 Z' fill='#d9ae72'/>")
    # Nanni, muy enfadado
    enf = seg(t, m[1] - 0.2, m[1] + 0.8)
    escribe = seg(t, m[3] - 0.3, m[3] + 0.3)
    temblor = 4 * math.sin(t * 40) * enf * (1 - escribe * 0.6)
    nx, ny = 560 + temblor, 900
    s.append(persona(nx, ny, 1.15, t, piel="#c68a5a", ropa="#e9dcc0", pelo="#2a1a14", barba=True, enfado=enf,
                     brazo=0.45 + 0.1 * math.sin(t * 6) * enf if escribe < 0.5 else 0.55, brazo2=0.25 + 0.5 * escribe,
                     flecos=True, boca=(0.8 if (m[1] + 0.5 < t < m[2] + 0.8 and (t * 3) % 1 < 0.5) else 0.0)))
    if enf > 0:   # humo de enfado
        s.append(vapor(nx - 50, ny - 520, t, 4, 140, 0.8 * enf, "#ffffff"))
        s.append(vapor(nx + 50, ny - 520, t, 4, 140, 0.8 * enf, "#ffffff", 0.5))
    # lingotes de cobre en una estera (frase 2): llegan relucientes y se vuelven malos
    li = seg(t, m[2] - 0.2, m[2] + 0.8)
    malo = seg(t, m[2] + 1.6, m[2] + 3.0)
    if li > 0:
        s.append(f"<g opacity='{li:.2f}'><path d='M760 880 L1120 880 L1150 820 L790 820 Z' fill='#b88a4a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 + lingote(870, 800 - 40 * (1 - li), 0.9, malo, -6) + lingote(1040, 800 - 40 * (1 - li), 0.9, malo, 5)
                 + lingote(955, 760 - 40 * (1 - li), 0.9, malo, 1) + "</g>")
    # la tablilla (frase 3) crece y sale disparada hacia nosotros (frase 4)
    tb = seg(t, m[3] - 0.2, m[3] + 0.6)
    marcas = seg(t, m[3] + 0.2, m[4])
    gran = seg(t, m[4] - 0.1, m[4] + 0.8)
    if tb > 0:
        tx, ty = lerp(1200, 1160, gran), lerp(560, 600, gran)
        sc = lerp(0.6, 1.25, gran) * (0.6 + 0.4 * ease(tb)) * (1 + 0.04 * math.sin(t * 8) * gran)
        s.append(tablilla(tx, ty, sc, t, marcas, lerp(8, -4, gran), enfado=gran))
        s.append(destellos(tx, ty, seg(t, m[4] + 0.2, m[4] + 1.8), 14, 360, "#ffffff"))
        if escribe > 0 and gran < 1:   # el punzón de caña escribe
            i = int(63 * clamp(marcas))
            f, c = divmod(min(i, 62), 7)
            px = tx + sc * (-92 + c * 30) ; py = ty + sc * (-150 + f * 36)
            s.append(f"<g opacity='{1 - gran:.2f}'><path d='M{px:.0f} {py:.0f} L{px + 120:.0f} {py - 150:.0f}' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
                     f"<path d='M{px:.0f} {py:.0f} L{px + 120:.0f} {py - 150:.0f}' stroke='#d9c07a' stroke-width='9' stroke-linecap='round'/></g>")
    ax = lerp(1600, 1650, gran) + 25 * math.sin(t * 0.9)
    ay = 470 + 18 * math.sin(t * 1.7)
    s.append(arenillo(ax, ay, 0.66, t, arena=0.7, mira=-1, susto=1.0 if m[1] + 0.3 < t < m[1] + 2.0 else 0.0,
                      guino=(m[5] + 0.6 < t < m[5] + 1.0)))
    return "".join(s)


# ================= 3 · Pompeya =================
def volcan(x, y, s, t):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-420 0 L-120 -300 Q-60 -330 0 -310 Q60 -330 120 -300 L420 0 Z' fill='#8a7a8c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-300 -120 Q-200 -150 -160 -200 Q-120 -150 -60 -170 L-120 -300 Z' fill='#a094a2' opacity='0.8'/>"
            f"<path d='M-260 -60 Q-100 -90 0 -60 Q120 -100 300 -60 L420 0 L-420 0 Z' fill='#6a9a4a' stroke='{INK}' stroke-width='7'/>"
            + vapor(0, -320, t * 0.5, 4, 120, 0.6, "#f4f0f4") + "</g>")


def pato(x, y, s, dirx=1, col="#3a9a5a"):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s * dirx:.2f},{s:.2f})'>"
            f"<path d='M-40 0 Q-50 -30 -10 -30 L20 -30 Q30 -56 46 -54 Q62 -52 60 -38 L76 -34 L60 -28 Q56 -10 40 -8 Q40 20 0 22 Q-40 22 -40 0 Z' fill='#f2e6cf' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<path d='M24 -36 Q40 -58 58 -40 Q50 -28 30 -26 Z' fill='{col}'/>"
            f"<circle cx='48' cy='-42' r='4' fill='{INK}'/><path d='M-30 -6 Q0 -16 20 -4' fill='none' stroke='#8a7a5a' stroke-width='5'/></g>")


def gallo(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-36 -10 Q-70 -70 -40 -80 Q-30 -50 -20 -40' fill='#2a6a3a' stroke='{INK}' stroke-width='5'/>"
            f"<ellipse cx='0' cy='-10' rx='38' ry='28' fill='#c0392b' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='30' cy='-46' r='18' fill='#e8a030' stroke='{INK}' stroke-width='5'/>"
            f"<path d='M22 -64 q6 -12 12 0 q6 -12 12 0' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<path d='M46 -46 L60 -42 L46 -38 Z' fill='#ffd23f' stroke='{INK}' stroke-width='3'/>"
            f"<circle cx='34' cy='-50' r='3' fill='{INK}'/><path d='M-6 18 L-10 36 M10 18 L12 36' stroke='{INK}' stroke-width='5'/></g>")


def caracol(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-40 20 Q-46 0 -20 2 L40 6 Q56 -10 50 -24 Q64 -20 60 0 Q60 20 40 22 Z' fill='#e8c4a0' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='-14' r='30' fill='#c97a3a' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M0 -14 m-18 0 a18 18 0 1 1 18 18 a10 10 0 1 1 -6 -14' fill='none' stroke='{INK}' stroke-width='5'/></g>")


def pescado(x, y, s, ang=0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({s:.2f})'>"
            f"<path d='M-50 0 L-80 -24 L-76 0 L-80 24 Z' fill='#7aa8c8' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='0' rx='56' ry='26' fill='#a8cce4' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='30' cy='-6' r='6' fill='{INK}'/></g>")


def muslo(x, y, s, ang=0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({s:.2f})'>"
            f"<rect x='10' y='-8' width='50' height='16' rx='8' fill='#f4efe4' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='62' cy='-8' r='9' fill='#f4efe4' stroke='{INK}' stroke-width='5'/><circle cx='62' cy='8' r='9' fill='#f4efe4' stroke='{INK}' stroke-width='5'/>"
            f"<ellipse cx='-14' cy='0' rx='40' ry='30' fill='#c0692a' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-34 -10 Q-14 -20 4 -12' fill='none' stroke='#e8945a' stroke-width='6' stroke-linecap='round'/></g>")


def esc_pompeya(t, dur, m):
    s = [cielo("pomp", "#7fd3ff", "#e3f7ff")]
    for i, (cx, cy, sc) in enumerate([(300, 180, 1.0), (1300, 140, 0.8)]):
        s.append(nube((cx + t * 16) % 2300 - 300, cy, sc))
    s.append(volcan(1560, 520, 0.9, t))
    # fachadas romanas
    s.append(f"<rect x='0' y='300' width='560' height='520' fill='#d9a06a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-20 300 L580 300 L560 260 L0 260 Z' fill='#c0532a' stroke='{INK}' stroke-width='7'/>"
             f"<rect x='120' y='420' width='120' height='170' rx='60' fill='#5a3a22' stroke='{INK}' stroke-width='7'/>"
             f"<rect x='330' y='440' width='110' height='90' fill='#5a3a22' stroke='{INK}' stroke-width='7'/>")
    # la tienda (termopolio)
    s.append(f"<rect x='600' y='290' width='980' height='530' fill='#b8402e' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M580 290 L1600 290 L1570 250 L610 250 Z' fill='#9a3020' stroke='{INK}' stroke-width='7'/>"
             f"<rect x='660' y='360' width='860' height='460' fill='#5a3426' stroke='{INK}' stroke-width='7'/>")
    for i in range(3):   # estantes con ánforas
        s.append(f"<rect x='690' y='{420 + i * 110}' width='800' height='14' fill='#8a5a30' stroke='{INK}' stroke-width='5'/>")
        for j in range(6):
            ax = 740 + j * 130 + (i % 2) * 40
            s.append(f"<path d='M{ax - 16} {420 + i * 110} Q{ax - 30} {380 + i * 110} {ax} {350 + i * 110} Q{ax + 30} {380 + i * 110} {ax + 16} {420 + i * 110} Z' fill='#c0643a' stroke='{INK}' stroke-width='5'/>")
    # el tendero
    s.append(persona(1240, 820, 1.0, t, piel="#d9a070", ropa="#f2e6cf", pelo="#5a3a22", brazo=0.35 + 0.15 * math.sin(t * 3),
                     brazo2=0.5, cinturon="#c0392b", alegre=1.0, boca=(0.7 if (t * 2.5) % 1 < 0.4 and m[1] < t < m[2] + 3 else 0)))
    # mostrador con ollas empotradas
    s.append(f"<rect x='620' y='600' width='900' height='34' rx='6' fill='#f4efe4' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='640' y='634' width='860' height='240' fill='#f2c25a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='660' y='652' width='820' height='204' fill='#e8a83a' stroke='#c0532a' stroke-width='8'/>")
    # pinturas del mostrador: dos patos y un gallo (frase 4: se iluminan)
    pin = seg(t, m[4] + 0.2, m[4] + 1.0)
    s.append(f"<g opacity='{0.75 + 0.25 * pin:.2f}'>{pato(760, 790, 1.2)}{pato(900, 790, 1.2, 1, '#2a7a8a')}{gallo(1230, 800, 1.3)}"
             f"<path d='M1040 700 Q1080 660 1120 700 Q1080 740 1040 700 Z' fill='#3aa07a' stroke='{INK}' stroke-width='4'/></g>")
    if pin > 0:
        s.append(f"<rect x='660' y='652' width='820' height='204' fill='#fff6c8' opacity='{0.3 * pin * (0.6 + 0.4 * math.sin(t * 5)):.2f}'/>")
        s.append(destellos(830, 760, seg(t, m[4] + 0.4, m[4] + 2.0), 10, 160))
        s.append(destellos(1230, 770, seg(t, m[4] + 0.8, m[4] + 2.4), 10, 160))
    ollas = [(760, 600), (960, 600), (1160, 600), (1360, 600)]
    hierve = seg(t, m[2] - 0.2, m[2] + 0.6)
    for i, (ox, oy) in enumerate(ollas):
        s.append(f"<ellipse cx='{ox}' cy='{oy + 2}' rx='62' ry='16' fill='#3a2216' stroke='{INK}' stroke-width='6'/>"
                 f"<ellipse cx='{ox}' cy='{oy}' rx='48' ry='10' fill='{['#c0692a', '#8a5a30', '#d9a040', '#a84a2a'][i]}'/>")
        s.append(vapor(ox, oy - 10, t, 4, 150 + 120 * hierve, 0.55 + 0.35 * hierve, "#ffffff", i * 0.3))
    # comida que salta de las ollas (frase 3)
    comida = [muslo, caracol, pescado, caracol, muslo]
    for i, f in enumerate(comida):
        k = seg(t, m[3] + 0.3 + i * 0.45, m[3] + 1.4 + i * 0.45)
        if 0 < k:
            ox = ollas[i % 4][0]
            tx = 740 + i * 175
            hx = lerp(ox, tx, k)
            hy = lerp(590, 470, k) - 170 * math.sin(math.pi * k) + 8 * math.sin(t * 4 + i) * k
            s.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{70 * k:.0f}' fill='#fff6c8' opacity='{0.55 * k:.2f}'/>")
            s.append(f(hx, hy, 1.4 * (0.5 + 0.5 * ease(k))))
    # clientes en la calle
    s.append(f"<rect x='0' y='820' width='{W}' height='260' fill='#9a948a' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(10):
        s.append(f"<path d='M{i * 200 - 40} 1080 L{i * 200 + 20} 860 L{i * 200 + 190} 860 L{i * 200 + 150} 1080' fill='#aaa49a' stroke='{INK}' stroke-width='6'/>")
    cola = seg(t, m[2] - 0.3, m[2] + 1.5)
    s.append(persona(lerp(-150, 470, cola), 960, 0.95, t, piel="#e0a878", ropa="#5a8ad0", pelo="#2a1a14", brazo2=0.6 * cola, alegre=1, cinturon="#2a3a6a"))
    s.append(persona(lerp(2100, 1720, cola), 970, 0.9, t, piel="#c68a5a", ropa="#e8c43a", pelo="#7a4a26", brazo=0.6 * cola, alegre=1, dirx=1))
    # Arenillo olfatea
    ax, ay = lerp(-200, 1760, seg(t, 0, 2.5)) - lerp(0, 0, 1), 400 + 18 * math.sin(t * 1.6)
    s.append(arenillo(ax, ay, 0.58, t, arena=0.6, mira=-1, ang=6 * math.sin(t * 1.4), guino=(m[2] + 1.0 < t < m[2] + 1.4)))
    s.append(destellos(1060, 560, seg(t, m[2] + 0.1, m[2] + 1.6), 14, 440))
    return "".join(s)


# ================= 4 · Hormigón romano =================
def obra(t, k):
    """Obra romana: muro de arcos a medio hacer con andamio y un obrero."""
    s = [f"<path d='M0 800 L1920 800 L1920 1080 L0 1080 Z' fill='#c9b48a' stroke='{INK}' stroke-width='{LW}'/>"]
    for i in range(5):
        x0 = 280 + i * 280
        s.append(f"<path d='M{x0} 800 L{x0} 520 Q{x0 + 140} 380 {x0 + 280} 520 L{x0 + 280} 800 L{x0 + 230} 800 L{x0 + 230} 540 Q{x0 + 140} 440 {x0 + 50} 540 L{x0 + 50} 800 Z' "
                 f"fill='#d8cfbf' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<rect x='280' y='420' width='1400' height='60' fill='#cfc6b4' stroke='{INK}' stroke-width='{LW}'/>")
    for x in (300, 700, 1100, 1500):
        s.append(f"<path d='M{x} 800 L{x} 360 M{x + 180} 800 L{x + 180} 360 M{x} 600 L{x + 180} 600 M{x} 400 L{x + 180} 400 M{x} 800 L{x + 180} 600' stroke='#8a5a30' stroke-width='12' stroke-linecap='round'/>")
    # obrero que vierte hormigón con un cubo
    v = math.sin(t * 2.2)
    s.append(persona(1720, 900, 0.95, t, piel="#d9a070", ropa="#c0392b", pelo="#2a1a14", brazo=0.55 + 0.1 * v, brazo2=0.55 + 0.1 * v, alegre=1))
    s.append(f"<path d='M1640 {640 - 10 * v:.0f} L1800 {640 - 10 * v:.0f} L1780 {700 - 10 * v:.0f} L1660 {700 - 10 * v:.0f} Z' fill='#8a8f96' stroke='{INK}' stroke-width='7'/>")
    return "".join(s)


def bloque(t, grieta, cura, op=1.0):
    """Trozo de hormigón romano en corte: piedras, grumos blancos de cal y una grieta que se cierra."""
    s = [f"<g opacity='{op:.2f}'><rect x='600' y='370' width='720' height='420' rx='26' fill='#b9b2a6' stroke='{INK}' stroke-width='{LW}'/>"]
    for x, y, r, a, n in PIEDRAS:
        pts = " L".join(f"{x + r * (0.8 + 0.2 * math.sin(i * 2.3 + a)) * math.cos(a + i * 2 * math.pi / n):.0f} {y + r * (0.8 + 0.2 * math.cos(i * 1.7 + a)) * math.sin(a + i * 2 * math.pi / n):.0f}" for i in range(n))
        s.append(f"<path d='M{pts} Z' fill='{mix('#8a8278', '#6e665c', (a % 1))}' stroke='{INK}' stroke-width='4'/>")
    for i, (x, y, r) in enumerate(CAL):
        cerca = abs(x - 960) < 140
        rr = r * (1 - 0.45 * cura if cerca else 1)
        s.append(f"<circle cx='{x}' cy='{y}' r='{rr:.0f}' fill='#ffffff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{x - rr * 0.3:.0f}' cy='{y - rr * 0.3:.0f}' r='{rr * 0.3:.0f}' fill='#eef4f8'/>")
    if grieta > 0:
        pts = [(960, 370), (930, 440), (985, 500), (945, 570), (1000, 640), (955, 720), (980, 790)]
        n = len(pts)
        corte = grieta * (n - 1)
        vis = [pts[0]]
        for i in range(1, n):
            if i <= corte:
                vis.append(pts[i])
            else:
                f = corte - (i - 1)
                if f > 0:
                    vis.append((lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)))
                break
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in vis)
        ancho = 26 * (1 - cura)
        if ancho > 1:
            s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='{ancho + 8:.0f}' stroke-linejoin='round' stroke-linecap='round'/>"
                     f"<path d='{d}' fill='none' stroke='#2a3a4a' stroke-width='{ancho:.0f}' stroke-linejoin='round' stroke-linecap='round'/>")
        if cura > 0:
            s.append(f"<path d='{d}' fill='none' stroke='#ffffff' stroke-width='{lerp(6, 30, cura):.0f}' stroke-linejoin='round' stroke-linecap='round' opacity='{min(1, cura * 1.5):.2f}'/>")
    s.append("</g>")
    return "".join(s)


def panteon(cx, base, s, op=1.0):
    g = [f"<g transform='translate({cx},{base}) scale({s:.2f})' opacity='{op:.2f}'>"]
    # cúpula y tambor detrás
    g.append(f"<path d='M-330 -330 Q-330 -560 0 -580 Q330 -560 330 -330 Z' fill='#d8cfbf' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(1, 4):
        g.append(f"<path d='M{-330 + i * 14} {-330 - i * 50} Q0 {-345 - i * 62} {330 - i * 14} {-330 - i * 50}' fill='none' stroke='#b9b2a6' stroke-width='7'/>")
    g.append(f"<rect x='-40' y='-600' width='80' height='26' rx='8' fill='#cfc6b4' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-360' y='-340' width='720' height='340' fill='#cfc6b4' stroke='{INK}' stroke-width='{LW}'/>")
    # pórtico con frontón y 8 columnas
    g.append(f"<path d='M-310 -330 L0 -460 L310 -330 Z' fill='#e9e2d2' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M-250 -345 L0 -440 L250 -345 Z' fill='#d8cfbf'/>"
             f"<rect x='-320' y='-330' width='640' height='44' fill='#e9e2d2' stroke='{INK}' stroke-width='7'/>")
    for i in range(8):
        x = -280 + i * 80
        g.append(f"<rect x='{x - 22}' y='-286' width='44' height='256' fill='#f4efe4' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='{x - 30}' y='-296' width='60' height='16' fill='#e9e2d2' stroke='{INK}' stroke-width='5'/>"
                 f"<path d='M{x - 8} -280 L{x - 8} -36 M{x + 8} -280 L{x + 8} -36' stroke='#d8cfbf' stroke-width='5'/>")
    g.append(f"<rect x='-340' y='-30' width='680' height='30' fill='#e9e2d2' stroke='{INK}' stroke-width='7'/></g>")
    return "".join(g)


def esc_hormigon(t, dur, m):
    s = [cielo("roma", "#8fd8ff", "#f0fbff")]
    for i, (cx, cy, sc) in enumerate([(200, 200, 1.0), (1000, 150, 0.8), (1600, 250, 0.9)]):
        s.append(nube((cx + t * 15) % 2300 - 300, cy, sc))
    corte = seg(t, m[1] - 0.4, m[1] + 0.6)
    pant = seg(t, m[4] - 0.3, m[4] + 1.0)
    if pant < 1:
        z = 1 + 0.35 * corte
        s.append(f"<g opacity='{1 - pant:.2f}' transform='translate(960,600) scale({z:.3f}) translate(-960,-600)'>{obra(t, corte)}</g>")
    if corte > 0 and pant < 1:
        s.append(f"<rect x='0' y='0' width='{W}' height='{H}' fill='#2a3440' opacity='{0.5 * corte * (1 - pant):.2f}'/>")
        grieta = seg(t, m[2] - 0.2, m[2] + 1.0)
        cura = seg(t, m[2] + 2.2, m[3] + 0.5)
        sc = 0.8 + 0.2 * ease(corte)
        s.append(f"<g transform='translate(960,580) scale({sc:.3f}) translate(-960,-580)'>{bloque(t, grieta, cura, corte * (1 - pant))}</g>")
        # gotas de agua que entran por la grieta
        if grieta > 0.3 and cura < 0.6:
            for i in range(6):
                k = (t * 1.4 + i / 6) % 1
                gx = 960 + 8 * math.sin(i * 3)
                gy = lerp(200, 520, k)
                s.append(f"<path d='M{gx:.0f} {gy - 22:.0f} Q{gx + 14:.0f} {gy:.0f} {gx:.0f} {gy + 8:.0f} Q{gx - 14:.0f} {gy:.0f} {gx:.0f} {gy - 22:.0f} Z' fill='#5ac8ff' stroke='{INK}' stroke-width='4' opacity='{(1 - k) * (1 - pant):.2f}'/>")
        s.append(destellos(960, 580, seg(t, m[3] - 0.6, m[3] + 1.0), 14, 330, "#ffffff"))
        # dos semanas: el sol y la luna dan vueltas (frase 3)
        ds = seg(t, m[3] - 0.2, m[3] + 0.4) * (1 - pant)
        if ds > 0:
            a = (t - m[3]) * 5
            ox, oy, rr = 1560, 560, 150
            s.append(f"<g opacity='{ds:.2f}'><circle cx='{ox}' cy='{oy}' r='{rr}' fill='#1e2a50' stroke='{INK}' stroke-width='7'/>"
                     f"<path d='M{ox - rr} {oy} A{rr} {rr} 0 0 1 {ox + rr} {oy} Z' fill='#8fd8ff'/>"
                     f"<circle cx='{ox}' cy='{oy}' r='{rr}' fill='none' stroke='{INK}' stroke-width='7'/>"
                     f"<circle cx='{ox + 100 * math.cos(a - math.pi / 2):.0f}' cy='{oy + 100 * math.sin(a - math.pi / 2):.0f}' r='30' fill='#ffd166' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='{ox + 100 * math.cos(a + math.pi / 2):.0f}' cy='{oy + 100 * math.sin(a + math.pi / 2):.0f}' r='24' fill='#f4f0d8' stroke='{INK}' stroke-width='6'/>"
                     + "".join(f"<line x1='{ox - 150 + i * 22}' y1='{oy + rr + 30}' x2='{ox - 150 + i * 22}' y2='{oy + rr + 70}' stroke='{INK}' stroke-width='7' stroke-linecap='round' opacity='{1 if i < int(clamp((t - m[3]) / 3.0) * 14) else 0.15}'/>" for i in range(14))
                     + "</g>")
    if pant > 0:
        s.append(f"<path d='M0 820 L1920 820 L1920 1080 L0 1080 Z' fill='#c9b48a' stroke='{INK}' stroke-width='{LW}' opacity='{pant:.2f}'/>")
        s.append(panteon(980, 830, lerp(0.85, 0.95, pant), pant))
        s.append(destellos(980, 400, seg(t, m[4] + 0.6, m[4] + 2.4), 14, 420))
    ax = lerp(380, 300, pant) + 25 * math.sin(t * 0.9)
    ay = 470 + 16 * math.sin(t * 1.6)
    s.append(arenillo(ax, ay, 0.62, t, arena=0.45, mira=1, susto=1.0 if m[2] < t < m[2] + 1.6 else 0.0,
                      guino=(m[3] + 2.0 < t < m[3] + 2.4)))
    return "".join(s)


# ================= 5 · Anticitera =================
def buzo(x, y, s, t, brazo=0.0):
    """Buzo con escafandra de casco de latón (1901)."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"]
    g.append(f"<path d='M0 -330 Q-40 -600 -120 -900' fill='none' stroke='{INK}' stroke-width='16'/><path d='M0 -330 Q-40 -600 -120 -900' fill='none' stroke='#8a8f96' stroke-width='8'/>")
    a = math.radians(30 + 80 * brazo)
    hx, hy = 60 + 130 * math.sin(a), -210 + 130 * math.cos(a)
    g.append(f"<path d='M-56 -200 L-90 -60' stroke='{INK}' stroke-width='48' stroke-linecap='round'/><path d='M-56 -200 L-90 -60' stroke='#9aa3ad' stroke-width='34' stroke-linecap='round'/>")
    g.append(f"<path d='M-36 -60 L-50 0 M36 -60 L50 0' stroke='{INK}' stroke-width='52' stroke-linecap='round'/><path d='M-36 -60 L-50 0 M36 -60 L50 0' stroke='#9aa3ad' stroke-width='38' stroke-linecap='round'/>")
    g.append(f"<rect x='-80' y='-10' width='70' height='26' rx='10' fill='#5a4a3a' stroke='{INK}' stroke-width='6'/><rect x='12' y='-10' width='70' height='26' rx='10' fill='#5a4a3a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-70 -250 Q0 -270 70 -250 L60 -60 Q0 -40 -60 -60 Z' fill='#9aa3ad' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M56 -200 L{hx:.0f} {hy:.0f}' stroke='{INK}' stroke-width='48' stroke-linecap='round'/><path d='M56 -200 L{hx:.0f} {hy:.0f}' stroke='#9aa3ad' stroke-width='34' stroke-linecap='round'/>")
    g.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='22' fill='#5a4a3a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-80 -250 L80 -250 L70 -280 L-70 -280 Z' fill='#d9a441' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='0' cy='-340' r='74' fill='#e0b04a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='14' cy='-340' r='38' fill='#bfe6ff' stroke='{INK}' stroke-width='8'/>"
             f"<path d='M-10 -360 Q2 -372 18 -368' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round'/>"
             f"<circle cx='-50' cy='-386' r='12' fill='#d9a441' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


def anfora(x, y, s, ang):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({s:.2f})'>"
            f"<path d='M-14 -110 L14 -110 L16 -80 Q60 -50 46 30 Q30 90 0 110 Q-30 90 -46 30 Q-60 -50 -16 -80 Z' fill='#c0643a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-16 -90 Q-50 -90 -40 -50 M16 -90 Q50 -90 40 -50' fill='none' stroke='{INK}' stroke-width='8'/></g>")


def pecio(t):
    s = [f"<path d='M0 860 Q400 820 900 850 T1920 840 L1920 1080 L0 1080 Z' fill='#d9c08a' stroke='{INK}' stroke-width='{LW}'/>"]
    # casco de madera roto, medio enterrado
    s.append(f"<path d='M1000 880 Q1100 700 1500 680 Q1760 690 1820 860 Z' fill='#6a4a2a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(6):
        x = 1100 + i * 120
        s.append(f"<path d='M{x} {870 - i * 4} Q{x + 20} {740 - (i % 3) * 20} {x + 70} {700 - (i % 2) * 20}' fill='none' stroke='#4a3218' stroke-width='16' stroke-linecap='round'/>")
    s.append(anfora(1180, 840, 0.8, -70) + anfora(1450, 830, 0.75, 80) + anfora(1640, 850, 0.7, -100))
    for i in range(4):   # algas
        x = 120 + i * 260
        sw = 18 * math.sin(t * 1.3 + i)
        s.append(f"<path d='M{x} 880 Q{x + sw} 800 {x - sw:.0f} 720 Q{x + sw} 660 {x:.0f} 620' fill='none' stroke='#3a9a5a' stroke-width='16' stroke-linecap='round'/>")
    return "".join(s)


def mecanismo(cx, cy, s, t, vel=1.0, nuevo=1.0, giro=0.0):
    """Mecanismo de Anticitera reconstruido: caja de madera, gran esfera de bronce con punteros y engranajes."""
    g = [f"<g transform='translate({cx:.0f},{cy:.0f}) scale({s:.3f})'>"]
    bronce, oscuro = mix("#5f8a6a", "#e0aa48", nuevo), mix("#3e6a4c", "#a8742a", nuevo)
    g.append(f"<rect x='-300' y='-280' width='600' height='560' rx='20' fill='#8a5a30' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-270' y='-250' width='540' height='500' rx='14' fill='#a8703e' stroke='{INK}' stroke-width='6'/>")
    # engranajes que asoman a la izquierda (detrás de la esfera)
    g.append(engranaje(-180, -150, 80, 14, giro * 1.4, bronce, oscuro, 6))
    g.append(engranaje(-200, 140, 64, 12, -giro * 1.75 + 10, bronce, oscuro, 6))
    # gran esfera
    g.append(f"<circle r='220' fill='{bronce}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle r='190' fill='{oscuro}' stroke='{INK}' stroke-width='5'/>")
    for i in range(36):
        a = i / 36 * 2 * math.pi
        g.append(f"<line x1='{196 * math.cos(a):.1f}' y1='{196 * math.sin(a):.1f}' x2='{214 * math.cos(a):.1f}' y2='{214 * math.sin(a):.1f}' stroke='{INK}' stroke-width='{5 if i % 3 == 0 else 3}'/>")
    for r in (150, 115, 85):
        g.append(f"<circle r='{r}' fill='none' stroke='{mix(oscuro, '#ffffff', 0.25)}' stroke-width='4'/>")
    # punteros: planetas, Luna y Sol
    for r, v, col, tam in ((150, 0.35, "#e0603a", 14), (115, 0.55, "#c9e0ff", 12), (85, 0.8, "#9ad07a", 11)):
        a = giro * v * 0.05
        g.append(f"<line x1='0' y1='0' x2='{r * math.cos(a):.1f}' y2='{r * math.sin(a):.1f}' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{r * math.cos(a):.1f}' cy='{r * math.sin(a):.1f}' r='{tam}' fill='{col}' stroke='{INK}' stroke-width='4'/>")
    a_luna = giro * 0.13 * 0.05 * 12
    a_sol = giro * 0.05
    g.append(f"<line x1='0' y1='0' x2='{170 * math.cos(a_sol):.1f}' y2='{170 * math.sin(a_sol):.1f}' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>"
             f"<circle cx='{170 * math.cos(a_sol):.1f}' cy='{170 * math.sin(a_sol):.1f}' r='24' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    lx, ly = 135 * math.cos(a_luna), 135 * math.sin(a_luna)
    g.append(f"<line x1='0' y1='0' x2='{lx:.1f}' y2='{ly:.1f}' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
             f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='20' fill='#f4f0d8' stroke='{INK}' stroke-width='5'/>"
             f"<path d='M{lx:.1f} {ly - 20:.1f} A20 20 0 0 1 {lx:.1f} {ly + 20:.1f} Z' fill='#3a3a4a'/>")
    g.append(f"<circle r='22' fill='{bronce}' stroke='{INK}' stroke-width='6'/>")
    # manivela a la derecha
    a = math.radians(giro * 2)
    mx, my = 300 + 0, 0
    hx, hy = mx + 90 * math.cos(a), my + 90 * math.sin(a)
    g.append(f"<circle cx='{mx}' cy='{my}' r='26' fill='{bronce}' stroke='{INK}' stroke-width='6'/>"
             f"<line x1='{mx}' y1='{my}' x2='{hx:.1f}' y2='{hy:.1f}' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
             f"<line x1='{mx}' y1='{my}' x2='{hx:.1f}' y2='{hy:.1f}' stroke='{bronce}' stroke-width='11' stroke-linecap='round'/>"
             f"<circle cx='{hx:.1f}' cy='{hy:.1f}' r='20' fill='#8a5a30' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def fragmento(cx, cy, s, t):
    """Trozo de bronce corroído y verde con ruedas dentadas a la vista."""
    return (f"<g transform='translate({cx:.0f},{cy:.0f}) scale({s:.3f})'>"
            f"<path d='M-140 -90 L-60 -130 L40 -110 L130 -60 L150 30 L90 110 L-20 130 L-120 90 L-160 0 Z' fill='#4e7a5a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            + engranaje(-20, -10, 70, 14, 12, "#7aa07a", "#3e6a4c", 5)
            + engranaje(80, 50, 34, 9, -8, "#7aa07a", "#3e6a4c", 4)
            + f"<path d='M-150 -20 L-110 -40 L-120 10 Z M100 -80 L140 -50 L110 -40 Z' fill='#3a5a44'/>"
            f"<circle cx='-90' cy='70' r='14' fill='#8ab08a'/><circle cx='40' cy='100' r='10' fill='#8ab08a'/></g>")


def esc_anticitera(t, dur, m):
    nuevo = seg(t, m[4] - 0.4, m[4] + 1.2)
    s = []
    if nuevo < 1:
        s.append(cielo("marA", "#2a8fd0", "#0b4a80"))
        for i in range(6):
            x = 150 + i * 330 + 60 * math.sin(t * 0.4 + i)
            s.append(f"<path d='M{x - 40:.0f} 0 L{x + 60:.0f} 0 L{x + 260:.0f} {H} L{x + 60:.0f} {H} Z' fill='#ffffff' opacity='{0.10 + 0.05 * math.sin(t * 0.7 + i * 2):.2f}'/>")
        s.append(pecio(t))
        baja = seg(t, m[1] - 0.6, m[1] + 2.2)
        coge = seg(t, m[2] - 0.2, m[2] + 0.8)
        s.append(buzo(lerp(420, 780, baja), lerp(-100, 900, baja), 0.9, t, brazo=coge))
        for i in range(6):   # burbujas del buzo
            k = (t * 0.8 + i / 6) % 1
            s.append(f"<circle cx='{lerp(420, 780, baja) + 20 + 14 * math.sin(t * 3 + i):.0f}' cy='{lerp(-100, 900, baja) - 400 - k * 300:.0f}' r='{6 + 6 * k:.0f}' fill='#d8f3ff' fill-opacity='0.35' stroke='#fff' stroke-width='3' opacity='{1 - k:.2f}'/>")
        # el trozo: primero en el fondo, luego grande en el centro (frase 2)
        gr = seg(t, m[2] + 0.3, m[2] + 1.8)
        fx, fy = lerp(990, 1100, gr), lerp(850, 560, gr)
        s.append(f"<g opacity='{1 - nuevo:.2f}'>" + (f"<circle cx='{fx:.0f}' cy='{fy:.0f}' r='{260 * gr:.0f}' fill='#bfe9ff' opacity='{0.25 * gr:.2f}'/>" if gr > 0 else "")
                 + fragmento(fx, fy, lerp(0.35, 1.25, gr), t) + "</g>")
        s.append(destellos(fx, fy, seg(t, m[2] + 1.0, m[2] + 2.6), 12, 300, "#ffffff"))
        if nuevo > 0:
            s.append(f"<rect width='{W}' height='{H}' fill='#ffe9a0' opacity='{math.sin(math.pi * nuevo):.2f}'/>")
    if nuevo > 0:
        osc = seg(t, m[5] - 0.2, m[5] + 0.8) * (1 - seg(t, m[6] - 0.2, m[6] + 0.6))
        s2 = [cielo("cosmos", mix("#1a2a5a", "#060818", osc), mix("#3a2a6a", "#14102a", osc))]
        for x, y, r, f in ESTRELLAS:
            s2.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * 0.6:.1f}' fill='#fff6d8' opacity='{0.4 + 0.5 * math.sin(t * 2 + f):.2f}'/>")
        # eclipse en el cielo (frase 5)
        if osc > 0:
            ex, ey = 1560, 420
            lun = lerp(ex + 170, ex, seg(t, m[5] - 0.2, m[5] + 1.2))
            s2.append(f"<g opacity='{osc:.2f}'><circle cx='{ex}' cy='{ey}' r='{150 + 10 * math.sin(t * 3):.0f}' fill='#ffe9a0' opacity='0.55'/>"
                      + "".join(f"<line x1='{ex + 100 * math.cos(i / 16 * 6.283):.0f}' y1='{ey + 100 * math.sin(i / 16 * 6.283):.0f}' x2='{ex + 150 * math.cos(i / 16 * 6.283):.0f}' y2='{ey + 150 * math.sin(i / 16 * 6.283):.0f}' stroke='#fff6c8' stroke-width='9' stroke-linecap='round' opacity='0.95'/>" for i in range(16))
                      + f"<circle cx='{ex}' cy='{ey}' r='92' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
                      f"<circle cx='{lun:.0f}' cy='{ey}' r='84' fill='#1a1a2a' stroke='{INK}' stroke-width='6'/></g>")
            # corona de laurel (Juegos Olímpicos)
            lau = seg(t, m[5] + 1.6, m[5] + 2.4)
            if lau > 0:
                lx, ly = 400, 480
                hojas = "".join(f"<ellipse cx='{lx + 110 * math.cos(a):.0f}' cy='{ly + 110 * math.sin(a):.0f}' rx='26' ry='12' fill='#5ab04a' stroke='{INK}' stroke-width='4' transform='rotate({math.degrees(a) + 90:.0f} {lx + 110 * math.cos(a):.0f} {ly + 110 * math.sin(a):.0f})'/>"
                                for a in [math.pi * (0.62 + 0.11 * i) for i in range(8)] + [math.pi * (0.38 - 0.11 * i) for i in range(8)])
                s2.append(f"<g opacity='{lau * osc:.2f}' transform='translate({lx},{ly}) scale({0.6 + 0.4 * ease(lau):.2f}) translate({-lx},{-ly})'>{hojas}"
                          f"<path d='M{lx - 20} {ly + 110} L{lx} {ly + 150} L{lx + 20} {ly + 110}' fill='none' stroke='#e62117' stroke-width='10'/></g>")
        giro = max(0.0, t - m[4]) * 140
        brilla = seg(t, m[6] - 0.2, m[6] + 1.0)
        z = lerp(0.8, 1.0, ease(nuevo)) * (1 + 0.05 * brilla)
        if brilla > 0:
            s2.append(f"<circle cx='930' cy='590' r='{420 + 20 * math.sin(t * 4):.0f}' fill='#ffd97a' opacity='{0.3 * brilla:.2f}'/>")
            for i in range(14):
                a = i / 14 * 2 * math.pi + t * 0.3
                s2.append(f"<path d='M{930 + 380 * math.cos(a):.0f} {590 + 380 * math.sin(a):.0f} L{930 + 520 * math.cos(a + 0.06):.0f} {590 + 520 * math.sin(a + 0.06):.0f} L{930 + 520 * math.cos(a - 0.06):.0f} {590 + 520 * math.sin(a - 0.06):.0f} Z' fill='#ffe9a0' opacity='{0.4 * brilla:.2f}'/>")
        s2.append(mecanismo(930, 590, 1.0 * z, t, nuevo=1.0, giro=giro))
        s2.append(destellos(960, 590, seg(t, m[6] + 0.2, m[6] + 2.0), 16, 460))
        s.append(f"<g opacity='{nuevo:.2f}'>{''.join(s2)}</g>")
    # Arenillo
    vuelta = seg(t, m[4] - 0.6, m[4] + 0.8)
    ax = lerp(1600, 1680, nuevo) + 25 * math.sin(t * 0.9)
    ay = lerp(420, 720, nuevo) + 16 * math.sin(t * 1.6)
    s.append(remolino_arena(ax, ay, t, math.sin(math.pi * vuelta), 300))
    s.append(arenillo(ax, ay, 0.6, t, arena=lerp(0.3, 0.2, nuevo), ang=360 * vuelta + 6 * math.sin(t * 1.4),
                      mira=-1, susto=1.0 if m[6] - 0.2 < t < m[6] + 1.6 else 0.0, brilla=seg(t, m[6], m[6] + 1)))
    return "".join(s)


# ================= despedida =================
def esc_final(t, dur, m):
    sube = seg(t, 0, 3.5)
    s = ["<defs><linearGradient id='atar' x1='0' y1='0' x2='0' y2='1'>"
         f"<stop offset='0' stop-color='{mix('#3a2a6a', '#ff8a6b', sube)}'/><stop offset='1' stop-color='{mix('#6a4a8a', '#ffe0a8', sube)}'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#atar)'/>",
         f"<circle cx='960' cy='{lerp(800, 560, sube):.0f}' r='120' fill='#ffd166' stroke='{INK}' stroke-width='{LW}' opacity='{sube:.2f}'/>"]
    for i, (cx, cy, sc) in enumerate([(200, 200, 1.0), (1500, 150, 0.9), (1100, 260, 0.7)]):
        dx = (t * 16 * (1 + i * 0.3)) % 2300
        s.append(nube((cx + dx) % 2300 - 300, cy, sc, "#fff4ea"))
    # colinas y una casita
    s.append(f"<path d='M0 700 Q400 600 900 680 T1920 650 L1920 1080 L0 1080 Z' fill='#7ac25a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M0 820 Q500 760 1000 820 T1920 800 L1920 1080 L0 1080 Z' fill='#5aa84a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='1420' y='560' width='180' height='130' fill='#fff1d6' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M1400 565 L1510 480 L1620 565 Z' fill='#e0603a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='1490' y='620' width='40' height='70' fill='#8a5a30' stroke='{INK}' stroke-width='5'/>"
             f"<rect x='1438' y='590' width='36' height='36' fill='#ffe066' stroke='{INK}' stroke-width='5'/>")
    s.append(palmera(200, 760, 0.8, t))
    zx = lerp(560, 400, seg(t, m[1] - 0.5, m[1] + 1.0))
    zy = lerp(1150, 520, sube) + 14 * math.sin(t * 2)
    s.append(remolino_arena(zx, zy, t, 0.5 * (1 - sube) + 0.2, 260))
    s.append(arenillo(zx, zy, 0.85, t, arena=0.06, ang=6 * math.sin(t * 1.6), guino=(m[4] + 0.3 < t < m[4] + 0.7)))
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
        s.append(f"<g transform='translate(1080,400) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1445' cy='400' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1445, 400, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1445, 400, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1060, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(950, 415, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1460, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 420, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1080, 400, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Un ordenador de hace dos mil años?", "escena": esc_intro, "susc": 2,
     "frases": ["¿Te imaginas encontrar un ordenador… de hace dos mil años?",
                "Hoy viajamos al pasado con Arenillo, un reloj de arena volador, y la última parada te va a dejar con la boca abierta.",
                "Suscríbete a Mundo Curioso cinco mil y… ¡despegamos!"]},
    {"titulo": "1. El puñal caído del cielo", "escena": esc_egipto, "tarjeta": "CAPÍTULO 1 · EL PUÑAL DEL CIELO",
     "frases": ["Primera parada: Egipto, hace más de tres mil trescientos años.",
                "Entramos en la tumba del faraón Tutankamón, llena de oro y de tesoros.",
                "Entre ellos hay un puñal con el mango de oro… y la hoja de hierro.",
                "Pero en aquella época, los egipcios todavía no sabían fabricar hierro.",
                "Los científicos lo analizaron y encontraron mucho níquel: ¡ese hierro venía de un meteorito!",
                "El faraón tenía un puñal hecho con hierro caído del cielo."],
     "grandes": {4: "¡METEORITO!"}},
    {"titulo": "2. La queja más antigua del mundo", "escena": esc_ur, "tarjeta": "CAPÍTULO 2 · LA QUEJA MÁS ANTIGUA",
     "frases": ["Arenillo da un salto todavía más atrás: Mesopotamia, hace casi cuatro mil años.",
                "En la ciudad de Ur, un señor llamado Nanni está muy, muy enfadado.",
                "Le compró cobre a un comerciante, Ea Násir, y le llegó de mala calidad.",
                "Así que le escribió una carta de queja… ¡en una tablilla de barro!",
                "Es la reclamación de cliente más antigua que se conoce: ¡se queja de que lo han tratado con desprecio!",
                "Pero en la siguiente parada nos espera algo que huele de maravilla…"],
     "grandes": {4: "¡RECLAMACIÓN!"}},
    {"titulo": "3. Comida rápida en Pompeya", "escena": esc_pompeya, "tarjeta": "CAPÍTULO 3 · COMIDA RÁPIDA ROMANA",
     "frases": ["Volamos a la ciudad romana de Pompeya, antes de la erupción del año setenta y nueve.",
                "¿Hueles eso? En la calle hay un mostrador lleno de ollas de barro.",
                "Es un termopolio: ¡un puesto de comida rápida de hace casi dos mil años!",
                "Los arqueólogos encontraron restos de pato, cerdo, cabra, pescado… ¡y hasta caracoles!",
                "Y el mostrador estaba decorado con pinturas de animales, como dos patos y un gallo."],
     "grandes": {2: "COMIDA RÁPIDA"}},
    {"titulo": "4. El hormigón que se cura solo", "escena": esc_hormigon, "tarjeta": "CAPÍTULO 4 · EL HORMIGÓN QUE SE CURA",
     "frases": ["Seguimos por el Imperio romano, donde construyen edificios enormes con hormigón.",
                "Pero el hormigón romano esconde un secreto: unos grumitos blancos de cal.",
                "Cuando se abre una grieta y entra el agua, la cal se disuelve y vuelve a endurecerse… ¡y tapa la grieta!",
                "Unos científicos lo probaron, y las grietas se cerraron solas en solo dos semanas.",
                "Por eso la gran cúpula del Panteón de Roma sigue en pie casi dos mil años después.",
                "Pero lo que nos espera en el fondo del mar es todavía más increíble…"],
     "grandes": {2: "¡SE CURA SOLO!", 3: "2 SEMANAS"}},
    {"titulo": "5. Un ordenador de hace 2.000 años", "escena": esc_anticitera, "tarjeta": "CAPÍTULO 5 · EL ORDENADOR DE BRONCE",
     "frases": ["Última parada: una isla griega, en el año mil novecientos uno.",
                "Unos buceadores que buscaban esponjas encuentran un barco romano hundido.",
                "Entre los restos aparece un trozo de bronce verde y roto… con ruedecitas dentadas.",
                "Es el mecanismo de Anticitera, y tiene unos dos mil años.",
                "Arenillo nos lleva atrás para verlo nuevo: al darle vueltas, sus engranajes movían el Sol, la Luna y los planetas.",
                "¡Y predecía los eclipses y hasta las fechas de los Juegos Olímpicos!",
                "Por eso lo llaman el primer ordenador analógico del mundo. ¡Un ordenador de hace dos mil años!"],
     "grandes": {5: "ECLIPSES", 6: "¡2.000 AÑOS!"}, "extra": 1.0},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así, con la arena de Arenillo casi agotada, volvemos a casa.",
                "Si este viaje por el pasado te ha gustado, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ninguna aventura: cada día, una historia nueva llena de curiosidades.",
                "Y cuéntame en los comentarios: ¿a qué época viajarías tú?",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
