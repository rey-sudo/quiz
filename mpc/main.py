from dotenv import load_dotenv
from layers.merge_questions import merge_json_questions
load_dotenv()
from layers.csv_creation import create_summary_csv
from utils.logging import setup_logging
setup_logging()
from layers.questions_creation import process_articles
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
    create_summary_csv()
    merge_json_questions()
if __name__ == "__main__":
    main()


