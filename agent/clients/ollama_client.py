import ollama

class OllamaChat:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.system_prompt = system_prompt
        self.historial = [{"role": "system", "content": system_prompt}]

    def preguntar(self, prompt: str, stream: bool = False, append: bool = True) -> str:
        mensajes = self.historial.copy()
        mensajes.append({"role": "user", "content": prompt})
        
        if stream:
            respuesta = ''
            for chunk in ollama.chat(
                model=self.model,
                messages=mensajes,
                stream=True
            ):
                texto = chunk['message'].get('content') or ''
                print(texto, end='', flush=True)
                respuesta += texto
            print()
        else:
            response = ollama.chat(
                model=self.model,
                messages=mensajes
            )
            respuesta = response['message'].get('content') or ''

        # Guarda respuesta del asistente en el historial
        if append:
            self.historial.append({"role": "user", "content": prompt})
            self.historial.append({"role": "assistant", "content": respuesta})

        return respuesta

    def limpiar(self):
        """Resetea el historial manteniendo el system prompt"""
        self.historial = [self.historial[0]]

    def ver_historial(self):
        for msg in self.historial:
            print(f"[{msg['role'].upper()}]: {msg['content']}\n")