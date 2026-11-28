import * as THREE from "three";
import ForceGraph3D from "3d-force-graph";

const TIPOS = {
  Problema: { nombre: "Problemas", singular: "Problema", color: "#ff7a6b" },
  Solucion: { nombre: "Soluciones", singular: "Solución", color: "#5fd4a8" },
  CausaRaiz: { nombre: "Causas raíz", singular: "Causa raíz", color: "#f2b84b" },
  Actor: { nombre: "Actores", singular: "Actor", color: "#7b93b8" },
  Categoria: { nombre: "Categorías", singular: "Categoría", color: "#a78bfa" },
  Ubicacion: { nombre: "Ubicaciones", singular: "Ubicación", color: "#4fc3d9" },
};
const RELACIONES = {
  PERTENECE_A: "categoría",
  CAUSADO_POR: "causa",
  AFECTA_A: "afecta a",
  UBICADO_EN: "lugar",
  IMPULSADA_POR: "impulsa",
  APUNTA_A_CATEGORIA: "apunta a",
  MITIGA_POTENCIALMENTE: "posible mitigación",
};
const MARCAS = { vacio: "Vacío de solución", gema: "Gema oculta", cuello: "Cuello de botella" };
const ATENUADO = "rgba(60,70,88,0.14)"; // translúcido: el resto queda de fondo, no tapa
const movil = matchMedia("(max-width: 900px)").matches;
const sinMovimiento = matchMedia("(prefers-reduced-motion: reduce)").matches;
const modoOg = new URLSearchParams(location.search).has("og"); // ?og: encuadre para la imagen de redes
const nf = new Intl.NumberFormat("es-AR");
const nf2 = new Intl.NumberFormat("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const $ = (id) => document.getElementById(id);
const el = (tag, props = {}, ...hijos) => {
  const e = Object.assign(document.createElement(tag), props);
  e.append(...hijos.filter((h) => h != null));
  return e;
};
const punto = (color) => {
  const s = el("span", { className: "punto" });
  s.style.setProperty("--c", color);
  return s;
};
const normalizar = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const humanizar = (s) => (/^[A-Z0-9_ ]+$/.test(s) ? s.replaceAll("_", " ").toLowerCase().replace(/^./, (c) => c.toUpperCase()) : s);

const estado = {
  datos: null,
  porId: new Map(),
  vecinos: new Map(), // id -> [{nodo, tipo}]
  activos: new Set(Object.keys(TIPOS)),
  seleccion: null,
  resaltados: new Set(),
  vacios: [],
  paso: -1,
  orbitando: false,
};

let grafo;
const halos = [];

/* ---------- Carga ---------- */

async function iniciar() {
  try {
    const indice = await (await fetch("data/index.json")).json();
    const params = new URLSearchParams(location.search);
    const elegido = indice.find((d) => d.id === params.get("ds")) || indice[0];
    const sel = $("selector-dataset");
    for (const d of indice) {
      sel.append(el("option", { value: d.id, textContent: `${humanizar(d.tema)} · ${d.version}`, selected: d.id === elegido.id }));
    }
    sel.addEventListener("change", () => {
      const u = new URL(location.href);
      u.searchParams.set("ds", sel.value);
      u.searchParams.delete("nodo");
      location.href = u; // recarga limpia: cada dataset trae su propio grafo
    });
    const datos = await (await fetch(`data/${elegido.archivo}`)).json();
    preparar(datos);
    pintarGrafo();
    pintarTextos();
    const nodo = params.get("nodo");
    if (nodo && estado.porId.has(nodo)) seleccionar(estado.porId.get(nodo));
    else if (!sinMovimiento) orbitar();
    $("cargando").classList.add("listo");
  } catch (err) {
    console.error(err);
    const c = $("cargando");
    c.textContent = "No se pudo cargar el grafo. Revisá la conexión y recargá la página.";
    c.classList.add("error");
  }
}

function preparar(datos) {
  estado.datos = datos;
  const grado = new Map();
  for (const n of datos.nodos) {
    estado.porId.set(n.id, n);
    estado.vecinos.set(n.id, []);
  }
  for (const a of datos.aristas) {
    estado.vecinos.get(a.origen).push({ nodo: estado.porId.get(a.destino), tipo: a.tipo });
    estado.vecinos.get(a.destino).push({ nodo: estado.porId.get(a.origen), tipo: a.tipo });
    grado.set(a.origen, (grado.get(a.origen) || 0) + 1);
    grado.set(a.destino, (grado.get(a.destino) || 0) + 1);
  }
  for (const n of datos.nodos) n.grado = grado.get(n.id) || 0;
  estado.vacios = datos.rankings.vacios_solucion.slice(0, 10).map((r) => estado.porId.get(r.nodo_id)).filter(Boolean);
}

/* ---------- Grafo ---------- */

function colorNodo(n) {
  if (estado.resaltados.size && !estado.resaltados.has(n.id)) return ATENUADO;
  return TIPOS[n.tipo]?.color || "#9aa6b8";
}

// 3d-force-graph reemplaza origen y destino por el objeto del nodo cuando arma el grafo.
const idDe = (x) => (typeof x === "object" ? x.id : x);
const nodoDe = (x) => (typeof x === "object" ? x : estado.porId.get(x));

function colorArista(a) {
  const o = idDe(a.origen), d = idDe(a.destino);
  if (estado.resaltados.size) {
    return estado.seleccion && (o === estado.seleccion.id || d === estado.seleccion.id)
      ? (a.tipo === "MITIGA_POTENCIALMENTE" ? "#5fd4a8" : "#c3ccda")
      : "rgba(40,48,62,0.25)";
  }
  return a.tipo === "MITIGA_POTENCIALMENTE" ? "rgba(95,212,168,0.35)" : "rgba(120,135,160,0.22)";
}

function halo(n) {
  if (!n.destacado) return null;
  const color = { vacio: "#ff7a6b", gema: "#5fd4a8", cuello: "#f2b84b" }[n.destacado];
  const r = Math.cbrt(tamano(n)) * 4 * 1.9;
  const malla = new THREE.Mesh(
    new THREE.RingGeometry(r, r * 1.12, 48),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7, side: THREE.DoubleSide, depthWrite: false }),
  );
  malla.userData = { fase: Math.random() * Math.PI * 2, nodo: n };
  halos.push(malla);
  return malla;
}

