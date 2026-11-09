"""2026-11-09-c5 · Las palomitas estallan a unos 180 °C: el agua que hay dentro del grano de maíz
se convierte en vapor, la presión rompe la cáscara y el almidón se hincha como una espuma blanca.

0-2,5 s  un grano de maíz original con cara cae botando en una sartén sobre el fuego.
2,5-5 s  dentro del grano se ve una gotita de agua; la llama crece y sale calor.
5-7,5 s  la gota hierve y se vuelve vapor; el grano se pone rojo, se hincha y tiembla.
7,5-10 s REVELACION: ¡POP! destello, el grano se convierte en una gran palomita blanca,
         saltan trocitos de cáscara, los demás granos también explotan y zoom de cámara.
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix, zoom, rebote

DUR = 10.0
REVELACION = 7.45
MUSICA = 6

rng = np.random.default_rng(51)
CX, KY = 540, 1405          # centro del grano protagonista
PAN_Y = 1470                # centro de la boca de la sartén
DOTS = [(rng.uniform(0, W), rng.uniform(0, 1000), rng.uniform(0, 6.28)) for _ in range(26)]
CASCARA = [(rng.uniform(-math.pi * 0.95, -math.pi * 0.05), rng.uniform(380, 720), rng.uniform(14, 24), rng.uniform(0, 360)) for _ in range(12)]
CHISPAS = [(rng.uniform(0, 2 * math.pi), rng.uniform(250, 520), rng.uniform(8, 16)) for _ in range(18)]
# granos pequeños: x, y, escala, segundo en que explotan, salto
GRANOS = [(330, 1478, 0.34, 7.85, 1), (755, 1482, 0.34, 8.3, -1), (415, 1515, 0.30, 8.75, -1),
          (680, 1520, 0.30, 9.1, 1), (260, 1515, 0.27, 9.4, 1)]

GRANO = ("M0 -112 C88 -112 104 -24 84 32 C66 82 30 112 0 117 C-30 112 -66 82 -84 32 "
         "C-104 -24 -88 -112 0 -112 Z")
PUNTA = "M-26 96 Q0 80 26 96 C18 108 8 116 0 117 C-8 116 -18 108 -26 96 Z"
LOBULOS = [(-118, -88, 58), (118, -88, 58), (0, -150, 66), (-102, 6, 82), (102, 6, 82),
           (-62, 82, 72), (62, 82, 72), (0, -54, 100), (0, 34, 92)]


def ojos(blink, mirar=0, susto=0):
    g = []
    for ex in (-34, 34):
        ry = 26 * blink
        g.append(f"<ellipse cx='{ex}' cy='-30' rx='{22 + 4 * susto:.1f}' ry='{max(2, ry + 6 * susto):.1f}' fill='#ffffff' stroke='{INK}' stroke-width='6'/>")
        if blink > 0.3:
            g.append(f"<circle cx='{ex + mirar:.1f}' cy='-26' r='{11 - 3 * susto:.1f}' fill='{INK}'/>")
            g.append(f"<circle cx='{ex + mirar - 4:.1f}' cy='-31' r='4' fill='#ffffff'/>")
    return "".join(g)


def grano(t, calor, hinchar, temblor, s=1.0, cara=True, corte=0.0):
    """Grano de maíz para palomitas: forma de gota, punta pálida, germen claro y brillo."""
    col = mix("#f6a91f", "#e2512a", calor)
    luz = mix("#ffd458", "#ff9a6a", calor)
    sx = s * (1 + 0.08 * hinchar + 0.02 * math.sin(t * 40) * temblor)
    sy = s * (1 + 0.10 * hinchar - 0.02 * math.sin(t * 40) * temblor)
    g = [f"<g transform='scale({sx:.4f},{sy:.4f})'>",
         f"<path d='{GRANO}' fill='{col}' stroke='{INK}' stroke-width='{LW / s if s < 1 else LW:.1f}' stroke-linejoin='round'/>",
         f"<path d='M-58 -70 C-40 -98 0 -100 20 -94 C-20 -82 -46 -60 -56 -30 Z' fill='{luz}' opacity='0.9'/>",
         f"<path d='{PUNTA}' fill='#f3e3b5' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"]
    if corte > 0:
        # ventanita al interior: almidón claro y una gota de agua que acaba hirviendo
        g.append(f"<ellipse cx='0' cy='42' rx='{54 * corte:.1f}' ry='{48 * corte:.1f}' fill='#fff1c9' stroke='{INK}' stroke-width='5'/>")
        hierve = seg(t, 5.0, 7.2)
        dr = 27 * corte * (1 - 0.45 * hierve)
        wob = 2 * math.sin(t * 6)
        g.append(f"<path d='M0 {22 - dr * 0.9 + wob:.1f} C{dr * 0.6:.1f} {34 - dr * 0.3:.1f} {dr:.1f} {40 + dr * 0.3:.1f} {dr * 0.85:.1f} {44 + dr * 0.5:.1f} "
                 f"A{dr * 0.9:.1f} {dr * 0.9:.1f} 0 0 1 {-dr * 0.85:.1f} {44 + dr * 0.5:.1f} C{-dr:.1f} {40 + dr * 0.3:.1f} {-dr * 0.6:.1f} {34 - dr * 0.3:.1f} 0 {22 - dr * 0.9 + wob:.1f} Z' "
                 f"fill='#47b8f5' stroke='{INK}' stroke-width='4'/>")
        g.append(f"<circle cx='{-dr * 0.3:.1f}' cy='{42:.1f}' r='{dr * 0.22:.1f}' fill='#ffffff' opacity='0.8'/>")
        for i in range(6):
            ph = (t * 1.6 + i / 6) % 1
            if hierve > 0.02:
                bx = 26 * math.sin(i * 2.3 + t * 3) * corte
                by = 70 - 60 * ph
                g.append(f"<circle cx='{bx:.1f}' cy='{by:.1f}' r='{(4 + 7 * ph) * hierve:.1f}' fill='#ffffff' stroke='#8fcfee' stroke-width='3' opacity='{0.95 * (1 - ph * 0.6):.2f}'/>")
    if cara:
        blink = 0.12 if ((t + 1.1) % 2.8) < 0.13 else 1.0
        g.append(ojos(blink, mirar=4 * math.sin(t * 1.3), susto=seg(t, 5.2, 6.4)))
        g.append(f"<ellipse cx='-56' cy='4' rx='13' ry='8' fill='#ff6f6f' opacity='{0.55 + 0.4 * calor:.2f}'/>")
        g.append(f"<ellipse cx='56' cy='4' rx='13' ry='8' fill='#ff6f6f' opacity='{0.55 + 0.4 * calor:.2f}'/>")
        miedo = seg(t, 5.2, 6.4)
        if miedo < 0.5:
            g.append(f"<path d='M-18 0 Q0 16 18 0' fill='none' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>")
        else:
            g.append(f"<ellipse cx='0' cy='6' rx='9' ry='{8 + 3 * math.sin(t * 20):.1f}' fill='#7a2a1f' stroke='{INK}' stroke-width='5'/>")
        # gotas de sudor con el calor
        sud = seg(t, 5.4, 6.2)
        if sud > 0:
            yy = -70 + ((t * 60) % 50)
            g.append(f"<path d='M78 {yy:.0f} q8 14 0 20 q-8 -6 0 -20 Z' fill='#7fd6ff' stroke='{INK}' stroke-width='4' opacity='{sud:.2f}'/>")
    g.append("</g>")
    return "".join(g)


def palomita(t, s=1.0, cara=True, feliz=1.0):
    """Palomita: racimo de lóbulos blancos con trocitos de cáscara naranja en la base."""
    g = [f"<g transform='scale({s:.4f})'>"]
    g.append(f"<path d='M-46 128 Q-20 150 0 140 Q22 152 46 128 L30 104 L-30 104 Z' fill='#f6a91f' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
    for i, (lx, ly, lr) in enumerate(LOBULOS):
        wob = 3 * math.sin(t * 5 + i)
        g.append(f"<circle cx='{lx}' cy='{ly + wob:.1f}' r='{lr}' fill='#fffaf0' stroke='{INK}' stroke-width='{LW}'/>")
        g.append(f"<path d='M{lx - lr * 0.55:.1f} {ly + lr * 0.45 + wob:.1f} A{lr} {lr} 0 0 0 {lx + lr * 0.7:.1f} {ly + lr * 0.55 + wob:.1f}' "
                 f"fill='none' stroke='#f3d98d' stroke-width='12' stroke-linecap='round'/>")
        g.append(f"<circle cx='{lx - lr * 0.35:.1f}' cy='{ly - lr * 0.4 + wob:.1f}' r='{lr * 0.16:.1f}' fill='#ffffff'/>")
    g.append(f"<path d='M-70 110 L-40 92 L-52 124 Z' fill='#e88a16' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
    if cara:
        blink = 0.12 if (t % 2.6) < 0.13 else 1.0
        g.append("<g transform='translate(0,-20)'>")
        g.append(ojos(blink, mirar=5 * math.sin(t * 2)))
        g.append(f"<ellipse cx='-60' cy='8' rx='15' ry='9' fill='#ff8f8f' opacity='0.8'/>")
        g.append(f"<ellipse cx='60' cy='8' rx='15' ry='9' fill='#ff8f8f' opacity='0.8'/>")
        g.append(f"<path d='M-34 4 Q0 {4 + 44 * feliz:.1f} 34 4 Z' fill='#9b2f24' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>")
        g.append(f"<path d='M-16 {14 + 20 * feliz:.1f} Q0 {6 + 18 * feliz:.1f} 16 {14 + 20 * feliz:.1f}' fill='#ff7f87'/>")
        g.append("</g>")
    g.append("</g>")
    return "".join(g)


def cocina(t, rev):
    s = []
    top = mix("#ffe9c7", "#fff3b0", rev); low = mix("#ffd29a", "#ffcf6a", rev)
    s.append(f"<linearGradient id='pared' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/>"
             f"<stop offset='1' stop-color='{low}'/></linearGradient>")
    s.append(f"<rect width='{W}' height='{H}' fill='url(#pared)'/>")
    # papel pintado suave: lunares
    for dx, dy, ph in DOTS:
        s.append(f"<circle cx='{dx:.0f}' cy='{dy:.0f}' r='{9 + 2 * math.sin(t * 2 + ph):.1f}' fill='#ffffff' opacity='0.35'/>")
    # azulejos de la pared (de y=1000 hacia abajo)
    s.append(f"<rect x='-10' y='1000' width='1100' height='700' fill='{mix('#8fd3c7', '#a8eadc', rev)}' stroke='{INK}' stroke-width='{LW}'/>")
    for y in range(1090, 1700, 90):
        s.append(f"<line x1='0' y1='{y}' x2='1080' y2='{y}' stroke='#ffffff' stroke-width='5' opacity='0.55'/>")
    for i, x in enumerate(range(0, 1100, 108)):
        for j, y in enumerate(range(1000, 1700, 90)):
            off = 54 if j % 2 else 0
            s.append(f"<line x1='{x + off}' y1='{y}' x2='{x + off}' y2='{y + 90}' stroke='#ffffff' stroke-width='5' opacity='0.55'/>")
    # repisa con frascos a los lados (no estorban al centro)
    s.append(f"<rect x='-10' y='1040' width='230' height='22' rx='6' fill='#c47a45' stroke='{INK}' stroke-width='7'/>")
    s.append(f"<rect x='860' y='1040' width='230' height='22' rx='6' fill='#c47a45' stroke='{INK}' stroke-width='7'/>")
    for fx, fc, fh in ((50, '#ff8a65', 70), (140, '#ffd54f', 90), (900, '#81c784', 80), (990, '#ba68c8', 64)):
        s.append(f"<rect x='{fx - 30}' y='{1040 - fh}' width='60' height='{fh}' rx='12' fill='{fc}' stroke='{INK}' stroke-width='7'/>")
        s.append(f"<rect x='{fx - 34}' y='{1040 - fh - 16}' width='68' height='18' rx='6' fill='#8d5a3a' stroke='{INK}' stroke-width='6'/>")
    # mazorca de maíz apoyada en la pared (detrás del mango)
    s.append(mazorca(t))
    return "".join(s)


def mazorca(t):
    sw = 3 * math.sin(t * 1.5)
    g = [f"<g transform='translate(960,1300) rotate({12 + sw:.1f})'>",
         f"<path d='M-20 150 Q-90 60 -70 -60 Q-40 40 -6 120 Z' fill='#7cc35a' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>",
         f"<path d='M-56 -150 Q0 -190 56 -150 L60 130 Q0 170 -60 130 Z' fill='#f7c531' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    for row in range(9):
        y = -140 + row * 32
        for col in range(-1, 2):
            g.append(f"<rect x='{col * 34 - 14}' y='{y}' width='28' height='26' rx='10' fill='#ffd84d' stroke='#d79a12' stroke-width='4'/>")
    g.append(f"<path d='M20 150 Q90 50 74 -40 Q46 50 6 120 Z' fill='#5eae46' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append(f"<path d='M-30 150 Q0 220 30 150 Z' fill='#5eae46' stroke='{INK}' stroke-width='7' stroke-linejoin='round'/>")
    g.append("</g>")
    return "".join(g)


def fuego(t, calor):
    s = []
    for i, fx in enumerate(range(330, 760, 54)):
        h = (34 + 50 * calor) * (0.8 + 0.25 * math.sin(t * 13 + i * 1.7))
        w = 22 + 6 * calor
        s.append(f"<path d='M{fx - w:.0f} 1690 Q{fx - w * 0.7:.0f} {1690 - h * 0.6:.0f} {fx + 4 * math.sin(t * 9 + i):.0f} {1690 - h:.0f} "
                 f"Q{fx + w * 0.7:.0f} {1690 - h * 0.6:.0f} {fx + w:.0f} 1690 Z' fill='{mix('#3d7cff', '#ff8a2a', calor * 0.6)}' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>")
        s.append(f"<path d='M{fx - w * 0.45:.0f} 1690 Q{fx:.0f} {1690 - h * 0.75:.0f} {fx + w * 0.45:.0f} 1690 Z' fill='{mix('#9fd0ff', '#ffe066', calor)}'/>")
    return "".join(s)


def sarten_atras():
    return (f"<ellipse cx='{CX}' cy='{PAN_Y}' rx='350' ry='84' fill='#3a3f4a' stroke='{INK}' stroke-width='{LW}'/>"
            f"<ellipse cx='{CX}' cy='{PAN_Y + 10}' rx='318' ry='66' fill='#2a2e36'/>")


def sarten_delante():
    s = [f"<path d='M{CX - 350} {PAN_Y} A350 84 0 0 0 {CX + 350} {PAN_Y} L{CX + 318} {PAN_Y + 120} "
         f"Q{CX} {PAN_Y + 170} {CX - 318} {PAN_Y + 120} Z' fill='#4a505d' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>",
         f"<path d='M{CX - 300} {PAN_Y + 70} Q{CX - 120} {PAN_Y + 120} {CX + 40} {PAN_Y + 118}' fill='none' stroke='#7b8494' stroke-width='10' stroke-linecap='round'/>",
         # mango
         f"<path d='M{CX + 330} {PAN_Y + 40} L{CX + 560} {PAN_Y - 10} Q{CX + 590} {PAN_Y + 10} {CX + 566} {PAN_Y + 34} L{CX + 336} {PAN_Y + 86} Z' "
         f"fill='#c0392b' stroke='{INK}' stroke-width='{LW}' stroke-linejoin='round'/>"]
    return "".join(s)


def cocina_delante(t):
    s = [f"<rect x='-10' y='1690' width='1100' height='40' fill='#2f3440' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='-10' y='1730' width='1100' height='200' fill='#f4f1ea' stroke='{INK}' stroke-width='{LW}'/>",
         f"<rect x='150' y='1855' width='780' height='40' rx='14' fill='#d9d2c4' stroke='{INK}' stroke-width='6'/>"]
    for i, kx in enumerate((200, 380, 700, 880)):
        rot = (30 + 60 * seg(t, 2.2, 3.2)) if i == 1 else 0
        s.append(f"<g transform='translate({kx},1792) rotate({rot:.1f})'><circle r='34' fill='#3b3f46' stroke='{INK}' stroke-width='7'/>"
                 f"<rect x='-6' y='-30' width='12' height='26' rx='5' fill='#ffd23f'/></g>")
    return "".join(s)


def vapor(t, k):
    s = []
    for i in range(7):
        ph = (t * 0.45 + i / 7) % 1
        x = 260 + i * 90 + 30 * math.sin(t * 2 + i * 1.3)
        y = 1430 - 380 * ph
        op = k * 0.65 * math.sin(math.pi * ph)
        if op > 0.02:
            s.append(f"<path d='M{x:.0f} {y + 60:.0f} q-22 -30 0 -60 q22 -30 0 -60' fill='none' stroke='#ffffff' stroke-width='14' stroke-linecap='round' opacity='{op:.2f}'/>")
    return "".join(s)


def frame(t):
    rev = seg(t, REVELACION, REVELACION + 0.25)
    calor = seg(t, 2.4, 7.3)
    defs = cocina(t, rev)
    sc = [defs.split("</linearGradient>")[0] + "</linearGradient>"]
    fondo = defs.split("</linearGradient>", 1)[1]
    cuerpo = [fondo]
    # rayos de explosión detrás
    if t >= REVELACION:
        k = seg(t, REVELACION, REVELACION + 0.4)
        rays = []
        for i in range(16):
            a = i * 2 * math.pi / 16 + t * 0.35
            a2 = a + 0.11
            R = 1500 * k
            rays.append(f"<path d='M{CX} 1300 L{CX + R * math.cos(a):.0f} {1300 + R * math.sin(a):.0f} L{CX + R * math.cos(a2):.0f} {1300 + R * math.sin(a2):.0f} Z' fill='#ffffff' opacity='0.38'/>")
        cuerpo.append("".join(rays))
    cuerpo.append(vapor(t, 0.3 + 0.7 * calor))
    cuerpo.append(fuego(t, calor))
    cuerpo.append(sarten_atras())
    # granos pequeños (detrás del protagonista): tiemblan y explotan después
    peque = []
    for i, (gx, gy, gs, tp, lado) in enumerate(GRANOS):
        if t < tp:
            hop = abs(math.sin(t * 7 + i)) * 10 * calor
            peque.append(f"<g transform='translate({gx},{gy - 40 * gs - hop:.1f}) rotate({8 * math.sin(t * 5 + i) * calor:.1f})'>{grano(t, calor, 0, calor, gs, cara=False)}</g>")
        else:
            k = clamp((t - tp) / 0.9)
            y = gy - 60 * gs - 330 * math.sin(math.pi * min(1, k * 0.9)) * (1 - 0.5 * k)
            x = gx + lado * 110 * k
            peque.append(f"<g transform='translate({x:.1f},{y:.1f}) rotate({lado * 200 * k:.1f}) scale({rebote(t, tp, 0.35):.3f})'>{palomita(t, gs * 0.75, cara=False)}</g>")
    cuerpo.append("".join(peque[:2]))
    # protagonista
    if t < REVELACION:
        caida = seg(t, 0, 0.7)
        y = lerp(1060, KY, caida * caida)
        if t > 0.7:
            y = KY - abs(math.sin((t - 0.7) * 6)) * 60 * math.exp(-(t - 0.7) * 2.5)
        temb = seg(t, 5.0, 7.3)
        jx = 6 * math.sin(t * 47) * temb
        rot = lerp(-25, 0, caida) + 4 * math.sin(t * 31) * temb
        cuerpo.append(f"<g transform='translate({CX + jx:.1f},{y:.1f}) rotate({rot:.1f})'>"
                      f"{grano(t, calor, seg(t, 5.2, 7.4), temb, 1.0, corte=seg(t, 2.5, 3.1))}</g>")
        # líneas de calor alrededor
        h = seg(t, 2.6, 4.0)
        for i, ox in enumerate((-160, 160)):
            for j in range(2):
                yy = 1360 - 40 * j + 10 * math.sin(t * 6 + i + j)
                cuerpo.append(f"<path d='M{CX + ox + j * 24 * (1 if ox > 0 else -1):.0f} {yy + 40:.0f} q-12 -20 0 -40 q12 -20 0 -40' fill='none' "
                              f"stroke='#ff6b3d' stroke-width='8' stroke-linecap='round' opacity='{0.85 * h:.2f}'/>")
    else:
        e = rebote(t, REVELACION, 0.45)
        y = lerp(KY, 1265, seg(t, REVELACION, REVELACION + 0.35)) + 8 * math.sin((t - REVELACION) * 4)
        cuerpo.append(f"<g transform='translate({CX},{y:.1f}) rotate({4 * math.sin(t * 2.5):.1f}) scale({1.08 * e:.4f})'>{palomita(t, 1.0, feliz=seg(t, 7.6, 8.1))}</g>")
        # trocitos de cáscara y chispas
        k = seg(t, REVELACION, REVELACION + 1.3)
        for a, d, r, ro in CASCARA:
            px = CX + math.cos(a) * d * k; py = 1350 + math.sin(a) * d * k + 520 * k * k
            if py < 1900:
                cuerpo.append(f"<g transform='translate({px:.0f},{py:.0f}) rotate({ro + 400 * k:.0f})'><path d='M{-r} 0 Q0 {-r} {r} 0 Q0 {r * 0.4:.1f} {-r} 0 Z' "
                              f"fill='#f39a1e' stroke='{INK}' stroke-width='4'/></g>")
        k2 = seg(t, REVELACION, REVELACION + 0.8)
        for a, d, r in CHISPAS:
            if k2 < 1:
                px = CX + math.cos(a) * d * k2; py = 1300 + math.sin(a) * d * k2
                cuerpo.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='{r * (1 - k2):.1f}' fill='#ffe14d' stroke='{INK}' stroke-width='3'/>")
    cuerpo.append("".join(peque[2:]))
    cuerpo.append(sarten_delante())
    cuerpo.append(cocina_delante(t))
    z = 1 + 0.12 * seg(t, REVELACION, 10)
    contenido = zoom(CX, 1380, z, "".join(cuerpo))
    flash = 0.0
    if t >= REVELACION:
        flash = 0.85 * (1 - seg(t, REVELACION, REVELACION + 0.45))
    extra = f"<rect width='{W}' height='{H}' fill='#ffffff' opacity='{flash:.2f}'/>" if flash > 0.01 else ""
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{sc[0]}</defs>{contenido}{extra}</svg>")
