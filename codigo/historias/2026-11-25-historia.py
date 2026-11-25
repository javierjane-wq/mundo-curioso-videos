"""Episodio: "Viaje por la selva amazónica" con Tuki, un globo aerostático explorador (original).

Datos (verificados el 25-11-2026):
- Encuentro de las aguas (cerca de Manaos, Brasil): el río Negro, oscuro «color té», y el Solimões,
  «color café con leche» y cargado de sedimentos, corren uno al lado del otro en el mismo cauce durante
  varios kilómetros sin mezclarse: las aguas del Solimões son más frías, densas y rápidas, y las del
  Negro más cálidas y lentas; la frontera se ve desde el espacio (NASA Earth Observatory «Meeting of
  the Waters», 2012; ESA «Meeting of waters», 2019).
- El nenúfar gigante: la especie más grande, Victoria boliviana (humedales y ríos del norte de
  Bolivia), tiene hojas de más de 3 m de ancho, «más grande que una cama de matrimonio»; el envés tiene
  gruesos nervios que la refuerzan y espinas (Natural History Museum de Londres y Kew, 2022;
  Universidad de Oxford / Manchester, 2024).
- El perezoso baja de los árboles solo una vez por semana para hacer caca; en su pelo viven algas
  verdes (Trichophilus) que lo tiñen de verde (Smithsonian Magazine; Pauli et al., Proceedings of the
  Royal Society B, 2014).
- «Ríos voladores»: los árboles de la Amazonia (unos 400.000 millones) sueltan cada día unos 20.000
  millones de toneladas de agua al aire, según WWF (Foro Económico Mundial, 2024); otra estimación da
  13-18 km³ al día (Discover Wildlife / BBC, 2026). Ese vapor forma corrientes de humedad que viajan
  como ríos por el cielo y la selva recicla así buena parte de su lluvia. En el guion: «más de diez mil
  millones de toneladas», compatible con ambas.
- Polvo del Sahara: cada año el viento saca del Sahara unos 182 millones de toneladas de polvo;
  27,7 millones caen sobre la cuenca del Amazonas («suficiente para llenar 104.908 camiones») y aportan
  unas 22.000 toneladas de fósforo, más o menos lo que la selva pierde con la lluvia y las
  inundaciones (NASA Goddard, satélite CALIPSO, Yu et al., Geophysical Research Letters, 2015).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-25-historia"
TITULO = "Viaje por la selva amazónica"
VOZ = "ef_dora"
VELOCIDAD = 0.95
MUSICA = 45

W, H = 1920, 1080
rng = np.random.default_rng(25)
VERDES = ["#2f8f3a", "#3fa84a", "#277a33", "#4cb84f", "#1f6b2c", "#5cc25a"]


def _capa(n, y0, y1, r0, r1, semilla):
    r = np.random.default_rng(semilla)
    return [(r.uniform(-60, W + 60), r.uniform(y0, y1), r.uniform(r0, r1), VERDES[int(r.integers(0, 6))], r.uniform(0, 6))
            for _ in range(n)]


CAPA_LEJOS = _capa(40, 600, 660, 50, 90, 1)
CAPA_MEDIO = _capa(34, 720, 800, 70, 120, 2)
CAPA_CERCA = _capa(26, 860, 960, 100, 160, 3)
POLVO = [(rng.uniform(0, 1), rng.uniform(-1, 1), rng.uniform(3, 8), rng.uniform(0, 6)) for _ in range(140)]
MANCHAS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 90), VERDES[i % 6]) for i in range(150)]
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, 420), rng.uniform(1.5, 3.5), rng.uniform(0, 6)) for _ in range(70)]


# ================= piezas comunes =================
def cielo(top, bot, id_="cie"):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def nube(x, y, sc, col="#fff", op=1.0):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})' opacity='{op:.2f}'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def sol(cx, cy, r, op=1.0):
    return (f"<g opacity='{op:.2f}'><circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r * 2.1:.0f}' fill='#fff3b0' opacity='0.35'/>"
            f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r}' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/></g>")


def copa(x, y, r, col, t, fase, borde=True, sway=1.0):
    """Copa de árbol de selva: racimo de círculos."""
    dx = 4 * sway * math.sin(t * 1.2 + fase)
    st = f" stroke='{INK}' stroke-width='6'" if borde else ""
    return (f"<g transform='translate({x + dx:.0f},{y:.0f})'>"
            f"<circle cx='{-r * 0.55:.0f}' cy='{r * 0.15:.0f}' r='{r * 0.62:.0f}' fill='{col}'{st}/>"
            f"<circle cx='{r * 0.55:.0f}' cy='{r * 0.12:.0f}' r='{r * 0.66:.0f}' fill='{col}'{st}/>"
            f"<circle cx='0' cy='{-r * 0.3:.0f}' r='{r * 0.75:.0f}' fill='{col}'{st}/>"
            f"<circle cx='{-r * 0.22:.0f}' cy='{-r * 0.5:.0f}' r='{r * 0.25:.0f}' fill='{mix(col, '#ffffff', 0.25)}'/></g>")


def dosel(t, tinte=0.0, lejos=True, medio=True, cerca=True, y_extra=0):
    """Mar de copas de árboles (de lejos a cerca)."""
    s = []
    if lejos:
        s.append(f"<rect x='0' y='{640 + y_extra}' width='{W}' height='{H}' fill='{mix('#3f8f5a', '#e08a5a', tinte * 0.4)}'/>")
        for x, y, r, c, f in CAPA_LEJOS:
            s.append(copa(x, y + y_extra, r, mix(mix(c, '#7fc7a0', 0.45), '#e8a070', tinte * 0.35), t, f, borde=False, sway=0.4))
    if medio:
        s.append(f"<rect x='0' y='{780 + y_extra}' width='{W}' height='{H}' fill='{mix('#2c7a3a', '#a0603a', tinte * 0.3)}'/>")
        for x, y, r, c, f in CAPA_MEDIO:
            s.append(copa(x, y + y_extra, r, mix(mix(c, '#5fae6a', 0.2), '#d08a5a', tinte * 0.25), t, f, borde=False, sway=0.7))
    if cerca:
        s.append(f"<rect x='0' y='{930 + y_extra}' width='{W}' height='{H}' fill='#1f6b2c'/>")
        for x, y, r, c, f in CAPA_CERCA:
            s.append(copa(x, y + y_extra, r, mix(c, '#c87a4a', tinte * 0.15), t, f))
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


def _gajo(a, b):
    return (f"M0 -250 C{a * 150:.1f} -250 {a * 200:.1f} -60 {a * 40:.1f} 105 L{b * 40:.1f} 105 "
            f"C{b * 200:.1f} -60 {b * 150:.1f} -250 0 -250 Z")


def tuki(x, y, s, t, ang=0.0, llama=0.6, guino=False, mira=0.0, boca=0.0):
    """Tuki: globo aerostático naranja con gajos amarillos, ojos grandes en la tela y cesta de mimbre."""
    parp = 0.12 if (t % 3.9) < 0.13 or guino else 1.0
    fl = llama * (0.85 + 0.15 * math.sin(t * 23) + 0.1 * math.sin(t * 37))
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    # cuerdas y cesta
    for a, b in ((-40, -40), (40, 40), (-14, -22), (14, 22)):
        g.append(f"<line x1='{a}' y1='118' x2='{b}' y2='182' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M-52 180 L52 180 L44 246 Q0 254 -44 246 Z' fill='#c98a4a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for yy in (200, 222):
        g.append(f"<path d='M-48 {yy} Q0 {yy + 6} 48 {yy}' fill='none' stroke='#8a5a2b' stroke-width='5'/>")
    for xx in (-26, 0, 26):
        g.append(f"<line x1='{xx}' y1='184' x2='{xx * 0.9:.0f}' y2='244' stroke='#8a5a2b' stroke-width='4'/>")
    g.append(f"<rect x='-58' y='172' width='116' height='16' rx='8' fill='#a86a32' stroke='{INK}' stroke-width='6'/>")
    # quemador y llama
    if fl > 0.05:
        g.append(f"<path d='M0 {150 - 70 * fl:.0f} Q{22 * fl:.0f} {140 - 20 * fl:.0f} 12 160 Q0 170 -12 160 Q{-22 * fl:.0f} {140 - 20 * fl:.0f} 0 {150 - 70 * fl:.0f} Z' fill='#ffb52e' stroke='{INK}' stroke-width='4'/>"
                 f"<path d='M0 {155 - 40 * fl:.0f} Q9 150 6 162 Q0 166 -6 162 Q-9 150 0 {155 - 40 * fl:.0f} Z' fill='#fff3a8'/>")
    g.append(f"<rect x='-18' y='160' width='36' height='16' rx='4' fill='#9aa3ad' stroke='{INK}' stroke-width='5'/>")
    # tela
    g.append(f"<path d='{_gajo(-1, 1)}' fill='#ff7a2f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for a, b in ((-0.78, -0.42), (0.42, 0.78)):
        g.append(f"<path d='{_gajo(a, b)}' fill='#ffd23f'/>")
    g.append(f"<path d='{_gajo(-0.16, 0.16)}' fill='#ff9a4a'/>")
    g.append(f"<path d='{_gajo(-1, 1)}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-150 -20 Q0 10 150 -20' fill='none' stroke='#3fa84a' stroke-width='16'/>")
    g.append(f"<path d='M-150 -20 Q0 10 150 -20' fill='none' stroke='{INK}' stroke-width='4' opacity='0.5'/>")
    g.append(f"<rect x='-44' y='98' width='88' height='24' rx='8' fill='#d9622a' stroke='{INK}' stroke-width='6'/>")
    g.append("<ellipse cx='-70' cy='-180' rx='26' ry='44' fill='#fff' opacity='0.35' transform='rotate(-25 -70 -180)'/>")
    # cara
    for ex in (-46, 46):
        g.append(f"<ellipse cx='{ex}' cy='-120' rx='30' ry='34' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        g.append(f"<g transform='translate({ex + 6 + 8 * mira:.1f},-116) scale(1,{parp})'><circle r='17' fill='{INK}'/><circle cx='-6' cy='-7' r='6' fill='#fff'/></g>")
    g.append("<ellipse cx='-92' cy='-72' rx='18' ry='10' fill='#ff5a6a' opacity='0.55'/><ellipse cx='92' cy='-72' rx='18' ry='10' fill='#ff5a6a' opacity='0.55'/>")
    if boca > 0.3:
        g.append(f"<ellipse cx='0' cy='-62' rx='{14 + 6 * boca:.0f}' ry='{10 + 12 * boca:.0f}' fill='#7a1f1f' stroke='{INK}' stroke-width='6'/>")
    else:
        g.append(f"<path d='M-28 -70 Q0 -44 28 -70' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def guacamayo(x, y, s, t, dirx=1, fase=0.0):
    """Guacamayo rojo volando: cuerpo rojo, alas azules con banda amarilla y cola larga."""
    a = math.sin(t * 9 + fase)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"
            f"<path d='M-30 6 L-170 {44 + 6 * a:.0f} L-160 {58 + 6 * a:.0f} L-26 22 Z' fill='#e8382f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M-120 {34 + 5 * a:.0f} L-170 {44 + 6 * a:.0f} L-160 {58 + 6 * a:.0f} L-112 {46 + 5 * a:.0f} Z' fill='#2f6fd6'/>"
            f"<path d='M10 -6 Q-10 {-20 - 80 * a:.0f} -80 {-22 - 90 * a:.0f} Q-50 {-8 - 30 * a:.0f} -24 4 Z' fill='#2f6fd6' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M4 -4 Q-8 {-14 - 40 * a:.0f} -40 {-16 - 45 * a:.0f} Q-26 {-6 - 15 * a:.0f} -16 2 Z' fill='#ffd23f'/>"
            f"<ellipse cx='0' cy='6' rx='52' ry='26' fill='#e8382f' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='48' cy='-10' r='24' fill='#e8382f' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='56' cy='-10' rx='13' ry='11' fill='#fff'/><circle cx='58' cy='-12' r='5' fill='{INK}'/>"
            f"<path d='M68 -22 Q100 -22 92 6 Q84 -4 70 -2 Z' fill='#f2efe8' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<path d='M70 -2 Q82 -2 84 4 Q76 10 68 6 Z' fill='{INK}'/></g>")


def polvo_dorado(t, k, x0, y0, x1, y1, cy, ancho=60, vel=0.12, tam=1.0):
    """Corriente de polvo dorado a lo largo de una curva (de x0,y0 a x1,y1 con control cy)."""
    if k <= 0:
        return ""
    s = []
    cx = (x0 + x1) / 2
    for u0, d, r, f in POLVO:
        u = (u0 + t * vel) % 1
        bx = (1 - u) ** 2 * x0 + 2 * u * (1 - u) * cx + u * u * x1
        by = (1 - u) ** 2 * y0 + 2 * u * (1 - u) * cy + u * u * y1
        by += d * ancho * (0.6 + 0.4 * math.sin(u * 6 + f)) + 8 * math.sin(t * 2 + f)
        op = k * min(1, u * 6, (1 - u) * 6) * (0.55 + 0.45 * math.sin(t * 3 + f))
        if op > 0.02:
            s.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{r * tam:.1f}' fill='#ffcf5a' opacity='{op:.2f}'/>")
    return "".join(s)


# ================= capítulos =================
def esc_intro(t, dur, m):
    s = [cielo("#ff9a6b", "#ffe3a8", "ci0"), sol(1500, 560, 110)]
    for i, (cx, cy, sc) in enumerate([(200, 300, 1.1), (900, 250, 0.8), (1500, 330, 0.9)]):
        dx = (cx + t * 16 * (1 + i * 0.3)) % 2300 - 300
        s.append(nube(dx, cy, sc, "#fff2e0"))
    # montañas lejanas y río que serpentea
    s.append(f"<path d='M0 640 L180 560 L330 620 L520 540 L700 610 L900 560 L1100 620 L1300 550 L1520 615 L1720 560 L1920 610 L1920 700 L0 700 Z' fill='#b9876e' opacity='0.6'/>")
    s.append(dosel(t, tinte=0.6, cerca=False))
    s.append(f"<path d='M-40 1080 Q300 900 700 960 Q1100 1020 1300 880 Q1450 790 1700 800 L1960 790 L1960 830 Q1720 840 1600 880 Q1380 960 1300 1080 Z' fill='#ffcf8a' stroke='{INK}' stroke-width='6' opacity='0.9'/>")
    for x, y, r, c, f in CAPA_CERCA:
        if x < 420 or x > 1450:
            s.append(copa(x, y + 40, r, mix(c, '#c87a4a', 0.12), t, f))
    # guacamayos que cruzan desde el primer fotograma
    for i, (y0, sc, v, fa) in enumerate([(430, 0.85, 160, 0), (520, 0.65, 130, 2), (380, 0.55, 190, 4)]):
        bx = (300 + i * 500 + t * v) % 2400 - 250
        s.append(guacamayo(bx, y0 + 30 * math.sin(t * 1.5 + i), sc, t, 1, fa))
    # remolino de polvo dorado (adelanto del final)
    s.append(polvo_dorado(t, 0.9, 2000, 380, 600, 600, 300, 70, 0.18, 1.2))
    # Tuki sube desde abajo (visible desde el fotograma 0) y al final despega hacia arriba
    sube = seg(t, 0, 2.6)
    vuela = seg(t, m[3] + 0.6, dur + 0.3)
    x = 760 + lerp(0, 380, vuela)
    y = lerp(760, 520, sube) + 14 * math.sin(t * 1.8) - lerp(0, 360, vuela)
    s.append(tuki(x, y, 0.95, t, ang=4 * math.sin(t * 1.3), llama=0.5 + 0.5 * vuela + 0.3 * (1 - sube),
                  guino=(m[2] + 1.0 < t < m[2] + 1.4), boca=seg(t, 0.1, 0.4) * (1 - seg(t, 1.6, 2.0))))
    return "".join(s)


def rio_cenital(t, m, dur):
    """Encuentro de las aguas visto desde arriba: el Negro (oscuro) arriba y el Solimões (café con leche) abajo."""
    s = [f"<rect width='{W}' height='{H}' fill='#2d8a3a'/>"]
    for x, y, r, c in MANCHAS:
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='{c}' stroke='{mix(c, '#000000', 0.3)}' stroke-width='4'/>")
    frontera = lambda x: 640 + 14 * math.sin(x / 110 - t * 2.2) + 6 * math.sin(x / 47 + t * 3)
    # cauce principal (de izquierda a derecha), con afluentes que llegan desde la izquierda
    neg = ("M-20 300 Q250 330 460 450 L1940 450 L1940 " + f"{frontera(1940):.0f} "
           + " ".join(f"L{x} {frontera(x):.0f}" for x in range(1900, 440, -40)) + " Q250 620 -20 560 Z")
    sol_ = ("M-20 1000 Q250 980 460 840 L1940 840 L1940 " + f"{frontera(1940):.0f} "
            + " ".join(f"L{x} {frontera(x):.0f}" for x in range(1900, 440, -40)) + " Q250 660 -20 720 Z")
    s.append(f"<path d='{neg}' fill='#2b1810' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='{sol_}' fill='#c99a5e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append("<path d='M" + " L".join(f"{x} {frontera(x):.0f}" for x in range(440, 1960, 40)) +
             "' fill='none' stroke='#fff3d6' stroke-width='5' stroke-dasharray='18 14' opacity='0.55'/>")
    # corrientes: el café va más rápido que el negro
    for i in range(14):
        xa = (i * 150 + t * 90) % 1600 + 380
        ya = 500 + (i * 37) % 110
        s.append(f"<path d='M{xa:.0f} {ya} q30 -8 60 0' fill='none' stroke='#6a4a3a' stroke-width='6' stroke-linecap='round' opacity='0.8'/>")
        xb = (i * 150 + t * 210) % 1600 + 380
        yb = 700 + (i * 41) % 110
        s.append(f"<path d='M{xb:.0f} {yb} q40 -10 80 0' fill='none' stroke='#f0d4a8' stroke-width='6' stroke-linecap='round' opacity='0.9'/>")
    # remolinos en la frontera
    for i in range(6):
        ex = (i * 280 + t * 140) % 1500 + 450
        ey = frontera(ex)
        rr = 16 + 6 * math.sin(t * 3 + i)
        s.append(f"<path d='M{ex - rr:.0f} {ey:.0f} a{rr:.0f} {rr:.0f} 0 1 1 {rr:.0f} {rr:.0f} a{rr * 0.5:.0f} {rr * 0.5:.0f} 0 1 1 {-rr * 0.5:.0f} {-rr * 0.5:.0f}' "
                 f"fill='none' stroke='#a8805a' stroke-width='5' stroke-linecap='round'/>")
    # una barquita en cada río
    for bx, by, col, v in ((1000, 520, "#ffd23f", 40), (700, 760, "#e8382f", 90)):
        xx = (bx + t * v) % 2100 - 100
        s.append(f"<g transform='translate({xx:.0f},{by})'><path d='M-40 -12 L36 -12 L50 0 L36 12 L-40 12 Z' fill='{col}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
                 f"<path d='M-80 0 L-46 0' stroke='#fff' stroke-width='5' opacity='0.6' stroke-linecap='round'/></g>")
    return "".join(s)


def satelite(x, y, s):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<rect x='-110' y='-22' width='70' height='44' fill='#3a6fd6' stroke='{INK}' stroke-width='5'/>"
            f"<rect x='40' y='-22' width='70' height='44' fill='#3a6fd6' stroke='{INK}' stroke-width='5'/>"
            f"<line x1='-75' y1='-22' x2='-75' y2='22' stroke='#9fc4ff' stroke-width='3'/><line x1='75' y1='-22' x2='75' y2='22' stroke='#9fc4ff' stroke-width='3'/>"
            f"<rect x='-40' y='-30' width='80' height='60' rx='10' fill='#d9dde3' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='0' cy='0' r='14' fill='#1e2a38' stroke='{INK}' stroke-width='4'/></g>")


def termo_icono(x, y, frio, op):
    col = "#5ac8ff" if frio else "#ff7a2f"
    return (f"<g transform='translate({x:.0f},{y:.0f})' opacity='{op:.2f}'>"
            f"<circle r='54' fill='#fff' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-11' y='-38' width='22' height='56' rx='11' fill='#fff' stroke='{INK}' stroke-width='5'/>"
            f"<rect x='-5' y='{-14 if frio else -32}' width='10' height='{32 if frio else 50}' fill='{col}'/>"
            f"<circle cy='24' r='15' fill='{col}' stroke='{INK}' stroke-width='5'/></g>")


def esc_rios(t, dur, m):
    z = lerp(1.0, 1.25, seg(t, m[2] - 0.2, m[2] + 1.6)) * lerp(1, 0.84, seg(t, m[4] - 0.3, m[4] + 1.2))
    s = [f"<rect width='{W}' height='{H}' fill='#2d8a3a'/>"]
    s.append(f"<g transform='translate(1000,640) scale({z:.3f}) translate(-1000,-640)'>{rio_cenital(t, m, dur)}")
    # la frontera brilla cuando se dice que no se mezclan
    br = seg(t, m[2] + 0.2, m[2] + 1.0) * (1 - seg(t, m[3] + 0.5, m[3] + 1.5))
    if br > 0:
        s.append(f"<rect x='440' y='{628}' width='1500' height='24' fill='#fff6a8' opacity='{0.45 * br * (0.7 + 0.3 * math.sin(t * 8)):.2f}'/>")
    s.append("</g>")
    # frío y rápido / cálido y lento
    k3 = seg(t, m[3], m[3] + 0.6) * (1 - seg(t, m[4] - 0.2, m[4] + 0.3))
    if k3 > 0:
        s.append(termo_icono(780, 820, True, k3))
        s.append(termo_icono(780, 470, False, k3))
        for i in range(3):
            xx = 900 + i * 60 + ((t * 300) % 60)
            s.append(f"<path d='M{xx:.0f} 800 l40 20 l-40 20' fill='none' stroke='#fff' stroke-width='8' stroke-linecap='round' stroke-linejoin='round' opacity='{k3:.2f}'/>")
    # se ve desde el espacio: pasa un satélite con su haz
    ks = seg(t, m[4] - 0.2, m[4] + 0.6)
    if ks > 0:
        sx = lerp(300, 820, seg(t, m[4] - 0.2, dur))
        s.append(f"<path d='M{sx:.0f} 360 L{sx - 120:.0f} 640 L{sx + 120:.0f} 640 Z' fill='#fff6a8' opacity='{0.3 * ks:.2f}'/>")
        s.append(satelite(sx, 340, 0.9 * ks))
    # Tuki flota por encima del río
    tx = lerp(2200, 1520, seg(t, 0, 2.6)) + 30 * math.sin(t * 0.7)
    s.append(tuki(tx, 560 + 14 * math.sin(t * 1.4), 0.72, t, ang=3 * math.sin(t * 1.1), mira=-1,
                  boca=seg(t, m[2], m[2] + 0.3) * (1 - seg(t, m[2] + 1.6, m[2] + 2.0))))
    return "".join(s)


def hoja_gigante(cx, cy, rx, ry, op=1.0):
    venas = "".join(f"<line x1='{cx}' y1='{cy + ry * 0.05:.0f}' x2='{cx + rx * 0.9 * math.cos(a):.0f}' y2='{cy + ry * 0.05 + ry * 0.75 * math.sin(a):.0f}' stroke='#2f8a2f' stroke-width='4'/>"
                    for a in [i * math.pi / 8 for i in range(16)])
    return (f"<g opacity='{op:.2f}'><ellipse cx='{cx:.0f}' cy='{cy:.0f}' rx='{rx:.0f}' ry='{ry:.0f}' fill='#b8452f' stroke='{INK}' stroke-width='{LW}'/>"
            f"<ellipse cx='{cx:.0f}' cy='{cy + ry * 0.08:.0f}' rx='{rx * 0.94:.0f}' ry='{ry * 0.78:.0f}' fill='#4cae3f' stroke='{INK}' stroke-width='5'/>"
            f"{venas}<ellipse cx='{cx:.0f}' cy='{cy + ry * 0.08:.0f}' rx='{rx * 0.94:.0f}' ry='{ry * 0.78:.0f}' fill='none' stroke='{INK}' stroke-width='5'/></g>")


def flor_nenufar(x, y, s, t, rosa=0.0):
    pet = "".join(f"<ellipse cx='0' cy='-30' rx='16' ry='36' fill='{mix('#ffffff', '#ff8ab8', rosa)}' stroke='{INK}' stroke-width='5' transform='rotate({a})'/>"
                  for a in (-60, -30, 30, 60, 0))
    return (f"<g transform='translate({x:.0f},{y + 4 * math.sin(t * 1.5 + x):.0f}) scale({s:.2f})'>{pet}"
            f"<circle cy='-10' r='14' fill='#ffd23f' stroke='{INK}' stroke-width='5'/></g>")


def ranita(x, y, s, t):
    parp = 0.15 if (t % 3.1) < 0.12 else 1
    gar = 6 * abs(math.sin(t * 2.5))
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<ellipse cx='0' cy='0' rx='46' ry='30' fill='#5ad35a' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='0' cy='{12 + gar * 0.3:.0f}' rx='{22 + gar:.0f}' ry='{10 + gar:.0f}' fill='#c8f5a0' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='-22' cy='-28' r='16' fill='#5ad35a' stroke='{INK}' stroke-width='5'/><circle cx='22' cy='-28' r='16' fill='#5ad35a' stroke='{INK}' stroke-width='5'/>"
            f"<g transform='translate(-22,-29) scale(1,{parp})'><circle r='8' fill='{INK}'/></g><g transform='translate(22,-29) scale(1,{parp})'><circle r='8' fill='{INK}'/></g>"
            f"<path d='M-16 -6 Q0 4 16 -6' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>"
            f"<path d='M-46 18 l-20 10 M46 18 l20 10' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>")


def cama(x, y, s, op):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.3f})' opacity='{op:.2f}'>"
            f"<rect x='-262' y='-170' width='30' height='170' rx='8' fill='#a86a32' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='238' y='-100' width='26' height='100' rx='8' fill='#a86a32' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-236' y='-96' width='476' height='58' rx='14' fill='#fff' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-90 -100 L238 -100 L238 -40 L-90 -40 Q-110 -70 -90 -100 Z' fill='#3a8dff' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse cx='-170' cy='-104' rx='56' ry='22' fill='#fff' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-236' y='-40' width='476' height='18' fill='#8a5a2b' stroke='{INK}' stroke-width='5'/></g>")


def esc_nenufar(t, dur, m):
    ys = 690
    s = [cielo("#8fd9ff", "#e6f8ff", "ci2"), sol(1680, 210, 60)]
    for i, (cx, cy, sc) in enumerate([(300, 260, 0.9), (1100, 200, 0.7)]):
        s.append(nube((cx + t * 14) % 2300 - 300, cy, sc))
    for x, y, r, c, f in CAPA_LEJOS:
        s.append(copa(x, y - 10, r * 1.2, mix(c, '#7fc7a0', 0.3), t, f, borde=False, sway=0.5))
    s.append(f"<rect x='0' y='{ys - 40}' width='{W}' height='60' fill='#2f8a3a'/>")
    # agua (corte: se ve por debajo de la superficie)
    s.append("<defs><linearGradient id='lag' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3aa0a0'/>"
             "<stop offset='1' stop-color='#0f4f5a'/></linearGradient></defs>")
    s.append(f"<rect x='0' y='{ys}' width='{W}' height='{H - ys}' fill='url(#lag)' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(10):
        wx = (i * 210 + t * 30) % 2100 - 80
        s.append(f"<path d='M{wx:.0f} {ys + 30 + (i * 23) % 60} q30 -10 60 0' fill='none' stroke='#bff0ee' stroke-width='5' stroke-linecap='round' opacity='0.6'/>")
    # hoja central: crece al decir el tamaño
    crece = seg(t, m[3] - 0.2, m[3] + 1.8)
    cx = 1040
    rx = lerp(300, 440, crece); ry = rx * 0.17
    # envés con nervios y espinas (frase 2)
    nv = seg(t, m[2] - 0.2, m[2] + 0.8)
    s.append(f"<path d='M{cx} {ys + 6} L{cx} 1080' stroke='#5a8a3a' stroke-width='16'/>")
    for i in range(-6, 7):
        bx = cx + i * rx / 7
        d = 80 * (1 - abs(i) / 8)
        y0r = ys + ry * 0.6
        s.append(f"<rect x='{bx - 10:.0f}' y='{ys:.0f}' width='20' height='{ry * 0.6 + d:.0f}' rx='8' fill='#b8452f' stroke='{INK}' stroke-width='4' opacity='{0.35 + 0.65 * nv:.2f}'/>")
        if nv > 0:
            for j in range(2):
                sy = y0r + d * (0.35 + 0.45 * j)
                s.append(f"<path d='M{bx - 10:.0f} {sy:.0f} l-18 8 l18 6 M{bx + 10:.0f} {sy:.0f} l18 8 l-18 6' fill='#f2efe8' stroke='{INK}' stroke-width='3' opacity='{nv:.2f}'/>")
    if nv > 0:
        s.append(destellos(cx, ys + 40, seg(t, m[2] + 0.3, m[2] + 2.0), 10, 260, "#fff"))
    # peces debajo que no se atreven a morder
    for i, (py, v, col) in enumerate([(870, 70, "#ffb52e"), (960, 50, "#ff7a6a")]):
        px = (300 + i * 700 + t * v) % 2200 - 150
        s.append(f"<g transform='translate({px:.0f},{py + 10 * math.sin(t * 2 + i):.0f}) scale(0.8)'>"
                 f"<path d='M-50 0 L-80 {-24 + 10 * math.sin(t * 9):.0f} L-80 {24 + 10 * math.sin(t * 9):.0f} Z' fill='{mix(col, '#000000', 0.2)}' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse rx='56' ry='28' fill='{col}' stroke='{INK}' stroke-width='6'/><circle cx='30' cy='-6' r='8' fill='#fff' stroke='{INK}' stroke-width='3'/><circle cx='32' cy='-6' r='4' fill='{INK}'/></g>")
    # otras hojas y flores
    s.append(hoja_gigante(330, ys + 4, 200, 34))
    s.append(hoja_gigante(1650, ys + 6, 230, 38))
    s.append(hoja_gigante(cx, ys + 2, rx, ry))
    s.append(flor_nenufar(470, ys - 10, 0.9, t, 0.0))
    s.append(flor_nenufar(1520, ys - 8, 1.0, t, 0.7))
    s.append(ranita(1720, ys - 18, 0.9, t))
    # la cama de matrimonio aparece encima para comparar (frase 4)
    kc = seg(t, m[4] - 0.1, m[4] + 0.6)
    if kc > 0:
        s.append(cama(cx + 20, ys + 2 - 40 * (1 - ease(kc)), 0.95 * (0.6 + 0.4 * ease(kc)), kc))
        s.append(destellos(cx + 20, ys - 70, seg(t, m[4] + 0.2, m[4] + 1.8), 12, 330))
    # Tuki planea por encima
    tx = lerp(-200, 470, seg(t, 0, 2.8))
    ty = 440 + 14 * math.sin(t * 1.5)
    s.append(tuki(tx, ty, 0.62, t, ang=4 * math.sin(t * 1.2), mira=1, guino=(m[4] + 1.5 < t < m[4] + 1.9),
                  boca=seg(t, m[3] + 0.5, m[3] + 0.8) * (1 - seg(t, m[3] + 2.2, m[3] + 2.6))))
    return "".join(s)


def _miembro(x0, y0, x1, y1, col):
    return (f"<path d='M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}' stroke='{INK}' stroke-width='38' stroke-linecap='round'/>"
            f"<path d='M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}' stroke='{col}' stroke-width='26' stroke-linecap='round'/>"
            + "".join(f"<path d='M{x1 + dx:.0f} {y1 + 6:.0f} q6 -26 -14 -30' fill='none' stroke='#3a2a1a' stroke-width='6' stroke-linecap='round'/>" for dx in (-10, 0, 10)))


def perezoso(x, y, s, t, algas=0.0, rot=0.0, mueve=0.0):
    """Perezoso de tres dedos colgado bajo una rama que está en y=0 (local). Algas verdes en el pelo."""
    col = mix("#a08a68", "#8f9f62", algas * 0.8)
    parp = 0.12 if (t % 4.3) < 0.16 else 1
    a = 10 * math.sin(t * 2) * mueve
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({s:.3f})'>"]
    for (sx, gx) in ((-95, -120 + a), (-40, -55 - a), (45, 40 + a), (100, 125 - a)):
        g.append(_miembro(sx, 80, gx, 4, col))
    g.append(f"<ellipse cx='0' cy='96' rx='132' ry='64' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(6):
        g.append(f"<path d='M{-90 + i * 34} {80 + (i % 2) * 18} q12 14 0 28' fill='none' stroke='{mix(col, '#000000', 0.25)}' stroke-width='5' stroke-linecap='round'/>")
    if algas > 0:
        for i in range(16):
            ax = -110 + (i * 53) % 220; ay = 60 + (i * 31) % 70
            g.append(f"<circle cx='{ax}' cy='{ay}' r='{6 + i % 3 * 3}' fill='#5fd35a' opacity='{0.85 * algas:.2f}'/>")
    # cabeza con antifaz
    g.append(f"<g transform='translate(136,118) rotate({8 * math.sin(t * 0.6):.1f})'>"
             f"<circle r='58' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<ellipse cx='4' cy='6' rx='44' ry='38' fill='#efe3c6'/>"
             f"<path d='M-46 -6 Q-22 -20 -6 -2 Q-22 12 -46 4 Z' fill='#4a3424'/><path d='M54 -6 Q30 -20 14 -2 Q30 12 54 4 Z' fill='#4a3424'/>"
             f"<g transform='translate(-20,-4) scale(1,{parp})'><circle r='7' fill='#111'/><circle cx='-2' cy='-2' r='2.5' fill='#fff'/></g>"
             f"<g transform='translate(28,-4) scale(1,{parp})'><circle r='7' fill='#111'/><circle cx='-2' cy='-2' r='2.5' fill='#fff'/></g>"
             f"<ellipse cx='4' cy='14' rx='11' ry='8' fill='#2a1a14'/>"
             f"<path d='M-14 26 Q4 40 22 26' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")
    g.append("</g>")
    return "".join(g)


def caca(x, y, k):
    if k <= 0:
        return ""
    sc = 0.4 + 0.6 * ease(min(1, k * 1.5))
    bol = "".join(f"<ellipse cx='{bx}' cy='{by}' rx='16' ry='11' fill='#7a4a24' stroke='{INK}' stroke-width='4'/>"
                  for bx, by in ((-30, 0), (0, 0), (30, 0), (-15, -16), (15, -16), (0, -32)))
    return f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})'>{bol}</g>"


def calendario(x, y, k):
    if k <= 0:
        return ""
    sc = 0.5 + 0.5 * ease(min(1, k * 1.5))
    c = [f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{min(1, k * 2):.2f}'>",
         f"<rect x='-190' y='-80' width='380' height='160' rx='18' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='-190' y='-80' width='380' height='44' rx='18' fill='#e8382f' stroke='{INK}' stroke-width='{LW}'/>"]
    for i in range(7):
        cx = -162 + i * 54
        hoy = i == 6
        c.append(f"<rect x='{cx - 20}' y='-20' width='40' height='70' rx='8' fill='{'#ffd23f' if hoy else '#e9f0f5'}' stroke='{INK}' stroke-width='4'/>")
        if hoy and k > 0.5:
            c.append(f"<path d='M{cx - 10} 16 l8 10 l14 -22' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")
    c.append("</g>")
    return "".join(c)


def polilla(x, y, t, op):
    a = abs(math.sin(t * 16))
    return (f"<g transform='translate({x:.0f},{y:.0f})' opacity='{op:.2f}'>"
            f"<path d='M0 0 L-22 {-20 * a - 4:.0f} L-26 6 Z M0 0 L22 {-20 * a - 4:.0f} L26 6 Z' fill='#d9c49a' stroke='{INK}' stroke-width='3'/>"
            f"<ellipse rx='5' ry='10' fill='#8a6a4a'/></g>")


def esc_perezoso(t, dur, m):
    s = ["<defs><linearGradient id='bos' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#9fe0a0'/>"
         "<stop offset='1' stop-color='#2f7a3a'/></linearGradient></defs>", f"<rect width='{W}' height='{H}' fill='url(#bos)'/>"]
    # rayos de luz entre los árboles
    for i in range(4):
        x0 = 300 + i * 420
        s.append(f"<path d='M{x0} 0 L{x0 + 90} 0 L{x0 + 300} {H} L{x0 + 150} {H} Z' fill='#fffbe0' opacity='{0.16 + 0.06 * math.sin(t + i):.2f}'/>")
    # troncos de fondo
    for x, w, c in ((180, 70, "#5f7a4a"), (620, 50, "#6a8a52"), (1640, 80, "#5f7a4a")):
        s.append(f"<rect x='{x}' y='0' width='{w}' height='900' fill='{c}' opacity='0.7'/>")
    # suelo
    s.append(f"<path d='M0 870 Q480 840 960 868 T1920 860 L1920 1080 L0 1080 Z' fill='#5a3f24' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(22):
        lx = (i * 97) % 1920; ly = 900 + (i * 53) % 150
        s.append(f"<ellipse cx='{lx}' cy='{ly}' rx='26' ry='10' fill='{['#c0702f', '#d9a03f', '#6f8a3a'][i % 3]}' stroke='{INK}' stroke-width='3' transform='rotate({(i * 37) % 180 - 90} {lx} {ly})'/>")
    # tronco principal y rama
    s.append(f"<path d='M1110 0 L1200 0 L1215 880 L1095 880 Z' fill='#7a5230' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for yy in (120, 300, 520, 700):
        s.append(f"<path d='M1125 {yy} q20 30 0 60' fill='none' stroke='#5a3a20' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<path d='M1180 330 L1820 300 L1825 334 L1185 372 Z' fill='#7a5230' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for x0 in (1300, 1560, 1760):
        s.append(f"<g transform='translate({x0 + 8 * math.sin(t * 1.3 + x0):.0f},300)'><ellipse cx='0' cy='-24' rx='46' ry='24' fill='#3fa84a' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse cx='40' cy='-10' rx='34' ry='18' fill='#4cb84f' stroke='{INK}' stroke-width='5'/></g>")
    # lianas
    for lx in (820, 1480, 1700):
        sw = 16 * math.sin(t * 1.1 + lx)
        s.append(f"<path d='M{lx} 0 Q{lx + sw:.0f} 300 {lx + 2 * sw:.0f} 560' fill='none' stroke='#3f7a2a' stroke-width='10' stroke-linecap='round'/>")
    # recorrido del perezoso: cuelga, va al tronco, baja (frase 3), hace caca y vuelve a subir (frase 4)
    va = seg(t, m[3] - 0.6, m[3] + 0.6)
    baja = seg(t, m[3] + 0.4, m[3] + 2.6)
    sube = seg(t, m[4] + 0.6, dur - 0.2)
    rot = lerp(0, -90, va)
    px = lerp(1420, 1155, va)
    py = lerp(352, 330, va) + lerp(0, 470, baja) - lerp(0, 380, sube)
    mueve = 1.0 if (0 < baja < 1 or 0 < sube < 1) else 0.0
    s.append(perezoso(px, py, 0.95, t, algas=seg(t, m[1] + 1.0, m[1] + 2.4), rot=rot, mueve=mueve))
    kc = seg(t, m[3] + 2.6, m[3] + 3.4)
    s.append(caca(1330, 872, kc))
    if kc > 0:
        for i in range(3):
            k = ((t * 0.6 + i / 3) % 1)
            s.append(f"<path d='M{1300 + i * 30} {840 - k * 80:.0f} q10 -12 0 -24 q-10 -12 0 -24' fill='none' stroke='#8fbf5a' stroke-width='5' stroke-linecap='round' opacity='{(1 - k) * kc:.2f}'/>")
        s.append(polilla(1330 + 50 * math.sin(t * 2), 760 + 20 * math.sin(t * 3), t, kc))
        s.append(destellos(1330, 850, seg(t, m[3] + 2.6, m[3] + 4.2), 10, 170))
    s.append(calendario(560, 760, seg(t, m[3] + 2.4, m[3] + 3.0) * (1 - seg(t, m[4] + 2.0, m[4] + 2.6))))
    # Tuki mira desde la izquierda
    s.append(tuki(lerp(-220, 430, seg(t, 0, 2.6)), 450 + 12 * math.sin(t * 1.4), 0.62, t, ang=3 * math.sin(t),
                  mira=1, boca=seg(t, m[3] + 2.6, m[3] + 2.9) * (1 - seg(t, m[3] + 4.0, m[3] + 4.4))))
    return "".join(s)


def cinta_nubes(t, k, y0=470):
    """Río de nubes que serpentea por el cielo, de derecha a izquierda."""
    if k <= 0:
        return ""
    s = []
    n = 34
    for i in range(n):
        u = i / (n - 1)
        x = lerp(2050, -130, u)
        y = y0 + 60 * math.sin(u * 7 + 0.5) - 20 * u
        r = (52 + 14 * math.sin(i * 1.7)) * (0.3 + 0.7 * clamp(k * 1.6 - u * 0.6))
        if r > 6:
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='#ffffff' stroke='{INK}' stroke-width='5'/>")
    for i in range(n):   # interior sin contornos para que parezca una sola cinta
        u = i / (n - 1)
        x = lerp(2050, -130, u)
        y = y0 + 60 * math.sin(u * 7 + 0.5) - 20 * u
        r = (52 + 14 * math.sin(i * 1.7)) * (0.3 + 0.7 * clamp(k * 1.6 - u * 0.6)) - 6
        if r > 2:
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='#f4fbff'/>")
    # corriente: rayitas azules que fluyen por la cinta
    for i in range(16):
        u = ((i / 16) + t * 0.07) % 1
        x = lerp(2050, -130, u); y = y0 + 60 * math.sin(u * 7 + 0.5) - 20 * u
        if clamp(k * 1.6 - u * 0.6) > 0.5:
            s.append(f"<path d='M{x + 30:.0f} {y:.0f} l-60 {-6 * math.cos(u * 7):.0f}' stroke='#5ab8ff' stroke-width='7' stroke-linecap='round' opacity='{k:.2f}'/>")
    return "".join(s)


def esc_vapor(t, dur, m):
    s = [cielo("#5fc0ff", "#d8f4ff", "ci4"), sol(560, 300, 70)]
    s.append(nube((1300 + t * 12) % 2300 - 300, 250, 0.8))
    # vapor que sube de los árboles
    kv = seg(t, 0.5, m[1] + 0.5) * 0.6 + 0.4 * seg(t, m[2] - 0.2, m[2] + 1.0)
    vap = []
    for i in range(18):
        x0 = 60 + i * 108
        for j in range(3):
            k = ((t * 0.25 + j / 3 + i * 0.13) % 1)
            y = 820 - k * 420
            xx = x0 + 30 * math.sin(k * 6 + i + t)
            vap.append(f"<path d='M{xx:.0f} {y:.0f} q22 -30 0 -60 q-22 -30 0 -60' fill='none' stroke='#ffffff' stroke-width='{12 + 10 * k:.0f}' stroke-linecap='round' opacity='{kv * 0.55 * (1 - k):.2f}'/>")
    # gotitas que salen de las hojas (frase 1)
    kg = seg(t, m[1], m[1] + 0.6)
    if kg > 0:
        for i in range(20):
            k = ((t * 0.5 + i * 0.37) % 1)
            gx = 80 + (i * 97) % 1800; gy = 800 - k * 220
            vap.append(f"<path d='M{gx} {gy - 16:.0f} Q{gx + 10} {gy:.0f} {gx} {gy + 6:.0f} Q{gx - 10} {gy:.0f} {gx} {gy - 16:.0f} Z' fill='#7fd0ff' stroke='{INK}' stroke-width='3' opacity='{kg * (1 - k):.2f}'/>")
    # río de nubes (frase 3) y lluvia (frase 4)
    kr = seg(t, m[3] - 0.3, m[3] + 2.0)
    kl = seg(t, m[4] - 0.2, m[4] + 0.8)
    if kl > 0:
        for i in range(40):
            k = ((t * 1.6 + i * 0.29) % 1)
            lx = (i * 53) % 1920; ly = 520 + k * 300
            s.append(f"<line x1='{lx}' y1='{ly:.0f}' x2='{lx - 8}' y2='{ly + 34:.0f}' stroke='#5ab8ff' stroke-width='5' stroke-linecap='round' opacity='{kl * 0.9:.2f}'/>")
    s.append(cinta_nubes(t, kr, 470))
    s.append(dosel(t, y_extra=-20))
    s.append("".join(vap))
    # Tuki sube desde abajo entre la niebla
    ty = lerp(980, 700, seg(t, 0, 3.0)) + 12 * math.sin(t * 1.3)
    s.append(tuki(1460, ty, 0.6, t, ang=3 * math.sin(t * 1.1), llama=0.8, mira=-1,
                  boca=seg(t, m[2] + 0.2, m[2] + 0.5) * (1 - seg(t, m[2] + 2.0, m[2] + 2.4))))
    s.append(destellos(960, 470, seg(t, m[3] + 0.8, m[3] + 2.6), 14, 520, "#ffffff"))
    return "".join(s)


def esc_sahara(t, dur, m):
    s = ["<defs><linearGradient id='esp' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0b1d4a'/>"
         "<stop offset='0.55' stop-color='#3a6fc0'/><stop offset='1' stop-color='#9fd6ff'/></linearGradient>"
         "<linearGradient id='oce' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3a9ae0'/>"
         "<stop offset='1' stop-color='#0f5aa0'/></linearGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#esp)'/>"]
    for x, y, r, f in ESTRELLAS:
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{0.4 + 0.3 * math.sin(t * 2 + f):.2f}'/>")
    # la Tierra curvada: océano Atlántico en medio, Sudamérica (selva) a la izquierda y África (Sahara) a la derecha
    s.append(f"<ellipse cx='960' cy='2500' rx='2300' ry='2010' fill='#9fd6ff' opacity='0.5'/>")
    s.append(f"<ellipse cx='960' cy='2500' rx='2260' ry='1990' fill='url(#oce)' stroke='{INK}' stroke-width='{LW}'/>")
    verde = seg(t, m[3], m[3] + 2.0)
    s.append(f"<path d='M-20 560 Q160 520 330 545 Q470 570 560 640 Q620 720 560 820 Q500 930 420 1080 L-20 1080 Z' fill='{mix('#2f8a3a', '#3fc24a', verde)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M1940 540 Q1760 520 1600 560 Q1460 600 1420 660 Q1390 720 1470 760 Q1560 800 1620 880 Q1680 980 1700 1080 L1940 1080 Z' fill='#e8b860' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for i in range(6):   # dunas
        dx = 1560 + (i % 3) * 110; dy = 620 + (i // 3) * 70
        s.append(f"<path d='M{dx} {dy} q40 -26 80 0' fill='none' stroke='#c8903a' stroke-width='6' stroke-linecap='round'/>")
    for i in range(12):  # arbolitos de la selva
        ax = 40 + (i * 47) % 480; ay = 600 + (i * 71) % 360
        if ax < 560 - (ay - 640) * 0.4:
            rr = 22 + 10 * verde + 4 * (i % 3)
            s.append(f"<circle cx='{ax}' cy='{ay}' r='{rr:.0f}' fill='{mix('#1f6b2c', '#5cd35a', verde)}' stroke='{INK}' stroke-width='4'/>")
    for i, (cx, cy, sc) in enumerate([(700, 760, 0.5), (1100, 830, 0.45), (850, 640, 0.35)]):
        s.append(nube((cx + t * 10) % 1200 + 500, cy, sc, "#ffffff", 0.85))
    # la nube de polvo cruza el océano desde África (frase 0-1) y se hace más grande (frase 2)
    kp = seg(t, 0.3, 2.5)
    grueso = seg(t, m[2] - 0.2, m[2] + 1.2)
    s.append(polvo_dorado(t, kp, 1600, 640, 330, 650, 470, lerp(40, 90, grueso), 0.1, lerp(1.0, 1.7, grueso)))
    s.append(f"<path d='M1580 610 Q960 420 360 630' fill='none' stroke='#ffcf5a' stroke-width='{lerp(40, 110, grueso):.0f}' stroke-linecap='round' opacity='{0.18 * kp:.2f}'/>")
    # el polvo cae sobre la selva como abono (frase 3)
    kf = seg(t, m[3] - 0.2, m[3] + 0.6)
    if kf > 0:
        for i in range(24):
            k = ((t * 0.7 + i * 0.41) % 1)
            fx = 80 + (i * 61) % 420; fy = 560 + k * 300
            s.append(f"<circle cx='{fx}' cy='{fy:.0f}' r='7' fill='#ffe066' stroke='{INK}' stroke-width='2' opacity='{kf * (1 - k):.2f}'/>")
    # gran momento: desierto y selva unidos (frase 4)
    kb = seg(t, m[4] - 0.1, m[4] + 1.8)
    s.append(destellos(280, 760, kb, 12, 280))
    s.append(destellos(1640, 700, seg(t, m[4] + 0.3, m[4] + 2.1), 12, 240))
    # Tuki vuela muy alto, por debajo de la nube de polvo
    tx = lerp(1250, 960, seg(t, 0, 3)) + 20 * math.sin(t * 0.6)
    s.append(tuki(tx, 735 + 10 * math.sin(t * 1.3), 0.5, t, ang=3 * math.sin(t), llama=0.7,
                  mira=lerp(1, -1, seg(t, 1, 4)), guino=(m[4] + 1.2 < t < m[4] + 1.6),
                  boca=seg(t, m[0] + 0.6, m[0] + 0.9) * (1 - seg(t, m[0] + 2.4, m[0] + 2.8)) + seg(t, m[4], m[4] + 0.3)))
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
    s = [cielo("#ff7a6b", "#ffd9a0", "ci6"), sol(760, 700, 110)]
    for i, (cx, cy, sc) in enumerate([(150, 200, 0.9), (1300, 160, 0.7)]):
        s.append(nube((cx + t * 12) % 2300 - 300, cy, sc, "#ffe8d6"))
    s.append(dosel(t, tinte=1.0))
    for i, (y0, sc, v, fa) in enumerate([(640, 0.5, 110, 1), (700, 0.4, 90, 3)]):
        bx = (200 + i * 900 + t * v) % 2400 - 250
        s.append(guacamayo(bx, y0 + 20 * math.sin(t * 1.5 + i), sc, t, 1, fa))
    tx = lerp(620, 420, seg(t, m[1] - 0.5, m[1] + 1.0))
    s.append(tuki(tx, 540 + 14 * math.sin(t * 1.6), 0.85, t, ang=4 * math.sin(t * 1.4),
                  guino=(m[3] + 0.4 < t < m[3] + 0.8), mira=1))
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
        s.append(f"<g transform='translate(1180,420) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='420' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, 420, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, 420, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(900, 435, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 440, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, 420, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Un desierto que alimenta a una selva?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que la selva más grande del mundo se abona con polvo de un desierto?",
                "Hoy cruzamos la Amazonia, y la última parada te va a dejar con la boca abierta.",
                "Nos acompaña Tuki, nuestro globo explorador.",
                "Suscríbete y… ¡despegamos!"]},
    {"titulo": "1. Dos ríos que no se mezclan", "escena": esc_rios, "tarjeta": "CAPÍTULO 1 · DOS RÍOS QUE NO SE MEZCLAN",
     "frases": ["Primera parada: cerca de la ciudad de Manaos, en Brasil. ¡Mira el río desde arriba!",
                "Aquí se juntan dos ríos enormes: el río Negro, oscuro como el té, y el Solimões, del color del café con leche.",
                "Pero en vez de mezclarse… ¡siguen uno al lado del otro durante kilómetros!",
                "El agua del Solimões es más fría, más pesada y más rápida; la del Negro, más cálida y más lenta.",
                "Por eso la frontera entre los dos ríos se ve incluso desde el espacio."],
     "grandes": {2: "¡SIN MEZCLARSE!"}},
    {"titulo": "2. La hoja gigante", "escena": esc_nenufar, "tarjeta": "CAPÍTULO 2 · LA HOJA GIGANTE",
     "frases": ["Tuki baja hasta una laguna tranquila. ¿Qué son esas bandejas verdes que flotan?",
                "Son hojas de nenúfar gigante, con el borde doblado hacia arriba, como un plato enorme.",
                "Por debajo tienen nervios gruesos que las hacen muy firmes, y espinas para que no se las coman.",
                "La especie más grande vive en Bolivia, y sus hojas miden más de tres metros de ancho.",
                "¡Una sola hoja es más grande que una cama de matrimonio!"],
     "grandes": {3: "MÁS DE 3 METROS"}},
    {"titulo": "3. El perezoso y su viaje semanal", "escena": esc_perezoso, "tarjeta": "CAPÍTULO 3 · UN VIAJE MUY LENTO",
     "frases": ["Ahora nos metemos entre los árboles. ¿Ves esa bola de pelo colgada de una rama?",
                "Es un perezoso de tres dedos, y su pelo es un poco verde… ¡porque le crecen algas!",
                "Se mueve tan despacio que pasa casi toda su vida aquí arriba.",
                "Pero una vez por semana hace algo muy arriesgado: baja hasta el suelo… ¡solo para hacer caca!",
                "Y luego vuelve a subir, tan tranquilo. Pero lo que nos espera en el cielo es todavía más increíble…"],
     "grandes": {3: "1 VEZ POR SEMANA"}, "extra": 0.8},
    {"titulo": "4. Ríos en el cielo", "escena": esc_vapor, "tarjeta": "CAPÍTULO 4 · RÍOS EN EL CIELO",
     "frases": ["Tuki sube por encima de los árboles, y el aire se llena de una niebla caliente.",
                "Es vapor de agua: los árboles beben del suelo con sus raíces y lo sueltan por sus hojas.",
                "Cada día, la selva entera suelta al aire más de diez mil millones de toneladas de agua.",
                "Ese vapor viaja por el cielo como un río invisible: los científicos lo llaman ríos voladores.",
                "Y así, la selva fabrica buena parte de su propia lluvia."],
     "grandes": {2: "¡10.000 MILLONES!", 3: "RÍOS VOLADORES"}},
    {"titulo": "5. Polvo del desierto", "escena": esc_sahara, "tarjeta": "CAPÍTULO 5 · POLVO DEL DESIERTO",
     "frases": ["Última parada: subimos tan alto que vemos el océano Atlántico… ¡y una nube dorada que viene de África!",
                "Es polvo del desierto del Sahara. El viento lo levanta y lo empuja miles de kilómetros sobre el mar.",
                "Cada año caen sobre la Amazonia unos veintisiete millones de toneladas: ¡más de cien mil camiones llenos!",
                "Y ese polvo trae fósforo, un abono que la lluvia y las inundaciones le roban a la selva.",
                "¡El desierto cálido más grande del mundo ayuda a crecer a la selva tropical más grande del planeta!"],
     "grandes": {2: "100.000 CAMIONES", 4: "¡DESIERTO + SELVA!"}, "extra": 1.2},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje por la selva amazónica.",
                "Si te ha gustado, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
