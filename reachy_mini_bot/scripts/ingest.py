from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from typing import List, Tuple

from bs4 import BeautifulSoup

from ..config import load_settings
from ..rag import RAGStore, chunk_text


TEXT_EXTS = {".txt", ".md", ".log"}
HTML_EXTS = {".html", ".htm"}
PDF_EXTS = {".pdf"}


def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTS:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix in HTML_EXTS:
        html = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n")
    if suffix in PDF_EXTS:
        try:
            from pdfminer.high_level import extract_text
        except Exception as e:
            raise RuntimeError("pdfminer.six is required for PDF ingestion") from e
        return extract_text(str(path))
    return ""


def file_id(path: Path, chunk_idx: int) -> str:
    h = hashlib.sha1(f"{str(path)}::{chunk_idx}".encode("utf-8")).hexdigest()
    return h


def ingest_folder(folder: Path, store: RAGStore) -> None:
    paths: List[Path] = []
    for root, _dirs, files in os.walk(folder):
        for name in files:
            p = Path(root) / name
            if p.suffix.lower() in TEXT_EXTS | HTML_EXTS | PDF_EXTS:
                paths.append(p)
    ids: List[str] = []
    docs: List[str] = []
    metas: List[dict] = []
    for p in sorted(paths):
        text = read_file(p)
        if not text.strip():
            continue
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            ids.append(file_id(p, idx))
            docs.append(chunk)
            metas.append({"source": str(p)})
    if ids:
        store.add_documents(ids, docs, metas)


def main():
    parser = argparse.ArgumentParser(description="Ingest a folder into the local RAG DB")
    parser.add_argument("folder", type=str, help="Path to folder with docs")
    args = parser.parse_args()

    settings = load_settings()
    store = RAGStore(
        path=settings.rag_db_path,
        collection=settings.rag_collection,
        openai_api_key=settings.openai_api_key,
        embedding_model=settings.openai_embedding_model,
    )

    folder = Path(args.folder)
    if not folder.exists():
        raise SystemExit(f"Folder does not exist: {folder}")
    ingest_folder(folder, store)
    print(f"Ingested documents from {folder} into {settings.rag_collection} at {settings.rag_db_path}")


if __name__ == "__main__":
    main()

