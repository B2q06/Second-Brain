#!/usr/bin/env python3
"""
Logging Infrastructure for Second Brain System
Provides consistent logging across all scripts with rotation and levels.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class SecondBrainLogger:
    """Centralized logging configuration for all scripts"""

    def __init__(self, name: str, vault_path: Path, log_to_file: bool = True, log_level: str = "INFO"):
        self.name = name
        self.vault_path = Path(vault_path)
        self.log_dir = self.vault_path / "_system" / "logs"
        self.log_level = getattr(logging, log_level.upper())

        # Create logs directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = self._setup_logger(log_to_file)

    def _setup_logger(self, log_to_file: bool) -> logging.Logger:
        """Configure logger with handlers"""

        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler (always enabled)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_to_file:
            log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"

            # Rotating file handler (10MB max, keep 5 backups)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Return configured logger instance"""
        return self.logger


def get_logger(name: str, vault_path: str = "C:/obsidian-memory-vault", log_level: str = "INFO") -> logging.Logger:
    """
    Convenience function to get a configured logger.

    Usage:
        from logger_setup import get_logger
        logger = get_logger(__name__)
        logger.info("Processing started")
        logger.warning("No timestamps found")
        logger.error("Failed to connect to Neo4j", exc_info=True)
    """
    sb_logger = SecondBrainLogger(name, Path(vault_path), log_level=log_level)
    return sb_logger.get_logger()


# Context manager for timed operations
class TimedOperation:
    """Context manager to log operation duration"""

    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(f"Failed: {self.operation_name} after {duration:.2f}s", exc_info=True)
        else:
            self.logger.info(f"Completed: {self.operation_name} in {duration:.2f}s")


# Example usage
if __name__ == "__main__":
    # Example: Basic logging
    logger = get_logger("example_script")
    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.debug("This debug message won't show (INFO level)")

    # Example: Timed operation
    with TimedOperation(logger, "Processing batch of files"):
        import time
        time.sleep(1)  # Simulate work

    # Example: Error logging with traceback
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.error("An error occurred", exc_info=True)

    print(f"\nLog files written to: {Path('C:/obsidian-memory-vault/_system/logs')}")
