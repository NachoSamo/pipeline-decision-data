"""Clasificación v2 de movilidad con vLLM: una copia del modelo por GPU, salida JSON guiada.

Cascada en dos etapas:
1. Relevancia, en todas las notas: el modelo elige un `motivo` de una lista cerrada.
   La nota es relevante si el motivo es `problema_o_solucion_concreta`.
2. Clasificación, solo en las relevantes: problema en una oración, solución, tipo,
   categorías (listas cerradas de etiquetado/config.js) y ubicación.

Cada etapa lanza un proceso por GPU (CUDA_VISIBLE_DEVICES), y cada proceso clasifica su mitad
de las notas en tandas, con un checkpoint en Parquet por tanda. Si se corta, al relanzar
saltea los id ya hechos. Las reglas salen de etiquetado/guia-movilidad.md.

Local (sin GPU):
    python scripts/clasificacion/clasificar_vllm.py --selfcheck
    python scripts/clasificacion/clasificar_vllm.py --armar-ejemplos
En Kaggle (ver notebooks/kaggle_movilidad_v2.ipynb):
    python clasificar_vllm.py --entradas A.parquet B.parquet --salida /kaggle/working/... [--ids ref.json]
"""

import argparse
import json
import os
import subprocess
import sys
import time
import zlib
from datetime import datetime
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
MODELO = "Qwen/Qwen2.5-7B-Instruct-AWQ"
EJEMPLOS = AQUI / "ejemplos_movilidad.json"
MAX_CUERPO = 2000
TANDA = 500

# Copias de etiquetado/config.js y de los motivos de etiquetado/calibrar.py: el selfcheck verifica que coincidan.
CATEGORIAS_PROBLEMA = [
    "CONGESTION_Y_DEMORAS", "EMISIONES_Y_FLOTA_OBSOLETA", "DEFICIT_TRANSPORTE_PUBLICO",
    "FALTA_INFRAESTRUCTURA_CICLISTA_PEATONAL", "OTRO_PROBLEMA_MOVILIDAD",
]
CATEGORIAS_SOLUCION = [
    "ELECTROMOVILIDAD_Y_BUSES_ELECTRICOS", "INFRAESTRUCTURA_BICICLETAS_Y_PEATONAL",
    "SISTEMAS_INTELIGENTES_TRANSITO_ITS", "REDES_FERROVIARIAS_Y_SUBTE", "OTRA_SOLUCION_MOVILIDAD",
]
RELEVANTE = "problema_o_solucion_concreta"
MOTIVOS = [
    RELEVANTE, "movilidad_de_pasada", "seguridad_vial", "politica_o_economia_sin_medida",
    "otro_track_ambiental", "otro_tema", "nota_de_color", "gestion_sin_problema_ni_solucion",
]


def texto_o_nulo(max_len):
    return {"anyOf": [{"type": "string", "maxLength": max_len}, {"type": "null"}]}


ESQUEMA_1 = {
    "type": "object",
    "properties": {"motivo": {"enum": MOTIVOS}},
    "required": ["motivo"],
    "additionalProperties": False,
}
# El orden importa: el modelo escribe primero el problema y la solución, y después elige tipo y categorías.
ESQUEMA_2 = {
    "type": "object",
    "properties": {
        "problema": {"type": "string", "maxLength": 300},
        "solucion": texto_o_nulo(300),
        "tipo": {"enum": ["problema", "solucion", "ambas"]},
        "categorias_problema": {"type": "array", "items": {"enum": CATEGORIAS_PROBLEMA}, "maxItems": 3},
        "categorias_solucion": {"type": "array", "items": {"enum": CATEGORIAS_SOLUCION}, "maxItems": 3},
        "categoria_otra": texto_o_nulo(120),
        "ubicacion": texto_o_nulo(80),
    },
    "required": ["problema", "solucion", "tipo", "categorias_problema", "categorias_solucion",
                 "categoria_otra", "ubicacion"],
    "additionalProperties": False,
}
ETAPAS = {1: (ESQUEMA_1, 20), 2: (ESQUEMA_2, 400)}  # esquema y max_tokens

