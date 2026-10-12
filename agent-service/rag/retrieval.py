from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

from .config import settings
from .embeddings import EmbeddingModel
from .vector_store import VectorStore


@dataclass(frozen=True)
class SearchResult:
    rank: int
    text: str
    source_path: str
    source_name: str
    page: int
    chunk_index: int
    distance: float
    similarity: float
    odoo_document_id: int = 0
    odoo_attachment_id: int = 0
    company_id: int = 0
    checksum: str = ""
    access_scope: str = "internal"

    @property
    def citation(self) -> str:
        page_part = f", trang {self.page}" if self.page > 0 else ""
        return f"{self.source_name}{page_part}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["citation"] = self.citation
        return data


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel()
        self.vector_store = vector_store or VectorStore()

    def search(
        self,
        query: str,
        top_k: int = settings.default_top_k,
        *,
        allowed_document_ids: Sequence[int] | None = None,
        company_id: int | None = None,
    ) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("Câu hỏi không được để trống")
        if top_k <= 0:
            raise ValueError("top_k phải lớn hơn 0")
        if allowed_document_ids is not None and not allowed_document_ids:
            return []

        # Báo lỗi collection trước khi nạp model lớn nếu người dùng chưa ingest.
        self.vector_store.get_collection()
        query_embedding = self.embedding_model.encode_query(query)
        filters: list[dict] = []
        if allowed_document_ids is not None:
            filters.append(
                {"odoo_document_id": {"$in": [int(value) for value in allowed_document_ids]}}
            )
        if company_id is not None:
            filters.append({"company_id": int(company_id)})
        where = None
        if len(filters) == 1:
            where = filters[0]
        elif filters:
            where = {"$and": filters}

        raw = self.vector_store.query(query_embedding, top_k=top_k, where=where)

        documents = (raw.get("documents") or [[]])[0]
        metadatas = (raw.get("metadatas") or [[]])[0]
        distances = (raw.get("distances") or [[]])[0]

        results: list[SearchResult] = []
        for rank, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1,
        ):
            metadata = metadata or {}
            distance_value = float(distance)
            results.append(
                SearchResult(
                    rank=rank,
                    text=document or "",
                    source_path=str(metadata.get("source_path", "")),
                    source_name=str(metadata.get("source_name", "Không rõ nguồn")),
                    page=int(metadata.get("page", 0)),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    distance=distance_value,
                    similarity=max(-1.0, min(1.0, 1.0 - distance_value)),
                    odoo_document_id=int(metadata.get("odoo_document_id", 0)),
                    odoo_attachment_id=int(metadata.get("odoo_attachment_id", 0)),
                    company_id=int(metadata.get("company_id", 0)),
                    checksum=str(metadata.get("checksum", "")),
                    access_scope=str(metadata.get("access_scope", "internal")),
                )
            )
        return results
