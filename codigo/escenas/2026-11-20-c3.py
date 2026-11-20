"""2026-11-20-c3 · Cuerpo humano: la pupila mide unos 2-4 mm con luz y en la oscuridad se abre hasta unos 8 mm.

Un niño original asoma de la cama bajo una lámpara de techo encendida: sus pupilas son puntitos dentro
del iris verde. La lámpara se apaga, la habitación se vuelve azul noche, el niño se sorprende y sus
pupilas empiezan a crecer. En la REVELACION la cámara se acerca a los ojos, las pupilas quedan enormes
y un halo de luz de luna entra en ellas.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 7.4    # pupilas enormes + halo + zoom: golpe musical
MUSICA = 6

rng = np.random.default_rng(31)
MOTAS = [(rng.uniform(250, 830), rng.uniform(320, 1050), rng.uniform(3, 7), rng.uniform(0, 6.28)) for _ in range(26)]
ESTRELLAS = [(rng.uniform(40, W - 40), rng.uniform(260, 1000), rng.uniform(5, 11), rng.uniform(0, 6.28)) for _ in range(22)]
CHISPAS = [(rng.uniform(0, 6.28), rng.uniform(150, 260), rng.uniform(0, 1)) for _ in range(16)]

APAGA = 5.3          # la lámpara se apaga
CX, EY = 540, 1395   # centro de la cara / altura de los ojos
EX = 150             # separación de cada ojo respecto al centro


def estrella(x, y, r, col, op):
    p = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        p.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return f"<polygon points='{' '.join(p)}' fill='{col}' opacity='{op:.2f}'/>"


def ojo(x, y, t, osc, pupila, mira):
    """Ojo grande: blanco, iris verde con rayitas, pupila negra (tamaño variable) y brillos."""
    blink = 0.1 if (t % 3.4) < 0.13 and t < 7.0 else 1.0
    rx, ry = 112, 122 * blink
    blanco = mix("#ffffff", "#c9d6f2", osc * 0.6)
    g = [f"<ellipse cx='{x}' cy='{y}' rx='{rx}' ry='{ry:.1f}' fill='{blanco}' stroke='{INK}' stroke-width='{LW}'/>"]
    if blink > 0.5:
        ix, iy = x + mira[0], y + mira[1]
        g.append(f"<clipPath id='c{x}'><ellipse cx='{x}' cy='{y}' rx='{rx - 4}' ry='{ry - 4:.1f}'/></clipPath>")
        g.append(f"<g clip-path='url(#c{x})'>")
        ir = 74
        g.append(f"<circle cx='{ix:.1f}' cy='{iy:.1f}' r='{ir}' fill='{mix('#3fae6a', '#2f7d6a', osc)}' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<circle cx='{ix:.1f}' cy='{iy:.1f}' r='{ir * 0.72:.1f}' fill='{mix('#8fd36a', '#5fae84', osc)}' opacity='0.55'/>")
        for k in range(18):
            a = k * math.pi / 9
            r0 = pupila + 4
            g.append(f"<line x1='{ix + r0 * math.cos(a):.1f}' y1='{iy + r0 * math.sin(a):.1f}' x2='{ix + (ir - 8) * math.cos(a):.1f}' y2='{iy + (ir - 8) * math.sin(a):.1f}' stroke='#1f6a45' stroke-width='4' opacity='0.55'/>")
        g.append(f"<circle cx='{ix:.1f}' cy='{iy:.1f}' r='{pupila:.1f}' fill='#120c0a'/>")
        g.append(f"<circle cx='{ix - ir * 0.36:.1f}' cy='{iy - ir * 0.38:.1f}' r='17' fill='#fff' opacity='0.95'/>")
        g.append(f"<circle cx='{ix + ir * 0.3:.1f}' cy='{iy + ir * 0.34:.1f}' r='8' fill='#fff' opacity='0.8'/>")
        g.append("</g>")
        g.append(f"<ellipse cx='{x}' cy='{y}' rx='{rx}' ry='{ry:.1f}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    else:
        g.append(f"<path d='M{x - rx} {y} Q{x} {y + 30} {x + rx} {y}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linecap='round'/>")
    # pestañas
    for k, a in enumerate((-150, -125, -100)):
        sg = 1 if x > CX else -1
        aa = math.radians(a if sg < 0 else -180 - a)
        bx, by = x + rx * 0.95 * math.cos(aa), y + ry * 0.95 * math.sin(aa)
        g.append(f"<line x1='{bx:.1f}' y1='{by:.1f}' x2='{bx + 26 * math.cos(aa):.1f}' y2='{by + 26 * math.sin(aa) - 4:.1f}' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    return "".join(g)


def nino(t, osc, pupila, sorpresa):
    """Niño original asomando de la cama: cara redonda, pelo castaño con mechón, orejas y pijama."""
    sube = lerp(420, 0, ease(seg(t, 0, 1.4))) + (8 * math.sin(math.pi * clamp((t - 1.4) / 0.4)) if t > 1.4 else 0)
    resp = 4 * math.sin(t * 2.4)
    piel = mix("#ffc9a0", "#9c8fb6", osc * 0.75)
    piel_s = mix("#f0a77c", "#7f739c", osc * 0.75)
    pelo = mix("#8a4a22", "#3e2c46", osc * 0.7)
    mir = (lerp(-14, 14, 0.5 + 0.5 * math.sin(t * 1.3)) if t < APAGA else lerp(0, 0, 1), 6 * math.sin(t * 0.9) if t < APAGA else -4)
    g = [f"<g transform='translate(0,{sube + resp:.1f})'>"]
    # pijama (cuello y hombros, se ven al incorporarse)
    pij = mix('#4fb3a9', '#2f5f78', osc * 0.8)
    g.append(f"<path d='M{CX - 380} {EY + 700} Q{CX - 390} {EY + 330} {CX} {EY + 300} Q{CX + 390} {EY + 330} {CX + 380} {EY + 700} Z' fill='{pij}' stroke='{INK}' stroke-width='{LW}'/>")
    for k in range(-2, 3):
        g.append(f"<line x1='{CX + k * 130}' y1='{EY + 330}' x2='{CX + k * 150}' y2='{EY + 700}' stroke='#ffffff' stroke-width='14' opacity='0.35'/>")
    # orejas
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{CX + sx * 330}' cy='{EY + 40}' rx='58' ry='78' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<ellipse cx='{CX + sx * 332}' cy='{EY + 42}' rx='26' ry='42' fill='{piel_s}'/>")
    # cabeza
    g.append(f"<ellipse cx='{CX}' cy='{EY + 40}' rx='335' ry='330' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo con mechón que se balancea
    mech = 10 * math.sin(t * 3.2)
    g.append(f"<path d='M{CX - 330} {EY - 10} Q{CX - 340} {EY - 300} {CX} {EY - 300} Q{CX + 340} {EY - 300} {CX + 330} {EY - 10} "
             f"Q{CX + 270} {EY - 160} {CX + 150} {EY - 180} Q{CX + 60} {EY - 130} {CX - 20} {EY - 190} Q{CX - 130} {EY - 140} {CX - 220} {EY - 170} Q{CX - 300} {EY - 120} {CX - 330} {EY - 10} Z' "
             f"fill='{pelo}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<g transform='rotate({mech:.1f},{CX + 10},{EY - 290})'><path d='M{CX - 10} {EY - 288} Q{CX - 30} {EY - 330} {CX + 45} {EY - 335} Q{CX + 15} {EY - 315} {CX + 40} {EY - 292} Z' fill='{pelo}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # cejas (suben con la sorpresa)
    for sx in (-1, 1):
        y0 = EY - 150 - 30 * sorpresa
        g.append(f"<path d='M{CX + sx * (EX - 70)} {y0 + 6:.1f} Q{CX + sx * EX} {y0 - 22:.1f} {CX + sx * (EX + 70)} {y0 + 8:.1f}' fill='none' stroke='{pelo}' stroke-width='18' stroke-linecap='round'/>")
    # ojos
    for sx in (-1, 1):
        g.append(ojo(CX + sx * EX, EY, t, osc, pupila, mir))
    # nariz y mejillas
    g.append(f"<path d='M{CX - 18} {EY + 120} Q{CX} {EY + 145} {CX + 18} {EY + 120}' fill='none' stroke='{piel_s}' stroke-width='10' stroke-linecap='round'/>")
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{CX + sx * 225}' cy='{EY + 150}' rx='48' ry='26' fill='#ff8f9c' opacity='{lerp(0.55, 0.3, osc):.2f}'/>")
    # boca: sonrisa -> "o" de sorpresa
    if sorpresa < 0.5:
        g.append(f"<path d='M{CX - 70} {EY + 200} Q{CX} {EY + 255} {CX + 70} {EY + 200}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round'/>")
    else:
        rr = 22 + 8 * sorpresa
        g.append(f"<ellipse cx='{CX}' cy='{EY + 220}' rx='{rr * 0.8:.1f}' ry='{rr:.1f}' fill='#a3283c' stroke='{INK}' stroke-width='8'/>")
    g.append("</g>")
    return "".join(g)


def frame(t):
    osc = seg(t, APAGA, APAGA + 0.35)                  # 0 = luz encendida, 1 = a oscuras
    pupila = lerp(19, 33, seg(t, APAGA + 0.4, 7.3)) + 18 * seg(t, 7.3, 7.9)   # crece hasta ~51 (8 mm)
    sorpresa = seg(t, APAGA + 0.3, APAGA + 0.7)
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.6)
    z = 1 + 0.10 * ease(seg(t, REVELACION - 0.2, 8.3))
    alza = -130 * ease(seg(t, REVELACION - 0.25, 8.0))   # se incorpora: ojos por encima del cierre
    # pared: amarillo cálido -> azul noche
    top = mix("#ffe9a8", "#1d2550", osc); low = mix("#ffd27a", "#2c3670", osc)
    defs = (f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='luz'><stop offset='0' stop-color='#fff6c8' stop-opacity='{0.85 * (1 - osc):.3f}'/><stop offset='1' stop-color='#ffd36a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='luna'><stop offset='0' stop-color='#bfe3ff' stop-opacity='{0.75 * rev:.3f}'/><stop offset='0.55' stop-color='#6fa8ff' stop-opacity='{0.35 * rev:.3f}'/><stop offset='1' stop-color='#3a5bd0' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#pared)'/>"]
    # papel pintado de estrellitas (se encienden un poco en la oscuridad)
    for x, y, r, ph in ESTRELLAS:
        col = mix("#ffc24a", "#fff1a8", osc)
        op = lerp(0.35, 0.55 + 0.4 * math.sin(t * 2 + ph), osc)
        s.append(estrella(x, y, r, col, op))
    # rodapié de cabecero de cama
    cab = mix("#6fb7e8", "#2d4f80", osc)
    s.append(f"<rect x='40' y='1020' width='1000' height='520' rx='60' fill='{cab}' stroke='{INK}' stroke-width='{LW}'/>")
    for bx in (210, 400, 680, 870):
        s.append(f"<rect x='{bx}' y='1080' width='26' height='420' rx='12' fill='{mix('#9fd0f2', '#3d6698', osc)}' stroke='{INK}' stroke-width='6'/>")
    # lámpara de techo (se balancea)
    sw = 4 * math.sin(t * 1.7) * (1 - 0.6 * osc)
    s.append(f"<circle cx='540' cy='175' r='330' fill='url(#luz)'/>")
    s.append(f"<g transform='rotate({sw:.2f},540,0)'>"
             f"<line x1='540' y1='0' x2='540' y2='120' stroke='{INK}' stroke-width='8'/>"
             f"<path d='M455 200 L480 120 L600 120 L625 200 Z' fill='{mix('#ff7a59', '#7a3a4a', osc)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
             f"<circle cx='540' cy='218' r='26' fill='{mix('#fff8d0', '#59607a', osc)}' stroke='{INK}' stroke-width='6'/></g>")
    # motas de polvo bailando en la luz
    for x, y, r, ph in MOTAS:
        yy = y + 30 * math.sin(t * 0.8 + ph); xx = x + 20 * math.sin(t * 0.6 + ph * 2)
        s.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#fff7d8' opacity='{0.6 * (1 - osc):.2f}'/>")
    # escena con zoom: halo de luna, niño, almohada y manta
    e = []
    e.append(f"<ellipse cx='{CX}' cy='1760' rx='470' ry='120' fill='{mix('#ffffff', '#8d97c8', osc)}' stroke='{INK}' stroke-width='{LW}'/>")
    e.append(f"<g transform='translate(0,{alza:.1f})'>")
    e.append(f"<ellipse cx='{CX}' cy='{EY}' rx='{lerp(200, 520, rev):.0f}' ry='{lerp(140, 330, rev):.0f}' fill='url(#luna)'/>")
    e.append(nino(t, osc, pupila, sorpresa))
    # anillos y chispas de luz entrando en las pupilas
    if rev > 0:
        for sx in (-1, 1):
            px = CX + sx * EX
            for k in range(3):
                fase = ((t - REVELACION) * 0.9 + k / 3) % 1
                rr = lerp(190, 60, fase)
                e.append(f"<circle cx='{px}' cy='{EY}' r='{rr:.1f}' fill='none' stroke='#cfe9ff' stroke-width='6' opacity='{0.7 * rev * math.sin(math.pi * fase):.2f}'/>")
            for a, d, ph in CHISPAS:
                fase = ((t - REVELACION) * 0.7 + ph) % 1
                dd = lerp(d, 70, fase)
                e.append(estrella(px + dd * math.cos(a), EY + dd * math.sin(a), 11 * (1 - fase) + 3, '#ffffff', 0.9 * rev))
    e.append('</g>')
    # manta con estampado (tapa la barbilla y los hombros)
    manta = mix("#ff8a5c", "#7a4a7a", osc)
    e.append(f"<path d='M-20 1700 Q270 1640 540 1690 Q810 1640 1100 1700 L1100 1940 L-20 1940 Z' fill='{manta}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for bx in range(60, 1080, 150):
        e.append(f"<circle cx='{bx}' cy='{1800 + 30 * ((bx // 150) % 2)}' r='20' fill='{mix('#ffd166', '#b58ab0', osc)}' stroke='{INK}' stroke-width='5'/>")
    e.append(f"<path d='M-20 1700 Q270 1640 540 1690 Q810 1640 1100 1700' fill='none' stroke='{mix('#fff1e0', '#c7b3d6', osc)}' stroke-width='22' stroke-linecap='round' opacity='0.9'/>")
    s.append(zoom(CX, EY, z, "".join(e)))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
