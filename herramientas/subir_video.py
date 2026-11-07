#!/usr/bin/env python3
"""Sube un vídeo a una rama de publicación para que Make lo descargue.

    python3 herramientas/subir_video.py subir <video.mp4> <id> <rama>   -> imprime la URL pública

<rama>: "publicar-codigo" (Shorts por código), "publicar-pixverse" (Short de PixVerse) o "publicar-largo" (vídeo largo semanal).
Cada subida SUSTITUYE (force-push) el contenido de la rama por un único commit sin historia que
solo contiene <id>.mp4: el vídeo anterior queda huérfano y GitHub lo elimina, así que el
repositorio no crece. Por eso hay que lanzar Make justo después de subir (Make lo descarga
enseguida) y no subir otro vídeo a la misma rama hasta que Make haya terminado.
"""
import os, subprocess, sys

REPO = "javierjane-wq/mundo-curioso-videos"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args, entrada=None):
    r = subprocess.run(["git", "-C", RAIZ, *args], input=entrada, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} falló:\n{r.stderr.decode(errors='replace')}")
    return r.stdout.decode().strip()


def subir(video, vid, rama):
    blob = git("hash-object", "-w", video)
    arbol = git("mktree", entrada=f"100644 blob {blob}\t{vid}.mp4\n".encode())
    commit = git("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com",
                 "commit-tree", arbol, "-m", f"Vídeo {vid} (rama temporal para publicar)")
    for intento in range(2):
        r = subprocess.run(["git", "-C", RAIZ, "push", "-f", "origin", f"{commit}:refs/heads/{rama}"],
                           capture_output=True)
        if r.returncode == 0:
            break
    else:
        raise SystemExit(f"push de {rama} falló:\n{r.stderr.decode(errors='replace')}")
    print(f"https://raw.githubusercontent.com/{REPO}/{rama}/{vid}.mp4")


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "subir" and sys.argv[4] in ("publicar-codigo", "publicar-pixverse", "publicar-largo"):
        subir(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__); sys.exit(1)