GUIA = """Analizás notas periodísticas para un estudio sobre movilidad sustentable. El track es el transporte
de personas o de cargas: vehículos, transporte público, tránsito e infraestructura vial, ferroviaria,
ciclista o peatonal. El idioma de la nota no importa.

Una nota es relevante solo si pasa estas tres preguntas, en orden:
1. ¿El tema central es la movilidad? Si aparece solo de pasada → movilidad_de_pasada.
2. ¿Es seguridad vial? Choques, atropellos, consejos de manejo o sillas infantiles → seguridad_vial,
   aunque sea educativa.
3. ¿Describe un problema concreto de movilidad o una solución concreta (producto, tecnología, obra,
   servicio o programa)? Si no plantea ninguno de los dos → gestion_sin_problema_ni_solucion.
Otros descartes: disputa política, crítica o declaración sin una medida de transporte concreta, o
economía y finanzas aunque digan "sustentable" → politica_o_economia_sin_medida. Otro tema ambiental
(residuos, biodiversidad, energía sin transporte) → otro_track_ambiental. Otro tema → otro_tema. Nota de
color o viral con el tránsito de escenario → nota_de_color.
Entra una obra, un servicio o una medida de transporte concreta aunque la impulse un gobierno.
Ante la duda, la nota NO es relevante."""

INSTRUCCION = {
    1: "Respondé solo el JSON con el motivo. Si la nota es relevante, el motivo es " + RELEVANTE + ".",
    2: f"""La nota ya es relevante. Respondé solo el JSON, en español:
- problema: una oración con el problema de movilidad que plantea la nota o, si presenta una solución,
  el problema que esa solución ataca. Genérica y comparable entre notas, sin nombres de medios.
- solucion: una oración con la solución concreta que presenta, o null si no presenta ninguna.
- tipo: problema (describe un problema sin solución concreta), solucion (presenta una solución; el
  problema es solo contexto) o ambas (un problema concreto y una solución que apunta a ese problema).
- categorias_problema: {CATEGORIAS_PROBLEMA}
- categorias_solucion: {CATEGORIAS_SOLUCION}
  Marcá todas las que la nota describe, no las que menciona de pasada.
- categoria_otra: texto breve si usaste una categoría OTRO/OTRA; si no, null.
- ubicacion: ciudad, provincia o país donde ocurre, o null si no se dice.""",
}


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def limpio(valor):
    return "" if valor is None or (isinstance(valor, float) and pd.isna(valor)) else str(valor).strip()


def texto_nota(nota, max_cuerpo=MAX_CUERPO):
    return (f"TÍTULO: {limpio(nota.get('titulo'))}\nBAJADA: {limpio(nota.get('bajada'))}\n"
            f"CUERPO: {limpio(nota.get('body'))[:max_cuerpo]}")


def prefijo(etapa, ejemplos):
    """Parte fija del prompt: igual para todas las notas, así vLLM la reusa con prefix caching."""
    partes = [GUIA, INSTRUCCION[etapa], "EJEMPLOS:"]
    for e in ejemplos[str(etapa)]:
        partes.append(f"{texto_nota(e, 400)}\nRESPUESTA: {json.dumps(e['respuesta'], ensure_ascii=False)}")
    return "\n\n".join(partes)


def conversacion(sistema, nota):
    return [{"role": "system", "content": sistema}, {"role": "user", "content": texto_nota(nota)}]


def mitad(id_, gpu, gpus):
    """Partición estable por id (no depende del orden ni de la semilla de Python)."""
    return zlib.crc32(str(id_).encode()) % gpus == gpu


def parsear(etapa, txt):
    """Devuelve (dict, error). Con salida guiada no debería fallar; si falla, queda registrado."""
    try:
        datos = json.loads(txt)
    except (json.JSONDecodeError, TypeError):
        return {}, f"JSON inválido: {str(txt)[:80]}"
    if etapa == 1:
        return {"motivo": datos.get("motivo"), "relevante": datos.get("motivo") == RELEVANTE}, None
    return {k: datos.get(k) for k in ESQUEMA_2["properties"]}, None


