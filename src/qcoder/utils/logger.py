"""Logging utilities for QCoder CLI."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..core.config import get_config


class QCoderLogger:
    """Custom logger for QCoder CLI."""

    def __init__(self, name: str = "qcoder", log_to_file: bool = True) -> None:
        """Initialize logger.

        Args:
            name: Logger name.
            log_to_file: Whether to log to file.
        """
        self.config = get_config()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Console handler (only errors and critical)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter(
            "[%(levelname)s] %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (all logs)
        if log_to_file:
            log_file = self._get_log_file()
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def _get_log_file(self) -> Path:
        """Get log file path.

        Returns:
            Path to log file.
        """
        log_dir = self.config.log_dir
        log_file = log_dir / f"qcoder_{datetime.now().strftime('%Y%m%d')}.log"
        return log_file

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)

    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message)


# Global logger instance
_logger: Optional[QCoderLogger] = None


def get_logger() -> QCoderLogger:
    """Get or create global logger instance.

    Returns:
        Global QCoderLogger instance.
    """
    global _logger
    if _logger is None:
        _logger = QCoderLogger()
    return _logger
