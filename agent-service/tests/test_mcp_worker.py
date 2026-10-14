import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from rag.odoo.worker import WorkerSummary, _call_json, process_once


class FakeClient:
    def __init__(self, result):
        self.result = result

    async def call_tool(self, name, arguments):
        return self.result


class McpWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_reads_v2_structured_list_result(self):
        client = FakeClient(
            SimpleNamespace(
                is_error=False,
                structured_content={"result": [{"document_id": 9}]},
                content=[],
            )
        )
        value = await _call_json(client, "claim_pending_rag_documents", {"limit": 1})
        self.assertEqual(value, [{"document_id": 9}])

    @patch("rag.odoo.worker.asyncio.to_thread", new_callable=AsyncMock)
    @patch("rag.odoo.worker._call_json", new_callable=AsyncMock)
    async def test_processes_index_job(self, call_json, to_thread):
        call_json.side_effect = [
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
        to_thread.return_value = SimpleNamespace(
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

        summary = await process_once(
            object(), limit=1, embedding_model=object(), vector_store=object()
        )

        self.assertEqual(summary, WorkerSummary(claimed=1, indexed=1))
        self.assertEqual(
            [call.args[1] for call in call_json.await_args_list],
            [
                "claim_pending_rag_documents",
                "update_rag_document_progress",
                "get_rag_document_payload",
                "mark_rag_document_indexed",
            ],
        )
        self.assertEqual(to_thread.await_args.kwargs["content"], b"policy")

    @patch("rag.odoo.worker.delete_odoo_document")
    @patch("rag.odoo.worker._call_json", new_callable=AsyncMock)
    async def test_processes_delete_job(self, call_json, delete):
        call_json.side_effect = [
            [{"operation": "delete", "document_id": 13}],
            True,
        ]
        vector_store = object()

        summary = await process_once(
            object(), limit=1, embedding_model=object(), vector_store=vector_store
        )

        self.assertEqual(summary, WorkerSummary(claimed=1, deleted=1))
        delete.assert_called_once_with(13, vector_store=vector_store)


if __name__ == "__main__":
    unittest.main()
