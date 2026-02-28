import os
from google import genai
from google.genai import types


class GeminiChat:
    def __init__(self, model: str, system_prompt: str):
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada")
        
        self.client = genai.Client(api_key=api_key) 
        self.model = model
        self.system_prompt = system_prompt
        self.historial: list[types.Content] = []

    def preguntar(self, prompt: str, stream: bool = False) -> str:
        self.historial.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
        )

        if stream:
            respuesta = ''
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=self.historial,
                config=config,
            ):
                if chunk.text:
                    print(chunk.text, end='', flush=True)
                    respuesta += chunk.text
            print()
        else:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.historial,
                config=config,
            )
            respuesta = response.text

        self.historial.append(
            types.Content(
                role="model",  # Gemini usa "model" en lugar de "assistant"
                parts=[types.Part.from_text(text=respuesta)]
            )
        )

        return respuesta

    def limpiar(self):
        """Resetea el historial manteniendo el system prompt"""
        self.historial = []

    def ver_historial(self):
        for msg in self.historial:
            rol = msg.role.upper()
            texto = msg.parts[0].text
            print(f"[{rol}]: {texto}\n")

