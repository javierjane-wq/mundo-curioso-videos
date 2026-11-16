"""2026-11-16-c1 · Química cotidiana: la cebolla te hace llorar porque, al cortarla, se rompen sus
células y se forma un gas irritante (óxido de syn-propanotial, syn-propanethial-S-oxide) que llega a
los ojos; los ojos lloran para limpiarlo (Library of Congress «Everyday Mysteries», Chemistry World).

Una cebolla entra rodando y aterriza en la tabla de cortar; un niño se asoma por detrás de la
encimera. Llega el cuchillo, ¡zas!, la parte en dos y la sigue picando (saltan gotitas: se rompen
las células). Empiezan a salir hilillos casi invisibles que flotan hacia los ojos del niño, que
se le humedecen. En la REVELACION el gas se vuelve verde brillante y envuelve sus ojos: el niño
cierra los ojos y le salen chorros de lágrimas, mientras la cámara se acerca.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, svg, zoom, rebote

DUR = 10.0
REVELACION = 7.45   # el gas se ve verde y el niño rompe a llorar: golpe musical
MUSICA = 7

rng = np.random.default_rng(1116)
GAS = [(rng.uniform(0, 1), rng.uniform(-70, 70), rng.uniform(-60, 60), rng.uniform(-45, 45),
        rng.uniform(0.8, 1.4), rng.uniform(0, 6.28)) for _ in range(46)]
MOTES = [(rng.uniform(0, W), rng.uniform(1000, 1650), rng.uniform(2.5, 5), rng.uniform(10, 30), rng.uniform(0, 6.28)) for _ in range(22)]
DROPS = [(rng.uniform(-1, 1), rng.uniform(0.6, 1.2), rng.uniform(5, 9)) for _ in range(9)]

ONX, ONY = 380, 1555        # centro de la cebolla sobre la tabla
KIDX, KIDY = 805, 1500      # centro de la cabeza del niño
EYES = [(KIDX - 52, KIDY - 22), (KIDX + 52, KIDY - 22)]
COUNTER = 1690
CHOPS = [2.78, 3.75, 4.45]
CHOP_X = [ONX, ONX - 150, ONX - 95]  # cuchilladas (la primera parte la cebolla)

ONION = "M0 -150 C30 -110 110 -70 110 10 C110 80 60 110 0 110 C-60 110 -110 80 -110 10 C-110 -70 -30 -110 0 -150 Z"
HALF_L = "M0 -150 C-30 -110 -110 -70 -110 10 C-110 80 -60 110 0 110 Z"
SKIN = "#d89a4a"; SKIN_D = "#b8742e"; FLESH = "#fbf1dc"; RING = "#e3c9e8"


def background(t, rev):
    wall_t = mix("#c4ebe1", "#d9f3b8", rev * 0.6); wall_b = mix("#a3dccd", "#bfe79a", rev * 0.6)
    s = [f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    # azulejos
    for y in range(-20, COUNTER, 120):
        s.append(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='#ffffff' stroke-width='5' opacity='0.45'/>")
    for x in range(60, W, 120):
        s.append(f"<line x1='{x}' y1='0' x2='{x}' y2='{COUNTER}' stroke='#ffffff' stroke-width='5' opacity='0.45'/>")
    # luz suave de ventana
    s.append(f"<ellipse cx='880' cy='420' rx='520' ry='420' fill='url(#light)'/>")
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_t}'/>"
            f"<stop offset='1' stop-color='{wall_b}'/></linearGradient>"
            "<radialGradient id='light'><stop offset='0' stop-color='#ffffff' stop-opacity='0.45'/>"
            "<stop offset='1' stop-color='#ffffff' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='gasglow'><stop offset='0' stop-color='#d8ff6a' stop-opacity='{0.75*rev:.3f}'/>"
            f"<stop offset='0.5' stop-color='#9be22e' stop-opacity='{0.4*rev:.3f}'/>"
            "<stop offset='1' stop-color='#7bd11c' stop-opacity='0'/></radialGradient>")
    return "".join(s), defs


def basil(t):
    """Maceta de albahaca a la izquierda, con hojas que se mecen."""
    sw = 4 * math.sin(t * 1.7)
    g = [f"<g transform='translate(52,{COUNTER}) scale(0.92)'>"]
    for i, (a, l) in enumerate([(-35, 120), (-10, 150), (15, 135), (38, 110), (0, 95)]):
        ang = a + sw * (1 + 0.2 * i)
        g.append(f"<g transform='translate(0,-95) rotate({ang:.1f})'>"
                 f"<line x1='0' y1='0' x2='0' y2='{-l}' stroke='#3f8f3a' stroke-width='8'/>"
                 f"<path d='M0 {-l} q-38 -10 -30 -50 q32 6 30 50 Z' fill='#5cbf4a' stroke='{INK}' stroke-width='6'/>"
                 f"<path d='M0 {-l + 45} q36 -6 34 -46 q-36 4 -34 46 Z' fill='#4fae40' stroke='{INK}' stroke-width='6'/></g>")
    g.append(f"<path d='M-62 -100 L62 -100 L48 0 L-48 0 Z' fill='#e2683f' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-72' y='-118' width='144' height='28' rx='8' fill='#f08a5d' stroke='{INK}' stroke-width='{LW}'/>")
    g.append("</g>")
    return "".join(g)


def jar(t):
    g = [f"<g transform='translate(1022,{COUNTER})'>",
         f"<rect x='-50' y='-150' width='100' height='150' rx='22' fill='#ffe08a' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='-56' y='-178' width='112' height='38' rx='10' fill='#e24b4b' stroke='{INK}' stroke-width='{LW}'/>",
         f"<path d='M-30 -120 Q-34 -70 -28 -30' stroke='#fff6cf' stroke-width='12' fill='none' stroke-linecap='round'/>",
         "</g>"]
    return "".join(g)


def kid(t, rev, worry, tear):
    rise = seg(t, 0.1, 1.1)
    y = lerp(KIDY + 130, KIDY, rise) + 4 * math.sin(t * 2.1)
    sway = 3 * math.sin(t * 1.3) - 6 * seg(t, 5.0, 6.5) * (1 - rev)   # se echa un poco hacia atrás
    blink_p = 3.3 if worry < 0.5 else 1.1
    blink = 0.12 if ((t + 1.4) % blink_p) < 0.13 else 1.0
    g = [f"<g transform='translate({KIDX},{y:.1f}) rotate({sway:.1f})'>"]
    # hombros / camiseta de rayas
    g.append(f"<path d='M-170 200 Q-160 120 -60 118 L60 118 Q160 120 170 200 Z' fill='#ff8a3d' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for yy in (150, 180):
        g.append(f"<path d='M-160 {yy} L160 {yy}' stroke='#ffd04a' stroke-width='14'/>")
    g.append(f"<path d='M-170 200 Q-160 120 -60 118 L60 118 Q160 120 170 200' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<rect x='-34' y='95' width='68' height='40' fill='#f2b98a' stroke='{INK}' stroke-width='7'/>")
    # orejas
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{sx*142}' cy='5' rx='28' ry='36' fill='#f6c79a' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M{sx*140} -10 Q{sx*152} 5 {sx*140} 20' stroke='#d99c6e' stroke-width='6' fill='none'/>")
    # cabeza
    g.append(f"<ellipse cx='0' cy='0' rx='145' ry='138' fill='#f6c79a' stroke='{INK}' stroke-width='{LW}'/>")
    # pelo con mechón que bota
    tuft = 8 * math.sin(t * 6)
    g.append(f"<path d='M-140 -30 Q-150 -130 -40 -140 Q40 -160 110 -120 Q150 -90 142 -30 Q120 -80 60 -88 Q0 -70 -60 -92 Q-110 -80 -140 -30 Z' fill='#5a3522' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<g transform='translate(-10,-140) rotate({tuft:.1f})'><path d='M0 0 Q-10 -50 25 -70 Q10 -35 30 -10 Z' fill='#5a3522' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")
    # mejillas
    for sx in (-1, 1):
        g.append(f"<ellipse cx='{sx*92}' cy='48' rx='26' ry='15' fill='{mix('#ff9a8a', '#ff5f5f', rev)}' opacity='0.75'/>")
    # cejas: preocupadas
    for sx in (-1, 1):
        ex = sx * 52
        inner = lerp(-80, -96, worry); outer = lerp(-84, -70, worry)
        g.append(f"<path d='M{ex - sx*30:.0f} {outer:.1f} Q{ex:.0f} {lerp(-96, -92, worry):.1f} {ex + sx*30:.0f} {inner:.1f}' "
                 f"fill='none' stroke='{INK}' stroke-width='9' stroke-linecap='round' transform='scale({1 if sx > 0 else 1},1)'/>")
    # ojos
    look = -0.55 + 0.25 * seg(t, 5.2, 6.2)   # miran a la cebolla (izquierda)
    for sx in (-1, 1):
        ex = sx * 52
        if rev > 0.5:
            # ojos cerrados con fuerza: > <
            d = 18
            g.append(f"<path d='M{ex - sx*d:.0f} -42 L{ex + sx*d:.0f} -22 L{ex - sx*d:.0f} -4' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round' stroke-linejoin='round'/>")
        else:
            wet = clamp(worry)
            g.append(f"<g transform='translate({ex},-22) scale(1,{blink})'>"
                     f"<ellipse rx='32' ry='37' fill='#fff' stroke='{INK}' stroke-width='7'/>"
                     f"<circle cx='{look*14:.1f}' cy='4' r='17' fill='#3b2a20'/>"
                     f"<circle cx='{look*14 - 6:.1f}' cy='-4' r='6' fill='#fff'/>"
                     f"<circle cx='{look*14 + 6:.1f}' cy='9' r='3' fill='#fff'/>"
                     + (f"<path d='M-26 22 Q0 38 26 22' fill='none' stroke='#7fd0ff' stroke-width='{6*wet:.1f}' stroke-linecap='round' opacity='{wet:.2f}'/>" if wet > 0.05 else "")
                     + "</g>")
    # lágrima que se forma antes de la revelación
    if tear > 0.02 and rev < 0.5:
        r = 6 + 6 * tear
        ty = 18 + 30 * clamp((t - 6.6) / 0.8)
        g.append(f"<path d='M{84} {ty - r*1.8:.1f} Q{84 + r} {ty:.1f} {84} {ty + r:.1f} Q{84 - r} {ty:.1f} {84} {ty - r*1.8:.1f} Z' fill='#8fdcff' stroke='{INK}' stroke-width='4' opacity='{tear:.2f}'/>")
    # nariz
    g.append(f"<path d='M-6 4 Q8 30 -10 32' fill='none' stroke='#c98a5c' stroke-width='7' stroke-linecap='round'/>")
    # boca
    if rev > 0.5:
        op = 22 + 6 * math.sin(t * 14)
        g.append(f"<path d='M-46 62 Q0 {62 + op:.1f} 46 62 Q0 52 -46 62 Z' fill='#8a2f2f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    elif worry > 0.5:
        g.append(f"<path d='M-30 72 Q-15 62 0 72 Q15 82 30 70' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    else:
        g.append(f"<path d='M-40 60 Q0 98 40 60' fill='#8a2f2f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>"
                 f"<path d='M-22 78 Q0 88 22 78' fill='#ff8a8a'/>")
    # chorros de lágrimas tras la revelación
    if rev > 0.02:
        for sx in (-1, 1):
            ex = sx * 52 + sx * 26
            path = f"M{ex} -16 Q{ex + sx*150} -170 {ex + sx*235} 130"
            g.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='{30*rev:.1f}' stroke-linecap='round' opacity='{rev:.2f}'/>")
            g.append(f"<path d='{path}' fill='none' stroke='#7fd6ff' stroke-width='{20*rev:.1f}' stroke-linecap='round' opacity='{rev:.2f}'/>")
            g.append(f"<path d='{path}' fill='none' stroke='#e6f8ff' stroke-width='{6*rev:.1f}' stroke-linecap='round' stroke-dasharray='18 26' stroke-dashoffset='{-t*160:.0f}' opacity='{rev:.2f}'/>")
            for i in range(5):
                u = ((t - REVELACION) * 1.6 + i / 5) % 1
                dx = ex + sx * (200 + 40 * u); dy = 140 + 260 * u * u
                g.append(f"<path d='M{dx:.1f} {dy - 20:.1f} Q{dx + 11:.1f} {dy:.1f} {dx:.1f} {dy + 10:.1f} Q{dx - 11:.1f} {dy:.1f} {dx:.1f} {dy - 20:.1f} Z' fill='#8fdcff' stroke='{INK}' stroke-width='4' opacity='{rev * (1 - u):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def hands(t):
    rise = seg(t, 0.5, 1.3)
    g = []
    for x, fl in ((675, 1), (935, -1)):
        y = lerp(COUNTER + 60, COUNTER + 6, rise)
        g.append(f"<g transform='translate({x},{y:.1f}) scale({fl},1)'>"
                 f"<path d='M-46 10 Q-50 -34 -10 -36 Q40 -40 48 -6 Q50 14 40 22 L-40 22 Z' fill='#f6c79a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"
                 + "".join(f"<line x1='{fx}' y1='-6' x2='{fx}' y2='18' stroke='#c98a5c' stroke-width='5' stroke-linecap='round'/>" for fx in (-18, 4, 26))
                 + "</g>")
    return "".join(g)


def counter():
    s = [f"<rect x='0' y='{COUNTER}' width='{W}' height='54' fill='#f7e2b5' stroke='{INK}' stroke-width='{LW}'/>",
         f"<line x1='0' y1='{COUNTER + 14}' x2='{W}' y2='{COUNTER + 14}' stroke='#fff4d8' stroke-width='6'/>",
         f"<rect x='-10' y='{COUNTER + 54}' width='{W + 20}' height='{H - COUNTER}' fill='#ef7b5b' stroke='{INK}' stroke-width='{LW}'/>"]
    for x0 in (30, 380, 730):
        s.append(f"<rect x='{x0}' y='{COUNTER + 84}' width='320' height='200' rx='18' fill='#f4906f' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<rect x='{x0 + 130}' y='{COUNTER + 110}' width='60' height='16' rx='8' fill='#ffd24a' stroke='{INK}' stroke-width='5'/>")
    return "".join(s)


def board():
    return (f"<ellipse cx='{ONX}' cy='{COUNTER + 4}' rx='250' ry='16' fill='#000' opacity='0.18'/>"
            f"<rect x='140' y='{COUNTER - 30}' width='490' height='36' rx='16' fill='#d9a066' stroke='{INK}' stroke-width='{LW}'/>"
            f"<circle cx='180' cy='{COUNTER - 12}' r='8' fill='#a86c3a' stroke='{INK}' stroke-width='4'/>"
            f"<line x1='230' y1='{COUNTER - 20}' x2='590' y2='{COUNTER - 20}' stroke='#eec08a' stroke-width='5' stroke-linecap='round'/>")


def onion_whole(x, y, rot, sx=1.0, sy=1.0, shiver=0.0):
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) translate(0,110) scale({sx:.3f},{sy:.3f}) translate({shiver:.1f},-110)'>"]
    # raíces
    for rx in (-24, -8, 8, 24):
        g.append(f"<path d='M{rx/2:.0f} 106 Q{rx:.0f} 122 {rx*1.3:.0f} 130' fill='none' stroke='#c9a06a' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='{ONION}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in (-0.6, -0.25, 0.25, 0.6):
        g.append(f"<path d='M0 -145 Q{110*k*1.6:.0f} -20 {60*k:.0f} 106' fill='none' stroke='{SKIN_D}' stroke-width='5' stroke-linecap='round'/>")
    g.append(f"<path d='M-70 -30 Q-80 30 -50 70' fill='none' stroke='#f3c27c' stroke-width='12' stroke-linecap='round'/>")
    g.append(f"<path d='M0 -148 Q8 -170 2 -190' fill='none' stroke='{INK}' stroke-width='12' stroke-linecap='round'/>"
             f"<path d='M0 -148 Q8 -170 2 -190' fill='none' stroke='#c9a06a' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    return "".join(g)


def onion_half(x, y, rot, side, sc=1.0):
    """Media cebolla con la cara cortada (anillos concéntricos). side=1: abombada a la derecha."""
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f}) scale({side*sc:.3f},{sc:.3f})'>"]
    g.append(f"<path d='{HALF_L}' fill='{SKIN}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<g transform='translate(0,25) scale(0.88) translate(0,-25)'><path d='{HALF_L}' fill='{FLESH}'/></g>")
    for k in (0.72, 0.54, 0.37, 0.2):
        g.append(f"<g transform='translate(0,25) scale({k}) translate(0,-25)'><path d='{HALF_L}' fill='none' stroke='{RING}' stroke-width='{6/k:.1f}'/></g>")
    g.append(f"<path d='M0 -150 L0 110' stroke='{INK}' stroke-width='6'/>")
    g.append(f"<path d='{HALF_L}' fill='none' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def onion(t):
    if t < 2.9:
        k = seg(t, 0, 1.15)
        x = lerp(-40, ONX, k)
        hop = abs(math.sin(k * math.pi * 2.0)) * 120 * (1 - k)
        rot = (x - ONX) / 110 * 57.3 * 0.6 if k < 1 else 0
        land = clamp((t - 1.15) / 0.35)
        sq = 1 - 0.14 * math.sin(math.pi * land) if 1.15 <= t < 1.5 else 1
        shiver = 4 * math.sin(t * 60) * seg(t, 2.15, 2.4)   # tiembla al ver el cuchillo
        wob = 2.5 * math.sin(t * 2.4) if t > 1.5 else 0
        return onion_whole(x, ONY - hop, rot + wob, 1 / sq ** 0.5, sq, shiver)
    # se parte en dos y cada mitad cae tumbada, con la cara cortada a la vista
    k = seg(t, 2.92, 3.3)
    sc = lerp(1.0, 0.85, k)
    j = sum(5 * math.sin((t - c) * 45) * clamp(1 - (t - c) / 0.35) for c in CHOPS[1:] if t > c)
    yl = lerp(ONY, COUNTER - 30, k) + (0 if k > 0.99 else -40 * math.sin(math.pi * k))
    left = onion_half(lerp(ONX - 4, ONX - 135, k), yl + (j if t > CHOPS[1] else 0), lerp(0, 90, k), 1, sc)
    right = onion_half(lerp(ONX + 4, ONX + 135, k), yl, lerp(0, -90, k), -1, sc)
    return left + right


def knife(t):
    if t < 1.9 or t > 5.7:
        return ""
    enter = seg(t, 1.9, 2.5); leave = seg(t, 5.0, 5.6)
    rest_x = ONX if t < 3.3 else (lerp(ONX, CHOP_X[1], seg(t, 3.25, 3.55)) if t < 4.0 else lerp(CHOP_X[1], CHOP_X[2], seg(t, 4.0, 4.3)))
    x = lerp(ONX + 520, rest_x, enter) + 600 * leave
    y = lerp(1080, 1360, enter) - 520 * leave
    down = 0.0
    for c in CHOPS:
        if c - 0.12 <= t < c: down = max(down, ease((t - c + 0.12) / 0.12))
        elif c <= t < c + 0.35: down = max(down, 1 - ease((t - c) / 0.35))
    y += down * (COUNTER - 30 - 1360)
    ang = -8 + 8 * down - 20 * leave
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f})'>",
         f"<path d='M140 0 L-150 0 Q-188 -4 -198 -22 Q-110 -100 0 -104 L140 -104 Z' fill='#dfe7f0' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M-140 -12 L130 -12' stroke='#ffffff' stroke-width='7' stroke-linecap='round'/>",
         f"<path d='M-60 -70 L110 -78' stroke='#b9c6d4' stroke-width='6' stroke-linecap='round'/>",
         f"<rect x='136' y='-104' width='26' height='104' rx='6' fill='#9aa6b4' stroke='{INK}' stroke-width='7'/>",
         f"<rect x='158' y='-92' width='170' height='76' rx='26' fill='#7a3f22' stroke='{INK}' stroke-width='{LW}'/>",
         "".join(f"<circle cx='{cx}' cy='-54' r='9' fill='#e8d3a8' stroke='{INK}' stroke-width='4'/>" for cx in (200, 250, 300)),
         "</g>"]
    return "".join(g)


def drops(t):
    """Gotitas que saltan al cortar: se rompen las células."""
    g = []
    for i, c in enumerate(CHOPS):
        if c <= t < c + 0.7:
            u = (t - c) / 0.7
            cx = CHOP_X[i]
            for dx, sp, r in DROPS:
                x = cx + dx * 150 * u
                y = COUNTER - 60 - sp * 330 * u + 520 * u * u
                g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='#f4fbff' stroke='{INK}' stroke-width='3' opacity='{1 - u:.2f}'/>")
            if u < 0.4:
                a = 1 - u / 0.4
                for k in range(6):
                    ang = math.radians(-160 + k * 28)
                    r1, r2 = 40 + 90 * u, 70 + 140 * u
                    g.append(f"<line x1='{cx + r1*math.cos(ang):.0f}' y1='{COUNTER - 40 + r1*math.sin(ang):.0f}' x2='{cx + r2*math.cos(ang):.0f}' y2='{COUNTER - 40 + r2*math.sin(ang):.0f}' "
                             f"stroke='#ffffff' stroke-width='8' stroke-linecap='round' opacity='{a:.2f}'/>")
    return "".join(g)


def gas(t, rev):
    strength = 0.25 * seg(t, 3.3, 4.6) + 0.3 * seg(t, 5.0, 7.2) + 0.45 * rev
    if strength < 0.01:
        return ""
    col = mix("#f1ecff", "#c8ff3e", rev); col2 = mix("#d9d0f2", "#8fe32a", rev)
    g = []
    # hilillos ondulados
    for i, (dx, cy) in enumerate(((-40, 0), (30, 30), (95, -20))):
        sx, sy = ONX + dx + 30, ONY - 40
        ex, ey = EYES[i % 2][0] - 10, EYES[i % 2][1] + 10
        d = f"M{sx} {sy} C{sx + 40} {sy - 160 + cy} {ex - 220} {ey - 200 + cy} {ex} {ey}"
        g.append(f"<path d='{d}' fill='none' stroke='{col2}' stroke-width='{lerp(10, 22, rev):.1f}' stroke-linecap='round' "
                 f"stroke-dasharray='40 46' stroke-dashoffset='{-t*120 - i*30:.0f}' opacity='{strength*0.9:.2f}'/>")
    # nubecillas
    for ph, ox, oy, ex_j, sz, wph in GAS:
        u = (t * 0.32 + ph) % 1
        p0 = (ONX + ox * 0.8 + 30, ONY - 60); p1 = (ONX + 150 + oy, ONY - 270 + ox)
        p2 = (EYES[0][0] - 95 + ex_j * 0.5, EYES[0][1] + 15 + ex_j * 0.6)
        x = (1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0] + 14 * math.sin(t * 3 + wph)
        y = (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1] + 10 * math.cos(t * 2.5 + wph)
        r = (10 + 16 * u) * sz * (1 + 0.3 * rev)
        a = strength * math.sin(math.pi * u)
        if a > 0.02:
            g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='{col}' opacity='{a:.2f}'/>")
    return "".join(g)


def gas_cloud(t, rev):
    """En la revelación, nube verde que rodea los ojos."""
    if rev < 0.01:
        return ""
    g = []
    for i in range(8):
        a = t * 1.6 + i * 0.785
        x = KIDX + 215 * math.cos(a); y = KIDY - 40 + 150 * math.sin(a)
        if math.sin(a) > 0.55: continue   # por delante de la cara no: se verían los ojos tapados
        g.append(f"<path d='M{x - 34:.0f} {y:.0f} q8 -30 34 -22 q20 -24 40 2 q24 6 6 26 q-40 10 -80 -6 Z' fill='#c8ff3e' stroke='{INK}' stroke-width='5' opacity='{0.85*rev:.2f}'/>")
    return "".join(g)


def motes(t, rev):
    g = []
    for x, y, r, sp, ph in MOTES:
        yy = (y - t * sp) % 700 + 1000
        a = 0.35 + 0.3 * math.sin(t * 2 + ph)
        g.append(f"<circle cx='{x + 18*math.sin(t*0.8 + ph):.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='{mix('#ffffff', '#eaffa0', rev)}' opacity='{a:.2f}'/>")
    return "".join(g)


def frame(t):
    rev = seg(t, REVELACION - 0.05, REVELACION + 0.3)
    worry = seg(t, 5.2, 6.2)
    tear = seg(t, 6.3, 7.2)
    bg, defs = background(t, rev)
    z = 1 + 0.2 * seg(t, REVELACION - 0.1, 9.6)
    glow = f"<circle cx='{KIDX}' cy='{KIDY - 30}' r='{lerp(120, 360, rev):.0f}' fill='url(#gasglow)'/>" if rev > 0.01 else ""
    scene = "".join([motes(t, rev), glow, kid(t, rev, worry, tear), counter(), basil(t), jar(t), board(), hands(t),
                     onion(t), drops(t), gas(t, rev), gas_cloud(t, rev), knife(t)])
    shake = 6 * math.sin(t * 70) * clamp(1 - (t - REVELACION) / 0.35) if t >= REVELACION else 0
    return svg(bg + f"<g transform='translate({shake:.1f},0)'>" + zoom(640, 1520, z, scene) + "</g>", defs)
