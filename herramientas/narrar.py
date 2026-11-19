#!/usr/bin/env python3
"""Narración con voz de IA (Kokoro, modelo libre que corre en local) para los Shorts.

  python3 herramientas/narrar.py prueba "Hola, esto es una prueba" [voz] [salida.wav]
      Genera un audio suelto para escuchar una voz.

Desde poner_textos.py (opción --voz) se llama a `pista(textos, dur, cierre)`, que devuelve un WAV
de toda la duración del vídeo con cada frase colocada en su sitio.

Frases: cada texto de textos.json puede llevar "voz": "frase que se dice". La frase empieza en
el "inicio" de ese texto (o justo al terminar la anterior, si aún se está hablando). Toda la
narración debe terminar antes del cierre "¡SÍGUEME!" (dur - 1,8 s): si no cabe, se acelera hasta
x1,25 y, si aun así no cabe, se avisa con un error (hay que acortar las frases).
Con cierre, en los últimos 1,8 s se dice VOZ_CIERRE.

La primera vez instala kokoro-onnx y descarga el modelo (~350 MB, desde GitHub) en
~/.cache/kokoro; las siguientes usa lo descargado.
"""
import os
import subprocess
import sys
import urllib.request

import numpy as np

VOZ = "em_alex"            # voz del canal: em_alex (hombre), ef_dora (mujer), em_santa (hombre grave)
VELOCIDAD = 1.1            # ritmo base, algo ágil para Shorts
VELOCIDAD_MAX = 1.25       # más rápido ya no se entiende bien
VOZ_CIERRE = "¡Sígueme para más!"
SR = 24000
CIERRE_DUR = 1.8
MARGEN = 0.12              # pausa mínima entre frases (s)

CACHE = os.path.expanduser("~/.cache/kokoro")
BASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
ARCHIVOS = {"kokoro-v1.0.onnx": 300_000_000, "voices-v1.0.bin": 25_000_000}

_tts = None


def _preparar():
    global _tts
    if _tts is not None:
        return _tts
    try:
        from kokoro_onnx import Kokoro  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages",
                        "kokoro-onnx", "soundfile"], check=True)
    from kokoro_onnx import Kokoro
    os.makedirs(CACHE, exist_ok=True)
    for nombre, minimo in ARCHIVOS.items():
        ruta = os.path.join(CACHE, nombre)
        if not os.path.exists(ruta) or os.path.getsize(ruta) < minimo:
            print(f"Descargando {nombre}…", file=sys.stderr)
            tmp = ruta + ".part"
            urllib.request.urlretrieve(BASE_URL + nombre, tmp)
            if os.path.getsize(tmp) < minimo:
                raise RuntimeError(f"Descarga incompleta de {nombre}")
            os.replace(tmp, ruta)
    _tts = Kokoro(os.path.join(CACHE, "kokoro-v1.0.onnx"), os.path.join(CACHE, "voices-v1.0.bin"))
    return _tts


def decir(frase, voz=VOZ, velocidad=VELOCIDAD):
    """Audio float32 a 24 kHz, sin silencios al principio ni al final."""
    audio, sr = _preparar().create(frase, voice=voz, speed=velocidad, lang="es")
    assert sr == SR
    audio = np.asarray(audio, dtype=np.float32)
    voz_on = np.where(np.abs(audio) > 0.01)[0]
    if len(voz_on):
        audio = audio[max(0, voz_on[0] - 240): voz_on[-1] + 1200]
    return audio


def _colocar(frases, velocidad, voz):
    """[(inicio, audio)] respetando el orden y sin solaparse."""
    puestos, libre = [], 0.0
    for inicio, frase in frases:
        a = decir(frase, voz, velocidad)
        t = max(inicio, libre)
        puestos.append((t, a))
        libre = t + len(a) / SR + MARGEN
    return puestos, libre - MARGEN


def pista(textos, dur, cierre=False, voz=None):
    """Devuelve (audio float32 de `dur` s, info) con la narración colocada."""
    voz = voz or textos.get("voz_ia") or VOZ
    frases = [(float(t["inicio"]), t["voz"].strip()) for t in textos["textos"] if t.get("voz", "").strip()]
    if not frases:
        raise ValueError("Ningún texto lleva \"voz\": no hay nada que narrar")
    limite = dur - CIERRE_DUR - 0.1 if cierre else dur - 0.15
    vel = VELOCIDAD
    puestos, fin = _colocar(frases, vel, voz)
    while fin > limite and vel < VELOCIDAD_MAX:
        vel = min(VELOCIDAD_MAX, round(vel + 0.05, 2))
        puestos, fin = _colocar(frases, vel, voz)
    if fin > limite:
        raise ValueError(f"La narración dura hasta {fin:.1f} s y debe acabar antes de {limite:.1f} s: "
                         "acorta las frases de \"voz\"")
    if cierre:
        a = decir(VOZ_CIERRE, voz, 1.15)
        t = dur - CIERRE_DUR + 0.15
        if t + len(a) / SR <= dur:
            puestos.append((t, a))
    pista = np.zeros(int(dur * SR) + SR, dtype=np.float32)
    for t, a in puestos:
        i = int(t * SR)
        pista[i:i + len(a)] += a[: len(pista) - i]
    pico = np.abs(pista).max()
    if pico > 0:
        pista *= 0.89 / pico
    return pista[: int(dur * SR)], {"voz": voz, "velocidad": vel, "fin_narracion": round(fin, 2),
                                    "frases": len(frases)}


def guardar_wav(audio, ruta):
    import soundfile as sf
    sf.write(ruta, audio, SR)
    return ruta


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "prueba":
        voz = sys.argv[3] if len(sys.argv) > 3 else VOZ
        salida = sys.argv[4] if len(sys.argv) > 4 else "prueba_voz.wav"
        print(guardar_wav(decir(sys.argv[2], voz), salida))
    else:
        print(__doc__)
        sys.exit(1)
