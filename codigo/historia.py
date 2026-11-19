#!/usr/bin/env python3
"""Vídeo largo diario "en forma de historia" (1920x1080, ~3 min) dibujado por código.

    python3 codigo/historia.py preview codigo/historias/<id>.py      -> hoja PNG con fotogramas de cada capítulo
    python3 codigo/historia.py render  codigo/historias/<id>.py      -> codigo/tmp/<id>.mp4 (+ _capitulos.txt, _revision.png)

Un episodio (codigo/historias/<id>.py) define:
    ID = "2026-11-19-historia"
    TITULO = "Viaje al fondo del mar"          # para la portada interna y los capítulos
    VOZ = "ef_dora"                            # voz de Kokoro (ef_dora, em_alex, em_santa)
    VELOCIDAD = 1.0                            # ritmo de la narración (más pausado que en los Shorts)
    MUSICA = 7                                 # semilla de la música: cada número da otra canción
    CAPITULOS = [
        {"titulo": "Introducción",              # nombre del capítulo (descripción de YouTube)
         "tarjeta": "CAPÍTULO 1 · 200 METROS",  # opcional: rótulo arriba al empezar el capítulo
         "frases": ["Primera frase narrada.", "Segunda frase…"],
         "grandes": {3: "INVISIBLE"},           # opcional: cifra/palabra en grande mientras suena la frase 3
         "escena": funcion},                    # funcion(t, dur, m) -> cuerpo SVG (sin <svg>) de 1920x1080
        ...]
    m = lista con el segundo (dentro del capítulo) en el que empieza cada frase: sirve para
    sincronizar la animación con la narración. El último capítulo debe ser la despedida con la
    llamada a suscribirse.

El script narra las frases con Kokoro (herramientas/narrar.py), calcula la duración de cada
capítulo a partir de la voz, dibuja todos los fotogramas, añade logo, subtítulos, el botón
"SUSCRÍBETE" fijo arriba a la derecha (late con una campanita cada ~25 s), una música de fondo
suave distinta según MUSICA (baja sola cuando se habla) y transiciones entre capítulos.
"""
import hashlib, importlib.util, json, math, os, re, subprocess, sys, textwrap, wave
from multiprocessing import Pool
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
TMP = os.path.join(AQUI, "tmp")
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))

W, H, FPS = 1920, 1080, 30
FUENTE = "Noto Sans CJK SC Black"
LOGO = os.path.join(RAIZ, "pixverse", "logo.png")
INICIO = 0.7          # silencio antes de la primera frase de cada capítulo
PAUSA = 0.45          # entre frases
COLA = 1.3            # después de la última frase de cada capítulo
SR_VOZ = 24000
SR = 44100
PULSO_SUSC = 25.0     # cada cuántos segundos late el botón de suscribirse
MAX_BYTES = 90_000_000

