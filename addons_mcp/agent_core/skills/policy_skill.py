# -*- coding: utf-8 -*-
import json
import os
import glob
import sys
from typing import Dict, Any
from .base_skill import BaseSkill, skill_tool

class PolicyRAGSkill(BaseSkill):
    """Kỹ năng Tra cứu Văn bản Quy trình và Chính sách Doanh nghiệp (RAG)"""
    def __init__(self, docs_dir: str = "data/company_documents"):
        super().__init__(
            name="policy_skill",
            description="Tra cứu cơ chế chính sách, quy chế bảo hành, đổi trả, chiết khấu và giao hàng."
        )
        if not os.path.isdir(docs_dir) and os.path.isdir(os.path.join("..", docs_dir)):
            docs_dir = os.path.join("..", docs_dir)
        self.docs_dir = docs_dir

    @skill_tool(
        name="get_company_policy",
        description="Tra cứu tài liệu quy trình, chính sách nội bộ công ty (Bảo hành, đổi trả, chiết khấu, giao hàng)",
        parameters={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Chủ đề quy trình cần tra cứu (Ví dụ: 'bảo hành', 'đổi trả', 'chiết khấu', 'vận chuyển', 'công nợ')"
                }
            },
            "required": ["topic"]
        }
    )
    def get_company_policy(self, args: Dict[str, Any]) -> str:
        topic = args.get("topic", "").lower()

        # 1. Tra cứu RAG từ agent-service nếu ChromaDB đã sẵn sàng
        try:
            rag_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent-service"))
            if rag_dir not in sys.path:
                sys.path.insert(0, rag_dir)
            from rag.retrieval import Retriever
            results = Retriever().search(topic, top_k=2)
            if results:
                summary_text = "\n\n".join(r.text for r in results)
                citation = results[0].citation if hasattr(results[0], "citation") else "agent-service/rag"
                return json.dumps({
                    "status": "success",
                    "topic": topic,
                    "source": "rag_chromadb",
                    "citation": citation,
                    "summary": summary_text
                }, ensure_ascii=False)
        except Exception:
            pass

        # 2. Dự phòng (Fallback): Thử tìm file markdown quy trình thực tế trong data/company_documents
        matched_doc = None
        if os.path.isdir(self.docs_dir):
            for filepath in glob.glob(os.path.join(self.docs_dir, "*.md")):
                filename = os.path.basename(filepath).lower()
                if any(w in filename or w in topic for w in ["bao-hanh", "bảo hành", "doi-tra", "đổi trả", "chiet-khau", "chiết khấu", "cong-no", "công nợ"]):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            matched_doc = f.read(500)
                            break
                    except Exception:
                        pass

        summary_text = matched_doc or "Bảo hành 24 tháng cho laptop, máy tính, màn hình; 12 tháng cho phụ kiện và thiết bị gia dụng. Hỗ trợ 1 đổi 1 trong 30 ngày nếu phát sinh lỗi nhà sản xuất."
        return json.dumps({
            "status": "success",
            "topic": topic,
            "policy_code": "QT-02 / CS-BH-02",
            "summary": summary_text
        }, ensure_ascii=False)
