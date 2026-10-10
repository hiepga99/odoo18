# -*- coding: utf-8 -*-
import os
import sys

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi font
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_core.agent import HermesAgent

# BỘ DỮ LIỆU ĐÁNH GIÁ 30 TEST CASES TIẾNG VIỆT CHO AGENT CORE
TEST_CASES = [
    # Nhóm 1: Hỏi giá sản phẩm (Expected: get_product_price)
    {"query": "Laptop Dell XPS 13 giá bao nhiêu tiền vậy em?", "expected_tool": "get_product_price"},
    {"query": "Báo giá cho anh con chuột Logitech MX Master 3S", "expected_tool": "get_product_price"},
    {"query": "Màn hình Dell UltraSharp 27 inch đơn giá thế nào?", "expected_tool": "get_product_price"},
    {"query": "Cho mình hỏi giá bán máy lọc không khí Xiaomi Pro 4", "expected_tool": "get_product_price"},
    {"query": "Chi phí mua bàn nâng hạ thông minh 2 motor là bao nhiêu?", "expected_tool": "get_product_price"},

    # Nhóm 2: Hỏi tồn kho sản phẩm (Expected: check_product_stock)
    {"query": "Trong kho còn bao nhiêu cái Laptop ThinkPad E14?", "expected_tool": "check_product_stock"},
    {"query": "Kiểm tra tồn kho bàn phím cơ Keychron K2 Pro", "expected_tool": "check_product_stock"},
    {"query": "Kho còn sẵn hàng robot hút bụi Dreame L20 không?", "expected_tool": "check_product_stock"},
    {"query": "Số lượng trong kho của ghế công thái học Sihoo M57", "expected_tool": "check_product_stock"},
    {"query": "Kiểm tra xem router wifi TP-Link AX73 có sẵn hàng không em", "expected_tool": "check_product_stock"},

    # Nhóm 3: Hỏi doanh thu & kinh doanh (Expected: get_revenue_report)
    {"query": "Tổng doanh thu bán hàng tháng 9 vừa rồi là bao nhiêu?", "expected_tool": "get_revenue_report"},
    {"query": "Tháng này công ty mình bán được bao nhiêu tiền rồi?", "expected_tool": "get_revenue_report"},
    {"query": "Báo cáo doanh số bán lẻ quý 3 của công ty", "expected_tool": "get_revenue_report"},
    {"query": "Cho xem tổng tiền bán hàng của nhóm thiết bị điện tử", "expected_tool": "get_revenue_report"},
    {"query": "Doanh thu hôm nay đạt bao nhiêu đơn và bao nhiêu tiền?", "expected_tool": "get_revenue_report"},

    # Nhóm 4: Tra cứu đơn hàng của khách (Expected: search_sale_orders)
    {"query": "Kiểm tra đơn hàng của Công ty Sao Mai xem đã giao chưa", "expected_tool": "search_sale_orders"},
    {"query": "Tra cứu tình trạng đơn hàng của khách hàng Nguyễn Văn An", "expected_tool": "search_sale_orders"},
    {"query": "Xem các đơn đặt hàng gần nhất của Công ty F-Tech", "expected_tool": "search_sale_orders"},
    {"query": "Tìm đơn bán của bên Bất động sản An Bình", "expected_tool": "search_sale_orders"},
    {"query": "Cho anh xem danh sách đơn hàng của SmartHome tuần này", "expected_tool": "search_sale_orders"},

    # Nhóm 5: Hỏi chính sách & quy trình (Expected: get_company_policy)
    {"query": "Chính sách bảo hành laptop bên mình như thế nào?", "expected_tool": "get_company_policy"},
    {"query": "Khách mua hàng về bị lỗi có được đổi trả trong 7 ngày không?", "expected_tool": "get_company_policy"},
    {"query": "Quy định chiết khấu cho khách mua đơn trên 100 triệu là bao nhiêu?", "expected_tool": "get_company_policy"},
    {"query": "Chính sách vận chuyển và miễn phí ship áp dụng khi nào?", "expected_tool": "get_company_policy"},
    {"query": "Quy chế công nợ cho khách hàng doanh nghiệp B2B như thế nào?", "expected_tool": "get_company_policy"},

    # Nhóm 6: Hội thoại xã giao / Chào hỏi (Expected: None - KHÔNG ĐƯỢC GỌI TOOL)
    {"query": "Xin chào bạn, chúc bạn một ngày tốt lành!", "expected_tool": None},
    {"query": "Bạn là ai và bạn có thể làm được những việc gì?", "expected_tool": None},
    {"query": "Cảm ơn bạn nhiều nhé, thông tin rất hữu ích", "expected_tool": None},
    {"query": "Tạm biệt bạn, hẹn gặp lại sau nhé", "expected_tool": None},
    {"query": "Trời hôm nay ở Hà Nội có đẹp không em?", "expected_tool": None},
]

def run_benchmark():
    print("=" * 80)
    print(" ĐÁNH GIÁ ĐỘ CHUẨN XÁC GỌI TOOL (AGENT CORE TOOL CALLING BENCHMARK)")
    print(" Người phụ trách: Phùng Thanh Bình (Engineer: BE/FE)")
    print(" Mục tiêu KPI đồ án: Tỷ lệ gọi đúng Tool >= 80%")
    print("=" * 80)
    
    agent = HermesAgent()
    passed_cases = 0
    total_cases = len(TEST_CASES)

    print(f"\n{'STT':<4} | {'Kỳ vọng':<22} | {'Thực tế gọi':<22} | {'Kết quả':<8} | {'Câu hỏi người dùng'}")
    print("-" * 80)

    for idx, tc in enumerate(TEST_CASES, start=1):
        agent.reset()
        result = agent.chat(tc["query"])
        actual_tool = result.get("tool_name")
        
        is_pass = (actual_tool == tc["expected_tool"])
        if is_pass:
            passed_cases += 1
            status = " ĐẠT"
        else:
            status = "❌ SAI"

        exp_str = str(tc["expected_tool"]) if tc["expected_tool"] else "(Không gọi)"
        act_str = str(actual_tool) if actual_tool else "(Không gọi)"
        
        # Cắt ngắn câu hỏi nếu quá dài
        q_display = tc["query"] if len(tc["query"]) <= 35 else tc["query"][:32] + "..."
        print(f"{idx:<4} | {exp_str:<22} | {act_str:<22} | {status:<8} | {q_display}")

    accuracy = (passed_cases / total_cases) * 100
    print("-" * 80)
    print(f"\n📊 KẾT QUẢ TỔNG HỢP:")
    print(f" * Tổng số câu hỏi kiểm thử: {total_cases}")
    print(f" * Số câu gọi chính xác:     {passed_cases}/{total_cases}")
    print(f" * ĐỘ CHÍNH XÁC ĐẠT ĐƯỢC:    {accuracy:.1f}%")
    
    if accuracy >= 80.0:
        print(f"\n🎉 KẾT LUẬN: ĐẠT CHỈ TIÊU KPI TUẦN 4! (Yêu cầu >= 80%, Thực tế: {accuracy:.1f}%)")
    else:
        print(f"\n⚠️ KẾT LUẬN: CHƯA ĐẠT CHỈ TIÊU (Cần >= 80%)")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
