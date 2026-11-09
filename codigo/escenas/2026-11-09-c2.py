"""2026-11-09-c2 · Al congelarse, el agua ocupa alrededor de un 9 % más de volumen (el hielo es
menos denso que el agua líquida): por eso una botella llena de agua revienta en el congelador.

0-2,5 s  una botella de cristal original con cara, llena de agua azul, entra deslizándose
         en el congelador y se coloca sobre la rejilla.
2,5-5 s  hace frío: cae escarcha, el termómetro baja y la botella tirita.
5-7,5 s  el agua se va volviendo hielo desde abajo; la botella se hincha y tiembla.
7,5-10 s REVELACION: el tapón sale disparado, el hielo asoma por el cuello, el cristal se
         agrieta, destello helado y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.45
MUSICA = 5

rng = np.random.default_rng(29)
COPOS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 9), rng.uniform(25, 70), rng.uniform(0, 6.28)) for _ in range(46)]
ESQUIRLAS = [(rng.uniform(-math.pi, 0), rng.uniform(260, 620), rng.uniform(12, 24), rng.uniform(0, 360)) for _ in range(16)]
CX = 540
BOT = 1770     # base de la botella (sobre la rejilla)

BOTELLA = (f"M490 1135 L490 1250 C490 1312 392 1322 392 1402 L392 {BOT - 40} Q392 {BOT} 432 {BOT} "
           f"L648 {BOT} Q688 {BOT} 688 {BOT - 40} L688 1402 C688 1322 590 1312 590 1250 L590 1135 Z")
DENTRO = (f"M504 1150 L504 1252 C504 1324 406 1334 406 1406 L406 {BOT - 46} Q406 {BOT - 14} 438 {BOT - 14} "
          f"L642 {BOT - 14} Q674 {BOT - 14} 674 {BOT - 46} L674 1406 C674 1334 576 1324 576 1252 L576 1150 Z")


def congelador(t, frio, rev):
    """Interior del congelador: pared de fondo, paredes laterales, rejilla y cosas congeladas."""
    s = []
    back_top = mix("#cfeefc", "#eafaff", rev); back_low = mix("#9fd6f2", "#bff0ff", rev)
    s.append(f"<linearGradient id='fondo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{back_top}'/>"
             f"<stop offset='1' stop-color='{back_low}'/></linearGradient>")
    s.append(f"<rect width='{W}' height='{H}' fill='url(#fondo)'/>")
    # paredes laterales en perspectiva
    side = mix("#86c3e6", "#a8e4ff", rev)
    s.append(f"<path d='M0 0 L120 120 L120 1690 L0 1850 Z' fill='{side}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M1080 0 L960 120 L960 1690 L1080 1850 Z' fill='{side}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M0 0 L120 120 L960 120 L1080 0' fill='none' stroke='{INK}' stroke-width='{LW}'/>")
    # nervios suaves en la pared del fondo
    for x in range(220, 960, 150):
        s.append(f"<line x1='{x}' y1='140' x2='{x}' y2='1670' stroke='#ffffff' stroke-width='6' opacity='0.35'/>")
    # escarcha en las esquinas superiores (crece con el frío)
    fr = 0.4 + 0.6 * frio
    for cx, cy, r in ((120, 120, 120), (960, 120, 120), (0, 0, 170), (1080, 0, 170)):
        s.append(f"<circle cx='{cx}' cy='{cy}' r='{r * fr:.0f}' fill='#ffffff' opacity='0.55'/>")
    # carámbanos colgando del techo del fondo
    for i, x in enumerate(range(150, 960, 70)):
        L = (26 + 22 * ((i * 7) % 3)) * (0.5 + 0.5 * frio)
        s.append(f"<path d='M{x - 14} 120 L{x + 14} 120 L{x} {120 + L:.0f} Z' fill='#f4fdff' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    # rejilla (balda) en perspectiva
    s.append(f"<path d='M120 1690 L960 1690 L1080 1850 L0 1850 Z' fill='{mix('#dff4ff', '#f2fcff', rev)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for k in range(1, 9):
        x0 = lerp(120, 960, k / 9); x1 = lerp(0, 1080, k / 9)
        s.append(f"<line x1='{x0:.0f}' y1='1690' x2='{x1:.0f}' y2='1850' stroke='#9bb8c8' stroke-width='6'/>")
    s.append(f"<rect x='-10' y='1850' width='1100' height='26' fill='#c9d8e2' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='0' y='1876' width='1080' height='60' fill='#6fa9cc'/>")
    # bandeja de cubitos (izquierda)
    s.append(f"<path d='M150 1700 L350 1700 L362 1748 L138 1748 Z' fill='#7fd0e8' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for i in range(4):
        bx = 165 + i * 47
        s.append(f"<rect x='{bx}' y='{1672 + 3 * math.sin(t * 3 + i):.0f}' width='38' height='34' rx='8' fill='#f1fbff' stroke='{INK}' stroke-width='5'/>")
    # bolsa de guisantes (derecha)
    s.append(f"<path d='M770 1735 L790 1585 Q850 1560 910 1585 L935 1735 Z' fill='#46b35a' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M790 1585 Q850 1572 910 1585 L905 1598 Q850 1586 795 1598 Z' fill='#2f8a42'/>")
    for px, py in ((830, 1650), (868, 1670), (850, 1695), (885, 1640)):
        s.append(f"<circle cx='{px}' cy='{py}' r='13' fill='#9be36b' stroke='{INK}' stroke-width='4'/>")
    # termómetro (sin números) en la pared izquierda del fondo
    tx, ty = 230, 1180
    s.append(f"<rect x='{tx - 26}' y='{ty}' width='52' height='330' rx='26' fill='#ffffff' stroke='{INK}' stroke-width='{LW}'/>")
    for k in range(6):
        s.append(f"<line x1='{tx + 8}' y1='{ty + 40 + k * 45}' x2='{tx + 22}' y2='{ty + 40 + k * 45}' stroke='{INK}' stroke-width='4'/>")
    lvl = lerp(ty + 50, ty + 260, frio)
    mc = mix("#ff4d4d", "#2f7fe0", frio)
    s.append(f"<rect x='{tx - 9}' y='{lvl:.0f}' width='18' height='{ty + 330 - lvl:.0f}' rx='9' fill='{mc}'/>")
    s.append(f"<circle cx='{tx}' cy='{ty + 340}' r='40' fill='{mc}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<circle cx='{tx - 12}' cy='{ty + 328}' r='10' fill='#ffffff' opacity='0.7'/>")
    return "".join(s)


def botella(t, frio, hielo, rev):
    """Botella de cristal con cara: agua azul que se convierte en hielo desde abajo."""
    entra = seg(t, 0, 1.7)
    x = lerp(620, 0, entra)
    hop = -40 * math.sin(math.pi * clamp(t / 1.7)) if t < 1.7 else 0
    tirita = (2.5 * frio + 9 * seg(t, 5.0, 7.4)) * math.sin(t * 55) * (1 - rev * 0.7)
    hinch = 1 + 0.10 * hielo + 0.03 * rev * math.exp(-(t - REVELACION) * 4 if t > REVELACION else 0)
    tilt = lerp(-14, 0, entra) + 1.5 * math.sin(t * 2.2)
    g = [f"<g transform='translate({x + tirita:.1f},{hop:.1f}) rotate({tilt:.2f},{CX},{BOT}) "
         f"translate({CX},{BOT}) scale({hinch:.4f},1) translate({-CX},{-BOT})'>"]
    g.append(f"<ellipse cx='{CX}' cy='{BOT + 8}' rx='190' ry='22' fill='#2a5a7a' opacity='0.25'/>")
    g.append(f"<clipPath id='dentro'><path d='{DENTRO}'/></clipPath>")
    # cristal
    g.append(f"<path d='{BOTELLA}' fill='{mix('#bfeee6', '#d9f5f2', hielo)}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # contenido: agua y hielo
    g.append("<g clip-path='url(#dentro)'>")
    ola = 6 * math.sin(t * 5)
    g.append(f"<path d='M380 {1172 + ola:.1f} Q540 {1158 - ola:.1f} 700 {1172 + ola:.1f} L700 {BOT} L380 {BOT} Z' fill='{mix('#3fa9f5', '#5cc0ff', frio)}'/>")
    for i in range(6):   # burbujitas subiendo en el agua
        by = BOT - 40 - ((t * 90 + i * 110) % 560)
        bx = 450 + (i * 37) % 180 + 8 * math.sin(t * 3 + i)
        if by > 1420 and (by < BOT - (BOT - 1150) * hielo - 10):
            g.append(f"<circle cx='{bx:.0f}' cy='{by:.0f}' r='{7 + i % 3 * 3}' fill='#bfe9ff' opacity='0.8'/>")
    if hielo > 0:
        top = BOT - (BOT - 1110) * hielo
        g.append(f"<rect x='380' y='{top:.0f}' width='320' height='{BOT - top + 10:.0f}' fill='#cbeaff'/>")
        g.append(f"<line x1='380' y1='{top:.0f}' x2='700' y2='{top:.0f}' stroke='#8fd3ff' stroke-width='8'/>")
        # vetas de cristales de hielo
        for i in range(9):
            yy = BOT - 50 - i * 70
            if yy > top + 10:
                xx = 420 + (i * 61) % 220
                g.append(f"<path d='M{xx} {yy} l30 -24 l26 18 M{xx + 30} {yy - 24} l4 -26' fill='none' stroke='#78bfe8' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    # brillo del cristal
    g.append(f"<path d='M418 1440 L418 {BOT - 70}' stroke='#ffffff' stroke-width='16' stroke-linecap='round' opacity='0.75'/>")
    g.append(f"<path d='M508 1165 L508 1240' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.75'/>")
    # anillo del cuello
    g.append(f"<rect x='478' y='1122' width='124' height='26' rx='9' fill='#bfeee6' stroke='{INK}' stroke-width='7'/>")
    # hielo que asoma por el cuello en la revelación
    if rev > 0:
        sale = 95 * rev
        g.append(f"<path d='M500 1130 L500 {1130 - sale:.0f} Q540 {1105 - sale:.0f} 580 {1130 - sale:.0f} L580 1130 Z' fill='#effbff' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
        g.append(f"<path d='M520 {1135 - sale * 0.8:.0f} l18 20 l14 -16' fill='none' stroke='#8fd3ff' stroke-width='5'/>")
    # grietas del cristal
    if rev > 0:
        a = clamp(rev * 1.5)
        for path in ("M600 1330 l-30 40 l18 22 l-34 46 l14 30", "M470 1600 l40 -26 l-12 -30 l38 -18",
                     "M660 1520 l-36 18 l10 30 l-40 16", "M430 1380 l30 30 l-10 34"):
            g.append(f"<path d='{path}' fill='none' stroke='#ffffff' stroke-width='11' stroke-linecap='round' stroke-linejoin='round' opacity='{a:.2f}'/>")
            g.append(f"<path d='{path}' fill='none' stroke='{INK}' stroke-width='4' stroke-linecap='round' stroke-linejoin='round' opacity='{a:.2f}'/>")
    # cara
    ey = 1500
    blink = 0.12 if (t % 2.7) < 0.12 and t < REVELACION else 1.0
    ojo = lerp(1.0, 1.35, rev)
    preoc = seg(t, 2.6, 3.4) * (1 - rev)
    for ex in (CX - 58, CX + 58):
        g.append(f"<g transform='translate({ex},{ey}) scale({ojo:.3f},{ojo * blink:.3f})'>"
                 f"<ellipse rx='34' ry='40' fill='#ffffff' stroke='{INK}' stroke-width='7'/>"
                 f"<circle cx='{4 * math.sin(t * 1.3):.1f}' cy='6' r='17' fill='{INK}'/>"
                 f"<circle cx='{-4 + 4 * math.sin(t * 1.3):.1f}' cy='-1' r='6' fill='#ffffff'/></g>")
    # cejas preocupadas
    if preoc > 0.02 or rev > 0:
        lift = 14 * rev
        for sgn in (-1, 1):
            ex = CX + sgn * 58
            g.append(f"<path d='M{ex - sgn * 30} {ey - 52 - lift - 12 * preoc:.0f} L{ex + sgn * 26} {ey - 60 - lift + 6 * preoc:.0f}' "
                     f"stroke='{INK}' stroke-width='8' stroke-linecap='round'/>")
    # boca: sonrisa -> dientes castañeteando -> "O" de sorpresa
    my = ey + 82
    if rev > 0.05:
        g.append(f"<ellipse cx='{CX}' cy='{my + 6}' rx='{22 + 8 * rev:.0f}' ry='{28 + 10 * rev:.0f}' fill='#7a1e2a' stroke='{INK}' stroke-width='7'/>")
    elif frio > 0.25:
        ch = 6 + 5 * abs(math.sin(t * 24))
        g.append(f"<rect x='{CX - 40}' y='{my - ch:.1f}' width='80' height='{2 * ch:.1f}' rx='8' fill='#ffffff' stroke='{INK}' stroke-width='6'/>")
        for dx in (-13, 13):
            g.append(f"<line x1='{CX + dx}' y1='{my - ch:.1f}' x2='{CX + dx}' y2='{my + ch:.1f}' stroke='{INK}' stroke-width='4'/>")
    else:
        g.append(f"<path d='M{CX - 34} {my - 6} Q{CX} {my + 28} {CX + 34} {my - 6}' fill='#7a1e2a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # mejillas
    g.append(f"<circle cx='{CX - 108}' cy='{ey + 52}' r='17' fill='#ff9db0' opacity='0.6'/><circle cx='{CX + 108}' cy='{ey + 52}' r='17' fill='#ff9db0' opacity='0.6'/>")
    # tapón: puesto hasta la revelación
    if t < REVELACION:
        g.append(f"<rect x='472' y='1076' width='136' height='58' rx='14' fill='#ff5a5f' stroke='{INK}' stroke-width='{LW}'/>")
        for k in range(5):
            g.append(f"<line x1='{492 + k * 24}' y1='1088' x2='{492 + k * 24}' y2='1122' stroke='#c63d44' stroke-width='6'/>")
    g.append("</g>")
    return "".join(g)


def tapon_volando(t):
    if t < REVELACION:
        return ""
    k = t - REVELACION
    x = CX + 400 * k
    y = 1105 - 400 * k + 300 * k * k
    rot = 400 * k
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({rot:.1f})'>"
            f"<rect x='-68' y='-29' width='136' height='58' rx='14' fill='#ff5a5f' stroke='{INK}' stroke-width='{LW}'/>"
            + "".join(f"<line x1='{-48 + j * 24}' y1='-17' x2='{-48 + j * 24}' y2='17' stroke='#c63d44' stroke-width='6'/>" for j in range(5))
            + "</g>")


def frame(t):
    frio = seg(t, 2.2, 5.2)
    hielo = seg(t, 5.0, 7.4)
    rev = seg(t, REVELACION, REVELACION + 0.35)
    s = ["<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920' viewBox='0 0 1080 1920'><defs>"]
    s.append(f"<radialGradient id='flash'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.95 * rev:.3f}'/>"
             f"<stop offset='0.4' stop-color='#9ff0ff' stop-opacity='{0.6 * rev:.3f}'/><stop offset='1' stop-color='#5cd6ff' stop-opacity='0'/></radialGradient>")
    s.append("</defs>")
    z = 1 + 0.16 * seg(t, REVELACION, 10)
    escena = [congelador(t, frio, rev)]
    # rayos de luz helada detrás de la botella
    if rev > 0:
        for i in range(12):
            a = i * 30 + t * 12
            escena.append(f"<path d='M{CX} 1300 L{CX + 900 * math.cos(math.radians(a - 5)):.0f} {1300 + 900 * math.sin(math.radians(a - 5)):.0f} "
                          f"L{CX + 900 * math.cos(math.radians(a + 5)):.0f} {1300 + 900 * math.sin(math.radians(a + 5)):.0f} Z' fill='#ffffff' opacity='{0.28 * rev:.2f}'/>")
        escena.append(f"<circle cx='{CX}' cy='1300' r='{lerp(150, 620, rev):.0f}' fill='url(#flash)'/>")
    escena.append(botella(t, frio, hielo, rev))
    # esquirlas de hielo que salen despedidas
    if t > REVELACION:
        k = t - REVELACION
        for ang, sp, sz, r0 in ESQUIRLAS:
            px = CX + math.cos(ang) * sp * k
            py = 1130 + math.sin(ang) * sp * k + 300 * k * k
            if py < 1000:
                continue
            escena.append(f"<g transform='translate({px:.0f},{py:.0f}) rotate({r0 + 300 * k:.0f})' opacity='{clamp(1.6 - k * 0.6):.2f}'>"
                          f"<path d='M0 {-sz} L{sz * 0.7:.0f} {sz * 0.6:.0f} L{-sz * 0.7:.0f} {sz * 0.6:.0f} Z' fill='#f4fdff' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/></g>")
    escena.append(tapon_volando(t))
    # copos y escarcha que caen
    for x0, y0, r, sp, ph in COPOS:
        yy = (y0 + t * sp) % (H + 40) - 20
        xx = x0 + 18 * math.sin(t * 1.2 + ph)
        op = (0.35 + 0.5 * frio) * (0.6 + 0.4 * math.sin(t * 2 + ph))
        escena.append(f"<circle cx='{xx:.0f}' cy='{yy:.0f}' r='{r:.1f}' fill='#ffffff' opacity='{op:.2f}'/>")
    # vaho frío que se mueve por abajo
    for i in range(3):
        mx = (t * 40 + i * 420) % 1500 - 260
        escena.append(f"<ellipse cx='{mx:.0f}' cy='{1660 + i * 25}' rx='190' ry='38' fill='#ffffff' opacity='{0.18 + 0.12 * frio:.2f}'/>")
    s.append(zoom(CX, 1250, z, "".join(escena)))
    s.append("</svg>")
    return "".join(s)
