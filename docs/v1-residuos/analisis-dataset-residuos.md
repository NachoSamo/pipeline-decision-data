# Análisis del dataset de residuos

Foto del 8/11/2026, después de la limpieza con [`limpiar.py`](../../scripts/limpiar.py) y antes de filtrar por utilidad o clasificar. Las cifras cambian cuando se ejecuten esas etapas.

| | Residuos |
|---|---|
| **Pregunta que ayuda a responder** | Qué problemas de residuos se publican |
| **Ubicación** | `data/residuos.parquet` |
| **Notas** | 40.232 (eran 47.944 antes de la limpieza) |
| **Fuentes** | 33 |
| **Período** | 2007 a 2026 |
| **Criterio para quedar** | Coincidir con la búsqueda y pasar la limpieza. No hay filtro por tema |
| **Tamaño aproximado** | 57 MB |

Para el dataset de soluciones y la comparación entre ambos, ver [el análisis de soluciones](../analisis-datasets/analisis-dataset-soluciones.md). Los criterios de limpieza están en [`contexto-pipeline.md`](../analisis-datasets/contexto-pipeline.md#limpieza-y-consolidación-8112026).

## Limpieza

| Iniciales | Título corto | Sin cuerpo | Seriado | Título repetido | Cuerpo repetido | Finales |
|---:|---:|---:|---:|---:|---:|---:|
| 47.944 | 87 | 7.325 | 63 | 209 | 28 | 40.232 |

De las 7.325 notas sin cuerpo, 6.804 ya venían vacías, casi todas videos de TN y El Doce. Las otras 521 quedaron vacías al recortar el pie de suscripción.

## Cifras

- **Mención del tema:** 28.863 notas mencionan alguna raíz del tema en título, bajada o cuerpo, y 19.706 la mencionan en título o bajada.
- **Por idioma de la fuente:** español 24.316, inglés 9.904, italiano 2.821, portugués 1.394, polaco 941 y alemán 856.
- **Argentina:** 19.188 notas de 9 medios, con 6.518 que tienen raíces del tema en título o bajada.
- **Córdoba:** El Doce y CBA24N suman 4.227 notas, con 1.101 que tienen raíces del tema en título o bajada.
- **Por año:** 1.596 en 2023, 8.713 en 2024, 10.020 en 2025 y 9.560 hasta noviembre de 2026.
- **Calidad del texto:** todas las notas tienen cuerpo. La mediana es de 3.234 caracteres y 304 tienen menos de 300.
- **Tipo de voz:** 22.221 notas de medio especializado, 17.192 de diario y 819 de opinión. Las de opinión vienen sobre todo de Inside Waste (282) y El Doce (146).

## Pros

- **Volumen de sobra para probar el método:** el objetivo de 10.000 notas se supera aun quedándose con las que mencionan el tema en título o bajada (19.706), aunque falta medir cuántas son útiles.
- **Mezcla de voces:** combina medios generalistas, medios especializados y organizaciones del sector.
- **Local e internacional:** tiene presencia argentina y cordobesa, y fuentes en seis idiomas.
- **Fuentes más antiguas:** ocho fuentes llegan antes de 2024, lo que permite mirar persistencia en esos medios.
- **Texto completo:** después de la limpieza no quedan notas sin cuerpo ni con el pie de suscripción de cada fuente.
- **Listo para filtrar:** un solo Parquet, con el mismo esquema que los otros tres datasets, y la fuente, la fecha, el cuerpo y los términos que coincidieron.

## Contras

- **Mucho ruido:** en una lectura rápida de 60 títulos al azar, antes de la limpieza, cerca de la mitad parecía tratar sobre residuos. Hay notas de espectáculos, recetas o política que coinciden por palabras como "camioneros" o "basura". La limpieza no filtra por tema, así que ese ruido sigue. Es una estimación informal, no una medición.
- **Ruido concentrado:** TN y El Doce aportan 11.563 notas (29 %), y solo 2.334 (20 %) tienen raíces del tema en título o bajada. En el resto son 17.372 de 28.669 (61 %).
- **Concentración:** las 5 fuentes más grandes reúnen el 49 % de las notas. Contar sin ponderar favorece a esos medios.
- **Serie temporal engañosa:** 11.939 notas son anteriores a 2024 y salen de solo ocho fuentes; las demás arrancan en 2024. El salto de 2023 a 2024 viene de cómo se buscó, no de un aumento real del tema.
- **Cobertura parcial:** en Infobae y Clarín se bajó solo lo prioritario, y quedaron sin bajar 5.781 y 1.894 notas. Falta La Voz, y Futuro Sustentable y Cadena 3 no aportan datos.
- **Duplicados entre medios sin detectar:** la limpieza quitó los títulos y cuerpos repetidos, pero no detecta notas reescritas, traducidas ni el mismo hecho contado por varios medios. Además, 2.637 notas también están en biodiversidad y 1.437 en movilidad.
- **Sesgo propio de las noticias:** muestra lo que se publica, no todo lo que pasa, ni la gravedad de cada problema.

## Cómo se midió

- **Conteos:** directos sobre `data/residuos.parquet` del 8/11/2026. Las notas sin bajar de Infobae y Clarín vienen de [`contexto-pipeline.md`](../analisis-datasets/contexto-pipeline.md).
- **Raíces:** se contaron con las raíces de todos los idiomas juntas, así que es una aproximación.
- **Idioma:** es el de la fuente, no el detectado en cada nota.
- **Medios argentinos:** se asignaron a mano por dominio o medio, sin un campo de país en los datos.
- **Coincidencias entre datasets:** por URL.
- **Muestras de títulos:** las leyó Claude, una sola vez y sin revisión del equipo. Sirven como orientación.
