from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from herramientas import extraer_datos_entidad, verificar_red_vinculos
# 1. Definición del Estado Central
class EstadoAgente(TypedDict):
messages: Annotated[Sequence[BaseMessage], add_messages]
entidad_investigada: str
score_riesgo_calculado: float
alerta_critica: bool
# 2. Definición de los Nodos del Sistema
def nodo_cerebro(state: EstadoAgente):
"""Nodo del LLM que decide de forma lógica la siguiente acción o herramienta a usar."""
# Vinculamos las herramientas disponibles al modelo de lenguaje
herramientas = [extraer_datos_entidad, verificar_red_vinculos]
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(herramientas)
response = model.invoke(state["messages"])
return {"messages": [response]}
def nodo_auditoria_interna(state: EstadoAgente):
"""Nodo determinista de control de calidad. Evalúa los resultados obtenidos antes del
cierre."""
historial_texto = "\n".join([m.content for m in state["messages"] if isinstance(m.content,
str)])
# Lógica analítica pura (No controlada por el LLM)

2

4. Archivo de Ejecución Principal
app.py
Orquesta la inicialización del estado, carga las variables del entorno y ejecuta el hilo de ejecución mostrando el
pensamiento del agente en tiempo real.
score = 0.0
if "desviacion_precios_promedio" in historial_texto:
score += 0.50
if "Empresa_Fantasma_S.A." in historial_texto:
score += 0.40
return {
"score_riesgo_calculado": score,
"alerta_critica": True if score >= 0.70 else False
}
# 3. Construcción del Flujo de Trabajo (Workflow)
workflow = StateGraph(EstadoAgente)
workflow.add_node("cerebro", nodo_cerebro)
workflow.add_node("herramientas", ToolNode([extraer_datos_entidad, verificar_red_vinculos]))
workflow.add_node("auditoria", nodo_auditoria_interna)
# Mapeo de conexiones
workflow.add_edge(START, "cerebro")
workflow.add_conditional_edges(
"cerebro",
tools_condition,
{"tools": "herramientas", "__end__": "auditoria"}
)
workflow.add_edge("herramientas", "cerebro")
workflow.add_edge("auditoria", END)
# Compilación final del agente
app_agente = workflow.compile()
