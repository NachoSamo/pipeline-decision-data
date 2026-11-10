"""Módulo de Inferencia y Clasificación LLM Modular.

Soporta múltiples backends (Mock para test, vLLM para GPU en Kaggle, y APIs).
Garantiza Structured Outputs y generación de strings sintéticos para embeddings.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import ValidationError

try:
    from .taxonomia import (
        RegistroAnalizado,
        TAXONOMIAS_POR_TEMA,
        TipoCausaRaiz,
        AlcanceGeografico,
        EstadoMadurezSolucion,
        generar_texto_embedding_problema,
        generar_texto_embedding_solucion
    )
except ImportError:
    from taxonomia import (
        RegistroAnalizado,
        TAXONOMIAS_POR_TEMA,
        TipoCausaRaiz,
        AlcanceGeografico,
        EstadoMadurezSolucion,
        generar_texto_embedding_problema,
        generar_texto_embedding_solucion
    )


def generar_prompt_sistema(tema: str = "residuos") -> str:
    """Genera el prompt del sistema adaptado dinámicamente a la temática seleccionada."""
    config_tema = TAXONOMIAS_POR_TEMA.get(tema, TAXONOMIAS_POR_TEMA["residuos"])
    lista_problemas = config_tema["problemas"]
    lista_soluciones = config_tema["soluciones"]
    lista_subcat = config_tema["subcategorias"]

    return f"""Eres un analista experto en sostenibilidad y temáticas ambientales enfocado en el sector de: {tema.upper()}.
Tu tarea es analizar notas informativas y extraer información estructurada en ESPAÑOL.

REGLAS CRÍTICAS:
1. IDIOMA: Todo el texto generado DEBE estar estrictamente en ESPAÑOL, independientemente del idioma original.
2. DESCARTE DE RUIDO: Si la nota NO trata genuinamente sobre {tema}, sostenibilidad o medio ambiente (ej. deportes, farándula, política partidaria sin vínculo ambiental), DEBES responder ÚNICAMENTE con:
{{}}

3. REGISTROS VÁLIDOS: Devuelve un JSON con:
- "problematica": null o {{
    "tipo_problema": Uno de {lista_problemas},
    "titulo_sintetico": Frase concisa del problema en español,
    "descripcion": Explicación de 1-2 oraciones del problema,
    "causas_raiz": Lista de 1 o más de {[e.value for e in TipoCausaRaiz]},
    "afectados_o_actores": Lista de comunidades, municipios o actores perjudicados,
    "magnitud_o_cifras": Toneladas, porcentajes o cantidades si se informan, o null,
    "soluciones_fallidas_mencionadas": Planes o proyectos anteriores que fallaron si se mencionan, o null
  }}

- "solucion": null o {{
    "tipo_solucion": Uno de {lista_soluciones},
    "nombre_solucion_o_tecnologia": Nombre del producto o iniciativa,
    "quien_la_impulsa": Empresa, startup, gobierno o entidad responsable,
    "descripcion": Breve descripción funcional,
    "estado_madurez": Uno de {[e.value for e in EstadoMadurezSolucion]},
    "tipo_problema_objetivo": Uno de {lista_problemas} (qué problema mitiga),
    "detalle_problema_objetivo": Explicación concisa de cómo ayuda a resolver ese problema,
    "evidencia_o_resultados": Adopción, toneladas recuperadas o clientes si se reportan, o null
  }}

- "metadatos": {{
    "fuente_medio": Nombre del medio o portal,
    "fecha_publicacion": Fecha en formato YYYY-MM-DD o null,
    "subcategoria": Uno de {lista_subcat},
    "alcance_geografico": Uno de {[e.value for e in AlcanceGeografico]},
    "ubicacion_especifica": Ciudad, provincia o país mencionado
  }}

No agregues texto explicativo ni bloques markdown adicionales.
"""


def construir_prompt_usuario(registro: Dict[str, Any]) -> str:
    """Arma el bloque con el contenido de la nota para el LLM."""
    return f"""Analiza la siguiente nota:

