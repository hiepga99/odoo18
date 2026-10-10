import os
import json
import random
from datetime import datetime, timedelta

os.makedirs('data/invoices', exist_ok=True)

# Đọc danh sách sản phẩm và khách hàng từ Odoo hoặc danh sách chuẩn
BUYERS = [
    {"name": "Công ty TNHH Công nghệ Alpha Việt Nam", "tax_code": "0108923412", "address": "Tầng 5, Tòa Keangnam Landmark 72, Nam Từ Liêm, Hà Nội", "contact": "Nguyễn Văn Hùng"},
    {"name": "Công ty Cổ phần Thương mại & Dịch vụ Sao Mai", "tax_code": "0314567890", "address": "Số 45 Lê Duẩn, Bến Nghé, Quận 1, TP. Hồ Chí Minh", "contact": "Trần Thị Mai"},
    {"name": "Công ty TNHH Giải pháp Phần mềm F-Tech", "tax_code": "0107891234", "address": "Tòa nhà FPT, Phố Duy Tân, Dịch Vọng Hậu, Cầu Giấy, Hà Nội", "contact": "Lê Tuấn Anh"},
    {"name": "Công ty CP Đầu tư & Phát triển Bất động sản An Bình", "tax_code": "0315678901", "address": "120 Nguyễn Thị Minh Khai, Võ Thị Sáu, Quận 3, TP. Hồ Chí Minh", "contact": "Phạm Quốc Bảo"},
    {"name": "Công ty TNHH LogiTech Solution Đà Nẵng", "tax_code": "0401889922", "address": "Số 15 Quang Trung, Thạch Thang, Hải Châu, Đà Nẵng", "contact": "Hoàng Minh Trí"},
    {"name": "Công ty CP Phân phối Thiết bị Thông minh SmartHome", "tax_code": "0316789012", "address": "Tòa nhà Landmark 81, Phường 22, Bình Thạnh, TP. Hồ Chí Minh", "contact": "Vũ Thu Trang"},
    {"name": "Công ty TNHH Thương mại Quốc tế Hòa Phát Tech", "tax_code": "0106789234", "address": "Số 88 Trần Hưng Đạo, Cửa Nam, Hoàn Kiếm, Hà Nội", "contact": "Đỗ Quang Vinh"},
    {"name": "Công ty CP Bán lẻ Kỹ thuật số Nam Á", "tax_code": "0317890123", "address": "64 Võ Văn Tần, Phường 6, Quận 3, TP. Hồ Chí Minh", "contact": "Ngô Bích Ngọc"},
    {"name": "Công ty TNHH Dịch vụ Truyền thông & Quảng cáo Sen Vàng", "tax_code": "0318901234", "address": "10 Mai Chí Thọ, An Phú, TP. Thủ Đức, TP. Hồ Chí Minh", "contact": "Đinh Hoàng Yến"},
    {"name": "Công ty CP Thiết bị Văn phòng Hiện Đại M-Office", "tax_code": "0105678901", "address": "Số 204 Hoàng Quốc Việt, Cổ Nhuế 1, Cầu Giấy, Hà Nội", "contact": "Bùi Văn Nam"},
    {"name": "Viện Nghiên cứu & Ứng dụng Công nghệ Mới", "tax_code": "0101234567", "address": "1 Đại Cồ Việt, Bách Khoa, Hai Bà Trưng, Hà Nội", "contact": "TS. Trần Văn Phong"},
    {"name": "Công ty TNHH Chuỗi Cung ứng Toàn Cầu V-Logistics", "tax_code": "3603456789", "address": "Đường 2A, KCN Biên Hòa 2, Long Bình Tân, Đồng Nai", "contact": "Lê Văn Thịnh"},
    {"name": "Công ty CP Xây dựng & Nội thất Vinadesign", "tax_code": "0201998877", "address": "18 Võ Thị Sáu, Máy Tơ, Ngô Quyền, Hải Phòng", "contact": "Trương Minh Đạt"},
    {"name": "Trung tâm Đào tạo Tin học & Ngoại ngữ Tân Tiến", "tax_code": "0402112233", "address": "254 Nguyễn Văn Linh, Thạc Gián, Thanh Khê, Đà Nẵng", "contact": "Nguyễn Hoàng Oanh"},
    {"name": "Công ty TNHH Sản xuất & Thương mại Gia dụng Sunhouse Mart", "tax_code": "2300998877", "address": "Khu công nghiệp Tiên Sơn, Đồng Nguyên, Từ Sơn, Bắc Ninh", "contact": "Phan Đình Trọng"},
]

