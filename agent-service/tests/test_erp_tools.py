import unittest

from mcp.client import Client

from rag.odoo import mcp_server


class ErpToolsOnSameEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_single_endpoint_lists_rag_and_erp_tools(self):
        async with Client(mcp_server.mcp) as client:
            names = {tool.name for tool in (await client.list_tools()).tools}

        self.assertEqual(len(mcp_server.ERP_TOOL_NAMES), 12)
        self.assertTrue(set(mcp_server.ERP_TOOL_NAMES) <= names)
        self.assertTrue({"search_internal_documents", "answer_internal_documents"} <= names)


if __name__ == "__main__":
    unittest.main()
