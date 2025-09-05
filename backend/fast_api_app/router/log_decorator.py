import functools
import logging
from fastapi import Request
from utils.utils import get_logger

logger = get_logger()

def log_response(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        logger.info(f"Response from {func.__name__}: {response}")
        return response
    return wrapper
