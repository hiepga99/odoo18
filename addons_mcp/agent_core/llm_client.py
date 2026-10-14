# -*- coding: utf-8 -*-
import os
import re
import json
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
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
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        default_timeout = "60.0" if self.provider == "ollama" else "15.0"
        timeout = float(os.getenv("LLM_TIMEOUT", default_timeout))
        if self.provider == "mock":
            self.client = None
            self.model_name = "hermes-rule-engine"
        elif self.provider == "gemini":
            self.client = OpenAI(
                base_url=base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=self.api_key,
                timeout=timeout
            )
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        elif self.provider == "ollama":
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
        # Fast Intent Router: Với câu chào hỏi/giao tiếp thông thường, trả lời ngay tức thì (< 0.001s)
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        greetings = [
            "helo", "hello", "hi", "alo", "hey", "hế lô", "chào", "chao", "xin chào", "xin chao",
            "chào bạn", "chào em", "chào anh", "chào chị", "hi em", "hi anh", "hi chị", "hi bạn",
            "bạn là ai", "tên gì", "làm được gì", "làm được những gì", "cảm ơn", "cam on", "thank", "thanks",
            "tạm biệt", "tam biet", "hẹn gặp lại", "thời tiết", "trời hôm nay"
        ]
        biz_words = ["giá", "kho", "đơn", "doanh thu", "doanh số", "bảo hành", "chính sách", "chiết khấu", "vận chuyển", "công nợ", "mua", "bán", "tồn", "báo giá"]
        # Kiểm tra từ chào hỏi đứng độc lập hoặc trong chuỗi
        words = last_user_msg.split()
        is_greeting = any(g in last_user_msg for g in greetings) or any(w in greetings for w in words)
        if is_greeting and not any(w in last_user_msg for w in biz_words):
            return self._heuristic_fallback(messages)

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
                    "tool_calls": tool_calls_data,
                    "engine": f"AI Model - {self.provider.upper()} ({self.model_name})"
                }
            except Exception:
                # Nếu API gặp lỗi (timeout, mạng chậm, hết quota), tự động fallback siêu tốc sang Heuristic
                pass

        # Fallback Heuristic Engine (mô phỏng chuẩn xác logic suy luận chuyên gia ERP)
        fallback_res = self._heuristic_fallback(messages)
        fallback_res["engine"] = "Quy tắc nội bộ (Heuristic Fast-Path)"
        return fallback_res

    def _heuristic_fallback(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Bộ phân tích Heuristic chuẩn xác cho ngữ nghĩa tiếng Việt"""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        # 1. Chào hỏi xã giao thông thường (Không gọi tool)
        greetings = [
            "helo", "hello", "hi", "alo", "hey", "hế lô", "chào", "chao", "xin chào", "xin chao",
            "chào bạn", "chào em", "chào anh", "chào chị", "hi em", "hi anh", "hi chị", "hi bạn",
            "bạn là ai", "tên gì", "làm được gì", "làm được những gì", "cảm ơn", "cam on", "thank", "thanks",
            "tạm biệt", "tam biet", "hẹn gặp lại", "thời tiết", "trời hôm nay"
        ]
        biz_words = ["giá", "kho", "đơn", "doanh thu", "doanh số", "bảo hành", "chính sách", "chiết khấu", "vận chuyển", "công nợ", "mua", "bán", "tồn", "báo giá"]
        words = last_user_msg.split()
        is_greeting = any(g in last_user_msg for g in greetings) or any(w in greetings for w in words)
        if is_greeting and not any(w in last_user_msg for w in biz_words):
            if any(k in last_user_msg for k in ["bạn là ai", "tên gì", "làm được những việc gì", "làm được gì"]):
                reply = (
                    "Dạ em chào Anh/Chị! Em là Chuyên viên Trợ lý AI ERP đồng hành phân tích và vận hành hệ thống Odoo của doanh nghiệp.\n\n"
                    "Em có thể hỗ trợ Anh/Chị xử lý tức thì các công việc sau:\n"
                    "• **Bán hàng & Báo giá:** Tra cứu giá niêm yết, chính sách chiết khấu, tự động bóc tách tin nhắn lập Báo giá nháp (Draft Quotation).\n"
                    "• **Kho vận:** Kiểm tra số lượng tồn kho khả dụng thời gian thực, vị trí kho và đánh giá ngưỡng an toàn (Min-Stock).\n"
                    "• **Kinh doanh & Tài chính:** Báo cáo doanh số bán hàng, giá trị đơn trung bình (AOV), nhóm sản phẩm bán chạy.\n"
                    "• **Tiến độ đơn hàng:** Tra cứu lịch sử đơn của khách, tình trạng xuất kho và giao vận.\n"
                    "• **Quy chế nội bộ:** Tra cứu quy định bảo hành 24 tháng, chính sách 1 đổi 1 trong 30 ngày, điều kiện công nợ.\n\n"
                    "Hôm nay Anh/Chị cần em kiểm tra thông tin hoặc xử lý đơn hàng nào trên Odoo ạ?"
                )
            elif any(k in last_user_msg for k in ["cảm ơn", "thank"]):
                reply = "Dạ không có chi ạ! Rất vui vì đã hỗ trợ được công việc cho Anh/Chị. Cần thêm số liệu đối soát hay phân tích nghiệp vụ nào trên Odoo, Anh/Chị cứ nhắn em nhé. Chúc Anh/Chị một ngày làm việc hiệu quả và chốt thật nhiều đơn hàng ạ!"
            elif any(k in last_user_msg for k in ["tạm biệt", "hẹn gặp lại"]):
                reply = "Dạ em chào tạm biệt Anh/Chị! Chúc Anh/Chị luôn gặp nhiều thuận lợi và thành công. Khi nào cần tra cứu số liệu hệ thống, em luôn sẵn sàng hỗ trợ ạ!"
            elif any(k in last_user_msg for k in ["thời tiết", "trời hôm nay"]):
                reply = "Dạ hôm nay thời tiết rất dễ chịu và thuận lợi cho các hoạt động giao hàng kinh doanh đấy ạ! Em có thể hỗ trợ gì cho Anh/Chị về số liệu kho bãi hoặc đơn hàng hôm nay không ạ?"
            else:
                reply = "Dạ em chào Anh/Chị! Em là Chuyên viên Trợ lý AI ERP đây ạ. Hôm nay Anh/Chị cần em kiểm tra giá bán, rà soát tồn kho hay tổng hợp số liệu kinh doanh nào trên Odoo không ạ?"

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

        # 6. Tạo báo giá / Lên đơn đặt hàng mới từ tin nhắn (TN2)
        create_quote_keywords = [
            "tạo báo giá", "lên báo giá", "lập báo giá", "tạo đơn báo giá", "tạo draft so",
            "báo giá nháp", "lên đơn", "chốt đơn", "đặt mua", "tạo đơn hàng mới", "lập đơn hàng",
            "đặt hàng", "soạn báo giá", "cần báo giá", "gửi báo giá", "xin báo giá"
        ]
        is_quote_for_target = (
            any(w in last_user_msg for w in [
                "báo giá cho bên", "báo giá giúp bên", "gửi báo giá cho bên", "báo giá cho công ty",
                "báo giá cho cty", "báo giá cho khách", "báo giá gửi", "lập báo giá cho", "lên báo giá cho"
            ])
            or bool(re.search(r'báo\s+giá\s+(?:cho|gửi|giúp)\s+(?:anh|chị)\s+([A-ZÀ-Ỹa-zà-ỹ0-9]+?)(?=[,:\.]|\s+(?:lấy|cần|mua|đặt|\d+))', last_user_msg, re.IGNORECASE))
        )
        is_create_quote = any(w in last_user_msg for w in create_quote_keywords) or is_quote_for_target
        if is_create_quote:
            from .skills.quotation_extractor import parse_quotation_message
            parsed = parse_quotation_message(last_user_msg)
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_quote",
                    "function": {
                        "name": "create_sale_quotation",
                        "arguments": {
                            "customer_name": parsed["customer_name"],
                            "products": parsed["products"],
                            "total_amount": parsed["total_amount"],
                            "phone": parsed["phone"],
                            "raw_message": last_user_msg
                        }
                    }
                }]
            }

        # 6.5. Tra cứu Bảng xếp hạng sản phẩm / Đắt nhất / Rẻ nhất / Toàn bộ danh mục
        if any(w in last_user_msg for w in ["đắt nhất", "dat nhat", "giá cao nhất", "gia cao nhat", "cao nhất", "đắt tiền nhất", "cao cấp nhất"]):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_top_prods",
                    "function": {
                        "name": "get_top_products",
                        "arguments": {"criterion": "highest_price", "limit": 5}
                    }
                }]
            }
        elif any(w in last_user_msg for w in ["rẻ nhất", "re nhat", "giá thấp nhất", "gia thap nhat", "thấp nhất", "rẻ tiền nhất", "tiết kiệm nhất"]):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_top_prods",
                    "function": {
                        "name": "get_top_products",
                        "arguments": {"criterion": "lowest_price", "limit": 5}
                    }
                }]
            }
        elif any(w in last_user_msg for w in ["danh mục sản phẩm", "toàn bộ sản phẩm", "tất cả sản phẩm", "danh sách sản phẩm"]):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_top_prods",
                    "function": {
                        "name": "get_top_products",
                        "arguments": {"criterion": "catalog", "limit": 10}
                    }
                }]
            }

        # 7. Hỏi giá sản phẩm cụ thể
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

        # 8. Yêu cầu Xuất file PDF Báo giá (Follow-up)
        export_keywords = [
            "xuất đi", "xuat di", "xuất pdf", "xuat pdf", "xuất file", "xuat file",
            "in báo giá", "in bao gia", "tải về", "tai ve"
        ]
        if any(w in last_user_msg for w in export_keywords) or last_user_msg.strip() in ["ok", "được", "duoc", "đồng ý", "dong y", "yes"]:
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_export_pdf",
                    "function": {
                        "name": "export_quotation_pdf",
                        "arguments": {"order_name": "SO-2026-DRAFT-042"}
                    }
                }]
            }

        # 9. Yêu cầu Gửi email báo giá
        email_keywords = ["gửi cho email", "gửi email", "gui email", "gửi mail", "gui mail", "@gmail", "@"]
        if any(w in last_user_msg for w in email_keywords):
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', last_user_msg)
            target_email = email_match.group(0) if email_match else "khách hàng"
            return {
                "content": "",
                "tool_calls": [{
                    "id": "call_send_email",
                    "function": {
                        "name": "send_quotation_email",
                        "arguments": {"recipient_email": target_email, "order_name": "SO-2026-DRAFT-042"}
                    }
                }]
            }

        return {
            "content": (
                "Dạ em chào Anh/Chị! Em là Chuyên viên Trợ lý AI ERP đồng hành phân tích và vận hành hệ thống Odoo của doanh nghiệp.\n\n"
                "Em có thể hỗ trợ Anh/Chị xử lý nhanh các tác vụ sau:\n"
                "• **Bán hàng & Báo giá:** Tra cứu giá niêm yết, chính sách chiết khấu, bóc tách tin nhắn lập Báo giá nháp (Draft Quotation).\n"
                "• **Kho vận:** Kiểm tra số lượng tồn kho khả dụng thời gian thực, vị trí kho và đánh giá ngưỡng an toàn (Min-Stock).\n"
                "• **Kinh doanh & Tài chính:** Báo cáo doanh số bán hàng, giá trị đơn trung bình (AOV), nhóm sản phẩm bán chạy.\n"
                "• **Tiến độ đơn hàng:** Tra cứu lịch sử đơn của khách, tình trạng xuất kho và giao vận.\n"
                "• **Quy chế nội bộ:** Tra cứu quy định bảo hành 24 tháng, chính sách 1 đổi 1 trong 30 ngày, điều kiện công nợ.\n\n"
                "Anh/Chị đang cần em kiểm tra thông tin mặt hàng hoặc hỗ trợ xử lý công việc nào trên Odoo ạ?"
            ),
            "tool_calls": []
        }