const tamano = (n) => (n.tipo === "Categoria" ? 6 : 1) + Math.min(n.grado, 30) * 0.25 + (n.destacado ? 2 : 0);

function pintarGrafo() {
  const contenedor = $("grafo");
  grafo = ForceGraph3D({ rendererConfig: { antialias: true, preserveDrawingBuffer: true, alpha: false } })(contenedor)
    .backgroundColor("#0b0e14")
    .showNavInfo(false)
    .nodeId("id")
    .linkSource("origen")
    .linkTarget("destino")
    .nodeRelSize(4)
    .nodeVal(tamano)
    .nodeColor(colorNodo)
    .nodeOpacity(0.95)
    .nodeResolution(movil ? 8 : 14)
    .nodeLabel((n) => `${TIPOS[n.tipo]?.singular || n.tipo}: ${escapar(humanizar(n.etiqueta))}`)
    .nodeThreeObject(halo)
    .nodeThreeObjectExtend(true)
    .nodeVisibility((n) => estado.activos.has(n.tipo))
    .linkVisibility((a) => estado.activos.has(nodoDe(a.origen).tipo) && estado.activos.has(nodoDe(a.destino).tipo))
    .linkColor(colorArista)
    .linkOpacity(1)
    .linkWidth((a) => (estado.seleccion && esDeSeleccion(a) ? 1.2 : 0))
    .linkDirectionalParticles((a) => (!movil && !sinMovimiento && a.tipo === "MITIGA_POTENCIALMENTE" && (!estado.seleccion || esDeSeleccion(a)) ? 2 : 0))
    .linkDirectionalParticleWidth(1.4)
    .linkDirectionalParticleSpeed(0.004)
    .linkDirectionalParticleColor(() => "#5fd4a8")
    .warmupTicks(movil ? 80 : 160) // el layout arranca armado, sin la explosión inicial
    .cooldownTicks(movil ? 80 : 120)
    .onNodeClick((n) => seleccionar(n))
    .onBackgroundClick(() => deseleccionar())
    .graphData({ nodes: estado.datos.nodos, links: estado.datos.aristas.map((a) => ({ ...a })) });

  grafo.d3Force("charge").strength(-28);
  grafo.d3Force("link").distance((a) => (a.tipo === "PERTENECE_A" ? 60 : 32));
  // Distancia inicial según el tamaño real del layout, que ya viene armado por warmupTicks.
  const bb = grafo.getGraphBbox();
  const radio = bb ? Math.max(...["x", "y", "z"].map((k) => bb[k][1] - bb[k][0])) / 2 : 400;
  estado.distancia = radio * (movil ? 5.2 : 3.6); // el layout sigue abriéndose un poco tras el warmup
  grafo.cameraPosition({ z: estado.distancia });

  // La rueda scrollea la página; Ctrl + rueda (o pellizcar) acerca y aleja.
  grafo.controls().noZoom = true;
  contenedor.addEventListener("wheel", (e) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    const cam = grafo.camera(), centro = grafo.controls().target;
    const v = cam.position.clone().sub(centro).multiplyScalar(Math.exp(e.deltaY * 0.002));
    if (v.length() > 40 && v.length() < 4000) cam.position.copy(centro).add(v);
  }, { passive: false });

  // Con un nodo en la URL, vuelve a enfocarlo cuando el layout se asienta.
  let primeraParada = true;
  grafo.onEngineStop(() => {
    if (primeraParada && estado.seleccion) enfocar(estado.seleccion, 800);
    primeraParada = false;
  });

  const ajustar = () => { grafo.width(contenedor.clientWidth).height(contenedor.clientHeight); encuadrar(); };
  addEventListener("resize", ajustar);
  ajustar();

  // Los halos miran a la cámara y respiran.
  const reloj = new THREE.Clock();
  (function animar() {
    const t = reloj.getElapsedTime();
    const cam = grafo.camera();
    aplicarDesplazamiento();
    for (const h of halos) {
      h.quaternion.copy(cam.quaternion);
      const visible = estado.activos.has(h.userData.nodo.tipo) && (!estado.resaltados.size || estado.resaltados.has(h.userData.nodo.id));
      h.visible = visible;
      if (!sinMovimiento) {
        const s = 1 + Math.sin(t * 1.6 + h.userData.fase) * 0.08;
        h.scale.set(s, s, s);
      }
    }
    requestAnimationFrame(animar);
  })();

  contenedor.addEventListener("pointerdown", () => (estado.orbitando = false));
}

