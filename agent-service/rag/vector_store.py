from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings

from .chunking import Chunk
from .config import settings


class VectorStore:
    def __init__(
        self,
        path: Path = settings.chroma_dir,
        collection_name: str = settings.collection_name,
        embedding_model: str = settings.embedding_model,
        mode: str = settings.chroma_mode,
        host: str = settings.chroma_host,
        port: int = settings.chroma_port,
        ssl: bool = settings.chroma_ssl,
        headers: dict[str, str] | None = None,
        client: Any | None = None,
    ) -> None:
        self.path = path
        self.collection_name = collection_name
        self.mode = mode.strip().lower()
        self.host = host
        self.port = port
        self.ssl = ssl
        if client is not None:
            self.client = client
        elif self.mode == "embedded":
            path.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        elif self.mode == "http":
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                ssl=ssl,
                headers=headers if headers is not None else settings.chroma_headers,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            raise ValueError("RAG_CHROMA_MODE phải là 'embedded' hoặc 'http'")
        self.embedding_model = embedding_model

    @property
    def location(self) -> str:
        if self.mode == "embedded":
            return str(self.path)
        scheme = "https" if self.ssl else "http"
        return f"{scheme}://{self.host}:{self.port}/{self.collection_name}"

    def collection_exists(self) -> bool:
        return self.collection_name in {item.name for item in self.client.list_collections()}

    def reset(self) -> None:
        if self.collection_exists():
            self.client.delete_collection(self.collection_name)

    def get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": self.embedding_model,
                "language": "vi",
            },
        )

    def get_collection(self):
        if not self.collection_exists():
            raise RuntimeError(
                "Chưa có Chroma collection. Hãy chạy: python -m rag.ingest --reset"
            )
        return self.client.get_collection(self.collection_name)

    def delete_sources(self, source_paths: Sequence[str]) -> None:
        collection = self.get_or_create_collection()
        for source_path in sorted(set(source_paths)):
            collection.delete(where={"source_path": source_path})

    def delete_where(self, where: dict) -> None:
        self.get_or_create_collection().delete(where=where)

    def upsert(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Số chunk và embedding không khớp")
        collection = self.get_or_create_collection()
        collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata() for chunk in chunks],
            embeddings=[list(vector) for vector in embeddings],
        )

    def count(self) -> int:
        return self.get_collection().count()

    def query(
        self,
        query_embedding: Sequence[float],
        top_k: int,
        where: dict | None = None,
    ) -> dict:
        collection = self.get_collection()
        count = collection.count()
        if count == 0:
            raise RuntimeError("Collection đang rỗng. Hãy chạy lại lệnh ingest.")
        query_options = {
            "query_embeddings": [list(query_embedding)],
            "n_results": min(top_k, count),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_options["where"] = where
        return collection.query(
            **query_options,
        )
