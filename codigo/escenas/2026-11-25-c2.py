"""Fobos, la mayor luna de Marte, se acerca al planeta unos 2 m cada siglo; la gravedad de Marte
la está agrietando y en 30-50 millones de años la romperá en pedazos (NASA, 2015).

Marte (con cara) en la mitad de abajo; Fobos, una luna-patata gris con ojos y cráter, gira a su
alrededor en una órbita que se encoge. En la tensión se estira y se agrieta; en la REVELACION
estalla en rocas que se reparten formando un anillo alrededor de Marte (zoom + destello).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.2    # Fobos se rompe: golpe musical
MUSICA = 8

CX, CY, MR = 540, 1480, 290          # Marte
rng = np.random.default_rng(25)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1920), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(110)]
# fragmentos: ángulo en el anillo, radio relativo, tamaño, desvío del estallido, forma
FRAG = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.9, 1.1), rng.uniform(7, 17),
         rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 360)) for _ in range(54)]
PATCHES = [(-120, -60, 90, 45), (60, 40, 120, 50), (-40, 150, 110, 40), (150, -130, 70, 35),
           (-200, 90, 60, 40), (240, 120, 70, 30)]
DUSTP = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(3, 6)) for _ in range(14)]

PHOBOS = ("M-74 -8 Q-70 -48 -22 -52 Q30 -60 62 -32 Q84 -6 68 26 Q50 54 0 52 "
          "Q-52 56 -68 30 Q-80 12 -74 -8 Z")


def theta(t):
    """Ángulo de Fobos en su órbita: va rápido y frena delante de Marte en la tensión."""
    n = 120; tt = min(t, 7.2); dt = tt / n; a = 0.4
    for i in range(n):
        s = (i + 0.5) * dt
        a += lerp(1.8, 0.2, seg(s, 3.6, 4.6)) * dt
    return a


def orbita(t):
    rx = lerp(520, 400, seg(t, 0, 7.2))
    return rx, rx * 0.27


def phobos(x, y, t, sc, rot):
    tens = seg(t, 5.0, 7.0)
    jit = 5 * tens * math.sin(t * 61)
    stretch = 1 + 0.28 * tens
    blink = 0.12 if ((t + 1.3) % 2.7) < 0.11 else 1.0
    worry = seg(t, 5.0, 5.6)
    # mira hacia Marte
    dx, dy = CX - x, CY - 120 - y; d = math.hypot(dx, dy) or 1
    lx, ly = 7 * dx / d, 7 * dy / d
    g = [f"<g transform='translate({x + jit:.1f},{y:.1f}) rotate({rot:.1f}) scale({sc * stretch:.3f},{sc / (1 + 0.12 * tens):.3f})'>"]
    g.append(f"<path d='{PHOBOS}' fill='{mix('#a39686', '#b08a78', tens)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("<path d='M-50 -30 Q-20 -46 30 -42' fill='none' stroke='#c9bfb2' stroke-width='8' stroke-linecap='round'/>")
    # cráter Stickney y cráteres pequeños
    g.append(f"<ellipse cx='-40' cy='12' rx='20' ry='17' fill='#7d7268' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='-36' cy='16' rx='11' ry='9' fill='#6b6159'/>")
    g.append(f"<circle cx='44' cy='30' r='7' fill='#857a70' stroke='{INK}' stroke-width='4'/>")
    g.append(f"<circle cx='-8' cy='38' r='5' fill='#857a70' stroke='{INK}' stroke-width='3'/>")
    # surcos (estrías) siempre, grietas que se abren en la tensión
    for k in (-1, 0, 1):
        g.append(f"<path d='M-60 {k*14 - 4} Q0 {k*14 + 8} 60 {k*14 - 6}' fill='none' stroke='#8a7f74' stroke-width='3' opacity='0.8'/>")
    if tens > 0.05:
        op = clamp(tens * 1.4)
        g.append(f"<path d='M-10 -50 L0 -26 L-12 -6 L6 18 L-4 50' fill='none' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='{op:.2f}'/>")
        g.append(f"<path d='M40 -40 L30 -16 L48 4' fill='none' stroke='{INK}' stroke-width='5' stroke-linejoin='round' opacity='{op:.2f}'/>")
        g.append(f"<path d='M-60 -14 L-44 -2' fill='none' stroke='{INK}' stroke-width='5' opacity='{op:.2f}'/>")
        g.append(f"<path d='M-10 -50 L0 -26 L-12 -6 L6 18 L-4 50' fill='none' stroke='#ff8a3d' stroke-width='2' opacity='{op:.2f}'/>")
    # ojos
    er = 15 + 4 * worry
    for ex in (8, 40):
        g.append(f"<circle cx='{ex}' cy='-14' r='{er:.1f}' fill='#fff' stroke='{INK}' stroke-width='5'/>")
        g.append(f"<g transform='translate({ex + lx:.1f},{-14 + ly:.1f}) scale(1,{blink})'><circle r='8' fill='{INK}'/>"
                 f"<circle cx='-3' cy='-3' r='3' fill='#fff'/></g>")
    # boca: sonrisa -> "o" de susto
    if worry < 0.5:
        g.append(f"<path d='M14 12 Q24 20 34 12' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='24' cy='16' rx='7' ry='9' fill='#5a2a22' stroke='{INK}' stroke-width='4'/>")
    g.append("</g>")
    return "".join(g)


def marte(t, ox, oy):
    rev = seg(t, 7.2, 7.6)
    blink = 0.12 if ((t + 2.0) % 3.3) < 0.12 else 1.0
    spin = (t * 22) % 700
    s = [f"<clipPath id='mc'><circle cx='{CX}' cy='{CY}' r='{MR}'/></clipPath>"]
    s.append(f"<circle cx='{CX}' cy='{CY}' r='{MR + 40}' fill='url(#atm)'/>")
    s.append(f"<circle cx='{CX}' cy='{CY}' r='{MR}' fill='#e0693d'/>")
    s.append("<g clip-path='url(#mc)'>")
    for px, py, rx, ry in PATCHES:
        xx = (px + spin + 350) % 700 - 350
        s.append(f"<ellipse cx='{CX + xx:.0f}' cy='{CY + py}' rx='{rx}' ry='{ry}' fill='#b94c2c' opacity='0.85'/>")
    s.append(f"<ellipse cx='{CX}' cy='{CY - MR + 18}' rx='120' ry='42' fill='#fff6ee'/>")
    s.append(f"<path d='M{CX - 150} {CY + 60} Q{CX} {CY + 80} {CX + 170} {CY + 50}' fill='none' stroke='#a8432a' stroke-width='10' stroke-linecap='round'/>")
    s.append(f"<circle cx='{CX + 90}' cy='{CY + 100}' r='190' fill='none' stroke='#8a321e' stroke-width='0'/>")
    s.append(f"<circle cx='{CX + 120}' cy='{CY + 90}' r='{MR + 40}' fill='#7a2a18' opacity='0.28' transform='translate(60,40)'/>")
    s.append("</g>")
    s.append(f"<path d='M{CX - 210} {CY - 120} A {MR - 40} {MR - 40} 0 0 1 {CX - 60} {CY - 245}' fill='none' stroke='#ffb48a' stroke-width='14' stroke-linecap='round' opacity='0.8'/>")
    s.append(f"<circle cx='{CX}' cy='{CY}' r='{MR}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # cara: los ojos siguen a Fobos
    dx, dy = ox - CX, oy - (CY - 70); d = math.hypot(dx, dy) or 1
    lx, ly = 13 * dx / d, 9 * dy / d
    er = 42 + 10 * rev
    for ex in (-85, 85):
        s.append(f"<ellipse cx='{CX + ex}' cy='{CY - 70}' rx='{er:.1f}' ry='{er * 1.12:.1f}' fill='#fff' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<g transform='translate({CX + ex + lx:.1f},{CY - 70 + ly:.1f}) scale(1,{blink})'>"
                 f"<circle r='21' fill='{INK}'/><circle cx='-7' cy='-8' r='7' fill='#fff'/></g>")
    for ex in (-150, 150):
        s.append(f"<ellipse cx='{CX + ex}' cy='{CY + 5}' rx='26' ry='14' fill='#ff8f8f' opacity='0.6'/>")
    if rev < 0.5:
        s.append(f"<path d='M{CX - 40} {CY + 10} Q{CX} {CY + 40} {CX + 40} {CY + 10}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    else:
        s.append(f"<ellipse cx='{CX}' cy='{CY + 25}' rx='26' ry='32' fill='#5a1e14' stroke='{INK}' stroke-width='7'/>")
    return "".join(s)


def frame(t):
    rev = seg(t, 7.2, 7.5)
    form = seg(t, 7.2, 8.1)                # los trozos se reparten en el anillo
    flash = clamp(1 - (t - 7.2) / 0.8) if t >= 7.2 else 0
    rx, ry = orbita(t)
    th = theta(t)
    ox, oy = CX + rx * math.cos(th), CY + ry * math.sin(th)
    front = math.sin(th) > 0
    depth = 1.35 + 0.25 * (math.sin(th) + 1) / 2
    rot = 12 * math.sin(t * 1.7)
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920' viewBox='0 0 1080 1920'><defs>",
         "<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0d0b2a'/>"
         f"<stop offset='0.55' stop-color='#1f1650'/><stop offset='1' stop-color='{mix('#3a1d4f', '#5a2a4a', rev)}'/></linearGradient>",
         "<radialGradient id='neb' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#7a4fd0' stop-opacity='0.35'/><stop offset='1' stop-color='#7a4fd0' stop-opacity='0'/></radialGradient>",
         "<radialGradient id='atm'><stop offset='0.84' stop-color='#ff9a5a' stop-opacity='0.55'/><stop offset='1' stop-color='#ff9a5a' stop-opacity='0'/></radialGradient>",
         "<radialGradient id='fl'><stop offset='0' stop-color='#fffbe6' stop-opacity='1'/><stop offset='0.4' stop-color='#ffd27a' stop-opacity='0.8'/><stop offset='1' stop-color='#ff7a3d' stop-opacity='0'/></radialGradient>",
         "</defs>",
         "<rect width='1080' height='1920' fill='url(#sky)'/>",
         "<ellipse cx='820' cy='520' rx='420' ry='260' fill='url(#neb)'/>",
         "<ellipse cx='180' cy='1050' rx='360' ry='220' fill='url(#neb)'/>"]
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.6 + ph * 3))
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # Sol lejano (abajo a la izquierda, ilumina a Marte)
    z = 1 + 0.12 * seg(t, 7.2, 9.6)
    cam = []
    # Deimos, la otra luna, pequeña y lejana
    dx_ = 900 - 40 * math.sin(t * 0.5); dy_ = 1110 + 12 * math.sin(t * 0.9)
    cam.append(f"<g transform='translate({dx_:.0f},{dy_:.0f}) rotate({t*8:.0f})'><path d='M-24 -4 Q-20 -18 0 -18 Q22 -18 24 0 Q22 16 0 16 Q-22 16 -24 -4 Z' fill='#8f857c' stroke='{INK}' stroke-width='5'/>"
               f"<circle cx='-6' cy='2' r='5' fill='#6f665e'/></g>")
    # órbita (línea discontinua) que se encoge, solo antes de romperse
    oop = 0.55 * (1 - rev)
    back_orb = f"M{CX - rx:.0f} {CY} A {rx:.0f} {ry:.0f} 0 0 1 {CX + rx:.0f} {CY}"
    front_orb = f"M{CX + rx:.0f} {CY} A {rx:.0f} {ry:.0f} 0 0 1 {CX - rx:.0f} {CY}"
    if oop > 0.01:
        cam.append(f"<path d='{back_orb}' fill='none' stroke='#cfc2ff' stroke-width='5' stroke-dasharray='18 16' opacity='{oop:.2f}'/>")
    # anillo (mitad de atrás)
    R, Rr = 430, 430 * 0.27
    ring_op = 0.75 * form
    if ring_op > 0.01:
        cam.append(f"<path d='M{CX - R} {CY} A {R} {Rr:.0f} 0 0 1 {CX + R} {CY}' fill='none' stroke='#c7a58a' stroke-width='30' opacity='{ring_op * 0.6:.2f}'/>")
    frags_back, frags_front = [], []
    if t >= 7.2:
        k = form
        spin = 0.35 * (t - 7.2)
        for i, (ph, rr, sz, bx, by, fr) in enumerate(FRAG):
            a = ph + spin
            tx, ty = CX + R * rr * math.cos(a), CY + Rr * rr * math.sin(a)
            bulge = math.sin(math.pi * k)
            px = lerp(ox, tx, ease(k)) + 220 * bx * bulge
            py = lerp(oy, ty, ease(k)) + 160 * by * bulge
            col = ["#a39686", "#8f8377", "#b5a898", "#7d7268"][i % 4]
            el = (f"<g transform='translate({px:.1f},{py:.1f}) rotate({fr + t * 90 * (1 if i % 2 else -1):.0f})'>"
                  f"<path d='M{-sz} {-sz*0.3:.1f} L{-sz*0.3:.1f} {-sz} L{sz} {-sz*0.4:.1f} L{sz*0.6:.1f} {sz*0.8:.1f} L{-sz*0.7:.1f} {sz*0.7:.1f} Z' "
                  f"fill='{col}' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/></g>")
            (frags_front if (k < 0.75 or math.sin(a) > 0) else frags_back).append(el)
    cam += frags_back
    if t < 7.2 and not front:
        cam.append(phobos(ox, oy, t, depth, rot))
    cam.append(marte(t, ox, oy))
    if ring_op > 0.01:
        cam.append(f"<path d='M{CX + R} {CY} A {R} {Rr:.0f} 0 0 1 {CX - R} {CY}' fill='none' stroke='#d9b89a' stroke-width='30' opacity='{ring_op * 0.75:.2f}'/>")
        cam.append(f"<path d='M{CX + R} {CY} A {R} {Rr:.0f} 0 0 1 {CX - R} {CY}' fill='none' stroke='#fff1dc' stroke-width='5' opacity='{ring_op * 0.6:.2f}'/>")
    if oop > 0.01:
        cam.append(f"<path d='{front_orb}' fill='none' stroke='#cfc2ff' stroke-width='5' stroke-dasharray='18 16' opacity='{oop:.2f}'/>")
    if t < 7.2 and front:
        # polvo que se suelta en la tensión
        tens = seg(t, 5.0, 7.0)
        for i, (ux, uy, rr_) in enumerate(DUSTP):
            if tens > 0.05:
                q = ((t * 1.3 + i * 0.13) % 1.0)
                cam.append(f"<circle cx='{ox + ux * 90 * (0.6 + q):.0f}' cy='{oy + uy * 70 * (0.6 + q):.0f}' r='{rr_:.1f}' fill='#c9bfb2' opacity='{tens * (1 - q):.2f}'/>")
        cam.append(phobos(ox, oy, t, depth, rot))
    cam += frags_front
    if flash > 0:
        cam.append(f"<circle cx='{ox:.0f}' cy='{oy:.0f}' r='{lerp(60, 420, 1 - flash):.0f}' fill='url(#fl)' opacity='{flash:.2f}'/>")
    s.append(zoom(CX, CY, z, "".join(cam)))
    if flash > 0.6:
        s.append(f"<rect width='1080' height='1920' fill='#fff4dc' opacity='{(flash - 0.6) * 0.9:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