const esDeSeleccion = (a) => {
  const id = estado.seleccion?.id;
  return idDe(a.origen) === id || idDe(a.destino) === id;
};
const escapar = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

function orbitar() {
  estado.orbitando = true;
  const distancia = estado.distancia;
  let angulo = 0;
  const inicio = performance.now();
  (function paso() {
    if (!estado.orbitando || performance.now() - inicio > 14000) return (estado.orbitando = false);
    angulo += 0.0016;
    grafo.cameraPosition({ x: distancia * Math.sin(angulo), z: distancia * Math.cos(angulo) });
    requestAnimationFrame(paso);
  })();
}

function refrescar() {
  grafo.nodeColor(grafo.nodeColor()).linkColor(grafo.linkColor()).linkWidth(grafo.linkWidth())
    .linkDirectionalParticles(grafo.linkDirectionalParticles())
    .nodeVisibility(grafo.nodeVisibility()).linkVisibility(grafo.linkVisibility());
}

// Corre el centro de la imagen para que el nodo quede en el área libre y no detrás de los paneles.
function encuadrar() {
  document.body.classList.toggle("modo-og", modoOg);
  const w = grafo.width(), h = grafo.height();
  const sel = !!estado.seleccion;
  document.querySelector(".escena").classList.toggle("con-seleccion", sel);
  // Celular: la hoja de detalle ocupa la parte de abajo. Escritorio: el panel derecho es más ancho que el riel.
  const dx = modoOg ? -0.2 * w : !movil && sel ? 40 : 0;
  const dy = movil ? (sel ? 0.16 * h : -0.1 * h) : 0;
  estado.desplazamiento = [dx, dy];
}

