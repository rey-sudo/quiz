from clients.gemini_client import GeminiChat
from clients.openai_client import OpenAIChat
from clients.ollama_client import OllamaChat
from utils.convert_to_json import convertir_a_json_formateado
from pydantic import BaseModel, Field
from typing import List


class QuestionItem(BaseModel):
    question: str = Field(..., description="Enunciado de la pregunta tipo caso con mención de artículo y normativa")
    options: List[str] = Field(..., min_items=4, max_items=4, description="Lista de opciones posibles")
    correct: int = Field(..., ge=0, description="Índice de la opción correcta")
    explanation: str = Field(..., description="Explicación completa de la respuesta")

formato_preguntas = {
    "type": "array",
    "items": QuestionItem.model_json_schema()
}


SYSTEM_PROMPT = """
Eres un asistente experto en normativa colombia vigente año 2026
"""

chat = OllamaChat(
    model='gemma3:4b',
    system_prompt=SYSTEM_PROMPT
)

chat = OpenAIChat(
    model='gpt-4o-mini',
    system_prompt=SYSTEM_PROMPT
)

chat = GeminiChat(
    model="gemini-2.5-flash",
    system_prompt=SYSTEM_PROMPT,
)

context ="""
LEY 1755 DE 2015
(Junio 30)
“Por medio de la cual se regula el Derecho Fundamental de Petición y se sustituye un título del Código de Procedimiento Administrativo y de lo
Contencioso Administrativo”.
EL CONGRESO DE COLOMBIA
DECRETA:
ARTÍCULO 1°. Sustitúyase el Título II, Derecho de Petición, Capítulo I, Derecho de Petición ante las autoridades-Reglas Generales, Capítulo II
Derecho de petición ante autoridades-Reglas Especiales y Capítulo III Derecho de Petición ante organizaciones e instituciones privadas, artículos
13 a 33, de la Parte Primera de la Ley 1437 de 2011, por el siguiente:
TÍTULO. II
DERECHO PETICIÓN
CAPÍTULO. I
DERECHO DE PETICIÓN ANTE AUTORIDADES REGLAS GENERALES
ARTÍCULO 13. Objeto y modalidades del derecho de petición ante autoridades. Toda persona tiene derecho a presentar peticiones respetuosas a
las autoridades, en los términos señalados en este código, por motivos de interés general o particular, y a obtener pronta resolución completa y
de fondo sobre la misma.
Toda actuación que inicie cualquier persona ante las autoridades implica el ejercicio del derecho de petición consagrado en el artículo 23 de la
Constitución Política, sin que sea necesario invocarlo. Mediante él, entre otras actuaciones, se podrá solicitar: el reconocimiento de un derecho,
la intervención de una entidad o funcionario, la resolución de una situación jurídica, la prestación de un servicio, requerir información, consultar,
examinar y requerir copias de documentos, formular consultas, quejas, denuncias y reclamos e interponer recursos.
El ejercicio del derecho de petición es gratuito y puede realizarse sin necesidad de representación a través de abogado, o de persona mayor
cuando se trate de menores en relación a las entidades dedicadas a su protección o formación.
(Ver Sentencia C-951 de 2014)
*jurisprudencia*
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

    prompt1 = {
    "tarea": "Analizar esta normativa colombiana de 2026.",
    "contexto": context,
    "instrucciones": [
        "Analizar toda la normativa proporcionada.",
        "Dar un ejemplo práctico.",
        "Usar lenguaje formal académico."
    ],
    "normativa": article
    }

    prompt2 = {
    "tarea": "Verificar tu análisis y hacer una lista numerada sin excluir información.",
    "instrucciones": [
        "Crear una lista enumerada con el resultado del análisis.",
        "La lista numerada no debe tener subnumeración.",
        "Usar este formato: (Número de numeración. Nombre del concepto o idea: contenido)."
    ],
    "normativa": article
    }

    prompt3 = {
    "tarea": "Crear preguntas de opción múltiple con respuesta única.",
    "instrucciones": [
        "Las preguntas deben ser tipo caso, relacionadas estrictamente con el artículo y cada uno de sus incisos.",
        "Recordar al lector el número del artículo y el nombre exacto de la norma.",
        "El número de preguntas debe abarcar todo el contexto y contenido del artículo y todos sus incisos.",
        "No dejar ningún tema del artículo sin pregunta."
        "Formatea las preguntas con formato_de_pregunta_json"
    ],
    "formato_de_pregunta_json": formato_preguntas,
    "normativa": article
    }
    
    prompts = [
        convertir_a_json_formateado(prompt1),     
        convertir_a_json_formateado(prompt2),
        convertir_a_json_formateado(prompt3)       
    ]
    

    for i, prompt in enumerate(prompts):
        print(f"\n--- Ejecutando prompt {i+1} ---")
        respuesta = chat.preguntar(prompt, True)
        print(respuesta)
    
    
    chat.ver_historial()
    
    
