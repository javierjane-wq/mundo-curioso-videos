"""El Panteón de Roma: dentro cabe una esfera perfecta.

Datos: el Panteón actual lo construyó el emperador Adriano hacia los años 118-128 d. C. (Britannica;
UW «The Pantheon»: ladrillos fechados en 120-128). La altura del suelo al óculo (~43,3 m) es igual
al diámetro interior de la cúpula, así que dentro cabría una esfera perfecta (MIT 21H.405 «The Dome»;
UW). El óculo mide unos 8-9 m.

Escena: vista frontal del Panteón en su plaza (pórtico de columnas con frontón y la cúpula detrás).
Dos turistas llegan andando. El edificio se vuelve «de rayos X» y se ve el corte: la cúpula con sus
casetones, el óculo y el rayo de sol. Una bola empieza a hincharse en el centro y crece hasta
tocar a la vez el suelo y la cúpula. Revelación: la bola se vuelve dorada, destello, flechas de alto
y ancho y zoom.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, pulso, rebote, zoom

DUR = 10.0
REVELACION = 7.45   # la bola encaja: golpe musical
MUSICA = 2

CX, R = 540, 300          # centro y radio interior
YS, YF = 1460, 1760       # arranque de la cúpula y suelo
WALL = 50
XL, XR = CX - R - WALL, CX + R + WALL          # 190 … 890
DOME_Y, DOME_RY = 1430, 300                    # cúpula exterior (más chata)
OCU = 60                                        # medio óculo

rng = np.random.default_rng(2411)
SPARKS = [(rng.uniform(0, 6.28), rng.uniform(1.05, 1.45), rng.uniform(0, 6.28), rng.uniform(10, 22)) for _ in range(18)]
COBBLES = [(rng.uniform(0, W), rng.uniform(1790, 1910), rng.uniform(14, 26)) for _ in range(60)]
DUSTS = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(0, 6.28)) for _ in range(22)]

STONE = "#ead7b0"; STONE_D = "#cfb487"; LEAD = "#b9b4ab"; LEAD_D = "#9a948a"
SECTION = "#b89b72"


def nube(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M0 50 Q-10 0 50 6 Q80 -40 140 -6 Q190 -30 220 20 Q270 24 260 50 Z' fill='{col}' "
            f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def pino(x, y, sc):
    """Pino piñonero romano: tronco fino y copa ancha como un paraguas."""
    return (f"<g transform='translate({x},{y}) scale({sc})'>"
            f"<path d='M-8 0 Q-4 -120 -14 -210 L8 -210 Q6 -120 10 0 Z' fill='#7a4e2c' stroke='{INK}' stroke-width='6'/>"
            f"<path d='M-150 -200 Q-150 -270 -60 -282 Q0 -320 70 -285 Q160 -275 150 -205 Q60 -180 0 -192 Q-70 -180 -150 -200 Z' "
            f"fill='#3f8a3a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
            f"<path d='M-100 -230 Q-40 -262 20 -250' fill='none' stroke='#5fae4f' stroke-width='10' stroke-linecap='round'/></g>")


def paloma(x, y, sc, t, ph):
    a = 22 * math.sin(t * 14 + ph)
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M-34 {-a*0.6:.1f} Q-16 {-a - 6:.1f} 0 0 Q16 {-a - 6:.1f} 34 {-a*0.6:.1f}' fill='none' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>"
            f"<path d='M-34 {-a*0.6:.1f} Q-16 {-a - 6:.1f} 0 0 Q16 {-a - 6:.1f} 34 {-a*0.6:.1f}' fill='none' stroke='#8c95a6' stroke-width='6' stroke-linecap='round'/>"
            f"<ellipse cx='0' cy='2' rx='12' ry='8' fill='#8c95a6' stroke='{INK}' stroke-width='5'/></g>")


def turista(x, y, shirt, t, ph, walk, up, jump, flip=1):
    """Turista original y redondito: camiseta de color, gorra, ojos grandes que parpadean."""
    jy = -abs(math.sin((t - 7.45) * 9)) * 26 * jump
    step = math.sin(t * 11 + ph) * walk
    blink = 0.12 if ((t + ph) % 2.9) < 0.11 else 1.0
    arm = lerp(18, -150, up * jump) if jump > 0 else 18 + 14 * step
    g = [f"<g transform='translate({x:.1f},{y + jy:.1f}) scale({flip},1)'>"]
    g.append(f"<ellipse cx='0' cy='{-jy + 2:.1f}' rx='34' ry='8' fill='#000' opacity='0.18'/>")
    for s in (-1, 1):
        g.append(f"<line x1='{s*10}' y1='-44' x2='{s*10 + s*step*10:.1f}' y2='-4' stroke='{INK}' stroke-width='13' stroke-linecap='round'/>"
                 f"<line x1='{s*10}' y1='-44' x2='{s*10 + s*step*10:.1f}' y2='-4' stroke='#3c5aa6' stroke-width='6' stroke-linecap='round'/>")
    for s in (-1, 1):
        aa = arm if s == 1 else (lerp(-18, 150, up * jump) if jump > 0 else -18 - 14 * step)
        g.append(f"<g transform='translate({s*22},-88) rotate({aa:.1f})'><line x1='0' y1='0' x2='0' y2='34' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
                 f"<line x1='0' y1='0' x2='0' y2='34' stroke='#f2c39a' stroke-width='5' stroke-linecap='round'/></g>")
    g.append(f"<rect x='-26' y='-100' width='52' height='60' rx='18' fill='{shirt}' stroke='{INK}' stroke-width='6'/>")
    hy = -128 - 4 * up
    g.append(f"<circle cx='0' cy='{hy:.1f}' r='28' fill='#f2c39a' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='M-29 {hy - 6:.1f} Q0 {hy - 46:.1f} 29 {hy - 6:.1f} Z' fill='{mix(shirt, '#ffffff', 0.25)}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
             f"<path d='M14 {hy - 8:.1f} L44 {hy - 6:.1f}' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    ey = hy + 4 - 7 * up
    for ex in (-10, 10):
        g.append(f"<g transform='translate({ex + 3},{ey:.1f}) scale(1,{blink})'><ellipse rx='6.5' ry='8' fill='#fff' stroke='{INK}' stroke-width='3'/>"
                 f"<circle cx='1' cy='{-2 - 2*up:.1f}' r='4' fill='{INK}'/></g>")
    if jump > 0.3:
        g.append(f"<ellipse cx='3' cy='{hy + 18:.1f}' rx='7' ry='8' fill='#7a2e2e' stroke='{INK}' stroke-width='3'/>")
    else:
        g.append(f"<path d='M-6 {hy + 15:.1f} Q3 {hy + 22:.1f} 12 {hy + 15:.1f}' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def interior(t, beam_on):
    """Corte del Panteón: pared del fondo con nichos, cúpula con casetones, óculo y rayo de sol."""
    s = []
    void = f"M{CX - R} {YF} L{CX - R} {YS} A{R} {R} 0 0 1 {CX + R} {YS} L{CX + R} {YF} Z"
    s.append(f"<path d='{void}' fill='#f1e3c4'/>")
    # banda ática y cornisa
    s.append(f"<rect x='{CX - R}' y='{YS - 6}' width='{2*R}' height='16' fill='#d9c39b' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<rect x='{CX - R}' y='{YS + 60}' width='{2*R}' height='12' fill='#d9c39b' stroke='{INK}' stroke-width='5'/>")
    for th in range(-75, 80, 15):
        x = CX + R * math.sin(math.radians(th)); w = 16 * math.cos(math.radians(th))
        s.append(f"<rect x='{x - w:.1f}' y='{YS + 18}' width='{2*w:.1f}' height='34' fill='#e6d2ac' stroke='{INK}' stroke-width='3'/>")
    # nichos y columnas del piso bajo
    for th in (-60, -30, 0, 30, 60):
        c = math.cos(math.radians(th)); x = CX + R * math.sin(math.radians(th)); w = 46 * c
        s.append(f"<path d='M{x - w:.1f} {YF} L{x - w:.1f} {YF - 150} Q{x:.1f} {YF - 205} {x + w:.1f} {YF - 150} L{x + w:.1f} {YF} Z' "
                 f"fill='#c9ae86' stroke='{INK}' stroke-width='5'/>")
        for cc in (-0.55, 0.55):
            s.append(f"<rect x='{x + cc*w - 6*c:.1f}' y='{YF - 140}' width='{12*c:.1f}' height='140' fill='#f6ead2' stroke='{INK}' stroke-width='3'/>")
    # casetones de la cúpula (filas que se estrechan hacia arriba)
    for i, ph in enumerate((8, 22, 36, 50)):
        p1, p2 = math.radians(ph), math.radians(ph + 11)
        ya, yb = YS - R * math.sin(p1) - 6, YS - R * math.sin(p2) + 6
        rr = R * math.cos((p1 + p2) / 2)
        for th in range(-78, 80, 13):
            ta, tb = math.radians(th - 4.5), math.radians(th + 4.5)
            xa, xb = CX + rr * math.sin(ta), CX + rr * math.sin(tb)
            if xb - xa < 4: continue
            s.append(f"<rect x='{xa:.1f}' y='{yb:.1f}' width='{xb - xa:.1f}' height='{ya - yb:.1f}' rx='3' fill='#d8c19a' stroke='#a88e66' stroke-width='3'/>")
    # suelo interior
    s.append(f"<rect x='{CX - R}' y='{YF - 8}' width='{2*R}' height='8' fill='#b9a07a'/>")
    # rayo de sol desde el óculo
    if beam_on > 0:
        sw = 18 * math.sin(t * 0.9)
        fx = CX - 190 + sw
        s.append(f"<path d='M{CX - OCU + 8} {YS - R + 4} L{CX + OCU - 8} {YS - R + 4} L{fx + 70:.1f} {YF - 4} L{fx - 70:.1f} {YF - 4} Z' "
                 f"fill='#fff6c8' opacity='{0.45*beam_on:.2f}'/>")
        s.append(f"<ellipse cx='{fx:.1f}' cy='{YF - 6}' rx='74' ry='14' fill='#fff2a6' opacity='{0.8*beam_on:.2f}'/>")
        for dx, dy, ph in DUSTS:
            k = (dy + t * 0.08) % 1
            px = lerp(CX, fx, k) + dx * lerp(40, 60, k)
            py = lerp(YS - R + 10, YF - 20, k)
            s.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='3.5' fill='#fff' opacity='{beam_on*(0.5 + 0.4*math.sin(t*3 + ph)):.2f}'/>")
    return "".join(s)


def seccion():
    """Muro y cúpula cortados (grosor de piedra)."""
    outer = f"M{XL} {YF} L{XL} {DOME_Y} A{XR - CX} {DOME_RY} 0 0 1 {XR} {DOME_Y} L{XR} {YF} Z"
    void = f"M{CX - R} {YF} L{CX - R} {YS} A{R} {R} 0 0 1 {CX + R} {YS} L{CX + R} {YF} Z"
    s = [f"<path d='{outer} {void}' fill='{SECTION}' fill-rule='evenodd' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    # óculo abierto al cielo
    top_out = DOME_Y - DOME_RY
    s.append(f"<rect x='{CX - OCU}' y='{top_out - 6}' width='{2*OCU}' height='{YS - R - top_out + 14}' fill='url(#sky)'/>")
    s.append(f"<line x1='{CX - OCU}' y1='{top_out + 2}' x2='{CX - OCU}' y2='{YS - R + 7}' stroke='{INK}' stroke-width='{LW}'/>"
             f"<line x1='{CX + OCU}' y1='{top_out + 2}' x2='{CX + OCU}' y2='{YS - R + 7}' stroke='{INK}' stroke-width='{LW}'/>")
    # textura de piedra en el corte
    for yy in range(1500, 1750, 46):
        s.append(f"<line x1='{XL + 8}' y1='{yy}' x2='{CX - R - 8}' y2='{yy}' stroke='#9c7f58' stroke-width='4'/>"
                 f"<line x1='{CX + R + 8}' y1='{yy + 23}' x2='{XR - 8}' y2='{yy + 23}' stroke='#9c7f58' stroke-width='4'/>")
    return "".join(s)


def exterior():
    """Fachada: tambor, cúpula de plomo con escalones, segundo frontón y pórtico con 8 columnas."""
    s = []
    s.append(f"<path d='M{XL} {DOME_Y} A{XR - CX} {DOME_RY} 0 0 1 {XR} {DOME_Y} Z' fill='{LEAD}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M{CX - 210} {DOME_Y - DOME_RY*0.80:.0f} Q{CX} {DOME_Y - DOME_RY*0.98:.0f} {CX + 210} {DOME_Y - DOME_RY*0.80:.0f}' fill='none' stroke='{LEAD_D}' stroke-width='7'/>")
    s.append(f"<path d='M{XL + 10} {DOME_Y - 34} L{XR - 10} {DOME_Y - 34} L{XR - 30} {DOME_Y - 70} L{XL + 30} {DOME_Y - 70} Z' fill='#d8cbb5' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M{XL + 30} {DOME_Y - 70} L{XR - 30} {DOME_Y - 70} L{XR - 56} {DOME_Y - 104} L{XL + 56} {DOME_Y - 104} Z' fill='#cfc1a9' stroke='{INK}' stroke-width='6'/>")
    top = DOME_Y - DOME_RY
    s.append(f"<rect x='{CX - OCU - 12}' y='{top - 10}' width='{2*OCU + 24}' height='18' rx='6' fill='#d8cbb5' stroke='{INK}' stroke-width='6'/>")
    # tambor
    s.append(f"<rect x='{XL}' y='{DOME_Y}' width='{XR - XL}' height='{YF - DOME_Y}' fill='{STONE_D}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='{XL - 10}' y='{DOME_Y - 6}' width='{XR - XL + 20}' height='22' rx='4' fill='{STONE}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<line x1='{XL}' y1='1560' x2='{XR}' y2='1560' stroke='{INK}' stroke-width='5'/>")
    # bloque intermedio con el segundo frontón
    s.append(f"<rect x='300' y='1470' width='480' height='290' fill='{STONE}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M285 1470 L540 1388 L795 1470 Z' fill='{STONE}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # pórtico
    s.append(f"<path d='M262 1546 L540 1452 L818 1546 Z' fill='#f4e6c6' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M318 1532 L540 1474 L762 1532 Z' fill='#e2cfa6' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    s.append(f"<rect x='262' y='1546' width='556' height='44' fill='#f4e6c6' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<line x1='270' y1='1566' x2='810' y2='1566' stroke='#d2bb8f' stroke-width='5'/>")
    s.append(f"<rect x='280' y='1590' width='520' height='150' fill='#6b4a30' stroke='{INK}' stroke-width='6'/>")
    for i in range(8):
        x = 300 + i * (480 / 7)
        s.append(f"<rect x='{x - 17:.1f}' y='1602' width='34' height='138' fill='#f7ecd4' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='{x - 25:.1f}' y='1590' width='50' height='14' rx='3' fill='#f4e6c6' stroke='{INK}' stroke-width='5'/>"
                 f"<line x1='{x - 6:.1f}' y1='1610' x2='{x - 6:.1f}' y2='1734' stroke='#dccaa6' stroke-width='4'/>")
    s.append(f"<rect x='256' y='1738' width='568' height='12' fill='{STONE}' stroke='{INK}' stroke-width='5'/>"
             f"<rect x='244' y='1748' width='592' height='14' fill='{STONE_D}' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def bola(t, r, gold, wob):
    cy = YF - r
    sx = 1 + 0.035 * math.sin(t * 13) * wob; sy = 1 - 0.035 * math.sin(t * 13) * wob
    col = mix("#47b9f5", "#ffcf33", gold); dark = mix("#2a86c9", "#e89a12", gold); lite = mix("#bfe9ff", "#fff6c0", gold)
    return (f"<g transform='translate({CX},{cy:.1f}) scale({sx:.4f},{sy:.4f})'>"
            f"<circle r='{r:.1f}' fill='{col}' stroke='{INK}' stroke-width='{LW}'/>"
            f"<path d='M{-r*0.86:.1f} {r*0.18:.1f} A{r*0.88:.1f} {r*0.88:.1f} 0 0 0 {r*0.5:.1f} {r*0.82:.1f} A{r:.1f} {r:.1f} 0 0 1 {-r*0.86:.1f} {r*0.18:.1f} Z' fill='{dark}' opacity='0.55'/>"
            f"<ellipse cx='{-r*0.38:.1f}' cy='{-r*0.42:.1f}' rx='{r*0.26:.1f}' ry='{r*0.15:.1f}' fill='{lite}' transform='rotate(-35 {-r*0.38:.1f} {-r*0.42:.1f})'/>"
            f"<circle cx='{-r*0.62:.1f}' cy='{-r*0.12:.1f}' r='{r*0.05:.1f}' fill='{lite}'/></g>")


def flecha(x1, y1, x2, y2, k):
    if k <= 0: return ""
    xe, ye = lerp(x1, x2, k), lerp(y1, y2, k)
    ang = math.degrees(math.atan2(ye - y1, xe - x1))
    head = lambda x, y, a: (f"<path d='M0 0 L-30 -17 L-30 17 Z' transform='translate({x:.1f},{y:.1f}) rotate({a:.1f})' "
                            f"fill='#fff' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    return (f"<line x1='{x1}' y1='{y1}' x2='{xe:.1f}' y2='{ye:.1f}' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
            f"<line x1='{x1}' y1='{y1}' x2='{xe:.1f}' y2='{ye:.1f}' stroke='#fff' stroke-width='8' stroke-dasharray='26 14'/>"
            + head(x1, y1, ang + 180) + head(xe, ye, ang))


def frame(t):
    cut = seg(t, 2.5, 3.7)                       # rayos X: se ve el interior
    grow = seg(t, 4.7, 7.45)                     # la bola se hincha
    rev = seg(t, 7.45, 7.9)                      # revelación
    r = R * (0.06 + 0.94 * (1 - (1 - grow) ** 1.6)) if t >= 4.7 else 0
    wob = (1 - grow) * (t >= 4.7)
    sky_top = mix("#5fb8f0", "#3f8fe0", rev); sky_low = mix("#cdeeff", "#fff1c9", rev)
    defs = (f"<linearGradient id='sky' gradientUnits='userSpaceOnUse' x1='0' y1='0' x2='0' y2='{H}'>"
            f"<stop offset='0' stop-color='{sky_top}'/><stop offset='0.75' stop-color='{sky_low}'/></linearGradient>"
            f"<radialGradient id='halo'><stop offset='0.55' stop-color='#fff3a0' stop-opacity='{0.85*rev:.2f}'/>"
            f"<stop offset='1' stop-color='#ffd84a' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='sun'><stop offset='0' stop-color='#fff8d0'/><stop offset='1' stop-color='#fff8d0' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # cámara: se aleja al principio y se acerca en la revelación
    z = lerp(1.13, 1.0, seg(t, 0, 2.3)) + 0.1 * seg(t, 7.45, 8.15)
    zy = lerp(1560, YS, seg(t, 6.5, 8.0))
    body = []
    # sol y nubes
    body.append(f"<circle cx='915' cy='1005' r='150' fill='url(#sun)' opacity='0.8'/>")
    body.append(f"<g transform='rotate({t*12:.1f} 915 1005)'>" + "".join(
        f"<line x1='{915 + 78*math.cos(a):.0f}' y1='{1005 + 78*math.sin(a):.0f}' x2='{915 + 104*math.cos(a):.0f}' y2='{1005 + 104*math.sin(a):.0f}' "
        f"stroke='#ffd23f' stroke-width='10' stroke-linecap='round'/>" for a in np.linspace(0, 2*math.pi, 10, endpoint=False)) + "</g>")
    body.append(f"<circle cx='915' cy='1005' r='60' fill='#ffe066' stroke='{INK}' stroke-width='7'/>")
    for i, (cx, cy, sc) in enumerate(((120, 860, 1.1), (700, 760, 0.9), (420, 1090, 0.8))):
        dx = (t * (16 + 6*i)) % 1500 - 300
        body.append(nube((cx + dx) % 1500 - 260, cy, sc, "#ffffff"))
    # ciudad lejana y pinos
    body.append(f"<path d='M0 1560 L0 1470 L70 1470 L70 1430 L150 1430 L150 1490 L210 1490 L210 1760 L0 1760 Z' fill='#e8a46a' stroke='{INK}' stroke-width='7'/>")
    body.append(f"<path d='M1080 1530 L1080 1440 L1010 1440 L1010 1400 L960 1400 L960 1470 L880 1470 L880 1760 L1080 1760 Z' fill='#e07f5a' stroke='{INK}' stroke-width='7'/>")
    for wx, wy in ((30, 1500), (105, 1460), (30, 1580), (975, 1430), (1030, 1480), (1030, 1560), (920, 1520)):
        body.append(f"<rect x='{wx}' y='{wy}' width='26' height='38' rx='4' fill='#7a4a3a' stroke='{INK}' stroke-width='4'/>")
    body.append(pino(80, 1770, 0.9))
    body.append(pino(1000, 1770, 0.8))
    # suelo de la plaza (adoquines)
    body.append(f"<rect x='0' y='{YF}' width='{W}' height='{H - YF}' fill='#d8b98f' stroke='{INK}' stroke-width='{LW}'/>")
    for x, y, rr in COBBLES:
        body.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='{rr:.0f}' ry='{rr*0.45:.0f}' fill='#c9a676' stroke='#a8865a' stroke-width='3'/>")
    # interior + bola + corte, y la fachada que se desvanece encima
    body.append(interior(t, cut))
    if rev > 0:
        body.append(f"<circle cx='{CX}' cy='{YS}' r='{R*1.5:.0f}' fill='url(#halo)'/>")
    if r > 0:
        body.append(bola(t, r, rev, wob))
    body.append(seccion())
    if cut < 1:
        body.append(f"<g opacity='{1 - cut:.3f}'>{exterior()}</g>")
    # flechas de medida (alto = ancho)
    ka = seg(t, 7.55, 8.05)
    body.append(flecha(CX - R + 24, YS, CX + R - 24, YS, ka))
    body.append(flecha(CX, YF - 24, CX, YS - R + 24, ka))
    # destellos alrededor de la bola
    if rev > 0:
        for a, d, ph, sz in SPARKS:
            aa = a + t * 0.4; k = 0.5 + 0.5 * math.sin(t * 6 + ph)
            x, y = CX + R * d * math.cos(aa), YS + R * d * math.sin(aa)
            if y > YF - 10: continue
            sz2 = sz * k * rev
            body.append(f"<path d='M{x:.1f} {y - sz2:.1f} L{x + sz2*0.3:.1f} {y - sz2*0.3:.1f} L{x + sz2:.1f} {y:.1f} L{x + sz2*0.3:.1f} {y + sz2*0.3:.1f} "
                        f"L{x:.1f} {y + sz2:.1f} L{x - sz2*0.3:.1f} {y + sz2*0.3:.1f} L{x - sz2:.1f} {y:.1f} L{x - sz2*0.3:.1f} {y - sz2*0.3:.1f} Z' "
                        f"fill='#fff6a8' stroke='{INK}' stroke-width='3'/>")
    # turistas: llegan andando y luego miran arriba; saltan en la revelación
    w1 = 1 - seg(t, 2.2, 2.5); up = seg(t, 4.6, 5.3)
    body.append(turista(lerp(-60, 290, seg(t, 0, 2.4)), YF, "#ff5a5f", t, 0.0, w1, up, rev, 1))
    body.append(turista(lerp(1140, 790, seg(t, 0, 2.4)), YF, "#ffb627", t, 1.3, w1, up, seg(t, 7.55, 8.0), -1))
    # palomas
    for i, (y0, sp, sc) in enumerate(((1080, 120, 0.9), (1150, 150, 0.7), (1020, 100, 1.0))):
        x = 1200 - ((t * sp + i * 420) % 1500)
        body.append(paloma(x, y0 + 18 * math.sin(t * 2 + i), sc, t, i))
    s.append(zoom(CX, zy, z, "".join(body)))
    # destello de la revelación
    fl = clamp(1 - (t - 7.45) / 0.45) if t >= 7.45 else 0
    if fl > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.75*fl:.2f}'/>")
    s.append("</svg>")
    return "".join(s)
