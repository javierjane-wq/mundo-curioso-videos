"""2026-11-10-c1 · Los girasoles jóvenes siguen al Sol de este a oeste y de noche vuelven a girarse hacia el este.

Un girasol joven con cara (original) en un campo: amanece a la izquierda (este), el Sol cruza el
cielo y la flor lo sigue; anochece a la derecha y, en la REVELACION, de noche, la flor se gira de
vuelta hacia el este (izquierda) con halo dorado, luciérnagas y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, zoom

DUR = 10.0
REVELACION = 7.45   # la flor se gira hacia el este de noche
MUSICA = 8

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1250), rng.uniform(2.5, 6), rng.uniform(0, 6.28)) for _ in range(80)]
FLIES = [(rng.uniform(80, 1000), rng.uniform(1250, 1800), rng.uniform(0, 6.28), rng.uniform(0.6, 1.4)) for _ in range(22)]
GRASS = [(x, rng.uniform(40, 80), rng.uniform(0, 6.28)) for x in range(-10, 1100, 26)]
SMALL = [(110, 1395, 0.36), (300, 1370, 0.30), (800, 1372, 0.30), (975, 1392, 0.36)]


def facing(t):
    """-1 = mira al este (izquierda), +1 = al oeste (derecha)."""
    f = lerp(-1, 1, seg(t, 2.2, 6.4))
    back = seg(t, 7.35, 8.5)
    f = lerp(f, -1, back)
    f -= 0.12 * math.sin(math.pi * clamp((t - 8.3) / 0.6)) * (t > 8.3)   # pequeño rebote al llegar
    return max(-1.1, min(1, f))


def sun_pos(t):
    s = seg(t, 0.0, 6.9)
    x = lerp(110, 970, s)
    y = 1340 - 430 * math.sin(math.pi * (0.10 + 0.80 * s))
    y += 300 * seg(t, 6.5, 7.6)
    return x, y


def head(cx, cy, f, sc, t, night, cara=True, blink_off=0.0):
    """Cabeza de girasol en vista 3/4: se estrecha y la cara se desplaza hacia donde mira."""
    sx = 1 - 0.30 * min(1, abs(f))
    tilt = 16 * f
    shift = 34 * f
    g = [f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({tilt:.1f}) scale({sc:.3f})'>"]
    g.append(f"<g transform='scale({sx:.3f},1)'>")
    pet_b = mix("#f08a1c", "#7a5a2a", night * 0.6); pet_f = mix("#ffd21f", "#a8893a", night * 0.6)
    for ring, col, off, L in ((0, pet_b, 10, 78), (1, pet_f, 0, 70)):
        for i in range(18):
            a = i * 20 + off + 3 * math.sin(t * 2 + i)
            g.append(f"<ellipse cx='0' cy='{-120 - L * 0.45:.0f}' rx='27' ry='{L}' fill='{col}' stroke='{INK}' stroke-width='6' transform='rotate({a:.1f})'/>")
    disc = mix("#7a4520", "#3e2614", night * 0.5)
    g.append(f"<circle r='118' fill='{disc}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<circle r='92' fill='none' stroke='{mix('#5c3216', '#2a1a10', night*0.5)}' stroke-width='10'/>")
    for i in range(70):
        r = 9 * math.sqrt(i + 1) + 6
        a = i * 2.39996
        if r < 108:
            g.append(f"<circle cx='{r*math.cos(a):.1f}' cy='{r*math.sin(a):.1f}' r='4' fill='{mix('#4a2810', '#22140a', night*0.5)}'/>")
    g.append("</g>")
    if cara:
        blink = 0.12 if (t + 1.3 + blink_off) % 2.9 < 0.13 else 1.0
        look = 9 * f
        for ex in (-40, 40):
            x = ex * sx + shift
            g.append(f"<ellipse cx='{x:.1f}' cy='-18' rx='{24*sx+4:.1f}' ry='{30*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
            if blink > 0.5:
                g.append(f"<circle cx='{x + look:.1f}' cy='-14' r='13' fill='{INK}'/>")
                g.append(f"<circle cx='{x + look - 4:.1f}' cy='-20' r='5' fill='#fff'/>")
        for ex in (-66, 66):
            g.append(f"<ellipse cx='{ex*sx + shift:.1f}' cy='22' rx='16' ry='10' fill='#ff7e86' opacity='0.75'/>")
        g.append(f"<path d='M{-30*sx + shift:.1f} 32 Q{shift:.1f} 62 {30*sx + shift:.1f} 32' fill='#c8303a' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def leaf(x, y, ang, size, col):
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({size:.3f})'>"
            f"<path d='M0 0 Q60 -70 150 -20 Q80 40 0 0 Z' fill='{col}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M8 -2 Q70 -30 135 -20' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/></g>")


def flower(t, night):
    f = facing(t)
    grow = seg(t, 0, 1.4)
    sway = 6 * math.sin(t * 1.7)
    base_x, base_y = 540, 1860
    hx = 540 + 38 * f + sway
    hy = lerp(1420, 1300, grow) + 5 * math.sin(t * 2.3)
    sc = lerp(0.86, 1.0, grow) * (1 + 0.06 * math.sin(math.pi * clamp((t - 7.45) / 0.7)))
    stem_c = mix("#3fae46", "#1f5a33", night * 0.6)
    g = []
    path = f"M{base_x} {base_y} Q{540 - 30 * f:.1f} 1620 {hx:.1f} {hy + 90:.1f}"
    g.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='40' stroke-linecap='round'/>")
    g.append(f"<path d='{path}' fill='none' stroke='{stem_c}' stroke-width='24' stroke-linecap='round'/>")
    lc = mix("#58c24f", "#235f36", night * 0.6)
    g.append(leaf(532, 1690, -18 + 8 * math.sin(t * 2.1), 1.05, lc))
    g.append(f"<g transform='translate(1080,0) scale(-1,1)'>{leaf(1080 - 548, 1600, -22 + 8 * math.sin(t * 2.1 + 1), 0.95, lc)}</g>")
    # sépalos verdes detrás de la cabeza
    g.append(f"<g transform='translate({hx:.1f},{hy:.1f}) rotate({16*f:.1f}) scale({sc*(1-0.3*min(1,abs(f))):.3f},{sc:.3f})'>")
    for i in range(12):
        g.append(f"<path d='M0 0 L-18 -190 L18 -190 Z' fill='{stem_c}' stroke='{INK}' stroke-width='6' transform='rotate({i*30+15})'/>")
    g.append("</g>")
    g.append(head(hx, hy, f, sc, t, night))
    return "".join(g), hx, hy


def bee(t, day):
    if day < 0.05: return ""
    x = 540 + 330 * math.sin(t * 0.9) ; y = 1150 + 60 * math.sin(t * 2.2)
    d = 1 if math.cos(t * 0.9) > 0 else -1
    wing = 0.6 + 0.4 * abs(math.sin(t * 40))
    return (f"<g transform='translate({x:.1f},{y:.1f}) scale({d},1)' opacity='{day:.2f}'>"
            f"<ellipse cx='-6' cy='-26' rx='20' ry='{26*wing:.1f}' fill='#eaf6ff' stroke='{INK}' stroke-width='5' opacity='0.9'/>"
            f"<ellipse cx='12' cy='-24' rx='16' ry='{22*wing:.1f}' fill='#eaf6ff' stroke='{INK}' stroke-width='5' opacity='0.9'/>"
            f"<ellipse rx='34' ry='24' fill='#ffcf26' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-8 -22 L-8 22 M8 -23 L8 23' stroke='{INK}' stroke-width='8'/>"
            f"<circle cx='24' cy='-5' r='5' fill='{INK}'/>"
            f"<path d='M-34 0 L-46 0' stroke='{INK}' stroke-width='6' stroke-linecap='round'/></g>")


def frame(t):
    dawn = seg(t, 0, 2.4)          # amanecer -> día
    dusk = seg(t, 5.0, 6.6)        # día -> atardecer
    night = seg(t, 6.4, 7.8)       # atardecer -> noche
    day = (1 - night)
    top = mix(mix(mix("#ff9f80", "#46a9f5", dawn), "#ff7a4a", dusk), "#0b1636", night)
    mid = mix(mix(mix("#ffc79a", "#8fd0ff", dawn), "#ffab5e", dusk), "#1c2b5e", night)
    low = mix(mix(mix("#ffe6b0", "#d6f0ff", dawn), "#ffd27a", dusk), "#2f3f78", night)
    sx, sy = sun_pos(t)
    rev = seg(t, 7.35, 8.4)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff6d0' stop-opacity='0.8'/><stop offset='1' stop-color='#ffb84a' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#ffe680' stop-opacity='{0.75*rev:.3f}'/><stop offset='0.5' stop-color='#ffb02e' stop-opacity='{0.35*rev:.3f}'/><stop offset='1' stop-color='#ff8a00' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='east' cx='0' cy='0.7' r='0.9'><stop offset='0' stop-color='#ff9d6b' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ff9d6b' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>",
         f"<rect width='{W}' height='{H}' fill='url(#east)'/>"]
    cuerpo = []
    st = seg(t, 6.6, 8.2)
    for x, y, r, ph in STARS:
        a = st * (0.55 + 0.45 * math.sin(t * 3 + ph))
        if a > 0.02: cuerpo.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # luna
    mo = seg(t, 6.8, 8.0)
    if mo > 0:
        my = lerp(1150, 1000, mo)
        cuerpo.append(f"<g opacity='{mo:.2f}'><circle cx='880' cy='{my:.0f}' r='58' fill='#fff6d8' stroke='{INK}' stroke-width='7'/>"
                      f"<circle cx='862' cy='{my-14:.0f}' r='10' fill='#e8dcb8'/><circle cx='898' cy='{my+16:.0f}' r='7' fill='#e8dcb8'/></g>")
    # sol
    if sy < 1500:
        cuerpo.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='210' fill='url(#glow)' opacity='{day:.2f}'/>")
        for i in range(12):
            a = i * 30 + t * 20
            cuerpo.append(f"<line x1='{sx:.0f}' y1='{sy:.0f}' x2='{sx + 125*math.cos(math.radians(a)):.0f}' y2='{sy + 125*math.sin(math.radians(a)):.0f}' "
                          f"stroke='{mix('#ffd84a', '#ff8a3a', dusk)}' stroke-width='14' stroke-linecap='round'/>")
        cuerpo.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='78' fill='{mix('#ffe14a', '#ff9a3a', dusk)}' stroke='{INK}' stroke-width='{LW}'/>")
    # nubes
    for i, (cx, cy, sc) in enumerate([(150, 760, 1.2), (760, 640, 1.0), (520, 1040, 0.8)]):
        dx = (t * 16 * (1 + 0.4 * i)) % 1500 - 300
        col = mix(mix("#ffe2d0", "#ffffff", dawn), "#4a5688", night)
        cuerpo.append(f"<g transform='translate({cx + dx - 300:.0f},{cy}) scale({sc})' opacity='0.92'>"
                      f"<path d='M0 50 Q10 0 70 10 Q100 -40 160 0 Q230 -20 250 50 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # colinas
    h1 = mix("#6cc06a", "#1c3d3a", night); h2 = mix("#8fd45a", "#24503a", night); h3 = mix("#5fb848", "#1d4630", night)
    cuerpo.append(f"<path d='M0 1360 Q220 1270 470 1340 T900 1320 T1080 1340 L1080 1920 L0 1920 Z' fill='{h1}' stroke='{INK}' stroke-width='{LW}'/>")
    # girasoles lejanos (también giran)
    f = facing(t)
    for i, (x, y, sc) in enumerate(SMALL):
        stc = mix("#3fae46", "#1f5a33", night * 0.6)
        cuerpo.append(f"<path d='M{x} {y + 160} L{x + 10*f:.1f} {y}' stroke='{INK}' stroke-width='18' stroke-linecap='round'/>"
                      f"<path d='M{x} {y + 160} L{x + 10*f:.1f} {y}' stroke='{stc}' stroke-width='9' stroke-linecap='round'/>")
        cuerpo.append(head(x + 10 * f, y, f, sc, t + i, night, cara=False))
    cuerpo.append(f"<path d='M0 1500 Q300 1430 600 1490 T1080 1470 L1080 1920 L0 1920 Z' fill='{h2}' stroke='{INK}' stroke-width='{LW}'/>")
    cuerpo.append(f"<path d='M0 1700 Q280 1640 560 1690 T1080 1680 L1080 1920 L0 1920 Z' fill='{h3}' stroke='{INK}' stroke-width='{LW}'/>")
    # halo de la revelación
    fl, hx, hy = flower(t, night)
    if rev > 0:
        cuerpo.append(f"<circle cx='{hx:.0f}' cy='{hy:.0f}' r='{lerp(200, 420, rev):.0f}' fill='url(#halo)'/>")
    cuerpo.append(fl)
    # hierba delantera
    gc = mix("#4aa63c", "#173a28", night)
    for x, h, ph in GRASS:
        b = 10 * math.sin(t * 2.5 + ph)
        cuerpo.append(f"<path d='M{x - 10} 1925 Q{x + b/2:.1f} {1925 - h/2:.1f} {x + b:.1f} {1925 - h:.1f} Q{x + 4} {1925 - h/2:.1f} {x + 12} 1925 Z' fill='{gc}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    cuerpo.append(bee(t, 1 - seg(t, 5.6, 6.8)))
    # luciérnagas
    ff = seg(t, 7.0, 8.0)
    if ff > 0:
        for x, y, ph, sp in FLIES:
            a = ff * (0.5 + 0.5 * math.sin(t * 5 * sp + ph))
            xx = x + 30 * math.sin(t * sp + ph); yy = y + 25 * math.cos(t * sp * 1.3 + ph)
            cuerpo.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='16' fill='#fff59a' opacity='{0.35*a:.2f}'/>"
                          f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='6' fill='#fffbd0' opacity='{a:.2f}'/>")
    z = 1 + 0.16 * seg(t, 7.35, 9.8)
    s.append(zoom(hx, hy, z, "".join(cuerpo)))
    s.append("</svg>")
    return "".join(s)