// three-render-objects borra el view offset en cada actualización; se reaplica en cada cuadro.
function aplicarDesplazamiento() {
  const cam = grafo.camera(), w = grafo.width(), h = grafo.height();
  const [dx, dy] = estado.desplazamiento || [0, 0];
  const v = cam.view;
  if (!dx && !dy) { if (v?.enabled) { cam.clearViewOffset(); } return; }
  if (!v?.enabled || v.offsetX !== dx || v.offsetY !== dy || v.fullWidth !== w || v.fullHeight !== h) {
    cam.setViewOffset(w, h, dx, dy, w, h);
  }
}

function enfocar(n, ms = 1100) {
  if (n.x == null) return;
  const d = 420;
  const r = 1 + d / Math.hypot(n.x, n.y, n.z || 1);
  grafo.cameraPosition({ x: n.x * r, y: n.y * r, z: n.z * r }, n, sinMovimiento ? 0 : ms);
}

/* ---------- Selección y detalle ---------- */

function seleccionar(n, { desdeRecorrido = false } = {}) {
  estado.orbitando = false;
  if (!estado.activos.has(n.tipo)) {
    estado.activos.add(n.tipo);
    const cb = document.querySelector(`#filtros input[value="${n.tipo}"]`);
    if (cb) cb.checked = true;
  }
  estado.seleccion = n;
  estado.resaltados = new Set([n.id, ...estado.vecinos.get(n.id).map((v) => v.nodo.id)]);
  if (!desdeRecorrido) salirDelRecorrido();
  refrescar();
  encuadrar();
  enfocar(n);
  mostrarDetalle(n);
  const u = new URL(location.href);
  u.searchParams.set("nodo", n.id);
  history.replaceState(null, "", u);
}

function deseleccionar() {
  estado.seleccion = null;
  estado.resaltados = new Set();
  refrescar();
  encuadrar();
  const d = $("detalle");
  d.classList.remove("abierto");
  d.setAttribute("aria-hidden", "true");
  const u = new URL(location.href);
  u.searchParams.delete("nodo");
  history.replaceState(null, "", u);
}

