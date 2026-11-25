# Guía de etiquetado: residuos

Última actualización: 25/11/2026.

Reglas para decidir si una nota del track de residuos es relevante y cómo se clasifica. Salen de la reconciliación entre Ignacio y Lauti sobre las 25 notas de la muestra `2026-11-25-s42`. Sirven para dos cosas: etiquetar las próximas tandas con el mismo criterio y escribir el prompt del LLM. La guía hermana es [`guia-movilidad.md`](guia-movilidad.md).

- **Base:** [`reconciliacion/residuos-gold.json`](reconciliacion/residuos-gold.json), con la etiqueta final de cada nota, y [`reconciliacion/residuos-informe.md`](reconciliacion/residuos-informe.md), con el acuerdo y las decisiones.
- **De dónde sale cada regla:**
  - "Gold": la respalda al menos una nota decidida en la reconciliación.
  - "Decisión del 25/11": la definieron Ignacio y Lauti al cerrar esta guía.
  - "Propuesta": todavía no tiene ninguna nota que la respalde.

## Qué mostró el gold

| Medida | Valor |
|---|---|
| Notas relevantes | 17 de 25 |
| Relevantes en diarios (TN, Infobae, Clarín, El Doce y CBA24N) | 3 de 5 |
| Relevantes en medios especializados (las otras 20 fuentes) | 14 de 20 |
| Tipo de las relevantes | 9 ambas, 4 solución y 4 problema |
| Acuerdo inicial entre Ignacio y Lauti en relevancia | 15 de 25, con kappa 0,14 |

- **Residuos tiene mucho menos ruido que movilidad** (17 relevantes contra 4). Pero la muestra tiene una nota por fuente, así que 20 de las 25 son de medios especializados. En el dataset completo, las notas de diarios son el 43 % (17.192 de 40.232). Por eso es probable que la proporción real de relevantes sea más baja. No se midió.
- **En la reconciliación ganó más el criterio amplio, el de Ignacio:** quedó la etiqueta de Ignacio en 10 notas y la de Lauti en 8. Lauti descartaba las notas de política y de empresas puntuales; las cinco terminaron entrando, porque hablan de residuos.
- **"Ambas" es el tipo más común.** Las notas especializadas suelen plantear un problema y una salida en el mismo texto.

## Paso 1: ¿es relevante?

Las preguntas se hacen en orden. A la primera que responde "no relevante", se corta.

1. **¿Hay un residuo en el centro de la nota?** Puede ser basura, reciclaje, separación, disposición final, desechos industriales, vertidos o contaminación por desechos, como los fármacos en ríos o los agrotóxicos en el agua. Las notas de agro, energía o biodiversidad sin un residuo de por medio quedan afuera. (Decisión del 25/11)
2. **¿Es un hecho policial o un accidente puntual?** Un asesinato o la muerte de un recolector quedan afuera, aunque pasen en un basural o en un camión de residuos. (Gold)
3. **¿Describe un problema concreto o una solución concreta?** Una solución puede ser un producto, una tecnología, una obra, un servicio, un programa, un contrato o una medida con presupuesto. Quedan afuera los anuncios de agenda, las notas superficiales y las campañas de sensibilización. (Gold y decisión del 25/11)

Si pasa las tres preguntas, es relevante. El idioma no importa: el gold tiene notas relevantes en inglés, portugués, italiano, alemán y polaco. (Gold)

### Gobierno, empresas y campañas

- **Entra la medida concreta de gobierno,** aunque sea administrativa: un contrato de recolección y reciclaje (Lincoln, £50 millones) o una convocatoria con presupuesto (Anci-Conai, 1,5 millones de euros). (Decisión del 25/11)
- **Entra la falla o la inacción regulatoria frente a un problema concreto,** aunque no traiga una medida. Por ejemplo, las ciudades polacas que critican la pasividad del gobierno con la responsabilidad extendida del productor, o el control a 155 empresas en Filipinas. Esta regla es propia de residuos, que tiene la categoría `FALLA_REGULATORIA_Y_FISCALIZACION`. En movilidad, la crítica sin medida queda afuera. (Decisión del 25/11)
- **Entra la empresa puntual si el tema es el residuo.** Por ejemplo, Unilever no cumple sus metas de reciclabilidad de envases. (Gold)
- **Quedan afuera las campañas escolares o de sensibilización,** aunque informen cantidades recolectadas. Por ejemplo, "Mostri del riciclo" (1.000 clases juntando RAEE) y el concurso de Gauteng (10.747 kg de vidrio). (Decisión del 25/11)
- **Ojo con el límite:** un fondo público para campañas de comunicación entra, porque es una medida con presupuesto. La campaña en sí, no. Conviene revisar este criterio con más casos. (Decisión del 25/11)

### Consejos caseros

