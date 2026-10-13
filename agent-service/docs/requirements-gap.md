# Đối chiếu yêu cầu kỹ thuật và hiện trạng

## Các quyết định cần thống nhất

1. Source có `documents`/`documents_account` Enterprise (OEEL-1), trong khi bảng
   yêu cầu ghi Community. Nếu dùng tính năng upload Documents có sẵn, mô tả kiến
   trúc phải đổi thành Odoo 18 Enterprise và dự án phải có giấy phép phù hợp.
2. PostgreSQL không đồng thời là vector store nếu hệ thống chạy ChromaDB. Cách
   diễn đạt nhất quán là: PostgreSQL lưu dữ liệu Odoo/audit/metadata; Odoo
   filestore lưu binary; ChromaDB lưu chunks và vectors.
3. Cấu hình mẫu của repo dùng Qwen/Ollama đúng yêu cầu. NVIDIA/Nemotron chỉ là
   backend tương thích tùy chọn để thử nghiệm, không thay đổi baseline kiến trúc.
4. Môi trường phát triển hiện tại dùng Python 3.11; yêu cầu ghi Python 3.12. CI và
   Docker image phải kiểm chứng toàn bộ dependency trên Python 3.12 trước khi coi
   là đáp ứng chính thức.

## Ma trận hiện trạng

| Hạng mục | Hiện trạng | Phần còn thiếu | Chủ trì đề xuất |
|---|---|---|---|
| Upload tài liệu | Enterprise Documents đã có upload, folder, version và quyền | Trường trạng thái RAG + background sync | Odoo/backend |
| PDF/ảnh hóa đơn | `documents_account` liên kết attachment với `account.move` | OCR và luồng duyệt kết quả OCR | Odoo/OCR |
| RAG preprocessing | PDF/DOCX/TXT/MD, clean, chunk, BGE-M3 | OCR PDF scan, parser bảng nâng cao | RAG/OCR |
| Ingest từ Odoo | Worker MCP lấy attachment, index và cập nhật trạng thái Odoo | Hardening/retry production | Backend/MCP |
| Vector local | Embedded Chroma hoạt động | Không dùng cho môi trường dùng chung | Đã thay thế tùy cấu hình |
| Vector online | Đã hỗ trợ Chroma HTTP + Compose fragment | Deploy, TLS/auth, backup volume | DevOps/backend |
| Phân quyền retrieval | Đã nhận `allowed_document_ids` và `company_id` | MCP phải tính quyền từ user Odoo hiện tại | Backend/MCP |
| Audit log | Chưa có model Odoo | `ai.agent.audit.log`, ACL append-only, masking | Odoo/backend |
| MCP | Đã có tool search/answer và worker tài liệu | User API key context và tool ERP ngoài RAG | Backend/MCP |
| LLM | Ollama và NVIDIA đều được hỗ trợ | Chốt backend production, quota/monitoring | Agent/backend |
| OCR | Chưa triển khai PaddleOCR | Service/pipeline OCR 3.7.0, đánh giá accuracy | OCR/ML |
| Dự báo | Chưa triển khai | pandas, sklearn, LightGBM, Prophet, dataset/eval | ML |
| OWL chat | Chưa triển khai | Chat UI, bảng/biểu đồ/xác nhận thao tác | Frontend |
| Telegram | Chưa triển khai | Bot, mapping user, authorization | Backend/frontend |
| Docker Compose | Có fragment ChromaDB | Odoo + PostgreSQL + Agent + Ollama + Chroma | DevOps |
| CI | Unit test RAG 17 test pass | Workflow Python 3.12, Odoo test, security/eval gates | CI/team |

## Câu mô tả lớp dữ liệu đề xuất

```text
PostgreSQL 16 lưu dữ liệu nghiệp vụ Odoo, metadata tài liệu và audit log trong
model riêng; Odoo filestore/ir.attachment lưu ảnh, PDF và file gốc; ChromaDB lưu
chunks, embeddings và metadata định danh để tìm kiếm ngữ nghĩa. Odoo là source
of truth và mọi truy vấn vector phải lọc theo quyền Odoo hiện tại.
```

## Tiêu chí hoàn thành phần RAG tích hợp

- Ingest được bytes từ attachment mà không cần chép file vào `data/raw`.
- Lưu `odoo_document_id`, `odoo_attachment_id`, checksum, company và citation.
- Thay chunks cũ khi attachment cập nhật; xóa chunks khi document bị xóa.
- Chạy được embedded local và ChromaDB HTTP bằng cùng interface.
- Retrieval lọc theo danh sách document được Odoo cho phép.
- MCP backend dùng một `Retriever` dùng chung, không nạp BGE-M3 mỗi request.
- Test loader bytes, replace/delete, remote client và access filter đều pass.
