"""Episodio: "La vuelta al mundo de los animales más extremos" con Rumbo, una brújula voladora (original).

Datos (verificados el 28-11-2026):
- Algunos vencejos comunes (Apus apus) pasan unos 10 meses seguidos volando sin aterrizar durante su
  viaje entre Europa (Suecia) y África: comen insectos en vuelo; se comprobó con registradores diminutos
  colocados en el lomo (Hedenström et al., Current Biology 2016; Lund University; Nature News 2016;
  National Geographic; Audubon).
- La rata topo desnuda (Heterocephalus glaber, África oriental) vive en colonias de hasta cientos de
  animales en túneles con poco oxígeno; en el laboratorio aguantó 18 minutos sin nada de oxígeno y se
  recuperó sin daños; su cuerpo pasa a quemar fructosa, como las plantas (Park et al., Science 2017;
  National Geographic; PBS NewsHour; NPR).
- La ardilla ártica (Urocitellus parryii, Alaska) hiberna unos 7-8 meses y su temperatura corporal baja
  hasta -2,9 °C sin congelarse (sobreenfriamiento), la más baja medida en un mamífero; cada 2-3 semanas
  tirita y se calienta unas horas (Barnes, Science 1989; Guinness World Records «Lowest body temperature
  recorded in a mammal»; University of Alaska Fairbanks; NPS).
- La gamba mantis pavo real (Odontodactylus scyllarus) golpea con sus mazas a hasta 23 m/s (unos
  80 km/h), con la aceleración de una bala del calibre 22; el golpe forma burbujas de cavitación que
  estallan y le permite romper conchas de caracol (Patek, Korff y Caldwell, Nature 2004; UC Berkeley
  News 2004; National Geographic).
- La «medusa inmortal» (Turritopsis dohrnii, Mediterráneo), de unos 4,5 mm, con el estómago rojo:
  cuando está dañada, enferma o envejece puede volver a ser pólipo y empezar su vida de nuevo
  (American Museum of Natural History «The Immortal Jellyfish»; Natural History Museum de Londres;
  Britannica).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-28-historia"
TITULO = "La vuelta al mundo de los animales más extremos"
VOZ = "ef_dora"
VELOCIDAD = 0.96
MUSICA = 67

W, H = 1920, 1080
rng = np.random.default_rng(28)
NIEVE = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 7), rng.uniform(30, 80)) for _ in range(80)]
PIEDRAS = [(rng.uniform(0, W), rng.uniform(420, 1060), rng.uniform(8, 26)) for _ in range(46)]
BANDADA = [(rng.uniform(0, 1), rng.uniform(250, 820), rng.uniform(0.25, 0.5), rng.uniform(0.8, 1.6)) for _ in range(14)]
PART = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(10, 30)) for _ in range(50)]
MANCHAS = [(rng.uniform(-60, 60), rng.uniform(-30, 25), rng.uniform(5, 10)) for _ in range(12)]


# ================= piezas comunes =================
def cielo(top, bot, id_):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def nube(x, y, sc, col="#fff", op=1.0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def nubes(t, lista, col="#fff", vel=18):
    s = []
    for i, (cx, cy, sc) in enumerate(lista):
        dx = (t * vel * (1 + i * 0.3)) % 2300
        s.append(nube((cx + dx) % 2300 - 300, cy, sc, col))
    return "".join(s)


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


def burbujas(t, x, y, n=8, sube=320, tam=1.0, fase=0.0):
    s = []
    for i in range(n):
        k = ((t * 0.9 + i / n + fase) % 1)
        bx = x + 22 * math.sin(t * 3 + i * 1.7) - i * 4
        by = y - k * sube
        r = (5 + (i % 4) * 3) * tam * (0.6 + k)
        s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{r:.1f}' fill='#d8f3ff' fill-opacity='0.35' stroke='#ffffff' stroke-width='3' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def rumbo(x, y, s, t, ang=0.0, guino=False, mira=(0, 0), frio=0.0, agua=False):
    """Rumbo: brújula de latón voladora con alas, hélice en la anilla y aguja roja y azul por nariz."""
    parp = 0.12 if (t % 3.9) < 0.13 or guino else 1.0
    hel = abs(math.sin(t * 22))
    ala = 14 * math.sin(t * (5 if agua else 9))
    tir = 3 * math.sin(t * 60) * frio
    agu = 10 * math.sin(t * 1.3)
    g = [f"<g transform='translate({x + tir:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    # alas
    for lado in (-1, 1):
        g.append(f"<g transform='scale({lado},1) rotate({-ala:.1f} 78 -6)'>"
                 f"<path d='M78 -6 Q150 -90 215 -70 Q190 -40 200 -22 Q160 -18 168 8 Q120 14 80 20 Z' fill='#8fe0ee' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M100 -10 Q150 -50 190 -58 M104 4 Q140 -14 168 -14' fill='none' stroke='#4fb6c9' stroke-width='5' stroke-linecap='round'/></g>")
    # anilla y hélice
    g.append(f"<circle cx='0' cy='-98' r='16' fill='none' stroke='{INK}' stroke-width='15'/>"
             f"<circle cx='0' cy='-98' r='16' fill='none' stroke='#f2b632' stroke-width='7'/>"
             f"<rect x='-5' y='-140' width='10' height='28' rx='4' fill='#9aa3ad' stroke='{INK}' stroke-width='5'/>"
             f"<ellipse cx='0' cy='-142' rx='{8 + 62 * hel:.0f}' ry='10' fill='#e85d75' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='0' cy='-142' r='8' fill='#ffd23f' stroke='{INK}' stroke-width='4'/>")
    # caja de latón
    g.append(f"<circle r='90' fill='#f2b632' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-70 -48 A84 84 0 0 1 40 -78' fill='none' stroke='#ffe08a' stroke-width='9' stroke-linecap='round'/>"
             f"<circle r='68' fill='{mix('#fff6dc', '#dff2ff', frio)}' stroke='{INK}' stroke-width='6'/>")
    for a in range(0, 360, 90):
        g.append(f"<path d='M0 -64 L7 -50 L-7 -50 Z' fill='#c98f1a' transform='rotate({a})'/>")
    for a in range(45, 360, 90):
        g.append(f"<circle cx='0' cy='-58' r='3.5' fill='#c98f1a' transform='rotate({a})'/>")
    # aguja (nariz) que oscila
    g.append(f"<g transform='translate(0,10) rotate({agu:.1f})'>"
             f"<path d='M0 -22 L8 0 L-8 0 Z' fill='#e8382f' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
             f"<path d='M0 22 L8 0 L-8 0 Z' fill='#3a6fd8' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
             f"<circle r='4' fill='{INK}'/></g>")
    # ojos
    for ex in (-28, 28):
        g.append(f"<g transform='translate({ex},-22) scale(1,{parp})'><ellipse rx='16' ry='20' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{3 + mira[0]:.1f}' cy='{2 + mira[1]:.1f}' r='9' fill='#1e2a38'/><circle cx='{mira[0]:.1f}' cy='{-3 + mira[1]:.1f}' r='3.5' fill='#fff'/></g>")
    g.append(f"<circle cx='-46' cy='14' r='9' fill='#ff9aa8' opacity='0.7'/><circle cx='46' cy='14' r='9' fill='#ff9aa8' opacity='0.7'/>")
    if frio > 0.3:
        g.append(f"<path d='M-20 44 l6 -5 l6 5 l6 -5 l6 5 l6 -5 l6 5' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M-18 40 Q0 54 18 40' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def cronometro(cx, cy, t, k, vueltas=1.0):
    if k <= 0:
        return ""
    ang = (t * 720) % 360
    s = (0.6 + 0.4 * ease(min(1, k * 2))) * 0.85
    return (f"<g transform='translate({cx},{cy}) scale({s:.2f})' opacity='{min(1, k * 3):.2f}'>"
            f"<rect x='-18' y='-138' width='36' height='30' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
            f"<circle r='112' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle r='92' fill='none' stroke='#ffd23f' stroke-width='10'/>"
            + "".join(f"<line x1='0' y1='-80' x2='0' y2='-66' stroke='{INK}' stroke-width='6' transform='rotate({a})'/>" for a in range(0, 360, 30))
            + f"<line x1='0' y1='0' x2='0' y2='-72' stroke='#e8382f' stroke-width='9' stroke-linecap='round' transform='rotate({ang:.0f})'/>"
            f"<circle r='12' fill='{INK}'/></g>")


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


# ================= animales =================
def vencejo(x, y, s, t, ang=0.0, fase=0.0, mochila=0.0, ojo=True):
    """Vencejo visto desde arriba: alas largas en forma de hoz, cola corta ahorquillada, garganta clara."""
    b = math.sin(t * 16 + fase)
    sy = 0.75 + 0.25 * b
    parp = 0.15 if ((t + fase) % 3.1) < 0.12 else 1
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    for lado in (-1, 1):
        g.append(f"<g transform='scale(1,{lado * sy:.3f})'>"
                 f"<path d='M18 -8 Q-10 -70 -95 -150 Q-150 -190 -190 -200 Q-120 -140 -70 -60 Q-40 -20 -20 -6 Z' fill='#3b302c' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M0 -14 Q-40 -60 -100 -120' fill='none' stroke='#55483f' stroke-width='5' stroke-linecap='round'/></g>")
    g.append(f"<path d='M-60 -6 L-112 -30 L-92 0 L-112 30 L-60 6 Z' fill='#3b302c' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M-70 0 Q-40 -26 20 -22 Q62 -20 74 0 Q62 20 20 22 Q-40 26 -70 0 Z' fill='#45382f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<ellipse cx='62' cy='0' rx='12' ry='9' fill='#d8cfc4'/>"
             f"<path d='M74 -4 L86 0 L74 4 Z' fill='#2a2220' stroke='{INK}' stroke-width='3'/>")
    if ojo:
        for ey in (-11, 11):
            g.append(f"<g transform='translate(52,{ey}) scale(1,{parp})'><circle r='6.5' fill='#fff' stroke='{INK}' stroke-width='2.5'/><circle cx='1.5' r='3.5' fill='{INK}'/></g>")
    if mochila > 0:
        g.append(f"<g opacity='{mochila:.2f}'><rect x='-26' y='-10' width='30' height='20' rx='6' fill='#9aa3ad' stroke='{INK}' stroke-width='4'/>"
                 f"<circle cx='-4' cy='0' r='4' fill='{'#5affb4' if (t * 2) % 1 < 0.5 else '#2a7a5a'}'/></g>")
    g.append("</g>")
    return "".join(g)


def rata_topo(x, y, s, t, fase=0.0, dir_=1, feliz=0.0, andar=1.0):
    """Rata topo desnuda: rosa, arrugada, sin pelo, ojos diminutos y dos pares de dientes enormes."""
    bob = 4 * math.sin(t * 10 * andar + fase) * andar
    pata = 10 * math.sin(t * 12 * andar + fase) * andar
    parp = 0.15 if ((t + fase) % 3.4) < 0.13 else 1
    g = [f"<g transform='translate({x:.1f},{y + bob:.1f}) scale({s * dir_:.3f},{s:.3f})'>"]
    g.append(f"<path d='M-120 10 Q-160 20 -175 -4' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
             f"<path d='M-120 10 Q-160 20 -175 -4' fill='none' stroke='#e9a99a' stroke-width='6' stroke-linecap='round'/>")
    for px, ph in ((-80, pata), (-40, -pata), (40, pata), (80, -pata)):
        g.append(f"<path d='M{px} 30 l{ph * 0.5:.0f} 26 l14 0' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='M{px} 30 l{ph * 0.5:.0f} 26 l14 0' fill='none' stroke='#f0a898' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M-130 0 Q-130 -58 -30 -60 Q60 -62 110 -34 Q150 -14 150 6 Q148 34 100 44 Q0 58 -100 44 Q-132 36 -130 0 Z' fill='#f4b8aa' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(6):
        wx = -90 + i * 34
        g.append(f"<path d='M{wx} -44 Q{wx + 8} -10 {wx} 30' fill='none' stroke='#d98e7e' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M100 -30 Q120 -24 128 -14' fill='none' stroke='#d98e7e' stroke-width='5' stroke-linecap='round'/>")
    # dientes de arriba y de abajo
    g.append(f"<path d='M136 -2 L140 34 Q146 38 150 34 L150 -2 Z' fill='#fff2c2' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
             f"<path d='M128 18 L130 50 Q136 54 140 50 L142 18 Z' fill='#fff2c2' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<circle cx='148' cy='-6' r='7' fill='#d97a8a' stroke='{INK}' stroke-width='3'/>")
    for wy in (-10, 0):
        g.append(f"<path d='M140 {wy} l40 {wy - 10}' stroke='{INK}' stroke-width='2.5' opacity='0.7'/>")
    g.append(f"<g transform='translate(96,-26) scale(1,{parp})'><circle r='6' fill='{INK}'/><circle cx='-2' cy='-2' r='2' fill='#fff'/></g>")
    if feliz > 0:
        g.append(f"<path d='M106 14 Q116 22 128 16' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round' opacity='{feliz:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def ardilla(x, y, s, t, tirita=0.0, frio=0.0):
    """Ardilla ártica hecha una bola, durmiendo, con la cola por encima y el lomo moteado."""
    resp = 1 + 0.025 * math.sin(t * 1.4)
    jx = 5 * math.sin(t * 70) * tirita
    piel = mix("#c98b4e", "#a9b7c6", frio * 0.45)
    cola = mix("#9a6a3a", "#8a98a8", frio * 0.45)
    g = [f"<g transform='translate({x + jx:.1f},{y:.1f}) scale({s * resp:.3f},{s / resp:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='0' rx='150' ry='112' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='10' cy='40' rx='100' ry='55' fill='{mix('#f2dcb8', '#dfe8f0', frio * 0.4)}'/>")
    for mx, my, mr in MANCHAS:
        g.append(f"<ellipse cx='{mx * 1.6:.0f}' cy='{my * 2 - 30:.0f}' rx='{mr:.0f}' ry='{mr * 0.7:.0f}' fill='#f6ead4' opacity='0.85'/>")
    # cabeza metida, oreja pequeña, ojo cerrado y hocico
    g.append(f"<circle cx='96' cy='30' r='58' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M70 -14 Q76 -36 92 -22' fill='{piel}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M96 20 Q110 30 124 20' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
             f"<ellipse cx='146' cy='48' rx='12' ry='9' fill='#7a4a3a' stroke='{INK}' stroke-width='4'/>"
             f"<path d='M118 52 Q128 62 140 58' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    # cola tapando la nariz
    g.append(f"<path d='M-140 30 Q-120 130 40 120 Q150 110 170 70 Q120 92 40 92 Q-80 92 -110 20 Z' fill='{cola}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M-110 60 Q-40 104 60 100 M-60 90 Q0 110 100 98' fill='none' stroke='{mix(cola, '#000000', 0.2)}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M-60 -100 Q-20 -112 30 -104' fill='none' stroke='#e7b980' stroke-width='9' stroke-linecap='round' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g)


def gamba_mantis(x, y, s, t, golpe=0.0):
    """Gamba mantis pavo real mirando a la izquierda: cuerpo verde segmentado, ojos con pedúnculo,
    mazas rojas plegadas delante (golpe: 0 plegada, 1 estirada) y abanico de la cola."""
    parp = 0.15 if (t % 2.9) < 0.12 else 1
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"]
    # patitas nadadoras bajo el abdomen
    for i in range(5):
        px = 40 + i * 44
        sw = 8 * math.sin(t * 9 + i)
        g.append(f"<path d='M{px} 34 q{sw:.0f} 22 {-6 + sw:.0f} 38' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
                 f"<path d='M{px} 34 q{sw:.0f} 22 {-6 + sw:.0f} 38' fill='none' stroke='#ff8a3d' stroke-width='6' stroke-linecap='round'/>")
    # abanico de la cola
    g.append(f"<path d='M262 -6 Q330 -70 350 -40 Q336 0 350 40 Q330 70 262 14 Z' fill='#3a8dff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<path d='M270 -4 Q320 -40 336 -30 M270 10 Q320 40 336 30' fill='none' stroke='#ff5a5a' stroke-width='6' stroke-linecap='round'/>")
    # abdomen segmentado
    for i in range(6):
        sx = 250 - i * 40
        g.append(f"<path d='M{sx} -34 Q{sx + 26} -40 {sx + 30} -6 Q{sx + 26} 34 {sx} 36 Q{sx - 30} 36 {sx - 30} 0 Q{sx - 30} -32 {sx} -34 Z' "
                 f"fill='{['#3fbf6a', '#36b060'][i % 2]}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M40 -26 Q150 -44 260 -30' fill='none' stroke='#8ff0a8' stroke-width='6' stroke-linecap='round' opacity='0.8'/>")
    # caparazón (manchas tipo leopardo)
    g.append(f"<path d='M-70 -10 Q-60 -52 0 -54 Q50 -54 60 -20 Q64 20 40 36 Q-30 44 -60 26 Q-76 12 -70 -10 Z' fill='#5ad070' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for cx, cy in ((-30, -30), (-8, -20), (18, -34), (-40, 6), (10, 8), (32, -6)):
        g.append(f"<circle cx='{cx}' cy='{cy}' r='6' fill='#2a7a4a'/>")
    # patas para andar
    for i in range(3):
        px = -20 + i * 24
        g.append(f"<path d='M{px} 34 l-8 34 l-10 6' fill='none' stroke='{INK}' stroke-width='11' stroke-linecap='round' stroke-linejoin='round'/>"
                 f"<path d='M{px} 34 l-8 34 l-10 6' fill='none' stroke='#ff5a3d' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")
    # antenas y escamas antenales naranjas
    for i, a0 in enumerate((-30, -50)):
        aa = a0 + 6 * math.sin(t * 3 + i)
        g.append(f"<path d='M-72 -30 q-60 {aa * 0.8:.0f} -130 {aa * 1.6:.0f}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='-96' cy='-40' rx='30' ry='12' fill='#ff9a2e' stroke='{INK}' stroke-width='5' transform='rotate(-25 -96 -40)'/>")
    # ojos con pedúnculo (giran)
    for i, (ex, ey) in enumerate(((-66, -70), (-40, -78))):
        ga = 12 * math.sin(t * 1.7 + i * 2)
        g.append(f"<path d='M{ex + 14} -40 L{ex} {ey}' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
                 f"<path d='M{ex + 14} -40 L{ex} {ey}' stroke='#5ad070' stroke-width='7' stroke-linecap='round'/>"
                 f"<g transform='translate({ex},{ey}) rotate({ga:.1f}) scale(1,{parp})'><ellipse rx='13' ry='18' fill='#8a6cff' stroke='{INK}' stroke-width='5'/>"
                 f"<rect x='-13' y='-3' width='26' height='6' fill='#ffe14d'/><circle cx='-3' cy='-8' r='3.5' fill='#fff'/></g>")
    # maza (apéndice raptor): segmento + puño rojo; se estira con el golpe
    k = clamp(golpe)
    a_merus = lerp(70, 0, k)
    a_dact = lerp(-150, -10, k)
    g.append(f"<g transform='translate(-62,10) rotate({180 - a_merus:.1f})'>"
             f"<rect x='0' y='-14' width='78' height='28' rx='13' fill='#ff5a3d' stroke='{INK}' stroke-width='7'/>"
             f"<g transform='translate(76,0) rotate({a_dact:.1f})'>"
             f"<path d='M-6 -16 L60 -14 Q86 -12 86 4 Q84 20 60 18 L-6 16 Z' fill='#e8382f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<circle cx='70' cy='2' r='16' fill='#ff7a5a' stroke='{INK}' stroke-width='6'/></g></g>")
    g.append("</g>")
    return "".join(g)


def caracol(x, y, s, roto=0.0, grieta=0.0):
    """Concha de caracol marino en espiral; roto>0 la parte en trozos que salen volando."""
    if roto <= 0:
        g = (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
             f"<path d='M-70 20 Q-80 -60 0 -70 Q70 -70 72 0 Q74 40 30 44 L-60 44 Z' fill='#f2c48a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M0 0 m-40 0 a40 40 0 1 1 80 0 a28 28 0 1 1 -56 0 a16 16 0 1 1 32 0' fill='none' stroke='#b9824a' stroke-width='8' stroke-linecap='round'/>")
        if grieta > 0:
            g += f"<path d='M-20 -66 L-8 -30 L-26 -10 L-6 20' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round' opacity='{grieta:.2f}'/>"
        return g + "</g>"
    out = []
    for i, (dx, dy, rot) in enumerate(((-1, -1.2, -80), (1.1, -1.4, 90), (-1.4, 0.2, -40), (1.3, 0.1, 60))):
        px = x + dx * 160 * roto; py = y + dy * 120 * roto + 200 * roto * roto
        out.append(f"<g transform='translate({px:.0f},{py:.0f}) rotate({rot * roto:.0f}) scale({s:.2f})' opacity='{1 - seg(roto, 0.7, 1):.2f}'>"
                   f"<path d='M0 0 L40 -10 L30 30 Z' fill='#f2c48a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    return "".join(out)


def medusa_t(x, y, s, t, enc=1.0, ojos=True):
    """Turritopsis: campana transparente con el estómago rojo y una franja de tentáculos finos.
    enc: 1 normal, 0 encogida en una bolita."""
    k = clamp(enc)
    lat = 1 + 0.08 * math.sin(t * 3.2)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"]
    g.append(f"<circle r='{150 * k + 40:.0f}' fill='#bff3ff' opacity='0.18'/>")
    if k > 0.05:
        for i in range(14):
            tx = -88 + i * 13.5
            L = 120 * k
            sw = 14 * math.sin(t * 2.4 + i * 0.7)
            g.append(f"<path d='M{tx * lat * k:.0f} {30 * k:.0f} q{sw:.0f} {L / 2:.0f} {sw * 0.3:.0f} {L:.0f}' fill='none' stroke='#f6e2ea' stroke-width='4' stroke-linecap='round' opacity='0.85'/>")
    rx, ry = 100 * lat * k + 30 * (1 - k), 90 / lat * k + 30 * (1 - k)
    g.append(f"<path d='M{-rx:.0f} {30 * k:.0f} Q{-rx:.0f} {-ry:.0f} 0 {-ry:.0f} Q{rx:.0f} {-ry:.0f} {rx:.0f} {30 * k:.0f} Q0 {14 * k:.0f} {-rx:.0f} {30 * k:.0f} Z' "
             f"fill='#e8f8ff' fill-opacity='0.55' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # estómago rojo en forma de cruz
    g.append(f"<g transform='translate(0,{-20 * k:.0f}) scale({0.6 + 0.4 * k:.2f})'>"
             f"<path d='M0 -36 Q16 -16 36 -10 Q16 0 0 26 Q-16 0 -36 -10 Q-16 -16 0 -36 Z' fill='#e8382f' stroke='#a3201a' stroke-width='5'/>"
             f"<circle r='14' fill='#ff6a4a'/></g>")
    if ojos and k > 0.5:
        parp = 0.15 if (t % 3.3) < 0.12 else 1
        for ex in (-40, 40):
            g.append(f"<g transform='translate({ex},-30) scale(1,{parp})'><circle r='9' fill='{INK}'/><circle cx='-3' cy='-3' r='3' fill='#fff'/></g>")
        g.append(f"<path d='M-50 6 Q-44 12 -38 6 M38 6 Q44 12 50 6' fill='none' stroke='#ff8aa0' stroke-width='5' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def polipo(x, y, s, t, k=1.0, yema=0.0):
    """Pólipo: tallito pegado a la roca con una corona de tentáculos; yema = medusita que brota."""
    if k <= 0:
        return ""
    alto = 150 * k
    sw = 8 * math.sin(t * 1.5 + x)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"]
    g.append(f"<path d='M0 0 Q{sw:.0f} {-alto / 2:.0f} {sw * 1.5:.0f} {-alto:.0f}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
             f"<path d='M0 0 Q{sw:.0f} {-alto / 2:.0f} {sw * 1.5:.0f} {-alto:.0f}' fill='none' stroke='#f4d6c8' stroke-width='12' stroke-linecap='round'/>")
    hx, hy = sw * 1.5, -alto
    for i in range(9):
        a = math.radians(-160 + i * 17.5)
        L = 46 * k
        g.append(f"<path d='M{hx:.0f} {hy:.0f} q{math.cos(a) * L * 0.6:.0f} {math.sin(a) * L * 0.6 - 10:.0f} {math.cos(a) * L:.0f} {math.sin(a) * L:.0f}' fill='none' stroke='#f6e2ea' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='{hx:.0f}' cy='{hy:.0f}' rx='{22 * k:.0f}' ry='{16 * k:.0f}' fill='#ff8a6a' stroke='{INK}' stroke-width='6'/>")
    if yema > 0:
        g.append(f"<g transform='translate({hx + 40:.0f},{hy + 40 - 30 * yema:.0f})'>{medusa_t(0, 0, 0.18 * yema, t, 1, ojos=False)}</g>")
    g.append("</g>")
    return "".join(g)


def mariposa(x, y, s, t, k):
    """k=0 mariposa, k=1 oruga (la metáfora de volver atrás)."""
    out = []
    if k < 1:
        a = 1 - seg(k, 0.3, 0.6)
        b = math.sin(t * 8) * 0.35 + 0.65
        out.append(f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' opacity='{a:.2f}'>"
                   + "".join(f"<g transform='scale({lado * b:.2f},1)'><path d='M0 -6 Q60 -110 120 -60 Q110 -10 0 0 Z' fill='#ff9a2e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                             f"<path d='M0 4 Q90 20 80 80 Q30 90 0 10 Z' fill='#ffd23f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                             f"<circle cx='70' cy='-56' r='12' fill='#fff'/></g>" for lado in (-1, 1))
                   + f"<ellipse rx='12' ry='54' fill='#3b302c' stroke='{INK}' stroke-width='5'/>"
                     f"<path d='M-4 -50 q-14 -30 -26 -34 M4 -50 q14 -30 26 -34' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")
    if k > 0:
        a = seg(k, 0.4, 0.7)
        out.append(f"<g transform='translate({x:.0f},{y + 30:.0f}) scale({s:.2f})' opacity='{a:.2f}'>"
                   + "".join(f"<circle cx='{-80 + i * 32}' cy='{6 * math.sin(t * 6 + i)}' r='{22 if i < 5 else 26}' fill='{['#7ed957', '#5cc84a'][i % 2]}' stroke='{INK}' stroke-width='6'/>" for i in range(6))
                   + f"<circle cx='86' cy='{-6 + 6 * math.sin(t * 6 + 5):.0f}' r='5' fill='{INK}'/></g>")
    return "".join(out)


def flecha_circular(cx, cy, r, k, col="#ffd23f"):
    if k <= 0:
        return ""
    a1 = -math.pi / 2; a2 = a1 - 2 * math.pi * 0.85 * k
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    big = 1 if 0.85 * k > 0.5 else 0
    d = f"M{x1:.0f} {y1:.0f} A{r} {r} 0 {big} 0 {x2:.0f} {y2:.0f}"
    ta = a2 - math.pi / 2
    hx, hy = math.cos(ta) * 30, math.sin(ta) * 30
    px, py = -math.sin(ta) * 22, math.cos(ta) * 22
    return (f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='{col}' stroke-width='12' stroke-linecap='round'/>"
            f"<path d='M{x2 + px:.0f} {y2 + py:.0f} L{x2 + hx:.0f} {y2 + hy:.0f} L{x2 - px:.0f} {y2 - py:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


# ================= capítulo 0: gancho =================
def esc_intro(t, dur, m):
    s = [cielo("#4fb8f5", "#cdefff", "cie0"),
         "<circle cx='1500' cy='300' r='170' fill='#fff3b0' opacity='0.45'/>",
         f"<circle cx='1500' cy='300' r='78' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>"]
    s.append(nubes(t, [(150, 210, 1.2), (800, 150, 1.0), (1650, 420, 0.9), (500, 520, 0.8)], vel=40))
    # la Tierra curva abajo (vuelta al mundo) que gira
    s.append(f"<defs><clipPath id='tie'><circle cx='960' cy='2700' r='1900'/></clipPath></defs>"
             f"<circle cx='960' cy='2700' r='1900' fill='#2e8fe0' stroke='{INK}' stroke-width='{LW}'/>")
    cont = []
    for i in range(6):
        cx = (i * 700 - t * 90) % 4200 - 1100
        cont.append(f"<path d='M{cx:.0f} 860 q80 -70 200 -40 q120 -50 220 10 q90 30 40 90 q-140 60 -300 40 q-160 -20 -160 -100 Z' fill='#5cc84a' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<g clip-path='url(#tie)'>{''.join(cont)}</g>")
    s.append(f"<circle cx='960' cy='2700' r='1920' fill='none' stroke='#bfe9ff' stroke-width='26' opacity='0.5'/>")
    # bandada de vencejos que pasa zumbando desde el fotograma 0
    for i, (f0, y0, sc, v) in enumerate(BANDADA):
        k = (t * 0.22 * v + f0) % 1
        bx = lerp(2100, -200, k)
        by = y0 + 30 * math.sin(t * 3 + i)
        s.append(vencejo(bx, by, sc, t, ang=180 + 8 * math.sin(t * 2 + i), fase=i, ojo=False))
    # un vencejo grande pasa muy cerca al principio
    k0 = seg(t, 0, 2.2)
    if k0 < 1:
        s.append(vencejo(lerp(1650, -400, k0), lerp(420, 560, k0), 1.4, t, ang=185))
    # Rumbo entra girando
    entra = seg(t, 0, 1.6)
    vete = seg(t, dur - 1.4, dur)
    rx = lerp(260, 700, entra) + lerp(0, 1500, vete)
    ry = 560 + 18 * math.sin(t * 2.2) - lerp(0, 200, vete)
    giro = -25 * (1 - entra)
    s.append(rumbo(rx, ry, 1.15, t, ang=giro + 5 * math.sin(t * 1.7) + 10 * vete, guino=(m[2] + 1.0 < t < m[2] + 1.35),
                   mira=(6, -2) if t < 2 else (3, 0)))
    # adelanto de la última parada: burbuja con una medusita que brilla
    ad = seg(t, m[2], m[2] + 0.7) * (1 - seg(t, m[3] - 0.2, m[3] + 0.4))
    if ad > 0:
        s.append(f"<g transform='translate(1300,560) scale({0.4 + 0.6 * ease(ad):.2f})' opacity='{ad:.2f}'>"
                 f"<circle r='180' fill='#0d5a9c' stroke='#fff' stroke-width='14'/><circle r='180' fill='none' stroke='{INK}' stroke-width='6'/>"
                 f"{medusa_t(0, 10, 0.9, t, 1)}</g>")
        s.append(destellos(1300, 560, (t - m[2]) % 1.5 / 1.5, 10, 230))
    return "".join(s)


# ================= capítulo 1: vencejos =================
def esc_vencejos(t, dur, m):
    noche = 0.0
    ciclo = seg(t, m[3] + 0.3, m[3] + 0.6) * (1 - seg(t, m[4] - 0.5, m[4]))
    if ciclo > 0:
        noche = ciclo * (0.5 + 0.5 * math.sin((t - m[3]) * 2.6 - math.pi / 2))
    s = [cielo(mix("#4fb8f5", "#141a4a", noche), mix("#d9f2ff", "#3a3f7a", noche), "cie1")]
    if noche > 0.1:
        for i in range(30):
            s.append(f"<circle cx='{(i * 131) % W}' cy='{(i * 71) % 560 + 60}' r='3' fill='#fff' opacity='{noche:.2f}'/>")
    # sol y luna que se turnan
    if ciclo > 0:
        a = (t - m[3]) * 2.6
        s.append(f"<circle cx='{960 + 800 * math.cos(a + math.pi):.0f}' cy='{900 - 600 * abs(math.sin(a)):.0f}' r='60' fill='#ffe066' stroke='{INK}' stroke-width='7' opacity='{1 - noche:.2f}'/>")
        s.append(f"<circle cx='{960 + 800 * math.cos(a):.0f}' cy='{900 - 600 * abs(math.sin(a)):.0f}' r='48' fill='#f2f2ff' stroke='{INK}' stroke-width='7' opacity='{noche:.2f}'/>")
    else:
        s.append(f"<circle cx='300' cy='380' r='70' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(nubes(t, [(100, 300, 1.0), (900, 250, 0.8), (1500, 600, 1.1), (600, 720, 0.7)], col=mix("#ffffff", "#8a90c0", noche), vel=70))
    # tejados de una ciudad europea abajo (al principio)
    ciudad = 1 - seg(t, m[1], m[2])
    if ciudad > 0:
        tj = []
        for i in range(12):
            bx = i * 170 - (t * 60) % 170
            hh = 120 + (i * 53) % 90
            tj.append(f"<rect x='{bx:.0f}' y='{1080 - hh}' width='150' height='{hh}' fill='#f2d4a8' stroke='{INK}' stroke-width='6'/>"
                      f"<path d='M{bx - 10:.0f} {1080 - hh} L{bx + 75:.0f} {1010 - hh} L{bx + 160:.0f} {1080 - hh} Z' fill='#d9603b' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                      f"<rect x='{bx + 50:.0f}' y='{1100 - hh}' width='40' height='40' fill='#8fd3ff' stroke='{INK}' stroke-width='4'/>")
        s.append(f"<g transform='translate(0,{lerp(0, 300, 1 - ciudad):.0f})'>{''.join(tj)}</g>")
    # bandada al fondo
    for i, (f0, y0, sc, v) in enumerate(BANDADA[:9]):
        k = (t * 0.3 * v + f0) % 1
        s.append(vencejo(lerp(2100, -200, k), y0 * 0.8 + 60 + 25 * math.sin(t * 3 + i), sc * 0.7, t, ang=180 + 10 * math.sin(t * 2 + i), fase=i, ojo=False))
    # protagonista: un vencejo grande en el centro (llega en la frase 1)
    llega = seg(t, m[1] - 0.6, m[1] + 1.2)
    vx = lerp(2200, 1100, llega) + 40 * math.sin(t * 0.9)
    vy = 560 + 40 * math.sin(t * 1.3)
    zoomk = seg(t, m[1], m[1] + 1.5) * (1 - seg(t, m[2] + 2.5, m[3]))
    mo = seg(t, m[2] + 0.8, m[2] + 1.6)
    s.append(vencejo(vx, vy, 1.4 + 0.25 * zoomk, t, ang=180 + 6 * math.sin(t * 1.4), mochila=mo))
    if mo > 0 and mo < 1:
        s.append(destellos(vx + 15, vy, mo, 8, 80))
    # Rumbo vuela al lado
    rx = 470 + 20 * math.sin(t * 0.8); ry = 520 + 22 * math.sin(t * 1.6)
    s.append(rumbo(rx, ry, 0.8, t, ang=-6 + 4 * math.sin(t * 2), mira=(7, 1), guino=(m[5] + 0.6 < t < m[5] + 0.9) if len(m) > 5 else False))
    # 10 lunas: los 10 meses en el aire
    if t > m[3]:
        for i in range(10):
            on = seg(t, m[3] + 0.4 + i * 0.35, m[3] + 0.6 + i * 0.35)
            cx = 645 + i * 70
            s.append(f"<circle cx='{cx}' cy='870' r='{22 + 6 * (on - seg(t, m[3] + 0.6 + i * 0.35, m[3] + 1.0 + i * 0.35)):.0f}' fill='{mix('#3a4a7a', '#ffe066', on)}' stroke='{INK}' stroke-width='6'/>")
    # insectos que caza al vuelo (frase 4)
    if t > m[4] - 0.3:
        for i in range(6):
            ix = vx - 160 - ((t - m[4]) * 220 + i * 140) % 700 + 400
            iy = vy - 60 + 60 * math.sin(t * 4 + i * 2)
            s.append(f"<g transform='translate({ix:.0f},{iy:.0f})'><ellipse rx='8' ry='5' fill='{INK}'/>"
                     f"<ellipse cx='-2' cy='-7' rx='7' ry='4' fill='#e8f6ff' stroke='{INK}' stroke-width='2' opacity='0.9'/></g>")
    # señal de "abajo" al final (cliffhanger)
    if len(m) > 5:
        ab = seg(t, m[5], m[5] + 0.6)
        if ab > 0:
            s.append(f"<g transform='translate(1500,{700 + 40 * math.sin(t * 6):.0f})' opacity='{ab:.2f}'><rect x='-24' y='-60' width='48' height='90' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
                     f"<path d='M-60 26 L60 26 L0 100 Z' fill='#ffd23f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    return "".join(s)


# ================= capítulo 2: rata topo desnuda =================
def tierra_africa(t):
    s = [cielo("#7fd3ff", "#ffe8b8", "cie2"),
         f"<circle cx='1600' cy='120' r='60' fill='#ffe066' stroke='{INK}' stroke-width='7'/>"]
    # acacia
    s.append(f"<path d='M1250 300 L1262 190 L1240 150 M1262 190 L1300 140' fill='none' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
             f"<path d='M1250 300 L1262 190 L1240 150 M1262 190 L1300 140' fill='none' stroke='#7a4f2e' stroke-width='9' stroke-linecap='round'/>"
             f"<ellipse cx='1270' cy='135' rx='150' ry='36' fill='#6aa84f' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<path d='M0 300 L1920 300 L1920 1080 L0 1080 Z' fill='#b07a45' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 300 Q480 288 960 300 T1920 296' fill='none' stroke='#c9a25a' stroke-width='22'/>")
    for i in range(40):
        gx = i * 50 + 10
        s.append(f"<path d='M{gx} 300 l-8 -26 M{gx + 8} 300 l4 -32 M{gx + 16} 300 l10 -22' stroke='#8a9a3a' stroke-width='5' stroke-linecap='round'/>")
    for i, y in enumerate((520, 760, 980)):
        s.append(f"<path d='M0 {y} Q480 {y - 18} 960 {y} T1920 {y}' fill='none' stroke='#9c6a3a' stroke-width='10' opacity='0.6'/>")
    for px, py, pr in PIEDRAS:
        if py > 330:
            s.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='{pr:.0f}' ry='{pr * 0.7:.0f}' fill='#8a5a32' opacity='0.7'/>")
    # túneles
    tun = ("M180 300 Q200 420 300 470 L620 520 Q760 560 900 620 L1700 620 Q1820 620 1920 600 "
           "M900 620 Q960 760 1100 790 L1500 800 M1300 620 Q1350 500 1480 470 L1900 460")
    s.append(f"<path d='{tun}' fill='none' stroke='{INK}' stroke-width='132' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='{tun}' fill='none' stroke='#4a2b17' stroke-width='118' stroke-linecap='round' stroke-linejoin='round'/>")
    s.append(f"<ellipse cx='1600' cy='790' rx='150' ry='80' fill='#4a2b17' stroke='{INK}' stroke-width='7'/>")
    return "".join(s)


def esc_ratas(t, dur, m):
    s = [tierra_africa(t)]
    poco = seg(t, m[2] + 0.5, m[3] + 0.5)
    # burbujas de aire (oxígeno) que se van apagando
    for i in range(14):
        bx = (i * 151 + t * 30) % 1700 + 150
        by = [470, 520, 620, 620, 790, 460][i % 6] + 22 * math.sin(t * 2 + i)
        op = (1 - poco) * 0.8 + 0.0
        if op > 0.02:
            s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{12 + (i % 3) * 4}' fill='#bfe9ff' fill-opacity='0.5' stroke='#fff' stroke-width='3' opacity='{op:.2f}'/>")
    sin_aire = seg(t, m[3], m[3] + 0.6) * (1 - seg(t, m[4] + 2.5, dur))
    s.append(f"<rect width='{W}' height='{H}' fill='#1a1030' opacity='{0.25 * sin_aire:.2f}'/>")
    # colonia de ratas topo (aparecen con la frase 1 y se multiplican con la 2)
    colonia = [(620, 525, 1, 0.0), (1050, 630, -1, 1.3), (1400, 630, 1, 2.1), (1650, 470, -1, 0.7), (1250, 795, 1, 1.8), (1700, 805, -1, 2.6), (840, 590, 1, 3.1)]
    n = 1 + int(round(6 * seg(t, m[2] - 0.2, m[2] + 1.5)))
    calma = seg(t, m[3], m[3] + 0.5) * (1 - seg(t, m[4] + 0.5, m[4] + 1.5))
    for i, (cx, cy, d, f) in enumerate(colonia[:n]):
        ap = seg(t, m[1] - 0.5 if i == 0 else m[2] - 0.2 + i * 0.2, (m[1] + 0.3) if i == 0 else m[2] + i * 0.2 + 0.4)
        if ap <= 0:
            continue
        paso = (t * 40 * d) % 120 - 60 if calma < 0.5 else 0
        s.append(f"<g opacity='{ap:.2f}'>{rata_topo(cx + paso, cy - 40, 0.62 if i else 0.95, t, f, d, feliz=seg(t, m[3] + 2.5, m[3] + 3.5), andar=1 - calma)}</g>")
    # cronómetro de 18 minutos
    s.append(cronometro(1000, 500, t * (1 + 3 * sin_aire), seg(t, m[3], m[3] + 0.5) * (1 - seg(t, m[4] - 0.3, m[4] + 0.2))))
    # chispas de alegría: se recuperan
    s.append(destellos(620, 480, seg(t, m[3] + 2.6, m[3] + 4.2), 10, 200))
    # combustible: fructosa (azúcar) y una hojita, como las plantas
    fr = seg(t, m[4] + 0.2, m[4] + 1.2)
    if fr > 0:
        for i in range(6):
            k = ((t - m[4]) * 0.6 + i / 6) % 1
            fx = lerp(1000, 690, k) + 30 * math.sin(i + t * 3); fy = lerp(380, 500, k)
            s.append(f"<rect x='{fx - 14:.0f}' y='{fy - 14:.0f}' width='28' height='28' rx='5' fill='#fff' stroke='{INK}' stroke-width='5' opacity='{fr * (1 - k):.2f}' transform='rotate({k * 180:.0f} {fx:.0f} {fy:.0f})'/>")
        s.append(f"<g transform='translate(1050,380) scale({ease(fr):.2f})'>"
                 f"<path d='M0 0 Q-60 -40 -30 -110 Q40 -90 30 -20 Z' fill='#5cc84a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M0 0 Q-10 -50 -20 -90' fill='none' stroke='#2f8a3a' stroke-width='5'/>"
                 f"<path d='M0 0 Q50 -20 80 -70 Q20 -80 6 -20' fill='#7ed957' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
        s.append(f"<circle cx='620' cy='490' r='{110 * fr:.0f}' fill='#ffd23f' opacity='{0.25 * fr * (0.7 + 0.3 * math.sin(t * 5)):.2f}'/>")
    # Rumbo baja por el agujero
    baja = seg(t, 0, 3.0)
    rx = lerp(430, 190, seg(t, 0, 1.4)); rx = lerp(rx, 330, seg(t, 1.8, 3.2)); ry = lerp(190, 470, baja) + 10 * math.sin(t * 2)
    s.append(rumbo(rx, ry, 0.55, t, ang=6 * math.sin(t * 1.7), mira=(6, 2)))
    return "".join(s)


# ================= capítulo 3: ardilla ártica =================
def esc_ardilla(t, dur, m):
    noche = 0.6
    s = [cielo("#2c3a78", "#9fb6e0", "cie3")]
    for i in range(3):   # aurora suave
        y0 = 120 + i * 40
        ola = " ".join(f"{x} {y0 + 30 * math.sin(x / 200 + t * 0.6 + i):.0f}" for x in range(0, 1921, 160))
        s.append(f"<path d='M{ola.replace(' ', ' L', 0)}' fill='none' stroke='{['#5affb4', '#7affd9', '#b48aff'][i]}' stroke-width='{40 - i * 8}' stroke-linecap='round' opacity='0.35'/>")
    # nieve que cae
    for x, y, r, v in NIEVE:
        yy = (y + t * v) % 460
        s.append(f"<circle cx='{x + 10 * math.sin(t + x):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#fff' opacity='0.85'/>")
    # abetos nevados
    for i, (ax, ah) in enumerate(((150, 220), (330, 180), (1500, 240), (1700, 190), (1850, 230))):
        s.append(f"<path d='M{ax} {440 - ah} L{ax + 70} 440 L{ax - 70} 440 Z' fill='#2f6b4a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M{ax} {440 - ah} L{ax + 30} {440 - ah * 0.55:.0f} L{ax - 30} {440 - ah * 0.55:.0f} Z' fill='#fff'/>")
    # nieve y suelo helado en corte
    s.append(f"<path d='M0 430 Q480 400 960 425 T1920 420 L1920 1080 L0 1080 Z' fill='#f4f9ff' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 520 Q480 505 960 520 T1920 515 L1920 1080 L0 1080 Z' fill='#7b6a5c' stroke='{INK}' stroke-width='7'/>")
    for px, py, pr in PIEDRAS:
        if py > 560:
            s.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='{pr:.0f}' ry='{pr * 0.7:.0f}' fill='#645446' opacity='0.8'/>")
    # túnel y madriguera
    s.append(f"<path d='M420 520 Q440 640 600 700 L760 720' fill='none' stroke='{INK}' stroke-width='112' stroke-linecap='round'/>"
             f"<path d='M420 520 Q440 640 600 700 L760 720' fill='none' stroke='#4a3a30' stroke-width='98' stroke-linecap='round'/>")
    frio = seg(t, m[2], m[3] + 1.5) * (1 - 0.8 * seg(t, m[4], m[4] + 0.8) * (1 - seg(t, m[4] + 3.0, m[4] + 4.5)))
    s.append(f"<ellipse cx='1000' cy='740' rx='280' ry='170' fill='{mix('#4a3a30', '#3a4a66', frio)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M740 830 Q1000 900 1260 830 L1250 870 Q1000 930 750 870 Z' fill='#d9b56a' stroke='{INK}' stroke-width='6'/>")
    for i in range(14):
        hx = 760 + i * 36
        s.append(f"<path d='M{hx} 860 l{10 + i % 3 * 4} -30' stroke='#c29a4a' stroke-width='5' stroke-linecap='round'/>")
    # escarcha alrededor
    if frio > 0:
        for i in range(12):
            a = i / 12 * 2 * math.pi
            fx, fy = 1000 + 250 * math.cos(a), 740 + 150 * math.sin(a)
            e = 16
            s.append(f"<g transform='translate({fx:.0f},{fy:.0f}) rotate({t * 20 + i * 30:.0f})' opacity='{frio * (0.6 + 0.4 * math.sin(t * 3 + i)):.2f}'>"
                     f"<path d='M-{e} 0 L{e} 0 M0 -{e} L0 {e} M-11 -11 L11 11 M-11 11 L11 -11' stroke='#e8f6ff' stroke-width='4' stroke-linecap='round'/></g>")
    aparece = seg(t, m[1] - 0.5, m[1] + 0.8)
    tir = seg(t, m[4] + 0.2, m[4] + 0.6) * (1 - seg(t, m[4] + 2.4, m[4] + 3.0))
    s.append(f"<g opacity='{aparece:.2f}'>{ardilla(1000, 730, 0.95, t, tirita=tir, frio=frio)}</g>")
    if tir > 0:
        s.append(f"<ellipse cx='1000' cy='730' rx='{200 + 20 * math.sin(t * 8):.0f}' ry='150' fill='#ff9a3d' opacity='{0.22 * tir:.2f}'/>")
    # zzz
    for i in range(3):
        k = ((t * 0.4 + i / 3) % 1)
        s.append(f"<path d='M{1150 + k * 60:.0f} {600 - k * 120:.0f} l24 0 l-24 24 l24 0' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round' stroke-linejoin='round' opacity='{aparece * (1 - k) * (1 - tir):.2f}'/>")
    # termómetro con cero
    op = seg(t, m[2] - 0.3, m[2] + 0.4) * (1 - seg(t, dur - 1.6, dur - 0.8))
    if op > 0:
        temp = lerp(37, -2.9, seg(t, m[2] + 0.3, m[3] + 1.2))
        temp = lerp(temp, 36, seg(t, m[4] + 0.3, m[4] + 1.5) * (1 - seg(t, m[4] + 3.0, m[4] + 4.5)))
        y0, y1 = 860, 400        # -10 °C .. 40 °C
        yt = lerp(y0, y1, (temp + 10) / 50)
        yc = lerp(y0, y1, 10 / 50)
        col = mix("#3a8dff", "#e8382f", clamp((temp + 3) / 20))
        s.append(f"<g opacity='{op:.2f}'>"
                 f"<rect x='1474' y='{y1 - 20}' width='52' height='{y0 - y1 + 40}' rx='26' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<rect x='1488' y='{yt:.0f}' width='24' height='{y0 + 30 - yt:.0f}' fill='{col}'/>"
                 f"<circle cx='1500' cy='{y0 + 40}' r='46' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<line x1='1440' y1='{yc:.0f}' x2='1560' y2='{yc:.0f}' stroke='{INK}' stroke-width='7'/>"
                 + "".join(f"<line x1='1526' y1='{lerp(y0, y1, i / 5):.0f}' x2='1506' y2='{lerp(y0, y1, i / 5):.0f}' stroke='{INK}' stroke-width='4'/>" for i in range(6))
                 + "</g>")
        if temp < 0:
            s.append(destellos(1500, yt, (t - m[3]) % 1.6 / 1.6, 8, 90, "#cfefff"))
    # Rumbo en la entrada del túnel, tiritando de frío
    baja = seg(t, 0, 2.5)
    rx = lerp(560, 470, baja); ry = lerp(180, 610, baja) + 8 * math.sin(t * 2)
    s.append(rumbo(rx, ry, 0.55, t, ang=4 * math.sin(t * 1.5), mira=(7, 3), frio=seg(t, 1.5, 2.5) * (1 - 0.6 * tir)))
    # cliffhanger: cambio a cálido
    if len(m) > 5:
        cal = seg(t, m[5] + 0.3, dur)
        s.append(f"<rect width='{W}' height='{H}' fill='#ffb347' opacity='{0.3 * cal:.2f}'/>")
    return "".join(s)


# ================= capítulo 4: gamba mantis =================
def arrecife(t):
    s = ["<defs><linearGradient id='mar4' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3fc4f0'/>"
         "<stop offset='1' stop-color='#0b6aa8'/></linearGradient>"
         "<linearGradient id='ray4' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='0.35'/>"
         "<stop offset='1' stop-color='#fff' stop-opacity='0'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#mar4)'/>"]
    for i in range(6):
        x = 150 + i * 330 + 60 * math.sin(t * 0.4 + i)
        s.append(f"<path d='M{x - 40:.0f} 0 L{x + 60:.0f} 0 L{x + 260:.0f} {H} L{x + 60:.0f} {H} Z' fill='url(#ray4)' opacity='{0.5 + 0.3 * math.sin(t * 0.7 + i * 2):.2f}'/>")
    for x, y, r, v in PART:
        s.append(f"<circle cx='{x:.0f}' cy='{(y - t * v) % H:.0f}' r='{r:.1f}' fill='#e8f6ff' opacity='0.35'/>")
    # corales
    for cx, base, col, al in ((140, 860, "#ff6a8a", 260), (1700, 860, "#ffb347", 300), (1860, 870, "#c77dff", 200), (330, 870, "#ffd23f", 170)):
        sw = 6 * math.sin(t + cx)
        ram = (f"M{cx} {base} L{cx} {base - al} M{cx} {base - al * 0.4:.0f} L{cx - 60 + sw:.0f} {base - al * 0.8:.0f} "
               f"M{cx} {base - al * 0.55:.0f} L{cx + 70 + sw:.0f} {base - al * 0.95:.0f} M{cx - 30 + sw / 2:.0f} {base - al * 0.6:.0f} L{cx - 80 + sw:.0f} {base - al * 0.55:.0f}")
        s.append(f"<path d='{ram}' fill='none' stroke='{INK}' stroke-width='40' stroke-linecap='round'/>"
                 f"<path d='{ram}' fill='none' stroke='{col}' stroke-width='28' stroke-linecap='round'/>")
    for cx, cy, r, col in ((560, 860, 70, "#ff8a3d"), (1500, 870, 90, "#7ed957")):
        s.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{r}' ry='{r * 0.7:.0f}' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
                 + "".join(f"<path d='M{cx - r * 0.6 + i * r * 0.3:.0f} {cy - r * 0.4:.0f} q{r * 0.15:.0f} {-r * 0.2:.0f} {r * 0.3:.0f} 0' fill='none' stroke='{mix(col, '#000000', 0.25)}' stroke-width='5'/>" for i in range(5)))
    s.append(f"<path d='M0 860 Q240 840 480 856 T960 850 T1440 862 T1920 852 L1920 1080 L0 1080 Z' fill='#f2dca0' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 960 Q300 940 640 955 T1280 948 T1920 958 L1920 1080 L0 1080 Z' fill='#e4c886'/>")
    # peces de colores
    for i in range(5):
        px = (i * 420 + t * (60 + i * 15)) % 2300 - 200
        py = 380 + i * 70 + 20 * math.sin(t * 1.5 + i)
        col = ["#ffd23f", "#ff6a8a", "#3a8dff", "#ff9a2e", "#5affb4"][i]
        c = 10 * math.sin(t * 9 + i)
        s.append(f"<g transform='translate({px:.0f},{py:.0f}) scale(0.45)'>"
                 f"<path d='M-70 0 L-120 {-40 + c:.0f} L-112 0 L-120 {40 + c:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>"
                 f"<ellipse rx='80' ry='42' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<path d='M-10 -36 Q8 0 -10 36' fill='none' stroke='#fff' stroke-width='12'/>"
                 f"<circle cx='45' cy='-10' r='13' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='49' cy='-10' r='6' fill='{INK}'/></g>")
    return "".join(s)


def esc_mantis(t, dur, m):
    s = [arrecife(t)]
    # golpes: el 1.º agrieta la concha (frase 3), el 2.º la rompe (frase 4)
    g1, g2 = m[3] + 0.9, m[4] + 2.2
    def golpe(tg):
        if t < tg - 0.08: return 0.0
        if t < tg: return (t - tg + 0.08) / 0.08
        return 1 - seg(t, tg + 0.25, tg + 0.7)
    gk = max(golpe(g1), golpe(g2))
    asoma = seg(t, m[1] - 0.4, m[1] + 1.2)
    gx = lerp(1550, 1160, asoma); gy = 770
    sh = 6 * math.sin(t * 80) * max(0, gk - 0.6) * 2
    s.append(gamba_mantis(gx + sh, gy, 1.6, t, golpe=gk))
    # concha
    cx, cy = 770, 806
    roto = seg(t, g2 + 0.02, g2 + 1.1)
    s.append(caracol(cx, cy, 0.9, roto=roto, grieta=seg(t, g1, g1 + 0.1)))
    # el impacto: destello, burbujas que estallan, líneas de velocidad
    for tg in (g1, g2):
        k = seg(t, tg, tg + 0.9)
        if 0 < k < 1:
            s.append(f"<circle cx='{cx + 40}' cy='{cy - 20}' r='{40 + 200 * k:.0f}' fill='none' stroke='#fff' stroke-width='{14 * (1 - k):.1f}' opacity='{1 - k:.2f}'/>")
            s.append(f"<path transform='translate({cx + 60},{cy - 30}) scale({1 + k:.2f})' d='M0 -60 L16 -16 L60 0 L16 16 L0 60 L-16 16 L-60 0 L-16 -16 Z' fill='#fff6a8' stroke='{INK}' stroke-width='5' opacity='{1 - k:.2f}'/>")
            for i in range(10):
                a = i / 10 * 2 * math.pi
                s.append(f"<circle cx='{cx + 60 + math.cos(a) * 150 * k:.0f}' cy='{cy - 30 + math.sin(a) * 110 * k:.0f}' r='{14 * (1 - k) + 4:.0f}' fill='#d8f3ff' fill-opacity='0.4' stroke='#fff' stroke-width='3' opacity='{1 - k:.2f}'/>")
        if tg - 0.1 < t < tg + 0.25:
            for i in range(4):
                s.append(f"<path d='M{cx + 150 + i * 30} {cy - 70 + i * 30} l110 {-10 + i * 6}' stroke='#fff' stroke-width='8' stroke-linecap='round' opacity='0.8'/>")
    s.append(destellos(cx + 40, cy - 30, seg(t, g2, g2 + 1.6), 12, 260))
    # mazas destacadas (frase 2): brillo alrededor del puño
    md = seg(t, m[2], m[2] + 0.4) * (1 - seg(t, m[3] - 0.2, m[3]))
    if md > 0:
        s.append(f"<circle cx='{gx - 125:.0f}' cy='{gy - 30:.0f}' r='{80 + 8 * math.sin(t * 6):.0f}' fill='none' stroke='#ffd23f' stroke-width='10' stroke-dasharray='22 14' opacity='{md:.2f}'/>")
    # Rumbo bajo el agua
    entra = seg(t, 0, 2.4)
    rx = lerp(-150, 380, entra); ry = lerp(200, 480, entra) + 14 * math.sin(t * 1.4)
    susto = (g1 < t < g1 + 0.8) or (g2 < t < g2 + 0.8)
    s.append(rumbo(rx - (20 if susto else 0), ry, 0.7, t, ang=6 * math.sin(t), mira=(6, 4), agua=True, guino=False))
    s.append(burbujas(t, rx, ry - 90, 6, 260, 0.8))
    return "".join(s)


# ================= capítulo 5: medusa inmortal =================
def esc_medusa(t, dur, m):
    s = ["<defs><linearGradient id='mar5' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a9fd8'/>"
         "<stop offset='1' stop-color='#0a3f78'/></linearGradient>"
         "<clipPath id='lupa'><circle cx='1080' cy='590' r='300'/></clipPath></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#mar5)'/>"]
    for x, y, r, v in PART:
        s.append(f"<circle cx='{x:.0f}' cy='{(y - t * v) % H:.0f}' r='{r:.1f}' fill='#e8f6ff' opacity='0.3'/>")
    # roca y posidonia
    s.append(f"<path d='M0 900 Q300 860 640 890 T1280 880 T1920 895 L1920 1080 L0 1080 Z' fill='#c9b48a' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(22):
        px = 30 + i * 90
        sw = 20 * math.sin(t * 1.2 + i)
        s.append(f"<path d='M{px} 900 Q{px + sw / 2:.0f} 800 {px + sw:.0f} {720 + (i % 3) * 30}' fill='none' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
                 f"<path d='M{px} 900 Q{px + sw / 2:.0f} 800 {px + sw:.0f} {720 + (i % 3) * 30}' fill='none' stroke='#4fae5a' stroke-width='10' stroke-linecap='round'/>")
    # medusita diminuta (tamaño real) al principio
    lupa = seg(t, m[1] - 0.3, m[1] + 0.8)
    if lupa < 1:
        mx0, my0 = 1080 + 30 * math.sin(t), 590 + 20 * math.sin(t * 1.3)
        s.append(f"<g opacity='{1 - lupa:.2f}'>{medusa_t(mx0, my0, 0.12, t, 1, ojos=False)}</g>")
        s.append(destellos(mx0, my0, (t % 1.4) / 1.4, 8, 70, '#ffffff'))
    # la lupa de Rumbo
    if lupa > 0:
        sc = 0.3 + 0.7 * ease(lupa)
        dentro = ["<rect x='780' y='290' width='600' height='600' fill='#0d5a9c'/>"]
        for i in range(10):
            dentro.append(f"<circle cx='{800 + (i * 97 + t * 20) % 560:.0f}' cy='{300 + (i * 61 - t * 25) % 580:.0f}' r='5' fill='#e8f6ff' opacity='0.4'/>")
        dentro.append(f"<path d='M780 820 Q900 790 1080 810 T1380 800 L1380 890 L780 890 Z' fill='#8a7a6a' stroke='{INK}' stroke-width='7'/>")
        # ciclo: pólipo (frase 2) -> medusa adulta; frase 3: encoge, baja y vuelve a ser pólipo
        p2 = seg(t, m[2] - 0.2, m[2] + 0.8) * (1 - seg(t, m[3] - 0.6, m[3] - 0.1))
        enc = 1 - seg(t, m[3] + 0.4, m[3] + 1.8)
        baja = seg(t, m[3] + 1.4, m[3] + 2.6)
        nace = seg(t, m[3] + 2.5, m[3] + 3.6)
        brota = seg(t, m[5] - 0.2, m[5] + 2.0) if len(m) > 5 else 0
        mx = lerp(1080, 1080, baja); my = lerp(560, 790, baja) + 20 * math.sin(t * 1.6) * (1 - baja)
        if p2 > 0:
            dentro.append(f"<g opacity='{p2:.2f}'>{polipo(930, 815, 0.9, t, 1, yema=seg(t, m[2] + 0.5, m[2] + 2.0))}{polipo(1230, 812, 0.8, t, 1)}</g>")
        if nace < 1:
            dentro.append(f"<g opacity='{1 - nace:.2f}'>{medusa_t(mx, my, 1.15 * (0.6 + 0.4 * enc), t, enc)}</g>")
        if nace > 0:
            dentro.append(polipo(1060, 815, 1.0, t, nace, yema=0))
            dentro.append(polipo(1180, 815, 0.8, t, seg(t, m[3] + 3.0, m[3] + 4.0)))
            dentro.append(polipo(940, 815, 0.75, t, seg(t, m[3] + 3.4, m[3] + 4.4)))
        if brota > 0:
            for i, (bx, f) in enumerate(((1060, 0.0), (1180, 0.33), (940, 0.66))):
                k = ((t - m[5]) * 0.35 + f) % 1
                dentro.append(medusa_t(bx + 40 * math.sin(t + i), lerp(640, 330, k), 0.35, t, 1, ojos=False).replace("<g ", f"<g opacity='{brota * min(1, (1 - k) * 4):.2f}' ", 1))
        s.append(f"<g transform='translate(1080,630) scale({sc * 0.9:.3f}) translate(-1080,-590)'>"
                 f"<g clip-path='url(#lupa)'>{''.join(dentro)}</g>"
                 f"<circle cx='1080' cy='590' r='300' fill='none' stroke='{INK}' stroke-width='34'/>"
                 f"<circle cx='1080' cy='590' r='300' fill='none' stroke='#f2b632' stroke-width='20'/>"
                 f"<path d='M880 410 A270 270 0 0 1 1060 320' fill='none' stroke='#fff' stroke-width='14' stroke-linecap='round' opacity='0.6'/></g>")
        # gran momento: flecha de "vuelta atrás"
        fl = seg(t, m[3] + 0.3, m[3] + 2.4) * (1 - seg(t, m[4] - 0.3, m[4] + 0.3))
        if fl > 0:
            s.append(f"<g opacity='{min(1, fl * 3):.2f}'>{flecha_circular(1080, 630, 330, fl)}</g>")
        s.append(destellos(1080, 720, seg(t, m[3] + 2.6, m[3] + 4.2), 12, 300))
        if len(m) > 5:
            s.append(destellos(1080, 630, (t - m[5]) % 1.8 / 1.8 if t > m[5] else 0, 14, 380, "#ffffff"))
    # mariposa que vuelve a ser oruga (frase 4)
    mar = seg(t, m[4] - 0.2, m[4] + 0.4) * (1 - seg(t, m[5] - 0.5, m[5])) if len(m) > 5 else 0
    if mar > 0:
        s.append(f"<g opacity='{mar:.2f}'><circle cx='470' cy='560' r='170' fill='#bfe9ff' stroke='{INK}' stroke-width='8'/>"
                 f"{mariposa(470, 545, 0.95, t, seg(t, m[4] + 1.0, m[4] + 2.4))}</g>")
    # Rumbo sostiene la lupa (a la izquierda al principio, luego a la derecha)
    rx = 400 + 20 * math.sin(t * 0.8) if mar <= 0 else lerp(400, 1560, mar)
    ry = 520 + 16 * math.sin(t * 1.4)
    if mar > 0:
        rx = lerp(400, 1560, mar)
    s.append(rumbo(rx, ry, 0.62, t, ang=5 * math.sin(t), mira=(8, 2) if rx < 900 else (-8, 2), agua=True, guino=(len(m) > 5 and m[5] + 1.5 < t < m[5] + 1.85)))
    s.append(burbujas(t, rx, ry - 90, 5, 240, 0.8))
    return "".join(s)


# ================= despedida =================
def esc_final(t, dur, m):
    sube = seg(t, 0, 3.5)
    s = ["<defs><linearGradient id='atar' x1='0' y1='0' x2='0' y2='1'>"
         f"<stop offset='0' stop-color='{mix('#2a9fd8', '#ff8a6b', sube)}'/><stop offset='1' stop-color='{mix('#0a3f78', '#ffe0a8', sube)}'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#atar)'/>",
         f"<circle cx='1720' cy='{lerp(900, 680, sube):.0f}' r='110' fill='#ffd166' stroke='{INK}' stroke-width='{LW}' opacity='{sube:.2f}'/>"]
    s.append(nubes(t, [(200, 200, 1.0), (1500, 150, 0.9), (1100, 260, 0.7)], col="#fff4ea", vel=16))
    # colinas y mar
    s.append(f"<path d='M0 700 Q300 620 640 680 T1280 660 T1920 690 L1920 1080 L0 1080 Z' fill='#5cae4a' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 820 Q400 780 900 815 T1920 800 L1920 1080 L0 1080 Z' fill='#4a9a3c' stroke='{INK}' stroke-width='7'/>")
    # vencejos al atardecer
    for i, (f0, y0, sc, v) in enumerate(BANDADA[:8]):
        k = (t * 0.18 * v + f0) % 1
        s.append(vencejo(lerp(2100, -200, k), 180 + (y0 % 300) * 0.7 + 20 * math.sin(t * 3 + i), sc * 0.55, t, ang=180, fase=i, ojo=False))
    rx = lerp(560, 430, seg(t, m[1] - 0.5, m[1] + 1.0))
    ry = lerp(1150, 520, sube) + 14 * math.sin(t * 2)
    s.append(rumbo(rx, ry, 1.0, t, ang=6 * math.sin(t * 1.6), guino=(m[3] + 0.3 < t < m[3] + 0.7), mira=(7, -2)))
    ap = seg(t, m[1] - 0.2, m[1] + 0.6)
    pulsa = m[1] + 2.4
    hecho = t > pulsa
    camp = seg(t, m[1] + 3.6, m[1] + 4.1)
    if ap > 0:
        late = 1 + 0.05 * math.sin(t * 6) if not hecho else 1 + 0.12 * math.exp(-(t - pulsa) * 5) * math.sin((t - pulsa) * 30)
        esc_ = (0.5 + 0.5 * ease(ap)) * late
        col = "#e62117" if not hecho else "#8a8f96"
        txt = "SUSCRÍBETE" if not hecho else "SUSCRITO"
        s.append(f"<g transform='translate(1180,450) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='450' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, 450, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, 450, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(950, 465, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 470, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, 450, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Un pájaro que pasa 10 meses volando?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que hay un pájaro que pasa diez meses volando sin aterrizar?",
                "Hoy buscamos con Rumbo, nuestra brújula voladora, los animales más extremos del mundo.",
                "Y la última parada te dejará con la boca abierta: ¡un animal que vuelve a ser joven!",
                "Suscríbete y… ¡despegamos!"]},
    {"titulo": "1. El pájaro que no aterriza", "escena": esc_vencejos, "tarjeta": "CAPÍTULO 1 · 10 MESES EN EL AIRE",
     "frases": ["Primera parada: el cielo de Europa. ¡Mira cuántos pájaros pasan zumbando!",
                "Son vencejos: tienen las alas largas como una media luna y unas patitas tan cortas que casi nunca se posan.",
                "Unos científicos suecos les pusieron mochilas diminutas para seguir su viaje.",
                "Y descubrieron algo increíble: algunos pasaron diez meses volando sin parar, de Europa a África y vuelta.",
                "Comen insectos en pleno vuelo. ¡El cielo es su casa!",
                "Pero nuestra siguiente parada está justo al revés: bajo tierra."],
     "grandes": {3: "10 MESES"}},
    {"titulo": "2. La rata que aguanta sin oxígeno", "escena": esc_ratas, "tarjeta": "CAPÍTULO 2 · SIN AIRE",
     "frases": ["Rumbo se mete por un agujero en la tierra de África oriental.",
                "En estos túneles oscuros viven las ratas topo desnudas: sin pelo, arrugadas y con unos dientes enormes.",
                "Viven apretujadas, a veces cientos en la misma colonia, y aquí abajo casi no hay oxígeno.",
                "En un laboratorio aguantaron dieciocho minutos sin nada de oxígeno… ¡y se recuperaron como si nada!",
                "¿Su truco? Su cuerpo cambia de combustible y quema un azúcar, la fructosa, como hacen las plantas."],
     "grandes": {3: "18 MINUTOS"}},
    {"titulo": "3. La ardilla bajo cero", "escena": esc_ardilla, "tarjeta": "CAPÍTULO 3 · BAJO CERO",
     "frases": ["Salimos de los túneles y volamos hasta Alaska. ¡Qué frío! Todo está cubierto de nieve.",
                "Bajo la nieve, hecha una bola en su madriguera, duerme una ardilla ártica.",
                "Hiberna hasta ocho meses, y su cuerpo se enfría más que el de ningún otro mamífero.",
                "¡Baja hasta casi tres grados bajo cero, y aun así no se congela!",
                "Cada pocas semanas tirita para calentarse un rato… y vuelve a dormirse.",
                "Pero ahora vamos a un mar calentito, donde vive el boxeador más rápido del océano."],
     "grandes": {3: "-2,9 °C"}},
    {"titulo": "4. El puñetazo más rápido del mar", "escena": esc_mantis, "tarjeta": "CAPÍTULO 4 · EL PUÑETAZO RÉCORD",
     "frases": ["Rumbo se zambulle en un arrecife de coral. ¡Cuántos colores!",
                "Entre las rocas asoma la gamba mantis, con los colores del arcoíris y unos ojos que giran como periscopios.",
                "Delante lleva dos mazas plegadas, como dos puños de boxeador.",
                "Y cuando golpea, lo hace a unos ochenta kilómetros por hora: ¡uno de los golpes más rápidos del mundo animal!",
                "Es tan rápido que el agua forma burbujas que estallan, y así rompe la concha de un caracol."],
     "grandes": {3: "80 km/h"}, "extra": 1.0},
    {"titulo": "5. La medusa que vuelve a ser joven", "escena": esc_medusa, "tarjeta": "CAPÍTULO 5 · LA MEDUSA INMORTAL",
     "frases": ["Última parada: el mar Mediterráneo. Rumbo busca algo muy, muy pequeño.",
                "Es una medusa transparente con el centro rojo, más pequeña que la uña de tu dedo.",
                "Las medusas nacen de pólipos, unas cositas pegadas a las rocas, como plantitas diminutas.",
                "Pero cuando esta medusa se hace mayor o se pone enferma… ¡vuelve a convertirse en pólipo!",
                "Es como si una mariposa pudiera volver a ser oruga y empezar su vida otra vez.",
                "Por eso la llaman la medusa inmortal: ¡puede volver a ser joven una y otra vez!"],
     "grandes": {3: "¡OTRA VEZ JOVEN!", 5: "INMORTAL"}, "extra": 1.0},
    {"titulo": "Suscríbete para más aventuras", "escena": esc_final,
     "frases": ["Y así termina nuestra vuelta al mundo de los animales más extremos.",
                "Si has alucinado con alguno, ayúdanos con un gesto muy pequeño: suscríbete al canal y activa la campanita.",
                "Así no te perderás ninguna aventura: cada día, una historia nueva llena de curiosidades.",
                "Y cuéntanos en los comentarios cuál te ha sorprendido más.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
