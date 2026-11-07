# Mundo Curioso 5000 · Shorts de PixVerse

Un Short al día de **10 segundos** en **dibujos animados**: un solo dato curioso y verificado, contado con
imagen y textos grabados, con música. Se genera con PixVerse V6 en OpenArt (360p, 9:16, con audio:
**100 créditos**), se le graban los textos aquí y Make lo publica en YouTube.

## Carpetas

- `pedidos/<id>.json` — `{"url": "https://cdn.openart.ai/…mp4"}`. Al hacer push, la GitHub Action
  `.github/workflows/descargar-openart.yml` descarga el vídeo (las sesiones de Claude no pueden
  descargar de OpenArt) y lo sube como `originales/<id>.mp4`. Tarda unos 30 s.
- `originales/<id>.mp4` — vídeo de PixVerse tal cual (360×640).
- `textos/<id>.json` — los textos y sus tiempos (formato en `poner_textos.py`).
- `videos/` — Shorts de los primeros días. Desde ahora el final se sube a la rama `publicar-pixverse`.
- `publicaciones.md` — `fecha · hora · id · título · tema`.
- `logo.png` — logotipo del canal. `poner_textos.py` lo pone arriba a la izquierda en todos los
  vídeos; si no existe, escribe "MUNDO CURIOSO 5000" en pequeño encima de la etiqueta.
- Los temas usados van en `../curiosidades_usadas.md` (compartido con los vídeos antiguos del canal).

Ids: `AAAA-MM-DD-px` (uno al día).

## Pasos

1. **Tema.** Un dato sorprendente, verificable y que se pueda **contar con imagen** en 10 s, sin
   necesidad de mapas, cifras ni texto dentro del vídeo: animales, cuerpo humano, espacio, naturaleza,
   física cotidiana, inventos, historia. Comprobado con búsquedas; nada que esté ya en
   `curiosidades_usadas.md`.
2. **Guion visual** en 4 momentos: 0–3 s presenta al protagonista (gancho), 3–6 s tensión, 6–8 s la
   acción clave, 8–10 s la revelación (lo más espectacular al final, para que se vea hasta el final).
3. **Vídeo en OpenArt**: `openart_generate_video` con `model: "pixverseV6"`, `mode: "text2video"` y
   `params: {"duration": 10, "aspectRatio": "9:16", "resolution": "360p", "generateAudio": true, "prompt": …}`.
   El prompt, en inglés, empieza siempre con el **estilo del canal**:

   > Vertical 2D cartoon animation, flat vector style, thick bold black outlines, simple clean shapes,
   > vibrant saturated colors, smooth playful animation, educational kids-science cartoon look.

   Después: la escena, el protagonista descrito con **rasgos anatómicos correctos** para que se
   reconozca (un camarón no es una langosta), los 4 momentos con sus segundos, y al final:
   "Audio: playful cartoon background music with a suspenseful build-up …, sound effects at the key
   moment. No text, no subtitles, no voice." Nada de personajes, marcas ni estilos de estudios reales.
4. **Pedido**: guarda `pedidos/<id>.json` con la URL del vídeo, commit y push; espera a que aparezca
   `originales/<id>.mp4` en `origin/main` (git fetch cada 10 s, hasta 5 min).
5. **Analiza**: `python3 pixverse/poner_textos.py analizar pixverse/originales/<id>.mp4` y mira la hoja
   (fotograma cada 0,5 s con su segundo) para ver qué pasa en cada momento y dónde están los cortes.
6. **Textos** en `textos/<id>.json`, sincronizados con lo que se ve: etiqueta `¿LO SABÍAS?`; 4 o 5
   textos de 2–3 líneas cortas (máx. ~20 caracteres por línea), palabra clave entre `*asteriscos*`;
   el primero desde el segundo 0 y de al menos 1,5 s; la cifra o palabra clave final con
   `"estilo": "grande"` y su explicación con `"posicion": "debajo"`. Sin emojis (la fuente no los tiene).
7. **Graba**: `python3 pixverse/poner_textos.py grabar pixverse/originales/<id>.mp4 pixverse/textos/<id>.json pixverse/videos/<id>.mp4`
   y revisa la hoja de revisión: textos legibles, sin cortes ni solapes, a tiempo con la imagen.
8. Graba el resultado en `pixverse/tmp/<id>.mp4` (no en `videos/`: los vídeos finales ya no se
   guardan en main). Commit y push de pedido y textos. Sube el vídeo con
   `python3 herramientas/subir_video.py subir pixverse/tmp/<id>.mp4 <id> publicar-pixverse`, que
   imprime la URL pública.
9. **Publicar** con Make (escenario 8175470, "Mundo Curioso 5000 · Publicar Short") justo después.
