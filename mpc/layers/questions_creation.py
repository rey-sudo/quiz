import json
import logging
from utils.clean_json import limpiar_json_markdown
from pydantic import ValidationError
from prompts.create_questions import PromptConfig, get_create_questions_prompt
from clients.gemini_client import GeminiChat
from clients.openai_client import OpenAIChat
from clients.ollama_client import OllamaChat
from tenacity import retry, wait_fixed, stop_after_attempt
import os
import glob
import re

logger = logging.getLogger("rich")

SYSTEM_PROMPT = """
Eres un asistente experto en normativa colombia vigente año 2026
"""


chat = OllamaChat(
    model='gemma3:4b',
    system_prompt=SYSTEM_PROMPT
)

chat = GeminiChat(
    model="gemini-2.5-flash",
    system_prompt=SYSTEM_PROMPT,
)

  
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def save_json_file(output_path: str, filename: str, data: str):
    """
    Saves a JSON string as a JSON file in 'output/questions'.
    """
    try:
        output_path
        os.makedirs(output_path, exist_ok=True)
        file_path = os.path.join(output_path, filename)
        
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
def save_md_file(output_path: str, filename: str, data: str):
    """
    Saves a markdown string as a .md file in the specified output path.
    """
    try:
        os.makedirs(output_path, exist_ok=True)
        file_path = os.path.join(output_path, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
        
        logger.info(f"Markdown file saved at: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Failed to save markdown (attempt failed): {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def try_prompt(prompt: PromptConfig):
    # Usamos un bucle interno para el manejo manual de 'r' (retry)
    while True:
        try:
            # 1. Llamada a la IA
            response = chat.preguntar(prompt.content, prompt.append)
            
            # 2. Limpieza inmediata
            respuesta_limpia = limpiar_json_markdown(response)
            
            # Validamos que no esté vacío antes de seguir
            if not respuesta_limpia or not respuesta_limpia.strip():
                print("⚠️ Respuesta de IA vacía.")
                if not prompt.debug: raise ValueError("Respuesta vacía")
                # Si es debug, permitiremos que el usuario decida abajo

            # 3. Interacción Humana (Debug)
            if prompt.debug:
                opcion = input("\n[Enter] Continuar | [r] Reintentar: ").strip().lower()
            
                if opcion == 'r':
                    print("🔄 Refrescando respuesta...")
                    continue # Vuelve al inicio del 'while True' (misma ejecución de la función)
                else:
                    print("➡️ Continuando a validación...")

            # 4. Validación Técnica
            if prompt.type_adapter:
                # Esto lanzará ValidationError si el JSON está mal
                prompt.type_adapter.validate_json(respuesta_limpia) 
                print("✅ Validación Pydantic exitosa.")

            if prompt.save_output:
                match prompt.output_format:
                    case ".json":
                        save_json_file(prompt.output_path, f"{prompt.filename}{prompt.output_format}", respuesta_limpia)
                    case ".md":
                        save_md_file(prompt.output_path, f"{prompt.filename}{prompt.output_format}", respuesta_limpia)
                    case _:
                        logger.warning(f"Unsupported output format: {prompt.output_format}")
            
            return respuesta_limpia

        except ValidationError as e:
            print(f"❌ Error de validación en prompt {prompt.index}")
            # Si estamos en debug, permitimos reintentar manualmente tras el error
            if prompt.debug:
                print(f"Detalle: {e.json()}")
                input("Presiona Enter para reintentar la llamada a la IA...")
                continue # Reintenta dentro del while
            raise # Si no es debug, lanza para que el @retry automático actúe

        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            raise # Lanza para que @retry actúe

    
    
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
        
        prompts = get_create_questions_prompt(context, contenido, filename)
        
        if not prompts:
            return None 

        for i, prompt in enumerate(prompts):
            logger.info(f"\n[magenta]{'=' * 50}[/magenta]\n[magenta]--- Ejecutando prompt {i} ---[/magenta]\n[magenta]{'=' * 50}[/magenta]")
        
            try_prompt(prompt)
        
        