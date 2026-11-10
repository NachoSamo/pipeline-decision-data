"""Pipeline de Clasificación Local usando la API de Gemini Flash.

Permite procesar el dataset empaquetado directamente desde tu máquina
a máxima velocidad, con checkpoints automáticos y tolerancia a reanudación.

Uso:
    python scripts/clasificacion/local_gemini_pipeline.py --limite 50
    python scripts/clasificacion/local_gemini_pipeline.py --api-key TU_API_KEY
    python scripts/clasificacion/local_gemini_pipeline.py --tema residuos
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Añadir directorio actual al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

from taxonomia import TAXONOMIAS_POR_TEMA, TipoCausaRaiz, AlcanceGeografico, EstadoMadurezSolucion

load_dotenv()


def armar_prompt_sistema(tema: str) -> str:
    config = TAXONOMIAS_POR_TEMA.get(tema, TAXONOMIAS_POR_TEMA["residuos"])
    return f"""Eres un analista experto en sostenibilidad enfocado en: {tema.upper()}.
Analiza la nota periodística y extrae información estructurada en ESPAÑOL.

REGLAS CRÍTICAS:
1. IDIOMA: Todo el contenido generado DEBE estar estrictamente en ESPAÑOL.
2. DESCARTE DE RUIDO: Si la nota NO trata sobre {tema}, sostenibilidad o medio ambiente (ej. deportes, fútbol, farándula, política partidaria sin contexto ambiental), responde ÚNICAMENTE:
{{}}

3. REGISTROS VÁLIDOS: Devuelve un JSON con:
- "problematica": null o {{
    "tipo_problema": Uno de {config['problemas']},
    "titulo_sintetico": Frase resumen en español,
    "descripcion": Explicación de 1-2 oraciones del problema,
    "causas_raiz": Lista de 1 o más de {[e.value for e in TipoCausaRaiz]},
    "afectados_o_actores": Lista de comunidades o actores perjudicados,
    "magnitud_o_cifras": Cifras, porcentajes o toneladas si se informan, o null
  }}
- "solucion": null o {{
    "tipo_solucion": Uno de {config['soluciones']},
    "nombre_solucion_o_tecnologia": Nombre de la tecnología o iniciativa,
    "quien_la_impulsa": Entidad responsable,
    "descripcion": Breve descripción funcional,
    "tipo_problema_objetivo": Uno de {config['problemas']},
    "detalle_problema_objetivo": Cómo resuelve ese problema,
    "estado_madurez": "INVESTIGACION_PILOTO" | "EN_MERCADO_COMERCIAL" | "POLITICA_PUBLICA" | "PROYECTO_FUTURO_ANUNCIO",
    "evidencia_o_resultados": Adopción, toneladas recuperadas o clientes, o null
  }}
- "metadatos": {{
    "fuente_medio": Nombre del medio o portal,
    "fecha_publicacion": Formato YYYY-MM-DD o null,
    "subcategoria": Uno de {config['subcategorias']},
    "alcance_geografico": "CORDOBA_LOCAL" | "ARGENTINA_NACIONAL" | "LATAM_REGIONAL" | "INTERNACIONAL_GLOBAL",
    "ubicacion_especifica": Ciudad, provincia o país mencionado
  }}

