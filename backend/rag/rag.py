
from utils.utils import get_logger
from db.dbo import get_vector_store
from utils.constants import OLLAMA_LLM_MODEL, BASE_PROMPT, SESSION_NAME_PROMPT
from db.models import Message

from typing import List, Tuple
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama

logger = get_logger()

# Prepare vector store (read-only)

_vectordb = get_vector_store()
_retriever = _vectordb.as_retriever(search_kwargs={"k": 4})
_llm = ChatOllama(model=OLLAMA_LLM_MODEL, temperature=0)


def format_history(pairs: List[Tuple[str, str]]) -> str:
    lines = []
    for role, content in pairs:
        lines.append(f"{role.title()}: {content}")
    return "\n".join(lines)


async def run_rag(question: str, history: List[Tuple[str, str]]):
    # Retrieve docs
    docs: List[Document] = _retriever.get_relevant_documents(question)
    context = "\n---\n".join([d.page_content for d in docs])
    messages = BASE_PROMPT.format_messages(
        context=context,
        history=format_history(history),
        question=question)
    logger.info(f"RAG prompt: {messages}")
    resp = await _llm.ainvoke(messages)
    # Gather metadata for sources
    sources = []
    for d in docs:
        src = {
            "id": d.metadata.get("id") or d.metadata.get("source") or "unknown",
            "source": d.metadata.get("source") or d.metadata.get("path") or "",
            "page": d.metadata.get("page") or d.metadata.get("loc") or None,
            "score": d.metadata.get("score") or None,
        }
        sources.append(src)
    return resp.content, sources


async def create_session_name(messages: List[Message]) -> str:
    prompt = SESSION_NAME_PROMPT.format_messages(
        messages=[msg.content for msg in messages[:6] if msg.role != "system"]
    )
    resp = await _llm.ainvoke(prompt)
    return resp.content.strip().strip('"').strip("'")