from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

# This module centralizes logging setup and access for the project.
_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# This module centralizes logging setup and access for the project.
def setup_logging(
    log_dir: Path,
    *,
    app_logger_name: str = "steamteam",
    level: int = logging.DEBUG,          # captures DEBUG/INFO/WARNING/ERROR
    console_level: int = logging.INFO,   # console is usually less noisy
    max_bytes: int = 2_000_000,          # 2 MB per file
    backup_count: int = 1,               # keep 5 rotated files
) -> logging.Logger:
    """
    Configure project logging once.
    Returns the app root logger (e.g., 'steamteam').

    Call this early in app.pyw before importing modules that log.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "steamteam.log"

    logger = logging.getLogger(app_logger_name)
    logger.setLevel(level)
    logger.propagate = False  # avoid duplicate logs via root logger

    # Prevent duplicate handlers if setup_logging() is called more than once.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # File handler: keeps everything (DEBUG+)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler: cleaner output for normal runtime
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Optional: quiet noisy third-party libs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return logger

# Helper to get loggers in other modules without worrying about naming.
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Use project-namespaced loggers:
      get_logger(__name__) in modules
    """
    if not name:
        return logging.getLogger("steamteam")
    if name.startswith("steamteam"):
        return logging.getLogger(name)
    return logging.getLogger(f"steamteam.{name}")
