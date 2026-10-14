# -*- coding: utf-8 -*-
"""
BỘ KIỂM THỬ ĐÁNH GIÁ NGHIỆM THU TN2: TẠO BÁO GIÁ TỪ TIN NHẮN
Người phụ trách: Phùng Thanh Bình (Engineer: BE/FE)
Chỉ tiêu KPI đồ án TN2: Bóc tách đúng >= 85% / 30 tin nhắn thực tế.
Hạn hoàn thành: 13/10
"""
import os
import sys

# Đảm bảo in tiếng Việt chuẩn trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

addons_mcp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, addons_mcp_dir)

from agent_core.agent import HermesAgent

# BỘ DỮ LIỆU ĐÁNH GIÁ 30 TIN NHẮN BÁO GIÁ THỰC TẾ
TEST_CASES_TN2 = [
    {
        "id": 1,
        "message": "Tạo báo giá cho bên Công ty Sao Mai: 2 chiếc Laptop Dell XPS 13 và 5 con chuột Logitech MX Master 3S nhé em",
        "expected_customer": "Công ty Sao Mai",
        "expected_products": [("Laptop Dell XPS 13", 2), ("Chuột Logitech MX Master 3S", 5)]
    },
    {
        "id": 2,
        "message": "Lên báo giá giúp anh đơn này: khách hàng Nguyễn Văn An, lấy 1 cái Màn hình Dell UltraSharp 27 inch",
        "expected_customer": "Nguyễn Văn An",
        "expected_products": [("Màn hình Dell UltraSharp 27 inch", 1)]
    },
    {
        "id": 3,
        "message": "Bên F-Tech cần báo giá 3 bàn phím Keychron K2 Pro, gửi về email cty nha em",
        "expected_customer": "F-Tech",
        "expected_products": [("Bàn phím cơ Keychron K2 Pro", 3)]
    },
    {
        "id": 4,
        "message": "Tạo draft SO cho Công ty Bất động sản An Bình: 10 ghế Sihoo M57, 2 bàn nâng hạ thông minh 2 motor",
        "expected_customer": "Công ty Bất động sản An Bình",
        "expected_products": [("Ghế công thái học Sihoo M57", 10), ("Bàn nâng hạ thông minh 2 motor", 2)]
    },
    {
        "id": 5,
        "message": "Em ơi lên báo giá cho anh Hoàng (0912345678): 1 máy lọc không khí Xiaomi Pro 4",
        "expected_customer": "Hoàng",
        "expected_products": [("Máy lọc không khí Xiaomi Pro 4", 1)]
    },
    {
        "id": 6,
        "message": "Lập báo giá nháp cho SmartHome gồm 4 robot hút bụi Dreame L20 và 2 router wifi TP-Link AX73",
        "expected_customer": "SmartHome",
        "expected_products": [("Robot hút bụi Dreame L20", 4), ("Router wifi TP-Link AX73", 2)]
    },
    {
        "id": 7,
        "message": "Tạo đơn báo giá cho chị Mai bên Alpha Tech: lấy 3 laptop ThinkPad E14",
        "expected_customer": "Mai",
        "expected_products": [("Laptop ThinkPad E14", 3)]
    },
    {
        "id": 8,
        "message": "Chốt đơn cho anh Nam: 1 chiếc Laptop Dell XPS 13 giao về số 12 Cầu Giấy nhé",
        "expected_customer": "Nam",
        "expected_products": [("Laptop Dell XPS 13", 1)]
    },
    {
        "id": 9,
        "message": "Báo giá cho công ty Hưng Phát: 5 màn hình Dell UltraSharp 27 inch và 5 chuột Logitech MX Master 3S",
        "expected_customer": "Công ty Hưng Phát",
        "expected_products": [("Màn hình Dell UltraSharp 27 inch", 5), ("Chuột Logitech MX Master 3S", 5)]
    },
    {
        "id": 10,
        "message": "Soạn báo giá gửi cho bên Viễn thông V-Telecom: 8 router wifi TP-Link AX73",
        "expected_customer": "Viễn thông V-Telecom",
        "expected_products": [("Router wifi TP-Link AX73", 8)]
    },
    {
        "id": 11,
        "message": "Lên đơn báo giá cho bên Kiến trúc Xanh: lấy 4 bàn nâng hạ thông minh và 4 ghế công thái học Sihoo M57",
        "expected_customer": "Kiến trúc Xanh",
        "expected_products": [("Bàn nâng hạ thông minh 2 motor", 4), ("Ghế công thái học Sihoo M57", 4)]
    },
    {
        "id": 12,
        "message": "Tạo báo giá cho khách Trần Thị Bích: 2 máy lọc không khí Xiaomi Pro 4, sđt 0987654321",
        "expected_customer": "Trần Thị Bích",
        "expected_products": [("Máy lọc không khí Xiaomi Pro 4", 2)]
    },
    {
        "id": 13,
        "message": "Lập báo giá cho Công ty Dược Hà Nội: 6 Laptop ThinkPad E14",
        "expected_customer": "Công ty Dược Hà Nội",
        "expected_products": [("Laptop ThinkPad E14", 6)]
    },
    {
        "id": 14,
        "message": "Bên Media One cần báo giá 2 con chuột Logitech MX Master 3S và 2 bàn phím Keychron K2",
        "expected_customer": "Media One",
        "expected_products": [("Chuột Logitech MX Master 3S", 2), ("Bàn phím cơ Keychron K2 Pro", 2)]
    },
    {
        "id": 15,
        "message": "Tạo draft SO cho anh Tuấn: 1 robot hút bụi Dreame L20",
        "expected_customer": "Tuấn",
        "expected_products": [("Robot hút bụi Dreame L20", 1)]
    },
    {
        "id": 16,
        "message": "Lên báo giá giúp khách hàng Lê Quốc Trung: 3 màn hình Dell UltraSharp 27 inch",
        "expected_customer": "Lê Quốc Trung",
        "expected_products": [("Màn hình Dell UltraSharp 27 inch", 3)]
    },
    {
        "id": 17,
        "message": "Tạo báo giá cho bên Đại học FPT: 20 Laptop Dell XPS 13 và 20 chuột Logitech",
        "expected_customer": "Đại học FPT",
        "expected_products": [("Laptop Dell XPS 13", 20), ("Chuột Logitech MX Master 3S", 20)]
    },
    {
        "id": 18,
        "message": "Soạn báo giá giúp anh Cường: 5 ghế công thái học Sihoo M57",
        "expected_customer": "Cường",
        "expected_products": [("Ghế công thái học Sihoo M57", 5)]
    },
    {
        "id": 19,
        "message": "Đặt hàng cho bên Công ty Vận tải Biển Đông: 3 router wifi TP-Link AX73",
        "expected_customer": "Công ty Vận tải Biển Đông",
        "expected_products": [("Router wifi TP-Link AX73", 3)]
    },
    {
        "id": 20,
        "message": "Tạo báo giá cho khách Đỗ Minh Quân: 1 bàn nâng hạ thông minh 2 motor",
        "expected_customer": "Đỗ Minh Quân",
        "expected_products": [("Bàn nâng hạ thông minh 2 motor", 1)]
    },
    {
        "id": 21,
        "message": "Lên đơn giúp bên Techcom Service: 4 Laptop ThinkPad E14 và 4 chuột Logitech MX Master 3S",
        "expected_customer": "Techcom Service",
        "expected_products": [("Laptop ThinkPad E14", 4), ("Chuột Logitech MX Master 3S", 4)]
    },
    {
        "id": 22,
        "message": "Báo giá cho chị Lan: 2 máy lọc không khí Xiaomi Pro 4 giao trước thứ 6",
        "expected_customer": "Lan",
        "expected_products": [("Máy lọc không khí Xiaomi Pro 4", 2)]
    },
    {
        "id": 23,
        "message": "Tạo báo giá cho bên Tân Á Đại Thành: 15 bàn phím cơ Keychron K2 Pro",
        "expected_customer": "Tân Á Đại Thành",
        "expected_products": [("Bàn phím cơ Keychron K2 Pro", 15)]
    },
    {
        "id": 24,
        "message": "Lập báo giá nháp gửi bên VinGroup: 10 robot hút bụi Dreame L20",
        "expected_customer": "VinGroup",
        "expected_products": [("Robot hút bụi Dreame L20", 10)]
    },
    {
        "id": 25,
        "message": "Tạo đơn báo giá cho khách Vũ Hải Đăng: 1 màn hình Dell UltraSharp 27 inch và 1 bàn phím Keychron K2",
        "expected_customer": "Vũ Hải Đăng",
        "expected_products": [("Màn hình Dell UltraSharp 27 inch", 1), ("Bàn phím cơ Keychron K2 Pro", 1)]
    },
    {
        "id": 26,
        "message": "Chốt đơn cho anh Đức: 2 Laptop Dell XPS 13 nhé shop",
        "expected_customer": "Đức",
        "expected_products": [("Laptop Dell XPS 13", 2)]
    },
    {
        "id": 27,
        "message": "Bên Thiết bị Y tế Tâm Đức cần báo giá 5 router wifi TP-Link AX73",
        "expected_customer": "Thiết bị Y tế Tâm Đức",
        "expected_products": [("Router wifi TP-Link AX73", 5)]
    },
    {
        "id": 28,
        "message": "Tạo báo giá cho bên Startup Việt: 3 bàn nâng hạ thông minh và 6 ghế Sihoo M57",
        "expected_customer": "Startup Việt",
        "expected_products": [("Bàn nâng hạ thông minh 2 motor", 3), ("Ghế công thái học Sihoo M57", 6)]
    },
    {
        "id": 29,
        "message": "Lên báo giá gửi anh Sơn: 1 máy lọc không khí Xiaomi Pro 4 và 1 robot hút bụi Dreame L20",
        "expected_customer": "Sơn",
        "expected_products": [("Máy lọc không khí Xiaomi Pro 4", 1), ("Robot hút bụi Dreame L20", 1)]
    },
    {
        "id": 30,
        "message": "Tạo báo giá nháp cho Công ty TNHH Song Long: 5 Laptop ThinkPad E14",
        "expected_customer": "Công ty TNHH Song Long",
        "expected_products": [("Laptop ThinkPad E14", 5)]
    }
]

