---
name: Grafo del método
description: Un grafo 3D vivo de notas de medios sobre residuos, seguido del ensayo que explica cómo se construyó.
colors:
  fondo: "#0b0e14"
  panel: "#11151d"
  panel-alto: "#171c26"
  fila-activa: "#222a38"
  borde: "#232b38"
  borde-hover: "#33405a"
  texto: "#e8ecf2"
  texto-ensayo: "#c9d1dd"
  texto-2: "#9aa6b8"
  texto-3: "#808c9f"
  problema: "#ff7a6b"
  problema-hover: "#ff9184"
  tinta-sobre-coral: "#1a0d0b"
  solucion: "#5fd4a8"
  causa: "#f2b84b"
  actor: "#7b93b8"
  categoria: "#a78bfa"
  ubicacion: "#4fc3d9"
  arista-activa: "#c3ccda"
typography:
  display:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(28px, 3.6vw, 48px)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(28px, 3vw, 38px)"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  lead:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 400
    lineHeight: 1.6
  body-ensayo:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.7
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.35
  cifra:
    fontFamily: "Geist Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 500
    fontFeature: "tnum"
rounded:
  fino: "3px"
  fila: "6px"
  panel: "8px"
  pastilla: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  seccion: "112px"
components:
  boton:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto}"
    typography: "{typography.label}"
    rounded: "{rounded.panel}"
    padding: "8px 14px"
  boton-hover:
    backgroundColor: "{colors.panel-alto}"
  boton-primario:
    backgroundColor: "{colors.problema}"
    textColor: "{colors.tinta-sobre-coral}"
    typography: "{typography.label}"
    rounded: "{rounded.panel}"
    padding: "8px 14px"
  boton-primario-hover:
    backgroundColor: "{colors.problema-hover}"
  boton-primario-activo:
    backgroundColor: "{colors.panel-alto}"
    textColor: "{colors.problema}"
  buscador:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.panel}"
    padding: "9px 12px 9px 34px"
  pastilla-estado:
    textColor: "{colors.causa}"
    rounded: "{rounded.pastilla}"
    padding: "4px 9px"
  panel-detalle:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.panel}"
    padding: "18px 18px 14px"
    width: "340px"
  fila-lista:
    textColor: "{colors.texto}"
    rounded: "{rounded.fila}"
    padding: "6px 8px"
  fila-lista-hover:
    backgroundColor: "{colors.panel-alto}"
---

# Design System: Grafo del método

## Overview

**Creative North Star: "La sala de observación"**

Un suelo azul negro donde el dato es la única fuente de luz. El grafo ocupa todo el primer viewport y la interfaz flota encima en paneles de línea fina, sin peso propio: el color pertenece a los nodos, no a los controles. Debajo, el ensayo de método se lee como una columna tranquila de 68 caracteres, con las cifras en mono tabular para que se puedan comparar de un vistazo.

La densidad es de herramienta: textos de 12 a 14 px en la interfaz, filas de 6 a 8 px de relleno, paneles de 8 px de radio. El ensayo cambia de registro: cuerpo de 17 px con interlineado 1,7 y aire vertical generoso entre secciones. El movimiento es de salida suave, la misma curva en todo, y se apaga con movimiento reducido.

Es el estándar de la categoría ejecutado sin ironía: grafo con terminación de Obsidian, ensayo con terminación de The Pudding.

