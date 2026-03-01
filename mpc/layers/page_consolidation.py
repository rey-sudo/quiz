import os
import re

# Rutas
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR  = os.path.join(BASE_DIR, "output", "pages")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def consolidar_paginas(nombre_salida: str = "documento_final.md"):
    """
    Une todos los .md de agent/output/pages/ en un solo archivo
    en agent/output/documento_final.md, respetando el orden de páginas.
    """
    if not os.path.exists(PAGES_DIR):
        print(f"❌ Carpeta no encontrada: {PAGES_DIR}")
        return

    # Obtener archivos .md y ordenarlos por número de página
    archivos = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    
    if not archivos:
        print(f"❌ No se encontraron archivos .md en {PAGES_DIR}")
        return

    # Ordenar por el número al final del nombre: _PAG_001, _PAG_002...
    def extraer_numero(nombre):
        match = re.search(r'_PAG_(\d+)\.md$', nombre, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    archivos.sort(key=extraer_numero)

    ruta_salida = os.path.join(OUTPUT_DIR, nombre_salida)

    print(f"📄 Consolidando {len(archivos)} páginas...")

    with open(ruta_salida, "w", encoding="utf-8") as f_out:
        for i, archivo in enumerate(archivos):
            ruta_pagina = os.path.join(PAGES_DIR, archivo)
            with open(ruta_pagina, "r", encoding="utf-8") as f_in:
                contenido = f_in.read()
            f_out.write(contenido)
            # Separador entre páginas (excepto la última)
            if i < len(archivos) - 1:
                f_out.write("\n\n")

    print(f"✅ Documento consolidado guardado en: {ruta_salida}")