PRODUCTS_CATALOG = [
    ("SP0001", "Laptop Dell XPS 13 Plus 9320 (i7-1360P/16GB/512GB)", "Chiếc", 34500000),
    ("SP0002", "Laptop Dell Latitude 3440 (i5-1335U/8GB/256GB)", "Chiếc", 15900000),
    ("SP0004", "Laptop Asus Zenbook 14 OLED UX3405 (Ultra 7/16GB/1TB)", "Chiếc", 28900000),
    ("SP0011", "Laptop Apple MacBook Air 13 inch M2 (8GB/256GB)", "Chiếc", 24900000),
    ("SP0014", "Màn hình Dell UltraSharp 27 inch 4K U2723QE", "Chiếc", 13200000),
    ("SP0015", "Màn hình Dell P2422H 23.8 inch FHD IPS", "Chiếc", 3990000),
    ("SP0016", "Màn hình LG 27UP850N-W 27 inch 4K Type-C", "Chiếc", 8900000),
    ("SP0027", "Ổ cứng SSD Samsung 990 Pro 1TB M.2 PCIe 4.0", "Chiếc", 2850000),
    ("SP0030", "Ổ cứng di động SSD SanDisk Extreme E61 1TB Chống nước", "Chiếc", 2950000),
    ("SP0031", "Chuột không dây Logitech MX Master 3S", "Chiếc", 2350000),
    ("SP0035", "Bàn phím cơ không dây Keychron K2 Pro QMK/VIA", "Chiếc", 2190000),
    ("SP0040", "Tai nghe chụp tai chống ồn Sony WH-1000XM5", "Chiếc", 7990000),
    ("SP0048", "Webcam Logitech C920 Pro HD 1080p", "Chiếc", 1650000),
    ("SP0056", "Router Wifi 6 TP-Link Archer AX73 AX5400", "Chiếc", 2250000),
    ("SP0064", "Switch mạng quản trị Cisco CBS110-24T-EU 24 Port Gigabit", "Chiếc", 3950000),
    ("SP0076", "Robot hút bụi lau nhà Dreame L20 Ultra Tự giặt giẻ sấy khô", "Chiếc", 18900000),
    ("SP0078", "Máy lọc không khí Xiaomi Smart Air Purifier 4 Pro", "Chiếc", 4890000),
    ("SP0080", "Nồi chiên không dầu Philips HD9650/91 dung tích XXL 1.4kg", "Chiếc", 5490000),
    ("SP0101", "Ghế công thái học Ergonomic Sihoo M57 Lưới thoáng khí", "Chiếc", 3850000),
    ("SP0104", "Bàn nâng hạ thông minh tự động điều chỉnh độ cao 2 motor", "Chiếc", 6900000),
    ("SP0107", "Máy in Laser đa năng HP LaserJet MFP M141w", "Chiếc", 3950000),
    ("SP0114", "Thùng 5 ram giấy in Double A A4 70gsm", "Thùng", 345000),
]

SELLER = {
    "name": "CÔNG TY TNHH GIẢI PHÁP CÔNG NGHỆ VÀ THƯƠNG MẠI VIỆT NAM",
    "tax_code": "0109988776",
    "address": "Số 18 Duy Tân, Phường Dịch Vọng Hậu, Quận Cầu Giấy, TP. Hà Nội",
    "phone": "0243 789 9999",
    "email": "hoadon@congnghevietnam.com.vn",
    "bank_account": "19038899220018 tại Ngân hàng TMCP Kỹ Thương Việt Nam (Techcombank) - CN Cầu Giấy"
}

def num_to_vietnamese_words(num):
    # Đơn giản hóa chuyển đổi số tiền thành chữ
    if num >= 1_000_000_000:
        ty = num // 1_000_000_000
        trieu = (num % 1_000_000_000) // 1_000_000
        return f"{ty} tỷ {trieu} triệu đồng"
    elif num >= 1_000_000:
        trieu = num // 1_000_000
        nghin = (num % 1_000_000) // 1_000
        if nghin > 0:
            return f"{trieu} triệu {nghin} nghìn đồng"
        return f"{trieu} triệu đồng"
    elif num >= 1_000:
        return f"{num // 1_000} nghìn đồng"
    return f"{num} đồng"

all_invoices = []
base_date = datetime(2026, 10, 7)

for i in range(1, 101):
    inv_num = f"HD2026-{i:04d}"
    lookup_code = f"VNP{random.randint(10000000, 99999999)}"
    days_ago = random.randint(1, 350)
    inv_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    buyer = random.choice(BUYERS)
    
    # Chọn 1-4 mặt hàng
    num_items = random.randint(1, 4)
    items = random.sample(PRODUCTS_CATALOG, num_items)
    
    inv_items = []
    subtotal = 0
    vat_total = 0
    
    for idx, (code, name, unit, price) in enumerate(items, start=1):
        qty = random.choice([1, 2, 3, 5, 10])
        amt = price * qty
        vat_rate = random.choice([8, 10]) # Thuế VAT 8% hoặc 10%
        vat_amt = int(amt * vat_rate / 100)
        
        inv_items.append({
            "line_number": idx,
            "product_code": code,
            "product_name": name,
            "unit": unit,
            "quantity": qty,
            "unit_price": price,
            "amount": amt,
            "vat_rate_percent": vat_rate,
            "vat_amount": vat_amt,
            "total_line_amount": amt + vat_amt
        })
        subtotal += amt
        vat_total += vat_amt
        
    total_amount = subtotal + vat_total
    
    inv_data = {
        "invoice_number": inv_num,
        "invoice_series": "1C26TBB",
        "invoice_date": inv_date,
        "lookup_code": lookup_code,
        "payment_method": random.choice(["Chuyển khoản", "Tiền mặt / Chuyển khoản", "Chuyển khoản"]),
        "currency": "VND",
        "seller": SELLER,
        "buyer": {
            "company_name": buyer["name"],
            "tax_code": buyer["tax_code"],
            "address": buyer["address"],
            "contact_person": buyer["contact"],
        },
        "items": inv_items,
        "subtotal_amount": subtotal,
        "vat_amount": vat_total,
        "total_amount": total_amount,
        "total_amount_in_words": num_to_vietnamese_words(total_amount),
        "status": "Đã ký số",
        "signer": "Nguyễn Văn Giám Đốc",
        "signature_date": inv_date + " 17:30:00"
    }
    
    all_invoices.append(inv_data)
    
    # Ghi file lẻ
    with open(f"data/invoices/invoice_{i:03d}.json", "w", encoding="utf-8") as f:
        json.dump(inv_data, f, ensure_ascii=False, indent=2)

# Ghi file tổng
with open("data/invoices/all_invoices_dataset.json", "w", encoding="utf-8") as f:
    json.dump(all_invoices, f, ensure_ascii=False, indent=2)

print(f"Generated {len(all_invoices)} invoices successfully!")
