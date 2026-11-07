#!/usr/bin/env python3
"""Textos grabados para los Shorts de PixVerse.

  python3 pixverse/poner_textos.py analizar <video.mp4>
      Duración, cortes de plano y una hoja PNG con un fotograma cada 0,5 s
      (con su segundo escrito encima) para decidir cuándo sale cada texto.

  python3 pixverse/poner_textos.py grabar <video.mp4> <textos.json> <salida.mp4>
      Amplía el vídeo a 1080x1920, graba los textos y la barra de progreso,
      conserva el audio y saca una hoja PNG del resultado para revisarlo.

Formato de textos.json:
{
  "etiqueta": "¿LO SABÍAS?",
  "textos": [
    {"inicio": 0,   "fin": 1.6,  "lineas": ["Este animal mide", "*solo 5 cm…*"]},
    {"inicio": 5.2, "fin": 10.1, "lineas": ["*4.700 °C*"], "estilo": "grande"},
    {"inicio": 5.4, "fin": 10.1, "lineas": ["Casi tan caliente", "como el Sol"], "posicion": "debajo"}
  ]
}
- *asteriscos*: palabra en amarillo.
- estilo "grande": cifra enorme en amarillo (una línea corta).
- posicion "debajo": el texto va bajo la cifra grande, si coinciden en el tiempo.
"""
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "tmp")
FUENTE = "Noto Sans CJK SC Black"
LOGO = os.path.join(AQUI, "logo.png")   # logotipo del canal (PNG, mejor con fondo transparente)
LOGO_ANCHO = 170                        # px de ancho sobre el vídeo de 1080

