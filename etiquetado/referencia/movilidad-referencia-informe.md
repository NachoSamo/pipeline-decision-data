# Referencia de movilidad · 300 notas

Generado el 26/11/2026 22:44 con `etiquetado/calibrar.py --unir`. Etiquetas de un LLM con la guía de movilidad, sobre una muestra al azar de los Parquet filtrados. No reemplaza al gold del equipo.

## Acuerdo de cada parte con el gold (25 notas)

| Etiquetador | Relevancia: acuerdo | Relevancia: kappa | Marcó relevantes | Tipo, en relevantes para los dos | Categorías (Jaccard) |
|---|---|---|---|---|---|
| parte 1 (haiku) | 23 de 25 (92 %) | 0,63 | 2 de 25 | 2 de 2 (100 %) | 1,00 |
| parte 2 (haiku) | 24 de 25 (96 %) | 0,83 | 3 de 25 | 3 de 3 (100 %) | 1,00 |
| parte 3 (haiku) | 24 de 25 (96 %) | 0,83 | 3 de 25 | 3 de 3 (100 %) | 1,00 |

## Relevantes

- **Total:** 63 de 300 (21 %).
- **problematicas:** 33 de 240 (14 %).
- **soluciones:** 30 de 60 (50 %).

| Fuente | Relevantes |
|---|---:|
| TN | 4 de 60 (7 %) |
| Clarín | 16 de 57 (28 %) |
| El Doce | 4 de 48 (8 %) |
| Grist | 1 de 28 (4 %) |
| La Nación | 6 de 21 (29 %) |
| Mobilidade Sampa | 11 de 20 (55 %) |
| CicloVivo | 1 de 15 (7 %) |
| Movilidad Eléctrica | 6 de 7 (86 %) |
| Ecoportal | 2 de 7 (29 %) |
| HDmotori | 1 de 6 (17 %) |
| Visión Sustentable | 0 de 5 (0 %) |
| CBA24N | 2 de 5 (40 %) |
| Ambientum | 1 de 3 (33 %) |
| Eco dalle Città | 3 de 3 (100 %) |
| Infobae | 0 de 2 (0 %) |
| Ecoticias | 1 de 2 (50 %) |
| EconomyUp | 0 de 2 (0 %) |
| Recover Web | 0 de 2 (0 %) |
| The Driven | 1 de 1 (100 %) |
| Bioplastics News | 0 de 1 (0 %) |
| Recycling Portal | 1 de 1 (100 %) |
| MamStartup | 0 de 1 (0 %) |
| Dialogue Earth | 1 de 1 (100 %) |
| Ecomundo | 0 de 1 (0 %) |
| Africa Sustainability Matters | 1 de 1 (100 %) |

## Motivos

| Valor | Notas |
|---|---:|
| `otro_tema` | 67 de 300 (22 %) |
| `problema_o_solucion_concreta` | 63 de 300 (21 %) |
| `gestion_sin_problema_ni_solucion` | 53 de 300 (18 %) |
| `politica_o_economia_sin_medida` | 42 de 300 (14 %) |
| `seguridad_vial` | 28 de 300 (9 %) |
| `otro_track_ambiental` | 27 de 300 (9 %) |
| `nota_de_color` | 13 de 300 (4 %) |
| `movilidad_de_pasada` | 7 de 300 (2 %) |

## Tipos (relevantes)

| Valor | Notas |
|---|---:|
| `solucion` | 39 de 63 (62 %) |
| `ambas` | 13 de 63 (21 %) |
| `problema` | 11 de 63 (17 %) |

## Categorías de problema

| Valor | Notas |
|---|---:|
| `DEFICIT_TRANSPORTE_PUBLICO` | 11 de 63 (17 %) |
| `OTRO_PROBLEMA_MOVILIDAD` | 9 de 63 (14 %) |
| `CONGESTION_Y_DEMORAS` | 4 de 63 (6 %) |
| `EMISIONES_Y_FLOTA_OBSOLETA` | 3 de 63 (5 %) |

## Categorías de solución

| Valor | Notas |
|---|---:|
| `ELECTROMOVILIDAD_Y_BUSES_ELECTRICOS` | 22 de 63 (35 %) |
| `OTRA_SOLUCION_MOVILIDAD` | 13 de 63 (21 %) |
| `REDES_FERROVIARIAS_Y_SUBTE` | 10 de 63 (16 %) |
| `SISTEMAS_INTELIGENTES_TRANSITO_ITS` | 6 de 63 (10 %) |
| `INFRAESTRUCTURA_BICICLETAS_Y_PEATONAL` | 2 de 63 (3 %) |

## Categorías sugeridas

Para que el equipo decida si alguna entra a la taxonomía antes de clasificar en Kaggle.

| Sugerencia | Notas | Ejemplos |
|---|---:|---|
| `TRANSPORTE_A_DEMANDA_TAXIS_Y_REMISES` | 1 | La Municipalidad ofrece taxis y remises a bajo costo |
| `ESTACIONAMIENTO_Y_ACARREO_DE_MOTOS` | 1 | Microcentro: entran 61% menos de autos y desde hoy suman grúas para llevarse mot |
| `GRATUIDAD_TRANSPORTE_ELECCIONES` | 1 | Prefeitura oferece transporte público gratuito para as eleições |
| `RENOVACION_DE_FLOTA_DE_BUSES` | 1 | Viação Miracatiba investe em 30 novos ônibus Apache Vip de quinta geração para I |
| `NORMATIVA_VEHICULOS_ELECTRICOS_LIVIANOS` | 1 | Mobilidade elétrica faz parte da solução |
| `MEJORAS_TRANSPORTE_MUNICIPAL` | 1 | Melhorias no transporte público de Taubaté |
| `TARIFA_SUBSIDIADA_ESTUDIANTIL` | 1 | Ciudad: hasta cuándo funciona el boleto educativo |
| `INFRAESTRUCTURA_VIAL_AUTOPISTAS` | 1 | Cierran la avenida Lugones este miércoles: dónde serán los cortes y cuándo volve |
| `INTEGRACION_TARIFARIA_TRANSPORTE` | 1 | Autolotações dos morros de Santos iniciam integração com VLT em 1º de maio |
| `INFRAESTRUCTURA_DE_RECARGA` | 1 | La red de recarga para coches eléctricos alcanza los 50.000 puntos operativos en |
