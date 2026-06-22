# =====================================================================
# FILENAME: herramientas.py — Asistente Agéntico de Programación
# Capacidades: leer/escribir archivos, ejecutar código, buscar docs,
#              analizar stacktraces, generar tests, multi-archivo
# =====================================================================
import os
import sys
import subprocess
import traceback
import tempfile
import httpx
from langchain_core.tools import tool


# ── 1. LEER ARCHIVO ──────────────────────────────────────────────────
@tool
def leer_archivo_codigo(nombre_archivo: str) -> str:
    """Lee el contenido de un archivo de código local para que el agente pueda analizarlo."""
    try:
        if not os.path.exists(nombre_archivo):
            return f"ERROR: El archivo '{nombre_archivo}' no existe en el directorio actual."
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        lineas = contenido.count('\n') + 1
        return f"ARCHIVO: {nombre_archivo} ({lineas} líneas)\n\n{contenido}"
    except Exception as e:
        return f"ERROR al leer '{nombre_archivo}': {str(e)}"


# ── 2. GUARDAR ARCHIVO ────────────────────────────────────────────────
@tool
def guardar_archivo_codigo(nombre_archivo: str, contenido: str) -> str:
    """Crea o reemplaza un archivo de código con el contenido proporcionado."""
    try:
        # Crear directorios si no existen
        directorio = os.path.dirname(nombre_archivo)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        lineas = contenido.count('\n') + 1
        return f"ÉXITO: '{nombre_archivo}' guardado correctamente ({lineas} líneas)."
    except Exception as e:
        return f"ERROR al guardar '{nombre_archivo}': {str(e)}"


