# -*- coding: utf-8 -*-
import os
import sys
import unittest

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_erp.server import MCPServer
from mcp_erp.tools import (
    get_product_info,
    check_inventory_stock,
    search_customers,
    get_customer_debt,
    search_sale_orders,
    get_order_detail,
    create_quotation,
    confirm_sale_order,
    get_revenue_analytics,
    search_purchase_orders,
    get_delivery_status,
    get_top_selling_products,
    MCP_TOOL_MAP
)

class TestMCPERPTools(unittest.TestCase):
    """
    Bộ Unit Test toàn diện cho 12 công cụ MCP kết nối Odoo 18 ERP.
    Mục tiêu KPI Tuần 5: >= 10 Tools, Unit test đạt 100% PASS.
    """
    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def test_01_tool_count_meets_kpi(self):
        """Kiểm tra số lượng tools MCP có đạt chỉ tiêu >= 10 tools hay không"""
        tool_count = len(self.server.list_tools())
        self.assertGreaterEqual(tool_count, 10, f"Yêu cầu >= 10 tools, thực tế có {tool_count}")
        print(f"\n[Test 1] Số lượng MCP Tools: {tool_count} (ĐẠT KPI >= 10 tools)")

    def test_02_get_product_info(self):
        """Tool 1: Tra cứu chi tiết sản phẩm (Laptop Dell)"""
        res = get_product_info("Laptop Dell")
        self.assertIn(res["status"], ["success", "not_found"])
        if res["status"] == "success":
            self.assertIn("list_price", res)
            self.assertGreater(res["list_price"], 0)
        print("[Test 2] Tool 1: get_product_info -> PASS")

    def test_03_check_inventory_stock(self):
        """Tool 2: Kiểm tra tồn kho khả dụng"""
        res = check_inventory_stock("Chuột")
        self.assertIn(res["status"], ["success", "not_found"])
        if res["status"] == "success":
            self.assertIn("qty_on_hand", res)
        print("[Test 3] Tool 2: check_inventory_stock -> PASS")

    def test_04_search_customers(self):
        """Tool 3: Tìm kiếm khách hàng"""
        res = search_customers("Sao Mai", limit=2)
        self.assertEqual(res["status"], "success")
        self.assertIn("customers", res)
        print("[Test 4] Tool 3: search_customers -> PASS")

    def test_05_get_customer_debt(self):
        """Tool 4: Tra cứu công nợ khách hàng"""
        res = get_customer_debt("Sao Mai")
        self.assertIn(res["status"], ["success", "not_found"])
        if res["status"] == "success":
            self.assertIn("total_debt", res)
        print("[Test 5] Tool 4: get_customer_debt -> PASS")

    def test_06_search_sale_orders(self):
        """Tool 5: Tra cứu đơn hàng bán"""
        res = search_sale_orders(limit=3)
        self.assertEqual(res["status"], "success")
        self.assertIn("orders", res)
        self.assertGreater(res["count"], 0)
        print("[Test 6] Tool 5: search_sale_orders -> PASS")

    def test_07_get_order_detail(self):
        """Tool 6: Xem chi tiết dòng sản phẩm của đơn hàng"""
        # Lấy 1 đơn bất kỳ
        orders_res = search_sale_orders(limit=1)
        if orders_res["orders"]:
            order_code = orders_res["orders"][0]["code"]
            res = get_order_detail(order_code)
            self.assertEqual(res["status"], "success")
            self.assertIn("items", res)
        print("[Test 7] Tool 6: get_order_detail -> PASS")

    def test_08_create_quotation_and_confirm(self):
        """Tool 7 & 8: Tạo báo giá nháp mới và xác nhận đơn hàng"""
        items = [{"product_name": "Laptop Dell", "quantity": 1}]
        res = create_quotation("Sao Mai", items)
        self.assertEqual(res["status"], "success")
        self.assertIn("order_code", res)
        new_code = res["order_code"]
        
        # Tool 8: Confirm đơn vừa tạo
        confirm_res = confirm_sale_order(new_code)
        self.assertEqual(confirm_res["status"], "success")
        print(f"[Test 8] Tool 7 & 8: create_quotation ({new_code}) & confirm_sale_order -> PASS")

    def test_09_get_revenue_analytics(self):
        """Tool 9: Báo cáo phân tích doanh thu"""
        res = get_revenue_analytics(period="all")
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_revenue"], 0)
        self.assertGreater(res["confirmed_orders_count"], 0)
        print("[Test 9] Tool 9: get_revenue_analytics -> PASS")

    def test_10_search_purchase_orders(self):
        """Tool 10: Tra cứu đơn mua hàng từ nhà cung cấp"""
        res = search_purchase_orders(limit=3)
        self.assertEqual(res["status"], "success")
        self.assertIn("purchase_orders", res)
        self.assertGreater(res["count"], 0)
        print("[Test 10] Tool 10: search_purchase_orders -> PASS")

    def test_11_get_delivery_status(self):
        """Tool 11: Tra cứu phiếu xuất kho / giao hàng"""
        res = get_delivery_status(limit=3)
        self.assertEqual(res["status"], "success")
        self.assertIn("delivery_orders", res)
        print("[Test 11] Tool 11: get_delivery_status -> PASS")

    def test_12_get_top_selling_products(self):
        """Tool 12: Thống kê Top sản phẩm bán chạy nhất"""
        res = get_top_selling_products(limit=5)
        self.assertEqual(res["status"], "success")
        self.assertIn("top_products", res)
        print("[Test 12] Tool 12: get_top_selling_products -> PASS")

    def test_13_mcp_server_dispatch(self):
        """Kiểm tra máy chủ MCP điều phối gọi tool hợp lệ và bắt lỗi tool không tồn tại"""
        # Gọi tool hợp lệ qua MCP
        res = self.server.call_tool("check_inventory_stock", {"product_name": "Laptop Dell"})
        self.assertIn(res["status"], ["success", "not_found"])
        
        # Gọi tool không tồn tại
        err_res = self.server.call_tool("invalid_tool_name", {})
        self.assertEqual(err_res["status"], "error")
        print("[Test 13] MCPServer dispatch & error handling -> PASS")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMCPERPTools)
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    result = runner.run(suite)
    
    total = result.testsRun
    failed = len(result.failures)
    errored = len(result.errors)
    passed = total - failed - errored
    pass_rate = (passed / total) * 100

    print("\n" + "=" * 70)
    print(f"📊 BÁO CÁO KẾT QUẢ UNIT TEST MCP TOOLS (TUẦN 5 - DEADLINE 11/10)")
    print(f" Người phụ trách: Phùng Thanh Bình (Engineer: BE/FE)")
    print(f" * Tổng số Unit Tests: {total}")
    print(f" * Số bài test thành công (PASS): {passed}/{total}")
    print(f" * TỶ LỆ ĐẠT (PASS RATE): {pass_rate:.1f}%")
    if pass_rate == 100.0:
        print(f"🎉 KẾT LUẬN: ĐẠT CHỈ TIÊU KPI 100% UNIT TEST!")
    print("=" * 70)
