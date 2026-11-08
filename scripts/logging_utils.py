import logging

from scripts.config import LOG_PATH, ensure_directories


def configure_logging() -> None:
    ensure_directories()
    logging.basicConfig(
        filename=str(LOG_PATH),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )


def show_warning(message: str) -> None:
    print(f"WARNUNG: {message}")
    logging.warning(message)


def show_error(message: str) -> None:
    print(f"FEHLER: {message}")
    logging.error(message)
