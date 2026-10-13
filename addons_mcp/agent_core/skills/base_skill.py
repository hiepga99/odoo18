# -*- coding: utf-8 -*-
"""
Hệ thống kiến trúc Kỹ năng (Skill-Based Architecture) cho AI Agent ERP.
Tuân theo chuẩn thiết kế Semantic Kernel & OpenClaw Agent Skills.
"""
import inspect
import json
from typing import Dict, Any, List, Callable, Optional

def skill_tool(name: str, description: str, parameters: Dict[str, Any]):
    """Decorator đánh dấu phương thức trong Skill là một Tool có thể gọi bởi LLM"""
    def decorator(func: Callable):
        func.__skill_tool__ = True
        func.__tool_spec__ = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        return func
    return decorator

class BaseSkill:
    """Lớp cơ sở cho toàn bộ các Kỹ năng nghiệp vụ của AI Agent"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class SkillRegistry:
    """
    Bộ quản lý và điều phối Kỹ năng (Skill Dispatcher & Registry).
    Tự động trích xuất Tool Definitions và định tuyến thực thi không cần if-else thủ công.
    """
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._tools: Dict[str, Callable] = {}
        self._specs: List[Dict[str, Any]] = []

    def register(self, skill: BaseSkill):
        """Đăng ký một Skill vào hệ sinh thái của Agent"""
        self._skills[skill.name] = skill
        for attr_name in dir(skill):
            attr = getattr(skill, attr_name)
            if callable(attr) and getattr(attr, "__skill_tool__", False):
                spec = getattr(attr, "__tool_spec__")
                tool_name = spec["function"]["name"]
                self._tools[tool_name] = attr
                self._specs.append(spec)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Trả về danh sách Schema chuẩn OpenAI Function Calling"""
        return self._specs

    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Định tuyến và thực thi tool tự động (Command Pattern)"""
        handler = self._tools.get(tool_name)
        if not handler:
            return json.dumps({
                "status": "error",
                "message": f"Không tìm thấy công cụ '{tool_name}' trong hệ thống kỹ năng."
            }, ensure_ascii=False)
        try:
            return handler(args)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "tool": tool_name,
                "message": f"Lỗi khi thực thi kỹ năng: {str(e)}"
            }, ensure_ascii=False)
