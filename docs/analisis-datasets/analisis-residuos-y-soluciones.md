# Análisis de los datasets de residuos y soluciones

Foto del 6/11/2026, antes de filtrar, deduplicar o clasificar. Las cifras cambian cuando esas etapas se ejecuten.

| | Residuos | Soluciones tecnológicas |
|---|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de residuos se publican | Qué soluciones tecnológicas se publican en cada track |
| **Ubicación** | `data/residuos/` | `data/soluciones/<track>/` |
| **Notas** | 47.944 | 20.131 únicas (20.914 filas sumando los tracks) |
| **Fuentes** | 33 | 62 |
| **Período** | 2007 a 2026 | 2024 a 2026 |
| **Criterio para quedar** | Coincidir con la búsqueda; sin filtro posterior | Coincidir con la búsqueda, ser de 2024 en adelante y tener un track en título o bajada |
| **Tamaño aproximado** | 116 MB | 79 MB |

Los volúmenes no se pueden comparar de forma directa, porque el criterio de entrada es distinto. Las URL son únicas dentro de cada dataset.

## Dataset de residuos

### Cifras

- **Con cuerpo:** 41.140 notas. A las otras 6.804 les falta casi siempre en TN (4.413) y El Doce (2.359).
- **Con mención del tema:** 29.413 tienen cuerpo y mención, según `relevante`. De ellas, 20.045 también lo mencionan en título o bajada (medición del 5/11).
- **Por idioma de la fuente:** español 31.298, inglés 10.601, italiano 2.827, portugués 1.416, polaco 943 y alemán 859.
- **Argentina:** 26.149 notas de 9 medios, con 7.783 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N suman 6.607 notas, con 1.636 que tienen raíces del tema en título o bajada.
- **Por año:** 1.793 en 2023, 9.399 en 2024, 10.335 en 2025 y 9.709 hasta noviembre de 2026.

### Pros

- **Volumen de sobra para probar el método:** el objetivo de 10.000 notas se supera aun quedándose con las que mencionan el tema en título o bajada, aunque falta medir cuántas son útiles.
- **Mezcla de voces:** combina medios generalistas, medios especializados y organizaciones del sector.
- **Local e internacional:** tiene presencia argentina y cordobesa, y fuentes en seis idiomas.
- **Fuentes más antiguas:** ocho fuentes llegan antes de 2024, lo que permite mirar persistencia en esos medios.
- **Poco cuerpo vacío fuera de dos medios:** el faltante se concentra en TN y El Doce.
- **Listo para filtrar:** cada fila conserva fuente, fecha, cuerpo y los términos que coincidieron.

### Contras

- **Mucho ruido:** en una lectura rápida de 60 títulos al azar, cerca de la mitad parecía tratar sobre residuos. Hay notas de espectáculos, recetas o política que coinciden por palabras como "camioneros" o "basura". Es una estimación informal, no una medición.
- **Ruido concentrado:** TN y El Doce aportan 18.421 notas (38 %), y solo 3.676 (20 %) tienen raíces del tema en título o bajada. En el resto son 17.472 de 29.523 (59 %).
- **Concentración:** las 5 fuentes más grandes reúnen el 56 % de las notas. Contar sin ponderar favorece a esos medios.
- **Serie temporal engañosa:** 18.501 notas son anteriores a 2024 o sin fecha, y salen de solo ocho fuentes; las demás arrancan en 2024. El salto de 2023 a 2024 viene de cómo se buscó, no de un aumento real del tema.
- **Cobertura parcial:** en Infobae y Clarín se bajó solo lo prioritario, y quedaron sin bajar 5.781 y 1.894 notas. Falta La Voz, y Futuro Sustentable y Cadena 3 no aportan datos.
- **Duplicados sin medir del todo:** solo se comparó el título exacto (25 títulos en más de una fuente). No detecta notas reescritas, traducidas ni el mismo hecho contado por varios medios.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema.

## Dataset de soluciones tecnológicas

### Cifras

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

### Pros

- **Cubre los cuatro tracks:** cada uno tiene su carpeta y un Parquet por fuente.
- **Período parejo:** todas las fuentes se buscaron desde 2024, y los tres años tienen un volumen parecido.
- **Más enfocado:** el filtro por título o bajada quitó gran parte del ruido. De TN quedó el 6 % de sus notas desde 2024, y de El Doce, el 2 %.
- **Menos dependencia de un medio:** las 5 mayores fuentes reúnen el 31 % de las notas.
- **Texto casi completo:** casi todas las notas tienen cuerpo.
- **Reversible mientras exista `crudo/`:** se puede repetir la separación con otras raíces sin volver a descargar.

### Contras

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

- **El contraste completo hoy solo se puede hacer en residuos:** agro, movilidad y biodiversidad tienen notas de soluciones, pero no un dataset de problemas equivalente.
- **Se pisan:** 4.878 de las 7.002 filas del track de residuos también están en el dataset de residuos. Una misma nota no debería contarse como evidencia independiente en los dos lados.
- **Comparten sesgos:** muchas fuentes son las mismas, con los mismos intereses editoriales.
- **Comparten período solo desde 2024:** antes de ese año no hay soluciones para comparar.

## Pendiente antes de analizar

1. Filtrar el ruido y medir la utilidad con una muestra revisada por el equipo.
2. Deduplicar entre fuentes y entre datasets, más allá del título exacto.
3. Clasificar cada nota en problema, solución, ambas u otra.
4. Extraer las soluciones de las notas y agruparlas.
5. Decidir si se conserva `crudo/` y dónde, antes de borrarlo.

## Cómo se midió

- **Conteos:** directos sobre los Parquet del 6/11/2026. Las cifras de 29.413 y 20.045, y las notas sin bajar de Infobae y Clarín, vienen de [`contexto-pipeline.md`](contexto-pipeline.md).
- **Raíces en título o bajada:** en residuos se contó con las raíces de todos los idiomas juntas, así que es una aproximación.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por dominio o medio, sin un campo de país en los datos.
- **Muestras de títulos:** las leyó Claude, una sola vez y sin revisión del equipo. Sirven como orientación.
