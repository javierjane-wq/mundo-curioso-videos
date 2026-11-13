"""2026-11-13-c2 · Física: en la cima del Everest el agua hierve a unos 70 °C (menos presión del aire).

Un cazo simpático llega dando saltitos a la cumbre nevada, se enciende el hornillo, el termómetro
sube… y el agua rompe a hervir mucho antes de llegar arriba (marca gris = 100 °C a nivel del mar).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 7.5   # el agua rompe a hervir con el termómetro a media altura
MUSICA = 7

rng = np.random.default_rng(1113)
SNOW = [(rng.uniform(0, W), rng.uniform(820, 1920), rng.uniform(3, 7), rng.uniform(160, 320), rng.uniform(0, 6.28)) for _ in range(55)]
BUBBLES = [(rng.uniform(-140, 140), rng.uniform(-18, 18), rng.uniform(7, 18), rng.uniform(0.35, 0.8), rng.uniform(0, 1)) for _ in range(34)]
PUFFS = [(rng.uniform(-130, 130), rng.uniform(0, 1), rng.uniform(40, 80), rng.uniform(-40, 40)) for _ in range(14)]
FLAG_COLS = ["#3a7bd5", "#ffffff", "#e8483b", "#3fae5a", "#ffd23f"]

PX, PY = 540, 1215        # centro del borde del cazo


def montanas(t, k):
    s = []
    far = mix("#6f7fc7", "#8a74c9", k)
    snow_far = mix("#eef4ff", "#fff1e0", k)
    # cordillera lejana
    s.append(f"<path d='M-20 1420 L110 1170 L210 1260 L330 1090 L450 1300 L560 1200 L690 1310 L820 1110 L940 1240 L1100 1150 L1100 1500 L-20 1500 Z' fill='{far}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for p in ("M70 1248 L110 1170 L150 1225 L130 1212 L110 1236 L90 1220 Z",
              "M282 1180 L330 1090 L382 1170 L356 1158 L334 1182 L308 1162 Z",
              "M770 1200 L820 1110 L868 1185 L842 1172 L820 1196 L796 1178 Z",
              "M1050 1185 L1100 1150 L1100 1215 L1078 1198 Z"):
        s.append(f"<path d='{p}' fill='{snow_far}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # mar de nubes
    cl = mix("#ffffff", "#ffe9d6", k)
    for i, (cx, cy, sc) in enumerate([(120, 1400, 1.4), (460, 1430, 1.7), (820, 1395, 1.5), (1080, 1430, 1.3), (300, 1470, 1.2), (700, 1480, 1.3)]):
        dx = ((t * (10 + 4 * i)) % 300) - 150
        s.append(f"<g transform='translate({cx + dx:.0f},{cy}) scale({sc})'>"
                 f"<path d='M-150 40 Q-140 -20 -80 -10 Q-60 -60 0 -40 Q40 -80 90 -30 Q150 -30 150 40 Z' fill='{cl}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/></g>")
    s.append(f"<rect x='-20' y='1470' width='1120' height='400' fill='{cl}'/>")
    # cumbre principal
    rock = mix("#5b6478", "#6d5c78", k)
    s.append(f"<path d='M-20 1940 L-20 1810 L180 1710 L330 1665 L540 1648 L760 1662 L930 1715 L1100 1810 L1100 1940 Z' fill='{rock}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    sn = mix("#f6faff", "#fff4e8", k); sh = mix("#c9d8f0", "#e9cfc6", k)
    s.append(f"<path d='M110 1745 L180 1710 L330 1665 L540 1648 L760 1662 L930 1715 L1010 1755 L950 1780 L900 1750 L830 1810 L760 1765 L680 1840 L600 1780 L520 1850 L440 1785 L360 1840 L290 1780 L210 1820 L160 1770 Z' fill='{sn}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M600 1780 L680 1840 L760 1765 L700 1750 Z' fill='{sh}'/>")
    s.append(f"<path d='M290 1780 L360 1840 L440 1785 L380 1762 Z' fill='{sh}'/>")
    for rx, ry, rr in [(130, 1850, 44), (900, 1830, 52), (520, 1880, 36), (1010, 1900, 30)]:
        s.append(f"<ellipse cx='{rx}' cy='{ry}' rx='{rr}' ry='{rr*0.55:.0f}' fill='{mix('#454c5e', '#56485f', k)}' stroke='{INK}' stroke-width='6'/>")
    return "".join(s)


def banderas(t):
    """Cuerda con banderitas de colores (sin texto) que ondean con el viento."""
    s = []
    x0, y0, x1, y1, sag = 930, 1380, 120, 1750, 110
    s.append(f"<rect x='{x0-9}' y='{y0-20}' width='18' height='{1700-y0+20}' rx='6' fill='#8a5a3c' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<circle cx='{x0}' cy='{y0-24}' r='13' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    s.append(f"<path d='M{x0} {y0} Q{cx} {cy} {x1} {y1}' fill='none' stroke='{INK}' stroke-width='5'/>")
    n = 10
    for i in range(1, n):
        u = i / n
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1
        sk = 12 * math.sin(t * 7 + i * 0.9)
        col = FLAG_COLS[i % len(FLAG_COLS)]
        s.append(f"<g transform='translate({bx:.1f},{by:.1f}) skewX({sk:.1f})'>"
                 f"<path d='M-24 0 L24 0 L22 52 L-22 54 Z' fill='{col}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/></g>")
    return "".join(s)


def hornillo(t):
    s = []
    # bombona de gas
    s.append(f"<rect x='455' y='1545' width='170' height='120' rx='34' fill='#2f6fd6' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='475' y='1580' width='130' height='22' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<rect x='500' y='1512' width='80' height='36' rx='8' fill='#9aa3ad' stroke='{INK}' stroke-width='7'/>")
    # patas de apoyo
    for x1, x2 in ((470, 420), (610, 660)):
        s.append(f"<line x1='{x1}' y1='1518' x2='{x2}' y2='1432' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>")
        s.append(f"<line x1='{x1}' y1='1518' x2='{x2}' y2='1432' stroke='#c9ced6' stroke-width='6' stroke-linecap='round'/>")
    s.append(f"<rect x='495' y='1494' width='90' height='22' rx='8' fill='#5b6270' stroke='{INK}' stroke-width='6'/>")
    # llama
    on = rebote(t, 2.3, 0.5)
    if on > 0:
        big = 1 + 0.35 * seg(t, 7.3, 7.7)
        fl = 1 + 0.12 * math.sin(t * 31) + 0.08 * math.sin(t * 17)
        sc = on * fl * big
        s.append(f"<g transform='translate(540,1498) scale({1.05*big:.3f},{sc:.3f})'>"
                 f"<path d='M-46 0 Q-50 -22 -30 -36 Q-26 -14 -14 -20 Q-14 -46 0 -58 Q14 -46 14 -20 Q26 -14 30 -36 Q50 -22 46 0 Z' fill='#4fa8ff' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
                 f"<path d='M-24 0 Q-22 -16 -10 -22 Q-4 -10 0 -34 Q6 -10 10 -22 Q22 -16 24 0 Z' fill='#bfe8ff'/></g>")
    return "".join(s)


def cazo(t):
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.35)
    # entrada dando saltitos desde la derecha
    ent = seg(t, 0, 1.9)
    x = lerp(620, 0, ent)
    hop = -abs(math.sin(t * 8.2)) * 70 * (1 - ent) if t < 1.9 else 0
    land = clamp((t - 1.9) / 0.35) if t >= 1.9 else 0
    squash = 1 - 0.12 * math.sin(math.pi * land) if 0 < land < 1 else 1.0
    jig = 4 * math.sin(t * 40) * seg(t, 5.2, 7.4) * 0.5 + 6 * math.sin(t * 46) * rev
    s = [f"<g transform='translate({x + jig:.1f},{hop:.1f}) translate({PX},1420) scale({1/squash:.3f},{squash:.3f}) translate({-PX},-1420)'>"]
    body = mix("#ff5b4a", "#ff3d2e", rev)
    # sombra de calor
    s.append(f"<ellipse cx='{PX}' cy='1428' rx='190' ry='16' fill='#000' opacity='0.18'/>")
    # asas
    for sx in (-1, 1):
        s.append(f"<path d='M{PX + sx*178} 1250 Q{PX + sx*250} 1250 {PX + sx*246} 1300 Q{PX + sx*240} 1330 {PX + sx*176} 1320' fill='none' stroke='{INK}' stroke-width='26' stroke-linecap='round'/>")
        s.append(f"<path d='M{PX + sx*178} 1250 Q{PX + sx*250} 1250 {PX + sx*246} 1300 Q{PX + sx*240} 1330 {PX + sx*176} 1320' fill='none' stroke='#2b2b33' stroke-width='12' stroke-linecap='round'/>")
    # cuerpo
    s.append(f"<path d='M{PX-185} {PY} L{PX-170} 1385 Q{PX-165} 1425 {PX-120} 1425 L{PX+120} 1425 Q{PX+165} 1425 {PX+170} 1385 L{PX+185} {PY} Z' fill='{body}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M{PX-150} 1250 L{PX-142} 1370' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='0.45'/>")
    s.append(f"<path d='M{PX-172} 1395 Q{PX} 1410 {PX+172} 1395' fill='none' stroke='{mix('#c93a2c', '#b52a1f', rev)}' stroke-width='10'/>")
    # borde y agua
    s.append(f"<ellipse cx='{PX}' cy='{PY}' rx='196' ry='40' fill='#d9dee6' stroke='{INK}' stroke-width='{LW}'/>")
    water = mix("#5ec8ff", "#8fe0ff", rev)
    s.append(f"<ellipse cx='{PX}' cy='{PY+4}' rx='170' ry='28' fill='{water}' stroke='{INK}' stroke-width='5'/>")
    # burbujas: empiezan tímidas y en la revelación el agua hierve con fuerza
    k = 0.35 * seg(t, 4.9, 7.0) + 0.65 * seg(t, REVELACION - 0.1, REVELACION + 0.4)
    nb = int(len(BUBBLES) * k)
    for bx, by, br, per, ph in BUBBLES[:nb]:
        u = ((t / per) + ph) % 1.0
        r = br * (0.4 + 0.8 * u) * (0.7 + 0.5 * rev)
        a = 1 - u ** 3
        s.append(f"<circle cx='{PX + bx:.0f}' cy='{PY + 4 + by - 6*u:.0f}' r='{r:.1f}' fill='#e9fbff' stroke='{INK}' stroke-width='4' opacity='{a:.2f}'/>")
    # cara
    blink = 0.12 if (t % 2.9) < 0.12 and t < 7.3 else 1.0
    eye_r = 34 * (1 + 0.25 * rev)
    look_x = lerp(0, 10, seg(t, 3.0, 3.8)) * (1 - rev)
    look_y = lerp(0, -12, seg(t, 3.0, 3.8)) * (1 - rev)
    for ex in (-62, 62):
        s.append(f"<g transform='translate({PX + ex},1295) scale(1,{blink})'>"
                 f"<ellipse rx='{eye_r:.1f}' ry='{eye_r*1.1:.1f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{look_x:.1f}' cy='{look_y:.1f}' r='{eye_r*0.5:.1f}' fill='{INK}'/>"
                 f"<circle cx='{look_x - 6:.1f}' cy='{look_y - 7:.1f}' r='{eye_r*0.18:.1f}' fill='#fff'/></g>")
        # cejas
        by_ = 1295 - eye_r * 1.1 - 14 - 16 * rev
        s.append(f"<path d='M{PX + ex - 24} {by_ + 6:.0f} Q{PX + ex} {by_ - 6 - 6*rev:.0f} {PX + ex + 24} {by_ + 6:.0f}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # mofletes
    for cx_ in (-112, 112):
        s.append(f"<ellipse cx='{PX + cx_}' cy='1345' rx='24' ry='14' fill='#ffb3a8' opacity='{0.6 + 0.4*rev:.2f}'/>")
    if rev < 0.5:
        s.append(f"<path d='M{PX-30} 1350 Q{PX} 1378 {PX+30} 1350' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    else:
        mo = 18 + 4 * math.sin(t * 9)
        s.append(f"<ellipse cx='{PX}' cy='1362' rx='{mo*0.8:.1f}' ry='{mo:.1f}' fill='#7a1f1a' stroke='{INK}' stroke-width='6'/>")
    s.append("</g>")
    return "".join(s), x + jig, hop


def termometro(t, dx, dy):
    """Termómetro de cristal metido en el agua. Marca gris arriba = 100 °C; el líquido para a ~70 %."""
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.35)
    app = seg(t, 2.0, 2.5)
    if app <= 0:
        return ""
    Lmax = 270
    lvl = lerp(10, 185, seg(t, 2.5, 7.3))
    s = [f"<g transform='translate({PX + 70 + dx:.1f},{PY + 6 + dy + lerp(-80, 0, app):.1f}) rotate(18)' opacity='{app:.2f}'>"]
    s.append(f"<rect x='-22' y='{-Lmax}' width='44' height='{Lmax + 10}' rx='22' fill='#eaf6ff' stroke='{INK}' stroke-width='{LW}'/>")
    # marcas
    for i in range(1, 9):
        yy = -i * 30
        s.append(f"<line x1='8' y1='{yy}' x2='18' y2='{yy}' stroke='#8aa0b8' stroke-width='4'/>")
    # meta de 100 °C (gris discontinua)
    s.append(f"<line x1='-30' y1='-240' x2='30' y2='-240' stroke='#9aa3ad' stroke-width='8' stroke-dasharray='10 7' stroke-linecap='round'/>")
    col = mix("#ff3b3b", "#ff2a2a", rev)
    s.append(f"<rect x='-9' y='{-lvl:.1f}' width='18' height='{lvl + 4:.1f}' rx='9' fill='{col}'/>")
    if rev > 0:
        pr = 26 + 6 * math.sin(t * 10)
        s.append(f"<circle cx='0' cy='{-lvl:.1f}' r='{pr * rev:.1f}' fill='none' stroke='#ffd23f' stroke-width='8'/>")
        s.append(f"<line x1='-36' y1='{-lvl:.1f}' x2='36' y2='{-lvl:.1f}' stroke='#ffd23f' stroke-width='9' stroke-linecap='round' opacity='{rev:.2f}'/>")
    s.append(f"<rect x='-14' y='{-Lmax + 10}' width='8' height='{Lmax - 40}' rx='4' fill='#fff' opacity='0.8'/>")
    s.append("</g>")
    # ondas donde entra en el agua
    for i in range(2):
        u = ((t * 0.9) + i * 0.5) % 1.0
        s.append(f"<ellipse cx='{PX + 70 + dx:.0f}' cy='{PY + 8 + dy:.0f}' rx='{14 + 30*u:.0f}' ry='{5 + 9*u:.0f}' fill='none' stroke='#ffffff' stroke-width='4' opacity='{(1-u)*0.8*app:.2f}'/>")
    return "".join(s)


def vapor(t, dx, dy):
    s = []
    k = 0.25 * seg(t, 3.5, 6.5) + 0.75 * seg(t, REVELACION - 0.1, REVELACION + 0.6)
    if k <= 0:
        return ""
    for i in range(4):
        u = ((t * 0.45) + i * 0.25) % 1.0
        x0 = PX - 110 + i * 70 + dx
        y0 = PY - 20 - u * 280 + dy
        w = 20 * math.sin(t * 3 + i)
        s.append(f"<path d='M{x0:.0f} {y0 + 90:.0f} q{18 + w:.0f} -30 0 -60 q{-18 - w:.0f} -30 0 -60' fill='none' stroke='#ffffff' stroke-width='{14 + 6*k:.0f}' stroke-linecap='round' opacity='{(1-u) * 0.75 * k:.2f}'/>")
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.6)
    if rev > 0:
        for ox, ph, r, drift in PUFFS:
            u = ((t - REVELACION) * 0.55 + ph) % 1.0
            yy = PY - 30 - u * 420 + dy
            s.append(f"<circle cx='{PX + ox + drift*u + dx:.0f}' cy='{yy:.0f}' r='{r*(0.6+0.8*u):.0f}' fill='#ffffff' stroke='{INK}' stroke-width='4' opacity='{(1-u)*0.85*rev:.2f}'/>")
    return "".join(s)


def frame(t):
    rev = seg(t, REVELACION - 0.1, REVELACION + 0.5)
    top = mix("#1c3f99", "#2a2d8f", rev); mid = mix("#3d7fe0", "#7a5cd6", rev); low = mix("#a9dcff", "#ffc9a8", rev)
    defs = (f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='sun'><stop offset='0' stop-color='#fffbe8' stop-opacity='0.9'/><stop offset='1' stop-color='#fff3c4' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='hot'><stop offset='0' stop-color='#fff1a8' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.45' stop-color='#ffb347' stop-opacity='{0.6*rev:.3f}'/><stop offset='1' stop-color='#ff7a45' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.16 * seg(t, REVELACION, 9.6)
    c = []
    # Sol pequeño y lejano
    c.append(f"<circle cx='900' cy='900' r='130' fill='url(#sun)'/>")
    c.append(f"<circle cx='900' cy='900' r='46' fill='#fffbe8' stroke='#ffe08a' stroke-width='7'/>")
    c.append(montanas(t, rev))
    c.append(banderas(t))
    # resplandor y rayos en la revelación
    if rev > 0:
        c.append(f"<circle cx='{PX}' cy='1250' r='{lerp(200, 620, rev):.0f}' fill='url(#hot)'/>")
        for i in range(12):
            a = i * 30 + t * 25
            c.append(f"<g transform='translate({PX},1250) rotate({a:.1f})'><path d='M0 -260 L18 -{260 + 120*rev:.0f} L-18 -{260 + 120*rev:.0f} Z' fill='#fff3b0' opacity='{0.55*rev:.2f}'/></g>")
    c.append(hornillo(t))
    pot, dx, dy = cazo(t)
    c.append(pot)
    c.append(termometro(t, dx, dy))
    c.append(vapor(t, dx, dy))
    # copos de nieve llevados por el viento
    for sx, sy, sr, sp, ph in SNOW:
        xx = (sx - t * sp) % (W + 80) - 40
        yy = sy + 18 * math.sin(t * 2 + ph)
        c.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{sr:.1f}' fill='#ffffff' opacity='0.8'/>")
    s.append(zoom(PX, 1250, z, "".join(c)))
    s.append("</svg>")
    return "".join(s)