# ── 3. EJECUTAR CÓDIGO PYTHON ─────────────────────────────────────────
@tool
def ejecutar_codigo_python(codigo: str, timeout: int = 15) -> str:
    """
    Ejecuta un bloque de código Python en un entorno aislado y devuelve
    stdout, stderr y el resultado. Ideal para probar snippets o scripts cortos.
    Timeout máximo: 15 segundos.
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(codigo)
            tmp_path = tmp.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        os.unlink(tmp_path)

        salida = []
        if result.stdout:
            salida.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            salida.append(f"STDERR:\n{result.stderr}")
        salida.append(f"Código de retorno: {result.returncode}")

        return "\n".join(salida) if salida else "Ejecución exitosa (sin salida)."

    except subprocess.TimeoutExpired:
        return f"ERROR: Tiempo de ejecución excedido ({timeout}s). El código puede tener un loop infinito."
    except Exception as e:
        return f"ERROR al ejecutar el código: {str(e)}"


# ── 4. BUSCAR DOCUMENTACIÓN ───────────────────────────────────────────
@tool
def buscar_documentacion(query: str) -> str:
    """
    Busca documentación técnica en PyPI, Python Docs y Stack Overflow
    para una librería, función o concepto de programación.
    """
    resultados = []

    # Buscar en PyPI
    try:
        pkg = query.split()[0].lower()
        r = httpx.get(f"https://pypi.org/pypi/{pkg}/json", timeout=8)
        if r.status_code == 200:
            data = r.json()["info"]
            resultados.append(
                f"📦 PyPI — {data['name']} v{data['version']}\n"
                f"   {data.get('summary','Sin descripción')}\n"
                f"   Docs: {data.get('project_urls',{}).get('Documentation','') or data.get('home_page','')}"
            )
    except Exception:
        pass

    # Buscar en Python Docs (búsqueda simple)
    try:
        r = httpx.get(
            "https://docs.python.org/3/search.html",
            params={"q": query, "check_keywords": "yes", "area": "default"},
            timeout=6
        )
        if r.status_code == 200:
            resultados.append(f"📖 Python Docs: https://docs.python.org/3/search.html?q={query.replace(' ','+')}")
    except Exception:
        pass

    # Buscar en Stack Overflow via API
    try:
        r = httpx.get(
            "https://api.stackexchange.com/2.3/search/advanced",
            params={
                "order": "desc", "sort": "relevance",
                "q": query, "site": "stackoverflow",
                "pagesize": 3, "filter": "withbody"
            },
            timeout=8
        )
        if r.status_code == 200:
            items = r.json().get("items", [])[:3]
            if items:
                resultados.append("💬 Stack Overflow — Preguntas relevantes:")
                for item in items:
                    score = item.get("score", 0)
                    answered = "✅" if item.get("is_answered") else "❓"
                    resultados.append(
                        f"   {answered} [{score} votos] {item['title']}\n"
                        f"      {item['link']}"
                    )
    except Exception:
        pass

    if not resultados:
        return f"No se encontraron resultados para '{query}'. Intentá con términos más específicos."

    return f"DOCUMENTACIÓN PARA: '{query}'\n\n" + "\n\n".join(resultados)


# ── 5. ANALIZAR STACKTRACE ────────────────────────────────────────────
@tool
def analizar_stacktrace(stacktrace: str) -> str:
    """
    Analiza un stacktrace o mensaje de error de Python e identifica:
    - Tipo de error y causa raíz
    - Archivo y línea del problema
    - Sugerencias de corrección
    """
    if not stacktrace.strip():
        return "ERROR: No se proporcionó ningún stacktrace para analizar."

    lineas = stacktrace.strip().split('\n')
    analisis = ["🔍 ANÁLISIS DE STACKTRACE\n"]

    # Detectar tipo de error
    tipo_error = None
    mensaje_error = None
    archivo_error = None
    linea_error = None

    for linea in reversed(lineas):
        linea = linea.strip()
        # Buscar línea de error final (ej: "ValueError: ...")
        if ':' in linea and not linea.startswith('File') and not linea.startswith('Traceback'):
            partes = linea.split(':', 1)
            if partes[0].strip().replace('Error','').replace('Exception','').isalpha() or 'Error' in partes[0] or 'Exception' in partes[0]:
                tipo_error = partes[0].strip()
                mensaje_error = partes[1].strip() if len(partes) > 1 else ''
                break

    # Buscar archivo y línea
    for linea in lineas:
        if 'File "' in linea and ', line ' in linea:
            try:
                archivo_error = linea.split('File "')[1].split('"')[0]
                linea_error = linea.split(', line ')[1].split(',')[0]
            except Exception:
                pass

    if tipo_error:
        analisis.append(f"❌ Tipo de error: {tipo_error}")
    if mensaje_error:
        analisis.append(f"💬 Mensaje: {mensaje_error}")
    if archivo_error:
        analisis.append(f"📄 Archivo: {archivo_error}")
    if linea_error:
        analisis.append(f"📍 Línea: {linea_error}")

    # Sugerencias por tipo de error
    analisis.append("\n💡 SUGERENCIAS:")
    sugerencias = {
        "ImportError": "Verificá que el paquete esté instalado: `pip install <nombre_paquete>`",
        "ModuleNotFoundError": "El módulo no existe o no está instalado. Revisá el nombre y ejecutá `pip install`.",
        "NameError": "Estás usando una variable o función que no fue definida. Verificá el nombre y el scope.",
        "TypeError": "Estás pasando un tipo de dato incorrecto. Verificá los tipos esperados por la función.",
        "ValueError": "El valor pasado es del tipo correcto pero no válido para esa operación.",
        "AttributeError": "Estás accediendo a un atributo que no existe en ese objeto. Revisá la documentación.",
        "IndexError": "Estás accediendo a un índice fuera del rango de la lista/array.",
        "KeyError": "La clave no existe en el diccionario. Usá `.get()` para manejo seguro.",
        "FileNotFoundError": "El archivo no existe en la ruta especificada. Verificá la ruta y el directorio de trabajo.",
        "ZeroDivisionError": "División por cero. Agregá una validación antes de dividir.",
        "SyntaxError": "Error de sintaxis. Verificá indentación, paréntesis y dos puntos faltantes.",
        "IndentationError": "Error de indentación. Usá espacios consistentes (4 espacios recomendado).",
        "RecursionError": "Recursión infinita. Verificá el caso base de tu función recursiva.",
        "MemoryError": "Sin memoria disponible. Optimizá el uso de datos o procesá en chunks.",
        "TimeoutError": "Operación tomó demasiado tiempo. Revisá loops y operaciones de red.",
    }

    sugerencia_encontrada = False
    for error_tipo, sugerencia in sugerencias.items():
        if tipo_error and error_tipo.lower() in tipo_error.lower():
            analisis.append(f"→ {sugerencia}")
            sugerencia_encontrada = True

    if not sugerencia_encontrada:
        analisis.append("→ Revisá la línea indicada en el traceback y verificá la lógica de tu código.")
        analisis.append("→ Agregá prints de depuración alrededor del error para ver el estado de las variables.")

    return "\n".join(analisis)


# ── 6. GENERAR TESTS UNITARIOS ────────────────────────────────────────
@tool
def generar_tests_unitarios(nombre_archivo: str) -> str:
    """
    Lee un archivo Python y genera un archivo de tests unitarios usando pytest
    para todas las funciones y clases encontradas.
    """
    try:
        if not os.path.exists(nombre_archivo):
            return f"ERROR: El archivo '{nombre_archivo}' no existe."

        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Extraer funciones y clases
        import ast
        try:
            tree = ast.parse(contenido)
        except SyntaxError as e:
            return f"ERROR: El archivo tiene un error de sintaxis: {e}"

        funciones = []
        clases = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                args = [a.arg for a in node.args.args]
                funciones.append((node.name, args))
            elif isinstance(node, ast.ClassDef):
                metodos = [
                    (n.name, [a.arg for a in n.args.args])
                    for n in ast.walk(node)
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')
                ]
                clases.append((node.name, metodos))

        if not funciones and not clases:
            return "No se encontraron funciones o clases públicas para testear."

        # Nombre del módulo sin extensión
        modulo = os.path.splitext(os.path.basename(nombre_archivo))[0]
        test_nombre = f"test_{modulo}.py"

        # Generar contenido del archivo de tests
        imports = f"# Tests generados automáticamente para {nombre_archivo}\n"
        imports += f"import pytest\n"
        imports += f"from {modulo} import *\n\n\n"

        tests = []

        for func_name, args in funciones:
            args_sin_self = [a for a in args if a != 'self']
            args_ejemplo = ', '.join(['None'] * len(args_sin_self))
            tests.append(
                f"def test_{func_name}_existe():\n"
                f"    \"\"\"Verifica que {func_name} existe y es callable.\"\"\"\n"
                f"    assert callable({func_name})\n\n"
                f"def test_{func_name}_basico():\n"
                f"    \"\"\"Test básico para {func_name}({', '.join(args_sin_self)}).\"\"\"\n"
                f"    # TODO: completar con valores reales\n"
                f"    # resultado = {func_name}({args_ejemplo})\n"
                f"    # assert resultado == <valor_esperado>\n"
                f"    pass\n"
            )

        for clase_name, metodos in clases:
            tests.append(
                f"class Test{clase_name}:\n"
                f"    def test_instancia(self):\n"
                f"        \"\"\"Verifica que {clase_name} se puede instanciar.\"\"\"\n"
                f"        # obj = {clase_name}()\n"
                f"        # assert obj is not None\n"
                f"        pass\n"
            )
            for metodo_name, metodo_args in metodos:
                args_sin_self = [a for a in metodo_args if a != 'self']
                tests.append(
                    f"    def test_{metodo_name}(self):\n"
                    f"        \"\"\"Test para {clase_name}.{metodo_name}.\"\"\"\n"
                    f"        # TODO: completar\n"
                    f"        pass\n"
                )

        contenido_tests = imports + "\n\n".join(tests)

        with open(test_nombre, "w", encoding="utf-8") as f:
            f.write(contenido_tests)

        resumen = f"✅ Tests generados en '{test_nombre}':\n"
        if funciones:
            resumen += f"   • {len(funciones)} función(es): {', '.join(f[0] for f in funciones)}\n"
        if clases:
            resumen += f"   • {len(clases)} clase(s): {', '.join(c[0] for c in clases)}\n"
        resumen += f"\nEjecutá con: pytest {test_nombre} -v"

        return resumen + f"\n\nCONTENIDO DE {test_nombre}:\n\n{contenido_tests}"

    except Exception as e:
        return f"ERROR al generar tests: {str(e)}\n{traceback.format_exc()}"


# ── 7. LISTAR ARCHIVOS DEL PROYECTO ──────────────────────────────────
@tool
def listar_archivos_proyecto(directorio: str = ".") -> str:
    """
    Lista todos los archivos de código del proyecto (py, js, ts, html, css, json, yaml, etc.)
    con su tamaño. Útil para entender la estructura del proyecto antes de trabajar.
    """
    extensiones = {'.py', '.js', '.ts', '.html', '.css', '.json', '.yaml', '.yml',
                   '.toml', '.txt', '.md', '.sh', '.sql', '.env.example', '.cfg', '.ini'}
    ignorar = {'__pycache__', '.git', '.venv', 'venv', 'node_modules', '.pytest_cache',
               'dist', 'build', '.mypy_cache', '.ruff_cache'}

    archivos_encontrados = []

    try:
        for root, dirs, files in os.walk(directorio):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in ignorar]

            for archivo in sorted(files):
                _, ext = os.path.splitext(archivo)
                if ext.lower() in extensiones:
                    ruta = os.path.join(root, archivo)
                    try:
                        size = os.path.getsize(ruta)
                        size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024} KB"
                        archivos_encontrados.append(f"  {ruta} ({size_str})")
                    except Exception:
                        archivos_encontrados.append(f"  {ruta}")

        if not archivos_encontrados:
            return f"No se encontraron archivos de código en '{directorio}'."

        return (
            f"📁 PROYECTO EN '{directorio}' — {len(archivos_encontrados)} archivo(s):\n\n"
            + "\n".join(archivos_encontrados)
        )

    except Exception as e:
        return f"ERROR al listar archivos: {str(e)}"


# Lista exportable de todas las herramientas
TODAS_LAS_HERRAMIENTAS = [
    leer_archivo_codigo,
    guardar_archivo_codigo,
    ejecutar_codigo_python,
    buscar_documentacion,
    analizar_stacktrace,
    generar_tests_unitarios,
    listar_archivos_proyecto,
]