"""2026-11-25-c1 · La lengua del camaleón mide unas 2 veces su cuerpo (National Geographic, Brown University 2016).

Un camaleón entra por una rama de la selva, ve un grillo lejos, se balancea apuntando y en la
REVELACION dispara la lengua (el doble de su cuerpo) y lo atrapa; cambia de color y aparecen dos
barras que comparan su cuerpo (verde) con la lengua (rosa, dos tramos iguales).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom

DUR = 10.0
REVELACION = 7.0   # sale la lengua: golpe musical
MUSICA = 5

rng = np.random.default_rng(25)
MOTAS = [(rng.uniform(0, W), rng.uniform(900, 1900), rng.uniform(3, 7), rng.uniform(15, 45), rng.uniform(0, 6.3)) for _ in range(34)]
TRONCOS = [(70, 46, "#4f9a6a"), (330, 30, "#5aa576"), (690, 38, "#4f9a6a"), (980, 52, "#468f60")]

S = 0.95                # escala del camaleón
X_FIN = 215            # x final del camaleón (centro del cuerpo)
Y_CAM = 1420            # y del centro del cuerpo
BOCA = (168, -4)        # boca en coordenadas locales (sin escalar)
GRILLO = (935, 1090)    # donde está el grillo (punta de la lengua), arriba a la derecha


def cam_x(t):
    return lerp(-60, X_FIN, seg(t, 0, 2.3))


def inclina(t):
    """El camaleón levanta la cabeza hacia el grillo (grados)."""
    return -9 * seg(t, 5.0, 6.0)


def boca(t):
    """Posición de la boca en pantalla (teniendo en cuenta la inclinación)."""
    a = math.radians(inclina(t)); bx, by = BOCA[0], BOCA[1] - 95
    rx = bx * math.cos(a) - by * math.sin(a); ry = bx * math.sin(a) + by * math.cos(a) + 95
    vaiven = 10 * math.sin(t * 7) * seg(t, 4.8, 5.3) * (1 - seg(t, 6.8, 7.0))
    return cam_x(t) + vaiven + rx * S, Y_CAM + ry * S


def hoja(x, y, ang, esc, col, ink=True):
    st = f" stroke='{INK}' stroke-width='6'" if ink else ""
    return (f"<g transform='translate({x:.1f},{y:.1f}) rotate({ang:.1f}) scale({esc:.2f})'>"
            f"<path d='M0 0 Q60 -55 150 0 Q60 55 0 0 Z' fill='{col}'{st} stroke-linejoin='round'/>"
            f"<path d='M8 0 L135 0' stroke='{mix(col, '#ffffff', 0.35)}' stroke-width='5' fill='none'/></g>")


def camaleon(t, exc):
    """Camaleón original de perfil (mira a la derecha). exc = 0..1 cambio de color en la revelación."""
    x = cam_x(t)
    andando = t < 2.35
    # balanceo típico al acechar (5-7 s) y paso al andar
    vaiven = 10 * math.sin(t * 7) * seg(t, 4.8, 5.3) * (1 - seg(t, 6.8, 7.0))
    paso = math.sin(t * 9) if andando else 0
    bob = 5 * abs(paso)
    piel = mix("#5cc94a", "#ff9f2e", exc)
    piel2 = mix("#9be36a", "#ffd23f", exc)
    oscuro = mix("#2f8f3a", "#e0453a", exc)
    g = [f"<g transform='translate({x + vaiven:.1f},{Y_CAM - bob:.1f}) scale({S}) rotate({inclina(t):.2f},0,95)'>"]
    # cola enroscada (tubo: contorno + relleno)
    cola = "M-125 5 Q-215 0 -225 70 Q-232 135 -175 140 Q-128 142 -130 105 Q-132 78 -160 82 Q-180 86 -175 105"
    rot = 3 * math.sin(t * 2.2)
    g.append(f"<g transform='rotate({rot:.1f},-125,5)'>"
             f"<path d='{cola}' fill='none' stroke='{INK}' stroke-width='{40 + 2*LW}' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='{cola}' fill='none' stroke='{piel}' stroke-width='40' stroke-linecap='round' stroke-linejoin='round'/>"
             f"<path d='{cola}' fill='none' stroke='{oscuro}' stroke-width='6' stroke-dasharray='6 26' stroke-linecap='round'/></g>")
    # patas traseras/delanteras (con pie en pinza agarrado a la rama)
    def pata(px, py, fx, fase):
        lev = 14 * max(0, math.sin(t * 9 + fase)) if andando else 0
        fy = 98 - lev
        kx = (px + fx) / 2 + 18
        return (f"<path d='M{px} {py} Q{kx:.0f} {py + 55} {fx:.0f} {fy:.0f}' fill='none' stroke='{INK}' stroke-width='{30 + 2*LW}' stroke-linecap='round'/>"
                f"<path d='M{px} {py} Q{kx:.0f} {py + 55} {fx:.0f} {fy:.0f}' fill='none' stroke='{piel}' stroke-width='30' stroke-linecap='round'/>"
                f"<ellipse cx='{fx - 12:.0f}' cy='{fy + 6:.0f}' rx='16' ry='12' fill='{piel2}' stroke='{INK}' stroke-width='6'/>"
                f"<ellipse cx='{fx + 12:.0f}' cy='{fy + 6:.0f}' rx='16' ry='12' fill='{piel2}' stroke='{INK}' stroke-width='6'/>")
    g.append(pata(-80, 25, -95, 0))
    g.append(pata(55, 30, 75, math.pi))
    # cuerpo: lomo alto y arqueado, comprimido de lado
    g.append(f"<path d='M-130 10 Q-120 -70 -40 -95 Q30 -110 95 -60 L110 25 Q40 55 -40 50 Q-110 45 -130 10 Z' "
             f"fill='{piel}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # cresta dorsal (dientecitos)
    cresta = " ".join(f"L{-110 + i*20} {-78 - 18*math.sin(math.pi*(i+0.5)/10):.0f} L{-100 + i*20} {-70 - 22*math.sin(math.pi*(i+1)/10):.0f}" for i in range(10))
    g.append(f"<path d='M-115 -60 {cresta}' fill='none' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    # franja lateral clara y manchas
    g.append(f"<path d='M-115 15 Q-30 35 90 10 Q30 30 -40 32 Q-100 30 -115 15 Z' fill='{piel2}' stroke='{INK}' stroke-width='5'/>")
    for mx, my, mr in ((-70, -40, 14), (-20, -60, 12), (30, -40, 15), (-40, -10, 10), (60, -25, 9)):
        g.append(f"<circle cx='{mx}' cy='{my}' r='{mr}' fill='{oscuro}' opacity='0.8'/>")
    # cabeza con casco (casque)
    abre = seg(t, 6.6, 6.95) * (1 - seg(t, 8.0, 8.4))
    mand = 14 * abre
    g.append(f"<path d='M90 -55 Q95 -125 135 -118 Q175 -95 212 -14 L200 {4 + mand:.1f} Q150 {30 + mand*0.6:.1f} 100 30 Z' "
             f"fill='{piel}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M100 -60 Q120 -112 138 -112' fill='none' stroke='{oscuro}' stroke-width='6' stroke-linecap='round'/>")
    if abre > 0.05:
        g.append(f"<path d='M205 -8 L150 2 L198 {4 + mand:.1f} Z' fill='#7a2140' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    else:
        g.append(f"<path d='M208 -8 Q175 12 140 4' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
    # ojo de torreta (escamas en anillos) con pupila que se mueve sola
    if t < 2.6:
        ang = 40 * math.sin(t * 2.6) - 20
    else:
        ang = lerp(40 * math.sin(2.6 * 2.6) - 20, -22, seg(t, 2.6, 3.1))
    pr = math.radians(ang)
    px, py = 148 + 13 * math.cos(pr), -42 + 13 * math.sin(pr)
    parp = 0.12 if (t % 2.7) < 0.12 and t < 6.5 else 1.0
    g.append(f"<circle cx='148' cy='-42' r='34' fill='{piel2}' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<circle cx='148' cy='-42' r='24' fill='none' stroke='{oscuro}' stroke-width='4' stroke-dasharray='5 6'/>")
    g.append(f"<g transform='translate({px:.1f},{py:.1f}) scale(1,{parp})'><circle r='13' fill='#fff' stroke='{INK}' stroke-width='4'/>"
             f"<circle r='8' fill='{INK}'/><circle cx='-3' cy='-3' r='3' fill='#fff'/></g>")
    # mejilla
    g.append(f"<circle cx='180' cy='8' r='10' fill='#ff8fa3' opacity='{0.7*(1-abre):.2f}'/>")
    g.append("</g>")
    return "".join(g)


def grillo(t, comido):
    """Grillo original: cuerpo marrón, gran pata saltadora, antenas largas (mira a la izquierda)."""
    if comido >= 1:
        return ""
    # da saltitos antes de quedarse quieto en su sitio
    hop = 0
    for a in (2.9, 4.0):
        k = clamp((t - a) / 0.45)
        hop = max(hop, 60 * math.sin(math.pi * k) if 0 < k < 1 else 0)
    gx = lerp(1000, GRILLO[0], seg(t, 2.5, 4.5))
    gy = GRILLO[1] - hop
    ant = 10 * math.sin(t * 6)
    return (f"<g transform='translate({gx:.1f},{gy:.1f}) scale(1.3)'>"
            f"<path d='M-34 -14 Q-80 {-70 + ant:.1f} -130 {-60 + ant:.1f}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M-30 -18 Q-60 {-90 - ant:.1f} -100 {-100 - ant:.1f}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M-10 10 L-20 34 M10 12 L6 36' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>"
            f"<ellipse cx='12' cy='-4' rx='44' ry='22' fill='#a8692e' stroke='{INK}' stroke-width='{LW-2}'/>"
            f"<path d='M-6 -20 Q30 -34 62 -8 Q30 -6 -6 -20 Z' fill='#7a4a1e' stroke='{INK}' stroke-width='5'/>"
            f"<path d='M30 0 L58 -42 L66 30' fill='none' stroke='{INK}' stroke-width='{14 + 10}' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M30 0 L58 -42 L66 30' fill='none' stroke='#c98a45' stroke-width='14' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<circle cx='-30' cy='-6' r='20' fill='#b57a3a' stroke='{INK}' stroke-width='6'/>"
            f"<circle cx='-38' cy='-10' r='7' fill='{INK}'/><circle cx='-40' cy='-12' r='2.5' fill='#fff'/></g>")


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)
    exc = seg(t, REVELACION, REVELACION + 0.8)
    flash = clamp(1 - (t - REVELACION) / 0.5) if t >= REVELACION else 0
    # lengua: sale en 0,12 s, se queda estirada con el grillo y vuelve a 8,6-8,9 s
    sale = seg(t, REVELACION, REVELACION + 0.12)
    vuelve = seg(t, 8.6, 8.9)
    largo = sale * (1 - vuelve)
    top = mix("#bfeedd", "#e6fff2", rev); mid = mix("#7fd1a6", "#b6f0c8", rev); low = mix("#2f8a5a", "#45a56b", rev)
    defs = (f"<linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            "<linearGradient id='rayo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fffbe0' stop-opacity='0.55'/>"
            "<stop offset='1' stop-color='#fffbe0' stop-opacity='0'/></linearGradient>"
            f"<radialGradient id='luz'><stop offset='0' stop-color='#fff6b0' stop-opacity='{0.9*rev:.3f}'/>"
            "<stop offset='1' stop-color='#fff6b0' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#cielo)'/>"]
    # rayos de sol entre los árboles (fondo tranquilo arriba)
    for i, (rx, rw) in enumerate(((180, 120), (520, 90), (840, 140))):
        a = 0.6 + 0.25 * math.sin(t * 1.3 + i)
        s.append(f"<path d='M{rx} 0 L{rx + rw} 0 L{rx + rw + 260} 1500 L{rx + 200} 1500 Z' fill='url(#rayo)' opacity='{a:.2f}'/>")
    c = []
    # troncos lejanos
    for tx, tw, col in TRONCOS:
        c.append(f"<rect x='{tx - tw}' y='-20' width='{2*tw}' height='1960' fill='{col}' opacity='0.55'/>")
    # copas de hojas lejanas arriba del todo (suaves, sin contorno)
    for i in range(8):
        hx = i * 150 - 40 + 12 * math.sin(t * 0.8 + i)
        c.append(f"<ellipse cx='{hx:.0f}' cy='{-30 + 25*(i % 2)}' rx='130' ry='90' fill='#3f9a5e' opacity='0.8'/>")
    # lianas a los lados
    for lx, ph in ((40, 0), (1045, 1.5)):
        sw = 14 * math.sin(t * 1.4 + ph)
        c.append(f"<path d='M{lx} 0 Q{lx + sw:.0f} 500 {lx - sw/2:.0f} 1000' fill='none' stroke='{INK}' stroke-width='20' stroke-linecap='round'/>"
                 f"<path d='M{lx} 0 Q{lx + sw:.0f} 500 {lx - sw/2:.0f} 1000' fill='none' stroke='#6b8f3a' stroke-width='12' stroke-linecap='round'/>")
        for k in range(4):
            yy = 200 + k * 220
            c.append(hoja(lx + sw * math.sin(math.pi * yy / 1000), yy, 30 if lx < 500 else 150, 0.45, "#5fb84f"))
    # halo de luz en la revelación
    c.append(f"<circle cx='620' cy='1260' r='{lerp(200, 620, rev):.0f}' fill='url(#luz)'/>")
    # suelo de selva al fondo
    c.append(f"<path d='M0 1640 Q270 1590 540 1630 T1080 1610 L1080 1920 L0 1920 Z' fill='#2a7a4a' stroke='{INK}' stroke-width='{LW}'/>")
    # rama del grillo (desde la derecha) y rama del camaleón (desde la izquierda)
    c.append(f"<path d='M1100 1128 Q1000 1138 860 1156' fill='none' stroke='{INK}' stroke-width='{34 + 2*LW}' stroke-linecap='round'/>"
             f"<path d='M1100 1128 Q1000 1138 860 1156' fill='none' stroke='#8a5a34' stroke-width='34' stroke-linecap='round'/>")
    c.append(hoja(880, 1154, 200 + 5 * math.sin(t * 2.1), 0.6, "#4fae45"))
    c.append(f"<path d='M-40 1520 Q200 1505 420 1512 Q470 1513 500 1520' fill='none' stroke='{INK}' stroke-width='{44 + 2*LW}' stroke-linecap='round'/>"
             f"<path d='M-40 1520 Q200 1505 420 1512 Q470 1513 500 1520' fill='none' stroke='#9a6238' stroke-width='44' stroke-linecap='round'/>"
             f"<path d='M40 1514 Q120 1508 180 1512 M260 1520 Q320 1514 380 1518' fill='none' stroke='#6e4224' stroke-width='6' stroke-linecap='round'/>")
    c.append(hoja(470, 1520, 330 + 6 * math.sin(t * 2), 0.6, "#5fb84f"))
    c.append(hoja(110, 1520, 150 + 6 * math.sin(t * 2.3), 0.55, "#4fae45"))
    if t < REVELACION + 0.12:
        c.append(grillo(t, 0))
    c.append(camaleon(t, exc))
    # lengua (sale de la boca hasta el grillo) con punta pegajosa y el grillo pegado
    if largo > 0.01:
        bx, by = boca(t)
        ex = lerp(bx, GRILLO[0], largo); ey = lerp(by, GRILLO[1], largo)
        if t >= REVELACION + 0.12:
            c.append(f"<g transform='translate({ex - GRILLO[0]:.1f},{ey - GRILLO[1]:.1f})'>{grillo(min(t, 4.6), 0)}</g>")
        c.append(f"<line x1='{bx:.0f}' y1='{by:.0f}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='{INK}' stroke-width='{22 + 2*LW}' stroke-linecap='round'/>"
                 f"<line x1='{bx:.0f}' y1='{by:.0f}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='#ff6f9c' stroke-width='22' stroke-linecap='round'/>"
                 f"<line x1='{bx:.0f}' y1='{by - 4:.0f}' x2='{ex:.1f}' y2='{ey - 4:.1f}' stroke='#ffb3cb' stroke-width='6' stroke-linecap='round'/>"
                 f"<circle cx='{ex:.1f}' cy='{ey:.1f}' r='26' fill='#ff4f86' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle cx='{ex - 8:.1f}' cy='{ey - 9:.1f}' r='7' fill='#ffd0de'/>")
    # estallido de rayitas en el impacto
    imp = seg(t, REVELACION + 0.1, REVELACION + 0.6)
    if 0 < imp < 1:
        for k in range(10):
            a = math.radians(k * 36 + 10)
            r1, r2 = lerp(40, 120, imp), lerp(70, 190, imp)
            c.append(f"<line x1='{GRILLO[0] + r1*math.cos(a):.0f}' y1='{GRILLO[1] + r1*math.sin(a):.0f}' "
                     f"x2='{GRILLO[0] + r2*math.cos(a):.0f}' y2='{GRILLO[1] + r2*math.sin(a):.0f}' stroke='#fff3a0' "
                     f"stroke-width='12' stroke-linecap='round' opacity='{1 - imp:.2f}'/>")
    # masticando al final
    if t >= 8.9:
        mm = abs(math.sin((t - 8.9) * 14))
        mx, my = boca(t)
        c.append(f"<circle cx='{mx - 18*S:.0f}' cy='{my + 22*S + 4*mm:.0f}' r='{10 + 5*mm:.0f}' fill='{mix('#5cc94a', '#ff9f2e', exc)}' stroke='{INK}' stroke-width='5'/>")
    # matorral delante, que se mece
    for i, (bx, by, sc) in enumerate(((60, 1860, 1.3), (330, 1900, 1.1), (620, 1870, 1.4), (900, 1880, 1.2), (1060, 1840, 1.0))):
        sw = 5 * math.sin(t * 1.8 + i)
        for k, ang in enumerate((-120, -80, -50)):
            c.append(hoja(bx, by, ang + sw + 15 * i % 30, sc, ("#2f8f3a", "#3aa04a", "#2a8034")[k]))
    # motas de polen flotando
    for px, py, pr, sp, ph in MOTAS:
        yy = (py - t * sp) % 1050 + 870
        c.append(f"<circle cx='{px + 18*math.sin(t + ph):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='#fff6c0' opacity='{0.45 + 0.3*math.sin(t*2 + ph):.2f}'/>")
    z = 1 + 0.08 * seg(t, REVELACION, REVELACION + 0.6)
    s.append(zoom(420, 1300, z, "".join(c)))
    # barras de comparación: cuerpo (verde) y lengua (rosa, dos tramos iguales)
    bar = seg(t, 7.35, 7.8) * (1 - seg(t, 8.5, 8.8))
    if bar > 0.01:
        cx0 = 40; cx1 = 40 + 340 * S; lt = 2 * 340 * S + 16
        y = 1600
        s.append(f"<g opacity='{bar:.2f}'>"
                 f"<rect x='{cx0:.0f}' y='{y}' width='{(cx1 - cx0) * bar:.0f}' height='34' rx='17' fill='#7be35a' stroke='{INK}' stroke-width='7'/>"
                 f"<rect x='{cx1 + 8:.0f}' y='{y}' width='{(lt/2 - 12) * bar:.0f}' height='34' rx='17' fill='#ff6f9c' stroke='{INK}' stroke-width='7'/>"
                 f"<rect x='{cx1 + lt/2 + 4:.0f}' y='{y}' width='{(lt/2 - 12) * seg(t, 7.6, 8.0) * bar:.0f}' height='34' rx='17' fill='#ff6f9c' stroke='{INK}' stroke-width='7'/>"
                 "</g>")
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{0.55*flash:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{''.join(s)}</svg>")
