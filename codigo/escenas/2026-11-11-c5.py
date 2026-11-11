"""Los anillos de Saturno: enormes (hasta 282.000 km) pero de unos 10 m de grosor típico.

Saturno (personaje original con cara) sube desde abajo con los anillos abiertos; los anillos giran,
una luna da vueltas y las estrellas titilan. A partir de 4,9 s el planeta se inclina hasta ver los
anillos de canto y en la REVELACION se quedan en una línea finísima que brilla (zoom de cámara).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.45   # los anillos quedan de canto: una línea finísima
MUSICA = 7

CX, CY = 540, 1430
R = 215            # radio del planeta
BANDAS = [         # (radio interior, radio exterior, color)
    (262, 300, "#b89a74"),   # anillo C
    (304, 392, "#f6e3b4"),   # anillo B
    (404, 470, "#d9b884"),   # anillo A
]

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1920), rng.uniform(2, 5.5), rng.uniform(0, 6.28)) for _ in range(95)]
PART = [(rng.uniform(270, 465), rng.uniform(0, 6.283), rng.uniform(3, 6)) for _ in range(46)]
DUST = [(rng.uniform(0, W), rng.uniform(1000, 1920), rng.uniform(2, 4), rng.uniform(15, 40)) for _ in range(26)]


def elipse(rx, ry):
    ry = max(ry, 0.6)
    return f"M{-rx:.1f} 0 a{rx:.1f} {ry:.2f} 0 1 0 {2*rx:.1f} 0 a{rx:.1f} {ry:.2f} 0 1 0 {-2*rx:.1f} 0 Z"


def anillos(sb, t, glow, mitad):
    """Dibuja los anillos (proyección: y = r·sin(a)·sb). mitad = 'atras' o 'delante'."""
    clip = "clipA" if mitad == "atras" else "clipD"
    g = [f"<g clip-path='url(#{clip})'>"]
    edge = clamp(1 - sb / 0.05)            # 1 cuando están de canto
    for ri, ro, col in BANDAS:
        c = mix(col, "#fff6c8", glow)
        g.append(f"<path d='{elipse(ro, ro*sb)} {elipse(ri, ri*sb)}' fill='{c}' fill-rule='evenodd' "
                 f"stroke='{INK}' stroke-width='{lerp(5, 3, edge):.1f}'/>")
    # partículas de hielo que giran
    for r, a0, pr in PART:
        a = a0 + t * (0.9 * 300 / r)
        y = r * math.sin(a) * sb
        if (mitad == "delante") == (math.sin(a) > 0):
            g.append(f"<circle cx='{r*math.cos(a):.1f}' cy='{y:.1f}' r='{pr*lerp(1, 0.5, edge):.1f}' fill='#fffaf0' opacity='0.85'/>")
    # borde exterior grueso
    g.append(f"<path d='{elipse(470, 470*sb)}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    g.append("</g>")
    return "".join(g)


def planeta(t, rev):
    blink = 0.12 if ((t + 1.2) % 2.9) < 0.13 or abs(t - 6.2) < 0.07 else 1.0
    g = [f"<g clip-path='url(#clipP)'>",
         f"<circle r='{R}' fill='#f0c06a'/>"]
    bandas = [(-190, 34, "#e7ad55"), (-120, 40, "#f8dc9c"), (-55, 26, "#dd9a47"),
              (40, 30, "#f8dc9c"), (95, 44, "#e2a24c"), (160, 30, "#cf8a3c")]
    for y, h, c in bandas:
        dy = 4 * math.sin(t * 1.3 + y)
        g.append(f"<path d='M-240 {y+dy:.1f} Q-120 {y-10+dy:.1f} 0 {y+dy:.1f} T240 {y+dy:.1f} L240 {y+h+dy:.1f} "
                 f"Q120 {y+h+10+dy:.1f} 0 {y+h+dy:.1f} T-240 {y+h+dy:.1f} Z' fill='{c}'/>")
    # brillo y sombra suaves
    g.append(f"<circle cx='-70' cy='-80' r='{R}' fill='#fff3cf' opacity='0.18'/>")
    g.append(f"<path d='M-{R} -{R} H{R} V{R} H-{R} Z M-30 -40 m-{R} 0 a{R} {R} 0 1 0 {2*R} 0 a{R} {R} 0 1 0 -{2*R} 0 Z' fill='#8a4515' opacity='0.22' fill-rule='evenodd'/>")
    g.append("</g>")
    g.append(f"<circle r='{R}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # cara
    ojo = 1 + 0.25 * rev
    for ex in (-72, 72):
        g.append(f"<g transform='translate({ex},-48) scale({ojo:.3f},{ojo*blink:.3f})'>"
                 f"<ellipse rx='34' ry='40' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='{4+6*math.sin(t*0.8):.1f}' cy='6' r='19' fill='#2a1a14'/>"
                 f"<circle cx='-4' cy='-4' r='7' fill='#fff'/></g>")
    for ex in (-122, 122):
        g.append(f"<ellipse cx='{ex}' cy='22' rx='26' ry='15' fill='#ff8a7a' opacity='0.7'/>")
    if rev < 0.5:
        g.append(f"<path d='M-36 48 Q0 82 36 48' fill='#c2453d' stroke='{INK}' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='62' rx='24' ry='30' fill='#7a2a24' stroke='{INK}' stroke-width='7'/>"
                 f"<ellipse cx='0' cy='76' rx='13' ry='9' fill='#ff7a7a'/>")
    return "".join(g)


def luna(t, lado):
    a = t * 0.75 + 2.2
    x = CX + 600 * math.cos(a); y = CY + 285 * math.sin(a)
    if (math.sin(a) > 0) != (lado == "delante"):
        return ""
    s = 0.85 + 0.15 * math.sin(a)
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({s:.3f})'>"
            f"<circle r='44' fill='#f19a4a' stroke='{INK}' stroke-width='7'/>"
            f"<circle cx='-12' cy='-10' r='10' fill='#d77a33'/><circle cx='14' cy='12' r='7' fill='#d77a33'/></g>")


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.5)
    glow = seg(t, 7.2, 7.9)
    # inclinación de los anillos (sin del ángulo de visión)
    sb = lerp(0.36, 0.003, seg(t, 4.9, 7.45)) + 0.025 * math.sin(t * 1.6) * (1 - seg(t, 4.5, 6))
    tilt = lerp(-17, -6, seg(t, 4.9, 7.45)) + 2 * math.sin(t * 0.9)
    enter = seg(t, 0, 1.6)
    py = lerp(1800, CY, enter) + (6 * math.sin(t * 2.1) if t > 1.6 else 0)
    sc = lerp(0.75, 1.0, enter)

    top = mix("#140b38", "#07204a", rev); bot = mix("#33196b", "#0f4a7a", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='1' stop-color='{bot}'/></linearGradient>"
            "<radialGradient id='neb1'><stop offset='0' stop-color='#b04fd6' stop-opacity='0.45'/><stop offset='1' stop-color='#b04fd6' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='neb2'><stop offset='0' stop-color='#36c5d6' stop-opacity='0.35'/><stop offset='1' stop-color='#36c5d6' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#ffe9a8' stop-opacity='{0.8*glow:.3f}'/><stop offset='1' stop-color='#ffb84d' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='aura'><stop offset='0.55' stop-color='#ffd98a' stop-opacity='0.35'/><stop offset='1' stop-color='#ffd98a' stop-opacity='0'/></radialGradient>"
            f"<clipPath id='clipA'><rect x='-600' y='-600' width='1200' height='600'/></clipPath>"
            f"<clipPath id='clipD'><rect x='-600' y='0' width='1200' height='600'/></clipPath>"
            f"<clipPath id='clipP'><circle r='{R}'/></clipPath>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>",
         f"<ellipse cx='{820+20*math.sin(t*0.4):.0f}' cy='520' rx='420' ry='300' fill='url(#neb1)'/>",
         f"<ellipse cx='{230-20*math.sin(t*0.3):.0f}' cy='860' rx='380' ry='260' fill='url(#neb2)'/>"]
    z = 1 + 0.22 * seg(t, 7.3, 10)
    s.append(f"<g transform='translate({CX},{CY}) scale({z:.4f}) translate({-CX},{-CY})'>")
    for sx, sy, sr, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 3.2 + ph * 3)
        s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # estrella fugaz en la parte baja
    k = (t - 2.6) / 0.9
    if 0 < k < 1:
        x0, y0 = lerp(1150, 120, k), lerp(1080, 1330, k)
        s.append(f"<line x1='{x0:.0f}' y1='{y0:.0f}' x2='{x0+160:.0f}' y2='{y0-40:.0f}' stroke='#fff' stroke-width='5' stroke-linecap='round' opacity='{math.sin(math.pi*k):.2f}'/>")
    s.append(luna(t, "atras"))
    s.append(f"<g transform='translate({CX},{py:.1f}) scale({sc:.4f}) rotate({tilt:.2f})'>")
    s.append(f"<circle r='{R+60}' fill='url(#aura)'/>")
    s.append(anillos(sb, t, glow, "atras"))
    s.append(planeta(t, rev))
    s.append(anillos(sb, t, glow, "delante"))
    if glow > 0:
        # la línea de los anillos de canto brilla
        s.append(f"<ellipse cx='0' cy='0' rx='{lerp(300, 560, glow):.0f}' ry='{lerp(20, 60, glow):.0f}' fill='url(#halo)'/>")
        s.append(f"<line x1='-472' y1='0' x2='472' y2='0' stroke='{INK}' stroke-width='{15*glow:.1f}' stroke-linecap='round'/>")
        s.append(f"<line x1='-468' y1='0' x2='468' y2='0' stroke='#ffd75a' stroke-width='{8*glow:.1f}' stroke-linecap='round'/>")
        s.append(f"<line x1='-440' y1='-1' x2='440' y2='-1' stroke='#fffbe6' stroke-width='{3*glow:.1f}' stroke-linecap='round'/>")
        for side in (-1, 1):
            for i in range(5):
                ang = side * 0.0 + (i - 2) * 0.5
                d = lerp(0, 70 + 15 * i, rev)
                x = side * (470 + d * math.cos(ang)); y = d * math.sin(ang)
                r = 9 * (1 - seg(t, 8.8, 10)) * rev
                if r > 0.3:
                    s.append(f"<path d='M{x:.1f} {y-r*2:.1f} L{x+r*0.6:.1f} {y:.1f} L{x:.1f} {y+r*2:.1f} L{x-r*0.6:.1f} {y:.1f} Z' fill='#fff2a8'/>")
    s.append("</g>")
    s.append(luna(t, "delante"))
    for px, pyy, pr, sp in DUST:
        yy = (pyy - t * sp) % 920 + 1000
        s.append(f"<circle cx='{px + 15*math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#c9b8ff' opacity='0.4'/>")
    s.append("</g>")
    # destello en la revelación
    fl = clamp(1 - abs(t - REVELACION - 0.05) / 0.25)
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fff7e0' opacity='{0.4*fl:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
