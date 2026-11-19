"""Short 2026-11-19-c3: la cola de un cometa siempre apunta lejos del Sol
(al acercarse va detrás; al alejarse, ¡va por delante!)."""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.0    # el cometa se aleja con la cola por delante: destello y zoom
MUSICA = 6

SX, SY, SR = 270, 1450, 105          # Sol (abajo a la izquierda)
R0 = 290                              # radio de la curva alrededor del Sol
ARM = math.pi * R0                    # largo de los tramos rectos (misma velocidad que en la curva)

rng = np.random.default_rng(1119)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(95)]
WIND = [(rng.uniform(0, 6.28), rng.uniform(0, 1), rng.uniform(0.8, 1.3)) for _ in range(46)]
SPARK = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(3, 7)) for _ in range(26)]


def u_de(t):
    """Parámetro de la órbita: rápido junto al Sol (t≈4,4), lento lejos."""
    if t < 4.4:
        return 1.35 * math.sin(math.pi / 2 * (4.4 - t) / 4.4)
    k = clamp((t - 4.4) / 3.75)
    return -1.15 * math.sin(math.pi / 2 * k) - 0.04 * max(0.0, t - 8.15)


def pos_u(u):
    """Llega por abajo a la derecha, rodea el Sol por la izquierda y se va por arriba a la derecha."""
    if abs(u) <= 0.5:
        f = math.pi - u * math.pi
        return SX + R0 * math.cos(f), SY + R0 * math.sin(f)
    s = abs(u) - 0.5
    sg = 1 if u > 0 else -1
    return SX + s * ARM, SY + sg * (R0 + s * 70)


def pos(t):
    return pos_u(u_de(t))


def fondo(t, rev):
    top = mix("#141033", "#1d1450", rev); mid = mix("#22195a", "#33207a", rev); low = mix("#2d2466", "#46308e", rev)
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nebulosa suave arriba (zona de textos tranquila)
    s.append(f"<ellipse cx='760' cy='520' rx='520' ry='260' fill='url(#neb)' opacity='0.55'/>")
    s.append(f"<ellipse cx='240' cy='860' rx='380' ry='170' fill='url(#neb2)' opacity='0.45'/>")
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 2.6 + ph)
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff8e0' opacity='{a:.2f}'/>")
    # planeta lejano con anillo (abajo a la derecha)
    px, py = 840, 1460 + 6 * math.sin(t * 1.3)
    s.append(f"<g transform='translate({px},{py:.1f}) rotate(-14) scale(0.78)'>"
             f"<ellipse cx='0' cy='0' rx='150' ry='34' fill='none' stroke='{INK}' stroke-width='22'/>"
             f"<ellipse cx='0' cy='0' rx='150' ry='34' fill='none' stroke='#f4b860' stroke-width='12'/>"
             f"<circle r='84' fill='#e9775a' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-80 -22 Q0 -40 80 -22' fill='none' stroke='#c95a44' stroke-width='12'/>"
             f"<path d='M-76 26 Q0 10 76 26' fill='none' stroke='#f09a74' stroke-width='10'/>"
             f"<path d='M-150 0 A150 34 0 0 0 150 0' fill='none' stroke='{INK}' stroke-width='22'/>"
             f"<path d='M-150 0 A150 34 0 0 0 150 0' fill='none' stroke='#f4b860' stroke-width='12'/></g>")
    # pequeño planeta azul a la izquierda abajo
    s.append(f"<circle cx='120' cy='{1830 + 5*math.sin(t*1.7+1):.1f}' r='44' fill='#4fb3e8' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M86 {1815 + 5*math.sin(t*1.7+1):.1f} q20 -10 38 4 q14 10 30 -2' fill='none' stroke='#8fe0a0' stroke-width='9' stroke-linecap='round'/>")
    return "".join(s)


