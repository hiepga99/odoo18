from __future__ import annotations

import argparse
import base64
import time
from dataclasses import asdict, dataclass

from ..config import settings
from ..embeddings import EmbeddingModel
from ..vector_store import VectorStore
from .ingest import delete_odoo_document, ingest_odoo_document
from .rpc import OdooRpcClient


@dataclass(frozen=True)
class WorkerSummary:
    claimed: int = 0
    indexed: int = 0
    deleted: int = 0
    errors: int = 0


def process_once(
    client: OdooRpcClient,
    *,
    limit: int,
    embedding_model: EmbeddingModel,
    vector_store: VectorStore,
) -> WorkerSummary:
    jobs = client.call("worker_claim_pending_documents", limit)
    indexed = deleted = errors = 0
    for job in jobs or []:
        document_id = int(job["document_id"])
        try:
            if job.get("operation") == "delete":
                delete_odoo_document(document_id, vector_store=vector_store)
                client.call("worker_mark_document_vectors_deleted", document_id)
                deleted += 1
                continue

            client.call(
                "worker_update_document_progress",
                document_id,
                10,
                "Đang tải tệp gốc từ Odoo",
            )
            payload = client.call("worker_get_document_payload", document_id)

            def report_progress(progress: int, stage: str) -> None:
                client.call(
                    "worker_update_document_progress",
                    document_id,
                    progress,
                    stage,
                )

            result = ingest_odoo_document(
                content=base64.b64decode(payload["content_base64"]),
                filename=payload["file_name"],
                odoo_document_id=document_id,
                odoo_attachment_id=int(payload["attachment_id"]),
                company_id=int(payload["company_id"]),
                checksum=payload.get("checksum", ""),
                embedding_model=embedding_model,
                vector_store=vector_store,
                progress_callback=report_progress,
            )
            client.call(
                "worker_mark_document_indexed",
                document_id,
                result.chunk_count,
                result.checksum,
                result.collection,
                result.storage_backend,
                result.storage_location,
                list(result.chunk_previews),
                result.page_count,
                result.clean_char_count,
                result.chunk_size,
                result.chunk_overlap,
                result.embedding_model,
            )
            indexed += 1
            print(
                f"[INDEXED] document_id={document_id}, chunks={result.chunk_count}, "
                f"collection={result.collection}"
            )
        except Exception as exc:
            errors += 1
            try:
                client.call(
                    "worker_mark_document_error", document_id, str(exc)[:2000]
                )
            except Exception as report_error:
                print(f"[ERROR] Không thể ghi lỗi document_id={document_id}: {report_error}")
            print(f"[ERROR] document_id={document_id}: {exc}")
    return WorkerSummary(len(jobs or []), indexed, deleted, errors)


def run_worker(*, once: bool, interval: float, limit: int) -> None:
    print("Đang kết nối ChromaDB và nạp embedding model...")
    store = VectorStore()
    store.get_or_create_collection()
    model = EmbeddingModel()
    client = OdooRpcClient()
    while True:
        try:
            summary = process_once(
                client,
                limit=limit,
                embedding_model=model,
                vector_store=store,
            )
            if summary.claimed:
                print("[BATCH]", asdict(summary))
        except Exception as exc:
            print(f"[WORKER ERROR] {exc}")
            if once:
                raise
        if once:
            return
        time.sleep(max(0.5, interval))


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatic Odoo upload-to-RAG worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=settings.rag_worker_interval)
    parser.add_argument("--limit", type=int, default=settings.rag_worker_batch_size)
    args = parser.parse_args()
    run_worker(once=args.once, interval=args.interval, limit=args.limit)


if __name__ == "__main__":
    main()
