# 🤖 ERP Chat Agent — AI Agent tích hợp Odoo 18

> **Đề tài:** Hệ thống AI Agent sử dụng ngôn ngữ tự nhiên tiếng Việt để tra cứu, phân tích và tạo báo giá trực tiếp từ dữ liệu Odoo 18 ERP.

---

## 📐 Kiến trúc tổng quan

```
Người dùng (chat tiếng Việt)
        │
        ▼
┌─────────────────────────────────────┐
│         Hermes Agent Core           │  ← addons_mcp/agent_core/
│  - Hiểu ý định (LLM / Gemini /     │
│    Groq / Ollama)                   │
│  - Phân quyền RBAC (sales/manager) │
│  - Skill Dispatcher                 │
└───────────┬─────────────────────────┘
            │ gọi tool
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────┐     ┌─────────────┐
│  MCP   │     │  RAG Skill  │  ← policy_skill.py
│  ERP   │     │  (ChromaDB) │  ← agent-service/rag/
│ 12 tool│     └─────────────┘
└───┬────┘
    │ XML-RPC / MCP HTTP
    ▼
┌──────────────┐
│  Odoo 18 ERP │  ← localhost:8069 hoặc ngrok URL
└──────────────┘
```

---

## 📁 Cấu trúc thư mục

```text
odoojob/
├── addons_mcp/                 # ← Bình phụ trách (AI Agent + MCP)
│   ├── agent_core/
│   │   ├── skills/
│   │   │   ├── base_skill.py         # BaseSkill, SkillRegistry, RBAC
│   │   │   ├── inventory_skill.py    # Giá, tồn kho, xuất kho
│   │   │   ├── sales_skill.py        # Đơn hàng, báo giá, khách hàng
│   │   │   ├── analytics_skill.py    # Doanh thu, công nợ (chỉ manager)
│   │   │   └── policy_skill.py       # Quy trình nội bộ (RAG-powered)
│   │   ├── agent.py                  # ReAct Agent điều phối
│   │   ├── synthesizer.py            # Chuẩn hóa câu trả lời ERP
│   │   └── llm_client.py             # Gemini / Groq / Ollama / Mock
│   ├── mcp_erp/
│   │   ├── odoo_client.py            # HTTP MCP + XML-RPC fallback
│   │   └── tools.py                  # 12 MCP tools Odoo
│   ├── tests/
│   │   ├── test_tool_calling.py      # Benchmark TN1 (30 câu)
│   │   ├── test_quotation_extraction.py  # Benchmark TN2 (30 tin nhắn)
│   │   ├── test_mcp_tools.py         # Unit test 12 MCP tools
│   │   ├── test_odoo_client_mcp.py   # Unit test MCP envelope unwrap
│   │   └── test_rag_skill_integration.py # Unit test RAG + fallback
│   └── chat_demo.py                  # CLI chat agent
│
├── agent-service/              # ← Tùng phụ trách (RAG Pipeline)
│   ├── rag/                    # ChromaDB, embeddings, retrieval
│   └── data/raw/               # PDF tài liệu chính sách Coolmate demo
│
├── custom_addons/              # ← Hiệp phụ trách (Odoo Addons)
│   ├── ai_mcp/                 # MCP server tích hợp Odoo
│   ├── ai_rag_document/        # Upload tài liệu RAG từ Odoo
│   └── sale_order_import/      # Import đơn hàng từ PDF
│
├── .env                        # ⚠️ KHÔNG COMMIT — cấu hình local
├── TESTER_GUIDE.md             # Hướng dẫn kết nối cho tester
└── SETUP_GUIDE.md              # Hướng dẫn cài đặt toàn bộ
```

---

## ⚙️ Cài đặt & Chạy

### 1. Yêu cầu
- Python 3.13+
- Git

### 2. Clone & checkout nhánh
```bash
git clone https://gitlab.com/binhpthe173173/erpchatagent.git
cd erpchatagent
git checkout dev
```

### 3. Cài thư viện
```bash
pip install openai python-dotenv requests
```

