"""2026-11-25-c4 · Récords: la muñeca de nieve más alta del mundo (Olympia, 37,21 m, Bethel, Maine, 2008).

Un muñeco de nieve normal entra dando saltitos por la nieve (0-4,3 s). Desde 4,3 s la cámara se aleja
muchísimo y aparece a su lado una muñeca de nieve gigante; en la REVELACION (6,5 s) sale el sol, el
cielo se pone azul brillante, rayos detrás de la gigante y destellos, con un ligero zoom de cámara.
Las coordenadas del mundo se convierten a pantalla a mano (no con scale) para que los contornos
mantengan su grosor al alejarse la cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 6.5
MUSICA = 8

GROUND = 1800                 # línea del suelo en pantalla
H_SMALL = 700                 # altura del muñeco normal (mundo, = pantalla a escala 1)
H_GIANT = H_SMALL * 20.5      # 37,2 m frente a ~1,8 m
G_X = -5000                   # posición de la gigante en el mundo
S_FIN = 0.06                  # escala final de la cámara

rng = np.random.default_rng(25)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 11), rng.uniform(60, 150), rng.uniform(0, 6.28))
          for _ in range(110)]
SPARK = [(rng.uniform(-1, 1), rng.uniform(0.05, 1.0), rng.uniform(0, 6.28)) for _ in range(26)]


def cam(t):
    k = seg(t, 4.3, 6.5)
    s = math.exp(lerp(0, math.log(S_FIN), k))
    X = lerp(700, 800, k)
    return s, X


def pine(cx, base, h, lw, col="#2f8a57", snow=True):
    w = h * 0.42
    p = [f"<rect x='{cx - h*0.04:.1f}' y='{base - h*0.14:.1f}' width='{h*0.08:.1f}' height='{h*0.14:.1f}' fill='#7a4a2a' stroke='{INK}' stroke-width='{lw:.1f}'/>"]
    for i, (yy, ww) in enumerate(((0.12, 1.0), (0.42, 0.78), (0.68, 0.55))):
        y0 = base - h * yy; top = y0 - h * 0.36
        p.append(f"<path d='M{cx - w*ww:.1f} {y0:.1f} L{cx:.1f} {top:.1f} L{cx + w*ww:.1f} {y0:.1f} Z' fill='{col}' "
                 f"stroke='{INK}' stroke-width='{lw:.1f}' stroke-linejoin='round'/>")
        if snow:
            p.append(f"<path d='M{cx - w*ww*0.45:.1f} {top + h*0.16:.1f} L{cx:.1f} {top:.1f} L{cx + w*ww*0.45:.1f} {top + h*0.16:.1f} "
                     f"Q{cx:.1f} {top + h*0.10:.1f} {cx - w*ww*0.45:.1f} {top + h*0.16:.1f} Z' fill='#ffffff' stroke='{INK}' stroke-width='{lw*0.6:.1f}'/>")
    return "".join(p)


def house(cx, base, h, lw):
    w = h * 1.1
    p = [f"<rect x='{cx - w/2:.1f}' y='{base - h*0.6:.1f}' width='{w:.1f}' height='{h*0.6:.1f}' fill='#e2574c' stroke='{INK}' stroke-width='{lw:.1f}'/>",
         f"<path d='M{cx - w*0.6:.1f} {base - h*0.58:.1f} L{cx:.1f} {base - h:.1f} L{cx + w*0.6:.1f} {base - h*0.58:.1f} Z' fill='#ffffff' stroke='{INK}' stroke-width='{lw:.1f}' stroke-linejoin='round'/>",
         f"<rect x='{cx - w*0.12:.1f}' y='{base - h*0.32:.1f}' width='{w*0.24:.1f}' height='{h*0.32:.1f}' fill='#7a4a2a' stroke='{INK}' stroke-width='{lw*0.7:.1f}'/>",
         f"<rect x='{cx + w*0.2:.1f}' y='{base - h*0.48:.1f}' width='{w*0.18:.1f}' height='{h*0.16:.1f}' fill='#ffd96a' stroke='{INK}' stroke-width='{lw*0.7:.1f}'/>",
         f"<rect x='{cx - w*0.38:.1f}' y='{base - h*0.48:.1f}' width='{w*0.18:.1f}' height='{h*0.16:.1f}' fill='#ffd96a' stroke='{INK}' stroke-width='{lw*0.7:.1f}'/>"]
    return "".join(p)


def snowman(cx, base, h, t, giant=False, look=(0.0, 0.0), wave=0.0, hop=0.0):
    lw = max(2.5, min(LW, h / 78))
    base = base - hop
    r1, r2, r3 = 0.21 * h, 0.15 * h, 0.115 * h
    y1 = base - 0.2 * h; y2 = base - 0.5 * h; y3 = base - 0.72 * h
    snow = "#ffffff"; shade = "#cfe3f5"
    blink = 0.12 if (t % (3.3 if giant else 2.7)) < 0.13 else 1.0
    p = [f"<ellipse cx='{cx:.1f}' cy='{base + 0.01*h:.1f}' rx='{0.22*h:.1f}' ry='{0.03*h:.1f}' fill='#7f9fc4' opacity='0.45'/>"]
    # brazos (ramas)
    for sgn in (-1, 1):
        ang = (-25 + (wave if sgn == 1 else -wave * 0.3)) * sgn
        ax = cx + sgn * r2 * 0.85; ay = y2 - r2 * 0.25
        L = 0.3 * h
        p.append(f"<g transform='translate({ax:.1f},{ay:.1f}) rotate({ang:.1f})'>"
                 f"<path d='M0 0 L{sgn*L:.1f} 0 M{sgn*L*0.65:.1f} 0 L{sgn*L*0.85:.1f} {-L*0.18:.1f} M{sgn*L*0.8:.1f} 0 L{sgn*L*1.0:.1f} {L*0.1:.1f}' "
                 f"stroke='{INK}' stroke-width='{lw*2.6:.1f}' stroke-linecap='round' fill='none'/>"
                 f"<path d='M0 0 L{sgn*L:.1f} 0 M{sgn*L*0.65:.1f} 0 L{sgn*L*0.85:.1f} {-L*0.18:.1f} M{sgn*L*0.8:.1f} 0 L{sgn*L*1.0:.1f} {L*0.1:.1f}' "
                 f"stroke='#8a5a34' stroke-width='{lw*1.3:.1f}' stroke-linecap='round' fill='none'/></g>")
    # bolas
    for (yy, rr) in ((y1, r1), (y2, r2), (y3, r3)):
        p.append(f"<circle cx='{cx:.1f}' cy='{yy:.1f}' r='{rr:.1f}' fill='{snow}' stroke='{INK}' stroke-width='{lw:.1f}'/>")
        p.append(f"<path d='M{cx + rr*0.55:.1f} {yy + rr*0.6:.1f} Q{cx + rr*0.95:.1f} {yy:.1f} {cx + rr*0.6:.1f} {yy - rr*0.55:.1f}' "
                 f"stroke='{shade}' stroke-width='{lw*1.6:.1f}' fill='none' stroke-linecap='round'/>")
    # botones
    for by in (y2 - r2 * 0.35, y2 + r2 * 0.2, y1 - r1 * 0.35):
        bc = "#ff6fa5" if giant else "#2a2a35"
        p.append(f"<circle cx='{cx:.1f}' cy='{by:.1f}' r='{0.017*h:.1f}' fill='{bc}' stroke='{INK}' stroke-width='{lw*0.6:.1f}'/>")
    # bufanda
    sc, sc2 = ("#8e5bd8", "#ffd23f") if giant else ("#e53b3b", "#ffffff")
    ny = y3 + r3 * 0.85
    p.append(f"<path d='M{cx - r3*1.05:.1f} {ny - 0.012*h:.1f} Q{cx:.1f} {ny + 0.05*h:.1f} {cx + r3*1.05:.1f} {ny - 0.012*h:.1f} "
             f"L{cx + r3*1.0:.1f} {ny + 0.035*h:.1f} Q{cx:.1f} {ny + 0.09*h:.1f} {cx - r3*1.0:.1f} {ny + 0.035*h:.1f} Z' "
             f"fill='{sc}' stroke='{INK}' stroke-width='{lw:.1f}' stroke-linejoin='round'/>")
    fl = 14 * math.sin(t * 5.2)
    tx = cx - r3 * 0.55
    p.append(f"<g transform='translate({tx:.1f},{ny + 0.04*h:.1f}) rotate({8 + fl:.1f})'>"
             f"<rect x='{-0.03*h:.1f}' y='0' width='{0.06*h:.1f}' height='{0.17*h:.1f}' rx='{0.01*h:.1f}' fill='{sc}' stroke='{INK}' stroke-width='{lw:.1f}'/>"
             f"<rect x='{-0.03*h:.1f}' y='{0.06*h:.1f}' width='{0.06*h:.1f}' height='{0.025*h:.1f}' fill='{sc2}'/>"
             f"<rect x='{-0.03*h:.1f}' y='{0.11*h:.1f}' width='{0.06*h:.1f}' height='{0.025*h:.1f}' fill='{sc2}'/></g>")
    # cara
    lx, ly = look
    for ex in (-0.045 * h, 0.045 * h):
        ex_c = cx + ex; ey = y3 - 0.025 * h
        p.append(f"<g transform='translate({ex_c:.1f},{ey:.1f}) scale(1,{blink})'>"
                 f"<ellipse rx='{0.028*h:.1f}' ry='{0.034*h:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='{lw*0.7:.1f}'/>"
                 f"<circle cx='{lx*0.012*h:.1f}' cy='{ly*0.012*h:.1f}' r='{0.018*h:.1f}' fill='#1d1d2a'/>"
                 f"<circle cx='{lx*0.012*h - 0.006*h:.1f}' cy='{ly*0.012*h - 0.008*h:.1f}' r='{0.006*h:.1f}' fill='#fff'/></g>")
        if giant and blink > 0.5:
            for k in (-1, 0, 1):
                a = math.radians(-90 + k * 32 + (14 if ex > 0 else -14))
                x0 = ex_c + math.cos(a) * 0.028 * h; y0 = ey + math.sin(a) * 0.034 * h
                x1 = ex_c + math.cos(a) * 0.05 * h; y1b = ey + math.sin(a) * 0.055 * h
                p.append(f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{x1:.1f}' y2='{y1b:.1f}' stroke='{INK}' stroke-width='{lw*0.8:.1f}' stroke-linecap='round'/>")
    if giant:
        for ex in (-0.075 * h, 0.075 * h):
            p.append(f"<ellipse cx='{cx + ex:.1f}' cy='{y3 + 0.03*h:.1f}' rx='{0.018*h:.1f}' ry='{0.011*h:.1f}' fill='#ff9bb8' opacity='0.8'/>")
    # nariz de zanahoria
    p.append(f"<path d='M{cx - 0.006*h:.1f} {y3 + 0.0*h:.1f} L{cx + 0.11*h:.1f} {y3 + 0.022*h:.1f} L{cx - 0.006*h:.1f} {y3 + 0.03*h:.1f} Z' "
             f"fill='#ff8a2a' stroke='{INK}' stroke-width='{lw*0.8:.1f}' stroke-linejoin='round'/>")
    # sonrisa
    p.append(f"<path d='M{cx - 0.045*h:.1f} {y3 + 0.05*h:.1f} Q{cx:.1f} {y3 + 0.085*h:.1f} {cx + 0.045*h:.1f} {y3 + 0.05*h:.1f}' "
             f"stroke='{'#d8355b' if giant else INK}' stroke-width='{lw*1.1:.1f}' fill='none' stroke-linecap='round'/>")
    # sombrero
    hy = y3 - r3 * 0.78
    if giant:
        p.append(f"<ellipse cx='{cx:.1f}' cy='{hy:.1f}' rx='{0.2*h:.1f}' ry='{0.035*h:.1f}' fill='#2fb5a8' stroke='{INK}' stroke-width='{lw:.1f}'/>")
        p.append(f"<path d='M{cx - 0.09*h:.1f} {hy:.1f} L{cx - 0.08*h:.1f} {hy - 0.12*h:.1f} Q{cx:.1f} {hy - 0.15*h:.1f} {cx + 0.08*h:.1f} {hy - 0.12*h:.1f} L{cx + 0.09*h:.1f} {hy:.1f} Z' "
                 f"fill='#2fb5a8' stroke='{INK}' stroke-width='{lw:.1f}' stroke-linejoin='round'/>")
        p.append(f"<rect x='{cx - 0.088*h:.1f}' y='{hy - 0.04*h:.1f}' width='{0.176*h:.1f}' height='{0.03*h:.1f}' fill='#ff6fa5' stroke='{INK}' stroke-width='{lw*0.7:.1f}'/>")
        fx, fy = cx + 0.065 * h, hy - 0.03 * h
        for a in range(0, 360, 72):
            p.append(f"<circle cx='{fx + math.cos(math.radians(a))*0.022*h:.1f}' cy='{fy + math.sin(math.radians(a))*0.022*h:.1f}' r='{0.017*h:.1f}' fill='#ffd23f' stroke='{INK}' stroke-width='{lw*0.6:.1f}'/>")
        p.append(f"<circle cx='{fx:.1f}' cy='{fy:.1f}' r='{0.014*h:.1f}' fill='#ff8a2a' stroke='{INK}' stroke-width='{lw*0.6:.1f}'/>")
    else:
        p.append(f"<ellipse cx='{cx:.1f}' cy='{hy:.1f}' rx='{0.15*h:.1f}' ry='{0.03*h:.1f}' fill='#2a2a35' stroke='{INK}' stroke-width='{lw:.1f}'/>")
        p.append(f"<rect x='{cx - 0.09*h:.1f}' y='{hy - 0.16*h:.1f}' width='{0.18*h:.1f}' height='{0.16*h:.1f}' rx='{0.01*h:.1f}' fill='#2a2a35' stroke='{INK}' stroke-width='{lw:.1f}'/>")
        p.append(f"<rect x='{cx - 0.09*h:.1f}' y='{hy - 0.05*h:.1f}' width='{0.18*h:.1f}' height='{0.03*h:.1f}' fill='#e53b3b'/>")
    return "".join(p)


def frame(t):
    s, X = cam(t)
    sun = seg(t, 6.2, 7.0)
    wx = lambda x: X + s * x
    sky_top = mix("#7d9cc9", "#2f8de4", sun); sky_mid = mix("#b9cbe6", "#7cc6ff", sun); sky_low = mix("#e4ecf7", "#d9f1ff", sun)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{sky_top}'/>"
            f"<stop offset='0.6' stop-color='{sky_mid}'/><stop offset='1' stop-color='{sky_low}'/></linearGradient>"
            f"<radialGradient id='glow'><stop offset='0' stop-color='#fff8d0' stop-opacity='{0.9*sun:.3f}'/>"
            f"<stop offset='0.5' stop-color='#fff1a8' stop-opacity='{0.45*sun:.3f}'/><stop offset='1' stop-color='#fff1a8' stop-opacity='0'/></radialGradient>")
    o = [f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # Sol que asoma en la revelación
    sx, sy = 950, lerp(1250, 1030, sun)
    if sun > 0:
        o.append(f"<circle cx='{sx}' cy='{sy:.0f}' r='260' fill='url(#glow)'/>")
        o.append(f"<circle cx='{sx}' cy='{sy:.0f}' r='{70*sun:.0f}' fill='#ffe066' stroke='{INK}' stroke-width='7'/>")
    # nubes que pasan
    cloud_c = mix("#eef3fa", "#ffffff", sun)
    for i, (cx, cy, sc) in enumerate(((150, 330, 1.3), (760, 560, 1.0), (420, 820, 0.8))):
        dx = ((t * (18 + 8 * i) + cx) % 1500) - 250
        o.append(f"<g transform='translate({dx:.0f},{cy}) scale({sc})'><path d='M0 50 Q10 0 70 10 Q100 -35 160 0 Q220 -20 240 40 Q260 75 210 80 L30 80 Q-15 80 0 50 Z' "
                 f"fill='{cloud_c}' stroke='{INK}' stroke-width='6' stroke-linejoin='round' opacity='0.95'/></g>")
    # montañas lejanas (pantalla)
    m1 = mix("#8fa8cc", "#7fb0e0", sun)
    o.append(f"<path d='M-20 1500 L180 1180 L330 1380 L520 1120 L720 1400 L880 1220 L1100 1480 L1100 1820 L-20 1820 Z' fill='{m1}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for (px, py) in ((180, 1180), (520, 1120), (880, 1220)):
        o.append(f"<path d='M{px-60} {py+95} L{px} {py} L{px+60} {py+95} Q{px+20} {py+75} {px} {py+100} Q{px-20} {py+75} {px-60} {py+95} Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # colina de nieve media
    o.append(f"<path d='M-20 1640 Q250 1540 560 1620 T1100 1590 L1100 1920 L-20 1920 Z' fill='{mix('#dbe7f5', '#e8f4ff', sun)}' stroke='{INK}' stroke-width='{LW}'/>")
    # suelo
    o.append(f"<path d='M-20 {GROUND - 40} Q300 {GROUND - 60} 560 {GROUND - 38} T1100 {GROUND - 46} L1100 1940 L-20 1940 Z' fill='#f4f9ff' stroke='{INK}' stroke-width='{LW}'/>")
    # rayos detrás de la gigante
    gcx = wx(G_X); gh = H_GIANT * s; gcy = GROUND - gh * 0.55
    if sun > 0 and gcx > -400:
        rays = []
        for k in range(14):
            a = math.radians(k * 360 / 14 + t * 12)
            a2 = a + math.radians(9)
            R = 900 * sun
            rays.append(f"M{gcx:.0f} {gcy:.0f} L{gcx + math.cos(a)*R:.0f} {gcy + math.sin(a)*R:.0f} L{gcx + math.cos(a2)*R:.0f} {gcy + math.sin(a2)*R:.0f} Z")
        o.append(f"<path d='{' '.join(rays)}' fill='#fff6b0' opacity='{0.35*sun:.2f}'/>")
    # árboles y casa del mundo (se ven al alejarse)
    for (px, ph) in ((-11600, 3600), (4100, 3100), (-520, 880), (420, 640)):
        h = ph * s; cxp = wx(px)
        if -h < cxp < W + h:
            o.append(pine(cxp, GROUND, h, max(2.5, min(LW, h / 60))))
    hh = 2300 * s; hxp = wx(2150)
    if hxp - hh < W:
        o.append(house(hxp, GROUND, hh, max(2.5, min(LW, hh / 40))))
    # gigante
    if gcx + H_GIANT * s * 0.5 > -50:
        o.append(snowman(gcx, GROUND, gh, t, giant=True, look=(0.6, 0.3), wave=18 * math.sin(t * 2.2)))
    # muñeco normal: entra dando saltitos
    kin = seg(t, 0, 1.6)
    hop = abs(math.sin(kin * math.pi * 3)) * 70 * (1 - kin) if t < 1.6 else 0
    look = (lerp(0.0, -1.0, seg(t, 3.9, 4.6)), lerp(0.2, -0.8, seg(t, 3.9, 4.6)))
    sm_x = wx(0) + lerp(320, 0, kin) * s
    o.append(snowman(sm_x, GROUND, H_SMALL * s, t, giant=False, look=look,
                     wave=lerp(10, 40, 0.5 + 0.5 * math.sin(t * 5)) if t < 4.3 else 10, hop=hop * s))
    # copos de nieve
    fall = 1 - 0.7 * sun
    for fx, fy, fr, sp, ph in FLAKES:
        yy = (fy + t * sp) % (H + 40) - 20
        xx = fx + 25 * math.sin(t * 1.3 + ph)
        o.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{fr:.1f}' fill='#ffffff' opacity='{0.85*fall:.2f}'/>")
    # destellos alrededor de la gigante
    if sun > 0:
        for (dx, dy, ph) in SPARK:
            a = sun * clamp(0.5 + 0.5 * math.sin(t * 7 + ph * 3))
            px = gcx + dx * gh * 0.4; py = GROUND - dy * gh
            r = 16 * a + 4
            o.append(f"<path d='M{px:.0f} {py - r*2:.0f} L{px + r*0.4:.0f} {py - r*0.4:.0f} L{px + r*2:.0f} {py:.0f} L{px + r*0.4:.0f} {py + r*0.4:.0f} "
                     f"L{px:.0f} {py + r*2:.0f} L{px - r*0.4:.0f} {py + r*0.4:.0f} L{px - r*2:.0f} {py:.0f} L{px - r*0.4:.0f} {py - r*0.4:.0f} Z' fill='#fffbe0' opacity='{a:.2f}'/>")
    cuerpo = "".join(o)
    z = 1 + 0.07 * seg(t, 6.5, 10)
    cuerpo = zoom(540, 1450, z, cuerpo)
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")

