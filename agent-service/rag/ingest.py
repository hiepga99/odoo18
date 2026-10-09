from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .chunking import Chunk, chunk_units
from .config import settings
from .embeddings import EmbeddingModel
from .loaders import discover_documents, load_document
from .vector_store import VectorStore


def _batches(items: list[Chunk], batch_size: int):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def ingest(
    data_dir: Path,
    reset: bool = False,
    batch_size: int = settings.embedding_batch_size,
) -> int:
    documents = discover_documents(data_dir)
    if not documents:
        raise RuntimeError(
            f"Không tìm thấy PDF, DOCX, TXT hoặc MD trong: {data_dir}"
        )

    units = []
    print(f"Tìm thấy {len(documents)} tài liệu:")
    for path in documents:
        loaded = load_document(path, data_dir)
        units.extend(loaded)
        print(f"  - {path.name}: {len(loaded)} đơn vị văn bản")

    chunks = chunk_units(
        units,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise RuntimeError("Không trích xuất được văn bản nào từ tài liệu.")

    print(f"Đã tạo {len(chunks)} chunk.")
    model = EmbeddingModel()
    all_embeddings: list[list[float]] = []
    for batch in _batches(chunks, batch_size):
        embeddings = model.encode_documents(
            [chunk.text for chunk in batch],
            batch_size=batch_size,
            show_progress_bar=True,
        )
        all_embeddings.extend(embeddings)
        print(f"Đã encode {len(all_embeddings)}/{len(chunks)} chunk.")

    # Chỉ thay đổi index sau khi toàn bộ embedding đã tạo thành công. Nhờ đó,
    # lỗi tải model hoặc lỗi encode không làm mất collection đang sử dụng.
    store = VectorStore()
    if reset:
        print("Đang xóa collection cũ theo yêu cầu --reset...")
        store.reset()
    else:
        store.delete_sources([chunk.source_path for chunk in chunks])

    stored = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings = all_embeddings[start : start + batch_size]
        store.upsert(batch, embeddings)
        stored += len(batch)
        print(f"Đã lưu {stored}/{len(chunks)} chunk vào ChromaDB.")

    total = store.count()
    print("\nINGEST THÀNH CÔNG")
    print(f"Collection: {settings.collection_name}")
    print(f"ChromaDB: {settings.chroma_dir}")
    print(f"Tổng số chunk trong collection: {total}")
    return total


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Đọc tài liệu, tạo embedding BGE-M3 và lưu vào ChromaDB."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=settings.raw_data_dir,
        help=f"Thư mục tài liệu (mặc định: {settings.raw_data_dir})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Xóa collection cũ trước khi index lại toàn bộ.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=settings.embedding_batch_size,
        help="Số chunk encode mỗi batch.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        ingest(args.data_dir.resolve(), reset=args.reset, batch_size=args.batch_size)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
