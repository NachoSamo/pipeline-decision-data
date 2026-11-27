# Gate de la clasificación v2 de movilidad

Generado el 27/11/2026 16:37 con `scripts/clasificacion/evaluar_movilidad.py`. Compara la salida de Qwen2.5-7B (vLLM, Kaggle) con la referencia de Haiku (300 notas). La referencia tiene criterios dispares en tarifas, paros, anuncios, aviación y proyectos sin aprobar: parte de los desacuerdos viene de ahí.

## Resumen

| Medida | Valor | Umbral |
|---|---|---|
| Relevancia: recall | 0,89 (56 de 63) | ≥ 0,85 |
| Relevancia: precisión | 0,45 (56 de 125) | ≥ 0,70 |
| Relevancia: kappa | 0,44 | |
| Tipo, en relevantes para los dos | 41 de 56 (73 %) | |
| Categorías (Jaccard) | 0,39 | |
| Notas sin respuesta | 0 de 300 | 0 |
| JSON inválidos | 1 de 300 | 0 |

## Por dataset

| Dataset | Recall | Precisión | Kappa | Relevantes en la referencia | Relevantes para Qwen |
|---|---|---|---|---|---|
| problematicas | 0,85 | 0,36 | 0,39 | 33 | 77 |
| soluciones | 0,93 | 0,58 | 0,27 | 30 | 48 |

## Motivos: referencia contra Qwen

| Referencia | Qwen | Notas |
|---|---|---:|
| `gestion_sin_problema_ni_solucion` | `problema_o_solucion_concreta` | 27 |
| `otro_tema` | `seguridad_vial` | 13 |
| `politica_o_economia_sin_medida` | `problema_o_solucion_concreta` | 13 |
| `otro_tema` | `politica_o_economia_sin_medida` | 10 |
| `otro_tema` | `otro_track_ambiental` | 8 |
| `otro_tema` | `problema_o_solucion_concreta` | 8 |
| `politica_o_economia_sin_medida` | `gestion_sin_problema_ni_solucion` | 6 |
| `seguridad_vial` | `problema_o_solucion_concreta` | 6 |
| `nota_de_color` | `problema_o_solucion_concreta` | 6 |
| `nota_de_color` | `seguridad_vial` | 5 |
| `otro_track_ambiental` | `problema_o_solucion_concreta` | 5 |
| `problema_o_solucion_concreta` | `gestion_sin_problema_ni_solucion` | 4 |
| `movilidad_de_pasada` | `problema_o_solucion_concreta` | 4 |
| `otro_track_ambiental` | `politica_o_economia_sin_medida` | 4 |
| `otro_tema` | `gestion_sin_problema_ni_solucion` | 4 |
| `gestion_sin_problema_ni_solucion` | `seguridad_vial` | 3 |
| `otro_track_ambiental` | `otro_tema` | 3 |
| `problema_o_solucion_concreta` | `politica_o_economia_sin_medida` | 2 |
| `gestion_sin_problema_ni_solucion` | `politica_o_economia_sin_medida` | 2 |
| `movilidad_de_pasada` | `seguridad_vial` | 1 |
| `nota_de_color` | `otro_tema` | 1 |
| `otro_track_ambiental` | `gestion_sin_problema_ni_solucion` | 1 |
| `seguridad_vial` | `gestion_sin_problema_ni_solucion` | 1 |
| `movilidad_de_pasada` | `politica_o_economia_sin_medida` | 1 |
| `politica_o_economia_sin_medida` | `otro_tema` | 1 |
| `problema_o_solucion_concreta` | `seguridad_vial` | 1 |
| `movilidad_de_pasada` | `nota_de_color` | 1 |
| `seguridad_vial` | `nota_de_color` | 1 |
| `seguridad_vial` | `politica_o_economia_sin_medida` | 1 |

## Desacuerdos en relevancia

