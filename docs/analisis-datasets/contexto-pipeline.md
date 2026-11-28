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
- **Resultado (6/11/2026):** 94.768 notas descargadas de 62 fuentes y 20.131 únicas con track desde 2024. Los pros y contras están en [el análisis de residuos](../v1-residuos/analisis-dataset-residuos.md) y en [el de soluciones](analisis-dataset-soluciones.md).

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

### Etiquetado manual antes de reclasificar (25/11/2026)

El piloto de residuos con LLM (Qwen 2.5 3B en Kaggle, 10/11) dejó categorías cortadas o inventadas: la respuesta se cortaba a los 220 tokens, el modelo leía solo 500 caracteres del cuerpo y nada verificaba que la categoría fuera válida. Antes de repetir la clasificación, se arma un set etiquetado a mano.

- **Quién:** Ignacio y Lauti etiquetan las mismas notas de los dos tracks, cada uno por su lado, para medir cuánto coinciden.
- **Muestra:** 25 notas por track de `data/movilidad.parquet` y `data/residuos.parquet`, con cuerpo de 300 caracteres o más, repartidas entre fuentes por turnos (semilla 42). Movilidad quedó con 10 fuentes (2 o 3 notas cada una) y residuos con 25 (una nota por fuente). Se mide con [`etiquetado/muestrear.py`](../../etiquetado/muestrear.py).
- **Qué se etiqueta:** si es relevante; si es problema, solución, ambas o ninguna; una o más categorías de problema y de solución; el alcance geográfico, y un comentario opcional. Las categorías son las de `TAXONOMIAS` en [`kaggle_pipeline.py`](../../scripts/clasificacion/kaggle_pipeline.py), y sus categorías "otro" (`OTRO_PROBLEMA_*`, `OTRA_SOLUCION_*`) piden texto libre. El alcance se etiquetó en la primera tanda; desde el 25/11 sale de la fuente.
- **Guardado:** un JSON por persona y track en `etiquetado/etiquetas/`, para que los dos puedan commitear sin conflictos.
- **Para qué:** medir el acuerdo entre personas y, después, evaluar al LLM contra estas etiquetas. Las notas que se usen como ejemplos dentro del prompt no cuentan para la evaluación.
- **Acuerdo medido (25/11/2026, con [`etiquetado/reconciliar.py`](../../etiquetado/reconciliar.py)):**

| Medida | Movilidad | Residuos |
|---|---|---|
| Acuerdo en todos los campos | 12 de 25 | 3 de 25 |
| Relevancia: acuerdo / kappa | 16 de 25 / 0,27 | 15 de 25 / 0,14 |
| Relevantes para Ignacio / para Lauti | 12 / 7 | 20 / 14 |
| Tipo, en las relevantes para los dos: acuerdo / kappa | 3 de 5 / 0,00 | 5 de 12 / 0,13 |
| Superposición media de categorías (Jaccard) | 0,57 | 0,26 |

  El acuerdo es bajo, sobre todo en qué cuenta como relevante: Ignacio marcó más notas relevantes que Lauti en los dos tracks. Con 25 notas las cifras son orientativas.
- **Reconciliación de movilidad (25/11/2026):** quedaron 4 notas relevantes de 25. Las reglas están en [`etiquetado/guia-movilidad.md`](../../etiquetado/guia-movilidad.md). Al cerrarla, se decidió:
  - **La seguridad vial queda afuera del track,** aunque sea educativa o hable de causas. Se sacó `SINIESTRALIDAD_VIAL` de [`etiquetado/config.js`](../../etiquetado/config.js); el piloto en `kaggle_pipeline.py` todavía la tiene.
  - **Una nota relevante exige un problema o una solución concretos.** Se sacó el tipo "ninguna". La nota del pase de las líneas 30 y 34 a SiBuS pasó a no relevante.
  - **Lo político entra solo con una medida de transporte concreta:** una obra, un servicio o una medida. La crítica o la disputa sin medida queda afuera.
  - **El alcance sale del origen del medio,** con [`scripts/diccionarios/alcance_fuentes.py`](../../scripts/diccionarios/alcance_fuentes.py), y ya no se etiqueta. En el gold, eso corrigió el Silence S04 (Ecoticias, España), que había quedado como nacional.
