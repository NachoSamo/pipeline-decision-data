# Análisis del dataset de problemáticas de movilidad sustentable

Foto del 6/11/2026, antes de filtrar, deduplicar o clasificar. Las cifras cambian cuando esas etapas se ejecuten.
CBA24N se cortó a mitad de camino: tiene 731 de las 1.083 notas que se iban a bajar.

| | Problemáticas de movilidad sustentable |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de movilidad se publican, quién los plantea y con qué voz |
| **Ubicación** | `data/movilidad/` |
| **Notas** | 67.399 únicas |
| **Fuentes** | 10 |
| **Período** | 2008 a 2026. Las fuentes con API de WordPress, desde 2021 |
| **Criterio para quedar** | Coincidir con la búsqueda; sin filtro posterior. Las señales marcan, no descartan |
| **Tamaño aproximado** | 116 MB |

El circuito y las decisiones están en [`circuito-problematicas.md`](../circuito-problematicas.md), y cómo se baja cada fuente, en [`scrapping-webs.md`](../scrapping-webs.md#dataset-de-problemáticas-biodiversidad-y-movilidad). Para biodiversidad, ver [el análisis de biodiversidad](analisis-dataset-biodiversidad.md).

## Cifras

| Fuente | Notas | Con raíces del tema en título o bajada |
|---|---:|---:|
| TN | 30.387 | 32 % |
| El Doce | 21.622 | 32 % |
| Clarín | 8.468 | 49 % |
| La Nación | 2.034 | 98 % |
| Grist | 1.992 | no medido (inglés) |
| CicloVivo | 1.188 | no medido (portugués) |
| CBA24N | 731 | 100 % |
| Visión Sustentable | 469 | 19 % |
| Ecoticias | 437 | 98 % |
| Ecomundo | 71 | 14 % |

- **Por idioma de la fuente:** español 64.219, inglés 1.992 y portugués 1.188.
- **Con raíces del tema en título o bajada:** 23.898 de las 64.219 notas en español (37 %).
- **Argentina:** 63.782 notas de 7 medios, con 23.471 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N, con 22.353 notas y 7.674 con raíces del tema en título o bajada. CBA24N aporta 731, casi todas con el tema en título o bajada porque se eligieron por la URL.
- **Por año:** entre 2.587 y 5.791 por año de 2016 a 2023, 9.455 en 2024, 9.500 en 2025 y 8.987 hasta el 6/11/2026.
- **Calidad del texto:** 12.496 notas sin cuerpo (19 %), casi todas de El Doce (7.215) y TN (5.253). La mediana es de 1.959 caracteres.
- **Señales:** 27.936 notas (41 %) tienen alguna señal de problema y 14.441 (21 %), alguna de opinión o voz especializada.
- **Tipo de voz:** 62.711 de diario, 4.139 de medio especializado y 549 de opinión, sobre todo de TN (296), El Doce (139) y Clarín (71).
- **Coincidencia con soluciones:** 341 de las 4.852 notas de `data/soluciones/movilidad/` también están acá.

## Pros

- **Muy local:** casi todo es de medios argentinos, y El Doce y CBA24N aportan 22.353 notas de Córdoba. Hay términos propios como SiBus, TAMSE, Coniferal y Circunvalación.
- **Volumen alto:** aun quedándose con las notas con el tema en título o bajada, hay unas 24.000 en español.
- **Las señales separan más que en biodiversidad:** marcan 41 % de problema y 21 % de opinión, así que sirven más para priorizar, aunque falta medir si aciertan.
- **Sitemaps precisos:** en La Nación y CBA24N casi todas las notas tienen el tema en título o bajada, porque se eligieron por la URL.
- **Poca superposición con soluciones:** comparten 341 notas.

## Contras

- **Mucho ruido:** en una lectura rápida de 40 títulos al azar, solo unas 6 parecían tratar sobre movilidad. Entraron espectáculos, deportes, policiales y cronogramas de pagos por palabras como "tránsito", "colectivo" o "boleto". Es una estimación informal, no una medición.
- **Clarín trae ruido:** la mitad de sus notas (51 %) no tiene el tema en título ni bajada. Probablemente entraron por la etiqueta amplia "autos".
- **Concentración extrema:** TN y El Doce reúnen 52.009 notas (77 %). Contar sin ponderar es casi contar lo que publican esos dos medios.
- **Cuerpo faltante:** casi 1 de cada 5 notas no tiene cuerpo, y las que sí lo tienen son más cortas que en biodiversidad.
- **"impacto" marca de más:** sacarlo deja afuera 4.005 notas con señal de problema.
- **Serie temporal engañosa:** el salto de 2023 a 2024 no está explicado. Puede venir de cómo ordenan los buscadores de TN y El Doce, que tienen tope de páginas, y no de un aumento del tema.
- **Cobertura parcial:** Infobae no se corrió (decisión del 6/11): sus etiquetas de movilidad son muy amplias y tardaría más de 8 horas. En CBA24N se listaron solo las 1.083 notas con raíces específicas y se bajaron 731: el sitio respondió 429 dos veces y se decidió parar (6/11). Mongabay quedó afuera por ser de biodiversidad.
- **Poco internacional:** Grist, CicloVivo y Ecoticias suman 3.617 notas, el 5 %.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema. Buscar con palabras de problema sesga hacia lo conflictivo y lo visible.

## Cómo se midió

- **Conteos:** directos sobre los Parquet del 6/11/2026.
- **Raíces en título o bajada:** con `RAICES_MOVILIDAD`, que están en español. Por eso no se midieron las fuentes en inglés y portugués.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por medio, sin un campo de país en los datos.
- **`keywords_core`:** usa las expresiones de residuos, así que no sirve para este dataset.
- **Duplicados:** solo se comparó el título exacto: 26 títulos aparecen en más de una fuente.
- **Muestras de títulos:** se leyeron una sola vez y no las revisó el equipo. Sirven como orientación.
