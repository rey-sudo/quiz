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
    if not prompts:
        return None 

    respuesta = None

    for i, prompt in enumerate(prompts):
        print(f"\n--- Ejecutando prompt {i+1} ---")
        
        es_ultimo = i == len(prompts) - 1
        
        if es_ultimo:
            print("✅ Esta es la última iteración")
            respuesta = chat.preguntar(prompt, True, False)
        else:
            respuesta = chat.preguntar(prompt, True)
            
    print(respuesta)
    
    return respuesta
        

 
            
def get_article_files() -> list[dict]:
    """
    Lee ordenadamente todos los archivos .md de un directorio,
    ordenados por el número antes del .md
    """
    patron = os.path.join("output/articles", "*.md")
    archivos = sorted(
        glob.glob(patron),
        key=lambda x: int(re.search(r'(\d+)(?=\.md$)', x).group())
    )

    resultados = []

    for ruta in archivos:
        nombre = os.path.basename(ruta)

        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()

        resultados.append({
            "nombre": nombre,
            "ruta": ruta,
            "contenido": contenido
        })

    print(f"[DEBUG] Total de archivos leídos: {len(resultados)}")
    return resultados

def extraer_contexto(n: int = 3) -> str:
    """
    Reads the first n .md articles from the output directory and
    combines them into a single string.

    Args:
        n: Number of articles to include (default: 3)

    Returns:
        A string containing the combined content of the first n articles
    """
    # Retrieve all available article files
    resultados = get_article_files()
    
    # Select the first n articles
    articles_files = resultados[:n]
    
    # Initialize the context string
    contexto = ""
    
    # Iterate over the selected articles
    for file in articles_files:
        print(f"[DEBUG] Agregando al contexto: {file['nombre']}")
        contexto += f"\n\n--- {file['nombre']} ---\n\n"
        contexto += file["contenido"]
    
    print(f"[DEBUG] Contexto generado con {len(articles_files)} artículos ({len(contexto)} caracteres)")
    return contexto   
    
    
def process_articles():
    """
    Iterates through all .md articles in an ordered way
    and processes them one by one.
    
    
    """
    # Retrieve the list of article files
    article_files = get_article_files()
    
    # Extract contextual information (e.g., first 3 articles)
    context = extraer_contexto(n=3)
    
     # Loop through each article file
    for file in article_files:
        tecla = input(f"\n¿Procesar '{file['nombre']}'? [y/n]: ").strip().lower()
        if tecla != "y":
            print(f"[DEBUG] Saltando: {file['nombre']}")
            continue
        
        print(f"[DEBUG] Procesando: {file['nombre']}")

        contenido = file["contenido"]
        
        prompts = get_create_questions_prompt(context, contenido)
        
        process_article(prompts) 
        
        