# ---------- notas y checkpoints ----------

def cargar_notas(entradas, ids=None, limite=None):
    """Une los Parquet de entrada con una columna `dataset` y sin id repetidos (gana el primero)."""
    dfs = []
    for ruta in entradas:
        df = pd.read_parquet(ruta)
        df["dataset"] = "soluciones" if "soluciones" in Path(ruta).stem else "problematicas"
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True).drop_duplicates("id")
    if ids is not None:
        df = df[df["id"].isin(ids)]
    return df.head(limite) if limite else df


def leer_ids(ruta):
    d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return {x["id"] for x in d.get("notas") or d.get("etiquetas")}


def leer_checkpoints(salida, etapa):
    archivos = sorted((Path(salida) / "checkpoints").glob(f"etapa{etapa}-*.parquet"))
    return pd.concat([pd.read_parquet(a) for a in archivos], ignore_index=True) if archivos else pd.DataFrame()


def pendientes(notas, salida, etapa, gpu, gpus):
    hechos = leer_checkpoints(salida, etapa)
    ids_hechos = set(hechos["id"]) if len(hechos) else set()
    mias = notas[notas["id"].map(lambda i: mitad(i, gpu, gpus))]
    return mias[~mias["id"].isin(ids_hechos)]


# ---------- vLLM (solo en GPU) ----------

def sampling(esquema, max_tokens):
    """SamplingParams con salida guiada. La API cambió de nombre entre versiones de vLLM."""
    from vllm import SamplingParams

    try:
        from vllm.sampling_params import StructuredOutputsParams

        return SamplingParams(temperature=0, max_tokens=max_tokens, structured_outputs=StructuredOutputsParams(json=esquema))
    except ImportError:
        from vllm.sampling_params import GuidedDecodingParams

        return SamplingParams(temperature=0, max_tokens=max_tokens, guided_decoding=GuidedDecodingParams(json=esquema))


def worker(args):
    from vllm import LLM

    gpu, etapa = args.gpu, args.etapa
    notas = cargar_notas(args.entradas, leer_ids(args.ids) if args.ids else None, args.limite)
    if etapa == 2:
        e1 = leer_checkpoints(args.salida, 1)
        notas = notas[notas["id"].isin(e1.loc[e1["relevante"] == True, "id"])]  # noqa: E712
    notas = pendientes(notas, args.salida, etapa, gpu, args.gpus)
    log(f"[GPU {gpu}] Etapa {etapa}: {len(notas)} notas pendientes")
    if notas.empty:
        return

    ejemplos = json.loads(Path(args.ejemplos).read_text(encoding="utf-8"))
    sistema = prefijo(etapa, ejemplos)
    params = sampling(*ETAPAS[etapa])
    llm = LLM(model=args.modelo, quantization="awq", dtype="half", max_model_len=4096,
              enable_prefix_caching=True, gpu_memory_utilization=0.90)
    carpeta = Path(args.salida) / "checkpoints"
    carpeta.mkdir(parents=True, exist_ok=True)

    filas = notas.to_dict("records")
    comienzo, hechas = time.monotonic(), 0
    for inicio in range(0, len(filas), args.tanda):
        tanda = filas[inicio:inicio + args.tanda]
        salidas = llm.chat([conversacion(sistema, n) for n in tanda], params, use_tqdm=False)
        registros = []
        for nota, salida in zip(tanda, salidas):
            datos, error = parsear(etapa, salida.outputs[0].text)
            registros.append({"id": nota["id"], **datos, "error": error})
        nombre = f"etapa{etapa}-gpu{gpu}-{int(time.time())}-{inicio:06d}.parquet"
        pd.DataFrame(registros).to_parquet(carpeta / nombre, index=False)
        hechas += len(tanda)
        ritmo = hechas / max(time.monotonic() - comienzo, 1) * 60
        log(f"[GPU {gpu}] Etapa {etapa}: {hechas} de {len(filas)} | {ritmo:.0f} notas/min | checkpoint {nombre}")


