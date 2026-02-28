import json
import ollama

def preguntar(model: str, system_prompt: str, prompt: str, stream: bool = False) -> str:
    messages = [
        {"role": "system", "content": system_prompt },
        {"role": "user", "content": prompt}
    ]   
     
    print(messages)
    
    if stream:
        respuesta = ''
        for chunk in ollama.chat(
            model=model,
            messages=messages,
            stream=True
        ):
            texto = chunk['message']['content']
            print(texto, end='', flush=True)
            respuesta += texto
            
        return respuesta
    else:
        response = ollama.chat(
            model=model,
            messages=messages
        )
        return response['message']['content']



SYSTEM_PROMPT = """

Eres experto en analizar normativa colombia vigente 2026.

"""

article = """

ARTÍCULO 19. Peticiones irrespetuosas, oscuras o reiterativas. Toda petición debe ser respetuosa so pena de rechazo. Solo cuando no se
comprenda la ﬁnalidad u objeto de la petición esta se devolverá al interesado para que la corrija o aclare dentro de los diez (10) días siguientes.
En caso de no corregirse o aclararse, se archivará la petición. En ningún caso se devolverán peticiones que se consideren inadecuadas o
incompletas.

Respecto de peticiones reiterativas ya resueltas, la autoridad podrá remitirse a las respuestas anteriores, salvo que se trate de derechos
imprescriptibles, o de peticiones que se hubieren negado por no acreditar requisitos, siempre que en la nueva petición se subsane.

(Ver Sentencia C-951 de 2014)

*jurisprudencia*

"""


def process_articles():

    json_prompt = {
        "tarea": "Analizar esta normativa colombiana 2026",
        "contexto": "Ley 1755 de 2015",
        "constantes": [
      
        ],
        "instrucciones": [
            "Analizar toda la normativa dada",
            "Dar un ejemplo práctico",
            "Usar lenguaje formal academico"
        ],
        "normativa": article
    }


    prompt_final = json.dumps(json_prompt, indent=4, ensure_ascii=False)
    

    respuesta = preguntar("gemma3:4b", SYSTEM_PROMPT, prompt_final, True)
    print(respuesta)
    
    
