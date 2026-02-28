from dotenv import load_dotenv
load_dotenv()
from layers.article_processing import process_articles
from layers.article_extraction import article_extraction
from utils.delete_output_content import delete_output_content
from layers.page_consolidation import consolidar_paginas
from layers.page_extraction import extraer_legal_financiero_estricto


def main():
    print("Running MPC server")

    
    
    #delete_output_content()
    #extraer_legal_financiero_estricto("ley_name_1755_year_2015.pdf", pausa_debug=True)
    #consolidar_paginas()
    #article_extraction()
    process_articles()
    
if __name__ == "__main__":
    main()