MEDIO: {registro.get('fuente', 'Desconocido')}
FECHA: {registro.get('fecha', 'S/D')}
TÍTULO: {registro.get('titulo', '')}
BAJADA: {registro.get('bajada', '')}
CUERPO:
{registro.get('cuerpo_limpio', '')}
"""


class BaseLLMBackend(ABC):
    @abstractmethod
    def inferir(self, prompt_sistema: str, prompt_usuario: str) -> str:
        pass


class MockLLMBackend(BaseLLMBackend):
    """Backend simulador para tests unitarios y benchmarks sin GPU/API."""
    def inferir(self, prompt_sistema: str, prompt_usuario: str) -> str:
        prompt_lower = prompt_usuario.lower()
        if any(w in prompt_lower for w in ["partido", "luján", "primera c", "la barra", "cuarteto", "marcos peña"]):
            return "{}"

        if "recycling rates remain at 44%" in prompt_lower or "stagnant" in prompt_lower:
            return json.dumps({
                "problematica": {
                    "tipo_problema": "ESTANCAMIENTO_SEPARACION_Y_RECICLAJE",
                    "titulo_sintetico": "Estancamiento en la tasa de reciclaje domiciliario en el Reino Unido",
                    "descripcion": "La tasa de reciclaje de residuos domiciliarios en el Reino Unido se mantiene estancada en el 44%.",
                    "causas_raiz": ["FALTA_DE_INFRAESTRUCTURA_TECNOLOGICA", "DESCENTRALIZACION_O_VACIO_NORMATIVO"],
                    "afectados_o_actores": ["Hogares del Reino Unido", "Defra"],
                    "magnitud_o_cifras": "44% tasa de reciclaje",
                    "soluciones_fallidas_mencionadas": None
                },
                "solucion": None,
                "metadatos": {
                    "fuente_medio": "Circular Online",
                    "fecha_publicacion": "2024-09-27",
                    "subcategoria": "MIXTO_DOMICILIARIO",
                    "alcance_geografico": "INTERNACIONAL_GLOBAL",
                    "ubicacion_especifica": "Reino Unido"
                }
            })

        if "durmientes" in prompt_lower or "circularis" in prompt_lower:
            return json.dumps({
                "problematica": None,
                "solucion": {
                    "tipo_solucion": "UPCYCLING_Y_VALORIZACION_MATERIAL",
                    "nombre_solucion_o_tecnologia": "Durmientes sintéticos de plástico reciclado",
                    "quien_la_impulsa": "Circularis",
                    "descripcion": "Fabricación de durmientes ferroviarios a partir de residuos plásticos bajo economía circular.",
                    "estado_madurez": "EN_MERCADO_COMERCIAL",
                    "tipo_problema_objetivo": "CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS",
                    "detalle_problema_objetivo": "Aprovecha plásticos descartados para reemplazar madera y hormigón en vías de tren.",
                    "evidencia_o_resultados": "Exportación a la red ferroviaria de Chile."
                },
                "metadatos": {
                    "fuente_medio": "ECOBIZ",
                    "fecha_publicacion": "2026-09-22",
                    "subcategoria": "PLASTICOS_ENVASES",
                    "alcance_geografico": "CORDOBA_LOCAL",
                    "ubicacion_especifica": "Monte Cristo, Córdoba, Argentina"
                }
            })

        return json.dumps({
            "problematica": {
                "tipo_problema": "CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS",
                "titulo_sintetico": "Impacto y acumulación de residuos plásticos",
                "descripcion": "Acumulación de residuos en el entorno natural con impacto ambiental.",
                "causas_raiz": ["SOBREPRODUCCION_Y_DISENO_NO_RECICLABLE"],
                "afectados_o_actores": ["Ecosistema local"],
                "magnitud_o_cifras": None,
                "soluciones_fallidas_mencionadas": None
            },
            "solucion": None,
            "metadatos": {
                "fuente_medio": "General",
                "fecha_publicacion": "2025-01-01",
                "subcategoria": "PLASTICOS_ENVASES",
                "alcance_geografico": "LATAM_REGIONAL",
                "ubicacion_especifica": "Regional"
            }
        })


class ClasificadorLLM:
    """Clasificador orquestador parametrizable por tema."""

    def __init__(self, backend: Optional[BaseLLMBackend] = None, tema: str = "residuos"):
        self.backend = backend or MockLLMBackend()
        self.tema = tema
        self.prompt_sistema = generar_prompt_sistema(tema)

    def procesar_registro(self, registro: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envía el registro al modelo, valida con Pydantic y genera strings de embeddings."""
        prompt_usuario = construir_prompt_usuario(registro)
        respuesta_raw = self.backend.inferir(self.prompt_sistema, prompt_usuario).strip()

        if respuesta_raw in ("{}", "", "{ }"):
            return None

        try:
            datos_json = json.loads(respuesta_raw)
            if not datos_json:
                return None

            modelo = RegistroAnalizado.model_validate(datos_json)

            embedding_prob = None
            if modelo.problematica:
                embedding_prob = generar_texto_embedding_problema(modelo.problematica, modelo.metadatos, tema=self.tema)

            embedding_sol = None
            if modelo.solucion:
                embedding_sol = generar_texto_embedding_solucion(modelo.solucion, modelo.metadatos, tema=self.tema)

            return {
                "id_original": registro.get("id"),
                "fuente_original": registro.get("fuente"),
                "url": registro.get("url"),
                "fecha_original": registro.get("fecha"),
                "datos_estructurados": modelo.model_dump(),
                "texto_embedding_problema": embedding_prob,
                "texto_embedding_solucion": embedding_sol
            }

        except (json.JSONDecodeError, ValidationError) as e:
            return {
                "id_original": registro.get("id"),
                "error_parseo": str(e),
                "respuesta_raw": respuesta_raw
            }
