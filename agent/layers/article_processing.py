import json
import logging
from utils.clean_json import limpiar_json_markdown
from pydantic import ValidationError
from prompts.create_questions import questionsAdapter, get_create_questions_prompt
from clients.gemini_client import GeminiChat
from clients.openai_client import OpenAIChat
from clients.ollama_client import OllamaChat
from tenacity import retry, wait_fixed, stop_after_attempt
import os
import glob
import re

logger = logging.getLogger(__name__)

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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def save_json_file(filename: str, data: str):
    """
    Saves a JSON string as a JSON file in 'output/questions'.
    """
    try:
        output_folder = "output/questions"
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(output_folder, filename + ".json")
        
        # If data is a string, parse it into a Python object
        if isinstance(data, str):
            data = json.loads(data)
        
        # Write JSON to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON file saved at: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Failed to save JSON (attempt failed): {e}")
        raise  


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def try_output_prompt(filename: str, prompt: str):
    try:
        response = chat.preguntar(prompt, False)
        respuesta_limpia = limpiar_json_markdown(response)
    
        validated = questionsAdapter.validate_json(respuesta_limpia)
        
        print("VALIDATED")

        save_json_file(filename, respuesta_limpia)
        
        return respuesta_limpia

    except ValidationError as e:
        print("❌ Error de validación Pydantic:")
        print(e)
        print("Errores detallados:")
        print(e.errors())
        raise  # importante para que retry vuelva a intentar

    except Exception as e:
        print("❌ Error inesperado:")
        print(str(e))
        raise  # también necesario para que retry funcione
        
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def try_prompt(prompt: str):
    try:
        response = chat.preguntar(prompt, True) 

        return response

    except ValidationError as e:
        print("❌ Error de validación Pydantic:")
        print(e)
        print("Errores detallados:")
        print(e.errors())
        raise  # importante para que retry vuelva a intentar

    except Exception as e:
        print("❌ Error inesperado:")
        print(str(e))
        raise  # también necesario para que retry funcione        


def process_article(filename: str, prompts: list[str]):
    if not prompts:
        return None 

    respuesta = None

    for i, prompt in enumerate(prompts):
        print(f"\n--- Ejecutando prompt {i+1} ---")
        
        is_output_prompt = i == len(prompts) - 1
        
        if is_output_prompt:
            print("✅ Esta es la última iteración")
            
            respuesta = try_output_prompt(filename, prompt)
        else:
            respuesta = try_prompt(prompt)
            
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
        
        filename = os.path.splitext(file["nombre"])[0]

        contenido = file["contenido"]
        
        prompts = get_create_questions_prompt(context, contenido)
        
        process_article(filename, prompts) 
        
        