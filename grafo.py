# =====================================================================
# FILENAME: grafo.py (Versión Asistente de Programación)
# =====================================================================
import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from herramientas import leer_archivo_codigo, guardar_archivo_codigo

load_dotenv()

class EstadoProgramador(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def nodo_desarrollador(state: EstadoProgramador):
    """Cerebro del agente que analiza tus dudas de código y decide qué herramientas usar."""
    herramientas = [leer_archivo_codigo, guardar_archivo_codigo]
    api_key = os.getenv("GROQ_API_KEY")

    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2, # Un toque de temperatura para darle creatividad resolviendo problemas
        groq_api_key=api_key
    ).bind_tools(herramientas)

    # Instrucciones específicas de programación
    instrucciones = SystemMessage(
        content="Sos un agente IA asistente de programación experto en Python y Data Science. "
                "Tu objetivo es ayudar al usuario a escribir código limpio, eficiente y corregir errores. "
                "Si necesitás ver el código de un archivo local para entender el problema, usá 'leer_archivo_codigo'. "
                "Si corregís un bug o creás un script útil, usá 'guardar_archivo_codigo' para dejárselo listo."
    )

    mensajes_con_guia = [instrucciones] + list(state["messages"])
    response = model.invoke(mensajes_con_guia)
    return {"messages": [response]}

def enrutador_programador(state: EstadoProgramador):
    ultimo_mensaje = state["messages"][-1]
    if ultimo_mensaje.tool_calls:
        return "herramientas"
    return END

# Construcción del flujo
workflow = StateGraph(EstadoProgramador)
workflow.add_node("desarrollador", nodo_desarrollador)
workflow.add_node("herramientas", ToolNode([leer_archivo_codigo, guardar_archivo_codigo]))

workflow.add_edge(START, "desarrollador")
workflow.add_conditional_edges(
    "desarrollador",
    enrutador_programador,
    {
        "herramientas": "herramientas",
        END: END
    }
)
workflow.add_edge("herramientas", "desarrollador")