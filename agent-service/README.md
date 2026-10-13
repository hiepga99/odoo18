# Vietnamese RAG MVP cho Odoo AI Agent

Hướng dẫn dựng môi trường trên máy mới: [SETUP.md](SETUP.md).

Hợp đồng tích hợp upload Odoo, MCP và ChromaDB online:
[docs/odoo-integration.md](docs/odoo-integration.md).

Hướng dẫn backend chatbot gọi câu trả lời qua MCP:
[docs/chatbot-integration.md](docs/chatbot-integration.md).

Ma trận đối chiếu toàn bộ yêu cầu kỹ thuật và phần việc còn thiếu:
[docs/requirements-gap.md](docs/requirements-gap.md).

Pipeline này xây dựng phần trợ lý tra cứu tài liệu nội bộ:

```text
PDF / DOCX / TXT / MD
        -> trích xuất và làm sạch
        -> chia chunk có overlap
        -> BGE-M3 tạo embedding
        -> ChromaDB lưu và tìm kiếm vector
        -> LLM đã cấu hình tổng hợp câu trả lời có nguồn
```

## Bắt đầu review từ đâu

Đi theo luồng dữ liệu, không cần đọc theo tên file alphabet:

1. `rag/config.py`: cấu hình runtime.
2. `rag/loaders.py` → `rag/chunking.py`: đọc, làm sạch và chia tài liệu.
3. `rag/embeddings.py` → `rag/vector_store.py` → `rag/retrieval.py`: tạo,
   lưu và truy vấn vector.
4. `rag/generate.py`: guardrail và sinh câu trả lời.
5. `rag/odoo/ingest.py` → `rag/odoo/mcp_server.py` → `rag/odoo/worker.py`:
   luồng upload Odoo chạy nền.
6. `custom_addons/ai_document_upload` rồi `custom_addons/ai_rag_document`:
   model, quyền và UI phía Odoo.

```text
agent-service/
├── rag/                 # Pipeline lõi và các CLI standalone
│   └── odoo/            # Chỉ phần tích hợp Odoo/MCP/worker
├── tests/               # Unit test theo tên module production
├── scripts/             # Công cụ chạy và smoke test
├── data/                # Dữ liệu demo/evaluation được commit
├── docs/                # Tài liệu tích hợp chuyên sâu
├── README.md            # Điểm bắt đầu review
└── SETUP.md             # Dựng môi trường mới
```

## 1. Phạm vi

- `rag.ingest`: đọc tài liệu và index vào ChromaDB.
- `rag.search`: kiểm tra retrieval, chưa gọi LLM và không tốn API.
- `rag.evaluate`: đo Recall@k và MRR bằng bộ câu hỏi tiếng Việt.
- `rag.generate`: lấy ngữ cảnh từ ChromaDB rồi gọi Qwen qua Ollama mặc định;
  cũng hỗ trợ NVIDIA Build hoặc endpoint tương thích OpenAI.

RAG chỉ dùng cho tài liệu như chính sách, quy trình và hướng dẫn. Câu hỏi dữ liệu thời gian thực như tồn kho hiện tại, doanh thu hay công nợ phải gọi Odoo/MCP, không đưa vào RAG.

## 2. Chuẩn bị môi trường

Chạy các lệnh từ thư mục `agent-service`:

```powershell
cd D:\Downloads\PYP\source_code\odoo18\agent-service
```

Kiểm tra Python:

```powershell
.\.venv\Scripts\python.exe --version
```

Nếu cần cài lại thư viện:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Không cần API key để chạy ingest, search và evaluate.

## 3. Dữ liệu demo

Bốn PDF Coolmate đã chuẩn hóa nằm trong:

```text
data/raw/coolmate_demo/
```

Loader hỗ trợ đệ quy các định dạng `.pdf`, `.docx`, `.txt` và `.md`. Với PDF, metadata giữ số trang để tạo trích dẫn.

## 4. Chạy unit test

Các test này không tải BGE-M3:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 5. Index tài liệu

Lần chạy đầu tiên sẽ tải `BAAI/bge-m3`. Mặc định model được cache tại `agent-service/.cache/huggingface`, tức nằm trên ổ D cùng project.

```powershell
.\.venv\Scripts\python.exe -m rag.ingest --reset
```

`--reset` xóa collection cũ rồi index lại toàn bộ. Những lần chỉ cập nhật file hiện có có thể bỏ `--reset`:

```powershell
.\.venv\Scripts\python.exe -m rag.ingest
```

Ở luồng standalone/embedded, ChromaDB được lưu tại:

```text
agent-service/chroma_data/
```

Luồng tích hợp Odoo dùng `RAG_CHROMA_MODE=http`. Không có Docker vẫn chạy được
Chroma server và worker bằng một lệnh:

```powershell
.\scripts\start_rag_local.ps1
```

Lệnh này duy trì Chroma tại `chroma_server_data/` và tự xử lý job upload mới.

Trên Windows, project mặc định đặt `HF_HUB_DISABLE_XET=1` để tải model qua HTTP thông thường. Nếu lần tải đầu bị gián đoạn, chạy lại cùng lệnh; Hugging Face sẽ tiếp tục từ cache `.incomplete`.

## 6. Thử retrieval

```powershell
.\.venv\Scripts\python.exe -m rag.search "Khách hàng được đổi trả trong bao nhiêu ngày?" --top-k 3
```

Xuất JSON:

```powershell
.\.venv\Scripts\python.exe -m rag.search "Khi tồn kho bị sai lệch thì xử lý thế nào?" --top-k 3 --json
```

