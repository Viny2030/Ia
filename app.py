# =====================================================================
# FILENAME: app.py (Versión Asistente de Programación)
# =====================================================================
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from grafo import workflow

load_dotenv()

memoria = MemorySaver()
asistente_ia = workflow.compile(checkpointer=memoria)


def chat_con_asistente():
    print("=========================================================")
    print("🤖 BIENVENIDO A TU ASISTENTE AGÉNTICO DE PROGRAMACIÓN 🤖")
    print("Escribí tu consulta (o 'salir' para terminar el chat)")
    print("=========================================================\n")

    config = {"configurable": {"thread_id": "sesion_programacion_1"}}

    while True:
        entrada_usuario = input("👨‍💻 Tu solicitud: ")
        if entrada_usuario.lower() in ["salir", "exit", "quit"]:
            print("¡Nos vemos! Éxito en tu código.")
            break

        estado_inicial = {
            "messages": [("user", entrada_usuario)]
        }

        # Ejecutamos el flujo en streaming
        for evento in asistente_ia.stream(estado_inicial, config, stream_mode="values"):
            if "messages" in evento:
                ultimo_mensaje = evento["messages"][-1]

                # CORRECCIÓN: Primero verificamos si es un mensaje de la IA
                if getattr(ultimo_mensaje, "type", "") == "ai":
                    # Ahora sí es seguro revisar content y tool_calls de forma aislada
                    if hasattr(ultimo_mensaje, "content") and ultimo_mensaje.content:
                        # Si la IA no está llamando herramientas, es su respuesta final en texto
                        if not hasattr(ultimo_mensaje, "tool_calls") or not ultimo_mensaje.tool_calls:
                            print(f"\n🤖 [Asistente]: {ultimo_mensaje.content}\n")


if __name__ == "__main__":
    chat_con_asistente()
