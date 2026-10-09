from __future__ import annotations

import gc
import tempfile
import unittest
from pathlib import Path

from rag.chunking import Chunk
from rag.generate import build_context
from rag.retrieval import Retriever
from rag.vector_store import VectorStore


class FakeEmbeddingModel:
    def encode_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class VectorStoreTests(unittest.TestCase):
    def test_upsert_and_cosine_query(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            store = VectorStore(
                path=Path(temp_dir),
                collection_name="test_collection",
                embedding_model="fake-test-model",
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

            del store
            gc.collect()


if __name__ == "__main__":
    unittest.main()
