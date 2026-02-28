import re
from prompts.create_questions import get_create_questions_prompt
from clients.gemini_client import GeminiChat
from clients.openai_client import OpenAIChat
from clients.ollama_client import OllamaChat
import os
import glob




SYSTEM_PROMPT = """
Eres un asistente experto en normativa colombia vigente año 2026
"""


chat = GeminiChat(
    model="gemini-2.5-flash",
    system_prompt=SYSTEM_PROMPT,
)

chat = OllamaChat(
    model='gemma3:4b',
    system_prompt=SYSTEM_PROMPT
)


def process_article(prompts: list[str]):
    for i, prompt in enumerate(prompts):
        print(f"\n--- Ejecutando prompt {i+1} ---")
        respuesta = chat.preguntar(prompt, True)
        print(respuesta)
    
    
    chat.ver_historial()


def leer_archivos_md(directorio: str = "output/articles") -> list[dict]:
    """
    Lee ordenadamente todos los archivos .md de un directorio,
    ordenados por el número antes del .md
    """
    patron = os.path.join(directorio, "*.md")
    archivos = sorted(
        glob.glob(patron),
        key=lambda x: int(re.search(r'(\d+)(?=\.md$)', x).group())
    )

    resultados = []

    for ruta in archivos:
        nombre = os.path.basename(ruta)
        print(f"[DEBUG] Leyendo archivo: {nombre}")

        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()

        resultados.append({
            "nombre": nombre,
            "ruta": ruta,
            "contenido": contenido
        })

    print(f"[DEBUG] Total de archivos leídos: {len(resultados)}")
    return resultados

def extraer_contexto(directorio: str = "output/articles", n: int = 3) -> str:
    """
    Lee los primeros n artículos .md del directorio y los une en un solo string.

    Args:
        directorio: Ruta del directorio donde buscar archivos .md
        n: Cantidad de artículos a tomar (default: 5)

    Returns:
        String con el contenido unido de los primeros n artículos
    """
    resultados = leer_archivos_md(directorio)
    primeros = resultados[:n]

    contexto = ""
    for articulo in primeros:
        print(f"[DEBUG] Agregando al contexto: {articulo['nombre']}")
        contexto += f"\n\n--- {articulo['nombre']} ---\n\n"
        contexto += articulo["contenido"]

    print(f"[DEBUG] Contexto generado con {len(primeros)} artículos ({len(contexto)} caracteres)")
    return contexto   
    
    
def process_articles(directorio: str = "output/articles"):
    """
    Itera ordenadamente todos los artículos .md y los procesa uno por uno.

    Args:
        directorio: Ruta del directorio donde buscar archivos .md
    """
    resultados = leer_archivos_md(directorio)
    
    context = extraer_contexto(n=3)
    
    for articulo in resultados:
        print(f"[DEBUG] Procesando: {articulo['nombre']}")

        nombre = articulo["nombre"]
        contenido = articulo["contenido"]
        
        promps1 = get_create_questions_prompt(context, contenido)
        
        process_article(promps1)
        
        