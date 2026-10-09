from __future__ import annotations

import argparse
import sys

from openai import OpenAI

from .config import settings
from .retrieval import Retriever, SearchResult


SYSTEM_PROMPT = """Bạn là trợ lý tra cứu tài liệu nội bộ bằng tiếng Việt.
Chỉ trả lời dựa trên NGỮ CẢNH được cung cấp.
Nếu ngữ cảnh không đủ, hãy nói rõ: "Tôi chưa tìm thấy đủ thông tin trong tài liệu hiện có."
Không tự tạo chính sách, số liệu, thời hạn hoặc điều kiện.
Sau mỗi khẳng định quan trọng, trích dẫn bằng ký hiệu [1], [2] tương ứng với ngữ cảnh.
Trả lời ngắn gọn, rõ ràng và nêu cả ngoại lệ có liên quan.
"""


def build_context(results: list[SearchResult]) -> str:
    blocks = []
    for result in results:
        blocks.append(
            f"[{result.rank}] Nguồn: {result.citation}\n"
            f"Độ tương đồng: {result.similarity:.4f}\n"
            f"Nội dung:\n{result.text}"
        )
    return "\n\n".join(blocks)


def answer_question(question: str, top_k: int = settings.default_top_k) -> tuple[str, list[SearchResult]]:
    supported_providers = {"ollama", "nvidia", "openai-compatible"}
    if settings.llm_provider not in supported_providers:
        raise RuntimeError(
            f"LLM_PROVIDER không được hỗ trợ: {settings.llm_provider}. "
            f"Các giá trị hợp lệ: {', '.join(sorted(supported_providers))}."
        )

    if settings.llm_provider != "ollama" and not settings.llm_api_key:
        raise RuntimeError(
            "Thiếu LLM_API_KEY cho backend đã chọn. Hãy sao chép .env.example thành .env "
            "và điền API key."
        )

    results = Retriever().search(question, top_k=top_k)
    context = build_context(results)
    client = OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key or "ollama",
        timeout=90.0,
    )
    request_options = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"NGỮ CẢNH:\n{context}\n\nCÂU HỎI:\n{question}",
            },
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": settings.llm_max_tokens,
    }
    if settings.llm_provider == "nvidia":
        request_options["extra_body"] = {
            "chat_template_kwargs": {
                "enable_thinking": settings.llm_enable_thinking,
            }
        }

    response = client.chat.completions.create(**request_options)
    answer = response.choices[0].message.content or ""
    return answer.strip(), results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RAG đầy đủ: retrieval bằng BGE-M3 và trả lời bằng LLM đã cấu hình."
    )
    parser.add_argument("question", help="Câu hỏi tiếng Việt.")
    parser.add_argument("--top-k", type=int, default=settings.default_top_k)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        answer, results = answer_question(args.question, top_k=args.top_k)
    except Exception as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("\nTRẢ LỜI")
    print(answer)
    print("\nNGUỒN TRUY XUẤT")
    for result in results:
        print(f"[{result.rank}] {result.citation} - similarity={result.similarity:.4f}")


if __name__ == "__main__":
    main()