CABECERA = """[Script Info]
ScriptType: v4.00+
PlayResX: 576
PlayResY: 1024
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{f},50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,3,8,30,30,250,1
Style: Big,{f},96,&H0000E1FF,&H0000E1FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,4,8,20,20,230,1
Style: Tag,{f},30,&H00000000,&H00000000,&H0000E1FF,&H0000E1FF,-1,0,0,0,100,100,2,0,3,10,0,8,30,30,90,1
Style: Brand,{f},22,&H26FFFFFF,&H26FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,2,0,1,2,2,8,30,30,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".format(f=FUENTE)

AMARILLO = r"{\c&H00E1FF&}"
BLANCO = r"{\c&HFFFFFF&}"


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def duracion(video):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "default=nw=1:nk=1", video]).stdout
    return float(out.strip())


def cortes(video):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf",
                        "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"],
                       text=True, capture_output=True)
    return [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def hoja(video, salida, paso=0.5, ancho=180, por_fila=7):
    """Hoja de fotogramas cada `paso` segundos con el segundo escrito encima."""
    vf = (f"fps=1/{paso},scale={ancho}:-2,"
          f"drawtext=font='{FUENTE}':text='%{{eif\\:n*{paso}\\:d}}.%{{eif\\:mod(n*{paso}*10\\,10)\\:d}} s':"
          "x=6:y=6:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=4,"
          f"tile={por_fila}x3:padding=4:color=white")
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
        "-vf", vf, "-frames:v", "99", os.path.join(os.path.dirname(salida), "hoja_%02d.png")])
    # Une las páginas en una sola imagen vertical
    paginas = sorted(p for p in os.listdir(os.path.dirname(salida)) if p.startswith("hoja_"))
    entradas = []
    for p in paginas:
        entradas += ["-i", os.path.join(os.path.dirname(salida), p)]
    if len(paginas) == 1:
        os.replace(os.path.join(os.path.dirname(salida), paginas[0]), salida)
    else:
        sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas,
            "-filter_complex", f"vstack={len(paginas)}", salida])
        for p in paginas:
            os.remove(os.path.join(os.path.dirname(salida), p))
    return salida


def ts(seg):
    seg = max(0.0, seg)
    h = int(seg // 3600)
    m = int(seg % 3600 // 60)
    s = seg % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def marcar(linea):
    """*palabra* -> amarillo."""
    partes = linea.split("*")
    return "".join(AMARILLO + p + BLANCO if i % 2 else p for i, p in enumerate(partes))


def construir_ass(textos, dur, con_logo):
    ev = []
    if not con_logo:
        # Sin logo.png: el nombre del canal en pequeño arriba, como en los vídeos antiguos
        ev.append(f"Dialogue: 2,{ts(0)},{ts(dur + 0.05)},Brand,,0,0,0,,MUNDO CURIOSO 5000")
    if textos.get("etiqueta"):
        ev.append(f"Dialogue: 1,{ts(0)},{ts(dur + 0.05)},Tag,,0,0,0,,"
                  + r"{\fad(150,0)}" + textos["etiqueta"])
    for t in textos["textos"]:
        ini, fin = float(t["inicio"]), min(float(t["fin"]), dur + 0.05)
        grande = t.get("estilo") == "grande"
        estilo = "Big" if grande else "Main"
        margen = 385 if t.get("posicion") == "debajo" else 0
        if grande:
            texto = " ".join(t["lineas"]).replace("*", "")
            anim = r"{\fscx160\fscy160\t(0,220,\fscx100\fscy100)}"
        else:
            texto = r"\N".join(marcar(l) for l in t["lineas"])
            anim = (r"{\fad(150,0)}" if margen else
                    r"{\fscx130\fscy130\t(0,180,\fscx100\fscy100)}")
        ev.append(f"Dialogue: 0,{ts(ini)},{ts(fin)},{estilo},,0,0,{margen},,{anim}{texto}")
    return CABECERA + "\n".join(ev) + "\n"


def analizar(video):
    os.makedirs(TMP, exist_ok=True)
    d = duracion(video)
    c = cortes(video)
    base = os.path.splitext(os.path.basename(video))[0]
    h = hoja(video, os.path.join(TMP, f"{base}_analisis.png"))
    print(json.dumps({"duracion": round(d, 2), "cortes_de_plano": c, "hoja": h},
                     ensure_ascii=False, indent=2))


def grabar(video, textos_json, salida):
    os.makedirs(TMP, exist_ok=True)
    textos = json.load(open(textos_json, encoding="utf-8"))
    d = duracion(video)
    base = os.path.splitext(os.path.basename(salida))[0]
    ass = os.path.join(TMP, f"{base}.ass")
    con_logo = os.path.exists(LOGO)
    open(ass, "w", encoding="utf-8").write(construir_ass(textos, d, con_logo))
    tmp = salida[:-4] + ".tmp.mp4"
    base_vf = (f"scale=1080:1920:flags=lanczos,ass={ass},"
               f"drawbox=x=0:y=ih-15:w=iw*t/{d:.2f}:h=15:color=0xFFE100@1:t=fill")
    if con_logo:
        # Logo arriba a la izquierda (zona que no tapan los botones de Shorts)
        entradas = ["-i", video, "-loop", "1", "-i", LOGO]
        filtro = ["-filter_complex",
                  f"[0:v]{base_vf}[v];"
                  f"[1:v]scale={LOGO_ANCHO}:-1,format=rgba,colorchannelmixer=aa=0.92[l];"
                  f"[v][l]overlay=40:60:shortest=1[out]",
                  "-map", "[out]", "-map", "0:a?"]
    else:
        entradas = ["-i", video]
        filtro = ["-vf", base_vf]
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entradas,
        *filtro, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", tmp])
    os.replace(tmp, salida)
    h = hoja(salida, os.path.join(TMP, f"{base}_revision.png"), paso=1.0, ancho=216, por_fila=5)
    print(json.dumps({"video": salida, "duracion": round(duracion(salida), 2),
                      "mb": round(os.path.getsize(salida) / 1e6, 2), "hoja_revision": h},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "analizar":
        analizar(sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == "grabar":
        grabar(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(1)
