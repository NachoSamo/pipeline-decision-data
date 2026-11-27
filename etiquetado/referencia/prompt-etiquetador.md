# Prompt del etiquetador de referencia · movilidad

Vale para Claude Code y para OpenCode. Antes de pegarlo, reemplazar `<ARCHIVO_ENTRADA>`, `<ARCHIVO_SALIDA>` y
`<MODELO>`.

| Corrida | `<ARCHIVO_ENTRADA>` | `<ARCHIVO_SALIDA>` |
|---|---|---|
| Calibración (25 notas del gold) | `etiquetado/referencia/movilidad-calibracion.json` | `etiquetado/referencia/movilidad-calibracion-<modelo>.json` |
| Referencia, parte n (125 notas) | `etiquetado/referencia/movilidad-parte<n>.json` | `etiquetado/referencia/movilidad-referencia-parte<n>.json` |

Después de las corridas: `python etiquetado/calibrar.py` (calibración) o `python etiquetado/calibrar.py --unir`
(referencia).

---

Trabajás en `C:\Users\Nacho\Hack2TheFuture-2026\pipeline-decision-data`. Respondé en español.
Tarea: etiquetar notas de movilidad como referencia para evaluar a un LLM chico. No modifiques ningún archivo salvo
el de salida.

1. Leé completos `etiquetado/guia-movilidad.md`, las categorías de movilidad de `etiquetado/config.js` y
   `etiquetado/reconciliacion/movilidad-gold.json` (ejemplo de formato; no uses sus etiquetas como respuesta).
   Las notas a etiquetar están en `<ARCHIVO_ENTRADA>`, en la lista `notas`.
2. Para cada nota, leé título, bajada y cuerpo y aplicá la guía en orden: relevancia con sus 3 preguntas, tipo y
   categorías. Ante la duda, gana el criterio estricto de la guía ("no relevante"). Son "no relevante": la seguridad
   vial, la política o economía sin una medida de transporte, otro track ambiental y la gestión sin problema ni
   solución. El idioma no importa. El alcance no se etiqueta: ya viene en la nota.
3. Escribí `<ARCHIVO_SALIDA>` con `{"track": "movilidad", "etiquetador": "<MODELO>", "etiquetas": [...]}`, una
   entrada por nota con:
   - `id` (copiado exacto) y `relevante` (true o false);
   - `motivo`: `problema_o_solucion_concreta` (solo si es relevante), `movilidad_de_pasada`, `seguridad_vial`,
     `politica_o_economia_sin_medida`, `otro_track_ambiental`, `otro_tema`, `nota_de_color` o
     `gestion_sin_problema_ni_solucion`;
   - `tipo`: `problema`, `solucion` o `ambas`; null si no es relevante;
   - `categorias_problema` y `categorias_solucion`: listas, solo con valores de `config.js`; vacías si no es
     relevante;
   - `categoria_otra`: texto obligatorio si usaste una categoría "otro"; si no, null;
   - `categoria_sugerida`: opcional. Si ninguna categoría describe bien la nota, un nombre corto y una línea,
     por ejemplo `"TRANSPORTE_DE_CARGAS: logística urbana de reparto"`; si no, null;
   - `comentario`: una línea con la regla de la guía que aplicaste.
4. Al terminar, validá el JSON: tantas entradas como notas, `id` únicos y categorías válidas. Decí cuántas notas
   marcaste como relevantes.

En Claude Code, para las 3 partes de la referencia: lanzá 3 subagentes en paralelo con el modelo elegido, uno por
parte, cada uno con este prompt y su archivo.
