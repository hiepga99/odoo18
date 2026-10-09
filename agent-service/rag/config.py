from __future__ import annotations

import os
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Settings:
    base_dir: Path = BASE_DIR
    raw_data_dir: Path = _env_path("RAG_DATA_DIR", BASE_DIR / "data" / "raw")
    chroma_dir: Path = _env_path("RAG_CHROMA_DIR", BASE_DIR / "chroma_data")
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
