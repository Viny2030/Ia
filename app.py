# =====================================================================
# FILENAME: app.py
# =====================================================================
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from grafo import workflow

# 1. Cargar las variables de entorno
load_dotenv()

# 2. Compilar el flujo de trabajo con persistencia en memoria
memoria = MemorySaver()
app_agente = workflow.compile(checkpointer=memoria)

def ejecutar_auditoria_agente(entidad: str):
    print(f"=== INICIANDO AGENTE DE AUDITORÍA PARA: {entidad} ===\n")
    
    # ESTADO INICIAL (Unificado en un solo renglón continuo sin saltos)
    estado_inicial = {
        "messages": [("user", f"Realiza una investigación completa de riesgo sobre la entidad: {entidad}")],
        "entidad_investigada": entidad,
        "score_riesgo_calculado": 0.0,
        "alerta_critica": False
    }
    
    config = {"configurable": {"thread_id": f"hilo_{entidad.lower()}"}}
    
    for evento in app_agente.stream(estado_inicial, config, stream_mode="values"):
        if "messages" in evento:
            ultimo_mensaje = evento["messages"][-1]
            if hasattr(ultimo_mensaje, "content") and ultimo_mensaje.content:
                print(f"[Agente]: {ultimo_mensaje.content}\n")
                
    estado_final = app_agente.get_state(config).values
    print("=== RESULTADO FINAL DE CONTROL DE CALIDAD ===")
    print(f"Score de Riesgo Asignado: {estado_final.get('score_riesgo_calculado')}")
    print(f"¿Se disparó Alerta Crítica?: {estado_final.get('alerta_critica')}")

if __name__ == "__main__":
    entidad_a_testear = "Empresa_Fantasma_S.A."
    ejecutar_auditoria_agente(entidad_a_testear)
