# Thiết lập RAG trên máy mới

Repository chỉ lưu source code, tài liệu demo, test và cấu hình mẫu. Không commit
virtual environment, model đã tải, ChromaDB sinh ra hoặc file `.env`.

## Yêu cầu

- Python 3.11
- Ollama cho Windows
- Khoảng 5 GB dung lượng trống cho Python packages, BGE-M3 và Qwen 2.5 3B

## 1. Tạo môi trường Python

Chạy trong thư mục `agent-service`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Cấu hình ứng dụng

```powershell
Copy-Item .env.example .env
```

Mặc định `.env.example` dùng Ollama qua API tương thích OpenAI:

```dotenv
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:3b
```

`.env` chỉ dùng trên máy local và không được commit.

## 3. Tải model sinh câu trả lời

```powershell
ollama pull qwen2.5:3b
ollama list
```

Nếu muốn lưu model Ollama trên ổ D, đặt biến môi trường trước khi tải model rồi
khởi động lại Ollama:

```powershell
New-Item -ItemType Directory -Force D:\AI_Cache\ollama
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "D:\AI_Cache\ollama", "User")
```

## 4. Tạo vector database

```powershell
.\.venv\Scripts\python.exe -m rag.ingest --reset
```

Lần đầu tiên lệnh này tự tải `BAAI/bge-m3` từ Hugging Face. Model được cache
trong `.cache/huggingface`; ChromaDB được tạo trong `chroma_data`. Cả hai thư
mục đều được Git bỏ qua và có thể tái tạo.

## 5. Kiểm tra

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m rag.evaluate --top-k 3
.\.venv\Scripts\python.exe -m rag.generate "Khách hàng được đổi trả trong bao nhiêu ngày?" --top-k 4
```

## Backend LLM tùy chọn

Các biến `LLM_*` hỗ trợ Ollama, NVIDIA Build hoặc endpoint tương thích OpenAI.

Ollama local:

```dotenv
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:3b
```

NVIDIA Build:

```dotenv
LLM_PROVIDER=nvidia
LLM_API_KEY=replace-with-your-nvidia-api-key
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b
```

Không ghi API key thật vào `.env.example`, source code hoặc lịch sử Git.

## Nội dung được commit và được tái tạo

| Thành phần | Commit | Cách tạo trên máy mới |
|---|---:|---|
| `rag/`, `tests/`, `scripts/` | Có | Git clone |
| `data/raw/`, `data/eval/` | Có | Git clone |
| `.env.example`, `requirements.txt` | Có | Git clone |
| `.env` | Không | Copy từ `.env.example` |
| `.venv/` | Không | `py -3.11 -m venv .venv` |
| `.cache/` và BGE-M3 | Không | Tự tải ở lần ingest đầu |
| Model Ollama | Không | `ollama pull qwen2.5:3b` |
| `chroma_data/` | Không | `python -m rag.ingest --reset` |
