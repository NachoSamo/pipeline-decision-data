# Pipeline de problemáticas: contexto

Última actualización: 8/11/2026. Equipo: Ignacio, Lauti y Diego.

## Objetivo

Encontrar los problemas más recurrentes en las fuentes de información de cada track, para descubrir alguno que el equipo no conocía.

El resultado es el punto 0 para elegir la problemática y plantear el producto. También sirve como evidencia para el pitch.

## Decisiones tomadas

- **Orden de los tracks:** primero residuos y, si funciona, el mismo proceso con los otros tres. No llegar a los otros tres es aceptable.
- **Tamaño del dataset:** el objetivo es 10.000 notas por track. En residuos, más de 10.000 notas mencionan el tema, pero falta medir cuántas son útiles. Los otros tres tracks no se midieron.
- **Fecha:** se guarda para filtrar y comparar, no como peso fijo desde el inicio. Un problema que persiste de 2021 a 2026 es justo lo que se busca.
- **Geografía:** tienen más peso los problemas que aparecen en varios países y los locales. Faltan los valores y definir qué cuenta como local.
- **Fuentes y arquitectura:** las posibles fuentes están en [Fuentes para el dataset del pipeline.md](../analisis-fuentes/Fuentes%20para%20el%20dataset%20del%20pipeline.md) y el boceto digitalizado, en [pipeline-arquitectura.html](../pipeline-arquitectura.html).
- **Función de los resultados:** son un insumo para decidir. No prueban por sí solos que un problema importe.

