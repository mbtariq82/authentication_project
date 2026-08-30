import logging
import os
import sys


def configure_logging() -> None:
    """
    Call this once, as early as possible in your app's entrypoint
    (e.g. the top of main.py, before creating the FastAPI app / the
    AdminAgent instance).

    Without this, Python's root logger defaults to WARNING and has
    no handler attached in most setups, so every logger.info(...)
    call scattered through admin_agent.py, admin_sql_agent.py,
    approval_service.py, etc. silently does nothing — which is
    exactly the "I can't tell where my request is going" problem.

    Controlled by env var LOG_LEVEL (default INFO). Set LOG_LEVEL=DEBUG
    for maximum verbosity while debugging a specific request.
    """

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if configure_logging() is accidentally
    # called more than once (e.g. under --reload).
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # These libraries are extremely chatty at INFO/DEBUG and drown
    # out your own app's logs — turn them down specifically, while
    # everything under agents.* / api.* / services.* still uses the
    # level set above.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if os.getenv("LOG_SQL") == "1" else logging.WARNING
    )