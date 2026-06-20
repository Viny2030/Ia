import pandas as pd
import numpy as np
from langchain_core.tools import tool
@tool
def extraer_datos_entidad(nombre_entidad: str) -> str:
"""Busca y extrae registros históricos, contratos y transacciones de una entidad específica
desde los archivos locales."""
try:
# Simulación de lectura de datos optimizada (p. ej., desde Parquet o CSV)
# En producción: df = pd.read_parquet(f"datos/{nombre_entidad}.parquet")
# Simulación de estructura de datos encontrada
datos_simulados = {
"entidad": nombre_entidad,
"contratos_totales": 5,
"monto_acumulado_ars": 150000000,
"desviacion_precios_promedio": 0.35, # 35% arriba del mercado
"adjudicaciones_directas": 4
}
return f"ÉXITO - Datos consolidados para {nombre_entidad}: {datos_simulados}"

1

3. Estructura del Grafo de Estados
grafo.py
Define la memoria estructural (Estado) y el flujo de control mediante nodos y reglas condicionales rígidas de
negocio.
except Exception as e:
return f"ERROR - No se pudieron extraer los datos debido a un fallo en el sistema:
{str(e)}"
@tool
def verificar_red_vinculos(nombre_entidad: str) -> str:
"""Analiza relaciones explícitas e implícitas de la entidad con firmas o directores bajo
sospecha."""
try:
# Lógica para cruzar matrices de relaciones directas/indirectas
conexiones_riesgosas = ["Empresa_Fantasma_S.A.", "Ex_Funcionario_Publico"]
return f"ANÁLISIS DE VÍNCULOS - La entidad '{nombre_entidad}' posee coincidencias con:
{conexiones_riesgosas}"
except Exception as e:
return f"ERROR - Fallo al procesar la red de vínculos relacionales: {str(e)}"""
