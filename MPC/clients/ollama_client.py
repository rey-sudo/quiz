import ollama
from typing import Iterator


class OllamaChat:
    def __init__(self, model: str, system_prompt: str = ""):
        self.model = model
        self.system_prompt = system_prompt
        self.historial: list[dict] = []
        if system_prompt:
            self.historial.append({"role": "system", "content": system_prompt})

    def preguntar_(self, prompt: str, append: bool = True) -> str:
        mensajes = self.historial + [{"role": "user", "content": prompt}]
        response = ollama.chat(model=self.model, messages=mensajes)
        respuesta = response.message.content or ""

        if append:
            self.historial.append({"role": "user", "content": prompt})
            self.historial.append({"role": "assistant", "content": respuesta})

        return respuesta
    
    def preguntar(self, prompt: str, append: bool = True) -> str:
        """Hace streaming imprimiendo en tiempo real y retorna el texto completo al final."""
        resultado = ""
        for chunk in self.preguntar_stream(prompt, append=append):
            print(chunk, end="", flush=True)
            resultado += chunk
        print()
        return resultado

    def preguntar_stream(self, prompt: str, append: bool = True) -> Iterator[str]:
        """Yields chunks — el caller controla el output."""
        mensajes = self.historial + [{"role": "user", "content": prompt}]
        respuesta = ""

        for chunk in ollama.chat(model=self.model, messages=mensajes, stream=True):
            texto = chunk.message.content or ""
            respuesta += texto
            yield texto

        if append:
            self.historial.append({"role": "user", "content": prompt})
            self.historial.append({"role": "assistant", "content": respuesta})

    def limpiar(self):
        self.historial = (
            [{"role": "system", "content": self.system_prompt}]
            if self.system_prompt else []
        )

    def ver_historial(self):
        for msg in self.historial:
            print(f"[{msg['role'].upper()}]: {msg['content']}\n")