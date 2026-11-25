# Guía de etiquetado: movilidad

Última actualización: 25/11/2026.

Reglas para decidir si una nota del track de movilidad es relevante y cómo se clasifica. Salen de la reconciliación entre Ignacio y Lauti, sobre las 25 notas de la muestra `2026-11-25-s42`. Sirven para dos cosas: etiquetar las próximas tandas con el mismo criterio y escribir el prompt del LLM.

- **Base:** [`reconciliacion/movilidad-gold.json`](reconciliacion/movilidad-gold.json), con la etiqueta final de cada nota, y [`reconciliacion/movilidad-informe.md`](reconciliacion/movilidad-informe.md), con el acuerdo y las decisiones.
- **Lo que es regla y lo que es propuesta:** cada regla dice de dónde sale. "Gold" quiere decir que la respalda al menos una nota decidida. "Decisión del 25/11" quiere decir que la definieron Ignacio y Lauti al cerrar la guía. "Propuesta" quiere decir que todavía no tiene ninguna nota que la respalde, y hay que validarla en la próxima tanda.

## Qué mostró el gold

| Medida | Valor |
|---|---|
| Notas relevantes | 4 de 25 |
| Relevantes en diarios (El Doce, TN, Clarín, La Nación y CBA24N) | 1 de 14 |
| Relevantes en medios especializados (Grist, Visión Sustentable, Ecoticias, CicloVivo y Ecomundo) | 3 de 11 |
| Acuerdo inicial entre Ignacio y Lauti en relevancia | 16 de 25, kappa 0,27 |

- **Casi todo es ruido.** El filtro por palabras clave deja pasar notas que mencionan tránsito, choques o transporte sin que ese sea el tema. El primer trabajo del LLM es descartar.
- **En la muestra, las fuentes están parejas.** En el dataset completo, el 91 % de las notas son de diarios (48.416 de 53.029), así que es probable que la proporción real de relevantes sea más baja que en la muestra. No se midió.
- **El desacuerdo inicial fue de criterio, no de lectura.** Ignacio marcó como relevantes 12 notas y Lauti 7. En la reconciliación ganó casi siempre el criterio más estricto, el de Lauti. Esta guía lo deja escrito.

## Paso 1: ¿es relevante?

Las preguntas se hacen en orden. A la primera que dice "no relevante", se corta.

1. **¿El tema central es la movilidad?** Es decir, el transporte de personas o de cargas: vehículos, transporte público, tránsito, e infraestructura vial, ferroviaria, ciclista o peatonal. Si la movilidad aparece solo de pasada, la nota no es relevante. (Gold)
2. **¿Es una nota de seguridad vial?** Choques, atropellos, consejos de manejo y sistemas de retención infantil quedan afuera, aunque sean educativos o hablen de causas. La seguridad vial no forma parte de este track. (Decisión del 25/11)
3. **¿Describe un problema concreto de movilidad o una solución concreta?** Una solución puede ser un producto, una tecnología, una obra, un servicio o un programa. Si la nota solo informa sin plantear ni lo uno ni lo otro, no es relevante: un cambio de operador, consejos genéricos o una disputa política. (Decisión del 25/11)

Si pasa las tres preguntas, es relevante. El idioma de la nota no importa: dos de las cuatro relevantes están en portugués. (Gold)

### Política y gobierno

- **Entra:** una obra, un servicio o una medida de transporte concreta, aunque la impulse un gobierno. Por ejemplo, el proyecto de teleférico y subte en La Plata. (Decisión del 25/11)
- **Queda afuera:** la disputa política, la crítica o la declaración que no viene con una medida concreta de transporte. Por ejemplo, las organizaciones que critican al alcalde de Valladolid. (Gold)
- **Queda afuera:** la economía y las finanzas, aunque usen la palabra "sustentable". Por ejemplo, una obligación negociable vinculada a la sustentabilidad, o el reporte de sustentabilidad de una aseguradora. (Gold)

### Exclusiones del gold, por motivo

| Motivo | Notas | Ejemplo del gold |
|---|---:|---|
| Seguridad vial | 6 | "Caos de tránsito en la autopista 9 de Julio Sur por un choque"; "Videos: qué le pasa a un niño en un accidente sin la protección adecuada"; "Manual del buen conductor" |
| Política o economía sin una medida de transporte | 6 | "El alcalde de Valladolid suspende en movilidad sostenible"; "Caputo amenazó con un ajuste a las provincias"; "Santander y San Miguel lideran la primera Obligación Negociable…" |
| Otro track ambiental | 4 | Minas abandonadas, deforestación y epidemias, caída de las poblaciones de fauna, plásticos de Pepsi y Coca-Cola |
| Otro tema | 2 | La salida de Messi del Barcelona; el diseño de videojuegos |
| Nota de color o viral con el tránsito de escenario | 2 | Un operativo de tránsito inventado para una sorpresa familiar; insultos a un agente de tránsito |
| Gestión sin problema ni solución | 1 | "Las líneas 30 y 34 pasan a formar parte de la empresa SiBuS" |

Una nota que pertenece a otro track ambiental se descarta en movilidad. No se reasigna a otro track. (Gold)

## Paso 2: tipo

Solo se elige en las notas relevantes. Hay tres opciones; "ninguna" ya no existe, porque una nota relevante siempre tiene un problema o una solución. (Decisión del 25/11)

| Tipo | Cuándo | Ejemplo del gold |
|---|---|---|
| `problema` | Describe un problema de movilidad y no presenta una solución concreta | Sin ejemplo todavía |
| `solucion` | Presenta una solución concreta. Si menciona el problema, es solo como contexto | Triciclo solar para entregas; configurador del Silence S04; startups del Hub Green Sampa |
| `ambas` | Describe un problema concreto y una solución que apunta a ese problema | Teleférico y subte en La Plata para aliviar el tránsito: "habla de cómo la solución ataca al problema" |

