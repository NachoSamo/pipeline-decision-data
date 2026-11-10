"""Taxonomía modular, Enums y modelos de datos para la clasificación con LLM.

Diseñado para soportar múltiples temáticas de sostenibilidad (Residuos, Biodiversidad,
Movilidad, Agro) compartiendo la misma estructura central de salida JSON.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# ENUMS TRANSVERSALES (Aplican a todos los tracks)
# ==============================================================================

class AlcanceGeografico(str, Enum):
    CORDOBA_LOCAL = "CORDOBA_LOCAL"
    ARGENTINA_NACIONAL = "ARGENTINA_NACIONAL"
    LATAM_REGIONAL = "LATAM_REGIONAL"
    INTERNACIONAL_GLOBAL = "INTERNACIONAL_GLOBAL"


class EstadoMadurezSolucion(str, Enum):
    INVESTIGACION_PILOTO = "INVESTIGACION_PILOTO"
    EN_MERCADO_COMERCIAL = "EN_MERCADO_COMERCIAL"
    POLITICA_PUBLICA = "POLITICA_PUBLICA"
    PROYECTO_FUTURO_ANUNCIO = "PROYECTO_FUTURO_ANUNCIO"
    NO_APLICA = "NO_APLICA"


class TipoCausaRaiz(str, Enum):
    """Causas raíz sistémicas compartidas en sostenibilidad."""
    FALTA_DE_INFRAESTRUCTURA_TECNOLOGICA = "FALTA_DE_INFRAESTRUCTURA_TECNOLOGICA"
    DESCONOCIMIENTO_O_FALTA_EDUCACION_CIUDADANA = "DESCONOCIMIENTO_O_FALTA_EDUCACION_CIUDADANA"
    DESCENTRALIZACION_O_VACIO_NORMATIVO = "DESCENTRALIZACION_O_VACIO_NORMATIVO"
    INEFICIENCIA_EN_GESTION_PUBLICA = "INEFICIENCIA_EN_GESTION_PUBLICA"
    INVIABILIDAD_ECONOMICA_O_COSTOS_LOGISTICOS = "INVIABILIDAD_ECONOMICA_O_COSTOS_LOGISTICOS"
    CONFLICTO_LABORAL_O_SINDICAL = "CONFLICTO_LABORAL_O_SINDICAL"
    SOBREPRODUCCION_Y_DISENO_NO_RECICLABLE = "SOBREPRODUCCION_Y_DISENO_NO_RECICLABLE"
    FALTA_DE_CONTROL_Y_SANCIONES = "FALTA_DE_CONTROL_Y_SANCIONES"
    CONFUSION_EN_ROTULADO_Y_FECHAS_CADUCIDAD = "CONFUSION_EN_ROTULADO_Y_FECHAS_CADUCIDAD"
    OTRA_CAUSA = "OTRA_CAUSA"


# ==============================================================================
# ENUMS ESPECÍFICOS: RESIDUOS
# ==============================================================================

class TipoProblemaResiduos(str, Enum):
    COLAPSO_Y_SATURACION_DISPOSICION_FINAL = "COLAPSO_Y_SATURACION_DISPOSICION_FINAL"
    ESTANCAMIENTO_SEPARACION_Y_RECICLAJE = "ESTANCAMIENTO_SEPARACION_Y_RECICLAJE"
    CONFLICTO_TERRITORIAL_Y_LABORAL = "CONFLICTO_TERRITORIAL_Y_LABORAL"
    DESPERDICIO_ALIMENTARIO_Y_ORGANICOS = "DESPERDICIO_ALIMENTARIO_Y_ORGANICOS"
    CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS = "CONTAMINACION_ECOSISTEMICA_Y_PLASTICOS"
    GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE = "GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE"
    BARRERAS_DE_MERCADO_Y_ECONOMICAS = "BARRERAS_DE_MERCADO_Y_ECONOMICAS"
    FALLA_REGULATORIA_Y_FISCALIZACION = "FALLA_REGULATORIA_Y_FISCALIZACION"
    EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES = "EFLUENTES_Y_LIXIVIADOS_INDUSTRIALES"
    OTRO_PROBLEMA_RESIDUOS = "OTRO_PROBLEMA_RESIDUOS"


class TipoSolucionResiduos(str, Enum):
    AUTOMATIZACION_Y_ROBOTICA_CLASIFICACION = "AUTOMATIZACION_Y_ROBOTICA_CLASIFICACION"
    TRAZABILIDAD_DIGITAL_Y_SOFTWARE = "TRAZABILIDAD_DIGITAL_Y_SOFTWARE"
    UPCYCLING_Y_VALORIZACION_MATERIAL = "UPCYCLING_Y_VALORIZACION_MATERIAL"
    SISTEMAS_DEPOSITO_Y_RETORNO_DRS = "SISTEMAS_DEPOSITO_Y_RETORNO_DRS"
    BIODIGESTION_Y_COMPOSTAJE_AVANZADO = "BIODIGESTION_Y_COMPOSTAJE_AVANZADO"
    ECODISENO_Y_REDUCCION_EN_ORIGEN = "ECODISENO_Y_REDUCCION_EN_ORIGEN"
    REUTILIZACION_Y_SEGUNDA_VIDA = "REUTILIZACION_Y_SEGUNDA_VIDA"
    REGULACION_Y_POLITICA_PUBLICA = "REGULACION_Y_POLITICA_PUBLICA"
    TRATAMIENTO_Y_VALORIZACION_EFLUENTES = "TRATAMIENTO_Y_VALORIZACION_EFLUENTES"
    OTRA_SOLUCION_RESIDUOS = "OTRA_SOLUCION_RESIDUOS"


class MaterialPredominanteResiduos(str, Enum):
    PLASTICOS_ENVASES = "PLASTICOS_ENVASES"
    ORGANICOS_ALIMENTOS = "ORGANICOS_ALIMENTOS"
    ELECTRONICOS_BATERIAS_RAEE = "ELECTRONICOS_BATERIAS_RAEE"
    TEXTILES = "TEXTILES"
    VIDRIO = "VIDRIO"
    METALES_FERROSOS = "METALES_FERROSOS"
    CONSTRUCCION_DEMOLICION_RCD = "CONSTRUCCION_DEMOLICION_RCD"
    EFLUENTES_LIXIVIADOS = "EFLUENTES_LIXIVIADOS"
    MIXTO_DOMICILIARIO = "MIXTO_DOMICILIARIO"
    NO_APLICA = "NO_APLICA"


# Registro extensible por tema
TAXONOMIAS_POR_TEMA = {
    "residuos": {
        "problemas": [e.value for e in TipoProblemaResiduos],
        "soluciones": [e.value for e in TipoSolucionResiduos],
        "subcategorias": [e.value for e in MaterialPredominanteResiduos],
        "etiqueta_subcategoria": "material_predominante"
    }
}


# ==============================================================================
# MODELOS PYDANTIC ESTRUCTURADOS (Salida estándar compartida)
# ==============================================================================

class AnalisisProblematica(BaseModel):
    tipo_problema: str = Field(..., description="Categoría de problema")
    titulo_sintetico: str = Field(..., description="Frase sintética clara del problema en español")
    descripcion: str = Field(..., description="Descripción breve (1-2 oraciones) del problema")
    causas_raiz: List[TipoCausaRaiz] = Field(..., description="Lista de causas raíz sistémicas identificadas")
    afectados_o_actores: List[str] = Field(default_factory=list, description="Actores o comunidades afectadas")
    magnitud_o_cifras: Optional[str] = Field(None, description="Métricas, porcentajes o cantidades reportadas")
    soluciones_fallidas_mencionadas: Optional[str] = Field(None, description="Planes o anuncios previos que fracasaron")


class AnalisisSolucion(BaseModel):
    tipo_solucion: str = Field(..., description="Categoría de solución tecnológica/circular")
    nombre_solucion_o_tecnologia: str = Field(..., description="Nombre del producto, startup o solución")
    quien_la_impulsa: str = Field(..., description="Empresa, universidad o entidad responsable")
    descripcion: str = Field(..., description="Breve descripción funcional de la solución")
    estado_madurez: EstadoMadurezSolucion = Field(default=EstadoMadurezSolucion.EN_MERCADO_COMERCIAL)
    tipo_problema_objetivo: str = Field(..., description="Clave de unión: qué tipo de problema busca resolver")
    detalle_problema_objetivo: str = Field(..., description="Explicación de cómo mitiga el problema")
    evidencia_o_resultados: Optional[str] = Field(None, description="Resultados reportados o tracción comercial")


class MetadatosRegistro(BaseModel):
    fuente_medio: str
    fecha_publicacion: Optional[str] = None
    subcategoria: str = Field("NO_APLICA", description="Material, sector o tipo específico según el track")
    alcance_geografico: AlcanceGeografico = AlcanceGeografico.INTERNACIONAL_GLOBAL
    ubicacion_especifica: Optional[str] = None


class RegistroAnalizado(BaseModel):
    """Estructura completa de salida para notas relevantes de cualquier temática."""
    problematica: Optional[AnalisisProblematica] = None
    solucion: Optional[AnalisisSolucion] = None
    metadatos: MetadatosRegistro


def generar_texto_embedding_problema(prob: AnalisisProblematica, meta: MetadatosRegistro, tema: str = "RESIDUOS") -> str:
    """Genera la ficha sintética estandarizada para vectorizar el problema."""
    causas = ", ".join([c.value if hasattr(c, "value") else str(c) for c in prob.causas_raiz])
    afectados = ", ".join(prob.afectados_o_actores[:5])
    return (
        f"TRACK: {tema.upper()}. PROBLEMA: {prob.tipo_problema}. "
        f"RESUMEN: {prob.titulo_sintetico}. {prob.descripcion} "
        f"CAUSAS SISTEMICAS: {causas}. "
        f"CATEGORIA: {meta.subcategoria}. "
        f"AFECTADOS: {afectados}. "
        f"ALCANCE: {meta.alcance_geografico.value} ({meta.ubicacion_especifica or ''})."
    ).strip()


def generar_texto_embedding_solucion(sol: AnalisisSolucion, meta: MetadatosRegistro, tema: str = "RESIDUOS") -> str:
    """Genera la ficha sintética estandarizada para vectorizar la solución."""
    return (
        f"TRACK: {tema.upper()}. SOLUCION: {sol.tipo_solucion}. "
        f"NOMBRE: {sol.nombre_solucion_o_tecnologia}. "
        f"IMPULSOR: {sol.quien_la_impulsa}. "
        f"PROBLEMA QUE RESUELVE: {sol.tipo_problema_objetivo}. "
        f"DETALLE: {sol.detalle_problema_objetivo}. "
        f"CATEGORIA: {meta.subcategoria}. "
        f"ESTADO: {sol.estado_madurez.value}."
    ).strip()
