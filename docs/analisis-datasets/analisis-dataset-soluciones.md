# Análisis del dataset de soluciones tecnológicas

Foto del 6/11/2026, antes de filtrar, deduplicar o clasificar. Las cifras cambian cuando esas etapas se ejecuten.

| | Soluciones tecnológicas |
|---|---|
| **Pregunta que ayuda a responder** | Qué soluciones tecnológicas se publican en cada track |
| **Ubicación** | `data/soluciones/<track>/` |
| **Notas** | 20.131 únicas (20.914 filas sumando los tracks) |
| **Fuentes** | 62 |
| **Período** | 2024 a 2026 |
| **Criterio para quedar** | Coincidir con la búsqueda, ser de 2024 en adelante y tener un track en título o bajada |
| **Tamaño aproximado** | 79 MB |

Para el dataset de residuos, ver [el análisis de residuos](analisis-dataset-residuos.md).

## Cifras

| Etapa | Notas | Qué pasa |
|---|---:|---|
| Descarga en `crudo/` (fuera de Git) | 94.768 | Todo lo que coincidió con los términos |
| Desde 2024 | 80.180 | Se quitan 14.588 anteriores |
| Con track en título o bajada | 20.131 | Se quita el 75 % de las que quedaban |

| Track | Filas | Fuentes | Fuentes con 100 o más | Las 3 mayores reúnen | Medios argentinos | Córdoba | También en el dataset de residuos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Residuos | 7.002 | 61 | 20 | 33 % | 245 | 7 | 4.878 |
| Agro | 6.651 | 57 | 15 | 46 % | 2.646 | 16 | 278 |
| Movilidad | 4.852 | 57 | 11 | 53 % | 573 | 52 | 133 |
| Biodiversidad | 2.409 | 50 | 6 | 45 % | 152 | 1 | 185 |

- **Por año:** 6.200 en 2024, 7.073 en 2025 y 6.858 hasta el 6/11/2026.
- **Por idioma de la fuente:** español 7.139, inglés 6.266, portugués 4.238, italiano 1.736, polaco 427 y alemán 325.
- **En más de un track:** 765 notas.
- **Calidad del texto:** 20 notas sin cuerpo y 215 con menos de 300 caracteres. La mediana es de 4.429 caracteres.
- **Aporte de las 29 fuentes sumadas para soluciones:** 11.129 notas, el 55 %.
- **Coincidencia con residuos:** 5.244 URL están en los dos datasets.

## Pros

- **Cubre los cuatro tracks:** cada uno tiene su carpeta y un Parquet por fuente.
- **Período parejo:** todas las fuentes se buscaron desde 2024, y los tres años tienen un volumen parecido.
- **Más enfocado:** el filtro por título o bajada quitó gran parte del ruido. De TN quedó el 6 % de sus notas desde 2024, y de El Doce, el 2 %.
- **Menos dependencia de un medio:** las 5 mayores fuentes reúnen el 31 % de las notas.
- **Texto casi completo:** casi todas las notas tienen cuerpo.
- **Reversible mientras exista `crudo/`:** se puede repetir la separación con otras raíces sin volver a descargar.

## Contras

- **Una nota no es una solución:** el mismo producto puede aparecer muchas veces, y todavía no se extrajeron soluciones.
- **Precisión variable por track:** en una lectura rápida de 40 títulos por track, parecían soluciones aplicadas cerca de la mitad en residuos y movilidad, unas 4 de cada 10 en agro y unas 2 o 3 de cada 10 en biodiversidad. Es una estimación informal de una sola lectura, solo por título.
- **Falsos positivos por raíces:** "How to perform chip harvesting" (reciclaje de chips) cayó en agro, "Preocupación por los trenes" en biodiversidad y "Hotel na Vila Mariana" en movilidad.
- **Soluciones perdidas:** una nota que nombra el track solo en el cuerpo se descarta, y lo mismo pasa si usa palabras fuera del diccionario. Esa pérdida no está medida.
- **Volumen que depende de las fuentes:** residuos tiene más notas en parte porque muchas fuentes se eligieron por ese tema. Que un track tenga menos notas no prueba que tenga menos soluciones.
- **Biodiversidad y movilidad dependen de pocos medios:** Mongabay en inglés aporta 685 de 2.409 en biodiversidad, y Mobilidade Sampa 1.513 de 4.852 en movilidad.
- **Poco local fuera de agro:** Córdoba suma 76 filas en total, y más de la mitad de las de medios argentinos son de agro.
- **Cobertura parcial en grandes medios:** Infobae y Clarín bajaron solo lo prioritario, y el tag `tecnologia` de Infobae llega hasta febrero de 2025 por un tope de 10.000 notas.
- **Sesgo de anuncio:** lo publicado muestra que algo se anunció, no que funcione, que se haya adoptado o que siga activo. Tampoco muestra lo que no llegó a la prensa.
- **Duplicados sin medir del todo:** 26 títulos exactos aparecen en más de una fuente, y los comunicados reescritos no se detectan.
- **Datos crudos solo en una máquina:** `crudo/` ocupa 1,8 GB y no está en Git. Si se borra, cambiar el filtro exige volver a descargar.

## Limitaciones de usarlos juntos

- **El contraste completo hoy solo se puede hacer en residuos:** agro, movilidad y biodiversidad tienen notas de soluciones, pero no un dataset de problemas equivalente. Desde el 6/11 hay uno de [biodiversidad](analisis-dataset-biodiversidad.md), armado con otro criterio (señales de problema) y sin fecha mínima en los diarios.
- **Se pisan:** 4.878 de las 7.002 filas del track de residuos también están en el dataset de residuos. Una misma nota no debería contarse como evidencia independiente en los dos lados.
- **Comparten sesgos:** muchas fuentes son las mismas, con los mismos intereses editoriales.
- **Comparten período solo desde 2024:** antes de ese año no hay soluciones para comparar.

## Pendiente antes de analizar

Vale para ambos datasets.

1. Filtrar el ruido y medir la utilidad con una muestra revisada por el equipo.
2. Deduplicar entre fuentes y entre datasets, más allá del título exacto.
3. Clasificar cada nota en problema, solución, ambas u otra.
4. Extraer las soluciones de las notas y agruparlas.
5. Decidir si se conserva `crudo/` y dónde, antes de borrarlo.

## Cómo se midió

- **Conteos:** directos sobre los Parquet del 6/11/2026. Las notas sin bajar de Infobae y Clarín vienen de [`contexto-pipeline.md`](contexto-pipeline.md).
- **Raíces en título o bajada:** se contaron con las raíces de todos los idiomas juntas, así que es una aproximación.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por dominio o medio, sin un campo de país en los datos.
- **Muestras de títulos:** las leyó Claude, una sola vez y sin revisión del equipo. Sirven como orientación.
