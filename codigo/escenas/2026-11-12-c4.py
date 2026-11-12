"""2026-11-12-c4 · Los vikingos no llevaban cascos con cuernos (los cuernos nacieron en el vestuario
de la ópera de Wagner de 1876). Un vikingo original llega a la playa de un fiordo con su casco de
cuernos; los cuernos tiemblan y en la REVELACION salen volando: queda el casco redondo de verdad."""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, rebote

DUR = 10.0
REVELACION = 7.5    # los cuernos salen disparados: golpe musical
MUSICA = 4

rng = np.random.default_rng(12)
PEBBLES = [(rng.uniform(30, 1050), rng.uniform(1560, 1900), rng.uniform(10, 22)) for _ in range(16)]
SPARKS = [(rng.uniform(0, 6.283), rng.uniform(160, 420), rng.uniform(7, 15)) for _ in range(26)]
TUFTS = [(70, 1500), (300, 1880), (960, 1480), (1020, 1860), (180, 1700)]


def nube(x, y, sc, col):
    return (f"<g transform='translate({x:.0f},{y:.0f}) scale({sc})'>"
            f"<path d='M0 60 Q-10 10 50 15 Q70 -30 130 -5 Q180 -35 220 15 Q280 10 270 60 Z' fill='{col}' "
            f"stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")


