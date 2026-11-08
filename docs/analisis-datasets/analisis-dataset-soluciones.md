# Análisis del dataset de soluciones tecnológicas

Foto del 8/11/2026, después de la limpieza con [`limpiar.py`](../../scripts/limpiar.py) y antes de extraer o clasificar soluciones. Las cifras cambian cuando se ejecuten esas etapas.

| | Soluciones tecnológicas |
|---|---|
| **Pregunta que ayuda a responder** | Qué soluciones tecnológicas se publican en cada track |
| **Ubicación** | `data/soluciones.parquet`. La columna `tracks` lista los tracks de cada nota |
| **Notas** | 19.817 únicas (eran 20.131 únicas y 20.914 filas sumando los tracks) |
| **Fuentes** | 62 |
| **Período** | 2024 a 2026 |
| **Criterio para quedar** | Coincidir con la búsqueda, ser de 2024 en adelante, tener un track en título o bajada y pasar la limpieza |
| **Tamaño aproximado** | 36 MB |

Para el dataset de residuos, ver [el análisis de residuos](analisis-dataset-residuos.md). Los criterios de limpieza están en [`contexto-pipeline.md`](contexto-pipeline.md#limpieza-y-consolidación-8112026).

## Cifras

| Etapa | Notas | Qué pasa |
|---|---:|---|
| Descarga en `crudo/` (fuera de Git) | 94.768 | Todo lo que coincidió con los términos |
| Desde 2024 | 80.180 | Se quitan 14.588 anteriores |
| Con track en título o bajada | 20.131 | Se quita el 75 % de las que quedaban |
| Después de la limpieza (8/11) | 19.817 | Se quitan 190 sin cuerpo, 57 seriadas, 4 de título corto y 69 repetidas por título o cuerpo. Las 777 filas repetidas entre tracks se unen en una sola nota |

| Track | Notas | Fuentes | Fuentes con 100 o más | Las 3 mayores reúnen | Medios argentinos | Córdoba | También en su dataset de problemas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Residuos | 6.811 | 61 | 19 | 33 % | 244 | 6 | 4.738 |
| Agro | 6.577 | 57 | 15 | 46 % | 2.599 | 14 | sin dataset |
| Movilidad | 4.828 | 57 | 11 | 53 % | 558 | 41 | 325 |
| Biodiversidad | 2.378 | 49 | 6 | 44 % | 152 | 1 | 1.014 |

- **Por año:** 6.009 en 2024, 7.007 en 2025 y 6.801 hasta el 6/11/2026.
- **Por idioma de la fuente:** español 7.049, inglés 6.067, portugués 4.216, italiano 1.733, polaco 427 y alemán 325.
- **En más de un track:** 759 notas.
- **Calidad del texto:** todas las notas tienen cuerpo. La mediana es de 4.460 caracteres y 28 tienen menos de 300.
- **Tipo de voz:** 18.161 de medio especializado, 1.269 de diario y 387 de opinión.
- **Aporte de las 29 fuentes sumadas para soluciones:** 11.061 notas, el 56 %.
- **Coincidencia con los datasets de problemas:** 5.096 notas también están en residuos, 1.367 en biodiversidad y 508 en movilidad.

## Pros

- **Cubre los cuatro tracks en un solo archivo:** la columna `tracks` indica a cuáles pertenece cada nota, sin filas repetidas.
- **Período parejo:** todas las fuentes se buscaron desde 2024, y los tres años tienen un volumen parecido.
- **Más enfocado:** el filtro por título o bajada quitó gran parte del ruido. De TN quedó el 6 % de sus notas desde 2024, y de El Doce, el 2 %.
- **Menos dependencia de un medio:** las 5 mayores fuentes reúnen el 31 % de las notas.
- **Texto completo:** todas las notas tienen cuerpo, sin el pie de suscripción de cada fuente.
- **Reversible mientras exista `crudo/`:** se puede repetir la separación con otras raíces sin volver a descargar.

## Contras

- **Una nota no es una solución:** el mismo producto puede aparecer muchas veces, y todavía no se extrajeron soluciones.
- **Precisión variable por track:** en una lectura rápida de 40 títulos por track, parecían soluciones aplicadas cerca de la mitad en residuos y movilidad, unas 4 de cada 10 en agro y unas 2 o 3 de cada 10 en biodiversidad. Es una estimación informal de una sola lectura, solo por título.
- **Falsos positivos por raíces:** "How to perform chip harvesting" (reciclaje de chips) cayó en agro, "Preocupación por los trenes" en biodiversidad y "Hotel na Vila Mariana" en movilidad.
- **Soluciones perdidas:** una nota que nombra el track solo en el cuerpo se descarta, y lo mismo pasa si usa palabras fuera del diccionario. Esa pérdida no está medida.
- **Volumen que depende de las fuentes:** residuos tiene más notas en parte porque muchas fuentes se eligieron por ese tema. Que un track tenga menos notas no prueba que tenga menos soluciones.
- **Biodiversidad y movilidad dependen de pocos medios:** Mongabay en inglés aporta 685 de 2.378 en biodiversidad, y Mobilidade Sampa 1.510 de 4.828 en movilidad.
- **Poco local fuera de agro:** Córdoba suma 62 notas en total, y más de la mitad de las de medios argentinos son de agro.
- **Cobertura parcial en grandes medios:** Infobae y Clarín bajaron solo lo prioritario, y el tag `tecnologia` de Infobae llega hasta febrero de 2025 por un tope de 10.000 notas.
- **Sesgo de anuncio:** lo publicado muestra que algo se anunció, no que funcione, que se haya adoptado o que siga activo. Tampoco muestra lo que no llegó a la prensa.
- **Duplicados entre medios sin detectar:** la limpieza quitó los títulos y cuerpos repetidos, pero no detecta comunicados reescritos ni traducidos por otro medio.
- **Datos crudos solo en una máquina:** `crudo/` ocupa 1,8 GB y no está en Git. Si se borra, cambiar el filtro exige volver a descargar.

## Limitaciones de usarlos juntos

- **Agro no tiene dataset de problemas:** el contraste se puede hacer en residuos, biodiversidad y movilidad. Biodiversidad y movilidad se armaron con otro criterio y sin fecha mínima en los diarios.
- **Se pisan:** 4.738 de las 6.811 notas del track de residuos también están en el dataset de residuos. Una misma nota no debería contarse como evidencia independiente en los dos lados.
- **Comparten sesgos:** muchas fuentes son las mismas, con los mismos intereses editoriales.
- **Comparten período solo desde 2024:** antes de ese año no hay soluciones para comparar.

## Pendiente antes de analizar

Vale para todos los datasets.

1. Filtrar el ruido y medir la utilidad con una muestra revisada por el equipo.
2. Detectar notas reescritas o traducidas, y decidir qué hacer con las que están en más de un dataset.
3. Clasificar cada nota en problema, solución, ambas u otra.
4. Extraer las soluciones de las notas y agruparlas.
5. Decidir si se conserva `crudo/` y dónde, antes de borrarlo.

## Cómo se midió

- **Conteos:** directos sobre `data/soluciones.parquet` del 8/11/2026. Las etapas anteriores a la limpieza vienen del análisis del 6/11. Las notas sin bajar de Infobae y Clarín vienen de [`contexto-pipeline.md`](contexto-pipeline.md).
- **Por track:** una nota cuenta en cada track de su columna `tracks`.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por dominio o medio, sin un campo de país en los datos.
- **Coincidencias entre datasets:** por URL.
- **Muestras de títulos:** las leyó Claude, una sola vez y sin revisión del equipo. Sirven como orientación.
