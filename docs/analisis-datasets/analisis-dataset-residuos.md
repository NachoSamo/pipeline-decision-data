# Análisis del dataset de residuos

Foto del 6/11/2026, antes de filtrar, deduplicar o clasificar. Las cifras cambian cuando esas etapas se ejecuten.

| | Residuos |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de residuos se publican |
| **Ubicación** | `data/residuos/` |
| **Notas** | 47.944 únicas |
| **Fuentes** | 33 |
| **Período** | 2007 a 2026 |
| **Criterio para quedar** | Coincidir con la búsqueda; sin filtro posterior |
| **Tamaño aproximado** | 116 MB |

Para el dataset de soluciones y la comparación entre ambos, ver [el análisis de soluciones](analisis-dataset-soluciones.md).

## Cifras

- **Con cuerpo:** 41.140 notas. A las otras 6.804 les falta casi siempre en TN (4.413) y El Doce (2.359).
- **Con mención del tema:** 29.413 tienen cuerpo y mención, según `relevante`. De ellas, 20.045 también lo mencionan en título o bajada (medición del 5/11).
- **Por idioma de la fuente:** español 31.298, inglés 10.601, italiano 2.827, portugués 1.416, polaco 943 y alemán 859.
- **Argentina:** 26.149 notas de 9 medios, con 7.783 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N suman 6.607 notas, con 1.636 que tienen raíces del tema en título o bajada.
- **Por año:** 1.793 en 2023, 9.399 en 2024, 10.335 en 2025 y 9.709 hasta noviembre de 2026.

## Pros

- **Volumen de sobra para probar el método:** el objetivo de 10.000 notas se supera aun quedándose con las que mencionan el tema en título o bajada, aunque falta medir cuántas son útiles.
- **Mezcla de voces:** combina medios generalistas, medios especializados y organizaciones del sector.
- **Local e internacional:** tiene presencia argentina y cordobesa, y fuentes en seis idiomas.
- **Fuentes más antiguas:** ocho fuentes llegan antes de 2024, lo que permite mirar persistencia en esos medios.
- **Poco cuerpo vacío fuera de dos medios:** el faltante se concentra en TN y El Doce.
- **Listo para filtrar:** cada fila conserva fuente, fecha, cuerpo y los términos que coincidieron.

## Contras

- **Mucho ruido:** en una lectura rápida de 60 títulos al azar, cerca de la mitad parecía tratar sobre residuos. Hay notas de espectáculos, recetas o política que coinciden por palabras como "camioneros" o "basura". Es una estimación informal, no una medición.
- **Ruido concentrado:** TN y El Doce aportan 18.421 notas (38 %), y solo 3.676 (20 %) tienen raíces del tema en título o bajada. En el resto son 17.472 de 29.523 (59 %).
- **Concentración:** las 5 fuentes más grandes reúnen el 56 % de las notas. Contar sin ponderar favorece a esos medios.
- **Serie temporal engañosa:** 18.501 notas son anteriores a 2024 o sin fecha, y salen de solo ocho fuentes; las demás arrancan en 2024. El salto de 2023 a 2024 viene de cómo se buscó, no de un aumento real del tema.
- **Cobertura parcial:** en Infobae y Clarín se bajó solo lo prioritario, y quedaron sin bajar 5.781 y 1.894 notas. Falta La Voz, y Futuro Sustentable y Cadena 3 no aportan datos.
- **Duplicados sin medir del todo:** solo se comparó el título exacto (25 títulos en más de una fuente). No detecta notas reescritas, traducidas ni el mismo hecho contado por varios medios.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema.

## Cómo se midió

- **Conteos:** directos sobre los Parquet del 6/11/2026. Las cifras de 29.413 y 20.045, y las notas sin bajar de Infobae y Clarín, vienen de [`contexto-pipeline.md`](contexto-pipeline.md).
- **Raíces en título o bajada:** se contaron con las raíces de todos los idiomas juntas, así que es una aproximación.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por dominio o medio, sin un campo de país en los datos.
- **Muestras de títulos:** las leyó Claude, una sola vez y sin revisión del equipo. Sirven como orientación.
