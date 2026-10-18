# Mundo Curioso 5000 · vídeos

Shorts verticales (1080×1920, ~20 s) de curiosidades del mundo para el canal de YouTube Mundo Curioso 5000. Cada vídeo termina invitando a suscribirse.

## Cómo se genera un vídeo

1. Escribe un guion en `guiones/<id>.json` siguiendo `guiones/ejemplo.json` (4 datos, palabras clave entre `*asteriscos*`).
2. Revisa los fotogramas: `python3 generar_video.py guiones/<id>.json --preview`
3. Genera el vídeo: `python3 generar_video.py guiones/<id>.json` → `videos/<id>.mp4`
4. Haz commit y push. El enlace público del vídeo queda en
   `https://raw.githubusercontent.com/javierjane-wq/mundo-curioso-videos/main/videos/<id>.mp4`
5. Metricool (marca 7503466) publica ese enlace en YouTube como Short.

## Reglas de contenido

- Solo datos verificables y vigentes; comprobar cada uno con una búsqueda antes de usarlo.
- Nada repetido: consulta y actualiza `curiosidades_usadas.md`.
- Texto corto: cada línea cabe en pantalla (máx. ~28 caracteres).
- Ids con formato `AAAA-MM-DD-N` (N = 1, 2, 3 para los tres vídeos del día).
