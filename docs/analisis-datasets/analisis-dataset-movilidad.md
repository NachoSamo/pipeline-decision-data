# Análisis del dataset de problemáticas de movilidad sustentable

Foto del 8/11/2026, después de la limpieza con [`limpiar.py`](../../scripts/limpiar.py) y antes de clasificar. El filtro de ruido del 25/11 tiene su propia sección; el resto de las cifras son de `data/movilidad.parquet` sin filtrar.
CBA24N se cortó a mitad de camino: se bajaron 731 de las 1.083 notas previstas, y quedan 728 después de la limpieza.

| | Problemáticas de movilidad sustentable |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de movilidad se publican, quién los plantea y con qué voz |
| **Ubicación** | `data/movilidad.parquet` |
| **Notas** | 53.029 (eran 67.399 antes de la limpieza) |
| **Fuentes** | 10 |
| **Período** | 2010 a 2026. Las fuentes con API de WordPress, desde 2021 |
| **Criterio para quedar** | Coincidir con la búsqueda y pasar la limpieza. No hay filtro por tema |
| **Tamaño aproximado** | 52 MB |

El circuito y las decisiones están en [`circuito-problematicas.md`](../circuito-problematicas.md), cómo se baja cada fuente en [`scrapping-webs.md`](../scrapping-webs.md#dataset-de-problemáticas-biodiversidad-y-movilidad) y los criterios de limpieza en [`contexto-pipeline.md`](contexto-pipeline.md#limpieza-y-consolidación-8112026). Para biodiversidad, ver [el análisis de biodiversidad](analisis-dataset-biodiversidad.md).

## Limpieza

| Iniciales | Título corto | Sin cuerpo | Seriado | Título repetido | Cuerpo repetido | Finales |
|---:|---:|---:|---:|---:|---:|---:|
| 67.399 | 75 | 12.449 | 1.573 | 187 | 86 | 53.029 |

Es el dataset que más cambió (−21 %). Las notas sin cuerpo eran casi todas videos de El Doce y TN. Los títulos seriados son notas de servicio, como cronogramas de pagos, cotizaciones del dólar, cortes de calles o "Qué significa la señal…".

## Filtro de ruido (25/11/2026)

[`filtrar_movilidad.py`](../../scripts/clasificacion/filtrar_movilidad.py) saca sin LLM el ruido de los diarios y escribe `data/v1-samo-movilidad/movilidad_filtrado.parquet`. Quedan **18.709 de 53.029 notas (35 %)**, en 23,5 MB. Los medios especializados pasan enteros. Los criterios están en [`contexto-pipeline.md`](contexto-pipeline.md#filtro-determinístico-de-ruido-en-movilidad-25112026).

| Motivo | Notas | % del total |
|---|---:|---:|
| Sección fuera del track | 15.694 | 29,6 % |
| Seguridad vial | 6.417 | 12,1 % |
| Sin raíces de movilidad | 12.209 | 23,0 % |
| **Quedan** | **18.709** | **35,3 %** |

| Fuente | Iniciales | Quedan | % que queda |
|---|---:|---:|---:|
| TN | 23.770 | 4.574 | 19 % |
| El Doce | 14.091 | 3.215 | 23 % |
| Clarín | 8.346 | 4.721 | 57 % |
| La Nación | 1.948 | 1.596 | 82 % |
| CBA24N | 728 | 457 | 63 % |
| Especializados (Grist, CicloVivo, Visión Sustentable, Ecoticias, Ecomundo) | 4.146 | 4.146 | 100 % |

- **La concentración baja:** TN y El Doce pasan del 71 % al 42 % de las notas.
- **Córdoba:** quedan 3.672 notas de El Doce y CBA24N.
- **Las 4 relevantes del gold pasan.** Es un chequeo débil: solo una es de un diario.
- **Lectura de control:** Claude leyó 15 títulos al azar por motivo (semilla 42) y no encontró ninguno relevante según la guía. El más dudoso, el choque de trenes en Palermo, igual es seguridad vial. Falta que el equipo lea su propia muestra con `--muestra 20`.
- **Alcance (26/11):** el Parquet filtrado tiene la columna `alcance`, que sale de la fuente: 11.431 notas nacionales, 3.672 de Córdoba, 2.418 internacionales y 1.188 de América Latina.
- **Sigue habiendo ruido:** quedan política o economía sin medida de transporte, notas de otros tracks y consejos de manejo sin palabras de choque. Eso lo descarta el LLM.

## Cifras

| Fuente | Notas | Con raíces del tema en título o bajada |
|---|---:|---:|
| TN | 23.770 | 27 % |
| El Doce | 14.091 | 26 % |
| Clarín | 8.346 | 48 % |
| Grist | 1.981 | no medido (inglés) |
| La Nación | 1.948 | 98 % |
| CicloVivo | 1.188 | no medido (portugués) |
| CBA24N | 728 | 100 % |
| Visión Sustentable | 469 | 19 % |
| Ecoticias | 437 | 98 % |
| Ecomundo | 71 | 14 % |

- **Por idioma de la fuente:** español 49.860, inglés 1.981 y portugués 1.188.
- **Con raíces del tema en título o bajada:** 17.386 de las 49.860 notas en español (35 %).
- **Argentina:** 49.423 notas de 7 medios, con 16.958 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N, con 14.819 notas y 4.447 con raíces del tema en título o bajada. CBA24N aporta 728, todas con el tema en título o bajada porque se eligieron por la URL.
- **Por año:** entre 1.185 y 5.056 por año de 2016 a 2023, 8.787 en 2024, 8.804 en 2025 y 8.243 hasta el 6/11/2026.
- **Calidad del texto:** todas las notas tienen cuerpo. La mediana es de 2.374 caracteres y 363 tienen menos de 300.
- **Tipo de voz:** 48.416 de diario, 4.128 de medio especializado y 485 de opinión, sobre todo de TN (258), El Doce (113) y Clarín (71).
- **Coincidencia con soluciones:** 325 de las 4.828 notas del track de movilidad de `data/soluciones.parquet` también están acá.

## Pros

- **Muy local:** casi todo es de medios argentinos, y El Doce y CBA24N aportan 14.819 notas de Córdoba. Hay términos propios como SiBus, TAMSE, Coniferal y Circunvalación.
- **Volumen alto:** aun quedándose con las notas con el tema en título o bajada, hay unas 17.000 en español.
- **Menos ruido de servicio:** la limpieza sacó 1.573 notas seriadas y todas las de video sin texto.
- **Sitemaps precisos:** en La Nación y CBA24N casi todas las notas tienen el tema en título o bajada, porque se eligieron por la URL.
- **Poca superposición con soluciones:** comparten 508 notas.

## Contras

- **Mucho ruido:** en una lectura rápida de 40 títulos al azar, antes de la limpieza, solo unas 6 parecían tratar sobre movilidad. Entraron espectáculos, deportes y policiales por palabras como "tránsito", "colectivo" o "boleto". La limpieza no filtra por tema; el filtro del 25/11 saca buena parte (ver arriba). Es una estimación informal, no una medición.
- **Clarín trae ruido:** la mitad de sus notas (52 %) no tiene el tema en título ni bajada. Probablemente entraron por la etiqueta amplia "autos".
- **Concentración extrema:** TN y El Doce reúnen 37.861 notas (71 %). Contar sin ponderar es casi contar lo que publican esos dos medios.
- **Notas más cortas:** la mediana de cuerpo es menos de la mitad que en biodiversidad.
- **Sin señales de problema:** `senal_problema` y `senal_opinion` se eliminaron el 8/11 porque se basaban en palabras genéricas, como "impacto". Distinguir problemas queda para la clasificación.
- **Serie temporal engañosa:** el salto de 2023 a 2024 no está explicado. Puede venir de cómo ordenan los buscadores de TN y El Doce, que tienen tope de páginas, y no de un aumento del tema.
- **Cobertura parcial:** Infobae no se corrió (decisión del 6/11): sus etiquetas de movilidad son muy amplias y tardaría más de 8 horas. En CBA24N se listaron solo las 1.083 notas con raíces específicas y se bajaron 731: el sitio respondió 429 dos veces y se decidió parar (6/11). Mongabay quedó afuera por ser de biodiversidad.
- **Poco internacional:** Grist, CicloVivo y Ecoticias suman 3.606 notas, el 7 %.
- **Se pisa con otros datasets:** 1.535 notas también están en biodiversidad y 1.437 en residuos.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema. Buscar con palabras de problema sesga hacia lo conflictivo y lo visible.

## Cómo se midió

- **Conteos:** directos sobre `data/movilidad.parquet` del 8/11/2026.
- **Raíces en título o bajada:** con `RAICES_MOVILIDAD`, que están en español. Por eso no se midieron las fuentes en inglés y portugués.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por medio, sin un campo de país en los datos.
- **`keywords_core`:** usa las expresiones de residuos, así que no sirve para este dataset.
- **Coincidencias entre datasets:** por URL.
- **Muestras de títulos:** se leyeron una sola vez y no las revisó el equipo. Sirven como orientación.