INK = "#2a1a14"


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def cargar(ruta):
    spec = importlib.util.spec_from_file_location("episodio", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------- narración y tiempos ----------------
def tts(frase, voz, vel):
    os.makedirs(os.path.join(TMP, "voz_cache"), exist_ok=True)
    clave = hashlib.md5(f"{voz}|{vel}|{frase}".encode()).hexdigest()
    p = os.path.join(TMP, "voz_cache", clave + ".npy")
    if os.path.exists(p):
        return np.load(p)
    import narrar
    a = narrar.decir(frase, voz, vel)
    np.save(p, a)
    return a


def linea_tiempo(ep):
    """[(inicio_cap, dur_cap, [inicio_frase_local...], [dur_frase...])], audios, total."""
    caps, audios, t0 = [], [], 0.0
    for c in ep.CAPITULOS:
        m, d, t = [], [], INICIO
        for f in c["frases"]:
            a = tts(f, ep.VOZ, getattr(ep, "VELOCIDAD", 1.0))
            m.append(round(t, 3)); d.append(len(a) / SR_VOZ); audios.append((t0 + t, a))
            t += len(a) / SR_VOZ + PAUSA
        dur = t - PAUSA + COLA + c.get("extra", 0.0)
        caps.append((t0, dur, m, d)); t0 += dur
    return caps, audios, t0


# ---------------- botón de suscripción (SVG) ----------------
def campana(cx, cy, s, ang, color="#fff"):
    return (f"<g transform='translate({cx:.1f},{cy:.1f}) rotate({ang:.1f}) scale({s:.3f})'>"
            f"<path d='M-20 14 Q-20 -18 0 -20 Q20 -18 20 14 L26 20 L-26 20 Z' fill='{color}' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='26' r='6' fill='{color}' stroke='{INK}' stroke-width='4'/>"
            f"<circle cx='0' cy='-23' r='4' fill='{color}' stroke='{INK}' stroke-width='3'/></g>")


def pulsos(ep, caps):
    """Momentos en que late el botón: cuando la narración pide suscribirse ("susc": n.º de frase)
    y, además, cada PULSO_SUSC s (sin acercarse a esos)."""
    fijos = [caps[i][0] + caps[i][2][c["susc"]] for i, c in enumerate(ep.CAPITULOS[:-1]) if "susc" in c]
    t, extra = 8.0, []
    while t < caps[-1][0] - 4:
        if all(abs(t - f) > 10 for f in fijos):
            extra.append(t)
        t += PULSO_SUSC
    return sorted(fijos + extra)


def boton_susc(t, fin, pulsos):
    """Píldora roja fija arriba a la derecha; en cada pulso crece y la campana se balancea.
    Desaparece al empezar la despedida (`fin`), donde manda el botón grande de la escena."""
    if t > fin:
        a = max(0.0, 1 - (t - fin) / 0.5)
        if a <= 0:
            return ""
    else:
        a = min(1.0, t / 0.6)
    fase = min([t - p for p in pulsos if t >= p] or [99])
    k = math.sin(math.pi * fase / 1.6) if fase < 1.6 else 0
    s = 1 + 0.12 * k
    ang = 22 * math.sin(fase * 14) * (1 - fase / 1.6) if fase < 1.6 else 0
    cx, cy = 1720, 78
    return (f"<g opacity='{a:.2f}' transform='translate({cx},{cy}) scale({s:.3f}) translate({-cx},{-cy})'>"
            f"<rect x='1555' y='44' width='330' height='68' rx='34' fill='#e62117' stroke='{INK}' stroke-width='5'/>"
            + campana(1597, 76, 0.85, ang) +
            f"<text x='1633' y='90' font-family=\"{FUENTE}\" font-weight='900' font-size='31' fill='#fff' "
            f"letter-spacing='1'>SUSCRÍBETE</text></g>")


def transicion(t, caps):
    """Burbujas que tapan el corte entre capítulos (0,45 s antes y después)."""
    out = []
    for t0, dur, _, _ in caps[1:]:
        d = t - t0
        if -0.5 < d < 0.5:
            k = 1 - abs(d) / 0.5
            out.append(f"<rect width='{W}' height='{H}' fill='#06243f' opacity='{0.85 * k:.2f}'/>")
            r = np.random.default_rng(int(t0 * 10))
            for _ in range(26):
                x, y0, rr = r.uniform(0, W), r.uniform(0, H), r.uniform(20, 90)
                y = y0 - (d + 0.5) * 900
                out.append(f"<circle cx='{x:.0f}' cy='{y % (H + 200) - 100:.0f}' r='{rr * k:.0f}' fill='#bfe9ff' "
                           f"opacity='{0.55 * k:.2f}' stroke='#fff' stroke-width='3'/>")
    return "".join(out)


# ---------------- fotogramas ----------------
_EP = None
_CAPS = None
_PULSOS = None


def _init(ruta, caps, pulsos_):
    global _EP, _CAPS, _PULSOS
    _EP = cargar(ruta); _CAPS = caps; _PULSOS = pulsos_


def svg_frame(t):
    for i, (t0, dur, m, _) in enumerate(_CAPS):
        if t < t0 + dur or i == len(_CAPS) - 1:
            cuerpo = _EP.CAPITULOS[i]["escena"](max(0.0, t - t0), dur, m)
            break
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
            f"{cuerpo}{transicion(t, _CAPS)}{boton_susc(t, _CAPS[-1][0], _PULSOS)}</svg>")


def _png(t):
    return subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H)], input=svg_frame(t).encode(),
                          capture_output=True, check=True).stdout


