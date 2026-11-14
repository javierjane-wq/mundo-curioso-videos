"""2026-11-14-c5 · Cuerpo humano: el cuerpo humano emite luz visible, unas 1.000 veces más débil
de lo que el ojo puede captar (Kobayashi et al., PLoS ONE 2009).

Un niño en pijama entra en su cuarto, se apaga la lámpara y queda a oscuras; aparecen
destellos tenues y, en la REVELACION, su cuerpo brilla con un halo dorado (la cara, más).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.5   # el niño brilla: golpe musical
MUSICA = 6

rng = np.random.default_rng(14)
STARS = [(rng.uniform(95, 305), rng.uniform(1030, 1235), rng.uniform(2, 4.5), rng.uniform(0, 6.28)) for _ in range(14)]
MOTES = [(rng.uniform(0, W), rng.uniform(1000, 1900), rng.uniform(3, 6), rng.uniform(15, 40)) for _ in range(30)]
SPARK = [(rng.uniform(-260, 260), rng.uniform(-470, 330), rng.uniform(4, 10), rng.uniform(0, 6.28)) for _ in range(34)]
DOTS = [(x, y) for y in range(80, 1000, 120) for x in range((y // 120) % 2 * 60 + 40, W, 120)]

KX, KY = 540, 1480   # centro del niño (cintura aprox.)


def nino(t, dark, glow):
    """Niño original en pijama de rayas: cabeza grande, flequillo, ojos que parpadean."""
    x = lerp(150, KX, seg(t, 0, 2.2))
    walking = t < 2.25
    bob = -abs(10 * math.sin(t * 9)) if walking else 3 * math.sin(t * 2.4)
    step = 22 * math.sin(t * 9) if walking else 0
    look_hands = seg(t, 5.2, 6.2) * (1 - seg(t, 7.4, 8.2))     # mira sus manos con curiosidad
    wonder = seg(t, 7.5, 8.2)                                  # boca de asombro
    raise_arms = seg(t, 7.5, 8.3)
    blink = 0.12 if ((t + 1.0) % 2.7) < 0.12 or abs(t - 6.9) < 0.07 else 1.0
    d = dark * 0.62 * (1 - 0.75 * glow)
    skin = mix(mix("#f6c9a0", "#202848", d), "#ffe6b8", 0.35 * glow)
    pj = mix(mix("#5bb7e8", "#1a2650", d), "#9fe3ff", 0.25 * glow)
    pj2 = mix(mix("#ffffff", "#2a3760", d), "#e8fbff", 0.25 * glow)
    hair = mix(mix("#7a4a2a", "#151a30", d), "#b07a45", 0.3 * glow)
    slip = mix(mix("#ff6f6f", "#2a1f40", d), "#ff9a8a", 0.3 * glow)
    ink = mix(INK, "#05070f", dark * 0.5)
    g = [f"<g transform='translate({x:.1f},{KY + bob:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='300' rx='170' ry='24' fill='#000' opacity='{0.25 * (1 - glow):.2f}'/>")
    # piernas y zapatillas
    for sx, ph in ((-50, 1), (50, -1)):
        lx = sx + ph * step * 0.6
        g.append(f"<path d='M{sx} 120 L{lx:.1f} 270' stroke='{ink}' stroke-width='70' stroke-linecap='round'/>")
        g.append(f"<path d='M{sx} 120 L{lx:.1f} 270' stroke='{pj}' stroke-width='52' stroke-linecap='round'/>")
        g.append(f"<ellipse cx='{lx + sx * 0.25:.1f}' cy='290' rx='52' ry='26' fill='{slip}' stroke='{ink}' stroke-width='7'/>")
    # brazos (balanceo al andar, luego miran las manos, luego arriba de alegría)
    for side in (-1, 1):
        sw = -side * step if walking else 0
        ang = side * (14 + sw) - side * lerp(0, 52, look_hands) - side * lerp(0, 120, raise_arms)
        g.append(f"<g transform='translate({side * 95},-40) rotate({ang:.1f})'>"
                 f"<path d='M0 0 L0 150' stroke='{ink}' stroke-width='60' stroke-linecap='round'/>"
                 f"<path d='M0 0 L0 150' stroke='{pj}' stroke-width='44' stroke-linecap='round'/>"
                 f"<circle cx='0' cy='165' r='30' fill='{skin}' stroke='{ink}' stroke-width='7'/></g>")
    # cuerpo (pijama de rayas)
    g.append("<clipPath id='pjc'><rect x='-115' y='-80' width='230' height='225' rx='60'/></clipPath>")
    g.append(f"<rect x='-115' y='-80' width='230' height='225' rx='60' fill='{pj}'/>")
    g.append("<g clip-path='url(#pjc)'>" + "".join(
        f"<rect x='-120' y='{yy}' width='240' height='18' fill='{pj2}' opacity='0.8'/>" for yy in range(-60, 150, 46)) + "</g>")
    g.append(f"<rect x='-115' y='-80' width='230' height='225' rx='60' fill='none' stroke='{ink}' stroke-width='{LW}'/>")
    for by in (-30, 20, 70):
        g.append(f"<circle cx='0' cy='{by}' r='9' fill='{mix('#ffd23f', '#3a3420', d)}' stroke='{ink}' stroke-width='4'/>")
    # cuello y cabeza
    g.append(f"<rect x='-30' y='-115' width='60' height='50' fill='{skin}' stroke='{ink}' stroke-width='7'/>")
    hx, hy = 0, -250
    g.append(f"<g transform='translate({hx},{hy}) rotate({lerp(0, 6, look_hands) - lerp(0, 4, raise_arms):.1f})'>")
    for ex in (-142, 142):  # orejas
        g.append(f"<ellipse cx='{ex}' cy='15' rx='28' ry='36' fill='{skin}' stroke='{ink}' stroke-width='7'/>")
    g.append(f"<circle r='145' fill='{skin}' stroke='{ink}' stroke-width='{LW}'/>")
    # pelo con flequillo
    g.append(f"<path d='M-146 -10 Q-150 -150 -20 -160 Q120 -165 148 -20 Q120 -80 70 -70 Q40 -40 20 -80 Q-10 -40 -40 -78 Q-80 -40 -110 -70 Q-130 -40 -146 -10 Z' "
             f"fill='{hair}' stroke='{ink}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-10 -160 Q10 -200 45 -195' fill='none' stroke='{ink}' stroke-width='9' stroke-linecap='round'/>")
    # ojos
    ly = lerp(0, 16, look_hands)
    for ex in (-55, 55):
        g.append(f"<g transform='translate({ex},10) scale(1,{blink})'>"
                 f"<ellipse rx='32' ry='38' fill='#fff' stroke='{ink}' stroke-width='6'/>"
                 f"<circle cx='{4:.0f}' cy='{6 + ly:.1f}' r='19' fill='#2a1a14'/>"
                 f"<circle cx='-4' cy='{-4 + ly:.1f}' r='7' fill='#fff'/></g>")
    # mejillas
    for ex in (-92, 92):
        g.append(f"<ellipse cx='{ex}' cy='62' rx='22' ry='13' fill='#ff8a8a' opacity='{0.55 * (1 - d):.2f}'/>")
    # boca: sonrisa -> "o" de asombro
    if wonder < 0.5:
        g.append(f"<path d='M-34 70 Q0 {98 - 20 * look_hands:.0f} 34 70' fill='none' stroke='{ink}' stroke-width='8' stroke-linecap='round'/>")
    else:
        g.append(f"<ellipse cx='0' cy='82' rx='{18 + 6 * wonder:.0f}' ry='{22 + 6 * wonder:.0f}' fill='#7a2a2a' stroke='{ink}' stroke-width='7'/>")
    g.append("</g></g>")
    return "".join(g), x, bob


def frame(t):
    dark = seg(t, 2.55, 2.85)          # se apaga la lámpara
    glow = seg(t, 7.45, 8.3)           # el cuerpo brilla
    hint = seg(t, 5.0, 7.4) * (1 - glow)
    wall_top = mix(mix("#f3d9a4", "#0f1638", dark), "#1c1a3a", 0.3 * glow)
    wall_low = mix(mix("#f7c98a", "#18204a", dark), "#2a2448", 0.3 * glow)
    dot = mix("#f9e6bd", "#1d2550", dark)
    floor = mix(mix("#c9814f", "#1a1a36", dark), "#3a2c40", 0.4 * glow)
    floor2 = mix(mix("#b06f41", "#15152e", dark), "#33263a", 0.4 * glow)
    defs = (f"<linearGradient id='wall' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{wall_top}'/>"
            f"<stop offset='1' stop-color='{wall_low}'/></linearGradient>"
            f"<radialGradient id='lamp'><stop offset='0' stop-color='#fff2c4' stop-opacity='{0.8 * (1 - dark):.3f}'/>"
            f"<stop offset='1' stop-color='#ffcf70' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='aura'><stop offset='0' stop-color='#fffbe6' stop-opacity='{0.95 * glow:.3f}'/>"
            f"<stop offset='0.35' stop-color='#ffe27a' stop-opacity='{0.75 * glow:.3f}'/>"
            f"<stop offset='0.7' stop-color='#ffb347' stop-opacity='{0.35 * glow:.3f}'/>"
            f"<stop offset='1' stop-color='#ff8a3d' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='face'><stop offset='0' stop-color='#ffffff' stop-opacity='{0.9 * glow:.3f}'/>"
            f"<stop offset='1' stop-color='#fff0a8' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='moon'><stop offset='0' stop-color='#cfe6ff' stop-opacity='0.35'/>"
            f"<stop offset='1' stop-color='#cfe6ff' stop-opacity='0'/></radialGradient>")
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#wall)'/>"]
    z = 1 + 0.16 * seg(t, 7.45, 10)
    s.append(f"<g transform='translate({KX},1330) scale({z:.4f}) translate({-KX},-1330)'>")
    # papel pintado de lunares (tranquilo, arriba)
    for dx, dy in DOTS:
        s.append(f"<circle cx='{dx}' cy='{dy}' r='10' fill='{dot}' opacity='0.7'/>")
    # zócalo
    s.append(f"<rect x='-50' y='1620' width='1180' height='40' fill='{mix('#e9b878', '#141a3c', dark)}' stroke='{INK}' stroke-width='{LW}'/>")
    # ventana con estrellas y luna
    sky = mix("#8ec9f0", "#0a0f2e", dark)
    s.append(f"<rect x='80' y='1010' width='240' height='240' rx='14' fill='{sky}' stroke='{INK}' stroke-width='{LW}'/>")
    for sx, sy, sr, ph in STARS:
        a = dark * (0.5 + 0.5 * math.sin(t * 3.5 + ph))
        if a > 0.03: s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    s.append(f"<circle cx='{255}' cy='{1070}' r='{lerp(0, 30, dark):.1f}' fill='#fff7d6' stroke='{INK}' stroke-width='5'/>")
    s.append(f"<circle cx='{240}' cy='{1062}' r='{lerp(0, 26, dark):.1f}' fill='{sky}'/>")
    s.append(f"<path d='M200 1010 L200 1250 M80 1130 L320 1130' stroke='{INK}' stroke-width='{LW}'/>")
    # cortinas que se mecen
    cw = 10 * math.sin(t * 1.6)
    cur = mix("#e85d75", "#2b1d48", dark * 0.8)
    s.append(f"<path d='M60 995 L130 995 Q{120 + cw:.0f} 1150 {140 + cw:.0f} 1290 L55 1290 Z' fill='{cur}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<path d='M270 995 L340 995 L{345 - cw:.0f} 1290 L{258 - cw:.0f} 1290 Q{280 - cw:.0f} 1150 270 995 Z' fill='{cur}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(f"<rect x='40' y='982' width='320' height='18' rx='9' fill='{mix('#a86a3a', '#2a2240', dark)}' stroke='{INK}' stroke-width='6'/>")
    # haz de luna en el suelo
    if dark > 0.05:
        s.append(f"<path d='M120 1250 L300 1250 L520 1900 L60 1900 Z' fill='#9fc4ff' opacity='{0.08 * dark:.3f}'/>")
    # suelo de madera
    s.append(f"<rect x='-50' y='1660' width='1180' height='300' fill='{floor}' stroke='{INK}' stroke-width='{LW}'/>")
    for fy in (1730, 1810):
        s.append(f"<line x1='-50' y1='{fy}' x2='1130' y2='{fy}' stroke='{floor2}' stroke-width='8'/>")
    for fx, fy in ((180, 1660), (620, 1660), (980, 1660), (380, 1730), (820, 1730), (120, 1810), (560, 1810), (900, 1810)):
        s.append(f"<line x1='{fx}' y1='{fy}' x2='{fx}' y2='{fy + 70}' stroke='{floor2}' stroke-width='7'/>")
    # alfombra
    s.append(f"<ellipse cx='540' cy='1790' rx='300' ry='60' fill='{mix('#8e6cd8', '#1f1a45', dark)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<ellipse cx='540' cy='1790' rx='220' ry='38' fill='none' stroke='{mix('#c8b3ff', '#2c2660', dark)}' stroke-width='8'/>")
    # mesilla y lámpara (derecha)
    s.append(f"<circle cx='880' cy='1240' r='260' fill='url(#lamp)'/>")
    s.append(f"<rect x='790' y='1440' width='190' height='230' rx='14' fill='{mix('#d98b4a', '#1e1a3a', dark)}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<rect x='812' y='1490' width='146' height='70' rx='10' fill='{mix('#c27537', '#19162f', dark)}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<circle cx='885' cy='1525' r='9' fill='{mix('#ffd23f', '#3a3420', dark)}' stroke='{INK}' stroke-width='4'/>")
    s.append(f"<rect x='875' y='1300' width='20' height='140' fill='{mix('#6b4a3a', '#151228', dark)}' stroke='{INK}' stroke-width='6'/>")
    s.append(f"<ellipse cx='885' cy='1442' rx='55' ry='14' fill='{mix('#6b4a3a', '#151228', dark)}' stroke='{INK}' stroke-width='6'/>")
    shade = mix("#ffe08a", "#2c2a4a", dark)
    s.append(f"<path d='M820 1310 L950 1310 L915 1200 L855 1200 Z' fill='{shade}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cadenita de la lámpara (se mueve al apagarse)
    sw = 14 * math.sin((t - 2.55) * 9) * math.exp(-max(0, t - 2.55) * 1.5) if t > 2.55 else 0
    s.append(f"<g transform='translate(935,1310) rotate({sw:.1f})'><line x1='0' y1='0' x2='0' y2='55' stroke='{INK}' stroke-width='5'/>"
             f"<circle cx='0' cy='60' r='8' fill='#ffd23f' stroke='{INK}' stroke-width='4'/></g>")
    # osito de peluche en la mesilla... no: libro y reloj sencillo
    s.append(f"<rect x='808' y='1415' width='60' height='24' rx='4' fill='{mix('#4fb06a', '#17283a', dark)}' stroke='{INK}' stroke-width='5'/>")
    # aura detrás del niño
    body, nx, bob = nino(t, dark, glow)
    gy = KY + bob - 120
    pul = 1 + 0.04 * math.sin(t * 5)
    if glow > 0:
        s.append(f"<ellipse cx='{nx:.0f}' cy='{gy:.0f}' rx='{lerp(200, 400, glow) * pul:.0f}' ry='{lerp(320, 560, glow) * pul:.0f}' fill='url(#aura)'/>")
    s.append(body)
    if glow > 0:
        # contorno luminoso y cara más brillante
        s.append(f"<circle cx='{nx:.0f}' cy='{KY + bob - 250:.0f}' r='{230 * pul:.0f}' fill='url(#face)'/>")
    # destellos: tenues en la tensión, intensos en la revelación
    amp = 0.35 * hint + glow
    if amp > 0.02:
        for px, py, pr, ph in SPARK:
            tw = 0.5 + 0.5 * math.sin(t * 6 + ph)
            yy = py - (t * 30) % 60
            r = pr * (0.6 + 0.4 * tw) * (1 + 0.6 * glow)
            cx, cy = nx + px * (1 + 0.25 * glow), KY + bob - 80 + yy
            s.append(f"<path d='M{cx:.0f} {cy - r * 2:.0f} L{cx + r * 0.5:.0f} {cy - r * 0.5:.0f} L{cx + r * 2:.0f} {cy:.0f} "
                     f"L{cx + r * 0.5:.0f} {cy + r * 0.5:.0f} L{cx:.0f} {cy + r * 2:.0f} L{cx - r * 0.5:.0f} {cy + r * 0.5:.0f} "
                     f"L{cx - r * 2:.0f} {cy:.0f} L{cx - r * 0.5:.0f} {cy - r * 0.5:.0f} Z' fill='#fff6c8' opacity='{amp * tw:.2f}'/>")
    # motas de polvo flotando
    for px, py, pr, sp in MOTES:
        yy = (py - t * sp) % 900 + 1000
        s.append(f"<circle cx='{px + 18 * math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='{mix('#fff3d0', '#8fb0ff', dark)}' opacity='{0.45 - 0.2 * dark:.2f}'/>")
    s.append("</g></svg>")
    return "".join(s)
