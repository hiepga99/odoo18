# -*- coding: utf-8 -*-
import os
import time
import xmlrpc.client
import http.client
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class TimeoutTransport(xmlrpc.client.Transport):
    """Transport XML-RPC với cơ chế timeout kết nối nhanh (tránh treo socket)"""
    def __init__(self, timeout: float = 1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        return http.client.HTTPConnection(host, timeout=self.timeout)

class OdooClient:
    """
    Client kết nối Odoo 18 ERP hỗ trợ chế độ KÉP (Hybrid):
    1. Chuẩn MCP Quốc tế: Gửi JSON-RPC 2.0 tới 'POST /mcp' với header 'Authorization: Bearer <API_KEY>'
       (Thừa hưởng 100% Odoo RBAC, Record Rules, Field Denylist, Rate Limit và Audit Log).
    2. Fallback XML-RPC: Tự động chuyển về XML-RPC truyền thống khi module ai_mcp chưa bật.
    """
    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 2.0
    ):
        self.url = (url or os.getenv("ODOO_URL", "http://localhost:8069")).rstrip("/")
        self.db = db or os.getenv("ODOO_DB", "odoo18")
        self.username = username or os.getenv("ODOO_USER", "admin")
        self.password = password or os.getenv("ODOO_PASSWORD", "admin")
        self.api_key = api_key or os.getenv("ODOO_MCP_KEY") or os.getenv("ODOO_API_KEY")
        self.timeout = timeout
        
        self.mcp_url = f"{self.url}/mcp"
        self.uid = None
        self.common = None
        self.models = None
        self.is_offline = False
        self.use_http_mcp = bool(self.api_key)

    def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], user_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Gửi yêu cầu gọi Tool qua chuẩn MCP HTTP (JSON-RPC 2.0) tới POST /mcp"""
        token = user_key or self.api_key
        if not token:
            return None

        import urllib.request
        import json

        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000) % 100000,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        try:
            req = urllib.request.Request(
                self.mcp_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return res_data.get("result")
        except Exception:
            # Nếu POST /mcp chưa bật hoặc key sai, trả về None để fallback sang XML-RPC
            pass
        return None

    def _authenticate(self) -> bool:
        if self.is_offline:
            return False
        try:
            transport = TimeoutTransport(timeout=self.timeout)
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", transport=transport)
            # Odoo XML-RPC cho phép truyền trực tiếp API Key vào tham số password
            auth_secret = self.api_key or self.password
            self.uid = self.common.authenticate(self.db, self.username, auth_secret, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", transport=transport)
                self.is_offline = False
                return True
        except Exception:
            self.is_offline = True
        return False

    def is_connected(self) -> bool:
        return bool(self.uid and self.models)

    def execute_kw(self, model: str, method: str, args: List, kwargs: Optional[Dict] = None, user_key: Optional[str] = None) -> Any:
        """Thực thi hàm Odoo: Thử qua MCP HTTP trước, nếu không được thì fallback sang XML-RPC"""
        kwargs = kwargs or {}

        # 1. Thử gọi qua endpoint MCP HTTP (ai_mcp) nếu là search_read hoặc read
        if self.use_http_mcp or user_key:
            if method == "search_read":
                domain = args[0] if args else []
                mcp_args = {
                    "model": model,
                    "domain": domain,
                    "fields": kwargs.get("fields", []),
                    "limit": kwargs.get("limit", 10)
                }
                mcp_res = self.execute_mcp_tool("odoo_search_read", mcp_args, user_key=user_key)
                if mcp_res and not mcp_res.get("isError"):
                    return mcp_res.get("records", [])

            elif method == "read":
                rec_ids = args[0] if args else []
                mcp_args = {
                    "model": model,
                    "ids": rec_ids,
                    "fields": kwargs.get("fields", [])
                }
                mcp_res = self.execute_mcp_tool("odoo_read", mcp_args, user_key=user_key)
                if mcp_res and not mcp_res.get("isError"):
                    return mcp_res.get("records", [])

        # 2. Fallback sang XML-RPC
        if not self.is_connected():
            if not self._authenticate():
                raise ConnectionError("Không thể kết nối đến Odoo 18 ERP qua XML-RPC.")
        auth_secret = self.api_key or self.password
        return self.models.execute_kw(self.db, self.uid, auth_secret, model, method, args, kwargs)

