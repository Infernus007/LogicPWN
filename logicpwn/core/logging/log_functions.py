"""
Convenience log functions and global logger instance for LogicPwn.
"""

from typing import Any, Optional

from .logger import LogicPwnLogger

logger = LogicPwnLogger()


def log_request(
    method: str,
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    body: Optional[Any] = None,
    timeout: Optional[int] = None,
):
    logger.log_request(method, url, headers, params, body, timeout)


def log_response(
    status_code: int,
    headers: Optional[dict] = None,
    body: Optional[Any] = None,
    response_time: Optional[float] = None,
):
    logger.log_response(status_code, headers, body, response_time)


def log_error(error: Exception, context: Optional[dict] = None):
    logger.log_error(error, context)


def log_info(message: str, data: Optional[dict] = None):
    logger.log_info(message, data)


def log_debug(message: str, data: Optional[dict] = None):
    logger.log_debug(message, data)


def log_warning(message: str, data: Optional[dict] = None):
    logger.log_warning(message, data)
