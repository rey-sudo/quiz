import logging
import os
import csv
import re
from pathlib import Path
from config import ARTICLES_DIR, SUMMARY_PATH, LISTS_DIR

logger = logging.getLogger("rich")

def create_summary_csv():
    """
    Iterates .md files from articles and lists folders in numeric order
    and generates a single unified CSV file.
    """
    def get_md_files(folder: str) -> dict:
        files = {}
        for f in Path(folder).glob("*.md"):
            match = re.search(r'(\d+)', f.stem)
            if match:
                number = match.group(1).zfill(4)
                files[number] = f
        return files

    articles = get_md_files(ARTICLES_DIR)
    lists = get_md_files(LISTS_DIR)

    all_numbers = sorted(set(articles.keys()) | set(lists.keys()))

    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)

    with open(SUMMARY_PATH, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Numero_Articulo", "Contenido_Articulo", "Lists"])
        writer.writeheader()

        for number in all_numbers:
            article_content = articles[number].read_text(encoding="utf-8").strip() if number in articles else ""
            list_content = lists[number].read_text(encoding="utf-8").strip() if number in lists else ""

            writer.writerow({
                "Numero_Articulo": number,
                "Contenido_Articulo": article_content,
                "Lists": list_content
            })

    logger.info(f"CSV saved at: {SUMMARY_PATH}")
    return SUMMARY_PATH