# ---------------- subtítulos y rótulos (ASS) ----------------
CABECERA = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,3,2,160,160,48,1
Style: Tag,{FUENTE},40,&H00000000,&H00000000,&H0000E1FF,&H0000E1FF,-1,0,0,0,100,100,2,0,3,14,0,8,40,40,150,1
Style: Big,{FUENTE},150,&H0000E1FF,&H0000E1FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,9,5,8,40,40,215,1
"""


def ts(s):
    s = max(0.0, s)
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def trozos(frase, ancho=46):
    """Divide una frase larga en subtítulos de 1-2 líneas."""
    lineas = textwrap.wrap(frase, ancho)
    return [lineas[i:i + 2] for i in range(0, len(lineas), 2)]


def ass(ep, caps):
    ev = ["[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for c, (t0, dur, m, d) in zip(ep.CAPITULOS, caps):
        if c.get("tarjeta"):
            ev.append(f"Dialogue: 2,{ts(t0 + 0.4)},{ts(t0 + 4.2)},Tag,,0,0,0,,{{\\fad(200,300)}}{c['tarjeta']}")
        for k, (ini, dd) in enumerate(zip(m, d)):
            partes = trozos(c["frases"][k])
            n = sum(len(" ".join(p)) for p in partes)
            t = t0 + ini
            for p in partes:
                fr = len(" ".join(p)) / n * dd
                ev.append(f"Dialogue: 1,{ts(t)},{ts(t + fr + 0.05)},Sub,,0,0,0,,{{\\fad(80,60)}}" + r"\N".join(p))
                t += fr
            if k in c.get("grandes", {}):
                fin = t0 + (m[k + 1] if k + 1 < len(m) else dur - 0.3)
                ev.append(f"Dialogue: 3,{ts(t0 + ini + 0.15)},{ts(fin)},Big,,0,0,0,,"
                          r"{\fscx170\fscy170\t(0,250,\fscx100\fscy100)\fad(0,250)}" + c["grandes"][k])
    return CABECERA + "\n" + "\n".join(ev) + "\n"


# ---------------- música de fondo ----------------
NOTAS = {"C": 0, "D": 2, "Eb": 3, "E": 4, "F": 5, "G": 7, "A": 9, "Bb": 10}
PROGS = [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4], [1, 4, 0, 5], [0, 2, 3, 3], [3, 0, 4, 5], [0, 3, 5, 4]]
ESCALA = [0, 2, 4, 5, 7, 9, 11]


def acorde(raiz, grado):
    return [raiz + ESCALA[(grado + k) % 7] + 12 * ((grado + k) // 7) for k in (0, 2, 4)]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def instrumento(tipo, f, dur, r):
    n = int(dur * SR); t = np.arange(n) / SR
    if tipo == "piano":
        s = sum(np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * (0.6 ** k) * np.exp(-t * (1.6 + k * 0.9))
                for k in range(1, 6))
    elif tipo == "marimba":
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 11)
    elif tipo == "pluck":   # Karplus-Strong
        p = max(2, int(SR / f)); buf = r.uniform(-1, 1, p); s = np.zeros(n)
        for i in range(n):
            s[i] = buf[i % p]; buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    else:                   # "epiano": FM suave
        s = np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 4) * np.sin(2 * np.pi * f * 2 * t)) * np.exp(-t * 1.8)
    ata = min(n, int(0.006 * SR)); s[:ata] *= np.linspace(0, 1, ata)
    return s


def musica(path, dur, semilla, campanas):
    r = np.random.default_rng(semilla)
    raiz = 48 + NOTAS[list(NOTAS)[semilla % len(NOTAS)]]
    prog = PROGS[(semilla // 3) % len(PROGS)]
    tipo = ["piano", "marimba", "epiano", "pluck"][(semilla // 2) % 4]
    bpm = [76, 82, 88, 72, 92, 80][semilla % 6]
    patron = [[0, 1, 2, 1, 0, 2, 1, 2], [0, 2, 1, 2, 0, 2, 1, 0], [0, 1, 2, 3, 2, 1, 0, 1], [0, 2, 3, 2, 1, 2, 3, 1]][semilla % 4]
    negra = 60 / bpm; compas = 4 * negra
    n = int((dur + 3) * SR); out = np.zeros(n)

    def add(sig, at, g):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += g * sig[:j - i]

    cache = {}
    def nota(f, d, g, at):
        k = (round(f, 2), round(d, 2))
        if k not in cache: cache[k] = instrumento(tipo, f, d, r)
        add(cache[k], at, g)

    tt_pad = np.arange(int(compas * SR)) / SR
    env_pad = np.minimum(1, tt_pad / 1.2) * np.minimum(1, (compas - tt_pad) / 0.8)
    c = 0
    while c * compas < dur + 1:
        a = c * compas
        notas = acorde(raiz, prog[c % 4])
        # colchón (pad) suave
        pad = sum(np.sin(2 * np.pi * hz(x + 12) * tt_pad) + 0.3 * np.sin(2 * np.pi * hz(x + 24) * tt_pad * 1.003) for x in notas)
        add(pad * env_pad, a, 0.022)
        # bajo
        for b in (0, 2):
            bl = int(negra * 1.8 * SR); bt = np.arange(bl) / SR
            add(np.sin(2 * np.pi * hz(notas[0] - 12) * bt) * np.exp(-bt * 1.4) * np.minimum(1, bt * 60), a + b * negra, 0.16)
        # arpegio (desde el compás 2), con alguna nota de adorno
        if c >= 2:
            tonos = notas + [notas[0] + 12]
            for i, idx in enumerate(patron):
                if r.random() < 0.12: continue
                nota(hz(tonos[idx % len(tonos)] + 12), negra * 1.6, 0.075, a + i * negra / 2)
        # percusión muy suave (escobillas) desde el compás 4
        if c >= 4:
            for i in range(8):
                hl = int(0.05 * SR)
                ruido = np.diff(r.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 70)
                add(ruido, a + i * negra / 2, 0.018 if i % 2 else 0.03)
        c += 1
    for at in campanas:      # campanita del botón de suscribirse
        for f, dl in ((1568.0, 0), (2093.0, 0.09)):
            bl = int(1.0 * SR); bt = np.arange(bl) / SR
            add(np.sin(2 * np.pi * f * bt) * np.exp(-bt * 4), at + dl, 0.05)
    # reverberación (respuesta de ruido que decae)
    irl = int(1.8 * SR); ir = r.standard_normal(irl) * np.exp(-np.arange(irl) / SR * 3.2)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = 1 << int(np.ceil(np.log2(n + irl)))
    wet = np.fft.irfft(np.fft.rfft(out, L) * np.fft.rfft(ir, L), L)[:n]
    m = out + 0.35 * wet
    m = m[: int(dur * SR)]
    m /= np.max(np.abs(m)) * 1.05
    fi = int(1.5 * SR); m[:fi] *= np.linspace(0, 1, fi)
    fo = int(3.0 * SR); m[-fo:] *= np.linspace(1, 0, fo)
    pcm = (np.clip(m, -0.98, 0.98) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], axis=1).tobytes())
    return {"tonalidad": list(NOTAS)[semilla % len(NOTAS)], "bpm": bpm, "instrumento": tipo}


def pista_voz(path, audios, total):
    pista = np.zeros(int(total * SR_VOZ) + SR_VOZ, dtype=np.float32)
    for t, a in audios:
        i = int(t * SR_VOZ); pista[i:i + len(a)] += a[: len(pista) - i]
    pista *= 0.89 / max(1e-6, np.abs(pista).max())
    import soundfile as sf
    sf.write(path, pista[: int(total * SR_VOZ)], SR_VOZ)


def mmss(s):
    s = int(s); return f"{s // 60}:{s % 60:02d}"


# ---------------- comandos ----------------
def preview(ruta):
    ep = cargar(ruta); caps, _, total = linea_tiempo(ep)
    _init(ruta, caps, pulsos(ep, caps))
    tiempos = []
    for t0, dur, m, _ in caps:
        tiempos += [t0 + 0.2, t0 + dur * 0.5, t0 + m[-1] + 0.6]
    pngs = []
    for i, t in enumerate(tiempos):
        p = os.path.join(TMP, f"prev_{i:02d}.png"); open(p, "wb").write(_png(t)); pngs.append(p)
    sal = os.path.join(TMP, f"{ep.ID}_preview.png")
    entradas = sum((["-i", p] for p in pngs), [])
    flt = ";".join(f"[{i}]scale=480:-2,drawtext=font='{FUENTE}':text='{t:.1f} s':x=6:y=6:fontsize=22:"
                   f"fontcolor=white:box=1:boxcolor=black@0.7[v{i}]" for i, t in enumerate(tiempos))
    flt += ";" + "".join(f"[v{i}]" for i in range(len(pngs))) + \
           f"xstack=inputs={len(pngs)}:layout=" + "|".join(f"{(i % 3) * 480}_{(i // 3) * 270}" for i in range(len(pngs)))
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas, "-filter_complex", flt, sal])
    for p in pngs: os.remove(p)
    print(json.dumps({"preview": sal, "duracion": mmss(total),
                      "capitulos": [(mmss(c[0]), round(c[1], 1)) for c in caps]}, ensure_ascii=False))


def render(ruta):
    os.makedirs(TMP, exist_ok=True)
    ep = cargar(ruta); caps, audios, total = linea_tiempo(ep)
    vid = ep.ID
    wav_voz = os.path.join(TMP, f"{vid}_voz.wav"); pista_voz(wav_voz, audios, total)
    campanas = pulsos(ep, caps)
    wav_mus = os.path.join(TMP, f"{vid}_musica.wav"); info_mus = musica(wav_mus, total, ep.MUSICA, campanas)
    fass = os.path.join(TMP, f"{vid}.ass"); open(fass, "w", encoding="utf-8").write(ass(ep, caps))
    n = int(round(total * FPS))
    solo = os.path.join(TMP, f"{vid}_video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "image2pipe",
                           "-framerate", str(FPS), "-c:v", "png", "-i", "-", "-loop", "1", "-i", LOGO,
                           "-filter_complex", f"[0:v]ass={fass}[v];[1:v]scale=190:-1,format=rgba,"
                           f"colorchannelmixer=aa=0.92[l];[v][l]overlay=40:34:shortest=1[o]",
                           "-map", "[o]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                           "-pix_fmt", "yuv420p", "-r", str(FPS), solo], stdin=subprocess.PIPE)
    with Pool(max(1, os.cpu_count() or 1), initializer=_init, initargs=(ruta, caps, campanas)) as pool:
        for i, png in enumerate(pool.imap(_png, [k / FPS for k in range(n)], chunksize=6)):
            ff.stdin.write(png)
            if i % 600 == 0: print(f"fotograma {i}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    if ff.returncode: raise SystemExit("ffmpeg falló al codificar el vídeo")
    final = os.path.join(TMP, f"{vid}.mp4")
    audio_fc = ("[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit[v1][v2];"
                "[2:a]aresample=48000,volume=0.28[mus];"
                "[mus][v1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[duck];"
                "[duck][v2]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,"
                "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", solo, "-i", wav_voz, "-i", wav_mus,
        "-filter_complex", audio_fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-shortest", "-movflags", "+faststart", final])
    if os.path.getsize(final) > MAX_BYTES:
        tmp = final[:-4] + ".tmp.mp4"
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", final, "-c:v", "libx264", "-preset",
            "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", tmp])
        os.replace(tmp, final)
    for p in (solo, wav_voz, wav_mus): os.remove(p)
    capitulos = "\n".join(f"{mmss(t0)} {c['titulo']}" for c, (t0, *_r) in zip(ep.CAPITULOS, caps))
    open(os.path.join(TMP, f"{vid}_capitulos.txt"), "w", encoding="utf-8").write(capitulos + "\n")
    # hoja de revisión: 2 fotogramas por capítulo
    tiles = []
    for i, (t0, dur, m, _) in enumerate(caps):
        for j, t in enumerate((t0 + m[0] + 1.0, t0 + m[-1] + 1.0)):
            p = os.path.join(TMP, f"rev_{i}_{j}.png")
            sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", final,
                "-frames:v", "1", "-vf", "scale=640:-2", p]); tiles.append(p)
    rev = os.path.join(TMP, f"{vid}_revision.png")
    entradas = sum((["-i", p] for p in tiles), [])
    layout = "|".join(f"{(i % 4) * 640}_{(i // 4) * 360}" for i in range(len(tiles)))
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas, "-filter_complex",
        f"xstack=inputs={len(tiles)}:layout={layout}:fill=white", rev])
    for p in tiles: os.remove(p)
    print(json.dumps({"video": final, "duracion": mmss(total), "segundos": round(total, 1),
                      "mb": round(os.path.getsize(final) / 1e6, 1), "musica": info_mus,
                      "capitulos": capitulos, "revision": rev}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("preview", "render"):
        (preview if sys.argv[1] == "preview" else render)(sys.argv[2])
    else:
        print(__doc__); sys.exit(1)
