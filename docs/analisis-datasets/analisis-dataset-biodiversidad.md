# Análisis del dataset de problemáticas de biodiversidad

Foto del 6/11/2026, antes de filtrar, deduplicar o clasificar. Las cifras cambian cuando esas etapas se ejecuten.

| | Problemáticas de biodiversidad |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de biodiversidad se publican, quién los plantea y con qué voz |
| **Ubicación** | `data/biodiversidad/` |
| **Notas** | 35.951 únicas |
| **Fuentes** | 13 |
| **Período** | 2008 a 2026. Las fuentes con API de WordPress, desde 2021 |
| **Criterio para quedar** | Coincidir con la búsqueda; sin filtro posterior. Las señales marcan, no descartan |
| **Tamaño aproximado** | 160 MB |

El circuito y las decisiones están en [`circuito-problematicas.md`](../circuito-problematicas.md), y cómo se baja cada fuente, en [`scrapping-webs.md`](../scrapping-webs.md#dataset-de-problemáticas-biodiversidad-y-movilidad).

## Cifras

| Fuente | Notas | Con raíces del tema en título o bajada |
|---|---:|---:|
| Mongabay en inglés | 8.192 | no medido (inglés) |
| Infobae | 7.103 | 65 % |
| Mongabay | 4.214 | 50 % |
| TN | 3.888 | 46 % |
| Clarín | 2.521 | 44 % |
| Grist | 2.367 | no medido (inglés) |
| CicloVivo | 2.360 | no medido (portugués) |
| Ecoticias | 1.990 | 98 % |
| El Doce | 1.753 | 27 % |
| La Nación | 715 | 97 % |
| CBA24N | 482 | 99 % |
| Visión Sustentable | 285 | 16 % |
| Ecomundo | 81 | 32 % |

- **Por idioma de la fuente:** español 23.032, inglés 10.559 y portugués 2.360.
- **Con raíces del tema en título o bajada:** 13.293 de las 23.032 notas en español (58 %).
- **Argentina:** 16.828 notas de 8 medios, con 9.229 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N suman 2.235 notas, con 956 que tienen raíces del tema en título o bajada.
- **Por año:** 1.327 en 2020, entre 4.306 y 6.774 por año de 2021 a 2025, y 6.229 hasta el 6/11/2026.
- **Calidad del texto:** 1.976 notas sin cuerpo, casi todas de TN (1.157) y El Doce (784). La mediana es de 5.116 caracteres.
- **Señales:** 28.092 notas (78 %) tienen alguna señal de problema y 24.202 (67 %), alguna de opinión o voz especializada.
- **Tipo de voz:** 18.860 de medio especializado, 16.271 de diario y 820 de opinión. De las de opinión, 606 son columnas de Mongabay en inglés y 92, de Infobae.
- **Coincidencia con soluciones:** 1.033 de las 2.409 notas de `data/soluciones/biodiversidad/` también están acá.

## Pros

- **Mezcla de voces:** combina medios especializados en biodiversidad, diarios nacionales y medios de Córdoba.
- **Texto completo:** el 95 % de las notas tiene cuerpo, con notas largas.
- **Marcas para filtrar:** cada nota guarda `senal_problema`, `senal_opinion` y `tipo_voz`, y se pueden recalcular sin volver a descargar.
- **Presencia local:** hay notas de Córdoba con términos como Ansenuza, Mar Chiquita, Sierras de Córdoba y Chaco seco.
- **Fuentes precisas:** en La Nación y CBA24N casi todas las notas tienen el tema en título o bajada, porque se eligieron por la URL. En Infobae, el 65 %, porque se bajaron solo las etiquetas del tema y las notas de etiquetas amplias con el tema en título o bajada.

## Contras

- **Ruido:** en una lectura rápida de 40 títulos al azar, antes de sumar Infobae, algo más de la mitad parecía tratar sobre biodiversidad. Entraron crímenes, fútbol y política por palabras como "extinción" (de dominio) o "desaparición". Muchas de las relevantes son descubrimientos o curiosidades, no problemas. Es una estimación informal, no una medición.
- **Las señales casi no separan:** 3 de cada 4 notas tienen señal de problema y 2 de cada 3, de opinión. Las señales de opinión más frecuentes son "cientific" y "biolog", que en biodiversidad aparecen aunque no hable un especialista. "impacto" marca notas de empresas; sacarlo solo deja afuera 997 notas.
- **Concentración:** las 5 fuentes más grandes reúnen el 72 % de las notas, y Mongabay en inglés sola, el 23 %. Contar sin ponderar favorece a ese medio.
- **Grist trae poco del tema:** es un medio de clima y ambiente, y la búsqueda devuelve notas amplias. Falta medirlo con raíces en inglés.
- **Serie temporal engañosa:** el salto de 2020 a 2021 viene de que las fuentes con WordPress se buscaron desde 2021, no de un aumento del tema.
- **Cobertura parcial:** en Infobae se bajó solo lo prioritario, y quedaron sin bajar 15.205 notas de etiquetas amplias, como "animales". De las prioritarias faltan 2. Infobae incluye ediciones de otros países. Las candidatas de opinión, ONG y política del circuito no se probaron.
- **Se pisa con soluciones:** 1.033 notas están en los dos datasets. Una misma nota no debería contar como evidencia independiente de un problema y de una solución.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema. Buscar con palabras de problema sesga hacia lo conflictivo y lo visible.

## Cómo se midió

- **Conteos:** directos sobre los Parquet del 6/11/2026.
- **Raíces en título o bajada:** con `RAICES_BIODIVERSIDAD`, que están en español. Por eso no se midieron las fuentes en inglés y portugués.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por medio, sin un campo de país en los datos. Mongabay (Latam) no se contó como argentino; Infobae sí, aunque tenga ediciones de otros países.
- **`keywords_core`:** usa las expresiones de residuos, así que no sirve para este dataset.
- **Duplicados:** solo se comparó el título exacto: 15 títulos aparecen en más de una fuente.
- **Muestras de títulos:** se leyeron una sola vez y no las revisó el equipo. Sirven como orientación.