function mostrarDetalle(n) {
  const tipo = TIPOS[n.tipo] || { singular: n.tipo, color: "#9aa6b8" };
  $("detalle-titulo").textContent = humanizar(n.etiqueta);

  const marca = $("detalle-marca");
  if (n.destacado) {
    const valor = typeof n.score === "number" ? nf2.format(n.score) : n.score;
    marca.replaceChildren(`${MARCAS[n.destacado]} n.º ${n.puesto} · puntaje `, el("b", { textContent: valor }));
    marca.hidden = false;
  } else marca.hidden = true;

  $("detalle-desc").textContent = n.descripcion;

  const datos = $("detalle-datos");
  datos.replaceChildren();
  const fila = (k, v) => v && datos.append(el("dt", { textContent: k }), el("dd", { textContent: v }));
  datos.append(el("dt", { textContent: "Tipo" }), el("dd", {}, punto(tipo.color), tipo.singular));
  fila("Categoría", n.categoria && humanizar(n.categoria));
  fila("Lugar", n.ubicacion && !/^no especificad/i.test(n.ubicacion) ? n.ubicacion : "");
  fila("Medio", n.fuente);
  fila("Fecha", n.fecha && new Date(n.fecha + "T12:00").toLocaleDateString("es-AR", { day: "numeric", month: "short", year: "numeric" }));
  fila("Conexiones", nf.format(n.grado));

  const fuente = $("detalle-fuente");
  fuente.hidden = !n.url_fuente;
  if (n.url_fuente) fuente.href = n.url_fuente;

  const lista = $("vecinos");
  const vecinos = estado.vecinos.get(n.id)
    .slice()
    .sort((a, b) => (b.nodo.destacado ? 1 : 0) - (a.nodo.destacado ? 1 : 0) || b.nodo.grado - a.nodo.grado);
  lista.replaceChildren(...vecinos.slice(0, 14).map((v) => el("li", {},
    el("button", { type: "button", onclick: () => seleccionar(v.nodo) },
      punto(TIPOS[v.nodo.tipo]?.color), recortar(humanizar(v.nodo.etiqueta), 60),
      el("span", { className: "rel", textContent: RELACIONES[v.tipo] || "" })))));
  if (vecinos.length > 14) lista.append(el("li", { className: "rel", textContent: `y ${vecinos.length - 14} más` }));
  $("vecinos-titulo").hidden = !vecinos.length;

  const d = $("detalle");
  d.classList.add("abierto");
  d.setAttribute("aria-hidden", "false");
  d.scrollTop = 0;
}

const recortar = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);

/* ---------- Recorrido de vacíos ---------- */

function recorrer(delta) {
  if (!estado.vacios.length) return;
  estado.paso = (estado.paso + delta + estado.vacios.length) % estado.vacios.length;
  $("recorrido").hidden = false;
  $("recorrer-vacios").setAttribute("aria-pressed", "true");
  $("recorrer-vacios").textContent = "Salir";
  $("vacio-contador").textContent = `Vacío ${estado.paso + 1} de ${estado.vacios.length}`;
  seleccionar(estado.vacios[estado.paso], { desdeRecorrido: true });
}

function salirDelRecorrido() {
  if (estado.paso < 0) return;
  estado.paso = -1;
  $("recorrido").hidden = true;
  $("recorrer-vacios").setAttribute("aria-pressed", "false");
  $("recorrer-vacios").textContent = "Recorrer vacíos";
}

/* ---------- Búsqueda ---------- */

