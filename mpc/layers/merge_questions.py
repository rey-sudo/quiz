import logging
import os
import json
import re
from pathlib import Path
from config import QUESTIONS_PATH

logger = logging.getLogger("rich")

def merge_json_questions():
    """
    Iterates .json files from questions folder in numeric order
    and concatenates all arrays into a single unified .json file.
    """
    output_file = "output/all_questions.json"
    
    def get_json_files(folder: str) -> dict:
        files = {}
        for f in Path(folder).glob("*.json"):
            match = re.search(r'(\d+)', f.stem)
            if match:
                number = match.group(1).zfill(4)
                files[number] = f
        return files

    json_files = get_json_files(QUESTIONS_PATH)
    all_numbers = sorted(json_files.keys())

    merged = []

    for number in all_numbers:
        try:
            content = json_files[number].read_text(encoding="utf-8")
            data = json.loads(content)

            if isinstance(data, list):
                merged.extend(data)
            else:
                merged.append(data)

            logger.info(f"Merged: {json_files[number].name} ({len(data)} questions)")

        except Exception as e:
            logger.error(f"Failed to read {json_files[number].name}: {e}")

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    logger.info(f"Merged JSON saved at: {output_file} — Total questions: {len(merged)}")
    return output_file