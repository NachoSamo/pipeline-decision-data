# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML, CSS y JS estáticos, sin build. El grafo se dibuja con three.js (vía `3d-force-graph`) y los datos llegan como JSON. Deploy en Vercel, con `Frontend/web` como Root Directory. El deploy lo hace el equipo.

## Users

- **Comunidad tech y datos**, que llega desde un posteo en LinkedIn u otras redes. Le interesa cómo se construyó el análisis.
- **Público general** interesado en ambiente y residuos, sin formación técnica. Tiene que entender qué está mirando sin leer documentación.

Las dos audiencias llegan desde el celular o desde una pestaña nueva, por lo general con poca paciencia.

## Product Purpose

Mostrar, como pieza de difusión, el análisis que hizo el equipo para la hackathon Hack to the Future (Córdoba Tech Week 2026). Miles de notas de medios se convirtieron en un grafo de problemas, soluciones, causas raíz y actores de la gestión de residuos.

El mensaje central es **cómo lo hicimos**: scraping de medios, clasificación con LLM, grafo de conocimiento y detección de no-patrones (vacíos de solución, gemas ocultas, causas cuello de botella). El grafo es la prueba visible del método.

Hay éxito si la persona explora el grafo, entiende el recorrido del método y se va sabiendo qué tan confiables son los datos.

## Positioning

No es un dashboard de un dataset público: es el pipeline propio del equipo, de punta a punta, con sus límites a la vista.

## Capabilities and Constraints

- Lee `web/data/index.json` y un `<version>-<tema>.json` por versión, con el contrato que genera `Frontend/exportar_web.py`.
- La versión disponible hoy (v1 de residuos) **no es vigente**: fue un piloto con Qwen 2.5 3B y su ranking tiene ruido. La página tiene que decirlo.
- Hay versiones futuras pendientes, por ejemplo la v2 de movilidad, que todavía no pasa su gate.

## Evidence on Hand

- `web/data/v1-residuos.json`: 1.169 nodos y 1.838 aristas. Incluye 409 problemas y 133 soluciones.
- Los rankings de vacíos, gemas y cuellos de botella.
- No hay métricas de impacto, usuarios ni testimonios. No inventarlos.

## Product Principles

1. **El método se muestra, no se declama.**
2. **Los límites van a la vista, no en letra chica.**
3. **Primero se entiende y después se explora.**
4. **Ninguna cifra que no salga del JSON.**

## Accessibility & Inclusion

Tiene que funcionar en el celular. Hace falta una alternativa textual al grafo (rankings en lista) para quien no puede o no quiere usar el canvas 3D.

## Brand Commitments

- Se eligió el estándar de la categoría, bien ejecutado y sin ironía.
- Nivel de terminación de referencia: **Obsidian Graph View**, para el grafo, y **The Pudding**, para el ensayo de método.
