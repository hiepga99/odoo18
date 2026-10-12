from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Callable, Protocol

from .embeddings import EmbeddingModel
from .odoo_ingest import delete_odoo_document, ingest_odoo_document
from .vector_store import VectorStore


class OdooRagGateway(Protocol):
    """Transport-neutral contract implemented by the backend's MCP client."""

    def claim_pending_documents(self, limit: int) -> list[dict]: ...

    def get_document_payload(self, document_id: int) -> dict: ...

    def mark_document_indexed(
        self,
        document_id: int,
        chunk_count: int,
        checksum: str,
        collection: str,
        storage_backend: str = "ChromaDB",
        storage_location: str = "",
        chunk_previews: tuple[dict, ...] = (),
        page_count: int = 0,
        clean_char_count: int = 0,
        chunk_size: int = 0,
        chunk_overlap: int = 0,
        embedding_model: str = "",
    ) -> None: ...

    def mark_document_error(self, document_id: int, error_message: str) -> None: ...

    def mark_document_vectors_deleted(self, document_id: int) -> None: ...


@dataclass(frozen=True)
class SyncSummary:
    claimed: int = 0
    indexed: int = 0
    deleted: int = 0
    errors: int = 0


def sync_pending_documents(
    gateway: OdooRagGateway,
    *,
    limit: int = 10,
    embedding_model: EmbeddingModel | None = None,
    vector_store: VectorStore | None = None,
    ingest: Callable = ingest_odoo_document,
    delete: Callable = delete_odoo_document,
) -> SyncSummary:
    """Process jobs claimed through MCP without coupling RAG to Odoo's HTTP API."""
    jobs = gateway.claim_pending_documents(limit)
    indexed = deleted = errors = 0
    model = embedding_model
    store = vector_store

    for job in jobs:
        document_id = int(job["document_id"])
        try:
            if job.get("operation") == "delete":
                delete(document_id, vector_store=store)
                gateway.mark_document_vectors_deleted(document_id)
                deleted += 1
                continue

            payload = gateway.get_document_payload(document_id)
            encoded = payload.get("content_base64", "")
            content = base64.b64decode(encoded)
            result = ingest(
                content=content,
                filename=payload["file_name"],
                odoo_document_id=document_id,
                odoo_attachment_id=int(payload["attachment_id"]),
                company_id=int(payload["company_id"]),
                checksum=payload.get("checksum", ""),
                embedding_model=model,
                vector_store=store,
            )
            gateway.mark_document_indexed(
                document_id,
                result.chunk_count,
                result.checksum,
                result.collection,
                getattr(result, "storage_backend", "ChromaDB"),
                getattr(result, "storage_location", ""),
                getattr(result, "chunk_previews", ()),
                getattr(result, "page_count", 0),
                getattr(result, "clean_char_count", 0),
                getattr(result, "chunk_size", 0),
                getattr(result, "chunk_overlap", 0),
                getattr(result, "embedding_model", ""),
            )
            indexed += 1
        except Exception as exc:
            gateway.mark_document_error(document_id, str(exc))
            errors += 1

    return SyncSummary(
        claimed=len(jobs),
        indexed=indexed,
        deleted=deleted,
        errors=errors,
    )
