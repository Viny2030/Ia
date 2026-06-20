# =====================================================================
# FILENAME: app.py
# =====================================================================
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from grafo import workflow

# 1. Cargar las variables de entorno (.env) antes de importar o compilar
load_dotenv()

# 2. Compilar el flujo de trabajo incluyendo el sistema de persistencia en memoria
# Esto permite simular hilos de conversación separados (threads)
memoria = MemorySaver()
app_agente = workflow.compile(checkpointer=memoria)

def ejecutar_auditoria_agente(entidad: str):
    print(f"=== INICIANDO AGENTE DE AUDITORÍA PARA: {entidad} ===\n")
    
    # ESTADO INICIAL (Corregido en una sola línea continua para evitar el SyntaxError)
    estado_inicial = {
        "messages": [("user", f"Realiza una investigación completa de riesgo sobre la entidad: {entidad}")],
        "entidad_investigada": entidad,
        "score_riesgo_calculado": 0.0,
        "alerta_critica": False
    }
    
    # Configuración de ID de hilo para persistencia de memoria
    config = {"configurable": {"thread_id": f"hilo_{entidad.lower()}"}}
    
    # Streaming de la ejecución paso a paso en la consola de Git Bash / PyCharm
    for evento in app_agente.stream(estado_inicial, config, stream_mode="values"):
        if "messages" in evento:
            ultimo_mensaje = evento["messages"][-1]
            # Si el mensaje contiene texto impreso por el cerebro o las herramientas
            if hasattr(ultimo_mensaje, "content") and ultimo_mensaje.content:
                print(f"[Agente]: {ultimo_mensaje.content}\n")
                
    # Extraer los metadatos agregados de forma determinista en el nodo de Auditoría Interna
    estado_final = app_agente.get_state(config).values
    print("=== RESULTADO FINAL DE CONTROL DE CALIDAD ===")
    print(f"Score de Riesgo Asignado: {estado_final.get('score_riesgo_calculado')}")
    print(f"¿Se disparó Alerta Crítica?: {estado_final.get('alerta_critica')}")

if __name__ == "__main__":
    # Entidad de prueba para verificar que el grafo ejecute sus ramificaciones
    entidad_a_testear = "Empresa_Fantasma_S.A."
    ejecutar_auditoria_agente(entidad_a_testear)
