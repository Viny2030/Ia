# =====================================================================
# FILENAME: herramientas.py (Versión Asistente de Programación)
# =====================================================================
import os
from langchain_core.tools import tool


@tool
def leer_archivo_codigo(nombre_archivo: str) -> str:
    """Lee el contenido de un archivo de código local para que el agente pueda analizarlo."""
    try:
        if not os.path.exists(nombre_archivo):
            return f"ERROR: El archivo {nombre_archivo} no existe en el directorio actual."

        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        return f"CONTENIDO DE {nombre_archivo}:\n\n{contenido}"
    except Exception as e:
        return f"ERROR al leer el archivo: {str(e)}"


@tool
def guardar_archivo_codigo(nombre_archivo: str, contenido: str) -> str:
    """Crea o reemplaza un archivo de código local con contenido corregido u optimizado."""
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"ÉXITO: Archivo {nombre_archivo} guardado y actualizado correctamente."
    except Exception as e:
        return f"ERROR al guardar el archivo: {str(e)}"