- **Reconciliación de residuos (25/11/2026):** quedaron 17 notas relevantes de 25, 9 de ellas de tipo "ambas". Las reglas están en [`etiquetado/guia-residuos.md`](../../etiquetado/guia-residuos.md). Al cerrarla, se decidió:
  - **Tiene que haber un residuo en el centro de la nota.** Entra la contaminación por desechos, como los fármacos o los agrotóxicos en el agua; el agro y la energía sin residuo quedan afuera. El riego solar en Ruanda pasó a no relevante.
  - **La medida concreta de gobierno entra,** incluidos los contratos y los fondos. El contrato de Lincoln y la convocatoria Anci-Conai pasaron a relevantes.
  - **La crítica a un gobierno sin una medida entra en residuos,** como falla regulatoria, y sigue afuera en movilidad. Cada track tiene su regla.
  - **Las campañas escolares y de sensibilización quedan afuera,** aunque informen cantidades. El concurso de Gauteng pasó a no relevante.
  - **`GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE` pasó a llamarse `GESTION_DEFICIENTE_RESIDUOS`** y abarca cualquier residuo, como ya se usaba. Se cambió en `config.js` y en el gold; el piloto en `kaggle_pipeline.py` y `taxonomia.py` todavía tiene el nombre viejo.
- **Falta:** escribir el prompt a partir de las dos guías, y etiquetar otra tanda de movilidad, porque 4 relevantes no alcanzan para darle ejemplos al LLM y además evaluarlo.

### Filtro determinístico de ruido en movilidad (25/11/2026)

El gold de movilidad tiene 4 relevantes de 25, y 1 de 14 en diarios. Para no gastar LLM en lo que la [guía](../../etiquetado/guia-movilidad.md) ya deja afuera, [`filtrar_movilidad.py`](../../scripts/clasificacion/filtrar_movilidad.py) corta antes con reglas fijas. Es la Fase 0 del [plan de Kaggle](../plan-kaggle-antipatrones-(INICIAL).md).

