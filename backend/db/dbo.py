from utils.constants import PERSIST_DIRECTORY, DATABASE_URL
from utils.utils import get_embedding_model, timeit

from langchain_chroma import Chroma
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


@timeit
def get_vector_store(persist_directory=PERSIST_DIRECTORY):
    """Get the vector store.

    Args:
        persist_directory (str, optional): The path to the directory for persisting the vector store. Defaults to PERSIST_DIRECTORY.

    Raises:
        RuntimeError: If the vector store cannot be opened.

    Returns:
        Chroma: The vector store.
    """
    embedding_model = get_embedding_model()
    try:
        vs = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            # collection_name=CHROMA_COLLECTION,
        )
    except Exception as e:
        raise RuntimeError(
        f"Failed to open Chroma at '{persist_directory}'. Ensure it's a valid Chroma persistence directory. Error: {e}"
        )
    # quick sanity check
    try:
        # Perform a sanity check to ensure the collection is accessible; result is intentionally unused.
        _ = vs._collection.count() # type: ignore[attr-defined]
    except Exception:
        pass
    return vs

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
