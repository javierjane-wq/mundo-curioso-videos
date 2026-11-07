#!/usr/bin/env python3
"""Vídeo largo semanal (1920x1080) con las escenas por código de la semana.

    python3 codigo/compilar_largo.py largo/<semana>.json

largo/<semana>.json:
{
  "id": "2026-11-15-largo",
  "titulo": ["42 curiosidades", "que no te vas a creer"],      # 1-2 líneas para la portada del vídeo
  "subtitulo": "Semana del 8 al 14 de noviembre",
  "segmentos": [
    {"id": "2026-11-08-c1", "resumen": "Los pulpos tienen tres corazones"},
    ...
  ]
}
Cada segmento usa codigo/escenas/<id>.py y codigo/textos/<id>.json.

Salida: codigo/tmp/<id>.mp4 y codigo/tmp/<id>_capitulos.txt (capítulos para la descripción),
más codigo/tmp/<id>_revision.png (un fotograma de la portada, de 4 segmentos y del cierre).
"""
import json, os, subprocess, sys, textwrap, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
TMP = os.path.join(AQUI, "tmp")
sys.path.insert(0, AQUI)
import lib  # noqa: E402

W, H, FPS = 1920, 1080, 30
PAUSA = 1.2                    # segundos de imagen congelada al final de cada curiosidad
FUENTE = "Noto Sans CJK SC Black"
LOGO = os.path.join(RAIZ, "pixverse", "logo.png")
LOGO_GRANDE = os.path.join(RAIZ, "pixverse", "logo_original.png")
NAVY = "0x12233d"
MAX_BYTES = 90_000_000         # GitHub no admite archivos de más de 100 MB
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def sh(cmd):
    subprocess.run(cmd, check=True)


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def archivo_texto(nombre, texto):
    p = os.path.join(TMP, nombre)
    open(p, "w", encoding="utf-8").write(texto)
    return p


def duracion(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", p], capture_output=True, text=True).stdout
    return float(out.strip())


def portada(sal, titulo, subtitulo, dur=6.0):
    t1 = archivo_texto("portada_titulo.txt", "\n".join(titulo))
    t2 = archivo_texto("portada_sub.txt", subtitulo)
    flt = (f"[1:v]scale=560:-1[l];[0:v][l]overlay=170:(H-h)/2[v];"
           f"[v]drawtext=font='{FUENTE}':textfile='{t1}':fontcolor=white:fontsize=92:line_spacing=18:"
           f"x=830:y=330:alpha='min(1,t/0.6)',"
           f"drawtext=font='{FUENTE}':textfile='{t2}':fontcolor=0xF2A93B:fontsize=48:x=834:y=620:"
           f"alpha='min(1,max(0,(t-0.5)/0.6))',fade=t=out:st={dur-0.4}:d=0.4")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
        f"color=c={NAVY}:s={W}x{H}:d={dur}:r={FPS}", "-i", LOGO_GRANDE, "-filter_complex", flt,
        "-t", str(dur), *ENC, "-crf", "24", sal])


def cierre(sal, dur=7.0):
    t1 = archivo_texto("cierre1.txt", "¡SUSCRÍBETE!")
    t2 = archivo_texto("cierre2.txt", "Curiosidades nuevas\ncada día")
    flt = (f"[1:v]scale=480:-1[l];[0:v][l]overlay=220:(H-h)/2[v];"
           f"[v]drawtext=font='{FUENTE}':textfile='{t1}':fontcolor=0xF2A93B:fontsize=110:x=820:y=360:"
           f"alpha='min(1,t/0.5)',"
           f"drawtext=font='{FUENTE}':textfile='{t2}':fontcolor=white:fontsize=64:line_spacing=14:"
           f"x=826:y=540:alpha='min(1,max(0,(t-0.4)/0.5))',fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.6}:d=0.6")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
        f"color=c={NAVY}:s={W}x{H}:d={dur}:r={FPS}", "-i", LOGO_GRANDE, "-filter_complex", flt,
        "-t", str(dur), *ENC, "-crf", "24", sal])