Devuelve únicamente el objeto JSON sin bloques adicionales ni introducciones.
"""


def a_str(val: Any) -> Optional[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
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


def procesar_nota_con_gemini(client: genai.Client, model_name: str, prompt_sistema: str, row: Dict[str, Any], tema: str) -> Optional[Dict[str, Any]]:
    texto_usuario = (
        f"MEDIO: {row.get('fuente', '')}\n"
        f"FECHA: {row.get('fecha', '')}\n"
        f"TÍTULO: {row.get('titulo', '')}\n"
        f"BAJADA: {row.get('bajada', '')}\n"
        f"CUERPO:\n{row.get('cuerpo_limpio', '')}"
    )

    max_intentos = 4
    for intento in range(max_intentos):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=texto_usuario,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            txt = (response.text or "").strip()
            if txt in ("{}", "", "{ }", "[]"):
                return None

            match_json = re.search(r"\{.*\}", txt, re.DOTALL)
            if not match_json:
                return None

            datos = json.loads(match_json.group(0))
            if not datos:
                return None

            prob = datos.get("problematica") or {}
            sol = datos.get("solucion") or {}
            meta = datos.get("metadatos") or {}

            # Si ambos vienen vacíos, es un descarte
            if not prob and not sol:
                return None

            causas_str = a_lista_str(prob.get("causas_raiz")) if prob else ""
            afectados_str = a_lista_str(prob.get("afectados_o_actores")) if prob else ""
            tipo_prob = a_str(prob.get("tipo_problema")) if prob else None
            tit_prob = a_str(prob.get("titulo_sintetico")) if prob else None
            tipo_sol = a_str(sol.get("tipo_solucion")) if sol else None
            nom_sol = a_str(sol.get("nombre_solucion_o_tecnologia")) if sol else None
            obj_sol = a_str(sol.get("tipo_problema_objetivo")) if sol else None

            embed_prob = f"TRACK: {tema.upper()}. PROBLEMA: {tipo_prob}. {tit_prob}. CAUSAS: {causas_str}" if prob else None
            embed_sol = f"TRACK: {tema.upper()}. SOLUCION: {tipo_sol}. {nom_sol}. RESUELVE: {obj_sol}" if sol else None

            return {
                "id_original": a_str(row.get("id")),
                "tema": tema,
                "fuente": a_str(meta.get("fuente_medio") or row.get("fuente")),
                "url": a_str(row.get("url")),
                "fecha": a_str(meta.get("fecha_publicacion") or row.get("fecha")),
                "es_problema": bool(prob),
                "tipo_problema": tipo_prob,
                "titulo_problema": tit_prob,
                "descripcion_problema": a_str(prob.get("descripcion")),
                "causas_raiz": causas_str,
                "afectados": afectados_str,
                "magnitud": a_str(prob.get("magnitud_o_cifras")),
                "es_solucion": bool(sol),
                "tipo_solucion": tipo_sol,
                "nombre_solucion": nom_sol,
                "quien_impulsa": a_str(sol.get("quien_la_impulsa")),
                "descripcion_solucion": a_str(sol.get("descripcion")),
                "tipo_problema_objetivo": obj_sol,
                "detalle_problema_objetivo": a_str(sol.get("detalle_problema_objetivo")),
                "subcategoria": a_str(meta.get("subcategoria")),
                "alcance_geo": a_str(meta.get("alcance_geografico")),
                "ubicacion": a_str(meta.get("ubicacion_especifica")),
                "texto_embedding_problema": embed_prob,
                "texto_embedding_solucion": embed_sol
            }
        except Exception as e:
            err_str = str(e).lower()
            if "503" in err_str or "unavailable" in err_str or "high demand" in err_str or "overloaded" in err_str:
                espera = 5 * (intento + 1)
                print(f"  ⏳ [Servidor ocupado 503] Alta demanda temporal en Gemini. Esperando {espera}s (intento {intento+1}/{max_intentos})...")
                time.sleep(espera)
                continue
            elif "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str or "rate limit" in err_str:
                espera = 8 * (intento + 1)
                print(f"  ⏳ [Límite de cuota 429] Superado límite RPM de la cuenta. Esperando {espera}s...")
                time.sleep(espera)
                continue
            else:
                print(f"  ⚠️ [Error API] Nota {row.get('url', 'S/URL')[:60]}...: {type(e).__name__} - {e}")
                return None
    return None


def ejecutar_pipeline_local_gemini(
    tema: str = "residuos",
    limite: Optional[int] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.8-flash",
    checkpoint_cada: int = 50,
    delay: float = 2.5
):
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        print("\nERROR: No se encontró GEMINI_API_KEY.")
        print("Configúrala en tu entorno o pásala como parámetro:")
        print("  python scripts/clasificacion/local_gemini_pipeline.py --api-key TU_API_KEY")
        return

    raiz = Path(__file__).resolve().parent.parent.parent
    ruta_input = raiz / "data" / "resultados" / tema / f"{tema}_listo_para_kaggle.parquet"

    if not ruta_input.exists():
        print(f"ERROR: No se encontró el dataset empaquetado en:\n{ruta_input}")
        print(f"Ejecuta primero: python scripts/clasificacion/empaquetar.py --tema {tema}")
        return

    print("=" * 80)
    print(f"PIPELINE LOCAL CON GEMINI FLASH ({model_name.upper()}) · TRACK: {tema.upper()}")
    print("=" * 80)

    client = genai.Client(api_key=key)

    # Healthcheck previo con el modelo
    print(f"Verificando conexión con el modelo '{model_name}'...")
    try:
        check = client.models.generate_content(
            model=model_name,
            contents="Responde únicamente con la palabra OK."
        )
        print(f"✅ Conexión exitosa con Google AI Studio. Respuesta: {check.text.strip()}\n")
    except Exception as e:
        print(f"\n❌ Error de conexión con '{model_name}': {e}")
        return
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
    dir_salida = raiz / "data" / "resultados" / tema
    dir_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = dir_salida / f"{tema}_clasificado.parquet"
    ruta_checkpoint = dir_salida / f"{tema}_checkpoint.parquet"

    # Si ya existía un archivo, cargamos los IDs ya procesados para no repetir
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
        res = procesar_nota_con_gemini(client, model_name, prompt_sistema, row, tema)
        if res:
            procesados.append(res)
            if limite and limite <= 50:
                tipo = res.get('tipo_problema') or res.get('tipo_solucion')
                etiqueta = "Problema" if res.get('es_problema') else "Solución"
                print(f"[{idx}/{len(filas_a_procesar)}] ✅ [{etiqueta}] {tipo} - {str(row.get('titulo', ''))[:55]}...")
        else:
            if limite and limite <= 50:
                print(f"[{idx}/{len(filas_a_procesar)}] ⚪ Descartado (No relevante / Ruido) - {str(row.get('titulo', ''))[:55]}...")

        if idx % 10 == 0 or idx == len(filas_a_procesar):
            ritmo = idx / (time.time() - inicio_tiempo)
            print(f"--- Progreso: [{idx}/{len(filas_a_procesar)}] ({idx/len(filas_a_procesar):.1%}) | Clasificados con valor: {len(procesados)} | {ritmo*60:.0f} notas/min ---")

        # Guardar checkpoint
        if len(procesados) > 0 and idx % checkpoint_cada == 0:
            df_ckpt = pd.DataFrame(procesados)
            for c in df_ckpt.select_dtypes(include=["object"]).columns:
                df_ckpt[c] = df_ckpt[c].apply(lambda x: None if x is None else str(x))
            df_ckpt.to_parquet(ruta_checkpoint, index=False)

        # Pausa entre peticiones para respetar el rate limit de Free Tier (15 RPM)
        if delay > 0 and idx < len(filas_a_procesar):
            time.sleep(delay)

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
    parser = argparse.ArgumentParser(description="Clasificador local con Gemini Flash API.")
    parser.add_argument("--tema", type=str, default="residuos", help="Temática (residuos, etc.)")
    parser.add_argument("--limite", type=int, default=None, help="Límite de notas a procesar (ej. 50 para prueba)")
    parser.add_argument("--api-key", type=str, default=None, help="Gemini API Key de Google AI Studio")
    parser.add_argument("--model", type=str, default="gemini-3.8-flash", help="Modelo de Gemini a usar")
    parser.add_argument("--checkpoint-cada", type=int, default=50, help="Frecuencia de guardado de checkpoints")
    parser.add_argument("--delay", type=float, default=2.5, help="Segundos de espera entre peticiones (default 2.5s para 15 RPM en Free Tier)")
    args = parser.parse_args()

    ejecutar_pipeline_local_gemini(
        tema=args.tema,
        limite=args.limite,
        api_key=args.api_key,
        model_name=args.model,
        checkpoint_cada=args.checkpoint_cada,
        delay=args.delay
    )
