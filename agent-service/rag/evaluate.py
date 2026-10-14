from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import settings
from .retrieval import Retriever


def load_cases(path: Path) -> list[dict]:
    cases = []
    with path.open("r", encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL lỗi tại dòng {line_number}: {exc}") from exc
            if not item.get("question") or not item.get("expected_source"):
                raise ValueError(f"Dòng {line_number} thiếu question hoặc expected_source")
            cases.append(item)
    return cases


def evaluate(path: Path, top_k: int) -> int:
    cases = load_cases(path)
    if not cases:
        raise ValueError("Bộ test đang rỗng")

    retriever = Retriever()
    hits = 0
    reciprocal_rank_sum = 0.0

    for index, case in enumerate(cases, start=1):
        results = retriever.search(case["question"], top_k=top_k)
        expected = case["expected_source"].lower()
        matched_rank = next(
            (
                result.rank
                for result in results
                if expected in result.source_name.lower()
                or expected in result.source_path.lower()
            ),
            None,
        )
        if matched_rank is not None:
            hits += 1
            reciprocal_rank_sum += 1.0 / matched_rank
            status = f"PASS (rank={matched_rank})"
        else:
            status = "FAIL"

        top_source = results[0].citation if results else "Không có kết quả"
        print(f"[{index:02d}] {status}: {case['question']}")
        print(f"     Kỳ vọng: {case['expected_source']}")
        print(f"     Top 1:   {top_source}")

    recall = hits / len(cases)
    mrr = reciprocal_rank_sum / len(cases)
    print("\nKẾT QUẢ ĐÁNH GIÁ RETRIEVAL")
    print(f"Số test: {len(cases)}")
    print(f"Recall@{top_k}: {recall:.2%} ({hits}/{len(cases)})")
    print(f"MRR@{top_k}: {mrr:.4f}")
    return 0 if hits == len(cases) else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Đánh giá retrieval bằng bộ câu hỏi JSONL.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=settings.base_dir / "data" / "eval" / "retrieval_cases.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=3)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        exit_code = evaluate(args.cases.resolve(), top_k=args.top_k)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
