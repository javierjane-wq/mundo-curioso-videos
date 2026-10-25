# Mundo Curioso 5000 · vídeos

Shorts verticales (1080×1920, unos 36 s) de curiosidades del mundo para el canal de YouTube Mundo Curioso 5000. Cada vídeo tiene **3 curiosidades**. Cada una lleva un **dibujo animado** propio del tema y un **gráfico animado** que la explica. El vídeo termina con la voz grabada del canal (`voz/outro.wav`, con la música bajando mientras se habla) invitando a suscribirse. No borres ni cambies los audios de `voz/`. `voz/intro.wav` anuncia "4 curiosidades", así que solo suena en los guiones antiguos de 4 datos.

## Cómo se genera un vídeo

1. Escribe un guion en `guiones/<id>.json` siguiendo `guiones/ejemplo.json`: 3 datos, palabras clave entre `*asteriscos*`, cada dato con `dibujo` y `grafico`.
2. Revisa los fotogramas: `python3 generar_video.py guiones/<id>.json --preview`. Saca una hoja PNG con el gancho, la parte del dibujo y la del gráfico de cada curiosidad, y el cierre.
3. Genera el vídeo: `python3 generar_video.py guiones/<id>.json` → `videos/<id>.mp4`.
4. Haz commit y push. El enlace público del vídeo queda en
   `https://raw.githubusercontent.com/javierjane-wq/mundo-curioso-videos/main/videos/<id>.mp4`
5. El escenario de Make "Mundo Curioso 5000 · Publicar Short" (id 8175470) descarga ese enlace y lo programa en YouTube.

Solo necesita Python con Pillow y numpy, y ffmpeg. Los dibujos los interpreta `dibujos.py`, sin librerías externas.

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

Un SVG dentro del JSON (usa comillas simples dentro del SVG). Estilo de dibujo animado plano:

- `viewBox='0 0 400 400'`, sin texto, sin degradados, sin imágenes y sin figuras con agujeros.
- Contorno oscuro grueso en todo: `stroke='#1d1b33'` con `stroke-width` de 6 a 9.
- De 4 a 6 colores vivos y planos. Brillos con formas blancas semitransparentes (`opacity`).
- Si encaja, carita simpática: ojos ovalados oscuros con un punto blanco, mejillas rosas (`#ff8fa3`, opacidad 0.8) y sonrisa.
- Un solo motivo grande y claro relacionado con el dato, con uno o dos detalles (estrellas, burbujas, sol…).
- Elementos permitidos: `circle`, `ellipse`, `rect` (con `rx`), `line`, `polyline`, `polygon`, `path` (M L H V C S Q T A Z), `g` con `transform`.
- El generador añade un borde blanco de pegatina, sombra y un balanceo suave.

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
