#!/usr/bin/env python3
"""Pipeline de Clasificación 100% Local y Offline con llama-cpp-python.

No requiere API keys, no usa servicios externos ni envía datos a la nube.
Usa cuantización GGUF en tu procesador/GPU local.
Garantiza Structured Outputs en formato JSON y checkpointing automático.
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd

# Importamos utilidades de taxonomía del proyecto
sys.path.append(str(Path(__file__).resolve().parent))
from taxonomia import TAXONOMIAS_POR_TEMA, TipoCausaRaiz, AlcanceGeografico, EstadoMadurezSolucion
from version import carpeta_resultados

try:
    from llama_cpp import Llama
except ImportError:
    print("ERROR: No se encontró 'llama_cpp'. Instálalo con: pip install llama-cpp-python")
    sys.exit(1)


CATEGORIAS_DETALLADAS = {
    "residuos": {
        "problemas": """- BARRERAS_DE_MERCADO_Y_ECONOMICAS: Impuestos al plástico, aranceles, trabas aduaneras, costos de reciclaje, quejas de la industria.
- ESTANCAMIENTO_SEPARACION_Y_RECICLAJE: Pérdida de velocidad en reciclaje, estancamiento de cuotas, baja recolección, falta de separación.
- CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS: Residuos plásticos en el entorno, microplásticos, basura marina o en ríos.
- COLAPSO_Y_SATURACION_DISPOSICION_FINAL: Basurales a cielo abierto, microbasurales, vertederos o rellenos saturados.
- FALLA_REGULATORIA_Y_FISCALIZACION: Falta de leyes o controles, vacíos normativos, falta de fiscalización.
- DESPERDICIO_ALIMENTARIO_Y_ORGANICOS: Desperdicio de comida, biomasa vegetal sin aprovechar.
- GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE: Chatarra electrónica, pilas, baterías, residuos industriales peligrosos.
- CONFLICTO_TERRITORIAL_Y_LABORAL: Huelgas de recolectores, paros sindicales, protestas vecinales por radicación de plantas.
- EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES: Líquidos lixiviados de basurales, vertidos químicos no tratados.
- OTRO_PROBLEMA_RESIDUOS: Cualquier otro problema ambiental del sector.""",
        "soluciones": """- VALORIZACION_ENERGETICA_BIOGAS: Generación de hidrógeno con residuos (waste-to-hydrogen), biogás, energía a partir de basura.
- UPCYCLING_Y_VALORIZACION_MATERIAL: Tecnologías de depolimerización, reciclaje químico o mecánico, nuevos materiales y durmientes plásticos.
- MODELOS_CIRCULARES_Y_REUTILIZACION: Cajas reutilizables (Mehrweg), botellas retornables, modelos de refill y retorno.
- LOGISTICA_INVERSA_Y_RECOLECCION_INTELIGENTE: Puntos verdes, sensores en contenedores, apps de recolección y logística inversa.
- ECO_DISENO_Y_BIOMATERIALES: Envases monomaterial, bioplásticos compostables, diseño para reciclabilidad.
- COMPOSTAJE_Y_BIOTRANSFORMACION: Plantas de compostaje, lombricultura, biofertilizantes a partir de orgánicos.
- TRAZABILIDAD_DIGITAL_Y_SOFTWARE: Plataformas SaaS, pasaportes digitales de producto, blockchain ambiental.
- OTRA_SOLUCION_RESIDUOS: Cualquier otra tecnología o proyecto sustentable."""
    }
}


def armar_prompt_sistema(tema: str = "residuos") -> str:
    config_tema = TAXONOMIAS_POR_TEMA.get(tema, TAXONOMIAS_POR_TEMA["residuos"])
    lista_subcat = config_tema["subcategorias"]
    cats_tema = CATEGORIAS_DETALLADAS.get(tema, CATEGORIAS_DETALLADAS["residuos"])

    return f"""Eres un analista ambiental senior enfocado en {tema.upper()}.
Analiza la noticia y extrae la información en un JSON estructurado en ESPAÑOL.

REGLAS DE IDENTIFICACIÓN:
1. DETERMINA EL TIPO DE NOTICIA:
   - Si relata un daño, reclamo, impuesto gravoso, traba económica, basural o contaminación -> "tipo_registro": "PROBLEMATICA"
   - Si relata un nuevo proyecto, tecnología, investigación, planta de tratamiento, hidrógeno o iniciativa circular -> "tipo_registro": "SOLUCION"
   - Si NO trata sobre {tema} o medio ambiente (ej. deportes, farándula, política partidaria) -> responde ÚNICAMENTE: {{}}

2. CATEGORÍAS DE PROBLEMÁTICA DISPONIBLES:
{cats_tema["problemas"]}