# ---------- orquestación ----------

def lanzar(args, etapa):
    """Un proceso por GPU; cada uno ve una sola placa."""
    procesos = []
    for gpu in range(args.gpus):
        cmd = [sys.executable, __file__, "--worker", "--gpu", str(gpu), "--etapa", str(etapa),
               "--salida", args.salida, "--ejemplos", args.ejemplos, "--modelo", args.modelo,
               "--gpus", str(args.gpus), "--tanda", str(args.tanda), "--entradas", *args.entradas]
        if args.ids:
            cmd += ["--ids", args.ids]
        if args.limite:
            cmd += ["--limite", str(args.limite)]
        procesos.append(subprocess.Popen(cmd, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)}))
    codigos = [p.wait() for p in procesos]
    if any(codigos):
        sys.exit(f"Etapa {etapa}: algún proceso falló (códigos {codigos}). Relanzar retoma desde los checkpoints.")


def unir(args):
    notas = cargar_notas(args.entradas, leer_ids(args.ids) if args.ids else None, args.limite)
    base = notas[["id", "dataset", "fuente", "alcance", "url", "fecha", "titulo"]]
    e1 = leer_checkpoints(args.salida, 1).drop_duplicates("id", keep="last").rename(columns={"error": "error_1"})
    e2 = leer_checkpoints(args.salida, 2)
    final = base.merge(e1, on="id", how="left")
    if len(e2):
        e2 = e2.drop_duplicates("id", keep="last").rename(columns={"error": "error_2"})
        final = final.merge(e2, on="id", how="left")
    ruta = Path(args.salida) / "movilidad_clasificado.parquet"
    final.to_parquet(ruta, index=False)
    rel = final["relevante"] == True  # noqa: E712
    log(f"Unido: {len(final)} notas, {int(rel.sum())} relevantes, {int(final['motivo'].isna().sum())} sin etapa 1")
    log(f"Motivos:\n{final['motivo'].value_counts().to_string()}")
    log(f"Guardado en {ruta}")


# ---------- ejemplos few-shot (local) ----------

# Notas del gold del equipo que van como ejemplos (por eso el gold no sirve para evaluar al modelo).
EJEMPLOS_GOLD = {
    "Triciclo movido a energia solar": RELEVANTE,
    "Un teleférico y un subte en La Plata": RELEVANTE,
    "Conheça startups do Hub Green Sampa": RELEVANTE,
    "Caos de tránsito en la autopista 9 de Julio Sur": "seguridad_vial",
    "El alcalde de Valladolid suspende": "politica_o_economia_sin_medida",
    "las líneas 30 y 34 pasan a formar parte": "gestion_sin_problema_ni_solucion",
    "El 70% de los últimos brotes epidémicos": "otro_track_ambiental",
    "llevaba años sin ver a su papá": "nota_de_color",
}


def armar_ejemplos():
    """Escribe ejemplos_movilidad.json con las notas del gold elegidas y su respuesta esperada."""
    gold = {e["id"]: e for e in json.loads((RAIZ / "etiquetado/reconciliacion/movilidad-gold.json")
                                          .read_text(encoding="utf-8"))["etiquetas"]}
    df = pd.read_parquet(RAIZ / "data" / "movilidad.parquet", columns=["id", "titulo", "bajada", "body"])
    df = df[df["id"].isin(gold)]
    salida = {"1": [], "2": []}
    for inicio, motivo in EJEMPLOS_GOLD.items():
        fila = df[df["titulo"].str.contains(inicio, regex=False)].iloc[0].to_dict()
        g = gold[fila["id"]]
        assert g["relevante"] == (motivo == RELEVANTE), inicio
        nota = {k: limpio(fila[k]) for k in ("titulo", "bajada")} | {"body": limpio(fila["body"])[:400]}
        salida["1"].append(nota | {"respuesta": {"motivo": motivo}})
        if g["relevante"]:
            resp = {k: g[k] for k in ("tipo", "categorias_problema", "categorias_solucion")}
            salida["2"].append(nota | {"respuesta": resp})
    EJEMPLOS.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"Escrito {EJEMPLOS.name}: {len(salida['1'])} ejemplos de etapa 1 y {len(salida['2'])} de etapa 2")


