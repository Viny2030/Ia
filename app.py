# =====================================================================
# FILENAME: app.py — Asistente Agéntico de Programación
# Web app con FastAPI + WebSocket para streaming en tiempo real
# =====================================================================
import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from grafo import workflow

load_dotenv()

app = FastAPI(title="Asistente Agéntico de Programación", version="2.0")

# Compilar el grafo con memoria persistente
memoria = MemorySaver()
agente = workflow.compile(checkpointer=memoria)

# Sesiones activas por thread_id
sesiones: dict[str, list] = {}


def leer_frontend() -> str:
    """Lee el archivo frontend.html para servirlo."""
    ruta = os.path.join(os.path.dirname(__file__), "frontend.html")
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def raiz():
    """Sirve la interfaz web principal."""
    return HTMLResponse(content=leer_frontend())


@app.get("/health")
async def health():
    """Health check para Railway."""
    return {"status": "ok", "agente": "Asistente de Programación v2.0"}


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint para chat en tiempo real con streaming.
    Cada sesión mantiene su propio historial de conversación.
    """
    await websocket.accept()
    config = {"configurable": {"thread_id": session_id}}

    try:
        while True:
            # Recibir mensaje del usuario
            data = await websocket.receive_text()
            payload = json.loads(data)
            mensaje_usuario = payload.get("mensaje", "").strip()

            if not mensaje_usuario:
                continue

            # Notificar que el agente está procesando
            await websocket.send_text(json.dumps({
                "tipo": "thinking",
                "contenido": "🤖 Procesando tu solicitud..."
            }))

            estado_inicial = {
                "messages": [HumanMessage(content=mensaje_usuario)]
            }

            # Streaming del grafo
            try:
                async for evento in agente.astream(
                    estado_inicial, config, stream_mode="values"
                ):
                    if "messages" not in evento:
                        continue

                    ultimo = evento["messages"][-1]

                    # Mensaje de herramienta siendo usada
                    if hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
                        for tc in ultimo.tool_calls:
                            nombre = tc.get("name", "herramienta")
                            ICONOS = {
                                "leer_archivo_codigo": "📄",
                                "guardar_archivo_codigo": "💾",
                                "ejecutar_codigo_python": "▶️",
                                "buscar_documentacion": "🔍",
                                "analizar_stacktrace": "🔬",
                                "generar_tests_unitarios": "🧪",
                                "listar_archivos_proyecto": "📁",
                            }
                            icono = ICONOS.get(nombre, "🔧")
                            await websocket.send_text(json.dumps({
                                "tipo": "tool_use",
                                "contenido": f"{icono} Usando: {nombre.replace('_', ' ').title()}"
                            }))

                    # Resultado de herramienta
                    elif isinstance(ultimo, ToolMessage):
                        await websocket.send_text(json.dumps({
                            "tipo": "tool_result",
                            "contenido": ultimo.content[:500] + ("..." if len(ultimo.content) > 500 else "")
                        }))

                    # Respuesta final del agente
                    elif (
                        hasattr(ultimo, "type") and ultimo.type == "ai"
                        and hasattr(ultimo, "content") and ultimo.content
                        and not (hasattr(ultimo, "tool_calls") and ultimo.tool_calls)
                    ):
                        await websocket.send_text(json.dumps({
                            "tipo": "respuesta",
                            "contenido": ultimo.content
                        }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "tipo": "error",
                    "contenido": f"❌ Error del agente: {str(e)}"
                }))

            # Señal de fin de respuesta
            await websocket.send_text(json.dumps({"tipo": "fin"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "tipo": "error",
                "contenido": f"❌ Error de conexión: {str(e)}"
            }))
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