def sol(t, rev):
    s = []
    s.append(f"<circle cx='{SX}' cy='{SY}' r='{SR*3.4 + 40*rev:.0f}' fill='url(#corona)'/>")
    rot = t * 14
    pts = []
    n = 18
    for i in range(2 * n):
        a = math.pi * i / n
        r = SR * (1.32 + 0.06 * math.sin(t * 6 + i)) if i % 2 == 0 else SR * 1.08
        pts.append(f"{SX + r*math.cos(a):.1f},{SY + r*math.sin(a):.1f}")
    s.append(f"<g transform='rotate({rot:.1f},{SX},{SY})'><polygon points='{' '.join(pts)}' fill='#ff9b2f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    s.append(f"<circle cx='{SX}' cy='{SY}' r='{SR}' fill='#ffd23f' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{SX}' cy='{SY}' r='{SR*0.72:.0f}' fill='#ffe98a'/>")
    s.append(f"<circle cx='{SX-38}' cy='{SY-40}' r='22' fill='#fff7cf' opacity='0.9'/>")
    # viento solar: rayitas que salen del Sol hacia fuera
    for ang, ph, sp in WIND:
        k = (t * 0.22 * sp + ph) % 1.0
        r1 = SR * 1.45 + k * 900
        a = 0.55 * (1 - k)
        x1, y1 = SX + r1 * math.cos(ang), SY + r1 * math.sin(ang)
        x2, y2 = SX + (r1 + 34) * math.cos(ang), SY + (r1 + 34) * math.sin(ang)
        s.append(f"<line x1='{x1:.0f}' y1='{y1:.0f}' x2='{x2:.0f}' y2='{y2:.0f}' stroke='#ffe7a3' stroke-width='5' stroke-linecap='round' opacity='{a:.2f}'/>")
    return "".join(s)


def cola(L, w, capas, t, fase):
    """Cola en coordenadas locales (apunta hacia +x). capas = [(color, escala)]."""
    g = []
    for i, (col, k) in enumerate(capas):
        LL, ww = L * k, w * k
        wv = 18 * math.sin(t * 7 + fase + i)
        d = (f"M0 {-46*k:.1f} C{LL*0.35:.1f} {-ww*0.8:.1f} {LL*0.7:.1f} {-ww + wv*0.4:.1f} {LL:.1f} {-ww*0.75 + wv:.1f} "
             f"Q{LL*0.86:.1f} {-ww*0.25:.1f} {LL*1.02:.1f} {wv*0.3:.1f} "
             f"Q{LL*0.86:.1f} {ww*0.25:.1f} {LL:.1f} {ww*0.75 - wv:.1f} "
             f"C{LL*0.7:.1f} {ww - wv*0.4:.1f} {LL*0.35:.1f} {ww*0.8:.1f} 0 {46*k:.1f} Z")
        sw = LW if i == 0 else 0
        g.append(f"<path d='{d}' fill='{col}' stroke='{INK}' stroke-width='{sw}' stroke-linejoin='round'/>")
    return "".join(g)


def cometa(t, rev):
    x, y = pos(t)
    x2, y2 = pos(t + 0.05)
    vx, vy = x2 - x, y2 - y
    vn = math.hypot(vx, vy) or 1
    vx, vy = vx / vn, vy / vn
    dx, dy = x - SX, y - SY
    dist = math.hypot(dx, dy)
    dx, dy = dx / dist, dy / dist
    prox = clamp(1 - (dist - 250) / 600)
    flare = 1 + 0.28 * seg(t, REVELACION, REVELACION + 0.6)
    L = (240 + 200 * prox) * flare
    if dy < -0.05:                     # la cola no sube a la zona de los textos
        L = min(L, (y - 960) / -dy)
    ang_ion = math.degrees(math.atan2(dy, dx))
    ddx, ddy = dx - 0.42 * vx, dy - 0.42 * vy
    ang_dust = math.degrees(math.atan2(ddy, ddx))
    g = []
    # brillo de la coma
    g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{140 + 30*prox + 40*rev:.0f}' fill='url(#coma)'/>")
    # cola de polvo (crema, algo curvada hacia atrás) y cola de iones (azul, recta)
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang_dust:.1f})'>"
             + cola(L * 0.82, 120 * flare, [("#ffd98a", 1.0), ("#fff1c4", 0.68)], t, 1.3) + "</g>")
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang_ion:.1f})'>"
             + cola(L, 82 * flare, [("#4fc3ff", 1.0), ("#a8e6ff", 0.7), ("#f2fbff", 0.42)], t, 0) + "</g>")
    # chispitas que se desprenden a lo largo de la cola
    for off, ph, r in SPARK:
        k = (t * 0.7 + ph) % 1.0
        sx = x + dx * L * k + (-dy) * off * 70 * k
        sy = y + dy * L * k + dx * off * 70 * k
        g.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{r*(1-k*0.6):.1f}' fill='#ffffff' opacity='{0.85*(1-k):.2f}'/>")
    # núcleo: roca de hielo con cara (siempre derecha)
    wob = 4 * math.sin(t * 5)
    g.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({wob:.1f}) scale(1.25)'>")
    g.append(f"<path d='M-62 -8 C-64 -44 -30 -66 4 -62 C40 -60 66 -34 62 2 C60 40 30 64 -6 60 C-42 58 -60 30 -62 -8 Z' "
             f"fill='#c9d6e6' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-40 -40 C-22 -56 10 -58 30 -46' fill='none' stroke='#ffffff' stroke-width='9' stroke-linecap='round'/>")
    g.append(f"<circle cx='34' cy='30' r='11' fill='#9fb0c6' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='-44' cy='22' r='7' fill='#9fb0c6' stroke='{INK}' stroke-width='4'/>")
    blink = 0.12 if ((t + 1.0) % 2.7) < 0.12 or abs(t - 6.1) < 0.07 else 1.0
    lx, ly = 9 * vx, 7 * vy
    for ex in (-20, 20):
        g.append(f"<g transform='translate({ex},-10) scale(1,{blink})'>"
                 f"<ellipse rx='17' ry='{20 + 4*rev:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='{lx:.1f}' cy='{ly:.1f}' r='10' fill='{INK}'/>"
                 f"<circle cx='{lx-3:.1f}' cy='{ly-4:.1f}' r='4' fill='#ffffff'/></g>")
    boca = 16 + 10 * rev
    g.append(f"<path d='M-14 22 Q0 {22 + boca:.1f} 14 22' fill='{'#7a2a2a' if rev > 0.2 else 'none'}' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='-38' cy='14' rx='9' ry='6' fill='#ff9fb0' opacity='0.8'/>"
             f"<ellipse cx='38' cy='14' rx='9' ry='6' fill='#ff9fb0' opacity='0.8'/>")
    g.append("</g>")
    return "".join(g), x, y


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)
    top = mix("#120e30", "#1c1150", rev); mid = mix("#211a58", "#2f1c76", rev); low = mix("#2e2468", "#4a2f90", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.5' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<radialGradient id='neb'><stop offset='0' stop-color='#8a5cd6' stop-opacity='0.7'/><stop offset='1' stop-color='#8a5cd6' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='neb2'><stop offset='0' stop-color='#3fa4d8' stop-opacity='0.6'/><stop offset='1' stop-color='#3fa4d8' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='corona'><stop offset='0' stop-color='#fff2b0' stop-opacity='0.95'/>"
            f"<stop offset='0.35' stop-color='#ffb347' stop-opacity='{0.55 + 0.25*rev:.2f}'/><stop offset='1' stop-color='#ff7a2f' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='coma'><stop offset='0' stop-color='#eafcff' stop-opacity='0.95'/>"
            f"<stop offset='0.45' stop-color='#7fdcff' stop-opacity='0.55'/><stop offset='1' stop-color='#4fc3ff' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>"]
    cx, cy = pos(REVELACION)
    z = 1 + 0.16 * seg(t, REVELACION, REVELACION + 1.0)
    s.append(f"<g transform='translate({cx:.1f},{cy:.1f}) scale({z:.4f}) translate({-cx:.1f},{-cy:.1f})'>")
    s.append(fondo(t, rev))
    # trayectoria punteada (órbita)
    pts = " ".join("%.0f,%.0f" % pos_u(u) for u in np.linspace(-1.6, 1.6, 90))
    s.append(f"<polyline points='{pts}' fill='none' stroke='#b9a8ff' stroke-width='5' stroke-dasharray='6 22' stroke-linecap='round' opacity='0.45'/>")
    s.append(sol(t, rev))
    c, x, y = cometa(t, rev)
    s.append(c)
    # destello en la revelación
    if REVELACION <= t < REVELACION + 1.0:
        k = (t - REVELACION) / 1.0
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{lerp(60, 330, k):.0f}' fill='none' stroke='#fff6c8' stroke-width='{lerp(18, 2, k):.1f}' opacity='{1-k:.2f}'/>")
        for i in range(10):
            a = i * math.pi / 5 + 0.3
            r = lerp(70, 260, ease(k))
            s.append(f"<circle cx='{x + r*math.cos(a):.0f}' cy='{y + r*math.sin(a):.0f}' r='{lerp(12, 3, k):.1f}' fill='#ffe98a' opacity='{1-k:.2f}'/>")
    s.append("</g></svg>")
    return "".join(s)
