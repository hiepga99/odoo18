from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rag.odoo_ingest import delete_odoo_document, ingest_odoo_document
from rag.embeddings import EmbeddingModel
from rag.retrieval import Retriever
from rag.vector_store import VectorStore


DEFAULT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "coolmate_demo"
    / "01_coolmate_chinh_sach_doi_tra_tom_tat.pdf"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mô phỏng Odoo/MCP gửi attachment bytes vào RAG."
    )
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--document-id", type=int, default=900001)
    parser.add_argument("--attachment-id", type=int, default=900002)
    parser.add_argument("--company-id", type=int, default=1)
    parser.add_argument(
        "--question",
        default="Khách hàng được đổi trả trong bao nhiêu ngày?",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Giữ chunks test trong collection thay vì dọn sau khi chạy.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    path = args.file.resolve()
    if not path.is_file():
        raise SystemExit(f"Không tìm thấy file test: {path}")

    store = VectorStore()
    embedding_model = EmbeddingModel()
    ingested = False
    try:
        result = ingest_odoo_document(
            content=path.read_bytes(),
            filename=path.name,
            odoo_document_id=args.document_id,
            odoo_attachment_id=args.attachment_id,
            company_id=args.company_id,
            access_scope="internal",
            extra_metadata={"smoke_test": True},
            embedding_model=embedding_model,
            vector_store=store,
        )
        ingested = True
        print("\nINGEST ATTACHMENT THÀNH CÔNG")
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

        results = Retriever(
            embedding_model=embedding_model,
            vector_store=store,
        ).search(
            args.question,
            top_k=3,
            allowed_document_ids=[args.document_id],
            company_id=args.company_id,
        )
        if not results:
            raise RuntimeError("Không tìm thấy document vừa ingest khi áp dụng access filter")

        print("\nRETRIEVAL CÓ PHÂN QUYỀN THÀNH CÔNG")
        print(
            json.dumps(
                [item.to_dict() for item in results],
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        if ingested and not args.keep:
            delete_odoo_document(args.document_id, vector_store=store)
            print(f"\nĐã dọn document test {args.document_id} khỏi vector store.")


if __name__ == "__main__":
    main()