3. CATEGORÍAS DE SOLUCIÓN DISPONIBLES:
{cats_tema["soluciones"]}

FORMATO DE SALIDA (JSON ESTRICTO):
{{
  "tipo_registro": "PROBLEMATICA" o "SOLUCION",
  "categoria": "Nombre exacto de la categoría elegida de las listas anteriores",
  "titulo_sintetico": "Frase concisa traducida y redactada en español",
  "descripcion": "Resumen conciso de 1-2 oraciones traducido al español",
  "causas_raiz": ["1 o 2 causas del problema si aplica"],
  "afectados_o_actores": ["actores, empresas o municipios clave"],
  "nombre_solucion": "Nombre del proyecto o tecnología si es solución (o null)",
  "quien_impulsa": "Empresa o entidad que impulsa la iniciativa si aplica",
  "tipo_problema_objetivo": "Qué categoría de problema mitiga si es solución",
  "metadatos": {{
    "subcategoria": "Uno de {lista_subcat}",
    "alcance_geografico": "Uno de {[e.value for e in AlcanceGeografico]}",
    "ubicacion_especifica": "Ciudad, provincia o país"
  }}
}}
No repitas valores. Devuelve solo el objeto JSON."""


def a_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    s = str(val).strip()
    return s if s else None


def a_lista_str(val: Any) -> str:
    if not val:
        return ""
    if isinstance(val, list):
        return "; ".join(str(x) for x in val if x)
    if isinstance(val, dict):
        return "; ".join(f"{k}: {v}" for k, v in val.items())
    return str(val)


def procesar_nota_con_llamacpp(llm: Llama, prompt_sistema: str, row: Dict[str, Any], tema: str) -> Optional[Dict[str, Any]]:
    texto_usuario = (
        f"MEDIO: {row.get('fuente', '')}\n"
        f"FECHA: {row.get('fecha', '')}\n"
        f"TÍTULO: {row.get('titulo', '')}\n"
        f"BAJADA: {row.get('bajada', '')}\n"
        f"CUERPO:\n{str(row.get('cuerpo_limpio', ''))[:1200]}"
    )

    try:
        salida = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Analiza esta nota y devuelve el JSON:\n\n{texto_usuario}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            repeat_penalty=1.18,
            max_tokens=650
        )

        txt = salida["choices"][0]["message"]["content"].strip()
        if txt in ("{}", "", "{ }", "[]"):
            return None

        idx_brace = txt.find('{')
        if idx_brace == -1:
            return None

        str_json = txt[idx_brace:]
        try:
            datos = json.loads(str_json)
        except Exception:
            try:
                import json_repair
                datos = json_repair.loads(str_json)
            except Exception:
                return None
        if not datos or not isinstance(datos, dict):
            return None

        # Soporte para formato unificado (tipo_registro) o anidado legado
        tipo_reg = str(datos.get("tipo_registro", "")).upper()
        categoria = datos.get("categoria")

        es_prob = False
        es_sol = False
        tipo_prob = None
        tit_prob = None
        desc_prob = None
        causas_str = ""
        afectados_str = ""
        magnitud_str = None

        tipo_sol = None
        nom_sol = None
        desc_sol = None
        quien_impulsa = None
        obj_sol = None

        meta = datos.get("metadatos") or {}

        if "PROBLEM" in tipo_reg:
            es_prob = True
            tipo_prob = a_str(categoria or datos.get("tipo_problema"))
            tit_prob = a_str(datos.get("titulo_sintetico") or row.get("titulo"))
            desc_prob = a_str(datos.get("descripcion"))
            causas_str = a_lista_str(datos.get("causas_raiz"))
            afectados_str = a_lista_str(datos.get("afectados_o_actores"))
        elif "SOLUC" in tipo_reg:
            es_sol = True
            tipo_sol = a_str(categoria or datos.get("tipo_solucion"))
            nom_sol = a_str(datos.get("nombre_solucion") or datos.get("titulo_sintetico") or row.get("titulo"))
            desc_sol = a_str(datos.get("descripcion"))
            quien_impulsa = a_lista_str(datos.get("quien_impulsa") or datos.get("afectados_o_actores"))
            obj_sol = a_str(datos.get("tipo_problema_objetivo"))
        elif datos.get("problematica") or datos.get("solucion"):
            prob = datos.get("problematica") or {}
            sol = datos.get("solucion") or {}
            if prob:
                es_prob = True
                tipo_prob = a_str(prob.get("tipo_problema"))
                tit_prob = a_str(prob.get("titulo_sintetico"))
                desc_prob = a_str(prob.get("descripcion"))
                causas_str = a_lista_str(prob.get("causas_raiz"))
                afectados_str = a_lista_str(prob.get("afectados_o_actores"))
                magnitud_str = a_str(prob.get("magnitud_o_cifras"))
            if sol:
                es_sol = True
                tipo_sol = a_str(sol.get("tipo_solucion"))
                nom_sol = a_str(sol.get("nombre_solucion_o_tecnologia"))
                desc_sol = a_str(sol.get("descripcion"))
                quien_impulsa = a_str(sol.get("quien_la_impulsa"))
                obj_sol = a_str(sol.get("tipo_problema_objetivo"))
        else:
            return None

        if not es_prob and not es_sol:
            return None

        embed_prob = f"TRACK: {tema.upper()}. PROBLEMA: {tipo_prob}. {tit_prob}. CAUSAS: {causas_str}" if es_prob else None
        embed_sol = f"TRACK: {tema.upper()}. SOLUCION: {tipo_sol}. {nom_sol}. RESUELVE: {obj_sol}" if es_sol else None

        return {
            "id_original": a_str(row.get("id")),
            "tema": tema,
            "fuente": a_str(meta.get("fuente_medio") or row.get("fuente")),
            "url": a_str(row.get("url")),
            "fecha": a_str(meta.get("fecha_publicacion") or row.get("fecha")),
            "es_problema": es_prob,
            "tipo_problema": tipo_prob,
            "titulo_problema": tit_prob,
            "descripcion_problema": desc_prob,
            "causas_raiz": causas_str,
            "afectados": afectados_str,
            "magnitud": magnitud_str,
            "es_solucion": es_sol,
            "tipo_solucion": tipo_sol,
            "nombre_solucion": nom_sol,
            "quien_impulsa": quien_impulsa,
            "descripcion_solucion": desc_sol,
            "tipo_problema_objetivo": obj_sol,
            "detalle_problema_objetivo": None,
            "subcategoria": a_str(meta.get("subcategoria")),
            "alcance_geo": a_str(meta.get("alcance_geografico")),
            "ubicacion": a_str(meta.get("ubicacion_especifica")),
            "texto_embedding_problema": embed_prob,
            "texto_embedding_solucion": embed_sol
        }
    except Exception as e:
        print(f"  [AVISO] Error al procesar nota {row.get('url', 'S/URL')[:50]}...: {e}")
        return None


def ejecutar_pipeline_llamacpp(
    tema: str = "residuos",
    limite: Optional[int] = None,
    modelo_path: Optional[str] = None,
    repo_id: str = "Qwen/Qwen2.5-3B-Instruct-GGUF",
    filename: str = "*q4_k_m.gguf",
    n_ctx: int = 3072,
    n_threads: Optional[int] = None,
    checkpoint_cada: int = 25
):
    ruta_input = carpeta_resultados(tema) / f"{tema}_listo_para_kaggle.parquet"

    if not ruta_input.exists():
        print(f"ERROR: No se encontró el dataset empaquetado en:\n{ruta_input}")
        print(f"Ejecuta primero: python scripts/clasificacion/empaquetar.py --tema {tema}")
        return

    threads = n_threads or max(1, (os.cpu_count() or 4) - 2)

    print("=" * 80)
    print(f"PIPELINE LOCAL CON LLAMA-CPP (OFFLINE / SIN API KEYS) · TRACK: {tema.upper()}")
    print("=" * 80)
    print(f"Hilos de CPU asignados: {threads} | Ventana de contexto: {n_ctx} tokens")

    # Cargar el modelo
    if modelo_path and Path(modelo_path).exists():
        print(f"Cargando modelo GGUF desde archivo local: {modelo_path}")
        llm = Llama(
            model_path=str(modelo_path),
            n_ctx=n_ctx,
            n_threads=threads,
            verbose=False
        )
    else:
        print(f"Cargando/descargando modelo desde Hugging Face: {repo_id} ({filename})...")
        llm = Llama.from_pretrained(
            repo_id=repo_id,
            filename=filename,
            n_ctx=n_ctx,
            n_threads=threads,
            verbose=False
        )
    print("[OK] Modelo local cargado y listo para inferencia.\n")

    prompt_sistema = armar_prompt_sistema(tema)

    print(f"Cargando dataset desde: {ruta_input}")
    df = pd.read_parquet(ruta_input)
    total_total = len(df)

    if limite:
        df = df.head(limite)
        print(f"Procesando muestra limitada a {len(df)} notas (de {total_total} totales)...")
    else:
        print(f"Procesando el dataset completo ({len(df)} notas)...")

    # Carpetas de salida y reanudación
    dir_salida = carpeta_resultados(tema)
    dir_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = dir_salida / f"{tema}_clasificado.parquet"
    ruta_checkpoint = dir_salida / f"{tema}_checkpoint.parquet"

    # Reanudación desde checkpoint
    ids_ya_procesados = set()
    procesados = []
    if ruta_checkpoint.exists():
        try:
            df_prev = pd.read_parquet(ruta_checkpoint)
            procesados = df_prev.to_dict(orient="records")
            ids_ya_procesados = {str(r.get("id_original")) for r in procesados if r.get("id_original")}
            print(f"--> Reanudando desde checkpoint: {len(procesados)} notas ya clasificadas previamente.")
        except Exception:
            pass

    filas_a_procesar = [r for r in df.to_dict(orient="records") if str(r.get("id")) not in ids_ya_procesados]
    print(f"Notas pendientes a procesar en esta corrida: {len(filas_a_procesar)}")

    inicio_tiempo = time.time()

    for idx, row in enumerate(filas_a_procesar, 1):
        res = procesar_nota_con_llamacpp(llm, prompt_sistema, row, tema)
        if res:
            procesados.append(res)
            if limite and limite <= 50:
                tipo = res.get('tipo_problema') or res.get('tipo_solucion')
                etiqueta = "Problema" if res.get('es_problema') else "Solucion"
                print(f"[{idx}/{len(filas_a_procesar)}] [OK] [{etiqueta}] {tipo} - {str(row.get('titulo', ''))[:55]}...", flush=True)
        else:
            if limite and limite <= 50:
                print(f"[{idx}/{len(filas_a_procesar)}] [-] Descartado (No relevante / Ruido) - {str(row.get('titulo', ''))[:55]}...", flush=True)

        if idx % 5 == 0 or idx == len(filas_a_procesar):
            ritmo = idx / (time.time() - inicio_tiempo)
            print(f"--- Progreso: [{idx}/{len(filas_a_procesar)}] ({idx/len(filas_a_procesar):.1%}) | Clasificados: {len(procesados)} | {ritmo*60:.0f} notas/min ---", flush=True)

        # Guardar checkpoint periódico
        if len(procesados) > 0 and idx % checkpoint_cada == 0:
            df_ckpt = pd.DataFrame(procesados)
            for c in df_ckpt.select_dtypes(include=["object"]).columns:
                df_ckpt[c] = df_ckpt[c].apply(lambda x: None if x is None else str(x))
            df_ckpt.to_parquet(ruta_checkpoint, index=False)

    # Guardado final
    df_final = pd.DataFrame(procesados)
    for c in df_final.select_dtypes(include=["object"]).columns:
        df_final[c] = df_final[c].apply(lambda x: None if x is None else str(x))
    df_final.to_parquet(ruta_salida, index=False)

    tiempo_total = time.time() - inicio_tiempo
    print("\n" + "=" * 80)
    print(f"¡PROCESO LOCAL COMPLETADO EN {tiempo_total/60:.2f} MINUTOS!")
    print(f"Archivo final guardado en: {ruta_salida}")
    print(f"Total registros clasificados: {len(df_final)}")
    if len(df_final) > 0:
        print("\nDistribución de Problemáticas:")
        print(df_final["tipo_problema"].value_counts().to_string())
        print("\nDistribución de Soluciones:")
        print(df_final["tipo_solucion"].value_counts().to_string())
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clasificador 100% local con llama-cpp-python.")
    parser.add_argument("--tema", type=str, default="residuos", help="Temática (residuos, etc.)")
    parser.add_argument("--limite", type=int, default=None, help="Límite de notas a procesar (ej. 30 para prueba)")
    parser.add_argument("--modelo-path", type=str, default=None, help="Ruta directa a un archivo .gguf local")
    parser.add_argument("--repo-id", type=str, default="Qwen/Qwen2.5-3B-Instruct-GGUF", help="Repositorio Hugging Face del modelo GGUF (ej. Qwen/Qwen2.5-3B-Instruct-GGUF o Qwen/Qwen2.5-1.5B-Instruct-GGUF)")
    parser.add_argument("--filename", type=str, default="*q4_k_m.gguf", help="Patrón del archivo GGUF")
    parser.add_argument("--ctx", type=int, default=3072, help="Tamaño de contexto")
    parser.add_argument("--threads", type=int, default=None, help="Hilos de CPU")
    parser.add_argument("--checkpoint-cada", type=int, default=25, help="Frecuencia de checkpoints")
    args = parser.parse_args()

    ejecutar_pipeline_llamacpp(
        tema=args.tema,
        limite=args.limite,
        modelo_path=args.modelo_path,
        repo_id=args.repo_id,
        filename=args.filename,
        n_ctx=args.ctx,
        n_threads=args.threads,
        checkpoint_cada=args.checkpoint_cada
    )
