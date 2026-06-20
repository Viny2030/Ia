# =====================================================================
# FILENAME: grafo.py
# =====================================================================
import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from herramientas import extraer_datos_entidad, verificar_red_vinculos

# Forzamos la lectura del archivo .env local antes de configurar el modelo
load_dotenv()

# 1. Definición del Estado Central del Agente
class EstadoAgente(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    entidad_investigada: str
    score_riesgo_calculado: float
    alerta_critica: bool

# 2. Definición de los Nodos del Grafo
def nodo_cerebro(state: EstadoAgente):
    """Nodo del LLM (GPT-4o) que analiza la situación y decide si llama herramientas

    o si ya posee suficiente información para concluir."""
    herramientas = [extraer_datos_entidad, verificar_red_vinculos]
    
    # Extraemos explícitamente la API Key del entorno local
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Inicializamos el modelo pasando la key directamente para asegurar autenticación
    model = ChatOpenAI(
        model="gpt-4o", 
        temperature=0, 
        openai_api_key=api_key
    ).bind_tools(herramientas)
    
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def nodo_auditoria_interna(state: EstadoAgente):
    """Nodo determinista de control de calidad. Evalúa el historial del flujo

    y calcula de forma rígida el score de riesgo final."""
    historial_texto = "\n".join([
        m.content for m in state["messages"] 
        if isinstance(m.content, str)
    ])
    
    score = 0.0
    # Reglas rígidas basadas en el texto obtenido por las herramientas
    if "desviacion_precios_promedio" in historial_texto:
        score += 0.50
    if "Empresa_Fantasma_S.A." in historial_texto:
        score += 0.40
        
    return {
        "score_riesgo_calculado": score,
        "alerta_critica": True if score >= 0.70 else False
    }

# 3. Función del Enrutador Condicional
def enrutador_cerebro(state: EstadoAgente):
    """Analiza si el último mensaje del cerebro exige llamados a funciones (tools)

    o si debe derivar al control de calidad final."""
    ultimo_mensaje = state["messages"][-1]
    
    # Si el modelo estructuró llamados a herramientas, viajamos al nodo de ejecución tool
    if ultimo_mensaje.tool_calls:
        return "herramientas"
    
    # Si no hay llamadas pendientes, pasamos obligatoriamente por la auditoría interna
    return "auditoria"

# 4. Construcción Estructural del Flujo de Trabajo (Workflow)
workflow = StateGraph(EstadoAgente)

# Registro de Nodos en la estructura
workflow.add_node("cerebro", nodo_cerebro)
workflow.add_node("herramientas", ToolNode([extraer_datos_entidad, verificar_red_vinculos]))
workflow.add_node("auditoria", nodo_auditoria_interna)

# Mapeo de Conexiones y Saltos Logicos
workflow.add_edge(START, "cerebro")

# Aplicación del enrutador condicional personalizado
workflow.add_conditional_edges(
    "cerebro",
    enrutador_cerebro,
    {
        "herramientas": "herramientas",
        "auditoria": "auditoria"
    }
)

# El nodo de herramientas retorna el control al cerebro para evaluar los nuevos datos
workflow.add_edge("herramientas", "cerebro")

# La auditoría determina la salida definitiva del proceso
workflow.add_edge("auditoria", END)