| Nota | Fuente | Referencia | Qwen | Comentario de Haiku |
|---|---|---|---|---|
| Prefeitura oferece transporte público gratuito para as eleições | Mobilidade Sampa | problema_o_solucion_concreta | gestion_sin_problema_ni_solucion | Medida concreta de transporte (gratuidad en 101 líneas); el problema de llegar a votar aparece como contexto. Dudosa: es |
| Cómo ir al Malba en transporte público y auto | La Nación | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Guía práctica de cómo llegar al MALBA: consejos genéricos, sin problema ni solución. Dudosa: la movilidad es el eje de l |
| Garrafas PET viram flutuadores de barcos no PR | CicloVivo | otro_track_ambiental | problema_o_solucion_concreta | Reúso de botellas PET como flotadores de barcos: reciclaje de plástico y fabricación náutica, sin problema ni solución d |
| Ya tiene abogado: un pato fue desalojado de la peatonal de Mendoza y los vecinos | TN | otro_tema | problema_o_solucion_concreta | Desalojo de un pato de una peatonal: tema municipal y animal, sin movilidad. |
| Tecnologia identifica excesso de velocidade em ônibus durante a Semana Nacional  | Mobilidade Sampa | seguridad_vial | problema_o_solucion_concreta | Telemetría de buses para detectar exceso de velocidad en la Semana Nacional de Tránsito: foco en prevención de siniestro |
| Radiografía de los peatones: dicen que los respetan y a ellos se los percibe irr | Clarín | seguridad_vial | problema_o_solucion_concreta | Encuesta sobre respeto de peatones y automovilistas a las normas de tránsito: educación vial, queda afuera. |
| Bicicletas por $8.000 al mes: cómo son los nuevos planes de hasta 30 cuotas sin  | Clarín | politica_o_economia_sin_medida | problema_o_solucion_concreta | Promociones de cuotas de bancos para comprar bicicletas: finanzas y comercio, sin medida de transporte. Dudosa: habla de |
| En Estados Unidos: los seis autos eléctricos usados que los expertos recomiendan | La Nación | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Guía de compra de autos eléctricos usados en EE.UU.: consejos de consumo sin problema ni solución. Dudosa: los vehículos |
| Quiénes recibirán una multa de $239.553 en Buenos Aires en diciembre por incumpl | TN | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Listado de multas de tránsito en CABA: informa importes sin problema ni solución. Dudosa: menciona la movilidad de perso |
| Linhas 704 e 528 terão novos horários a partir de segunda-feira | Mobilidade Sampa | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Cambio de horarios de dos líneas de colectivo en Jundiaí: ajuste de programación, gestión sin problema ni solución de fo |
| Entra en vigencia la renuncia voluntaria a los subsidios de colectivos y trenes: | TN | politica_o_economia_sin_medida | problema_o_solucion_concreta | Renuncia voluntaria al subsidio del transporte: política de subsidios y redistribución. Dudosa: es una tarifa concreta p |
| A group of young people just forced Hawaiʻi to take major climate action | Grist | politica_o_economia_sin_medida | problema_o_solucion_concreta | Acuerdo judicial que obliga a Hawái a descarbonizar el transporte al 2045: meta y plan, sin medida concreta. Dudosa: el  |
| Grupo CCR e SENAI-SP firmam parceria para formação profissional em mobilidade | Mobilidade Sampa | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Convenio de formación profesional entre una concesionaria y un instituto: acuerdo de recursos humanos sin medida de movi |
| Guía para viajar en subte: qué estaciones siguen abiertas y cuáles son las que e | Clarín | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Guía de estaciones de subte abiertas y cerradas por la pandemia: informa sin problema ni solución planteados. Dudosa: lo |
| Peças feitas com madeira substituem louça e porcelana em banheiro | CicloVivo | otro_track_ambiental | problema_o_solucion_concreta | Sanitarios de madera en lugar de cerámica: materiales de construcción, otro track ambiental. |
| Azul lança serviço de Concierge com automóveis da BYD | CicloVivo | movilidad_de_pasada | problema_o_solucion_concreta | Servicio premium de concierge de una aerolínea con autos eléctricos para clientes frecuentes: anuncio comercial, la movi |
| Mercedes-Benz VLE: debutto ufficiale il 10 marzo a Stoccarda | HDmotori | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Lanzamiento de una van eléctrica premium: anuncio de producto sin problema de movilidad planteado. Dudosa: un vehículo e |
| Cómo funciona el robot que viste a personas con movilidad reducida | TN | otro_tema | problema_o_solucion_concreta | Robot de asistencia para vestir personas: robótica asistencial, sin movilidad. |
| “El cambio climático no puede detenerse sin descarbonizar el transporte urbano” | Visión Sustentable | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Nota de prensa de una concesionaria del subte sobre huella de carbono y gestión ambiental: discurso general y medidas in |
| El boleto de colectivo aumentó más de 20% en el AMBA en lo que va del año: cuál  | TN | politica_o_economia_sin_medida | problema_o_solucion_concreta | Aumentos de boleto por inflación e indexación en AMBA y comparación con el interior: tarifas y subsidios, sin medida de  |
| When hurricane evacuation isn’t an option | Grist | otro_track_ambiental | problema_o_solucion_concreta | Evacuación por huracanes y desigualdad: desastre climático; el transporte aparece como barrera de pasada. |
| Maio Amarelo: Fretadão investe em segurança no trânsito com campanhas de conscie | Mobilidade Sampa | seguridad_vial | problema_o_solucion_concreta | Campaña de seguridad en el tránsito de una empresa de transporte fretado: seguridad vial, queda afuera. |
| Sólo en Japón: dejó su bicicleta pinchada en un parte y, en lugar de robársela,  | Clarín | nota_de_color | problema_o_solucion_concreta | Historia viral de una bicicleta reparada en Japón: nota de color, sin problema ni solución de movilidad. |
| Paro de subte: la línea D estará interrumpida este lunes desde las 21 por una me | TN | politica_o_economia_sin_medida | problema_o_solucion_concreta | Paro de la línea D del subte por reclamos laborales (dos francos, personal, asbesto): conflicto gremial sin medida de mo |
| Habrá un corte de tránsito parcial por seis días en el centro de Córdoba: los mo | El Doce | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Aviso de corte parcial de un carril por obras de una empresa de energía: informa sin problema ni solución. Criterio igua |
| Cómo funciona la nueva ley de licencias de conducir para personas mayores de 70  | Clarín | seguridad_vial | problema_o_solucion_concreta | Renovación de licencias para mayores de 70 y pruebas de manejo: seguridad vial, queda afuera. |
| ¿Moto o transporte público? La cuenta que tenés que hacer para saber si te convi | Clarín | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Comparativa de costos moto vs transporte publico: informa |
| Rusia 2018 | 4000 km. en bicicleta por Europa para ver a la Selección | TN | nota_de_color | problema_o_solucion_concreta | Exclusion: nota de color o viral: Cronica de un viaje en bicicleta para ver al seleccionado: nota de color, sin problema |
| El Gobierno aplicará aumentos escalonados en las tarifas de los colectivos y los | TN | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Cronograma de aumentos de tarifas de colectivos y trenes: |
| Cuánto cuesta cargar coches eléctricos en México: Tipos de carga y precios | Ecoportal | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Guia de consumo sobre costo de cargar autos electricos en |
| Vivía en un colectivo con su bebé y ahora construye estufas para que otras famil | TN | otro_tema | problema_o_solucion_concreta | Paso 1, pregunta 1: el tema central no es movilidad: Estufas para calefaccion en Bariloche: no es movilidad. |
| La respuesta de ERSA tras la denuncia de choferes por falta de colectivos | El Doce | problema_o_solucion_concreta | gestion_sin_problema_ni_solucion | Paso 1, pregunta 3: problema o solucion concreta: Falta de colectivos en Cordoba (choferes dicen 60 a 70 por dia): defic |
| Los colectiveros, los otros héroes de la pandemia: transportan a los esenciales  | Clarín | nota_de_color | problema_o_solucion_concreta | Exclusion: nota de color o viral: Cronica humana de colectiveros en la pandemia. Duda fuerte: describe capacidad limitad |
| Ciudad: hasta cuándo funciona el boleto educativo | La Nación | problema_o_solucion_concreta | gestion_sin_problema_ni_solucion | Paso 1, pregunta 3: problema o solucion concreta: Programa concreto de boleto subsidiado (ampliado a nivel superior). Du |
| Mogi das Cruzes garante continuidade do transporte público com renovação de cont | Mobilidade Sampa | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Renovacion de un contrato de concesion de colectivos: ges |
| Cómo funcionan los trenes hoy, jueves 30 de mayo | TN | otro_tema | problema_o_solucion_concreta | Paso 1, pregunta 1: el tema central no es movilidad: Medida de fuerza gremial en trenes (velocidad limitada por paritari |
| Crescimento da frota de veículos elétricos impulsiona modernização das rodovias  | Mobilidade Sampa | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Estadistica de flota electrica en Sao Paulo con inversion |
| Este motor ultracompacto ha destrozado al hidrógeno: es el futuro de la movilida | Ecoportal | movilidad_de_pasada | problema_o_solucion_concreta | Paso 1, pregunta 1: movilidad de pasada: Motor rotativo de combustion para multiples usos (motos, generadores, drones).  |
| El Consejo Internacional de Transporte Limpio revela que operar un vehículo eléc | Ecoportal | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Informe que compara costo de operar autos electricos vs n |
| La AIE prevé que los autos eléctricos alcancen el 29 % de las ventas mundiales e | Ecoportal | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Proyeccion de ventas de autos electricos de la AIE: dato  |
| Passerini reclamó en el Congreso por los subsidios al transporte y explicó qué p | El Doce | politica_o_economia_sin_medida | problema_o_solucion_concreta | Paso 1, pregunta 3: politica o economia sin medida de transporte: Reclamo de intendentes en el Congreso por reparto de f |
| ABB acquisisce BrightLoop | Recover Web | politica_o_economia_sin_medida | problema_o_solucion_concreta | Paso 1, pregunta 3: politica o economia sin medida de transporte: Adquisicion empresarial de una firma de electronica de |
| ¿Tesla dice adiós a los autos eléctricos? Elon Musk apuesta al dominio mundial | Ecoportal | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Estrategia de Tesla que deja de lado autos electricos hac |
| The US electric grid is getting a $3.5 billion upgrade | Grist | otro_track_ambiental | problema_o_solucion_concreta | Exclusion: otro track ambiental: Inversion en la red electrica de EE. UU.: energia, no movilidad. |
| Micro trailer dobrável pode ser acoplado em bike para “escapar” da cidade | CicloVivo | movilidad_de_pasada | problema_o_solucion_concreta | Paso 1, pregunta 1: movilidad de pasada: Trailer plegable para llevar de remolque en bici con fines de camping: la movil |
| En la empresa TBA sospechan de los incidentes | Clarín | problema_o_solucion_concreta | seguridad_vial | Paso 1, pregunta 3: problema o solucion concreta: Problema concreto de servicio ferroviario (paralizacion y menos formac |
| Huawei gana el premio al "Caso de uso de transporte óptico más innovador" en Net | Infobae | otro_tema | problema_o_solucion_concreta | Paso 1, pregunta 1: el tema central no es movilidad: Premio de Huawei a redes opticas: telecomunicaciones, no movilidad. |
| Habrá paro de transporte urbano el martes en Córdoba | El Doce | otro_tema | problema_o_solucion_concreta | Paso 1, pregunta 1: el tema central no es movilidad: Paro de UTA por salarios: disputa gremial. Duda: afecta el servicio |
| Trenes más exigidos: hoy transportan un 54% más de pasajeros que en 2015 | Clarín | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paso 1, pregunta 3: informa sin problema ni solucion concreta: Informe oficial de crecimiento de pasajeros en trenes: in |
| Proponen que los autos 0 km lleven una etiqueta oficial según su calificación en | TN | seguridad_vial | problema_o_solucion_concreta | Paso 1, pregunta 2: seguridad vial, queda afuera: Propuesta de etiquetar autos con resultados de crash test: seguridad v |
| El Gobierno acelera la privatización de los trenes de pasajeros y divide el nego | Clarín | problema_o_solucion_concreta | politica_o_economia_sin_medida | Medida concreta de transporte (concesión de trenes de pasajeros y división de cargas). Duda fuerte: el foco es económico |
| Corte total por 10 días en una calle clave de zona norte de Córdoba: mirá los de | El Doce | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Aviso de corte de calle por repavimentación: informa desvíos sin plantear problema ni solución. |
| Dove nasce la mobilità del futuro: dalla Cina le lezioni che l’Europa non può ig | HDmotori | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Entrevista de opinión sobre el futuro de la mobilidad: reflexión general sin problema ni solución concreta. Duda fuerte. |
| Colgada del poste: la insólita "solución" para que no le roben la bici | El Doce | nota_de_color | problema_o_solucion_concreta | Nota de color: bicicleta colgada de un poste para evitar robos; el tránsito es solo escenario. |
| Por el paro, un joven caminó 12,7 kilómetros desde Argüello hasta Alberdi | El Doce | nota_de_color | problema_o_solucion_concreta | Historia personal durante un paro de transporte: nota de color. |
| Así es el tren que recorre paisajes a una de las mayores alturas del planeta | Clarín | otro_tema | problema_o_solucion_concreta | Nota turística sobre el Tren a las Nubes: informa sin problema ni solución de movilidad. Duda moderada. |
| Coronavirus en la Argentina | Trabajadores del agro deberán tramitar un permiso  | TN | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Trámite de constancia para circulación de trabajadores agropecuarios durante la pandemia: gestión sin problema ni soluci |
| Two Sessions: EVs dominate Chinese provincial plans | Dialogue Earth | problema_o_solucion_concreta | politica_o_economia_sin_medida | Regla 3: planes provinciales concretos de vehículos eléctricos y carga. Duda fuerte: el enfoque es industrial. |
| In Michigan, a new housing project shows that sustainable development isn’t only | Grist | otro_tema | problema_o_solucion_concreta | Proyecto de vivienda sostenible: el transporte es un detalle del barrio. |
| Mercedes-Benz, il diesel resta: ecco come sono cambiati i consumi dal 1936 al 20 | HDmotori | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Estrategia y evolución histórica de motores diésel de una marca: informa sin problema ni solución concreta. Duda moderad |
| Tras siete horas sin funcionar, se levantó el paro de colectivos en el AMBA | TN | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Paro de choferes por aguinaldo y reclamo tarifario de cámaras: conflicto laboral y tarifa, sin problema ni solución nuev |
| Calculadora de TN.com.ar: tras el aumento del subte, fijate cuánto vas a gastar  | TN | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Calculadora de gasto en transporte tras aumentos: informa tarifas sin problema ni solución nueva. |
| Incidentes en la estación Constitución por demoras en el subte | Clarín | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Incidente puntual por demora de una formación en el subte: no describe un problema estructural ni una solución. Duda mod |
| Allison Transmission lancia Allison Ventures e annuncia il primo investimento in | Recover Web | politica_o_economia_sin_medida | problema_o_solucion_concreta | Inversión de venture capital en imanes para motores eléctricos: economía sin medida de transporte. Duda moderada. |
| En marcha las obras de la gigafactoria de Stellantis y CATL en Figueruelas que p | Movilidad Eléctrica | politica_o_economia_sin_medida | problema_o_solucion_concreta | Inversión industrial en una fábrica de baterías: economía sin medida de transporte. Duda fuerte: es una inversión para m |
| El Centro de Vehículos Eléctricos Ford ya es una realidad | Ecoticias | politica_o_economia_sin_medida | problema_o_solucion_concreta | Inauguración de una planta industrial de vehículos eléctricos: economía e inversión, sin medida de transporte ni problem |
| Boleto estudiantil universitario. A partir de cuándo regirá el nuevo beneficio e | La Nación | problema_o_solucion_concreta | gestion_sin_problema_ni_solucion | Regla 3, tipo ambas: boleto gratuito para estudiantes universitarios frente al costo del transporte. Duda fuerte: es una |
| Choferes anunciaron asambleas y amenazan con paro en el transporte interurbano | El Doce | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Conflicto salarial y amenaza de paro en transporte interurbano: gestión laboral. |
| Fundación Grupo Volkswagen avanza con la creación del Bosque Volkswagen | Visión Sustentable | otro_track_ambiental | problema_o_solucion_concreta | Reforestación de una fundación automotriz: otro track ambiental. |
| Es el tren de carga más largo de la historia: tiene 7,6 kilómetros de largo y es | Clarín | nota_de_color | problema_o_solucion_concreta | Récord de tren de carga en un viaje de prueba: nota de color, sin problema ni solución planteados. Duda moderada. |
| Luca de Meo, serve maggiore flessibilità sulla transizione ma nessun passo indie | HDmotori | politica_o_economia_sin_medida | problema_o_solucion_concreta | Opinión de un ejecutivo sobre la regulación europea del auto eléctrico: política sin medida concreta. Duda moderada. |
| Intelligenza artificiale e mobilità smart: le soluzioni Bosch al CES 2026 | HDmotori | movilidad_de_pasada | problema_o_solucion_concreta | Anuncios tecnológicos de una empresa en varios rubros: la movilidad es una parte. Duda fuerte. |
| Por la quita de subsidios a colectivos en el AMBA: las empresas reducirán los se | Clarín | politica_o_economia_sin_medida | problema_o_solucion_concreta | Quita de subsidios y reducción de servicios nocturnos: disputa económica entre jurisdicciones. Duda fuerte; el criterio  |
| Buenas noticias para California: Newsom destina 140 millones de dólares a proyec | Clarín | seguridad_vial | problema_o_solucion_concreta | Fondos estatales para proyectos de seguridad vial: la guía excluye la seguridad vial aunque incluya ciclovías y veredas. |
| Firmada por Gavin Newsom: una nueva ley autoriza un préstamo de emergencia de 59 | Clarín | politica_o_economia_sin_medida | problema_o_solucion_concreta | Préstamo de emergencia para sostener un sistema de transporte: medida financiera sin medida de transporte nueva. Duda fu |
| Nuevo saldo negativo de la SUBE: otra vez, sólo alcanza para dos viajes en colec | Clarín | gestion_sin_problema_ni_solucion | problema_o_solucion_concreta | Cambio del saldo negativo de la SUBE: gestión tarifaria. |