- **Solo diarios:** TN, El Doce, Clarín, La Nación y CBA24N. Los especializados pasan enteros: las raíces están en español, y 3 de las 4 relevantes del gold son de esos medios.
- **Reglas, en orden:** sección fuera del track (deportes, espectáculos, famosos, policiales, redes sociales y similares); vocabulario de choque o accidente en título o bajada (`choc*`, `accidente*`, `atropell*`, `volc*`, `siniestro*`, `tragedia`, `alcoholemia`, `picadas`); y ninguna raíz de `RAICES_MOVILIDAD` en título, bajada ni tags.
- **Seguridad vial con corte agresivo:** cualquier vocabulario de choque en título o bajada descarta la nota, aunque mencione transporte. Sigue la decisión de dejar la seguridad vial fuera del track.
- **Sin corte por largo del cuerpo:** puede haber notas útiles cortas.
- **No se guardan los descartes:** se pueden recalcular en un minuto, y `--muestra N` los muestra para auditar.
- **Resultado:** quedan 18.709 de 53.029 notas (35 %). Las cifras por motivo y fuente están en el [análisis de movilidad](analisis-dataset-movilidad.md#filtro-de-ruido-25112026).
- **Esquema:** `data/v1-samo-movilidad/movilidad_filtrado.parquet` tiene las mismas columnas que `data/movilidad.parquet`, más `alcance`, que sale de la fuente (26/11).
- **Soluciones (26/11):** con `--soluciones`, las mismas reglas se aplican a las 4.828 notas de movilidad de `data/soluciones.parquet` (Infobae se sumó a los diarios). Quedan 4.792 en `data/v1-samo-movilidad/movilidad_soluciones_filtrado.parquet`, con el mismo esquema. Se sumaron al diccionario de alcance las 28 fuentes de soluciones que faltaban; Ecoportal y Movilidad Eléctrica quedaron como internacionales con origen sin confirmar.
- **Falta:** que el equipo audite una muestra por motivo. Las reglas no sacan la política sin medida ni las notas de otros tracks.

### Clasificación v2 de movilidad, parte A (26/11/2026)

La v1 (Kaggle, 10/11) clasificó 12.714 notas de residuos en 7 h 14 min sobre 2×T4 (29 notas/min en total), con transformers + bitsandbytes 4-bit y el cuerpo cortado a 500 caracteres. Solo 547 quedaron clasificadas, con categorías cortadas o inventadas. La v2 cambia el motor y agrega una referencia para evaluar antes de correr todo.

- **Objetivo de fondo:** proyectar problemas y soluciones en un mismo espacio de embeddings, agrupar notas del mismo problema, emparejar soluciones con problemas, buscar zonas con problemas y sin soluciones, y ubicarlas en el territorio.
- **Motor:** vLLM, una copia de Qwen2.5-7B-Instruct AWQ por GPU, en dos procesos. Salida JSON guiada contra un esquema con listas cerradas y prefix caching para el prompt fijo. Código en [`clasificar_vllm.py`](../../scripts/clasificacion/clasificar_vllm.py) y [`notebooks/kaggle_movilidad_v2.ipynb`](../../notebooks/kaggle_movilidad_v2.ipynb). **Todavía no se corrió.**
- **Cascada:** la etapa 1 elige un `motivo` en todas las notas; la nota es relevante si el motivo es `problema_o_solucion_concreta`. La etapa 2, solo en las relevantes, escribe el problema en una oración normalizada, la solución, el tipo, las categorías y la ubicación. Sin causas ni actores. Los embeddings se calculan después, en CPU.
- **Entradas:** problemáticas y soluciones filtradas, con una columna `dataset`. Sin soluciones no hay qué emparejar.
- **Ejemplos few-shot:** 8 notas del gold del equipo (3 relevantes), en `scripts/clasificacion/ejemplos_movilidad.json`. Por eso el gold no sirve para evaluar al modelo de Kaggle.
- **Referencia:** 300 notas al azar de los Parquet filtrados (240 de problemáticas y 60 de soluciones, semilla 42), en 3 partes de 100, cada una con las 25 del gold mezcladas. Las etiqueta un LLM grande con la guía, usando [`prompt-etiquetador.md`](../../etiquetado/referencia/prompt-etiquetador.md). Se arma con [`muestrear_referencia.py`](../../etiquetado/muestrear_referencia.py).
- **Categorías:** lista cerrada más una `categoria_sugerida` libre y opcional en la referencia. El equipo decide qué sugerencias entran a la taxonomía antes de Kaggle.
- **Calibración del etiquetador (26/11):** Haiku etiquetó las 25 notas del gold. Coincidió en relevancia en 24 (kappa 0,83), en tipo en 3 de 3 y en categorías con Jaccard 1,00. Solo difirió en el Hub Green Sampa, que marcó como movilidad de pasada. **Está inflado:** la guía cita por nombre varias notas del gold (La Plata, Valladolid, SiBuS, Silence), así que el modelo vio parte de las respuestas. Informe en [`calibracion-informe.md`](../../etiquetado/referencia/calibracion-informe.md). Los gratuitos de OpenCode (DeepSeek V4.1 Flash, MiMo-V2.6-Flash) no se midieron: el equipo eligió Haiku.
- **Referencia etiquetada por Haiku (26/11):** 3 subagentes, uno por parte. Informe en [`movilidad-referencia-informe.md`](../../etiquetado/referencia/movilidad-referencia-informe.md).
  - **Relevantes:** 63 de 300 (21 %): 33 de 240 problemáticas (14 %) y 30 de 60 soluciones (50 %). Tipos: 39 solución, 13 ambas y 11 problema.
  - **Acuerdo de cada parte con el gold:** 23, 24 y 24 de 25 en relevancia (kappa 0,63, 0,83 y 0,83). Las tres marcaron como no relevante el Hub Green Sampa, que el gold tiene como relevante.
  - **Las partes no aplican el mismo criterio:** sin contar las del gold, marcaron 14, 31 y 18 relevantes de 100. La parte 2 tenía 25 notas de soluciones contra 13 y 22, lo que explica parte de la diferencia, no toda.
  - **Huecos de la guía que aparecieron:** tarifas y subsidios (una parte los toma como gestión, otra como política sin medida, otra como relevantes), paros y conflictos gremiales que cortan el servicio, anuncios de producto con tono publicitario, aviación eléctrica y proyectos sin aprobar. Fijar estos criterios mueve la cifra de relevantes.
  - **Categorías:** `OTRA_SOLUCION_MOVILIDAD` se usó en 13 de 63 relevantes y `OTRO_PROBLEMA_MOVILIDAD` en 9. Hubo 10 categorías sugeridas, ninguna repetida: entre otras, tarifas (estudiantil, integración), renovación de flota de buses, infraestructura de recarga e infraestructura vial.

### Versionado de resultados (26/11/2026)

- **Qué se decidió:** los resultados de la clasificación van por versión. La v1 (piloto de Qwen 2.5 3B del 10/11) queda en [`data/resultados/v1-residuos/`](../../data/resultados/v1-residuos/) y su análisis en [`docs/v1-residuos/`](../v1-residuos/). Se conserva para comparar, no se borra.
- **Cómo:** la versión vigente es `VERSION` en [`scripts/clasificacion/version.py`](../../scripts/clasificacion/version.py). Cada versión escribe en `data/resultados/<version>-<tema>/`, así que la v2 no pisa la v1.
- **Qué no se versiona:** los Parquet limpios de `data/` (`residuos.parquet`, etc.) son la entrada compartida y quedan en su lugar.

### Web del grafo (27/11/2026)

- **Qué se decidió:** el grafo se publica como web estática para difundir el análisis en redes, con el foco en **cómo lo hicimos**. Público: comunidad tech y público general.
- **Contrato de datos:** [`Frontend/exportar_web.py`](../../Frontend/exportar_web.py) lee el `.gexf` y `reporte_no_patrones.json` de una versión y escribe `Frontend/web/data/<version>-<tema>.json`. Ese JSON tiene `meta` (versión, tema, vigente, fechas, totales, advertencias y el embudo de `Frontend/recorridos/`), `nodos`, `aristas` y `rankings`. También actualiza `index.json`. La web solo lee esos JSON, así que una versión nueva se suma corriendo el exportador.
- **Stack:** HTML, CSS y JS sin build, con `3d-force-graph` (three.js) desde esm.sh. El deploy en Vercel (`Root Directory = Frontend/web`) lo hace el equipo.
- **Diseño:** el estándar de la categoría, con Obsidian Graph View y The Pudding como nivel de referencia. No toma nada de la UI del grafo vis.js anterior, que se eliminó junto con `generar_grafo_html_interactivo`.
- **Honestidad:** la v1 se exporta como no vigente, con sus límites como advertencias visibles. Las cifras del embudo salen de los análisis medidos, no de estimaciones.

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

### Clasificación v2 de movilidad

- **Criterios que la guía no cubre:** tarifas y subsidios, paros gremiales, anuncios de producto, aviación eléctrica y proyectos sin aprobar. Hay que decidirlos y, si cambian, volver a etiquetar esas notas de la referencia.
- **Qué categorías sugeridas entran a la taxonomía,** después de leer el informe de la referencia.
- **Parte B:** el evaluador del gate ([`evaluar_movilidad.py`](../../scripts/clasificacion/evaluar_movilidad.py)) y el paquete para Kaggle están listos (26/11); falta subirlo y correrlo. Fijar la versión de vLLM que corra en T4 con AWQ y salida guiada; correr el gate contra la referencia (umbrales propuestos: recall de relevancia ≥ 0,85, precisión ≥ 0,70, 100 % de JSON válidos, corrida completa estimada ≤ 4 h); corrida completa; embeddings y análisis de vacíos.

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
- [ ] ¿Las categorías se definen antes o surgen de los datos? Por ahora se parte de las de `kaggle_pipeline.py`, con texto libre en las categorías "otro" para que aparezcan las que faltan (25/11).
- [ ] ¿Se usan embeddings, clasificación con LLM o ambos?
- [ ] ¿Cómo se combinan las 11 medidas? ¿O se muestran por separado?
- [ ] ¿Qué significa exactamente "sin solución"?
- [ ] ¿Cómo se valida un resultado con personas del sector?

### Ejecución

- [ ] ¿Qué proveedor de IA se usa y con qué presupuesto?
- [ ] ¿Quién se encarga de cada parte?
- [ ] ¿Qué tiene que estar listo antes del 12/11?
