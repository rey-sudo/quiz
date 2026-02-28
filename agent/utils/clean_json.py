import re

def limpiar_json_markdown(text: str) -> str:
    """
    Elimina los backticks de código Markdown y espacios innecesarios
    """
    # Quita ```json al inicio y ``` al final
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()