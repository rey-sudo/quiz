from dotenv import load_dotenv
load_dotenv()

from layers.merge_questions import merge_json_questions
from layers.summary_creation import create_summary
from layers.questions_creation import process_articles
from layers.article_extraction import extract_articles
from layers.page_consolidation import consolidar_paginas
from layers.page_extraction import extract_pages
from utils.delete_output_content import delete_output_content
from utils.logging import setup_logging
from prefect import flow, task
import logging

setup_logging()


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────

def build_error_response(task_name: str, error: Exception) -> dict:
    """Siempre devuelve una respuesta estructurada al agente."""
    return {
        "status": "error",
        "task": task_name,
        "message": str(error),
        "retryable": False,
        "agent_action": "El agente debe decidir si abortar, reintentar manualmente o continuar con datos parciales."
    }


# ─────────────────────────────────────────
# TASKS
# ─────────────────────────────────────────

@task(name="delete_output_content", retries=2, retry_delay_seconds=2)
def delete_output_content_task():
    skip = True
    if(skip): return {"status": "skipped"}
    
    delete_output_content()

@task(name="extract_pages", retries=2, retry_delay_seconds=2)
def extract_pages_task(pdf_name: str):
    skip = True
    if(skip): return {"status": "skipped"}
    
    extract_pages(pdf_name, pausa_debug=False)

@task(name="consolidar_paginas", retries=2, retry_delay_seconds=2)
def consolidar_paginas_task():
    skip = True
    if(skip): return {"status": "skipped"}   
     
    consolidar_paginas()

@task(name="extract_articles", retries=2, retry_delay_seconds=2)
def extract_articles_task():
    skip = True
    if(skip): return {"status": "skipped"}
    
    extract_articles()

@task(name="process_articles", retries=2, retry_delay_seconds=2)
def process_articles_task():
    skip = True
    if(skip): return {"status": "skipped"}
    
    process_articles()

@task(name="create_summary", retries=2, retry_delay_seconds=2)
def create_summary_task():
    skip = False
    if(skip): return {"status": "skipped"}    
    create_summary()

@task(name="merge_json_questions", retries=2, retry_delay_seconds=2)
def merge_json_questions_task():
    skip = False
    if(skip): return {"status": "skipped"}    
    merge_json_questions()


# ─────────────────────────────────────────
# FLOW 
# ─────────────────────────────────────────

@flow(name="mcp-decreto-flow", log_prints=True)
def main() -> dict:
    logger = logging.getLogger(__name__)
    logger.info("Running MCP server")

    # ── TASK 1: delete_output_content ────────────────────────
    state = delete_output_content_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("delete_output_content", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ delete_output_content OK")

    # ── TASK 2: extract_pages ─────────────────────────────────
    state = extract_pages_task("decreto_name_1165_year_2019.pdf", return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("extract_pages", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ extract_pages OK")

    # ── TASK 3: consolidar_paginas ───────────────────────────
    state = consolidar_paginas_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("consolidar_paginas", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ consolidar_paginas OK")

    # ── TASK 4: extract_articles ──────────────────────────────
    state = extract_articles_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("extract_articles", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ extract_articles OK")

    # ── TASK 5: process_articles ──────────────────────────────
    state = process_articles_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("process_articles", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ process_articles OK")

    # ── TASK 6: create_summary ────────────────────────────────
    state = create_summary_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("create_summary", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ create_summary OK")

    # ── TASK 7: merge_json_questions ──────────────────────────
    state = merge_json_questions_task(return_state=True)
    if state.is_failed():
        error = state.result(raise_on_failure=False)
        response = build_error_response("merge_json_questions", error)
        logger.error(f"❌ {response}")
        return response

    logger.info("✅ merge_json_questions OK")

    # ── TODAS LAS TASKS EXITOSAS ──────────────────────────────
    return {
        "status": "success",
        "message": "Flow completado sin errores",
        "tasks_completed": [
            "delete_output_content",
            "extract_pages",
            "consolidar_paginas",
            "extract_articles",
            "process_articles",
            "create_summary",
            "merge_json_questions"
        ]
    }


if __name__ == "__main__":
    result = main()
    print("\n── RESPUESTA AL AGENTE ──────────────────")
    print(result)