Un consejo que propone reaprovechar un desecho cuenta como solución. Por ejemplo, secar las cáscaras de cítricos para usarlas en la cocina o el jardín. (Gold) En movilidad, los consejos de manejo quedaron afuera, porque no plantean ni un problema ni una solución.

### Exclusiones del gold, por motivo

| Motivo | Notas | Ejemplo del gold |
|---|---:|---|
| Agro, energía o política sin residuo | 3 | Riego solar en Ruanda; el hotel que se volvió "mini farmer"; un libro sobre reformas en las repúblicas andinas |
| Campañas escolares o de sensibilización | 2 | "Mostri del riciclo"; concurso de vidrio en Gauteng |
| Hecho policial o accidente | 2 | Los asesinos de Ángeles y el CEAMSE; un recolector que murió aplastado por el camión |
| Anuncio de agenda, superficial | 1 | "Save the Date: Chemical Recycling Europe Forum 2025" |

## Paso 2: tipo

Solo se elige en las notas relevantes. Hay tres opciones. (Decisión del 25/11, igual que en movilidad)

| Tipo | Cuándo | Ejemplo del gold |
|---|---|---|
| `problema` | Describe un problema y no presenta una solución concreta | Fármacos en 1 de cada 4 ríos; agrotóxicos en el agua de Pergamino; basural en Barrio Arenales; control en Filipinas |
| `solucion` | Presenta una solución concreta. Si menciona el problema, es solo como contexto | Contrato de Lincoln; fondos Anci-Conai; "wood vaulting"; cáscaras de cítricos |
| `ambas` | Describe un problema y presenta una solución para ese problema, aunque la solución sea general, como la economía circular | Usinas de Criciúma; vertido ilegal de escombros en Victoria con más control y trazabilidad; desperdicio de reciclables en el mundo |

En la reconciliación se eligió "ambas" cada vez que la nota "habla del problema y de la solución". (Gold, 7 notas)

## Paso 3: categorías

Una nota puede tener una o más categorías de cada lado, y se marcan todas las que la nota describe. En el gold es habitual: Unilever tiene 3 problemas y 2 soluciones. (Gold) Una categoría que la nota solo menciona de pasada no se marca. (Propuesta, igual que en movilidad)

Las listas son las de [`config.js`](config.js). Entre paréntesis, cuántas notas del gold usan cada categoría.

### Problemas

| Categoría | Qué abarca | Ejemplos del gold |
|---|---|---|
| `CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS` (6) | Contaminación del agua, el suelo o el ambiente por desechos, plásticos o químicos | Fármacos en ríos; agrotóxicos en Pergamino; basural en Barrio Arenales; envases de Unilever |
| `FALLA_REGULATORIA_Y_FISCALIZACION` (5) | Normas que no se cumplen o no se controlan, y gobiernos que no actúan | Filipinas; Polonia; Victoria; Unilever pide política pública |
| `ESTANCAMIENTO_SEPARACION_Y_RECICLAJE` (5) | Tasas de reciclaje bajas o estancadas, y materiales reciclables que se pierden | 200.000 millones de euros en reciclables desperdiciados; Unilever; Polonia |
| `GESTION_DEFICIENTE_RESIDUOS` (4) | Gestión deficiente de cualquier residuo: basurales, vertido ilegal, residuos especiales, de construcción o RAEE | Basural en Barrio Arenales; vertido ilegal de escombros en Victoria; construcción y metalurgia (CIRCOM) |
| `BARRERAS_DE_MERCADO_Y_ECONOMICAS` (4) | Costos, precios, mercados o incentivos que traban el reciclaje o la circularidad | Efectos rebote de la economía circular; reciclables que valen más que el petróleo |
| `COLAPSO_Y_SATURACION_DISPOSICION_FINAL` (1) | Rellenos, vertederos o sitios de disposición final saturados | Criciúma |
| `DESPERDICIO_ALIMENTARIO_Y_ORGANICOS` (1) | Desperdicio de alimentos y residuos orgánicos | Carta de la ciudad de Nelson |
| `CONFLICTO_TERRITORIAL_Y_LABORAL` (0) | Conflictos con vecinos, recuperadores o trabajadores por la gestión de residuos (propuesta) | Sin ejemplo |
| `EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES` (0) | Vertidos líquidos de industrias y lixiviados de basurales (propuesta) | Sin ejemplo |
| `OTRO_PROBLEMA_RESIDUOS` (0) | Ninguna de las anteriores. Requiere describir el problema en texto libre | Sin ejemplo |

`GESTION_DEFICIENTE_RESIDUOS` se llamaba `GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE`. El 25/11 se amplió a cualquier residuo y se renombró, porque en la práctica ya se usaba así. (Decisión del 25/11)

### Soluciones

