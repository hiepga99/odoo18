from __future__ import annotations

import gc
import tempfile
import unittest
from pathlib import Path

from rag.odoo_ingest import delete_odoo_document, ingest_odoo_document
from rag.vector_store import VectorStore


class FakeEmbeddingModel:
    def encode_documents(self, texts, batch_size=8, show_progress_bar=False):
        return [[1.0, 0.0, 0.0] for _ in texts]


class OdooIngestTests(unittest.TestCase):
    def test_ingest_replace_and_delete_odoo_document(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            store = VectorStore(
                path=Path(temp_dir),
                collection_name="odoo_ingest_test",
                embedding_model="fake-test-model",
                mode="embedded",
            )
            progress_updates = []
            first = ingest_odoo_document(
                content="Chính sách đổi trả trong 60 ngày.".encode("utf-8"),
                filename="chinh_sach.md",
                odoo_document_id=42,
                odoo_attachment_id=420,
                company_id=1,
                embedding_model=FakeEmbeddingModel(),
                vector_store=store,
                progress_callback=lambda progress, stage: progress_updates.append(
                    (progress, stage)
                ),
            )
            self.assertEqual(first.chunk_count, 1)
            self.assertEqual(first.page_count, 1)
            self.assertGreater(first.clean_char_count, 0)
            self.assertGreater(first.chunk_size, 0)
            self.assertTrue(first.embedding_model)
            self.assertEqual(len(first.chunk_previews), 1)
            self.assertIn("60 ngày", first.chunk_previews[0]["text_preview"])
            self.assertEqual(store.count(), 1)
            self.assertEqual(
                [progress for progress, _stage in progress_updates],
                [15, 35, 45, 80, 90, 95],
            )

            updated = ingest_odoo_document(
                content="Chính sách đổi trả đã được cập nhật.".encode("utf-8"),
                filename="chinh_sach.md",
                odoo_document_id=42,
                odoo_attachment_id=421,
                company_id=1,
                embedding_model=FakeEmbeddingModel(),
                vector_store=store,
            )
            self.assertEqual(updated.chunk_count, 1)
            self.assertEqual(store.count(), 1)
            stored = store.get_collection().get(include=["metadatas", "documents"])
            self.assertEqual(stored["metadatas"][0]["odoo_attachment_id"], 421)
            self.assertIn("cập nhật", stored["documents"][0])

            delete_odoo_document(42, vector_store=store)
            self.assertEqual(store.count(), 0)

            del store
            gc.collect()


if __name__ == "__main__":
    unittest.main()