def barco(t):
    """Barco vikingo de fondo (casco con escudos, vela a rayas)."""
    x = 860 - 18 * t
    y = 1238 + 7 * math.sin(t * 2.1)
    r = 2.5 * math.sin(t * 1.7)
    g = [f"<g transform='translate({x:.1f},{y:.1f}) rotate({r:.2f}) scale(0.82)'>"]
    g.append(f"<line x1='0' y1='-10' x2='0' y2='-250' stroke='{INK}' stroke-width='14' stroke-linecap='round'/>"
             f"<line x1='0' y1='-10' x2='0' y2='-250' stroke='#8a5a32' stroke-width='6' stroke-linecap='round'/>")
    g.append(f"<path d='M-110 -225 L110 -225 Q125 -120 105 -40 L-105 -40 Q-125 -120 -110 -225 Z' fill='#f4ecd8' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    for sx in (-66, 0, 66):
        g.append(f"<path d='M{sx-20} -225 L{sx+20} -225 L{sx+22} -40 L{sx-22} -40 Z' fill='#d8453b'/>")
    g.append(f"<path d='M-110 -225 L110 -225 Q125 -120 105 -40 L-105 -40 Q-125 -120 -110 -225 Z' fill='none' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M-200 -20 Q-215 -95 -175 -105 Q-160 -70 -150 -20 L150 -20 Q160 -70 175 -105 Q215 -95 200 -20 Q170 45 0 50 Q-170 45 -200 -20 Z' "
             f"fill='#9a5f2e' stroke='{INK}' stroke-width='8' stroke-linejoin='round'/>")
    g.append(f"<path d='M-180 5 Q0 25 180 5' fill='none' stroke='#6e3f1c' stroke-width='6'/>")
    for i, sx in enumerate(range(-120, 140, 60)):
        c = ("#ffd23f", "#2f7fd1", "#e2483d", "#3faa5a", "#ffd23f")[i]
        g.append(f"<circle cx='{sx}' cy='-18' r='22' fill='{c}' stroke='{INK}' stroke-width='6'/><circle cx='{sx}' cy='-18' r='6' fill='{INK}'/>")
    g.append("</g>")
    return "".join(g)


def cuerno(lado):
    """Un cuerno curvo (lado -1 izquierda, 1 derecha), dibujado con su base en (0,0)."""
    s = -lado
    return (f"<path d='M0 25 Q{-95*s} 10 {-125*s} -150 Q{-75*s} -65 {5*s} -25 Z' fill='#f6ecd2' stroke='{INK}' "
            f"stroke-width='{LW}' stroke-linejoin='round'/>"
            f"<path d='M{-40*s} 12 Q{-30*s} -10 {-12*s} -18' fill='none' stroke='#c9b48a' stroke-width='6' stroke-linecap='round'/>"
            f"<path d='M{-82*s} -30 Q{-68*s} -52 {-50*s} -50' fill='none' stroke='#c9b48a' stroke-width='6' stroke-linecap='round'/>")


def vikingo(t):
    # entra caminando desde la izquierda (0-2,4 s)
    walk = seg(t, 0, 2.4)
    x = lerp(170, 540, walk)
    andando = t < 2.45
    paso = math.sin(t * 7.0) if andando else 0.0
    bob = (-10 * abs(math.sin(t * 7.0))) if andando else 3 * math.sin(t * 2.6)
    tension = seg(t, 5.0, 7.4) * (1 - seg(t, REVELACION, REVELACION + 0.05))
    shake = tension * 6 * math.sin(t * 55)
    blink = 0.12 if ((t + 1.3) % 2.7) < 0.12 and not (REVELACION - 0.2 < t < REVELACION + 1.2) else 1.0
    pupil_dy = lerp(0, -12, tension)
    sorpresa = seg(t, REVELACION, REVELACION + 0.25) * (1 - seg(t, 8.9, 9.4))
    # brazo derecho (del espectador, izquierda): saluda / puño en alto 2,6-5
    saludo = seg(t, 2.5, 3.1) * (1 - seg(t, 4.8, 5.3))
    brazo_rot = lerp(15, 145, saludo) + 12 * saludo * math.sin(t * 9)
    beard_sw = 3 * math.sin(t * 2.3)
    cape_sw = 4 * math.sin(t * 3.1)

    g = [f"<g transform='translate({x + shake:.1f},{bob:.1f})'>"]
    g.append(f"<ellipse cx='0' cy='1838' rx='230' ry='26' fill='#000' opacity='0.2'/>")
    # capa de piel por detrás
    g.append(f"<path d='M-150 1360 Q{-235 + cape_sw:.0f} 1560 {-205 + cape_sw:.0f} 1700 L{205 + cape_sw:.0f} 1700 Q{235 + cape_sw:.0f} 1560 150 1360 Z' "
             f"fill='#7a5638' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # piernas y botas
    for lado, fase in ((-1, 1), (1, -1)):
        sw = 22 * paso * fase
        g.append(f"<g transform='rotate({sw:.1f} {lado*55} 1640)'>"
                 f"<rect x='{lado*55-38}' y='1630' width='76' height='160' rx='18' fill='#4a6b3a' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<path d='M{lado*55-30} 1690 L{lado*55+30} 1710 M{lado*55-30} 1730 L{lado*55+30} 1750' stroke='#e9d9b8' stroke-width='7'/>"
                 f"<path d='M{lado*55-44} 1775 L{lado*55+44} 1775 L{lado*55+44+lado*30} 1835 L{lado*55-44} 1835 Z' fill='#6b3f22' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/></g>")
    # túnica
    g.append(f"<path d='M-150 1360 L150 1360 L178 1660 L-178 1660 Z' fill='#d8453b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-168 1610 L168 1610' stroke='#ffd23f' stroke-width='10'/>")
    # cinturón
    g.append(f"<rect x='-168' y='1540' width='336' height='40' rx='8' fill='#5a3420' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<rect x='-24' y='1534' width='48' height='52' rx='8' fill='#ffd23f' stroke='{INK}' stroke-width='7'/>")
    # brazo que saluda (izquierda del espectador)
    g.append(f"<g transform='rotate({brazo_rot:.1f} -150 1400)'>"
             f"<path d='M-150 1400 L-150 1560' stroke='{INK}' stroke-width='76' stroke-linecap='round'/>"
             f"<path d='M-150 1400 L-150 1560' stroke='#d8453b' stroke-width='60' stroke-linecap='round'/>"
             f"<rect x='-178' y='1500' width='56' height='34' rx='6' fill='#7a5638' stroke='{INK}' stroke-width='6'/>"
             f"<circle cx='-150' cy='1585' r='40' fill='#f5c9a0' stroke='{INK}' stroke-width='{LW}'/></g>")
    # escudo redondo (brazo derecho del espectador)
    srot = 4 * math.sin(t * 2.0)
    g.append(f"<g transform='translate(175,1515) rotate({srot:.1f})'>"
             f"<circle r='128' fill='#e9b44c' stroke='{INK}' stroke-width='{LW}'/>"
             f"<path d='M-128 0 L128 0 M0 -128 L0 128' stroke='#2f7fd1' stroke-width='34'/>"
             f"<circle r='128' fill='none' stroke='{INK}' stroke-width='{LW}'/>"
             f"<circle r='118' fill='none' stroke='#9aa3ad' stroke-width='10'/>"
             f"<circle r='34' fill='#c9ced6' stroke='{INK}' stroke-width='7'/><circle cx='-10' cy='-10' r='9' fill='#fff' opacity='0.8'/></g>")
    # cabeza
    g.append(f"<ellipse cx='-106' cy='1240' rx='22' ry='30' fill='#f5c9a0' stroke='{INK}' stroke-width='7'/>"
             f"<ellipse cx='106' cy='1240' rx='22' ry='30' fill='#f5c9a0' stroke='{INK}' stroke-width='7'/>")
    g.append(f"<ellipse cx='0' cy='1225' rx='105' ry='118' fill='#f5c9a0' stroke='{INK}' stroke-width='{LW}'/>")
    # barba (naranja, con trenzas)
    g.append(f"<g transform='rotate({beard_sw:.1f} 0 1270)'>")
    g.append(f"<path d='M-112 1240 Q-125 1400 -40 1450 Q0 1475 40 1450 Q125 1400 112 1240 Q60 1300 0 1300 Q-60 1300 -112 1240 Z' "
             f"fill='#e8742c' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    for bx in (-34, 34):
        g.append(f"<path d='M{bx} 1440 L{bx} 1530' stroke='{INK}' stroke-width='34' stroke-linecap='round'/>"
                 f"<path d='M{bx} 1440 L{bx} 1530' stroke='#e8742c' stroke-width='20' stroke-linecap='round'/>"
                 f"<rect x='{bx-14}' y='1495' width='28' height='16' rx='4' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<path d='M-60 1395 Q-50 1360 -40 1395 M50 1390 Q60 1350 70 1390' fill='none' stroke='#c0541a' stroke-width='6' stroke-linecap='round'/>")
    g.append("</g>")
    # boca (se abre de sorpresa)
    mo = lerp(10, 34, sorpresa)
    g.append(f"<ellipse cx='0' cy='1335' rx='{lerp(26, 22, sorpresa):.0f}' ry='{mo:.0f}' fill='#7a1f1f' stroke='{INK}' stroke-width='6'/>")
    # bigote
    g.append(f"<path d='M0 1300 Q-60 1280 -105 1320 Q-70 1325 -50 1312 Q-20 1310 0 1318 Q20 1310 50 1312 Q70 1325 105 1320 Q60 1280 0 1300 Z' "
             f"fill='#d8611f' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # nariz
    g.append(f"<ellipse cx='0' cy='1272' rx='28' ry='24' fill='#f0b088' stroke='{INK}' stroke-width='7'/>")
    # ojos y cejas
    for ex in (-46, 46):
        g.append(f"<g transform='translate({ex},1222) scale(1,{blink})'><ellipse rx='24' ry='{lerp(26, 32, sorpresa):.0f}' fill='#fff' stroke='{INK}' stroke-width='6'/>"
                 f"<circle cx='{3 if ex < 0 else -3}' cy='{pupil_dy + 3:.1f}' r='12' fill='{INK}'/><circle cx='{-1 if ex < 0 else -7}' cy='{pupil_dy - 2:.1f}' r='4.5' fill='#fff'/></g>")
        ang = (-1 if ex < 0 else 1) * lerp(8, -14, max(tension, sorpresa))
        g.append(f"<g transform='rotate({ang:.1f} {ex} 1180)'><rect x='{ex-32}' y='1170' width='64' height='18' rx='9' fill='#d8611f' stroke='{INK}' stroke-width='5'/></g>")
    # mejillas
    g.append("<ellipse cx='-72' cy='1262' rx='18' ry='10' fill='#f08a7a' opacity='0.7'/><ellipse cx='72' cy='1262' rx='18' ry='10' fill='#f08a7a' opacity='0.7'/>")
    # casco: cúpula de hierro, banda y nasal
    g.append(f"<path d='M-114 1190 Q-114 1075 0 1072 Q114 1075 114 1190 Z' fill='#9aa3ad' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M-60 1100 Q-20 1084 10 1086' fill='none' stroke='#e6ebf0' stroke-width='12' stroke-linecap='round'/>")
    g.append(f"<path d='M0 1075 L0 1180' stroke='#6f7882' stroke-width='16'/>")
    g.append(f"<rect x='-122' y='1168' width='244' height='36' rx='12' fill='#7d8690' stroke='{INK}' stroke-width='{LW}'/>")
    for rx_ in (-90, -45, 45, 90):
        g.append(f"<circle cx='{rx_}' cy='1186' r='6' fill='#d7dce2'/>")
    g.append(f"<path d='M-14 1196 L14 1196 L12 1262 Q0 1272 -12 1262 Z' fill='#7d8690' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    # cuernos: tiemblan en la tensión y salen volando en la revelación
    k = clamp((t - REVELACION) / 1.1)
    for lado in (-1, 1):
        bx, by = lado * 104, 1150
        if t < REVELACION:
            wob = tension * 7 * math.sin(t * 40 + lado)
            g.append(f"<g transform='translate({bx},{by}) rotate({wob:.1f})'>{cuerno(lado)}</g>")
        elif k < 1:
            dx = lado * 760 * k
            dy = -620 * k + 380 * k * k
            rot = lado * 540 * k
            g.append(f"<g transform='translate({bx + dx:.1f},{by + dy:.1f}) rotate({rot:.1f})' opacity='{1 - k*k:.2f}'>{cuerno(lado)}</g>")
    g.append("</g>")
    return "".join(g), x


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.6)
    flash = clamp(1 - (t - REVELACION) / 0.45) if t >= REVELACION else 0.0
    top = mix("#59b6ea", "#ffb85c", rev); mid = mix("#9fd8f5", "#ffd88f", rev); low = mix("#d6f1fb", "#fff1c6", rev)
    s = ["<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.6' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{mix('#2f8fc9', '#3a9ac0', rev)}'/><stop offset='1' stop-color='{mix('#1f6aa8', '#2a7aa0', rev)}'/></linearGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff7d0' stop-opacity='{0.95*rev:.3f}'/><stop offset='0.5' stop-color='#ffd36b' stop-opacity='{0.55*rev:.3f}'/><stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>",
         "</defs>"]
    s.append(f"<rect width='{W}' height='{H}' fill='url(#sky)'/>")
    # nubes tranquilas arriba
    for i, (cx, cy, sc) in enumerate([(120, 330, 1.2), (700, 560, 1.0), (380, 790, 0.8)]):
        dx = (t * 16 * (1 + 0.35 * i)) % 1500
        s.append(nube((cx + dx) % 1500 - 300, cy, sc, mix("#ffffff", "#fff4dc", rev)))
    # gaviotas
    for i, (gx, gy, sp) in enumerate([(100, 900, 55), (300, 960, 70), (820, 870, 48)]):
        xx = (gx + t * sp) % 1300 - 110
        fl = 14 * math.sin(t * 8 + i * 2)
        s.append(f"<path d='M{xx-30:.0f} {gy+fl:.0f} Q{xx-14:.0f} {gy-16:.0f} {xx:.0f} {gy:.0f} Q{xx+14:.0f} {gy-16:.0f} {xx+30:.0f} {gy+fl:.0f}' "
                 f"fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/>")
    z = 1 + 0.16 * seg(t, REVELACION, 9.6)
    cuerpo_vik, vx = vikingo(t)
    cx, cy = 540, 1300
    esc = []
    # montañas del fiordo
    m1 = mix("#4f8a8b", "#7a9a7a", rev); m2 = mix("#2f6b5f", "#5b8a5a", rev)
    esc.append(f"<path d='M-20 1180 L120 1010 L230 1090 L380 960 L520 1110 L640 1030 L760 1120 L900 990 L1100 1150 L1100 1200 L-20 1200 Z' fill='{m1}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    esc.append(f"<path d='M120 1010 L160 1058 L135 1050 L100 1036 Z M380 960 L428 1015 L395 1005 L350 995 Z M900 990 L955 1040 L915 1032 L870 1022 Z' fill='#ffffff' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    esc.append(f"<path d='M-20 1200 Q200 1120 420 1170 T880 1150 T1100 1180 L1100 1230 L-20 1230 Z' fill='{m2}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # mar
    esc.append(f"<rect x='-20' y='1210' width='1120' height='280' fill='url(#sea)' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(barco(t))
    for j, wy in enumerate((1300, 1360, 1420)):
        off = (t * (40 + 15 * j) + j * 90) % 180
        d = "".join(f"M{wx - off:.0f} {wy} q22 -16 44 0 " for wx in range(-60, 1200, 180))
        esc.append(f"<path d='{d}' fill='none' stroke='#cfeeff' stroke-width='7' stroke-linecap='round' opacity='0.85'/>")
    # orilla con espuma y playa
    fo = 8 * math.sin(t * 2.4)
    esc.append(f"<path d='M-20 {1478+fo:.0f} Q270 {1450-fo:.0f} 540 {1478+fo:.0f} T1100 {1470:.0f} L1100 1940 L-20 1940 Z' fill='#ffffff' stroke='{INK}' stroke-width='7'/>")
    esc.append(f"<path d='M-20 {1500+fo:.0f} Q270 {1475-fo:.0f} 540 {1500+fo:.0f} T1100 1495 L1100 1940 L-20 1940 Z' fill='{mix('#e9cf96', '#f3d89c', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for px, py, pr in PEBBLES:
        esc.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='{pr:.0f}' ry='{pr*0.65:.0f}' fill='#b9a07a' stroke='{INK}' stroke-width='5'/>")
    for tx, ty in TUFTS:
        sw = 6 * math.sin(t * 3 + tx)
        esc.append(f"<path d='M{tx-22} {ty} Q{tx-26+sw:.0f} {ty-40} {tx-34+sw:.0f} {ty-60} M{tx} {ty} Q{tx+sw:.0f} {ty-50} {tx+4+sw:.0f} {ty-75} M{tx+22} {ty} Q{tx+26+sw:.0f} {ty-40} {tx+36+sw:.0f} {ty-58}' "
                   f"fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
                   f"<path d='M{tx-22} {ty} Q{tx-26+sw:.0f} {ty-40} {tx-34+sw:.0f} {ty-60} M{tx} {ty} Q{tx+sw:.0f} {ty-50} {tx+4+sw:.0f} {ty-75} M{tx+22} {ty} Q{tx+26+sw:.0f} {ty-40} {tx+36+sw:.0f} {ty-58}' "
                   f"fill='none' stroke='#5fae4a' stroke-width='8' stroke-linecap='round'/>")
    # halo y rayos dorados tras el vikingo en la revelación
    if rev > 0:
        esc.append(f"<circle cx='{vx:.0f}' cy='1230' r='{lerp(150, 620, rev):.0f}' fill='url(#glow)'/>")
        rays = []
        for i in range(14):
            a = i * 2 * math.pi / 14 + t * 0.35
            a2 = a + 0.12
            r1, r2 = 170, lerp(200, 700, rev)
            rays.append(f"M{vx + r1*math.cos(a):.0f} {1230 + r1*math.sin(a):.0f} L{vx + r2*math.cos(a):.0f} {1230 + r2*math.sin(a):.0f} "
                        f"L{vx + r2*math.cos(a2):.0f} {1230 + r2*math.sin(a2):.0f} Z")
        esc.append(f"<path d='{' '.join(rays)}' fill='#fff3b0' opacity='{0.45*rev:.2f}'/>")
    esc.append(cuerpo_vik)
    # chispas que salen del casco al soltar los cuernos
    if t >= REVELACION:
        k = clamp((t - REVELACION) / 1.4)
        for a, dist, r in SPARKS:
            px = vx + math.cos(a) * dist * ease(k * 1.3)
            py = 1150 + math.sin(a) * dist * 0.8 * ease(k * 1.3)
            op = 1 - k
            if op > 0.02:
                esc.append(f"<path d='M{px:.0f} {py - r*1.8:.0f} L{px + r*0.5:.0f} {py:.0f} L{px:.0f} {py + r*1.8:.0f} L{px - r*0.5:.0f} {py:.0f} Z' "
                           f"fill='#ffe14d' stroke='{INK}' stroke-width='3' opacity='{op:.2f}'/>")
    s.append(f"<g transform='translate({cx},{cy}) scale({z:.4f}) translate({-cx},{-cy})'>{''.join(esc)}</g>")
    if flash > 0:
        s.append(f"<rect width='{W}' height='{H}' fill='#fffbe6' opacity='{0.75*flash:.2f}'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            + "".join(s) + "</svg>")