- **Notas de soluciones:** son las más valiosas para encontrar patrones y contrastar con soluciones ya validadas, como [Reaquila en Visión Sustentable](https://www.visionsustentable.com/2026/06/24/reaquila-plataforma-gestion-residuos-reciclaje-empresas/). Una nota así prueba que la solución existe, no que esté validada. Falta definir qué evidencia cuenta como validación.

- **Arquitectura:** después del dataset van filtro y limpieza, clasificación en problema, solución, ambas u otra, dos ramas de análisis, tres vistas (ranking, grafo y mapa de embeddings) y contraste con soluciones validadas y datos abiertos. Sigue en duda si hace falta una muestra de control.

### Evaluación de volumen (4/11/2026, 23:34, descargas en curso)

**Actualización del 5/11/2026, 00:49:** terminaron todas las descargas salvo Futuro Sustentable, que no tiene datos. Hay 47.944 notas únicas en 33 Parquet: 41.140 con cuerpo, 29.413 con cuerpo y mención, y 20.045 que además mencionan el tema en título o bajada. De las 29.413, 9.028 son de medios argentinos, 1.076 de Mongabay, 3.284 de medios de España y 16.025 de otros países e idiomas. Unas 1.555 de las notas argentinas son de secciones de Infobae de otros países. La tabla de abajo es la medición anterior, sin las 19 fuentes especializadas.

Hay 28.072 notas descargadas de residuos, y 13.633 tienen cuerpo y mencionan el tema. Mencionarlo no vuelve útil a una nota: en una muestra informal de 56 títulos, cerca de la mitad parecía útil. Si esa proporción se mantuviera, serían unas 6.800, pero es una lectura rápida, no una medición.

| Fuente | Notas únicas | Con cuerpo | Con cuerpo y mención | Estado |
|---|---:|---:|---:|---|
| TN | 8.245 | 5.018 | 1.592 | En curso, sin Parquet |
| El Doce | 6.194 | 3.835 | 877 | Terminada |
| Resource Recycling | 2.681 | 2.681 | 2.591 | Terminada |
| Infobae | 2.641 | 2.640 | 2.217 | Terminada, solo prioritarias |
| Clarín | 2.609 | 2.604 | 1.553 | Terminada, solo prioritarias |
| Mongabay | 1.718 | 1.718 | 1.076 | Terminada |
| Circular Online | 1.081 | 1.081 | 1.063 | Terminada |
| Visión Sustentable | 829 | 829 | 743 | Terminada |
| Mongabay en inglés | 529 | 529 | 521 | En curso, sin Parquet |
| Ecomundo | 468 | 468 | 333 | Terminada |
| ECOBIZ | 398 | 398 | 395 | Terminada |
| La Nación | 370 | 366 | 364 | Terminada |
| CBA24N | 309 | 308 | 308 | En curso, sin Parquet |
| Grist | Sin datos | Sin datos | Sin datos | Pendiente, después de Mongabay en inglés |
| Futuro Sustentable | Sin datos | Sin datos | Sin datos | Sin archivo en `data/` |
| **Total** | **28.072** | **22.475** | **13.633** | |

Los 10 Parquet ya generados suman 18.989 notas únicas, y 11.212 tienen cuerpo y mención.

Cómo leer la tabla:

- **Mención:** usa `relevante` de `scripts/progreso.py`, con `RAICES_RESIDUOS` en español y `RAICES_INGLES_RESIDUOS` en inglés. Es más estricta que el diccionario completo: en El Doce da 877 notas, contra 1.331 con `diccionario_en_texto`.
- **Duplicados:** las notas son únicas dentro de cada fuente. No se midieron los duplicados entre fuentes.
- **Fuentes en inglés:** aportan 4.175 de las 13.633 notas con mención y cubren desde 2024. Quedan 9.458 en español, no todas de Argentina.
- **Córdoba:** El Doce y CBA24N suman 1.185 notas con mención. La Voz sigue sin acceso resuelto.

Conviene decidir si hacen falta más fuentes cuando terminen las descargas, mirando los huecos y no solo el total: Córdoba y soluciones.

En Infobae y Clarín se decidió bajar solo lo prioritario: tags de residuos y notas de tags amplios con el tema en título, bajada o URL. Quedan sin bajar 5.781 notas en Infobae y 1.894 en Clarín, que se pueden retomar si hace falta.

### Dataset de soluciones (5/11/2026)

Busca notas desde 2024 sobre productos, startups o proyectos tecnológicos aplicados a un problema, para contrastarlas con los problemas de cada track. Una nota no equivale a una solución: contarlas requiere extraerlas después.

- **Volumen:** lo fija la medición, no la meta inicial de 500.000. Desde 2024, las 26 fuentes WordPress que había entonces suman 75.759 notas de todos los temas.
- **Fuentes:** las actuales más 29 nuevas de tecnología, agro, movilidad, biodiversidad y ambiente, para no sesgar la comparación hacia residuos.
- **Salida:** un Parquet por track y fuente. Una nota puede estar en varios tracks, y las que no tienen track se descartan.
- **Asignación de tracks:** por raíces en título o bajada. Con menciones en el cuerpo resultaba demasiado laxa.
- **Resultado (6/11/2026):** 94.768 notas descargadas de 62 fuentes y 20.131 únicas con track desde 2024. Los pros y contras están en [el análisis de residuos](analisis-dataset-residuos.md) y en [el de soluciones](analisis-dataset-soluciones.md).

### Limpieza y consolidación (8/11/2026)

[`scripts/limpiar.py`](../../scripts/limpiar.py) une los Parquet por fuente en un archivo por dataset, con el mismo esquema en los cuatro:

```text
data/biodiversidad.parquet   data/movilidad.parquet   data/residuos.parquet   data/soluciones.parquet
```

Pasos, en este orden:

1. **Recorta el pie de suscripción** del cuerpo: el boletín de Mongabay Latam, el muro de pago de Bioplastics News, el formulario de 320°, los newsletters de Inside Climate News, el glosario en JavaScript de Grist y líneas cortas de "Sign up for the … newsletter".
2. **Descarta** las notas con título de menos de 15 caracteres, sin cuerpo (casi todas videos), sin fecha o con título seriado. Los seriados son notas de servicio que se repiten con el mismo comienzo, como "Cronograma de pagos", "Dólar oficial y dólar…", "Cortes de luz", "Los cortes de calles", "Lo más leído", "Pocos lo saben" u horóscopos.
3. **Deduplica** dentro de cada dataset por `id`, por título normalizado (sin tildes, mayúsculas ni espacios de más) y por cuerpo. Se queda con la versión de cuerpo más largo y, si empatan, con la más vieja. Así, entre la versión de video y la de texto de TN, queda la de texto.
4. **Une los tracks:** en soluciones, una nota repetida entre tracks queda una sola vez, con todos sus tracks en la columna `tracks`.
5. **Recalcula `tipo_voz`:** `diario` para CBA24N, Clarín, El Doce, Infobae, La Nación y TN; `medio_especializado` para el resto; `opinion` si la sección o las etiquetas lo indican. Las organizaciones, como GAIA o ISWA, quedan como `medio_especializado`.
6. **Guarda** con zstd nivel 19, para quedar debajo de los 100 MB por archivo de GitHub, y borra los Parquet por fuente.

| Dataset | Iniciales | Título corto | Sin cuerpo | Seriado | `id` repetido | Título repetido | Cuerpo repetido | Finales |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Biodiversidad | 35.951 | 40 | 1.957 | 173 | 0 | 97 | 64 | 33.620 |
| Movilidad | 67.399 | 75 | 12.449 | 1.573 | 0 | 187 | 86 | 53.029 |
| Residuos | 47.944 | 87 | 7.325 | 63 | 0 | 209 | 28 | 40.232 |
| Soluciones (filas de los 4 tracks) | 20.914 | 4 | 190 | 57 | 777 | 68 | 1 | 19.817 |

Ninguna nota se descartó por falta de fecha.

**Esquema común:** `id`, `url`, `fuente`, `titulo`, `bajada`, `fecha`, `seccion`, `tags`, `tipo`, `body`, `acceso_libre`, `terminos_busqueda`, `terminos_en_texto`, `diccionario_en_texto`, `keywords_core`, `tipo_voz` y `tracks`.

- **Se eliminaron `senal_problema` y `senal_opinion`.** Marcaban el 78 % y el 67 % de las notas de biodiversidad con palabras genéricas como "impacto" o "riesgo", así que no separaban. Distinguir problemas queda para la clasificación.
- **`vertical` se reemplazó por `tracks`**, una lista, para que problemáticas y soluciones compartan esquema.
- **Se eliminaron `edicion` y `ruta`**, que solo traía Infobae y se pueden sacar de la URL.
- **`acceso_libre`** pasó a ser booleano en todas las fuentes, con nulo si el medio no lo informa.

**Lo que no hace:** no filtra por tema ni por año, no saca las coberturas en vivo y no detecta la misma noticia reescrita o traducida por otro medio. Tampoco deduplica entre datasets: una nota puede estar en residuos y en soluciones.

**Para volver a descargar:** los scrapers siguen escribiendo un Parquet por fuente en `data/<dataset>/`, pero esas carpetas ya no tienen los archivos anteriores. Recuperarlos de Git (commit `afe111c`) antes de retomar una descarga, y volver a correr `limpiar.py` después. En soluciones, el orden es `crudo/` → `separar_por_track.py` → `limpiar.py`.

### Plan de scraping

Cómo funciona cada script: [scrapping-webs.md](../scrapping-webs.md).

Este es el plan que planteó Ignacio:

1. Identificar 10 fuentes relevantes, medir cuántos datos aportan y sumar otras si faltan.
2. Catalogar las secciones de cada fuente, como ecología o sustentabilidad.
3. Armar un diccionario amplio de palabras clave por track, que funcione como primer filtro.
4. Lanzar agentes de IA en paralelo, uno por fuente, que ejecuten Playwright en bucle.
5. Escribir una guía de scraping por fuente.
6. Guardar el dataset, quizá en Parquet.

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

- [ ] ¿Cuántas de las notas que mencionan residuos son útiles? ¿Qué se hace si un track no llega a 10.000?
- [ ] ¿Alcanza con recorrer secciones ambientales o hay notas de residuos en otras secciones?
- [ ] ¿Los agentes recorren cada página o generan un script por fuente que después se repite?
- [ ] ¿Qué palabras entran en el diccionario de cada track?
- [ ] ¿Se puede obtener el texto completo con los muros de pago?
- [ ] ¿Qué campos se guardan de cada nota, además de título, fecha y texto?
- [x] ¿Cómo se detectan las notas duplicadas o replicadas? Dentro de cada dataset, por `id`, título normalizado y cuerpo (8/11). Falta detectar las reescritas o traducidas.

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
