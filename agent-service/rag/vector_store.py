from __future__ import annotations

from pathlib import Path
from typing import Sequence

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
    ) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.embedding_model = embedding_model

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

    def query(self, query_embedding: Sequence[float], top_k: int) -> dict:
        collection = self.get_collection()
        count = collection.count()
        if count == 0:
            raise RuntimeError("Collection đang rỗng. Hãy chạy lại lệnh ingest.")
        return collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )
