"""Episodio: "Viaje por el sistema solar" con Nova, un pequeño cohete explorador original.

Datos (verificados el 22-11-2026):
- En el Sol cabrían unos 1,3 millones de Tierras (por volumen): "it would take 1.3 million Earths to fill
  the Sun's volume" (NASA Science «Sun: Facts»).
- Mercurio da una vuelta al Sol cada 88 días terrestres (su año), pero un día solar completo (día y noche,
  de un amanecer al siguiente) dura 176 días terrestres: unos dos años de Mercurio (NASA Science «Mercury: Facts»).
- Ío, luna de Júpiter, es el cuerpo con más actividad volcánica del sistema solar, con cientos de volcanes
  activos (más de 400); la gravedad de Júpiter la estira y la aprieta y eso calienta su interior (calentamiento
  por mareas) (NASA Science «Europa: Facts» / «Io»; The Planetary Society «Io»).
- Europa, otra luna de Júpiter, esconde bajo una capa de hielo de unos 15-25 km un océano que podría tener
  el doble de agua que el océano de la Tierra; es uno de los lugares más prometedores para buscar entornos
  aptos para la vida (NASA Science «Europa: Facts»; NASA Europa Clipper).
- Neptuno es el planeta con más viento del sistema solar: más de 2.000 km/h (NASA; Guinness World Records
  da unos 2.400 km/h, medidos por la Voyager 2 en 1989); los vientos más fuertes de la Tierra rondan los
  400 km/h (NASA Science «Neptune: Facts»).
"""
import math
import numpy as np
from lib import INK, LW, clamp, ease, seg, lerp, mix

ID = "2026-11-22-historia"
TITULO = "Viaje por el sistema solar"
VOZ = "ef_dora"
VELOCIDAD = 0.93
MUSICA = 61

W, H = 1920, 1080
rng = np.random.default_rng(22)
ESTRELLAS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 4.2), rng.uniform(0, 6.3)) for _ in range(110)]
RAPIDAS = [(rng.uniform(0, 1), rng.uniform(250, 950), rng.uniform(0.6, 1.4)) for _ in range(30)]
CRATERES = [(rng.uniform(0, 6.28), rng.uniform(0.1, 0.85), rng.uniform(0.07, 0.17)) for _ in range(16)]
GRIETAS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28), rng.uniform(0.5, 1.1)) for _ in range(9)]
VOLC = [(rng.uniform(0, 6.28), rng.uniform(0.15, 0.85)) for _ in range(14)]


# ================= piezas comunes =================
def espacio(t, top="#0b0a2e", bot="#2a1559", vel=0.0, neb=True):
    """Fondo de espacio: degradado, nebulosas suaves, estrellas que titilan y, si vel>0, estrellas fugaces."""
    s = [f"<defs><linearGradient id='esp' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
         f"<stop offset='1' stop-color='{bot}'/></linearGradient>"
         "<radialGradient id='neb'><stop offset='0' stop-color='#ff5ad8' stop-opacity='0.22'/>"
         "<stop offset='1' stop-color='#ff5ad8' stop-opacity='0'/></radialGradient>"
         "<radialGradient id='neb2'><stop offset='0' stop-color='#3ad1ff' stop-opacity='0.2'/>"
         "<stop offset='1' stop-color='#3ad1ff' stop-opacity='0'/></radialGradient></defs>",
         f"<rect width='{W}' height='{H}' fill='url(#esp)'/>"]
    if neb:
        s.append(f"<ellipse cx='{1500 + 40 * math.sin(t * 0.2):.0f}' cy='260' rx='520' ry='260' fill='url(#neb)'/>"
                 f"<ellipse cx='{500 + 40 * math.cos(t * 0.25):.0f}' cy='820' rx='600' ry='280' fill='url(#neb2)'/>")
    for x, y, r, f in ESTRELLAS:
        a = 0.45 + 0.45 * math.sin(t * 2.2 + f * 3)
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    if vel > 0.01:
        for u, y, v in RAPIDAS:
            x = W + 200 - ((u * W + t * 1400 * v * vel) % (W + 400))
            largo = 120 * vel * v
            s.append(f"<line x1='{x:.0f}' y1='{y:.0f}' x2='{x + largo:.0f}' y2='{y:.0f}' stroke='#cfe8ff' stroke-width='4' "
                     f"stroke-linecap='round' opacity='{0.7 * vel:.2f}'/>")
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


def estrellita(x, y, r, op=1.0, col="#fff176"):
    return (f"<g transform='translate({x:.0f},{y:.0f})' opacity='{op:.2f}'><circle r='{r * 2.4:.0f}' fill='{col}' opacity='0.3'/>"
            f"<path d='M0 {-r * 1.7:.0f} L{r * 0.4:.0f} {-r * 0.4:.0f} L{r * 1.7:.0f} 0 L{r * 0.4:.0f} {r * 0.4:.0f} L0 {r * 1.7:.0f} "
            f"L{-r * 0.4:.0f} {r * 0.4:.0f} L{-r * 1.7:.0f} 0 L{-r * 0.4:.0f} {-r * 0.4:.0f} Z' fill='#fffde7' stroke='{col}' stroke-width='4'/></g>")