### 4. Tạo file `.env`
```ini
# LLM Engine (chọn 1 trong 3)
GEMINI_API_KEY=AIzaSy...          # Google Gemini (khuyến nghị)
# GROQ_API_KEY=gsk_...            # Groq Cloud (nhanh nhất, miễn phí)
# LLM_PROVIDER=ollama             # Chạy local hoàn toàn

# Kết nối Odoo ERP
ODOO_URL=https://<ngrok-url-của-nhóm>
ODOO_DB=odoo18
ODOO_USER=admin
ODOO_PASSWORD=<mật khẩu nhóm>
```

> 📘 Xem [TESTER_GUIDE.md](TESTER_GUIDE.md) để biết URL và mật khẩu test.

---

## 🚀 Khởi chạy

### Chat agent (CLI)
```bash
python addons_mcp/chat_demo.py
```

**Ví dụ câu hỏi:**
| Loại nghiệp vụ | Câu hỏi mẫu |
|---|---|
| Tra giá | `Laptop Dell XPS 13 giá bao nhiêu?` |
| Tồn kho | `Kho còn bàn phím cơ Keychron K2 không?` |
| Đơn hàng | `Xem đơn hàng của Công ty Sao Mai` |
| Tạo báo giá | `Tạo báo giá cho anh Nguyễn Văn An: 2 chuột Logitech MX Master 3` |
| Chính sách | `Chính sách đổi trả hàng bị lỗi như thế nào?` |
| Doanh thu *(cần quyền manager)* | Gõ `tôi là sếp` → `Doanh thu tháng này bao nhiêu?` |

---

## ✅ Kết quả Kiểm thử (KPI Nghiệm thu)

### Chạy toàn bộ test
```bash
python -m unittest discover -s addons_mcp/tests -p "test_*.py"
```

### Kết quả đạt được

| Bộ kiểm thử | Mục tiêu | Thực tế |
|---|---|---|
| TN1 — Tool Calling (30 câu) | ≥ 80% | **100% (30/30)** |
| TN2 — Tạo báo giá từ tin nhắn (30 tin nhắn) | ≥ 85% | **100% (30/30)** |
| Unit test MCP 12 tools | Pass | **13/13 Pass** |
| Unit test RAG integration | Pass | **2/2 Pass** |

### Chạy riêng từng bộ test
```bash
# TN1
python addons_mcp/tests/test_tool_calling.py

# TN2
python addons_mcp/tests/test_quotation_extraction.py

# Unit tests
python -m unittest addons_mcp/tests/test_mcp_tools.py
python -m unittest addons_mcp/tests/test_odoo_client_mcp.py
python -m unittest addons_mcp/tests/test_rag_skill_integration.py
```

---

## 🔐 Phân quyền RBAC

| Vai trò | Kích hoạt | Quyền truy cập |
|---|---|---|
| `sales_user` | Mặc định | Giá, tồn kho, đơn hàng, tra cứu chính sách |
| `manager` | Gõ `tôi là sếp` | Thêm: doanh thu, tài chính, công nợ toàn công ty |

Nhân viên Sale **tuyệt đối không thể** xem báo cáo tài chính dù hỏi trực tiếp — bị chặn tại cả tầng Agent lẫn tầng Odoo Record Rules.

---

## 👥 Phân công nhóm

| Module | Người phụ trách |
|---|---|
| AI Agent Core + MCP + Tests | Phùng Thanh Bình |
| RAG Pipeline (ChromaDB + Embeddings) | Tùng |
| Odoo Addons (ai_mcp, ai_rag_document) | Hoàng Hiệp |

---

## 🔗 Liên kết

- **GitHub (upstream):** https://github.com/hiepga99/odoo18
- **GitLab (Bình):** https://gitlab.com/binhpthe173173/erpchatagent
- **Nhánh tích hợp:** `dev`
- **Hướng dẫn cài RAG:** [agent-service/SETUP.md](agent-service/SETUP.md)
- **Hướng dẫn cài Odoo:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
