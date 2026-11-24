"""Uñas de las manos contra uñas de los pies: las de las manos crecen más del doble de rápido.

Datos (Yaemsiri et al. 2010, J Eur Acad Dermatol Venereol; PubMed 19744178): uñas de las manos
~3,47 mm/mes, uñas de los pies ~1,62 mm/mes.

Protagonistas: una mano (vista por el dorso, con cara) y un pie (también por el dorso, dedos hacia
arriba, con cara) que salen de la arena de una playa. El Sol sale y se pone deprisa (pasan los días)
y las uñas crecen: las de la mano mucho más. Revelación: brillo dorado y destellos en las uñas de la
mano, el pie se sorprende y zoom a la mano.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.4    # destello en las uñas de la mano: golpe musical
MUSICA = 5

rng = np.random.default_rng(1124)
SPARKS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28), rng.uniform(0.7, 1.3)) for _ in range(16)]
SAND_DOTS = [(rng.uniform(0, W), rng.uniform(1430, 1900), rng.uniform(3, 7)) for _ in range(70)]
SPLASH = [(rng.uniform(-1, 1), rng.uniform(0.6, 1.2), rng.uniform(6, 13)) for _ in range(14)]
SHELLS = [(120, 1600, 0.9, 20), (965, 1520, 0.75, -25), (560, 1880, 1.0, 10)]

SKIN, SKIN_D = "#f7c59f", "#e9a47a"
NAIL, NAIL_EDGE = "#ffc9cf", "#fffaf0"

HX, HY = 320, 1790     # base de la muñeca
FX, FY = 790, 1800     # talón


def nail(cx, top, w, h, grow, glow=0.0):
    """Uña sobre la punta de un dedo: lecho rosa + borde libre blanco que crece hacia arriba."""
    s = []
    if grow > 0.5:
        s.append(f"<rect x='{cx - w/2:.1f}' y='{top - grow:.1f}' width='{w:.1f}' height='{h*0.5 + grow:.1f}' rx='{w*0.42:.1f}' "
                 f"fill='{mix(NAIL_EDGE, '#fff3a8', glow)}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<rect x='{cx - w/2:.1f}' y='{top + 4:.1f}' width='{w:.1f}' height='{h:.1f}' rx='{w*0.42:.1f}' "
             f"fill='{mix(NAIL, '#ffd9a0', glow*0.6)}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<path d='M{cx - w*0.22:.1f} {top + 14:.1f} Q{cx - w*0.25:.1f} {top + h*0.5:.1f} {cx - w*0.12:.1f} {top + h - 6:.1f}' "
             f"stroke='#fff' stroke-width='6' fill='none' stroke-linecap='round' opacity='0.8'/>")
    return "".join(s)


def eyes(t, cx, cy, r, sep, look=0.0, wide=0.0, fase=0.0):
    ciclo = (t + fase) % 2.9
    blink = 0.12 if ciclo < 0.13 else 1.0
    rr = r * (1 + 0.25 * wide)
    s = []
    for ex in (-sep, sep):
        s.append(f"<ellipse cx='{cx + ex:.1f}' cy='{cy:.1f}' rx='{rr:.1f}' ry='{rr*1.12*blink:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.5:
            s.append(f"<circle cx='{cx + ex + look:.1f}' cy='{cy + 2:.1f}' r='{rr*0.52:.1f}' fill='{INK}'/>")
            s.append(f"<circle cx='{cx + ex + look - rr*0.18:.1f}' cy='{cy - rr*0.2:.1f}' r='{rr*0.18:.1f}' fill='#fff'/>")
    return "".join(s)


def hand(t, g, glow):
    """Mano derecha vista por el dorso (pulgar a la izquierda), origen en la base de la muñeca."""
    up = 0.45 * (1 - ease(clamp(t / 0.8)))
    jump = -40 * math.sin(math.pi * seg(t, 7.4, 7.95)) if t > 7.4 else 0
    wave = 7 * math.sin(t * 3.2) * (1 - 0.6 * seg(t, 7.2, 7.6))
    s = [f"<g transform='translate({HX},{HY + 620*up + jump:.1f}) scale(1.12) rotate({wave:.2f})'>"]
    # muñeca y palma
    s.append(f"<rect x='-88' y='-170' width='176' height='200' rx='30' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    # dedos (índice, corazón, anular, meñique)
    dedos = [(-102, 190, 64), (-34, 218, 66), (34, 200, 64), (100, 158, 58)]
    for i, (dx, ln, wd) in enumerate(dedos):
        a = 4 * math.sin(t * 4.0 + i * 0.9)
        base = -380
        s.append(f"<g transform='translate({dx},{base}) rotate({a:.2f})'>")
        s.append(f"<rect x='{-wd/2}' y='{-ln}' width='{wd}' height='{ln + 60}' rx='{wd/2}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(f"<path d='M{-wd*0.28:.1f} {-ln*0.45:.1f} Q0 {-ln*0.40:.1f} {wd*0.28:.1f} {-ln*0.45:.1f}' stroke='{SKIN_D}' stroke-width='5' fill='none' stroke-linecap='round'/>")
        s.append(nail(0, -ln + 8, wd * 0.66, 50, g, glow))
        s.append("</g>")
    # pulgar
    s.append(f"<g transform='translate(-128,-210) rotate(-42)'>")
    s.append(f"<rect x='-33' y='-150' width='66' height='190' rx='33' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(nail(0, -142, 44, 46, g, glow))
    s.append("</g>")
    s.append(f"<rect x='-150' y='-420' width='300' height='290' rx='80' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    # nudillos
    for kx in (-102, -34, 34, 100):
        s.append(f"<path d='M{kx - 16} -392 Q{kx} -404 {kx + 16} -392' stroke='{SKIN_D}' stroke-width='6' fill='none' stroke-linecap='round'/>")
    # cara
    s.append(f"<ellipse cx='-80' cy='-215' rx='24' ry='14' fill='#ff9a8a' opacity='0.55'/>")
    s.append(f"<ellipse cx='80' cy='-215' rx='24' ry='14' fill='#ff9a8a' opacity='0.55'/>")
    s.append(eyes(t, 0, -275, 30, 52, look=4 * math.sin(t * 1.3), fase=0.4))
    smile = lerp(22, 46, seg(t, 7.4, 7.8))
    s.append(f"<path d='M-44 -205 Q0 {-205 + smile:.1f} 44 -205' fill='{'#a8323a' if smile > 30 else 'none'}' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    s.append("</g>")
    return "".join(s)


def foot(t, g, wide):
    """Pie derecho visto por el dorso con los dedos hacia arriba (dedo gordo a la izquierda)."""
    up = 0.45 * (1 - ease(clamp((t - 0.1) / 0.8)))
    sway = 5 * math.sin(t * 2.6 + 1.0)
    shake = 6 * math.sin(t * 40) * seg(t, 7.45, 7.6) * (1 - seg(t, 7.9, 8.2))
    s = [f"<g transform='translate({FX + shake:.1f},{FY + 620*up:.1f}) scale(1.12) rotate({sway:.2f})'>"]
    # tobillo
    s.append(f"<rect x='-80' y='-150' width='160' height='190' rx='30' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
    # dedos: (x, y de la punta, ancho, alto)
    dedos = [(-84, -478, 84, 130), (-14, -458, 58, 104), (40, -440, 54, 96), (88, -414, 50, 86), (128, -380, 44, 72)]
    for i, (dx, top, wd, ht) in enumerate(dedos):
        wig = 5 * math.sin(t * 5 + i * 1.1)
        s.append(f"<g transform='translate(0,{wig:.1f})'>")
        s.append(f"<rect x='{dx - wd/2}' y='{top}' width='{wd}' height='{ht + 40}' rx='{wd/2}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}'/>")
        s.append(nail(dx, top + 6, wd * 0.62, ht * 0.42, g * (1.0 if i == 0 else 0.75)))
        s.append("</g>")
    # empeine (forma de pie: ancho delante, estrecho en el talón)
    s.append(f"<path d='M-92 -20 C-130 -120 -150 -260 -132 -350 C-118 -410 -40 -400 20 -390 "
             f"C90 -380 150 -360 152 -310 C156 -230 120 -120 92 -20 Z' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M-40 -360 Q10 -372 60 -360' stroke='{SKIN_D}' stroke-width='6' fill='none' stroke-linecap='round'/>")
    # cara
    s.append(f"<ellipse cx='-70' cy='-180' rx='22' ry='13' fill='#ff9a8a' opacity='0.55'/>")
    s.append(f"<ellipse cx='80' cy='-180' rx='22' ry='13' fill='#ff9a8a' opacity='0.55'/>")
    s.append(eyes(t, 4, -240, 27, 48, look=-6 * seg(t, 5.0, 5.6), wide=wide, fase=1.5))
    if wide > 0.3:
        s.append(f"<ellipse cx='4' cy='-160' rx='{lerp(10, 20, wide):.1f}' ry='{lerp(10, 26, wide):.1f}' fill='#a8323a' stroke='{INK}' stroke-width='6'/>")
        # gota de sudor
        dy = 30 * seg(t, 7.6, 9.6)
        s.append(f"<path d='M118 {-300 + dy:.1f} q14 22 0 32 q-14 -10 0 -32 Z' fill='#7fd0ff' stroke='{INK}' stroke-width='5'/>")
    else:
        s.append(f"<path d='M-30 -168 Q4 -146 38 -168' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    s.append("</g>")
    return "".join(s)


def frame(t):
    glow = seg(t, 7.3, 7.7)
    # los días pasan: el Sol sale y se pone (2 vueltas) entre 2,4 y 7,4 s
    k = clamp((t - 2.4) / 5.0) * 2.0 if t >= 2.4 else 0.0
    ph = k % 1.0
    night = 0.0 if t < 2.4 or t > 7.4 else 0.35 * (1 - math.sin(math.pi * ph)) ** 3
    top = mix("#7fd3ff", "#3b4f9a", night); low = mix("#d9f4ff", "#e9a8c8", night)
    # crecimiento de las uñas (px): mano más del doble que el pie
    gh = lerp(0, 56, seg(t, 2.4, 7.4)); gf = lerp(0, 24, seg(t, 2.4, 7.4))
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0' stop-color='#fff6b0' stop-opacity='{0.95*glow:.3f}'/>"
            f"<stop offset='0.5' stop-color='#ffd23f' stop-opacity='{0.55*glow:.3f}'/><stop offset='1' stop-color='#ffb000' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#1fa3d6', '#25508f', night)}'/><stop offset='1' stop-color='{mix('#5fd6e8', '#3f7db0', night)}'/></linearGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # Sol que sale y se pone tras el mar (pasan los días)
    if t < 2.4:
        sx, sy = 880, 1010
    else:
        sx = lerp(980, 640, ph); sy = 1150 - 190 * math.sin(math.pi * ph)
    s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='92' fill='#fff2a8' opacity='0.45'/>")
    s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='62' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>")
    # nubes suaves arriba
    for i, (cx, cy, sc, sp) in enumerate([(160, 520, 1.3, 16), (820, 760, 1.0, 24), (480, 300, 0.8, 12)]):
        x = (cx + t * sp) % 1400 - 200
        s.append(f"<g transform='translate({x:.0f},{cy}) scale({sc})' opacity='0.92'>"
                 f"<path d='M0 40 Q15 -15 75 0 Q105 -45 165 -5 Q225 -20 245 40 Z' fill='{mix('#ffffff', '#c9c4e8', night)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # mar con olas
    s.append(f"<rect x='0' y='1130' width='{W}' height='420' fill='url(#sea)'/>")
    s.append(f"<line x1='0' y1='1130' x2='{W}' y2='1130' stroke='{INK}' stroke-width='{LW}'/>")
    for row, yy in enumerate((1185, 1250, 1320)):
        off = (t * (40 + row * 25)) % 160
        d = " ".join(f"M{x - off:.0f} {yy} q20 -14 40 0" for x in range(0, W + 200, 160))
        s.append(f"<path d='{d}' stroke='#e8fbff' stroke-width='6' fill='none' stroke-linecap='round' opacity='0.8'/>")
    # orilla de espuma y arena
    sw = 10 * math.sin(t * 2.2)
    s.append(f"<path d='M0 {1395 + sw:.1f} Q270 {1360 + sw:.1f} 540 {1392 + sw:.1f} T1080 {1380 + sw:.1f} L1080 1440 L0 1440 Z' fill='#f4fdff' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<path d='M0 1430 Q300 1395 600 1425 T1080 1415 L1080 1920 L0 1920 Z' fill='#f5d28c' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, r in SAND_DOTS:
        s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#d9ac62' opacity='0.7'/>")
    for x, y, sc, rot in SHELLS:
        s.append(f"<g transform='translate({x},{y}) rotate({rot}) scale({sc})'><path d='M-30 10 Q0 -40 30 10 Z' fill='#ff9fb2' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
                 f"<path d='M0 8 L0 -18 M-14 8 L-8 -12 M14 8 L8 -12' stroke='{INK}' stroke-width='4'/></g>")
    # brillo dorado detrás de la mano
    if glow > 0:
        s.append(f"<circle cx='{HX}' cy='1200' r='{lerp(120, 420, glow):.0f}' fill='url(#halo)'/>")
        for i in range(12):
            a = i * math.pi / 6 + t * 0.6
            r1, r2 = 200, lerp(220, 430, glow)
            s.append(f"<line x1='{HX + r1*math.cos(a):.0f}' y1='{1200 + r1*math.sin(a):.0f}' x2='{HX + r2*math.cos(a):.0f}' y2='{1200 + r2*math.sin(a):.0f}' "
                     f"stroke='#ffe066' stroke-width='14' stroke-linecap='round' opacity='{0.75*glow:.2f}'/>")
    s.append(hand(t, gh, glow))
    s.append(foot(t, gf, seg(t, 7.45, 7.8)))
    # arena delante (los personajes salen de ella)
    s.append(f"<path d='M0 1760 Q140 1735 {HX} 1745 Q{HX + 180} 1735 {FX} 1752 Q{FX + 150} 1740 1080 1760 L1080 1920 L0 1920 Z' fill='#f5d28c'/>")
    s.append(f"<path d='M0 1760 Q140 1735 {HX} 1745 Q{HX + 180} 1735 {FX} 1752 Q{FX + 150} 1740 1080 1760' fill='none' stroke='{INK}' stroke-width='7'/>")
    for bx in (HX, FX):
        s.append(f"<ellipse cx='{bx}' cy='1760' rx='170' ry='34' fill='#e8bf72' stroke='{INK}' stroke-width='7'/>")
    # salpicadura de arena al salir
    for cx, t0 in ((HX, 0.0), (FX, 0.1)):
        k2 = clamp((t - t0) / 0.9)
        if 0 < k2 < 1:
            for dx, dv, r in SPLASH:
                x = cx + dx * 220 * k2
                y = 1740 - 260 * dv * k2 + 380 * k2 * k2
                s.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='#e8bf72' stroke='{INK}' stroke-width='4' opacity='{1 - k2:.2f}'/>")
    # destellos en las uñas de la mano
    if glow > 0:
        for dx, dy, ph2, sc in SPARKS:
            tw = 0.5 + 0.5 * math.sin(t * 9 + ph2)
            x = HX + dx * 250; y = 1150 + dy * 160
            r = 26 * sc * tw * glow
            s.append(f"<path d='M{x:.0f} {y - r:.0f} L{x + r*0.25:.0f} {y - r*0.25:.0f} L{x + r:.0f} {y:.0f} L{x + r*0.25:.0f} {y + r*0.25:.0f} "
                     f"L{x:.0f} {y + r:.0f} L{x - r*0.25:.0f} {y + r*0.25:.0f} L{x - r:.0f} {y:.0f} L{x - r*0.25:.0f} {y - r*0.25:.0f} Z' fill='#fff59a' stroke='{INK}' stroke-width='3'/>")
    z = 1 + 0.17 * seg(t, 7.4, 8.1) + 0.02 * seg(t, 8.1, 10)
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>" \
           + zoom(520, 1450, z, "".join(s)) + "</svg>"
