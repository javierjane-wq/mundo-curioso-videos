#!/usr/bin/env python3
"""Kit para los Shorts de Mundo Curioso 5000 dibujados por código (1080x1920, 30 fps).

Una escena es un archivo .py (ver codigo/escenas/ejemplo_marte.py) que define:
    DUR = 10.0          # segundos
    REVELACION = 7.5    # segundo de la revelación final: golpe musical + campanas
    MUSICA = 3          # semilla: cambia acordes y ritmo
    def frame(t): ...   # devuelve el SVG (texto) del fotograma en el segundo t

Uso:
    python3 codigo/lib.py preview codigo/escenas/<id>.py 0.5 3 6 8 9.5
        -> codigo/tmp/<id>_preview.png (esos fotogramas en fila) para revisar el dibujo
    python3 codigo/lib.py render codigo/escenas/<id>.py
        -> codigo/tmp/<id>_base.mp4 (vídeo con música, sin textos)
Después: pixverse/poner_textos.py grabar … pone textos, logo y barra de progreso.
"""
import importlib.util, math, os, subprocess, sys, wave
from multiprocessing import Pool
import numpy as np

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "tmp")
INK = "#2a1a14"   # color del contorno (estilo del canal: contornos gruesos)
LW = 9            # grosor del contorno

