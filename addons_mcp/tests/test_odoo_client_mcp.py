# -*- coding: utf-8 -*-
"""OdooClient must unwrap the MCP tools/call envelope and fall back to XML-RPC on tool errors."""
import io
import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_erp.odoo_client import OdooClient


class _Resp(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _mcp_response(payload, is_error=False):
    body = {"jsonrpc": "2.0", "id": 1, "result": {
        "content": [{"type": "text", "text": json.dumps(payload)}], "isError": is_error}}
    return _Resp(json.dumps(body).encode("utf-8"))


class TestOdooClientMcpEnvelope(unittest.TestCase):
    def setUp(self):
        self.client = OdooClient(url="http://odoo.test", api_key="k")

    def test_search_read_records_are_unwrapped_from_content_text(self):
        records = [{"id": 15, "name": "Azure Interior"}]
        with patch("urllib.request.urlopen", return_value=_mcp_response({"records": records, "count_returned": 1})):
            result = self.client.execute_kw("res.partner", "search_read", [[["name", "ilike", "Azure"]]],
                                            {"fields": ["name"], "limit": 2})
        self.assertEqual(result, records)

    def test_tool_error_returns_none_so_xmlrpc_fallback_runs(self):
        with patch("urllib.request.urlopen", return_value=_mcp_response({"error": "denied"}, is_error=True)):
            self.assertIsNone(self.client.execute_mcp_tool("odoo_search_read", {"model": "product.template"}))


if __name__ == "__main__":
    unittest.main()
