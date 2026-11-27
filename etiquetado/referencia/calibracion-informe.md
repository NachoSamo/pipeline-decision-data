# Calibración de etiquetadores · movilidad

Generado el 26/11/2026 22:29 con `etiquetado/calibrar.py`. Cada modelo etiquetó las 25 notas del gold del equipo (`reconciliacion/movilidad-gold.json`) con la guía, sin ver las etiquetas.

**Medición débil:** 25 notas con 4 relevantes. Un solo acierto o error mueve mucho las cifras. Sirve para descartar modelos que se apartan claramente del criterio del equipo, no para afinar.

Kappa mide el acuerdo descontando el azar: menos de 0,4 es bajo, de 0,4 a 0,6 moderado y más de 0,6 bueno.

## Acuerdo con el gold

| Etiquetador | Relevancia: acuerdo | Relevancia: kappa | Marcó relevantes | Tipo, en relevantes para los dos | Categorías (Jaccard) |
|---|---|---|---|---|---|
| haiku | 24 de 25 (96 %) | 0,83 | 3 de 25 | 3 de 3 (100 %) | 1,00 |

## Detalle por etiquetador

### haiku

- **Formato:** válido.
- Difiere en relevancia: _Conheça startups do Hub Green Sampa e suas tecnologias_. Gold: True; modelo: False (movilidad_de_pasada). Roundup de startups sustentables; movilidad es uno de nueve ejes y no el tema central (criterio estricto).
