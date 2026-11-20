"""Episodio: "Viaje a la época de los dinosaurios" con Tico, una máquina del tiempo original.

Datos (verificados el 20-11-2026):
- El estegosaurio vivió hace unos 150 millones de años y el tiranosaurio no apareció hasta hace unos
  67 millones: «Less time separates us from Tyrannosaurus rex than separated T. rex from Stegosaurus»
  (Smithsonian Magazine «On Dinosaur Time»).
- Las crías de saurópodo (como los titanosaurios de los nidos de Auca Mahuevo, Argentina, con 15-40 huevos
  por puesta) pesaban menos de 5 kg, como un ganso, y en unas tres décadas llegaban a adultos 10.000 veces
  más pesados o más (American Museum of Natural History «How did sauropods get so big?», 2011; AMNH
  «Titanosaur nest»).
- El velociraptor era del tamaño de un pavo (unos 30 libras, ~14 kg) y tenía plumas: en un cúbito hallado en
  Mongolia se ven las «quill knobs» donde se anclaban (Turner, Makovicky y Norell, Science 2007; Live Science).
- El asteroide de Chicxulub (de unos 10 km o más; cráter en el Yucatán, México) chocó en primavera del
  hemisferio norte: lo revelan los anillos de crecimiento y los isótopos de huesos de peces fosilizados en
  Tanis (Dakota del Norte), que murieron menos de una hora después del impacto (During et al., Nature 2022;
  Vrije Universiteit Amsterdam; NASA/JPL).
- Las aves son dinosaurios: el colágeno de un hueso de T. rex de 68 millones de años se agrupó con las aves
  (gallina y avestruz) mejor que con ningún otro animal estudiado (Organ, Asara et al., Science 2008;
  Harvard Gazette).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-20-historia"
TITULO = "Viaje a la época de los dinosaurios"
VOZ = "em_alex"
VELOCIDAD = 0.95
MUSICA = 34

W, H = 1920, 1080
rng = np.random.default_rng(20)
ESTRELLAS = [(rng.uniform(0, 1), rng.uniform(0, 2 * math.pi), rng.uniform(2, 5)) for _ in range(60)]
POLVO = [(rng.uniform(0, W), rng.uniform(250, 900), rng.uniform(3, 7), rng.uniform(20, 60)) for _ in range(30)]
CENIZA = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 8), rng.uniform(30, 90)) for _ in range(60)]


def C(sil, col):
    return sil if sil else col


# ================= piezas comunes =================
def cielo(id_, top, bot):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


def nube(x, y, sc, op=1.0, col="#fff"):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def nubes(t, ys=(250, 190, 330), vel=14, col="#fff"):
    s = []
    for i, (cx, sc) in enumerate([(300, 1.2), (1000, 0.9), (1650, 1.0)]):
        x = (cx + t * vel * (1 + i * 0.3)) % 2300 - 300
        s.append(nube(x, ys[i], sc, 0.95, col))
    return "".join(s)


def suelo(y, col, col2=None, t=0.0):
    col2 = col2 or mix(col, "#000000", 0.18)
    return (f"<path d='M0 {y} Q300 {y - 25} 640 {y - 5} T1280 {y - 10} T1920 {y} L1920 1080 L0 1080 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M0 {y + 90} Q320 {y + 65} 700 {y + 85} T1400 {y + 80} T1920 {y + 90} L1920 1080 L0 1080 Z' fill='{col2}'/>")


def helecho(x, y, s, t, col="#4caf50", fase=0.0):
    """Mata de helecho: hojas largas y puntiagudas en abanico que se mecen."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"]
    osc = mix(col, "#000000", 0.25)
    for i, a in enumerate((-62, -35, -10, 14, 40, 64)):
        aa = a + 5 * math.sin(t * 1.3 + i + fase)
        g.append(f"<g transform='rotate({aa:.1f})'>"
                 f"<path d='M0 0 Q-34 -110 0 -230 Q34 -110 0 0 Z' fill='{col if i % 2 else osc}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M0 -10 L0 -215' stroke='{INK}' stroke-width='4'/>"
                 + "".join(f"<path d='M0 {-40 - k * 36} l{-16 + 2 * k} -14 M0 {-40 - k * 36} l{16 - 2 * k} -14' stroke='{INK}' stroke-width='3'/>" for k in range(5))
                 + "</g>")
    g.append("</g>")
    return "".join(g)


