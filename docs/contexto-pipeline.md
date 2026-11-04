# Pipeline de problemáticas: contexto

Última actualización: 4/11/2026. Equipo: Ignacio, Lauti y Diego.

## Objetivo

Encontrar los problemas más recurrentes en las fuentes de información de cada track, para descubrir alguno que el equipo no conocía.

El resultado es el punto 0 para elegir la problemática y plantear el producto. También sirve como evidencia para el pitch.

## Decisiones tomadas

- **Orden de los tracks:** primero residuos y, si funciona, el mismo proceso con los otros tres. No llegar a los otros tres es aceptable.
- **Tamaño del dataset:** el objetivo es 10.000 notas por track. Todavía no está comprobado que existan.
- **Fecha:** se guarda para filtrar y comparar, no como peso fijo desde el inicio. Un problema que persiste de 2021 a 2026 es justo lo que se busca.
- **Geografía:** tienen más peso los problemas que aparecen en varios países y los locales. Faltan los valores y definir qué cuenta como local.
- **Fuentes y arquitectura:** las posibles fuentes están en [este doc](https://claude.ai/artifact/Ks4WAtVgcdcGNSxywUQFyw) y el boceto digitalizado, en [pipeline-arquitectura.html](pipeline-arquitectura.html).
- **Función de los resultados:** son un insumo para decidir. No prueban por sí solos que un problema importe.

### Medidas de recurrencia

| Grupo | Medida | Qué mira |
|---|---|---|
| Volumen | Cantidad de notas | Cuántas notas hablan del problema |
| Volumen | Hechos distintos | Cuántos eventos separados aparecen |
| Volumen | Medios independientes | Cuántos medios lo cubren por su cuenta |
| Tiempo | Años en que aparece | Si persiste a lo largo de los años |
| Tiempo | Continuidad | Si es parejo durante meses o solo un pico |
| Tiempo | Tendencia | Si crece o baja en los últimos años |
| Alcance | Lugares afectados | En cuántas ciudades o provincias aparece |
| Alcance | Actores afectados | Qué tipos de actores menciona |
| Alcance | Magnitud informada | Qué cifras reportan las notas |
| Respuesta | Soluciones fallidas | Si sigue después de planes o anuncios |
| Respuesta | Origen de la voz | Quién plantea el problema |

## Hechos

### Del evento

- Se puede usar datos externos, llevar trabajo hecho y enviar textos de diarios a una API de IA. Lo confirmó la organización, según Ignacio.
- Día 1: 12/11. Demo Day: 13/11.
- Los criterios de evaluación no están publicados.

### Del equipo

- Ya está inscripto.
- Nadie tiene experiencia directa con residuos.

### De la inspiración

El video "Idea Plotter", de @re_skob, se basa en una receta de Synthetic Beef:

1. Convirtieron 189.495 juegos de Steam en embeddings de 1.024 dimensiones.
2. Buscaron zonas vacías en ese mapa.
3. Generaron ideas para esas zonas y volvieron a medir qué tan cerca quedaban de juegos existentes.

Ese proceso mide qué tan distinta es una idea, no si es buena.

### De las fuentes (probado el 4/11/2026)

| Fuente | Resultado |
|---|---|
| La Nación | Publica sitemaps diarios; su índice histórico cubre 730 días, desde noviembre de 2024 |
| La Nación | Su `robots.txt` excluye `/buscador` |
| La Voz | Su `robots.txt` excluye a `ChatGPT-User`, `OpenAI`, `ChatGPT`, `FacebookBot` y `Meta AI` |
| La Voz | Sus dos sitemaps probados devolvieron el error 1016 |
| Clarín | Declara sitemaps en su `robots.txt`; su contenido no se revisó |
| Reddit | Su `robots.txt` excluye a cualquier bot genérico |
| GDELT | Rechazó las consultas por límite de frecuencia; no se midió nada |

### Muestra de volumen (La Nación)

Se revisó el día 15 de cada mes de 2025, con 5.305 URLs en total. Tres contenían palabras clave de residuos, y una de ellas era un falso positivo ("televisión basura").

Esto da unas 60 notas relevantes por año si se mira solo la URL. La muestra es muy chica, así que es apenas un orden de magnitud. La búsqueda en el texto completo no se probó.

## Limitaciones del método

- Las noticias muestran lo que se publica, no todo lo que pasa. Un problema frecuente en los diarios no es necesariamente el más grave.
- Lo más recurrente suele ser lo más visible. Eso puede chocar con el objetivo de encontrar algo que no se conocía.
- Que una solución no aparezca en las noticias no significa que no exista.

## Falta aclarar

### Fuentes

- [ ] ¿Qué diarios nacionales y de Córdoba entran?
- [ ] ¿Cómo se accede a La Voz, dado que sus sitemaps fallaron?
- [ ] ¿Hay un archivo de La Nación anterior a noviembre de 2024?
- [ ] ¿Qué foros de sustentabilidad y ecologismo existen?
- [ ] ¿Se incluyen redes sociales? ¿Por qué vía permitida?
- [ ] ¿GDELT aporta cobertura argentina suficiente?
- [ ] ¿Qué fuentes sirven para relevar soluciones existentes?
- [ ] ¿Qué permiten los términos de uso de cada medio?

### Datos

- [ ] ¿Cuántas notas hay realmente? ¿Qué se hace si un track no llega a 10.000?
- [ ] ¿Se puede obtener el texto completo con los muros de pago?
- [ ] ¿Qué campos se guardan de cada nota, además de título, fecha y texto?
- [ ] ¿Cómo se detectan las notas duplicadas o replicadas?

### Método

- [ ] ¿La unidad de análisis es la nota o el hecho?
- [ ] ¿Las categorías se definen antes o surgen de los datos?
- [ ] ¿Se usan embeddings, clasificación con LLM o ambos?
- [ ] ¿Cómo se combinan las 11 medidas? ¿O se muestran por separado?
- [ ] ¿Qué significa exactamente "sin solución"?
- [ ] ¿Cómo se valida un resultado con personas del sector?

### Ejecución

- [ ] ¿Qué proveedor de IA se usa y con qué presupuesto?
- [ ] ¿Quién se encarga de cada parte?
- [ ] ¿Qué tiene que estar listo antes del 12/11?
