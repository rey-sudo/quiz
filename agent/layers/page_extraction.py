import fitz  # PyMuPDF
import time
import os
import re
import sys
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input")

def get_input_path(filename: str) -> str:
    """Devuelve la ruta absoluta de un archivo dentro de agent/input/."""
    path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado en input/: {path}")
    return path

def limpiar_texto_exhaustivo(texto):
    """
    Filtra carácter por carácter, conservando todo lo válido.
    Normaliza a NFC para unificar representaciones (e.g. á = a + ́).
    """
    if not texto:
        return ""
    
    # Normalización Unicode NFC: compone caracteres base + diacríticos
    texto = unicodedata.normalize('NFC', texto)
    
    # Filtrado carácter por carácter
    resultado = ''.join(c for c in texto if c.isprintable() or c in '\n\r\t')
    
    # Colapsar espacios múltiples en una sola línea (no entre líneas)
    lineas = resultado.split('\n')
    lineas = [re.sub(r'[ \t]+', ' ', linea).strip() for linea in lineas]
    
    # Eliminar líneas vacías consecutivas (máximo 2 seguidas)
    texto_final = re.sub(r'\n{3,}', '\n\n', '\n'.join(lineas))
    
    return texto_final.strip()


def extraer_legal_financiero_estricto(nombre_pdf, pausa_debug=True):
    ruta_pdf = get_input_path(nombre_pdf)
   
    doc = fitz.open(ruta_pdf)
    
    # Verificar si el PDF está cifrado
    if doc.is_encrypted:
        print(f"🔒 El PDF está cifrado. Intenta desbloquearlo primero.")
        doc.close()
        return

    OUTPUT_DIR = os.path.join(BASE_DIR, "output/pages")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nombre_base = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(ruta_pdf))[0])
    
    total_paginas = len(doc)
    
    print(f"⚖️  Procesando documento crítico: {ruta_pdf}")
    print(f"📄 Total de páginas: {total_paginas}")
    print(f"Presiona Ctrl+C en cualquier momento para CERRAR el programa.\n")

    try:
        for i in range(total_paginas):
            num_pagina = i + 1
            pagina = doc.load_page(i)
            
            contenido_limpio = []

            # --- CAPA 1: Extracción por bloques (preserva estructura espacial) ---
            bloques = pagina.get_text("blocks")
            bloques.sort(key=lambda b: (round(b[1] / 5) * 5, b[0]))  # tolerancia vertical de 5pts

            for b in bloques:
                # b[6] == 0 → bloque de texto; b[6] == 1 → imagen (omitir)
                if b[6] != 0:
                    continue
                texto_bloque = b[4].strip()
                if texto_bloque:
                    texto_bloque = limpiar_texto_exhaustivo(texto_bloque)
                    if texto_bloque:
                        contenido_limpio.append(texto_bloque)

            texto_bloques = "\n\n".join(contenido_limpio)

            # --- CAPA 2: Extracción raw como respaldo para capturar texto no bloqueado ---
            texto_raw = pagina.get_text("text")
            texto_raw = limpiar_texto_exhaustivo(texto_raw)

            # Usar el que tenga más contenido
            texto_final = texto_bloques if len(texto_bloques) >= len(texto_raw) else texto_raw

            # --- CAPA 3: Extracción por palabras individuales si ambas capas fallan ---
            if len(texto_final) < 50:
                palabras = pagina.get_text("words")
                palabras.sort(key=lambda w: (round(w[1] / 5) * 5, w[0]))
                texto_palabras = ' '.join(
                    limpiar_texto_exhaustivo(w[4]) for w in palabras if w[4].strip()
                )
                if len(texto_palabras) > len(texto_final):
                    texto_final = texto_palabras

            # Guardado físico
            nombre_archivo = f"{nombre_base}_PAG_{num_pagina:03d}.md"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write(f"--- PAGINA {num_pagina} / {total_paginas} ---\n\n")
                f.write(texto_final if texto_final else "*[Página sin texto extraíble]*")

            chars = len(texto_final)
            estado = "⚠️ " if chars < 50 else "✅"
            print(f"{estado} Pág {num_pagina:>4} guardada. ({chars:,} caracteres)")

            if pausa_debug and i < total_paginas - 1:
                print(f"   ⏳ Pausa de 10s... [Ctrl+C para detener]")
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n🛑 DETENCIÓN FORZADA POR EL USUARIO.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error inesperado en página {num_pagina}: {e}")
        raise

    finally:
        doc.close()
        print("\n🚀 Proceso completado. Documento cerrado correctamente.")