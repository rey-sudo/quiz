import os
import re

# Rutas
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ARTICLES_DIR = os.path.join(OUTPUT_DIR, "articles")
DOCUMENTO_FINAL = os.path.join(OUTPUT_DIR, "documento_final.md")


def detectar_inicio_articulo(linea: str):
    """
    Detecta si una línea es el inicio de un artículo.
    Casos soportados:
      ARTÍCULO 29.     ARTICULO 29.     Artículo 29.
      ART. 29.         ART 29.
      Art. 29.         Art 29.
      ART.° 29.        ART° 29.         Art.° 29.
      Artículo 29°     ARTICULO 29°
      ARTICULO 3o      ARTÍCULO 3o.     Artículo 3°
    """
    match = re.match(
        r'^\s*'
        r'(?:ART[IÍ]CULO|ART\.?°?|Art\.?°?)'  # palabra clave
        r'\s*'
        r'(\d+)'                                 # número de artículo
        r'(?:°|º|o|[a-zA-Z])?'                  # sufijo ordinal opcional: °, º, o, letras
        r'\s*[.°:\s]',                           # separador
        linea,
        re.IGNORECASE
    )
    return match.group(1) if match else None


def article_extraction(ruta_doc: str = DOCUMENTO_FINAL):
    """
    Lee documento_final.md, detecta artículos y genera un .md por artículo
    en agent/output/articles/.
    """
    if not os.path.exists(ruta_doc):
        print(f"❌ Archivo no encontrado: {ruta_doc}")
        return

    os.makedirs(ARTICLES_DIR, exist_ok=True)

    with open(ruta_doc, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    articulo_actual  = None   # número del artículo activo
    contenido_actual = []     # líneas acumuladas
    articulos_guardados = 0

    def guardar_articulo(numero, contenido):
        nombre_archivo = os.path.join(ARTICLES_DIR, f"articulo_{numero.zfill(4)}.md")
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("".join(contenido).strip() + "\n")

    for linea in lineas:
        numero = detectar_inicio_articulo(linea)

        if numero:
            # Guardar artículo anterior antes de empezar el nuevo
            if articulo_actual is not None:
                guardar_articulo(articulo_actual, contenido_actual)
                articulos_guardados += 1

            articulo_actual  = numero
            contenido_actual = [linea]
        else:
            if articulo_actual is not None:
                contenido_actual.append(linea)

    # Guardar el último artículo
    if articulo_actual is not None:
        guardar_articulo(articulo_actual, contenido_actual)
        articulos_guardados += 1

    print(f"✅ {articulos_guardados} artículos extraídos en: {ARTICLES_DIR}")