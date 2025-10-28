"""
Logging Configuration for LogicPWN

Centralized logging setup with sensible defaults and easy customization.
Provides consistent logging across all LogicPWN modules.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    colorize: bool = True,
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
) -> logger:
    """
    Configure LogicPWN logging with sensible defaults.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        format_string: Custom format string (None for default)
        colorize: Whether to use colored output in console
        rotation: Log file rotation size (default: "10 MB")
        retention: Log file retention period (default: "1 week")
        compression: Compression format for rotated logs (default: "zip")

    Returns:
        Configured logger instance

    Examples:
        >>> # Basic configuration
        >>> from logicpwn import configure_logging
        >>> configure_logging(level="DEBUG")

        >>> # With file output
        >>> configure_logging(level="INFO", log_file="security_test.log")

        >>> # Custom format
        >>> configure_logging(
        ...     level="DEBUG",
        ...     format_string="{time} | {level} | {message}"
        ... )
    """
    # Remove existing handlers
    logger.remove()

    # Default format with colors and context
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Console handler
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
    )

    # File handler (if specified)
    if log_file:
        # Create log directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=format_string,
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
        )

    logger.info(f"LogicPWN logging configured (level={level})")

    return logger


def configure_minimal_logging():
    """
    Configure minimal logging (only errors and warnings).

    Useful for production environments or when you want quiet output.

    Examples:
        >>> from logicpwn import configure_minimal_logging
        >>> configure_minimal_logging()
    """
    return configure_logging(
        level="WARNING",
        format_string="{time:HH:mm:ss} | {level: <8} | {message}",
        colorize=True,
    )


def configure_debug_logging(log_file: str = "logicpwn_debug.log"):
    """
    Configure verbose debug logging.

    Logs everything to both console and file for troubleshooting.

    Args:
        log_file: Path to debug log file

    Examples:
        >>> from logicpwn import configure_debug_logging
        >>> configure_debug_logging()
    """
    return configure_logging(level="DEBUG", log_file=log_file, colorize=True)


def configure_security_logging(log_file: str = "security_audit.log"):
    """
    Configure logging for security audits.

    Includes timestamps, context, and automatic rotation for compliance.

    Args:
        log_file: Path to security audit log file

    Examples:
        >>> from logicpwn import configure_security_logging
        >>> configure_security_logging("audit.log")
    """
    return configure_logging(
        level="INFO",
        log_file=log_file,
        format_string=(
            "[{time:YYYY-MM-DD HH:mm:ss.SSS}] "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        colorize=False,  # Plain text for audit logs
        rotation="100 MB",
        retention="1 year",
        compression="gz",
    )


def configure_ci_logging():
    """
    Configure logging for CI/CD environments.

    Simple, non-colored output suitable for automated pipelines.

    Examples:
        >>> from logicpwn import configure_ci_logging
        >>> configure_ci_logging()
    """
    return configure_logging(
        level="INFO",
        format_string="{time:HH:mm:ss} | {level} | {message}",
        colorize=False,
    )


def disable_logging():
    """
    Disable all logging output.

    Useful for tests or when you need complete silence.

    Examples:
        >>> from logicpwn import disable_logging
        >>> disable_logging()
    """
    logger.remove()
    logger.info("Logging disabled")


# Quick access presets
PRESETS = {
    "default": configure_logging,
    "minimal": configure_minimal_logging,
    "debug": configure_debug_logging,
    "security": configure_security_logging,
    "ci": configure_ci_logging,
}


def use_preset(preset_name: str, **kwargs):
    """
    Use a predefined logging preset.

    Args:
        preset_name: Name of preset ("default", "minimal", "debug", "security", "ci")
        **kwargs: Additional arguments to pass to the preset function

    Returns:
        Configured logger instance

    Examples:
        >>> from logicpwn import use_logging_preset
        >>> use_logging_preset("debug")
        >>> use_logging_preset("security", log_file="my_audit.log")
    """
    if preset_name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")

    preset_func = PRESETS[preset_name]
    return preset_func(**kwargs)


# Export public API
__all__ = [
    "configure_logging",
    "configure_minimal_logging",
    "configure_debug_logging",
    "configure_security_logging",
    "configure_ci_logging",
    "disable_logging",
    "use_preset",
]
