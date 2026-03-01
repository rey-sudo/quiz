import os
from typing import Iterator
from google import genai
from google.genai import types


class GeminiChat:
    def __init__(self, model: str, system_prompt: str = ""):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.historial: list[types.Content] = []

    def _config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_prompt or None,
        )

    def _mensajes(self, prompt: str) -> list[types.Content]:
        return self.historial + [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]

    def _guardar(self, prompt: str, respuesta: str):
        self.historial.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )
        self.historial.append(
            types.Content(role="model", parts=[types.Part.from_text(text=respuesta)])
        )

    def preguntar_(self, prompt: str, append: bool = True) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=self._mensajes(prompt),
            config=self._config(),
        )
        respuesta = response.text or ""

        if append:
            self._guardar(prompt, respuesta)

        return respuesta

    def preguntar_stream(self, prompt: str, append: bool = True) -> Iterator[str]:
        """Yields chunks — el caller controla el output."""
        respuesta = ""

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=self._mensajes(prompt),
            config=self._config(),
        ):
            texto = chunk.text or ""
            respuesta += texto
            yield texto

        if append:
            self._guardar(prompt, respuesta)

    def preguntar(self, prompt: str, append: bool = True) -> str:
        """Streaming en tiempo real, retorna el texto completo al final."""
        resultado = ""
        for chunk in self.preguntar_stream(prompt, append=append):
            print(chunk, end="", flush=True)
            resultado += chunk
        print()
        return resultado

    def limpiar(self):
        self.historial = []

    def ver_historial(self):
        for msg in self.historial:
            print(f"[{msg.role.upper()}]: {msg.parts[0].text}\n")