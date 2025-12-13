import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    discord_token: str
    openai_api_key: str
    rag_db_path: str = "./rag_db"
    rag_documents_path: str = "./rag_documents"
    rag_collection: str = "reachy_mini"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    thread_history_limit: int = 25


def load_settings() -> Settings:
    load_dotenv(override=False)
    # Prefer lowercase `discord_token`, fall back to `DISCORD_TOKEN`
    discord_token = os.getenv("discord_token", os.getenv("DISCORD_TOKEN", "")).strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    rag_db_path = os.getenv("RAG_DB_PATH", "./rag_db").strip()
    rag_documents_path = os.getenv("RAG_DOCUMENTS_PATH", "./rag_documents").strip()
    rag_collection = os.getenv("RAG_COLLECTION", "reachy_mini").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    openai_embedding_model = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    ).strip()
    # Optional: number of prior messages from the current thread to include
    try:
        thread_history_limit = int(os.getenv("THREAD_HISTORY_LIMIT", "25").strip())
    except Exception:
        thread_history_limit = 25

    if not discord_token:
        raise RuntimeError("discord_token is required. Set it in .env or env vars.")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required. Set it in .env or env vars.")

    return Settings(
        discord_token=discord_token,
        openai_api_key=openai_api_key,
        rag_db_path=rag_db_path,
        rag_documents_path=rag_documents_path,
        rag_collection=rag_collection,
        openai_model=openai_model,
        openai_embedding_model=openai_embedding_model,
        thread_history_limit=thread_history_limit,
    )
