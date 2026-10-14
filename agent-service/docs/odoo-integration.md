# Hợp đồng tích hợp Odoo Documents, MCP và RAG

## Quyết định lưu trữ

| Dữ liệu | Nguồn chính |
|---|---|
| Bán hàng, kho, mua hàng, kế toán | Model nghiệp vụ Odoo/PostgreSQL |
| Audit AI Agent | Model riêng trong Odoo/PostgreSQL |
| Metadata, quyền và trạng thái tài liệu | `ai.rag.document` (Community) |
| PDF, DOCX, ảnh và hóa đơn gốc | `ir.attachment`/Odoo filestore |
| Chunk, embedding và metadata tìm kiếm | ChromaDB server với persistent volume |
| Model ML | Volume/cache của Agent Service |

> **Phân biệt HTTP với cloud:** `RAG_CHROMA_MODE=http` chỉ có nghĩa Agent Service
> gọi ChromaDB qua HTTP. Nếu `RAG_CHROMA_HOST=localhost`, dữ liệu vector vẫn nằm
> trên máy local. Tương tự, upload qua giao diện Odoo vẫn nằm trong filestore của
> máy chạy Odoo cho đến khi Odoo được deploy lên server hoặc cấu hình object
> storage.

### Hai chế độ trong source

- **Runtime tích hợp Odoo:** `rag.odoo.ingest`, `rag.odoo.worker`, MCP server và
  `VectorStore` HTTP. Đây là đường chạy production cần giữ.
- **Công cụ phát triển:** `rag.ingest`, `data/raw`, embedded ChromaDB và
  `scripts/start_rag_local.ps1`. Chúng phục vụ demo, evaluation, CI và khả năng
  dựng lại index; không phải nguồn dữ liệu production.

Các thư mục `.cache`, `.venv`, `chroma_data`, `chroma_server_data`, `logs` và
`output` đều bị Git ignore. Vì vậy model/vector local không được đẩy lên Git và
không làm nặng source mà dev khác clone về.

ChromaDB không lưu bản sao file gốc. Odoo là source of truth; vector có thể xóa
và tái tạo từ attachment.

Source có thể chứa module Enterprise `documents` và `documents_account`, nhưng
luồng hiện tại chốt theo Community và dùng model upload custom dựa trên
`ir.attachment`; hợp đồng RAG bên dưới không phụ thuộc Enterprise.

Phương án Community được tách thành hai addon độc lập về trách nhiệm:

- `custom_addons/ai_document_upload`: backend model/file validation, application
  service, wizard presenter và các view upload đơn/nhiều file theo MVP.
- `custom_addons/ai_rag_document`: kế thừa model trên để quản lý trạng thái RAG,
  preview nội dung đã làm sạch và hợp đồng MCP worker.

Cả hai dùng chung model kỹ thuật `ai.rag.document` để giữ dữ liệu tương thích.
File nằm trong trường `file_data` với `attachment=True`; addon RAG cung cấp các
method dành cho MCP worker để claim job, đọc payload và cập nhật kết quả.

## Luồng đồng bộ

1. Người dùng upload một hoặc nhiều file trong **AI Agent → Kho tài liệu**.
2. Odoo lưu binary trong `ir.attachment`, metadata/quyền trong
   `ai.rag.document`, và đặt `rag_status=pending`.
3. `rag.odoo.worker` tự polling và đọc attachment qua MCP bằng API key của
   user/service được ủy quyền.
4. Backend gọi `rag.odoo.ingest.ingest_odoo_document` với bytes và metadata.
5. RAG trích xuất text, chunk, embed rồi thay toàn bộ vector cũ của document.
6. Backend cập nhật `rag_status=indexed`, `rag_indexed_at`, `rag_chunk_count`,
   số trang, số ký tự sạch và cấu hình chunk; hoặc
   ghi `rag_status=error`, `rag_error_message`.
7. Odoo lưu preview/mã vector để người dùng kiểm tra trực quan; embedding thật
   chỉ nằm trong ChromaDB.
8. Khi tắt RAG, backend xóa vector rồi chuyển tài liệu sang `disabled`. Khi người
   dùng xóa tài liệu, Odoo ẩn record và đặt cờ xóa; backend xóa vector trước rồi
   xác nhận để Odoo tự xóa hẳn record cùng attachment. Người dùng chỉ cần bấm
   Delete một lần.

Không chạy embedding đồng bộ trong HTTP request upload của Odoo.

## Hàm backend/MCP sử dụng

```python
from rag.odoo.ingest import ingest_odoo_document

result = ingest_odoo_document(
    content=attachment_bytes,
    filename=document.name,
    odoo_document_id=document.id,
    odoo_attachment_id=document.attachment_id.id,
    company_id=document.company_id.id,
    checksum=document.checksum,
    access_scope="internal",
    extra_metadata={
        "folder_id": document.folder_id.id or 0,
        "owner_id": document.owner_id.id or 0,
    },
)
```

MCP tool tìm kiếm phải lấy danh sách `ai.rag.document` mà user hiện tại có
quyền đọc từ Odoo trước, sau đó truyền danh sách đó vào retrieval:

```python
results = retriever.search(
    question,
    top_k=4,
    allowed_document_ids=allowed_document_ids,
    company_id=current_company_id,
)
return [result.to_dict() for result in results]
```

Không tin `company_id`, user ID hay danh sách document do trình duyệt tự gửi.
Các giá trị này phải được backend suy ra từ API key/user context của Odoo.

## Tool MCP đề xuất

```text
search_internal_documents(question, top_k=4)
```

Mô tả tool:

```text
Tìm chính sách, quy trình, hướng dẫn ERP và tài liệu nội bộ mà người dùng hiện
tại có quyền đọc. Không dùng cho doanh thu, công nợ, tồn kho thời gian thực hoặc
thao tác tạo/sửa chứng từ.
```

MCP tool chỉ trả chunks và citations. LLM điều phối ở Agent Service tổng hợp câu
trả lời; không gọi `rag.generate` lồng bên trong tool.

Luồng trả lời Community phải gọi
`rag.generate.answer_from_odoo_documents(question, allowed_document_ids,
company_id)`. Hàm này từ chối gọi LLM khi danh sách quyền rỗng hoặc mọi kết quả
có similarity thấp hơn `RAG_MIN_SIMILARITY`.

## Trường Odoo của phần mở rộng RAG

Addon `ai_rag_document` kế thừa `ai.rag.document` từ addon upload:

```text
rag_enabled: Boolean
rag_status: Selection(pending, processing, indexed, error)
rag_indexed_at: Datetime
rag_error_message: Text
rag_chunk_count: Integer
rag_checksum: Char
rag_collection: Char
```

Model audit append-only đề xuất `ai.agent.audit.log`:

```text
user_id, company_id, channel, conversation_id, question, tool_name,
tool_arguments_sanitized, status, duration_ms, model_name, source_document_ids,
result_summary, error_message, approval_state, create_date
```

Không lưu API key, token đăng nhập, toàn bộ reasoning hoặc dữ liệu nhạy cảm chưa
được masking vào audit log.

## ChromaDB online

Không có Docker, khởi chạy Chroma và worker trên Windows:

```powershell
.\scripts\start_rag_local.ps1
```

Hoặc dùng Docker cho Chroma:

```powershell
docker compose -f docker-compose.rag.yml up -d
```

Cấu hình Agent Service:

```dotenv
RAG_CHROMA_MODE=http
RAG_CHROMA_HOST=localhost
RAG_CHROMA_PORT=8000
RAG_CHROMA_SSL=false
```

Trong Docker Compose đầy đủ:

```dotenv
RAG_CHROMA_MODE=http
RAG_CHROMA_HOST=chromadb
RAG_CHROMA_PORT=8000
RAG_CHROMA_SSL=false
```

Không public ChromaDB trực tiếp ra Internet. Nếu khác host/network, đặt reverse
proxy TLS và authentication, rồi truyền header qua `RAG_CHROMA_HEADERS_JSON`.

## Smoke test attachment

Mô phỏng backend/MCP gửi bytes của một attachment Odoo, tìm lại bằng đúng
`odoo_document_id`/`company_id`, rồi tự dọn dữ liệu test:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test_odoo_ingest.py
```

Lệnh trên dùng vector store theo `.env`. Để test ChromaDB server mà không sửa
file cấu hình:

```powershell
$env:RAG_CHROMA_MODE="http"
$env:RAG_CHROMA_HOST="localhost"
$env:RAG_CHROMA_PORT="8000"
.\.venv\Scripts\python.exe scripts\smoke_test_odoo_ingest.py
```

Kiểm tra collection dùng chung:

```powershell
.\.venv\Scripts\python.exe -m rag.inspect_store
```

Trong Odoo, mở **AI Agent → Nội dung đã làm sạch** để xem các thẻ nội dung,
trang nguồn và số ký tự. Quản trị viên có thể xem thêm mã vector và vị trí
lưu trữ kỹ thuật. Đây là dữ liệu quan sát/audit; không sao chép mảng embedding vào
PostgreSQL.

MCP endpoint cho backend:

```powershell
.\.venv\Scripts\python.exe -m rag.odoo.mcp_server --transport streamable-http
```

Các tool `search_internal_documents` và `answer_internal_documents` chỉ dùng
document IDs do Odoo trả về cho user của `ODOO_API_KEY`.

## Quy tắc cập nhật và xóa

- Dùng `odoo_document_id` làm định danh ổn định.
- Dùng checksum để bỏ qua file không đổi.
- Khi attachment đổi, embed bản mới trước rồi thay chunks cũ.
- Khi xóa document hoặc mất quyền toàn công ty, xóa vector tương ứng.
- Mỗi truy vấn phải lọc bằng quyền Odoo hiện tại, không chỉ dựa vào metadata
  `access_scope` lưu từ lần index trước.
- Sao lưu Odoo database + filestore là bắt buộc; ChromaDB có thể backup volume
  hoặc rebuild từ Odoo.
