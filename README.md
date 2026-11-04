# pipeline-decision-data

Pipeline para detectar los problemas más recurrentes en noticias y foros sobre sostenibilidad. Lo prepara un equipo de tres personas (Ignacio, Lauti y Diego) para elegir la problemática y plantear su producto en [Hack to the Future](https://cordobatechweek.com/side-events/hack-to-the-future/), los días 12 y 13 de noviembre de 2026 en Córdoba.

**Estado:** en diseño. Todavía no hay código ni dataset.

## Objetivo

Encontrar problemas recurrentes en las fuentes de cada track, para descubrir alguno que el equipo no conocía. Los resultados son un insumo para decidir: no prueban por sí solos que un problema importe.

El orden de trabajo es:

1. Gestión sostenible de residuos.
2. Si hay tiempo, el mismo proceso para biodiversidad, agro y movilidad.

## Pipeline previsto

```text
Fuentes → Scraping → Dataset → Clasificar / Segmentar → Grafo → Decisiones
```

- **Dataset:** título, fuente, body y fecha de cada nota. El objetivo es llegar a 10.000 notas por track, pero todavía no está comprobado que existan.
- **Por definir:** la forma de hacer scraping, el modelo para clasificar y si el grafo es la mejor vista.

Podés ver el boceto completo en [pipeline-arquitectura.html](docs/pipeline-arquitectura.html).

## Documentación

- [Contexto del pipeline](docs/contexto-pipeline.md): objetivo, decisiones, hechos comprobados, limitaciones y dudas abiertas.
- [Arquitectura](docs/pipeline-arquitectura.html): boceto digitalizado y dudas por etapa.
- [Fuentes posibles](https://claude.ai/artifact/Ks4WAtVgcdcGNSxywUQFyw): lista de medios y su acceso. Es un doc privado, así que hay que compartirlo para que otros lo vean.
- [CLAUDE.md](CLAUDE.md): datos del evento e indicaciones de trabajo para Claude.
