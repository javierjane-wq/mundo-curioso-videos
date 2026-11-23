"""Episodio: "De polo a polo" con Copo, un pequeño dirigible explorador original.

Datos (verificados el 23-11-2026):
- El charrán ártico vuela cada año del Ártico a la Antártida y vuelta: más de 70.000 km (de media 70.900 km);
  en toda su vida recorre el equivalente a ir a la Luna y volver tres veces (Egevang et al., PNAS 2010;
  phys.org «Arctic terns confirmed to have the longest animal migration in the world»). Al ir de un verano
  polar al otro, vive dos veranos cada año.
- En el Polo Norte no hay tierra: está en medio del océano Ártico, sobre hielo marino de unos 2-3 m de grosor
  que flota sobre un mar de más de 4.000 m de profundidad (National Geographic Education «North Pole»).
- El pingüino emperador macho incuba el huevo sobre las patas, bajo un pliegue de piel de la barriga, en pleno
  invierno antártico: tarda 65-75 días en eclosionar, con temperaturas muy por debajo de -35 °C; cuando nace
  el polluelo, el padre lleva unos 4 meses sin comer y ha perdido casi la mitad de su peso (Australian
  Antarctic Division «Emperor penguin breeding cycle»).
- La temperatura más baja medida por una estación: -89,2 °C en la base Vostok (Antártida), el 21 de julio de
  1983 (Organización Meteorológica Mundial, archivo de extremos); los satélites han detectado hasta -98 °C en
  pequeñas hondonadas de la meseta antártica oriental (Scambos et al. 2018, AGU «Coldest place on Earth is
  colder than scientists thought»).
- El hielo de la Antártida mide casi 4,9 km en su punto más grueso y, si se derritiera entero, el nivel del mar
  subiría unos 58 m (NSIDC «Ice sheet quick facts»). El Everest mide 8.849 m.
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-23-historia"
TITULO = "De polo a polo"
VOZ = "em_alex"
VELOCIDAD = 0.95
MUSICA = 23

W, H = 1920, 1080
rng = np.random.default_rng(23)
NIEVE = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2.5, 6), rng.uniform(30, 90), rng.uniform(0, 6.3)) for _ in range(90)]
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, 620), rng.uniform(1.5, 3.8), rng.uniform(0, 6.3)) for _ in range(90)]
RACHAS = [(rng.uniform(0, 1), rng.uniform(150, 950), rng.uniform(0.7, 1.4)) for _ in range(34)]


# ================= piezas comunes =================
def cielo(top, bot, id_="cie"):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def estrellas(t, op=1.0):
    return "".join(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{op * (0.55 + 0.45 * math.sin(t * 2.2 + f)):.2f}'/>"
                   for x, y, r, f in ESTRELLAS)


def aurora(t, op=1.0, base=330, cols=("#5cffb0", "#7af0ff", "#b98cff")):
    """Cintas de aurora polar que ondulan."""
    s = []
    for i, c in enumerate(cols):
        gid = f"aur{i}"
        s.append(f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{c}' stop-opacity='0'/>"
                 f"<stop offset='0.75' stop-color='{c}' stop-opacity='0.55'/><stop offset='1' stop-color='{c}' stop-opacity='0.05'/></linearGradient></defs>")
        b = base + i * 55
        arriba, abajo = [], []
        for x in range(-60, 2001, 80):
            yb = b + 45 * math.sin(x / 260 + t * 0.6 + i * 1.7) + 18 * math.sin(x / 90 + t * 1.3 + i)
            arriba.append(f"{x} {yb - 190 - 40 * math.sin(x / 330 + t * 0.4 + i):.0f}")
            abajo.append(f"{x} {yb:.0f}")
        pts = "M" + " L".join(arriba) + " L" + " L".join(reversed(abajo)) + " Z"
        s.append(f"<path d='{pts}' fill='url(#{gid})' opacity='{op * (0.75 + 0.25 * math.sin(t * 0.9 + i * 2)):.2f}'/>")
    return "".join(s)


def nieve(t, op=0.9, viento=0.0, tam=1.0):
    s = []
    for x, y, r, v, f in NIEVE:
        yy = (y + t * v * (1 + viento * 0.5)) % (H + 20) - 10
        xx = (x + 25 * math.sin(t * 0.8 + f) + t * viento * 260) % (W + 40) - 20
        s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{r * tam:.1f}' fill='#fff' opacity='{op:.2f}'/>")
    return "".join(s)


def rachas(t, k):
    """Rachas de viento con nieve (tormenta)."""
    if k <= 0:
        return ""
    s = []
    for u, y, v in RACHAS:
        x = ((u + t * 0.9 * v) % 1.2) * (W + 600) - 400
        s.append(f"<path d='M{x:.0f} {y:.0f} q60 -10 120 0 t120 0' fill='none' stroke='#eaf6ff' stroke-width='5' stroke-linecap='round' opacity='{0.5 * k:.2f}'/>")
    return "".join(s)


def suelo(y0, t, col="#f4fbff", sombra="#cfe6f5", amp=18):
    ola = "".join(f"Q{i * 240 + 120} {y0 - amp * (1 if i % 2 else -0.6):.0f} {i * 240 + 240} {y0:.0f} " for i in range(9))
    ola2 = "".join(f"Q{i * 300 + 150} {y0 + 70 - amp * 0.8 * (1 if i % 2 else -0.5):.0f} {i * 300 + 300} {y0 + 70:.0f} " for i in range(7))
    return (f"<path d='M-20 {y0} {ola} L1940 1100 L-20 1100 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-20 {y0 + 70} {ola2} L1940 1100 L-20 1100 Z' fill='{sombra}' opacity='0.7'/>")


def iceberg(x, y, s, t, col="#eef9ff"):
    b = 6 * math.sin(t * 1.2 + x)
    return (f"<g transform='translate({x:.0f},{y + b:.0f}) scale({s:.2f})'>"
            f"<path d='M-160 0 L-120 -110 L-60 -150 L-10 -230 L50 -140 L110 -120 L170 0 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-10 -230 L10 -120 L-40 0 L-120 0 L-60 -150 Z' fill='#cbe9fb'/>"
            f"<path d='M50 -140 L60 -60 L110 0 L170 0 L110 -120 Z' fill='#b4dcf5'/>"
            f"<path d='M-160 0 L-120 -110 L-60 -150 L-10 -230 L50 -140 L110 -120 L170 0 Z' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")


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


def copo(x, y, s, t, ang=0.0, guino=False, frio=0.0, mira=0.0, susto=0.0):
    """Copo: dirigible rojo coral con franja blanca, aletas turquesa, góndola amarilla con hélice
    y dos ojos grandes en la parte delantera del globo. Mira hacia la derecha (+x)."""
    parp = 0.12 if ((t + 0.4) % 3.6) < 0.13 or guino else 1.0
    tb = frio * 3.5 * math.sin(t * 55)
    hel = abs(math.sin(t * 20))
    cuerpo = mix("#ff5a5f", "#c8a7d8", 0.35 * frio)
    g = [f"<g transform='translate({x + tb:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='215' rx='150' ry='14' fill='#000' opacity='0.0'/>")
    g.append(f"<path d='M-70 78 L-50 128 M70 78 L50 128 M0 92 L0 128' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-104' y='148' width='30' height='10' fill='#9aa3ad' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<ellipse cx='-110' cy='153' rx='9' ry='{6 + 34 * hel:.0f}' fill='#e6ebf0' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<rect x='-78' y='124' width='156' height='62' rx='22' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>")
    for wx in (-40, 0, 40):
        g.append(f"<circle cx='{wx}' cy='154' r='12' fill='#bfe9ff' stroke='{INK}' stroke-width='5'/>")
    for sy in (-1, 1):
        g.append(f"<path d='M-150 {sy * 40} L-232 {sy * 120} L-256 {sy * 112} L-208 {sy * 8} Z' fill='#2ec4b6' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M-190 -12 L-266 -10 L-266 10 L-190 12 Z' fill='#2ec4b6' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<ellipse rx='212' ry='94' fill='{cuerpo}'/>")
    g.append(f"<ellipse rx='210' ry='34' fill='#fff'/><ellipse rx='210' ry='11' fill='{cuerpo}'/>")
    g.append(f"<path d='M-130 -64 Q-10 -94 100 -72' fill='none' stroke='#ffb0b2' stroke-width='12' stroke-linecap='round'/>")
    g.append(f"<ellipse rx='212' ry='94' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    ry = 23 * (1 + 0.25 * susto)
    for ex in (92, 142):
        g.append(f"<g transform='translate({ex},-38) scale(1,{parp})'><ellipse rx='18' ry='{ry:.0f}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{4 + mira * 5:.0f}' cy='{3 + abs(mira) * 2:.0f}' r='{10 - 3 * susto:.0f}' fill='#1e2a38'/><circle cx='{1 + mira * 5:.0f}' cy='-3' r='3.5' fill='#fff'/></g>")
    g.append(f"<circle cx='66' cy='22' r='10' fill='#ff9ec0' opacity='0.85'/><circle cx='168' cy='20' r='10' fill='#ff9ec0' opacity='0.85'/>")
    if susto > 0.5:
        g.append(f"<ellipse cx='118' cy='56' rx='13' ry='12' fill='#7a2433' stroke='{INK}' stroke-width='5'/>")
    elif frio > 0.5:
        g.append(f"<path d='M96 54 l8 -7 l8 7 l8 -7 l8 7 l8 -7 l8 7' fill='none' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M96 48 Q118 66 140 48' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    if frio > 0:   # carámbanos colgando del globo
        for i, cx in enumerate((-130, -80, -30, 20, 70)):
            ly = 94 * math.sqrt(max(0, 1 - (cx / 212) ** 2)) - 6
            g.append(f"<path d='M{cx - 9} {ly:.0f} L{cx + 9} {ly:.0f} L{cx} {ly + (24 + 10 * (i % 2)) * frio:.0f} Z' fill='#bfeaff' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>")
        g.append(f"<path d='M-150 -70 Q-40 -110 60 -86' fill='none' stroke='#fff' stroke-width='16' stroke-linecap='round' opacity='{0.8 * frio:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def charran(x, y, s, t, dirx=1, fase=0.0, op=1.0):
    """Charrán ártico de perfil: blanco, alas grises largas y puntiagudas, gorro negro, pico y patas rojos,
    cola en horquilla."""
    k = math.sin(t * 9 + fase)
    ty = -10 - 120 * k
    tx = -70 + 25 * abs(k)
    def ala(dx, dy, col):
        return (f"<path d='M{24 + dx} {-14 + dy} Q{-5 + dx} {ty * 0.55 + dy:.0f} {tx - 40 + dx:.0f} {ty + dy:.0f} "
                f"Q{-25 + dx} {ty * 0.25 + 6 + dy:.0f} {-22 + dx} {-6 + dy} Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    parp = 0.15 if ((t + fase) % 3.1) < 0.12 else 1
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})' opacity='{op:.2f}'>"
            + ala(-14, -4, "#9eabb7")
            + f"<path d='M-58 -6 L-165 -42 L-112 2 L-165 30 L-58 10 Z' fill='#e9eef2' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M-14 18 L-34 30 M6 20 L-12 32' stroke='#e8382f' stroke-width='6' stroke-linecap='round'/>"
            f"<path d='M-72 0 Q-40 -30 30 -26 Q66 -24 80 -10 Q88 6 72 14 Q30 28 -40 16 Q-72 10 -72 0 Z' fill='#fbfdff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<circle cx='82' cy='-14' r='22' fill='#fbfdff' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M60 -16 A22 22 0 0 1 104 -14 L98 -6 Q80 -10 61 -8 Z' fill='#1c2230' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<path d='M101 -16 L152 -7 L101 -3 Z' fill='#e8382f' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<g transform='translate(88,-16) scale(1,{parp})'><circle r='6' fill='#fff'/><circle cx='1' r='3.5' fill='#111'/></g>"
            + ala(0, 2, "#d5dde4") + "</g>")


def osito(x, y, s, t, anda=1.0):
    """Oso polar de perfil caminando hacia la derecha."""
    p = math.sin(t * 4) * anda
    parp = 0.15 if (t % 3.9) < 0.13 else 1
    def pata(px, fase):
        a = 14 * math.sin(t * 4 + fase) * anda
        return (f"<g transform='rotate({a:.1f},{px},-60)'><rect x='{px - 24}' y='-70' width='48' height='92' rx='20' fill='#efe6cf' stroke='{INK}' stroke-width='{LW}'/>"
                f"<path d='M{px - 22} 14 q22 10 44 0' fill='none' stroke='{INK}' stroke-width='5'/></g>")
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
            f"<ellipse cx='0' cy='26' rx='190' ry='16' fill='#9fc3dc' opacity='0.6'/>"
            + pata(-110, 3.1) + pata(90, 0) +
            f"<path d='M-190 -80 Q-200 -190 -60 -200 Q60 -205 130 -170 Q175 -150 180 -100 Q182 -40 130 -30 L-150 -30 Q-195 -40 -190 -80 Z' fill='#fbf6e6' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-196 -120 q-22 0 -20 18' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
            + pata(-150, 0) + pata(60, 3.1) +
            f"<g transform='translate({170 + 4 * p:.0f},-140)'>"
            f"<path d='M-40 20 Q-50 -40 10 -50 Q60 -52 90 -20 Q110 -6 104 8 Q96 22 60 22 Q10 40 -40 20 Z' fill='#fbf6e6' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<circle cx='-10' cy='-46' r='14' fill='#fbf6e6' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='104' cy='0' rx='11' ry='9' fill='{INK}'/>"
            f"<g transform='translate(42,-18) scale(1,{parp})'><circle r='7' fill='{INK}'/><circle cx='-2' cy='-2' r='2.5' fill='#fff'/></g>"
            f"<path d='M70 16 q12 6 22 -2' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g></g>")


def beluga(x, y, s, t, op=1.0):
    c = 14 * math.sin(t * 2.6)
    parp = 0.15 if (t % 4.3) < 0.13 else 1
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})' opacity='{op:.2f}'>"
            f"<path d='M-250 0 L-330 {-55 + c:.0f} Q-300 {c * 0.3:.0f} -330 {55 + c:.0f} Z' fill='#e6eef5' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-260 0 Q-150 -80 40 -80 Q150 -82 190 -40 Q215 -10 205 20 Q190 60 110 70 Q-100 80 -260 0 Z' fill='#f4f8fb' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M40 50 Q20 100 -30 110 Q-10 70 0 45 Z' fill='#e6eef5' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M120 -70 Q170 -60 185 -30' fill='none' stroke='#fff' stroke-width='10' stroke-linecap='round'/>"
            f"<g transform='translate(140,-14) scale(1,{parp})'><circle r='10' fill='{INK}'/><circle cx='-3' cy='-3' r='3' fill='#fff'/></g>"
            f"<path d='M160 30 Q185 34 202 18' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def pez(x, y, s, t, col="#ffb347", dirx=1):
    c = 14 * math.sin(t * 9 + x)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"
            f"<path d='M-50 0 L-85 {-28 + c:.0f} L-80 0 L-85 {28 + c:.0f} Z' fill='{mix(col, '#000000', 0.2)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<ellipse rx='58' ry='28' fill='{col}' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='30' cy='-6' r='8' fill='#fff' stroke='{INK}' stroke-width='4'/><circle cx='32' cy='-6' r='4' fill='{INK}'/></g>")


def pinguino(x, y, s, t, flaco=0.0, pliegue=0.0, huevo=False, cria=0.0, fase=0.0, oscuro=0.0, dirx=1):
    """Pingüino emperador de pie (perfil 3/4 mirando a la derecha): espalda negra, barriga blanca,
    pecho amarillo claro, mancha naranja en el cuello y franja naranja en el pico. y = suelo (pies)."""
    bal = 3 * math.sin(t * 1.8 + fase)
    parp = 0.15 if ((t + fase) % 3.4) < 0.13 else 1
    negro = mix("#1d2333", "#0d1220", oscuro)
    blanco = mix("#f7f7f2", "#b8c3d3", oscuro)
    sx = 1 - 0.28 * flaco
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({bal:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    g.append(f"<ellipse cx='0' cy='4' rx='75' ry='12' fill='#7fa6c8' opacity='0.45'/>")
    g.append(f"<g transform='scale({sx:.3f},1)'>")
    g.append(f"<path d='M-60 -10 Q-88 -130 -58 -215 Q-42 -262 2 -264 Q44 -262 54 -222 Q80 -125 60 -10 Q0 8 -60 -10 Z' fill='{negro}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-22 -14 Q-44 -110 -16 -196 Q20 -214 42 -188 Q66 -110 48 -14 Q12 2 -22 -14 Z' fill='{blanco}'/>")
    g.append(f"<path d='M-14 -192 Q20 -212 42 -186 Q50 -160 46 -140 Q12 -150 -20 -150 Q-24 -172 -14 -192 Z' fill='{mix('#ffe7a0', '#9aa6b5', oscuro)}' opacity='0.9'/>")
    g.append(f"<path d='M-50 -190 Q-82 -120 -70 -60 Q-60 -50 -52 -70 Q-48 -130 -36 -180 Z' fill='{negro}' stroke='{INK}' stroke-width='6' stroke-linejoin='round' "
             f"transform='rotate({6 * math.sin(t * 2.4 + fase):.1f},-44,-185)'/>")
    g.append("</g>")
    # cabeza
    g.append(f"<circle cx='8' cy='-250' r='40' fill='{negro}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M14 -232 Q40 -232 44 -206 Q30 -196 18 -204 Q8 -216 14 -232 Z' fill='{mix('#ffa726', '#8a7a60', oscuro)}'/>")
    g.append(f"<path d='M40 -262 Q80 -262 104 -244 Q80 -238 42 -242 Z' fill='{negro}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append(f"<path d='M50 -246 Q76 -244 96 -243' fill='none' stroke='#ff8a50' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<g transform='translate(28,-258) scale(1,{parp})'><circle r='7' fill='#fff'/><circle cx='2' r='4' fill='#111'/></g>")
    # patas
    g.append(f"<path d='M-34 -6 q-10 12 -24 12 h40 Z M14 -6 q10 12 34 12 h-40 Z' fill='#2c2c33' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    if huevo or cria > 0:
        if cria > 0:
            ch = cria
            g.append(f"<g transform='translate(14,{-30 - 20 * ch:.0f}) scale({0.6 + 0.4 * ch:.2f})'>"
                     f"<ellipse cx='0' cy='0' rx='34' ry='38' fill='#b9c0c9' stroke='{INK}' stroke-width='6'/>"
                     f"<circle cx='4' cy='-40' r='24' fill='#1d2333' stroke='{INK}' stroke-width='5'/>"
                     f"<path d='M-8 -44 Q4 -64 22 -48 Q22 -28 4 -26 Q-12 -30 -8 -44 Z' fill='#fff'/>"
                     f"<circle cx='8' cy='-44' r='4.5' fill='#111'/><path d='M24 -40 l14 3 l-14 4 Z' fill='#1d2333'/></g>")
        else:
            g.append(f"<ellipse cx='14' cy='-30' rx='26' ry='33' fill='#fffdf4' stroke='{INK}' stroke-width='6'/>"
                     f"<path d='M4 -48 Q10 -56 20 -52' fill='none' stroke='#fff' stroke-width='5' stroke-linecap='round'/>")
    # pliegue de la barriga (tapa el huevo; se levanta con pliegue=1)
    sube = 34 * pliegue
    g.append(f"<path d='M-26 {-20 - sube:.0f} Q14 {-2 - sube * 1.4:.0f} 52 {-20 - sube:.0f} Q50 {-50 - sube:.0f} 14 {-62 - sube * 0.6:.0f} Q-24 {-50 - sube:.0f} -26 {-20 - sube:.0f} Z' "
             f"fill='{mix(blanco, '#b8c3d3', 0.3)}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def termometro(x, y, nivel, op, frio=True):
    """Termómetro: nivel de 0 (vacío) a 1 (lleno)."""
    alto = 340
    col = "#3aa8ff" if frio else "#e8382f"
    return (f"<g transform='translate({x},{y})' opacity='{op:.2f}'>"
            f"<rect x='-30' y='{-alto}' width='60' height='{alto + 10}' rx='30' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
            f"<rect x='-14' y='{-alto * nivel + 10:.0f}' width='28' height='{alto * nivel:.0f}' fill='{col}'/>"
            f"<circle cy='44' r='54' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='-16' cy='30' r='12' fill='#fff' opacity='0.5'/>"
            + "".join(f"<line x1='30' y1='{-alto + 40 + i * 52}' x2='8' y2='{-alto + 40 + i * 52}' stroke='{INK}' stroke-width='5'/>" for i in range(6))
            + "</g>")


def escarcha(k):
    """Escarcha que se forma en los bordes de la pantalla."""
    if k <= 0:
        return ""
    s = ["<defs><radialGradient id='esc' cx='0.5' cy='0.5' r='0.75'><stop offset='0.55' stop-color='#ffffff' stop-opacity='0'/>"
         "<stop offset='1' stop-color='#e8f8ff' stop-opacity='0.95'/></radialGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#esc)' opacity='{k:.2f}'/>"]
    for i in range(14):
        a = i / 14 * 2 * math.pi
        cx, cy = 960 + 1000 * math.cos(a), 540 + 600 * math.sin(a)
        r = 150 * k
        s.append(f"<g transform='translate({cx:.0f},{cy:.0f}) rotate({i * 23})' opacity='{0.8 * k:.2f}'>"
                 + "".join(f"<line x1='0' y1='0' x2='{r * math.cos(b * math.pi / 3):.0f}' y2='{r * math.sin(b * math.pi / 3):.0f}' stroke='#fff' stroke-width='7' stroke-linecap='round'/>" for b in range(6))
                 + "</g>")
    return "".join(s)


def copo_nieve(x, y, r, ang, op=1.0):
    s = [f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f})' opacity='{op:.2f}'>"]
    for b in range(6):
        s.append(f"<g transform='rotate({b * 60})'><line x1='0' y1='0' x2='0' y2='{-r}' stroke='#fff' stroke-width='6' stroke-linecap='round'/>"
                 f"<path d='M{-r * 0.25:.0f} {-r * 0.7:.0f} L0 {-r * 0.5:.0f} L{r * 0.25:.0f} {-r * 0.7:.0f}' fill='none' stroke='#fff' stroke-width='5' stroke-linecap='round'/></g>")
    s.append("</g>")
    return "".join(s)


def sol(cx, cy, r, op=1.0):
    return (f"<defs><radialGradient id='solh'><stop offset='0' stop-color='#fff8c8'/><stop offset='1' stop-color='#ffd85a' stop-opacity='0'/></radialGradient></defs>"
            f"<g opacity='{op:.2f}'><circle cx='{cx}' cy='{cy}' r='{r * 2.3:.0f}' fill='url(#solh)'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/></g>")


# ================= capítulos =================
def esc_intro(t, dur, m):
    s = [cielo("#071733", "#1d4a7c"), estrellas(t), aurora(t, 1.0, 360)]
    for x, y, sc in ((300, 760, 1.2), (1580, 770, 1.5), (1050, 790, 0.8)):
        s.append(iceberg(x, y, sc, t, "#e4f4ff"))
    s.append(suelo(790, t, "#eaf6ff", "#bcdaf0"))
    # el charrán cruza desde el fotograma 0
    k = (t * 0.11) % 1
    tx = lerp(700, 2200, k) if t < m[2] else lerp(1100, 2300, seg(t, m[2], m[2] + 4))
    ty = 400 + 40 * math.sin(t * 1.3)
    s.append(charran(tx, ty, 0.9, t))
    s.append(charran(lerp(-200, 1500, (t * 0.08 + 0.2) % 1), 300 + 20 * math.sin(t), 0.5, t, fase=1.3, op=0.85))
    # Copo entra (frase 2), y en la frase 3 despega hacia la derecha
    entra = seg(t, max(0.0, m[2] - 0.8), m[2] + 1.6)
    sale = seg(t, m[3] + 1.0, dur + 0.3)
    cx = lerp(-400, 760, entra) + lerp(0, 1600, sale)
    cy = 560 + 14 * math.sin(t * 2.1) - lerp(0, 160, sale)
    if entra > 0:
        s.append(copo(cx, cy, 0.95, t, ang=4 * math.sin(t * 1.7) - 6 * sale, guino=(m[2] + 1.8 < t < m[2] + 2.2)))
        if sale > 0:
            for i in range(6):
                s.append(f"<path d='M{cx - 330 - i * 70:.0f} {cy - 60 + i * 26:.0f} h-{120 * sale:.0f}' stroke='#fff' stroke-width='8' stroke-linecap='round' opacity='{0.7 * sale:.2f}'/>")
    s.append(nieve(t, 0.85))
    return "".join(s)


def tierra_globo(cx, cy, r, t, op=1.0):
    """La Tierra vista de lado con los dos polos blancos arriba y abajo."""
    c = []
    for i, (u, v, w, h) in enumerate([(-0.45, -0.45, 0.32, 0.22), (-0.35, 0.05, 0.22, 0.38), (0.25, -0.35, 0.4, 0.25),
                                      (0.35, 0.15, 0.22, 0.3), (0.62, 0.42, 0.18, 0.14), (-0.1, -0.15, 0.12, 0.1)]):
        c.append(f"<ellipse cx='{cx + u * r:.0f}' cy='{cy + v * r:.0f}' rx='{w * r:.0f}' ry='{h * r:.0f}' fill='#4caf50' stroke='#2e7d32' stroke-width='5' "
                 f"transform='rotate({(i * 31) % 50 - 25},{cx + u * r:.0f},{cy + v * r:.0f})'/>")
    c.append(f"<ellipse cx='{cx}' cy='{cy - r * 0.95:.0f}' rx='{r * 0.55:.0f}' ry='{r * 0.2:.0f}' fill='#ffffff'/>")
    c.append(f"<ellipse cx='{cx}' cy='{cy + r * 0.95:.0f}' rx='{r * 0.75:.0f}' ry='{r * 0.25:.0f}' fill='#ffffff'/>")
    for i in range(4):
        x = cx + r * (((i * 0.55 + t * 0.04) % 2) - 1)
        c.append(f"<path d='M{x - r * 0.25:.0f} {cy + (i - 1.5) * r * 0.45:.0f} q{r * 0.12:.0f} {-r * 0.06:.0f} {r * 0.25:.0f} 0 t{r * 0.25:.0f} 0' fill='none' stroke='#fff' stroke-width='9' stroke-linecap='round' opacity='0.8'/>")
    return (f"<g opacity='{op:.2f}'><defs><clipPath id='glo'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath></defs>"
            f"<circle cx='{cx}' cy='{cy}' r='{r + 26}' fill='#9fe0ff' opacity='0.25'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#2f8fe0'/><g clip-path='url(#glo)'>{''.join(c)}"
            f"<circle cx='{cx + r * 0.7:.0f}' cy='{cy}' r='{r * 1.05:.0f}' fill='#0b0a2e' opacity='0.25'/></g>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/></g>")


def ruta_polos(cx, cy, r, k):
    """Puntos de la ruta: baja por la izquierda del globo (Atlántico) y sube por la derecha. k de 0 a 1."""
    pts = []
    n = 80
    for i in range(int(n * k) + 1):
        u = i / n
        if u <= 0.5:
            a = math.pi * (u / 0.5)        # de arriba (0) a abajo (pi), por la izquierda
            x = cx - r * 0.55 * math.sin(a); y = cy - r * 0.92 * math.cos(a)
        else:
            a = math.pi * ((u - 0.5) / 0.5)
            x = cx + r * 0.45 * math.sin(a); y = cy + r * 0.92 * math.cos(a)
        pts.append((x, y))
    return pts


def luna(cx, cy, r):
    return (f"<circle cx='{cx}' cy='{cy}' r='{r + 18}' fill='#fff8d0' opacity='0.2'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#e9e4d4' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='{cx - r * 0.3:.0f}' cy='{cy - r * 0.25:.0f}' r='{r * 0.22:.0f}' fill='#cfc8b4' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='{cx + r * 0.35:.0f}' cy='{cy + r * 0.2:.0f}' r='{r * 0.15:.0f}' fill='#cfc8b4' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='{cx - r * 0.1:.0f}' cy='{cy + r * 0.45:.0f}' r='{r * 0.1:.0f}' fill='#cfc8b4' stroke='{INK}' stroke-width='3'/>")


def esc_charran(t, dur, m):
    f2 = seg(t, m[2] - 0.4, m[2] + 0.4)     # paso al globo
    f3 = seg(t, m[4] - 0.4, m[4] + 0.4)     # paso a la Tierra y la Luna
    s = []
    if f2 < 1:   # costa ártica en verano
        g = [cielo("#6cc8f5", "#dff5ff"), sol(1500, 250, 70)]
        g.append(f"<rect y='640' width='{W}' height='440' fill='#2a8fd0'/>")
        for i in range(7):
            sx = (i * 300 + t * 30) % 2100 - 100
            g.append(f"<path d='M{sx:.0f} {700 + (i * 61) % 200:.0f} q30 -12 60 0' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.8'/>")
        for x, y, w in ((1300, 700, 170), (1700, 760, 120), (420, 820, 140)):
            g.append(f"<ellipse cx='{x}' cy='{y + 4 * math.sin(t + x):.0f}' rx='{w}' ry='26' fill='#f2fbff' stroke='{INK}' stroke-width='7'/>")
        g.append(iceberg(1650, 650, 0.9, t))
        g.append(f"<path d='M-20 660 Q150 560 380 600 Q560 630 700 720 Q760 760 700 820 L-20 840 Z' fill='#8a8f96' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M-20 640 Q150 548 380 588 Q470 600 520 625 Q420 610 300 625 Q120 640 -20 690 Z' fill='#7fbf5a' stroke='{INK}' stroke-width='6'/>")
        for i, bx in enumerate((120, 230, 340)):   # charranes posados
            g.append(f"<g transform='translate({bx},{600 - i * 6}) scale(0.45)'>"
                     f"<path d='M-60 0 Q-20 -40 50 -30 Q80 -10 60 10 Q0 30 -60 0 Z' fill='#fbfdff' stroke='{INK}' stroke-width='9'/>"
                     f"<circle cx='62' cy='-40' r='24' fill='#1c2230' stroke='{INK}' stroke-width='6'/>"
                     f"<path d='M80 -42 L130 -34 L80 -30 Z' fill='#e8382f' stroke='{INK}' stroke-width='6'/>"
                     f"<path d='M-10 14 L-10 46 M20 14 L20 46' stroke='#e8382f' stroke-width='9'/></g>")
        llega = seg(t, 0.3, m[1])
        big = seg(t, m[1] - 0.2, m[1] + 1.2)
        bx = lerp(2100, 1150, llega) + 30 * math.sin(t * 1.1); by = 470 + 30 * math.sin(t * 1.7)
        g.append(copo(lerp(-300, 420, seg(t, 0, 2.2)), 470 + 12 * math.sin(t * 2), 0.75, t, mira=0.6))
        g.append(charran(bx, by, lerp(0.9, 1.6, big), t))
        g.append(destellos(bx + 40, by - 20, seg(t, m[1] + 0.2, m[1] + 1.8), 10, 260))
        s.append(f"<g opacity='{1 - f2:.2f}'>{''.join(g)}</g>")
    if f2 > 0 and f3 < 1:   # el globo con la ruta de polo a polo
        g = [cielo("#0b1d3a", "#1e3f6e", "cg"), estrellas(t, 0.8)]
        gx, gy, gr = 1250, 640, 255
        g.append(tierra_globo(gx, gy, gr, t))
        k = seg(t, m[2] + 0.3, m[3] + 0.6)
        pts = ruta_polos(gx, gy, gr, k)
        for i, (x, y) in enumerate(pts):
            if i % 2 == 0:
                g.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='7' fill='#ffd23f' stroke='{INK}' stroke-width='3'/>")
        if pts:
            x, y = pts[-1]
            g.append(charran(x, y, 0.42, t, dirx=1 if len(pts) < 41 else -1))
        # dos veranos: un sol se enciende en cada polo
        v1 = seg(t, m[3], m[3] + 0.6); v2 = seg(t, m[3] + 1.0, m[3] + 1.6)
        for vy, vk in ((gy - gr - 70, v1), (gy + gr + 40, v2)):
            if vk > 0:
                g.append(f"<g transform='translate({gx + 300},{vy}) scale({vk:.2f})'>"
                         + "".join(f"<line x1='0' y1='0' x2='{60 * math.cos(a * math.pi / 4):.0f}' y2='{60 * math.sin(a * math.pi / 4):.0f}' stroke='#ffd23f' stroke-width='8' stroke-linecap='round' transform='rotate({t * 40:.0f})'/>" for a in range(8))
                         + f"<circle r='34' fill='#ffe066' stroke='{INK}' stroke-width='7'/></g>")
        g.append(copo(470, 600 + 14 * math.sin(t * 2), 0.8, t, mira=0.8))
        s.append(f"<g opacity='{f2 * (1 - f3):.2f}'>{''.join(g)}</g>")
    if f3 > 0:   # ir a la Luna y volver, tres veces
        g = [cielo("#070b25", "#1d1650", "cl"), estrellas(t)]
        ex, ey, mx, my = 430, 640, 1560, 600
        g.append(tierra_globo(ex, ey, 120, t))
        g.append(luna(mx, my, 80))
        cxl, cyl = (ex + mx) / 2, (ey + my) / 2
        cabeza = None
        for j in range(3):
            kk = seg(t, m[4] + 0.6 + j * 1.3, m[4] + 1.8 + j * 1.3)
            if kk <= 0:
                continue
            rx, ry = (mx - ex) / 2 + 40, 70 + 55 * j
            pts = []
            for i in range(int(60 * kk) + 1):
                a = math.pi + 2 * math.pi * i / 60
                pts.append((cxl + rx * math.cos(a), cyl + ry * math.sin(a)))
            col = ["#ffd23f", "#ff8a3d", "#ff5ad8"][j]
            g.append(f"<polyline points='{' '.join(f'{x:.0f},{y:.0f}' for x, y in pts)}' fill='none' stroke='{col}' stroke-width='10' stroke-linecap='round' stroke-dasharray='4 22'/>")
            cabeza = pts[-1]
            if kk >= 1:
                g.append(destellos(ex, ey, seg(t, m[4] + 1.8 + j * 1.3, m[4] + 3.0 + j * 1.3), 10, 170))
        if cabeza:
            g.append(charran(cabeza[0], cabeza[1], 0.38, t))
        s.append(f"<g opacity='{f3:.2f}'>{''.join(g)}</g>")
    return "".join(s)


def esc_polo(t, dur, m):
    s = [cielo("#a9ddff", "#f2fbff"), sol(1550, 300, 60, 0.95)]
    s.append(f"<path d='M0 470 Q300 455 700 465 T1400 460 T1920 468 L1920 560 L0 560 Z' fill='#d9eefb'/>")
    rev = seg(t, m[2] - 0.2, m[2] + 1.4)
    # agua debajo del hielo (se ve al revelarse)
    s.append("<defs><linearGradient id='mar' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a7fc0'/>"
             "<stop offset='0.55' stop-color='#0b3d70'/><stop offset='1' stop-color='#03132b'/></linearGradient></defs>")
    s.append(f"<rect y='585' width='{W}' height='{H - 585}' fill='url(#mar)'/>")
    if rev > 0:
        for i in range(7):   # rayos de luz bajo el hielo
            x = 200 + i * 260 + 30 * math.sin(t * 0.5 + i)
            s.append(f"<path d='M{x:.0f} 600 L{x + 60:.0f} 600 L{x + 160:.0f} 1000 L{x + 60:.0f} 1000 Z' fill='#bfe9ff' opacity='{0.12 * rev:.2f}'/>")
        bx = lerp(2300, 900, seg(t, m[3] - 0.5, m[3] + 4.0)) + 30 * math.sin(t * 0.6)
        s.append(beluga(bx, 780 + 20 * math.sin(t * 1.1), 0.8, t, op=rev))
        for i in range(4):
            s.append(pez((i * 420 + t * 70) % 2200 - 140, 680 + i * 50, 0.6, t, ["#ffb347", "#ff7a5c", "#ffd23f", "#7ad0ff"][i]))
        # flecha de profundidad (frase 3)
        pr = seg(t, m[3] - 0.1, m[3] + 1.6)
        if pr > 0:
            y1 = 600 + 330 * pr
            s.append(f"<line x1='1700' y1='605' x2='1700' y2='{y1:.0f}' stroke='#ffd23f' stroke-width='12' stroke-linecap='round'/>"
                     f"<path d='M1670 {y1 - 10:.0f} L1730 {y1 - 10:.0f} L1700 {y1 + 34:.0f} Z' fill='#ffd23f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                     + "".join(f"<line x1='1680' y1='{y}' x2='1720' y2='{y}' stroke='#ffd23f' stroke-width='6'/>" for y in range(660, int(y1), 60)))
    # placa de hielo: al principio parece suelo firme hasta abajo; al revelarse se queda en una lámina
    fondo = lerp(1100, 610, rev)
    s.append(f"<path d='M-20 560 Q480 548 960 556 T1940 560 L1940 {fondo:.0f} L-20 {fondo:.0f} Z' fill='#f4fbff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if rev < 1:
        for i in range(6):
            yy = 620 + i * 80
            if yy < fondo - 20:
                s.append(f"<path d='M{(i * 377) % 1700 + 60} {yy} q80 -10 160 0' fill='none' stroke='#cfe6f5' stroke-width='10' stroke-linecap='round'/>")
    s.append(f"<path d='M-20 {fondo - 22:.0f} L1940 {fondo - 22:.0f}' stroke='#cbe9fb' stroke-width='14' opacity='{rev:.2f}'/>")
    # grieta (frase 1)
    gr = seg(t, m[1] + 0.8, m[2] + 0.2)
    if gr > 0 and rev < 1:
        s.append(f"<path d='M700 560 L760 610 L730 660 L800 720 L770 {lerp(660, 900, gr):.0f}' fill='none' stroke='#2a7fc0' stroke-width='10' stroke-linecap='round' stroke-linejoin='round' opacity='{1 - rev:.2f}'/>")
    # poste del polo y oso polar
    s.append(f"<rect x='1046' y='400' width='18' height='165' fill='#fff' stroke='{INK}' stroke-width='6'/>"
             + "".join(f"<path d='M1046 {415 + i * 36} L1064 {400 + i * 36} L1064 {416 + i * 36} L1046 {431 + i * 36} Z' fill='#e8382f'/>" for i in range(4))
             + f"<circle cx='1055' cy='392' r='18' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    ox = lerp(1500, 1300, seg(t, 0, dur))
    s.append(osito(ox, 562, 0.55, t, anda=1 - rev * 0.7))
    # Copo: llega, baja a aterrizar, se asusta y sale volando al sur (frase 4)
    llega = seg(t, 0, 2.5); baja = seg(t, m[1], m[1] + 2.0); sube = seg(t, m[2] + 0.2, m[2] + 1.0)
    vete = seg(t, m[4] + 0.5, dur + 0.3)
    cx = lerp(-300, 560, llega) + lerp(0, 1700, vete)
    cy = 330 + 10 * math.sin(t * 2) + lerp(0, 120, baja) - lerp(0, 150, sube) + lerp(0, 120, vete)
    s.append(copo(cx, cy, 0.7, t, ang=lerp(0, 12, vete) + 3 * math.sin(t * 1.8), susto=sube * (1 - seg(t, m[3] + 1.5, m[3] + 2.5)), mira=0.4 + 0.5 * rev))
    s.append(nieve(t, 0.6, tam=0.8))
    return "".join(s)


def esc_pinguinos(t, dur, m):
    tormenta = 0.5 + 0.5 * seg(t, m[3], m[3] + 1.5)
    s = [cielo("#0a1630", "#2d4f80"), estrellas(t, 0.6), aurora(t, 0.8, 300, ("#5cffb0", "#7af0ff"))]
    s.append(suelo(700, t, "#e8f4fc", "#b7d4ea", 14))
    cerca = seg(t, m[2] - 0.3, m[2] + 1.5)
    z = lerp(1.0, 1.4, cerca)
    zx, zy = 980, 840
    g = []
    # grupo de pingüinos apiñados (al fondo)
    for i in range(14):
        fila = i // 7
        px = 420 + (i % 7) * 120 + fila * 60 + 10 * math.sin(t * 0.7 + i)
        g.append(pinguino(px, 705 + fila * 26, 0.55 + 0.05 * fila, t, fase=i * 0.7, oscuro=0.35 - fila * 0.15, dirx=1 if i % 3 else -1))
    # el papá, delante
    pli = seg(t, m[2] + 0.6, m[2] + 1.6) * (1 - seg(t, m[3] + 2.5, m[3] + 3.2)) + seg(t, m[4] + 0.6, m[4] + 1.6)
    flaco = seg(t, m[4] + 0.2, m[4] + 3.5)
    cria = seg(t, m[4] + 1.2, m[4] + 2.6)
    g.append(pinguino(980, 850, 1.05, t, flaco=flaco, pliegue=min(1, pli), huevo=True, cria=cria, fase=0.3))
    if flaco > 0:   # silueta de antes, para comparar
        g.append(f"<g opacity='{0.45 * flaco:.2f}'><path transform='translate(980,850) scale(1.05)' d='M-60 -10 Q-88 -130 -58 -215 Q-42 -262 2 -264 Q44 -262 54 -222 Q80 -125 60 -10' "
                 f"fill='none' stroke='#ffd23f' stroke-width='8' stroke-dasharray='18 14'/></g>")
    g.append(destellos(995, 790, seg(t, m[2] + 1.2, m[2] + 2.6), 10, 170, "#ffffff"))
    g.append(destellos(995, 760, seg(t, m[4] + 2.0, m[4] + 3.4), 12, 200))
    s.append(f"<g transform='translate({zx},{zy}) scale({z:.3f}) translate({-zx},{-zy})'>{''.join(g)}</g>")
    # termómetro (frase 3)
    tk = seg(t, m[3] - 0.2, m[3] + 0.4) * (1 - seg(t, m[4] - 0.3, m[4] + 0.3))
    if tk > 0:
        s.append(termometro(1560, 720, lerp(0.75, 0.22, seg(t, m[3] + 0.2, m[3] + 2.2)), tk))
    # Copo, tiritando
    cx = lerp(-300, 430, seg(t, 0, 2.4)); cy = 300 + 10 * math.sin(t * 2)
    s.append(copo(cx, cy, 0.62, t, frio=0.7, mira=0.6))
    s.append(rachas(t, tormenta))
    s.append(nieve(t, 0.85, viento=tormenta))
    return "".join(s)


def base_vostok(x, y, s):
    g = [f"<g transform='translate({x},{y}) scale({s})'>"]
    for bx, bw, bh, col in ((-260, 220, 90, "#3a7bd5"), (-20, 260, 110, "#ff8a3d"), (260, 160, 80, "#3a7bd5")):
        for lx in (bx + 20, bx + bw - 20):
            g.append(f"<rect x='{lx - 7}' y='-40' width='14' height='40' fill='#6b7380' stroke='{INK}' stroke-width='5'/>")
        g.append(f"<rect x='{bx}' y='{-40 - bh}' width='{bw}' height='{bh}' rx='8' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<rect x='{bx - 6}' y='{-48 - bh}' width='{bw + 12}' height='16' rx='6' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        for wx in range(bx + 30, bx + bw - 30, 60):
            g.append(f"<rect x='{wx}' y='{-20 - bh}' width='30' height='26' rx='4' fill='#ffe58a' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<line x1='330' y1='-120' x2='330' y2='-330' stroke='{INK}' stroke-width='8'/>"
             f"<circle cx='330' cy='-335' r='12' fill='#e8382f' stroke='{INK}' stroke-width='5'/>"
             f"<path d='M300 -280 L360 -280 M310 -240 L350 -240' stroke='{INK}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def satelite(x, y, s, ang):
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({s:.2f})'>"
            f"<rect x='-150' y='-24' width='100' height='48' fill='#2f5fb8' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='50' y='-24' width='100' height='48' fill='#2f5fb8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-125 -24 V24 M-100 -24 V24 M-75 -24 V24 M75 -24 V24 M100 -24 V24 M125 -24 V24' stroke='#9fc3ff' stroke-width='4'/>"
            f"<rect x='-50' y='-40' width='100' height='80' rx='10' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='0' cy='44' r='16' fill='#c9ced6' stroke='{INK}' stroke-width='6'/></g>")


def esc_vostok(t, dur, m):
    s = [cielo("#040a1a", "#1a2f58"), estrellas(t), aurora(t, 0.7, 280, ("#ff7ad9", "#5cffb0"))]
    s.append(f"<path d='M-20 760 Q480 700 960 690 T1940 720 L1940 1100 L-20 1100 Z' fill='#cfe3f3' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M-20 840 Q600 800 1100 810 T1940 830 L1940 1100 L-20 1100 Z' fill='#b4cde3'/>")
    base = seg(t, m[1] - 0.5, m[1] + 1.0)
    if base > 0:
        s.append(f"<g opacity='{base:.2f}'>{base_vostok(lerp(1400, 1150, base), 735, 0.85)}</g>")
    # hondonadas que brillan (frase 3)
    hk = seg(t, m[3] + 1.0, m[3] + 2.0)
    for hx in (420, 760, 1600):
        s.append(f"<ellipse cx='{hx}' cy='{870 + (hx % 3) * 20}' rx='110' ry='24' fill='{mix('#9fbcd6', '#7ff4ff', hk)}' stroke='{INK}' stroke-width='6'/>")
        if hk > 0:
            s.append(f"<ellipse cx='{hx}' cy='{870 + (hx % 3) * 20}' rx='{150 + 20 * math.sin(t * 5):.0f}' ry='50' fill='#7ff4ff' opacity='{0.3 * hk:.2f}'/>")
    sk = seg(t, m[3] - 0.3, m[3] + 3.2)
    if 0 < sk < 1:
        sx = lerp(-200, 2100, sk); sy = 200 + 40 * math.sin(sk * 3)
        s.append(f"<path d='M{sx:.0f} {sy + 40:.0f} L{sx - 200:.0f} 880 L{sx + 200:.0f} 880 Z' fill='#7ff4ff' opacity='0.18'/>")
        s.append(satelite(sx, sy, 0.7, 10 * math.sin(t)))
    # termómetro que se desploma (frase 2)
    tk = seg(t, m[1] + 0.4, m[1] + 1.0)
    caida = seg(t, m[2] - 0.1, m[2] + 1.6)
    nivel = lerp(0.55, 0.03, caida)
    frio = 0.6 + 0.4 * caida
    if tk > 0:
        s.append(termometro(1560, 600, nivel, tk))
        s.append(destellos(1560, 640, seg(t, m[2] + 1.2, m[2] + 2.8), 12, 230, "#bff6ff"))
    cx = lerp(-300, 560, seg(t, 0, 2.6)); cy = 470 + 10 * math.sin(t * 2)
    s.append(copo(cx, cy, 0.8, t, frio=frio, mira=0.5 if t < m[4] else 0.2))
    for i in range(6):
        k = seg(t, m[2] + 0.2 + i * 0.2, m[2] + 1.2 + i * 0.2)
        if k > 0:
            fx, fy = ((900, 580), (1080, 440), (1250, 620), (1420, 450), (1760, 520), (220, 760))[i]
            s.append(copo_nieve(fx, fy, 34 * k, t * 30 + i * 20, 0.9 * k))
    s.append(escarcha(0.75 * caida))
    s.append(nieve(t, 0.5, tam=0.7))
    return "".join(s)


def edificio(x, base, ancho, pisos, alto_piso, col, t):
    h = pisos * alto_piso
    s = [f"<rect x='{x}' y='{base - h:.0f}' width='{ancho}' height='{h:.0f}' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"]
    for p in range(pisos):
        y = base - (p + 1) * alto_piso + alto_piso * 0.25
        for wx in range(int(x + 14), int(x + ancho - 24), 34):
            s.append(f"<rect x='{wx}' y='{y:.0f}' width='20' height='{alto_piso * 0.45:.0f}' fill='#ffe9a0' stroke='{INK}' stroke-width='3'/>")
    s.append(f"<rect x='{x - 8}' y='{base - h - 14:.0f}' width='{ancho + 16}' height='16' fill='{mix(col, '#000000', 0.25)}' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def esc_hielo(t, dur, m):
    ciudad = seg(t, m[3] - 0.7, m[3] + 0.1)
    s = []
    if ciudad < 1:   # corte de la capa de hielo antártica
        g = [cielo("#8fd6ff", "#eaf8ff"), sol(1600, 220, 60)]
        derr = seg(t, m[2] + 0.3, m[3] - 0.5)
        top = lerp(470, 640, derr)
        g.append("<defs><linearGradient id='hie' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f4fbff'/>"
                 "<stop offset='1' stop-color='#8ccbef'/></linearGradient></defs>")
        g.append(f"<path d='M-20 860 L200 760 L360 820 L560 700 L760 800 L980 720 L1180 810 L1400 740 L1600 820 L1940 760 L1940 1100 L-20 1100 Z' fill='#8a6a54' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<path d='M-20 960 L300 900 L700 940 L1100 900 L1500 950 L1940 910 L1940 1100 L-20 1100 Z' fill='#6e5242'/>")
        g.append(f"<path d='M-20 {top:.0f} Q600 {top - 30:.0f} 1200 {top - 20:.0f} T1940 {top:.0f} L1940 760 L1600 820 L1400 740 L1180 810 L980 720 L760 800 L560 700 L360 820 L200 760 L-20 860 Z' "
                 f"fill='url(#hie)' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round' opacity='{1 - 0.6 * derr:.2f}'/>")
        for i in range(5):
            yy = top + 60 + i * 50
            g.append(f"<path d='M{100 + i * 150} {yy:.0f} q300 -14 600 0 t600 0' fill='none' stroke='#b4dcf5' stroke-width='9' opacity='{0.8 * (1 - derr):.2f}'/>")
        # flecha de grosor y montaña para comparar (frase 1)
        fk = seg(t, m[1] - 0.2, m[1] + 1.0) * (1 - seg(t, m[2] + 0.1, m[2] + 0.8))
        if fk > 0:
            g.append(f"<g opacity='{fk:.2f}'><line x1='560' y1='{top + 6:.0f}' x2='560' y2='695' stroke='#e8382f' stroke-width='12'/>"
                     f"<path d='M530 {top + 40:.0f} L560 {top + 4:.0f} L590 {top + 40:.0f} Z M530 660 L560 696 L590 660 Z' fill='#e8382f' stroke='{INK}' stroke-width='5'/>"
                     f"<path d='M1300 700 L1480 {700 - 400 * fk:.0f} L1540 {740 - 400 * fk:.0f} L1580 {710 - 400 * fk:.0f} L1760 700 Z' fill='#9a8f9e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                     f"<path d='M1430 {700 - 300 * fk:.0f} L1480 {700 - 400 * fk:.0f} L1540 {740 - 400 * fk:.0f} L1580 {710 - 400 * fk:.0f} L1620 {700 - 310 * fk:.0f} L1560 {700 - 320 * fk:.0f} L1520 {700 - 290 * fk:.0f} Z' fill='#fff'/>"
                     f"<line x1='600' y1='{top + 6:.0f}' x2='1400' y2='{top + 6:.0f}' stroke='#e8382f' stroke-width='5' stroke-dasharray='16 12'/></g>")
        if derr > 0:   # gotas que caen
            for i in range(10):
                k = ((t * 1.2 + i / 10) % 1)
                gx = 120 + i * 180
                g.append(f"<path transform='translate({gx},{top + 20 + k * 220:.0f})' d='M0 -16 Q13 4 0 12 Q-13 4 0 -16 Z' fill='#5ac8ff' stroke='{INK}' stroke-width='4' opacity='{derr * (1 - k):.2f}'/>")
        g.append(copo(lerp(-300, 430, seg(t, 0, 2.4)), 330 + 10 * math.sin(t * 2), 0.6, t, mira=0.3))
        s.append(f"<g opacity='{1 - ciudad:.2f}'>{''.join(g)}</g>")
    if ciudad > 0:   # ciudad de la costa: el mar sube 58 m
        g = [cielo("#7fd0ff", "#e8f7ff", "cc"), sol(300, 230, 55)]
        base, ap = 900, 23
        g.append(f"<rect y='{base}' width='{W}' height='{H - base}' fill='#c9b48a'/>")
        g.append(edificio(380, base, 170, 8, ap, "#ffb74d", t))
        g.append(edificio(600, base, 150, 13, ap, "#80cbc4", t))
        g.append(edificio(800, base, 200, 22, ap, "#9fa8da", t))
        g.append(edificio(1060, base, 160, 10, ap, "#ef9a9a", t))
        g.append(edificio(1270, base, 190, 16, ap, "#ffe082", t))
        g.append(edificio(1510, base, 140, 6, ap, "#a5d6a7", t))
        g.append(f"<path d='M1680 {base} L1700 {base - 40} M1690 {base - 40} q-30 -10 -50 10 M1690 {base - 40} q30 -14 50 6' stroke='#2e7d32' stroke-width='8' fill='none' stroke-linecap='round'/>")
        sube = seg(t, m[3] + 0.1, m[3] + 2.6)
        nivel = base + 40 - (19 * ap + 40) * sube
        ola = "".join(f"Q{60 + i * 120:.0f} {nivel - 12 * math.sin(t * 2.4 + i):.0f} {120 + i * 120:.0f} {nivel:.0f} " for i in range(17))
        g.append(f"<path d='M0 {nivel:.0f} {ola} L1920 1100 L0 1100 Z' fill='#2a8fd0' fill-opacity='0.72' stroke='{INK}' stroke-width='{LW}'/>")
        for i in range(8):
            sx = (i * 260 + t * 50) % 2000 - 40
            g.append(f"<path d='M{sx:.0f} {nivel + 40 + (i * 53) % 160:.0f} q30 -12 60 0' fill='none' stroke='#bfe9ff' stroke-width='6' stroke-linecap='round' opacity='0.7'/>")
        if sube > 0.6:
            for i in range(3):
                g.append(pez((i * 520 + t * 90) % 2100 - 100, nivel + 110 + i * 70, 0.55, t, ["#ffb347", "#ff7a5c", "#ffd23f"][i]))
        # marca del nivel en el edificio alto
        mk = seg(t, m[3] + 2.0, m[3] + 2.8)
        if mk > 0:
            g.append(f"<g opacity='{mk:.2f}'><line x1='770' y1='{nivel:.0f}' x2='1030' y2='{nivel:.0f}' stroke='#e8382f' stroke-width='10' stroke-dasharray='26 14'/></g>")
            g.append(destellos(900, nivel, seg(t, m[3] + 2.2, m[3] + 3.6), 14, 260))
        g.append(copo(lerp(1700, 1500, ciudad), 330 + 10 * math.sin(t * 2), 0.6, t, susto=seg(t, m[3] + 0.8, m[3] + 1.4), mira=-0.8, guino=False))
        s.append(f"<g opacity='{ciudad:.2f}'>{''.join(g)}</g>")
    return "".join(s)


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


def esc_final(t, dur, m):
    s = [cielo("#ff9a76", "#ffe3a8"), sol(980, 800, 110)]
    for x, y, sc in ((250, 790, 1.1), (1700, 800, 1.3)):
        s.append(iceberg(x, y, sc, t, "#fff4ea"))
    s.append(suelo(800, t, "#fff7ef", "#f2d2c2"))
    s.append(pinguino(1580, 860, 0.7, t, huevo=False, fase=1.0))
    s.append(pinguino(1720, 870, 0.6, t, huevo=False, fase=2.0, dirx=-1))
    s.append(charran((t * 160) % 2400 - 250, 250 + 30 * math.sin(t), 0.6, t))
    llega = seg(t, 0, 2.4)
    nx = lerp(-300, 470, llega) + lerp(0, -40, seg(t, m[1] - 0.5, m[1] + 1.0)); ny = 540 + 16 * math.sin(t * 2)
    s.append(destellos(nx, ny, seg(t, 1.8, 3.2), 12, 260))
    s.append(copo(nx, ny, 0.85, t, ang=4 * math.sin(t * 1.6), guino=(m[3] + 0.4 < t < m[3] + 0.8), mira=0.5))
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
    s.append(nieve(t, 0.5, tam=0.7))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Un pájaro que vuela de polo a polo?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que hay un pájaro que cada año vuela de un polo al otro… y vuelve?",
                "Hoy viajamos de polo a polo, y la última parada te dejará con la boca abierta.",
                "Sube a Copo, nuestro dirigible explorador.",
                "Suscríbete, abrígate y… ¡despegamos!"]},
    {"titulo": "1. El gran viajero del Ártico", "escena": esc_charran, "tarjeta": "CAPÍTULO 1 · EL GRAN VIAJERO",
     "frases": ["Primera parada: el Ártico, en el norte del planeta. Aquí nos espera un pájaro blanco con el pico rojo.",
                "Es el charrán ártico, un pájaro pequeño con unas alas larguísimas.",
                "Cada año vuela del Ártico a la Antártida, y luego vuelve: ¡más de setenta mil kilómetros!",
                "Así vive dos veranos cada año, uno en cada polo.",
                "Y en toda su vida recorre lo mismo que ir a la Luna y volver… ¡tres veces!"],
     "grandes": {2: "70.000 km", 4: "¡3 VECES!"}, "extra": 1.5},
    {"titulo": "2. El Polo Norte sin tierra", "escena": esc_polo, "tarjeta": "CAPÍTULO 2 · EL POLO NORTE",
     "frases": ["Seguimos volando hasta el punto más al norte de la Tierra: el Polo Norte.",
                "Copo baja para aterrizar… pero aquí pasa algo muy raro.",
                "¡En el Polo Norte no hay tierra! Solo una capa de hielo de dos o tres metros que flota sobre el mar.",
                "Y debajo de ese hielo, el océano tiene más de cuatro mil metros de profundidad.",
                "Ahora toca cruzar el planeta entero, hasta el otro extremo: la Antártida."],
     "grandes": {2: "¡SIN TIERRA!", 3: "4.000 m"}},
    {"titulo": "3. El papá pingüino", "escena": esc_pinguinos, "tarjeta": "CAPÍTULO 3 · UN PAPÁ DE RÉCORD",
     "frases": ["Llegamos a la Antártida en pleno invierno. Hace un frío terrible y casi no sale el sol.",
                "Aquí, los pingüinos emperador se apiñan unos contra otros para darse calor.",
                "Fíjate en este papá: lleva un huevo encima de las patas, tapado con un pliegue de su barriga.",
                "Lo cuida así unos dos meses, a más de treinta y cinco grados bajo cero, y sin comer nada.",
                "Cuando por fin nace el polluelo, el papá lleva unos cuatro meses en ayunas… ¡y ha perdido casi la mitad de su peso!"],
     "grandes": {3: "2 MESES", 4: "¡MITAD DE PESO!"}, "extra": 1.0},
    {"titulo": "4. El lugar más frío de la Tierra", "escena": esc_vostok, "tarjeta": "CAPÍTULO 4 · EL LUGAR MÁS FRÍO",
     "frases": ["Copo vuela hacia el centro de la Antártida, una meseta de hielo altísima.",
                "Aquí está la base Vostok, donde un termómetro midió la temperatura más baja de la historia.",
                "¡Ochenta y nueve grados bajo cero! Fue el veintiuno de julio de mil novecientos ochenta y tres.",
                "Y los satélites han encontrado rincones todavía más fríos: ¡hasta noventa y ocho bajo cero!",
                "Pero el mayor secreto de la Antártida está justo debajo de nosotros…"],
     "grandes": {2: "-89,2 °C", 3: "-98 °C"}},
    {"titulo": "5. El secreto del hielo", "escena": esc_hielo, "tarjeta": "CAPÍTULO 5 · UNA MONTAÑA DE HIELO",
     "frases": ["Todo este suelo blanco no es roca: es hielo, una capa gigantesca que cubre casi todo el continente.",
                "En su punto más grueso mide casi cinco kilómetros: ¡más de la mitad de la altura del Everest!",
                "Y ahora, lo más increíble: si todo este hielo se derritiera, el agua acabaría en el mar.",
                "¡El nivel del mar subiría en todo el mundo unos cincuenta y ocho metros!",
                "Es como un edificio de casi veinte pisos. Muchas ciudades de la costa quedarían bajo el agua."],
     "grandes": {1: "4,9 km", 3: "+58 m"}, "extra": 0.8},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje de polo a polo. ¡Copo ya vuelve a casa, calentito!",
                "Si te ha gustado, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
