"""2026-11-23-c4 · La calabaza más pesada del mundo: 1.431,5 kg (Ron Wallace, 10-10-2026),
más del doble que una vaca Holstein (Guinness World Records).

Un balancín en una granja de otoño: a la izquierda saltan dos vacas, a la derecha crece una
calabaza con cara. Mientras crece, las vacas ganan; en la REVELACION la calabaza se hincha,
el balancín se vuelca hacia su lado y lanza a las dos vacas por los aires.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote, zoom

DUR = 10.0
REVELACION = 6.6
MUSICA = 2

PX, PY = 540, 1640          # pivote del balancín
rng = np.random.default_rng(23)
LEAVES = [(rng.uniform(0, W), rng.uniform(-200, 1900), rng.uniform(16, 26), rng.uniform(0, 6.28),
           rng.uniform(60, 120), ["#e8562a", "#f2a21f", "#c9401f", "#f5c542"][i % 4]) for i in range(16)]
SPARK = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 6.28)) for _ in range(14)]


def blink(t, periodo, fase=0.0):
    return 0.12 if ((t + fase) % periodo) < 0.13 else 1.0


def cow(t, x, y, ph, surprised):
    """Vaca lechera original de perfil (mira a la derecha), patas en y=0."""
    tail = 14 * math.sin(t * 3.2 + ph)
    chew = 3 * math.sin(t * 9 + ph)
    bl = blink(t, 2.9, ph)
    g = [f"<g transform='translate({x:.1f},{y:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='4' rx='105' ry='10' fill='#000' opacity='0.18'/>")
    # cola
    g.append(f"<g transform='translate(-102,-150) rotate({tail:.1f})'>"
             f"<path d='M0 0 Q-34 30 -22 88' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
             f"<path d='M0 0 Q-34 30 -22 88' fill='none' stroke='#fff' stroke-width='6' stroke-linecap='round'/>"
             f"<ellipse cx='-22' cy='96' rx='12' ry='18' fill='#2b2b2b' stroke='{INK}' stroke-width='5'/></g>")
    # patas
    for lx in (-78, -46, 42, 72):
        g.append(f"<rect x='{lx - 12}' y='-80' width='24' height='74' rx='9' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<rect x='{lx - 13}' y='-18' width='26' height='18' rx='5' fill='#4a3b36' stroke='{INK}' stroke-width='5'/>")
    # ubre
    g.append(f"<ellipse cx='-8' cy='-72' rx='28' ry='17' fill='#ffa6b8' stroke='{INK}' stroke-width='6'/>")
    # cuerpo y manchas
    g.append(f"<rect x='-112' y='-178' width='214' height='112' rx='52' fill='#ffffff' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-70 -170 Q-40 -150 -55 -120 Q-80 -100 -96 -128 Q-104 -160 -70 -170 Z' fill='#262626'/>")
    g.append(f"<path d='M10 -174 Q55 -170 52 -138 Q46 -110 14 -118 Q-6 -140 10 -174 Z' fill='#262626'/>")
    g.append(f"<ellipse cx='-20' cy='-92' rx='22' ry='12' fill='#262626'/>")
    # cabeza
    g.append(f"<g transform='translate(118,-172)'>")
    g.append(f"<ellipse cx='-44' cy='-38' rx='22' ry='12' fill='#fff' stroke='{INK}' stroke-width='6' transform='rotate(-25 -44 -38)'/>")
    g.append(f"<path d='M-18 -54 Q-26 -82 -10 -88' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
             f"<path d='M-18 -54 Q-26 -82 -10 -88' fill='none' stroke='#f3e6c4' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<path d='M22 -54 Q28 -82 12 -88' fill='none' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
             f"<path d='M22 -54 Q28 -82 12 -88' fill='none' stroke='#f3e6c4' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='0' cy='-8' rx='50' ry='54' fill='#fff' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='54' cy='-34' rx='22' ry='12' fill='#fff' stroke='{INK}' stroke-width='6' transform='rotate(25 54 -34)'/>")
    g.append(f"<ellipse cx='54' cy='-34' rx='12' ry='6' fill='#ffa6b8' transform='rotate(25 54 -34)'/>")
    g.append(f"<path d='M-46 -30 Q-30 -56 -6 -40 Q-10 -14 -36 -8 Z' fill='#262626'/>")
    # ojos
    er = 13 if not surprised else 16
    pr = 7 if not surprised else 4
    for ex in (-18, 20):
        g.append(f"<g transform='translate({ex},-22) scale(1,{bl if not surprised else 1})'>"
                 f"<ellipse rx='{er}' ry='{er + 2}' fill='#fff' stroke='{INK}' stroke-width='5'/>"
                 f"<circle cx='3' cy='1' r='{pr}' fill='{INK}'/><circle cx='0' cy='-3' r='2.5' fill='#fff'/></g>")
    # hocico
    g.append(f"<ellipse cx='4' cy='{24 + chew * 0.3:.1f}' rx='40' ry='26' fill='#ffb3c1' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<ellipse cx='-10' cy='18' rx='6' ry='8' fill='#c4657a'/><ellipse cx='18' cy='18' rx='6' ry='8' fill='#c4657a'/>")
    if surprised:
        g.append(f"<ellipse cx='4' cy='38' rx='9' ry='8' fill='#7a2a3a' stroke='{INK}' stroke-width='4'/>")
    else:
        g.append(f"<path d='M-8 {36 + chew:.1f} Q4 {42 + chew:.1f} 16 {36 + chew:.1f}' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round'/>")
    g.append("</g></g>")
    return "".join(g)


def pumpkin(t, cx, base, r, proud):
    """Calabaza gigante con gajos, rabo, hoja y cara simpática; base = y del suelo."""
    rx, ry = r * 1.18, r * 0.86
    cy = base - ry
    wob = 1 + 0.015 * math.sin(t * 5)
    g = [f"<g transform='translate({cx:.1f},{cy:.1f}) scale({wob:.4f},{2 - wob:.4f})'>"]
    sw = max(5, LW * min(1, r / 120))
    # rabo y hoja
    g.append(f"<path d='M{-r*0.08:.1f} {-ry*0.92:.1f} Q{-r*0.1:.1f} {-ry*1.22:.1f} {r*0.06:.1f} {-ry*1.3:.1f} "
             f"L{r*0.16:.1f} {-ry*1.2:.1f} Q{r*0.06:.1f} {-ry*1.1:.1f} {r*0.1:.1f} {-ry*0.92:.1f} Z' fill='#6b8f2a' stroke='{INK}' stroke-width='{sw:.1f}' stroke-linejoin='round'/>")
    g.append(f"<path d='M{r*0.1:.1f} {-ry*0.98:.1f} Q{r*0.5:.1f} {-ry*1.35:.1f} {r*0.75:.1f} {-ry*1.05:.1f} Q{r*0.45:.1f} {-ry*0.92:.1f} {r*0.1:.1f} {-ry*0.98:.1f} Z' fill='#7cc443' stroke='{INK}' stroke-width='{sw*0.8:.1f}' stroke-linejoin='round'/>")
    g.append(f"<path d='M{-r*0.12:.1f} {-ry*1.0:.1f} q{-r*0.25:.1f} {-r*0.05:.1f} {-r*0.22:.1f} {-r*0.2:.1f} q{r*0.06:.1f} {-r*0.1:.1f} {r*0.12:.1f} 0' fill='none' stroke='#5a7d22' stroke-width='{sw*0.7:.1f}' stroke-linecap='round'/>")
    # gajos (de fuera hacia dentro)
    for ox, k, col in ((-0.55, 0.52, "#e86a14"), (0.55, 0.52, "#e86a14"), (-0.28, 0.6, "#f47b1c"), (0.28, 0.6, "#f47b1c"), (0, 0.5, "#ff8f2a")):
        g.append(f"<ellipse cx='{ox*rx:.1f}' cy='0' rx='{k*rx:.1f}' ry='{ry:.1f}' fill='{col}' stroke='{INK}' stroke-width='{sw:.1f}'/>")
    g.append(f"<ellipse cx='{-0.12*rx:.1f}' cy='{-0.55*ry:.1f}' rx='{0.12*rx:.1f}' ry='{0.18*ry:.1f}' fill='#ffc27a' opacity='0.7'/>")
    # cara
    bl = blink(t, 3.3, 1.1)
    es = r * 0.15
    for ex in (-0.32, 0.32):
        g.append(f"<g transform='translate({ex*rx:.1f},{-0.12*ry:.1f}) scale(1,{bl})'>"
                 f"<ellipse rx='{es:.1f}' ry='{es*1.2:.1f}' fill='#fff' stroke='{INK}' stroke-width='{sw*0.8:.1f}'/>"
                 f"<circle cx='{es*0.2:.1f}' cy='{es*0.15:.1f}' r='{es*0.6:.1f}' fill='{INK}'/>"
                 f"<circle cx='{-es*0.1:.1f}' cy='{-es*0.25:.1f}' r='{es*0.22:.1f}' fill='#fff'/></g>")
        g.append(f"<ellipse cx='{ex*rx*1.45:.1f}' cy='{0.2*ry:.1f}' rx='{es*0.8:.1f}' ry='{es*0.45:.1f}' fill='#ff5a6e' opacity='0.55'/>")
    if proud > 0.5:
        g.append(f"<path d='M{-0.28*rx:.1f} {0.22*ry:.1f} Q0 {0.62*ry:.1f} {0.28*rx:.1f} {0.22*ry:.1f} Z' fill='#7a2a1a' stroke='{INK}' stroke-width='{sw*0.8:.1f}' stroke-linejoin='round'/>"
                 f"<ellipse cx='0' cy='{0.43*ry:.1f}' rx='{0.1*rx:.1f}' ry='{0.05*ry:.1f}' fill='#ff7a7a'/>")
    else:
        g.append(f"<path d='M{-0.16*rx:.1f} {0.25*ry:.1f} Q0 {0.4*ry:.1f} {0.16*rx:.1f} {0.25*ry:.1f}' fill='none' stroke='{INK}' stroke-width='{sw*0.8:.1f}' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def angulo(t):
    a = lerp(0, -11, seg(t, 1.0, 1.7)) + 2.5 * math.sin(max(0, t - 1.7) * 9) * math.exp(-max(0, t - 1.7) * 4) * (t > 1.7)
    a += lerp(0, 3, seg(t, 2.2, 4.4))                     # la calabaza crece y alivia un poco
    a += lerp(0, -5, seg(t, 5.2, 5.6))                    # aterriza la segunda vaca
    if t > 5.6: a += 2 * math.sin((t - 5.6) * 10) * math.exp(-(t - 5.6) * 5)
    if 5.9 < t < 6.6: a += 0.8 * math.sin(t * 60)         # tiembla: tensión
    k = seg(t, 6.7, 7.05)
    a = lerp(a, 13, k)
    if t > 7.05: a += -3 * math.sin((t - 7.05) * 12) * math.exp(-(t - 7.05) * 5)
    return a


def frame(t):
    rev = seg(t, 6.6, 7.1)
    # cielo de otoño
    top = mix("#6fc3f2", "#ffd07a", 0.0)
    s = ["<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#5bb6ee', '#4aa8ea', rev)}'/>"
         f"<stop offset='0.55' stop-color='{mix('#9fd8f5', '#b9e4ff', rev)}'/><stop offset='1' stop-color='#ffe3a8'/></linearGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff6c2' stop-opacity='{0.95*rev:.3f}'/>"
         f"<stop offset='0.5' stop-color='#ffc14d' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ff9a1f' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    # sol suave
    s.append(f"<circle cx='880' cy='330' r='110' fill='#fff3b0' opacity='0.55'/><circle cx='880' cy='330' r='72' fill='#fff7cf' stroke='#ffd76a' stroke-width='6'/>")
    # nubes
    for i, (cx, cy, sc, sp) in enumerate([(160, 260, 1.3, 16), (720, 560, 1.0, 22), (380, 860, 1.5, 12)]):
        x = (cx + t * sp) % 1400 - 200
        s.append(f"<g transform='translate({x:.0f},{cy}) scale({sc})'>"
                 f"<path d='M0 50 Q-10 10 40 12 Q60 -28 110 -6 Q150 -26 175 14 Q215 18 205 50 Z' fill='#ffffff' stroke='{INK}' stroke-width='5' stroke-linejoin='round' opacity='0.95'/></g>")
    cam = 1 + 0.12 * seg(t, 6.6, 7.6)
    shake = 9 * math.sin(t * 70) * math.exp(-max(0, t - 7.0) * 9) * (t > 7.0)
    w = []
    # colinas lejanas, granero y árboles
    w.append(f"<path d='M0 1230 Q220 1130 470 1200 T940 1170 T1080 1190 L1080 1920 L0 1920 Z' fill='#9cc65a' stroke='{INK}' stroke-width='{LW}'/>")
    w.append(f"<g transform='translate(760,1080)'>"
             f"<rect x='0' y='60' width='170' height='120' fill='#d8443a' stroke='{INK}' stroke-width='7'/>"
             f"<path d='M-14 66 L85 0 L184 66 Z' fill='#a82f2a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='60' y='108' width='50' height='72' fill='#fff1d6' stroke='{INK}' stroke-width='6'/>"
             f"<path d='M60 108 L110 180 M110 108 L60 180' stroke='{INK}' stroke-width='5'/></g>")
    for tx, ty, sc, col in ((140, 1150, 1.0, '#f08a24'), (300, 1175, 0.8, '#e2542a'), (620, 1170, 0.85, '#f5b62a')):
        sway = 3 * math.sin(t * 1.5 + tx)
        w.append(f"<g transform='translate({tx},{ty}) scale({sc}) rotate({sway:.1f})'>"
                 f"<rect x='-12' y='0' width='24' height='90' fill='#8a5a34' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='0' cy='-20' r='70' fill='{col}' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='-30' cy='-40' r='20' fill='#fff' opacity='0.18'/></g>")
    w.append(f"<path d='M0 1380 Q300 1300 600 1360 T1080 1340 L1080 1920 L0 1920 Z' fill='#7fb848' stroke='{INK}' stroke-width='{LW}'/>")
    # valla
    for fx in range(-20, 1100, 120):
        w.append(f"<rect x='{fx}' y='1330' width='22' height='110' rx='4' fill='#c98b52' stroke='{INK}' stroke-width='5'/>")
    w.append(f"<rect x='0' y='1350' width='1080' height='16' fill='#d99a5e' stroke='{INK}' stroke-width='5'/>"
             f"<rect x='0' y='1395' width='1080' height='16' fill='#d99a5e' stroke='{INK}' stroke-width='5'/>")
    w.append(f"<path d='M0 1500 Q270 1460 540 1490 T1080 1480 L1080 1920 L0 1920 Z' fill='#5ea83a' stroke='{INK}' stroke-width='{LW}'/>")
    for gx in range(30, 1080, 90):
        gy = 1560 + (gx * 37) % 300
        w.append(f"<path d='M{gx} {gy} l8 -26 l6 24 l8 -20 l4 22' fill='none' stroke='#3f8a28' stroke-width='5' stroke-linecap='round'/>")
    # resplandor y rayos detrás de la calabaza en la revelación
    if rev > 0:
        gx_, gy_ = 800, 1440
        w.append(f"<circle cx='{gx_}' cy='{gy_}' r='{lerp(150, 560, rev):.0f}' fill='url(#glow)'/>")
        rays = []
        for i in range(12):
            a0 = math.radians(i * 30 + t * 20)
            a1 = a0 + math.radians(9)
            R = 700 * rev
            rays.append(f"M{gx_} {gy_} L{gx_ + R*math.cos(a0):.0f} {gy_ + R*math.sin(a0):.0f} L{gx_ + R*math.cos(a1):.0f} {gy_ + R*math.sin(a1):.0f} Z")
        w.append(f"<path d='{' '.join(rays)}' fill='#fff2a8' opacity='{0.35*rev:.2f}'/>")
    # sombra y soporte del balancín
    w.append(f"<ellipse cx='{PX}' cy='1815' rx='430' ry='30' fill='#000' opacity='0.18'/>")
    w.append(f"<path d='M{PX} {PY} L{PX - 110} 1815 L{PX + 110} 1815 Z' fill='#e9b44c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    w.append(f"<path d='M{PX - 55} 1730 L{PX + 55} 1730' stroke='{INK}' stroke-width='6'/>")
    # balancín con sus pasajeros
    a = angulo(t)
    b = [f"<g transform='translate({PX},{PY}) rotate({a:.2f})'>"]
    b.append(f"<rect x='-460' y='-20' width='920' height='40' rx='14' fill='#b8743c' stroke='{INK}' stroke-width='{LW}'/>")
    for px_ in range(-400, 460, 110):
        b.append(f"<line x1='{px_}' y1='-12' x2='{px_ + 40}' y2='-12' stroke='#8d5428' stroke-width='5' stroke-linecap='round'/>")
    # calabaza: crece poco a poco y se hincha en la revelación
    r = lerp(55, 120, seg(t, 0, 4.4)) + lerp(0, 32, seg(t, 4.4, 6.4))
    if 5.9 < t < 6.6: r += 4 * math.sin(t * 40)
    r = lerp(r, 215, seg(t, 6.6, 7.0))
    if 6.9 < t < 7.35: r *= 1 + 0.07 * math.sin(math.pi * (t - 6.9) / 0.45)
    b.append(pumpkin(t, 265 if t < 6.6 else lerp(265, 250, seg(t, 6.6, 7.0)), -20, r, seg(t, 6.75, 6.85)))
    # vacas: saltan al balancín
    sorpresa = 6.85 < t < 8.1
    def salto(t0, t1, x0, x1):
        k = clamp((t - t0) / (t1 - t0))
        return lerp(x0, x1, k), lerp(170, -20, ease(k)) - 300 * math.sin(math.pi * k)
    hop = 0.0
    if t > 6.85:
        k = clamp((t - 6.85) / 1.1)
        hop = -360 * math.sin(math.pi * k)
    if t < 1.0:
        cx1, cy1 = salto(0, 1.0, -640, -360)
    else:
        cx1, cy1 = -360, -20 + 4 * math.sin(t * 5)
    b.append(cow(t, cx1, cy1 + hop, 0.0, sorpresa))
    if t >= 4.5:
        if t < 5.4:
            cx2, cy2 = salto(4.5, 5.4, -760, -175)
        else:
            cx2, cy2 = -175, -20 + 4 * math.sin(t * 5 + 1)
        hop2 = 0.0
        if t > 6.9:
            k = clamp((t - 6.9) / 1.15)
            hop2 = -300 * math.sin(math.pi * k)
        b.append(cow(t, cx2, cy2 + hop2, 1.7, sorpresa))
    b.append("</g>")
    w.append("".join(b))
    # polvo del golpe
    if 7.0 < t < 8.2:
        k = seg(t, 7.0, 8.2)
        ex, ey = PX + 440 * math.cos(math.radians(13)), PY + 440 * math.sin(math.radians(13)) + 30
        for i in range(7):
            ang = math.radians(180 + i * 30)
            dx, dy = math.cos(ang) * 160 * k, -abs(math.sin(ang)) * 70 * k - 10
            w.append(f"<circle cx='{ex + dx:.0f}' cy='{ey + dy:.0f}' r='{lerp(20, 55, k):.0f}' fill='#f1e2c2' stroke='{INK}' stroke-width='5' opacity='{1 - k:.2f}'/>")
    # destellos alrededor de la calabaza ganadora
    if t > 7.0:
        for sx, sy, ph in SPARK:
            a_ = max(0.0, math.sin(t * 4 + ph))
            x, y = 800 + sx * 330, 1360 + sy * 230
            rr = 18 * a_ * seg(t, 7.0, 7.5)
            if rr > 1:
                w.append(f"<path d='M{x:.0f} {y - rr*1.8:.0f} Q{x:.0f} {y:.0f} {x + rr*1.8:.0f} {y:.0f} Q{x:.0f} {y:.0f} {x:.0f} {y + rr*1.8:.0f} Q{x:.0f} {y:.0f} {x - rr*1.8:.0f} {y:.0f} Q{x:.0f} {y:.0f} {x:.0f} {y - rr*1.8:.0f} Z' fill='#fff7b0' stroke='{INK}' stroke-width='3'/>")
    # hojas de otoño cayendo
    for lx, ly, sz, ph, sp, col in LEAVES:
        y = (ly + t * sp) % 2000 - 80
        if y < 1050: continue
        x = lx + 40 * math.sin(t * 1.3 + ph)
        rot = math.degrees(ph) + t * 70
        w.append(f"<g transform='translate({x:.0f},{y:.0f}) rotate({rot:.0f})'>"
                 f"<path d='M0 {-sz} Q{sz*0.8:.0f} 0 0 {sz} Q{-sz*0.8:.0f} 0 0 {-sz} Z' fill='{col}' stroke='{INK}' stroke-width='4'/></g>")
    s.append(f"<g transform='translate({shake:.1f},0)'>" + zoom(780, 1480, cam, "".join(w)) + "</g>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>" + "".join(s) + "</svg>")
