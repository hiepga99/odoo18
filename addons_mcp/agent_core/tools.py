# -*- coding: utf-8 -*-
"""
Tầng điều phối công cụ thông qua Kiến trúc Kỹ năng (Skill-based Dispatcher).
Tự động đăng ký Schemas và định tuyến thực thi từ các Skill module độc lập.
"""
from typing import Dict, Any, List
from .skills import default_registry

# Danh sách Schemas chuẩn OpenAI Tool Calling trích xuất tự động từ các Skills
TOOL_DEFINITIONS: List[Dict[str, Any]] = default_registry.get_tool_definitions()

def execute_tool(tool_name: str, args: Dict[str, Any], user_role: str = "sales_user") -> str:
    """Định tuyến và thực thi Tool thông qua Skill Registry kèm kiểm tra phân quyền vai trò (RBAC)"""
    return default_registry.execute(tool_name, args, user_role=user_role)