def segmento(n, total, seg, sal):
    """Escena vertical (con sus textos) sobre fondo desenfocado + panel con número y resumen."""
    vid = seg["id"]
    escena = os.path.join(AQUI, "escenas", f"{vid}.py")
    textos = os.path.join(AQUI, "textos", f"{vid}.json")
    lib.render(escena)
    base = os.path.join(TMP, f"{vid}_base.mp4")
    vertical = os.path.join(TMP, f"{vid}_vertical.mp4")
    sh(["python3", os.path.join(RAIZ, "pixverse", "poner_textos.py"), "grabar", base, textos, vertical])
    num = archivo_texto(f"num_{n}.txt", f"CURIOSIDAD {n}")
    res = archivo_texto(f"res_{n}.txt", "\n".join(textwrap.wrap(seg["resumen"], 24)))
    d = duracion(vertical)
    flt = ("[0:v]split=2[a][b];"
           "[a]scale=1920:-2,crop=1920:1080,boxblur=45:3,eq=brightness=-0.25:saturation=1.15[bg];"
           "[b]scale=-2:1080[fg];[bg][fg]overlay=170:0[v2];"
           "[v2]drawbox=x=850:y=250:w=990:h=560:color=black@0.40:t=fill,"
           f"drawtext=font='{FUENTE}':textfile='{num}':fontcolor=0xFFE100:fontsize=58:x=900:y=300:"
           "alpha='min(1,t/0.4)',"
           f"drawtext=font='{FUENTE}':textfile='{res}':fontcolor=white:fontsize=62:line_spacing=16:"
           "x=900:y=400:alpha='min(1,max(0,(t-0.3)/0.5))',"
           f"drawtext=font='{FUENTE}':text='{n} / {total}':fontcolor=white@0.6:fontsize=30:x=900:y=760,"
           f"tpad=stop_mode=clone:stop_duration={PAUSA},fade=t=in:st=0:d=0.25,"
           f"fade=t=out:st={d + PAUSA - 0.3:.2f}:d=0.3")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", vertical,
        "-filter_complex", flt, *ENC, "-crf", "25", sal])
    for p in (base, vertical):
        os.remove(p)
    mod = lib.cargar(escena)
    return duracion(sal), getattr(mod, "REVELACION", 7.5)


def musica_larga(path, dur, cortes, revelaciones, semilla=5):
    """Fondo continuo suave + 'whoosh' en cada cambio + campanas en cada revelación."""
    SR = 44100; n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    r = np.random.default_rng(semilla)
    def add(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[:j - i]
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    paso = 2.4
    for k in range(int(dur / paso) + 1):
        ch = acordes[k % 4]; a = k * paso
        m = (tt >= a) & (tt < a + paso); ss = tt[m] - a
        env = np.minimum(1, ss * 3) * np.exp(-ss * 0.5)
        out[m] += 0.05 * sum(np.sin(2 * np.pi * f * ss) + 0.25 * np.sin(4 * np.pi * f * ss) for f in ch) * env
    beat = 0.6
    kl = int(0.2 * SR); kt = np.arange(kl) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 14) * 0.28
    hl = int(0.04 * SR); hat = lambda: np.diff(r.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 90) * 0.06
    b = 0.0
    while b < dur:
        add(kick, b); add(hat(), b + beat / 2); b += beat
    wl = int(0.4 * SR); wt = np.arange(wl) / SR
    whoosh = np.convolve(r.standard_normal(wl), np.ones(14) / 14, mode="same") * (wt / 0.4) ** 2 * 0.35
    for c in cortes: add(whoosh, c - 0.4)
    for rv in revelaciones:
        for f, dl in ((1046.5, 0), (1318.5, 0.1), (1568.0, 0.2)):
            bl = int(1.2 * SR); bt = np.arange(bl) / SR
            add(np.sin(2 * np.pi * f * bt) * np.exp(-bt * 2.5) * 0.09, rv + dl)
    m = np.tanh(out * 1.4); m /= np.max(np.abs(m)) * 1.15
    fi = int(0.5 * SR); m[:fi] *= np.linspace(0, 1, fi)
    fo = int(2.0 * SR); m[-fo:] *= np.linspace(1, 0, fo)
    pcm = (np.clip(m, -0.98, 0.98) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], axis=1).tobytes())