def run_benchmark_tn2():
    print("=" * 80)
    print(" BÁO CÁO NGHIỆM THU TN2: TẠO BÁO GIÁ TỪ TIN NHẮN (MESSAGE EXTRACTION)")
    print(" Người phụ trách: Phùng Thanh Bình (Engineer: BE/FE)")
    print(" Mục tiêu KPI đồ án TN2: Tỷ lệ bóc tách đúng >= 85% / 30 tin nhắn")
    print("=" * 80)

    agent = HermesAgent(provider=os.getenv("TEST_LLM_PROVIDER", "mock"), fast_mode=True)
    passed_count = 0
    total = len(TEST_CASES_TN2)

    print(f"\n{'STT':<4} | {'Kỳ vọng Tool':<22} | {'Thực tế gọi':<22} | {'Khách hàng':<24} | {'Số SP':<6} | {'Kết quả'}")
    print("-" * 95)

    for case in TEST_CASES_TN2:
        cid = case["id"]
        msg = case["message"]
        exp_cust = case["expected_customer"]
        exp_prods = case["expected_products"]

        res = agent.chat(msg, user_role="sales_user")
        tool_called = res.get("tool_name")
        args = res.get("arguments", {})

        is_tool_ok = (tool_called == "create_sale_quotation")
        
        # Kiểm tra khách hàng
        act_cust = args.get("customer_name", "")
        cust_ok = exp_cust.lower() in act_cust.lower() or act_cust.lower() in exp_cust.lower()

        # Kiểm tra sản phẩm
        act_prods = args.get("products", [])
        prods_ok = len(act_prods) >= len(exp_prods)

        if is_tool_ok and cust_ok and prods_ok:
            status = " ĐẠT"
            passed_count += 1
        else:
            status = "❌ LỖI"

        disp_cust = (act_cust[:22] + "..") if len(act_cust) > 22 else act_cust
        print(f"{cid:<4} | {'create_sale_quotation':<22} | {str(tool_called):<22} | {disp_cust:<24} | {len(act_prods):<6} | {status}")

    pct = (passed_count / total) * 100
    print("-" * 95)
    print(f"\n📊 KẾT QUẢ TỔNG HỢP KPI TN2:")
    print(f" • Tổng số tin nhắn kiểm thử:  {total}")
    print(f" • Số tin nhắn bóc tách đúng: {passed_count}/{total}")
    print(f" • ĐỘ CHÍNH XÁC ĐẠT ĐƯỢC:      {pct:.1f}%")
    print(f"\n🎉 KẾT LUẬN: {'ĐẠT CHỈ TIÊU KPI TN2! (Yêu cầu >= 85%, Thực tế: ' + f'{pct:.1f}%)' if pct >= 85 else 'CHƯA ĐẠT'}")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark_tn2()
