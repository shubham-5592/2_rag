from utils.constants import OLLAMA_EMBEDDING_MODEL

from langchain_ollama import OllamaEmbeddings

import logging
import time
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(funcName)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def timeit(func):
    """Decorator to time a function."""
    def wrapper(*args, **kwargs):
        logger.info(f"Function '{func.__name__}' | Started ...")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"Function '{func.__name__}' | Completed in {end - start:.4f} seconds.")
        return result
    return wrapper


@timeit
def get_embedding_model():
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    return embeddings


def get_logger():
    return logger
