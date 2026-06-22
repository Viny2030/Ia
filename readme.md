# 🤖 Asistente Agéntico de Programación

Agente IA con LangGraph + Groq (Llama 3.3 70B) que actúa como tu asistente de programación personal con interfaz web en tiempo real.

## Capacidades

| Herramienta | Descripción |
|---|---|
| 📄 `leer_archivo_codigo` | Lee cualquier archivo del proyecto |
| 💾 `guardar_archivo_codigo` | Crea o corrige archivos |
| ▶️ `ejecutar_codigo_python` | Ejecuta código en tiempo real |
| 🔍 `buscar_documentacion` | Busca en PyPI, Python Docs y Stack Overflow |
| 🔬 `analizar_stacktrace` | Diagnostica errores y sugiere correcciones |
| 🧪 `generar_tests_unitarios` | Genera tests pytest automáticamente |
| 📁 `listar_archivos_proyecto` | Muestra la estructura del proyecto |

## Setup

```bash
# 1. Clonar el repo
git clone https://github.com/Viny2030/Ia.git
cd Ia

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY

# 4. Correr
python app.py
```

Abrir en el browser: `http://localhost:8000`

## Obtener GROQ_API_KEY

1. Ir a [console.groq.com](https://console.groq.com)
2. Crear cuenta gratuita
3. Generar API key
4. Pegar en el `.env`

## Stack

- **LLM**: Llama 3.3 70B vía Groq (gratuito)
- **Framework agéntico**: LangGraph
- **Backend**: FastAPI + WebSocket
- **Frontend**: HTML/CSS/JS puro (sin dependencias)