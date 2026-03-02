import logging
import os
import re
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from config import ARTICLES_DIR, SUMMARY_PATH, LISTS_DIR

logger = logging.getLogger("rich")

def create_summary():
    """
    Iterates .md files from articles and lists folders in numeric order
    and generates a single unified .xlsx file.
    """
    def get_md_files(folder) -> dict:
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

    output_path = SUMMARY_PATH / "summary.xlsx"
    output_dir = output_path.parent
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    wb = Workbook()
    wb.properties.defaultThemeVersion = "124226"
    wb.properties.language = "es-CO"    
    ws = wb.active
    ws.title = "Summary"

    # Header styling
    headers = ["Numero_Articulo", "Contenido_Articulo", "Lists"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, name="Arial")
        cell.fill = PatternFill("solid", start_color="4472C4", end_color="4472C4")
        cell.font = Font(bold=True, color="FFFFFF", name="Arial")
        cell.alignment = Alignment(horizontal="center")

    # Column widths
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 80
    ws.column_dimensions["C"].width = 80

    # Data rows
    for row_idx, number in enumerate(all_numbers, 2):
        article_content = articles[number].read_text(encoding="utf-8").strip() if number in articles else ""
        list_content = lists[number].read_text(encoding="utf-8").strip() if number in lists else ""

        cell_num = ws.cell(row=row_idx, column=1, value=number)
        cell_num.alignment = Alignment(horizontal="center")
        cell_num.font = Font(name="Arial", size=14)

        cell_article = ws.cell(row=row_idx, column=2, value=article_content)
        cell_article.alignment = Alignment(wrap_text=True, vertical="top")
        cell_article.font = Font(name="Arial", size=14)

        cell_list = ws.cell(row=row_idx, column=3, value=list_content)
        cell_list.alignment = Alignment(wrap_text=True, vertical="top")
        cell_list.font = Font(name="Arial", size=14)

        wb.save(output_path)

    
    return output_path