# Contract RAG cho module MCP/chatbot

`agent-service` chỉ cung cấp pipeline và hàm Python. Việc khai báo MCP server,
transport, URL, tool và xác thực người dùng thuộc module tích hợp trung tâm.

## Tìm kiếm tài liệu

```python
from rag.retrieval import Retriever

results = Retriever().search(
    question,
    top_k=4,
    allowed_document_ids=allowed_document_ids,
    company_id=current_company_id,
)
payload = [result.to_dict() for result in results]
```

## Trả lời bằng RAG

```python
from rag.generate import answer_from_odoo_documents

answer, results = answer_from_odoo_documents(
    question,
    top_k=4,
    allowed_document_ids=allowed_document_ids,
    company_id=current_company_id,
)
payload = {
    "answer": answer,
    "sources": [result.to_dict() for result in results],
}
```

`allowed_document_ids` và `current_company_id` phải được module tích hợp lấy
từ phiên người dùng Odoo đã xác thực. Không nhận trực tiếp các giá trị này từ
trình duyệt hoặc từ arguments do LLM tự tạo.

Nếu module MCP chạy ở process hoặc repository khác, nhóm tích hợp có thể đóng
gói contract trên thành internal API. Phần RAG không tự chọn transport để tránh
trùng cấu hình.

## Response tối thiểu

```json
{
  "answer": "Nội dung trả lời có trích dẫn [1].",
  "sources": [
    {
      "citation": "policy.pdf, trang 2",
      "odoo_document_id": 42,
      "similarity": 0.81,
      "text": "Đoạn nội dung được truy xuất"
    }
  ]
}
```

Frontend chỉ gọi backend chatbot. Không để frontend gọi trực tiếp ChromaDB,
LLM hoặc truyền API key Odoo.
