import logging
import sys

from app.core.config import settings

def start_logging():
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
