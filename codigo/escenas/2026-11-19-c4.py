"""Short 2026-11-19-c4: las gotas de lluvia no tienen forma de lágrima: las pequeñas son
redondas y, al caer, el aire aplasta las grandes por abajo como un pan de hamburguesa (USGS)."""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 6.9    # la gota se aplasta como un pan de hamburguesa: destello y zoom
MUSICA = 2

CX, CY, R = 540, 1360, 215
NP = 96

rng = np.random.default_rng(1904)
STREAKS = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(40, 110), rng.uniform(0.7, 1.4)) for _ in range(55)]
SPARK = [(rng.uniform(0, 6.28), rng.uniform(300, 470), rng.uniform(10, 18)) for _ in range(22)]
CLOUDS = [(120, 300, 1.25, 10), (720, 210, 1.0, 14), (980, 470, 1.1, 8), (380, 560, 0.85, 12)]


def forma(k_punta, k_bun, t):
    """Puntos del contorno de la gota: lágrima (k_punta=1) -> esfera -> pan de hamburguesa (k_bun=1)."""
    pts = []
    for i in range(NP):
        a = 2 * math.pi * i / NP
        s, c = math.sin(a), math.cos(a)
        # esfera
        xs, ys = R * s, -R * c
        # lágrima con punta arriba
        xt = R * 1.12 * s * abs(math.sin(a / 2)) ** 1.15
        yt = -R * 1.18 * c + R * 0.08
        # pan de hamburguesa: cúpula arriba, base plana con un pequeño hoyuelo
        xb = R * 1.34 * math.copysign(abs(s) ** 0.8, s)
        if c > 0:
            yb = -R * 0.98 * c ** 0.85
        else:
            yb = R * 0.30 * (-c) ** 0.3 - R * 0.07 * math.exp(-(s / 0.3) ** 2)
        yb += R * 0.25
        x = lerp(xs, xt, k_punta); y = lerp(ys, yt, k_punta)
        x = lerp(x, xb, k_bun); y = lerp(y, yb, k_bun)
        # temblor de la superficie (agua viva)
        wob = 1 + 0.018 * math.sin(3 * a + t * 7) + 0.012 * math.sin(5 * a - t * 9)
        pts.append((x * wob, y * wob))
    return pts


def camino(pts):
    """Curva suave cerrada (Catmull-Rom -> Bézier)."""
    n = len(pts); d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(d) + "Z"