def nova(x, y, s, t, ang=0.0, fuego=1.0, guino=False, mira=0.0, susto=0.0, sudor=0.0):
    """Nova: cohetito blanco con punta rosa, franja turquesa, aletas rosas y dos ojos grandes junto a la punta.
    Apunta hacia la derecha (+x); el fuego sale por detrás."""
    parp = 0.12 if ((t + 0.9) % 3.4) < 0.13 or guino else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"]
    if fuego > 0.01:
        fl = (80 + 28 * math.sin(t * 31)) * fuego
        g.append(f"<path d='M-168 -40 Q{-168 - fl * 1.25:.0f} {6 * math.sin(t * 23):.0f} -168 40 Z' fill='#ff7b2e' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M-168 -26 Q{-168 - fl * 0.85:.0f} 0 -168 26 Z' fill='#ffd23f'/>"
                 f"<path d='M-168 -12 Q{-168 - fl * 0.45:.0f} 0 -168 12 Z' fill='#fffbe0'/>")
    # tobera
    g.append(f"<path d='M-140 -40 L-176 -52 L-176 52 L-140 40 Z' fill='#9aa3ad' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # aletas
    for sy in (-1, 1):
        g.append(f"<path d='M-40 {sy * 58} L-128 {sy * 128} L-170 {sy * 128} L-140 {sy * 58} Z' fill='#ff4f8b' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # cuerpo
    cuerpo = "M-145 -62 L95 -62 Q180 -46 218 0 Q180 46 95 62 L-145 62 Q-158 0 -145 -62 Z"
    g.append(f"<path d='{cuerpo}' fill='#f6f3ff'/>")
    g.append(f"<path d='M-150 30 L120 30 Q170 30 205 14 Q180 46 95 62 L-145 62 Q-152 46 -150 30 Z' fill='#dcd6f5'/>")
    g.append(f"<path d='M95 -62 Q180 -46 218 0 Q180 46 95 62 Q112 0 95 -62 Z' fill='#ff4f8b'/>")
    g.append(f"<path d='M110 -48 Q160 -36 190 -14' fill='none' stroke='#ffb3cf' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<rect x='-100' y='-62' width='34' height='124' fill='#2ec4b6'/>")
    g.append(f"<path d='M-130 -40 Q-40 -54 60 -50' fill='none' stroke='#fff' stroke-width='10' stroke-linecap='round' opacity='0.8'/>")
    g.append(f"<path d='{cuerpo}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<line x1='95' y1='-62' x2='95' y2='62' stroke='{INK}' stroke-width='6'/>"
             f"<line x1='-100' y1='-62' x2='-100' y2='62' stroke='{INK}' stroke-width='5'/><line x1='-66' y1='-62' x2='-66' y2='62' stroke='{INK}' stroke-width='5'/>")
    for rx in (-125, -20):
        for ry in (-44, 44):
            g.append(f"<circle cx='{rx}' cy='{ry}' r='4' fill='#b9b2d9'/>")
    # cara
    ojo_ry = 24 * (1 + 0.25 * susto)
    for ex in (12, 62):
        g.append(f"<g transform='translate({ex},-12) scale(1,{parp})'><ellipse rx='19' ry='{ojo_ry:.0f}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{5 + mira * 6:.0f}' cy='3' r='{11 - 3 * susto:.0f}' fill='#1e2a38'/><circle cx='{1 + mira * 6:.0f}' cy='-4' r='4' fill='#fff'/></g>")
    g.append(f"<circle cx='-14' cy='24' r='10' fill='#ff9ec0' opacity='0.8'/><circle cx='86' cy='24' r='10' fill='#ff9ec0' opacity='0.8'/>")
    if susto > 0.5:
        g.append(f"<ellipse cx='38' cy='34' rx='13' ry='11' fill='#7a2433' stroke='{INK}' stroke-width='5'/>")
    else:
        g.append(f"<path d='M20 26 Q38 44 58 26' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    if sudor > 0:
        for i, (dx, dy) in enumerate(((-30, -80), (110, -78))):
            k = ((t * 1.2 + i * 0.5) % 1)
            g.append(f"<path transform='translate({dx},{dy + 30 * k:.0f})' d='M0 -14 Q12 4 0 10 Q-12 4 0 -14 Z' fill='#8fd8ff' "
                     f"stroke='{INK}' stroke-width='4' opacity='{sudor * (1 - k):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def bola(id_, cx, cy, r, base, detalles="", sombra=0.5, luz_izq=True, borde=True):
    """Planeta o luna: círculo de color, detalles recortados dentro, lado de noche y contorno."""
    sx = cx + (r * 0.62 if luz_izq else -r * 0.62)
    s = [f"<defs><clipPath id='{id_}'><circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}'/></clipPath></defs>",
         f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}' fill='{base}'/>",
         f"<g clip-path='url(#{id_})'>{detalles}"
         f"<circle cx='{sx:.1f}' cy='{cy - r * 0.05:.1f}' r='{r * 1.05:.1f}' fill='#0b0a2e' opacity='{sombra:.2f}' "
         f"transform='translate({(r * 0.35 if luz_izq else -r * 0.35):.1f},0)'/>"
         f"<path d='M{cx - r * 0.62:.1f} {cy - r * 0.55:.1f} Q{cx - r * 0.3:.1f} {cy - r * 0.85:.1f} {cx + r * 0.05:.1f} {cy - r * 0.84:.1f}' "
         f"fill='none' stroke='#fff' stroke-width='{max(4, r * 0.05):.0f}' stroke-linecap='round' opacity='0.35'/></g>"]
    if borde:
        s.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(s)


def tierra(id_, cx, cy, r, t, giro=0.06, sombra=0.4):
    """La Tierra: océano azul, continentes verdes que giran y nubes blancas."""
    d = []
    for i, (u, v, w, h) in enumerate([(0.0, -0.35, 0.55, 0.38), (0.9, 0.25, 0.4, 0.55), (1.8, -0.1, 0.7, 0.32),
                                      (2.6, 0.45, 0.35, 0.25), (3.5, -0.5, 0.45, 0.3), (4.4, 0.1, 0.6, 0.45), (5.3, -0.25, 0.3, 0.5)]):
        x = cx + r * (((u + t * giro) % 6.283) / 3.1416 - 1) * 1.25
        d.append(f"<ellipse cx='{x:.0f}' cy='{cy + v * r:.0f}' rx='{w * r * 0.55:.0f}' ry='{h * r * 0.5:.0f}' fill='#4caf50' "
                 f"stroke='#2e7d32' stroke-width='{max(3, r * 0.025):.0f}' transform='rotate({(i * 37) % 60 - 30},{x:.0f},{cy + v * r:.0f})'/>")
    for i in range(5):
        x = cx + r * ((((i * 1.3 + t * giro * 1.6) % 6.283) / 3.1416) - 1) * 1.25
        d.append(f"<path d='M{x - r * 0.3:.0f} {cy + (i - 2) * r * 0.33:.0f} q{r * 0.15:.0f} {-r * 0.08:.0f} {r * 0.3:.0f} 0 t{r * 0.3:.0f} 0' fill='none' stroke='#fff' "
                 f"stroke-width='{max(4, r * 0.06):.0f}' stroke-linecap='round' opacity='0.85'/>")
    return bola(id_, cx, cy, r, "#2f8fe0", "".join(d), sombra)


# ================= capítulos =================
def esc_intro(t, dur, m):
    s = [espacio(t, vel=1 - seg(t, 1.2, 2.6) + seg(t, dur - 1.8, dur - 0.6))]
    # planeta con anillos lejano
    s.append(f"<g transform='translate(760,330) rotate(-18)'><ellipse rx='110' ry='26' fill='none' stroke='#ffcf8a' stroke-width='12'/>"
             f"<circle r='52' fill='#e9b36a' stroke='{INK}' stroke-width='7'/><path d='M-50 -10 Q0 0 50 -10' stroke='#c98a45' stroke-width='9' fill='none'/>"
             f"<path d='M-110 0 A110 26 0 0 0 110 0' fill='none' stroke='#ffcf8a' stroke-width='12'/></g>")
    # estrella fugaz desde el primer fotograma
    k = seg(t, 0, 1.6)
    if k < 1:
        x0, y0 = lerp(300, 1500, k), lerp(380, 520, k)
        s.append(f"<line x1='{x0:.0f}' y1='{y0:.0f}' x2='{x0 - 260:.0f}' y2='{y0 - 30:.0f}' stroke='#fff6a8' stroke-width='8' stroke-linecap='round' opacity='{1 - k:.2f}'/>"
                 + estrellita(x0, y0, 12, 1 - k))
    # la Tierra y la Luna
    la = t * 0.5
    lx, ly = 1450 + 430 * math.cos(la), 640 + 110 * math.sin(la)
    luna = bola("lun", lx, ly, 46, "#c9c3b8", "".join(f"<circle cx='{lx + dx}' cy='{ly + dy}' r='{rr}' fill='#a59f95'/>" for dx, dy, rr in ((-12, -10, 10), (14, 12, 8), (8, -22, 6))), 0.35)
    if math.sin(la) < 0:
        s.append(luna)
    s.append(f"<circle cx='1450' cy='640' r='{300 + 8 * math.sin(t * 2):.0f}' fill='#6fd0ff' opacity='0.15'/>")
    s.append(tierra("tie", 1450, 640, 270, t))
    if math.sin(la) >= 0:
        s.append(luna)
    # Nova entra, saluda, tiembla con la cuenta atrás y despega
    entra = seg(t, 0, 2.2)
    sale = seg(t, dur - 1.6, dur - 0.1)
    tiembla = seg(t, m[3], m[3] + 0.8) * (1 - sale)
    nx = lerp(160, 640, entra) + lerp(0, 1900, sale ** 2) + tiembla * 7 * math.sin(t * 60)
    ny = 600 + 28 * math.sin(t * 2.1) * (1 - tiembla) - lerp(0, 120, sale)
    nang = lerp(-8, 0, entra) + 4 * math.sin(t * 1.7) - 8 * sale
    ns = lerp(0.9, 1.05, seg(t, m[2], m[2] + 0.8))
    for i in range(7):   # estela
        kk = ((t * 2.2 + i / 7) % 1)
        s.append(f"<circle cx='{nx - 220 * ns - kk * 300:.0f}' cy='{ny + 18 * math.sin(t * 3 + i):.0f}' r='{16 * (1 - kk):.0f}' fill='#ffb36b' opacity='{0.7 * (1 - kk):.2f}'/>")
    s.append(nova(nx, ny, ns, t, ang=nang, fuego=0.8 + 0.6 * tiembla + 0.8 * sale, guino=(m[1] + 1.2 < t < m[1] + 1.6), mira=0.6 * seg(t, m[2], m[2] + 0.5)))
    s.append(destellos(nx, ny, seg(t, m[2] + 0.2, m[2] + 1.6), 10, 230))
    fl = seg(t, dur - 0.45, dur)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff6d0' opacity='{fl:.2f}'/>")
    return "".join(s)


def sol(cx, cy, r, t, brillo=1.0):
    s = ["<defs><radialGradient id='sol' cx='0.45' cy='0.42' r='0.6'><stop offset='0' stop-color='#fff3a0'/>"
         "<stop offset='0.6' stop-color='#ffb627'/><stop offset='1' stop-color='#ff7a1a'/></radialGradient>"
         "<radialGradient id='corona'><stop offset='0.55' stop-color='#ffcf4a' stop-opacity='0.55'/>"
         "<stop offset='1' stop-color='#ff7a1a' stop-opacity='0'/></radialGradient></defs>",
         f"<circle cx='{cx}' cy='{cy}' r='{r * (1.5 + 0.04 * math.sin(t * 2)):.0f}' fill='url(#corona)' opacity='{brillo:.2f}'/>"]
    # protuberancias (arcos de fuego en el borde)
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.4 + t * 0.05
        h = r * (0.18 + 0.1 * math.sin(t * 1.3 + i * 2))
        x1, y1 = cx + r * math.cos(a - 0.12), cy + r * math.sin(a - 0.12)
        x2, y2 = cx + r * math.cos(a + 0.12), cy + r * math.sin(a + 0.12)
        xc, yc = cx + (r + h * 2) * math.cos(a), cy + (r + h * 2) * math.sin(a)
        s.append(f"<path d='M{x1:.0f} {y1:.0f} Q{xc:.0f} {yc:.0f} {x2:.0f} {y2:.0f}' fill='none' stroke='#ff8a1f' stroke-width='{r * 0.06:.0f}' stroke-linecap='round'/>"
                 f"<path d='M{x1:.0f} {y1:.0f} Q{xc:.0f} {yc:.0f} {x2:.0f} {y2:.0f}' fill='none' stroke='#ffd166' stroke-width='{r * 0.025:.0f}' stroke-linecap='round'/>")
    s.append(f"<defs><clipPath id='csol'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath></defs>"
             f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='url(#sol)'/>")
    g = []
    for i in range(22):   # granulado que hierve
        a = i * 2.39996; d = r * math.sqrt((i + 0.5) / 22) * 0.95
        gx, gy = cx + d * math.cos(a), cy + d * math.sin(a)
        rr = r * (0.09 + 0.03 * math.sin(t * 3 + i))
        g.append(f"<circle cx='{gx:.0f}' cy='{gy:.0f}' r='{rr:.0f}' fill='#ffe27a' opacity='0.45'/>")
    g.append(f"<circle cx='{cx + r * 0.35:.0f}' cy='{cy + r * 0.2:.0f}' r='{r * 0.05:.0f}' fill='#c2410c' opacity='0.7'/>"
             f"<circle cx='{cx + r * 0.42:.0f}' cy='{cy + r * 0.27:.0f}' r='{r * 0.03:.0f}' fill='#c2410c' opacity='0.7'/>")
    s.append(f"<g clip-path='url(#csol)'>{''.join(g)}</g>")
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(s)


def mini_tierra(x, y, r, op=1.0):
    return (f"<g opacity='{op:.2f}'><circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='#2f8fe0' stroke='{INK}' stroke-width='{max(2, r * 0.14):.1f}'/>"
            f"<ellipse cx='{x - r * 0.25:.1f}' cy='{y - r * 0.15:.1f}' rx='{r * 0.45:.1f}' ry='{r * 0.35:.1f}' fill='#4caf50'/>"
            f"<ellipse cx='{x + r * 0.35:.1f}' cy='{y + r * 0.35:.1f}' rx='{r * 0.25:.1f}' ry='{r * 0.2:.1f}' fill='#4caf50'/></g>")


def esc_sol(t, dur, m):
    s = [espacio(t, "#1a0b2e", "#4a1a3a")]
    cx, cy, r = 1290, 640, 340
    z = lerp(0.82, 1.0, seg(t, 0, m[1] + 1.5))
    cuerpo = [sol(cx, cy, r, t)]
    # 1,3 millones de Tierras: se llena de tierritas desde el centro
    llena = seg(t, m[3] + 0.1, m[3] + 2.8)
    vacia = seg(t, m[4] - 0.2, m[4] + 0.6)
    if llena > 0 and vacia < 1:
        paso, rr = 38, 16.5
        pts = []
        for j in range(-11, 12):
            for i in range(-10, 11):
                px = cx + i * paso + (paso / 2 if j % 2 else 0); py = cy + j * paso * 0.866
                d = math.hypot(px - cx, py - cy)
                if d < r - 16:
                    pts.append((d, px, py))
        pts.sort()
        n = int(len(pts) * llena)
        cuerpo.append(f"<g opacity='{1 - vacia:.2f}'>" + "".join(mini_tierra(px, py, rr) for _, px, py in pts[:n]) + "</g>")
        cuerpo.append(destellos(cx, cy, seg(t, m[3] + 2.4, m[3] + 3.8), 14, 420))
    s.append(f"<g transform='translate({cx},{cy}) scale({z:.3f}) translate({-cx},{-cy})'>{''.join(cuerpo)}</g>")
    # una Tierra de verdad, pequeñita, junto a Nova (frase 2)
    ap = seg(t, m[2] - 0.1, m[2] + 0.6)
    if ap > 0:
        tx = lerp(620, lerp(620, cx, seg(t, m[3] - 0.2, m[3] + 0.8)), 1); ty = lerp(430, cy, seg(t, m[3] - 0.2, m[3] + 0.8))
        if llena < 0.05:
            s.append(f"<circle cx='{tx:.0f}' cy='{ty:.0f}' r='{34 + 4 * math.sin(t * 5):.0f}' fill='#6fd0ff' opacity='0.3'/>"
                     + mini_tierra(tx, ty + 6 * math.sin(t * 3), 16 * ap))
        s.append(destellos(620, 430, seg(t, m[2], m[2] + 1.4), 8, 90))
    # Mercurio pasa por delante (frase 4)
    me = seg(t, m[4] - 0.3, dur)
    if me > 0:
        mx = lerp(1850, 760, me)
        s.append(bola("mer0", mx, 360, 44, "#a8a29e", f"<circle cx='{mx - 10:.0f}' cy='350' r='10' fill='#8a847f'/><circle cx='{mx + 14:.0f}' cy='374' r='7' fill='#8a847f'/>", 0.3, luz_izq=False))
    # Nova se acerca con cuidado y suda
    nx = lerp(-260, 400, seg(t, 0, 3.0)) + 10 * math.sin(t * 1.3)
    ny = 610 + 22 * math.sin(t * 1.8)
    s.append(nova(nx, ny, 0.8, t, ang=3 * math.sin(t * 1.4), fuego=0.7, sudor=seg(t, m[0] + 2.0, m[0] + 3.0),
                  susto=seg(t, m[3] + 0.3, m[3] + 0.6) * (1 - seg(t, m[4], m[4] + 0.4)), mira=1.0))
    # ondas de calor
    for i in range(4):
        k = ((t * 0.7 + i / 4) % 1)
        s.append(f"<path d='M{900 - k * 260:.0f} {420 + i * 90} q20 -14 40 0 t40 0 t40 0' fill='none' stroke='#ffcf8a' stroke-width='5' stroke-linecap='round' opacity='{0.6 * math.sin(k * math.pi):.2f}'/>")
    return "".join(s)


def mercurio(cx, cy, r, giro, t):
    d = []
    for a, rel, cr in CRATERES:
        aa = a + math.radians(giro)
        x, y = cx + r * rel * math.cos(aa), cy + r * rel * math.sin(aa)
        d.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * cr:.0f}' fill='#8f8984' stroke='#6f6a66' stroke-width='5'/>"
                 f"<circle cx='{x - r * cr * 0.25:.0f}' cy='{y - r * cr * 0.25:.0f}' r='{r * cr * 0.55:.0f}' fill='#a59f99'/>")
    return bola("mer", cx, cy, r, "#b5afa8", "".join(d), 0.55)


def esc_mercurio(t, dur, m):
    s = [espacio(t, "#120b2e", "#3a1a4a")]
    s.append(sol(-150, 600, 420, t))
    cx, cy, r = 820, 600, 175
    # fase 1: un año (una vuelta en el mapa de órbita); fase 2: dos vueltas mientras pasa un día
    a1 = seg(t, m[1] + 0.6, m[2] - 0.2)
    a2 = (t - m[2] - 0.4) / max(1.0, (m[3] + 2.6) - (m[2] + 0.4))
    a2 = clamp(a2)
    giro = -360 * a2
    s.append(mercurio(cx, cy, r, giro, t))
    # Nova aterrizada sobre Mercurio, gira con él
    th = math.radians(-150 + giro)
    llega = seg(t, 0, 2.6)
    px, py = cx + (r + 58) * math.cos(th), cy + (r + 58) * math.sin(th)
    nx = lerp(1400, px, llega); ny = lerp(260, py, llega)
    s.append(nova(nx, ny, 0.34, t, ang=lerp(-180, math.degrees(th), llega), fuego=1 - llega, guino=(m[3] + 1.0 < t < m[3] + 1.4)))
    # mapa de la órbita
    ox, oy, rx, ry = 1530, 600, 230, 140
    ap = seg(t, m[1] - 0.2, m[1] + 0.6)
    if ap > 0:
        s.append(f"<g opacity='{ap:.2f}'><ellipse cx='{ox}' cy='{oy}' rx='{rx + 40}' ry='{ry + 60}' fill='#1d1640' opacity='0.6' stroke='#6a5acd' stroke-width='4'/>"
                 f"<ellipse cx='{ox}' cy='{oy}' rx='{rx}' ry='{ry}' fill='none' stroke='#cfc8ff' stroke-width='5' stroke-dasharray='14 12'/>"
                 f"<circle cx='{ox}' cy='{oy}' r='{48 + 3 * math.sin(t * 4):.0f}' fill='#ffcf4a' opacity='0.35'/>"
                 f"<circle cx='{ox}' cy='{oy}' r='36' fill='#ffb627' stroke='{INK}' stroke-width='6'/>")
        ang = 2 * math.pi * (a1 if t < m[2] else 2 * a2) - math.pi / 2
        # rastro de la vuelta
        frac = a1 if t < m[2] else (2 * a2) % 1 if a2 < 1 else 1
        if frac > 0.01:
            n = int(60 * frac)
            pts = " ".join(f"{ox + rx * math.cos(-math.pi / 2 + 2 * math.pi * i / 60):.0f},{oy + ry * math.sin(-math.pi / 2 + 2 * math.pi * i / 60):.0f}" for i in range(n + 1))
            s.append(f"<polyline points='{pts}' fill='none' stroke='#ffe066' stroke-width='9' stroke-linecap='round'/>")
        mx, my = ox + rx * math.cos(ang), oy + ry * math.sin(ang)
        s.append(f"<circle cx='{mx:.0f}' cy='{my:.0f}' r='20' fill='#b5afa8' stroke='{INK}' stroke-width='6'/>")
        # medallas: cada vuelta completada durante el día
        for i in range(2):
            on = seg(t, m[2] + 0.4 + (i + 1) * (m[3] + 2.2 - m[2]) / 2 - 0.2, m[2] + 0.4 + (i + 1) * (m[3] + 2.2 - m[2]) / 2) if t > m[2] else 0
            bx = ox - 60 + i * 120
            s.append(f"<circle cx='{bx}' cy='{oy + ry + 105}' r='{30 + 6 * on * math.sin(t * 8):.0f}' fill='{mix('#3a3366', '#ffd23f', on)}' stroke='{INK}' stroke-width='7'/>"
                     f"<circle cx='{bx}' cy='{oy + ry + 105}' r='9' fill='{mix('#5a5388', '#ff8a1f', on)}'/>")
            s.append(destellos(bx, oy + ry + 105, seg(t, m[2] + 0.4 + (i + 1) * (m[3] + 2.2 - m[2]) / 2, m[2] + 1.6 + (i + 1) * (m[3] + 2.2 - m[2]) / 2), 8, 80))
        s.append("</g>")
    s.append(destellos(cx, cy, seg(t, m[3] + 0.2, m[3] + 1.8), 12, 330))
    return "".join(s)


def jupiter(cx, cy, r, t, sombra=0.35):
    bandas = []
    cols = ["#f3d9b1", "#d9a066", "#f7e6c8", "#c7834a", "#efd2a4", "#b8733f", "#f3dcb8", "#d39a5f"]
    for i, c in enumerate(cols):
        y0 = cy - r + i * 2 * r / len(cols)
        ond = 10 * math.sin(t * 0.8 + i)
        bandas.append(f"<path d='M{cx - r} {y0:.0f} Q{cx - r / 2} {y0 + ond:.0f} {cx} {y0:.0f} T{cx + r} {y0:.0f} L{cx + r} {y0 + 2 * r / len(cols) + 2:.0f} L{cx - r} {y0 + 2 * r / len(cols) + 2:.0f} Z' fill='{c}'/>")
    gx = cx + r * 0.25 + 10 * math.sin(t * 0.3)
    bandas.append(f"<ellipse cx='{gx:.0f}' cy='{cy + r * 0.32:.0f}' rx='{r * 0.2:.0f}' ry='{r * 0.12:.0f}' fill='#c8553d' stroke='#9c3b2a' stroke-width='6'/>"
                  f"<ellipse cx='{gx:.0f}' cy='{cy + r * 0.32:.0f}' rx='{r * 0.1:.0f}' ry='{r * 0.05:.0f}' fill='#e07a5f'/>")
    return bola("jup", cx, cy, r, "#e9c896", "".join(bandas), sombra)


def esc_io(t, dur, m):
    s = [espacio(t, "#0f0b2a", "#2b1240")]
    s.append(jupiter(420, 610, 330, t))
    # líneas de gravedad entre Júpiter e Ío (frase 3)
    gr = seg(t, m[3] - 0.2, m[3] + 0.6) * (1 - seg(t, m[4] - 0.3, m[4] + 0.3))
    cx, cy, r = 1240, 610, 215
    if gr > 0:
        for i in range(-2, 3):
            off = (t * 120) % 60
            s.append(f"<line x1='760' y1='{cy + i * 50}' x2='{cx - r - 10}' y2='{cy + i * 35}' stroke='#ffd166' stroke-width='7' "
                     f"stroke-dasharray='30 30' stroke-dashoffset='{-off:.0f}' opacity='{0.8 * gr:.2f}'/>")
    estira = gr * 0.07 * math.sin(t * 5)
    sx_, sy_ = 1 + estira, 1 - estira
    # Ío
    d = ["<defs><radialGradient id='calor'><stop offset='0' stop-color='#ff3d00' stop-opacity='0.85'/>"
         "<stop offset='1' stop-color='#ff9100' stop-opacity='0'/></radialGradient></defs>"]
    for i, (a, rel) in enumerate(VOLC):
        x, y = cx + r * rel * math.cos(a), cy + r * rel * math.sin(a)
        d.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{r * 0.09:.0f}' ry='{r * 0.065:.0f}' fill='{['#c0392b', '#3b2a1a', '#e67e22', '#f5f0d0'][i % 4]}' opacity='0.85'/>")
    on = [seg(t, m[2] + 0.2 + i * 0.25, m[2] + 0.5 + i * 0.25) for i in range(len(VOLC))]
    for i, (a, rel) in enumerate(VOLC):
        if on[i] > 0:
            x, y = cx + r * rel * math.cos(a), cy + r * rel * math.sin(a)
            fl = 0.7 + 0.3 * math.sin(t * 9 + i)
            d.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * 0.12 * on[i] * fl:.0f}' fill='#ff6d00' opacity='0.55'/>"
                     f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r * 0.05 * on[i]:.0f}' fill='#ffe082'/>")
    if gr > 0:
        d.append(f"<circle cx='{cx}' cy='{cy}' r='{r * 0.9:.0f}' fill='url(#calor)' opacity='{gr * (0.6 + 0.3 * math.sin(t * 5)):.2f}'/>")
    io = bola("io", cx, cy, r, "#f2d64b", "".join(d), 0.45)
    # penachos volcánicos en el borde (frase 1 grande, luego varios)
    pen = []
    for j, (ang, t0, h0) in enumerate(((-62, m[1] + 0.4, 1.0), (-128, m[2] + 0.8, 0.6), (-20, m[2] + 1.6, 0.55), (205, m[2] + 2.3, 0.5))):
        k = seg(t, t0, t0 + 1.4)
        if k <= 0:
            continue
        a = math.radians(ang)
        bx, by = cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a)
        h = r * 1.05 * h0 * k * (0.95 + 0.05 * math.sin(t * 6 + j))
        w = h * 0.75
        p = [f"<g transform='translate({bx:.0f},{by:.0f}) rotate({ang + 90:.1f})'>",
             f"<path d='M{-w * 0.25:.0f} 0 Q{-w * 1.15:.0f} {-h * 1.15:.0f} 0 {-h:.0f} Q{w * 1.15:.0f} {-h * 1.15:.0f} {w * 0.25:.0f} 0 Z' "
             f"fill='#fff3b0' fill-opacity='0.28' stroke='#ffe9a8' stroke-width='5' stroke-opacity='0.8'/>"]
        for q in range(7):   # fuente de lava en abanico
            xq = (q - 3) / 3 * w
            p.append(f"<path d='M0 0 Q{xq * 0.5:.0f} {-h * 1.5:.0f} {xq:.0f} {-h * 0.25:.0f}' fill='none' stroke='#ff8f00' stroke-width='{6 * h0 + 2:.0f}' stroke-linecap='round' opacity='0.75'/>")
        p.append(f"<path d='M0 0 L0 {-h * 0.7:.0f}' stroke='{INK}' stroke-width='{26 * h0 + 6:.0f}' stroke-linecap='round'/>"
                 f"<path d='M0 0 L0 {-h * 0.7:.0f}' stroke='#ff6d00' stroke-width='{20 * h0 + 2:.0f}' stroke-linecap='round'/>"
                 f"<path d='M0 0 L0 {-h * 0.55:.0f}' stroke='#ffe082' stroke-width='{8 * h0 + 2:.0f}' stroke-linecap='round'/>")
        for q in range(8):   # gotas de lava que suben y caen
            kk = ((t * 0.7 + q / 8 + j * 0.3) % 1)
            xq = ((q * 5) % 7 - 3) / 3 * w
            px_ = 2 * (1 - kk) * kk * xq * 0.5 + kk * kk * xq
            py_ = 2 * (1 - kk) * kk * (-h * 1.5) + kk * kk * (-h * 0.25)
            p.append(f"<circle cx='{px_:.0f}' cy='{py_:.0f}' r='{6 * h0 + 4:.0f}' fill='#ffb300' stroke='{INK}' stroke-width='3'/>")
        p.append("</g>")
        pen.append("".join(p))
    s.append(f"<g transform='translate({cx},{cy}) scale({sx_:.3f},{sy_:.3f}) translate({-cx},{-cy})'>{''.join(pen)}{io}</g>")
    s.append(destellos(cx + r * 0.5, cy - r * 0.95, seg(t, m[1] + 0.4, m[1] + 1.8), 12, 260, "#ffcc80"))
    # Europa asoma (frase 4)
    eu = seg(t, m[4] - 0.2, dur)
    if eu > 0:
        ex = lerp(2050, 1720, eu)
        s.append(bola("eu0", ex, 840, 62, "#efe6d6", f"<path d='M{ex - 50:.0f} 820 Q{ex:.0f} 850 {ex + 50:.0f} 830 M{ex - 40:.0f} 860 Q{ex:.0f} 840 {ex + 45:.0f} 870' stroke='#a0522d' stroke-width='5' fill='none'/>", 0.35))
    # Nova observa y se asusta con el ¡bum!
    bum = seg(t, m[1] + 0.3, m[1] + 0.6) * (1 - seg(t, m[1] + 2.2, m[1] + 2.8))
    nx = lerp(2150, 1690, seg(t, 0, 2.8)) + 10 * math.sin(t * 1.2) + 40 * bum
    ny = 370 + 18 * math.sin(t * 1.7) - 30 * bum
    s.append(nova(nx, ny, 0.55, t, ang=180 + 4 * math.sin(t * 1.5) - 10 * bum, fuego=0.6 + 0.6 * bum, susto=bum, mira=0.0))
    return "".join(s)


