from dotenv import load_dotenv
load_dotenv()
from utils.logging import setup_logging
setup_logging()
from layers.create_questions import process_articles
from layers.article_extraction import extract_articles
from layers.page_consolidation import consolidar_paginas
from layers.page_extraction import extract_pages
from utils.delete_output_content import delete_output_content
import logging

def main():
    logger = logging.getLogger(__name__)   
    
    logger.info("Running MPC server")
    
    #delete_output_content()
    #extract_pages("decreto_name_1165_year_2019.pdf", pausa_debug=False)
    #consolidar_paginas()
    #extract_articles()
    process_articles()
    
if __name__ == "__main__":
    main()


