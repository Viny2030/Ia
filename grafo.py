# =====================================================================
# FILENAME: grafo.py — Asistente Agéntico de Programación
# =====================================================================
import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from herramientas import TODAS_LAS_HERRAMIENTAS

load_dotenv()


class EstadoProgramador(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


SYSTEM_PROMPT = """Sos un agente IA asistente de programación experto en Python, Data Science y desarrollo de software.

TUS HERRAMIENTAS DISPONIBLES:
• leer_archivo_codigo — Para leer cualquier archivo del proyecto
• guardar_archivo_codigo — Para crear o corregir archivos
• ejecutar_codigo_python — Para probar código en tiempo real y ver resultados
• buscar_documentacion — Para buscar en PyPI, Python Docs y Stack Overflow
• analizar_stacktrace — Para diagnosticar errores y stacktraces
• generar_tests_unitarios — Para crear tests pytest automáticamente
• listar_archivos_proyecto — Para ver la estructura del proyecto

TU FORMA DE TRABAJAR:
1. Primero entendé el problema completamente
2. Si necesitás ver código existente, usá leer_archivo_codigo
3. Si el usuario pega un error, usá analizar_stacktrace para diagnosticarlo
4. Ejecutá código para verificar que tus soluciones funcionan antes de guardarlas
5. Siempre explicá QUÉ hiciste y POR QUÉ, con el código relevante
6. Generá tests cuando entregues código nuevo

REGLAS:
- Respondé siempre en español
- Código limpio, con type hints y docstrings
- Si no podés resolver algo, explicá por qué y sugerí alternativas
- Nunca ejecutes código destructivo (borrar archivos, rm -rf, etc.)
"""


def nodo_desarrollador(state: EstadoProgramador):
    """Nodo principal del agente que razona y decide qué herramientas usar."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no encontrada en las variables de entorno.")

    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=api_key,
        max_tokens=4096,
    ).bind_tools(TODAS_LAS_HERRAMIENTAS)

    instrucciones = SystemMessage(content=SYSTEM_PROMPT)
    mensajes = [instrucciones] + list(state["messages"])
    response = model.invoke(mensajes)
    return {"messages": [response]}


def enrutador(state: EstadoProgramador):
    """Decide si el agente necesita usar herramientas o ya terminó."""
    ultimo = state["messages"][-1]
    if hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
        return "herramientas"
    return END


# ── Construcción del grafo ────────────────────────────────────────────
workflow = StateGraph(EstadoProgramador)

workflow.add_node("desarrollador", nodo_desarrollador)
workflow.add_node("herramientas", ToolNode(TODAS_LAS_HERRAMIENTAS))

workflow.add_edge(START, "desarrollador")
workflow.add_conditional_edges(
    "desarrollador",
    enrutador,
    {"herramientas": "herramientas", END: END}
)
workflow.add_edge("herramientas", "desarrollador")