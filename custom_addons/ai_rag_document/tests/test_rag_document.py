import base64

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAiRagDocument(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Document = cls.env["ai.rag.document"]

    def _create_document(self, filename="policy.txt", content=b"Return period is 60 days."):
        return self.Document.create(
            {
                "name": "Policy",
                "file_name": filename,
                "file_data": base64.b64encode(content),
            }
        )

    def test_upload_is_queued_and_stored_as_attachment(self):
        document = self._create_document()
        self.assertEqual(document.rag_status, "pending")
        self.assertEqual(document.rag_progress, 0)
        self.assertTrue(document.content_checksum)
        self.assertEqual(document.file_size, len(b"Return period is 60 days."))
        self.assertTrue(document._get_binary_attachment())

    def test_rejects_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            self._create_document(filename="malware.exe")

    def test_worker_contract_and_access_list(self):
        document = self._create_document()
        jobs = self.Document.worker_claim_pending_documents()
        job = next(item for item in jobs if item["document_id"] == document.id)
        self.assertEqual(job["operation"], "index")
        self.assertEqual(document.rag_status, "processing")
        self.assertEqual(document.rag_progress, 5)

        progress_result = self.Document.worker_update_document_progress(
            document.id, 55, "Đang tạo embedding"
        )
        self.assertTrue(progress_result["updated"])
        self.assertEqual(document.rag_progress, 55)
        self.assertEqual(document.rag_progress_stage, "Đang tạo embedding")

        payload = self.Document.worker_get_document_payload(document.id)
        self.assertEqual(base64.b64decode(payload["content_base64"]), b"Return period is 60 days.")
        self.assertTrue(payload["attachment_id"])

        result = self.Document.worker_mark_document_indexed(
            document.id,
            2,
            document.content_checksum,
            "company_knowledge",
            "ChromaDB HTTP",
            "http://127.0.0.1:8000/company_knowledge",
            [
                {
                    "vector_id": "chunk-1",
                    "chunk_index": 0,
                    "page": 1,
                    "source_name": "policy.txt",
                    "char_count": 24,
                    "text_preview": "Return period is 60 days.",
                }
            ],
            page_count=1,
            clean_char_count=24,
            chunk_size=900,
            chunk_overlap=150,
            embedding_model="BAAI/bge-m3",
        )
        self.assertTrue(result["updated"])
        self.assertEqual(document.rag_status, "indexed")
        self.assertEqual(document.rag_progress, 100)
        self.assertEqual(document.rag_progress_stage, "Hoàn tất - sẵn sàng tra cứu")
        self.assertEqual(document.rag_storage_backend, "ChromaDB HTTP")
        self.assertEqual(document.rag_page_count, 1)
        self.assertEqual(document.rag_chunk_size, 900)
        self.assertEqual(document.rag_embedding_model, "BAAI/bge-m3")
        self.assertEqual(len(document.chunk_preview_ids), 1)
        self.assertIn("Đoạn 1", document.rag_clean_preview_html)
        self.assertIn("Return period is 60 days", document.rag_clean_preview_html)
        self.assertIn(document.id, self.Document.list_readable_document_ids())
        scope = self.Document.get_current_rag_scope()
        self.assertEqual(scope["company_id"], self.env.company.id)
        self.assertIn(document.id, scope["allowed_document_ids"])

    def test_delete_queues_vector_cleanup_then_hard_deletes_document(self):
        document = self._create_document()
        document_id = document.id
        attachment_id = document._get_binary_attachment().id
        document.with_context(rag_worker_update=True).write({"rag_status": "indexed"})
        document.unlink()

        queued = self.Document.with_context(active_test=False).browse(document_id).exists()
        self.assertTrue(queued)
        self.assertFalse(queued.active)
        self.assertEqual(queued.rag_status, "delete_pending")
        self.assertTrue(queued.delete_after_vector_cleanup)

        jobs = self.Document.worker_claim_pending_documents()
        job = next(item for item in jobs if item["document_id"] == document_id)
        self.assertEqual(job["operation"], "delete")

        late_index_result = self.Document.worker_mark_document_indexed(
            document_id,
            1,
            queued.content_checksum,
            "company_knowledge",
        )
        self.assertFalse(late_index_result["updated"])
        self.assertEqual(late_index_result["reason"], "delete_requested")
        self.assertEqual(queued.rag_status, "delete_pending")

        self.Document.worker_mark_document_vectors_deleted(document_id)
        self.assertFalse(
            self.Document.with_context(active_test=False).browse(document_id).exists()
        )
        self.assertFalse(self.env["ir.attachment"].browse(attachment_id).exists())
