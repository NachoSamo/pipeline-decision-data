<div align="center">

# pipeline-decision-data

**Saber qué problemas se repiten antes de elegir cuál resolver.**

Pipeline de análisis de problemáticas · Hack to the Future · Córdoba Tech Week 2026

[![Estado](https://img.shields.io/badge/Estado-En%20dise%C3%B1o-111111?style=for-the-badge)](#estado-del-repositorio)
[![Código](https://img.shields.io/badge/C%C3%B3digo-Todav%C3%ADa%20no-111111?style=for-the-badge)](#estado-del-repositorio)
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
> **Estado actual:** el proyecto está en diseño. Hay contexto, un boceto digitalizado y un relevamiento
> inicial de fuentes. Todavía no hay código ni dataset, y el tamaño objetivo no está comprobado.

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
    A["Fuentes"] --> B["Scraping<br/>¿con Playwright?"]
    B --> C["Dataset<br/>¿≈ 10.000 notas?"]
    C --> D["Clasificar y segmentar<br/>¿con LLM?"]
    D --> E["¿Grafo?"]
    E --> F["Decisiones en base<br/>al análisis"]
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
| **Residuos** | Hasta 10.000 notas | Si el pipeline revela problemas que el equipo no conocía |
| **Biodiversidad, agro y movilidad** | El mismo proceso, con hasta 10.000 notas por track, si hay tiempo | Qué problemas se repiten en cada temática |

Si no llegamos a procesar los otros tres tracks, el análisis de residuos sigue siendo válido.

---

## Arquitectura objetivo

La arquitectura todavía es un boceto. Las etapas con `?` siguen en duda.

```mermaid
flowchart LR
    subgraph Fuentes["1 · Fuentes"]
        A["Clarín"]
        B["La Nación"]
        C["El Doce"]
        D["La Voz"]
        E["¿Reddit? ¿X?<br/>¿Comentarios de Instagram?"]
    end

    subgraph Datos["2 · Datos"]
        F["Scraping<br/>¿con Playwright?"]
        G["Dataset<br/>título, fuente, body y fecha"]
    end

    subgraph Analisis["3 · Análisis"]
        H["Clasificar y segmentar<br/>¿con LLM?"]
        I["¿Grafo?"]
    end

    subgraph Decision["4 · Decisión"]
        J["Decisiones en base<br/>al análisis"]
    end

    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F --> G --> H --> I --> J
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
| Hay 22 fuentes posibles, con su acceso revisado | [Doc de fuentes](https://claude.ai/artifact/Ks4WAtVgcdcGNSxywUQFyw) (privado) | Comparar cada fila con el `robots.txt` del medio |
| Las 10.000 notas todavía no están comprobadas | [`docs/contexto-pipeline.md`](docs/contexto-pipeline.md) | Leer "Muestra de volumen"; los scripts de esa prueba no están en el repo |
| Datos del evento y reglas confirmadas | [`CLAUDE.md`](CLAUDE.md) | Comparar con la [fuente oficial](https://cordobatechweek.com/side-events/hack-to-the-future/) y lo informado por la organización |

---

## Estado del repositorio

| Área | Estado |
|---|---|
| Contexto y decisiones | **Documentado** |
| Boceto de la arquitectura | **Digitalizado**, con dudas abiertas |
| Relevamiento de fuentes | **Inicial:** falta revisar términos de uso y foros |
| Medición del volumen | **Inicial:** solo muestras por URL, sin texto completo |
| Scraping | **No iniciado** |
| Dataset | **No iniciado** |
| Clasificación y segmentación | **No iniciado** |
| Grafo y análisis | **No iniciado** |

---

## Ejecutar localmente

Todavía no hay nada para ejecutar. Para revisar el diseño, cloná el repositorio y abrí
`docs/pipeline-arquitectura.html` en el navegador.

```bash
git clone https://github.com/NachoSamo/pipeline-decision-data.git
```

---

## Mapa del repositorio

```text
.
├── docs/
│   ├── contexto-pipeline.md        Objetivo, decisiones, hechos y dudas abiertas
│   └── pipeline-arquitectura.html  Boceto digitalizado del pipeline
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
