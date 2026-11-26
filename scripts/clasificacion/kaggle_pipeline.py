"""Kaggle Pipeline Modular: Inferencia Masiva Multi-GPU con Qwen 2.5 3B (4-bit NF4).

Optimizaciones implementadas:
1. Cuantización 4-bit (NF4 con bitsandbytes): 1.8 GB VRAM por tarjeta.
2. Multi-GPU paralelo (2x T4): Workers concurrentes con ThreadPoolExecutor.
3. Pre-filtrado heurístico modular en CPU: reducción del ~68% de ruido.
4. Resumen estructurado de alta densidad informativa (máx 30 palabras) con max_new_tokens=220.
"""

import os
import sys
import json
import glob
import re
import time
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any

# Dependencias ligeras sin conflictos
os.system("pip install -q pydantic accelerate bitsandbytes json-repair")

import torch
import pandas as pd
import numpy as np
import json_repair
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

TEMA_ACTUAL = os.environ.get("TEMA", "residuos").lower()
VERSION = "v1"  # Mantener igual que scripts/clasificacion/version.py

TAXONOMIAS = {
    "residuos": {
        "problemas": [
            "COLAPSO_Y_SATURACION_DISPOSICION_FINAL", "ESTANCAMIENTO_SEPARACION_Y_RECICLAJE",
            "CONFLICTO_TERRITORIAL_Y_LABORAL", "DESPERDICIO_ALIMENTARIO_Y_ORGANICOS",
            "CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS", "GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE",
            "BARRERAS_DE_MERCADO_Y_ECONOMICAS", "FALLA_REGULATORIA_Y_FISCALIZACION",
            "EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES", "OTRO_PROBLEMA_RESIDUOS"
        ],
        "soluciones": [
            "UPCYCLING_Y_VALORIZACION_MATERIAL", "VALORIZACION_ENERGETICA_BIOGAS",
            "MODELOS_CIRCULARES_Y_REUTILIZACION", "LOGISTICA_INVERSA_Y_RECOLECCION_INTELIGENTE",
            "ECO_DISENO_Y_BIOMATERIALES", "COMPOSTAJE_Y_BIOTRANSFORMACION",
            "TRAZABILIDAD_DIGITAL_Y_SOFTWARE", "OTRA_SOLUCION_RESIDUOS"
        ],
        "subcategorias": [
            "PLASTICOS_ENVASES", "ORGANICOS_ALIMENTOS", "ELECTRONICOS_BATERIAS_RAEE",
            "TEXTILES", "VIDRIO", "METALES_FERROSOS", "CONSTRUCCION_DEMOLICION_RCD",
            "EFLUENTES_LIXIVIADOS", "MIXTO_DOMICILIARIO", "NO_APLICA"
        ]
    },
    "biodiversidad": {
        "problemas": [
            "PERDIDA_HABITAT_Y_DEFORESTACION", "CAZA_Y_TRAFICO_DE_FAUNA",
            "ESPECIES_INVASORAS", "FRAGMENTACION_DE_CORREDORES",
            "CONTAMINACION_Y_EUTROFIZACION", "INCENDIOS_FORESTALES",
            "OTRO_PROBLEMA_BIODIVERSIDAD"
        ],
        "soluciones": [
            "RESTAURACION_Y_REFORESTACION", "AREAS_PROTEGIDAS_Y_CORREDORES",
            "CONTROL_DE_INVASORAS", "MONITOREO_SATELITAL_Y_BIOACUSTICA",
            "OTRA_SOLUCION_BIODIVERSIDAD"
        ],
        "subcategorias": ["FLORA_BOSQUES", "FAUNA_TERRESTRE", "HUMEDALES_AGUAS", "NO_APLICA"]
    },
    "movilidad": {
        "problemas": [
            "CONGESTION_Y_DEMORAS", "EMISIONES_Y_FLOTA_OBSOLETA",
            "DEFICIT_TRANSPORTE_PUBLICO", "FALTA_INFRAESTRUCTURA_CICLISTA_PEATONAL",
            "SINIESTRALIDAD_VIAL", "OTRO_PROBLEMA_MOVILIDAD"
        ],
        "soluciones": [
            "ELECTROMOVILIDAD_Y_BUSES_ELECTRICOS", "INFRAESTRUCTURA_BICICLETAS_Y_PEATONAL",
            "SISTEMAS_INTELIGENTES_TRANSITO_ITS", "REDES_FERROVIARIAS_Y_SUBTE",
            "OTRA_SOLUCION_MOVILIDAD"
        ],
        "subcategorias": ["TRANSPORTE_PUBLICO", "MICROMOVILIDAD", "VEHICULOS_PARTICULARES", "NO_APLICA"]
    }
}

