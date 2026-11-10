"""Empaqueta y pre-limpia cualquier temática para procesar en Kaggle o con LLM.

Uso:
    python scripts/clasificacion/empaquetar.py --tema residuos
    python scripts/clasificacion/empaquetar.py --tema biodiversidad
    python scripts/clasificacion/empaquetar.py --tema movilidad
"""

import argparse
import glob
import sys
import time
from pathlib import Path

# Permitir ejecución directa del script
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from prelimpieza import prefiltrar_dataframe


def empaquetar_por_tema(tema: str = "residuos", max_chars_cuerpo: int = 2500, long_minima_cuerpo: int = 150):
    inicio = time.time()
    raiz = Path(__file__).resolve().parent.parent.parent
    carpeta_origen = raiz / "data" / tema
    archivos = glob.glob(str(carpeta_origen / "*.parquet"))

    if not archivos:
        # Caso especial para soluciones estructuradas por track
        archivos = glob.glob(str(raiz / "data" / "soluciones" / tema / "*.parquet"))

    if not archivos:
        print(f"Error: No se encontraron archivos Parquet para el tema '{tema}' en {carpeta_origen}")
        return

    print("=" * 80)
    print(f"EMPAQUETADO MODULAR PARA KAGGLE: TRACK '{tema.upper()}'")
    print("=" * 80)
    print(f"Cargando {len(archivos)} archivos Parquet desde {carpeta_origen}...")

    dfs = []
    columnas_necesarias = ["id", "fuente", "url", "fecha", "titulo", "bajada", "body", "seccion", "tags"]

    for arch in archivos:
        try:
            df = pd.read_parquet(arch)
            cols = [c for c in columnas_necesarias if c in df.columns]
            dfs.append(df[cols])
        except Exception as e:
            print(f"  Aviso: Error al leer {Path(arch).name}: {e}")

    if not dfs:
        print("No se pudo cargar ningún registro.")
        return

    df_completo = pd.concat(dfs, ignore_index=True)
    total_original = len(df_completo)
    print(f"Total registros crudos cargados: {total_original}")

    print("Aplicando pre-limpieza heurística ultra-optimizada...")
    df_aptos, df_descartados = prefiltrar_dataframe(
        df_completo,
        max_chars_cuerpo=max_chars_cuerpo,
        long_minima_cuerpo=long_minima_cuerpo
    )

    print(f"- Descartados por heurística (0$ tokens): {len(df_descartados)} ({len(df_descartados)/total_original:.1%})")
    print(f"- Registros APTOS para el LLM:           {len(df_aptos)} ({len(df_aptos)/total_original:.1%})")

    # Guardar en data/resultados/{tema}/
    carpeta_destino = raiz / "data" / "resultados" / tema
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta_destino / f"{tema}_listo_para_kaggle.parquet"

    df_aptos.to_parquet(ruta_salida, index=False)
    tiempo_total = time.time() - inicio

    tam_mb = round(ruta_salida.stat().st_size / (1024 * 1024), 2)
    print(f"\n¡Empaquetado exitoso en {tiempo_total:.2f} segundos!")
    print(f"Archivo guardado en: {ruta_salida}")
    print(f"Tamaño: {tam_mb} MB")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Empaqueta y pre-limpia datasets para inferencia masiva.")
    parser.add_argument("--tema", type=str, default="residuos", help="Temática (residuos, biodiversidad, movilidad, etc.)")
    parser.add_argument("--max-chars", type=int, default=2500, help="Límite de caracteres en el cuerpo (default: 2500)")
    parser.add_argument("--min-chars", type=int, default=150, help="Longitud mínima requerida del cuerpo (default: 150)")
    args = parser.parse_args()

    empaquetar_por_tema(tema=args.tema, max_chars_cuerpo=args.max_chars, long_minima_cuerpo=args.min_chars)
