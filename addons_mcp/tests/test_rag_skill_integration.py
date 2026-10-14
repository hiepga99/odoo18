# -*- coding: utf-8 -*-
"""
Kiểm thử tích hợp Kỹ năng Tra cứu Quy trình (PolicyRAGSkill) với Module RAG (agent-service)
Bao gồm:
1. Luồng thành công khi RAG ChromaDB trả về dữ liệu trích dẫn
2. Luồng Fallback an toàn khi ChromaDB chưa chạy hoặc thiếu thư viện
"""
import unittest
from unittest.mock import MagicMock
import sys
import json
from addons_mcp.agent_core.skills.policy_skill import PolicyRAGSkill

class TestPolicyRAGIntegration(unittest.TestCase):
    def setUp(self):
        self.skill = PolicyRAGSkill()

    def test_rag_hit_retrieval(self):
        """Khi RAG có kết quả: Trả về văn bản kèm trích dẫn nguồn từ ChromaDB"""
        fake_retriever_mod = MagicMock()
        fake_hit = MagicMock()
        fake_hit.text = "Chính sách Coolmate: Đổi trả miễn phí 60 ngày tận nơi."
        fake_hit.citation = "01_coolmate_chinh_sach_doi_tra.pdf, trang 2"
        fake_retriever_mod.Retriever.return_value.search.return_value = [fake_hit]

        # Giả lập nạp module rag.retrieval
        original_module = sys.modules.get("rag.retrieval")
        try:
            sys.modules["rag.retrieval"] = fake_retriever_mod
            raw_res = self.skill.get_company_policy({"topic": "đổi trả"})
            res = json.loads(raw_res)

            self.assertEqual(res.get("status"), "success")
            self.assertEqual(res.get("source"), "rag_chromadb")
            self.assertEqual(res.get("citation"), "01_coolmate_chinh_sach_doi_tra.pdf, trang 2")
            self.assertIn("60 ngày", res.get("summary"))
        finally:
            if original_module is not None:
                sys.modules["rag.retrieval"] = original_module
            else:
                sys.modules.pop("rag.retrieval", None)

    def test_rag_fallback_offline(self):
        """Khi RAG gặp lỗi / offline: Tự động fallback về quy chế mặc định, không crash"""
        fake_retriever_mod = MagicMock()
        fake_retriever_mod.Retriever.side_effect = ConnectionError("ChromaDB server down")

        original_module = sys.modules.get("rag.retrieval")
        try:
            sys.modules["rag.retrieval"] = fake_retriever_mod
            raw_res = self.skill.get_company_policy({"topic": "bảo hành"})
            res = json.loads(raw_res)

            self.assertEqual(res.get("status"), "success")
            self.assertIn("Bảo hành 24 tháng", res.get("summary"))
        finally:
            if original_module is not None:
                sys.modules["rag.retrieval"] = original_module
            else:
                sys.modules.pop("rag.retrieval", None)

if __name__ == "__main__":
    unittest.main()
