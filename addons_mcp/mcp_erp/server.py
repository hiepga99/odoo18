# -*- coding: utf-8 -*-
from typing import Dict, Any, List
from .tools import MCP_TOOL_MAP

class MCPServer:
    """
    Máy chủ MCP (Model Context Protocol) quản lý việc công bố và thực thi các Tools.
    Tuân thủ chuẩn Model Context Protocol của Anthropic.
    """
    def __init__(self, name: str = "odoo-18-erp-mcp"):
        self.name = name
        self.tools = MCP_TOOL_MAP

    def list_tools(self) -> List[str]:
        """Danh sách tên các tools sẵn sàng phục vụ"""
        return list(self.tools.keys())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi tool theo giao thức MCP"""
        if name not in self.tools:
            return {"status": "error", "message": f"Tool '{name}' không tồn tại trên server MCP"}
        func = self.tools[name]
        try:
            return func(**arguments)
        except TypeError as e:
            # Xử lý trường hợp truyền thiếu/thừa tham số
            return {"status": "error", "message": f"Sai tham số gọi tool {name}: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi thực thi tool {name}: {e}"}
