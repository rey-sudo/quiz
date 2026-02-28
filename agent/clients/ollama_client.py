import ollama

class OllamaChat:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.historial = [{"role": "system", "content": system_prompt}]

    def preguntar(self, prompt: str, stream: bool = False) -> str:
        self.historial.append({"role": "user", "content": prompt})

        if stream:
            respuesta = ''
            for chunk in ollama_client.chat(
                model=self.model,
                messages=self.historial,
                stream=True
            ):
                texto = chunk['message']['content']
                print(texto, end='', flush=True)
                respuesta += texto
            print()
        else:
            response = ollama_client.chat(
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