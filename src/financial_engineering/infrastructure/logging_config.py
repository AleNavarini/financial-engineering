from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s: %(message)s'


def _secrets() -> list[str]:
    return [value for value in (os.getenv('LSEG_APP_KEY', '').strip(),) if value]


def setup_logging() -> None:
    root = logging.getLogger()
    if getattr(root, '_financial_engineering_configured', False):
        return

    level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)

    root.setLevel(logging.DEBUG)
    root.addHandler(_console_handler(level))
    root.addHandler(_file_handler())

    root._financial_engineering_configured = True


def _console_handler(level: int) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(RedactingFormatter(LOG_FORMAT))
    return handler


def _file_handler() -> logging.Handler:
    log_directory = Path(os.getenv('LOG_DIR') or PROJECT_ROOT / 'logs')
    log_directory.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_directory / 'app.log',
        maxBytes=max(int(os.getenv('LOG_MAX_BYTES', '5000000')), 1),
        backupCount=int(os.getenv('LOG_BACKUP_COUNT', '3')),
        encoding='utf-8',
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(RedactingFormatter(LOG_FORMAT))
    return handler


def redact_message(message: str) -> str:
    rendered = message
    for secret in _secrets():
        if secret:
            rendered = rendered.replace(secret, '***')
    return rendered


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        for secret in _secrets():
            if secret:
                rendered = rendered.replace(secret, '***')
        return rendered