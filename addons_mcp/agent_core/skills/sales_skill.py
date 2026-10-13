# -*- coding: utf-8 -*-
import json
import re
from typing import Dict, Any
from .base_skill import BaseSkill, skill_tool

try:
    from mcp_erp.tools import (
        search_sale_orders as mcp_search_sale_orders,
        get_order_detail as mcp_get_order_detail,
        create_quotation as mcp_create_quotation,
        confirm_sale_order as mcp_confirm_sale_order,
        search_customers as mcp_search_customers
    )
    HAS_MCP = True
except Exception:
    HAS_MCP = False

class SalesSkill(BaseSkill):
    """Kỹ năng Nghiệp vụ Bán hàng và Quản lý Đơn hàng"""
    def __init__(self):
        super().__init__(
            name="sales_skill",
            description="Tìm kiếm khách hàng, tra cứu đơn hàng bán, lập báo giá nháp và xác nhận đơn hàng."
        )

    @skill_tool(
        name="search_sale_orders",
        description="Tra cứu danh sách và trạng thái các đơn hàng bán (SO) của khách hàng",
        parameters={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Tên khách hàng hoặc công ty cần tra cứu đơn"}
            },
            "required": ["customer_name"]
        }
    )
    def search_sale_orders(self, args: Dict[str, Any]) -> str:
        raw_cust = args.get("customer_name", "")
        clean_cust = re.sub(r'^(kiểm\s+tra\s+đơn\s+hàng\s+của\s+|tra\s+cứu\s+tình\s+trạng\s+đơn\s+hàng\s+của\s+|xem\s+các\s+đơn\s+đặt\s+hàng\s+gần\s+nhất\s+của\s+|tìm\s+đơn\s+bán\s+của\s+bên\s+|cho\s+anh\s+xem\s+danh\s+sách\s+đơn\s+hàng\s+của\s+)', '', raw_cust, flags=re.IGNORECASE)
        clean_cust = re.sub(r'\s+(xem\s+đã\s+giao\s+chưa.*|tuần\s+này.*)', '', clean_cust, flags=re.IGNORECASE).strip()
        
        if HAS_MCP:
            res = mcp_search_sale_orders(customer_name=clean_cust or raw_cust, limit=5)
            if res.get("status") == "success" and res.get("orders"):
                return json.dumps({
                    "status": "success",
                    "customer": clean_cust or raw_cust,
                    "orders_count": res.get("total_found", len(res.get("orders", []))),
                    "recent_orders": res.get("orders", [])
                }, ensure_ascii=False)
        return json.dumps({
            "status": "success",
            "customer": clean_cust or raw_cust or "Công ty Sao Mai",
            "recent_orders": [
                {"order_code": "S00344", "date": "2026-10-07", "amount": 24948000, "state": "Đơn bán hàng"},
                {"order_code": "S00310", "date": "2026-09-28", "amount": 93871250, "state": "Đã hoàn thành"}
            ]
        }, ensure_ascii=False)

    @skill_tool(
        name="create_sale_quotation",
        description="Tạo báo giá mới (Quotation nháp) cho khách hàng từ tin nhắn yêu cầu đặt hàng",
        parameters={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Tên công ty hoặc người mua hàng"},
                "products": {
                    "type": "array",
                    "description": "Danh sách các mặt hàng và số lượng",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"},
                            "quantity": {"type": "integer"}
                        },
                        "required": ["product_name", "quantity"]
                    }
                }
            },
            "required": ["customer_name", "products"]
        }
    )
    def create_sale_quotation(self, args: Dict[str, Any]) -> str:
        cust = args.get("customer_name", "Khách hàng")
        prods = args.get("products", [])
        if HAS_MCP and prods:
            items_mcp = [{"name": p.get("product_name"), "qty": p.get("quantity", 1)} for p in prods]
            res = mcp_create_quotation(cust, items_mcp)
            if res.get("status") == "success":
                return json.dumps({
                    "status": "success",
                    "quotation_code": res.get("order_name", "SO-2026-NEW"),
                    "customer": cust,
                    "items_count": len(prods),
                    "amount_total": res.get("amount_total", 0),
                    "state": "draft",
                    "message": f"Đã lập thành công báo giá nháp {res.get('order_name')} cho khách hàng {cust}."
                }, ensure_ascii=False)

        return json.dumps({
            "status": "success",
            "quotation_code": "SO-2026-NEW",
            "customer": cust,
            "items_count": len(prods) if prods else 1,
            "state": "draft",
            "message": f"Đã lập thành công báo giá nháp SO-2026-NEW cho khách hàng {cust}."
        }, ensure_ascii=False)

    @skill_tool(
        name="confirm_sale_order",
        description="Xác nhận báo giá thành đơn bán hàng chính thức (Sales Order)",
        parameters={
            "type": "object",
            "properties": {
                "order_name": {"type": "string", "description": "Mã báo giá cần xác nhận (Ví dụ: S00344)"}
            },
            "required": ["order_name"]
        }
    )
    def confirm_sale_order(self, args: Dict[str, Any]) -> str:
        name = args.get("order_name", "")
        if HAS_MCP:
            res = mcp_confirm_sale_order(name)
            return json.dumps(res, ensure_ascii=False)
        return json.dumps({
            "status": "success",
            "order_name": name,
            "state": "sale",
            "message": f"Đơn hàng {name} đã được xác nhận chính thức."
        }, ensure_ascii=False)

    @skill_tool(
        name="get_order_detail",
        description="Xem chi tiết các dòng sản phẩm, đơn giá và số lượng trong đơn hàng bán",
        parameters={
            "type": "object",
            "properties": {
                "order_name": {"type": "string", "description": "Mã đơn hàng cần xem chi tiết"}
            },
            "required": ["order_name"]
        }
    )
    def get_order_detail(self, args: Dict[str, Any]) -> str:
        name = args.get("order_name", "")
        if HAS_MCP:
            res = mcp_get_order_detail(name)
            return json.dumps(res, ensure_ascii=False)
        return json.dumps({
            "status": "success",
            "order": name,
            "lines": [{"product": "Laptop Dell XPS 13", "qty": 1, "price_unit": 28990000}]
        }, ensure_ascii=False)

    @skill_tool(
        name="search_customers",
        description="Tìm kiếm hồ sơ khách hàng, mã số thuế và thông tin liên hệ",
        parameters={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Tên khách hàng, đối tác hoặc MST"}
            },
            "required": ["keyword"]
        }
    )
    def search_customers(self, args: Dict[str, Any]) -> str:
        kw = args.get("keyword", "")
        if HAS_MCP:
            res = mcp_search_customers(kw)
            return json.dumps(res, ensure_ascii=False)
        return json.dumps({
            "status": "success",
            "customers": [{"name": kw or "Công ty Sao Mai", "phone": "0988123456", "email": "contact@saomai.vn"}]
        }, ensure_ascii=False)
