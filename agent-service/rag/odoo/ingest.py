from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Callable

from ..chunking import chunk_units
from ..config import settings
from ..embeddings import EmbeddingModel
from ..loaders import MetadataValue, load_document_bytes
from ..vector_store import VectorStore


@dataclass(frozen=True)
class OdooIngestResult:
    odoo_document_id: int
    odoo_attachment_id: int
    filename: str
    checksum: str
    chunk_count: int
    collection: str
    storage_backend: str
    storage_location: str
    chunk_previews: tuple[dict, ...]
    page_count: int = 0
    clean_char_count: int = 0
    chunk_size: int = 0
    chunk_overlap: int = 0
    embedding_model: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def ingest_odoo_document(
    *,
    content: bytes,
    filename: str,
    odoo_document_id: int,
    odoo_attachment_id: int,
    company_id: int,
    checksum: str = "",
    access_scope: str = "internal",
    extra_metadata: dict[str, MetadataValue] | None = None,
    embedding_model: EmbeddingModel | None = None,
    vector_store: VectorStore | None = None,
    progress_callback: Callable[[int, str], None] | None = None,
) -> OdooIngestResult:
    """Index bytes fetched from Odoo by the background worker.

    The source binary remains in ``ir.attachment``. ChromaDB only receives text
    chunks, embeddings and identifiers needed to enforce Odoo access decisions.
    """

    if odoo_document_id <= 0:
        raise ValueError("odoo_document_id phải lớn hơn 0")
    if odoo_attachment_id <= 0:
        raise ValueError("odoo_attachment_id phải lớn hơn 0")
    if company_id < 0:
        raise ValueError("company_id không được âm")

    def report(progress: int, stage: str) -> None:
        if progress_callback:
            progress_callback(progress, stage)

    report(15, "Đang đọc và trích xuất nội dung tệp")
    file_checksum = checksum.strip() or hashlib.sha256(content).hexdigest()
    metadata: dict[str, MetadataValue] = {
        **(extra_metadata or {}),
        "odoo_document_id": odoo_document_id,
        "odoo_attachment_id": odoo_attachment_id,
        "company_id": company_id,
        "checksum": file_checksum,
        "access_scope": access_scope,
    }
    source_path = f"odoo://ai.rag.document/{odoo_document_id}"
    units = load_document_bytes(
        content,
        filename,
        source_path=source_path,
        metadata=metadata,
    )
    chunks = chunk_units(
        units,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise RuntimeError("Không trích xuất được văn bản từ attachment Odoo")

    report(35, f"Đã làm sạch và chia thành {len(chunks)} đoạn")
    model = embedding_model or EmbeddingModel()
    report(45, "Đang nạp mô hình và tạo embedding")
    embeddings = model.encode_documents(
        [chunk.text for chunk in chunks],
        batch_size=settings.embedding_batch_size,
        show_progress_bar=False,
    )

    report(80, "Đã tạo embedding, đang chuẩn bị kho vector")
    store = vector_store or VectorStore()
    # Replace all previous chunks for the same Odoo document only after the new
    # embeddings are ready, so an embedding failure leaves the old index intact.
    store.delete_where({"odoo_document_id": odoo_document_id})
    report(90, "Đang lưu vector vào ChromaDB")
    store.upsert(chunks, embeddings)
    report(95, "Đã lưu vector, đang cập nhật kết quả về Odoo")

    return OdooIngestResult(
        odoo_document_id=odoo_document_id,
        odoo_attachment_id=odoo_attachment_id,
        filename=filename,
        checksum=file_checksum,
        chunk_count=len(chunks),
        collection=store.collection_name,
        storage_backend="ChromaDB HTTP" if store.mode == "http" else "ChromaDB embedded",
        storage_location=store.location,
        chunk_previews=tuple(
            {
                "vector_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page": chunk.page,
                "source_name": chunk.source_name,
                "char_count": len(chunk.text),
                "text_preview": chunk.text[:1000],
            }
            for chunk in chunks
        ),
        page_count=len({(unit.source_path, unit.page) for unit in units}),
        clean_char_count=sum(len(unit.text) for unit in units),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        embedding_model=settings.embedding_model,
    )


def delete_odoo_document(
    odoo_document_id: int,
    *,
    vector_store: VectorStore | None = None,
) -> None:
    if odoo_document_id <= 0:
        raise ValueError("odoo_document_id phải lớn hơn 0")
    (vector_store or VectorStore()).delete_where(
        {"odoo_document_id": odoo_document_id}
    )
