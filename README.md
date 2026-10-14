# AI Agent ERP (Odoo 18) - Natural Language Chatbot

> **Đề tài:** Hệ thống AI Agent tích hợp ERP hỗ trợ quản lý bán hàng và kho bằng ngôn ngữ tự nhiên tiếng Việt cho doanh nghiệp SME.  
> **Kiến trúc:** Skill-Based Agent Core (Hermes / Llama 3.3) kết hợp Model Context Protocol (MCP) kết nối trực tiếp Odoo 18 ERP qua XML-RPC.

---

## 🏛️ Kiến trúc Hệ thống (Skill-Based Architecture)

Hệ thống được tổ chức theo mô hình **Kỹ năng (Skill Pattern)** tinh gọn, toàn bộ phân hệ AI Agent & MCP ERP do Bình phụ trách được đóng gói trọn vẹn trong folder `addons_mcp/`:

```text
odoojob/
├── addons_mcp/             # Toàn bộ phân hệ AI Agent Core & MCP Server
│   ├── agent_core/         # Lõi điều phối AI Agent
│   │   ├── skills/         # 4 Module Kỹ năng nghiệp vụ độc lập
│   │   │   ├── base_skill.py       # BaseSkill & SkillRegistry (Auto-dispatching)
│   │   │   ├── inventory_skill.py  # Quản lý kho, giá bán, tồn kho, xuất kho
│   │   │   ├── sales_skill.py      # Bán hàng, đơn hàng, tạo báo giá nháp
│   │   │   ├── analytics_skill.py  # Báo cáo doanh thu, AOV, top sản phẩm
│   │   │   └── policy_skill.py     # Tra cứu quy trình, chính sách công ty (RAG)
│   │   ├── agent.py        # Hermes ReAct Agent Controller
│   │   ├── synthesizer.py  # Bộ chuẩn hóa phản hồi Chuyên viên ERP
│   │   └── llm_client.py   # Tích hợp Groq (Llama 3.3) / Ollama / Fallback
│   ├── mcp_erp/            # MCP Server kết nối Odoo 18 qua XML-RPC (12 tools)
│   ├── tests/              # Bộ kiểm thử tự động (Unit Test & Tool Calling Benchmark)
│   └── chat_demo.py        # Giao diện chạy thử nghiệm tương tác
├── data/                   # Bộ dữ liệu chuẩn (100 hóa đơn + 20 tài liệu quy trình)
├── docker-compose.yml      # Hạ tầng Odoo 18 CE & PostgreSQL 16
└── README.md
```

---

## ⚡ Hướng dẫn Khởi chạy Nhanh

### 1. Khởi động hạ tầng ERP (Docker)
```bash
docker compose up -d
```
* Odoo 18: `http://localhost:8069` (Database: `odoo18`, User: `binhphung19112003@gmail.com`)
* PostgreSQL 16: Cổng `5432`

### 2. Cấu hình LLM Engine (Tùy chọn)
Hệ thống mặc định có sẵn Offline Rule Engine chạy tức thì (< 0.01s). Để đạt tốc độ siêu tốc ~300 token/s với mô hình Llama-3.3-70B, thêm biến môi trường:
```bash
export GROQ_API_KEY="gsk_..."
```

### 3. Trải nghiệm Hội thoại Tương tác
```bash
python addons_mcp/chat_demo.py
```

### 4. Chạy Bộ Kiểm thử Nghiệm thu (Benchmarks)
* **Kiểm thử Tool Calling tiếng Việt (KPI Tuần 4 - Đạt 100% / 30 câu):**
  ```bash
  python addons_mcp/tests/test_tool_calling.py
  ```
* **Kiểm thử 12 MCP Tools kết nối Odoo 18 (Unit test 13/13 Pass):**
  ```bash
  python -m unittest addons_mcp/tests/test_mcp_tools.py
  ```

---

## 🎯 Chỉ tiêu Nghiệm thu Đồ án (KPIs)
* **Dữ liệu mẫu ERP:** 160 sản phẩm, 348 đơn hàng bán, 100 hóa đơn GTGT, 20 quy trình doanh nghiệp.
* **Tích hợp MCP:** 12 tools nghiệp vụ hai chiều với Odoo 18.
* **Agent Core:** Gọi đúng tool đạt **100%** trên bộ test 30 tình huống tiếng Việt thực tế.

---

Các module do nhóm phát triển được đặt chung trong
[`custom_addons/`](custom_addons/README.md), không đặt trực tiếp vào `odoo/`
hoặc `enterprise/`. Mỗi tính năng Odoo mới là một addon con độc lập trong thư
mục này để các thành viên có thể cùng bổ sung module mà không sửa source lõi.

Phần Agent Service cho RAG, ChromaDB, MCP và LLM nằm trong
[`agent-service/`](agent-service/README.md).

## Cấu trúc phần nhóm phát triển

```text
odoo18/
├── custom_addons/
│   ├── ai_document_upload/
│   └── ai_rag_document/
└── agent-service/
```

Xem [SETUP_GUIDE.md](SETUP_GUIDE.md) để chạy Odoo và
[agent-service/SETUP.md](agent-service/SETUP.md) để dựng pipeline RAG.
