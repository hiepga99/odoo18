import unittest
from types import SimpleNamespace

from rag.mcp_worker import _call_json


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


if __name__ == "__main__":
    unittest.main()
