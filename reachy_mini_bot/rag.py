from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import chromadb
from chromadb.api import ClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


@dataclass
class RetrievedDoc:
    doc_id: str
    text: str
    source: Optional[str]


class RAGStore:
    def __init__(self, path: str, collection: str, openai_api_key: str, embedding_model: str):
        os.makedirs(path, exist_ok=True)
        self.client: ClientAPI = chromadb.PersistentClient(path=path)
        self.embedding = OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name=embedding_model,
        )
        self.collection = self.client.get_or_create_collection(
            name=collection,
            embedding_function=self.embedding,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, ids: List[str], texts: List[str], metadatas: Optional[List[dict]] = None) -> None:
        # Chroma is idempotent on ids; newer add of existing ids will fail unless we handle upsert via delete
        # To keep it simple, delete existing ids first (if any)
        if ids:
            try:
                self.collection.delete(ids=ids)
            except Exception:
                pass
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def query(self, text: str, k: int = 5) -> List[RetrievedDoc]:
        if not text.strip():
            return []
        # Note: 'ids' is always returned by Chroma and must NOT be listed in 'include'.
        res = self.collection.query(
            query_texts=[text],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        docs: List[RetrievedDoc] = []
        if res and res.get("documents"):
            for i, doc in enumerate(res["documents"][0]):
                meta = None
                if res.get("metadatas") and res["metadatas"][0] and i < len(res["metadatas"][0]):
                    meta = res["metadatas"][0][i]
                doc_id = res["ids"][0][i] if res.get("ids") else str(i)
                docs.append(
                    RetrievedDoc(
                        doc_id=doc_id,
                        text=doc,
                        source=(meta or {}).get("source") if meta else None,
                    )
                )
        return docs


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    text = text.replace("\r\n", "\n")
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks
