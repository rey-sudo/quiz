
from utils.convert_to_json import convertir_a_json_formateado
from pydantic import BaseModel, Field, TypeAdapter
from typing import List

class QuestionItem(BaseModel):
    question: str = Field(..., description="Enunciado de la pregunta tipo caso con mención de artículo y normativa")
    options: List[str] = Field(..., min_items=4, max_items=4, description="Lista de opciones posibles")
    correct: int = Field(..., ge=0, le=3, description="Índice de la opción correcta")
    explanation: str = Field(..., description="Explicación completa de la respuesta")

questionsAdapter = TypeAdapter(List[QuestionItem])

formato_preguntas = questionsAdapter.json_schema()

def get_create_questions_prompt(context: str, article: str) -> list[str]:
    prompt1 = {
        "tarea": "Analizar esta normativa colombiana de 2026.",
        "contexto": context,
        "instrucciones": [
            "Analizar toda la normativa proporcionada.",
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
        #convertir_a_json_formateado(prompt2),
        convertir_a_json_formateado(prompt3)    #OUTPUT PROMPT   
    ]

    return prompts