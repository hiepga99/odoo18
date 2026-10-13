# Tích hợp chatbot với RAG qua MCP

## Điểm vào dành cho backend chatbot

- MCP URL: `http://127.0.0.1:8010/mcp`
- Tool đầy đủ: `answer_internal_documents(question, top_k=4)`
- Tool chỉ tìm kiếm, không gọi LLM: `search_internal_documents(question, top_k=4)`

Frontend OWL hoặc Telegram **không gọi NVIDIA, ChromaDB hay MCP trực tiếp**.
Frontend gửi câu hỏi tới backend chatbot; backend dùng MCP client gọi tool và trả
`answer`/`sources` về giao diện.

## Luồng xử lý câu hỏi

```text
OWL/Telegram
  -> backend chatbot
  -> MCP answer_internal_documents
  -> Odoo: lấy company + danh sách tài liệu được phép đọc
  -> BGE-M3: embedding câu hỏi
  -> ChromaDB: tìm chunk phù hợp, có filter quyền
  -> ngưỡng RAG_MIN_SIMILARITY
  -> NVIDIA Nemotron: tổng hợp câu trả lời chỉ từ context
  -> MCP trả answer + sources
  -> backend trả kết quả cho giao diện
```

Nemotron không đọc trực tiếp PDF và không tìm vector. BGE-M3 + ChromaDB đảm nhận
retrieval; Nemotron chỉ tổng hợp câu trả lời từ các chunk đã tìm thấy.

## Ví dụ Python

Trong thư mục `agent-service`:

```powershell
.\.venv\Scripts\python.exe scripts\demo_mcp_chat.py `
  "Khách hàng được đổi trả trong bao nhiêu ngày?" `
  --top-k 4
```

Code tối thiểu cho backend:

```python
from mcp import Client

async with Client("http://127.0.0.1:8010/mcp") as client:
    result = await client.call_tool(
        "answer_internal_documents",
        {"question": question, "top_k": 4},
    )
```

Dùng helper `_read_tool_result` trong `scripts/demo_mcp_chat.py` để hỗ trợ cả
structured content và JSON text của các phiên bản MCP SDK khác nhau.

## Response contract

```json
{
  "answer": "Khách hàng được đổi hoặc trả sản phẩm trong vòng 60 ngày [1].",
  "sources": [
    {
      "rank": 1,
      "citation": "01_policy.pdf, trang 1",
      "source_name": "01_policy.pdf",
      "page": 1,
      "similarity": 0.7169,
      "odoo_document_id": 9,
      "text": "Đoạn nội dung được retrieval..."
    }
  ]
}
```

Giao diện nên hiển thị `answer`, sau đó render nguồn bằng `citation`. Có thể dùng
`odoo_document_id` để mở form tài liệu trong Odoo. Không hiển thị checksum,
attachment ID hoặc toàn bộ chunk nếu người dùng không yêu cầu xem chi tiết.

## Cấu hình trên máy dev khác

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\start_rag_local.ps1
```

Trong `.env`, cấu hình NVIDIA và Odoo API key ở backend. Tuyệt đối không đưa hai
API key này vào OWL JavaScript, Telegram client, Git hoặc response gửi về browser.

## Giới hạn phân quyền hiện tại

MCP server hiện dùng một cặp `ODOO_LOGIN`/`ODOO_API_KEY` từ `.env`, nên mọi câu
hỏi chạy theo quyền của tài khoản service đó. Cách này dùng được cho demo một
công ty nhưng chưa đáp ứng hoàn toàn yêu cầu “API key theo từng người dùng”.

Trước khi triển khai nhiều người dùng, backend cần xác thực phiên Odoo rồi truyền
identity tới MCP bằng cơ chế server-side an toàn (connection token/signed token),
để MCP tạo Odoo client theo người dùng. Không truyền API key Odoo trong prompt,
tool arguments do LLM tạo hoặc dữ liệu frontend có thể đọc được.
