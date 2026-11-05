# Scraping de webs

Última actualización: 4/11/2026.

Cada fuente tiene su forma de listar y leer notas, porque cada sitio permite y expone cosas distintas. Todos los scripts corren desde la raíz del repo, guardan en `data/` y se pueden cortar y retomar volviendo a ejecutar el mismo comando. Cuántas notas trajo cada fuente está en la [evaluación de volumen](contexto-pipeline.md#evaluación-de-volumen-4112026-2334-descargas-en-curso).

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

Las palabras están en [`scripts/keywords.py`](../scripts/keywords.py):

- **`BUSQUEDAS_RESIDUOS`:** términos para buscadores.
- **`CORE_KEYWORDS_RESIDUOS`:** expresiones regulares que marcan temas específicos.
- **`BUSQUEDAS_PRECISAS_RESIDUOS`:** términos con menos ruido, sin los que en El Doce trajeron más resultados irrelevantes. Los usan TN y Mongabay.
- **`BUSQUEDAS_INGLES_RESIDUOS` y `RAICES_INGLES_RESIDUOS`:** términos y raíces para fuentes en inglés.
- **`TAGS_INFOBAE_*` y `TAGS_CLARIN_*`:** tags de cada medio, separados en residuos y amplios.
- **`RAICES_RESIDUOS`:** raíces sin tildes para filtrar URLs de sitemaps y priorizar notas.

## Qué guarda

Cada script deja estos archivos en `data/`:

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

### Bloomberg (sin script)

No se scrapea. Sus términos prohíben scrapers, bots, minería de datos y crear bases de datos sin consentimiento escrito, y su `robots.txt` excluye `/search`.

## Pendiente de revisar

- Los términos de uso de Visión Sustentable, Ecomundo, Futuro Sustentable, ECOBIZ, TN, Mongabay, CBA24N, Cadena 3, Resource Recycling, Circular Online, Mongabay en inglés y Grist.
- Si los términos de Clarín y La Nación tienen otras condiciones fuera de lo buscado.
