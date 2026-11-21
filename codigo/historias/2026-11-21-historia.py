"""Episodio: "Viaje por dentro del cuerpo humano" con Pildo, una nave cápsula original.

Datos (verificados el 21-11-2026):
- El jugo gástrico es ácido clorhídrico (pH de 1,5 a 3,5), tan fuerte que puede disolver algunos metales
  como el zinc; el estómago no se digiere a sí mismo porque se protege con una capa de moco (y bicarbonato)
  que fabrica sin parar (Live Science «Why doesn't stomach acid burn through our stomachs?»; IFLScience;
  Healthline «How strong is stomach acid?»; Royal Society of Chemistry «Hydrochloric acid»).
- En el cuerpo de una persona de referencia viven unos 38 billones (38 × 10^12) de bacterias, sobre todo
  en el intestino grueso: aproximadamente tantas como células humanas (unos 30 billones), una proporción
  cercana a 1:1 (Sender, Fuchs y Milo, PLoS Biology 2016; Weizmann Institute; Scientific American).
- En reposo el corazón bombea unos 5 litros de sangre por minuto (gasto cardíaco), más o menos toda la
  sangre de un adulto, que da la vuelta completa al cuerpo en alrededor de un minuto (Britannica «Cardiac
  output»; WebMD; Encyclopedia.com «Blood circulation»).
- Los pulmones tienen unos 480 millones de alvéolos (Ochs et al., 2004) y su superficie de intercambio es
  de unos 70 m² (Wikipedia «Pulmonary alveolus», Kenhub, LibreTexts); una pista de bádminton de dobles
  mide 13,4 × 6,1 m ≈ 82 m².
- En los nervios mielinizados más rápidos los impulsos viajan a unos 120 m/s (≈ 430 km/h, 268 mph),
  más que la velocidad punta de un Fórmula 1 (≈ 370 km/h) (Discover Magazine «Numbers: The Nervous
  System, From 268-MPH Signals…»; NCBI Bookshelf, Neuroscience, Purves et al.).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-21-historia"
TITULO = "Viaje por dentro del cuerpo humano"
VOZ = "em_santa"
VELOCIDAD = 0.95
MUSICA = 52

W, H = 1920, 1080
rng = np.random.default_rng(21)
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), rng.uniform(0, 6)) for _ in range(60)]
BACT = [(rng.uniform(0, 1), rng.uniform(330, 820), rng.integers(0, 3), rng.integers(0, 5), rng.uniform(0, 6.3),
         rng.uniform(0.7, 1.2)) for _ in range(34)]
GLOB = [(rng.uniform(0, 1), rng.uniform(290, 830), rng.uniform(0.7, 1.15), rng.uniform(0, 6.3)) for _ in range(20)]
BURBS = [(rng.uniform(150, 1800), rng.uniform(0, 1), rng.uniform(6, 16)) for _ in range(26)]


# ================= piezas comunes =================
def fondo(id_, top, bot):
    return (f"<defs><linearGradient id='{id_}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#{id_})'/>")


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


def chispa(x, y, r, op=1.0, col="#fff176"):
    return (f"<g transform='translate({x:.0f},{y:.0f})' opacity='{op:.2f}'><circle r='{r * 2.2:.0f}' fill='{col}' opacity='0.3'/>"
            f"<path d='M0 {-r * 1.6:.0f} L{r * 0.4:.0f} {-r * 0.4:.0f} L{r * 1.6:.0f} 0 L{r * 0.4:.0f} {r * 0.4:.0f} L0 {r * 1.6:.0f} "
            f"L{-r * 0.4:.0f} {r * 0.4:.0f} L{-r * 1.6:.0f} 0 L{-r * 0.4:.0f} {-r * 0.4:.0f} Z' fill='#fffde7' stroke='{col}' stroke-width='4'/></g>")


def pildo(x, y, s, t, guino=False, ang=0.0, fuego=1.0, mira=0.0, dirx=1):
    """Pildo: nave cápsula (mitad turquesa, mitad amarilla) con visera de cristal y dos ojos, antena con luz,
    aletas y propulsor que echa una llamita azul."""
    parp = 0.12 if ((t + 1.7) % 3.6) < 0.13 or guino else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s * dirx:.3f},{s:.3f})'>"]
    if fuego > 0.01:
        fl = 70 + 25 * math.sin(t * 28)
        g.append(f"<path d='M-168 -30 Q{-168 - fl * fuego:.0f} 0 -168 30 Z' fill='#4cc9f0' stroke='{INK}' stroke-width='5' opacity='{fuego:.2f}'/>"
                 f"<path d='M-168 -16 Q{-168 - fl * 0.6 * fuego:.0f} 0 -168 16 Z' fill='#e0fbff' opacity='{fuego:.2f}'/>")
    g.append(f"<rect x='-178' y='-34' width='36' height='68' rx='10' fill='#9aa3ad' stroke='{INK}' stroke-width='6'/>")
    # aletas
    g.append(f"<path d='M-90 -66 L-130 -118 L-40 -70 Z' fill='#ff6b6b' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M-90 66 L-130 118 L-40 70 Z' fill='#ff6b6b' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # antena
    luz = 0.5 + 0.5 * math.sin(t * 6)
    g.append(f"<line x1='-40' y1='-72' x2='-52' y2='-124' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
             f"<circle cx='-54' cy='-132' r='22' fill='#ff4d6d' opacity='{0.3 * luz:.2f}'/>"
             f"<circle cx='-54' cy='-132' r='12' fill='{mix('#c9184a', '#ff8fa3', luz)}' stroke='{INK}' stroke-width='5'/>")
    # cuerpo de cápsula
    g.append(f"<path d='M0 -75 L-80 -75 A75 75 0 0 0 -80 75 L0 75 Z' fill='#2ec4b6'/>"
             f"<path d='M0 -75 L80 -75 A75 75 0 0 1 80 75 L0 75 Z' fill='#ffd23f'/>"
             f"<path d='M-140 30 Q-60 62 0 62 L0 75 L-80 75 A75 75 0 0 1 -150 20 Z' fill='#1f9e93'/>"
             f"<path d='M0 62 Q80 62 140 30 L150 20 A75 75 0 0 1 80 75 L0 75 Z' fill='#f4b400'/>"
             f"<rect x='-155' y='-75' width='310' height='150' rx='75' fill='none' stroke='{INK}' stroke-width='{LW}'/>"
             f"<line x1='0' y1='-75' x2='0' y2='75' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M-120 -42 Q-70 -64 -20 -60' fill='none' stroke='#fff' stroke-width='10' stroke-linecap='round' opacity='0.7'/>")
    for k in range(3):
        on = 0.5 + 0.5 * math.sin(t * 5 + k * 2)
        g.append(f"<circle cx='{-105 + k * 30}' cy='8' r='9' fill='{mix('#0b6e66', '#b9fff6', on)}' stroke='{INK}' stroke-width='4'/>")
    # visera con los ojos
    g.append(f"<ellipse cx='72' cy='-8' rx='64' ry='50' fill='#e9f7ff' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<path d='M30 -36 Q48 -52 74 -54' fill='none' stroke='#fff' stroke-width='7' stroke-linecap='round'/>")
    for ex in (48, 98):
        g.append(f"<g transform='translate({ex},-10) scale(1,{parp})'><ellipse rx='19' ry='23' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{4 + mira * 6:.0f}' cy='2' r='11' fill='#1e2a38'/><circle cx='{mira * 6:.0f}' cy='-4' r='4' fill='#fff'/></g>")
    g.append(f"<path d='M56 26 Q74 40 94 26' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def corazon(x, y, s, op):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 18 C-30 -6 -22 -30 0 -16 C22 -30 30 -6 0 18 Z' "
            f"fill='#ff5a8a' stroke='{INK}' stroke-width='5' opacity='{op:.2f}'/>")


def cronometro(cx, cy, ang, k, s0=1.0):
    if k <= 0:
        return ""
    s = s0 * (0.6 + 0.4 * ease(min(1, k * 2)))
    return (f"<g transform='translate({cx},{cy}) scale({s:.2f})' opacity='{min(1, k * 3):.2f}'>"
            f"<rect x='-18' y='-138' width='36' height='30' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>"
            f"<circle r='112' fill='#fff8e6' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M0 0 L0 -92 A92 92 0 {1 if ang > 180 else 0} 1 {92 * math.sin(math.radians(ang)):.1f} {-92 * math.cos(math.radians(ang)):.1f} Z' fill='#ffd23f' opacity='0.6'/>"
            + "".join(f"<line x1='0' y1='-80' x2='0' y2='-66' stroke='{INK}' stroke-width='6' transform='rotate({a})'/>" for a in range(0, 360, 30))
            + f"<line x1='0' y1='0' x2='0' y2='-82' stroke='#e8382f' stroke-width='9' stroke-linecap='round' transform='rotate({ang:.0f})'/>"
            f"<circle r='12' fill='{INK}'/></g>")


# ---------------- cuerpo humano (mapa) ----------------
ORG = {"boca": (0, 150), "estomago": (52, 520), "intestino": (0, 640), "corazon": (28, 410),
       "pulmones": (-75, 395), "cerebro": (0, 72)}
RUTA = [(0, 150), (0, 300), (20, 450), (52, 520), (20, 600), (0, 640), (-40, 600), (-10, 520), (28, 410),
        (-30, 380), (-75, 395), (-60, 300), (0, 220), (0, 72)]


def cuerpo(cx, top, s, t, brillo=1.0, cerebro=0.0, ruta=0.0, cara=True, col="#cdeaff"):
    """Silueta humana de frente (mapa del viaje) con órganos visibles. (0,0) = coronilla."""
    g = [f"<g transform='translate({cx:.0f},{top:.0f}) scale({s:.3f})'>"]
    for sx in (-1, 1):   # brazos y piernas
        g.append(f"<path d='M{sx * 172} 268 Q{sx * 236} 450 {sx * 246} 660' fill='none' stroke='{INK}' stroke-width='80' stroke-linecap='round'/>"
                 f"<path d='M{sx * 172} 268 Q{sx * 236} 450 {sx * 246} 660' fill='none' stroke='{col}' stroke-width='62' stroke-linecap='round'/>"
                 f"<path d='M{sx * 75} 700 L{sx * 90} 1060' fill='none' stroke='{INK}' stroke-width='112' stroke-linecap='round'/>"
                 f"<path d='M{sx * 75} 700 L{sx * 90} 1060' fill='none' stroke='{col}' stroke-width='94' stroke-linecap='round'/>")
    g.append(f"<rect x='-42' y='170' width='84' height='80' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-185 270 Q-190 232 -140 228 L140 228 Q190 232 185 270 L165 640 Q155 705 100 725 L-100 725 Q-155 705 -165 640 Z' "
             f"fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<circle cx='0' cy='100' r='96' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>")
    b = brillo * (0.85 + 0.15 * math.sin(t * 4))
    # órganos
    g.append(f"<g opacity='{b:.2f}'>")
    g.append(f"<path d='M-72 86 Q-80 20 -30 14 Q0 -4 30 14 Q80 20 72 86 Q40 104 0 96 Q-40 104 -72 86 Z' fill='{mix('#ff9ecb', '#fff59d', cerebro)}' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M-50 40 q15 15 0 30 M-14 26 q14 18 -2 36 M22 30 q-12 18 4 34 M52 48 q-14 12 0 26 M0 18 L0 94' fill='none' stroke='#d0619a' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M-6 300 L-6 250' stroke='#f6a27a' stroke-width='14'/>")
    for sx in (-1, 1):
        g.append(f"<path d='M{sx * 20} 300 Q{sx * 20} 290 {sx * 30} 300 Q{sx * 125} 300 {sx * 128} 420 Q{sx * 128} 500 {sx * 70} 500 Q{sx * 25} 500 {sx * 25} 450 Z' "
                 f"fill='#ff8fa3' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M28 445 C-14 410 -6 370 28 390 C62 370 70 410 28 445 Z' fill='#e63946' stroke='{INK}' stroke-width='6' "
             f"transform='translate(28,410) scale({1 + 0.1 * abs(math.sin(t * 4)):.2f}) translate(-28,-410)'/>")
    g.append(f"<path d='M20 470 Q110 455 105 525 Q100 585 40 575 Q0 568 10 540 Q50 545 60 520 Q60 490 20 495 Z' fill='#ffb45c' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-90 600 Q-90 580 -60 585 L60 585 Q90 580 90 610 L90 680 Q90 700 60 700 L-60 700 Q-90 700 -90 680 Z' fill='#f6a27a' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M-60 615 Q0 600 60 615 Q70 640 0 640 Q-70 640 -60 665 Q0 680 60 668' fill='none' stroke='#d9735a' stroke-width='9' stroke-linecap='round'/>")
    g.append("</g>")
    if cara:
        g.append(f"<circle cx='-34' cy='120' r='9' fill='{INK}'/><circle cx='34' cy='120' r='9' fill='{INK}'/>"
                 f"<ellipse cx='0' cy='154' rx='16' ry='12' fill='#7a2433' stroke='{INK}' stroke-width='5'/>")
    if ruta > 0:   # ruta del viaje: puntitos que se van dibujando
        tot = sum(math.dist(RUTA[i], RUTA[i + 1]) for i in range(len(RUTA) - 1))
        lim, d = ruta * tot, 0.0
        for i in range(len(RUTA) - 1):
            a, c = RUTA[i], RUTA[i + 1]; L = math.dist(a, c); n = max(1, int(L / 22))
            for k in range(n):
                if d + L * k / n > lim:
                    break
                p = (lerp(a[0], c[0], k / n), lerp(a[1], c[1], k / n))
                g.append(f"<circle cx='{p[0]:.0f}' cy='{p[1]:.0f}' r='6' fill='#ffe066' stroke='{INK}' stroke-width='2'/>")
            d += L
        for i, nombre in enumerate(("estomago", "intestino", "corazon", "pulmones", "cerebro")):
            if ruta > (i + 1) / 5.3:
                ox, oy = ORG[nombre]
                g.append(f"<circle cx='{ox}' cy='{oy}' r='{18 + 6 * math.sin(t * 5 + i):.0f}' fill='none' stroke='#ffe066' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def rayitos(cx, cy, k, t, r=120, n=8, col="#fff176"):
    """Pequeños rayos eléctricos alrededor de un punto."""
    if k <= 0:
        return ""
    s = []
    for i in range(n):
        a = i / n * 2 * math.pi + t * 0.8
        if (math.sin(t * 13 + i * 2.3) > 0.1):
            x0, y0 = cx + r * 0.7 * math.cos(a), cy + r * 0.7 * math.sin(a)
            x1, y1 = cx + r * 1.15 * math.cos(a + 0.1), cy + r * 1.15 * math.sin(a + 0.1)
            x2, y2 = cx + r * 1.5 * math.cos(a - 0.05), cy + r * 1.5 * math.sin(a - 0.05)
            s.append(f"<path d='M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}' fill='none' stroke='{col}' stroke-width='7' stroke-linecap='round' stroke-linejoin='round' opacity='{k:.2f}'/>")
    return "".join(s)


# ================= capítulos =================
def esc_intro(t, dur, m):
    s = [fondo("noche", "#1b1446", "#3a1f6e")]
    for x, y, r, f in ESTRELLAS:
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{0.35 + 0.35 * math.sin(t * 2 + f):.2f}'/>")
    for i in range(8):   # rejilla de "pantalla de mapa"
        s.append(f"<line x1='{i * 280 - (t * 30) % 280:.0f}' y1='0' x2='{i * 280 - (t * 30) % 280:.0f}' y2='{H}' stroke='#6a5acd' stroke-width='2' opacity='0.35'/>")
    for i in range(5):
        s.append(f"<line x1='0' y1='{i * 260 + 40}' x2='{W}' y2='{i * 260 + 40}' stroke='#6a5acd' stroke-width='2' opacity='0.35'/>")
    cx, top, sc = 1260, 150, 0.84
    # halo detrás del cuerpo
    s.append(f"<circle cx='{cx}' cy='560' r='{430 + 15 * math.sin(t * 2):.0f}' fill='#7b6cff' opacity='0.18'/>")
    ruta = seg(t, m[1] + 0.8, m[2] + 1.5)
    cer = 0.5 + 0.5 * math.sin(t * 9) if t < m[1] else seg(t, m[2], m[2] + 0.6) * (0.5 + 0.5 * math.sin(t * 7))
    cuerpo_svg = cuerpo(cx, top, sc, t, cerebro=cer, ruta=ruta)
    s.append(cuerpo_svg)
    # rayos en el cerebro desde el fotograma 0 (frase 0) y al anunciar la última parada
    k_ray = (1 - seg(t, m[1] - 0.4, m[1])) + seg(t, m[2], m[2] + 0.5) * (1 - seg(t, m[3], m[3] + 0.5))
    s.append(rayitos(cx, top + 72 * sc, clamp(k_ray), t, r=95))
    # Pildo: entra a toda velocidad, se encoge (frase 1) y vuela hacia la boca
    entra = seg(t, 0, 2.0)
    encoge = seg(t, m[1] + 0.8, m[1] + 2.8)
    boca = (cx, top + 150 * sc)
    va = seg(t, dur - 2.6, dur - 0.8)
    px = lerp(330, 560, entra) + 20 * math.sin(t * 1.6)
    py = 560 + 25 * math.sin(t * 2.2)
    px = lerp(px, boca[0] - 150, seg(t, m[2], m[3])); py = lerp(py, boca[1] + 40, seg(t, m[2], m[3]))
    px = lerp(px, boca[0] + 10, va); py = lerp(py, boca[1], va)
    ps = lerp(1.05, 0.34, encoge) * (1 - 0.6 * va)
    if encoge > 0 and encoge < 1:   # anillos del "rayo reductor"
        for i in range(4):
            k = (t * 1.5 + i / 4) % 1
            s.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{80 + k * 320:.0f}' fill='none' stroke='{['#f15bb5', '#00f5d4', '#fee440', '#9b5de5'][i]}' stroke-width='{14 * (1 - k):.0f}' opacity='{1 - k:.2f}'/>")
    s.append(destellos(px, py, seg(t, m[1] + 2.0, m[1] + 3.4), 10, 160))
    for i in range(6):   # estela
        k = ((t * 2 + i / 6) % 1)
        s.append(f"<circle cx='{px - 200 * ps - k * 260 * max(ps, 0.3):.0f}' cy='{py + 20 * math.sin(t * 3 + i):.0f}' r='{14 * (1 - k) * max(ps, 0.35):.0f}' fill='#4cc9f0' opacity='{0.7 * (1 - k):.2f}'/>")
    s.append(pildo(px, py, ps, t, ang=6 * math.sin(t * 1.7) + 10 * va, guino=(m[3] + 0.3 < t < m[3] + 0.7)))
    cuerpo_y_todo = "".join(s)
    z = 1 + 7 * seg(t, dur - 1.4, dur) ** 2
    out = [f"<g transform='translate({boca[0]:.1f},{boca[1]:.1f}) scale({z:.3f}) translate({-boca[0]:.1f},{-boca[1]:.1f})'>{cuerpo_y_todo}</g>"]
    fl = seg(t, dur - 0.5, dur)
    if fl > 0:
        out.append(f"<rect width='{W}' height='{H}' fill='#ff8fa3' opacity='{fl:.2f}'/>")
    return "".join(out)


CAVIDAD = "M70 430 Q60 215 420 228 Q960 165 1500 228 Q1860 215 1850 430 L1850 1100 L70 1100 Z"


def paredes(t, color="#c93b5c", pliegue="#e2607c", fondo_="#ff9fb0"):
    """Paredes del estómago con pliegues que se mueven (movimientos peristálticos) y cavidad interior."""
    s = [f"<rect width='{W}' height='{H}' fill='{color}'/>"]
    for i in range(9):
        y = 40 + i * 120
        ola = "".join(f"Q{120 + k * 240} {y + 40 * math.sin(t * 1.6 + k + i):.0f} {240 + k * 240} {y} " for k in range(8))
        s.append(f"<path d='M0 {y} {ola}' fill='none' stroke='{pliegue}' stroke-width='22' stroke-linecap='round'/>")
    s.append("<defs><radialGradient id='cav' cx='0.5' cy='0.45' r='0.7'>"
             f"<stop offset='0' stop-color='{mix(fondo_, '#ffffff', 0.25)}'/><stop offset='1' stop-color='{fondo_}'/></radialGradient></defs>")
    s.append(f"<path d='{CAVIDAD}' fill='url(#cav)' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(5):   # pliegues de la pared interior
        x = 300 + i * 330 + 30 * math.sin(t * 1.2 + i)
        s.append(f"<path d='M{x:.0f} 250 Q{x + 40 * math.sin(t + i):.0f} 420 {x - 30:.0f} 600' fill='none' stroke='#f48aa0' stroke-width='16' stroke-linecap='round' opacity='0.55'/>")
    return "".join(s)


def tuerca(x, y, r, ang, col="#9aa3ad"):
    pts = " ".join(f"{x + r * math.cos(math.radians(ang + k * 60)):.0f},{y + r * math.sin(math.radians(ang + k * 60)):.0f}" for k in range(6))
    return (f"<polygon points='{pts}' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * 0.42:.0f}' fill='#ff9fb0' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M{x - r * 0.6:.0f} {y - r * 0.55:.0f} L{x - r * 0.15:.0f} {y - r * 0.8:.0f}' stroke='#fff' stroke-width='6' stroke-linecap='round' opacity='0.8'/>")


def esc_estomago(t, dur, m):
    s = [paredes(t)]
    # entrada (esófago) arriba
    s.append(f"<ellipse cx='960' cy='200' rx='120' ry='34' fill='#7a1f36' stroke='{INK}' stroke-width='{LW}'/>")
    # lago de jugo gástrico
    lago_y = 800
    ola = "".join(f"Q{60 + i * 120:.0f} {lago_y + 16 * math.sin(t * 2.2 + i):.0f} {120 + i * 120:.0f} {lago_y} " for i in range(17))
    s.append("<defs><linearGradient id='acido' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e4ff6b'/>"
             "<stop offset='1' stop-color='#8fbf1f'/></linearGradient></defs>")
    s.append(f"<path d='M0 {lago_y} {ola} L1920 1080 L0 1080 Z' fill='url(#acido)' stroke='{INK}' stroke-width='{LW}'/>")
    for x, f, r in BURBS:   # burbujas del ácido
        k = (t * 0.7 + f) % 1
        y = lago_y + 220 - k * 250
        s.append(f"<circle cx='{x + 10 * math.sin(t * 3 + f * 9):.0f}' cy='{y:.0f}' r='{r * (0.6 + k):.0f}' fill='#f4ffb0' fill-opacity='0.5' stroke='#5f8a10' stroke-width='3' opacity='{1 - k ** 3:.2f}'/>")
    for i in range(5):   # vapor
        k = (t * 0.4 + i / 5) % 1
        vx = 300 + i * 330 + 40 * math.sin(t + i)
        s.append(f"<path d='M{vx:.0f} {lago_y - 10 - k * 200:.0f} q20 -30 0 -60 q-20 -30 0 -60' fill='none' stroke='#f4ffb0' stroke-width='9' stroke-linecap='round' opacity='{0.5 * (1 - k):.2f}'/>")
    # trocitos de comida que caen desde el esófago y se deshacen en el ácido
    comidas = [(0.0, 760, "#7bc043"), (0.9, 1180, "#e9c46a"), (1.8, 1450, "#ffd166")]
    for ini, fx, col in comidas:
        k = seg(t, ini, ini + 1.6)
        dis = seg(t, ini + 1.6, ini + 5.5)
        if dis < 1:
            fy = lerp(200, lago_y + 5, k) + (10 * math.sin(t * 3 + ini) if k >= 1 else 0)
            xx = lerp(960, fx, k)
            r = 30 * (1 - dis)
            if col == "#e9c46a":
                s.append(f"<rect x='{xx - r:.0f}' y='{fy - r:.0f}' width='{2 * r:.0f}' height='{2 * r:.0f}' rx='10' fill='{col}' stroke='{INK}' stroke-width='6' transform='rotate({t * 40:.0f},{xx:.0f},{fy:.0f})'/>")
            elif col == "#ffd166":
                s.append(f"<path d='M{xx - r:.0f} {fy + r * 0.7:.0f} L{xx + r:.0f} {fy + r * 0.7:.0f} L{xx:.0f} {fy - r:.0f} Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round' transform='rotate({-t * 30:.0f},{xx:.0f},{fy:.0f})'/>")
            else:
                s.append(f"<circle cx='{xx:.0f}' cy='{fy:.0f}' r='{r:.0f}' fill='{col}' stroke='{INK}' stroke-width='6'/>")
    # la tuerca de metal cae (frase 2) y se disuelve entre burbujas
    cae = seg(t, m[2] - 0.3, m[2] + 1.0)
    disu = seg(t, m[2] + 1.0, m[2] + 5.5)
    if t > m[2] - 0.3 and disu < 1:
        tx, ty = lerp(960, 1220, cae), lerp(200, lago_y + 10, cae ** 1.5)
        r = 88 * (1 - 0.92 * disu)
        s.append(f"<circle cx='{tx:.0f}' cy='{ty:.0f}' r='{r * 2.4 + 60 * disu:.0f}' fill='#f4ffb0' opacity='{0.45 * disu:.2f}'/>")
        s.append(tuerca(tx, ty, r, t * 50, mix("#9aa3ad", "#b8d86a", disu)))
        if disu > 0:
            for i in range(12):
                k = (t * 1.4 + i / 12) % 1
                bx = tx + 90 * math.sin(i * 2.1 + t) * (0.3 + k)
                s.append(f"<circle cx='{bx:.0f}' cy='{ty - k * 260:.0f}' r='{(8 + i % 4 * 4) * (0.5 + k):.0f}' fill='#ffffff' fill-opacity='0.4' stroke='#5f8a10' stroke-width='3' opacity='{(1 - k) * (1 - disu ** 4):.2f}'/>")
    s.append(destellos(1220, lago_y - 40, seg(t, m[2] + 4.5, m[2] + 6.0), 12, 260, "#f4ffb0"))
    # capa de moco protectora (frase 4)
    moco = seg(t, m[4] - 0.2, m[4] + 1.2)
    if moco > 0:
        s.append(f"<path d='{CAVIDAD}' fill='none' stroke='#eaf6ff' stroke-width='{46 * moco:.0f}' opacity='0.75'/>")
        s.append(f"<path d='{CAVIDAD}' fill='none' stroke='#ffffff' stroke-width='10' stroke-dasharray='60 140' stroke-dashoffset='{-t * 200:.0f}' opacity='{0.9 * moco:.2f}'/>")
        for i in range(6):   # gotas de ácido que rebotan en el moco
            k = ((t - m[4]) * 0.9 + i / 6) % 1
            gx = 200 + i * 300
            gy = lago_y - 40 - 330 * math.sin(math.pi * k)
            s.append(f"<circle cx='{gx + 120 * k:.0f}' cy='{gy:.0f}' r='14' fill='#d4f05a' stroke='{INK}' stroke-width='4' opacity='{moco:.2f}'/>")
    # Pildo: cae por el esófago al empezar y luego flota mirando
    cae_p = seg(t, 0, 1.6)
    px = lerp(960, 520, seg(t, 0.8, 2.6)) + 20 * math.sin(t * 0.9)
    py = lerp(150, 520, cae_p) + 16 * math.sin(t * 1.5)
    ang = lerp(80, 0, cae_p) + 4 * math.sin(t * 1.4)
    mira = 1 if m[2] < t < m[3] + 0.5 else 0
    s.append(pildo(px, py, 0.82, t, ang=ang, mira=mira, guino=(m[4] + 1.6 < t < m[4] + 2.0)))
    return "".join(s)


# ---------------- intestino ----------------
BCOL = ["#7bd389", "#b388eb", "#4cc9f0", "#ffa94d", "#ffd23f"]


def bacteria(x, y, s, tipo, col, ang, t, feliz=0.0):
    osc = mix(col, "#000000", 0.25)
    parp = 0.15 if ((t + x * 0.01) % 3.1) < 0.12 else 1
    if tipo == 0:     # bacilo (bastón)
        cuerpo = f"<rect x='-55' y='-26' width='110' height='52' rx='26' fill='{col}' stroke='{INK}' stroke-width='6'/>" \
                 f"<path d='M-55 0 q-20 {10 * math.sin(t * 8):.0f} -40 0' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
    elif tipo == 1:   # coco (bolita)
        cuerpo = f"<circle r='34' fill='{col}' stroke='{INK}' stroke-width='6'/>"
    else:             # espirilo (curvado)
        cuerpo = f"<path d='M-60 0 Q-30 -40 0 0 Q30 40 60 0' fill='none' stroke='{INK}' stroke-width='40' stroke-linecap='round'/>" \
                 f"<path d='M-60 0 Q-30 -40 0 0 Q30 40 60 0' fill='none' stroke='{col}' stroke-width='28' stroke-linecap='round'/>"
    ojos = (f"<g transform='scale(1,{parp})'><circle cx='-10' cy='-6' r='8' fill='#fff' stroke='{INK}' stroke-width='3'/><circle cx='-9' cy='-5' r='4' fill='{INK}'/>"
            f"<circle cx='12' cy='-6' r='8' fill='#fff' stroke='{INK}' stroke-width='3'/><circle cx='13' cy='-5' r='4' fill='{INK}'/></g>")
    boca = f"<path d='M-8 {8} Q1 {8 + 8 * feliz + 2:.0f} 10 8' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>"
    puntos = f"<circle cx='-30' cy='10' r='5' fill='{osc}'/><circle cx='28' cy='12' r='4' fill='{osc}'/>" if tipo == 0 else ""
    return f"<g transform='translate({x:.0f},{y:.0f}) rotate({ang:.0f}) scale({s:.2f})'>{cuerpo}{puntos}<g transform='rotate({-ang:.0f})'>{ojos}{boca}</g></g>"


def celula(x, y, r):
    return (f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r}' fill='#ffb3c6' stroke='{INK}' stroke-width='5'/>"
            f"<circle cx='{x + r * 0.15:.0f}' cy='{y - r * 0.1:.0f}' r='{r * 0.4:.0f}' fill='#9b5de5' stroke='{INK}' stroke-width='4'/>")


def balanza(cx, cy, ang, k, t):
    if k <= 0:
        return ""
    a = math.radians(ang)
    lx, ly = cx - 260 * math.cos(a), cy - 260 * math.sin(a)
    rx_, ry_ = cx + 260 * math.cos(a), cy + 260 * math.sin(a)
    s = [f"<g opacity='{min(1, k * 2):.2f}' transform='translate({cx},{cy + 120}) scale({0.6 + 0.4 * ease(k):.2f}) translate({-cx},{-cy - 120})'>"]
    s.append(f"<path d='M{cx - 110} {cy + 300} L{cx + 110} {cy + 300} L{cx + 30} {cy + 260} L{cx + 18} {cy} L{cx - 18} {cy} L{cx - 30} {cy + 260} Z' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for (px, py, lado) in ((lx, ly, 0), (rx_, ry_, 1)):
        s.append(f"<path d='M{px:.0f} {py:.0f} L{px - 95:.0f} {py + 150:.0f} M{px:.0f} {py:.0f} L{px + 95:.0f} {py + 150:.0f}' stroke='{INK}' stroke-width='5'/>")
        if lado == 0:
            for i in range(7):
                bx = px - 70 + (i % 4) * 46 + (23 if i >= 4 else 0); by = py + 128 - (i // 4) * 40
                s.append(bacteria(bx, by, 0.42, i % 3, BCOL[i % 5], 10 * math.sin(t * 3 + i), t, 1))
        else:
            for i in range(7):
                cx2 = px - 70 + (i % 4) * 46 + (23 if i >= 4 else 0); cy2 = py + 130 - (i // 4) * 40
                s.append(celula(cx2, cy2, 22))
        s.append(f"<path d='M{px - 115:.0f} {py + 150:.0f} Q{px:.0f} {py + 215:.0f} {px + 115:.0f} {py + 150:.0f} Z' fill='#9aa3ad' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    s.append(f"<line x1='{lx:.0f}' y1='{ly:.0f}' x2='{rx_:.0f}' y2='{ry_:.0f}' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>"
             f"<line x1='{lx:.0f}' y1='{ly:.0f}' x2='{rx_:.0f}' y2='{ry_:.0f}' stroke='#ffd23f' stroke-width='14' stroke-linecap='round'/>"
             f"<circle cx='{cx}' cy='{cy}' r='22' fill='#ff6b6b' stroke='{INK}' stroke-width='6'/></g>")
    return "".join(s)


def vellosidades(t, y0, sentido, avance, col="#f58ea0"):
    s = []
    for i in range(30):
        x = (i * 72 - avance) % (W + 144) - 72
        largo = 120 + 30 * math.sin(i * 1.7)
        sw = 14 * math.sin(t * 2 + i * 0.8)
        y1 = y0 + sentido * largo
        d = f"M{x:.0f} {y0} Q{x + sw / 2:.0f} {(y0 + y1) / 2:.0f} {x + sw:.0f} {y1:.0f}"
        s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='48' stroke-linecap='round'/>"
                 f"<path d='{d}' fill='none' stroke='{col}' stroke-width='34' stroke-linecap='round'/>")
    return "".join(s)


def esc_intestino(t, dur, m):
    avance = t * 90
    s = [fondo("intes", "#ffd3d9", "#ffb8c3")]
    s.append(f"<rect x='0' y='0' width='{W}' height='250' fill='#d95c74'/>"
             f"<rect x='0' y='860' width='{W}' height='220' fill='#d95c74'/>")
    s.append(vellosidades(t, 250, 1, avance))
    s.append(vellosidades(t + 1.3, 860, -1, avance * 1.1))
    s.append(f"<path d='M0 250 L{W} 250 M0 860 L{W} 860' stroke='{INK}' stroke-width='{LW}'/>")
    # bacterias: unas pocas al principio, muchísimas al decir la cifra (frase 2)
    n = int(lerp(3, len(BACT), seg(t, m[1] - 0.3, m[2] + 2.5)))
    bal = seg(t, m[3] - 0.3, m[3] + 0.6) * (1 - seg(t, m[5] - 0.6, m[5]))
    feliz = seg(t, m[4], m[4] + 0.8)
    for i, (fx, y, tipo, c, f, sc) in enumerate(BACT[:n]):
        x = (fx * (W + 300) - avance * 0.6 * (1 + i % 3 * 0.2)) % (W + 300) - 150
        yy = y + 22 * math.sin(t * 1.5 + f)
        aparece = min(1.0, (t - (m[1] - 0.3) - i * 0.08) * 3) if i >= 3 else 1.0
        if aparece <= 0:
            continue
        op = 1 - 0.7 * bal
        s.append(f"<g opacity='{op:.2f}'>{bacteria(x, yy, sc * max(0.2, aparece), tipo, BCOL[c], 20 * math.sin(t * 2 + f), t, feliz)}</g>")
    # balanza: bacterias contra células (frase 3)
    if bal > 0:
        osc = 14 * math.exp(-max(0, t - m[3]) * 1.1) * math.cos((t - m[3]) * 5)
        s.append(balanza(1180, 470, osc, bal, t))
    if feliz > 0 and bal < 1:
        for i in range(5):
            k = ((t - m[4]) * 0.5 + i / 5) % 1
            s.append(corazon(700 + i * 260, 760 - k * 380, 1.4, feliz * (1 - k) * (1 - bal * 0.7)))
    # Pildo
    px = lerp(-260, 420, seg(t, 0, 2.0)) + 18 * math.sin(t * 1.1)
    py = 540 + 18 * math.sin(t * 1.6)
    s.append(pildo(px, py, 0.8, t, ang=4 * math.sin(t * 1.3), guino=(m[4] + 0.5 < t < m[4] + 0.9), mira=0.6 * bal))
    # río rojo que se acerca (frase 5)
    rojo = seg(t, m[5], dur)
    if rojo > 0:
        s.append(f"<rect x='{lerp(W, 0, rojo):.0f}' y='0' width='{W}' height='{H}' fill='#d62839' opacity='0.85'/>")
        for i, (fx, y, sc, f) in enumerate(GLOB[:10]):
            gx = lerp(W + 100, -100, (rojo * 1.2 + fx * 0.6) % 1.2)
            s.append(globulo(gx, y, sc, t * 3 + f, rojo))
    return "".join(s)


# ---------------- sangre ----------------
def globulo(x, y, s, giro, op=1.0):
    ry = 56 * (0.35 + 0.65 * abs(math.cos(giro)))
    return (f"<g transform='translate({x:.0f},{y:.0f}) rotate({20 * math.sin(giro * 0.5):.0f}) scale({s:.2f})' opacity='{op:.2f}'>"
            f"<ellipse rx='60' ry='{ry:.0f}' fill='#e3263a' stroke='{INK}' stroke-width='6'/>"
            f"<ellipse rx='30' ry='{ry * 0.45:.0f}' fill='#b5162a'/>"
            f"<path d='M-40 {-ry * 0.55:.0f} Q-10 {-ry * 0.9:.0f} 25 {-ry * 0.7:.0f}' fill='none' stroke='#ff7a85' stroke-width='6' stroke-linecap='round'/></g>")


def latido(t):
    k = (t % 0.85) / 0.85
    return math.exp(-k * 9) + 0.5 * math.exp(-max(0, k - 0.22) * 12) * (k > 0.22)


def corazon_grande(x, y, s, t):
    b = 1 + 0.1 * latido(t)
    parp = 0.15 if (t % 3.4) < 0.13 else 1
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s * b:.3f})'>"
            f"<path d='M-40 -150 Q-40 -260 60 -260 Q150 -260 150 -170' fill='none' stroke='{INK}' stroke-width='62' stroke-linecap='round'/>"
            f"<path d='M-40 -150 Q-40 -260 60 -260 Q150 -260 150 -170' fill='none' stroke='#ff4d5e' stroke-width='44' stroke-linecap='round'/>"
            f"<path d='M-110 -140 L-110 -240' stroke='{INK}' stroke-width='56' stroke-linecap='round'/>"
            f"<path d='M-110 -140 L-110 -240' stroke='#4d7cff' stroke-width='38' stroke-linecap='round'/>"
            f"<path d='M0 200 C-260 40 -230 -190 -60 -150 Q-20 -140 0 -100 Q20 -140 60 -150 C230 -190 260 40 0 200 Z' fill='#e63946' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M-150 -60 Q-140 -120 -90 -125' fill='none' stroke='#ff8a95' stroke-width='14' stroke-linecap='round'/>"
            f"<path d='M10 -95 Q-20 20 30 160' fill='none' stroke='#b51f2e' stroke-width='10' stroke-linecap='round'/>"
            f"<g transform='translate(-50,0) scale(1,{parp})'><circle r='18' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='3' cy='2' r='9' fill='{INK}'/></g>"
            f"<g transform='translate(55,0) scale(1,{parp})'><circle r='18' fill='#fff' stroke='{INK}' stroke-width='5'/><circle cx='3' cy='2' r='9' fill='{INK}'/></g>"
            f"<path d='M-22 50 Q2 72 26 50' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>")


def botella(x, y, k, op):
    """Botella de un litro que se llena de sangre (k de 0 a 1)."""
    alto = 190
    return (f"<g transform='translate({x:.0f},{y:.0f})' opacity='{op:.2f}'>"
            f"<rect x='-45' y='{-alto + alto * (1 - k):.0f}' width='90' height='{alto * k:.0f}' fill='#d62839'/>"
            f"<path d='M-45 0 L-45 -150 Q-45 -175 -20 -185 L-20 -215 L20 -215 L20 -185 Q45 -175 45 -150 L45 0 Z' fill='#ffffff' fill-opacity='0.25' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<rect x='-26' y='-238' width='52' height='26' rx='6' fill='#4d7cff' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-30 -140 L-30 -30' stroke='#fff' stroke-width='7' stroke-linecap='round' opacity='0.7'/></g>")


CIRC = [(0, 410), (-10, 250), (0, 120), (10, 250), (28, 410), (100, 520), (90, 900), (70, 1000), (40, 900), (28, 600), (28, 410)]


def esc_sangre(t, dur, m):
    b = latido(t)
    s = [fondo("plasma", "#ffc2b3", "#ff9b8c")]
    # paredes del vaso sanguíneo, que se ensanchan con cada latido
    e = 14 * b
    s.append(f"<path d='M0 0 L{W} 0 L{W} {250 - e:.0f} " + " ".join(f"Q{W - 120 - i * 240} {270 - e + 18 * math.sin(t * 2 + i):.0f} {W - 240 - i * 240} {250 - e:.0f}" for i in range(8)) +
             f" Z' fill='#b3202f' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1080 L{W} 1080 L{W} {860 + e:.0f} " + " ".join(f"Q{W - 120 - i * 240} {840 + e + 18 * math.sin(t * 2 + i):.0f} {W - 240 - i * 240} {860 + e:.0f}" for i in range(8)) +
             f" Z' fill='#b3202f' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(6):
        x = (i * 360 - t * 200) % (W + 360) - 180
        s.append(f"<path d='M{x:.0f} 120 q60 -30 120 0' fill='none' stroke='#d94656' stroke-width='12' stroke-linecap='round'/>"
                 f"<path d='M{x + 160:.0f} 960 q60 30 120 0' fill='none' stroke='#d94656' stroke-width='12' stroke-linecap='round'/>")
    panel = seg(t, m[4] - 0.3, m[4] + 0.5)
    cora = seg(t, m[2] - 0.2, m[2] + 0.8) * (1 - panel)
    vel = 300 * (1 + 1.2 * b)
    pos = t * 300 + 0.25 * (t // 0.85) * 300
    for i, (fx, y, sc, f) in enumerate(GLOB):
        x = (fx * (W + 300) - pos * (1 + (i % 3) * 0.15)) % (W + 300) - 150
        s.append(globulo(x, y + 15 * math.sin(t + f), sc, t * 2 + f, 1 - 0.6 * max(cora, panel) * (i % 2)))
    # Pildo arrastrado por la corriente
    px = lerp(-260, 400, seg(t, 0, 1.8)) + 25 * math.sin(t * 1.3) + 25 * b
    py = 560 + 25 * math.sin(t * 1.1)
    # corazón (frase 2) y 5 botellas de un litro (frase 3)
    if cora > 0:
        s.append(f"<g opacity='{cora:.2f}'>{corazon_grande(1440, 600, 0.95 * (0.6 + 0.4 * ease(cora)), t)}</g>")
        for i in range(3):
            k = ((t % 0.85) / 0.85 + i * 0.1)
            if k < 0.6:
                s.append(f"<path d='M{1700 + k * 120:.0f} {420 + i * 120:.0f} q30 40 0 80' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round' opacity='{(1 - k / 0.6) * cora:.2f}'/>")
        bot = seg(t, m[3] - 0.2, m[3] + 0.3)
        for i in range(5):
            llena = seg(t, m[3] + 0.2 + i * 0.5, m[3] + 0.8 + i * 0.5)
            s.append(botella(700 + i * 118, 830, llena, bot * cora))
    # gran momento (frase 4): la sangre da la vuelta al cuerpo en un minuto
    if panel > 0:
        k = seg(t, m[4] + 0.4, m[4] + 4.0)
        s.append(f"<g opacity='{panel:.2f}'>")
        s.append(f"<rect x='640' y='270' width='1180' height='600' rx='60' fill='#fff4ec' fill-opacity='0.9' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(cuerpo(1450, 300, 0.52, t, brillo=0.5, cara=True))
        # bucle de circulación
        pts = [(1450 + x * 0.52, 300 + y * 0.52) for x, y in CIRC]
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        s.append(f"<path d='{d}' fill='none' stroke='#e3263a' stroke-width='10' stroke-dasharray='18 14' stroke-linejoin='round'/>")
        tot = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        dd, obj = 0, k * tot
        for i in range(len(pts) - 1):
            L = math.dist(pts[i], pts[i + 1])
            if dd + L >= obj:
                q = (obj - dd) / L
                gx, gy = lerp(pts[i][0], pts[i + 1][0], q), lerp(pts[i][1], pts[i + 1][1], q)
                break
            dd += L
        else:
            gx, gy = pts[-1]
        s.append(f"<circle cx='{gx:.0f}' cy='{gy:.0f}' r='30' fill='#ff4d5e' opacity='0.35'/>"
                 f"<ellipse cx='{gx:.0f}' cy='{gy:.0f}' rx='20' ry='14' fill='#e3263a' stroke='{INK}' stroke-width='5'/>")
        s.append(cronometro(1000, 600, 360 * k, panel, 1.35))
        s.append(destellos(1000, 600, seg(t, m[4] + 4.0, m[4] + 5.5), 12, 240))
        s.append("</g>")
        px = lerp(px, 330, panel); py = lerp(py, 560, panel)
    s.append(pildo(px, py, 0.8 * (1 - 0.25 * panel), t, ang=6 * math.sin(t * 2), guino=(m[1] + 1.5 < t < m[1] + 1.9)))
    return "".join(s)


# ---------------- pulmones ----------------
RACIMOS = [(1180, 480, 1.0), (1520, 430, 0.9), (1330, 720, 1.05), (900, 700, 0.85), (1700, 700, 0.8), (760, 430, 0.75)]
RAMAS = [((1250, 120), (1180, 480)), ((1250, 120), (1520, 430)), ((1180, 480), (1330, 720)), ((1180, 480), (900, 700)),
         ((1520, 430), (1700, 700)), ((1250, 120), (760, 430))]


def racimo(x, y, s, t, aire, op=1.0):
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s * aire:.3f})' opacity='{op:.2f}'>"]
    for i, (dx, dy) in enumerate(((0, 0), (-70, -30), (70, -30), (-55, 55), (55, 55), (0, -80), (0, 95))):
        g.append(f"<circle cx='{dx}' cy='{dy}' r='52' fill='#ff8fa8' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M{dx - 28} {dy - 18} Q{dx - 16} {dy - 36} {dx + 4} {dy - 36}' fill='none' stroke='#ffd1dc' stroke-width='7' stroke-linecap='round'/>")
    for k in range(3):   # capilares
        g.append(f"<path d='M{-110 + k * 20} {-60 + k * 60} Q0 {-20 + k * 40 + 20 * math.sin(t + k)} {110 - k * 15} {-40 + k * 50}' fill='none' stroke='#d62839' stroke-width='5' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g)


def pista(k, t, op):
    """Pista de bádminton en perspectiva con red y volante (aparece de 0 a 1)."""
    if k <= 0:
        return ""
    def P(u, v):   # u: largo (0-1, izquierda a derecha), v: ancho (0 cerca, 1 lejos)
        y = lerp(905, 545, v)
        xl, xr = lerp(300, 620, v), lerp(1620, 1520, v)
        return (lerp(xl, xr, u), y)
    def L(a, b):
        return f"M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}"
    sc = 0.4 + 0.6 * ease(k)
    s = [f"<g opacity='{op * min(1, k * 2):.2f}' transform='translate(960,730) scale({sc:.3f}) translate(-960,-730)'>"]
    q = [P(0, 0), P(1, 0), P(1, 1), P(0, 1)]
    s.append(f"<path d='M{q[0][0]:.0f} {q[0][1]:.0f} L{q[1][0]:.0f} {q[1][1]:.0f} L{q[2][0]:.0f} {q[2][1]:.0f} L{q[3][0]:.0f} {q[3][1]:.0f} Z' fill='#3fae5a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    lineas = [L(P(0, 0.08), P(1, 0.08)), L(P(0, 0.92), P(1, 0.92)), L(P(0.35, 0), P(0.35, 1)), L(P(0.65, 0), P(0.65, 1)),
              L(P(0.06, 0), P(0.06, 1)), L(P(0.94, 0), P(0.94, 1)), L(P(0, 0.5), P(0.35, 0.5)), L(P(0.65, 0.5), P(1, 0.5))]
    s.append(f"<path d='{' '.join(lineas)}' stroke='#ffffff' stroke-width='7'/>")
    # red
    a, b = P(0.5, 0), P(0.5, 1)
    s.append(f"<path d='M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f} L{b[0]:.0f} {b[1] - 95:.0f} L{a[0]:.0f} {a[1] - 135:.0f} Z' fill='#ffffff' fill-opacity='0.25' stroke='{INK}' stroke-width='5'/>")
    for i in range(1, 8):
        v = i / 8; c = P(0.5, v); hh = lerp(135, 95, v)
        s.append(f"<line x1='{c[0]:.0f}' y1='{c[1]:.0f}' x2='{c[0]:.0f}' y2='{c[1] - hh:.0f}' stroke='#ffffff' stroke-width='3' opacity='0.8'/>")
    s.append(f"<line x1='{a[0]:.0f}' y1='{a[1] - 135:.0f}' x2='{b[0]:.0f}' y2='{b[1] - 95:.0f}' stroke='#ffffff' stroke-width='10'/>")
    for c, hh in ((a, 135), (b, 95)):
        s.append(f"<rect x='{c[0] - 7:.0f}' y='{c[1] - hh - 8:.0f}' width='14' height='{hh + 8:.0f}' fill='#ffd23f' stroke='{INK}' stroke-width='4'/>")
    # volante que va y viene por encima de la red
    f = (t * 0.45) % 2
    u = f if f < 1 else 2 - f
    vx = lerp(560, 1380, ease(u)); vy = 640 - 210 * math.sin(math.pi * ease(u))
    giro = 90 if f < 1 else -90
    s.append(f"<g transform='translate({vx:.0f},{vy:.0f}) rotate({giro + 30 * math.sin(math.pi * u):.0f})'>"
             f"<path d='M-26 -30 L26 -30 L10 10 L-10 10 Z' fill='#ffffff' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
             f"<circle cx='0' cy='20' r='14' fill='#ff6b6b' stroke='{INK}' stroke-width='5'/></g>")
    s.append("</g>")
    return "".join(s)


def esc_pulmones(t, dur, m):
    aire = 1 + 0.1 * math.sin(t * 1.7)
    s = [fondo("pulm", "#ffd9e1", "#ffb3c4")]
    for i in range(7):   # fondo de tejido esponjoso
        x = (i * 300 + 40 * math.sin(t * 0.5 + i)) % W
        s.append(f"<circle cx='{x:.0f}' cy='{200 + (i * 211) % 700}' r='{150 + 20 * math.sin(t * 1.7 + i):.0f}' fill='#ffc4d1' opacity='0.6'/>")
    pista_k = seg(t, m[3] - 0.2, m[3] + 1.4)
    tejido = 1 - pista_k * 0.75
    # bronquiolos (tubos) con anillos
    for (a, b) in RAMAS:
        d = f"M{a[0]} {a[1]} Q{(a[0] + b[0]) / 2 + 40} {(a[1] + b[1]) / 2 - 30} {b[0]} {b[1]}"
        s.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='58' stroke-linecap='round' opacity='{tejido:.2f}'/>"
                 f"<path d='{d}' fill='none' stroke='#fbe3e8' stroke-width='42' stroke-linecap='round' opacity='{tejido:.2f}'/>"
                 f"<path d='{d}' fill='none' stroke='#f2b8c6' stroke-width='42' stroke-dasharray='6 26' opacity='{tejido:.2f}'/>")
    # oxígeno que entra (bolitas azules)
    for i in range(14):
        a, b = RAMAS[i % len(RAMAS)]
        k = (t * 0.5 + i / 14) % 1
        x, y = lerp(a[0], b[0], k), lerp(a[1], b[1], k)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='11' fill='#4cc9f0' stroke='{INK}' stroke-width='3' opacity='{tejido:.2f}'/>")
    # racimos de alvéolos: aparecen más con la cifra (frase 1) y se esparcen para formar la pista (frase 3)
    mas = seg(t, m[1], m[1] + 2.0)
    for i, (x, y, sc) in enumerate(RACIMOS):
        ap = 1.0 if i < 3 else seg(mas, (i - 3) / 3, (i - 2) / 3)
        if ap <= 0:
            continue
        xx = lerp(x, 960 + (x - 1180) * 1.8, pista_k); yy = lerp(y, 730, pista_k)
        s.append(racimo(xx, yy, sc * ap * (1 - 0.6 * pista_k), t, aire, op=1 - pista_k))
    s.append(pista(pista_k, t, 1.0))
    s.append(destellos(960, 700, seg(t, m[3] + 0.8, m[3] + 2.4), 14, 520, "#ffffff"))
    # Pildo empujado por el aire al respirar
    px = lerp(-260, 400, seg(t, 0, 1.8)) + 30 * math.sin(t * 1.7)
    py = lerp(560, 330, pista_k) + 20 * math.sin(t * 1.2)
    s.append(pildo(px, py, 0.78 * (1 - 0.2 * pista_k), t, ang=5 * math.sin(t * 1.7), mira=pista_k * 0.8, guino=(m[4] + 0.5 < t < m[4] + 0.9)))
    # chispas eléctricas que anuncian la última parada (frase 5)
    ch = seg(t, m[5], m[5] + 0.8)
    if ch > 0:
        for i in range(6):
            k = ((t - m[5]) * 0.8 + i / 6) % 1
            s.append(chispa(lerp(W + 60, 1200, k), 300 + i * 90 + 30 * math.sin(t * 4 + i), 18, ch * (1 - k)))
    return "".join(s)


# ---------------- cerebro ----------------
NEUR = [(700, 380), (1060, 300), (1420, 400), (1700, 330), (860, 700), (1250, 640), (1600, 720), (560, 640)]
AXON = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (1, 5), (5, 2), (5, 6), (2, 6), (7, 4), (7, 0)]


def neurona(x, y, s, t, brillo):
    g = [f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"]
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.3
        x1, y1 = 75 * math.cos(a), 75 * math.sin(a)
        g.append(f"<path d='M0 0 L{x1:.0f} {y1:.0f} M{x1:.0f} {y1:.0f} l{25 * math.cos(a + 0.6):.0f} {25 * math.sin(a + 0.6):.0f} "
                 f"M{x1:.0f} {y1:.0f} l{25 * math.cos(a - 0.6):.0f} {25 * math.sin(a - 0.6):.0f}' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
                 f"<path d='M0 0 L{x1:.0f} {y1:.0f} M{x1:.0f} {y1:.0f} l{25 * math.cos(a + 0.6):.0f} {25 * math.sin(a + 0.6):.0f} "
                 f"M{x1:.0f} {y1:.0f} l{25 * math.cos(a - 0.6):.0f} {25 * math.sin(a - 0.6):.0f}' stroke='#c77dff' stroke-width='8' stroke-linecap='round'/>")
    g.append(f"<circle r='{60 + 10 * brillo:.0f}' fill='#fff176' opacity='{0.35 * brillo:.2f}'/>")
    g.append(f"<path d='M-38 -8 Q-30 -40 0 -38 Q36 -40 40 -6 Q42 30 6 38 Q-36 40 -38 -8 Z' fill='{mix('#e0aaff', '#fff59d', brillo)}' stroke='{INK}' stroke-width='7'/>"
             f"<circle cx='4' cy='0' r='13' fill='#7b2cbf' stroke='{INK}' stroke-width='4'/>")
    g.append("</g>")
    return "".join(g)


def coche(x, y, s, t):
    """Coche de carreras genérico de ruedas descubiertas (sin marcas)."""
    r = (t * 900) % 360
    rueda = lambda cx: (f"<g transform='translate({cx},28) rotate({r:.0f})'><circle r='42' fill='#222' stroke='{INK}' stroke-width='6'/>"
                        f"<circle r='16' fill='#9aa3ad'/><line x1='-30' y1='0' x2='30' y2='0' stroke='#555' stroke-width='6'/></g>")
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({s:.2f})'>"
            f"<rect x='-190' y='-70' width='40' height='70' fill='#d62828' stroke='{INK}' stroke-width='6'/>"
            f"<rect x='-215' y='-84' width='80' height='22' rx='4' fill='#d62828' stroke='{INK}' stroke-width='6'/>"
            + rueda(-125) +
            f"<path d='M-170 30 L-170 -10 Q-100 -40 -10 -40 L40 -62 L80 -62 L90 -30 Q170 -20 230 10 L250 30 Z' fill='#e63946' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-100 0 L180 6' stroke='#ffffff' stroke-width='10' stroke-linecap='round'/>"
            f"<circle cx='50' cy='-62' r='24' fill='#ffd23f' stroke='{INK}' stroke-width='6'/><rect x='52' y='-74' width='24' height='12' rx='4' fill='#1e2a38'/>"
            f"<rect x='215' y='20' width='70' height='16' rx='4' fill='#d62828' stroke='{INK}' stroke-width='5'/>"
            + rueda(150) + "</g>")


def esc_cerebro(t, dur, m):
    s = [fondo("cer", "#2b1055", "#120628")]
    for i in range(6):   # pliegues del cerebro al fondo
        y = 150 + i * 160
        ola = "".join(f"Q{100 + k * 200} {y + 50 * math.sin(k * 1.3 + i)} {200 + k * 200} {y} " for k in range(10))
        s.append(f"<path d='M0 {y} {ola}' fill='none' stroke='#4a2280' stroke-width='26' stroke-linecap='round' opacity='0.6'/>")
    nervio = seg(t, m[2] - 0.2, m[2] + 1.0)
    red = 1 - nervio
    if red > 0:   # red de neuronas con mensajes eléctricos
        s.append(f"<g opacity='{red:.2f}'>")
        for a, b in AXON:
            (x1, y1), (x2, y2) = NEUR[a], NEUR[b]
            s.append(f"<path d='M{x1} {y1} Q{(x1 + x2) / 2} {(y1 + y2) / 2 - 60} {x2} {y2}' fill='none' stroke='{INK}' stroke-width='16'/>"
                     f"<path d='M{x1} {y1} Q{(x1 + x2) / 2} {(y1 + y2) / 2 - 60} {x2} {y2}' fill='none' stroke='#9d4edd' stroke-width='8'/>")
        for i, (a, b) in enumerate(AXON):
            k = (t * 0.9 + i * 0.37) % 1
            (x1, y1), (x2, y2) = NEUR[a], NEUR[b]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2 - 60
            px = (1 - k) ** 2 * x1 + 2 * (1 - k) * k * cx + k ** 2 * x2
            py = (1 - k) ** 2 * y1 + 2 * (1 - k) * k * cy + k ** 2 * y2
            if t > m[1] - 0.5 or i % 3 == 0:
                s.append(chispa(px, py, 12))
        for i, (x, y) in enumerate(NEUR):
            br = max(0.0, math.sin(t * 2.5 + i * 1.3)) * seg(t, m[1] - 0.5, m[1] + 0.5) + 0.2
            s.append(neurona(x, y, 0.9 + 0.1 * (i % 2), t, min(1, br)))
        s.append("</g>")
    if nervio > 0:   # un nervio largo (con mielina) y, debajo, la carrera
        s.append(f"<g opacity='{nervio:.2f}'>")
        s.append(f"<path d='M-40 520 L1960 520' stroke='{INK}' stroke-width='40' stroke-linecap='round'/>"
                 f"<path d='M-40 520 L1960 520' stroke='#9d4edd' stroke-width='24'/>")
        for i in range(12):
            x = i * 170 - 40
            s.append(f"<rect x='{x + 14}' y='488' width='142' height='64' rx='32' fill='#fff3c4' stroke='{INK}' stroke-width='6'/>")
        carrera = seg(t, m[4] - 0.4, m[4] + 3.2)
        k1 = (t - m[2]) * 0.6 % 1 if carrera <= 0 else min(1.0, carrera * 1.25)
        sx_ = lerp(-200, 2150, k1 if carrera <= 0 else carrera ** 1.6 * 1.05)
        for j in range(7):
            s.append(chispa(sx_ - j * 55, 520, 26 - j * 3, 1 - j / 7))
        s.append(chispa(sx_, 520, 34))
        pista_ = seg(t, m[3] + 1.0, m[4])
        if pista_ > 0:
            s.append(f"<g opacity='{pista_:.2f}'><rect x='0' y='790' width='{W}' height='110' fill='#4a4e69' stroke='{INK}' stroke-width='{LW}'/>")
            for i in range(10):
                x = (i * 240 - t * 900 * (1 if carrera > 0 else 0.2)) % (W + 240) - 120
                s.append(f"<rect x='{x:.0f}' y='838' width='120' height='14' rx='6' fill='#ffffff'/>")
            s.append("</g>")
            cx_ = lerp(-300, 1500, carrera) if carrera > 0 else lerp(-300, 260, pista_)
            for j in range(4):
                s.append(f"<line x1='{cx_ - 230 - j * 30:.0f}' y1='{760 + j * 14}' x2='{cx_ - 380 - j * 50:.0f}' y2='{760 + j * 14}' stroke='#ffffff' stroke-width='6' stroke-linecap='round' opacity='{0.6 * pista_:.2f}'/>")
            s.append(coche(cx_, 760, 0.95, t))
            if carrera > 0:
                adel = seg(t, m[4] + 2.0, m[4] + 3.4)
                s.append(destellos(1250, 520, adel, 12, 260))
        s.append("</g>")
    # Pildo
    px = lerp(-260, 380, seg(t, 0, 1.8)) + 20 * math.sin(t * 1.2)
    py = lerp(560, 300, nervio) + 18 * math.sin(t * 1.5)
    s.append(pildo(px, py, 0.75 * (1 - 0.2 * nervio), t, ang=5 * math.sin(t * 1.4), mira=0.8 * nervio,
                   guino=(m[5] + 0.6 < t < m[5] + 1.0)))
    return "".join(s)


# ---------------- despedida ----------------
def cursor(x, y, s=1.0):
    return (f"<path transform='translate({x:.0f},{y:.0f}) scale({s:.2f})' d='M0 0 L0 80 L20 62 L34 94 L48 88 L34 56 L60 56 Z' "
            f"fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")


def campana_grande(cx, cy, s, ang):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='#e62117' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='#e62117' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='#e62117' stroke='{INK}' stroke-width='3'/></g>")


def esc_final(t, dur, m):
    tarde = seg(t, 0, 5)
    s = [fondo("atar", mix("#7fd3ff", "#ff9a76", tarde), mix("#e3f7ff", "#ffe0a8", tarde))]
    s.append(f"<circle cx='300' cy='{lerp(260, 420, tarde):.0f}' r='90' fill='#ffd166' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (cx, cy, sc) in enumerate([(500, 200, 1.1), (1300, 150, 0.9), (1800, 260, 1.0)]):
        x = (cx + t * 15 * (1 + i * 0.3)) % 2300 - 300
        s.append(f"<g transform='translate({x:.0f},{cy}) scale({sc})'><path d='M0 40 Q15 -10 70 5 Q100 -40 160 0 Q220 -10 235 40 Z' fill='#fff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    s.append(f"<path d='M0 820 Q400 700 900 790 T1920 760 L1920 1080 L0 1080 Z' fill='#7cc66b' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M0 930 Q500 860 1000 920 T1920 900 L1920 1080 L0 1080 Z' fill='#5aa84e'/>")
    for i in range(7):   # florecitas
        fx = 120 + i * 270; fy = 900 + 30 * math.sin(i * 2)
        s.append(f"<g transform='translate({fx},{fy}) rotate({8 * math.sin(t * 2 + i):.0f})'><line x1='0' y1='0' x2='0' y2='40' stroke='{INK}' stroke-width='6'/>"
                 + "".join(f"<circle cx='{14 * math.cos(a * 1.2566):.0f}' cy='{14 * math.sin(a * 1.2566):.0f}' r='11' fill='{['#ff7eb6', '#ffd23f', '#9b5de5'][i % 3]}' stroke='{INK}' stroke-width='4'/>" for a in range(5))
                 + f"<circle r='8' fill='#fff' stroke='{INK}' stroke-width='4'/></g>")
    # Pildo sale y recupera su tamaño
    crece = seg(t, 0.2, 2.2)
    px = lerp(560, 470, seg(t, m[1] - 0.5, m[1] + 1.0)); py = 640 + 18 * math.sin(t * 2)
    s.append(destellos(px, py, seg(t, 0.8, 2.6), 12, 240))
    s.append(pildo(px, py, lerp(0.2, 0.95, crece), t, ang=6 * math.sin(t * 1.6), guino=(m[3] + 0.4 < t < m[3] + 0.8)))
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
    {"titulo": "¿Qué pasa dentro de tu cuerpo?", "escena": esc_intro, "susc": 3,
     "frases": ["Ahora mismo, en tu cabeza, viajan mensajes más rápidos que un coche de carreras.",
                "Hoy nos hacemos diminutos para viajar por tu cuerpo con Pildo, nuestra nave cápsula.",
                "Y ojo: la última parada te dejará con la boca abierta.",
                "¡Suscríbete, y allá vamos!"]},
    {"titulo": "1. Un lago de ácido", "escena": esc_estomago, "tarjeta": "CAPÍTULO 1 · UN LAGO DE ÁCIDO",
     "frases": ["Primera parada: entramos por la boca y caemos… ¡al estómago!",
                "Las paredes se mueven sin parar, y abajo burbujea un lago de jugos.",
                "Es ácido clorhídrico, y es tan fuerte que puede disolver algunos metales, como el zinc.",
                "Entonces, ¿por qué el estómago no se disuelve a sí mismo?",
                "Porque se cubre con una capa de moco protectora, que fabrica sin parar."],
     "grandes": {2: "¡DISUELVE METAL!"}, "extra": 0.8},
    {"titulo": "2. Un intestino lleno de vida", "escena": esc_intestino, "tarjeta": "CAPÍTULO 2 · LLENO DE VIDA",
     "frases": ["Seguimos por un túnel larguísimo y lleno de pliegues: el intestino.",
                "¡Y está lleno de vida! Son bacterias, de todas las formas y colores.",
                "En tu cuerpo viven unos treinta y ocho billones de bacterias.",
                "¡Casi tantas como células tiene tu propio cuerpo!",
                "Y tranquilo: la mayoría son amigas, y te ayudan a digerir la comida.",
                "Pero de repente, Pildo se cuela en un río rojo…"],
     "grandes": {2: "38 BILLONES"}},
    {"titulo": "3. La vuelta al cuerpo en un minuto", "escena": esc_sangre, "tarjeta": "CAPÍTULO 3 · EL RÍO ROJO",
     "frases": ["Estamos dentro de un vaso sanguíneo, y la corriente nos arrastra.",
                "Estos discos rojos son glóbulos rojos: llevan el oxígeno a todo el cuerpo.",
                "Al fondo suena un tambor: ¡pum, pum! Es el corazón.",
                "Cada minuto bombea unos cinco litros de sangre, más o menos toda la que tienes.",
                "¡Así que tu sangre da la vuelta completa a tu cuerpo en más o menos un minuto!"],
     "grandes": {3: "5 LITROS", 4: "1 MINUTO"}, "extra": 1.5},
    {"titulo": "4. Una pista dentro del pecho", "escena": esc_pulmones, "tarjeta": "CAPÍTULO 4 · LOS PULMONES",
     "frases": ["La corriente nos lleva hasta los pulmones.",
                "Aquí hay unos cuatrocientos ochenta millones de saquitos de aire llamados alvéolos.",
                "Parecen racimos de uvas que se inflan cada vez que respiras.",
                "Si pudiéramos extenderlos todos, ocuparían unos setenta metros cuadrados…",
                "¡Casi una pista de bádminton entera, guardada dentro de tu pecho!",
                "Pero lo que nos espera en la última parada es todavía más increíble…"],
     "grandes": {1: "480 MILLONES", 3: "70 m²"}},
    {"titulo": "5. Más rápido que un coche de carreras", "escena": esc_cerebro, "tarjeta": "CAPÍTULO 5 · MENSAJES A TODA VELOCIDAD",
     "frases": ["Última parada: el cerebro.",
                "Aquí, miles de millones de neuronas se mandan mensajes eléctricos sin parar.",
                "Cuando decides mover un dedo, la orden baja por tus nervios como un rayo.",
                "En los nervios más rápidos, esos mensajes viajan a unos cuatrocientos treinta kilómetros por hora.",
                "¡Más rápido que un coche de Fórmula uno!",
                "Por eso, si tocas algo que quema, apartas la mano antes de pensarlo."],
     "grandes": {3: "430 KM/H", 4: "¡MÁS QUE UN F1!"}},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje de hoy por dentro del cuerpo humano.",
                "Si has descubierto algo nuevo, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
