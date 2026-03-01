from dotenv import load_dotenv
load_dotenv()
from utils.logging import setup_logging
setup_logging()
from layers.article_processing import process_articles
from layers.article_extraction import extract_articles
from layers.page_consolidation import consolidar_paginas
from layers.page_extraction import extract_pages
from utils.delete_output_content import delete_output_content
import logging

def main():
    logger = logging.getLogger(__name__)   
    
    logger.info("Running MPC server")
    
    #delete_output_content()
    #extract_pages("ley_name_1755_year_2015.pdf", pausa_debug=True)
    #consolidar_paginas()
    #extract_articles()
    process_articles()
    
if __name__ == "__main__":
    main()