function buscar() {
  const input = $("buscar"), lista = $("resultados");
  let activo = -1, encontrados = [];
  const cerrar = () => { lista.hidden = true; input.setAttribute("aria-expanded", "false"); activo = -1; };
  const marcar = () => [...lista.children].forEach((li, i) => li.setAttribute("aria-selected", String(i === activo)));
  const elegir = (n) => { cerrar(); input.value = ""; input.blur(); seleccionar(n); };

  input.addEventListener("input", () => {
    const q = normalizar(input.value.trim());
    if (q.length < 2) return cerrar();
    encontrados = estado.datos.nodos
      .filter((n) => normalizar(n.etiqueta).includes(q))
      .sort((a, b) => b.grado - a.grado)
      .slice(0, 8);
    lista.replaceChildren(...(encontrados.length
      ? encontrados.map((n, i) => el("li", { role: "option", id: `r-${i}`, onmousedown: (e) => { e.preventDefault(); elegir(n); } },
          punto(TIPOS[n.tipo]?.color), recortar(humanizar(n.etiqueta), 70)))
      : [el("li", { className: "vacio", textContent: "Sin resultados" })]));
    lista.hidden = false;
    input.setAttribute("aria-expanded", "true");
    activo = -1;
  });
  input.addEventListener("keydown", (e) => {
    if (lista.hidden || !encontrados.length) return;
    if (e.key === "ArrowDown") { activo = Math.min(activo + 1, encontrados.length - 1); marcar(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { activo = Math.max(activo - 1, 0); marcar(); e.preventDefault(); }
    else if (e.key === "Enter") { elegir(encontrados[Math.max(activo, 0)]); e.preventDefault(); }
    else if (e.key === "Escape") cerrar();
  });
  input.addEventListener("blur", () => setTimeout(cerrar, 100));
}

/* ---------- Textos que salen del JSON ---------- */

function pintarTextos() {
  const { meta, nodos, rankings } = estado.datos;
  const cuenta = (t) => nodos.filter((n) => n.tipo === t).length;

  const estadoV = $("estado-version");
  estadoV.textContent = meta.vigente ? `${meta.version} · vigente` : `${meta.version} · no vigente`;
  estadoV.className = `estado ${meta.vigente ? "vigente" : "no-vigente"}`;
  estadoV.title = meta.vigente ? "Versión vigente del análisis" : "Versión anterior: ver «Qué tan confiable es»";

  $("bajada").replaceChildren(
    el("b", { textContent: nf.format(meta.totales.total_problemas) }), " problemas y ",
    el("b", { textContent: nf.format(meta.totales.total_soluciones) }), " soluciones sacadas de notas de medios, unidas por categoría, causa, actor y similitud. Tocá un nodo.",
  );

  // Filtros y leyenda, solo con los tipos que existen en este dataset.
  const presentes = Object.keys(TIPOS).filter((t) => cuenta(t));
  $("filtros").replaceChildren(...presentes.map((t) => {
    const cb = el("input", { type: "checkbox", value: t, checked: true });
    cb.addEventListener("change", () => {
      cb.checked ? estado.activos.add(t) : estado.activos.delete(t);
      if (estado.seleccion && !estado.activos.has(estado.seleccion.tipo)) deseleccionar();
      refrescar();
    });
    return el("label", { className: "filtro" }, cb, punto(TIPOS[t].color),
      el("span", { className: "nombre", textContent: TIPOS[t].nombre }),
      el("span", { className: "cuenta", textContent: nf.format(cuenta(t)) }));
  }));
  $("leyenda").replaceChildren(
    ...presentes.map((t) => el("span", {}, punto(TIPOS[t].color), TIPOS[t].nombre)),
    el("span", {}, el("i", { className: "linea" }), "Posible mitigación"),
    el("span", {}, el("i", { className: "anillo" }), "Top 15 en vacíos, gemas o cuellos"),
    el("span", { className: "ayuda", textContent: movil ? "Arrastrá para girar · pellizcá para acercar" : "Arrastrá para girar · Ctrl + rueda para acercar" }),
  );

  // Embudo del método.
  const rec = meta.recorrido;
  const embudo = $("embudo");
  if (rec?.pasos?.length) {
    const max = Math.max(...rec.pasos.map((p) => p.cifra));
    embudo.replaceChildren(...rec.pasos.map((p) => {
      const pista = el("div", { className: "pista" }, el("div", { className: "relleno" }));
      pista.firstChild.style.setProperty("--w", `${(p.cifra / max) * 100}%`);
      return el("li", {},
        el("span", { className: "etapa", textContent: p.etapa }),
        el("span", { className: "cifra" }, nf.format(p.cifra), el("small", { textContent: p.unidad })),
        pista,
        el("span", { className: "det", textContent: p.detalle }));
    }));
    $("embudo-fuente").textContent = `Fuente de las cifras: ${rec.fuente}.`;
    new IntersectionObserver(([e], obs) => {
      if (e.isIntersecting) { embudo.classList.add("visto"); obs.disconnect(); }
    }, { threshold: 0.3 }).observe(embudo);
  } else {
    embudo.replaceWith(el("p", { textContent: "Esta versión todavía no tiene el recorrido medido." }));
  }

  // Límites.
  const adv = meta.advertencias?.length ? meta.advertencias : ["Esta versión no declara límites conocidos. Eso no quiere decir que no los tenga."];
  $("advertencias").replaceChildren(...adv.map((t) => el("li", { textContent: t })));

  // Rankings como alternativa textual.
  const fila = (id, valor) => {
    const n = estado.porId.get(id);
    if (!n) return null;
    return el("li", {}, el("button", {
      type: "button",
      onclick: () => { document.querySelector(".escena").scrollIntoView({ behavior: sinMovimiento ? "auto" : "smooth" }); setTimeout(() => seleccionar(n), sinMovimiento ? 0 : 500); },
    }, el("span", { textContent: humanizar(n.etiqueta) }), el("span", { className: "valor", textContent: valor })));
  };
  $("ranking-vacios").replaceChildren(...rankings.vacios_solucion.slice(0, 10).map((r) => fila(r.nodo_id, nf2.format(r.gap_score))).filter(Boolean));
  $("ranking-gemas").replaceChildren(...rankings.gemas_ocultas.slice(0, 10).map((r) => fila(r.nodo_id, nf2.format(r.score_gema_oculta))).filter(Boolean));
  $("ranking-cuellos").replaceChildren(...rankings.causas_cuello_botella.slice(0, 10).map((r) => fila(r.nodo_id, `${r.problemas_que_la_padecen} / ${r.soluciones_que_la_mitigan}`)).filter(Boolean));

  const fecha = (s) => new Date(s + "T12:00").toLocaleDateString("es-AR", { day: "numeric", month: "numeric", year: "numeric" });
  $("pie-fechas").textContent = `Análisis del ${fecha(meta.fecha_analisis)} · datos exportados el ${fecha(meta.fecha_exportacion)}`;
}

/* ---------- Imagen para compartir ---------- */

function descargar() {
  const fuente = grafo.renderer().domElement;
  const lienzo = document.createElement("canvas");
  lienzo.width = fuente.width;
  lienzo.height = fuente.height;
  const ctx = lienzo.getContext("2d");
  ctx.drawImage(fuente, 0, 0);
  const m = estado.datos.meta;
  const esc = lienzo.width / fuente.clientWidth;
  ctx.fillStyle = "rgba(11,14,20,0.82)";
  ctx.fillRect(0, lienzo.height - 56 * esc, lienzo.width, 56 * esc);
  ctx.fillStyle = "#e8ecf2";
  ctx.font = `600 ${16 * esc}px Geist, sans-serif`;
  ctx.fillText(`Residuos en los medios, hecho grafo · ${humanizar(m.tema)} ${m.version}${m.vigente ? "" : " (no vigente)"}`, 20 * esc, lienzo.height - 24 * esc);
  ctx.fillStyle = "#9aa6b8";
  ctx.font = `400 ${13 * esc}px Geist, sans-serif`;
  ctx.textAlign = "right";
  ctx.fillText("pipeline-decision-data · Hack to the Future 2026", lienzo.width - 20 * esc, lienzo.height - 24 * esc);
  const a = el("a", { href: lienzo.toDataURL("image/png"), download: `grafo-${m.version}-${m.tema}.png` });
  a.click();
}

/* ---------- Arranque ---------- */

$("cerrar-detalle").addEventListener("click", deseleccionar);
$("recorrer-vacios").addEventListener("click", () => (estado.paso >= 0 ? (salirDelRecorrido(), deseleccionar()) : recorrer(1)));
$("vacio-anterior").addEventListener("click", () => recorrer(-1));
$("vacio-siguiente").addEventListener("click", () => recorrer(1));
$("descargar").addEventListener("click", descargar);
addEventListener("keydown", (e) => {
  if (e.target.matches("input, select")) return;
  if (e.key === "Escape") { salirDelRecorrido(); deseleccionar(); }
  if (estado.paso >= 0 && e.key === "ArrowRight") recorrer(1);
  if (estado.paso >= 0 && e.key === "ArrowLeft") recorrer(-1);
});
buscar();
iniciar();