def cica(x, y, s, t, col="#3f9a48", tronco="#8d6e4a"):
    """Cícada / palmera prehistórica: tronco con escamas y corona de hojas."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"]
    g.append(f"<path d='M-30 0 Q-38 -150 -18 -300 L18 -300 Q38 -150 30 0 Z' fill='{tronco}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(7):
        yy = -30 - k * 40
        g.append(f"<path d='M{-28 + k} {yy} Q0 {yy - 18} {28 - k} {yy}' fill='none' stroke='{INK}' stroke-width='5'/>")
    for i, a in enumerate((-80, -50, -20, 10, 40, 70, 100, 130)):
        aa = a + 4 * math.sin(t * 1.1 + i) - 25
        g.append(f"<g transform='translate(0,-300) rotate({aa:.1f})'><path d='M0 0 Q90 -40 200 10 Q100 -5 0 0 Z' fill='{col if i % 2 else mix(col, '#000000', 0.2)}' "
                 f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    g.append("</g>")
    return "".join(g)


def conifera(x, y, s, t, col="#2f7d4a"):
    """Araucaria (conífera del Cretácico): tronco alto y pisos de ramas planas."""
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>",
         f"<rect x='-16' y='-420' width='32' height='420' fill='#7a5638' stroke='{INK}' stroke-width='{LW}'/>"]
    for k, (yy, ww) in enumerate(((-420, 90), (-350, 140), (-280, 170), (-210, 190))):
        sw = 4 * math.sin(t * 0.9 + k)
        g.append(f"<path d='M{-ww} {yy + 30 + sw:.0f} Q0 {yy - 40} {ww} {yy + 30 - sw:.0f} Q0 {yy + 10} {-ww} {yy + 30 + sw:.0f} Z' "
                 f"fill='{col if k % 2 else mix(col, '#000000', 0.15)}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def destellos(cx, cy, k, n=10, r=220, col="#fff6a8"):
    if k <= 0 or k >= 1:
        return ""
    s = []
    for i in range(n):
        a = i / n * 2 * math.pi
        d = r * (0.4 + 0.6 * k)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        e = 18 * (1 - k) + 6
        s.append(f"<path d='M{x:.0f} {y - e:.0f} L{x + e * 0.3:.0f} {y:.0f} L{x:.0f} {y + e:.0f} L{x - e * 0.3:.0f} {y:.0f} Z' "
                 f"fill='{col}' stroke='{INK}' stroke-width='2' opacity='{1 - k:.2f}'/>")
    return "".join(s)


def portal(x, y, k, t, r=170):
    """Remolino del tiempo por el que aparece Tico (k de 0 a 1 y vuelta a 0)."""
    if k <= 0.01:
        return ""
    s = [f"<g transform='translate({x:.0f},{y:.0f}) scale({k:.3f})'>"]
    s.append(f"<circle r='{r}' fill='#2b1b5c' opacity='0.85'/>")
    for i, c in enumerate(["#9b5de5", "#00bbf9", "#f15bb5", "#fee440", "#00f5d4"]):
        a = (t * 240 + i * 72) % 360
        rr = r * (1 - i * 0.17)
        s.append(f"<path transform='rotate({a:.0f})' d='M{rr:.0f} 0 A{rr:.0f} {rr:.0f} 0 0 1 {-rr * 0.5:.0f} {rr * 0.87:.0f}' fill='none' "
                 f"stroke='{c}' stroke-width='16' stroke-linecap='round'/>")
    s.append(f"<circle r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/></g>")
    return "".join(s)


def tico(x, y, s, t, vuelo=0.0, guino=False, prisa=1.0, ang=0.0, mira=0.0):
    """Tico: máquina del tiempo redonda turquesa, cúpula de cristal con dos ojos, reloj en la barriga,
    engranajes a los lados y antena con luz. vuelo=1 recoge las patas y enciende el propulsor."""
    parp = 0.12 if (t % 3.9) < 0.13 or guino else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if vuelo < 0.5:
        g.append(f"<ellipse cx='0' cy='4' rx='115' ry='14' fill='#000' opacity='{0.15 * (1 - vuelo * 2):.2f}'/>")
    # propulsor
    if vuelo > 0.01:
        fl = 60 + 25 * math.sin(t * 30)
        g.append(f"<path d='M-34 -40 Q0 {-40 + fl * vuelo * 2:.0f} 34 -40 Z' fill='#ffb703' stroke='{INK}' stroke-width='5' opacity='{vuelo:.2f}'/>"
                 f"<path d='M-18 -40 Q0 {-40 + fl * vuelo * 1.2:.0f} 18 -40 Z' fill='#fff3b0' opacity='{vuelo:.2f}'/>")
    # patas
    lp = 60 * (1 - vuelo)
    for sx in (-1, 1):
        g.append(f"<path d='M{sx * 55} -70 L{sx * 85} {-62 + lp:.0f}' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
                 f"<path d='M{sx * 55} -70 L{sx * 85} {-62 + lp:.0f}' stroke='#9aa3ad' stroke-width='9' stroke-linecap='round'/>"
                 f"<ellipse cx='{sx * 92}' cy='{-60 + lp:.0f}' rx='30' ry='12' fill='#ffb703' stroke='{INK}' stroke-width='6'/>")
    # engranajes laterales
    for sx in (-1, 1):
        a = (t * 90 * prisa * sx) % 360
        dientes = "".join(f"<rect x='-9' y='-46' width='18' height='18' rx='3' fill='#ffb703' stroke='{INK}' stroke-width='4' transform='rotate({k * 45})'/>" for k in range(8))
        g.append(f"<g transform='translate({sx * 102},-135) rotate({a:.0f})'>{dientes}<circle r='34' fill='#ffb703' stroke='{INK}' stroke-width='6'/>"
                 f"<circle r='11' fill='#fff3b0' stroke='{INK}' stroke-width='5'/></g>")
    # cuerpo
    g.append(f"<circle cx='0' cy='-130' r='100' fill='#2ec4b6' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-96 -100 Q0 -70 96 -100' fill='none' stroke='#1f9e93' stroke-width='14' stroke-linecap='round'/>")
    # reloj de la barriga
    g.append(f"<circle cx='0' cy='-108' r='40' fill='#fff8e6' stroke='{INK}' stroke-width='7'/>")
    g.append("".join(f"<line x1='0' y1='-32' x2='0' y2='-25' stroke='{INK}' stroke-width='4' transform='translate(0,-108) rotate({k * 30})'/>" for k in range(12)))
    g.append(f"<line x1='0' y1='0' x2='0' y2='-28' stroke='#e63946' stroke-width='6' stroke-linecap='round' transform='translate(0,-108) rotate({(t * 360 * prisa) % 360:.0f})'/>"
             f"<line x1='0' y1='0' x2='0' y2='-18' stroke='{INK}' stroke-width='7' stroke-linecap='round' transform='translate(0,-108) rotate({(t * 30 * prisa) % 360:.0f})'/>"
             f"<circle cx='0' cy='-108' r='6' fill='{INK}'/>")
    # cúpula con los ojos
    g.append(f"<path d='M-82 -196 Q-82 -300 0 -300 Q82 -300 82 -196 Z' fill='#cdeeff' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-55 -215 Q-55 -270 -15 -282' fill='none' stroke='#fff' stroke-width='9' stroke-linecap='round' opacity='0.8'/>")
    for ex in (-30, 30):
        g.append(f"<g transform='translate({ex + mira * 8:.0f},-240) scale(1,{parp})'><ellipse rx='20' ry='24' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{4 + mira * 6:.0f}' cy='2' r='11' fill='#1e2a38'/><circle cx='{mira * 6:.0f}' cy='-4' r='4' fill='#fff'/></g>")
    g.append(f"<rect x='-90' y='-206' width='180' height='18' rx='9' fill='#ffb703' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-24 -170 Q0 -152 24 -170' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # antena
    luz = 0.5 + 0.5 * math.sin(t * 6)
    g.append(f"<line x1='0' y1='-300' x2='0' y2='-338' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='0' cy='-346' r='20' fill='#ff4d6d' opacity='{0.3 * luz:.2f}'/>"
             f"<circle cx='0' cy='-346' r='12' fill='{mix('#c9184a', '#ff8fa3', luz)}' stroke='{INK}' stroke-width='5'/>")
    g.append("</g>")
    return "".join(g)


# ---------------- dinosaurios y aves ----------------
def estegosaurio(x, y, s, t, dirx=1, sil=None, come=0.0):
    """Estegosaurio de perfil (mira a la derecha): placas en dos filas, cabeza pequeña y baja, 4 pinchos en la cola."""
    cu, pl, pa = C(sil, "#7cb342"), C(sil, "#ff8a3d"), C(sil, "#5f8f2f")
    ink = C(sil, INK)
    cola = 6 * math.sin(t * 1.5)
    cab = 8 * math.sin(t * 2.2) * (1 - come) + 14 * come * abs(math.sin(t * 4))
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if not sil:
        g.append("<ellipse cx='-20' cy='4' rx='330' ry='20' fill='#000' opacity='0.15'/>")
    # patas del fondo
    for lx, ln in ((-150, 0), (130, 0)):
        g.append(f"<path d='M{lx - 10} -150 L{lx - 20} -4 L{lx + 30} -4 L{lx + 35} -150 Z' fill='{pa}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # placas (fila de atrás, más oscuras)
    lomo = [(-300, -165), (-240, -200), (-180, -238), (-115, -268), (-50, -285), (15, -282), (75, -262), (130, -230), (175, -195)]
    alt = [55, 75, 100, 118, 125, 118, 100, 78, 55]
    for i, ((px, py), a) in enumerate(zip(lomo, alt)):
        if i % 2 == 0:
            g.append(f"<path d='M{px - 30} {py + 20} L{px + 6} {py - a} L{px + 36} {py + 20} Z' fill='{C(sil, mix('#ff8a3d', '#000000', 0.25))}' stroke='{ink}' stroke-width='7' stroke-linejoin='round'/>")
    # cola con pinchos
    g.append(f"<g transform='rotate({cola:.1f},-260,-150)'>")
    for sx, sy, a in ((-360, -150, -40), (-395, -140, -60), (-370, -160, 30), (-405, -150, 10)):
        g.append(f"<path d='M{sx - 8} {sy} L{sx - 40 * math.sin(math.radians(a + 30)):.0f} {sy - 70 * math.cos(math.radians(a)):.0f} L{sx + 10} {sy - 4} Z' "
                 f"fill='{C(sil, '#f2efe8')}' stroke='{ink}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<path d='M-200 -200 Q-330 -170 -430 -140 Q-330 -120 -200 -125 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # cuerpo
    g.append(f"<path d='M-260 -140 Q-230 -230 -100 -275 Q20 -305 120 -240 Q190 -190 230 -130 Q170 -95 80 -95 Q-60 -90 -180 -100 Q-240 -105 -260 -140 Z' "
             f"fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if not sil:
        g.append(f"<path d='M-200 -112 Q-40 -88 170 -110' fill='none' stroke='#c5e1a5' stroke-width='16' stroke-linecap='round'/>")
        for k in range(5):
            g.append(f"<circle cx='{-150 + k * 60}' cy='{-190 + (k % 2) * 30}' r='9' fill='#5f8f2f'/>")
    # cuello y cabeza (baja, pequeña)
    g.append(f"<g transform='rotate({cab:.1f},200,-150)'>"
             f"<path d='M180 -190 Q260 -150 300 -95 Q330 -80 360 -80 Q385 -72 380 -55 Q360 -40 320 -48 Q270 -55 230 -100 Q200 -125 170 -130 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             + ("" if sil else f"<circle cx='330' cy='-74' r='8' fill='{INK}'/><circle cx='328' cy='-77' r='3' fill='#fff'/>"
                f"<path d='M345 -54 Q362 -52 376 -58' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
             + "</g>")
    # placas (fila de delante)
    for i, ((px, py), a) in enumerate(zip(lomo, alt)):
        if i % 2 == 1:
            g.append(f"<path d='M{px - 32} {py + 22} L{px} {py - a} L{px + 32} {py + 22} Z' fill='{pl}' stroke='{ink}' stroke-width='7' stroke-linejoin='round'/>")
    # patas de delante
    for lx in (-110, 165):
        alto = 150 if lx < 0 else 110
        g.append(f"<path d='M{lx - 30} {-alto - 20} L{lx - 30} -4 L{lx + 28} -4 L{lx + 30} {-alto - 10} Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
        g.append(f"<path d='M{lx - 36} 0 L{lx + 34} 0' stroke='{ink}' stroke-width='12' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def trex(x, y, s, t, dirx=1, sil=None, boca=0.0, paso=0.0):
    """Tiranosaurio de perfil (mira a la derecha): cabeza enorme, brazos diminutos, cola horizontal."""
    cu, ba, osc = C(sil, "#5f9e57"), C(sil, "#d4e09b"), C(sil, "#467a3f")
    ink = C(sil, INK)
    cola = 5 * math.sin(t * 1.2)
    ang_m = boca * 28
    pz = 18 * math.sin(paso * math.pi * 2)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if not sil:
        g.append("<ellipse cx='0' cy='4' rx='300' ry='20' fill='#000' opacity='0.15'/>")
    # pierna del fondo
    g.append(f"<g transform='rotate({-pz:.1f},-40,-330)'><path d='M-80 -360 Q-10 -380 20 -300 Q20 -220 0 -170 L40 -20 L90 -8 L90 4 L-10 4 L-40 -160 Q-110 -240 -80 -360 Z' fill='{osc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # cola y cuerpo
    g.append(f"<g transform='rotate({cola:.1f},-150,-380)'><path d='M-150 -440 Q-330 -420 -520 -360 Q-330 -330 -150 -330 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    g.append(f"<path d='M-190 -430 Q-60 -480 90 -455 Q170 -440 210 -400 Q230 -330 170 -280 Q80 -240 -40 -260 Q-170 -290 -200 -340 Q-220 -400 -190 -430 Z' "
             f"fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if not sil:
        g.append(f"<path d='M-150 -300 Q20 -250 180 -300' fill='none' stroke='{ba}' stroke-width='22' stroke-linecap='round'/>")
        for k in range(6):
            g.append(f"<path d='M{-160 + k * 50} -440 q12 18 0 36' fill='none' stroke='{osc}' stroke-width='8' stroke-linecap='round'/>")
    # brazo diminuto
    g.append(f"<path d='M160 -320 Q200 -300 205 -270 L222 -262 M205 -270 L208 -250' fill='none' stroke='{ink}' stroke-width='18' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M160 -320 Q200 -300 205 -270' fill='none' stroke='{cu}' stroke-width='9' stroke-linecap='round'/>")
    # cabeza
    hx, hy = 170, -500
    g.append(f"<g transform='translate({hx},{hy})'>")
    g.append(f"<g transform='rotate({ang_m:.1f},20,40)'><path d='M10 40 Q140 40 250 30 Q250 62 205 78 Q100 92 20 80 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             + ("" if sil else "".join(f"<path d='M{60 + k * 32} 38 l10 -18 l10 18' fill='#fff' stroke='{INK}' stroke-width='3'/>" for k in range(6)))
             + "</g>")
    if boca > 0.05 and not sil:
        g.append(f"<path d='M30 45 Q140 50 240 36 L230 {36 + boca * 70:.0f} Q130 {60 + boca * 70:.0f} 30 50 Z' fill='#7a1f2b'/>")
    g.append(f"<path d='M-20 10 Q0 -70 110 -75 Q220 -75 268 -30 Q275 10 262 38 Q150 46 10 50 Q-30 40 -20 10 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if not sil:
        g.append("".join(f"<path d='M{60 + k * 32} 46 l10 20 l10 -20' fill='#fff' stroke='{INK}' stroke-width='3'/>" for k in range(6)))
        parp = 0.15 if (t % 4.3) < 0.14 else 1
        g.append(f"<path d='M60 -52 Q95 -72 130 -52' fill='none' stroke='{osc}' stroke-width='12' stroke-linecap='round'/>"
                 f"<g transform='translate(95,-30) scale(1,{parp})'><circle r='15' fill='#ffd23f' stroke='{INK}' stroke-width='5'/><ellipse rx='4' ry='11' fill='{INK}'/></g>"
                 f"<ellipse cx='240' cy='-25' rx='9' ry='5' fill='{INK}'/>")
    g.append("</g>")
    # cuello (tapa la unión)
    g.append(f"<path d='M120 -440 Q160 -470 190 -470 L230 -430 Q215 -380 190 -360 Z' fill='{cu}'/>")
    # pierna de delante
    g.append(f"<g transform='rotate({pz:.1f},-60,-330)'><path d='M-150 -380 Q-20 -420 20 -320 Q30 -240 -10 -180 L30 -20 L100 -8 L100 4 L-30 4 L-60 -170 Q-170 -250 -150 -380 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    g.append("</g>")
    return "".join(g)


def raptor(x, y, s, t, dirx=1, plumas=1.0, alas=0.0, sil=None, corre=0.0):
    """Velociraptor con plumas (tamaño pavo): cuerpo esbelto, hocico largo, cola rígida con abanico de plumas,
    brazos con plumas y la garra en hoz del segundo dedo levantada. plumas=0 -> versión 'de película' con escamas."""
    pc = mix("#5d8a4e", "#c0703a", plumas) if not sil else sil
    p2 = mix("#476b3b", "#8a4a26", plumas) if not sil else sil
    vi = C(sil, "#f3d6a0")
    ink = C(sil, INK)
    pz = 22 * math.sin(corre * t * 14)
    cab = 6 * math.sin(t * 3)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if not sil:
        g.append("<ellipse cx='0' cy='4' rx='170' ry='14' fill='#000' opacity='0.15'/>")
    # pierna del fondo
    g.append(f"<g transform='rotate({-pz:.1f},-10,-150)'><path d='M-20 -170 L10 -80 L-10 -6 L40 -6 M10 -80 L30 -40' fill='none' stroke='{ink}' stroke-width='20' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M-20 -170 L10 -80 L-10 -6 L40 -6' fill='none' stroke='{p2}' stroke-width='10' stroke-linecap='round' stroke-linejoin='round'/></g>")
    # cola
    g.append(f"<path d='M-60 -190 Q-200 -215 -300 -205 Q-200 -160 -60 -150 Z' fill='{pc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if plumas > 0.3:
        for k in range(6):
            a = -30 + k * 12 + 4 * math.sin(t * 4 + k)
            g.append(f"<g transform='translate(-290,-205) rotate({a:.0f})' opacity='{plumas:.2f}'><path d='M0 0 Q-60 -14 -110 0 Q-60 14 0 0 Z' fill='{p2 if k % 2 else pc}' stroke='{ink}' stroke-width='5'/></g>")
    # cuerpo
    g.append(f"<path d='M-90 -175 Q-60 -240 40 -230 Q100 -220 110 -180 Q100 -120 20 -115 Q-70 -110 -90 -175 Z' fill='{pc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-40 -125 Q30 -110 95 -150' fill='none' stroke='{vi}' stroke-width='14' stroke-linecap='round'/>")
    if plumas > 0.3 and not sil:
        for k in range(4):
            g.append(f"<path d='M{-50 + k * 35} -215 q10 20 -6 34' fill='none' stroke='{p2}' stroke-width='7' stroke-linecap='round' opacity='{plumas:.2f}'/>")
    elif not sil:
        for k in range(10):
            g.append(f"<circle cx='{-60 + (k % 5) * 32}' cy='{-195 + (k // 5) * 28}' r='7' fill='none' stroke='{p2}' stroke-width='4'/>")
    # cuello y cabeza
    g.append(f"<g transform='rotate({cab:.1f},90,-200)'>"
             f"<path d='M60 -215 Q110 -260 120 -300 L170 -300 Q150 -240 110 -170 Z' fill='{pc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M100 -305 Q130 -340 180 -330 Q250 -318 285 -300 Q290 -285 270 -280 Q200 -270 130 -270 Q95 -280 100 -305 Z' fill='{pc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             + ("" if sil else
                f"<path d='M150 -282 Q210 -278 268 -284' fill='none' stroke='{INK}' stroke-width='4'/>"
                + "".join(f"<path d='M{170 + k * 18} -282 l5 9 l5 -9' fill='#fff' stroke='{INK}' stroke-width='2'/>" for k in range(5))
                + f"<g transform='translate(160,-308) scale(1,{0.15 if (t % 3.1) < 0.12 else 1})'><circle r='11' fill='#ffd23f' stroke='{INK}' stroke-width='4'/><circle cx='2' r='5' fill='{INK}'/></g>")
             + (f"<path d='M110 -330 Q90 -370 120 -350 Q115 -380 140 -345' fill='{p2}' stroke='{ink}' stroke-width='5' opacity='{plumas:.2f}'/>" if plumas > 0.3 else "")
             + "</g>")
    # brazo con plumas (ala)
    abre = alas
    g.append(f"<g transform='translate(70,-180) rotate({-20 - 70 * abre:.0f})'>")
    if plumas > 0.3:
        for k in range(5):
            g.append(f"<path d='M{10 + k * 14} 0 Q{-4 + k * 14} {50 + k * 4} {10 + k * 10} {80 + k * 6} Q{24 + k * 14} 40 {22 + k * 14} 0 Z' fill='{p2 if k % 2 else pc}' stroke='{ink}' stroke-width='4' opacity='{plumas:.2f}'/>")
    g.append(f"<path d='M0 0 L70 10 L95 30' fill='none' stroke='{ink}' stroke-width='16' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M0 0 L70 10 L95 30' fill='none' stroke='{pc}' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M95 30 l14 14 M95 30 l2 20' stroke='{ink}' stroke-width='5' stroke-linecap='round'/></g>")
    # pierna de delante con la garra en hoz
    g.append(f"<g transform='rotate({pz:.1f},10,-150)'><path d='M-10 -175 Q50 -170 40 -120 L60 -70 L50 -6 L105 -6' fill='none' stroke='{ink}' stroke-width='24' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M-10 -175 Q50 -170 40 -120 L60 -70 L50 -6 L105 -6' fill='none' stroke='{pc}' stroke-width='13' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='M62 -8 Q70 -45 95 -40 Q80 -30 74 -6 Z' fill='{C(sil, '#f2efe8')}' stroke='{ink}' stroke-width='5'/></g>")
    g.append("</g>")
    return "".join(g)


def titanosaurio(x, y, s, t, dirx=1, sil=None, cuello=0.0):
    """Titanosaurio adulto (mira a la izquierda si dirx=-1): patas como columnas, cuello larguísimo, cola larga."""
    cu, osc, ba = C(sil, "#b98b5e"), C(sil, "#94693f"), C(sil, "#e3c8a0")
    ink = C(sil, INK)
    cn = 4 * math.sin(t * 0.8) + cuello
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if not sil:
        g.append("<ellipse cx='-40' cy='4' rx='380' ry='24' fill='#000' opacity='0.16'/>")
    for lx in (-200, 160):
        g.append(f"<path d='M{lx - 45} -260 L{lx - 50} 0 L{lx + 45} 0 L{lx + 50} -260 Z' fill='{osc}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cola
    g.append(f"<path d='M-280 -420 Q-500 -380 -720 -220 Q-480 -300 -260 -290 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cuello y cabeza
    g.append(f"<g transform='rotate({cn:.1f},250,-440)'>"
             f"<path d='M200 -480 Q360 -560 440 -780 Q470 -860 520 -880 L560 -850 Q510 -800 480 -720 Q420 -520 300 -340 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M500 -900 Q560 -920 610 -890 Q630 -870 615 -852 Q570 -840 520 -850 Q490 -870 500 -900 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
             + ("" if sil else
                f"<g transform='translate(545,-885) scale(1,{0.15 if (t % 4.7) < 0.14 else 1})'><circle r='10' fill='{INK}'/><circle cx='-3' cy='-3' r='3' fill='#fff'/></g>"
                f"<path d='M585 -858 Q600 -856 612 -862' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>"
                + "".join(f"<path d='M{300 + k * 40} {-470 - k * 70} q20 -6 30 6' fill='none' stroke='{osc}' stroke-width='7' stroke-linecap='round'/>" for k in range(5)))
             + "</g>")
    # cuerpo
    g.append(f"<path d='M-320 -380 Q-250 -560 20 -570 Q260 -560 330 -400 Q320 -260 80 -240 Q-160 -230 -300 -280 Q-340 -320 -320 -380 Z' "
             f"fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    if not sil:
        g.append(f"<path d='M-250 -275 Q40 -230 300 -300' fill='none' stroke='{ba}' stroke-width='22' stroke-linecap='round'/>")
        for k in range(7):
            g.append(f"<circle cx='{-200 + k * 70}' cy='{-470 + (k % 2) * 40}' r='16' fill='{osc}' stroke='{INK}' stroke-width='4'/>")
    for lx in (-130, 230):
        g.append(f"<path d='M{lx - 50} -300 L{lx - 55} 0 L{lx + 50} 0 L{lx + 55} -300 Z' fill='{cu}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 f"<path d='M{lx - 40} -8 l0 -14 M{lx} -8 l0 -14 M{lx + 40} -8 l0 -14' stroke='{ink}' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def cria(x, y, s, t, dirx=1, sil=None):
    """Cría de titanosaurio: cabezona, cuello corto y patitas."""
    cu, osc = C(sil, "#c9a074"), C(sil, "#a27a4f")
    ink = C(sil, INK)
    cab = 8 * math.sin(t * 2.5)
    parp = 0.15 if (t % 2.9) < 0.13 else 1
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"
            f"<path d='M-60 -50 Q-140 -40 -175 -10 Q-120 -22 -60 -25 Z' fill='{cu}' stroke='{ink}' stroke-width='7' stroke-linejoin='round'/>"
            f"<rect x='-55' y='-50' width='26' height='50' rx='8' fill='{osc}' stroke='{ink}' stroke-width='6'/>"
            f"<rect x='30' y='-50' width='26' height='50' rx='8' fill='{osc}' stroke='{ink}' stroke-width='6'/>"
            f"<ellipse cx='0' cy='-70' rx='80' ry='45' fill='{cu}' stroke='{ink}' stroke-width='{LW}'/>"
            f"<g transform='rotate({cab:.1f},50,-90)'><path d='M40 -100 Q70 -150 90 -170 L120 -160 Q100 -130 80 -80 Z' fill='{cu}' stroke='{ink}' stroke-width='7' stroke-linejoin='round'/>"
            f"<ellipse cx='118' cy='-180' rx='44' ry='32' fill='{cu}' stroke='{ink}' stroke-width='{LW}'/>"
            + ("" if sil else f"<g transform='translate(125,-190) scale(1,{parp})'><circle r='12' fill='#fff' stroke='{INK}' stroke-width='4'/><circle cx='3' r='7' fill='{INK}'/><circle cx='0' cy='-3' r='2.5' fill='#fff'/></g>"
               f"<path d='M135 -165 Q148 -162 158 -170' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
            + "</g>"
            f"<rect x='-30' y='-45' width='26' height='45' rx='8' fill='{cu}' stroke='{ink}' stroke-width='6'/>"
            f"<rect x='52' y='-45' width='26' height='45' rx='8' fill='{cu}' stroke='{ink}' stroke-width='6'/></g>")


def huevo(x, y, r, t=0.0, tiembla=0.0, roto=0.0, col="#efe3c8"):
    sh = tiembla * 8 * math.sin(t * 40)
    g = [f"<g transform='translate({x + sh:.1f},{y:.1f})'>"]
    if roto <= 0:
        g.append(f"<circle cx='0' cy='{-r}' r='{r}' fill='{col}' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='{-r * 0.35:.0f}' cy='{-r * 1.35:.0f}' r='{r * 0.18:.0f}' fill='#fff' opacity='0.7'/>"
                 f"<circle cx='{r * 0.3:.0f}' cy='{-r * 0.7:.0f}' r='5' fill='#c9b48e'/><circle cx='{-r * 0.2:.0f}' cy='{-r * 0.5:.0f}' r='4' fill='#c9b48e'/>")
        if tiembla > 0.3:
            g.append(f"<path d='M{-r * 0.6:.0f} {-r:.0f} l18 -14 l14 16 l16 -18 l14 14' fill='none' stroke='{INK}' stroke-width='5'/>")
    else:
        dy = -60 * roto
        g.append(f"<path d='M{-r} {-r} A{r} {r} 0 0 0 {r} {-r} l-14 -14 l-16 16 l-16 -18 l-14 16 l-16 -14 l-14 14 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<g transform='translate({-40 * roto:.0f},{dy:.0f}) rotate({-40 * roto:.0f})' opacity='{1 - roto * 0.6:.2f}'>"
                 f"<path d='M{-r} {-r} A{r} {r} 0 0 1 {r} {-r} l-14 14 l-16 -16 l-16 18 l-14 -16 l-16 14 l-14 -14 Z' transform='translate(0,{-r * 0.2:.0f})' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    g.append("</g>")
    return "".join(g)


def paloma(x, y, s, t, dirx=1, picotea=0.0, vuela=0.0, sil=None):
    """Paloma gris con cuello verde-violeta tornasolado. picotea: baja la cabeza; vuela: abre las alas."""
    cu, ala, cue = C(sil, "#a7b0bf"), C(sil, "#7f8a9c"), C(sil, "#4f9d8a")
    ink = C(sil, INK)
    pk = picotea * max(0, math.sin(t * 7)) * 40
    al = vuela * (30 + 40 * math.sin(t * 22))
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if vuela < 0.3 and not sil:
        g.append("<ellipse cx='0' cy='4' rx='70' ry='9' fill='#000' opacity='0.15'/>")
    if vuela < 0.5:
        g.append(f"<path d='M-10 -40 L-14 -4 L-2 -4 M14 -40 L12 -4 L26 -4' fill='none' stroke='{C(sil, '#e5636b')}' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/>")
    g.append(f"<path d='M-60 -80 L-120 -70 L-110 -55 Z' fill='{ala}' stroke='{ink}' stroke-width='6' stroke-linejoin='round'/>")
    g.append(f"<ellipse cx='0' cy='-70' rx='66' ry='40' fill='{cu}' stroke='{ink}' stroke-width='{LW}'/>")
    g.append(f"<g transform='rotate({-al:.0f},-10,-85)'><path d='M-10 -85 Q-60 -100 -95 -70 Q-40 -50 20 -62 Z' fill='{ala}' stroke='{ink}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M-50 -72 l20 -6 M-70 -68 l20 -6' stroke='{C(sil, '#3a3f4a')}' stroke-width='6' stroke-linecap='round'/></g>")
    g.append(f"<g transform='rotate({pk:.0f},40,-90)'>"
             f"<path d='M20 -90 Q40 -130 60 -128 Q80 -110 60 -70 Z' fill='{cue}' stroke='{ink}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M38 -100 Q55 -95 62 -80' fill='none' stroke='{C(sil, '#8e6bbf')}' stroke-width='8' stroke-linecap='round'/>"
             f"<circle cx='58' cy='-135' r='24' fill='{cu}' stroke='{ink}' stroke-width='6'/>"
             f"<path d='M78 -140 L98 -132 L78 -127 Z' fill='{C(sil, '#3a3f4a')}' stroke='{ink}' stroke-width='3'/>"
             + ("" if sil else f"<circle cx='64' cy='-140' r='6' fill='#ff8c1a' stroke='{INK}' stroke-width='3'/><circle cx='65' cy='-140' r='2.5' fill='{INK}'/>")
             + "</g></g>")
    return "".join(g)


def gallina(x, y, s, t, dirx=1):
    """Gallina blanca con cresta roja."""
    cab = 5 * math.sin(t * 3)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"
            "<ellipse cx='0' cy='4' rx='80' ry='10' fill='#000' opacity='0.15'/>"
            f"<path d='M-8 -50 L-12 -4 L4 -4 M18 -50 L16 -4 L32 -4' fill='none' stroke='#f4a300' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M-60 -100 Q-110 -170 -70 -175 Q-60 -140 -40 -120 Z' fill='#f7f3ea' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<path d='M-70 -100 Q-80 -40 0 -40 Q70 -40 70 -90 Q50 -130 0 -120 Q-40 -130 -70 -100 Z' fill='#fbf8f0' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-30 -90 Q0 -60 30 -88' fill='none' stroke='#d9d2c2' stroke-width='8' stroke-linecap='round'/>"
            f"<g transform='rotate({cab:.1f},40,-110)'>"
            f"<path d='M30 -110 Q30 -170 60 -175 Q90 -170 85 -120 Z' fill='#fbf8f0' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M45 -172 Q48 -198 60 -186 Q66 -206 76 -188 Q90 -196 84 -170 Z' fill='#e63946' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
            f"<path d='M84 -150 L104 -144 L84 -136 Z' fill='#f4a300' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<path d='M80 -134 Q90 -118 78 -114 Q72 -124 76 -134 Z' fill='#e63946' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='68' cy='-152' r='6' fill='{INK}'/></g></g>")


def avestruz(x, y, s, t, dirx=1):
    cab = 5 * math.sin(t * 2)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s * dirx:.3f},{s:.3f})'>"
            "<ellipse cx='0' cy='4' rx='90' ry='10' fill='#000' opacity='0.15'/>"
            f"<path d='M-20 -150 L-30 -4 L-5 -4 M20 -150 L25 -4 L50 -4' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M-20 -150 L-30 -4 L-5 -4 M20 -150 L25 -4 L50 -4' fill='none' stroke='#f2b8a0' stroke-width='11' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M-100 -200 Q-120 -260 -40 -270 Q60 -280 80 -220 Q70 -150 0 -145 Q-80 -145 -100 -200 Z' fill='#3b3434' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-110 -210 Q-150 -240 -130 -260 Q-100 -230 -90 -225 Z' fill='#f7f3ea' stroke='{INK}' stroke-width='6'/>"
            f"<g transform='rotate({cab:.1f},60,-240)'>"
            f"<path d='M50 -250 Q60 -350 70 -420 L92 -420 Q85 -340 80 -240 Z' fill='#f2b8a0' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<ellipse cx='88' cy='-432' rx='30' ry='22' fill='#f2b8a0' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M112 -436 L140 -428 L112 -420 Z' fill='#e8a07a' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='94' cy='-438' r='7' fill='{INK}'/><circle cx='92' cy='-440' r='2.5' fill='#fff'/></g></g>")


def persona(x, y, s, col="#ff6b9a"):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M-30 0 L-22 -70 M30 0 L22 -70' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
            f"<path d='M-40 -60 Q-45 -140 0 -145 Q45 -140 40 -60 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='-180' r='36' fill='#f6c9a0' stroke='{INK}' stroke-width='7'/>"
            f"<path d='M-36 -190 Q-30 -225 0 -222 Q34 -225 36 -190 Q20 -205 -36 -190 Z' fill='#5a3a22' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='-12' cy='-178' r='4' fill='{INK}'/><circle cx='12' cy='-178' r='4' fill='{INK}'/>"
            f"<path d='M-10 -163 Q0 -155 10 -163' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/></g>")


def asteroide(x, y, r, t, cola=1.0, dx=-1.0, dy=0.6):
    """Roca con cráteres y estela de fuego en la dirección opuesta al movimiento."""
    n = math.hypot(dx, dy); ux, uy = -dx / n, -dy / n
    px, py = -uy, ux
    L = r * 5 * cola
    s = []
    for k, (c, w) in enumerate((("#ff7b00", 1.0), ("#ffb703", 0.7), ("#fff3b0", 0.4))):
        ww = r * w
        s.append(f"<path d='M{x + px * ww:.0f} {y + py * ww:.0f} L{x + ux * L * w:.0f} {y + uy * L * w:.0f} L{x - px * ww:.0f} {y - py * ww:.0f} Z' fill='{c}' opacity='0.9'/>")
    rot = (t * 40) % 360
    s.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({rot:.0f})'>"
             f"<path d='M{-r} 0 Q{-r} {-r * 0.9:.0f} {-r * 0.1:.0f} {-r} Q{r * 0.9:.0f} {-r * 1.05:.0f} {r} {-r * 0.1:.0f} Q{r * 1.05:.0f} {r * 0.8:.0f} 0 {r} Q{-r * 0.95:.0f} {r * 0.95:.0f} {-r} 0 Z' "
             f"fill='#7a6a5e' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<circle cx='{-r * 0.3:.0f}' cy='{-r * 0.3:.0f}' r='{r * 0.25:.0f}' fill='#5e5048' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='{r * 0.4:.0f}' cy='{r * 0.25:.0f}' r='{r * 0.18:.0f}' fill='#5e5048' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='{-r * 0.2:.0f}' cy='{r * 0.5:.0f}' r='{r * 0.1:.0f}' fill='#5e5048'/></g>")
    return "".join(s)


def lupa(x, y, r, contenido, op=1.0):
    return (f"<g opacity='{op:.2f}'><defs><clipPath id='lupa'><circle cx='{x:.0f}' cy='{y:.0f}' r='{r}'/></clipPath></defs>"
            f"<path d='M{x + r * 0.7:.0f} {y + r * 0.7:.0f} L{x + r * 1.25:.0f} {y + r * 1.25:.0f}' stroke='{INK}' stroke-width='50' stroke-linecap='round'/>"
            f"<path d='M{x + r * 0.72:.0f} {y + r * 0.72:.0f} L{x + r * 1.22:.0f} {y + r * 1.22:.0f}' stroke='#8d5a3b' stroke-width='34' stroke-linecap='round'/>"
            f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r}' fill='#fff8e6'/>"
            f"<g clip-path='url(#lupa)'>{contenido}</g>"
            f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r}' fill='none' stroke='#c9ced6' stroke-width='22'/>"
            f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r + 11}' fill='none' stroke='{INK}' stroke-width='{LW}'/></g>")


def flor(x, y, s, col="#ff7eb6"):
    if s <= 0.01:
        return ""
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<path d='M0 0 L0 -60' stroke='#3f9a48' stroke-width='8'/>"
            f"<path d='M0 -30 Q-26 -40 -30 -20 Q-10 -18 0 -30 Z' fill='#5cbf60' stroke='{INK}' stroke-width='4'/>"
            + "".join(f"<circle cx='{18 * math.cos(a):.0f}' cy='{-60 + 18 * math.sin(a):.0f}' r='14' fill='{col}' stroke='{INK}' stroke-width='4'/>" for a in [k * 2 * math.pi / 5 for k in range(5)])
            + f"<circle cx='0' cy='-60' r='11' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")


# ================= capítulos =================
def esc_intro(t, dur, m):
    """Túnel del tiempo: anillos de colores que vienen hacia nosotros y siluetas que pasan girando."""
    cx, cy = 960, 560
    vel = 1 + 2.5 * seg(t, m[3] + 1.2, m[3] + 2.5)
    tt = t * 0.45 * vel + t * 0.2
    s = ["<defs><radialGradient id='tun' cx='0.5' cy='0.52' r='0.7'><stop offset='0' stop-color='#ffffff'/>"
         "<stop offset='0.08' stop-color='#ffe066'/><stop offset='0.3' stop-color='#7b2ff7'/><stop offset='1' stop-color='#14072e'/></radialGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#tun)'/>"]
    cols = ["#f15bb5", "#00bbf9", "#fee440", "#00f5d4", "#9b5de5", "#ff8a3d"]
    for i in range(14):
        k = (tt + i / 14) % 1
        r = 30 + (k ** 2.2) * 1500
        s.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{r:.0f}' ry='{r * 0.62:.0f}' fill='none' stroke='{cols[i % 6]}' "
                 f"stroke-width='{4 + 40 * k:.0f}' opacity='{min(1, k * 3) * 0.75:.2f}' transform='rotate({(t * 25 + i * 9) % 360:.0f},{cx},{cy})'/>")
    for k0, a, w in ESTRELLAS:
        k = (k0 + tt * 1.3) % 1
        d1, d2 = 60 + k ** 2 * 1300, 60 + (k ** 2) * 1300 + 30 + 160 * k
        s.append(f"<line x1='{cx + d1 * math.cos(a):.0f}' y1='{cy + d1 * math.sin(a) * 0.62:.0f}' x2='{cx + d2 * math.cos(a):.0f}' "
                 f"y2='{cy + d2 * math.sin(a) * 0.62:.0f}' stroke='#fff' stroke-width='{w:.1f}' stroke-linecap='round' opacity='{min(1, k * 2):.2f}'/>")
    # siluetas que salen del túnel girando: paloma (frase 0), estegosaurio, tiranosaurio
    for (ini, f, sc, ang0) in ((0.0, "paloma", 1.6, 1), (m[1] - 0.3, "trex", 0.7, -1), (m[2] + 1.0, "estego", 0.65, 1), (m[3] - 0.5, "raptor", 1.1, -1)):
        k = (t - ini) / 3.2
        if 0 <= k <= 1:
            esc = 0.15 + 1.1 * k ** 1.6
            ang = ang0 * (25 * k)
            x = cx + ang0 * 900 * k ** 1.5
            y = cy - 280 * k ** 1.3 + (360 * k if f == "estego" else 0)
            sil = "#2a1458"
            if f == "paloma":
                d = paloma(0, 0, sc, t, vuela=1.0)
                x = lerp(-150, 2100, clamp(t / 4.2)); y = 380 + 60 * math.sin(t * 2.5); ang = 0; esc = 1
                k = t / 4.2
            elif f == "trex":
                d = trex(0, 0, sc, t, sil=sil)
            elif f == "estego":
                d = estegosaurio(0, 0, sc, t, sil=sil)
            else:
                d = raptor(0, 0, sc, t, sil=sil)
            s.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({esc:.3f})' opacity='{min(1, k * 4) * min(1, (1 - k) * 4):.2f}'>{d}</g>")
    # Tico en el centro
    ap = seg(t, 0, 1.2)
    tx = cx - 40 + 30 * math.sin(t * 1.3)
    ty = 760 + 18 * math.sin(t * 2.1) + lerp(300, 0, ap)
    sc = 0.95 * (1 - 0.6 * seg(t, dur - 1.2, dur))
    s.append(tico(tx, ty - seg(t, dur - 1.2, dur) * 200, sc, t, vuelo=1.0, guino=(m[2] + 1.6 < t < m[2] + 2.0),
                  prisa=vel * 2, ang=6 * math.sin(t * 1.7)))
    fl = seg(t, dur - 0.6, dur)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff' opacity='{fl:.2f}'/>")
    return "".join(s)


def selva_jurasica(t):
    s = [cielo("cj", "#ffcf8a", "#fff1c9"),
         f"<circle cx='1560' cy='250' r='90' fill='#fff3b0' stroke='{INK}' stroke-width='{LW}'/>"]
    # volcán lejano con humo
    s.append(f"<path d='M180 760 L420 430 L470 430 L760 760 Z' fill='#b07a5a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<path d='M420 430 L470 430 L455 470 L440 455 L428 475 Z' fill='#ff6b35' stroke='{INK}' stroke-width='5'/>")
    for i in range(5):
        k = (t * 0.15 + i / 5) % 1
        s.append(f"<circle cx='{445 + 60 * k + 20 * math.sin(k * 6):.0f}' cy='{410 - k * 300:.0f}' r='{25 + k * 60:.0f}' fill='#8a7a74' opacity='{0.6 * (1 - k):.2f}'/>")
    s.append(nubes(t, (200, 150, 300), 10))
    s.append(f"<path d='M0 720 Q200 650 420 700 T900 690 T1400 700 T1920 680 L1920 800 L0 800 Z' fill='#7fae5a' stroke='{INK}' stroke-width='6'/>")
    s.append(suelo(800, "#8fbf5a", "#6f9d45", t))
    s.append(cica(150, 820, 1.0, t))
    s.append(cica(1780, 830, 1.15, t + 1))
    s.append(cica(1380, 760, 0.6, t + 2))
    return "".join(s)


def esc_estego(t, dur, m):
    s = [selva_jurasica(t)]
    # Tico aparece por un remolino
    k_p = seg(t, 0.0, 0.6) * (1 - seg(t, 1.6, 2.2))
    s.append(portal(360, 650, k_p, t))
    tico_on = seg(t, 0.6, 1.4)
    # estegosaurio que entra caminando y come helechos
    ex = lerp(2300, 1080, seg(t, 0, m[1] + 0.5))
    linea = seg(t, m[2] + 0.2, m[2] + 1.2)
    estego = estegosaurio(ex, 860, 0.95, t, dirx=-1, come=seg(t, m[1] + 0.5, m[1] + 1.2) * (1 - linea))
    s.append(f"<g opacity='{1 - 0.75 * linea:.2f}'>{estego}</g>")
    s.append(helecho(600, 900, 0.6, t))
    s.append(helecho(1500, 900, 0.9, t, "#5cbf60", 1))
    s.append(tico(360, 880 + 8 * math.sin(t * 2) * (1 - tico_on), 0.6 * tico_on + 0.01, t, vuelo=1 - seg(t, 1.0, 1.8), mira=1))
    # panel de la línea del tiempo (frase 2 en adelante)
    if linea > 0:
        y0 = 470
        s.append(f"<g opacity='{linea:.2f}' transform='translate(960,{y0 + 180}) scale({0.85 + 0.15 * ease(linea):.3f}) translate(-960,{-(y0 + 180)})'>")
        s.append(f"<rect x='250' y='{y0}' width='1420' height='380' rx='40' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}'/>")
        xa, xb, xc, yl = 380, 380 + 1160 * 83 / 150, 1540, y0 + 300
        s.append(f"<line x1='{xa}' y1='{yl}' x2='{xc}' y2='{yl}' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        k1 = seg(t, m[3], m[3] + 2.0); k2 = seg(t, m[4] + 0.2, m[4] + 1.8)
        if k1 > 0:
            s.append(f"<rect x='{xa}' y='{yl - 22}' width='{(xb - xa) * k1:.0f}' height='44' rx='22' fill='#ff8a3d' stroke='{INK}' stroke-width='6'/>")
        if k2 > 0:
            s.append(f"<rect x='{xc - (xc - xb) * k2:.0f}' y='{yl - 22}' width='{(xc - xb) * k2:.0f}' height='44' rx='22' fill='#3a8dff' stroke='{INK}' stroke-width='6'/>")
        for x_ in (xa, xb, xc):
            s.append(f"<circle cx='{x_:.0f}' cy='{yl}' r='20' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
        s.append(estegosaurio(xa + 10, yl - 40, 0.28, t, dirx=1))
        rex = 1 + 0.12 * math.sin(t * 8) * seg(t, m[4], m[4] + 0.5) * (1 - seg(t, m[4] + 2, m[4] + 2.5))
        s.append(trex(xb - 10, yl - 40, 0.36 * rex, t, dirx=-1, boca=0.4 * seg(t, m[2], m[2] + 1)))
        s.append(persona(xc, yl - 40, 0.95))
        s.append("</g>")
        s.append(destellos(1100, yl if False else y0 + 300, seg(t, m[4] + 1.8, m[4] + 3.6), 14, 520, "#ffffff"))
    return "".join(s)


def esc_titano(t, dur, m):
    s = [cielo("ca", "#8fd3ff", "#e8f7ff"),
         f"<circle cx='300' cy='230' r='80' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>",
         nubes(t, (180, 260, 150), 12),
         f"<path d='M0 700 L250 560 L420 650 L700 520 L950 660 L1250 540 L1550 640 L1920 560 L1920 800 L0 800 Z' fill='#c9a27a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>",
         suelo(800, "#d9b98a", "#c39d6c", t),
         conifera(170, 820, 0.9, t), conifera(1240, 790, 0.55, t + 1)]
    # temblor del suelo cuando llega la madre
    llega = seg(t, m[3] - 0.4, m[3] + 2.6)
    tiembla = 6 * math.sin(t * 30) * (seg(t, m[3] - 0.4, m[3]) * (1 - seg(t, m[3] + 2.6, m[3] + 3.2)))
    s.append(f"<g transform='translate(0,{tiembla:.1f})'>")
    s.append(titanosaurio(lerp(2700, 1840, llega), 900, 0.78, t, dirx=-1, cuello=lerp(-10, 36, llega)))
    s.append("</g>")
    # nido con huevos
    nx, ny = 760, 880
    s.append(f"<ellipse cx='{nx}' cy='{ny}' rx='260' ry='46' fill='#a57c4f' stroke='{INK}' stroke-width='{LW}'/>"
             f"<ellipse cx='{nx}' cy='{ny - 6}' rx='220' ry='30' fill='#7d5a36'/>")
    rompe = seg(t, m[2] + 0.8, m[2] + 1.6)
    for i, (dx, r) in enumerate(((-150, 44), (-60, 48), (40, 46), (130, 44), (-100, 40), (90, 40))):
        if i < 4:
            if i == 2:
                if rompe < 1:
                    s.append(huevo(nx + dx, ny - 12, r, t, tiembla=seg(t, m[2], m[2] + 0.3), roto=rompe))
                else:
                    s.append(huevo(nx + dx, ny - 12, r, t, roto=1))
            else:
                s.append(huevo(nx + dx, ny - 12, r, t))
    # la cría
    sale = seg(t, m[2] + 1.0, m[2] + 2.4)
    if sale > 0:
        crece = seg(t, m[4] + 0.2, m[4] + 3.2)
        cx_ = nx + 40 + lerp(0, 160, seg(t, m[2] + 2.4, m[3] + 0.5))
        s.append(cria(cx_, ny - 10 - 40 * (1 - sale), 0.9 * sale, t, dirx=1))
        if crece > 0:
            # silueta de la cría que crece hasta el tamaño de un adulto
            g = 0.9 + 2.6 * crece
            s.append(f"<g opacity='{0.6 * (1 - seg(t, m[4] + 3.6, m[4] + 4.4)):.2f}'>"
                     f"{cria(cx_ - 60 * crece, ny - 10, g, t, dirx=1, sil='#fff3b0')}</g>")
            s.append(destellos(cx_ + 120, ny - 300, seg(t, m[4] + 2.8, m[4] + 4.4), 12, 380))
    s.append(tico(360, 900, 0.55, t, vuelo=1 - seg(t, 0.6, 1.5), mira=1, guino=(m[2] + 2.6 < t < m[2] + 3.0)))
    s.append(portal(360, 680, seg(t, 0, 0.5) * (1 - seg(t, 1.4, 2.0)), t))
    return "".join(s)


ROCA = ("<path d='M1180 900 Q1190 780 1310 760 Q1460 760 1480 900 Z' fill='#c76a45' stroke='" + INK + "' stroke-width='9' stroke-linejoin='round'/>"
        "<path d='M1240 860 Q1300 820 1360 840' fill='none' stroke='#a5502f' stroke-width='9' stroke-linecap='round'/>")


def esc_raptor(t, dur, m):
    s = [cielo("cm", "#ffb36b", "#ffe8b8"),
         f"<circle cx='1500' cy='240' r='85' fill='#fff3b0' stroke='{INK}' stroke-width='{LW}'/>",
         f"<path d='M0 640 L120 470 L330 470 L420 560 L600 540 L690 640 Z' fill='#d9603b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M130 520 L320 520 M160 580 L380 590' stroke='#b4462a' stroke-width='9' stroke-linecap='round'/>",
         f"<path d='M1300 650 L1400 520 L1640 500 L1760 590 L1920 560 L1920 700 Z' fill='#e0724a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M0 720 Q400 640 800 700 T1600 690 T1920 700 L1920 820 L0 820 Z' fill='#f2b866' stroke='{INK}' stroke-width='6'/>",
         suelo(820, "#f5c77e", "#e2a95c", t)]
    for x, y, r, v in POLVO:
        xx = (x + t * v) % W
        s.append(f"<circle cx='{xx:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff1d0' opacity='0.5'/>")
    # roca de la que sale
    salta = seg(t, m[1] + 0.3, m[1] + 1.3)
    rx = 1250
    # imaginado: silueta enorme con escamas en un bocadillo (frase 2) que se encoge (frase 3)
    imag = seg(t, m[2] - 0.2, m[2] + 0.6) * (1 - seg(t, m[3] - 0.2, m[3] + 0.5))
    real = salta
    alas = seg(t, m[4] + 0.3, m[4] + 1.0) * (1 - seg(t, m[4] + 3.8, m[4] + 4.6))
    if imag > 0:
        s.append(f"<g opacity='{imag:.2f}'>"
                 f"<circle cx='1020' cy='600' r='16' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='1070' cy='560' r='24' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<ellipse cx='1400' cy='520' rx='330' ry='200' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>"
                 f"{raptor(1400, 670, 1.0, t, dirx=-1, plumas=0.0)}</g>")
    pv = seg(t, m[3] + 0.3, m[3] + 1.0) * (1 - seg(t, m[4] - 0.2, m[4] + 0.4))
    sh_ = 5 * math.sin(t * 40) * seg(t, m[1] - 0.6, m[1] - 0.2) * (1 - seg(t, m[1] + 0.2, m[1] + 0.4))
    s.append(f"<g transform='translate({sh_:.1f},0)'>" + ROCA + helecho(1390, 905, 0.4, t, "#8a9a4a") + "</g>")
    if real > 0:
        ry = 880 - 160 * math.sin(math.pi * salta) * (salta < 1)
        xx = lerp(rx + 60, 900, salta) + (0 if alas else 10 * math.sin(t * 2))
        s.append(raptor(xx, ry, 0.95, t, dirx=-1, plumas=1.0, alas=alas, corre=0.0))
        if pv > 0:   # pavo para comparar el tamaño
            s.append(f"<g opacity='{pv:.2f}'>{pavo(1250, 900, 1.0, t)}</g>")
        if alas > 0:
            for i in range(8):
                k = ((t - m[4]) * 0.4 + i / 8) % 1
                fx = xx - 60 + 220 * math.sin(i * 1.9) ; fy = 650 - k * 300
                s.append(f"<g transform='translate({fx:.0f},{fy:.0f}) rotate({(t * 90 + i * 45) % 360:.0f})' opacity='{alas * (1 - k):.2f}'>"
                         f"<path d='M0 -26 Q14 0 0 26 Q-14 0 0 -26 Z' fill='#c0703a' stroke='{INK}' stroke-width='4'/><path d='M0 -26 L0 30' stroke='{INK}' stroke-width='3'/></g>")
            s.append(destellos(xx, 620, seg(t, m[4] + 0.4, m[4] + 2.2), 12, 300))
    # la roca tiembla antes de que salga
    s.append(tico(380, 900, 0.58, t, vuelo=1 - seg(t, 0.6, 1.5), mira=1))
    s.append(portal(380, 680, seg(t, 0, 0.5) * (1 - seg(t, 1.4, 2.0)), t))
    return "".join(s)


def pavo(x, y, s, t):
    cab = 4 * math.sin(t * 3)
    cola = "".join(f"<g transform='translate(-40,-110) rotate({-80 + k * 20})'><path d='M0 0 Q-20 -90 0 -120 Q20 -90 0 0 Z' fill='{['#8a5a32', '#b07a45', '#6b4423'][k % 3]}' stroke='{INK}' stroke-width='5'/>"
                   f"<path d='M-12 -100 Q0 -112 12 -100' fill='none' stroke='#f2efe8' stroke-width='6'/></g>" for k in range(7))
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            "<ellipse cx='0' cy='4' rx='90' ry='10' fill='#000' opacity='0.15'/>"
            f"{cola}"
            f"<path d='M-10 -50 L-14 -4 L2 -4 M20 -50 L18 -4 L34 -4' fill='none' stroke='#d9883a' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<ellipse cx='0' cy='-95' rx='75' ry='55' fill='#6b4423' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M-40 -100 Q0 -70 50 -95' fill='none' stroke='#8a5a32' stroke-width='10' stroke-linecap='round'/>"
            f"<g transform='rotate({cab:.1f},50,-130)'>"
            f"<path d='M40 -120 Q50 -180 70 -190 L90 -180 Q75 -150 70 -110 Z' fill='#9fc6e8' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
            f"<circle cx='82' cy='-192' r='20' fill='#9fc6e8' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M100 -195 L116 -190 L100 -184 Z' fill='#e8c07a' stroke='{INK}' stroke-width='3'/>"
            f"<path d='M100 -186 Q110 -160 98 -150 Q92 -165 96 -184 Z' fill='#e63946' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='86' cy='-196' r='5' fill='{INK}'/></g></g>")


def esc_asteroide(t, dur, m):
    imp = m[2] + 0.6              # momento del choque
    luz = seg(t, m[1], imp)
    tras = seg(t, imp + 0.2, imp + 2.5)
    fosil = seg(t, m[3] - 0.4, m[3] + 0.6)
    s = []
    if fosil < 1:
        top = mix(mix("#9ad7ff", "#ffb36b", luz), "#7a2a1a", tras)
        bot = mix(mix("#e9f7ff", "#ffe3b0", luz), "#ff7b3a", tras)
        s.append(cielo("cr", top, bot))
        s.append(f"<path d='M0 690 Q300 640 640 680 T1300 670 T1920 690 L1920 790 L0 790 Z' fill='{mix('#6f9d45', '#4a2a20', tras)}' stroke='{INK}' stroke-width='6'/>")
        # río
        s.append(f"<path d='M0 800 Q500 770 960 790 T1920 790 L1920 1080 L0 1080 Z' fill='{mix('#5ab0e0', '#a0402a', tras)}' stroke='{INK}' stroke-width='{LW}'/>")
        for i in range(7):
            x = (i * 300 + t * 50) % 2100 - 100
            s.append(f"<path d='M{x:.0f} {850 + (i * 40) % 120} q30 -10 60 0' fill='none' stroke='#e8f6ff' stroke-width='6' stroke-linecap='round' opacity='0.6'/>")
        s.append(f"<path d='M0 760 Q400 720 760 750 L760 840 Q400 860 0 850 Z' fill='{mix('#8fbf5a', '#5a3a2a', tras)}' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(helecho(120, 800, 0.7, t, mix("#4caf50", "#3a2a22", tras)))
        s.append(cica(1840, 800, 0.8, t, mix("#3f9a48", "#3a2a22", tras)))
        # asteroide: entra arriba a la derecha y cae hacia el horizonte izquierdo
        k = seg(t, m[1] + 0.2, imp) if t < imp else 1
        if t < imp:
            ax = lerp(1650, 1350, k); ay = lerp(300, 640, k ** 1.5)
            s.append(f"<circle cx='{ax:.0f}' cy='{ay:.0f}' r='{120 + 200 * k:.0f}' fill='#fff3b0' opacity='{0.25 * k:.2f}'/>")
            s.append(asteroide(ax, ay, 40 + 45 * k, t, 1.0, -0.6, 1.0))
        # tiranosaurio que ruge (frase 0) y luego mira al cielo
        boca = seg(t, m[0] + 1.0, m[0] + 1.6) * (1 - seg(t, m[0] + 2.8, m[0] + 3.4)) + 0.5 * seg(t, m[1] + 1.5, m[1] + 2.0)
        rex = trex(760, 830, 0.85, t, dirx=1, boca=boca, sil="#2a1410" if tras > 0.5 else None)
        s.append(rex)
        # destello y onda de choque en el horizonte
        if t > imp - 0.1:
            f = seg(t, imp - 0.1, imp + 0.15) * (1 - seg(t, imp + 0.3, imp + 1.6))
            r = 200 + 1400 * seg(t, imp, imp + 2.5)
            s.append(f"<ellipse cx='1350' cy='680' rx='{r:.0f}' ry='{r * 0.35:.0f}' fill='#ffcf5a' opacity='{0.5 * (1 - seg(t, imp, imp + 3)):.2f}'/>")
            for i in range(9):
                kk = ((t - imp) * 0.4 + i / 9) % 1
                s.append(f"<circle cx='{1350 + (i - 4) * 90 + 80 * kk:.0f}' cy='{640 - kk * 380:.0f}' r='{60 + kk * 140:.0f}' fill='{mix('#5a3a30', '#2a1a18', kk)}' opacity='{0.75 * (1 - kk) * tras:.2f}'/>")
        for x, y, r, v in CENIZA:
            if tras > 0:
                s.append(f"<circle cx='{(x + t * 20) % W:.0f}' cy='{(y + t * v) % H:.0f}' r='{r:.1f}' fill='#ffdca8' opacity='{0.5 * tras:.2f}'/>")
        s.append(tico(250, 760, 0.5, t, vuelo=1.0, mira=1 if t < imp else -1, prisa=2 if tras else 1))
        s.append(portal(250, 600, seg(t, 0, 0.5) * (1 - seg(t, 1.4, 2.0)), t))
        if t > imp - 0.1:
            f = seg(t, imp - 0.1, imp + 0.15) * (1 - seg(t, imp + 0.3, imp + 1.6))
            s.append(f"<rect width='{W}' height='{H}' fill='#fff8e0' opacity='{f:.2f}'/>")
    if fosil > 0:
        # capa de roca con un pez fósil y la lupa sobre su hueso: anillos que terminan en primavera
        s.append(f"<g opacity='{fosil:.2f}'>")
        s.append(cielo("cf", "#c7a27c", "#8d6a4c"))
        for i in range(5):
            y = 300 + i * 130
            s.append(f"<path d='M0 {y} Q480 {y - 30 + i * 6} 960 {y} T1920 {y}' fill='none' stroke='{['#a7835e', '#b8936c', '#9a7553'][i % 3]}' stroke-width='60'/>")
        # pez fósil (espina y costillas)
        fx, fy = 620, 620
        s.append(f"<g transform='translate({fx},{fy})'>"
                 f"<path d='M-260 0 Q0 -30 220 0' fill='none' stroke='#f2e6cf' stroke-width='14' stroke-linecap='round'/>"
                 + "".join(f"<path d='M{-200 + k * 36} -6 q10 -50 20 -70 M{-200 + k * 36} 6 q10 50 20 70' fill='none' stroke='#f2e6cf' stroke-width='8' stroke-linecap='round'/>" for k in range(12))
                 + f"<path d='M220 -60 Q320 -40 330 0 Q320 50 220 60 Q250 0 220 -60 Z' fill='#e6d6b8' stroke='#f2e6cf' stroke-width='6'/>"
                 f"<circle cx='280' cy='-10' r='14' fill='#5a4232'/>"
                 f"<path d='M-260 0 L-330 -70 L-320 0 L-330 70 Z' fill='none' stroke='#f2e6cf' stroke-width='9' stroke-linejoin='round'/></g>")
        lk = seg(t, m[3] + 0.4, m[3] + 1.4)
        if lk > 0:
            # anillos de crecimiento: el último anillo (verde claro) está a medio formar = primavera
            ani = seg(t, m[4] + 0.2, m[4] + 2.4)
            cont = [f"<circle cx='1300' cy='560' r='260' fill='#e9dcc0'/>"]
            for k in range(7):
                cont.append(f"<circle cx='1300' cy='560' r='{185 - k * 26}' fill='none' stroke='{'#9a7553' if k % 2 else '#c9ad85'}' stroke-width='14'/>")
            cont.append(f"<circle cx='1300' cy='560' r='212' fill='none' stroke='#7ed957' stroke-width='{26 * ani:.0f}' "
                        f"stroke-dasharray='{1332 * ani:.0f} 2000'/>")
            s.append(lupa(1300, 560, 230 * lk, "".join(cont)))
            prim = seg(t, m[4] + 1.6, m[4] + 3.0)
            for i, (x, y) in enumerate(((1040, 860), (1560, 860), (1160, 900), (1450, 900), (980, 760), (1620, 780))):
                s.append(flor(x, y, prim * (0.9 + 0.2 * (i % 2)) * (1 - seg(t, m[5] - 0.3, m[5] + 0.3)), ["#ff7eb6", "#ffd23f", "#9b5de5"][i % 3]))
            s.append(destellos(1300, 560, seg(t, m[4] + 1.6, m[4] + 3.4), 12, 330))
        # cliffhanger (frase 5): un pajarito con plumas que escapa volando
        pj = seg(t, m[5], m[5] + 3.0)
        if pj > 0:
            s.append(f"<rect width='{W}' height='{H}' fill='#2a1a18' opacity='{0.55 * seg(t, m[5], m[5] + 0.6):.2f}'/>")
            s.append(paloma(lerp(500, 1500, pj), lerp(760, 480, pj) + 20 * math.sin(t * 4), 0.9, t, vuela=1.0, sil="#ffd9a0"))
        s.append(tico(230, 880, 0.45, t, vuelo=0.0, mira=1))
        s.append("</g>")
    return "".join(s)


def parque(t, tarde=0.0):
    top = mix("#7fd3ff", "#ff8a6b", tarde); bot = mix("#e3f7ff", "#ffe0a8", tarde)
    s = [cielo("cp" + ("t" if tarde else ""), top, bot),
         f"<circle cx='1550' cy='{lerp(230, 480, tarde):.0f}' r='80' fill='#ffe066' stroke='{INK}' stroke-width='{LW}'/>",
         nubes(t, (200, 150, 290), 12)]
    # edificios lejanos
    for i, (x, w, h) in enumerate(((60, 160, 300), (240, 120, 380), (380, 180, 260), (1180, 150, 340), (1350, 200, 280), (1580, 140, 400), (1740, 170, 310))):
        col = mix(["#b9c7e6", "#a6b6dc", "#c7d2ec"][i % 3], "#c88a8a", tarde)
        s.append(f"<rect x='{x}' y='{720 - h}' width='{w}' height='{h}' fill='{col}' stroke='{INK}' stroke-width='6'/>")
        for r in range(int(h / 70)):
            for c in range(int(w / 50)):
                s.append(f"<rect x='{x + 18 + c * 50}' y='{720 - h + 24 + r * 70}' width='22' height='30' fill='{mix('#eef3ff', '#ffe28a', tarde)}' stroke='{INK}' stroke-width='3'/>")
    s.append(f"<path d='M0 700 Q480 660 960 690 T1920 680 L1920 800 L0 800 Z' fill='#7cc96a' stroke='{INK}' stroke-width='6'/>")
    s.append(suelo(800, "#8fd36f", "#74bb58", t))
    # camino
    s.append(f"<path d='M0 900 Q700 850 1920 880 L1920 960 Q700 930 0 990 Z' fill='#e8d3a8' stroke='{INK}' stroke-width='6'/>")
    # árbol y banco
    s.append(f"<rect x='1690' y='520' width='50' height='300' fill='#8d6e4a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='1715' cy='470' r='150' fill='#4caf50' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='1630' cy='540' r='90' fill='#5cbf60' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle cx='1810' cy='530' r='95' fill='#43a047' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='1260' y='760' width='300' height='26' rx='8' fill='#c8813f' stroke='{INK}' stroke-width='6'/>"
             f"<rect x='1260' y='700' width='300' height='24' rx='8' fill='#c8813f' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M1290 786 L1290 840 M1530 786 L1530 840' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>")
    return "".join(s)


def esc_aves(t, dur, m):
    s = [parque(t)]
    # migas en el suelo
    for i in range(7):
        s.append(f"<circle cx='{820 + i * 37 % 200}' cy='{905 + (i * 13) % 18}' r='6' fill='#f4c46a' stroke='{INK}' stroke-width='2'/>")
    pal_x = lerp(1250, 900, seg(t, m[1] - 0.6, m[1] + 0.8))
    # gran momento (frase 2): la sombra de un tiranosaurio aparece detrás de la paloma
    som = seg(t, m[2] + 0.1, m[2] + 0.9) * (1 - seg(t, m[3] - 0.2, m[3] + 0.5))
    if som > 0:
        s.append(f"<g opacity='{0.6 * som:.2f}'>{trex(pal_x - 40, 930, 0.95 * (0.7 + 0.3 * som), t, dirx=1, sil='#4a3d78', boca=0.4)}</g>")
        s.append(destellos(pal_x, 650, seg(t, m[2] + 0.3, m[2] + 2.0), 14, 420))
    # frase 3: pequeño dinosaurio con plumas -> ave
    morf = seg(t, m[3] + 0.3, m[3] + 2.8) if t < m[4] else 1
    comp = seg(t, m[4] - 0.2, m[4] + 0.8) * (1 - seg(t, m[5] - 0.2, m[5] + 0.3))
    if comp <= 0.01:
        if 0 < morf < 1 and t > m[3]:
            s.append(f"<g opacity='{math.sin(math.pi * morf):.2f}'>{raptor(pal_x - 330, 930, 0.55, t, dirx=1)}</g>")
            s.append(f"<path d='M{pal_x - 200:.0f} 760 q60 -40 120 0' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round' opacity='{math.sin(math.pi * morf):.2f}'/>"
                     f"<path d='M{pal_x - 92:.0f} 742 l12 22 l-26 4 Z' fill='{INK}' opacity='{math.sin(math.pi * morf):.2f}'/>")
        vuela = seg(t, m[5] + 0.8, m[5] + 1.4)
        px = pal_x + lerp(0, 1300, seg(t, m[5] + 1.0, m[5] + 3.5)); py = 920 - lerp(0, 600, seg(t, m[5] + 1.0, m[5] + 3.5))
        s.append(paloma(px, py, 1.15, t, dirx=-1 if t < m[5] + 0.8 else 1, picotea=seg(t, m[1], m[1] + 0.5) * (1 - seg(t, m[2], m[2] + 0.3)) + 0.0, vuela=vuela))
    else:
        # frase 4: proteínas de T. rex -> sus parientes vivos más cercanos: gallina y avestruz
        s.append(f"<g opacity='{comp:.2f}'>")
        s.append(f"<rect x='380' y='330' width='1160' height='560' rx='40' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}' opacity='0.96'/>")
        s.append(trex(650, 850, 0.6, t, dirx=1, boca=0.2))
        un = seg(t, m[4] + 2.2, m[4] + 3.4)
        s.append(gallina(1090, 850, 1.2 * (0.4 + 0.6 * seg(t, m[4] + 2.0, m[4] + 2.8)), t, dirx=-1))
        s.append(avestruz(1350, 850, 1.0 * (0.4 + 0.6 * seg(t, m[4] + 2.6, m[4] + 3.4)), t, dirx=-1))
        if un > 0:
            for x2 in (1040, 1330):
                s.append(f"<path d='M820 520 Q{(820 + x2) / 2:.0f} {420:.0f} {x2} 560' fill='none' stroke='#f15bb5' stroke-width='12' stroke-linecap='round' "
                         f"stroke-dasharray='{700 * un:.0f} 900'/>")
            for i in range(4):
                s.append(corazon(1000 + i * 110, 470 - 40 * math.sin(t * 3 + i), 1.3, un))
        s.append("</g>")
        s.append(destellos(1150, 560, seg(t, m[4] + 3.2, m[4] + 5.0), 12, 340))
    tl = seg(t, 0.6, 1.4)
    s.append(tico(300, 930, 0.6, t, vuelo=1 - tl, mira=1, guino=(m[5] + 0.3 < t < m[5] + 0.7)))
    s.append(portal(300, 700, seg(t, 0, 0.5) * (1 - seg(t, 1.4, 2.0)), t))
    return "".join(s)


def corazon(x, y, s, op):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 18 C-30 -6 -22 -30 0 -16 C22 -30 30 -6 0 18 Z' "
            f"fill='#ff5a8a' stroke='{INK}' stroke-width='5' opacity='{op:.2f}'/>")


def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


def esc_final(t, dur, m):
    s = [parque(t, tarde=seg(t, 0, 5))]
    # Tico salta de alegría y la paloma pasea
    salto = abs(math.sin(t * 3.2)) * 40 * (1 - seg(t, m[1] - 0.4, m[1]))
    s.append(tico(lerp(620, 470, seg(t, m[1] - 0.5, m[1] + 1.0)), 880 - salto, 0.75, t, guino=(m[3] + 0.4 < t < m[3] + 0.8), mira=1))
    s.append(paloma(760 + 40 * math.sin(t * 0.6), 920, 0.9, t, dirx=1 if math.sin(t * 0.6 + 1) > 0 else -1, picotea=0.6))
    ap = seg(t, m[1] - 0.2, m[1] + 0.6)
    pulsa = m[1] + 2.4
    hecho = t > pulsa
    camp = seg(t, m[1] + 3.6, m[1] + 4.1)
    if ap > 0:
        late = 1 + 0.05 * math.sin(t * 6) if not hecho else 1 + 0.12 * math.exp(-(t - pulsa) * 5) * math.sin((t - pulsa) * 30)
        esc_ = (0.5 + 0.5 * ease(ap)) * late
        col = "#e62117" if not hecho else "#8a8f96"
        txt = "SUSCRÍBETE" if not hecho else "SUSCRITO"
        s.append(f"<g transform='translate(1180,470) scale({esc_:.3f})' opacity='{min(1, ap * 2):.2f}'>"
                 f"<rect x='-330' y='-80' width='560' height='160' rx='80' fill='{col}' stroke='{INK}' stroke-width='10'/>"
                 f"<text x='-50' y='28' text-anchor='middle' font-family=\"Noto Sans CJK SC Black\" font-weight='900' font-size='74' fill='#fff'>{txt}</text></g>")
        ang = 25 * math.sin((t - m[1] - 3.6) * 16) * math.exp(-max(0, t - m[1] - 3.6) * 1.2) if camp > 0 else 0
        s.append(f"<g opacity='{min(1, ap * 2):.2f}'>"
                 f"<circle cx='1545' cy='470' r='{90 * (0.6 + 0.4 * ease(ap)):.0f}' fill='{'#ffd23f' if camp > 0 else '#fff'}' stroke='{INK}' stroke-width='9'/>"
                 + campana_grande(1545, 470, 2.4 * (0.6 + 0.4 * ease(ap)), ang) + "</g>")
        if camp > 0:
            s.append(destellos(1545, 470, seg(t, m[1] + 3.6, m[1] + 5.2), 12, 190))
        if t < m[1] + 5.0:
            cx = lerp(1900, 1160, seg(t, m[1] + 0.4, pulsa - 0.2)); cy = lerp(1000, 485, seg(t, m[1] + 0.4, pulsa - 0.2))
            cx = lerp(cx, 1560, seg(t, pulsa + 0.6, m[1] + 3.5)); cy = lerp(cy, 490, seg(t, pulsa + 0.6, m[1] + 3.5))
            clic = 0.85 if (abs(t - pulsa) < 0.12 or abs(t - (m[1] + 3.6)) < 0.12) else 1.0
            s.append(cursor(cx, cy, 1.3 * clic))
    s.append(destellos(1180, 470, seg(t, pulsa, pulsa + 1.4), 14, 330, "#ffffff"))
    return "".join(s)


CAPITULOS = [
    {"titulo": "¿Has visto hoy un dinosaurio?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que hoy, seguramente, has visto un dinosaurio… sin darte cuenta?",
                "Quédate hasta el final: la última parada te dejará con la boca abierta.",
                "Viajamos al pasado con Tico, nuestra máquina del tiempo.",
                "Suscríbete para no perderte ningún viaje. ¡Allá vamos!"]},
    {"titulo": "1. Más lejos de lo que crees", "escena": esc_estego, "tarjeta": "CAPÍTULO 1 · MÁS LEJOS DE LO QUE CREES",
     "frases": ["Primera parada: hace ciento cincuenta millones de años.",
                "Entre helechos gigantes pasta un estegosaurio, con placas en la espalda y pinchos en la cola.",
                "Mucha gente cree que vivió junto al tiranosaurio… pero no.",
                "Entre el estegosaurio y el tiranosaurio pasaron más de setenta millones de años.",
                "¡Tú vives más cerca del tiranosaurio de lo que él vivió del estegosaurio!"],
     "grandes": {3: "+70 MILLONES"}, "extra": 1.0},
    {"titulo": "2. Un bebé que se convierte en gigante", "escena": esc_titano, "tarjeta": "CAPÍTULO 2 · UN BEBÉ GIGANTE",
     "frases": ["Saltamos al Cretácico, a lo que hoy es Argentina.",
                "Aquí, en el suelo, hay un nido lleno de huevos de dinosaurio.",
                "¡Mira! Uno se rompe… y sale una cría que pesa menos de cinco kilos, como un ganso.",
                "Pero cuidado, que llega su madre: un titanosaurio, de los animales más grandes que han pisado la Tierra.",
                "En unos treinta años, ese bebé podía llegar a pesar diez mil veces más."],
     "grandes": {2: "< 5 KG", 4: "× 10.000"}, "extra": 1.0},
    {"titulo": "3. El cazador con plumas", "escena": esc_raptor, "tarjeta": "CAPÍTULO 3 · EL CAZADOR CON PLUMAS",
     "frases": ["Siguiente parada: el desierto de Mongolia.",
                "Algo se mueve detrás de las rocas. ¡Es un velociraptor!",
                "Seguro que lo imaginabas enorme y cubierto de escamas…",
                "Pues en realidad era del tamaño de un pavo.",
                "Y tenía plumas: en un hueso de su brazo se encontraron las marcas donde se sujetaban.",
                "Pero lo que nos espera en la siguiente parada es todavía más increíble…"],
     "grandes": {3: "¡COMO UN PAVO!", 4: "¡CON PLUMAS!"}},
    {"titulo": "4. El último día de los dinosaurios", "escena": esc_asteroide, "tarjeta": "CAPÍTULO 4 · EL ÚLTIMO DÍA",
     "frases": ["Hace sesenta y seis millones de años, un tiranosaurio ruge a la orilla de un río.",
                "De repente, en el cielo aparece una luz: un asteroide de unos diez kilómetros, más grande que el Everest.",
                "Choca contra la Tierra, en lo que hoy es México, y cambia el planeta para siempre.",
                "Y lo más sorprendente: los científicos saben en qué estación del año ocurrió.",
                "Los huesos de unos peces que murieron ese mismo día tienen anillos, como los troncos de los árboles… y dicen que era primavera.",
                "Pero espera… porque no todos los dinosaurios desaparecieron."],
     "grandes": {1: "10 KM", 4: "PRIMAVERA"}},
    {"titulo": "5. ¡Los dinosaurios siguen aquí!", "escena": esc_aves, "tarjeta": "CAPÍTULO 5 · ¡SIGUEN AQUÍ!",
     "frases": ["Tico vuelve a nuestro tiempo y aterriza en un parque.",
                "Y ahí está: una paloma picoteando migas.",
                "Las aves no son primas lejanas de los dinosaurios: ¡son dinosaurios!",
                "Descienden de pequeños dinosaurios con plumas que sobrevivieron al asteroide.",
                "Unos científicos estudiaron proteínas de un hueso de tiranosaurio, y sus parientes vivos más cercanos eran… la gallina y el avestruz.",
                "Así que sí: hoy has visto un dinosaurio."],
     "grandes": {2: "¡DINOSAURIOS!"}},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje de hoy a la época de los dinosaurios.",
                "Si has descubierto algo nuevo, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
