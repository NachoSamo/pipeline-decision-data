# Análisis del dataset de problemáticas de biodiversidad

Foto del 8/11/2026, después de la limpieza con [`limpiar.py`](../../scripts/limpiar.py) y antes de filtrar por utilidad o clasificar. Las cifras cambian cuando se ejecuten esas etapas.

| | Problemáticas de biodiversidad |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de biodiversidad se publican, quién los plantea y con qué voz |
| **Ubicación** | `data/biodiversidad.parquet` |
| **Notas** | 33.620 (eran 35.951 antes de la limpieza) |
| **Fuentes** | 13 |
| **Período** | 2010 a 2026. Las fuentes con API de WordPress, desde 2021 |
| **Criterio para quedar** | Coincidir con la búsqueda y pasar la limpieza. No hay filtro por tema |
| **Tamaño aproximado** | 72 MB |

El circuito y las decisiones están en [`circuito-problematicas.md`](../circuito-problematicas.md), cómo se baja cada fuente en [`scrapping-webs.md`](../scrapping-webs.md#dataset-de-problemáticas-biodiversidad-y-movilidad) y los criterios de limpieza en [`contexto-pipeline.md`](contexto-pipeline.md#limpieza-y-consolidación-8112026).

## Limpieza

| Iniciales | Título corto | Sin cuerpo | Seriado | Título repetido | Cuerpo repetido | Finales |
|---:|---:|---:|---:|---:|---:|---:|
| 35.951 | 40 | 1.957 | 173 | 97 | 64 | 33.620 |

Las notas sin cuerpo eran casi todas videos de TN y El Doce. Los títulos seriados son sobre todo los resúmenes semanales "Lo más leído" de Mongabay.

## Cifras

| Fuente | Notas | Con raíces del tema en título o bajada |
|---|---:|---:|
| Mongabay en inglés | 8.190 | no medido (inglés) |
| Infobae | 7.072 | 65 % |
| Mongabay | 4.045 | 50 % |
| TN | 2.695 | 49 % |
| Clarín | 2.419 | 45 % |
| CicloVivo | 2.360 | no medido (portugués) |
| Grist | 2.354 | no medido (inglés) |
| Ecoticias | 1.989 | 98 % |
| El Doce | 965 | 30 % |
| La Nación | 700 | 98 % |
| CBA24N | 465 | 100 % |
| Visión Sustentable | 285 | 16 % |
| Ecomundo | 81 | 32 % |

- **Por idioma de la fuente:** español 20.716, inglés 10.544 y portugués 2.360.
- **Con raíces del tema en título o bajada:** 12.508 de las 20.716 notas en español (60 %).
- **Argentina:** 14.682 notas de 8 medios, con 8.529 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N suman 1.430 notas, con 759 que tienen raíces del tema en título o bajada.
- **Por año:** 1.173 en 2020, entre 4.216 y 6.677 por año de 2021 a 2025, y 6.121 hasta el 6/11/2026.
- **Calidad del texto:** todas las notas tienen cuerpo. La mediana es de 5.419 caracteres y 53 tienen menos de 300.
- **Tipo de voz:** 18.675 de medio especializado, 14.131 de diario y 814 de opinión. De las de opinión, 606 son columnas de Mongabay en inglés y 92, de Infobae.
- **Coincidencia con soluciones:** 1.014 de las 2.378 notas del track de biodiversidad de `data/soluciones.parquet` también están acá.

## Pros

- **Mezcla de voces:** combina medios especializados en biodiversidad, diarios nacionales y medios de Córdoba.
- **Texto completo:** todas las notas tienen cuerpo, con notas largas.
- **Voz identificada:** cada nota guarda `tipo_voz`, con la misma regla en los cuatro datasets.
- **Presencia local:** hay notas de Córdoba con términos como Ansenuza, Mar Chiquita, Sierras de Córdoba y Chaco seco.
- **Fuentes precisas:** en La Nación y CBA24N casi todas las notas tienen el tema en título o bajada, porque se eligieron por la URL. En Infobae, el 65 %, porque se bajaron solo las etiquetas del tema y las notas de etiquetas amplias con el tema en título o bajada.

## Contras

- **Ruido:** en una lectura rápida de 40 títulos al azar, antes de sumar Infobae, algo más de la mitad parecía tratar sobre biodiversidad. Entraron crímenes, fútbol y política por palabras como "extinción" (de dominio) o "desaparición". Muchas de las relevantes son descubrimientos o curiosidades, no problemas. La limpieza no filtra por tema, así que ese ruido sigue. Es una estimación informal, no una medición.
- **Sin señales de problema:** `senal_problema` y `senal_opinion` se eliminaron el 8/11. Marcaban el 78 % y el 67 % de las notas, con palabras genéricas como "impacto" o "riesgo", así que no separaban. Distinguir problemas queda para la clasificación.
- **Concentración:** las 5 fuentes más grandes reúnen el 73 % de las notas, y Mongabay en inglés sola, el 24 %. Contar sin ponderar favorece a ese medio.
- **Grist trae poco del tema:** es un medio de clima y ambiente, y la búsqueda devuelve notas amplias. Falta medirlo con raíces en inglés.
- **Serie temporal engañosa:** el salto de 2020 a 2021 viene de que las fuentes con WordPress se buscaron desde 2021, no de un aumento del tema.
- **Cobertura parcial:** en Infobae se bajó solo lo prioritario, y quedaron sin bajar 15.205 notas de etiquetas amplias, como "animales". De las prioritarias faltan 2. Infobae incluye ediciones de otros países. Las candidatas de opinión, ONG y política del circuito no se probaron.
- **Se pisa con otros datasets:** 1.367 notas también están en soluciones, 2.637 en residuos y 1.535 en movilidad. Una misma nota no debería contar como evidencia independiente en dos lados.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema. Buscar con palabras de problema sesga hacia lo conflictivo y lo visible.

## Cómo se midió

- **Conteos:** directos sobre `data/biodiversidad.parquet` del 8/11/2026.
- **Raíces en título o bajada:** con `RAICES_BIODIVERSIDAD`, que están en español. Por eso no se midieron las fuentes en inglés y portugués.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por medio, sin un campo de país en los datos. Mongabay (Latam) no se contó como argentino; Infobae sí, aunque tenga ediciones de otros países.
- **`keywords_core`:** usa las expresiones de residuos, así que no sirve para este dataset.
- **Coincidencias entre datasets:** por URL.
- **Muestras de títulos:** se leyeron una sola vez y no las revisó el equipo. Sirven como orientación.
