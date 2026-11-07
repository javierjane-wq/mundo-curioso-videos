"""EJEMPLO de escena (atardecer azul en Marte). Copia su estructura para cada vídeo nuevo.

Reglas de composición (ver codigo/README.md):
- Protagonista y acción en la mitad de ABAJO (y > 1000): arriba van el logo y los textos.
- Fondo completo, contornos gruesos (INK, LW), colores planos vivos, personajes originales.
- Algo se mueve SIEMPRE: entrada del protagonista, movimiento secundario (parpadeo, antena,
  polvo, nubes) y un gran cambio en la REVELACION (luz, color, zoom de cámara).
"""
import math
import numpy as np
from lib import W, H, INK, LW, clamp, ease, seg, lerp, mix

DUR = 10.0
REVELACION = 7.45   # aparece el halo azul: golpe musical
MUSICA = 3

rng = np.random.default_rng(7)
STARS = [(rng.uniform(0, W), rng.uniform(0, 1250), rng.uniform(2.5, 6), rng.uniform(0, 6.28)) for _ in range(70)]
DUST = [(rng.uniform(0, W), rng.uniform(900, 1900), rng.uniform(3, 7), rng.uniform(20, 60)) for _ in range(40)]
ROCKS = [(120, 1640, 46), (930, 1580, 34), (760, 1820, 60), (330, 1880, 40), (1010, 1760, 28)]


def rover(t):
    """Robot explorador original: 6 ruedas, panel solar, mástil con cámara de dos lentes."""
    # entra desde la izquierda en 0-2 s, luego se para; rebote suave al rodar
    x = lerp(60, 330, seg(t, 0, 2.2))
    rolling = t < 2.3
    bob = 6 * math.sin(t * 22) if rolling else 2 * math.sin(t * 3)
    wheel_rot = lerp(0, 720, seg(t, 0, 2.2))
    # la cabeza mira al frente y luego gira hacia el Sol (derecha) a partir de 4,6 s
    head_turn = seg(t, 4.6, 5.6)
    head_tilt = lerp(0, -12, head_turn)
    blink = 1.0 if (t % 3.1) > 0.12 else 0.15
    ant = 8 * math.sin(t * 4.5)
    g = [f"<g transform='translate({x:.1f},{1520 + bob:.1f})'>"]
    # sombra
    g.append(f"<ellipse cx='0' cy='205' rx='260' ry='26' fill='#000' opacity='0.22'/>")
    # suspensión
    g.append(f"<path d='M-190 120 L-120 40 L0 70 L120 40 L190 120' fill='none' stroke='{INK}' stroke-width='16' stroke-linejoin='round'/>")
    g.append(f"<path d='M-190 120 L-120 40 L0 70 L120 40 L190 120' fill='none' stroke='#9aa3ad' stroke-width='8' stroke-linejoin='round'/>")
    # ruedas
    for wx in (-190, 0, 190):
        g.append(f"<g transform='translate({wx},150) rotate({wheel_rot:.1f})'>"
                 f"<circle r='58' fill='#3b3f46' stroke='{INK}' stroke-width='{LW}'/>"
                 f"<circle r='30' fill='#c9ced6' stroke='{INK}' stroke-width='6'/>"
                 + "".join(f"<rect x='-6' y='-56' width='12' height='18' rx='3' fill='#23262b' transform='rotate({a})'/>" for a in range(0, 360, 45))
                 + f"<circle r='8' fill='{INK}'/></g>")
    # cuerpo
    g.append(f"<rect x='-170' y='-40' width='340' height='110' rx='22' fill='#f2ead8' stroke='{INK}' stroke-width='{LW}'/>")
    g.append(f"<rect x='-150' y='-20' width='130' height='60' rx='10' fill='#e0d4bb' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='60' cy='15' r='16' fill='#ff7a45' stroke='{INK}' stroke-width='5'/>")
    g.append(f"<circle cx='110' cy='15' r='10' fill='#ffd23f' stroke='{INK}' stroke-width='5'/>")
    # panel solar
    g.append(f"<rect x='-200' y='-62' width='400' height='26' rx='8' fill='#2e5c9a' stroke='{INK}' stroke-width='{LW}'/>")
    for px in range(-160, 200, 60):
        g.append(f"<line x1='{px}' y1='-60' x2='{px}' y2='-38' stroke='#8fb3e8' stroke-width='4'/>")
    # antena
    g.append(f"<g transform='translate(-130,-62) rotate({ant:.1f})'><line x1='0' y1='0' x2='0' y2='-110' stroke='{INK}' stroke-width='8' stroke-linecap='round'/>"
             f"<circle cx='0' cy='-118' r='14' fill='#ff5a5f' stroke='{INK}' stroke-width='6'/></g>")
    # mástil
    g.append(f"<rect x='88' y='-230' width='26' height='175' rx='8' fill='#c9ced6' stroke='{INK}' stroke-width='{LW}'/>")
    # cabeza (cámara)
    g.append(f"<g transform='translate(101,-250) rotate({head_tilt:.1f})'>")
    g.append(f"<rect x='-100' y='-62' width='200' height='110' rx='28' fill='#f2ead8' stroke='{INK}' stroke-width='{LW}'/>")
    look = lerp(0, 14, head_turn)
    for ex in (-45, 45):
        g.append(f"<circle cx='{ex}' cy='-8' r='34' fill='#1e2a38' stroke='{INK}' stroke-width='7'/>")
        g.append(f"<g transform='translate({ex + look:.1f},-8) scale(1,{blink})'><circle r='17' fill='#5ec8ff'/>"
                 f"<circle cx='-6' cy='-7' r='7' fill='#fff'/></g>")
    g.append(f"<rect x='-30' y='-84' width='60' height='22' rx='8' fill='#ff7a45' stroke='{INK}' stroke-width='6'/>")
    g.append("</g></g>")
    return "".join(g)