RAICES_POR_TEMA = {
    "residuos": [
        "basur", "residu", "recicl", "verted", "lixiviad", "compost", "chatarra", "plástic", "plastic",
        "desecho", "relleno sanitar", "ecodiseñ", "ecodiseno", "economía circular", "economia circular",
        "recolecc", "cartoner", "desperdicio aliment", "durmiente", "envase", "botell"
    ],
    "biodiversidad": [
        "fauna", "flora", "especie", "bosque", "deforestac", "humedal", "extinción", "extincion",
        "reserva natural", "caza furtiva", "invasora", "hábitat", "habitat", "biodiversid", "selva",
        "parque nacional", "yaguaret", "avifauna", "anfibio"
    ],
    "movilidad": [
        "tránsito", "transito", "transporte", "colectivo", "tren", "bicisenda", "ciclovía", "ciclovia",
        "movilidad eléctric", "movilidad electric", "subte", "congestión", "congestion", "peatonal",
        "electromovilidad", "flota", "autobús", "autobus"
    ]
}

SECCIONES_RUIDO = {
    "deportes", "futbol", "fútbol", "primera c", "primera división", "copa de la liga",
    "espectaculos", "espectáculos", "cuarteteando", "fama", "show", "musica", "música",
    "cine y series", "horoscopo", "horóscopo", "policiales"
}
PATRON_DEPORTE = re.compile(r"\b(goles?|partidos?|director técnico|primer tiempo|segundo tiempo|tiro al arco|penales?)\b", re.IGNORECASE)

def filtrar_candidatos_tema(df: pd.DataFrame, tema: str) -> pd.DataFrame:
    """Pre-filtrado heurístico ultrarrápido parametrizado por tema (en memoria con CPU)."""
    raices = RAICES_POR_TEMA.get(tema, RAICES_POR_TEMA.get("residuos", []))
    patron_tema = re.compile(r"\b(" + "|".join(re.escape(r) for r in raices) + ")", re.IGNORECASE) if raices else None
    
    candidatos = []
    for fila in df.to_dict(orient="records"):
        seccion = str(fila.get("seccion") or "").strip().lower()
        if seccion in SECCIONES_RUIDO:
            continue
            
        titulo = str(fila.get("titulo") or "").strip()
        bajada = str(fila.get("bajada") or "").strip()
        cuerpo = str(fila.get("cuerpo_limpio") or fila.get("body") or fila.get("cuerpo") or "").strip()
        
        if len(cuerpo) < 150:
            continue
            
        if PATRON_DEPORTE.search(f"{titulo} {bajada}"):
            continue
            
        if patron_tema:
            texto_eval = f"{titulo} {bajada} {cuerpo[:400]}".lower()
            if not patron_tema.search(texto_eval):
                continue
                
        candidatos.append(fila)
        
    return pd.DataFrame(candidatos)

