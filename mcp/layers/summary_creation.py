import logging
import os
import re
from pathlib import Path
from config import ARTICLES_DIR, SUMMARY_PATH, LISTS_DIR

logger = logging.getLogger("rich")

def create_summary():
    """
    Iterates .md files from articles and lists folders in numeric order
    and generates multiple .md files, one per every 100 rows.
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

    output_dir = Path(SUMMARY_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    CHUNK_SIZE = 100
    output_paths = []

    for chunk_start in range(0, len(all_numbers), CHUNK_SIZE):
        chunk_numbers = all_numbers[chunk_start:chunk_start + CHUNK_SIZE]

        first_num = int(chunk_numbers[0])
        last_num = int(chunk_numbers[-1])
        output_path = output_dir / f"summary_{first_num:04d}-{last_num:04d}.md"

        lines = []
        for number in chunk_numbers:
            try:
                article_content = articles[number].read_text(encoding="utf-8").strip() if number in articles else ""
            except Exception as e:
                logger.warning(f"Could not read article {number}: {e}")
                article_content = ""

            try:
                list_content = lists[number].read_text(encoding="utf-8").strip() if number in lists else ""
            except Exception as e:
                logger.warning(f"Could not read list {number}: {e}")
                list_content = ""

            lines.append(f"## {number}\n")
            if article_content:
                lines.append(f"{article_content}\n")
            if list_content:
                lines.append(f"{list_content}\n")
            lines.append("\n---\n")

        output_path.write_text("".join(lines), encoding="utf-8")
        output_paths.append(output_path)
        logger.info(f"Saved: {output_path.name} ({len(chunk_numbers)} entries)")

    return output_paths