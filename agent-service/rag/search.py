from __future__ import annotations

import argparse
import json
import sys

from .config import settings
from .retrieval import Retriever, SearchResult


def print_results(results: list[SearchResult], max_chars: int) -> None:
    if not results:
        print("Không tìm thấy đoạn tài liệu phù hợp.")
        return
    for result in results:
        content = result.text
        if max_chars > 0 and len(content) > max_chars:
            content = content[:max_chars].rstrip() + "..."
        print(f"\n[{result.rank}] {result.citation}")
        print(f"    Điểm tương đồng: {result.similarity:.4f}")
        print(f"    {content}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tìm các đoạn tài liệu liên quan nhất trong ChromaDB."
    )
    parser.add_argument("question", help="Câu hỏi tiếng Việt cần tìm kiếm.")
    parser.add_argument("--top-k", type=int, default=settings.default_top_k)
    parser.add_argument(
        "--max-chars",
        type=int,
        default=700,
        help="Số ký tự nội dung tối đa in cho mỗi kết quả; 0 để in toàn bộ.",
    )
    parser.add_argument("--json", action="store_true", help="Xuất JSON thay vì văn bản.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        results = Retriever().search(args.question, top_k=args.top_k)
    except (RuntimeError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if args.json:
        print(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))
    else:
        print(f"Câu hỏi: {args.question}")
        print_results(results, max_chars=args.max_chars)


if __name__ == "__main__":
    main()
