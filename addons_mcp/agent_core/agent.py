import os
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from .prompts import SYSTEM_PROMPT, ANALYST_SYNTHESIS_PROMPT
from .tools import TOOL_DEFINITIONS, execute_tool
from .llm_client import LLMClient
from .synthesizer import synthesize_erp_analyst_response

class HermesAgent:
    """
    Agent Core điều phối xử lý hội thoại và gọi Tool (Function Calling).
    Thiết kế theo chuẩn kiến trúc Hermes Agent / ReAct Loop và phong cách Chuyên viên ERP cao cấp.
    """
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, fast_mode: bool = True):
        if not provider:
            env_provider = os.getenv("LLM_PROVIDER")
            if env_provider:
                provider = env_provider
            elif os.getenv("GEMINI_API_KEY") or (api_key and api_key.startswith("AIzaSy")):
                provider = "gemini"
            elif os.getenv("GROQ_API_KEY"):
                provider = "groq"
            elif os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            else:
                provider = "mock"

        self.fast_mode = fast_mode
        self.llm_client = LLMClient(provider=provider, api_key=api_key)
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str, user_role: str = "sales_user") -> Dict[str, Any]:
        """
        Nhận tin nhắn của người dùng -> Suy luận -> Quyết định gọi Tool hay trả lời trực tiếp
        Tự động tổng hợp câu trả lời theo văn phong Chuyên viên Phân tích & Tư vấn ERP cao cấp.
        Hỗ trợ chế độ Fast-Mode (1-Pass) và phân quyền bảo mật vai trò người dùng (RBAC).
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
            
            # Bước 2: Thực thi Tool tra cứu dữ liệu ERP kèm kiểm tra phân quyền RBAC
            tool_output = execute_tool(func_name, func_args, user_role=user_role)
            
            # Bước 3: Tổng hợp câu trả lời theo chuẩn Chuyên viên Phân tích ERP
            # Fast-Path: Bỏ round 2 tốn thời gian, dùng bộ chuyên viên ERP tối ưu (< 0.005s)
            if self.fast_mode or not self.llm_client.client:
                final_analyst_answer = synthesize_erp_analyst_response(
                    tool_name=func_name,
                    args=func_args,
                    raw_result=tool_output,
                    user_query=user_message,
                    user_role=user_role
                )
            else:
                final_analyst_answer = ""
                try:
                    synthesis_messages = list(self.history)
                    synthesis_messages.append({
                        "role": "system",
                        "content": ANALYST_SYNTHESIS_PROMPT
                    })
                    synthesis_resp = self.llm_client.chat_completion(synthesis_messages)
                    final_analyst_answer = synthesis_resp.get("content", "").strip()
                except Exception:
                    final_analyst_answer = ""

                if not final_analyst_answer:
                    final_analyst_answer = synthesize_erp_analyst_response(
                        tool_name=func_name,
                        args=func_args,
                        raw_result=tool_output,
                        user_query=user_message,
                        user_role=user_role
                    )

            # Ghi nhận phản hồi hoàn chỉnh vào lịch sử hội thoại
            self.history.append({
                "role": "assistant",
                "content": final_analyst_answer
            })

            engine = response.get("engine", "Chuyên viên Phân tích ERP")
            return {
                "type": "tool_call",
                "tool_name": func_name,
                "arguments": func_args,
                "tool_result": tool_output,
                "final_answer": final_analyst_answer,
                "engine": engine
            }
        else:
            # Nếu chỉ trả lời văn bản thông thường
            assistant_reply = response.get("content", "")
            self.history.append({
                "role": "assistant",
                "content": assistant_reply
            })
            engine = response.get("engine", "Chuyên viên Phân tích ERP")
            return {
                "type": "direct_answer",
                "tool_name": None,
                "final_answer": assistant_reply,
                "engine": engine
            }

    def reset(self):
        """Reset lịch sử hội thoại"""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

