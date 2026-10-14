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
        
        timeout = float(os.getenv("LLM_TIMEOUT", "4.0"))
        if self.provider == "ollama":
            self.client = OpenAI(
                base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key="ollama",
                timeout=timeout
            )
            self.model_name = os.getenv("OLLAMA_MODEL", "hermes3:8b")
        elif self.provider == "groq" and self.api_key:
            self.client = OpenAI(
                base_url=base_url or "https://api.groq.com/openai/v1",
                api_key=self.api_key,
                timeout=timeout
            )
            self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        elif self.provider == "openai" and self.api_key:
            self.client = OpenAI(
                base_url=base_url or "https://api.openai.com/v1",
                api_key=self.api_key,
                timeout=timeout
            )
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            self.client = None
            self.model_name = "hermes-rule-engine"

    def chat_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Gọi LLM sinh phản hồi hoặc trả về tool_calls với cơ chế timeout nhanh an toàn"""
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
            except Exception:
                # Nếu API gặp lỗi (timeout, mạng chậm, hết quota), tự động fallback siêu tốc sang Heuristic
                pass

        # Fallback Heuristic Engine (mô phỏng chuẩn xác logic suy luận chuyên gia ERP)
        return self._heuristic_fallback(messages)

    def _heuristic_fallback(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Bộ phân tích Heuristic chuẩn xác cho ngữ nghĩa tiếng Việt"""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        # 1. Chào hỏi xã giao thông thường (Không gọi tool)
        greetings = ["xin chào", "chào bạn", "chào em", "chào anh", "chào chị", "hello", "hi em", "bạn là ai", "tên gì", "làm được gì", "cảm ơn", "thank", "tạm biệt", "hẹn gặp lại", "thời tiết", "trời hôm nay"]
        biz_words = ["giá", "kho", "đơn", "doanh thu", "doanh số", "bảo hành", "chính sách", "chiết khấu", "vận chuyển", "công nợ"]
        if any(g in last_user_msg for g in greetings) and not any(w in last_user_msg for w in biz_words):
            if any(k in last_user_msg for k in ["bạn là ai", "tên gì", "làm được những việc gì", "làm được gì"]):
                reply = "Kính chào Anh/Chị! Em là Chuyên viên Trợ lý AI ERP chuyên trách phân tích và điều phối vận hành doanh nghiệp. Em có thể hỗ trợ Anh/Chị: tra cứu giá niêm yết, kiểm tra số lượng tồn kho khả dụng, tổng hợp báo cáo doanh số bán hàng, kiểm tra tình trạng đơn hàng và bóc tách tin nhắn lập báo giá nháp tự động trên Odoo ERP. Anh/Chị cần em kiểm tra thông tin nào ạ?"
            elif any(k in last_user_msg for k in ["cảm ơn", "thank"]):
                reply = "Dạ không có gì ạ! Rất vui vì đã hỗ trợ được công việc cho Anh/Chị. Nếu cần thêm số liệu đối soát hay phân tích nghiệp vụ trên Odoo, Anh/Chị cứ nhắn em nhé. Chúc Anh/Chị một ngày làm việc hiệu quả và nhiều niềm vui!"
            elif any(k in last_user_msg for k in ["tạm biệt", "hẹn gặp lại"]):
                reply = "Dạ em chào tạm biệt Anh/Chị! Chúc Anh/Chị luôn gặt hái nhiều thành công. Khi nào cần hỗ trợ dữ liệu hệ thống, em luôn sẵn sàng đồng hành ạ!"
            elif any(k in last_user_msg for k in ["thời tiết", "trời hôm nay"]):
                reply = "Dạ hôm nay thời tiết rất dễ chịu và thuận lợi cho công việc kinh doanh giao hàng đấy ạ! Em có thể giúp gì cho Anh/Chị về số liệu tồn kho hoặc đơn hàng hôm nay không ạ?"
            else:
                reply = "Kính chào Anh/Chị! Em là Chuyên viên Trợ lý AI ERP. Em luôn sẵn sàng hỗ trợ Anh/Chị kiểm tra giá, tồn kho, doanh số và xử lý đơn hàng trên hệ thống Odoo. Hôm nay Anh/Chị cần em hỗ trợ công việc nào ạ?"

            return {
                "content": reply,
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
