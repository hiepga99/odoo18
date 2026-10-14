import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from rag.odoo.worker import WorkerSummary, process_once


class OdooWorkerTests(unittest.TestCase):
    @patch("rag.odoo.worker.ingest_odoo_document")
    def test_processes_index_job(self, ingest):
        client = Mock()
        client.call.side_effect = [
            [{"operation": "index", "document_id": 12}],
            {"updated": True},
            {
                "content_base64": "cG9saWN5",
                "file_name": "policy.txt",
                "attachment_id": 120,
                "company_id": 2,
                "checksum": "abc",
            },
            {"updated": True},
        ]
        ingest.return_value = SimpleNamespace(
            chunk_count=3,
            checksum="abc",
            collection="company_knowledge",
            storage_backend="ChromaDB HTTP",
            storage_location="http://localhost:8000/company_knowledge",
            chunk_previews=(),
            page_count=1,
            clean_char_count=6,
            chunk_size=1000,
            chunk_overlap=150,
            embedding_model="BAAI/bge-m3",
        )

        summary = process_once(
            client, limit=1, embedding_model=object(), vector_store=object()
        )

        self.assertEqual(summary, WorkerSummary(claimed=1, indexed=1))
        self.assertEqual(
            [call.args[0] for call in client.call.call_args_list],
            [
                "worker_claim_pending_documents",
                "worker_update_document_progress",
                "worker_get_document_payload",
                "worker_mark_document_indexed",
            ],
        )
        self.assertEqual(ingest.call_args.kwargs["content"], b"policy")

    @patch("rag.odoo.worker.delete_odoo_document")
    def test_processes_delete_job(self, delete):
        client = Mock()
        client.call.side_effect = [
            [{"operation": "delete", "document_id": 13}],
            True,
        ]
        vector_store = object()

        summary = process_once(
            client, limit=1, embedding_model=object(), vector_store=vector_store
        )

        self.assertEqual(summary, WorkerSummary(claimed=1, deleted=1))
        delete.assert_called_once_with(13, vector_store=vector_store)
        client.call.assert_any_call("worker_mark_document_vectors_deleted", 13)


if __name__ == "__main__":
    unittest.main()