def mmss(s):
    s = int(s); return f"{s // 60}:{s % 60:02d}"


def main(manifiesto):
    os.makedirs(TMP, exist_ok=True)
    m = json.load(open(manifiesto, encoding="utf-8"))
    vid = m["id"]; segs = m["segmentos"]
    partes, cortes, revel, caps = [], [], [], []
    p0 = os.path.join(TMP, f"{vid}_p000.mp4"); portada(p0, m["titulo"], m.get("subtitulo", ""))
    partes.append(p0); t = duracion(p0); caps.append(("0:00", "Introducción"))
    for n, seg in enumerate(segs, 1):
        print(f"[{n}/{len(segs)}] {seg['id']}", flush=True)
        p = os.path.join(TMP, f"{vid}_p{n:03d}.mp4")
        d, rv = segmento(n, len(segs), seg, p)
        cortes.append(t); revel.append(t + rv); caps.append((mmss(t), f"{n}. {seg['resumen']}"))
        partes.append(p); t += d
    pz = os.path.join(TMP, f"{vid}_p999.mp4"); cierre(pz); partes.append(pz); cortes.append(t)
    caps.append((mmss(t), "Suscríbete")); t += duracion(pz)
    lista = archivo_texto(f"{vid}_lista.txt", "".join(f"file '{p}'\n" for p in partes))
    solo_video = os.path.join(TMP, f"{vid}_video.mp4")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
        "-c", "copy", solo_video])
    wav = os.path.join(TMP, f"{vid}.wav"); musica_larga(wav, duracion(solo_video), cortes, revel)
    final = os.path.join(TMP, f"{vid}.mp4"); tmp = final[:-4] + ".tmp.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", solo_video, "-i", wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", tmp])
    if os.path.getsize(tmp) > MAX_BYTES:   # recomprime si no cabe en GitHub
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "31", "-pix_fmt", "yuv420p", "-c:a", "copy",
            "-movflags", "+faststart", final])
        os.remove(tmp)
    else:
        os.replace(tmp, final)
    for p in partes + [solo_video, wav, lista]:
        os.remove(p)
    capitulos = "\n".join(f"{a} {b}" for a, b in caps)
    open(os.path.join(TMP, f"{vid}_capitulos.txt"), "w", encoding="utf-8").write(capitulos + "\n")
    # hoja de revisión: portada, 4 segmentos repartidos y cierre
    total = duracion(final)
    momentos = [3] + [cortes[i] + 8.5 for i in np.linspace(0, len(segs) - 1, min(4, len(segs))).astype(int)] + [total - 3]
    tiles = []
    for i, s in enumerate(momentos):
        p = os.path.join(TMP, f"rev_{i}.png")
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{s:.2f}", "-i", final,
            "-frames:v", "1", "-vf", "scale=640:-2", p]); tiles.append(p)
    rev = os.path.join(TMP, f"{vid}_revision.png")
    entradas = sum((["-i", p] for p in tiles), [])
    cols = 3; filas = (len(tiles) + cols - 1) // cols
    layout = "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(len(tiles)))
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas, "-filter_complex",
        f"xstack=inputs={len(tiles)}:layout={layout}:fill=white", rev] if len(tiles) > 1 else
       ["cp", tiles[0], rev])
    for p in tiles: os.remove(p)
    print(json.dumps({"video": final, "duracion": mmss(total), "mb": round(os.path.getsize(final) / 1e6, 1),
                      "capitulos": capitulos, "revision": rev}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1])
