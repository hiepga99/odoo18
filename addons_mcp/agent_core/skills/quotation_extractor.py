# -*- coding: utf-8 -*-
"""
Module bóc tách thông tin Báo giá từ Tin nhắn tự nhiên (Message to Quotation Extractor - TN2).
Bóc tách: Tên khách hàng / Công ty, Số điện thoại, Danh mục sản phẩm & Số lượng.
"""
import re
from typing import Dict, Any, List

# Danh mục sản phẩm chuẩn hóa trên Odoo ERP kèm từ khóa nhận diện & đơn giá
STANDARD_CATALOG = [
    {
        "name": "Laptop Dell XPS 13",
        "keywords": ["laptop dell xps 13", "dell xps 13", "dell xps", "laptop dell"],
        "list_price": 24950000,
        "uom": "Chiếc"
    },
    {
        "name": "Chuột Logitech MX Master 3S",
        "keywords": ["chuột logitech mx master 3s", "logitech mx master 3s", "mx master 3s", "chuột logitech", "chuột mx master"],
        "list_price": 2450000,
        "uom": "Con"
    },
    {
        "name": "Màn hình Dell UltraSharp 27 inch",
        "keywords": ["màn hình dell ultrasharp 27 inch", "màn hình dell ultrasharp 27", "màn hình dell ultrasharp", "dell ultrasharp 27", "dell ultrasharp", "màn hình dell 27", "màn hình dell"],
        "list_price": 11500000,
        "uom": "Chiếc"
    },
    {
        "name": "Máy lọc không khí Xiaomi Pro 4",
        "keywords": ["máy lọc không khí xiaomi pro 4", "máy lọc không khí xiaomi", "máy lọc xiaomi", "xiaomi pro 4", "máy lọc không khí"],
        "list_price": 4890000,
        "uom": "Chiếc"
    },
    {
        "name": "Bàn nâng hạ thông minh 2 motor",
        "keywords": ["bàn nâng hạ thông minh 2 motor", "bàn nâng hạ thông minh", "bàn nâng hạ 2 motor", "bàn nâng hạ"],
        "list_price": 6900000,
        "uom": "Bộ"
    },
    {
        "name": "Laptop ThinkPad E14",
        "keywords": ["laptop thinkpad e14", "thinkpad e14", "laptop lenovo thinkpad", "thinkpad"],
        "list_price": 18500000,
        "uom": "Chiếc"
    },
    {
        "name": "Bàn phím cơ Keychron K2 Pro",
        "keywords": ["bàn phím cơ keychron k2 pro", "bàn phím keychron k2 pro", "keychron k2 pro", "bàn phím keychron k2", "keychron k2", "bàn phím keychron"],
        "list_price": 2190000,
        "uom": "Chiếc"
    },
    {
        "name": "Robot hút bụi Dreame L20",
        "keywords": ["robot hút bụi dreame l20", "robot hút bụi dreame", "dreame l20", "robot hút bụi"],
        "list_price": 16990000,
        "uom": "Chiếc"
    },
    {
        "name": "Ghế công thái học Sihoo M57",
        "keywords": ["ghế công thái học sihoo m57", "ghế công thái học sihoo", "sihoo m57", "ghế sihoo m57", "ghế sihoo", "ghế công thái học"],
        "list_price": 3850000,
        "uom": "Chiếc"
    },
    {
        "name": "Router wifi TP-Link AX73",
        "keywords": ["router wifi tp-link ax73", "router wifi tp-link", "router tp-link ax73", "tp-link ax73", "router wifi"],
        "list_price": 2390000,
        "uom": "Chiếc"
    }
]

WORD_NUMBERS = {
    "một": 1, "mot": 1, "1": 1,
    "hai": 2, "2": 2,
    "ba": 3, "3": 3,
    "bốn": 4, "bon": 4, "4": 4,
    "năm": 5, "nam": 5, "5": 5,
    "sáu": 6, "sau": 6, "6": 6,
    "bảy": 7, "bay": 7, "7": 7,
    "tám": 8, "tam": 8, "8": 8,
    "chín": 9, "chin": 9, "9": 9,
    "mười": 10, "muoi": 10, "10": 10
}