def armar_prompt_sistema(tema: str) -> str:
    config = TAXONOMIAS.get(tema, TAXONOMIAS["residuos"])
    return f"""Eres un analista ambiental experto en {tema.upper()}.
Analiza la nota y devuelve un JSON en ESPAÑOL.

REGLAS CRÍTICAS:
1. IDIOMA: Todo el texto generado DEBE estar en ESPAÑOL.
2. DESCARTE DE RUIDO: Si la nota NO trata genuinamente sobre {tema} o medio ambiente, responde ÚNICAMENTE: {{}}
3. REGISTROS VÁLIDOS: Devuelve un JSON estructurado con:
{{
  "tipo_registro": "PROBLEMATICA" o "SOLUCION",
  "categoria": "Una de las categorías permitidas",
  "titulo_sintetico": "Frase breve en español",
  "descripcion": "1 sola oración informativa y directa (máx 30 palabras) con qué ocurre, actores y lugar exacto",
  "causas_raiz": ["1 o 2 causas del problema si aplica"],
  "afectados_o_actores": ["comunidades, municipios o actores"],
  "nombre_solucion": "Nombre del proyecto o tecnología si es solución",
  "quien_impulsa": "Empresa o entidad que impulsa si es solución",
  "tipo_problema_objetivo": "Qué categoría de problema mitiga si es solución",
  "subcategoria": "Una de {config['subcategorias']}",
  "alcance_geografico": "CORDOBA_LOCAL, ARGENTINA_NACIONAL, LATAM_REGIONAL o INTERNACIONAL_GLOBAL",
  "ubicacion_especifica": "Ciudad, provincia o país"
}}
CATEGORÍAS DE PROBLEMAS: {config['problemas']}
CATEGORÍAS DE SOLUCIONES: {config['soluciones']}
Devuelve solo el objeto JSON."""

