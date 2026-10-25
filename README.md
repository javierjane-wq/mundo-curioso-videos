# Mundo Curioso 5000 · vídeos

Shorts verticales (1080×1920, unos 36 s) de curiosidades del mundo para el canal de YouTube Mundo Curioso 5000. Cada vídeo tiene **3 curiosidades**. Cada una lleva un **dibujo animado** propio del tema y un **gráfico animado** que la explica. El vídeo termina con la voz grabada del canal (`voz/outro.wav`, con la música bajando mientras se habla) invitando a suscribirse. No borres ni cambies los audios de `voz/`. `voz/intro.wav` anuncia "4 curiosidades", así que solo suena en los guiones antiguos de 4 datos.

## Cómo se genera un vídeo

1. Escribe un guion en `guiones/<id>.json` siguiendo `guiones/ejemplo.json`: 3 datos, palabras clave entre `*asteriscos*`, cada dato con `dibujo` y `grafico`.
2. Revisa los fotogramas: `python3 generar_video.py guiones/<id>.json --preview`. Saca una hoja PNG con el gancho, la parte del dibujo y la del gráfico de cada curiosidad, y el cierre.
3. Genera el vídeo: `python3 generar_video.py guiones/<id>.json` → `videos/<id>.mp4`.
4. Haz commit y push. El enlace público del vídeo queda en
   `https://raw.githubusercontent.com/javierjane-wq/mundo-curioso-videos/main/videos/<id>.mp4`
5. El escenario de Make "Mundo Curioso 5000 · Publicar Short" (id 8175470) descarga ese enlace y lo programa en YouTube.

Solo necesita Python con Pillow y numpy, y ffmpeg. Los dibujos los interpreta `dibujos.py`, sin librerías externas. Generar un vídeo tarda unos 2 minutos.

## Formato de cada dato

```json
{
  "grande": "10.210 m",
  "contar": [0, 10210, "{} m"],
  "lineas": ["mide el volcán *Mauna Kea*", "desde su base en el", "*fondo del mar* (Hawái)"],
  "dibujo": "<svg viewBox='0 0 400 400'>…</svg>",
  "grafico": { "tipo": "barras", … }
}
```

- `grande`: número o palabra muy corta. `contar` (opcional) hace que una cifra entera cuente hacia arriba.
- `lineas`: 2 o 3 líneas de unos 28 caracteres como máximo.
- Escena: unos 4,6 s de dibujo con el dato y después unos 4,4 s de gráfico.

### Dibujo (`dibujo`)

Un SVG dentro del JSON (usa comillas simples dentro del SVG). Lo interpreta `dibujos.py`. Estilo: **ilustración vectorial moderna**, como las de una buena app o un canal de divulgación, no un dibujo infantil. Mira los tres de `guiones/ejemplo.json` antes de dibujar.

**Composición**
- `viewBox='0 0 400 400'`. Toda la escena va dentro de un círculo: define `<clipPath id='c'><circle cx='200' cy='200' r='180'/></clipPath>`, mete la escena en `<g clip-path='url(#c)'>…</g>` y cierra con un aro blanco: `<circle cx='200' cy='200' r='180' fill='none' stroke='#ffffff' stroke-width='10'/>`.
- Una escena completa, no un objeto suelto: fondo (cielo, mar, espacio, interior…), un motivo principal grande que se reconozca a primera vista y 2 o 3 detalles de apoyo (nubes, sol, burbujas, estrellas, plantas…).

**Volumen y luz**
- Sin contornos negros. El volumen sale del color: cada forma importante con `linearGradient` o `radialGradient` (de claro a oscuro, con la luz arriba a la izquierda).
- Sombra propia: una forma más oscura (`opacity` 0.2–0.35) en el lado derecho o abajo, recortada a la figura con su propio `clipPath`.
- Brillos: trazos o manchas blancas con `opacity` 0.6–0.85 en el lado de la luz. Rayos de luz o halos con degradados que van a transparente (`stop-opacity='0'`).
- Paleta armónica de 5 a 8 tonos. Fondos más claros y suaves que el motivo para que este destaque.
- Las caritas (ojos con brillo, mejillas rosas y sonrisa) solo cuando el motivo es un personaje u objeto simpático (una gota, un planeta, un animal). En paisajes, edificios y objetos, nada de caras.

**Partes animadas** (un `<g>` con `data-anim`; dale vida a 2–4 partes por dibujo)
- `flotar` (sube y baja: nubes, olas, burbujas), `balancear` (oscila: peces, banderas, objetos colgados), `girar` (planetas, ruedas, hélices), `latir` (corazones, estrellas grandes), `parpadear` (los ojos de un personaje: un grupo con los dos ojos) y `brillar` (destellos, soles, halos).
- Opciones: `data-origen='x y'` (punto de giro o escala; por defecto, el centro de la parte), `data-periodo` (segundos por ciclo), `data-amplitud` (píxeles del viewBox en flotar, grados en balancear, % en latir) y `data-fase` (segundos de desfase entre partes parecidas).
- No metas un grupo animado dentro de otro.

**Técnica**
- Elementos: `circle`, `ellipse`, `rect` (con `rx`), `line`, `polyline`, `polygon`, `path` (M L H V C S Q T A Z), `g` con `transform`, `defs`, `linearGradient`, `radialGradient` y `clipPath`. Un `path` con varias subrutas hace huecos (regla par-impar).
- Sin texto, sin imágenes, sin filtros ni máscaras. Nada de personajes, logotipos ni marcas reales.
- El generador añade un halo de luz detrás, una sombra suave, la entrada animada y un ligero balanceo de todo el dibujo.

### Gráfico (`grafico`)

Elige el que mejor explique el dato. Todos admiten `titulo` (línea corta con `*asteriscos*`) y `nota` (etiqueta final corta, por ejemplo "229 años de diferencia"; no la uses con `porcentaje`).

- **barras**: para comparar de 2 a 4 cantidades.
  `{"tipo": "barras", "titulo": "¿Cuál es *más alto*?", "unidad": "m", "items": [{"etiqueta": "Everest", "valor": 8849}, {"etiqueta": "Mauna Kea", "valor": 10210, "destacar": true}], "nota": "…"}`
- **porcentaje**: para un dato en %.
  `{"tipo": "porcentaje", "titulo": "Toda el agua del planeta", "valor": 2.5, "etiqueta": "solo esto es agua *dulce*"}`
- **linea_tiempo**: para fechas, de 2 a 4 puntos. `texto` admite dos líneas separadas por `|`.
  `{"tipo": "linea_tiempo", "titulo": "¿Qué fue *antes*?", "items": [{"etiqueta": "1096", "texto": "Clases en|Oxford", "destacar": true}, {"etiqueta": "1325", "texto": "Nace|Tenochtitlán"}], "nota": "…"}`

## Reglas de contenido

- Solo datos verificables y vigentes; comprobar cada uno con una búsqueda antes de usarlo. Las cifras de los gráficos también.
- Nada repetido: consulta y actualiza `curiosidades_usadas.md`.
- Ids con formato `AAAA-MM-DD-N` (N = 1, 2, 3 para los tres vídeos del día).
