from __future__ import annotations

import argparse
import asyncio
import base64
import json
from dataclasses import asdict, dataclass
from typing import Any

from mcp.client import Client

from .config import settings
from .embeddings import EmbeddingModel
from .odoo_ingest import delete_odoo_document, ingest_odoo_document
from .odoo_mcp_server import mcp
from .vector_store import VectorStore


@dataclass(frozen=True)
class WorkerSummary:
    claimed: int = 0
    indexed: int = 0
    deleted: int = 0
    errors: int = 0


async def _call_json(client: Client, name: str, arguments: dict | None = None) -> Any:
    result = await client.call_tool(name, arguments or {})
    if result.is_error:
        message = "\n".join(
            getattr(item, "text", str(item)) for item in result.content
        )
        raise RuntimeError(message or f"MCP tool {name} failed")
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        if set(structured) == {"result"}:
            return structured["result"]
        return structured
    for item in result.content:
        text = getattr(item, "text", None)
        if text is not None:
            return json.loads(text)
    return None


async def process_once(
    client: Client,
    *,
    limit: int,
    embedding_model: EmbeddingModel,
    vector_store: VectorStore,
) -> WorkerSummary:
    jobs = await _call_json(client, "claim_pending_rag_documents", {"limit": limit})
    indexed = deleted = errors = 0
    for job in jobs or []:
        document_id = int(job["document_id"])
        try:
            if job.get("operation") == "delete":
                delete_odoo_document(document_id, vector_store=vector_store)
                await _call_json(
                    client,
                    "mark_rag_document_vectors_deleted",
                    {"document_id": document_id},
                )
                deleted += 1
                continue

            await _call_json(
                client,
                "update_rag_document_progress",
                {
                    "document_id": document_id,
                    "progress": 10,
                    "stage": "Đang tải tệp gốc từ Odoo",
                },
            )
            payload = await _call_json(
                client,
                "get_rag_document_payload",
                {"document_id": document_id},
            )
            loop = asyncio.get_running_loop()

            def report_progress(progress: int, stage: str) -> None:
                future = asyncio.run_coroutine_threadsafe(
                    _call_json(
                        client,
                        "update_rag_document_progress",
                        {
                            "document_id": document_id,
                            "progress": progress,
                            "stage": stage,
                        },
                    ),
                    loop,
                )
                future.result(timeout=30)

            result = await asyncio.to_thread(
                ingest_odoo_document,
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
            await _call_json(
                client,
                "mark_rag_document_indexed",
                {
                    "document_id": document_id,
                    "chunk_count": result.chunk_count,
                    "checksum": result.checksum,
                    "collection": result.collection,
                    "storage_backend": result.storage_backend,
                    "storage_location": result.storage_location,
                    "chunk_previews": list(result.chunk_previews),
                    "page_count": result.page_count,
                    "clean_char_count": result.clean_char_count,
                    "chunk_size": result.chunk_size,
                    "chunk_overlap": result.chunk_overlap,
                    "embedding_model": result.embedding_model,
                },
            )
            indexed += 1
            print(
                f"[INDEXED] document_id={document_id}, chunks={result.chunk_count}, "
                f"collection={result.collection}"
            )
        except Exception as exc:
            errors += 1
            try:
                await _call_json(
                    client,
                    "mark_rag_document_error",
                    {"document_id": document_id, "error_message": str(exc)[:2000]},
                )
            except Exception as report_error:
                print(f"[ERROR] Không thể ghi lỗi document_id={document_id}: {report_error}")
            print(f"[ERROR] document_id={document_id}: {exc}")
    return WorkerSummary(len(jobs or []), indexed, deleted, errors)


async def run_worker(*, once: bool, interval: float, limit: int) -> None:
    print("Đang kết nối ChromaDB và nạp embedding model...")
    store = VectorStore()
    store.get_or_create_collection()
    model = EmbeddingModel()
    async with Client(mcp, raise_exceptions=True) as client:
        while True:
            try:
                summary = await process_once(
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
            await asyncio.sleep(max(0.5, interval))


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatic Odoo upload-to-RAG worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=settings.rag_worker_interval)
    parser.add_argument("--limit", type=int, default=settings.rag_worker_batch_size)
    args = parser.parse_args()
    asyncio.run(run_worker(once=args.once, interval=args.interval, limit=args.limit))


if __name__ == "__main__":
    main()