def frame(t):
    day = 1 - seg(t, 4.8, 8.2)                  # 1 = de día, 0 = anochecer
    blue = seg(t, 7.2, 8.6)                     # halo azul
    # cielo: naranja de día -> marrón oscuro con halo azul al anochecer
    top = mix("#2b2440", "#e89a5c", day); mid = mix("#5a3a3a", "#f3b77c", day); low = mix("#7a4a38", "#f7cf98", day)
    sun_y = lerp(760, 1300, seg(t, 0.5, 8.8)); sun_x = lerp(820, 640, seg(t, 0.5, 8.8))
    sun_r = lerp(70, 80, seg(t, 4, 9))
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
         "<defs>",
         f"<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{top}'/><stop offset='0.55' stop-color='{mid}'/><stop offset='1' stop-color='{low}'/></linearGradient>",
         f"<radialGradient id='halo'><stop offset='0' stop-color='#eaf6ff' stop-opacity='{0.95*blue:.3f}'/>"
         f"<stop offset='0.25' stop-color='#8fd3ff' stop-opacity='{0.95*blue:.3f}'/>"
         f"<stop offset='0.6' stop-color='#3d8fe0' stop-opacity='{0.7*blue:.3f}'/><stop offset='1' stop-color='#1d4fa8' stop-opacity='0'/></radialGradient>",
         f"<radialGradient id='glow'><stop offset='0' stop-color='#fff4d6' stop-opacity='{0.7*day:.3f}'/><stop offset='1' stop-color='#ffb060' stop-opacity='0'/></radialGradient>",
         "</defs>",
         f"<rect width='{W}' height='{H}' fill='url(#sky)'/>"]
    z = 1 + 0.14 * seg(t, 7.2, 10)
    s.append(f"<g transform='translate({sun_x:.1f},{sun_y:.1f}) scale({z:.4f}) translate({-sun_x:.1f},{-sun_y:.1f})'>")
    # estrellas al anochecer
    st = seg(t, 6.8, 9.2)
    for sx, sy, sr, ph in STARS:
        a = st * (0.55 + 0.45 * math.sin(t * 3 + ph))
        if a > 0.02: s.append(f"<circle cx='{sx:.0f}' cy='{sy:.0f}' r='{sr:.1f}' fill='#fff' opacity='{a:.2f}'/>")
    # nubes de polvo lejanas
    for i, (cx, cy, sc) in enumerate([(200, 1000, 1.7), (900, 1110, 1.3), (560, 880, 1.1)]):
        dx = (t * 14 * (1 + i * 0.3)) % 1400 - 200
        col = mix("#8a5a4a", "#f9d7b0", day)
        s.append(f"<g transform='translate({cx + dx - 400:.0f},{cy}) scale({sc})' opacity='0.85'>"
                 f"<path d='M0 40 Q20 -10 80 5 Q110 -40 170 0 Q230 -15 250 40 Z' fill='{col}' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/></g>")
    # halo y Sol
    s.append(f"<circle cx='{sun_x:.0f}' cy='{sun_y:.0f}' r='{lerp(200, 680, blue):.0f}' fill='url(#halo)'/>")
    s.append(f"<circle cx='{sun_x:.0f}' cy='{sun_y:.0f}' r='{sun_r*3:.0f}' fill='url(#glow)'/>")
    sun_col = mix("#fffbe8", "#fff3c4", day)
    s.append(f"<circle cx='{sun_x:.0f}' cy='{sun_y:.0f}' r='{sun_r:.0f}' fill='{sun_col}' stroke='{mix('#bfe6ff', '#ffb347', day)}' stroke-width='8'/>")
    # dunas (lejanas, medias, cercanas)
    d1 = mix("#5e3426", "#c8663c", day); d2 = mix("#6e3a28", "#d9773f", day); d3 = mix("#7d4129", "#e8894a", day)
    s.append(f"<path d='M0 1330 Q200 1240 420 1300 T860 1270 T1080 1300 L1080 1920 L0 1920 Z' fill='{d1}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1420 Q260 1340 540 1410 T1080 1390 L1080 1920 L0 1920 Z' fill='{d2}' stroke='{INK}' stroke-width='{LW}'/>")
    s.append(f"<path d='M0 1560 Q300 1480 620 1540 T1080 1520 L1080 1920 L0 1920 Z' fill='{d3}' stroke='{INK}' stroke-width='{LW}'/>")
    for rx, ry, rr in ROCKS:
        s.append(f"<ellipse cx='{rx}' cy='{ry}' rx='{rr}' ry='{rr*0.6:.0f}' fill='{mix('#4a2a20', '#a8502e', day)}' stroke='{INK}' stroke-width='7'/>")
    # huellas del robot
    tr = seg(t, 0, 2.2)
    if tr > 0:
        s.append(f"<path d='M240 1735 L{lerp(240, 530, tr):.0f} 1735' stroke='{mix('#5a2e1e', '#b95a33', day)}' stroke-width='14' stroke-dasharray='22 14'/>")
    s.append(rover(t))
    # polvo flotando
    for px, py, pr, sp in DUST:
        yy = (py - t * sp) % 1100 + 850
        s.append(f"<circle cx='{px + 20*math.sin(t + px):.0f}' cy='{yy:.0f}' r='{pr:.1f}' fill='{mix('#c98f6a', '#ffe0b8', day)}' opacity='0.55'/>")
    # viñeta suave para dar profundidad
    s.append("</g></svg>")
    return "".join(s)

