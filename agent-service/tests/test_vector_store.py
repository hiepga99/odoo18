from __future__ import annotations

import gc
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rag.chunking import Chunk
from rag.generate import build_context
from rag.retrieval import Retriever
from rag.vector_store import VectorStore


class FakeEmbeddingModel:
    def encode_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]

    def encode_documents(self, texts, batch_size=8, show_progress_bar=False):
        return [
            [1.0, 0.0, 0.0] if "đổi trả" in text.lower() else [0.0, 1.0, 0.0]
            for text in texts
        ]


class VectorStoreTests(unittest.TestCase):
    @patch("rag.vector_store.chromadb.HttpClient")
    def test_http_mode_uses_remote_chroma_client(self, http_client) -> None:
        fake_client = http_client.return_value
        store = VectorStore(
            mode="http",
            host="chroma.internal",
            port=8443,
            ssl=True,
            headers={"Authorization": "Bearer test"},
            collection_name="remote_test",
        )
        self.assertIs(store.client, fake_client)
        self.assertIn("remote_test", store.location)
        http_client.assert_called_once()
        kwargs = http_client.call_args.kwargs
        self.assertEqual(kwargs["host"], "chroma.internal")
        self.assertEqual(kwargs["port"], 8443)
        self.assertTrue(kwargs["ssl"])

    def test_upsert_and_cosine_query(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            store = VectorStore(
                path=Path(temp_dir),
                collection_name="test_collection",
                embedding_model="fake-test-model",
                mode="embedded",
            )
            chunks = [
                Chunk(
                    id="return-policy",
                    text="Khách hàng được đổi trả trong vòng 60 ngày.",
                    source_path="return.pdf",
                    source_name="return.pdf",
                    file_type="pdf",
                    page=1,
                    chunk_index=0,
                    document_hash="hash-a",
                    extra_metadata={
                        "odoo_document_id": 10,
                        "odoo_attachment_id": 100,
                        "company_id": 1,
                    },
                ),
                Chunk(
                    id="privacy-policy",
                    text="Dữ liệu thanh toán được xử lý qua đối tác.",
                    source_path="privacy.pdf",
                    source_name="privacy.pdf",
                    file_type="pdf",
                    page=2,
                    chunk_index=0,
                    document_hash="hash-b",
                    extra_metadata={
                        "odoo_document_id": 20,
                        "odoo_attachment_id": 200,
                        "company_id": 2,
                    },
                ),
            ]
            store.upsert(chunks, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
            self.assertEqual(store.count(), 2)

            result = store.query([1.0, 0.0, 0.0], top_k=1)
            self.assertEqual(result["ids"][0][0], "return-policy")
            self.assertEqual(result["metadatas"][0][0]["page"], 1)

            retrieved = Retriever(
                embedding_model=FakeEmbeddingModel(),
                vector_store=store,
            ).search("Đổi trả trong bao lâu?", top_k=1)
            self.assertEqual(retrieved[0].source_name, "return.pdf")
            self.assertEqual(retrieved[0].citation, "return.pdf, trang 1")
            self.assertIn("[1] Nguồn: return.pdf, trang 1", build_context(retrieved))

            filtered = Retriever(
                embedding_model=FakeEmbeddingModel(),
                vector_store=store,
            ).search(
                "Đổi trả trong bao lâu?",
                top_k=2,
                allowed_document_ids=[20],
                company_id=2,
            )
            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0].odoo_document_id, 20)
            self.assertEqual(filtered[0].company_id, 2)

            del store
            gc.collect()


if __name__ == "__main__":
    unittest.main()