**Key Characteristics:**
- Fondo azul negro único (#0b0e14) compartido por la página y el lienzo 3D.
- Seis tonos de nodo por tipo; los controles son neutros.
- Paneles de 1 px a 8 px de radio, translúcidos sobre el grafo.
- Geist para todo el texto, Geist Mono solo para cifras e identificadores.
- Una sola curva de salida para todas las transiciones.

## Colors

Neutros fríos de baja luminancia y una paleta categórica saturada que solo vive en los datos.

### Primary
- **Coral Problema** (problema): nodos de tipo problema, vacíos de solución, la pastilla de error de carga y el único botón primario ("Recorrer vacíos"). Sobre coral, el texto va en **Tinta sobre Coral** (tinta-sobre-coral); al pasar el puntero, **Coral Claro** (problema-hover).

### Secondary
- **Menta Solución** (solucion): nodos de solución, gemas ocultas, aristas MITIGA_POTENCIALMENTE y sus partículas, enlaces, aro de foco, selección de texto (al 35 %) y la pastilla "vigente". Es el acento de interacción del sistema.

### Tertiary
- **Ámbar Causa** (causa): causas raíz, cuellos de botella, la pastilla "no vigente" y el rombo de cada límite.
- **Azul Acero Actor** (actor): nodos de actor y relleno por defecto de las barras del embudo.
- **Violeta Categoría** (categoria): nodos de categoría.
- **Cian Ubicación** (ubicacion): nodos de ubicación.

### Neutral
- **Fondo Nocturno** (fondo): página, lienzo del grafo y viñeta superior e inferior de la escena.
- **Panel** (panel) y **Panel Alto** (panel-alto): superficies de controles, y hover de filas y desplegables.
- **Fila Activa** (fila-activa): opción elegida o con hover en los resultados del buscador.
- **Borde** (borde): todas las líneas de 1 px; **Borde Hover** (borde-hover) al pasar sobre campos y botones.
- **Texto** (texto), **Texto Ensayo** (texto-ensayo), **Texto 2** (texto-2) y **Texto 3** (texto-3): de mayor a menor jerarquía. Texto 3 es el mínimo para leyendas, conteos y placeholders.
- **Arista Activa** (arista-activa): aristas de la selección que no son de mitigación.

### Named Rules
**The Color Es Dato Rule.** Los seis tonos de tipo solo identifican tipos de nodo y sus métricas (vacío coral, gema menta, cuello ámbar). Un control nunca toma un tono de tipo para decorar; la excepción es el botón primario coral, que lanza el recorrido de vacíos.

**The Mismo Hex Rule.** Los colores de tipo son idénticos en style.css y en app.js. Un tono nuevo se agrega en los dos lados a la vez.

**The Atenuado Translúcido Rule.** Con una selección, el resto de los nodos pasa a gris azulado translúcido (rgba(60,70,88,0.14)) y las aristas ajenas a rgba(40,48,62,0.25): quedan de fondo sin tapar lo resaltado.

## Typography

**Display Font:** Geist (con ui-sans-serif, system-ui)
**Body Font:** Geist (con ui-sans-serif, system-ui)
**Label/Mono Font:** Geist Mono (con ui-monospace), solo cifras e identificadores

**Character:** Una sola sans geométrica y neutra en todos los tamaños; el contraste lo hacen el peso (400, 500, 600) y el tracking negativo en titulares, no un cambio de familia.

### Hierarchy
- **Display** (600, clamp(28px, 3.6vw, 48px), 1.05, -0.025em): el titular del grafo. En el celular, 28 px fijos. La segunda parte va en Texto 2.
- **Headline** (600, clamp(28px, 3vw, 38px), 1.1, -0.025em): títulos de sección del ensayo.
- **Title** (600, 19 a 20 px, 1.25, -0.01em): título del panel de detalle y subtítulos del ensayo.
- **Lead** (400, 20px, 1.6): el párrafo de entrada del ensayo.
- **Body ensayo** (400, 17px, 1.7, máximo 68ch): párrafos del método, en Texto Ensayo.
- **Body** (400, 16px, 1.6): base de la página; la bajada usa 15 px y máximo 52ch.
- **Label** (500, 12 a 13px): botones, filtros, leyenda, pastillas y subtítulos del panel. Sin mayúsculas forzadas ni tracking abierto.
- **Cifra** (Geist Mono 400 a 500, 12 a 15px, tabular-nums): conteos de filtros, valores de rankings, cifras del embudo y el contador del recorrido.

### Named Rules
**The Mono Es Número Rule.** Geist Mono aparece solo en cifras, identificadores de versión y contadores, siempre con números tabulares. Nunca en titulares ni en prosa.

## Layout

La escena del grafo ocupa 100svh (mínimo 560px). El lienzo 3D va de borde a borde, detrás; encima, una grilla de tres columnas (280px, 1fr, 340px) y tres filas: titular y dataset arriba, riel de filtros y panel de detalle al medio, leyenda y acciones abajo. El relleno es de 24px y el gap de 16px. La columna central queda libre para el grafo, y los contenedores dejan pasar el puntero salvo en sus hijos.

Dos viñetas en degradado de Fondo Nocturno (220px arriba, 120px abajo, al 85 %) garantizan la lectura del texto sobre el grafo.

**Encuadre con view offset.** La cámara corre el centro óptico para que el nodo enfocado caiga en el área libre: en escritorio, 40px a la derecha cuando hay selección; en el celular, -10 % del alto sin selección y +16 % con la hoja abierta. El offset se reaplica en cada cuadro porque la librería lo borra.

**Celular (900px o menos).** Una columna, en orden dataset, titular, riel y barra; relleno de 16px y gap de 12px. La escena baja a 86svh (mínimo 620px) para que asome el ensayo y se pueda scrollear, ya que arrastrar sobre el grafo lo gira. La viñeta superior se vuelve opaca hasta 230px. Los filtros por tipo y "Descargar imagen" se ocultan; los botones de acción se reparten el ancho. Con una selección, titular, riel y leyenda se ocultan y el detalle sube como hoja inferior. El grafo usa menos resolución por nodo y no muestra partículas.

**Ensayo.** Columna de 68ch centrada, relleno de 96px arriba y 64px abajo, 112px entre secciones (64px y 80px en el celular). Los rankings se abren a 1120px en tres columnas con gap de 40px, y pasan a una en el celular.

**Ritmo.** Pasos de 4, 8, 12, 16 y 24px en la interfaz; 56px antes de cada subtítulo del ensayo.

## Elevation & Depth

Híbrido: la profundidad principal es la del propio espacio 3D y la translucidez de los paneles sobre él. Las superficies de interfaz son planas, con borde de 1px. Solo dos piezas flotantes llevan sombra difusa: el desplegable del buscador y el panel de detalle.

### Shadow Vocabulary
- **Desplegable** (`box-shadow: 0 12px 32px rgb(0 0 0 / 0.45)`): resultados del buscador.
- **Panel flotante** (`box-shadow: 0 16px 40px rgb(0 0 0 / 0.4)`): panel de detalle sobre el grafo.

### Named Rules
**The Plano Salvo Que Flote Rule.** Botones, campos, filtros y tarjetas de límites no llevan sombra. La sombra queda para lo que se superpone al grafo y puede taparlo.

## Shapes

Rectángulos de esquina suave y líneas finas. Paneles, campos, botones y tarjetas a 8px; filas internas, tooltips y la marca del detalle a 6px; las barras del embudo a 3px; las pastillas de estado a 999px. Los puntos de tipo son círculos de 8px; un filtro apagado deja solo el contorno de 1,5px. Los destacados del grafo son aros finos (grosor del 12 % del radio, al 70 % de opacidad) que miran a la cámara y respiran ±8 %. Los íconos son SVG de trazo 1,6px a 16px.

## Components

### Buttons
Neutros y discretos; solo uno lleva color.
- **Shape:** esquina suave (8px), borde de 1px en Borde.
- **Por defecto:** fondo Panel, texto Texto, label 13px 500, relleno 8px 14px. Al pasar, Panel Alto y Borde Hover, transición de 0,2s.
- **Primario:** fondo y borde Coral Problema, texto Tinta sobre Coral; al pasar, Coral Claro. Activo (aria-pressed): fondo Panel Alto, texto coral y borde coral al 50 %.
- **Ícono:** 30 a 32px cuadrados; el de cerrar no tiene borde y toma Panel Alto al pasar.
- **Focus:** contorno de 2px en Menta Solución con 2px de separación.

### Chips
- **Pastilla de estado:** 12px 500, relleno 4px 9px, radio 999px. El borde va al 40 % y el fondo al 10 % del tono: Ámbar Causa para "no vigente", Menta Solución para "vigente".

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** Panel al 88 % (filtros) o al 94 % (detalle) sobre el grafo; Panel sólido en el ensayo y en la hoja del celular.
- **Shadow Strategy:** ver Elevation & Depth.
- **Border:** 1px en Borde.
- **Internal Padding:** 18px en el detalle; 14px 16px en las tarjetas de límites, con un rombo ámbar de contorno a la izquierda.

### Inputs / Fields
- **Style:** fondo Panel, borde de 1px, radio 8px, 13 a 14px. El buscador lleva una lupa SVG en Texto 3 a la izquierda; el selector, una flecha SVG en Texto 2.
- **Focus:** contorno de 2px en Menta Solución. Al pasar, Borde Hover.

### Navigation
- **Riel de filtros:** filas de 7px 8px y radio 6px, con punto de color, nombre y conteo en mono. Apagado: texto en Texto 3 y punto hueco.
- **Listas de vecinos y resultados:** filas de 13px con punto de tipo y relación en 11px Texto 3 alineada a la derecha.
- **Enlace "Cómo lo hicimos":** 14px 500 en Texto, pasa a Menta al hacer hover; la flecha baja 2px con la curva de salida.

### Panel de detalle
Se desliza desde la derecha (translateX del 100 % + 32px) en 0,45s con la curva de salida, y la opacidad en 0,3s. En el celular sube desde abajo como hoja entre 12px de los bordes, sobre la barra, con alto máximo de 38svh.

### Grafo
Fondo Fondo Nocturno, nodos al 95 % de opacidad, tamaño según grado. Las aristas en reposo van al 22 % en acero (MITIGA en menta al 35 %). Al seleccionar, la cámara vuela al nodo en 1,1s, los vecinos quedan con color, el resto se atenúa translúcido y las aristas propias toman 1,2px de ancho. En escritorio, dos partículas menta recorren cada arista MITIGA. Al entrar, la cámara orbita hasta 14s y se detiene al primer toque. Con movimiento reducido no hay órbita, ni partículas, ni respiración de aros, y el vuelo es instantáneo.

### Embudo
Filas de etapa y cifra mono tabular sobre una pista de 10px en Panel, a 3px de radio. El relleno crece en 1,2s con la curva de salida al entrar en vista. Las dos últimas etapas van en Menta y el resto en Azul Acero.

### Rankings
Listas numeradas con contador mono en Texto 3, filas separadas por líneas de 1px, valor mono en Texto 2. Hover en Panel.

## Do's and Don'ts

### Do:
- **Do** usar una sola curva para todo el movimiento: cubic-bezier(0.16, 1, 0.3, 1).
- **Do** mantener los colores de tipo idénticos en style.css y app.js.
- **Do** poner toda cifra en Geist Mono con números tabulares.
- **Do** dibujar los paneles sobre el grafo con 1px de Borde, 8px de radio y fondo Panel translúcido.
- **Do** marcar los destacados con aros finos que miran a la cámara, en el color de su métrica.
- **Do** atenuar lo no seleccionado con translucidez, no con un gris opaco.
- **Do** correr el centro de la cámara con view offset para que lo enfocado no quede detrás de un panel.
- **Do** desactivar órbita, partículas y respiración con prefers-reduced-motion.

### Don't:
- **Don't** usar un tono de tipo de nodo para decorar controles, fondos o titulares.
- **Don't** agregar sombras a botones, campos o tarjetas planas.
- **Don't** usar Geist Mono en prosa o titulares.
- **Don't** bajar de Texto 3 (#808c9f) para texto legible sobre Fondo Nocturno.
- **Don't** forzar mayúsculas ni tracking abierto en labels.
