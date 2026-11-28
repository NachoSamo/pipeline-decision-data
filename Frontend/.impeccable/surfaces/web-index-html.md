---
version: 1
slug: "web-index-html"
primary_target: "web/index.html"
related_targets: []
---

# Surface brief: web del grafo (Frontend/web/index.html)

Mode: Read (ensayo de método) con el grafo como pieza que se explora. Audiencia: comunidad tech y público general, que llegan desde redes. Acción: explorar el grafo y leer cómo se hizo. Prueba: el JSON del contrato y el recorrido medido de la v1. Restricción: los límites siempre a la vista.

## Direction contract

THESIS: The graph is the proof of the method. A canvas of 1.169 live nodes comes first, and the essay explaining how it was built comes right after. The category standard, played straight: an Obsidian-grade graph plus a Pudding-grade method essay. No hero-metric template and no card grid.

OWN-WORLD: Blue-black ground. Five node hues by type: coral problems, mint solutions, amber root causes, steel-blue actors, violet categories. Highlighted nodes carry a soft bloom ring. UI is hairline 1px panels at 8px radius with tabular numerals. Geist for UI and essay, Geist Mono only for numbers and ids. Text selection, focus rings and scrollbars are themed in the coral or mint accent.

STORY: The visitor sees the graph breathing and reads in one line what it is. They click a node, and the camera flies to it while its neighbours light up. Then they scroll: the method appears as a measured funnel from 47.944 notes down to 547 classified, then how no-patterns are scored, then the limits, then the rankings as text. They leave knowing how it was done and how much to trust it.

FIRST VIEWPORT: The 3D graph is full-bleed. Top-left: the title and a single sentence, with "Cómo lo hicimos" below. Top-right: the dataset selector and a "v1 · no vigente" status pill. Left rail: type filters with counts and the search. Right: a detail drawer that slides in on selection. Bottom: the legend and the "Recorrer vacíos" tour.

FORM: canon (category standard), 1 of 1. seed:0424af22ba715988
SIGNATURE: clicking a node flies the camera to it, dims everything else and pulses its neighbours. "Recorrer vacíos" tours the top 10 gaps.
MOTION: a camera orbit on the intro that settles; particles flow along MITIGA_POTENCIALMENTE edges; ease-out everywhere; reduced motion disables the orbit and the particles.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
