import os
import shutil

# Rutas
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def limpiar_directorio(ruta: str):
    """Borra todo el contenido de una carpeta sin borrar la carpeta misma."""
    if not os.path.exists(ruta):
        print(f"⚠️  Carpeta no encontrada, se omite: {ruta}")
        return

    eliminados = 0
    for item in os.listdir(ruta):
        ruta_item = os.path.join(ruta, item)
        if os.path.isfile(ruta_item):
            os.remove(ruta_item)
        elif os.path.isdir(ruta_item):
            shutil.rmtree(ruta_item)
        eliminados += 1

    print(f"🗑️  {eliminados} elemento(s) eliminado(s) de: {ruta}")


def delete():
    """Borra el contenido de agent/input/ y agent/output/."""

    limpiar_directorio(OUTPUT_DIR)
    print("\n✅ Limpieza completada.")


