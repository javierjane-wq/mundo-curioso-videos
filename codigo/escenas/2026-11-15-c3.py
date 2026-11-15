"""2026-11-15-c3 · La Luna siempre nos enseña la misma cara: gira sobre sí misma en ~27 días,
lo mismo que tarda en dar la vuelta a la Tierra (rotación síncrona).

Vista desde arriba: la Tierra en el centro de la mitad de abajo y una Luna original con cara
que la orbita mirándola siempre. En la revelación se ve la Luna en cuatro puntos de la órbita,
siempre con la cara hacia la Tierra, la órbita se enciende en dorado y la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.5
MUSICA = 4

EX, EY = 540, 1450          # centro de la Tierra
ER = 150                    # radio de la Tierra
R_ORB = 330                 # radio de la órbita
MR = 95                     # radio de la Luna

rng = np.random.default_rng(15)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(110)]
CRATERS = [(-38, -40, 17), (26, -52, 12), (46, -14, 9), (-8, -22, 8), (-55, -6, 10), (10, -70, 7)]
CONT = [  # continentes (en coordenadas de la Tierra, giran con ella)
    "M-60 -110 Q-10 -130 30 -100 Q50 -70 20 -50 Q-20 -40 -40 -60 Q-80 -70 -60 -110 Z",
    "M40 -10 Q90 -30 110 10 Q120 60 80 80 Q50 90 40 50 Q20 20 40 -10 Z",
    "M-120 10 Q-80 0 -70 40 Q-60 90 -100 100 Q-130 80 -135 40 Z",
    "M-30 90 Q0 80 20 110 Q0 140 -30 130 Z",
]


_TS = np.linspace(0, DUR, 2001)
_F = np.array([lerp(1.0, 0.12, seg(u, 7.3, 8.6)) for u in _TS])
_P = np.concatenate([[0], np.cumsum((_F[1:] + _F[:-1]) / 2 * np.diff(_TS))])
_P85 = float(np.interp(8.5, _TS, _P))
_W0 = -(0.25 + 2 * math.pi + math.pi / 2) / _P85   # sentido antihorario visto desde el norte


def ang_luna(t):
    """Ángulo de la Luna: entra por la derecha (t=0) y está arriba (-90°) en t=8.5."""
    return -math.pi / 2 + _W0 * (float(np.interp(t, _TS, _P)) - _P85)


def pos_luna(t):
    r = lerp(560, R_ORB, seg(t, 0, 1.9))
    a = ang_luna(t)
    return EX + r * math.cos(a), EY + r * math.sin(a)


def luna(mx, my, t, escala=1.0, opac=1.0, oro=0.0, cara=True):
    """Luna original: cara (lado visible) mirando a la Tierra, cara oculta más oscura con cráteres."""
    rot = math.degrees(math.atan2(EY - my, EX - mx)) - 90  # el 'abajo' local apunta a la Tierra
    blink = 0.12 if (t % 2.7) < 0.13 else 1.0
    base = mix("#e9e6dc", "#ffe9a8", oro)
    lejos = mix("#8f8ca6", "#d9a85a", oro)
    g = [f"<g transform='translate({mx:.1f},{my:.1f}) rotate({rot:.1f}) scale({escala:.3f})' opacity='{opac:.2f}'>"]
    g.append(f"<clipPath id='cl{int(mx)}{int(my)}'><circle r='{MR}'/></clipPath>")
    g.append(f"<circle r='{MR}' fill='{base}'/>")
    # mitad lejana (cara oculta), más oscura
    g.append(f"<g clip-path='url(#cl{int(mx)}{int(my)})'><rect x='-{MR}' y='-{MR}' width='{2*MR}' height='{MR}' fill='{lejos}'/>"
             + "".join(f"<circle cx='{cx}' cy='{cy}' r='{cr}' fill='{mix('#8c8a9c', '#c9a35a', oro)}' stroke='{INK}' stroke-width='4'/>" for cx, cy, cr in CRATERS)
             + "</g>")
    g.append(f"<circle r='{MR}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    if cara:
        # cara mirando a la Tierra (abajo local)
        for ex in (-25, 25):
            g.append(f"<g transform='translate({ex},18) scale(1,{blink})'><ellipse rx='13' ry='15' fill='{INK}'/>"
                     f"<circle cx='4' cy='-6' r='5' fill='#fff'/></g>")
        g.append(f"<ellipse cx='-48' cy='38' rx='11' ry='7' fill='#ff9aa8' opacity='0.8'/><ellipse cx='48' cy='38' rx='11' ry='7' fill='#ff9aa8' opacity='0.8'/>")
        g.append(f"<path d='M-16 44 Q0 60 16 44' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def tierra(t, brillo):
    giro = -t * 14
    g = [f"<circle cx='{EX}' cy='{EY}' r='{ER + 40}' fill='url(#atm)'/>",
         f"<clipPath id='ctierra'><circle cx='{EX}' cy='{EY}' r='{ER}'/></clipPath>",
         f"<circle cx='{EX}' cy='{EY}' r='{ER}' fill='{mix('#2f8fe8', '#4fb0ff', brillo)}'/>",
         f"<g clip-path='url(#ctierra)'><g transform='translate({EX},{EY}) rotate({giro:.1f})'>"]
    for d in CONT:
        g.append(f"<path d='{d}' fill='{mix('#4fc26a', '#6be08a', brillo)}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    g.append("</g>")
    # nubes que se mueven más rápido que los continentes
    for i, (cx, cy, s) in enumerate([(-90, -30, 1.0), (60, -90, 0.8), (20, 70, 0.9)]):
        dx = ((t * 22 + i * 90) % 360) - 180
        g.append(f"<g transform='translate({EX + cx + dx:.0f},{EY + cy}) scale({s})'>"
                 f"<path d='M-40 8 Q-30 -14 -6 -6 Q8 -22 28 -8 Q46 -4 40 10 Z' fill='#fff' opacity='0.9'/></g>")
    g.append("</g>")
    # sombra de la noche (el Sol ilumina desde la izquierda)
    g.append(f"<path d='M{EX} {EY - ER} A{ER} {ER} 0 0 1 {EX} {EY + ER} A{ER*0.35:.0f} {ER} 0 0 0 {EX} {EY - ER} Z' fill='#0b1240' opacity='0.28'/>")
    g.append(f"<circle cx='{EX}' cy='{EY}' r='{ER}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    return "".join(g)


def flecha_giro(mx, my, t, k):
    """Flecha circular alrededor de la Luna: 'también gira sobre sí misma'."""
    if k <= 0.01:
        return ""
    r = MR + 34
    a0 = math.degrees(ang_luna(t)) + 40
    p = []
    for i in range(0, 241, 8):
        a = math.radians(a0 + i)
        p.append(f"{mx + r*math.cos(a):.1f},{my + r*math.sin(a):.1f}")
    a = math.radians(a0 + 240)
    hx, hy = mx + r * math.cos(a), my + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)   # tangente (sentido del giro)
    nx, ny = math.cos(a), math.sin(a)
    tip = f"{hx + tx*30:.1f},{hy + ty*30:.1f} {hx + nx*20:.1f},{hy + ny*20:.1f} {hx - nx*20:.1f},{hy - ny*20:.1f}"
    return (f"<g opacity='{k:.2f}'><polyline points='{' '.join(p)}' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
            f"<polyline points='{' '.join(p)}' fill='none' stroke='#ffd23f' stroke-width='8' stroke-linecap='round'/>"
            f"<polygon points='{tip}' fill='#ffd23f' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/></g>")


def frame(t):
    rev = seg(t, 7.5, 8.3)
    ten = seg(t, 5.0, 5.7) * (1 - seg(t, 7.4, 7.8))
    top = mix("#0a0f33", "#1a1450", rev); mid = mix("#1b1752", "#3a2370", rev); low = mix("#2a1c5e", "#5a2f7e", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='atm'><stop offset='0.75' stop-color='#7fd0ff' stop-opacity='0.55'/><stop offset='1' stop-color='#7fd0ff' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sol'><stop offset='0' stop-color='#fff1b0' stop-opacity='0.55'/><stop offset='0.4' stop-color='#ffd23f' stop-opacity='0.25'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='neb'><stop offset='0' stop-color='#b06cff' stop-opacity='0.35'/><stop offset='1' stop-color='#b06cff' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='oro'><stop offset='0' stop-color='#fff2b0' stop-opacity='{0.9*rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffcf4a' stop-opacity='{0.45*rev:.3f}'/><stop offset='1' stop-color='#ff9f1c' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # nebulosa tranquila arriba y abajo
    s.append(f"<ellipse cx='{820 + 20*math.sin(t*0.6):.0f}' cy='520' rx='420' ry='260' fill='url(#neb)'/>")
    s.append(f"<ellipse cx='200' cy='1750' rx='380' ry='240' fill='url(#neb)'/>")
    # estrellas que titilan
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 2.6 + ph * 3)
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # estrella fugaz
    k = seg(t, 2.6, 3.6)
    if 0 < k < 1:
        x0, y0 = lerp(1150, 420, k), lerp(160, 560, k)
        s.append(f"<line x1='{x0:.0f}' y1='{y0:.0f}' x2='{x0 + 170:.0f}' y2='{y0 - 92:.0f}' stroke='#fff' stroke-width='6' stroke-linecap='round' opacity='{(1-k)*0.9:.2f}'/>"
                 f"<circle cx='{x0:.0f}' cy='{y0:.0f}' r='8' fill='#fff' opacity='{(1-k):.2f}'/>")
    # Sol lejano a la izquierda (fuera del encuadre): rayos suaves
    s.append(f"<circle cx='-60' cy='1450' r='{330 + 15*math.sin(t*2):.0f}' fill='url(#sol)'/>")
    # planeta anillado lejano
    py = 1075 + 8 * math.sin(t * 1.3)
    s.append(f"<g transform='translate(965,{py:.1f}) rotate(-18) scale(0.85)'>"
             f"<ellipse rx='78' ry='20' fill='none' stroke='{INK}' stroke-width='12'/><ellipse rx='78' ry='20' fill='none' stroke='#ffb36b' stroke-width='6'/>"
             f"<circle r='40' fill='#ff7a8a' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M-78 0 A78 20 0 0 0 78 0' fill='none' stroke='{INK}' stroke-width='12'/><path d='M-78 0 A78 20 0 0 0 78 0' fill='none' stroke='#ffb36b' stroke-width='6'/></g>")

    z = 1 + 0.08 * seg(t, 7.5, 10)
    esc = [f"<circle cx='{EX}' cy='{EY}' r='{R_ORB + 120}' fill='url(#oro)'/>"]
    # órbita: discontinua y tenue; dorada y brillante en la revelación
    oc = mix("#8f9be8", "#ffd23f", rev); ow = lerp(5, 12, rev)
    dash = lerp(18, 0.1, rev); off = -t * 40
    esc.append(f"<circle cx='{EX}' cy='{EY}' r='{R_ORB}' fill='none' stroke='{oc}' stroke-width='{ow:.1f}' "
               f"stroke-dasharray='{dash:.1f} {lerp(22, 0.1, rev):.1f}' stroke-dashoffset='{off:.0f}' opacity='{lerp(0.6, 1, rev):.2f}'/>")
    esc.append(tierra(t, rev))
    # revelación: la Luna en cuatro puntos de la órbita, siempre mirando a la Tierra
    if rev > 0:
        for i, a in enumerate((0, math.pi / 2, math.pi)):
            gk = seg(t, 7.5 + 0.18 * i, 8.1 + 0.18 * i)
            gx, gy = EX + R_ORB * math.cos(a), EY + R_ORB * math.sin(a)
            esc.append(luna(gx, gy, t + i * 0.7, escala=0.82 * rebote(t, 7.5 + 0.18 * i, 0.5) if gk < 1 else 0.82,
                            opac=0.85 * gk, oro=0.25))
    mx, my = pos_luna(t)
    esc.append(f"<circle cx='{mx:.0f}' cy='{my:.0f}' r='{MR + 60}' fill='url(#oro)'/>")
    esc.append(flecha_giro(mx, my, t, ten))
    puls = 1 + 0.05 * math.sin(t * 9) * ten + 0.12 * (rebote(t, 7.5, 0.6) - (1 if t >= 7.5 else 0)) * (t < 8.1)
    esc.append(luna(mx, my, t, escala=puls, oro=rev))
    # brillitos en la revelación
    if rev > 0:
        for i in range(10):
            a = i * 0.628 + t * 0.8
            rr = lerp(MR, MR + 120, ((t - 7.5) * 0.9 + i * 0.1) % 1)
            s_ = 6 + 3 * math.sin(t * 6 + i)
            esc.append(f"<circle cx='{mx + rr*math.cos(a):.0f}' cy='{my + rr*math.sin(a):.0f}' r='{s_:.1f}' fill='#fff6c8' opacity='{rev*0.9:.2f}'/>")
    s.append(f"<g transform='translate({EX},{EY}) scale({z:.4f}) translate({-EX},{-EY})'>{''.join(esc)}</g>")
    s.append("</svg>")
    return "".join(s)