def nube(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M-150 40 Q-160 -20 -95 -25 Q-80 -85 -10 -70 Q40 -115 95 -60 Q160 -60 155 0 Q185 40 140 55 L-130 55 Q-165 55 -150 40 Z' "
            f"fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def gota(t):
    k_punta = 1 - seg(t, 4.7, 5.9)
    k_bun = seg(t, 6.0, REVELACION)
    jig = 0.04 * math.sin(t * 16) * math.exp(-max(0, t - REVELACION) * 2.5) * (t > REVELACION)
    # al final el aire la frena y sube un poco (deja sitio al cierre «¡SÍGUEME!»)
    y = lerp(1180, CY, ease(seg(t, 0, 1.3))) + 10 * math.sin(t * 2.6) - 150 * seg(t, 7.5, 8.2)
    rot = 6 * math.sin(t * 1.9) * (1 - k_bun) + 9 * (1 - seg(t, 0, 1.3))
    pts = forma(k_punta, k_bun, t)
    d = camino(pts)
    g = [f"<g transform='translate({CX + 14 * math.sin(t * 1.3):.1f},{y:.1f}) rotate({rot:.2f}) scale({1 + jig:.3f},{1 - jig:.3f})'>"]
    g.append(f"<path d='{d}' fill='url(#agua)' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # brillos
    hx, hy = lerp(-95, -150, k_bun), lerp(-70, -95, k_bun) + lerp(0, -30, k_punta)
    g.append(f"<ellipse cx='{hx:.0f}' cy='{hy:.0f}' rx='{lerp(34, 46, k_bun):.0f}' ry='{lerp(58, 30, k_bun):.0f}' fill='#ffffff' opacity='0.85' transform='rotate(-28 {hx:.0f} {hy:.0f})'/>")
    g.append(f"<circle cx='{hx + 40:.0f}' cy='{hy - 55 + 25 * k_bun:.0f}' r='14' fill='#ffffff' opacity='0.85'/>")
    # cara
    fy = lerp(20, -5, k_bun) + lerp(0, 10, k_punta)
    blink = 0.12 if ((t + 1.2) % 2.7) < 0.13 or abs(t - 6.3) < 0.07 else 1.0
    look = 10 * math.sin(t * 0.9) * (1 - k_bun)
    sx = lerp(1, 1.12, k_bun); sy = lerp(1, 0.9, k_bun)
    g.append(f"<g transform='translate(0,{fy:.1f}) scale({sx:.3f},{sy:.3f})'>")
    for ex in (-62, 62):
        g.append(f"<ellipse cx='{ex}' cy='-10' rx='38' ry='{46 * blink:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='7'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + look:.1f}' cy='-4' r='22' fill='{INK}'/>"
                     f"<circle cx='{ex + look - 8:.1f}' cy='-13' r='8' fill='#ffffff'/>")
    for ex in (-108, 108):
        g.append(f"<ellipse cx='{ex}' cy='42' rx='24' ry='13' fill='#ff8fb1' opacity='0.75'/>")
    sorpresa = seg(t, 5.0, 5.6) * (1 - seg(t, REVELACION, REVELACION + 0.3))
    alegria = seg(t, REVELACION, REVELACION + 0.4)
    if alegria > 0.05:
        g.append(f"<path d='M-44 48 Q0 {48 + 48 * alegria:.0f} 44 48 Z' fill='#7a2230' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    elif sorpresa > 0.05:
        g.append(f"<ellipse cx='0' cy='58' rx='{10 + 8 * sorpresa:.0f}' ry='{10 + 14 * sorpresa:.0f}' fill='#7a2230' stroke='{INK}' stroke-width='7'/>")
    else:
        g.append(f"<path d='M-30 50 Q0 74 30 50' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    g.append("</g></g>")
    return "".join(g), y


def frame(t):
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.6)
    flash = clamp(1 - abs(t - REVELACION - 0.08) / 0.35)
    top = mix("#5577b4", "#3fa9f5", rev); mid = mix("#86a8da", "#7fd0ff", rev); low = mix("#b6cde9", "#c8f0ff", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<linearGradient id='agua' x1='0' y1='0' x2='0.4' y2='1'><stop offset='0' stop-color='#a6e6ff'/>"
            "<stop offset='0.55' stop-color='#42b0f5'/><stop offset='1' stop-color='#1f74d1'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.75 * rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#bff0ff' stop-opacity='{0.45 * rev:.3f}'/>"
            "<stop offset='1' stop-color='#bff0ff' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         f"<defs>{defs}</defs>", f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION - 0.1, 9.6)
    s.append(f"<g transform='translate({CX},{CY}) scale({z:.4f}) translate({-CX},{-CY})'>")
    # rayos de sol que salen en la revelación
    if rev > 0.02:
        for i in range(12):
            a = i * 30 + t * 6
            s.append(f"<path d='M0 0 L{1400 * math.cos(math.radians(a - 5)):.0f} {1400 * math.sin(math.radians(a - 5)):.0f} "
                     f"L{1400 * math.cos(math.radians(a + 5)):.0f} {1400 * math.sin(math.radians(a + 5)):.0f} Z' "
                     f"fill='#fff6c8' opacity='{0.22 * rev:.3f}' transform='translate({CX},{CY})'/>")
    # nubes (arriba, tranquilas)
    for x, y, sc, sp in CLOUDS:
        xx = (x + t * sp) % 1400 - 160
        s.append(nube(xx, y, sc, mix("#d5deeb", "#ffffff", rev)))
    # colinas y pueblo muy abajo (la gota va bajando: suben despacio)
    up = lerp(0, 90, t / DUR)
    s.append(f"<path d='M0 {1800 - up:.0f} Q270 {1700 - up:.0f} 560 {1780 - up:.0f} T1080 {1730 - up:.0f} L1080 1920 L0 1920 Z' "
             f"fill='{mix('#5fae5a', '#6fd26a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for hx, hw, hh, col in ((120, 90, 70, "#ff8a5c"), (300, 70, 60, "#ffd25e"), (820, 100, 80, "#ff6f91"), (960, 70, 55, "#a98bff")):
        by = 1812 - up - (30 if hx > 600 else 0)
        s.append(f"<rect x='{hx}' y='{by - hh:.0f}' width='{hw}' height='{hh}' fill='{col}' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M{hx - 12} {by - hh:.0f} L{hx + hw / 2:.0f} {by - hh - 45:.0f} L{hx + hw + 12} {by - hh:.0f} Z' fill='#b8473a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    s.append(f"<path d='M0 {1870 - up * 0.6:.0f} Q360 {1800 - up * 0.6:.0f} 700 {1860 - up * 0.6:.0f} T1080 {1840 - up * 0.6:.0f} L1080 1920 L0 1920 Z' "
             f"fill='{mix('#3f8f4a', '#4fb85a', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    # lluvia de fondo y líneas de velocidad (suben: la gota cae)
    for x, ph, ln, sp in STREAKS:
        yy = 1950 - ((ph * 2000 + t * 900 * sp) % 2000)
        if abs(x - CX) < 330 and 1050 < yy < 1650:
            continue
        s.append(f"<line x1='{x:.0f}' y1='{yy:.0f}' x2='{x:.0f}' y2='{yy + ln:.0f}' stroke='#ffffff' stroke-width='5' stroke-linecap='round' opacity='0.55'/>")
    # halo
    s.append(f"<circle cx='{CX}' cy='{CY}' r='{lerp(250, 560, rev):.0f}' fill='url(#halo)'/>")
    cuerpo, gy = gota(t)
    # aire que empuja desde abajo (aparece al cambiar de forma)
    aire = seg(t, 5.6, 6.4)
    if aire > 0.02:
        for i, dx in enumerate((-200, -110, 0, 110, 200)):
            ph = (t * 1.6 + i * 0.23) % 1
            yb = gy + lerp(250, 175, seg(t, 6.0, REVELACION)) - ph * 90 + abs(dx) * -0.25
            op = aire * math.sin(math.pi * ph) * 0.95
            s.append(f"<path d='M{CX + dx - 26} {yb + 40:.0f} Q{CX + dx} {yb - 14:.0f} {CX + dx + 26} {yb + 40:.0f}' fill='none' "
                     f"stroke='#ffffff' stroke-width='13' stroke-linecap='round' opacity='{op:.2f}'/>")
    s.append(cuerpo)
    # chispas en la revelación
    if t > REVELACION:
        k = seg(t, REVELACION, REVELACION + 0.9)
        for a, dist, rr in SPARK:
            px = CX + math.cos(a + t * 0.5) * dist * (0.6 + 0.4 * k)
            py = CY + math.sin(a + t * 0.5) * dist * (0.6 + 0.4 * k) * 0.8
            tw = 0.6 + 0.4 * math.sin(t * 8 + a * 5)
            if py < 1010:
                continue
            s.append(f"<path d='M{px:.0f} {py - rr * 2:.0f} L{px + rr * 0.5:.0f} {py:.0f} L{px:.0f} {py + rr * 2:.0f} L{px - rr * 0.5:.0f} {py:.0f} Z' "
                     f"fill='#fff4a8' stroke='{INK}' stroke-width='3' opacity='{tw * k:.2f}'/>")
    s.append("</g>")
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.55 * flash:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
