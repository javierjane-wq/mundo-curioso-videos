"""2026-11-26-c1 · Inventos: la lata de conserva (1810) llegó 48 años antes que el abrelatas (1858).

Una lata de tomate con cara entra dando saltitos por la encimera de una cocina (0-2,3 s). Un martillo
y un cincel flotantes la golpean en la tapa con chispas mientras ella cierra los ojos (2,3-4,4 s).
El tiempo pasa: por la ventana se suceden días y noches, crece una telaraña y la lata se adormila
(4,4-6,6 s). En la REVELACION (6,6 s) llega volando un abrelatas brillante, la tapa salta por los
aires, sale un chorro de luz dorada de la lata, la cocina se ilumina y la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 6.6
MUSICA = 5

CX, TOP, BOT = 400, 1080, 1452      # lata: centro, borde de la tapa, base
RW, RY = 150, 30                    # semiancho y semieje de las elipses
COUNTER = 1440                      # superficie de la encimera

rng = np.random.default_rng(1810)
DUST = [(rng.uniform(0, W), rng.uniform(950, 1900), rng.uniform(3, 6), rng.uniform(15, 40), rng.uniform(0, 6.28)) for _ in range(30)]
STARS = [(rng.uniform(660, 980), rng.uniform(1030, 1250), rng.uniform(2.5, 4.5)) for _ in range(12)]
SPARKS = [(rng.uniform(0, 6.28), rng.uniform(40, 110)) for _ in range(9)]
CONFETTI = [(rng.uniform(-1, 1), rng.uniform(0.4, 1.0), rng.uniform(0, 6.28),
             ["#ffd23f", "#ff5a5f", "#5ec8ff", "#7ed957", "#ff9f1c"][i % 5]) for i in range(34)]

HIT_T = [2.5 + 0.5 * i for i in range(4)] + [4.7, 5.5, 6.2]   # golpes del martillo


def hammer_angle(t):
    """0 = golpeando; positivo = martillo levantado."""
    if t < 2.3:
        return 40 * seg(t, 1.6, 2.3)
    for h in HIT_T:
        if t < h:
            prev = max([x for x in HIT_T if x < h], default=2.3)
            k = (t - prev) / (h - prev)
            return 40 * math.sin(math.pi * min(1, k * 1.05)) ** 0.7 if k < 0.95 else 40 * (1 - (k - 0.95) / 0.05) * 0.2
    return 0.0


def last_hit(t):
    hs = [h for h in HIT_T if h <= t]
    return t - hs[-1] if hs else 99


def window(t, light):
    """Ventana con el cielo que pasa de día a noche varias veces (paso del tiempo)."""
    x0, y0, x1, y1 = 650, 1010, 1000, 1330
    cyc = seg(t, 4.4, 6.5) * 2.0                 # 2 ciclos día-noche
    night = 0.5 - 0.5 * math.cos(2 * math.pi * cyc)
    sky = mix("#8fd6ff", "#1b2350", night)
    sky = mix(sky, "#bfeaff", seg(t, 6.6, 7.4))
    p = [f"<rect x='{x0}' y='{y0}' width='{x1-x0}' height='{y1-y0}' fill='{sky}'/>"]
    ang = 2 * math.pi * (cyc % 1.0)
    # sol y luna giran detrás del cristal
    sx, sy = 825 - 150 * math.sin(ang), 1260 - 180 * math.cos(ang)
    mx, my = 825 + 150 * math.sin(ang), 1260 + 180 * math.cos(ang)
    p.append(f"<clipPath id='win'><rect x='{x0}' y='{y0}' width='{x1-x0}' height='{y1-y0}'/></clipPath><g clip-path='url(#win)'>")
    for sxx, syy, sr in STARS:
        if night > 0.3:
            p.append(f"<circle cx='{sxx:.0f}' cy='{syy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{(night-0.3)*1.4:.2f}'/>")
    p.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='44' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    p.append(f"<circle cx='{mx:.0f}' cy='{my:.0f}' r='36' fill='#f4f1de' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='{mx+14:.0f}' cy='{my-8:.0f}' r='30' fill='{sky}'/>")
    # nubes que pasan
    for i, (cy, sp) in enumerate(((1080, 60), (1170, 40))):
        cxn = x0 - 120 + ((t * sp + i * 210) % 520)
        p.append(f"<path d='M{cxn:.0f} {cy} q15 -30 50 -20 q20 -28 55 -8 q30 -4 30 28 z' fill='{mix('#ffffff', '#5a6290', night)}' "
                 f"stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    p.append("</g>")
    # marco y cruz
    p.append(f"<rect x='{x0}' y='{y0}' width='{x1-x0}' height='{y1-y0}' fill='none' stroke='#f7f0e1' stroke-width='26'/>")
    p.append(f"<rect x='{x0-13}' y='{y0-13}' width='{x1-x0+26}' height='{y1-y0+26}' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    p.append(f"<line x1='{(x0+x1)/2}' y1='{y0}' x2='{(x0+x1)/2}' y2='{y1}' stroke='#f7f0e1' stroke-width='16'/>"
             f"<line x1='{x0}' y1='{(y0+y1)/2}' x2='{x1}' y2='{(y0+y1)/2}' stroke='#f7f0e1' stroke-width='16'/>")
    p.append(f"<rect x='{x0+13}' y='{y0+13}' width='{x1-x0-26}' height='{y1-y0-26}' fill='none' stroke='{INK}' stroke-width='5'/>")
    # cortina que se mece
    sw = 14 * math.sin(t * 1.7)
    p.append(f"<path d='M{x0-40} {y0-40} L{x0+90} {y0-40} Q{x0+60+sw:.0f} {y0+120} {x0+70+sw:.0f} {y1+10} "
             f"Q{x0+10} {y1+30} {x0-40} {y1+20} Z' fill='#ff8a5c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    p.append(f"<path d='M{x1+40} {y0-40} L{x1-90} {y0-40} Q{x1-60+sw:.0f} {y0+120} {x1-70+sw:.0f} {y1+10} "
             f"Q{x1-10} {y1+30} {x1+40} {y1+20} Z' fill='#ff8a5c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    p.append(f"<rect x='{x0-70}' y='{y0-58}' width='{x1-x0+140}' height='24' rx='12' fill='#a0623a' stroke='{INK}' stroke-width='7'/>")
    # maceta en el alféizar
    lean = 6 * math.sin(t * 2.2)
    p.append(f"<g transform='translate(930,{COUNTER-2}) rotate({lean:.1f})'>"
             f"<path d='M-8 -60 Q-40 -120 -10 -150' fill='none' stroke='#3f9b4b' stroke-width='10' stroke-linecap='round'/>"
             f"<ellipse cx='-14' cy='-140' rx='16' ry='30' fill='#5cc46a' stroke='{INK}' stroke-width='6' transform='rotate(-25 -14 -140)'/>"
             f"<ellipse cx='22' cy='-120' rx='14' ry='28' fill='#5cc46a' stroke='{INK}' stroke-width='6' transform='rotate(30 22 -120)'/>"
             f"<path d='M4 -60 Q20 -100 22 -110' fill='none' stroke='#3f9b4b' stroke-width='9' stroke-linecap='round'/></g>")
    p.append(f"<path d='M890 {COUNTER-70} L970 {COUNTER-70} L958 {COUNTER} L902 {COUNTER} Z' fill='#e2733e' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='882' y='{COUNTER-82}' width='96' height='20' rx='6' fill='#c95f2f' stroke='{INK}' stroke-width='6'/>")
    return "".join(p)


def can(t):
    """Lata de tomate con cara. Devuelve (cuerpo, tapa) por separado (la tapa salta en la revelación)."""
    # entrada a saltitos desde la izquierda
    ent = seg(t, 0, 1.5)
    dx = lerp(-560, 0, ent)
    hop = -abs(math.sin(ent * math.pi * 3)) * 70 * (1 - ent) if t < 1.5 else 0
    # aplastamiento al golpear y al aterrizar
    lh = last_hit(t)
    squash = 0.07 * math.exp(-lh * 9) if lh < 0.6 else 0
    if 1.5 <= t < 1.9:
        squash += 0.06 * math.sin(math.pi * (t - 1.5) / 0.4)
    joy = seg(t, 6.8, 7.2)
    jump = -40 * math.sin(math.pi * seg(t, 6.8, 7.5)) if t < 7.6 else -6 * abs(math.sin(t * 5))
    sy = 1 - squash + 0.04 * joy * math.sin(t * 10)
    sx = 1 + squash * 0.8
    sleepy = seg(t, 4.6, 5.3) * (1 - seg(t, 6.5, 6.75))
    wince = (lh < 0.35 and t < 6.5) or (2.3 < t < 4.45 and lh < 0.45)
    blink = (t % 2.7) < 0.12 and not wince

    body = [f"<g transform='translate({CX + dx:.1f},{BOT + hop + jump:.1f}) scale({sx:.3f},{sy:.3f}) translate({-CX},{-BOT})'>"]
    body.append(f"<ellipse cx='{CX}' cy='{BOT+6}' rx='{RW+30}' ry='22' fill='#000' opacity='0.18'/>")
    # cilindro plateado
    body.append(f"<path d='M{CX-RW} {TOP} L{CX-RW} {BOT} A{RW} {RY} 0 0 0 {CX+RW} {BOT} L{CX+RW} {TOP} Z' fill='#cfd6de' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    body.append(f"<path d='M{CX-RW+18} {TOP+20} L{CX-RW+18} {BOT-10}' stroke='#f4f7fa' stroke-width='14' stroke-linecap='round'/>")
    # aros del metal
    for yy in (TOP + 28, TOP + 50, BOT - 34):
        body.append(f"<path d='M{CX-RW} {yy} A{RW} {RY} 0 0 0 {CX+RW} {yy}' fill='none' stroke='#8d98a5' stroke-width='6'/>")
    # etiqueta roja con franjas
    lt, lb = TOP + 78, BOT - 64
    body.append(f"<path d='M{CX-RW} {lt} A{RW} {RY} 0 0 0 {CX+RW} {lt} L{CX+RW} {lb} A{RW} {RY} 0 0 1 {CX-RW} {lb} Z' fill='#e8483c' stroke='{INK}' stroke-width='7'/>")
    body.append(f"<path d='M{CX-RW} {lt+18} A{RW} {RY} 0 0 0 {CX+RW} {lt+18}' fill='none' stroke='#ffd23f' stroke-width='12'/>")
    body.append(f"<path d='M{CX-RW} {lb-18} A{RW} {RY} 0 0 0 {CX+RW} {lb-18}' fill='none' stroke='#ffd23f' stroke-width='12'/>")
    # tomatitos dibujados en la etiqueta (laterales)
    for tx, ty, rr in ((CX - 112, lb - 70, 22), (CX + 112, lb - 70, 22)):
        body.append(f"<circle cx='{tx}' cy='{ty}' r='{rr}' fill='#ff7a45' stroke='{INK}' stroke-width='5'/>"
                    f"<path d='M{tx-10} {ty-rr+2} L{tx} {ty-rr-8} L{tx+10} {ty-rr+2} Z' fill='#3f9b4b' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>")
    # cara
    ey = lt + 92
    look = 10 * math.sin(t * 1.3) if t < 2.3 else (lerp(0, -8, seg(t, 6.3, 6.6)) if t < 6.8 else 0)
    for ex in (CX - 52, CX + 52):
        if wince:
            d = 1 if ex < CX else -1
            body.append(f"<path d='M{ex-22*d} {ey-16} L{ex+14*d} {ey} L{ex-22*d} {ey+16}' fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/>")
        elif blink:
            body.append(f"<path d='M{ex-26} {ey} Q{ex} {ey+14} {ex+26} {ey}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
        else:
            s = 1 + 0.18 * joy
            body.append(f"<g transform='translate({ex},{ey}) scale({s:.3f})'><ellipse rx='32' ry='37' fill='#ffffff' stroke='{INK}' stroke-width='7'/>"
                        f"<circle cx='{look:.1f}' cy='4' r='17' fill='{INK}'/><circle cx='{look-6:.1f}' cy='-4' r='7' fill='#fff'/></g>")
            if sleepy > 0.02:   # párpado que baja (adormilada)
                lid = lerp(-40, 2, sleepy)
                body.append(f"<path d='M{ex-34} {ey-40} L{ex+34} {ey-40} L{ex+34} {ey+lid:.1f} Q{ex} {ey+lid+10:.1f} {ex-34} {ey+lid:.1f} Z' fill='#d63a30' stroke='{INK}' stroke-width='6'/>")
    body.append(f"<ellipse cx='{CX-92}' cy='{ey+46}' rx='18' ry='10' fill='#ff9aa2' opacity='0.85'/>"
                f"<ellipse cx='{CX+92}' cy='{ey+46}' rx='18' ry='10' fill='#ff9aa2' opacity='0.85'/>")
    my = ey + 62
    if joy > 0.3:
        body.append(f"<path d='M{CX-38} {my-6} Q{CX} {my+52} {CX+38} {my-6} Z' fill='#7a1f1a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                    f"<path d='M{CX-18} {my+22} Q{CX} {my+14} {CX+18} {my+22} Q{CX} {my+36} {CX-18} {my+22}' fill='#ff8a8a'/>")
    elif wince or (2.3 < t < 4.45):
        body.append(f"<path d='M{CX-30} {my+8} Q{CX-15} {my-4} {CX} {my+8} Q{CX+15} {my+20} {CX+30} {my+8}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    elif sleepy > 0.3:
        body.append(f"<ellipse cx='{CX}' cy='{my+6}' rx='12' ry='{8 + 4*math.sin(t*3):.1f}' fill='#7a1f1a' stroke='{INK}' stroke-width='6'/>")
    else:
        body.append(f"<path d='M{CX-28} {my} Q{CX} {my+26} {CX+28} {my}' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # interior oscuro (visible cuando la tapa ya no está)
    gone = seg(t, 6.85, 7.0)
    if gone > 0:
        body.append(f"<ellipse cx='{CX}' cy='{TOP}' rx='{RW-12}' ry='{RY-6}' fill='#b8322a' stroke='{INK}' stroke-width='6' opacity='{gone:.2f}'/>")
    body.append("</g>")

    # tapa: con abolladuras de los golpes; en la revelación sale disparada girando
    fly = clamp((t - 6.85) / 0.9)
    lx = CX + dx - 680 * fly
    ly = BOT + hop + jump - (BOT - TOP) * sy - 760 * fly + 520 * fly ** 2
    rot = lerp(0, -540, fly)
    dents = sum(1 for h in HIT_T if h <= t)
    lid = [f"<g transform='translate({lx:.1f},{ly:.1f}) rotate({rot:.1f}) scale({sx:.3f},1)'>"]
    lid.append(f"<ellipse rx='{RW}' ry='{RY}' fill='#e3e8ee' stroke='{INK}' stroke-width='{LW}'/>")
    lid.append(f"<ellipse rx='{RW-22}' ry='{RY-9}' fill='none' stroke='#9aa5b1' stroke-width='5'/>")
    for i in range(min(dents, 5)):
        ox = -55 + i * 28
        lid.append(f"<path d='M{ox-10} -4 L{ox} 3 L{ox+10} -3' fill='none' stroke='#7c8794' stroke-width='4'/>")
    lid.append("</g>")
    return "".join(body), "".join(lid), (CX + dx, BOT + hop + jump - (BOT - TOP) * sy)


def tools(t, top_pt):
    """Martillo y cincel flotantes (golpean de 2,3 a 6,3 s y luego salen volando)."""
    tx, ty = top_pt
    inn = seg(t, 1.4, 2.2)
    out = seg(t, 6.3, 6.75)
    if inn <= 0 or out >= 1:
        return ""
    ox = lerp(520, 0, inn) + lerp(0, 700, out)
    oy = lerp(-260, 0, inn) - lerp(0, 300, out)
    p = [f"<g transform='translate({ox:.1f},{oy:.1f})'>"]
    # cincel vertical apoyado en la tapa
    cx, cy = tx + 30, ty - 4
    p.append(f"<g transform='translate({cx:.1f},{cy:.1f}) rotate(-8)'>"
             f"<path d='M-9 0 L9 0 L13 -120 L-13 -120 Z' fill='#9aa5b1' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
             f"<rect x='-20' y='-210' width='40' height='96' rx='10' fill='#f2a541' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-22' y='-226' width='44' height='22' rx='6' fill='#cfd6de' stroke='{INK}' stroke-width='6'/></g>")
    # martillo: gira en torno a un pivote a la derecha
    ang = hammer_angle(t) if out <= 0 else 70
    px, py = cx + 260, cy - 190
    p.append(f"<g transform='translate({px:.1f},{py:.1f}) rotate({ang:.1f})'>"
             f"<rect x='-250' y='-12' width='250' height='24' rx='11' fill='#b5713d' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-60' y='-14' width='60' height='28' rx='10' fill='#2f3a4a' stroke='{INK}' stroke-width='6'/>"
             f"<rect x='-300' y='-46' width='70' height='92' rx='12' fill='#6b7685' stroke='{INK}' stroke-width='{LW}'/>"
             f"<rect x='-292' y='-38' width='16' height='76' rx='6' fill='#a7b1bd'/></g>")
    p.append("</g>")
    # chispas y estrellitas de golpe
    lh = last_hit(t)
    if lh < 0.3 and out <= 0 and t > 2.4:
        k = lh / 0.3
        for a, r in SPARKS:
            rr = r * (0.4 + k * 1.2)
            x, y = cx + ox + rr * math.cos(a), cy - 30 + oy - abs(rr * math.sin(a)) * 0.9
            p.append(f"<path d='M{x:.0f} {y-14:.0f} L{x+5:.0f} {y-4:.0f} L{x+15:.0f} {y:.0f} L{x+5:.0f} {y+4:.0f} L{x:.0f} {y+14:.0f} "
                     f"L{x-5:.0f} {y+4:.0f} L{x-15:.0f} {y:.0f} L{x-5:.0f} {y-4:.0f} Z' fill='#ffd23f' stroke='{INK}' stroke-width='3' opacity='{1-k:.2f}'/>")
    return "".join(p)


def opener(t, top_pt):
    """Abrelatas de mariposa (genérico): llega volando brillando y se engancha al borde de la lata."""
    a = seg(t, 6.35, 6.85)
    if a <= 0:
        return ""
    tx, ty = top_pt
    gx = lerp(1250, tx + RW + 10, a); gy = lerp(1000, ty + 10, a) - 30 * math.sin(math.pi * a)
    away = seg(t, 7.0, 7.6)
    gx += lerp(0, 120, away); gy += lerp(0, 40, away)
    rot = lerp(-70, -20, a) + lerp(0, 15, away) + 4 * math.sin(t * 6)
    spin = (t - 6.35) * 900
    p = [f"<g transform='translate({gx:.1f},{gy:.1f}) rotate({rot:.1f})'>"]
    # brillo detrás
    p.append(f"<circle r='{90 + 10*math.sin(t*12):.0f}' fill='url(#glowO)'/>")
    # mangos rojos
    p.append(f"<path d='M10 -16 L250 -40 Q272 -40 272 -22 L268 -10 L12 4 Z' fill='#e8483c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    p.append(f"<path d='M10 10 L250 30 Q272 32 270 48 L262 58 L8 26 Z' fill='#d63a30' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cabeza metálica con rueda de corte
    p.append(f"<rect x='-40' y='-38' width='80' height='76' rx='18' fill='#cfd6de' stroke='{INK}' stroke-width='{LW}'/>")
    p.append(f"<g transform='rotate({spin:.0f})'><circle r='22' fill='#9aa5b1' stroke='{INK}' stroke-width='6'/>"
             + "".join(f"<line x1='0' y1='0' x2='{22*math.cos(math.radians(k)):.1f}' y2='{22*math.sin(math.radians(k)):.1f}' stroke='{INK}' stroke-width='4'/>" for k in range(0, 360, 60))
             + "</g>")
    # llave de mariposa
    p.append(f"<g transform='translate(-40,-60) rotate({spin*0.5:.0f})'>"
             f"<ellipse cx='-34' cy='0' rx='34' ry='16' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>"
             f"<ellipse cx='34' cy='0' rx='34' ry='16' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>"
             f"<circle r='12' fill='#cfd6de' stroke='{INK}' stroke-width='5'/></g>")
    p.append("</g>")
    return "".join(p)


def frame(t):
    rev = seg(t, 6.6, 7.4)
    dim = seg(t, 4.4, 5.2) * (1 - rev)          # la cocina se apaga un poco mientras pasa el tiempo
    wall_t = mix(mix("#fbe9c8", "#c9b79a", dim), "#fff3cf", rev)
    wall_b = mix(mix("#f6d9a8", "#b49a78", dim), "#ffe29a", rev)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_t}'/><stop offset='1' stop-color='{wall_b}'/></linearGradient>"
            f"<radialGradient id='glowO'><stop offset='0' stop-color='#fff7c2' stop-opacity='0.95'/><stop offset='1' stop-color='#ffd23f' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='burst'><stop offset='0' stop-color='#fffbe0' stop-opacity='{0.95*rev:.3f}'/>"
            f"<stop offset='0.35' stop-color='#ffe27a' stop-opacity='{0.75*rev:.3f}'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='beam' x1='0' y1='1' x2='0' y2='0'><stop offset='0' stop-color='#fff7c2' stop-opacity='0.95'/><stop offset='1' stop-color='#ffe27a' stop-opacity='0'/></linearGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    # papel pintado suave arriba (lunares grandes y tenues)
    for i in range(6):
        for j in range(9):
            x = 90 + i * 180 + (90 if j % 2 else 0); y = 70 + j * 105
            s.append(f"<circle cx='{x}' cy='{y}' r='12' fill='#ffffff' opacity='0.35'/>")
    # zócalo de azulejos (detrás de la encimera)
    z = 1 + 0.16 * seg(t, 6.6, 7.9)
    sc = [f"<rect x='0' y='960' width='{W}' height='{COUNTER-960}' fill='{mix(mix('#bfe7e0', '#8fb0aa', dim), '#d4f5ee', rev)}'/>"]
    for y in range(960, COUNTER, 80):
        sc.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='#ffffff' stroke-width='5' opacity='0.8'/>")
    for x in range(0, W + 1, 80):
        sc.append(f"<line x1='{x}' y1='960' x2='{x}' y2='{COUNTER}' stroke='#ffffff' stroke-width='5' opacity='0.8'/>")
    sc.append(f"<line x1='0' y1='960' x2='{W}' y2='960' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(window(t, rev))
    # balda con tarros a la izquierda (contexto de cocina)
    sc.append(f"<rect x='-20' y='1030' width='230' height='22' rx='8' fill='#a0623a' stroke='{INK}' stroke-width='7'/>")
    for jx, jh, col in ((30, 90, '#ffb3c1'), (95, 120, '#9be36b'), (160, 80, '#ffd23f')):
        sc.append(f"<rect x='{jx-26}' y='{1030-jh}' width='52' height='{jh}' rx='10' fill='{col}' stroke='{INK}' stroke-width='6'/>"
                  f"<rect x='{jx-30}' y='{1030-jh-14}' width='60' height='18' rx='5' fill='#8d5a3b' stroke='{INK}' stroke-width='5'/>")
    # rayos y halo de la revelación (detrás de la lata)
    canb, lid, top_pt = can(t)
    if rev > 0:
        cx, cy = top_pt
        rays = []
        for k in range(14):
            a = math.radians(k * (360 / 14) + t * 25)
            r1 = 1200 * rev
            rays.append(f"<path d='M{cx:.0f} {cy:.0f} L{cx + r1*math.cos(a - 0.09):.0f} {cy + r1*math.sin(a - 0.09):.0f} "
                        f"L{cx + r1*math.cos(a + 0.09):.0f} {cy + r1*math.sin(a + 0.09):.0f} Z' fill='#fff2a8' opacity='{0.5*rev:.2f}'/>")
        sc.append("".join(rays))
        sc.append(f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{700*rev:.0f}' fill='url(#burst)'/>")
    # encimera y armarios
    sc.append(f"<rect x='-20' y='{COUNTER}' width='{W+40}' height='44' fill='#e9b87a' stroke='{INK}' stroke-width='{LW}'/>")
    sc.append(f"<rect x='-20' y='{COUNTER+44}' width='{W+40}' height='{H-COUNTER}' fill='{mix(mix('#3c8dbc', '#2c6a8e', dim), '#4aa3d6', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for dx0 in (30, 560):
        sc.append(f"<rect x='{dx0}' y='{COUNTER+80}' width='490' height='360' rx='18' fill='{mix(mix('#4aa3d6', '#357aa2', dim), '#62b8ea', rev)}' stroke='{INK}' stroke-width='7'/>"
                  f"<rect x='{dx0 + (420 if dx0 == 30 else 40)}' y='{COUNTER+200}' width='26' height='90' rx='12' fill='#ffd23f' stroke='{INK}' stroke-width='6'/>")
    # haz de luz que sale de la lata abierta
    gone = seg(t, 6.85, 7.2)
    if gone > 0:
        cx, cy = top_pt
        sc.append(f"<path d='M{cx-RW+14:.0f} {cy:.0f} L{cx-RW-90:.0f} {cy-520:.0f} L{cx+RW+90:.0f} {cy-520:.0f} L{cx+RW-14:.0f} {cy:.0f} Z' fill='url(#beam)' opacity='{gone:.2f}'/>")
    sc.append(canb)
    # telaraña que crece en la esquina de la lata (paso del tiempo)
    web = seg(t, 4.6, 6.2) * (1 - seg(t, 6.6, 6.9))
    if web > 0.01:
        wx, wy = top_pt[0] - RW + 6, top_pt[1] + 8
        r = 120 * web
        w = [f"<g opacity='{min(1, web*1.5):.2f}'>"]
        for k in range(5):
            a = math.radians(-180 + k * 22.5)
            w.append(f"<line x1='{wx:.0f}' y1='{wy:.0f}' x2='{wx + r*math.cos(a):.0f}' y2='{wy + r*math.sin(a):.0f}' stroke='#ffffff' stroke-width='4'/>")
        for rr in (0.35, 0.65, 0.95):
            pts = " ".join(f"{wx + r*rr*math.cos(math.radians(-180 + k*22.5)):.0f},{wy + r*rr*math.sin(math.radians(-180 + k*22.5)):.0f}" for k in range(5))
            w.append(f"<polyline points='{pts}' fill='none' stroke='#ffffff' stroke-width='3'/>")
        w.append(f"<line x1='{wx:.0f}' y1='{wy:.0f}' x2='{wx:.0f}' y2='{wy - 40*web:.0f}' stroke='#ffffff' stroke-width='3'/>"
                 f"<circle cx='{wx:.0f}' cy='{wy - 40*web - 9:.0f}' r='10' fill='{INK}'/></g>")
        s_web = "".join(w)
        sc.append(s_web)
    # zzz de la lata dormida
    zz = seg(t, 5.0, 5.4) * (1 - seg(t, 6.3, 6.5))
    if zz > 0.01:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            x = top_pt[0] + 120 + ph * 60 + k * 10; y = top_pt[1] + 40 - ph * 150
            sz = 18 + k * 8
            sc.append(f"<path d='M{x:.0f} {y:.0f} l{sz} 0 l{-sz} {sz} l{sz} 0' fill='none' stroke='#ffffff' stroke-width='7' stroke-linejoin='round' opacity='{zz*(1-ph):.2f}'/>")
    sc.append(tools(t, top_pt))
    sc.append(lid)
    sc.append(opener(t, top_pt))
    # confeti al abrirse
    cf = seg(t, 6.9, 7.1)
    if cf > 0:
        k = t - 6.9
        cx, cy = top_pt
        for vx, vy, ph, col in CONFETTI:
            x = cx + vx * 520 * min(1, k * 1.4) + 20 * math.sin(t * 4 + ph)
            y = cy - vy * 700 * min(1, k * 1.6) + 260 * k * k
            if y < 1900:
                sc.append(f"<rect x='{x:.0f}' y='{y:.0f}' width='22' height='12' rx='3' fill='{col}' stroke='{INK}' stroke-width='3' "
                          f"transform='rotate({(t*300 + ph*60) % 360:.0f} {x:.0f} {y:.0f})'/>")
    # polvo flotando en la luz
    for px, py, pr, sp, ph in DUST:
        yy = (py - t * sp) % 950 + 950
        sc.append(f"<circle cx='{px + 18*math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fff6dc' opacity='0.5'/>")
    s.append(zoom(CX, 1250, z, "".join(sc)))
    s.append("</svg>")
    return "".join(s)
