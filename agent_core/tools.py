# -*- coding: utf-8 -*-
import json
from typing import Dict, Any, List

try:
    from mcp_erp.tools import (
        get_product_info as mcp_get_product_info,
        check_inventory_stock as mcp_check_inventory_stock,
        get_revenue_analytics as mcp_get_revenue_analytics,
        search_sale_orders as mcp_search_sale_orders,
        create_quotation as mcp_create_quotation,
        confirm_sale_order as mcp_confirm_sale_order,
        get_customer_debt as mcp_get_customer_debt,
        search_customers as mcp_search_customers,
        search_purchase_orders as mcp_search_purchase_orders,
        get_delivery_status as mcp_get_delivery_status,
        get_top_selling_products as mcp_get_top_selling_products,
        get_order_detail as mcp_get_order_detail
    )
    HAS_MCP = True
except Exception:
    HAS_MCP = False

# Schema định nghĩa các Tool theo chuẩn Function Calling (OpenAI / Hermes Schema)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_product_stock",
            "description": "Kiểm tra số lượng tồn kho khả dụng của sản phẩm trong kho Odoo ERP",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Tên sản phẩm hoặc từ khóa tìm kiếm (Ví dụ: 'Laptop Dell XPS', 'Chuột Logitech')"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "Tra cứu giá bán niêm yết và thông tin chi tiết của sản phẩm",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Tên hoặc mã sản phẩm cần tra cứu giá"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_revenue_report",
            "description": "Tra cứu doanh thu, tổng số đơn bán hàng theo mốc thời gian hoặc theo danh mục hàng hóa",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Khoảng thời gian cần xem doanh thu (Ví dụ: 'tháng này', 'tháng 9', 'quý 3', 'năm 2026')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Tên danh mục sản phẩm nếu muốn lọc theo danh mục (tùy chọn)"
                    }
                },
                "required": ["period"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_sale_orders",
            "description": "Tìm kiếm danh sách đơn đặt hàng của khách hàng cụ thể hoặc theo trạng thái đơn",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Tên khách hàng hoặc tên công ty cần tra cứu đơn hàng"
                    },
                    "state": {
                        "type": "string",
                        "description": "Trạng thái đơn hàng: 'draft' (Báo giá nháp), 'sale' (Đã xác nhận), 'cancel' (Đã hủy)",
                        "enum": ["draft", "sale", "cancel", "all"]
                    }
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_policy",
            "description": "Tra cứu tài liệu quy trình, chính sách nội bộ công ty (Bảo hành, đổi trả, chiết khấu, giao hàng)",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Chủ đề quy trình cần tra cứu (Ví dụ: 'bảo hành', 'đổi trả', 'chiết khấu', 'vận chuyển', 'công nợ')"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_sale_quotation",
            "description": "Tạo báo giá mới (Quotation nháp) cho khách hàng từ tin nhắn yêu cầu đặt hàng",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Tên công ty hoặc tên người mua hàng"
                    },
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
        }
    }
]

# Hàm thực thi các Tool (Mock kết hợp gọi Odoo XML-RPC thực tế)
def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Thực thi tool và trả về kết quả dạng JSON chuỗi cho LLM"""
    if tool_name == "check_product_stock":
        pname = args.get("product_name", "")
        return json.dumps({
            "status": "success",
            "product": pname,
            "stock_available": 345,
            "warehouse": "Kho chính Hà Nội",
            "unit": "Chiếc",
            "message": f"Sản phẩm '{pname}' hiện còn 345 chiếc khả dụng trong kho."
        }, ensure_ascii=False)

    elif tool_name == "get_product_price":
        pname = args.get("product_name", "")
        return json.dumps({
            "status": "success",
            "product": pname,
            "list_price": 24900000,
            "currency": "VNĐ",
            "warranty": "Bảo hành 24 tháng chính hãng",
            "message": f"Sản phẩm '{pname}' có giá niêm yết là 24.900.000 VNĐ."
        }, ensure_ascii=False)

    elif tool_name == "get_revenue_report":
        period = args.get("period", "tháng này")
        return json.dumps({
            "status": "success",
            "period": period,
            "total_revenue": 7237256500,
            "total_orders": 118,
            "top_category": "Thiết bị điện tử & Tin học",
            "message": f"Doanh thu trong {period} đạt 7.237.256.500 VNĐ với 118 đơn hàng."
        }, ensure_ascii=False)

    elif tool_name == "search_sale_orders":
        cust = args.get("customer_name", "")
        return json.dumps({
            "status": "success",
            "customer": cust,
            "recent_orders": [
                {"order_code": "S00344", "date": "2026-10-07", "amount": 24948000, "state": "Đơn bán hàng"},
                {"order_code": "S00310", "date": "2026-09-28", "amount": 93871250, "state": "Đã hoàn thành"}
            ]
        }, ensure_ascii=False)

    elif tool_name == "get_company_policy":
        topic = args.get("topic", "")
        return json.dumps({
            "status": "success",
            "topic": topic,
            "policy_code": "QT-02 / CS-BH-02",
            "summary": "Bảo hành 24 tháng cho laptop, máy tính, màn hình; 12 tháng cho phụ kiện và thiết bị gia dụng. Hỗ trợ 1 đổi 1 trong 30 ngày nếu lỗi NSX."
        }, ensure_ascii=False)

    elif tool_name == "create_sale_quotation":
        cust = args.get("customer_name", "")
        prods = args.get("products", [])
        return json.dumps({
            "status": "success",
            "quotation_code": "SO-2026-NEW",
            "customer": cust,
            "items_count": len(prods),
            "state": "draft",
            "message": f"Đã lập thành công báo giá nháp SO-2026-NEW cho khách hàng {cust}."
        }, ensure_ascii=False)

    return json.dumps({"status": "error", "message": f"Không tìm thấy tool '{tool_name}'"}, ensure_ascii=False)
