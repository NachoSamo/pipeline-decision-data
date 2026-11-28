# Resultados v1: residuos

Primera versión de la clasificación de residuos, hecha con Qwen 2.5 3B en Kaggle (piloto del 10/11/2026). **No es la versión vigente:** se decidió volver a hacer el análisis y la clasificación (ver [contexto-pipeline.md](../../../docs/analisis-datasets/contexto-pipeline.md), "Etiquetado manual antes de reclasificar"). Se conserva para comparar con la v2 sin mezclarlas.

Los documentos de esta versión están en [`docs/v1-residuos/`](../../../docs/v1-residuos/).

| Archivo o carpeta | Qué es | Cómo se generó |
|---|---|---|
| `residuos_listo_para_kaggle.parquet` | Notas de residuos empaquetadas, con la pre-limpieza heurística | `python scripts/clasificacion/empaquetar.py --tema residuos` (en v1) |
| `residuos_clasificado_final.parquet` | Clasificación del piloto, con categorías cortadas o inventadas (ver contexto) | `scripts/clasificacion/pipeline_clasificacion_kaggle.ipynb` en Kaggle |
| `test_residuos_clasificado.parquet` | Muestra de prueba del piloto | No está documentado cómo se generó |
| `no_patrones/` | Grafo GEXF, mapa UMAP, reporte y JSON de no-patrones. El grafo HTML de vis.js se eliminó el 27/11/2026: ahora lo muestra la web de [`Frontend/`](../../../Frontend), que lee `Frontend/web/data/v1-residuos.json` | `python scripts/grafo/ejecutar_analisis.py --entrada data/resultados/v1-residuos/residuos_clasificado_final.parquet --dir-salida data/resultados/v1-residuos/no_patrones` |

Para la v2, la constante `VERSION` de [`scripts/clasificacion/version.py`](../../../scripts/clasificacion/version.py) cambia a `"v2"` y los resultados nuevos van a `data/resultados/v2-residuos/`.
