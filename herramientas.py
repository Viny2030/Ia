# =====================================================================
# FILENAME: herramientas.py
# =====================================================================
import os
import httpx
from langchain_core.tools import tool

# Traemos las URLs de tus servicios (con los fallbacks que usás en main.py)
CONTRATOS_V2_URL = os.getenv("CONTRATOS_V2_API_URL", "https://monitorcontratos-production.up.railway.app")
IRI_URL = os.getenv("IRI_API_URL", "https://monitor-production-f053.up.railway.app")

@tool
def extraer_datos_entidad(nombre_entidad: str) -> str:
    """Busca y extrae registros históricos, contratos y desvíos de precios 
    de una entidad o proveedor específico desde el Monitor de Contratos v2."""
    try:
        # Consultamos tu API de contratos v2 en producción
        with httpx.Client(timeout=10) as client:
            # Nota: Ajustá el endpoint (/proveedor, /buscar, etc.) según la API de tu contenedor
            endpoint = f"{CONTRATOS_V2_URL}/buscar?q={nombre_entidad}"
            response = client.get(endpoint)
            
            if response.status_code == 200:
                datos = response.json()
                return f"ÉXITO - Datos reales consolidados para {nombre_entidad}: {datos}"
            else:
                return f"ALERTA - Endpoint respondió con código {response.status_code} para {nombre_entidad}."
    except Exception as e:
        # Fallback controlado si el servicio está caído para que el agente no muera
        return f"ERROR - No se pudo conectar al Monitor de Contratos v2: {str(e)}"

@tool
def verificar_red_vinculos(nombre_entidad: str) -> str:
    """Analiza el Índice de Riesgo Institucional (IRI) y busca si la entidad 
    posee alertas de riesgo financiero, de contratación u operativo."""
    try:
        with httpx.Client(timeout=10) as client:
            # Consultamos tus endpoints analíticos del IRI
            endpoint = f"{IRI_URL}/iri/top-riesgo"
            response = client.get(endpoint)
            
            if response.status_code == 200:
                datos_iri = response.json()
                # Acá el LLM podrá evaluar si el proveedor figura en el top de riesgo
                return f"ANÁLISIS DE VÍNCULOS E IRI - Reporte de riesgo actual: {datos_iri}"
            else:
                return f"ALERTA - No se pudo obtener el top de riesgo del IRI. Código: {response.status_code}"
    except Exception as e:
        return f"ERROR - Fallo al procesar la red de vínculos relacionales en el IRI: {str(e)}"
