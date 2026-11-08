# Hack to the Future: contexto del evento

Proyecto de brainstorming previo a la hackathon. Respondé siempre en español.

## Datos del evento

- **Nombre:** Hack to the Future, hackathon de innovación sostenible dentro de la Córdoba Tech Week.
- **Organiza:** Córdoba Cluster.
- **Fuente oficial:** https://cordobatechweek.com/side-events/hack-to-the-future/
- **Lugar:** Pabellón Amarillo, Predio Ferial Córdoba.
- **Fechas:**
  - Pre-hackathon: semana del 2/11, sesión virtual de 1 hora y kit digital.
  - Día 1 (Hackathon): jueves 12/11, de 9 a 16 h.
  - Día 2 (Demo Day): viernes 13/11, de 9 a 16 h.
- **Inscripción:** hasta el 5/11, mediante https://forms.gle/JPukJPq7qyHWxhDs8. Se puede inscribir en equipo o de forma individual; los individuales se suman a un equipo.
- **Participantes:** jóvenes, estudiantes y profesionales de distintas disciplinas, de 18 a 35 años. No se requieren conocimientos previos en tecnología ni en sostenibilidad.
- **Metodología:** Design Thinking, con herramientas de inteligencia artificial, facilitadores y mentores.
- **Temáticas (Global Gateway de la Unión Europea):**
  - Protección de la biodiversidad.
  - Transición sostenible en el agro.
  - Movilidad sostenible.
  - Gestión sostenible de residuos.
- **Premios e incubación:** se seleccionan 8 finalistas, de los cuales 4 equipos ganan. Los equipos ganadores acceden al programa de incubación de la Unión Europea en 2027.
- **Demo Day:** todos los equipos presentan su propuesta ante un jurado.

## Reglas confirmadas por la organización

Según informó Ignacio el 4/11/2026:

- Se pueden usar datos externos.
- Se puede llevar trabajo hecho a la hackathon.
- Se pueden enviar textos de diarios a una API de IA. Esto no reemplaza revisar los términos de uso de cada medio.

## Criterios de evaluación (confirmados)

Según una placa oficial compartida el 6/11/2026:

- **Jurado:** 12 personas, 3 por vertical. Evalúa el viernes 13/11.
- **Escala:** cada criterio se puntúa de 1 a 5, con estos pesos:

| Criterio | Peso |
|---|---:|
| Impacto social y ambiental | 25 % |
| Innovación y originalidad | 20 % |
| Factibilidad técnica y económica | 20 % |
| Escalabilidad y sostenibilidad | 15 % |
| Vínculo con el ecosistema | 10 % |
| Pitch y equipo | 10 % |

La placa lleva los logos de Global Gateway, "Financiado por la Unión Europea",
Centro de Comercio Internacional (ITC) y Córdoba Cluster.

## Facilitadores

Según información del equipo, sin fuente pública: los facilitadores trabajan en
ciencia política.

## Quién está detrás y qué foco tiene

- **Centro de Comercio Internacional (ITC):** agencia conjunta de la ONU y la OMC.
  Se describe como la única agencia de desarrollo dedicada por completo a que las
  pymes vendan al exterior.
  - En Argentina tiene el hub SheTrades, para emprendedoras, con la Agencia de
    Inversiones y Comercio Internacional (AAICI) hasta fines de 2026.
  - Hace el Deforestation-Free Trade Gateway, una herramienta gratuita para la EUDR.
- **Licitación del ITC (julio-agosto de 2026):** organización de una hackathon en
  Argentina dentro del proyecto "Social Investment and Innovation (Social
  Accelerator)".

### Dónde podrían incidir más (inferencia, no confirmado)

- **ITC:** su foco en pymes, comercio exterior e inclusión de jóvenes y mujeres
  podría pesar en impacto, escalabilidad y vínculo con el ecosistema.
- **Facilitadores de ciencia política:** podrían prestar atención a actores,
  políticas públicas y gobernanza, sobre todo en impacto y vínculo con el
  ecosistema.

## Datos no especificados por la organización

Estos puntos figuran como abiertos en la información pública. No asumir respuestas:

- Reglas adicionales (hardware, cruce de temáticas, trabajo entre días).
- Duración del pitch y horario efectivo del Demo Day.
- Costos, transporte y alojamiento.
- Quién conduce el programa de incubación 2027 y en qué consiste.

## Documentación: actualizarla siempre

Regla para cualquier agente o persona que trabaje en este repositorio. **Todo cambio que toque código, datos,
esquemas, fuentes o decisiones incluye, en el mismo commit, la actualización de la documentación afectada.** No
hace falta que nadie lo pida, y no se deja "para después".

| Si cambia… | Actualizar |
|---|---|
| Un script, un comando o un flag | [`docs/scrapping-webs.md`](docs/scrapping-webs.md) y "Ejecutar localmente" del [`README.md`](README.md) |
| Los datos de `data/` (descarga, limpieza, filtro, clasificación) | El análisis del dataset en [`docs/analisis-datasets/`](docs/analisis-datasets/), con cifras medidas y la fecha de la foto, y "Estado actual" y "Estado del repositorio" del README |
| Las columnas o el esquema de un Parquet | [`docs/scrapping-webs.md`](docs/scrapping-webs.md) y [`contexto-pipeline.md`](docs/analisis-datasets/contexto-pipeline.md) |
| Una decisión, un criterio o una duda resuelta | [`contexto-pipeline.md`](docs/analisis-datasets/contexto-pipeline.md): "Decisiones tomadas" o "Falta aclarar" |
| Las fuentes de problemáticas o su circuito | [`docs/circuito-problematicas.md`](docs/circuito-problematicas.md) |
| Las fuentes posibles o su acceso | [`docs/analisis-fuentes/Fuentes para el dataset del pipeline.md`](docs/analisis-fuentes/Fuentes%20para%20el%20dataset%20del%20pipeline.md) |
| Un archivo o una carpeta nueva, movida o borrada | "Mapa del repositorio" del README |
| Una etapa del pipeline | "Arquitectura objetivo" del README y [`docs/pipeline-arquitectura.html`](docs/pipeline-arquitectura.html) |

Cómo hacerlo:

- **Medir, no estimar.** Las cifras salen de contar sobre los archivos. Si algo no se midió, se dice.
- **Fechas absolutas** (8/11/2026), nunca "hoy" o "ayer".
- **Separar lo hecho de lo planeado.** No presentar como implementado algo que no lo está.
- **Buscar referencias viejas** (`grep` del número, la ruta o la columna que cambió) y corregirlas todas, no solo la primera.
- **Mantener el estilo:** español, frases cortas y la estructura que ya tiene cada archivo. El README sigue la estructura acordada.
- **Al terminar, decir qué documentos se actualizaron**, y si alguno quedó pendiente, por qué.

Los Parquet de `data/` tienen que quedar debajo de 100 MB por archivo, el límite de GitHub. `limpiar.py` guarda con zstd nivel 19 por eso.

## Preferencias de trabajo

- Las sesiones son introspectivas: ideas que surgen de a poco, y cómo impactar con la experiencia de cada integrante del equipo.
- Background del usuario: buscarlo en la memoria de Claude antes de asumir nada.
- No afirmar todo. Si algo no está claro o Claude se equivoca, decirlo.
- Si no está claro qué quiere el usuario, entrevistarlo con preguntas de opción múltiple dentro del chat.
- Ante la duda, preguntar.
- No sesgar el pensamiento del equipo con conceptos o soluciones propuestas por Claude. Entregar información relevante del evento y preguntas elementales y contextuales.
