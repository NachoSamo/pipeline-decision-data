<div align="center">

# pipeline-decision-data

**Saber qué problemas se repiten antes de elegir cuál resolver.**

Pipeline de análisis de problemáticas · Hack to the Future · Córdoba Tech Week 2026

[![Estado](https://img.shields.io/badge/Estado-Scraping%20en%20curso-111111?style=for-the-badge)](#estado-del-repositorio)
[![Código](https://img.shields.io/badge/C%C3%B3digo-Scraping-111111?style=for-the-badge)](docs/scrapping-webs.md)
[![Track](https://img.shields.io/badge/Primer%20track-Residuos-111111?style=for-the-badge)](#alcance-objetivo)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-Boceto-5964F2?style=for-the-badge)](docs/pipeline-arquitectura.html)

**Ignacio, Lauti y Diego**

</div>

---

Hack to the Future plantea cuatro temáticas de sostenibilidad, y el equipo tiene que elegir qué problema
abordar. Nadie del equipo tiene experiencia directa con residuos, el primer track que va a analizar.

Este proyecto busca reunir miles de notas periodísticas, ordenarlas por problema y mostrar cuáles se
repiten. El objetivo es descubrir alguno que el equipo no conocía y usar esa información como punto 0
para elegir la problemática y plantear el producto.

```text
Formato de ejemplo, sin datos reales:

Problema:             <nombre del problema>
Track:                Residuos
Notas y hechos:       <cantidad de notas> · <hechos distintos>
Medios:               <medios independientes>
Tiempo:               <años en que aparece> · <continuidad> · <tendencia>
Lugares:              <ciudades, provincias o países>
Actores:              <actores afectados> · <origen de la voz>
Magnitud:             <cifras informadas en las notas>
Soluciones fallidas:  <planes o anuncios previos>
```

> [!IMPORTANT]
> **Los datos orientan. El equipo decide.** Los resultados ayudan a elegir, pero no prueban por sí solos
> que un problema importe. Las noticias muestran lo que se publica, no todo lo que pasa.

> [!NOTE]
> **Estado actual:** el proyecto está en la etapa de scraping del track de residuos. Al 4/11/2026 hay
> 28.072 notas descargadas, y 13.633 tienen cuerpo y mencionan el tema. Falta medir cuántas son útiles
> y cuántas están duplicadas entre fuentes. Todavía no hay clasificación ni análisis.

---

## Por qué este proyecto

La idea surge del video "Idea Plotter", de @re_skob, basado en una receta de Synthetic Beef. Ahí
convierten 189.495 juegos de Steam en un mapa de significado para encontrar zonas vacías. El equipo
quiere llevar ese enfoque a problemas reales, aunque no necesariamente con el mismo método.

El pipeline busca:

1. **Reunir** noticias de medios locales, nacionales e internacionales.
2. **Ordenar** cada nota con título, fuente, cuerpo y fecha.
3. **Clasificar y segmentar** el contenido según el problema que describe.
4. **Medir** cuánto se repite cada problema, dónde y durante cuánto tiempo.
5. **Decidir** qué problemática abordar a partir de ese análisis.

---

## De las notas a la decisión

```mermaid
flowchart LR
    A["Fuentes"] --> B["Scraping<br/>por fuente"]
    B --> C["Dataset"]
    C --> D["Filtro y<br/>limpieza"]
    D --> E["Clasificar y<br/>segmentar"]
    E --> F["Agrupar y medir<br/>en dos ramas"]
    F --> G["Ranking, grafo<br/>y mapa"]
    G --> H["Contraste"]
    H --> I["Decisiones"]
```

### Medidas de recurrencia

| Grupo | Pregunta que responde | Medidas |
|---|---|---|
| **Volumen** | ¿Cuánto se habla del problema? | Cantidad de notas · hechos distintos · medios independientes |
| **Tiempo** | ¿Persiste o fue un pico? | Años en que aparece · continuidad · tendencia |
| **Alcance** | ¿A quién y dónde afecta? | Lugares afectados · actores afectados · magnitud informada |
| **Respuesta** | ¿Quién lo plantea y qué se intentó? | Soluciones fallidas · origen de la voz |

---

## Alcance objetivo

| Etapa | Qué incluye | Qué tendría que mostrar |
|---|---|---|
| **Residuos** | Hasta 10.000 notas de medios locales y nacionales, y fuentes internacionales desde 2024 | Si el pipeline revela problemas que el equipo no conocía |
| **Biodiversidad, agro y movilidad** | El mismo proceso, con hasta 10.000 notas por track, si hay tiempo | Qué problemas se repiten en cada temática |

Si no llegamos a procesar los otros tres tracks, el análisis de residuos sigue siendo válido.

---

## Arquitectura objetivo

Hoy solo están construidas las etapas de fuentes, scraping y dataset, para residuos. El resto es el
diseño acordado; las dudas abiertas están en [`docs/pipeline-arquitectura.html`](docs/pipeline-arquitectura.html).

```mermaid
flowchart TB
    subgraph Datos["1 · Datos"]
        A["16 fuentes con script<br/>locales e internacionales"] --> B["Scraping por fuente"] --> C["Dataset en Parquet"]
    end

    subgraph Preparacion["2 · Preparación"]
        D["Filtro y limpieza"] --> E["Clasificar: problema,<br/>solución, ambas u otra"]
    end

    subgraph Analisis["3 · Análisis"]
        F["Problemas: agrupar<br/>y medir recurrencia"]
        G["Soluciones: agrupar<br/>y registrar evidencia"]
        H["Ranking, grafo y<br/>mapa de embeddings"]
        F --> H
        G --> H
    end

    subgraph Decision["4 · Decisión"]
        I["Contraste con soluciones<br/>validadas y datos abiertos"] --> J["Decisiones en base<br/>al análisis"]
    end

    C --> D
    E --> F
    E --> G
    H --> I
```

### Criterios de ponderación

- **Geografía:** tienen más peso los problemas locales y los que aparecen en varios países. Faltan los
  valores y definir qué cuenta como local.
- **Fecha:** se guarda para filtrar y comparar, no como peso fijo. Un problema que persiste de 2021 a
  2026 es justo lo que se busca.

### Límites del método

- Un problema frecuente en los diarios no es necesariamente el más grave.
- Lo más recurrente suele ser lo más visible, y eso puede chocar con la búsqueda de algo desconocido.
- Que una solución no aparezca en las noticias no significa que no exista.

---

## Dónde está la evidencia

| Afirmación | Dónde está | Cómo revisarla |
|---|---|---|
| Objetivo, decisiones y dudas abiertas | [`docs/contexto-pipeline.md`](docs/contexto-pipeline.md) | Leer las secciones de decisiones y "Falta aclarar" |
| Diseño del pipeline | [`docs/pipeline-arquitectura.html`](docs/pipeline-arquitectura.html) | Abrir el boceto y la lista "Por definir" |
| Hay 43 fuentes posibles, con su acceso revisado | [`docs/Fuentes para el dataset del pipeline.md`](docs/Fuentes%20para%20el%20dataset%20del%20pipeline.md) | Comparar cada fila con el `robots.txt` del medio |
| 13.633 notas de residuos tienen cuerpo y mencionan el tema, pero falta medir cuántas son útiles | [`docs/contexto-pipeline.md`](docs/contexto-pipeline.md) y [`data/`](data/) | Leer "Evaluación de volumen" y recontar los Parquet con `relevante`, de [`scripts/progreso.py`](scripts/progreso.py) |
| Cada fuente se lista por una vía que su `robots.txt` no excluye | [`docs/scrapping-webs.md`](docs/scrapping-webs.md) y [`scripts/`](scripts/) | Comparar la sección "Permisos" de cada fuente con su `robots.txt` |
| Datos del evento y reglas confirmadas | [`CLAUDE.md`](CLAUDE.md) | Comparar con la [fuente oficial](https://cordobatechweek.com/side-events/hack-to-the-future/) y lo informado por la organización |

---

## Estado del repositorio

| Área | Estado |
|---|---|
| Contexto y decisiones | **Documentado** |
| Boceto de la arquitectura | **Digitalizado**, con dudas abiertas |
| Relevamiento de fuentes | **Inicial:** falta revisar términos de uso y foros |
| Medición del volumen | **Parcial:** conteo de menciones por fuente; falta medir utilidad y duplicados entre fuentes |
| Scraping | **En curso:** 16 scripts. Terminaron 10 fuentes; siguen TN, CBA24N y las internacionales; Futuro Sustentable no tiene datos; Cadena 3 quedó de lado por falta de volumen |
| Dataset | **En curso:** solo residuos, con 18.989 notas únicas en 10 Parquet |
| Clasificación y segmentación | **No iniciado** |
| Grafo y análisis | **No iniciado** |

---

## Ejecutar localmente

Requiere Python con `requests`, `pandas` y `pyarrow`. Los comandos de cada fuente están en
[`docs/scrapping-webs.md`](docs/scrapping-webs.md). Por ejemplo:

```bash
python scripts/scrape_internacional.py
```

Para verificar el código sin descargar nada:

```bash
python scripts/scrape_infobae.py --selfcheck
```

---

## Mapa del repositorio

```text
.
├── data/                                            Notas descargadas por fuente, en Parquet
├── docs/
│   ├── analisis-croma.md                            Qué es Croma y cómo podría ayudar
│   ├── Fuentes para el dataset del pipeline.md      Fuentes posibles y su acceso
│   ├── contexto-pipeline.md                         Objetivo, decisiones, hechos y dudas abiertas
│   ├── pipeline-arquitectura.html                   Boceto digitalizado del pipeline
│   ├── publicaciones-periodistas-ambientales.md     Resumen de 16 publicaciones
│   └── scrapping-webs.md                            Cómo funciona cada script
├── scripts/                                         Scraping por fuente y diccionario
├── CLAUDE.md                       Datos del evento e indicaciones para Claude
└── README.md                       Presentación del proyecto
```

---

## Principios

1. **Los datos orientan; el equipo decide.**
2. **Lo publicado no es todo lo que pasa.**
3. **La persistencia es una señal.**
4. **Primero medir; después escalar.**
5. **Decir lo que todavía no está comprobado.**

---

## Equipo

| Integrante | Foco |
|---|---|
| **Ignacio** | Idea inicial y diseño del pipeline |
| **Lauti** | Perfil técnico; tareas por definir |
| **Diego** | Perfil técnico; tareas por definir |

Preparado en Córdoba para **Hack to the Future**, la hackathon de innovación sostenible de la
**Córdoba Tech Week**, organizada por **Córdoba Cluster**.

<div align="center">

### pipeline-decision-data

*De noticias dispersas a una decisión informada.*

</div>
