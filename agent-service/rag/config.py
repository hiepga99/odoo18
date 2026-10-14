from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Đặt cache mặc định cạnh project (đang nằm trên ổ D) trước khi tải model.
# Biến môi trường của người dùng luôn được ưu tiên nếu đã cấu hình từ trước.
DEFAULT_CACHE_DIR = BASE_DIR / ".cache"
os.environ.setdefault("HF_HOME", str(DEFAULT_CACHE_DIR / "huggingface"))
os.environ.setdefault("TORCH_HOME", str(DEFAULT_CACHE_DIR / "torch"))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Xet đôi khi treo khi tải file model lớn trên Windows. HTTP chuẩn ổn định hơn
# cho môi trường demo và vẫn hỗ trợ tiếp tục file .incomplete.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")


def _env_path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default))).expanduser().resolve()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def _env_with_legacy(name: str, legacy_name: str, default: str) -> str:
    """Read the new generic setting, falling back to the former NVIDIA name."""
    return os.getenv(name, os.getenv(legacy_name, default)).strip()


def _llm_provider() -> str:
    explicit_provider = os.getenv("LLM_PROVIDER")
    if explicit_provider:
        return explicit_provider.strip().lower()

    # Backward compatibility for an existing .env created before LLM_* existed.
    legacy_base_url = os.getenv("NVIDIA_BASE_URL", "").lower()
    if "nvidia.com" in legacy_base_url:
        return "nvidia"
    return "ollama"


def _env_json_dict(name: str) -> dict[str, str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in parsed.items()
    ):
        raise ValueError(f"{name} phải là JSON object chỉ chứa key/value dạng chuỗi")
    return parsed


@dataclass(frozen=True)
class Settings:
    base_dir: Path = BASE_DIR
    raw_data_dir: Path = _env_path("RAG_DATA_DIR", BASE_DIR / "data" / "raw")
    chroma_dir: Path = _env_path("RAG_CHROMA_DIR", BASE_DIR / "chroma_data")
    chroma_mode: str = os.getenv("RAG_CHROMA_MODE", "embedded").strip().lower()
    chroma_host: str = os.getenv("RAG_CHROMA_HOST", "localhost").strip()
    chroma_port: int = int(os.getenv("RAG_CHROMA_PORT", "8000"))
    chroma_ssl: bool = _env_bool("RAG_CHROMA_SSL", False)
    chroma_headers: dict[str, str] = field(
        default_factory=lambda: _env_json_dict("RAG_CHROMA_HEADERS_JSON")
    )
    model_cache_dir: Path = _env_path(
        "RAG_MODEL_CACHE_DIR",
        Path(os.environ["HF_HOME"]),
    )
    embedding_model: str = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
    collection_name: str = os.getenv("RAG_COLLECTION_NAME", "company_knowledge")
    device: str = os.getenv("RAG_DEVICE", "cpu")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
    embedding_batch_size: int = int(os.getenv("RAG_EMBED_BATCH_SIZE", "8"))
    default_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    min_similarity: float = _env_float("RAG_MIN_SIMILARITY", 0.45)

    odoo_url: str = os.getenv("ODOO_URL", "http://127.0.0.1:1818").rstrip("/")
    odoo_database: str = os.getenv("ODOO_DATABASE", "odoo18_ai_demo").strip()
    odoo_login: str = os.getenv("ODOO_LOGIN", "admin").strip()
    odoo_api_key: str = os.getenv("ODOO_API_KEY", "").strip()
    rag_worker_interval: float = _env_float("RAG_WORKER_INTERVAL", 3.0)
    rag_worker_batch_size: int = int(os.getenv("RAG_WORKER_BATCH_SIZE", "10"))
    llm_provider: str = _llm_provider()
    llm_api_key: str = _env_with_legacy("LLM_API_KEY", "NVIDIA_API_KEY", "")
    llm_base_url: str = _env_with_legacy(
        "LLM_BASE_URL",
        "NVIDIA_BASE_URL",
        "http://localhost:11434/v1",
    )
    llm_model: str = _env_with_legacy(
        "LLM_MODEL",
        "NVIDIA_MODEL",
        "qwen2.5:3b",
    )
    llm_max_tokens: int = int(
        _env_with_legacy("LLM_MAX_TOKENS", "NVIDIA_MAX_TOKENS", "1200")
    )
    llm_enable_thinking: bool = _env_bool(
        "LLM_ENABLE_THINKING",
        _env_bool("NVIDIA_ENABLE_THINKING", False),
    )


settings = Settings()
