# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from .prompts import SYSTEM_PROMPT
from .tools import TOOL_DEFINITIONS, execute_tool
from .llm_client import LLMClient

class HermesAgent:
    """
    Agent Core điều phối xử lý hội thoại và gọi Tool (Function Calling).
    Thiết kế theo chuẩn kiến trúc Hermes Agent / ReAct Loop.
    """
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None):
        self.llm_client = LLMClient(provider=provider, api_key=api_key)
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Nhận tin nhắn của người dùng -> Suy luận -> Quyết định gọi Tool hay trả lời trực tiếp
        """
        self.history.append({"role": "user", "content": user_message})

        # Bước 1: Gửi yêu cầu kèm danh sách Tools cho mô hình
        response = self.llm_client.chat_completion(
            messages=self.history,
            tools=TOOL_DEFINITIONS
        )

        tool_calls = response.get("tool_calls", [])
        
        # Nếu mô hình quyết định gọi Tool
        if tool_calls:
            first_tool = tool_calls[0]
            func_name = first_tool["function"]["name"]
            func_args = first_tool["function"]["arguments"]
            
            # Bước 2: Thực thi Tool
            tool_output = execute_tool(func_name, func_args)
            
            # Ghi nhận vào lịch sử
            self.history.append({
                "role": "assistant",
                "content": f"[Tool Call: {func_name}({func_args})]"
            })
            self.history.append({
                "role": "tool",
                "content": tool_output
            })
            
            return {
                "type": "tool_call",
                "tool_name": func_name,
                "arguments": func_args,
                "tool_result": tool_output,
                "final_answer": f"Đã gọi công cụ {func_name} thành công. Kết quả: {tool_output}"
            }
        else:
            # Nếu chỉ trả lời văn bản thông thường
            assistant_reply = response.get("content", "")
            self.history.append({
                "role": "assistant",
                "content": assistant_reply
            })
            return {
                "type": "direct_answer",
                "tool_name": None,
                "final_answer": assistant_reply
            }

    def reset(self):
        """Reset lịch sử hội thoại"""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
