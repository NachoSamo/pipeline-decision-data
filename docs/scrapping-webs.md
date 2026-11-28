# Scraping de webs

Última actualización: 6/11/2026.

Cada fuente tiene su forma de listar y leer notas, porque cada sitio permite y expone cosas distintas. Todos los scripts corren desde la raíz del repo, guardan en `data/` y se pueden cortar y retomar volviendo a ejecutar el mismo comando. Cuántas notas trajo cada fuente está en la [evaluación de volumen](analisis-datasets/contexto-pipeline.md#evaluación-de-volumen-4112026-2334-descargas-en-curso).

| Fuente | Script | Cómo lista | Cómo lee la nota | Pausa |
|---|---|---|---|---|
| El Doce | `scrape_eldoce.py` | API del buscador | La misma API | 4 s |
| Infobae | `scrape_infobae.py` | API de tags | Contenido embebido en la página | 2 s por nota, 4 s en el listado |
| Clarín | `scrape_ldjson.py clarin` | Páginas de tags | JSON-LD de la página | 2 s por nota, 4 s en el listado |
| La Nación | `scrape_ldjson.py lanacion` | Sitemap histórico | JSON-LD de la página | 2 s |
| Visión Sustentable | `scrape_visionsustentable.py` | API de WordPress | La misma API | 4 s |
| Ecomundo | `scrape_ecomundo.py` | API de WordPress | La misma API | 4 s |
| Futuro Sustentable | `scrape_futurosustentable.py` | Sitemaps | Bloque `entry-content` y JSON-LD | 60 s |
| ECOBIZ | `scrape_ecobiz.py` | Buscador | Bloques `post-copete` y `post-desarrollo` | 4 s |
| TN | `scrape_tn.py` | API del buscador | La misma API | 4 s |
| Mongabay | `scrape_mongabay.py` | API de WordPress | La misma API | 10 s |
| CBA24N | `scrape_cba24n.py` | Sitemaps mensuales | JSON-LD y bloque `article-body-content` | 12 s |
| Cadena 3 | `scrape_cadena3.py` | Sitemap de noticias y lista propia | JSON-LD y bloque `cuerpo-nota` | 4 s |
| Resource Recycling, Circular Online y Grist | `scrape_internacional.py` | API de WordPress | La misma API | 4 s |
| Mongabay en inglés | `scrape_internacional.py` | API de WordPress | La misma API | 10 s |
| 19 especializadas | `scrape_especializadas.py` | API de WordPress | La misma API | 4 s; 20 s en Eco dalle Città |

## Cómo leer el progreso

Cada script imprime líneas como esta:

```text
[22:35:52] TN [1/18] residuos: 120 de 503 (24%) | mencionan residuos 104 (87%) | 240/min | faltan 2 min
```

| Parte | Qué indica |
|---|---|
| `[1/18] residuos` | Término en curso y cuántos hay en total |
| `120 de 503 (24%)` | Avance de ese término o de toda la fuente |
| `mencionan residuos 104 (87%)` | Notas nuevas con alguna raíz de `RAICES_RESIDUOS`. Mide el ruido, no si la nota es útil |
| `240/min` | Ritmo de esta corrida |
| `faltan 2 min` | Tiempo estimado para ese término o fuente |

Los términos ya completos muestran "ya estaba descargado". Los scripts que estaban corriendo cuando se agregó este formato lo muestran recién al ejecutarlos de nuevo.

## Qué busca cada script

Las palabras están en [`scripts/diccionarios/keywords_residuos.py`](../scripts/diccionarios/keywords_residuos.py) y [`keywords_soluciones.py`](../scripts/diccionarios/keywords_soluciones.py). Las de problemáticas están en [`keywords_biodiversidad.py`](../scripts/diccionarios/keywords_biodiversidad.py), [`keywords_movilidad.py`](../scripts/diccionarios/keywords_movilidad.py) y [`keywords_senales.py`](../scripts/diccionarios/keywords_senales.py) y se describen en [su sección](#dataset-de-problemáticas-biodiversidad-y-movilidad). Las de residuos son:

- **`BUSQUEDAS_RESIDUOS`:** términos para buscadores.
- **`CORE_KEYWORDS_RESIDUOS`:** expresiones regulares que marcan temas específicos.
- **`BUSQUEDAS_PRECISAS_RESIDUOS`:** términos con menos ruido, sin los que en El Doce trajeron más resultados irrelevantes. Los usan TN y Mongabay.
- **`BUSQUEDAS_INGLES_RESIDUOS` y `RAICES_INGLES_RESIDUOS`:** términos y raíces para fuentes en inglés.
- **`TAGS_INFOBAE_*` y `TAGS_CLARIN_*`:** tags de cada medio, separados en residuos y amplios.
- **`RAICES_RESIDUOS`:** raíces sin tildes para filtrar URLs de sitemaps y priorizar notas.
- **`RAICES_ITALIANO_RESIDUOS`, `RAICES_PORTUGUES_RESIDUOS`, `RAICES_POLACO_RESIDUOS` y `RAICES_ALEMAN_RESIDUOS`:** raíces para las especializadas en esos idiomas. En esas fuentes, `diccionario_en_texto` guarda estas raíces.

## Qué guarda

Cada script deja estos archivos en `data/residuos/`, o en `data/soluciones/crudo/` para soluciones:

| Archivo | Contenido | ¿En Git? |
|---|---|---|
| `<fuente>_residuos.parquet` | Notas únicas | Sí |
| `<fuente>_residuos.jsonl` | Filas crudas, una por nota y término | No |
| `<fuente>_residuos.listado.jsonl` | URLs pendientes de leer | No |
| `<fuente>_residuos.progreso.json` | Última página de cada término | No |

Columnas del Parquet:

| Columna | Qué indica |
|---|---|
| `id`, `fuente`, `url` | Identificación de la nota |
| `titulo`, `bajada`, `body`, `fecha` | Contenido |
| `seccion`, `tags`, `tipo` | Clasificación del propio medio |
| `terminos_busqueda` | Términos o tags que trajeron la nota |
| `terminos_en_texto` | Cuáles de esos términos aparecen de verdad en el texto |
| `diccionario_en_texto` | Términos de `BUSQUEDAS_RESIDUOS` presentes en el texto |
| `keywords_core` | Expresiones de `CORE_KEYWORDS_RESIDUOS` presentes en el texto |
| `edicion` | Solo Infobae: primera parte de la URL, por ejemplo `mexico` |
| `acceso_libre` | Solo Clarín y La Nación: si el medio marca la nota como de acceso libre |

Para descartar ruido, conviene filtrar por `diccionario_en_texto`. Solo busca frases exactas sin distinguir tildes: "residuos" no encuentra "residuo".

Estos son los Parquet por fuente que deja cada descarga. Desde el 8/11/2026 se consolidan en un archivo por dataset, con otro esquema: ver [Limpieza y consolidación](#limpieza-y-consolidación).

## Por fuente

### El Doce

- **Comando:** `python scripts/scrape_eldoce.py`
- **Busca:** todos los términos de `BUSQUEDAS_RESIDUOS`.
- **Cómo:** pide `/pf/api/v3/content/fetch/search-api`, la misma API que usa "Cargar más notas". Devuelve 20 notas completas por pedido.
- **Límites:** el buscador trae resultados aproximados. De 6.194 notas únicas, 1.331 mencionan el diccionario. Los videos no tienen cuerpo.
- **Permisos:** `robots.txt` no excluye esta vía. Los términos piden no copiar sin autorización y limitan el acceso automático a un ritmo humano.

### Infobae

- **Comando:** `python scripts/scrape_infobae.py --solo-prioritarias`. Sin esa opción también baja las 5.781 notas restantes de tags amplios.
- **Busca:** tags de residuos y amplios.
- **Cómo:** lista con `/pf/api/v3/content/fetch/content-feed`, que no trae cuerpo, y lee cada nota desde `Fusion.globalContent`. Primero van los tags de residuos, después las notas de tags amplios con el diccionario en título o bajada, y al final el resto.
- **Límites:** excluye EFE, igual que la página de tags. Incluye ediciones de otros países.
- **Permisos:** `robots.txt` excluye `/buscador`, así que no se usa el buscador ni su API. El punto 3.4 de los términos prohíbe copiar o reutilizar contenidos sin autorización.

### Clarín

- **Comando:** `python scripts/scrape_ldjson.py clarin --solo-prioritarias`. Sin esa opción también baja las 1.894 notas restantes de tags amplios.
- **Busca:** tags de residuos y amplios.
- **Cómo:** recorre `/tema/<tag>.html` y `/tema/<tag>/page/N`, y lee el `articleBody` del JSON-LD de cada nota.
- **Límites:** las notas pagas pueden quedar incompletas; `acceso_libre` lo indica.
- **Permisos:** `robots.txt` excluye `/api/`, que no se usa. No encontré una cláusula sobre copia o bots al buscar por palabras clave en los términos, pero no los leí completos.

### La Nación

- **Comando:** `python scripts/scrape_ldjson.py lanacion`
- **Busca:** URLs con alguna raíz de `RAICES_RESIDUOS`.
- **Cómo:** recorre los 730 sitemaps diarios de `sitemap-index-historico.xml` y lee el JSON-LD de cada nota elegida.
- **Límites:** cubre solo unos 2 años y deja afuera notas relevantes cuya URL no tenga la raíz.
- **Permisos:** `robots.txt` excluye `/buscador` y `/pf/api/`, así que no se usan.

### Visión Sustentable

- **Comando:** `python scripts/scrape_visionsustentable.py`
- **Busca:** todos los términos de `BUSQUEDAS_RESIDUOS`.
- **Cómo:** pide `/wp-json/wp/v2/posts?search=<término>`, con 100 notas completas por pedido.
- **Permisos:** `robots.txt` no excluye nada.

### Ecomundo

- **Comando:** `python scripts/scrape_ecomundo.py`
- **Busca:** la categoría Reciclado completa y todos los términos de `BUSQUEDAS_RESIDUOS`.
- **Cómo:** usa la misma API de WordPress que Visión Sustentable.
- **Límites:** es una fuente chica. La categoría Reciclado tiene 38 notas.
- **Permisos:** `robots.txt` solo excluye `/wp-admin/`.

### Futuro Sustentable

- **Comando:** `python scripts/scrape_futurosustentable.py`
- **Busca:** URLs con alguna raíz de `RAICES_RESIDUOS`.
- **Cómo:** lista los `post-sitemap` y lee el JSON-LD y el bloque `entry-content` de cada nota.
- **Límites:** tarda 1 minuto por nota y deja afuera notas relevantes cuya URL no tenga la raíz.
- **Permisos:** `robots.txt` excluye `/?s=` y cualquier URL con `?`, y pide 60 segundos entre pedidos. Por eso no se usa el buscador ni la API.

### ECOBIZ

- **Comando:** `python scripts/scrape_ecobiz.py`
- **Busca:** todos los términos de `BUSQUEDAS_RESIDUOS`.
- **Cómo:** pide `/resultados-busqueda/<término en base64>/pg-N` y lee los bloques `post-copete` y `post-desarrollo` de cada nota.
- **Permisos:** `robots.txt` no excluye el buscador ni las notas.

### TN

- **Comando:** `python scripts/scrape_tn.py`
- **Busca:** `BUSQUEDAS_PRECISAS_RESIDUOS`, incluida "residuos sustentables".
- **Cómo:** pide `/pf/api/v3/content/fetch/search-api`, la misma API que usa su página de resultados. Devuelve 20 notas completas por pedido.
- **Límites:** deja un término si encuentra 10 páginas seguidas sin notas que mencionen residuos, o si el servidor falla 3 veces en una página. El buscador trae mucho ruido en páginas profundas: en "basura", la página 270 dio error 504 y las últimas revisadas casi no aportaban.
- **Permisos:** `robots.txt` excluye `/search/` y `meta-api`, que no se usan.

### Mongabay

- **Comando:** `python scripts/scrape_mongabay.py`
- **Busca:** `BUSQUEDAS_PRECISAS_RESIDUOS`.
- **Cómo:** pide `/wp-json/wp/v2/posts?search=<término>`, con 100 notas completas por pedido.
- **Límites:** es una fuente regional. Una búsqueda de varias palabras puede traer notas que no contienen la frase exacta, y las notas son largas, así que conviene revisar `terminos_en_texto`.
- **Permisos:** `robots.txt` no excluye rutas y pide 10 segundos entre pedidos.

### CBA24N

- **Comando:** `python scripts/scrape_cba24n.py`
- **Busca:** URLs con alguna raíz de `RAICES_RESIDUOS`.
- **Cómo:** recorre unos 100 sitemaps mensuales desde 2017, y lee el JSON-LD y el bloque `article-body-content` de cada nota.
- **Límites:** deja afuera notas relevantes cuya URL no tenga la raíz. Con 4 segundos de pausa, el sitio respondió 429 tras 257 notas; por eso ahora usa 12 segundos.
- **Permisos:** `robots.txt` excluye `/search` y `/api`, que no se usan. También excluye por nombre a `ClaudeBot`, `GPTBot`, `CCBot`, `Bytespider`, `Amazonbot`, `Applebot-Extended` y `meta-externalagent`, así que hay que decidir si estos textos pueden pasar por un LLM.

### Cadena 3

**Dejada de lado el 4/11/2026:** la primera corrida encontró 1 sola nota.

- **Comando:** `python scripts/scrape_cadena3.py`
- **Busca:** URLs recientes con alguna raíz de `RAICES_RESIDUOS`, y las URLs de `data/cadena3_urls.txt`.
- **Cómo:** lee `feed/sitemap-news.xml`, que trae unas 180 notas recientes, y el JSON-LD y el bloque `cuerpo-nota` de cada nota. Volver a ejecutarlo suma notas nuevas.
- **Límites:** sin lista propia casi no tiene historial.
- **Permisos:** `robots.txt` excluye `/pagina/buscador?q` y `/pagina/tag?q`. Las páginas `/pagina/tag/<tema>` cargan los resultados con una verificación anti-bots (Firebase App Check con reCAPTCHA), que el script no intenta esquivar.

Para sumar notas de búsquedas hechas a mano, abrí el buscador, ejecutá esto en la consola del navegador en cada página de resultados y pegá el resultado en `data/cadena3_urls.txt`, una URL por línea:

```js
copy([...new Set([...document.querySelectorAll("a.gs-title")].map(a => a.href))].join("\n"))
```

### Fuentes internacionales

- **Comando:** `python scripts/scrape_internacional.py`, o con las fuentes elegidas: `resourcerecycling`, `circularonline`, `mongabayen` y `grist`.
- **Busca:** `BUSQUEDAS_INGLES_RESIDUOS`, en notas publicadas desde el 1/1/2024.
- **Cómo:** pide `/wp-json/wp/v2/posts?search=<término>&after=2024-01-01T00:00:00`, con 100 notas completas por pedido.
- **Límites:** la búsqueda puede traer notas que no contienen la frase exacta. "open dump" trajo 197 notas en Mongabay en inglés, y solo 74 contenían algún término del diccionario.
- **Permisos:** `robots.txt` no excluye estas rutas ni estos bots de IA. Mongabay en inglés pide 10 segundos entre pedidos.

### Fuentes especializadas

- **Comando:** `python scripts/scrape_especializadas.py`, o con las fuentes elegidas, por ejemplo `zerowasteeurope globalrec`. Las claves están en `FUENTES`, dentro del script.
- **Busca:** un solo término por idioma, desde el 1/1/2024: "residuos", "waste", "rifiuti", "resíduos", "odpady" o "Abfall".
- **Cómo:** pide `/wp-json/wp/v2/posts?search=<término>&after=2024-01-01T00:00:00`, con 100 notas completas por pedido. Baja una fuente por vez y, si una falla, sigue con la próxima. Al final indica cuáles quedaron incompletas y el comando para retomarlas.
- **Límites:** el total del 5/11/2026 era de 14.984 resultados brutos en 170 páginas. Un solo término no encuentra todo lo que usa otras palabras, y Recycling Portal se busca solo con "waste", aunque publica en varios idiomas. En Inside Waste, muchas notas son muy cortas.
- **Permisos:** `robots.txt` no excluye la API ni a los bots de Claude en estas fuentes. Residuos Profesional, Portal Komunalny, Recycling International, Envirotec y Ecoticias prohíben reproducir o distribuir sin permiso. Los términos se revisaron por palabras clave, sin leerlos completos: el detalle está en [Fuentes para el dataset del pipeline.md](analisis-fuentes/Fuentes%20para%20el%20dataset%20del%20pipeline.md#más-fuentes-con-api-de-wordpress).

### Bloomberg (sin script)

No se scrapea. Sus términos prohíben scrapers, bots, minería de datos y crear bases de datos sin consentimiento escrito, y su `robots.txt` excluye `/search`.

## Dataset de soluciones

Reutiliza estos scripts con otro diccionario, solo desde 2024. Lo activa [`scripts/soluciones.py`](../scripts/soluciones.py), y los términos están en [`keywords_soluciones.py`](../scripts/diccionarios/keywords_soluciones.py).

- **Todas las fuentes en paralelo:** `python scripts/soluciones.py todas`. Deja un log por fuente en `data/soluciones/crudo/logs/`.
- **Una fuente:** `python scripts/soluciones.py tn`.
- **Fallos:** relanza una fuente solo si falló la red, y nunca insiste ante un 403 o 429.
- **Separar:** `python scripts/separar_por_track.py` escribe `data/soluciones/<track>/<fuente>.parquet`. Asigna tracks por raíces en título o bajada, deja afuera lo anterior a 2024 y descarta las notas sin track. Después, `limpiar.py` une esas carpetas en `data/soluciones.parquet`.
- **Límites:** Infobae y Clarín bajan solo las notas prioritarias. El tag `tecnologia` de Infobae tiene un tope de 10.000 notas y llega hasta febrero de 2025. "drones" y "sensores" traen mucho ruido en TN y El Doce.

Los temporales de residuos se borraron: volver a correr un script de residuos empieza de cero y, al terminar, reescribe su Parquet.

## Dataset de problemáticas (biodiversidad y movilidad)

Reutiliza estos scripts para buscar problemas, no soluciones, en dos verticales. El porqué está en [`circuito-problematicas.md`](circuito-problematicas.md) y las cifras, en el [análisis de biodiversidad](analisis-datasets/analisis-dataset-biodiversidad.md). Los términos están en [`keywords_biodiversidad.py`](../scripts/diccionarios/keywords_biodiversidad.py), [`keywords_movilidad.py`](../scripts/diccionarios/keywords_movilidad.py) y [`keywords_senales.py`](../scripts/diccionarios/keywords_senales.py), que tiene las señales comunes.

No usa la variable `DATASET`. Lo activan dos scripts propios, que aceptan `--vertical biodiversidad` (por defecto) o `--vertical movilidad`:

- **[`scrape_problematicas.py`](../scripts/scrape_problematicas.py):** fuentes con API de WordPress. Llama a `scrape_wordpress.descargar` con otra carpeta y sin sufijo.
- **[`scrape_diarios_problematicas.py`](../scripts/scrape_diarios_problematicas.py):** los 6 diarios. Antes de llamar a sus scripts, reemplaza en memoria el diccionario, las etiquetas y las rutas de residuos por los de la vertical, sin modificar esos archivos.

Una terminal por fuente, y nunca la misma fuente en dos verticales a la vez, ni al mismo tiempo que una descarga de residuos o soluciones.

| Fuente | Script | Vertical | Cómo lista | Pausa |
|---|---|---|---|---|
| Mongabay | `scrape_problematicas.py mongabay` | Biodiversidad | API de WordPress, desde 2021 | 10 s |
| Mongabay en inglés | `scrape_problematicas.py mongabayen` | Biodiversidad | API de WordPress, desde 2021 | 10 s |
| Grist, Ecoticias, CicloVivo, Visión Sustentable y Ecomundo | `scrape_problematicas.py <fuente>` | Las dos | API de WordPress, desde 2021 | 4 s |
| El Doce | `scrape_diarios_problematicas.py eldoce` | Las dos | API del buscador | 4 s |
| TN | `scrape_diarios_problematicas.py tn` | Las dos | API del buscador | 4 s |
| Infobae | `scrape_diarios_problematicas.py infobae` | Biodiversidad | API de tags, solo prioritarias | 2 s por nota, 4 s en el listado |
| Clarín | `scrape_diarios_problematicas.py clarin` | Las dos | Páginas de tags, solo prioritarias | 2 s por nota, 4 s en el listado |
| La Nación | `scrape_diarios_problematicas.py lanacion` | Las dos | Sitemap histórico, por `RAICES_<VERTICAL>` | 2 s |
| CBA24N | `scrape_diarios_problematicas.py cba24n` | Las dos | Sitemaps mensuales, por `RAICES_<VERTICAL>` | 20 s |

Cómo correrlo:

```bash
python scripts/scrape_problematicas.py --selfcheck
python scripts/scrape_problematicas.py --listar --vertical movilidad
python scripts/scrape_problematicas.py mongabay
python scripts/scrape_problematicas.py grist --vertical movilidad
python scripts/scrape_diarios_problematicas.py --selfcheck
python scripts/scrape_diarios_problematicas.py clarin --limite 5
python scripts/scrape_diarios_problematicas.py tn --vertical movilidad
```

### Qué busca

- **`BUSQUEDAS_<VERTICAL>`, `BUSQUEDAS_INGLES_<VERTICAL>` y `BUSQUEDAS_PORTUGUES_<VERTICAL>`:** términos del tema, por idioma de la fuente.
- **`RAICES_<VERTICAL>`:** raíces sin tildes, en español, para filtrar URLs de sitemaps y medir el ruido en el progreso.
- **`TAGS_INFOBAE_*_<VERTICAL>` y `TAGS_CLARIN_*_<VERTICAL>`:** etiquetas probadas el 5/11 y el 6/11/2026. De las amplias solo se bajan notas con el tema en título o bajada.
- **`SENALES_PROBLEMA` y `SENALES_OPINION`:** palabras en español, inglés y portugués que marcan cada nota. No filtran.

### Qué guarda

Cada fuente deja sus archivos en `data/biodiversidad/` o `data/movilidad/`, sin sufijo: `<fuente>.parquet`, y fuera de Git `<fuente>.jsonl`, `<fuente>.listado.jsonl` y `<fuente>.progreso.json`. Los mismos campos que en residuos, más estos:

| Columna | Qué indica |
|---|---|
| `vertical` | `biodiversidad` o `movilidad` |
| `tipo_voz` | `diario`, `medio_especializado` u `opinion`. Es `opinion` si la sección o las etiquetas lo indican |
| `senal_problema` | Señales de problema encontradas en el texto, vacía si no hay |
| `senal_opinion` | Señales de opinión o voz especializada encontradas, vacía si no hay |

Las señales se buscan como palabra completa, con hasta 3 letras de más para plurales y femeninos. Así "ong" no coincide con "ongoing". `keywords_core` usa las expresiones de residuos y no sirve en este dataset.

La limpieza del 8/11/2026 elimina `senal_problema` y `senal_opinion`, y reemplaza `vertical` por `tracks` en el archivo consolidado.

### Diferencias con residuos

- **El Doce:** el buscador falla en páginas profundas (502 en la 111 de "colectivos", 504 en la 81 de "veredas"). Pasada la página 20, un error del servidor da el término por terminado. Un 403 o 429 corta siempre.
- **TN:** el buscador responde 400 desde la página 501, como en "trenes". Se trata igual que en El Doce. Como en residuos, TN deja un término tras 10 páginas seguidas sin notas que mencionen el tema; acá se mide con `RAICES_<VERTICAL>`.
- **Clarín, Infobae y CBA24N:** se saltea una nota solo si redirige en círculo. Cualquier otra falla sigue cortando.
- **CBA24N:** usa 20 segundos de pausa, porque respondió 429 con 12 segundos en movilidad.
- **Infobae en movilidad:** no se corrió (decisión del 6/11). Sus etiquetas de movilidad son muy amplias y tardaría más de 8 horas.
- **CBA24N en movilidad:** lista solo las 1.083 notas con raíces específicas. La lista completa quedó en `cba24n.listado.completo.jsonl`, fuera de Git. Se bajaron 731: el sitio respondió 429 dos veces, también con 20 segundos, y se decidió parar el 6/11. Se puede retomar volviendo a correr el mismo comando.
- **Para sumar términos:** se vuelve a correr la fuente y solo busca los nuevos. En La Nación y CBA24N hay que borrar `<fuente>.listado.jsonl` para que vuelva a listar con las raíces nuevas.

Los permisos de cada fuente son los mismos que en residuos, descritos arriba.

## Limpieza y consolidación

[`scripts/limpiar.py`](../scripts/limpiar.py) une los Parquet por fuente en `data/biodiversidad.parquet`, `data/movilidad.parquet`, `data/residuos.parquet` y `data/soluciones.parquet`, con el mismo esquema. Recorta el pie de suscripción, descarta notas sin cuerpo, sin fecha, de título corto o seriado, deduplica por `id`, título normalizado y cuerpo, y después borra los Parquet por fuente. Los criterios y las cifras están en [`contexto-pipeline.md`](analisis-datasets/contexto-pipeline.md#limpieza-y-consolidación-8112026).

```bash
python scripts/limpiar.py --selfcheck
python scripts/limpiar.py --simular
python scripts/limpiar.py
```

- **`--simular`:** muestra cuántas notas saldrían por cada motivo, sin escribir ni borrar nada.
- **Guarda con zstd nivel 19:** tarda unos minutos, pero deja cada archivo debajo de los 100 MB que acepta GitHub.
- **Frena si faltan Parquet por fuente:** así una segunda corrida no pisa los archivos consolidados.
- **Antes de retomar una descarga:** las carpetas por fuente ya no tienen los Parquet anteriores. Hay que recuperarlos de Git (commit `afe111c`), descargar y volver a correr `limpiar.py`. En soluciones, después de `separar_por_track.py`.

## Muestra para etiquetado manual

[`etiquetado/muestrear.py`](../etiquetado/muestrear.py) toma 25 notas por track de `data/movilidad.parquet` y `data/residuos.parquet` y las escribe en `etiquetado/muestra.js`, que carga [`etiquetado/index.html`](../etiquetado/index.html).

```bash
python etiquetado/muestrear.py
```

- **Descarta los cuerpos de menos de 300 caracteres** y recorta el cuerpo a 15.000.
- **Reparte entre fuentes:** mezcla con semilla 42 y toma de a una nota por fuente, por turnos, hasta llegar a 25.
- **Es determinística:** con los mismos Parquet sale la misma muestra. Si los Parquet cambian, cambia la muestra; por eso se commitea `muestra.js` antes de etiquetar.

## Reconciliación del etiquetado

[`etiquetado/reconciliar.py`](../etiquetado/reconciliar.py) lee los dos `etiquetado/etiquetas/*-<track>.json` y escribe en `etiquetado/reconciliacion/`:

- **`<track>-informe.md`:** acuerdo en todos los campos; acuerdo y kappa en relevancia y tipo; acuerdo en alcance; superposición de categorías (Jaccard); uso de cada categoría por persona; textos libres de las categorías "otro", y la lista de desacuerdos.
- **`<track>-gold.json`:** la etiqueta final de cada nota, con `origen` (`acuerdo`, la persona elegida o `nueva`), `nota_reconciliacion` (el porqué, que alimenta la guía) y los comentarios de los dos.

```bash
python etiquetado/reconciliar.py --selfcheck
python etiquetado/reconciliar.py movilidad --informe
python etiquetado/reconciliar.py movilidad
```

- **Desacuerdo es cualquier diferencia:** relevancia, tipo, categorías o texto libre (sin distinguir mayúsculas). El comentario no cuenta, y el alcance tampoco, porque desde el 25/11 sale de la fuente.
- **Orden de la sesión:** primero las notas que difieren en relevancia, después en tipo y al final el resto. Las notas en las que coinciden pasan directo al gold.
- **Se puede cortar y retomar:** guarda después de cada decisión, y al volver a correr salta las ya decididas.
- **Frena si los JSON son de otra muestra** que la de `muestra.js`.
- **Lee las categorías renombradas con el nombre nuevo:** `RENOMBRADAS` traduce `GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE` a `GESTION_DEFICIENTE_RESIDUOS` al cargar los JSON. Los JSON originales no se modifican.

## Alcance por fuente

[`scripts/diccionarios/alcance_fuentes.py`](../scripts/diccionarios/alcance_fuentes.py) asigna el alcance geográfico según el origen del medio: Córdoba, resto de Argentina, resto de América Latina o resto del mundo. Cubre todas las fuentes de movilidad y residuos. Si aparece una fuente nueva, hay que sumarla, y el chequeo falla hasta que eso pase.

```bash
python scripts/diccionarios/alcance_fuentes.py
```

## Filtro de ruido de movilidad

[`scripts/clasificacion/filtrar_movilidad.py`](../scripts/clasificacion/filtrar_movilidad.py) saca de `data/movilidad.parquet` el ruido que la [guía de movilidad](../etiquetado/guia-movilidad.md) ya deja afuera, sin usar un LLM. Escribe solo las notas que pasan en `data/v1-samo-movilidad/movilidad_filtrado.parquet`, con las mismas columnas. Los descartes no se guardan. Los criterios y las cifras están en [`contexto-pipeline.md`](analisis-datasets/contexto-pipeline.md#filtro-determinístico-de-ruido-en-movilidad-25112026).

```bash
python scripts/clasificacion/filtrar_movilidad.py --selfcheck
python scripts/clasificacion/filtrar_movilidad.py --muestra 20
python scripts/clasificacion/filtrar_movilidad.py
python scripts/clasificacion/filtrar_movilidad.py --soluciones
```

- **Solo filtra diarios:** TN, El Doce, Clarín, La Nación y CBA24N. Los medios especializados pasan enteros.
- **Tres reglas, en orden:** sección fuera del track (deportes, espectáculos, policiales y similares), vocabulario de choque o accidente en título o bajada, y ninguna raíz de `RAICES_MOVILIDAD` en título, bajada ni tags. La primera que coincide es el motivo.
- **No corta por largo del cuerpo:** puede haber notas útiles cortas.
- **`--muestra N`:** imprime N títulos al azar por motivo (semilla 42) para auditar a mano. No escribe nada.
- **`--selfcheck`:** casos de prueba y verifica que las 4 notas relevantes del gold pasan.
- **Log:** las líneas llevan la hora, como en el scraping, y se agregan a `data/logs/filtrar_movilidad.log`, que queda fuera de Git.
- **Alcance:** agrega la columna `alcance` con [`alcance_fuentes.py`](../scripts/diccionarios/alcance_fuentes.py). Falla si aparece una fuente sin alcance.
- **`--soluciones`:** toma las notas de movilidad de `data/soluciones.parquet` y escribe `data/v1-samo-movilidad/movilidad_soluciones_filtrado.parquet`. Infobae cuenta como diario.

## Referencia para evaluar la clasificación de movilidad

[`etiquetado/muestrear_referencia.py`](../etiquetado/muestrear_referencia.py) arma 300 notas al azar de los dos Parquet filtrados (240 de problemáticas y 60 de soluciones, semilla 42, sin las del gold) en `etiquetado/referencia/movilidad-parte{1,2,3}.json`. Cada parte suma las 25 del gold, mezcladas, para medir al etiquetador. También escribe `movilidad-calibracion.json`, solo con las 25 del gold. El cuerpo se corta a 6.000 caracteres.

Un LLM grande etiqueta esos archivos con [`etiquetado/referencia/prompt-etiquetador.md`](../etiquetado/referencia/prompt-etiquetador.md), en Claude Code o en OpenCode. Después, [`etiquetado/calibrar.py`](../etiquetado/calibrar.py) compara con el gold (reusa kappa y Jaccard de `reconciliar.py`):

```bash
python etiquetado/muestrear_referencia.py
python etiquetado/calibrar.py --selfcheck
python etiquetado/calibrar.py
python etiquetado/calibrar.py --unir
```

- **Sin flags:** lee `movilidad-calibracion-<modelo>.json` y escribe `calibracion-informe.md`, con el acuerdo de cada modelo con el equipo.
- **`--unir`:** lee `movilidad-referencia-parte{1,2,3}.json`, valida el formato y escribe `movilidad-referencia.json` (las 300) y `movilidad-referencia-informe.md`, con las categorías sugeridas agrupadas.

## Clasificación v2 de movilidad (vLLM en Kaggle)

[`scripts/clasificacion/clasificar_vllm.py`](../scripts/clasificacion/clasificar_vllm.py) corre la cascada: etapa 1 (motivo y relevancia) en todas las notas y etapa 2 (problema, solución, tipo, categorías y ubicación) en las relevantes. Lanza un proceso por GPU, con Qwen2.5-7B-Instruct AWQ y salida JSON guiada. Guarda un checkpoint en Parquet por tanda de 500 notas y, al relanzar, saltea lo hecho. Se usa desde [`notebooks/kaggle_movilidad_v2.ipynb`](../notebooks/kaggle_movilidad_v2.ipynb). **Todavía no se corrió.**

```bash
python scripts/clasificacion/clasificar_vllm.py --selfcheck
python scripts/clasificacion/clasificar_vllm.py --armar-ejemplos
```

- **`--selfcheck`:** sin GPU. Verifica que las categorías coincidan con `etiquetado/config.js` y los motivos con `calibrar.py`, la partición por GPU y que el prefijo del prompt sea igual para todas las notas.
- **`--armar-ejemplos`:** escribe `ejemplos_movilidad.json` con 12 ejemplos few-shot (9 del gold y 3 del filtrado, ninguno de la referencia).
- **Etapa 1:** devuelve `planteo` (el problema o la solución concreta, o null) y `motivo`, con el cuerpo cortado a 1.000 caracteres. **Etapa 2:** 2.000 caracteres, y una limpieza fija deja las categorías coherentes con el tipo.
- **Checkpoints:** el script saltea los id que ya tienen checkpoint en la carpeta de salida. Para repetir una corrida con otro prompt, hay que usar otra carpeta.
- **En Kaggle:** `--entradas`, `--salida`, `--ids` (solo las notas de un JSON, como la referencia), `--limite`, `--gpus` y `--etapa`. Sale `movilidad_clasificado.parquet`.

### Cómo correrlo en Kaggle (a mano, en la web)

1. Armar el paquete en `kaggle/movilidad-v2/`, que queda fuera de Git: los dos Parquet de `data/v1-samo-movilidad/`, `clasificar_vllm.py`, `ejemplos_movilidad.json` y `etiquetado/referencia/movilidad-referencia.json`.
2. Crear un Kaggle Dataset **privado** con esos 5 archivos.
3. Importar `notebooks/kaggle_movilidad_v2.ipynb`. En las opciones: GPU T4 x2, Internet On y el dataset como input.
4. **Prueba de humo** (celda 0, 50 notas): verifica que vLLM corra el modelo en T4 y da una primera medida de notas/min. Si falla, se fija otra versión de vLLM en la celda de instalación.
5. **Gate** (celda 1, solo las 300 de la referencia). Bajar `gate/movilidad_clasificado.parquet` de la pestaña Output a `data/resultados/v2-movilidad/gate/`.
6. Evaluar localmente:

```bash
python scripts/clasificacion/evaluar_movilidad.py --selfcheck
python scripts/clasificacion/evaluar_movilidad.py
```

[`evaluar_movilidad.py`](../scripts/clasificacion/evaluar_movilidad.py) compara con la referencia y escribe `gate-informe.md`: relevancia (recall, precisión y kappa, en total y por dataset), tipo, Jaccard de categorías, notas sin respuesta, JSON inválidos, motivos cruzados y desacuerdos con el comentario de Haiku. Umbrales propuestos: recall ≥ 0,85, precisión ≥ 0,70 y 0 JSON inválidos.

7. Solo si el gate pasa: corrida completa (celda 2). Correrla con **Save Version → Save & Run All (Commit)**: corre en la nube sin el navegador, hasta 12 h. Una sesión interactiva se corta si la compu se bloquea.
8. **Reanudar después de un fallo:** cada commit arranca con `/kaggle/working` vacío. Con **Add Input → Your Work → Notebooks**, sumar como input este mismo notebook (su salida, incluso la de una versión fallida) y volver a hacer commit. La celda de configuración copia `resultados/v2-movilidad/` de ese input y cada celda saltea las notas que ya tienen checkpoint.

## Pendiente de revisar

- Los términos de uso de Visión Sustentable, Ecomundo, Futuro Sustentable, ECOBIZ, TN, Mongabay, CBA24N, Cadena 3, Resource Recycling, Circular Online, Mongabay en inglés y Grist.
- Si los términos de Clarín y La Nación tienen otras condiciones fuera de lo buscado.
