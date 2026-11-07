# Mundo Curioso 5000 · Shorts dibujados por código

Seis Shorts al día de **10 segundos**, cada uno con **un solo dato curioso** contado con una escena de
dibujos animados que Claude dibuja y anima con código (SVG fotograma a fotograma). 1080×1920, 30 fps,
con música generada, textos grabados, logo del canal y barra de progreso. Sin créditos de OpenArt.

## Archivos

- `lib.py` — utilidades (`seg`, `lerp`, `mix`, `rebote`, `pulso`, `zoom`, `svg`, colores `INK`/`LW`),
  música y render. Ver su cabecera.
- `escenas/ejemplo_marte.py` — **escena de ejemplo**: léela entera antes de escribir una nueva.
- `escenas/<id>.py` — la escena de cada vídeo.
- `textos/<id>.json` — textos y tiempos (formato en `../pixverse/poner_textos.py`).
- `publicaciones.md` — `fecha · hora · id · título · tema`.
- Temas usados: `../curiosidades_usadas.md` (compartido con todo el canal).
- Los vídeos NO se guardan en main: se suben a la rama `publicar-codigo` con `../herramientas/subir_video.py`,
  que sustituye el vídeo anterior en cada subida (así el repositorio no crece).

Ids: `AAAA-MM-DD-cN` (N = 1…6 en el día).

## Cómo contar el dato en 10 s

Un único dato sorprendente y verificable que se entienda **con imagen**: un protagonista claro
(animal, planeta, órgano, objeto, edificio…) y un cambio visible que lo explique. Estructura:

| Segundos | Imagen | Texto |
|---|---|---|
| 0–2,5 | El protagonista ya está en pantalla desde el fotograma 0, entrando o haciendo algo | Gancho: qué es |
| 2,5–5 | Se muestra la situación normal | Contexto |
| 5–7,5 | Tensión: algo empieza a cambiar | "…pero…" |
| 7,5–10 | **Revelación** (`REVELACION`): gran cambio de luz/color/tamaño, zoom de cámara | Cifra o palabra clave en grande + explicación |

## Estilo (igual que los vídeos de PixVerse del canal)

- **2D plano con contornos gruesos**: `stroke=INK`, `stroke-width=LW` (o 5–7 en detalles). Colores
  planos y vivos; degradados solo para cielos, luces y halos. Fondo completo (cielo/mar/espacio/
  interior + suelo), nunca un objeto suelto sobre un color.
- **Composición**: el protagonista y la acción en la **mitad de abajo** (y > 1000). Arriba
  (y < 1000) solo cielo o fondo tranquilo: ahí van el logo (arriba a la izquierda), la etiqueta
  y los textos.
- **Personajes originales** con encanto: ojos grandes que parpadean si el motivo puede tener cara.
  Anatomía y forma **correctas** para que se reconozca qué es. Nada de personajes, marcas ni
  diseños reconocibles de películas o estudios (ni parecidos).
- **Movimiento constante**: entrada del protagonista, 2–4 movimientos secundarios (parpadeo,
  balanceo, partículas, nubes, burbujas) y un cambio grande en la revelación (con `zoom`).
- Nada de texto dentro del dibujo: los textos los pone `poner_textos.py`.

## Pasos

1. Escribe `escenas/<id>.py` copiando la estructura del ejemplo (`DUR = 10.0`, `REVELACION`,
   `MUSICA` = un número del 1 al 9, `frame(t)` que devuelve el SVG).
2. Revisa el dibujo: `python3 codigo/lib.py preview codigo/escenas/<id>.py 0 2.5 5 7.6 9.5` y mira
   el PNG con Read. Corrige hasta que se reconozca y quede bonito (máximo 3 vueltas).
3. Render: `python3 codigo/lib.py render codigo/escenas/<id>.py` → `codigo/tmp/<id>_base.mp4` (~30–60 s).
4. Textos en `textos/<id>.json` (mismo formato y reglas que `../pixverse/README.md`).
5. Graba: `python3 pixverse/poner_textos.py grabar codigo/tmp/<id>_base.mp4 codigo/textos/<id>.json codigo/tmp/<id>.mp4`
   y revisa la hoja que imprime.
6. Commit y push de la escena y los textos (no del vídeo).
7. Sube el vídeo: `python3 herramientas/subir_video.py subir codigo/tmp/<id>.mp4 <id> publicar-codigo` → imprime la URL.
8. Publica con Make (escenario 8175470) usando esa URL, justo después de subirlo.
