from utils.convert_to_json import convertir_a_json_formateado
import ollama

class Chat:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.historial = [{"role": "system", "content": system_prompt}]

    def preguntar(self, prompt: str, stream: bool = False) -> str:
        self.historial.append({"role": "user", "content": prompt})

        if stream:
            respuesta = ''
            for chunk in ollama.chat(
                model=self.model,
                messages=self.historial,
                stream=True
            ):
                texto = chunk['message']['content']
                print(texto, end='', flush=True)
                respuesta += texto
            print()
        else:
            response = ollama.chat(
                model=self.model,
                messages=self.historial
            )
            respuesta = response['message']['content']

        # Guarda respuesta del asistente en el historial
        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta

    def limpiar(self):
        """Resetea el historial manteniendo el system prompt"""
        self.historial = [self.historial[0]]

    def ver_historial(self):
        for msg in self.historial:
            print(f"[{msg['role'].upper()}]: {msg['content']}\n")


SYSTEM_PROMPT = """
Eres un asistente experto en normativa colombia vigente año 2026
"""

chat = Chat(
    model='gemma3:4b',
    system_prompt=SYSTEM_PROMPT
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
        "tarea": "Analizar esta normativa colombiana 2026",
        "contexto": context,
        "constantes": [
      
        ],
        "instrucciones": [
            "Analizar toda la normativa dada",
            "Dar un ejemplo práctico",
            "Usar lenguaje formal academico"
        ],
        "normativa": article
    }


    prompts = [
        convertir_a_json_formateado(prompt1)       
    ]
    

    respuesta = chat.preguntar(prompts[0], True)
    print(respuesta)
    
    chat.ver_historial()
    
    
