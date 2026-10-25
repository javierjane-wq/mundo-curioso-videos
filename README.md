# Mundo Curioso 5000 · vídeos

Shorts verticales (1080×1920, unos 36 s) de curiosidades del mundo para el canal de YouTube Mundo Curioso 5000. Cada vídeo tiene **3 curiosidades**. Cada una lleva un **dibujo animado** propio del tema y un **gráfico animado** que la explica. El vídeo termina con la voz grabada del canal (`voz/outro.wav`, con la música bajando mientras se habla) invitando a suscribirse. No borres ni cambies los audios de `voz/`. `voz/intro.wav` anuncia "4 curiosidades", así que solo suena en los guiones antiguos de 4 datos.

## Cómo se genera un vídeo

1. Escribe un guion en `guiones/<id>.json` siguiendo `guiones/ejemplo.json`: 3 datos, palabras clave entre `*asteriscos*`, cada dato con `dibujo` y `grafico`.
2. Revisa los fotogramas: `python3 generar_video.py guiones/<id>.json --preview`. Saca una hoja PNG con el gancho, la parte del dibujo y la del gráfico de cada curiosidad, y el cierre.
3. Genera el vídeo: `python3 generar_video.py guiones/<id>.json` → `videos/<id>.mp4`.
4. Haz commit y push. El enlace público del vídeo queda en
   `https://raw.githubusercontent.com/javierjane-wq/mundo-curioso-videos/main/videos/<id>.mp4`
5. El escenario de Make "Mundo Curioso 5000 · Publicar Short" (id 8175470) descarga ese enlace y lo programa en YouTube.

Solo necesita Python con Pillow y numpy, y ffmpeg. Los dibujos los interpreta `dibujos.py`, sin librerías externas. Generar un vídeo tarda unos 3 minutos.

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

Un SVG dentro del JSON (usa comillas simples dentro del SVG). Lo interpreta `dibujos.py`. Estilo: **ilustración con acabado 3D de animación**: formas redondeadas y voluminosas, materiales brillantes y luz de estudio, como un fotograma de una película de animación moderna (sin copiar personajes de ninguna). Mira los tres de `guiones/ejemplo.json` antes de dibujar: son el nivel mínimo de calidad.

**Composición**
- `viewBox='0 0 400 400'`. Toda la escena va dentro de un círculo: define `<clipPath id='c'><circle cx='200' cy='200' r='180'/></clipPath>`, mete la escena en `<g clip-path='url(#c)'>…</g>` y cierra con un aro blanco: `<circle cx='200' cy='200' r='180' fill='none' stroke='#ffffff' stroke-width='10'/>`.
- Una escena completa, no un objeto suelto: fondo (cielo, mar, espacio, interior…), un motivo principal grande que se reconozca a primera vista y 3 o 4 detalles de apoyo (nubes, sol, burbujas, estrellas, pájaros, peces…).
- Las partes que se mueven deben quedar dentro del círculo incluso en el punto más extremo de su movimiento (deja de margen al menos su amplitud).

**Acabado 3D** (sin contornos negros; el volumen sale de la luz, que viene de arriba a la izquierda)
- **Sombreado esférico**: cada forma redondeada con `radialGradient` de 3 o 4 paradas, con el centro desplazado hacia la luz (`cx='0.35' cy='0.3'`): tono muy claro, tono medio y tono oscuro saturado en el borde.
- **Caras planas** (edificios, cajas, pirámides): cara frontal iluminada con `linearGradient` claro y cara lateral derecha más oscura, para que se vea la profundidad.
- **Brillo especular**: una elipse con `radialGradient` blanco a transparente en la zona de luz, y a veces un punto pequeño muy brillante.
- **Luz de contorno**: en el lado de sombra, un trazo de la misma silueta con `stroke` en `linearGradient` (de transparente a un tono claro), recortado con un `clipPath` de la propia figura.
- **Sombra propia** dentro de la figura (forma oscura con `opacity` 0.2–0.35 recortada con `clipPath`) y **sombra de contacto** en el suelo: elipse con `radialGradient` oscuro a transparente.
- **Fondo de estudio**: degradado radial suave y algún círculo de luz desenfocado (`radialGradient` blanco a transparente).
- Paleta armónica de 6 a 10 tonos, vivos pero no chillones. El motivo principal, más saturado que el fondo.
- **Personajes**: si el motivo puede tener cara (una gota, un planeta, un animal, una nube), dale ojos grandes y brillantes: blanco con degradado, iris en degradado, pupila, un reflejo grande y otro pequeño. Mejillas con `radialGradient` rosa a transparente y boca con interior oscuro y lengua. En edificios, paisajes y objetos técnicos, sin cara.

**Movimiento** (cuanto más vivo, mejor: anima de 4 a 7 partes por dibujo, con fases distintas para que no se muevan todas a la vez)
- Cada parte animada es un `<g data-anim='TIPO'>`. Tipos:
  - `flotar`: sube y baja (nubes, humo, burbujas, objetos en el aire).
  - `desplazar`: va y viene en horizontal (peces nadando, nubes, pájaros, coches).
  - `balancear`: oscila alrededor de `data-origen` (colas, borlas, banderas, hojas, ramas).
  - `girar`: gira sin parar (agujas de reloj, planetas, ruedas, hélices).
  - `latir`: crece y decrece (corazones, estrellas grandes, botones).
  - `saltar`: bota con estiramiento en el aire y aplastamiento al caer; `data-origen` es el punto de apoyo en el suelo. Ideal para personajes.
  - `sombra`: la sombra de contacto de algo que salta; usa el mismo `data-periodo` y `data-fase` que el salto.
  - `orbitar`: da vueltas en una elipse (lunas, satélites, abejas).
  - `parpadear`: cierra un momento los ojos (un grupo con los dos ojos; `data-origen` en el centro de los ojos).
  - `brillar`: destella creciendo y desvaneciéndose (soles, halos, chispas, llamas).
- Se pueden **anidar**: una parte animada dentro de otra se mueve con ella (los ojos que parpadean dentro del cuerpo que salta; la cola que se balancea dentro del pez que nada).
- Opciones: `data-origen='x y'` (punto de giro, escala o apoyo; por defecto, el centro de la parte), `data-periodo` (segundos por ciclo), `data-amplitud` (píxeles del viewBox en flotar, desplazar, orbitar y saltar; grados en balancear; % en latir) y `data-fase` (segundos de desfase).

**Técnica**
- Elementos: `circle`, `ellipse`, `rect` (con `rx`), `line`, `polyline`, `polygon`, `path` (M L H V C S Q T A Z), `g` con `transform`, `defs`, `linearGradient`, `radialGradient` (con `stop-opacity`) y `clipPath`. Un `path` con varias subrutas hace huecos (regla par-impar).
- Sin texto, sin imágenes, sin filtros ni máscaras. Nada de personajes, logotipos ni marcas reales.
- Para revisar un dibujo de cerca: `python3 dibujos.py dibujo.svg salida.png 600`.
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
