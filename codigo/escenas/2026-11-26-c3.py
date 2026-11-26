"""2026-11-26-c3 · Cuerpo humano: el pulmón izquierdo es más pequeño que el derecho (2 lóbulos frente a 3)
porque le deja sitio al corazón (escotadura cardíaca).

Dentro del pecho (costillas, columna y diafragma), dos pulmones con cara respiran a la vez; una silueta
fantasma del pulmón derecho reflejada muestra que el izquierdo es menor; se marcan sus lóbulos (3 y 2) y,
en la REVELACION, el corazón se ilumina, late fuerte y la cámara se acerca a la muesca donde encaja.
Todo en la mitad de abajo; arriba, fondo azul tranquilo con burbujas de aire.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.2    # el corazón se ilumina en su hueco
MUSICA = 2

rng = np.random.default_rng(1126)
BOKEH = [(rng.uniform(0, W), rng.uniform(60, 1000), rng.uniform(6, 22), rng.uniform(0, 6.28), rng.uniform(10, 28)) for _ in range(26)]
AIR = [(rng.uniform(-22, 22), rng.uniform(0, 1), rng.uniform(5, 10)) for _ in range(14)]
INSIDE = [(rng.uniform(170, 900), rng.uniform(1200, 1690), rng.uniform(3, 6), rng.uniform(0, 6.28)) for _ in range(34)]
BURST = [(rng.uniform(0, 6.28), rng.uniform(220, 430), rng.uniform(10, 18)) for _ in range(28)]

# pulmón derecho (a la izquierda de la pantalla: el personaje nos mira de frente)
DER = ("M400 1140 C300 1140 180 1300 150 1500 C135 1620 150 1700 190 1720 "
       "C260 1680 400 1675 470 1705 C482 1550 472 1350 455 1220 C450 1170 430 1140 400 1140 Z")
# pulmón izquierdo (a la derecha): más estrecho y con la muesca del corazón en el lado interior
IZQ = ("M680 1175 C650 1175 630 1200 625 1245 C620 1330 625 1395 640 1432 "
       "C705 1455 742 1525 730 1592 C724 1640 694 1662 672 1690 "
       "C735 1702 810 1688 858 1710 C898 1686 902 1600 890 1480 C868 1310 770 1175 680 1175 Z")
NOTCH = "M640 1432 C705 1455 742 1525 730 1592 C724 1640 694 1662 672 1690"
CORAZON = "M0 -40 C-20 -92 -112 -82 -106 -8 C-100 52 -32 92 8 124 C50 84 112 42 106 -20 C100 -88 18 -92 0 -40 Z"


def respira(t):
    return 0.5 - 0.5 * math.cos(2 * math.pi * t / 2.4)


def latido(t, fuerza):
    p = (t % 0.8) / 0.8
    return 1 + fuerza * (math.exp(-((p - 0.08) / 0.05) ** 2) + 0.6 * math.exp(-((p - 0.28) / 0.05) ** 2))


def costillas():
    g = ["<g opacity='0.55'>"]
    # columna
    for y in range(1060, 1920, 70):
        g.append(f"<rect x='510' y='{y}' width='60' height='54' rx='14' fill='#f3e6c8' stroke='{INK}' stroke-width='6'/>")
    for i, y in enumerate(range(1120, 1700, 95)):
        sp = 400 + i * 22
        for sgn in (-1, 1):
            x2 = 540 + sgn * sp
            d = f"M{540 + sgn * 30} {y} C{540 + sgn * 200} {y - 50} {x2} {y - 10} {x2 + sgn * 10} {y + 120}"
            g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>")
            g.append(f"<path d='{d}' fill='none' stroke='#f3e6c8' stroke-width='20' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def diafragma(br):
    dy = 24 * br
    return (f"<path d='M-30 {1790 + dy:.0f} Q270 {1640 + dy:.0f} 540 {1735 + dy:.0f} Q810 {1640 + dy:.0f} 1110 {1790 + dy:.0f} "
            f"L1110 1940 L-30 1940 Z' fill='#d9485a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            + "".join(f"<path d='M{x} {1800 + dy:.0f} Q{x + 40} {1850 + dy:.0f} {x + 20} {1920}' fill='none' stroke='#b8344a' stroke-width='7' stroke-linecap='round'/>"
                      for x in range(40, 1080, 120)))


def traquea(t, br):
    g = []
    # bronquios
    for d in ("M540 1262 Q500 1290 446 1336", "M540 1262 Q585 1290 640 1328"):
        g.append(f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='48' stroke-linecap='round'/>")
        g.append(f"<path d='{d}' fill='none' stroke='#f6d8cf' stroke-width='32' stroke-linecap='round'/>")
    g.append(f"<rect x='506' y='985' width='68' height='285' rx='12' fill='#f6d8cf' stroke='{INK}' stroke-width='{LW}'/>")
    for y in range(1010, 1260, 34):
        g.append(f"<path d='M512 {y} Q540 {y + 10} 568 {y}' fill='none' stroke='#d9a79c' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='540' cy='985' rx='34' ry='11' fill='#b5524f' stroke='{INK}' stroke-width='6'/>")
    # burbujas de aire que entran al inspirar y salen al espirar
    sube = math.sin(2 * math.pi * t / 2.4)   # >0: entra aire
    for dx, ph, r in AIR:
        u = (t * 0.7 + ph) % 1
        y = lerp(840, 1240, u) if sube >= 0 else lerp(1240, 840, u)
        a = 0.85 * min(1, abs(sube) * 2) * math.sin(math.pi * u)
        if a > 0.03:
            g.append(f"<circle cx='{540 + dx * (0.6 if y > 990 else 1):.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#e9fbff' stroke='{INK}' stroke-width='3' opacity='{a:.2f}'/>")
    return "".join(g)


def cara(cx, cy, t, look_x, look_y, modo, fase):
    """modo: 'feliz', 'timido', 'orgulloso', 'sorpresa', 'amor'."""
    g = []
    blink = 0.12 if ((t + fase) % 2.9) < 0.12 else 1.0
    if modo == "amor":
        for ex in (-42, 42):
            g.append(f"<path d='M{cx + ex - 22} {cy + 4} Q{cx + ex} {cy - 22} {cx + ex + 22} {cy + 4}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    else:
        for ex in (-42, 42):
            g.append(f"<ellipse cx='{cx + ex}' cy='{cy}' rx='25' ry='{29 * blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
            if blink > 0.5:
                g.append(f"<circle cx='{cx + ex + look_x:.1f}' cy='{cy + look_y:.1f}' r='13' fill='{INK}'/>")
                g.append(f"<circle cx='{cx + ex + look_x - 4:.1f}' cy='{cy + look_y - 5:.1f}' r='4.5' fill='#fff'/>")
    if modo == "timido":
        g.append(f"<path d='M{cx - 16} {cy + 52} Q{cx} {cy + 44} {cx + 16} {cy + 52}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
        g.append(f"<path d='M{cx - 66} {cy - 44} L{cx - 26} {cy - 36} M{cx + 26} {cy - 36} L{cx + 66} {cy - 44}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    elif modo == "sorpresa":
        g.append(f"<ellipse cx='{cx}' cy='{cy + 56}' rx='15' ry='19' fill='#7a1f33' stroke='{INK}' stroke-width='6'/>")
    else:
        w = 34 if modo == "amor" else 28
        g.append(f"<path d='M{cx - w} {cy + 42} Q{cx} {cy + 82} {cx + w} {cy + 42} Z' fill='#7a1f33' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<path d='M{cx - w * 0.5:.0f} {cy + 62} Q{cx} {cy + 76} {cx + w * 0.5:.0f} {cy + 62}' fill='none' stroke='#ff7a8a' stroke-width='7' stroke-linecap='round'/>")
    for ex in (-78, 78):
        g.append(f"<ellipse cx='{cx + ex}' cy='{cy + 36}' rx='17' ry='11' fill='#ff5c7a' opacity='0.6'/>")
    return "".join(g)


def pulmon(path, clip, ax, ay, sx, sy, lobulos, t, extra=""):
    g = [f"<g transform='translate({ax},{ay}) scale({sx:.4f},{sy:.4f}) translate({-ax},{-ay})'>"]
    g.append(f"<path d='{path}' fill='#ff8fa3' stroke='{INK}' stroke-width='{LW + 4}' stroke-linejoin='round'/>")
    g.append(f"<g clip-path='url(#{clip})'>")
    for poly, col, a in lobulos:
        if a > 0.01:
            g.append(f"<polygon points='{poly}' fill='{col}' opacity='{a:.2f}'/>")
    # brillo y textura (alvéolos)
    g.append(f"<path d='{path}' fill='none' stroke='#ffc4ce' stroke-width='26' opacity='0.55' transform='translate(18,16)'/>")
    for px, py, pr, ph in INSIDE:
        g.append(f"<circle cx='{px}' cy='{py}' r='{pr * (1 + 0.3 * math.sin(t * 2 + ph)):.1f}' fill='#ffd3da' opacity='0.5'/>")
    g.append(extra)
    g.append("</g>")
    g.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def corazon(t, rev):
    sc = (0.92 + 0.14 * rev) * latido(t, lerp(0.05, 0.12, rev))
    if t >= REVELACION:
        sc *= 1 + 0.18 * math.sin(math.pi * clamp((t - REVELACION) / 0.45))
    col = mix("#b8323a", "#ff3348", rev)
    hi = mix("#d9616a", "#ff8a96", rev)
    cx, cy = 604, 1572
    g = []
    if rev > 0.02:
        g.append(f"<circle cx='{cx}' cy='{cy}' r='{lerp(120, 300, rev) * (0.95 + 0.05 * math.sin(t * 8)):.0f}' fill='url(#glow)'/>")
    g.append(f"<g transform='translate({cx},{cy}) rotate(-28) scale({sc:.4f})'>")
    # vasos grandes (aorta roja y tronco pulmonar azul)
    g.append(f"<path d='M-14 -54 C-18 -130 60 -150 78 -98' fill='none' stroke='{INK}' stroke-width='44' stroke-linecap='round'/>")
    g.append(f"<path d='M-14 -54 C-18 -130 60 -150 78 -98' fill='none' stroke='{mix('#c43a45', '#ff4a5c', rev)}' stroke-width='28' stroke-linecap='round'/>")
    g.append(f"<path d='M30 -50 C34 -100 -40 -120 -62 -92' fill='none' stroke='{INK}' stroke-width='38' stroke-linecap='round'/>")
    g.append(f"<path d='M30 -50 C34 -100 -40 -120 -62 -92' fill='none' stroke='#4f7fd9' stroke-width='23' stroke-linecap='round'/>")
    g.append(f"<path d='{CORAZON}' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-78 -30 C-80 -60 -50 -70 -36 -58' fill='none' stroke='{hi}' stroke-width='14' stroke-linecap='round'/>")
    g.append(f"<path d='M10 -30 C0 20 -10 60 4 100' fill='none' stroke='{mix('#8e2230', '#c4243a', rev)}' stroke-width='7' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.35)
    flash = clamp(1 - (t - REVELACION) / 0.8) if t >= REVELACION else 0
    br = respira(t) * (1 - 0.6 * seg(t, REVELACION, REVELACION + 0.5))
    warm = 0.5 * rev
    top = mix("#173f63", "#3a2a66", warm)
    low = mix("#2f7fa6", "#a8507a", warm)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='bg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         "<radialGradient id='glow'><stop offset='0' stop-color='#fff3b0' stop-opacity='0.9'/>"
         "<stop offset='0.4' stop-color='#ff8aa0' stop-opacity='0.55'/><stop offset='1' stop-color='#ff4d6d' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.9 * flash:.3f}'/>"
         f"<stop offset='0.45' stop-color='#ffd1dc' stop-opacity='{0.5 * flash:.3f}'/><stop offset='1' stop-color='#ff8aa0' stop-opacity='0'/></radialGradient>",
         f"<clipPath id='cder'><path d='{DER}'/></clipPath><clipPath id='cizq'><path d='{IZQ}'/></clipPath>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#bg)'/>"]
    # burbujas suaves de fondo (arriba, tranquilo)
    for bx, by, brr, ph, sp in BOKEH:
        yy = (by - t * sp) % 1000 + 30
        s.append(f"<circle cx='{bx + 12 * math.sin(t * 0.8 + ph):.0f}' cy='{yy:.0f}' r='{brr:.1f}' fill='#ffffff' opacity='{0.10 + 0.06 * math.sin(t * 1.5 + ph):.2f}'/>")

    z = 1 + 0.22 * seg(t, REVELACION, 8.0)
    cx, cy = 640, 1520
    ent = seg(t, 0, 1.0)
    s.append(f"<g transform='translate({cx},{cy}) scale({z:.4f}) translate({-cx},{-cy})'>")
    s.append(f"<g transform='translate(0,{lerp(90, 0, ent) + 6 * math.sin(t * 1.3):.1f})'>")
    s.append(costillas())
    s.append(diafragma(br))
    s.append(traquea(t, br))

    # lóbulos: derecho 3, izquierdo 2 (se van encendiendo)
    def luz(a0):
        k = seg(t, a0, a0 + 0.25)
        pico = math.exp(-((t - a0 - 0.25) / 0.22) ** 2) if t > a0 else 0
        return k, pico
    lob_der, lob_izq = [], []
    cols = ["#ff6f8c", "#ffa3b5", "#ff7d98"]
    polys_der = ["0,1000 540,1000 540,1386 0,1476", "80,1463 540,1386 540,1768", "0,1409 540,1768 540,1920 0,1920"]
    for i, p in enumerate(polys_der):
        k, pico = luz(4.9 + 0.35 * i)
        lob_der.append((p, cols[i], 0.55 * k))
        lob_der.append((p, "#fff6c2", 0.7 * pico))
    polys_izq = ["540,1000 1080,1000 1080,1267 540,1912", "1080,1267 1080,1920 540,1920 540,1912"]
    for i, p in enumerate(polys_izq):
        k, pico = luz(6.0 + 0.35 * i)
        lob_izq.append((p, cols[i], 0.55 * k))
        lob_izq.append((p, "#fff6c2", 0.7 * pico))
    fis = seg(t, 4.7, 5.1)
    fis_der = (f"<path d='M158 1450 L458 1400 M152 1510 L430 1695' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' opacity='{fis:.2f}'/>")
    fis_izq = (f"<path d='M902 1470 L720 1697' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' opacity='{seg(t, 5.8, 6.1):.2f}'/>")
    # bronquiolos claros
    ramas_d = "<path d='M446 1336 Q380 1380 330 1470 M400 1370 Q330 1330 270 1300 M380 1400 Q360 1520 300 1600' fill='none' stroke='#ffd7de' stroke-width='9' stroke-linecap='round' opacity='0.8'/>"
    ramas_i = "<path d='M640 1328 Q720 1360 770 1440 M690 1345 Q760 1300 810 1290 M740 1400 Q800 1500 820 1600' fill='none' stroke='#ffd7de' stroke-width='9' stroke-linecap='round' opacity='0.8'/>"

    sx, sy = 1 + 0.045 * br, 1 + 0.06 * br
    s.append(pulmon(DER, "cder", 310, 1150, sx, sy, lob_der, t, ramas_d + fis_der))
    s.append(pulmon(IZQ, "cizq", 760, 1180, sx, sy, lob_izq, t, ramas_i + fis_izq))

    # caras
    ghost = seg(t, 2.4, 2.9) * (1 - seg(t, 4.7, 5.1))
    if t < 2.4:
        m_d, m_i, lk_d, lk_i = "feliz", "feliz", (4, 0), (-4, 0)
    elif t < 4.8:
        m_d, m_i, lk_d, lk_i = "feliz", "timido", (10, 0), (4, 8)
    elif t < REVELACION:
        m_d, m_i, lk_d, lk_i = "feliz", "feliz", (0, -6), (0, -6)
    else:
        m_d, m_i, lk_d, lk_i = "sorpresa", "amor", (12, 6), (-12, 6)
    s.append(f"<g transform='translate(310,1150) scale({sx:.4f},{sy:.4f}) translate(-310,-1150)'>{cara(300, 1390, t, *lk_d, m_d, 0.0)}</g>")
    s.append(f"<g transform='translate(760,1180) scale({sx:.4f},{sy:.4f}) translate(-760,-1180)'>{cara(800, 1385, t, *lk_i, m_i, 1.1)}</g>")

    s.append(corazon(t, rev))

    # silueta fantasma: el pulmón derecho reflejado no cabe en el lado izquierdo
    if ghost > 0.01:
        s.append(f"<g transform='translate(1080,0) scale(-1,1)' opacity='{ghost:.2f}'>"
                 f"<path d='{DER}' fill='#ffffff' fill-opacity='0.22' stroke='#ffffff' stroke-width='8' stroke-dasharray='24 16' "
                 f"stroke-dashoffset='{-t * 50:.0f}' stroke-linejoin='round'/></g>")
    # muesca del corazón resaltada en la revelación
    if rev > 0.01:
        s.append(f"<g transform='translate(760,1180) scale({sx:.4f},{sy:.4f}) translate(-760,-1180)'>"
                 f"<path d='{NOTCH}' fill='none' stroke='#ffe14d' stroke-width='{lerp(0, 16, rev):.1f}' stroke-linecap='round' opacity='{0.9 * (0.75 + 0.25 * math.sin(t * 9)):.2f}'/></g>")
        u = clamp((t - REVELACION) / 1.4)
        for ang, dist, rr in BURST:
            d = 130 + dist * ease(u)
            a = (1 - u) * 0.95
            if a > 0.02:
                px, py = 604 + d * math.cos(ang), 1572 + d * math.sin(ang)
                s.append(f"<g transform='translate({px:.0f},{py:.0f}) scale({rr / 60:.3f})'><path d='{CORAZON}' fill='#ff6b86' stroke='{INK}' stroke-width='10' opacity='{a:.2f}'/></g>")
    s.append("</g></g>")
    if flash > 0:
        s.append(f"<circle cx='604' cy='1572' r='900' fill='url(#flash)'/>")
    s.append("</svg>")
    return "".join(s)
