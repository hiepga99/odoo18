# Odoo18

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