| Categoría | Qué abarca | Ejemplos del gold |
|---|---|---|
| `MODELOS_CIRCULARES_Y_REUTILIZACION` (6) | Economía circular, reutilización y responsabilidad extendida del productor | CIRCOM; Unilever; Polonia; efectos rebote |
| `COMPOSTAJE_Y_BIOTRANSFORMACION` (4) | Compostaje y otros tratamientos biológicos de orgánicos, incluido el reaprovechamiento de restos vegetales | Cáscaras de cítricos; "wood vaulting"; Nelson; Criciúma |
| `UPCYCLING_Y_VALORIZACION_MATERIAL` (2) | Convertir residuos en materiales o productos nuevos | Criciúma; reciclables que valen más que el petróleo |
| `VALORIZACION_ENERGETICA_BIOGAS` (2) | Obtener energía o biogás de residuos | Criciúma; Nelson |
| `ECO_DISENO_Y_BIOMATERIALES` (1) | Envases y productos diseñados para reciclarse, o materiales de origen biológico | Unilever |
| `TRAZABILIDAD_DIGITAL_Y_SOFTWARE` (1) | Seguimiento digital de los residuos, desde quien los genera hasta su disposición | Control a los contenedores en Victoria |
| `LOGISTICA_INVERSA_Y_RECOLECCION_INTELIGENTE` (1) | Servicios y sistemas de recolección y de devolución de residuos | Contrato de Lincoln |
| `OTRA_SOLUCION_RESIDUOS` (1) | Ninguna de las anteriores. Requiere describir la solución en texto libre | Financiamiento público para campañas (Anci-Conai) |

Si un mismo texto libre de "otro" se repite en varias notas, es candidato a categoría nueva.

## Alcance geográfico: no lo decide nadie

El alcance sale del origen del medio que publica la nota, con el diccionario [`scripts/diccionarios/alcance_fuentes.py`](../scripts/diccionarios/alcance_fuentes.py). Es igual que en movilidad. (Decisión del 25/11)

| Origen del medio | Alcance | Fuentes de residuos |
|---|---|---|
| Córdoba | `CORDOBA_LOCAL` | El Doce y CBA24N |
| Resto de Argentina | `ARGENTINA_NACIONAL` | TN, Clarín, La Nación, Infobae, Visión Sustentable, Ecomundo y ECOBIZ |
| Resto de América Latina | `LATAM_REGIONAL` | CicloVivo, Abrema y Mongabay (Latam) |
| Resto del mundo | `INTERNACIONAL_GLOBAL` | Las otras 21 fuentes |

## En qué se diferencia de movilidad

| Tema | Movilidad | Residuos |
|---|---|---|
| Crítica al gobierno sin una medida | Afuera | Entra como falla regulatoria |
| Consejos | Los de manejo quedan afuera | Entran los que proponen reaprovechar un desecho |
| Accidentes | Toda la seguridad vial afuera | Afuera los accidentes y hechos policiales puntuales |
| Medida concreta de gobierno | Entra | Entra, incluidos contratos y fondos |
| Nota de otro track | Afuera | Afuera, salvo que haya un residuo en el centro |

## Del gold al prompt

Lo que tiene que llevar el prompt, en este orden:

1. **Qué es el track:** la pregunta 1 del paso 1.
2. **Las tres preguntas de relevancia, en orden,** con las reglas de gobierno, empresas y campañas, y la tabla de exclusiones resumida.
3. **Los tres tipos.** Conviene aclarar que "ambas" es lo habitual cuando la nota plantea una salida.
4. **Las categorías** con su "qué abarca", copiadas de `config.js`. No van las del piloto, en `scripts/clasificacion/kaggle_pipeline.py` y `taxonomia.py`, que todavía usan el nombre viejo `GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE`.
5. **El formato de salida:** `relevante`, `tipo`, `categorias_problema`, `categorias_solucion` y `categoria_otra`, con las categorías como lista cerrada. Además, un campo corto `motivo` que diga qué regla aplicó. (Propuesta)

Sobre los ejemplos dentro del prompt (few-shot):

- **Las notas que van al prompt no sirven para evaluar** al LLM.
- **Hay más margen que en movilidad.** El gold tiene 17 relevantes, así que se pueden separar unas pocas como ejemplos y medir con el resto. Igual, conviene sumar notas de diarios, porque la muestra casi no tiene. (Propuesta)

## Pendiente

- **Tres categorías de problema sin ejemplo:** `CONFLICTO_TERRITORIAL_Y_LABORAL`, `EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES` y `OTRO_PROBLEMA_RESIDUOS`.
- **Contaminación o efluentes:** los fármacos en ríos y los agrotóxicos en el agua se clasificaron como `CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS`, y nadie usó `EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES`. Falta definir dónde termina una y empieza la otra.
- **El límite entre fondos y campañas,** descrito en "Gobierno, empresas y campañas".
- **Notas de diarios:** la muestra tiene solo 5. Las reglas de policiales y accidentes salen de esas pocas.
- **Fuentes con origen a confirmar:** falta verificar si ECOBIZ es cordobés. El origen de Bioplastics News no está confirmado.