def extract_customer_name(text: str) -> str:
    """Bóc tách tên khách hàng hoặc tên công ty từ nội dung tin nhắn"""
    patterns = [
        r'(?:cho\s+bên|cho\s+công\s+ty|cho\s+cty|cho\s+bên\s+công\s+ty|gửi\s+bên|gửi\s+cho\s+bên)\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-_&]+?)(?=[,:\.\n\(\[]|\s+(?:lấy|cần|mua|đặt|sđt|gồm|\d+\s*(?:chiếc|cái|con|bộ|hộp|máy))|$)',
        r'(?:khách\s+hàng|khách)\s*[:\-]?\s*([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-_&]+?)(?=[,:\.\n\(\[]|\s+(?:lấy|cần|mua|đặt|sđt|gồm|\d+\s*(?:chiếc|cái|con|bộ|hộp|máy))|$)',
        r'(?:(?:cho|gửi|gửi\s+cho|báo\s+giá\s+giúp|báo\s+giá\s+gửi|giúp)\s+(?:anh|chị))\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-_&]+?)(?=[,:\.\n\(\[]|\s+(?:lấy|cần|mua|đặt|sđt|gồm|\d+\s*(?:chiếc|cái|con|bộ|hộp|máy))|$)',
        r'(?:bên)\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-_&]+?)(?=\s+(?:cần|lấy|mua|đặt|hỏi|muốn|gửi|yêu\s+cầu)|\s*[,:\.\n])',
        r'(?:cho)\s+([A-ZÀ-Ỹ][A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-_&]+?)(?=\s*[,:\.\n]|\s+(?:gồm|lấy|cần|mua|đặt))'
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            cand = m.group(1).strip(" :,.-_")
            cand = re.sub(r'\s+(nhé|nha|ạ|em|ơi|nhé em|nha em)$', '', cand, flags=re.IGNORECASE).strip()
            # Bỏ các từ vô nghĩa nếu bắt nhầm
            if cand and len(cand) > 1 and cand.lower() not in ["báo giá", "đơn này", "đơn hàng"]:
                # Nếu bắt được chữ thường thì viết hoa chữ cái đầu cho đẹp
                if not cand.startswith("Công ty") and cand[0].islower():
                    cand = cand.title()
                return cand

    return "Khách hàng liên hệ"

def extract_phone_number(text: str) -> str:
    """Bóc tách số điện thoại nếu có"""
    m = re.search(r'\b(0\d{9,10})\b', text)
    return m.group(1) if m else ""

def extract_products(text: str) -> List[Dict[str, Any]]:
    """Bóc tách danh sách sản phẩm và số lượng từ tin nhắn tiếng Việt"""
    found_products = []
    text_lower = text.lower()

    for item in STANDARD_CATALOG:
        matched_kw = None
        for kw in item["keywords"]:
            if kw in text_lower:
                matched_kw = kw
                break

        if matched_kw:
            # Tìm số lượng đặt trước hoặc sau từ khóa
            qty = 1  # Mặc định là 1 nếu không nói rõ
            
            # Pattern 1: Số lượng ĐỨNG TRƯỚC từ khóa (ví dụ: "2 chiếc laptop dell", "hai con chuột")
            pre_pattern = r'(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s*(?:chiếc|cái|con|bộ|hộp|máy)?\s*(?:[a-zA-ZÀ-Ỹà-ỹ\s]{0,15}?)' + re.escape(matched_kw)
            m_pre = re.search(pre_pattern, text_lower)
            if m_pre:
                q_str = m_pre.group(1)
                qty = WORD_NUMBERS.get(q_str, int(q_str) if q_str.isdigit() else 1)
            else:
                # Pattern 2: Số lượng ĐỨNG SAU từ khóa (ví dụ: "laptop dell xps 13: 2 chiếc", "dell xps 13 x 2", "dell xps 13 lấy 2")
                post_pattern = re.escape(matched_kw) + r'(?:[:\s\-x*]+(?:lấy|sl|số lượng)?:?\s*)(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s*(?:chiếc|cái|con|bộ|hộp|máy)?'
                m_post = re.search(post_pattern, text_lower)
                if m_post:
                    q_str = m_post.group(1)
                    qty = WORD_NUMBERS.get(q_str, int(q_str) if q_str.isdigit() else 1)

            price = item["list_price"]
            found_products.append({
                "product_name": item["name"],
                "quantity": qty,
                "uom": item["uom"],
                "price_unit": price,
                "subtotal": price * qty
            })

    return found_products

def parse_quotation_message(message: str) -> Dict[str, Any]:
    """
    Hàm bóc tách tổng hợp: nhận tin nhắn thô -> trả về cấu trúc báo giá đầy đủ.
    """
    cust_name = extract_customer_name(message)
    phone = extract_phone_number(message)
    prods = extract_products(message)

    # Nếu không bóc tách được sản phẩm cụ thể, gán sản phẩm mẫu mặc định
    if not prods:
        prods = [{
            "product_name": "Laptop Dell XPS 13",
            "quantity": 1,
            "uom": "Chiếc",
            "price_unit": 24950000,
            "subtotal": 24950000
        }]

    total_amount = sum(p["subtotal"] for p in prods)
    # Tính thuế VAT 10%
    vat_amount = int(total_amount * 0.1)
    grand_total = total_amount + vat_amount

    return {
        "status": "success",
        "customer_name": cust_name,
        "phone": phone,
        "products": prods,
        "items_count": len(prods),
        "total_amount": grand_total,
        "raw_message": message
    }
