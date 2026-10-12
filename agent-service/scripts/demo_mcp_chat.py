from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

from mcp import Client


def _read_tool_result(result) -> Any:
    if result.is_error:
        message = "\n".join(
            getattr(item, "text", str(item)) for item in result.content
        )
        raise RuntimeError(message or "MCP tool trả về lỗi")

    structured = getattr(result, "structured_content", None)
    if structured is not None:
        if isinstance(structured, dict) and set(structured) == {"result"}:
            return structured["result"]
        return structured

    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            return json.loads(text)
    return None


async def ask(question: str, *, url: str, top_k: int) -> dict:
    async with Client(url, read_timeout_seconds=120) as client:
        result = await client.call_tool(
            "answer_internal_documents",
            {"question": question, "top_k": top_k},
        )
    payload = _read_tool_result(result)
    if not isinstance(payload, dict):
        raise RuntimeError("MCP không trả về object answer/sources hợp lệ")
    return payload


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Ví dụ backend chatbot gọi RAG qua MCP."
    )
    parser.add_argument("question", help="Câu hỏi tiếng Việt")
    parser.add_argument(
        "--url",
        default=os.getenv("MCP_URL", "http://127.0.0.1:8010/mcp"),
    )
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    payload = asyncio.run(
        ask(args.question, url=args.url, top_k=max(1, min(args.top_k, 20)))
    )
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("\nTRẢ LỜI")
    print(payload.get("answer", ""))
    print("\nNGUỒN")
    for source in payload.get("sources", []):
        print(
            f"[{source.get('rank')}] {source.get('citation')} "
            f"(similarity={source.get('similarity', 0):.4f}, "
            f"document_id={source.get('odoo_document_id')})"
        )


if __name__ == "__main__":
    main()
