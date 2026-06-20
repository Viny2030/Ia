import os
from grafo import app_agente
def ejecutar_auditoria_agente(entidad: str):
print(f"=== INICIANDO AGENTE DE AUDITORÍA PARA: {entidad} ===\n")
# Estado inicial enviado al Grafo
estado_inicial = {
"messages": [("user", f"Realiza una investigación completa de riesgo sobre la entidad:
{entidad}")],
"entidad_investigada": entidad,
"score_riesgo_calculado": 0.0,
"alerta_critica": False
}
# Configuración de ID de hilo para persistencia de memoria

3

Recomendación Técnica: Coloca estos 4 archivos dentro de la misma carpeta raíz en tu espacio de trabajo local
en PyCharm. Al ejecutar python app.py, verás cómo interactúan dinámicamente el cerebro y tus funciones de
datos.
config = {"configurable": {"thread_id": f"hilo_{entidad.lower()}"}}
# Streaming de la ejecución paso a paso en consola
for evento in app_agente.stream(estado_inicial, config, stream_mode="values"):
if "messages" in evento:
ultimo_mensaje = evento["messages"][-1]
if hasattr(ultimo_mensaje, "content") and ultimo_mensaje.content:
print(f"[Agente]: {ultimo_mensaje.content}\n")
# Extraer el estado final consolidado
estado_final = app_agente.get_state(config).values
print("=== RESULTADO FINAL DE CONTROL DE CALIDAD ===")
print(f"Score de Riesgo Asignado: {estado_final.get('score_riesgo_calculado')}")
print(f"¿Se disparó Alerta Crítica?: {estado_final.get('alerta_critica')}")
if __name__ == "__main__":
# Asegúrate de configurar tu API Key antes de ejecutar
# os.environ["OPENAI_API_KEY"] = "tu_clave"
entidad_a_testear = "Proveedor_Corporativo_Alfa"
ejecutar_auditoria_agente(entidad_a_testear)
