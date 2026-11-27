"""2026-11-27-c1 · El hipopótamo «suda» rojo: un protector solar natural (Saikawa et al., Nature 2004).

Un hipopótamo original sale del río africano (0-2,2 s), el sol aprieta y suben ondas de calor,
le aparecen gotitas transparentes por la piel y en la REVELACION se vuelven ROJAS, la piel se tiñe
de rosa rojizo y un halo naranja le rodea mientras los rayos del sol rebotan (zoom de cámara).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 7.0   # las gotas se vuelven rojas: golpe musical
MUSICA = 2

rng = np.random.default_rng(27)
DESTELLOS = [(rng.uniform(0, W), rng.uniform(1330, 1900), rng.uniform(18, 40), rng.uniform(0, 6.3)) for _ in range(26)]
CHISPAS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(5, 10), rng.uniform(0, 6.3)) for _ in range(22)]
# gotas de «sudor» sobre la piel (coordenadas locales del hipopótamo), tamaño y segundo en que salen
GOTAS = [(-210, -95, 18, 5.0), (-120, -142, 20, 5.25), (-25, -152, 19, 5.1), (70, -132, 18, 5.45),
         (-170, -25, 17, 5.6), (-70, -70, 20, 5.35), (25, -45, 18, 5.75), (125, -95, 17, 5.9),
         (205, -118, 16, 5.55), (262, -62, 18, 6.0), (335, -72, 16, 6.15), (-262, 30, 16, 6.25),
         (95, 15, 17, 6.3), (372, -5, 15, 6.1), (-130, 60, 16, 6.4)]

HX = 430          # centro del cuerpo en pantalla
AGUA = 1575       # nivel del agua delante del hipopótamo
SOL = (905, 860)


def hipo_y(t):
    """Sale del agua: al principio solo asoman ojos y orejas."""
    return lerp(1650, 1415, seg(t, 0, 2.2)) + 5 * math.sin(t * 2.2) * seg(t, 2.0, 2.6)


def hipopotamo(t, roj):
    y = hipo_y(t)
    piel = mix("#9a8bb0", "#c9799a", roj * 0.75)
    piel2 = mix("#c7b3cf", "#f0a2b4", roj * 0.75)
    rosa = "#f4a6b8"
    # parpadeo y ojos entornados por el sol (3-6,8 s); en la revelación, ojos bien abiertos
    sol_ojo = seg(t, 3.0, 4.0) * (1 - seg(t, 6.8, 7.2))
    blink = 0.12 if (t % 2.9) < 0.13 else 1.0
    abre = min(blink, 1 - 0.45 * sol_ojo)
    oreja = 10 * math.sin(t * 9) * (0.4 + 0.6 * (math.sin(t * 1.3) > 0.6))
    resp = 1 + 0.012 * math.sin(t * 2.5)
    g = [f"<g transform='translate({HX},{y:.1f}) scale({resp:.4f},{1/resp:.4f})'>"]
    # patas (quedan casi todas bajo el agua)
    for lx in (-200, -70, 110, 210):
        g.append(f"<rect x='{lx - 42}' y='90' width='84' height='150' rx='34' fill='{mix(piel, '#000000', 0.12)}' stroke='{INK}' stroke-width='{LW}'/>")
    # cola
    g.append(f"<path d='M-290 -40 Q-335 -20 -330 25' fill='none' stroke='{INK}' stroke-width='22' stroke-linecap='round'/>")
    g.append(f"<path d='M-290 -40 Q-335 -20 -330 25' fill='none' stroke='{piel}' stroke-width='10' stroke-linecap='round'/>")
    # cuerpo (barril)
    g.append(f"<ellipse cx='-40' cy='0' rx='275' ry='175' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<path d='M-260 70 Q-40 190 200 80 Q-40 150 -260 70 Z' fill='{piel2}' opacity='0.8'/>")
    g.append(f"<path d='M-230 -95 Q-120 -150 0 -150' fill='none' stroke='#ffffff' stroke-width='10' stroke-linecap='round' opacity='0.35'/>")
    # cabeza (mira a la derecha): frente con el ojo en lo alto y hocico ancho
    cab = ("M150 -150 Q250 -205 318 -150 Q350 -135 395 -128 Q470 -112 478 -30 Q484 55 410 82 "
           "Q320 108 230 80 Q150 58 130 0 Z")
    g.append(f"<path d='{cab}' fill='{piel}' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>")
    g.append(f"<path d='M250 60 Q340 92 430 64 Q400 90 330 92 Q270 88 250 60 Z' fill='{piel2}'/>")
    # oreja
    g.append(f"<g transform='translate(222,-178) rotate({-20 + oreja:.1f})'>"
             f"<ellipse cx='0' cy='-16' rx='20' ry='30' fill='{piel}' stroke='{INK}' stroke-width='7'/>"
             f"<ellipse cx='0' cy='-14' rx='9' ry='17' fill='{rosa}'/></g>")
    # ojo sobre su abultamiento
    g.append(f"<circle cx='290' cy='-150' r='42' fill='{piel}' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<ellipse cx='296' cy='-150' rx='26' ry='{26 * abre:.1f}' fill='#ffffff' stroke='{INK}' stroke-width='5'/>")
    if abre > 0.3:
        g.append(f"<circle cx='304' cy='{-150 + 2 * (1 - abre):.1f}' r='{14 * min(1, abre + 0.2):.1f}' fill='{INK}'/>")
        g.append(f"<circle cx='299' cy='-156' r='5' fill='#ffffff'/>")
    # ceja que se frunce con el calor
    g.append(f"<path d='M262 {-196 + 8 * sol_ojo:.1f} Q292 {-206 + 4 * sol_ojo:.1f} 322 {-194 + 10 * sol_ojo:.1f}' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    # orificios nasales en lo alto del hocico
    g.append(f"<ellipse cx='430' cy='-104' rx='13' ry='8' fill='{INK}' transform='rotate(-15 430 -104)'/>")
    g.append(f"<ellipse cx='462' cy='-90' rx='10' ry='7' fill='{INK}' transform='rotate(-25 462 -90)'/>")
    # boca sonriente y mejilla
    g.append(f"<path d='M476 18 Q410 50 330 34' fill='none' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>")
    g.append(f"<ellipse cx='345' cy='-20' rx='30' ry='17' fill='{rosa}' opacity='0.75'/>")
    g.append(f"<rect x='430' y='22' width='16' height='22' rx='5' fill='#fffaf0' stroke='{INK}' stroke-width='4'/>")
    # gotas de «sudor»: transparentes y brillantes, se vuelven rojas en la revelación
    for gx, gy, gr, ga in GOTAS:
        k = rebote(t, ga, 0.45)
        if k <= 0:
            continue
        resb = 10 * seg(t, ga, ga + 3.5)
        col = mix("#bfe9ff", "#e8261f", roj)
        op = lerp(0.85, 1.0, roj)
        g.append(f"<g transform='translate({gx},{gy + resb:.1f}) scale({k * gr / 18:.3f})'>"
                 f"<path d='M0 -24 Q15 -3 13 8 Q10 20 0 20 Q-10 20 -13 8 Q-15 -3 0 -24 Z' fill='{col}' opacity='{op:.2f}' stroke='{INK}' stroke-width='4'/>"
                 f"<ellipse cx='-4' cy='4' rx='3.5' ry='6' fill='#ffffff' opacity='0.85'/></g>")
    g.append("</g>")
    return "".join(g), y


def acacia(x, y, s, col):
    return (f"<g transform='translate({x},{y}) scale({s})'>"
            f"<path d='M-6 0 L-4 -70 L-40 -110 M-4 -70 L30 -115 M-4 -70 L-2 -118' fill='none' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>"
            f"<path d='M-6 0 L-4 -70 L-40 -110 M-4 -70 L30 -115 M-4 -70 L-2 -118' fill='none' stroke='#7a5236' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M-110 -112 Q-90 -150 -20 -150 Q50 -160 110 -128 Q120 -108 80 -104 L-90 -100 Q-120 -100 -110 -112 Z' fill='{col}' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/></g>")


def frame(t):
    calor = seg(t, 2.3, 4.8)                 # el sol aprieta
    roj = seg(t, 6.8, 7.6)                   # revelación: rojo
    halo = seg(t, 7.0, 8.0)
    top = mix("#5fb8ec", "#7fc4ee", calor); mid = mix("#a8dcf5", "#ffe9b0", calor); low = mix("#ffe6b0", "#ffc978", calor)
    top = mix(top, "#ffb88a", roj * 0.35); mid = mix(mid, "#ffd1a0", roj * 0.4)
    sol_r = lerp(78, 112, calor) + 4 * math.sin(t * 6)
    defs = (f"<linearGradient id='cielo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
            f"<stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>"
            f"<radialGradient id='brillo'><stop offset='0' stop-color='#fffbe0' stop-opacity='{lerp(0.55, 0.95, calor):.2f}'/>"
            f"<stop offset='1' stop-color='#ffd24a' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='rio' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#5cc0d8'/><stop offset='1' stop-color='#2a77a6'/></linearGradient>"
            f"<radialGradient id='escudo'><stop offset='0.55' stop-color='#ff7a2f' stop-opacity='0'/>"
            f"<stop offset='0.8' stop-color='#ff9a3c' stop-opacity='{0.55 * halo:.2f}'/><stop offset='1' stop-color='#ffcf5a' stop-opacity='0'/></radialGradient>")
    s = [f"<rect width='{W}' height='{H}' fill='url(#cielo)'/>"]
    esc = []
    # nubes suaves (arriba, tranquilas)
    for i, (cx, cy, sc) in enumerate([(160, 940, 1.0), (720, 1010, 0.8)]):
        dx = t * (10 + 6 * i)
        esc.append(f"<g transform='translate({cx + dx:.0f},{cy}) scale({sc})' opacity='0.95'>"
                   f"<path d='M0 40 Q10 0 60 10 Q85 -30 140 0 Q190 -10 200 40 Z' fill='#fffaf0' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # sol con brillo
    esc.append(f"<circle cx='{SOL[0]}' cy='{SOL[1]}' r='{sol_r * 3.2:.0f}' fill='url(#brillo)'/>")
    esc.append(f"<circle cx='{SOL[0]}' cy='{SOL[1]}' r='{sol_r:.0f}' fill='{mix('#ffe15a', '#fff3a8', calor)}' stroke='{mix('#ffb020', '#ff8a1e', calor)}' stroke-width='9'/>")
    for a in range(0, 360, 30):
        ra = math.radians(a + t * 12)
        r1 = sol_r + 22; r2 = sol_r + 52 + 10 * math.sin(t * 5 + a)
        esc.append(f"<line x1='{SOL[0] + r1 * math.cos(ra):.0f}' y1='{SOL[1] + r1 * math.sin(ra):.0f}' x2='{SOL[0] + r2 * math.cos(ra):.0f}' y2='{SOL[1] + r2 * math.sin(ra):.0f}' stroke='#ffb020' stroke-width='9' stroke-linecap='round'/>")
    # pájaros lejanos
    for i in range(3):
        bx = (t * 55 + i * 120) % 1400 - 200; by = 1060 + i * 28 + 8 * math.sin(t * 2 + i)
        al = 10 * math.sin(t * 10 + i)
        esc.append(f"<path d='M{bx - 18:.0f} {by - al:.0f} Q{bx - 8:.0f} {by - 6:.0f} {bx:.0f} {by:.0f} Q{bx + 8:.0f} {by - 6:.0f} {bx + 18:.0f} {by - al:.0f}' fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    # colinas de la sabana y acacias
    esc.append(f"<path d='M0 1190 Q180 1130 380 1170 T760 1150 T1080 1170 L1080 1400 L0 1400 Z' fill='#e0b862' stroke='{INK}' stroke-width='{LW}'/>")
    esc.append(acacia(150, 1182, 1.0, "#6f9a3c"))
    esc.append(acacia(640, 1160, 0.75, "#7aa646"))
    esc.append(acacia(980, 1176, 0.9, "#6f9a3c"))
    esc.append(f"<path d='M0 1250 Q260 1215 540 1250 T1080 1240 L1080 1400 L0 1400 Z' fill='#b9c24e' stroke='{INK}' stroke-width='{LW}'/>")
    for i in range(14):
        gx = 30 + i * 78; gy = 1262 + 6 * math.sin(i * 2.1)
        sw = 5 * math.sin(t * 2 + i)
        esc.append(f"<path d='M{gx} {gy + 30} Q{gx + sw:.0f} {gy + 5} {gx + 6 + sw:.0f} {gy - 16} M{gx + 14} {gy + 30} Q{gx + 18 + sw:.0f} {gy + 10} {gx + 28 + sw:.0f} {gy - 4}' fill='none' stroke='#7a8d2e' stroke-width='6' stroke-linecap='round'/>")
    # río (detrás)
    esc.append(f"<path d='M0 1312 Q270 1296 540 1312 T1080 1306 L1080 1920 L0 1920 Z' fill='url(#rio)' stroke='{INK}' stroke-width='{LW}'/>")
    # halo naranja (protector) detrás del hipopótamo
    hip, hy = hipopotamo(t, roj)
    if halo > 0:
        esc.append(f"<ellipse cx='{HX + 90}' cy='{hy - 20:.0f}' rx='{lerp(380, 520, halo) + 8 * math.sin(t * 8):.0f}' ry='{lerp(250, 360, halo):.0f}' fill='url(#escudo)'/>")
    esc.append(hip)
    # agua delante (tapa patas y vientre)
    ola = " ".join(f"Q{x + 45} {AGUA - 14 + 8 * math.sin(t * 3 + x * 0.02):.0f} {x + 90} {AGUA + 6 * math.sin(t * 3 + x * 0.03):.0f}" for x in range(-90, 1170, 90))
    esc.append(f"<path d='M-90 {AGUA} {ola} L1180 1920 L-90 1920 Z' fill='#3f9cc6' stroke='{INK}' stroke-width='7'/>")
    # ondas alrededor del hipopótamo
    for i in range(3):
        k = ((t * 0.55) + i / 3) % 1
        rx = lerp(260, 560, k)
        esc.append(f"<ellipse cx='{HX + 80}' cy='{AGUA + 30}' rx='{rx:.0f}' ry='{rx * 0.12:.0f}' fill='none' stroke='#d8f4ff' stroke-width='{lerp(8, 2, k):.1f}' opacity='{0.8 * (1 - k):.2f}'/>")
    # chorreones de agua al salir del río (0-2,6 s)
    if t < 2.8:
        for i in range(10):
            px = HX - 240 + i * 62; ph = (t * 1.6 + i * 0.37) % 1
            py = hy - 120 + 40 * math.sin(i) + ph * 300
            op = (1 - ph) * (1 - seg(t, 2.2, 2.8))
            if py < AGUA:
                esc.append(f"<ellipse cx='{px:.0f}' cy='{py:.0f}' rx='7' ry='11' fill='#dff6ff' stroke='{INK}' stroke-width='3' opacity='{op:.2f}'/>")
    # ondas de calor que suben del lomo (2,8-6,9 s)
    oc = seg(t, 2.8, 3.6) * (1 - seg(t, 6.6, 7.0))
    if oc > 0:
        for i in range(3):
            ox = HX - 170 + i * 150; base = hy - 210
            k = ((t * 0.8) + i * 0.33) % 1
            oy = base - k * 140
            d = " ".join(f"Q{ox + (14 if j % 2 == 0 else -14)} {oy - j * 22 - 11:.0f} {ox} {oy - (j + 1) * 22:.0f}" for j in range(5))
            esc.append(f"<path d='M{ox} {oy:.0f} {d}' fill='none' stroke='#ff8a3a' stroke-width='8' stroke-linecap='round' opacity='{oc * (1 - k) * 0.9:.2f}'/>")
    # rayos del sol hacia el hipopótamo; en la revelación rebotan
    ry_ = seg(t, 2.6, 3.4)
    for i, (dx, dy) in enumerate([(-130, -150), (40, -175), (230, -165)]):
        tx, ty = HX + dx, hy + dy
        if halo > 0:
            # rayo que rebota contra el halo
            k = ((t - 7.0) * 1.2 + i * 0.3) % 1
            hxp, hyp = lerp(tx, SOL[0], 0.25), lerp(ty, SOL[1], 0.25)
            ex, ey = hxp + (hxp - SOL[0]) * -0.0 - 160 + i * 60, hyp - 170 - k * 60
            esc.append(f"<line x1='{SOL[0]}' y1='{SOL[1]}' x2='{hxp:.0f}' y2='{hyp:.0f}' stroke='#ffd23f' stroke-width='10' stroke-linecap='round' stroke-dasharray='26 18' opacity='0.85'/>")
            esc.append(f"<line x1='{hxp:.0f}' y1='{hyp:.0f}' x2='{lerp(hxp, ex, halo):.0f}' y2='{lerp(hyp, ey, halo):.0f}' stroke='#ffd23f' stroke-width='10' stroke-linecap='round' stroke-dasharray='26 18' opacity='0.85'/>")
        elif ry_ > 0:
            off = (t * 120) % 44
            esc.append(f"<line x1='{SOL[0]}' y1='{SOL[1]}' x2='{lerp(SOL[0], tx, ry_):.0f}' y2='{lerp(SOL[1], ty, ry_):.0f}' stroke='#ffc93a' stroke-width='10' stroke-linecap='round' stroke-dasharray='26 18' stroke-dashoffset='{-off:.0f}' opacity='0.8'/>")
    # chispas brillantes en la revelación
    if halo > 0:
        for cx, cy, cr, ph in CHISPAS:
            px = HX + 90 + cx * 470; py = hy - 20 + cy * 320
            a = halo * (0.5 + 0.5 * math.sin(t * 7 + ph))
            esc.append(f"<g transform='translate({px:.0f},{py:.0f}) rotate({t * 90 + ph * 50:.0f})' opacity='{a:.2f}'>"
                       f"<path d='M0 {-cr * 2} L{cr * 0.5} {-cr * 0.5} L{cr * 2} 0 L{cr * 0.5} {cr * 0.5} L0 {cr * 2} L{-cr * 0.5} {cr * 0.5} L{-cr * 2} 0 L{-cr * 0.5} {-cr * 0.5} Z' fill='#fff3a0'/></g>")
    # destellos del agua
    for dx, dy, dl, ph in DESTELLOS:
        if dy < AGUA + 20:
            continue
        a = 0.5 + 0.5 * math.sin(t * 3 + ph)
        esc.append(f"<line x1='{dx:.0f}' y1='{dy:.0f}' x2='{dx + dl:.0f}' y2='{dy:.0f}' stroke='#e8fbff' stroke-width='6' stroke-linecap='round' opacity='{0.7 * a:.2f}'/>")
    # juncos en primer plano
    for jx, jh, lado in ((40, 300, 1), (95, 230, 1), (1010, 280, -1), (1055, 210, -1)):
        sw = 10 * math.sin(t * 1.8 + jx)
        esc.append(f"<path d='M{jx} 1930 Q{jx + 10 * lado} {1930 - jh / 2:.0f} {jx + sw:.0f} {1930 - jh}' fill='none' stroke='{INK}' stroke-width='16' stroke-linecap='round'/>"
                   f"<path d='M{jx} 1930 Q{jx + 10 * lado} {1930 - jh / 2:.0f} {jx + sw:.0f} {1930 - jh}' fill='none' stroke='#5e9a3a' stroke-width='8' stroke-linecap='round'/>"
                   f"<rect x='{jx + sw - 11:.0f}' y='{1930 - jh - 60}' width='22' height='70' rx='11' fill='#8a5a32' stroke='{INK}' stroke-width='6'/>")
    z = 1 + 0.16 * seg(t, 6.9, 9.6)
    s.append(zoom(HX + 160, 1380, z, "".join(esc)))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>{defs}</defs>{''.join(s)}</svg>"
