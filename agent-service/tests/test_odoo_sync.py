import base64
import unittest
from types import SimpleNamespace

from rag.odoo_sync import sync_pending_documents


class FakeGateway:
    def __init__(self, jobs, payload=None):
        self.jobs = jobs
        self.payload = payload or {}
        self.indexed = []
        self.deleted = []
        self.errors = []

    def claim_pending_documents(self, limit):
        return self.jobs[:limit]

    def get_document_payload(self, document_id):
        return self.payload

    def mark_document_indexed(self, *args):
        self.indexed.append(args)

    def mark_document_error(self, *args):
        self.errors.append(args)

    def mark_document_vectors_deleted(self, document_id):
        self.deleted.append(document_id)


class OdooSyncTests(unittest.TestCase):
    def test_index_job(self):
        gateway = FakeGateway(
            [{"operation": "index", "document_id": 12}],
            {
                "content_base64": base64.b64encode(b"policy").decode("ascii"),
                "file_name": "policy.txt",
                "attachment_id": 120,
                "company_id": 2,
                "checksum": "abc",
            },
        )
        calls = []

        def ingest(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                chunk_count=3,
                checksum="abc",
                collection="company_knowledge",
                storage_backend="ChromaDB HTTP",
                storage_location="http://localhost:8000/company_knowledge",
                chunk_previews=({"vector_id": "v1"},),
            )

        summary = sync_pending_documents(gateway, ingest=ingest)
        self.assertEqual(summary.indexed, 1)
        self.assertEqual(calls[0]["content"], b"policy")
        self.assertEqual(
            gateway.indexed[0],
            (
                12,
                3,
                "abc",
                "company_knowledge",
                "ChromaDB HTTP",
                "http://localhost:8000/company_knowledge",
                ({"vector_id": "v1"},),
                0,
                0,
                0,
                0,
                "",
            ),
        )

    def test_delete_job(self):
        gateway = FakeGateway([{"operation": "delete", "document_id": 13}])
        deleted = []

        def delete(document_id, *, vector_store):
            deleted.append(document_id)

        summary = sync_pending_documents(gateway, delete=delete)
        self.assertEqual(summary.deleted, 1)
        self.assertEqual(deleted, [13])
        self.assertEqual(gateway.deleted, [13])


if __name__ == "__main__":
    unittest.main()
