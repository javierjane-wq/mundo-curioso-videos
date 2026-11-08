"""2026-11-08-px · La Venus atrapamoscas «cuenta»: solo se cierra si se tocan 2 pelos sensores en pocos
segundos, y entonces se cierra en unos 0,1 s. Versión por código del Short de PixVerse del día.

Fuentes: Forterre et al., Nature 433, 421 (2005) "How the Venus flytrap snaps" (cierre en ~100 ms);
Böhm et al., Current Biology 26, 286 (2016) "The Venus flytrap Dionaea muscipula counts prey-induced
action potentials" (dos toques cierran la trampa).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.4    # la trampa se cierra de golpe
MUSICA = 6

rng = np.random.default_rng(23)
TUFTS = [(rng.uniform(0, W), rng.uniform(1300, 1900), rng.uniform(0.7, 1.3), rng.uniform(0, 6.28)) for _ in range(16)]
MOSS = [(rng.uniform(0, W), rng.uniform(1280, 1900), rng.uniform(8, 22)) for _ in range(55)]
SPARK = [(rng.uniform(-360, 360), rng.uniform(-420, 260), rng.uniform(10, 22), rng.uniform(0, 6.28)) for _ in range(14)]
LEAVES = [(rng.uniform(0, 6.28), rng.uniform(260, 520), rng.uniform(-200, 200)) for _ in range(10)]

HX, HY = 285, 1470               # bisagra de la trampa (vista de lado, como unas mandíbulas)
L, HJ = 440, 175                 # largo y alto de cada lóbulo
UP0, LOW0 = 38, 12               # apertura (grados) del lóbulo de arriba y del de abajo
HAIRS = [175, 315]
CX, CY = HX + 230, HY - 30       # centro visual de la trampa (zoom, destello)               # pelos sensores sobre el lóbulo de abajo (distancia a la bisagra)
TOUCH1, TOUCH2, SNAP = 3.6, 5.8, 7.15
GREEN, GREEN_D, GREEN_L = "#5cc93a", "#2f8f2a", "#a8ec6a"
RED, RED_D = "#e8323a", "#b51f2d"


def half(rx, ry, cx, n=36):
    return " ".join(f"{cx + rx * math.cos(math.pi * i / n):.1f},{-ry * math.sin(math.pi * i / n):.1f}" for i in range(n + 1))


def teeth(t, down=True, shift=0.0, closed=0.0):
    out = []
    sg = 1 if down else -1
    for i in range(12):
        x = 40 + i * 34 + shift
        if x > L - 20: break
        ln = 58 + 6 * math.sin(i * 1.9) + 3 * math.sin(t * 5 + i)
        lean = lerp(10, 0, closed) * (x / L)
        out.append(f"<path d='M{x - 7:.1f} 0 L{x + lean:.1f} {sg * ln:.1f} L{x + 7:.1f} 0' fill='{GREEN_L}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return "".join(out)


def jaw(t, lower, red_k):
    """Lóbulo visto de lado: concha verde con la cara interior roja y dientes en el borde."""
    face = mix(RED, GREEN, red_k)
    g = [f"<polygon points='{half(L / 2, HJ, L / 2)}' fill='{GREEN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<polygon points='{half(L / 2 - 30, HJ - 32, L / 2 + 6)}' fill='{face}' stroke='{mix(RED_D, GREEN_D, red_k)}' stroke-width='4'/>"]
    if red_k < 0.9:
        for i in range(9):
            a = math.pi * (i + 0.5) / 9
            for rr in (0.4, 0.7):
                g.append(f"<circle cx='{L / 2 + 6 + (L / 2 - 50) * rr * math.cos(a):.0f}' cy='{-(HJ - 40) * rr * math.sin(a):.0f}' r='5' fill='{RED_D}' opacity='{0.7 * (1 - red_k):.2f}'/>")
    for i in range(1, 6):
        a = math.pi * i / 6
        g.append(f"<path d='M{L / 2 + (L / 2 - 30) * math.cos(a):.0f} {-(HJ - 32) * math.sin(a):.0f} L{L / 2 + (L / 2 - 6) * math.cos(a):.0f} {-(HJ - 6) * math.sin(a):.0f}' stroke='{GREEN_D}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M{L * 0.25:.0f} {-HJ * 0.86:.0f} Q{L * 0.5:.0f} {-HJ * 1.02:.0f} {L * 0.75:.0f} {-HJ * 0.86:.0f}' fill='none' stroke='{GREEN_L}' stroke-width='10' stroke-linecap='round' opacity='0.7'/>")
    body = "".join(g)
    return f"<g transform='scale(1,-1)'>{body}</g>" if lower else body


def hair(x, glow):
    g = []
    if glow > 0.01:
        g.append(f"<circle cx='{x}' cy='-30' r='{lerp(14, 42, glow):.1f}' fill='#fff59a' opacity='{0.8 * glow:.2f}'/>")
    g.append(f"<line x1='{x}' y1='14' x2='{x}' y2='-26' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<circle cx='{x}' cy='-30' r='7' fill='{mix('#ffd0d0', '#fff36a', glow)}' stroke='{INK}' stroke-width='3'/>")
    return "".join(g)


def touch_glow(t, a):
    return clamp(1 - abs(t - a - 0.15) / 0.55) if t > a - 0.4 else 0.0


def fly(x, y, t, flying, scale=1.0, look=1):
    """Mosca original: cuerpo azul oscuro a franjas, dos alas transparentes, ojos rojos grandes, 6 patas."""
    wing = 28 * math.sin(t * 70) if flying else 6 * math.sin(t * 3)
    blink = 0.15 if ((t + 1.3) % 2.7) < 0.12 else 1.0
    g = [f"<g transform='translate({x:.1f},{y:.1f}) scale({scale * look:.3f},{scale:.3f})'>"]
    # patas
    for i, lx in enumerate((-22, 0, 22)):
        step = 6 * math.sin(t * 16 + i * 2) if not flying else 0
        g.append(f"<path d='M{lx} 10 L{lx - 14 + step:.0f} 34 L{lx - 18 + step:.0f} 46' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")
        g.append(f"<path d='M{lx} 10 L{lx + 12 - step:.0f} 36 L{lx + 16 - step:.0f} 46' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/>")
    # alas
    for sgn, dx in ((-1, -8), (1, 10)):
        g.append(f"<g transform='translate({dx},-18) rotate({-30 * sgn + wing * sgn:.1f})'>"
                 f"<ellipse cx='{-30 * sgn}' cy='-24' rx='42' ry='22' fill='#e6f6ff' opacity='0.8' stroke='{INK}' stroke-width='5'/>"
                 f"<path d='M0 0 L{-50 * sgn} -26' stroke='#9cc8e0' stroke-width='3'/></g>")
    # abdomen y tórax
    g.append(f"<ellipse cx='-30' cy='4' rx='42' ry='30' fill='#3a4a78' stroke='{INK}' stroke-width='{LW - 2}'/>")
    for k in (-44, -28):
        g.append(f"<path d='M{k} -22 Q{k - 6} 4 {k} 30' fill='none' stroke='#8fa3c9' stroke-width='6'/>")
    g.append(f"<ellipse cx='18' cy='0' rx='30' ry='26' fill='#2b3558' stroke='{INK}' stroke-width='{LW - 2}'/>")
    # cabeza con ojos rojos grandes
    g.append(f"<circle cx='52' cy='-6' r='26' fill='#4a5a88' stroke='{INK}' stroke-width='{LW - 2}'/>")
    for ex in (44, 70):
        g.append(f"<ellipse cx='{ex}' cy='-16' rx='19' ry='{21 * blink:.1f}' fill='#e8442e' stroke='{INK}' stroke-width='5'/>")
        if blink > 0.5:
            g.append(f"<circle cx='{ex + 4}' cy='-18' r='8' fill='#1a1010'/><circle cx='{ex + 6}' cy='-22' r='3.5' fill='#fff'/>")
    g.append(f"<path d='M56 10 Q62 16 68 10' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def on_chord(d, ang, lift=0):
    """Punto del borde del lóbulo de abajo a distancia d de la bisagra (lift: hacia arriba)."""
    r = math.radians(ang)
    return HX + d * math.cos(r) + lift * math.sin(r), HY + d * math.sin(r) - lift * math.cos(r)


def fly_track(t):
    """(d sobre el borde o None, x, y en vuelo, mirando)."""
    if t < 2.7:
        a = t * 2.3
        return None, 560 + 230 * math.sin(a), 900 + 110 * math.sin(2 * a) + lerp(0, 160, seg(t, 1.4, 2.7)), (1 if math.cos(a) > 0 else -1)
    if t < 3.25:
        return "landing", seg(t, 2.7, 3.25), 0, 1
    if t < 4.6:
        return lerp(110, 140, seg(t, 3.3, 3.6)), 0, 0, 1
    return lerp(140, 280, seg(t, 4.6, 5.75)), 0, 0, 1


def mini_trap(bx, by, sc, rot, k, t):
    sw = 3 * math.sin(t * 1.5 + bx)
    return (f"<g transform='translate({bx},{by}) rotate({rot + sw:.1f}) scale({sc})'>"
            f"<path d='M0 300 Q-20 150 0 0' fill='none' stroke='{INK}' stroke-width='44' stroke-linecap='round'/>"
            f"<path d='M0 300 Q-20 150 0 0' fill='none' stroke='{GREEN}' stroke-width='26' stroke-linecap='round'/>"
            f"<g transform='rotate({-90 + 30 * k:.1f})'>{teeth(t, True)}{jaw(t, False, 0)}</g>"
            f"<g transform='rotate({-90 - 30 * k:.1f})'>{teeth(t, False, 17)}{jaw(t, True, 0)}</g></g>")


def plant_base(t):
    return "".join(mini_trap(*a, t) for a in ((150, 1780, 0.38, -25, 1), (900, 1760, 0.42, 25, 0.9), (60, 1900, 0.34, -40, 0), (1010, 1890, 0.34, 40, 0)))


def frame(t):
    sky_k = seg(t, SNAP, 8.4)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#3fb4f2', '#2a8ff0', sky_k)}'/>"
         f"<stop offset='1' stop-color='{mix('#c6efff', '#ffe9a8', sky_k)}'/></linearGradient>",
         "<radialGradient id='sun'><stop offset='0' stop-color='#fff8c8'/><stop offset='1' stop-color='#fff8c8' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='flash'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.95'/><stop offset='0.5' stop-color='#ffe46a' stop-opacity='0.5'/><stop offset='1' stop-color='#ffe46a' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # cámara: acercamiento lento y zoom en la revelación, con sacudida al cerrarse
    z = 1 + 0.05 * seg(t, 0, 7) + 0.16 * seg(t, REVELACION, 9.0)
    shake = 10 * math.sin(t * 90) * clamp(1 - abs(t - 7.4) / 0.25)
    body = []
    # sol y nubes
    body.append(f"<circle cx='880' cy='260' r='230' fill='url(#sun)' opacity='0.8'/>")
    body.append(f"<circle cx='880' cy='260' r='80' fill='#fff1a0' stroke='{INK}' stroke-width='{LW}'/>")
    for i, (cx, cy, sc) in enumerate([(160, 330, 1.4), (700, 560, 1.1), (330, 780, 0.9)]):
        dx = (t * (16 + 8 * i)) % 1500 - 300
        body.append(f"<g transform='translate({(cx + dx) % 1500 - 260:.0f},{cy}) scale({sc})'>"
                    f"<path d='M0 50 Q0 0 60 10 Q90 -40 150 0 Q210 -20 230 40 Q260 70 220 80 L20 80 Q-20 80 0 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # colinas y pantano
    body.append(f"<path d='M0 1180 Q220 1080 470 1150 T1080 1120 L1080 1920 L0 1920 Z' fill='#7fcf5a' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<path d='M0 1290 Q300 1230 600 1280 T1080 1260 L1080 1920 L0 1920 Z' fill='#4fa83a' stroke='{INK}' stroke-width='{LW}'/>")
    body.append(f"<ellipse cx='210' cy='1560' rx='170' ry='38' fill='#6fc6e8' stroke='{INK}' stroke-width='7'/>")
    body.append(f"<ellipse cx='880' cy='1650' rx='140' ry='32' fill='#6fc6e8' stroke='{INK}' stroke-width='7'/>")
    for i, (px, py) in enumerate(((210, 1560), (880, 1650))):
        rr = (t * 50 + i * 40) % 120
        body.append(f"<ellipse cx='{px}' cy='{py}' rx='{rr:.0f}' ry='{rr * 0.22:.0f}' fill='none' stroke='#e8f8ff' stroke-width='4' opacity='{1 - rr / 120:.2f}'/>")
    for mx, my, mr in MOSS:
        body.append(f"<circle cx='{mx:.0f}' cy='{my:.0f}' r='{mr:.0f}' fill='#3d8c30' opacity='0.55'/>")
    for gx, gy, gs, ph in TUFTS:
        sw = 6 * math.sin(t * 2 + ph)
        body.append(f"<g transform='translate({gx:.0f},{gy:.0f}) scale({gs:.2f})'>"
                    + "".join(f"<path d='M{dx} 0 Q{dx + sw + dx * 0.3:.0f} -40 {dx * 1.8 + sw:.0f} -70' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
                              f"<path d='M{dx} 0 Q{dx + sw + dx * 0.3:.0f} -40 {dx * 1.8 + sw:.0f} -70' fill='none' stroke='#8ee05a' stroke-width='6' stroke-linecap='round'/>" for dx in (-14, 0, 14))
                    + "</g>")
    body.append(plant_base(t))
    # tallo principal hasta la bisagra
    sway = 5 * math.sin(t * 1.3)
    hx, hy = HX + sway, HY
    stem = f"M470 1930 Q{390 + sway:.0f} 1700 {hx:.0f} {hy + 20}"
    body.append(f"<path d='{stem}' fill='none' stroke='{INK}' stroke-width='62' stroke-linecap='round'/>")
    body.append(f"<path d='{stem}' fill='none' stroke='{GREEN}' stroke-width='44' stroke-linecap='round'/>")
    body.append(f"<path d='M458 1930 Q{376 + sway:.0f} 1700 {hx - 10:.0f} {hy + 30}' fill='none' stroke='{GREEN_L}' stroke-width='9' stroke-linecap='round' opacity='0.7'/>")

    # contador: dos luces que se encienden con cada toque
    for i, (a, dx) in enumerate(((TOUCH1, -75), (TOUCH2, 75))):
        k = rebote(t, a + 0.1, 0.45)
        if k > 0:
            big = 1 + 0.35 * seg(t, REVELACION, 7.9) + 0.12 * max(0, pulso(t, 0.6, i * 0.3)) * seg(t, REVELACION, 8)
            cx, cy = 540 + dx, 1080
            if t > REVELACION:
                for j in range(8):
                    an = j * math.pi / 4 + t * 0.8
                    r1, r2 = 50 * big, 80 * big
                    body.append(f"<line x1='{cx + r1 * math.cos(an):.0f}' y1='{cy + r1 * math.sin(an):.0f}' x2='{cx + r2 * math.cos(an):.0f}' y2='{cy + r2 * math.sin(an):.0f}' stroke='#fff36a' stroke-width='8' stroke-linecap='round' opacity='{seg(t, REVELACION, 7.8):.2f}'/>")
            body.append(f"<circle cx='{cx}' cy='{cy}' r='{60 * k * big:.1f}' fill='#fff59a' opacity='0.45'/>")
            body.append(f"<circle cx='{cx}' cy='{cy}' r='{34 * k * big:.1f}' fill='#ffe03a' stroke='{INK}' stroke-width='7'/>")
            body.append(f"<circle cx='{cx - 10 * k:.1f}' cy='{cy - 10 * k:.1f}' r='{9 * k:.1f}' fill='#fff' opacity='0.85'/>")

    # trampa: dos lóbulos como mandíbulas con dientes
    snap = seg(t, SNAP, SNAP + 0.25)
    trem = 0
    if TOUCH1 < t < TOUCH1 + 0.5: trem += 3 * math.sin((t - TOUCH1) * 45) * (1 - (t - TOUCH1) / 0.5)
    if TOUCH2 < t < TOUCH2 + 0.6: trem += 5 * math.sin((t - TOUCH2) * 45) * (1 - (t - TOUCH2) / 0.6)
    ang_up = lerp(UP0 + trem, 0, snap)
    ang_low = lerp(LOW0 - trem * 0.3, 0, snap)
    if t > SNAP + 0.25:
        ang_up = -2.5 * math.sin((t - SNAP - 0.25) * 30) * clamp(1 - (t - SNAP - 0.25) / 0.5)
    closed = seg(t, SNAP + 0.1, SNAP + 0.35)
    tilt = 4 * math.sin(t * 6) * seg(t, 8.2, 8.6) - 4 * seg(t, SNAP, 7.6)
    tr = [f"<g transform='translate({hx:.1f},{hy}) rotate({tilt:.1f})'>"]
    # lóbulo de abajo
    tr.append(f"<g transform='rotate({ang_low:.2f})'>{jaw(t, True, closed)}")
    for d, a in zip(HAIRS, (TOUCH1, TOUCH2)):
        tr.append(hair(d, touch_glow(t, a)))
        k = seg(t, a, a + 0.5)
        if 0 < k < 1:
            tr.append(f"<circle cx='{d}' cy='-30' r='{lerp(10, 90, k):.0f}' fill='none' stroke='#fff36a' stroke-width='8' opacity='{1 - k:.2f}'/>")
    tr.append(teeth(t, False, 17, closed))
    tr.append("</g>")
    # mosca posada sobre el borde del lóbulo de abajo
    d, fx, fy, look = fly_track(t)
    if d is not None:
        if d == "landing":
            k = fx
            x0, y0 = 560 + 230 * math.sin(2.7 * 2.3), 900 + 110 * math.sin(5.4 * 2.3) + 160
            px, py = on_chord(110, ang_low, 52)
            x0 -= hx - sway * 0; y0 -= hy
            tr.append(fly(lerp(x0 - HX, px - HX, k), lerp(y0, py - HY, k) , t, True, 1.25, 1))
        else:
            r = math.radians(ang_low)
            tr.append(f"<g transform='rotate({ang_low:.2f})'>{fly(d, -56, t, False, 1.25, 1)}</g>")
    # lóbulo de arriba (se cierra de golpe)
    tr.append(f"<g transform='rotate({-ang_up:.2f})'>{jaw(t, False, closed)}")
    peek = seg(t, 7.9, 8.4)
    if peek > 0:
        for ex in (215, 255):
            tr.append(f"<ellipse cx='{ex}' cy='4' rx='17' ry='{19 * peek:.1f}' fill='#e8442e' stroke='{INK}' stroke-width='5'/>"
                      f"<circle cx='{ex + 3 * math.sin(t * 3):.1f}' cy='6' r='{7 * peek:.1f}' fill='#1a1010'/>")
    tr.append(teeth(t, True, 0, closed))
    tr.append("</g></g>")
    body.append("".join(tr))
    # mosca volando (fuera de la trampa)
    if d is None:
        body.append(fly(fx, fy, t, True, 1.25, look))
    # líneas de movimiento y hojitas al cerrarse
    k = seg(t, SNAP, SNAP + 0.6)
    if 0 < k < 1:
        for j, sg in enumerate((-1, 1)):
            for r in (300, 350, 400):
                body.append(f"<path d='M{CX + sg * r * 0.95:.0f} {CY - 200} Q{CX + sg * (r + 40):.0f} {CY} {CX + sg * r * 0.95:.0f} {CY + 200}' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='{1 - k:.2f}'/>")
    kl = seg(t, REVELACION, REVELACION + 1.4)
    if 0 < kl < 1:
        for an, sp, dx in LEAVES:
            lx = CX + math.cos(an) * sp * kl + dx * 0.2
            ly = CY + math.sin(an) * sp * kl - 120 * kl + 300 * kl * kl
            body.append(f"<ellipse cx='{lx:.0f}' cy='{ly:.0f}' rx='18' ry='9' transform='rotate({an * 57 + t * 300:.0f} {lx:.0f} {ly:.0f})' fill='#8ee05a' stroke='{INK}' stroke-width='4' opacity='{1 - kl:.2f}'/>")
    # destello y chispas de la revelación
    fl = clamp(1 - abs(t - 7.5) / 0.45)
    if fl > 0:
        body.append(f"<circle cx='{CX}' cy='{CY}' r='{lerp(200, 700, seg(t, 7.2, 8.0)):.0f}' fill='url(#flash)' opacity='{fl:.2f}'/>")
    sp = seg(t, REVELACION, 8.0)
    if sp > 0:
        for sx, sy, sr, ph in SPARK:
            a = sp * (0.5 + 0.5 * math.sin(t * 5 + ph))
            x, y, r = CX + sx, CY + sy, sr * (0.8 + 0.4 * math.sin(t * 4 + ph))
            body.append(f"<path d='M{x:.0f} {y - r * 2:.0f} L{x + r * 0.5:.0f} {y - r * 0.5:.0f} L{x + r * 2:.0f} {y:.0f} L{x + r * 0.5:.0f} {y + r * 0.5:.0f} L{x:.0f} {y + r * 2:.0f} "
                        f"L{x - r * 0.5:.0f} {y + r * 0.5:.0f} L{x - r * 2:.0f} {y:.0f} L{x - r * 0.5:.0f} {y - r * 0.5:.0f} Z' fill='#fff36a' stroke='{INK}' stroke-width='3' opacity='{a:.2f}'/>")
    s.append(f"<g transform='translate({shake:.1f},0)'>")
    s.append(zoom(CX, CY + 40, z, "".join(body)))
    s.append("</g></svg>")
    return "".join(s)
