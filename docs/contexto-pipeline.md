# Pipeline de problemáticas: contexto

Última actualización: 4/11/2026. Equipo: Ignacio, Lauti y Diego.

## Objetivo

Encontrar los problemas más recurrentes en las fuentes de información de cada track, para descubrir alguno que el equipo no conocía.

El resultado es el punto 0 para elegir la problemática y plantear el producto. También sirve como evidencia para el pitch.

## Decisiones tomadas

- **Orden de los tracks:** primero residuos y, si funciona, el mismo proceso con los otros tres. No llegar a los otros tres es aceptable.
- **Tamaño del dataset:** el objetivo es 10.000 notas por track. En residuos, más de 10.000 notas mencionan el tema, pero falta medir cuántas son útiles. Los otros tres tracks no se midieron.
- **Fecha:** se guarda para filtrar y comparar, no como peso fijo desde el inicio. Un problema que persiste de 2021 a 2026 es justo lo que se busca.
- **Geografía:** tienen más peso los problemas que aparecen en varios países y los locales. Faltan los valores y definir qué cuenta como local.
- **Fuentes y arquitectura:** las posibles fuentes están en [Fuentes para el dataset del pipeline.md](Fuentes%20para%20el%20dataset%20del%20pipeline.md) y el boceto digitalizado, en [pipeline-arquitectura.html](pipeline-arquitectura.html).
- **Función de los resultados:** son un insumo para decidir. No prueban por sí solos que un problema importe.