def gota(x, y, s, t, op=1.0):
    return (f"<g transform='translate({x:.0f},{y + 6 * math.sin(t * 2.5 + x):.0f}) scale({s:.2f})' opacity='{op:.2f}'>"
            f"<path d='M0 -70 Q48 -6 44 22 Q40 62 0 62 Q-40 62 -44 22 Q-48 -6 0 -70 Z' fill='#3fa9f5' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>"
            f"<path d='M-20 0 Q-26 24 -10 40' fill='none' stroke='#cdeeff' stroke-width='9' stroke-linecap='round'/></g>")


def europa(cx, cy, r, t, corte, hielo=0.0, sombra=0.4):
    d = []
    for gx, gy, a, l in GRIETAS:
        x0, y0 = cx + gx * r * 0.8, cy + gy * r * 0.8
        dx, dy = math.cos(a) * r * l, math.sin(a) * r * l
        d.append(f"<path d='M{x0 - dx:.0f} {y0 - dy:.0f} Q{x0 + dy * 0.3:.0f} {y0 - dx * 0.3:.0f} {x0 + dx:.0f} {y0 + dy:.0f}' fill='none' stroke='#a0522d' stroke-width='{max(4, r * 0.03):.0f}' stroke-linecap='round' opacity='0.85'/>"
                 f"<path d='M{x0 - dx:.0f} {y0 - dy:.0f} Q{x0 + dy * 0.3:.0f} {y0 - dx * 0.3:.0f} {x0 + dx:.0f} {y0 + dy:.0f}' fill='none' stroke='#d9a27a' stroke-width='{r * 0.012:.0f}' stroke-linecap='round'/>")
    s = [bola("eur", cx, cy, r, "#f2ece0", "".join(d), sombra)]
    if corte > 0:
        a0, a1 = math.radians(-80), math.radians(-80 + 95 * corte)
        R = r + 4
        cuña = (f"M{cx} {cy} L{cx + R * math.cos(a0):.1f} {cy + R * math.sin(a0):.1f} "
                f"A{R} {R} 0 0 1 {cx + R * math.cos(a1):.1f} {cy + R * math.sin(a1):.1f} Z")
        olas = "".join(f"<circle cx='{cx}' cy='{cy}' r='{r * (0.6 + 0.07 * i) + 4 * math.sin(t * 3 + i):.0f}' fill='none' stroke='#7fd3ff' stroke-width='4' opacity='0.6'/>" for i in range(4))
        brillos = "".join(estrellita(cx + r * 0.75 * math.cos(-1.2 + 0.25 * i), cy + r * 0.75 * math.sin(-1.2 + 0.25 * i), 6, 0.5 + 0.5 * math.sin(t * 4 + i), "#bff3ff") for i in range(4))
        hl = hielo * (0.5 + 0.5 * math.sin(t * 7))
        s.append(f"<defs><clipPath id='cuna'><path d='{cuña}'/></clipPath></defs>"
                 f"<g clip-path='url(#cuna)'>"
                 f"<circle cx='{cx}' cy='{cy}' r='{r + 4}' fill='{mix('#ffffff', '#fff59d', hl)}'/>"
                 f"<circle cx='{cx}' cy='{cy}' r='{r * 0.88:.0f}' fill='#1e6fd9' stroke='{INK}' stroke-width='6'/>{olas}{brillos}"
                 f"<circle cx='{cx}' cy='{cy}' r='{r * 0.55:.0f}' fill='#8d6e63' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{cx}' cy='{cy}' r='{r * 0.25:.0f}' fill='#c97b4a' stroke='{INK}' stroke-width='5'/></g>"
                 f"<path d='{cuña}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
        if hielo > 0:
            s.append(f"<g clip-path='url(#cuna)'><circle cx='{cx}' cy='{cy}' r='{r * 0.94:.0f}' fill='none' stroke='#ffd23f' stroke-width='{8 * hielo:.0f}' opacity='{hl:.2f}'/></g>")
    return "".join(s)


def esc_europa(t, dur, m):
    s = [espacio(t, "#0a1030", "#1d1a4f")]
    s.append(jupiter(1560, 240, 80, t, 0.5))
    corte = seg(t, m[1] + 0.8, m[1] + 2.6)
    hielo = seg(t, m[2], m[2] + 0.5) * (1 - seg(t, m[3] - 0.3, m[3]))
    mueve = seg(t, m[3] - 0.2, m[3] + 1.0)
    cx = lerp(930, 720, mueve); cy = 610; r = lerp(270, 250, mueve)
    gira = 6 * math.sin(t * 0.4)
    s.append(f"<g transform='rotate({gira:.1f},{cx:.0f},{cy})'>{europa(cx, cy, r, t, corte, hielo)}</g>")
    # comparación: el agua de la Tierra (1 gota) y la de Europa (2 gotas)
    ap = seg(t, m[3] + 0.2, m[3] + 1.0)
    if ap > 0:
        s.append(f"<g opacity='{ap:.2f}'>")
        s.append(f"<rect x='1230' y='330' width='600' height='520' rx='40' fill='#1d1640' opacity='0.7' stroke='#6a5acd' stroke-width='5'/>")
        s.append(tierra("tie2", 1340, 470, 62, t, 0.3, 0.3))
        s.append(gota(1520, 470, 0.8 * seg(t, m[3] + 0.6, m[3] + 1.2), t))
        s.append(europa(1340, 715, 62, t, 0, 0, 0.3))
        s.append(gota(1520, 715, 0.8 * seg(t, m[3] + 1.2, m[3] + 1.8), t))
        s.append(gota(1680, 715, 0.8 * seg(t, m[3] + 1.6, m[3] + 2.2), t))
        s.append(f"<line x1='1260' y1='592' x2='1800' y2='592' stroke='#6a5acd' stroke-width='4'/>")
        s.append("</g>")
        s.append(destellos(1600, 715, seg(t, m[3] + 2.0, m[3] + 3.4), 12, 200))
    # Nova con su luz
    llega = seg(t, 0, 2.6)
    nx = lerp(lerp(-260, 1480, llega), 300, mueve) + 12 * math.sin(t * 1.3)
    ny = lerp(lerp(300, 400, llega), 470, mueve) + 16 * math.sin(t * 1.9)
    ang = lerp(180, 0, mueve) if llega >= 1 else 0
    if llega < 1:
        ang = lerp(10, 180, seg(t, 1.6, 2.6))
    s.append(nova(nx, ny, 0.5, t, ang=ang + 4 * math.sin(t * 1.5), fuego=0.6, guino=(m[4] + 0.8 < t < m[4] + 1.2),
                  susto=seg(t, m[1] + 1.2, m[1] + 1.5) * (1 - seg(t, m[2], m[2] + 0.3))))
    s.append(destellos(cx + r * 0.4, cy - r * 0.5, seg(t, m[1] + 2.2, m[1] + 3.6), 10, 220, "#bff3ff"))
    return "".join(s)


def neptuno(cx, cy, r, t, viento):
    d = [f"<ellipse cx='{cx}' cy='{cy - r * 0.55:.0f}' rx='{r * 1.1:.0f}' ry='{r * 0.12:.0f}' fill='#3d7be0' opacity='0.6'/>",
         f"<ellipse cx='{cx}' cy='{cy + r * 0.35:.0f}' rx='{r * 1.1:.0f}' ry='{r * 0.16:.0f}' fill='#2a5fc4' opacity='0.6'/>",
         f"<ellipse cx='{cx}' cy='{cy + r * 0.75:.0f}' rx='{r * 1.1:.0f}' ry='{r * 0.1:.0f}' fill='#3d7be0' opacity='0.5'/>"]
    vel = 0.12 + 0.9 * viento
    # gran mancha oscura y su nube blanca, arrastradas por el viento
    off = (t * 60 * vel) % (2.6 * r)
    mx = cx - 1.3 * r + off
    d.append(f"<ellipse cx='{mx:.0f}' cy='{cy - r * 0.15:.0f}' rx='{r * 0.2:.0f}' ry='{r * 0.11:.0f}' fill='#16306e' stroke='#0f2353' stroke-width='5'/>"
             f"<path d='M{mx - r * 0.18:.0f} {cy - r * 0.02:.0f} q{r * 0.2:.0f} {r * 0.06:.0f} {r * 0.4:.0f} 0' fill='none' stroke='#f2f8ff' stroke-width='{r * 0.035:.0f}' stroke-linecap='round'/>")
    for i in range(9):   # nubes de metano helado (vetas blancas)
        yy = cy + (i - 4) * r * 0.21
        o2 = (t * (120 + 30 * i) * vel + i * 170) % (2.8 * r)
        xx = cx - 1.4 * r + o2
        lg = r * (0.25 + 0.1 * (i % 3)) * (1 + viento)
        d.append(f"<path d='M{xx - lg:.0f} {yy:.0f} Q{xx:.0f} {yy - 10:.0f} {xx + lg * 0.3:.0f} {yy:.0f}' fill='none' stroke='#eaf4ff' stroke-width='{r * 0.03:.0f}' stroke-linecap='round' opacity='0.85'/>")
    return bola("nep", cx, cy, r, "#4f8ff7", "".join(d), 0.5)


def esc_neptuno(t, dur, m):
    s = [espacio(t, "#040818", "#0d1a3e", neb=False)]
    viento = seg(t, m[2] - 0.2, m[2] + 1.5)
    # el Sol, una estrellita lejana (frase 1)
    sl = seg(t, m[1] - 0.2, m[1] + 0.6)
    s.append(estrellita(700, 380, 9 + 6 * sl + 1.5 * math.sin(t * 4), 0.75 + 0.25 * sl, "#ffe066"))
    s.append(destellos(700, 380, seg(t, m[1], m[1] + 1.4), 8, 90))
    cx, cy, r = 1290, 620, 330
    s.append(f"<circle cx='{cx}' cy='{cy}' r='{r + 30 + 6 * math.sin(t * 2):.0f}' fill='#6fb6ff' opacity='0.18'/>")
    s.append(neptuno(cx, cy, r, t, viento))
    # vendaval: rayas de viento por toda la pantalla
    if viento > 0:
        for i in range(16):
            y = 280 + (i * 47) % 640
            v = 1 + (i % 4) * 0.35
            x = ((t * 1500 * v + i * 270) % (W + 900)) - 450
            lg = 220 + 90 * (i % 3)
            s.append(f"<path d='M{x - lg:.0f} {y} Q{x - lg / 2:.0f} {y - 16} {x:.0f} {y}' fill='none' stroke='#dff3ff' stroke-width='{6 + (i % 3) * 2}' "
                     f"stroke-linecap='round' opacity='{0.65 * viento:.2f}'/>")
        for i in range(10):   # cristalitos de hielo que vuelan
            x = ((t * 1100 + i * 230) % (W + 200)) - 100; y = 300 + (i * 83) % 600 + 20 * math.sin(t * 5 + i)
            s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='6' fill='#ffffff' opacity='{0.8 * viento:.2f}'/>")
    s.append(destellos(cx, cy - r * 0.2, seg(t, m[3] + 0.2, m[3] + 1.8), 14, 420, "#dff3ff"))
    # Nova: llega, el viento la empuja, enciende todos los motores
    llega = seg(t, 0, 2.8)
    motor = seg(t, m[4], m[4] + 0.8)
    empuje = viento * (1 - motor)
    nx = lerp(-260, 520, llega) - 120 * empuje + 18 * empuje * math.sin(t * 17)
    ny = 600 + 22 * math.sin(t * 1.8) + 14 * empuje * math.sin(t * 13)
    ang = -14 * empuje * math.sin(t * 9) + 3 * math.sin(t * 1.5)
    s.append(nova(nx, ny, 0.72, t, ang=ang, fuego=0.6 + 0.6 * viento + 0.9 * motor, susto=clamp(empuje * 2),
                  guino=(dur - 1.4 < t < dur - 1.0)))
    if motor > 0:
        s.append(destellos(nx - 200, ny, seg(t, m[4] + 0.1, m[4] + 1.3), 10, 160, "#ffcc80"))
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
    s = [espacio(t, "#0b0a2e", "#2a1559")]
    # la Tierra grande abajo (vuelta a casa)
    sube = seg(t, 0, 3.0)
    ty = lerp(1500, 1430, sube)
    s.append(f"<circle cx='960' cy='{ty:.0f}' r='{800 + 10 * math.sin(t * 2):.0f}' fill='#6fd0ff' opacity='0.2'/>")
    s.append(tierra("tie3", 960, ty, 760, t, 0.03, 0.15))
    # Nova vuelve
    llega = seg(t, 0, 2.4)
    nx = lerp(-300, 470, llega) + lerp(0, -40, seg(t, m[1] - 0.5, m[1] + 1.0)); ny = 520 + 20 * math.sin(t * 2)
    s.append(destellos(nx, ny, seg(t, 1.8, 3.2), 12, 240))
    s.append(nova(nx, ny, 0.9, t, ang=4 * math.sin(t * 1.6), fuego=0.7, guino=(m[3] + 0.4 < t < m[3] + 0.8), mira=0.5))
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
    {"titulo": "¿Un día más largo que un año?", "escena": esc_intro, "susc": 3,
     "frases": ["¿Sabías que hay un lugar donde un día dura más que un año?",
                "Hoy vamos a visitarlo… y la última parada te dejará con la boca abierta.",
                "Sube a Nova, nuestro pequeño cohete explorador.",
                "Suscríbete, y… ¡despegamos!"]},
    {"titulo": "1. El gigante de fuego", "escena": esc_sol, "tarjeta": "CAPÍTULO 1 · EL SOL",
     "frases": ["Primera parada: el Sol. Nova se acerca con cuidado, porque aquí hace muchísimo calor.",
                "Desde la Tierra parece pequeño, pero de cerca es una bola de gas ardiente gigantesca.",
                "¿Cuántas Tierras crees que cabrían dentro?",
                "¡Un millón trescientas mil! Como un saco gigante lleno de canicas.",
                "Pero muy cerquita del Sol nos espera un planeta con un horario de locos."],
     "grandes": {3: "1,3 MILLONES"}},
    {"titulo": "2. El día más largo", "escena": esc_mercurio, "tarjeta": "CAPÍTULO 2 · MERCURIO",
     "frases": ["Llegamos a Mercurio, el planeta más cercano al Sol, lleno de cráteres como nuestra Luna.",
                "Corre tanto que da una vuelta al Sol en solo ochenta y ocho días: ese es su año.",
                "Pero gira sobre sí mismo tan despacio que, de un amanecer al siguiente, pasan ciento setenta y seis días.",
                "¡Un solo día en Mercurio dura lo mismo que dos de sus años!"],
     "grandes": {1: "AÑO: 88 DÍAS", 2: "DÍA: 176 DÍAS", 3: "1 DÍA = 2 AÑOS"}, "extra": 1.2},
    {"titulo": "3. La luna de los volcanes", "escena": esc_io, "tarjeta": "CAPÍTULO 3 · ÍO, LA LUNA DE FUEGO",
     "frases": ["Ahora volamos muy lejos, hasta Júpiter, el gigante de rayas. A su alrededor gira una luna amarilla: Ío.",
                "De repente… ¡bum! Del suelo sale disparado un chorro de lava y gas.",
                "Ío es el lugar con más volcanes activos de todo el sistema solar: ¡tiene cientos!",
                "Júpiter la estira y la aprieta con su gravedad, y eso calienta su interior, como una pelota que amasas sin parar.",
                "Pero en la luna de al lado nos espera todo lo contrario: hielo… y un gran secreto."],
     "grandes": {2: "¡CIENTOS!"}},
    {"titulo": "4. El océano escondido", "escena": esc_europa, "tarjeta": "CAPÍTULO 4 · EUROPA",
     "frases": ["Esta es Europa, otra luna de Júpiter: blanca, helada y llena de grietas.",
                "Parece un mundo quieto… pero bajo su costra de hielo se esconde un océano gigante.",
                "Esa capa de hielo podría tener entre quince y veinticinco kilómetros de grosor.",
                "Y el océano de debajo podría tener el doble de agua que todos los mares de la Tierra juntos.",
                "¡Por eso es uno de los lugares más prometedores para buscar vida fuera de la Tierra!"],
     "grandes": {2: "15-25 km", 3: "¡EL DOBLE!"}, "extra": 0.8},
    {"titulo": "5. Los vientos más rápidos", "escena": esc_neptuno, "tarjeta": "CAPÍTULO 5 · NEPTUNO",
     "frases": ["Última parada, la más lejana: Neptuno, el planeta más alejado del Sol, azul y helado.",
                "Desde aquí, el Sol se ve como una estrella pequeñita.",
                "Pero agárrate fuerte, porque aquí soplan los vientos más rápidos de todo el sistema solar.",
                "¡A más de dos mil kilómetros por hora! Unas cinco veces más que los vientos más fuertes de la Tierra.",
                "Nova tiene que encender todos sus motores para no salir volando."],
     "grandes": {3: "2.000 km/h"}},
    {"titulo": "Suscríbete para más viajes", "escena": esc_final,
     "frases": ["Y así termina nuestro viaje por el sistema solar. ¡Nova ya vuelve a casa!",
                "Si te ha gustado, ayúdanos con un pequeño gesto: suscríbete al canal y activa la campanita.",
                "Así no te perderás ningún viaje: cada día, una historia nueva llena de curiosidades.",
                "¡Nos vemos en el próximo viaje!"],
     "extra": 1.5},
]
