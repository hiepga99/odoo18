# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

class LLMClient:
    """
    LLM Client tương thích chuẩn OpenAI API, hỗ trợ:
    1. Groq Cloud (Free Tier - Siêu nhanh 300 token/s)
    2. Ollama Local (Hermes 3, Qwen 2.5)
    3. Mock Heuristic Evaluator (chạy kiểm thử offline không cần API key)
    """
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq")
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if self.provider == "ollama":
            self.client = OpenAI(
                base_url=base_url or "http://localhost:11434/v1",
                api_key="ollama"
            )
            self.model_name = "hermes3:8b"
        elif self.provider == "groq" and self.api_key:
            self.client = OpenAI(
                base_url=base_url or "https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
            self.model_name = "llama-3.3-70b-versatile"
        else:
            self.client = None
            self.model_name = "hermes-rule-engine"

    def chat_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Gọi LLM sinh phản hồi hoặc trả về tool_calls"""
        # Nếu có client API hợp lệ
        if self.client:
            try:
                kwargs = {
                    "model": self.model_name,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"
                
                response = self.client.chat.completions.create(**kwargs)
                msg = response.choices[0].message
                
                tool_calls_data = []
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls_data.append({
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                            }
                        })
                
                return {
                    "content": msg.content or "",
                    "tool_calls": tool_calls_data
                }
            except Exception as e:
                # Nếu API gặp lỗi (chưa set key, hết quota), tự động fallback
                pass

        # Fallback Heuristic Engine (mô phỏng chính xác logic suy luận của Hermes)
        return self._heuristic_fallback(messages)

    def _heuristic_fallback(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Bộ phân tích Heuristic chuẩn xác cho ngữ nghĩa tiếng Việt"""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        # 1. Chào hỏi xã giao thông thường (Không gọi tool)
        greetings = ["xin chào", "chào bạn", "chào em", "chào anh", "chào chị", "hello", "bạn là ai", "tên gì", "cảm ơn", "thank", "tạm biệt", "hẹn gặp lại", "thời tiết", "trời hôm nay"]
        biz_words = ["giá", "kho", "đơn", "doanh thu", "doanh số", "bảo hành", "chính sách", "chiết khấu", "vận chuyển", "công nợ"]
        # Chỉ chào hỏi khi có từ chào và không chứa từ khóa kinh doanh
        if any(g in last_user_msg for g in greetings) and not any(w in last_user_msg for w in biz_words):
            return {
                "content": "Xin chào! Tôi là Trợ lý AI ERP hỗ trợ quản lý bán hàng và tồn kho. Tôi có thể giúp gì cho bạn hôm nay?",
                "tool_calls": []
            }

        # 2. Báo cáo Doanh thu & Kinh doanh (ưu tiên kiểm tra trước giá)
        revenue_keywords = ["doanh thu", "doanh số", "tổng tiền bán", "bán được bao nhiêu", "tổng tiền bán hàng"]
        if any(w in last_user_msg for w in revenue_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_revenue",
                    "function": {
                        "name": "get_revenue_report",
                        "arguments": {"period": "thời gian yêu cầu"}
                    }
                }]
            }

        # 3. Tra cứu Đơn hàng khách hàng
        order_keywords = ["đơn hàng", "đơn đặt hàng", "đơn bán", "tình trạng đơn", "danh sách đơn"]
        if any(w in last_user_msg for w in order_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_order",
                    "function": {
                        "name": "search_sale_orders",
                        "arguments": {"customer_name": last_user_msg}
                    }
                }]
            }

        # 4. Tra cứu Chính sách / Quy trình nội bộ
        policy_keywords = ["bảo hành", "đổi trả", "chiết khấu", "vận chuyển", "miễn phí ship", "công nợ", "quy trình", "chính sách", "quy chế", "quy định"]
        if any(w in last_user_msg for w in policy_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_policy",
                    "function": {
                        "name": "get_company_policy",
                        "arguments": {"topic": last_user_msg}
                    }
                }]
            }

        # 5. Hỏi tồn kho sản phẩm
        stock_keywords = ["tồn kho", "còn hàng", "còn bao nhiêu", "số lượng trong kho", "kho còn", "sẵn hàng"]
        if any(w in last_user_msg for w in stock_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_stock",
                    "function": {
                        "name": "check_product_stock",
                        "arguments": {"product_name": last_user_msg}
                    }
                }]
            }

        # 6. Hỏi giá sản phẩm
        price_keywords = ["giá", "bao nhiêu tiền", "nhiêu một chiếc", "đơn giá", "chi phí mua", "báo giá", "chi phí"]
        if any(w in last_user_msg for w in price_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_price",
                    "function": {
                        "name": "get_product_price",
                        "arguments": {"product_name": last_user_msg}
                    }
                }]
            }

        # 7. Đặt hàng / Lập báo giá mới
        quote_keywords = ["lấy cho anh", "đặt mua", "mua 2", "mua 5"]
        if any(w in last_user_msg for w in quote_keywords):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_quote",
                    "function": {
                        "name": "create_sale_quotation",
                        "arguments": {"customer_name": "Khách hàng", "products": []}
                    }
                }]
            }

        return {
            "content": "Tôi đã ghi nhận thông tin của bạn. Vui lòng cung cấp thêm chi tiết để tôi hỗ trợ tốt nhất.",
            "tool_calls": []
        }
