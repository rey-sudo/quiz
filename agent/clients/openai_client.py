import os
from openai import OpenAI

class OpenAIChat:
    def __init__(self, model: str, system_prompt: str):
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")

        self.client = OpenAI(api_key=api_key) 
        self.model = model
        self.historial = [{"role": "system", "content": system_prompt}]

    def preguntar(self, prompt: str, stream: bool = False) -> str:
        self.historial.append({"role": "user", "content": prompt})

        if stream:
            respuesta = ''
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.historial,
                stream=True
            )
            for chunk in stream_response:
                texto = chunk.choices[0].delta.content or ''
                print(texto, end='', flush=True)
                respuesta += texto
            print()
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.historial
            )
            respuesta = response.choices[0].message.content

        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta

    def limpiar(self):
        """Resetea el historial manteniendo el system prompt"""
        self.historial = [self.historial[0]]

    def ver_historial(self):
        for msg in self.historial:
            print(f"[{msg['role'].upper()}]: {msg['content']}\n")