# ---------- utilidades de animación ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def seg(t, a, b):
    """0 antes de a, 1 después de b, suave entre medias."""
    return ease((t - a) / (b - a)) if b > a else float(t >= a)
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k):
    """Mezcla dos colores '#rrggbb' (k=0 -> c1, k=1 -> c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(round(lerp(x, y, clamp(k)))) for x, y in zip(a, b))
def pulso(t, periodo=1.0, fase=0.0): return math.sin(2 * math.pi * (t + fase) / periodo)
def rebote(t, a, dur=0.5):
    """Escala con rebote al aparecer en el segundo a (0 -> 1.12 -> 1)."""
    k = clamp((t - a) / dur)
    return 0 if t < a else (1 + 0.12 * math.sin(math.pi * k)) * ease(k * 1.6)

def svg(cuerpo, defs=""):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"<defs>{defs}</defs>{cuerpo}</svg>")

def zoom(cx, cy, z, contenido):
    """Acerca la cámara (z>1) hacia el punto cx,cy."""
    return f"<g transform='translate({cx:.1f},{cy:.1f}) scale({z:.4f}) translate({-cx:.1f},{-cy:.1f})'>{contenido}</g>"

# ---------- música ----------
def musica(path, dur, revelacion, semilla=1):
    """Pulso que se acelera, acordes suaves, subida antes de la revelación, golpe + campanas y colchón final."""
    SR = 44100; n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    r = np.random.default_rng(semilla)
    def add(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[:j - i]
    beat, k = 0.5, 0.0
    while k < revelacion - 0.1:
        kl = int(0.25 * SR); kt = np.arange(kl) / SR
        add(np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 12) * 0.55, k)
        hl = int(0.05 * SR); add(np.diff(r.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 80) * 0.12, k + beat / 2)
        k += beat; beat = max(0.28, beat * 0.965)
    progs = [[(220.0, 261.63, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (164.81, 207.65, 246.94)],
             [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)],
             [(196.0, 246.94, 293.66), (164.81, 196.0, 246.94), (130.81, 164.81, 196.0), (146.83, 185.0, 220.0)]]
    acordes = progs[semilla % len(progs)]; largo = revelacion / 4
    for i, ch in enumerate(acordes):
        a, b = i * largo, (i + 1) * largo
        m = (tt >= a) & (tt < b); ss = tt[m] - a
        env = np.minimum(1, ss * 4) * np.exp(-ss * 0.6)
        out[m] += 0.06 * sum(np.sin(2 * np.pi * f * ss) + 0.3 * np.sin(4 * np.pi * f * ss) for f in ch) * env
    rl = int(1.2 * SR); rt = np.arange(rl) / SR
    add(np.sin(2 * np.pi * np.cumsum(300 + 900 * (rt / 1.2) ** 2) / SR) * (rt / 1.2) ** 2 * 0.18, revelacion - 1.2)
    il = int(1.2 * SR); it = np.arange(il) / SR
    add(np.sin(2 * np.pi * (38 + 70 * np.exp(-it * 14)) * it) * np.exp(-it * 4) * 0.9, revelacion)
    for f, dl in ((1046.5, 0), (1318.5, 0.12), (1568.0, 0.24), (2093.0, 0.36)):
        bl = int(1.6 * SR); bt = np.arange(bl) / SR
        add(np.sin(2 * np.pi * f * bt) * np.exp(-bt * 2.2) * 0.12, revelacion + 0.05 + dl)
    pad = tt >= revelacion; ps = tt[pad] - revelacion
    out[pad] += 0.07 * sum(np.sin(2 * np.pi * f * ps) for f in (261.63, 329.63, 392.0, 493.88)) * np.minimum(1, ps * 2)
    m = np.tanh(out * 1.3); m /= np.max(np.abs(m)) * 1.1
    fo = int(0.5 * SR); m[-fo:] *= np.linspace(1, 0, fo)
    pcm = (np.clip(m, -0.98, 0.98) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], axis=1).tobytes())

# ---------- render ----------
_ESC = None

def cargar(ruta):
    spec = importlib.util.spec_from_file_location("escena", ruta)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for nombre in ("DUR", "frame"):
        if not hasattr(mod, nombre): raise SystemExit(f"La escena debe definir {nombre}")
    return mod

def _pintar(args):
    t, destino = args
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-o", destino],
                   input=_ESC.frame(t).encode(), check=True)

def _init(ruta):
    global _ESC
    sys.path.insert(0, AQUI)
    _ESC = cargar(ruta)

def preview(ruta, tiempos):
    os.makedirs(TMP, exist_ok=True)
    base = os.path.splitext(os.path.basename(ruta))[0]
    pngs = [os.path.join(TMP, f"{base}_p{i}.png") for i in range(len(tiempos))]
    _init(ruta)
    for t, p in zip(tiempos, pngs): _pintar((t, p))
    entradas = sum((["-i", p] for p in pngs), [])
    partes = [f"[{i}]scale=300:-1,drawtext=font='Noto Sans CJK SC Black':text='{t:g} s':x=8:y=8:"
              f"fontsize=26:fontcolor=white:box=1:boxcolor=black@0.7[v{i}]" for i, t in enumerate(tiempos)]
    une = "".join(f"[v{i}]" for i in range(len(tiempos))) + (f"hstack={len(tiempos)}" if len(tiempos) > 1 else "null")
    flt = ";".join(partes) + ";" + une
    salida = os.path.join(TMP, f"{base}_preview.png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas, "-filter_complex", flt, salida], check=True)
    for p in pngs: os.remove(p)
    print(salida)

def render(ruta):
    os.makedirs(TMP, exist_ok=True)
    base = os.path.splitext(os.path.basename(ruta))[0]
    carpeta = os.path.join(TMP, f"{base}_frames"); os.makedirs(carpeta, exist_ok=True)
    esc = cargar(ruta)
    n = int(round(esc.DUR * FPS))
    trabajos = [(i / FPS, os.path.join(carpeta, f"f_{i:04d}.png")) for i in range(n)]
    with Pool(max(1, os.cpu_count() or 1), initializer=_init, initargs=(ruta,)) as pool:
        pool.map(_pintar, trabajos, chunksize=4)
    wav = os.path.join(TMP, f"{base}.wav")
    musica(wav, esc.DUR, getattr(esc, "REVELACION", esc.DUR * 0.75), getattr(esc, "MUSICA", 1))
    salida = os.path.join(TMP, f"{base}_base.mp4"); tmp = salida[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(carpeta, "f_%04d.png"), "-i", wav, "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", tmp], check=True)
    os.replace(tmp, salida)
    for f in os.listdir(carpeta): os.remove(os.path.join(carpeta, f))
    os.rmdir(carpeta); os.remove(wav)
    print(salida)

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "preview":
        preview(sys.argv[2], [float(x) for x in sys.argv[3:]])
    elif len(sys.argv) == 3 and sys.argv[1] == "render":
        render(sys.argv[2])
    else:
        print(__doc__); sys.exit(1)