def a_str(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    s = str(val).strip()
    return s if s else None

def a_lista_str(val):
    if not val:
        return ""
    if isinstance(val, list):
        return "; ".join(str(x) for x in val if x)
    if isinstance(val, dict):
        return "; ".join(f"{k}: {v}" for k, v in val.items())
    return str(val)


def worker_inferencia(
    gpu_id: int,
    df_subset: pd.DataFrame,
    tema: str,
    model_id: str,
    bnb_config: BitsAndBytesConfig,
    tokenizer: AutoTokenizer,
    dir_salida: Path
) -> List[Dict[str, Any]]:
    """Worker dedicado que carga un modelo 4-bit en una GPU específica y procesa su partición."""
    device_str = f"cuda:{gpu_id}"
    torch.cuda.set_device(gpu_id)
    ruta_ckpt_gpu = dir_salida / f"{tema}_checkpoint_gpu{gpu_id}.parquet"
    prompt_sistema = armar_prompt_sistema(tema)
    TAM_LOTE = 16
    CHECKPOINT_CADA = 200

    print(f"[GPU {gpu_id}] Cargando copia 4-bit de {model_id} en {device_str}...")
    model_gpu = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map={"": f"cuda:{gpu_id}"},
        trust_remote_code=True
    )
    vram_gb = torch.cuda.memory_allocated(gpu_id) / (1024**3)
    print(f"[GPU {gpu_id}] ✅ Modelo listo. VRAM: {vram_gb:.2f} GB | Notas a procesar: {len(df_subset):,}")

    procesados_gpu = []
    t_inicio = time.time()
    total_notas = len(df_subset)

    for i in range(0, total_notas, TAM_LOTE):
        lote = df_subset.iloc[i : i + TAM_LOTE]
        mensajes_lote = []

        for _, row in lote.iterrows():
            cuerpo_texto = row.get("cuerpo_limpio") or row.get("body") or row.get("cuerpo") or ""
            texto_usuario = (
                f"MEDIO: {row.get('fuente', '')}\n"
                f"FECHA: {row.get('fecha', '')}\n"
                f"TÍTULO: {row.get('titulo', '')}\n"
                f"BAJADA: {row.get('bajada', '')}\n"
                f"CUERPO:\n{str(cuerpo_texto)[:500]}"
            )
            conversacion = [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_usuario}
            ]
            mensajes_lote.append(tokenizer.apply_chat_template(conversacion, tokenize=False, add_generation_prompt=True))

        try:
            entradas = tokenizer(mensajes_lote, return_tensors="pt", padding=True, truncation=True, max_length=950).to(device_str)

            with torch.no_grad():
                salidas = model_gpu.generate(
                    **entradas,
                    max_new_tokens=220,
                    temperature=0.1,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id
                )

            long_entrada = entradas["input_ids"].shape[1]
            respuestas_texto = [tokenizer.decode(out_ids[long_entrada:], skip_special_tokens=True).strip() for out_ids in salidas]
        except Exception as e_gen:
            print(f"[GPU {gpu_id}] Advertencia en lote {i}: {e_gen}")
            continue

        for (_, row), txt in zip(lote.iterrows(), respuestas_texto):
            if txt in ("{}", "", "{ }", "[]"):
                continue

            idx_brace = txt.find('{')
            if idx_brace == -1:
                continue

            str_json = txt[idx_brace:]
            try:
                datos = json.loads(str_json)
            except Exception:
                try:
                    datos = json_repair.loads(str_json)
                except Exception:
                    continue

            if not datos or not isinstance(datos, dict):
                continue

            tipo_reg = str(datos.get("tipo_registro", "")).upper()
            categoria = datos.get("categoria")
            meta = datos.get("metadatos") or {}

            es_prob = "PROBLEM" in tipo_reg or bool(datos.get("problematica"))
            es_sol = "SOLUC" in tipo_reg or bool(datos.get("solucion"))

            if not es_prob and not es_sol:
                continue

            tipo_prob = a_str(categoria or datos.get("tipo_problema")) if es_prob else None
            tit_prob = a_str(datos.get("titulo_sintetico") or row.get("titulo")) if es_prob else None
            desc_prob = a_str(datos.get("descripcion")) if es_prob else None
            causas_str = a_lista_str(datos.get("causas_raiz")) if es_prob else ""
            afectados_str = a_lista_str(datos.get("afectados_o_actores")) if es_prob else ""

            tipo_sol = a_str(categoria or datos.get("tipo_solucion")) if es_sol else None
            nom_sol = a_str(datos.get("nombre_solucion") or datos.get("titulo_sintetico") or row.get("titulo")) if es_sol else None
            desc_sol = a_str(datos.get("descripcion")) if es_sol else None
            quien_imp = a_lista_str(datos.get("quien_impulsa") or datos.get("afectados_o_actores")) if es_sol else None
            obj_sol = a_str(datos.get("tipo_problema_objetivo")) if es_sol else None

            embed_prob = f"TRACK: {tema.upper()}. PROBLEMA: {tipo_prob}. {tit_prob}. CAUSAS: {causas_str}" if es_prob else None
            embed_sol = f"TRACK: {tema.upper()}. SOLUCION: {tipo_sol}. {nom_sol}. RESUELVE: {obj_sol}" if es_sol else None

            procesados_gpu.append({
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
                "magnitud": None,
                "es_solucion": es_sol,
                "tipo_solucion": tipo_sol,
                "nombre_solucion": nom_sol,
                "quien_impulsa": quien_imp,
                "descripcion_solucion": desc_sol,
                "tipo_problema_objetivo": obj_sol,
                "detalle_problema_objetivo": None,
                "subcategoria": a_str(meta.get("subcategoria")),
                "alcance_geo": a_str(meta.get("alcance_geografico")),
                "ubicacion": a_str(meta.get("ubicacion_especifica")),
                "texto_embedding_problema": embed_prob,
                "texto_embedding_solucion": embed_sol
            })

        paso_actual = min(i + TAM_LOTE, total_notas)
        if (i // TAM_LOTE) % 5 == 0 or paso_actual == total_notas:
            ritmo = paso_actual / max(time.time() - t_inicio, 1)
            print(f"[GPU {gpu_id}] Progreso: {paso_actual}/{total_notas} ({paso_actual/total_notas:.1%}) | Clasificados: {len(procesados_gpu)} | Ritmo: {ritmo*60:.0f} notas/min")

        if len(procesados_gpu) > 0 and (i // TAM_LOTE) % (CHECKPOINT_CADA // TAM_LOTE) == 0:
            df_ckpt = pd.DataFrame(procesados_gpu)
            for c in df_ckpt.select_dtypes(include=["object"]).columns:
                df_ckpt[c] = df_ckpt[c].apply(lambda x: None if x is None else str(x))
            df_ckpt.to_parquet(ruta_ckpt_gpu, index=False)
            print(f"[GPU {gpu_id}] --> Checkpoint guardado en {ruta_ckpt_gpu}")

    print(f"[GPU {gpu_id}] 🎉 Tarea finalizada. Total clasificados: {len(procesados_gpu):,}")
    return procesados_gpu


def ejecutar_pipeline_kaggle(tema: str = TEMA_ACTUAL):
    print("=" * 80)
    print(f"🚀 INICIANDO PIPELINE MULTI-GPU HUGGING FACE EN KAGGLE (TEMA: {tema.upper()})")
    print("=" * 80)

    patron = f"/kaggle/input/**/{tema}*.parquet"
    archivos = glob.glob(patron, recursive=True)
    if not archivos:
        archivos = glob.glob("/kaggle/input/**/*.parquet", recursive=True)

    if not archivos:
        raise FileNotFoundError("No se encontró ningún archivo Parquet en /kaggle/input/. Revisa haber añadido el dataset.")

    ruta_entrada = archivos[0]
    print(f"📂 Cargando archivo: {ruta_entrada}")
    df_raw = pd.read_parquet(ruta_entrada)
    print(f"Total notas brutas en el dataset: {len(df_raw):,}")

    print(f"⚡ Aplicando pre-filtrado heurístico modular para '{tema}'...")
    t0 = time.time()
    df = filtrar_candidatos_tema(df_raw, tema=tema)
    t1 = time.time()
    print(f"✅ Filtrado completado en {t1 - t0:.2f}s: {len(df):,} notas candidatas ({len(df)/len(df_raw):.1%} del total)")

    num_gpus = torch.cuda.device_count()
    print(f"🎮 GPUs CUDA detectadas: {num_gpus}")
    for g in range(num_gpus):
        prop = torch.cuda.get_device_properties(g)
        print(f"   - GPU {g}: {prop.name} ({prop.total_memory / (1024**3):.1f} GB VRAM)")

    if num_gpus == 0:
        raise SystemError("No se detectó GPU CUDA. Por favor activa 'GPU T4 x2' en las opciones de Kaggle.")

    model_id = "Qwen/Qwen2.5-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    dir_salida = Path(f"/kaggle/working/resultados/{VERSION}-{tema}")
    dir_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = dir_salida / f"{tema}_clasificado_final.parquet"

    gpus_a_usar = min(num_gpus, 2)
    print(f"🚀 Lanzando inferencia paralela en {gpus_a_usar} GPU(s)...")

    particiones = [df.iloc[g::gpus_a_usar].copy() for g in range(gpus_a_usar)]
    t_inicio_total = time.time()
    todos_procesados = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=gpus_a_usar) as executor:
        futuros = [
            executor.submit(worker_inferencia, g, particiones[g], tema, model_id, bnb_config, tokenizer, dir_salida)
            for g in range(gpus_a_usar)
        ]
        for futuro in concurrent.futures.as_completed(futuros):
            todos_procesados.extend(futuro.result())

    df_final = pd.DataFrame(todos_procesados)
    for c in df_final.select_dtypes(include=["object"]).columns:
        df_final[c] = df_final[c].apply(lambda x: None if x is None else str(x))

    df_final.to_parquet(ruta_salida, index=False)
    tiempo_tot = (time.time() - t_inicio_total) / 60
    ritmo_global = len(df) / max(time.time() - t_inicio_total, 1) * 60

    print(f"\n{'='*70}")
    print(f"🎉 ¡PROCESO MULTI-GPU COMPLETADO EN {tiempo_tot:.2f} MINUTOS!")
    print(f"⚡ Ritmo global promedio: {ritmo_global:.0f} notas/minuto")
    print(f"📁 Archivo final consolidado: {ruta_salida}")
    print(f"📊 Total registros clasificados: {len(df_final):,}")
    print(f"{'='*70}")


if __name__ == "__main__":
    tema = sys.argv[1] if len(sys.argv) > 1 else TEMA_ACTUAL
    ejecutar_pipeline_kaggle(tema=tema)
