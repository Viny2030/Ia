# =====================================================================
# FILENAME: grafo.py (Versión Corregida y Optimizada)
# =====================================================================
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from herramientas import extraer_datos_entidad, verificar_red_vinculos

# 1. Definición del Estado Central
class EstadoAgente(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    entidad_investigada: str
    score_riesgo_calculado: float
    alerta_critica: bool

# 2. Definición de los Nodos del Sistema
def nodo_cerebro(state: EstadoAgente):
    """Nodo del LLM que decide de forma lógica la siguiente acción."""
    herramientas = [extraer_datos_entidad, verificar_red_vinculos]
    # Usamos temperatura 0 para garantizar un análisis analítico frío y preciso
    model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(herramientas)
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def nodo_auditoria_interna(state: EstadoAgente):
    """Nodo determinista de control de calidad. Evalúa el historial obtenido."""
    historial_texto = "\n".join([
        m.content for m in state["messages"] 
        if isinstance(m.content, str)
    ])
    
    score = 0.0
    # Reglas rígidas basadas en los outputs simulados de tus herramientas
    if "desviacion_precios_promedio" in historial_texto:
        score += 0.50
    if "Empresa_Fantasma_S.A." in historial_texto:
        score += 0.40
        
    return {
        "score_riesgo_calculado": score,
        "alerta_critica": True if score >= 0.70 else False
    }

# 3. Función del Enrutador Personalizado
def enrutador_cerebro(state: EstadoAgente):
    """Determina si se continúa ejecutando herramientas o se pasa al control de calidad."""
    ultimo_mensaje = state["messages"][-1]
    # Si el modelo solicita llamadas a funciones (tools), vamos al nodo de herramientas
    if ultimo_mensaje.tool_calls:
        return "herramientas"
    # Si no hay herramientas por llamar, pasamos a la auditoría interna antes del cierre
    return "auditoria"

# 4. Construcción del Flujo de Trabajo (Workflow)
workflow = StateGraph(EstadoAgente)

# Registro de Nodos
workflow.add_node("cerebro", nodo_cerebro)
workflow.add_node("herramientas", ToolNode([extraer_datos_entidad, verificar_red_vinculos]))
workflow.add_node("auditoria", nodo_auditoria_interna)

# Mapeo de Conexiones de Control
workflow.add_edge(START, "cerebro")

# Aplicación del enrutador condicional corregido
workflow.add_conditional_edges(
    "cerebro",
    enrutador_cerebro,
    {
        "herramientas": "herramientas",
        "auditoria": "auditoria"
    }
)

# El nodo de herramientas vuelve siempre al cerebro para evaluar el resultado
workflow.add_edge("herramientas", "cerebro")
# La auditoría pone el punto final al proceso
workflow.add_edge("auditoria", END)

# Compilación final del agente
app_agente = workflow.compile()
