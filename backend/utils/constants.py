import os
from pathlib import Path

from langchain.prompts import ChatPromptTemplate

OLLAMA_LLM_MODEL: str = "gemma2:2b"
OLLAMA_EMBEDDING_MODEL: str = "mxbai-embed-large"
PERSIST_DIRECTORY: str = str(os.path.join(Path(__file__).parent.parent, "db", "aqi_data"))
DATA_FOLDER: str = str(os.path.join(Path(__file__).parent.parent, "data_ingestion", "data_files"))
DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(Path(__file__).parent.parent, 'db', 'rag.db')}"
BACKEND_HOST: str = "0.0.0.0"
BACKEND_PORT: int = 8000
FRONTEND_ORIGIN: str = "http://localhost:5173"
STOPWORDS = set("""a an and are as at be but by for if in into is it its of on or the to with from""".split())
SYSTEM_MSG = (
    "You are a helpful assistant. Use the provided context to answer the user's question.\n"
    "If the answer isn't in the context, say you don't know. Be concise."
)
BASE_HUMAN_MSG = "Context:\n{context}\n\nChat History:\n{history}\n\nUser:{question}"

BASE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MSG),
    ("human", BASE_HUMAN_MSG),
])

SESSION_NAME_PROMPT = ChatPromptTemplate.from_messages([
    ("user", "Generate a short 3-4 word session name from the following messages:\n{messages}")
])