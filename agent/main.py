
from utils import delete_output_content
from layers.page_consolidation import consolidar_paginas
from layers.page_extraction import extraer_legal_financiero_estricto


def main():
    print("Running MPC server")
    delete_output_content.delete()
    extraer_legal_financiero_estricto("ley_name_1755_year_2015.pdf", pausa_debug=True)
    consolidar_paginas()
    
if __name__ == "__main__":
    main()