- **Notas de soluciones:** son las más valiosas para encontrar patrones y contrastar con soluciones ya validadas, como [Reaquila en Visión Sustentable](https://www.visionsustentable.com/2026/06/24/reaquila-plataforma-gestion-residuos-reciclaje-empresas/). Una nota así prueba que la solución existe, no que esté validada. Falta definir qué evidencia cuenta como validación.

- **Arquitectura:** después del dataset van filtro y limpieza, clasificación en problema, solución, ambas u otra, dos ramas de análisis, tres vistas (ranking, grafo y mapa de embeddings) y contraste con soluciones validadas y datos abiertos. Sigue en duda si hace falta una muestra de control.

### Evaluación de volumen (4/11/2026, 23:34, descargas en curso)

**Actualización del 5/11/2026, 00:49:** terminaron todas las descargas salvo Futuro Sustentable, que no tiene datos. Hay 47.944 notas únicas en 33 Parquet: 41.140 con cuerpo, 29.413 con cuerpo y mención, y 20.045 que además mencionan el tema en título o bajada. De las 29.413, 9.028 son de medios argentinos, 1.076 de Mongabay, 3.284 de medios de España y 16.025 de otros países e idiomas. Unas 1.555 de las notas argentinas son de secciones de Infobae de otros países. La tabla de abajo es la medición anterior, sin las 19 fuentes especializadas.

Hay 28.072 notas descargadas de residuos, y 13.633 tienen cuerpo y mencionan el tema. Mencionarlo no vuelve útil a una nota: en una muestra informal de 56 títulos, cerca de la mitad parecía útil. Si esa proporción se mantuviera, serían unas 6.800, pero es una lectura rápida, no una medición.

| Fuente | Notas únicas | Con cuerpo | Con cuerpo y mención | Estado |
|---|---:|---:|---:|---|
| TN | 8.245 | 5.018 | 1.592 | En curso, sin Parquet |
| El Doce | 6.194 | 3.835 | 877 | Terminada |
| Resource Recycling | 2.681 | 2.681 | 2.591 | Terminada |
| Infobae | 2.641 | 2.640 | 2.217 | Terminada, solo prioritarias |
| Clarín | 2.609 | 2.604 | 1.553 | Terminada, solo prioritarias |
| Mongabay | 1.718 | 1.718 | 1.076 | Terminada |
| Circular Online | 1.081 | 1.081 | 1.063 | Terminada |
| Visión Sustentable | 829 | 829 | 743 | Terminada |
| Mongabay en inglés | 529 | 529 | 521 | En curso, sin Parquet |
| Ecomundo | 468 | 468 | 333 | Terminada |
| ECOBIZ | 398 | 398 | 395 | Terminada |
| La Nación | 370 | 366 | 364 | Terminada |
| CBA24N | 309 | 308 | 308 | En curso, sin Parquet |
| Grist | Sin datos | Sin datos | Sin datos | Pendiente, después de Mongabay en inglés |
| Futuro Sustentable | Sin datos | Sin datos | Sin datos | Sin archivo en `data/` |
| **Total** | **28.072** | **22.475** | **13.633** | |

Los 10 Parquet ya generados suman 18.989 notas únicas, y 11.212 tienen cuerpo y mención.

Cómo leer la tabla:

- **Mención:** usa `relevante` de `scripts/progreso.py`, con `RAICES_RESIDUOS` en español y `RAICES_INGLES_RESIDUOS` en inglés. Es más estricta que el diccionario completo: en El Doce da 877 notas, contra 1.331 con `diccionario_en_texto`.
- **Duplicados:** las notas son únicas dentro de cada fuente. No se midieron los duplicados entre fuentes.
- **Fuentes en inglés:** aportan 4.175 de las 13.633 notas con mención y cubren desde 2024. Quedan 9.458 en español, no todas de Argentina.
- **Córdoba:** El Doce y CBA24N suman 1.185 notas con mención. La Voz sigue sin acceso resuelto.

Conviene decidir si hacen falta más fuentes cuando terminen las descargas, mirando los huecos y no solo el total: Córdoba y soluciones.

En Infobae y Clarín se decidió bajar solo lo prioritario: tags de residuos y notas de tags amplios con el tema en título, bajada o URL. Quedan sin bajar 5.781 notas en Infobae y 1.894 en Clarín, que se pueden retomar si hace falta.

### Plan de scraping

Cómo funciona cada script: [scrapping-webs.md](scrapping-webs.md).

Este es el plan que planteó Ignacio:

1. Identificar 10 fuentes relevantes, medir cuántos datos aportan y sumar otras si faltan.
2. Catalogar las secciones de cada fuente, como ecología o sustentabilidad.
3. Armar un diccionario amplio de palabras clave por track, que funcione como primer filtro.
4. Lanzar agentes de IA en paralelo, uno por fuente, que ejecuten Playwright en bucle.
5. Escribir una guía de scraping por fuente.
6. Guardar el dataset, quizá en Parquet.

### Medidas de recurrencia

| Grupo | Medida | Qué mira |
|---|---|---|
| Volumen | Cantidad de notas | Cuántas notas hablan del problema |
| Volumen | Hechos distintos | Cuántos eventos separados aparecen |
| Volumen | Medios independientes | Cuántos medios lo cubren por su cuenta |
| Tiempo | Años en que aparece | Si persiste a lo largo de los años |
| Tiempo | Continuidad | Si es parejo durante meses o solo un pico |
| Tiempo | Tendencia | Si crece o baja en los últimos años |
| Alcance | Lugares afectados | En cuántas ciudades o provincias aparece |
| Alcance | Actores afectados | Qué tipos de actores menciona |
| Alcance | Magnitud informada | Qué cifras reportan las notas |
| Respuesta | Soluciones fallidas | Si sigue después de planes o anuncios |
| Respuesta | Origen de la voz | Quién plantea el problema |

## Hechos

### Del evento

- Se puede usar datos externos, llevar trabajo hecho y enviar textos de diarios a una API de IA. Lo confirmó la organización, según Ignacio.
- Día 1: 12/11. Demo Day: 13/11.
- Los criterios de evaluación no están publicados.

### Del equipo

- Ya está inscripto.
- Nadie tiene experiencia directa con residuos.

### De la inspiración

El video "Idea Plotter", de @re_skob, se basa en una receta de Synthetic Beef:

1. Convirtieron 189.495 juegos de Steam en embeddings de 1.024 dimensiones.
2. Buscaron zonas vacías en ese mapa.
3. Generaron ideas para esas zonas y volvieron a medir qué tan cerca quedaban de juegos existentes.

Ese proceso mide qué tan distinta es una idea, no si es buena.

### De las fuentes (probado el 4/11/2026)

| Fuente | Resultado |
|---|---|
| La Nación | Publica sitemaps diarios; su índice histórico cubre 730 días, desde noviembre de 2024 |
| La Nación | Su `robots.txt` excluye `/buscador` |
| La Voz | Su `robots.txt` excluye a `ChatGPT-User`, `OpenAI`, `ChatGPT`, `FacebookBot` y `Meta AI` |
| La Voz | Sus dos sitemaps probados devolvieron el error 1016 |
| Clarín | Declara sitemaps en su `robots.txt`; su contenido no se revisó |
| Reddit | Su `robots.txt` excluye a cualquier bot genérico |
| GDELT | Rechazó las consultas por límite de frecuencia; no se midió nada |

### Muestra de volumen (La Nación)

Se revisó el día 15 de cada mes de 2025, con 5.305 URLs en total. Tres contenían palabras clave de residuos, y una de ellas era un falso positivo ("televisión basura").

Esto da unas 60 notas relevantes por año si se mira solo la URL. La muestra es muy chica, así que es apenas un orden de magnitud. La búsqueda en el texto completo no se probó.

## Limitaciones del método

- Las noticias muestran lo que se publica, no todo lo que pasa. Un problema frecuente en los diarios no es necesariamente el más grave.
- Lo más recurrente suele ser lo más visible. Eso puede chocar con el objetivo de encontrar algo que no se conocía.
- Que una solución no aparezca en las noticias no significa que no exista.

## Falta aclarar

### Fuentes

- [ ] ¿Qué diarios nacionales y de Córdoba entran?
- [ ] ¿Cómo se accede a La Voz, dado que sus sitemaps fallaron?
- [ ] ¿Hay un archivo de La Nación anterior a noviembre de 2024?
- [ ] ¿Qué foros de sustentabilidad y ecologismo existen?
- [ ] ¿Se incluyen redes sociales? ¿Por qué vía permitida?
- [ ] ¿GDELT aporta cobertura argentina suficiente?
- [ ] ¿Qué fuentes sirven para relevar soluciones existentes?
- [ ] ¿Qué permiten los términos de uso de cada medio?

### Datos

- [ ] ¿Cuántas de las notas que mencionan residuos son útiles? ¿Qué se hace si un track no llega a 10.000?
- [ ] ¿Alcanza con recorrer secciones ambientales o hay notas de residuos en otras secciones?
- [ ] ¿Los agentes recorren cada página o generan un script por fuente que después se repite?
- [ ] ¿Qué palabras entran en el diccionario de cada track?
- [ ] ¿Se puede obtener el texto completo con los muros de pago?
- [ ] ¿Qué campos se guardan de cada nota, además de título, fecha y texto?
- [ ] ¿Cómo se detectan las notas duplicadas o replicadas?

### Método

- [ ] ¿La unidad de análisis es la nota o el hecho?
- [ ] ¿Las categorías se definen antes o surgen de los datos?
- [ ] ¿Se usan embeddings, clasificación con LLM o ambos?
- [ ] ¿Cómo se combinan las 11 medidas? ¿O se muestran por separado?
- [ ] ¿Qué significa exactamente "sin solución"?
- [ ] ¿Cómo se valida un resultado con personas del sector?

### Ejecución

- [ ] ¿Qué proveedor de IA se usa y con qué presupuesto?
- [ ] ¿Quién se encarga de cada parte?
- [ ] ¿Qué tiene que estar listo antes del 12/11?