## Paso 3: categorías

Una nota puede tener una o más categorías de cada lado. Se marcan todas las que la nota describe. Por ejemplo, el Hub Green Sampa quedó con tres soluciones porque presenta varias startups con tecnologías distintas. (Gold) Una categoría que la nota solo menciona de pasada no se marca. (Propuesta)

Las listas son las de [`config.js`](config.js). Las definiciones que no tienen ejemplo son propuestas, armadas a partir del nombre de la categoría.

### Problemas

| Categoría | Qué abarca | Ejemplo del gold |
|---|---|---|
| `CONGESTION_Y_DEMORAS` | Tránsito saturado, demoras y tiempos de viaje | Tránsito en La Plata, la capital bonaerense |
| `EMISIONES_Y_FLOTA_OBSOLETA` | Contaminación del aire y emisiones del transporte, y vehículos viejos o contaminantes (propuesta) | Sin ejemplo |
| `DEFICIT_TRANSPORTE_PUBLICO` | Falta de frecuencias, recorridos, cobertura o calidad en el transporte público (propuesta) | Sin ejemplo |
| `FALTA_INFRAESTRUCTURA_CICLISTA_PEATONAL` | Falta de ciclovías, veredas o cruces para moverse a pie o en bicicleta (propuesta) | Sin ejemplo |
| `OTRO_PROBLEMA_MOVILIDAD` | Ninguna de las anteriores. Requiere describir el problema en texto libre | Sin ejemplo |

`SINIESTRALIDAD_VIAL` se sacó de la lista el 25/11 porque la seguridad vial quedó afuera del track.

### Soluciones

| Categoría | Qué abarca | Ejemplo del gold |
|---|---|---|
| `ELECTROMOVILIDAD_Y_BUSES_ELECTRICOS` | Vehículos eléctricos o solares de cualquier tamaño, incluidos los de reparto | Triciclo solar; Silence S04; Hub Green Sampa |
| `INFRAESTRUCTURA_BICICLETAS_Y_PEATONAL` | Ciclovías, bicicletas, servicios y tecnologías para moverse en bicicleta o a pie | Hub Green Sampa |
| `SISTEMAS_INTELIGENTES_TRANSITO_ITS` | Software, datos y sensores para gestionar el tránsito o el transporte | Hub Green Sampa |
| `REDES_FERROVIARIAS_Y_SUBTE` | Trenes, subtes y otros sistemas guiados, como un teleférico urbano | Teleférico y subte en La Plata |
| `OTRA_SOLUCION_MOVILIDAD` | Ninguna de las anteriores. Requiere describir la solución en texto libre | Sin ejemplo |

Si un mismo texto libre de "otro" se repite en varias notas, es candidato a categoría nueva.

## Alcance geográfico: no lo decide nadie

El alcance sale del origen del medio que publica la nota, con el diccionario [`scripts/diccionarios/alcance_fuentes.py`](../scripts/diccionarios/alcance_fuentes.py). (Decisión del 25/11)

| Origen del medio | Alcance | Fuentes de movilidad |
|---|---|---|
| Córdoba | `CORDOBA_LOCAL` | El Doce y CBA24N |
| Resto de Argentina | `ARGENTINA_NACIONAL` | TN, Clarín, La Nación, Visión Sustentable y Ecomundo |
| Resto de América Latina | `LATAM_REGIONAL` | CicloVivo |
| Resto del mundo | `INTERNACIONAL_GLOBAL` | Grist y Ecoticias |

El LLM no devuelve alcance, y la app de etiquetado ya no lo pregunta.

## Del gold al prompt

Lo que tiene que llevar el prompt, en este orden:

1. **Qué es el track:** la definición del paso 1, pregunta 1.
2. **Las tres preguntas de relevancia, en orden,** con la tabla de exclusiones resumida a una línea por motivo.
3. **Los tres tipos** y sus definiciones.
4. **Las categorías** con su "qué abarca", copiadas de `config.js`. No van las del piloto en `scripts/clasificacion/kaggle_pipeline.py`, que todavía incluye `SINIESTRALIDAD_VIAL`.
5. **El formato de salida:** `relevante`, `tipo`, `categorias_problema`, `categorias_solucion` y `categoria_otra`, con las categorías como lista cerrada. Además, un campo corto `motivo` que diga qué regla aplicó, para poder auditar los descartes. (Propuesta)

Sobre los ejemplos dentro del prompt (few-shot):

- **Las notas que van al prompt no sirven para evaluar** al LLM, porque ya vio la respuesta.
- **El gold tiene solo 4 relevantes.** No alcanzan para usar algunas como ejemplo y medir con el resto. Hace falta otra tanda etiquetada con esta guía, con más notas relevantes y con ejemplos de las categorías que hoy no tienen ninguno. (Propuesta)

## Pendiente

- **Seis categorías sin ejemplo:** tres de problemas, las dos "otro" y no hay ningún caso de tipo `problema` puro. Las definiciones de esas categorías son propuestas.
- **Diferencias con residuos:** residuos se reconcilió el 25/11 y tiene su propia [guía](guia-residuos.md). La diferencia principal: allá, la crítica a un gobierno sin una medida entra como falla regulatoria; acá queda afuera.
- **Fuentes con origen a confirmar:** ECOBIZ figura como portal argentino en el relevamiento, pero falta verificar si es cordobés. El origen de Bioplastics News no está confirmado. Las dos son de residuos.
