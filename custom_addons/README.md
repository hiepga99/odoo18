# Custom Odoo addons

Đây là thư mục cha dùng chung cho toàn bộ module Odoo do nhóm phát triển.
Không thêm module tùy chỉnh trực tiếp vào source `odoo/` hoặc `enterprise/`.

## Module hiện có

- `ai_document_upload`: lớp upload, kiểm tra file, lưu file gốc bằng
  `ir.attachment` và giao diện quản lý tài liệu.
- `ai_rag_document`: mở rộng tài liệu với trạng thái pipeline, preview nội dung
  đã làm sạch và hợp đồng MCP cho RAG worker.

Hai module được tách riêng theo MVP: module upload không phụ thuộc thư viện AI;
module RAG phụ thuộc `ai_document_upload` và Agent Service chạy ở process riêng.

## Quy ước thêm module

```text
custom_addons/
└── ten_module/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── security/
    ├── views/
    └── tests/
```

Tên module dùng chữ thường và dấu gạch dưới. Mỗi module phải có manifest,
phân quyền, tài liệu ngắn và test phù hợp. Không commit virtual environment,
API key, model AI, filestore, dữ liệu ChromaDB hoặc file cấu hình `.env`.

Đảm bảo cấu hình Odoo có thư mục này trong `addons_path`:

```ini
addons_path = odoo/odoo/addons,odoo/addons,enterprise,custom_addons
```