Kết quả gồm nội dung chunk, tên file, số trang, khoảng cách cosine và điểm tương đồng.

## 7. Đánh giá retrieval

Bộ test mẫu nằm tại `data/eval/retrieval_cases.jsonl`.

```powershell
.\.venv\Scripts\python.exe -m rag.evaluate --top-k 3
```

Chỉ số:

- `Recall@3`: tỷ lệ câu hỏi có tài liệu đúng xuất hiện trong ba kết quả đầu.
- `MRR@3`: tài liệu đúng xuất hiện càng gần vị trí đầu thì điểm càng cao.

## 8. Cấu hình LLM sinh câu trả lời

Sao chép file cấu hình mẫu:

```powershell
Copy-Item .env.example .env
```

Mặc định `.env.example` đã cấu hình Qwen chạy miễn phí trên Ollama:

```dotenv
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:3b
```

Tải model một lần trên từng máy:

```powershell
ollama pull qwen2.5:3b
```

Không đưa API key, model đã tải, `.env`, `.cache`, `.venv` hoặc `chroma_data`
vào Git. Xem đầy đủ các bước cho máy mới tại [SETUP.md](SETUP.md).

Endpoint Ollama mặc định:

```text
http://localhost:11434/v1
```

Model mặc định:

```text
qwen2.5:3b
```

Chạy RAG đầy đủ:

```powershell
.\.venv\Scripts\python.exe -m rag.generate "Khách ở tỉnh được giao hàng trong bao lâu?" --top-k 4
```

Chương trình luôn in danh sách nguồn retrieval sau câu trả lời, kể cả khi LLM không tạo citation đúng định dạng.

## 9. Thêm tài liệu mới

1. Chép PDF, DOCX, TXT hoặc MD vào `data/raw/`.
2. Chạy lại `python -m rag.ingest`.
3. Thử câu hỏi bằng `python -m rag.search`.
4. Bổ sung câu hỏi và `expected_source` vào `data/eval/retrieval_cases.jsonl`.
5. Chạy `python -m rag.evaluate --top-k 3`.

Nếu đã xóa hoặc đổi tên tài liệu, nên dùng `--reset` để loại bỏ chunk cũ.

### Upload từ Odoo Community

Addon `custom_addons/ai_rag_document` cung cấp menu **AI Agent → Knowledge
Documents**. File upload được lưu trong `ir.attachment` và chuyển sang
`pending`. Khi `rag.odoo.worker` đang chạy, worker tự claim job qua MCP, trích
text/chunk/embed, lưu vector vào Chroma HTTP rồi cập nhật `indexed` hoặc
`error`. Không phải chạy ingest lại bằng tay sau mỗi lần upload.

Kiểm tra trực quan trong Odoo tại **AI Agent → Indexed Chunks** hoặc nút
**Indexed Chunks** trên form tài liệu. Màn hình hiển thị trang nguồn, mã vector,
preview, collection và vị trí storage; embedding thật vẫn chỉ nằm ở Chroma.

```powershell
.\.venv\Scripts\python.exe -m rag.inspect_store
.\.venv\Scripts\python.exe -m rag.odoo.mcp_server --transport streamable-http
```

Lệnh thứ hai mở MCP endpoint cho backend. Hai tool hỏi đáp là
`search_internal_documents` và `answer_internal_documents`; phạm vi tài liệu
được lấy từ quyền của user gắn với `ODOO_API_KEY`.

Luồng hỏi đáp tích hợp Odoo phải dùng
`rag.generate.answer_from_odoo_documents`; hàm yêu cầu danh sách document Odoo
đã kiểm tra quyền và từ chối gọi LLM khi không có nguồn đủ liên quan.

## 10. Cấu hình quan trọng

Có thể chỉnh trong `.env`:

| Biến | Mặc định | Ý nghĩa |
|---|---:|---|
| `RAG_DEVICE` | `cpu` | Thiết bị chạy embedding |
| `RAG_CHUNK_SIZE` | `1000` | Kích thước chunk theo ký tự |
| `RAG_CHUNK_OVERLAP` | `150` | Phần nội dung chồng lặp |
| `RAG_TOP_K` | `5` | Số chunk retrieval mặc định |
| `RAG_MIN_SIMILARITY` | `0.45` | Ngưỡng tối thiểu trước khi cho phép LLM trả lời |
| `RAG_CHROMA_MODE` | `http` khi tích hợp | Chroma server dùng chung giữa các process |
| `ODOO_API_KEY` | trống | API key của Odoo user mà MCP đại diện |
| `RAG_WORKER_INTERVAL` | `3` | Số giây giữa hai lần kiểm tra upload |
| `LLM_PROVIDER` | `ollama` | Backend sinh câu trả lời (`ollama`, `nvidia`, `openai-compatible`) |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Endpoint tương thích OpenAI |
| `LLM_MODEL` | `qwen2.5:3b` | Model sinh câu trả lời |
| `LLM_ENABLE_THINKING` | `false` | Bật/tắt reasoning nếu backend hỗ trợ |

## 11. Giới hạn hiện tại

- PDF scan chưa có lớp OCR; PyMuPDF chỉ đọc PDF có text layer.
- Chưa có reranker sau bước vector search.
- Dữ liệu Coolmate là bản tóm tắt phục vụ demo, không phải tài liệu nội bộ thật.
- Ollama và model local cần đủ RAM/dung lượng trên từng máy; NVIDIA Build là backend tùy chọn và có quota/điều khoản riêng.
