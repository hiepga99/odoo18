# 🧪 Hướng dẫn Kết nối & Test Agent ERP AI

> Dành cho **Kim Hae Ji** và các tester — không cần biết code, chỉ cần làm đúng từng bước.

---

## Bước 1: Chuẩn bị môi trường (chỉ làm 1 lần)

### 1.1. Yêu cầu
- Python 3.13 ([tải tại đây](https://python.org/downloads)) — **tick vào "Add Python to PATH"** khi cài
- Git ([tải tại đây](https://git-scm.com/download/win))

### 1.2. Clone code về máy
Mở **PowerShell** (bấm Windows → gõ `powershell` → Enter), chạy:

```powershell
git clone https://gitlab.com/binhpthe173173/erpchatagent.git
cd erpchatagent
git checkout dev
```

### 1.3. Cài thư viện
```powershell
pip install openai python-dotenv requests
```

---

## Bước 2: Cấu hình kết nối Odoo

Tạo file `.env` trong thư mục `erpchatagent` (cùng cấp với `README.md`):

```ini
# Cấu hình Odoo server của nhóm
ODOO_URL=https://luann-rhonchial-impotently.ngrok-free.dev
ODOO_DB=odoo18
ODOO_USER=admin
ODOO_PASSWORD=Dtg-jD7spey2Gag2ma!

# Key LLM (lấy từ Bình/Hiệp)
GEMINI_API_KEY=<dán key Gemini ở đây>
```

> ⚠️ File `.env` **không được commit lên Git** — chứa mật khẩu nhóm.

---

## Bước 3: Chạy Test

### Test 1 — Kiểm tra gọi tool đúng (TN1 Benchmark)
```powershell
python addons_mcp/tests/test_tool_calling.py
```
✅ Kết quả mong đợi: `30/30 ĐẠT (100%)`

### Test 2 — Kiểm tra tạo báo giá từ tin nhắn (TN2 Benchmark)
```powershell
python addons_mcp/tests/test_quotation_extraction.py
```
✅ Kết quả mong đợi: `30/30 ĐẠT (100%)`

### Test 3 — Chat thử với dữ liệu Odoo thật
```powershell
python addons_mcp/chat_demo.py
```
Thử hỏi:
- `Laptop Dell XPS 13 giá bao nhiêu?`
- `Kho còn hàng bàn phím cơ không?`
- `Cho anh xem đơn hàng của khách hàng Sao Mai`
- `Tôi là sếp` → rồi hỏi: `Doanh thu tháng này bao nhiêu?`

---

## Bước 4: Kiểm tra phân quyền RBAC

| Vai trò | Cách kích hoạt | Quyền truy cập |
|---|---|---|
| Nhân viên Sale | Mặc định | Giá, tồn kho, đơn hàng, chính sách |
| Quản lý / Sếp | Gõ: `tôi là sếp` | Thêm: Doanh thu, tài chính, công nợ |

---

## Gặp lỗi?

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `ModuleNotFoundError` | Thiếu thư viện | Chạy lại `pip install openai python-dotenv` |
| `UID: FAIL` | Odoo server đang restart | Báo Hiệp kiểm tra ngrok |
| `GEMINI_API_KEY` chưa có | Chưa điền key | Xin key từ Bình hoặc Hiệp |