# ---------- selfcheck ----------

def selfcheck():
    sys.path.insert(0, str(RAIZ / "etiquetado"))
    from calibrar import MOTIVOS as MOTIVOS_REF, categorias

    probs, sols = categorias()
    assert set(CATEGORIAS_PROBLEMA) == probs and set(CATEGORIAS_SOLUCION) == sols, "categorías distintas de config.js"
    assert MOTIVOS == MOTIVOS_REF, "motivos distintos de etiquetado/calibrar.py"
    assert parsear(1, '{"motivo": "seguridad_vial"}') == ({"motivo": "seguridad_vial", "relevante": False}, None)
    assert parsear(1, '{"motivo": "' + RELEVANTE + '"}')[0]["relevante"] is True
    assert parsear(2, "{roto")[1].startswith("JSON inválido")
    ids = [f"https://x/{i}" for i in range(1000)]
    a, b = [sum(mitad(i, g, 2) for i in ids) for g in (0, 1)]
    assert a + b == 1000 and 400 < a < 600, (a, b)
    ejemplos = json.loads(EJEMPLOS.read_text(encoding="utf-8"))
    assert len(ejemplos["1"]) == len(EJEMPLOS_GOLD) and len(ejemplos["2"]) == 3
    for etapa in (1, 2):
        s = prefijo(etapa, ejemplos)
        c1, c2 = conversacion(s, {"titulo": "A"}), conversacion(s, {"titulo": "B"})
        assert c1[0] == c2[0] and c1[1] != c2[1], "el prefijo tiene que ser idéntico entre notas"
    for e in ejemplos["2"]:
        r = e["respuesta"]
        assert set(r["categorias_problema"]) <= probs and set(r["categorias_solucion"]) <= sols
    log("selfcheck ok")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--armar-ejemplos", action="store_true", help="escribe ejemplos_movilidad.json desde el gold")
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--gpu", type=int, default=0, help=argparse.SUPPRESS)
    ap.add_argument("--etapa", type=int, choices=[1, 2], help="correr solo esa etapa (sin unir)")
    ap.add_argument("--unir", action="store_true", help="solo unir los checkpoints")
    ap.add_argument("--entradas", nargs="+", default=[str(RAIZ / "data/v1-samo-movilidad/movilidad_filtrado.parquet"),
                                                     str(RAIZ / "data/v1-samo-movilidad/movilidad_soluciones_filtrado.parquet")])
    ap.add_argument("--salida", default=str(RAIZ / "data/resultados/v2-movilidad"))
    ap.add_argument("--ejemplos", default=str(EJEMPLOS))
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--ids", help="JSON con 'notas' o 'etiquetas' (id): clasifica solo esas, p. ej. la referencia")
    ap.add_argument("--limite", type=int, help="clasifica solo las primeras N notas (prueba de velocidad)")
    ap.add_argument("--gpus", type=int, default=2)
    ap.add_argument("--tanda", type=int, default=TANDA)
    args = ap.parse_args()

    if args.selfcheck:
        selfcheck()
    elif args.armar_ejemplos:
        armar_ejemplos()
    elif args.worker:
        worker(args)
    elif args.unir:
        unir(args)
    elif args.etapa:
        lanzar(args, args.etapa)
    else:
        comienzo = time.monotonic()
        for etapa in (1, 2):
            log(f"Etapa {etapa} en {args.gpus} GPU")
            lanzar(args, etapa)
        unir(args)
        log(f"Tiempo total: {(time.monotonic() - comienzo) / 60:.1f} min")


if __name__ == "__main__":
    main()
