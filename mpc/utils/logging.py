import logging
from rich.logging import RichHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),                          
            logging.FileHandler("logs/app.log", encoding="utf-8"),  
            RichHandler(markup=True, rich_tracebacks=True)
        ],
    )