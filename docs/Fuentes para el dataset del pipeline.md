# Fuentes para el dataset del pipeline

Nov 4, 2026 · @Ignacio Samocachan

## Resumen

Hay 43 fuentes posibles de noticias y redes. La primera tanda sugerida tiene 10: La Nación, Clarín, Infobae, Página/12, El Doce, Cadena 3, Mongabay, Climate Tracker, Futuro Sustentable y Visión Sustentable. Tienen sitemaps y no excluyen bots de IA por nombre. La Voz también importa por ser de Córdoba, pero primero hay que resolver su acceso.

**Las 10.000 notas útiles por track todavía no están comprobadas.** En residuos, 13.633 notas con cuerpo mencionan el tema, pero falta medir cuántas son útiles; los otros tres tracks no se midieron. El detalle por fuente está en la [evaluación de volumen](contexto-pipeline.md#evaluación-de-volumen-4112026-2334-descargas-en-curso). Mirar solo la URL encuentra mucho menos: unas 60 notas por año en La Nación y 56 de 8.000 en Mongabay.

El 4/11/2026 revisé `robots.txt` y sitemaps, no los términos de uso. Que un `robots.txt` no excluya a un bot no implica permiso para reutilizar el contenido. Los focos de cada medio salen de la investigación de Ignacio y no los verifiqué.

## Primera tanda

Varias fuentes comparten el mismo patrón de sitemap, así que quizá no haga falta una guía distinta para cada una. Falta catalogar las secciones de cada medio y probar la extracción de texto.

| Patrón de sitemap | Fuentes de la primera tanda | Otras fuentes con el mismo patrón |
| --- | --- | --- |
| `/arc/outboundfeeds/` | El Doce, Infobae, Página/12 | La Voz, TN, El Cronista |
| `sitemap_index.xml` | Mongabay, Climate Tracker, Futuro Sustentable, Visión Sustentable | Ecomundo |
| Propio | La Nación, Clarín, Cadena 3 | Sin revisar |

## Córdoba y Argentina

Los seis medios argentinos declaran sitemaps, así que se pueden listar sus notas sin navegar el sitio. La Voz es el único de los seis que excluye a bots de IA por nombre.

| Fuente | Alcance | Sitemaps en `robots.txt` | Restricción observada |
| --- | --- | --- | --- |
| [La Voz](https://www.lavoz.com.ar/robots.txt) | Córdoba | Declara 3; los 2 probados dieron error 1016 | Excluye a `ChatGPT-User`, `OpenAI`, `ChatGPT`, `FacebookBot` y `Meta AI` |
| [El Doce](https://eldoce.tv/robots.txt) | Córdoba | Declara 7 | Ninguna por bot de IA |
| [La Nación](https://www.lanacion.com.ar/robots.txt) | Nacional | Declara 6; índice histórico de 730 días | Excluye `/buscador` |
| [Clarín](https://www.clarin.com/robots.txt) | Nacional | Declara 3 | Ninguna por bot de IA |
| [Infobae](https://www.infobae.com/robots.txt) | Nacional | Declara 17 | Ninguna por bot de IA |
| [Página/12](https://www.pagina12.com.ar/robots.txt) | Nacional | Declara 2 | Ninguna por bot de IA |

El Doce sale del boceto del pipeline. Falta probar el texto completo y los muros de pago en todos.

## Más medios nacionales y federales

De estos doce medios, once declaran sitemaps y solo CBA24N excluye bots de IA por nombre. Para Córdoba, Cadena 3 no presenta esa restricción. No abrí ninguno de estos sitemaps.

| Fuente | Alcance | Sitemaps en `robots.txt` | Bots de IA excluidos por nombre |
| --- | --- | --- | --- |
| [Cadena 3](https://www.cadena3.com/robots.txt) | Córdoba y federal | Declara 6 | Ninguno |
| [CBA24N](https://www.cba24n.com.ar/robots.txt) | Córdoba | Declara 2 | `GPTBot`, `ClaudeBot`, `CCBot` y `meta-externalagent` |
| [TN](https://tn.com.ar/robots.txt) | Nacional | Declara 4 | Ninguno |
| [Perfil](https://www.perfil.com/robots.txt) | Nacional | Declara 4 | Ninguno |
| [El Cronista](https://www.cronista.com/robots.txt) | Nacional | Declara 8 | Ninguno |
| [Diario Popular](https://www.diariopopular.com.ar/robots.txt) | Nacional | Declara 4 | Ninguno |
| [Crónica](https://www.cronica.com.ar/robots.txt) | Nacional | No declara | Ninguno |
| [La Capital](https://www.lacapital.com.ar/robots.txt) | Rosario | Declara 5 | Ninguno |
| [La Gaceta](https://www.lagaceta.com.ar/robots.txt) | Tucumán | Declara 8, uno de ellos histórico | Ninguno |
| [Los Andes](https://www.losandes.com.ar/robots.txt) | Mendoza | Declara 4 | Ninguno |
| [Río Negro](https://www.rionegro.com.ar/robots.txt) | Patagonia norte | Declara 3 | Ninguno |
| [El Tribuno](https://www.eltribuno.com/robots.txt) | Salta y Jujuy | Declara 5 | Ninguno |

## Portales especializados de Argentina

Estos portales concentran más notas sobre residuos, entre 5 % y 8 % de sus URLs, pero entre los tres medidos suman solo 395. Sirven por su foco, no por su volumen.

| Fuente | Foco según la investigación | URLs revisadas | Con palabras de residuos en la URL | Estado |
| --- | --- | --- | --- | --- |
| [Futuro Sustentable](https://futurosustentable.com.ar/) | Normativa ambiental y gestión industrial | 2.172 | 174 | Tiene sitemap, aunque `robots.txt` no lo declara; ese archivo excluye `/?s=` y pide 60 segundos entre pedidos |
| [Visión Sustentable](https://www.visionsustentable.com/) | Sustentabilidad empresarial y economía circular | 2.929 | 150 | Declara sitemap |
| [Ecomundo](https://www.ecomundo.com.ar/) | Noticias ambientales, incluida gestión de residuos | 1.122 | 71 | Declara sitemap; el último revisado tiene fechas de 2016, y falta ver si sigue activo |
| [ECOBIZ](https://ecobiz.com.ar/) | Economía circular y reciclaje | Sin medir | Su buscador da 170 para "residuos" | Se lista con el buscador, permitido en `robots.txt`; no encontré sitemap en la ruta probada |
| Red Argentina de Periodismo Ambiental | Investigaciones ambientales de campo | Sin medir | Sin medir | No encontré su sitio en los dominios probados |

Esta búsqueda incluyó "envases" y "microplástico", así que no es exactamente comparable con las muestras anteriores. Ninguno de los tres portales medidos excluye bots de IA en `robots.txt`.

## América Latina

Mongabay es la fuente regional con más volumen, aunque solo 0,7 % de sus URLs revisadas menciona residuos. Ninguna de las tres excluye a bots de IA por nombre.

| Fuente | Foco según la investigación | URLs revisadas | Con palabras de residuos en la URL |
| --- | --- | --- | --- |
| [Mongabay Latam](https://es.mongabay.com/) | Conservación, bosques y biodiversidad | 8.000, en 8 de sus 10 sitemaps | 56 |
| [Climate Tracker América Latina](https://climatetrackerlatam.org/) | Clima y transición energética | 722 | 9 |
| [Periodistas Ambientales](https://periodistasambientales.org/) ([resumen](publicaciones-periodistas-ambientales.md)) | Red y recursos sobre crisis climática | 16 | 1 |

La búsqueda miró solo la URL, así que puede omitir notas relevantes e incluir falsos positivos.

## España y medios internacionales

Estas fuentes tienen menos prioridad para una primera versión, porque varias excluyen bots de IA y no hablan de la realidad local. Sirven sobre todo para ver si un problema aparece en otros países.

| Fuente | Idioma | Sitemaps en `robots.txt` | Bots de IA excluidos por nombre |
| --- | --- | --- | --- |
| [Planeta Futuro, de El País](https://elpais.com/robots.txt) | Español | No declara | `ClaudeBot`, `Claude-User`, `Claude-SearchBot`, `Claude-Extension` y `CCBot` |
| [EFEverde](https://efeverde.com/robots.txt) | Español | Declara 1, en el dominio efesalud.com | Ninguno |
| [Ballena Blanca](https://ballenablanca.es/) | Español | No se encontró | Sin dato |
| [Climática](https://climatica.coop/robots.txt) | Español | No declara | `GPTBot` y `CCBot` |
| [The Guardian](https://www.theguardian.com/robots.txt) | Inglés | Declara 2 | `ClaudeBot`, `Claude-User`, `Claude-SearchBot`, `anthropic-ai`, `CCBot` y `meta-externalagent` |
| [BBC](https://www.bbc.com/robots.txt) | Varios | Declara 39 | `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `Claude-Web`, `Claude-SearchBot`, `anthropic-ai`, `CCBot` y `meta-externalagent` |
| [National Geographic](https://www.nationalgeographic.com/robots.txt) | Inglés | Declara 5 | Ninguno |

## Internacionales con acceso permitido

Estas cuatro fuentes tienen API de WordPress abierta y no excluyen bots de IA por nombre en `robots.txt`. Se descargan con `scrape_internacional.py`, desde 2024. Falta revisar sus términos de uso.

| Fuente | Foco | Resultados para "waste" desde 2024 | Pausa pedida |
| --- | --- | --- | --- |
| [Resource Recycling](https://resource-recycling.com/) | Industria del reciclaje | 1.424 | No indica |
| [Circular Online](https://www.circularonline.co.uk/) | Economía circular y residuos | 1.027 | No indica |
| [Mongabay en inglés](https://news.mongabay.com/) | Ambiente global | 754 | 10 s |
| [Grist](https://grist.org/) | Clima y ambiente | 391 | No indica |

Los resultados son los que devuelve la búsqueda, así que pueden incluir ruido. [Waste Dive](https://www.wastedive.com/) y [Eco-Business](https://www.eco-business.com/) no tienen esa API; quedan para revisar. La API oficial de The Guardian pide una clave propia, y no pude leer sus condiciones.

## Negocios y ciencia

Las tres fuentes excluyen bots de IA por nombre, así que conviene revisar sus términos antes de incluirlas. **Bloomberg queda descartada para scraping:** sus términos prohíben scrapers, bots, minería de datos y crear bases de datos sin consentimiento escrito, y su `robots.txt` excluye `/search`.

| Fuente | Foco según la investigación | Sitemaps en `robots.txt` | Bots de IA excluidos por nombre |
| --- | --- | --- | --- |
| [Bloomberg Green](https://www.bloomberg.com/robots.txt) | Finanzas sostenibles y transición energética | Declara 10 | `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `anthropic-ai`, `CCBot` y otros |
| [Financial Times, Climate Capital](https://www.ft.com/robots.txt) | Negocios y regulación climática | Declara 1 | `ClaudeBot`, `Claude-Web`, `anthropic-ai`, `CCBot` y otros |
| [The Conversation](https://theconversation.com/robots.txt) | Artículos de investigadores para público general | Declara 15 | `GPTBot`, `ChatGPT`, `OpenAI`, `ClaudeBot`, `CCBot` y otros |

## Redes sociales y foros

Reddit, X e Instagram excluyen a los bots genéricos en su `robots.txt`, así que no sirven para un scraping simple. Habría que evaluar sus API oficiales, cuyas condiciones y costos no revisé.

| Fuente | Estado en el boceto | Qué podría aportar | Falta revisar |
| --- | --- | --- | --- |
| [Reddit](https://www.reddit.com/robots.txt) | En duda | Relatos en primera persona | API, comunidades y volumen en español |
| [X](https://x.com/robots.txt) | En duda | Reclamos y reacciones públicas | API y costos |
| [Instagram](https://www.instagram.com/robots.txt) | En duda: comentarios, sin definir de qué cuentas | Reacciones a notas y campañas | Si los comentarios se pueden obtener y cuáles |

Los foros de sustentabilidad y ecologismo siguen sin relevar: ninguna de las investigaciones nombra uno.

## Datos abiertos y APIs

Estas fuentes no suman notas a las 10.000: sirven para contrastar lo que dicen los medios y para ubicar los hechos. Hay datos sobre residuos, pero son pocos: 9 resultados en datos.gob.ar y 2 en el portal provincial de Córdoba.

### Para residuos

| Fuente | Qué podría aportar | Resultado de la prueba |
| --- | --- | --- |
| [datos.gob.ar](https://datos.gob.ar/) | Datasets nacionales | 9 resultados para "residuos", no todos relevantes; incluye Residuos Sólidos Urbanos (13 CSV) y Residuos peligrosos (14 CSV) |
| [API de Series de Tiempo](https://apis.datos.gob.ar/series/api/search?q=residuos) | Series históricas | 156 resultados para "residuos"; falta ver cuántos sirven |
| [GEOREF](https://apis.datos.gob.ar/georef/api/municipios?nombre=cordoba&max=2) | Normalizar los lugares que nombran las notas | Responde y devuelve municipios con coordenadas |
| [Datos Gestión Abierta](https://datosgestionabierta.cba.gov.ar/) | Datos de la provincia de Córdoba | 2 resultados para "residuos" |
| [Gobierno Abierto Córdoba](https://gobiernoabierto.cordoba.gob.ar/api/) | Datos de la ciudad de Córdoba | Responde, pero la raíz no lista Puntos Verdes ni transporte; falta revisar `datos-abiertos` |
| [IDERA](https://www.idera.gob.ar/) | Capas geográficas | El sitio responde; no verifiqué la capa de basurales |
| [IDECOR](https://idecor.cba.gov.ar/) | Capas de Córdoba | Devolvió error 403 |
| [OpenStreetMap, vía Overpass](https://overpass-api.de/) | Centros de reciclaje mapeados | Devolvió error 406; sin comprobar |
| [FARN](https://farn.org.ar/) y [Greenpeace Argentina](https://www.greenpeace.org/argentina/) | Informes y seguimiento de leyes | Los sitios responden; no son API |
| FACyR | Toneladas recuperadas por cooperativas | facyr.org.ar no respondió; falta encontrar su sitio y sus datos |
| [Banco Mundial](https://api.worldbank.org/v2/country/ARG/indicator/EG.FEC.RNEW.ZS?format=json) | Indicadores por país | La API responde; no verifiqué el indicador de residuos por habitante |

### Para los otros tracks

| Fuente | Track | Resultado de la prueba |
| --- | --- | --- |
| [GBIF](https://api.gbif.org/v1/occurrence/search?country=AR&limit=0) | Biodiversidad | Responde: 16,4 millones de registros de Argentina |
| [Portal de Biodiversidad](https://biodiversidad.ar/) | Biodiversidad | El sitio responde |
| [Global Forest Watch](https://www.globalforestwatch.org/) | Biodiversidad y agro | Redirige a globalnaturewatch.org; falta revisar la API |
| [Copernicus Data Space](https://dataspace.copernicus.eu/) | Biodiversidad y agro | El sitio responde; el antiguo scihub.copernicus.eu no respondió |
| [Open-Meteo Air Quality](https://air-quality-api.open-meteo.com/v1/air-quality?latitude=-31.42&longitude=-64.18&hourly=pm10&past_days=1&forecast_days=0) | Movilidad y agro | Responde con datos de Córdoba |
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/) | Biodiversidad y agro | La página de la API responde; no hice consultas |
| [Google Earth Engine](https://earthengine.google.com/) | Biodiversidad y agro | El sitio responde; no probé su API |
| [BA Data](https://data.buenosaires.gob.ar/) | Movilidad | El sitio responde; no probé sus API |
| SUBE y GTFS | Movilidad | Sin probar |

### Repositorios y otras fuentes

- [CONICET Digital](https://ri.conicet.gov.ar/) y [SEDICI](https://sedici.unlp.edu.ar/) responden. SEDICI aparece como repositorio del CONICET en la investigación, pero su dominio es de la UNLP.
- [ArgentinaDatos](https://api.argentinadatos.com/v1/) devolvió 404 en la raíz. No probé sus rutas.
- Las fechas de modificación de datos.gob.ar corresponden a los metadatos, así que no indican cuán actuales son los datos.

## Ponderación geográfica

El equipo quiere dar más peso a los problemas que aparecen en varios países y a los locales. Los valores de esos pesos todavía no están definidos.

| Señal | Qué habría que medir | Cuidado |
| --- | --- | --- |
| Varios países | En cuántos países ocurre el problema | Debe contar el país del hecho, no el del medio; además, depende de cuántos medios se incluyan por país |
| Local | Si el hecho ocurre en Córdoba o en Argentina | Falta decidir si cuenta el lugar del hecho, el origen del medio o ambos |

## Falta aclarar

Lo más urgente es medir cuántas notas hay buscando en el texto completo, porque de eso depende la lista final.

- [ ] Medir el volumen real con texto completo en la primera tanda.
- [ ] Catalogar las secciones de cada fuente de la primera tanda.
- [ ] Definir el diccionario de palabras clave de residuos.
- [ ] Definir qué hacer si un track no llega a 10.000 notas.
- [x] Confirmar que la fuente del boceto es El Doce.
- [ ] Comprobar cómo acceder a La Voz.
- [ ] Revisar los términos de uso de cada medio elegido.
- [ ] Comprobar cómo afectan los muros de pago.
- [ ] Relevar foros de sustentabilidad y ecologismo.
- [ ] Elegir fuentes para relevar soluciones existentes.
- [ ] Revisar si estas fuentes cubren los otros tres tracks.
- [ ] Definir los pesos para varios países y para lo local.
